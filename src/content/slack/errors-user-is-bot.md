---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Slack API user_is_bot: Bot user tried to access a method not available to bots"
description: "Fix Slack API user_is_bot error. Bot user tried to access a method not available to bots. Use user token instead of bot token for the specific method."
tool: "slack"
errorCode: "user_is_bot"
errorName: "user_is_bot"
httpStatus: 0
category: "unknown"
severity: "medium"
priority: 2
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "slack api user_is_bot error"
  - "slack user_is_bot fix"
  - "slack api bot user tried to"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** You're trying to perform an action that bots can't do. Some Slack API methods only work with user tokens, not bot tokens.

**The fix:**
1. Check if your token starts with `xoxb-` (bot) — you need `xoxp-` (user) for this method
2. Re-install your Slack app with user token scopes to get an `xoxp-` token
3. Use the user token instead of the bot token for this specific API call

**Copy-paste this code** (if you're using a code editor):
```python
import requests

resp = requests.post("https://slack.com/api/users.setPresence",
    headers={"Authorization": f"Bearer {USER_TOKEN}"},
    json={"presence": "auto"})
if resp.json().get("error") == "user_is_bot":
    print("This method needs a user token (xoxp-), not a bot token (xoxb-)")
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm getting a "user_is_bot" error from the Slack API.
> The response is: {"ok":false,"error":"user_is_bot"}
> I'm using a bot token (xoxb-) to call users.setPresence.
> Please give me a step-by-step fix with working Python code that shows how to use a user token instead.

**What to expect:** The AI should explain the difference between bot and user tokens and show you how to get a user token through Slack's OAuth flow.

**If it doesn't work**, add this follow-up:
> The fix didn't work. I got a user token but still get user_is_bot. Here's what I tried: [paste your code]. Please debug this.

**Best AI tools for this:** Claude (best at explaining Slack token types), ChatGPT-4 (good code generation), Cursor (if you want inline code fixes)

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to fix user_is_bot in popular automation tools:

### Zapier
1. Open your Zap → click the Slack action step
2. Go to "Account" → click "Reconnect" → during authorization, make sure to approve user token scopes
3. Test the step to confirm the connection includes user-level permissions

### Make (Integromat)
1. Open your scenario → click the Slack module → go to "Connection"
2. Click "Create a new connection" → during OAuth, approve the user scopes when prompted
3. Run the scenario once to verify the user token is working

### n8n
1. Open your workflow → click the Slack node → go to "Credentials"
2. Click "Create New" → during OAuth, ensure user scopes are included in the authorization
3. Execute the node to confirm the user token has the right permissions

### Power Automate
1. Open your flow → click the Slack action → go to "Connection"
2. Click "Add new connection" → approve user-level permissions during sign-in
3. Save and run the flow to test the new connection

**Which tool should you use?** The fix is the same for all tools — you need to re-authorize with user token scopes, not just bot scopes.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `{"ok":false,"error":"user_is_bot"}`
- `{"ok":false,"error":"not_allowed"}`
- Your bot token works for posting messages but fails for user-specific actions like setting presence
- You get this error on methods like `users.setPresence`, `users.profile.set`, or `admin.*` endpoints

**What it means in plain English:** You're using a bot token to call a Slack method that only works with user tokens. Bot tokens and user tokens have different permissions — some actions can only be done on behalf of a real person, not a bot.

**Most common cause:** Using a bot token (`xoxb-`) on a method that requires a user token (`xoxp-`), like setting user presence or updating a user profile.

</div>

## What Causes Slack user_is_bot

Slack returns the `user_is_bot` error when a bot token (`xoxb-*`) is used to call a method that is restricted to user tokens (`xoxp-*` or `xoxs-*`). Certain Slack API methods — particularly those involving user presence, user status, or admin-level operations — are not available to bot users and require a user-level OAuth token.

The error response is `{"ok":false,"error":"user_is_bot"}`. This is a permission model distinction: bot tokens act as the bot app itself, while user tokens act on behalf of a specific Slack user. Methods like `users.setPresence`, `admin.*`, and `users.profile.set` all require user tokens.

### Common Scenarios
- Calling `users.setPresence` with a bot token to set a user's online status
- Using `users.profile.set` with a bot token to update a user's profile
- Calling any `admin.*` endpoints (e.g., `admin.users.invite`) with a bot token
- Building a custom integration that needs to impersonate users but only has a bot token

## How to Detect If You're Affected

1. Check the error field in Slack's response:
   ```bash
   curl -s -X POST "https://slack.com/api/users.setPresence" \
     -H "Authorization: Bearer $BOT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"presence":"auto"}' | jq '.error'
   ```
   If `"user_is_bot"`, the method requires a user token.

2. Check your token type — bot tokens start with `xoxb-`, user tokens start with `xoxp-`:
   ```bash
   echo $TOKEN | grep -o '^xox[bp]'
   ```

## Step-by-Step Fix

### 1. Identify the Required Token Type
```python
# Check the Slack API docs to see if the method requires a user token
# Methods that return user_is_bot typically need xoxp-* tokens

def get_token_type(token):
    if token.startswith("xoxb-"):
        return "bot"
    elif token.startswith("xoxp-"):
        return "user"
    return "unknown"
```

### 2. Switch to a User Token
```python
# BAD — bot token on user-only method
bot_token = "xoxb-123456"
resp = requests.post("https://slack.com/api/users.setPresence",
    headers={"Authorization": f"Bearer {bot_token}"},
    json={"presence": "auto"}
)
print(resp.json()["error"])  # user_is_bot

# GOOD — use user token
user_token = "xoxp-789012"
resp = requests.post("https://slack.com/api/users.setPresence",
    headers={"Authorization": f"Bearer {user_token}"},
    json={"presence": "auto"}
)
print(resp.json()["ok"])  # true
```

### 3. Get a User Token via OAuth
If you don't have a user token, request one during Slack app installation with the `user.token` scope:
```python
# During OAuth, request user token scopes
SCOPES = "users:write,users.profile:write"
auth_url = f"https://slack.com/oauth/v2/authorize?client_id={CLIENT_ID}&scope={SCOPES}&user_scope={USER_SCOPES}"
# After authorization, exchange code for tokens — response includes both bot and user tokens
```

## Prevention

- Document which Slack API methods require bot vs user tokens in your integration's README
- Store both bot token (`xoxb-`) and user token (`xoxp-`) from the OAuth response
- Route API calls to the correct token based on the method requirements
- Add a check at integration startup: validate that you have a user token if you call user-only methods
- Use Slack's `auth.test` method to verify token type and available scopes on startup

## Official Documentation

- [Slack API Methods](https://api.slack.com/methods)
- [Slack OAuth Tokens](https://api.slack.com/authentication/token-types)
- [Slack Bot vs User Tokens](https://api.slack.com/authentication/token-types#bot)

## People Also Ask

- **What methods return user_is_bot?** Methods like `users.setPresence`, `users.profile.set`, `admin.*` endpoints, and any method that acts on a specific user rather than as a bot.
- **How do I know if my token is a bot or user token?** Bot tokens start with `xoxb-`, user tokens start with `xoxp-`. Check the first 5 characters of your token.
- **Can I convert a bot token to a user token?** No — they're different token types with different purposes. You need to request a user token during OAuth installation with appropriate `user_scope` parameters.
- **Does the user_is_bot error mean my bot is misconfigured?** No — it means the specific method you're calling requires user-level permissions. Your bot token is fine for bot-permitted methods.

## Related Errors

- [Slack invalid_auth](/slack/errors/invalid_auth) — Invalid auth credentials
- [Slack token_revoked](/slack/errors/token_revoked) — Token was revoked
- [Slack account_inactive](/slack/errors/account_inactive) — OAuth token revoked
