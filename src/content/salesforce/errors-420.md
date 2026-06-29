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
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "salesforce api 420 error"
  - "salesforce 420 fix"
  - "salesforce api salesforce edge routing information"
  - "salesforce http 420"
---

## What Causes Salesforce 420

Salesforce returns HTTP 420 when the Salesforce Edge network cannot route the request to the correct instance. This is an infrastructure-level error that indicates a problem with Salesforce's global load balancing and routing layer — not an issue with the request itself.

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
