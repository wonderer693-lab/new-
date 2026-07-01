# Hybrid Vibe Coder Content Optimization — Design Spec

**Date:** 2026-07-01
**Status:** Approved
**Scope:** All 97 content pages (74 error + 24 integration + 1 migration)

---

## Problem Statement

The API Integration Hub currently scores **5/10** for its target audience. Content is written exclusively for experienced developers (Python code, API internals, technical jargon). The actual audience is a hybrid of two vibe coder types:

1. **Experienced vibe coders** — use agentic coding tools (Cursor, Claude Code) with solid coding experience. They want code fixes and understand API internals.
2. **Non-coding vibe coders** — use AI models (ChatGPT, Claude) purely by prompting. They want copy-paste fixes, plain English explanations, and no-code alternatives.

The current content serves Type 1 well but completely ignores Type 2.

## Solution: Progressive Disclosure (Layered Approach)

Keep all existing technical content intact. Add 4 new sections **above** the existing content on every page, ordered from simplest to most technical. Non-coders get their fix in the first viewport without scrolling. Developers scroll past to the technical depth they need.

### Audience Segments

| Segment | Tools They Use | What They Want |
|---|---|---|
| Non-coding vibe coder | ChatGPT, Claude (prompting only) | Copy-paste fix, plain English, AI prompts |
| No-code automation user | Zapier, Make, n8n, Power Automate | Visual workflow steps, no code |
| Experienced vibe coder | Cursor, Claude Code, Copilot | Code fixes, root cause analysis, detection |

---

## Page Structure

### Error Pages (74 pages)

```
## Quick Fix (TL;DR)                    ← NEW [No Code badge]
## Fix This With AI                     ← NEW [No Code badge]
## No-Code Fix                          ← NEW [Low Code badge]
## If You See This Error                ← NEW [No Code badge]
--- existing content below ---
## What Causes This Error               [Developer badge]
## Step-by-Step Fix (Code)             [Developer badge]
## How to Detect                        [Developer badge]
## Prevention                           [Developer badge]
## People Also Ask
## Official Documentation
## Related Errors
```

### Integration Pages (24 pages)

```
## Quick Fix (TL;DR)                    ← NEW [No Code badge]
## Fix This With AI                     ← NEW [No Code badge]
## No-Code Workaround                   ← NEW [Low Code badge]
## If You See This Error                ← NEW [No Code badge]
--- existing content below ---
## The Problem                          [Developer badge]
## Root Cause                           [Developer badge]
## How to Detect                        [Developer badge]
## Step-by-Step Fix (Code)             [Developer badge]
## Prevention                           [Developer badge]
## Integration-Specific Context
## People Also Ask
## Official Documentation
## Related Errors
```

### Audience Badges

Each section heading gets a colored badge:

| Badge | CSS Class | Color | Meaning |
|---|---|---|---|
| `No Code` | `.audience-badge--no-code` | Green (#d1fae5 / #065f46) | Non-coders / prompt-only |
| `Low Code` | `.audience-badge--low-code` | Blue (#dbeafe / #1e40af) | No-code platform users |
| `Developer` | `.audience-badge--developer` | Purple (#ede9fe / #5b21b6) | Experienced coders |

---

## New Content Sections — Detailed Spec

### 1. Quick Fix (TL;DR)

**Audience:** Non-coding vibe coders
**Badge:** `No Code`
**CSS wrapper:** `.quick-fix`

**Format:**
```markdown
<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** [One plain-English sentence]

**The fix:**
1. [Step 1 — actionable without reading the rest]
2. [Step 2]
3. [Step 3]

**Copy-paste this code** (if you're using a code editor):
```python
# [Minimal working fix — 5-10 lines max, self-contained]
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>
```

**Rules:**
- Max 5 steps, max 10 lines of code
- Every step must be actionable without reading the rest of the page
- Code block must be self-contained (imports included, no placeholders)
- Written at 8th-grade reading level
- Must include a plain-English problem statement

### 2. Fix This With AI

**Audience:** Prompt-only vibe coders
**Badge:** `No Code`
**CSS wrapper:** `.ai-prompt`

**Format:**
```markdown
<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm getting a [error name] error from [tool] API.
> The error message is: "[exact error message]"
> I'm using [context: Zapier/Make/custom code/etc.]
> Please give me a step-by-step fix with working code.

**What to expect:** The AI should give you [brief description].

**If it doesn't work**, add this follow-up:
> The fix didn't work. I'm still getting the same error. Here's what I tried: [paste your code]. Please debug this.

**Best AI tools for this:** [ChatGPT-4 / Claude / Cursor — brief note on which works best]

</div>
```

**Rules:**
- Prompt must be self-contained (includes error context)
- Include a follow-up prompt for when the first attempt fails
- Mention which AI tools work best for this type of error
- Prompt must reference the specific error code and tool name

### 3. No-Code Fix

**Audience:** No-code automation platform users
**Badge:** `Low Code`

**Format:**
```markdown
## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to handle this error in popular automation tools:

### Zapier
[2-3 steps to configure error handling]

### Make (Integromat)
[2-3 steps to configure error handling]

### n8n
[2-3 steps to configure error handling]

### Power Automate
[2-3 steps to configure error handling]

**Which tool should you use?** [One sentence recommendation]
```

**Rules:**
- Each platform gets 2-3 steps max
- Describe what to click and what to type (UI navigation)
- If a platform can't handle this specific error, say "Not applicable" with a reason
- Only include platforms that have native integrations with the relevant tool(s)

### 4. If You See This Error

**Audience:** Non-coders trying to identify their problem
**Badge:** `No Code`
**CSS wrapper:** `.error-match`

**Format:**
```markdown
<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"exact error message from API response"`
- `"another variation of the same error"`
- `"error message from a different tool that means the same thing"`

**What it means in plain English:** [One sentence, no jargon]

**Most common cause:** [One sentence]

</div>
```

**Rules:**
- List 2-4 actual error message variations (from real API responses)
- Plain English translation — no technical jargon
- One-sentence most common cause

---

## CSS Components

### New additions to `src/styles/global.css`

```css
/* Audience Badges */
.audience-badge {
  display: inline-block;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  vertical-align: middle;
  margin-left: 0.5rem;
}
.audience-badge--no-code { background: #d1fae5; color: #065f46; }
.audience-badge--low-code { background: #dbeafe; color: #1e40af; }
.audience-badge--developer { background: #ede9fe; color: #5b21b6; }

/* Quick Fix Box */
.quick-fix {
  background: #f0fdf4;
  border: 2px solid #86efac;
  border-radius: 0.75rem;
  padding: 1.25rem 1.5rem;
  margin-bottom: 2rem;
}

/* AI Prompt Box */
.ai-prompt {
  background: #fefce8;
  border: 2px solid #fde047;
  border-radius: 0.75rem;
  padding: 1.25rem 1.5rem;
  margin-bottom: 2rem;
}
.ai-prompt blockquote {
  border-left: 3px solid #eab308;
  padding-left: 1rem;
  font-family: ui-monospace, 'SF Mono', 'Fira Code', monospace;
  font-size: 0.9rem;
  background: #fffbeb;
  padding: 0.75rem;
  border-radius: 0.25rem;
  margin: 0.5rem 0;
}

/* Error Match Box */
.error-match {
  background: #fef2f2;
  border: 2px solid #fca5a5;
  border-radius: 0.75rem;
  padding: 1.25rem 1.5rem;
  margin-bottom: 2rem;
}
.error-match code {
  background: #fee2e2;
  padding: 0.15rem 0.4rem;
  border-radius: 0.25rem;
  font-size: 0.85rem;
}

/* Dark Mode Variants */
@media (prefers-color-scheme: dark) {
  .audience-badge--no-code { background: #064e3b; color: #6ee7b7; }
  .audience-badge--low-code { background: #1e3a5f; color: #93c5fd; }
  .audience-badge--developer { background: #3b0764; color: #c4b5fd; }

  .quick-fix { background: #052e16; border-color: #166534; }
  .ai-prompt { background: #422006; border-color: #854d0e; }
  .ai-prompt blockquote { background: #451a03; border-left-color: #ca8a04; }
  .error-match { background: #450a0a; border-color: #991b1b; }
  .error-match code { background: #7f1d1d; }
}
```

### No layout file changes needed

The new sections are rendered from markdown body content. `ErrorCodeLayout.astro` and `IntegrationErrorLayout.astro` already pass body content through via `<Content />`.

---

## Schema & Structured Data

### `src/content.config.ts` — No changes required

All new sections are body markdown. No new frontmatter fields needed.

### Structured Data — Automatic enhancement

- **HowTo JSON-LD:** The `extractSteps()` utility will automatically pick up numbered steps from the "Quick Fix" section.
- **FAQPage JSON-LD:** Add an AI-related Q&A to the existing "People Also Ask" section on each page so `extractFaq()` captures it.

---

## Implementation Phases

### Phase 1: CSS Foundation (1 file)
- Add all new CSS components to `src/styles/global.css`
- Audience badges, quick-fix box, AI prompt box, error-match box
- Dark mode variants for all components

### Phase 2: Template Pages (2 files)
- Create all 4 new sections on `src/content/hubspot/errors-429.md` (error page reference)
- Create all 4 new sections on `src/content/make/int-make-to-slack-make-slack-module-oauth-re-authentication.md` (integration page reference)
- Build and validate both render correctly

### Phase 3: Error Page Rollout (74 files)
Apply 4 new sections to all error pages, grouped by tool:
1. HubSpot (9 pages)
2. Salesforce (11 pages)
3. Mailchimp (4 pages)
4. Slack (8 pages)
5. ActiveCampaign (7 pages)
6. Calendly (6 pages)
7. Zapier (4 pages)
8. Make (7 pages)
9. Zoho (7 pages)
10. Pipedrive (11 pages)

Each page gets unique, error-specific content — not boilerplate.

### Phase 4: Integration Page Rollout (24 files)
Apply 4 new sections to all integration pages with tool-pair-specific content.

### Phase 5: Verification
- Build site: `npx astro build` — confirm all 97 pages pass schema validation
- Spot-check 5 error pages + 3 integration pages for content quality
- Verify dark mode rendering on all new CSS components

---

## Content Generation Rules

Each page's new sections are generated based on:
- The error's frontmatter: `errorCode`, `errorName`, `httpStatus`, `category`, `severity`, `tool`
- The existing body content: "What Causes," "Step-by-Step Fix," "How to Detect"
- Tool-specific API documentation patterns

**No boilerplate.** Every Quick Fix, AI prompt, no-code step, and error message example must be specific to that error and tool.

## Estimated Output

- **74 error pages** × 4 new sections = 296 new content sections
- **24 integration pages** × 4 new sections = 96 new content sections
- **1 CSS update** with ~80 new lines
- **Total new content:** ~15,000-20,000 words across the site

---

## Success Criteria

After implementation, the content rating for vibe coders should improve from **5/10 to 8/10**:

| Criterion | Before | After |
|---|---|---|
| Non-coders can find a fix in < 30 seconds | No | Yes (Quick Fix section) |
| Prompt-only users have ready-to-copy AI prompts | No | Yes (Fix With AI section) |
| No-code platform users have step-by-step guides | No | Yes (No-Code Fix section) |
| Non-coders can identify their error visually | No | Yes (If You See This Error) |
| Developers still get full technical depth | Yes | Yes (existing content preserved) |
| SEO: All new content is indexable | N/A | Yes (no hidden/tabbed content) |
