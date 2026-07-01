---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "ActiveCampaign API 401: Invalid or missing API token"
description: "Fix ActiveCampaign API 401 (401 Unauthorized) error. Invalid or missing API token. Verify Api-Token header is present and correct."
tool: "activecampaign"
errorCode: "401"
errorName: "401 Unauthorized"
httpStatus: 401
category: "authentication"
severity: "high"
priority: 1
lastUpdated: '2026-05-10'
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "activecampaign api 401 error"
  - "activecampaign 401 fix"
  - "activecampaign api invalid or missing api"
  - "activecampaign http 401"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Your ActiveCampaign API key is wrong or expired, so the server won't let you in.

**The fix:**
1. Go to ActiveCampaign → Settings → Developer → API Access
2. Copy the current API key (or generate a new one)
3. Replace the old key in your integration with the new one

**Copy-paste this code** (if you're using a code editor):
```python
import requests

headers = {"Api-Token": "YOUR_NEW_KEY_HERE"}
resp = requests.get("https://{account}.api-us1.com/api/3/contacts", headers=headers)
print(resp.status_code)  # 200 means it works
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Start by asking your AI coding tool:

> I'm getting a 401 Unauthorized error from the ActiveCampaign API.
> The error message is: "Invalid or missing API token"
> I'm using a custom integration that sends requests with the Api-Token header.
> Please give me a step-by-step fix with working Python code to authenticate correctly.

The response should tell you how to find and update your API key, and show you the correct header format.

If that doesn't resolve it, send a second prompt:
> The fix didn't work. I'm still getting 401 errors. Here's what I tried: [paste your code]. Please debug this.

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to fix ActiveCampaign authentication in popular automation tools:

### Zapier
1. Open your Zap → click the ActiveCampaign action step
2. Click "Reconnect" on the ActiveCampaign account connection
3. Paste your new API key from ActiveCampaign Settings → Developer → API Access

### Make (Integromat)
1. Open your scenario → click the ActiveCampaign module
2. Click the connection dropdown → "Add" a new connection
3. Enter your ActiveCampaign URL and new API key, then save

### n8n
1. Open your workflow → click the ActiveCampaign node
2. Under "Credentials" → click "Create New" or edit the existing one
3. Paste the new API key and your account URL, then save

### Power Automate
1. Open your flow → click the ActiveCampaign action
2. Click the connection settings (three dots menu) → "Sign in" or "Edit connection"
3. Enter your updated API key and account URL

**Which tool should you use?** Zapier makes re-authentication the easiest — just click "Reconnect" and paste the new key.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"401 Unauthorized"`
- `"API key invalid"`
- `"Invalid or missing API token"`
- `"Authentication failed"` in your integration logs

**What it means in plain English:** ActiveCampaign doesn't recognize your API key. It's either wrong, expired, or missing from your request. Get a fresh key and try again.

**Most common cause:** Someone regenerated the API key in ActiveCampaign settings but forgot to update the integration that uses it.

</div>

## What Causes ActiveCampaign 401

ActiveCampaign returns HTTP 401 when the `Api-Token` header is missing, invalid, or has been revoked. The API authenticates via a per-user API token found in Settings > Developer > API Access. A 401 means the server either didn't receive the token or the token doesn't match any active key on the account.

The response body contains `{"errors":[{"title":"401 Unauthorized","detail":"Invalid or missing API token"}]}`. This error is distinct from 403 (authenticated but not authorized) — 401 means the authentication itself failed.

### Common Scenarios
- Forgetting to include the `Api-Token` header in API requests
- Regenerating the API key in ActiveCampaign settings without updating the integration
- Using an API key from a different ActiveCampaign account
- API key revoked due to security policy or account changes

## How to Detect If You're Affected

1. Test authentication with a simple curl:
   ```bash
   curl -s -w "\n%{http_code}" "https://{account}.api-us1.com/api/3/contacts" \
     -H "Api-Token: $YOUR_TOKEN" | tail -1
   ```
   Returns 401 if token is invalid.

2. Check the response detail field:
   ```bash
   curl -s "https://{account}.api-us1.com/api/3/contacts" \
     -H "Api-Token: $YOUR_TOKEN" | jq '.errors[0].title'
   ```

3. Verify the API key in ActiveCampaign settings: Settings > Developer > API Access should show "Enabled" with a valid key.

## Step-by-Step Fix

### 1. Verify and Update the API Token
```python
import requests

# Test with your current token
url = "https://{account}.api-us1.com/api/3/contacts"
headers = {"Api-Token": "your_current_token"}
resp = requests.get(url, headers=headers)

if resp.status_code == 401:
    print("Token invalid — regenerate in ActiveCampaign settings")
    new_token = "regenerated_token_from_settings"
    headers["Api-Token"] = new_token
    resp = requests.get(url, headers=headers)
    print(f"Status after fix: {resp.status_code}")
```

### 2. Update All Integration Endpoints
```bash
# BAD — missing Api-Token header
curl -s "https://{account}.api-us1.com/api/3/contacts"

# GOOD — include Api-Token header
curl -s "https://{account}.api-us1.com/api/3/contacts" \
  -H "Api-Token: YOUR_VALID_TOKEN"
```

### 3. Use Environment Variables for Token Storage
```python
import os

# Store token in environment variable, never hardcode
headers = {"Api-Token": os.environ["ACTIVECAMPAIGN_API_TOKEN"]}

resp = requests.get("https://{account}.api-us1.com/api/3/contacts", headers=headers)
print(resp.status_code)  # 200 if token is valid
```

## Prevention

- Store the API token in environment variables or a secrets manager, never in code
- Set up monitoring for 401 responses and alert when they spike
- Generate a dedicated API key per integration so regenerating one doesn't break others
- Rotate API keys periodically and update all integrations in sync
- Test authentication with a single GET request before making write operations

## Official Documentation

- [ActiveCampaign API Overview](https://developers.activecampaign.com/reference/overview)
- [ActiveCampaign Authentication](https://developers.activecampaign.com/reference/authentication)

## People Also Ask

- **How do I find my ActiveCampaign API key?** Go to Settings > Developer > API Access. The API key is shown under "Your API URL" and "Your API Key". If not visible, generate a new key.
- **Does ActiveCampaign API use OAuth?** No — ActiveCampaign uses a simple API token passed via the `Api-Token` header. No OAuth flow is required.
- **Can I have multiple ActiveCampaign API keys?** Yes — each user can have their own API key. Manage them under Settings > Developer > API Access for each user.
- **What happens if I regenerate my ActiveCampaign API key?** The old key is immediately invalidated. All integrations using the old key will get 401 until updated with the new key.

See all [ActiveCampaign API errors](/activecampaign/) in our complete reference.

Similar auth issues occur with [Salesforce 401](/salesforce/errors/401), [HubSpot 401](/hubspot/errors/401), and [Slack invalid_auth](/slack/errors/invalid_auth).

This error also affects integrations. See our [ActiveCampaign to Slack](/integrations/activecampaign-to-slack/) and [Salesforce to ActiveCampaign](/integrations/salesforce-to-activecampaign/) integration error guides.

## Related Errors

- [ActiveCampaign 403 Forbidden](/activecampaign/errors/403) — Authenticated but not authorized for resource
- [ActiveCampaign 404 Not Found](/activecampaign/errors/404) — Resource does not exist
- [ActiveCampaign 429 Rate Limit](/activecampaign/errors/429) — Too many requests
