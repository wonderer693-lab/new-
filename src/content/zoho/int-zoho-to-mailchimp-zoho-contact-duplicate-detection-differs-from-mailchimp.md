---
layout: ../../layouts/IntegrationErrorLayout.astro
title: "Zoho Duplicate Detection Differs From Mailchimp — Email Unique Key Sync Conflict"
description: "Zoho CRM allows multiple contacts with the same email address; Mailchimp deduplicates strictly on email. Syncing Zoho to Mailchimp produces conflicts, 400 errors, and overwritten member records."
toolA: "zoho"
toolB: "mailchimp"
integrationSlug: "zoho-to-mailchimp"
errorSlug: "zoho-contact-duplicate-detection-differs-from-mailchimp"
errorName: "Zoho contact duplicate detection differs from Mailchimp"
category: "DATA_QUALITY"
errorType: "error"
severity: "high"
priority: 2
lastUpdated: "2026-06-06"
lastReviewed: "2026-06-06"
pageType: "integration-error"
author: "API Integration Hub"
keywords:
  - "zoho mailchimp duplicate email contacts"
  - "mailchimp unique email key sync conflict"
  - "zoho crm multiple contacts same email"
  - "mailchimp member overwrite duplicate"
  - "zoho to mailchimp 400 duplicate email"
  - "mailchimp merge field email md5 sync"
---

## The Problem

You run a sync from Zoho CRM contacts into a Mailchimp audience and partway through the batch you receive `400 Member Exists` for some records while other emails land on the wrong contact record. Mailchimp treats `email_address` as the primary key for an audience and will overwrite merge fields on the existing member, so two distinct Zoho contacts that happen to share an email collapse into one Mailchimp profile — typically the last one written wins.

## Root Cause

- **Zoho**: duplicate email detection is **optional** and disabled by default on most editions. `Duplicate_Check` is a field-level admin setting; many orgs leave it off so customer service can log a call against a shared inbox.
- **Mailchimp**: every list member is keyed on a lowercase normalized `email_address`. The MD5 of that normalized email (`id` field of the list member) is the immutable identifier. `PUT /lists/{list_id}/members/{subscriber_hash}` upserts on email alone.
- **Merge behavior**: a second Zoho contact with the same email but different `First_Name`/`Last_Name` overwrites the Mailchimp member's merge fields unless your middleware skips already-existing members.

| Scenario | Zoho behavior | Mailchimp behavior |
|---|---|---|
| 2 contacts, same email | Both allowed (admin setting) | Second overwrites first |
| Email differs in casing | Treated as distinct | Normalized — collapses to one |
| Email has trailing space | Stored as-is | Mailchimp normalizes & strips — collision |
| Email = shared alias (sales@) | Multiple contacts legitimately | One Mailchimp member, last write wins |

## How to Detect If You're Affected

1. Pull duplicate emails directly from Zoho:
   ```bash
   # ZohoContacts API via Coql
   curl -s "https://www.zohoapis.com/crm/v2/coql" \
     -H "Authorization: Zoho-oauthtoken $TOKEN" \
     -d '{"select_query":"select Email from Contacts where Email is not null"}' | \
     jq '.data | group_by(.Email) | map(select(length>1)) | length'
   ```
2. Compare Mailchimp audience size to Zoho "contacts with email" count — a smaller Mailchimp audience signals collapsed duplicates.
3. Inspect middleware logs for `Member Exists` errors (`title:"Member Exists"`, `status:400`) from `POST /lists/{id}/members`.
4. Sample five Mailchimp members and verify their `merge_fields` match a single Zoho record — mismatched first names are a collision fingerprint.

## Step-by-Step Fix

1. Resolve duplicates in Zoho before syncing. Detect them with a Coql query and decide winners:
   ```python
   import requests
   q = {"select_query": "select id, Email, First_Name, Last_Name, Modified_Time from Contacts where Email is not null order by Email"}
   r = requests.post("https://www.zohoapis.com/crm/v2/coql",
                      headers={"Authorization": f"Zoho-oauthtoken {token}"}, json=q).json()
   from collections import defaultdict
   buckets = defaultdict(list)
   for c in r["data"]:
       buckets[c["Email"].strip().lower()].append(c)
   dupes = {k: v for k, v in buckets.items() if len(v) > 1}
   ```
2. Choose a winner per email (e.g., latest `Modified_Time`) and add losers to a suppression list so they're skipped by the sync:
   ```python
   loser_ids = [c["id"] for es in dupes.values() for c in es[1:]]
   ```
3. Use `PUT /lists/{list_id}/members/{subscriber_hash}` and pass `status_if_new` so upsert is idempotent:
   ```bash
   HASH=$(echo -n "user@example.com" | md5sum | cut -d' ' -f1)
   curl -X PUT "https://$DC.api.mailchimp.com/3.0/lists/$LIST/members/$HASH" \
     -H "Authorization: apikey $MC_KEY" \
     -H "Content-Type: application/json" \
     -d '{"email_address":"user@example.com","status_if_new":"subscribed","merge_fields":{"FNAME":"Jane","LNAME":"Doe"}}'
   ```
4. Wrong (causes overwrite): reuse the `id` from Zoho as the Mailchimp subscriber hash. Mailchimp ignores it — only MD5(email) is used.

## Prevention

- Enable Zoho's `Duplicate_Check` on the Email field and set duplicate-resolution rules to "Block and warn" so future dups cannot be created.
- Normalize emails before sync (trim, lowercase, strip aliases) so `User@Example.com` and `user@example.com` don't both create separate Mailchimp records.
- Maintain a local "winner map" (email → preferred Zoho contact id) updated on every Zoho create/update; losers hit a skip log for data stewardship.
- Pre-flight every batch by hashing the email set in your middleware; abort if any hash collision appears in the inbound payload.
- Audit Mailchimp `merge_fields` monthly against Zoho for any field where Mailchimp shows the loser's name — those are silent collisions.

## Integration-Specific Context

- **Native Zoho-to-Mailchimp connector**: respects mailchimp's upsert, so overwrites still happen — there is no winner logic.
- **Zapier**: the "Add/Update Subscriber" action upserts on email by default; you cannot suppress it without a filter step.
- **Make (Integromat)**: use the "Iterator" + "Array Aggregator" pattern to dedupe by email before the Mailchimp module.
- **Custom middleware**: own the winner logic; the snippet above is the correct architecture.
- **2026 change**: Mailchimp Transactional/Audience API now strips trailing whitespace during normalize — older middleware that pre-trimmed also worked, but middleware that added a space to force uniqueness now silently breaks.

## People Also Ask

- **Does Mailchimp allow duplicate email addresses in one audience?** No. Mailchimp key members on a normalized lowercase email and upsert onto that key, so two contacts with the same address collapse into one profile.
- **Can Zoho CRM have two contacts with the same email?** Yes, unless the admin enables `Duplicate_Check` on the Email field, which is off by default.
- **How do I prevent two Zoho contacts overwriting each other in Mailchimp?** Pick a winner before sync, suppress losers with a skip log, and use `PUT /members/{hash}` with `status_if_new` so upsert is idempotent.
- **Why are my Mailchimp first names wrong after the Zoho sync?** A second Zoho contact with the same email overwrote the `FNAME` merge field because Mailchimp upserts on email.

## Official Documentation

**Zoho CRM:**
- [API Docs](https://www.zoho.com/crm/developer/docs/api/v3/)
- [OAuth](https://www.zoho.com/crm/developer/docs/api/v3/auth.html)

**Mailchimp:**
- [API Docs](https://mailchimp.com/developer/marketing/api/)
- [Lists](https://mailchimp.com/developer/marketing/api/lists/)

## Related Errors
- [Email field mismatch (Salesforce ↔ Mailchimp)](/integrations/salesforce-to-mailchimp/errors/email-field-mismatch)
- [Mailchimp unsubscribes re-synced (Salesforce)](/integrations/salesforce-to-mailchimp/errors/mailchimp-unsubscribes-re-synced)
- [Zoho OAuth token expires every hour](/integrations/zoho-to-mailchimp/errors/zoho-oauth-token-expires-every-hour)
- [Zoho CRM API Reference](/zoho)
- [Mailchimp API Reference](/mailchimp)