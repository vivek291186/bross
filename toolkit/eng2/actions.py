"""Reusable center-stage animations for Bro Bros Fun episodes."""
import math, random
from PIL import Image, ImageDraw
from engine import *

CX, CY = 640, 420   # center stage

def panel(im, box, fill=WHITE, r=24, outline=NAVY, w=5):
    def fn(d, s, _):
        d.rounded_rectangle([w * s, w * s, (box[2] - box[0] - w) * s, (box[3] - box[1] - w) * s], radius=r * s, fill=fill, outline=outline, width=w * s)
    spr = aa(box[2] - box[0], box[3] - box[1], fn)
    im.alpha_composite(spr, (box[0], box[1]))

def label(im, xy, text, size=34, fill=WHITE, ow=5):
    d = ImageDraw.Draw(im)
    text_outline(d, xy, text, FD(size), fill, ow=ow, shadow=3)

# ---- props ----
def draw_pumpkin(d, x, y, r, face=True):
    d.ellipse([x - r, y - r * 0.82, x + r, y + r * 0.82], fill=(255, 140, 20), outline=NAVY, width=4)
    d.arc([x - r * 0.55, y - r * 0.82, x + r * 0.55, y + r * 0.82], 270, 90, fill=(210, 100, 10), width=3)
    d.arc([x - r * 0.55, y - r * 0.82, x + r * 0.55, y + r * 0.82], 90, 270, fill=(210, 100, 10), width=3)
    d.rectangle([x - 4, y - r * 0.82 - 12, x + 4, y - r * 0.82 + 2], fill=(60, 140, 50), outline=NAVY, width=2)
    if face:
        for sx in (-1, 1):
            d.polygon([(x + sx * r * 0.35 - 8, y - 4), (x + sx * r * 0.35 + 8, y - 4), (x + sx * r * 0.35, y - 18)], fill=NAVY)
        d.chord([x - r * 0.5, y - r * 0.1, x + r * 0.5, y + r * 0.5], 0, 180, fill=NAVY)

def draw_pin(d, x, y, ang=0, s=1.0):
    pts = [(-9, -40), (9, -40), (14, 0), (9, 20), (-9, 20), (-14, 0)]
    ca, sa = math.cos(ang), math.sin(ang)
    P = [(x + (px * ca - py * sa) * s, y + (px * sa + py * ca) * s) for px, py in pts]
    d.polygon(P, fill=WHITE, outline=NAVY)
    hx, hy = x + (0 * ca - (-30) * sa) * s, y + (0 * sa + (-30) * ca) * s
    d.ellipse([hx - 9 * s, hy - 9 * s, hx + 9 * s, hy + 9 * s], fill=(255, 150, 30), outline=NAVY)

def draw_candy(d, x, y, c, r=11):
    d.polygon([(x - r - 9, y - 7), (x - r, y), (x - r - 9, y + 7)], fill=c, outline=NAVY)
    d.polygon([(x + r + 9, y - 7), (x + r, y), (x + r + 9, y + 7)], fill=c, outline=NAVY)
    d.ellipse([x - r, y - r, x + r, y + r], fill=c, outline=NAVY, width=2)

def draw_ghost(d, x, y, r=40, alpha_face=True):
    d.pieslice([x - r, y - r, x + r, y + r], 180, 360, fill=WHITE, outline=NAVY, width=4)
    d.rectangle([x - r, y, x + r, y + r * 0.9], fill=WHITE)
    d.line([x - r, y, x - r, y + r * 0.9], fill=NAVY, width=4); d.line([x + r, y, x + r, y + r * 0.9], fill=NAVY, width=4)
    for k in range(4):
        xx = x - r + k * r / 2
        d.pieslice([xx, y + r * 0.65, xx + r / 2, y + r * 1.15], 0, 180, fill=WHITE, outline=NAVY, width=3)
    d.ellipse([x - 16, y - 12, x - 4, y + 4], fill=NAVY); d.ellipse([x + 4, y - 12, x + 16, y + 4], fill=NAVY)
    d.ellipse([x - 7, y + 10, x + 7, y + 26], fill=NAVY)

def draw_diya(d, x, y, r=34, lit=True, flick=0.0):
    if lit:
        fh = r * (1.05 + 0.12 * math.sin(flick * 9))
        d.ellipse([x - r * 0.42, y - r * 0.2 - fh, x + r * 0.42, y - r * 0.15], fill=(255, 190, 30))
        d.ellipse([x - r * 0.22, y - r * 0.2 - fh * 0.7, x + r * 0.22, y - r * 0.2], fill=(255, 250, 200))
    d.chord([x - r, y - r * 0.55, x + r, y + r * 0.75], 0, 180, fill=(205, 100, 40), outline=NAVY, width=4)
    d.line([x - r * 0.75, y + r * 0.25, x + r * 0.75, y + r * 0.25], fill=(255, 210, 90), width=3)

def glow(im, x, y, r, c=(255, 200, 60), a=120):
    g = Image.new("RGBA", (2 * r, 2 * r), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    for k in range(r, 0, -4):
        gd.ellipse([r - k, r - k, r + k, r + k], fill=c + (int(a * (1 - k / r) ** 1.6),))
    im.alpha_composite(g, (int(x - r), int(y - r)))

# ---- actions ----
def race_bars(labels=("BIG BRO", "LIL BRO"), finals=(100, 80), unit="%", title=None, cols=(CYAN, PINK)):
    def ov(im, u, ts):
        panel(im, (470, 250, 810, 560))
        d = ImageDraw.Draw(im)
        if title: d.text((640, 285), title, font=FD(26), fill=NAVY, anchor="mm")
        for i, (lab, fin, c) in enumerate(zip(labels, finals, cols)):
            y = 345 + i * 110
            v = fin * ease(min(1, u * 1.15))
            d.text((500, y - 26), lab, font=FD(22), fill=NAVY, anchor="lm")
            d.rounded_rectangle([500, y, 780, y + 38], radius=19, fill=(232, 228, 245), outline=NAVY, width=3)
            w_ = int(280 * v / max(finals + (100,)))
            if w_ > 8: d.rounded_rectangle([500, y, 500 + w_, y + 38], radius=19, fill=c, outline=NAVY, width=3)
            d.text((780, y - 26), f"{int(v)}{unit}", font=FD(24), fill=NAVY, anchor="rm")
    return ov

def jars(final=(12, 15), draw_item=None, title="COUNT!", cols=None):
    rnd = random.Random(5)
    pos = [[(rnd.uniform(-48, 48), rnd.uniform(-10, 0)) for _ in range(60)] for _ in range(2)]
    palette = cols or [(255, 80, 80), (255, 200, 40), (80, 200, 120), (90, 160, 255), (200, 90, 230)]
    def ov(im, u, ts):
        d = ImageDraw.Draw(im)
        for j, cx in enumerate((560, 720)):
            n = int(final[j] * min(1, u * 1.2))
            # jar
            d.rounded_rectangle([cx - 66, 330, cx + 66, 560], radius=26, fill=(235, 245, 255), outline=NAVY, width=5)
            for k in range(n):
                row, col = divmod(k, 6)
                x = cx - 50 + col * 20 + (row % 2) * 8
                y = 540 - row * 20
                if draw_item: draw_item(d, x, y, k)
                else: draw_candy(d, x, y, palette[k % len(palette)], r=8)
            d.rectangle([cx - 56, 316, cx + 56, 334], fill=(150, 100, 60), outline=NAVY, width=4)
            text_outline(d, (cx, 290), str(n), FD(40), WHITE, ow=5, shadow=3)
        label(im, (640, 240), title, 30, YEL)
    return ov

def quiz(question, options, correct=None, reveal=0.7, picks=None):
    """picks: dict who->index chosen, shown with face tags."""
    def ov(im, u, ts):
        panel(im, (440, 215, 840, 590))
        d = ImageDraw.Draw(im)
        lines = wrap(question, FD(26), 340, d)
        for i, l in enumerate(lines[:3]):
            d.text((640, 255 + i * 32), l, font=FD(26), fill=NAVY, anchor="mm")
        y0 = 255 + len(lines[:3]) * 32 + 12
        for i, o in enumerate(options):
            y = y0 + i * 62
            show_ok = correct is not None and u >= reveal and i == correct
            show_bad = correct is not None and u >= reveal and i != correct and picks and i in picks.values()
            fill = (110, 220, 130) if show_ok else ((255, 140, 140) if show_bad else (238, 234, 252))
            d.rounded_rectangle([470, y, 810, y + 50], radius=25, fill=fill, outline=NAVY, width=3)
            d.text((500, y + 25), "ABCD"[i], font=FD(24), fill=PINK, anchor="mm")
            d.text((530, y + 25), o, font=FB(22), fill=NAVY, anchor="lm")
            if picks and u > 0.35:
                for who, idx in picks.items():
                    if idx == i:
                        fs = face_sprite(who, r=15)
                        im.alpha_composite(fs, (780 - (0 if who == "big" else 36), y + 25 - fs.height // 2))
    return ov

def meters(title, finals=(70, 90), cols=(CYAN, PINK)):
    def ov(im, u, ts):
        panel(im, (500, 230, 780, 590))
        d = ImageDraw.Draw(im)
        d.text((640, 262), title, font=FD(24), fill=NAVY, anchor="mm")
        for i, (fin, c) in enumerate(zip(finals, cols)):
            x = 580 + i * 120
            wob = 6 * math.sin(ts * 12 + i) if u < 0.85 else 0
            v = max(0, min(100, fin * ease(min(1, u * 1.1)) + wob))
            d.rounded_rectangle([x - 28, 300, x + 28, 540], radius=28, fill=(238, 234, 252), outline=NAVY, width=4)
            h = int(232 * v / 100)
            if h > 20: d.rounded_rectangle([x - 24, 536 - h, x + 24, 536], radius=24, fill=c)
            d.text((x, 566), "BIG BRO" if i == 0 else "LIL BRO", font=FD(16), fill=NAVY, anchor="mm")
            d.text((x, 290), f"{int(v)}", font=FD(22), fill=NAVY, anchor="mm")
    return ov

def timer(seconds=10, label_text="GO!"):
    def ov(im, u, ts):
        d = ImageDraw.Draw(im)
        left = max(0, seconds - ts)
        d.ellipse([560, 330, 720, 490], fill=WHITE, outline=NAVY, width=6)
        frac = left / seconds
        d.pieslice([572, 342, 708, 478], -90, -90 + 360 * frac, fill=(255, 210, 63))
        d.ellipse([600, 370, 680, 450], fill=WHITE, outline=NAVY, width=3)
        d.text((640, 410), str(int(math.ceil(left))), font=FD(44), fill=NAVY, anchor="mm")
        label(im, (640, 300), label_text, 34, YEL)
    return ov

def countdown_321():
    def ov(im, u, ts):
        k = int(ts)  # 0,1,2,3
        txt = ["3", "2", "1", "GO!"][min(3, k)]
        f = ts - k
        size = int(150 - 60 * f)
        label(im, (640, 380), txt, size, YEL if txt != "GO!" else (120, 230, 120), ow=8)
    return ov

def bowling(knock=7, total=10):
    rnd = random.Random(knock)
    pins = []
    rows = [4, 3, 2, 1]
    for r_, cnt in enumerate(rows):
        for c in range(cnt):
            pins.append((700 + r_ * 26, 420 + (c - (cnt - 1) / 2) * 34))
    fall = set(rnd.sample(range(total), knock))
    def ov(im, u, ts):
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([470, 440, 820, 520], radius=12, fill=(200, 150, 90), outline=NAVY, width=4)
        bx = lerp(480, 720, min(1, u / 0.55)); by = 470
        hit = u > 0.55
        for i, (px, py) in enumerate(pins):
            ang = 0
            if hit and i in fall:
                ang = min(1.4, (u - 0.55) * 6) * (1 if i % 2 else -1)
            draw_pin(d, px - 10, py - 10 + 30, ang, s=0.7)
        if not hit or u < 0.7:
            draw_pumpkin(d, bx, by - 6, 26, face=True)
        if u > 0.75:
            label(im, (640, 300), f"{knock} PINS!" if knock < total else "STRIKE!", 48, YEL if knock < total else (120, 230, 120))
    return ov

def ring_toss(hits=(1, 1, 0, 1, 0)):
    def ov(im, u, ts):
        d = ImageDraw.Draw(im)
        # witch hat target
        d.polygon([(600, 520), (680, 520), (648, 330)], fill=(60, 40, 120), outline=NAVY, width=4)
        d.ellipse([560, 505, 720, 540], fill=(60, 40, 120), outline=NAVY, width=4)
        n = len(hits); per = 1 / n
        k = min(n - 1, int(u / per)); f = (u - k * per) / per
        landed = sum(hits[:k])
        for j in range(landed):
            d.ellipse([612 - j * 3, 470 - j * 22, 668 + j * 3, 486 - j * 22], outline=(255, 210, 63), width=6)
        x = lerp(470, 640, f); y = 520 - 260 * math.sin(math.pi * min(1, f)) * 0.9
        if not hits[k]: x += f * 120
        if f < 0.95:
            d.ellipse([x - 28, y - 8, x + 28, y + 8], outline=(255, 210, 63), width=6)
        label(im, (640, 260), f"{landed + (hits[k] if f >= 0.95 else 0)} / {n}", 40, WHITE)
    return ov

def doors(n=3, ghost_at=1, open_seq=(1,), labels=("SOFA", "CURTAIN", "BOX")):
    def ov(im, u, ts):
        d = ImageDraw.Draw(im)
        w_ = 104
        for i in range(n):
            x = 482 + i * (w_ + 8)
            opened = any(u > (0.3 + 0.3 * j) for j, o in enumerate(open_seq) if o == i)
            d.rounded_rectangle([x, 330, x + w_, 560], radius=14, fill=(140, 80, 40), outline=NAVY, width=4)
            if opened:
                d.rounded_rectangle([x + 6, 336, x + w_ - 6, 554], radius=10, fill=(30, 20, 60))
                if i == ghost_at:
                    draw_ghost(d, x + w_ / 2, 420, 34)
                else:
                    d.text((x + w_ / 2, 445), "EMPTY", font=FD(18), fill=WHITE, anchor="mm")
            else:
                d.ellipse([x + w_ - 26, 440, x + w_ - 14, 452], fill=YEL, outline=NAVY)
                d.text((x + w_ / 2, 360), labels[i], font=FD(16), fill=WHITE, anchor="mm")
    return ov

def gift_reveal(draw_item, text=None):
    def ov(im, u, ts):
        d = ImageDraw.Draw(im)
        open_ = u > 0.5
        lid = 0 if not open_ else min(1, (u - 0.5) * 4)
        shake = 0 if open_ else 6 * math.sin(ts * 30)
        x0 = 560 + shake
        if open_:
            draw_item(im, d, min(1, (u - 0.5) * 3))
        d.rectangle([x0, 430, x0 + 160, 560], fill=(150, 90, 230), outline=NAVY, width=5)
        d.rectangle([x0 + 70, 430, x0 + 90, 560], fill=YEL, outline=NAVY, width=3)
        ly = 410 - 120 * lid
        d.rectangle([x0 - 10, ly, x0 + 170, ly + 26], fill=(170, 110, 250), outline=NAVY, width=5)
        if not open_:
            label(im, (640, 360), "?", 80, YEL)
        if text and u > 0.7:
            label(im, (640, 270), text, 40, YEL)
    return ov

def notes(im, ts, color=WHITE):
    d = ImageDraw.Draw(im)
    for k in range(6):
        x = 520 + (k * 53) % 260; y = 560 - ((ts * 90 + k * 70) % 330)
        d.ellipse([x - 12, y - 9, x + 6, y + 9], fill=color, outline=NAVY, width=3)
        d.line([x + 5, y, x + 5, y - 38], fill=NAVY, width=4)
        d.line([x + 5, y - 38, x + 20, y - 30], fill=NAVY, width=4)

def score_pop(who, pts=1):
    def ov(im, u, ts):
        x = 315 if who == "big" else 965
        y = 210 - 60 * ease(u)
        label(im, (x, y), f"+{pts}", 70, (120, 230, 120), ow=7)
    return ov

def confetti(im, ts, n=60, seed=1):
    rnd = random.Random(seed); d = ImageDraw.Draw(im)
    cols = [YEL, PINK, CYAN, (120, 230, 120), WHITE, (255, 140, 20)]
    for i in range(n):
        x0 = rnd.uniform(0, W); sp = rnd.uniform(120, 260); ph = rnd.uniform(0, 600)
        y = (ph + ts * sp) % 720 - 40; x = x0 + 30 * math.sin(ts * 3 + i)
        c = cols[i % len(cols)]
        d.rectangle([x, y, x + 10, y + 16], fill=c)
