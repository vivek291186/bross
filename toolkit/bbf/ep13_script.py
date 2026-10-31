"""Episode 13: THE ZOO TRIP with Grandpa and Zoomy (new zoo set, origin x=3100)."""
import json, numpy as np, soundfile as sf, os, sys
sys.path.insert(0, "/home/claude/bbf")
from engine import tts, sfx, music, tone, noise, SR, VOICES

VOICES.update({"vanu": ("af_heart", 2, 1.0), "aarav": ("am_puck", 4, 1.05), "vihaan": ("af_jessica", 4, 1.08),
               "himank": ("am_echo", 5, 1.05), "buddy": ("af_kore", 3, 1.08),
               "mummy": ("af_nicole", 0, 1.0), "papa": ("am_adam", -1, 0.98), "zoomy": ("am_michael", 3, 1.15), "grandpa": ("am_adam", -3, 0.92)})
OUT = "/mnt/user-data/outputs/ep13"; os.makedirs(OUT, exist_ok=True)
T = 0.0; ev = []; shots = []; voice = []; fx = []; scenes = []; moods = []
ALL = ["vanu", "aarav", "vihaan", "himank", "buddy"]
OFF = ("mummy", "papa", "zoomy", "grandpa")
TALK = ["Talk with Right Hand Open", "Talk Passionately", "Talk with Left Hand on Hip", "Agree Gesture"]
_tk = {}
def scene(name, set_, cast, light="day", mood="happy"):
    if scenes: scenes[-1]["t1"] = round(T, 3)
    scenes.append({"name": name, "set": set_, "t0": round(T, 3), "cast": cast, "light": light}); moods.append((T, mood))
def mood(m): moods.append((T, m))
def shot(s): shots.append((round(T, 3), s))
def robot(a):
    t = np.arange(len(a)) / SR
    y = a * (0.55 + 0.45 * np.sin(2 * np.pi * 55 * t))
    y = np.round(y * 24) / 24
    return (y / (np.abs(y).max() + 1e-6) * 0.8).astype(np.float32)
def say(who, text, clip=None, cam=None, gap=0.3, look=None, emote=None):
    global T
    if cam: shot(cam)
    a = tts(who, text)
    if who == "zoomy": a = robot(a)
    d = len(a) / SR
    voice.append((T + 0.05, a))
    if who in OFF:
        ev.append({"t": round(T, 3), "type": "say", "who": who, "whos": [who], "text": text, "dur": round(d, 3), "clip": "-"})
    else:
        if clip is None:
            i = _tk.get(who, 0); clip = TALK[i % 2] if who != "vanu" else TALK[(i % 2) + 1 if i % 3 else 0]; _tk[who] = i + 1
        ev.append({"t": round(T, 3), "type": "say", "who": who, "text": text, "dur": round(d, 3), "clip": clip, "look": look, "emote": emote})
    T += d + gap
def chorus(whos, text, clip="Cheer with Both Hands", cam=None, gap=0.3):
    global T
    if cam: shot(cam)
    parts = [tts(k, text) for k in whos]; n = max(len(p) for p in parts)
    a = sum(np.pad(p, (0, n - len(p))) for p in parts) * (0.9 / len(parts) ** 0.5)
    voice.append((T + 0.05, a))
    ev.append({"t": round(T, 3), "type": "say", "who": "+".join(whos), "whos": whos, "text": text, "dur": round(n / SR, 3), "clip": clip})
    T += n / SR + gap
def do(who, clip, dur, block=False, sounds=(), cam=None):
    global T
    if cam: shot(cam)
    ev.append({"t": round(T, 3), "type": "clip", "who": who, "clip": clip, "dur": dur})
    for at, s, g in sounds: fx.append((T + at, s, g))
    if block: T += dur
def move(who, to, dur, clip="Running", at=None):
    t0 = T if at is None else at
    ev.append({"t": round(t0, 3), "type": "move", "who": who, "to": to, "dur": dur, "clip": clip})
    fx.append((t0, steps(dur, 7 if "Run" in clip or "Sprint" in clip else 3.6), 0.45))
def prop(name, action, sounds=(), **kw):
    e = {"t": round(T, 3), "type": "prop", "name": name, "action": action}; e.update(kw); ev.append(e)
    for at, s, g in sounds: fx.append((T + at, s, g))
def card(name, dur, sounds=(), cam=None, **kw):
    global T
    if cam: shot(cam)
    e = {"t": round(T, 3), "type": "card", "name": name, "dur": dur}; e.update(kw); ev.append(e)
    for at, s, g in sounds: fx.append((T + at, s, g))
    T += dur
def wait(d):
    global T; T += d

# ---------- SFX ----------
def cat_(*xs): return np.concatenate(xs).astype(np.float32)
def silence(d): return np.zeros(int(d * SR), np.float32)
def steps(d, rate):
    out = np.zeros(int(d * SR) + 10, np.float32)
    for k in range(int(d * rate)):
        p = int(k / rate * SR); s = tone(lambda t: 150 - 200 * t, 0.06, "sine", 0.12, r=0.03); out[p:p + len(s)] += s[:len(out) - p]
    return out
whoosh = lambda: sfx("whoosh"); boing = lambda: sfx("boing"); pop = lambda: sfx("pop"); ding = lambda: sfx("ding"); tada = lambda: sfx("tada")
cheer = lambda: sfx("cheer") if False else sfx("tada"); drumroll = lambda: sfx("drumroll")
def vac(d=2.0, turbo=False):
    n = int(d * SR); t = np.arange(n) / SR
    f = (220 if not turbo else 330) + 25 * np.sin(2 * np.pi * 3 * t)
    hum = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.18 + noise(d, 0.5, r=0.1, lp=2500 if not turbo else 5000)[:n] * 0.5
    env = np.minimum(1, t / 0.15) * np.minimum(1, (d - t) / 0.2)
    return (hum * env * (0.6 if not turbo else 0.85)).astype(np.float32)
def beepboop():
    return cat_(tone(880, 0.08, "square", 0.2, r=0.02), silence(0.04), tone(660, 0.08, "square", 0.2, r=0.02), silence(0.04), tone(1175, 0.12, "square", 0.2, r=0.04))
def slip(): return cat_(tone(lambda t: 1200 - 900 * t / 0.3, 0.3, "sine", 0.3, r=0.05), noise(0.2, 0.7, r=0.15, lp=1500))
def thud(): return (noise(0.35, 1.0, r=0.3, lp=220) * 0.9).astype(np.float32)
def squelch():
    n = int(0.5 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * np.cumsum(180 + 260 * np.sin(t * 18)) / SR) * 0.35 * np.exp(-t * 4) + noise(0.5, 0.6, r=0.3, lp=900)[:n] * 0.6).astype(np.float32)
def splash(): return cat_(noise(0.05, 1.0, r=0.02, lp=9000), noise(0.9, 0.7, r=0.7, lp=6000))
def spray(d=4.0):
    n = int(d * SR); t = np.arange(n) / SR
    hiss = noise(d, 0.35, r=0.3, lp=7000)[:n]; tick = (np.sin(2 * np.pi * 5 * t) > 0.92).astype(np.float32) * noise(d, 0.6, r=0.0, lp=3000)[:n]
    env = np.minimum(1, t / 0.2) * np.minimum(1, (d - t) / 0.3)
    return ((hiss * 0.6 + tick * 0.5) * env).astype(np.float32)
def birds(d=3.0):
    out = np.zeros(int(d * SR), np.float32); rng = np.random.RandomState(4)
    for k in range(int(d * 2.5)):
        p = int(rng.uniform(0, d - 0.3) * SR); f0 = rng.uniform(2400, 3600)
        s = tone(lambda t, f0=f0: f0 + 900 * np.sin(t * 60), 0.12, "sine", 0.08, r=0.05); out[p:p + len(s)] += s[:len(out) - p]
    return out
def pullstrain(): return tone(lambda t: 300 + 200 * t, 1.4, "saw", 0.06, a=0.1, r=0.2)
def popout(): return cat_(tone(lambda t: 500 - 300 * t / 0.12, 0.12, "sine", 0.6, r=0.05), noise(0.15, 0.5, r=0.1, lp=3000))
def ticktock(n=5):
    out = []
    for i in range(n): out += [tone(1200 if i % 2 else 900, 0.05, "square", 0.18, r=0.03), silence(0.45)]
    return cat_(*out)
def scream(): return tone(lambda t: 900 + 250 * np.sin(t * 30), 0.9, "saw", 0.10, a=0.02, r=0.3)
def ahoy(): return cat_(tone(392, 0.25, "tri", 0.25, r=0.1), tone(523, 0.25, "tri", 0.25, r=0.1), tone(659, 0.45, "tri", 0.25, r=0.3))


def trumpet(): return cat_(tone(lambda t: 220 + 500 * t, 0.5, "saw", 0.14, a=0.03, r=0.1), tone(lambda t: 700 - 150 * t, 0.6, "saw", 0.12, r=0.3))
def oohaah(n=4): return cat_(*[cat_(tone(lambda t: 500 + 400 * np.sin(t * 25), 0.18, "tri", 0.15, r=0.05), silence(0.08)) for _ in range(n)])
def munch(): return cat_(*[cat_(noise(0.06, 1.0, r=0.04, lp=2500), silence(0.12)) for _ in range(4)])
def squawk(n=3): return cat_(*[cat_(tone(lambda t: 900 - 300 * t / 0.15, 0.15, "saw", 0.1, r=0.05), silence(0.12)) for _ in range(n)])
def spray2(d=1.5): return (noise(d, 0.9, r=0.3, lp=7000) * 0.8).astype(np.float32)
def sparkle(): return cat_(*[tone(1800 + 300 * i, 0.08, "sine", 0.15, r=0.06) for i in range(5)])
KIDS4 = ["vanu", "aarav", "vihaan", "himank"]

# ================= COLD OPEN: Zoomy arrives at the zoo =================
scene("cold", "zoo", {"vanu": [-3.0, -4.6, 0, "Idle"], "aarav": [-2.4, -4.9, 0, "Idle"], "vihaan": [-3.6, -4.9, 0, "Idle"],
                      "himank": [-2.0, -4.6, 0, "Idle"], "buddy": [-4.0, -4.6, 0, "Idle"]}, mood="happy")
prop("zoomy", "place", at=[-3.0, -4.2])
shot("insert:arch"); wait(0.3)
move("vanu", [-1.0, -1.6], 2.4, clip="Run Fast"); move("aarav", [-0.2, -1.9], 2.6, clip="Run Fast"); move("vihaan", [-1.8, -2.0], 2.5, clip="Run Fast")
move("himank", [0.6, -1.7], 2.7, clip="Run Fast"); move("buddy", [-2.6, -2.2], 3.0, clip="Running")
chorus(ALL, "The BRO BROS ZOO!", clip="Run Fast", gap=0.6)
prop("zoomy", "path", pts=[[-3.0, -4.2], [-2.2, -2.8], [-1.4, -2.6]], dur=1.8)
shot("zoo_wide"); wait(2.0)
fx.append((T, beepboop(), 0.7)); prop("zoomy", "eyes", color="red")
say("zoomy", "Scanning. Fur. Feathers. Hay. And... elephant poop. DANGER LEVEL: MAXIMUM.", cam="insert:zoomy")
say("grandpa", "Ho ho! Don't worry, little robot. Grandpa will show you all the animals!", cam="zoo_wide")
card("intro", 3.0, sounds=[(0.2, tada(), 0.8)], cam="high_wide")

# ================= GIRAFFE =================
scene("giraffe", "zoo", {"vihaan": [-2.4, 0.8, 180 - 160, "Idle"], "himank": [-1.6, 0.6, 10, "Idle"], "vanu": [-0.8, 0.3, 10, "Idle"],
                         "aarav": [-3.2, 0.4, 0, "Idle"], "buddy": [0.0, 0.1, 0, "Idle"]}, mood="happy")
prop("zoomy", "place", at=[-0.6, -0.6]); prop("zoomy", "eyes", color="blue")
shot("insert:giraffe"); wait(0.6)
say("grandpa", "This is the giraffe. Giraffes are the tallest animals in the whole world!", cam="insert:giraffe")
say("himank", "Taller than ME? Impossible. I'm the tallest Bro Bro!", clip="Show Both Arm Muscles", cam="close:himank", emote="brows")
do("himank", "Regular Jump", 2.0, cam="close:himank"); wait(1.8)
prop("giraffe", "bend", to="vihaan", dur=2.0, sounds=[(1.6, munch(), 0.8)])
say("vihaan", "Ooh, she's coming down to say hello...", clip="Big Wave Hello", cam="close:vihaan", emote="brows")
wait(1.0)
do("vihaan", "Slap Reaction", 2.2, cam="insert:giraffe"); wait(1.0)
say("vihaan", "HEY! My hair is NOT a leaf!", clip="Angry Ground Stomp", cam="close:vihaan", emote="brows")
prop("giraffe", "up", dur=1.5)
chorus(["vanu", "aarav", "himank", "buddy"], "Ha ha ha ha!", clip="Victory Cheer", cam="zoo_wide")

# ================= ELEPHANT =================
scene("elephant", "zoo", {"aarav": [0.4, 0.9, 10, "Idle"], "vanu": [-0.6, 0.8, 0, "Idle"], "vihaan": [1.4, 0.7, -10, "Idle"],
                          "himank": [-1.4, 0.5, 10, "Idle"], "buddy": [2.2, 0.4, -20, "Idle"]}, mood="plan")
prop("zoomy", "place", at=[0.9, 1.2])
shot("insert:elephant"); fx.append((T, trumpet(), 0.9)); wait(1.4)
say("grandpa", "And this is the elephant. Look at her long trunk. She uses it like a hose!", cam="insert:elephant")
fx.append((T, beepboop(), 0.7)); prop("zoomy", "eyes", color="green")
say("zoomy", "Beep! A big grey vacuum! Hello, sister! Let us clean the zoo together!", cam="insert:zoomy")
prop("trunk", "aim", sounds=[(0.0, trumpet(), 0.8)]); wait(1.0)
prop("spray", "on", to="zoomy", dur=1.6, sounds=[(0.0, spray2(1.6), 0.9)])
shot("insert:elephant"); wait(1.8)
prop("zoomy", "eyes", color="orange"); prop("zoomy", "spin", dur=1.6)
say("zoomy", "Beep. Blub. Blub. I am... very... clean. Too clean.", cam="insert:zoomy")
say("aarav", "Ha! The elephant gave Zoomy a bath!", clip="Talk Passionately", cam="close:aarav", emote="brows")
prop("spray", "on", to="aarav", dur=1.2, sounds=[(0.0, spray2(1.2), 0.9)])
do("aarav", "Slap Reaction", 2.0, cam="close:aarav"); wait(1.6)
say("aarav", "...and me. Thank you, elephant.", clip="Shrug", cam="close:aarav", emote="brows")
chorus(["vanu", "vihaan", "himank", "buddy"], "Ha ha ha ha!", clip="Victory Cheer", cam="zoo_wide")
prop("trunk", "rest")

# ================= MONKEYS steal the ice cream =================
scene("monkeys", "zoo", {"buddy": [1.6, -0.2, -40, "Idle"], "vanu": [0.4, -0.6, -10, "Idle"], "himank": [-0.4, -0.8, 0, "Idle"],
                         "aarav": [2.6, -0.9, -60, "Idle"], "vihaan": [-1.2, -0.6, 10, "Idle"]}, mood="chase")
prop("zoomy", "place", at=[-0.8, -1.6]); prop("zoomy", "eyes", color="blue")
shot("insert:cart"); fx.append((T, ding(), 0.6)); wait(0.6)
say("buddy", "Grandpa! Can I have an ice cream? A BIG one?", clip="Big Heart Gesture", cam="close:buddy", emote="brows")
say("grandpa", "One big strawberry ice cream for Buddy!")
prop("icecream", "give", who="buddy", sounds=[(0.0, sparkle(), 0.6)])
say("buddy", "Mmm. The best ice cream in the whole wide...", clip="Happy Sway Standing", cam="close:buddy", emote="brows")
fx.append((T, oohaah(5), 0.9))
prop("monkey", "steal", who="buddy", dur=2.6, sounds=[(0.0, whoosh(), 0.6)])
shot("insert:monkeys"); wait(2.8)
say("buddy", "HEY! Mister Monkey! That's MY ice cream!", clip="Angry Ground Stomp", cam="close:buddy", emote="brows")
fx.append((T, oohaah(6), 0.8)); prop("monkey", "lick")
shot("insert:monkeys"); wait(2.0)
say("grandpa", "Ho ho! Monkeys LOVE treats, Buddy. Next time, hold it tight!")
say("vanu", "Here, Buddy. We can share mine. Sharing is caring!", clip="Big Heart Gesture", cam="close:vanu", emote="brows")
say("buddy", "Thank you, Vanu! ...Can I have the biggest half?", clip="Scheming Hand Rub", cam="close:buddy", emote="brows")
chorus(["vanu", "aarav", "vihaan", "himank"], "BUDDY!", clip="Slap Reaction", cam="zoo_wide")

# ================= PENGUIN PARADE =================
scene("penguins", "zoo", {"vanu": [0.2, -2.4, -20, "Idle"], "aarav": [-0.6, -2.7, -10, "Idle"], "vihaan": [1.0, -2.8, -30, "Idle"],
                          "himank": [-1.4, -2.5, 0, "Idle"], "buddy": [-2.2, -2.2, 10, "Idle"]}, mood="happy")
prop("zoomy", "place", at=[0.9, -1.4])
shot("insert:penguins"); fx.append((T, squawk(4), 0.8)); wait(1.2)
say("grandpa", "And here are the penguins! They walk like this... waddle, waddle!", cam="insert:penguins")
for k in ALL: do(k, "Penguin Walk", 4.0)
shot("zoo_wide"); fx.append((T, squawk(5), 0.7)); wait(3.6)
fx.append((T, beepboop(), 0.7)); prop("zoomy", "eyes", color="rainbow")
say("zoomy", "Beep. Penguins. Follow me. I am... the PENGUIN KING.", cam="insert:zoomy")
prop("zoomy", "path", pts=[[0.9, -1.4], [0.0, -1.2], [-1.4, -1.5], [-2.2, -2.4]], dur=4.0)
prop("penguins", "follow", dur=4.0, sounds=[(0.0, squawk(6), 0.7), (2.0, squawk(5), 0.6)])
shot("zoo_wide"); wait(4.2)
chorus(ALL, "PENGUIN PARADE!", clip="Penguin Walk", cam="zoo_wide")
for k in ALL: do(k, "Penguin Walk", 3.0)
wait(2.0)

# ================= ENDING =================
scene("ending", "zoo", {"vanu": [-1.4, -1.0, 10, "Idle"], "aarav": [-0.6, -1.2, 5, "Idle"], "vihaan": [0.2, -1.2, 0, "Idle"],
                        "himank": [1.0, -1.0, -5, "Idle"], "buddy": [1.8, -1.2, -15, "Idle"]}, mood="happy")
prop("zoomy", "place", at=[0.2, -2.3]); prop("penguins", "home")
say("grandpa", "What a day! So, Bro Bros... which animal was your favourite?", cam="zoo_wide")
say("vihaan", "The giraffe! Even if she tried to eat my hair.", clip="Talk with Right Hand Open", cam="close:vihaan", emote="brows")
say("buddy", "The monkey! He has very good taste in ice cream.", clip="Shrug", cam="close:buddy", emote="brows")
say("zoomy", "The elephant. Free shower. Five stars. Beep.", cam="insert:zoomy")
chorus(ALL, "Thank you, Grandpa!", clip="Cheer with Both Hands Up", cam="zoo_wide")
mood("mystery")
say("grandpa", "And guess what? Tomorrow is a very special day... BUDDY'S BIRTHDAY!")
say("buddy", "A birthday party? With CAKE?!", clip="Jump with Arms Open", cam="close:buddy", emote="brows")
fx.append((T, beepboop(), 0.7)); prop("zoomy", "eyes", color="red")
say("zoomy", "Cake. Crumbs. Balloons. Confetti. Oh no... OH NO.", cam="insert:zoomy")
chorus(ALL, "Ha ha ha ha!", clip="Victory Cheer", cam="zoo_wide")
say("vanu", "See you at Buddy's party! Ask a grown up to subscribe to Bro Bros Fun!", clip="Big Wave Hello", cam="close:vanu", emote="brows")
for k in ("aarav", "vihaan", "himank", "buddy"): do(k, "Big Wave Hello", 3.0)
wait(0.4)
card("endcard", 6.0, sounds=[(0.2, tada(), 0.7)])
scenes[-1]["t1"] = round(T, 3)
TOTAL = T
print("TOTAL", round(TOTAL, 1), "events", len(ev), "shots", len(shots))

# ---------- mix ----------
n = int((TOTAL + 1) * SR); mixv = np.zeros(n, np.float32); mixf = np.zeros(n, np.float32)
for t0, a in voice:
    p = int(t0 * SR); mixv[p:p + len(a)] += a[:n - p]
for t0, a, g in fx:
    p = int(max(0, t0) * SR); mixf[p:p + len(a)] += (a * g)[:n - p]
mus = np.zeros(n, np.float32)
MM = {"chase": ("happy", 150), "happy": ("happy", 126), "plan": ("happy", 132), "mystery": ("spooky", 100)}
segs = moods + [(TOTAL, None)]
for (t0, m), (t1, _) in zip(segs, segs[1:]):
    if t1 - t0 < 0.5: continue
    mm_, bpm_ = MM.get(m, ("happy", 126))
    try: mm = music(t1 - t0 + 0.5, mm_, bpm=bpm_)
    except Exception: mm = music(t1 - t0 + 0.5, "happy", bpm=bpm_)
    p = int(t0 * SR); L_ = min(len(mm), n - p); mus[p:p + L_] += mm[:L_]
envv = np.convolve(np.abs(mixv), np.ones(4800) / 4800, mode="same")
envf = np.convolve(np.abs(mixf), np.ones(4800) / 4800, mode="same")
duck = 1 - 0.6 * np.clip(envv / 0.03, 0, 1) - 0.25 * np.clip(envf / 0.05, 0, 1)
out = mixv * 1.0 + mixf * 0.9 + mus * 0.28 * np.clip(duck, 0.15, 1)
out = out / max(1e-6, np.abs(out).max()) * 0.92
sf.write(f"{OUT}/audio.wav", out, SR); sf.write(f"{OUT}/voice.wav", mixv, SR)
json.dump({"total": TOTAL, "scenes": scenes, "events": ev, "shots": shots}, open(f"{OUT}/timeline.json", "w"), indent=1)
