---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Pipedrive API 403: Request not allowed"
description: "Fix Pipedrive API 403 (403 Forbidden) error. Request not allowed — user reached entity limit or Cloudflare block after rate limit abuse. For rate limit blocks: wait penalty period, fix misconfiguration causing excessive requests."
tool: "pipedrive"
errorCode: "403"
errorName: "403 Forbidden"
httpStatus: 403
category: "permission"
severity: "high"
priority: 1
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "pipedrive api 403 error"
  - "pipedrive 403 fix"
  - "pipedrive api request not allowed —"
  - "pipedrive http 403"
---

## What Causes Pipedrive 403

Pipedrive returns HTTP 403 for two distinct scenarios: (1) the user has reached a per-entity limit (e.g., maximum number of deals, persons, or custom fields) and the request is blocked, or (2) Cloudflare has temporarily blocked the request due to rate limit abuse. Both result in `{"error":"Request not allowed"}`.

The entity limit scenario is a soft limit — upgrading your plan or archiving unused records resolves it. The Cloudflare block is a hard penalty triggered by sustained rate limit abuse (typically 20-30 minutes). It resets automatically after a cooling-off period.

### Common Scenarios
- Creating a deal when the account has reached its maximum deal count (entity limit)
- Creating custom fields beyond the plan's limit
- Sending excessive requests in a short period, triggering Cloudflare's abuse detection
- API token used from a blocked IP address due to previous abuse
- Account reached its maximum number of users, pipelines, or products

## How to Detect If You're Affected

1. Check the response body for details:
   ```bash
   curl -s -w "\n%{http_code}" -X POST "https://api.pipedrive.com/v1/deals?api_token=$TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"title":"Test"}' | tail -1
   ```

2. Check if it's a Cloudflare block — look for Cloudflare headers or HTML in the response:
   ```bash
   curl -s -v "https://api.pipedrive.com/v1/deals?api_token=$TOKEN" 2>&1 | findstr -i "cloudflare"
   ```

## Step-by-Step Fix

### 1. Identify the Block Type
```python
resp = requests.get(f"https://api.pipedrive.com/v1/deals?api_token={TOKEN}")
if resp.status_code == 403:
    # Check if it's Cloudflare
    if "cloudflare" in resp.text.lower():
        print("Cloudflare block — wait 20-30 minutes")
    else:
        print("Entity limit reached — check plan limits")
```

### 2. For Entity Limits: Archive or Upgrade
```python
# Check account limits via API
resp = requests.get(f"https://api.pipedrive.com/v1/deals?api_token={TOKEN}&limit=1")
total = resp.json().get("additional_data", {}).get("pagination", {}).get("total_count")
print(f"Total deals: {total}")

# Archive old deals to free up space
old_deals = get_deals_older_than(days=365)
for deal in old_deals:
    requests.put(f"https://api.pipedrive.com/v1/deals/{deal['id']}?api_token={TOKEN}",
        json={"status": "deleted"})
```

### 3. For Cloudflare Blocks: Wait and Fix Root Cause
```python
# Wait 30 minutes for the block to lift
print("Cloudflare block detected — waiting 30 minutes...")
time.sleep(1800)  # 30 minutes

# Then fix the root cause (reduce request rate)
# Add delays between requests
time.sleep(1)  # At least 1 second between calls
```

## Prevention

- Monitor entity counts and archive records before reaching limits
- Stay well within rate limits to avoid Cloudflare blocks — a 10-second minimum between bulk operations
- Implement exponential backoff before Cloudflare's threshold is reached
- Track your plan's entity limits and alert when approaching them
- Use Pipedrive's webhooks for event-driven updates instead of polling

## Official Documentation

- [Pipedrive API Documentation](https://developers.pipedrive.com/docs/api/v1)
- [Pipedrive Plans and Pricing](https://www.pipedrive.com/pricing)
- [Pipedrive API Errors](https://developers.pipedrive.com/docs/api/v1/errors)

## People Also Ask

- **Why does Pipedrive return 403?** Either you've hit an entity limit (deals, persons, custom fields) or Cloudflare has blocked your IP for rate limit abuse.
- **How long does a Pipedrive Cloudflare ban last?** Typically 20-30 minutes. The ban is automatic and lifts itself after the cooling-off period without rate limit violations.
- **How do I check my Pipedrive entity limits?** Pipedrive does not expose entity limits via API. Check your plan details in the Pipedrive web UI under Company Settings.
- **What's the difference between Pipedrive 403 and 429?** 429 is a standard rate limit with Retry-After header. 403 (Cloudflare) is an abuse detection block without Retry-After.

## Related Errors

- [Pipedrive 429 Rate Limit](/pipedrive/errors/429) — Rate limit exceeded
- [Pipedrive 402 Payment Required](/pipedrive/errors/402) — Company account not open
- [Pipedrive 415 Feature Not Enabled](/pipedrive/errors/415) — Feature not enabled for account
