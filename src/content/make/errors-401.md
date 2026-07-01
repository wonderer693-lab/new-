---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Make API 401 Error: Unauthorized — Fix Authentication Issues"
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

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Your Make API key or a connected app's authentication has expired or is invalid.

**The fix:**
1. Go to Make → Profile → API Tokens and check if your token is still active
2. If the token was revoked or expired, generate a new one
3. Update your integration with the new token immediately

**Copy-paste this code** (if you're using a code editor):
```python
import requests

headers = {"Authorization": f"Token {new_token}"}
resp = requests.get("https://api.make.com/api/v2/organizations", headers=headers)
if resp.status_code == 401:
    print("Token still invalid — regenerate in Make admin")
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm getting a 401 Unauthorized error from Make (Integromat).
> The error message is: "Unauthorized — invalid or missing token"
> I'm trying to connect to Make's API or a connected app's authentication expired.
> Please give me a step-by-step fix to re-authenticate and update my token.

**What to expect:** The AI should walk you through regenerating your Make API token and updating your integration configuration.

**If it doesn't work**, add this follow-up:
> The fix didn't work. I'm still getting 401 errors. Here's what I tried: [paste your steps]. Please debug this.

**Best AI tools for this:** Claude (best at explaining Make authentication), ChatGPT-4 (good at token management), Cursor (if you want inline code fixes)

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to fix Make 401 errors in popular automation tools:

### Make (Integromat)
1. Open Make → click your profile icon → "API Tokens"
2. Check if your token shows as "Active" — if not, click "Generate new token"
3. Copy the new token and paste it into your scenario's connection settings

### Zapier
1. Open your Zap → click the Make connection step
2. Click "Reconnect" to re-authenticate your Make account
3. Test the connection — Zapier will confirm if the new auth works

### n8n
1. Open your workflow → click the Make credentials node
2. Click "Edit" → paste your new Make API token
3. Click "Save" and test the connection with the "Test" button

### Power Automate
1. Open your flow → click the Make connection action
2. Click "Edit connection" → sign in again with your Make credentials
3. Save and run a test to verify the new authentication works

**Which tool should you use?** Make's own UI is fastest — regenerate the token directly in your profile settings.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"401 Unauthorized"`
- `"invalid token"`
- `"Unauthorized — invalid or missing token"`
- `"Token expired or revoked"` in your Make logs

**What it means in plain English:** Make doesn't recognize your credentials. Your API token is either wrong, expired, or was deleted. Get a new token and update your setup.

**Most common cause:** The API token was regenerated in Make admin but the integration still uses the old one.

</div>

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
