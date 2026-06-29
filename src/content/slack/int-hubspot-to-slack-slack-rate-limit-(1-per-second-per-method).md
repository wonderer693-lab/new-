---
layout: ../../layouts/IntegrationErrorLayout.astro
title: "Slack Rate Limit 1 req/sec Per Method — HubSpot Bulk Deal Update Notifications Fail"
description: "HubSpot bulk deal updates fan out 50+ Slack notifications via a custom middleware, exceeding Slack's 1 req/sec per method limit and returning 429 with Retry-After. Fix with batched chat.postMessage calls, queue with credit tracking, and summary messages."
toolA: "hubspot"
toolB: "slack"
integrationSlug: "hubspot-to-slack"
errorSlug: "slack-rate-limit-(1-per-second-per-method)"
errorName: "Slack rate limit (1 per second per method)"
category: "RATE_LIMIT"
errorType: "error"
severity: "high"
priority: 2
lastUpdated: "2026-05-09"
lastReviewed: "2026-05-09"
pageType: "integration-error"
author: "API Integration Hub"
keywords:
  - "hubspot slack webhook 429 rate limit"
  - "slack chat.postmessage 1 req/sec per method"
  - "hubspot deal update slack notification burst"
  - "slack ratelimited retry after fix"
  - "custom middleware hubspot to slack throttling"
  - "slack tier 3 postmessage limit 2026"
---

## The Problem

A mass HubSpot deal update (a territory reassignment, for example) generates one webhook per deal; your middleware forwards each to Slack as a single notification. Within seconds Slack returns `429 ratelimited`, half the notifications are never delivered, and sales reps miss the very deals they were being notified about.

## Root Cause

- **HubSpot webhooks** fire in parallel for bulk operations: HubSpot caps webhook delivery concurrency — up to 10 simultaneous POSTs in flight per subscription — so a 50-deal update produces a near-instant Slack burst.
- **Slack Tier 3 limit on `chat.postMessage`**: 1 req/sec per method per workspace. Slack evaluates the limit at the workspace level, so two Slack apps posting in different channels still share the budget.
- **Slack ignores scope of token**: bot tokens (`xoxb-`) and user tokens (`xoxp-`) for the same workspace share the chat.postMessage bucket.
- **No built-in queue**: curl-your-way-to-victory middleware does not retry `ratelimited`; the notification is lost.

| Pattern | Slack result |
|---|---|
| Send 50 messages in parallel | ~1 delivered, 49 × `ratelimited` |
| Send 50 with 1 s sleep between each | All delivered, total ~50 s |
| Aggregate → 1 summary message | 1 delivered instantly |

## How to Detect If You're Affected

1. Slack-side browse the API log under `api.slack.com/apps/{app}/logs`; filter for `ratelimited` — the error string is:
   ```json
   {"ok": false, "error": "ratelimited", "retry_after": 1}
   ```
2. In your middleware grep the Slack response body for `"error":"ratelimited"`:
   ```bash
   rg 'ratelimited' middleware.log --stats
   ```
3. Symptom check: notify count != received count in #ops-channel — run message count in Slack via `conversations.history`:
   ```bash
   curl -s "https://slack.com/api/conversations.history?channel=$CH&limit=200&oldest=$(date -d '-1 hour' +%s)" \
     -H "Authorization: Bearer $TOKEN" | jq '.messages | length'
   ```
4. Watch `Retry-After` values consistently at 1 — that's the smoking gun for a missing throttle.

## Step-by-Step Fix

1. Replace per-event notifications with a single summary post:
   ```python
   summary = "\n".join(f"- {d['dealname']} → {d['hubspot_owner_id']}" for d in deals)
   requests.post("https://slack.com/api/chat.postMessage",
       headers={"Authorization": f"Bearer {bot_token}"},
       json={"channel": channel, "text": f"*{len(deals)} deals reassigned*\n{summary}"})
   ```
2. If you must send per-deal notifications, drive Slack from a consumer-paced queue:
   ```python
   import asyncio, time, aiohttp
   class SlackPacer:
       def __init__(self): self.last = 0.0
       async def post(self, s, payload):
           dt = time.monotonic() - self.last
           if dt < 1.0:
               await asyncio.sleep(1.0 - dt)
           self.last = time.monotonic()
           r = await s.post("https://slack.com/api/chat.postMessage", json=payload)
           j = await r.json()
           if j.get("error") == "ratelimited":
               wait = int(j.get("retry_after", 1))
               await asyncio.sleep(wait)
               return await self.post(s, payload)
           return j
   ```
3. Wrong: spawn one thread per HubSpot webhook and POST synchronously — they all hit Slack at the same wall instant.
4. Use Slack Block Kit's "fields" array to put 10 deals in one message, broadening the volume you can summarize in a single call.

## Prevention

- Coalesce webhook events with a 5-second debouncer in your middleware so 50 HubSpot deals arriving in the same second produce one Slack message.
- Track Slack's `Retry-After` value per response and use it to drive sleep — don't hardcode a fixed 1 s sleep, as Slack sometimes asks for more under load.
- Channel categorization: route noisy events to a low-priority channel and have the user subscribe or mute; rare high-urgency events can then run at Slack's full 1/s budget without contention.
- Add a Slack-side kill switch (a flag in your middleware) to mute bursts during a planned HubSpot territory reassignment.
- Monitor for `ratelimited` events as a first-class alert (the error string is easy to grep); treat any non-zero count in a 5-min window as actionable.

## Integration-Specific Context

- **Native HubSpot-Slack connector (HubSpot side)**: batches notifications per user — Slack bursts are rare unless the connector is misconfigured.
- **Zapier HubSpot-Slack** Zap: Zapier routes Slack calls through its own queue, so bursts are paced at ~1/s but multi-Zap collisions consume the same workspace budget.
- **Make (Integromat)**: this is the case where Make's Slack module fails hard without a Throttle module added in front.
- **Custom middleware**: own the credit bucket — the snippet above is the production pattern.
- **2026 change**: with Slack's tightened Tier 3 peak enforcement, even moderate bursts that previously averaged under 1/s now 429. Recompute cadence.

## People Also Ask

- **What is Slack's per-method rate limit on `chat.postMessage`?** Tier 3, approximately one request per second per workspace, regardless of app or token. The limit returns `ratelimited` and a `retry_after` in seconds when exceeded.
- **Why do HubSpot deal-update webhooks fail Slack delivery?** A bulk HubSpot update produces a webhook burst; the middleware then urges Slack faster than 1 req/s and gets `ratelimited`.
- **How do I stop Slack notifications dropping during bulk HubSpot updates?** Aggregate events into a summary message, or pace messages from a queue using the `retry_after` returned by Slack.
- **Does Slack share the `chat.postMessage` limit across channels?** Yes. The limit is per workspace and per method, not per channel.

## Official Documentation

**HubSpot:**
- [API Overview](https://developers.hubspot.com/docs/api/overview)
- [CRM API](https://developers.hubspot.com/docs/api/crm/overview)

**Slack:**
- [Web API](https://api.slack.com/web)
- [Rate Limits](https://api.slack.com/docs/rate-limits)

## Related Errors
- [Slack rate limit in Make scenarios](/integrations/make-to-slack/errors/slack-rate-limit-in-make-scenarios)
- [HubSpot to Slack message formatting issues](/integrations/hubspot-to-slack/errors/message-formatting-issues)
- [Slack 1 req/sec vs ActiveCampaign webhook burst](/integrations/activecampaign-to-slack/errors/slack-1-req-sec-vs-activecampaign-webhook-burst)
- [ActiveCampaign API rate limit on webhook responses](/integrations/activecampaign-to-slack/errors/activecampaign-api-rate-limit-on-webhook-responses)
- [HubSpot API Reference](/hubspot)
- [Slack API Reference](/slack)