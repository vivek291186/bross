"""Bro Bros Fun episode engine: PIL frames + Kokoro voices + synthesized music/SFX -> mp4."""
import math, os, random, subprocess, hashlib, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import soundfile as sf

W, H = 1280, 720
FPS_ACT = 12
SR = 24000
ROOT = "/home/claude/bbf"
A = ROOT + "/assets"
NAVY = (34, 22, 79)
WHITE = (255, 255, 255)
YEL = (255, 210, 63)
PINK = (239, 61, 124)
CYAN = (40, 186, 236)
BLUE_BODY = (64, 192, 235)
PINK_BODY = (238, 72, 128)
SKIN = (166, 110, 72)
PURPLE_FLOOR = (52, 30, 110)

def F(name, size, var=None):
    f = ImageFont.truetype(f"{A}/{name}.ttf", size)
    if var:
        try: f.set_variation_by_name(var)
        except Exception: pass
    return f

FD = lambda s: F("Fredoka", s, "Bold")
FB = lambda s: F("Nunito", s, "Black")

# ---------- helpers ----------
def aa(w, h, fn, scale=2):
    big = Image.new("RGBA", (w * scale, h * scale), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    fn(d, scale, big)
    return big.resize((w, h), Image.LANCZOS)

def lerp(a, b, t): return a + (b - a) * t
def mix(c1, c2, t): return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))
def ease(t): return 0.5 - 0.5 * math.cos(math.pi * max(0, min(1, t)))

_bg_cache = {}
def rays_bg(c1, c2, n=28, stars=False):
    key = (c1, c2, n, stars)
    if key in _bg_cache: return _bg_cache[key]
    s = 2
    im = Image.new("RGB", (W * s, H * s), c1)
    d = ImageDraw.Draw(im)
    cx, cy, R = W * s // 2, int(H * s * 0.48), W * s * 2
    for i in range(n):
        if i % 2: continue
        a1 = 2 * math.pi * i / n; a2 = 2 * math.pi * (i + 1) / n
        d.polygon([(cx, cy), (cx + R * math.cos(a1), cy + R * math.sin(a1)), (cx + R * math.cos(a2), cy + R * math.sin(a2))], fill=c2)
    im = im.resize((W, H), Image.LANCZOS)
    # radial soft vignette toward center glow
    glow = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(glow)
    for r in range(380, 0, -20):
        gd.ellipse([W // 2 - r * 1.6, H * 0.48 - r, W // 2 + r * 1.6, H * 0.48 + r], fill=int(60 * (1 - r / 380)))
    glow = glow.filter(ImageFilter.GaussianBlur(40))
    im = Image.composite(Image.new("RGB", (W, H), (255, 255, 255)), im, glow)
    if stars:
        rnd = random.Random(7); d = ImageDraw.Draw(im)
        for _ in range(70):
            x, y, r = rnd.randint(0, W), rnd.randint(0, 600), rnd.choice([1, 1, 2, 2, 3])
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 250, 220))
    # floor
    d = ImageDraw.Draw(im)
    d.rectangle([0, 620, W, H], fill=PURPLE_FLOOR)
    for i in range(0, W, 107):
        d.rectangle([i, 620, i + 53, H], fill=(60, 36, 124))
    d.line([0, 620, W, 620], fill=(30, 18, 70), width=4)
    _bg_cache[key] = im
    return im

def text_outline(d, xy, txt, font, fill, outline=NAVY, ow=4, anchor="mm", shadow=0):
    if shadow:
        d.text((xy[0] + shadow, xy[1] + shadow), txt, font=font, fill=outline, anchor=anchor, stroke_width=ow, stroke_fill=outline)
    d.text(xy, txt, font=font, fill=fill, anchor=anchor, stroke_width=ow, stroke_fill=outline)

def wrap(text, font, maxw, d):
    words = text.split(); lines = []; cur = ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else:
            if cur: lines.append(cur)
            cur = w_
    if cur: lines.append(cur)
    return lines

# ---------- logo ----------
_logo = None
def logo():
    global _logo
    if _logo: return _logo
    def fn(d, s, im):
        text_outline(d, (95 * s, 22 * s), "BRO BROS", FD(30 * s), YEL, ow=4 * s, shadow=3 * s)
        text_outline(d, (100 * s, 56 * s), "FUN!", FD(40 * s), PINK, ow=4 * s, shadow=3 * s)
    _logo = aa(200, 84, fn)
    return _logo

# ---------- faces ----------
def face_sprite(who, r=78):
    src = Image.open(f"{A}/face_{who}_25.png").convert("RGB")
    # source 170px covers circle radius (r_src-12); crop inside white ring
    w, h = src.size
    inset = int(w * 0.10)
    src = src.crop((inset, inset, w - inset, h - inset)).resize((2 * r * 2, 2 * r * 2), Image.LANCZOS)
    def fn(d, s, im):
        R = (r + 12) * s
        c = (r + 12) * s
        d.ellipse([c - R, c - R, c + R, c + R], fill=NAVY)
        R2 = (r + 6) * s
        d.ellipse([c - R2, c - R2, c + R2, c + R2], fill=WHITE)
        mask = Image.new("L", (2 * r * s, 2 * r * s), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, 2 * r * s - 1, 2 * r * s - 1], fill=255)
        im.paste(src.resize((2 * r * s, 2 * r * s)), (c - r * s, c - r * s), mask)
    return aa(2 * (r + 12), 2 * (r + 12), fn)

# ---------- characters ----------
_char_cache = {}
def character(who, pose="idle", costume=()):
    """Return RGBA sprite 320x470; face center at (160,100)."""
    key = (who, pose, tuple(costume))
    if key in _char_cache: return _char_cache[key]
    body = BLUE_BODY if who == "big" else PINK_BODY
    dark = tuple(int(c * 0.82) for c in body)
    label = "BIG BRO" if who == "big" else "LIL BRO"
    cw, ch = 320, 470
    def fn(d, s, im):
        S = lambda *v: [x * s for x in v]
        sh_l, sh_r = (112, 228), (208, 228)
        if pose == "idle":
            hands = [(78, 395), (242, 395)]
        elif pose == "cheer":
            hands = [(62, 120), (258, 120)]
        elif pose == "point_r":
            hands = [(78, 395), (300, 240)]
        elif pose == "point_l":
            hands = [(20, 240), (242, 395)]
        elif pose == "shrug":
            hands = [(40, 230), (280, 230)]
        elif pose == "think":
            hands = [(78, 395), (190, 170)]
        elif pose == "dance1":
            hands = [(50, 140), (250, 395)]
        elif pose == "dance2":
            hands = [(70, 395), (270, 140)]
        else:
            hands = [(78, 395), (242, 395)]
        if "cape" in costume:
            d.polygon(S(95, 205, 225, 205, 268, 455, 52, 455), fill=(150, 20, 40), outline=NAVY, width=5 * s)
        # arms behind torso
        for (sx, sy), (hx, hy) in zip([sh_l, sh_r], hands):
            d.line(S(sx, sy, hx, hy), fill=NAVY, width=44 * s, joint="curve")
            d.line(S(sx, sy, hx, hy), fill=body, width=34 * s, joint="curve")
            d.ellipse(S(sx - 22, sy - 22, sx + 22, sy + 22), fill=body)
        # torso
        d.rounded_rectangle(S(88, 200, 232, 450), radius=48 * s, fill=body, outline=NAVY, width=5 * s)
        d.rounded_rectangle(S(100, 380, 220, 444), radius=36 * s, fill=dark)
        d.rounded_rectangle(S(88, 200, 232, 450), radius=48 * s, outline=NAVY, width=5 * s)
        if "mummy" in costume:
            for i, y in enumerate(range(225, 445, 26)):
                d.polygon(S(88, y, 232, y - 12 + (i % 2) * 18, 232, y + 4 + (i % 2) * 18, 88, y + 16), fill=(245, 240, 225), outline=(190, 180, 160))
        # collar
        d.chord(S(130, 186, 190, 236), 0, 180, fill=WHITE, outline=NAVY, width=4 * s)
        # name tag
        d.rounded_rectangle(S(108, 285, 212, 320), radius=10 * s, fill=WHITE, outline=NAVY, width=4 * s)
        d.text((160 * s, 303 * s), label, font=FD(20 * s), fill=NAVY, anchor="mm")
        if "garland" in costume:
            cols = [(255, 160, 0), (255, 200, 30), (240, 110, 0)]
            for i in range(17):
                t = i / 16
                x = lerp(110, 210, t); y = 215 + 70 * math.sin(math.pi * t)
                r = 11
                d.ellipse(S(x - r, y - r, x + r, y + r), fill=cols[i % 3], outline=(180, 90, 0), width=2 * s)
        # hands on top
        for (hx, hy) in hands:
            d.ellipse(S(hx - 18, hy - 18, hx + 18, hy + 18), fill=SKIN, outline=NAVY, width=4 * s)
        # face
        fs = face_sprite(who)
        big = fs.resize((fs.width * s, fs.height * s), Image.LANCZOS)
        im.alpha_composite(big, (160 * s - big.width // 2, 100 * s - big.height // 2))
        if "wizard" in costume:
            d.polygon(S(80, 40, 240, 40, 168, -60 + 60), fill=(90, 50, 200), outline=NAVY, width=5 * s)
        if "pumpkin_crown" in costume:
            for k in range(5):
                x = 105 + k * 28
                d.polygon(S(x, 22, x + 14, -2 + 10, x + 28, 22), fill=YEL, outline=NAVY, width=3 * s)
            d.rectangle(S(105, 18, 245 - 0, 32), fill=YEL, outline=NAVY, width=3 * s)
        if "horns" in costume:
            for sx in (1, -1):
                x0 = 160 + sx * 55
                d.polygon(S(x0 - 14, 30, x0 + 14, 30, x0 + sx * 30, -5 + 15), fill=(230, 40, 40), outline=NAVY, width=4 * s)
    if "wizard" in costume:
        # stars on hat: drawn separately for clarity
        pass
    spr = aa(cw, ch, fn)
    if "wizard" in costume:
        d = ImageDraw.Draw(spr)
        d.ellipse([60, 26, 260, 54], fill=(90, 50, 200), outline=NAVY, width=4)
        for (x, y) in [(150, 0), (175, 22), (140, 28)]:
            star(d, x, y + 2, 7, YEL)
    _char_cache[key] = spr
    return spr

def star(d, x, y, r, c, outline=None):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.45; a = -math.pi / 2 + i * math.pi / 5
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    d.polygon(pts, fill=c, outline=outline)

def burst(r=170, c=(255, 226, 90)):
    def fn(d, s, im):
        pts = []
        for i in range(32):
            rr = (r if i % 2 == 0 else r * 0.78) * s; a = i * math.pi / 16
            pts.append((r * s + rr * math.cos(a), r * s + rr * math.sin(a)))
        d.polygon(pts, fill=c, outline=NAVY, width=4 * s)
    return aa(2 * r, 2 * r, fn)
BURST = None

# ---------- bubbles ----------
TAGC = {"big": CYAN, "lil": PINK, "ann": YEL}
TAGN = {"big": "BIG BRO", "lil": "LIL BRO", "ann": "SHOW HOST"}
_bub_cache = {}
def bubble(who, text):
    key = (who, text)
    if key in _bub_cache: return _bub_cache[key]
    font = FB(29); tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    maxw = 520 if who != "ann" else 760
    lines = wrap(text, font, maxw, tmp)
    if len(lines) > 3:
        font = FB(25); lines = wrap(text, font, maxw + 40, tmp)
    lh = font.size + 8
    tw = max(tmp.textlength(l, font=font) for l in lines)
    bw, bh = int(tw + 64), int(len(lines) * lh + 40)
    tail = 28
    def fn(d, s, im):
        S = lambda *v: [x * s for x in v]
        d.rounded_rectangle(S(4, 16, bw, 16 + bh), radius=26 * s, fill=WHITE, outline=NAVY, width=5 * s)
        if who == "big":
            d.polygon(S(70, 12 + bh, 112, 12 + bh, 60, 16 + bh + tail), fill=WHITE, outline=NAVY, width=5 * s)
            d.line(S(72, 12 + bh, 110, 12 + bh), fill=WHITE, width=8 * s)
        elif who == "lil":
            d.polygon(S(bw - 112, 12 + bh, bw - 70, 12 + bh, bw - 60, 16 + bh + tail), fill=WHITE, outline=NAVY, width=5 * s)
            d.line(S(bw - 110, 12 + bh, bw - 72, 12 + bh), fill=WHITE, width=8 * s)
        tf = FD(19 * s)
        tl = d.textlength(TAGN[who], font=tf) / s + 28
        tx = 36
        d.rounded_rectangle(S(tx, 2, tx + tl, 32), radius=15 * s, fill=TAGC[who], outline=NAVY, width=4 * s)
        d.text(((tx + tl / 2) * s, 17 * s), TAGN[who], font=tf, fill=NAVY if who == "ann" else NAVY, anchor="mm")
        f2 = FB(font.size * s)
        for i, l in enumerate(lines):
            d.text(((bw + 4) / 2 * s, (16 + 22 + i * lh + font.size / 2) * s), l, font=f2, fill=NAVY, anchor="mm")
    spr = aa(bw + 10, bh + 16 + tail + 6, fn)
    _bub_cache[key] = spr
    return spr

# ---------- HUD ----------
_hud_cache = {}
def scoreboard(sb, sl, label):
    key = (sb, sl, label)
    if key in _hud_cache: return _hud_cache[key]
    def fn(d, s, im):
        S = lambda *v: [x * s for x in v]
        d.rounded_rectangle(S(4, 4, 456, 60), radius=28 * s, fill=NAVY, outline=WHITE, width=3 * s)
        f = FD(17 * s); fn_ = FD(32 * s); fs = FD(12 * s)
        for who, x in (("big", 34), ("lil", 426)):
            fsp = face_sprite(who, r=18)
            fsp = fsp.resize((fsp.width * s, fsp.height * s))
            im.alpha_composite(fsp, (x * s - fsp.width // 2, 32 * s - fsp.height // 2))
        d.text((92 * s, 32 * s), "BIG BRO", font=f, fill=WHITE, anchor="mm")
        d.text((368 * s, 32 * s), "LIL BRO", font=f, fill=WHITE, anchor="mm")
        for v, x in ((sb, 175), (sl, 285)):
            d.rounded_rectangle(S(x - 26, 12, x + 26, 52), radius=10 * s, fill=(70, 52, 140))
            d.text((x * s, 32 * s), str(v), font=fn_, fill=WHITE, anchor="mm")
        d.text((230 * s, 25 * s), "VS", font=FD(16 * s), fill=YEL, anchor="mm")
        d.text((230 * s, 44 * s), label, font=fs, fill=(200, 190, 240), anchor="mm")
    spr = aa(460, 64, fn)
    _hud_cache[key] = spr
    return spr

def pill(text, bg=NAVY, fg=WHITE, size=20, pad=22):
    key = ("pill", text, bg, fg, size)
    if key in _hud_cache: return _hud_cache[key]
    f = FD(size); tmp = ImageDraw.Draw(Image.new("RGB", (5, 5)))
    tw = tmp.textlength(text, font=f)
    w_, h_ = int(tw + 2 * pad), size + 26
    def fn(d, s, im):
        d.rounded_rectangle([2 * s, 2 * s, (w_ - 2) * s, (h_ - 2) * s], radius=h_ // 2 * s, fill=bg, outline=WHITE if bg == NAVY else NAVY, width=3 * s)
        d.text((w_ / 2 * s, h_ / 2 * s), text, font=FD(size * s), fill=fg, anchor="mm")
    spr = aa(w_, h_, fn)
    _hud_cache[key] = spr
    return spr

def strip(n, done, icon_fn, current=None):
    key = ("strip", n, done, current, icon_fn.__name__)
    if key in _hud_cache: return _hud_cache[key]
    gap = 72; total = gap * n
    def fn(d, s, im):
        for i in range(n):
            x = (i * gap + gap / 2)
            icon_fn(d, s, x, 40, i, i < done, i == current)
    spr = aa(total, 80, fn)
    _hud_cache[key] = spr
    return spr

def icon_pumpkin(d, s, x, y, i, done, cur):
    S = lambda *v: [q * s for q in v]
    c = (255, 140, 20) if done or cur else (150, 120, 190)
    r = 26 if cur else 22
    d.ellipse(S(x - r, y - r * 0.85, x + r, y + r * 0.85), fill=c, outline=NAVY, width=3 * s)
    d.rectangle(S(x - 3, y - r * 0.85 - 8, x + 3, y - r * 0.85 + 2), fill=(60, 140, 50), outline=NAVY, width=2 * s)
    d.text((x * s, (y + 2) * s), str(i + 1), font=FD(20 * s), fill=WHITE if (done or cur) else NAVY, anchor="mm", stroke_width=2 * s, stroke_fill=NAVY)

def icon_diya(d, s, x, y, i, done, cur):
    S = lambda *v: [q * s for q in v]
    if done or cur:
        d.ellipse(S(x - 9, y - 34, x + 9, y - 6), fill=(255, 200, 40))
        d.ellipse(S(x - 5, y - 26, x + 5, y - 10), fill=(255, 250, 200))
    d.chord(S(x - 28, y - 20, x + 28, y + 26), 0, 180, fill=(210, 110, 40) if (done or cur) else (130, 100, 170), outline=NAVY, width=3 * s)
    d.text((x * s, (y + 12) * s), str(i + 1), font=FD(16 * s), fill=WHITE, anchor="mm", stroke_width=2 * s, stroke_fill=NAVY)

# ---------- scene composition ----------
class Scene:
    def __init__(self, ep):
        self.ep = ep
        self.bg = ((60, 190, 235), (110, 215, 245))
        self.stars = False
        self.poses = {"big": "idle", "lil": "idle"}
        self.cost = {"big": [], "lil": []}
        self.winner = None
        self.prop = None          # fn(img, t) drawing center overlay
        self.hud = None           # fn(img)
        self.strip = None         # fn(img)
        self.show_chars = True
        self.title = None         # (text, color)

    def compose(self, speaker=None, text=None, bounce=0, t=0.0, extra=None):
        im = rays_bg(self.bg[0], self.bg[1], stars=self.stars).copy().convert("RGBA")
        im.alpha_composite(logo(), (14, 6))
        if self.hud: self.hud(im)
        if self.show_chars:
            for who, cx in (("big", 315), ("lil", 965)):
                if self.winner == who:
                    global BURST
                    if BURST is None: BURST = burst()
                    im.alpha_composite(BURST, (cx - 170, 330 - 170 - 60))
                spr = character(who, self.poses[who], self.cost[who])
                dy = -bounce if speaker == who else 0
                # shadow
                sh = Image.new("RGBA", (220, 30), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse([0, 0, 219, 29], fill=(0, 0, 0, 55))
                im.alpha_composite(sh, (cx - 110, 600))
                im.alpha_composite(spr, (cx - 160, 158 + dy))
        if self.prop: self.prop(im, t)
        if extra: extra(im, t)
        if self.strip: self.strip(im)
        if text:
            b = bubble(speaker, text)
            if speaker == "big": pos = (60, 82)
            elif speaker == "lil": pos = (W - 60 - b.width, 82)
            else: pos = ((W - b.width) // 2, 80)
            im.alpha_composite(b, pos)
        if self.title:
            self.title(im, t)
        return im.convert("RGB")

# ---------- audio ----------
VOICES = {"big": ("af_bella", 3, 1.05), "lil": ("af_jessica", 4, 1.08), "ann": ("am_onyx", 0, 0.98)}
_kok = None
def tts(who, text):
    global _kok
    v, st, sp = VOICES[who]
    h = hashlib.md5(f"{who}|{text}".encode()).hexdigest()[:12]
    out = f"{ROOT}/cache/{who}_{h}.wav"
    if os.path.exists(out):
        return sf.read(out)[0].astype(np.float32)
    os.makedirs(f"{ROOT}/cache", exist_ok=True)
    if _kok is None:
        from kokoro_onnx import Kokoro
        _kok = Kokoro(f"/home/claude/tts/kokoro-v1.0.onnx", f"/home/claude/tts/voices-v1.0.bin")
    s, sr = _kok.create(text.replace("Lil Bro", "Lil Bro"), voice=v, speed=sp, lang="en-us")
    raw = f"{ROOT}/cache/raw_{h}.wav"; sf.write(raw, s, sr)
    f = 2 ** (st / 12)
    af = f"asetrate={sr}*{f:.5f},aresample={SR},atempo={1/f:.5f}" if st else f"aresample={SR}"
    if who == "ann":
        af += ",aecho=0.8:0.6:40:0.18"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", af, "-ac", "1", out], check=True)
    os.remove(raw)
    a = sf.read(out)[0].astype(np.float32)
    # trim silence
    nz = np.where(np.abs(a) > 0.01)[0]
    if len(nz): a = a[max(0, nz[0] - 600): nz[-1] + 1200]
    rms = np.sqrt((a ** 2).mean()) + 1e-6
    a = a * (0.11 / rms); a = np.clip(a, -0.95, 0.95)
    sf.write(out, a, SR)
    return a

def env(n, a=0.005, r=0.2):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / max(r, 1e-4))
    return e.astype(np.float32)

def tone(freq, dur, kind="sine", vol=0.3, a=0.005, r=0.25):
    n = int(dur * SR); t = np.arange(n) / SR
    if callable(freq): ph = 2 * np.pi * np.cumsum(freq(t)) / SR
    else: ph = 2 * np.pi * freq * t
    if kind == "sine": w = np.sin(ph)
    elif kind == "square": w = np.sign(np.sin(ph)) * 0.6
    elif kind == "tri": w = 2 / np.pi * np.arcsin(np.sin(ph))
    elif kind == "saw": w = 2 * ((ph / (2 * np.pi)) % 1) - 1
    else: w = np.sin(ph)
    return (w * env(n, a, r) * vol).astype(np.float32)

def noise(dur, vol=0.2, r=0.2, lp=None):
    n = int(dur * SR); x = np.random.RandomState(1).randn(n).astype(np.float32)
    if lp:
        k = int(SR / lp); x = np.convolve(x, np.ones(k) / k, mode="same")
    return x * env(n, 0.002, r) * vol

def cat(*parts):
    return np.concatenate(parts).astype(np.float32)

def sfx(name):
    if name == "ding": return tone(1320, 0.8, "sine", 0.35, r=0.3) + np.pad(tone(1980, 0.8, "sine", 0.15, r=0.25), (0, 0))
    if name == "tada":
        out = np.zeros(int(1.4 * SR), np.float32)
        for i, f in enumerate([523, 659, 784, 1047]):
            s = tone(f, 1.0, "tri", 0.22, r=0.5); st = int(i * 0.09 * SR); out[st:st + len(s)] += s[:len(out) - st]
        return out
    if name == "boing": return tone(lambda t: 200 + 400 * np.abs(np.sin(t * 14)) * np.exp(-t * 3), 0.7, "sine", 0.35, r=0.4)
    if name == "whoosh":
        n = noise(0.6, 0.25, r=0.3, lp=3000); return n * np.sin(np.linspace(0, np.pi, len(n))).astype(np.float32)
    if name == "pop": return tone(lambda t: 900 - 600 * t * 8, 0.12, "sine", 0.4, r=0.05)
    if name == "tick": return tone(2000, 0.05, "square", 0.12, r=0.02)
    if name == "buzz": return tone(140, 0.6, "square", 0.18, r=0.5)
    if name == "drumroll":
        n = int(1.6 * SR); out = np.zeros(n, np.float32)
        for k in range(0, n, int(SR / 22)):
            b = noise(0.05, 0.12 + 0.12 * k / n, r=0.03, lp=2500); out[k:k + len(b)] += b[:n - k]
        return out
    if name == "owl":
        h = tone(lambda t: 420 - 60 * t, 0.45, "sine", 0.3, a=0.05, r=0.3)
        return cat(h, np.zeros(int(0.15 * SR), np.float32), tone(lambda t: 400 - 80 * t, 0.7, "sine", 0.3, a=0.05, r=0.4))
    if name == "door":
        return tone(lambda t: 180 + 120 * np.sin(t * 9) + 60 * np.sin(t * 31), 1.6, "saw", 0.12, a=0.1, r=1.2)
    if name == "thunder":
        return noise(2.0, 0.5, r=0.9, lp=180)
    if name == "ghost":
        return tone(lambda t: 520 + 40 * np.sin(t * 30) - 120 * t, 1.6, "sine", 0.25, a=0.3, r=0.9)
    if name == "knock":
        k = noise(0.08, 0.5, r=0.03, lp=600); g = np.zeros(int(0.18 * SR), np.float32)
        return cat(k, g, k, g, k)
    if name == "cheer":
        n = noise(1.6, 0.18, r=0.9, lp=1800); return n * np.minimum(1, np.linspace(0, 6, len(n))).astype(np.float32)
    if name == "sparkle":
        out = np.zeros(int(1.0 * SR), np.float32)
        for i, f in enumerate([1568, 2093, 2637, 3136, 2637, 3520]):
            s = tone(f, 0.4, "sine", 0.12, r=0.15); st = int(i * 0.07 * SR); out[st:st + len(s)] += s[:len(out) - st]
        return out
    if name == "slide": return tone(lambda t: 300 + 900 * t, 0.5, "sine", 0.25, r=0.4)
    if name == "sneeze":
        return cat(tone(lambda t: 500 + 300 * t, 0.35, "sine", 0.15, a=0.2, r=0.3), noise(0.5, 0.45, r=0.2, lp=4000))
    raise KeyError(name)

def music(total_s, mood="happy", bpm=118):
    rng = random.Random(3 if mood == "happy" else 9)
    beat = 60 / bpm; n = int(total_s * SR) + SR
    out = np.zeros(n, np.float32)
    if mood == "happy":
        prog = [(60, [0, 4, 7]), (67, [0, 4, 7]), (69, [0, 3, 7]), (65, [0, 4, 7])]   # C G Am F
        scale = [0, 2, 4, 7, 9, 12, 14, 16]
    elif mood == "spooky":
        prog = [(57, [0, 3, 7]), (53, [0, 4, 7]), (55, [0, 4, 7]), (52, [0, 4, 7])]   # Am F G E
        scale = [0, 3, 5, 7, 10, 12, 15]
    else:
        prog = [(62, [0, 4, 7]), (67, [0, 4, 7]), (59, [0, 3, 7]), (64, [0, 3, 7])]  # D G Bm Em (festive)
        scale = [0, 2, 4, 7, 9, 12, 14]
    mf = lambda m: 440 * 2 ** ((m - 69) / 12)
    # build an 8-bar motif then loop with variation
    motif = [rng.choice(scale) for _ in range(16)]
    bar = 4 * beat; t = 0.0; bi = 0
    while t < total_s + 2:
        root, tri = prog[bi % 4]
        st = int(t * SR)
        # bass on beats 1 and 3
        for k in (0, 2):
            s = tone(mf(root - 24), beat * 0.9, "tri", 0.16, r=0.3); p = st + int(k * beat * SR); out[p:p + len(s)] += s[:max(0, n - p)]
        # off-beat chord stabs
        for k in (0.5, 1.5, 2.5, 3.5):
            for iv in tri:
                s = tone(mf(root + iv - 12), beat * 0.35, "square" if mood != "spooky" else "tri", 0.035, r=0.08)
                p = st + int(k * beat * SR); out[p:p + len(s)] += s[:max(0, n - p)]
        # melody 8ths
        for k in range(8):
            if rng.random() < 0.25: continue
            m = root + motif[(bi * 8 + k) % 16] + (12 if mood != "spooky" else 0)
            kind = "tri" if mood != "spooky" else "sine"
            s = tone(mf(m), beat * 0.45, kind, 0.06, r=0.12)
            p = st + int(k * beat / 2 * SR); out[p:p + len(s)] += s[:max(0, n - p)]
        # light percussion
        for k in range(4):
            s = noise(0.04, 0.05, r=0.02, lp=6000) if k % 2 else tone(lambda tt: 120 - 300 * tt, 0.12, "sine", 0.18, r=0.08)
            p = st + int(k * beat * SR); out[p:p + len(s)] += s[:max(0, n - p)]
        t += bar; bi += 1
    return out[:int(total_s * SR)]

# ---------- episode builder ----------
class Episode:
    def __init__(self, name, mood="happy"):
        self.name = name; self.mood = mood
        self.frames = []   # (Image or path, dur)
        self.voice = []    # (t, array)
        self.fx = []       # (t, array, gain)
        self.t = 0.0
        self.sc = Scene(self)
        self.fdir = f"{ROOT}/frames_{name}"
        os.makedirs(self.fdir, exist_ok=True)
        self.fi = 0
        self.speech_spans = []

    def _save(self, im, dur):
        p = f"{self.fdir}/{self.fi:06d}.png"; self.fi += 1
        im.save(p, compress_level=1)
        self.frames.append((p, dur)); self.t += dur

    def hold(self, dur, speaker=None, text=None):
        self._save(self.sc.compose(speaker, text), dur)

    def say(self, who, text, pose=None, after=0.35, other_pose=None):
        if pose: self.sc.poses[who] = pose
        if other_pose:
            o = "lil" if who == "big" else "big"; self.sc.poses[o] = other_pose
        a = tts(who, text)
        dur = len(a) / SR + after
        self.voice.append((self.t + 0.05, a))
        self.speech_spans.append((self.t, self.t + len(a) / SR + 0.05))
        if who == "ann":
            self._save(self.sc.compose(who, text), dur)
        else:
            k = 0; step = 0.2; el = 0.0
            while el < dur - 1e-6:
                d = min(step, dur - el)
                self._save(self.sc.compose(who, text, bounce=8 if (k % 2 == 0 and el < dur - after) else 0), d)
                el += d; k += 1
        return dur

    def sfx(self, name, gain=1.0, at=None):
        self.fx.append((self.t if at is None else at, sfx(name), gain))

    def action(self, dur, overlay, sounds=(), speaker=None, text=None):
        """overlay(im, t01, tsec) draws on top; rendered at FPS_ACT."""
        n = max(1, int(round(dur * FPS_ACT)))
        t0 = self.t
        for (at, nm, g) in sounds:
            self.fx.append((t0 + at, sfx(nm), g))
        for i in range(n):
            u = i / max(1, n - 1)
            im = self.sc.compose(speaker, text, extra=lambda img, tt, u=u, i=i: overlay(img, u, i / FPS_ACT))
            self._save(im, 1 / FPS_ACT)

    def title_card(self, big, small=None, color=YEL, dur=2.6, sound="whoosh", bg=None):
        old = (self.sc.show_chars,)
        def ov(im, u, ts):
            k = ease(min(1, ts / 0.45))
            ov_ = Image.new("RGBA", (W, H), (20, 10, 60, int(140 * k)))
            im.alpha_composite(ov_)
            d = ImageDraw.Draw(im)
            y = int(lerp(-120, 330, k))
            text_outline(d, (W // 2, y), big, FD(78), color, ow=7, shadow=6)
            if small:
                text_outline(d, (W // 2, y + 82), small, FD(40), WHITE, ow=5, shadow=4)
        self.action(dur, ov, sounds=[(0, sound, 1.0)])

    def render(self, out_mp4, music_gain=0.32):
        total = self.t
        print(self.name, "duration", round(total, 1), "s", len(self.frames), "frames")
        # concat list
        lst = f"{self.fdir}/list.txt"
        with open(lst, "w") as f:
            for p, d in self.frames:
                f.write(f"file '{p}'\nduration {d:.4f}\n")
            f.write(f"file '{self.frames[-1][0]}'\n")
        # audio
        n = int((total + 1) * SR)
        voice = np.zeros(n, np.float32); fx = np.zeros(n, np.float32)
        for t, a in self.voice:
            p = int(t * SR); voice[p:p + len(a)] += a[:max(0, n - p)]
        for t, a, g in self.fx:
            p = int(t * SR); fx[p:p + len(a)] += (a * g)[:max(0, n - p)]
        m = music(total + 1, self.mood)[:n]
        m = np.pad(m, (0, n - len(m)))
        duck = np.ones(n, np.float32)
        for s0, s1 in self.speech_spans:
            duck[int(s0 * SR):int(s1 * SR)] = 0.45
        k = int(0.15 * SR); duck = np.convolve(duck, np.ones(k) / k, mode="same")
        mixd = voice + fx * 0.9 + m * music_gain * duck
        # fade in/out
        fi = int(0.5 * SR); mixd[:fi] *= np.linspace(0, 1, fi); mixd[-SR:] *= np.linspace(1, 0, SR)
        peak = np.abs(mixd).max(); mixd = mixd / max(1.0, peak / 0.95)
        wav = f"{self.fdir}/audio.wav"; sf.write(wav, mixd[:int(total * SR)], SR)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-i", wav,
                        "-vf", "fps=24,format=yuv420p", "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-tune", "animation",
                        "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                        "-movflags", "+faststart", "-shortest", out_mp4], check=True)
        print("wrote", out_mp4, os.path.getsize(out_mp4) // 1024, "KB")
