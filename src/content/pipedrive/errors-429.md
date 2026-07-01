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

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Too many API calls to Pipedrive — you've hit the rate limit and Pipedrive is telling you to slow down.

**The fix:**
1. Wait for the number of seconds shown in the `Retry-After` header (usually 10 seconds)
2. Slow down your requests — add a delay between calls
3. Switch to v2 endpoints — they use 50% fewer rate limit tokens

**Copy-paste this code** (if you're using a code editor):
```python
import time, requests

resp = requests.get(
    "https://api.pipedrive.com/v1/deals?api_token=TOKEN"
)
if resp.status_code == 429:
    wait = int(resp.headers.get("Retry-After", 10))
    time.sleep(wait)
    resp = requests.get(
        "https://api.pipedrive.com/v1/deals?api_token=TOKEN"
    )
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Send this to your AI coding assistant and ask it to generate working code:

> I'm getting a 429 Too Many Requests error from the Pipedrive API.
> The error message is: "Too Many Requests" with a Retry-After header.
> My integration makes frequent API calls and keeps hitting the rate limit.
> Please give me a step-by-step fix with working Python code that handles Pipedrive rate limiting with exponential backoff.

You want code that the AI should give you a retry function with exponential backoff and jitter, plus tips to reduce token consumption using v2 endpoints.

If the generated code doesn't handle the edge cases, refine with:
> The fix didn't work. I'm still getting 429 errors. Here's what I tried: [paste your code]. Please debug this.

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to handle Pipedrive rate limits in popular automation tools:

### Zapier
1. Open your Zap → click the Pipedrive action step
2. Enable "Auto-retry on error" in the step settings (Zapier auto-retries 429 errors up to 3 times)
3. If you're hitting limits frequently, add a "Delay by Zapier" step before the Pipedrive action (set to 10 seconds)

### Make (Integromat)
1. Open your scenario → right-click the Pipedrive module → "Add error handler"
2. Choose "Retry" → set interval to 10 seconds, max retries to 3
3. For bulk operations, add a "Sleep" module (10 seconds) between Pipedrive calls

### n8n
1. Open your workflow → click the Pipedrive node
2. In "Settings" → enable "Retry on Fail" → set "Wait Between Tries" to 10000ms, "Max Tries" to 3
3. For bulk operations, add a "Wait" node (10 seconds) between Pipedrive nodes

### Power Automate
1. Open your flow → click the Pipedrive action
2. In "Settings" → enable "Retry Policy" → set to "Exponential interval" with count 3
3. For bulk operations, add a "Delay" action (10 seconds) before the Pipedrive action

**Which tool should you use?** Zapier has the best built-in retry for Pipedrive — it handles 429 errors automatically without any configuration.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"429 Too Many Requests"`
- `"Rate limit exceeded"`
- `"Too Many Requests"` with a `Retry-After` header
- `"HTTP 429"` in your integration logs

**What it means in plain English:** Pipedrive is telling you to slow down. You're making too many API calls in a short time. Wait a few seconds and try again.

**Most common cause:** Bulk imports or sync jobs that fire too many requests at once without pausing between them, or using v1 endpoints that cost more rate limit tokens.

</div>

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

See all [Pipedrive API errors](/pipedrive/) in our complete reference. Similar rate limit issues occur with [HubSpot 429](/hubspot/errors/429), [Salesforce 429](/salesforce/errors/429), and [Slack rate_limited](/slack/errors/rate_limited). This error also affects integrations — see our [Pipedrive to Mailchimp integration errors](/integrations/pipedrive-to-mailchimp/) for common cross-tool issues.
