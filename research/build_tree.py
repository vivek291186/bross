#!/usr/bin/env python3
"""Build the Bro Bros 'learning tree' page from knowledge.json -> tree.html (self-contained)."""
import json, math, html, sys, os

here = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(here, "knowledge.json")))
branches = d["branches"]
total = sum(len(b["leaves"]) for b in branches)
TARGET = 500  # leaves for "fully ready"
ready = min(100, round(100 * total / TARGET))
colors = ["#4CAF50", "#2196F3", "#FF9800", "#9C27B0", "#E91E63", "#00BCD4", "#795548", "#F44336", "#8BC34A", "#3F51B5"]

# ---- SVG tree: trunk in the middle, branches fan out, leaves are circles along each branch ----
W, H = 900, 560
cx, base = W / 2, H - 30
trunk_top = H - 150 - int(110 * min(1, (total / TARGET) ** 0.5))
svg = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Learning tree">']
svg.append(f'<ellipse cx="{cx}" cy="{base+8}" rx="210" ry="16" fill="#d7ecc9"/>')
svg.append(f'<path d="M{cx-26},{base} C{cx-18},{base-90} {cx-14},{trunk_top+60} {cx-8},{trunk_top} L{cx+8},{trunk_top} C{cx+14},{trunk_top+60} {cx+18},{base-90} {cx+26},{base} Z" fill="#8d6e4f"/>')
n = len(branches)
newest_date = max((l["date"] for b in branches for l in b["leaves"]), default="")
for i, b in enumerate(branches):
    ang = math.radians(200 + (140 * i / max(1, n - 1)))  # fan from left to right
    L = 215 + (55 if i % 2 else 0)
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
        glow = ' stroke="#ffd54f" stroke-width="3"' if b["leaves"][j].get("run", 0) == d["runs"] else ''
        svg.append(f'<circle cx="{lx:.0f}" cy="{ly:.0f}" r="9" fill="{c}" opacity="0.88"{glow}><title>{html.escape(b["leaves"][j]["t"])}</title></circle>')
    if k == 0:
        svg.append(f'<circle cx="{ex:.0f}" cy="{ey:.0f}" r="7" fill="none" stroke="{c}" stroke-dasharray="3 3"/>')
    svg.append(f'<text x="{ex:.0f}" y="{ey-14:.0f}" text-anchor="middle" font-size="13" font-weight="700" fill="{c}">{k}</text>')
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
hist = d.get("history", [])
gw, gh = 900, 160
pts = ""
if len(hist) >= 1:
    mx = max(TARGET * 0.2, max(h["total"] for h in hist))
    for k, h in enumerate(hist):
        x = 40 + (gw - 60) * (k / max(1, len(hist) - 1))
        y = gh - 25 - (gh - 45) * h["total"] / mx
        pts += f"{x:.0f},{y:.0f} "
growth = (f'<svg viewBox="0 0 {gw} {gh}" xmlns="http://www.w3.org/2000/svg"><line x1="40" y1="{gh-25}" x2="{gw-20}" y2="{gh-25}" stroke="#ccc"/>'
          f'<polyline points="{pts}" fill="none" stroke="#4caf50" stroke-width="4" stroke-linejoin="round"/>'
          + "".join(f'<circle cx="{p.split(",")[0]}" cy="{p.split(",")[1]}" r="4" fill="#2e7d32"/>' for p in pts.split())
          + f'<text x="40" y="16" font-size="13" fill="#555">Learnings over time (latest {total})</text>'
          + (f'<text x="40" y="{gh-6}" font-size="11" fill="#888">{html.escape(hist[0]["date"])}</text><text x="{gw-20}" y="{gh-6}" font-size="11" fill="#888" text-anchor="end">{html.escape(hist[-1]["date"])}</text>' if hist else "")
          + '</svg>')
stages = [(0, "Seed"), (10, "Sprout"), (25, "Sapling"), (50, "Young tree"), (75, "Strong tree"), (95, "Fully grown")]
stage = [nm for th, nm in stages if ready >= th][-1]
newest = max((l["date"] for b in branches for l in b["leaves"]), default="")
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
.legend{{display:flex;flex-wrap:wrap;gap:8px 16px;margin:10px 4px}} .legend span{{font-size:14px}} .legend i{{display:inline-block;width:12px;height:12px;border-radius:50%;margin-right:5px;vertical-align:-1px}}
</style></head><body><div class="wrap">
<h1>Bro Bros learning tree</h1>
<p class="sub">What the research agent has learned about kids' videos and music. Updated {html.escape(d["updated"])} &middot; research runs so far: {d["runs"]}</p>
<div class="stats"><div class="stat"><b>{total}</b>learnings</div><div class="stat"><b>{n}</b>branches</div><div class="stat"><b>{len(d.get("playbook",[]))}</b>playbook rules</div><div class="stat"><b>{ready}%</b>ready for next week</div><div class="stat"><b>{stage}</b>tree stage</div></div>
<div class="bar"><i></i></div>
<div class="tree">{''.join(svg)}</div>
<div class="legend">{"".join(f'<span><i style="background:{colors[i%len(colors)]}"></i>{html.escape(b["name"])} <b>{len(b["leaves"])}</b></span>' for i, b in enumerate(branches))}</div>
<p class="src">Gold-ringed leaves are the newest learnings. The trunk grows taller as learnings add up.</p>
<h2>Growth</h2><div class="tree">{growth}</div>
<h2>Playbook for next week's songs</h2><ol>{play}</ol>
{("<h2>Song ideas for next week</h2><ol>" + "".join(f"<li><b>{html.escape(x['title'])}</b>: {html.escape(x['why'])}</li>" for x in d.get("next_week_ideas", [])) + "</ol>") if d.get("next_week_ideas") else ""}
{("<h2>Trend bank: trends to use in our videos</h2><ul>" + "".join(f"<li><b>{html.escape(x['name'])}</b> <span class='tag'>{html.escape(x.get('status',''))}</span> <span class='src'>{html.escape(x.get('where',''))}</span><br>{html.escape(x['use'])}</li>" for x in d.get("trend_bank", [])) + "</ul>") if d.get("trend_bank") else ""}
<h2>Newest learnings</h2><ul>{recent}</ul>
<h2>All branches</h2>{cards}
<h2>Research log</h2><ul>{log or "<li class='src'>First run</li>"}</ul>
</div></body></html>"""
open(os.path.join(here, "tree.html"), "w").write(page)
print("tree.html", total, "leaves", ready, "% ready")
