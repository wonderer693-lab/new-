---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Salesforce API 403: Request refused"
description: "Fix Salesforce API 403 (403 Forbidden) error. Request refused — resource not accessible to user. Check /limits endpoint for remaining allocations."
tool: "salesforce"
errorCode: "403"
errorName: "403 Forbidden"
httpStatus: 403
category: "permission"
severity: "high"
priority: 1
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "salesforce api 403 error"
  - "salesforce 403 fix"
  - "salesforce api request refused — resource"
  - "salesforce http 403"
---

## What Causes Salesforce 403

Salesforce returns HTTP 403 when the authenticated user does not have permission to access the requested resource or when an API limit has been exhausted. The response includes an `errorCode` that distinguishes between permission issues (`REQUEST_NOT_AUTHORIZED`, `INSUFFICIENT_ACCESS`) and limit issues (`API_LIMIT_EXCEEDED`, `STORAGE_LIMIT_EXCEEDED`).

The response looks like `[{"message":"Insufficient permissions","errorCode":"INSUFFICIENT_ACCESS_OR_READONLY","fields":[]}]`. Unlike 401 (invalid session), 403 means the session is valid but the user's profile or permission set doesn't grant access to the specific object, field, or operation.

### Common Scenarios
- The integration user has read-only access but the integration tries to create or update records
- The user's profile doesn't include access to a specific object (e.g., custom object)
- Field-level security restricts the user from viewing or editing a specific field
- API request limits for the org have been exhausted (daily or concurrent)
- The user's IP is outside the trusted IP ranges configured in the org

## How to Detect If You're Affected

1. Check the error code to distinguish permission vs limit issues:
   ```bash
   curl -s "https://yourdomain.my.salesforce.com/services/data/v60.0/sobjects/Contact" \
     -H "Authorization: Bearer $TOKEN" | jq '.[0]'
   ```

2. Check API limits:
   ```bash
   curl -s "https://yourdomain.my.salesforce.com/services/data/v60.0/limits" \
     -H "Authorization: Bearer $TOKEN" | jq '.DailyApiRequests'
   ```

3. Verify user permissions (requires Salesforce admin access):
   ```bash
   # No direct API — check in Setup > Users > [User] > Permission Sets
   ```

## Step-by-Step Fix

### 1. Check API Limit Remaining
```python
import requests

# Check remaining API calls
limits_resp = requests.get(f"{instance_url}/services/data/v60.0/limits", headers=headers)
limits = limits_resp.json()
daily_api = limits.get("DailyApiRequests", {})
print(f"Used: {daily_api.get('Remaining')} of {daily_api.get('Max')}")
```

### 2. Verify Object and Field Permissions
```python
# Describe the object to check what fields are accessible
describe_resp = requests.get(
    f"{instance_url}/services/data/v60.0/sobjects/Contact/describe",
    headers=headers,
)
fields = describe_resp.json().get("fields", [])
for field in fields:
    if not field.get("updateable"):
        print(f"Field not updateable: {field['name']}")

# BAD — trying to write to a read-only field
payload = {"LastName": "Test", "CreatedDate": "2026-01-01"}  # 403

# GOOD — only include updateable fields
editable_fields = [f["name"] for f in fields if f.get("updateable")]
payload = {f: value for f, value in data.items() if f in editable_fields}
```

### 3. Fix Permission Issues Programmatically
```python
# Check if user has access to a specific object
def check_object_access(sobject):
    resp = requests.get(
        f"{instance_url}/services/data/v60.0/sobjects/{sobject}",
        headers=headers,
    )
    if resp.status_code == 403:
        print(f"No access to {sobject} — check user permissions")
        return False
    return True

# Test before attempting operations
if check_object_access("CustomObject__c"):
    # Proceed with create/update
    pass
```

## Prevention

- Use a dedicated integration user with "Modify All Data" or full API permission set
- Map required API operations to specific permission sets and verify before deployment
- Monitor the `/limits` endpoint daily to track API consumption and avoid limit exhaustion
- Set up alerts in Salesforce for API limit usage above 80%
- Document all objects and fields the integration needs and verify access during setup

## Official Documentation

- [Salesforce Limits](https://developer.salesforce.com/docs/atlas.en-us.salesforce_app_limits_cheatsheet.meta/salesforce_app_limits_cheatsheet/)
- [Salesforce Permission Sets](https://help.salesforce.com/s/articleView?id=sf.perm_sets_overview.htm)
- [Salesforce Object Permissions](https://help.salesforce.com/s/articleView?id=sf.record_type_visibility.htm)

## People Also Ask

- **What's the difference between Salesforce 401 and 403?** 401 means the session is invalid or expired. 403 means the session is valid but the user doesn't have permission for the requested resource.
- **How do I check remaining Salesforce API calls?** Call `GET /services/data/v60.0/limits` and check the `DailyApiRequests.Remaining` field.
- **Can field-level security cause 403?** Yes — if a user has object-level access but a specific field is restricted by field-level security (FLS), writing to that field returns 403.
- **What is INSUFFICIENT_ACCESS_OR_READONLY?** The user has read access but not write access to the object or field. Check the user's profile and permission sets for write permissions.

## Related Errors

- [Salesforce 401 Unauthorized](/salesforce/errors/401) — Session expired or invalid
- [Salesforce 429 REQUEST_LIMIT_EXCEEDED](/salesforce/errors/429) — Rate limit exceeded
- [Salesforce 503 Service Unavailable](/salesforce/errors/503) — Server overload
