---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Zoho API DUPLICATE_DATA: Record with same unique field value already exists"
description: "Fix Zoho API DUPLICATE_DATA error. Record with same unique field value already exists. Use UPSERT with duplicate check field parameter instead of INSERT."
tool: "zoho"
errorCode: "DUPLICATE_DATA"
errorName: "DUPLICATE_DATA"
httpStatus: 0
category: "unknown"
severity: "medium"
priority: 2
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "zoho api DUPLICATE_DATA error"
  - "zoho DUPLICATE_DATA fix"
  - "zoho api record with same unique"
---

## What Causes Zoho DUPLICATE_DATA

Zoho returns `DUPLICATE_DATA` when you attempt to create a record with a value that conflicts with an existing unique field constraint. Every module has a set of unique fields (e.g., `Email` on Contacts, `Account_Name` on Accounts) that prevent duplicate records. The error also triggers for custom unique fields configured in Zoho settings.

The response contains `{"code":"DUPLICATE_DATA","details":{"api_name":"Email"},"message":"Record with same unique field value already exists"}`. The `details.api_name` field tells you which field triggered the duplicate check. This is Zoho's server-side protection against data integrity issues — it runs before the record is created.

### Common Scenarios
- Creating a Contact with an email that already exists in the system
- Inserting an Account with a name that matches an existing Account (if configured as unique)
- Bulk imports of Lead/Contact records where some already exist in the CRM
- Re-running a failed import without deduplicating the source data first

## How to Detect If You're Affected

1. Parse the error to find the duplicate field:
   ```bash
   curl -s -X POST "https://www.zohoapis.com/crm/v3/Leads" \
     -H "Authorization: Zoho-oauthtoken $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"data":[{"Last_Name":"Test","Email":"existing@example.com"}]}' | jq '.details.api_name'
   ```
   Returns the field causing the duplicate.

2. Check if a record already exists before inserting:
   ```bash
   curl -s "https://www.zohoapis.com/crm/v3/Leads/search?criteria=Email:equals:existing@example.com" \
     -H "Authorization: Zoho-oauthtoken $TOKEN" | jq '.data | length'
   ```
   If length > 0, a duplicate exists.

## Step-by-Step Fix

### 1. Use UPSERT Instead of INSERT
The UPSERT endpoint checks for duplicates based on the specified field and either inserts or updates:
```python
# BAD — INSERT fails on duplicate
payload = {"data": [{"Last_Name": "Smith", "Email": "smith@example.com"}]}
resp = requests.post("https://www.zohoapis.com/crm/v3/Leads", headers=headers, json=payload)
print(resp.json().get("code"))  # DUPLICATE_DATA

# GOOD — UPSERT with duplicate check field
payload = {
    "data": [{"Last_Name": "Smith", "Email": "smith@example.com"}],
    "duplicate_check_fields": ["Email"]
}
resp = requests.post("https://www.zohoapis.com/crm/v3/Leads/upsert", headers=headers, json=payload)
print(resp.json().get("data")[0]["status"])  # "update" or "create"
```

### 2. Search Before Insert (Pre-Check)
```python
def record_exists(module, field, value):
    url = f"https://www.zohoapis.com/crm/v3/{module}/search?criteria={field}:equals:{value}"
    resp = requests.get(url, headers=headers)
    return len(resp.json().get("data", [])) > 0

# Pre-check before insert
if not record_exists("Leads", "Email", "test@example.com"):
    requests.post("https://www.zohoapis.com/crm/v3/Leads", headers=headers, json=payload)
else:
    print("Skipping duplicate — record already exists")
```

### 3. Handle Duplicates in Bulk Imports
When processing bulk data, log duplicates and continue rather than aborting the entire batch:
```python
results = []
for record in records:
    resp = requests.post(url, headers=headers, json={"data": [record]})
    data = resp.json()
    if data.get("code") == "DUPLICATE_DATA":
        results.append({"record": record, "status": "skipped", "reason": "duplicate"})
    else:
        results.append({"record": record, "status": "created"})
```

## Prevention

- Always use UPSERT with `duplicate_check_fields` for imports instead of INSERT — it handles both new and existing records
- Configure external ID fields in Zoho to use your source system's primary keys for deduplication
- Pre-process source data to remove exact duplicates before any API call
- Log the `details.api_name` field from DUPLICATE_DATA responses to track which fields are causing conflicts
- Set up daily deduplication reports in Zoho CRM to identify and merge existing duplicates

## Official Documentation

- [Zoho CRM API Upsert Records](https://www.zoho.com/crm/developer/docs/api/v3/upsert-records.html)
- [Zoho CRM API Search Records](https://www.zoho.com/crm/developer/docs/api/v3/search-records.html)
- [Zoho CRM API Insert Records](https://www.zoho.com/crm/developer/docs/api/v3/insert-records.html)

## People Also Ask

- **How do I fix Zoho DUPLICATE_DATA?** Use the UPSERT endpoint (`POST /crm/v3/{module}/upsert`) with the `duplicate_check_fields` parameter set to the unique field name (e.g., `["Email"]`). Zoho will update the existing record instead of throwing an error.
- **Can I specify multiple duplicate check fields?** Yes — pass an array like `["Email", "Phone"]`. Zoho checks all specified fields; if any match, the record is updated rather than inserted.
- **Does UPSERT work for all Zoho modules?** Yes — Leads, Contacts, Accounts, Deals, and custom modules all support UPSERT. The behavior is consistent across modules.
- **What fields can I use for duplicate detection?** Any field with unique constraints enabled in Zoho settings — typically Email for Contacts/Leads, Account_Name for Accounts, and any custom fields with "Unique" checked in field properties.

## Related Errors

- [Zoho MANDATORY_NOT_FOUND](/zoho/errors/MANDATORY_NOT_FOUND) — Required field missing in request
- [Zoho LIMIT_EXCEEDED](/zoho/errors/LIMIT_EXCEEDED) — General API limit reached
- [Zoho INVALID_OAUTHTOKEN](/zoho/errors/INVALID_OAUTHTOKEN) — Access token expired or invalid
