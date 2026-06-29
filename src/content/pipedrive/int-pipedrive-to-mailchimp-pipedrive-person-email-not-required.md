---
layout: ../../layouts/IntegrationErrorLayout.astro
title: "Pipedrive Person Email Not Required — Mailchimp Sync Silently Skips Contacts"
description: "Pipedrive persons can be created without an email; Mailchimp requires email as a member's primary key. Persons with no email are silently skipped by the sync. Filter null-email persons and log them for data enrichment."
toolA: "pipedrive"
toolB: "mailchimp"
integrationSlug: "pipedrive-to-mailchimp"
errorSlug: "pipedrive-person-email-not-required"
errorName: "Pipedrive person email not required"
category: "DATA_QUALITY"
errorType: "silent-failure"
severity: "high"
priority: 2
lastUpdated: "2026-05-20"
lastReviewed: "2026-05-20"
pageType: "integration-error"
author: "API Integration Hub"
keywords:
  - "pipedrive person email optional mailchimp sync"
  - "pipedrive contact no email mailchimp skip"
  - "mailchimp email required silent sync skip"
  - "pipedrive email array primary v2"
  - "pipedrive mailchimp missing member"
  - "pipedrive email field not mandatory integration"
---

<div class="urgency-banner">
  <strong>Silent failure:</strong> Pipedrive contacts without a primary email are skipped by the Mailchimp sync without an error. The Mailchimp audience is silently short compared to Pipedrive. Compare counts today.
</div>

## The Problem

You onboard a list of Pipedrive persons into a Mailchimp audience for the first launch and discover the audience is short of the Pipedrive count. There were no error logs from the middleware. The root cause: a chunk of Pipedrive persons were created without an email address, and Mailchimp requires email as the member primary key, so the integration silently passed them over.

## Root Cause

- **Pipedrive** (`/persons` endpoint): the `email` field is **optional**. Many sales-rep workflows create phone-only persons; some imports create persons with only `name`.
- **Pipedrive v2** wraps email as an array of `{value,label,primary,}` objects — `email = []` is valid, as are null entries with `value=""`.
- **Mailchimp** requires `email_address` on `POST /lists/{list_id}/members`. The v3 API rejects only when the field is missing; middleware often pre-filters and skips silently.
- **Mailchimp subscriber hash** is MD5(normalize(email)) — null email has no hash, so `PUT /members/{hash}` has no target.
- **Sales-rep workflow**: phone-only persons get created in Pipedrive; the sync rule "Mailchimp requires email" is enforced at the destination, never the source.

| Pipedrive state | Sync behavior | Mailchimp result |
|---|---|---|
| `email=[]` | Middleware skips | No member |
| `email=[{value:""}]` | Looks filled but empty value | No member |
| `email=[{value:"x@y"}]` | Normal | Member created |
| Person with email "primary=false" only | Middleware reads `email[0]` regardless | Still syncs but uses non-primary |

## How to Detect If You're Affected

1. Count Pipedrive persons with no populate phone-email vs Mailchimp members:
   ```bash
   curl -s "https://api.pipedrive.com/v2/persons?fields=id,email&limit=500" \
     -H "Authorization: Bearer $TOKEN" | \
     jq '[.data[] | select((.email | length) == 0)] | length'
   ```
2. Compare Mailchimp audience size to Pipedrive person count:
   ```bash
   curl -s "https://$DC.api.mailchimp.com/3.0/lists/$LIST?fields=stats.member_count" \
     -H "Authorization: apikey $MC_KEY"
   ```
3. Look in middleware logs for skip events: `rg -i 'skip.*email' middleware.log`.
4. Symptom: many "Sync" tasks succeed yet Mailchimp audience barely grows day over day.

## Step-by-Step Fix

1. Filter Pipedrive persons by `email.length >= 1 && value != ""` before sync:
   ```python
   def should_sync(person):
       for e in person.get("email") or []:
           if e.get("primary") and e.get("value", "").strip():
               return True
       return False
   unsync = [p for p in persons if not should_sync(p)]
   ```
2. Persist a skip log of unsynced persons for data enrichment:
   ```python
   import csv
   with open("skipped_persons.csv","w") as f:
       w = csv.writer(f); w.writerow(["id","name","phone"])
       for p in unsync:
           phones = [ph.get("value") for ph in p.get("phone",[]) if ph.get("value")]
           w.writerow([p["id"], p["name"], ", ".join(phones)])
   ```
3. Choose the primary email — don't blindly take `email[0]`:
   ```python
   email = next((e["value"] for e in person["email"] if e.get("primary")), "")
   or
   email = person["email"][0]["value"] if person.get("email") else ""
   ```
4. UPSERT into Mailchimp using `PUT /members/{md5}` with `status_if_new`:
   ```bash
   HASH=$(echo -n "$EMAIL" | md5sum | cut -d' ' -f1)
   curl -X PUT "https://$DC.api.mailchimp.com/3.0/lists/$LIST/members/$HASH" \
     -H "Authorization: apikey $MC_KEY" -H "Content-Type: application/json" \
     -d "{\"email_address\":\"$EMAIL\",\"status_if_new\":\"subscribed\"}"
   ```
5. Wrong: emit `200 OK` for skipped persons. Correct: emit a skip event and write to a data-steward list so operators can enrich emails.

## Prevention

- Pre-validate at the source: create a Pipedrive field requirement (via the API field-configuration) that flags persons lacking email; sync them only after email backfill.
- Treat skipped records as p1 backlog — a quarterly review meeting pulls the skip CSV and assigns enrichment work.
- Use Pipedrive's "primary email" concept (`primary=true`) consistently — avoid mailing contacts via non-primary addresses.
- Audit Mailchimp member counts against Pipedrive person counts every Monday; alert on drift > 1%.
- Back-check weekday imports — a CRM gave-onboard data import often creates no-email persons during bulk upload, even if the user-facing form requires them.

## Integration-Specific Context

- **Native Pipedrive-Mailchimp connector**: silently includes only `email`-populated persons; no skip log.
- **Zapier Pipedrive-Mailchimp**: the "Create Subscriber" action stops the Zap with the Mailchimp error if email is missing — better visibility than custom Middleware.
- **Make**: use a filter on `email[1]:empty` — bundle iteration of skipped persons counts against "operations" billing, but they produce zero side-effects.
- **Custom middleware**: own the skip-list enrichment loop — `skipped_persons.csv` in the snippet.
- **2026 change**: Pipedrive released "email quality scoring" (paid add-on) — persons with invalid emails now get a `quality` field; pre-filter to skip low-quality addresses before driving Mailchimp.

## People Also Ask

- **Does Mailchimp require an email when adding a list member?** Yes — `email_address` is mandatory on `POST /lists/{list_id}/members`; it is the unique member key.
- **Can I create a Pipedrive person without an email?** Yes — Pipedrive auto allows you to create a person with only name or phone; some sales reps do this for phone-only prospects.
- **How do I detect Pipedrive persons my Mailchimp sync skipped?** Count Pipedrive persons with empty `email` arrays and compare with the Mailchimp member delta for the period; bias toward >0 indicates silent skips.
- **What is Mailchimp's "member status_if_new" parameter?** It tells the API which status (e.g., `subscribed`, `pending`) to set if creating a new member for that email; existing members retain their status, making upserts idempotent.

## Official Documentation

**Pipedrive:**
- [API Docs](https://developers.pipedrive.com/docs/api/v1)
- [v2 Migration](https://pipedrive.readme.io/docs/migrating-from-v1-to-v2)

**Mailchimp:**
- [API Docs](https://mailchimp.com/developer/marketing/api/)
- [Lists](https://mailchimp.com/developer/marketing/api/lists/)

## Related Errors
- [Pipedrive v2 hash key field IDs in custom data](/integrations/pipedrive-to-mailchimp/errors/pipedrive-v2-hash-key-field-ids-in-custom-data)
- [Mailchimp daily list add limit](/integrations/pipedrive-to-mailchimp/errors/mailchimp-daily-list-add-limit)
- [Email field mismatch (Salesforce ↔ Mailchimp)](/integrations/salesforce-to-mailchimp/errors/email-field-mismatch)
- [Pipedrive API Reference](/pipedrive)
- [Mailchimp API Reference](/mailchimp)