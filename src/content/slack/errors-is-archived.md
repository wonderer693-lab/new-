---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Slack API is_archived: Channel is archived"
description: "Fix Slack API is_archived error. Channel is archived — cannot post. Check channel status before posting."
tool: "slack"
errorCode: "is_archived"
errorName: "is_archived"
httpStatus: 0
category: "unknown"
severity: "medium"
priority: 2
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "slack api is_archived error"
  - "slack is_archived fix"
  - "slack api channel is archived —"
---

## What Causes Slack is_archived

Slack returns the `is_archived` error when you attempt to post a message, upload a file, or perform any write operation on a channel that has been archived. Archived channels are read-only — no member (including bots) can send new messages or modify the channel in any way.

The error appears as `{"ok":false,"error":"is_archived"}`. Channels are archived by workspace admins or members with permission. This is a permanent state unless an admin explicitly un-archives the channel. Archived channels still appear in `conversations.list` with `is_archived: true` but reject all write operations.

### Common Scenarios
- Bot tries to post a notification to a channel that was archived by an admin
- Integration still references an old channel that was cleaned up and archived
- User archived the channel but the integration's channel list was not updated
- Automation checks a channel for updates but the channel was set to read-only first

## How to Detect If You're Affected

1. Check the response error field:
   ```bash
   curl -s -X POST "https://slack.com/api/chat.postMessage" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"channel":"C12345","text":"Hello"}' | jq '.error'
   ```
   If `"is_archived"`, the channel is archived.

2. Check channel info before posting:
   ```bash
   curl -s "https://slack.com/api/conversations.info?channel=C12345" \
     -H "Authorization: Bearer $TOKEN" | jq '.channel.is_archived'
   ```

## Step-by-Step Fix

### 1. Check Channel Status Before Posting
```python
def is_channel_archived(channel_id, headers):
    resp = requests.get(
        "https://slack.com/api/conversations.info",
        headers=headers,
        params={"channel": channel_id}
    )
    data = resp.json()
    return data.get("channel", {}).get("is_archived", False)

if is_channel_archived(channel_id, headers):
    print(f"Channel {channel_id} is archived — cannot post")
else:
    requests.post("https://slack.com/api/chat.postMessage", headers=headers,
                  json={"channel": channel_id, "text": "Hello"})
```

### 2. Route to a Fallback Channel
```python
def post_with_fallback(channel_id, text, fallback_channel):
    if is_channel_archived(channel_id, headers):
        return requests.post("https://slack.com/api/chat.postMessage", headers=headers,
            json={"channel": fallback_channel, "text": f"[Originally for {channel_id}] {text}"})
    return requests.post("https://slack.com/api/chat.postMessage", headers=headers,
        json={"channel": channel_id, "text": text})
```

### 3. Notify Admin to Un-Archive
```python
if is_channel_archived(channel_id, headers):
    admin_channel = get_admin_channel()
    requests.post("https://slack.com/api/chat.postMessage", headers=headers,
        json={"channel": admin_channel,
              "text": f"Channel <#{channel_id}> is archived — integration blocked"})
```

## Prevention

- Check `is_archived` from `conversations.info` before every write operation
- Maintain a local cache of channel status and refresh it daily to detect newly archived channels
- Set up a monitor that periodically scans channels your bot uses and alerts if any become archived
- Implement a fallback channel for critical notifications when primary channel is archived
- For user-facing messages, use ephemeral messages or DMs as a fallback

## Official Documentation

- [Slack conversations.info](https://api.slack.com/methods/conversations.info)
- [Slack Channel Archiving](https://slack.com/help/articles/213185307-Archive-a-channel)
- [Slack chat.postMessage](https://api.slack.com/methods/chat.postMessage)

## People Also Ask

- **Can I post to an archived Slack channel?** No — archived channels are read-only. Ask an admin to un-archive it or use a different channel.
- **How do I know if a Slack channel is archived?** Call `conversations.info` — the `is_archived` field returns `true` if the channel is archived.
- **Does Slack is_archived apply to direct messages?** No — DMs cannot be archived. This error only applies to public and private channels.
- **Can my bot un-archive a channel?** No — only workspace admins with appropriate permissions can un-archive a channel from the Slack UI.

## Related Errors

- [Slack not_in_channel](/slack/errors/not_in_channel) — Bot is not a member of the channel
- [Slack user_is_bot](/slack/errors/user_is_bot) — Bot token used on user-only method
- [Slack invalid_auth](/slack/errors/invalid_auth) — Invalid auth credentials
