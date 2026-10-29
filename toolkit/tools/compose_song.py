"""Composite song frames + song overlays and encode with the full mix. usage: compose_song.py SONGDIR OVDIR AUDIO OUT"""
import sys, os, json, subprocess
from PIL import Image
D, OV, AUD, OUT = sys.argv[1:5]
d = json.load(open(os.path.join(OV, "ov.json")))
logo = Image.open(os.path.join(OV, "logo.png")).convert("RGBA")
subs = [(Image.open(os.path.join(OV, s)).convert("RGBA"), a, b) for s, a, b in d["subs"]]
ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "854x480", "-r", "24", "-i", "-", "-i", AUD,
                       "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", OUT], stdin=subprocess.PIPE)
for f in range(1, d["total"] + 1):
    im = Image.alpha_composite(Image.open(os.path.join(D, "frames_sd", "%05d.jpg" % f)).convert("RGBA"), logo)
    for s, a, b in subs:
        if a <= f <= b: im = Image.alpha_composite(im, s)
    for pre, f0, n, f1 in d["cues"]:
        if f0 <= f <= f1: im = Image.alpha_composite(im, Image.open(os.path.join(OV, f"{pre}{min(n - 1, f - f0):02d}.png")).convert("RGBA"))
    if f >= d["end_start"]:
        im = Image.alpha_composite(im, Image.open(os.path.join(OV, "end_%04d.png" % min(d["end_n"], f - d["end_start"] + 1))).convert("RGBA"))
    ff.stdin.write(im.convert("RGB").tobytes())
ff.stdin.close(); ff.wait(); print("done", OUT)
