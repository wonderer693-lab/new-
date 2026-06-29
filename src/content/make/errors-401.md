---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Make API 401: Unauthorized"
description: "Fix Make API 401 error. Unauthorized — invalid or missing token. Verify API token is valid and has required scopes."
tool: "make"
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
  - "make api 401 error"
  - "make 401 fix"
  - "make api unauthorized — invalid or"
  - "make http 401"
---

## What Causes Make 401

Make returns HTTP 401 when the `Authorization` header contains an invalid, expired, or missing API token. Make uses token-based authentication with the `Authorization: Token <your_token>` header format. A 401 means either the token was mistyped, has been revoked, or the header format is incorrect.

The response is `{"error":"Unauthorized"}`. This is distinct from 403 (forbidden) — 401 means the server doesn't recognize your credentials at all.

### Common Scenarios
- Token is missing from the request header entirely
- Token is copied incorrectly (extra spaces, partial copy, or wrong case)
- Token was regenerated in Make admin but the integration still uses the old one
- Token was revoked due to security policy or user deactivation
- Incorrect header format — using `Bearer` instead of `Token` scheme

## How to Detect If You're Affected

1. Test the token directly:
   ```bash
   curl -s -w "\n%{http_code}" "https://api.make.com/api/v2/organizations" \
     -H "Authorization: Token $TOKEN" | tail -1
   ```
   If `401`, the token is invalid.

2. Check the exact header being sent (debug mode):
   ```bash
   curl -s -v "https://api.make.com/api/v2/organizations" \
     -H "Authorization: Token $TOKEN" 2>&1 | grep -i "authorization"
   ```

## Step-by-Step Fix

### 1. Verify Header Format
```python
# BAD — wrong scheme
headers = {"Authorization": f"Bearer {token}"}  # Make uses "Token", not "Bearer"

# BAD — missing scheme
headers = {"Authorization": token}

# GOOD
headers = {"Authorization": f"Token {token}"}
```

### 2. Test Token Validity
```python
def check_token_valid(token):
    headers = {"Authorization": f"Token {token}"}
    resp = requests.get("https://api.make.com/api/v2/organizations", headers=headers)
    if resp.status_code == 401:
        print("Token is invalid or expired — regenerate")
        return False
    return True
```

### 3. Regenerate Token
In Make admin: Organization settings > API Tokens > Generate new token. Update your configuration immediately:
```python
# Store securely — never hardcode
import os
MAKE_TOKEN = os.environ.get("MAKE_API_TOKEN")
```

## Prevention

- Store Make API tokens in environment variables or a secrets manager — never in code
- Implement automatic token validation on application startup
- Set up monitoring for 401 responses and alert the team immediately
- Document the required `Token` header format (not `Bearer`) in your integration guide
- Rotate tokens quarterly and during staff transitions

## Official Documentation

- [Make API Documentation](https://www.make.com/en/api-documentation)
- [Make API Authentication](https://www.make.com/en/api-documentation#authentication)
- [Make API Tokens](https://www.make.com/en/api-documentation#tokens)

## People Also Ask

- **What header format does Make API use?** Make uses `Authorization: Token <token>` — not `Bearer` like most OAuth APIs. Using `Bearer` will result in a 401.
- **How do I get a Make API token?** Go to Make admin > Organization settings > API Tokens > Generate new token. Copy the token immediately — it's only shown once.
- **Can Make API tokens expire?** Make API tokens don't expire automatically but can be revoked manually from the admin dashboard. Security policies may enforce periodic rotation.
- **Does Make 401 mean my account is locked?** Not necessarily — 401 means the token is unrecognized. It could be a typo, expired, or revoked. Check the token in admin settings first.

## Related Errors

- [Make 403 Forbidden](/make/errors/403) — Insufficient permissions
- [Make 429 Rate Limit](/make/errors/429) — Rate limit exceeded
- [Make 500 Server Error](/make/errors/500) — Server error
