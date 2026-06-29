---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Calendly API 403: Insufficient permissions or subscription level"
description: "Fix Calendly API 403 error. Insufficient permissions or subscription level. Check user role and subscription."
tool: "calendly"
errorCode: "403"
errorName: "403"
httpStatus: 403
category: "permission"
severity: "high"
priority: 1
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "calendly api 403 error"
  - "calendly 403 fix"
  - "calendly api insufficient permissions or subscription"
  - "calendly http 403"
---

## What Causes Calendly 403

Calendly returns HTTP 403 when the authenticated token is valid but the user or their subscription plan doesn't have permission to access the requested resource. This is common for webhook subscriptions (which require a paid Premium plan) and for resources scoped to organization admins only.

The response contains `{"message":"Forbidden","errors":[{"message":"Insufficient permissions or subscription level"}]}`. Calendly has different API access tiers — free accounts have very limited API access, and certain endpoints are restricted to organization-level operations that require admin privileges.

### Common Scenarios
- Creating webhook subscriptions on a free Calendly account (requires Premium)
- Accessing organization-scoped resources without admin permissions
- Listing users in an organization when the token is scoped to a single user
- Updating event type settings that require owner-level access

## How to Detect If You're Affected

1. Check subscription plan:
   ```bash
   curl -s "https://api.calendly.com/users/me" \
     -H "Authorization: Bearer $TOKEN" | jq '.resource.current_organization'
   ```

2. Test specific endpoints to identify permission boundaries:
   ```bash
   # Webhook subscriptions often trigger 403 on free plans
   curl -s -w "\n%{http_code}" "https://api.calendly.com/webhook_subscriptions" \
     -H "Authorization: Bearer $TOKEN" | tail -1
   ```

3. Check the error detail for the specific restriction:
   ```bash
   curl -s "https://api.calendly.com/webhook_subscriptions" \
     -H "Authorization: Bearer $TOKEN" | jq '.errors'
   ```

## Step-by-Step Fix

### 1. Check Current User's Organization Role
```python
resp = requests.get("https://api.calendly.com/users/me", headers=headers)
user = resp.json().get("resource", {})
org_url = user.get("current_organization")

# Get organization membership details
org_resp = requests.get(org_url, headers=headers)
print(org_resp.json())
```

### 2. Verify Subscription Plan
```python
# Get user's organization membership to see role
resp = requests.get("https://api.calendly.com/users/me", headers=headers)
org_url = resp.json()["resource"]["current_organization"]

# Check memberships for role information
memberships = requests.get(f"{org_url}/memberships", headers=headers)
for m in memberships.json().get("collection", []):
    print(f"Role: {m.get('role')}")
    # "owner" or "admin" roles have full access
```

### 3. Upgrade Plan or Use Admin Token
```python
# If on free plan, switch to a Premium account token
if resp.status_code == 403:
    print("""
    Solutions:
    1. Upgrade Calendly account to Premium to enable webhooks
    2. Use an admin/organization token with broader permissions
    3. Use a different API feature that is available on your current plan
    """)
```

## Prevention

- Use a Calendly Premium or higher plan for integrations that need webhooks
- Create API tokens from an organization admin account for full permissions
- Check the Calendly API docs for "Availability" notes on each endpoint
- Test API calls with a free account first to understand permission boundaries
- Document which endpoints require which subscription tier for your integration

## Official Documentation

- [Calendly API Overview](https://developer.calendly.com/api-docs/)
- [Calendly API Webhooks](https://developer.calendly.com/api-docs/reference/calendly-api/openapi/webhooks)
- [Calendly Rate Limits](https://developer.calendly.com/api-docs/basics/rate-limits)

## People Also Ask

- **Do I need a paid Calendly plan for API access?** Basic API access (read users, event types) works on free plans. Webhooks and some endpoints require Premium plans.
- **Can I use webhooks on Calendly free plan?** No — webhook subscriptions require at least a Premium plan. Free accounts cannot create or manage webhooks via API.
- **What causes Calendly 403 for an admin?** Even admins get 403 for organization-level resources if the API token is not scoped to the organization. Use organization OAuth scopes.
- **How do I check my Calendly subscription level?** Go to Calendly web app > Settings > Account > Subscription or call `GET /users/me` and check the organization details.

## Related Errors

- [Calendly 401 Unauthorized](/calendly/errors/401) — Invalid or missing token
- [Calendly 404 Not Found](/calendly/errors/404) — Resource not found
- [Calendly 429 Rate Limit](/calendly/errors/429) — Too many requests
