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


<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** ActiveCampaign webhook data format doesn't match what Slack expects. Contact events use different JSON keys than deal events, so your Slack template shows blank fields.

**The fix:**
1. Check which ActiveCampaign event type is firing (contact vs deal vs tag)
2. Add a JSON parser module in Make or a Formatter step in Zapier to detect the event type
3. Create separate Slack message templates for each event type
4. Route each event type to its own Zap or scenario with matching field mappings

**Copy-paste this code** (if you're using a code editor):
```python
def render(event):
    t = event["type"]
    if t.startswith("deal_"):
        d = event["data"]["deal"]
        return f"Deal *{d['title']}* ({d['currency']} {d['value']})"
    c = event["data"]["contact"]
    return f"Contact {c.get('first_name', '')} - {c.get('email', '')}" 
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code workaround](#no-code-workaround).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm integrating ActiveCampaign with Slack and my Slack notifications show blank fields. The ActiveCampaign webhook sends different JSON formats for contact events vs deal events, and my single Slack template can't handle both. How do I parse each event type and render the correct fields in Slack?

**What to expect:** The AI should help you create separate Slack templates per ActiveCampaign event type and add routing logic.

**If it doesn't work**, add this follow-up:
> I split my Zaps by event type but some ActiveCampaign webhooks still arrive with unexpected fields. How do I add a fallback Slack message for unknown event types?

**Best AI tools for this:** ChatGPT-4 (good at step-by-step UI navigation), Claude (good at explaining API concepts)

</div>

## No-Code Workaround <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to debug this? Here's how to handle ActiveCampaign webhook parsing for Slack in other automation tools:

### Zapier
1. Create separate Zaps for each ActiveCampaign event type (contact, deal, tag)
2. Add a 'Filter' step after the webhook trigger to route by event type
3. Use Zapier's Formatter step to extract the correct fields before sending to Slack

### Make (Integromat)
1. Create separate scenarios for each ActiveCampaign event type
2. Add a JSON 'Parse' module after the webhook trigger to extract the event type
3. Use a 'Router' module to send each event type to the correct Slack template

### n8n
1. Create a webhook trigger node and add a 'Switch' node to route by event type
2. Add a 'Set' node per branch to map the correct fields for each event type
3. Connect each branch to a Slack node with the matching message template

### Power Automate
1. Use 'When an HTTP request is received' trigger with a JSON schema
2. Add a 'Condition' action to check the event type field
3. Route each branch to a different Slack message template

**Which tool should you use?** Zapier is the easiest -- create one Zap per event type with a Filter step, so each Slack template only sees the fields it expects.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these:

- Slack notifications from ActiveCampaign show blank or null fields for some events
- Contact-created notifications look fine but deal-updated show empty values
- Your Slack template renders data.contact.email as blank on deal events
- ActiveCampaign webhook logs show successful delivery but Slack messages are incomplete

**What it means in plain English:** ActiveCampaign sends different JSON structures for different event types. Your Slack template was built for one structure and breaks when a different event type arrives.

**Most common cause:** Using a single Slack message template for all ActiveCampaign webhook event types instead of creating per-type templates.

</div>

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