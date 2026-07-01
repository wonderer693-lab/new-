---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "HubSpot API 404: Requested resource does not exist"
description: "Fix HubSpot API 404 (404 Not Found) error. Requested resource does not exist. Verify the object ID is correct and the object hasn't been deleted."
tool: "hubspot"
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
  - "hubspot api 404 error"
  - "hubspot 404 fix"
  - "hubspot api requested resource does not"
  - "hubspot http 404"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** The HubSpot record you're looking for doesn't exist (deleted or wrong ID).

**The fix:**
1. Double-check the record ID — make sure it's correct and not a typo
2. Make sure you're using the right object type (use `contacts`, not `contact`)
3. Search for the record by email or name instead of using the ID directly

**Copy-paste this code** (if you're using a code editor):
```python
import requests

resp = requests.get(f"https://api.hubapi.com/crm/v3/objects/contacts/{record_id}", headers=headers)
if resp.status_code == 404:
    print(f"Record {record_id} not found — searching by email instead")
    search = requests.post("https://api.hubapi.com/crm/v3/objects/contacts/search",
        headers=headers, json={"filterGroups": [{"filters": [{"propertyName": "email", "operator": "EQ", "value": email}]}]})
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Start with this prompt in ChatGPT, Claude, or any AI coding assistant:

> I'm getting a 404 Not Found error from the HubSpot API.
> The error says "Object not found" and "record does not exist."
> I'm trying to look up a contact by ID but it keeps failing.
> Please give me code that searches for the contact by email instead, and handles the case where the record was deleted.

A good response will give you a search-based lookup function that finds records by email or other properties instead of relying on a specific ID.

Follow up with additional context if needed:
> The fix didn't work. The record might be in a different HubSpot account or object type. How do I check multiple object types?

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to handle HubSpot 404 errors in popular automation tools:

### Zapier
1. Open your Zap → click the HubSpot action step
2. Before the HubSpot action, add a "Find Contact" step that searches by email instead of ID
3. Add a "Filter by Zapier" step after the search — only continue if a contact was found (this prevents 404 errors)

### Make (Integromat)
1. Open your scenario → add a "Search Contacts" module before your main HubSpot module
2. Set the search filter to look up by email or name
3. Add a "Router" after the search — one path for "found" (continue to main module) and one for "not found" (skip or log)

### n8n
1. Open your workflow → add a HubSpot "Search" node before your main action node
2. Configure the search to find records by email or other unique property
3. Add an "IF" node after the search — route to the main action only if results exist, otherwise route to a logging node

### Power Automate
1. Open your flow → add a "Search records" HubSpot action before your main action
2. Set the search criteria to email or name
3. Add a "Condition" action — if search results are empty, skip the main action and log the missing record instead

**Which tool should you use?** Zapier has the simplest "find or skip" pattern — the Filter step makes it easy to avoid 404 errors.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"404 Not Found"`
- `"Object not found"`
- `"record does not exist"`
- `"Resource not found"` in your integration logs

**What it means in plain English:** HubSpot can't find the record you asked for. It was either deleted, never created, or you're looking in the wrong place (wrong ID or wrong object type).

**Most common cause:** Using a record ID that was deleted from HubSpot, or using `contact` (singular) instead of `contacts` (plural) in the URL.

</div>

## What Causes HubSpot 404

HubSpot returns HTTP 404 when the requested resource does not exist — a contact, deal, or company with that ID was never created, has been deleted, or the object type is misspelled. HubSpot's REST API is strict about object types and IDs.

The response includes `{"status":"error","message":"Resource not found","category":"OBJECT_NOT_FOUND"}`. The `category` field is usually `OBJECT_NOT_FOUND` for missing records, but can also be related to incorrect object type names (e.g., `contact` instead of `contacts`). See all [HubSpot API errors](/hubspot/) in our complete reference.

This error also affects integrations. See our [HubSpot to Slack integration errors](/integrations/hubspot-to-slack/) for common cross-tool issues.

### Common Scenarios
- Referencing a record ID that was deleted or never existed
- Typo in the object type — `/crm/v3/objects/contact` (singular) instead of `/crm/v3/objects/contacts`
- Record moved to a different pipeline or stage that uses a different object type
- Using an association label that doesn't exist
- Record created in a different HubSpot account than the one the token has access to

## How to Detect If You're Affected

1. Check the response status and category:
   ```bash
   curl -s -w "\n%{http_code}" "https://api.hubapi.com/crm/v3/objects/contacts/99999999999" \
     -H "Authorization: Bearer $TOKEN" | tail -1
   ```

2. Verify the record exists by searching:
   ```bash
   curl -s -X POST "https://api.hubapi.com/crm/v3/objects/contacts/search" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"filterGroups":[{"filters":[{"propertyName":"hs_object_id","operator":"EQ","value":"12345"}]}]}' | jq '.results'
   ```

## Step-by-Step Fix

### 1. Verify Object Type Name
```python
# BAD — singular object type
resp = requests.get("https://api.hubapi.com/crm/v3/objects/contact/123", headers=headers)

# GOOD — plural object type
VALID_OBJECTS = ["contacts", "deals", "companies", "products", "tickets"]
for obj in VALID_OBJECTS:
    resp = requests.get(f"https://api.hubapi.com/crm/v3/objects/{obj}/123", headers=headers)
    if resp.status_code == 200:
        print(f"Found in {obj}")
        break
```

### 2. Search Before Access
```python
def find_record(object_type, record_id):
    resp = requests.get(
        f"https://api.hubapi.com/crm/v3/objects/{object_type}/{record_id}",
        headers=headers
    )
    if resp.status_code == 404:
        # Try search as fallback
        search_resp = requests.post(
            f"https://api.hubapi.com/crm/v3/objects/{object_type}/search",
            headers=headers,
            json={
                "filterGroups": [{
                    "filters": [{"propertyName": "hs_object_id", "operator": "EQ", "value": str(record_id)}]
                }]
            }
        )
        total = search_resp.json().get("total", 0)
        if total == 0:
            print(f"Record {record_id} does not exist in {object_type}")
            return None
    return resp.json()
```

### 3. Handle Deleted Records
```python
# If a record returns 404, remove it from your local reference table
if resp.status_code == 404:
    delete_from_cache(record_id)
    print(f"Record {record_id} removed from cache — not found in HubSpot")
```

## Prevention

- Use the correct plural object type in URLs (`contacts` not `contact`, `deals` not `deal`)
- Validate record IDs exist before making related operations (associations, notes)
- Cache record IDs and periodically verify they still exist in HubSpot
- Implement a 404 handler that cleans up stale references from your local database
- Use HubSpot's search API for lookups instead of direct ID access when possible
- Similar not-found issues occur with [Salesforce 404](/salesforce/errors/404), [Mailchimp 404](/mailchimp/errors/404), and [ActiveCampaign 404](/activecampaign/errors/404).

## Official Documentation

- [HubSpot CRM API Overview](https://developers.hubspot.com/docs/api/crm/overview)
- [HubSpot Search API](https://developers.hubspot.com/docs/api/crm/search)
- [HubSpot API Errors](https://developers.hubspot.com/docs/api/errors)

## People Also Ask

- **What causes HubSpot 404?** The record ID doesn't exist, the object type is misspelled, or the record was deleted. Check both the ID and the URL path.
- **How do I fix HubSpot 404?** Verify the object type is correct (always plural: `contacts`, `deals`), and check the record ID via search endpoint.
- **Does HubSpot 404 mean the record was deleted?** Possibly — records can be deleted from the HubSpot UI or API. Use the search endpoint to confirm if the record exists.
- **Can HubSpot 404 be caused by permissions?** No — permission issues return 403. A 404 always means the resource genuinely doesn't exist at that URL.

## Related Errors

- [HubSpot 400 Bad Request](/hubspot/errors/400) — Validation error
- [HubSpot 403 Forbidden](/hubspot/errors/403) — Token lacks OAuth scopes
- [HubSpot 409 Conflict](/hubspot/errors/409) — Duplicate detected
