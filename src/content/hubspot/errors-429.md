---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "HubSpot API 429 Too Many Requests — Production Retry Strategy (2026)"
description: "Fix HubSpot API 429 rate limit errors in production. Exponential backoff, jitter, batch queuing, and 2026 rate limit header changes for public and private apps."
tool: "hubspot"
errorCode: "429"
errorName: "Too Many Requests"
httpStatus: 429
category: "rate-limit"
severity: "high"
priority: 1
lastUpdated: "2026-05-29"
keywords:
  - "hubspot api 429 fix"
  - "hubspot rate limit retry strategy"
  - "hubspot exponential backoff"
  - "hubspot 429 production code"
  - "hubspot api rate limit 2026"
  - "hubspot 110 requests per 10 seconds"
  - "hubspot retry-after header"
---

<div class="urgency-banner">
  <strong>Critical:</strong> HubSpot's March 2026 API update changed rate limit headers and limits.
  Existing retry logic may no longer work. See <a href="#2026-changes">2026 changes</a> below.
</div>

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** You're sending too many requests to HubSpot's API too fast, and HubSpot is temporarily blocking you.

**The fix:**
1. Wait for the number of seconds shown in the `Retry-After` header (usually 10 seconds)
2. Slow down your requests — don't send more than 11 per second
3. If you're doing a bulk import, split it into smaller batches

**Copy-paste this code** (if you're using a code editor):
```python
import time, requests

resp = requests.get(url, headers=headers)
if resp.status_code == 429:
    wait = int(resp.headers.get("Retry-After", 10))
    time.sleep(wait)
    resp = requests.get(url, headers=headers)
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Send this to your AI coding assistant and ask it to generate working code:

> I'm getting a 429 Too Many Requests error from the HubSpot API.
> The error message is: "You have reached your ten second limit"
> I'm using a custom integration that makes API calls to HubSpot.
> Please give me a step-by-step fix with working Python code that handles rate limiting.

You want code that the AI should give you a retry function with exponential backoff and explain HubSpot's rate limits.

If the generated code doesn't handle the edge cases, refine with:
> The fix didn't work. I'm still getting 429 errors. Here's what I tried: [paste your code]. Please debug this.

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to handle HubSpot rate limits in popular automation tools:

### Zapier
1. Open your Zap → click the HubSpot action step
2. Enable "Auto-retry on error" in the step settings (Zapier auto-retries 429 errors up to 3 times)
3. If you're hitting limits frequently, add a "Delay by Zapier" step before the HubSpot action (set to 10 seconds)

### Make (Integromat)
1. Open your scenario → right-click the HubSpot module → "Add error handler"
2. Choose "Retry" → set interval to 10 seconds, max retries to 3
3. For bulk operations, add a "Sleep" module (10 seconds) between HubSpot calls

### n8n
1. Open your workflow → click the HubSpot node
2. In "Settings" → enable "Retry on Fail" → set "Wait Between Tries" to 10000ms, "Max Tries" to 3
3. For bulk operations, add a "Wait" node (10 seconds) between HubSpot nodes

### Power Automate
1. Open your flow → click the HubSpot action
2. In "Settings" → enable "Retry Policy" → set to "Exponential interval" with count 3
3. For bulk operations, add a "Delay" action (10 seconds) before the HubSpot action

**Which tool should you use?** Zapier has the best built-in retry for HubSpot — it handles 429 errors automatically without any configuration.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"You have reached your ten second limit"`
- `"429 Too Many Requests"`
- `"Rate limit exceeded. Please retry after X seconds"`
- `"HTTP 429"` in your integration logs

**What it means in plain English:** HubSpot is telling you to slow down. You're making too many API calls in a short time. Wait a few seconds and try again.

**Most common cause:** Bulk imports or sync jobs that fire too many requests at once without pausing between them.

</div>

## What Causes HubSpot 429

HubSpot enforces rate limits per API key/application. Hitting the limit returns HTTP 429 with a `Retry-After` header. See all [HubSpot API errors](/hubspot/) in our complete reference.

This error also affects integrations. See our [HubSpot to Slack integration errors](/integrations/hubspot-to-slack/) for common cross-tool issues.

### Current Limits (March 2026+)
- **Public OAuth apps**: 110 requests per 10 seconds per installed account
- **Private apps**: Varies by app type — check your dashboard
- **Batch API**: 200 objects per call (use batching to reduce call count)

### Common Triggers
- Bulk import jobs sending > 110 requests in 10 seconds
- Webhook handler that makes API calls without queuing — bursts on mass update
- Multiple Lambda/serverless instances sharing the same API key (parallel concurrency)
- Polling loop with no delay between iterations

## Production Retry Strategy

### Minimal Fix (Copy-Paste Ready)

```python
import time
import random
import requests

def hubspot_request(url, headers, max_retries=5):
    for attempt in range(max_retries):
        resp = requests.get(url, headers=headers)
        if resp.status_code != 429:
            return resp

        retry_after = int(resp.headers.get("Retry-After", 1000))
        jitter = random.randint(0, 1000)
        wait = (retry_after * 1000) + jitter
        time.sleep(wait / 1000)

    raise Exception("HubSpot 429 — max retries exceeded")
```

### Production Queue (Recommended)

```python
import asyncio
import time
import random

class HubSpotRateLimiter:
    def __init__(self, max_rpm=660, window_s=10):
        self.max_rpm = max_rpm
        self.window_s = window_s
        self.tokens = max_rpm
        self.last_refill = time.monotonic()
        self.queue = asyncio.Queue()
        self.lock = asyncio.Lock()

    async def _refill(self):
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.max_rpm,
                         self.tokens + elapsed * (self.max_rpm / self.window_s))
        self.last_refill = now

    async def acquire(self):
        async with self.lock:
            await self._refill()
            while self.tokens < 1:
                wait = (1 - self.tokens) * (self.window_s / self.max_rpm)
                await asyncio.sleep(wait)
                await self._refill()
            self.tokens -= 1

    async def request(self, session, method, url, **kwargs):
        await self.acquire()
        for attempt in range(5):
            async with session.request(method, url, **kwargs) as resp:
                if resp.status != 429:
                    return resp
                retry_after = int(resp.headers.get("Retry-After", 1))
                jitter = random.uniform(0, 1)
                await asyncio.sleep(retry_after + jitter)
        raise Exception("429 max retries exceeded")

# Usage
limiter = HubSpotRateLimiter()
results = await asyncio.gather(*[
    limiter.request(session, "GET", url) for url in urls
])
```

### Exponential Backoff with Jitter

| Attempt | Base Wait | Jitter (0-1s) | Total Wait |
|---------|-----------|---------------|------------|
| 1 | 1s | 0.37s | 1.37s |
| 2 | 2s | 0.81s | 2.81s |
| 3 | 4s | 0.12s | 4.12s |
| 4 | 8s | 0.94s | 8.94s |
| 5 | 16s | 0.45s | 16.45s |

**Rule**: After 5 retries, push to dead-letter queue. Do NOT retry indefinitely.

## 2026 Changes

HubSpot's March 2026 date-versioned API update changed rate limit behavior:

| Change | Before 2026 | After March 2026 |
|--------|-------------|-------------------|
| Rate limit header | `X-HubSpot-RateLimit-Secondly` | New format — check `Retry-After` |
| Public app limit | 100 req/10s | 110 req/10s per installed account |
| OAuth token TTL | 6h (fixed) | Configurable 1-6 hours |
| Private app limits | Fixed | Varies by app type |

**If your retry logic parses the old header format, update it now.**

## How to Detect If You're Affected

1. Check the `Retry-After` header in the 429 response — it tells you how many seconds to wait:
   ```bash
   curl -s -I https://api.hubapi.com/crm/v3/objects/contacts \
     -H "Authorization: Bearer $TOKEN" | grep -i retry-after
   ```
2. Monitor HubSpot's rate limit headers on every response:
   ```python
   remaining = resp.headers.get("X-HubSpot-RateLimit-Daily-Remaining")
   print(f"Daily calls remaining: {remaining}")
   ```
3. Check HubSpot Operations Hub > API Usage dashboard for real-time consumption graphs.
4. Symptom: bulk operations fail mid-run with 429, while single-record operations succeed.

## Prevention

1. **Batch API**: Use POST `/crm/v3/objects/{object}/batch/read` — 200 objects per call
2. **Webhook queuing**: Don't make API calls inside webhook handlers. Push to queue, process in batches
3. **Connection pooling**: Reuse HTTP connections (requests.Session, aiohttp.ClientSession)
4. **Monitoring**: Set up alert in HubSpot Operations Hub for API usage > 80%
5. **Key isolation**: Different workflows = different API keys (don't share across parallel services)
6. Similar rate limit issues occur with [Salesforce 429](/salesforce/errors/429), [Slack rate_limited](/slack/errors/rate_limited), and [Pipedrive 429](/pipedrive/errors/429).

## People Also Ask

- **What is HubSpot's API rate limit?** Public OAuth apps get 110 requests per 10 seconds per installed account (since March 2026). Private apps vary by tier: Starter 100/10s, Professional 190/10s, Enterprise 190/10s with higher daily limits.
- **Does HubSpot 429 apply per API key or per app?** Per installed account for OAuth apps. Each HubSpot account that installs your app has its own 110/10s limit. Private apps share a single account's limit.
- **Can I request a HubSpot rate limit increase?** Yes — HubSpot offers up to 2 increases of 250 req/10s and 1M additional daily calls. Contact your account manager or HubSpot support.
- **Why does HubSpot 429 not include Retry-After sometimes?** The header is always present on 429 responses. If missing, check that your HTTP client isn't stripping it. The value is in seconds (not milliseconds).

## Official Documentation

- [HubSpot API Overview](https://developers.hubspot.com/docs/api/overview)
- [HubSpot OAuth Guide](https://developers.hubspot.com/docs/api/oauth-quickstart-guide)
- [HubSpot Rate Limits](https://developers.hubspot.com/docs/api/usage-details)
- [HubSpot CRM API](https://developers.hubspot.com/docs/api/crm/overview)

## Related Errors
- [HubSpot 401 Unauthorized](/hubspot/errors/401) — expired OAuth token
- [Salesforce INVALID_SESSION_ID](/salesforce/errors/INVALID_SESSION_ID) — session management
- [ActiveCampaign ContactTag 400](/activecampaign/errors/400) — payload format bug