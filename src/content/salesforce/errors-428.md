---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Salesforce API 428: Request was not conditional"
description: "Fix Salesforce API 428 (428 Precondition Required) error. Request was not conditional — missing If-Match or similar header. Add Conditional Request Headers (e."
tool: "salesforce"
errorCode: "428"
errorName: "428 Precondition Required"
httpStatus: 428
category: "configuration"
severity: "low"
priority: 2
lastUpdated: '2026-05-02'
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "salesforce api 428 error"
  - "salesforce 428 fix"
  - "salesforce api request was not conditional"
  - "salesforce http 428"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Salesforce requires a precondition header (like `If-Match`) before it will process your request — usually for update operations.

**The fix:**
1. First, GET the record to retrieve its `ETag` header value
2. Add `If-Match` header with that ETag value to your PATCH/PUT request
3. If you get a 412 error, the record changed since you read it — re-read and retry

**Copy-paste this code** (if you're using a code editor):
```python
import requests

get_resp = requests.get(f"{instance_url}/services/data/v60.0/sobjects/Contact/003ID", headers=headers)
etag = get_resp.headers.get("ETag")
headers["If-Match"] = etag
resp = requests.patch(f"{instance_url}/services/data/v60.0/sobjects/Contact/003ID",
    headers=headers, json={"LastName": "Updated"})
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Send this to your AI coding assistant and ask it to generate working code:

> I'm getting a 428 Precondition Required error from the Salesforce API.
> The error message is: "Precondition Required" or "PRECONDITION_REQUIRED"
> I'm trying to update a Salesforce record with a PATCH request.
> Please give me a step-by-step fix with working Python code that reads the ETag and adds the If-Match header.

You want code that the AI should give you a read-then-update pattern that fetches the ETag first and includes it in the update request headers.

If the generated code doesn't handle the edge cases, refine with:
> The fix didn't work. I added the If-Match header but now I'm getting 412 Precondition Failed. Here's my code: [paste your code]. Please debug this.

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to handle Salesforce precondition errors in popular automation tools:

### Zapier
1. Open your Zap → click the Salesforce "Update Record" step
2. Zapier handles conditional headers automatically — if you're getting 428, switch from a custom API call to Zapier's built-in "Update Record" action
3. If using "Create or Update", make sure you're mapping a valid record ID from a previous "Find" step

### Make (Integromat)
1. Open your scenario → click the Salesforce "Update Record" module
2. Make's Salesforce module handles ETags automatically — if getting 428, switch from "Make an API Call" to the built-in "Update a Record" module
3. If you must use "Make an API Call", add a "Get a Record" module first and map the ETag to the `If-Match` header

### n8n
1. Open your workflow → click the Salesforce node set to "Update"
2. n8n's Salesforce node handles conditional headers automatically — use the "Update" operation instead of a raw HTTP request
3. If using the "HTTP Request" node, add a preceding Salesforce "Get" node and map the ETag header

### Power Automate
1. Open your flow → click the Salesforce "Update record" action
2. Power Automate's built-in Salesforce connector handles preconditions — use it instead of a generic HTTP action
3. If using "Send an HTTP request", add a "Get record" action first and include the ETag in custom headers

**Which tool should you use?** All major tools handle this automatically with their built-in Salesforce "Update" actions. Only custom API calls need manual ETag handling.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"428 Precondition Required"`
- `"Precondition failed"`
- `"PRECONDITION_REQUIRED"`
- `"Missing If-Match header"` in your integration logs

**What it means in plain English:** Salesforce wants proof that you've read the latest version of the record before changing it. It's a safety check to prevent overwriting someone else's changes.

**Most common cause:** Using a raw HTTP request (custom API call) to update a record without including the required `If-Match` header with the record's ETag.

</div>

## What Causes Salesforce 428

Salesforce returns HTTP 428 when a request requires conditional headers (like `If-Match` or `If-None-Match`) but they are missing. See all [Salesforce API errors](/salesforce/) in our complete reference. This is part of Salesforce's support for HTTP conditional requests, primarily used with the REST API's composite resources and some SObject endpoints that support optimistic concurrency.

The 428 status code means "Precondition Required" — the endpoint requires a precondition header to process the request. Salesforce uses this for operations that need to ensure the resource hasn't changed since it was last read, preventing lost-update problems. The response typically contains `[{"message":"Precondition Required","errorCode":"PRECONDITION_REQUIRED"}]`.

### Common Scenarios
- Updating a record via Composite API without `If-Match` header when the resource has a version
- Using the SObject PATCH endpoint that requires the record's last-modified timestamp
- Accessing a resource that requires conditional headers in the org's API configuration
- Using a Beta API feature that enforces conditional requests for data consistency

## How to Detect If You're Affected

1. Check the response error code:
   ```bash
   curl -s -X PATCH "https://yourdomain.my.salesforce.com/services/data/v60.0/sobjects/Contact/003..." \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"LastName":"Updated"}' | jq '.[0].errorCode'
   ```
   Returns `"PRECONDITION_REQUIRED"` if the header is missing.

2. Verify by adding the conditional header:
   ```bash
   curl -s -X PATCH "https://yourdomain.my.salesforce.com/services/data/v60.0/sobjects/Contact/003..." \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -H "If-Match: \"specific-etag-value\"" \
     -d '{"LastName":"Updated"}' | jq '.'
   ```

## Step-by-Step Fix

### 1. Add If-Match Header for Updates
```python
# First, GET the record to get its ETag
get_resp = requests.get(
    f"{instance_url}/services/data/v60.0/sobjects/Contact/0035x000007ABCdEAO",
    headers=headers,
)
etag = get_resp.headers.get("ETag")  # Salesforce returns ETag on GET

# BAD — PATCH without If-Match
patch_headers = headers.copy()
resp = requests.patch(
    f"{instance_url}/services/data/v60.0/sobjects/Contact/0035x000007ABCdEAO",
    headers=patch_headers,
    json={"LastName": "Updated"},
)
print(resp.status_code)  # 428 if ETag required

# GOOD — PATCH with If-Match
patch_headers["If-Match"] = etag
resp = requests.patch(
    f"{instance_url}/services/data/v60.0/sobjects/Contact/0035x000007ABCdEAO",
    headers=patch_headers,
    json={"LastName": "Updated"},
)
print(resp.status_code)  # 204 No Content (success)
```

### 2. Use ETag for Optimistic Concurrency
```python
def update_with_concurrency_control(sobject, record_id, fields):
    # Read current record to get ETag
    get_resp = requests.get(
        f"{instance_url}/services/data/v60.0/sobjects/{sobject}/{record_id}",
        headers=headers,
    )
    etag = get_resp.headers.get("ETag", "")

    # Update with If-Match to prevent lost updates
    patch_headers = headers.copy()
    patch_headers["If-Match"] = etag

    resp = requests.patch(
        f"{instance_url}/services/data/v60.0/sobjects/{sobject}/{record_id}",
        headers=patch_headers,
        json=fields,
    )

    if resp.status_code == 412:
        print("Precondition failed — record was modified since last read")
        # Re-read and retry
        return update_with_concurrency_control(sobject, record_id, fields)
    return resp
```

### 3. Handle Conditional Requests in Composite API
```python
# Composite requests may require If-Match for subrequests
composite_payload = {
    "compositeRequest": [
        {
            "method": "PATCH",
            "url": "/services/data/v60.0/sobjects/Contact/0035x000007ABCdEAO",
            "referenceId": "updateContact",
            "body": {"LastName": "Updated"},
            "httpHeaders": {
                "If-Match": '"specific-etag-value"',
            },
        }
    ]
}
resp = requests.post(
    f"{instance_url}/services/data/v60.0/composite",
    headers=headers,
    json=composite_payload,
)
```

## Prevention

- Always capture the `ETag` header from GET responses and use it in subsequent PATCH requests
- Implement optimistic concurrency control with If-Match/If-None-Match headers
- Check API documentation for endpoints that require conditional headers
- Test update operations with and without If-Match to understand which endpoints require it
- Log 428 responses with the endpoint and resource ID to identify patterns
- Similar precondition issues occur with [HubSpot 423](/hubspot/errors/423).
- This error also affects integrations. See our [Salesforce to Mailchimp](/integrations/salesforce-to-mailchimp/) and [Salesforce to ActiveCampaign](/integrations/salesforce-to-activecampaign/) integration error guides.

## Official Documentation

- [Salesforce REST API](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/)
- [Salesforce Conditional Requests](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/headers_conditional.htm)
- [Salesforce Composite API](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/using_composite_resources.htm)

## People Also Ask

- **What is HTTP 428 in Salesforce?** Precondition Required — the request needs a conditional header like `If-Match` or `If-None-Match` to proceed.
- **How do I get the ETag from Salesforce?** Salesforce returns the `ETag` header in GET responses for records. Use this value in subsequent `If-Match` headers for updates.
- **Does Salesforce require If-Match for all updates?** No — only specific endpoints and composite requests require conditional headers. Standard SObject PATCH typically doesn't require it.
- **What happens if If-Match doesn't match?** Salesforce returns 412 Precondition Failed, meaning the resource was modified since you last read it. Re-read and retry.

## Related Errors

- [Salesforce 409 Conflict](/salesforce/errors/409) — Resource state conflict
- [Salesforce 400 Bad Request](/salesforce/errors/400) — Invalid payload or field values
- [Salesforce 503 Service Unavailable](/salesforce/errors/503) — Server overload
