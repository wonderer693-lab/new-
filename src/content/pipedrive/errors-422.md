---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Pipedrive API 422: Webhooks limit reached"
description: "Fix Pipedrive API 422 (422 Unprocessable Entity) error. Webhooks limit reached. Delete unused webhooks before creating new ones."
tool: "pipedrive"
errorCode: "422"
errorName: "422 Unprocessable Entity"
httpStatus: 422
category: "validation"
severity: "medium"
priority: 2
lastUpdated: '2026-05-09'
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "pipedrive api 422 error"
  - "pipedrive 422 fix"
  - "pipedrive api webhooks limit reached"
  - "pipedrive http 422"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Pipedrive rejected your data — either you've hit the webhook limit or a field value is invalid.

**The fix:**
1. If it's a webhook limit: list your webhooks and delete old ones you don't need
2. If it's a validation error: check the field values in your request — dates, numbers, and enums must match Pipedrive's format
3. Re-try your request after cleaning up

**Copy-paste this code** (if you're using a code editor):
```python
import requests

resp = requests.get(
    "https://api.pipedrive.com/v1/webhooks?api_token=TOKEN"
)
webhooks = resp.json().get("data", [])
print(f"Active webhooks: {len(webhooks)}")
for wh in webhooks:
    print(f"  {wh['id']}: {wh['subscription_url']}")
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Start with this prompt in ChatGPT, Claude, or any AI coding assistant:

> I'm getting a 422 Unprocessable Entity error from the Pipedrive API.
> The error message is: "Webhooks limit reached"
> I need to create a new webhook but Pipedrive says I have too many.
> Please give me code to list, audit, and delete unused webhooks so I can create new ones.

A good response will give you a webhook management script that lists all webhooks, identifies stale ones, and deletes them safely.

Follow up with additional context if needed:
> The fix didn't work. I deleted webhooks but still get 422. Here's my current webhook count: [paste count]. Please help.

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to handle Pipedrive validation errors in popular automation tools:

### Zapier
1. Open your Zap → check the error log for 422 errors on Pipedrive steps
2. If it's a webhook limit: go to Pipedrive Settings > Webhooks and delete old webhooks you don't need
3. If it's a field value: check that dates use YYYY-MM-DD format and enum fields use valid values

### Make (Integromat)
1. Open your scenario → check the history for 422 errors
2. Add a "Tools > Set Variable" module before Pipedrive to format field values correctly
3. For webhook limits: go to Pipedrive web UI and remove unused webhook subscriptions

### n8n
1. Open your workflow → check the execution log for 422 status codes
2. Add a "Function" node before Pipedrive to validate field values (dates, numbers, enums)
3. For webhook limits: add a step that lists and counts webhooks before creating new ones

### Power Automate
1. Open your flow → check run history for 422 failures
2. Add a "Compose" action before Pipedrive to format dates and validate field values
3. For webhook limits: periodically run a cleanup flow that deletes old webhook subscriptions

**Which tool should you use?** Make has the best data formatting tools — its "Set Variable" module handles date and enum formatting automatically.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"422 Unprocessable Entity"`
- `"Webhooks limit reached"`
- `"validation error"`
- `"HTTP 422"` in your integration logs

**What it means in plain English:** Pipedrive looked at your data and said "this doesn't work." Either you have too many webhooks set up, or one of your field values is wrong.

**Most common cause:** Creating too many webhooks without cleaning up old ones, or sending field values in the wrong format (like a date in MM/DD/YYYY instead of YYYY-MM-DD).

</div>

## What Causes Pipedrive 422

Pipedrive returns HTTP 422 when you've reached the maximum number of webhook subscriptions for your account. Pipedrive limits the number of active webhooks per account — the exact limit depends on your plan. When exceeded, new webhook creation requests fail with `{"error":"Webhooks limit reached"}`.

This is a hard limit. You must delete unused or stale webhooks before creating new ones. Pipedrive also returns 422 for other validation errors — always check the error message to confirm it's a webhook limit vs. a different validation failure.

### Common Scenarios
- Creating a new webhook for each user or integration without tracking existing ones
- Old webhooks from decommissioned integrations still active
- Testing webhook creation repeatedly without cleanup
- Reaching the plan-specific webhook limit (varies by Pipedrive subscription tier)

## How to Detect If You're Affected

1. List all existing webhooks and count them:
   ```bash
   curl -s "https://api.pipedrive.com/v1/webhooks?api_token=$TOKEN" | jq '.data | length'
   ```

2. Check the error message:
   ```bash
   curl -s -X POST "https://api.pipedrive.com/v1/webhooks?api_token=$TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"event_action":"added","event_object":"deal","subscription_url":"https://example.com/hook"}' | jq '.error'
   ```

## Step-by-Step Fix

### 1. List and Audit Existing Webhooks
```python
resp = requests.get(f"https://api.pipedrive.com/v1/webhooks?api_token={TOKEN}")
webhooks = resp.json().get("data", [])
print(f"Active webhooks: {len(webhooks)}")
for wh in webhooks:
    print(f"  {wh['id']}: {wh['event_object']}.{wh['event_action']} -> {wh['subscription_url']}")
```

### 2. Delete Old Webhooks
```python
# Delete webhooks that are no longer in use
for wh in webhooks:
    if "old-integration" in wh["subscription_url"]:
        requests.delete(f"https://api.pipedrive.com/v1/webhooks/{wh['id']}?api_token={TOKEN}")
        print(f"Deleted webhook {wh['id']}")
```

### 3. Track Webhook Usage
```python
# Before creating a webhook, check the limit
MAX_WEBHOOKS = 10  # Plan-specific
if len(webhooks) >= MAX_WEBHOOKS:
    raise Exception(f"Webhook limit reached ({MAX_WEBHOOKS}). Delete unused hooks first.")
```

## Prevention

- Maintain a registry of active webhooks in your application database
- Delete webhooks when decommissioning an integration or environment
- Set up monitoring for 422 responses — alert when webhook count nears the limit
- Use a single webhook endpoint that routes events based on payload content
- Audit webhooks monthly to remove stale subscriptions

## Official Documentation

- [Pipedrive Webhooks API](https://developers.pipedrive.com/docs/api/v1/webhooks)
- [Pipedrive API Errors](https://developers.pipedrive.com/docs/api/v1/errors)
- [Pipedrive API Documentation](https://developers.pipedrive.com/docs/api/v1)

## People Also Ask

- **What is Pipedrive's webhook limit?** The exact limit depends on your Pipedrive plan. Contact Pipedrive support or check your plan documentation for the specific number.
- **How do I check how many webhooks I have in Pipedrive?** Call `GET /v1/webhooks?api_token=TOKEN` and count the items in the response `data` array.
- **Can I increase my Pipedrive webhook limit?** Upgrading to a higher Pipedrive plan may increase your webhook limit. Contact Pipedrive support for plan-specific details.
- **Does Pipedrive 422 always mean webhook limit?** No — 422 is also returned for other validation errors. Check the `error` field in the response body to confirm.

## Related Errors

- [Pipedrive 400 Bad Request](/pipedrive/errors/400) — Request not understood
- [Pipedrive 403 Forbidden](/pipedrive/errors/403) — Request not allowed
- [Pipedrive 429 Rate Limit](/pipedrive/errors/429) — Rate limit exceeded

See all [Pipedrive API errors](/pipedrive/) in our complete reference. Similar validation issues occur with [HubSpot 400](/hubspot/errors/400), [Salesforce 400](/salesforce/errors/400), and [ActiveCampaign 422](/activecampaign/errors/422). This error also affects integrations — see our [Pipedrive to Mailchimp integration errors](/integrations/pipedrive-to-mailchimp/) for common cross-tool issues.
