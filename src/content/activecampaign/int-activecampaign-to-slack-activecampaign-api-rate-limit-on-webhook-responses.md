---
layout: ../../layouts/IntegrationErrorLayout.astro
title: "ActiveCampaign API Rate Limit on Webhook Responses — 5s ACK Deadline Causes Retries"
description: "ActiveCampaign expects a 200 response within 5 seconds for each webhook delivery. When your middleware blocks on Slack 429s, ActiveCampaign times you out and redelivers, causing duplicate downstream actions. ACK first; process asynchronously."
toolA: "activecampaign"
toolB: "slack"
integrationSlug: "activecampaign-to-slack"
errorSlug: "activecampaign-api-rate-limit-on-webhook-responses"
errorName: "ActiveCampaign API rate limit on webhook responses"
category: "RATE_LIMIT"
errorType: "error"
severity: "high"
priority: 2
lastUpdated: "2026-03-29"
lastReviewed: "2026-03-29"
pageType: "integration-error"
author: "API Integration Hub"
keywords:
  - "activecampaign webhook 5 second ack deadline"
  - "activecampaign webhook timeout duplicate retries"
  - "activecampaign webhook resend timeout 200"
  - "activecampaign webhook response must be 2xx 5s"
  - "middleware ack before processing webhook"
  - "activecampaign webhook delivery fail retry policy"
---


<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** ActiveCampaign webhooks overwhelm Slack's rate limit because your middleware tries to post to Slack before responding to ActiveCampaign. ActiveCampaign times out at 5 seconds and retries, creating duplicates.

**The fix:**
1. ACK the ActiveCampaign webhook immediately with a 200 response (under 1 second)
2. Queue the Slack message for async delivery after the ACK
3. Add a delay module in Make or Zapier between ActiveCampaign and Slack steps
4. Use webhook_id for deduplication so retries don't create duplicate Slack messages

**Copy-paste this code** (if you're using a code editor):
```python
import threading

@app.post("/acf/hook")
def hook():
    payload = request.json
    threading.Thread(target=send_to_slack, args=(payload,)).start()
    return "", 200  # ACK in milliseconds
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code workaround](#no-code-workaround).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm integrating ActiveCampaign with Slack and getting duplicate Slack messages. ActiveCampaign webhooks are being retried because my middleware takes too long to respond (over 5 seconds) while waiting for Slack's API. How do I ACK the webhook immediately and process the Slack message asynchronously?

**What to expect:** The AI should walk you through ACK-first architecture and adding a queue between the webhook receiver and the Slack poster.

**If it doesn't work**, add this follow-up:
> I set up ACK-first but I'm still seeing duplicate Slack messages. How do I add idempotency keys using the ActiveCampaign webhook_id?

**Best AI tools for this:** ChatGPT-4 (good at step-by-step UI navigation), Claude (good at explaining API concepts)

</div>

## No-Code Workaround <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to debug this? Here's how to handle ActiveCampaign-to-Slack rate limit issues in other automation tools:

### Zapier
1. Create a new Zap with trigger 'Webhooks by Zapier' (Catch Hook) -- Zapier auto-responds 200 to ActiveCampaign instantly
2. Add a 'Delay by Zapier' step (1 second) before the Slack action to pace messages
3. Zapier auto-retries on Slack 429 errors, so no messages are lost

### Make (Integromat)
1. Use the 'Instant Trigger (Webhook)' module -- Make returns 200 to ActiveCampaign immediately
2. Add a 'Sleep' module (1 second) before the Slack module to respect Slack's rate limit
3. Add an error handler on the Slack module to catch 429 and retry after the Retry-After period

### n8n
1. Create a webhook trigger node -- n8n responds 200 immediately before processing
2. Add a 'Wait' node (1 second) before the Slack node
3. Enable 'Retry on Fail' on the Slack node with 3 retries and 2-second intervals

### Power Automate
1. Use 'When an HTTP request is received' trigger -- Power Automate responds quickly
2. Add a 'Delay' action (1 second) before the Slack 'Post message' action
3. Enable 'Retry Policy' on the Slack action with exponential interval

**Which tool should you use?** Zapier is the easiest -- its Catch Hook trigger auto-ACKs ActiveCampaign webhooks instantly and handles Slack retries automatically.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these:

- ActiveCampaign webhook log shows the same event retried every 30 seconds
- Slack channel gets the same notification 2-5 times within minutes
- Your middleware logs show Slack returning 429 ratelimited while ActiveCampaign waits
- ActiveCampaign dashboard shows webhook delivery failures or timeouts

**What it means in plain English:** ActiveCampaign expects a response within 5 seconds, but your middleware is stuck waiting for Slack to accept the message. ActiveCampaign thinks the delivery failed and keeps retrying.

**Most common cause:** Your middleware processes the Slack call synchronously before responding to ActiveCampaign, exceeding the 5-second ACK deadline whenever Slack rate-limits.

</div>

## The Problem

ActiveCampaign fires a webhook, your middleware synchronously pushes to Slack, Slack is throttled (429 with Retry-After = 1 s), the middleware waits for the Slack retry, the AC webhook hits the 5-second ACK deadline, AC declares the delivery failed and queues it again. The downstream Slack channel now gets the same event delivered 2–5 times; ops sees "duplicate lead created" Slack alerts and CRM end up double-inserted.

## Root Cause

- **ActiveCampaign has a 5-second ACK window**: the receiver must return `2xx` (200/201/204) within 5 seconds or AC records it as a failed delivery and retries.
- **Slack `Retry-After`** can be 1–3 seconds; combined with middleware CPU/network latency, you easily exceed 5 seconds whenever Slack throttles.
- **ActiveCampaign's retry policy**: retries every 30s up to 5 attempts over 30 minutes — a burst of duplicate deliveries every 30s when deadlines are missed.
- **Idempotency missing**: middleware like a single Zap lacks idempotency keys, so retries write duplicate contacts/tags into CRM.
- **Slack's `ratelimited` 429**: locked into 1 req/sec on Tier 3, perpetually triggering this cascade.

| Middleware behavior | AC outcome |
|---|---|
| ACK in < 1s, then process async | Single delivery, no duplicate |
| Block on Slack call, 200 returns at 7s | AC records failed, retries in 30s |
| Block on Slack call (Slack 429) | AC times out at 5s, retries 5 times |

## How to Detect If You're Affected

1. ActiveCampaign webhook log; look for the same event "instance" retried:
   ```bash
   # webhooks dashboard: filter "Delivered" and look at Time per row — same webhook_id in 30-second intervals
   ```
2. Count duplicate same-id payloads in middleware:
   ```bash
   rg 'acf.*webhook_id' middleware.log | sort | uniq -c | sort -rn | head
   ```
3. Slack channel proof: same lead appears in Slack notifications within minutes triggered multiple times (search "AC retry / 30s gap).
4. CRM proof: duplicate active campaign tag assignments in audit history for the same contact.

## Step-by-Step Fix

1. ACK webhooks immediately on receipt, before doing downstream work:
   ```python
   @app.post("/acf/hook")
   def hook():
       payload = request.json
       threading.Thread(target=handle, args=(payload,)).start()
       return "", 200  # return within milliseconds
   ```
2. Use a durable queue (SQS, RabbitMQ, in-memory queue) to absorb spikes — duplicate detection here is easier than at Slack.
3. For Zapier: use the "Webhooks by Zapier" Catch Hook as the trigger; Zapier auto-responds 200 before your action steps run, so AC ACKs in time.
4. For Make: use the "Instant Trigger (Webhook)" module; Make returns 200 immediately and queues processing — Make actually kicks back "Response in 150ms" here.
5. Implement idempotency keys keyed on `webhook_id`:
   ```python
   if redis.exists(payload["webhook_id"]):
       return "", 200
   redis.setex(payload["webhook_id"], 3600, "1")
   ```
6. Wrong: call `requests.post("https://slack.com...")` synchronously before returning 200. Correct: enqueue first, return 200 within 1 second.

## Prevention

- Mandatory: every AC webhook consumer must return 2xx under 2 seconds — include a unit test that asserts the ACK time.
- CacheSlack messages you'd send; flush on a 1-second timer that paces Slack calls — protects against duplicate cascades.
- Subscribe ActiveCampaign's `webhook_id` (added to headers in mid-2025) so downstream duplicates are deduplicated even across mirrored middleware instances.
- Alert whenever AC webhook duplicate ratio (same `webhook_id` in > 1 request) exceeds 0.1% — duplicates at any volume mean a low-latency downstream component or an AC ACK timeout.
- Document for ops: response codes ending in anything other than 2xx count as failures — non-200 paths will be retried.

## Integration-Specific Context

- **Native ActiveCampaign-Slack**: no native Slack integration; you own this entire path.
- **Zapier Webhooks by Zapier**: instant triggers ACK to AC before the action chain runs — the correct abstraction.
- **Make**: use the instant webhook-trigger module — same behavior as Zapier, returning 200 instantly.
- **Custom middleware**: snippet above; treat the webhook receiver as 5 s SLA service.
- **2026 change**: AC revised its retry policy — the 5 s ACK deadline persists; retries now occur every 30s for 5 attempts and then permanently fail. Schedule robustness of receivers, not just retry at Slack-level.

## People Also Ask

- **How long does ActiveCampaign wait for a webhook response?** 5 seconds. Return 2xx within that window or ActiveCampaign marks the delivery failed and retries up to 5 times.
- **Why does my ActiveCampaign webhook get redelivered multiple times?** Your middleware exceeded the 5-second ACK deadline — usually because it blocks on Slack's Tier 3 rate limit (1 req/sec) which forces a `Retry-After` sleep.
- **How do I stop ActiveCampaign from retrying duplicates?** ACK immediately with 2xx, then process Slack posting asynchronously from a queue, and use `webhook_id` for idempotency.
- **What HTTP statuses does ActiveCampaign accept as success?** Any 2xx — 200, 201, 204. Anything else (including 4xx errors from your app) will trigger retries.

## Official Documentation

**ActiveCampaign:**
- [API Overview](https://developers.activecampaign.com/reference/overview)
- [Authentication](https://developers.activecampaign.com/reference/authentication)

**Slack:**
- [Web API](https://api.slack.com/web)
- [Rate Limits](https://api.slack.com/docs/rate-limits)

Related: [ActiveCampaign 429](/activecampaign/errors/429) for AC rate limits, [Slack rate_limited](/slack/errors/rate_limited) for Slack rate limits.

See all [ActiveCampaign API errors](/activecampaign/) or [Slack API errors](/slack/) for more troubleshooting.

## Related Errors
- [Slack 1 req/sec vs ActiveCampaign webhook burst](/integrations/activecampaign-to-slack/errors/slack-1-req-sec-vs-activecampaign-webhook-burst)
- [ActiveCampaign webhook payload format](/integrations/activecampaign-to-slack/errors/activecampaign-webhook-payload-format)
- [Calendly webhook delivery delays](/integrations/zapier-to-calendly/errors/calendly-webhook-delivery-delays)
- [ActiveCampaign API Reference](/activecampaign)
- [Slack API Reference](/slack)