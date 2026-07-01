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
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "hubspot api 207 Multi-Status error"
  - "hubspot 207 Multi-Status fix"
  - "hubspot api partial success for batch"
---

## What Causes HubSpot 207 Multi-Status

HubSpot returns HTTP 207 Multi-Status when using batch endpoints (like `POST /crm/v3/objects/contacts/batch/upsert` or `POST /crm/v3/objects/contacts/batch/read`) with multi-status error handling enabled. Unlike 200 (all success) or 400 (all fail), 207 indicates a mixed result — some individual records succeeded while others failed.

The response contains a `results` array where each item has its own `status` (200 for success, 400+ for failure). This is expected behavior for batch operations — it's not really an "error" but a partial success signal. You must iterate through the `results` array to identify which specific records failed and why.

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
