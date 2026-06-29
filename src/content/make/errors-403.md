---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Make API 403: Forbidden"
description: "Fix Make API 403 error. Forbidden — insufficient permissions. Check that token has the required scopes for the endpoint."
tool: "make"
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
  - "make api 403 error"
  - "make 403 fix"
  - "make api forbidden — insufficient permissions"
  - "make http 403"
---

## What Causes Make 403

Make returns HTTP 403 when the authenticated token has insufficient permissions for the requested operation. Make's API uses token-based authentication with scoped permissions — not all tokens can access all endpoints. A token created for read-only access will 403 on write operations, and a token for one organization will 403 when used against another.

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
