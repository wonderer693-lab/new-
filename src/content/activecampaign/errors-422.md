---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "ActiveCampaign API 422: Missing or invalid parameter"
description: "Fix ActiveCampaign API 422 (422 Unprocessable Entity) error. Missing or invalid parameter — request understood but cannot be processed. Check error titles for which fields are missing or invalid."
tool: "activecampaign"
errorCode: "422"
errorName: "422 Unprocessable Entity"
httpStatus: 422
category: "validation"
severity: "medium"
priority: 2
lastUpdated: '2026-04-17'
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "activecampaign api 422 error"
  - "activecampaign 422 fix"
  - "activecampaign api missing or invalid parameter"
  - "activecampaign http 422"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** ActiveCampaign rejected your data format. A required field is missing or a value has the wrong type.

**The fix:**
1. Check the error message — it tells you exactly which field is wrong
2. Make sure required fields are included (like `email` for contacts)
3. Verify field types match what ActiveCampaign expects (text vs number vs date)

**Copy-paste this code** (if you're using a code editor):
```python
import requests

headers = {"Api-Token": "YOUR_TOKEN", "Content-Type": "application/json"}
payload = {"contact": {"email": "test@example.com", "firstName": "John"}}
resp = requests.post("https://{account}.api-us1.com/api/3/contacts", headers=headers, json=payload)
if resp.status_code == 422:
    print(resp.json()["errors"])  # Shows exactly which field is wrong
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Start with this prompt in ChatGPT, Claude, or any AI coding assistant:

> I'm getting a 422 Unprocessable Entity error from the ActiveCampaign API.
> The error message is: "Missing or invalid parameter"
> I'm trying to create a contact but ActiveCampaign rejects my request.
> Please give me a step-by-step fix with working Python code and the correct payload format.

A good response will show you the correct payload structure, list required fields, and explain how to read the error details to find the exact problem field.

Follow up with additional context if needed:
> The fix didn't work. Here's my payload and the full error response: [paste both]. Please tell me exactly which field is wrong.

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to validate data before sending in popular automation tools:

### Zapier
1. Open your Zap → click the ActiveCampaign action step
2. Check that all required fields are mapped (e.g., email is required for contacts)
3. Add a "Formatter by Zapier" step before the action to clean up data (trim spaces, format dates)

### Make (Integromat)
1. Open your scenario → click the ActiveCampaign module → check mapped fields
2. Add a "Tools > Set Multiple Variables" module before it to validate and format values
3. Use the "Tools > Parse JSON" module to check your data structure before sending

### n8n
1. Open your workflow → click the ActiveCampaign node → verify all required fields are set
2. Add a "Function" node before it to validate data (check email format, required fields)
3. Use an IF node to skip invalid records instead of sending bad data

### Power Automate
1. Open your flow → click the ActiveCampaign action → check required field mappings
2. Add a "Compose" action before it to format and validate data
3. Add a "Condition" to check that required fields are not empty before sending

**Which tool should you use?** Zapier's Formatter step is the easiest way to clean data before it hits ActiveCampaign — it handles date formatting, text trimming, and email validation out of the box.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"422 Unprocessable Entity"`
- `"validation failed"`
- `"Missing or invalid parameter"`
- `"cannot be processed"` in your integration logs

**What it means in plain English:** ActiveCampaign understood your request but the data you sent has a problem. A required field might be empty, a number field might have text, or a date might be in the wrong format.

**Most common cause:** Sending a contact creation request without an email address, or using the wrong data type for a field (like sending "abc" where a number is expected).

</div>

## What Causes ActiveCampaign 422

ActiveCampaign returns HTTP 422 when the request is syntactically valid but the server cannot process it due to missing or invalid parameters. This is a validation error — the endpoint exists and the JSON parses, but the data doesn't meet business rules.

The response includes an `errors` array with `title` and `detail` fields that indicate which parameter is wrong. Common validation failures: missing required fields on contact creation (like `email`), invalid field values (string where number expected), or attempting to set a value that doesn't match the field type.

### Common Scenarios
- Creating a contact without providing an email address
- Sending a string value for a field that expects an integer (e.g., `"0"` instead of `0`)
- Including an unrecognized field name in the payload
- Setting a date field to an invalid date format
- Trying to assign a tag or list that doesn't exist (returns 404, but the surrounding payload might also cause 422)

## How to Detect If You're Affected

1. Parse the errors array to identify the problematic field:
   ```bash
   curl -s -X POST "https://{account}.api-us1.com/api/3/contacts" \
     -H "Api-Token: $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"contact":{"email":"","firstName":"Test"}}' | jq '.errors'
   ```

2. Check the error title and detail:
   ```bash
   curl -s -X POST "https://{account}.api-us1.com/api/3/contacts" \
     -H "Api-Token: $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"contact":{"email":"test@example.com","field":"invalid"}}' \
     | jq '.errors[] | {title: .title, detail: .detail, field: .source.pointer}'
   ```

3. Validate your payload against ActiveCampaign's documented schema: compare field names exactly as documented.

## Step-by-Step Fix

### 1. Identify the Invalid Field
```python
import requests

headers = {"Api-Token": "YOUR_TOKEN"}
url = "https://{account}.api-us1.com/api/3/contacts"
payload = {"contact": {"email": "test@example.com", "invalid_field": "value"}}

resp = requests.post(url, headers=headers, json=payload)
if resp.status_code == 422:
    errors = resp.json().get("errors", [])
    for err in errors:
        print(f"Field: {err.get('source', {}).get('pointer', 'unknown')}")
        print(f"Error: {err.get('title', '')} — {err.get('detail', '')}")
```

### 2. Fix Required Fields (Contact Example)
```python
# BAD — missing required email
bad_payload = {"contact": {"firstName": "John"}}
resp = requests.post(url, headers=headers, json=bad_payload)
print(resp.status_code)  # 422

# GOOD — include all required fields
good_payload = {"contact": {"email": "john@example.com", "firstName": "John"}}
resp = requests.post(url, headers=headers, json=good_payload)
print(resp.status_code)  # 201 Created
```

### 3. Validate Field Types
```python
# BAD — wrong type for a numeric field
payload = {"contact": {"email": "test@example.com", "phone": "not_a_number"}}

# GOOD — use correct types per ActiveCampaign API docs
# Strings for text fields, integers for ID fields, ISO dates for date fields
payload = {"contact": {"email": "test@example.com", "phone": "+1234567890"}}
```

## Prevention

- Validate payloads against ActiveCampaign's API schema before sending
- Use the API Playground in ActiveCampaign settings to test payloads interactively
- Log the full errors array from 422 responses — it pinpoints the exact problem
- Build a schema validation step into your integration (e.g., Python `jsonschema` library)
- Test each field type independently when integrating a new ActiveCampaign module

## Official Documentation

- [ActiveCampaign API Overview](https://developers.activecampaign.com/reference/overview)
- [ActiveCampaign Create Contact](https://developers.activecampaign.com/reference/create-a-contact)
- [ActiveCampaign API Errors](https://developers.activecampaign.com/reference/errors)

## People Also Ask

- **What's the difference between ActiveCampaign 400 and 422?** 400 means the JSON is malformed (can't parse). 422 means the JSON is valid but the data fails business validation rules.
- **How do I find required fields for ActiveCampaign endpoints?** Check the API documentation for each endpoint — required fields are marked in the request body schema.
- **Can 422 be caused by duplicate data?** ActiveCampaign uses 422 for validation errors including duplicates in some cases, but duplicates typically return a different error structure.
- **What does the source.pointer field mean?** It indicates which part of the request body caused the error, using JSON pointer notation (e.g., `/data/attributes/email`).

See all [ActiveCampaign API errors](/activecampaign/) in our complete reference.

Similar validation issues occur with [HubSpot 400](/hubspot/errors/400), [Salesforce 400](/salesforce/errors/400), and [Mailchimp 400](/mailchimp/errors/400).

This error also affects integrations. See our [ActiveCampaign to Slack](/integrations/activecampaign-to-slack/) and [Salesforce to ActiveCampaign](/integrations/salesforce-to-activecampaign/) integration error guides.

## Related Errors

- [ActiveCampaign 404 Not Found](/activecampaign/errors/404) — Resource does not exist
- [ActiveCampaign 401 Unauthorized](/activecampaign/errors/401) — Invalid or missing API token
- [ActiveCampaign 429 Rate Limit](/activecampaign/errors/429) — Too many requests
