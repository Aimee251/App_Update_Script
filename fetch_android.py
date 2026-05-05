import cloudscraper
from bs4 import BeautifulSoup
import time
import re

ANDROID_APPS = {
    "Instagram": "https://apkpure.com/instagram-android-2025/com.instagram.android/versions",
    "Spotify":   "https://apkpure.com/spotify-music-and-podcasts/com.spotify.music/versions",
    "YouTube":   "https://apkpure.com/youtube/com.google.android.youtube/versions",
    "Uber":      "https://apkpure.com/uber/com.ubercab/versions",
    "UberEats":  "https://apkpure.com/uber-eats-food-delivery/com.ubercab.eats/versions",
    "Duolingo":  "https://apkpure.com/duolingo-language-lessons/com.duolingo/versions",
    "WhatsApp":  "https://apkpure.com/whatsapp-messenger/com.whatsapp/versions",
    "Gmail":     "https://apkpure.com/gmail/com.google.android.gm/versions",
    "TikTok":    "https://apkpure.com/tiktok/com.zhiliaoapp.musically/versions",
    "PayPal":    "https://apkpure.com/paypal-mobile-cash/com.paypal.android.p2pmobile/versions",
}

def get_android_history(app_name):
    url = ANDROID_APPS[app_name]
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        versions = []

        for item in soup.select("div.ver-item"):
            version_el = item.select_one(".ver-item-n")
            date_el    = item.select_one(".update-on")
            notes_el   = item.select_one(".ver-des, .des, .desc, .info")

            if version_el:
                # Clean version — extract just the number
                raw_version = version_el.text.strip()
                # Extract version number like 428.0.0.47.67
                version_match = re.search(r"[\d]+[\d\.]+", raw_version)
                version_num = version_match.group(0) if version_match else raw_version

                versions.append({
                    "app_name":      app_name,
                    "platform":      "Android",
                    "version":       version_num,
                    "release_date":  date_el.text.strip() if date_el else "",
                    "release_notes": notes_el.text.strip() if notes_el else "",
                    "is_current":    "No",
                    "source_url":    url,
                })

        # Mark first as current
        if versions:
            versions[0]["is_current"] = "Yes"

        # Clean up all fields
        for v in versions:
            v["version"]       = v["version"].replace("\n", " ").strip()
            v["release_date"]  = v["release_date"].replace("\n", " ").strip()
            v["release_notes"] = v["release_notes"].replace("\n", " ").strip()

        print(f"  Android {app_name}: found {len(versions)} versions")
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
