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

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** The time slot is already booked or a resource already exists — Calendly won't let you create a duplicate.

**The fix:**
1. Check if the time slot or webhook already exists before trying to create it
2. If a webhook conflict — delete the old one first, then create the new one
3. If a booking conflict — check availability before booking

**Copy-paste this code** (if you're using a code editor):
```python
import requests

headers = {"Authorization": "Bearer YOUR_TOKEN"}
resp = requests.get("https://api.calendly.com/webhook_subscriptions", headers=headers)
for wh in resp.json().get("collection", []):
    print(f"{wh['url']} — {wh['uri']}")
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm getting a 409 Conflict error from the Calendly API.
> The error message is: "Resource already exists" or "already booked"
> I'm trying to create a webhook subscription or book a time slot in Calendly.
> Please give me a step-by-step fix to check for existing resources and add an availability check before booking.

**What to expect:** The AI should show you how to list existing resources, delete duplicates, and add availability checks before creating new bookings.

**If it doesn't work**, add this follow-up:
> The fix didn't work. I'm still getting 409 errors. Here's what I tried: [paste your code]. Please debug this.

**Best AI tools for this:** Claude (best at explaining conflict resolution), ChatGPT-4 (good code generation), Cursor (if you want inline code fixes)

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to fix Calendly 409 errors in popular automation tools:

### Zapier
1. Open your Zap → add a "Find Event" Calendly step before your booking step
2. Add a "Filter" step — only continue if no matching event was found
3. This prevents duplicate bookings from triggering a 409

### Make (Integromat)
1. Open your scenario → add a "List Webhook Subscriptions" module before creating a new one
2. Add a "Router" — one path for "exists" (skip), one for "doesn't exist" (create)
3. For booking conflicts, add a "Get Available Times" module first

### n8n
1. Open your workflow → add a Calendly "Get Many" node to check existing resources
2. Add an "IF" node — only proceed to the create node if no match is found
3. For bookings, add an availability check node before the booking node

### Power Automate
1. Open your flow → add a "List" Calendly action before your "Create" action
2. Add a "Condition" step — check if the resource already exists
3. Only run the "Create" action on the "No" branch of the condition

**Which tool should you use?** All tools need the same pattern — check first, then create. Zapier's Filter step makes this the easiest to set up.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"409 Conflict"`
- `"Resource already exists"`
- `"already booked"` in your Calendly API response
- `"HTTP 409"` in your integration logs

**What it means in plain English:** You're trying to create something that already exists in Calendly. It's like trying to book a meeting room that someone else already reserved.

**Most common cause:** Creating a webhook subscription without checking if one already exists, or double-booking a time slot that's already taken.

</div>

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
