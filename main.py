import pandas as pd
from fetch_ios     import get_all_ios
from fetch_android import get_all_android
from categorize    import categorize_all
from export        import export_to_excel

def main():
    
    # ── Step 1: Fetch iOS data ─────────────────────────────
    print("=== Step 1: Fetching iOS version history ===")
    ios_data = get_all_ios()
    print(f"Total iOS versions collected: {len(ios_data)}")

    # ── Step 2: Fetch Android data ─────────────────────────
    print("\n=== Step 2: Fetching Android version history ===")
    android_data = get_all_android()
    print(f"Total Android versions collected: {len(android_data)}")

    # ── Step 3: Combine into one DataFrame ─────────────────
    print("\n=== Step 3: Combining data ===")
    all_data = ios_data + android_data
    
    df = pd.DataFrame(all_data)
    
    # Add empty columns to fill in later
    df["update_categories"]    = ""
    df["standardized_summary"] = ""
    df["is_current"]           = "No"
    df["data_quality_notes"]   = ""
    
    print(f"Total rows combined: {len(df)}")
    print(f"Apps found: {df['app_name'].unique()}")

    # ── Step 4: Categorize with Claude API ─────────────────
    print("\n=== Step 4: Categorizing with Claude API ===")
    df = categorize_all(df)

    # ── Step 5: Export to Excel ────────────────────────────
    print("\n=== Step 5: Exporting to Excel ===")
    export_to_excel(df, "app_updates.xlsx")

    print("\nDone! Open app_updates.xlsx to see your results.")

if __name__ == "__main__":
    main()