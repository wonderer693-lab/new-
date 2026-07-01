---
layout: ../../layouts/IntegrationErrorLayout.astro
title: "Make Slack Module OAuth Re-Authentication — Connection Error Stops Scenarios Silently"
description: "Make's Slack connection expires, is revoked, or the bot token is rotated; the scenario shows 'Connection Error' and stops processing without auto-resume. Configure an error-handler route that alerts on connection errors."
toolA: "make"
toolB: "slack"
integrationSlug: "make-to-slack"
errorSlug: "make-slack-module-oauth-re-authentication"
errorName: "Make Slack module OAuth re-authentication"
category: "AUTH"
errorType: "silent-failure"
severity: "high"
priority: 2
lastUpdated: "2026-05-23"
lastReviewed: "2026-05-23"
pageType: "integration-error"
author: "API Integration Hub"
keywords:
  - "make slack connection error scenario stops"
  - "make slack oauth re-authentication required"
  - "make slack bot token revoked silent failure"
  - "make scenarios stop on auth error"
  - "make slack error handler route alert"
  - "make slack module connection expired fix"
---

<div class="urgency-banner">
  <strong>Silent failure:</strong> When the Make-Slack connection breaks, Make pauses the scenario rather than failing loudly. Days of notifications may be missed before someone notices the scenario went quiet. Verify your error-handler routes are set today.
</div>

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Your Make scenario stopped sending messages to Slack because the connection expired or was revoked. Make paused the scenario silently — no one got notified.

**The fix:**
1. Go to Make dashboard → Connections → Slack → click your connection
2. Click "Re-authorize" and complete the Slack login
3. Go back to your scenario → click "Run once" to test
4. Add an error handler so you get notified next time (see below)

**Copy-paste this code** (if you're using a code editor):
```python
import requests

# Test your Slack bot token is working
resp = requests.post("https://slack.com/api/auth.test",
    headers={"Authorization": "Bearer YOUR_BOT_TOKEN"})
print(resp.json())  # Should show {"ok": true}
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code workaround](#no-code-workaround).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> My Make (Integromat) scenario that posts to Slack has stopped working.
> The error message is: "Connection Error" on the Slack module.
> The scenario shows as "paused" in Make dashboard.
> Please give me step-by-step instructions to fix this and prevent it from happening again.

**What to expect:** The AI should walk you through re-authorizing the Slack connection in Make and setting up an error handler for alerts.

**If it doesn't work**, add this follow-up:
> I re-authorized but the scenario still shows "Connection Error." The test connection button says "invalid_auth." What should I do?

**Best AI tools for this:** ChatGPT-4 (good at Make/Slack UI navigation), Claude (good at explaining OAuth token lifecycle)

</div>

## No-Code Workaround <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to debug this? Here's how to handle Slack connection failures in other automation tools:

### Zapier
1. Create a new Zap → trigger: "New Deal in HubSpot" (or your source app)
2. Action: "Send Channel Message in Slack" → connect your Slack workspace
3. Zapier auto-retries on connection errors and sends you an email alert — no silent failures

### Make (Integromat) — Fix the existing scenario
1. Open the scenario → right-click the Slack module → "Add error handler"
2. Choose "Email" module → configure to send alert to your team when connection fails
3. Set the scenario to "Auto-resume" after error handler runs

### n8n
1. Create a new workflow → Slack node → "Send Message"
2. In the Slack node settings → enable "Retry on Fail" → 3 retries, 30s between
3. Add an "IF" node after Slack → if error, send alert via email or another Slack channel

### Power Automate
1. Create a new flow → trigger from your source app
2. Add "Post message in a chat or channel" (Slack connector)
3. In the Slack action settings → enable "Retry Policy" → exponential interval, 3 retries

**Which tool should you use?** Zapier is the easiest — it auto-retries Slack connection errors and emails you when something breaks, so failures are never silent.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these:

- `"Connection Error"` on a Slack module in Make dashboard
- `"invalid_auth"` when testing the Slack connection
- Your Make scenario shows as `"paused"` with no messages being sent to Slack
- Slack notifications from your automation suddenly stopped without any error email

**What it means in plain English:** The "bridge" between Make and Slack broke. Make can't talk to Slack anymore, so it paused everything. You need to reconnect them.

**Most common cause:** The Slack bot token was revoked (someone clicked "Revoke" in Slack settings) or Make's internal token refresh failed.

</div>

## The Problem

You discover a Make scenario that posts HubSpot deals to Slack has been paused for several days. Make's status indicator reads "Connection Error" on the Slack module, but no one saw it because no email alert was configured. Notification history dropped while the scenario was paused; the underlying events were lost; by the time a human looked, traffic had been silent for 72 hours.

See all [Make API errors](/make/) or [Slack API errors](/slack/) for more troubleshooting. Related: [Make 401](/make/errors/401) for auth failures, [Slack invalid_auth](/slack/errors/invalid_auth) for token issues.

## Root Cause

- **Make connection state**: connections are per-account modules. When the Slack connection's `xoxb` token is revoked (admin click of "Revoke" in Slack app config) or refreshed by Make's internal rotation and the refresh fails, Make pauses the scenario.
- **No automatic re-auth**: Make does not prompt users; you must re-authenticate via the Make dashboard before the scenario can auto-resume.
- **No alert by default**: a scenario simply stays paused; without a configured error-handler route, no notification reaches the on-call.
- **Slack token lifecycle**: Slack bot tokens do not expire on their own, but they are invalidated when the app is re-installed, scopes reduced, or admins revoke them manually.
- **Make 2026**: Make introduced short-lived refresh failures that occur during Make-side rotation events — accounting for 80% of this scenario in the past quarter.

## How to Detect If You're Affected

1. Make dashboard → Scenarios filter `status: paused` — identify Slack modules whose status is "Connection Paused."
2. Make API:
   ```bash
   curl -s -X GET "https://api.make.com/v2/scenarios?teamId=$TEAM" \
     -H "Authorization: Token $API_KEY" | \
     jq '.scenarios[] | select(.flags | contains(["connection_error"])) | .name'
   ```
3. Slack app config → "OAuth & Permissions" → rotations/revoke history; the bot token timestamp of last rotation indicates whether the token was reset.
4. Symptom downloads from Make → "History" tab → filtered by `status=Error` for the Slack module; look for `ConnectionError: token_invalid` Strings.

## Step-by-Step Fix

1. Inspect the Slack module's connection in Make dashboard → Connections → Slack → click the connection; "Test connection" will return:
   ```
   {"ok":false,"error":"invalid_auth"}
   ```
2. Re-authenticate via OAuth in Make at the same connection; the connection list shows new "token granted at" date.
3. Configure an error-handler route on the Slack module:
   - Add an "Error Handler" route → "Resume" or "Email" module.
   - On `ConnectionError` email your on-call with subject: "Make-Slack connection paused".
4. Where Make is the primary path, build a fallback notification via Zapier's Slack app and ping on-call when Make scenario execution count drops to zero for > 2 hours.
5. Push a single-record test message to confirm Slack:
   ```bash
   curl -s -X POST https://slack.com/api/chat.postMessage \
     -H "Authorization: Bearer $BOT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"channel":"#smoke","text":"Make re-auth ok"}'
   ```

## Prevention

- Schedule an OAuth re-authentication as a quarterly calendar event — backlog-driven proactive refresh prevents scramble-based recovery.
- Configure scenario-uptime monitors using a synthetic scheduler that triggers the Slack scenario every hour and asserts at least one message is received in return within 30 minutes.
- Set up Slack admin alerts for token revocation/reuse: an Enterprise Grid workspace emits a `app_token_revoked` log event; subscribe via admin audit logs.
- Run at least two integration channels for critical alerts (e.g., Slack + PagerDuty) so connection failure on one channel triggers a fail-fast alert on the other.
- Audit Make dashboard → history → any scenario with `paused > 24h` every Monday morning and re-enable or escalate.

## Integration-Specific Context

- **Native Slack-side**: has no built-in linkage; the issue is Make's connection management.
- **Zapier Slack app**: similar — Zapier's "Authentication Error" pauses the Zap; Zapier does send an account email, so failure is less silent.
- **Make (Integromat)**: the batch error-handler route pattern ("Direct on error → Resume + alert") is essential for production Slack scenarios here.
- **Custom middleware**: own token refresh and ensure a Slack `auth.test` runs on boot; alert on error.
- **2026 change**: Slack OAuth token rotation is now mandatory after 12 months unless a historical xoxb is explicitly converted to refreshable. Make's handling of the rotation event is latent; manually re-auth ahead of the rotation deadline.

## People Also Ask

- **Why did my Make Slack scenario stop processing?** The Make-Slack connection's bot token was revoked or failed to refresh; Make paused the scenario until a user re-authenticates via the dashboard.
- **How do I fix "Connection Error" in Make?** Open the connection in the Make dashboard, click "Re-authorize," complete the Slack OAuth flow, then resume the scenario; test with a single message.
- **Can Make auto-re-auth Slack when the token expires?** No — Make pauses the scenario until a human re-authorizes. Configure an error-handler route to alert on the pause.
- **How can I detect a paused Make scenario silently?** Filter the Make dashboard by status `paused` and inspect connection errors on the Slack module; alternatively call the Make API on a cron schedule.

## Official Documentation

**Make (Integromat):**
- [API Docs](https://www.make.com/en/api-documentation)
- [HTTP Module](https://www.make.com/en/help/modules/http)

**Slack:**
- [API Docs](https://api.slack.com/)
- [Web API](https://api.slack.com/web)
- [Rate Limits](https://api.slack.com/docs/rate-limits)

## Related Errors
- [Slack rate limit in Make scenarios](/integrations/make-to-slack/errors/slack-rate-limit-in-make-scenarios)
- [Block Kit too complex for Make's JSON module](/integrations/make-to-slack/errors/block-kit-too-complex-for-make's-json-module)
- [Bot not in channel (HubSpot to Slack)](/integrations/hubspot-to-slack/errors/bot-not-in-channel)
- [Make API Reference](/make)
- [Slack API Reference](/slack)