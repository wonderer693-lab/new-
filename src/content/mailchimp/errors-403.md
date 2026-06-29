---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Mailchimp API 403: User role lacks permission for the action or API access d..."
description: "Fix Mailchimp API 403 (403 Forbidden) error. User role lacks permission for the action or API access disabled. Use an admin-level user for API operations."
tool: "mailchimp"
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
  - "mailchimp api 403 error"
  - "mailchimp 403 fix"
  - "mailchimp api user role lacks permission"
  - "mailchimp http 403"
---

## What Causes Mailchimp 403

Mailchimp returns HTTP 403 when the API key's associated user account lacks permission for the requested operation, or when API access has been disabled for the account. Mailchimp restricts API access based on user roles — Manager and Read Only roles have limited API access, while Admin role has full access.

The response is `{"type":"https://mailchimp.com/developer/marketing/docs/errors/","title":"Forbidden","status":403,"detail":"User role lacks permission"}`. API access can also be disabled entirely for an account from the Mailchimp admin panel under Extras > API keys.

### Common Scenarios
- API key was created by a user with "Manager" role — they can't access all endpoints
- "Read Only" user trying to create or update resources via API
- API access was disabled for the account in Mailchimp settings
- Account has a restriction based on the Mailchimp plan (e.g., some endpoints require paid plans)
- Two-factor authentication requirement blocking API access for that user

## How to Detect If You're Affected

1. Check the response detail:
   ```bash
   curl -s "https://usX.api.mailchimp.com/3.0/" \
     -H "Authorization: apikey $API_KEY" | jq '.detail'
   ```

2. Check your account role via the root endpoint:
   ```bash
   curl -s "https://usX.api.mailchimp.com/3.0/" \
     -H "Authorization: apikey $API_KEY" | jq '.account_role'
   ```

## Step-by-Step Fix

### 1. Check Account Role
```python
resp = requests.get("https://usX.api.mailchimp.com/3.0/", headers=headers)
account = resp.json()
role = account.get("account_role")
print(f"Account role: {role}")
# Admin or Owner have full API access
# Manager has limited access
# Read-only cannot write
```

### 2. Use Admin-Level API Key
```python
# BAD — using Manager's API key
manager_key = "abc123-usX"
headers = {"Authorization": f"apikey {manager_key}"}
resp = requests.post("https://usX.api.mailchimp.com/3.0/lists/{id}/members",
    headers=headers, json=payload)
print(resp.status_code)  # 403

# GOOD — use Admin's API key
admin_key = "def456-usX"
headers = {"Authorization": f"apikey {admin_key}"}
resp = requests.post("https://usX.api.mailchimp.com/3.0/lists/{id}/members",
    headers=headers, json=payload)
print(resp.status_code)  # 200
```

### 3. Verify API Access Is Enabled
In Mailchimp web UI: Profile > Extras > API keys > ensure API access is enabled for the account. If disabled, toggle it on.

## Prevention

- Generate API keys under an Admin or Owner account, not a Manager or Read-only account
- Document which role is required for each API operation in your integration guide
- Add a startup check — call `GET /3.0/` and verify `account_role` is "Admin" or "Owner"
- Create a dedicated Mailchimp user with Admin role purely for API integration purposes
- Monitor for 403 errors and alert immediately — they often indicate account configuration drift

## Official Documentation

- [Mailchimp API Overview](https://mailchimp.com/developer/marketing/api/)
- [Mailchimp User Roles](https://mailchimp.com/help/account-roles-and-permissions/)
- [Mailchimp API Key Setup](https://mailchimp.com/help/about-api-keys/)

## People Also Ask

- **Why does Mailchimp return 403?** The API key's user role lacks permission for the endpoint. Admin/Owner roles have full access; Manager and Read-only roles are restricted.
- **How do I check my Mailchimp account role?** Call `GET /3.0/` and inspect the `account_role` field in the response — it returns "Owner", "Admin", "Manager", or "Read Only".
- **Can I fix Mailchimp 403 by changing permissions?** No — permissions are tied to the Mailchimp user role, which is set in the web UI. Generate the API key under an Admin-level user instead.
- **Does Mailchimp 403 mean my API key is expired?** No — API keys don't expire. A 403 means the key is valid but the associated user lacks the required permissions.

## Related Errors

- [Mailchimp 401 Unauthorized](/mailchimp/errors/401) — Invalid or missing API token
- [Mailchimp 404 Not Found](/mailchimp/errors/404) — Resource does not exist
- [Mailchimp 400 Bad Request](/mailchimp/errors/400) — Malformed request or validation error
