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
lastUpdated: '2026-04-30'
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "make api 404 error"
  - "make 404 fix"
  - "make api resource not found"
  - "make http 404"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** The Make scenario or module resource you're trying to access doesn't exist — it may have been deleted or you have the wrong ID.

**The fix:**
1. Open your Make scenario list and confirm the scenario still exists
2. Check the scenario ID or module ID you're referencing — make sure it matches
3. If the resource was deleted, recreate it or update your reference to point to a valid one

**Copy-paste this code** (if you're using a code editor):
```python
import requests

resp = requests.get(f"https://api.make.com/api/v2/scenarios/{scenario_id}", headers=headers)
if resp.status_code == 404:
    print(f"Scenario {scenario_id} not found — check ID or recreate")
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy and send this to your AI tool:

> I'm getting a 404 Not Found error from Make (Integromat).
> The error message is: "Resource not found"
> I'm trying to access a Make scenario or module but it says it doesn't exist.
> Please give me a step-by-step fix to verify the resource ID and find the correct one.

You should get help listing your existing scenarios and modules to find the correct IDs.

If the error persists, try this follow-up:
> The fix didn't work. I'm still getting 404 errors. Here's the ID I'm using: [paste ID]. Please help me find the right one.

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to fix Make 404 errors in popular automation tools:

### Make (Integromat)
1. Open Make → go to "Scenarios" → confirm the scenario you're referencing is listed
2. Click the scenario → check the URL bar for the correct scenario ID number
3. If the scenario was deleted, recreate it or update any references to point to a valid scenario

### Zapier
1. Open your Zap → click the Make action step → check the scenario ID field
2. Use the dropdown to select an existing scenario instead of typing an ID manually
3. Test the step to confirm Zapier can find the scenario

### n8n
1. Open your workflow → click the Make node → check the scenario ID parameter
2. Use the "Search" feature to find existing scenarios instead of hardcoding IDs
3. Execute the node to verify n8n can locate the resource

### Power Automate
1. Open your flow → click the Make action → verify the scenario or module ID
2. Use the dynamic content picker to select an existing resource from your Make account
3. Run a test to confirm Power Automate can access the resource

**Which tool should you use?** Make's own UI is best — browse your scenarios list to confirm what exists and get the correct IDs.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"404 Not Found"`
- `"not found"`
- `"Resource not found"`
- `"Scenario or module does not exist"` in your Make logs

**What it means in plain English:** Make can't find what you're looking for. The scenario, module, or resource ID you're using doesn't exist — it may have been deleted or you have a typo.

**Most common cause:** Referencing a scenario or module ID that was deleted, or using an ID from one organization while authenticated against another.

</div>

## What Causes Make 404

Make returns HTTP 404 when the requested resource does not exist at the specified URL. This can mean the resource ID is wrong, the endpoint path is incorrect, the resource was deleted, or the request is being made in the wrong organization context (Make isolates resources per organization). See all [Make API errors](/make/) in our complete reference.

Similar not-found issues occur with [HubSpot 404](/hubspot/errors/404), [Salesforce 404](/salesforce/errors/404), and [Pipedrive 404](/pipedrive/errors/404).

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

This error also affects integrations. See our [Make to Slack integration errors](/integrations/make-to-slack/) for common cross-tool issues.

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
