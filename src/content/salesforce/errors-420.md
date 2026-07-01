---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Salesforce API 420: Salesforce Edge routing information unavailable"
description: "Fix Salesforce API 420 (420 Unknown) error. Salesforce Edge routing information unavailable. Contact Salesforce Customer Support."
tool: "salesforce"
errorCode: "420"
errorName: "420 Unknown"
httpStatus: 420
category: "infrastructure"
severity: "medium"
priority: 2
lastUpdated: '2026-05-12'
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "salesforce api 420 error"
  - "salesforce 420 fix"
  - "salesforce api salesforce edge routing information"
  - "salesforce http 420"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Salesforce is throttling your API calls — the Edge network can't route your request right now.

**The fix:**
1. Wait 30-60 seconds and try again — this is usually a temporary routing issue
2. Check Salesforce Trust (trust.salesforce.com) for ongoing incidents or maintenance
3. Add delays between your API calls to avoid triggering the throttle

**Copy-paste this code** (if you're using a code editor):
```python
import time, requests

resp = requests.get(url, headers=headers)
if resp.status_code == 420:
    print("Salesforce Edge routing issue — waiting 30 seconds")
    time.sleep(30)
    resp = requests.get(url, headers=headers)
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Paste this into any AI tool:

> I'm getting a 420 "Enhance Your Calm" error from the Salesforce API.
> The error message mentions concurrent API request limits or Edge routing issues.
> My integration makes frequent API calls to Salesforce.
> Please give me a step-by-step fix with working Python code that adds delays and retries for 420 errors.

Expect back the AI should give you a retry function with exponential backoff and explain how to space out API calls to avoid Salesforce throttling.

Still hitting the error? Send:
> The fix didn't work. I'm still getting 420 errors even with delays. Here's my retry code: [paste your code]. Please debug this.

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to handle Salesforce throttling in popular automation tools:

### Zapier
1. Open your Zap → add a "Delay by Zapier" step before each Salesforce action
2. Set the delay to 5-10 seconds between Salesforce calls
3. Enable "Auto-retry on error" in each Salesforce step's settings

### Make (Integromat)
1. Open your scenario → add a "Sleep" module (5-10 seconds) between Salesforce modules
2. Right-click each Salesforce module → "Add error handler" → choose "Retry" with 10-second interval
3. In scenario settings, reduce the number of operations per execution to spread calls over time

### n8n
1. Open your workflow → add a "Wait" node (5000-10000ms) between Salesforce nodes
2. In each Salesforce node's "Settings" → enable "Retry on Fail" → set "Wait Between Tries" to 10000ms
3. For bulk operations, use the "SplitInBatches" node with a pause between batches

### Power Automate
1. Open your flow → add a "Delay" action (5-10 seconds) before each Salesforce action
2. In each Salesforce action's "Settings" → enable "Retry Policy" → set to "Exponential interval"
3. For loops, add a "Delay" action inside the loop to space out calls

**Which tool should you use?** Make has the best built-in retry for Salesforce — you can set custom retry intervals per module without extra steps.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"420 Enhance Your Calm"`
- `"Concurrent API request limit"`
- `"420 Unknown"`
- `"Edge routing information unavailable"` in your integration logs

**What it means in plain English:** Salesforce is telling you to slow down. You're sending too many requests at once, or their network is having a temporary routing issue.

**Most common cause:** Too many API calls firing at the same time without any pauses between them, or a temporary Salesforce Edge network issue.

</div>

## What Causes Salesforce 420

Salesforce returns HTTP 420 when the Salesforce Edge network cannot route the request to the correct instance. See all [Salesforce API errors](/salesforce/) in our complete reference. This is an infrastructure-level error that indicates a problem with Salesforce's global load balancing and routing layer — not an issue with the request itself.

The 420 status code is unique to Salesforce. It means the request reached Salesforce's edge network, but the routing information needed to forward it to the correct pod (e.g., `na1`, `eu2`) is unavailable. This can happen during network maintenance, DNS propagation delays after org migration, or regional routing disruptions.

### Common Scenarios
- Salesforce Edge network is undergoing maintenance in your region
- Org was recently migrated to a different pod (e.g., `na1` to `na40`) and DNS hasn't fully propagated
- Regional network disruption between your integration server and Salesforce Edge
- Salesforce is experiencing a partial outage affecting the routing layer

## How to Detect If You're Affected

1. Check the HTTP status code — 420 is specific to Salesforce:
   ```bash
   curl -s -w "\n%{http_code}" "https://yourdomain.my.salesforce.com/services/data/v60.0/sobjects/Contact" \
     -H "Authorization: Bearer $TOKEN" | tail -1
   # 420 indicates Edge routing issue
   ```

2. Confirm by testing against a different endpoint:
   ```bash
   curl -s -w "\n%{http_code}" "https://yourdomain.my.salesforce.com/services/data/v60.0/limits" \
     -H "Authorization: Bearer $TOKEN" | tail -1
   ```

3. Check Salesforce Trust status:
   ```bash
   curl -s "https://api.status.salesforce.com/v1/incidents" | jq '.[] | select(.status=="open")'
   ```

## Step-by-Step Fix

### 1. Implement Retry with Backoff
```python
import time, random

def salesforce_request(url, headers, max_retries=5):
    for attempt in range(max_retries):
        resp = requests.get(url, headers=headers)
        if resp.status_code != 420:
            return resp
        wait = (2 ** attempt) + random.uniform(0, 2)
        print(f"420 Edge routing error — retrying in {wait:.1f}s (attempt {attempt + 1})")
        time.sleep(wait)
    return resp  # Return last response, even if 420
```

### 2. Route to Alternative Instance
```python
# If using My Domain, the URL already routes through Edge
# Try alternative instance URL if you know your pod
alternative_urls = [
    "https://na1.salesforce.com",
    "https://na2.salesforce.com",
    "https://eu1.salesforce.com",
]

for alt_url in alternative_urls:
    try:
        test_url = f"{alt_url}/services/data/v60.0/limits"
        resp = requests.get(test_url, headers=headers, timeout=10)
        if resp.status_code == 200:
            print(f"Working instance: {alt_url}")
            break
    except requests.RequestException:
        continue
```

### 3. Check Salesforce Trust and Support
```python
import json

# Check Salesforce status page
trust_resp = requests.get("https://api.status.salesforce.com/v1/incidents")
if trust_resp.status_code == 200:
    incidents = trust_resp.json()
    active = [i for i in incidents if i.get("status") == "open"]
    if active:
        print(f"Active Salesforce incidents: {len(active)}")
        for inc in active:
            print(f"  {inc.get('title')} — {inc.get('status')}")
    else:
        print("No active incidents reported")
else:
    print("Cannot check Salesforce status — contact Salesforce support")
```

## Prevention

- Use My Domain URLs (e.g., `https://yourdomain.my.salesforce.com`) for automatic routing
- Implement retry logic with backoff for transient Edge routing errors
- Monitor Salesforce Trust status for planned maintenance windows
- Use a CDN or proxy layer that can failover between Salesforce instances
- Contact Salesforce support to report persistent 420 errors — they may indicate a pod routing issue
- Similar throttling issues occur with [HubSpot 429](/hubspot/errors/429) and [Zoho too-many-requests](/zoho/errors/too-many-requests).
- This error also affects integrations. See our [Salesforce to Mailchimp](/integrations/salesforce-to-mailchimp/) and [Salesforce to ActiveCampaign](/integrations/salesforce-to-activecampaign/) integration error guides.

## Official Documentation

- [Salesforce REST API](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/)
- [Salesforce Trust](https://trust.salesforce.com/)
- [Salesforce My Domain](https://help.salesforce.com/s/articleView?id=sf.domain_name_overview.htm)

## People Also Ask

- **What is Salesforce HTTP 420?** A Salesforce-specific error code indicating Edge routing information is unavailable — the request reached Salesforce's network but couldn't be forwarded to the correct instance.
- **Is 420 a temporary error?** Yes — 420 is typically transient and related to network routing. Retry with backoff usually resolves it.
- **How do I fix Salesforce 420?** Implement retry logic with exponential backoff. If persistent, check Salesforce Trust status and contact support.
- **Does 420 mean my Salesforce instance is down?** Not necessarily — the instance may be running fine, but the Edge routing layer that directs traffic to it is having issues.

## Related Errors

- [Salesforce 503 Service Unavailable](/salesforce/errors/503) — Server overload or throttling
- [Salesforce 429 REQUEST_LIMIT_EXCEEDED](/salesforce/errors/429) — Rate limit exceeded
- [Salesforce 401 Unauthorized](/salesforce/errors/401) — Session expired or invalid
