---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Pipedrive API 429 Error: Rate Limit Exceeded — Fix & Prevention"
description: "Fix Pipedrive API 429 (429 Too Many Requests) error. Rate limit exceeded. Wait for Retry-After seconds (typically 10s penalty)."
tool: "pipedrive"
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
  - "pipedrive api 429 error"
  - "pipedrive 429 fix"
  - "pipedrive api rate limit exceeded"
  - "pipedrive http 429"
---

## What Causes Pipedrive 429

Pipedrive enforces API rate limits using a token bucket system. Each API call consumes tokens based on the endpoint — v1 endpoints typically consume 1-2 tokens per call, while v2 endpoints can consume 50% fewer tokens. When the bucket is empty, Pipedrive returns HTTP 429 with a `Retry-After` header (typically 10 seconds).

The response is `{"error":"Too Many Requests"}`. Rate limits are per API token, not per user or per company. Pipedrive uses a sliding window — requests reset based on time, not at fixed intervals. API token authentication has lower limits than OAuth authentication.

### Common Scenarios
- Polling deals or persons at high frequency (once per second or faster)
- Bulk import/export operations making individual calls per record
- Multiple systems sharing the same Pipedrive API token without coordination
- Not using cursor-based pagination, leading to many GET calls for large result sets
- Using v1 endpoints when v2 equivalents with lower token costs are available

## How to Detect If You're Affected

1. Check Retry-After and response headers:
   ```bash
   curl -s -I "https://api.pipedrive.com/v1/deals?api_token=$TOKEN" 2>&1 | findstr -i "retry"
   ```

2. Count your token usage per endpoint:
   ```python
   # Pipedrive doesn't expose remaining tokens in headers
   # but you can estimate based on endpoint type
   V1_TOKEN_COST = 2
   V2_TOKEN_COST = 1
   ```

## Step-by-Step Fix

### 1. Respect Retry-After Header
```python
import time

def pipedrive_call(url):
    resp = requests.get(url)
    if resp.status_code == 429:
        retry = int(resp.headers.get("Retry-After", 10))
        print(f"Rate limited — waiting {retry}s")
        time.sleep(retry)
        return requests.get(url)
    return resp
```

### 2. Implement Exponential Backoff with Jitter
```python
import time, random

def pipedrive_retry(url, max_retries=5):
    for attempt in range(max_retries):
        resp = requests.get(url)
        if resp.status_code != 429:
            return resp
        wait = min(30, (2 ** attempt) + random.uniform(0, 1))
        time.sleep(wait)
    raise Exception("Pipedrive 429 — max retries")
```

### 3. Use v2 Endpoints (50% Fewer Tokens)
```python
# BAD — v1 endpoint (2 tokens)
resp = requests.get(f"https://api.pipedrive.com/v1/deals?api_token={token}")

# GOOD — v2 endpoint (1 token)
resp = requests.get("https://api.pipedrive.com/v2/deals",
    headers={"Authorization": f"Bearer {token}"})
```

### 4. Use Cursor Pagination
```python
# BAD — page-based pagination (many calls)
for page in range(1, 100):
    requests.get(f"https://api.pipedrive.com/v1/deals?api_token={token}&page={page}")

# GOOD — cursor-based pagination (fewer calls)
cursor = None
while True:
    params = {"cursor": cursor} if cursor else {}
    resp = requests.get("https://api.pipedrive.com/v2/deals",
        headers={"Authorization": f"Bearer {token}"}, params=params)
    data = resp.json()
    cursor = data.get("next_cursor")
    if not cursor:
        break
```

## Prevention

- Migrate to OAuth authentication — OAuth tokens have higher rate limits than API tokens
- Use v2 endpoints — they consume 50% fewer tokens per call than v1
- Use cursor-based pagination instead of page-based pagination
- Replace polling with Pipedrive webhooks where possible
- Implement a token bucket rate limiter locally that mirrors Pipedrive's limits

## Official Documentation

- [Pipedrive API Rate Limits](https://developers.pipedrive.com/docs/api/v1/rate-limits)
- [Pipedrive API v2 Migration](https://developers.pipedrive.com/docs/api/v2)
- [Pipedrive Webhooks](https://developers.pipedrive.com/docs/api/v1/webhooks)

## People Also Ask

- **What is Pipedrive's API rate limit?** Pipedrive uses a token bucket system. Each call consumes tokens based on the endpoint (v1: ~2 tokens, v2: ~1 token). OAuth tokens have higher limits than API tokens. Exact limits are not publicly documented.
- **How long does a Pipedrive rate limit penalty last?** Typically 10 seconds, indicated by the `Retry-After` header. More severe violations may result in longer penalties.
- **Does Pipedrive API token have different limits than OAuth?** Yes — OAuth authentication provides higher rate limits than API token (`api_token`) authentication. Migrate to OAuth for production integrations.
- **How do I reduce Pipedrive API token consumption?** Use v2 endpoints (50% fewer tokens), cursor-based pagination, and webhooks instead of polling.

## Related Errors

- [Pipedrive 403 Forbidden](/pipedrive/errors/403) — Request not allowed
- [Pipedrive 500 Internal Server Error](/pipedrive/errors/500) — Generic server error
- [Pipedrive 503 Service Unavailable](/pipedrive/errors/503) — Scheduled maintenance
