---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Calendly API 404: Resource not found"
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
