"""
fetch_schools.py  (v4 — correct HDX download URLs, no export.hotosm.org)
========================================================================
Downloads HOTOSM education facility point data for conflict-zone countries
directly from data.humdata.org using the stable HDX resource download URL.

CORRECT URL PATTERN (verified May 2025):
  https://data.humdata.org/dataset/{slug}/resource/{uuid}/download/{filename}

  Example:
  https://data.humdata.org/dataset/hotosm_phl_education_facilities/
    resource/f493860f-5653-41fd-a316-3d68ada0ed05/
    download/hotosm_phl_education_facilities_points_geojson.zip

NOTE: export.hotosm.org/downloads/... URLs are DEAD as of 2025.
      The correct host is data.humdata.org.

HOW TO REFRESH A UUID
---------------------
If you get a 404 for a country:
  1. Visit https://data.humdata.org/dataset/hotosm_{iso3.lower()}_education_facilities
  2. Find the row: "hotosm_{iso3}_education_facilities_points_geojson.zip"
  3. The UUID is the long hex string shown next to the download link
  4. Update DATASETS below with the new UUID

Install:
    pip install requests geopandas pandas

Usage:
    python fetch_schools.py                          # all countries
    python fetch_schools.py --countries LBN IRQ SYR  # specific countries
    python fetch_schools.py --countries NGA SOM ETH

Output:
    school_data/
        {ISO3}_schools.geojson   per-country files
        schools_all.geojson      merged Leaflet-ready GeoJSON
        schools_all.csv          flat CSV with latitude/longitude
"""

import argparse
import io
import json
import os
import re
import time
import zipfile

import pandas as pd
import geopandas as gpd
import requests
from shapely.geometry import shape

OUT_DIR = "school_data"
HDX_BASE = "https://data.humdata.org/dataset"
HEADERS  = {"User-Agent": "school-data-research/1.0 (humanitarian research project)"}

os.makedirs(OUT_DIR, exist_ok=True)

# ── Dataset registry ──────────────────────────────────────────────────────────
# Format: "ISO3": (slug, uuid, filename, country_name)
#
# slug     = HDX dataset slug  (hotosm_{iso3}_education_facilities)
# uuid     = resource UUID for the points_geojson.zip file
#            → from: https://data.humdata.org/dataset/{slug}
#            → look for the UUID next to "points_geojson.zip" download link
# filename = the zip filename inside the resource
#
# Download URL assembled as:
#   {HDX_BASE}/{slug}/resource/{uuid}/download/{filename}

DATASETS = {
    # ISO3  : (slug,                                    uuid,                                   filename,                                                   country_name)

    # ── Sub-Saharan Africa ─────────────────────────────────────────────────
    "SOM": ("hotosm_som_education_facilities",  "041f0358-f0fb-4dbe-b9f2-9b958d62cdec",  "hotosm_som_education_facilities_points_geojson.zip",  "Somalia"),
    "ETH": ("hotosm_eth_education_facilities",  "5b302f49-9354-4739-9b37-987a30d120ad",  "hotosm_eth_education_facilities_points_geojson.zip",  "Ethiopia"),
    "SDN": ("hotosm_sdn_education_facilities",  "e247b3bb-f2f5-4de6-b969-e507ac80fb50",  "hotosm_sdn_education_facilities_points_geojson.zip",  "Sudan"),
    "SSD": ("hotosm_ssd_education_facilities",  "d77e5e15-1917-4055-9aa9-31ec3efcc0b3",  "hotosm_ssd_education_facilities_points_geojson.zip",  "South Sudan"),
    "NGA": ("hotosm_nga_education_facilities",  "c3a5dfd5-1a04-4076-bc3d-20d709e19789",  "hotosm_nga_education_facilities_points_geojson.zip",  "Nigeria"),
    "MLI": ("hotosm_mli_education_facilities",  "81f0997e-bf57-4be5-9f44-41ed4c2827e8",                                "hotosm_mli_education_facilities_points_geojson.zip",  "Mali"),
    "BFA": ("hotosm_bfa_education_facilities",  "2daa435a-4241-4102-89f2-4a78d67e2526",                                "hotosm_bfa_education_facilities_points_geojson.zip",  "Burkina Faso"),
    "TCD": ("hotosm_tcd_education_facilities",  "41adc619-cd3e-4ca9-a788-02137bce7503",                                "hotosm_tcd_education_facilities_points_geojson.zip",  "Chad"),
    "CAF": ("hotosm_caf_education_facilities",  "52b646ee-8c34-43a5-80dd-dc7a7604c59f",                                "hotosm_caf_education_facilities_points_geojson.zip",  "Central African Republic"),
    "COD": ("hotosm_cod_education_facilities",  "5d95f52e-b04c-48c0-aeb4-6a1c54c3e6b5",                                "hotosm_cod_education_facilities_points_geojson.zip",  "DR Congo"),
    "MOZ": ("hotosm_moz_education_facilities",  "49ed5cda-fe8b-410e-95bd-15d9027c30c1",                                "hotosm_moz_education_facilities_points_geojson.zip",  "Mozambique"),

    # ── Middle East ────────────────────────────────────────────────────────
    "YEM": ("hotosm_yem_education_facilities",  "d22d241f-2f97-447c-8962-5846ec3c11c0",                                "hotosm_yem_education_facilities_points_geojson.zip",  "Yemen"),
    "SYR": ("hotosm_syr_education_facilities",  "04338c33-c5a9-4c44-9ab8-65aaab553583",  "hotosm_syr_education_facilities_points_geojson.zip",  "Syria"),
    "IRQ": ("hotosm_irq_education_facilities",  "b08a8387-f977-42fa-83f2-c400a9ba44d3",  "hotosm_irq_education_facilities_points_geojson.zip",  "Iraq"),
    "AFG": ("hotosm_afg_education_facilities",  "adbdd0df-d7fb-458e-af13-6e69ea8011dc",  "hotosm_afg_education_facilities_points_geojson.zip",  "Afghanistan"),
    "LBN": ("hotosm_lbn_education_facilities",  "966ddf12-0c80-44aa-8c6f-6a647ad4723a",  "hotosm_lbn_education_facilities_points_geojson.zip",  "Lebanon"),
    "PSE": ("hotosm_pse_education_facilities",  "99edf9f9-b1af-42ba-bc88-c286fc507cc2",                                "hotosm_pse_education_facilities_points_geojson.zip",  "Palestine"),
    "LBY": ("hotosm_lby_education_facilities",  "8205117f-2173-4fea-ae54-ebe7daed688f",                                "hotosm_lby_education_facilities_points_geojson.zip",  "Libya"),

    # ── SE Asia ────────────────────────────────────────────────────────────
    "MMR": ("hotosm_mmr_education_facilities",  "be0f4e04-4345-469b-ac14-e0605f15b0bb",                                "hotosm_mmr_education_facilities_points_geojson.zip",  "Myanmar"),
    "PAK": ("hotosm_pak_education_facilities",  "d04ed972-03e0-4aba-b4e3-40e33cfe7f7d",  "hotosm_pak_education_facilities_points_geojson.zip",  "Pakistan"),
    "KHM": ("hotosm_khm_education_facilities",  "27d92a03-c8ab-4662-a618-7783f721b633",  "hotosm_khm_education_facilities_points_geojson.zip",  "Cambodia"),
    "PHL": ("hotosm_phl_education_facilities",  "f493860f-5653-41fd-a316-3d68ada0ed05",  "hotosm_phl_education_facilities_points_geojson.zip",  "Philippines"),
    "BGD": ("hotosm_bgd_education_facilities",  "22a1683b-551b-4e47-ab77-048f95f3181f",                                "hotosm_bgd_education_facilities_points_geojson.zip",  "Bangladesh"),
}

UUID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)


# ── UUID lookup by scraping the HDX dataset page ─────────────────────────────

def lookup_uuid(slug: str, filename: str) -> str | None:
    """
    Fetch the HDX dataset page and extract the resource UUID for a given filename.
    The page text contains: "Download {filename} {UUID} More"
    """
    url = f"{HDX_BASE}/{slug}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code != 200:
            print(f"    HDX page returned HTTP {r.status_code}")
            return None
        # Find the filename then grab the UUID immediately after it
        idx = r.text.lower().find(filename.lower())
        if idx == -1:
            print(f"    Filename '{filename}' not found on HDX page")
            return None
        snippet = r.text[idx: idx + 150]
        m = UUID_RE.search(snippet)
        return m.group(0) if m else None
    except Exception as e:
        print(f"    Page fetch error: {e}")
    return None


# ── Download and parse one country ───────────────────────────────────────────

def fetch_country(slug: str, uuid: str, filename: str, iso3: str, cname: str) -> gpd.GeoDataFrame | None:
    url = f"{HDX_BASE}/{slug}/resource/{uuid}/download/{filename}"
    print(f"  → {url}")

    try:
        r = requests.get(url, headers=HEADERS, timeout=120, allow_redirects=True)
        if r.status_code == 404:
            print(f"  ✗ 404 — UUID is stale. Visit:\n    {HDX_BASE}/{slug}")
            return None
        if r.status_code == 403:
            print(f"  ✗ 403 — HDX is blocking this request (try a browser or VPN)")
            return None
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"  ✗ Network error: {e}")
        return None

    # Parse ZIP → GeoJSON
    try:
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            geojson_names = [n for n in z.namelist() if n.endswith(".geojson")]
            if not geojson_names:
                print(f"  ✗ No .geojson file in ZIP. Contents: {z.namelist()}")
                return None
            with z.open(geojson_names[0]) as f:
                geojson = json.load(f)
    except Exception as e:
        print(f"  ✗ ZIP/JSON error: {e}")
        return None

    features = geojson.get("features", [])
    if not features:
        print(f"  ✗ Empty FeatureCollection")
        return None

    rows = []
    for feat in features:
        raw_geom = feat.get("geometry")
        if not raw_geom:
            continue
        try:
            geom = shape(raw_geom)
        except Exception:
            continue

        pt = geom if geom.geom_type == "Point" else geom.centroid
        p  = feat.get("properties") or {}

        rows.append({
            "osm_id":    p.get("osm_id", ""),
            "name":      p.get("name") or p.get("name_en") or "",
            "amenity":   p.get("amenity", "school"),
            "building":  p.get("building", ""),
            "operator":  p.get("operator_type") or p.get("operatorty") or p.get("operator_t", ""),
            "capacity":  p.get("capacity_persons") or p.get("capacitype") or p.get("capacity_p", ""),
            "addr_city": p.get("addr_city") or p.get("addrcity", ""),
            "country":   cname,
            "iso3":      iso3,
            "source":    "HOTOSM/OSM",
            "latitude":  round(pt.y, 6),
            "longitude": round(pt.x, 6),
            "geometry":  pt,
        })

    if not rows:
        print(f"  ✗ No valid point geometries")
        return None

    gdf = gpd.GeoDataFrame(rows, crs="EPSG:4326")
    print(f"  ✓ {len(gdf):,} schools")
    return gdf


# ── Main ──────────────────────────────────────────────────────────────────────

def fetch_all(target_countries: list | None = None):
    all_gdfs = []
    targets  = {k: v for k, v in DATASETS.items()
                if target_countries is None or k in [c.upper() for c in target_countries]}

    for iso3, (slug, uuid, filename, cname) in targets.items():
        print(f"\n[{iso3}] {cname}")

        # Resolve UUID if unknown
        if uuid == "LOOKUP":
            print(f"  Resolving UUID from HDX page...")
            uuid = lookup_uuid(slug, filename)
            if not uuid:
                print(f"  ✗ Could not resolve UUID — skipping {iso3}")
                print(f"    Manual lookup: {HDX_BASE}/{slug}")
                time.sleep(1)
                continue
            print(f"  UUID: {uuid}")
            time.sleep(0.5)

        gdf = fetch_country(slug, uuid, filename, iso3, cname)
        if gdf is None:
            continue

        out = os.path.join(OUT_DIR, f"{iso3}_schools.geojson")
        gdf.to_file(out, driver="GeoJSON")
        print(f"  Saved → {out}")
        all_gdfs.append(gdf)
        time.sleep(0.5)  # polite pause

    if not all_gdfs:
        print("\n⚠  No data fetched.")
        print("   Possible causes:")
        print("   1. HDX is blocking requests from your IP/network")
        print("   2. Some UUIDs are stale — check HDX pages for updated UUIDs")
        print("   3. Network/firewall restrictions")
        print("\n   Try running: python fetch_schools.py --countries LBN")
        print("   to test a single small country first.")
        return

    merged = gpd.GeoDataFrame(pd.concat(all_gdfs, ignore_index=True), crs="EPSG:4326")

    geojson_path = os.path.join(OUT_DIR, "schools_all.geojson")
    merged.to_file(geojson_path, driver="GeoJSON")

    csv_cols = ["name", "amenity", "building", "operator", "addr_city",
                "country", "iso3", "source", "latitude", "longitude"]
    csv_path = os.path.join(OUT_DIR, "schools_all.csv")
    merged[[c for c in csv_cols if c in merged.columns]].to_csv(csv_path, index=False)

    print(f"\n{'='*55}")
    print(f"✅  Total schools : {len(merged):,}")
    print(f"    GeoJSON → {geojson_path}")
    print(f"    CSV     → {csv_path}")
    print(f"\nBreakdown:")
    summary = (merged.groupby(["iso3", "country"]).size()
                     .reset_index(name="count")
                     .sort_values("count", ascending=False))
    print(summary.to_string(index=False))


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download HOTOSM school point data from HDX for conflict-zone countries.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fetch_schools.py
  python fetch_schools.py --countries LBN
  python fetch_schools.py --countries SOM ETH NGA SDN
  python fetch_schools.py --countries SYR IRQ AFG LBN PSE LBY YEM
        """
    )
    parser.add_argument("--countries", nargs="+", metavar="ISO3",
                        help="ISO3 codes to fetch (default: all)")
    args = parser.parse_args()
    fetch_all(target_countries=args.countries)