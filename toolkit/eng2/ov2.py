# Ep2 overlay PNGs (1920x1080): logo, intro title, wipes, subtitles, end card  -> ep02ov/ + ov.json
import json, os, math, sys
from PIL import Image, ImageDraw, ImageFont
EP = sys.argv[1] if len(sys.argv) > 1 else "/mnt/user-data/outputs/ep02"
TITLE1, TITLE2 = (sys.argv[2], sys.argv[3]) if len(sys.argv) > 3 else ("THE", "LUNCHBOX SWAP MYSTERY!")
OUT = EP + "ov/"; os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT): os.remove(OUT + f)
TL = json.load(open(EP + "/timeline.json")); FPS = 24; W, H = 1920, 1080
F = lambda t: int(round(t * FPS)) + 1
NAVY = (34, 22, 79); YEL = (255, 210, 63); PINK = (239, 61, 124); CYAN = (40, 186, 236); WHITE = (255, 255, 255)
GREEN = (90, 200, 110); PURPLE = (170, 110, 240); ORANGE = (255, 150, 40)
FONT = "/home/claude/bbf/assets/Fredoka.ttf"
def font(s):
    f = ImageFont.truetype(FONT, s)
    try: f.set_variation_by_name("Bold")
    except Exception: pass
    return f
FL1, FL2, FSUB, FTAG, FBIG, FMID, FSM = font(48), font(63), font(54), font(30), font(130), font(74), font(52)
TAG = {"vanu": ("VANU", PINK), "aarav": ("AARAV", CYAN), "vihaan": ("VIHAAN", YEL), "himank": ("HIMANK", PURPLE), "buddy": ("BUDDY", GREEN)}
def tag_of(w):
    ks = w.split("+")
    if len(ks) >= 4: return ("EVERYBODY!", YEL)
    if len(ks) == 1 and w in TAG: return TAG[w]
    return (" & ".join(k.upper() for k in ks), ORANGE)
def outline(d, xy, t, f, fill, ow=7):
    d.text((xy[0] + 4, xy[1] + 6), t, font=f, fill=NAVY, anchor="mm", stroke_width=ow, stroke_fill=NAVY)
    d.text(xy, t, font=f, fill=fill, anchor="mm", stroke_width=ow, stroke_fill=NAVY)
def wrap(d, text, f, maxw):
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: out.append(cur); cur = w
    out.append(cur); return out
def blank(): im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); return im, ImageDraw.Draw(im)
M = {"total": F(TL["total"]), "subs": [], "wipes": []}

# logo (persistent, top-left)
im, d = blank(); outline(d, (160, 48), "BRO BROS", FL1, YEL, 5); outline(d, (165, 104), "FUN!", FL2, PINK, 6); im.save(OUT + "logo.png")

# intro title over first card
intro = [e for e in TL["events"] if e["type"] == "card" and e["name"] == "intro"][0]
n_intro = F(intro["t"] + intro["dur"] + 0.8) - 1
for i in range(n_intro):
    ts = i / FPS; im, d = blank()
    k = min(1, ts / 0.6); k = 1 - (1 - k) ** 3
    fade = max(0, 1 - max(0, ts - (intro["dur"] - 0.2)) / 0.8)
    a = int(255 * fade)
    if a > 0:
        lay, dl = blank()
        dl.rectangle([0, 0, W, H], fill=(10, 5, 40, 120))
        outline(dl, (W // 2, int(-90 + 470 * k)), TITLE1, FMID, WHITE, 8)
        outline(dl, (W // 2, int(-90 + 600 * k)), TITLE2, FBIG, YEL, 12)
        outline(dl, (W // 2, int(-90 + 730 * k)), "Episode 2", FSM, CYAN, 6)
        r, g, b, al = lay.split(); al = al.point(lambda v: v * a // 255); lay = Image.merge("RGBA", (r, g, b, al))
        im = Image.alpha_composite(im, lay)
    im.save(OUT + "intro_%04d.png" % (i + 1))
M["intro"] = n_intro

# wipes: star iris that closes before the cut and opens after it
cols = [YEL, PINK, CYAN, GREEN, PURPLE]
def star(d, cx, cy, r, c, rot=0):
    pts = []
    for j in range(10):
        a = rot + j * math.pi / 5 - math.pi / 2; rr = r if j % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=c, outline=NAVY, width=8)
wi = 0
for e in TL["events"]:
    if e["type"] == "card" and e["name"] == "wipe":
        cut = F(e["t"] + e["dur"]); n = 30
        for j in range(n):
            u = j / (n - 1)                      # 0..1, cut at 0.5
            cover = 1 - abs(u - 0.5) * 2         # 0 ->1 ->0
            im, d = blank()
            for q, c in enumerate(cols):
                rr = (2400 - q * 330) * cover ** 0.9
                if rr > 5: star(d, W // 2, H // 2, rr, c + (255,), rot=u * 2.5 + q * 0.3)
            if cover > 0.85: outline(d, (W // 2, H // 2), "BRO BROS FUN!", FBIG, WHITE, 10)
            im.save(OUT + f"wipe{wi}_{j:04d}.png")
        M["wipes"].append([f"wipe{wi}_", cut - n // 2, n]); wi += 1

# subtitles
says = [e for e in TL["events"] if e["type"] == "say"]
for i, e in enumerate(says):
    im, d = blank()
    lines = wrap(d, e["text"], FSUB, 1340)
    h = 40 + 70 * len(lines); y0 = 1050 - h
    d.rounded_rectangle([255, y0, 1665, 1050], radius=40, fill=(255, 252, 240, 238), outline=NAVY, width=6)
    for j, l in enumerate(lines): d.text((960, y0 + 55 + j * 70), l, font=FSUB, fill=NAVY, anchor="mm")
    tag, col = tag_of(e["who"]); tw = d.textlength(tag, font=FTAG) + 46
    d.rounded_rectangle([294, y0 - 27, 294 + tw, y0 + 25], radius=26, fill=col, outline=NAVY, width=5)
    d.text((294 + tw / 2, y0 - 1), tag, font=FTAG, fill=NAVY, anchor="mm")
    fn = "sub_%03d.png" % i; im.save(OUT + fn)
    M["subs"].append([fn, F(e["t"]), F(e["t"] + e["dur"] + 0.25)])

# end card
endc = [e for e in TL["events"] if e["type"] == "card" and e["name"] == "endcard"][0]
n_end = 18
for i in range(n_end):
    k = (i + 1) / n_end; k = 1 - (1 - k) ** 3
    im, d = blank()
    d.rectangle([0, 0, W, H], fill=(10, 5, 40, int(110 * k)))
    outline(d, (W // 2, int(-120 + 450 * k)), "SEE YOU TOMORROW!", FBIG, YEL, 12)
    outline(d, (W // 2, int(-120 + 600 * k)), "Ask a grown up to subscribe to Bro Bros Fun!", FSM, WHITE, 6)
    outline(d, (W // 2, int(-120 + 700 * k)), "Next: more fun with the gang!", font(44), CYAN, 5)
    im.save(OUT + "end_%04d.png" % (i + 1))
M["end_start"] = F(endc["t"]); M["end_n"] = n_end
json.dump(M, open(OUT + "ov.json", "w"))
print("overlays", len(os.listdir(OUT)), "subs", len(M["subs"]), "wipes", len(M["wipes"]))
