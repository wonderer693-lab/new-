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
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "pipedrive api 415 error"
  - "pipedrive 415 fix"
  - "pipedrive api feature is not enabled"
  - "pipedrive http 415"
---

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
