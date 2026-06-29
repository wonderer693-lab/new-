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