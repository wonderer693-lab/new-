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
lastUpdated: '2026-06-07'
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "slack api rate_limited error"
  - "slack rate_limited fix"
  - "slack api http 429 with retry-after"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Slack is throttling your API calls. You're hitting a specific method's rate limit and Slack is telling you to slow down.

**The fix:**
1. Wait for the number of seconds in the `Retry-After` header (usually 30-60 seconds)
2. Add delays between your API calls so you don't hit the limit again
3. Enable auto-retry in your automation tool if available

**Copy-paste this code** (if you're using a code editor):
```python
import time, requests

resp = requests.post("https://slack.com/api/conversations.list",
    headers={"Authorization": f"Bearer {TOKEN}"})
if resp.status_code == 429:
    wait = int(resp.headers.get("Retry-After", 60))
    time.sleep(wait)
    resp = requests.post("https://slack.com/api/conversations.list",
        headers={"Authorization": f"Bearer {TOKEN}"})
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Try this prompt in ChatGPT, Claude, Cursor, or Gemini:

> I'm getting a "rate_limited" error from the Slack API with HTTP 429.
> The response is: {"ok":false,"error":"rate_limited"} and there's a Retry-After header.
> I'm calling conversations.list too frequently.
> Please give me a step-by-step fix with working Python code that handles Slack rate limiting with retry logic.

The AI should outline a retry function that reads the Retry-After header, waits the right amount of time, and tries again.

Need more? Follow up with:
> The fix didn't work. I'm still getting rate_limited after adding delays. Here's what I tried: [paste your code]. Please debug this.

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to handle Slack rate limiting in popular automation tools:

### Zapier
1. Open your Zap → click the Slack action step
2. Enable "Auto-retry on error" in the step settings (Zapier retries on rate limits automatically)
3. If you're still hitting limits, add a "Delay by Zapier" step (set to 60 seconds) before the Slack action

### Make (Integromat)
1. Open your scenario → right-click the Slack module → "Add error handler"
2. Choose "Retry" → set interval to 60 seconds, max retries to 3
3. For bulk operations, add a "Sleep" module (60 seconds) between Slack calls

### n8n
1. Open your workflow → click the Slack node
2. In "Settings" → enable "Retry on Fail" → set "Wait Between Tries" to 60000ms, "Max Tries" to 3
3. For bulk operations, add a "Wait" node (60 seconds) between Slack nodes

### Power Automate
1. Open your flow → click the Slack action
2. In "Settings" → enable "Retry Policy" → set to "Exponential interval" with count 3
3. For bulk operations, add a "Delay" action (60 seconds) before the Slack action

**Which tool should you use?** Zapier has the best built-in retry for Slack — it handles rate limits automatically without extra configuration.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `{"ok":false,"error":"rate_limited"}` with HTTP status 429
- `{"ok":false,"error":"rate_limited"}` and a `Retry-After` header in the response
- HTTP 429 in your integration logs when calling Slack
- Your Slack integration works sometimes but fails randomly with rate limit errors

**What it means in plain English:** Slack is telling you to slow down. You're calling a specific API method too many times in a short period. Wait for the time shown in the Retry-After header and try again.

**Most common cause:** Calling low-tier methods like `conversations.list` or `users.list` too frequently, or running multiple processes that all hit the same Slack endpoint at once.

</div>

## What Causes Slack rate_limited

Slack returns HTTP 429 with a `Retry-After` header when your app exceeds the per-method rate limit tier. Slack assigns each API method to a rate limit tier (Tier 1, 2, 3, or 4). Tier 1 methods (e.g., `conversations.list`, `users.list`) allow as little as 1 request per minute for non-marketplace apps, while Tier 4 methods allow up to 100 requests per minute. See all [Slack API errors](/slack/) in our complete reference.

Similar rate limit issues occur with [HubSpot 429](/hubspot/errors/429), [Salesforce 429](/salesforce/errors/429), and [Pipedrive 429](/pipedrive/errors/429).

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

This error also affects integrations. See our [HubSpot to Slack](/integrations/hubspot-to-slack/), [Make to Slack](/integrations/make-to-slack/), and [ActiveCampaign to Slack](/integrations/activecampaign-to-slack/) integration error guides.

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
