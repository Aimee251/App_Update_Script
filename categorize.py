import anthropic
import json
import time
import re
import os
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

CATEGORIES = [
    "Bug fixes / performance improvements",
    "UI / design changes",
    "Privacy / data policy changes",
    "AI-related features",
    "Payments / monetization",
    "Personalization / recommendations",
    "Security / account safety",
    "SDK / API / developer integration",
    "New product feature",
    "Other"
]

SKIP_PHRASES = [
    "we're always making changes",
    "we update our app",
    "minor bug fixes",
    "stability improvements",
]

def rule_based_categorize(release_notes):
    """Fast keyword matching — used when notes are empty or generic"""
    if not release_notes or str(release_notes).strip() in ["", "nan"]:
        return ["Other"]
    n = str(release_notes).lower()
    cats = []
    if any(w in n for w in ["bug","fix","crash","performance","stability",
                             "optimiz","faster","smooth","reliable","squash","speed"]):
        cats.append("Bug fixes / performance improvements")
    if any(w in n for w in ["ui","design","layout","interface","visual",
                             "dark mode","icon","theme","redesign"]):
        cats.append("UI / design changes")
    if any(w in n for w in ["privacy","data policy","permission","gdpr",
                             "tracking","consent","personal information"]):
        cats.append("Privacy / data policy changes")
    if any(w in n for w in ["ai","artificial intelligence","machine learning",
                             "smart","generative","gpt","gemini","assistant"]):
        cats.append("AI-related features")
    if any(w in n for w in ["pay","payment","purchase","subscri","checkout",
                             "billing","wallet","transaction","commerce"]):
        cats.append("Payments / monetization")
    if any(w in n for w in ["personal","custom","prefer","recommendation",
                             "for you","feed","suggest","tailor"]):
        cats.append("Personalization / recommendations")
    if any(w in n for w in ["security","safe","protect","encrypt","login",
                             "password","authenticat","verif","2fa"]):
        cats.append("Security / account safety")
    if any(w in n for w in ["sdk","api","developer","integration",
                             "third-party","library","framework"]):
        cats.append("SDK / API / developer integration")
    if any(w in n for w in ["new feature","introducing","launch","now you can",
                             "we've added","announcing","added support"]):
        cats.append("New product feature")
    if not cats:
        cats.append("Other")
    return cats

def is_generic_notes(notes):
    """Check if notes are too generic to send to API"""
    if not notes or str(notes).strip() in ["", "nan"]:
        return True
    if len(str(notes).strip()) < 20:
        return True
    for phrase in SKIP_PHRASES:
        if phrase in str(notes).lower():
            return True
    return False

def categorize_update(app_name, platform, version, release_notes):
    """Categorize one update — uses API if notes are substantive, rules otherwise"""

    # Skip API for empty or generic notes
    if is_generic_notes(release_notes):
        cats = rule_based_categorize(release_notes)
        return {
            "categories": cats,
            "standardized_summary": f"Generic update — no specific details disclosed in release notes."
        }

    prompt = f"""Analyze this mobile app update. Respond with JSON only, no other text.

App: {app_name} ({platform})
Version: {version}
Release Notes: {release_notes}

Choose ALL applicable categories from:
{json.dumps(CATEGORIES, indent=2)}

Return ONLY this JSON format:
{{
  "categories": ["Category 1", "Category 2"],
  "standardized_summary": "1-2 sentence structured summary suitable for data analysis."
}}"""

    for attempt in range(3):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = re.sub(r"```json|```", "", response.content[0].text.strip()).strip()
            if not raw:
                time.sleep(1)
                continue
            result = json.loads(raw)
            valid_cats = [c for c in result["categories"] if c in CATEGORIES]
            if not valid_cats:
                valid_cats = rule_based_categorize(release_notes)
            return {
                "categories": valid_cats,
                "standardized_summary": result.get("standardized_summary", "")
            }
        except json.JSONDecodeError:
            time.sleep(1)
            continue
        except Exception as e:
            print(f"    API error: {e}")
            time.sleep(2)
            continue

    # All attempts failed — fall back to rules
    return {
        "categories": rule_based_categorize(release_notes),
        "standardized_summary": f"Categorized by keyword matching (API unavailable)."
    }


def categorize_all(df):
    total = len(df)
    api_count  = 0
    rule_count = 0
    print(f"\nCategorizing {total} entries...")

    # Handle both old and new column names
    app_col   = "App Name"      if "App Name"      in df.columns else "app_name"
    plat_col  = "Platform"      if "Platform"      in df.columns else "platform"
    ver_col   = "Version Number" if "Version Number" in df.columns else "version"
    notes_col = "Update Description / Release Notes" if "Update Description / Release Notes" in df.columns else "release_notes"
    cats_col  = "Update Categories"    if "Update Categories"    in df.columns else "update_categories"
    summ_col  = "Standardized Summary" if "Standardized Summary" in df.columns else "standardized_summary"

    for idx, row in df.iterrows():
        notes = str(row[notes_col]) if row[notes_col] == row[notes_col] else ""
        print(f"  [{idx+1}/{total}] {row[app_col]} {row[plat_col]} v{row[ver_col]}", end="")

        if is_generic_notes(notes):
            print(" (rule-based)")
            rule_count += 1
        else:
            print(" (Claude API)")
            api_count += 1

        result = categorize_update(
            app_name      = row[app_col],
            platform      = row[plat_col],
            version       = str(row[ver_col]),
            release_notes = notes
        )

        df.at[idx, cats_col] = ", ".join(result["categories"])
        df.at[idx, summ_col] = result["standardized_summary"]

        # Only sleep when using API
        if not is_generic_notes(notes):
            time.sleep(0.3)

    print(f"\nDone! Claude API used: {api_count} times | Rule-based: {rule_count} times")
    return df
