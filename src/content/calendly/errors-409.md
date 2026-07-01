---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Calendly API 409 Error: Conflict — Fix & Prevention Guide"
description: "Fix Calendly API 409 error. Conflict — resource already exists. Check for existing resources before creating duplicates."
tool: "calendly"
errorCode: "409"
errorName: "409"
httpStatus: 409
category: "conflict"
severity: "medium"
priority: 2
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "calendly api 409 error"
  - "calendly 409 fix"
  - "calendly api conflict — resource already"
  - "calendly http 409"
---

## What Causes Calendly 409

Calendly returns HTTP 409 when you attempt to create a resource that conflicts with an existing one. The most common case is creating a scheduling link or webhook subscription for an event type that already has one configured. Calendly enforces uniqueness constraints to prevent duplicate configurations.

The response includes `{"message":"Conflict","errors":[{"message":"Resource already exists"}]}`. This applies to webhook subscriptions (one per event+URL combination) and certain scheduling configurations. Unlike 422 (validation error), 409 means the operation would create a duplicate state that Calendly doesn't allow.

### Common Scenarios
- Creating a webhook subscription for an event type that already has one registered to the same URL
- Attempting to create duplicate scheduling rules for the same time slot
- Re-registering the same webhook URL after a deployment without unregistering the old one
- Multiple environments (dev/staging/prod) pointing to the same webhook URL

## How to Detect If You're Affected

1. Check the response for conflict:
   ```bash
   curl -s -X POST "https://api.calendly.com/webhook_subscriptions" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"url":"https://example.com/hook","events":["invitee.created"]}' | jq '.errors'
   ```

2. List existing webhooks to check for duplicates:
   ```bash
   curl -s "https://api.calendly.com/webhook_subscriptions" \
     -H "Authorization: Bearer $TOKEN" | jq '.collection[] | {url: .url, event: .events}'
   ```

## Step-by-Step Fix

### 1. List Existing Resources Before Creating
```python
# Check for existing webhook subscription
resp = requests.get("https://api.calendly.com/webhook_subscriptions", headers=headers)
existing = resp.json().get("collection", [])
for webhook in existing:
    if webhook["url"] == my_url:
        print(f"Webhook already exists: {webhook['uri']}")
        # Use existing instead of creating new
        break
```

### 2. Delete Existing Then Re-Create
```python
# For re-registration, delete old first
resp = requests.get("https://api.calendly.com/webhook_subscriptions", headers=headers)
for webhook in resp.json().get("collection", []):
    if webhook["url"] == my_url:
        webhook_uri = webhook["uri"]
        webhook_id = webhook_uri.split("/")[-1]
        requests.delete(f"https://api.calendly.com/webhook_subscriptions/{webhook_id}", headers=headers)
        print(f"Deleted existing webhook: {webhook_id}")

# Now create new
resp = requests.post("https://api.calendly.com/webhook_subscriptions", headers=headers, json={
    "url": my_url,
    "events": ["invitee.created", "invitee.canceled"],
})
```

### 3. Use Idempotency Keys
```python
# Calendly supports idempotency — include Idempotency-Key header
import uuid

idempotency_key = str(uuid.uuid4())
headers["Calendly-Idempotency-Key"] = idempotency_key

resp = requests.post("https://api.calendly.com/webhook_subscriptions", headers=headers, json=payload)
```

## Prevention

- Check for existing resources before creating — especially webhooks and scheduling rules
- Use the same webhook endpoint for multiple events (one subscription, many event types)
- Delete old webhook subscriptions when deploying new versions to avoid conflicts
- Implement idempotency keys for all creation requests
- Register webhooks only once during initial setup, not on every application startup

## Official Documentation

- [Calendly Webhook Subscriptions](https://developer.calendly.com/api-docs/reference/calendly-api/openapi/webhooks)
- [Calendly API Idempotency](https://developer.calendly.com/api-docs/basics/idempotency)
- [Calendly API Errors](https://developer.calendly.com/api-docs/basics/errors)

## People Also Ask

- **What causes Calendly 409?** Attempting to create a duplicate resource — typically a webhook subscription with the same URL and event type as an existing one.
- **How do I fix Calendly 409?** List existing resources first, delete duplicates if needed, then create. Or use idempotency keys.
- **Can I have multiple Calendly webhooks for the same URL?** No — each URL can only have one webhook subscription. Process multiple event types in the same webhook handler.
- **Does Calendly 409 apply to event scheduling?** Less commonly — most scheduling conflicts are handled by Calendly's UI. 409 mainly occurs with webhook subscriptions and configuration resources.

## Related Errors

- [Calendly 422 Validation Error](/calendly/errors/422) — Validation error
- [Calendly 404 Not Found](/calendly/errors/404) — Resource not found
- [Calendly 403 Forbidden](/calendly/errors/403) — Insufficient permissions
