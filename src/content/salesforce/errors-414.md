---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Salesforce API 414: Combined URI + headers exceed 16,384 bytes"
description: "Fix Salesforce API 414 (414 URI Too Long) error. Combined URI + headers exceed 16,384 bytes. Reduce SOQL query length, use composite/sobjects for batch operations instead of many query params."
tool: "salesforce"
errorCode: "414"
errorName: "414 URI Too Long"
httpStatus: 414
category: "payload"
severity: "low"
priority: 2
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "salesforce api 414 error"
  - "salesforce 414 fix"
  - "salesforce api combined uri + headers"
  - "salesforce http 414"
---

## What Causes Salesforce 414

Salesforce returns HTTP 414 when the combined URI path and headers exceed 16,384 bytes (16 KB). This limit applies to the entire HTTP request line and header section — not just the URL. Long SOQL queries in the query string are the most common trigger, followed by oversized headers from authentication tokens or custom headers.

The limit is a Salesforce platform restriction enforced at the edge. GET requests with long SOQL queries in the `?q=` parameter are the #1 cause. The error typically appears as a raw HTTP 414 without a JSON body because the Salesforce application layer never receives the request — it's rejected at the HTTP server level.

### Common Scenarios
- SOQL query with hundreds of IN-clause values (e.g., `WHERE Id IN ('001...', '001...', ...)`)
- Long filter strings passed via the `q` parameter in the query endpoint
- Extremely long custom headers (e.g., oversized `Authorization` token or `Sforce-*` headers)
- Bulk API jobs with overly long query strings

## How to Detect If You're Affected

1. Check the exact URL length:
   ```bash
   url="https://yourdomain.my.salesforce.com/services/data/v60.0/query?q=SELECT+Id+FROM+Contact+WHERE+Id+IN+(%27003...%27)"
   echo -n $url | wc -c
   # If > 16384 bytes, you'll get 414
   ```

2. Test with a minimal query to confirm the endpoint works:
   ```bash
   curl -s -w "\n%{http_code}" "https://yourdomain.my.salesforce.com/services/data/v60.0/query?q=SELECT+Id+FROM+Contact+LIMIT+1" \
     -H "Authorization: Bearer $TOKEN" | tail -1
   # 200 confirms the endpoint is fine — the issue is URL size
   ```

3. Strip headers to check if they contribute:
   ```bash
   # Count header sizes too
   curl -s -o /dev/null -w "Total: %{size_request}\n" \
     "https://yourdomain.my.salesforce.com/services/data/v60.0/query?q=..." \
     -H "Authorization: Bearer $TOKEN"
   ```

## Step-by-Step Fix

### 1. Use POST for Long SOQL Queries
```python
# BAD — long query in GET URL (triggers 414)
query = "SELECT Id, Name, Email, ... FROM Contact WHERE Id IN ('001...', '001...', ...)"
url = f"{instance_url}/services/data/v60.0/query?q={query}"
resp = requests.get(url, headers=headers)
# 414 if URL exceeds 16KB

# GOOD — use POST query endpoint (no URL size limit)
url = f"{instance_url}/services/data/v60.0/query"
resp = requests.post(url, headers=headers, data={"q": query})
# POST body has a much higher limit
```

### 2. Use Composite API for Batch Operations
```python
# BAD — separate requests for each record (hits URL limit with long IDs)
for record_id in many_ids:
    requests.get(f"{instance_url}/services/data/v60.0/sobjects/Contact/{record_id}", headers=headers)

# GOOD — batch in a single composite request
composite_url = f"{instance_url}/services/data/v60.0/composite"
subrequests = []
for i, record_id in enumerate(many_ids[:25]):  # Max 25 per composite
    subrequests.append({
        "method": "GET",
        "url": f"/services/data/v60.0/sobjects/Contact/{record_id}",
        "referenceId": f"ref{i}",
    })
resp = requests.post(composite_url, headers=headers, json={"compositeRequest": subrequests})
```

### 3. Chunk IN-Clause Values
```python
# BAD — thousands of IDs in a single query
ids = ["001..."] * 10000
query = f"SELECT Id FROM Contact WHERE Id IN ({','.join(ids)})"  # Way too long

# GOOD — chunk into batches of 200-500 IDs
def chunk_list(lst, size):
    return [lst[i:i+size] for i in range(0, len(lst), size)]

for chunk in chunk_list(ids, 200):
    formatted = ",".join(f"'{i}'" for i in chunk)
    query = f"SELECT Id FROM Contact WHERE Id IN ({formatted})"
    resp = requests.post(f"{instance_url}/services/data/v60.0/query", headers=headers, data={"q": query})
```

## Prevention

- Use POST to the query endpoint instead of GET for long SOQL queries
- Chunk IN-clause values into groups of 200 or fewer
- Use the Composite API to batch multiple requests into one HTTP call
- Monitor request URL size and add validation to stay under 16 KB
- Prefer parameterized queries over string concatenation for dynamic filters

## Official Documentation

- [Salesforce REST API](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/)
- [Salesforce SOQL](https://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta/soql_sosl/)
- [Salesforce Composite API](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/using_composite_resources.htm)

## People Also Ask

- **What is the Salesforce URL length limit?** 16,384 bytes (16 KB) combined for URI path and all headers.
- **How do I run long SOQL queries without hitting 414?** Use `POST /services/data/v60.0/query` with the query in the request body instead of `GET` with the query in the URL.
- **Can I get 414 from composite requests?** Composite requests use POST with the payload in the body, so they typically don't hit the URL limit. The body limit is much higher (10 MB).
- **Does the 414 limit include headers?** Yes — the limit applies to the entire request line plus all headers. Large `Authorization` tokens can contribute significantly.

## Related Errors

- [Salesforce 400 Bad Request](/salesforce/errors/400) — Invalid payload or field values
- [Salesforce 429 REQUEST_LIMIT_EXCEEDED](/salesforce/errors/429) — Rate limit exceeded
- [Salesforce 503 Service Unavailable](/salesforce/errors/503) — Server overload
