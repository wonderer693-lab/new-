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

## What Causes Slack invalid_auth

Slack returns the `invalid_auth` error when the `Authorization` header contains a token that Slack cannot recognize as valid. This is the most common Slack authentication error — it means the token is malformed, mistyped, expired, or belongs to a different workspace.

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
