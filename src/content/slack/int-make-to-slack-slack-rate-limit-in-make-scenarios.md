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


<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Make scenarios hit Slack rate limits when looping over multiple items. The first Slack message succeeds but the rest return 429 'ratelimited' because Make fires all iterations instantly.

**The fix:**
1. Add a 'Sleep' module (1 second) between Slack module iterations in Make
2. Use Make's 'Array Aggregator' to combine items into one summary Slack message
3. Add a 'Throttle' module before the Slack module to pace at 1 request/second
4. Add an error handler on the Slack module to catch 429 and retry

**Copy-paste this code** (if you're using a code editor):
```python
# In Make, add these modules in order:
# 1. Iterator (over your items)
# 2. Sleep module: 1 second delay
# 3. Slack module: Send Message
#
# Or use Array Aggregator instead:
# 1. Iterator -> Array Aggregator -> single Slack message
# Text: {{forEach(array; item; "- " & item.name)}}
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code workaround](#no-code-workaround).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm integrating Make with Slack and my scenario fails after the first message when looping over multiple items. Slack returns 429 'ratelimited' because Make fires all iterations at once. How do I add a throttle or aggregate messages to fix this?

**What to expect:** The AI should walk you through adding Make's Throttle/Sleep module or using Array Aggregator for summary messages.

**If it doesn't work**, add this follow-up:
> I added a Throttle module but the scenario is too slow for 100+ items. Can I aggregate items into batches of 10 instead?

**Best AI tools for this:** ChatGPT-4 (good at step-by-step UI navigation), Claude (good at explaining API concepts)

</div>

## No-Code Workaround <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to debug this? Here's how to handle Slack rate limits in Make scenarios using other tools:

### Zapier
1. Use Zapier's Slack action -- it auto-paces messages through Zapier's internal queue
2. Add a 'Delay by Zapier' step (1 second) between Slack actions
3. Aggregate items into a single summary message using Zapier's 'Line Items' feature

### Make (Integromat)
1. Add Make's 'Throttle' module (1 second delay) before the Slack module
2. Or use 'Array Aggregator' to combine all items into one Slack message
3. Add a 'Break' error handler on the Slack module to catch and retry 429 errors

### n8n
1. Add a 'Wait' node (1 second) between Slack node executions
2. Use an 'Item Lists' node to aggregate items before the Slack node
3. Enable 'Retry on Fail' with 3 retries and 2-second intervals

### Power Automate
1. Add a 'Delay' action (1 second) before each Slack message
2. Use 'Apply to each' with sequential processing
3. Aggregate items into a single message using 'Compose' with a join expression

**Which tool should you use?** Make's Array Aggregator is the best fix -- it turns 50 Slack messages into 1 summary message, completely avoiding the rate limit.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these:

- Make scenario shows red error lines after the first Slack message
- Slack returns 429 'ratelimited' with retry_after: 1 for most iterations
- Only the first message in a loop arrives in Slack; the rest fail
- Make history shows HTTP 429 errors on the Slack module

**What it means in plain English:** Make's Iterator fires all bundles simultaneously, and Slack only allows 1 message per second. The second through last messages get rate-limited.

**Most common cause:** Running a Make scenario loop that posts to Slack without a Throttle/Sleep module or message aggregation.

</div>

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