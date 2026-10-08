"""Images for the post, taken from the built viz so every number on them is the tool's own.

Opens dist/index.html in headless Chrome with the dark palette (house rule for static images), sets the
controls for each scene, and saves the map or one chart from the county panel under a title.
Scenes follow the case study in posts/rentals-within-reach/POST.md: a single teacher in Phoenix on
$53,000, then Santa Cruz County on $45,000.
Output: posts/rentals-within-reach/images/01-*.png to 05-*.png"""
import base64
import importlib.util
import io
import json
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "posts" / "rentals-within-reach" / "images"
BG, TEXT, MUTED = "#181A1B", "#E4E2DC", "#BBBDC0"
SANS = "/System/Library/Fonts/SFNS.ttf"
DSF = 2

spec = importlib.util.spec_from_file_location("bv", ROOT / "video" / "build_video.py")
bv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bv)


def font(size, bold=False):
    f = ImageFont.truetype(SANS, size)
    try:
        f.set_variation_by_name("Bold" if bold else "Regular")
    except Exception:
        pass
    return f


def wrap(text, f, maxw):
    d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    lines, cur = [], ""
    for w in text.split():
        if d.textlength((cur + " " + w).strip(), font=f) > maxw and cur:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    return lines + [cur]


def titled(img, title, sub):
    """Put the shot under a title and a line saying what was set, on the dark background."""
    pad, f1, f2 = 44, font(40, True), font(26)
    t1, t2 = wrap(title, f1, img.width - 8), wrap(sub, f2, img.width - 8)
    head = pad + len(t1) * 50 + len(t2) * 34 + 34
    out = Image.new("RGB", (img.width + 2 * pad, img.height + head + pad), BG)
    d = ImageDraw.Draw(out)
    for i, ln in enumerate(t1):
        d.text((pad, pad - 6 + i * 50), ln, font=f1, fill=TEXT)
    for i, ln in enumerate(t2):
        d.text((pad, pad + len(t1) * 50 + 4 + i * 34), ln, font=f2, fill=MUTED)
    out.paste(img, (pad, head))
    d.text((pad, out.height - pad + 8), "Built by Data 4 The People", font=font(20), fill=MUTED)
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ch = bv.Chrome(port=9353)
    try:
        ch.cmd("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": "dark"}])
        ch.cmd("Emulation.setDeviceMetricsOverride", width=1240, height=1500, deviceScaleFactor=DSF, mobile=False)
        ch.cmd("Page.navigate", url=f"file://{ROOT / 'dist' / 'index.html'}#embed=0&debug=1")
        for _ in range(120):
            time.sleep(0.25)
            try:
                if ch.js("!!window.__ahdbg"):
                    break
            except Exception:
                pass
        # recording only: a tall page so the whole county panel shows without scrolling
        ch.js("document.getElementById('ah').style.height = '1400px'; document.getElementById('detail').style.flex = 'none'; document.getElementById('rank').style.display = 'none'")
        time.sleep(0.8)

        def tall(on):                  # maps are shot at the normal frame height, panel charts on a tall page
            ch.js(f"document.getElementById('ah').style.height = '{1400 if on else 860}px'")
            time.sleep(0.6)

        def scene(st, inc, pct, sel):
            ch.js(f"""(() => {{ const S = __ahdbg.S; S.st = '{st}'; S.prof = 6; S.inc = {inc}; S.pct = {pct}; S.ht = 0; S.after = true; S.fi = __ahdbg.F.length - 1;
                document.getElementById('state').value = '{st}'; document.getElementById('state').dispatchEvent(new Event('change'));
                S.sel = __ahdbg.byId.get('{sel}'); S.hover = null; __ahdbg.update(); }})()""")
            time.sleep(1.2)
            ch.frame_done()
            c = ch.js(f"(() => {{ const c = __ahdbg.calc(__ahdbg.byId.get('{sel}'), __ahdbg.S.fi); return [Math.round(100 * c.sh.v), Math.round(c.ceil), c.sh.tot]; }})()")
            return c

        def clip(js_rect):
            r = ch.js(js_rect)
            d = ch.cmd("Page.captureScreenshot", format="png", clip=dict(x=r[0], y=r[1], width=r[2], height=r[3], scale=1))["data"]
            return Image.open(io.BytesIO(base64.b64decode(d))).convert("RGB")

        box = lambda sel: f"(() => {{ const r = document.querySelector({json.dumps(sel)}).getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; }})()"
        # one chart from the county panel: from the top of its svg to the bottom of the note under it
        chart = lambda cls: f"""(() => {{ const s = document.querySelector('#detail .{cls}'), n = s.nextElementSibling, a = s.getBoundingClientRect(), b = n.getBoundingClientRect();
            return [a.x - 6, a.y + 1, a.width + 12, b.bottom - a.y + 9]; }})()"""
        # the top of the county panel: name, share, the income-to-ceiling table and the rent bars
        panel = """(() => { const d = document.getElementById('detail').getBoundingClientRect(), n = document.querySelector('#detail .ladder').nextElementSibling.getBoundingClientRect();
            return [d.x, d.y, d.width, n.bottom - d.y + 6]; })()"""
        made = {}

        tall(False)
        pct, ceil, tot = scene("04", 53000, 30, "04013")
        made["01-arizona-map-53k.png"] = titled(clip(box("#mapwrap")), "Arizona: share of rentals within reach on a $53,000 income",
                                               "2020-2024. 30% of after-tax income, taxed as single with no children. Maricopa County is outlined.")
        tall(True)
        scene("04", 53000, 30, "04013")
        made["02-maricopa-rents-by-price.png"] = titled(clip(chart("ladder")), f"Maricopa County: {pct}% of {tot:,} rentals fall under a ${ceil:,} ceiling",
                                                        "Rentals by monthly gross rent, 2020-2024. $53,000 income, 30% after taxes.")
        made["03-maricopa-change-in-rentals.png"] = titled(clip(chart("cols")), "Maricopa County: more rentals, fewer within reach on $53,000",
                                                           "Change from 2005-2009 to 2020-2024. Income held at $53,000 in 2024 dollars.")
        facts = {"maricopa_30": [pct, ceil, tot]}
        tall(False)
        pct50, ceil50, _ = scene("04", 53000, 50, "04013")
        facts["maricopa_50"] = [pct50, ceil50]
        made["04-arizona-map-53k-at-50-percent.png"] = titled(clip(box("#mapwrap")), "Arizona: the same $53,000 income, spending 50% on rent",
                                                             "2020-2024. 50% of after-tax income, taxed as single with no children.")
        tall(True)
        p2, c2, t2 = scene("04", 45000, 30, "04023")
        facts["santa_cruz_30"] = [p2, c2, t2]
        made["05-santa-cruz-45k.png"] = titled(clip(panel), "Santa Cruz County, Arizona, on a $45,000 income",
                                              "2020-2024. 30% of after-tax income, taxed as single with no children.")
        for name, im in made.items():
            im.save(OUT / name, optimize=True)
            print(name, im.size)
        (ROOT / "data" / "processed" / "post_facts.json").write_text(json.dumps(facts))
        print(facts)
    finally:
        ch.close()


if __name__ == "__main__":
    main()
