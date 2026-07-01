---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "ActiveCampaign API 429: Rate limit exceeded"
description: "Fix ActiveCampaign API 429 (429 Too Many Requests) error. Rate limit exceeded — sent too many requests in a given amount of time. Reduce request frequency."
tool: "activecampaign"
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
  - "activecampaign api 429 error"
  - "activecampaign 429 fix"
  - "activecampaign api rate limit exceeded —"
  - "activecampaign http 429"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Too many API calls to ActiveCampaign. You're sending more than 5 requests per second and getting blocked.

**The fix:**
1. Wait 60 seconds before trying again
2. Add a delay between requests (at least 200ms between each call)
3. If doing a bulk import, split it into smaller batches with pauses

**Copy-paste this code** (if you're using a code editor):
```python
import time, requests

headers = {"Api-Token": "YOUR_TOKEN"}
resp = requests.get("https://{account}.api-us1.com/api/3/contacts", headers=headers)
if resp.status_code == 429:
    time.sleep(60)  # Wait 60 seconds, then retry
    resp = requests.get("https://{account}.api-us1.com/api/3/contacts", headers=headers)
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm getting a 429 Too Many Requests error from the ActiveCampaign API.
> The error message is: "Rate limit exceeded"
> I'm running a bulk contact sync that makes many API calls in a loop.
> Please give me a step-by-step fix with working Python code that handles rate limiting with delays and retries.

**What to expect:** The AI should give you a throttling function with delays between requests and exponential backoff for retries.

**If it doesn't work**, add this follow-up:
> The fix didn't work. I'm still getting 429 errors even with delays. Here's what I tried: [paste your code]. Please debug this.

**Best AI tools for this:** Claude (best at explaining rate limit strategies), ChatGPT-4 (good code generation), Cursor (if you want inline code fixes)

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to handle ActiveCampaign rate limits in popular automation tools:

### Zapier
1. Open your Zap → click the ActiveCampaign action step
2. Enable "Auto-retry on error" in the step settings (Zapier retries 429 errors automatically)
3. If hitting limits often, add a "Delay by Zapier" step before the action (set to 1 second)

### Make (Integromat)
1. Open your scenario → right-click the ActiveCampaign module → "Add error handler"
2. Choose "Retry" → set interval to 5 seconds, max retries to 3
3. For bulk operations, add a "Sleep" module (1 second) between ActiveCampaign calls

### n8n
1. Open your workflow → click the ActiveCampaign node
2. In "Settings" → enable "Retry on Fail" → set "Wait Between Tries" to 5000ms, "Max Tries" to 3
3. For bulk operations, add a "Wait" node (1 second) between ActiveCampaign nodes

### Power Automate
1. Open your flow → click the ActiveCampaign action
2. In "Settings" → enable "Retry Policy" → set to "Exponential interval" with count 3
3. For bulk operations, add a "Delay" action (1 second) before the ActiveCampaign action

**Which tool should you use?** Zapier has the best built-in retry — it handles 429 errors automatically without any configuration.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"429 Too Many Requests"`
- `"rate limit"`
- `"Rate limit exceeded"`
- `"HTTP 429"` in your integration logs

**What it means in plain English:** ActiveCampaign is telling you to slow down. You're making too many API calls too fast. Wait a bit and try again with pauses between requests.

**Most common cause:** Bulk imports or sync jobs that fire hundreds of requests in a loop without any delay between them.

</div>

## What Causes ActiveCampaign 429

ActiveCampaign returns HTTP 429 when your integration exceeds the API rate limit. ActiveCampaign's rate limits are 5 requests per second for most accounts, with higher limits available on Enterprise plans. The limit applies per API token, not per IP address.

The response contains `{"errors":[{"title":"429 Too Many Requests","detail":"Rate limit exceeded"}]}`. ActiveCampaign does not include a `Retry-After` header in the response, so you must implement your own rate limiting logic. Exceeding the rate limit temporarily blocks further requests from that token.

### Common Scenarios
- Processing large contact imports by looping through individual POST requests without delays
- Multiple integration services sharing the same API token and exceeding the combined limit
- Polling ActiveCampaign endpoints in a tight loop for real-time updates
- Synchronizing large datasets from ActiveCampaign to another system using concurrent requests

## How to Detect If You're Affected

1. Check for 429 on any endpoint:
   ```bash
   curl -s -w "\n%{http_code}" "https://{account}.api-us1.com/api/3/contacts" \
     -H "Api-Token: $TOKEN" | tail -1
   ```

2. Monitor request timing to identify bursts:
   ```bash
   # Time a single request
   time curl -s "https://{account}.api-us1.com/api/3/contacts" \
     -H "Api-Token: $TOKEN" -o /dev/null
   ```

3. Check if multiple services use the same token by reviewing integration logs for overlapping timestamps.

## Step-by-Step Fix

### 1. Implement Request Throttling
```python
import time
import requests

MIN_DELAY = 0.2  # 200ms between requests (5 req/s limit)
last_request = 0

def throttled_request(url, headers, params=None):
    global last_request
    now = time.time()
    elapsed = now - last_request
    if elapsed < MIN_DELAY:
        time.sleep(MIN_DELAY - elapsed)
    resp = requests.get(url, headers=headers, params=params)
    last_request = time.time()
    return resp

# Use for all API calls
resp = throttled_request("https://{account}.api-us1.com/api/3/contacts", headers)
```

### 2. Use Bulk Endpoints (When Available)
```python
# BAD — creating contacts one by one
for email in email_list:
    payload = {"contact": {"email": email}}
    resp = requests.post(url, headers=headers, json=payload)

# GOOD — use batch sync if available, or add delays between calls
for i, email in enumerate(email_list):
    payload = {"contact": {"email": email}}
    resp = requests.post(url, headers=headers, json=payload)
    if (i + 1) % 5 == 0:
        time.sleep(1)  # Pause every 5 requests
```

### 3. Implement Retry with Backoff
```python
import time, random

def activecampaign_request(url, headers, method="GET", data=None, max_retries=3):
    for attempt in range(max_retries):
        resp = requests.request(method, url, headers=headers, json=data)
        if resp.status_code != 429:
            return resp
        wait = (2 ** attempt) + random.uniform(0, 0.5)
        print(f"Rate limited — retrying in {wait:.1f}s (attempt {attempt + 1})")
        time.sleep(wait)
    raise Exception("ActiveCampaign 429 — max retries exceeded")
```

## Prevention

- Add a minimum 200ms delay between API requests to stay within the 5 req/s limit
- Use separate API tokens for different integration services to isolate rate limits
- Batch contact operations using ActiveCampaign's bulk sync if available, or process in chunks
- Cache frequently accessed reference data (lists, tags, fields) to reduce redundant API calls
- Monitor per-token request volume and set up alerts before hitting the limit

## Official Documentation

- [ActiveCampaign API Overview](https://developers.activecampaign.com/reference/overview)
- [ActiveCampaign API Rate Limits](https://developers.activecampaign.com/reference/rate-limits)
- [ActiveCampaign Authentication](https://developers.activecampaign.com/reference/authentication)

## People Also Ask

- **What is ActiveCampaign's API rate limit?** 5 requests per second per API token for most plans. Enterprise plans may have higher limits.
- **Does ActiveCampaign include Retry-After headers?** No — ActiveCampaign 429 responses do not include a Retry-After header. You must implement your own rate limiting.
- **Can I increase my ActiveCampaign rate limit?** Enterprise plans may have higher limits. Contact ActiveCampaign support or your account manager to discuss rate limit increases.
- **How long does a 429 block last?** Typically 60 seconds. After the cooldown, requests from the token are accepted again.

## Related Errors

- [ActiveCampaign 401 Unauthorized](/activecampaign/errors/401) — Invalid or missing API token
- [ActiveCampaign 403 Forbidden](/activecampaign/errors/403) — Authenticated but not authorized for resource
- [ActiveCampaign 422 Unprocessable Entity](/activecampaign/errors/422) — Missing or invalid parameters
