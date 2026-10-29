"""Episode 4: Diwali Dhamaka. Builds timeline.json + audio.wav for the eng2 pipeline (build4).
Scenes: decorated living room -> balcony rangoli relay + diya relay -> kitchen laddoos -> balcony night: safety rules, sparklers, anar, chakri, rockets, song."""
import json, numpy as np, soundfile as sf, os, sys
sys.path.insert(0, "/home/claude/bbf")
from engine import tts, sfx, music, tone, noise, SR, VOICES

VOICES.update({"vanu": ("af_heart", 2, 1.0), "aarav": ("am_puck", 4, 1.05), "vihaan": ("af_jessica", 4, 1.08),
               "himank": ("am_echo", 5, 1.05), "buddy": ("af_kore", 3, 1.08), "mummy": ("af_sarah", -1, 0.98)})
OUT = "/mnt/user-data/outputs/ep04"; os.makedirs(OUT, exist_ok=True)
T = 0.0; ev = []; shots = []; voice = []; fx = []; scenes = []; moods = []
ALL = ["vanu", "aarav", "vihaan", "himank", "buddy"]
TALK = ["Talk with Right Hand Open", "Talk Passionately", "Talk with Left Hand on Hip", "Agree Gesture"]
_tk = {}
def scene(name, set_, cast, light="day", mood="festive"):
    if scenes: scenes[-1]["t1"] = round(T, 3)
    scenes.append({"name": name, "set": set_, "t0": round(T, 3), "cast": cast, "light": light}); moods.append((T, mood))
def shot(s): shots.append((round(T, 3), s))
def say(who, text, clip=None, cam=None, gap=0.3, look=None, emote=None):
    global T
    if cam: shot(cam)
    if clip is None:
        i = _tk.get(who, 0); clip = TALK[i % 2] if who != "vanu" else TALK[(i % 2) + 1 if i % 3 else 0]; _tk[who] = i + 1
    a = tts(who, text); d = len(a) / SR
    voice.append((T + 0.05, a))
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
def do(who, clip, dur, block=False, sounds=(), cam=None, speed=1.0):
    global T
    if cam: shot(cam)
    ev.append({"t": round(T, 3), "type": "clip", "who": who, "clip": clip, "dur": dur, "speed": speed})
    for at, s, g in sounds: fx.append((T + at, s, g))
    if block: T += dur
def move(who, to, dur, clip="Walking", yaw=None, steps_sfx=True):
    ev.append({"t": round(T, 3), "type": "move", "who": who, "to": to, "dur": dur, "clip": clip, "yaw": yaw})
    if steps_sfx: fx.append((T, steps(dur, 7 if "Run" in clip or "Sprint" in clip else 3.6), 0.5))
def prop(name, action, sounds=(), **kw):
    e = {"t": round(T, 3), "type": "prop", "name": name, "action": action}; e.update(kw); ev.append(e)
    for at, s, g in sounds: fx.append((T + at, s, g))
def card(name, dur, sounds=(), cam=None):
    global T
    if cam: shot(cam)
    ev.append({"t": round(T, 3), "type": "card", "name": name, "dur": dur})
    for at, s, g in sounds: fx.append((T + at, s, g))
    T += dur
def wait(d):
    global T; T += d

# ---------- SFX ----------
def steps(d, rate):
    out = np.zeros(int(d * SR) + 10, np.float32)
    for k in range(int(d * rate)):
        p = int(k / rate * SR); s = tone(lambda t: 150 - 200 * t, 0.06, "sine", 0.14, r=0.03); out[p:p + len(s)] += s[:len(out) - p]
    return out
whoosh = lambda: sfx("whoosh"); boing = lambda: sfx("boing"); pop = lambda: sfx("pop"); ding = lambda: sfx("ding"); tada = lambda: sfx("tada")
sparkle = lambda: sfx("sparkle"); cheer = lambda: sfx("cheer"); sneeze = lambda: sfx("sneeze")
def crackle(d, vol=0.22):
    n = int(d * SR); rng = np.random.default_rng(4); out = np.zeros(n, np.float32)
    hiss = noise(d, 0.35, r=0.2, lp=9000)[:n]
    for p in rng.integers(0, n - 400, int(d * 160)):
        out[p:p + 300] += (rng.random(300) * 2 - 1).astype(np.float32) * rng.random() * 0.6
    env = np.minimum(1, np.arange(n) / (0.2 * SR)) * np.minimum(1, (n - np.arange(n)) / (0.4 * SR))
    return ((hiss + out) * env * vol).astype(np.float32)
def fountain(d, vol=0.3):
    n = int(d * SR); t = np.arange(n) / SR
    env = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 0.8) * (0.6 + 0.4 * np.sin(t * 5.0) ** 2)
    return ((noise(d, 0.5, r=0.1, lp=5000)[:n] + crackle(d, 0.5)[:n] * 0.5) * env * vol).astype(np.float32)
def whirr(d, vol=0.22):
    n = int(d * SR); t = np.arange(n) / SR
    f = 160 + 420 * np.minimum(1, t / 0.8)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4 + noise(d, 0.6, r=0.1, lp=4000)[:n]
    env = np.minimum(1, t / 0.3) * np.minimum(1, (d - t) / 0.6)
    return (s * env * vol).astype(np.float32)
def rocket_sfx(rise=1.3, vol=0.5):
    n = int(rise * SR); t = np.arange(n) / SR
    f = 400 + 1400 * t / rise
    w = (np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25 + noise(rise, 0.5, r=0.05, lp=6000)[:n]) * np.minimum(1, t / 0.1)
    boom = noise(1.4, 1.0, r=0.9, lp=260) * 1.2
    crk = crackle(1.2, 0.7)
    out = np.zeros(n + len(boom) + 2000, np.float32); out[:n] += w * 0.5; out[n:n + len(boom)] += boom; out[n + 2000:n + 2000 + len(crk)] += crk
    return (out * vol).astype(np.float32)
def far_boom(vol=0.18):
    return (noise(1.0, 1.0, r=0.8, lp=200) * vol).astype(np.float32)
def laugh(): return sfx("cheer")

# ================= SCRIPT =================
# ---- 1. LIVING ROOM (decorated): it's Diwali! ----
scene("living", "living_diwali", {"vanu": [0.0, 0.4, 0, "Idle"], "aarav": [-1.4, 0.8, 20, "Idle"], "himank": [1.4, 0.8, -20, "Idle"],
                                 "vihaan": [-0.6, -0.3, 10, "Idle"], "buddy": [-1.7, 0.0, 30, "Idle"]}, light="day", mood="festive")
card("intro", 3.4, sounds=[(0.2, tada(), 0.8), (0.6, sparkle(), 0.6)], cam="living_wide")
say("vanu", "Happy Diwali, Bro Bros! Today is the festival of lights, and our house is going to shine like a star!", clip="Cheer with Both Hands", cam="close:vanu", emote="brows")
say("himank", "Fun fact! Diwali means a row of lamps. Deepa is lamp, avali is row. Deepavali!", clip="Talk with Right Hand Open", cam="close:himank", emote="brows")
say("vihaan", "A row of lamps? I want a hundred rows!", clip="Jump with Arms Open", cam="close:vihaan")
say("aarav", "First we decorate, then we play, and only at night, with Mummy, the crackers.", clip="Agree Gesture", cam="two:aarav:vihaan")
do("buddy", "Male Bend Over Pick Up", 2.4, cam="close:buddy"); prop("tangle", "grab", who="buddy"); wait(2.0)
say("buddy", "I found the fairy lights! I will put them up all by myself.", clip="Happy Sway Standing", cam="close:buddy")
do("buddy", "Confused Scratch", 3.0, sounds=[(0.5, boing(), 0.5), (1.4, boing(), 0.5)], cam="close:buddy"); wait(2.2)
say("buddy", "Um. Guys? The lights put ME up. I am a Diwali tree!", clip="Shrug", cam="living_wide", emote="brows")
fx.append((T, laugh(), 0.5))
for k in ("vanu", "aarav", "vihaan", "himank"): do(k, "Happy Sway Standing", 2.6)
wait(1.6)
say("aarav", "Hold still, Diwali tree. Himank, you take that end.", clip="Talk with Right Hand Open", cam="two:aarav:buddy")
move("himank", [-1.1, 0.1], 1.2); move("aarav", [-2.2, 0.1], 1.2); wait(1.4)
do("himank", "Collect Object", 2.4); do("aarav", "Collect Object", 2.4, cam="living_wide"); prop("tangle", "free", who="buddy"); wait(2.6)
say("buddy", "Free! Thank you, thank you. Now where do the lights go?", clip="Big Wave Hello", cam="close:buddy")
say("vanu", "Already done, Buddy. Look up!", clip="Talk with Right Hand Open", cam="living_wide")
fx.append((T, sparkle(), 0.7)); shot("insert:thali"); wait(2.4)
say("vihaan", "Whoa. Diyas! Lanterns! And... laddoos!", clip="Look Around Dumbfounded", cam="insert:sweets", emote="brows")
say("vanu", "Laddoos are for later. Now, who is ready for the Diwali games?", clip="Hand on Hip Gesture", cam="close:vanu")
chorus(ALL, "Diwali games!", clip="Cheer with Both Hands", cam="living_wide")
for k in ALL: move(k, [2.9, 2.3], 2.8, clip="Excited Walk Male")
shot("living_wide"); wait(2.4)
card("wipe", 0.8, sounds=[(0.0, whoosh(), 0.7)])

# ---- 2. BALCONY (sunset): rangoli relay + diya relay ----
scene("balcony", "balcony", {"vanu": [0.0, 0.9, 0, "Idle"], "aarav": [-1.3, 0.7, 20, "Idle"], "vihaan": [1.3, 0.7, -20, "Idle"],
                             "himank": [-2.0, 0.1, 30, "Idle"], "buddy": [2.0, 0.1, -30, "Idle"]}, light="sunset", mood="festive")
shot("balcony_wide"); wait(1.6)
say("vanu", "Game one: the Rangoli Relay! Each of us adds one ring of colour. Ready, steady, rangoli!", clip="Talk with Right Hand Open", cam="close:vanu", emote="brows")
fx.append((T, ding(), 0.6)); prop("rangoli", "start")
for i, (k, line) in enumerate((("aarav", "Red petals on the outside. Neat and tidy."), ("himank", "Yellow and green rings. Perfectly round, like a planet."),
                               ("vihaan", "Blue petals! Blue is the best colour in the universe!"), ("buddy", "Pink in the middle. And done! Rangoli power!"))):
    move(k, [0.0, 0.2 + (0.35 if i % 2 else -0.35)], 1.4); wait(1.5)
    do(k, "Male Bend Over Pick Up", 2.4, sounds=[(0.6, pop(), 0.4), (1.4, pop(), 0.4)], cam="insert:rangoli"); prop("rangoli", "reveal", step=i); wait(2.5)
    say(k, line, clip="Agree Gesture" if i < 3 else "Victory Cheer", cam="close:" + k)
    move(k, [-1.3 + i * 0.9, 0.9 if i % 2 else 0.6], 1.4); wait(0.4)
shot("insert:rangoli"); wait(2.0)
say("vihaan", "Achoo!", clip="Headache Relief", cam="close:vihaan"); fx.append((T - 1.2, sneeze(), 0.8)); prop("rangoli", "puff")
say("buddy", "Vihaan! You sneezed on the rangoli!", clip="Look Around Dumbfounded", cam="two:buddy:vihaan", emote="brows")
say("vihaan", "The colours tickled my nose. Is it okay?", clip="Shrug", cam="close:vihaan")
say("aarav", "Phew. Still perfect. Rangoli relay, complete!", clip="Sit Thumbs Up Right" if False else "Agree Gesture", cam="insert:rangoli")
say("vanu", "Game two: the Diya Relay. Mummy lit four diyas. Carry one across the balcony, nice and slow. If the flame goes out, you start again.", clip="Talk with Left Hand on Hip", cam="close:vanu")
say("mummy", "Slow and steady, kids! Two hands on the diya, and walk, don't run.", clip="-", cam="insert:rangoli")
fx.append((T, ding(), 0.6)); prop("rangoli", "light")
for i, k in enumerate(("aarav", "himank", "vihaan")):
    move(k, [0.0 + (0.45 if i % 2 else -0.45), 0.35], 1.2); wait(1.3)
    do(k, "Collect Object", 2.0, cam="close:" + k); prop("diya", "carry", who=k); wait(2.0)
    move(k, [2.4 if i % 2 else -2.4, -1.0], 3.2, clip="Cautious Crouch Walk Forward"); shot("balcony_wide"); wait(3.3)
    prop("diya", "place", who=k, sounds=[(0.2, ding(), 0.5)])
    say(k, ("Steady... steady... and safe!", "Science says: walk slowly and the flame stays happy.", "I did it! Slowest and bestest!")[i], clip="Victory Cheer", cam="close:" + k)
move("buddy", [0.45, 0.35], 1.2); wait(1.3)
do("buddy", "Collect Object", 2.0, cam="close:buddy"); prop("diya", "carry", who="buddy"); wait(2.0)
say("buddy", "My turn! Buddy express, coming through!", clip="-", cam="close:buddy", emote="brows")
move("buddy", [2.4, -1.0], 1.3, clip="Running"); shot("balcony_wide"); wait(1.2)
prop("diya", "blowout", who="buddy", sounds=[(0.0, whoosh(), 0.5)]); wait(0.6)
say("buddy", "Oh no. My flame ran away!", clip="Look Around Dumbfounded", cam="close:buddy")
say("vanu", "Because you ran, Buddy! Fire likes slow and careful. Try again.", clip="Finger Wag No", cam="two:vanu:buddy")
say("buddy", "Slow... and... careful.", clip="-", cam="close:buddy")
prop("diya", "relight", who="buddy")
move("buddy", [-2.4, -1.0], 4.0, clip="Cautious Crouch Walk Forward"); shot("balcony_wide"); wait(4.1)
prop("diya", "place", who="buddy", sounds=[(0.2, ding(), 0.5)])
chorus(ALL, "Slow and steady, flame stays ready!", clip="Cheer with Both Hands", cam="balcony_wide")
say("himank", "Everybody wins the Diya Relay. And I am hungry for laddoos.", clip="Hand on Hip Gesture", cam="close:himank")
card("wipe", 0.8, sounds=[(0.0, whoosh(), 0.7)])

# ---- 3. KITCHEN: laddoo rolling ----
scene("kitchen", "kitchen", {"vanu": [0.0, 1.35, 0, "Idle"], "aarav": [-1.2, 0.35, 0, "Idle"], "vihaan": [1.2, 0.35, 0, "Idle"],
                             "himank": [-0.6, 1.35, 0, "Idle"], "buddy": [0.6, 1.35, 0, "Idle"]}, light="morning", mood="festive")
prop("laddoo", "show", who="kitchen")
shot("kitchen_wide"); wait(1.2)
say("vanu", "Laddoo time! Roll, roll, roll it round. Like a tiny yellow moon.", clip="Scheming Hand Rub", cam="close:vanu")
for k in ("aarav", "vihaan", "himank", "buddy"): do(k, "Scheming Hand Rub", 3.5)
shot("insert:laddoos"); wait(3.0)
say("vihaan", "Mine is a square moon.", clip="Shrug", cam="close:vihaan")
say("aarav", "Mine is a triangle moon. Modern art.", clip="Talk with Right Hand Open", cam="close:aarav")
do("buddy", "Stand and Drink", 2.6, sounds=[(0.9, pop(), 0.4)], cam="close:buddy"); wait(2.0)
say("buddy", "Mmm. Quality check. Delicious.", clip="-", cam="close:buddy", emote="brows")
say("vanu", "Buddy! One laddoo now, the rest after the fireworks.", clip="Finger Wag No", cam="two:vanu:buddy")
say("mummy", "Kids! The sun is down. Wash your hands, it is cracker time on the balcony. Grown-ups only light them, remember!", clip="-", cam="kitchen_wide")
chorus(ALL, "Cracker time!", clip="Jump with Arms Open", cam="kitchen_wide")
card("wipe", 0.8, sounds=[(0.0, whoosh(), 0.7)])

# ---- 4. BALCONY NIGHT: safety rules, sparklers, anar, chakri, rockets, song ----
scene("night", "balcony_night", {"vanu": [0.0, 0.3, 0, "Idle"], "aarav": [-1.2, 0.2, 15, "Idle"], "vihaan": [1.2, 0.2, -15, "Idle"],
                                 "himank": [-2.1, -0.2, 25, "Idle"], "buddy": [2.1, -0.2, -25, "Idle"]}, light="night", mood="festive")
shot("balcony_wide"); fx.append((T + 0.3, sparkle(), 0.6)); prop("diyas", "light"); wait(1.2)
shot("insert:diyas"); wait(2.6)
say("vihaan", "The diyas are all lit! Our balcony is glowing!", clip="Jump with Arms Open", cam="close:vihaan", emote="brows")
say("vanu", "Before any cracker, the Bro Bros safety rules. Rule one?", clip="Finger Wag No", cam="close:vanu")
say("aarav", "Only grown-ups light the crackers. Kids stand back.", clip="Agree Gesture", cam="close:aarav")
say("vanu", "Rule two?", clip="-", cam="close:vanu")
say("himank", "A bucket of water and a tray of sand, always ready. Science and safety!", clip="Talk with Right Hand Open", cam="insert:bucket")
say("vanu", "Rule three?", clip="-", cam="close:vanu")
say("buddy", "Never hold a cracker in your hand, and never, ever bend over one to look.", clip="Finger Wag No", cam="close:buddy")
say("vanu", "And rule four, the most important one?", clip="-", cam="close:vanu")
chorus(ALL, "Cotton clothes, open space, and a grown-up by your side!", clip="Cheer with Both Hands", cam="balcony_wide")
say("mummy", "Perfect! Sparklers first. I will light them, you hold them out, far from your face and from each other.", clip="-", cam="balcony_wide")
fx.append((T + 0.3, crackle(9.0, 0.3), 1.0)); prop("sparkler", "on", whos=ALL, dur=9.0)
shot("low_wide"); wait(1.0)
for k in ALL: do(k, "Happy Sway Standing", 3.0)
say("vihaan", "Whee! I am writing my name in the air! V... I... H...", clip="Happy Sway Standing", cam="close:vihaan", emote="brows")
say("buddy", "Mine is a star! A sparkly star!", clip="Happy Sway Standing", cam="close:buddy")
shot("dance_orbit"); wait(2.4)
prop("sparkler", "off", whos=ALL)
say("himank", "Sparklers done. Into the water bucket, so they cool down.", clip="Agree Gesture", cam="insert:bucket")
say("mummy", "Now the anar. Everybody behind the line. Three, two, one!", clip="-", cam="balcony_wide")
for k in ALL: move(k, [k and {"vanu": 0.0, "aarav": -1.2, "vihaan": 1.2, "himank": -2.1, "buddy": 2.1}[k], -1.6], 1.4, clip="Walking")
wait(1.6)
fx.append((T + 0.2, fountain(4.0, 0.35), 1.0)); prop("anar", "fire", dur=3.6)
shot("insert:anar"); wait(1.6); shot("balcony_wide"); wait(1.4)
chorus(ALL, "Oooooh!", clip="Look Around Dumbfounded", cam="low_wide")
say("vihaan", "It's a golden fountain! A volcano of sparkles!", clip="Jump with Arms Open", cam="close:vihaan", emote="brows")
say("mummy", "Chakri next. Watch it spin!", clip="-", cam="balcony_wide")
fx.append((T + 0.2, whirr(3.4), 1.0)); prop("chakri", "spin", dur=3.2)
shot("insert:chakri"); wait(1.8); shot("low_wide"); wait(1.6)
say("himank", "Round and round! The sparks push it, like a tiny jet engine!", clip="Talk Passionately", cam="close:himank")
say("aarav", "Science even on Diwali. Classic Himank.", clip="Shrug", cam="two:aarav:himank")
say("mummy", "And now, the rockets! Everyone look up!", clip="-", cam="balcony_wide")
for i, col_ in enumerate(("red", "green", "gold")):
    fx.append((T + 0.2, rocket_sfx(1.3, 0.5), 1.0)); prop("rocket", "launch", idx=i, colour=col_)
    shot("insert:sky" if i != 1 else "low_wide"); wait(2.9)
    chorus(ALL, ("Wooow!", "Aaaah!", "Happy Diwali!")[i], clip=("Cheer with Both Hands", "Jump with Arms Open", "Victory Cheer")[i], cam="balcony_wide" if i != 2 else "dance_orbit", gap=0.2)
for j in range(6): fx.append((T + 0.5 + j * 0.9, far_boom(0.16), 1.0))
prop("city", "fireworks", dur=7.0)
say("vanu", "Look! The whole city is celebrating with us!", clip="Talk with Right Hand Open", cam="insert:city", emote="brows")
shot("insert:city"); wait(2.6)
say("buddy", "Diwali is the best day ever. Even better than laddoo day.", clip="Happy Jump Male", cam="close:buddy")
say("vanu", "Time for the Diwali song! Everybody dance!", clip="Cheer with Both Hands", cam="balcony_wide")
prop("city", "fireworks", dur=14.0)
chorus(ALL, "Light a diya, light a smile, Diwali night is here a while!", clip="Joyful Dance with Hand Sway", cam="dance_orbit")
for k in ALL: do(k, "Joyful Dance with Hand Sway" if k in ("vanu", "aarav") else "Funny Dancing 1", 4.0)
wait(2.0); shot("low_wide"); wait(2.0)
chorus(ALL, "Sparkle, sparkle, safe and bright, grown-ups light and we stand right!", clip="Happy Sway Standing", cam="balcony_wide")
for k in ALL: do(k, "Funny Dancing 1" if k in ("vanu", "aarav") else "Joyful Dance with Hand Sway", 4.0)
wait(2.0); shot("dance_orbit"); wait(2.0)
chorus(ALL, "Happy Diwali, everyone!", clip="Victory Cheer", cam="balcony_wide")
for i in range(3):
    fx.append((T + 0.1 + i * 0.7, rocket_sfx(1.0, 0.35), 1.0)); prop("rocket", "launch", idx=3 + i, colour=("gold", "red", "green")[i])
wait(1.0); shot("insert:sky"); wait(2.6)
say("vanu", "Bye bye friends! Stay safe, stay bright, and ask a grown-up to subscribe to Bro Bros Fun!", clip="Big Wave Hello", cam="balcony_wide")
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
segs = moods + [(TOTAL, None)]
for (t0, m), (t1, _) in zip(segs, segs[1:]):
    if t1 - t0 < 0.5: continue
    mm = music(t1 - t0 + 0.5, m, bpm=124)
    p = int(t0 * SR); L = min(len(mm), n - p); mus[p:p + L] += mm[:L]
envv = np.convolve(np.abs(mixv), np.ones(4800) / 4800, mode="same")
duck = 1 - 0.6 * np.clip(envv / 0.03, 0, 1)
out = mixv * 1.0 + mixf * 0.9 + mus * 0.30 * duck
out = out / max(1e-6, np.abs(out).max()) * 0.92
sf.write(f"{OUT}/audio.wav", out, SR); sf.write(f"{OUT}/voice.wav", mixv, SR)
json.dump({"total": TOTAL, "scenes": scenes, "events": ev, "shots": shots}, open(f"{OUT}/timeline.json", "w"), indent=1)
