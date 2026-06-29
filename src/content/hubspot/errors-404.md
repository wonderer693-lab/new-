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

## What Causes HubSpot 404

HubSpot returns HTTP 404 when the requested resource does not exist — a contact, deal, or company with that ID was never created, has been deleted, or the object type is misspelled. HubSpot's REST API is strict about object types and IDs.

The response includes `{"status":"error","message":"Resource not found","category":"OBJECT_NOT_FOUND"}`. The `category` field is usually `OBJECT_NOT_FOUND` for missing records, but can also be related to incorrect object type names (e.g., `contact` instead of `contacts`).

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
