"""Source coverage check: how much of what the map shows is a direct read and how much is filled in.

By frame: units shown and blank; units taken directly, merged or rebuilt; share of income profile
values published against estimated from buckets; share of units where the default rent ceiling
(median renter household, married with no children, 30% of post-tax income) lands in the open top rent
bucket; share of units and of rentals marked low reliability; and the gap between our interpolated medians and the published ones.
Output: data/processed/coverage.csv"""
import bisect
import json

import pandas as pd

from common import FRAMES, INC_EDGES, PROC, RENTER_EDGES, RENT_EDGES, STATE_INFO


def interp_median(counts, edges):
    tot, cum = sum(counts), 0
    for i, c in enumerate(counts):
        if cum + c >= tot / 2 and c > 0:
            return None if i == len(counts) - 1 else edges[i] + (tot / 2 - cum) / c * (edges[i + 1] - edges[i])
        cum += c


def main():
    D = json.loads((PROC / "map_data.json").read_text())
    H = json.loads((PROC / "harmonized.json").read_text())
    sts = sorted(STATE_INFO)
    inc = D["tax"]["inc"]
    rows = []
    for fi, (fk, label, _, _) in enumerate(FRAMES):
        recs = [(u, u["f"][fi]) for u in D["units"]]
        shown = [(u, r) for u, r in recs if "x" not in r]
        n = len(shown)
        vals = sum(1 for _, r in shown for i in range(5) if r["p"][i] is not None)
        est = sum(1 for _, r in shown for i in range(5) if r["p"][i] is not None and r["e"] >> i & 1)
        top = 0
        for u, r in shown:
            m = r["p"][5]
            if m is None:
                continue
            tax = D["tax"]["t"][fi][1][sts.index(u["s"])]
            j = min(len(inc) - 2, max(0, bisect.bisect_right(inc, m) - 1))
            t = tax[j] + (tax[j + 1] - tax[j]) * (m - inc[j]) / (inc[j + 1] - inc[j])
            if 0.30 * (m - t) / 12 >= RENT_EDGES[fk][-1]:
                top += 1
        units_all = sum(sum(r["r"]) for _, r in shown)
        # interpolated against published medians, units read directly
        gi, gr, gt = [], [], []
        for uid, info in H["units"].items():
            x = info["f"][fk]
            if "na" in x or x.get("how") != "direct":
                continue
            if x["mi"]:
                e = interp_median(x["i"], INC_EDGES[fk])
                if e:
                    gi.append(abs(e / x["mi"] - 1))
            if x["ri"] and sum(x["ti"]) >= 500:
                e = interp_median(x["ti"], RENTER_EDGES)
                if e:
                    gt.append(abs(e / x["ri"] - 1))
            if x["mr"] and sum(x["r"]) >= 200:
                e = interp_median(x["r"], RENT_EDGES[fk])
                if e:
                    gr.append(abs(e / x["mr"] - 1))
        al = H["us"][fk].get("al")
        rows.append({"frame": label, "units_shown": n, "blank": len(recs) - n,
                     "direct": sum(r["h"] == 0 for _, r in shown), "merged": sum(r["h"] == 1 for _, r in shown), "rebuilt": sum(r["h"] == 2 for _, r in shown),
                     "profile_pct_estimated": round(100 * est / vals, 1), "p80_unavailable": sum(r["p"][4] is None for _, r in shown),
                     "renter_median_published": sum(r["p"][5] is not None and not r["e"] >> 5 & 1 for _, r in shown), "renter_median_estimated": sum(r["p"][5] is not None and bool(r["e"] >> 5 & 1) for _, r in shown),
                     "renter_median_none": sum(r["p"][5] is None for _, r in shown),
                     "renter_median_gap_typical_pct": round(100 * pd.Series(gt).median(), 2), "renter_median_gap_p95_pct": round(100 * pd.Series(gt).quantile(.95), 2),
                     "ceiling_in_top_bucket_units": top,
                     "low_reliability_units_pct": round(100 * sum(r["lo"] for _, r in shown) / n, 1),
                     "low_reliability_rentals_pct": round(100 * sum(sum(r["r"]) for _, r in shown if r["lo"]) / units_all, 2),
                     "rent_imputed_pct": round(100 * al[0] / al[1], 1) if al else None, "income_imputed_pct": round(100 * al[2] / al[3], 1) if al else None,
                     "median_income_gap_typical_pct": round(100 * pd.Series(gi).median(), 2), "median_income_gap_p95_pct": round(100 * pd.Series(gi).quantile(.95), 2),
                     "median_rent_gap_typical_pct": round(100 * pd.Series(gr).median(), 2), "median_rent_gap_p95_pct": round(100 * pd.Series(gr).quantile(.95), 2)})
    c = pd.DataFrame(rows)
    c.to_csv(PROC / "coverage.csv", index=False)
    pd.set_option("display.width", 250)
    print(c.set_index("frame").T.to_string())


if __name__ == "__main__":
    main()
