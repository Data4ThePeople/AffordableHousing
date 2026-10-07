"""Pack everything the page needs into data/processed/map_data.json.

Per unit and frame: cash-rent bucket counts, units paying no cash rent, six income profiles
(median renter household; 20th, 40th, 50th, 60th, 80th percentile of all households), which of
those are published and which we estimated from buckets, and a low-reliability mark.
Also: state and national records, the tax grid, CPI factors, shapes.
Output: data/processed/map_data.json"""
import json

from common import FRAMES, INC_EDGES, PROC, RENTER_EDGES, RENT_EDGES, STATE_INFO

PCTS = [0.2, 0.4, 0.5, 0.6, 0.8]
MIN_UNITS = 200     # fewer cash-rent units than this: low reliability
MAX_CV = 0.30       # ACS: margin of error on renter units implies a coefficient of variation above this: low reliability
HOW = {"direct": 0, "merged": 1, "rebuilt": 2}


def pctl(counts, edges, p):
    """Percentile by straight-line interpolation inside the bucket that holds it. None if it falls in the open top bucket."""
    tot = sum(counts)
    if tot <= 0:
        return None
    need, cum = p * tot, 0
    for i, c in enumerate(counts):
        if cum + c >= need and c > 0:
            if i == len(counts) - 1:
                return None
            return round(edges[i] + (need - cum) / c * (edges[i + 1] - edges[i]))
        cum += c
    return None


def pack(x, fk):
    """One unit-frame record for the page."""
    if "na" in x:
        return {"x": x["na"]}
    edges = INC_EDGES[fk]
    est = [pctl(x["i"], edges, p) for p in PCTS]
    pub = [x["q"][0], x["q"][1], x["mi"], x["q"][2], x["q"][3]] if x["q"] else [None, None, x["mi"], None, None]
    prof, mask = [], 0
    for i in range(5):
        if pub[i]:
            prof.append(round(pub[i]))
        else:
            prof.append(est[i])
            mask |= 1 << i
    if x["ri"]:
        prof.append(round(x["ri"]))
    else:                                               # no published renter median: estimate it from renter income buckets
        prof.append(pctl(x["ti"], RENTER_EDGES, 0.5))
        mask |= 1 << 5
    cash = sum(x["r"])
    lo = cash < MIN_UNITS
    if x["moe"] is not None and cash + x["nc"] > 0 and (x["moe"] / 1.645) / (cash + x["nc"]) > MAX_CV:
        lo = True
    return {"r": x["r"], "nc": x["nc"], "p": prof, "e": mask, "lo": int(lo), "h": HOW.get(x.get("how", "direct"), 0), "hh": sum(x["i"])}


def main():
    H = json.loads((PROC / "harmonized.json").read_text())
    G = json.loads((PROC / "geo.json").read_text())
    T = json.loads((PROC / "tax_grid.json").read_text())
    cpi = json.loads((PROC / "cpi.json").read_text())
    sts = sorted(STATE_INFO)
    frames = [{"k": fk, "label": label, "y": y, "re": RENT_EDGES[fk], "cpi": cpi[str(y)] / cpi["2024"]} for fk, label, _, y in FRAMES]
    units = []
    for u in sorted(H["units"]):
        info = H["units"][u]
        units.append({"id": u, "n": info["name"], "s": info["st"], "c": G["pts"][u], "m": len(info["members"]),
                      "f": [pack(info["f"][fk], fk) for fk, *_ in FRAMES]})
    assert len({u["id"] for u in units}) == len(units)
    out = {"frames": frames, "grid": G["grid"], "geo": G["geo"], "borders": G["borders"],
           "states": {s: list(STATE_INFO[s]) for s in sts}, "units": units,
           "us": [pack(H["us"][fk], fk) for fk, *_ in FRAMES],
           "st": {s: [pack(H["states"][s][fk], fk) for fk, *_ in FRAMES] for s in sts},
           "tax": {"inc": T["inc"], "types": T["types"],
                   "t": [[[T["tax"][fk][str(ti)][s] for s in sts] for ti in range(len(T["types"]))] for fk, *_ in FRAMES]},
           "rules": {"minUnits": MIN_UNITS, "maxCv": MAX_CV}}
    dest = PROC / "map_data.json"
    dest.write_text(json.dumps(out, separators=(",", ":")))
    import gzip
    print(f"wrote {dest.name}: {dest.stat().st_size / 1e6:.1f} MB, {len(gzip.compress(dest.read_bytes(), 9)) / 1e6:.2f} MB gzipped")


if __name__ == "__main__":
    main()
