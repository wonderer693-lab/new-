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
lastUpdated: '2026-04-16'
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "salesforce api 429 error"
  - "salesforce 429 fix"
  - "salesforce api daily api request limit"
  - "salesforce http 429"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Too many API calls to Salesforce in a short period — you've hit the daily or concurrent request limit.

**The fix:**
1. Check your remaining API calls at the `/limits` endpoint
2. Use the Composite API to batch up to 25 requests into a single API call
3. For bulk operations, switch to Bulk API 2.0 instead of individual REST calls

**Copy-paste this code** (if you're using a code editor):
```python
import requests

limits = requests.get(f"{instance_url}/services/data/v60.0/limits", headers=headers).json()
remaining = limits["DailyApiRequests"]["Remaining"]
print(f"API calls remaining today: {remaining}")
if remaining < 100:
    print("Warning: running low — switch to Composite or Bulk API")
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Try this prompt in ChatGPT, Claude, Cursor, or Gemini:

> I'm getting a 429 REQUEST_LIMIT_EXCEEDED error from the Salesforce API.
> The error message is: "API limit exceeded"
> My integration makes many API calls to Salesforce throughout the day.
> Please give me a step-by-step fix with working Python code that uses Composite API batching and monitors remaining API calls.

The AI should outline code that batches requests using the Composite API, monitors your daily limit, and implements backoff when you're running low.

Need more? Follow up with:
> The fix didn't work. I'm still hitting the daily limit even with batching. Here's my usage pattern: [describe how many calls per day]. Please suggest a better strategy.

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to handle Salesforce rate limits in popular automation tools:

### Zapier
1. Open your Zap → enable "Auto-retry on error" in each Salesforce step's settings
2. Add a "Delay by Zapier" step (10-30 seconds) between Salesforce actions to spread out calls
3. If running bulk operations, schedule the Zap to run during off-peak hours (evenings/weekends)

### Make (Integromat)
1. Open your scenario → right-click each Salesforce module → "Add error handler" → choose "Retry"
2. Set retry interval to 60 seconds with max 3 retries
3. In scenario settings, reduce "Maximum number of operations" to spread API calls across multiple executions

### n8n
1. Open your workflow → in each Salesforce node's "Settings" → enable "Retry on Fail"
2. Set "Wait Between Tries" to 60000ms (60 seconds), "Max Tries" to 3
3. For bulk operations, use "SplitInBatches" node with a "Wait" node between batches

### Power Automate
1. Open your flow → in each Salesforce action's "Settings" → enable "Retry Policy"
2. Set to "Exponential interval" with count 3 (waits get longer between retries)
3. Add a "Delay" action (30-60 seconds) between Salesforce actions in loops

**Which tool should you use?** Zapier has the simplest auto-retry — it handles 429 errors automatically. For heavy usage, Make gives you the most control over retry timing.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"429 Too Many Requests"`
- `"REQUEST_LIMIT_EXCEEDED"`
- `"API limit exceeded"`
- `"Concurrent API request limit exceeded"` in your integration logs

**What it means in plain English:** You've used up your Salesforce API allowance for the day, or too many requests are running at the same time. It's like hitting a daily spending limit on a credit card.

**Most common cause:** Bulk data syncs or integrations that make individual API calls for every record instead of batching them together.

</div>

## What Causes Salesforce 429

Salesforce returns HTTP 429 when the daily API request limit or concurrent request limit is exceeded. See all [Salesforce API errors](/salesforce/) in our complete reference. The error code is `REQUEST_LIMIT_EXCEEDED` for daily limits. Salesforce enforces two types of limits: daily API calls per org (e.g., 15,000–1,000,000+ depending on edition) and concurrent request limits (typically 25–100 simultaneous long-running requests).

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
- Similar rate limit issues occur with [HubSpot 429](/hubspot/errors/429), [Slack rate_limited](/slack/errors/rate_limited), and [Pipedrive 429](/pipedrive/errors/429).
- This error also affects integrations. See our [Salesforce to Mailchimp](/integrations/salesforce-to-mailchimp/) and [Salesforce to ActiveCampaign](/integrations/salesforce-to-activecampaign/) integration error guides.

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
