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