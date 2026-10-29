"""Episode 9: WHERE'S ZOOMY? Backyard hide & seek comedy (follows the Ep 8 cliffhanger). New BACKYARD GARDEN set (origin x=1700).
Beats: cold open - the walking bucket; stakes - Papa's Big Garden Contest + prize pumpkin; search montage (penguin disguise,
interrogating the gnome); the 'very personal sprinkler'; MUD MODE + Himank's mud dive; the prize carrot pull that flies into
the pool; Operation Pool Trap (bucket brigade + Buddy the bait AGAIN); BOAT MODE; Zoomy blames Himank; Sports Day teaser.
Builds timeline.json + audio.wav + voice.wav for build8 + props_ep9."""
import json, numpy as np, soundfile as sf, os, sys
sys.path.insert(0, "/home/claude/bbf")
from engine import tts, sfx, music, tone, noise, SR, VOICES

VOICES.update({"vanu": ("af_heart", 2, 1.0), "aarav": ("am_puck", 4, 1.05), "vihaan": ("af_jessica", 4, 1.08),
               "himank": ("am_echo", 5, 1.05), "buddy": ("af_kore", 3, 1.08),
               "mummy": ("af_nicole", 0, 1.0), "papa": ("am_adam", -1, 0.98), "zoomy": ("am_michael", 3, 1.15)})
OUT = "/mnt/user-data/outputs/ep09"; os.makedirs(OUT, exist_ok=True)
T = 0.0; ev = []; shots = []; voice = []; fx = []; scenes = []; moods = []
ALL = ["vanu", "aarav", "vihaan", "himank", "buddy"]
OFF = ("mummy", "papa", "zoomy")
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

L = lambda x, y: [x, y]   # garden coordinates relative to origin
CAST0 = {"vanu": [-0.3, -0.6, 0, "Idle"], "aarav": [-1.3, -0.2, 10, "Idle"], "vihaan": [0.7, -1.0, -10, "Idle"],
         "himank": [-2.3, -0.9, 20, "Idle"], "buddy": [1.9, -1.4, -20, "Idle"]}

# ================= COLD OPEN: the walking bucket =================
scene("cold", "garden", CAST0, mood="mystery")
prop("zoomy", "place", at=[0.3, 0.5]); prop("bucket", "cover")
shot("garden_wide"); fx.append((T, birds(3.0), 0.5)); wait(1.2)
do("himank", "Sneaky Walk", 3.0); move("himank", L(-0.9, -0.2), 3.0, clip="Sneaky Walk")
do("aarav", "Sneaky Walk", 3.0); move("aarav", L(-0.3, 0.0), 2.6, clip="Sneaky Walk")
say("himank", "Shhh. Did that bucket just... move?", clip="Sneaky Walk", cam="close:himank", emote="brows")
prop("zoomy", "path", pts=[[0.3, 0.5], [0.55, 0.45]], dur=0.6, sounds=[(0.0, vac(0.6), 0.4)])
shot("insert:zoomy"); wait(1.0)
say("aarav", "Buckets don't move, Himank. Buckets are lazy.", clip="Shrug", cam="close:aarav", emote="brows")
prop("zoomy", "path", pts=[[0.55, 0.45], [-0.2, -0.4], [-1.4, -0.9], [-2.4, -0.2], [-1.0, 0.9], [0.6, 1.3]], dur=2.6, turbo=True, sounds=[(0.0, vac(2.6, True), 0.7)])
fx.append((T + 0.1, scream(), 0.5))
do("himank", "Jump Over Obstacle", 2.2, sounds=[(0.4, boing(), 0.5)]); do("aarav", "Fall Down", 2.4, sounds=[(0.3, slip(), 0.7), (0.8, thud(), 0.8)])
shot("low_wide"); wait(2.0)
prop("bucket", "off", sounds=[(0.0, popout(), 0.7)])
shot("insert:zoomy"); wait(0.8)
say("zoomy", "Beep boop. Peekaboo.", gap=0.2)
chorus(ALL, "ZOOMY!", clip="Slap Reaction", cam="garden_wide", gap=0.1)
prop("zoomy", "path", pts=[[0.6, 1.3], [2.6, 3.4], [4.6, 3.8]], dur=1.6, turbo=True, sounds=[(0.0, vac(1.6, True), 0.6)])
wait(1.0)
card("intro", 3.0, sounds=[(0.2, tada(), 0.8)], cam="high_wide")

# ================= SETUP: the stakes =================
scene("setup", "garden", {"vanu": [-0.3, -0.6, 0, "Idle"], "aarav": [-1.3, -0.3, 10, "Idle"], "vihaan": [0.7, -1.0, -10, "Idle"],
                          "himank": [-2.2, -0.9, 20, "Idle"], "buddy": [1.6, -1.3, -20, "Idle"]}, mood="happy")
prop("zoomy", "place", at=[6.5, 3.0]); prop("bucket", "hide")
shot("insert:veg"); fx.append((T, birds(4.0), 0.4)); wait(0.8)
say("mummy", "Bro Bros! Papa's Big Garden Contest starts at five o'clock! Find Zoomy fast... and keep him far, FAR away from Papa's prize pumpkin!")
chorus(ALL, "Okay, Mummy!", clip="Agree Gesture", cam="garden_wide", gap=0.1)
say("vanu", "Team Zoomy Hunt! Everybody spread out. Search every leaf, every bush, every flower!", clip="Motivational Cheer", cam="close:vanu", emote="brows")
mood("plan")
# search montage
move("vihaan", L(-2.0, 1.2), 2.4, clip="Crawl and Look Back"); do("vihaan", "Crawl and Look Back", 3.2, cam="low_wide"); wait(2.6)
say("vihaan", "Not under here. Just one very surprised snail.", clip="Shrug", cam="close:vihaan", emote="brows")
move("buddy", L(0.4, -1.6), 3.0, clip="Penguin Walk"); do("buddy", "Penguin Walk", 3.0, cam="garden_wide"); wait(1.0)
say("buddy", "I'm walking like a penguin. Robots are not scared of penguins. Very smart, right?", clip="Penguin Walk", cam="close:buddy", emote="brows")
move("himank", L(-3.5, 0.0), 2.0, clip="Walking"); wait(2.1)
say("himank", "Excuse me, Mister Gnome. Have you seen a small round robot?", clip="Talk with Right Hand Open", cam="insert:gnome")
shot("insert:gnome"); wait(1.4)
say("himank", "He's not talking. Very suspicious.", clip="Hand on Hip Gesture", cam="close:himank", emote="brows")
# the very personal sprinkler
move("aarav", L(-0.9, 1.3), 2.2, clip="Walking"); wait(2.0)
say("aarav", "Look! Little tyre tracks! They go right over this hose...", clip="Look Around Dumbfounded", cam="insert:sprinkler")
prop("sprinkler", "on", dur=6.0, sounds=[(0.0, spray(6.0), 0.8)])
prop("drips", "on", who="aarav", dur=6.5)
do("aarav", "Shake It Off Dance", 5.0, cam="close:aarav"); wait(0.6)
say("aarav", "Why is it always raining on ME?", clip="Shake It Off Dance", gap=0.2)
say("vanu", "Aarav. That's a sprinkler.", clip="Hand on Hip Gesture", cam="close:vanu", emote="brows")
say("aarav", "It's a very personal sprinkler.", clip="Shrug", cam="close:aarav", emote="brows")
prop("sprinkler", "off")
fx.append((T, ha := tone(1, 0.01, "sine", 0.0), 0.0))
chorus(["vanu", "vihaan", "himank", "buddy"], "Ha ha ha ha!", clip="Victory Cheer", cam="garden_wide")

# ================= MUD MODE =================
mood("chase")
prop("zoomy", "place", at=[-1.6, 1.6])
prop("zoomy", "path", pts=[[-1.6, 1.6], [-0.2, 1.4], [1.0, 1.0], [1.5, 0.9]], dur=1.8, turbo=True, sounds=[(0.0, vac(1.8, True), 0.6)])
shot("garden_wide"); wait(1.8)
prop("zoomy", "spin", dur=3.0, sounds=[(0.0, squelch(), 0.8), (1.0, squelch(), 0.7), (2.0, squelch(), 0.6)])
prop("mudspray", "on", dur=3.0)
fx.append((T, beepboop(), 0.7)); prop("zoomy", "eyes", color="orange")
say("zoomy", "Mud detected. Mud is... extra delicious dirt. MUD MODE. Activated.", cam="insert:mud")
say("buddy", "He's making mud pies! Without ME!", clip="Slap Reaction", cam="close:buddy", emote="brows")
say("vanu", "Grab him, Himank! Now!", clip="Talk Passionately", cam="close:vanu", emote="brows")
move("himank", L(0.6, 0.6), 1.0, clip="Run and Leap"); do("himank", "Run and Leap", 1.6, cam="low_wide"); wait(1.1)
prop("zoomy", "path", pts=[[1.5, 0.9], [2.9, 0.4]], dur=0.7, turbo=True)
do("himank", "Stumble Walk", 1.4, sounds=[(0.2, slip(), 0.6)]); wait(1.3)
do("himank", "Fall Down", 2.4, sounds=[(0.3, squelch(), 1.0), (0.5, thud(), 0.7)], cam="insert:mud"); prop("mud", "splat", who="himank", dur=0.0)
wait(2.2)
say("himank", "I meant to do that. Mud is very good for your skin.", clip="Kneel on One Knee and Stand", cam="close:himank", emote="brows")
prop("zoomy", "path", pts=[[2.9, 0.4], [1.2, -0.3], [-0.6, 0.6], [-1.4, 1.5]], dur=2.4, turbo=False, tracks=True, sounds=[(0.0, vac(2.4), 0.5)])
shot("high_wide"); wait(1.6)
say("vihaan", "Uh oh. Muddy tracks... going straight to the veggie patch!", clip="Look Around Dumbfounded", cam="close:vihaan", emote="brows")
fx.append((T, drumroll(), 0.6)); shot("insert:veg"); wait(1.2)
chorus(ALL, "THE PUMPKIN!", clip="Slap Reaction", cam="garden_wide", gap=0.1)

# ================= THE PRIZE CARROT =================
move("buddy", L(-1.85, 1.65), 2.4, clip="Hello Run"); wait(2.5)
say("buddy", "Don't worry, Papa! I'll save the biggest carrot first!", clip="Motivational Cheer", cam="close:buddy", emote="brows")
prop("bigcarrot", "pull", dur=3.0, sounds=[(0.0, pullstrain(), 0.5), (1.5, pullstrain(), 0.5)])
do("buddy", "Pull Radish", 3.4, cam="insert:veg"); wait(3.0)
prop("bigcarrot", "fly", dur=1.6, sounds=[(0.0, popout(), 0.9), (0.1, whoosh(), 0.6), (1.5, splash(), 0.8)])
do("buddy", "Fall Down", 2.4, sounds=[(0.2, thud(), 0.6)]); shot("insert:pool"); wait(2.1)
say("vihaan", "Buddy! That was the PRIZE carrot!", clip="Hand on Hip Gesture", cam="close:vihaan", emote="brows")
say("buddy", "Now it's the prize... swimming carrot.", clip="Shrug", cam="close:buddy", emote="brows")
fx.append((T, beepboop(), 0.7)); prop("zoomy", "eyes", color="red")
say("zoomy", "Pumpkin detected. Pumpkin is one giant. Orange. CRUMB.", cam="insert:zoomy")
prop("zoomy", "path", pts=[[-1.4, 1.5], [-1.0, 1.8], [-0.95, 2.35]], dur=1.6, sounds=[(0.0, vac(1.6), 0.5)])
prop("pumpkin", "wobble", dur=1.5)
fx.append((T, ticktock(4), 0.6)); shot("insert:veg"); wait(1.6)

# ================= OPERATION POOL TRAP =================
mood("plan")
say("vanu", "I've got it! Zoomy loves crumbs... so we lead him into the pool! Operation Pool Trap!", clip="Motivational Cheer", cam="close:vanu", emote="brows")
say("vanu", "Vihaan, Aarav, more water! Buddy, you're the bait.", clip="Talk with Left Hand Raised", gap=0.2)
say("buddy", "AGAIN? Why is it always me?", clip="Slap Reaction", cam="close:buddy", emote="brows")
chorus(["vanu", "aarav", "vihaan", "himank"], "Because you have the cookies!", clip="Hand on Hip Gesture", cam="garden_wide")
prop("wbucket", "carry", who="vihaan", dur=3.6); prop("wbucket", "carry", who="aarav", dur=3.6)
move("vihaan", L(2.6, 1.4), 3.6, clip="Carry Water Bucket Walk"); move("aarav", L(2.4, 2.4), 3.6, clip="Carry Water Bucket Walk")
shot("garden_wide"); wait(3.7)
prop("pool", "fill", dur=1.6, sounds=[(0.0, splash(), 0.6), (0.6, splash(), 0.5)])
shot("insert:pool"); wait(1.8)
move("buddy", L(2.3, 1.4), 3.4, clip="Hello Run")
prop("crumbs", "trail", pts=[[-0.9, 1.9], [0.3, 1.2], [1.4, 1.5], [2.5, 2.2]], sounds=[(0.3, pop(), 0.3), (1.0, pop(), 0.3), (1.7, pop(), 0.3)])
say("buddy", "Here, Zoomy Zoomy! Cookie crumbs! Extra crunchy!", clip="Hello Run", cam="garden_wide")
prop("zoomy", "path", pts=[[-0.95, 2.35], [-0.9, 1.9], [0.3, 1.2], [1.4, 1.5], [2.5, 2.2], [3.6, 2.5]], dur=3.0, turbo=True, sounds=[(0.0, vac(3.0, True), 0.6)])
shot("high_wide"); wait(2.9)
prop("zoomy", "float", sounds=[(0.0, splash(), 1.0)])
shot("insert:pool"); wait(1.6)
fx.append((T, beepboop(), 0.7)); prop("zoomy", "eyes", color="rainbow")
say("zoomy", "Water detected. BOAT MODE. Activated. Ahoy, mateys!", cam="insert:pool")
fx.append((T, ahoy(), 0.7)); prop("zoomy", "spin", dur=4.0, slow=True)
mood("happy")
chorus(ALL, "We caught Zoomy!", clip="Victory", cam="garden_wide")
for k in ("vanu", "vihaan", "buddy"): do(k, "Jumping Jacks", 3.0)
do("aarav", "Victory Cheer", 3.0)
say("himank", "And look! He's all clean and shiny now.", clip="Talk with Right Hand Open", cam="close:himank", emote="brows")
say("vanu", "Unlike you, Himank.", clip="Hand on Hip Gesture", cam="close:vanu", emote="brows")

# ================= ENDING =================
say("papa", "Bro Bros! Who left muddy footprints all over my garden?", cam="garden_wide")
for k in ALL: do(k, "Look Around Dumbfounded", 2.2)
wait(1.0)
say("zoomy", "Beep boop. It was Himank.", cam="insert:zoomy")
say("himank", "...Fair.", clip="Shrug", cam="close:himank", emote="brows")
chorus(["vanu", "aarav", "vihaan", "buddy"], "Ha ha ha ha!", clip="Victory Cheer", cam="garden_wide")
say("papa", "But my prize pumpkin is safe! Thank you, Bro Bros! You're my garden heroes!")
chorus(ALL, "Yaaay!", clip="Cheer with Both Hands Up", cam="garden_wide")
# teaser
mood("mystery")
fx.append((T, beepboop(), 0.7)); prop("zoomy", "eyes", color="red")
say("zoomy", "Next stop... SPORTS DAY. I will win. Every. Race.", cam="insert:zoomy")
chorus(ALL, "OH NO!", clip="Slap Reaction", cam="garden_wide")
say("vanu", "See you at Sports Day! Ask a grown up to subscribe to Bro Bros Fun!", clip="Big Wave Hello", cam="close:vanu", emote="brows")
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
