---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Salesforce API 503: Salesforce temporarily throttling or server overload"
description: "Fix Salesforce API 503 (503 Service Unavailable) error. Salesforce temporarily throttling or server overload. Implement exponential backoff retry."
tool: "salesforce"
errorCode: "503"
errorName: "503 Service Unavailable"
httpStatus: 503
category: "server"
severity: "critical"
priority: 1
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "salesforce api 503 error"
  - "salesforce 503 fix"
  - "salesforce api salesforce temporarily throttling or"
  - "salesforce http 503"
---

## What Causes Salesforce 503

Salesforce returns HTTP 503 when the server is temporarily unable to handle the request due to maintenance, overload, or throttling. This is a server-side error that indicates the Salesforce platform is under load or undergoing maintenance — not a problem with the request itself.

The 503 response typically doesn't include a JSON body — it's a raw HTTP 503 from Salesforce's load balancers or application servers. Salesforce occasionally throttles during high-traffic periods (especially end-of-month for CRM-heavy orgs) and during planned maintenance windows. The error is almost always transient.

### Common Scenarios
- Salesforce instance is under heavy load during peak business hours
- Scheduled Salesforce maintenance window (typically Friday night to Saturday morning)
- Apex CPU time limit being hit by a governor-limited operation (can manifest as 503)
- Salesforce's load balancer temporarily routing traffic away from an instance
- Sudden burst of traffic from your integration triggering server-side throttling

## How to Detect If You're Affected

1. Check if the error is consistent or intermittent:
   ```bash
   for i in 1 2 3 4 5; do
     curl -s -w "%{http_code}\n" -o /dev/null \
       "https://yourdomain.my.salesforce.com/services/data/v60.0/limits" \
       -H "Authorization: Bearer $TOKEN"
     sleep 2
   done
   # If intermittent, it's transient — retry
   ```

2. Check Salesforce Trust for ongoing incidents:
   ```bash
   curl -s "https://api.status.salesforce.com/v1/incidents" | jq '.[] | select(.status=="open") | {title: .title, status: .status}'
   ```

3. Test against a different instance or API version:
   ```bash
   curl -s -w "\n%{http_code}" "https://yourdomain--sandbox.my.salesforce.com/services/data/v60.0/limits" \
     -H "Authorization: Bearer $TOKEN" | tail -1
   ```

## Step-by-Step Fix

### 1. Implement Exponential Backoff
```python
import time, random

def salesforce_request_with_retry(url, headers, method="GET", data=None, max_retries=5):
    for attempt in range(max_retries):
        resp = requests.request(method, url, headers=headers, json=data)
        if resp.status_code != 503:
            return resp
        wait = (2 ** attempt) + random.uniform(0, 2)
        print(f"503 — Salesforce throttling. Retrying in {wait:.1f}s (attempt {attempt + 1})")
        time.sleep(wait)
    raise Exception(f"Salesforce 503 — max retries exceeded after {max_retries} attempts")
```

### 2. Check for Maintenance Window
```python
# Check if maintenance is scheduled (Salesforce typically emails ahead)
# No API for this — check your registered Salesforce admin email

import datetime

# Log 503 occurrences with timestamps to identify patterns
def log_503(instance_url, endpoint):
    with open("sf_503.log", "a") as f:
        timestamp = datetime.datetime.utcnow().isoformat()
        f.write(f"{timestamp} | 503 | {instance_url}{endpoint}\n")
    print(f"Logged 503 at {timestamp} — check if this follows a pattern (e.g., end of month)")
```

### 3. Circuit Breaker Pattern
```python
class SalesforceCircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=300):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED = normal, OPEN = failing

    def call(self, url, headers, method="GET", data=None):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker OPEN — Salesforce 503")

        resp = requests.request(method, url, headers=headers, json=data)
        if resp.status_code == 503:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
        else:
            self.failure_count = 0
            self.state = "CLOSED"
        return resp
```

## Prevention

- Implement exponential backoff with jitter for all 503 responses
- Schedule bulk operations during off-peak hours (avoid month-end processing rushes)
- Use the Bulk API 2.0 for large operations — it handles server-side retries better than REST API
- Monitor Salesforce Trust for planned maintenance and pre-schedule downtime
- Set up a circuit breaker to stop sending requests after repeated 503s to avoid making things worse

## Official Documentation

- [Salesforce REST API](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/)
- [Salesforce Trust](https://trust.salesforce.com/)
- [Salesforce API Best Practices](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/quickstart.htm)

## People Also Ask

- **Is Salesforce 503 temporary?** Yes — 503 is almost always transient. Salesforce servers recover automatically. Retry with backoff.
- **How long does Salesforce 503 last?** Usually seconds to minutes. During maintenance windows, it can last up to several hours (typically Friday night).
- **Does Salesforce schedule 503 maintenance?** Yes — Salesforce has regular maintenance windows. Check your admin email and Salesforce Trust for schedules.
- **What's the difference between Salesforce 429 and 503?** 429 means you exceeded your API limit. 503 means Salesforce's servers are overloaded or under maintenance — it's their problem, not yours.

## Related Errors

- [Salesforce 429 REQUEST_LIMIT_EXCEEDED](/salesforce/errors/429) — Rate limit exceeded
- [Salesforce 420 Unknown](/salesforce/errors/420) — Edge routing information unavailable
- [Salesforce 401 Unauthorized](/salesforce/errors/401) — Session expired or invalid
