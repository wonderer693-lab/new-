---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Slack API not_in_channel: Bot user is not a member of the channel"
description: "Fix Slack API not_in_channel error. Bot user is not a member of the channel. Invite bot to the channel using conversations."
tool: "slack"
errorCode: "not_in_channel"
errorName: "not_in_channel"
httpStatus: 0
category: "unknown"
severity: "medium"
priority: 2
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "slack api not_in_channel error"
  - "slack not_in_channel fix"
  - "slack api bot user is not"
---

## What Causes Slack not_in_channel

Slack returns the `not_in_channel` error when your bot token attempts to read messages, send messages, or perform channel operations in a channel where the bot user has not been added as a member. Slack bots can only access channels they've been explicitly invited to (for private channels) or have joined (for public channels).

The error appears as `{"ok":false,"error":"not_in_channel"}`. This applies to both public and private channels — bots do not automatically have access to all channels in a workspace. The bot must be a member of the channel to read history, listen to messages, or post messages.

### Common Scenarios
- Bot tries to send a message to a channel it hasn't been invited to
- Bot calls `conversations.history` on a channel it doesn't belong to
- Multi-workspace app tries to post to a channel in a workspace where the bot hasn't joined
- Bot was removed from a channel by an admin but the integration still references it
- Dynamic channel creation — bot tries to access a newly created channel before being added

## How to Detect If You're Affected

1. Check the error field in Slack's response:
   ```bash
   curl -s -X POST "https://slack.com/api/chat.postMessage" \
     -H "Authorization: Bearer $BOT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"channel":"C12345","text":"Hello"}' | jq '.error'
   ```
   If `"not_in_channel"`, the bot isn't a member.

2. Verify bot membership via `conversations.members`:
   ```bash
   curl -s "https://slack.com/api/conversations.members?channel=C12345" \
     -H "Authorization: Bearer $BOT_TOKEN" | jq '.members[]'
   ```
   If your bot's user ID is not in the list, it's not a member.

## Step-by-Step Fix

### 1. Check Bot Membership Before Posting
```python
def is_bot_in_channel(channel_id, headers):
    resp = requests.get(
        "https://slack.com/api/conversations.members",
        headers=headers,
        params={"channel": channel_id}
    )
    data = resp.json()
    if not data.get("ok"):
        return False
    # Your bot's user ID — get from auth.test
    bot_user_id = get_bot_user_id(headers)
    return bot_user_id in data.get("members", [])
```

### 2. Invite Bot to the Channel
```python
# Use conversations.invite to add the bot
resp = requests.post("https://slack.com/api/conversations.invite",
    headers=headers,
    json={"channel": channel_id, "users": BOT_USER_ID}
)
print(resp.json())
```

### 3. Handle Missing Membership Gracefully
```python
def post_to_channel(channel_id, text):
    if not is_bot_in_channel(channel_id, headers):
        # Invite bot first, then post
        requests.post("https://slack.com/api/conversations.invite",
            headers=headers,
            json={"channel": channel_id, "users": BOT_USER_ID}
        )
    resp = requests.post("https://slack.com/api/chat.postMessage",
        headers=headers,
        json={"channel": channel_id, "text": text}
    )
    return resp.json()
```

## Prevention

- Call `conversations.members` before any channel operation to verify bot membership
- Implement auto-join: detect `not_in_channel` → invite bot → retry the original operation
- Install your Slack app with `chat:write.public` scope to post to public channels without joining
- For private channels, ensure the installation process includes an invitation step
- Store the list of channels the bot has joined and verify against this list before posting

## Official Documentation

- [Slack conversations.invite](https://api.slack.com/methods/conversations.invite)
- [Slack conversations.join](https://api.slack.com/methods/conversations.join)
- [Slack Bot Membership](https://api.slack.com/automation/channels)

## People Also Ask

- **How do I add my bot to a Slack channel?** Use `conversations.invite` with the bot's user ID, or ask a workspace admin to manually add the bot from the channel's Integrations tab.
- **Can a Slack bot see all public channels?** No — bots must explicitly join each channel. Use `conversations.join` for public channels or `conversations.invite` for private channels.
- **What's the difference between not_in_channel and is_archived?** `not_in_channel` means the bot isn't a member. `is_archived` means the channel is archived and no one can post.
- **Does not_in_channel apply to user tokens too?** Yes — user tokens also need the user to be a member of the channel to perform operations.

## Related Errors

- [Slack is_archived](/slack/errors/is_archived) — Channel is archived
- [Slack user_is_bot](/slack/errors/user_is_bot) — Bot token used on user-only method
- [Slack invalid_auth](/slack/errors/invalid_auth) — Invalid auth credentials
