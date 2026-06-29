---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Pipedrive API 404: Resource unavailable"
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
