---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "ActiveCampaign API 404: Requested resource does not exist"
description: "Fix ActiveCampaign API 404 (404 Not Found) error. Requested resource does not exist. Check resource ID, verify the endpoint path, confirm account has the resource (list, tag, etc."
tool: "activecampaign"
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
  - "activecampaign api 404 error"
  - "activecampaign 404 fix"
  - "activecampaign api requested resource does not"
  - "activecampaign http 404"
---

## What Causes ActiveCampaign 404

ActiveCampaign returns HTTP 404 when the requested resource does not exist at the specified URL. This can happen when the resource ID is wrong, the endpoint path is incorrect, or the account doesn't have access to the resource (e.g., a deleted list or tag).

ActiveCampaign's REST API uses resource IDs in URL paths like `/api/3/contacts/{id}`. If the ID doesn't match any existing record, the API returns 404 with `{"errors":[{"title":"404 Not Found","detail":"Requested resource does not exist"}]}`.

### Common Scenarios
- Referencing a contact, deal, or list ID that was deleted from the system
- Using an ID from one ActiveCampaign account in a different account's API URL
- Mistyping the endpoint path (e.g., `/api/3/contact` instead of `/api/3/contacts`)
- Trying to access a list or tag that exists but is archived or in a different group

## How to Detect If You're Affected

1. Try listing resources to confirm the ID exists:
   ```bash
   # Test if the resource exists
   curl -s -w "\n%{http_code}" "https://{account}.api-us1.com/api/3/contacts/42" \
     -H "Api-Token: $TOKEN" | tail -1
   # 404 means contact 42 doesn't exist
   ```

2. List all resources of that type to find valid IDs:
   ```bash
   curl -s "https://{account}.api-us1.com/api/3/contacts" \
     -H "Api-Token: $TOKEN" | jq '.contacts[] | {id: .id, email: .email}'
   ```

3. Verify the endpoint path matches ActiveCampaign's documented routes:
   ```bash
   # BAD — wrong endpoint name
   curl -s "https://{account}.api-us1.com/api/3/contact" \
     -H "Api-Token: $TOKEN"
   
   # GOOD — correct endpoint name
   curl -s "https://{account}.api-us1.com/api/3/contacts" \
     -H "Api-Token: $TOKEN"
   ```

## Step-by-Step Fix

### 1. Validate Resource IDs Before Use
```python
import requests

headers = {"Api-Token": "YOUR_TOKEN"}
base_url = "https://{account}.api-us1.com/api/3"

def resource_exists(resource_type, resource_id):
    url = f"{base_url}/{resource_type}/{resource_id}"
    resp = requests.get(url, headers=headers)
    return resp.status_code == 200

# BAD — assuming ID exists
resp = requests.get(f"{base_url}/contacts/99999", headers=headers)
print(resp.status_code)  # 404

# GOOD — check first
if resource_exists("contacts", 42):
    resp = requests.get(f"{base_url}/contacts/42", headers=headers)
else:
    print("Contact 42 does not exist — check the ID")
```

### 2. Fetch Valid IDs from List Endpoints
```python
# Get all contacts and find valid IDs
resp = requests.get(f"{base_url}/contacts", headers=headers, params={"limit": 100})
data = resp.json()
valid_ids = [c["id"] for c in data.get("contacts", [])]
print(f"Valid contact IDs: {valid_ids}")

# Only use IDs from this list
if target_id in valid_ids:
    resp = requests.get(f"{base_url}/contacts/{target_id}", headers=headers)
```

### 3. Handle 404 Gracefully
```python
resp = requests.get(f"{base_url}/contacts/{contact_id}", headers=headers)
if resp.status_code == 404:
    # Re-fetch the contact list to get current IDs
    fresh = requests.get(f"{base_url}/contacts", headers=headers, params={"limit": 1})
    print("Contact not found — may have been deleted. Re-sync IDs.")
```

## Prevention

- Fetch and cache resource IDs periodically rather than hardcoding them
- Implement ID validation before making requests to individual resource endpoints
- Log 404 responses with the exact URL and ID for debugging
- Use the list endpoint first to confirm a resource exists before attempting to read/update it
- Add retry logic that re-fetches IDs if a 404 is received for a previously valid ID

## Official Documentation

- [ActiveCampaign API Overview](https://developers.activecampaign.com/reference/overview)
- [ActiveCampaign List Contacts](https://developers.activecampaign.com/reference/list-all-contacts)
- [ActiveCampaign Retrieve a Contact](https://developers.activecampaign.com/reference/retrieve-a-contact)

## People Also Ask

- **How do I find valid ActiveCampaign contact IDs?** Call `GET /api/3/contacts?limit=100` and extract IDs from the `contacts` array in the response.
- **Does ActiveCampaign return 404 for deleted resources?** Yes — once a contact, deal, list, or tag is deleted, the API returns 404 when trying to access it by ID.
- **Can I get 404 for a valid ID?** Not normally. If a valid ID returns 404, it may be archived or in a different scope (e.g., a list in a different group).
- **What's the difference between ActiveCampaign 404 and 422?** 404 means the resource doesn't exist. 422 means the resource path is valid but the request body has missing or invalid parameters.

## Related Errors

- [ActiveCampaign 422 Unprocessable Entity](/activecampaign/errors/422) — Missing or invalid parameters
- [ActiveCampaign 401 Unauthorized](/activecampaign/errors/401) — Invalid or missing API token
- [ActiveCampaign 403 Forbidden](/activecampaign/errors/403) — Authenticated but not authorized
