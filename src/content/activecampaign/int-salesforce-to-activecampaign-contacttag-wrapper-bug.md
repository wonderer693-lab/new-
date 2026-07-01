---
layout: ../../layouts/IntegrationErrorLayout.astro
title: "ActiveCampaign ContactTag Wrapper Bug — Flat POST Payload Returns 400"
description: "ActiveCampaign's POST /contactTags rejects flat tag payloads and requires a {'contactTag': {'contact': 'id', 'tag': 'id'}} wrapper. Flat payloads return 400 and your contact remains untagged. Fix by wrapping the payload."
toolA: "salesforce"
toolB: "activecampaign"
integrationSlug: "salesforce-to-activecampaign"
errorSlug: "contacttag-wrapper-bug"
errorName: "ContactTag wrapper bug"
category: "API_BUG"
errorType: "error"
severity: "high"
priority: 2
lastUpdated: "2026-03-18"
lastReviewed: "2026-03-18"
pageType: "integration-error"
author: "API Integration Hub"
keywords:
  - "activecampaign contacttags post 400 wrapper"
  - "activecampaign contacttag wrapper bug"
  - "activecampaign tag assignment payload schema"
  - "activecampaign flat payload rejected 400"
  - "activecampaign contacts tags postbody required format"
  - "salesforce activecampaign tag payload fix"
---


<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** ActiveCampaign's ContactTag API requires a specific wrapper format. Sending a flat payload returns HTTP 400 and contacts stay untagged. The fix is wrapping the payload in a contactTag key.

**The fix:**
1. Check your current payload -- if it looks like {"contact": "1", "tag": "2"}, it's missing the wrapper
2. Wrap the payload as {"contactTag": {"contact": "1", "tag": "2"}} with both IDs as strings
3. In Zapier or Make, use the built-in 'Add Tag' action which handles the wrapper automatically
4. Test with a single contact to confirm the tag appears in ActiveCampaign

**Copy-paste this code** (if you're using a code editor):
```python
import requests

def attach_tag(contact_id, tag_id, ac_url, ac_token):
    resp = requests.post(f"{ac_url}/api/3/contactTags",
        headers={"Api-Token": ac_token, "Content-Type": "application/json"},
        json={"contactTag": {"contact": str(contact_id), "tag": str(tag_id)}})
    return resp.json()
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code workaround](#no-code-workaround).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm integrating Salesforce with ActiveCampaign and getting HTTP 400 errors when trying to tag contacts. The error says 'Validation failed: Contact must be a valid contact id, Tag must be a valid tag id' but my IDs are correct. What's the correct payload format for the /contactTags endpoint?

**What to expect:** The AI should explain the required contactTag wrapper and help you fix the payload structure.

**If it doesn't work**, add this follow-up:
> I fixed the wrapper but I'm still getting 400 errors. Could the issue be that I'm sending integer IDs instead of string IDs?

**Best AI tools for this:** ChatGPT-4 (good at step-by-step UI navigation), Claude (good at explaining API concepts)

</div>

## No-Code Workaround <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to debug this? Here's how to handle Salesforce-to-ActiveCampaign tagging in other automation tools:

### Zapier
1. Use Zapier's native 'Add Tag to Contact' action for ActiveCampaign -- it handles the wrapper automatically
2. Map the Salesforce contact ID to the ActiveCampaign contact ID using a lookup step
3. Test the Zap with a single record to confirm the tag appears

### Make (Integromat)
1. Use Make's ActiveCampaign 'Add Tag' module -- it wraps the payload for you
2. Connect the Salesforce module output to the ActiveCampaign module input
3. Add an error handler to catch 400 errors and log them

### n8n
1. Add an HTTP Request node targeting the ActiveCampaign /contactTags endpoint
2. Set the body to JSON with the contactTag wrapper: {"contactTag": {"contact": "...", "tag": "..."}}
3. Add an IF node to check for 200 response and alert on failure

### Power Automate
1. Use the HTTP action to call ActiveCampaign's /contactTags endpoint
2. Set the body with the contactTag wrapper and string IDs
3. Add a condition to check the response and send an alert on failure

**Which tool should you use?** Zapier is the easiest -- its native ActiveCampaign 'Add Tag' action handles the payload wrapper automatically.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these:

- ActiveCampaign returns HTTP 400 when tagging contacts from Salesforce
- Error message says 'Validation failed' even though contact and tag IDs are valid
- Salesforce shows the sync as successful but ActiveCampaign contacts have no tags
- The same tag assignment works in the ActiveCampaign UI but fails via API

**What it means in plain English:** ActiveCampaign's API requires a specific JSON wrapper around the tag assignment payload. Without it, the API rejects the request even with valid IDs.

**Most common cause:** Sending a flat JSON payload like {"contact": "1", "tag": "2"} instead of wrapping it in {"contactTag": {...}}.

</div>

## The Problem

When applying Salesforce-driven tags to ActiveCampaign contacts, all POST calls to `/contactTags` fail with HTTP 400 and your contacts remain untagged. The error body is generic: `"Validation failed: Contact must be a valid contact id, Tag must be a valid tag id."` Meanwhile the IDs you supplied pass through `GET /tags` and `GET /contacts` with no issues. The header missing here is the wrapper, not the values.

## Root Cause

- **ActiveCampaign v3 endpoint** `/contactTags` requires a top-level wrapper object named `contactTag`:
  ```json
  {"contactTag": {"contact": "1", "tag": "2"}}
  ```
- **Flat payloads return 400**:
  ```json
  {"contact": "1", "tag": "2"}  // explicitly rejected
  ```
- **Type strictness**: `contact` and `tag` must be string representations of the integer IDs (not integers; not `null`).
- **Other ActiveCampaign endpoints** (`/.contacts`, `/tags`, `/fieldValues`) follow the same wrapper convention (`{"contact": {...}}`, `{"fieldValue": {...}}`), but their content sometimes validates partial usage while `contactTags` is strict.
- **Many SDK wrappers** for ActiveCampaign (community libraries) misserialize this; the bug surfaces most commonly in custom Salesforce integrations that auto-serialise generic structs.

| Payload | Response |
|---|---|
| `{"contactTag":{"contact":"1","tag":"2"}}` | 200 created |
| `{"contact":1,"tag":2}` (numbers, no wrapper) | 400 validation |
| `{"contact":"1","tag":"2"}` (strings, no wrapper) | 400 validation |
| `{"contactTag":{"contact":1,"tag":2}}` (numbers inside wrapper) | 400 validation on some tenants |

## How to Detect If You're Affected

1. Middleware log for the response body:
   ```bash
   rg 'POST.*contactTags.*400' middleware.log
   ```
2. Spot-check untagged contacts — sync the expected tags and verify by:
   ```bash
   curl -s "https://$AC.api-us1.com/api/3/contacts/1/contactTags" \
     -H "Api-Token: $AC_TOKEN" | jq '.contactTags'
   ```
   Empty array means the tag never persisted.
3. Verify the exact payload hit:
   ```bash
   rg 'POST.*contactTags' --csv-outgoing.log
   ```

## Step-by-Step Fix

1. Wrap the payload in the `contactTag` key:
   ```python
   import requests
   def attach_tag(contact_id, tag_id, ac_token):
       return requests.post(f"https://{ac}.api-us1.com/api/3/contactTags",
                            headers={"Api-Token": ac_token, "Content-Type": "application/json"},
                            json={"contactTag": {"contact": str(contact_id), "tag": str(tag_id)}}).json()
   ```
2. Resolve Salesforce lead id → ActiveCampaign contact id via `POST /contact/sync` first:
   ```bash
   cid=$(curl -s -X POST "https://$AC.api-us1.com/api/3/contact/sync" \
       -H "Api-Token: $AC_TOKEN" -H "Content-Type: application/json" \
       -d '{"contact":{"email":"u@example.com"}}' | jq -r .contact.id)
   tid=$(curl -s "https://$AC.api-us1.com/api/3/tags?search=Priority" -H "Api-Token: $AC_TOKEN" \
       | jq -r '.tags[0].id')
   ```
3. Wrong: pass integers directly. Correct: stringify both ids.
4. Idempotency: ActiveCampaign does not return an error on duplicate tag applications, so safe to retry on 500.
5. Bulk tag: iterate at 0.25 s between calls, since ActiveCampaign enforces ~5 req/s.

## Prevention

- Persist a Salesforce ID → ActiveCampaign contact ID map so tagging flows always have the numeric string ready.
- Validate the response `200 contactTag.id` after POST; if missing, raise an alert — generic 400 errors are easy to ignore.
- Document the wrapper requirement for every ActiveCampaign insert-style endpoint across your team's integration documentation.
- Add a single end-to-end unit test that asserts tags are visible after sync, run daily.
- Review third-party clients that interact with ActiveCampaign — confirm they wrap payloads correctly before production rollout.

## Integration-Specific Context

- **Native Salesforce-AC connector**: uses correct wrappers; you won't see this if you use the official connector.
- **Zapier ActiveCampaign app**: handles wrappers internally for "Add tag to contact" actions.
- **Make ActiveCampaign module**: same — the "Add Tag" module wraps the payload for you.
- **Custom middleware**: snippet shows the required wrapper, the only place this bug surfaces.
- **2026 change**: ActiveCampaign announced the v3 API contract stabilization (no schema change to `contactTags`); the wrapper requirement will remain in v3 forever, plan accordingly.

## People Also Ask

- **What's the correct ActiveCampaign POST `/contactTags` payload?** `{"contactTag": {"contact": "<contact_id>", "tag": "<tag_id>"}}` — both ids as strings, wrapped in `contactTag`.
- **Why does ActiveCampaign return 400 on tag assignment?** Most causes are missing the `contactTag` wrapper or sending numeric integers instead of strings — fix the wrapper; the response will validate. Empty contact/tag ids return the same 400.
- **Does ActiveCampaign deduplicate tag assignment?** No — applying the same tag twice does not raise an error, so it's safe to call idempotently on retry.
- **Is there a bulk tag assignment endpoint in ActiveCampaign?** No bulk endpoint exists; iterate per contact at ≤5 req/s to stay within rate limits.

## Official Documentation

**Salesforce:**
- [REST API](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/)
- [OAuth](https://help.salesforce.com/s/articleView?id=sf.remoteaccess_oauth_web_server_flow.htm)

**ActiveCampaign:**
- [API Overview](https://developers.activecampaign.com/reference/overview)
- [Contact Tags](https://developers.activecampaign.com/reference/create-a-new-contacttag)

## Related Errors
- [Custom field type mismatch (Salesforce ↔ ActiveCampaign)](/integrations/salesforce-to-activecampaign/errors/custom-field-type-mismatch)
- [Salesforce daily API limit exhausted by AC sync](/integrations/salesforce-to-activecampaign/errors/salesforce-daily-api-limit-exhausted-by-ac-sync)
- [ActiveCampaign API rate limit on webhook responses](/integrations/activecampaign-to-slack/errors/activecampaign-api-rate-limit-on-webhook-responses)
- [Salesforce API Reference](/salesforce)
- [ActiveCampaign API Reference](/activecampaign)