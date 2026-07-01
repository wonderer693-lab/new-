---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "HubSpot API 207 Multi-Status: Partial success for batch endpoints when multi-status err..."
description: "Fix HubSpot API 207 Multi-Status error. Partial success for batch endpoints when multi-status error handling is enabled. Check individual status entries in response body for per-item errors."
tool: "hubspot"
errorCode: "207-multi-status"
errorName: "207 Multi-Status"
httpStatus: 0
category: "unknown"
severity: "medium"
priority: 2
lastUpdated: '2026-04-18'
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "hubspot api 207 Multi-Status error"
  - "hubspot 207 Multi-Status fix"
  - "hubspot api partial success for batch"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Some records in your bulk update succeeded but others failed silently.

**The fix:**
1. Check the `results` array in the response — each item has its own status code
2. Filter out the items where `status` is not 200 (those are the failures)
3. Retry only the failed records instead of the whole batch

**Copy-paste this code** (if you're using a code editor):
```python
import requests

resp = requests.post(url, headers=headers, json=payload)
if resp.status_code == 207:
    failures = [r for r in resp.json()["results"] if r["status"] != 200]
    print(f"{len(failures)} records failed — retry these individually")
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Send this to your AI coding assistant and ask it to generate working code:

> I'm getting a 207 Multi-Status response from the HubSpot batch API.
> Some records in my batch upsert succeeded but others failed.
> The error message says "partial success" and I don't know which records failed.
> Please give me Python code that parses the results array, identifies failures, and retries only the failed records.

You want code that the AI should give you code that loops through the `results` array, separates successes from failures, and retries only the failed items.

If the generated code doesn't handle the edge cases, refine with:
> The fix didn't work. Here's the response body I'm getting: [paste your JSON]. Please help me identify which records failed and why.

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to handle HubSpot 207 partial success in popular automation tools:

### Zapier
1. Open your Zap → click the HubSpot action step that does batch operations
2. Add a "Filter by Zapier" step after the HubSpot action — set it to continue only if the status is 200
3. Add a "Paths by Zapier" step to route failed records to a separate path that retries them individually

### Make (Integromat)
1. Open your scenario → right-click the HubSpot module → "Add error handler"
2. Choose "Ignore" so the scenario continues even if some records fail
3. Add a "JSON Parse" module after the HubSpot module to extract the `results` array, then use a "Router" to separate success from failure items

### n8n
1. Open your workflow → click the HubSpot node
2. In "Settings" → enable "Continue On Fail" so the workflow doesn't stop on 207
3. Add a "Function" node after the HubSpot node to filter the results array and pass only failed records to a retry node

### Power Automate
1. Open your flow → click the HubSpot action
2. In "Settings" → set "Run after" to include "has failed" so the next step runs even on 207
3. Add a "Parse JSON" action to read the response body, then use a "Filter array" action to separate failed records by their status code

**Which tool should you use?** Make has the best error handling for batch operations — its JSON parsing and routing make it easy to separate successes from failures.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"207 Multi-Status"`
- `"partial success"`
- `"some records failed"`
- `"HTTP 207"` in your integration logs

**What it means in plain English:** Your batch request went through, but not everything worked. Some records were saved, and some had problems. You need to check which ones failed.

**Most common cause:** Batch imports where some records have duplicate emails (409), missing fields (400), or invalid data — while the rest succeed just fine.

</div>

## What Causes HubSpot 207 Multi-Status

HubSpot returns HTTP 207 Multi-Status when using batch endpoints (like `POST /crm/v3/objects/contacts/batch/upsert` or `POST /crm/v3/objects/contacts/batch/read`) with multi-status error handling enabled. Unlike 200 (all success) or 400 (all fail), 207 indicates a mixed result — some individual records succeeded while others failed.

The response contains a `results` array where each item has its own `status` (200 for success, 400+ for failure). This is expected behavior for batch operations — it's not really an "error" but a partial success signal. You must iterate through the `results` array to identify which specific records failed and why. See all [HubSpot API errors](/hubspot/) in our complete reference for a full list of status codes you may encounter in batch responses.

This error also affects integrations. See our [HubSpot to Slack integration errors](/integrations/hubspot-to-slack/) for common cross-tool issues.

### Common Scenarios
- Batch upsert where some records are duplicates (409) while others succeed (200)
- Batch create where some records fail validation (400) and others succeed
- Batch read where some IDs don't exist (404) but others return data
- Mixed success/failure across a batch of related records

## How to Detect If You're Affected

1. Check if you're receiving 207:
   ```bash
   curl -s -w "\n%{http_code}" -X POST "https://api.hubapi.com/crm/v3/objects/contacts/batch/upsert" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"inputs":[{"properties":{"email":"test@example.com","firstname":"Test"}}]}' | tail -1
   ```

2. Inspect individual results:
   ```bash
   curl -s -X POST "https://api.hubapi.com/crm/v3/objects/contacts/batch/upsert" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"inputs":[{"properties":{"email":"test@example.com"}}]}' | jq '.results[] | {id: .id, status: .status}'
   ```

## Step-by-Step Fix

### 1. Parse Individual Results
```python
resp = requests.post(url, headers=headers, json=payload)
if resp.status_code == 207:
    data = resp.json()
    successes = [r for r in data["results"] if r["status"] == 200]
    failures = [r for r in data["results"] if r["status"] != 200]
    print(f"{len(successes)} succeeded, {len(failures)} failed")

    for failure in failures:
        print(f"  Record {failure.get('id')}: {failure['status']} - {failure.get('message')}")
```

### 2. Handle Partial Success in Batch Operations
```python
def batch_upsert(object_type, records):
    url = f"https://api.hubapi.com/crm/v3/objects/{object_type}/batch/upsert"
    payload = {"inputs": [{"properties": r} for r in records]}
    resp = requests.post(url, headers=headers, json=payload)
    data = resp.json()

    failed_records = []
    for i, result in enumerate(data.get("results", data)):
        if result.get("status", 200) != 200:
            failed_records.append(records[i])

    # Retry only failed records
    if failed_records:
        print(f"Retrying {len(failed_records)} failed records")
        batch_upsert(object_type, failed_records)
```

### 3. Log Per-Item Failures
```python
for result in data["results"]:
    if result["status"] != 200:
        log_error(
            record_id=result.get("id"),
            status=result["status"],
            message=result.get("message"),
        )
```

## Prevention

- Always parse the `results` array on 207 responses — never treat 207 as all-success or all-failure
- Implement per-record error handling in your batch processing pipeline
- Log individual failure reasons for retry or manual review
- Keep batch sizes manageable (HubSpot recommends 100 records per batch)
- Use the batch endpoints' multi-status mode explicitly by setting appropriate request parameters

## Official Documentation

- [HubSpot Batch API](https://developers.hubspot.com/docs/api/crm/batch)
- [HubSpot CRM API Overview](https://developers.hubspot.com/docs/api/crm/overview)
- [HubSpot API Errors](https://developers.hubspot.com/docs/api/errors)

## People Also Ask

- **What does HubSpot 207 mean?** Partial success — some records in your batch operation succeeded while others failed. Check the `results` array for per-item status codes.
- **How do I handle HubSpot 207?** Iterate through the `results` array. Items with `status` 200 succeeded; items with other status codes (400, 409) failed individually.
- **Is HubSpot 207 an error?** It's a mixed-status signal. Your batch request was processed, but individual records within it may have failed validation, duplicates, or other issues.
- **What causes individual failures in HubSpot batch operations?** Common per-record failures: duplicate detected (409), validation error (400), missing required field (400), or property doesn't exist (400).

## Related Errors

- [HubSpot 409 Conflict](/hubspot/errors/409) — Duplicate detected
- [HubSpot 400 Bad Request](/hubspot/errors/400) — Validation error
- [HubSpot 404 Not Found](/hubspot/errors/404) — Resource does not exist
