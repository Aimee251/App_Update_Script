import cloudscraper
import requests
from bs4 import BeautifulSoup
import time
import re

# APKPure apps — use cloudscraper to bypass Cloudflare
APKPURE_APPS = {
    "Instagram":  "https://apkpure.com/instagram-android-2025/com.instagram.android/versions",
    "Spotify":    "https://apkpure.com/spotify-music-and-podcasts/com.spotify.music/versions",
    "YouTube":    "https://apkpure.com/youtube/com.google.android.youtube/versions",
    "LyftDriver": "https://apkpure.com/lyft-driver/com.lyft.android.driver/versions",
    "Duolingo":   "https://apkpure.com/duolingo-language-chess/com.duolingo/versions",
    "WhatsApp":   "https://apkpure.com/whatsapp-messenger/com.whatsapp/versions",
    "Gmail":      "https://apkpure.com/gmail/com.google.android.gm/versions",
    "TikTok":     "https://apkpure.com/tiktok/com.zhiliaoapp.musically/versions",
}

# APKCombo apps — use regular requests
APKCOMBO_APPS = {
    "UberEats": "https://apkcombo.com/uber-eats/com.ubercab.eats/old-versions/",
    "PayPal":   "https://apkcombo.com/paypal-business/com.paypal.merchant.client/old-versions/",
    "Lyft":     "https://apkcombo.com/lyft/me.lyft.android/old-versions/",
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}

def get_release_notes_apkpure(scraper, detail_url):
    """Fetch release notes from APKPure version detail page"""
    try:
        r = scraper.get(detail_url, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        content = soup.select_one("div.whats-new-content p.content")
        if content:
            notes = content.get_text(separator=" ").strip()
            return re.sub(r"\s+", " ", notes).strip()
        return ""
    except:
        return ""

def get_apkpure_history(app_name, scraper):
    """Scrape version history + release notes from APKPure"""
    url = APKPURE_APPS[app_name]
    try:
        response = scraper.get(url, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        versions = []

        items = soup.select("div.ver-item")
        total = len(items)
        print(f"  Found {total} versions, fetching release notes...")

        for i, item in enumerate(items):
            version_el = item.select_one(".ver-item-n")
            date_el    = item.select_one(".update-on")
            link_el    = item.select_one("a")

            if not version_el:
                continue

            # Clean version number
            raw_version = version_el.text.strip()
            version_match = re.search(r"[\d]+[\d\.]+", raw_version)
            version_num = version_match.group(0) if version_match else raw_version

            # Get release notes from detail page
            detail_url = link_el.get("href") if link_el else None
            notes = ""
            if detail_url:
                print(f"    [{i+1}/{total}] v{version_num}...")
                notes = get_release_notes_apkpure(scraper, detail_url)
                time.sleep(0.5)

            # Data quality note
            if app_name == "LyftDriver":
                quality = "Using Lyft Driver Android app — matches iOS LyftDriver data. Lyft passenger app (me.lyft.android) was originally used for Android but replaced for consistency."
            else:
                quality = "Release notes from APKPure detail page (div.whats-new-content p.content)."

            versions.append({
                "app_name":           app_name,
                "platform":           "Android",
                "version":            version_num,
                "release_date":       date_el.text.strip() if date_el else "",
                "release_notes":      notes,
                "is_current":         "No",
                "source_url":         url,
                "data_quality_notes": quality,
            })

        if versions:
            versions[0]["is_current"] = "Yes"

        # Clean up
        for v in versions:
            v["version"]       = v["version"].replace("\n", " ").strip()
            v["release_date"]  = v["release_date"].replace("\n", " ").strip()
            v["release_notes"] = v["release_notes"].replace("\n", " ").strip()

        print(f"  Android {app_name}: done {len(versions)} versions")
        return versions

    except Exception as e:
        print(f"  Error fetching {app_name}: {e}")
        return []

def get_apkcombo_history(app_name):
    """Scrape version history from APKCombo"""
    url = APKCOMBO_APPS[app_name]
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        versions = []

        for item in soup.select("div.apks div.apk"):
            version_el = item.select_one(".name, h3, .apk-name")
            date_el    = item.select_one(".date, .update-date, time")
            notes_el   = item.select_one(".whats-new, .changelog, p")

            if not version_el:
                continue

            raw = version_el.text.strip()
            version_match = re.search(r"[\d]+[\d\.]+", raw)
            version_num = version_match.group(0) if version_match else raw

            versions.append({
                "app_name":           app_name,
                "platform":           "Android",
                "version":            version_num,
                "release_date":       date_el.text.strip() if date_el else "",
                "release_notes":      notes_el.text.strip() if notes_el else "",
                "is_current":         "No",
                "source_url":         url,
                "data_quality_notes": "Version data from APKCombo. Historical release notes may be limited.",
            })

        if versions:
            versions[0]["is_current"] = "Yes"

        for v in versions:
            v["version"]       = v["version"].replace("\n", " ").strip()
            v["release_date"]  = v["release_date"].replace("\n", " ").strip()
            v["release_notes"] = v["release_notes"].replace("\n", " ").strip()

        print(f"  Android {app_name} (APKCombo): done {len(versions)} versions")
        return versions

    except Exception as e:
        print(f"  Error fetching {app_name}: {e}")
        return []

def get_all_android():
    all_versions = []
    scraper = cloudscraper.create_scraper()

    # APKPure apps
    for app_name in APKPURE_APPS:
        print(f"Fetching Android (APKPure): {app_name}...")
        versions = get_apkpure_history(app_name, scraper)
        all_versions.extend(versions)
        time.sleep(2)

    # APKCombo apps
    for app_name in APKCOMBO_APPS:
        print(f"Fetching Android (APKCombo): {app_name}...")
        versions = get_apkcombo_history(app_name)
        all_versions.extend(versions)
        time.sleep(2)

    return all_versions

# Override the apkcombo function with fixed selectors
def get_apkcombo_history(app_name):
    """Scrape version history from APKCombo using cloudscraper"""
    url = APKCOMBO_APPS[app_name]
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        versions = []

        for item in soup.select("a.ver-item"):
            version_el = item.select_one("span.vername")
            # Date is in format "May 5, 2026 · Android 9.0+"
            info_el = item.select_one("div.info")

            if not version_el:
                continue

            # Clean version — extract just the number
            raw = version_el.text.strip()
            version_match = re.search(r"[\d]+[\d\.]+", raw)
            version_num = version_match.group(0) if version_match else raw

            # Extract date from info text
            date_text = ""
            if info_el:
                info_text = info_el.text.strip()
                date_match = re.search(
                    r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}",
                    info_text
                )
                if date_match:
                    date_text = date_match.group(0)

            versions.append({
                "app_name":           app_name,
                "platform":           "Android",
                "version":            version_num,
                "release_date":       date_text,
                "release_notes":      "",
                "is_current":         "No",
                "source_url":         url,
                "data_quality_notes": "Version data from APKCombo. No release notes available.",
            })

        if versions:
            versions[0]["is_current"] = "Yes"

        for v in versions:
            v["version"]      = v["version"].replace("\n", " ").strip()
            v["release_date"] = v["release_date"].replace("\n", " ").strip()

        print(f"  Android {app_name} (APKCombo): done {len(versions)} versions")
        return versions

    except Exception as e:
        print(f"  Error fetching {app_name}: {e}")
        return []
