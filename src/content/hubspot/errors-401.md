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

## What Causes HubSpot 401

HubSpot API 401 means your request lacks valid authentication. Common causes:

- OAuth access token expired (default 6h, configurable 1-6h since March 2026)

- Refresh token expired or revoked (user disconnected app)

- Private app token revoked or deleted

- API key auth used (deprecated, removed in some regions)

- Token sent in wrong header or format



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