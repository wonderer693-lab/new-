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

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Your Zoho OAuth token expired or is invalid. Zoho tokens only last 1 hour, and yours ran out.

**The fix:**
1. Use your refresh token to get a new access token
2. Store the new token and use it for future requests
3. Refresh tokens automatically before they expire (every 50 minutes)

**Copy-paste this code** (if you're using a code editor):
```python
import requests

resp = requests.post("https://accounts.zoho.com/oauth/v2/token", data={
    "refresh_token": REFRESH_TOKEN,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "grant_type": "refresh_token",
})
new_token = resp.json()["access_token"]
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm getting an "INVALID_OAUTHTOKEN" error from the Zoho CRM API.
> The error message is: "Access token is invalid or expired"
> I have a refresh token but I'm not sure how to use it to get a new access token.
> Please give me a step-by-step fix with working Python code that auto-refreshes the token before it expires.

**What to expect:** The AI should give you a token manager class that tracks expiry and refreshes automatically, so you never hit this error again.

**If it doesn't work**, add this follow-up:
> The fix didn't work. My refresh token also seems invalid. Here's what I tried: [paste your code]. Please help me re-authorize.

**Best AI tools for this:** Claude (best at explaining OAuth flows), ChatGPT-4 (good code generation), Cursor (if you want inline code fixes)

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to handle Zoho OAuth token errors in popular automation tools:

### Zapier
1. Open your Zap → click the Zoho CRM connection in "Accounts"
2. Click "Reconnect" to refresh the OAuth token — Zapier handles the refresh automatically
3. If reconnection fails, disconnect and re-authorize the Zoho account from scratch

### Make (Integromat)
1. Open your scenario → go to "Connections" → find your Zoho connection
2. Click "Reauthorize" to refresh the OAuth token
3. If that fails, delete the connection and create a new one by going through the Zoho OAuth flow again

### n8n
1. Open your workflow → click the Zoho CRM node → go to "Credentials"
2. Click "Reconnect" to refresh the OAuth token
3. If the refresh token is revoked, delete the credential and create a new one with fresh OAuth authorization

### Power Automate
1. Open your flow → click the Zoho connection reference
2. Go to "Data" → "Connections" → find Zoho → click "Fix connection"
3. Re-authenticate with your Zoho account to get fresh tokens

**Which tool should you use?** Zapier handles Zoho token refresh automatically — just reconnect and it takes care of the rest.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"INVALID_OAUTHTOKEN"` in the API response
- `"Access token is invalid or expired"`
- `"token expired"` in your integration logs
- HTTP 200 response with `"code":"INVALID_OAUTHTOKEN"` (Zoho returns 200 even for errors)

**What it means in plain English:** Your Zoho access token ran out of time. Zoho tokens only last 1 hour. You need to get a fresh one using your refresh token.

**Most common cause:** Using the same access token for more than 1 hour without refreshing it, or copying a token from one environment to another.

</div>

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

- [Zoho Access Denied (OAuth throttle)](/zoho/errors/access-denied-oauth-throttle) — Too many OAuth token requests
- [Zoho TOO_MANY_REQUESTS](/zoho/errors/TOO_MANY_REQUESTS) — Daily credit limit exceeded
- [Zoho LIMIT_EXCEEDED](/zoho/errors/LIMIT_EXCEEDED) — General API limit reached
