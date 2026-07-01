---
layout: ../../layouts/IntegrationErrorLayout.astro
title: "Salesforce Daily API Limit Exhausted by ActiveCampaign Bidirectional Sync"
description: "Bidirectional Salesforce ↔ ActiveCampaign sync burns the Salesforce 24-hour API allocation. Combined with other integrations, calls are expended by mid-day. Fix with Bulk API 2.0, scheduling, and field-level sync filters."
toolA: "salesforce"
toolB: "activecampaign"
integrationSlug: "salesforce-to-activecampaign"
errorSlug: "salesforce-daily-api-limit-exhausted-by-ac-sync"
errorName: "Salesforce daily API limit exhausted by AC sync"
category: "RATE_LIMIT"
errorType: "error"
severity: "high"
priority: 2
lastUpdated: "2026-05-15"
lastReviewed: "2026-05-15"
pageType: "integration-error"
author: "API Integration Hub"
keywords:
  - "salesforce api request limit exceeded"
  - "activecampaign salesforce bidirectional sync api calls"
  - "salesforce bulk api 2.0 activecampaign"
  - "salesforce 24 hour api limit by edition"
  - "salesforce rest api vs bulk 2.0 limit"
  - "activecampaign salesforce rate limit exhausted"
---


<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** ActiveCampaign's bidirectional sync exhausts Salesforce's daily API limit by mid-day. The sync polls Salesforce REST endpoints every minute, burning through the org-wide allocation and breaking every other integration.

**The fix:**
1. Check Salesforce API usage: Setup > Integrations > API Use
2. Switch from REST polling to Salesforce Bulk API 2.0 (1 call per million records)
3. Reduce sync frequency -- schedule incremental syncs off-peak (e.g., 2 AM UTC)
4. Add field-level filters so only relevant field changes trigger the ActiveCampaign sync

**Copy-paste this code** (if you're using a code editor):
```python
import requests

r = requests.get(f"https://{instance}.my.salesforce.com/services/data/v60.0/limits",
    headers={"Authorization": f"Bearer {token}"})
limits = r.json()["DailyApiRequest"]
print(f"Remaining: {limits['Remaining']} of {limits['Max']}")
if limits["Remaining"] < limits["Max"] * 0.2:
    print("WARNING: Below 20% - reduce sync frequency")
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code workaround](#no-code-workaround).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Give your AI assistant the full picture of both tools involved:

> I'm integrating Salesforce with ActiveCampaign and the sync exhausts Salesforce's daily API limit by mid-day. The bidirectional sync polls REST endpoints every minute, consuming the org-wide quota. How do I reduce API calls using Bulk API 2.0 and scheduling?

The AI should provide help switching to Bulk API 2.0, scheduling off-peak syncs, and adding field-level filters.

If the first attempt misses a tool-specific detail, follow up with:
> I switched to Bulk API 2.0 but the limit is still being hit. Could other integrations in the org be sharing the same quota?

</div>

## No-Code Workaround <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to debug this? Here's how to reduce Salesforce API usage for ActiveCampaign syncs in other tools:

### Zapier
1. Use Zapier's native Salesforce trigger ('New or Updated Record') -- it uses webhooks, not polling
2. Reduce Zap polling frequency to every 15 minutes instead of every minute
3. Add a 'Filter' step to only sync records with relevant field changes

### Make (Integromat)
1. Use Make's Salesforce 'Watch Records' module with a longer polling interval
2. Add a filter to only process records where subscribed fields changed
3. Use Make's HTTP module to call Salesforce Bulk API 2.0 for large datasets

### n8n
1. Use the Salesforce trigger node with event-based listening instead of polling
2. Add an IF node to filter records by relevant field changes
3. Schedule the workflow to run off-peak using a Cron trigger

### Power Automate
1. Use the Salesforce 'When a record is modified' trigger for event-based sync
2. Add a Condition to filter only relevant field changes
3. Schedule the flow to run during off-peak hours

**Which tool should you use?** Zapier is the easiest -- its native Salesforce trigger uses webhooks instead of polling, dramatically reducing API calls.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these:

- Salesforce returns REQUEST_LIMIT_EXCEEDED for all integrations by mid-day
- ActiveCampaign sync accounts for more than 50% of Salesforce API usage
- Other integrations (Mulesoft, Boomi, native apps) start failing
- Salesforce API Usage dashboard shows rapid consumption starting at sync times

**What it means in plain English:** The ActiveCampaign sync polls Salesforce REST endpoints too frequently, consuming the org-wide daily API allocation. Once exhausted, every integration in the org stalls.

**Most common cause:** Using REST polling (per-record GET calls) instead of Bulk API 2.0 query jobs, which consume 1 call per million records.

</div>

## The Problem

Bidirectional Salesforce ↔ ActiveCampaign syncs return `REQUEST_LIMIT_EXCEEDED` to every other integration in the org by mid-day. See all [Salesforce API errors](/salesforce/) or [ActiveCampaign API errors](/activecampaign/) for more troubleshooting. Users see failures in unrelated Mulesoft, Boomi, and native apps because the shared 24-hour Salesforce API quota was consumed by ActiveCampaign polling. Once exhausted, all API integrations stall until the next rolling day.

## Root Cause

- **Salesforce 24-hour rolling limit** is not per-user or per-app — allocations are **org-wide**. Enterprise edition ships 1,000,000 calls/24h; Professional 1,000/hour and a daily cap. A single chatty AC sync eats the entire org's allocation.
- **Polling anti-pattern**: ActiveCampaign's connector polls Salesforce every minute via REST (`query`), issuing hundreds of REST calls even when no records changed.
- **SOQL `SELECT COUNT()` and per-record `GET /sobjects/Contact/{id}` are full API calls**. A 50k-contact sync that fetches one-by-one consumes 50,000 calls.
- **Bulk API 2.0** (`/services/data/v60.0/jobs/query`) consumes only 1 call per job, not per record. Related: [Salesforce 429](/salesforce/errors/429) for rate limit issues, [ActiveCampaign 429](/activecampaign/errors/429) for AC rate limits.

| Edition | 24h limit | Notes |
|---|---|---|
| Professional | 1,000/hr cap, low daily | Unsuited for bulk syncs |
| Enterprise | 1,000,000/24h | Default for orgs |
| Unlimited | 5,000,000/24h | Add-on parity available |
| Developer | ~100,000/day | Capped; not for prod integrations |

## How to Detect If You're Affected

1. Inspect the Salesforce "API Usage" under Setup → Integrations → API Use; the ActiveCampaign user measurement accounts for >50% of allocation.
2. Hit Salesforce Limits API:
   ```bash
   SF_TOKEN="..."
   curl -s "https://$INSTANCE.my.salesforce.com/services/data/v60.0/limits" \
     -H "Authorization: Bearer $SF_TOKEN" | \
     jq '.DailyApiRequest | "remaining \(.Remaining) of \(.Max), used concurrently: \(.ConcurrentRequest)"'
   ```
3. Logs of the failure (`REQUEST_LIMIT_EXCEEDED`):
   ```bash
   rg 'REQUEST_LIMIT_EXCEEDED' middleware.log
   ```
4. Symptom: every outlier integration returns `REQUEST_LIMIT_EXCEEDED` from `14:00 UTC` onward daily.

## Step-by-Step Fix

1. Replace REST polling with Salesforce Bulk API 2.0 query jobs:
   ```bash
   # create a query job
   JOB=$(curl -s -X POST "https://$INSTANCE.my.salesforce.com/services/data/v60.0/jobs/query" \
     -H "Authorization: Bearer $SF_TOKEN" -H "Content-Type: application/json" \
     -d '{"operation":"query","query":"SELECT Id, Email, LastModifiedDate FROM Contact WHERE LastModifiedDate >= YESTERDAY"}')
   JOB_ID=$(echo $JOB | jq -r '.id')
   ```
   This consumes **1 call per million records**, vastly cheaper than per-row REST reads.
2. Schedule incremental syncs off-peak:
   ```yaml
   # cron: 02:00 UTC daily — outside business hours
   0 2 * * * /opt/sf-ac/sync.sh incr
   ```
3. Add field-level sync filters so only changes on subscribed fields trigger the AC sync:
   ```python
   relevant_fields = {"Email", "FirstName", "LastName", "MailingPostalCode"}
   if set(payload["changed_fields"]) & relevant_fields:
       sync_to_ac(payload)
   ```
4. Wrong: synchronous REST `for row in rows: GET /sobjects/.../{id}`. Correct: single Bulk API 2.0 query returning all rows in one job.
5. Cache Salesforce Id → ActiveCampaign contact Id in the middleware so updates do not need an `AccountContact` lookup per record.

## Prevention

- Use Salesforce change-data-capture (CDC) events to push changed records to your middleware instead of polling — CDC consumes 0 REST calls per change.
- Set the integration user to a "low priority" profile that shares a smaller custom API limit; isolate ActiveCampaign from critical integrations.
- Cap each incremental sync run at a defined "API budget" (e.g., 50,000 calls) and abort if exceeded, escalating an alert regardless of how many records are processed.
- Monitor `/limits` every 5 minutes; alert when daily remaining drops below 20% before 12:00 local time.
- Audit field-level sync filters quarterly to abort syncing irrelevant fields like `LastReferencedDate` that change constantly but never matter downstream.

## Integration-Specific Context

- **Native ActiveCampaign-Salesforce connector**: uses REST polling by default; you must reconfigure to use Change Data Capture if available (late-2026 release only in beta).
- **Zapier Salesforce-AC**: REST-based; rarely approaches the limit alone but compounds when multiple Zaps run for the same object.
- **Make**: Bulk API 2.0 requires the "HTTP" raw module — Make's Salesforce app does not yet expose queries as jobs.
- **Custom middleware**: own the Bulk API 2.0 path (snippet above) for any sync above 5,000 records.
- **2026 change**: Salesforce moved Bulk API v1 to "deprecated" status — use v2 (`/jobs/query`) only. The single-call query job also moves to async notification by default.

## People Also Ask

- **What is Salesforce's daily API limit?** Enterprise edition grants 1,000,000 API requests per rolling 24 hours at the org level, shared across every integration. Professional is capped per hour (1,000/h).
- **Why does my ActiveCampaign-Salesforce sync exhaust the org's API quota?** The connector polls Salesforce REST endpoints every minute and issues per-record `GET` calls, rapidly consuming the daily allocation shared by every other integration.
- **How do I reduce Salesforce API calls from ActiveCampaign syncs?** Use Salesforce Bulk API 2.0 query jobs (1 call per million records), Change Data Capture events, and field-level filter rules that ignore irrelevant changes.
- **Does Salesforce's API limit reset at midnight?** No — it is a rolling 24-hour window, and once exhausted, every other integration also gets `REQUEST_LIMIT_EXCEEDED` until the window frees up.

## Official Documentation

**Salesforce:**
- [REST API](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/)
- [Bulk API](https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/)
- [Limits](https://developer.salesforce.com/docs/atlas.en-us.salesforce_app_limits_cheatsheet.meta/salesforce_app_limits_cheatsheet/)

**ActiveCampaign:**
- [API Overview](https://developers.activecampaign.com/reference/overview)
- [Authentication](https://developers.activecampaign.com/reference/authentication)

## Related Errors
- [Zoho API rate limit (250 req/min)](/integrations/zoho-to-mailchimp/errors/zoho-api-rate-limit-(250-req-min))
- [Custom field type mismatch (Salesforce ↔ ActiveCampaign)](/integrations/salesforce-to-activecampaign/errors/custom-field-type-mismatch)
- [ContactTag wrapper bug (Salesforce ↔ ActiveCampaign)](/integrations/salesforce-to-activecampaign/errors/contacttag-wrapper-bug)
- [Salesforce API Reference](/salesforce)
- [ActiveCampaign API Reference](/activecampaign)