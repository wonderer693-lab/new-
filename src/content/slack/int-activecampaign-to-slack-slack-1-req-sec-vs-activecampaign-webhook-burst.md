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

## The Problem

A marketer bulk-tags 100 ActiveCampaign contacts in the admin UI; ActiveCampaign fires a webhook for every changed contact; your middleware immediately sends a Slack notification each, and 99% of those calls return `{"ok":false,"error":"ratelimited"}` from Slack. On-call sees one notification in Slack and 99 failed webhooks on the ActiveCampaign webhook log — the team thinks only one contact was tagged.

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