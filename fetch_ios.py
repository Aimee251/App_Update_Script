import requests
from bs4 import BeautifulSoup
import time
import re

IOS_APPS = {
    "Instagram": "https://www.ipa4fun.com/history/871/",
    "Spotify":   "https://www.ipa4fun.com/history/1060/",
    "YouTube":   "https://www.ipa4fun.com/history/185230/",
    "Uber":      "https://www.ipa4fun.com/history/468/",
    "UberEats":  "https://www.ipa4fun.com/history/59778/",
    "Duolingo":  "https://www.ipa4fun.com/history/754/",
    "WhatsApp":  "https://www.ipa4fun.com/history/278/",
    "Gmail":     "https://www.ipa4fun.com/history/228/",
    "TikTok":    "https://www.ipa4fun.com/history/27847/",
    "PayPal":    "https://www.ipa4fun.com/history/1015/",
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def get_ios_history(app_name):
    url = IOS_APPS[app_name]
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        versions = []

        # The version list is in <ol class="history"> > <li>
        history_ol = soup.select_one("ol.history")
        if not history_ol:
            print(f"  WARNING: No history list found for {app_name}")
            return []

        for li in history_ol.select("li"):
            # Version number from the link title
            a_tag = li.select_one("a[title]")
            if not a_tag:
                continue
            version_match = re.search(r"v([\d\.]+)", a_tag.get("title", ""))
            if not version_match:
                continue
            version_num = version_match.group(1)

            # Date from first <p class="app-desc"> 
            # e.g. "► Updated: April 21, 2026"
            date_text = ""
            all_desc = li.select("p.app-desc")
            if all_desc:
                raw_date = all_desc[0].text.strip()
                date_text = raw_date.replace("► Updated:", "").strip()

            # Release notes from <div class="info"> > <p>
            notes_text = ""
            info_div = li.select_one("div.info p")
            if info_div:
                notes_text = info_div.text.strip()

            # Is this the latest version?
            is_current = "Yes" if "(Latest Version)" in li.text else "No"

            versions.append({
                "app_name":      app_name,
                "platform":      "iOS",
                "version":       version_num,
                "release_date":  date_text,
                "release_notes": notes_text,
                "is_current":    is_current,
                "source_url":    url,
            })

        print(f"  iOS {app_name}: found {len(versions)} versions")
        return versions

    except Exception as e:
        print(f"  Error fetching iOS {app_name}: {e}")
        return []

def get_all_ios():
    all_versions = []
    for app_name in IOS_APPS:
        print(f"Fetching iOS: {app_name}...")
        versions = get_ios_history(app_name)
        all_versions.extend(versions)
        time.sleep(1)
    return all_versions
