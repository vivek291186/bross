#!/usr/bin/env python3
"""Build the Bro Bros 'learning tree' page from knowledge.json -> tree.html (self-contained)."""
import json, math, html, sys, os

here = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(here, "knowledge.json")))
branches = d["branches"]
total = sum(len(b["leaves"]) for b in branches)
TARGET = 200  # leaves for "fully ready"
ready = min(100, round(100 * total / TARGET))
colors = ["#4CAF50", "#2196F3", "#FF9800", "#9C27B0", "#E91E63", "#00BCD4", "#795548", "#F44336", "#8BC34A", "#3F51B5"]

# ---- SVG tree: trunk in the middle, branches fan out, leaves are circles along each branch ----
W, H = 900, 560
cx, base = W / 2, H - 30
trunk_top = H - 230
svg = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Learning tree">']
svg.append(f'<ellipse cx="{cx}" cy="{base+8}" rx="210" ry="16" fill="#d7ecc9"/>')
svg.append(f'<path d="M{cx-26},{base} C{cx-18},{base-90} {cx-14},{trunk_top+60} {cx-8},{trunk_top} L{cx+8},{trunk_top} C{cx+14},{trunk_top+60} {cx+18},{base-90} {cx+26},{base} Z" fill="#8d6e4f"/>')
n = len(branches)
for i, b in enumerate(branches):
    ang = math.radians(200 + (140 * i / max(1, n - 1)))  # fan from left to right
    L = 230
    ex, ey = cx + L * math.cos(ang), trunk_top + L * math.sin(ang) * 0.95
    sx, sy = cx, trunk_top + 30 - 12 * (i % 3)
    c = colors[i % len(colors)]
    k = len(b["leaves"])
    sw = 4 + min(10, k * 0.6)
    svg.append(f'<path d="M{sx},{sy} Q{(sx+ex)/2},{sy-30} {ex:.0f},{ey:.0f}" stroke="#8d6e4f" stroke-width="{sw:.1f}" fill="none" stroke-linecap="round"/>')
    for j in range(k):
        t = 0.35 + 0.65 * (j + 1) / (k + 1)
        px = (1 - t) ** 2 * sx + 2 * (1 - t) * t * (sx + ex) / 2 + t ** 2 * ex
        py = (1 - t) ** 2 * sy + 2 * (1 - t) * t * (sy - 30) + t ** 2 * ey
        off = 16 if j % 2 else -16
        lx, ly = px + off * math.sin(ang), py - off * math.cos(ang)
        svg.append(f'<circle cx="{lx:.0f}" cy="{ly:.0f}" r="9" fill="{c}" opacity="0.88"><title>{html.escape(b["leaves"][j]["t"])}</title></circle>')
    if k == 0:
        svg.append(f'<circle cx="{ex:.0f}" cy="{ey:.0f}" r="7" fill="none" stroke="{c}" stroke-dasharray="3 3"/>')
    lx = ex + (14 if math.cos(ang) > 0 else -14)
    anchor = "start" if math.cos(ang) > 0 else "end"
    svg.append(f'<text x="{lx:.0f}" y="{ey-6:.0f}" text-anchor="{anchor}" font-size="15" font-weight="700" fill="{c}">{html.escape(b["name"])}</text>')
    svg.append(f'<text x="{lx:.0f}" y="{ey+12:.0f}" text-anchor="{anchor}" font-size="12" fill="#555">{k} learnings</text>')
svg.append("</svg>")

# ---- recent learnings ----
allleaves = [(l["date"], b["name"], l) for b in branches for l in b["leaves"]]
allleaves.sort(key=lambda x: x[0], reverse=True)
recent = "".join(f'<li><span class="tag">{html.escape(bn)}</span> {html.escape(l["t"])} <span class="src">({html.escape(l["src"])})</span></li>' for _, bn, l in allleaves[:12])
cards = "".join(
    f'<details class="card" style="border-color:{colors[i%len(colors)]}"><summary><b style="color:{colors[i%len(colors)]}">{html.escape(b["name"])}</b> &middot; {len(b["leaves"])}</summary><ul>'
    + "".join(f'<li>{html.escape(l["t"])} <span class="src">({html.escape(l["src"])}, {l["conf"]})</span></li>' for l in b["leaves"])
    + ("" if b["leaves"] else "<li class='src'>Waiting for data</li>") + "</ul></details>"
    for i, b in enumerate(branches))
play = "".join(f"<li>{html.escape(p)}</li>" for p in d.get("playbook", []))
log = "".join(f'<li><b>{html.escape(e["date"])}</b> {html.escape(e["note"])}</li>' for e in reversed(d.get("log", [])[-10:]))

page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Bro Bros learning tree</title>
<style>
body{{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#f6faf3;color:#222}}
.wrap{{max-width:980px;margin:0 auto;padding:20px}}
h1{{margin:0 0 4px;font-size:26px}} .sub{{color:#666;margin:0 0 14px}}
.stats{{display:flex;gap:12px;flex-wrap:wrap;margin:10px 0 6px}}
.stat{{background:#fff;border-radius:12px;padding:10px 16px;box-shadow:0 1px 3px #0001}} .stat b{{font-size:22px;display:block}}
.bar{{height:14px;background:#e3eedc;border-radius:8px;overflow:hidden;margin:6px 0 14px}} .bar i{{display:block;height:100%;width:{ready}%;background:linear-gradient(90deg,#8bc34a,#4caf50)}}
.tree{{background:#fff;border-radius:16px;box-shadow:0 1px 4px #0001;padding:6px}}
h2{{font-size:18px;margin:22px 0 8px}}
ul{{padding-left:18px}} li{{margin:5px 0;line-height:1.4}}
.tag{{background:#eef6e8;border-radius:6px;padding:1px 6px;font-size:12px;color:#33691e}}
.src{{color:#888;font-size:12px}}
.card{{background:#fff;border-left:5px solid;border-radius:10px;padding:8px 12px;margin:8px 0;box-shadow:0 1px 3px #0001}}
summary{{cursor:pointer}}
</style></head><body><div class="wrap">
<h1>Bro Bros learning tree</h1>
<p class="sub">What the research agent has learned about kids' videos and music. Updated {html.escape(d["updated"])} &middot; research runs so far: {d["runs"]}</p>
<div class="stats"><div class="stat"><b>{total}</b>learnings</div><div class="stat"><b>{n}</b>branches</div><div class="stat"><b>{len(d.get("playbook",[]))}</b>playbook rules</div><div class="stat"><b>{ready}%</b>ready for next week</div></div>
<div class="bar"><i></i></div>
<div class="tree">{''.join(svg)}</div>
<h2>Playbook for next week's songs</h2><ol>{play}</ol>
<h2>Newest learnings</h2><ul>{recent}</ul>
<h2>All branches</h2>{cards}
<h2>Research log</h2><ul>{log or "<li class='src'>First run</li>"}</ul>
</div></body></html>"""
open(os.path.join(here, "tree.html"), "w").write(page)
print("tree.html", total, "leaves", ready, "% ready")
