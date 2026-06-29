---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Pipedrive API 401: Invalid API token or OAuth access token"
description: "Fix Pipedrive API 401 (401 Unauthorized) error. Invalid API token or OAuth access token. Verify api_token query parameter or OAuth Bearer token."
tool: "pipedrive"
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
  - "pipedrive api 401 error"
  - "pipedrive 401 fix"
  - "pipedrive api invalid api token or"
  - "pipedrive http 401"
---

## What Causes Pipedrive 401

Pipedrive returns HTTP 401 when the API token or OAuth access token is missing, invalid, or expired. Pipedrive supports two authentication methods: (1) API token as a query parameter (`?api_token=...`) for v1, and (2) OAuth Bearer token in the `Authorization` header for v2. Using the wrong method for the API version results in 401.

The response is `{"error":"Invalid API token or OAuth access token"}`. API tokens come from the Pipedrive web UI (Settings > API > Your token) and don't expire. OAuth access tokens expire after a set period and must be refreshed.

### Common Scenarios
- API token passed in wrong location — header instead of query param (v1)
- OAuth token used as `api_token` query parameter instead of Bearer header (v2)
- OAuth access token expired — default lifetime is 1 hour
- API token copied with extra whitespace or truncated characters
- Using an API token from a development account against a production account

## How to Detect If You're Affected

1. Test v1 authentication:
   ```bash
   curl -s -w "\n%{http_code}" "https://api.pipedrive.com/v1/deals?api_token=$TOKEN" | tail -1
   ```

2. Test v2 authentication:
   ```bash
   curl -s -w "\n%{http_code}" "https://api.pipedrive.com/v2/deals" \
     -H "Authorization: Bearer $TOKEN" | tail -1
   ```

## Step-by-Step Fix

### 1. Use Correct Auth Method for API Version
```python
# BAD — mixing v1 and v2 auth
# v1 token in Bearer header:
headers = {"Authorization": f"Bearer {token}"}
resp = requests.get("https://api.pipedrive.com/v1/deals", headers=headers)  # 401

# BAD — v2 token in query param:
resp = requests.get(f"https://api.pipedrive.com/v2/deals?api_token={token}")  # 401

# GOOD — match auth to version
# v1: api_token query parameter
resp = requests.get(f"https://api.pipedrive.com/v1/deals?api_token={token}")

# v2: Bearer in Authorization header
headers = {"Authorization": f"Bearer {token}"}
resp = requests.get("https://api.pipedrive.com/v2/deals", headers=headers)
```

### 2. Validate Token Format
```python
token = token.strip()  # Remove whitespace
if not token or len(token) < 10:
    print("Token appears invalid — check Pipedrive Settings > API")

# For OAuth, check expiry
if token_type == "oauth":
    if time.time() > oauth_expires_at:
        print("OAuth token expired — refresh")
        # Implement refresh flow
```

### 3. Refresh OAuth Token
```python
def refresh_pipedrive_oauth(refresh_token, client_id, client_secret):
    resp = requests.post("https://oauth.pipedrive.com/oauth/token", data={
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
    })
    return resp.json()  # Contains new access_token and refresh_token
```

## Prevention

- Store the API version alongside each token to ensure correct auth method usage
- For OAuth, implement proactive token refresh before expiry (refresh after 50 minutes)
- Strip whitespace from tokens and validate length before use
- Use environment variables or a secrets manager — never hardcode tokens
- Add a startup test: call a simple endpoint to verify authentication works

## Official Documentation

- [Pipedrive API Authentication](https://developers.pipedrive.com/docs/api/v1/authentication)
- [Pipedrive OAuth Guide](https://developers.pipedrive.com/docs/api/oauth)
- [Pipedrive API Documentation](https://developers.pipedrive.com/docs/api/v1)

## People Also Ask

- **How do I authenticate with Pipedrive API v1?** Pass your API token as a query parameter: `?api_token=YOUR_TOKEN`. Find your token in Pipedrive Settings > API.
- **How do I authenticate with Pipedrive API v2?** Use the `Authorization: Bearer YOUR_TOKEN` header. v2 requires OAuth tokens, not API tokens.
- **Do Pipedrive API tokens expire?** No — API tokens (v1) do not expire. OAuth access tokens (v2) expire after a set period (typically 1 hour) and require refresh.
- **Where do I find my Pipedrive API token?** In Pipedrive web UI: Settings (gear icon) > API > Your token. Copy the full token string.

## Related Errors

- [Pipedrive 403 Forbidden](/pipedrive/errors/403) — Request not allowed
- [Pipedrive 400 Bad Request](/pipedrive/errors/400) — Request not understood
- [Pipedrive 429 Rate Limit](/pipedrive/errors/429) — Rate limit exceeded
