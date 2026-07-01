---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Salesforce INVALID_SESSION_ID — Causes, Fix & OAuth Session Management"
description: "Fix Salesforce INVALID_SESSION_ID error. MFA enforcement, password expiry, session timeout, and instance URL hardcoding. Production session management strategies."
tool: "salesforce"
errorCode: "INVALID_SESSION_ID"
errorName: "Invalid Session ID"
httpStatus: 401
category: "authentication"
severity: "high"
priority: 2
lastUpdated: "2026-06-13"
keywords:
  - "salesforce invalid_session_id"
  - "salesforce api authentication error"
  - "salesforce session expired"
  - "salesforce oauth token invalid"
  - "salesforce api 401 error fix"
  - "salesforce instance url hardcoding"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Your Salesforce session token is no longer valid — it expired, was revoked, or your password changed.

**The fix:**
1. Refresh your OAuth token using the refresh token from your initial login
2. If the refresh token is also invalid, re-authenticate through the Salesforce login page
3. Make sure you're using the instance URL from the OAuth response (not a hardcoded URL)

**Copy-paste this code** (if you're using a code editor):
```python
import requests

resp = requests.post("https://login.salesforce.com/services/oauth2/token", data={
    "grant_type": "refresh_token",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "refresh_token": REFRESH_TOKEN,
})
new_token = resp.json()["access_token"]
instance_url = resp.json()["instance_url"]
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm getting an INVALID_SESSION_ID error from the Salesforce API.
> The error message is: "Session expired or invalid"
> My integration was working fine but suddenly started failing on every request.
> Please give me a step-by-step fix with working Python code that auto-detects INVALID_SESSION_ID and refreshes the OAuth token automatically.

**What to expect:** The AI should give you a wrapper function that catches INVALID_SESSION_ID errors, refreshes the token, and retries the original request — all automatically.

**If it doesn't work**, add this follow-up:
> The fix didn't work. The refresh token is also returning an error. Here's the error: [paste error]. Please help me re-authenticate.

**Best AI tools for this:** Claude (best at explaining Salesforce session management), ChatGPT-4 (good code generation), Cursor (if you want inline code fixes)

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to fix Salesforce session errors in popular automation tools:

### Zapier
1. Open your Zap → click any Salesforce step
2. Click "Reconnect" on the Salesforce account — this refreshes the OAuth token
3. If reconnecting doesn't work, disconnect completely and add a fresh Salesforce connection

### Make (Integromat)
1. Open your scenario → click any Salesforce module
2. Go to "Connection" → click "Reauthorize" to refresh the OAuth token
3. If that fails, create a new connection from scratch and update all modules to use it

### n8n
1. Open your workflow → click any Salesforce node
2. In "Credentials" → click "Reconnect" to refresh the OAuth session
3. If the credential is completely broken, delete it and create a new one with fresh OAuth

### Power Automate
1. Open your flow → click any Salesforce action
2. Go to the three dots menu → "My connections" → click the refresh icon next to your Salesforce connection
3. If that fails, click "Add new connection" and sign in again

**Which tool should you use?** Zapier makes re-authentication the easiest — one click to reconnect. All tools require you to log in again if the refresh token is expired.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"INVALID_SESSION_ID"`
- `"Session expired or invalid"`
- `"Session expired"`
- `"INVALID_SESSION_ID"` with HTTP 401 in your integration logs

**What it means in plain English:** Your Salesforce login session ran out. It's like a website logging you out after being idle too long — you need to sign in again.

**Most common cause:** Session timeout (default 2 hours), a password change that killed all sessions, or your integration's IP address being outside Salesforce's trusted IP ranges.

</div>

## What Causes INVALID_SESSION_ID



INVALID_SESSION_ID is the most common Salesforce API error. It means your session/OAuth token is not valid for the endpoint you're calling. See all [Salesforce API errors](/salesforce/) in our complete reference.



### Root Causes

- **MFA enforcement**: Salesforce enforces MFA. If user's session requires MFA but your integration doesn't handle it, session invalidated.

- **Password expiry**: User password expires → all sessions for that user are invalidated (including API-only sessions).

- **Instance URL hardcoding**: You hardcoded `https://na1.salesforce.com` but the org was migrated to `na40` or uses My Domain.

- **Session timeout**: Salesforce org session timeout setting (default 2h, can be as low as 15min).

- **OAuth token revoked**: Admin revoked your connected app.

- **IP range restriction**: Salesforce org has trusted IP range; your API call is from outside that range.



## Step-by-Step Fix



### 1. Refresh OAuth Token

```python

import requests



def refresh_salesforce_token(refresh_token, client_id, client_secret):

    resp = requests.post('https://login.salesforce.com/services/oauth2/token', data={

        'grant_type': 'refresh_token',

        'client_id': client_id,

        'client_secret': client_secret,

        'refresh_token': refresh_token

    })

    body = resp.json()

    return body['access_token'], body['instance_url']

```



### 2. Use Dynamic Instance URL

```python

# NEVER hardcode instance URL

# BAD: 'https://na1.salesforce.com'



# GOOD: Always get from OAuth response

instance_url = oauth_response['instance_url']  # e.g., https://yourdomain.my.salesforce.com

```



### 3. Check Session Settings

- Go to Salesforce Setup > Session Settings

- Check 'Timeout Value' — set appropriate for your integration

- Disable 'Force logout on password change' if it's breaking API integrations

- Add integration IP to Trusted IP Ranges



## Common Scenarios



| Scenario | Why It Happens | Fix |

|----------|---------------|-----|

| Works for hours, then fails suddenly | Session timeout | Increase timeout or implement auto-refresh |

| Works from dev machine, fails from server | IP range restriction | Add server IP to trusted ranges |

| Fails after password reset | Password change invalidates sessions | Use dedicated integration user with no password expiry |

| Fails after MFA enrollment | MFA required for session | Use OAuth 2.0 JWT Bearer flow (bypasses MFA) |



## How to Detect If You're Affected

1. Check the response body — Salesforce returns `[{"message":"Session expired or invalid","errorCode":"INVALID_SESSION_ID"}]`.
2. Verify your instance URL matches the OAuth response:
   ```python
   # BAD: hardcoded
   url = "https://na1.salesforce.com/services/data/v60.0/sobjects/Contact"
   
   # GOOD: from OAuth response
   url = f"{instance_url}/services/data/v60.0/sobjects/Contact"
   ```
3. Check Salesforce Setup > Session Settings for timeout value (default 2 hours, can be as low as 15 minutes).
4. Symptom: integration works for hours, then suddenly fails with INVALID_SESSION_ID on every request.

## Prevention

- Use OAuth 2.0 JWT Bearer Flow for server-to-server (no user interaction, no MFA issues)

- Create dedicated 'Integration User' with API access only

- Set session timeout to maximum (8h) for integration users

- Implement auto-refresh: detect INVALID_SESSION_ID → refresh token → retry

- Don't cache access_token longer than 30 minutes
- Similar auth issues occur with [HubSpot 401](/hubspot/errors/401), [Slack invalid_auth](/slack/errors/invalid_auth), and [Zoho INVALID_OAUTHTOKEN](/zoho/errors/invalid-oauthtoken).
- This error also affects integrations. See our [Salesforce to Mailchimp](/integrations/salesforce-to-mailchimp/) and [Salesforce to ActiveCampaign](/integrations/salesforce-to-activecampaign/) integration error guides.



## People Also Ask

- **What causes Salesforce INVALID_SESSION_ID?** The most common causes are: session timeout (default 2h), password expiry (invalidates all sessions), hardcoded instance URL (org migrated to different pod), MFA enforcement, or OAuth token revoked by admin.
- **How long do Salesforce sessions last?** Configurable in Setup > Session Settings. Default is 2 hours, minimum 15 minutes, maximum 8 hours. Each API call resets the timer if "Timeout Value" is set to "Reset on activity".
- **What's the difference between OAuth and JWT Bearer flow?** OAuth Authorization Code flow requires user interaction and is subject to MFA. JWT Bearer flow is server-to-server, no user interaction, bypasses MFA. Use JWT for integrations.
- **Can INVALID_SESSION_ID mean my IP is blocked?** Yes — if the Salesforce org has "Trusted IP Ranges" configured and your API call originates from outside those ranges, the session is invalidated. Add your server IP to Setup > Network Access.

## Official Documentation

- [Salesforce REST API](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/)
- [Salesforce OAuth](https://help.salesforce.com/s/articleView?id=sf.remoteaccess_oauth_web_server_flow.htm)
- [Salesforce Limits](https://developer.salesforce.com/docs/atlas.en-us.salesforce_app_limits_cheatsheet.meta/salesforce_app_limits_cheatsheet/)

## Related Errors

- [HubSpot 401 Unauthorized](/hubspot/errors/401)
- [HubSpot 429 Rate Limit](/hubspot/errors/429)