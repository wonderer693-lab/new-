---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Zoho API Access Denied (OAuth throttle): Made too many OAuth token requests continuously"
description: "Fix Zoho API Access Denied (OAuth throttle) error. Made too many OAuth token requests continuously. Wait before generating more tokens."
tool: "zoho"
errorCode: "access-denied-oauth-throttle"
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

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Zoho blocked your request because you made too many OAuth token requests in a short time.

**The fix:**
1. Stop all token requests and wait 10-15 minutes
2. Make sure you're not refreshing tokens more than once per hour
3. Use one shared token instead of creating a new one for every request

**Copy-paste this code** (if you're using a code editor):
```python
import time, requests

resp = requests.post(token_url, data=token_params)
if "OAuth throttle" in resp.text:
    time.sleep(900)
    resp = requests.post(token_url, data=token_params)
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm getting an "Access Denied (OAuth throttle)" error from the Zoho API.
> The error message is: "Made too many OAuth token requests continuously"
> I'm using a Zoho CRM integration that refreshes OAuth tokens.
> Please give me a step-by-step fix with working Python code that caches tokens and adds delays between refresh calls.

**What to expect:** The AI should give you a token manager that caches access tokens and spaces out refresh calls to stay under Zoho's 10-per-10-minute limit.

**If it doesn't work**, add this follow-up:
> The fix didn't work. I'm still getting OAuth throttle errors. Here's what I tried: [paste your code]. Please debug this.

**Best AI tools for this:** Claude (best at explaining OAuth flows), ChatGPT-4 (good code generation), Cursor (if you want inline code fixes)

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to handle Zoho OAuth throttle errors in popular automation tools:

### Zapier
1. Open your Zap → click the Zoho CRM action step
2. Enable "Auto-retry on error" in the step settings — Zapier will retry failed auth calls automatically
3. Add a "Delay by Zapier" step (5 minutes) before the Zoho action to space out token requests

### Make (Integromat)
1. Open your scenario → right-click the Zoho CRM module → "Add error handler"
2. Choose "Retry" → set interval to 300 seconds (5 minutes), max retries to 3
3. Add a "Sleep" module (5 minutes) between Zoho calls to avoid rapid token refreshes

### n8n
1. Open your workflow → click the Zoho CRM node
2. In "Settings" → enable "Retry on Fail" → set "Wait Between Tries" to 300000ms (5 minutes), "Max Tries" to 3
3. Add a "Wait" node (5 minutes) before the Zoho node if you're running multiple calls

### Power Automate
1. Open your flow → click the Zoho action
2. In "Settings" → enable "Retry Policy" → set to "Fixed interval" with count 3 and interval 5 minutes
3. Add a "Delay" action (5 minutes) before the Zoho action to prevent rapid token requests

**Which tool should you use?** Zapier has the best built-in retry for Zoho — it handles auth errors automatically without extra configuration.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"ACCESS_DENIED"` with mention of OAuth throttle
- `"OAuth throttle"` in the error response
- `"Too many requests"` from the Zoho token endpoint
- `{"error":"Access Denied (OAuth throttle)"}` in your logs

**What it means in plain English:** Zoho is telling you to slow down on token requests. You're asking for new OAuth tokens too often. Wait a few minutes and try again.

**Most common cause:** Apps that create a new token for every API call instead of reusing the same token, or multiple servers all refreshing tokens at the same time.

</div>

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
