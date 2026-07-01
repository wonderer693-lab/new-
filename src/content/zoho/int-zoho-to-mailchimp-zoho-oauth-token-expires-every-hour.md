---
layout: ../../layouts/IntegrationErrorLayout.astro
title: "Zoho CRM OAuth Token Expires Every Hour — Mailchimp Sync Silent 401 Failures"
description: "Fix Zoho CRM OAuth access tokens that expire every 60 minutes, causing silent 401 failures in Mailchimp contact sync jobs. Proactive refresh, retry-on-401, and token caching strategy for middleware."
toolA: "zoho"
toolB: "mailchimp"
integrationSlug: "zoho-to-mailchimp"
errorSlug: "zoho-oauth-token-expires-every-hour"
errorName: "Zoho OAuth token expires every hour"
category: "AUTH"
errorType: "silent-failure"
severity: "high"
priority: 2
lastUpdated: "2026-06-03"
lastReviewed: "2026-06-03"
pageType: "integration-error"
author: "API Integration Hub"
keywords:
  - "zoho crm oauth token expiry"
  - "zoho mailchimp sync 401 silent failure"
  - "zoho oauth refresh token grant_type"
  - "zoho api token expires every hour middleware"
  - "zoho to mailchimp contact sync authorization header"
  - "zoho 60 minute access token fix"
---

<div class="urgency-banner">
  <strong>Silent failure:</strong> The Zoho API returns HTTP 401 when the access token expires, and a single sync batch of 200 contacts will skip the remaining 199 records. The middleware rarely surfaces this — check your Mailchimp subscriber delta before assuming the integration works.
</div>


<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Zoho OAuth access tokens expire every 60 minutes. When the token expires mid-sync, the remaining Mailchimp contacts are silently skipped with HTTP 401 errors.

**The fix:**
1. Set up auto-refresh: refresh the token proactively at 50 minutes (before expiry)
2. Wrap every Zoho API call in a retry-on-401 that refreshes the token and replays
3. Use the correct auth header: 'Zoho-oauthtoken' (not 'Bearer')
4. Re-run skipped records using a last_modified_time bookmark after token refresh

**Copy-paste this code** (if you're using a code editor):
```python
import time, requests

_cache = {"token": None, "expires_at": 0}

def get_token(client_id, client_secret, refresh_token):
    if _cache["token"] and time.time() < _cache["expires_at"] - 600:
        return _cache["token"]
    r = requests.post("https://accounts.zoho.com/oauth/v2/token", data={
        "grant_type": "refresh_token", "client_id": client_id,
        "client_secret": client_secret, "refresh_token": refresh_token})
    _cache["token"] = r.json()["access_token"]
    _cache["expires_at"] = time.time() + 3600
    return _cache["token"]
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code workaround](#no-code-workaround).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Paste this into ChatGPT, Claude, Cursor, or Gemini:

> I'm integrating Zoho CRM with Mailchimp and the sync silently stops after about an hour. Zoho OAuth tokens expire every 60 minutes, and my middleware doesn't refresh them -- the remaining contacts get 401 errors. How do I auto-refresh the token before it expires?

Expect back help implementing proactive token refresh and retry-on-401 logic.

Didn't work? Send a refinement prompt:
> I added auto-refresh but I'm getting 'invalid_code' errors on refresh. Could it be that I'm reusing a rotated refresh token?

</div>

## No-Code Workaround <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to debug this? Here's how to handle Zoho token expiry in Mailchimp syncs using other tools:

### Zapier
1. Use Zapier's native Zoho CRM connection -- it auto-refreshes tokens
2. Check Zap history for 'authentication_error' which indicates a stale token
3. Re-authorize the Zoho connection in Zapier if refresh fails

### Make (Integromat)
1. Store Zoho credentials in Make's connection manager -- it handles refresh
2. Enable the 'Break' error handler on the Zoho module to surface 401 errors
3. Re-authorize the Zoho connection in Make if tokens fail to refresh

### n8n
1. Use the Zoho credential node with auto-refresh enabled
2. Add a 'Code' node to implement proactive token refresh at 50 minutes
3. Add error handling to catch 401 and trigger a token refresh

### Power Automate
1. Use the Zoho connector's built-in authentication -- it handles token refresh
2. Add a Condition to check for 401 errors and refresh the token
3. Store the refresh token in a secure variable for reuse

**Which tool should you use?** Zapier is the easiest -- its native Zoho connection handles token refresh automatically without any code.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these:

- Zoho-to-Mailchimp sync silently stops after about an hour
- Zoho API returns 401 'INVALID_TOKEN' for contacts mid-batch
- Mailchimp audience hasn't grown in 24 hours despite Zoho having new contacts
- Middleware logs show a spike of 401 errors once per hour

**What it means in plain English:** Zoho OAuth access tokens expire every 60 minutes. When the token expires, all API calls return 401 and the sync silently skips remaining records.

**Most common cause:** Not implementing proactive token refresh -- the middleware uses the token until it expires instead of refreshing at 50 minutes.

</div>

## The Problem

A Zoho-to-Mailchimp contact sync that worked yesterday stops adding or updating subscribers in Mailchimp, but no exception is raised in the middleware. The Zoho REST API returns `HTTP 401 Unauthorized` after the access token's lifetime elapses, and unless your integration explicitly treats 401 as a refresh trigger, the rest of the batch is silently aborted. By the time an operator notices the Mailchimp audience has not grown in 24 hours, hundreds of Zoho records are un-synced.

## Root Cause

Zoho's OAuth 2.0 implementation uses short-lived access tokens and long-lived refresh tokens:

- **Access token TTL**: 1 hour (3,600 s) — fixed by Zoho, not configurable on self-client apps.
- **Refresh token**: long-lived but single-use per rotation in Zoho's newer data-center model (revoked on reuse on some accounts).
- **Fetch endpoint**: `https://accounts.zoho.com/oauth/v2/token` (data center URL varies — `.eu`, `.in`).
- **Required auth header**: `Authorization: Zoho-oauthtoken <access_token>` — note the literal `Zoho-oauthtoken` scheme, not `Bearer`. Even middleware that correctly refreshes a `Bearer` token will keep failing if it carries the scheme over from another provider.

| Symptom | Cause | HTTP response |
|---|---|---|
| All calls return 401 | Token expired, not refreshed | `{"code":"INVALID_TOKEN"}` |
| 401 after first 50 calls | Token refreshed mid-batch but cached stale | `INVALID_TOKEN` intermittently |
| `invalid_code` on refresh | Re-using a rotated refresh token | 400 from `/oauth/v2/token` |

## How to Detect If You're Affected

1. Query Mailchimp and compare subscriber counts to Zoho for the same `last_modified` window:
   ```bash
   curl -s "https://$(dc).api.mailchimp.com/3.0/lists/{list_id}/members?count=5000&since_last_changed=2026-06-25T00:00:00Z" \
     -H "Authorization: apikey $MC_KEY" | jq '.total_items'
   ```
2. Inspect middleware logs for the literal string `"INVALID_TOKEN"` or HTTP 401. A spike once per hour is the tell-tale signature.
3. Dump the cached token's issued-at timestamp and compare to wall clock:
   ```python
   cached = load_token()
   age = time.time() - cached["fetched_at"]
   print(f"token age {age}s -> {'STALE' if age > 3600 else 'OK'}")
   ```

## Step-by-Step Fix

1. Cache the token with an explicit `expires_at` timestamp, refreshed proactively at 50 minutes:
   ```python
   import time, requests

   TOKEN_URL = "https://accounts.zoho.com/oauth/v2/token"
   _cache = {"access_token": None, "expires_at": 0}

   def get_token(client_id, client_secret, refresh_token):
       if _cache["access_token"] and time.time() < _cache["expires_at"] - 600:
           return _cache["access_token"]
       r = requests.post(TOKEN_URL, data={
           "grant_type": "refresh_token",
           "client_id": client_id,
           "client_secret": client_secret,
           "refresh_token": refresh_token,
       })
       r.raise_for_status()
       d = r.json()
       _cache["access_token"] = d["access_token"]
       _cache["expires_at"] = time.time() + int(d["expires_in"])
       return _cache["access_token"]
   ```
   Wrong: `Authorization: Bearer {token}` — Zoho rejects this. Correct: `Authorization: Zoho-oauthtoken {token}`.
2. Wrap every Zoho call in a retry-on-401 that refreshes once and replays:
   ```python
   def zoho_get(url, **auth):
       for attempt in range(2):
           token = get_token(**auth)
           r = requests.get(url, headers={"Authorization": f"Zoho-oauthtoken {token}"})
           if r.status_code != 401 or attempt:
               return r
       raise RuntimeError("Zoho 401 after refresh")
   ```
3. Validate the refresh token once per day by rotating it; if rotation fails, alert — the connected app may have been de-authorized.
4. Re-run the batch with a `last_modified` filter so records skipped during the stale-token window are picked up.

## Prevention

- Refresh tokens proactively at 45–50 minutes (not on the hour) so a slow Zoho OAuth response still completes before expiry.
- Never reuse a rotated refresh token; store only the latest one, in a secret manager — not in source code.
- Log `expires_in` and `fetched_at` for every refresh, and emit a metric alert if age exceeds 70 minutes (sign of silent skip).
- Treat any `INVALID_TOKEN` response as fatal for the record in flight, but trigger a single token refresh for the rest of the batch.
- Run a nightly reconciliation script that diffs Mailchimp members vs Zoho contacts by `last_modified_time` and pages the on-call on drift > 0.5%.

## Integration-Specific Context

- **Native Zoho-MC connector (Piesync/HubSpot Sync)**: refresh is handled inside the connector but only retries 3 times before pausing the connector for 24 h — manual resume required.
- **Zapier**: the official Zoho CRM connection auto-refreshes, but each Zap step carries its own token; a stalled refresh disables a single Zap silently. Watch the "Zap history" for `authentication_error`.
- **Make (Integromat)**: store credentials in the Zoho module and enable the "Break" error handler route to surface 401 instead of burying it.
- **Custom middleware**: you own the entire retry path — see the snippet above.
- **2026 change**: Zoho rolled out data-center-specific OAuth domains (`accounts.zoho.eu`, `accounts.zoho.in`) earlier in 2026; hitting `accounts.zoho.com` for an EU tenant now returns `invalid_client`.

## People Also Ask

- **How long does a Zoho CRM OAuth access token last?** One hour (3,600 seconds). Refresh tokens are long-lived but must be exchanged via `grant_type=refresh_token` before the access token is used again.
- **Why does my Zoho-to-Mailchimp sync silently stop?** The most common cause is a 401 from an expired access token that the middleware does not refresh, so the remaining records in the batch are skipped without an exception.
- **What's the correct Zoho authorization header scheme?** `Zoho-oauthtoken`, not `Bearer`. Middleware built generically for OAuth often defaults to `Bearer` and fails.
- **Can I make the access token last longer?** No. Zoho caps `expires_in` at 3,600 seconds. You must implement refresh.

## Official Documentation

**Zoho CRM:**
- [API Docs](https://www.zoho.com/crm/developer/docs/api/v3/)
- [OAuth](https://www.zoho.com/crm/developer/docs/api/v3/auth.html)

**Mailchimp:**
- [API Docs](https://mailchimp.com/developer/marketing/api/)
- [Authentication](https://mailchimp.com/developer/marketing/guides/access-user-data-api-keys/)

## Related Errors
- [Zoho API rate limit (250 req/min)](/integrations/zoho-to-mailchimp/errors/zoho-api-rate-limit-(250-req-min))
- [Zoho contact duplicate detection differs from Mailchimp](/integrations/zoho-to-mailchimp/errors/zoho-contact-duplicate-detection-differs-from-mailchimp)
- [Make Slack module OAuth re-authentication](/integrations/make-to-slack/errors/make-slack-module-oauth-re-authentication)
- [Zoho CRM API Reference](/zoho)
- [Mailchimp API Reference](/mailchimp)

See all [Zoho API errors](/zoho/) or [Mailchimp API errors](/mailchimp/) for more troubleshooting. Related: [Zoho INVALID_OAUTHTOKEN](/zoho/errors/invalid-oauthtoken) for token issues, [Zoho access-denied](/zoho/errors/access-denied-oauth-throttle-) for OAuth throttling.