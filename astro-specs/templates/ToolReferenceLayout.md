# ToolReferenceLayout — Astro Template Spec

## Route
`/[tool-slug]`

## Example URLs
- `/hubspot` — "HubSpot API Integration Guide: Errors, Auth, Rate Limits"
- `/salesforce` — "Salesforce API Integration Guide: Errors, Auth, Rate Limits"
- `/pipedrive` — "Pipedrive v2 API Migration: Complete Developer Guide"

## Page Purpose
Topical hub for each tool. Aggregates all error pages, integration pages, and reference data for one tool. This is the "second click" page — visitor arrives at an error page, then navigates here for the full tool reference.

## Frontmatter Schema

```yaml
---
layout: ../../layouts/ToolReferenceLayout.astro
title: "HubSpot API Integration Guide: Error Codes, Auth, Rate Limits & Best Practices"
description: "Complete HubSpot API integration reference. All error codes with fixes, OAuth 2.0 setup, rate limit strategy, and connector guides for Salesforce, Mailchimp, Pipedrive, and more."
tool: "hubspot"
toolDisplayName: "HubSpot"
apiVersion: "2026-03 (date-versioned)"
baseUrl: "https://api.hubapi.com"
authType: "OAuth 2.0 (private app access tokens also supported)"
rateLimitSummary: "110 req/10s per account (public OAuth apps)"
lastUpdated: "2026-06-26"
keywords:
  - "hubspot api integration guide"
  - "hubspot api error codes"
  - "hubspot api authentication"
  - "hubspot api rate limits 2026"
  - "hubspot api reference"
integrationCount: 5
errorCount: 9
---
```

## Page Template Structure

```
┌─────────────────────────────────────────────┐
│  Breadcrumb                                  │
│  HubSpot > API Integration Guide            │
├─────────────────────────────────────────────┤
│  H1: HubSpot API Integration Guide           │
│                                               │
│  Metadata bar:                                │
│  API: 2026-03  |  🔐 OAuth 2.0              │
│  🚦 110 req/10s  |  📅 Jun 26, 2026         │
│  📊 9 errors  |  🔗 5 integrations           │
├─────────────────────────────────────────────┤
│  Quick stats cards (3-column grid)           │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐ │
│  │ ⚠ Errors │ │ 🔐 Auth  │ │ 🔄 Integrate │ │
│  │ 9 codes  │ │ OAuth 2.0│ │ 5 connectors │ │
│  │ 4 high   │ │ + private│ │ + integration│ │
│  │ severity │ │ app token│ │   guides     │ │
│  └──────────┘ └──────────┘ └──────────────┘ │
├─────────────────────────────────────────────┤
│  Table of Contents (sticky)                  │
│  1. Authentication                           │
│  2. Rate Limits                              │
│  3. API Reference (base URL, headers, pag.) │
│  4. Error Code Reference                    │
│  5. Integration Guides                      │
│  6. Best Practices                          │
│  7. 2026 Changes & Migration               │
├─────────────────────────────────────────────┤
│  Section 1: Authentication                  │
│  • OAuth 2.0 flow (auth code grant)         │
│    - Step-by-step with curl                 │
│    - Token refresh (configurable 1-6h)      │
│  • Private app access tokens                │
│    - Create in UI, no OAuth needed          │
│    - Limited to one account                 │
│  • API key auth (legacy, deprecated)        │
│  ▶ [Full OAuth guide](/hubspot/auth/oauth)  │
├─────────────────────────────────────────────┤
│  Section 2: Rate Limits                     │
│  • Public OAuth apps: 110 req/10s           │
│  • Private apps: different limits           │
│  • Retry strategy (link to 429 page)        │
│  • 2026 header changes                      │
│  • Batch API: 200 objects per call          │
│  ▶ [Full rate limit guide](/hubspot/errors/429)
├─────────────────────────────────────────────┤
│  Section 3: API Reference                   │
│  • Base URL: https://api.hubapi.com         │
│  • Headers: Authorization: Bearer {token}   │
│  • Pagination: offset-based (limit=100)     │
│  • Object IDs vs CRM IDs                    │
│  • Search API: POST /crm/v3/objects/        │
│    {object}/search                          │
├─────────────────────────────────────────────┤
│  Section 4: Error Code Reference            │
│  Error code table:                          │
│  ┌────────────┬──────────┬────────────────┐ │
│  │ Code       │ Severity │ Quick Fix      │ │
│  ├────────────┼──────────┼────────────────┤ │
│  │ 400        │ Medium   │ Check request  │ │
│  │            │          │ body format    │ │
│  │ 401        │ High     │ Refresh OAuth  │ │
│  │            │          │ token          │ │
│  │ 429        │ High     │ Exponential    │ │
│  │            │          │ backoff       │ │
│  │ 500        │ Critical │ Check HubSpot  │ │
│  │            │          │ status page    │ │
│  │ ... 6 more │          │                │ │
│  └────────────┴──────────┴────────────────┘ │
│  Full links to each error page.              │
├─────────────────────────────────────────────┤
│  Section 5: Integration Guides              │
│  Integration cards (2-column grid):         │
│  ┌────────────────────┬────────────────────┐│
│  │ HubSpot ↔ Salesforce│ HubSpot ↔ Mailchimp││
│  │ • Field mapping bug │ • Unidirectional  ││
│  │ • Value vs Label   │ • Unsubscribe sync ││
│  │ • Deal stage sync  │ • Custom webhook   ││
│  │ ⬇ 2 errors found  │ ⬇ 2 errors found  ││
│  ├────────────────────┼────────────────────┤│
│  │ HubSpot ↔ Pipdrv   │ HubSpot ↔ ActvCmpgn││
│  │ • Currency mism.  │ • ContactTag bug  ││
│  │ • Deal mapping    │ • Custom field     ││
│  │ ⬇ 2 errors found  │ ⬇ 2 errors found  ││
│  ├────────────────────┴────────────────────┤│
│  │ HubSpot ↔ Zapier                        ││
│  │ • Trigger timing                       ││
│  │ • Field passthrough                    ││
│  │ ⬇ 2 errors found                      ││
│  └─────────────────────────────────────────┘│
├─────────────────────────────────────────────┤
│  Section 6: Best Practices                  │
│  • Batch API calls where possible           │
│  • Register webhooks (not polling)          │
│  • Use associations API for CRM links       │
│  • Handle rate limits with queue            │
│  • Test in sandbox first                   │
│  • Monitor with Operations Hub              │
├─────────────────────────────────────────────┤
│  Section 7: 2026 Changes                   │
│  • March 2026 date-versioned API launch     │
│  • Rate limit header format changed         │
│  • OAuth token TTL configurable             │
│  • Salesforce sync engine v2 announced      │
│  • Legacy API sunset timeline               │
│  ▶ [Full changelog](/hubspot/changelog)    │
├─────────────────────────────────────────────┤
│  SEO Footer                                  │
│  • "Browse all 9 HubSpot API errors"        │
│  • "Browse all HubSpot integrations"       │
│  • "Related tools: Salesforce, Pipedrive,   │
│    Mailchimp, ActiveCampaign, Zapier, Make, │
│    Zoho CRM, Slack, Calendly"               │
│  • PAA-style: "Which HubSpot API version    │
│    should I use in 2026?"                   │
└─────────────────────────────────────────────┘
```

## Component Dependencies
- `Breadcrumb.astro`
- `MetadataBar.astro`
- `StatCards.astro` (3-column grid: errors, auth, integrations)
- `StickyTOC.astro`
- `ErrorCodeTable.astro` — renders error table from data, links to each error page
- `IntegrationCardGrid.astro` — renders 2-column card grid, links to each integration
- `SEOFoooter.astro`

## Data Dependencies
- `src/data/tools/{tool}.json` — tool metadata, all error codes, all integration references
- `src/data/errors/{tool}/*.json` — all error files for aggregation
- `src/data/integrations/*.json` — integration pair data filtered by matching tool

## Variant Considerations
- **Established tools (HubSpot, Salesforce)**: Emphasize migration/versioning. 2026 changes section is critical.
- **Newer tools (Pipedrive v2)**: Emphasize migration from v1. Deadline urgency.
- **Middleware tools (Zapier, Make)**: Emphasize trigger/action errors, field passthrough, rate limit delegation.
- **Communication tools (Slack)**: Emphasize webhook format, event subscriptions, workspace-level rate limits.
- **Scheduling tools (Calendly)**: Emphasize webhook verification, event types, availability conflicts.

## Performance Targets
- Error code table: static render (no JS). Max 20 rows, server-rendered.
- Integration cards: lazy-load images (tool logos) with blur placeholder.
- Stat cards: pure CSS grid, no JS.