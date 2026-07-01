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

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Too many Slack API calls in a burst. You're sending requests too fast across all Slack endpoints at once, and Slack is temporarily blocking you.

**The fix:**
1. Wait 30-60 seconds and try again
2. Add at least a 1-second delay between every Slack API call
3. Don't fire multiple Slack requests at the exact same time

**Copy-paste this code** (if you're using a code editor):
```python
import time, requests

resp = requests.post("https://slack.com/api/chat.postMessage",
    headers={"Authorization": f"Bearer {TOKEN}"},
    json={"channel": "C12345", "text": "Hello"})
if resp.json().get("error") == "too_many_requests":
    time.sleep(30)
    resp = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": f"Bearer {TOKEN}"},
        json={"channel": "C12345", "text": "Hello"})
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm getting a "too_many_requests" error from the Slack API.
> The response is: {"ok":false,"error":"too_many_requests"} (with HTTP 200, not 429).
> I'm making multiple Slack API calls at the same time from different parts of my app.
> Please give me a step-by-step fix with working Python code that spaces out Slack API requests to avoid burst limits.

**What to expect:** The AI should give you a rate limiter that adds delays between requests and explains the difference between Slack's burst limits and per-method limits.

**If it doesn't work**, add this follow-up:
> The fix didn't work. I added delays but still get too_many_requests. Here's what I tried: [paste your code]. Please debug this.

**Best AI tools for this:** Claude (best at explaining rate limit strategies), ChatGPT-4 (good code generation), Cursor (if you want inline code fixes)

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to handle Slack burst rate limits in popular automation tools:

### Zapier
1. Open your Zap → add a "Delay by Zapier" step before each Slack action
2. Set the delay to 2-5 seconds to space out your requests
3. If you have multiple Slack steps, add a delay between each one

### Make (Integromat)
1. Open your scenario → add a "Sleep" module (2-5 seconds) between Slack modules
2. Right-click each Slack module → "Add error handler" → choose "Retry" with a 30-second interval
3. Avoid running multiple Slack modules in parallel — chain them one after another

### n8n
1. Open your workflow → add a "Wait" node (2-5 seconds) between Slack nodes
2. In each Slack node's "Settings" → enable "Retry on Fail" → set "Wait Between Tries" to 30000ms
3. Make sure Slack nodes run one at a time, not in parallel branches

### Power Automate
1. Open your flow → add a "Delay" action (2-5 seconds) before each Slack action
2. In each Slack action's "Settings" → enable "Retry Policy" → set to "Fixed interval" with count 3
3. Avoid having multiple Slack actions trigger at the exact same time

**Which tool should you use?** Make (Integromat) gives you the most control over timing between Slack calls.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `{"ok":false,"error":"too_many_requests"}` (usually with HTTP 200, not 429)
- `{"ok":false,"error":"ratelimited"}` in your integration logs
- Your Slack integration works fine for single requests but fails when processing many at once
- Errors appear randomly during busy periods and then resolve on their own

**What it means in plain English:** You're sending too many Slack API requests at the same time. Unlike the per-method rate limit, this is a global burst limit — it counts all your requests together, not just one method.

**Most common cause:** A bot that processes many incoming messages at once, or a migration script that pulls data from multiple Slack endpoints without pausing between calls.

</div>

## What Causes Slack too_many_requests

Slack returns the `too_many_requests` error (not to be confused with HTTP 429 `rate_limited`) when your app exceeds Slack's rate limits but Slack does not provide a `Retry-After` header. This error appears in the response body as `{"ok":false,"error":"too_many_requests"}` with HTTP status 200 — Slack often returns 200 with an error field rather than using HTTP status codes for non-429 rate limit issues. See all [Slack API errors](/slack/) in our complete reference.

Similar rate limit issues occur with [HubSpot 429](/hubspot/errors/429), [Salesforce 429](/salesforce/errors/429), and [Pipedrive 429](/pipedrive/errors/429).

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

This error also affects integrations. See our [HubSpot to Slack](/integrations/hubspot-to-slack/), [Make to Slack](/integrations/make-to-slack/), and [ActiveCampaign to Slack](/integrations/activecampaign-to-slack/) integration error guides.

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
