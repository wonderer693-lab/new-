---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "ActiveCampaign API 403: Authentication failed or user not authorized for resource"
description: "Fix ActiveCampaign API 403 (403 Forbidden) error. Authentication failed or user not authorized for resource. Ensure API key is valid and user has appropriate permissions."
tool: "activecampaign"
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
  - "activecampaign api 403 error"
  - "activecampaign 403 fix"
  - "activecampaign api authentication failed or user"
  - "activecampaign http 403"
---

## What Causes ActiveCampaign 403

ActiveCampaign returns HTTP 403 when the API token is valid but the authenticated user does not have permission to access the requested resource. This is a permissions error, distinct from 401 (invalid token). ActiveCampaign uses user-level permissions — each user's API key inherits the permissions assigned to that user in the account.

The response typically contains `{"errors":[{"title":"403 Forbidden","detail":"Authentication failed or user not authorized for resource"}]}`. The 403 applies to specific endpoints: a user might have access to contacts but not to deals, or read-only access but attempting a write operation.

### Common Scenarios
- User account has "View" permission on contacts but the integration tries to create or update
- API user was removed from a team that had access to specific lists or campaigns
- Integration user was created with limited permissions and tries to access a restricted module
- Trying to access a custom object or feature not included in the user's plan

## How to Detect If You're Affected

1. Identify which specific endpoints return 403:
   ```bash
   curl -s -w "\n%{http_code}" "https://{account}.api-us1.com/api/3/contacts" \
     -H "Api-Token: $TOKEN" | tail -1
   curl -s -w "\n%{http_code}" "https://{account}.api-us1.com/api/3/deals" \
     -H "Api-Token: $TOKEN" | tail -1
   ```
   Compare which endpoints succeed (200) vs fail (403).

2. Check the error detail:
   ```bash
   curl -s "https://{account}.api-us1.com/api/3/deals" \
     -H "Api-Token: $TOKEN" | jq '.errors[0].title'
   ```

3. Go to ActiveCampaign Settings > Users > [User] > Permissions to verify assigned permissions.

## Step-by-Step Fix

### 1. Identify Missing Permissions
```python
import requests

headers = {"Api-Token": "YOUR_TOKEN"}
base_url = "https://{account}.api-us1.com/api/3"

# Test multiple endpoints to identify which modules are blocked
endpoints = ["contacts", "deals", "lists", "campaigns", "tags"]
for ep in endpoints:
    resp = requests.get(f"{base_url}/{ep}", headers=headers)
    status = resp.status_code
    if status == 403:
        print(f"403 on /{ep} — missing permissions for this module")
```

### 2. Update User Permissions
```python
# No API to change permissions — must use web UI
print("1. Go to Settings > Users in ActiveCampaign")
print("2. Select the API user")
print("3. Go to Permissions tab")
print("4. Enable access to the required modules (at minimum: Contacts)")
print("5. Save changes")
```

### 3. Use a Different API User
```bash
# If permissions cannot be changed, switch to a user with full access
# Generate a new API token from a user with admin permissions
curl -s "https://{account}.api-us1.com/api/3/contacts" \
  -H "Api-Token: $ADMIN_TOKEN" \
  | jq '.contacts | length'
```

## Prevention

- Create a dedicated API integration user with explicitly assigned permissions
- Assign the minimum permissions needed (least privilege principle)
- Document which API endpoints each integration uses and map them to user permissions
- Test all API operations after any user permission changes
- Use ActiveCampaign's "Admin" user for integrations that need full access

## Official Documentation

- [ActiveCampaign API Overview](https://developers.activecampaign.com/reference/overview)
- [ActiveCampaign User Permissions](https://help.activecampaign.com/hc/en-us/articles/115000983230-User-permissions)
- [ActiveCampaign Authentication](https://developers.activecampaign.com/reference/authentication)

## People Also Ask

- **What's the difference between ActiveCampaign 401 and 403?** 401 means the API token is missing or invalid. 403 means the token is valid but the user doesn't have permission for that specific resource.
- **How do I give API access to a user?** Go to Settings > Users, select the user, go to Permissions, and enable access to each module the integration needs.
- **Can I have an admin-only API key?** Yes — generate the API token from an admin user account. That key will have full access to all modules.
- **Why does one endpoint return 403 while others work?** The API user likely has partial permissions — access to some modules but not others. Check the user's permission settings.

## Related Errors

- [ActiveCampaign 401 Unauthorized](/activecampaign/errors/401) — Invalid or missing API token
- [ActiveCampaign 404 Not Found](/activecampaign/errors/404) — Resource does not exist
- [ActiveCampaign 429 Rate Limit](/activecampaign/errors/429) — Too many requests
