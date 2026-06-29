---
layout: ../../layouts/IntegrationErrorLayout.astro
title: "Calendly API Rate Limit on Webhook Subscriptions — 429 When Creating Webhooks"
description: "Calendly enforces API rate limits and frequent webhook subscription create/delete calls exceed them, returning 429 with a Retry-After. Cache subscription IDs and reuse them. Monitor X-RateLimit-Remaining to avoid burning the quota."
toolA: "zapier"
toolB: "calendly"
integrationSlug: "zapier-to-calendly"
errorSlug: "calendly-api-rate-limit-on-webhook-subscriptions"
errorName: "Calendly API rate limit on webhook subscriptions"
category: "RATE_LIMIT"
errorType: "error"
severity: "high"
priority: 2
lastUpdated: "2026-04-03"
lastReviewed: "2026-04-03"
pageType: "integration-error"
author: "API Integration Hub"
keywords:
  - "calendly api rate limit webhook subscription"
  - "calendly 429 retry after webhook subscription"
  - "calendly x-ratelimit-remaining header"
  - "calendly webhook subscription reuse cache"
  - "calendly create webhook rate limit zapier"
  - "calendly personal access token limit"
---

## The Problem

Your Zapier integration creates a new Calendly webhook subscription on every Zap turn ("if not exists, create it"), and within minutes Calendly returns `429 Retry-After=60` for all webhook management calls. New bookings stop arriving in Zapier. Worse, the same flow on Zapier's background polling exposes large-error "out of quota" stacks with no automatic recovery.

## Root Cause

- **Calendly API quota**: per OAuth token (or PAT — Personal Access Token), Calendly caps at roughly **120 requests/minute** and a daily quota tier; webhook subscription creation (`POST /webhook_subscriptions`) consumes quota alongside every other endpoint call.
- **Subscription lifecycle**: every Zapier "test" step in the UI creates a Webhook subscription; if the worker doesn't clean up, you accumulate stale subscriptions. Listing (`GET`), creating (`POST`), deleting (`DELETE`) each cost a call.
- **Headers**: Calendly responses include `X-RateLimit-Remaining` and `RateLimit-Reset` (epoch seconds); a 429 includes `Retry-After` (seconds).
- **Per-user PAT vs per-OAuth app**: limits are linked to the user account; multiple Zaps for the same user share quota.
- **Idempotency**: the API does not deduplicate by `url`+`events`+`user`+`organization`; two POSTs with the same target create two subscriptions.

| Endpoint | Quota cost | Notes |
|---|---|---|
| `POST /webhook_subscriptions` | 1 | Does not check duplicates |
| `GET /webhook_subscriptions` | 1 | List existing (paginated) |
| `DELETE /webhook_subscriptions/{uuid}` | 1 | Per webhook |
| `GET /users/me` | 1 | Low priority, frequent in Zap tests |

## How to Detect If You're Affected

1. Calendly reply body to subscription POST:
   ```json
   {"status":429, "title":"Rate Limit Exceeded","detail":"You have made too many requests recently"}
   ```
2. Inspect the webhook subscription list — too many identical hooks indicate runaway create:
   ```bash
   curl -s "https://api.calendly.com/webhook_subscriptions?organization=$ORG" \
     -H "Authorization: Bearer $TOKEN" | jq '._embedded.webhook_subscriptions | length'
   ```
3. Symptom: Zapier's Calendly trigger stops firing within minutes of test runs.
4. Calendly's response headers as a leading indicator:
   ```
   X-RateLimit-Remaining: 0     RateLimit-Reset: 1719723000
   ```

## Step-by-Step Fix

1. Cache subscription UUIDs in middleware; reuse a subscription for the same target URL + event set instead of recreating:
   ```python
   import requests
   def get_or_create(area_url, events):
       existing = requests.get("https://api.calendly.com/webhook_subscriptions",
                                params={"organization": ORG},
                                headers={"Authorization": f"Bearer {TOKEN}"}).json()
       for w in existing["_embedded"]["webhook_subscriptions"]:
           if w["attributes"]["url"] == URL and set(w["attributes"]["events"]) == events:
               return w["id"]
       return requests.post("https://api.calendly.com/webhook_subscriptions",
                              headers={"Authorization": f"Bearer {TOKEN}"},
                              json={"url": URL, "events": list(events),
                                    "organization": ORG,
                                    "user": USER}).json()["id"]
   ```
2. Honor `Retry-After`:
   ```python
   r = requests.post(hook_url, headers=h, json=payload)
   if r.status_code == 429:
       time.sleep(int(r.headers.get("Retry-After", "5")))
   ```
3. Garbage collect orphan subscriptions:
   ```bash
   for UUID in $(curl -s ... | jq -r '._embedded.webhook_subscriptions[].id'); do
       curl -X DELETE "https://api.calendly.com/webhook_subscriptions/$UUID" \
         -H "Authorization: Bearer $TOKEN"
   done
   ```
4. Wrong: query Calendly's `GET /users/me` inside every Zap task to validate the token. Correct: cache the user URI once and reuse for webhook creation calls.

## Prevention

- Store subscription UUIDs in a persistent key-value store (Redis/SSM Parameter Store); never recreate a webhook before reusing it.
- Refuse CRUD ops more than once per minute via a local throttle in middleware; surface the throttle via metrics.
- Rotate tokens (PAT) per quarter; Calendly recommended deadlines align with quota calendar resets.
- Audit Calendly's webhook dashboard weekly — URLs that don't respond with 200 should be cleaned out by the Calendly-side listing API.
- Log `X-RateLimit-Remaining` after each call; graphs will surface trouble spots before getting a full 429.

## Integration-Specific Context

- **Native Calendly-Zapier app**: handles subscription management internally via Zapier's connectors; you can't see the limits unless the Calendly Zap fails on a 429 in Zapier history.
- **Make**: subscriptions via the "Calendly — Watch events" trigger have the same problem; explicitly cache subscription UUIDs in a Make "Data Store" module.
- **Custom middleware**: snippet pattern is canonical.
- **Sales-force scenarios**: Salesforce Field Service uses the Calendly subscription on a service-account basis; ensure the service account isn't also sharing with other integrations.
- **2026 change**: Calendly increased the per-token quota to 120/min in May 2026 (up from 60) but added the daily cap (50,000 calls/day) to compensate; create-only flows run out of daily quota similarly.

## People Also Ask

- **Does Calendly rate-limit webhook subscription creation?** Yes; Calendly caps at roughly 120 requests/minute per token and a daily quota; frequent create/list/delete calls blow the budget and return 429.
- **How do I prevent Calendly 429 on webhook management?** Cache subscription UUIDs in your middleware and reuse existing subscriptions instead of recreating them on every Zap turn. Honor the `Retry-After` header on 429.
- **What's Calendly's rate limit response shape?** A 429 with `Retry-After` in seconds. Every response also carries `X-RateLimit-Remaining` (calls left in the window) and `RateLimit-Reset` (epoch seconds for window reset).
- **Does Calendly deduplicate identical webhook subscriptions?** No — two POSTs with the same URL and event set create two distinct subscriptions. Your middleware must idempotently deduplicate.

## Official Documentation

**Zapier:**
- [Platform Docs](https://platform.zapier.com/)
- [Webhooks](https://zapier.com/help/doc/common-issues-webhooks)

**Calendly:**
- [API Docs](https://developer.calendly.com/api-docs/)
- [Webhooks](https://developer.calendly.com/api-docs/ZG9jOjM2MzE2MzQ-webhooks)

## Related Errors
- [Calendly webhook verification header missing](/integrations/zapier-to-calendly/errors/calendly-webhook-verification-header-missing)
- [Calendly webhook delivery delays](/integrations/zapier-to-calendly/errors/calendly-webhook-delivery-delays)
- [Zoho API rate limit (250 req/min)](/integrations/zoho-to-mailchimp/errors/zoho-api-rate-limit-(250-req-min))
- [Zapier API Reference](/zapier)
- [Calendly API Reference](/calendly)