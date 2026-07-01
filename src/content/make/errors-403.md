---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Make API 403 Error: Forbidden Request — Fix & Prevention Guide"
description: "Fix Make API 403 error. Forbidden — insufficient permissions. Check that token has the required scopes for the endpoint."
tool: "make"
errorCode: "403"
errorName: "403"
httpStatus: 403
category: "permission"
severity: "high"
priority: 1
lastUpdated: '2026-05-04'
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "make api 403 error"
  - "make 403 fix"
  - "make api forbidden — insufficient permissions"
  - "make http 403"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Your Make account doesn't have permission for this action — your token lacks the right access level.

**The fix:**
1. Check your Make plan — free plans can't access premium features
2. Go to Make admin → API Tokens → verify your token has write permissions (not just read)
3. If using multiple organizations, make sure you're using the right token for the right org

**Copy-paste this code** (if you're using a code editor):
```python
import requests

headers = {"Authorization": f"Token {token}"}
resp = requests.get("https://api.make.com/api/v2/organizations", headers=headers)
if resp.status_code == 403:
    print("Token lacks permission — regenerate with proper scopes")
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Start by asking your AI coding tool:

> I'm getting a 403 Forbidden error from Make (Integromat).
> The error message is: "Forbidden — insufficient permissions"
> I'm trying to perform an action in Make but my account doesn't have permission.
> Please give me a step-by-step fix to check my plan and token permissions.

The response should help you identify whether it's a plan limitation or a token scope issue, and guide you through fixing it.

If that doesn't resolve it, send a second prompt:
> The fix didn't work. I'm still getting 403 errors. Here's my Make plan and what I'm trying to do: [paste details]. Please debug this.

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to fix Make 403 errors in popular automation tools:

### Make (Integromat)
1. Open Make → click your profile → "Plan & Billing" → check your current plan tier
2. Go to "API Tokens" → verify your token has the right scopes (read + write, not just read)
3. If using multiple organizations, confirm you're using the correct token for each org

### Zapier
1. Open your Zap → click the Make connection → check if your Make plan allows this action
2. If on a free plan, upgrade to access premium features that trigger 403 errors
3. Reconnect your Make account to refresh permissions after any plan changes

### n8n
1. Open your workflow → check the Make credentials node → verify token scopes
2. If the token is read-only, regenerate it with write permissions in Make admin
3. Test the node after updating credentials to confirm the 403 is resolved

### Power Automate
1. Open your flow → click the Make connection → check your Make plan allows this action
2. If needed, upgrade your Make plan or switch to a token with proper permissions
3. Re-authenticate the connection after making changes to verify access

**Which tool should you use?** Make's own admin panel is best — check your plan and token scopes directly there.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"403 Forbidden"`
- `"access denied"`
- `"Forbidden — insufficient permissions"`
- `"Token lacks required scope"` in your Make logs

**What it means in plain English:** Make recognizes who you are, but your account or token doesn't have permission to do what you're trying to do. Check your plan and token settings.

**Most common cause:** Using a read-only token to perform write operations, or trying to access premium features on a free plan.

</div>

## What Causes Make 403

Make returns HTTP 403 when the authenticated token has insufficient permissions for the requested operation. Make's API uses token-based authentication with scoped permissions — not all tokens can access all endpoints. A token created for read-only access will 403 on write operations, and a token for one organization will 403 when used against another. See all [Make API errors](/make/) in our complete reference.

Similar permission issues occur with [Salesforce 403](/salesforce/errors/403), [HubSpot 403](/hubspot/errors/403), and [Slack not_in_channel](/slack/errors/not_in_channel).

The response is `{"error":"Forbidden"}`. Unlike 401 (invalid credentials), a 403 means your token is valid but lacks sufficient authorization for that specific endpoint or resource.

### Common Scenarios
- Using a read-only API token to attempt a POST, PUT, or DELETE operation
- Token was created for Organization A but used to access Organization B's resources
- Token lacks specific scope for the endpoint (e.g., trying to manage users with a scenarios-only token)
- API key has been restricted in the Make admin console
- Free-plan accounts attempting premium features

## How to Detect If You're Affected

1. Check the response status against a known-good endpoint:
   ```bash
   curl -s -w "\n%{http_code}" "https://api.make.com/api/v2/organizations" \
     -H "Authorization: Token $TOKEN" | tail -1
   ```

2. Test write permissions by trying a simple POST:
   ```bash
   curl -s -X POST "https://api.make.com/api/v2/scenarios" \
     -H "Authorization: Token $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name":"test"}' | jq .
   ```

## Step-by-Step Fix

### 1. Check Token Permissions
```python
# Try a simple GET to verify basic access
resp = requests.get("https://api.make.com/api/v2/organizations", headers=headers)
if resp.status_code == 403:
    print("Token lacks organization read access — regenerate with proper scopes")
```

### 2. Regenerate Token with Proper Scopes
In the Make admin dashboard, go to Organization settings > API tokens and generate a new token with the required scopes for your use case (read + write for scenarios, connections, etc.).

### 3. Use Organization-Specific Token
```python
# Each Make organization needs its own token
org_tokens = {
    "org_prod": "token_abc123",
    "org_dev": "token_def456",
}

def call_make(org, endpoint):
    token = org_tokens[org]
    headers = {"Authorization": f"Token {token}"}
    return requests.get(f"https://api.make.com/api/v2/organizations/{org}/{endpoint}", headers=headers)
```

## Prevention

- Create separate API tokens for each organization with minimal required scopes (principle of least privilege)
- Document which scopes each token needs and regenerate immediately when requirements change
- Add a permission check on startup — test a representative endpoint and fail fast if 403
- Use dedicated service accounts rather than personal user tokens for automated integrations
- Audit token permissions quarterly — remove unused scopes and rotate tokens

This error also affects integrations. See our [Make to Slack integration errors](/integrations/make-to-slack/) for common cross-tool issues.

## Official Documentation

- [Make API Documentation](https://www.make.com/en/api-documentation)
- [Make API Authentication](https://www.make.com/en/api-documentation#authentication)
- [Make Organizations](https://www.make.com/en/api-documentation#organizations)

## People Also Ask

- **What's the difference between Make 401 and 403?** 401 means invalid or missing token. 403 means the token is valid but doesn't have permission for that resource or action.
- **Does each Make organization need its own API token?** Yes — API tokens are scoped to a single organization. A token from Organization A cannot access Organization B's resources.
- **Can I create a read-only Make API token?** Yes — when generating an API token in Make admin, you can select specific scopes. Limit to `scenarios:read` for read-only access.
- **Why does my Make token work for GET but fail with 403 on POST?** Your token likely has read-only scopes. Generate a new token with write scopes (e.g., `scenarios:write`) for mutation operations.

## Related Errors

- [Make 401 Unauthorized](/make/errors/401) — Invalid or missing token
- [Make 404 Not Found](/make/errors/404) — Resource not found
- [Make 500 Server Error](/make/errors/500) — Server error
