---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Salesforce API 404: Resource does not exist"
description: "Fix Salesforce API 404 (404 Not Found) error. Resource does not exist. Verify record ID, API version, and endpoint path."
tool: "salesforce"
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
  - "salesforce api 404 error"
  - "salesforce 404 fix"
  - "salesforce api resource does not exist"
  - "salesforce http 404"
---

## What Causes Salesforce 404

Salesforce returns HTTP 404 when the requested resource does not exist at the specified URL. This can be caused by an invalid record ID, a wrong API version, a mistyped endpoint path, or referencing a record that has been deleted or whose ID format is incorrect.

Salesforce uses 18-character record IDs (the 15-character ID + 3-character suffix) for all records. A 404 with `NOT_FOUND` error code means the ID doesn't map to any record in the system. API versions follow the pattern `/services/data/v{version}/` — using a version number that doesn't exist also returns 404.

### Common Scenarios
- Using a 15-character ID when Salesforce expects 18 characters (the 3-character suffix is missing)
- Referencing a record that was hard-deleted (emptied from Recycle Bin)
- Making a request to a non-existent API version (e.g., `v99.0`)
- Typo in the endpoint path (e.g., `sobject` instead of `sobjects`)
- Referencing a record from a different Salesforce org or sandbox

## How to Detect If You're Affected

1. Test the record ID with a direct query:
   ```bash
   curl -s -w "\n%{http_code}" "https://yourdomain.my.salesforce.com/services/data/v60.0/sobjects/Contact/003XXXXXXXXXXXXXXX" \
     -H "Authorization: Bearer $TOKEN" | tail -1
   ```

2. Verify the record exists with a SOQL query:
   ```bash
   curl -s "https://yourdomain.my.salesforce.com/services/data/v60.0/query?q=SELECT+Id+FROM+Contact+WHERE+Id='003XXXXXXXXXXXXXXX'" \
     -H "Authorization: Bearer $TOKEN" | jq '.totalSize'
   ```

3. Check API version availability:
   ```bash
   curl -s "https://yourdomain.my.salesforce.com/services/data/" \
     -H "Authorization: Bearer $TOKEN" | jq '.'
   ```

## Step-by-Step Fix

### 1. Validate Record ID
```python
import re

# Salesforce IDs are 15 or 18 characters, alphanumeric
def is_valid_sf_id(value):
    return bool(re.match(r'^[a-zA-Z0-9]{15,18}$', value))

# BAD — invalid ID format
record_id = "123"  # Too short
resp = requests.get(f"{instance_url}/services/data/v60.0/sobjects/Contact/{record_id}", headers=headers)
print(resp.status_code)  # 404

# GOOD — valid format
record_id = "0035x000007ABCdEAO"  # 18 chars
if is_valid_sf_id(record_id):
    resp = requests.get(f"{instance_url}/services/data/v60.0/sobjects/Contact/{record_id}", headers=headers)
```

### 2. Query to Confirm Existence
```python
def record_exists(sobject, record_id):
    query_url = f"{instance_url}/services/data/v60.0/query"
    params = {"q": f"SELECT Id FROM {sobject} WHERE Id='{record_id}'"}
    resp = requests.get(query_url, headers=headers, params=params)
    return resp.json().get("totalSize", 0) > 0

# Check before accessing
if record_exists("Contact", "0035x000007ABCdEAO"):
    resp = requests.get(f"{instance_url}/services/data/v60.0/sobjects/Contact/0035x000007ABCdEAO", headers=headers)
else:
    print("Record not found — may have been deleted")
```

### 3. Verify API Version and Endpoint
```python
# Get available API versions
versions_resp = requests.get(f"{instance_url}/services/data/", headers=headers)
available_versions = [v["version"] for v in versions_resp.json()]
print(f"Available versions: {available_versions}")

# BAD — non-existent version
url = f"{instance_url}/services/data/v99.0/sobjects/Contact"  # 404

# GOOD — use a valid version (latest is recommended)
latest_version = available_versions[-1]
url = f"{instance_url}/services/data/v{latest_version}/sobjects/Contact"
```

## Prevention

- Always use 18-character record IDs (convert 15-char to 18-char if needed)
- Query for a record before attempting to read or update it
- Use the latest stable API version, avoid deprecated versions
- Never hardcode record IDs — fetch them dynamically from SOQL queries
- Handle 404 by re-querying for fresh IDs rather than retrying the same request

## Official Documentation

- [Salesforce REST API](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/)
- [Salesforce SOQL](https://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta/soql_sosl/)
- [Salesforce Record IDs](https://help.salesforce.com/s/articleView?id=sf.faq_general_develop.htm)

## People Also Ask

- **What's the difference between 15 and 18 character Salesforce IDs?** The 18-character ID is the 15-character ID with a 3-character suffix that encodes case. Use 18-character IDs for API calls to avoid case-sensitivity issues.
- **Can I get 404 for a record in the Recycle Bin?** Yes — if the record is in the Recycle Bin, it still exists but returns 404 from the standard API. Use `ALL ROWS` in SOQL to query deleted records.
- **How do I find the latest Salesforce API version?** Call `GET /services/data/` to list all available versions. The highest version number is the latest.
- **Does Salesforce 404 apply to deleted records?** Hard-deleted records (emptied from Recycle Bin) return 404. Soft-deleted records (in Recycle Bin) also return 404 from the standard REST API.

## Related Errors

- [Salesforce 400 Bad Request](/salesforce/errors/400) — Invalid payload or field values
- [Salesforce 401 Unauthorized](/salesforce/errors/401) — Session expired or invalid
- [Salesforce 403 Forbidden](/salesforce/errors/403) — Request refused
