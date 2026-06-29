---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Make API 429: Rate limit exceeded"
description: "Fix Make API 429 error. Rate limit exceeded — organization-level limit hit. Wait 1 minute for the limit to reset."
tool: "make"
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
  - "make api 429 error"
  - "make 429 fix"
  - "make api rate limit exceeded —"
  - "make http 429"
---

## What Causes Make 429

Make enforces rate limits at the organization level. When your organization exceeds its allowed requests-per-minute, Make returns HTTP 429 with a `Retry-After` header. Each Make plan (Free, Pro, Teams, Enterprise) has a different API call quota, visible in the `license.apiLimit` field returned by the organization endpoint.

The response is `{"error":"Rate limit exceeded"}`. Make typically enforces a 1-minute cooldown window. The organization-level limit applies to all API calls made by any user or integration within your Make organization.

### Common Scenarios
- Multiple Make scenarios all calling the API simultaneously during execution
- A data-heavy scenario that makes individual API calls for each bundle (instead of batching)
- Frequent polling of Make's API endpoints for monitoring or reporting
- Custom integrations built on Make's API that don't implement rate limiting

## How to Detect If You're Affected

1. Check the Retry-After header:
   ```bash
   curl -s -I "https://api.make.com/api/v2/organizations" \
     -H "Authorization: Token $TOKEN" 2>&1 | findstr -i "retry"
   ```

2. Check your organization's rate limit:
   ```bash
   curl -s "https://api.make.com/api/v2/organizations/{org_id}" \
     -H "Authorization: Token $TOKEN" | jq '.license.apiLimit'
   ```

## Step-by-Step Fix

### 1. Wait and Retry
```python
import time

resp = requests.get(url, headers=headers)
if resp.status_code == 429:
    wait_seconds = int(resp.headers.get("Retry-After", 60))
    print(f"Make 429 — waiting {wait_seconds}s")
    time.sleep(wait_seconds)
```

### 2. Check Plan Limits
```python
def check_org_limits(org_id, headers):
    resp = requests.get(f"https://api.make.com/api/v2/organizations/{org_id}", headers=headers)
    data = resp.json()
    api_limit = data.get("license", {}).get("apiLimit")
    print(f"Organization API limit: {api_limit} req/min")
    return api_limit
```

### 3. Implement Request Queuing
```python
import asyncio

class MakeRateLimiter:
    def __init__(self, max_per_minute=30):
        self.min_interval = 60.0 / max_per_minute
        self.last_call = 0

    async def wait(self):
        now = time.time()
        elapsed = now - self.last_call
        if elapsed < self.min_interval:
            await asyncio.sleep(self.min_interval - elapsed)
        self.last_call = time.time()
```

## Prevention

- Check your `license.apiLimit` from the organization endpoint and calculate safe request spacing
- Implement request queuing with an interval calculated from your plan's limit
- Upgrade your Make plan if you consistently need more API calls per minute
- Use Make's built-in batch processing modules instead of per-bundle API calls
- Monitor rate limit headers on every response and throttle proactively

## Official Documentation

- [Make API Documentation](https://www.make.com/en/api-documentation)
- [Make Organizations API](https://www.make.com/en/api-documentation#organizations)
- [Make Plans and Pricing](https://www.make.com/en/pricing)

## People Also Ask

- **What is Make's API rate limit?** Limits are per-organization and depend on your Make plan. Check the `license.apiLimit` field from `GET /api/v2/organizations/{id}` for your specific quota.
- **How long does Make 429 cooldown last?** Typically 60 seconds, indicated by the `Retry-After` header. The limit resets on a rolling window basis.
- **Does each Make user have their own rate limit?** No — the rate limit is per organization. All API calls from all users under the same Make organization count toward the same limit.
- **Can I increase Make's API rate limit?** Yes — upgrading to a higher Make plan increases your organization's API call quota. Contact Make sales for enterprise limits.

## Related Errors

- [Make 500 Server Error](/make/errors/500) — Server error
- [Make 413 Payload Too Large](/make/errors/413) — Payload too large
- [Make 403 Forbidden](/make/errors/403) — Insufficient permissions
