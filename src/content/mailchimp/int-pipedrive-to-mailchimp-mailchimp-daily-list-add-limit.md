---
layout: ../../layouts/IntegrationErrorLayout.astro
title: "Mailchimp Daily List Add Limit — Pipedrive Bulk Sync Rejected Subscribers"
description: "Mailchimp enforces a daily add-subscribers cap based on your plan; a Pipedrive bulk sync that exceeds it stops adding new members mid-batch. Monitor subscriber count vs plan limit, spread bulk syncs over multiple days, and prune inactive contacts first."
toolA: "pipedrive"
toolB: "mailchimp"
integrationSlug: "pipedrive-to-mailchimp"
errorSlug: "mailchimp-daily-list-add-limit"
errorName: "Mailchimp daily list add limit"
category: "RATE_LIMIT"
errorType: "error"
severity: "high"
priority: 2
lastUpdated: "2026-05-27"
lastReviewed: "2026-05-27"
pageType: "integration-error"
author: "API Integration Hub"
keywords:
  - "mailchimp daily list add limit per plan"
  - "pipedrive mailchimp bulk sync rejected"
  - "mailchimp subscriber limit exceeded error"
  - "mailchimp 400 too many subscribers"
  - "pipedrive to mailchimp daily add cap fix"
  - "mailchimp audience member count quota"
---

## The Problem

You bulk-sync 5,000 Pipedrive persons to a Mailchimp audience; the first ~750 succeed and the next 4,250 fail every time. The Mailchimp dashboard reads "your daily add-subscriber limit has been reached for this audience." No error is logged in middleware beyond a generic 400; meanwhile the Mailchimp audience only grew by a fraction of the intended count.

## Root Cause

- **Mailchimp daily add-subscriber quota** ranges from about 500/day on the Free plan, 25,000/day on Essentials, up to 75,000 on Premium (figures vary by account; check "Account & Billing" → "Plan details"). The cap is per audience and per day.
- **Cap counts new members only**: updating existing members and updating `merge_fields` do not count, but adding a new email does. Pipedrive email-confirmations and re-engagement imports incur lots of new members.
- **HTTP error**: 400 with title "Daily Add Limit Reached," body:
  ```json
  {"type":"http://mailchimp.com/...", "title":"Daily Add Limit Reached", "status":400, "detail":"You have reached your daily add limit..."}
  ```
- **No `Retry-After`**: Mailchimp does not tell you when you can resume; you must wait until midnight UTC (or your audience's timezone reset).
- **Pipedrive side**: bulk sync triggers from a marketing import do not honor Mailchimp's quota; they'll keep retrying the Mailchimp call forever.

| Mailchimp plan | Approx. daily add cap |
|---|---|
| Free | ~500 |
| Essentials | ~5,000–25,000 based on tier |
| Standard | ~75,000 |
| Premium | ~75,000 |

## How to Detect If You're Affected

1. Middleware log of the literal Mailchimp response:
   ```bash
   rg 'Daily Add Limit' middleware.log
   ```
2. Mailchimp API call error field:
   ```python
   r = requests.post(f"https://{dc}.api.mailchimp.com/3.0/lists/{LIST}/members", ...force=True)
   if r.json().get("title") == "Daily Add Limit Reached":
       halt_and_alert()
   ```
3. Check audience counts on the dashboard: if new subscribers stop growing mid-batch, this is the cause.
4. Periodic dashboard check under "Audience → Signup forms → Signups today" – a quick view of daily count.

## Step-by-Step Fix

1. Pre-emptively query Mailchimp's audience "new_today" via a daily count tracker:
   ```bash
   ADDED=$(curl -s "https://$DC.api.mailchimp.com/3.0/lists/$LIST?fields=stats.member_count_since_send" \
     -H "Authorization: apikey $KEY" | jq '.stats.member_count_since_send')
   if (( ADDED > CAP-100 )); then exit 0; fi
   ```
2. Spread bulk syncs over multiple days using a job queue in middleware:
   ```python
   import datetime, json
   batches = split(mailchimp_batch, 750)  # Safe under Free-tier daily cap of 500
   schedule = []
   for i, b in enumerate(batches):
       schedule.append({"day": datetime.date.today() + datetime.timedelta(days=i),
                        "records": [r["email_address"] for r in b]})
   ```
3. Prefer `PUT /members/{hash}` (idempotent upsert) — but bear in mind that "adds" still count toward the daily limit when the email doesn't yet exist.
4. Use `POST /lists/{list_id}` `members` with `status_if_new="pending"` for a clean compliance track if you're catching double-opt-in via marketing campaign.
5. Prune inactive Mailchimp contacts first to free up "audience room" if you are at your subscription cap, not just your add cap:
   ```bash
   curl -X POST "https://$DC.api.mailchimp.com/3.0/lists/$LIST/members/6a258b22af2425/use_batch?..."
   ```

## Prevention

- Sync daily with a small batch (250) rather than monthly with 5,000 — Mailchimp's daily cap tolerates slow streams.
- Use a job scheduler with persistent state so a failed batch resumes the next day when the cap resets.
- Pre-filter Pipedrive persons before delivery: skip emails that already exist as Mailchimp members (only new emails count toward the cap; his email being an `unsubscribed` contact still counts).
- For the Free/Lite segments, route larger batches through a Mailchimp Transactional Email add-on (Mandrill) or upgrade mid-campaign if approaching $ ROI threshold.
- Set an alert at 80% of the cap daily so you can dip before hitting 100 and deploying a fix.

## Integration-Specific Context

- **Native Pipedrive-Mailchimp connector**: hits the same cap; the connector halts and reserves a manual resume.
- **Zapier**: behavior is zap-by-zap; you can throttle individual Zaps via the "Delay After Queue" to stay under the cap.
- **Make**: chunk via array iterator + "Sleep" module; bulk batches can still exceed the cap rate of Mailchimp.
- **Custom middleware**: snippet above is correct, schedule-based multi-day throughput.
- **2026 change**: Mailchimp rolled out a beta "daily add limit warning" via Dashboard API in Spring 2026 — query it to programmatically back off.

## People Also Ask

- **What's Mailchimp's daily subscriber add limit?** Free caps around 500/day, Essentials 5,000–25,000/day depending on tier, Standard/Premium ~75,000/day. The limit is per audience per day.
- **Why does my Pipedrive sync to Mailchimp fail partway through?** You've hit Mailchimp's daily add-subscriber cap based on your plan; the remaining subscribers get 400 errors until midnight reset.
- **Does updating an existing Mailchimp member count toward the daily add limit?** No — only new emails. `PUT /members/{hash}` for an existing email is counted as an update, not an add.
- **How do I avoid Mailchimp's daily add limit on bulk Pipedrive imports?** Split the list into ≤500-record batches scheduled across multiple days and idempotently resume from the last successfully-added email.

## Official Documentation

**Pipedrive:**
- [API Docs](https://developers.pipedrive.com/docs/api/v1)
- [Authentication](https://developers.pipedrive.com/docs/api/v1/#/Authentication)

**Mailchimp:**
- [API Docs](https://mailchimp.com/developer/marketing/api/)
- [Lists](https://mailchimp.com/developer/marketing/api/lists/)

## Related Errors
- [Pipedrive person email not required](/integrations/pipedrive-to-mailchimp/errors/pipedrive-person-email-not-required)
- [Pipedrive v2 hash key field IDs in custom data](/integrations/pipedrive-to-mailchimp/errors/pipedrive-v2-hash-key-field-ids-in-custom-data)
- [Zoho API rate limit (250 req/min)](/integrations/zoho-to-mailchimp/errors/zoho-api-rate-limit-(250-req-min))
- [Pipedrive API Reference](/pipedrive)
- [Mailchimp API Reference](/mailchimp)