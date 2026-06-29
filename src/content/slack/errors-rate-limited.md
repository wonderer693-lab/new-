---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Slack API rate_limited: HTTP 429 with Retry-After header"
description: "Fix Slack API rate_limited error. HTTP 429 with Retry-After header. Respect Retry-After header value (seconds)."
tool: "slack"
errorCode: "rate_limited"
errorName: "rate_limited"
httpStatus: 0
category: "unknown"
severity: "medium"
priority: 2
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "slack api rate_limited error"
  - "slack rate_limited fix"
  - "slack api http 429 with retry-after"
---

## What Causes Slack rate_limited

Slack returns HTTP 429 with a `Retry-After` header when your app exceeds the per-method rate limit tier. Slack assigns each API method to a rate limit tier (Tier 1, 2, 3, or 4). Tier 1 methods (e.g., `conversations.list`, `users.list`) allow as little as 1 request per minute for non-marketplace apps, while Tier 4 methods allow up to 100 requests per minute.

The response is HTTP 429 with header `Retry-After: <seconds>` and body `{"ok":false,"error":"rate_limited"}`. This is distinct from `too_many_requests` (burst limit without `Retry-After`) — `rate_limited` always includes a `Retry-After` header telling you exactly how long to wait.

### Common Scenarios
- Calling a Tier 1 method like `conversations.list` more than once per minute
- Calling `users.list` frequently for user lookups (Tier 2, 20 req/min for non-marketplace)
- Polling `chat.scheduledMessages.list` faster than its tier allows
- Multiple scenarios or processes all calling the same high-tier-cost method simultaneously

## How to Detect If You're Affected

1. Check the Retry-After header:
   ```bash
   curl -s -I "https://slack.com/api/conversations.list?limit=1" \
     -H "Authorization: Bearer $TOKEN" 2>&1 | findstr -i "retry"
   ```

2. Parse the response body:
   ```bash
   curl -s "https://slack.com/api/conversations.list" \
     -H "Authorization: Bearer $TOKEN" | jq '.'
   ```

## Step-by-Step Fix

### 1. Respect Retry-After Header
```python
import time

resp = requests.post("https://slack.com/api/conversations.list", headers=headers)
data = resp.json()
if resp.status_code == 429:
    retry_after = int(resp.headers.get("Retry-After", 60))
    print(f"Rate limited — retry after {retry_after}s")
    time.sleep(retry_after)
```

### 2. Implement Tier-Aware Request Scheduling
```python
SLACK_TIERS = {
    "Tier 1": 1,   # req/min
    "Tier 2": 20,
    "Tier 3": 50,
    "Tier 4": 100,
}

METHOD_TIERS = {
    "conversations.list": "Tier 1",
    "users.list": "Tier 2",
    "chat.postMessage": "Tier 3",
    "conversations.history": "Tier 3",
}

def get_min_interval(method):
    tier = METHOD_TIERS.get(method, "Tier 2")
    max_per_min = SLACK_TIERS[tier]
    return 60.0 / max_per_min
```

### 3. Marketplace App Consideration
If you publish to the Slack App Directory, limits are higher:
```python
# Marketplace apps get 4x-15x higher limits
# Check if you should apply for marketplace distribution
IS_MARKETPLACE_APP = False  # Set based on your app status
LIMIT_MULTIPLIER = 15 if IS_MARKETPLACE_APP else 1
effective_limit = SLACK_TIERS[mytier] * LIMIT_MULTIPLIER
```

## Prevention

- Look up the rate limit tier for each method you call and calculate the minimum interval
- Cache responses from list-type endpoints — `conversations.list` and `users.list` data changes infrequently
- Use Slack's `cursor` pagination to get all results in one call instead of multiple calls
- Implement a central rate limiter that tracks calls per method per minute
- For Tier 1 methods especially, cache aggressively and re-fetch only when needed

## Official Documentation

- [Slack Rate Limits](https://api.slack.com/docs/rate-limits)
- [Slack Tiered Rate Limits](https://api.slack.com/docs/rate-limits#tiers)
- [Slack Web API Methods](https://api.slack.com/methods)

## People Also Ask

- **What's the difference between Slack rate_limited and too_many_requests?** `rate_limited` is HTTP 429 with a `Retry-After` header (per-method tier limit). `too_many_requests` is a burst limit across all methods without `Retry-After`.
- **What is Slack Tier 1 rate limit?** 1 request per minute for non-marketplace apps, up to 15 per minute for Slack App Directory apps.
- **How long should I wait on Slack 429?** Read the `Retry-After` header — it tells you exactly how many seconds to wait. Typical values are 30-120 seconds.
- **Does each Slack workspace have its own rate limit?** Yes — rate limits are per-workspace per-app. The same app in different workspaces has independent rate limit counters.

## Related Errors

- [Slack too_many_requests](/slack/errors/too_many_requests) — Burst limit exceeded
- [Slack invalid_auth](/slack/errors/invalid_auth) — Invalid auth credentials
- [Slack token_revoked](/slack/errors/token_revoked) — Token was revoked
