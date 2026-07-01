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

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Pipedrive rejected your data format — your request has bad JSON, missing fields, or wrong data types.

**The fix:**
1. Check your JSON for syntax errors (trailing commas, missing quotes)
2. Make sure all required fields are included (like `title` for deals)
3. Use the right data types — numbers for numbers, strings for text

**Copy-paste this code** (if you're using a code editor):
```python
import json, requests

payload = {"title": "My Deal", "value": 1000, "currency": "USD"}
json_str = json.dumps(payload)
resp = requests.post(
    "https://api.pipedrive.com/v1/deals?api_token=TOKEN",
    data=json_str, headers={"Content-Type": "application/json"}
)
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm getting a 400 Bad Request error from the Pipedrive API.
> The error message is: "Request not understood — malformed JSON or invalid parameters"
> I'm trying to create a deal but Pipedrive rejects my data.
> Please give me a step-by-step fix with working Python code that validates the payload before sending.

**What to expect:** The AI should give you a validated payload builder that checks required fields and data types before calling Pipedrive.

**If it doesn't work**, add this follow-up:
> The fix didn't work. I'm still getting 400 errors. Here's my payload: [paste your JSON]. Please debug this.

**Best AI tools for this:** Claude (best at explaining validation), ChatGPT-4 (good code generation), Cursor (if you want inline code fixes)

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to handle Pipedrive data validation errors in popular automation tools:

### Zapier
1. Open your Zap → click the Pipedrive action step
2. Check that all required fields (like Deal Title) are mapped — empty required fields cause 400 errors
3. Use Zapier's "Formatter" step before Pipedrive to clean up data (remove special characters, fix date formats)

### Make (Integromat)
1. Open your scenario → click the Pipedrive module
2. In the field mapping, make sure required fields have values — use the "ifempty" function as a fallback
3. Add a "Tools > Set Variable" module before Pipedrive to format dates as YYYY-MM-DD

### n8n
1. Open your workflow → click the Pipedrive node
2. In the parameters panel, verify all required fields are filled — check for null or undefined values
3. Add a "Function" node before Pipedrive to validate and clean your data

### Power Automate
1. Open your flow → click the Pipedrive action
2. Check that required fields have values — use the "coalesce" expression for fallback values
3. Add a "Compose" action before Pipedrive to format data correctly (dates, numbers, booleans)

**Which tool should you use?** Zapier has the best field validation for Pipedrive — it highlights missing required fields before sending.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"400 Bad Request"`
- `"Request not understood — malformed JSON or invalid parameters"`
- `"invalid data"`
- `"HTTP 400"` in your integration logs

**What it means in plain English:** Pipedrive can't understand your request. Something in the data you sent is wrong — bad formatting, missing info, or wrong types.

**Most common cause:** Sending a request with missing required fields (like forgetting the deal title) or using the wrong data type (text instead of a number).

</div>

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

See all [Pipedrive API errors](/pipedrive/) in our complete reference. Similar validation issues occur with [HubSpot 400](/hubspot/errors/400), [Salesforce 400](/salesforce/errors/400), and [Mailchimp 400](/mailchimp/errors/400). This error also affects integrations — see our [Pipedrive to Mailchimp integration errors](/integrations/pipedrive-to-mailchimp/) for common cross-tool issues.
