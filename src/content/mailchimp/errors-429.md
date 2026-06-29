---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Mailchimp API 429: Exceeded 10 simultaneous connections or high volume thres..."
description: "Fix Mailchimp API 429 (429 Too Many Requests) error. Exceeded 10 simultaneous connections or high volume threshold. Implement request queuing — reduce parallelism."
tool: "mailchimp"
errorCode: "429"
errorName: "429 Too Many Requests"
httpStatus: 429
category: "rate-limit"
severity: "high"
priority: 1
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "mailchimp api 429 error"
  - "mailchimp 429 fix"
  - "mailchimp api exceeded 10 simultaneous connections"
  - "mailchimp http 429"
---

## What Causes Mailchimp 429

Mailchimp's API enforces two types of rate limits: a maximum of 10 simultaneous connections per API key, and a per-second request cap (typically 10 req/s for standard plans, lower for free plans). Exceeding either returns HTTP 429 with a `Retry-After` header. Mailchimp also applies a 120-second timeout on individual requests — long-running operations must use the batch endpoint.

The response is HTTP 429 with `{"status":429,"title":"Too Many Requests","detail":"Your request count is too high"}`. Mailchimp's rate limits are per API key, not per user or per list. Free accounts have stricter limits than paid plans.

### Common Scenarios
- Parallel processing scripts that fire 10+ concurrent requests to Mailchimp
- Bulk sync operations that send individual API calls for each subscriber instead of using batch
- Long-running report or export requests that exceed the 120-second timeout
- Multiple applications sharing the same Mailchimp API key without coordination
- Polling operations that check list activity at high frequency

## How to Detect If You're Affected

1. Check the Retry-After header:
   ```bash
   curl -s -I -X GET "https://usX.api.mailchimp.com/3.0/lists" \
     -H "Authorization: apikey $API_KEY" 2>&1 | findstr -i "retry"
   ```

2. Check response for rate limit info:
   ```bash
   curl -s "https://usX.api.mailchimp.com/3.0/lists" \
     -H "Authorization: apikey $API_KEY" | jq '.status, .detail'
   ```

## Step-by-Step Fix

### 1. Implement Request Queuing
```python
import time
from threading import Semaphore

mailchimp_semaphore = Semaphore(5)  # Max 5 concurrent, under 10 limit

def mailchimp_request(method, path, **kwargs):
    with mailchimp_semaphore:
        resp = requests.request(method, f"https://usX.api.mailchimp.com/3.0/{path}",
            headers={"Authorization": f"apikey {API_KEY}"}, **kwargs)
        if resp.status_code == 429:
            retry = int(resp.headers.get("Retry-After", 10))
            time.sleep(retry)
        return resp
```

### 2. Use Batch Endpoint for Large Operations
```python
# BAD — individual calls per subscriber
for email in emails:
    requests.post(f"https://usX.api.mailchimp.com/3.0/lists/{list_id}/members",
        headers=headers, json={"email_address": email, "status": "subscribed"})

# GOOD — use batch endpoint
batch_ops = [{"method": "POST", "path": f"lists/{list_id}/members",
              "body": json.dumps({"email_address": e, "status": "subscribed"})}
             for e in emails]
requests.post(f"https://usX.api.mailchimp.com/3.0/batches",
    headers=headers, json={"operations": batch_ops})
```

### 3. Respect the 120s Timeout
Long operations should use batch processing:
```python
# BAD — direct call that may exceed 120s
resp = requests.get("https://usX.api.mailchimp.com/3.0/reports/{campaign_id}/click-details",
    headers=headers)

# GOOD — use batch for large reports
batch_resp = requests.post("https://usX.api.mailchimp.com/3.0/batches",
    headers=headers, json={"operations": [{
        "method": "GET",
        "path": f"reports/{campaign_id}/click-details"
    }]})
```

## Prevention

- Limit concurrent connections to 5 (well below the 10-connection cap)
- Use Mailchimp's batch API for any operation involving more than 100 records
- Add a minimum 100ms delay between individual API calls
- Monitor `X-Forwarded-For` headers if behind a proxy — Mailchimp may rate-limit by IP
- Implement a central rate limiter that all Mailchimp API consumers share

## Official Documentation

- [Mailchimp API Rate Limits](https://mailchimp.com/developer/marketing/guides/rate-limits/)
- [Mailchimp Batch Operations](https://mailchimp.com/developer/marketing/api/batch-operations/)
- [Mailchimp API Overview](https://mailchimp.com/developer/marketing/api/)

## People Also Ask

- **What is Mailchimp's API rate limit?** Maximum 10 simultaneous connections per API key, plus approximately 10 requests per second for standard plans. Free plans have lower limits.
- **How do I fix Mailchimp 429?** Reduce parallel connections to 5 or fewer, and use the batch endpoint for bulk operations instead of individual API calls.
- **Does Mailchimp's batch endpoint count against rate limits?** A batch operation counts as 1 API call for the batch submission, plus 1 per operation within it for rate limiting purposes. However, it avoids the 10-connection concurrency limit.
- **Can I increase my Mailchimp API rate limit?** Higher rate limits are available on paid Mailchimp plans. Contact Mailchimp support or your account manager for plan-specific allocations.

## Related Errors

- [Mailchimp 403 Forbidden](/mailchimp/errors/403) — User role lacks permission
- [Mailchimp 404 Not Found](/mailchimp/errors/404) — Resource does not exist
- [Mailchimp 400 Bad Request](/mailchimp/errors/400) — Malformed request or validation error
