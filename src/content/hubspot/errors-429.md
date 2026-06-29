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

## What Causes HubSpot 429

HubSpot enforces rate limits per API key/application. Hitting the limit returns HTTP 429 with a `Retry-After` header.

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