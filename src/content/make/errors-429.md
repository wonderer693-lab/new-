---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Make API 429 Error: Rate Limit Exceeded — Fix & Prevention"
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

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Make is rate limiting your API calls — you're making too many requests too fast.

**The fix:**
1. Wait 60 seconds for Make's rate limit to reset (check the `Retry-After` header)
2. Slow down your scenario — add delays between API calls
3. Reduce how often your scenario runs (change from every 1 minute to every 5 minutes)

**Copy-paste this code** (if you're using a code editor):
```python
import time, requests

resp = requests.get(url, headers=headers)
if resp.status_code == 429:
    wait = int(resp.headers.get("Retry-After", 60))
    time.sleep(wait)
    resp = requests.get(url, headers=headers)
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm getting a 429 Too Many Requests error from Make (Integromat).
> The error message is: "Rate limit exceeded"
> I'm running a Make scenario that makes many API calls and it's hitting the rate limit.
> Please give me a step-by-step fix to reduce scenario frequency and add delays.

**What to expect:** The AI should help you adjust your scenario scheduling and add proper delays between API calls.

**If it doesn't work**, add this follow-up:
> The fix didn't work. I'm still getting 429 errors. Here's my scenario schedule: [paste settings]. Please debug this.

**Best AI tools for this:** Claude (best at explaining rate limit strategies), ChatGPT-4 (good at scheduling optimization), Cursor (if you want inline code fixes)

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to fix Make 429 errors in popular automation tools:

### Make (Integromat)
1. Open your scenario → click the scheduling clock icon → increase the interval (e.g., from 1 min to 5 min)
2. Add a "Sleep" module between API calls to pause for 10-30 seconds
3. Right-click modules → "Add error handler" → choose "Retry" with a 60-second interval

### Zapier
1. Open your Zap → add a "Delay by Zapier" step before the Make action (set to 60 seconds)
2. Reduce Zap frequency — change from "Instant" to "Every 15 minutes" in the trigger settings
3. Enable "Auto-retry on error" in the Make action step settings

### n8n
1. Open your workflow → click the trigger node → increase the polling interval
2. Add a "Wait" node (60 seconds) between Make API calls
3. In node settings → enable "Retry on Fail" → set wait time to 60000ms

### Power Automate
1. Open your flow → click the trigger → increase the recurrence interval
2. Add a "Delay" action (60 seconds) before the Make action
3. In the Make action settings → enable "Retry Policy" → set to "Fixed interval" with 60-second waits

**Which tool should you use?** Make's own scheduling settings are best — adjust the scenario frequency directly in the Make UI.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"429 Too Many Requests"`
- `"rate limit"`
- `"Rate limit exceeded"`
- `"Organization API limit reached"` in your Make logs

**What it means in plain English:** Make is telling you to slow down. You're making too many API calls in a short time. Wait a minute and reduce how often your scenarios run.

**Most common cause:** Scenarios running too frequently (every 1 minute) or making too many individual API calls instead of batching them.

</div>

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
