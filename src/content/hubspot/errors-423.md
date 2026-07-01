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
lastUpdated: '2026-05-03'
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "hubspot api 423 error"
  - "hubspot 423 fix"
  - "hubspot api attempting to sync large"
  - "hubspot http 423"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** A HubSpot record is locked because another process is editing it.

**The fix:**
1. Wait at least 2-3 seconds before trying again
2. Slow down your updates — don't send more than 1 write per second to the same record
3. Use batch endpoints to combine multiple updates into a single request

**Copy-paste this code** (if you're using a code editor):
```python
import time, requests

resp = requests.patch(url, headers=headers, json=payload)
if resp.status_code == 423:
    print("Record locked — waiting 3 seconds")
    time.sleep(3)
    resp = requests.patch(url, headers=headers, json=payload)
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Try this prompt in ChatGPT, Claude, Cursor, or Gemini:

> I'm getting a 423 Locked error from the HubSpot API.
> The error says "Resource is locked" and "concurrent modification."
> I'm updating the same contact record multiple times in quick succession.
> Please give me code that adds a delay between writes and retries automatically when a 423 occurs.

The AI should outline a retry function with a 2-3 second delay that handles locked records gracefully and prevents rapid-fire writes.

Need more? Follow up with:
> The fix didn't work. I'm still getting 423 errors even with delays. I have multiple threads updating the same record. How do I add a write queue?

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to handle HubSpot 423 locked record errors in popular automation tools:

### Zapier
1. Open your Zap → add a "Delay by Zapier" step before each HubSpot write action
2. Set the delay to 3 seconds to avoid triggering the system lock
3. If you have multiple HubSpot actions in a row, add a delay between each one

### Make (Integromat)
1. Open your scenario → add a "Sleep" module (3 seconds) before each HubSpot write module
2. Right-click the HubSpot module → "Add error handler" → choose "Retry" with a 3-second interval and max 3 retries
3. For bulk operations, use the batch update module instead of individual update modules

### n8n
1. Open your workflow → add a "Wait" node (3000ms) before each HubSpot write node
2. In the HubSpot node "Settings" → enable "Retry on Fail" → set "Wait Between Tries" to 3000ms, "Max Tries" to 3
3. Combine multiple updates into a single "Batch Update" node instead of separate write nodes

### Power Automate
1. Open your flow → add a "Delay" action (3 seconds) before each HubSpot write action
2. In the HubSpot action "Settings" → set "Retry Policy" to "Exponential interval" with count 3
3. If updating the same record multiple times, combine the updates into a single action with all fields mapped at once

**Which tool should you use?** Make has the best retry handler for 423 errors — its error handler with retry interval handles locked records automatically.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"423 Locked"`
- `"Resource is locked"`
- `"concurrent modification"`
- `"Attempting to sync large volume too quickly"` in your integration logs

**What it means in plain English:** HubSpot put a temporary lock on a record because too many things are trying to edit it at the same time. Wait a few seconds and try again.

**Most common cause:** Sending rapid updates to the same contact, deal, or company record — like 5 updates in 1 second — which triggers HubSpot's write lock.

</div>

## What Causes HubSpot 423

HubSpot returns HTTP 423 when a special rate-limit mechanism called a "system lock" is triggered. This lock activates when HubSpot detects a large volume of requests targeting the same object or the same account within a short timeframe — typically around 4-5 requests per second to the same resource. The lock lasts approximately 2 seconds.

The response is `{"status":"error","message":"Attempting to sync large volume too quickly; system lock for ~2 seconds","category":"LOCKED"}`. This is distinct from the standard 429 rate limit — 423 is a temporary write lock on a specific resource to prevent data inconsistencies during high-frequency updates. See all [HubSpot API errors](/hubspot/) in our complete reference.

This error also affects integrations. See our [HubSpot to Slack integration errors](/integrations/hubspot-to-slack/) for common cross-tool issues.

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
- Similar rate limit issues occur with [Salesforce 429](/salesforce/errors/429), [Slack rate_limited](/slack/errors/rate_limited), and [Pipedrive 429](/pipedrive/errors/429).

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
