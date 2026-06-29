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
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "salesforce api 428 error"
  - "salesforce 428 fix"
  - "salesforce api request was not conditional"
  - "salesforce http 428"
---

## What Causes Salesforce 428

Salesforce returns HTTP 428 when a request requires conditional headers (like `If-Match` or `If-None-Match`) but they are missing. This is part of Salesforce's support for HTTP conditional requests, primarily used with the REST API's composite resources and some SObject endpoints that support optimistic concurrency.

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
