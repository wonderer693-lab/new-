---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Mailchimp API 400: Malformed request or validation error"
description: "Fix Mailchimp API 400 (400 Bad Request) error. Malformed request or validation error. Use PUT /3."
tool: "mailchimp"
errorCode: "400"
errorName: "400 Bad Request"
httpStatus: 400
category: "validation"
severity: "medium"
priority: 2
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "mailchimp api 400 error"
  - "mailchimp 400 fix"
  - "mailchimp api malformed request or validation"
  - "mailchimp http 400"
---

## What Causes Mailchimp 400

Mailchimp returns HTTP 400 when the request body is malformed, contains invalid JSON, uses wrong data types, or fails validation rules (e.g., invalid email format, missing required merge fields). This is the most common Mailchimp API error during integration development.

The response includes `{"status":400,"title":"Bad Request","detail":"..."}` with a `detail` field explaining the specific validation failure. Mailchimp also returns `errors` array with per-field validation details. Common specific issues include invalid email addresses, merge field values that don't match their types, and subscriber status transitions that aren't allowed (e.g., cleaning a subscriber directly without proper state flow).

### Common Scenarios
- Invalid email format (missing `@`, invalid domain, spaces in email)
- Wrong merge field type — sending a string for a `number` or `date` merge field
- Invalid subscriber status transition — e.g., trying to go from "cleaned" to "subscribed" directly
- Missing required merge fields that the list requires
- Using `PUT /3.0/lists/{id}/members/{hash}` without the correct subscriber hash format

## How to Detect If You're Affected

1. Check the detail field for the specific error:
   ```bash
   curl -s -X POST "https://usX.api.mailchimp.com/3.0/lists/{id}/members" \
     -H "Authorization: apikey $API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"email_address":"invalid","status":"subscribed"}' | jq '.detail'
   ```

2. Check the errors array for per-field details:
   ```bash
   curl -s ... | jq '.errors[] | {field, message}'
   ```

## Step-by-Step Fix

### 1. Validate Email Format
```python
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

# BAD — send invalid email
payload = {"email_address": "not-an-email", "status": "subscribed"}  # 400

# GOOD — validate first
if not EMAIL_REGEX.match(email):
    raise ValueError(f"Invalid email format: {email}")
payload = {"email_address": email, "status": "subscribed"}
```

### 2. Pre-Create Merge Fields
When syncing from another system (e.g., HubSpot), ensure merge fields exist:
```python
def ensure_merge_field(list_id, tag, name, type_):
    url = f"https://usX.api.mailchimp.com/3.0/lists/{list_id}/merge-fields"
    resp = requests.post(url, headers=headers, json={
        "tag": tag, "name": name, "type": type_
    })
    if resp.status_code == 400:
        # May already exist — try fetching it
        existing = requests.get(url, headers=headers).json()
        print(f"Merge field {tag} may already exist")

# Create merge fields before sending data
ensure_merge_field(list_id, "FNAME", "First Name", "text")
ensure_merge_field(list_id, "PHONE", "Phone Number", "phone")
```

### 3. Use PUT for Upsert (Create or Update)
```python
# BAD — POST fails if member exists
resp = requests.post(f"https://usX.api.mailchimp.com/3.0/lists/{list_id}/members",
    headers=headers, json=payload)

# GOOD — PUT creates or updates
subscriber_hash = hashlib.md5(email.lower().encode()).hexdigest()
resp = requests.put(
    f"https://usX.api.mailchimp.com/3.0/lists/{list_id}/members/{subscriber_hash}",
    headers=headers, json=payload
)
```

## Prevention

- Validate email format with a regex before any API call
- Use PUT (upsert) instead of POST to create/update subscribers in one call
- Pre-create all merge fields before sending subscriber data — use `GET /3.0/lists/{id}/merge-fields` to check first
- Log the full request body alongside every 400 response for rapid debugging
- Add JSON schema validation to your integration to catch structural errors early

## Official Documentation

- [Mailchimp List Members API](https://mailchimp.com/developer/marketing/api/list-members/)
- [Mailchimp Merge Fields](https://mailchimp.com/developer/marketing/api/merge-fields/)
- [Mailchimp API Overview](https://mailchimp.com/developer/marketing/api/)

## People Also Ask

- **What causes Mailchimp 400?** Invalid request body — malformed JSON, invalid email, wrong merge field types, or disallowed subscriber status transitions. Check the `detail` field for specifics.
- **How do I fix Mailchimp 400?** Validate email format, ensure merge field tags match existing fields, use PUT instead of POST for subscriber operations, and check subscriber status transition rules.
- **What's the correct subscriber status flow in Mailchimp?** Valid statuses are: subscribed, unsubscribed, cleaned, pending. You cannot transition from "cleaned" directly to "subscribed" — use "pending" as an intermediate step.
- **How do I create a subscriber with Mailchimp API?** Use `PUT /3.0/lists/{list_id}/members/{subscriber_hash}` with `email_address` and `status` fields. PUT acts as upsert — it creates if new, updates if existing.

## Related Errors

- [Mailchimp 404 Not Found](/mailchimp/errors/404) — Resource does not exist
- [Mailchimp 403 Forbidden](/mailchimp/errors/403) — User role lacks permission
- [Mailchimp 429 Rate Limit](/mailchimp/errors/429) — Too many requests
