---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Zapier API 429 Error: Rate Limit Exceeded — Fix & Prevention"
description: "Fix Zapier API 429 error. Rate limit exceeded. Wait 60 seconds (cooldown)."
tool: "zapier"
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
  - "zapier api 429 error"
  - "zapier 429 fix"
  - "zapier api rate limit exceeded"
  - "zapier http 429"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Zapier is rate limiting your API calls because your Zaps are running too many actions too fast.

**The fix:**
1. Wait 60 seconds — Zapier's cooldown period usually clears on its own
2. Slow down your Zap triggers — add a "Delay by Zapier" step between actions
3. If you have many Zaps running at once, stagger their schedules so they don't all fire at the same time

**Copy-paste this code** (if you're building a custom integration):
```python
import time, requests

resp = requests.get(url, headers=headers)
if resp.status_code == 429:
    wait = int(resp.headers.get("Retry-After", 60))
    time.sleep(wait)
    resp = requests.get(url, headers=headers)
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code fix](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm getting a 429 Too Many Requests error from Zapier.
> The error message says: "Rate limit exceeded" with a Retry-After header.
> My Zaps are running too many API calls and Zapier is throttling me.
> Please give me a step-by-step fix to slow down my Zaps and avoid hitting this rate limit again.

**What to expect:** The AI should show you how to add delays between Zap actions, reduce polling frequency, and set up retry logic.

**If it doesn't work**, add this follow-up:
> I added delays but I'm still getting 429 errors. Here's my Zap setup: [describe your Zaps]. What else can I do?

**Best AI tools for this:** Claude (great at explaining rate limit strategies), ChatGPT-4 (good at Zapier scheduling tips), Cursor (if you're writing custom retry code)

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write retry code? Here's how to handle Zapier rate limits in popular automation tools:

### Zapier
1. Open your Zap → add a "Delay by Zapier" step before the action that's getting rate limited (set to 60 seconds)
2. In your Zap settings, change the trigger polling interval to a longer time (e.g., every 15 minutes instead of every 5)
3. Go to "Zap History" (left sidebar) → check if multiple Zaps are failing at the same time → stagger their schedules

### Make (Integromat)
1. Open your scenario → right-click the module getting rate limited → "Add error handler" → choose "Retry"
2. Set the retry interval to 60 seconds and max retries to 3
3. Add a "Sleep" module (60 seconds) between API-heavy modules to space out requests

### n8n
1. Open your workflow → click the node getting 429 errors → go to "Settings" → enable "Retry on Fail"
2. Set "Wait Between Tries" to 60000ms (60 seconds) and "Max Tries" to 3
3. Add a "Wait" node (60 seconds) before the rate-limited node to slow down the workflow

### Power Automate
1. Open your flow → click the action getting throttled → go to "Settings" → enable "Retry Policy"
2. Set to "Exponential interval" with count 3 and minimum interval 60 seconds
3. Add a "Delay" action (60 seconds) before the throttled action to space out requests

**Which tool should you use?** Zapier's built-in "Delay by Zapier" step is the simplest fix — just drag it in before the failing action and set 60 seconds.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"429 Too Many Requests"`
- `"rate limit"`
- `"Rate limit exceeded"`
- `"Too many requests, please slow down"` in your Zap error log

**What it means in plain English:** Zapier is telling you to slow down. Your Zaps are making too many API calls in a short time, and Zapier is temporarily pausing you to protect its servers.

**Most common cause:** Multiple Zaps running at the same time, or a single Zap with a very fast trigger (like "every 1 minute") that fires too many actions per hour.

</div>

## What Causes Zapier 429

Zapier's API platform enforces rate limits to protect its infrastructure. The exact limits depend on your Zapier plan: Free/Starter plans have tighter limits, while Professional/Team/Company plans have higher caps. When you exceed the limit, Zapier returns HTTP 429 with a `Retry-After` header indicating the cooldown period in seconds.

The response includes `{"status":"error","message":"Rate limit exceeded"}`. Zapier uses a rolling window approach — each request resets the window rather than having fixed-minute boundaries. A 60-second cooldown period is typical after hitting the limit. See all [Zapier errors](/zapier/) in our complete reference.

This error also affects integrations. See our [Zapier to Calendly integration errors](/integrations/zapier-to-calendly/) for common cross-tool issues.

### Common Scenarios
- Polling the Zapier API faster than once per few seconds
- Running multiple parallel integrations against the same API key
- High-volume webhook triggers generating API calls faster than the plan allows
- A burst of requests after a long idle period (cold start)

## How to Detect If You're Affected

1. Check the Retry-After header in the response:
   ```bash
   curl -s -I "https://api.zapier.com/v2/..." \
     -H "Authorization: Bearer $TOKEN" 2>&1 | grep -i retry-after
   ```

2. Parse the response status code:
   ```python
   resp = requests.get(url, headers=headers)
   if resp.status_code == 429:
       retry_after = int(resp.headers.get("Retry-After", 60))
       print(f"Rate limited. Retry after {retry_after}s")
   ```

## Step-by-Step Fix

### 1. Wait the Cooldown Period
```python
import time

resp = requests.get(url, headers=headers)
if resp.status_code == 429:
    cooldown = int(resp.headers.get("Retry-After", 60))
    print(f"Rate limited — waiting {cooldown}s")
    time.sleep(cooldown)
    resp = requests.get(url, headers=headers)  # Retry
```

### 2. Implement Exponential Backoff
```python
import time, random

def zapier_request(url, headers, max_retries=5):
    for attempt in range(max_retries):
        resp = requests.get(url, headers=headers)
        if resp.status_code != 429:
            return resp
        wait = min(60, (2 ** attempt)) + random.uniform(0, 1)
        time.sleep(wait)
    raise Exception("Zapier 429 — max retries exceeded")
```

### 3. Reduce Request Frequency
If you're consistently hitting limits, add inter-request delays:
```python
import time

# Add 1-2 second delay between requests
for item in items:
    call_zapier_api(item)
    time.sleep(1.5)
```

## Prevention

- Add a minimum 1-second delay between API calls to stay well within rate limits
- Cache API responses that don't change frequently (schema lookups, user info)
- Use Zapier's webhook-triggered approach instead of polling where possible
- Upgrade your Zapier plan if you consistently exceed the rate allocation
- Monitor `X-RateLimit-Remaining` headers (if available) and slow down proactively
- Similar rate limit issues occur with [Salesforce 429](/salesforce/errors/429), [Slack rate_limited](/slack/errors/rate_limited), and [Pipedrive 429](/pipedrive/errors/429).

## Official Documentation

- [Zapier Platform API](https://platform.zapier.com/)
- [Zapier API Authentication](https://platform.zapier.com/docs/auth)
- [Zapier Status Page](https://status.zapier.com/)

## People Also Ask

- **What is Zapier's API rate limit?** Limits vary by plan. Free/Starter plans have lower limits (typical ~10 req/min), while higher-tier plans get increased allocations. Exact numbers are not publicly documented.
- **How long does a Zapier rate limit cooldown last?** The `Retry-After` header typically indicates 60 seconds, but it can vary based on the severity of the rate limit breach.
- **Does each Zapier API key have its own rate limit?** Yes — rate limits are applied per API key/authentication. Using multiple API keys can increase your effective throughput.
- **Can I request a higher rate limit from Zapier?** Zapier does not publicly offer rate limit increases. Upgrade your plan or distribute calls across multiple API keys.

## Related Errors

- [Zapier 500 Server Error](/zapier/errors/500) — Server error
- [Zapier 401 Unauthorized](/zapier/errors/401) — Invalid or expired access token
- [Zapier 400 Bad Request](/zapier/errors/400) — Malformed request
