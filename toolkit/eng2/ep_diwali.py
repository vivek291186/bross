import sys
from common import *

ep = Episode("diwali", mood="festive")
sc = ep.sc
B, L, H = "big", "lil", "ann"
S = ep.say

NIGHT = ((35, 28, 100), (52, 42, 130))
SAFF = ((255, 140, 30), (255, 175, 70))
MAG = ((205, 45, 140), (230, 85, 170))
GOLD = ((245, 175, 20), (255, 205, 70))
TEAL = ((20, 160, 170), (50, 190, 195))
PURP = ((110, 50, 200), (140, 85, 225))
ROSE = ((240, 90, 110), (255, 125, 140))
GREEN = ((40, 170, 100), (75, 200, 130))

RED_C, YEL_C, BLU_C, WHI_C = (230, 40, 50), (255, 210, 30), (40, 110, 230), (255, 255, 255)
ORA_C, GRN_C, PUR_C, PNK_C, BRN_C = (255, 140, 20), (60, 180, 70), (140, 60, 200), (255, 150, 190), (120, 80, 45)

# ---------- HUD: countdown pill + 8-diya segment strip ----------
ep.seg = 0
def hud(im):
    p = pill("DIWALI IN 18 DAYS!", bg=NAVY, fg=YEL, size=24)
    im.alpha_composite(p, ((W - p.width) // 2, 10))
def stripf(im):
    s_ = strip(8, max(0, ep.seg - 1), icon_diya, current=ep.seg - 1 if ep.seg else None)
    im.alpha_composite(s_, ((W - s_.width) // 2, 630))
sc.hud = hud; sc.strip = stripf

def segment(title, sub, bg, stars=False):
    ep.seg += 1
    sc.bg = bg; sc.stars = stars; sc.winner = None
    sc.poses = {B: "idle", L: "idle"}
    ep.title_card(title, sub, dur=2.4, sound="sparkle")

# ---------- overlays ----------
DPOS = [(500 + (i % 5) * 70, 410 + (i // 5) * 100) for i in range(10)]
def diya_row(shown, lit, labels=True):
    def ov(im, u, ts):
        d = ImageDraw.Draw(im)
        n = shown(u) if callable(shown) else shown
        L_ = lit(u) if callable(lit) else lit
        for i in range(n):
            x, y = DPOS[i]
            if i in L_: glow(im, x, y - 18, 46)
        d = ImageDraw.Draw(im)
        for i in range(n):
            x, y = DPOS[i]
            draw_diya(d, x, y, 26, lit=i in L_, flick=ts + i)
            if labels: text_outline(d, (x, y + 40), str(i + 1), FD(22), WHITE, ow=4)
    return ov

def blob_mix(c1, c2, res, n1, n2, nres):
    def ov(im, u, ts):
        panel(im, (450, 250, 830, 590), fill=(255, 252, 240))
        d = ImageDraw.Draw(im)
        k = ease(min(1, u / 0.6))
        if u < 0.62:
            x1 = lerp(530, 625, k); x2 = lerp(750, 655, k)
            d.ellipse([x1 - 55, 360, x1 + 55, 470], fill=c1, outline=NAVY, width=4)
            d.ellipse([x2 - 55, 360, x2 + 55, 470], fill=c2, outline=NAVY, width=4)
            if u < 0.3:
                d.text((530, 500), n1, font=FD(26), fill=NAVY, anchor="mm")
                d.text((640, 415), "+", font=FD(50), fill=NAVY, anchor="mm")
                d.text((750, 500), n2, font=FD(26), fill=NAVY, anchor="mm")
        else:
            r = 70 + 6 * math.sin(ts * 6)
            d.ellipse([640 - r, 415 - r, 640 + r, 415 + r], fill=res, outline=NAVY, width=5)
            text_outline(d, (640, 530), nres, FD(40), res if res != WHI_C else NAVY, ow=5)
        d.text((640, 290), "COLOUR MIX", font=FD(24), fill=NAVY, anchor="mm")
    return ov

def rangoli(stage, grow=True, cols=None, mirror_half=False):
    """stage 1..7 progressive layers; u animates the newest layer."""
    cols = cols or [RED_C, YEL_C, GRN_C, BLU_C, PUR_C, ORA_C, PNK_C]
    cx, cy = 640, 410
    def layer(d, k, f, mirror_mask=False):
        if k == 1:
            r = 40 * f; d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=cols[0], outline=NAVY, width=3)
        elif k == 2:
            r = 78 * f
            d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], outline=NAVY, fill=None, width=3)
            d.polygon([(cx, cy - r + 6), (cx + r - 6, cy), (cx, cy + r - 6), (cx - r + 6, cy)], outline=cols[1], width=8)
        elif k == 3:
            for a in range(4):
                ang = a * math.pi / 2 + math.pi / 4
                tx, ty = cx + 112 * f * math.cos(ang), cy + 112 * f * math.sin(ang)
                p1 = (cx + 70 * math.cos(ang - 0.5), cy + 70 * math.sin(ang - 0.5))
                p2 = (cx + 70 * math.cos(ang + 0.5), cy + 70 * math.sin(ang + 0.5))
                d.polygon([p1, (tx, ty), p2], fill=cols[2], outline=NAVY, width=3)
        elif k == 4:
            star(d, cx, cy, 34 * f, YEL, outline=NAVY)
        elif k == 5:
            for a in range(8):
                ang = a * math.pi / 4
                px, py = cx + 128 * math.cos(ang), cy + 128 * math.sin(ang)
                r = 22 * f
                d.ellipse([px - r, py - r, px + r, py + r], fill=cols[(a % 3) + 3], outline=NAVY, width=3)
        elif k == 6:
            for a in range(16):
                ang = a * math.pi / 8
                px, py = cx + 160 * math.cos(ang), cy + 160 * math.sin(ang)
                r = 9 * f
                d.ellipse([px - r, py - r, px + r, py + r], fill=WHITE, outline=NAVY, width=2)
    def ov(im, u, ts):
        d = ImageDraw.Draw(im)
        for k in range(1, stage + 1):
            f = ease(min(1, u * 1.4)) if (k == stage and grow) else 1
            if f > 0.02: layer(d, k, f)
        if mirror_half:
            # hide right half with a "paper" sheet that slides away
            cover = int(lerp(170, 0, ease(max(0, (u - 0.4) / 0.5))))
            if cover > 0:
                d.rectangle([cx + 2, cy - 175, cx + 2 + cover, cy + 175], fill=(250, 245, 230), outline=NAVY, width=3)
            d.line([cx, cy - 180, cx, cy + 180], fill=PINK, width=4)
    return ov

def draw_laddoo(d, x, y, r=20):
    d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 160, 30), outline=NAVY, width=3)
    for (dx, dy) in [(-7, -5), (6, -8), (0, 4), (8, 6), (-8, 7)]:
        d.ellipse([x + dx - 2, y + dy - 2, x + dx + 2, y + dy + 2], fill=(220, 110, 10))

def draw_barfi(d, x, y, r=20):
    d.polygon([(x, y - r), (x + r, y), (x, y + r), (x - r, y)], fill=(250, 240, 210), outline=NAVY, width=3)
    d.line([x - 6, y - 4, x + 6, y + 4], fill=(170, 170, 190), width=3)

def draw_jalebi(d, x, y, r=20):
    pts = []
    for i in range(60):
        t = i / 59 * 4 * math.pi; rr = r * t / (4 * math.pi)
        pts.append((x + rr * math.cos(t), y + rr * math.sin(t)))
    d.line(pts, fill=(255, 150, 20), width=6, joint="curve")
    d.line(pts, fill=(255, 190, 60), width=3, joint="curve")

def plate(items, title=None, eaten=0):
    """items: list of draw fns; eaten: how many vanish over u."""
    def ov(im, u, ts):
        panel(im, (450, 260, 830, 580), fill=(255, 250, 235))
        d = ImageDraw.Draw(im)
        d.ellipse([480, 330, 800, 560], fill=(235, 235, 245), outline=NAVY, width=4)
        n = len(items)
        gone = int(eaten * min(1, u * 1.3))
        for i, fn in enumerate(items):
            if i >= n - gone: continue
            col, row = i % 4, i // 4
            fn(d, 560 + col * 54, 400 + row * 58)
        if title: d.text((640, 295), title, font=FD(26), fill=NAVY, anchor="mm")
        if eaten and u > 0.3:
            text_outline(d, (640, 540), f"{n} - {gone} = {n - gone}", FD(34), YEL, ow=5)
    return ov

def lantern(d, x, y, c, r=26):
    d.polygon([(x, y - r * 1.3), (x + r, y), (x, y + r * 1.3), (x - r, y)], fill=c, outline=NAVY, width=3)
    d.line([x, y - r * 1.3 - 18, x, y - r * 1.3], fill=NAVY, width=3)
    for k in (-8, 0, 8):
        d.line([x + k, y + r * 1.3, x + k, y + r * 1.3 + 22], fill=YEL, width=3)

def seq(items, answer_fn, reveal=0.6, title="WHAT COMES NEXT?"):
    """items: list of fn(d,x,y); answer drawn at '?' after reveal."""
    def ov(im, u, ts):
        panel(im, (440, 280, 840, 560), fill=(255, 252, 240))
        d = ImageDraw.Draw(im)
        d.text((640, 312), title, font=FD(24), fill=NAVY, anchor="mm")
        n = len(items) + 1; sp = 340 / n
        for i, fn in enumerate(items):
            fn(d, 470 + sp / 2 + i * sp, 430)
        x = 470 + sp / 2 + (n - 1) * sp
        if u >= reveal:
            answer_fn(d, x, 430)
            d.ellipse([x - 34, 384, x + 34, 476], outline=(80, 200, 100), width=5)
        else:
            d.text((x, 430), "?", font=FD(60), fill=PINK, anchor="mm")
    return ov

# ======================= SCRIPT =======================
intro(ep, "Diwali is Coming!", "Rangoli Colours and Diya Counting")
sc.cost = {B: ["garland"], L: ["garland"]}

# ---------- 1. Welcome ----------
segment("DIWALI IS COMING!", "Let's get ready together", SAFF)
S(B, "Namaste friends! Welcome back to Bro Bros Fun!", pose="wave")
S(L, "Guess what? Diwali is coming! Only eighteen more days!", pose="cheer")
S(B, "Eighteen days? Lil Bro, you have been counting since August.", pose="point_r")
S(L, "Because Diwali is the best! Lights, sweets, new clothes and more sweets!", pose="dance1")
S(B, "You said sweets two times.", pose="shrug")
S(L, "Because sweets are two times important.", pose="point_l")
S(H, "Diwali is the Festival of Lights. Families light little lamps called diyas, make colourful rangoli and share sweets.")
S(B, "Today we are going to get ready for Diwali, and learn some cool things on the way.", pose="idle")
S(L, "We will count diyas, mix colours, find shapes, and do sweet shop maths!", pose="cheer")
S(B, "Watch the diyas at the bottom of the screen. Every time we finish a game, one more diya lights up!", pose="point_r")
S(L, "Eight games, eight diyas. Let's go!", pose="cheer")

# ---------- 2. Count the diyas ----------
segment("COUNT THE DIYAS", "Numbers 1 to 10", NIGHT, stars=True)
S(H, "Game one! Let's count the diyas from one to ten. Count along with the Bro Bros!")
nums = ["One!", "Two!", "Three!", "Four!", "Five!", "Six!", "Seven!", "Eight!", "Nine!", "Ten!"]
for i, w_ in enumerate(nums):
    who = B if i % 2 == 0 else L
    sc.prop = (lambda k: (lambda im, t: diya_row(k, set())(im, 1, t)))(i + 1)
    ep.sfx("pop", 0.6)
    S(who, w_, pose="point_r" if who == B else "point_l", after=0.25)
sc.prop = None
S(L, "Ten diyas! But they're not shining yet. They look sleepy.", pose="shrug")
S(B, "Let's light them! But remember friends, only a grown up lights real diyas. We'll use our imagination!", pose="think")
S(H, "Lighting diyas, with grown up help!")
ep.action(5.0, diya_row(10, lambda u: set(range(int(u * 7.99)))), sounds=[(k * 0.65, "sparkle", 0.5) for k in range(7)])
sc.prop = lambda im, t: diya_row(10, set(range(7)))(im, 1, t)
S(L, "Wait! Only some diyas are shining. How many are lit?", pose="think")
S(B, "Let's count the shining ones. One, two, three, four, five, six, seven. Seven are lit!", pose="point_r")
S(L, "And three are still sleeping. Seven plus three is...", pose="think")
S(B, "Ten! Seven plus three makes ten!", pose="cheer")
ep.action(3.0, lambda im, u, ts: text_outline(ImageDraw.Draw(im), (640, 300), "7 + 3 = 10", FD(64), YEL, ow=7, shadow=5), sounds=[(0, "ding", 1)])
ep.action(3.0, diya_row(10, set(range(10))), sounds=[(0, "sparkle", 0.8), (0.8, "sparkle", 0.6)])
sc.prop = lambda im, t: diya_row(10, set(range(10)))(im, 1, t)
S(L, "Now all ten are glowing! It looks like a tiny city of lights!", pose="cheer")
S(B, "Diwali tip! Never touch a diya flame, and keep diyas away from curtains and clothes.", pose="point_r")
S(L, "And keep them away from Big Bro's hair. It's very fluffy.", pose="point_l")
S(B, "Hey! My hair is perfectly safe.", pose="shrug")
sc.prop = None

# ---------- 3. Colour mixing ----------
segment("COLOUR MIXING MAGIC", "Rangoli colours", MAG)
S(H, "Game two! Rangoli needs lots of colours. But what if we only have red, yellow, blue and white?")
S(B, "Then we mix them! Mixing colours makes new colours. It's like magic, but real.", pose="cheer")
S(L, "First mix! Red and yellow. What do they make?", pose="think")
ep.action(4.5, blob_mix(RED_C, YEL_C, ORA_C, "RED", "YELLOW", "ORANGE!"), sounds=[(2.6, "pop", 0.9), (2.8, "ding", 0.8)])
S(B, "Orange! Like marigold flowers. Marigolds are everywhere at Diwali!", pose="point_r")
S(L, "Next! Blue and yellow!", pose="point_l")
ep.action(4.5, blob_mix(BLU_C, YEL_C, GRN_C, "BLUE", "YELLOW", "GREEN!"), sounds=[(2.6, "pop", 0.9), (2.8, "ding", 0.8)])
S(B, "Green! Like the mango leaves we hang on the door. They're called a toran.", pose="think")
S(L, "Now red and blue!", pose="cheer")
ep.action(4.5, blob_mix(RED_C, BLU_C, PUR_C, "RED", "BLUE", "PURPLE!"), sounds=[(2.6, "pop", 0.9), (2.8, "ding", 0.8)])
S(B, "Purple! My favourite colour for the middle of the rangoli.", pose="cheer")
S(L, "And last one. Red and white!", pose="point_l")
ep.action(4.5, blob_mix(RED_C, WHI_C, PNK_C, "RED", "WHITE", "PINK!"), sounds=[(2.6, "pop", 0.9), (2.8, "ding", 0.8)])
S(B, "Pink! Pink like Lil Bro's shirt.", pose="point_r")
S(L, "Pink is a power colour. Now watch this. I'm going to mix ALL the colours together. Mega colour!", pose="dance1")
S(B, "Lil Bro, wait. I don't think that's a good...", pose="shrug")
ep.action(4.0, blob_mix(PUR_C, ORA_C, BRN_C, "EVERYTHING", "MORE!", "MUD?!"), sounds=[(2.6, "pop", 0.9), (2.9, "buzz", 0.7)])
S(L, "Oh no. It looks like chocolate pudding. Or mud.", pose="shrug")
S(B, "That's what happens when you mix all the colours. They turn brown!", pose="point_r")
S(L, "Okay. New rule. Don't mix everything. Unless you want a mud rangoli.", pose="think")
S(H, "Remember, friends. Red plus yellow is orange. Blue plus yellow is green. Red plus blue is purple. Red plus white is pink!")

# ---------- 4. Shapes in rangoli ----------
segment("SHAPE RANGOLI", "Circle, square, triangle, star", TEAL)
S(H, "Game three! Rangoli is made of shapes. Let's build one, shape by shape. Can you name each shape?")
ep.action(3.0, rangoli(1), sounds=[(0.3, "pop", 0.8)])
sc.prop = lambda im, t: rangoli(1, grow=False)(im, 1, t)
S(L, "A round red shape. Easy! It's a circle!", pose="point_l")
S(B, "Correct! A circle has no corners at all. It just goes round and round.", pose="think")
ep.action(3.0, rangoli(2), sounds=[(0.3, "pop", 0.8)])
sc.prop = lambda im, t: rangoli(2, grow=False)(im, 1, t)
S(B, "Next, a yellow shape with four equal sides. It's a square, standing on its corner!", pose="point_r")
S(L, "A square doing a handstand! That's a diamond square.", pose="cheer")
ep.action(3.0, rangoli(3), sounds=[(0.3, "pop", 0.8)])
sc.prop = lambda im, t: rangoli(3, grow=False)(im, 1, t)
S(L, "Green pointy shapes! How many sides do they have? One, two, three. Triangles!", pose="think")
S(B, "Four triangles, pointing in four directions. Up, down, left and right. Well, kind of sideways.", pose="point_r")
ep.action(3.0, rangoli(4), sounds=[(0.3, "sparkle", 0.8)])
sc.prop = lambda im, t: rangoli(4, grow=False)(im, 1, t)
S(B, "And in the middle, a shining yellow star! How many points does it have?", pose="cheer")
S(L, "One, two, three, four, five! A five pointed star!", pose="point_l")
ep.action(3.0, rangoli(5), sounds=[(0.3, "pop", 0.6), (0.6, "pop", 0.6)])
sc.prop = lambda im, t: rangoli(5, grow=False)(im, 1, t)
S(L, "Now eight little circles go all around, like a necklace!", pose="dance1")
ep.action(3.0, rangoli(6), sounds=[(0.3, "sparkle", 0.8)])
sc.prop = lambda im, t: rangoli(6, grow=False)(im, 1, t)
S(B, "And sixteen white dots on the outside. Our shape rangoli is ready!", pose="cheer")
S(L, "It's beautiful! I want to make one at the front door. A giant one!", pose="cheer")
S(B, "A giant one? You can't even sit still for two minutes.", pose="shrug")
S(L, "I can sit still. I just choose not to.", pose="point_l")
sc.prop = None

# ---------- 5. Symmetry ----------
segment("MIRROR MAGIC", "What is symmetry?", PURP)
S(H, "Game four! Rangoli has a secret. If you fold it in half, both sides match! That's called symmetry.")
S(L, "Sim-met-tree? Is that a tree?", pose="shrug")
S(B, "No, it's not a tree. Symmetry means one side is a mirror of the other side.", pose="think")
S(B, "Look. Here is half a rangoli. What should the other half look like?", pose="point_r")
ep.action(6.0, rangoli(6, grow=False, mirror_half=True), sounds=[(2.6, "whoosh", 0.8), (5.0, "ding", 0.9)])
sc.prop = lambda im, t: rangoli(6, grow=False)(im, 1, t)
S(L, "Exactly the same! Like a mirror! Left side and right side are twins!", pose="cheer")
S(B, "Just like us. We're brothers, but we match.", pose="point_r")
S(L, "We don't match. I'm much more handsome.", pose="shrug")
S(B, "What else has symmetry? A butterfly! Both wings are the same.", pose="think")
S(L, "And a face! Two eyes, two ears, one nose in the middle.", pose="point_l")
S(B, "Let's try a mirror game, friends. Put both hands up. Now wiggle both thumbs at the same time.", pose="cheer", other_pose="cheer")
ep.action(3.0, lambda im, u, ts: label(im, (640, 330), "WIGGLE!", 60, YEL), sounds=[(0, "boing", 0.6), (1, "boing", 0.6), (2, "boing", 0.6)], pre=lambda u, ts: sc.poses.update({B: "cheer" if int(ts * 4) % 2 else "dance1", L: "cheer" if int(ts * 4) % 2 else "dance2"}))
S(L, "I'm a symmetrical wiggle monster!", pose="dance2")
sc.prop = None

# ---------- 6. Sweet shop maths ----------
segment("SWEET SHOP MATHS", "Laddoo, barfi, jalebi", GOLD)
S(H, "Game five! Welcome to the Bro Bros Sweet Shop! Today, our sweets will help us do maths.")
S(L, "Maths with sweets? This is the best school ever!", pose="cheer")
ep.action(3.0, plate([draw_laddoo] * 6, "6 LADDOOS"), sounds=[(0.2, "pop", 0.5), (0.6, "pop", 0.5), (1.0, "pop", 0.5)])
sc.prop = lambda im, t: plate([draw_laddoo] * 6, "6 LADDOOS")(im, 1, t)
S(B, "Here are some round, orange laddoos. Let's count. One, two, three, four, five, six. Six laddoos!", pose="point_r")
S(L, "Laddoos are round like a circle! And yummy like a laddoo.", pose="dance1")
S(B, "Lil Bro, please don't eat any. We need them for the next game.", pose="point_r")
S(L, "Of course. I would never.", pose="shrug")
sc.prop = None
ep.action(4.5, plate([draw_laddoo] * 6, "6 LADDOOS", eaten=2), sounds=[(1.2, "pop", 0.9), (2.4, "pop", 0.9)], pre=lambda u, ts: sc.poses.update({L: "think" if int(ts * 3) % 2 else "point_l"}))
sc.prop = lambda im, t: plate([draw_laddoo] * 6, "6 LADDOOS", eaten=2)(im, 1, t)
S(B, "Wait! Where did two laddoos go? Lil Bro! Is your mouth full?", pose="point_r")
S(L, "Mm hmm. I was checking if they were fresh. They are very fresh.", pose="shrug")
S(B, "Okay friends. We had six laddoos. Lil Bro ate two. Six take away two is...", pose="think")
S(L, "Four! Four laddoos left. Maths is delicious!", pose="cheer")
sc.prop = None
S(H, "Next, the diamond shaped barfi! Big Bro has five barfis. Lil Bro brings three more.")
ep.action(3.5, plate([draw_barfi] * 8, "5 + 3 = ?"), sounds=[(0.3, "pop", 0.5), (1.0, "pop", 0.5), (1.6, "pop", 0.5)])
sc.prop = lambda im, t: plate([draw_barfi] * 8, "5 + 3 = 8")(im, 1, t)
S(B, "Five plus three. Let's count them all. Five, six, seven, eight. Eight barfis!", pose="point_r")
S(L, "Barfi is a diamond shape. Like the square that did a handstand!", pose="point_l")
sc.prop = None
S(H, "And finally, the curly jalebi! What shape is a jalebi?")
ep.action(3.0, plate([draw_jalebi] * 4, "JALEBI"), sounds=[(0.3, "slide", 0.6)])
sc.prop = lambda im, t: plate([draw_jalebi] * 4, "JALEBI")(im, 1, t)
S(L, "It goes round and round and round. It's a spiral!", pose="dance2")
S(B, "Yes! A spiral is a line that curls around and around. Like a snail shell.", pose="think")
S(L, "Or like my brain when I do homework.", pose="shrug")
S(B, "So, friends. Laddoo is a circle. Barfi is a diamond. Jalebi is a spiral. Shapes are everywhere!", pose="cheer")
sc.prop = None

# ---------- 7. Lantern patterns ----------
segment("LANTERN PATTERNS", "What comes next?", ROSE)
S(H, "Game six! At Diwali, people hang big paper lanterns called kandil. Let's play the pattern game!")
S(B, "A pattern is something that repeats again and again. Your job is to guess what comes next!", pose="point_r")
ep.action(4.5, seq([lambda d, x, y: lantern(d, x, y, RED_C), lambda d, x, y: lantern(d, x, y, YEL_C)] * 2, lambda d, x, y: lantern(d, x, y, RED_C), reveal=0.65), sounds=[(2.9, "ding", 0.9)])
S(L, "Red, yellow, red, yellow... red! Next is red!", pose="cheer")
S(B, "Correct! Next pattern. This one is trickier.", pose="think")
st = lambda d, x, y: star(d, x, y, 24, YEL, outline=NAVY)
ci = lambda d, x, y: d.ellipse([x - 20, y - 20, x + 20, y + 20], fill=BLU_C, outline=NAVY, width=3)
ep.action(4.5, seq([st, st, ci, st, st], ci, reveal=0.65), sounds=[(2.9, "ding", 0.9)])
S(L, "Star, star, circle. Star, star... circle!", pose="point_l")
S(B, "Yes! Two stars, then one circle. Two stars, then one circle!", pose="cheer")
S(L, "My turn to make one! Big diya, small diya, big diya, small diya...", pose="think")
big_d = lambda d, x, y: draw_diya(d, x, y + 10, 26, lit=True)
small_d = lambda d, x, y: draw_diya(d, x, y + 10, 15, lit=True)
ep.action(4.5, seq([big_d, small_d, big_d, small_d], big_d, reveal=0.65), sounds=[(2.9, "ding", 0.9)])
S(B, "Big diya! Easy peasy. Okay, last one. Laddoo, laddoo, jalebi, laddoo, laddoo...", pose="point_r")
lad = lambda d, x, y: draw_laddoo(d, x, y, 18); jal = lambda d, x, y: draw_jalebi(d, x, y, 18)
ep.action(4.5, seq([lad, lad, jal, lad, lad], jal, reveal=0.65), sounds=[(2.9, "ding", 0.9)])
S(L, "Jalebi! And now I'm hungry again.", pose="shrug")
S(B, "You're always hungry.", pose="point_r")
S(H, "Fantastic, Bro Bros! You're pattern champions!")

# ---------- 8. Big rangoli + safety + bye ----------
segment("THE BIG RANGOLI", "Let's make it together!", SAFF)
S(H, "The final game! Let's make one big rangoli together, using all our colours and shapes!")
S(B, "Circle in the middle!", pose="point_r")
ep.action(2.2, rangoli(1), sounds=[(0.2, "pop", 0.8)])
S(L, "Square doing a handstand!", pose="cheer")
ep.action(2.2, rangoli(2), sounds=[(0.2, "pop", 0.8)])
S(B, "Four green triangles!", pose="point_r")
ep.action(2.2, rangoli(3), sounds=[(0.2, "pop", 0.8)])
S(L, "Shining star!", pose="cheer")
ep.action(2.2, rangoli(4), sounds=[(0.2, "sparkle", 0.8)])
S(B, "Eight colourful circles!", pose="point_r")
ep.action(2.2, rangoli(5), sounds=[(0.2, "pop", 0.8)])
S(L, "And sixteen little dots! Done!", pose="cheer")
ep.action(2.6, rangoli(6), sounds=[(0.2, "sparkle", 0.9), (0.9, "tada", 0.8)])
sc.prop = lambda im, t: rangoli(6, grow=False)(im, 1, t)
S(B, "It's perfect! Our best rangoli ever!", pose="cheer")
S(L, "Wait. My nose is tickly. All this colour powder. Ah... ah... ah...", pose="think")
S(B, "No, no, no! Lil Bro, don't sneeze on the rangoli!", pose="shrug")
def sneeze_ov(im, u, ts):
    d = ImageDraw.Draw(im)
    rnd = random.Random(int(ts * 5))
    if u > 0.45:
        for _ in range(int(140 * min(1, (u - 0.45) * 3))):
            x = rnd.uniform(470, 1100); y = rnd.uniform(180, 600)
            c = rnd.choice([RED_C, YEL_C, GRN_C, BLU_C, PUR_C, PNK_C, ORA_C]); r = rnd.uniform(3, 9)
            d.ellipse([x - r, y - r, x + r, y + r], fill=c)
        label(im, (640, 300), "ACHOOO!", 70, YEL)
ep.action(4.0, sneeze_ov, sounds=[(0.3, "sneeze", 1.2)], pre=lambda u, ts: sc.poses.update({L: "cheer" if u > 0.45 else "think"}))
sc.prop = None
S(L, "Oops. Now it's a colour explosion rangoli. Very modern.", pose="shrug")
S(B, "Ha ha! It actually looks more like Diwali fireworks now. Silent fireworks!", pose="cheer")
S(L, "See? I'm an artist. A sneezing artist.", pose="dance1")
sc.bg = TEAL
S(H, "Before we go, here are the Bro Bros Diwali safety tips!")
S(B, "One. Only grown ups light diyas, candles and sparklers.", pose="point_r")
S(L, "Two. Keep a bucket of water nearby, just in case.", pose="point_l")
S(B, "Three. Wear cotton clothes near diyas, not floppy silky ones.", pose="think")
S(L, "Four. Loud crackers scare dogs, cats and birds. Let's keep our pet friends calm and happy.", pose="shrug")
S(B, "Five. The best part of Diwali is sharing. Share sweets with your neighbours and friends!", pose="cheer")
S(L, "And share them with your little brother. Very important.", pose="point_l")
S(H, "Wonderful! Now, let's count down to Diwali together! Eighteen days to go!")
S(B, "Thank you for playing with us, friends! Ask a grown up to subscribe to Bro Bros Fun!", pose="wave")
S(L, "Tomorrow we have a brand new battle. See you there!", pose="wave")
S(B, "Happy almost Diwali!", pose="cheer", other_pose="cheer")
S(L, "Shubh Deepavali! Bye bye!", pose="cheer")
ep.seg = 9
ep.action(4.0, lambda im, u, ts: (confetti(im, ts, seed=5), label(im, (640, 380), "SEE YOU TOMORROW!", 56, YEL)), sounds=[(0, "tada", 0.9)])

if __name__ == "__main__":
    print("timeline seconds:", round(ep.t, 1))
    if len(sys.argv) > 1 and sys.argv[1] == "render":
        ep.render(f"{ROOT}/out/Bro Bros Fun - Diwali Rangoli Colours and Diya Counting.mp4")
