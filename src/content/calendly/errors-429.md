---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Calendly API 429: Rate limit exceeded"
description: "Fix Calendly API 429 error. Rate limit exceeded. Implement exponential backoff."
tool: "calendly"
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
  - "calendly api 429 error"
  - "calendly 429 fix"
  - "calendly api rate limit exceeded"
  - "calendly http 429"
---

## What Causes Calendly 429

Calendly returns HTTP 429 when your API requests exceed the allowed rate limit. Calendly's API uses a sliding window rate limiter — limits apply per access token. Exceeding the limit returns 429 with a `Retry-After` header indicating how many seconds to wait.

The response is `{"message":"Rate limit exceeded","errors":[{"message":"Rate limit exceeded"}]}`. Calendly's rate limits are per-token, not per-user or per-organization. Free accounts have stricter limits than paid subscriptions.

### Common Scenarios
- Polling Calendly's API for scheduled events at high frequency
- Bulk operations that make individual API calls for each event type or user
- Multiple integration services sharing the same Calendly API token
- Webhook processing that triggers additional API calls without delay

## How to Detect If You're Affected

1. Check the Retry-After header:
   ```bash
   curl -s -I "https://api.calendly.com/users/me" \
     -H "Authorization: Bearer $TOKEN" 2>&1 | findstr -i "retry"
   ```

2. Check the response status:
   ```bash
   curl -s -w "\n%{http_code}" "https://api.calendly.com/users/me" \
     -H "Authorization: Bearer $TOKEN" | tail -1
   ```

## Step-by-Step Fix

### 1. Respect Retry-After Header
```python
import time

resp = requests.get("https://api.calendly.com/users/me", headers=headers)
if resp.status_code == 429:
    retry = int(resp.headers.get("Retry-After", 60))
    print(f"Rate limited — waiting {retry}s")
    time.sleep(retry)
```

### 2. Implement Exponential Backoff
```python
import time, random

def calendly_request(url, headers, max_retries=5):
    for attempt in range(max_retries):
        resp = requests.get(url, headers=headers)
        if resp.status_code != 429:
            return resp
        wait = (2 ** attempt) + random.uniform(0, 1)
        time.sleep(wait)
    raise Exception("Calendly 429 — max retries exceeded")
```

### 3. Add Inter-Request Delay
```python
# Add minimum delay between calls
MIN_DELAY = 0.5  # 500ms between calls
last_call = 0

def rate_limited_call(url, headers):
    global last_call
    now = time.time()
    elapsed = now - last_call
    if elapsed < MIN_DELAY:
        time.sleep(MIN_DELAY - elapsed)
    last_call = time.time()
    return requests.get(url, headers=headers)
```

## Prevention

- Add a minimum 500ms delay between API calls to stay well within rate limits
- Cache Calendly responses that don't change frequently (user info, event types)
- Use Calendly webhooks instead of polling for event updates
- Monitor response headers for rate limit warnings and throttle proactively
- Use separate API tokens for different integration services

## Official Documentation

- [Calendly API Documentation](https://developer.calendly.com/api-docs/)
- [Calendly API Rate Limits](https://developer.calendly.com/api-docs/basics/rate-limits)
- [Calendly Authentication](https://developer.calendly.com/api-docs/basics/authentication)

## People Also Ask

- **What is Calendly's API rate limit?** Exact limits are not publicly documented. Limits are per access token and vary by account plan. Start with 500ms between calls.
- **Does Calendly provide Retry-After headers?** Yes — 429 responses include a `Retry-After` header with the number of seconds to wait before retrying.
- **How do I fix Calendly 429?** Add exponential backoff with jitter, respect the Retry-After header, and add inter-request delays.
- **Can I increase my Calendly rate limit?** Higher limits are available on paid Calendly plans. Contact Calendly support for plan-specific allocations.

## Related Errors

- [Calendly 401 Unauthorized](/calendly/errors/401) — Invalid or missing token
- [Calendly 403 Forbidden](/calendly/errors/403) — Insufficient permissions
- [Calendly 422 Validation Error](/calendly/errors/422) — Validation error
