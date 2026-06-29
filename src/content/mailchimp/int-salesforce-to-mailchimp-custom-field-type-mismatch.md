---
layout: ../../layouts/IntegrationErrorLayout.astro
title: "Salesforce to Mailchimp Custom Field Type Mismatch — Dates and Numbers Reject"
description: "Salesforce sends date fields as ISO timestamps and numbers as strings; Mailchimp merge tags expect YYYY-MM-DD dates and number-typed fields. Resulting casts produce unusable merge data for segments and trigger email personalization."
toolA: "salesforce"
toolB: "mailchimp"
integrationSlug: "salesforce-to-mailchimp"
errorSlug: "custom-field-type-mismatch"
errorName: "Custom field type mismatch"
category: "FIELD_TYPES"
errorType: "error"
severity: "high"
priority: 2
lastUpdated: "2026-04-14"
lastReviewed: "2026-04-14"
pageType: "integration-error"
author: "API Integration Hub"
keywords:
  - "salesforce mailchimp merge field date format"
  - "mailchimp merge field type number text date"
  - "salesforce iso datetime mailchimp merge tag"
  - "mailchimp custom field type validation"
  - "salesforce to mailchimp date cast fail"
  - "mailchimp audience merge field types"
---

## The Problem

Mailchimp subscribers arrive with empty or obviously wrong merge fields after a Salesforce sync. Date fields render as raw ISO timestamps (`2026-06-26T18:43:00.000+0000`), numeric fields arrive as strings (`"5000"`), and groups fail validation entirely. Dynamic personalization in campaigns then displays `*|RENEW_DATE|*` literally because the field's value failed type validation on the Mailchimp side.

## Root Cause

- **Mailchimp merge fields are typed** per the merge tag config: `text`, `number`, `date`, `radio`, `dropdown`, `birthday`, `zip`, `phone`, `url`, `address`. Mailchimp validates POST bodies against the field's type and silently drops (`null`) the value on mismatch.
- **Salesforce REST API** returns dates as ISO 8601 full timestamps by default (`2026-06-26T18:43:00.000+0000`); Mailchimp date merge fields expect only `YYYY-MM-DD`.
- **Salesforce `Number` returned as JSON string** in some legacy `json` formats (`"5000"` rather than `5000`); Mailchimp's `number` reject type a field when a non-numeric string is sent.
- **Mailchimp `birthday` merge field** expects `MM/DD` (not `YYYY-MM-DD`), and `date` expects `YYYY-MM-DD`.

| Mailchimp type | Expected payload | Salesforce default payload | Result |
|---|---|---|---|
| `date` | `2026-06-26` | `2026-06-26T18:43:00+0000` | Drop/null |
| `number` | `5000` (or `5000.0`) | `"5000"` | Drop/null |
| `birthday` | `06/26` | `2026-06-26` | Drop/null |
| `text` | any string | JSON object | Drop/null |
| `url` | full URL | domain only | Drop/null |

## How to Detect If You're Affected

1. Pull a sample of Mailchimp members and inspect merge field values:
   ```bash
   curl -s "https://$DC.api.mailchimp.com/3.0/lists/$LIST/members?fields=members.email_address,members.merge_fields&count=20" \
     -H "Authorization: apikey $MC_KEY"
   ```
   Null dates/numbers across many members means type mismatch on write.
2. Send a test upsert and observe Mailchimp's response: `merge_fields` you sent that fail validation are silently dropped — the response body has no error, but the field is `null`.
3. Run a Salesforce-side `LastModifiedDate` export and compare to Mailchimp members; if Mailchimp shows nulls where Salesforce has data, this is the cause.
4. Test explicit bad payload to confirm Mailchimp behavior:
   ```bash
   HASH=$(echo -n "u@example.com" | md5sum | cut -d' ' -f1)
   curl -X PUT "https://$DC.api.mailchimp.com/3.0/lists/$LIST/members/$HASH" \
     -H "Authorization: apikey $KEY" -H "Content-Type: application/json" \
     -d '{"email_address":"u@example.com","merge_fields":{"RENEW":"2026-06-26T18:00:00Z"}}'
   ```
   Response shows `"RENEW":""` — silent drop.

## Step-by-Step Fix

1. Inspect Mailchimp field types once and build a typed marshaller:
   ```bash
   curl -s "https://$DC.api.mailchimp.com/3.0/lists/$LIST/merge-fields" \
     -H "Authorization: apikey $KEY" | jq '.merge_fields[] | {tag, name, type}'
   ```
2. Convert Salesforce dates server-side:
   ```python
   from datetime import datetime
   def sf_to_mc_date(s):
       return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%Y-%m-%d")
   def sf_to_mc_number(s):
       return float(s) if s not in (None, "") else None
   ```
3. Send only the cast-compatible payload:
   ```bash
   curl -X PUT "https://$DC.api.mailchimp.com/3.0/lists/$LIST/members/$HASH" \
     -H "Authorization: apikey $KEY" -H "Content-Type: application/json" \
     -d '{"email_address":"u@example.com","merge_fields":{"RENEW":"2026-06-26","LTV":5000.0}}'
   ```
4. Wrong: forward Salesforce JSON values verbatim (raw ISO into `RENEW`). Correct: drop the time-of-day component and use `YYYY-MM-DD`.
5. For `birthday` Mailchimp merge tags, convert to `MM/DD`:
   ```python
   "BDAY": sf_to_mc_date(s)[5:].replace("-", "/")  # → "06/26"
   ```

## Prevention

- Cache Mailchimp's merge field schema on each sync run and inspect the configured `type`; mismatches between new field definitions and cast logic often slip after admin changes.
- Rename merge fields to include type suffixes in your system (`RENEW_DATE`, `LTV_NUM`) so middleware types them automatically.
- Add a unit test that runs the marshallers on sample Salesforce rows — full ISO timestamps, leading zeros, None — and asserts Mailchimp accepts each.
- Pre-flight every POST body: cast, serialize, then verify with `jsonschema` that numbers are floats and dates match `YYYY-MM-DD`.
- Audit Mailchimp's `merge_fields` API monthly; admins often add fields with the wrong type from the UI and break the downstream sync.

## Integration-Specific Context

- **Native Salesforce-MC connector**: handles date conversion automatically but only for a curated list of fields; new fields require re-mapping.
- **Zapier Formatter**: use the "Format Date → YYYY-MM-DD" utility step before the Mailchimp action — most reliable approach in Zapier.
- **Make**: use the "Date Format" tool with custom pattern `yyyy-MM-dd` before the Mailchimp module.
- **Custom middleware**: see marshaller snippet above; never pass-through Salesforce ISO.
- **2026 change**: Mailchimp now supports `YYYY-MM-DD` and ISO for `date` (added late 2025) but returns them as `YYYY-MM-DD`; birthday still requires `MM/DD` strictly.

## People Also Ask

- **What date format does Mailchimp expect for a `date` merge field?** `YYYY-MM-DD`. Salesforce ships ISO 8601 timestamps which Mailchimp silently drops unless cast to `YYYY-MM-DD` server-side.
- **Can Mailchimp accept a number field as a string "5000"?** No — `number` merge fields reject string payloads; cast to a numeric value (`float(5000)`) before sending JSON.
- **How do I sync Salesforce picklists to Mailchimp dropdown fields?** Create matching Mailchimp dropdown options, then send the label as a string matching an option; Mailchimp rejects values absent from the option list.
- **Does Mailchimp error when a merge field fails validation?** No. The POST succeeds but the invalid field is set to empty silently — making detection hard; always test with a single record.

## Official Documentation

**Salesforce:**
- [REST API](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/)
- [Limits](https://developer.salesforce.com/docs/atlas.en-us.salesforce_app_limits_cheatsheet.meta/salesforce_app_limits_cheatsheet/)

**Mailchimp:**
- [API Docs](https://mailchimp.com/developer/marketing/api/)
- [Lists](https://mailchimp.com/developer/marketing/api/lists/)

## Related Errors
- [Email field mismatch (Salesforce ↔ Mailchimp)](/integrations/salesforce-to-mailchimp/errors/email-field-mismatch)
- [Mailchimp unsubscribes re-synced (Salesforce)](/integrations/salesforce-to-mailchimp/errors/mailchimp-unsubscribes-re-synced)
- [Custom field type mismatch (Salesforce ↔ ActiveCampaign)](/integrations/salesforce-to-activecampaign/errors/custom-field-type-mismatch)
- [Salesforce API Reference](/salesforce)
- [Mailchimp API Reference](/mailchimp)