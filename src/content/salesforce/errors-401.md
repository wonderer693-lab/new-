---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Salesforce API 401: Session ID or OAuth token expired or invalid"
description: "Fix Salesforce API 401 (401 Unauthorized) error. Session ID or OAuth token expired or invalid. Re-authenticate."
tool: "salesforce"
errorCode: "401"
errorName: "401 Unauthorized"
httpStatus: 401
category: "authentication"
severity: "high"
priority: 1
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "salesforce api 401 error"
  - "salesforce 401 fix"
  - "salesforce api session id or oauth"
  - "salesforce http 401"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Your Salesforce session or OAuth token expired. Salesforce no longer trusts your login.

**The fix:**
1. Refresh your OAuth token using the refresh token you saved during login
2. If the refresh token is also expired, re-authenticate through the Salesforce login page
3. Make sure you're using the correct instance URL (not a hardcoded one like `na1.salesforce.com`)

**Copy-paste this code** (if you're using a code editor):
```python
import requests

resp = requests.post("https://login.salesforce.com/services/oauth2/token", data={
    "grant_type": "refresh_token",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "refresh_token": REFRESH_TOKEN,
})
access_token = resp.json()["access_token"]
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Start by asking your AI coding tool:

> I'm getting a 401 Unauthorized error from the Salesforce API.
> The error message is: "INVALID_SESSION_ID" — "Session expired or invalid"
> I'm using OAuth to authenticate with Salesforce.
> Please give me a step-by-step fix with working Python code that auto-refreshes the token when it expires.

The response should give you a token refresh function with auto-retry logic that detects 401 errors and refreshes the token automatically.

If that doesn't resolve it, send a second prompt:
> The fix didn't work. I'm still getting 401 errors after refreshing. Here's what I tried: [paste your code]. Please debug this.

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to fix Salesforce authentication errors in popular automation tools:

### Zapier
1. Open your Zap → click the Salesforce action step
2. Click "Reconnect" on the Salesforce account connection
3. Log in with your Salesforce credentials and re-authorize Zapier

### Make (Integromat)
1. Open your scenario → click the Salesforce module
2. Go to "Connection" → click "Reauthorize"
3. Log in with your Salesforce credentials and approve the connection

### n8n
1. Open your workflow → click the Salesforce node
2. In "Credentials" → click "Reconnect" or create a new credential
3. Complete the OAuth flow in the popup window

### Power Automate
1. Open your flow → click the Salesforce action
2. Click the three dots menu → "My connections" → click "Add new connection"
3. Sign in with your Salesforce credentials and authorize

**Which tool should you use?** Zapier handles Salesforce re-auth the easiest — one click to reconnect. All tools require you to log in again.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"401 Unauthorized"`
- `"INVALID_SESSION_ID"`
- `"Session expired or invalid"`
- `"Session expired"` in your integration logs

**What it means in plain English:** Your login to Salesforce timed out. It's like being logged out of a website — you need to log back in (or have your app do it automatically).

**Most common cause:** Session timeout (default 2 hours) or a password change that invalidated all active sessions.

</div>

## What Causes Salesforce 401

Salesforce returns HTTP 401 when the session ID or OAuth token used for authentication is invalid or expired. See all [Salesforce API errors](/salesforce/) in our complete reference. This is the most common Salesforce API error. The error code is typically `INVALID_SESSION_ID` with the message "Session expired or invalid".

A 401 can be caused by session timeout (default 2 hours, configurable down to 15 minutes), password expiry (invalidates all sessions including API-only sessions), MFA enforcement, instance URL hardcoding after org migration, or OAuth token revocation by an admin. The response body is `[{"message":"Session expired or invalid","errorCode":"INVALID_SESSION_ID"}]`.

### Common Scenarios
- Hardcoding the instance URL (e.g., `na1.salesforce.com`) when the org has been migrated to a different pod
- Session timeout after the org's configured timeout period with no API activity
- Password change for the integration user invalidating all active sessions
- MFA being enforced on the org, breaking non-interactive API sessions
- OAuth connected app being deauthorized by an administrator

## How to Detect If You're Affected

1. Check the response error code:
   ```bash
   curl -s "https://yourdomain.my.salesforce.com/services/data/v60.0/sobjects/Contact" \
     -H "Authorization: Bearer $TOKEN" | jq '.[0].errorCode'
   ```
   Returns `"INVALID_SESSION_ID"` if session is invalid.

2. Verify your instance URL matches your OAuth response:
   ```bash
   echo $INSTANCE_URL
   # Should match what OAuth returned — never hardcode na1/na2 etc.
   ```

3. Check session timeout settings (requires Salesforce admin access):
   ```bash
   # No API for this — check in Setup > Session Settings > Timeout Value
   ```

## Step-by-Step Fix

### 1. Refresh OAuth Token (Web Server Flow)
```python
import requests

def refresh_token(refresh_token, client_id, client_secret):
    resp = requests.post("https://login.salesforce.com/services/oauth2/token", data={
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
    })
    body = resp.json()
    return body["access_token"], body["instance_url"]

# Use when 401 detected
access_token, instance_url = refresh_token(
    refresh_token="your_refresh_token",
    client_id="your_client_id",
    client_secret="your_client_secret",
)
```

### 2. Use JWT Bearer Flow (No User Interaction)
```python
# JWT Bearer bypasses MFA and doesn't need refresh tokens
import jwt

def get_jwt_token(client_id, username, private_key_path):
    with open(private_key_path, "r") as f:
        private_key = f.read()
    now = int(time.time())
    payload = {
        "iss": client_id,
        "sub": username,
        "aud": "https://login.salesforce.com",
        "exp": now + 300,
    }
    assertion = jwt.encode(payload, private_key, algorithm="RS256")
    resp = requests.post("https://login.salesforce.com/services/oauth2/token", data={
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": assertion,
    })
    return resp.json()["access_token"], resp.json()["instance_url"]
```

### 3. Use Dynamic Instance URL
```python
# BAD — hardcoded instance URL
url = "https://na1.salesforce.com/services/data/v60.0/sobjects/Contact"

# GOOD — always from OAuth response
instance_url = oauth_response["instance_url"]  # e.g., https://yourdomain.my.salesforce.com
url = f"{instance_url}/services/data/v60.0/sobjects/Contact"
```

## Prevention

- Use OAuth 2.0 JWT Bearer flow for server-to-server integrations (no MFA issues, no refresh needed)
- Never hardcode instance URLs — always extract from the OAuth token response
- Create a dedicated integration user with API-only access and no password expiry
- Implement auto-refresh: detect INVALID_SESSION_ID → refresh token → retry the request
- Store tokens in memory only, refresh from the refresh token before expiry
- Similar auth issues occur with [HubSpot 401](/hubspot/errors/401), [Slack invalid_auth](/slack/errors/invalid_auth), and [Zoho INVALID_OAUTHTOKEN](/zoho/errors/invalid-oauthtoken).
- This error also affects integrations. See our [Salesforce to Mailchimp](/integrations/salesforce-to-mailchimp/) and [Salesforce to ActiveCampaign](/integrations/salesforce-to-activecampaign/) integration error guides.

## Official Documentation

- [Salesforce REST API](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/)
- [Salesforce OAuth Token Endpoint](https://help.salesforce.com/s/articleView?id=sf.remoteaccess_oauth_web_server_flow.htm)
- [Salesforce JWT Bearer Flow](https://help.salesforce.com/s/articleView?id=sf.remoteaccess_oauth_jwt_flow.htm)
- [Salesforce Identity Endpoint](https://help.salesforce.com/s/articleView?id=sf.remoteaccess_using_openid_connect.htm)

## People Also Ask

- **How long do Salesforce API sessions last?** Configurable in Setup > Session Settings. Default is 2 hours, minimum 15 minutes, maximum 8 hours. "Timeout Value" can reset on activity.
- **What's the difference between OAuth and JWT Bearer flow?** OAuth Authorization Code flow requires user interaction and can be blocked by MFA. JWT Bearer is server-to-server, no user interaction, and bypasses MFA.
- **Can INVALID_SESSION_ID mean my IP is blocked?** Yes — if the org has "Trusted IP Ranges" configured and your API call originates outside those ranges, the session will be invalidated.
- **Does password expiry affect API access?** Yes — when a user's password expires, all sessions for that user are invalidated, including API-only sessions. Use a dedicated integration user with no password expiry.

## Related Errors

- [Salesforce INVALID_SESSION_ID](/salesforce/errors/INVALID_SESSION_ID) — Detailed session management guide
- [Salesforce 403 Forbidden](/salesforce/errors/403) — Request refused
- [Salesforce 429 REQUEST_LIMIT_EXCEEDED](/salesforce/errors/429) — Rate limit exceeded
