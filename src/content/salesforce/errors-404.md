---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Salesforce API 404: Resource does not exist"
description: "Fix Salesforce API 404 (404 Not Found) error. Resource does not exist. Verify record ID, API version, and endpoint path."
tool: "salesforce"
errorCode: "404"
errorName: "404 Not Found"
httpStatus: 404
category: "not-found"
severity: "medium"
priority: 2
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "salesforce api 404 error"
  - "salesforce 404 fix"
  - "salesforce api resource does not exist"
  - "salesforce http 404"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** The Salesforce record doesn't exist — wrong ID, deleted record, or typo in the URL.

**The fix:**
1. Double-check the record ID — Salesforce IDs are 15 or 18 characters (use 18-character IDs)
2. Search for the record in Salesforce to confirm it hasn't been deleted
3. Make sure you're using the right API endpoint path (e.g., `sobjects` not `sobject`)

**Copy-paste this code** (if you're using a code editor):
```python
import requests

record_id = "0035x000007ABCdEAO"
resp = requests.get(f"{instance_url}/services/data/v60.0/sobjects/Contact/{record_id}", headers=headers)
if resp.status_code == 404:
    print("Record not found — it may have been deleted or the ID is wrong")
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy and send this to your AI tool:

> I'm getting a 404 Not Found error from the Salesforce API.
> The error message is: "NOT_FOUND" — "The requested resource does not exist"
> I'm trying to read a Contact record by its ID.
> Please give me a step-by-step fix with working Python code that checks if a record exists before accessing it.

You should get a lookup function that queries for the record first using SOQL, validates the ID format, and handles the case where the record was deleted.

If the error persists, try this follow-up:
> The fix didn't work. The record definitely exists in Salesforce but I still get 404. Here's the ID I'm using: [paste ID]. Please debug this.

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to handle Salesforce "not found" errors in popular automation tools:

### Zapier
1. Open your Zap → add a "Find Record" step before your main Salesforce action
2. In the Find step, search by email or name instead of ID — this confirms the record exists
3. Add a "Filter" step after Find: only continue if the Find step returned a result

### Make (Integromat)
1. Open your scenario → add a "Search Records" module before your main Salesforce action
2. Search by a unique field (email, name) to find the record's ID first
3. Add a "Router" after Search: one path for "record found" → proceed, another for "not found" → skip or log

### n8n
1. Open your workflow → add a "Salesforce" node set to "Search" before your main action
2. Use SOQL query: `SELECT Id FROM Contact WHERE Email = 'test@example.com'`
3. Add an "IF" node: if search returns results → proceed, if empty → handle gracefully

### Power Automate
1. Open your flow → add a "List records" action before your main Salesforce action
2. Set a filter query to search by a known field (e.g., email)
3. Add a "Condition" action: if records found → use the ID from results, if not → skip or send alert

**Which tool should you use?** Zapier has the simplest "Find Record" step — it searches and returns the ID in one click, so you never hit a 404.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"404 Not Found"`
- `"NOT_FOUND"`
- `"The requested resource does not exist"`
- `"Could not find resource"` in your integration logs

**What it means in plain English:** Salesforce can't find the record you're looking for. The ID is wrong, the record was deleted, or you're looking in the wrong place.

**Most common cause:** Using a 15-character Salesforce ID instead of the 18-character version, or referencing a record that was deleted and emptied from the Recycle Bin.

</div>

## What Causes Salesforce 404

Salesforce returns HTTP 404 when the requested resource does not exist at the specified URL. See all [Salesforce API errors](/salesforce/) in our complete reference. This can be caused by an invalid record ID, a wrong API version, a mistyped endpoint path, or referencing a record that has been deleted or whose ID format is incorrect.

Salesforce uses 18-character record IDs (the 15-character ID + 3-character suffix) for all records. A 404 with `NOT_FOUND` error code means the ID doesn't map to any record in the system. API versions follow the pattern `/services/data/v{version}/` — using a version number that doesn't exist also returns 404.

### Common Scenarios
- Using a 15-character ID when Salesforce expects 18 characters (the 3-character suffix is missing)
- Referencing a record that was hard-deleted (emptied from Recycle Bin)
- Making a request to a non-existent API version (e.g., `v99.0`)
- Typo in the endpoint path (e.g., `sobject` instead of `sobjects`)
- Referencing a record from a different Salesforce org or sandbox

## How to Detect If You're Affected

1. Test the record ID with a direct query:
   ```bash
   curl -s -w "\n%{http_code}" "https://yourdomain.my.salesforce.com/services/data/v60.0/sobjects/Contact/003XXXXXXXXXXXXXXX" \
     -H "Authorization: Bearer $TOKEN" | tail -1
   ```

2. Verify the record exists with a SOQL query:
   ```bash
   curl -s "https://yourdomain.my.salesforce.com/services/data/v60.0/query?q=SELECT+Id+FROM+Contact+WHERE+Id='003XXXXXXXXXXXXXXX'" \
     -H "Authorization: Bearer $TOKEN" | jq '.totalSize'
   ```

3. Check API version availability:
   ```bash
   curl -s "https://yourdomain.my.salesforce.com/services/data/" \
     -H "Authorization: Bearer $TOKEN" | jq '.'
   ```

## Step-by-Step Fix

### 1. Validate Record ID
```python
import re

# Salesforce IDs are 15 or 18 characters, alphanumeric
def is_valid_sf_id(value):
    return bool(re.match(r'^[a-zA-Z0-9]{15,18}$', value))

# BAD — invalid ID format
record_id = "123"  # Too short
resp = requests.get(f"{instance_url}/services/data/v60.0/sobjects/Contact/{record_id}", headers=headers)
print(resp.status_code)  # 404

# GOOD — valid format
record_id = "0035x000007ABCdEAO"  # 18 chars
if is_valid_sf_id(record_id):
    resp = requests.get(f"{instance_url}/services/data/v60.0/sobjects/Contact/{record_id}", headers=headers)
```

### 2. Query to Confirm Existence
```python
def record_exists(sobject, record_id):
    query_url = f"{instance_url}/services/data/v60.0/query"
    params = {"q": f"SELECT Id FROM {sobject} WHERE Id='{record_id}'"}
    resp = requests.get(query_url, headers=headers, params=params)
    return resp.json().get("totalSize", 0) > 0

# Check before accessing
if record_exists("Contact", "0035x000007ABCdEAO"):
    resp = requests.get(f"{instance_url}/services/data/v60.0/sobjects/Contact/0035x000007ABCdEAO", headers=headers)
else:
    print("Record not found — may have been deleted")
```

### 3. Verify API Version and Endpoint
```python
# Get available API versions
versions_resp = requests.get(f"{instance_url}/services/data/", headers=headers)
available_versions = [v["version"] for v in versions_resp.json()]
print(f"Available versions: {available_versions}")

# BAD — non-existent version
url = f"{instance_url}/services/data/v99.0/sobjects/Contact"  # 404

# GOOD — use a valid version (latest is recommended)
latest_version = available_versions[-1]
url = f"{instance_url}/services/data/v{latest_version}/sobjects/Contact"
```

## Prevention

- Always use 18-character record IDs (convert 15-char to 18-char if needed)
- Query for a record before attempting to read or update it
- Use the latest stable API version, avoid deprecated versions
- Never hardcode record IDs — fetch them dynamically from SOQL queries
- Handle 404 by re-querying for fresh IDs rather than retrying the same request
- Similar not-found issues occur with [HubSpot 404](/hubspot/errors/404), [Mailchimp 404](/mailchimp/errors/404), and [Pipedrive 404](/pipedrive/errors/404).
- This error also affects integrations. See our [Salesforce to Mailchimp](/integrations/salesforce-to-mailchimp/) and [Salesforce to ActiveCampaign](/integrations/salesforce-to-activecampaign/) integration error guides.

## Official Documentation

- [Salesforce REST API](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/)
- [Salesforce SOQL](https://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta/soql_sosl/)
- [Salesforce Record IDs](https://help.salesforce.com/s/articleView?id=sf.faq_general_develop.htm)

## People Also Ask

- **What's the difference between 15 and 18 character Salesforce IDs?** The 18-character ID is the 15-character ID with a 3-character suffix that encodes case. Use 18-character IDs for API calls to avoid case-sensitivity issues.
- **Can I get 404 for a record in the Recycle Bin?** Yes — if the record is in the Recycle Bin, it still exists but returns 404 from the standard API. Use `ALL ROWS` in SOQL to query deleted records.
- **How do I find the latest Salesforce API version?** Call `GET /services/data/` to list all available versions. The highest version number is the latest.
- **Does Salesforce 404 apply to deleted records?** Hard-deleted records (emptied from Recycle Bin) return 404. Soft-deleted records (in Recycle Bin) also return 404 from the standard REST API.

## Related Errors

- [Salesforce 400 Bad Request](/salesforce/errors/400) — Invalid payload or field values
- [Salesforce 401 Unauthorized](/salesforce/errors/401) — Session expired or invalid
- [Salesforce 403 Forbidden](/salesforce/errors/403) — Request refused
