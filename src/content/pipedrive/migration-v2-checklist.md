---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Pipedrive v2 Migration Checklist — Complete Upgrade Guide (2026)"
description: "Step-by-step Pipedrive v1 to v2 migration checklist. Auth header changes, hash key field IDs, cursor pagination, URL prefix changes, and deadline July 31, 2026."
tool: "pipedrive"
pageType: "migration-guide"
priority: 1
lastUpdated: "2026-06-16"
deadline: "2026-07-31"
keywords:
  - "pipedrive v2 migration checklist"
  - "pipedrive v1 deprecation july 31 2026"
  - "pipedrive v2 api changes"
  - "pipedrive v2 x-api-token"
  - "pipedrive v2 hash key field ids"
  - "pipedrive v2 cursor pagination"
  - "pipedrive v1 to v2 upgrade guide"
---

<div class="urgency-banner">
  <strong>Urgent:</strong> Pipedrive v1 API retires <strong>July 31, 2026</strong>.
  All integrations must be migrated to v2 by this date.
  <a href="#deadline-impact">See what happens after July 31</a>.
</div>

## What Changed in v2

Pipedrive v2 is not a minor update — it's a breaking API overhaul. Every integration must be updated.
Here are the non-negotiable changes:

| Area | v1 (old) | v2 (required) |
|------|---------|---------------|
| Base URL | `https://{company}.pipedrive.com/v1/` | `https://{company}.pipedrive.com/api/v2/` |
| Auth header | `Authorization: Bearer {token}` | `x-api-token: {api_token}` |
| Custom field IDs | Numeric (e.g., `42`) | Hash keys (e.g., `a1b2c3d4e5f6`) |
| Pagination | Offset-based (`start=0`) | Cursor-based (`cursor=...`) |
| Response format | `{ data: [...] }` | `{ data: [...], next_cursor: "..." }` |

## Migration Checklist

### Prerequisites (Week 1)
- [ ] Generate new v2 API token in Pipedrive Settings > API > v2 Token
- [ ] Enable sandbox/testing account for v2
- [ ] Document all current v1 API endpoints your integration uses
- [ ] List all custom fields referenced by numeric ID in code

### Auth Header Change (Week 1)
- [ ] Replace `Authorization: Bearer` with `x-api-token` header
- [ ] Update all API client configurations
- [ ] Test against `GET /api/v2/deals` with new header
- [ ] Verify OAuth apps (if applicable) — OAuth uses Bearer, API token uses x-api-token

```python
# v1 (deprecated)
headers = {"Authorization": "Bearer " + token}

# v2 (required)
headers = {"x-api-token": api_token}
```

### URL Prefix Change (Week 1-2)
- [ ] Replace `/v1/` with `/api/v2/` in all endpoint paths
- [ ] Update base URL configuration
- [ ] Test 3 endpoints: deals, persons, organizations

```python
# v1
url = f"https://{company}.pipedrive.com/v1/deals"

# v2
url = f"https://{company}.pipedrive.com/api/v2/deals"
```

### Hash Key Field IDs (Week 2 — Critical)
This is the most common silent failure in v2 migration.

- [ ] Fetch all custom field schemas: `GET /api/v2/dealFields`
- [ ] Create mapping table: numeric ID → hash key
- [ ] Update all API calls that reference custom fields
- [ ] Update middleware / Zapier / Make field mappings
- [ ] Test write operations with hash keys

```python
# v1: numeric field ID
deal_data = {"42": "Custom Value"}

# v2: hash key field ID
deal_data = {"a1b2c3d4e5f6": "Custom Value"}
```

### Cursor Pagination (Week 2)
- [ ] Replace offset-based pagination with cursor-based
- [ ] Update loop logic to use `next_cursor` from response
- [ ] Handle end of results (no `next_cursor` in response)

```python
# v1: offset-based
page = 0
while True:
    r = requests.get(f"{base}/deals?start={page * 100}&limit=100")
    data = r.json()["data"]
    if not data:
        break
    page += 1

# v2: cursor-based
cursor = None
while True:
    params = {"limit": 100}
    if cursor:
        params["cursor"] = cursor
    r = requests.get(f"{base}/deals", params=params)
    body = r.json()
    for item in body["data"]:
        process(item)
    cursor = body.get("next_cursor")
    if not cursor:
        break
```

### Testing & Validation (Week 3)
- [ ] Run full sync cycle in sandbox
- [ ] Verify all custom field values are written correctly
- [ ] Verify pagination returns complete dataset
- [ ] Check for silent failures (no error, wrong data)
- [ ] Benchmark response times (v2 may differ)
- [ ] Test error handling: 401, 404, 429, 500

### Deployment (Week 3-4)
- [ ] Deploy to staging environment
- [ ] Run parallel v1 + v2 for 48 hours, compare results
- [ ] Schedule cutover (off-peak hours)
- [ ] Deploy to production
- [ ] Keep v1 integration as fallback for 72 hours
- [ ] Monitor error logs for 401 / hash key failures

## Deadline Impact

After July 31, 2026, Pipedrive v1 API will stop responding. All endpoints will return errors.
Your integration will **completely stop working**. No grace period has been announced.

Actions that stop working on Aug 1:
- All CRUD operations on deals, persons, organizations
- Webhook delivery
- Custom field reads/writes
- Any integration using `/v1/` prefix

## Known Migration Errors

| Error | Symptom | Fix |
|-------|---------|-----|
| 401 Unauthorized | `x-api-token` header missing/wrong | Use API token, not OAuth Bearer |
| 400 Bad Request | Hash key instead of numeric ID | Map all custom field IDs to hash keys |
| Empty data (no error) | Numeric field ID sent — v2 silently ignores | Fetch field schemas, use hash keys |
| Missing records (pagination) | Using offset instead of cursor | Replace with cursor-based pagination |
| Wrong custom field values | Field ID collision | Verify hash key → field mapping |

## Official Documentation

- [Pipedrive API Docs](https://developers.pipedrive.com/docs/api/v1)
- [Pipedrive v2 Migration Guide](https://pipedrive.readme.io/docs/migrating-from-v1-to-v2)
- [Pipedrive Authentication](https://developers.pipedrive.com/docs/api/v1/#/Authentication)