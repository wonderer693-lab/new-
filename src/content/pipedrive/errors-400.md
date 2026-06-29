---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Pipedrive API 400: Request not understood"
description: "Fix Pipedrive API 400 (400 Bad Request) error. Request not understood — malformed JSON or invalid parameters. Check JSON syntax, required field presence, and parameter types."
tool: "pipedrive"
errorCode: "400"
errorName: "400 Bad Request"
httpStatus: 400
category: "validation"
severity: "medium"
priority: 2
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "pipedrive api 400 error"
  - "pipedrive 400 fix"
  - "pipedrive api request not understood —"
  - "pipedrive http 400"
---

## What Causes Pipedrive 400

Pipedrive returns HTTP 400 when the request body contains malformed JSON, missing required fields, or parameters with invalid values. This is the most common client error — the request was received but cannot be processed due to payload issues.

The response is `{"error":"Request not understood — malformed JSON or invalid parameters"}`. Pipedrive's API validates request bodies against strict schemas. Required fields vary by resource (e.g., `title` is required for deals, `name` for persons). Field types are also enforced — sending a string where an integer is expected will trigger 400.

### Common Scenarios
- Missing `title` field when creating a deal
- Invalid JSON with syntax errors (trailing comma, unquoted key)
- Wrong data type — sending "true" (string) instead of `true` (boolean)
- Invalid enum value — using an unsupported deal status
- Date/time in wrong format — Pipedrive expects `YYYY-MM-DD` for date fields

## How to Detect If You're Affected

1. Check the error message for details:
   ```bash
   curl -s -X POST "https://api.pipedrive.com/v1/deals?api_token=$TOKEN" \
     -H "Content-Type: application/json" \
     -d '{}' | jq '.error'
   ```

2. Validate your JSON syntax locally:
   ```bash
   echo '{"title": "Test", "value": "not-a-number"}' | jq .
   ```

## Step-by-Step Fix

### 1. Validate Required Fields
```python
# BAD — missing required fields
payload = {}  # 400 — title required for deals
requests.post("https://api.pipedrive.com/v1/deals?api_token=TOKEN", json=payload)

# GOOD — provide all required fields
payload = {
    "title": "Test Deal",
    "value": 1000,
    "currency": "USD",
    "status": "open",
}
```

### 2. Check Field Types
```python
# BAD — wrong types
payload = {
    "title": "Test Deal",
    "value": "1000",  # Should be numeric
    "probability": "50",  # Should be integer
    "visible_to": "1",  # Depends on endpoint
}

# GOOD — correct types
payload = {
    "title": "Test Deal",
    "value": 1000,
    "probability": 50,
}
```

### 3. Verify JSON Structure
```python
import json

# BAD — malformed JSON string
json_str = "{'title': 'test'}"  # Single quotes are invalid JSON

# GOOD — use json.dumps
payload = json.dumps({"title": "test"})  # Produces valid JSON
```

## Prevention

- Use a JSON validator (`jq .`) on every payload before sending
- Build payloads with typed dictionaries (not string concatenation)
- Log the full request body alongside every 400 response for rapid debugging
- Implement pre-submit validation: check required fields and types match API specs
- Test payloads against Pipedrive's API sandbox before production

## Official Documentation

- [Pipedrive API Documentation](https://developers.pipedrive.com/docs/api/v1)
- [Pipedrive Deals API](https://developers.pipedrive.com/docs/api/v1/deals)
- [Pipedrive API Errors](https://developers.pipedrive.com/docs/api/v1/errors)

## People Also Ask

- **What causes Pipedrive 400?** Invalid request body — malformed JSON, missing required fields, wrong data types, or invalid enum values.
- **How do I fix Pipedrive 400?** Validate your JSON with `jq`, ensure all required fields (like `title` for deals) are present, and use correct data types.
- **What fields are required for Pipedrive deal creation?** At minimum, `title` is required. Other common fields are `value`, `currency`, and `status`.
- **Does Pipedrive 400 mean my API token is wrong?** No — invalid tokens return 401. A 400 always means the request body is invalid.

## Related Errors

- [Pipedrive 401 Unauthorized](/pipedrive/errors/401) — Invalid API token
- [Pipedrive 422 Unprocessable Entity](/pipedrive/errors/422) — Webhooks limit reached
- [Pipedrive 404 Not Found](/pipedrive/errors/404) — Resource unavailable
