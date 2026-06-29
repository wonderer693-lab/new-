---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Zoho API INVALID_OAUTHTOKEN: Access token is invalid or expired"
description: "Fix Zoho API INVALID_OAUTHTOKEN error. Access token is invalid or expired. Refresh access token using refresh token."
tool: "zoho"
errorCode: "INVALID_OAUTHTOKEN"
errorName: "INVALID_OAUTHTOKEN"
httpStatus: 0
category: "unknown"
severity: "medium"
priority: 2
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "zoho api INVALID_OAUTHTOKEN error"
  - "zoho INVALID_OAUTHTOKEN fix"
  - "zoho api access token is invalid"
---

## What Causes Zoho INVALID_OAUTHTOKEN

Zoho returns `INVALID_OAUTHTOKEN` when the access token in the `Authorization` header is expired, revoked, or malformed. Zoho access tokens have a fixed 1-hour lifetime, after which they must be refreshed using the refresh token. The error also occurs if the refresh token itself has been revoked or if you've exceeded the maximum of 15 active access tokens per refresh token.

The response body shows `{"code":"INVALID_OAUTHTOKEN","message":"Access token is invalid or expired"}`. This is distinct from authentication errors at the token grant endpoint — `INVALID_OAUTHTOKEN` appears when hitting CRM API endpoints with a bad token.

### Common Scenarios
- Using an access token older than 1 hour without refreshing
- Refresh token was revoked (user uninstalled app or admin disabled access)
- More than 15 access tokens generated from the same refresh token without deleting old ones
- Token generated for one Zoho domain (e.g., `accounts.zoho.com`) used on another (e.g., `accounts.zoho.eu`)
- Token copied from dev environment to production without re-authorization

## How to Detect If You're Affected

1. Test the token directly against any CRM endpoint:
   ```bash
   curl -s "https://www.zohoapis.com/crm/v3/Leads" \
     -H "Authorization: Zoho-oauthtoken $TOKEN" | jq '.code'
   ```
   If `"INVALID_OAUTHTOKEN"`, the token is bad.

2. Check token expiry time (if you stored it):
   ```python
   from datetime import datetime
   age = datetime.now() - token_created_at
   print(f"Token age: {age}")
   if age.total_seconds() > 3300:  # 55 minutes
       print("Token is near expiry or expired")
   ```

3. Verify the refresh token is still valid by attempting a refresh:
   ```bash
   curl -s -X POST "https://accounts.zoho.com/oauth/v2/token" \
     -d "refresh_token=$REFRESH_TOKEN" \
     -d "client_id=$CLIENT_ID" \
     -d "client_secret=$CLIENT_SECRET" \
     -d "grant_type=refresh_token" | jq .
   ```
   If it returns `{"error":"invalid_code"}`, the refresh token is revoked.

## Step-by-Step Fix

### 1. Implement Automatic Token Refresh
```python
import requests
from datetime import datetime, timedelta

class ZohoAuth:
    def __init__(self, client_id, client_secret, refresh_token):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.access_token = None
        self.expires_at = datetime.now()

    def refresh(self):
        resp = requests.post("https://accounts.zoho.com/oauth/v2/token", data={
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
        })
        data = resp.json()
        self.access_token = data["access_token"]
        self.expires_at = datetime.now() + timedelta(seconds=3300)

    def get_headers(self):
        if datetime.now() > self.expires_at:
            self.refresh()
        return {"Authorization": f"Zoho-oauthtoken {self.access_token}"}
```

### 2. Handle Token Cleanup
If you've exceeded 15 active tokens, delete old ones:
```bash
# List active tokens (conceptual — Zoho doesn't expose a list API)
# Solution: stop creating new tokens on every request.
# Store and reuse the same access token for its full 55-minute lifetime.
```

### 3. Re-authorize If Refresh Token Is Dead
```python
# If refresh returns invalid_code, the user must re-authorize
if "invalid_code" in resp.text:
    print("Refresh token revoked — redirect user to OAuth flow:")
    auth_url = f"https://accounts.zoho.com/oauth/v2/auth?scope=ZohoCRM.modules.ALL&client_id={CLIENT_ID}&response_type=code&access_type=offline&redirect_uri={REDIRECT_URI}"
    # Send user to auth_url, exchange code for new tokens
```

## Prevention

- Store `created_at` timestamp alongside every access token and proactively refresh after 50 minutes (before the 60-minute expiry)
- Never generate a new access token until the current one is within 5 minutes of expiry — avoid creating more than 15 per refresh token
- Persist tokens to a database and lock access so concurrent processes don't each create separate tokens
- Use the same Zoho accounts domain consistently (e.g., `accounts.zoho.com` for global, `accounts.zoho.eu` for Europe)
- Implement a scheduled job that checks token expiry every 10 minutes and refreshes proactively

## Official Documentation

- [Zoho OAuth Overview](https://www.zoho.com/crm/developer/docs/api/v3/oauth-overview.html)
- [Zoho OAuth Token Refresh](https://www.zoho.com/crm/developer/docs/api/v3/refresh-token.html)
- [Zoho CRM API Authentication](https://www.zoho.com/crm/developer/docs/api/v3/authentication.html)

## People Also Ask

- **How long do Zoho access tokens last?** Zoho access tokens expire exactly 1 hour (3,600 seconds) after issuance. Refresh tokens do not expire unless revoked by the user or admin.
- **What is the 15-token limit?** Zoho allows a maximum of 15 active access tokens per refresh token. If you generate more, older tokens are silently invalidated but the INVALID_OAUTHTOKEN error appears when you try to use them.
- **How do I fix Zoho INVALID_OAUTHTOKEN?** Refresh the access token using `POST /oauth/v2/token` with `grant_type=refresh_token`. If the refresh token itself is invalid, the user must re-authorize the app through the OAuth flow.
- **Does Zoho INVALID_OAUTHTOKEN mean my refresh token is also expired?** Not necessarily. First try refreshing — if refresh succeeds, only the access token was stale. If refresh returns `invalid_code`, the refresh token has been revoked and re-authorization is required.

## Related Errors

- [Zoho Access Denied (OAuth throttle)](/zoho/errors/Access-Denied-OAuth-throttle) — Too many OAuth token requests
- [Zoho TOO_MANY_REQUESTS](/zoho/errors/TOO_MANY_REQUESTS) — Daily credit limit exceeded
- [Zoho LIMIT_EXCEEDED](/zoho/errors/LIMIT_EXCEEDED) — General API limit reached
