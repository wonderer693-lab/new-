---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Slack API token_revoked: Token has been revoked by user or workspace admin"
description: "Fix Slack API token_revoked error. Token has been revoked by user or workspace admin. Notify user to re-install the app."
tool: "slack"
errorCode: "token_revoked"
errorName: "token_revoked"
httpStatus: 0
category: "unknown"
severity: "medium"
priority: 2
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "slack api token_revoked error"
  - "slack token_revoked fix"
  - "slack api token has been revoked"
---

## What Causes Slack token_revoked

Slack returns the `token_revoked` error when the OAuth token your app is using has been explicitly revoked by a user or workspace admin. The error appears as `{"ok":false,"error":"token_revoked"}` on any API call. Once revoked, the token is permanently invalid — there is no way to "un-revoke" it.

Users can revoke tokens from Slack's App Management page, and workspace admins can revoke tokens from the admin dashboard. Common reasons include a user uninstalling your app, an admin de-authorizing it, or a security policy that periodically revokes unused OAuth grants.

### Common Scenarios
- User uninstalled your Slack app from their workspace
- Admin removed your app's OAuth permission from the workspace settings
- Security policy rotated all OAuth tokens (common in enterprise grids)
- User changed workspaces and the old workspace token is no longer valid
- App was blocked by Slack due to policy violations or abuse detection

## How to Detect If You're Affected

1. Check the response error field:
   ```bash
   curl -s "https://slack.com/api/auth.test" \
     -H "Authorization: Bearer $TOKEN" | jq '.error'
   ```
   If `"token_revoked"`, the token is permanently invalid.

2. Check if the token was recently valid:
   ```python
   # If you store token creation/refresh timestamps
   if last_successful_call < time.time() - 3600:
       print("Token was valid within the last hour — may be freshly revoked")
   ```

## Step-by-Step Fix

### 1. Detect Revocation
```python
resp = requests.post("https://slack.com/api/auth.test", headers=headers)
data = resp.json()
if not data.get("ok") and data.get("error") == "token_revoked":
    print("Token permanently revoked — must re-install app")
    # Trigger re-authorization flow
```

### 2. Notify the User
```python
def handle_token_revoked(user_email):
    # Send notification asking user to re-install
    send_email(
        to=user_email,
        subject="Slack Integration Disconnected",
        body=f"""
        Your Slack integration token has been revoked.
        Please re-install the app to restore functionality:
        {INSTALL_URL}
        """
    )
```

### 3. Initiate Re-Installation
If the user wants to reconnect, they must go through the OAuth installation flow again:
```python
# Generate a new install URL
install_url = "https://slack.com/oauth/v2/authorize?" + urlencode({
    "client_id": CLIENT_ID,
    "scope": BOT_SCOPES,
    "user_scope": USER_SCOPES,
    "redirect_uri": REDIRECT_URI,
})
# Redirect the user to this URL
```

## Prevention

- Monitor `auth.test` responses — a `token_revoked` there is the earliest detection signal
- Implement a webhook that receives Slack's `tokens_revoked` event if your app supports Event Subscriptions
- Set up a periodic health check that tests the token every hour and alerts if revoked
- Store the `installed_at` timestamp and warn users if no successful API call has been made in 30+ days
- In enterprise grids, handle workspace-level token management where tokens can be independently revoked per workspace

## Official Documentation

- [Slack OAuth Tokens](https://api.slack.com/authentication/token-types)
- [Slack Token Revocation](https://api.slack.com/authentication/revocation)
- [Slack auth.test](https://api.slack.com/methods/auth.test)

## People Also Ask

- **Can I un-revoke a Slack token?** No — once revoked, a token is permanently invalid. The user or admin must re-install the app to generate a new token.
- **How do I detect a revoked Slack token?** Call `auth.test` — if it returns `{"ok":false,"error":"token_revoked"}`, the token has been revoked and cannot be used.
- **What's the difference between token_revoked and account_inactive?** `token_revoked` means the token was explicitly revoked by a user/admin. `account_inactive` means the Slack user account itself is deactivated or disabled.
- **Can I prevent Slack token revocation?** Not directly — users and admins can always revoke tokens. You can minimize revocation risk by clearly communicating what your app does during installation.

## Related Errors

- [Slack account_inactive](/slack/errors/account_inactive) — OAuth token revoked
- [Slack invalid_auth](/slack/errors/invalid_auth) — Invalid auth credentials
- [Slack user_is_bot](/slack/errors/user_is_bot) — Bot token used on user-only method
