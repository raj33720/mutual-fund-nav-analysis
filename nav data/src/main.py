import argparse
import os
import sys
import pandas as pd
from datetime import timedelta

# Constants
YEARS = 7                        # We want to analyze the last 7 years of NAV data
SWING_THRESHOLD_PERCENT = 5.0    # Flag NAV jumps greater than 5%

# Step 1: Read all NAV files from the data folder

def read_nav_files(data_dir: str) -> pd.DataFrame:
    """
    Reads every CSV file inside the given folder.
    Normalizes column names so they match 'Fund Name', 'Date', 'NAV'.
    Returns one combined DataFrame with all funds.
    """
    files = []
    for fname in os.listdir(data_dir):
        path = os.path.join(data_dir, fname)
        if fname.lower().endswith(".csv"):
            df = pd.read_csv(path)

            # Normalize column names (handle variations like 'Fund name', 'Net Asset Value')
            col_map = {}
            for col in df.columns:
                col_norm = col.strip().lower()
                if "fund" in col_norm:
                    col_map[col] = "Fund Name"
                elif "date" in col_norm:
                    col_map[col] = "Date"
                elif "nav" in col_norm:
                    col_map[col] = "NAV"

            df = df.rename(columns=col_map)
            df = df[["Fund Name", "Date", "NAV"]]  # Keep only the 3 required columns
            files.append(df)

    if not files:
        print(f"No CSV files found in {data_dir}", file=sys.stderr)
        sys.exit(1)

    # Combine all funds into one dataset
    df = pd.concat(files, ignore_index=True)

    # Clean data types
    df["Fund Name"] = df["Fund Name"].astype(str).str.strip()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["NAV"] = pd.to_numeric(df["NAV"], errors="coerce")

    # Drop bad rows and sort
    df = df.dropna().sort_values(by=["Fund Name", "Date"])
    return df


# Step 2: Filter NAV data to the last N years

def filter_last_n_years(df: pd.DataFrame, years: int) -> pd.DataFrame:
    """
    For each fund, keep only the NAV values from the last 'years' years.
    """
    out_frames = []
    for fund, g in df.groupby("Fund Name"):
        max_date = g["Date"].max()
        start_date = max_date - timedelta(days=365 * years)
        g_f = g[g["Date"] >= start_date].copy()
        out_frames.append(g_f)

    return pd.concat(out_frames, ignore_index=True).sort_values(by=["Fund Name", "Date"])


# Step 3: CAGR calculation

def compute_cagr(start_nav, end_nav, years):
    """
    CAGR formula:
    CAGR = (Ending NAV / Starting NAV)^(1/years) - 1
    """
    if start_nav <= 0:
        return None
    return (end_nav / start_nav) ** (1.0 / years) - 1.0

def compute_cagrs(df: pd.DataFrame, years: int):
    """
    Compute CAGR for each fund and return a sorted list.
    """
    results = []
    for fund, g in df.groupby("Fund Name"):
        start_nav = g.iloc[0]["NAV"]
        end_nav = g.iloc[-1]["NAV"]
        cagr = compute_cagr(start_nav, end_nav, years)
        if cagr is not None:
            results.append((fund, cagr))
    return sorted(results, key=lambda x: x[1], reverse=True)


# Step 4: Detect NAV swings > threshold

def detect_swings(df: pd.DataFrame, threshold_percent: float):
    """
    Look for NAV jumps greater than 'threshold_percent' between consecutive days.
    """
    events = []
    for fund, g in df.groupby("Fund Name"):
        g = g.sort_values("Date").reset_index(drop=True)
        for i in range(1, len(g)):
            prev_nav = g.loc[i-1, "NAV"]
            curr_nav = g.loc[i, "NAV"]
            change_pct = ((curr_nav - prev_nav) / prev_nav) * 100.0
            if change_pct > threshold_percent:
                events.append((fund, g.loc[i, "Date"].date(), prev_nav, curr_nav, change_pct))
    return events


# Step 5: Main program flow

def main():
    parser = argparse.ArgumentParser(description="Mutual Fund NAV Analysis")
    parser.add_argument("--data-dir", required=True, help="Path to folder containing NAV CSV files")
    args = parser.parse_args()

    # Load and clean data
    df_all = read_nav_files(args.data_dir)

    # Filter to last 7 years
    df_7y = filter_last_n_years(df_all, YEARS)

    # Compute CAGR rankings
    cagrs = compute_cagrs(df_7y, YEARS)
    print("\nTop 2 funds:")
    for fund, cagr in cagrs[:2]:
        print(f"{fund}: {cagr*100:.2f}%")

    print("\nWorst 2 funds:")
    for fund, cagr in cagrs[-2:]:
        print(f"{fund}: {cagr*100:.2f}%")

    # Detect NAV swings
    swings = detect_swings(df_7y, SWING_THRESHOLD_PERCENT)
    print("\nNAV swings > 5%:")
    for fund, date, prev, curr, pct in swings:
        print(f"{fund} | {date} | {prev:.2f} -> {curr:.2f} | +{pct:.2f}%")


# Entry point

if __name__ == "__main__":
    main()