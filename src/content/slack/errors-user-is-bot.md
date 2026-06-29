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
