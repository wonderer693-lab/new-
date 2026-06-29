---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Zoho API MANDATORY_NOT_FOUND: Required field missing in request"
description: "Fix Zoho API MANDATORY_NOT_FOUND error. Required field missing in request. Check module metadata for mandatory fields."
tool: "zoho"
errorCode: "MANDATORY_NOT_FOUND"
errorName: "MANDATORY_NOT_FOUND"
httpStatus: 0
category: "unknown"
severity: "medium"
priority: 2
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "zoho api MANDATORY_NOT_FOUND error"
  - "zoho MANDATORY_NOT_FOUND fix"
  - "zoho api required field missing in"
---

## What Causes Zoho MANDATORY_NOT_FOUND

Zoho returns `MANDATORY_NOT_FOUND` when an API request omits a required field that Zoho's module schema mandates. Each Zoho module (Leads, Contacts, Accounts, etc.) has its own set of mandatory fields defined in the CRM settings, and Zoho validates every request against this schema before processing.

The error response contains `{"code":"MANDATORY_NOT_FOUND","details":{"api_name":"Last_Name"},"message":"required field not found"}`. The `details.api_name` field tells you exactly which field is missing. The most common culprit is `Last_Name`, which is mandatory for Leads and Contacts by default.

### Common Scenarios
- `Last_Name` missing on Lead or Contact creation (the most frequent case)
- Custom mandatory fields added by the Zoho admin but not reflected in the integration
- Empty strings or null values sent for mandatory fields (Zoho treats these as missing)
- Wrong `api_name` used for a field (e.g., `LastName` instead of `Last_Name`)

## How to Detect If You're Affected

1. Parse the error response to identify the missing field:
   ```bash
   curl -s -X POST "https://www.zohoapis.com/crm/v3/Leads" \
     -H "Authorization: Zoho-oauthtoken $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"data":[{"Company":"Acme"}]}' | jq '.details.api_name'
   ```
   This returns the missing field name, e.g., `"Last_Name"`.

2. Fetch the module's field metadata to see all mandatory fields:
   ```bash
   curl -s "https://www.zohoapis.com/crm/v3/settings/fields?module=Leads" \
     -H "Authorization: Zoho-oauthtoken $TOKEN" | jq '.fields[] | select(.system_mandatory==true) | .api_name'
   ```

## Step-by-Step Fix

### 1. Identify the Missing Field
Check the error response's `details.api_name` to find the exact field:
```python
resp = requests.post(url, headers=headers, json=payload)
error = resp.json()
missing_field = error.get("details", {}).get("api_name")
print(f"Missing mandatory field: {missing_field}")
```

### 2. Fetch Mandatory Fields Dynamically
Instead of hardcoding the field list, query Zoho's schema at startup:
```python
def get_mandatory_fields(module):
    url = f"https://www.zohoapis.com/crm/v3/settings/fields?module={module}"
    resp = requests.get(url, headers=headers)
    fields = resp.json().get("fields", [])
    return [f["api_name"] for f in fields if f.get("system_mandatory")]
```

### 3. Validate Before Sending
```python
# BAD: send without checking
payload = {"data": [{"Company": "Acme"}]}
requests.post("https://www.zohoapis.com/crm/v3/Leads", headers=headers, json=payload)

# GOOD: validate first
mandatory = get_mandatory_fields("Leads")
for field in mandatory:
    if field not in payload["data"][0]:
        print(f"Field {field} is required")
        # Add sensible default or raise error
```

## Prevention

- Dynamically fetch required fields from Zoho's `/settings/fields` endpoint instead of hardcoding them
- Add pre-submit validation that compares payload against system_mandatory fields
- Log `details.api_name` from every MANDATORY_NOT_FOUND response — it pinpoints schema drift
- Test with empty payloads in your sandbox to discover all mandatory fields before production
- Include `Last_Name` and `Company` in every Lead/Contact payload (they are mandatory by default)

## Official Documentation

- [Zoho CRM API Field Metadata](https://www.zoho.com/crm/developer/docs/api/v3/field-meta.html)
- [Zoho CRM API Modules](https://www.zoho.com/crm/developer/docs/api/v3/modules.html)
- [Zoho CRM API Overview](https://www.zoho.com/crm/developer/docs/api/v3/)

## People Also Ask

- **What is the most common missing field in Zoho?** `Last_Name` — it's a system-mandatory field for Leads and Contacts. Zoho cannot create a record without it.
- **How do I find which fields are mandatory in Zoho?** Call `GET /crm/v3/settings/fields?module=Leads` and filter for fields where `system_mandatory` is `true`. This returns the exact set of required fields for that module.
- **Does Zoho MANDATORY_NOT_FOUND apply to custom fields?** Yes — if an admin marks a custom field as required in Zoho settings, the API enforces it the same as system-mandatory fields.
- **Can I bypass mandatory field validation?** No — Zoho API enforces mandatory fields server-side. However, you can set default values in Zoho settings for some field types to avoid omitting them.

## Related Errors

- [Zoho DUPLICATE_DATA](/zoho/errors/DUPLICATE_DATA) — Record with same unique field value already exists
- [Zoho LIMIT_EXCEEDED](/zoho/errors/LIMIT_EXCEEDED) — General API limit reached
- [Zoho INVALID_OAUTHTOKEN](/zoho/errors/INVALID_OAUTHTOKEN) — Access token expired or invalid
