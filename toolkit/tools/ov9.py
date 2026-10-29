"""Episode overlays (rebuilt ov8, SD 854x480): logo, intro title card, speaker subtitles, end card -> <EP>ov_sd/ + ov.json (for compose_ep.py)
usage: ov9.py EPDIR TITLE1 TITLE2 "Episode N" ENDBIG NEXTLINE"""
import sys, os, json, textwrap
from PIL import Image, ImageDraw, ImageFont
EP, T1, T2, EPL, ENDBIG, NEXT = sys.argv[1:7]
OUT = EP.rstrip("/") + "ov_sd/"; os.makedirs(OUT, exist_ok=True)
W, H = 854, 480; S = W / 1920
FONT = "/home/claude/bbf/assets/Fredoka.ttf"
def font(px):
    f = ImageFont.truetype(FONT, max(8, int(px * S)))
    try: f.set_variation_by_name("Bold")
    except Exception: pass
    return f
INK = (34, 20, 70); CREAM = (243, 242, 230); YEL = (255, 210, 60); CYAN = (60, 190, 240); PINK = (239, 61, 124)
TAGC = {"vanu": (255, 120, 170), "aarav": (100, 200, 255), "vihaan": (120, 220, 120), "himank": (180, 140, 255), "buddy": (255, 170, 80),
        "zoomy": (80, 220, 230), "mummy": (255, 150, 150), "papa": (150, 190, 255), "grandma": (255, 190, 120), "grandpa": (200, 170, 120), "coach": (200, 200, 200)}
TL = json.load(open(os.path.join(EP, "timeline.json"))); F = lambda t: int(round(t * 24)) + 1
total = F(TL["total"])
Image.open("/home/claude/tools/logo1080.png").convert("RGBA").resize((W, H), Image.LANCZOS).save(OUT + "logo.png")
def stroked(d, xy, s, f, fill, sw, anchor="mm"):
    d.text(xy, s, font=f, fill=fill, stroke_width=sw, stroke_fill=INK, anchor=anchor)
# subtitles
subs = []
for i, e in enumerate([e for e in TL["events"] if e["type"] == "say"]):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    lines = textwrap.wrap(e["text"], 58)[:2]
    bh = int((88 if len(lines) == 1 else 128) * S); x0, x1 = int(255 * S), int(1665 * S); y1 = int(1050 * S); y0 = y1 - bh
    d.rounded_rectangle((x0, y0, x1, y1), radius=int(46 * S), fill=CREAM, outline=INK, width=max(2, int(7 * S)))
    f = font(54 if len(lines) == 1 else 48)
    for j, ln in enumerate(lines):
        stroked(d, ((x0 + x1) // 2, y0 + bh // 2 + int((j - (len(lines) - 1) / 2) * 56 * S)), ln, f, INK, 0)
    whos = e.get("whos") or [e["who"]]
    tag = "EVERYBODY!" if len(whos) >= 4 else " + ".join(w.upper() for w in whos)
    col = YEL if len(whos) >= 4 or len(whos) > 1 else TAGC.get(whos[0], YEL)
    ft = font(34); tw = d.textlength(tag, font=ft) + int(44 * S)
    tx0, ty1 = int(295 * S), y0 + int(22 * S); ty0 = ty1 - int(50 * S)
    d.rounded_rectangle((tx0, ty0, tx0 + tw, ty1), radius=int(25 * S), fill=col, outline=INK, width=max(2, int(6 * S)))
    stroked(d, (tx0 + tw / 2, (ty0 + ty1) / 2), tag, ft, INK, 0)
    nm = f"sub_{i:03d}.png"; im.save(OUT + nm)
    subs.append([nm, F(e["t"]), F(e["t"] + e["dur"])])
# intro card (87 frames, starts at the intro card event)
for i in range(1, 88):
    a = min(1, i / 8, (88 - i) / 8)
    im = Image.new("RGBA", (W, H), (20, 40, 30, int(120 * a))); d = ImageDraw.Draw(im)
    pop = min(1.0, i / 10) if i < 10 else 1.0
    if a > 0.05:
        s1 = font(110 * (0.7 + 0.3 * pop)); s2 = font(190 * (0.7 + 0.3 * pop)); s3 = font(80)
        stroked(d, (W // 2, int(385 * S)), T1, s1, (255, 255, 255, int(255 * a)), max(2, int(12 * S)))
        stroked(d, (W // 2, int(515 * S)), T2, s2, YEL + (int(255 * a),), max(3, int(14 * S)))
        stroked(d, (W // 2, int(642 * S)), EPL, s3, CYAN + (int(255 * a),), max(2, int(9 * S)))
    im.save(OUT + f"intro_{i:04d}.png")
# end card (18-frame build then hold)
for i in range(1, 19):
    u = i / 18
    im = Image.new("RGBA", (W, H), (20, 40, 60, int(150 * u))); d = ImageDraw.Draw(im)
    stroked(d, (W // 2, int((620 - 40 * (1 - u)) * S)), ENDBIG, font(150 * (0.8 + 0.2 * u)), YEL + (int(255 * u),), max(3, int(14 * S)))
    stroked(d, (W // 2, int(735 * S)), "Ask a grown up to subscribe to Bro Bros Fun!", font(60), (255, 255, 255, int(255 * u)), max(2, int(8 * S)))
    stroked(d, (W // 2, int(820 * S)), NEXT, font(54), CYAN + (int(255 * u),), max(2, int(7 * S)))
    im.save(OUT + f"end_{i:04d}.png")
cards = [e for e in TL["events"] if e["type"] == "card"]
end_start = F([c for c in cards if c["name"] == "endcard"][0]["t"]) if any(c["name"] == "endcard" for c in cards) else total - 24 * 6
json.dump({"total": total, "subs": subs, "wipes": [], "intro": 87, "cards": [], "end_start": end_start, "end_n": 18}, open(OUT + "ov.json", "w"))
print("overlays subs", len(subs), "->", OUT)
