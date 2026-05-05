import requests
from bs4 import BeautifulSoup

# Each app needs its ipa4fun URL
# Find it by searching the app name on ipa4fun.com
IOS_APPS = {
    "Instagram": "https://www.ipa4fun.com/history/871/",
    "Spotify":   "https://www.ipa4fun.com/history/1060/",
    "YouTube":   "https://www.ipa4fun.com/history/185230/",
    "Uber":      "https://www.ipa4fun.com/history/468/",
    "UberEats":  "https://www.ipa4fun.com/history/59778/",
    "Duolingo":   "https://www.ipa4fun.com/history/754/",
    "WhatsApp":  "https://www.ipa4fun.com/history/278/",
    "Gmail":     "https://www.ipa4fun.com/history/228/",
    "TikTok":    "https://www.ipa4fun.com/history/27847/",
    "PayPal":    "https://www.ipa4fun.com/history/1015/4/",
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def get_ios_history(app_name):
    url = IOS_APPS[app_name]
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        versions = []
        
        # Loop through each version block on the page
        # Note: inspect ipa4fun page in browser to confirm these selectors
        for block in soup.select(".app-version"):
            version_num  = block.select_one(".version-num")
            release_date = block.select_one(".date")
            notes        = block.select_one(".release-notes")
            
            if version_num:
                versions.append({
                    "app_name":      app_name,
                    "platform":      "iOS",
                    "version":       version_num.text.strip(),
                    "release_date":  release_date.text.strip() if release_date else "",
                    "release_notes": notes.text.strip() if notes else "",
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
    return all_versions