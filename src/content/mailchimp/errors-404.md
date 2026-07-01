---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Mailchimp API 404: Resource does not exist (e"
description: "Fix Mailchimp API 404 (404 Not Found) error. Resource does not exist (e. Verify list_id and subscriber hash (MD5 of lowercase email)."
tool: "mailchimp"
errorCode: "404"
errorName: "404 Not Found"
httpStatus: 404
category: "not-found"
severity: "medium"
priority: 2
lastUpdated: '2026-05-14'
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "mailchimp api 404 error"
  - "mailchimp 404 fix"
  - "mailchimp api resource does not exist"
  - "mailchimp http 404"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** The Mailchimp list, campaign, or subscriber you're looking for doesn't exist — or you're using the wrong ID to find it.

**The fix:**
1. Double-check your list ID — find it in Mailchimp under Audience > Settings > Audience name and defaults
2. If looking up a subscriber, make sure you lowercase the email before creating the MD5 hash
3. Check your data center suffix (like `us1`, `us2`) matches your Mailchimp account

**Copy-paste this code** (if you're using a code editor):
```python
import hashlib, requests

email = "user@example.com"
subscriber_hash = hashlib.md5(email.lower().encode()).hexdigest()
resp = requests.get(f"https://usX.api.mailchimp.com/3.0/lists/{list_id}/members/{subscriber_hash}",
    headers={"Authorization": f"apikey {API_KEY}"})
print(resp.status_code)  # 200 = found, 404 = not found
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy and send this to your AI tool:

> I'm getting a 404 Not Found error from the Mailchimp API.
> The error message is: "Resource Not Found" or "list not found"
> I'm trying to look up a subscriber in a Mailchimp list using their API.
> Please give me a step-by-step fix with working Python code that generates the correct subscriber hash and verifies the list ID.

You should get code that lowercases the email before hashing, verifies your list ID exists, and confirms you're using the right data center suffix.

If the error persists, try this follow-up:
> The fix didn't work. I'm still getting 404 errors. My list ID is [paste ID] and my data center is [paste suffix]. Please debug this.

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to avoid Mailchimp 404 errors in popular automation tools:

### Zapier
1. Open your Zap → click the Mailchimp action step
2. In the "List" dropdown, select your list from the menu — don't type the ID manually (Zapier fetches valid IDs for you)
3. If looking up a subscriber, use the "Find Subscriber" action and search by email instead of by hash

### Make (Integromat)
1. Open your scenario → click the Mailchimp module
2. In the "List ID" field, choose from the dropdown — Make pulls valid lists from your account automatically
3. Add an error handler: right-click the module → "Add error handler" → "Resume" to skip missing subscribers gracefully

### n8n
1. Open your workflow → click the Mailchimp node
2. Use the "Get All" operation first to fetch valid list IDs, then filter for the one you need
3. In the Mailchimp node settings → enable "Continue on Fail" so missing subscribers don't stop your workflow

### Power Automate
1. Open your flow → click the Mailchimp action
2. Use the "Get contacts" action with the list name selected from the dropdown — don't paste raw IDs
3. Add a "Condition" step after the action to check if the result is empty before processing

**Which tool should you use?** Zapier's dropdown selectors prevent 404 errors by only showing valid list IDs from your account.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"404 Not Found"`
- `"Resource Not Found"`
- `"list not found"`
- `"The requested resource could not be found"`

**What it means in plain English:** Mailchimp can't find what you're looking for. The list ID, subscriber, or campaign you asked about either doesn't exist, was deleted, or you typed the ID wrong.

**Most common cause:** Using the wrong list ID, or not lowercasing the email address before creating the subscriber hash that Mailchimp uses as an ID.

</div>

## What Causes Mailchimp 404

Mailchimp returns HTTP 404 when the requested resource does not exist — an invalid list ID, a subscriber hash that doesn't match any member, or a campaign ID that was never created. Mailchimp uses MD5 hashes of lowercase email addresses as subscriber IDs, so using the wrong hash format is a very common cause.

The response is `{"type":"https://mailchimp.com/developer/marketing/docs/errors/","title":"Resource Not Found","status":404,"detail":"The requested resource could not be found."}`. The subscriber hash must be `md5(strtolower(email))` — any deviation (uppercase, extra whitespace) results in a 404 for an otherwise valid subscriber.

### Common Scenarios
- Wrong list_id — using a list ID from a different Mailchimp account or misspelling it
- Subscriber hash calculated incorrectly — not lowercasing the email before MD5
- Member was deleted or archived from the list and the integration hasn't updated
- Campaign, template, or automation ID that doesn't exist or was purged
- Endpoint path incorrect — using wrong data center suffix (`us1` vs `us2`)

## How to Detect If You're Affected

1. Use verbose curl to see the full response:
   ```bash
   curl -s "https://usX.api.mailchimp.com/3.0/lists/INVALID/members" \
     -H "Authorization: apikey $API_KEY" | jq '.detail'
   ```

2. Verify your subscriber hash generation:
   ```bash
   echo -n "test@example.com" | md5sum
   # Must be lowercase email as input
   ```

## Step-by-Step Fix

### 1. Generate the Correct Subscriber Hash
```python
import hashlib

# BAD — not lowercasing
email = "Test@Example.COM"
wrong_hash = hashlib.md5(email.encode()).hexdigest()

# GOOD — lowercase before hashing
correct_hash = hashlib.md5(email.lower().encode()).hexdigest()
```

### 2. Verify List ID
```python
# Fetch all lists to confirm the ID
resp = requests.get("https://usX.api.mailchimp.com/3.0/lists", headers=headers)
lists = resp.json().get("lists", [])
list_ids = [l["id"] for l in lists]
if target_list_id not in list_ids:
    print(f"List {target_list_id} not found. Available: {list_ids}")
```

### 3. Handle Deleted Members Gracefully
```python
def get_subscriber(list_id, email):
    subscriber_hash = hashlib.md5(email.lower().encode()).hexdigest()
    resp = requests.get(
        f"https://usX.api.mailchimp.com/3.0/lists/{list_id}/members/{subscriber_hash}",
        headers=headers
    )
    if resp.status_code == 404:
        print(f"Subscriber {email} not found — may have been deleted")
        return None
    return resp.json()
```

## Prevention

- Always lowercase emails before generating subscriber hashes with `md5(email.lower().encode()).hexdigest()`
- Cache list IDs and verify them before making member-level requests
- Check the data center suffix (`us1` through `us20`) matches your Mailchimp account — find it in your account settings
- Implement a 404 handler that cleans up stale subscriber references from your local database
- Use Mailchimp's search endpoint (`GET /3.0/search-members`) to find subscribers by email instead of by hash

## Official Documentation

- [Mailchimp API Overview](https://mailchimp.com/developer/marketing/api/)
- [Mailchimp List Members](https://mailchimp.com/developer/marketing/api/list-members/)
- [Mailchimp Data Centers](https://mailchimp.com/developer/marketing/docs/data-centers/)

## People Also Ask

- **Why does Mailchimp return 404 for a valid subscriber?** The subscriber hash is probably wrong. It must be `md5(strtolower(email))` — case-sensitive and using the exact MD5 hash of the lowercase email.
- **How do I find my Mailchimp list ID?** Call `GET /3.0/lists` — each list returns an `id` field. You can also find it in the Mailchimp web UI under Audience > Settings > Audience name and defaults.
- **What data center should I use in the API URL?** Your Mailchimp data center (e.g., `us1`, `us2`, `us19`) is visible in your browser URL when logged into Mailchimp — it's the two-letter-two-digit prefix before `.api.mailchimp.com`.
- **Does Mailchimp 404 mean my API key is wrong?** No — a wrong API key would return 401 (Unauthorized). A 404 means the endpoint or resource ID is incorrect.

See all [Mailchimp API errors](/mailchimp/) in our complete reference.

Similar not-found issues occur with [HubSpot 404](/hubspot/errors/404), [Salesforce 404](/salesforce/errors/404), and [Pipedrive 404](/pipedrive/errors/404).

This error also affects integrations. See our [Salesforce to Mailchimp](/integrations/salesforce-to-mailchimp/), [Pipedrive to Mailchimp](/integrations/pipedrive-to-mailchimp/), and [Zoho to Mailchimp](/integrations/zoho-to-mailchimp/) integration error guides.

## Related Errors

- [Mailchimp 400 Bad Request](/mailchimp/errors/400) — Malformed request or validation error
- [Mailchimp 403 Forbidden](/mailchimp/errors/403) — User role lacks permission
- [Mailchimp 429 Rate Limit](/mailchimp/errors/429) — Too many requests
