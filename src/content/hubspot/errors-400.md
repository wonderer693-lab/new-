---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "HubSpot API 400: Validation error, often due to invalid property values or..."
description: "Fix HubSpot API 400 (400 Bad Request) error. Validation error, often due to invalid property values or missing required fields. Verify all property names and values against the CRM object schema before sending."
tool: "hubspot"
errorCode: "400"
errorName: "400 Bad Request"
httpStatus: 400
category: "validation"
severity: "medium"
priority: 2
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "hubspot api 400 error"
  - "hubspot 400 fix"
  - "hubspot api validation error, often due"
  - "hubspot http 400"
---

## What Causes HubSpot 400

HubSpot returns HTTP 400 when the request body contains invalid JSON, unknown property names, incorrect property data types, or missing required fields. HubSpot's CRM validates every request against the object type's schema — for example, a Contact creation request must use valid Contact property names like `email`, `firstname`, `lastname`, and values must match the property's data type.

The response includes `{"status":"error","message":"...","category":"VALIDATION_ERROR"}` with details about which field failed validation. The `message` field often includes the specific property name and expected format.

### Common Scenarios
- Unknown property name — using `firstName` instead of `firstname` (HubSpot uses lowercase API names)
- Wrong data type — sending a string for a `number` property
- Missing required property — `lastname` is required for Contact creation
- Invalid email format — email doesn't pass HubSpot's validation
- Property value exceeds maximum length (e.g., `firstname` max 100 characters)

## How to Detect If You're Affected

1. Inspect the error message for the specific property:
   ```bash
   curl -s -X POST "https://api.hubapi.com/crm/v3/objects/contacts" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"properties":{"invalidProp":"value"}}' | jq '.message'
   ```

2. Fetch the object schema to check valid property names:
   ```bash
   curl -s "https://api.hubapi.com/crm/v3/properties/contacts" \
     -H "Authorization: Bearer $TOKEN" | jq '.results[].name' | head -20
   ```

## Step-by-Step Fix

### 1. Fetch Valid Property Names
```python
def get_valid_properties(object_type, headers):
    resp = requests.get(f"https://api.hubapi.com/crm/v3/properties/{object_type}", headers=headers)
    return {p["name"]: p["type"] for p in resp.json()["results"]}

# BAD — property name doesn't exist
payload = {"properties": {"FirstName": "John", "Email": "john@test.com"}}  # Should be "firstname"

# GOOD — use exact API names
valid = get_valid_properties("contacts", headers)
payload = {"properties": {"firstname": "John", "email": "john@test.com"}}
```

### 2. Validate Data Types
```python
# BAD — wrong type for number property
payload = {"properties": {"num_employees": "500"}}  # Should be integer

# GOOD — correct type
payload = {"properties": {"num_employees": 500}}
```

### 3. Include Required Fields
```python
# BAD — missing required fields
payload = {"properties": {"email": "test@test.com"}}  # 400 — lastname required

# GOOD — include all required
payload = {"properties": {"email": "test@test.com", "lastname": "Test"}}
```

## Prevention

- Fetch the object property schema at integration startup and validate payloads against it
- Map source field names to HubSpot's lowercase API names (e.g., `firstName` → `firstname`)
- Validate data types before sending — especially for custom properties with specific types
- Include `lastname` and `email` in every Contact payload (system-required fields)
- Test with a single record before sending batch operations

## Official Documentation

- [HubSpot CRM Object Properties](https://developers.hubspot.com/docs/api/crm/properties)
- [HubSpot CRM API Overview](https://developers.hubspot.com/docs/api/crm/overview)
- [HubSpot API Errors](https://developers.hubspot.com/docs/api/errors)

## People Also Ask

- **What causes HubSpot 400?** Invalid property names, wrong data types, missing required fields, or malformed JSON. HubSpot's validation is strict — every property must exist in the object's schema.
- **How do I find valid HubSpot property names?** Call `GET /crm/v3/properties/contacts` to get all valid property names and their types. Property names are lowercase with underscores.
- **Why does HubSpot 400 say "Property does not exist"?** You're using a property name that doesn't match the schema. Check the exact `name` field from the properties API — they're case-sensitive.
- **What properties are required for HubSpot Contacts?** `lastname` is system-required. While `email` is not technically required by the API, most integrations should include it for deduplication.

## Related Errors

- [HubSpot 403 Forbidden](/hubspot/errors/403) — Token lacks OAuth scopes
- [HubSpot 409 Conflict](/hubspot/errors/409) — Duplicate detected
- [HubSpot 404 Not Found](/hubspot/errors/404) — Resource does not exist
