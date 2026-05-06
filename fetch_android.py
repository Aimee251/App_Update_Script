import cloudscraper
from bs4 import BeautifulSoup
import time
import re

ANDROID_APPS = {
    "Instagram": "https://apkpure.com/instagram-android-2025/com.instagram.android/versions",
    "Spotify":   "https://apkpure.com/spotify-music-and-podcasts/com.spotify.music/versions",
    "YouTube":   "https://apkpure.com/youtube/com.google.android.youtube/versions",
    "Uber":      "https://apkpure.com/uber-request-a-ride/com.ubercab/versions",
    "UberEats":  "https://apkpure.com/uber-eats-food-and-grocery/com.ubercab.eats/versions",
    "Duolingo":  "https://apkpure.com/duolingo-language-chess/com.duolingo/versions",
    "WhatsApp":  "https://apkpure.com/whatsapp-messenger/com.whatsapp/versions",
    "Gmail":     "https://apkpure.com/gmail/com.google.android.gm/versions",
    "TikTok":    "https://apkpure.com/tiktok/com.zhiliaoapp.musically/versions",
    "PayPal":    "https://apkpure.com/paypal-pay-send-save/com.paypal.android.p2pmobile/versions",
}

def get_release_notes(scraper, detail_url):
    try:
        r = scraper.get(detail_url, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        content = soup.select_one('div.whats-new-content p.content')
        if content:
            notes = content.get_text(separator=' ').strip()
            return re.sub(r'\s+', ' ', notes).strip()
        return ""
    except Exception as e:
        return ""

def get_android_history(app_name):
    url = ANDROID_APPS[app_name]
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        versions = []

        items = soup.select('div.ver-item')
        total = len(items)
        print(f"  Found {total} versions, fetching release notes...")

        for i, item in enumerate(items):
            version_el = item.select_one('.ver-item-n')
            date_el    = item.select_one('.update-on')
            link_el    = item.select_one('a')

            if not version_el:
                continue

            raw_version = version_el.text.strip()
            version_match = re.search(r'[\d]+[\d\.]+', raw_version)
            version_num = version_match.group(0) if version_match else raw_version

            detail_url = link_el.get('href') if link_el else None
            notes = ""
            if detail_url:
                print(f"    [{i+1}/{total}] v{version_num}...")
                notes = get_release_notes(scraper, detail_url)
                time.sleep(0.5)

            versions.append({
                "app_name":      app_name,
                "platform":      "Android",
                "version":       version_num,
                "release_date":  date_el.text.strip() if date_el else "",
                "release_notes": notes,
                "is_current":    "No",
                "source_url":    url,
            })

        if versions:
            versions[0]["is_current"] = "Yes"

        for v in versions:
            v["version"]       = v["version"].replace("\n", " ").strip()
            v["release_date"]  = v["release_date"].replace("\n", " ").strip()
            v["release_notes"] = v["release_notes"].replace("\n", " ").strip()

        print(f"  Android {app_name}: done {len(versions)} versions")
        return versions

    except Exception as e:
        print(f"  Error fetching Android {app_name}: {e}")
        return []

def get_all_android():
    all_versions = []
    for app_name in ANDROID_APPS:
        print(f"Fetching Android: {app_name}...")
        versions = get_android_history(app_name)
        all_versions.extend(versions)
        time.sleep(2)
    return all_versions
