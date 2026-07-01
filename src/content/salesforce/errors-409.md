---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Salesforce API 409: Conflict with current resource state (e"
description: "Fix Salesforce API 409 (409 Conflict) error. Conflict with current resource state (e. Check API version compatibility with the resource being accessed."
tool: "salesforce"
errorCode: "409"
errorName: "409 Conflict"
httpStatus: 409
category: "conflict"
severity: "medium"
priority: 2
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "salesforce api 409 error"
  - "salesforce 409 fix"
  - "salesforce api conflict with current resource"
  - "salesforce http 409"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** You're trying to create a record that conflicts with an existing one — Salesforce's duplicate rules caught it.

**The fix:**
1. Search for the existing record before creating a new one (use SOQL to check for duplicates)
2. If you want to update instead of create, use the existing record's ID with a PATCH request
3. To bypass duplicate rules, add the header `Sforce-Duplicate-Rule-Header: allowSave=true`

**Copy-paste this code** (if you're using a code editor):
```python
import requests

query = "SELECT Id FROM Account WHERE Name='Acme Corp'"
resp = requests.get(f"{instance_url}/services/data/v60.0/query", headers=headers, params={"q": query})
if resp.json()["totalSize"] > 0:
    record_id = resp.json()["records"][0]["Id"]
    print(f"Record exists: {record_id} — use PATCH to update instead")
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm getting a 409 Conflict error from the Salesforce API.
> The error message is: "DUPLICATE_VALUE" — a record with this value already exists.
> I'm trying to create new Account records but duplicate rules are blocking me.
> Please give me a step-by-step fix with working Python code that checks for duplicates before creating records.

**What to expect:** The AI should give you a "find or create" pattern — search for existing records first, update if found, create if not.

**If it doesn't work**, add this follow-up:
> The fix didn't work. I'm still getting 409 errors. Here's my code: [paste your code]. The duplicate rule seems to match on fuzzy logic. Please debug this.

**Best AI tools for this:** Claude (best at explaining duplicate rule logic), ChatGPT-4 (good code generation), Cursor (if you want inline code fixes)

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to handle Salesforce duplicate conflicts in popular automation tools:

### Zapier
1. Open your Zap → add a "Find Record" step before your "Create Record" step
2. Search by the unique field (e.g., email for Contacts, name for Accounts)
3. Add a "Paths" step: Path A (found) → "Update Record", Path B (not found) → "Create Record"

### Make (Integromat)
1. Open your scenario → add a "Search Records" module before your "Create Record" module
2. Search by the field that's causing the duplicate conflict
3. Add a "Router": if found → "Update Record" module, if not found → "Create Record" module

### n8n
1. Open your workflow → add a Salesforce "Search" node before your "Create" node
2. Query: `SELECT Id FROM Account WHERE Name = '{{$json.name}}'`
3. Add an "IF" node: if results exist → route to "Update" node, if empty → route to "Create" node

### Power Automate
1. Open your flow → add a "List records" action before "Create record"
2. Set filter query to check for existing records by the unique field
3. Add a "Condition": if records found → "Update record" action, if not → "Create record" action

**Which tool should you use?** Zapier Paths make "find or create" logic the easiest — it handles both cases in one step without extra modules.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"409 Conflict"`
- `"DUPLICATE_VALUE"`
- `"duplicate id"`
- `"API_VERSION_NOT_SUPPORTED"` in your integration logs

**What it means in plain English:** Salesforce already has a record that matches what you're trying to create. It's like trying to add a contact with an email that's already in the system.

**Most common cause:** Running the same integration twice, or two different integrations creating the same record at the same time.

</div>

## What Causes Salesforce 409

Salesforce returns HTTP 409 when the request conflicts with the current state of the resource. The most common cause is an API version incompatibility — attempting to use an API feature that isn't available in the specified version. It can also occur with duplicate detection rules, where creating a record would create a duplicate that violates an org's duplicate rule.

The response contains `[{"message":"API version x not supported for this resource","errorCode":"API_VERSION_NOT_SUPPORTED"}]`. This is distinct from 400 (invalid payload) — 409 means the request is valid but can't be applied due to the resource's current state.

### Common Scenarios
- Using an API version that doesn't support a specific feature (e.g., Platform Event publishing in older versions)
- Duplicate rule matching: creating an Account with a name that matches a duplicate rule
- Attempting to insert a record that triggers a fuzzy-matching duplicate rule
- Using a Beta API feature that was removed in a newer version

## How to Detect If You're Affected

1. Check the error code in the response:
   ```bash
   curl -s -X POST "https://yourdomain.my.salesforce.com/services/data/v60.0/sobjects/Account" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"Name":"Existing Account"}' | jq '.[0].errorCode'
   ```

2. Test with a different API version to isolate the issue:
   ```bash
   curl -s -w "\n%{http_code}" "https://yourdomain.my.salesforce.com/services/data/v58.0/sobjects/Account" \
     -H "Authorization: Bearer $TOKEN" | tail -1
   ```

3. Check if duplicate rules are enabled:
   ```bash
   curl -s "https://yourdomain.my.salesforce.com/services/data/v60.0/limits" \
     -H "Authorization: Bearer $TOKEN" | jq '.DuplicateRule'
   ```

## Step-by-Step Fix

### 1. Use a Compatible API Version
```python
# BAD — using too old a version for the feature
url = f"{instance_url}/services/data/v20.0/sobjects/Account"

# GOOD — use the latest stable version
url = f"{instance_url}/services/data/v60.0/sobjects/Account"
resp = requests.post(url, headers=headers, json=payload)
```

### 2. Handle Duplicate Rules
```python
# BAD — creates duplicate that triggers rule
payload = {"Name": "Acme Corporation"}
resp = requests.post(url, headers=headers, json=payload)
# 409 if duplicate rule matches

# GOOD — use DuplicateRuleHeader to bypass or allow
headers_with_rule = headers.copy()
headers_with_rule["Sforce-Duplicate-Rule-Header"] = "allowSave=true"

resp = requests.post(url, headers=headers_with_rule, json=payload)
if resp.status_code == 409:
    print("Duplicate detected — check duplicate rules in Setup")
    # Query for existing duplicate
    query_resp = requests.get(
        f"{instance_url}/services/data/v60.0/query",
        headers=headers,
        params={"q": f"SELECT Id, Name FROM Account WHERE Name='Acme Corporation'"},
    )
    existing = query_resp.json().get("records", [])
    print(f"Existing record: {existing[0]['Id'] if existing else 'none'}")
```

### 3. Check Feature Availability Per Version
```python
# Check available API versions
resp = requests.get(f"{instance_url}/services/data/", headers=headers)
versions = [v["version"] for v in resp.json()]
print(f"Available versions: {versions}")

# Use the latest for new features, check release notes for version-specific changes
latest = versions[-1]
print(f"Using latest version: v{latest}")
```

## Prevention

- Always use the latest stable Salesforce API version for new integrations
- Test API calls across multiple versions to ensure compatibility
- Review Salesforce API release notes for breaking changes each season
- Use the `Sforce-Duplicate-Rule-Header` header to control duplicate rule behavior
- Query for existing records before inserting to avoid duplicate rule triggers

## Official Documentation

- [Salesforce REST API](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/)
- [Salesforce API Versioning](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/versioning.htm)
- [Salesforce Duplicate Rules](https://help.salesforce.com/s/articleView?id=sf.duplicate_rules_overview.htm)

## People Also Ask

- **What causes Salesforce API_VERSION_NOT_SUPPORTED?** Using a Salesforce API version that doesn't support the requested resource or feature. Use the latest stable version.
- **How do I bypass Salesforce duplicate rules via API?** Add the `Sforce-Duplicate-Rule-Header: allowSave=true` HTTP header to allow creation even if duplicates are detected.
- **What Salesforce API version should I use?** Use the latest available version for new integrations. Check `GET /services/data/` for the latest version in your org.
- **Can 409 be caused by concurrent updates?** Not typically — Salesforce uses 409 for version incompatibility and duplicate rules, not for concurrent modification conflicts.

## Related Errors

- [Salesforce 400 Bad Request](/salesforce/errors/400) — Invalid payload or field values
- [Salesforce 403 Forbidden](/salesforce/errors/403) — Request refused
- [Salesforce 414 URI Too Long](/salesforce/errors/414) — URL exceeds 16,384 bytes
