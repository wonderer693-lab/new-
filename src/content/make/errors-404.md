---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Make API 404 Error: Resource Not Found — Fix & Prevention"
description: "Fix Make API 404 error. Resource not found. Verify resource ID and organization context."
tool: "make"
errorCode: "404"
errorName: "404"
httpStatus: 404
category: "not-found"
severity: "medium"
priority: 2
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "make api 404 error"
  - "make 404 fix"
  - "make api resource not found"
  - "make http 404"
---

## What Causes Make 404

Make returns HTTP 404 when the requested resource does not exist at the specified URL. This can mean the resource ID is wrong, the endpoint path is incorrect, the resource was deleted, or the request is being made in the wrong organization context (Make isolates resources per organization).

The response is `{"error":"Resource not found"}`. Since Make's API is organized hierarchically (`/organizations/{org_id}/...`), a common cause is using an ID from one organization while authenticated against another. Resources like scenarios, webhooks, and connections all belong to a specific organization.

### Common Scenarios
- Referencing a scenario, webhook, or connection ID that doesn't exist
- Using a resource ID from one organization in a request for another organization
- Attempting to access a deleted or archived scenario
- Typo in the endpoint URL or API version
- Resource was created in a different environment (dev vs. prod organization)

## How to Detect If You're Affected

1. Test the URL directly:
   ```bash
   curl -s -w "\n%{http_code}" "https://api.make.com/api/v2/scenarios/99999999" \
     -H "Authorization: Token $TOKEN" | tail -1
   ```
   If 404, the resource doesn't exist.

2. Verify organization context:
   ```bash
   curl -s "https://api.make.com/api/v2/organizations" \
     -H "Authorization: Token $TOKEN" | jq '.[].id'
   ```
   Confirm the resource was created in one of these organizations.

## Step-by-Step Fix

### 1. Verify Resource ID
```python
# List all scenarios to confirm the ID exists
resp = requests.get("https://api.make.com/api/v2/scenarios", headers=headers)
scenarios = resp.json()
scenario_ids = [s["id"] for s in scenarios]
if target_id not in scenario_ids:
    print(f"Scenario {target_id} not found — listing available: {scenario_ids}")
```

### 2. Check Organization Context
```python
# Resources are scoped to organizations
org_id = "123456"
resp = requests.get(
    f"https://api.make.com/api/v2/organizations/{org_id}/scenarios/{scenario_id}",
    headers=headers
)
```

### 3. Handle Deleted Resources Gracefully
```python
try:
    resp = requests.get(url, headers=headers)
    if resp.status_code == 404:
        # Resource was deleted — clean up reference
        delete_local_reference(resource_id)
        print(f"Resource {resource_id} no longer exists — removed from local cache")
except Exception as e:
    print(f"Error accessing resource: {e}")
```

## Prevention

- Always validate resource IDs exist before referencing them in operations
- Store the organization ID alongside each resource ID for context verification
- Implement a resource lookup/refresh function that retrieves the current state before acting
- Catch 404 responses and clean up any stale references in your local database
- Use Make's listing endpoints to programmatically verify resource existence

## Official Documentation

- [Make API Documentation](https://www.make.com/en/api-documentation)
- [Make Scenarios API](https://www.make.com/en/api-documentation#scenarios)
- [Make Organizations API](https://www.make.com/en/api-documentation#organizations)

## People Also Ask

- **Why does Make return 404 for a resource I just created?** The resource may belong to a different organization. Make scopes all resources to organizations — ensure you're using the correct `org_id` in the URL path.
- **Can a Make 404 mean a permissions issue?** No — Make returns 403 Forbidden for permission issues and 404 only when the resource genuinely doesn't exist or was deleted.
- **How long does Make keep deleted resources?** Make may retain deleted resources in a soft-delete state for a short period. After that, the 404 is permanent.
- **Does Make 404 ever mean the endpoint URL is wrong?** Yes — if you mistype the endpoint path (e.g., `scenario` instead of `scenarios`), Make returns 404. Double-check the API documentation for the exact URL pattern.

## Related Errors

- [Make 403 Forbidden](/make/errors/403) — Insufficient permissions
- [Make 400 Bad Request](/make/errors/400) — Invalid request parameters
- [Make 500 Server Error](/make/errors/500) — Server error
