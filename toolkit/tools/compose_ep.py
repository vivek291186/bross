# Rebuild of vse8_local: composite SD frames + overlays (logo, intro card, subtitles, end card) and encode.
# usage: compose_ep.py EPDIR OVDIR AUDIO OUT
import sys, os, json, subprocess
from PIL import Image
EP, OV, AUD, OUT = sys.argv[1:5]
d = json.load(open(os.path.join(OV, "ov.json")))
tl = json.load(open(os.path.join(EP, "timeline.json")))
F = lambda t: int(round(t * 24)) + 1
cards = [e for e in tl["events"] if e["type"] == "card"]
intro_f0 = F(cards[0]["t"]) if cards else 1
total = d["total"]
logo = Image.open(os.path.join(OV, "logo.png")).convert("RGBA")
subs = [(Image.open(os.path.join(OV, s)).convert("RGBA"), a, b) for s, a, b in d["subs"]]
ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "854x480", "-r", "24", "-i", "-",
                       "-i", AUD, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", OUT], stdin=subprocess.PIPE)
for f in range(1, total + 1):
    im = Image.open(os.path.join(EP, "frames_sd", "%05d.jpg" % f)).convert("RGBA")
    im = Image.alpha_composite(im, logo)
    k = f - intro_f0 + 1
    p = os.path.join(OV, "intro_%04d.png" % k)
    if k >= 1 and os.path.exists(p): im = Image.alpha_composite(im, Image.open(p).convert("RGBA"))
    for s, a, b in subs:
        if a <= f <= b: im = Image.alpha_composite(im, s)
    if f >= d["end_start"]:
        im = Image.alpha_composite(im, Image.open(os.path.join(OV, "end_%04d.png" % min(d["end_n"], f - d["end_start"] + 1))).convert("RGBA"))
    ff.stdin.write(im.convert("RGB").tobytes())
ff.stdin.close(); ff.wait(); print("done", OUT, total)
