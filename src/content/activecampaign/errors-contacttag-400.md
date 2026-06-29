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

## Related Errors

- [Salesforce INVALID_SESSION_ID](/salesforce/errors/INVALID_SESSION_ID)
- [Custom field type mismatch (Salesforce ↔ ActiveCampaign)](/integrations/salesforce-to-activecampaign/errors/custom-field-type-mismatch)