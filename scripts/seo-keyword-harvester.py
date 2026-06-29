"""
SEO Keyword Harvester & Content Blueprint Generator
----------------------------------------------------
Reads the integration hub JSON database, generates:
  - Long-tail keyword variations (like HasData/python-for-seo)
  - PAA-style question trees
  - Intent-based clustering (like every-app/open-seo)
  - Priority-scored content blueprint

Usage:
  python scripts/seo-keyword-harvester.py
  python scripts/seo-keyword-harvester.py --cluster-only
  python scripts/seo-keyword-harvester.py --output blueprint
"""

import json
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ============================================================
# CONFIG
# ============================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"
INTEGRATIONS_DIR = DATA_DIR / "integrations"
OUTPUT_FILE = PROJECT_ROOT / "data" / "content-blueprint.json"

# ============================================================
# KEYWORD PATTERN GENERATORS (HasData/python-for-seo style)
# ============================================================

# Preposition chains for long-tail expansion
PREPOSITIONS = ["for", "in", "with", "to", "after", "when", "using", "via", "through"]
ERROR_PREFIXES = ["fix", "solve", "resolve", "handle", "avoid", "troubleshoot", "debug", "stop"]
QUESTION_PREFIXES = ["how to", "why do I get", "what causes", "how do I fix", "why is", "when does"]

# Tool name aliases for keyword variety
TOOL_ALIASES = {
    "hubspot": ["HubSpot", "Hubspot", "HS"],
    "salesforce": ["Salesforce", "SF", "SFDC"],
    "mailchimp": ["Mailchimp", "MailChimp", "MC"],
    "activecampaign": ["ActiveCampaign", "Active Campaign", "AC"],
    "pipedrive": ["Pipedrive", "PipeDrive", "PD"],
    "zapier": ["Zapier", "ZP"],
    "make": ["Make", "Make.com", "Integromat"],
    "zoho": ["Zoho CRM", "Zoho"],
    "slack": ["Slack"],
    "calendly": ["Calendly"]
}

def generate_keyword_variations(error_code, description, tool_name, tool_id):
    """Generate long-tail keyword variations for a single error."""
    variations = set()

    # 1. Direct error phrase
    variations.add(f"{tool_name} API {error_code}")
    variations.add(f"{tool_name} {error_code} {description[:60].split('.')[0]}")

    # 2. Error + fix patterns
    for prefix in ERROR_PREFIXES:
        variations.add(f"{prefix} {tool_name} {error_code}")
        variations.add(f"{prefix} {tool_name} API {error_code} {description[:40].split('.')[0]}")

    # 3. Question patterns
    for qp in QUESTION_PREFIXES:
        variations.add(f"{qp} {tool_name} return {error_code}")
        variations.add(f"{qp} {tool_name} API error {error_code}")

    # 4. Preposition chains
    for prep in PREPOSITIONS:
        variations.add(f"{tool_name} API {error_code} {prep} integration")
        variations.add(f"{error_code} error {tool_name} {prep} sync")
        variations.add(f"{tool_name} {error_code} {prep} {description[:30].lower()}")

    # 5. Integration context
    variations.add(f"{tool_name} API {error_code} integration fix")
    variations.add(f"sync error {tool_name} {error_code}")

    return list(variations)[:30]  # Cap at 30 per error


def generate_paa_questions(error_code, description, tool_name, solution_hint):
    """Generate People-Also-Ask style questions."""
    questions = []
    desc_short = description[:60].split('.')[0]

    question_templates = [
        f"Why does {tool_name} return {error_code}?",
        f"How to fix {tool_name} {error_code} {desc_short}?",
        f"What causes {tool_name} API {error_code} error?",
        f"Is {tool_name} {error_code} a rate limit or permissions error?",
        f"How do I resolve {tool_name} {error_code} during integration?",
        f"Can {tool_name} {error_code} cause data loss?",
        f"How long does {tool_name} {error_code} last?",
        f"Does {tool_name} {error_code} mean my token is expired?",
        f"What is the difference between {tool_name} {error_code} and {error_code[:3]}XX?",
        f"Will upgrading my {tool_name} plan fix {error_code}?",
    ]

    for qt in question_templates:
        questions.append({
            "question": qt,
            "answer": solution_hint[:120],
            "intent": "troubleshoot"
        })

    return questions


# ============================================================
# INTENT CLUSTERING (every-app/open-seo style)
# ============================================================

INTENT_CATEGORIES = {
    "rate_limit": ["429", "rate", "limit", "throttl", "too many", "concurrent", "burst"],
    "auth": ["401", "unauthorized", "token", "oauth", "auth", "session", "expired", "invalid_grant", "api_key", "apikey"],
    "permission": ["403", "forbidden", "scope", "permission", "role", "access denied"],
    "validation": ["400", "422", "bad request", "validation", "missing field", "invalid", "malformed"],
    "not_found": ["404", "not found", "does not exist", "resource unavailable"],
    "conflict": ["409", "conflict", "duplicate", "member exists", "already exists"],
    "server_error": ["500", "502", "503", "5xx", "server error", "internal", "unavailable", "service"],
    "data_format": ["format", "merge field", "picklist", "type mismatch", "character limit", "truncat"],
    "configuration": ["setup", "migration", "deprecated", "v1", "version", "endpoint", "migrate to"]
}

def classify_intent(error_code, description, solution):
    """Classify an error into intent category."""
    text = f"{error_code} {description} {solution}".lower()
    scores = {}
    for category, keywords in INTENT_CATEGORIES.items():
        score = sum(1 for kw in keywords if kw.lower() in text)
        if score > 0:
            scores[category] = score
    if not scores:
        return "general"
    return max(scores, key=scores.get)


# ============================================================
# MAIN ENGINE
# ============================================================

def load_all_data():
    """Load all tool and integration data."""
    tools = {}
    for f in DATA_DIR.glob("*-api-data.json"):
        if f.name == "master-integration-hub-index.json":
            continue
        data = json.loads(f.read_text(encoding="utf-8"))
        tools[data["tool_id"]] = data

    integrations = []
    if INTEGRATIONS_DIR.exists():
        for f in INTEGRATIONS_DIR.glob("*.json"):
            integrations.append(json.loads(f.read_text(encoding="utf-8")))

    return tools, integrations


def build_content_blueprint(tools, integrations):
    """Build the complete content blueprint with keyword data."""
    blueprint = {
        "generated": datetime.now().isoformat(),
        "source_data": {
            "tools": len(tools),
            "integration_pairs": len(integrations)
        },
        "pages": [],
        "clusters": defaultdict(list),
        "summary": {}
    }

    total_keywords = 0
    total_paa = 0

    # Process each tool's errors
    for tool_id, tool in tools.items():
        tool_name = tool["tool_name"]
        aliases = TOOL_ALIASES.get(tool_id, [tool_name])

        for error in tool.get("error_dictionary", []):
            error_code = error["error_code"]
            description = error.get("description", "")
            solution = error.get("solution", "")
            category = classify_intent(error_code, description, solution)

            keywords = generate_keyword_variations(
                error_code, description, tool_name, tool_id
            )
            questions = generate_paa_questions(
                error_code, description, tool_name, solution
            )

            total_keywords += len(keywords)
            total_paa += len(questions)

            page = {
                "type": "error",
                "tool_id": tool_id,
                "tool_name": tool_name,
                "error_code": error_code,
                "category": category,
                "title": f"How to Fix {tool_name} API {error_code} Error: {description[:80]}",
                "meta_description": f"Learn what causes the {tool_name} API {error_code} error and how to fix it. {solution[:100]}",
                "keywords": keywords[:15],
                "questions": questions[:8],
                "solution_summary": solution[:200],
                "priority_score": _calculate_priority(category, error_code)
            }

            blueprint["pages"].append(page)
            blueprint["clusters"][category].append(page["title"])

    # Add integration pages
    for int_pair in integrations:
        for error in int_pair.get("edge_cases_and_errors", []):
            error_code = error.get("error_code", "N/A")
            description = error.get("cause", "")
            solution = error.get("solution", "")
            tool_a = int_pair["tool_a"]["tool_name"]
            tool_b = int_pair["tool_b"]["tool_name"]
            combined_name = f"{tool_a} to {tool_b}"
            category = classify_intent(error_code, description, solution)

            keywords = generate_keyword_variations(error_code, description, combined_name, int_pair["integration_id"])
            questions = generate_paa_questions(error_code, description, combined_name, solution)

            total_keywords += len(keywords)
            total_paa += len(questions)

            page = {
                "type": "integration_error",
                "integration_id": int_pair["integration_id"],
                "tool_a": tool_a,
                "tool_b": tool_b,
                "error_code": error_code,
                "category": category,
                "title": f"Fix {tool_a} to {tool_b} Integration Error {error_code}: {description[:80]}",
                "meta_description": f"Troubleshoot {error_code} error in {tool_a}-{tool_b} sync. {solution[:100]}",
                "keywords": keywords[:15],
                "questions": questions[:8],
                "solution_summary": solution[:200],
                "priority_score": _calculate_priority(category, error_code) + 0.5
            }

            blueprint["pages"].append(page)

    # Convert clusters from defaultdict to dict
    blueprint["clusters"] = dict(blueprint["clusters"])

    # Summary stats
    priority_groups = {"high": 0, "medium": 0, "standard": 0}
    for p in blueprint["pages"]:
        if p["priority_score"] >= 8:
            priority_groups["high"] += 1
        elif p["priority_score"] >= 5:
            priority_groups["medium"] += 1
        else:
            priority_groups["standard"] += 1

    blueprint["summary"] = {
        "total_pages": len(blueprint["pages"]),
        "total_keywords_generated": total_keywords,
        "total_paa_questions": total_paa,
        "intent_clusters": {k: len(v) for k, v in blueprint["clusters"].items()},
        "pages_by_priority": priority_groups,
        "recommended_build_order": sorted(blueprint["pages"], key=lambda x: -x["priority_score"])[:10]
    }

    return blueprint


def _calculate_priority(category, error_code):
    """Calculate priority score 1-10 based on category and error code."""
    # High priority: auth + rate limit errors (most searched)
    base_scores = {
        "auth": 9,
        "rate_limit": 8.5,
        "permission": 8,
        "validation": 7,
        "data_format": 7,
        "configuration": 6.5,
        "conflict": 6,
        "not_found": 5,
        "server_error": 5,
        "general": 4
    }
    boost = 0
    # 401, 403, 429 have highest search volume
    if error_code in ["401", "403", "429"]:
        boost = 1.5
    elif error_code in ["400", "422", "409"]:
        boost = 0.5
    elif error_code in ["500", "502", "503"]:
        boost = 0.3
    return min(base_scores.get(category, 4) + boost, 10)


def save_blueprint(blueprint):
    """Save the content blueprint to JSON."""
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(blueprint, f, indent=2, ensure_ascii=False)
    print(f"[+] Content blueprint saved: {OUTPUT_FILE}")


def print_summary(blueprint):
    """Print a human-readable summary."""
    s = blueprint["summary"]
    print("\n" + "=" * 60)
    print("CONTENT BLUEPRINT SUMMARY")
    print("=" * 60)
    print(f"  Total pages:          {s['total_pages']}")
    print(f"  Keywords generated:   {s['total_keywords_generated']}")
    print(f"  PAA questions:        {s['total_paa_questions']}")
    print(f"\n  Intent clusters:")
    for cat, count in s['intent_clusters'].items():
        print(f"    {cat:20s}: {count} pages")
    print(f"\n  Pages by priority:")
    for group, count in s['pages_by_priority'].items():
        print(f"    {group:10s}: {count}")
    print(f"\n  TOP 10 RECOMMENDED PAGES (build these first):")
    for i, page in enumerate(s['recommended_build_order'][:10], 1):
        print(f"  {i:2d}. [{page['priority_score']}] {page['title'][:80]}")
    print("=" * 60)
    print(f"  Full blueprint: {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    import sys

    print("[*] Loading integration hub data...")
    tools, integrations = load_all_data()
    print(f"    {len(tools)} tools, {len(integrations)} integration pairs loaded")

    print("[*] Generating keywords, PAA questions, and clustering...")
    blueprint = build_content_blueprint(tools, integrations)

    save_blueprint(blueprint)
    print_summary(blueprint)

    if "--cluster-only" in sys.argv:
        print("\n[CLUSTERS]")
        for cat, pages in blueprint["clusters"].items():
            print(f"\n  [{cat.upper()}]")
            for p in pages[:5]:
                print(f"    - {p}")
