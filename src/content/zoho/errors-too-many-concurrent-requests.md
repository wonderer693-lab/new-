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
lastUpdated: '2026-06-11'
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "zoho api TOO_MANY_CONCURRENT_REQUESTS error"
  - "zoho TOO_MANY_CONCURRENT_REQUESTS fix"
  - "zoho api exceeded concurrency limit for"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Too many simultaneous API calls to Zoho. You're sending more than 5 requests at the same time, and Zoho is blocking the extras.

**The fix:**
1. Send requests one at a time instead of all at once
2. Add a short delay (1-2 seconds) between requests
3. If you're using a tool with parallel workers, reduce them to 3 or fewer

**Copy-paste this code** (if you're using a code editor):
```python
import time, requests

for record in records:
    resp = requests.post(url, headers=headers, json={"data": [record]})
    time.sleep(1)
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Paste this into any AI tool:

> I'm getting a "TOO_MANY_CONCURRENT_REQUESTS" error from the Zoho CRM API.
> The error message is: "Exceeded concurrency limit for org/app"
> I'm running multiple parallel API calls to Zoho using asyncio/threading.
> Please give me a step-by-step fix with working Python code that serializes requests with a semaphore to stay under Zoho's 5 concurrent request limit.

Expect back the AI should give you code that uses a semaphore or queue to limit parallel requests to 3 at a time, well under Zoho's concurrency cap.

Still hitting the error? Send:
> The fix didn't work. I'm still getting concurrent request errors. Here's my current setup: [paste your code and worker count]. Please help me reduce parallelism.

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to handle Zoho concurrent request errors in popular automation tools:

### Zapier
1. Open your Zap → check if you have multiple Zoho actions running in parallel paths
2. Merge parallel paths into a single sequential flow — put Zoho actions one after another
3. Add a "Delay by Zapier" step (2 seconds) between Zoho actions to space them out

### Make (Integromat)
1. Open your scenario → check if the Zoho module is set to process bundles in parallel
2. Set the scenario to "Process bundles sequentially" in scenario settings
3. Add a "Sleep" module (2 seconds) between Zoho calls to avoid hitting the concurrency cap

### n8n
1. Open your workflow → go to workflow settings
2. Set "Concurrency Limit" to 1 — this prevents multiple workflow executions from running Zoho calls at the same time
3. Add a "Wait" node (2 seconds) between Zoho nodes if you have multiple in sequence

### Power Automate
1. Open your flow → click the "Apply to each" loop containing Zoho actions
2. Set "Concurrency Control" to "On" and set "Degree of Parallelism" to 1
3. Add a "Delay" action (2 seconds) inside the loop before each Zoho action

**Which tool should you use?** n8n gives you the most control — its workflow-level concurrency setting prevents all parallel Zoho calls at once.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"TOO_MANY_CONCURRENT_REQUESTS"` in the API response
- `"concurrent limit"` exceeded in your integration logs
- `"Exceeded concurrency limit for org/app"` from Zoho
- Errors that only appear when multiple processes run at the same time

**What it means in plain English:** Zoho only allows 5 API calls at the exact same time. You're sending more than that simultaneously. Slow down and send them one at a time.

**Most common cause:** Scripts or automations that use parallel workers, multiple threads, or fire many requests at once without any queuing.

</div>

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

See all [Zoho API errors](/zoho/) in our complete reference. Similar rate limit issues occur with [HubSpot 429](/hubspot/errors/429), [Salesforce 429](/salesforce/errors/429), and [Slack rate_limited](/slack/errors/rate_limited). This error also affects integrations — see our [Zoho to Mailchimp integration errors](/integrations/zoho-to-mailchimp/) for common cross-tool issues.
