# Hybrid Vibe Coder Content Optimization — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add 4 new audience-layered sections (Quick Fix, AI Prompt, No-Code Fix, Visual Error Matching) to all 97 content pages, plus supporting CSS, so non-coding vibe coders get instant fixes while developers keep full technical depth.

**Architecture:** Progressive Disclosure pattern — new sections stacked above existing content in markdown body. CSS-only styling (audience badges, colored boxes, dark mode). No JS, no layout changes, no schema changes. Existing `extractSteps()` and `extractFaq()` utilities automatically pick up new content for JSON-LD.

**Tech Stack:** Astro 5, Markdown, CSS custom properties, static site generation

**Spec:** `docs/superpowers/specs/2026-07-01-hybrid-vibe-coder-content-optimization-design.md`

---

## File Structure

| Action | File | Responsibility |
|--------|------|----------------|
| Modify | `src/styles/global.css` | Add audience badges, colored section boxes, dark mode variants |
| Modify | `src/content/hubspot/errors-429.md` | Error page reference template (4 new sections) |
| Modify | `src/content/make/int-make-to-slack-make-slack-module-oauth-re-authentication.md` | Integration page reference template (4 new sections) |
| Modify | `src/content/hubspot/errors-*.md` (8 files) | HubSpot error rollout |
| Modify | `src/content/salesforce/errors-*.md` (10 files) | Salesforce error rollout |
| Modify | `src/content/mailchimp/errors-*.md` (4 files) | Mailchimp error rollout |
| Modify | `src/content/slack/errors-*.md` (7 files) | Slack error rollout |
| Modify | `src/content/activecampaign/errors-*.md` (7 files) | ActiveCampaign error rollout |
| Modify | `src/content/calendly/errors-*.md` (6 files) | Calendly error rollout |
| Modify | `src/content/zapier/errors-*.md` (4 files) | Zapier error rollout |
| Modify | `src/content/make/errors-*.md` (7 files) | Make error rollout |
| Modify | `src/content/zoho/errors-*.md` (7 files) | Zoho error rollout |
| Modify | `src/content/pipedrive/errors-*.md` (11 files) | Pipedrive error rollout |
| Modify | `src/content/*/int-*.md` (23 files) | Integration page rollout |

---

## Content Templates

### Error Page Template (insert after frontmatter, before existing content)

```markdown
<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** {PLAIN_ENGLISH_PROBLEM}

**The fix:**
1. {STEP_1}
2. {STEP_2}
3. {STEP_3}

**Copy-paste this code** (if you're using a code editor):
```python
{MINIMAL_CODE_FIX}
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm getting a {ERROR_NAME} error from {TOOL} API.
> The error message is: "{EXACT_ERROR_MESSAGE}"
> I'm using {CONTEXT}.
> Please give me a step-by-step fix with working code.

**What to expect:** {EXPECTED_AI_OUTPUT}

**If it doesn't work**, add this follow-up:
> The fix didn't work. I'm still getting the same error. Here's what I tried: [paste your code]. Please debug this.

**Best AI tools for this:** {BEST_AI_TOOLS}

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to handle this error in popular automation tools:

### Zapier
{ZAPIER_STEPS}

### Make (Integromat)
{MAKE_STEPS}

### n8n
{N8N_STEPS}

### Power Automate
{POWER_AUTOMATE_STEPS}

**Which tool should you use?** {TOOL_RECOMMENDATION}

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"{ERROR_MESSAGE_1}"`
- `"{ERROR_MESSAGE_2}"`
- `"{ERROR_MESSAGE_3}"`

**What it means in plain English:** {PLAIN_ENGLISH_MEANING}

**Most common cause:** {MOST_COMMON_CAUSE}

</div>
```

### Integration Page Template (insert after frontmatter, before existing content)

Same structure as error page template, but:
- "No-Code Fix" becomes "No-Code Workaround"
- AI prompt references both tools in the integration pair
- Error messages include symptoms from both sides of the integration

---

## Task 1: CSS Foundation

**Files:**
- Modify: `src/styles/global.css:407` (append after last line)

- [ ] **Step 1: Add audience badges and section box styles**

Append the following CSS to the end of `src/styles/global.css` (after line 407):

```css
/* === Hybrid Vibe Coder Sections === */

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

.quick-fix {
  background: #f0fdf4;
  border: 2px solid #86efac;
  border-radius: 0.75rem;
  padding: 1.25rem 1.5rem;
  margin-bottom: 2rem;
}
.quick-fix h2 { margin-top: 0; }

.ai-prompt {
  background: #fefce8;
  border: 2px solid #fde047;
  border-radius: 0.75rem;
  padding: 1.25rem 1.5rem;
  margin-bottom: 2rem;
}
.ai-prompt h2 { margin-top: 0; }
.ai-prompt blockquote {
  border-left: 3px solid #eab308;
  padding-left: 1rem;
  font-family: var(--font-mono);
  font-size: 0.9rem;
  background: #fffbeb;
  padding: 0.75rem;
  border-radius: 0.25rem;
  margin: 0.5rem 0;
}

.error-match {
  background: #fef2f2;
  border: 2px solid #fca5a5;
  border-radius: 0.75rem;
  padding: 1.25rem 1.5rem;
  margin-bottom: 2rem;
}
.error-match h2 { margin-top: 0; }
.error-match code {
  background: #fee2e2;
  padding: 0.15rem 0.4rem;
  border-radius: 0.25rem;
  font-size: 0.85rem;
}
```

- [ ] **Step 2: Add dark mode variants**

Append the following inside the existing `@media (prefers-color-scheme: dark)` block (after line 406, before the closing `}`):

```css
  .audience-badge--no-code { background: #064e3b; color: #6ee7b7; }
  .audience-badge--low-code { background: #1e3a5f; color: #93c5fd; }
  .audience-badge--developer { background: #3b0764; color: #c4b5fd; }
  .quick-fix { background: #052e16; border-color: #166534; }
  .ai-prompt { background: #422006; border-color: #854d0e; }
  .ai-prompt blockquote { background: #451a03; border-left-color: #ca8a04; }
  .error-match { background: #450a0a; border-color: #991b1b; }
  .error-match code { background: #7f1d1d; }
```

- [ ] **Step 3: Build to verify CSS compiles**

Run: `npx astro build`
Expected: Build succeeds with no CSS errors.

- [ ] **Step 4: Commit**

```bash
git add src/styles/global.css
git commit -m "feat: add hybrid vibe coder CSS components (badges, quick-fix, ai-prompt, error-match)"
```

---

## Task 2: Error Page Reference Template — HubSpot 429

**Files:**
- Modify: `src/content/hubspot/errors-429.md`

- [ ] **Step 1: Insert 4 new sections after the urgency banner (line 26) and before "## What Causes" (line 28)**

Insert the following content between the closing `</div>` of the urgency banner (line 26) and the `## What Causes HubSpot 429` heading (line 28):

```markdown

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** You're sending too many requests to HubSpot's API too fast, and HubSpot is temporarily blocking you.

**The fix:**
1. Wait for the number of seconds shown in the `Retry-After` header (usually 10 seconds)
2. Slow down your requests — don't send more than 11 per second
3. If you're doing a bulk import, split it into smaller batches

**Copy-paste this code** (if you're using a code editor):
```python
import time, requests

resp = requests.get(url, headers=headers)
if resp.status_code == 429:
    wait = int(resp.headers.get("Retry-After", 10))
    time.sleep(wait)
    resp = requests.get(url, headers=headers)
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code tool](#no-code-fix).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> I'm getting a 429 Too Many Requests error from the HubSpot API.
> The error message is: "You have reached your ten second limit"
> I'm using a custom integration that makes API calls to HubSpot.
> Please give me a step-by-step fix with working Python code that handles rate limiting.

**What to expect:** The AI should give you a retry function with exponential backoff and explain HubSpot's rate limits.

**If it doesn't work**, add this follow-up:
> The fix didn't work. I'm still getting 429 errors. Here's what I tried: [paste your code]. Please debug this.

**Best AI tools for this:** Claude (best at explaining rate limit strategies), ChatGPT-4 (good code generation), Cursor (if you want inline code fixes)

</div>

## No-Code Fix <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to write code? Here's how to handle HubSpot rate limits in popular automation tools:

### Zapier
1. Open your Zap → click the HubSpot action step
2. Enable "Auto-retry on error" in the step settings (Zapier auto-retries 429 errors up to 3 times)
3. If you're hitting limits frequently, add a "Delay by Zapier" step before the HubSpot action (set to 10 seconds)

### Make (Integromat)
1. Open your scenario → right-click the HubSpot module → "Add error handler"
2. Choose "Retry" → set interval to 10 seconds, max retries to 3
3. For bulk operations, add a "Sleep" module (10 seconds) between HubSpot calls

### n8n
1. Open your workflow → click the HubSpot node
2. In "Settings" → enable "Retry on Fail" → set "Wait Between Tries" to 10000ms, "Max Tries" to 3
3. For bulk operations, add a "Wait" node (10 seconds) between HubSpot nodes

### Power Automate
1. Open your flow → click the HubSpot action
2. In "Settings" → enable "Retry Policy" → set to "Exponential interval" with count 3
3. For bulk operations, add a "Delay" action (10 seconds) before the HubSpot action

**Which tool should you use?** Zapier has the best built-in retry for HubSpot — it handles 429 errors automatically without any configuration.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these messages:

- `"You have reached your ten second limit"`
- `"429 Too Many Requests"`
- `"Rate limit exceeded. Please retry after X seconds"`
- `"HTTP 429"` in your integration logs

**What it means in plain English:** HubSpot is telling you to slow down. You're making too many API calls in a short time. Wait a few seconds and try again.

**Most common cause:** Bulk imports or sync jobs that fire too many requests at once without pausing between them.

</div>
```

- [ ] **Step 2: Build to verify the page renders**

Run: `npx astro build`
Expected: Build succeeds. The HubSpot 429 page renders with the 4 new sections above the existing content.

- [ ] **Step 3: Commit**

```bash
git add src/content/hubspot/errors-429.md
git commit -m "feat: add hybrid vibe coder sections to HubSpot 429 (reference template)"
```

---

## Task 3: Integration Page Reference Template — Make-Slack OAuth

**Files:**
- Modify: `src/content/make/int-make-to-slack-make-slack-module-oauth-re-authentication.md`

- [ ] **Step 1: Insert 4 new sections after the urgency banner (line 29) and before "## The Problem" (line 31)**

Insert the following content between the closing `</div>` of the urgency banner (line 29) and the `## The Problem` heading (line 31):

```markdown

<div class="quick-fix">

## Quick Fix (TL;DR) <span class="audience-badge audience-badge--no-code">No Code</span>

**The problem:** Your Make scenario stopped sending messages to Slack because the connection expired or was revoked. Make paused the scenario silently — no one got notified.

**The fix:**
1. Go to Make dashboard → Connections → Slack → click your connection
2. Click "Re-authorize" and complete the Slack login
3. Go back to your scenario → click "Run once" to test
4. Add an error handler so you get notified next time (see below)

**Copy-paste this code** (if you're using a code editor):
```python
import requests

# Test your Slack bot token is working
resp = requests.post("https://slack.com/api/auth.test",
    headers={"Authorization": "Bearer YOUR_BOT_TOKEN"})
print(resp.json())  # Should show {"ok": true}
```

**Still stuck?** Try the [AI prompt below](#fix-this-with-ai) or use a [no-code workaround](#no-code-workaround).

</div>

<div class="ai-prompt">

## Fix This With AI <span class="audience-badge audience-badge--no-code">No Code</span>

Copy this prompt and paste it into ChatGPT, Claude, or your AI coding assistant:

> My Make (Integromat) scenario that posts to Slack has stopped working.
> The error message is: "Connection Error" on the Slack module.
> The scenario shows as "paused" in Make dashboard.
> Please give me step-by-step instructions to fix this and prevent it from happening again.

**What to expect:** The AI should walk you through re-authorizing the Slack connection in Make and setting up an error handler for alerts.

**If it doesn't work**, add this follow-up:
> I re-authorized but the scenario still shows "Connection Error." The test connection button says "invalid_auth." What should I do?

**Best AI tools for this:** ChatGPT-4 (good at Make/Slack UI navigation), Claude (good at explaining OAuth token lifecycle)

</div>

## No-Code Workaround <span class="audience-badge audience-badge--low-code">Low Code</span>

Don't want to debug this? Here's how to handle Slack connection failures in other automation tools:

### Zapier
1. Create a new Zap → trigger: "New Deal in HubSpot" (or your source app)
2. Action: "Send Channel Message in Slack" → connect your Slack workspace
3. Zapier auto-retries on connection errors and sends you an email alert — no silent failures

### Make (Integromat) — Fix the existing scenario
1. Open the scenario → right-click the Slack module → "Add error handler"
2. Choose "Email" module → configure to send alert to your team when connection fails
3. Set the scenario to "Auto-resume" after error handler runs

### n8n
1. Create a new workflow → Slack node → "Send Message"
2. In the Slack node settings → enable "Retry on Fail" → 3 retries, 30s between
3. Add an "IF" node after Slack → if error, send alert via email or another Slack channel

### Power Automate
1. Create a new flow → trigger from your source app
2. Add "Post message in a chat or channel" (Slack connector)
3. In the Slack action settings → enable "Retry Policy" → exponential interval, 3 retries

**Which tool should you use?** Zapier is the easiest — it auto-retries Slack connection errors and emails you when something breaks, so failures are never silent.

<div class="error-match">

## If You See This Error <span class="audience-badge audience-badge--no-code">No Code</span>

You might be dealing with this issue if you see any of these:

- `"Connection Error"` on a Slack module in Make dashboard
- `"invalid_auth"` when testing the Slack connection
- Your Make scenario shows as `"paused"` with no messages being sent to Slack
- Slack notifications from your automation suddenly stopped without any error email

**What it means in plain English:** The "bridge" between Make and Slack broke. Make can't talk to Slack anymore, so it paused everything. You need to reconnect them.

**Most common cause:** The Slack bot token was revoked (someone clicked "Revoke" in Slack settings) or Make's internal token refresh failed.

</div>
```

- [ ] **Step 2: Build to verify the page renders**

Run: `npx astro build`
Expected: Build succeeds. The Make-Slack integration page renders with the 4 new sections.

- [ ] **Step 3: Commit**

```bash
git add src/content/make/int-make-to-slack-make-slack-module-oauth-re-authentication.md
git commit -m "feat: add hybrid vibe coder sections to Make-Slack OAuth (integration reference template)"
```

---

## Task 4: HubSpot Error Rollout (8 remaining files)

**Files:**
- Modify: `src/content/hubspot/errors-207-multi-status.md`
- Modify: `src/content/hubspot/errors-400.md`
- Modify: `src/content/hubspot/errors-401.md`
- Modify: `src/content/hubspot/errors-403.md`
- Modify: `src/content/hubspot/errors-404.md`
- Modify: `src/content/hubspot/errors-409.md`
- Modify: `src/content/hubspot/errors-414.md`
- Modify: `src/content/hubspot/errors-423.md`

- [ ] **Step 1: Add 4 sections to each HubSpot error page**

For each file listed above, insert the 4 new sections (using the Error Page Template from the top of this plan) immediately after the frontmatter closing `---` and before the first existing `##` heading.

**Customization per file:**

| File | Quick Fix Problem | Error Messages | No-Code Focus |
|------|-------------------|----------------|---------------|
| `errors-207-multi-status.md` | Some records in your bulk update succeeded but others failed silently | `"207 Multi-Status"`, `"partial success"`, `"some records failed"` | Zapier batch error handling |
| `errors-400.md` | HubSpot rejected your request because the data format is wrong | `"400 Bad Request"`, `"Invalid input"`, `"Property value is not valid"` | Make data validation module |
| `errors-401.md` | Your HubSpot API key or OAuth token is expired or wrong | `"401 Unauthorized"`, `"Invalid API key"`, `"authentication failed"` | Zapier/Make re-auth flow |
| `errors-403.md` | Your API key doesn't have permission to access this HubSpot resource | `"403 Forbidden"`, `"Missing scopes"`, `"insufficient permissions"` | Check app scopes in Zapier/Make |
| `errors-404.md` | The HubSpot record you're looking for doesn't exist (deleted or wrong ID) | `"404 Not Found"`, `"Object not found"`, `"record does not exist"` | Add lookup step before action |
| `errors-409.md` | You're trying to create a HubSpot record that already exists | `"409 Conflict"`, `"Contact already exists"`, `"duplicate email"` | Add "find or create" logic in Zapier/Make |
| `errors-414.md` | Your HubSpot API request URL is too long (too many parameters) | `"414 URI Too Long"`, `"Request-URI Too Large"` | Split into smaller batches |
| `errors-423.md` | A HubSpot record is locked because another process is editing it | `"423 Locked"`, `"Resource is locked"`, `"concurrent modification"` | Add delay and retry |

For each file:
1. Read the existing content to understand the specific error
2. Write the 4 sections following the Error Page Template
3. Fill in all `{PLACEHOLDERS}` with error-specific content
4. The Quick Fix code block should be the simplest possible fix (3-5 lines)
5. The AI prompt should reference the specific error code and HubSpot context
6. The No-Code Fix should give 2-3 steps per platform relevant to that error type
7. The Error Match section should list 2-4 real error message variations

- [ ] **Step 2: Build to verify all HubSpot pages render**

Run: `npx astro build`
Expected: Build succeeds. All 9 HubSpot error pages render with the new sections.

- [ ] **Step 3: Commit**

```bash
git add src/content/hubspot/errors-*.md
git commit -m "feat: add hybrid vibe coder sections to all HubSpot error pages"
```

---

## Task 5: Salesforce Error Rollout (10 files)

**Files:**
- Modify: `src/content/salesforce/errors-400.md`
- Modify: `src/content/salesforce/errors-401.md`
- Modify: `src/content/salesforce/errors-403.md`
- Modify: `src/content/salesforce/errors-404.md`
- Modify: `src/content/salesforce/errors-409.md`
- Modify: `src/content/salesforce/errors-414.md`
- Modify: `src/content/salesforce/errors-420.md`
- Modify: `src/content/salesforce/errors-428.md`
- Modify: `src/content/salesforce/errors-429.md`
- Modify: `src/content/salesforce/errors-503.md`
- Modify: `src/content/salesforce/errors-INVALID_SESSION_ID.md`

- [ ] **Step 1: Add 4 sections to each Salesforce error page**

Same process as Task 4. Insert the 4 new sections after frontmatter, before existing content.

**Customization per file:**

| File | Quick Fix Problem | Error Messages | No-Code Focus |
|------|-------------------|----------------|---------------|
| `errors-400.md` | Salesforce rejected your data format (wrong field type or missing required field) | `"400 Bad Request"`, `"INVALID_FIELD"`, `"MALFORMED_QUERY"` | Validate data in Make/Zapier before sending |
| `errors-401.md` | Your Salesforce session or OAuth token expired | `"401 Unauthorized"`, `"INVALID_SESSION_ID"`, `"Session expired"` | Re-auth in Zapier/Make dashboard |
| `errors-403.md` | Your Salesforce user doesn't have permission for this operation | `"403 Forbidden"`, `"INSUFFICIENT_ACCESS"`, `"API_DISABLED_FOR_ORG"` | Check profile permissions, API enabled |
| `errors-404.md` | The Salesforce record doesn't exist (wrong ID or deleted) | `"404 Not Found"`, `"NOT_FOUND"`, `"The requested resource does not exist"` | Add lookup step before action |
| `errors-409.md` | You're trying to create a record that conflicts with an existing one | `"409 Conflict"`, `"DUPLICATE_VALUE"`, `"duplicate id"` | Add "find or create" logic |
| `errors-414.md` | Your SOQL query or API URL is too long | `"414 URI Too Long"`, `"Request-URI Too Large"` | Use POST with body instead of GET |
| `errors-420.md` | Salesforce is throttling your API calls (enhanced rate limiting) | `"420 Enhance Your Calm"`, `"Concurrent API request limit"` | Add delays between calls |
| `errors-428.md` | Salesforce requires a precondition before this request | `"428 Precondition Required"`, `"Precondition failed"` | Add required headers/conditions |
| `errors-429.md` | Too many API calls to Salesforce in a short period | `"429 Too Many Requests"`, `"REQUEST_LIMIT_EXCEEDED"` | Enable auto-retry in Zapier/Make |
| `errors-503.md` | Salesforce is temporarily unavailable (maintenance or overload) | `"503 Service Unavailable"`, `"SERVER_UNAVAILABLE"`, `"maintenance"` | Wait and retry |
| `errors-INVALID_SESSION_ID.md` | Your Salesforce session token is no longer valid | `"INVALID_SESSION_ID"`, `"Session expired or invalid"` | Refresh OAuth token |

- [ ] **Step 2: Build to verify**

Run: `npx astro build`
Expected: Build succeeds.

- [ ] **Step 3: Commit**

```bash
git add src/content/salesforce/errors-*.md
git commit -m "feat: add hybrid vibe coder sections to all Salesforce error pages"
```

---

## Task 6: Mailchimp Error Rollout (4 files)

**Files:**
- Modify: `src/content/mailchimp/errors-400.md`
- Modify: `src/content/mailchimp/errors-403.md`
- Modify: `src/content/mailchimp/errors-404.md`
- Modify: `src/content/mailchimp/errors-429.md`

- [ ] **Step 1: Add 4 sections to each Mailchimp error page**

| File | Quick Fix Problem | Error Messages | No-Code Focus |
|------|-------------------|----------------|---------------|
| `errors-400.md` | Mailchimp rejected your data (invalid email format, missing fields) | `"400 Bad Request"`, `"Invalid Resource"`, `"email address is invalid"` | Validate emails before adding |
| `errors-403.md` | Your API key doesn't have permission for this Mailchimp action | `"403 Forbidden"`, `"API key not authorized"`, `"action not allowed"` | Check API key permissions |
| `errors-404.md` | The Mailchimp list, campaign, or subscriber doesn't exist | `"404 Not Found"`, `"Resource Not Found"`, `"list not found"` | Verify list ID before action |
| `errors-429.md` | Too many requests to Mailchimp API | `"429 Too Many Requests"`, `"rate limit exceeded"`, `"too many requests"` | Enable auto-retry, add delays |

- [ ] **Step 2: Build to verify**

Run: `npx astro build`
Expected: Build succeeds.

- [ ] **Step 3: Commit**

```bash
git add src/content/mailchimp/errors-*.md
git commit -m "feat: add hybrid vibe coder sections to all Mailchimp error pages"
```

---

## Task 7: Slack Error Rollout (7 files)

**Files:**
- Modify: `src/content/slack/errors-account-inactive.md`
- Modify: `src/content/slack/errors-invalid-auth.md`
- Modify: `src/content/slack/errors-is-archived.md`
- Modify: `src/content/slack/errors-not-in-channel.md`
- Modify: `src/content/slack/errors-rate-limited.md`
- Modify: `src/content/slack/errors-token-revoked.md`
- Modify: `src/content/slack/errors-too-many-requests.md`
- Modify: `src/content/slack/errors-user-is-bot.md`

- [ ] **Step 1: Add 4 sections to each Slack error page**

**Important:** Slack errors use `httpStatus: 0` (errors in JSON body, not HTTP status). Error messages are in the format `{"ok":false,"error":"error_name"}`. Adjust the Error Match section accordingly.

| File | Quick Fix Problem | Error Messages | No-Code Focus |
|------|-------------------|----------------|---------------|
| `errors-account-inactive.md` | The Slack account you're trying to use is deactivated | `"account_inactive"`, `"user_not_found"` | Check user status in Slack admin |
| `errors-invalid-auth.md` | Your Slack bot token or user token is wrong | `"invalid_auth"`, `"not_authed"`, `"{"ok":false}"` | Re-auth in Zapier/Make |
| `errors-is-archived.md` | The Slack channel is archived — you can't post to it | `"is_archived"`, `"channel_not_found"` | Unarchive or use different channel |
| `errors-not-in-channel.md` | Your Slack bot isn't invited to the channel | `"not_in_channel"`, `"channel_not_found"` | Invite bot to channel |
| `errors-rate-limited.md` | Slack is throttling your API calls | `"rate_limited"`, `"{"ok":false,"error":"rate_limited"}"` | Add delays, enable retry |
| `errors-token-revoked.md` | Someone revoked your Slack bot token | `"token_revoked"`, `"account_inactive"` | Generate new token, re-auth |
| `errors-too-many-requests.md` | Too many Slack API calls in a burst | `"too_many_requests"`, `"ratelimited"` | Space out requests |
| `errors-user-is-bot.md` | You're trying to perform an action that bots can't do | `"user_is_bot"`, `"not_allowed"` | Use user token instead of bot token |

- [ ] **Step 2: Build to verify**

Run: `npx astro build`
Expected: Build succeeds.

- [ ] **Step 3: Commit**

```bash
git add src/content/slack/errors-*.md
git commit -m "feat: add hybrid vibe coder sections to all Slack error pages"
```

---

## Task 8: ActiveCampaign Error Rollout (7 files)

**Files:**
- Modify: `src/content/activecampaign/errors-401.md`
- Modify: `src/content/activecampaign/errors-402.md`
- Modify: `src/content/activecampaign/errors-403.md`
- Modify: `src/content/activecampaign/errors-404.md`
- Modify: `src/content/activecampaign/errors-422.md`
- Modify: `src/content/activecampaign/errors-429.md`
- Modify: `src/content/activecampaign/errors-contacttag-400.md`

- [ ] **Step 1: Add 4 sections to each ActiveCampaign error page**

| File | Quick Fix Problem | Error Messages | No-Code Focus |
|------|-------------------|----------------|---------------|
| `errors-401.md` | Your ActiveCampaign API key is wrong or expired | `"401 Unauthorized"`, `"API key invalid"` | Re-auth in Zapier/Make |
| `errors-402.md` | Your ActiveCampaign plan doesn't allow this API feature | `"402 Payment Required"`, `"upgrade required"` | Check plan limits |
| `errors-403.md` | Your API key doesn't have permission for this action | `"403 Forbidden"`, `"access denied"` | Check API key permissions |
| `errors-404.md` | The contact, list, or automation doesn't exist | `"404 Not Found"`, `"resource not found"` | Verify IDs before action |
| `errors-422.md` | ActiveCampaign rejected your data format | `"422 Unprocessable Entity"`, `"validation failed"` | Validate data before sending |
| `errors-429.md` | Too many API calls to ActiveCampaign | `"429 Too Many Requests"`, `"rate limit"` | Enable retry, add delays |
| `errors-contacttag-400.md` | The ContactTag API call has a format bug (wrapper object issue) | `"400 Bad Request"`, `"contactTag wrapper"` | Fix payload structure |

- [ ] **Step 2: Build to verify**

Run: `npx astro build`
Expected: Build succeeds.

- [ ] **Step 3: Commit**

```bash
git add src/content/activecampaign/errors-*.md
git commit -m "feat: add hybrid vibe coder sections to all ActiveCampaign error pages"
```

---

## Task 9: Calendly Error Rollout (6 files)

**Files:**
- Modify: `src/content/calendly/errors-401.md`
- Modify: `src/content/calendly/errors-403.md`
- Modify: `src/content/calendly/errors-404.md`
- Modify: `src/content/calendly/errors-409.md`
- Modify: `src/content/calendly/errors-422.md`
- Modify: `src/content/calendly/errors-429.md`

- [ ] **Step 1: Add 4 sections to each Calendly error page**

| File | Quick Fix Problem | Error Messages | No-Code Focus |
|------|-------------------|----------------|---------------|
| `errors-401.md` | Your Calendly access token is expired or invalid | `"401 Unauthorized"`, `"invalid token"` | Re-auth in Zapier/Make |
| `errors-403.md` | Your token doesn't have permission for this Calendly action | `"403 Forbidden"`, `"forbidden"` | Check OAuth scopes |
| `errors-404.md` | The Calendly event type or user doesn't exist | `"404 Not Found"`, `"resource not found"` | Verify event type URI |
| `errors-409.md` | The time slot is already booked | `"409 Conflict"`, `"already booked"` | Add availability check before booking |
| `errors-422.md` | Calendly rejected your booking data format | `"422 Unprocessable Entity"`, `"validation error"` | Validate invitee data |
| `errors-429.md` | Too many API calls to Calendly | `"429 Too Many Requests"`, `"rate limit"` | Enable retry, add delays |

- [ ] **Step 2: Build to verify**

Run: `npx astro build`
Expected: Build succeeds.

- [ ] **Step 3: Commit**

```bash
git add src/content/calendly/errors-*.md
git commit -m "feat: add hybrid vibe coder sections to all Calendly error pages"
```

---

## Task 10: Zapier Error Rollout (4 files)

**Files:**
- Modify: `src/content/zapier/errors-400.md`
- Modify: `src/content/zapier/errors-401.md`
- Modify: `src/content/zapier/errors-429.md`
- Modify: `src/content/zapier/errors-500.md`

- [ ] **Step 1: Add 4 sections to each Zapier error page**

**Note:** For Zapier error pages, the "No-Code Fix" section should focus on Zapier's own UI (task history, error logs, re-auth) since Zapier IS the no-code tool. For n8n/Power Automate alternatives, suggest equivalent features.

| File | Quick Fix Problem | Error Messages | No-Code Focus |
|------|-------------------|----------------|---------------|
| `errors-400.md` | Zapier rejected your Zap configuration (invalid data) | `"400 Bad Request"`, `"invalid configuration"` | Fix Zap step settings |
| `errors-401.md` | A connected app's authentication expired in Zapier | `"401 Unauthorized"`, `"authentication failed"` | Reconnect app in Zapier |
| `errors-429.md` | Zapier is rate limiting your API calls | `"429 Too Many Requests"`, `"rate limit"` | Slow down Zap trigger frequency |
| `errors-500.md` | Zapier's server had an internal error processing your Zap | `"500 Internal Server Error"`, `"server error"` | Retry the Zap, check task history |

- [ ] **Step 2: Build to verify**

Run: `npx astro build`
Expected: Build succeeds.

- [ ] **Step 3: Commit**

```bash
git add src/content/zapier/errors-*.md
git commit -m "feat: add hybrid vibe coder sections to all Zapier error pages"
```

---

## Task 11: Make Error Rollout (7 files)

**Files:**
- Modify: `src/content/make/errors-400.md`
- Modify: `src/content/make/errors-401.md`
- Modify: `src/content/make/errors-403.md`
- Modify: `src/content/make/errors-404.md`
- Modify: `src/content/make/errors-413.md`
- Modify: `src/content/make/errors-429.md`
- Modify: `src/content/make/errors-500.md`

- [ ] **Step 1: Add 4 sections to each Make error page**

**Note:** For Make error pages, the "No-Code Fix" section should focus on Make's own UI (scenario settings, error handlers, module configuration). For Zapier/n8n/Power Automate, suggest equivalent features.

| File | Quick Fix Problem | Error Messages | No-Code Focus |
|------|-------------------|----------------|---------------|
| `errors-400.md` | Make rejected your scenario configuration | `"400 Bad Request"`, `"invalid data"` | Fix module settings |
| `errors-401.md` | Your Make API key or a connected app's auth expired | `"401 Unauthorized"`, `"invalid token"` | Re-auth connection |
| `errors-403.md` | Your Make account doesn't have permission for this action | `"403 Forbidden"`, `"access denied"` | Check plan/permissions |
| `errors-404.md` | The Make scenario or module resource doesn't exist | `"404 Not Found"`, `"not found"` | Verify scenario/module IDs |
| `errors-413.md` | Your data payload is too large for Make to process | `"413 Payload Too Large"`, `"data size exceeded"` | Split data into smaller chunks |
| `errors-429.md` | Make is rate limiting your API calls | `"429 Too Many Requests"`, `"rate limit"` | Reduce scenario frequency |
| `errors-500.md` | Make's server had an internal error | `"500 Internal Server Error"`, `"server error"` | Retry scenario, check status page |

- [ ] **Step 2: Build to verify**

Run: `npx astro build`
Expected: Build succeeds.

- [ ] **Step 3: Commit**

```bash
git add src/content/make/errors-*.md
git commit -m "feat: add hybrid vibe coder sections to all Make error pages"
```

---

## Task 12: Zoho Error Rollout (7 files)

**Files:**
- Modify: `src/content/zoho/errors-access-denied-oauth-throttle-.md`
- Modify: `src/content/zoho/errors-duplicate-data.md`
- Modify: `src/content/zoho/errors-invalid-oauthtoken.md`
- Modify: `src/content/zoho/errors-limit-exceeded.md`
- Modify: `src/content/zoho/errors-mandatory-not-found.md`
- Modify: `src/content/zoho/errors-too-many-concurrent-requests.md`
- Modify: `src/content/zoho/errors-too-many-requests.md`

- [ ] **Step 1: Add 4 sections to each Zoho error page**

| File | Quick Fix Problem | Error Messages | No-Code Focus |
|------|-------------------|----------------|---------------|
| `errors-access-denied-oauth-throttle-.md` | Zoho blocked your request due to OAuth throttling | `"ACCESS_DENIED"`, `"OAuth throttle"`, `"Too many requests"` | Add delays between auth calls |
| `errors-duplicate-data.md` | You're trying to create a Zoho record that already exists | `"DUPLICATE_DATA"`, `"record already exists"` | Add "find or create" logic |
| `errors-invalid-oauthtoken.md` | Your Zoho OAuth token expired or is invalid | `"INVALID_OAUTHTOKEN"`, `"token expired"` | Refresh OAuth token |
| `errors-limit-exceeded.md` | You've exceeded Zoho's API credit limit | `"LIMIT_EXCEEDED"`, `"API credit limit"` | Check plan limits, reduce calls |
| `errors-mandatory-not-found.md` | A required field is missing from your Zoho API request | `"MANDATORY_NOT_FOUND"`, `"required field missing"` | Add required fields to payload |
| `errors-too-many-concurrent-requests.md` | Too many simultaneous API calls to Zoho | `"TOO_MANY_CONCURRENT_REQUESTS"`, `"concurrent limit"` | Serialize requests, add delays |
| `errors-too-many-requests.md` | Too many total API calls to Zoho | `"TOO_MANY_REQUESTS"`, `"rate limit"` | Enable retry, reduce frequency |

- [ ] **Step 2: Build to verify**

Run: `npx astro build`
Expected: Build succeeds.

- [ ] **Step 3: Commit**

```bash
git add src/content/zoho/errors-*.md
git commit -m "feat: add hybrid vibe coder sections to all Zoho error pages"
```

---

## Task 13: Pipedrive Error Rollout (11 files)

**Files:**
- Modify: `src/content/pipedrive/errors-400.md`
- Modify: `src/content/pipedrive/errors-401.md`
- Modify: `src/content/pipedrive/errors-402.md`
- Modify: `src/content/pipedrive/errors-403.md`
- Modify: `src/content/pipedrive/errors-404.md`
- Modify: `src/content/pipedrive/errors-410.md`
- Modify: `src/content/pipedrive/errors-415.md`
- Modify: `src/content/pipedrive/errors-422.md`
- Modify: `src/content/pipedrive/errors-429.md`
- Modify: `src/content/pipedrive/errors-500.md`
- Modify: `src/content/pipedrive/errors-503.md`

- [ ] **Step 1: Add 4 sections to each Pipedrive error page**

| File | Quick Fix Problem | Error Messages | No-Code Focus |
|------|-------------------|----------------|---------------|
| `errors-400.md` | Pipedrive rejected your data format | `"400 Bad Request"`, `"invalid data"` | Validate data before sending |
| `errors-401.md` | Your Pipedrive API token is wrong or expired | `"401 Unauthorized"`, `"invalid token"` | Re-auth, regenerate token |
| `errors-402.md` | Your Pipedrive plan doesn't allow this API feature | `"402 Payment Required"`, `"upgrade required"` | Check plan limits |
| `errors-403.md` | Your API token doesn't have permission | `"403 Forbidden"`, `"access denied"` | Check token permissions |
| `errors-404.md` | The deal, person, or organization doesn't exist | `"404 Not Found"`, `"record not found"` | Verify IDs before action |
| `errors-410.md` | The Pipedrive API endpoint has been removed (v1→v2 migration) | `"410 Gone"`, `"endpoint deprecated"` | Migrate to v2 endpoints |
| `errors-415.md` | Pipedrive doesn't accept your request content type | `"415 Unsupported Media Type"`, `"content-type"` | Set Content-Type header |
| `errors-422.md` | Pipedrive rejected your data validation | `"422 Unprocessable Entity"`, `"validation error"` | Fix field values |
| `errors-429.md` | Too many API calls to Pipedrive | `"429 Too Many Requests"`, `"rate limit"` | Enable retry, use v2 endpoints |
| `errors-500.md` | Pipedrive's server had an internal error | `"500 Internal Server Error"`, `"server error"` | Retry, check status page |
| `errors-503.md` | Pipedrive is temporarily unavailable | `"503 Service Unavailable"`, `"maintenance"` | Wait and retry |

- [ ] **Step 2: Build to verify**

Run: `npx astro build`
Expected: Build succeeds.

- [ ] **Step 3: Commit**

```bash
git add src/content/pipedrive/errors-*.md
git commit -m "feat: add hybrid vibe coder sections to all Pipedrive error pages"
```

---

## Task 14: Integration Page Rollout (23 remaining files)

**Files (23 integration pages):**
- `src/content/activecampaign/int-activecampaign-to-slack-activecampaign-api-rate-limit-on-webhook-responses.md`
- `src/content/activecampaign/int-activecampaign-to-slack-activecampaign-webhook-payload-format.md`
- `src/content/activecampaign/int-salesforce-to-activecampaign-contacttag-wrapper-bug.md`
- `src/content/activecampaign/int-salesforce-to-activecampaign-custom-field-type-mismatch.md`
- `src/content/calendly/int-zapier-to-calendly-calendly-api-rate-limit-on-webhook-subscriptions.md`
- `src/content/calendly/int-zapier-to-calendly-calendly-webhook-delivery-delays.md`
- `src/content/calendly/int-zapier-to-calendly-calendly-webhook-verification-header-missing.md`
- `src/content/mailchimp/int-pipedrive-to-mailchimp-mailchimp-daily-list-add-limit.md`
- `src/content/mailchimp/int-salesforce-to-mailchimp-custom-field-type-mismatch.md`
- `src/content/mailchimp/int-salesforce-to-mailchimp-mailchimp-unsubscribes-re-synced.md`
- `src/content/make/int-make-to-slack-block-kit-too-complex-for-make's-json-module.md`
- `src/content/pipedrive/int-pipedrive-to-mailchimp-pipedrive-person-email-not-required.md`
- `src/content/pipedrive/int-pipedrive-to-mailchimp-pipedrive-v2-hash-key-field-ids-in-custom-data.md`
- `src/content/salesforce/int-salesforce-to-activecampaign-salesforce-daily-api-limit-exhausted-by-ac-sync.md`
- `src/content/salesforce/int-salesforce-to-mailchimp-email-field-mismatch.md`
- `src/content/slack/int-activecampaign-to-slack-slack-1-req-sec-vs-activecampaign-webhook-burst.md`
- `src/content/slack/int-hubspot-to-slack-bot-not-in-channel.md`
- `src/content/slack/int-hubspot-to-slack-message-formatting-issues.md`
- `src/content/slack/int-hubspot-to-slack-slack-rate-limit-(1-per-second-per-method).md`
- `src/content/slack/int-make-to-slack-slack-rate-limit-in-make-scenarios.md`
- `src/content/zoho/int-zoho-to-mailchimp-zoho-api-rate-limit-(250-req-min).md`
- `src/content/zoho/int-zoho-to-mailchimp-zoho-contact-duplicate-detection-differs-from-mailchimp.md`
- `src/content/zoho/int-zoho-to-mailchimp-zoho-oauth-token-expires-every-hour.md`

- [ ] **Step 1: Add 4 sections to each integration page**

For each file, insert the 4 new sections (using the Integration Page Template) after the frontmatter closing `---` and before the first existing `##` heading (or after the urgency banner if present).

**Key differences from error pages:**
- "No-Code Fix" heading becomes "No-Code Workaround"
- AI prompt references BOTH tools in the integration pair (e.g., "I'm integrating Salesforce with Mailchimp and getting...")
- Error messages include symptoms from both sides (e.g., "Salesforce shows success but Mailchimp never receives the data")
- No-Code workarounds focus on the specific integration pair (e.g., "Use Zapier's native Salesforce-to-Mailchimp Zap instead of custom code")

**Customization per file:**

| File | Quick Fix Problem | No-Code Focus |
|------|-------------------|---------------|
| `int-activecampaign-to-slack-...rate-limit...` | ActiveCampaign webhooks overwhelm Slack's rate limit | Add delay module in Make between AC and Slack |
| `int-activecampaign-to-slack-...payload-format` | ActiveCampaign webhook data format doesn't match what Slack expects | Add JSON parser module in Make |
| `int-salesforce-to-activecampaign-contacttag...` | ContactTag API wrapper bug causes 400 errors | Fix payload structure in Zapier/Make |
| `int-salesforce-to-activecampaign-custom-field...` | Field types don't match between Salesforce and ActiveCampaign | Map fields correctly in Zapier/Make |
| `int-zapier-to-calendly-...rate-limit...` | Calendly webhooks exceed Zapier's processing rate | Add delay between webhook triggers |
| `int-zapier-to-calendly-...delivery-delays` | Calendly webhook events arrive late in Zapier | Add timeout/retry in Zapier |
| `int-zapier-to-calendly-...verification-header` | Calendly webhook verification fails in Zapier | Configure webhook secret correctly |
| `int-pipedrive-to-mailchimp-...daily-list-add-limit` | Mailchimp daily list add limit hit by Pipedrive sync | Batch contacts, spread across days |
| `int-salesforce-to-mailchimp-custom-field...` | Field type mismatch between Salesforce and Mailchimp | Map fields in Zapier/Make |
| `int-salesforce-to-mailchimp-...unsubscribes-re-synced` | Mailchimp unsubscribes get re-added by Salesforce sync | Add suppression list check |
| `int-make-to-slack-block-kit...` | Block Kit JSON too complex for Make's JSON module | Simplify Block Kit structure |
| `int-pipedrive-to-mailchimp-...email-not-required` | Pipedrive person without email causes Mailchimp error | Add email validation step |
| `int-pipedrive-to-mailchimp-...v2-hash-key...` | Pipedrive v2 custom data uses hash keys instead of field names | Map hash keys to field names |
| `int-salesforce-to-activecampaign-...daily-api-limit...` | ActiveCampaign sync exhausts Salesforce daily API limit | Reduce sync frequency, batch requests |
| `int-salesforce-to-mailchimp-email-field...` | Email field format mismatch between Salesforce and Mailchimp | Transform email field in Zapier/Make |
| `int-activecampaign-to-slack-...1-req-sec...` | ActiveCampaign webhook burst exceeds Slack's 1 req/sec | Add rate limiter/delay module |
| `int-hubspot-to-slack-bot-not-in-channel` | HubSpot-Slack bot not invited to target channel | Invite bot to channel |
| `int-hubspot-to-slack-message-formatting` | HubSpot data doesn't format correctly in Slack messages | Fix message template |
| `int-hubspot-to-slack-...rate-limit...` | HubSpot-Slack integration hits Slack's rate limit | Add delay between messages |
| `int-make-to-slack-...rate-limit...` | Make scenarios hit Slack rate limits | Add sleep module between Slack calls |
| `int-zoho-to-mailchimp-...rate-limit...` | Zoho API rate limit (250 req/min) hit during Mailchimp sync | Batch requests, add delays |
| `int-zoho-to-mailchimp-...duplicate-detection...` | Zoho and Mailchimp detect duplicates differently | Normalize email/fields before sync |
| `int-zoho-to-mailchimp-...oauth-token...` | Zoho OAuth token expires every hour, breaking Mailchimp sync | Auto-refresh token before expiry |

- [ ] **Step 2: Build to verify all integration pages render**

Run: `npx astro build`
Expected: Build succeeds. All 24 integration pages render with the new sections.

- [ ] **Step 3: Commit**

```bash
git add src/content/*/int-*.md
git commit -m "feat: add hybrid vibe coder sections to all integration pages"
```

---

## Task 15: Final Verification

- [ ] **Step 1: Full build**

Run: `npx astro build`
Expected: Build succeeds with 146+ pages generated, zero errors.

- [ ] **Step 2: Spot-check 5 error pages**

Verify these pages have all 4 new sections rendering correctly:
1. `src/content/hubspot/errors-429.md` (reference template)
2. `src/content/salesforce/errors-401.md` (authentication error)
3. `src/content/slack/errors-rate-limited.md` (rate limit, non-HTTP error)
4. `src/content/pipedrive/errors-429.md` (rate limit)
5. `src/content/zoho/errors-invalid-oauthtoken.md` (OAuth error)

Check each page for:
- Quick Fix box with green border renders
- AI Prompt box with yellow border renders
- No-Code Fix section with all 4 platform subsections
- Error Match box with red border renders
- Audience badges display with correct colors
- Existing technical content still renders below new sections

- [ ] **Step 3: Spot-check 3 integration pages**

Verify these pages have all 4 new sections:
1. `src/content/make/int-make-to-slack-make-slack-module-oauth-re-authentication.md` (reference template)
2. `src/content/slack/int-hubspot-to-slack-bot-not-in-channel.md` (permission error)
3. `src/content/zoho/int-zoho-to-mailchimp-zoho-oauth-token-expires-every-hour.md` (OAuth issue)

- [ ] **Step 4: Verify dark mode**

Check that all new CSS components render correctly in dark mode:
- Audience badges have dark-mode color variants
- Quick Fix box has dark green background
- AI Prompt box has dark yellow background
- Error Match box has dark red background
- Blockquotes inside AI Prompt box have dark styling

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "feat: complete hybrid vibe coder content optimization — all 97 pages updated"
```

---

## Content Quality Checklist (apply to every page)

When writing the 4 new sections for each page, verify:

- [ ] Quick Fix: Problem statement is one plain-English sentence (8th-grade reading level)
- [ ] Quick Fix: Code block is self-contained (includes imports, no placeholders)
- [ ] Quick Fix: Max 5 steps, max 10 lines of code
- [ ] AI Prompt: Prompt includes specific error code, tool name, and error message
- [ ] AI Prompt: Follow-up prompt is included
- [ ] AI Prompt: Best AI tools are mentioned
- [ ] No-Code Fix: All 4 platforms have 2-3 steps each (or "Not applicable" with reason)
- [ ] No-Code Fix: Steps describe what to click/type (UI navigation)
- [ ] No-Code Fix: Tool recommendation sentence is included
- [ ] Error Match: 2-4 real error message variations listed
- [ ] Error Match: Plain English meaning (no jargon)
- [ ] Error Match: One-sentence most common cause
