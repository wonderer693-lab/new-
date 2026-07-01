---
layout: ../../layouts/IntegrationErrorLayout.astro
title: "HubSpot to Slack Bot Not in Channel — chat.postMessage Returns not_in_channel"
description: "Slack bot tokens grant chat:write but not auto-join; posting to a private channel the bot wasn't invited to returns not_in_channel. Fix by inviting the bot, calling conversations.join with channels:join scope, or posting to the channel ID."
toolA: "hubspot"
toolB: "slack"
integrationSlug: "hubspot-to-slack"
errorSlug: "bot-not-in-channel"
errorName: "Bot not in channel"
category: "PERMISSION"
errorType: "error"
severity: "high"
priority: 2
lastUpdated: "2026-05-03"
lastReviewed: "2026-05-03"
pageType: "integration-error"
author: "API Integration Hub"
keywords:
  - "slack not_in_channel error fix"
  - "slack bot chat:write scope must join channel"
  - "slack conversations.join scope channels:join"
  - "hubspot slack integration private channel 403"
  - "slack bot invite to private channel api"
  - "slack chat.postmessage channel name vs id"
---


<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Your HubSpot-Slack bot isn't invited to the target channel. Slack returns 'not_in_channel' when the bot tries to post to a private channel it hasn't been added to.

**The fix:**
1. Invite the bot to the channel: type /invite @YourBotName in the Slack channel
2. Or use the Slack API: call conversations.invite with the bot's user ID
3. Always use channel IDs (C012AB3CD) instead of channel names in your integration
4. Add the channels:join scope so the bot can self-join public channels

**Copy-paste this code** (if you're using a code editor):
```python
import requests

# Invite bot to a private channel
resp = requests.post("https://slack.com/api/conversations.invite",
    headers={"Authorization": f"Bearer {admin_token}",
             "Content-Type": "application/json"},
    json={"channel": "C012AB3CD", "users": "U_BOT_USER_ID"})
print(resp.json())  # Should show {"ok": true}
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code workaround](#no-code-workaround).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm integrating HubSpot with Slack and getting 'not_in_channel' errors when posting to private channels. The Slack bot has chat:write scope but hasn't been invited to the target channel. How do I invite the bot and prevent this from happening with new channels?

**What to expect:** The AI should walk you through inviting the bot to the channel and setting up auto-join for future channels.

**If it doesn't work**, add this follow-up:
> I invited the bot but it still gets 'not_in_channel' on some channels. Could workspace admin policies be blocking the bot?

**Best AI tools for this:** ChatGPT-4 (good at step-by-step UI navigation), Claude (good at explaining API concepts)

</div>

## No-Code Workaround <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to debug this? Here's how to handle bot channel membership in other automation tools:

### Zapier
1. In Zapier's Slack action, re-auth the connection after inviting the bot to new channels
2. Use channel IDs (not names) in the Zap's Slack action configuration
3. Test the Zap after inviting the bot to confirm it can post

### Make (Integromat)
1. In Make's Slack module, re-select the channel after inviting the bot
2. Use the channel ID picker (not manual text entry) for reliable targeting
3. Add an error handler to catch 'not_in_channel' and alert your team

### n8n
1. Add an HTTP Request node to call conversations.invite before posting
2. Use the Slack node with the channel ID (not name) for posting
3. Add error handling for 'not_in_channel' with an alert

### Power Automate
1. Use the 'Invite to channel' Slack action before posting
2. Use channel IDs in the 'Post message' action
3. Add error handling for permission errors

**Which tool should you use?** Zapier is the easiest -- just re-auth the Slack connection after inviting the bot, and use channel IDs from the dropdown.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these:

- Slack returns 'not_in_channel' when posting HubSpot notifications
- Public channel notifications work but private channel notifications fail
- The Slack bot doesn't appear in the channel's member list
- New channels created after setup don't receive HubSpot notifications

**What it means in plain English:** The Slack bot needs to be a member of the channel before it can post. Private channels require an explicit invite; the bot can't auto-join them.

**Most common cause:** The bot was never invited to the private channel, or new channels were created after the initial setup without adding the bot.

</div>

## The Problem

A HubSpot-triggered Slack notification intermittently fails with `{"ok":false,"error":"not_in_channel"}`. Public channels work; private channels fail; DMs sometimes work, sometimes don't. The integration looked perfect in setup but breaks the moment you target a private `#deals-west` channel.

## Root Cause

- **`chat:write` alone is not enough** for private channels. A Slack bot must be a member of the channel to post; `chat:write` only grants it the ability to post *where it's already a member*.
- **Private channels require explicit invite**: `/invite @Bot` in-channel, or `conversations.invite` from an admin.
- **Public channels** auto-join if the bot has `channels:join`; without it, the bot stays out and `not_in_channel` returns.
- **Channel name vs. channel ID**: passing a channel name like `#deals-west` works in the Slack UI but is unreliable over the API; IDs (`C012AB3CD`) resolve reliably.
- **Workspace admin policy**: even bots with the right scopes get `not_authorized` if the admin disabled `bot:join` for the channel — a 2026 FedRAMP tightening.

| Scope present | Posting public channel | Posting private channel |
|---|---|---|
| `chat:write` only | OK if bot is member | `not_in_channel` unless invited |
| `chat:write` + `channels:join` | Auto-join on first post | still requires invite |
| `chat:write` + `groups:write` | — | Bot can self-join via `conversations.join` |

## How to Detect If You're Affected

1. Slack response body check — the literal error:
   ```bash
   rg '"error":"not_in_channel"' middleware.log | head
   ```
2. List channels the bot is in:
   ```bash
   curl -s "https://slack.com/api/users.conversations?types=public_channel,private_channel" \
     -H "Authorization: Bearer $BOT_TOKEN" | jq '.channels[].id'
   ```
   If your target channel is missing, this is the cause.
3. Symptom: notifications deliver only to public channels; private ones fail silently.
4. Cross-check scopes: `curl -s https://slack.com/api/auth.test` then look up requested scopes on the app config.

## Step-by-Step Fix

1. Invite the bot to the private channel:
   ```bash
   curl -s -X POST https://slack.com/api/conversations.invite \
     -H "Authorization: Bearer $ADMIN_TOKEN" \
     -H "Content-Type: application/json" \
     -d "{\"channel\":\"$CH_ID\",\"users\":\"$BOT_USER_ID\"}"
   ```
2. Or grant `channels:join` + `groups:write` to the bot and self-join:
   ```bash
   curl -s -X POST https://slack.com/api/conversations.join \
     -H "Authorization: Bearer $BOT_TOKEN" \
     -H "Content-Type: application/json" \
     -d "{\"channel\":\"$CH_ID\"}"
   ```
3. Always post with channel ID (not name). Resolve name → ID once and cache:
   ```bash
   CH_ID=$(curl -s "https://slack.com/api/conversations.list?types=private_channel" \
     -H "Authorization: Bearer $BOT_TOKEN" | \
     jq -r '.channels[] | select(.name=="deals-west") | .id')
   ```
4. Wrong: pass `"channel":"#deals-west"` — Slack sometimes returns `channel_not_found` and never consistently resolves a private channel name. Correct: pass `"channel":"C012AB3CD"`.

## Prevention

- Onboard new channels to the bot via an automated provisioning script that always calls `conversations.join` after channel creation to guarantee membership.
- Request `channels:join` and `groups:write` at install time — Slack no longer grants them retroactively without re-OAuth.
- Cache channel IDs resolved via `conversations.list` (refresh nightly) so channel renames do not silently break the integration.
- Run a "membership probe" once a week — list reachable channels and diff against the configured notifications list to flag missing memberships.
- For DMs via `im:write`, verify `im.open` succeeds once per recipient to make sure the bot has an existing IM channel.

## Integration-Specific Context

- **Native HubSpot-Slack connector**: handles its own bot membership via OAuth but only fetches channels at install; new private channels require re-running the connector setup.
- **Zapier Slack app**: only lists channels the Zap's bot can see at Zap-creation time — new private channels won't appear in the dropdown until you re-auth the connection.
- **Make Slack module**: identical caveat; use the channel ID picker only after inviting the bot.
- **Custom middleware**: own the `conversations.join` fail-safe — call it before posting to any new channel.
- **2026 change**: Slack rolled out enterprise-only channel role controls; a bot can be a member but still get `not_in_channel` if it lacks the per-channel "poster" role. Check with your enterprise admin.

## People Also Ask

- **Why does my Slack bot get `not_in_channel` on private channels?** `chat:write` grants posting where the bot is already a member. Private channels require an explicit `/invite` or `conversations.invite` from an admin.
- **How do I invite a Slack bot to a private channel?** Use `/invite @your_bot` inside the channel, or call `conversations.invite` with `users: conversations.list` and the bot's user ID.
- **Should I post to Slack by channel name or channel ID?** Channel ID is reliable; channel name resolution is inconsistent over the API, especially for private channels, which can return `channel_not_found`.
- **Can a Slack bot self-join a private channel?** Only if it has the `groups:write` scope; otherwise `conversations.join` returns `missing_scope` on private channels.

## Official Documentation

**HubSpot:**
- [API Overview](https://developers.hubspot.com/docs/api/overview)
- [OAuth Guide](https://developers.hubspot.com/docs/api/oauth-quickstart-guide)

**Slack:**
- [Web API](https://api.slack.com/web)
- [Rate Limits](https://api.slack.com/docs/rate-limits)

## Related Errors
- [HubSpot to Slack message formatting issues](/integrations/hubspot-to-slack/errors/message-formatting-issues)
- [Slack rate limit (1 per second per method) — HubSpot to Slack](/integrations/hubspot-to-slack/errors/slack-rate-limit-(1-per-second-per-method))
- [Make Slack module OAuth re-authentication](/integrations/make-to-slack/errors/make-slack-module-oauth-re-authentication)
- [HubSpot API Reference](/hubspot)
- [Slack API Reference](/slack)