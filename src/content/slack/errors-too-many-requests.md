---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Slack API too_many_requests: Rate limit exceeded without Retry-After"
description: "Fix Slack API too_many_requests error. Rate limit exceeded without Retry-After. Implement adaptive rate limiting."
tool: "slack"
errorCode: "too_many_requests"
errorName: "too_many_requests"
httpStatus: 0
category: "unknown"
severity: "medium"
priority: 2
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "slack api too_many_requests error"
  - "slack too_many_requests fix"
  - "slack api rate limit exceeded without"
---

## What Causes Slack too_many_requests

Slack returns the `too_many_requests` error (not to be confused with HTTP 429 `rate_limited`) when your app exceeds Slack's rate limits but Slack does not provide a `Retry-After` header. This error appears in the response body as `{"ok":false,"error":"too_many_requests"}` with HTTP status 200 — Slack often returns 200 with an error field rather than using HTTP status codes for non-429 rate limit issues.

This typically happens with Slack's "burst" rate limits (not the tier-based per-method limits). Burst limits apply across all methods globally — hitting 30+ requests in a few seconds to any Slack API method can trigger this, even if you're within per-method tier limits.

### Common Scenarios
- Sending burst requests to Slack across different API methods (e.g., chat.postMessage + conversations.list + users.list simultaneously)
- A chat bot that responds to many incoming messages at once, each triggering API calls
- Migration or backfill scripts that pull data from multiple Slack endpoints without pacing
- Multiple server instances all making Slack API calls without coordination

## How to Detect If You're Affected

1. Check the response body for the error field:
   ```bash
   curl -s "https://slack.com/api/conversations.list?limit=100" \
     -H "Authorization: Bearer $TOKEN" | jq '.error'
   ```
   If `"too_many_requests"`, you've hit the burst limit.

2. Check X-RateLimit-* headers on all responses:
   ```bash
   curl -s -I "https://slack.com/api/conversations.list?limit=1" \
     -H "Authorization: Bearer $TOKEN" 2>&1 | findstr -i "ratelimit"
   ```

## Step-by-Step Fix

### 1. Implement Adaptive Rate Limiting
```python
import time
import random

class SlackAdaptiveLimiter:
    def __init__(self):
        self.min_delay = 1.0  # Start with 1 second between calls
        self.max_delay = 60.0

    def call(self, method, **kwargs):
        resp = requests.post(f"https://slack.com/api/{method}",
            headers=headers, json=kwargs)
        data = resp.json()

        if data.get("error") == "too_many_requests":
            self.min_delay = min(self.min_delay * 2, self.max_delay)
            wait = self.min_delay + random.uniform(0, 1)
            print(f"Burst limit hit — backing off {wait:.1f}s")
            time.sleep(wait)
        else:
            self.min_delay = max(1.0, self.min_delay * 0.9)

        return data
```

### 2. Monitor Rate Limit Headers
```python
resp = requests.post("https://slack.com/api/conversations.list", headers=headers)
print(f"Remaining: {resp.headers.get('X-RateLimit-Remaining')}")
print(f"Reset: {resp.headers.get('X-RateLimit-Reset')}")

# Slow down if remaining is low
remaining = int(resp.headers.get("X-RateLimit-Remaining", 100))
if remaining < 10:
    time.sleep(10)
```

### 3. Add Inter-Request Delay
```python
# Add a minimum delay between consecutive Slack API calls
MINIMUM_DELAY = 1.5  # seconds

last_call_time = 0

def slack_api_call(method, **kwargs):
    global last_call_time
    now = time.time()
    elapsed = now - last_call_time
    if elapsed < MINIMUM_DELAY:
        time.sleep(MINIMUM_DELAY - elapsed)
    last_call_time = time.time()
    return requests.post(f"https://slack.com/api/{method}", headers=headers, json=kwargs)
```

## Prevention

- Add a minimum 1-second delay between all Slack API calls regardless of method
- Monitor `X-RateLimit-Remaining` headers on every response and throttle proactively when low
- Avoid burst patterns — stagger parallel requests by at least 500ms each
- Use Slack's Web API only for actions, not for data polling (use Events API instead)
- Implement a token bucket or leaky bucket rate limiter that paces all outgoing Slack calls

## Official Documentation

- [Slack Rate Limits](https://api.slack.com/docs/rate-limits)
- [Slack Web API](https://api.slack.com/methods)
- [Slack Tiered Rate Limits](https://api.slack.com/docs/rate-limits#tiers)

## People Also Ask

- **What's the difference between Slack too_many_requests and rate_limited?** `rate_limited` is an HTTP 429 with `Retry-After` header (per-method tier limit). `too_many_requests` is a burst limit without `Retry-After` (transient, resolves in seconds).
- **How long does Slack's burst rate limit last?** Typically 30-60 seconds. The burst limit is based on a sliding window — reduce request frequency and the window clears.
- **Does Slack's too_many_requests apply globally or per method?** Burst limits apply globally across all API methods — 30+ requests to any combination of methods in a few seconds can trigger it.
- **How do I prevent Slack too_many_requests?** Add a minimum 1-second delay between all API calls and avoid parallel requests to multiple Slack endpoints simultaneously.

## Related Errors

- [Slack rate_limited](/slack/errors/rate_limited) — HTTP 429 with Retry-After header
- [Slack invalid_auth](/slack/errors/invalid_auth) — Invalid auth credentials
- [Slack token_revoked](/slack/errors/token_revoked) — Token was revoked
