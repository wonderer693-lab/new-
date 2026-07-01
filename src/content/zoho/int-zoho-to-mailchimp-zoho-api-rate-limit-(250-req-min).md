---
layout: ../../layouts/IntegrationErrorLayout.astro
title: "Zoho API Rate Limit 250 req/min — Mailchimp Bulk Contact Sync Stalls"
description: "Bulk Zoho CRM to Mailchimp contact syncs exceed the 250 requests/minute Zoho API limit and fail midway. Implement 250 RPM throttling, exponential backoff on 429, and Coql batch queries to fix stalled syncs."
toolA: "zoho"
toolB: "mailchimp"
integrationSlug: "zoho-to-mailchimp"
errorSlug: "zoho-api-rate-limit-(250-req-min)"
errorName: "Zoho API rate limit (250 req/min)"
category: "RATE_LIMIT"
errorType: "error"
severity: "high"
priority: 2
lastUpdated: "2026-06-09"
lastReviewed: "2026-06-09"
pageType: "integration-error"
author: "API Integration Hub"
keywords:
  - "zoho crm 250 requests per minute limit"
  - "zoho mailchimp bulk sync 429"
  - "zoho api rate limit retry after header"
  - "zoho coql batch query limit"
  - "zoho to mailchimp sync stalls midway"
  - "zoho crm rate limit 2026"
---


<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Zoho CRM's 250 requests/minute API rate limit is hit during Mailchimp bulk sync. The sync stalls after a few hundred records and requires manual re-runs.

**The fix:**
1. Add a rate limiter to pace Zoho API calls at 240 requests/minute (leave headroom)
2. Use Zoho Coql batch queries to fetch 200 records per call instead of one-by-one
3. Add exponential backoff on 429 errors -- honor the Retry-After header
4. Bookmark sync progress by last_modified_time so stalled batches resume, not restart

**Copy-paste this code** (if you're using a code editor):
```python
import time

class ZohoLimiter:
    def __init__(self, rpm=240):
        self.calls = []
        self.rpm = rpm
    def acquire(self):
        now = time.monotonic()
        self.calls = [t for t in self.calls if now - t < 60]
        if len(self.calls) >= self.rpm:
            time.sleep(60 - (now - self.calls[0]))
        self.calls.append(time.monotonic())
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code workaround](#no-code-workaround).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm integrating Zoho CRM with Mailchimp and bulk syncs stall after a few hundred records. Zoho returns 429 'Rate Limit Exceeded' at 250 requests/minute. How do I pace API calls and use batch queries to sync large contact lists?

**What to expect:** The AI should help you implement rate limiting, batch queries, and resume bookmarks for Zoho-to-Mailchimp syncs.

**If it doesn't work**, add this follow-up:
> I added rate limiting but the sync is still too slow for 10,000 contacts. Can I use Zoho's bulk export API instead of Coql?

**Best AI tools for this:** ChatGPT-4 (good at step-by-step UI navigation), Claude (good at explaining API concepts)

</div>

## No-Code Workaround <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to debug this? Here's how to handle Zoho rate limits in Mailchimp syncs using other tools:

### Zapier
1. Use Zapier's 'Delay After Queue' to throttle Zoho API calls
2. Add a 'Delay by Zapier' step (1 second) between Zoho fetch actions
3. Split contacts into batches of 200 with delays between each batch

### Make (Integromat)
1. Use Make's built-in rate-limit module with a 60-second window
2. Add an 'Array Aggregator' to chunk contacts into 200-record batches
3. Add a 'Sleep' module between batches to stay under 250 RPM

### n8n
1. Use a 'Wait' node between Zoho API calls to pace at 240 RPM
2. Use the 'Split In Batches' node to process contacts in groups
3. Add error handling to catch 429 and wait for the Retry-After period

### Power Automate
1. Add a 'Delay' action between Zoho API calls
2. Use 'Apply to each' with sequential processing and delays
3. Add error handling with retry on 429 responses

**Which tool should you use?** Zapier is the easiest -- its Delay action lets you throttle Zoho calls without building a custom rate limiter.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these:

- Zoho returns 429 'Rate Limit Exceeded' during Mailchimp sync
- Sync stalls after 200-300 records and requires manual re-runs
- Middleware logs show X-RateLimit-Remaining: 0 from Zoho
- Re-running the sync repeats the first records because the cursor was lost

**What it means in plain English:** Your Zoho-to-Mailchimp sync exceeds Zoho's 250 requests/minute limit. The rolling 60-second window means you can't burst and wait -- you must pace continuously.

**Most common cause:** Making too many Zoho API calls per minute without rate limiting, batch queries, or progress bookmarks.

</div>

## The Problem

A 10,000-contact Zoho-to-Mailchimp sync routinely stalls after a few hundred records, leaving the Mailchimp audience partially populated and requiring hours of manual re-runs. The middleware stops because Zoho returns `429 Too Many Requests` once the rolling 60-second window exceeds 250 calls, and most middleware aborts the batch instead of waiting.

## Root Cause

- **Allocation**: Zoho CRM REST API applies a rolling per-minute allocation: **250 requests/minute** on Standard edition (Enterprise: 1,000/min). The counter resets on a sliding 60 s window, not at the top of the minute.
- **Headers**: responses include `X-RateLimit-Remaining` and `X-RateLimit-Limit`; 429 includes a `Retry-After` (seconds) header.
- **Coql**: the Query Language endpoint is itself rate-limited — 200 queries/min, max 200 records returned per query.
- **Pagination overhead**: each `Contacts` list page = 1 call; a 10k sync with page-size 200 = 50 reads + 10k writes = 10,050 calls = 40 minutes at the limit even with perfect pacing.
- **Webhook fan-out**: every Zoho webhook that triggers a downstream GET back to Zoho during the sync eats into the same minute window.

| Limit tier | req/min | What counts |
|---|---|---|
| Standard | 250 | All REST endpoints, including `/coql` |
| Professional | 250 (same) | — |
| Enterprise | 1,000 | Higher burst tolerance |
| Unlimited (Zoho One add-on) | 1,000 | Add-on must be enabled |

## How to Detect If You're Affected

1. Look in middleware logs for `429` and the response header `X-RateLimit-Remaining: 0`.
2. Check the response body — Zoho returns:
   ```json
   {"code":"RATE_LIMIT_EXCEEDED","message":"Rate limit exceeded. Try after some time"}
   ```
3. Diagnose cumulative burn rate:
   ```bash
   grep -c ' POST .*crm/v2/Contacts' middleware.log
   # divide by elapsed minutes; > 250 means you are throttled
   ```
4. Symptom: syncs repeat the first 200–300 records on re-run because the cursor was lost when the batch died.

## Step-by-Step Fix

1. Implement a token-bucket limiter at 240 RPM (leave headroom for webhook-triggered reads):
   ```python
   import time, threading
   class ZohoLimiter:
       def __init__(self, rpm=240):
           self.min_window = 60.0
           self.max_calls = rpm
           self.calls = []
           self.lock = threading.Lock()
       def acquire(self):
           with self.lock:
               now = time.monotonic()
               self.calls = [t for t in self.calls if now - t < self.min_window]
               if len(self.calls) >= self.max_calls:
                   time.sleep(self.min_window - (now - self.calls[0]))
               self.calls.append(time.monotonic())
   ```
2. Use Coql to fetch in batches of 200 to minimize read calls:
   ```bash
   curl -s "https://www.zohoapis.com/crm/v2/coql" \
     -H "Authorization: Zoho-oauthtoken $TOKEN" \
     -d '{"select_query":"select id, Email, First_Name from Contacts where Modified_Time >= '\''2026-06-25T00:00:00Z'\'' limit 0,200"}'
   ```
3. Wrong: parallelize 20 worker threads — they share the same org allocation and hit 429 instantly. Correct: serialize writes or partition by record-id ranges with a separate limiter instance counting into the same global budget.
4. Retry on 429 honoring `Retry-After`:
   ```python
   r = requests.post(url, json=payload, headers=h)
   if r.status_code == 429:
       wait = int(r.headers.get("Retry-After", "5"))
       time.sleep(wait)
       return post_with_retry(url, payload)  # one retry
   ```
5. Add a `last_modified_time` bookmark so a stalled batch resumes where it died instead of restarting from offset 0.

## Prevention

- Default your sync cadence to a continuous loop with a steady pace, not a midnight burst — Zoho's rolling window penalizes spikes.
- Use Coql bulk queries (`limit 0,200` increments) for reads and the Records API `insert`/`update` endpoint (`up to 100 records per call`) for Mailchimp-write-side fetches — but keep Zoho writes under 200 records/call.
- Cache `X-RateLimit-Remaining` and slow down when it drops below 20; never blow through it.
- Disable webhook subscriptions on the Zoho org during bulk migration so every change event does not back-feed into the rate window.
- Surface 429 events as an explicit alert in your APM since middleware often logs them as warnings, not errors.

## Integration-Specific Context

- **Native Zoho-MC connector**: handles pacing internally but pauses syncs for the full minute on a 429 — visible only in connector logs.
- **Zapier**: each Zap step counts as a Zoho call; running multiple Zaps against one org multiplies burn. Use the "Delay after queue" option.
- **Make (Integromat)**: use the built-in rate-limit module (60 s window) and the "Array Aggregator" to chunk 100-record payloads.
- **Custom middleware**: implement the limiter above and remember Zoho's window slides — it is not safe to do 250 calls at second 0 then wait 59 s.
- **2026 change**: Zoho deprecated the ` Pregnancy exception` "10 req/sec burst" carve-out for Enterprise; you now share the single 1000/min budget across all concurrent connections.

## People Also Ask

- **What is the Zoho CRM API rate limit?** 250 requests/minute on Standard edition and 1,000/minute on Enterprise, measured on a rolling 60-second window shared across all connections in the org.
- **Does Zoho return a `Retry-After` header on 429?** Yes, in seconds. Use it before retrying, or you will be banned from the window again.
- **How many records can Zoho Coql return per query?** 200 records per query, and Coql itself is capped at 200 queries/minute.
- **How do I avoid stalling my Zoho-to-Mailchimp bulk sync?** Pace at 240 RPM, fetch via Coql in 200-record pages, and bookmark by `Modified_Time` so a stalled batch resumes.

## Official Documentation

**Zoho CRM:**
- [API Docs](https://www.zoho.com/crm/developer/docs/api/v3/)
- [Rate Limits](https://www.zoho.com/crm/developer/docs/api/v3/api-limits.html)

**Mailchimp:**
- [API Docs](https://mailchimp.com/developer/marketing/api/)
- [Lists](https://mailchimp.com/developer/marketing/api/lists/)

## Related Errors
- [Zoho OAuth token expires every hour](/integrations/zoho-to-mailchimp/errors/zoho-oauth-token-expires-every-hour)
- [Zoho contact duplicate detection differs from Mailchimp](/integrations/zoho-to-mailchimp/errors/zoho-contact-duplicate-detection-differs-from-mailchimp)
- [Salesforce daily API limit exhausted by AC sync](/integrations/salesforce-to-activecampaign/errors/salesforce-daily-api-limit-exhausted-by-ac-sync)
- [Zoho CRM API Reference](/zoho)
- [Mailchimp API Reference](/mailchimp)