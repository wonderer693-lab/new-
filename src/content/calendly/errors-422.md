---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Calendly API 422: Validation error"
description: "Fix Calendly API 422 error. Validation error — invalid request body. Check required fields and data types."
tool: "calendly"
errorCode: "422"
errorName: "422"
httpStatus: 422
category: "validation"
severity: "medium"
priority: 2
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "calendly api 422 error"
  - "calendly 422 fix"
  - "calendly api validation error — invalid"
  - "calendly http 422"
---

## What Causes Calendly 422

Calendly returns HTTP 422 when the request body passes basic JSON parsing but fails business validation — missing required fields, invalid UUIDs, wrong date/time formats, or values outside allowed ranges. This is different from 400 (malformed JSON) — 422 means the request structure is valid but the content doesn't meet Calendly's business rules.

The response includes a `"errors"` array with details about each validation failure. Common validation failures: invalid event type UUID, scheduling request outside available hours, invalid invitee email, or missing required questions in a booking form.

### Common Scenarios
- Event type UUID doesn't match any existing event type in the account
- Scheduling window start time is after end time
- Invitee email is missing or invalid format
- Booking form question marked as required but not provided
- Date/time in the past for a new booking

## How to Detect If You're Affected

1. Check the errors array for specific details:
   ```bash
   curl -s -X POST "https://api.calendly.com/scheduled_events" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"event_type":"invalid-uuid"}' | jq '.errors'
   ```

2. Validate UUID format locally:
   ```bash
   echo "550e8400-e29b-41d4-a716-446655440000" | grep -E '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
   ```

## Step-by-Step Fix

### 1. Validate UUIDs
```python
import re

UUID_REGEX = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')

def validate_uuid(value):
    if not UUID_REGEX.match(value.lower()):
        raise ValueError(f"Invalid UUID format: {value}")

# BAD — send invalid UUID
payload = {"event_type": "123"}  # 422

# GOOD — validate first
event_type_uuid = "550e8400-e29b-41d4-a716-446655440000"
validate_uuid(event_type_uuid)
```

### 2. Check Required Fields
```python
# Calendly booking requires:
required = ["event_type", "start_time", "end_time", "invitee", "invitee.email"]
payload = {
    "event_type": event_type_uuid,
    "start_time": "2026-07-01T10:00:00Z",
    "end_time": "2026-07-01T11:00:00Z",
    "invitee": {"email": "test@example.com"},
}

for field in required:
    if field not in str(payload):  # Simple check
        print(f"Missing field: {field}")
```

### 3. Verify Date/Time Order
```python
from datetime import datetime

start = datetime.fromisoformat("2026-07-01T10:00:00Z".replace("Z", "+00:00"))
end = datetime.fromisoformat("2026-07-01T11:00:00Z".replace("Z", "+00:00"))

if start >= end:
    raise ValueError("start_time must be before end_time")
if start < datetime.now().astimezone():
    raise ValueError("Cannot schedule event in the past")
```

## Prevention

- Validate UUID format with a regex before including in payloads
- Check date/time ordering: start < end, and both > now
- Ensure all required fields (event_type, start_time, end_time, invitee.email) are present
- Fetch the event type details first to verify it exists and has available slots
- Test scheduling with minimal payloads against a sandbox Calendly account

## Official Documentation

- [Calendly Scheduling API](https://developer.calendly.com/api-docs/reference/calendly-api/openapi/scheduling)
- [Calendly Event Types](https://developer.calendly.com/api-docs/reference/calendly-api/openapi/event-types)
- [Calendly API Errors](https://developer.calendly.com/api-docs/basics/errors)

## People Also Ask

- **What causes Calendly 422?** Business validation failures — invalid event type UUID, missing required fields, invalid date/time, or scheduling outside available hours.
- **How do I find valid Calendly event type UUIDs?** Call `GET /event_types?user=<user_uri>` — each event type has a `uri` field containing its UUID.
- **Does Calendly 422 mean my JSON is invalid?** No — 400 is for malformed JSON. 422 means the JSON structure is valid but the content fails business validation rules.
- **How do I fix Calendly 422?** Check the `errors` array in the response for specific failure details. Common fixes: validate UUIDs, ensure dates are in the future, include required fields.

## Related Errors

- [Calendly 409 Conflict](/calendly/errors/409) — Resource already exists
- [Calendly 404 Not Found](/calendly/errors/404) — Resource not found
- [Calendly 403 Forbidden](/calendly/errors/403) — Insufficient permissions
