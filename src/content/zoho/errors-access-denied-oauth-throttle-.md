---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Zoho API Access Denied (OAuth throttle): Made too many OAuth token requests continuously"
description: "Fix Zoho API Access Denied (OAuth throttle) error. Made too many OAuth token requests continuously. Wait before generating more tokens."
tool: "zoho"
errorCode: "Access Denied (OAuth throttle)"
errorName: "Access Denied (OAuth throttle)"
httpStatus: 0
category: "unknown"
severity: "medium"
priority: 2
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "zoho api Access Denied (OAuth throttle) error"
  - "zoho Access Denied (OAuth throttle) fix"
  - "zoho api made too many oauth"
---

## What Causes Zoho Access Denied (OAuth throttle)

Zoho throttles OAuth token endpoint requests to prevent abuse. There are two separate throttles: a maximum of 10 grant token requests per 10 minutes per client ID (from the authorization code grant flow), and a maximum of 10 access token requests per 10 minutes per refresh token (from the refresh flow). Exceeding either triggers an "Access Denied (OAuth throttle)" response from the `accounts.zoho.com` token endpoint.

This is not a CRM API error — it occurs at the OAuth layer when your app programmatically requests tokens too aggressively. The response is `{"error":"Access Denied (OAuth throttle)"}` with HTTP status 429. This typically happens when your integration enters a tight loop of failed refreshes, or when multiple instances all try to get initial tokens simultaneously.

### Common Scenarios
- Multiple server instances all boot up and request OAuth tokens at the same time
- A buggy retry loop that keeps calling the token endpoint without backoff
- Deploying a new integration that goes through the OAuth authorization flow many times in quick succession
- Testing OAuth flows manually by clicking "Authorize" repeatedly

## How to Detect If You're Affected

1. Check the OAuth token endpoint response:
   ```bash
   curl -s -X POST "https://accounts.zoho.com/oauth/v2/token" \
     -d "code=$AUTH_CODE" \
     -d "client_id=$CLIENT_ID" \
     -d "client_secret=$CLIENT_SECRET" \
     -d "redirect_uri=$REDIRECT_URI" \
     -d "grant_type=authorization_code" | jq .
   ```
   If it returns `{"error":"Access Denied (OAuth throttle)"}`, you're being throttled.

2. Count your recent token requests — Zoho allows 10 per 10 minutes. Check logs for outgoing POST requests to `accounts.zoho.com/oauth/v2/token`.

## Step-by-Step Fix

### 1. Stop All Token Requests and Wait
The throttle self-resets. Stop making token requests for 10-15 minutes:
```python
import time
print("OAuth throttle detected — waiting 15 minutes...")
time.sleep(900)  # 15 minutes
# Then retry the token request
```

### 2. Implement a Token Cache with Rate Limiting
```python
import time
from collections import deque

class ZohoTokenManager:
    def __init__(self):
        self.tokens = deque()
        self.last_refresh = 0

    def request_token(self):
        now = time.time()
        # Rate limit: max 1 token request per 60 seconds
        if now - self.last_refresh < 60:
            wait = 60 - (now - self.last_refresh)
            print(f"Rate limited — waiting {wait:.0f}s")
            time.sleep(wait)

        resp = requests.post("https://accounts.zoho.com/oauth/v2/token", data={
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
        })
        self.last_refresh = time.time()
        self.tokens.append(resp.json()["access_token"])
        return self.tokens[-1]
```

### 3. Single-Instance Token Management
Avoid concurrent token refreshes from multiple processes — centralize through a shared cache:
```python
# BAD — every instance refreshes independently
# GOOD — use a distributed lock (Redis) or single daemon
import redis
r = redis.Redis()
if not r.exists("zoho_token"):
    token = refresh_zoho_token()
    r.setex("zoho_token", 3300, token)
access_token = r.get("zoho_token")
```

## Prevention

- Cache access tokens for their full 55-minute useful lifetime — don't refresh preemptively more than once per token
- Implement a distributed lock (Redis, database row lock) so concurrent processes share one refresh, not each trigger a refresh
- Monitor for "Access Denied (OAuth throttle)" in token endpoint responses and trigger an immediate 15-minute backoff
- Never implement retry-on-error loops that call the token endpoint without exponential backoff
- Use a single dedicated service to manage token lifecycle — other services request tokens from it over internal API

## Official Documentation

- [Zoho OAuth Overview](https://www.zoho.com/crm/developer/docs/api/v3/oauth-overview.html)
- [Zoho OAuth Token Refresh](https://www.zoho.com/crm/developer/docs/api/v3/refresh-token.html)
- [Zoho CRM API Authentication](https://www.zoho.com/crm/developer/docs/api/v3/authentication.html)

## People Also Ask

- **What triggers Zoho's OAuth throttle?** Making more than 10 grant token requests per 10 minutes per client ID, or more than 10 access token requests per 10 minutes per refresh token.
- **How long does the OAuth throttle last?** The throttle window is 10 minutes from the first excess request. You must wait the full 10 minutes without making new token requests for the count to reset.
- **Does the OAuth throttle affect CRM API calls?** No — it only affects the OAuth token endpoint (`accounts.zoho.com/oauth/v2/token`). Your existing access token continues to work for CRM API calls during the throttle period.
- **How do I prevent OAuth throttling?** Cache access tokens and reuse them for their full lifetime. Don't generate a new token on every request. Use a single token manager instance shared across your entire application.

## Related Errors

- [Zoho INVALID_OAUTHTOKEN](/zoho/errors/INVALID_OAUTHTOKEN) — Access token expired or invalid
- [Zoho TOO_MANY_REQUESTS](/zoho/errors/TOO_MANY_REQUESTS) — Daily credit limit exceeded
- [Zoho LIMIT_EXCEEDED](/zoho/errors/LIMIT_EXCEEDED) — General API limit reached
