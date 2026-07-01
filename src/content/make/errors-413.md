---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Make API 413 Error: Payload Too Large — Fix & Prevention Guide"
description: "Fix Make API 413 error. Payload too large. Reduce request body size below 10MB limit and compress JSON payloads."
tool: "make"
errorCode: "413"
errorName: "413"
httpStatus: 413
category: "payload"
severity: "low"
priority: 2
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "make api 413 error"
  - "make 413 fix"
  - "make api payload too large"
  - "make http 413"
---

## What Causes Make 413

Make returns HTTP 413 when the request body exceeds its maximum payload size limits. Make enforces a maximum request body size (typically 10 MB for most endpoints, but may be lower for specific operations). This error commonly occurs when uploading large files, sending extensive JSON payloads with many bundles, or including Base64-encoded content that expands significantly in size.

The response is `{"error":"Payload too large"}`. This is a hard limit — splitting the payload into smaller chunks is the only solution. Make also has per-field size limits, so even if the total payload is under the limit, individual fields exceeding their maximum can trigger this error.

### Common Scenarios
- Uploading files larger than 10 MB through Make's API
- Sending scenario configurations with hundreds of module steps in a single payload
- Including large Base64-encoded binary data (e.g., images, PDFs) in API calls
- Bulk data operations that serialize thousands of records into a single request body

## How to Detect If You're Affected

1. Check the response status and body:
   ```bash
   curl -s -w "\n%{http_code}" -X POST "https://api.make.com/api/v2/..." \
     -H "Authorization: Token $TOKEN" \
     -H "Content-Type: application/json" \
     -d @large_payload.json | tail -1
   ```
   If the output is `413`, the payload is too large.

2. Measure your payload size:
   ```bash
   wc -c large_payload.json
   ```
   Compare against Make's limits (typically 10 MB for request bodies).

## Step-by-Step Fix

### 1. Split Large Payloads
```python
# BAD — sending all records at once
payload = {"data": all_10000_records}  # 413 if too large

# GOOD — send in batches
batch_size = 500
for i in range(0, len(all_records), batch_size):
    batch = all_records[i:i+batch_size]
    payload = {"data": batch}
    requests.post(url, headers=headers, json=payload)
```

### 2. Reduce File Size Before Upload
```python
# Compress or resize before uploading
import base64

# BAD — upload raw large file
large_data = open("large_file.pdf", "rb").read()
encoded = base64.b64encode(large_data).decode()

# GOOD — compress first or use chunked upload
# Check if Make supports chunked upload or file references
```

### 3. Use Streaming for Large Requests
If Make supports streaming, avoid loading the entire payload into memory:
```python
# Use memory-efficient approaches
with open("large_file.bin", "rb") as f:
    requests.post(url, headers=headers, data=f)  # streams the file
```

## Prevention

- Keep individual request payloads under 5 MB to stay well below the 10 MB limit
- Use batch processing — send data in chunks of 500 records or less
- Compress files before uploading (lower resolution, use efficient formats like CSV instead of Base64)
- Monitor Content-Length header before sending and warn if it exceeds limits
- For file transfers, use Make's dedicated file handling modules instead of raw API calls

## Official Documentation

- [Make API Documentation](https://www.make.com/en/api-documentation)
- [Make API File Limits](https://www.make.com/en/api-documentation#limits)
- [Make API Authentication](https://www.make.com/en/api-documentation#authentication)

## People Also Ask

- **What is Make's maximum payload size?** Make's API typically accepts request bodies up to 10 MB. Individual field limits may be smaller for specific data types.
- **Does Make support chunked uploads?** Make's REST API does not support chunked uploads. You must split large data into multiple requests or use Make's file transfer modules.
- **How do I fix Make 413?** Reduce the request body size — send data in smaller batches, compress files, or split single large requests into multiple smaller ones.
- **Can I request a higher payload limit from Make?** Make does not publicly offer payload limit increases. Use batching and chunking strategies instead.

## Related Errors

- [Make 429 Rate Limit](/make/errors/429) — Rate limit exceeded
- [Make 400 Bad Request](/make/errors/400) — Invalid request parameters
- [Make 500 Server Error](/make/errors/500) — Server error
