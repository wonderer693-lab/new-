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


<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Calendly returns 429 rate limit errors when your Zapier integration creates too many webhook subscriptions. Each Zap test creates a new subscription, burning through Calendly's 120 requests/minute quota.

**The fix:**
1. Check your Calendly webhook subscriptions list for duplicates
2. Delete orphan subscriptions you no longer need
3. Cache subscription IDs and reuse them instead of creating new ones
4. Add a delay between webhook management API calls

**Copy-paste this code** (if you're using a code editor):
```python
import requests

def list_webhooks(token, org):
    r = requests.get("https://api.calendly.com/webhook_subscriptions",
        params={"organization": org},
        headers={"Authorization": f"Bearer {token}"})
    hooks = r.json()["_embedded"]["webhook_subscriptions"]
    print(f"Found {len(hooks)} subscriptions")
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code workaround](#no-code-workaround).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm integrating Zapier with Calendly and getting 429 rate limit errors when creating webhook subscriptions. My Zap creates a new webhook subscription on every test run and I've exceeded Calendly's API quota. How do I cache and reuse existing webhook subscriptions?

**What to expect:** The AI should help you implement subscription caching and clean up orphan subscriptions.

**If it doesn't work**, add this follow-up:
> I cleaned up subscriptions but I'm still hitting the rate limit during Zap testing. How do I reduce API calls to Calendly during development?

**Best AI tools for this:** ChatGPT-4 (good at step-by-step UI navigation), Claude (good at explaining API concepts)

</div>

## No-Code Workaround <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to debug this? Here's how to handle Calendly webhook management in other automation tools:

### Zapier
1. Use Zapier's native Calendly trigger ('Invitee Created') -- it manages subscriptions internally
2. Avoid using 'Webhooks by Zapier' as a Calendly trigger unless you need custom events
3. If using custom webhooks, test with a single subscription and reuse it across Zap runs

### Make (Integromat)
1. Use Make's 'Calendly -- Watch Events' trigger module
2. Cache the subscription UUID in a Make Data Store module to avoid recreating it
3. Add a filter to check for existing subscriptions before creating new ones

### n8n
1. Create a Calendly trigger node and configure the webhook subscription once
2. Store the subscription ID in a static variable or database node
3. Add a check at the start of the workflow to skip creation if the subscription exists

### Power Automate
1. Use the Calendly connector's built-in trigger -- it handles subscription management
2. Avoid creating webhook subscriptions manually in the flow
3. Add a 'Delay' action between any Calendly API calls to stay under the rate limit

**Which tool should you use?** Zapier's native Calendly trigger is the easiest -- it manages webhook subscriptions internally without burning your API quota.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these:

- Calendly returns 429 'Rate Limit Exceeded' when creating webhook subscriptions
- Zapier Calendly trigger stops firing after multiple test runs
- Calendly webhook list shows many duplicate subscriptions for the same URL
- New Calendly bookings stop arriving in Zapier after testing

**What it means in plain English:** Your integration is creating new Calendly webhook subscriptions too frequently, exceeding the API rate limit. Calendly caps at about 120 requests per minute per token.

**Most common cause:** Each Zapier test run creates a new webhook subscription without cleaning up old ones, quickly exhausting Calendly's API quota.

</div>

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

Related: [Calendly 429](/calendly/errors/429) for rate limits, [Zapier 429](/zapier/errors/429) for Zapier rate limits.

See all [Calendly API errors](/calendly/) or [Zapier errors](/zapier/) for more troubleshooting.

## Related Errors
- [Calendly webhook verification header missing](/integrations/zapier-to-calendly/errors/calendly-webhook-verification-header-missing)
- [Calendly webhook delivery delays](/integrations/zapier-to-calendly/errors/calendly-webhook-delivery-delays)
- [Zoho API rate limit (250 req/min)](/integrations/zoho-to-mailchimp/errors/zoho-api-rate-limit-(250-req-min))
- [Zapier API Reference](/zapier)
- [Calendly API Reference](/calendly)