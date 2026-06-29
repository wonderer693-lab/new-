---
layout: ../../layouts/IntegrationErrorLayout.astro
title: "HubSpot to Slack Message Formatting Issues — Plain Text Deals Look Broken"
description: "HubSpot deal fields pushed to Slack as raw text arrive unstyled and with mishandled currency, dates, and line breaks. Fix with Slack Block Kit section blocks, mrkdwn formatting, and field-pair layout for currency and stage fields."
toolA: "hubspot"
toolB: "slack"
integrationSlug: "hubspot-to-slack"
errorSlug: "message-formatting-issues"
errorName: "Message formatting issues"
category: "FORMATTING"
errorType: "error"
severity: "high"
priority: 2
lastUpdated: "2026-05-06"
lastReviewed: "2026-05-06"
pageType: "integration-error"
author: "API Integration Hub"
keywords:
  - "hubspot to slack block kit formatting"
  - "slack mrkdwn currency deal amount"
  - "slack chat.postmessage blocks array wrong format"
  - "hubspot deal amount plain text slack"
  - "slack section block field pairs deal card"
  - "slack markdown bold curly quotes hubspot"
---

## The Problem

HubSpot deal updates pushed to Slack look like walls of plain text: amounts show as `1000000` instead of `$1,000,000`, dates bleed through as raw ISO strings, and line breaks collapse so two deals blur into one unreadable line. Recipients ignore these notifications, which defeats the point of the integration.

## Root Cause

- **Slack renders text via mrkdwn**, not CommonMark. Use `*bold*` (not `**bold**`) and `_italic_` (not `*italic*`). HubSpot field values piped straight in are not mrkdwn-escaped, so `*` characters from product names break formatting.
- **Currency**: HubSpot `amount` is a number in HubSpot's API (`1000000`); Slack has no currency primitive, so it prints as-is unless you format it server-side.
- **Plain text vs. blocks**: `text` parameter renders as a single line (newlines in `text` collapse unless `mrkdwn` sections are used). To get a structured "deal card", build the `blocks` array with `section` blocks.
- **Curly quotes and unicode**: HubSpot exports smart quotes; Slack mrkdwn handles them but tighter escaping (e.g., `<`, `>`, `&`) is needed to avoid suppression.

| Goal | Wrong | Correct |
|---|---|---|
| Bold label | `**Deal:**` | `*Deal:*` |
| Currency | `Deal amount: {{amount}}` | `*Amount:* ${{formatNumber(amount, 2, "en-US")}}` |
| Multi-line | `\n` in `text` | `section` blocks per row |
| Status pill | `Stage: closedwon` | `` `Stage: closedwon` `` (inline code) |

## How to Detect If You're Affected

1. Compose a tip message body (`https://app.slack.com/block-kit-builder`) and visually compare to your live messages — if amounts and dates render literally with no styling, you are unformatted.
2. Inspect actual posted payload:
   ```bash
   rg '"text":"[^b]' middleware.log | head
   ```
   A high count of `text`-only posts confirms the issue.
3. Use Slack's `chat.postMessage` API response — `warnings` indicates mrkdwn escapes triggered unexpectedly:
   ```json
   {"ok": true, "warnings": "meet_suppression"}
   ```
4. Sanity-check a few days of notifications — do sales reps click and act on them? Low engagement + wall-of-text = formatting problem.

## Step-by-Step Fix

1. Build a Block Kit payload with a header and a fields array:
   ```json
   {
     "channel": "tradeboard",
     "blocks": [
       {"type":"header","text":{"type":"plain_text","text":"New deal: ACME Corp"}},
       {"type":"section","fields":[
         {"type":"mrkdwn","text":"*Amount:* $1,000,000"},
         {"type":"mrkdwn","text":"*Stage:* closedwon"},
         {"type":"mrkdwn","text":"*Owner:* Jane Doe"},
         {"type":"mrkdwn","text":"*Close date:* 2026-06-29"}
       ]},
       {"type":"context","elements":[{"type":"mrkdwn","text":"Synced from HubSpot"}]}
     ]
   }
   ```
2. Send with curl:
   ```bash
   curl -s -X POST https://slack.com/api/chat.postMessage \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d @deal_card.json | jq .
   ```
3. Server-side currency formatting:
   ```python
   from babel.numbers import format_currency
   amount = format_currency(deal["amount"], "USD", locale="en_US")
   ```
4. Wrong: build Slack payload by string-concatenating HubSpot fields. Correct: define a JSON template and use a templating engine (Jinja) so escaping is automatic.
5. Validate the blocks with the Block Kit Builder before deploying — Slack renders invalid blocks as `validation_error`.

## Prevention

- Standardize one "deal card" Slack template across all HubSpot-to-Slack flows; never inline-format per Zap or per scenario.
- Escape mrkdwn special characters (`*`, `_`, `` ` ``, `~`) on values coming from HubSpot free-text fields so formatting doesn't break when a customer name contains `*`.
- Format currency and dates in your middleware **server-side** rather than relying on Slack's display to interpret integers.
- Pair fields using Slack's 2-column layout (`fields` array with two entries) so amounts and stage stay aligned.
- Roll out a smoke test notification to an internal channel daily to catch formatting regressions introduced by HubSpot field-type changes.

## Integration-Specific Context

- **Native HubSpot-Slack connector**: produces decent block-based cards but uses HubSpot's own template — limited customization for currency locale.
- **Zapier Slack action** ("Send Block Kit Message"): provides a JSON editor; use the formatter step before it to ensure currency is a string.
- **Make Slack module**: ships a JSON module — easier to paste a raw Block Kit JSON payload than riff through Make's structured module.
- **Custom middleware**: full control — always validate output against Slack's schema before deploying.
- **2026 change**: Slack deprecated `mrkdwn: true` block-level flag in favor of per-element `type: "mrkdwn"` — older templates still work but emit `warnings`.

## People Also Ask

- **How do I format HubSpot deal amount as currency in Slack?** Format it server-side before calling `chat.postMessage`. Pass a string like `$1,000,000` in the `blocks` `mrkdwn` text — Slack has no native currency formatter.
- **Why does my Slack message show `**Deal:**` literally?** Slack uses mrkdwn, not CommonMark. Single `*` for bold; `**double asterisks**` render literally.
- **Should I use `text` or `blocks` in `chat.postMessage`?** Use `blocks` for structured content; legacy `text` renders as one unstyled paragraph and ignores newlines under modern Slack apps.
- **How do I make HubSpot-Slack notifications look like cards?** Build a `header`, a `section` with paired `fields`, and a `context` block-footer for the "synced from HubSpot" tag.

## Official Documentation

**HubSpot:**
- [API Overview](https://developers.hubspot.com/docs/api/overview)
- [CRM API](https://developers.hubspot.com/docs/api/crm/overview)

**Slack:**
- [Web API](https://api.slack.com/web)
- [Block Kit](https://api.slack.com/block-kit)

## Related Errors
- [Slack rate limit (1 per second per method) — HubSpot to Slack](/integrations/hubspot-to-slack/errors/slack-rate-limit-(1-per-second-per-method))
- [Bot not in channel — HubSpot to Slack](/integrations/hubspot-to-slack/errors/bot-not-in-channel)
- [Block Kit too complex for Make's JSON module](/integrations/make-to-slack/errors/block-kit-too-complex-for-make's-json-module)
- [HubSpot API Reference](/hubspot)
- [Slack API Reference](/slack)