---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Salesforce API 429: Daily API request limit or concurrent request limit exceeded"
description: "Fix Salesforce API 429 (429 REQUEST_LIMIT_EXCEEDED) error. Daily API request limit or concurrent request limit exceeded. Use Composite API to batch calls (counts as 1)."
tool: "salesforce"
errorCode: "429"
errorName: "429 REQUEST_LIMIT_EXCEEDED"
httpStatus: 429
category: "rate-limit"
severity: "high"
priority: 1
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "salesforce api 429 error"
  - "salesforce 429 fix"
  - "salesforce api daily api request limit"
  - "salesforce http 429"
---

## What Causes Salesforce 429

Salesforce returns HTTP 429 when the daily API request limit or concurrent request limit is exceeded. The error code is `REQUEST_LIMIT_EXCEEDED` for daily limits. Salesforce enforces two types of limits: daily API calls per org (e.g., 15,000–1,000,000+ depending on edition) and concurrent request limits (typically 25–100 simultaneous long-running requests).

The response contains `[{"message":"API limit exceeded","errorCode":"REQUEST_LIMIT_EXCEEDED"}]`. Daily limits reset at org timezone midnight. Concurrent limits apply to requests running longer than 5 seconds. The `/limits` endpoint shows your current daily usage and remaining capacity.

### Common Scenarios
- Bulk data synchronization running daily without batching and exhausting the daily limit
- Multiple integration services sharing the same org's API call allocation
- Polling for record changes every few seconds instead of using streaming API or Platform Events
- Concurrent batch jobs exceeding the long-running request limit
- Inefficient integration making individual API calls for each record instead of using batch endpoints

## How to Detect If You're Affected

1. Check the error code:
   ```bash
   curl -s "https://yourdomain.my.salesforce.com/services/data/v60.0/sobjects/Contact" \
     -H "Authorization: Bearer $TOKEN" | jq '.[0].errorCode'
   ```

2. Check remaining API limits:
   ```bash
   curl -s "https://yourdomain.my.salesforce.com/services/data/v60.0/limits" \
     -H "Authorization: Bearer $TOKEN" | jq '.DailyApiRequests'
   ```

3. Monitor concurrent request limits:
   ```bash
   curl -s "https://yourdomain.my.salesforce.com/services/data/v60.0/limits" \
     -H "Authorization: Bearer $TOKEN" | jq '.ConcurrentSync'
   ```

## Step-by-Step Fix

### 1. Use the Composite API to Batch Requests
```python
# BAD — 5 individual API calls (5 of your daily limit)
for contact_id in contact_ids:
    requests.get(f"{instance_url}/services/data/v60.0/sobjects/Contact/{contact_id}", headers=headers)

# GOOD — 1 composite API call (counts as 1)
composite_url = f"{instance_url}/services/data/v60.0/composite"
subrequests = [
    {
        "method": "GET",
        "url": f"/services/data/v60.0/sobjects/Contact/{cid}",
        "referenceId": f"ref{i}",
    }
    for i, cid in enumerate(contact_ids[:25])  # Max 25 subrequests
]
resp = requests.post(composite_url, headers=headers, json={"compositeRequest": subrequests})
print(f"Used 1 API call instead of {len(contact_ids)}")
```

### 2. Use Bulk API 2.0 for Large Operations
```python
# BAD — individual inserts for 10,000 records
for record in records:
    requests.post(f"{instance_url}/services/data/v60.0/sobjects/Contact", headers=headers, json=record)
# 10,000 API calls

# GOOD — Bulk API 2.0 (counts as a few calls)
import csv, io

# Create a Bulk API 2.0 job
job_resp = requests.post(
    f"{instance_url}/services/data/v60.0/jobs/ingest",
    headers=headers,
    json={"object": "Contact", "operation": "insert", "contentType": "CSV"},
)
job_id = job_resp.json()["id"]

# Upload CSV data to the job
csv_buffer = io.StringIO()
writer = csv.DictWriter(csv_buffer, fieldnames=["LastName", "Email"])
writer.writeheader()
writer.writerows(records)
csv_data = csv_buffer.getvalue()

upload_resp = requests.put(
    f"{instance_url}/services/data/v60.0/jobs/ingest/{job_id}/batches",
    headers={**headers, "Content-Type": "text/csv"},
    data=csv_data,
)
print(f"Bulk job created: {job_id} — uses minimal API calls")
```

### 3. Cache Reference Data
```python
# BAD — fetching picklist values every time
def get_picklist_values(field_name):
    resp = requests.get(describe_url, headers=headers)
    # ... parse each time

# GOOD — cache in memory
class SalesforceCache:
    def __init__(self):
        self._cache = {}

    def get_sobject_fields(self, sobject, headers):
        if sobject not in self._cache:
            resp = requests.get(
                f"{instance_url}/services/data/v60.0/sobjects/{sobject}/describe",
                headers=headers,
            )
            self._cache[sobject] = resp.json()
        return self._cache[sobject]

cache = SalesforceCache()
fields = cache.get_sobject_fields("Contact", headers)  # 1 API call, cached afterward
```

## Prevention

- Use Composite API to batch up to 25 subrequests into a single API call
- Migrate large data operations to Bulk API 2.0 (designed for 10,000+ records)
- Cache reference data (picklists, field definitions, user info) with TTL-based expiry
- Use Streaming API or Platform Events instead of polling for real-time changes
- Monitor `/limits` daily and set up alerts when usage exceeds 80% of the allocation

## Official Documentation

- [Salesforce API Limits](https://developer.salesforce.com/docs/atlas.en-us.salesforce_app_limits_cheatsheet.meta/salesforce_app_limits_cheatsheet/)
- [Salesforce Composite API](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/using_composite_resources.htm)
- [Salesforce Bulk API 2.0](https://developer.salesforce.com/docs/atlas.en-us.api_bulk_v2.meta/api_bulk_v2/)
- [Salesforce Limits Endpoint](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_limits.htm)

## People Also Ask

- **What is the Salesforce daily API limit?** Varies by edition: Developer (15,000), Enterprise (100,000–500,000 depending on user count), Unlimited (1,000,000+). Check your org at `/limits`.
- **How do I check remaining Salesforce API calls?** Call `GET /services/data/v60.0/limits` and check the `DailyApiRequests.Remaining` and `DailyApiRequests.Max` fields.
- **Does Composite API reduce API call usage?** Yes — a composite request with 25 subrequests counts as a single API call against your daily limit.
- **What's the difference between daily and concurrent limits?** Daily limits track total API calls in 24 hours. Concurrent limits track how many long-running requests (>5s) can run simultaneously.

## Related Errors

- [Salesforce 403 Forbidden](/salesforce/errors/403) — Request refused
- [Salesforce 503 Service Unavailable](/salesforce/errors/503) — Server overload
- [Salesforce 414 URI Too Long](/salesforce/errors/414) — URL exceeds 16,384 bytes
