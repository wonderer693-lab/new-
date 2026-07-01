---
layout: ../../layouts/IntegrationErrorLayout.astro
title: "Calendly Webhook Verification Header Missing — Zapier Custom Trigger Drops Events"
description: "Calendly webhook payload includes a Calendly-Webhook-Signature header required for verification. Zapier's built-in Calendly trigger validates it; the custom 'Webhooks by Zapier' trigger does not, so events arrive untrusted and silently dropped."
toolA: "zapier"
toolB: "calendly"
integrationSlug: "zapier-to-calendly"
errorSlug: "calendly-webhook-verification-header-missing"
errorName: "Calendly webhook verification header missing"
category: "WEBHOOK"
errorType: "error"
severity: "high"
priority: 2
lastUpdated: "2026-06-19"
lastReviewed: "2026-06-19"
pageType: "integration-error"
author: "API Integration Hub"
keywords:
  - "calendly webhook signature header verify"
  - "zapier webhooks by zapier calendly signature"
  - "calendly webhook signing secret required"
  - "calendly webhook verification missing header"
  - "calendly hmac sha256 webhook signature"
  - "calendly webhook payload verification zapier"
---


<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Calendly webhook verification fails in Zapier because the generic 'Webhooks by Zapier' trigger doesn't validate the Calendly-Webhook-Signature header. Events arrive untrusted and may be silently dropped.

**The fix:**
1. Switch to Zapier's official Calendly app trigger -- it verifies signatures automatically
2. If you must use 'Webhooks by Zapier', add a 'Run JavaScript' step to verify the HMAC signature
3. Get your webhook signing key from Calendly: Integrations & Apps > API and Webhooks
4. Reject webhooks with invalid or stale signatures (older than 3 minutes)

**Copy-paste this code** (if you're using a code editor):
```python
const crypto = require("crypto");
const [t, v1] = input.headers["calendly-webhook-signature"]
    .split(",").map(p => p.split("=")[1]);
const hmac = crypto.createHmac("sha256", SIGNING_KEY)
    .update(`${t}.${input.rawBody}`).digest("hex");
if (hmac !== v1) throw new Error("Bad signature");
return { verified: true };
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code workaround](#no-code-workaround).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm integrating Zapier with Calendly and webhook events are arriving unverified. I'm using 'Webhooks by Zapier' as the trigger and it doesn't check the Calendly-Webhook-Signature header. How do I verify the HMAC signature to ensure webhooks are authentic?

**What to expect:** The AI should walk you through verifying Calendly's HMAC-SHA256 signature in a Zapier code step, or switching to the official Calendly trigger.

**If it doesn't work**, add this follow-up:
> I added signature verification but Calendly is still retrying events. Could the issue be that I'm returning 200 for invalid signatures instead of 401?

**Best AI tools for this:** ChatGPT-4 (good at step-by-step UI navigation), Claude (good at explaining API concepts)

</div>

## No-Code Workaround <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to debug this? Here's how to handle Calendly webhook verification in other automation tools:

### Zapier
1. Use Zapier's native Calendly trigger ('Invitee Created') -- it verifies signatures automatically
2. Avoid 'Webhooks by Zapier' for Calendly unless you add a JavaScript verification step
3. Store the signing key in Zapier's environment, not in the Zap's visible fields

### Make (Integromat)
1. Use Make's official Calendly module which handles verification
2. If using a custom webhook, add a 'Hash (HMAC)' module to compute and compare signatures
3. Set the signing secret in a Make Data Store or key management module

### n8n
1. Create a Webhook trigger node and add a 'Crypto' node to verify HMAC-SHA256
2. Compare the computed hash with the Calendly-Webhook-Signature header
3. Return 401 for invalid signatures and 200 for valid ones

### Power Automate
1. Use 'When an HTTP request is received' trigger
2. Add a 'Compose' action to compute HMAC-SHA256 of the body with the signing key
3. Add a 'Condition' to compare the computed hash with the header value

**Which tool should you use?** Zapier's native Calendly trigger is the easiest -- it handles signature verification automatically without any code.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these:

- Calendly webhook events arrive in Zapier but are marked as unverified
- Calendly's webhook log shows retries with 'not verified' or '500' status
- Zapier received fewer events than Calendly reports sending
- Calendly pauses the webhook integration after 5 consecutive unverified responses

**What it means in plain English:** Calendly signs every webhook with an HMAC-SHA256 header. Your Zapier trigger receives the data but doesn't verify the signature, so Calendly considers the delivery unverified and may pause the integration.

**Most common cause:** Using 'Webhooks by Zapier' (a raw HTTP receiver) instead of the official Calendly Zapier trigger, which handles signature verification automatically.

</div>

## The Problem

Calendly firing into a custom Zapier "Webhooks by Zapier" trigger delivers meeting events — but every event arrives unverified. Calendly expects a 200 response only after you validate the `Calendly-Webhook-Signature` header; Zapier's generic Catch Hook does not do this for you. Worse, missed-verifications occasionally look like spam and Calendly retries the same event repeatedly until they hit the retry cap.

## Root Cause

- **Calendly sends `Calendly-Webhook-Signature`** header on every webhook delivery. Format: `t=<unix_ts>,v1=<hex_hmac_sha256_of_payload>`.
- **Verification algorithm**: compute `HMAC_SHA256("{t}.{raw_body}", signing_secret)` and compare to `v1` of the header; reject on mismatch or timestamp skew > 3 min.
- **Zapier's official Calendly integration** handles validation internally when used as the trigger. The generic **"Webhooks by Zapier"** Catch Hook is "raw HTTP receiver" and does not validate.
- **Signing secret**: lives in Calendly → "Integrations & Apps → Webhooks" page as `Webhook Signing Key`. Without verifying, you face replay attacks and tampering.
- **2026 Calendly tightening**: Calendly now drops delivery after 5 consecutive unverified (non-200) responses, pausing your integration silently.

| Trigger type | Verifies signature? | Notes |
|---|---|---|
| Official Calendly app | Yes | Calendly-managed, hides signing secret |
| Custom "Webhooks by Zapier" | No | You must verify in a code step |
| Make (custom HTTP) | No | Same as Webhooks by Zapier |
| Custom middleware | Your code | Best path for compliance |

## How to Detect If You're Affected

1. Hooh inspect your Zapier Receive history: events are arriving with raw payload but no metadata listing "Signature verified."
2. Compare Calendly's webhook log → "Webhooks" tab vs. event count in Zapier:
   ```
   Calendly sent: 100 events to your hook URL
   Zapier received: 78
   Dropped retries due to unverified status: 22
   ```
3. Attempt verification in a Zapier Developer JS step:
   ```javascript
   const sig = input.calendlySignature; // header
   const raw = input.rawBody;
   const [t, v1] = sig.split(",").map(p => p.split("=")[1]);
   const created = Math.floor(Date.now()/1000) - parseInt(t);
   if (created > 180) throw new Error("Stale webhook");
   const hmac = crypto.createHmac("sha256", SIGNING_KEY).update(`${t}.${raw}`).digest("hex");
   if (hmac !== v1) throw new Error("Signature mismatch");
   ```
4. Symptom: retries appear in Calendly's webhook log as `received 500` or `not verified`.

## Step-by-Step Fix

1. Pull the signing secret from Calendly:
   ```bash
   # In Calendly UI: Integrations & Apps → API and Webhooks → Webhook Signing Key
   SIGNING_KEY="..."
   ```
2. Verify on the receiving end before processing. Use a custom middleware or Zapier Developer "Run JavaScript" step as the first step:
   ```javascript
   const crypto = require("crypto");
   module.exports = (input) => {
     const [t, v1] = input.headers["Calendly-Webhook-Signature"]
                        .split(",").map(p => p.slice(3));
     const age = Math.floor(Date.now()/1000) - parseInt(t);
     if (age > 180) throw new Error(`Stale by ${age}s`);
     const sig = crypto.createHmac("sha256", process.env.CALENDLY_KEY)
                       .update(`${t}.${input.rawBody}`).digest("hex");
     if (sig !== v1) throw new Error("Bad signature");
     return { verified: true, payload: JSON.parse(input.rawBody) };
   };
   ```
3. Prefer the official Calendly Zap:
   - Zapier → Make a Zap → Trigger → "Calendly" → "Invitee Created" — Zapier validates the signature for you.
4. Reject incorrect signatures explicitly so Calendly knows to stop retrying:
   ```python
   if not verified:
       return "", 401  # Calendly will stop retries after 5 fails
   return "", 200
   ```
5. Wrong: accept every webhook as truth and pipe it to downstream CRM. Correct: verify, then process; else respond 401.

## Prevention

- Use the official Calendly Zapier app instead of custom Catch Hooks unless you have a specific reason; signature verification is automatic.
- Store the Calendly signing secret in environment variables — never in the Zap action's exposed field; reference via `process.env.CALENDLY_KEY`.
- Rotate the signing secret quarterly; on rotation, update secrets in middleware and run a smoke test inceptive webhook delivery.
- Set up an alert on Calendly's webhook log: failed deliveries > 5 within 1 hour indicates verification failure.
- Reject stale webhooks (older than 3 min) by comparing `t` to wall clock; this defeats replay attempts.

## Integration-Specific Context

- **Native Calendly-Zapier app**: handles signature internally; use this whenever possible.
- **Zapier "Webhooks by Zapier" Catch Hook**: raw receiver; you must verify in a JS step — make it the first step before any other action.
- **Make "Custom Webhook" module**: same situation; use the "Hash (HMAC)" module to compute and compare.
- **Custom middleware**: snippet above is the canonical pattern (200 after verify, 401 on miss).
- **2026 change**: Calendly added IP allow-listing on top of signature verification; ensure your hook receiver is reachable by Calendly's documented IP ranges if your WAF blocks defaults.

## People Also Ask

- **Does Calendly sign webhook payloads?** Yes — every webhook includes a `Calendly-Webhook-Signature` header with `t=<unix_ts>,v1=<hmac>`; the receiver verifies with the Calendly webhook signing key.
- **How do I verify Calendly webhook signature in Zapier?** Authenticate with the official Calendly app as your trigger — Zapier performs the verification automatically. If using the custom "Webhooks by Zapier" trigger, verify HMAC-SHA256 in a "Run JavaScript" step.
- **What happens if I don't verify Calendly webhooks?** Calendly drops the webhook retainer after 5 unverified responses and pauses the integration; in the interim, anyone can spoof to your endpoint.
- **What's Calendly's signature algorithm?** HMAC-SHA256 over `{t}.{raw_body}` where `t` is the unix timestamp from the `Calendly-Webhook-Signature` header. Compare with the `v1` portion in constant time.

## Official Documentation

**Zapier:**
- [Platform Docs](https://platform.zapier.com/)
- [Webhooks](https://zapier.com/help/doc/common-issues-webhooks)

**Calendly:**
- [API Docs](https://developer.calendly.com/api-docs/)
- [Webhooks](https://developer.calendly.com/api-docs/ZG9jOjM2MzE2MzQ-webhooks)

## Related Errors
- [Calendly webhook delivery delays](/integrations/zapier-to-calendly/errors/calendly-webhook-delivery-delays)
- [Calendly API rate limit on webhook subscriptions](/integrations/zapier-to-calendly/errors/calendly-api-rate-limit-on-webhook-subscriptions)
- [ActiveCampaign webhook payload format](/integrations/activecampaign-to-slack/errors/activecampaign-webhook-payload-format)
- [Zapier API Reference](/zapier)
- [Calendly API Reference](/calendly)