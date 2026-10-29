import json, os, sys, subprocess
from PIL import Image, ImageDraw, ImageFont
D = os.path.expanduser("~/mnt/Downloads/.bbf/3d2/")
FONTD = os.path.expanduser("~/mnt/Downloads/.bbf/3d/")
OUTD = D + "comp/"; os.makedirs(OUTD, exist_ok=True)
TL = json.load(open(D + "timeline.json")); FPS = 24
NAVY = (34, 22, 79); YEL = (255, 210, 63); PINK = (239, 61, 124); CYAN = (40, 186, 236); WHITE = (255, 255, 255); ORANGE = (255, 150, 40)
def font(n, s, var="Bold"):
    f = ImageFont.truetype(FONTD + n, s)
    try: f.set_variation_by_name(var)
    except Exception: pass
    return f
FL1, FL2 = font("Fredoka.ttf", 32), font("Fredoka.ttf", 42)
FSUB, FTAG, FBIG, FMID, FSM = font("Fredoka.ttf", 38), font("Fredoka.ttf", 20), font("Fredoka.ttf", 96), font("Fredoka.ttf", 48), font("Nunito.ttf", 24, "ExtraBold")
TAG = {"big": ("BIG BRO", CYAN), "lil": ("LIL BRO", PINK), "papa": ("PAPA", ORANGE), "both": ("BRO BROS", YEL)}
says = [e for e in TL["events"] if e["type"] == "say"]
intro = [e for e in TL["events"] if e["type"] == "act" and e["name"] == "intro_card"][0]
endc = [e for e in TL["events"] if e["type"] == "act" and e["name"] == "end_card"][0]

def outline(d, xy, t, f, fill, ow=5):
    d.text((xy[0] + 3, xy[1] + 4), t, font=f, fill=NAVY, anchor="mm", stroke_width=ow, stroke_fill=NAVY)
    d.text(xy, t, font=f, fill=fill, anchor="mm", stroke_width=ow, stroke_fill=NAVY)

def wrap(d, text, f, maxw):
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: out.append(cur); cur = w
    out.append(cur); return out

a, b = int(sys.argv[1]), int(sys.argv[2])
frames = sorted(x for x in os.listdir(D + "frames") if x.endswith(".png"))
for i, fn in enumerate(frames[a:b], start=a):
    if os.path.exists(OUTD + fn): continue
    ts = i / FPS
    im = Image.open(D + "frames/" + fn).convert("RGBA")
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    outline(d, (104, 30), "BRO BROS", FL1, YEL, 4); outline(d, (108, 68), "FUN!", FL2, PINK, 4)
    if ts < intro["t"] + intro["dur"] + 2.0:
        k = min(1, ts / 0.6)
        d.rectangle([0, 0, 1280, 720], fill=(10, 5, 40, int(110 * max(0, 1 - max(0, ts - 3.0) / 0.6))))
        if ts < 3.6:
            outline(d, (640, int(-60 + 290 * k)), "DIWALI", FBIG, YEL, 9)
            outline(d, (640, int(-60 + 390 * k)), "CRACKER NIGHT!", FMID, WHITE, 6)
        txt = "Crackers are lit only by grown ups. Kids, never light crackers yourself!"
        d.rounded_rectangle([170, 640, 1110, 694], radius=26, fill=(255, 245, 220, 235), outline=NAVY, width=3)
        d.text((640, 667), txt, font=FSM, fill=NAVY, anchor="mm")
    cur = [e for e in says if e["t"] <= ts < e["t"] + e["dur"] + 0.25]
    if cur:
        e = cur[-1]; lines = wrap(d, e["text"], FSUB, 900)
        h = 26 + 46 * len(lines)
        y0 = 700 - h
        d.rounded_rectangle([170, y0, 1110, 700], radius=28, fill=(255, 252, 240, 238), outline=NAVY, width=4)
        for j, l in enumerate(lines):
            d.text((640, y0 + 36 + j * 46), l, font=FSUB, fill=NAVY, anchor="mm")
        tag, col = TAG[e["who"]]
        tw = d.textlength(tag, font=FTAG) + 30
        d.rounded_rectangle([196, y0 - 18, 196 + tw, y0 + 16], radius=17, fill=col, outline=NAVY, width=3)
        d.text((196 + tw / 2, y0 - 1), tag, font=FTAG, fill=NAVY, anchor="mm")
    if ts >= endc["t"]:
        k = min(1, (ts - endc["t"]) / 0.6)
        outline(d, (640, int(-80 + 300 * k)), "HAPPY DIWALI!", FBIG, YEL, 9)
        outline(d, (640, int(-80 + 400 * k)), "Ask a grown up to subscribe to Bro Bros Fun!", font("Fredoka.ttf", 36), WHITE, 5)
    im.alpha_composite(ov)
    im.convert("RGB").save(OUTD + fn, compress_level=1)
print("chunk", a, b, "done")
if len(sys.argv) > 3 and sys.argv[3] == "encode":
    out = os.path.expanduser("~/mnt/Downloads/Bro Bros Fun - Diwali Cracker Night 3D.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "24", "-i", OUTD + "f_%04d.png", "-i", D + "audio.wav",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-ac", "2",
                    "-shortest", "-movflags", "+faststart", out], check=True)
    print("ENCODED", out, os.path.getsize(out))
