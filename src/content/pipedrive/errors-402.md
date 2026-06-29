---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Pipedrive API 402: Company account not open (trial expired, payment not ente..."
description: "Fix Pipedrive API 402 (402 Payment Required) error. Company account not open (trial expired, payment not entered). Verify subscription status in Pipedrive account settings."
tool: "pipedrive"
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
  - "pipedrive api 402 error"
  - "pipedrive 402 fix"
  - "pipedrive api company account not open"
  - "pipedrive http 402"
---

## What Causes Pipedrive 402

Pipedrive returns HTTP 402 when the company account is not in an active billing state — typically because a free trial has expired, payment information is missing or declined, or the subscription has been canceled. The API is fully blocked for all operations until billing is resolved.

The response is `{"error":"Company account not open (trial expired, payment not entered)"}`. This error appears on every API call regardless of the endpoint, as Pipedrive's billing system gates all API access. Unlike 403 (which blocks specific operations), 402 blocks everything.

### Common Scenarios
- Free trial period ended without upgrading to a paid plan
- Credit card on file expired or was declined for renewal
- Subscription manually canceled but API calls still being made
- Account suspended due to non-payment after the grace period
- New account with incomplete billing information

## How to Detect If You're Affected

1. Check the error message on any API call:
   ```bash
   curl -s "https://api.pipedrive.com/v1/deals?api_token=$TOKEN" | jq '.error'
   ```

2. Verify your account is open in the Pipedrive web UI: check Company Settings > Billing.

## Step-by-Step Fix

### 1. Check Subscription Status
```python
resp = requests.get(f"https://api.pipedrive.com/v1/companies?api_token={TOKEN}")
company = resp.json().get("data", {})
print(f"Company: {company.get('name')}")
print(f"Status: {'open' if company.get('status') == 'open' else 'closed'}")
```

### 2. Notify Billing Contact
```python
if "not open" in resp.json().get("error", ""):
    send_alert(
        subject="Pipedrive API blocked — account not open",
        message=f"Token {TOKEN[:8]}... is blocked due to billing issues. "
                "Resolve in Pipedrive Settings > Company > Billing."
    )
```

### 3. Resolve Billing
Access Pipedrive Settings > Company > Billing to update payment method, upgrade from trial, or renew subscription. Once billing is resolved, the API immediately starts working again without token changes.

## Prevention

- Set up payment method alerts in Pipedrive to notify before trials expire
- Use a dedicated billing monitoring endpoint (or the company API) to check account status daily
- Implement a 402 detection handler that sends an immediate ops alert — this is a high-severity issue
- Keep a backup API token from a separate Pipedrive account for critical operations
- Monitor Pipedrive billing emails and add the billing team as notification contacts

## Official Documentation

- [Pipedrive API Documentation](https://developers.pipedrive.com/docs/api/v1)
- [Pipedrive Billing Help](https://support.pipedrive.com/en/billing)
- [Pipedrive API Errors](https://developers.pipedrive.com/docs/api/v1/errors)

## People Also Ask

- **Why does Pipedrive return 402?** Your Pipedrive account is not in active billing status — trial expired, payment declined, or subscription canceled. Resolve billing in account settings.
- **Is Pipedrive 402 temporary?** It persists until billing is resolved. Once payment is processed, the API starts working again immediately.
- **Does Pipedrive 402 affect all API tokens?** Yes — the account-level billing block affects every API token associated with that Pipedrive account.
- **How do I know if my Pipedrive trial has expired?** You'll receive email notifications from Pipedrive, and all API calls will return 402 with "Company account not open (trial expired)".

## Related Errors

- [Pipedrive 403 Forbidden](/pipedrive/errors/403) — Request not allowed
- [Pipedrive 415 Feature Not Enabled](/pipedrive/errors/415) — Feature not enabled for account
- [Pipedrive 503 Service Unavailable](/pipedrive/errors/503) — Scheduled maintenance
