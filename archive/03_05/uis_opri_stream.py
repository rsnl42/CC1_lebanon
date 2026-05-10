"""
uis_opri_stream.py
==================
Streams the UNESCO UIS OPRI bulk ZIP directly from the web,
extracts and filters OPRI_DATA_NATIONAL.csv on-the-fly —
never writing the full 2.7M-row file to disk.

Only the filtered rows you care about are kept and saved.

Install: pip install requests pandas
"""

import requests
import zipfile
import io
import os
import pandas as pd

# ── What you want to keep ────────────────────────────────────────────────────
# Set any of these to None to keep everything for that dimension

FILTER_COUNTRIES = [
    # Sub-Saharan Africa (HRP & Neighbors)
    "NGA", "ETH", "COD", "KEN", "TZA", "UGA", "GHA", "MOZ", "SOM",
    "SDN", "SSD", "MLI", "BFA", "NER", "TCD", "CMR", "BDI", "CAF",
    # Middle East & North Africa
    "IRQ", "SYR", "YEM", "AFG", "LBN", "LBY", "JOR", "PSE",
    # Latin America & Caribbean
    "HTI", "VEN", "COL",
    # Europe
    "UKR",
    # SE Asia & Others
    "MMR", "THA", "VNM", "PHL", "IDN", "KHM", "LAO", "BGD",
]

FILTER_INDICATORS = None    # None = keep all OPRI indicators
START_YEAR        = 2000
END_YEAR          = 2025 # Changed from 2023
CHUNK_SIZE        = 50_000  # rows read at a time — tune based on your RAM

OPRI_ZIP_URL = "https://download.uis.unesco.org/bdds/202509/OPRI.zip"
TARGET_CSV   = "OPRI_DATA_NATIONAL.csv"   # the big file inside the ZIP
LABEL_CSV    = "OPRI_LABEL.csv"           # indicator name lookup
COUNTRY_CSV  = "OPRI_COUNTRY.csv"         # country name lookup
OUT_FILE     = "opri_filtered.csv"


# ── Step 1: Stream ZIP into memory (not disk) ─────────────────────────────────
def stream_zip_to_memory(url: str) -> zipfile.ZipFile:
    print(f"Streaming ZIP from UIS...")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        buf   = io.BytesIO()
        done  = 0
        for chunk in r.iter_content(chunk_size=1 << 20):
            buf.write(chunk)
            done += len(chunk)
            if total:
                print(f"  {done/1e6:.0f} / {total/1e6:.0f} MB", end="")
    print(f"  Done. ZIP size in memory: {done/1e6:.1f} MB")
    buf.seek(0)
    return zipfile.ZipFile(buf)


# ── Step 2: Load small lookup files fully ─────────────────────────────────────
def load_lookup(zf: zipfile.ZipFile, filename: str, key_col: str, val_col: str) -> dict:
    if filename not in zf.namelist():
        return {}
    with zf.open(filename) as f:
        df = pd.read_csv(f, low_memory=False)
    return df.set_index(key_col)[val_col].to_dict()


# ── Step 3: Stream-filter the big CSV ─────────────────────────────────────────
def stream_filter(zf: zipfile.ZipFile, indicator_labels: dict, country_labels: dict) -> pd.DataFrame:
    print(f"Streaming {TARGET_CSV} in {CHUNK_SIZE:,}-row chunks...")
    kept_chunks = []
    total_read  = 0
    total_kept  = 0

    with zf.open(TARGET_CSV) as raw:
        reader = pd.read_csv(raw, chunksize=CHUNK_SIZE, low_memory=False)
        for i, chunk in enumerate(reader):
            total_read += len(chunk)

            # ── Apply filters ─────────────────────────────────────────────
            if FILTER_COUNTRIES:
                chunk = chunk[chunk["COUNTRY_ID"].isin(FILTER_COUNTRIES)]
            if FILTER_INDICATORS:
                chunk = chunk[chunk["INDICATOR_ID"].isin(FILTER_INDICATORS)]
            if START_YEAR:
                chunk = chunk[chunk["YEAR"] >= START_YEAR]
            if END_YEAR:
                chunk = chunk[chunk["YEAR"] <= END_YEAR]

            if not chunk.empty:
                kept_chunks.append(chunk)
                total_kept += len(chunk)

            print(f"  Chunk {i+1:3d}: read {total_read:>9,} rows | kept {total_kept:>7,}", end="")

    print(f"  Finished. Read {total_read:,} rows → kept {total_kept:,} rows")

    if not kept_chunks:
        print("  ⚠ No rows matched your filters.")
        return pd.DataFrame()

    df = pd.concat(kept_chunks, ignore_index=True)

    # ── Attach human-readable labels ──────────────────────────────────────
    if indicator_labels:
        df["INDICATOR_NAME"] = df["INDICATOR_ID"].map(indicator_labels)
    if country_labels:
        df["COUNTRY_NAME"] = df["COUNTRY_ID"].map(country_labels)

    return df


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # 1. Stream ZIP into a memory buffer (no disk write)
    zf = stream_zip_to_memory(OPRI_ZIP_URL)

    print(f"Files in ZIP: {zf.namelist()}")

    # 2. Load small lookup tables fully (they're tiny — KB range)
    indicator_labels = load_lookup(zf, LABEL_CSV,   "INDICATOR_ID", "INDICATOR_LABEL_EN")
    country_labels   = load_lookup(zf, COUNTRY_CSV, "COUNTRY_ID",   "COUNTRY_NAME_EN")
    print(f"Loaded {len(indicator_labels)} indicator labels, {len(country_labels)} country labels")

    # 3. Stream + filter the big file
    df = stream_filter(zf, indicator_labels, country_labels)
    zf.close()

    if df.empty:
        print("Nothing to save.")
    else:
        df.to_csv(OUT_FILE, index=False)
        size_kb = os.path.getsize(OUT_FILE) / 1e3
        print(f"✅ Saved {len(df):,} rows → {OUT_FILE}  ({size_kb:.0f} KB)")
        print(f"Column summary:")
        print(df.dtypes.to_string())
        print(f"Indicators found: {df['INDICATOR_ID'].nunique()}")
        print(df[["INDICATOR_ID", "INDICATOR_NAME"]].drop_duplicates().head(15).to_string(index=False))
