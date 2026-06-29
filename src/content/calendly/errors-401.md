---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Calendly API 401: Invalid or missing token"
description: "Fix Calendly API 401 error. Invalid or missing token. Verify token is valid."
tool: "calendly"
errorCode: "401"
errorName: "401"
httpStatus: 401
category: "authentication"
severity: "high"
priority: 1
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "calendly api 401 error"
  - "calendly 401 fix"
  - "calendly api invalid or missing token"
  - "calendly http 401"
---

## What Causes Calendly 401

Calendly returns HTTP 401 when the request is missing a valid authorization token or the token has expired. Calendly supports two authentication methods: Personal Access Tokens (long-lived, managed in developer settings) and OAuth 2.0 Bearer tokens (short-lived, 2-hour expiry, requires refresh).

The response contains `{"message":"Unauthorized","errors":[{"message":"Invalid or missing token"}]}`. Personal Access Tokens never expire but can be revoked. OAuth tokens expire after 2 hours and require a refresh token flow to obtain a new one. A 401 always means the API doesn't recognize the token as valid.

### Common Scenarios
- Using an expired OAuth access token without refreshing it first
- Forgetting to include the `Authorization: Bearer` header in the request
- Personal Access Token was revoked in Calendly developer settings
- Using the wrong token type (e.g., OAuth token on a Personal Access Token endpoint)

## How to Detect If You're Affected

1. Test with a simple authenticated request:
   ```bash
   curl -s -w "\n%{http_code}" "https://api.calendly.com/users/me" \
     -H "Authorization: Bearer $TOKEN" | tail -1
   ```
   Returns 401 if token is invalid.

2. Check the response body:
   ```bash
   curl -s "https://api.calendly.com/users/me" \
     -H "Authorization: Bearer $TOKEN" | jq '.'
   ```

3. For OAuth, check if the token has expired by decoding it:
   ```bash
   # JWT tokens have an exp claim — decode the payload
   echo $TOKEN | cut -d'.' -f2 | base64 --decode 2>/dev/null | jq '.exp'
   ```

## Step-by-Step Fix

### 1. Refresh OAuth Token
```python
import requests

# BAD — using expired OAuth token
headers = {"Authorization": "Bearer expired_token"}
resp = requests.get("https://api.calendly.com/users/me", headers=headers)
print(resp.status_code)  # 401

# GOOD — refresh using the refresh token
refresh_resp = requests.post("https://auth.calendly.com/oauth/token", data={
    "grant_type": "refresh_token",
    "refresh_token": "your_refresh_token",
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
})
new_token = refresh_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {new_token}"}
resp = requests.get("https://api.calendly.com/users/me", headers=headers)
print(resp.status_code)  # 200
```

### 2. Use Personal Access Token Instead
```python
# Personal Access Tokens don't expire — create one in Calendly settings
# Go to https://calendly.com/integrations/api_webhooks

headers = {"Authorization": "Bearer your_personal_access_token"}
resp = requests.get("https://api.calendly.com/users/me", headers=headers)
```

### 3. Implement Auto-Refresh Logic
```python
def calendly_authenticated_request(url, headers, refresh_token, client_id, client_secret):
    resp = requests.get(url, headers=headers)
    if resp.status_code == 401:
        # Token expired — refresh it
        refresh_resp = requests.post("https://auth.calendly.com/oauth/token", data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        })
        new_token = refresh_resp.json()["access_token"]
        headers["Authorization"] = f"Bearer {new_token}"
        resp = requests.get(url, headers=headers)
    return resp
```

## Prevention

- Use Personal Access Tokens for server-to-server integrations (they don't expire)
- Store the refresh token securely alongside the access token for OAuth flows
- Implement automatic token refresh when 401 is detected (don't fail — refresh and retry)
- Monitor token age and refresh proactively before the 2-hour OAuth expiry
- Keep tokens in environment variables, not in source code

## Official Documentation

- [Calendly API Authentication](https://developer.calendly.com/api-docs/basics/authentication)
- [Calendly OAuth 2.0](https://developer.calendly.com/api-docs/basics/oauth)
- [Calendly Personal Access Tokens](https://developer.calendly.com/api-docs/basics/authentication#personal-access-tokens)

## People Also Ask

- **How long do Calendly OAuth tokens last?** OAuth access tokens expire after 2 hours. Use the refresh token to get a new one without user interaction.
- **Do Calendly Personal Access Tokens expire?** No — Personal Access Tokens are long-lived and only expire if you manually revoke them in settings.
- **How do I create a Calendly Personal Access Token?** Go to https://calendly.com/integrations/api_webhooks and click "Generate New Token" under Personal Access Tokens.
- **What's the difference between Calendly 401 and 403?** 401 means the token is missing or invalid. 403 means the token is valid but the user doesn't have permission for that specific resource.

## Related Errors

- [Calendly 403 Forbidden](/calendly/errors/403) — Insufficient permissions
- [Calendly 404 Not Found](/calendly/errors/404) — Resource not found
- [Calendly 429 Rate Limit](/calendly/errors/429) — Too many requests
