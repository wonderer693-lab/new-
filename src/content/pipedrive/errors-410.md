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
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "pipedrive api 410 error"
  - "pipedrive 410 fix"
  - "pipedrive api old resource permanently unavailable"
  - "pipedrive http 410"
---

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
