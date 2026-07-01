---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "HubSpot API 401 Unauthorized — OAuth Token Expired? Fix & Prevention"
description: "Fix HubSpot API 401 Unauthorized errors. OAuth token refresh, private app token rotation, and 2026 configurable token TTL changes."
tool: "hubspot"
errorCode: "401"
errorName: "Unauthorized"
httpStatus: 401
category: "authentication"
severity: "high"
priority: 2
lastUpdated: "2026-04-09"
keywords:
  - "hubspot api 401 unauthorized"
  - "hubspot oauth token expired"
  - "hubspot api authentication error"
  - "hubspot 401 fix"
  - "hubspot oauth refresh token"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Your HubSpot API key or OAuth token is expired or wrong.

**The fix:**
1. Check if your OAuth token has expired (they last 6 hours by default)
2. Refresh your token using the refresh token — or re-connect your app
3. If using a private app token, check if it was revoked in HubSpot settings

**Copy-paste this code** (if you're using a code editor):
```python
import requests

resp = requests.post("https://api.hubapi.com/oauth/v1/token", data={
    "grant_type": "refresh_token",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "refresh_token": REFRESH_TOKEN,
})
new_token = resp.json()["access_token"]
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Paste this into ChatGPT, Claude, Cursor, or Gemini:

> I'm getting a 401 Unauthorized error from the HubSpot API.
> The error message says "Invalid API key" and "authentication failed."
> I'm using OAuth tokens with a refresh token flow.
> Please give me code that detects expired tokens, refreshes them automatically, and retries the original request.

You should get back a token refresh function with automatic retry logic that handles expired access tokens gracefully.

If the first fix doesn't work, follow up with:
> The fix didn't work. My refresh token might also be invalid. How do I re-authorize the OAuth flow from scratch?

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to handle HubSpot 401 authentication errors in popular automation tools:

### Zapier
1. Open your Zap → click the HubSpot action step
2. Click "Reconnect" next to your HubSpot account — this refreshes the OAuth token
3. If reconnection fails, go to Zapier Settings → Connected Accounts → HubSpot → Disconnect, then reconnect from scratch

### Make (Integromat)
1. Open your scenario → click the HubSpot module
2. Click the connection dropdown → "Reauthorize" to refresh the OAuth token
3. If that fails, go to Make Settings → Connections → HubSpot → Delete, then create a new connection with fresh credentials

### n8n
1. Open your workflow → click the HubSpot node
2. In the "Credentials" section → click "Reconnect" to refresh the OAuth token
3. If using API key auth, generate a new private app token in HubSpot Settings → Integrations → Private Apps, then update the credential in n8n

### Power Automate
1. Open your flow → click the HubSpot action
2. Click the three dots menu → "My connections" → sign in again to refresh the token
3. If that fails, go to Power Automate Settings → Data → Connections → HubSpot → Edit connection, and re-authenticate

**Which tool should you use?** Zapier has the simplest re-auth flow — just click "Reconnect" and you're done in one click.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"401 Unauthorized"`
- `"Invalid API key"`
- `"authentication failed"`
- `"Authentication token not found"` in your integration logs

**What it means in plain English:** HubSpot doesn't recognize who you are. Your access token expired, was revoked, or was never set up correctly. You need to log in again or get a fresh token.

**Most common cause:** OAuth access tokens expire after 6 hours. If your integration doesn't refresh them automatically, it will start failing with 401 errors.

</div>

## What Causes HubSpot 401

HubSpot API 401 means your request lacks valid authentication. Common causes:

- OAuth access token expired (default 6h, configurable 1-6h since March 2026)

- Refresh token expired or revoked (user disconnected app)

- Private app token revoked or deleted

- API key auth used (deprecated, removed in some regions)

- Token sent in wrong header or format

See all [HubSpot API errors](/hubspot/) in our complete reference. Similar auth issues occur with [Salesforce 401](/salesforce/errors/401), [Slack invalid_auth](/slack/errors/invalid_auth), and [Make 401](/make/errors/401).

This error also affects integrations. See our [HubSpot to Slack integration errors](/integrations/hubspot-to-slack/) for common cross-tool issues.

## Step-by-Step Fix



### 1. Check Token Expiry

```python

import requests



# Test with current token

headers = {'Authorization': f'Bearer {token}'}

resp = requests.get('https://api.hubapi.com/crm/v3/objects/contacts', headers=headers)



if resp.status_code == 401:

    # Token expired — refresh

    refresh_resp = requests.post('https://api.hubapi.com/oauth/v1/token', data={

        'grant_type': 'refresh_token',

        'client_id': client_id,

        'client_secret': client_secret,

        'refresh_token': refresh_token

    })

    new_token = refresh_resp.json()['access_token']

```



### 2. Verify Refresh Token

- User may have disconnected your app from HubSpot Settings > Integrations

- Refresh token lifetime: 6 months (no activity) or until revoked

- Re-authorize: send user through OAuth flow again



### 3. Private App Token

- Check if token exists in HubSpot Settings > Integrations > Private Apps

- Generate new token, update your integration

- Max 10 private app tokens per account



## 2026 Changes

- OAuth token TTL now configurable: 1-6 hours (was fixed 6h)

- Shorter TTL = more frequent refreshes = more 401 risk if refresh logic fails

- Longer TTL = longer window if token compromised



## How to Detect If You're Affected

1. Check the response body — HubSpot returns `{"status":"error","message":"Authentication token not found","category":"INVALID_AUTHENTICATION"}`.
2. Inspect your token's issued-at timestamp and compare to current time:
   ```python
   import time
   age = time.time() - token_issued_at
   print(f"Token age: {age}s — {'EXPIRED' if age > 21600 else 'OK'}")
   ```
3. Verify the refresh token is still valid by attempting a refresh:
   ```bash
   curl -s -X POST https://api.hubapi.com/oauth/v1/token \
     -d "grant_type=refresh_token&client_id=$ID&client_secret=$SECRET&refresh_token=$TOKEN" | jq .
   ```
   If it returns `{"status":"error","message":"refresh_token is invalid"}`, the user revoked access.
4. Check HubSpot Settings > Integrations > Connected Apps to see if your app is still authorized.

## Prevention

- Implement OAuth token refresh with retry (401 → refresh → retry original request)

- Monitor token expiry and proactively refresh before expiry

- Log authentication failures with token ID to identify revoked tokens

- Use private app tokens for server-to-server integrations (no OAuth flow needed)
- Similar auth issues occur with [Salesforce 401](/salesforce/errors/401), [Slack invalid_auth](/slack/errors/invalid_auth), and [Make 401](/make/errors/401).



## People Also Ask

- **Why does HubSpot return 401 Unauthorized?** The most common cause is an expired OAuth access token (default 6-hour lifetime). Refresh it using the refresh token via `POST /oauth/v1/token` with `grant_type=refresh_token`.
- **How long do HubSpot OAuth access tokens last?** Default is 6 hours, but since March 2026 the TTL is configurable between 1-6 hours. Refresh tokens last 6 months with no activity or until revoked.
- **What's the difference between HubSpot private app tokens and OAuth?** Private app tokens are static, single-account, and don't expire. OAuth tokens are multi-account, short-lived, and require refresh logic. Use private apps for server-to-server integrations.
- **Can HubSpot 401 mean my API key is wrong?** Yes — if you're using the deprecated `hapikey` query parameter, it may have been removed in your region. Switch to OAuth or private app tokens.

## Official Documentation

- [HubSpot API Overview](https://developers.hubspot.com/docs/api/overview)
- [HubSpot OAuth Guide](https://developers.hubspot.com/docs/api/oauth-quickstart-guide)
- [HubSpot Rate Limits](https://developers.hubspot.com/docs/api/usage-details)

## Related Errors

- [HubSpot 429 Rate Limit](/hubspot/errors/429)
- [Salesforce INVALID_SESSION_ID](/salesforce/errors/INVALID_SESSION_ID)
- [ActiveCampaign ContactTag 400](/activecampaign/errors/400)