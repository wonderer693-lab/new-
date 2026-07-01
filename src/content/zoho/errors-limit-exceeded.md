---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Zoho API LIMIT_EXCEEDED: General limit exceeded"
description: "Fix Zoho API LIMIT_EXCEEDED error. General limit exceeded. Implement exponential backoff."
tool: "zoho"
errorCode: "LIMIT_EXCEEDED"
errorName: "LIMIT_EXCEEDED"
httpStatus: 0
category: "unknown"
severity: "medium"
priority: 2
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "zoho api LIMIT_EXCEEDED error"
  - "zoho LIMIT_EXCEEDED fix"
  - "zoho api general limit exceeded"
---

## What Causes Zoho LIMIT_EXCEEDED

Zoho returns `LIMIT_EXCEEDED` when any API usage metric exceeds its quota — this includes the per-request rate limit (requests per minute), concurrent bulk job limits, or daily API call counts. Unlike `TOO_MANY_REQUESTS` (specific to daily credits), `LIMIT_EXCEEDED` is a catch-all for various throttling scenarios.

The error response shows `{"code":"LIMIT_EXCEEDED","message":"General limit exceeded"}`. The exact limit depends on your Zoho CRM edition: Free (250 req/min), Standard (1,000 req/min), Professional (5,000 req/min), Enterprise (10,000 req/min). Bulk API jobs have separate limits (2 concurrent bulk jobs for most editions).

### Common Scenarios
- Sending more than the per-minute rate limit (e.g., 250 requests in a minute on Free edition)
- Running more than 2 concurrent bulk API jobs
- Hitting the daily API call cap for your edition tier
- Exceeding the per-module record creation limit (e.g., 10,000 records/day for some modules)

## How to Detect If You're Affected

1. Inspect the response code — distinguish LIMIT_EXCEEDED from other errors:
   ```bash
   curl -s "https://www.zohoapis.com/crm/v3/Leads" \
     -H "Authorization: Zoho-oauthtoken $TOKEN" | jq '.code'
   ```
   `"LIMIT_EXCEEDED"` means a general limit was hit.

2. Check your edition limits by querying org settings:
   ```bash
   curl -s "https://www.zohoapis.com/crm/v3/settings/org" \
     -H "Authorization: Zoho-oauthtoken $TOKEN" | jq '.api_limit'
   ```

3. Review the `X-RATELIMIT-REMAINING` header on successful responses — if it drops quickly, a rate limit breach is imminent.

## Step-by-Step Fix

### 1. Implement Exponential Backoff
```python
import time
import random

def zoho_request_with_backoff(url, headers, max_retries=5):
    for attempt in range(max_retries):
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200 and resp.json().get("code") != "LIMIT_EXCEEDED":
            return resp
        wait = (2 ** attempt) + random.uniform(0, 1)
        print(f"LIMIT_EXCEEDED, retrying in {wait:.1f}s (attempt {attempt+1}/{max_retries})")
        time.sleep(wait)
    raise Exception("LIMIT_EXCEEDED — max retries exceeded")
```

### 2. Check Your Edition's Rate Limits
```python
EDITION_LIMITS = {
    "Free": {"rate": 250, "bulk_jobs": 1},
    "Standard": {"rate": 1000, "bulk_jobs": 2},
    "Professional": {"rate": 5000, "bulk_jobs": 2},
    "Enterprise": {"rate": 10000, "bulk_jobs": 5},
}
edition = get_org_edition()  # Fetch from /settings/org
max_rpm = EDITION_LIMITS[edition]["rate"]
```

### 3. Upgrade Plan If Needed
If you consistently hit limits with normal usage, your plan may be undersized. Free edition (250 req/min) is suitable for light testing only. Professional or Enterprise is recommended for production integrations with moderate to high traffic.

## Prevention

- Pre-calculate your required requests-per-minute based on record volume and choose an edition that provides 2x headroom
- Spread API calls evenly — avoid burst patterns that spike into rate limit territory
- Use Zoho's Bulk API jobs instead of individual POST/PUT for large datasets (fewer overall requests)
- Monitor `X-RATELIMIT-REMAINING` headers and throttle proactively when remaining calls drop below 20%
- Implement a distributed rate limiter if multiple services share the same Zoho org

## Official Documentation

- [Zoho CRM API Rate Limits by Edition](https://www.zoho.com/crm/developer/docs/api/v3/rate-limits.html)
- [Zoho CRM API Bulk Operations](https://www.zoho.com/crm/developer/docs/api/v3/bulk-operations.html)
- [Zoho CRM API Overview](https://www.zoho.com/crm/developer/docs/api/v3/)

## People Also Ask

- **What's the difference between LIMIT_EXCEEDED and TOO_MANY_REQUESTS?** TOO_MANY_REQUESTS specifically means daily credit limit exhausted. LIMIT_EXCEEDED covers all other limits: rate per minute, concurrent bulk jobs, or per-module daily caps.
- **What is Zoho's per-minute rate limit?** Free: 250 req/min, Standard: 1,000, Professional: 5,000, Enterprise: 10,000. Check your edition at `/settings/org`.
- **Can I run multiple bulk API jobs at once?** Most editions allow 2 concurrent bulk jobs. Enterprise allows 5. Attempting more returns LIMIT_EXCEEDED.
- **How do I monitor Zoho API rate limit usage?** Read the `X-RATELIMIT-REMAINING` response header. It shows how many requests you can make in the current minute window before hitting the rate limit.

## Related Errors

- [Zoho TOO_MANY_REQUESTS](/zoho/errors/TOO_MANY_REQUESTS) — Daily credit limit exceeded
- [Zoho TOO_MANY_CONCURRENT_REQUESTS](/zoho/errors/TOO_MANY_CONCURRENT_REQUESTS) — Exceeded parallel request limit
- [Zoho Access Denied (OAuth throttle)](/zoho/errors/access-denied-oauth-throttle) — OAuth token request throttled
