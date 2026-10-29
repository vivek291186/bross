import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
D = os.path.expanduser("~/mnt/Downloads/.bbf/3d/")
OUTD = D + "comp/"; os.makedirs(OUTD, exist_ok=True)
song = json.load(open(D + "song.json"))
FPS = 24; LEAD = song["lead"]; SLOT = song["slot"]
NAVY = (34, 22, 79); YEL = (255, 210, 63); PINK = (239, 61, 124); CYAN = (40, 186, 236); WHITE = (255, 255, 255)
def font(n, s, var="Bold"):
    f = ImageFont.truetype(D + n, s)
    try: f.set_variation_by_name(var)
    except Exception: pass
    return f
F_LOGO1, F_LOGO2 = font("Fredoka.ttf", 34), font("Fredoka.ttf", 44)
F_LYR, F_NEXT, F_TAG, F_BIG = font("Fredoka.ttf", 46), font("Nunito.ttf", 26, "ExtraBold"), font("Fredoka.ttf", 20), font("Fredoka.ttf", 84)

def outline(d, xy, t, f, fill, ow=5, anchor="mm"):
    d.text((xy[0] + 3, xy[1] + 3), t, font=f, fill=NAVY, anchor=anchor, stroke_width=ow, stroke_fill=NAVY)
    d.text(xy, t, font=f, fill=fill, anchor=anchor, stroke_width=ow, stroke_fill=NAVY)

frames = sorted(x for x in os.listdir(D + "frames") if x.endswith(".png"))
for i, fn in enumerate(frames):
    ts = i / FPS
    im = Image.open(D + "frames/" + fn).convert("RGBA")
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    outline(d, (110, 30), "BRO BROS", F_LOGO1, YEL, 4)
    outline(d, (114, 70), "FUN!", F_LOGO2, PINK, 4)
    if ts < LEAD:
        k = min(1, ts / 0.5)
        outline(d, (640, int(-80 + 300 * k)), "SING ALONG!", F_BIG, YEL, 8)
        if ts > 0.8: outline(d, (640, 320), "Diya Diya Shining Bright", font("Fredoka.ttf", 44), WHITE, 6)
    else:
        k = int((ts - LEAD) / SLOT)
        if k < len(song["lines"]):
            cur = song["lines"][k]; nxt = song["lines"][k + 1] if k + 1 < len(song["lines"]) else ""
            d.rounded_rectangle([200, 560, 1080, 700], radius=30, fill=(255, 250, 235, 235), outline=NAVY, width=5)
            frac = ((ts - LEAD) % SLOT) / SLOT
            words = cur.split(); lit = int(len(words) * min(1, frac / 0.6)) + 1
            tw = d.textlength(cur, font=F_LYR); x = 640 - tw / 2
            for j, w in enumerate(words):
                d.text((x, 612), w, font=F_LYR, fill=PINK if j < lit else NAVY, anchor="lm")
                x += d.textlength(w + " ", font=F_LYR)
            if nxt: d.text((640, 668), nxt, font=F_NEXT, fill=(150, 140, 180), anchor="mm")
            who = song["who"][k]
            tag = {"big": "BIG BRO", "lil": "LIL BRO", "both": "EVERYBODY!"}[who]
            col = {"big": CYAN, "lil": PINK, "both": YEL}[who]
            tw2 = d.textlength(tag, font=F_TAG) + 30
            d.rounded_rectangle([220, 540, 220 + tw2, 574], radius=17, fill=col, outline=NAVY, width=4)
            d.text((220 + tw2 / 2, 557), tag, font=F_TAG, fill=NAVY, anchor="mm")
        else:
            outline(d, (640, 620), "HAPPY DIWALI!", F_BIG, YEL, 8)
    im.alpha_composite(ov)
    im.convert("RGB").save(OUTD + fn, compress_level=1)
out = os.path.expanduser("~/mnt/Downloads/Bro Bros Fun - 3D Test - Diwali Song.mp4")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "24", "-i", OUTD + "f_%04d.png", "-i", D + "song.wav",
                "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-ac", "2",
                "-shortest", "-movflags", "+faststart", out], check=True)
print("DONE", out, os.path.getsize(out))
