# ErrorCodeLayout — Astro Template Spec

## Route
`/[tool-slug]/errors/[error-code]`

## Example URLs
- `/hubspot/errors/429` — "HubSpot API 429 Rate Limit Error"
- `/salesforce/errors/INVALID_SESSION_ID` — "Salesforce INVALID_SESSION_ID Error"
- `/pipedrive/errors/401` — "Pipedrive v2 401 Authentication Error"

## Page Purpose
One error code, one page. Highest-intent traffic (developer with error in hand, pasting into Google).

## Frontmatter Schema (Astro content collection)

```yaml
---
layout: ../../layouts/ErrorCodeLayout.astro
title: "HubSpot API 429 Too Many Requests — Causes, Fix, Retry Strategy"
description: "How to fix HubSpot API 429 rate limit errors. Production retry logic with exponential backoff, batch queuing, and 2026 rate limit header changes."
tool: "hubspot"
errorCode: "429"
errorName: "Too Many Requests"
httpStatus: 429
category: "rate-limit"
severity: "high"
priority: 1
lastUpdated: "2026-06-26"
keywords:
  - "hubspot api 429 error fix"
  - "hubspot rate limit retry"
  - "hubspot 429 production retry logic"
  - "hubspot api rate limit 2026"
  - "hubspot public app rate limit 110 per 10 seconds"
---
```

## Page Template Structure

```
┌─────────────────────────────────────────────┐
│  Breadcrumb                                  │
│  Tool > Errors > 429 Too Many Requests      │
├─────────────────────────────────────────────┤
│  H1: HubSpot API 429 Too Many Requests       │
│                                               │
│  Metadata bar:                                │
│  ⚠ Severity: High  |  🔄 HTTP 429           │
│  📅 Updated: Jun 26, 2026                    │
├─────────────────────────────────────────────┤
│  Quick Fix (collapsible)                      │
│  ▶ "I just need the fix"                     │
│  Backoff: 1s → 2s → 4s → 8s                 │
│  Header: Retry-After: {seconds}             │
│  Max 5 retries, then dead-letter queue.      │
├─────────────────────────────────────────────┤
│  Table of Contents (sticky)                  │
│  1. What causes this error                   │
│  2. Step-by-step fix                        │
│  3. Production retry strategy               │
│  4. 2026-specific changes                   │
│  5. Code examples (curl, JS, Python)        │
│  6. Prevention                              │
│  7. Related errors                          │
├─────────────────────────────────────────────┤
│  Section 1: What causes this error           │
│  • Brief explanation (2-3 sentences)         │
│  • Link to official HubSpot docs             │
│  • Common scenarios:                         │
│    - Bulk import jobs > 100 req/10s         │
│    - Webhook bursts without queuing         │
│    - OAuth refresh token storms             │
├─────────────────────────────────────────────┤
│  Section 2: Step-by-step fix                │
│  Step 1: Check Retry-After header           │
│  Step 2: Wait duration {n}s                 │
│  Step 3: Retry request                      │
│  Step 4: If 5+ failures → log to queue      │
│  (each step has curl/Python snippet)         │
├─────────────────────────────────────────────┤
│  Section 3: Production retry strategy       │
│  Code block with:                            │
│  - Exponential backoff function             │
│  - Jitter: random(0, 1000)ms                │
│  - Queue with batch drain every 2s          │
│  - Rate limit keyed by API key/app          │
├─────────────────────────────────────────────┤
│  Section 4: 2026 changes                    │
│  • March 2026 — date-versioned API          │
│  • Public apps: 110 req/10s per account     │
│  • OAuth token: configurable 1-6h           │
│  • New rate limit header format             │
│  • Private apps: different limits           │
├─────────────────────────────────────────────┤
│  Section 5: Code examples                   │
│  Tab bar: [curl] [Python] [JavaScript]      │
│  Each tab shows retry logic snippet.        │
├─────────────────────────────────────────────┤
│  Section 6: Prevention                      │
│  • Batch API calls                          │
│  • Use webhook payload signing              │
│  • Monitor with Usage dashboard             │
│  • Set up alert in Operations Hub           │
├─────────────────────────────────────────────┤
│  Section 7: Related errors                  │
│  • [HubSpot 500 Internal](/hubspot/errors/500)
│  • [HubSpot 401 Unauthorized](/hubspot/errors/401)
│  • [HubSpot 504 Gateway Timeout](/hubspot/errors/504)
│                                               │
│  Community-sourced note:                     │
│  "I hit 429 even at 80 req/10s. Found       │
│  that concurrent Lambda invocations were    │
│  sharing the same API key." — u/apidev      │
│  Source: r/HubSpot_Developers, Apr 2026     │
├─────────────────────────────────────────────┤
│  SEO Footer                                  │
│  Common questions (from PAA data):          │
│  • Why does HubSpot 429 not include         │
│    Retry-After sometimes?                   │
│  • Does 429 apply per key or per app?       │
│  • Can I request a rate limit increase?     │
│  Internal links to all HubSpot errors       │
│  Internal links to HubSpot integrations     │
└─────────────────────────────────────────────┘
```

## Component Dependencies
- `Breadcrumb.astro`
- `MetadataBar.astro` (severity badge, status code, date)
- `QuickFixCollapsible.astro`
- `StickyTOC.astro`
- `CodeTabs.astro` (curl / Python / JS)
- `RelatedErrors.astro`
- `CommunityQuote.astro`
- `SEOFooter.astro` (PAA block + internal links)

## Data Dependencies
- `src/data/tools/{tool}.json` — tool metadata
- `src/data/errors/{errorCode}.json` — error data from processed JSON

## Variant Considerations
- **4xx errors**: Emphasize fix steps (actionable). Include "Common mistakes" section.
- **5xx errors**: Emphasize escalation path. Include "Is this HubSpot's fault?" section.
- **Auth errors**: Emphasize token refresh, credential rotation, OAuth flow diagram.
- **Rate limit errors**: Emphasize retry strategy, backoff code, queue architecture.

## Performance Targets
- Critical CSS inlined (first paint < 1.5s)
- Code syntax highlighting via Shiki (SSR, no JS runtime)
- PAA accordion uses `<details>` element (no JS)
- Community quote lazy-loaded
