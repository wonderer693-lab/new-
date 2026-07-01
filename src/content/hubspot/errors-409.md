---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "HubSpot API 409: Duplicate detected or conflicting state (e"
description: "Fix HubSpot API 409 (409 Conflict) error. Duplicate detected or conflicting state (e. Use upsert or batch operations with the appropriate ID; check for existing records first."
tool: "hubspot"
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
  - "hubspot api 409 error"
  - "hubspot 409 fix"
  - "hubspot api duplicate detected or conflicting"
  - "hubspot http 409"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** You're trying to create a HubSpot record that already exists.

**The fix:**
1. Use "upsert" (create or update) instead of "create" — this updates existing records instead of failing
2. Search for the record first by email before trying to create it
3. If it exists, update it instead of creating a new one

**Copy-paste this code** (if you're using a code editor):
```python
import requests

payload = {"inputs": [{"properties": {"email": "test@example.com", "lastname": "Test"}}], "idProperty": "email"}
resp = requests.post("https://api.hubapi.com/crm/v3/objects/contacts/batch/upsert",
    headers=headers, json=payload)
print("Created or updated successfully" if resp.status_code in (200, 207) else "Failed")
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy and send this to your AI tool:

> I'm getting a 409 Conflict error from the HubSpot API when creating contacts.
> The error says "Contact already exists" and "duplicate email."
> I'm using POST /crm/v3/objects/contacts to create new contacts.
> Please give me code that uses upsert instead of create, so it updates existing contacts instead of failing.

You should get code using the batch upsert endpoint with `idProperty: "email"` that creates new records and updates existing ones without errors.

If the error persists, try this follow-up:
> The fix didn't work. I'm still getting 409 errors in batch operations. Here's my payload: [paste it]. Please debug this.

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to handle HubSpot 409 duplicate errors in popular automation tools:

### Zapier
1. Open your Zap → replace the "Create Contact" HubSpot action with "Find or Create Contact"
2. The "Find or Create" action searches by email first — if the contact exists, it updates; if not, it creates
3. Map your fields the same way as before — Zapier handles the deduplication automatically

### Make (Integromat)
1. Open your scenario → replace the "Create a Contact" module with "Search for a Contact"
2. Add a "Router" after the search — Path 1: if found, use "Update a Contact"; Path 2: if not found, use "Create a Contact"
3. Alternatively, use the "Upsert" module if available in your HubSpot connection — it handles find-or-create in one step

### n8n
1. Open your workflow → add a HubSpot "Search" node before the "Create" node
2. Search by email — if a result exists, route to an "Update" node; if not, route to the "Create" node
3. Use an "IF" node to branch: condition = `{{$json.results.length}} > 0`

### Power Automate
1. Open your flow → add a "Search records" HubSpot action before the "Create record" action
2. Add a "Condition" action — if search returns results, use "Update record" instead of "Create record"
3. In the "Update" branch, map the same fields and use the record ID from the search result

**Which tool should you use?** Zapier's "Find or Create" action is the simplest — it handles deduplication in a single step with no extra logic needed.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"409 Conflict"`
- `"Contact already exists"`
- `"duplicate email"`
- `"CONFLICT"` in your integration logs

**What it means in plain English:** You're trying to add a record that's already in HubSpot. The email address (or other unique field) is already used by another contact.

**Most common cause:** Running an import script twice without checking for existing records, or two different tools trying to create the same contact at the same time.

</div>

## What Causes HubSpot 409

HubSpot returns HTTP 409 when attempting to create a record that duplicates an existing record on a unique property (most commonly `email` for Contacts). HubSpot enforces uniqueness on `email` for Contacts, `dealname` for Deals (within the same pipeline), and custom unique properties you've configured.

The response includes `{"status":"error","message":"...","category":"CONFLICT"}`. For Contacts, the message typically says "Contact already exists with this email address." This is HubSpot's safeguard against data duplication — it refuses to create a second record with the same unique identifier. See all [HubSpot API errors](/hubspot/) in our complete reference.

This error also affects integrations. See our [HubSpot to Slack integration errors](/integrations/hubspot-to-slack/) for common cross-tool issues.

### Common Scenarios
- Creating a Contact with an email that already exists in HubSpot
- Creating a Deal with a name that matches an existing deal in the same pipeline
- Upserting a record with an ID that conflicts with an existing association
- Batch import where some records are duplicates of existing data
- Re-running an import script without deduplicating against existing records first

## How to Detect If You're Affected

1. Check the error category:
   ```bash
   curl -s -X POST "https://api.hubapi.com/crm/v3/objects/contacts" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"properties":{"email":"existing@example.com","lastname":"Test"}}' | jq '.category'
   ```
   If `"CONFLICT"`, duplicate detected.

2. Check for existing record before creating:
   ```bash
   curl -s -X POST "https://api.hubapi.com/crm/v3/objects/contacts/search" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"filterGroups":[{"filters":[{"propertyName":"email","operator":"EQ","value":"existing@example.com"}]}]}' | jq '.total'
   ```

## Step-by-Step Fix

### 1. Use Upsert Instead of Create
```python
# BAD — POST /contacts fails if email exists
payload = {"properties": {"email": "existing@example.com", "lastname": "Test"}}
resp = requests.post("https://api.hubapi.com/crm/v3/objects/contacts", headers=headers, json=payload)
print(resp.json().get("category"))  # CONFLICT

# GOOD — use batch upsert with idProperty
payload = {
    "inputs": [{"properties": {"email": "existing@example.com", "lastname": "Test"}}],
    "idProperty": "email"
}
resp = requests.post(
    "https://api.hubapi.com/crm/v3/objects/contacts/batch/upsert",
    headers=headers, json=payload
)
# This creates if new, updates if existing
```

### 2. Search Before Create
```python
def contact_exists_by_email(email):
    payload = {
        "filterGroups": [{"filters": [{"propertyName": "email", "operator": "EQ", "value": email}]}]
    }
    resp = requests.post("https://api.hubapi.com/crm/v3/objects/contacts/search",
        headers=headers, json=payload)
    return resp.json().get("total", 0) > 0

# Check first
if not contact_exists_by_email("test@example.com"):
    requests.post("https://api.hubapi.com/crm/v3/objects/contacts", headers=headers, json=payload)
else:
    print("Contact exists — skipping or updating")
```

### 3. Handle 409 in Batch Operations
When processing many records, catch duplicates and log them:
```python
for record in records:
    resp = requests.post("https://api.hubapi.com/crm/v3/objects/contacts", headers=headers, json=record)
    if resp.status_code == 409:
        conflict_log.append({"record": record, "status": "duplicate_skipped"})
```

## Prevention

- Always use batch upsert with `idProperty: "email"` instead of POST for Contact operations
- Search for existing records before creating if you need deterministic behavior
- Configure custom unique properties in HubSpot to prevent duplicates on your business keys
- Implement pre-import deduplication against your source data
- Log 409 responses with the conflicting value for data quality monitoring

## Official Documentation

- [HubSpot Batch Upsert](https://developers.hubspot.com/docs/api/crm/batch#upsert)
- [HubSpot Search API](https://developers.hubspot.com/docs/api/crm/search)
- [HubSpot CRM API Overview](https://developers.hubspot.com/docs/api/crm/overview)

## People Also Ask

- **What causes HubSpot 409?** Attempting to create a record that duplicates an existing record on a unique property — typically creating a Contact with an email that already exists.
- **How do I fix HubSpot 409 on Contact creation?** Use batch upsert with `idProperty: "email"` instead of POST create. Upsert creates if new, updates if existing — no conflict.
- **Does HubSpot 409 apply to all object types?** It applies to any object with unique property constraints. Contacts (email), Deals (dealname within pipeline), and custom unique fields.
- **Can I disable HubSpot's duplicate detection?** No — duplicate detection is hard-coded for system unique properties. Use upsert or search-then-create to work around it.

## Related Errors

- [HubSpot 400 Bad Request](/hubspot/errors/400) — Validation error
- [HubSpot 404 Not Found](/hubspot/errors/404) — Resource does not exist
- [HubSpot 207 Multi-Status](/hubspot/errors/207-multi-status) — Partial batch success
