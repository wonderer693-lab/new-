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


<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** HubSpot data doesn't format correctly in Slack messages. Deal amounts show as raw numbers, dates appear as ISO strings, and text runs together without styling.

**The fix:**
1. Use Slack Block Kit instead of plain text for structured deal notifications
2. Format currency server-side before sending (e.g., $1,000,000 instead of 1000000)
3. Use Slack's mrkdwn syntax: *bold* (not **bold**), _italic_ (not *italic*)
4. Build a reusable message template with header, fields, and context blocks

**Copy-paste this code** (if you're using a code editor):
```python
deal_card = {
    "channel": "#deals",
    "blocks": [
        {"type": "header", "text": {"type": "plain_text", "text": f"New deal: {deal_name}"}},
        {"type": "section", "fields": [
            {"type": "mrkdwn", "text": f"*Amount:* ${amount:,.0f}"},
            {"type": "mrkdwn", "text": f"*Stage:* {stage}"}
        ]}
    ]
}
print(json.dumps(deal_card, indent=2))
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code workaround](#no-code-workaround).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm integrating HubSpot with Slack and deal notifications look like walls of plain text. Amounts show as raw numbers (1000000 instead of $1,000,000), dates are ISO strings, and there's no formatting. How do I use Slack Block Kit to create properly formatted deal cards?

**What to expect:** The AI should help you build Block Kit deal card templates with proper currency formatting and mrkdwn styling.

**If it doesn't work**, add this follow-up:
> I built a Block Kit template but HubSpot product names with asterisks break the formatting. How do I escape mrkdwn special characters?

**Best AI tools for this:** ChatGPT-4 (good at step-by-step UI navigation), Claude (good at explaining API concepts)

</div>

## No-Code Workaround <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to debug this? Here's how to format HubSpot-Slack notifications in other automation tools:

### Zapier
1. Use Zapier's 'Formatter' step to format currency and dates before the Slack action
2. Use Zapier's 'Send Block Kit Message' action with a pre-built JSON template
3. Test the message in Slack's Block Kit Builder before deploying

### Make (Integromat)
1. Use Make's 'Set Variable' module to build a Block Kit JSON string
2. Format currency and dates in Make before the Slack module
3. Send via Make's HTTP module with the Block Kit JSON payload

### n8n
1. Use a 'Set' node to format currency and dates from HubSpot
2. Build the Block Kit JSON in a 'Code' node
3. Send via the Slack node with the formatted blocks

### Power Automate
1. Use a 'Compose' action to format currency and dates
2. Build the Block Kit JSON in the compose output
3. Send via the Slack connector with the composed payload

**Which tool should you use?** Zapier is the easiest -- its Formatter step handles currency and date formatting, and the Block Kit editor catches JSON errors at setup time.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these:

- HubSpot deal notifications show raw numbers instead of formatted currency
- Dates appear as ISO timestamps (2026-06-26T18:43:00) instead of readable dates
- Slack messages look like walls of plain text with no structure
- Sales reps ignore notifications because they're hard to read

**What it means in plain English:** HubSpot field values are being sent as raw text to Slack without formatting. Slack has no built-in currency or date formatter -- you must format values before sending.

**Most common cause:** Piping HubSpot field values directly into Slack's text parameter without using Block Kit or server-side formatting.

</div>

## The Problem

HubSpot deal updates pushed to Slack look like walls of plain text: amounts show as `1000000` instead of `$1,000,000`, dates bleed through as raw ISO strings, and line breaks collapse so two deals blur into one unreadable line. Recipients ignore these notifications, which defeats the point of the integration.

See all [Slack API errors](/slack/) or [HubSpot API errors](/hubspot/) for more troubleshooting. Related: [Slack not_in_channel](/slack/errors/not_in_channel), [Slack rate_limited](/slack/errors/rate_limited).

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