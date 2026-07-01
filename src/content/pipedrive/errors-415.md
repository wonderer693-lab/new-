---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Pipedrive API 415: Feature is not enabled for the account"
description: "Fix Pipedrive API 415 (415 Unsupported Media Type) error. Feature is not enabled for the account. Check Pipedrive subscription plan for feature availability."
tool: "pipedrive"
errorCode: "415"
errorName: "415 Unsupported Media Type"
httpStatus: 415
category: "configuration"
severity: "low"
priority: 2
lastUpdated: '2026-05-10'
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "pipedrive api 415 error"
  - "pipedrive 415 fix"
  - "pipedrive api feature is not enabled"
  - "pipedrive http 415"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Pipedrive doesn't accept your request — the feature you're trying to use isn't available on your plan.

**The fix:**
1. Check which Pipedrive plan you're on at Settings > Company > Subscription
2. See if the feature you need (webhooks, email sync, etc.) requires a higher plan
3. Upgrade your plan or use an alternative approach (like polling instead of webhooks)

**Copy-paste this code** (if you're using a code editor):
```python
import requests

resp = requests.get(
    "https://api.pipedrive.com/v1/webhooks?api_token=TOKEN"
)
if resp.status_code == 415:
    print("Feature not on your plan — check Settings > Subscription")
    print("Alternative: use polling instead of webhooks")
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Give your AI as much detail as you can. Paste this:

> I'm getting a 415 error from the Pipedrive API.
> The error message is: "Feature is not enabled for the account"
> I'm trying to use webhooks but my plan might not support them.
> Please give me code to detect which features are available and suggest fallback approaches.

The AI should return feature detection code and alternative approaches when premium features aren't available on your plan.

If you're still seeing errors, send a second prompt with what you tried:
> The fix didn't work. Here's the endpoint I'm calling: [paste URL]. Is there an alternative way to do this?

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to handle Pipedrive feature-not-enabled errors in popular automation tools:

### Zapier
1. Open your Zap → check the error log for 415 errors on Pipedrive steps
2. Check your Pipedrive plan at Settings > Company > Subscription to see if the feature is included
3. If the feature isn't available, switch to a different Zapier trigger (use "New Deal" polling instead of webhooks)

### Make (Integromat)
1. Open your scenario → check the history for 415 errors
2. Verify your Pipedrive plan supports the feature you're using
3. Replace the webhook module with a polling module (e.g., "Watch Deals" instead of "Watch Webhooks")

### n8n
1. Open your workflow → check the execution log for 415 status codes
2. Check if your Pipedrive plan includes the feature at Settings > Subscription
3. Switch from webhook triggers to polling triggers if webhooks aren't available on your plan

### Power Automate
1. Open your flow → check run history for 415 failures
2. Verify your Pipedrive subscription includes the feature
3. Use a "Recurrence" trigger with a "Get items" action instead of webhook-based triggers

**Which tool should you use?** Zapier has the best fallback options — it offers both webhook and polling triggers for Pipedrive, so you can switch easily.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"415 Unsupported Media Type"`
- `"Feature is not enabled for the account"`
- `"content-type"` errors in Pipedrive context
- `"HTTP 415"` in your integration logs

**What it means in plain English:** The Pipedrive feature you're trying to use isn't included in your subscription plan. Despite the technical-sounding name, it's not about content types — it's about your plan level.

**Most common cause:** Trying to use webhooks, email sync, or advanced features on a basic Pipedrive plan that doesn't include them.

</div>

## What Causes Pipedrive 415

Pipedrive returns HTTP 415 when you attempt to use an API feature that is not enabled on your Pipedrive subscription plan. Despite the HTTP status code name "Unsupported Media Type", Pipedrive uses 415 to indicate that a specific feature (not the content type) is not available on your plan.

The response is `{"error":"Feature is not enabled for the account"}`. Features like custom fields, webhooks, advanced permissions, email sync, and certain API endpoints require specific Pipedrive subscription tiers. Using any of these features on a plan that doesn't support them triggers this error.

### Common Scenarios
- Calling webhook endpoints on a plan without webhook support
- Accessing email sync or email tracking features on a basic plan
- Using advanced permission set endpoints on a plan without permission features
- Attempting to access marketing or campaigns features on a sales-only plan
- Using v2 API endpoints that require a plan upgrade

## How to Detect If You're Affected

1. Check the error message:
   ```bash
   curl -s "https://api.pipedrive.com/v1/webhooks?api_token=$TOKEN" | jq '.error'
   ```

2. Review your plan features on the Pipedrive dashboard under Company Settings > Subscription.

## Step-by-Step Fix

### 1. Identify the Unsupported Feature
```python
resp = requests.get(f"https://api.pipedrive.com/v1/webhooks?api_token={TOKEN}")
error = resp.json().get("error", "")
if "not enabled" in error.lower():
    print("This feature requires a plan upgrade")
```

### 2. Check Your Plan Details
```python
resp = requests.get("https://api.pipedrive.com/v1/companies?api_token={TOKEN}")
company = resp.json().get("data", {})
print(f"Plan: {company.get('plan')}")
print(f"Features: {company.get('features')}")
```

### 3. Upgrade Plan or Switch Feature
```python
# Option A: Upgrade to a plan that includes the feature
# Option B: Use an alternative API approach
if "webhooks" not in enabled_features:
    print("Webhooks not available — use polling instead")
    # Fall back to polling via GET requests
```

## Prevention

- Check your Pipedrive plan features at integration setup time and fail fast if required features are missing
- Document which Pipedrive plan is required for your integration
- Implement feature detection — query available features before attempting to use them
- Provide fallback mechanisms when premium features are unavailable
- Test integration against the same plan tier as your production target

## Official Documentation

- [Pipedrive Plans and Pricing](https://www.pipedrive.com/pricing)
- [Pipedrive API Documentation](https://developers.pipedrive.com/docs/api/v1)
- [Pipedrive API Errors](https://developers.pipedrive.com/docs/api/v1/errors)

## People Also Ask

- **Why does Pipedrive return 415?** The specific API feature you're trying to use is not included in your current subscription plan. Check your plan features and upgrade if needed.
- **Does Pipedrive 415 mean my content type is wrong?** Despite the standard HTTP meaning of 415, Pipedrive uses this code to indicate a feature is not enabled on your plan — not an actual `Content-Type` issue.
- **How do I check which features my Pipedrive plan has?** Check Company Settings > Subscription in the Pipedrive web UI, or call the company API endpoint.
- **Can I use Pipedrive webhooks on the Essential plan?** No — webhooks typically require at least the Advanced plan or higher. Check Pipedrive's pricing page for specific feature availability by plan.

## Related Errors

- [Pipedrive 402 Payment Required](/pipedrive/errors/402) — Company account not open (trial expired)
- [Pipedrive 403 Forbidden](/pipedrive/errors/403) — Request not allowed
- [Pipedrive 404 Not Found](/pipedrive/errors/404) — Resource unavailable

See all [Pipedrive API errors](/pipedrive/) in our complete reference. Similar content-type issues occur with [HubSpot 400](/hubspot/errors/400) for request format errors. This error also affects integrations — see our [Pipedrive to Mailchimp integration errors](/integrations/pipedrive-to-mailchimp/) for common cross-tool issues.
