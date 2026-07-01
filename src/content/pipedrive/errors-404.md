---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Pipedrive API 404 Error: Resource Unavailable — Fix & Prevention"
description: "Fix Pipedrive API 404 (404 Not Found) error. Resource unavailable. Verify resource ID, endpoint path, and API version."
tool: "pipedrive"
errorCode: "404"
errorName: "404 Not Found"
httpStatus: 404
category: "not-found"
severity: "medium"
priority: 2
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "pipedrive api 404 error"
  - "pipedrive 404 fix"
  - "pipedrive api resource unavailable"
  - "pipedrive http 404"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** The deal, person, or organization you're looking for doesn't exist in Pipedrive — it was deleted, or the ID is wrong.

**The fix:**
1. Double-check the ID you're using — make sure it's a real Pipedrive record ID
2. Verify the record still exists by searching for it in the Pipedrive web UI
3. Make sure you're using the right API version (v1 vs v2) for your URL

**Copy-paste this code** (if you're using a code editor):
```python
import requests

deal_id = 12345
resp = requests.get(
    f"https://api.pipedrive.com/v1/deals/{deal_id}?api_token=TOKEN"
)
if resp.status_code == 404:
    print(f"Deal {deal_id} not found — check if it was deleted")
else:
    print(resp.json()["data"]["title"])
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Start with this prompt in ChatGPT, Claude, or any AI coding assistant:

> I'm getting a 404 Not Found error from the Pipedrive API.
> The error message is: "Resource unavailable"
> I'm trying to look up a deal by ID but Pipedrive says it doesn't exist.
> Please give me code to verify the ID is correct and handle deleted records gracefully.

A good response will give you code that checks if a record exists before acting on it and cleans up stale references.

Follow up with additional context if needed:
> The fix didn't work. I'm still getting 404 errors. Here's the deal ID I'm using: [paste ID]. Please help me debug.

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to handle Pipedrive "not found" errors in popular automation tools:

### Zapier
1. Open your Zap → check the error log for 404 errors on Pipedrive steps
2. In Pipedrive web UI, search for the record by name to confirm it exists and get the correct ID
3. Add a "Filter" step before the Pipedrive action to skip records that don't have valid IDs

### Make (Integromat)
1. Open your scenario → check the history for 404 errors on Pipedrive modules
2. Add a "Router" after the Pipedrive module — one path for success, one path with an "Error Handler" for 404s
3. In the error handler, log the missing record ID so you can investigate later

### n8n
1. Open your workflow → check the execution log for 404 status codes
2. Add an "IF" node before the Pipedrive node to check if the record ID is not empty
3. Set the Pipedrive node to "Continue on Fail" in Settings so the workflow doesn't stop on 404s

### Power Automate
1. Open your flow → check run history for 404 failures
2. Add a "Condition" action to verify the record ID exists before calling Pipedrive
3. Configure "Run after" on the Pipedrive action to handle failures gracefully

**Which tool should you use?** n8n's "Continue on Fail" setting is the best for handling 404s — it lets your workflow keep running even when records are missing.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"404 Not Found"`
- `"Resource unavailable"`
- `"record not found"`
- `"HTTP 404"` in your integration logs

**What it means in plain English:** Pipedrive can't find the record you're looking for. The deal, person, or organization was either deleted, never existed, or you're using the wrong ID.

**Most common cause:** Referencing a record ID that was deleted from Pipedrive, or using an ID from a different Pipedrive account.

</div>

## What Causes Pipedrive 404

Pipedrive returns HTTP 404 when the requested resource does not exist — a deal ID that was deleted, a person ID that never existed, or an endpoint path that is incorrect. Since Pipedrive uses integer IDs for most resources (deals, persons, organizations), a 404 often means the ID is wrong, the resource was deleted, or you're using the wrong API version.

The response is `{"error":"Resource unavailable"}`. Pipedrive's v1 and v2 APIs have different URL structures — using v1 paths against v2 (or vice versa) can result in 404s even when the resource ID is correct.

### Common Scenarios
- Referencing a deal, person, or organization ID that doesn't exist
- Resource was deleted from Pipedrive but the integration still references it
- Using v1 URL pattern against v2 API or vice versa
- Incorrect endpoint path — e.g., `/v1/deals` vs `/v1/deal` (typo)
- Resource exists in a different Pipedrive company account

## How to Detect If You're Affected

1. Test the resource ID directly:
   ```bash
   curl -s -w "\n%{http_code}" "https://api.pipedrive.com/v1/deals/99999999?api_token=$TOKEN" | tail -1
   ```

2. Verify resource existence by listing recent items:
   ```bash
   curl -s "https://api.pipedrive.com/v1/deals?api_token=$TOKEN&limit=5" | jq '.data[].id'
   ```

## Step-by-Step Fix

### 1. Verify Resource ID
```python
# List available resources to confirm IDs
resp = requests.get(f"https://api.pipedrive.com/v1/deals?api_token={TOKEN}&limit=100")
deal_ids = [d["id"] for d in resp.json().get("data", [])]
if target_id not in deal_ids:
    print(f"Deal {target_id} not found. First 100 IDs: {deal_ids[:10]}...")
```

### 2. Check API Version Path
```python
# BAD — v1 ID used with v2 endpoint format
requests.get("https://api.pipedrive.com/v2/deals/123",
    headers={"Authorization": f"Bearer {TOKEN}"})

# GOOD — match version to correct URL pattern
# v1: /v1/{resource}?api_token=TOKEN
# v2: /v2/{resource} with Bearer auth header
```

### 3. Handle Deleted Resources Gracefully
```python
def get_deal(deal_id):
    resp = requests.get(f"https://api.pipedrive.com/v1/deals/{deal_id}?api_token={TOKEN}")
    if resp.status_code == 404:
        print(f"Deal {deal_id} deleted or never existed")
        delete_from_local_cache(deal_id)
        return None
    return resp.json().get("data")
```

## Prevention

- Cache resource IDs locally and validate them before making API calls
- Implement a sync process that periodically checks if tracked resources still exist
- Handle 404 responses by cleaning up stale references in your database
- Use Pipedrive webhooks to receive real-time notifications of deletions
- Log the full URL attempted with every 404 to catch path typos quickly

## Official Documentation

- [Pipedrive API Documentation](https://developers.pipedrive.com/docs/api/v1)
- [Pipedrive Deals API](https://developers.pipedrive.com/docs/api/v1/deals)
- [Pipedrive API Errors](https://developers.pipedrive.com/docs/api/v1/errors)

## People Also Ask

- **Why does Pipedrive return 404?** The resource ID is incorrect, the resource was deleted, or the API version path is wrong. Check both the ID and the URL for typos.
- **How do I check if a Pipedrive deal exists?** Call `GET /v1/deals/{id}?api_token=TOKEN` — a 404 means the deal doesn't exist or was deleted.
- **Does Pipedrive 404 ever mean permissions?** No — Pipedrive returns 403 for permission issues. A 404 always means the resource genuinely doesn't exist at that URL.
- **Can a Pipedrive 404 be caused by a wrong API version?** Yes — using v1 endpoint paths with v2 authentication (or vice versa) can result in 404s even for valid resource IDs.

## Related Errors

- [Pipedrive 403 Forbidden](/pipedrive/errors/403) — Request not allowed
- [Pipedrive 410 Gone](/pipedrive/errors/410) — Deprecated v1 endpoint
- [Pipedrive 400 Bad Request](/pipedrive/errors/400) — Request not understood

See all [Pipedrive API errors](/pipedrive/) in our complete reference. Similar not-found issues occur with [HubSpot 404](/hubspot/errors/404), [Salesforce 404](/salesforce/errors/404), and [Mailchimp 404](/mailchimp/errors/404). This error also affects integrations — see our [Pipedrive to Mailchimp integration errors](/integrations/pipedrive-to-mailchimp/) for common cross-tool issues.
