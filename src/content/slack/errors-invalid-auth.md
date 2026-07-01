---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Slack API invalid_auth: Invalid auth credentials"
description: "Fix Slack API invalid_auth error. Invalid auth credentials. Check token format and validity."
tool: "slack"
errorCode: "invalid_auth"
errorName: "invalid_auth"
httpStatus: 0
category: "unknown"
severity: "medium"
priority: 2
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "slack api invalid_auth error"
  - "slack invalid_auth fix"
  - "slack api invalid auth credentials"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Your Slack bot token or user token is wrong. It might be mistyped, copied from the wrong workspace, or missing characters.

**The fix:**
1. Check that your token starts with `xoxb-` (bot) or `xoxp-` (user)
2. Make sure there are no extra spaces or missing characters
3. If in doubt, regenerate the token from your Slack app settings

**Copy-paste this code** (if you're using a code editor):
```python
import requests

resp = requests.post("https://slack.com/api/auth.test",
    headers={"Authorization": f"Bearer {TOKEN.strip()}"})
if resp.json().get("error") == "invalid_auth":
    print("Token is not recognized — check format or regenerate it")
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Start by asking your AI coding tool:

> I'm getting an "invalid_auth" error from the Slack API.
> The response is: {"ok":false,"error":"invalid_auth"}
> I'm using a bot token that starts with xoxb-.
> Please give me a step-by-step fix with working Python code to validate and fix my Slack token.

The response should walk you through checking your token format, testing it against Slack's auth.test endpoint, and regenerating it if needed.

If that doesn't resolve it, send a second prompt:
> The fix didn't work. I regenerated the token but still get invalid_auth. Here's what I tried: [paste your code]. Please debug this.

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to fix invalid_auth in popular automation tools:

### Zapier
1. Open your Zap → click the Slack action step
2. Go to "Account" → click "Reconnect" → sign in again to get a fresh token
3. Test the step to confirm the connection works

### Make (Integromat)
1. Open your scenario → click the Slack module → go to "Connection"
2. Click "Create a new connection" → re-authorize with your Slack workspace
3. Run the scenario once to verify the new token works

### n8n
1. Open your workflow → click the Slack node → go to "Credentials"
2. Delete the old credential → click "Create New" → complete the OAuth flow
3. Execute the node to confirm the connection is live

### Power Automate
1. Open your flow → click the Slack action → go to "Connection"
2. Click "Add new connection" → sign in with your Slack workspace
3. Save and run the flow to test the new connection

**Which tool should you use?** Zapier is the easiest — just click "Reconnect" and it handles the rest.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `{"ok":false,"error":"invalid_auth"}`
- `{"ok":false,"error":"not_authed"}`
- `{"ok":false}` with no error field but auth is failing
- Your Slack integration stopped working after you changed workspaces or regenerated a token

**What it means in plain English:** Slack doesn't recognize your token. It could be mistyped, from the wrong workspace, or missing some characters from a bad copy-paste.

**Most common cause:** Copying a token incorrectly (missing characters, extra spaces) or using a token from one Slack workspace on a different workspace's API.

</div>

## What Causes Slack invalid_auth

Slack returns the `invalid_auth` error when the `Authorization` header contains a token that Slack cannot recognize as valid. This is the most common Slack authentication error — it means the token is malformed, mistyped, expired, or belongs to a different workspace. See all [Slack API errors](/slack/) in our complete reference.

Similar auth issues occur with [Salesforce 401](/salesforce/errors/401), [HubSpot 401](/hubspot/errors/401), and [Zoho INVALID_OAUTHTOKEN](/zoho/errors/invalid-oauthtoken).

The error appears as `{"ok":false,"error":"invalid_auth"}`. Valid Slack tokens start with `xoxb-` (bot tokens) or `xoxp-` (user tokens), followed by a unique string. A common mistake is using a token from one workspace against a different workspace's API, or using a token that was truncated during copy-paste.

### Common Scenarios
- Token copied incorrectly — missing characters or extra whitespace
- Using a token generated for one Slack workspace against another workspace's API
- Token from an older Slack app format (pre-2020) that has been deprecated
- Token was regenerated but the integration still uses the old value
- Wrong token type — using a webhook URL instead of an OAuth token

## How to Detect If You're Affected

1. Check the error response:
   ```bash
   curl -s "https://slack.com/api/auth.test" \
     -H "Authorization: Bearer $TOKEN" | jq '.error'
   ```
   If `"invalid_auth"`, your token is not recognized.

2. Validate token format:
   ```bash
   echo $TOKEN | grep -E '^xox[bps]-[A-Za-z0-9]+'
   ```

## Step-by-Step Fix

### 1. Validate Token Format
```python
import re

def validate_slack_token(token):
    if not re.match(r'^xox[bps]-[A-Za-z0-9]{10,}$', token):
        print("Invalid token format — must start with xoxb- or xoxp-")
        return False
    return True

# Test against Slack's auth.test endpoint
def test_token(token):
    resp = requests.post("https://slack.com/api/auth.test",
        headers={"Authorization": f"Bearer {token}"})
    return resp.json().get("ok", False)
```

### 2. Check for Extra Whitespace or Truncation
```python
# BAD — copy-paste errors
token = " xoxb-12345"  # Leading space
token = "xoxb-1234"  # Truncated

# GOOD
token = token.strip()  # Remove whitespace
assert len(token) > 20, "Token appears truncated"  # Basic length check
```

### 3. Regenerate Token
If validation fails, generate a new token from the Slack API dashboard:
```python
# Install the app again to get fresh tokens
install_url = f"https://slack.com/oauth/v2/authorize?client_id={CLIENT_ID}&scope={SCOPES}&redirect_uri={REDIRECT_URI}"
print(f"Re-install required: {install_url}")
# After installation, exchange code for new token
```

## Prevention

- Store tokens in environment variables or a secrets manager — never hardcode them
- Add a startup check that calls `auth.test` and fails immediately if token is invalid
- Validate token format with a regex before making any API calls
- Implement token rotation alerts — if a 401/`invalid_auth` appears, notify the team immediately
- Use Slack's OAuth v2 flow (not v1) which provides clearer error messages

This error also affects integrations. See our [HubSpot to Slack](/integrations/hubspot-to-slack/), [Make to Slack](/integrations/make-to-slack/), and [ActiveCampaign to Slack](/integrations/activecampaign-to-slack/) integration error guides.

## Official Documentation

- [Slack auth.test](https://api.slack.com/methods/auth.test)
- [Slack OAuth Tokens](https://api.slack.com/authentication/token-types)
- [Slack Token Best Practices](https://api.slack.com/authentication/best-practices)

## People Also Ask

- **What does Slack invalid_auth mean?** The token in your `Authorization` header is not recognized by Slack. Check token format, workspace, and whether it was recently regenerated.
- **What format should a Slack token have?** Bot tokens start with `xoxb-`, user tokens start with `xoxp-`. The full token is typically 30-50 characters including the prefix.
- **How is invalid_auth different from token_revoked?** `invalid_auth` means the token format or workspace is wrong. `token_revoked` means the token was valid but a user/admin explicitly revoked it.
- **Can a Slack token expire?** Slack access tokens do not have a built-in expiration, but they can be revoked by users, admins, or Slack's security systems.

## Related Errors

- [Slack token_revoked](/slack/errors/token_revoked) — Token was revoked
- [Slack account_inactive](/slack/errors/account_inactive) — OAuth token revoked
- [Slack user_is_bot](/slack/errors/user_is_bot) — Bot token used on user-only method
