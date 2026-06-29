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
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "pipedrive api 422 error"
  - "pipedrive 422 fix"
  - "pipedrive api webhooks limit reached"
  - "pipedrive http 422"
---

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
