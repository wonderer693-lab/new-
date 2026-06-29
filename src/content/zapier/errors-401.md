---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Zapier API 401: Invalid or expired access token"
description: "Fix Zapier API 401 error. Invalid or expired access token. Refresh token via /oauth/token."
tool: "zapier"
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
  - "zapier api 401 error"
  - "zapier 401 fix"
  - "zapier api invalid or expired access"
  - "zapier http 401"
---

## What Causes Zapier 401

Zapier returns HTTP 401 when the access token in the `Authorization` header is invalid, expired, or missing. Zapier access tokens expire after 10 hours and use rotating refresh tokens — each time you refresh, a new refresh token is returned (the old one is invalidated). This rotating behavior means you must store the latest refresh token after every refresh.

The response contains `{"status":"error","message":"Invalid or expired access token"}`. Common causes include using an expired token, using a token generated for a different environment, or failing to persist a new refresh token after rotation.

### Common Scenarios
- Using an access token beyond its 10-hour expiry window
- Refresh token rotation not handled — old refresh token used after a refresh invalidated it
- Token copied from dev environment to production without re-authorization
- API key disabled or deleted from the Zapier developer dashboard
- Incorrect `Authorization` header format (wrong scheme or missing "Bearer" prefix)

## How to Detect If You're Affected

1. Check the response status and body:
   ```bash
   curl -s -w "\n%{http_code}" "https://api.zapier.com/v2/..." \
     -H "Authorization: Bearer $TOKEN" | tail -1
   ```
   If the output is `401`, the token is rejected.

2. Test token validity via Zapier's check endpoint:
   ```bash
   curl -s "https://api.zapier.com/v2/check" \
     -H "Authorization: Bearer $TOKEN" | jq .
   ```

## Step-by-Step Fix

### 1. Refresh the Token
```python
import requests

def refresh_zapier_token(refresh_token, client_id, client_secret):
    resp = requests.post("https://api.zapier.com/oauth/v2/token", data={
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
    })
    data = resp.json()
    # IMPORTANT: Zapier uses rotating refresh tokens
    new_access_token = data["access_token"]
    new_refresh_token = data["refresh_token"]  # Save this!
    return new_access_token, new_refresh_token
```

### 2. Store the Rotated Refresh Token
```python
# BAD — overwrite with same value
refresh_token = old_refresh_token

# GOOD — persist the new one every time
current_refresh_token = persist_token(data["refresh_token"])
# Save to database, environment variable, or secure store
```

### 3. Implement Auto-Refresh on 401
```python
def call_with_auto_refresh(url, headers):
    resp = requests.get(url, headers=headers)
    if resp.status_code == 401:
        new_token, new_refresh = refresh_zapier_token(
            stored_refresh, CLIENT_ID, CLIENT_SECRET
        )
        stored_refresh = new_refresh  # Persist this
        headers["Authorization"] = f"Bearer {new_token}"
        resp = requests.get(url, headers=headers)
    return resp
```

## Prevention

- Persist the new `refresh_token` from every refresh response — the old one becomes invalid immediately
- Set up a token refresh schedule (every 9 hours, well before the 10-hour expiry)
- Implement automatic 401 detection: catch 401 → refresh token → retry original request
- Validate token format before sending: it should start with a specific prefix and not contain whitespace
- Use environment variables or a secrets manager — never hardcode tokens in source code

## Official Documentation

- [Zapier Platform API](https://platform.zapier.com/)
- [Zapier API Authentication](https://platform.zapier.com/docs/auth)
- [Zapier OAuth Documentation](https://platform.zapier.com/docs/oauth)

## People Also Ask

- **How long do Zapier access tokens last?** Zapier access tokens expire after 10 hours. Refresh tokens use rotation — each refresh returns a new refresh token and invalidates the old one.
- **What does rotating refresh token mean?** Each time you call the token refresh endpoint, Zapier returns a new refresh token and invalidates the previous one. You must persist the new refresh token every time or your next refresh will fail.
- **Why does Zapier use rotating refresh tokens?** Rotation improves security — if a refresh token is compromised, it's only valid for a single refresh cycle. The attacker needs to intercept the rotated token to maintain access.
- **How do I fix Zapier 401?** Refresh the access token using `POST /oauth/v2/token` with `grant_type=refresh_token`. If the refresh token was already rotated, use the latest refresh token you received.

## Related Errors

- [Zapier 429 Rate Limit](/zapier/errors/429) — Rate limit exceeded
- [Zapier 500 Server Error](/zapier/errors/500) — Server error
- [Zapier 400 Bad Request](/zapier/errors/400) — Malformed request
