---
layout: ../../layouts/IntegrationErrorLayout.astro
title: "Pipedrive v2 Hash Key Field IDs in Custom Data — Mailchimp Reads Empty Merge Fields"
description: "Pipedrive API v2 returns custom field keys as 40-char hash strings (e.g., a1b2c3...) instead of numeric IDs. Middleware expecting numeric keys reads empty values and writes blank fields to Mailchimp. Update field maps to use hash keys after migrating to v2."
toolA: "pipedrive"
toolB: "mailchimp"
integrationSlug: "pipedrive-to-mailchimp"
errorSlug: "pipedrive-v2-hash-key-field-ids-in-custom-data"
errorName: "Pipedrive v2 hash key field IDs in custom data"
category: "API_VERSION"
errorType: "error"
severity: "high"
priority: 2
lastUpdated: "2026-04-25"
lastReviewed: "2026-04-25"
pageType: "integration-error"
author: "API Integration Hub"
keywords:
  - "pipedrive v2 custom field hash key id"
  - "pipedrive api v2 field id 40 character"
  - "pipedrive mailchimp custom field empty after migration"
  - "pipedrive person custom field key change"
  - "pipedrive v1 to v2 migration custom fields"
  - "pipedrive deal custom data json key hash"
---

## The Problem

After migrating your Pipedrive integration from v1 to v2, every Mailchimp merge field that came from a custom field is now blank — but the Pipedrive record itself shows the value plainly in the UI. The middleware was looking up `['12345']` and Pipedrive v2 is now returning `['a1b2c3d4e5f6...40-char-hash']` as the JSON key, so your field map misses and the value is silently dropped.

## Root Cause

- **Pipedrive v2 (2026)**: custom fields are keyed by an **opaque 40-character hash** rather than the legacy numeric `id` (an integer like `12345`).
- **v1 behavior**: response payload mix: `{ "12345": "Senior" }` where `12345` was the field id.
- **v2 behavior**: `{ "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2": "Senior" }` — opaque hash.
- **Field schema lookup**: v2 endpoint `/dealFields` (or `/personFields`) returns `key` (the hash) and `id` (still numeric), but the actual deal object only uses the hash key in its custom field data.
- **Backward compatibility**: there is none. v2 endpoints exclusively return hash-keyed payload; v1 was deprecated in Sep 2025 and removed June 2026.

| Field source | v1 payload key | v2 payload key |
|---|---|---|
| Custom dropdown | `"12345"` | `"a1b2c3d4…"` |
| Person email | `email` (string) | `[{value:…,label:…,primary:…}]` (array of objects) |
| `org_id` | numeric `123` | `{"id":123,"name":"…"}` (object) |
| `owner_id` | numeric | `{"id":…,"name":…}` |

## How to Detect If You're Affected

1. Fetch a recent Pipedrive deal and inspect keys:
   ```bash
   curl -s "https://api.pipedrive.com/v2/deals/1?include=custom_fields" \
     -H "Authorization: Bearer $TOKEN" | jq '.data.custom_fields | keys'
   ```
   Hash strings instead of integers in `keys[]` confirm v2 mode.
2. Compare Mailchimp merge field values:
   ```bash
   curl -s "https://$DC.api.mailchimp.com/3.0/lists/$LIST/members/$HASH?fields=merge_fields" \
     -H "Authorization: apikey $MC_KEY"
   ```
   If value is `null` for fields where Pipedrive has data, this is the cause.
3. Grep your middleware for hardcoded numeric field ids:
   ```bash
   rg '"12345"' middleware --type=py
   ```
4. Symptom: marketable field missing — e.g., `Member Tier` merge field blank across all newly synced records after Pipedrive upgrade.

## Step-by-Step Fix

1. Fetch the v2 field schema and build an `id → key` map:
   ```python
   import requests
   token = "..."
   r = requests.get("https://api.pipedrive.com/v2/personFields",
                     headers={"Authorization": f"Bearer {token}"},
                     params={"limit": 500})
   id_to_key = {f["id"]: f["key"] for f in r.json()["data"]}
   ```
2. Refactor your middleware field map to use keys:
   ```python
   _FIELD_MAP = {
       "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2": "MEMBERTIER",  # Pipedrive key → Mailchimp merge tag
   }
   def to_mailchimp_merge(p):
       return {tag: p["custom_fields"].get(key, "")
               for key, tag in _FIELD_MAP.items()}
   ```
3. Handle email — it's now an array in v2:
   ```python
   def primary_email(p):
       for e in p.get("email", []):
           if e.get("primary"):
               return e["value"]
       return p.get("email", [{}])[0].get("value", "") if p.get("email") else ""
   ```
4. Wrong: re-add numeric IDs to the middleware (they no longer exist in v2 deal payloads). Correct: discard numeric IDs, build the `id→key` map once and persist.
5. Validate end-to-end with a sandbox contact — Pipedrive custom → Mailchimp merge — and verify the merge field is populated after upsert.

## Prevention

- After any Pipedrive v2 minor release, re-fetch `personFields` and `dealFields` schemas; hashes are stable but new fields only appear with hashes.
- Pin your integration to a specific data version header (`/v2`) — do not auto-upgrade with `Accept-version` ambiguity.
- Persist the field schema in a config file (commit to source control) so a parser change does not silently break field mapping.
- Add a nightly conformance test that picks 5 random Pipedrive contacts, syncs each to Mailchimp, and asserts the merge fields are non-blank — abort on first mismatch.
- Document the v1→v2 schema differences for your team so future maintenance avoids regressing back to numeric IDs.

## Integration-Specific Context

- **Native Pipedrive-Mailchimp connector**: updated by Pipedrive automatically; you do not need to act unless you depend on custom fields not mapped by the official connector.
- **Zapier Pipedrive app**: v2-ready since May 2026; old custom-field references in Zaps should be re-selected in the UI (Zapier shows them blank if the field key changed).
- **Make Pipedrive module**: same; ensure custom field dropdowns are re-picked in module config.
- **Custom middleware**: own the schema-cache rebuild; see snippet.
- **2026 change**: Pipedrive removed v1 endpoints entirely in June 2026; v1 calls now return `410 Gone` with a deprecation-resolver URL — you must migrate.

## People Also Ask

- **Why are my Pipedrive custom field IDs now 40-character strings?** Pipedrive v2 switched from numeric `id` keys to opaque 40-char hash strings in the deal/person payload JSON, with `id` retained only in the schema endpoint.
- **How do I migrate middleware from Pipedrive v1 to v2 custom fields?** Fetch `/personFields` and `/dealFields` once, build an `id → key` map, then use the hash keys to read `custom_fields` in v2 deal responses.
- **Does Pipedrive v2 still emit `email` as a string?** No — `email`, `phone`, `im` are now arrays of `{value, label, primary}` objects. Use the entry where `primary=true`.
- **Are Pipedrive v2 hash field keys stable across releases?** Yes for the lifetime of a custom field. Re-fetch the schema when new fields are created so your middleware learns the new hash.

## Official Documentation

**Pipedrive:**
- [API Docs](https://developers.pipedrive.com/docs/api/v1)
- [v2 Migration](https://pipedrive.readme.io/docs/migrating-from-v1-to-v2)

**Mailchimp:**
- [API Docs](https://mailchimp.com/developer/marketing/api/)
- [Lists](https://mailchimp.com/developer/marketing/api/lists/)

## Related Errors
- [Pipedrive person email not required](/integrations/pipedrive-to-mailchimp/errors/pipedrive-person-email-not-required)
- [Mailchimp daily list add limit](/integrations/pipedrive-to-mailchimp/errors/mailchimp-daily-list-add-limit)
- [Custom field type mismatch (Salesforce ↔ Mailchimp)](/integrations/salesforce-to-mailchimp/errors/custom-field-type-mismatch)
- [Pipedrive API Reference](/pipedrive)
- [Mailchimp API Reference](/mailchimp)