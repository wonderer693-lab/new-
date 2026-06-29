---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Salesforce API 409: Conflict with current resource state (e"
description: "Fix Salesforce API 409 (409 Conflict) error. Conflict with current resource state (e. Check API version compatibility with the resource being accessed."
tool: "salesforce"
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
  - "salesforce api 409 error"
  - "salesforce 409 fix"
  - "salesforce api conflict with current resource"
  - "salesforce http 409"
---

## What Causes Salesforce 409

Salesforce returns HTTP 409 when the request conflicts with the current state of the resource. The most common cause is an API version incompatibility — attempting to use an API feature that isn't available in the specified version. It can also occur with duplicate detection rules, where creating a record would create a duplicate that violates an org's duplicate rule.

The response contains `[{"message":"API version x not supported for this resource","errorCode":"API_VERSION_NOT_SUPPORTED"}]`. This is distinct from 400 (invalid payload) — 409 means the request is valid but can't be applied due to the resource's current state.

### Common Scenarios
- Using an API version that doesn't support a specific feature (e.g., Platform Event publishing in older versions)
- Duplicate rule matching: creating an Account with a name that matches a duplicate rule
- Attempting to insert a record that triggers a fuzzy-matching duplicate rule
- Using a Beta API feature that was removed in a newer version

## How to Detect If You're Affected

1. Check the error code in the response:
   ```bash
   curl -s -X POST "https://yourdomain.my.salesforce.com/services/data/v60.0/sobjects/Account" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"Name":"Existing Account"}' | jq '.[0].errorCode'
   ```

2. Test with a different API version to isolate the issue:
   ```bash
   curl -s -w "\n%{http_code}" "https://yourdomain.my.salesforce.com/services/data/v58.0/sobjects/Account" \
     -H "Authorization: Bearer $TOKEN" | tail -1
   ```

3. Check if duplicate rules are enabled:
   ```bash
   curl -s "https://yourdomain.my.salesforce.com/services/data/v60.0/limits" \
     -H "Authorization: Bearer $TOKEN" | jq '.DuplicateRule'
   ```

## Step-by-Step Fix

### 1. Use a Compatible API Version
```python
# BAD — using too old a version for the feature
url = f"{instance_url}/services/data/v20.0/sobjects/Account"

# GOOD — use the latest stable version
url = f"{instance_url}/services/data/v60.0/sobjects/Account"
resp = requests.post(url, headers=headers, json=payload)
```

### 2. Handle Duplicate Rules
```python
# BAD — creates duplicate that triggers rule
payload = {"Name": "Acme Corporation"}
resp = requests.post(url, headers=headers, json=payload)
# 409 if duplicate rule matches

# GOOD — use DuplicateRuleHeader to bypass or allow
headers_with_rule = headers.copy()
headers_with_rule["Sforce-Duplicate-Rule-Header"] = "allowSave=true"

resp = requests.post(url, headers=headers_with_rule, json=payload)
if resp.status_code == 409:
    print("Duplicate detected — check duplicate rules in Setup")
    # Query for existing duplicate
    query_resp = requests.get(
        f"{instance_url}/services/data/v60.0/query",
        headers=headers,
        params={"q": f"SELECT Id, Name FROM Account WHERE Name='Acme Corporation'"},
    )
    existing = query_resp.json().get("records", [])
    print(f"Existing record: {existing[0]['Id'] if existing else 'none'}")
```

### 3. Check Feature Availability Per Version
```python
# Check available API versions
resp = requests.get(f"{instance_url}/services/data/", headers=headers)
versions = [v["version"] for v in resp.json()]
print(f"Available versions: {versions}")

# Use the latest for new features, check release notes for version-specific changes
latest = versions[-1]
print(f"Using latest version: v{latest}")
```

## Prevention

- Always use the latest stable Salesforce API version for new integrations
- Test API calls across multiple versions to ensure compatibility
- Review Salesforce API release notes for breaking changes each season
- Use the `Sforce-Duplicate-Rule-Header` header to control duplicate rule behavior
- Query for existing records before inserting to avoid duplicate rule triggers

## Official Documentation

- [Salesforce REST API](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/)
- [Salesforce API Versioning](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/versioning.htm)
- [Salesforce Duplicate Rules](https://help.salesforce.com/s/articleView?id=sf.duplicate_rules_overview.htm)

## People Also Ask

- **What causes Salesforce API_VERSION_NOT_SUPPORTED?** Using a Salesforce API version that doesn't support the requested resource or feature. Use the latest stable version.
- **How do I bypass Salesforce duplicate rules via API?** Add the `Sforce-Duplicate-Rule-Header: allowSave=true` HTTP header to allow creation even if duplicates are detected.
- **What Salesforce API version should I use?** Use the latest available version for new integrations. Check `GET /services/data/` for the latest version in your org.
- **Can 409 be caused by concurrent updates?** Not typically — Salesforce uses 409 for version incompatibility and duplicate rules, not for concurrent modification conflicts.

## Related Errors

- [Salesforce 400 Bad Request](/salesforce/errors/400) — Invalid payload or field values
- [Salesforce 403 Forbidden](/salesforce/errors/403) — Request refused
- [Salesforce 414 URI Too Long](/salesforce/errors/414) — URL exceeds 16,384 bytes
