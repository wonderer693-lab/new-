---
layout: "../../layouts/ErrorCodeLayout.astro"
title: "ActiveCampaign ContactTag 400 — Payload Format Bug & Fix"
description: "Fix ActiveCampaign contactTags API 400 error. Correct payload format: {'contactTag': {'contact': '1', 'tag': '2'}} not {'contact': '1', 'tag': '2'}. Official docs issue."
tool: "activecampaign"
errorCode: "400"
errorName: "Bad Request — ContactTag Payload"
httpStatus: 400
category: "api-bug"
severity: "high"
priority: 2
lastUpdated: "2026-03-23"
keywords:
  - "activecampaign contacttag 400 error"
  - "activecampaign contacttag payload format"
  - "activecampaign api documentation bug"
  - "activecampaign tag contact fix"
  - "activecampaign contacttag wrapper object"
---

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** The ContactTag API call has a format bug — your payload is missing the `contactTag` wrapper object.

**The fix:**
1. Wrap your payload inside a `"contactTag"` key
2. Change `{"contact": "1", "tag": "2"}` to `{"contactTag": {"contact": "1", "tag": "2"}}`
3. Re-send the request

**Copy-paste this code** (if you're using a code editor):
```python
import requests

headers = {"Api-Token": "YOUR_TOKEN", "Content-Type": "application/json"}
payload = {"contactTag": {"contact": "1", "tag": "2"}}  # Must have contactTag wrapper
resp = requests.post("https://{account}.api-us1.com/api/3/contactTags", headers=headers, json=payload)
print(resp.status_code)  # 201 means it worked
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm getting a 400 Bad Request error from the ActiveCampaign contactTags API.
> The error message mentions "contactTag wrapper" or "Invalid request".
> I'm sending POST /api/3/contactTags with payload {"contact": "1", "tag": "2"}.
> Please give me the correct payload format with working Python code.

**What to expect:** The AI should show you the correct wrapper structure and explain that ActiveCampaign requires all resource payloads to be wrapped in a resource key.

**If it doesn't work**, add this follow-up:
> The fix didn't work. I'm using the contactTag wrapper but still getting 400. Here's my exact payload: [paste it]. Please debug this.

**Best AI tools for this:** Claude (best at explaining API payload structures), ChatGPT-4 (good code generation), Cursor (if you want inline code fixes)

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to fix the ContactTag payload structure in popular automation tools:

### Zapier
1. Open your Zap → check if you're using "Webhooks by Zapier" to call contactTags directly
2. In the webhook body, wrap your JSON: `{"contactTag": {"contact": "ID", "tag": "ID"}}`
3. If using the built-in ActiveCampaign "Add Tag" action, it handles this automatically — no fix needed

### Make (Integromat)
1. Open your scenario → click the ActiveCampaign "Create a Contact Tag" module
2. If using a custom API call module, set the body to: `{"contactTag": {"contact": "ID", "tag": "ID"}}`
3. The native ActiveCampaign module handles the wrapper for you — switch to it if possible

### n8n
1. Open your workflow → click the ActiveCampaign node or HTTP Request node
2. In the JSON body, use: `{"contactTag": {"contact": "ID", "tag": "ID"}}`
3. If using the native ActiveCampaign node, the wrapper is added automatically

### Power Automate
1. Open your flow → click the HTTP action that calls contactTags
2. Set the body to: `{"contactTag": {"contact": "ID", "tag": "ID"}}`
3. If using the ActiveCampaign connector's built-in action, the wrapper is handled for you

**Which tool should you use?** The built-in ActiveCampaign actions in Zapier, Make, and n8n all handle the wrapper automatically. Only custom webhook calls need the manual fix.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"400 Bad Request"`
- `"contactTag wrapper"`
- `"Invalid request"` on the contactTags endpoint
- `"/data"` in the error source pointer

**What it means in plain English:** Your API request to tag a contact has the wrong format. ActiveCampaign expects the data to be wrapped inside a `contactTag` object, but you're sending it flat. It's like putting a letter in the mailbox without an envelope.

**Most common cause:** Following outdated or incorrect documentation that shows the payload without the required `contactTag` wrapper key.

</div>

## The Bug



ActiveCampaign's `POST /api/3/contactTags` endpoint requires a specific JSON wrapper structure that differs from what many developers (and some documentation examples) expect.



### Wrong (Returns 400):

```json

{

  "contact": "1",

  "tag": "2"

}

```



### Correct:

```json

{

  "contactTag": {

    "contact": "1",

    "tag": "2"

  }

}

```



## Why This Happens

- ActiveCampaign API wraps most resources in a resource key (e.g., `{'contact': {...}}` for contacts)

- The contactTags endpoint follows this pattern but the documentation is inconsistent

- Developer community reports confirm this as a recurring issue (2025-2026)

- Zapier/Make connectors handle this internally, but custom API calls and Code by Zapier fail



## Step-by-Step Fix



```python

import requests



# WRONG — produces 400

wrong_payload = {

    "contact": contact_id,

    "tag": tag_id

}

resp = requests.post(

    "https://{account}.api-us1.com/api/3/contactTags",

    headers=headers,

    json=wrong_payload

)

print(resp.status_code)  # 400



# CORRECT

correct_payload = {

    "contactTag": {

        "contact": contact_id,

        "tag": tag_id

    }

}

resp = requests.post(

    "https://{account}.api-us1.com/api/3/contactTags",

    headers=headers,

    json=correct_payload

)

print(resp.status_code)  # 201 or 200

```



## How to Detect If You're Affected

1. Check the response body — ActiveCampaign returns `{"errors":[{"title":"Invalid request","detail":"...","source":{"pointer":"/data"}}]}` with status 400.
2. Inspect your request payload structure:
   ```bash
   curl -s -X POST https://{account}.api-us1.com/api/3/contactTags \
     -H "Api-Token: $KEY" -H "Content-Type: application/json" \
     -d '{"contact":"1","tag":"2"}' | jq .
   ```
   If it returns 400, you're missing the `contactTag` wrapper.
3. Compare your payload to the correct format — the top-level key must be `contactTag`, not `contact` or `tag`.
4. Symptom: all `contactTags` POST requests fail with 400, while other endpoints (contacts, deals) succeed.

## Prevention

- Always wrap related-resource payloads in the resource key object

- Test with ActiveCampaign API Playground before production

- Add JSON schema validation to your integration (catch wrapper bugs at dev time)

- Log full API request/response for debugging (redact API key)



## If You Use Zapier or Make

- Standard connectors handle this correctly

- If using 'Webhooks by Zapier' or 'Code by Zapier' to call ActiveCampaign API directly, you must use the correct wrapper format

- Test with a single contact before batch operations



## People Also Ask

- **Why does ActiveCampaign return 400 on contactTags?** The API requires a wrapper object: `{"contactTag":{"contact":"1","tag":"2"}}`. Sending `{"contact":"1","tag":"2"}` directly returns 400 Bad Request.
- **Does the wrapper apply to all ActiveCampaign resources?** Yes — most endpoints follow this pattern: `{"contact":{...}}` for contacts, `{"deal":{...}}` for deals, `{"contactTag":{...}}` for contact tags. Check the API docs for each endpoint.
- **Why does Zapier work but my custom code fails?** Zapier's ActiveCampaign app handles the wrapper internally. Custom API calls, Code by Zapier, and Webhooks by Zapier require you to build the correct payload structure.
- **How do I test ActiveCampaign API payloads?** Use the ActiveCampaign API Playground (Settings > Developer > API Playground) to test requests before deploying to production.

## Official Documentation

- [ActiveCampaign API Overview](https://developers.activecampaign.com/reference/overview)
- [ActiveCampaign Authentication](https://developers.activecampaign.com/reference/authentication)
- [ActiveCampaign Contact Tags](https://developers.activecampaign.com/reference/create-a-new-contacttag)

See all [ActiveCampaign API errors](/activecampaign/) in our complete reference.

Similar validation issues occur with [HubSpot 400](/hubspot/errors/400), [Salesforce 400](/salesforce/errors/400), and [Mailchimp 400](/mailchimp/errors/400).

This error also affects integrations. See our [ActiveCampaign to Slack](/integrations/activecampaign-to-slack/) and [Salesforce to ActiveCampaign](/integrations/salesforce-to-activecampaign/) integration error guides.

## Related Errors

- [Salesforce INVALID_SESSION_ID](/salesforce/errors/INVALID_SESSION_ID)
- [Custom field type mismatch (Salesforce ↔ ActiveCampaign)](/integrations/salesforce-to-activecampaign/errors/custom-field-type-mismatch)