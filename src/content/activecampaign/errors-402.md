---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "ActiveCampaign API 402: Account payment issues"
description: "Fix ActiveCampaign API 402 (402 Payment Required) error. Account payment issues — subscription expired or billing problem. Check account billing status in ActiveCampaign settings."
tool: "activecampaign"
errorCode: "402"
errorName: "402 Payment Required"
httpStatus: 402
category: "billing"
severity: "medium"
priority: 2
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "activecampaign api 402 error"
  - "activecampaign 402 fix"
  - "activecampaign api account payment issues —"
  - "activecampaign http 402"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Your ActiveCampaign plan doesn't allow this API feature, or your subscription has a billing issue.

**The fix:**
1. Log into ActiveCampaign → Settings → Billing
2. Check for overdue invoices or an expired payment method
3. Update your payment info or upgrade your plan to restore API access

**Copy-paste this code** (if you're using a code editor):
```python
import requests

headers = {"Api-Token": "YOUR_TOKEN"}
resp = requests.get("https://{account}.api-us1.com/api/3/contacts", headers=headers)
if resp.status_code == 402:
    print("Billing issue — fix payment in ActiveCampaign Settings > Billing")
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm getting a 402 Payment Required error from the ActiveCampaign API.
> The error message is: "Account payment issues"
> My integration was working before but now all API calls fail with 402.
> Please tell me what this means and how to fix it step by step.

**What to expect:** The AI should explain that this is a billing problem (not a code problem) and walk you through checking your ActiveCampaign subscription.

**If it doesn't work**, add this follow-up:
> I've updated my payment method but I'm still getting 402 errors. How long does it take for API access to come back?

**Best AI tools for this:** ChatGPT-4 (good at explaining billing flows), Claude (clear step-by-step guidance)

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to check ActiveCampaign plan limits in popular automation tools:

### Zapier
1. Open your Zap → check if the ActiveCampaign step shows a 402 error in the task history
2. Log into ActiveCampaign web app → Settings → Billing to verify your subscription is active
3. Once billing is fixed, re-test the Zap step — no Zapier changes needed

### Make (Integromat)
1. Open your scenario → check the history for 402 errors on ActiveCampaign modules
2. Verify your ActiveCampaign subscription at Settings → Billing in the web app
3. After fixing billing, click "Run once" to test the scenario again

### n8n
1. Open your workflow → check execution logs for 402 status codes on ActiveCampaign nodes
2. Confirm your ActiveCampaign plan is active and paid at Settings → Billing
3. Re-execute the workflow manually after billing is resolved

### Power Automate
1. Open your flow → check run history for failed ActiveCampaign actions with 402 status
2. Go to ActiveCampaign web app → Settings → Billing and fix any payment issues
3. Re-run the flow after billing is resolved

**Which tool should you use?** This error is always fixed in ActiveCampaign's billing page — no automation tool changes needed. Just fix the payment and re-run.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"402 Payment Required"`
- `"upgrade required"`
- `"Account payment issues"`
- `"Subscription expired"` in your integration logs

**What it means in plain English:** ActiveCampaign is blocking your API access because of a billing problem. Your subscription may have expired, your credit card may have been declined, or you need to upgrade your plan.

**Most common cause:** A credit card on file expired or a trial period ended without adding a payment method.

</div>

## What Causes ActiveCampaign 402

ActiveCampaign returns HTTP 402 when the account has an active billing issue — typically an expired subscription, failed payment, or account suspension. This is a rarely-seen error in API integrations because ActiveCampaign blocks all API access when billing is not current.

The error indicates a subscription-level problem, not an API request issue. Unlike 401 (authentication) or 403 (permissions), 402 means the account itself is not in good standing. The response usually contains `{"errors":[{"title":"402 Payment Required","detail":"Account payment issues."}]}`.

### Common Scenarios
- Subscription trial period ended and no payment method was added
- Credit card on file expired or was declined for the monthly charge
- Account was manually suspended due to non-payment
- Subscription plan was downgraded to a tier that doesn't include API access

## How to Detect If You're Affected

1. Check all API endpoints return 402:
   ```bash
   curl -s -w "\n%{http_code}" "https://{account}.api-us1.com/api/3/contacts" \
     -H "Api-Token: $TOKEN" | tail -1
   ```
   If 402, the entire account has a billing issue.

2. Log into ActiveCampaign and check billing status:
   ```bash
   # No API endpoint for billing status — check manually at:
   # Settings > Billing > Subscription Details
   ```

3. Verify account access via ActiveCampaign web UI: if you can't log in to the web app, the account is suspended.

## Step-by-Step Fix

### 1. Check Billing Status in ActiveCampaign
Log in to ActiveCampaign at `https://{account}.activehosted.com`. Navigate to Settings > Billing. Look for:
- Overdue invoices
- Expired payment method
- Subscription end date

### 2. Update Payment Method
```python
# No API fix — must be done via web UI
print("Log into ActiveCampaign web app")
print("Go to Settings > Billing")
print("Update payment method or renew subscription")
print("API access resumes once billing is resolved")
```

### 3. Verify API Access Restored
```bash
curl -s -w "\n%{http_code}" "https://{account}.api-us1.com/api/3/contacts" \
  -H "Api-Token: $TOKEN" | tail -1
# Should return 200 after billing is resolved
```

## Prevention

- Set up automatic payment notifications in ActiveCampaign billing settings
- Use a corporate credit card with auto-pay to prevent accidental expiration
- Monitor ActiveCampaign account status emails and add them to your monitoring inbox
- Keep a backup payment method on file
- Set a calendar reminder for subscription renewal dates

## Official Documentation

- [ActiveCampaign Billing](https://help.activecampaign.com/hc/en-us/articles/360020815760-Billing-overview)
- [ActiveCampaign API Overview](https://developers.activecampaign.com/reference/overview)

## People Also Ask

- **Why does ActiveCampaign return 402?** The account has an unpaid invoice, expired subscription, or failed payment. All API access is blocked until billing is resolved.
- **Can I check billing status via the API?** No — billing status must be checked via the ActiveCampaign web UI at Settings > Billing.
- **How long after payment does API access resume?** Usually within minutes of successful payment. If still blocked after 24 hours, contact ActiveCampaign support.
- **Does downgrading my plan cause 402?** Possibly — if the new plan doesn't include API access, you'll get 402 errors. Verify your plan includes API features.

## Related Errors

- [ActiveCampaign 401 Unauthorized](/activecampaign/errors/401) — Invalid or missing API token
- [ActiveCampaign 403 Forbidden](/activecampaign/errors/403) — Authenticated but not authorized
