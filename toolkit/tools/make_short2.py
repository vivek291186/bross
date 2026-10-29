"""Vertical Short (540x960, <15 s) from a finished song video. usage: make_short2.py in.mp4 start dur out.mp4 "TOP TITLE" "button text" """
import sys, subprocess, os
from PIL import Image, ImageDraw, ImageFont
src, ss, dur, out, top, bot = sys.argv[1:7]
FONT = "/home/claude/bbf/assets/Fredoka.ttf"
def font(px):
    f = ImageFont.truetype(FONT, px)
    try: f.set_variation_by_name("Bold")
    except Exception: pass
    return f
INK = (34, 20, 70)
ov = Image.new("RGBA", (540, 960), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
d.text((270, 150), top, font=font(66), fill=(255, 210, 60), stroke_width=6, stroke_fill=INK, anchor="mm")
d.text((270, 230), "Sing along with the Bro Bros!", font=font(26), fill=(255, 255, 255), stroke_width=3, stroke_fill=INK, anchor="mm")
d.rounded_rectangle((150, 790, 390, 850), radius=30, fill=(239, 61, 124), outline=INK, width=4)
d.text((270, 820), bot + "  ▶", font=font(30), fill=(255, 255, 255), anchor="mm")
d.text((270, 900), "BRO BROS FUN", font=font(24), fill=(60, 190, 240), stroke_width=2, stroke_fill=INK, anchor="mm")
png = out + ".ov.png"; ov.save(png)
fc = ("[0:v]scale=1080:608,crop=540:960:270:0,boxblur=18:2,eq=brightness=-0.12[bg];"
      "[0:v]crop=480:480:187:0,scale=540:540[fg];[bg][fg]overlay=0:240[v1];[v1][1:v]overlay=0:0[v]")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(ss), "-t", str(dur), "-i", src, "-i", png, "-filter_complex", fc,
                "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-c:a", "aac", "-b:a", "160k", out], check=True)
os.remove(png); print("short", out)
