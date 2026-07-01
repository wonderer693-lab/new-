---
layout: ../../layouts/IntegrationErrorLayout.astro
title: "Block Kit Too Complex for Make's JSON Module — Slack Messages Fail to Send"
description: "Make's Slack JSON module throws schema errors on nested Block Kit arrays. A missing comma or bracket breaks the entire Slack message. Build the JSON as a templated variable string and validate with the Block Kit Builder."
toolA: "make"
toolB: "slack"
integrationSlug: "make-to-slack"
errorSlug: "block-kit-too-complex-for-make's-json-module"
errorName: "Block Kit too complex for Make's JSON module"
category: "FORMATTING"
errorType: "error"
severity: "high"
priority: 2
lastUpdated: "2026-04-20"
lastReviewed: "2026-04-20"
pageType: "integration-error"
author: "API Integration Hub"
keywords:
  - "make slack json module block kit error"
  - "make block kit invalid_blocks error"
  - "slack chat.postmessage make template blocks"
  - "make slack json schema validation"
  - "make set variable block kit json"
  - "make slack complex blocks module fail"
---


<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Block Kit JSON is too complex for Make's structured Slack module. A missing comma or bracket in the nested JSON breaks the entire Slack message with an 'invalid_blocks' error.

**The fix:**
1. Build the Block Kit JSON as a plain text string using Make's 'Set Variable' module
2. Escape dynamic values to prevent unescaped quotes from breaking the JSON
3. Validate the rendered JSON in Slack's Block Kit Builder before deploying
4. Use Make's HTTP module with 'Body type: JSON' instead of the structured Slack module

**Copy-paste this code** (if you're using a code editor):
```python
blocks_json = '{{"blocks": [{{"type": "section", "text": {{"type": "mrkdwn", "text": "*{name}* - {amount}"}}}}]}}'.format(
    name=deal_name.replace('"', '\\"'),
    amount=deal_amount
)
print(blocks_json)  # Paste into Block Kit Builder to validate
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code workaround](#no-code-workaround).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm integrating Make with Slack and complex Block Kit messages fail with 'invalid_blocks' errors. Make's structured Slack module can't handle deeply nested JSON -- a single missing comma breaks everything. How do I build Block Kit messages as a text string and validate them before sending?

**What to expect:** The AI should help you build Block Kit JSON as a templated string and validate it with Slack's Block Kit Builder.

**If it doesn't work**, add this follow-up:
> I switched to a text string but dynamic values with quotes still break the JSON. How do I escape special characters in Make variables?

**Best AI tools for this:** ChatGPT-4 (good at step-by-step UI navigation), Claude (good at explaining API concepts)

</div>

## No-Code Workaround <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to debug this? Here's how to send complex Slack messages from Make using other tools:

### Zapier
1. Use Zapier's 'Send Block Kit Message' action -- it has a JSON editor that catches syntax errors
2. Build the JSON in a Zapier 'Formatter' step before the Slack action
3. Validate the JSON in Slack's Block Kit Builder before deploying the Zap

### Make (Integromat)
1. Build the Block Kit JSON as a string in Make's 'Set Variable' module
2. Use Make's HTTP module (not the Slack module) to send the JSON -- set Body type to JSON
3. Keep messages under 15 blocks to reduce complexity

### n8n
1. Use a 'Set' node to build the Block Kit JSON as a string
2. Send via the Slack node with the JSON string in the 'blocks' field
3. Add error handling to catch invalid_blocks and send a plain-text fallback

### Power Automate
1. Use a 'Compose' action to build the Block Kit JSON string
2. Send via the Slack connector with the composed JSON
3. Add a condition to check for errors and send a plain-text fallback

**Which tool should you use?** Zapier is the easiest -- its Block Kit message editor catches JSON syntax errors at setup time, before they reach production.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these:

- Slack returns 'invalid_blocks' error for Make scenario messages
- Complex Block Kit layouts with sections, fields, and actions fail to send
- Simple text messages work fine but formatted messages break
- Make scenario history shows the Slack module failing on every iteration

**What it means in plain English:** Make's structured Slack module tries to build nested JSON through UI fields, making it easy to introduce syntax errors. Slack rejects the entire message when the JSON is malformed.

**Most common cause:** Building complex Block Kit JSON inside Make's structured module fields instead of composing it as a validated text string.

</div>

## The Problem

A Make scenario builds a Slack message with nested Block Kit (Sections containing `mrkdwn`, accessory images, conditional `actions`) using Make's structured Slack module. Each iteration the scenario fails with `invalid_blocks` from Slack and the entire Slack payload is discarded. The Make UI makes it easy to drop a comma or bracket in the deeply nested JSON, and the user-friendliest browsing field doesn't surface the syntax error until a real Slack call attempts to render it.

## Root Cause

- **Make's Slack "Send a Message" module** lets you build the `blocks` array through structured fields. Behind the scenes it concatenates your values to JSON; an unescaped quote inside a variable yields malformed JSON.
- **Slack `invalid_blocks` validation** is strict and returns with no line number; pinpointing the broken element in a Make scenario is impossible.
- **Block Kit complexity cap**: Slack enforces a 50-block limit per message and 3,000-char payload limit. Make's structured module does not pre-validate, so over-built messages fail.
- **Template partial rendering**: Make functions like `={{mapper(...)}}` return unescaped text values; values from Slack variables can replace JSON tokens with raw text that breaks the structure.

| Failure mode | Cause returned by Slack |
|---|---|
| Single missing comma | `invalid_blocks` |
| Unescaped `"` in field | `invalid_blocks` |
| > 50 blocks in payload | `invalid_blocks` with `too_many_blocks` |
| Empty `text` element | `invalid_blocks` with `missing_field:text` |

## How to Detect If You're Affected

1. Look at Make's scenario history: each iteration contains an error block from the Slack module with body `{"ok":false,"error":"invalid_blocks"}`.
2. Open Slack's Block Kit Tester (`https://app.slack.com/block-kit-builder`), paste the rendered JSON from a logged Slack payload; the tester shows the precise failing element.
3. Capture the outgoing payload with a Webhook-response Make module or logger:
   ```bash
   rg '"error":"invalid_blocks"' logs/make-slack-request.log
   ```
4. Symptom: messages with simple text pass; complex Block Kit layouts fail.

## Step-by-Step Fix

1. Build blocks JSON as a single templated string in Make before the Slack module, using Make's "Set Variable" module:
   ```text
   {{{
     "blocks": [
       {{#each deals}}
       {"type":"section","text":{"type":"mrkdwn","text":"*{{this.name}}* — {{this.amount}}"}}{{#unless @last}},{{/unless}}
       {{/each}}
     ]
   }}}
   ```
   Navigate to your Slack module and use `"blocks": {{5.json_string}}` directly via the raw HTTP "Make a custom API call" module if the structured Slak module misbehaves.
2. Validate the rendered JSON via Block Kit Builder before deploying the production scenario.
3. If using the Make HTTP module, set `Body type` to `JSON` and pass the JSON string:
   ```bash
   curl -s -X POST https://slack.com/api/chat.postMessage \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d @deal_card.json | jq .
   ```
4. Wrong: Build the entire nested structure inside the Make Slack module's structured fields. Correct: Compose JSON with the "Set Multiple Variables" + "Compose a string" approach for safer escaping.
5. Escape variables Make-side: wrap dynamic values in `{{replace(5.name; "\""; "\\\"")}}` to neutralize embedded quotes.

## Prevention

- Keep Block Kit payloads under 15 blocks: anything deeper risks schema complexity and brevity is friendlier to mobile Slack users.
- Run every release through the Slack Block Kit Builder's "Validate" button before pushing a scenario to production.
- Keep a "golden payload" template JSON under version control; use `jq` to diff new versions against the gold standard before publishing.
- Add a smoke-test Hack: per scenario run, send a `POST` to a smoke channel with the same blocks as production; the smoke-test failure alerts before end users notice.
- Document each dynamic field's required JSON format and escaping in your team's Make scenario documentation; many invalid_blocks errors come from inheriting scenarios without documentation.

## Integration-Specific Context

- **Native Slack app**: no Block Kit JSON required — but you forfeit the rich layout control.
- **Zapier Slack "Send Block Kit Message"**: provides a JSON editor in the action setup, which catches syntax errors at task creation time more reliably than Make.
- **Make (Integromat)**: see the templated-JSON-string workaround above; this is the most resilient Make pattern for complex Block Kit.
- **Custom middleware**: use a JSON serializer (`json.Marshal` in Go, `JObject` in JS, `json.dumps` in Python) — never hand-build JSON by string concatenation.
- **2026 change**: Slack now imposes a single overall 50-block limit per message (previously per section type) — re-tune any grandfathered layouts that threaded across more blocks.

## People Also Ask

- **Why does Make throw `invalid_blocks` when sending Slack messages?** Make-built structured Block Kit JSON has malformed values (missing commas, unquoted strings, > 50 blocks). Slack rejects the entire payload via `invalid_blocks`.
- **How do I send complex Block Kit messages from Make without errors?** Build the JSON as a templated string via the "Set Variable" module, validate it in Slack's Block Kit Builder, then send via Make's HTTP module setting `Body type: JSON`.
- **What's the Slack block limit per message?** A single message can contain up to 50 blocks total. Make does not pre-validate; you must enforce this yourself.
- **Does Slack Block Kit support `if`/`else` in JSON?** No — branching happens client-side; conditionally include or omit blocks via Make or middleware logic before the API call.

## Official Documentation

**Make (Integromat):**
- [API Docs](https://www.make.com/en/api-documentation)
- [HTTP Module](https://www.make.com/en/help/modules/http)

**Slack:**
- [API Docs](https://api.slack.com/)
- [Block Kit](https://api.slack.com/block-kit)

## Related Errors
- [HubSpot to Slack message formatting issues](/integrations/hubspot-to-slack/errors/message-formatting-issues)
- [Slack rate limit in Make scenarios](/integrations/make-to-slack/errors/slack-rate-limit-in-make-scenarios)
- [Make Slack module OAuth re-authentication](/integrations/make-to-slack/errors/make-slack-module-oauth-re-authentication)
- [Make API Reference](/make)
- [Slack API Reference](/slack)