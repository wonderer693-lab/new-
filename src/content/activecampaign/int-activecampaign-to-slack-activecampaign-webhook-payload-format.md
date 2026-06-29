---
layout: ../../layouts/IntegrationErrorLayout.astro
title: "ActiveCampaign Webhook Payload Format Varies by Event — Slack Template Breaks"
description: "ActiveCampaign webhook payloads differ by event type: contact payloads use different keys than deal payloads. A single Slack template renders with blank fields when an unexpected event fires. Use separate Zapier Zaps per webhook type with templates matching each schema."
toolA: "activecampaign"
toolB: "slack"
integrationSlug: "activecampaign-to-slack"
errorSlug: "activecampaign-webhook-payload-format"
errorName: "ActiveCampaign webhook payload format"
category: "WEBHOOK"
errorType: "error"
severity: "high"
priority: 2
lastUpdated: "2026-06-25"
lastReviewed: "2026-06-25"
pageType: "integration-error"
author: "API Integration Hub"
keywords:
  - "activecampaign webhook payload per event type"
  - "activecampaign contact vs deal webhook format"
  - "slack template blank from activecampaign webhook"
  - "activecampaign webhook type field missing"
  - "activecampaign webhook schema per event"
  - "slack notification breaks on activecampaign event type"
---

## The Problem

Your Zapier or Make pipeline routes all ActiveCampaign webhooks to one Slack notification template. Contact-created events look fine, but deal-updated notifications arrive with blank fields — `First Name`/`Email` rendered as `null` because the deal payload employeesfields at a different JSON path. Slack teams see half-filled notifications, lose confidence in the integration, and stop reading them.

## Root Cause

- **ActiveCampaign webhooks** include a `type` header (`type` string like `update`, `add`, `deal_add`, etc.) and the body shape varies accordingly.
- **Contact events** (`subscribe`, `update`, `unsubscribe`): payload `data.contact` and `data.contact.email`, `first_name`, `last_name`, `tags`.
- **Deal events** (`deal_add`, `deal_update`): payload `data.deal` with `title`, `value`, `currency`, `group`, `contact`.
- **Custom fields**: included as a flat array `data.contact.fieldValues` on contact events, absent on deal events; deal events nest fields in `data.deal.fields` as `[{"field":"12","value":"..."}]`.
- **Slack template reference**: Zapier/Make templates commonly bind to `1.contact.email` — which works for contact events but renders blank when the bundle is a deal event.

| Event | Top-level key | Sample fields |
|---|---|---|
| `subscribe` | `data.contact` | `email`, `first_name`, `tags` |
| `unsubscribe` | `data.contact` | `email`, ` unsubscribe_reason` |
| `deal_add` | `data.deal` | `title`, `value`, `currency`, `contact` |
| `deal_update` | `data.deal` | same as deal_add |
| `contact_tag_added` | `data.contactTag` | `contact`, `tag` (ids only) |

## How to Detect If You're Affected

1. Inspect a sample of every ActiveCampaign webhook event via middleware. Sign the raw payloads:
   ```bash
   rg 'POST.*acf-webhook' middleware.log | grep '"type":"' | awk -F'"type":"' '{split($2,a,"\""); print a[1]}' | sort -u
   ```
2. Compare Slack message blank-rate per `type`:
   ```python
   by_type = defaultdict(lambda: [0,0])
   for ev in events:
       by_type[ev.type][0] += 1
       if ev.payload.get("email"):
           by_type[ev.type][1] += 1
   ```
   Types with low "email filled" ratio are template mismatches.
3. Symptom spot check: look at recent bot messages from ActiveCampaign webhooks — find ones lacking the expected UI fields (e.g., the `Deal value`).

## Step-by-Step Fix

1. Split each webhook type into its own Zapier Zap or Make scenario:
   - Zap A: trigger `Webhook by Zapier` filtered on `type = subscribe`.
   - Zap B: trigger `Webhook by Zapier` filtered on `type = deal_add`.
   - Zap C: trigger `Webhook by Zapier` filtered on `type = contact_tag_added`.
   Use a Filter step (`Payload.type` equals `type`) before composing the Slack message.
2. Map schema fields explicitly with extraction:
   ```python
   def render(ev):
       t = ev["type"]
       if t.startswith("deal_"):
           d = ev["data"]["deal"]
           return f"Deal *{d['title']}* ({d['currency']} {d['value']}) — {d.get('contact','?')}"
       # contact events
       c = ev["data"]["contact"]
       return f"Contact {c.get('first_name','')} {c.get('email','')} tagged {c.get('tags','')}"
   ```
3. Send to Slack:
   ```bash
   curl -X POST https://slack.com/api/chat.postMessage \
     -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
     -d "{\"channel\":\"#events\",\"text\":\"$MSG_ESCAPED\"}"
   ```
4. Wrong: reuse the contact-payload template for deal events; the email reference is empty. Correct: per-type templated paths.
5. Add a Slack fallback "Could not parse payload of type X — see raw log" as the Slack text when fields are missing, so you receive a notification rather than nothing.

## Prevention

- Maintain an ActiveCampaign webhook schema cheat-sheet for your integration operators — copy stays with the team; new event types are less likely to break the templates unexpectedly.
- Pin webhook topic subscriptions per type at registration time; reject unpartitioned subscription where webhook topic coverage is broad.
- Add a Zapier/Make filter step that explicitly routes each event type to the matching Zap; route unhandled webhook types to a `#integration-warnings` Slack channel.
- Subscribe a monitoring job to all webhook types — track which one produced Slack renders with empty required fields; alert at > 1% blank rate per type.
- Update templates whenever ActiveCampaign adds a new event type (they did add `contact_note_added` in early 2026); subscribe and templatize before going to production.

## Integration-Specific Context

- **Native ActiveCampaign-Slack integration** does not exist — most teams use Zapier or hand-coded endpoints; you are responsible for parsing.
- **Zapier**: use one Zap per event type for clarity; large multi-filter Zaps are prone to bundle-level test failures.
- **Make**: same. Route by event type, then aggregate inside.
- **Custom middleware**: snippet above is the canonical data path.
- **2026 change**: ActiveCampaign now sends `webhook_id` and `attempt` headers alongside payloads; logging these helps reconcile missed events.

## People Also Ask

- **Why do my ActiveCampaign Slack notifications show blank fields?** You're using one template rendered for contact payloads across all webhook types; deal events have a different JSON path, so references like `data.contact.email` render as blank.
- **How do ActiveCampaign webhook payloads vary by event?** Contact events nest under `data.contact`; deal events nest under `data.deal` with `title`, `value`, `currency`, and `contact`; tag events reference only ids in `data.contactTag`.
- **Should I create one Zap for each ActiveCampaign webhook type?** Yes. Each event type has a different spec, and the Slack template path matches better to a single event type per Zap. Add a filter step to the trigger to route correctly.
- **How do I handle unknown ActiveCampaign webhook events in Slack?** Default to a generic "Unknown event type X — raw payload" notification and route to a monitoring channel so you can route new event types promptly.

## Official Documentation

**ActiveCampaign:**
- [API Overview](https://developers.activecampaign.com/reference/overview)
- [Authentication](https://developers.activecampaign.com/reference/authentication)

**Slack:**
- [Web API](https://api.slack.com/web)
- [Block Kit](https://api.slack.com/block-kit)

## Related Errors
- [ActiveCampaign API rate limit on webhook responses](/integrations/activecampaign-to-slack/errors/activecampaign-api-rate-limit-on-webhook-responses)
- [Slack 1 req/sec vs ActiveCampaign webhook burst](/integrations/activecampaign-to-slack/errors/slack-1-req-sec-vs-activecampaign-webhook-burst)
- [Calendly webhook delivery delays](/integrations/zapier-to-calendly/errors/calendly-webhook-delivery-delays)
- [ActiveCampaign API Reference](/activecampaign)
- [Slack API Reference](/slack)