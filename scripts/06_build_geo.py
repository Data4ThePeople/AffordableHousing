"""Shapes for the map: one outline per stable county unit on 2024 boundaries, plus state borders.

Census cartographic boundary polygons (1:500,000) are merged where a unit has several member
counties, projected (Albers USA with Alaska and Hawaii insets), simplified and delta-encoded.
Each unit also gets a point inside its largest piece, used for the bubble view.
Shapes are for drawing only; no number is computed from them.
Output: data/processed/geo.json"""
import json

import geopandas as gpd
import numpy as np
import shapely

from albers import project
from common import PROC, RAW, STATE_INFO

TOL = 200          # simplification tolerance, meters
GRID = 50          # coordinate grid, meters
MIN_PART = 0.2e6   # drop detached parts under 0.2 km2 after simplification (unless it is the only part)


def prep(geom, st):
    g = shapely.simplify(project(shapely.make_valid(geom), st), TOL, preserve_topology=True)
    parts = [p for p in getattr(g, "geoms", [g]) if p.geom_type == "Polygon" and not p.is_empty]
    if len(parts) > 1:
        big = [p for p in parts if p.area >= MIN_PART]
        parts = big or [max(parts, key=lambda p: p.area)]
    return parts


def encode(parts):
    out = []
    for p in parts:
        rings = []
        for ring in [p.exterior, *p.interiors]:
            xy = np.round(np.asarray(ring.coords)[:-1] / GRID).astype(np.int64)
            keep = np.r_[True, np.any(np.diff(xy, axis=0) != 0, axis=1)]
            xy = xy[keep]
            if len(xy) < 3:
                continue
            d = np.vstack([xy[:1], np.diff(xy, axis=0)])
            d[:, 1] *= -1  # screen y points down
            rings.append(d.ravel().tolist())
        if rings:
            out.append(rings)
    return out


def main():
    units = json.loads((PROC / "harmonized.json").read_text())["units"]
    cb = gpd.read_file(f"zip://{RAW / 'cb' / 'cb_2024_us_county_500k.zip'}").set_index("GEOID").geometry
    geo, pts = {}, {}
    for u, info in units.items():
        g = shapely.union_all([cb[m] for m in info["members"]])
        parts = prep(g, info["st"])
        assert parts, f"no shape for {u}"
        geo[u] = encode(parts)
        c = max(parts, key=lambda p: p.area).representative_point()
        pts[u] = [int(round(c.x / GRID)), int(round(-c.y / GRID))]
    st = gpd.read_file(f"zip://{RAW / 'cb' / 'cb_2024_us_state_500k.zip'}")
    st = st[st.STATEFP.isin(STATE_INFO)]
    borders = [encode(prep(g, s)) for g, s in zip(st.geometry, st.STATEFP)]
    dest = PROC / "geo.json"
    dest.write_text(json.dumps({"grid": GRID, "geo": geo, "pts": pts, "borders": borders}, separators=(",", ":")))
    import gzip
    print(f"wrote {dest.name}: {dest.stat().st_size / 1e6:.1f} MB, {len(gzip.compress(dest.read_bytes(), 9)) / 1e6:.2f} MB gzipped; {len(geo)} units")


if __name__ == "__main__":
    main()
