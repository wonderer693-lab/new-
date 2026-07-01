---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "HubSpot API 403: Token lacks required OAuth scopes for the requested resource"
description: "Fix HubSpot API 403 (403 Forbidden) error. Token lacks required OAuth scopes for the requested resource. Verify OAuth scopes during authorization flow."
tool: "hubspot"
errorCode: "403"
errorName: "403 Forbidden"
httpStatus: 403
category: "permission"
severity: "high"
priority: 1
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "hubspot api 403 error"
  - "hubspot 403 fix"
  - "hubspot api token lacks required oauth"
  - "hubspot http 403"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Your API key doesn't have permission to access this HubSpot resource.

**The fix:**
1. Check which scopes your app needs (e.g., `crm.objects.contacts.read` for reading contacts)
2. Re-authorize your app with the missing scopes included
3. For private apps, go to HubSpot Settings → Integrations → Private Apps and add the missing scopes

**Copy-paste this code** (if you're using a code editor):
```python
import requests

resp = requests.get(url, headers=headers)
if resp.status_code == 403:
    print(f"Missing scopes: {resp.json().get('category')}")
    # Re-authorize with required scopes
    scopes = "crm.objects.contacts.read crm.objects.contacts.write"
    auth_url = f"https://app.hubspot.com/oauth/authorize?client_id={CLIENT_ID}&scope={scopes}"
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm getting a 403 Forbidden error from the HubSpot API.
> The error says "Missing scopes" and "insufficient permissions."
> I'm trying to read deals using the CRM API.
> Please tell me which OAuth scopes I need and how to re-authorize my app with those scopes.

**What to expect:** The AI should list the exact OAuth scopes needed for your endpoint and give you the authorization URL with those scopes included.

**If it doesn't work**, add this follow-up:
> The fix didn't work. I re-authorized but still get 403. Here's my authorization URL: [paste it]. Please check if the scopes are correct.

**Best AI tools for this:** Claude (best at explaining OAuth scopes), ChatGPT-4 (good at building auth URLs), Cursor (if you want inline code fixes)

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to handle HubSpot 403 permission errors in popular automation tools:

### Zapier
1. Open your Zap → click the HubSpot action step
2. Click "Reconnect" next to your HubSpot account
3. During reconnection, make sure all the checkboxes for the features you need are selected (contacts, deals, companies, etc.)

### Make (Integromat)
1. Open your scenario → click the HubSpot module
2. Click the connection dropdown → "Reauthorize"
3. In the authorization popup, check all the permission boxes your scenario needs — especially any new ones since you first connected

### n8n
1. Open your workflow → click the HubSpot node
2. In the "Credentials" section → click "Reconnect"
3. During the OAuth popup, approve all requested scopes — if you added new features to your workflow, you may need additional scopes

### Power Automate
1. Open your flow → click the HubSpot action
2. Click the three dots menu → "My connections" → sign in again
3. During sign-in, approve all the permissions requested — make sure deal, company, and ticket access are checked if your flow needs them

**Which tool should you use?** Zapier makes it easiest to see and select scopes during reconnection — the checkboxes are clearly labeled.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"403 Forbidden"`
- `"Missing scopes"`
- `"insufficient permissions"`
- `"The provided token does not have the required scopes"` in your integration logs

**What it means in plain English:** Your app is logged in correctly, but it wasn't given permission to do what it's trying to do. It's like having a valid key to the building but not to a specific room.

**Most common cause:** You added a new feature to your integration (like reading deals) but didn't re-authorize with the new scope (like `crm.objects.deals.read`).

</div>

## What Causes HubSpot 403

HubSpot returns HTTP 403 when the OAuth token's scopes do not include the permissions required for the requested API endpoint. HubSpot uses OAuth scopes to gate access to different API resources — a token without the `crm.objects.contacts.read` scope cannot read contacts, even if the token is otherwise valid.

The response includes `{"status":"error","message":"The provided token does not have the required scopes","category":"MISSING_SCOPES"}`. The `category` field is always `MISSING_SCOPES` for 403 responses. Scopes are assigned during the OAuth authorization flow and cannot be added to an existing token — you must re-authorize.

### Common Scenarios
- Token only has `crm.objects.contacts.read` but calling `crm.objects.deals.read`
- Integration re-authorized without selecting all required scopes
- New feature added to integration that requires additional scopes not requested initially
- Using a private app token that doesn't have all the scopes assigned
- Token created before a scope was required now needs re-authorization with updated scopes

## How to Detect If You're Affected

1. Check the error category:
   ```bash
   curl -s "https://api.hubapi.com/crm/v3/objects/deals" \
     -H "Authorization: Bearer $TOKEN" | jq '.category'
   ```
   If `"MISSING_SCOPES"`, the token lacks required permissions.

2. Check which scopes your token has vs. what's needed:
   ```python
   # HubSpot doesn't expose a "token scopes" endpoint
   # Check the API documentation for the endpoint you're calling
   # to find which scopes are required
   ```

## Step-by-Step Fix

### 1. Identify Required Scopes
```python
# HubSpot API reference lists required scopes per endpoint
ENDPOINT_SCOPES = {
    "GET /crm/v3/objects/contacts": ["crm.objects.contacts.read"],
    "POST /crm/v3/objects/contacts": ["crm.objects.contacts.write"],
    "GET /crm/v3/objects/deals": ["crm.objects.deals.read"],
    "POST /crm/v3/objects/deals": ["crm.objects.deals.write"],
}
```

### 2. Re-authorize with Correct Scopes
```python
# Build an authorization URL with all required scopes
scopes = " ".join([
    "crm.objects.contacts.read",
    "crm.objects.contacts.write",
    "crm.objects.deals.read",
    "crm.objects.deals.write",
])
auth_url = f"https://app.hubspot.com/oauth/authorize?client_id={CLIENT_ID}&scope={scopes}&redirect_uri={REDIRECT_URI}"
print(f"Send user to: {auth_url}")
```

### 3. Handle 403 in Code
```python
resp = requests.get("https://api.hubapi.com/crm/v3/objects/deals", headers=headers)
if resp.status_code == 403:
    category = resp.json().get("category")
    if category == "MISSING_SCOPES":
        print("Token needs re-authorization with additional scopes")
        # Trigger re-auth flow
```

## Prevention

- Request the maximum set of scopes your integration might need upfront — you can't add scopes without re-authorization
- Document which HubSpot scopes each feature of your integration requires
- Add a permission check on startup: test a representative endpoint for each scope group
- Monitor for 403/MISSING_SCOPES errors and trigger automatic re-authorization
- Use HubSpot's private apps for server-to-server (static scopes, no OAuth flow)

## Official Documentation

- [HubSpot API Scopes](https://developers.hubspot.com/docs/api/scopes)
- [HubSpot OAuth Guide](https://developers.hubspot.com/docs/api/oauth-quickstart-guide)
- [HubSpot API Overview](https://developers.hubspot.com/docs/api/overview)

## People Also Ask

- **What causes HubSpot 403?** Your OAuth token lacks the required scopes for the endpoint. Check the `category` field — if `MISSING_SCOPES`, re-authorize with broader scopes.
- **How do I fix HubSpot 403?** Re-authorize the OAuth flow with all required scopes included. You cannot add scopes to an existing token.
- **How do I check which scopes my HubSpot token has?** HubSpot does not expose a token introspection endpoint. Check the scopes requested during the original OAuth authorization.
- **What's the difference between HubSpot 401 and 403?** 401 means the token is invalid or expired. 403 means the token is valid but lacks the required scopes for that specific endpoint.

## Related Errors

- [HubSpot 401 Unauthorized](/hubspot/errors/401) — OAuth token expired
- [HubSpot 429 Rate Limit](/hubspot/errors/429) — Too Many Requests
- [HubSpot 400 Bad Request](/hubspot/errors/400) — Validation error
