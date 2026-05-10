"""
fetch_children_population.py  (v2 — bulk CSV, no API key needed)
================================================================
Fetches disaggregated school-age children population data from the
UN World Population Prospects 2024 bulk CSV files.

WHY THIS APPROACH
-----------------
The WPP REST API (/dataportalapi/...) now requires an Azure subscription
key that is not publicly documented. The bulk CSV files on population.un.org
are the official recommended alternative — same data, no auth required.

SOURCE FILE
-----------
WPP2024_PopulationByAge5GroupSex_Medium.zip
  → Contains population estimates 1950–2024 + projections 2025–2100
  → Rows: one per (country × year × sex × 5-year age group)
  → ~2.3 million rows total (~150 MB unzipped) — we stream + filter

HOW TO GET THE SUBSCRIPTION KEY (if you prefer the API later)
--------------------------------------------------------------
1. Visit https://population.un.org/dataportal/
2. Click "Data API" in the top nav
3. Register / log in → go to your profile → "Subscriptions"
4. Subscribe to the WPP product → copy your Ocp-Apim-Subscription-Key
5. Use it as:  headers={"Ocp-Apim-Subscription-Key": "<your_key>"}

Install:  pip install requests pandas
Usage:    python fetch_children_population.py
Output:
    children_data/
        children_schoolage_raw.csv     all school-age bands, all target countries
        children_schoolage_summary.csv  pivot: country × year × sex × level
"""

import io
import os
import time
import zipfile

import pandas as pd
import requests

OUT_DIR = "children_data"
os.makedirs(OUT_DIR, exist_ok=True)

# ── Bulk CSV download URL (WPP 2024, Medium variant) ─────────────────────────
# Source: https://population.un.org/wpp/downloads
# File: "Population by 5-year age group and sex" → Medium variant ZIP
WPP_CSV_URL = (
    "https://population.un.org/wpp/assets/Excel%20Files/"
    "1_Indicator%20(Standard)/CSV_FILES/"
    "WPP2024_PopulationByAge5GroupSex_Medium.zip"
)

# ── Countries of interest (ISO3 codes) ───────────────────────────────────────
TARGET_ISO3 = {
    # Sub-Saharan Africa
    "SOM", "ETH", "SDN", "SSD", "NGA", "MLI", "BFA", "TCD",
    "CAF", "COD", "MOZ", "KEN", "UGA", "GHA", "CMR",
    # Middle East
    "YEM", "SYR", "IRQ", "AFG", "PSE", "LBN", "LBY",
    # SE Asia
    "MMR", "PAK", "KHM", "PHL", "BGD", "THA", "VNM",
}

# ── Year range of interest ────────────────────────────────────────────────────
START_YEAR = 2000
END_YEAR   = 2024    # 2024 is the last estimate year; beyond is projection

# ── School-age bands (5-year WPP groups) ─────────────────────────────────────
# Primary school age  ≈ 6–11  →  nearest 5-yr bands: 5-9 and 10-14
# Secondary school age ≈ 12–17 → nearest 5-yr bands: 10-14 and 15-19
# We keep all four bands and let the user combine as needed
SCHOOL_AGE_BANDS = {"5-9", "10-14", "15-19"}   # also useful: "0-4" for under-5

# Sex codes in WPP CSV: 1=Male, 2=Female, 3=Both sexes
SEX_LABELS = {1: "Male", 2: "Female", 3: "Both"}

HEADERS = {"User-Agent": "school-age-research/1.0"}


def download_zip_to_memory(url: str) -> bytes:
    """Stream-download a ZIP file into memory with progress display."""
    print(f"Downloading WPP bulk CSV...")
    print(f"  {url}")
    r = requests.get(url, headers=HEADERS, stream=True, timeout=300)
    if r.status_code == 403:
        print("\n⚠  population.un.org returned 403.")
        print("   The file may have moved. Check the current URL at:")
        print("   https://population.un.org/wpp/downloads")
        print("   Look for: 'Population by 5-year age group and sex' → CSV ZIP\n")
        raise SystemExit(1)
    r.raise_for_status()

    total = int(r.headers.get("content-length", 0))
    chunks = []
    done = 0
    for chunk in r.iter_content(chunk_size=1 << 20):   # 1 MB chunks
        chunks.append(chunk)
        done += len(chunk)
        if total:
            pct = done / total * 100
            print(f"  {done/1e6:.0f} / {total/1e6:.0f} MB ({pct:.0f}%)", end="\r")
    print(f"\n  Downloaded {done/1e6:.1f} MB")
    return b"".join(chunks)


def stream_filter_csv(zip_bytes: bytes) -> pd.DataFrame:
    """
    Extract and stream-filter the WPP CSV from the ZIP.
    Returns only rows matching our target countries, years, and age bands.
    Uses chunked reading to keep memory low — the full file is ~150 MB.
    """
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        csv_files = [n for n in zf.namelist() if n.endswith(".csv")]
        if not csv_files:
            raise ValueError(f"No CSV in ZIP. Contents: {zf.namelist()}")
        csv_name = csv_files[0]
        print(f"\nReading: {csv_name}  (filtering to {len(TARGET_ISO3)} countries...)")

        kept = []
        total_rows = 0
        with zf.open(csv_name) as f:
            reader = pd.read_csv(
                f,
                chunksize=100_000,
                low_memory=False,
                encoding="utf-8-sig",   # handles BOM if present
            )
            for i, chunk in enumerate(reader):
                total_rows += len(chunk)

                # Normalise column names (WPP uses CamelCase in newer files)
                chunk.columns = chunk.columns.str.strip()

                # ── Detect column names ───────────────────────────────────
                # WPP2024 uses: ISO3_code, Location, Time, AgeGrp, Sex, PopMale, PopFemale, PopTotal
                # Older WPP used: country_code, LocID, Location, Variant, Time, MidPeriod, AgeGrp, ...
                iso_col  = next((c for c in chunk.columns
                                 if c.lower() in ("iso3_code", "iso3", "countrycode", "iso_code")), None)
                time_col = next((c for c in chunk.columns
                                 if c.lower() in ("time", "year")), None)
                age_col  = next((c for c in chunk.columns
                                 if c.lower() in ("agegrp", "agegroup", "age_grp")), None)
                sex_col  = next((c for c in chunk.columns
                                 if c.lower() in ("sex", "sexid")), None)
                loc_col  = next((c for c in chunk.columns
                                 if c.lower() in ("location", "locationname", "country")), None)

                if i == 0:
                    print(f"  Columns detected: {list(chunk.columns[:12])}...")
                    print(f"  → iso={iso_col}, time={time_col}, age={age_col}, "
                          f"sex={sex_col}, loc={loc_col}")

                # ── Apply filters ─────────────────────────────────────────
                mask = pd.Series([True] * len(chunk), index=chunk.index)

                if iso_col:
                    mask &= chunk[iso_col].isin(TARGET_ISO3)
                elif loc_col:
                    # Fall back to matching on country name if no ISO3 col
                    pass   # keep all and filter by name later

                if time_col:
                    mask &= chunk[time_col].between(START_YEAR, END_YEAR)

                if age_col:
                    mask &= chunk[age_col].isin(SCHOOL_AGE_BANDS)

                filtered = chunk[mask]
                if not filtered.empty:
                    kept.append(filtered)

                print(f"  Chunk {i+1}: read {total_rows:>8,} rows | "
                      f"kept {sum(len(k) for k in kept):>6,}", end="\r")

    print(f"\n  Done. Total rows read: {total_rows:,}")
    if not kept:
        print("  ⚠  No matching rows found — check column names above")
        return pd.DataFrame()
    return pd.concat(kept, ignore_index=True)


def reshape(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise column names and create a clean output with columns:
    iso3, country, year, sex, age_group, school_level, population
    """
    # Rename to standard names
    rename = {}
    col_lower = {c.lower(): c for c in df.columns}

    for target, candidates in {
        "iso3":       ["iso3_code", "iso3", "countrycode"],
        "country":    ["location", "locationname", "country"],
        "year":       ["time", "year"],
        "age_group":  ["agegrp", "agegroup", "age_grp"],
        "sex_id":     ["sex", "sexid"],
        "population": ["value", "popbothsexes", "poptotal", "popmale", "popfemale"],
    }.items():
        for cand in candidates:
            if cand in col_lower:
                rename[col_lower[cand]] = target
                break

    df = df.rename(columns=rename)

    # If file has separate Male/Female columns rather than a Sex column:
    if "sex_id" not in df.columns:
        pop_cols = {c.lower(): c for c in df.columns}
        male_col   = pop_cols.get("popmale")
        female_col = pop_cols.get("popfemale")
        both_col   = pop_cols.get("popbothsexes") or pop_cols.get("poptotal")

        rows = []
        for col, label in [(male_col, "Male"), (female_col, "Female"), (both_col, "Both")]:
            if col:
                tmp = df.copy()
                tmp["sex"] = label
                tmp["population"] = pd.to_numeric(tmp[col], errors="coerce") * 1000
                rows.append(tmp)
        if rows:
            df = pd.concat(rows, ignore_index=True)
    else:
        df["sex"]        = df["sex_id"].map({1: "Male", 2: "Female", 3: "Both"})
        df["population"] = pd.to_numeric(df.get("population", df.get("value", 0)),
                                          errors="coerce") * 1000

    # Label school levels
    df["school_level"] = df["age_group"].map({
        "0-4":   "Under primary",
        "5-9":   "Primary (approx, age 5–9)",
        "10-14": "Primary/Secondary overlap (age 10–14)",
        "15-19": "Secondary (approx, age 15–19)",
    })

    keep = ["iso3", "country", "year", "sex", "age_group", "school_level", "population"]
    keep = [c for c in keep if c in df.columns]
    return df[keep].dropna(subset=["population"]).sort_values(
        ["country", "year", "sex", "age_group"]
    )


def summarise(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pivot to a wide summary:
    country × year × sex → primary_pop, secondary_pop, total_school_age
    Uses Male + Female (not Both) to avoid double-counting.
    """
    sub = df[df["sex"].isin(["Male", "Female"])].copy()
    sub["level_simple"] = sub["age_group"].map({
        "5-9":   "primary_5to9",
        "10-14": "overlap_10to14",
        "15-19": "secondary_15to19",
    })
    pivot = (
        sub.groupby(["iso3", "country", "year", "sex", "level_simple"])["population"]
           .sum()
           .unstack("level_simple")
           .reset_index()
    )
    # Approximate school-age totals
    if "primary_5to9" in pivot and "overlap_10to14" in pivot:
        pivot["primary_approx"]   = pivot["primary_5to9"].fillna(0) + pivot["overlap_10to14"].fillna(0) / 2
    if "secondary_15to19" in pivot and "overlap_10to14" in pivot:
        pivot["secondary_approx"] = pivot["secondary_15to19"].fillna(0) + pivot["overlap_10to14"].fillna(0) / 2
    return pivot.round(0)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    # 1. Download
    zip_bytes = download_zip_to_memory(WPP_CSV_URL)

    # 2. Stream-filter
    df_raw = stream_filter_csv(zip_bytes)
    if df_raw.empty:
        return

    # 3. Reshape
    df = reshape(df_raw)
    print(f"\n  Kept {len(df):,} rows after reshaping")

    # 4. Save raw
    raw_path = os.path.join(OUT_DIR, "children_schoolage_raw.csv")
    df.to_csv(raw_path, index=False)
    print(f"  ✓ Saved → {raw_path}")

    # 5. Summary pivot
    summary = summarise(df)
    sum_path = os.path.join(OUT_DIR, "children_schoolage_summary.csv")
    summary.to_csv(sum_path, index=False)
    print(f"  ✓ Saved → {sum_path}")

    # 6. Quick preview
    print(f"\n── Sample output ─────────────────────────────────────")
    sample = (
        df[df["sex"] != "Both"]
          .groupby(["country", "year", "sex", "age_group"])["population"]
          .sum()
          .reset_index()
    )
    print(sample[sample["year"] == 2020].head(20).to_string(index=False))

    print(f"\n── Countries fetched ─────────────────────────────────")
    print(df.groupby(["country", "iso3"])["population"].count()
            .rename("rows")
            .reset_index()
            .to_string(index=False))

    print(f"\n✅  Done. Outputs in ./{OUT_DIR}/")
    print(f"    children_schoolage_raw.csv     — full detail (age band × sex × year)")
    print(f"    children_schoolage_summary.csv — wide pivot per country/year/sex")
    print(f"\nNote: population values are absolute counts (not thousands).")
    print(f"Source: UN WPP 2024, Medium variant (CC-BY 3.0 IGO)")


if __name__ == "__main__":
    main()