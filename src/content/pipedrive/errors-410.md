---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Pipedrive API 410: Old resource permanently unavailable (deprecated v1 endpo..."
description: "Fix Pipedrive API 410 (410 Gone) error. Old resource permanently unavailable (deprecated v1 endpoints). Migrate to v2 equivalent endpoints."
tool: "pipedrive"
errorCode: "410"
errorName: "410 Gone"
httpStatus: 410
category: "deprecation"
severity: "medium"
priority: 2
lastUpdated: '2026-05-03'
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "pipedrive api 410 error"
  - "pipedrive 410 fix"
  - "pipedrive api old resource permanently unavailable"
  - "pipedrive http 410"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** The Pipedrive API endpoint you're calling has been permanently removed — it's part of the v1 to v2 migration.

**The fix:**
1. Change your URL from `/v1/` to `/v2/` (e.g., `/v1/deals` becomes `/v2/deals`)
2. Switch from `?api_token=TOKEN` to `Authorization: Bearer TOKEN` header
3. Update pagination from page-based to cursor-based

**Copy-paste this code** (if you're using a code editor):
```python
import requests

# OLD (410 Gone):
# resp = requests.get("https://api.pipedrive.com/v1/deals?api_token=TOKEN")

# NEW (v2 endpoint):
resp = requests.get(
    "https://api.pipedrive.com/v2/deals",
    headers={"Authorization": "Bearer TOKEN"}
)
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy and send this to your AI tool:

> I'm getting a 410 Gone error from the Pipedrive API.
> The error message is: "Old resource permanently unavailable (deprecated v1 endpoints)"
> My integration uses v1 endpoints and I need to migrate to v2.
> Please give me a step-by-step migration guide with code examples for the most common endpoints.

You should get a mapping of v1 to v2 endpoints and updated code with v2 authentication and cursor-based pagination.

If the error persists, try this follow-up:
> The migration didn't work. Here's my v1 code: [paste your code]. Please convert it to v2.

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to handle Pipedrive v1 deprecation in popular automation tools:

### Zapier
1. Open your Zap → click the Pipedrive action step
2. Reconnect your Pipedrive account — Zapier's latest Pipedrive integration uses v2 endpoints automatically
3. Re-map your fields if the v2 field names differ from v1

### Make (Integromat)
1. Open your scenario → click the Pipedrive module
2. Update the module to the latest version — Make updates Pipedrive modules to use v2 endpoints
3. Check the module settings for any changed field names or pagination options

### n8n
1. Open your workflow → click the Pipedrive node
2. In the node settings, switch the "API Version" from v1 to v2
3. Update authentication from API token to OAuth/Bearer token if required

### Power Automate
1. Open your flow → click the Pipedrive action
2. Check for a newer version of the Pipedrive connector — update if available
3. Reconfigure any fields that changed between v1 and v2

**Which tool should you use?** Zapier handles v2 migration automatically when you reconnect — no manual URL changes needed.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"410 Gone"`
- `"Old resource permanently unavailable (deprecated v1 endpoints)"`
- `"endpoint deprecated"`
- `"HTTP 410"` in your integration logs

**What it means in plain English:** The Pipedrive API page you're trying to reach has been permanently shut down. It's not coming back. You need to switch to the new v2 version.

**Most common cause:** Using old v1 API endpoints that Pipedrive has removed as part of their migration to v2.

</div>

## What Causes Pipedrive 410

Pipedrive returns HTTP 410 when you call a v1 API endpoint that has been permanently removed and replaced by a v2 equivalent. The 410 "Gone" status means the resource is permanently unavailable and will never return — you must migrate to the v2 endpoint.

Pipedrive has been deprecating v1 endpoints in favor of v2, which offers better performance, lower token consumption (50% fewer), and improved data models. The response includes `{"error":"Old resource permanently unavailable (deprecated v1 endpoints)"}`. Affected endpoints typically include deal lists, person searches, and paginated collection endpoints.

### Common Scenarios
- Using `GET /v1/deals/list` (v1) instead of `GET /v2/deals` (v2)
- Using page-based pagination (`/v1/deals?page=1`) instead of cursor-based (`/v2/deals?cursor=...`)
- Calling `/v1/searchResults` or other deprecated search endpoints
- Integration that hasn't been updated since Pipedrive v1 deprecation announcements

## How to Detect If You're Affected

1. Check the response status:
   ```bash
   curl -s -w "\n%{http_code}" "https://api.pipedrive.com/v1/deals?api_token=$TOKEN" | tail -1
   ```

2. Check the Pipedrive changelog for deprecation announcements:
   ```bash
   curl -s https://developers.pipedrive.com/changelog | grep -i deprecated
   ```

## Step-by-Step Fix

### 1. Identify Deprecated Endpoints
```python
# Common v1-to-v2 migrations:
V1_TO_V2 = {
    "/v1/deals": "/v2/deals",
    "/v1/persons": "/v2/persons",
    "/v1/organizations": "/v2/organizations",
    "/v1/products": "/v2/products",
}

# Replace v1 URL with v2
v1_url = "https://api.pipedrive.com/v1/deals?api_token=..."
for v1_path, v2_path in V1_TO_V2.items():
    if v1_path in v1_url:
        v2_url = v1_url.replace(v1_path, v2_path)
        break
```

### 2. Migrate to v2 Authentication
```python
# v1: API token in query param
resp = requests.get("https://api.pipedrive.com/v1/deals?api_token=TOKEN")

# v2: Bearer token in Authorization header
resp = requests.get("https://api.pipedrive.com/v2/deals",
    headers={"Authorization": f"Bearer {TOKEN}"})
```

### 3. Update Pagination Logic
```python
# v1: page-based
for page in range(1, 50):
    resp = requests.get(f"https://api.pipedrive.com/v1/deals?api_token={TOKEN}&page={page}")

# v2: cursor-based
cursor = None
while True:
    params = {"cursor": cursor} if cursor else {}
    resp = requests.get("https://api.pipedrive.com/v2/deals",
        headers={"Authorization": f"Bearer {TOKEN}"}, params=params)
    data = resp.json()
    cursor = data.get("next_cursor")
    if not cursor:
        break
```

## Prevention

- Subscribe to the Pipedrive developer changelog for deprecation announcements
- Use v2 endpoints for all new development — avoid v1 entirely
- Implement a version monitoring check: at startup, test a known v1 endpoint and log a warning if it still works (indicating future risk)
- Schedule v1-to-v2 migration as part of your regular dependency update cycle
- Use Pipedrive's API client libraries that handle versioning automatically

## Official Documentation

- [Pipedrive API v2 Documentation](https://developers.pipedrive.com/docs/api/v2)
- [Pipedrive API Migration Guide](https://developers.pipedrive.com/docs/api/v2/migration)
- [Pipedrive Changelog](https://developers.pipedrive.com/changelog)

## People Also Ask

- **What does Pipedrive 410 mean?** The endpoint you're calling has been permanently removed (deprecated v1). You must migrate to the v2 equivalent endpoint.
- **How do I find the v2 equivalent of my v1 endpoint?** Check Pipedrive's migration guide at developers.pipedrive.com/docs/api/v2/migration for a complete endpoint mapping.
- **Does Pipedrive v2 use different authentication?** Yes — v2 uses `Authorization: Bearer <token>` header instead of the `api_token` query parameter used in v1.
- **What are the benefits of migrating to Pipedrive v2?** v2 endpoints consume 50% fewer rate limit tokens, support cursor-based pagination for better performance, and have improved data models.

## Related Errors

- [Pipedrive 404 Not Found](/pipedrive/errors/404) — Resource unavailable
- [Pipedrive 400 Bad Request](/pipedrive/errors/400) — Request not understood
- [Pipedrive 429 Rate Limit](/pipedrive/errors/429) — Rate limit exceeded

See all [Pipedrive API errors](/pipedrive/) in our complete reference. Similar deprecation issues occur with [Make 404](/make/errors/404) for removed endpoints. This error also affects integrations — see our [Pipedrive to Mailchimp integration errors](/integrations/pipedrive-to-mailchimp/) for common cross-tool issues.
