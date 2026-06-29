---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Zapier API 429: Rate limit exceeded"
description: "Fix Zapier API 429 error. Rate limit exceeded. Wait 60 seconds (cooldown)."
tool: "zapier"
errorCode: "429"
errorName: "429"
httpStatus: 429
category: "rate-limit"
severity: "high"
priority: 1
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "zapier api 429 error"
  - "zapier 429 fix"
  - "zapier api rate limit exceeded"
  - "zapier http 429"
---

## What Causes Zapier 429

Zapier's API platform enforces rate limits to protect its infrastructure. The exact limits depend on your Zapier plan: Free/Starter plans have tighter limits, while Professional/Team/Company plans have higher caps. When you exceed the limit, Zapier returns HTTP 429 with a `Retry-After` header indicating the cooldown period in seconds.

The response includes `{"status":"error","message":"Rate limit exceeded"}`. Zapier uses a rolling window approach — each request resets the window rather than having fixed-minute boundaries. A 60-second cooldown period is typical after hitting the limit.

### Common Scenarios
- Polling the Zapier API faster than once per few seconds
- Running multiple parallel integrations against the same API key
- High-volume webhook triggers generating API calls faster than the plan allows
- A burst of requests after a long idle period (cold start)

## How to Detect If You're Affected

1. Check the Retry-After header in the response:
   ```bash
   curl -s -I "https://api.zapier.com/v2/..." \
     -H "Authorization: Bearer $TOKEN" 2>&1 | grep -i retry-after
   ```

2. Parse the response status code:
   ```python
   resp = requests.get(url, headers=headers)
   if resp.status_code == 429:
       retry_after = int(resp.headers.get("Retry-After", 60))
       print(f"Rate limited. Retry after {retry_after}s")
   ```

## Step-by-Step Fix

### 1. Wait the Cooldown Period
```python
import time

resp = requests.get(url, headers=headers)
if resp.status_code == 429:
    cooldown = int(resp.headers.get("Retry-After", 60))
    print(f"Rate limited — waiting {cooldown}s")
    time.sleep(cooldown)
    resp = requests.get(url, headers=headers)  # Retry
```

### 2. Implement Exponential Backoff
```python
import time, random

def zapier_request(url, headers, max_retries=5):
    for attempt in range(max_retries):
        resp = requests.get(url, headers=headers)
        if resp.status_code != 429:
            return resp
        wait = min(60, (2 ** attempt)) + random.uniform(0, 1)
        time.sleep(wait)
    raise Exception("Zapier 429 — max retries exceeded")
```

### 3. Reduce Request Frequency
If you're consistently hitting limits, add inter-request delays:
```python
import time

# Add 1-2 second delay between requests
for item in items:
    call_zapier_api(item)
    time.sleep(1.5)
```

## Prevention

- Add a minimum 1-second delay between API calls to stay well within rate limits
- Cache API responses that don't change frequently (schema lookups, user info)
- Use Zapier's webhook-triggered approach instead of polling where possible
- Upgrade your Zapier plan if you consistently exceed the rate allocation
- Monitor `X-RateLimit-Remaining` headers (if available) and slow down proactively

## Official Documentation

- [Zapier Platform API](https://platform.zapier.com/)
- [Zapier API Authentication](https://platform.zapier.com/docs/auth)
- [Zapier Status Page](https://status.zapier.com/)

## People Also Ask

- **What is Zapier's API rate limit?** Limits vary by plan. Free/Starter plans have lower limits (typical ~10 req/min), while higher-tier plans get increased allocations. Exact numbers are not publicly documented.
- **How long does a Zapier rate limit cooldown last?** The `Retry-After` header typically indicates 60 seconds, but it can vary based on the severity of the rate limit breach.
- **Does each Zapier API key have its own rate limit?** Yes — rate limits are applied per API key/authentication. Using multiple API keys can increase your effective throughput.
- **Can I request a higher rate limit from Zapier?** Zapier does not publicly offer rate limit increases. Upgrade your plan or distribute calls across multiple API keys.

## Related Errors

- [Zapier 500 Server Error](/zapier/errors/500) — Server error
- [Zapier 401 Unauthorized](/zapier/errors/401) — Invalid or expired access token
- [Zapier 400 Bad Request](/zapier/errors/400) — Malformed request
