"use strict";
// Rentals Within Reach. Vanilla JS on canvas; every number is computed here from DATA.
(async function () {
  const root = document.getElementById("ah");
  let framed = false;
  try { framed = window.self !== window.top; } catch (e) { framed = true; }
  const hashFlags = new URLSearchParams(location.hash.slice(1));
  if (hashFlags.get("embed") === "1") framed = true;
  if (hashFlags.get("embed") === "0") framed = false;
  if (framed) { root.classList.add("framed"); document.documentElement.setAttribute("data-theme", "light"); }

  const $ = (id) => document.getElementById(id);
  const TOP_N = 25;
  // Fixed class breaks (percent of rentals within reach), the same in every period.
  const BINS = [15, 30, 45, 60, 75, 90];
  const VARS = ["--s0", "--s1", "--s2", "--s3", "--s4", "--s5", "--s6"];
  const PROF = ["20th percentile household", "40th percentile household", "median household", "60th percentile household", "80th percentile household", "median renter household", "household"];
  const PROF_SHORT = ["20th percentile income", "40th percentile income", "Median household income", "60th percentile income", "80th percentile income", "Median renter income", "Income entered"];
  // where each period sits on the trend chart's time axis
  const MID = { "1980": 1980, "1990": 1990, "2000": 2000, "2009": 2007, "2014": 2012, "2019": 2017, "2024": 2022 };

  // ---------- data ----------
  async function loadData() {
    const bin = Uint8Array.from(atob(DATA_B64), (c) => c.charCodeAt(0));
    const stream = new Blob([bin]).stream().pipeThrough(new DecompressionStream("gzip"));
    return JSON.parse(await new Response(stream).text());
  }
  const DATA = await loadData();
  const F = DATA.frames, NF = F.length, GRID = DATA.grid;
  const U = DATA.units;
  const byId = new Map();
  for (const u of U) {
    if (byId.has(u.id)) throw new Error("duplicate unit id " + u.id);
    byId.set(u.id, u);
  }
  const ST = Object.keys(DATA.states).sort();
  const stIdx = {}; ST.forEach((s, i) => (stIdx[s] = i));
  const TAXINC = DATA.tax.inc;

  // ---------- geometry ----------
  function buildPath(polys, bb) {
    const p = new Path2D();
    for (const rings of polys) for (const a of rings) {
      let x = 0, y = 0;
      for (let i = 0; i < a.length; i += 2) {
        x += a[i]; y += a[i + 1];
        if (i) p.lineTo(x, y); else p.moveTo(x, y);
        if (bb) { if (x < bb[0]) bb[0] = x; if (x > bb[2]) bb[2] = x; if (y < bb[1]) bb[1] = y; if (y > bb[3]) bb[3] = y; }
      }
      p.closePath();
    }
    return p;
  }
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  const stateBB = {};
  for (const u of U) {
    const g = DATA.geo[u.id];
    if (!g) throw new Error("unit with no shape " + u.id);
    u.bb = [Infinity, Infinity, -Infinity, -Infinity];
    u.path = buildPath(g, u.bb);
    minX = Math.min(minX, u.bb[0]); minY = Math.min(minY, u.bb[1]); maxX = Math.max(maxX, u.bb[2]); maxY = Math.max(maxY, u.bb[3]);
    const b = stateBB[u.s] || (stateBB[u.s] = [Infinity, Infinity, -Infinity, -Infinity]);
    b[0] = Math.min(b[0], u.bb[0]); b[1] = Math.min(b[1], u.bb[1]); b[2] = Math.max(b[2], u.bb[2]); b[3] = Math.max(b[3], u.bb[3]);
  }
  const borders = DATA.borders.map((b) => buildPath(b, null));
  const GX = 60, GY = 40, cellW = (maxX - minX) / GX, cellH = (maxY - minY) / GY;
  const cells = Array.from({ length: GX * GY }, () => []);
  for (const u of U) {
    const x0 = Math.max(0, Math.floor((u.bb[0] - minX) / cellW)), x1 = Math.min(GX - 1, Math.floor((u.bb[2] - minX) / cellW));
    const y0 = Math.max(0, Math.floor((u.bb[1] - minY) / cellH)), y1 = Math.min(GY - 1, Math.floor((u.bb[3] - minY) / cellH));
    for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) cells[y * GX + x].push(u);
  }
  const hitCtx = document.createElement("canvas").getContext("2d");
  function hitShape(gx, gy) {
    const cx = Math.floor((gx - minX) / cellW), cy = Math.floor((gy - minY) / cellH);
    if (cx < 0 || cy < 0 || cx >= GX || cy >= GY) return null;
    for (const u of cells[cy * GX + cx]) {
      if (gx < u.bb[0] || gx > u.bb[2] || gy < u.bb[1] || gy > u.bb[3]) continue;
      if (hitCtx.isPointInPath(u.path, gx, gy, "evenodd")) return u;
    }
    return null;
  }

  // ---------- state ----------
  const S = { fi: NF - 1, prof: 2, inc: 60000, pct: 30, after: true, ht: 1, st: "", bub: false, sel: null, hover: null, rankTab: 0 };
  const inState = (u) => !S.st || u.s === S.st;

  // Total tax (federal and state income tax plus the employee's payroll tax) on an income, from the grid.
  function taxOn(fi, ht, s, inc) {
    const t = DATA.tax.t[fi][ht][stIdx[s]], n = TAXINC.length;
    if (inc <= 0) return 0;
    if (inc >= TAXINC[n - 1]) return (t[n - 1] / TAXINC[n - 1]) * inc;
    let lo = 0, hi = n - 1;
    while (hi - lo > 1) { const m = (lo + hi) >> 1; if (TAXINC[m] <= inc) lo = m; else hi = m; }
    return t[lo] + ((t[hi] - t[lo]) * (inc - TAXINC[lo])) / (TAXINC[hi] - TAXINC[lo]);
  }
  // Share of cash-rent units at or under a monthly rent ceiling.
  // v: straight-line estimate inside the bucket the ceiling falls in. lo, hi: the two direct reads on either side.
  // top: the ceiling is in the open top bucket, so v is a floor ("at least").
  function shareOf(r, edges, c) {
    let tot = 0; for (const x of r) tot += x;
    if (!tot) return null;
    let cum = 0;
    for (let i = 0; i < r.length; i++) {
      const a = edges[i], b = edges[i + 1];
      if (b === undefined) return c >= a ? { v: cum / tot, lo: cum / tot, hi: 1, top: true, bi: i, tot } : { v: cum / tot, lo: cum / tot, hi: cum / tot, bi: i, tot };
      if (c >= b) { cum += r[i]; continue; }
      if (c <= a) return { v: cum / tot, lo: cum / tot, hi: cum / tot, bi: i, tot };
      return { v: (cum + (r[i] * (c - a)) / (b - a)) / tot, lo: cum / tot, hi: (cum + r[i]) / tot, bi: i, tot };
    }
    return null;
  }
  // The whole calculation for one unit and period.
  function calc(u, fi) {
    const f = u.f[fi];
    if (f.x) return { blank: f.x };
    const inc = S.prof === 6 ? S.inc * F[fi].cpi : f.p[S.prof];
    if (inc === null || inc === undefined) return { noinc: true };
    const tax = S.after ? taxOn(fi, S.ht, u.s, inc) : 0;
    const net = inc - tax;
    const ceil = (S.pct / 100) * net / 12;
    const sh = shareOf(f.r, F[fi].re, ceil);
    if (!sh) return { norent: true };
    return { inc, tax, net, ceil, sh, est: S.prof < 5 && !!((f.e >> S.prof) & 1), lo: !!f.lo, f };
  }
  function binOf(v) { let i = 0; while (i < BINS.length && v >= BINS[i]) i++; return i; }
  function value(u, fi) {
    const c = calc(u, fi);
    if (!c.sh) return { cls: "none", c };
    const v = 100 * c.sh.v;
    return { v, cls: binOf(v), c };
  }
  const shaded = (v) => typeof v.cls === "number";
  // All counties together: rentals within reach of the local household, added up. An editorial sum.
  function total(fi, st) {
    let a = 0, t = 0, n = 0, under = 0, top = 0;
    for (const u of U) {
      if (st && u.s !== st) continue;
      const c = calc(u, fi);
      if (!c.sh) continue;
      a += c.sh.v * c.sh.tot; t += c.sh.tot; n++;
      if (c.sh.v < 0.5) under++;
      if (c.sh.top) top++;
    }
    return t ? { v: (100 * a) / t, n, under, top, units: t } : null;
  }

  // ---------- colors ----------
  let C = {};
  function hatch(bg, line, w, cross) {
    const pc = document.createElement("canvas"); pc.width = pc.height = 8;
    const x = pc.getContext("2d");
    if (bg) { x.fillStyle = bg; x.fillRect(0, 0, 8, 8); }
    x.strokeStyle = line; x.lineWidth = w; x.beginPath(); x.moveTo(-2, 10); x.lineTo(10, -2); x.moveTo(-2, 2); x.lineTo(2, -2); x.moveTo(6, 10); x.lineTo(10, 6);
    if (cross) { x.moveTo(-2, -2); x.lineTo(10, 10); x.moveTo(-2, 6); x.lineTo(2, 10); x.moveTo(6, -2); x.lineTo(10, 2); }
    x.stroke();
    return bctx.createPattern(pc, "repeat");
  }
  function readColors() {
    const cs = getComputedStyle(root);
    const g = (n) => cs.getPropertyValue(n).trim();
    C = { seq: VARS.map(g), nohist: g("--nohist"), hatch: g("--hatch"), mark: g("--mark"),
      edge: g("--edge"), state: g("--state"), hi: g("--hi"), panel: g("--panel"), ink3: g("--ink-3"), accent: g("--accent") };
    C.nonePat = hatch(C.nohist, C.hatch, 1.2, true);    // crosshatch: no figure
    C.markPat = hatch(null, C.mark, 1);                 // overlay: few rentals, low reliability
  }
  const colorOf = (val) => (shaded(val) ? C.seq[val.cls] : C.nonePat);

  // ---------- canvas & view ----------
  const cv = $("map"), wrap = $("mapbox");
  const ctx = cv.getContext("2d");
  let W = 0, H = 0, dpr = 1;
  const view = { k: 1, tx: 0, ty: 0 };
  function fitBox(bb, pad = 0.06, maxK = Infinity) {
    const bw = bb[2] - bb[0], bh = bb[3] - bb[1];
    const k = Math.min(maxK, Math.min(W * (1 - 2 * pad) / bw, H * (1 - 2 * pad) / bh));
    view.k = k; view.tx = (W - bw * k) / 2 - bb[0] * k; view.ty = (H - bh * k) / 2 - bb[1] * k;
  }
  let homeK = 1, pendingSel = null;
  function home() {
    if (S.st && stateBB[S.st]) fitBox(stateBB[S.st]); else fitBox([minX, minY, maxX, maxY], 0.03);
    if (!S.st) homeK = view.k;
  }
  function resize() {
    const r = wrap.getBoundingClientRect();
    const first = W === 0;
    dpr = Math.min(2, window.devicePixelRatio || 1);
    W = r.width; H = r.height;
    cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
    if (first) {
      fitBox([minX, minY, maxX, maxY], 0.03); homeK = view.k; home();
      if (pendingSel) { select(pendingSel, true); pendingSel = null; return; }
    }
    draw();
  }

  let vals = new Map();
  function computeVals() { vals = new Map(); for (const u of U) vals.set(u.id, value(u, S.fi)); }

  // bubbles: area in proportion to the county's cash-rent units; they grow a little as the map zooms
  const maxUnits = Math.max(...U.map((u) => Math.max(...u.f.map((f) => (f.r ? f.r.reduce((a, b) => a + b, 0) : 0)))));
  function bubR(u) {
    const v = vals.get(u.id);
    const n = v.c.sh ? v.c.sh.tot : (u.f[S.fi].r || []).reduce((a, b) => a + b, 0);
    if (!n) return 0;
    return Math.max(1.2, 30 * Math.sqrt(n / maxUnits) * Math.sqrt(view.k / homeK));
  }
  let bubList = [];

  const base = document.createElement("canvas"), bctx = base.getContext("2d");
  const prev = document.createElement("canvas"), pctx = prev.getContext("2d");
  let frame = 0, baseDirty = true, baseView = null, settleT = 0, fadeT0 = 0;
  const FADE_MS = 350;
  function schedule() { if (!W) return; cancelAnimationFrame(frame); frame = requestAnimationFrame(render); }
  function draw(fade) {
    if (fade && baseView && base.width) {
      if (prev.width !== base.width || prev.height !== base.height) { prev.width = base.width; prev.height = base.height; }
      pctx.setTransform(1, 0, 0, 1, 0, 0); pctx.drawImage(base, 0, 0);
      fadeT0 = performance.now();
    }
    baseDirty = true; schedule();
  }
  function drawOverlay() { schedule(); }
  function interact() {
    fadeT0 = 0;
    if (!baseView) baseDirty = true;
    schedule(); clearTimeout(settleT); settleT = setTimeout(() => draw(false), 160);
  }
  function render(now) {
    if (baseDirty) { renderBase(); baseDirty = false; }
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.fillStyle = C.panel; ctx.fillRect(0, 0, cv.width, cv.height);
    const r = view.k / baseView.k;
    ctx.setTransform(r, 0, 0, r, dpr * (view.tx - baseView.tx * r), dpr * (view.ty - baseView.ty * r));
    const a = fadeT0 ? Math.min(1, ((now || performance.now()) - fadeT0) / FADE_MS) : 1;
    if (a < 1) { ctx.drawImage(prev, 0, 0); ctx.globalAlpha = a; }
    ctx.drawImage(base, 0, 0);
    ctx.globalAlpha = 1;
    ctx.setTransform(dpr * view.k, 0, 0, dpr * view.k, dpr * view.tx, dpr * view.ty);
    const lw = 1 / view.k;
    ctx.lineJoin = "round";
    const outline = (u, w) => {
      ctx.strokeStyle = C.hi; ctx.lineWidth = w * lw;
      if (S.bub) { const rr = bubR(u) / view.k; if (rr) { ctx.beginPath(); ctx.arc(u.c[0], u.c[1], rr, 0, 6.2832); ctx.stroke(); } }
      ctx.stroke(u.path);
    };
    if (S.sel) outline(S.sel, 2.4);
    if (S.hover && S.hover !== S.sel) outline(S.hover, 1.6);
    if (a < 1) schedule(); else fadeT0 = 0;
  }
  function renderBase() {
    if (base.width !== cv.width || base.height !== cv.height) { base.width = cv.width; base.height = cv.height; }
    const c = bctx;
    c.setTransform(1, 0, 0, 1, 0, 0);
    c.fillStyle = C.panel; c.fillRect(0, 0, base.width, base.height);
    c.setTransform(dpr * view.k, 0, 0, dpr * view.k, dpr * view.tx, dpr * view.ty);
    const x0 = -view.tx / view.k, y0 = -view.ty / view.k, x1 = (W - view.tx) / view.k, y1 = (H - view.ty) / view.k;
    const lw = 1 / view.k;
    const inv = new DOMMatrix().scale(1 / view.k);
    C.nonePat.setTransform(inv); C.markPat.setTransform(inv);
    c.lineJoin = "round";
    c.strokeStyle = C.edge; c.lineWidth = 0.6 * lw;
    for (const u of U) {
      if (u.bb[2] < x0 || u.bb[0] > x1 || u.bb[3] < y0 || u.bb[1] > y1) continue;
      const v = vals.get(u.id);
      c.globalAlpha = S.st && !inState(u) ? 0.18 : 1;
      c.fillStyle = S.bub ? C.nohist : colorOf(v);
      c.fill(u.path, "evenodd");
      if (!S.bub && shaded(v) && v.c.lo) { c.fillStyle = C.markPat; c.fill(u.path, "evenodd"); }
      c.stroke(u.path);
    }
    c.globalAlpha = 1;
    c.strokeStyle = C.state; c.lineWidth = 0.9 * lw;
    for (const b of borders) c.stroke(b);
    bubList = [];
    if (S.bub) {
      for (const u of U) {
        const v = vals.get(u.id);
        if (!shaded(v)) continue;
        const rr = bubR(u) / view.k;
        if (u.c[0] + rr < x0 || u.c[0] - rr > x1 || u.c[1] + rr < y0 || u.c[1] - rr > y1) continue;
        bubList.push([u, rr, v]);
      }
      bubList.sort((p, q) => q[1] - p[1]);                 // large first, so small ones stay on top
      c.strokeStyle = C.panel; c.lineWidth = 1 * lw;       // a surface-colored ring separates overlapping bubbles
      for (const [u, rr, v] of bubList) {
        c.globalAlpha = S.st && !inState(u) ? 0.15 : 1;
        c.beginPath(); c.arc(u.c[0], u.c[1], rr, 0, 6.2832);
        c.fillStyle = C.seq[v.cls]; c.fill(); c.stroke();
      }
      c.globalAlpha = 1;
    }
    baseView = { k: view.k, tx: view.tx, ty: view.ty };
  }

  // pan & zoom
  function zoomAt(f, sx, sy) {
    const k = Math.max(homeK * 0.8, Math.min(homeK * 60, view.k * f));
    const gx = (sx - view.tx) / view.k, gy = (sy - view.ty) / view.k;
    view.k = k; view.tx = sx - gx * k; view.ty = sy - gy * k;
    interact();
  }
  cv.addEventListener("wheel", (e) => { e.preventDefault(); const r = cv.getBoundingClientRect(); zoomAt(Math.exp(-e.deltaY * 0.0015), e.clientX - r.left, e.clientY - r.top); }, { passive: false });
  $("zin").onclick = () => zoomAt(1.6, W / 2, H / 2);
  $("zout").onclick = () => zoomAt(1 / 1.6, W / 2, H / 2);
  const ptrs = new Map();
  let drag = null, moved = false, pinch = null;
  cv.addEventListener("pointerdown", (e) => {
    cv.setPointerCapture(e.pointerId); ptrs.set(e.pointerId, [e.clientX, e.clientY]);
    moved = false;
    if (ptrs.size === 1) drag = { x: e.clientX, y: e.clientY, tx: view.tx, ty: view.ty };
    if (ptrs.size === 2) { const [a, b] = [...ptrs.values()]; pinch = { d: Math.hypot(a[0] - b[0], a[1] - b[1]), k: view.k }; drag = null; }
  });
  cv.addEventListener("pointermove", (e) => {
    const r = cv.getBoundingClientRect();
    if (ptrs.has(e.pointerId)) ptrs.set(e.pointerId, [e.clientX, e.clientY]);
    if (pinch && ptrs.size === 2) {
      const [a, b] = [...ptrs.values()];
      const dd = Math.hypot(a[0] - b[0], a[1] - b[1]);
      zoomAt((pinch.k * dd / pinch.d) / view.k, (a[0] + b[0]) / 2 - r.left, (a[1] + b[1]) / 2 - r.top);
      moved = true; return;
    }
    if (drag) {
      const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
      if (Math.abs(dx) + Math.abs(dy) > 3) { moved = true; cv.classList.add("drag"); }
      if (moved) { view.tx = drag.tx + dx; view.ty = drag.ty + dy; hideTip(); interact(); return; }
    }
    if (e.pointerType === "mouse") hoverAt(e.clientX - r.left, e.clientY - r.top);
  });
  const endPtr = (e) => {
    ptrs.delete(e.pointerId);
    if (ptrs.size < 2) pinch = null;
    if (ptrs.size === 0) {
      cv.classList.remove("drag");
      if (drag && !moved) {
        const r = cv.getBoundingClientRect();
        const u = pick(e.clientX - r.left, e.clientY - r.top);
        select(u, false);
        if (e.pointerType !== "mouse") { S.hover = u; if (u) showTip(u, e.clientX - r.left, e.clientY - r.top); else hideTip(); }
      }
      drag = null;
    }
  };
  cv.addEventListener("pointerup", endPtr);
  cv.addEventListener("pointercancel", endPtr);
  cv.addEventListener("pointerleave", () => { if (!drag) { S.hover = null; hideTip(); showDetail(S.sel); drawOverlay(); } });

  let clearT = 0;
  function pick(sx, sy) {
    const gx = (sx - view.tx) / view.k, gy = (sy - view.ty) / view.k;
    if (S.bub) {                                            // smallest bubble under the pointer, with a 4px margin
      const pad = 4 / view.k;
      for (let i = bubList.length - 1; i >= 0; i--) {
        const [u, rr] = bubList[i];
        if (Math.hypot(gx - u.c[0], gy - u.c[1]) <= rr + pad) return u;
      }
    }
    return hitShape(gx, gy);
  }
  function hoverAt(sx, sy) {
    const u = pick(sx, sy);
    if (u !== S.hover) {
      S.hover = u; drawOverlay();
      clearTimeout(clearT);
      if (u) showDetail(u); else clearT = setTimeout(() => { if (!S.hover) showDetail(S.sel); }, 250);
    }
    if (u) showTip(u, sx, sy); else hideTip();
  }

  // ---------- formatting ----------
  const nf = new Intl.NumberFormat("en-US");
  const MINUS = "−";
  const usd = (v) => (v < 0 ? MINUS : "") + "$" + nf.format(Math.abs(Math.round(v)));
  const pc = (v) => ((v > 0 && v < 1) || (v > 99 && v < 100) ? v.toFixed(1) : v.toFixed(0)) + "%";
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const flabel = (fi) => F[fi].label;
  const whose = () => (S.prof === 6 ? `a household with ${usd(S.inc)} in 2024 dollars` : `the ${PROF[S.prof]}`);
  const setup = () => `${S.pct}% of ${S.after ? "after-tax" : "pre-tax"} income${S.after ? `, taxed as ${DATA.tax.types[S.ht].toLowerCase()}` : ""}`;
  function bigLine(c) {
    return `${c.sh.top ? "At least " : ""}${pc(100 * c.sh.v)} of rentals within reach`;
  }
  function noFigure(u, c, fi) {
    if (c.blank) return `Not shown for ${flabel(fi)}: ${c.blank}, so earlier figures cover a different area.`;
    if (c.noinc) return S.prof === 5 ? `The Census Bureau publishes no median renter income for this county in ${flabel(fi)}. It is available from 2005-2009 on, and not for joined or rebuilt areas.`
      : `This income level falls in the open top income bucket for ${flabel(fi)}, so it cannot be estimated here.`;
    return `No rentals paying cash rent are recorded here for ${flabel(fi)}.`;
  }
  function mathTable(c, fi) {
    let h = `<table class="math"><tr><td>${PROF_SHORT[S.prof]}${S.prof === 6 ? `, in ${F[fi].y} dollars` : `, ${F[fi].y}`}</td><td>${usd(c.inc)}</td></tr>`;
    if (S.after) h += `<tr><td>${c.tax < 0 ? "Plus tax credits, net of taxes" : "Less income and payroll taxes"}</td><td>${c.tax < 0 ? "+" + usd(-c.tax) : MINUS + usd(c.tax)}</td></tr>`
      + `<tr><td>Income after taxes</td><td>${usd(c.net)}</td></tr>`;
    h += `<tr class="eq"><td>Rent ceiling (${S.pct}%, per month)</td><td>${usd(c.ceil)}</td></tr></table>`;
    return h;
  }
  function rangeLine(c) {
    if (c.sh.top) return `The ceiling is above ${usd(F[S.fi].re[F[S.fi].re.length - 1])}, the top of the Census rent scale for this period, so the true share is somewhere from ${pc(100 * c.sh.lo)} to 100%.`;
    if (c.sh.lo === c.sh.hi) return `Direct Census read: ${pc(100 * c.sh.lo)}.`;
    return `Direct Census reads: ${pc(100 * c.sh.lo)} in rent buckets fully under the ceiling, ${pc(100 * c.sh.hi)} counting the bucket the ceiling falls in. ${pc(100 * c.sh.v)} is our estimate between them.`;
  }

  // ---------- tooltip ----------
  const tip = $("tip");
  function showTip(u, sx, sy) {
    const v = vals.get(u.id), c = v.c;
    let h = `<b>${esc(u.n)}</b>`;
    if (!c.sh) h += `<div class="src">${esc(noFigure(u, c, S.fi))}</div>`;
    else h += `<div>${bigLine(c)}</div><table class="math"><tr><td>Rent ceiling</td><td>${usd(c.ceil)} a month</td></tr><tr><td>Rentals paying cash rent</td><td>${nf.format(c.sh.tot)}</td></tr></table>`
      + (c.lo ? `<div class="src">Few rentals in the sample. Treat with care.</div>` : "");
    tip.innerHTML = h;
    tip.hidden = false;
    const tw = tip.offsetWidth, th = tip.offsetHeight;
    let x = sx + 14, y = sy + 14;
    if (x + tw > W - 6) x = sx - tw - 14;
    if (y + th > H - 6) y = sy - th - 14;
    tip.style.left = Math.max(4, x) + "px"; tip.style.top = Math.max(4, y) + "px";
  }
  function hideTip() { tip.hidden = true; }

  // ---------- detail: the rent ladder and the trend ----------
  // Rentals in each Census rent bucket, with the ceiling drawn across them.
  function ladder(u, c) {
    const r = c.f.r, e = F[S.fi].re, n = r.length;
    const w = 300, h = 112, l = 4, rt = 4, t = 16, b = 18;
    const bw = (w - l - rt) / n, mx = Math.max(...r, 1);
    const ys = (v) => t + (1 - v / mx) * (h - t - b);
    let bars = "";
    for (let i = 0; i < n; i++) {
      const x = l + i * bw, y = ys(r[i]), hh = h - b - y;
      const name = e[i + 1] === undefined ? `${usd(e[i])} or more` : i === 0 ? `Under ${usd(e[1])}` : `${usd(e[i])} to ${usd(e[i + 1] - 1)}`;
      const frac = i < c.sh.bi ? 1 : i > c.sh.bi ? 0 : e[i + 1] === undefined ? 0 : Math.max(0, Math.min(1, (c.ceil - e[i]) / (e[i + 1] - e[i])));
      bars += `<g><title>${name} a month: ${nf.format(r[i])} rentals</title><rect x="${(x + 1).toFixed(1)}" y="${y.toFixed(1)}" width="${(bw - 2).toFixed(1)}" height="${Math.max(hh, 0.5).toFixed(1)}" fill="var(--hatch)"/>`
        + (frac > 0 ? `<rect x="${(x + 1).toFixed(1)}" y="${y.toFixed(1)}" width="${((bw - 2) * frac).toFixed(1)}" height="${Math.max(hh, 0.5).toFixed(1)}" fill="var(--accent)"/>` : "")
        + `<rect x="${x.toFixed(1)}" y="${t}" width="${bw.toFixed(1)}" height="${h - t - b}" fill="transparent"/></g>`;
    }
    const bi = c.sh.bi, fr = e[bi + 1] === undefined ? (c.sh.top ? 0.5 : 0) : Math.max(0, Math.min(1, (c.ceil - e[bi]) / (e[bi + 1] - e[bi])));
    const cx = l + (bi + fr) * bw;
    const anchor = cx > w * 0.6 ? "end" : "start";
    const line = `<line x1="${cx.toFixed(1)}" x2="${cx.toFixed(1)}" y1="${t - 3}" y2="${h - b}" stroke="var(--ink)" stroke-width="1.5" stroke-dasharray="4 3"/>`
      + `<text x="${(cx + (anchor === "end" ? -4 : 4)).toFixed(1)}" y="${t - 5}" text-anchor="${anchor}" font-size="10.5" fill="var(--ink)">${usd(c.ceil)} ceiling</text>`;
    const step = Math.ceil(n / 5);
    let ticks = "";
    for (let i = step; i < n; i += step) ticks += `<text x="${(l + i * bw).toFixed(1)}" y="${h - 5}" text-anchor="middle" font-size="10" fill="var(--ink-3)">${usd(e[i])}</text>`;
    return `<h3>Rentals by monthly rent, ${flabel(S.fi)}</h3>`
      + `<svg class="ladder" viewBox="0 0 ${w} ${h}" role="img" aria-label="Rentals in each rent bucket, ${esc(u.n)}, with the rent ceiling at ${usd(c.ceil)}">`
      + `<line x1="${l}" x2="${w - rt}" y1="${h - b}" y2="${h - b}" stroke="var(--line)"/>${bars}${line}${ticks}</svg>`
      + `<div class="src">Dark bars are within reach. Buckets are the Census Bureau's and are wider at higher rents.</div>`;
  }
  // Share within reach in every period: this county, its state, the country.
  function spark(u) {
    const series = [
      { key: "u", pts: F.map((f, i) => { const c = calc(u, i); return c.sh ? 100 * c.sh.v : null; }) },
      { key: "st", pts: F.map((f, i) => { const t = total(i, u.s); return t ? t.v : null; }) },
      { key: "us", pts: usTrend() },
    ];
    const w = 300, h = 110, l = 30, r = 34, t = 8, b = 18;
    const x0 = MID[F[0].k], x1 = MID[F[NF - 1].k];
    const xs = (i) => l + ((MID[F[i].k] - x0) / (x1 - x0)) * (w - l - r);
    const ys = (v) => t + (1 - v / 100) * (h - t - b);
    const path = (pts) => { let d = "", pen = false; pts.forEach((v, i) => { if (v === null) { pen = false; return; } d += `${pen ? "L" : "M"}${xs(i).toFixed(1)},${ys(v).toFixed(1)}`; pen = true; }); return d; };
    const grid = [0, 50, 100].map((v) => `<line x1="${l}" x2="${w - r}" y1="${ys(v)}" y2="${ys(v)}" stroke="var(--grid)"/><text x="${l - 4}" y="${ys(v) + 3.5}" text-anchor="end" font-size="10" fill="var(--ink-3)">${v}%</text>`).join("");
    const xl = [0, 2, NF - 1].map((i) => `<text x="${xs(i)}" y="${h - 4}" text-anchor="${i === NF - 1 ? "end" : "middle"}" font-size="10" fill="var(--ink-3)">${i === NF - 1 ? "2020-24" : F[i].label}</text>`).join("");
    const up = series[0].pts;
    const dots = up.map((v, i) => (v === null ? "" : `<circle cx="${xs(i).toFixed(1)}" cy="${ys(v).toFixed(1)}" r="${i === S.fi ? 4 : 2.2}" fill="var(--accent)"${i === S.fi ? ' stroke="var(--panel)" stroke-width="2"' : ""}><title>${flabel(i)}: ${pc(v)}</title></circle>`)).join("");
    const last = up[NF - 1];
    const endLab = last === null ? "" : `<text x="${w - r + 5}" y="${ys(last) + 3.5}" font-size="10.5" font-weight="600" fill="var(--ink)">${pc(last)}</text>`;
    return `<h3>Share within reach over time</h3><div class="key"><span><i></i>This county</span><span><i class="st"></i>${esc(DATA.states[u.s][1])}</span><span><i class="us"></i>United States</span></div>`
      + `<svg class="spark" viewBox="0 0 ${w} ${h}" role="img" aria-label="Share of rentals within reach by period, ${esc(u.n)}, its state and the United States">${grid}${xl}`
      + `<path d="${path(series[2].pts)}" fill="none" stroke="var(--ink-3)" stroke-width="2" stroke-dasharray="1.5 3"/>`
      + `<path d="${path(series[1].pts)}" fill="none" stroke="var(--st-line)" stroke-width="2" stroke-dasharray="5 3"/>`
      + `<path d="${path(up)}" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linejoin="round"/>${dots}${endLab}</svg>`;
  }
  let usCache = null;
  function usTrend() { return usCache || (usCache = F.map((f, i) => { const t = total(i, ""); return t ? t.v : null; })); }
  function notes(u, c) {
    const out = [];
    if (c.sh && c.est) out.push(`The Census Bureau does not publish this income level for this county in ${flabel(S.fi)}; we estimated it from the income buckets.`);
    if (c.sh && c.lo) out.push("Few rentals in the sample here. Treat the figure with care.");
    const f = u.f[S.fi];
    if (u.m > 1) out.push("Several counties or cities are joined here because their boundaries changed after 1980.");
    else if (f.h === 2) out.push(`For ${flabel(S.fi)} this area was rebuilt from smaller Census areas to match today's boundaries.`);
    const blank = F.filter((x, i) => u.f[i].x).map((x) => x.label);
    if (blank.length) out.push(`Not shown for ${blank.join(" and ")}: ${u.f.find((x) => x.x).x}.`);
    out.push("Each period's line for the state and the country adds up every county's rentals within reach of that county's own household.");
    return out.join(" ");
  }
  function showDetail(u) {
    const el = $("detail");
    if (!u) { el.innerHTML = `<h2>County</h2><div class="empty">Hover over or tap a county to see its rent ceiling, its rentals by monthly rent, and how the share within reach has changed since 1980.</div>`; return; }
    const v = vals.get(u.id), c = v.c;
    let h = `<h2>County</h2><div class="name">${esc(u.n)}</div><div class="meta">${DATA.states[u.s][1]} &middot; ${flabel(S.fi)}</div>`;
    if (!c.sh) h += `<div class="src">${esc(noFigure(u, c, S.fi))}</div>`;
    else h += `<div class="big">${bigLine(c)}</div>` + mathTable(c, S.fi) + `<div class="src">${esc(rangeLine(c))}</div>` + ladder(u, c);
    h += spark(u) + `<div class="hist">${esc(notes(u, c))}</div>`;
    el.innerHTML = h;
  }

  // ---------- legend ----------
  function legend() {
    const el = $("legend");
    let h = `<div><h2>Share of rentals within reach, ${flabel(S.fi)}</h2><div class="unit" style="display:flex;justify-content:space-between"><span>Fewer</span><span>More</span></div>`
      + `<div class="strip">${C.seq.map((c) => `<span style="background:${c}"></span>`).join("")}</div>`
      + `<div class="ticks">${BINS.map((t, i) => `<span style="left:${((i + 1) / C.seq.length) * 100}%">${t}%</span>`).join("")}</div></div><div>`;
    if (S.bub) h += `<div class="row">Bubble size: rentals paying cash rent in the county</div>`;
    else h += `<div class="row"><span class="sw" style="background:repeating-linear-gradient(135deg,${C.panel} 0 3px,${C.mark} 3px 4px)"></span>Few rentals in the sample, treat with care</div>`;
    h += `<div class="row"><span class="sw" style="background:repeating-linear-gradient(135deg,transparent 0 3px,${C.hatch} 3px 4.5px),repeating-linear-gradient(45deg,${C.nohist} 0 3px,${C.hatch} 3px 4.5px)"></span>No comparable figure</div>`;
    el.innerHTML = h + `</div>`;
  }

  // ---------- headline ----------
  function headline() {
    const where = S.st ? DATA.states[S.st][1] : "United States";
    const t = total(S.fi, S.st);
    if (!t) {
      $("sub").textContent = S.prof === 5 ? `${where}, ${flabel(S.fi)}: the Census Bureau publishes median renter income by county only from 2005-2009 on. Pick a later period or another household.`
        : `${where}, ${flabel(S.fi)}: no counties with a figure for this view.`;
      return;
    }
    const who = S.prof === 6 ? whose() : `each county's ${PROF[S.prof]}`;
    $("sub").textContent = `${where}, ${flabel(S.fi)}: ${who}, spending ${setup()}, could afford ${pc(t.v)} of the rentals in its own county, all counties added together. In ${nf.format(t.under)} of ${nf.format(t.n)} counties the share is under half.`;
  }

  // ---------- rankings ----------
  function rankings() {
    const el = $("rank");
    const tabs = ["Fewest within reach", "Most within reach"];
    const rows = [];
    for (const u of U) {
      if (!inState(u)) continue;
      const v = vals.get(u.id);
      if (shaded(v) && !v.c.lo) rows.push([u, v]);
    }
    const sign = S.rankTab === 0 ? 1 : -1;
    rows.sort((x, y) => sign * (x[1].v - y[1].v) || x[0].n.localeCompare(y[0].n));
    let h = `<h2>Rankings</h2><div class="tabs">${tabs.map((t, i) => `<button type="button" data-t="${i}" aria-pressed="${i === S.rankTab}">${t}</button>`).join("")}</div>`;
    h += `<p class="scope">${esc(S.st ? DATA.states[S.st][1] : "All states")}, ${flabel(S.fi)}. ${nf.format(rows.length)} counties, leaving out those with few rentals in the sample.</p>`;
    if (rows.length < 3) h += `<p class="msg">Not enough counties to rank here.</p>`;
    else h += "<table>" + rows.slice(0, TOP_N).map(([u, v], i) =>
      `<tr data-id="${u.id}"${S.sel === u ? ' class="sel"' : ""}><td class="r">${i + 1}</td><td>${esc(u.n)}<br><small>${usd(v.c.ceil)} ceiling, ${nf.format(v.c.sh.tot)} rentals</small></td><td class="n">${v.c.sh.top ? "≥" : ""}${pc(v.v)}</td></tr>`).join("") + "</table>";
    el.innerHTML = h;
    el.querySelectorAll(".tabs button").forEach((b) => (b.onclick = () => { S.rankTab = +b.dataset.t; rankings(); }));
    el.querySelectorAll("tr[data-id]").forEach((tr) => (tr.onclick = () => select(byId.get(tr.dataset.id), true)));
  }

  // ---------- selection ----------
  function select(u, zoom) {
    S.sel = u;
    showDetail(u);
    if (u && zoom) {
      const pad = Math.max(u.bb[2] - u.bb[0], u.bb[3] - u.bb[1]) * 1.5;
      fitBox([u.bb[0] - pad, u.bb[1] - pad, u.bb[2] + pad, u.bb[3] + pad], 0.05, homeK * 40);
    }
    rankings();
    if (u && zoom) draw(false); else drawOverlay();
  }

  // ---------- controls ----------
  function press(on, off) { $(on).setAttribute("aria-pressed", "true"); $(off).setAttribute("aria-pressed", "false"); }
  function update(fade) {
    usCache = null;
    computeVals(); legend(); headline(); rankings(); showDetail(S.hover || S.sel);
    $("yearOut").textContent = flabel(S.fi);
    $("stamp").textContent = flabel(S.fi);
    $("pctOut").textContent = S.pct + "%";
    $("incCtl").hidden = S.prof !== 6;
    $("ht").disabled = !S.after;
    draw(!!fade);
  }
  $("prof").onchange = () => { S.prof = +$("prof").value; update(); };
  const incEl = $("inc");
  const readInc = () => { const v = +incEl.value.replace(/[^0-9.]/g, ""); if (v > 0 && v <= 5e6) { S.inc = Math.round(v); update(); } };
  incEl.oninput = readInc;
  incEl.onblur = () => { incEl.value = usd(S.inc); };
  $("pct").oninput = () => { S.pct = +$("pct").value; update(); };
  $("tAfter").onclick = () => { S.after = true; press("tAfter", "tBefore"); update(); };
  $("tBefore").onclick = () => { S.after = false; press("tBefore", "tAfter"); update(); };
  $("ht").onchange = () => { S.ht = +$("ht").value; update(); };
  $("vArea").onclick = () => { S.bub = false; press("vArea", "vBub"); update(); };
  $("vBub").onclick = () => { S.bub = true; press("vBub", "vArea"); update(); };
  const yr = $("year");
  yr.max = NF - 1; yr.value = S.fi;
  yr.oninput = () => { S.fi = +yr.value; update(true); };
  let playT = null;
  const STEP_MS = 1500;
  function stopPlay() { if (playT) { clearInterval(playT); playT = null; $("play").textContent = "Play"; } }
  $("play").onclick = () => {
    if (playT) return stopPlay();
    if (S.fi === NF - 1) S.fi = 0;
    $("play").textContent = "Pause";
    yr.value = S.fi; update(true);
    playT = setInterval(() => { if (S.fi >= NF - 1) return stopPlay(); S.fi++; yr.value = S.fi; update(true); }, STEP_MS);
  };
  const stSel = $("state");
  Object.entries(DATA.states).sort((a, b) => a[1][1].localeCompare(b[1][1])).forEach(([f, [ab, nm]]) => stSel.add(new Option(nm, f)));
  stSel.onchange = () => { S.st = stSel.value; home(); update(); };
  $("reset").onclick = () => {
    stopPlay(); S.st = ""; stSel.value = ""; S.sel = null; S.hover = null; S.fi = NF - 1; yr.value = S.fi;
    S.prof = 2; $("prof").value = 2; S.pct = 30; $("pct").value = 30; S.after = true; press("tAfter", "tBefore"); S.ht = 1; $("ht").value = 1;
    S.bub = false; press("vArea", "vBub"); S.inc = 60000; incEl.value = usd(S.inc); S.rankTab = 0; hideTip(); home(); update();
  };
  $("more").onclick = () => {
    const open = document.querySelector(".controls").classList.toggle("open");
    $("more").textContent = open ? "Fewer options" : "More options";
    $("more").setAttribute("aria-expanded", String(open));
  };

  // search
  const q = $("q"), lb = $("lb");
  const searchIdx = U.map((u) => [u, (u.n + " " + DATA.states[u.s][1]).toLowerCase()]);
  let hits = [], act = -1;
  function renderLb() {
    lb.innerHTML = hits.map((u, i) => `<li role="option" id="o${i}" data-i="${i}" aria-selected="${i === act}">${esc(u.n)}</li>`).join("");
    lb.hidden = !hits.length; q.setAttribute("aria-expanded", String(!!hits.length));
    lb.querySelectorAll("li").forEach((li) => (li.onmousedown = (e) => { e.preventDefault(); choose(hits[+li.dataset.i]); }));
  }
  function choose(u) { q.value = u.n; hits = []; renderLb(); select(u, true); }
  q.oninput = () => {
    const t = q.value.trim().toLowerCase();
    act = -1;
    hits = t.length < 2 ? [] : searchIdx.filter(([u, s]) => s.includes(t) && inState(u)).map((x) => x[0]).slice(0, 12);
    renderLb();
  };
  q.onkeydown = (e) => {
    if (e.key === "ArrowDown" && hits.length) { act = Math.min(hits.length - 1, act + 1); renderLb(); e.preventDefault(); }
    else if (e.key === "ArrowUp" && hits.length) { act = Math.max(0, act - 1); renderLb(); e.preventDefault(); }
    else if (e.key === "Enter" && hits.length) { choose(hits[Math.max(0, act)]); e.preventDefault(); }
    else if (e.key === "Escape") { hits = []; renderLb(); }
  };
  q.onblur = () => setTimeout(() => { hits = []; renderLb(); }, 100);

  const mq = window.matchMedia("(prefers-color-scheme: dark)");
  (mq.addEventListener ? mq.addEventListener("change", () => { readColors(); update(); }) : null);

  // ---------- start ----------
  readColors();
  const hs = hashFlags;
  const fIdx = F.findIndex((f) => f.k === hs.get("f"));
  if (fIdx >= 0) { S.fi = fIdx; yr.value = S.fi; }
  if (hs.get("p") && +hs.get("p") >= 0 && +hs.get("p") <= 6) { S.prof = +hs.get("p"); $("prof").value = S.prof; }
  if (hs.get("inc") && +hs.get("inc") > 0) { S.inc = Math.round(+hs.get("inc")); }
  incEl.value = usd(S.inc);
  if (hs.get("pct") && +hs.get("pct") >= 10 && +hs.get("pct") <= 50) { S.pct = +hs.get("pct"); $("pct").value = S.pct; }
  if (hs.get("tax") === "0") { S.after = false; press("tBefore", "tAfter"); }
  if (hs.get("ht") && +hs.get("ht") >= 0 && +hs.get("ht") <= 2) { S.ht = +hs.get("ht"); $("ht").value = S.ht; }
  if (hs.get("st") && DATA.states[hs.get("st")]) { S.st = hs.get("st"); stSel.value = S.st; }
  if (hs.get("view") === "bubble") { S.bub = true; press("vBub", "vArea"); }
  computeVals();
  $("loading").remove();
  new ResizeObserver(resize).observe(wrap);
  update();
  if (hs.get("debug") === "1") window.__ahdbg = { S, vals: () => vals, calc, total, byId, taxOn, shareOf, update, view, F };
  if (hs.get("u") && byId.get(hs.get("u"))) { pendingSel = byId.get(hs.get("u")); if (W) { select(pendingSel, true); pendingSel = null; } }
})().catch((e) => {
  const s = document.getElementById("sub");
  if (s) s.textContent = "The map could not load: " + e.message;
  throw e;
});
