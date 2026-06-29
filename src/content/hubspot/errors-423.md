---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "HubSpot API 423: Attempting to sync large volume too quickly; system lock ..."
description: "Fix HubSpot API 423 (423 Locked) error. Attempting to sync large volume too quickly; system lock for ~2 seconds. Add a delay of at least 2 seconds between requests."
tool: "hubspot"
errorCode: "423"
errorName: "423 Locked"
httpStatus: 423
category: "rate-limit"
severity: "low"
priority: 2
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "hubspot api 423 error"
  - "hubspot 423 fix"
  - "hubspot api attempting to sync large"
  - "hubspot http 423"
---

## What Causes HubSpot 423

HubSpot returns HTTP 423 when a special rate-limit mechanism called a "system lock" is triggered. This lock activates when HubSpot detects a large volume of requests targeting the same object or the same account within a short timeframe — typically around 4-5 requests per second to the same resource. The lock lasts approximately 2 seconds.

The response is `{"status":"error","message":"Attempting to sync large volume too quickly; system lock for ~2 seconds","category":"LOCKED"}`. This is distinct from the standard 429 rate limit — 423 is a temporary write lock on a specific resource to prevent data inconsistencies during high-frequency updates.

### Common Scenarios
- Sending rapid updates to the same Contact record (e.g., 10 updates in 1 second)
- Bulk association creation for the same object pair in quick succession
- Rapid-fire API calls from parallel threads updating the same deal or company
- Webhook-triggered updates that fire multiple times for the same event
- Data migration scripts that update records without inter-request delays

## How to Detect If You're Affected

1. Check the response status and category:
   ```bash
   curl -s -w "\n%{http_code}" -X PUT "https://api.hubapi.com/crm/v3/objects/contacts/1" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"properties":{"firstname":"Test"}}' | tail -1
   ```

2. Check the error message for "system lock":
   ```python
   data = resp.json()
   if data.get("category") == "LOCKED":
       print("System lock triggered — add delay between requests")
   ```

## Step-by-Step Fix

### 1. Add a Minimum 2-Second Delay
```python
import time

# BAD — rapid updates to same record
for i in range(10):
    requests.patch(url, headers=headers, json={"properties": {"firstname": f"Name{i}"}})

# GOOD — 2+ second delay between writes
for i in range(10):
    requests.patch(url, headers=headers, json={"properties": {"firstname": f"Name{i}"}})
    time.sleep(2.5)  # Slightly more than 2s for safety
```

### 2. Throttle Batch Operations
```python
# BAD — rapid batch operations
for batch in batches:
    requests.post("https://api.hubapi.com/crm/v3/objects/contacts/batch/update",
        headers=headers, json={"inputs": batch})

# GOOD — throttle batches
for batch in batches:
    requests.post("https://api.hubapi.com/crm/v3/objects/contacts/batch/update",
        headers=headers, json={"inputs": batch})
    time.sleep(3)  # Wait 3 seconds between batches
```

### 3. Implement a Rate Limiter for Write Operations
```python
class HubSpotWriteLimiter:
    def __init__(self):
        self.last_write_time = 0
        self.min_gap = 2.5  # Minimum 2.5 seconds between writes

    def wait_if_needed(self):
        now = time.time()
        elapsed = now - self.last_write_time
        if elapsed < self.min_gap:
            time.sleep(self.min_gap - elapsed)
        self.last_write_time = time.time()

limiter = HubSpotWriteLimiter()
for record in updates:
    limiter.wait_if_needed()
    requests.patch(url, headers=headers, json={"properties": record})
```

## Prevention

- Add a minimum 2.5-second delay between any write operations (create, update, delete) to the same object type
- Implement a write-rate limiter that tracks per-object write frequency
- Batch individual updates into batch operations (which count as 1 write) instead of multiple PATCH calls
- Queue write operations and process them at a controlled rate
- Monitor for 423 responses and add automatic backoff when detected

## Official Documentation

- [HubSpot API Overview](https://developers.hubspot.com/docs/api/overview)
- [HubSpot Batch Operations](https://developers.hubspot.com/docs/api/crm/batch)
- [HubSpot API Errors](https://developers.hubspot.com/docs/api/errors)

## People Also Ask

- **What does HubSpot 423 mean?** A system lock triggered by too many write operations to the same resource in a short time (typically >4-5 req/s). The lock lasts ~2 seconds.
- **How is HubSpot 423 different from 429?** 429 is the standard per-account rate limit with a Retry-After header. 423 is a per-resource write lock to prevent data inconsistency.
- **How do I fix HubSpot 423?** Add a 2-3 second delay between rapid write operations to the same object. Use batch endpoints instead of individual updates.
- **Does HubSpot 423 apply to read operations?** No — 423 typically applies to write operations (POST, PUT, PATCH, DELETE). Read operations use the standard 429 rate limit.

## Related Errors

- [HubSpot 429 Rate Limit](/hubspot/errors/429) — Too Many Requests
- [HubSpot 409 Conflict](/hubspot/errors/409) — Duplicate detected
- [HubSpot 400 Bad Request](/hubspot/errors/400) — Validation error
