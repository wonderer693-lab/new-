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

## What Causes HubSpot 409

HubSpot returns HTTP 409 when attempting to create a record that duplicates an existing record on a unique property (most commonly `email` for Contacts). HubSpot enforces uniqueness on `email` for Contacts, `dealname` for Deals (within the same pipeline), and custom unique properties you've configured.

The response includes `{"status":"error","message":"...","category":"CONFLICT"}`. For Contacts, the message typically says "Contact already exists with this email address." This is HubSpot's safeguard against data duplication — it refuses to create a second record with the same unique identifier.

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
