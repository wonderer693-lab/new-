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

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** HubSpot rejected your request because the data format is wrong.

**The fix:**
1. Check the error message — it tells you which field is invalid
2. Make sure property names are lowercase (use `firstname`, not `FirstName`)
3. Make sure values match the expected data type (numbers for number fields, valid emails, etc.)

**Copy-paste this code** (if you're using a code editor):
```python
import requests

resp = requests.post(url, headers=headers, json=payload)
if resp.status_code == 400:
    error = resp.json()
    print(f"Bad field: {error.get('message')}")
    print(f"Category: {error.get('category')}")
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm getting a 400 Bad Request error from the HubSpot API when trying to create a contact.
> The error message says "Invalid input" and "Property value is not valid."
> I'm sending this data: [paste your JSON payload].
> Please tell me which fields are wrong and give me the corrected payload.

**What to expect:** The AI should identify the invalid property names or data types and give you a corrected JSON payload that matches HubSpot's schema.

**If it doesn't work**, add this follow-up:
> The fix didn't work. Here's the full error response: [paste the error JSON]. Please debug this step by step.

**Best AI tools for this:** Claude (best at explaining validation rules), ChatGPT-4 (good at fixing JSON payloads), Cursor (if you want inline code fixes)

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to handle HubSpot 400 validation errors in popular automation tools:

### Zapier
1. Open your Zap → click the HubSpot action step
2. Check each mapped field — make sure you're using HubSpot's internal field names (lowercase with underscores)
3. Add a "Formatter by Zapier" step before the HubSpot action to validate and clean data (e.g., trim whitespace, format dates)

### Make (Integromat)
1. Open your scenario → click the HubSpot module
2. Add a "Data Validation" module before the HubSpot module to check field formats
3. In the HubSpot module mapping, verify each field name matches HubSpot's API names exactly (case-sensitive)

### n8n
1. Open your workflow → click the HubSpot node
2. Add a "Set" node before the HubSpot node to rename fields to HubSpot's lowercase format
3. In "Settings" → enable "Continue On Fail" and add an error handler that logs the invalid field names

### Power Automate
1. Open your flow → click the HubSpot action
2. Add a "Compose" action before the HubSpot action to format and validate your data
3. Check the "Inputs" field mapping — make sure email fields contain valid emails and number fields contain numbers, not text

**Which tool should you use?** Make has the best data validation module — it lets you check field formats before sending data to HubSpot.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"400 Bad Request"`
- `"Invalid input"`
- `"Property value is not valid"`
- `"Property does not exist"` in your integration logs

**What it means in plain English:** HubSpot doesn't like the data you sent. Either a field name is wrong, a value is the wrong type, or a required field is missing.

**Most common cause:** Using the wrong property name (like `FirstName` instead of `firstname`) or sending text where HubSpot expects a number.

</div>

## What Causes HubSpot 400

HubSpot returns HTTP 400 when the request body contains invalid JSON, unknown property names, incorrect property data types, or missing required fields. HubSpot's CRM validates every request against the object type's schema — for example, a Contact creation request must use valid Contact property names like `email`, `firstname`, `lastname`, and values must match the property's data type.

The response includes `{"status":"error","message":"...","category":"VALIDATION_ERROR"}` with details about which field failed validation. The `message` field often includes the specific property name and expected format. See all [HubSpot API errors](/hubspot/) in our complete reference.

This error also affects integrations. See our [HubSpot to Slack integration errors](/integrations/hubspot-to-slack/) for common cross-tool issues.

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
- Similar validation issues occur with [Salesforce 400](/salesforce/errors/400), [Mailchimp 400](/mailchimp/errors/400), and [Make 400](/make/errors/400).

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
