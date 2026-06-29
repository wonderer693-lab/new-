---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "Make API 400: Invalid request parameters"
description: "Fix Make API 400 error. Invalid request parameters. Check request body and parameter types."
tool: "make"
errorCode: "400"
errorName: "400"
httpStatus: 400
category: "validation"
severity: "medium"
priority: 2
lastUpdated: "2026-06-29"
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "make api 400 error"
  - "make 400 fix"
  - "make api invalid request parameters"
  - "make http 400"
---

## What Causes Make 400

Make returns HTTP 400 when the request contains invalid JSON, missing required parameters, or incorrectly typed values. This is a client-side validation error — the request was received but could not be processed due to malformed or invalid content.

The response typically includes `{"error":"Invalid request parameters"}`. Since Make's API manages complex resources like scenarios, webhooks, and connections, the validation rules can be strict — wrong parameter names, nested objects, or data types all trigger 400.

### Common Scenarios
- Invalid JSON syntax in the request body (trailing commas, unquoted keys)
- Missing required fields for a scenario or webhook configuration
- Wrong data type — sending a string where an integer is expected
- Invalid date/time format in scheduling parameters
- Passing an empty array or null for a required collection

## How to Detect If You're Affected

1. Inspect the full error response:
   ```bash
   curl -s -X POST "https://api.make.com/api/v2/scenarios" \
     -H "Authorization: Token $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"invalid": true}' | jq .
   ```

2. Validate your JSON before sending:
   ```bash
   echo '{"name": "test", "invalid trailing comma",}' | jq .
   # jq will show parse error with line number
   ```

## Step-by-Step Fix

### 1. Validate JSON Structure
```python
import json

# BAD — raw string with potential issues
payload = '{"name": "test"}'  # Works but error-prone

# GOOD — use Python dicts
payload = json.dumps({
    "name": "Test Scenario",
    "description": "Integration scenario",
    "organizationId": 12345,
})
```

### 2. Check Required Parameters
```python
# Make endpoints have specific required fields
required = {
    "/scenarios": ["name", "organizationId"],
    "/webhooks": ["name", "url"],
}

endpoint = "/scenarios"
for field in required[endpoint]:
    if field not in payload:
        print(f"Missing required parameter: {field}")
```

### 3. Correct Data Types
```python
# BAD — wrong types
payload = {
    "name": "Test",
    "organizationId": "12345",  # Should be integer
    "active": "true",  # Should be boolean
    "schedule": "2024-01-01",  # May need specific format
}

# GOOD — correct types
payload = {
    "name": "Test",
    "organizationId": 12345,
    "active": True,
    "schedule": {"type": "interval", "minutes": 15},
}
```

## Prevention

- Build a JSON schema for each endpoint and validate before every request
- Use type-safe constructors — never concatenate strings to build JSON
- Log the exact request body alongside every 400 response for rapid debugging
- Test payloads against Make's API playground or a development organization first
- Implement integration tests that verify payload structure against known-good examples

## Official Documentation

- [Make API Documentation](https://www.make.com/en/api-documentation)
- [Make Scenarios API](https://www.make.com/en/api-documentation#scenarios)
- [Make Webhooks API](https://www.make.com/en/api-documentation#webhooks)

## People Also Ask

- **How do I fix Make 400?** Check your request body for valid JSON, ensure all required parameters are present, and verify data types match the API specification.
- **Does Make 400 mean my token is wrong?** No — 400 is a validation error on the request body. If your token were wrong, you'd get 401 (Unauthorized).
- **What's the most common cause of Make 400?** Invalid JSON syntax — trailing commas, unquoted string keys, or missing closing brackets are the most frequent issues.
- **How do I validate JSON for Make API?** Use `jq .` to parse and pretty-print your JSON before sending. If jq fails, your JSON is malformed.

## Related Errors

- [Make 401 Unauthorized](/make/errors/401) — Invalid or missing token
- [Make 403 Forbidden](/make/errors/403) — Insufficient permissions
- [Make 413 Payload Too Large](/make/errors/413) — Payload too large
