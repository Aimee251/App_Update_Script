import requests
from bs4 import BeautifulSoup
import time
import re

IOS_APPS = {
    "Instagram":  "https://www.ipa4fun.com/history/871/",
    "Spotify":    "https://www.ipa4fun.com/history/1060/",
    "YouTube":    "https://www.ipa4fun.com/history/185230/",
    "LyftDriver": "https://www.ipa4fun.com/history/111511/",
    "UberEats":   "https://www.ipa4fun.com/history/59778/",
    "Duolingo":   "https://www.ipa4fun.com/history/754/",
    "WhatsApp":   "https://www.ipa4fun.com/history/278/",
    "Gmail":      "https://www.ipa4fun.com/history/228/",
    "TikTok":     "https://www.ipa4fun.com/history/27847/",
    "PayPal":     "https://www.ipa4fun.com/history/1015/",
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}
MAX_PAGES = 10

def get_ios_history_page(app_name, url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        versions = []

        history_ol = soup.select_one("ol.history")
        if not history_ol:
            return versions, None

        for li in history_ol.select("li"):
            a_tag = li.select_one("a[title]")
            if not a_tag:
                continue
            version_match = re.search(r"v([\d\.]+)", a_tag.get("title", ""))
            if not version_match:
                continue
            version_num = version_match.group(1)

            # Date
            date_text = ""
            all_desc = li.select("p.app-desc")
            if all_desc:
                date_text = all_desc[0].text.strip().replace("► Updated:", "").strip()

            # Release notes
            notes_text = ""
            info_div = li.select_one("div.info p")
            if info_div:
                notes_text = info_div.text.strip()

            is_current = "Yes" if "(Latest Version)" in li.text else "No"

            # Data quality note for LyftDriver
            quality_note = ""
            if app_name == "LyftDriver":
                quality_note = (
                    "Using Lyft Driver iOS app — Lyft passenger iOS history page "
                    "(ipa4fun.com/history/154/) returns 404. "
                    "Android data uses Lyft passenger app (me.lyft.android)."
                )
            else:
                quality_note = "Release notes sourced from ipa4fun.com version history page."

            versions.append({
                "app_name":           app_name,
                "platform":           "iOS",
                "version":            version_num,
                "release_date":       date_text,
                "release_notes":      notes_text,
                "is_current":         is_current,
                "source_url":         url,
                "data_quality_notes": quality_note,
            })

        # Find next page
        next_page = None
        current = soup.select_one("span.page-numbers.current")
        if current:
            try:
                current_num = int(current.text.strip())
                next_num = current_num + 1
                base_url = url.rstrip("/")
                # Remove current page number from URL if present
                base_url = re.sub(r'/\d+$', '', base_url)
                next_page = f"{base_url}/{next_num}/"
            except:
                pass

        return versions, next_page

    except Exception as e:
        print(f"  Error on page {url}: {e}")
        return [], None


def get_ios_history(app_name):
    base_url = IOS_APPS[app_name]
    all_versions = []
    current_url = base_url
    page_num = 1

    while current_url and page_num <= MAX_PAGES:
        print(f"  Fetching page {page_num}/{MAX_PAGES}: {current_url}")
        versions, next_url = get_ios_history_page(app_name, current_url)
        all_versions.extend(versions)
        print(f"    Got {len(versions)} versions on this page")

        if not next_url or not versions:
            break

        current_url = next_url
        page_num += 1
        time.sleep(1)

    print(f"  iOS {app_name}: total {len(all_versions)} versions across {page_num} pages")
    return all_versions


def get_all_ios():
    all_versions = []
    for app_name in IOS_APPS:
        print(f"Fetching iOS: {app_name}...")
        versions = get_ios_history(app_name)
        all_versions.extend(versions)
        time.sleep(1)
    return all_versions
