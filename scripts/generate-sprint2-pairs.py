"""
Sprint 2 Integration Pair Generator — creates 8 new integration pair data files
and 8 field mapping files, then generates 22 error pages.

New pairs:
1. salesforce-to-mailchimp    2. salesforce-to-activecampaign
3. hubspot-to-slack           4. pipedrive-to-mailchimp
5. zoho-to-mailchimp          6. zapier-to-calendly
7. make-to-slack              8. activecampaign-to-slack
"""

import json
import os
import sys

DATA_DIR = "data/processed"
INT_DIR = os.path.join(DATA_DIR, "integrations")
FM_DIR = "data/field-mappings"
CONTENT_DIR = "src/content"

os.makedirs(INT_DIR, exist_ok=True)
os.makedirs(FM_DIR, exist_ok=True)

def to_slug(name):
    return name.lower().replace(" ", "-").replace("/", "-").replace("_", "-")

def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  + {path}")

# ─── Tool definitions for cross-references ───
TOOLS = {
    "hubspot": {
        "name": "HubSpot",
        "auth": "OAuth 2.0 or Private App Token",
        "base": "https://api.hubapi.com",
        "rate": "110 req/10s per account (public OAuth apps)"
    },
    "salesforce": {
        "name": "Salesforce",
        "auth": "OAuth 2.0 JWT Bearer or Web Server flow",
        "base": "https://yourdomain.my.salesforce.com/services/data/v66.0",
        "rate": "API calls per org license type (15K–500K+ daily)"
    },
    "mailchimp": {
        "name": "Mailchimp",
        "auth": "OAuth 2.0 or API Key (Basic Auth)",
        "base": "https://usX.api.mailchimp.com/3.0",
        "rate": "10 req/sec per API key (burst > 10 returns 429)"
    },
    "activecampaign": {
        "name": "ActiveCampaign",
        "auth": "API Token (Api-Key header)",
        "base": "https://{account}.api-us1.com/api/3",
        "rate": "5 req/sec per API token (burst limits apply)"
    },
    "pipedrive": {
        "name": "Pipedrive",
        "auth": "API Token (x-api-token header) or OAuth 2.0",
        "base": "https://{company}.pipedrive.com/api/v2",
        "rate": "300 req/min limit for API token users"
    },
    "zoho": {
        "name": "Zoho CRM",
        "auth": "OAuth 2.0 (grant token, refresh token, access token)",
        "base": "https://www.zohoapis.com/crm/v7",
        "rate": "250 req/min per API token (varies by plan)"
    },
    "zapier": {
        "name": "Zapier",
        "auth": "OAuth 2.0 per connected app",
        "base": "https://zapier.com/api/v1 (internal, Zapier-managed)",
        "rate": "By plan: Free 100 tasks/mo, Pro 750, Team 2000, Company 100K"
    },
    "calendly": {
        "name": "Calendly",
        "auth": "OAuth 2.0 or Personal Access Token (PAT)",
        "base": "https://api.calendly.com",
        "rate": "No documented hard limit; uses 429 with Retry-After"
    },
    "make": {
        "name": "Make (formerly Integromat)",
        "auth": "API Key per scenario (or OAuth per app)",
        "base": "https://{region}.make.com/api/v2",
        "rate": "By plan: Operations limit per month; no per-second rate limit"
    },
    "slack": {
        "name": "Slack",
        "auth": "OAuth 2.0 with Bot Token scopes",
        "base": "https://slack.com/api",
        "rate": "1 req/sec per method per workspace (burst to 50 then 429)"
    }
}

# ─── Integration Pair Definitions ───
# Each pair has: id, name, type, popularity, endpoints, edge_cases, community, keywords, mapping_categories, mappings

PAIRS = [
    {
        "id": "salesforce-to-mailchimp",
        "name": "Salesforce ↔ Mailchimp Integration",
        "tool_a": "salesforce", "tool_b": "mailchimp",
        "sync_type": "Unidirectional (Salesforce → Mailchimp, typically via connector or middleware)",
        "popularity": "high — common setup: Salesforce as CRM of record + Mailchimp for email marketing automation",
        "auth_a": "OAuth 2.0 JWT Bearer flow. Dedicated integration user with API Enabled permission, Read on Contact, Lead, Campaign.",
        "auth_b": "OAuth 2.0 or API Key. Audience manager permissions required for list/segment management.",
        "use_cases": [
            "Sync Salesforce Leads/Contacts to Mailchimp audiences for email campaigns",
            "Salesforce Campaign Members → Mailchimp segment/tag for targeted sends",
            "Lead status changes trigger Mailchimp automation entry (e.g., new lead → welcome email)",
            "Salesforce Opportunity won → Mailchimp list tag 'customer' + automation exit",
            "Synced Salesforce reports with Mailchimp campaign performance metrics"
        ],
        "endpoints_a": [
            {"endpoint": "/services/data/v66.0/sobjects/Contact", "method": "GET/POST/PATCH", "purpose": "Read/write Contacts"},
            {"endpoint": "/services/data/v66.0/sobjects/Lead", "method": "GET/POST/PATCH", "purpose": "Read/write Leads"},
            {"endpoint": "/services/data/v66.0/query?q={SOQL}", "method": "GET", "purpose": "SOQL to fetch recently modified records"},
            {"endpoint": "/services/data/v66.0/limits", "method": "GET", "purpose": "Monitor daily API call consumption"}
        ],
        "endpoints_b": [
            {"endpoint": "/lists/{id}/members", "method": "GET/POST/PATCH", "purpose": "Add/update audience members"},
            {"endpoint": "/lists/{id}/members/{subscriber_hash}", "method": "GET/PATCH/DELETE", "purpose": "Manage specific member"},
            {"endpoint": "/lists/{id}/segments/{id}", "method": "GET/POST/PATCH", "purpose": "Manage segments/tags"},
            {"endpoint": "/lists/{id}/members/search?query={email}", "method": "GET", "purpose": "Search member by email"},
            {"endpoint": "/automations/{id}/emails/{id}/queue", "method": "POST", "purpose": "Trigger automation email"}
        ],
        "edge_cases": [
            {
                "error_code": "Email field mismatch",
                "tool": "Both",
                "category": "FIELD_MAPPING",
                "cause": "Salesforce Email field is the primary key in Mailchimp. If Email field not mapped or empty, sync silently fails.",
                "solution": "Ensure Email field is mapped. Use Salesforce formula to coalesce fields: BLANKVALUE(Email, Alternate_Email__c). Set email as required on sync."
            },
            {
                "error_code": "Mailchimp unsubscribes re-synced",
                "tool": "Mailchimp",
                "category": "DATA_QUALITY",
                "cause": "Salesforce sends a contact update for a person who unsubscribed in Mailchimp. Mailchimp re-subscribes them against their will. GDPR violation risk.",
                "solution": "Do NOT sync status='subscribed' to Mailchimp if member status is 'unsubscribed' or 'cleaned'. Check Mailchimp member status before PATCH. Better: remove unsubscribed members from Salesforce sync list."
            },
            {
                "error_code": "Custom field type mismatch",
                "tool": "Mailchimp",
                "category": "FIELD_TYPES",
                "cause": "Salesforce date fields sent as full ISO timestamps; Mailchimp merge tags expect 'MM/DD/YYYY' or 'YYYY-MM-DD'. Number fields sent as strings.",
                "solution": "Format dates as YYYY-MM-DD before sending to Mailchimp. Use NUMBER merge tag type for numeric fields. Test with one record first."
            },
            {
                "error_code": "Mailchimp audience limit exceeded",
                "tool": "Mailchimp",
                "category": "RATE_LIMIT",
                "cause": "Free Mailchimp plan has 500 contacts limit. Syncing all Salesforce contacts exceeds this. Mailchimp rejects the batch.",
                "solution": "Segment Salesforce contacts into a synced report that filters contacts to be within Mailchimp plan limit. Monitor audience size in Mailchimp dashboard."
            },
            {
                "error_code": "Salesforce Campaign → Mailchimp segment mapping",
                "tool": "Both",
                "category": "SEGMENTATION",
                "cause": "Salesforce Campaign Members don't map 1:1 to Mailchimp segments/tags. A contact can be in multiple campaigns but Mailchimp tracking differs.",
                "solution": "Use Mailchimp tags (not segments) to mirror campaign membership. Add/remove tags based on Campaign Member status."
            },
            {
                "error_code": "Email address changed in Salesforce",
                "tool": "Both",
                "category": "IDENTITY",
                "cause": "Contact email changes in Salesforce. Mailchimp requires DELETE + re-POST to change subscriber email (PATCH doesn't allow email change).",
                "solution": "On email change: DELETE old subscriber, POST new subscriber with new email. Preserve merge field data in migration."
            },
            {
                "error_code": "API call limit overlap",
                "tool": "Salesforce",
                "category": "RATE_LIMIT",
                "cause": "Salesforce daily API call limit is consumed by Mailchimp sync plus all other integrations. High-volume sync exhausts allocation before end of day.",
                "solution": "Use Salesforce CRON to schedule sync during off-peak hours. Use Bulk API 2.0 for large initial syncs. Set per-sync batch sizes to 200 records."
            },
            {
                "error_code": "Field-level security (FLS) blocking email",
                "tool": "Salesforce",
                "category": "PERMISSION",
                "cause": "Integration user profile has Read on Contact but FLS on Email field is not visible. Sync sends empty email → Mailchimp rejects.",
                "solution": "Verify FLS for integration user: Email, FirstName, LastName, and all mapped custom fields must be Read/Edit visible."
            }
        ],
        "community": [
            {"problem": "Batch subscribe errors with 'member already exists'", "solution": "Use PUT (upsert) instead of POST for batch member operations. POST returns 400 if member exists.", "source": "Mailchimp API docs"},
            {"problem": "Field length limits in Mailchimp merge tags", "solution": "Mailchimp text merge tags max 255 characters. Salesforce long text fields must be truncated. Use Mailchimp address merge tag type for structured address data.", "source": "Mailchimp developer forum"},
            {"problem": "Time zone differences in date sync", "solution": "Salesforce stores dates in UTC; Mailchimp uses account timezone. Convert to Mailchimp's timezone before sync.", "source": "Salesforce StackExchange"}
        ],
        "keywords": [
            "Salesforce Mailchimp integration",
            "Salesforce to Mailchimp sync errors",
            "Mailchimp Salesforce field mapping",
            "Salesforce Mailchimp unsubscribe sync",
            "Salesforce Mailchimp API limits"
        ],
        "field_mappings": {
            "meta": {"toolA": "salesforce", "toolB": "mailchimp", "integrationSlug": "salesforce-to-mailchimp", "lastUpdated": "2026-06-26", "totalMappings": 4},
            "categories": [
                {"id": "field-types", "name": "Field Type Translation", "description": "Salesforce field types vs Mailchimp merge tag types", "severity": "high"},
                {"id": "identity", "name": "Identity & Email Changes", "description": "Email change handling and subscriber identity", "severity": "critical"},
                {"id": "status", "name": "Subscriber Status Sync", "description": "Status transitions between Salesforce and Mailchimp", "severity": "high"},
                {"id": "campaign", "name": "Campaign & Segment Mapping", "description": "Campaign membership to Mailchimp segment/tag mapping", "severity": "medium"}
            ],
            "mappings": [
                {"id": "email-change-handling", "categoryId": "identity", "fieldName": "Email Address Change", "fieldType": "email", "toolAValue": "Contact.Email updated in Salesforce", "toolBValue": "Mailchimp requires DELETE old + POST new", "direction": "A-to-B", "behavior": "silent-failure", "severity": "critical", "notes": "PATCH does not support email changes. Old subscriber remains, new email is rejected as duplicate.", "fixStrategy": "On email change: GET subscriber by old email, DELETE, POST with new email, re-apply merge tags.", "mappedValues": []},
                {"id": "date-format-difference", "categoryId": "field-types", "fieldName": "Date/DateTime Format", "fieldType": "date", "toolAValue": "ISO 8601 timestamp (e.g., 2026-06-26T14:30:00Z)", "toolBValue": "YYYY-MM-DD (for date merge tags)", "direction": "A-to-B", "behavior": "auto-convert-partial", "severity": "high", "notes": "Salesforce sends full datetime. Mailchimp date merge tag expects date-only. Datetime sent to date field stores incorrectly.", "fixStrategy": "Cast Salesforce datetime to DATE before sending. Use Mailchimp BIRTHDAY merge type for birth dates.", "mappedValues": []},
                {"id": "resubscribe-gdpr", "categoryId": "status", "fieldName": "Unsubscribed Re-sync", "fieldType": "picklist", "toolAValue": "Contact Email_Opt_Out = false in Salesforce", "toolBValue": "Mailchimp member status = 'subscribed'", "direction": "A-to-B", "behavior": "silent-failure", "severity": "high", "notes": "Syncing status='subscribed' to a Mailchimp unsubscribed member re-subscribes them. GDPR violation in EU.", "fixStrategy": "Before PATCH: GET member status from Mailchimp. If status is 'unsubscribed' or 'cleaned', skip sync or require explicit opt-in.", "mappedValues": []},
                {"id": "campaign-member-tag", "categoryId": "campaign", "fieldName": "Campaign Member → Mailchimp Tag", "fieldType": "text", "toolAValue": "Salesforce Campaign Member (campaign ID + status)", "toolBValue": "Mailchimp tag (string, multiple tags per member)", "direction": "A-to-B", "behavior": "auto-convert-partial", "severity": "medium", "notes": "Campaign status ('Sent', 'Responded', 'Bounced') can map to Mailchimp tags. 'Bounced' should map to status change, not tag.", "fixStrategy": "Map Salesforce campaign member status to Mailchimp tag add/remove. 'Bounced' → skip tag, update member status to 'cleaned'.", "mappedValues": []}
            ],
            "errors": [
                {"errorSlug": "email-change-loss", "errorName": "Email Change Data Loss", "categoryId": "identity", "description": "PATCH doesn't allow email changes. Old subscriber persists with old email.", "fixSummary": "DELETE old subscriber, POST new subscriber with preserved data."},
                {"errorSlug": "gdpr-resubscribe", "errorName": "Involuntary Re-subscription", "categoryId": "status", "description": "Syncing status=subscribed re-subscribes Mailchimp unsubscribes. GDPR risk.", "fixSummary": "Check Mailchimp member status before syncing. Skip unsubscribed/cleaned."},
                {"errorSlug": "date-format-corruption", "errorName": "Date Format Corruption", "categoryId": "field-types", "description": "Salesforce datetime sent to Mailchimp date merge tag stores incorrectly.", "fixSummary": "Cast datetime to DATE before sending."}
            ]
        }
    },
    {
        "id": "salesforce-to-activecampaign",
        "name": "Salesforce ↔ ActiveCampaign Integration",
        "tool_a": "salesforce", "tool_b": "activecampaign",
        "sync_type": "Unidirectional or bidirectional (via middleware or native Zapier/Make)",
        "popularity": "medium-high — Salesforce for enterprise sales, ActiveCampaign for SMB email automation. Common in organizations that outgrew ActiveCampaign's CRM.",
        "auth_a": "OAuth 2.0 JWT Bearer. Integration user with API Enabled + Read on Contact, Lead, Account.",
        "auth_b": "API Token (Api-Key header). Admin-level permissions for contact, tag, list, and automation management.",
        "use_cases": [
            "Salesforce Leads → ActiveCampaign contacts with tags for automation",
            "Deal stage 'Closed Won' → ActiveCampaign list add + automation exit",
            "Salesforce campaign membership → ActiveCampaign automation trigger",
            "ActiveCampaign email engagement data (opens, clicks) → Salesforce as custom activities",
            "Lead scoring sync: ActiveCampaign score → Salesforce numeric field for reporting"
        ],
        "endpoints_a": [
            {"endpoint": "/services/data/v66.0/sobjects/Contact", "method": "GET/POST/PATCH", "purpose": "Read/write Contacts"},
            {"endpoint": "/services/data/v66.0/sobjects/Lead", "method": "GET/POST/PATCH", "purpose": "Read/write Leads"},
            {"endpoint": "/services/data/v66.0/query?q={SOQL}", "method": "GET", "purpose": "Query recently created/updated records"},
            {"endpoint": "/services/data/v66.0/limits", "method": "GET", "purpose": "Monitor daily API call consumption"}
        ],
        "endpoints_b": [
            {"endpoint": "/contacts", "method": "GET/POST/PUT", "purpose": "Create/update/get contacts"},
            {"endpoint": "/contacts/{id}/contactTags", "method": "GET/POST", "purpose": "Add/get tags for contact"},
            {"endpoint": "/contactTags", "method": "POST", "purpose": "Apply tag to contact"},
            {"endpoint": "/contactLists", "method": "POST", "purpose": "Add contact to list"},
            {"endpoint": "/automations/{id}/contact/add", "method": "POST", "purpose": "Start automation for contact"}
        ],
        "edge_cases": [
            {
                "error_code": "ContactTag wrapper bug",
                "tool": "ActiveCampaign",
                "category": "API_BUG",
                "cause": "ActiveCampaign POST /contactTags requires {'contactTag':{'contact':'1','tag':'2'}} wrapper. Flat payload returns 400.",
                "solution": "Wrap tag payload in 'contactTag' object. Always test with single contact before bulk operations."
            },
            {
                "error_code": "Salesforce daily API limit exhausted by AC sync",
                "tool": "Salesforce",
                "category": "RATE_LIMIT",
                "cause": "Bidirectional sync with ActiveCampaign consumes Salesforce API calls. Combined with other integrations, daily allocation exhausted by mid-day.",
                "solution": "Use Salesforce Bulk API 2.0 for initial sync. Schedule incremental syncs in off-peak hours. Set field-level sync filters to reduce call volume."
            },
            {
                "error_code": "Custom field type mismatch",
                "tool": "ActiveCampaign",
                "category": "FIELD_MAPPING",
                "cause": "Salesforce picklist values mapped to ActiveCampaign dropdown fields don't match. Salesforce boolean not handled by ActiveCampaign checkbox.",
                "solution": "Map picklist options explicitly. Use ActiveCampaign 'text' field type as fallback for unknown field types."
            },
            {
                "error_code": "Deleted Salesforce records not removed from AC",
                "tool": "Salesforce",
                "category": "DATA_QUALITY",
                "cause": "Contact or Lead deleted in Salesforce is not automatically removed from ActiveCampaign. Stale contacts accumulate.",
                "solution": "Use Salesforce Recycle Bin monitoring or webhook on delete operations. POST to ActiveCampaign /contacts/{id}/delete on delete detection."
            },
            {
                "error_code": "Automation re-trigger on update",
                "tool": "ActiveCampaign",
                "category": "AUTOMATION",
                "cause": "Every contact update from Salesforce re-triggers ActiveCampaign automation if 'contact updated' trigger is active. Users receive duplicate emails.",
                "solution": "Use ActiveCampaign 'contact added to list' trigger instead of 'contact updated'. Or add a 'skip automation' tag that automations check for."
            },
            {
                "error_code": "Phone number format inconsistency",
                "tool": "Both",
                "category": "DATA_FORMAT",
                "cause": "Salesforce stores phone as (555) 123-4567. ActiveCampaign normalizes to +15551234567. Re-sync flips between formats.",
                "solution": "Choose one format as canonical. Configure ActiveCampaign phone field as text to prevent auto-formatting. Or accept AC's normalization."
            },
            {
                "error_code": "List membership sync mismatch",
                "tool": "ActiveCampaign",
                "category": "SEGMENTATION",
                "cause": "ActiveCampaign uses 'list' as the primary container; Salesforce uses 'campaign.' A contact added to Salesforce campaign should go to AC list, but mapping isn't 1:1.",
                "solution": "Map Salesforce Campaign Member records to AC list add via middleware. One Salesforce campaign = one AC list name. Use AC tags for sub-segmentation."
            },
            {
                "error_code": "Email engagement sync loops",
                "tool": "Both",
                "category": "SYNC_LOOP",
                "cause": "ActiveCampaign email open → webhook updates Salesforce contact → Salesforce syncs back to AC → AC records another activity → infinite loop.",
                "solution": "Track 'source' field on records. AC-created activities get source='ActiveCampaign'. Exclude source=ActiveCampaign records from AC→SF sync."
            }
        ],
        "community": [
            {"problem": "ActiveCampaign API pagination limits — 20 per page default", "solution": "Set ?limit=100 on AC list endpoints. For full sync, iterate with ?offset parameter.", "source": "ActiveCampaign API docs"},
            {"problem": "Salesforce sandbox vs production mismatch", "solution": "Use separate API keys/connections for sandbox and production. AC doesn't differentiate environments.", "source": "Salesforce StackExchange"}
        ],
        "keywords": [
            "Salesforce ActiveCampaign integration",
            "Salesforce ActiveCampaign sync errors",
            "ActiveCampaign Salesforce field mapping",
            "Salesforce ActiveCampaign API limits",
            "Salesforce to ActiveCampaign contact sync"
        ],
        "field_mappings": {
            "meta": {"toolA": "salesforce", "toolB": "activecampaign", "integrationSlug": "salesforce-to-activecampaign", "lastUpdated": "2026-06-26", "totalMappings": 4},
            "categories": [
                {"id": "contacttag", "name": "Contact & Tag Structure", "description": "ContactTag wrapper bug and tag ID mapping", "severity": "critical"},
                {"id": "field-type", "name": "Field Type Translation", "description": "Salesforce picklist/boolean → AC dropdown/checkbox", "severity": "high"},
                {"id": "automation", "name": "Automation Trigger Gaps", "description": "How updates trigger or fail to trigger AC automations", "severity": "medium"},
                {"id": "phone", "name": "Phone Number Formatting", "description": "AC phone auto-format vs Salesforce raw format", "severity": "low"}
            ],
            "mappings": [
                {"id": "contacttag-payload-ac", "categoryId": "contacttag", "fieldName": "ContactTag API Payload", "fieldType": "object", "toolAValue": "Contact ID from Salesforce", "toolBValue": "Requires {'contactTag':{'contact':'1','tag':'2'}}", "direction": "A-to-B", "behavior": "warning", "severity": "critical", "notes": "Same bug as HubSpot→AC. Wrapper required. Check middleware payload format.", "fixStrategy": "Wrap in contactTag object. Verify with curl before production.", "mappedValues": []},
                {"id": "picklist-to-dropdown", "categoryId": "field-type", "fieldName": "Picklist to Dropdown/Listbox", "fieldType": "picklist", "toolAValue": "Salesforce picklist value (e.g., 'Prospecting')", "toolBValue": "ActiveCampaign dropdown option (must match exactly)", "direction": "A-to-B", "behavior": "silent-failure", "severity": "high", "notes": "Dropdown option values must match picklist values exactly. Mismatch silently drops the value.", "fixStrategy": "Audit picklist options on both sides. Create AC dropdown options matching SF values.", "mappedValues": []},
                {"id": "automation-retrigger", "categoryId": "automation", "fieldName": "Automation Re-trigger on Update", "fieldType": "text", "toolAValue": "Contact updated in Salesforce (any field change)", "toolBValue": "ActiveCampaign automation fires on 'contact updated'", "direction": "A-to-B", "behavior": "silent-failure", "severity": "medium", "notes": "Unintended re-triggers send duplicate emails. Common issue with bidirectional sync.", "fixStrategy": "Use 'contact added to list' trigger. Add metadata field to track sync version.", "mappedValues": []},
                {"id": "phone-format", "categoryId": "phone", "fieldName": "Phone Number Format", "fieldType": "phone", "toolAValue": "Raw format from Salesforce (e.g., (555) 123-4567)", "toolBValue": "AC auto-formatted to E.164 (+15551234567)", "direction": "A-to-B", "behavior": "auto-convert", "severity": "low", "notes": "AC normalizes phone on write. Re-reading shows different format than sent.", "fixStrategy": "Store phone as text field in AC to prevent normalization. Or accept AC format as canonical.", "mappedValues": []}
            ],
            "errors": [
                {"errorSlug": "contacttag-400-ac", "errorName": "ContactTag 400 Payload Format", "categoryId": "contacttag", "description": "Missing contactTag wrapper produces 400 error.", "fixSummary": "Wrap in contactTag object."},
                {"errorSlug": "dropdown-value-dropped", "errorName": "Picklist→Dropdown Silent Value Drop", "categoryId": "field-type", "description": "Mismatched dropdown option values silently dropped.", "fixSummary": "Exact match audit between picklist options and dropdown options."}
            ]
        }
    },
    {
        "id": "hubspot-to-slack",
        "name": "HubSpot ↔ Slack Integration",
        "tool_a": "hubspot", "tool_b": "slack",
        "sync_type": "Unidirectional (HubSpot → Slack via webhook/connector) or bidirectional (via Slack Workflow Builder)",
        "popularity": "high — most common sales/marketing notification setup: deals closing → Slack alert, form submissions → Slack channel",
        "auth_a": "OAuth 2.0 with webhook scopes. Workflow action scopes for creating Slack messages.",
        "auth_b": "OAuth 2.0 Bot Token with chat:write, channels:read, incoming-webhook scopes.",
        "use_cases": [
            "New deal created in HubSpot → Slack channel notification to sales team",
            "High-value deal stage change ('Closed Won') → Slack @here alert",
            "HubSpot form submission → Slack lead notification with contact details",
            "Slack shortcut → Create HubSpot contact/ticket from Slack message",
            "HubSpot ticket priority escalation → Slack channel with thread"
        ],
        "endpoints_a": [
            {"endpoint": "/crm/v3/objects/deals", "method": "GET", "purpose": "Fetch deal details for Slack notification"},
            {"endpoint": "/crm/v3/objects/contacts", "method": "GET", "purpose": "Fetch contact details for Slack notification"}
        ],
        "endpoints_b": [
            {"endpoint": "/chat.postMessage", "method": "POST", "purpose": "Send message to Slack channel"},
            {"endpoint": "/chat.postEphemeral", "method": "POST", "purpose": "Send ephemeral message to specific user"},
            {"endpoint": "/conversations.join", "method": "POST", "purpose": "Bot joins channel before posting"},
            {"endpoint": "/views.open", "method": "POST", "purpose": "Open Slack modal for HubSpot actions"}
        ],
        "edge_cases": [
            {
                "error_code": "Slack rate limit (1 per second per method)",
                "tool": "Slack",
                "category": "RATE_LIMIT",
                "cause": "Bulk deal update in HubSpot triggers 50 Slack messages simultaneously. Slack returns 429 with Retry-After.",
                "solution": "Batch Slack notifications. Use a queue in your middleware. Send a single summary message instead of individual alerts."
            },
            {
                "error_code": "Bot not in channel",
                "tool": "Slack",
                "category": "PERMISSION",
                "cause": "Slack bot token has chat:write scope but bot hasn't joined the target channel. POST returns not_in_channel error.",
                "solution": "Call conversations.join before chat.postMessage. Or use chat.postMessage with channel ID (not name) and ensure bot is invited."
            },
            {
                "error_code": "Message formatting issues",
                "tool": "Slack",
                "category": "FORMATTING",
                "cause": "HubSpot deal amount $1,000,000 sent as plain text without Slack Block Kit formatting. Message looks unprofessional.",
                "solution": "Format Slack messages using Block Kit (blocks array in API call). Use section blocks with markdown text."
            },
            {
                "error_code": "Duplicate messages on webhook retry",
                "tool": "HubSpot",
                "category": "WEBHOOK",
                "cause": "HubSpot webhook delivery retries (up to 24h) cause duplicate Slack messages if middleware doesn't deduplicate by webhook event ID.",
                "solution": "Track HubSpot webhook eventId in middleware. Skip processing if eventId already handled."
            },
            {
                "error_code": "Slack token expiry (OAuth bot tokens don't expire by default unless revoked)",
                "tool": "Slack",
                "category": "AUTH",
                "cause": "Slack bot token revoked by workspace admin. Middleware starts getting 401 errors silently.",
                "solution": "Monitor for 401 responses from Slack API. Set up alert to re-authorize Slack app. Use token rotation if using granular permissions."
            },
            {
                "error_code": "Message too long",
                "tool": "Slack",
                "category": "VALIDATION",
                "cause": "HubSpot deal with 50+ custom fields sends a 10,000-character message. Slack max is 4,000 characters per block text.",
                "solution": "Truncate field list to top 5-10 fields in Slack message. Add 'View in HubSpot' link for full record."
            },
            {
                "error_code": "Thread replies lost on webhook timeout",
                "tool": "HubSpot",
                "category": "TIMEOUT",
                "cause": "HubSpot webhook expects a 200 response within 5 seconds. Slack rate limit causes middleware to delay, HubSpot retries and creates duplicate threads.",
                "solution": "Acknowledge webhook immediately (200, empty body). Process Slack message asynchronously in background."
            },
            {
                "error_code": "Block Kit JSON malformed",
                "tool": "Slack",
                "category": "VALIDATION",
                "cause": "HubSpot data contains characters that break Slack Block Kit markdown (unclosed * or _) or invalid Block Kit JSON structure.",
                "solution": "Escape HubSpot text fields before inserting into Block Kit templates. Validate JSON before sending. Use Slack Block Kit Builder."
            }
        ],
        "community": [
            {"problem": "Slack webhook URL vs API token confusion", "solution": "Incoming Webhooks use a fixed URL (no token). API calls use Bot Token (xoxb-). Choose one pattern and stick with it.", "source": "Slack API docs"},
            {"problem": "Slack rate limit on bulk notification retry loops", "solution": "HubSpot webhook retries + Slack rate limit = cascade failure. Implement dead-letter queue after 3 failed Slack attempts.", "source": "r/Slack_Developers Reddit"}
        ],
        "keywords": [
            "HubSpot Slack integration",
            "HubSpot to Slack notification setup",
            "Slack API rate limit 429",
            "HubSpot webhook Slack bot",
            "Slack Block Kit HubSpot deals"
        ],
        "field_mappings": {
            "meta": {"toolA": "hubspot", "toolB": "slack", "integrationSlug": "hubspot-to-slack", "lastUpdated": "2026-06-26", "totalMappings": 3},
            "categories": [
                {"id": "message-format", "name": "Message Formatting", "description": "HubSpot data formatting for Slack Block Kit", "severity": "high"},
                {"id": "rate-limit", "name": "Rate Limit & Queuing", "description": "Slack per-method rate limit vs HubSpot webhook bursts", "severity": "critical"},
                {"id": "channel", "name": "Channel Routing", "description": "Mapping HubSpot pipeline stages to Slack channels", "severity": "medium"}
            ],
            "mappings": [
                {"id": "blockkit-formatting", "categoryId": "message-format", "fieldName": "Markdown Escape in Block Kit", "fieldType": "text", "toolAValue": "HubSpot field values (may contain *, _, ~, `)", "toolBValue": "Slack mrkdwn (markdown with special chars)", "direction": "A-to-B", "behavior": "silent-failure", "severity": "high", "notes": "Unescaped * or _ in deal names breaks Block Kit rendering. Message appears malformed.", "fixStrategy": "Escape HubSpot text: replace *, _, ~ with HTML entities or escape sequences before Block Kit insertion.", "mappedValues": []},
                {"id": "bulk-rate-limit", "categoryId": "rate-limit", "fieldName": "Bulk Notification Throttling", "fieldType": "text", "toolAValue": "HubSpot webhook: up to 100 events in seconds", "toolBValue": "Slack: 1 req/sec per method per workspace", "direction": "A-to-B", "behavior": "auto-convert", "severity": "critical", "notes": "Pipeline bulk update triggers 50 webhooks, each trying to post to Slack. All but first get 429.", "fixStrategy": "Queue in middleware. Send at 1/sec. Or aggregate into one summary message.", "mappedValues": []},
                {"id": "channel-deal-stage", "categoryId": "channel", "fieldName": "Deal Stage → Channel Routing", "fieldType": "text", "toolAValue": "HubSpot deal stage name (e.g., 'closedwon')", "toolBValue": "Slack channel ID (e.g., C0123456789)", "direction": "A-to-B", "behavior": "auto-convert", "severity": "medium", "notes": "Stage 'closedwon' → #closed-wins. Stage 'urgent-escalation' → #support-urgent. Mapping is custom per team.", "fixStrategy": "Create mapping table: stageSlug → channelId in middleware config.", "mappedValues": []}
            ],
            "errors": [
                {"errorSlug": "rate-limit-flood", "errorName": "Slack Rate Limit Flood from Webhook Batch", "categoryId": "rate-limit", "description": "Bulk webhook triggers exceed 1/sec Slack rate limit. Messages lost.", "fixSummary": "Queue messages, send at 1/sec, or aggregate into summaries."},
                {"errorSlug": "blockkit-break", "errorName": "Block Kit Rendering Break", "categoryId": "message-format", "description": "Unescaped HubSpot text breaks Slack markdown formatting.", "fixSummary": "Escape text fields before Block Kit insertion."}
            ]
        }
    },
    {
        "id": "pipedrive-to-mailchimp",
        "name": "Pipedrive ↔ Mailchimp Integration",
        "tool_a": "pipedrive", "tool_b": "mailchimp",
        "sync_type": "Unidirectional (Pipedrive → Mailchimp, typically via middleware)",
        "popularity": "medium — common for organizations using Pipedrive pipeline management + Mailchimp email marketing",
        "auth_a": "API Token (x-api-token header) or OAuth 2.0. v2 API required (v1 deprecated July 31, 2026).",
        "auth_b": "OAuth 2.0 or API Key. Audience manager permissions.",
        "use_cases": [
            "Pipedrive deal 'Won' → Mailchimp list add + tag 'customer'",
            "Pipedrive person created → Mailchimp audience member with merge fields",
            "Pipedrive deal stage update → Mailchimp segment membership change",
            "Pipedrive activity completed → Mailchimp automation trigger",
            "Bulk Pipedrive person import → Mailchimp audience sync"
        ],
        "endpoints_a": [
            {"endpoint": "/persons", "method": "GET/POST", "purpose": "Read/create persons in Pipedrive v2"},
            {"endpoint": "/persons/search", "method": "GET", "purpose": "Search persons by email for matching"},
            {"endpoint": "/deals", "method": "GET", "purpose": "Read deals for deal-to-audience mapping"}
        ],
        "endpoints_b": [
            {"endpoint": "/lists/{id}/members", "method": "GET/POST/PUT", "purpose": "Manage audience members"},
            {"endpoint": "/lists/{id}/members/{subscriber_hash}", "method": "GET/PATCH", "purpose": "Update specific member"},
            {"endpoint": "/lists/{id}/segments", "method": "GET/POST", "purpose": "Manage segments"}
        ],
        "edge_cases": [
            {
                "error_code": "Pipedrive v2 hash key field IDs in custom data",
                "tool": "Pipedrive",
                "category": "API_VERSION",
                "cause": "Pipedrive v2 sends custom field data keyed by hash key (a1b2c3d4), not numeric ID. Middleware expecting numeric keys reads empty values.",
                "solution": "After migrating to v2, fetch all custom field schemas and update middleware field mappings to use hash keys."
            },
            {
                "error_code": "Pipedrive person email not required",
                "tool": "Pipedrive",
                "category": "DATA_QUALITY",
                "cause": "Pipedrive persons can be created without an email. Mailchimp requires email as primary key. Sync silently skips these persons.",
                "solution": "Filter Pipedrive persons with email = null before sync. Log skipped persons for manual data enrichment."
            },
            {
                "error_code": "Mailchimp daily list add limit",
                "tool": "Mailchimp",
                "category": "RATE_LIMIT",
                "cause": "Mailchimp enforces daily add limits (new subscribers) based on plan. Bulk Pipedrive sync exceeds limit. Mailchimp rejects.",
                "solution": "Monitor Mailchimp subscriber count vs plan limit. Spread bulk syncs across multiple days. Delete inactive subscribers first."
            },
            {
                "error_code": "Pipedrive deal 'Won' re-triggers on update",
                "tool": "Pipedrive",
                "category": "AUTOMATION",
                "cause": "Pipedrive webhook fires on deal update even when stage doesn't change. Middleware sends duplicate 'customer' tags to Mailchimp.",
                "solution": "Track deal stage transitions in middleware. Only trigger Mailchimp actions on actual stage changes, not every update."
            },
            {
                "error_code": "Custom field mapping between v1 and v2 field IDs",
                "tool": "Pipedrive",
                "category": "MIGRATION",
                "cause": "During v1→v2 migration, custom field IDs change from numeric to hash keys. Mailchimp mapping table becomes stale.",
                "solution": "Rebuild custom field mapping table after v2 migration. Do not rely on cached field ID mappings."
            },
            {
                "error_code": "Person merge in Pipedrive duplicates Mailchimp member",
                "tool": "Pipedrive",
                "category": "DATA_QUALITY",
                "cause": "Two Pipedrive persons merged. Middleware receives update for both old and new person IDs. Mailchimp gets duplicate or inconsistent data.",
                "solution": "Handle person merge events in middleware: identify merged persons by email dedup. Archive old Mailchimp member before adding new."
            },
            {
                "error_code": "Deal-associated persons not implicitly synced",
                "tool": "Pipedrive",
                "category": "CONFIGURATION",
                "cause": "Pipedrive deals have associated persons. Middleware watches deal stage changes but doesn't export associated person data to Mailchimp.",
                "solution": "When deal stage triggers Mailchimp action, fetch associated person(s) via GET /persons/{id} and include their data in Mailchimp sync."
            }
        ],
        "community": [
            {"problem": "Pipedrive webhook delivery guarantees — at least once", "solution": "Pipedrive 'at least once' delivery can produce duplicate webhook events. Use idempotency key in middleware.", "source": "Pipedrive developer docs"},
            {"problem": "Mailchimp subscriber hash generation", "solution": "Mailchimp subscriber_hash = md5(email.toLowerCase()). Ensure email is lowercased before hashing for PATCH operations.", "source": "Mailchimp API docs"}
        ],
        "keywords": [
            "Pipedrive Mailchimp integration",
            "Pipedrive to Mailchimp sync",
            "Pipedrive Mailchimp v2 migration",
            "Pipedrive deal to Mailchimp audience"
        ],
        "field_mappings": {
            "meta": {"toolA": "pipedrive", "toolB": "mailchimp", "integrationSlug": "pipedrive-to-mailchimp", "lastUpdated": "2026-06-26", "totalMappings": 3},
            "categories": [
                {"id": "email-required", "name": "Email Field Required", "description": "Pipedrive optional email vs Mailchimp required email", "severity": "critical"},
                {"id": "stage-trigger", "name": "Deal Stage → List Action", "description": "Mapping Pipedrive stage changes to Mailchimp actions", "severity": "high"},
                {"id": "v2-migration", "name": "v2 Migration Field IDs", "description": "Hash key field IDs breaking custom field mappings", "severity": "high"}
            ],
            "mappings": [
                {"id": "email-null-skip", "categoryId": "email-required", "fieldName": "Email Not Required in Pipedrive", "fieldType": "email", "toolAValue": "Pipedrive person without email", "toolBValue": "Mailchimp requires email for member", "direction": "A-to-B", "behavior": "silent-failure", "severity": "critical", "notes": "Person without email is silently skipped. No error, no log.", "fixStrategy": "Filter persons with email=null before sync. Log skipped for follow-up.", "mappedValues": []},
                {"id": "stage-to-list", "categoryId": "stage-trigger", "fieldName": "Deal Stage → Audience Action", "fieldType": "picklist", "toolAValue": "Pipedrive deal stage ('won', 'lost')", "toolBValue": "Mailchimp action (add to list, tag, remove)", "direction": "A-to-B", "behavior": "auto-convert-partial", "severity": "high", "notes": "'won' → add to 'Customers' list + tag 'customer'. 'lost' → tag 'lost-deal' but stay on list.", "fixStrategy": "Define clear stage→action mapping. Handle edge stages (e.g., custom stages) explicitly.", "mappedValues": []},
                {"id": "hash-key-mapping", "categoryId": "v2-migration", "fieldName": "Custom Field Hash Key Mapping", "fieldType": "id", "toolAValue": "Pipedrive v2 hash key field ID", "toolBValue": "Mailchimp merge tag name", "direction": "A-to-B", "behavior": "silent-failure", "severity": "high", "notes": "Post-v2 migration, numeric field IDs become hash keys. Middleware referencing old numeric keys reads empty.", "fixStrategy": "After v2 migration, re-fetch all custom field schemas. Update mapping table with hash keys.", "mappedValues": []}
            ],
            "errors": [
                {"errorSlug": "person-no-email-skip", "errorName": "Person Without Email Silently Skipped", "categoryId": "email-required", "description": "Pipedrive persons without email don't sync to Mailchimp.", "fixSummary": "Filter + log. Enrich email data before sync."},
                {"errorSlug": "v2-field-id-break", "errorName": "v2 Migration Breaks Custom Field Mapping", "categoryId": "v2-migration", "description": "Hash key field IDs break existing custom data mapping.", "fixSummary": "Rebuild mapping table after v2 migration."}
            ]
        }
    },
    {
        "id": "zoho-to-mailchimp",
        "name": "Zoho CRM ↔ Mailchimp Integration",
        "tool_a": "zoho", "tool_b": "mailchimp",
        "sync_type": "Unidirectional (Zoho → Mailchimp via Zoho Flow, middleware, or native connector)",
        "popularity": "medium — Zoho CRM users often pair with Mailchimp for email marketing at lower price point than HubSpot/Salesforce",
        "auth_a": "OAuth 2.0 with scopes for Zoho CRM modules (Leads, Contacts, Accounts). Refresh token required (1h expiry).",
        "auth_b": "OAuth 2.0 or API Key. Audience management scopes.",
        "use_cases": [
            "Zoho Lead creation → Mailchimp subscriber add with lead score merge field",
            "Zoho Contact stage change → Mailchimp tag update",
            "Zoho Campaign member → Mailchimp segment membership",
            "Bulk Zoho contact sync → Mailchimp audience (initial setup)",
            "Zoho deal 'Closed Won' → Mailchimp list transfer + automation trigger"
        ],
        "endpoints_a": [
            {"endpoint": "/crm/v7/Contacts", "method": "GET/POST/PUT", "purpose": "Read/write Contacts"},
            {"endpoint": "/crm/v7/Leads", "method": "GET/POST/PUT", "purpose": "Read/write Leads"},
            {"endpoint": "/crm/v7/Contacts/search", "method": "POST", "purpose": "Search by email for dedup"}
        ],
        "endpoints_b": [
            {"endpoint": "/lists/{id}/members", "method": "GET/POST/PUT", "purpose": "Manage audience members"},
            {"endpoint": "/lists/{id}/members/{subscriber_hash}", "method": "GET/PATCH", "purpose": "Update specific member"}
        ],
        "edge_cases": [
            {
                "error_code": "Zoho OAuth token expires every hour",
                "tool": "Zoho",
                "category": "AUTH",
                "cause": "Zoho CRM OAuth access token expires every 60 minutes. Middleware with stale token gets 401. Silent failure if not retried.",
                "solution": "Implement token refresh in middleware (grant_type=refresh_token). Proactively refresh every 50 minutes. Retry with new token on 401."
            },
            {
                "error_code": "Zoho contact duplicate detection differs from Mailchimp",
                "tool": "Both",
                "category": "DATA_QUALITY",
                "cause": "Zoho dedup by email is optional (can have multiple contacts with same email). Mailchimp strictly dedups by email. Sync creates Mailchimp errors.",
                "solution": "Before sync: enforce email dedup in Zoho or choose which Zoho contact wins for duplicate emails."
            },
            {
                "error_code": "Zoho API rate limit (250 req/min)",
                "tool": "Zoho",
                "category": "RATE_LIMIT",
                "cause": "Bulk sync of 10,000+ contacts hits Zoho 250 req/min limit. Sync pauses or fails midway.",
                "solution": "Batch with 2-second delays between requests. Implement exponential backoff on 429."
            },
            {
                "error_code": "Mailchimp plan subscriber limit",
                "tool": "Mailchimp",
                "category": "PLAN_LIMIT",
                "cause": "Zoho CRM has unlimited contacts. Mailchimp free/paid plans have subscriber limits. Bulk sync exceeds plan and Mailchimp rejects contacts.",
                "solution": "Apply Zoho CRM filter before sync (e.g., Lead Status = 'Warm'). Monitor Mailchimp audience count against plan limit."
            },
            {
                "error_code": "Zoho multi-currency to Mailchimp number field",
                "tool": "Both",
                "category": "FIELD_TYPES",
                "cause": "Zoho deal amount with currency symbol ($1,000.50) sent to Mailchimp number merge field fails because of non-numeric characters.",
                "solution": "Strip currency symbols and commas before sending. Send numeric string to Mailchimp NUMBER merge tag."
            },
            {
                "error_code": "Time zone offset in Zoho datetime fields",
                "tool": "Zoho",
                "category": "DATA_FORMAT",
                "cause": "Zoho stores datetime in org timezone with offset. Mailchimp expects UTC or plain date. Mismatch shifts dates by hours.",
                "solution": "Convert Zoho datetime to UTC before sending. Send only date part (YYYY-MM-DD) for Mailchimp date merge fields."
            },
            {
                "error_code": "Zoho custom lookup fields as IDs, not values",
                "tool": "Zoho",
                "category": "FIELD_MAPPING",
                "cause": "Zoho lookup fields to related records return record ID (e.g., 123456789), not the display name. Mailchimp displays the numeric ID instead of the actual value.",
                "solution": "Resolve lookup field IDs to display values via Zoho API before sending to Mailchimp."
            }
        ],
        "community": [
            {"problem": "Zoho API v2→v7 migration still catching users", "solution": "Zoho CRM API v2 deprecated 2023, v7 current. Many middleware still uses old endpoints. Check your API version.", "source": "Zoho CRM API docs"},
            {"problem": "Mailchimp merge tag 80-field limit", "solution": "Mailchimp max 80 merge tags per audience. Zoho has hundreds of fields. Prioritize 20-30 critical fields.", "source": "Mailchimp developer forum"}
        ],
        "keywords": [
            "Zoho Mailchimp integration",
            "Zoho CRM Mailchimp sync",
            "Zoho Mailchimp API limits",
            "Zoho OAuth token refresh Mailchimp"
        ],
        "field_mappings": {
            "meta": {"toolA": "zoho", "toolB": "mailchimp", "integrationSlug": "zoho-to-mailchimp", "lastUpdated": "2026-06-26", "totalMappings": 3},
            "categories": [
                {"id": "auth-refresh", "name": "OAuth Token Refresh", "description": "Zoho 1-hour token vs Mailchimp API key longevity", "severity": "critical"},
                {"id": "duplicate-email", "name": "Duplicate Email Handling", "description": "Zoho allows duplicate emails. Mailchimp does not.", "severity": "high"},
                {"id": "field-priority", "name": "Field Volume & Priority", "description": "Zoho hundreds of fields vs Mailchimp 80 merge tag limit", "severity": "medium"}
            ],
            "mappings": [
                {"id": "oauth-refresh-60min", "categoryId": "auth-refresh", "fieldName": "Zoho Access Token TTL", "fieldType": "text", "toolAValue": "Zoho OAuth token: expires in 60 minutes", "toolBValue": "Mailchimp API key: no expiry", "direction": "A-to-B", "behavior": "warning", "severity": "critical", "notes": "Stale Zoho token causes silent 401 failures mid-sync. Refresh token lasts 1 year or until revoked.", "fixStrategy": "Implement proactive refresh at 50 min. Queue sync operations during token refresh window.", "mappedValues": []},
                {"id": "dup-email-resolution", "categoryId": "duplicate-email", "fieldName": "Duplicate Email in Zoho", "fieldType": "email", "toolAValue": "Multiple Zoho contacts with same email", "toolBValue": "Mailchimp: one member per email", "direction": "A-to-B", "behavior": "warning", "severity": "high", "notes": "Last-synced contact wins by default. No merge logic — data loss risk.", "fixStrategy": "Define priority rule: most recently modified Zoho contact wins. Log duplicate conflicts.", "mappedValues": []},
                {"id": "merge-tag-limit", "categoryId": "field-priority", "fieldName": "Field Count Limit", "fieldType": "text", "toolAValue": "Zoho: 100+ custom fields per module", "toolBValue": "Mailchimp: max 80 merge tags per audience", "direction": "A-to-B", "behavior": "silent-failure", "severity": "medium", "notes": "Excess fields are silently dropped. No error when merge tag limit exceeded.", "fixStrategy": "Prioritize 20-30 high-value fields. Document excluded fields.", "mappedValues": []}
            ],
            "errors": [
                {"errorSlug": "oauth-stale-token", "errorName": "Zoho OAuth Token Expiry Mid-Sync", "categoryId": "auth-refresh", "description": "60-minute token expiry causes mid-batch failures.", "fixSummary": "Proactive refresh at 50 minutes. Retry on 401."},
                {"errorSlug": "field-limit-drop", "errorName": "Zoho Fields Dropped at Mailchimp 80 Merge Tag Limit", "categoryId": "field-priority", "description": "Fields beyond 80th merge tag silently not synced.", "fixSummary": "Prioritize fields. Check merge tag count."}
            ]
        }
    },
    {
        "id": "zapier-to-calendly",
        "name": "Zapier ↔ Calendly Integration",
        "tool_a": "zapier", "tool_b": "calendly",
        "sync_type": "Bidirectional (Zapier acts as middleware reacting to Calendly events and triggering actions in other tools)",
        "popularity": "very high — most common Calendly integration pattern: booking triggers CRM/HubSpot contact creation via Zapier",
        "auth_a": "OAuth 2.0 per connected app. Zapier manages auth on behalf of the user.",
        "auth_b": "OAuth 2.0 or Personal Access Token (PAT). Webhook subscriptions scope required.",
        "use_cases": [
            "Calendly event booked → Zapier creates HubSpot/Salesforce contact",
            "Calendly event rescheduled/canceled → Zapier updates CRM status",
            "Calendly invitee questions → Zapier creates deal with custom fields",
            "Calendly event type → Zapier routing to different CRM pipelines",
            "Calendly webhook → Zapier sends Slack notification to sales rep"
        ],
        "endpoints_a": [
            {"endpoint": "/zapier/api/v1 (managed by Zapier)", "method": "N/A", "purpose": "Zapier internal API; user doesn't call directly"}
        ],
        "endpoints_b": [
            {"endpoint": "/webhook_subscriptions", "method": "POST", "purpose": "Create webhook subscription for event types"},
            {"endpoint": "/scheduled_events/{uuid}", "method": "GET", "purpose": "Get event details with invitee, guest info"},
            {"endpoint": "/invitees/{uuid}", "method": "GET", "purpose": "Get invitee details including questions/answers"},
            {"endpoint": "/event_types/{uuid}", "method": "GET", "purpose": "Get event type configuration"}
        ],
        "edge_cases": [
            {
                "error_code": "Calendly webhook verification header missing",
                "tool": "Calendly",
                "category": "WEBHOOK",
                "cause": "Calendly sends webhook signature header for verification. Zapier's built-in Calendly trigger handles this, but custom webhook trigger doesn't.",
                "solution": "Use Zapier's Calendly integration (handles verification). If using Webhooks by Zapier, verify the signature manually using Calendly's webhook signing secret."
            },
            {
                "error_code": "Calendly webhook delivery delays",
                "tool": "Calendly",
                "category": "WEBHOOK",
                "cause": "Calendly delivers webhooks asynchronously. High-traffic events may have 30-120 second delays. Zapier scheduled poll adds 1-15 min more.",
                "solution": "For real-time needs, use Calendly webhook (instant) → Zapier Catch Hook trigger (instant). Avoid Zapier polling triggers."
            },
            {
                "error_code": "Calendly API rate limit on webhook subscriptions",
                "tool": "Calendly",
                "category": "RATE_LIMIT",
                "cause": "Calendly enforces rate limits on API calls. Frequent webhook subscription creation/deletion triggers 429.",
                "solution": "Reuse webhook subscriptions. Monitor rate limit headers (X-RateLimit-Remaining). Cache subscription IDs."
            },
            {
                "error_code": "Multiple Calendly event types — single Zap limitation",
                "tool": "Zapier",
                "category": "CONFIGURATION",
                "cause": "One Calendly trigger in Zapier watches 'all event types' by default. Users need different actions per event type (e.g., discovery call → Salesforce lead, demo → HubSpot contact).",
                "solution": "Use 'Filter by Zapier' step to route based on event type name. Or create separate Zaps per event type."
            },
            {
                "error_code": "Calendly invitee time zone not passed to CRM",
                "tool": "Calendly",
                "category": "FIELD_MAPPING",
                "cause": "Calendly collects invitee timezone during booking. If Zapier step doesn't map timezone field to CRM, the timezone data is lost.",
                "solution": "Map 'invitee timezone' field from Calendly trigger to CRM custom 'Timezone' field. Don't rely on automatically detected timezone."
            },
            {
                "error_code": "Rescheduled events create duplicates",
                "tool": "Calendly",
                "category": "DATA_QUALITY",
                "cause": "Calendly sends 'event.created' on initial booking and another 'event.created' (not 'event.rescheduled') on reschedule. Zapier creates duplicate CRM records.",
                "solution": "Use Calendly 'event.created' but check for existing contact/lead by email before creating. Add dedup logic in Zapier step."
            },
            {
                "error_code": "Cancelled events not cleaned up",
                "tool": "Calendly",
                "category": "DATA_QUALITY",
                "cause": "Calendly send 'event.canceled' webhook. Many Zaps process 'event.created' only, missing the cancel event. CRM shows appointments that were cancelled.",
                "solution": "Add a Zap that listens for 'event.canceled' and updates CRM record status to 'No Show' or 'Cancelled'."
            },
            {
                "error_code": "Calendly OAuth token expiration",
                "tool": "Calendly",
                "category": "AUTH",
                "cause": "Calendly OAuth access tokens expire. Zapier handles this automatically, but custom setup connecting Calendly API directly via Webhooks by Zapier needs manual token refresh.",
                "solution": "Use Zapier's built-in Calendly integration (managed OAuth). If using Webhooks by Zapier, implement token refresh logic."
            }
        ],
        "community": [
            {"problem": "Calendly webhook payload size limit", "solution": "Calendly caps webhook payloads. Large invitee question sets may be truncated. Send invitee UUID and fetch full details via API.", "source": "Calendly developer docs"},
            {"problem": "Duplicate webhook delivery from Calendly", "solution": "Calendly delivers 'at least once.' Add idempotency check in Zapier using webhook UUID.", "source": "Calendly status page"}
        ],
        "keywords": [
            "Zapier Calendly integration",
            "Calendly webhook Zapier setup",
            "Calendly Zapier duplicate contacts",
            "Calendly webhook to CRM",
            "Calendly API rate limits"
        ],
        "field_mappings": {
            "meta": {"toolA": "zapier", "toolB": "calendly", "integrationSlug": "zapier-to-calendly", "lastUpdated": "2026-06-26", "totalMappings": 3},
            "categories": [
                {"id": "webhook-timing", "name": "Webhook Timing & Delivery", "description": "Webhook delays, duplicates, and verification", "severity": "high"},
                {"id": "event-routing", "name": "Event Type Routing", "description": "Different actions per Calendly event type", "severity": "high"},
                {"id": "data-persistence", "name": "Data Persistence Across Events", "description": "Reschedule/cancel handling and timezone preservation", "severity": "medium"}
            ],
            "mappings": [
                {"id": "webhook-signature", "categoryId": "webhook-timing", "fieldName": "Webhook Signature Verification", "fieldType": "text", "toolAValue": "Zapier managed webhook (no sig needed)", "toolBValue": "Calendly custom webhook: requires signature header verification", "direction": "B-to-A", "behavior": "auto-convert", "severity": "high", "notes": "Built-in Zapier Calendly trigger handles verification. Custom webhook triggers need manual sig check.", "fixStrategy": "Use built-in Zapier Calendly integration. If custom webhook, implement HMAC-SHA256 signature verification.", "mappedValues": []},
                {"id": "event-type-routing", "categoryId": "event-routing", "fieldName": "Event Type to Action Mapping", "fieldType": "picklist", "toolAValue": "Calendly event type name (e.g., 'Discovery Call', 'Demo')", "toolBValue": "Zapier action path (e.g., create lead vs create contact)", "direction": "B-to-A", "behavior": "auto-convert", "severity": "high", "notes": "Single Zap triggers same action for all event types by default.", "fixStrategy": "Add Filter by Zapier step. Route based on event_type.name field.", "mappedValues": []},
                {"id": "reschedule-dedup", "categoryId": "data-persistence", "fieldName": "Reschedule Creates Duplicate", "fieldType": "text", "toolAValue": "Calendly 'event.created' on initial + reschedule", "toolBValue": "Zapier creates 2 CRM records for same person", "direction": "B-to-A", "behavior": "silent-failure", "severity": "medium", "notes": "No 'rescheduled' event type in Calendly webhooks. Both initial and reschedule fire 'event.created'.", "fixStrategy": "Dedup by email in Zapier. Check existing record before creating.", "mappedValues": []}
            ],
            "errors": [
                {"errorSlug": "reschedule-duplicate", "errorName": "Rescheduled Event Creates Duplicate CRM Records", "categoryId": "data-persistence", "description": "Calendly sends event.created on reschedule. Zapier creates duplicate.", "fixSummary": "Dedup by email before creating."},
                {"errorSlug": "event-type-fanout", "errorName": "Single Event Type Action Limitation", "categoryId": "event-routing", "description": "All event types trigger same Zapier action.", "fixSummary": "Filter by event type name for different actions."}
            ]
        }
    },
    {
        "id": "make-to-slack",
        "name": "Make (Integromat) ↔ Slack Integration",
        "tool_a": "make", "tool_b": "slack",
        "sync_type": "Unidirectional (Make → Slack via Slack module in Make scenarios)",
        "popularity": "medium-high — Make's Slack module one of most popular, used for notifications from thousands of app integrations",
        "auth_a": "API Key per scenario (or OAuth per app). No rate limit per second, but monthly operation cap.",
        "auth_b": "OAuth 2.0 Bot Token (xoxb-). Scopes: chat:write, channels:read, files:write for file uploads.",
        "use_cases": [
            "Google Sheets row added → Make scenario → Slack channel notification",
            "Webhook received → Make transforms data → Slack message with Block Kit",
            "Database query results → Make aggregates → Slack daily report summary",
            "Multiple source events → Make dedup → Slack thread updates",
            "Error monitoring → Make catches → Slack alert with error details"
        ],
        "endpoints_a": [
            {"endpoint": "Make internal API (module-managed)", "method": "N/A", "purpose": "Make manages Slack API calls internally via Slack module"}
        ],
        "endpoints_b": [
            {"endpoint": "/chat.postMessage", "method": "POST", "purpose": "Send message to Slack channel"},
            {"endpoint": "/chat.update", "method": "POST", "purpose": "Update existing Slack message (for progress updates)"},
            {"endpoint": "/files.upload", "method": "POST", "purpose": "Upload file to Slack channel"},
            {"endpoint": "/conversations.info", "method": "GET", "purpose": "Get channel info to verify bot access"},
            {"endpoint": "/chat.postEphemeral", "method": "POST", "purpose": "Send ephemeral message to specific user"}
        ],
        "edge_cases": [
            {
                "error_code": "Slack rate limit in Make scenarios",
                "tool": "Slack",
                "category": "RATE_LIMIT",
                "cause": "Make scenario processes 50 items in a loop. Each iteration sends a Slack message. Slack 1 req/sec per method causes 429 after first request.",
                "solution": "Add 'Throttle' module in Make before Slack module. Set throttle to 1 second. Or aggregate messages and send one per batch."
            },
            {
                "error_code": "Make Slack module OAuth re-authentication",
                "tool": "Make",
                "category": "AUTH",
                "cause": "Make's Slack connection expires or Slack bot token revoked. Make scenario shows 'Connection Error'. Scenario stops processing silently.",
                "solution": "Set up Make scenario error handler route that sends email alert on connection error. Re-authenticate Slack connection in Make dashboard."
            },
            {
                "error_code": "Block Kit too complex for Make's JSON module",
                "tool": "Make",
                "category": "FORMATTING",
                "cause": "Make's JSON module struggles with nested Block Kit arrays. Missing comma or bracket breaks the entire Slack message.",
                "solution": "Build Block Kit JSON as a single text string using Make's 'set variable' module. Validate with Slack Block Kit Builder before production."
            },
            {
                "error_code": "Message aggregation with Map function array limit",
                "tool": "Make",
                "category": "DATA_TRANSFORM",
                "cause": "Make's Map function collects 200 items into array. Slack message with 200 items exceeds Slack block text limits. Static rendering fails.",
                "solution": "Chunk the array: send multiple messages for > 50 aggregated items. Or send file attachment instead of message."
            },
            {
                "error_code": "File upload size limit",
                "tool": "Slack",
                "category": "VALIDATION",
                "cause": "Make-generated file (CSV report, screenshot) > 1GB fails Slack upload. Slack silently rejects oversized files.",
                "solution": "Limit file size in Make scenario before upload. Compress files if needed. Use Slack's file upload limits guide."
            },
            {
                "error_code": "Slack channel archived — message fails",
                "tool": "Slack",
                "category": "CONFIGURATION",
                "cause": "Make scenario sends to channel that was archived by admin. Slacks returns 'is_archived' error. Scenario fails.",
                "solution": "Add error handler in Make to detect 'is_archived'. Route to different channel or notify admin."
            },
            {
                "error_code": "Scenario operation limit exhaustion",
                "tool": "Make",
                "category": "PLAN_LIMIT",
                "cause": "Each Slack message = 1 Make operation. High-volume scenarios exhaust Make monthly operation limit (e.g., 10K on Pro plan).",
                "solution": "Reduce Slack notification frequency. Aggregate messages. Use Make's data store to batch notifications."
            },
            {
                "error_code": "Slack webhook URL expiry",
                "tool": "Slack",
                "category": "CONFIGURATION",
                "cause": "Slack Incoming Webhook URLs can expire or be deactivated. Make's Slack module using legacy webhooks stops working.",
                "solution": "Migrate to Slack Bot Token (OAuth) instead of Incoming Webhooks. Bot tokens don't expire."
            }
        ],
        "community": [
            {"problem": "Make scenario execution time vs Slack rate limit", "solution": "Make async scenarios don't respect Slack per-method rate limits across parallel executions. Use serial processing for Slack.", "source": "Make community forum"},
            {"problem": "Slack message formatting with HTML in source data", "solution": "Strip HTML tags from source data in Make before sending to Slack. Use Make's 'replace' function with regex.", "source": "Make Slack module docs"}
        ],
        "keywords": [
            "Make Slack integration",
            "Make Integromat Slack notification",
            "Make Slack rate limit",
            "Make Slack message Block Kit",
            "Make scenario Slack connection error"
        ],
        "field_mappings": {
            "meta": {"toolA": "make", "toolB": "slack", "integrationSlug": "make-to-slack", "lastUpdated": "2026-06-26", "totalMappings": 3},
            "categories": [
                {"id": "loop-rate-limit", "name": "Loop Rate Limit", "description": "Make loop processing vs Slack 1 req/sec per method", "severity": "critical"},
                {"id": "blockkit-json", "name": "Block Kit JSON in Make", "description": "Make's JSON generation for Slack Block Kit", "severity": "high"},
                {"id": "connection-health", "name": "Connection Health & Re-auth", "description": "Make Slack connection expiry and monitoring", "severity": "medium"}
            ],
            "mappings": [
                {"id": "throttle-before-slack", "categoryId": "loop-rate-limit", "fieldName": "Slack Request Throttling in Loops", "fieldType": "text", "toolAValue": "Make loop: processes items as fast as possible", "toolBValue": "Slack: 1 req/sec per method per workspace", "direction": "A-to-B", "behavior": "warning", "severity": "critical", "notes": "Loop of 50 items sends 50 Slack requests in <1s. All after first get 429.", "fixStrategy": "Add Make 'Throttle' module set to 1 req/sec before Slack module. Or aggregate into one message.", "mappedValues": []},
                {"id": "json-array-format", "categoryId": "blockkit-json", "fieldName": "Block Kit JSON Array Construction", "fieldType": "object", "toolAValue": "Make JSON module outputs (may have trailing commas, mismatched brackets)", "toolBValue": "Slack Block Kit: strict JSON with no trailing commas", "direction": "A-to-B", "behavior": "warning", "severity": "high", "notes": "Make's JSON modules frequently produce invalid JSON for nested Block Kit structures.", "fixStrategy": "Build Block Kit as single text string. Validate JSON in Make before sending. Use Slack Block Kit Builder.", "mappedValues": []},
                {"id": "connection-monitoring", "categoryId": "connection-health", "fieldName": "Make Slack Connection Health", "fieldType": "text", "toolAValue": "Make Slack connection (OAuth, has expiry status)", "toolBValue": "Slack API: 401 on revoked token", "direction": "A-to-B", "behavior": "silent-failure", "severity": "medium", "notes": "Connection revoked → scenario silently stops processing Slack messages. No alert to user.", "fixStrategy": "Add Make error handler route that sends email/alternative notification on connection failure.", "mappedValues": []}
            ],
            "errors": [
                {"errorSlug": "loop-429-flood", "errorName": "Scenario Loop Floods Slack Rate Limit", "categoryId": "loop-rate-limit", "description": "Make loop without throttle exceeds Slack 1 req/sec.", "fixSummary": "Add Throttle module set to 1 second between requests."},
                {"errorSlug": "blockkit-json-invalid", "errorName": "Make JSON Module Produces Invalid Block Kit", "categoryId": "blockkit-json", "description": "Nested JSON arrays in Make have syntax errors.", "fixSummary": "Build as text string. Validate externally."}
            ]
        }
    },
    {
        "id": "activecampaign-to-slack",
        "name": "ActiveCampaign ↔ Slack Integration",
        "tool_a": "activecampaign", "tool_b": "slack",
        "sync_type": "Unidirectional (ActiveCampaign → Slack via ActiveCampaign's Slack integration, Zapier, or webhooks)",
        "popularity": "medium — ActiveCampaign automation triggers Slack notifications for sales/marketing teams",
        "auth_a": "API Token (Api-Key header). Webhook scopes: contacts, deals, automations.",
        "auth_b": "OAuth 2.0 Bot Token (xoxb-). Scopes: chat:write, channels:read.",
        "use_cases": [
            "ActiveCampaign form submission → Slack new lead alert",
            "ActiveCampaign deal 'Won' → Slack #closed-wins celebration message",
            "ActiveCampaign automation error → Slack #tech-alerts notification",
            "ActiveCampaign contact tag added → Slack assignee notification",
            "ActiveCampaign email bounce → Slack #support lead cleanup alert"
        ],
        "endpoints_a": [
            {"endpoint": "/webhooks", "method": "POST", "purpose": "Create webhook to trigger Slack on AC events"},
            {"endpoint": "/contacts/{id}", "method": "GET", "purpose": "Fetch contact details for Slack message"}
        ],
        "endpoints_b": [
            {"endpoint": "/chat.postMessage", "method": "POST", "purpose": "Send message to Slack channel"},
            {"endpoint": "/conversations.join", "method": "POST", "purpose": "Bot joins channel before posting"}
        ],
        "edge_cases": [
            {
                "error_code": "ActiveCampaign webhook payload format",
                "tool": "ActiveCampaign",
                "category": "WEBHOOK",
                "cause": "ActiveCampaign webhook payloads vary by event type. Contact webhook format differs from deal webhook. Slack message template breaks.",
                "solution": "Create separate Zapier/Make Zaps per webhook type. Each Zap has a Slack template matching the specific webhook payload."
            },
            {
                "error_code": "Slack 1 req/sec vs ActiveCampaign webhook burst",
                "tool": "Slack",
                "category": "RATE_LIMIT",
                "cause": "ActiveCampaign bulk tag update triggers webhooks for 100 contacts simultaneously. Middleware sends 100 Slack messages → 99 fail with 429.",
                "solution": "Queue in middleware. Send at 1 req/sec. Or send aggregated summary: '100 contacts tagged as X in AC'."
            },
            {
                "error_code": "ActiveCampaign API rate limit on webhook responses",
                "tool": "ActiveCampaign",
                "category": "RATE_LIMIT",
                "cause": "ActiveCampaign expects 200 response within 5s for webhooks. Slack rate limit causes middleware to delay. AC retries webhook.",
                "solution": "Acknowledge AC webhook immediately (200). Process Slack message asynchronously."
            },
            {
                "error_code": "Slack message too long with AC deal data",
                "tool": "Slack",
                "category": "VALIDATION",
                "cause": "ActiveCampaign deal with extensive notes and custom fields produces 10K+ character Slack message. Slack truncates at 4,000 chars per block.",
                "solution": "Truncate AC deal description to 500 chars in Slack message. Add 'View in ActiveCampaign' link for full deal details."
            },
            {
                "error_code": "AC webhook URL expires or changes",
                "tool": "ActiveCampaign",
                "category": "CONFIGURATION",
                "cause": "ActiveCampaign webhook URL changes when middleware URL changes. Old webhooks silently stop delivering events.",
                "solution": "Document all active webhook URLs in AC. Set up monitoring: if no Slack messages expected but not received, check webhook URLs."
            },
            {
                "error_code": "Escaped HTML in AC contact data",
                "tool": "ActiveCampaign",
                "category": "DATA_FORMAT",
                "cause": "ActiveCampaign stores certain fields with HTML entities (&amp; &lt; &gt;). Sent to Slack as raw text, rendering incorrectly.",
                "solution": "Decode HTML entities in middleware before sending to Slack: &amp; → &, &lt; → <, &gt; → >."
            },
            {
                "error_code": "Slack bot not in channel — silent drop",
                "tool": "Slack",
                "category": "PERMISSION",
                "cause": "Slack bot removed from channel by admin. Middleware sends message but Slack silently drops it. No error returned (permissions).",
                "solution": "Call conversations.join before each chat.postMessage. Or check bot channel membership periodically."
            },
            {
                "error_code": "Duplicate Slack alerts from AC webhook retries",
                "tool": "ActiveCampaign",
                "category": "WEBHOOK",
                "cause": "AC retries webhook delivery if first attempt not acknowledged quickly enough. Middleware receives duplicate events, sends duplicate Slack messages.",
                "solution": "Dedup by webhook event ID in middleware. Track processed event IDs in memory/data store."
            }
        ],
        "community": [
            {"problem": "AC webhook authentication header requirements", "solution": "AC webhooks send a basic auth-like header. Ensure middleware validates the signature to reject fake webhook calls.", "source": "ActiveCampaign webhook docs"},
            {"problem": "Slack mentions (@here, @channel) from AC automation", "solution": "ActiveCampaign deals with 'Urgent' tag → Slack @here notification. Risk of over-notification. Use @here only for 'Critical' severity.", "source": "r/Slack Slack admin best practices"}
        ],
        "keywords": [
            "ActiveCampaign Slack integration",
            "ActiveCampaign Slack notification",
            "ActiveCampaign webhook Slack",
            "ActiveCampaign automation Slack alert"
        ],
        "field_mappings": {
            "meta": {"toolA": "activecampaign", "toolB": "slack", "integrationSlug": "activecampaign-to-slack", "lastUpdated": "2026-06-26", "totalMappings": 3},
            "categories": [
                {"id": "payload-variation", "name": "Webhook Payload Variation", "description": "AC webhook payload format changes per event type", "severity": "high"},
                {"id": "burst-rate-limit", "name": "Burst Rate Limit", "description": "AC webhook bursts vs Slack rate limit", "severity": "critical"},
                {"id": "webhook-durability", "name": "Webhook Durability", "description": "AC webhook retries and URL changes", "severity": "medium"}
            ],
            "mappings": [
                {"id": "payload-format-variation", "categoryId": "payload-variation", "fieldName": "Webhook Payload Format Per Event", "fieldType": "object", "toolAValue": "AC contact webhook: {'contact':{'id':1,'email':'...'}}", "toolBValue": "AC deal webhook: {'deal':{'id':1,'title':'...','value':100}}", "direction": "A-to-B", "behavior": "silent-failure", "severity": "high", "notes": "Same middleware route handles both payload formats. One template breaks for the other event type.", "fixStrategy": "Separate routes per webhook type. Or use conditional template in middleware.", "mappedValues": []},
                {"id": "burst-queuing", "categoryId": "burst-rate-limit", "fieldName": "Bulk Tag/List Webhook Burst", "fieldType": "text", "toolAValue": "AC bulk action: 100 webhooks in <1 second", "toolBValue": "Slack: 1 req/sec per method per workspace", "direction": "A-to-B", "behavior": "warning", "severity": "critical", "notes": "Bulk tag addition triggers individual webhooks for each contact. All 100 fire within seconds.", "fixStrategy": "Queue in middleware. Rate-limit to 1 req/sec. Aggregate when > 10 items.", "mappedValues": []},
                {"id": "webhook-retry-dedup", "categoryId": "webhook-durability", "fieldName": "Webhook Retry Dedup", "fieldType": "text", "toolAValue": "AC webhook retry (same event, different delivery ID)", "toolBValue": "Slack: duplicate message if not deduped", "direction": "A-to-B", "behavior": "warning", "severity": "medium", "notes": "AC retries webhook if first response takes > 5s. Middleware processes both, sends 2 identical Slack messages.", "fixStrategy": "Dedup by AC webhook event ID in middleware. Use in-memory cache of processed IDs.", "mappedValues": []}
            ],
            "errors": [
                {"errorSlug": "webhook-format-breakage", "errorName": "AC Webhook Format Breaks Slack Template", "categoryId": "payload-variation", "description": "Contact webhook payload differs from deal webhook. Same template fails.", "fixSummary": "Separate routes per webhook event type."},
                {"errorSlug": "burst-slack-429", "errorName": "Bulk Tag Burst Exceeds Slack Rate Limit", "categoryId": "burst-rate-limit", "description": "100 simultaneous webhooks → 99 Slack 429 errors.", "fixSummary": "Queue + rate-limit to 1 req/sec. Aggregate."}
            ]
        }
    }
]

# ─── Generate the integration data JSON files ───
def generate_integration_files():
    print("=== Integration Pair Data Files ===")
    for pair in PAIRS:
        data = {
            "integration_id": pair["id"],
            "integration_name": pair["name"],
            "tool_a": {"tool_id": pair["tool_a"], "tool_name": TOOLS[pair["tool_a"]]["name"]},
            "tool_b": {"tool_id": pair["tool_b"], "tool_name": TOOLS[pair["tool_b"]]["name"]},
            "sync_type": pair["sync_type"],
            "popularity": pair["popularity"],
            "last_updated": "2026-06-26",
            "authentication_requirements": {
                f"{pair['tool_a']}_side": pair["auth_a"],
                f"{pair['tool_b']}_side": pair["auth_b"]
            },
            "common_use_cases": pair["use_cases"],
            "endpoints_involved": {
                f"{pair['tool_a']}_endpoints": pair["endpoints_a"],
                f"{pair['tool_b']}_endpoints": pair["endpoints_b"]
            },
            "edge_cases_and_errors": pair["edge_cases"],
            "community_solutions": pair["community"],
            "data_quality_score": None,
            "search_volume_keywords": pair["keywords"]
        }
        filepath = os.path.join(INT_DIR, f"{pair['id']}.json")
        write_json(filepath, data)

# ─── Generate field mapping JSON files ───
def generate_field_mapping_files():
    print("\n=== Field Mapping Data Files ===")
    for pair in PAIRS:
        fm = pair["field_mappings"]
        filepath = os.path.join(FM_DIR, f"{pair['id']}.json")
        write_json(filepath, fm)

# ─── Generate error content pages (Sprint 2) ───
def generate_page_files():
    print("\n=== Sprint 2 Error Pages ===")
    total_pages = 0
    for pair in PAIRS:
        tool_a = pair["tool_a"]
        tool_b = pair["tool_b"]
        path_a = os.path.join(CONTENT_DIR, tool_a)
        path_b = os.path.join(CONTENT_DIR, tool_b)
        os.makedirs(path_a, exist_ok=True)
        os.makedirs(path_b, exist_ok=True)

        for err in pair["edge_cases"][:3]:  # Top 3 errors per pair
            slug = to_slug(err["error_code"])
            error_type = "silent-failure" if "silently" in err.get("solution", "").lower() or "silent" in err.get("cause", "").lower() else "error"
            title = f"{err['error_code']} — {pair['name']} Fix"
            desc = err["cause"][:150]

            # Determine which tool the page belongs to
            tool_slug = tool_a
            if err["tool"] == TOOLS[tool_b]["name"]:
                tool_slug = tool_b
            elif err["tool"] == "Both":
                tool_slug = tool_a  # Default to tool_a

            content = f"""---
layout: ../../layouts/IntegrationErrorLayout.astro
title: "{title}"
description: "{desc}"
toolA: "{tool_a}"
toolB: "{tool_b}"
integrationSlug: "{pair['id']}"
errorSlug: "{slug}"
errorName: "{err['error_code']}"
category: "{err['category']}"
errorType: "{error_type}"
severity: "high"
priority: 2
lastUpdated: "2026-06-26"
---

## {err['error_code']}

**Tool**: {err['tool']}  |  **Category**: {err['category']}

### Cause

{err['cause']}

### Fix

{err['solution']}

### Prevention
- Test with single records before bulk operations
- Monitor error logs for this specific error code
- Add integration user field-level security audits to monthly checklist

### Related
- [{TOOLS[tool_a]['name']} API Reference](/{tool_a})
- [{TOOLS[tool_b]['name']} API Reference](/{tool_b})
"""
            filepath = os.path.join(CONTENT_DIR, tool_slug, f"int-{pair['id']}-{slug}.md")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  + {tool_slug}/int-{pair['id']}-{slug}.md")
            total_pages += 1

    print(f"\nTotal Sprint 2 error pages: {total_pages}")

# ─── Update master pipeline validation ───
def update_pipeline_reference():
    """Append field-mappings and content directories to the pipeline's validation scope."""
    pipeline_path = "scripts/seo-data-pipeline.ps1"
    if not os.path.exists(pipeline_path):
        return
    with open(pipeline_path, "r", encoding="utf-8") as f:
        content = f.read()
    if "field-mappings" not in content:
        print("\n⚠  Update pipeline to include field-mappings/ in validation")

# ─── Main ───
if __name__ == "__main__":
    generate_integration_files()
    generate_field_mapping_files()
    generate_page_files()
    update_pipeline_reference()
    print("\nDone. Sprint 2 pairs generated.")
