"""Episode 8: ZOOMY the Crazy Robot Vacuum! Slapstick comedy format: cold-open chase (sock gets eaten), title, stakes
(Grandma arrives in 10 minutes + DON'T touch the cake), TURBO button chaos, running gag (Zoomy chases crumbs -> Buddy),
Operation Cake Shield, DANCE MODE, slow-mo cake save + frosting SPLAT, fast-forward clean, Grandma, sock gag, cliffhanger.
One set: living room (origin x=400). Builds timeline.json + audio.wav + voice.wav for build8 + props_ep8."""
import json, numpy as np, soundfile as sf, os, sys
sys.path.insert(0, "/home/claude/bbf")
from engine import tts, sfx, music, tone, noise, SR, VOICES

VOICES.update({"vanu": ("af_heart", 2, 1.0), "aarav": ("am_puck", 4, 1.05), "vihaan": ("af_jessica", 4, 1.08),
               "himank": ("am_echo", 5, 1.05), "buddy": ("af_kore", 3, 1.08),
               "mummy": ("af_nicole", 0, 1.0), "grandma": ("bf_emma", -1, 0.92), "zoomy": ("am_michael", 3, 1.15)})
OUT = "/mnt/user-data/outputs/ep08"; os.makedirs(OUT, exist_ok=True)
T = 0.0; ev = []; shots = []; voice = []; fx = []; scenes = []; moods = []
ALL = ["vanu", "aarav", "vihaan", "himank", "buddy"]
OFF = ("mummy", "grandma", "zoomy")
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
    fx.append((t0, steps(dur, 7 if "Run" in clip else 3.6), 0.45))
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
        p = int(k / rate * SR); s = tone(lambda t: 150 - 200 * t, 0.06, "sine", 0.14, r=0.03); out[p:p + len(s)] += s[:len(out) - p]
    return out
whoosh = lambda: sfx("whoosh"); boing = lambda: sfx("boing"); pop = lambda: sfx("pop"); ding = lambda: sfx("ding"); tada = lambda: sfx("tada")
sparkle = lambda: sfx("sparkle"); cheer = lambda: sfx("cheer"); drumroll = lambda: sfx("drumroll"); buzz = lambda: sfx("buzz")
def vac(d=2.0, turbo=False):
    n = int(d * SR); t = np.arange(n) / SR
    f = (220 if not turbo else 330) + 25 * np.sin(2 * np.pi * 3 * t)
    hum = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.18 + noise(d, 0.5, r=0.1, lp=2500 if not turbo else 5000)[:n] * 0.5
    env = np.minimum(1, t / 0.15) * np.minimum(1, (d - t) / 0.2)
    return (hum * env * (0.6 if not turbo else 0.85)).astype(np.float32)
def slurp():
    n = int(0.6 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * np.cumsum(300 + 1800 * t) / SR) * 0.3 * np.exp(-t * 2) + noise(0.6, 0.4, r=0.1, lp=4000)[:n] * 0.4).astype(np.float32)
def beepboop():
    return cat_(tone(880, 0.08, "square", 0.2, r=0.02), silence(0.04), tone(660, 0.08, "square", 0.2, r=0.02), silence(0.04), tone(1175, 0.12, "square", 0.2, r=0.04))
def slip(): return cat_(tone(lambda t: 1200 - 900 * t / 0.3, 0.3, "sine", 0.3, r=0.05), noise(0.2, 0.7, r=0.15, lp=1500))
def thud(): return (noise(0.35, 1.0, r=0.3, lp=220) * 0.9).astype(np.float32)
def crash(): return cat_(noise(0.08, 1.0, r=0.05, lp=8000), noise(0.6, 0.6, r=0.5, lp=5000))
def splat(): return cat_(noise(0.06, 1.0, r=0.04, lp=1200), tone(lambda t: 300 - 200 * t, 0.25, "sine", 0.4, r=0.2))
def doorbell(): return cat_(tone(659, 0.45, "sine", 0.35, r=0.5), tone(523, 0.7, "sine", 0.35, r=0.7))
def scream(): return tone(lambda t: 900 + 250 * np.sin(t * 30), 0.9, "saw", 0.10, a=0.02, r=0.3)
def ticktock(n=5):
    out = []
    for i in range(n): out += [tone(1200 if i % 2 else 900, 0.05, "square", 0.18, r=0.03), silence(0.45)]
    return cat_(*out)
def rewind(): return tone(lambda t: 2000 - 1700 * t / 0.8, 0.8, "saw", 0.12, r=0.1)
def ffwd(d=3.0): return (vac(d, True) + cat_(*[cat_(tone(1400, 0.05, "square", 0.08, r=0.02), silence(0.1)) for _ in range(int(d / 0.15))])[:int(d * SR)]).astype(np.float32)
def disco(d=4.0):
    out = np.zeros(int(d * SR), np.float32); B_ = 60 / 128
    for k in range(int(d / B_)):
        p = int(k * B_ * SR); s = tone(lambda t: 120 - 80 * t, 0.15, "sine", 0.45, r=0.1); out[p:p + len(s)] += s[:len(out) - p]
        q = int((k + 0.5) * B_ * SR); h = noise(0.05, 0.3, r=0.04, lp=9000); out[q:q + len(h)] += h[:len(out) - q]
    return out

L = lambda x, y: [x, y]   # living-room coordinates relative to origin
CAST0 = {"vanu": [-0.4, 0.3, 0, "Idle"], "aarav": [-1.4, 0.0, 15, "Idle"], "vihaan": [0.6, -0.2, -10, "Idle"],
         "himank": [-2.2, -0.4, 25, "Idle"], "buddy": [1.6, -0.7, -20, "Idle"]}

# ================= COLD OPEN (the funniest moment first, no title) =================
scene("cold", "living", CAST0, mood="chase")
shot("living_wide")
prop("zoomy", "place", at=[2.9, -0.4])
prop("zoomy", "path", pts=[[2.9, -0.4], [2.2, -0.9], [1.2, -1.2], [0.2, -0.9]], dur=1.8, turbo=True, sounds=[(0.0, vac(2.0, True), 0.6)])
move("buddy", L(-0.8, -1.5), 1.6)
fx.append((T + 0.1, scream(), 0.5))
say("buddy", "AAAAH! It's chasing me! Help!", clip="Running", cam="low_wide", gap=0.0)
for k in ("vanu", "aarav", "vihaan", "himank"): do(k, "Look Around Dumbfounded", 2.5)
prop("zoomy", "path", pts=[[0.2, -0.9], [-0.6, -1.4]], dur=0.8, turbo=True)
prop("sock", "eat", sounds=[(0.3, slurp(), 0.9)])
shot("insert:feet"); wait(1.3)
say("buddy", "MY SOCK! It ate my SOCK!", clip="Slap Reaction", cam="close:buddy", emote="brows", gap=0.1)
say("zoomy", "Beep boop. Delicious.", cam="insert:zoomy", gap=0.2)
fx.append((T, rewind(), 0.7))
card("rewind", 1.6, txt="10 MINUTES EARLIER...", sounds=[(0.0, whoosh(), 0.5)])
card("intro", 3.0, sounds=[(0.2, tada(), 0.8), (0.6, sparkle(), 0.6)], cam="living_wide")

# ================= SETUP: the stakes =================
scene("setup", "living", CAST0, mood="happy")
prop("zoomy", "place", at=[3.3, 1.9]); prop("sock", "reset"); prop("box", "show")
shot("living_wide"); wait(0.6)
say("mummy", "Bro Bros! Grandma is coming in TEN minutes! Clean the living room... and please, please, do NOT touch Grandma's birthday cake!", cam="insert:cake")
chorus(ALL, "Okay, Mummy!", clip="Agree Gesture", cam="living_wide", gap=0.1)
say("vihaan", "Ten minutes? This room looks like a dinosaur had a party in it.", clip="Look Around Dumbfounded", cam="close:vihaan", emote="brows")
say("himank", "Relax. I have a secret weapon. Ta-daa! A brand new robot vacuum!", clip="Hop with Arms Raised", cam="close:himank", emote="brows")
prop("box", "open", sounds=[(0.1, pop(), 0.6), (0.3, sparkle(), 0.5)])
prop("zoomy", "path", pts=[[3.3, 1.9], [2.6, 0.9]], dur=1.4, sounds=[(0.0, beepboop(), 0.7), (0.2, vac(1.4), 0.4)])
shot("insert:zoomy"); wait(1.6)
say("zoomy", "Hello. I am Zoomy. I love dirt. Dirt is my best friend.", cam="insert:zoomy")
say("buddy", "Aww, he's so cute! Can I keep him? Can he sleep in my bed?", clip="Big Heart Gesture", cam="close:buddy", emote="brows")
say("aarav", "The remote has a big red button that says TURBO. Turbo means... super clean, right?", clip="Scheming Hand Rub", cam="close:aarav")
say("vanu", "Aarav. Read the tiny writing first.", clip="Finger Wag No", cam="close:vanu", emote="brows")
say("aarav", "Pfff. Tiny writing is for tiny people. Pressing it!", clip="Talk Passionately", cam="close:aarav", emote="brows")
fx.append((T, beepboop(), 0.8)); prop("zoomy", "eyes", color="red")
say("zoomy", "TURBO MODE. ACTIVATED. MUST. EAT. EVERYTHING.", cam="insert:zoomy")
mood("chase")

# ================= CHAOS =================
prop("zoomy", "path", pts=[[2.6, 0.9], [1.5, -0.4], [0.9, -0.5]], dur=1.2, turbo=True, sounds=[(0.0, vac(4.0, True), 0.6)])
prop("car", "eat", sounds=[(1.0, slurp(), 0.9)])
shot("low_wide"); wait(1.4)
say("vihaan", "NOOO! My race car! It swallowed my race car!", clip="Slap Reaction", cam="close:vihaan", emote="brows")
prop("zoomy", "path", pts=[[0.9, -0.5], [0.0, -0.1], [-1.2, -0.3], [-2.0, -0.9]], dur=2.0, turbo=True)
move("aarav", L(-3.0, -1.8), 1.2); move("himank", L(-0.6, -2.2), 1.3)
wait(0.5); do("vanu", "Hop with Arms Raised", 1.4, sounds=[(0.2, boing(), 0.5)])
wait(1.2)
do("himank", "Fall Down", 2.4, sounds=[(0.1, slip(), 0.8), (0.6, thud(), 0.9)], cam="close:himank"); wait(1.0)
say("himank", "I'm okay! The floor is just... very friendly.", clip="Kneel on One Knee and Stand", emote="brows")
say("vanu", "Everybody FREEZE! Look. It's not chasing us. It's going in circles... around Buddy.", clip="Talk with Left Hand Raised", cam="close:vanu", emote="brows")
prop("zoomy", "circle", center=[1.6, -0.7], r=0.6, dur=3.0, turbo=True, sounds=[(0.0, vac(3.0, True), 0.5)])
shot("insert:buddyfeet"); wait(1.0)
say("buddy", "Why me? What did I do? I'm a nice boy!", clip="Shrug", cam="close:buddy", emote="brows")
say("himank", "Buddy. Check your pockets.", clip="Talk with Right Hand Open", cam="close:himank")
do("buddy", "Confused Scratch", 2.0); prop("crumbs", "drop", at=[1.6, -0.7], sounds=[(0.2, pop(), 0.4)])
say("buddy", "Oh. Cookie crumbs. Lots of cookie crumbs. And one whole cookie. For emergencies.", clip="Confused Scratch", cam="close:buddy", emote="brows")
chorus(["vanu", "aarav", "vihaan", "himank"], "BUDDY!", clip="Hand on Hip Gesture", cam="living_wide")
fx.append((T, ticktock(6), 0.5))
say("vihaan", "Guys. Big problem. If Zoomy follows crumbs... and the CAKE is covered in yummy crumbs...", clip="Look Around Dumbfounded", cam="close:vihaan", emote="brows")
prop("zoomy", "path", pts=[[1.6, -0.7], [0.4, 0.2], [-1.3, 0.7]], dur=2.6, turbo=False, sounds=[(0.0, vac(2.6), 0.5)])
shot("insert:cake"); fx.append((T, drumroll(), 0.6)); wait(1.4)
chorus(ALL, "THE CAKE!", clip="Slap Reaction", cam="low_wide", gap=0.1)

# ================= OPERATION CAKE SHIELD =================
mood("plan")
say("vanu", "Operation Cake Shield! Buddy, you're the bait. Make a cookie trail AWAY from the cake!", clip="Motivational Cheer", cam="close:vanu", emote="brows")
say("buddy", "I'm bait? Cool! Wait... is bait good?", clip="Hop with Arms Raised", cam="close:buddy", emote="brows")
move("buddy", L(2.4, -1.4), 2.0, clip="Running")
prop("crumbs", "trail", pts=[[-0.5, 0.2], [1.0, -0.8], [2.4, -1.4]], sounds=[(0.2, pop(), 0.3), (0.7, pop(), 0.3), (1.2, pop(), 0.3)])
prop("zoomy", "path", pts=[[-1.3, 0.7], [-0.5, 0.2], [1.0, -0.8], [2.0, -1.3]], dur=2.6, turbo=True, sounds=[(0.0, vac(2.6, True), 0.5)])
say("buddy", "Here, Zoomy Zoomy! Yummy crumbs! Come to Buddy!", clip="Big Wave Hello", cam="living_wide")
say("himank", "Now my superhero jump! Over the robot... HUP!", clip="Jump with Arms Open", cam="close:himank", emote="brows")
do("himank", "Jump with Arms Open", 1.6, sounds=[(0.3, whoosh(), 0.6), (1.0, boing(), 0.6)], cam="low_wide"); wait(1.6)
say("himank", "Did you see that? I flew! I'm basically a bird.", clip="Victory Fist Pump", cam="close:himank", emote="brows")
say("aarav", "The remote! I'll switch it off. Okay... OFF button, OFF button... this one!", clip="Talk with Hands Open", cam="close:aarav", emote="brows")
fx.append((T, beepboop(), 0.8)); prop("zoomy", "eyes", color="rainbow")
say("zoomy", "DANCE MODE. ACTIVATED. Let's boogie.", cam="insert:zoomy")
mood("disco"); prop("disco", "on", dur=7.0, sounds=[(0.0, disco(7.0), 0.9)])
prop("zoomy", "spin", dur=7.0)
for k in ALL: do(k, "Hip Hop Dance" if k in ("vanu", "himank") else "FunnyDancing 03", 7.0)
shot("dance_orbit"); wait(1.5)
say("vihaan", "Why... can't... I... stop... dancing?", clip="FunnyDancing 03", cam="close:vihaan", emote="brows", gap=0.2)
shot("living_wide"); wait(1.6)
say("vanu", "Aarav! That's not OFF!", clip="Hip Hop Dance", cam="close:vanu", emote="brows", gap=0.2)
say("aarav", "Every button is a surprise button!", clip="FunnyDancing 03", cam="close:aarav", gap=0.1)
prop("disco", "off"); fx.append((T, beepboop(), 0.7)); prop("zoomy", "eyes", color="red"); mood("chase")

# ================= CLIMAX: the cake =================
say("zoomy", "Cake detected. Cake. Is. DIRT.", cam="insert:zoomy")
prop("zoomy", "path", pts=[[1.0, -0.2], [-1.2, 0.5], [-2.7, 1.0]], dur=1.8, turbo=True, sounds=[(0.0, vac(2.0, True), 0.7)])
fx.append((T, ticktock(4), 0.6)); shot("insert:cake"); wait(1.0)
say("vihaan", "Not on my watch!", clip="Running", cam="close:vihaan", emote="brows", gap=0.0)
move("vihaan", L(-2.3, 0.4), 1.0)
wait(0.8)
prop("cake", "fly", dur=2.2, sounds=[(0.0, crash(), 0.7), (0.2, whoosh(), 0.7)])
prop("frosting", "fly", dur=0.9, to="buddy")
do("vihaan", "Kneel on One Knee and Stand", 3.0, cam="insert:cake")
wait(1.0); shot("close:vihaan"); wait(1.2)
fx.append((T - 0.2, splat(), 1.0)); prop("frosting", "splat", who="buddy")
do("buddy", "Slap Reaction", 2.0, cam="close:buddy"); wait(1.2)
say("vihaan", "Caught it! The cake is safe! Not even one crumb fell!", clip="Victory Cheer", cam="close:vihaan", emote="brows")
say("buddy", "Um. One crumb fell. On my FACE.", clip="Shrug", cam="close:buddy", emote="brows")
do("buddy", "Shrug", 1.5)
say("buddy", "...It's strawberry. Ten out of ten.", clip="Agree Gesture", cam="close:buddy", emote="brows")
fx.append((T, cheer(), 0.3))
chorus(["vanu", "aarav", "vihaan", "himank"], "Ha ha ha ha!", clip="Victory Cheer", cam="living_wide")

# ================= DOORBELL! fast-forward clean =================
fx.append((T, doorbell(), 0.9)); mood("panic")
say("vanu", "The doorbell! Grandma's here, and the room is still a disaster!", clip="Look Around Dumbfounded", cam="close:vanu", emote="brows")
say("himank", "Zoomy! Normal mode! Clean, clean, CLEAN!", clip="Talk Passionately", cam="close:himank", emote="brows")
fx.append((T, beepboop(), 0.7)); prop("zoomy", "eyes", color="green")
say("zoomy", "Cleaning mode. Hold on to your socks.", cam="insert:zoomy")
card("ffwd", 3.2, txt="SUPER FAST CLEANING!", sounds=[(0.0, ffwd(3.2), 0.8)])
prop("zoomy", "zigzag", dur=3.2, t0=T - 3.2); prop("blocks", "clean", t0=T - 3.2, dur=3.2)
mood("happy")
say("grandma", "Hellooo, my darlings! Oh my! What a sparkling clean house!", cam="living_wide")
chorus(ALL, "Happy birthday, Grandma!", clip="Cheer with Both Hands Up", cam="living_wide")
say("grandma", "And Buddy, why is your face pink?", gap=0.2)
say("buddy", "...New face cream?", clip="Shrug", cam="close:buddy", emote="brows")
prop("zoomy", "path", pts=[[-0.4, -0.6], [1.4, -1.0]], dur=1.4, turbo=True, sounds=[(0.0, vac(1.4, True), 0.5)])
prop("sock2", "eat", sounds=[(1.0, slurp(), 0.9)])
shot("insert:buddyfeet"); wait(1.6)
say("buddy", "MY OTHER SOCK!", clip="Slap Reaction", cam="close:buddy", emote="brows")
say("zoomy", "Beep boop. Matching set.", cam="insert:zoomy")
chorus(["vanu", "aarav", "vihaan", "himank"], "Ha ha ha ha!", clip="Victory Cheer", cam="living_wide")

# ================= CLIFFHANGER =================
mood("mystery")
prop("zoomy", "path", pts=[[1.4, -1.0], [3.0, -2.6], [4.2, -4.6]], dur=2.6, turbo=True, sounds=[(0.0, vac(2.6, True), 0.5)])
prop("door", "open", sounds=[(0.2, sfx("door"), 0.6)])
shot("insert:door"); wait(2.0)
say("aarav", "Wait. The front door is open... Where is Zoomy going?", clip="Look Around Dumbfounded", cam="close:aarav", emote="brows")
say("zoomy", "Next stop... THE PARK. So. Much. Dirt.", cam="insert:door")
chorus(ALL, "OH NO!", clip="Slap Reaction", cam="living_wide")
say("vanu", "Find out what Zoomy does next time! Ask a grown up to subscribe to Bro Bros Fun!", clip="Big Wave Hello", cam="close:vanu", emote="brows")
for k in ("aarav", "vihaan", "himank", "buddy"): do(k, "Big Wave Hello", 3.0)
wait(0.4)
card("endcard", 6.0, sounds=[(0.2, tada(), 0.7), (0.5, sparkle(), 0.6)])
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
MM = {"chase": ("adventure", 150), "happy": ("happy", 126), "plan": ("adventure", 132), "disco": (None, 0), "panic": ("adventure", 150), "mystery": ("mystery", 110)}
segs = moods + [(TOTAL, None)]
for (t0, m), (t1, _) in zip(segs, segs[1:]):
    if t1 - t0 < 0.5: continue
    mm_, bpm_ = MM.get(m, ("happy", 126))
    if mm_ is None: continue
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
