---
layout: ../../layouts/IntegrationErrorLayout.astro
title: "Slack Rate Limit in Make Scenarios — 429 After First Iteration on Bulk Loops"
description: "Make (Integromat) scenario loops over 50 items and posts a Slack message per item, hitting Slack's 1 req/sec per method limit. The scenario fails after the first iteration with HTTP 429 and a Retry-After header. Fix with a Throttle module or message aggregation."
toolA: "make"
toolB: "slack"
integrationSlug: "make-to-slack"
errorSlug: "slack-rate-limit-in-make-scenarios"
errorName: "Slack rate limit in Make scenarios"
category: "RATE_LIMIT"
errorType: "error"
severity: "high"
priority: 2
lastUpdated: "2026-05-12"
lastReviewed: "2026-05-12"
pageType: "integration-error"
author: "API Integration Hub"
keywords:
  - "make slack scenario 429 rate limit"
  - "slack 1 request per second per method"
  - "make integromat slack throttle module"
  - "make slack chat.postmessage retry after"
  - "make bulk loop slack rate limit fix"
  - "slack web api tier 3 limit 2026"
---

## The Problem

A Make scenario iterates 50 fresh rows from a CRM and tries to notify a Slack channel each row, but only the first message lands; the remainder error out with `chat.postMessage` returning HTTP 429 `{"error":"ratelimited"}`. Make flags those executions as failed, so end users see 49 red execution lines per run plus an aggrieved Slack team pinging on real-time alerts they missed.

## Root Cause

Slack's Web API applies **tiered rate limits per method**, not globally. `chat.postMessage` is **Tier 3**: ~1 request per second per method per workspace, enforced on a rolling short window. Other Slack endpoints have different tiers, so total workspace capacity varies.

| Slack method | Tier | Limit |
|---|---|---|
| `chat.postMessage` | 3 | ~1 req/s per workspace |
| `conversations.list` | 2 | ~20/min tier (lower) |
| `users.lookupByEmail` | 4 | ~100/min |
| `auth.test` | 1 | ~100/min |

Make runs a scenario iteration per bundle: each iteration is its own HTTP call to Slack, with no inter-bundle sleep. On a 50-item stack Make fires all 50 inside ~1 s, and Slack returns `ratelimited` with a `Retry-After` (whole seconds) for 49 of them. Make's default Slack module does **not** queue or throttle; it surfaces every retry-after as a red execution unless you add error handling.

## How to Detect If You're Affected

1. Open Make → History and filter for the Slack module's `429` runs — typical signature:
   ```
   {"ok":false,"error":"ratelimited","retry_after":1}
   ```
2. Slack admin UI → Apps → Rate-limit headers — check `X-Envoy-Decorator-Rate-Limit` instruments — usually zero remaining during the burst.
3. Quick reproduction:
   ```bash
   for i in $(seq 1 50); do
     curl -s -X POST https://slack.com/api/chat.postMessage \
       -H "Authorization: Bearer $TOKEN" \
       -H "Content-Type: application/json" \
       -d "{\"channel\":\"$CH\",\"text\":\"burst $i\"}" | jq -r '.error'
   done
   ```
   Expect `ratelimited` on iterations 2–50.

## Step-by-Step Fix

1. Insert the **Throttle** module between the iterator and the Slack module:
   - Type: `Delay`
   - Value: `1` second
   - Mode: `Constant` — applies to every bundle.
2. Aggregate bundles when the content is similar — send one summary message instead of 50:
   - Add the **Array Aggregator** module between Iterator and Slack.
   - In the Slack module, format text as a single bulleted list built from `{{5.array}}` elements:
     ```
     {{forEach(5.array; item; "- " & item.name & " : " & item.value)}}
     ```
3. For custom middleware bypassing Make, gate pace with a token bucket:
   ```python
   import time
   def slack_post(session, channel, text):
       while True:
           r = session.post("https://slack.com/api/chat.postMessage",
              json={"channel": channel, "text": text})
           if r.json().get("error") != "ratelimited":
               return r
           time.sleep(int(r.json().get("retry_after", 1)))
   ```
4. Wrong: catching 429 as fatal. Correct: treat `ratelimited` as retryable (`retry_after` is whole seconds) and route to a Break + continue handler in Make.

## Prevention

- Default Slack notifications to aggregation (one digest per scenario) and only switch to per-item mode when alerts are truly time-sensitive.
- Reserve `chat.postMessage` for the message; do not call `auth.test` or `users.lookupByEmail` inside the loop — these burn the lower-tier limits and cascade.
- Cache Slack user/channel ID lookups to `users.list` in your scenario variables; one daily cache refresh is enough.
- Set the Make scenario's "Max cycles" to a value consistent with Slack's bucket; never leave it unbounded.
- Monitor Slack dashboard → Analytics → API calls; alert when 4xx within a 5-minute bucket > 10 (early sign of throttling).

## Integration-Specific Context

- **Native Slack-isms inside Make**: Make's Slack module does not auto-throttle; you must add the Throttle module — many users find out only after their first bulk CRM run.
- **Zapier Slack app**: Zapier's Slack integration does buffer Slack calls on its own worker, masking the issue until you exceed Zapier's per-task delay — but it isn't documented as live throttling in 2026.
- **Custom middleware**: own the credit bucket; Slack's `Retry-After` is the source of truth, not the manual tier table.
- **2026 change**: Slack tightened Tier 3 enforcement from "1/s average" to hard "1/s peak per workspace" — bursts that previously passed now 429 even under their old monthly usage.

## People Also Ask

- **What's Slack's `chat.postMessage` rate limit?** Tier 3 — about 1 request per second, per workspace. Slack returns `ratelimited` with `retry_after` (seconds) when you exceed it.
- **Why does my Make Slack scenario fail after the first message?** The Iterator fires every bundle simultaneously and Slack rejects the second through last as `ratelimited`. Add a 1-second Throttle module or aggregate the bundles.
- **Is `retry_after` in seconds or milliseconds?** Seconds (whole integer). Sleep that many whole seconds before retrying.
- **Can I disable Slack's per-method limit?** No. You must throttle clientside and respect the `retry_after` returned.

## Official Documentation

**Make (Integromat):**
- [API Docs](https://www.make.com/en/api-documentation)
- [HTTP Module](https://www.make.com/en/help/modules/http)

**Slack:**
- [API Docs](https://api.slack.com/)
- [Web API](https://api.slack.com/web)
- [Rate Limits](https://api.slack.com/docs/rate-limits)

## Related Errors
- [Slack rate limit (1 per second per method) — HubSpot ↔ Slack](/integrations/hubspot-to-slack/errors/slack-rate-limit-(1-per-second-per-method))
- [Slack 1 req/sec vs ActiveCampaign webhook burst](/integrations/activecampaign-to-slack/errors/slack-1-req-sec-vs-activecampaign-webhook-burst)
- [Make Slack module OAuth re-authentication](/integrations/make-to-slack/errors/make-slack-module-oauth-re-authentication)
- [Make API Reference](/make)
- [Slack API Reference](/slack)