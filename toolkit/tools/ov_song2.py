"""Song overlays (rebuilt ov_song, SD): logo+SING-ALONG, lyric bar per line, big cue words (8-frame pop), end card -> <DIR>ov/ + ov.json
usage: ov_song2.py SONGDIR"""
import sys, os, json
from PIL import Image, ImageDraw, ImageFont
D = sys.argv[1].rstrip("/"); OUT = D + "ov/"; os.makedirs(OUT, exist_ok=True)
W, H = 854, 480; FONT = "/home/claude/bbf/assets/Fredoka.ttf"
def font(px):
    f = ImageFont.truetype(FONT, int(px))
    try: f.set_variation_by_name("Bold")
    except Exception: pass
    return f
INK = (34, 20, 70); CREAM = (243, 242, 230); YEL = (255, 210, 60); CYAN = (60, 190, 240); PINK = (239, 61, 124)
TL = json.load(open(D + "/timeline.json")); F = lambda t: int(round(t * 24)) + 1; total = F(TL["total"])
Image.open("/home/claude/tools/song_logo_sd.png").save(OUT + "logo.png")
subs = []
for i, ln in enumerate(TL["lines"]):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = font(22); tw = d.textlength(ln["text"], font=f)
    if tw > 600: f = font(22 * 600 / tw); tw = d.textlength(ln["text"], font=f)
    x0 = int(W / 2 - tw / 2 - 20); x1 = int(W / 2 + tw / 2 + 20); y0, y1 = 414, 462
    d.rounded_rectangle((x0, y0, x1, y1), radius=20, fill=CREAM, outline=INK, width=2)
    d.text((W / 2, (y0 + y1) / 2), ln["text"], font=f, fill=INK, anchor="mm")
    ev = [e for e in TL["events"] if e["type"] == "say" and abs(e["t"] - ln["t0"]) < 0.01]
    whos = ev[0]["whos"] if ev else []
    tag = "EVERYBODY!" if len(whos) >= 4 or not whos else " + ".join(w.upper() for w in whos)
    ft = font(11); tg = d.textlength(tag, font=ft) + 18
    d.rounded_rectangle((x0 + 12, y0 - 12, x0 + 12 + tg, y0 + 8), radius=10, fill=YEL, outline=INK, width=2)
    d.text((x0 + 12 + tg / 2, y0 - 2), tag, font=ft, fill=INK, anchor="mm")
    nm = f"sub_{i:03d}.png"; im.save(OUT + nm); subs.append([nm, F(ln["t0"]), F(ln["t1"])])
cues = []
for i, (txt, t0, t1, col) in enumerate(TL.get("cues", [])):
    for j in range(8):
        s_ = 0.6 + 0.4 * min(1, (j + 1) / 6) + (0.08 if j == 5 else 0)
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.text((W / 2, 104), txt, font=font(46 * s_), fill=tuple(col), stroke_width=4, stroke_fill=INK, anchor="mm")
        im.save(OUT + f"cue{i}_{j:02d}.png")
    cues.append([f"cue{i}_", F(t0), 8, F(t1)])
end_start = total - 24 * 4
for i in range(1, 19):
    u = i / 18; im = Image.new("RGBA", (W, H), (20, 40, 30, int(150 * u))); d = ImageDraw.Draw(im)
    d.text((W / 2, 275), TL.get("title", "THANK YOU!").split("!")[0] + "!", font=font(44 * (0.8 + 0.2 * u)), fill=YEL + (int(255 * u),), stroke_width=4, stroke_fill=INK, anchor="mm")
    d.text((W / 2, 340), "New song every day!", font=font(22), fill=(255, 255, 255, int(255 * u)), stroke_width=3, stroke_fill=INK, anchor="mm")
    d.text((W / 2, 362 + 0), "", font=font(16))
    d.text((W / 2, 366), "Ask a grown up to subscribe to Bro Bros Fun!", font=font(16), fill=CYAN + (int(255 * u),), stroke_width=2, stroke_fill=INK, anchor="mm")
    d.text((W / 2, 388), TL.get("next", "New song tomorrow at 10 AM!"), font=font(16), fill=PINK + (int(255 * u),), stroke_width=2, stroke_fill=INK, anchor="mm")
    im.save(OUT + f"end_{i:04d}.png")
json.dump({"total": total, "subs": subs, "cues": cues, "end_start": end_start, "end_n": 18}, open(OUT + "ov.json", "w"))
print("song overlays", len(subs), "lines", len(cues), "cues ->", OUT)
