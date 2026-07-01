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

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Your SOQL query or API URL is too long — Salesforce has a 16 KB limit on the total URL + headers.

**The fix:**
1. Switch from GET to POST — put your query in the request body instead of the URL
2. If you have hundreds of IDs in an IN clause, split them into smaller batches (200 per query)
3. Use the Composite API to batch multiple requests into one call

**Copy-paste this code** (if you're using a code editor):
```python
import requests

query = "SELECT Id, Name FROM Contact WHERE Id IN ('001...', '001...')"
resp = requests.post(f"{instance_url}/services/data/v60.0/query",
    headers=headers, data={"q": query})
print(resp.json()["records"])
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm getting a 414 URI Too Long error from the Salesforce API.
> The error message is: "Request-URI Too Large"
> I'm running a SOQL query with hundreds of IDs in a WHERE IN clause using GET.
> Please give me a step-by-step fix with working Python code that uses POST instead and chunks large queries.

**What to expect:** The AI should give you code that switches to POST for the query endpoint and splits large IN clauses into batches of 200 IDs.

**If it doesn't work**, add this follow-up:
> The fix didn't work. I switched to POST but I'm still getting errors with very large queries. Here's my query: [paste query]. Please debug this.

**Best AI tools for this:** Claude (best at explaining SOQL optimization), ChatGPT-4 (good code generation), Cursor (if you want inline code fixes)

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to handle Salesforce URL-too-long errors in popular automation tools:

### Zapier
1. Open your Zap → click the Salesforce "Find Record" step
2. Instead of filtering by a long list of IDs, filter by a simpler field (e.g., date range, status)
3. If you need many IDs, split into multiple Zap steps each searching a smaller batch

### Make (Integromat)
1. Open your scenario → click the Salesforce "Search Records" module
2. Reduce the SOQL query complexity — use fewer fields in SELECT or fewer IDs in WHERE IN
3. Add an "Iterator" module before Salesforce to process IDs in batches of 200

### n8n
1. Open your workflow → click the Salesforce node
2. Switch the operation from "Get" (uses URL) to "Search" (uses body) for long queries
3. Add a "SplitInBatches" node before Salesforce to chunk large ID lists into groups of 200

### Power Automate
1. Open your flow → click the Salesforce "List records" action
2. Simplify the filter query — use date ranges or status fields instead of long ID lists
3. Add an "Apply to each" loop with a batch of 200 IDs per iteration

**Which tool should you use?** n8n handles this best — its "Search" operation uses POST by default, so you rarely hit URL length limits.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"414 URI Too Long"`
- `"Request-URI Too Large"`
- `"URI Too Long"`
- A raw HTTP 414 with no JSON body in your integration logs

**What it means in plain English:** The web address (URL) you're sending to Salesforce is too long. It's like writing a letter on the outside of an envelope — there's only so much space.

**Most common cause:** A SOQL query with hundreds or thousands of IDs in a WHERE IN clause, sent as a GET request where the query goes in the URL.

</div>

## What Causes Salesforce 414

Salesforce returns HTTP 414 when the combined URI path and headers exceed 16,384 bytes (16 KB). See all [Salesforce API errors](/salesforce/) in our complete reference. This limit applies to the entire HTTP request line and header section — not just the URL. Long SOQL queries in the query string are the most common trigger, followed by oversized headers from authentication tokens or custom headers.

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
- Similar URI length issues occur with [HubSpot 414](/hubspot/errors/414).
- This error also affects integrations. See our [Salesforce to Mailchimp](/integrations/salesforce-to-mailchimp/) and [Salesforce to ActiveCampaign](/integrations/salesforce-to-activecampaign/) integration error guides.

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
