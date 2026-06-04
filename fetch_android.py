import requests
from bs4 import BeautifulSoup

# Each app needs its APKPure versions page URL
ANDROID_APPS = {
    "Instagram": "https://apkpure.com/instagram-android-2025/com.instagram.android/versions",
    "Spotify":   "https://apkpure.com/spotify-music-and-podcasts-for-android-2025/com.spotify.music/versions",
    "YouTube":   "https://apkpure.com/youtube-2025/com.google.android.youtube/versions",

    "Lyft":      "https://apkpure.com/lyft/me.lyft.android/versions",
    # use apkcombo instead
    "UberEats":  "https://apkcombo.com/uber-eats/com.ubercab.eats/old-versions/",

    "Duolingo":  "https://apkpure.com/duolingo-language-chess/com.duolingo/versions",
    "WhatsApp":  "https://apkpure.com/whatsapp-android/com.whatsapp/versions",
    "Gmail":     "https://apkpure.com/gmail/com.google.android.gm/versions",
    "TikTok":    "https://apkpure.com/tiktok-musically-2025/com.zhiliaoapp.musically/versions",
    # use apkcombo instead
    "PayPal":    "",
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def get_android_history(app_name):
    url = ANDROID_APPS[app_name]
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        versions = []
        
        # Loop through version rows
        # Note: inspect APKPure page in browser to confirm selectors
        for row in soup.select(".ver-wrap"):
            version_num  = row.select_one(".ver-item-n")
            release_date = row.select_one(".ver-item-t")
            
            if version_num:
                versions.append({
    "app_name":      app_name,
    "platform":      "Android",
    "version":       version_num,
    "release_date":  date_el.text.strip() if date_el else "",
    "release_notes": "",  # APKPure does not store release notes
    "is_current":    "No",
    "source_url":    url,
    "data_quality_notes": "Release notes not available on APKPure version history page",
})

        
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
    return all_versions