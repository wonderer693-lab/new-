"""
Sprint 1 Page Generator — produces Astro content collection pages for highest-priority content.

Priority 1 (deadline-driven, before July 31, 2026):
1. Pipedrive v2 Migration Checklist (/pipedrive/migration/v2-checklist)
2. HubSpot 429 Production Retry Logic (/hubspot/errors/429)

Priority 2 (high-intent error pages):
3. HubSpot 401 Unauthorized (/hubspot/errors/401)
4. Salesforce INVALID_SESSION_ID (/salesforce/errors/INVALID_SESSION_ID)
5. ActiveCampaign ContactTag 400 (/activecampaign/errors/contacttag-400)

Output: src/content/{tool}/{slug}.md (Astro content collection format)
"""

import json
import os
from datetime import datetime

OUTPUT_DIR = os.path.join("src", "content")
DATA_DIR = os.path.join("data", "processed")

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def frontmatter(fields):
    """Generate Astro frontmatter YAML block."""
    lines = ["---"]
    for k, v in fields.items():
        if isinstance(v, list):
            lines.append(f'{k}:')
            for item in v:
                lines.append(f'  - "{item}"')
        elif isinstance(v, bool):
            lines.append(f"{k}: {str(v).lower()}")
        elif isinstance(v, int):
            lines.append(f"{k}: {v}")
        elif v is None:
            continue
        else:
            lines.append(f'{k}: "{v}"')
    lines.append("---")
    return "\n".join(lines)

# --- PAGE 1: Pipedrive v2 Migration Checklist ---

def generate_pipedrive_v2_migration():
    data = load_json(os.path.join(DATA_DIR, "pipedrive-api-data.json"))
    errors = data.get("errors", [])
    constraints = data.get("communityConstraints", [])
    auth = data.get("authentication", {})

    fm = frontmatter({
        "layout": "../../layouts/ErrorCodeLayout.astro",
        "title": "Pipedrive v2 Migration Checklist — Complete Upgrade Guide (2026)",
        "description": "Step-by-step Pipedrive v1 to v2 migration checklist. Auth header changes, hash key field IDs, cursor pagination, URL prefix changes, and deadline July 31, 2026.",
        "tool": "pipedrive",
        "pageType": "migration-guide",
        "priority": 1,
        "lastUpdated": "2026-06-26",
        "deadline": "2026-07-31",
        "keywords": [
            "pipedrive v2 migration checklist",
            "pipedrive v1 deprecation july 31 2026",
            "pipedrive v2 api changes",
            "pipedrive v2 x-api-token",
            "pipedrive v2 hash key field ids",
            "pipedrive v2 cursor pagination",
            "pipedrive v1 to v2 upgrade guide"
        ]
    })

    sections = []

    # Urgency banner
    sections.append("""<div class="urgency-banner">
  <strong>Urgent:</strong> Pipedrive v1 API retires <strong>July 31, 2026</strong>.
  All integrations must be migrated to v2 by this date.
  <a href="#deadline-impact">See what happens after July 31</a>.
</div>""")

    # Overview
    sections.append("""## What Changed in v2

Pipedrive v2 is not a minor update — it's a breaking API overhaul. Every integration must be updated.
Here are the non-negotiable changes:

| Area | v1 (old) | v2 (required) |
|------|---------|---------------|
| Base URL | `https://{company}.pipedrive.com/v1/` | `https://{company}.pipedrive.com/api/v2/` |
| Auth header | `Authorization: Bearer {token}` | `x-api-token: {api_token}` |
| Custom field IDs | Numeric (e.g., `42`) | Hash keys (e.g., `a1b2c3d4e5f6`) |
| Pagination | Offset-based (`start=0`) | Cursor-based (`cursor=...`) |
| Response format | `{ data: [...] }` | `{ data: [...], next_cursor: "..." }` |""")

    # Step-by-step checklist
    sections.append("""## Migration Checklist

### Prerequisites (Week 1)
- [ ] Generate new v2 API token in Pipedrive Settings > API > v2 Token
- [ ] Enable sandbox/testing account for v2
- [ ] Document all current v1 API endpoints your integration uses
- [ ] List all custom fields referenced by numeric ID in code""")

    sections.append("""### Auth Header Change (Week 1)
- [ ] Replace `Authorization: Bearer` with `x-api-token` header
- [ ] Update all API client configurations
- [ ] Test against `GET /api/v2/deals` with new header
- [ ] Verify OAuth apps (if applicable) — OAuth uses Bearer, API token uses x-api-token

```python
# v1 (deprecated)
headers = {"Authorization": "Bearer " + token}

# v2 (required)
headers = {"x-api-token": api_token}
```""")

    sections.append("""### URL Prefix Change (Week 1-2)
- [ ] Replace `/v1/` with `/api/v2/` in all endpoint paths
- [ ] Update base URL configuration
- [ ] Test 3 endpoints: deals, persons, organizations

```python
# v1
url = f"https://{company}.pipedrive.com/v1/deals"

# v2
url = f"https://{company}.pipedrive.com/api/v2/deals"
```""")

    sections.append("""### Hash Key Field IDs (Week 2 — Critical)
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
```""")

    sections.append("""### Cursor Pagination (Week 2)
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
```""")

    sections.append("""### Testing & Validation (Week 3)
- [ ] Run full sync cycle in sandbox
- [ ] Verify all custom field values are written correctly
- [ ] Verify pagination returns complete dataset
- [ ] Check for silent failures (no error, wrong data)
- [ ] Benchmark response times (v2 may differ)
- [ ] Test error handling: 401, 404, 429, 500""")

    sections.append("""### Deployment (Week 3-4)
- [ ] Deploy to staging environment
- [ ] Run parallel v1 + v2 for 48 hours, compare results
- [ ] Schedule cutover (off-peak hours)
- [ ] Deploy to production
- [ ] Keep v1 integration as fallback for 72 hours
- [ ] Monitor error logs for 401 / hash key failures""")

    sections.append(f"""## Deadline Impact

After July 31, 2026, Pipedrive v1 API will stop responding. All endpoints will return errors.
Your integration will **completely stop working**. No grace period has been announced.

Actions that stop working on Aug 1:
- All CRUD operations on deals, persons, organizations
- Webhook delivery
- Custom field reads/writes
- Any integration using `/v1/` prefix""")

    # Known errors
    sections.append("""## Known Migration Errors

| Error | Symptom | Fix |
|-------|---------|-----|
| 401 Unauthorized | `x-api-token` header missing/wrong | Use API token, not OAuth Bearer |
| 400 Bad Request | Hash key instead of numeric ID | Map all custom field IDs to hash keys |
| Empty data (no error) | Numeric field ID sent — v2 silently ignores | Fetch field schemas, use hash keys |
| Missing records (pagination) | Using offset instead of cursor | Replace with cursor-based pagination |
| Wrong custom field values | Field ID collision | Verify hash key → field mapping |""")

    # Community constraints
    if constraints:
        sections.append("""## Community Reports\n""")
        for c in constraints:
            sections.append(f"> **{c.get('source', 'Community')}**: {c.get('description', '')}")

    content = fm + "\n\n" + "\n\n".join(sections)
    return content

# --- PAGE 2: HubSpot 429 Production Retry Logic ---

def generate_hubspot_429():
    data = load_json(os.path.join(DATA_DIR, "hubspot-api-data.json"))
    errors = data.get("errors", [])
    rate_limits = data.get("rateLimits", {})
    community = data.get("communityConstraints", [])

    err_429 = next((e for e in errors if e.get("errorCode") == "429"), {})
    retry_strategy = err_429.get("fixStrategy", {})
    backoff_ms = retry_strategy.get("backoffMs", "1000,2000,4000,8000,16000")

    fm = frontmatter({
        "layout": "../../layouts/ErrorCodeLayout.astro",
        "title": "HubSpot API 429 Too Many Requests — Production Retry Strategy (2026)",
        "description": "Fix HubSpot API 429 rate limit errors in production. Exponential backoff, jitter, batch queuing, and 2026 rate limit header changes for public and private apps.",
        "tool": "hubspot",
        "errorCode": "429",
        "errorName": "Too Many Requests",
        "httpStatus": 429,
        "category": "rate-limit",
        "severity": "high",
        "priority": 1,
        "lastUpdated": "2026-06-26",
        "keywords": [
            "hubspot api 429 fix",
            "hubspot rate limit retry strategy",
            "hubspot exponential backoff",
            "hubspot 429 production code",
            "hubspot api rate limit 2026",
            "hubspot 110 requests per 10 seconds",
            "hubspot retry-after header"
        ]
    })

    sections = []

    sections.append("""<div class="urgency-banner">
  <strong>Critical:</strong> HubSpot's March 2026 API update changed rate limit headers and limits.
  Existing retry logic may no longer work. See <a href="#2026-changes">2026 changes</a> below.
</div>""")

    sections.append(f"""## What Causes HubSpot 429

HubSpot enforces rate limits per API key/application. Hitting the limit returns HTTP 429 with a `Retry-After` header.

### Current Limits (March 2026+)
- **Public OAuth apps**: 110 requests per 10 seconds per installed account
- **Private apps**: Varies by app type — check your dashboard
- **Batch API**: 200 objects per call (use batching to reduce call count)

### Common Triggers
- Bulk import jobs sending > 110 requests in 10 seconds
- Webhook handler that makes API calls without queuing — bursts on mass update
- Multiple Lambda/serverless instances sharing the same API key (parallel concurrency)
- Polling loop with no delay between iterations""")

    sections.append(f"""## Production Retry Strategy

### Minimal Fix (Copy-Paste Ready)

```python
import time
import random
import requests

def hubspot_request(url, headers, max_retries=5):
    for attempt in range(max_retries):
        resp = requests.get(url, headers=headers)
        if resp.status_code != 429:
            return resp

        retry_after = int(resp.headers.get("Retry-After", {backoff_ms.split(",")[0]}))
        jitter = random.randint(0, 1000)
        wait = (retry_after * 1000) + jitter
        time.sleep(wait / 1000)

    raise Exception("HubSpot 429 — max retries exceeded")
```""")

    sections.append("""### Production Queue (Recommended)

```python
import asyncio
import time
import random

class HubSpotRateLimiter:
    def __init__(self, max_rpm=660, window_s=10):
        self.max_rpm = max_rpm
        self.window_s = window_s
        self.tokens = max_rpm
        self.last_refill = time.monotonic()
        self.queue = asyncio.Queue()
        self.lock = asyncio.Lock()

    async def _refill(self):
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.max_rpm,
                         self.tokens + elapsed * (self.max_rpm / self.window_s))
        self.last_refill = now

    async def acquire(self):
        async with self.lock:
            await self._refill()
            while self.tokens < 1:
                wait = (1 - self.tokens) * (self.window_s / self.max_rpm)
                await asyncio.sleep(wait)
                await self._refill()
            self.tokens -= 1

    async def request(self, session, method, url, **kwargs):
        await self.acquire()
        for attempt in range(5):
            async with session.request(method, url, **kwargs) as resp:
                if resp.status != 429:
                    return resp
                retry_after = int(resp.headers.get("Retry-After", 1))
                jitter = random.uniform(0, 1)
                await asyncio.sleep(retry_after + jitter)
        raise Exception("429 max retries exceeded")

# Usage
limiter = HubSpotRateLimiter()
results = await asyncio.gather(*[
    limiter.request(session, "GET", url) for url in urls
])
```""")

    sections.append("""### Exponential Backoff with Jitter

| Attempt | Base Wait | Jitter (0-1s) | Total Wait |
|---------|-----------|---------------|------------|
| 1 | 1s | 0.37s | 1.37s |
| 2 | 2s | 0.81s | 2.81s |
| 3 | 4s | 0.12s | 4.12s |
| 4 | 8s | 0.94s | 8.94s |
| 5 | 16s | 0.45s | 16.45s |

**Rule**: After 5 retries, push to dead-letter queue. Do NOT retry indefinitely.""")

    sections.append("""## 2026 Changes

HubSpot's March 2026 date-versioned API update changed rate limit behavior:

| Change | Before 2026 | After March 2026 |
|--------|-------------|-------------------|
| Rate limit header | `X-HubSpot-RateLimit-Secondly` | New format — check `Retry-After` |
| Public app limit | 100 req/10s | 110 req/10s per installed account |
| OAuth token TTL | 6h (fixed) | Configurable 1-6 hours |
| Private app limits | Fixed | Varies by app type |

**If your retry logic parses the old header format, update it now.**""")

    sections.append("""## Prevention

1. **Batch API**: Use POST `/crm/v3/objects/{object}/batch/read` — 200 objects per call
2. **Webhook queuing**: Don't make API calls inside webhook handlers. Push to queue, process in batches
3. **Connection pooling**: Reuse HTTP connections (requests.Session, aiohttp.ClientSession)
4. **Monitoring**: Set up alert in HubSpot Operations Hub for API usage > 80%
5. **Key isolation**: Different workflows = different API keys (don't share across parallel services)""")

    # Add community-sourced notes
    if community:
        sections.append("""## Community Reports\n""")
        for c in community:
            if "rate" in c.get("description", "").lower():
                sections.append(f"> **{c.get('source', 'Community')}**: {c.get('description', '')}")

    sections.append("""## Related Errors
- [HubSpot 401 Unauthorized](/hubspot/errors/401) — expired OAuth token
- [HubSpot 500 Internal](/hubspot/errors/500) — server error vs rate limit
- [HubSpot 504 Gateway Timeout](/hubspot/errors/504) — slow response vs rate limit
- [Pipedrive v2 Migration](/pipedrive/migration/v2-checklist) — similar rate limit changes""")

    content = fm + "\n\n" + "\n\n".join(sections)
    return content

# --- PAGE 3: HubSpot 401 Unauthorized ---

def generate_hubspot_401():
    fm = frontmatter({
        "layout": "../../layouts/ErrorCodeLayout.astro",
        "title": "HubSpot API 401 Unauthorized — OAuth Token Expired? Fix & Prevention",
        "description": "Fix HubSpot API 401 Unauthorized errors. OAuth token refresh, private app token rotation, and 2026 configurable token TTL changes.",
        "tool": "hubspot",
        "errorCode": "401",
        "errorName": "Unauthorized",
        "httpStatus": 401,
        "category": "authentication",
        "severity": "high",
        "priority": 2,
        "lastUpdated": "2026-06-26",
        "keywords": [
            "hubspot api 401 unauthorized",
            "hubspot oauth token expired",
            "hubspot api authentication error",
            "hubspot 401 fix",
            "hubspot oauth refresh token"
        ]
    })

    sections = [
        "## What Causes HubSpot 401",
        "HubSpot API 401 means your request lacks valid authentication. Common causes:",
        "- OAuth access token expired (default 6h, configurable 1-6h since March 2026)",
        "- Refresh token expired or revoked (user disconnected app)",
        "- Private app token revoked or deleted",
        "- API key auth used (deprecated, removed in some regions)",
        "- Token sent in wrong header or format",
        "",
        "## Step-by-Step Fix",
        "",
        "### 1. Check Token Expiry",
        "```python",
        "import requests",
        "",
        "# Test with current token",
        "headers = {'Authorization': f'Bearer {token}'}",
        "resp = requests.get('https://api.hubapi.com/crm/v3/objects/contacts', headers=headers)",
        "",
        "if resp.status_code == 401:",
        "    # Token expired — refresh",
        "    refresh_resp = requests.post('https://api.hubapi.com/oauth/v1/token', data={",
        "        'grant_type': 'refresh_token',",
        "        'client_id': client_id,",
        "        'client_secret': client_secret,",
        "        'refresh_token': refresh_token",
        "    })",
        "    new_token = refresh_resp.json()['access_token']",
        "```",
        "",
        "### 2. Verify Refresh Token",
        "- User may have disconnected your app from HubSpot Settings > Integrations",
        "- Refresh token lifetime: 6 months (no activity) or until revoked",
        "- Re-authorize: send user through OAuth flow again",
        "",
        "### 3. Private App Token",
        "- Check if token exists in HubSpot Settings > Integrations > Private Apps",
        "- Generate new token, update your integration",
        "- Max 10 private app tokens per account",
        "",
        "## 2026 Changes",
        "- OAuth token TTL now configurable: 1-6 hours (was fixed 6h)",
        "- Shorter TTL = more frequent refreshes = more 401 risk if refresh logic fails",
        "- Longer TTL = longer window if token compromised",
        "",
        "## Prevention",
        "- Implement OAuth token refresh with retry (401 → refresh → retry original request)",
        "- Monitor token expiry and proactively refresh before expiry",
        "- Log authentication failures with token ID to identify revoked tokens",
        "- Use private app tokens for server-to-server integrations (no OAuth flow needed)",
        "",
        "## Related Errors",
        "- [HubSpot 429 Rate Limit](/hubspot/errors/429)",
        "- [Salesforce INVALID_SESSION_ID](/salesforce/errors/INVALID_SESSION_ID)",
        "- [Pipedrive v2 401 Auth Header](/pipedrive/errors/401)"
    ]

    return fm + "\n\n" + "\n\n".join(sections)

# --- PAGE 4: Salesforce INVALID_SESSION_ID ---

def generate_salesforce_invalid_session():
    fm = frontmatter({
        "layout": "../../layouts/ErrorCodeLayout.astro",
        "title": "Salesforce INVALID_SESSION_ID — Causes, Fix & OAuth Session Management",
        "description": "Fix Salesforce INVALID_SESSION_ID error. MFA enforcement, password expiry, session timeout, and instance URL hardcoding. Production session management strategies.",
        "tool": "salesforce",
        "errorCode": "INVALID_SESSION_ID",
        "errorName": "Invalid Session ID",
        "httpStatus": 401,
        "category": "authentication",
        "severity": "high",
        "priority": 2,
        "lastUpdated": "2026-06-26",
        "keywords": [
            "salesforce invalid_session_id",
            "salesforce api authentication error",
            "salesforce session expired",
            "salesforce oauth token invalid",
            "salesforce api 401 error fix",
            "salesforce instance url hardcoding"
        ]
    })

    sections = [
        "## What Causes INVALID_SESSION_ID",
        "",
        "INVALID_SESSION_ID is the most common Salesforce API error. It means your session/OAuth token is not valid for the endpoint you're calling.",
        "",
        "### Root Causes",
        "- **MFA enforcement**: Salesforce enforces MFA. If user's session requires MFA but your integration doesn't handle it, session invalidated.",
        "- **Password expiry**: User password expires → all sessions for that user are invalidated (including API-only sessions).",
        "- **Instance URL hardcoding**: You hardcoded `https://na1.salesforce.com` but the org was migrated to `na40` or uses My Domain.",
        "- **Session timeout**: Salesforce org session timeout setting (default 2h, can be as low as 15min).",
        "- **OAuth token revoked**: Admin revoked your connected app.",
        "- **IP range restriction**: Salesforce org has trusted IP range; your API call is from outside that range.",
        "",
        "## Step-by-Step Fix",
        "",
        "### 1. Refresh OAuth Token",
        "```python",
        "import requests",
        "",
        "def refresh_salesforce_token(refresh_token, client_id, client_secret):",
        "    resp = requests.post('https://login.salesforce.com/services/oauth2/token', data={",
        "        'grant_type': 'refresh_token',",
        "        'client_id': client_id,",
        "        'client_secret': client_secret,",
        "        'refresh_token': refresh_token",
        "    })",
        "    body = resp.json()",
        "    return body['access_token'], body['instance_url']",
        "```",
        "",
        "### 2. Use Dynamic Instance URL",
        "```python",
        "# NEVER hardcode instance URL",
        "# BAD: 'https://na1.salesforce.com'",
        "",
        "# GOOD: Always get from OAuth response",
        "instance_url = oauth_response['instance_url']  # e.g., https://yourdomain.my.salesforce.com",
        "```",
        "",
        "### 3. Check Session Settings",
        "- Go to Salesforce Setup > Session Settings",
        "- Check 'Timeout Value' — set appropriate for your integration",
        "- Disable 'Force logout on password change' if it's breaking API integrations",
        "- Add integration IP to Trusted IP Ranges",
        "",
        "## Common Scenarios",
        "",
        "| Scenario | Why It Happens | Fix |",
        "|----------|---------------|-----|",
        "| Works for hours, then fails suddenly | Session timeout | Increase timeout or implement auto-refresh |",
        "| Works from dev machine, fails from server | IP range restriction | Add server IP to trusted ranges |",
        "| Fails after password reset | Password change invalidates sessions | Use dedicated integration user with no password expiry |",
        "| Fails after MFA enrollment | MFA required for session | Use OAuth 2.0 JWT Bearer flow (bypasses MFA) |",
        "",
        "## Prevention",
        "- Use OAuth 2.0 JWT Bearer Flow for server-to-server (no user interaction, no MFA issues)",
        "- Create dedicated 'Integration User' with API access only",
        "- Set session timeout to maximum (8h) for integration users",
        "- Implement auto-refresh: detect INVALID_SESSION_ID → refresh token → retry",
        "- Don't cache access_token longer than 30 minutes",
        "",
        "## Related Errors",
        "- [HubSpot 401 Unauthorized](/hubspot/errors/401)",
        "- [Salesforce 400 Bad Request](/salesforce/errors/400)"
    ]

    return fm + "\n\n" + "\n\n".join(sections)

# --- PAGE 5: ActiveCampaign ContactTag 400 ---

def generate_activecampaign_contacttag():
    fm = frontmatter({
        "layout": "../../layouts/ErrorCodeLayout.astro",
        "title": "ActiveCampaign ContactTag 400 — Payload Format Bug & Fix",
        "description": "Fix ActiveCampaign contactTags API 400 error. Correct payload format: {'contactTag': {'contact': '1', 'tag': '2'}} not {'contact': '1', 'tag': '2'}. Official docs issue.",
        "tool": "activecampaign",
        "errorCode": "400",
        "errorName": "Bad Request — ContactTag Payload",
        "httpStatus": 400,
        "category": "api-bug",
        "severity": "high",
        "priority": 2,
        "lastUpdated": "2026-06-26",
        "keywords": [
            "activecampaign contacttag 400 error",
            "activecampaign contacttag payload format",
            "activecampaign api documentation bug",
            "activecampaign tag contact fix",
            "activecampaign contacttag wrapper object"
        ]
    })

    sections = [
        "## The Bug",
        "",
        "ActiveCampaign's `POST /api/3/contactTags` endpoint requires a specific JSON wrapper structure that differs from what many developers (and some documentation examples) expect.",
        "",
        "### Wrong (Returns 400):",
        "```json",
        '{',
        '  "contact": "1",',
        '  "tag": "2"',
        '}',
        "```",
        "",
        "### Correct:",
        "```json",
        '{',
        '  "contactTag": {',
        '    "contact": "1",',
        '    "tag": "2"',
        '  }',
        '}',
        "```",
        "",
        "## Why This Happens",
        "- ActiveCampaign API wraps most resources in a resource key (e.g., `{'contact': {...}}` for contacts)",
        "- The contactTags endpoint follows this pattern but the documentation is inconsistent",
        "- Developer community reports confirm this as a recurring issue (2025-2026)",
        "- Zapier/Make connectors handle this internally, but custom API calls and Code by Zapier fail",
        "",
        "## Step-by-Step Fix",
        "",
        "```python",
        "import requests",
        "",
        "# WRONG — produces 400",
        "wrong_payload = {",
        '    "contact": contact_id,',
        '    "tag": tag_id',
        "}",
        "resp = requests.post(",
        '    "https://{account}.api-us1.com/api/3/contactTags",',
        "    headers=headers,",
        "    json=wrong_payload",
        ")",
        "print(resp.status_code)  # 400",
        "",
        "# CORRECT",
        'correct_payload = {',
        '    "contactTag": {',
        '        "contact": contact_id,',
        '        "tag": tag_id',
        '    }',
        '}',
        "resp = requests.post(",
        '    "https://{account}.api-us1.com/api/3/contactTags",',
        "    headers=headers,",
        "    json=correct_payload",
        ")",
        "print(resp.status_code)  # 201 or 200",
        "```",
        "",
        "## Prevention",
        "- Always wrap related-resource payloads in the resource key object",
        "- Test with ActiveCampaign API Playground before production",
        "- Add JSON schema validation to your integration (catch wrapper bugs at dev time)",
        "- Log full API request/response for debugging (redact API key)",
        "",
        "## If You Use Zapier or Make",
        "- Standard connectors handle this correctly",
        "- If using 'Webhooks by Zapier' or 'Code by Zapier' to call ActiveCampaign API directly, you must use the correct wrapper format",
        "- Test with a single contact before batch operations",
        "",
        "## Related Errors",
        "- [ActiveCampaign 403 Forbidden](/activecampaign/errors/403)",
        "- [HubSpot ↔ ActiveCampaign Field Type Mismatch](/integrations/hubspot-activecampaign/errors/custom-field-type-mismatch)"
    ]

    return fm + "\n\n" + "\n\n".join(sections)

# --- MAIN: Write all pages ---

def main():
    ensure_dir(os.path.join(OUTPUT_DIR, "pipedrive"))
    ensure_dir(os.path.join(OUTPUT_DIR, "hubspot"))
    ensure_dir(os.path.join(OUTPUT_DIR, "salesforce"))
    ensure_dir(os.path.join(OUTPUT_DIR, "activecampaign"))

    pages = [
        ("pipedrive", "migration-v2-checklist", generate_pipedrive_v2_migration()),
        ("hubspot", "errors-429", generate_hubspot_429()),
        ("hubspot", "errors-401", generate_hubspot_401()),
        ("salesforce", "errors-INVALID_SESSION_ID", generate_salesforce_invalid_session()),
        ("activecampaign", "errors-contacttag-400", generate_activecampaign_contacttag()),
    ]

    for tool, slug, content in pages:
        filename = f"{slug}.md"
        filepath = os.path.join(OUTPUT_DIR, tool, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  + {tool}/{filename} ({len(content)} chars)")

    print(f"\nDone. Generated {len(pages)} pages in {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
