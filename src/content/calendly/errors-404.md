---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Calendly API 404 Error: Resource Not Found — Fix & Prevention"
description: "Fix Calendly API 404 error. Resource not found. Verify UUID format and resource existence."
tool: "calendly"
errorCode: "404"
errorName: "404"
httpStatus: 404
category: "not-found"
severity: "medium"
priority: 2
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "calendly api 404 error"
  - "calendly 404 fix"
  - "calendly api resource not found"
  - "calendly http 404"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** The Calendly event type or user you're looking for doesn't exist — the UUID is wrong or the resource was deleted.

**The fix:**
1. Double-check the UUID in your request URL — it should look like `550e8400-e29b-41d4-a716-446655440000`
2. Fetch the list of event types to get valid UUIDs
3. Make sure the resource hasn't been canceled or deleted

**Copy-paste this code** (if you're using a code editor):
```python
import requests

headers = {"Authorization": "Bearer YOUR_TOKEN"}
resp = requests.get("https://api.calendly.com/event_types", headers=headers)
for et in resp.json().get("collection", []):
    print(et["uri"])
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm getting a 404 Not Found error from the Calendly API.
> The error message is: "Resource not found"
> I'm trying to access a Calendly event type or scheduled event by its UUID.
> Please give me a step-by-step fix to verify the event type URI and handle missing resources.

**What to expect:** The AI should show you how to list valid event types, validate UUIDs, and handle deleted resources gracefully.

**If it doesn't work**, add this follow-up:
> The fix didn't work. I'm still getting 404 errors. Here's the UUID I'm using: [paste your UUID]. Please debug this.

**Best AI tools for this:** Claude (best at explaining UUID issues), ChatGPT-4 (good code generation), Cursor (if you want inline code fixes)

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to fix Calendly 404 errors in popular automation tools:

### Zapier
1. Open your Zap → click the Calendly action step
2. In the event type dropdown, re-select the event type — don't use a hardcoded UUID
3. Test the step to confirm it finds the event type

### Make (Integromat)
1. Open your scenario → click the Calendly module
2. Replace any hardcoded event type URI with a dynamic value from a "List Event Types" module
3. Add a filter to skip items where the event type is empty

### n8n
1. Open your workflow → add a "Calendly" node set to "Get Many Event Types"
2. Use the output UUID in your next Calendly node instead of a hardcoded value
3. Add an "IF" node to check the UUID exists before using it

### Power Automate
1. Open your flow → add a "List event types" Calendly action before your main action
2. Use the dynamic UUID from the list output in your next step
3. Add a "Condition" to check the event type exists before proceeding

**Which tool should you use?** Always fetch event types dynamically instead of hardcoding UUIDs — this prevents 404 errors when event types change.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"404 Not Found"`
- `"Resource not found"`
- `"Not found"` in your Calendly API response
- `"HTTP 404"` in your integration logs

**What it means in plain English:** Calendly can't find what you're looking for. The event type, scheduled event, or user doesn't exist — it may have been deleted or the ID is wrong.

**Most common cause:** Using a hardcoded UUID that was deleted, or copying a UUID from a different Calendly account.

</div>

## What Causes Calendly 404

Calendly returns HTTP 404 when the requested resource does not exist at the specified URI. Calendly uses UUIDs to identify resources like event types, scheduled events, and users. A 404 means the UUID doesn't match any existing resource or the resource is not accessible with the current token.

The response typically contains `{"message":"Not found","errors":[{"message":"Resource not found"}]}`. Calendly's API uses UUIDs in the format `https://api.calendly.com/scheduled_events/{uuid}`. Common causes include deleted events, expired scheduling links, or using a UUID from a different Calendly account.

### Common Scenarios
- Referencing a scheduled event that was canceled or deleted
- Using an event type UUID from a different Calendly account
- Including a UUID with incorrect format (missing dashes, wrong length)
- Accessing a resource outside the token's organization scope
- Referencing an event that occurred outside the accessible date range

## How to Detect If You're Affected

1. Verify the resource with a list call:
   ```bash
   # Check if the event type UUID exists
   curl -s "https://api.calendly.com/event_types" \
     -H "Authorization: Bearer $TOKEN" | jq '.collection[].uri'
   ```

2. Validate UUID format:
   ```bash
   echo "550e8400-e29b-41d4-a716-446655440000" | grep -E '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
   # Returns the UUID if valid, nothing if invalid
   ```

3. Check if the resource is scoped to the current user's organization:
   ```bash
   curl -s "https://api.calendly.com/users/me" \
     -H "Authorization: Bearer $TOKEN" | jq '.resource.current_organization'
   ```

## Step-by-Step Fix

### 1. Validate UUID Format
```python
import re

UUID_REGEX = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')

def is_valid_uuid(value):
    return bool(UUID_REGEX.match(value.lower()))

# BAD — invalid UUID
uri = "https://api.calendly.com/scheduled_events/123"
resp = requests.get(uri, headers=headers)  # 404

# GOOD — valid UUID
event_uuid = "550e8400-e29b-41d4-a716-446655440000"
if is_valid_uuid(event_uuid):
    uri = f"https://api.calendly.com/scheduled_events/{event_uuid}"
    resp = requests.get(uri, headers=headers)
```

### 2. Fetch Valid Resource UUIDs
```python
# List event types to get valid UUIDs
resp = requests.get("https://api.calendly.com/event_types", headers=headers)
event_types = resp.json().get("collection", [])
valid_uris = [et["uri"] for et in event_types]
print(f"Valid event types: {valid_uris}")

# Only use UUIDs from this list
if target_uri in valid_uris:
    resp = requests.get(target_uri, headers=headers)
else:
    print("Event type not found — may have been deleted")
```

### 3. Handle Deleted or Expired Resources
```python
resp = requests.get(f"https://api.calendly.com/scheduled_events/{uuid}", headers=headers)
if resp.status_code == 404:
    print(f"Scheduled event {uuid} not found — it may have been canceled or deleted")
    # Refresh the event list to get current events
    events_resp = requests.get("https://api.calendly.com/scheduled_events", headers=headers)
    current_events = events_resp.json().get("collection", [])
    print(f"Current events: {len(current_events)}")
```

## Prevention

- Always fetch resource UUIDs from list endpoints rather than hardcoding them
- Validate UUID format with a regex before sending to the API
- Handle 404 responses gracefully by re-fetching the resource list
- Use organization-scoped tokens to ensure access to resources across the account
- Cache UUIDs with their creation timestamps and refresh periodically

## Official Documentation

- [Calendly API Overview](https://developer.calendly.com/api-docs/)
- [Calendly List Event Types](https://developer.calendly.com/api-docs/reference/calendly-api/openapi/event-types)
- [Calendly Get Scheduled Event](https://developer.calendly.com/api-docs/reference/calendly-api/openapi/scheduled-events)

## People Also Ask

- **How do I find valid Calendly event type UUIDs?** Call `GET /event_types` and extract the `uri` field from each item. The UUID is the last segment of the URI path.
- **Does Calendly return 404 for deleted events?** Yes — once a scheduled event is canceled or deleted, the API returns 404 when trying to fetch it.
- **Can I get 404 with a valid UUID?** Yes — if the UUID is from a different organization or the resource is outside the token's scope, you'll get 404 even with a valid format.
- **How do I get Calendly scheduled event UUIDs?** Use `GET /scheduled_events?user=<user_uri>` to list upcoming events and their UUIDs.

## Related Errors

- [Calendly 401 Unauthorized](/calendly/errors/401) — Invalid or missing token
- [Calendly 403 Forbidden](/calendly/errors/403) — Insufficient permissions
- [Calendly 429 Rate Limit](/calendly/errors/429) — Too many requests
