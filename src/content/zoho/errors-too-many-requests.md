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
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "zoho api TOO_MANY_REQUESTS error"
  - "zoho TOO_MANY_REQUESTS fix"
  - "zoho api daily credit limit exceeded"
---

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
