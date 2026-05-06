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
MAX_PAGES = 10

def get_ios_history_page(app_name, url):
    """Scrape one page of version history"""
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

            versions.append({
                "app_name":      app_name,
                "platform":      "iOS",
                "version":       version_num,
                "release_date":  date_text,
                "release_notes": notes_text,
                "is_current":    is_current,
                "source_url":    url,
            })

        # Find next page URL
        next_page = None
        pagination = soup.select("a.page-numbers")
        for a in pagination:
            if "Next" in a.text or "»" in a.text:
                next_page = a.get("href")
                if next_page and not next_page.startswith("http"):
                    next_page = "https://www.ipa4fun.com" + next_page
                break

        # Also check for numbered pages
        if not next_page:
            current = soup.select_one("span.page-numbers.current")
            if current:
                try:
                    current_num = int(current.text.strip())
                    next_num = current_num + 1
                    # Build next page URL
                    base_url = url.rstrip("/")
                    if f"/{current_num}" in base_url:
                        next_page = base_url.replace(f"/{current_num}", f"/{next_num}") + "/"
                    else:
                        next_page = base_url + f"/{next_num}/"
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
        time.sleep(1)  # be polite

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
