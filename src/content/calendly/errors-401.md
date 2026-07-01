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
lastUpdated: '2026-04-23'
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "calendly api 401 error"
  - "calendly 401 fix"
  - "calendly api invalid or missing token"
  - "calendly http 401"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Your Calendly access token is expired or invalid, so the API won't let you in.

**The fix:**
1. Check if you're using an OAuth token (expires after 2 hours) or a Personal Access Token
2. If OAuth — refresh it using your refresh token
3. If Personal Access Token — go to Calendly settings and generate a new one

**Copy-paste this code** (if you're using a code editor):
```python
import requests

resp = requests.post("https://auth.calendly.com/oauth/token", data={
    "grant_type": "refresh_token",
    "refresh_token": "YOUR_REFRESH_TOKEN",
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
})
new_token = resp.json()["access_token"]
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Start by asking your AI coding tool:

> I'm getting a 401 Unauthorized error from the Calendly API.
> The error message is: "Invalid or missing token"
> I'm using an OAuth integration that connects to Calendly.
> Please give me a step-by-step fix with working Python code that handles token refresh.

The response should give you a token refresh function and explain the difference between OAuth tokens and Personal Access Tokens.

If that doesn't resolve it, send a second prompt:
> The fix didn't work. I'm still getting 401 errors. Here's what I tried: [paste your code]. Please debug this.

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to fix Calendly 401 errors in popular automation tools:

### Zapier
1. Open your Zap → click the Calendly action step
2. Click "Reconnect" on the Calendly account — this refreshes the OAuth token automatically
3. Test the step again to confirm it works

### Make (Integromat)
1. Open your scenario → click the Calendly module
2. Go to "Connection" → click "Reauthorize" to get a fresh token
3. Run the scenario once to verify the connection

### n8n
1. Open your workflow → click the Calendly node
2. In "Credentials" → click "Reconnect" to refresh the OAuth token
3. Execute the node to test the new connection

### Power Automate
1. Open your flow → click the Calendly action
2. Click the three dots menu → "My connections" → sign in again to Calendly
3. Save and test the flow

**Which tool should you use?** Zapier handles Calendly re-auth the smoothest — one click and you're back in business.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"401 Unauthorized"`
- `"Invalid or missing token"`
- `"Unauthorized"` in your Calendly API logs
- `"HTTP 401"` in your integration dashboard

**What it means in plain English:** Calendly doesn't recognize your access token. It's like trying to open a door with the wrong key — you need a valid one.

**Most common cause:** Using an OAuth token that expired (they only last 2 hours) without refreshing it first.

</div>

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

See all [Calendly API errors](/calendly/) in our complete reference.

Similar auth issues occur with [Salesforce 401](/salesforce/errors/401), [HubSpot 401](/hubspot/errors/401), and [Slack invalid_auth](/slack/errors/invalid_auth).

This error also affects integrations. See our [Zapier to Calendly integration errors](/integrations/zapier-to-calendly/) for common cross-tool issues.

## Related Errors

- [Calendly 403 Forbidden](/calendly/errors/403) — Insufficient permissions
- [Calendly 404 Not Found](/calendly/errors/404) — Resource not found
- [Calendly 429 Rate Limit](/calendly/errors/429) — Too many requests
