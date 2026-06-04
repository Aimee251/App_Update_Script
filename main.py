import pandas as pd
from fetch_ios     import get_all_ios
from fetch_android import get_all_android
from categorize    import categorize_all
from export        import export_to_excel
from app_metadata  import APP_META

def main():

   
    print("=== Step 1: Fetching iOS version history ===")
    ios_data = get_all_ios()
    print(f"Total iOS versions collected: {len(ios_data)}")

   
    print("\n=== Step 2: Fetching Android version history ===")
    android_data = get_all_android()
    print(f"Total Android versions collected: {len(android_data)}")

  
    print("\n=== Step 3: Combining data ===")
    all_data = ios_data + android_data
    df = pd.DataFrame(all_data)

   
    print("\n=== Step 4: Adding metadata ===")
    df["developer"]            = df["app_name"].map(lambda x: APP_META.get(x, {}).get("developer", "Unknown"))
    df["category"]             = df["app_name"].map(lambda x: APP_META.get(x, {}).get("category", "Unknown"))
    df["initial_release_date"] = df.apply(lambda row:
        APP_META.get(row["app_name"], {}).get(
            "initial_release_ios" if row["platform"] == "iOS" else "initial_release_android", ""
        ), axis=1)

   
    df = df[[
        "app_name", "platform", "developer", "category",
        "version", "release_date", "is_current",
        "initial_release_date", "release_notes",
        "update_categories", "standardized_summary",
        "source_url", "data_quality_notes"
    ]]

    # Rename to match required field names
    df.columns = [
        "App Name", "Platform", "Developer / Company", "App Category",
        "Version Number", "Version Release Date", "Is Current Version",
        "Initial App Release Date", "Update Description / Release Notes",
        "Update Categories", "Standardized Summary",
        "Source URL", "Data Quality Notes"
    ]

    print(f"Total rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")


    print("\n=== Step 6: Categorizing with Claude API ===")
    df = categorize_all(df)

   
    print("\n=== Step 7: Exporting to Excel ===")
    export_to_excel(df, "app_updates_v2.xlsx")

    print("\n Done! Open app_updates.xlsx to see your results.")

if __name__ == "__main__":
    main()