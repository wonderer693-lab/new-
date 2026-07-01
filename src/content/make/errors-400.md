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
lastUpdated: '2026-05-08'
lastReviewed: "2026-06-29"
pageType: "error-code"
author: "API Integration Hub"
keywords:
  - "make api 400 error"
  - "make 400 fix"
  - "make api invalid request parameters"
  - "make http 400"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Make rejected your scenario configuration because something in your setup is wrong or missing.

**The fix:**
1. Open your scenario in Make and check each module for red error icons
2. Make sure every required field is filled in — no blank boxes
3. Check that your data types match (numbers where numbers go, text where text goes)

**Copy-paste this code** (if you're using a code editor):
```python
import json, requests

payload = {"name": "My Scenario", "organizationId": 12345}
resp = requests.post(url, headers=headers, json=payload)
if resp.status_code == 400:
    print(f"Fix this: {resp.json().get('error')}")
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Start with this prompt in ChatGPT, Claude, or any AI coding assistant:

> I'm getting a 400 Bad Request error from Make (Integromat).
> The error message is: "Invalid request parameters"
> I'm trying to configure a scenario module in Make.
> Please give me a step-by-step fix to find and correct the invalid settings.

A good response will walk you through checking each module's required fields and data types in your Make scenario.

Follow up with additional context if needed:
> The fix didn't work. I'm still getting 400 errors. Here's what my module settings look like: [paste your settings]. Please debug this.

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to fix Make 400 errors in popular automation tools:

### Make (Integromat)
1. Open your scenario → look for modules with a red warning icon
2. Click each flagged module → fill in all required fields marked with an asterisk (*)
3. Use the "Run once" button to test — Make will highlight exactly which field is wrong

### Zapier
1. Open your Zap → click the action step showing the error
2. Check that all required fields are filled in and match the expected format
3. Use Zapier's "Test" button to validate your step before turning on the Zap

### n8n
1. Open your workflow → click the node showing the error
2. Check the "Parameters" panel — make sure all required fields have valid values
3. Click "Execute Node" to test — n8n will show the exact field that failed validation

### Power Automate
1. Open your flow → click the action with the error
2. Check that all required fields are filled and use the correct data type
3. Use "Test" mode to run the flow and see which field is causing the 400 error

**Which tool should you use?** Make's own UI is best for this — it highlights invalid fields directly in the scenario editor with red icons.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"400 Bad Request"`
- `"Invalid request parameters"`
- `"invalid data"`
- `"Missing required field"` in your Make scenario logs

**What it means in plain English:** Make is saying your setup has something wrong — a missing field, a wrong data type, or bad formatting. Fix the highlighted fields and try again.

**Most common cause:** A module in your scenario has a blank required field or the wrong type of data (like text where a number should be).

</div>

## What Causes Make 400

Make returns HTTP 400 when the request contains invalid JSON, missing required parameters, or incorrectly typed values. This is a client-side validation error — the request was received but could not be processed due to malformed or invalid content. See all [Make API errors](/make/) in our complete reference.

Similar validation issues occur with [HubSpot 400](/hubspot/errors/400), [Salesforce 400](/salesforce/errors/400), and [Zapier 400](/zapier/errors/400).

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

This error also affects integrations. See our [Make to Slack integration errors](/integrations/make-to-slack/) for common cross-tool issues.

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
