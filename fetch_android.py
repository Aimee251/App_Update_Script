import requests
from bs4 import BeautifulSoup

# Each app needs its APKPure versions page URL
ANDROID_APPS = {
    "Instagram": "https://apkpure.com/instagram/com.instagram.android/versions",
    "Spotify":   "https://apkpure.com/spotify/com.spotify.music/versions",
    "YouTube":   "https://apkpure.com/youtube/com.google.android.youtube/versions",
    "Uber":      "https://apkpure.com/uber/com.ubercab/versions",
    "DoorDash":  "https://apkpure.com/doordash/com.dd.doordash/versions",
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
                    "version":       version_num.text.strip(),
                    "release_date":  release_date.text.strip() if release_date else "",
                    "release_notes": "",  # APKPure often needs a detail page per version
                    "source_url":    url,
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