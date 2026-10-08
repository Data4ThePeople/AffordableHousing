"""Hero image for the post: the default bubble map at hero scale beside the title and the headline count.

Same layout as the child poverty viz hero. The map is shot from dist/index.html in headless Chrome with
the dark palette, the headline count is read from the page, and the card is drawn at 1546 x 994 so
that `hero pad` brings it to 1680 x 1080 without scaling type.
Output: posts/rentals-within-reach/images/rentals-within-reach-hero-source.png"""
import base64
import importlib.util
import io
import re
import time
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "posts" / "rentals-within-reach" / "images"
BUILD = ROOT / "video" / "build"
BG, TEXT, MUTED, DIM = "#181A1B", "#BBBDC0", "#8C9094", "#6E7377"
CW, CH = 1546, 994
RAMP = ["#7a0f1a", "#cf3b2c", "#f08a3c", "#f7dc6f", "#7cc6a4", "#08606b"]

spec = importlib.util.spec_from_file_location("bv", ROOT / "video" / "build_video.py")
bv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bv)


def main():
    BUILD.mkdir(parents=True, exist_ok=True)
    ch = bv.Chrome(port=9355)
    try:
        ch.cmd("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": "dark"}])
        ch.cmd("Emulation.setDeviceMetricsOverride", width=1500, height=940, deviceScaleFactor=2, mobile=False)
        ch.cmd("Page.navigate", url=f"file://{ROOT / 'dist' / 'index.html'}#embed=0&debug=1")
        for _ in range(120):
            time.sleep(0.25)
            try:
                if ch.js("!!window.__ahdbg"):
                    break
            except Exception:
                pass
        ch.js("document.getElementById('ah').style.height = '940px'; document.getElementById('legend').style.display = 'none'; document.querySelector('.zoom').style.display = 'none'; document.getElementById('stamp').style.display = 'none'; document.querySelector('.mapwrap').style.border = '0'")
        # recording only: the map takes the hero's background, then the page re-reads its colors (it does so
        # whenever the color scheme changes) and refits the map to its resized box
        ch.js(f"""(() => {{ const e = document.getElementById('ah'); e.style.setProperty('--panel', '{BG}'); e.style.setProperty('--nohist', '#22262A');
            e.style.setProperty('--edge', 'rgba(255,255,255,.07)'); e.style.setProperty('--state', '#5B6266'); e.style.setProperty('--line', '{BG}'); }})()""")
        ch.cmd("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": "light"}])
        time.sleep(0.4)
        ch.cmd("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": "dark"}])
        time.sleep(0.6)
        ch.js("document.getElementById('state').dispatchEvent(new Event('change'))")
        time.sleep(1.5)
        ch.frame_done()
        sub = ch.js("document.getElementById('sub').textContent")
        m_ = re.search(r"In ([\d,]+) of ([\d,]+) counties the share is under half", sub)
        under, total = m_.group(1), m_.group(2)
        r = ch.js("(() => { const r = document.getElementById('mapbox').getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; })()")
        d = ch.cmd("Page.captureScreenshot", format="png", clip=dict(x=r[0], y=r[1], width=r[2], height=r[3], scale=1))["data"]
        m = Image.open(io.BytesIO(base64.b64decode(d))).convert("RGB")
        m.save(BUILD / "hero-map.png")
        ticks = ["30%", "40%", "50%", "65%", "80%"]
        html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
        html,body{{margin:0;width:{CW}px;height:{CH}px;overflow:hidden;background:{BG};color:{TEXT};
          font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}
        .head{{position:absolute;left:40px;top:44px;font-size:30px;font-weight:700;color:{TEXT}}}
        .map{{position:absolute;left:0;top:96px;width:1030px;height:auto}}
        .leg{{position:absolute;left:60px;top:850px;width:560px}}
        .leg .cap{{font-size:18px;color:{MUTED};margin-bottom:8px;display:flex;justify-content:space-between}}
        .leg .strip{{display:flex;height:24px;border-radius:3px;overflow:hidden}}
        .leg .strip span{{flex:1}}
        .leg .ticks{{position:relative;height:28px;font-size:18px;color:{TEXT};margin-top:6px}}
        .leg .ticks span{{position:absolute;transform:translateX(-50%)}}
        .txt{{position:absolute;left:1040px;top:0;bottom:0;width:480px;display:flex;flex-direction:column;justify-content:center}}
        h1{{font-size:70px;line-height:1.02;margin:0 0 56px;font-weight:800;color:{TEXT}}}
        .big{{font-size:124px;font-weight:800;line-height:1;color:#f08a3c}}
        .of{{font-size:40px;font-weight:700;margin-top:10px;color:{TEXT}}}
        .what{{font-size:27px;line-height:1.3;margin-top:18px;color:{TEXT}}}
        .where{{font-size:21px;line-height:1.35;color:{MUTED};margin-top:44px}}
        .src{{position:absolute;left:1040px;bottom:60px;font-size:16px;color:{DIM}}}
        </style></head><body>
        <div class="head">Share of rentals the median renter household can afford, by county, 2020-2024</div>
        <img class="map" src="file://{BUILD / 'hero-map.png'}">
        <div class="leg"><div class="cap"><span>Fewer within reach</span><span>More within reach</span></div>
          <div class="strip">{''.join(f'<span style="background:{c}"></span>' for c in RAMP)}</div>
          <div class="ticks">{''.join(f'<span style="left:{(i + 1) / 6 * 100:.2f}%">{t}</span>' for i, t in enumerate(ticks))}</div></div>
        <div class="txt"><h1>Rentals<br>Within<br>Reach</h1>
          <div class="big">{under}</div>
          <div class="of">of {total} counties</div>
          <div class="what">where the median renter household can afford fewer than half the rentals</div>
          <div class="where">Every U.S. county<br>2005-2009 to 2020-2024</div></div>
        <div class="src">Data 4 The People &nbsp;&middot;&nbsp; Source: U.S. Census Bureau, ACS</div>
        </body></html>"""
        p = BUILD / "hero.html"
        p.write_text(html)
        ch.cmd("Emulation.setEmulatedMedia", features=[])
        ch.cmd("Emulation.setDeviceMetricsOverride", width=CW, height=CH, deviceScaleFactor=1, mobile=False)
        ch.cmd("Page.navigate", url=f"file://{p}")
        time.sleep(1.5)
        out = IMG / "rentals-within-reach-hero-source.png"
        ch.shot().save(out, optimize=True)
        print("wrote", out, "headline figure", under, "of", total)
    finally:
        ch.close()


if __name__ == "__main__":
    main()
