"""Themed stage sets + funny face effects for Bro Bros Fun."""
import math, random
from PIL import Image, ImageDraw, ImageFilter
from engine import *

_set_cache = {}

def _grad(c1, c2):
    im = Image.new("RGB", (W, H), c1); d = ImageDraw.Draw(im)
    for y in range(H):
        d.line([0, y, W, y], fill=mix(c1, c2, y / H))
    return im

def haunted_set(variant="night"):
    key = ("haunt", variant)
    if key in _set_cache: return _set_cache[key]
    sky = {"night": ((30, 18, 80), (110, 50, 150)), "sunset": ((90, 30, 120), (255, 120, 50)),
           "fog": ((20, 60, 70), (60, 140, 120)), "moon": ((15, 25, 70), (60, 80, 160))}[variant]
    im = _grad(*sky).convert("RGBA")
    s = 2
    def fn(d, S_, big):
        S = lambda *v: [x * S_ for x in v]
        rnd = random.Random(11)
        for _ in range(60):
            x, y = rnd.randint(0, W), rnd.randint(0, 300); r = rnd.choice([1, 1, 2])
            d.ellipse(S(x - r, y - r, x + r, y + r), fill=(255, 250, 220, 200))
        # moon with glow
        mx, my = 1080, 120
        for k in range(6, 0, -1):
            r = 60 + k * 14
            d.ellipse(S(mx - r, my - r, mx + r, my + r), fill=(255, 240, 180, 14))
        d.ellipse(S(mx - 60, my - 60, mx + 60, my + 60), fill=(255, 245, 200, 255))
        for (cx, cy, r) in [(1060, 100, 12), (1100, 140, 8), (1090, 95, 6)]:
            d.ellipse(S(cx - r, cy - r, cx + r, cy + r), fill=(235, 220, 170, 255))
        # far hills
        d.polygon(S(0, 470, 200, 400, 420, 450, 640, 390, 900, 440, 1120, 395, 1280, 430, 1280, 620, 0, 620), fill=(40, 20, 70, 255))
        # haunted house center-back
        hx = 640
        d.polygon(S(hx - 150, 330, hx, 210, hx + 150, 330), fill=(25, 12, 45, 255))
        d.rectangle(S(hx - 130, 330, hx + 130, 560), fill=(30, 15, 55, 255))
        d.polygon(S(hx + 60, 250, hx + 95, 180, hx + 130, 250), fill=(25, 12, 45, 255))
        d.rectangle(S(hx + 70, 250, hx + 120, 330), fill=(30, 15, 55, 255))
        for (wx, wy) in [(hx - 90, 370), (hx + 50, 370), (hx - 90, 450), (hx + 50, 450), (hx - 18, 270)]:
            d.rectangle(S(wx, wy, wx + 40, wy + 46), fill=(255, 200, 60, 255))
            d.line(S(wx + 20, wy, wx + 20, wy + 46), fill=(30, 15, 55, 255), width=3 * S_)
            d.line(S(wx, wy + 23, wx + 40, wy + 23), fill=(30, 15, 55, 255), width=3 * S_)
        d.rectangle(S(hx - 22, 500, hx + 22, 560), fill=(80, 40, 20, 255))
        # bare trees
        for tx, flip in ((150, 1), (1150, -1)):
            d.line(S(tx, 620, tx, 300), fill=(20, 10, 35, 255), width=22 * S_)
            for k in range(4):
                y = 330 + k * 55
                d.line(S(tx, y, tx + flip * (90 - k * 10), y - 60), fill=(20, 10, 35, 255), width=9 * S_)
                d.line(S(tx, y + 20, tx - flip * (70 - k * 8), y - 30), fill=(20, 10, 35, 255), width=7 * S_)
        # bats
        for (bx, by, sz) in [(300, 120, 1.0), (380, 170, 0.7), (850, 90, 0.8), (960, 200, 0.6)]:
            d.polygon(S(bx, by, bx - 30 * sz, by - 14 * sz, bx - 20 * sz, by + 2 * sz, bx - 40 * sz, by + 4 * sz, bx, by + 10 * sz,
                        bx + 40 * sz, by + 4 * sz, bx + 20 * sz, by + 2 * sz, bx + 30 * sz, by - 14 * sz), fill=(15, 8, 25, 255))
        # fence
        for fx in range(0, W + 1, 46):
            d.polygon(S(fx, 600, fx, 545, fx + 9, 530, fx + 18, 545, fx + 18, 600), fill=(15, 8, 25, 255))
        d.rectangle(S(0, 560, W, 568), fill=(15, 8, 25, 255))
        # ground + floor band
        d.rectangle(S(0, 600, W, 620), fill=(35, 60, 30, 255))
    layer = aa(W, H, fn)
    im.alpha_composite(layer)
    # fog
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0)); fd = ImageDraw.Draw(fog)
    for k in range(14):
        x = (k * 97) % W; fd.ellipse([x - 160, 540, x + 160, 640], fill=(230, 220, 255, 26))
    im.alpha_composite(fog.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 620, W, H], fill=(48, 26, 92))
    for i in range(0, W, 107): d.rectangle([i, 620, i + 53, H], fill=(58, 34, 110))
    d.line([0, 620, W, 620], fill=(25, 14, 60), width=4)
    # small pumpkins on the floor edge
    for px in (60, 1220, 560, 720):
        r = 22
        d.ellipse([px - r, 590 - r * 0.8, px + r, 590 + r * 0.8], fill=(255, 140, 20), outline=NAVY, width=3)
        d.rectangle([px - 3, 568, px + 3, 576], fill=(60, 140, 50))
        d.polygon([(px - 9, 586), (px - 3, 586), (px - 6, 579)], fill=(255, 230, 120))
        d.polygon([(px + 3, 586), (px + 9, 586), (px + 6, 579)], fill=(255, 230, 120))
    out = im.convert("RGB")
    _set_cache[key] = out
    return out

def diwali_set(variant="evening"):
    key = ("diwali", variant)
    if key in _set_cache: return _set_cache[key]
    wall = {"evening": ((255, 196, 120), (245, 150, 90)), "night": ((70, 40, 110), (120, 60, 130)),
            "pink": ((255, 170, 190), (240, 120, 160)), "gold": ((255, 215, 120), (240, 175, 70))}[variant]
    im = _grad(*wall).convert("RGBA")
    def fn(d, S_, big):
        S = lambda *v: [x * S_ for x in v]
        # window with night sky and fireworks-free sparkles
        d.rounded_rectangle(S(500, 150, 780, 400), radius=20 * S_, fill=(30, 30, 90, 255), outline=(120, 70, 30, 255), width=12 * S_)
        d.line(S(640, 150, 640, 400), fill=(120, 70, 30, 255), width=8 * S_)
        d.line(S(500, 275, 780, 275), fill=(120, 70, 30, 255), width=8 * S_)
        rnd = random.Random(4)
        for _ in range(25):
            x, y = rnd.randint(515, 765), rnd.randint(165, 385); r = rnd.choice([1, 2])
            d.ellipse(S(x - r, y - r, x + r, y + r), fill=(255, 250, 210, 255))
        d.ellipse(S(700, 180, 740, 220), fill=(255, 245, 200, 255))
        # toran: mango leaves + marigolds across top
        for k in range(28):
            x = 20 + k * 46
            d.polygon(S(x, 60, x + 16, 60, x + 8, 110), fill=(50, 150, 60, 255), outline=(20, 80, 30, 255))
        for k in range(56):
            x = 10 + k * 23
            d.ellipse(S(x - 12, 46, x + 12, 70), fill=[(255, 150, 0, 255), (255, 200, 30, 255)][k % 2], outline=(190, 90, 0, 255))
        # string lights (two drapes)
        for (x0, x1) in ((0, 470), (810, 1280)):
            pts = []
            for i in range(25):
                t = i / 24; x = lerp(x0, x1, t); y = 140 + 70 * math.sin(math.pi * t)
                pts.append((x, y))
            d.line([(p[0] * S_, p[1] * S_) for p in pts], fill=(60, 40, 30, 255), width=3 * S_)
            for i, (x, y) in enumerate(pts[::2]):
                c = [(255, 220, 80), (255, 90, 120), (100, 220, 255), (140, 255, 140)][i % 4]
                for k in range(3, 0, -1):
                    d.ellipse(S(x - 6 * k, y + 8 - 6 * k, x + 6 * k, y + 8 + 6 * k), fill=c + (40,))
                d.ellipse(S(x - 6, y + 2, x + 6, y + 14), fill=c + (255,))
        # hanging lanterns (kandil)
        for (lx, c) in ((90, (230, 40, 80)), (1190, (255, 150, 0))):
            d.line(S(lx, 110, lx, 190), fill=(80, 50, 30, 255), width=3 * S_)
            d.polygon(S(lx, 190, lx + 40, 245, lx, 300, lx - 40, 245), fill=c + (255,), outline=NAVY + (255,), width=4 * S_)
            d.polygon(S(lx, 210, lx + 22, 245, lx, 280, lx - 22, 245), fill=(255, 230, 120, 255))
            for k in (-12, 0, 12): d.line(S(lx + k, 300, lx + k, 335), fill=(255, 210, 60, 255), width=3 * S_)
        # side table shelves with diyas (left/right back)
        for sx in (40, 1100):
            d.rectangle(S(sx, 480, sx + 140, 495), fill=(140, 80, 40, 255))
        # floor rangoli border strip
        d.rectangle(S(0, 600, W, 620), fill=(255, 235, 200, 255))
        for k in range(0, W, 40):
            c = [(230, 40, 80), (255, 170, 0), (40, 160, 90), (90, 80, 220)][(k // 40) % 4]
            d.polygon(S(k, 610, k + 20, 600, k + 40, 610, k + 20, 620), fill=c + (255,))
    im.alpha_composite(aa(W, H, fn))
    d = ImageDraw.Draw(im)
    for sx in (60, 120, 1120, 1180):
        glow_simple(im, sx, 470, 30)
    d = ImageDraw.Draw(im)
    for sx in (60, 120, 1120, 1180):
        d.ellipse([sx - 6, 456, sx + 6, 476], fill=(255, 200, 40)); d.ellipse([sx - 3, 462, sx + 3, 474], fill=(255, 250, 210))
        d.chord([sx - 18, 466, sx + 18, 490], 0, 180, fill=(205, 100, 40), outline=NAVY, width=3)
    d.rectangle([0, 620, W, H], fill=(120, 40, 60))
    for i in range(0, W, 107): d.rectangle([i, 620, i + 53, H], fill=(140, 50, 70))
    d.line([0, 620, W, 620], fill=(70, 20, 40), width=4)
    out = im.convert("RGB")
    _set_cache[key] = out
    return out

def glow_simple(im, x, y, r, c=(255, 200, 60)):
    g = Image.new("RGBA", (2 * r, 2 * r), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for k in range(r, 0, -3):
        gd.ellipse([r - k, r - k, r + k, r + k], fill=c + (int(110 * (1 - k / r) ** 1.5),))
    im.alpha_composite(g, (int(x - r), int(y - r)))

# ---------- face gags ----------
_fx_cache = {}
def face_img(who, r):
    key = (who, r)
    if key not in _fx_cache:
        _fx_cache[key] = face_sprite(who, r=r)
    return _fx_cache[key]

def face_fx_layer(im, who, cx, cy, fx, ts):
    """Draw a transformed face over the character's face (face center cx,cy)."""
    if fx == "bobble":
        f = face_img(who, 112); wob = 10 * math.sin(ts * 12)
        im.alpha_composite(f.rotate(wob, resample=Image.BICUBIC), (int(cx - f.width / 2), int(cy - f.height / 2 - 20)))
    elif fx == "squash":
        base = face_img(who, 78)
        k = 0.65 + 0.35 * abs(math.sin(ts * 7))
        f = base.resize((int(base.width * (2 - k)), int(base.height * k)), Image.LANCZOS)
        im.alpha_composite(f, (int(cx - f.width / 2), int(cy - f.height / 2 + (base.height - f.height) / 2)))
    elif fx == "spin":
        f = face_img(who, 78).rotate(ts * 540 % 360, resample=Image.BICUBIC)
        im.alpha_composite(f, (int(cx - f.width / 2), int(cy - f.height / 2)))
    elif fx == "tiny":
        bg = face_img(who, 78)
        # cover original with body-coloured disc, then tiny face
        d = ImageDraw.Draw(im)
        d.ellipse([cx - 92, cy - 92, cx + 92, cy + 92], fill=None)
        f = face_img(who, 34)
        im.alpha_composite(f, (int(cx - f.width / 2), int(cy + 20 - f.height / 2)))
    elif fx == "shake":
        f = face_img(who, 78)
        dx = 8 * math.sin(ts * 60); dy = 5 * math.cos(ts * 47)
        im.alpha_composite(f, (int(cx - f.width / 2 + dx), int(cy - f.height / 2 + dy)))
    elif fx == "upside":
        f = face_img(who, 78).rotate(180)
        im.alpha_composite(f, (int(cx - f.width / 2), int(cy - f.height / 2)))

def face_on_pumpkin(im, who, x, y, r=70, ts=0):
    d = ImageDraw.Draw(im)
    d.ellipse([x - r * 1.35, y - r * 1.05, x + r * 1.35, y + r * 1.05], fill=(255, 140, 20), outline=NAVY, width=5)
    for k in (-0.75, 0.75):
        d.arc([x - r * 1.35 * abs(k), y - r * 1.05, x + r * 1.35 * abs(k), y + r * 1.05], 90 if k > 0 else 270, 270 if k > 0 else 90, fill=(210, 100, 10), width=4)
    d.rectangle([x - 8, y - r * 1.05 - 26, x + 8, y - r * 1.05 + 4], fill=(60, 140, 50), outline=NAVY, width=3)
    f = face_img(who, int(r * 0.72))
    im.alpha_composite(f, (int(x - f.width / 2), int(y - f.height / 2)))

def face_on_ghost(im, who, x, y, r=70, ts=0):
    d = ImageDraw.Draw(im)
    y = y + 8 * math.sin(ts * 3)
    d.pieslice([x - r, y - r, x + r, y + r], 180, 360, fill=WHITE, outline=NAVY, width=5)
    d.rectangle([x - r, y, x + r, y + r * 1.1], fill=WHITE)
    d.line([x - r, y, x - r, y + r * 1.1], fill=NAVY, width=5); d.line([x + r, y, x + r, y + r * 1.1], fill=NAVY, width=5)
    for k in range(4):
        xx = x - r + k * r / 2
        d.pieslice([xx, y + r * 0.85, xx + r / 2, y + r * 1.35], 0, 180, fill=WHITE, outline=NAVY, width=4)
    f = face_img(who, int(r * 0.62))
    im.alpha_composite(f, (int(x - f.width / 2), int(y - 10 - f.height / 2)))

def face_on_laddoo(im, who, x, y, r=60, ts=0):
    d = ImageDraw.Draw(im)
    d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 160, 30), outline=NAVY, width=5)
    rnd = random.Random(2)
    for _ in range(30):
        a = rnd.uniform(0, 6.28); rr = rnd.uniform(r * 0.7, r * 0.95)
        px, py = x + rr * math.cos(a), y + rr * math.sin(a)
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(220, 110, 10))
    f = face_img(who, int(r * 0.66))
    im.alpha_composite(f, (int(x - f.width / 2), int(y - f.height / 2)))

def reaction(ep, who, text, sound="boing", dur=2.2, bg=((255, 60, 90), (255, 110, 130))):
    """Meme-style zoom on one face with shaking caption."""
    rays = rays_bg(*bg)
    big = face_sprite(who, r=230)
    def ov(im, u, ts):
        im.paste(rays.convert("RGBA"), (0, 0))
        k = 0.6 + 0.4 * ease(min(1, ts / 0.25))
        f = big.resize((int(big.width * k), int(big.height * k)), Image.LANCZOS)
        dx = 6 * math.sin(ts * 50) if ts < 0.8 else 0
        im.alpha_composite(f, (int(640 - f.width / 2 + dx), int(370 - f.height / 2)))
        d = ImageDraw.Draw(im)
        text_outline(d, (640, 640), text, FD(64), YEL, ow=8, shadow=6)
    ep.action(dur, ov, sounds=[(0, sound, 1.0), (0.05, "whoosh", 0.6)])
