---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Slack API account_inactive: OAuth token has been revoked"
description: "Fix Slack API account_inactive error. OAuth token has been revoked. Re-authorize the app with the workspace."
tool: "slack"
errorCode: "account_inactive"
errorName: "account_inactive"
httpStatus: 0
category: "unknown"
severity: "medium"
priority: 2
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "slack api account_inactive error"
  - "slack account_inactive fix"
  - "slack api oauth token has been"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** The Slack account you're trying to use is deactivated. Someone (usually an admin) turned off this user's account, so the token attached to it no longer works.

**The fix:**
1. Ask your Slack workspace admin to check if the user account is still active
2. If the user left the company, have an admin re-install the app with a different account
3. Use a dedicated service account for integrations so this doesn't happen again

**Copy-paste this code** (if you're using a code editor):
```python
import requests

resp = requests.post("https://slack.com/api/auth.test",
    headers={"Authorization": f"Bearer {TOKEN}"})
if resp.json().get("error") == "account_inactive":
    print("User account is deactivated — ask admin to re-install the app")
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm getting an "account_inactive" error from the Slack API.
> The response is: {"ok":false,"error":"account_inactive"}
> My integration was working before but now it stopped.
> Please explain what this means and give me a step-by-step fix with working Python code.

**What to expect:** The AI should explain that the Slack user account behind your token was deactivated and walk you through re-authorizing with an active account.

**If it doesn't work**, add this follow-up:
> The fix didn't work. I still get account_inactive after re-installing. Here's what I tried: [paste your code]. Please debug this.

**Best AI tools for this:** Claude (best at explaining Slack auth flows), ChatGPT-4 (good code generation), Cursor (if you want inline code fixes)

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to fix the account_inactive error in popular automation tools:

### Zapier
1. Open your Zap → click the Slack action step
2. Go to "Account" → click "Reconnect" → sign in with an active Slack admin account
3. Test the step to confirm the new connection works

### Make (Integromat)
1. Open your scenario → click the Slack module → go to "Connection"
2. Click "Create a new connection" → authorize with an active workspace member
3. Run the scenario once to verify the new token works

### n8n
1. Open your workflow → click the Slack node → go to "Credentials"
2. Click "Create New" → complete the OAuth flow with an active Slack account
3. Execute the node to confirm the connection is live

### Power Automate
1. Open your flow → click the Slack action → go to "Connection"
2. Click "Add new connection" → sign in with an active Slack workspace member
3. Save and run the flow to test the new connection

**Which tool should you use?** Any of these work — the key is reconnecting with an active Slack account, not the deactivated one.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `{"ok":false,"error":"account_inactive"}`
- `{"ok":false,"error":"user_not_found"}`
- `"account_inactive"` in your integration logs
- Your Slack integration suddenly stops working after someone leaves the company

**What it means in plain English:** The Slack user account tied to your integration token has been turned off. The token itself might be fine, but the person behind it no longer has an active account.

**Most common cause:** An employee left the company and their Slack account was deactivated by an admin, or a guest account expired.

</div>

## What Causes Slack account_inactive

Slack returns the `account_inactive` error when the Slack user account associated with your OAuth token has been deactivated, disabled, or removed from the workspace. Unlike `token_revoked` (which means the app was uninstalled), `account_inactive` means the user behind the token no longer has an active account. See all [Slack API errors](/slack/) in our complete reference.

Similar account issues occur with [Salesforce 404](/salesforce/errors/404) and [HubSpot 404](/hubspot/errors/404).

The error appears as `{"ok":false,"error":"account_inactive"}`. This can happen when a user is deactivated by an admin, the user deletes their own account, or the user is removed from the workspace during an SCIM provisioning sync. The token itself may be perfectly valid — it's the underlying user account that's gone.

### Common Scenarios
- Employee left the company and admin deactivated their Slack account
- User account was deactivated due to inactivity policy
- SCIM provisioning removed the user from the workspace
- Workspace migration — user IDs changed during a workspace merge or migration
- Guest account expired or was removed by the workspace admin

## How to Detect If You're Affected

1. Check the error response:
   ```bash
   curl -s "https://slack.com/api/auth.test" \
     -H "Authorization: Bearer $TOKEN" | jq '.error'
   ```
   If `"account_inactive"`, the user account is deactivated.

2. Compare with token status — the token may still be valid but the user is gone:
   ```python
   if error == "account_inactive":
       print("User account deactivated — token will never work again")
   ```

## Step-by-Step Fix

### 1. Determine the User's Status
```python
def check_user_status(user_id, admin_token):
    resp = requests.get(
        "https://slack.com/api/users.info",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={"user": user_id}
    )
    data = resp.json()
    user = data.get("user", {})
    if user.get("deleted"):
        return "deleted"
    if not user.get("is_active"):
        return "deactivated"
    return "active"
```

### 2. Notify the Workspace Admin
```python
if error == "account_inactive":
    # Send notification to workspace owner or admin
    admin_channel = get_workspace_admin_channel()
    requests.post("https://slack.com/api/chat.postMessage", headers=admin_headers,
        json={"channel": admin_channel,
              "text": f"Integration user account is deactivated — token not working"})
```

### 3. Re-Authorize with an Active Account
```python
# The integration must be re-installed by an active workspace admin
# Generate a new install URL pointing to admin authorization
install_url = f"https://slack.com/oauth/v2/authorize?client_id={CLIENT_ID}&scope={SCOPES}&redirect_uri={REDIRECT_URI}"
print(f"Re-authorize required — send admin to: {install_url}")
```

## Prevention

- Use a dedicated integration user account that is never deactivated — create a "bot owner" or "service account" in Slack
- Implement SCIM-aware logic: if a user is de-provisioned during SCIM sync, pause the integration rather than retrying infinitely
- Set up monitoring for `account_inactive` errors — they indicate a user management issue that needs manual resolution
- For app installations, suggest the workspace admin install the app rather than a regular user
- Maintain a fallback admin user ID that can re-authorize the integration if the primary account is deactivated

This error also affects integrations. See our [HubSpot to Slack](/integrations/hubspot-to-slack/), [Make to Slack](/integrations/make-to-slack/), and [ActiveCampaign to Slack](/integrations/activecampaign-to-slack/) integration error guides.

## Official Documentation

- [Slack User Deactivation](https://slack.com/help/articles/204475027-Deactivate-a-user-account)
- [Slack auth.test](https://api.slack.com/methods/auth.test)
- [Slack OAuth Tokens](https://api.slack.com/authentication/token-types)

## People Also Ask

- **What's the difference between Slack account_inactive and token_revoked?** `account_inactive` means the underlying user account is deactivated — the token itself may be valid but the user is gone. `token_revoked` means the token was explicitly revoked by a user or admin.
- **Can I reactivate an inactive Slack account via API?** No — user activation/deactivation is an admin UI action. You cannot reactivate accounts through the Slack API.
- **Does account_inactive affect all tokens for that user?** Yes — all OAuth tokens issued to that user (including bot tokens scoped to that user's workspace) will return `account_inactive`.
- **How do I fix account_inactive?** An active workspace admin must re-install the app. The old token cannot be recovered — a new OAuth installation flow is required.

## Related Errors

- [Slack token_revoked](/slack/errors/token_revoked) — Token was revoked
- [Slack invalid_auth](/slack/errors/invalid_auth) — Invalid auth credentials
- [Slack user_is_bot](/slack/errors/user_is_bot) — Bot token used on user-only method
