---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Zoho API TOO_MANY_CONCURRENT_REQUESTS: Exceeded concurrency limit for org/app"
description: "Fix Zoho API TOO_MANY_CONCURRENT_REQUESTS error. Exceeded concurrency limit for org/app. Implement request queuing."
tool: "zoho"
errorCode: "TOO_MANY_CONCURRENT_REQUESTS"
errorName: "TOO_MANY_CONCURRENT_REQUESTS"
httpStatus: 0
category: "unknown"
severity: "medium"
priority: 2
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "zoho api TOO_MANY_CONCURRENT_REQUESTS error"
  - "zoho TOO_MANY_CONCURRENT_REQUESTS fix"
  - "zoho api exceeded concurrency limit for"
---

## What Causes Zoho TOO_MANY_CONCURRENT_REQUESTS

Zoho limits the number of simultaneous API requests per org and per app. The org-level concurrency cap is typically 5 concurrent requests, while heavy operations like ConvertLead, getRelatedRecords, and file uploads have a stricter sub-limit of 10 across the entire org. When you exceed these limits, Zoho returns `TOO_MANY_CONCURRENT_REQUESTS`.

The error appears as `{"code":"TOO_MANY_CONCURRENT_REQUESTS","message":"Exceeded concurrency limit for org/app"}`. Unlike `TOO_MANY_REQUESTS` (daily credit limit), this error triggers immediately when parallel requests exceed the cap, regardless of remaining daily credits.

### Common Scenarios
- Parallel async workers (Airflow, Celery, Lambda) all calling Zoho simultaneously
- Webhook handlers firing concurrent API calls on mass-update events
- Multiple microservices sharing the same Zoho API credentials
- Bulk import scripts using `ThreadPoolExecutor` or `asyncio.gather` with too many concurrent tasks

## How to Detect If You're Affected

1. Run a concurrency test to reproduce the error:
   ```python
   import requests
   from concurrent.futures import ThreadPoolExecutor, as_completed

   urls = ["https://www.zohoapis.com/crm/v3/Leads"] * 10
   headers = {"Authorization": f"Zoho-oauthtoken {TOKEN}"}

   with ThreadPoolExecutor(max_workers=10) as exe:
       futures = [exe.submit(requests.get, url, headers=headers) for url in urls]
       for f in as_completed(futures):
           resp = f.result()
           if resp.json().get("code") == "TOO_MANY_CONCURRENT_REQUESTS":
               print("Concurrency limit hit!")
   ```

2. Check the error response body:
   ```bash
   curl -s "https://www.zohoapis.com/crm/v3/Leads" \
     -H "Authorization: Zoho-oauthtoken $TOKEN" | jq .
   ```
   Look for `"code": "TOO_MANY_CONCURRENT_REQUESTS"`.

3. Symptom: errors appear only during parallel bursts (mass update webhooks, multi-threaded scripts), never during sequential single requests.

## Step-by-Step Fix

### 1. Implement Request Queuing
Use an asyncio semaphore or thread pool with a max concurrency of 3-4 (well below the typical 5 limit):
```python
import asyncio
import aiohttp

semaphore = asyncio.Semaphore(3)  # Max 3 concurrent requests

async def zoho_request(session, url):
    async with semaphore:
        async with session.get(url, headers=headers) as resp:
            return await resp.json()

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [zoho_request(session, url) for url in urls]
        return await asyncio.gather(*tasks)
```

### 2. Reduce Parallelism at Source
If you're using a worker pool, cap concurrency explicitly:
```python
from concurrent.futures import ThreadPoolExecutor

# BAD: unlimited parallelism
with ThreadPoolExecutor(max_workers=20) as pool:
    pool.map(call_zoho, records)

# GOOD: cap at 3 concurrent requests
with ThreadPoolExecutor(max_workers=3) as pool:
    pool.map(call_zoho, records)
```

### 3. Throttle Heavy Operations
Operations like ConvertLead have a separate org-wide sub-limit of 10. Use a global queue for these:
```python
import time

heavy_ops_queue = asyncio.Queue(maxsize=1)

async def convert_lead(lead_id):
    await heavy_ops_queue.put(None)  # Acquire global lock
    try:
        resp = await session.post(f"https://www.zohoapis.com/crm/v3/Leads/{lead_id}/convert")
        return resp
    finally:
        await heavy_ops_queue.get()  # Release
        heavy_ops_queue.task_done()
```

## Prevention

- Use a semaphore or bounded thread pool with max 3 concurrent requests across all integration code
- Centralize all Zoho API calls through a shared rate limiter module (not per-service pools)
- Avoid making Zoho API calls inside webhook handlers — push to a queue and process sequentially
- For ETL pipelines, use sequential processing with batching rather than parallel workers
- Set `max_connections` on your HTTP client session to 3 (e.g., `aiohttp.TCPConnector(limit=3)`)

## Official Documentation

- [Zoho CRM API Concurrent Request Limits](https://www.zoho.com/crm/developer/docs/api/v3/concurrent-requests.html)
- [Zoho CRM API Rate Limits](https://www.zoho.com/crm/developer/docs/api/v3/rate-limits.html)
- [Zoho CRM API Overview](https://www.zoho.com/crm/developer/docs/api/v3/)

## People Also Ask

- **What is Zoho's concurrent request limit?** Zoho allows 5 concurrent requests per org by default. Heavy operations (ConvertLead, file uploads) have a stricter org-wide sub-limit of 10 concurrent calls.
- **How is TOO_MANY_CONCURRENT_REQUESTS different from TOO_MANY_REQUESTS?** TOO_MANY_REQUESTS is a daily credit limit error; TOO_MANY_CONCURRENT_REQUESTS is an instantaneous parallelism cap. You can hit the concurrency limit even with plenty of daily credits remaining.
- **Does the concurrent limit apply per user or per org?** Per org. All API calls from all users and integrations under the same Zoho org share the same concurrency pool.
- **Can I increase Zoho's concurrent request limit?** Zoho does not publicly offer concurrent limit increases. Stay under the cap by using request queuing with max 3 concurrent calls.

## Related Errors

- [Zoho TOO_MANY_REQUESTS](/zoho/errors/TOO_MANY_REQUESTS) — Daily credit limit exceeded
- [Zoho LIMIT_EXCEEDED](/zoho/errors/LIMIT_EXCEEDED) — General API limit reached
- [Zoho Access Denied (OAuth throttle)](/zoho/errors/access-denied-oauth-throttle) — OAuth token request throttled
