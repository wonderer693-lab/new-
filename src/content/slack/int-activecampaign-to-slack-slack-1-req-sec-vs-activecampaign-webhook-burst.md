---
layout: ../../layouts/IntegrationErrorLayout.astro
title: "Slack 1 req/sec vs ActiveCampaign Webhook Burst — Bulk Tag Update Drops 99% of Notifications"
description: "ActiveCampaign triggers a webhook per contact when bulk-tagging 100 records; the middleware post to Slack hits the 1 req/sec per method limit and 99 of 100 messages return 429 ratelimited. Fix by aggregating into one summary message."
toolA: "activecampaign"
toolB: "slack"
integrationSlug: "activecampaign-to-slack"
errorSlug: "slack-1-req-sec-vs-activecampaign-webhook-burst"
errorName: "Slack 1 req/sec vs ActiveCampaign webhook burst"
category: "RATE_LIMIT"
errorType: "error"
severity: "high"
priority: 2
lastUpdated: "2026-04-30"
lastReviewed: "2026-04-30"
pageType: "integration-error"
author: "API Integration Hub"
keywords:
  - "activecampaign bulk tag webhook burst"
  - "slack ratelimited activecampaign trigger"
  - "activecampaign webhook 100 contacts slack 429"
  - "activecampaign to slack rate limit fix"
  - "aggregate slack messages activecampaign webhook"
  - "slack tier 3 postmessage bulk tag update"
---


<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** ActiveCampaign fires a webhook per contact during bulk tag updates. Your middleware sends a Slack notification for each, but Slack's 1 req/sec limit rejects 99 out of 100 messages.

**The fix:**
1. Add a rate limiter or delay module between ActiveCampaign webhooks and Slack posts
2. Buffer webhooks for 2 seconds and aggregate into a single summary Slack message
3. ACK each ActiveCampaign webhook immediately (200) before processing the Slack post
4. Send one summary message like '100 contacts tagged Priority' instead of 100 individual messages

**Copy-paste this code** (if you're using a code editor):
```python
import threading, time

buffer = {}
def on_webhook(payload):
    tag = payload["tag"]["id"]
    buffer.setdefault(tag, []).append(payload["contact"])
    threading.Timer(2.0, drain, args=(tag,)).start()

def drain(tag):
    contacts = buffer.pop(tag, [])
    msg = f'{len(contacts)} contacts tagged "{tag}"'
    print(msg)  # Send this single message to Slack
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code workaround](#no-code-workaround).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Paste this into ChatGPT, Claude, Cursor, or Gemini:

> I'm integrating ActiveCampaign with Slack and bulk tag updates only deliver 1 out of 100 Slack notifications. ActiveCampaign fires a webhook per contact, and Slack's 1 req/sec rate limit rejects the rest. How do I aggregate webhooks into a single summary Slack message?

Expect back help implementing webhook buffering and message aggregation to stay under Slack's rate limit.

Didn't work? Send a refinement prompt:
> I added aggregation but individual notifications are still needed for some events. How do I handle both summary and per-contact messages?

</div>

## No-Code Workaround <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to debug this? Here's how to handle ActiveCampaign-to-Slack rate limiting in other tools:

### Zapier
1. Use Zapier's built-in queue pacing -- it automatically spaces Slack calls at ~1/second
2. Add a 'Delay by Zapier' step (1 second) before each Slack action
3. Use a single summary Zap that aggregates events instead of one notification per webhook

### Make (Integromat)
1. Add a 'Throttle' module (1 second delay) before the Slack module
2. Use Make's 'Array Aggregator' to collect webhook events into a single batch
3. Send one summary Slack message per batch instead of individual notifications

### n8n
1. Add a 'Wait' node (1 second) between Slack message sends
2. Use a 'Merge' node to aggregate events before the Slack node
3. Send a single summary message with the count and details

### Power Automate
1. Add a 'Delay' action (1 second) before each Slack 'Post message' action
2. Use 'Apply to each' with sequential processing to pace messages
3. Aggregate events into a single summary message when possible

**Which tool should you use?** Zapier is the easiest -- its queue pacing automatically spaces Slack calls to respect the 1 req/sec limit.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these:

- Only 1 Slack notification arrives when ActiveCampaign bulk-tags 100 contacts
- Slack returns 429 'ratelimited' for most ActiveCampaign webhook-triggered messages
- ActiveCampaign webhook log shows a 1:99 sent-to-failed ratio
- Slack channel shows one message despite many contacts being tagged

**What it means in plain English:** ActiveCampaign sends one webhook per contact during bulk operations. Your middleware posts each to Slack instantly, exceeding Slack's 1 message per second limit.

**Most common cause:** Forwarding each ActiveCampaign webhook directly to Slack without aggregation or rate limiting.

</div>

## The Problem

A marketer bulk-tags 100 ActiveCampaign contacts in the admin UI; ActiveCampaign fires a webhook for every changed contact; your middleware immediately sends a Slack notification each, and 99% of those calls return `{"ok":false,"error":"ratelimited"}` from Slack. On-call sees one notification in Slack and 99 failed webhooks on the ActiveCampaign webhook log — the team thinks only one contact was tagged.

See all [Slack API errors](/slack/) or [ActiveCampaign API errors](/activecampaign/) for more troubleshooting. Related: [Slack rate_limited](/slack/errors/rate_limited), [ActiveCampaign 429](/activecampaign/errors/429).

## Root Cause

- **ActiveCampaign webhooks fire per-record, synchronously during bulk operations**: there is no batch webhook payload. Each contact update is its own POST to your endpoint within seconds.
- **Slack Tier 3 limit** (`chat.postMessage`): 1 req/sec per workspace. 99 of 100 ActiveCampaign webhooks arriving in a sub-second burst get `ratelimited` with `retry_after=1`.
- **ActiveCampaign tries harder on its own**: if your endpoint does not ACK each webhook with 200 within ~5 seconds, ActiveCampaign considers the delivery failed and stops retrying (see the ActiveCampaign rate-limit-on-webhook-responses error).
- **No deduplication on middleware side**: each webhook is processed independently, with no batching or collapsing of multiple records with the same event type.

| Setting | Behavior |
|---|---|
| AC bulk tag 100 contacts | 100 webhooks, ~1 s apart |
| AC `batched=false` (default) | Webhooks per contact |
| Middleware forwards each to Slack | 1 delivered, 99 `ratelimited` |

## How to Detect If You're Affected

1. ActiveCampaign admin → "Webhooks" tab → click into your webhook URL. The "Sent/Failed" ratio will be ~1:99 for a batch run.
2. Slack app logs (`https://api.slack.com/apps/{app}/logs`): filter for `ratelimited`.
3. Your middleware's HTTP access logs:
   ```bash
   rg 'POST.*activecampaign-hook.*200' middleware-access.log | wc -l
   rg 'POST.*slack.com.*429' middleware-upstream.log | wc -l
   ```
   Expect counts around 100 and 99 respectively for that minute.
4. Slack channel proof: count messages in the channel — only 1 was delivered, despite AC reporting 100 webhooks sent.

## Step-by-Step Fix

1. Coalesce webhooks in the middleware with a 2-second debounce keyed by `tag_id`:
   ```python
   buffer = {}
   def on_webhook(payload):
       tag = payload["payload"]["tag"]["id"]
       buffer.setdefault(tag, []).append(payload["payload"]["contact"])
       threading.Timer(2.0, drain, args=(tag,)).start()
   def drain(tag):
       contacts = buffer.pop(tag)
       msg = f"{len(contacts)} contacts tagged '{tag_map[tag]}'"
       slack_post(msg)
   ```
2. Send one Slack message summarizing the bulk action:
   ```json
   {
     "channel":"#sales-ops",
     "blocks":[
       {"type":"header","text":{"type":"plain_text","text":"Bulk tag update"}},
       {"type":"section","text":{"type":"mrkdwn","text":"100 contacts tagged *Priority*"}},
       {"type":"context","elements":[{"type":"mrkdwn","text":"Triggered in ActiveCampaign"}]}
     ]
   }
   ```
3. ACK every ActiveCampaign webhook immediately with `200 OK` and process asynchronously so AC does not time your endpoint out:
   ```python
   @app.post("/ac/webhook")
   def ac_hook():
       threading.Thread(target=on_webhook, args=(request.json,)).start()
       return "", 200
   ```
4. Wrong: handle the Slack post inline before responding to ActiveCampaign — you may exceed AC's 5 s ACK deadline. Correct: ACK first, post to Slack in the background.

## Prevention

- Route ActiveCampaign webhooks like bulk-tag updates to a queue (SQS/RabbitMQ), then process with a consumer pacing Slack at 1 req/s — this pattern absorbs any burst.
- Configure webhook health alerts on ActiveCampaign's "Delivery Failures" counter > 5 per hour, which is an early warning of Slack-side throttling.
- Maintain a per-tag summary debounce by default; only escalate to individual notifications when signing-on changes explicitly opt-in to per-contact granularity.
- Use Slack's `chat.unfurl` with smart links instead of full messages — reduces both the rate-limit pressure and the noise.
- Run a nightly report on the ActiveCampaign webhook log to assert that the sent/failed ratio is near 1:0; any deviation is a rate-limit signature.

## Integration-Specific Context

- **ActiveCampaign native Slack integration**: does not exist — most orgs use Zapier or Make as the bridge.
- **Zapier "ActiveCampaign → Slack"** Zap: Zapier's queue pacing turns the burst into ~1/s delivery, but you still consume the whole workspace's Slack budget; multiple Zaps posting simultaneously can clash with each other.
- **Make**: needs both a Throttle module and an Array Aggregator; otherwise 99/100 traces error in Make history.
- **Custom middleware**: own the debounce (snippet above) — this is the only method that completely avoids 429 and AC timeouts.
- **2026 change**: ActiveCampaign now sends `webhook_id` and `attempt` headers; log these so clicks on the AC dashboard line up with a single webhook, not a 99-trace blast in Slack.

## People Also Ask

- **Why does Slack drop my ActiveCampaign bulk-tag notifications?** ActiveCampaign sends one webhook per contact during a bulk tag; your middleware then posts to Slack faster than 1 req/s and Slack returns `ratelimited` for the excess.
- **How do I send one Slack message for a 100-contact ActiveCampaign update?** Buffer webhooks in your middleware for 2 seconds keyed by `tag_id`, then send a single summary Slack message.
- **Does ActiveCampaign support batch webhooks?** No. ActiveCampaign sends one webhook per record per event; batching must be implemented in your middleware.
- **What is Slack's `retry_after` unit?** Whole seconds. Sleep that many seconds before retrying the message.

## Official Documentation

**ActiveCampaign:**
- [API Overview](https://developers.activecampaign.com/reference/overview)
- [Authentication](https://developers.activecampaign.com/reference/authentication)

**Slack:**
- [Web API](https://api.slack.com/web)
- [Rate Limits](https://api.slack.com/docs/rate-limits)

## Related Errors
- [ActiveCampaign API rate limit on webhook responses](/integrations/activecampaign-to-slack/errors/activecampaign-api-rate-limit-on-webhook-responses)
- [ActiveCampaign webhook payload format](/integrations/activecampaign-to-slack/errors/activecampaign-webhook-payload-format)
- [Slack rate limit (1 per second per method) — HubSpot to Slack](/integrations/hubspot-to-slack/errors/slack-rate-limit-(1-per-second-per-method))
- [ActiveCampaign API Reference](/activecampaign)
- [Slack API Reference](/slack)