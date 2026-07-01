---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Salesforce API 400: Request body malformed, invalid JSON/XML, or invalid fiel..."
description: "Fix Salesforce API 400 (400 Bad Request) error. Request body malformed, invalid JSON/XML, or invalid field values. Log full request body and response."
tool: "salesforce"
errorCode: "400"
errorName: "400 Bad Request"
httpStatus: 400
category: "validation"
severity: "medium"
priority: 2
lastUpdated: '2026-05-11'
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "salesforce api 400 error"
  - "salesforce 400 fix"
  - "salesforce api request body malformed, invalid"
  - "salesforce http 400"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Salesforce rejected your data format — wrong field type, missing required field, or invalid JSON.

**The fix:**
1. Check the `errorCode` in the response (`INVALID_FIELD`, `MALFORMED_QUERY`, `FIELD_INTEGRITY_EXCEPTION`)
2. Make sure every field name in your payload matches a real Salesforce field
3. Validate your JSON is well-formed (no trailing commas, proper quotes)

**Copy-paste this code** (if you're using a code editor):
```python
import json, requests

payload = {"LastName": "Test", "Email": "test@example.com"}
json.dumps(payload)
resp = requests.post(url, headers=headers, json=payload)
if resp.status_code == 400:
    print(resp.json()[0]["errorCode"], resp.json()[0]["message"])
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Start with this prompt in ChatGPT, Claude, or any AI coding assistant:

> I'm getting a 400 Bad Request error from the Salesforce API.
> The error message is: "INVALID_FIELD" or "MALFORMED_QUERY"
> I'm sending a POST request to create a Contact record.
> Please give me a step-by-step fix with working Python code that validates the payload before sending.

A good response will give you a payload validator that checks field names against the Salesforce SObject describe endpoint and fixes JSON formatting issues.

Follow up with additional context if needed:
> The fix didn't work. I'm still getting 400 errors. Here's my payload: [paste your payload]. Here's the error: [paste error response]. Please debug this.

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to handle Salesforce data validation errors in popular automation tools:

### Zapier
1. Open your Zap → click the Salesforce action step
2. In the field mapping, check that every field matches a real Salesforce field name (e.g., "LastName" not "Last_Name")
3. Add a "Formatter by Zapier" step before Salesforce to validate and clean data (use "Text" → "Trim Whitespace")

### Make (Integromat)
1. Open your scenario → right-click the Salesforce module → "Add error handler"
2. Choose "Ignore" or "Resume" → log the error so you can see which field caused the 400
3. Add a "Set" module before Salesforce to validate field names and remove empty values

### n8n
1. Open your workflow → add a "Function" node before the Salesforce node
2. In the Function node, add validation: `if (!item.LastName) throw new Error("Missing required field")`
3. Check the Salesforce node field mapping — make sure field names match exactly (case-sensitive)

### Power Automate
1. Open your flow → click the Salesforce action
2. In the field mapping, verify each field name against your Salesforce object's field list
3. Add a "Condition" action before Salesforce to check that required fields are not empty

**Which tool should you use?** Make has the best error handling for Salesforce — you can catch 400 errors and route them to a fix queue automatically.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"400 Bad Request"`
- `"INVALID_FIELD"`
- `"MALFORMED_QUERY"`
- `"FIELD_INTEGRITY_EXCEPTION"` in your integration logs

**What it means in plain English:** Salesforce didn't understand your request. The data you sent has a problem — a field name is wrong, a value is the wrong type, or the JSON is broken.

**Most common cause:** Sending a field that doesn't exist on the Salesforce object, or sending a text value where Salesforce expects a number or date.

</div>

## What Causes Salesforce 400

Salesforce returns HTTP 400 when the request body is malformed, contains invalid JSON or XML, or has invalid field values that fail server-side parsing. See all [Salesforce API errors](/salesforce/) in our complete reference. The response includes an `errorCode` and `message` that pinpoints the problem — common codes include `MALFORMED_ID`, `INVALID_FIELD`, `INVALID_OR_NULL_FOR_RESTRICTED_PICKLIST`, and `FIELD_INTEGRITY_EXCEPTION`.

The response body looks like `[{"message":"field integrity exception: unknown","errorCode":"FIELD_INTEGRITY_EXCEPTION","fields":["CustomField__c"]}]`. Unlike 422 (which some APIs use for validation), Salesforce uses 400 for both syntax and validation errors across all REST API operations.

### Common Scenarios
- Sending an ID that doesn't match the 18-character Salesforce ID format
- Including a field name in the payload that doesn't exist on the SObject
- Sending a picklist value that isn't in the allowed picklist values
- Malformed JSON with trailing commas, unescaped quotes, or mismatched brackets
- Sending a date/time value in an incorrect format

## How to Detect If You're Affected

1. Capture the full error response:
   ```bash
   curl -s -X POST "https://yourdomain.my.salesforce.com/services/data/v60.0/sobjects/Contact" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"LastName":"Test","InvalidField":"value"}' | jq '.'
   ```

2. Check for malformed JSON:
   ```bash
   echo '{"LastName":"Test",}' | python -c "import sys,json; json.load(sys.stdin)" 2>&1
   # Will print error if JSON is invalid
   ```

3. Validate the payload against the SObject describe:
   ```bash
   curl -s "https://yourdomain.my.salesforce.com/services/data/v60.0/sobjects/Contact/describe" \
     -H "Authorization: Bearer $TOKEN" | jq '.fields[] | {name: .name, type: .type}'
   ```

## Step-by-Step Fix

### 1. Validate JSON Before Sending
```python
import json

# BAD — malformed JSON (trailing comma)
payload = '{"LastName": "Test", "Email": "test@example.com",}'

# GOOD — validate JSON first
try:
    payload_dict = {"LastName": "Test", "Email": "test@example.com"}
    json.dumps(payload_dict)  # Validates serialization
    resp = requests.post(url, headers=headers, json=payload_dict)
except (json.JSONDecodeError, TypeError) as e:
    print(f"Invalid JSON: {e}")
```

### 2. Validate Fields Against SObject Describe
```python
def get_sobject_fields(sobject):
    describe_url = f"{instance_url}/services/data/v60.0/sobjects/{sobject}/describe"
    resp = requests.get(describe_url, headers=headers)
    return {f["name"]: f["type"] for f in resp.json()["fields"]}

contact_fields = get_sobject_fields("Contact")

# BAD — using invalid field
payload = {"LastName": "Test", "NonExistentField__c": "value"}  # 400

# GOOD — check field exists
def validate_payload(payload, valid_fields):
    for field in payload:
        if field not in valid_fields:
            raise ValueError(f"Unknown field: {field}")

validate_payload(payload, contact_fields)
```

### 3. Fix Common Field-Type Issues
```python
# BAD — wrong format for Date field
payload = {"LastName": "Test", "BirthDate": "not-a-date"}  # 400

# GOOD — use correct format (ISO 8601 for Date fields)
payload = {"LastName": "Test", "BirthDate": "1990-01-15"}

# BAD — Restricted picklist invalid value
payload = {"LastName": "Test", "LeadSource": "InvalidSource"}  # 400

# GOOD — use picklist values from describe
# Get picklist values from describe endpoint
lead_source_values = ["Web", "Phone", "Email", "Other"]
payload = {"LastName": "Test", "LeadSource": "Web"}
```

## Prevention

- Always validate payloads against the SObject describe endpoint before posting
- Use a JSON schema validator in your integration to catch malformed payloads early
- Log both the full request body and the full error response for debugging
- Fetch picklist values from the describe endpoint rather than hardcoding them
- Test with a single record before bulk operations using the same payload structure
- Similar validation issues occur with [HubSpot 400](/hubspot/errors/400), [Mailchimp 400](/mailchimp/errors/400), and [Pipedrive 400](/pipedrive/errors/400).
- This error also affects integrations. See our [Salesforce to Mailchimp](/integrations/salesforce-to-mailchimp/) and [Salesforce to ActiveCampaign](/integrations/salesforce-to-activecampaign/) integration error guides.

## Official Documentation

- [Salesforce REST API](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/)
- [Salesforce SObject Describe](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_sobject_describe.htm)
- [Salesforce Error Codes](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/errorcodes.htm)

## People Also Ask

- **What does Salesforce FIELD_INTEGRITY_EXCEPTION mean?** A field value violates a database constraint — required field empty, invalid lookup reference, or value doesn't match picklist options.
- **How do I find valid Salesforce field names?** Call `GET /services/data/v60.0/sobjects/{ObjectName}/describe` and check the `fields` array for `name` and `type`.
- **Why does Salesforce return 400 for valid JSON?** 400 can also mean invalid field values — check the `errorCode` in the response body. `MALFORMED_ID` means the ID format is wrong, `INVALID_FIELD` means the field doesn't exist.
- **What's the difference between Salesforce 400 and 404?** 400 means the request payload is invalid. 404 means the endpoint or resource doesn't exist.

## Related Errors

- [Salesforce 401 Unauthorized](/salesforce/errors/401) — Session expired or invalid
- [Salesforce 403 Forbidden](/salesforce/errors/403) — Request refused
- [Salesforce 404 Not Found](/salesforce/errors/404) — Resource does not exist
