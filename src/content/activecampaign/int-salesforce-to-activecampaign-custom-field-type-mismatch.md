---
layout: ../../layouts/IntegrationErrorLayout.astro
title: "Salesforce ActiveCampaign Custom Field Type Mismatch — Picklist and Boolean Drops"
description: "Salesforce picklist values are option labels (display strings); ActiveCampaign dropdown options require the internal option name. Booleans don't translate to ActiveCampaign checkboxes. Use explicit option-name mapping; fall back to a text field when types diverge."
toolA: "salesforce"
toolB: "activecampaign"
integrationSlug: "salesforce-to-activecampaign"
errorSlug: "custom-field-type-mismatch"
errorName: "Custom field type mismatch"
category: "FIELD_MAPPING"
errorType: "error"
severity: "high"
priority: 2
lastUpdated: "2026-06-22"
lastReviewed: "2026-06-22"
pageType: "integration-error"
author: "API Integration Hub"
keywords:
  - "salesforce activecampaign field type mismatch"
  - "activecampaign custom field dropdown option name"
  - "salesforce picklist to activecampaign dropdown mapping"
  - "activecampaign checkbox boolean salesforce"
  - "activecampaign custom field validation rejected"
  - "salesforce to activecampaign field mapping fix"
---


<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Salesforce and ActiveCampaign use different field types. Picklist values from Salesforce don't match ActiveCampaign dropdown options, and booleans don't translate to checkboxes. Fields arrive blank in ActiveCampaign.

**The fix:**
1. Check which Salesforce fields are syncing blank into ActiveCampaign
2. Look up the ActiveCampaign field type and options for each field (GET /fields)
3. Map Salesforce picklist values to ActiveCampaign dropdown option labels
4. Convert Salesforce booleans to '0'/'1' strings for ActiveCampaign checkboxes

**Copy-paste this code** (if you're using a code editor):
```python
import requests

f = requests.get(f"{ac_url}/api/3/fields",
    headers={"Api-Token": token}).json()
for field in f["fields"]:
    if field["type"] == "dropdown":
        print(field["title"], field.get("options", []))
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code workaround](#no-code-workaround).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm integrating Salesforce with ActiveCampaign and custom fields are syncing blank. Salesforce sends picklist values as internal names but ActiveCampaign dropdowns expect option labels. How do I map Salesforce picklist values to ActiveCampaign dropdown options correctly?

**What to expect:** The AI should help you build a mapping between Salesforce picklist values and ActiveCampaign dropdown labels, and handle boolean/date conversions.

**If it doesn't work**, add this follow-up:
> I mapped the dropdown values but date fields are still failing. Salesforce sends ISO timestamps -- what format does ActiveCampaign expect?

**Best AI tools for this:** ChatGPT-4 (good at step-by-step UI navigation), Claude (good at explaining API concepts)

</div>

## No-Code Workaround <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to debug this? Here's how to handle Salesforce-to-ActiveCampaign field mapping in other automation tools:

### Zapier
1. Use Zapier's 'Formatter' step to convert picklist values before the ActiveCampaign action
2. Add a 'Lookup Table' in Formatter to map Salesforce values to ActiveCampaign option labels
3. Use the 'Format Date' step to convert ISO timestamps to YYYY-MM-DD

### Make (Integromat)
1. Add a 'Set Variable' module to transform field values before the ActiveCampaign module
2. Use Make's built-in date formatting to convert Salesforce timestamps
3. Create a lookup table in a Data Store for picklist-to-dropdown mapping

### n8n
1. Add a 'Set' node to transform each field value before the ActiveCampaign node
2. Use the 'Date & Time' node to convert ISO dates to YYYY-MM-DD
3. Map picklist values using an expression with a lookup object

### Power Automate
1. Use a 'Compose' action to transform field values before the ActiveCampaign action
2. Add a 'Condition' to check field types and apply the correct conversion
3. Use the 'Convert time zone' action for date fields

**Which tool should you use?** Zapier is the easiest -- its Formatter step handles picklist mapping and date conversion without code.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these:

- ActiveCampaign custom fields show blank values after Salesforce sync
- Salesforce picklist values don't appear in ActiveCampaign dropdown fields
- Boolean fields from Salesforce show as literal 'true'/'false' instead of checkboxes
- ActiveCampaign segmentation by custom field returns zero contacts

**What it means in plain English:** Salesforce and ActiveCampaign use different data formats for the same field types. Without conversion, ActiveCampaign silently drops values that don't match its expected format.

**Most common cause:** Passing Salesforce picklist internal values directly to ActiveCampaign dropdowns, which expect option labels instead.

</div>

## The Problem

Salesforce picklist updates pushed to ActiveCampaign arrive blank, or the picklist array arrives as `[redundant.encoded.label]` and silently refuses. Sometimes a Salesforce boolean true/false becomes "1"/"0" and triggers a duplicate-value error in ActiveCampaign's strict checkbox validation. New contacts arrive without their favorite fields populated, segmentation breaks, and operations teams scramble to remediate the silent data loss.

## Root Cause

- **Salesforce picklist REST response**: returns `{value: "Implementation", label: "Implementation Phase"}` and the value is the internal API name; picklist labels change in translation workflows without changing the value.
- **ActiveCampaign custom field options**: stored as numeric IDs alongside an admin-readable label; the custom field API expects the **option label** (e.g., `"Implementation"`) as the payload string, not the option id.
- **Salesforce boolean**: only `true`/`false`, never `0` or `1`; ActiveCampaign accepts only `"0"`/`"1"` or boolean `true`/`false`. ActiveCampaign's checkbox rejects the value when the active "0" is sent as a string boolean.
- **Date conversion**: ActiveCampaign expects `YYYY-MM-DD`; Salesforce ships ISO timestamps.
- **Required**: ActiveCampaign custom fields with `isrequired=1` reject `null` payloads.

| Salesforce field type | ActiveCampaign type | Failure mode | Fix |
|---|---|---|---|
| Picklist (value="Implementation") | Dropdown (option "Implementation Phase") | Stores blank | Map option label |
| Checkbox | `1`/`0` | Stores `1` as literal "1" string | Cast bool to "0"/"1" |
| Date | `date` | ISO timestamp rejected | Cast to `YYYY-MM-DD` |
| Number (text in JSON) | Number | Append `.0` accepted | numeric cast |
| Multi-select | Tags (single-comma) | `["a","b"]` JSON broken | Concatenate as comma-string |

## How to Detect If You're Affected

1. List ActiveCampaign custom fields and their option sets:
   ```bash
   curl -s "https://$AC.api-us1.com/api/3/fields?limit=100" \
     -H "Api-Token: $AC_TOKEN" | jq '.fields[] | {title, type, options}'
   ```
   Inspect option labels vs what Salesforce pushes.
2. Pull a sample Salesforce contact:
   ```bash
   sfdx force:data:soql:query -q "SELECT PicklistField__c, CheckboxField__c FROM Contact LIMIT 5"
   ```
3. Search middleware logs for `Field value not allowed` or `validation_failed`:
   ```bash
   rg 'field.*validation|option.*not.*allowed' middleware.log
   ```
4. Symptom: ActiveCampaign segmentation by custom field returns 0 contacts; picklist-driven workflow queues stall.

## Step-by-Step Fix

1. Fetch the ActiveCampaign field schema with options, and build a map:
   ```python
   import requests
   f = requests.get(f"https://{ac}.api-us1.com/api/3/fields",
                    headers={"Api-Token": token}).json()
   opt_map = {}
   for field in f["fields"]:
       if field["type"] == "dropdown":
           opt_map[field["title"]] = {o["value"]: o["label"] for o in field.get("options", [])}
   ```
2. Map Salesforce picklist **value** to ActiveCampaign option **label**:
   ```python
   def to_ac_dropdown(sf_value, field_title):
       for opt_value, opt_label in opt_map[field_title].items():
           if opt_value in (sf_value, sf_value.lower(), sf_value.upper()):
               return opt_label
       return sf_value  # fallback text
   ```
3. Cast booleans to `"0"`/`"1"` (ActiveCampaign's checkbox canonical form):
   ```python
   def sf_bool_to_ac(val):
       if val in (True, "true", "TRUE", "1"):
           return "1"
       return "0"
   ```
4. Send via `POST /contact/sync` (upsert on email):
   ```bash
   curl -s -X POST "https://$AC.api-us1.com/api/3/contact/sync" \
     -H "Api-Token: $AC_TOKEN" -H "Content-Type: application/json" \
     -d '{
       "contact": {"email":"u@example.com","fieldValues":[
         {"field":"7","value":"Implementation Phase"},
         {"field":"8","value":"1"}
       ]}}'
   ```
5. Wrong: pass Salesforce picklist **value** ("Implementation") directly as the ActiveCampaign dropdown payload. Correct: convert to the option **label** ("Implementation Phase").

## Prevention

- Cache the ActiveCampaign field schema (with options) inside your sync service; refresh on every sync run to catch admin-created options.
- Default to ActiveCampaign `text` field type when type uncertainty exists — text never fails validation, only the dropdown strict fields do.
- Audit ActiveCampaign dropdown options monthly for unused or duplicate labels; the API rejects duplicates when a contact value doesn't match exactly.
- Add a unit test that runs through sample Salesforce picklist values and asserts the ActiveCampaign mapping is non-blank per field.
- For boolean sync, verify consistent casing — Salesforce booleans serialize inconsistently across API versions.

## Integration-Specific Context

- **Native Salesforce-AC connector**: maintains its own picklist-to-dropdown translation table; teams often duplicate that mapping in custom flows without realizing the connector does it for free.
- **Zapier**: use the "Formatter" "Pick List" → "Default Value" mapping before the ActiveCampaign "Create Update Contact" action.
- **Make**: same pattern; map field via the "Get" or "Set Variable" module.
- **Custom middleware**: snippet above is canonical; centralize option label maps so every sync reuses them.
- **2026 change**: ActiveCampaign introduced "default fallback" field-level config that allows bad dropdown values to auto-write to text-field version of the same field, preventing total drops — enable in the admin.

## People Also Ask

- **Why does my Salesforce picklist sync blank into ActiveCampaign?** ActiveCampaign dropdowns expect the option label (`Implementation Phase`), but Salesforce ships the picklist internal value (`Implementation`); without conversion, ActiveCampaign silently drops the value.
- **How do I sync Salesforce booleans to ActiveCampaign checkboxes?** Convert `true/false` to `"1"/"0"` (string) — ActiveCampaign's checkbox API accepts either but rejects raw booleans when sent as JSON `true`/`false`.
- **Can I use ActiveCampaign text fields for Salesforce picklists?** Yes — text fields never fail option validation; switch dropdown fields to text when picklist values are volatile across languages.
- **Does ActiveCampaign expose an API for custom field options?** Yes; `GET /fields` returns each dropdown field with its options array, each carrying option `id` and `label`. Cache this map for translation.

## Official Documentation

**Salesforce:**
- [REST API](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/)
- [Limits](https://developer.salesforce.com/docs/atlas.en-us.salesforce_app_limits_cheatsheet.meta/salesforce_app_limits_cheatsheet/)

**ActiveCampaign:**
- [API Overview](https://developers.activecampaign.com/reference/overview)
- [Authentication](https://developers.activecampaign.com/reference/authentication)

## Related Errors
- [ContactTag wrapper bug (Salesforce ↔ ActiveCampaign)](/integrations/salesforce-to-activecampaign/errors/contacttag-wrapper-bug)
- [Salesforce daily API limit exhausted by AC sync](/integrations/salesforce-to-activecampaign/errors/salesforce-daily-api-limit-exhausted-by-ac-sync)
- [Custom field type mismatch (Salesforce ↔ Mailchimp)](/integrations/salesforce-to-mailchimp/errors/custom-field-type-mismatch)
- [Salesforce API Reference](/salesforce)
- [ActiveCampaign API Reference](/activecampaign)