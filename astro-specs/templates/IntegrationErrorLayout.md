# IntegrationErrorLayout — Astro Template Spec

## Route
`/integrations/[tool-a]-[tool-b]/errors/[error-slug]`

## Example URLs
- `/integrations/hubspot-salesforce/errors/field-mapping-mismatch` — "HubSpot ↔ Salesforce Field Mapping Mismatch"
- `/integrations/hubspot-mailchimp/errors/unsubscribe-sync-failure` — "HubSpot ↔ Mailchimp Unsubscribe Sync Failure"
- `/integrations/hubspot-pipedrive/errors/deal-currency-mismatch` — "HubSpot ↔ Pipedrive Deal Currency Mismatch"

## Page Purpose
Cross-tool integration errors — the "silent failure" layer competitors don't cover. These have lower search volume but near-zero competition and extremely high conversion value (reader is actively running an integration in production).

## Frontmatter Schema

```yaml
---
layout: ../../layouts/IntegrationErrorLayout.astro
title: "HubSpot ↔ Salesforce Field Mapping Mismatch: Integration Value vs Label"
description: "Fix HubSpot ↔ Salesforce field mapping mismatch. Why 'Integration Value' in HubSpot maps to 'Label' in Salesforce and how to handle picklist translation."
toolA: "hubspot"
toolB: "salesforce"
errorSlug: "field-mapping-mismatch"
errorName: "Field Mapping Mismatch — Integration Value vs Label"
category: "data-mapping"
errorType: "silent-failure"
severity: "medium"
priority: 2
lastUpdated: "2026-06-26"
keywords:
  - "hubspot salesforce field mapping"
  - "salesforce integration value vs label"
  - "hubspot salesforce picklist translation"
  - "hubspot salesforce silent data loss"
  - "hubspot salesforce field mismatch fix"
---
```

## Page Template Structure

```
┌─────────────────────────────────────────────┐
│  Breadcrumb                                  │
│  Integrations > HubSpot-Salesforce > Errors >
│  Field Mapping Mismatch                     │
├─────────────────────────────────────────────┤
│  H1: HubSpot ↔ Salesforce Field Mapping     │
│      Mismatch — Integration Value vs Label   │
│                                               │
│  Metadata bar:                                │
│  ⚠ Severity: Medium  |  🕳 Error Type:     │
│  Silent Failure                              │
│  📅 Updated: Jun 26, 2026                    │
├─────────────────────────────────────────────┤
│  The Problem (top fold, critical)            │
│  "If you're syncing picklist fields between  │
│   HubSpot and Salesforce, your data is       │
│   probably wrong right now and you don't     │
│   know it."                                  │
│                                               │
│  HubSpot sends: "Integration Value"          │
│  Salesforce expects: "Label"                │
│  Result: Field set to blank. No error log.  │
├─────────────────────────────────────────────┤
│  Table of Contents (sticky)                  │
│  1. Root cause                              │
│  2. How to detect if you're affected        │
│  3. Fix: Custom mapping table               │
│  4. Prevention                              │
│  5. Integration-specific context            │
│  6. Related errors                          │
├─────────────────────────────────────────────┤
│  Section 1: Root cause                      │
│  • HubSpot API returns `value` field        │
│  • Salesforce API expects `label` field     │
│  • Middleware (native connector, Zapier,    │
│    custom) may or may not translate         │
│  • Native connector: partial translation    │
│    (known bug, Salesforce side)             │
├─────────────────────────────────────────────┤
│  Section 2: Detection                       │
│  • Query both APIs for same record          │
│  • Compare picklist values side by side     │
│  • Look for blank fields post-sync          │
│  • Check audit logs for field write skips   │
│  • Automated detection script (Python)      │
├─────────────────────────────────────────────┤
│  Section 3: Fix — Custom mapping table      │
│                                             │
│  ┌──────────────────────────────────────┐   │
│  │ HubSpot Value    │ Salesforce Label  │   │
│  │──────────────────┼───────────────────│   │
│  │ new              │ New              │   │
│  │ qualified        │ Qualified        │   │
│  │ contacted        │ Contacted        │   │
│  │ customer         │ Closed Won       │   │
│  │ closed_lost      │ Closed Lost      │   │
│  │ junk             │ Junk             │   │
│  │ ──────────────── │ ──────────────── │   │
│  │ NOT MAPPED:      │                  │   │
│  │ unqualified      │ → N/A (create)  │   │
│  │ attempt          │ → N/A (create)  │   │
│  └──────────────────────────────────────┘   │
│                                               │
│  Code: Middleware translation function        │
│  (Python + curl examples)                    │
├─────────────────────────────────────────────┤
│  Section 4: Prevention                      │
│  • Test sync with a single record first     │
│  • Add monitoring on blank-field writes      │
│  • Use webhook to validate sync payload      │
│  • Weekly audit script (cron)               │
├─────────────────────────────────────────────┤
│  Section 5: Integration context             │
│  • Native HubSpot-Salesforce connector vs   │
│    custom API sync: tradeoffs               │
│  • Zapier: uses custom field mapping UI     │
│  • Make: requires manual label mapping      │
│  • Custom: you control the translation      │
│  • HubSpot rebuilding sync engine (v2)      │
│    → beta Q4 2026, may fix this             │
├─────────────────────────────────────────────┤
│  Section 6: Related errors                  │
│  • [HubSpot-Salesforce: Deal Stage Mismatch]
│    /integrations/hubspot-salesforce/errors/ │
│    deal-stage-mismatch                      │
│  • [HubSpot-Salesforce: Record Owner Sync   │
│    Loop] /integrations/hubspot-salesforce/  │
│    errors/owner-sync-loop                   │
│  • [HubSpot-Salesforce: Duplicate Detection │
│    Mismatch] /integrations/hubspot-         │
│    salesforce/errors/duplicate-mismatch     │
│                                               │
│  Community:                                   │
│  "Lost 2,000 leads to blank picklist fields. │
│   No error, no alert. We found it 3 months   │
│   later." — api_integration_dev,             │
│   GitHub Discussions, May 2026               │
├─────────────────────────────────────────────┤
│  SEO Footer                                  │
│  Common questions:                           │
│  • Does native HubSpot-Salesforce connector  │
│    handle picklist translation?              │
│  • Can I use Salesforce formula fields to    │
│    fix value/label mismatch?                 │
│  • How do I detect silent field mapping      │
│    failures?                                 │
│  Internal links to:                          │
│  - All HubSpot-Salesforce integration pages  │
│  - HubSpot picklist field API docs           │
│  - Salesforce picklist field API docs        │
└─────────────────────────────────────────────┘
```

## Component Dependencies
- `Breadcrumb.astro`
- `MetadataBar.astro` (severity badge, error type badge, date)
- `StickyTOC.astro`
- `FieldMappingTable.astro` — renders mapping tables from data
- `CodeTabs.astro`
- `DetectionScriptBlock.astro` — scrollable block for detection scripts
- `RelatedErrors.astro`
- `CommunityQuote.astro`
- `SEOFooter.astro`

## Unique Features
- **Silent Failure Warning Banner** — top of page, yellow background, icon. Triggers when `errorType: "silent-failure"`. Text: "⚠ This error produces no HTTP error code. Your data may be wrong right now."
- **Mapping Table** — renders the critical field mapping from structured data. Sortable by hubspot-value, salesforce-label, maps-to columns.
- **Detection Script** — inline Python script snippet that queries both APIs and diffs the picklist values. Copy-paste ready.

## Data Dependencies
- `src/data/tools/{toolA}.json` and `{toolB}.json`
- `src/data/integrations/{integration}.json`
- `src/data/field-mappings/{integration}.json` — the mapping table data

## Variant Considerations
- **Silent failures**: Warning banner prominent. Emphasize detection (you can't Google what you don't know exists).
- **Auth errors across integration**: Emphasize token lifecycle, which tool's token is expiring.
- **Data format errors**: Emphasize transformation layer. Currency, date, phone format normalization.
- **Rate limit cascading**: Cross-tool rate limit interactions (one tool's slow response times out the other).

## Performance Targets
- Same as ErrorCodeLayout
- Mapping tables use static rendering (no JS sort unless > 30 rows)
- Warning banner is inline HTML/CSS, no component JS