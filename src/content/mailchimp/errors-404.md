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
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "mailchimp api 404 error"
  - "mailchimp 404 fix"
  - "mailchimp api resource does not exist"
  - "mailchimp http 404"
---

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

## Related Errors

- [Mailchimp 400 Bad Request](/mailchimp/errors/400) — Malformed request or validation error
- [Mailchimp 403 Forbidden](/mailchimp/errors/403) — User role lacks permission
- [Mailchimp 429 Rate Limit](/mailchimp/errors/429) — Too many requests
