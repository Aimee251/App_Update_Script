import pandas as pd
from export import export_to_excel

df = pd.read_excel("app_updates.xlsx")
print("Before cleanup:", df.shape)

# Convert column to string type first
df['data_quality_notes'] = df['data_quality_notes'].astype(str)

# Fix data_quality_notes
df.loc[df['platform'] == 'Android', 'data_quality_notes'] = \
    "Historical release notes not available - Android apps do not publish changelogs publicly"

df.loc[df['platform'] == 'iOS', 'data_quality_notes'] = \
    "Release notes sourced from ipa4fun.com version history page"

# Fix is_current
df['release_date_parsed'] = pd.to_datetime(df['release_date'], errors='coerce')

for app_name in df['app_name'].unique():
    for platform in ['iOS', 'Android']:
        mask = (df['app_name'] == app_name) & (df['platform'] == platform)
        subset = df[mask]
        if len(subset) > 0:
            df.loc[mask, 'is_current'] = 'No'
            latest_idx = subset['release_date_parsed'].idxmax()
            df.at[latest_idx, 'is_current'] = 'Yes'

df = df.drop(columns=['release_date_parsed'])

print("After cleanup:", df.shape)
print("\nis_current distribution:")
print(df['is_current'].value_counts())

export_to_excel(df, "app_updates_final.xlsx")
print("\nDone! Open app_updates_final.xlsx")
