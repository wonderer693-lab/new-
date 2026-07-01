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
lastUpdated: '2026-05-16'
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "slack api not_in_channel error"
  - "slack not_in_channel fix"
  - "slack api bot user is not"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Your Slack bot isn't invited to the channel. Bots can only read and post in channels they've been added to.

**The fix:**
1. Open the channel in Slack → click the channel name → "Integrations" tab
2. Click "Add an App" and select your bot
3. Or type `/invite @YourBotName` in the channel

**Copy-paste this code** (if you're using a code editor):
```python
import requests

resp = requests.post("https://slack.com/api/conversations.join",
    headers={"Authorization": f"Bearer {BOT_TOKEN}"},
    json={"channel": "C12345"})
if resp.json().get("ok"):
    print("Bot joined the channel — now you can post messages")
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

The more context you give your AI, the better the fix. Send this:

> I'm getting a "not_in_channel" error from the Slack API when trying to post a message.
> The response is: {"ok":false,"error":"not_in_channel"}
> My bot needs to send messages to this channel but hasn't been added yet.
> Please give me a step-by-step fix with working Python code that invites the bot to the channel and then posts a message.

Expect the AI to give you code that checks if the bot is in the channel, invites it if not, and then sends the message. 

Still stuck? Reply with this:
> The fix didn't work. The bot still can't post after joining. Here's what I tried: [paste your code]. Please debug this.

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to fix not_in_channel in popular automation tools:

### Zapier
1. Open the Slack channel in your browser → click the channel name → "Integrations"
2. Click "Add an App" → find and add your Zapier-connected bot
3. Go back to Zapier → test the Slack action step to confirm it works

### Make (Integromat)
1. Open the Slack channel → type `/invite @YourBotName` to add the bot
2. Open your scenario → click the Slack module → test the connection
3. Run the scenario once to verify messages go through

### n8n
1. Open the Slack channel → click the channel name → "Integrations" → "Add an App"
2. Add your n8n-connected bot to the channel
3. Execute the Slack node in your workflow to confirm it works

### Power Automate
1. Open the Slack channel → type `/invite @YourBotName` to add the bot
2. Open your flow → click the Slack action → test the connection
3. Save and run the flow to verify messages are delivered

**Which tool should you use?** The fix is the same for all tools — invite the bot to the channel first, then retry.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `{"ok":false,"error":"not_in_channel"}`
- `{"ok":false,"error":"channel_not_found"}` (returned when bot can't see a private channel)
- Your bot's messages silently fail and the logs show "not_in_channel"
- A newly created channel doesn't receive your bot's notifications

**What it means in plain English:** Your Slack bot hasn't been added to the channel it's trying to post in. Bots don't automatically have access to every channel — they need to be invited first.

**Most common cause:** The bot was never invited to the channel, or someone removed it. New channels also don't include bots by default.

</div>

## What Causes Slack not_in_channel

Slack returns the `not_in_channel` error when your bot token attempts to read messages, send messages, or perform channel operations in a channel where the bot user has not been added as a member. Slack bots can only access channels they've been explicitly invited to (for private channels) or have joined (for public channels). See all [Slack API errors](/slack/) in our complete reference.

Similar permission issues occur with [Salesforce 403](/salesforce/errors/403), [HubSpot 403](/hubspot/errors/403), and [Mailchimp 403](/mailchimp/errors/403).

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

This error also affects integrations. See our [HubSpot to Slack](/integrations/hubspot-to-slack/), [Make to Slack](/integrations/make-to-slack/), and [ActiveCampaign to Slack](/integrations/activecampaign-to-slack/) integration error guides.

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
