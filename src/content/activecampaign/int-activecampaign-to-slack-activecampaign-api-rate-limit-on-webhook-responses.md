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

## Related Errors
- [Slack 1 req/sec vs ActiveCampaign webhook burst](/integrations/activecampaign-to-slack/errors/slack-1-req-sec-vs-activecampaign-webhook-burst)
- [ActiveCampaign webhook payload format](/integrations/activecampaign-to-slack/errors/activecampaign-webhook-payload-format)
- [Calendly webhook delivery delays](/integrations/zapier-to-calendly/errors/calendly-webhook-delivery-delays)
- [ActiveCampaign API Reference](/activecampaign)
- [Slack API Reference](/slack)