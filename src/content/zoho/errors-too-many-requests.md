---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Zoho API TOO_MANY_REQUESTS: Daily credit limit exceeded"
description: "Fix Zoho API TOO_MANY_REQUESTS error. Daily credit limit exceeded. Check remaining credits via API."
tool: "zoho"
errorCode: "TOO_MANY_REQUESTS"
errorName: "TOO_MANY_REQUESTS"
httpStatus: 0
category: "unknown"
severity: "medium"
priority: 2
lastUpdated: '2026-06-25'
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "zoho api TOO_MANY_REQUESTS error"
  - "zoho TOO_MANY_REQUESTS fix"
  - "zoho api daily credit limit exceeded"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Too many total API calls to Zoho. You've used up your daily credit allowance for your Zoho plan.

**The fix:**
1. Wait for credits to replenish (they reset on a rolling 24-hour basis, not at midnight)
2. Use UPSERT instead of separate INSERT + UPDATE to cut your API calls in half
3. Check your plan's daily limit — Free: 500/day, Standard: 5,000/day, Professional: 10,000/day

**Copy-paste this code** (if you're using a code editor):
```python
import requests

resp = requests.get(f"{base_url}/settings/org", headers=headers)
limit_info = resp.json()
print(f"Daily credit limit: {limit_info.get('api_limit')}")
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Try this prompt in ChatGPT, Claude, Cursor, or Gemini:

> I'm getting a "TOO_MANY_REQUESTS" error from the Zoho CRM API.
> The error message is: "Daily credit limit exceeded"
> I'm running a Zoho integration that makes many API calls throughout the day.
> Please give me a step-by-step fix with working Python code that monitors remaining credits, uses UPSERT to reduce calls, and implements retry logic for when credits run low.

The AI should outline code that checks remaining credits before each call, switches to UPSERT to halve credit usage, and pauses when credits are low.

Need more? Follow up with:
> The fix didn't work. I'm still running out of daily credits. Here's my Zoho edition and how many calls I make per day: [details]. Please help me optimize or decide if I need to upgrade.

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to handle Zoho rate limit errors in popular automation tools:

### Zapier
1. Open your Zap → click the Zoho CRM action step
2. Enable "Auto-retry on error" — Zapier will retry when credits become available
3. Reduce Zap frequency — change polling triggers from every 5 minutes to every 15-30 minutes to use fewer credits

### Make (Integromat)
1. Open your scenario → click the Zoho CRM module
2. Switch from "Create a Record" + "Update a Record" to a single "Upsert a Record" module to cut API calls in half
3. Increase the scenario scheduling interval (e.g., from every 5 minutes to every 30 minutes) to reduce daily call volume

### n8n
1. Open your workflow → click the Zoho CRM node
2. In "Settings" → enable "Retry on Fail" → set "Wait Between Tries" to 3600000ms (1 hour), "Max Tries" to 2
3. Add a "Function" node before Zoho to batch multiple records into a single API call

### Power Automate
1. Open your flow → click the Zoho action
2. In "Settings" → enable "Retry Policy" → set to "Exponential interval" with count 3 and max interval 1 hour
3. Reduce trigger frequency — change recurrence triggers from every 5 minutes to every 30 minutes

**Which tool should you use?** Make is best for reducing credit usage — its UPSERT module and flexible scheduling help you stay within limits.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"TOO_MANY_REQUESTS"` in the API response
- `"rate limit"` exceeded in your integration logs
- `"Daily credit limit exceeded"` from Zoho
- Your integration works in the morning but stops working later in the day

**What it means in plain English:** You've used up all your Zoho API credits for today. Each Zoho plan has a daily limit. Once you hit it, you have to wait for credits to come back (on a rolling 24-hour basis).

**Most common cause:** Integrations that poll Zoho too frequently, bulk syncs that process thousands of records, or multiple tools sharing the same Zoho account's credit pool.

</div>

## What Causes Zoho TOO_MANY_REQUESTS

Zoho enforces a daily credit-based API quota per org. Each API call consumes credits based on the operation type (GET, POST, PUT, DELETE, and UPSERT have different costs). When your org exhausts its daily credit allocation, Zoho returns `TOO_MANY_REQUESTS` for all subsequent calls until the rolling 24-hour window resets.

The error appears in the response body as `{"code":"TOO_MANY_REQUESTS","message":"Daily credit limit exceeded"}` with HTTP status 200 (Zoho uses 200 for most errors — always check the `code` field). Credits reset on a rolling 24-hour basis, not at midnight.

### Common Scenarios
- Bulk sync jobs that process thousands of records without checking remaining credits
- Polling loops that call GET endpoints every few seconds
- Multiple integrations sharing the same Zoho org API credits
- Heavy operations like file uploads or report exports that consume more credits per call

## How to Detect If You're Affected

1. Check remaining credits via the API:
   ```bash
   curl -s "https://www.zohoapis.com/crm/v3/settings/org" \
     -H "Authorization: Zoho-oauthtoken $TOKEN" | jq .
   ```
   Look for the `api_limit` field in the response.

2. Parse the error response from any failing call:
   ```bash
   curl -s -X POST "https://www.zohoapis.com/crm/v3/Leads" \
     -H "Authorization: Zoho-oauthtoken $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"data":[{"Last_Name":"Test"}]}' | jq '.code'
   ```
   If the output is `"TOO_MANY_REQUESTS"`, you've hit the daily limit.

3. Monitor the `X-RATELIMIT-REMAINING` response header on each API call — it shows remaining credits for the current window.

## Step-by-Step Fix

### 1. Check Remaining Credits
Run this script to check your daily credit usage:
```python
import requests

url = "https://www.zohoapis.com/crm/v3/settings/org"
headers = {"Authorization": f"Zoho-oauthtoken {TOKEN}"}
resp = requests.get(url, headers=headers)
data = resp.json()
print(f"API Limit: {data.get('api_limit')}")
```

### 2. Optimize Operations — Use UPSERT
Replace separate INSERT + UPDATE with a single UPSERT call, which consumes fewer total credits:
```python
# BAD: INSERT then UPDATE (2 credits)
requests.post("https://www.zohoapis.com/crm/v3/Leads", ...)
requests.put("https://www.zohoapis.com/crm/v3/Leads/{id}", ...)

# GOOD: Single UPSERT (1 credit)
payload = {
    "data": [{"Last_Name": "Smith", "Email": "smith@example.com"}],
    "duplicate_check_fields": ["Email"]
}
requests.post("https://www.zohoapis.com/crm/v3/Leads/upsert", ...)
```

### 3. Wait for Rolling 24h Reset
If you've exhausted the daily quota, the only option is to wait. Credits replenish on a rolling 24-hour basis — not at midnight. Use the `X-RATELIMIT-RESET` header to know exactly when more credits become available.

## Prevention

- Monitor `X-RATELIMIT-REMAINING` on every response and pause processing when credits fall below 10%
- Use UPSERT endpoints instead of separate INSERT/UPDATE to halve credit consumption
- Cache reference data (picklists, users, products) locally instead of fetching repeatedly
- Batch bulk operations with Zoho's `/bulk` endpoints — they consume fewer credits per record
- Configure alerts in your integration to fire when remaining credits drop below 20%

## Official Documentation

- [Zoho CRM API Rate Limits](https://www.zoho.com/crm/developer/docs/api/v3/rate-limits.html)
- [Zoho CRM API Credit Usage](https://www.zoho.com/crm/developer/docs/api/v3/api-limits.html)
- [Zoho CRM API Overview](https://www.zoho.com/crm/developer/docs/api/v3/)

## People Also Ask

- **What is Zoho's daily API credit limit?** Limits vary by CRM edition: Free (500/day), Standard (5,000/day), Professional (10,000/day), Enterprise (50,000/day). Check your org settings for the exact number.
- **How do I check remaining Zoho API credits?** Call `GET /crm/v3/settings/org` and inspect the `api_limit` field. Alternatively, read the `X-RATELIMIT-REMAINING` response header on any API call.
- **Does Zoho TOO_MANY_REQUESTS reset at midnight?** No — it resets on a rolling 24-hour window. Each credit is tied to the time it was consumed, so credits become available again exactly 24 hours after they were used.
- **Can I increase my Zoho API credit limit?** Yes — upgrading to a higher CRM edition increases your daily credit allocation. Enterprise customers can request additional credits through Zoho support.

## Related Errors

- [Zoho TOO_MANY_CONCURRENT_REQUESTS](/zoho/errors/TOO_MANY_CONCURRENT_REQUESTS) — Exceeded parallel request limit for org
- [Zoho LIMIT_EXCEEDED](/zoho/errors/LIMIT_EXCEEDED) — General API limit reached (daily or rate)
- [Zoho INVALID_OAUTHTOKEN](/zoho/errors/INVALID_OAUTHTOKEN) — Access token expired or invalid

See all [Zoho API errors](/zoho/) in our complete reference. Similar rate limit issues occur with [HubSpot 429](/hubspot/errors/429), [Salesforce 429](/salesforce/errors/429), and [Slack rate_limited](/slack/errors/rate_limited). This error also affects integrations — see our [Zoho to Mailchimp integration errors](/integrations/zoho-to-mailchimp/) for common cross-tool issues.
