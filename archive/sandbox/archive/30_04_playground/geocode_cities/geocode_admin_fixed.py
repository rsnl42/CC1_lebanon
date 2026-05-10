"""
geocode_admin.py
================
Generic geocoder for any CSV/Excel file containing Country, Admin1, Admin2
columns. Resolves coordinates using the Nominatim (OpenStreetMap) API with:

  • Smart deduplication  — only unique (Admin2, Admin1, Country) combos are
                           geocoded; results are joined back to all rows
  • 3-level fallback     — tries Admin2+Admin1+Country → Admin2+Country →
                           Admin1+Country, so partial data still resolves
  • Cache file           — saves a JSON sidecar of resolved coordinates so
                           re-runs and multi-file workflows never re-query
                           a place already looked up
  • Fuzzy matching       — optionally attempts fuzzy name matching for minor
                           spelling differences (requires `thefuzz` package)
  • Rate limiting        — respects Nominatim ToS (max 1 req/sec)
  • Dry-run mode         — preview what would be queried without hitting the API

Usage (command line)
--------------------
    pip install pandas requests openpyxl thefuzz
    
    # Basic — auto-detects column names, geocodes everything
    python geocode_admin.py MyCountry.csv

    # Specify output path
    python geocode_admin.py MyCountry.csv MyCountry_geocoded.csv

    # Override column names if they differ from Country/Admin1/Admin2
    python geocode_admin.py data.csv --country-col nation --admin1-col state --admin2-col district

    # Dry run — shows what would be queried, no API calls
    python geocode_admin.py data.csv --dry-run

    # Use a shared cache across multiple country files
    python geocode_admin.py Nigeria.csv --cache geocode_cache.json
    python geocode_admin.py Somalia.csv --cache geocode_cache.json

Usage (as a module)
-------------------
    from geocode_admin import geocode_file
    df = geocode_file("Lebanon.csv")
    df = geocode_file("Nigeria.xlsx", admin2_col="LGA", cache_path="cache.json")

Inputs accepted
---------------
    .csv, .xlsx, .xls

Output
------
    Same file with two new columns appended: Latitude, Longitude
    A JSON cache file (default: geocode_cache.json) for reuse

Column name auto-detection
--------------------------
    The script looks for columns matching (case-insensitive):
      Country  → country, nation, iso3, country_name
      Admin1   → admin1, state, governorate, province, region
      Admin2   → admin2, district, county, lga, qadaa, sub-district, zone
    Override with --country-col / --admin1-col / --admin2-col if needed.
"""

import argparse
import json
import os
import sys
import time

import pandas as pd
import requests

# ── Constants ─────────────────────────────────────────────────────────────────
NOMINATIM_URL  = "https://nominatim.openstreetmap.org/search"
USER_AGENT     = "geocode-admin-research/2.0 (open-source field research tool)"
REQUEST_DELAY  = 1.1        # seconds between API calls (Nominatim ToS)
DEFAULT_CACHE  = "geocode_cache.json"

# Column name aliases (lowercase) for auto-detection
COUNTRY_ALIASES = ["country", "country_name", "countryname", "nation", "iso3"]
ADMIN1_ALIASES  = ["admin1", "admin1name", "admin_1", "state", "governorate", "province", "region"]
ADMIN2_ALIASES  = ["admin2", "admin2name", "admin_2", "district", "county", "lga", "qadaa",
                   "sub-district", "subdistrict", "zone", "woreda", "upazila", "kecamatan"]


# ── Cache helpers ──────────────────────────────────────────────────────────────
def load_cache(path: str) -> dict:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"  Loaded {len(data)} cached entries from {path}")
        return data
    return {}


def save_cache(cache: dict, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def cache_key(admin2: str, admin1: str, country: str) -> str:
    return f"{str(admin2).strip()}|{str(admin1).strip()}|{str(country).strip()}"


# ── Column auto-detection ──────────────────────────────────────────────────────
def detect_col(columns: list[str], aliases: list[str], label: str) -> str | None:
    col_lower = {c.lower().replace(" ", "_"): c for c in columns}
    for alias in aliases:
        if alias in col_lower:
            return col_lower[alias]
    return None


def resolve_columns(df: pd.DataFrame,
                    country_col: str | None,
                    admin1_col:  str | None,
                    admin2_col:  str | None) -> tuple[str, str, str]:
    cols = list(df.columns)

    country_col = country_col or detect_col(cols, COUNTRY_ALIASES, "Country")
    admin1_col  = admin1_col  or detect_col(cols, ADMIN1_ALIASES,  "Admin1")
    admin2_col  = admin2_col  or detect_col(cols, ADMIN2_ALIASES,  "Admin2")

    missing = [label for label, col in
               [("Country", country_col), ("Admin1", admin1_col), ("Admin2", admin2_col)]
               if col is None]
    if missing:
        print(f"\n⚠  Could not auto-detect columns for: {', '.join(missing)}")
        print(f"   Available columns: {cols}")
        print(f"   Use --country-col / --admin1-col / --admin2-col to specify them.\n")
        sys.exit(1)

    print(f"  Using columns → Country: '{country_col}' | "
          f"Admin1: '{admin1_col}' | Admin2: '{admin2_col}'")
    return country_col, admin1_col, admin2_col


# ── Nominatim geocoder ─────────────────────────────────────────────────────────
def nominatim_query(params: dict) -> tuple[float, float] | None:
    """Single Nominatim request; returns (lat, lon) or None."""
    try:
        r = requests.get(
            NOMINATIM_URL,
            params={**params, "format": "json", "limit": 1},
            headers={"User-Agent": USER_AGENT},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print(f"    Request error: {e}")
    return None


def geocode_place(admin2: str, admin1: str, country: str) -> tuple[float | None, float | None, str]:
    """
    Try three progressively coarser queries:
      1. Admin2 + Admin1 + Country  (most precise)
      2. Admin2 + Country           (if Admin1 causes ambiguity)
      3. Admin1 + Country           (Admin2 not found, fall back to Admin1 centroid)
    Returns (lat, lon, method_used)
    """
    # Level 1: full structured query
    result = nominatim_query({"county": admin2, "state": admin1, "country": country})
    if result:
        return *result, "admin2+admin1+country"
    time.sleep(REQUEST_DELAY)

    # Level 2: Admin2 + Country only
    result = nominatim_query({"county": admin2, "country": country})
    if result:
        return *result, "admin2+country"
    time.sleep(REQUEST_DELAY)

    # Level 3: free-text fallback with Admin2, Admin1, Country
    result = nominatim_query({"q": f"{admin2}, {admin1}, {country}"})
    if result:
        return *result, "freetext-admin2"
    time.sleep(REQUEST_DELAY)

    # Level 4: fall back to Admin1 centroid
    result = nominatim_query({"state": admin1, "country": country})
    if result:
        return *result, "admin1-fallback"
    time.sleep(REQUEST_DELAY)

    return None, None, "failed"


# ── Fuzzy match helper ─────────────────────────────────────────────────────────
def try_fuzzy_match(name: str, cache: dict, threshold: int = 85) -> tuple[float, float] | None:
    """
    If an exact cache key miss occurs, try fuzzy-matching the Admin2 part
    of existing cache keys. Requires `thefuzz` package.
    """
    try:
        from thefuzz import process
        existing_keys = list(cache.keys())
        if not existing_keys:
            return None
        # Extract just the admin2 portion of cache keys
        admin2_parts = [k.split("|")[0] for k in existing_keys]
        match, score = process.extractOne(name, admin2_parts)
        if score >= threshold:
            matched_key = existing_keys[admin2_parts.index(match)]
            print(f"    Fuzzy matched '{name}' → '{match}' (score {score})")
            return cache[matched_key]
    except ImportError:
        pass
    return None


# ── Core function ──────────────────────────────────────────────────────────────
def geocode_file(
    input_path:  str,
    output_path: str | None = None,
    country_col: str | None = None,
    admin1_col:  str | None = None,
    admin2_col:  str | None = None,
    cache_path:  str = DEFAULT_CACHE,
    dry_run:     bool = False,
    fuzzy:       bool = True,
) -> pd.DataFrame:
    """
    Main entry point. Reads input_path, geocodes it, saves to output_path.
    Returns the geocoded DataFrame.
    """

    # ── Load file ─────────────────────────────────────────────────────────────
    ext = os.path.splitext(input_path)[1].lower()
    if ext in (".xlsx", ".xls"):
        df = pd.read_excel(input_path)
    elif ext == ".csv":
        df = pd.read_csv(input_path, low_memory=False)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    print(f"\nLoaded  : {input_path}  ({len(df):,} rows × {len(df.columns)} cols)")

    # ── Detect columns ────────────────────────────────────────────────────────
    c_col, a1_col, a2_col = resolve_columns(df, country_col, admin1_col, admin2_col)

    # ── Identify unique combos to geocode ─────────────────────────────────────
    unique = (
        df[[c_col, a1_col, a2_col]]
        .drop_duplicates()
        .dropna(subset=[a2_col])
        .reset_index(drop=True)
    )
    print(f"Unique  : {len(unique)} (Country, Admin1, Admin2) combinations to resolve")

    if dry_run:
        print("\n── DRY RUN — queries that would be sent ──")
        for _, row in unique.iterrows():
            print(f"  {row[a2_col]!r:30} | {row[a1_col]!r:25} | {row[c_col]!r}")
        print(f"\nTotal API calls (worst case): {len(unique) * 4}")
        return df

    # ── Load cache ────────────────────────────────────────────────────────────
    cache = load_cache(cache_path)
    print(f"To fetch: {sum(1 for _, r in unique.iterrows() if cache_key(r[a2_col], r[a1_col], r[c_col]) not in cache)} new queries")

    # ── Geocode unique combos ─────────────────────────────────────────────────
    print()
    results = {}  # key → (lat, lon)

    for i, row in unique.iterrows():
        a2, a1, country = str(row[a2_col]), str(row[a1_col]), str(row[c_col])
        key = cache_key(a2, a1, country)

        # Cache hit
        if key in cache:
            results[key] = tuple(cache[key])
            print(f"  [{i+1:>3}/{len(unique)}] {a2:<28} ✓ cached")
            continue

        # Fuzzy match against existing cache
        if fuzzy:
            fuzzy_result = try_fuzzy_match(a2, cache)
            if fuzzy_result:
                results[key] = fuzzy_result
                cache[key]   = list(fuzzy_result)
                save_cache(cache, cache_path)
                print(f"  [{i+1:>3}/{len(unique)}] {a2:<28} ✓ fuzzy")
                continue

        # API call
        lat, lon, method = geocode_place(a2, a1, country)
        time.sleep(REQUEST_DELAY)

        if lat is not None:
            results[key] = (lat, lon)
            cache[key]   = [lat, lon]
            save_cache(cache, cache_path)
            print(f"  [{i+1:>3}/{len(unique)}] {a2:<28} ✓ {method}  ({lat:.4f}, {lon:.4f})")
        else:
            results[key] = (None, None)
            print(f"  [{i+1:>3}/{len(unique)}] {a2:<28} ✗ FAILED — add manually to cache")

    # ── Join coordinates back to all rows ─────────────────────────────────────
    def get_lat(row):
        k = cache_key(row[a2_col], row[a1_col], row[c_col])
        return results.get(k, (None, None))[0]

    def get_lon(row):
        k = cache_key(row[a2_col], row[a1_col], row[c_col])
        return results.get(k, (None, None))[1]

    df["Latitude"]  = df.apply(get_lat, axis=1)
    df["Longitude"] = df.apply(get_lon, axis=1)

    # ── Summary ───────────────────────────────────────────────────────────────
    matched    = df["Latitude"].notna().sum()
    unmatched  = df["Latitude"].isna().sum()
    failed_a2s = df[df["Latitude"].isna()][a2_col].unique()

    print(f"\n{'─'*55}")
    print(f"  Geocoded : {matched:,} / {len(df):,} rows")
    if unmatched:
        print(f"  Failed   : {unmatched:,} rows — Admin2 values with no result:")
        for name in failed_a2s:
            print(f"    → '{name}'")
        print(f"\n  To fix: add these to {cache_path} manually:")
        print(f'  "{failed_a2s[0]}|<admin1>|<country>": [<lat>, <lon>]')

    # ── Save output ───────────────────────────────────────────────────────────
    if output_path is None:
        stem = os.path.splitext(input_path)[0]
        output_path = f"{stem}_geocoded.csv"

    df.to_csv(output_path, index=False)
    print(f"\n✅  Saved → {output_path}")
    print(f"    Cache  → {cache_path}  ({len(cache)} total entries)")

    return df


# ── CLI ────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Geocode CSV/Excel files with Country, Admin1, Admin2 columns.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python geocode_admin.py Lebanon.csv
  python geocode_admin.py Nigeria.xlsx --cache shared_cache.json
  python geocode_admin.py data.csv --admin2-col LGA --admin1-col State
  python geocode_admin.py data.csv --dry-run
        """
    )
    parser.add_argument("input",         help="Input CSV or Excel file path")
    parser.add_argument("output",        nargs="?", default=None,
                                         help="Output CSV path (default: <input>_geocoded.csv)")
    parser.add_argument("--country-col", default=None, help="Column name for country")
    parser.add_argument("--admin1-col",  default=None, help="Column name for Admin1")
    parser.add_argument("--admin2-col",  default=None, help="Column name for Admin2")
    parser.add_argument("--cache",       default=DEFAULT_CACHE,
                                         help=f"Cache JSON file (default: {DEFAULT_CACHE})")
    parser.add_argument("--dry-run",     action="store_true",
                                         help="Preview queries without calling the API")
    parser.add_argument("--no-fuzzy",    action="store_true",
                                         help="Disable fuzzy name matching")

    args = parser.parse_args()

    geocode_file(
        input_path  = args.input,
        output_path = args.output,
        country_col = args.country_col,
        admin1_col  = args.admin1_col,
        admin2_col  = args.admin2_col,
        cache_path  = args.cache,
        dry_run     = args.dry_run,
        fuzzy       = not args.no_fuzzy,
    )


if __name__ == "__main__":
    main()
