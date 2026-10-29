"""Episode 2: The Lunchbox Swap Mystery. Builds timeline.json (scenes, cast, events, shots) and audio.wav for the eng2 (Meshy rig) pipeline.
Yaw: 0 = facing camera side (-Y). Clips are Meshy preset motion names."""
import json, numpy as np, soundfile as sf, os, sys
sys.path.insert(0, "/home/claude/bbf")
from engine import tts, sfx, music, tone, noise, SR, VOICES

VOICES.update({"vanu": ("af_heart", 2, 1.0), "aarav": ("am_puck", 4, 1.05), "vihaan": ("af_jessica", 4, 1.08),
               "himank": ("am_echo", 5, 1.05), "buddy": ("af_kore", 3, 1.08)})
OUT = "/mnt/user-data/outputs/ep02"; os.makedirs(OUT, exist_ok=True)
T = 0.0; ev = []; shots = []; voice = []; fx = []; scenes = []; moods = []

TALK = ["Talk with Right Hand Open", "Talk Passionately", "Talk with Left Hand on Hip", "Agree Gesture"]
_tk = {}
def scene(name, set_, cast, light="day", mood="happy"):
    if scenes: scenes[-1]["t1"] = round(T, 3)
    scenes.append({"name": name, "set": set_, "t0": round(T, 3), "cast": cast, "light": light})
    moods.append((T, mood))
def shot(s):
    shots.append((round(T, 3), s))
def say(who, text, clip=None, cam=None, gap=0.3, look=None):
    """clip=None -> rotating talk gesture (standing). clip='-' -> no body clip (keep current, e.g. seated)"""
    global T
    if cam: shot(cam)
    if clip is None:
        i = _tk.get(who, 0); clip = TALK[i % 2] if who != "vanu" else TALK[(i % 2) + 1 if i % 3 else 0]; _tk[who] = i + 1
    a = tts(who, text); d = len(a) / SR
    voice.append((T + 0.05, a))
    ev.append({"t": round(T, 3), "type": "say", "who": who, "text": text, "dur": round(d, 3), "clip": clip, "look": look})
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
    if steps_sfx: fx.append((T, steps(dur, 7 if "Run" in clip or "Sprint" in clip else 3.6), 0.6))
def turn(who, yaw, dur=0.5):
    ev.append({"t": round(T, 3), "type": "turn", "who": who, "yaw": yaw, "dur": dur})
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
def bell(d, f=1500, vol=0.22):
    n = int(d * SR); t = np.arange(n) / SR
    hammer = (np.sin(2 * np.pi * 18 * t) > 0).astype(np.float32)
    ring = np.sin(2 * np.pi * f * t) + 0.6 * np.sin(2 * np.pi * f * 1.48 * t) + 0.3 * np.sin(2 * np.pi * f * 2.1 * t)
    e = np.minimum(1, t * 30) * np.minimum(1, (d - t) * 20)
    return (ring * (0.35 + 0.65 * hammer) * e * vol).astype(np.float32)
def engine_hum(d):
    n = int(d * SR); t = np.arange(n) / SR
    return ((np.sin(2 * np.pi * 48 * t) * 0.5 + np.sin(2 * np.pi * 96 * t) * 0.25) * 0.10 + noise(d, 0.05, r=0.3, lp=400)[:n]).astype(np.float32)
def clank(): return (tone(880, 0.25, "square", 0.10, r=0.2) + tone(1320, 0.25, "sine", 0.08, r=0.2)).astype(np.float32)
def thump(): return tone(lambda t: 90 - 60 * t, 0.35, "sine", 0.5, r=0.3)
def sniff():
    return np.concatenate([noise(0.12, 0.12, r=0.05, lp=3000), np.zeros(1200, np.float32), noise(0.12, 0.12, r=0.05, lp=3000), np.zeros(1200, np.float32), noise(0.25, 0.14, r=0.1, lp=3000)])
def crunch(): return noise(0.5, 0.18, r=0.1, lp=2500)
def chatter(d): return noise(d, 0.05, r=0.5, lp=1200)
def suspense(d):
    n = int(d * SR); t = np.arange(n) / SR; out = np.zeros(n, np.float32)
    for k, f in enumerate([220, 233, 220, 196]):
        s = tone(f, d / 4, "triangle", 0.10, r=0.1); p = int(k * d / 4 * SR); out[p:p + len(s)] += s[:n - p]
    return out
whoosh = lambda: sfx("whoosh"); boing = lambda: sfx("boing"); pop = lambda: sfx("pop"); ding = lambda: sfx("ding"); tada = lambda: sfx("tada")

# ================= SCRIPT =================
# ---- 1. KITCHEN, morning: packing the lunchboxes ----
scene("kitchen", "kitchen", {"vanu": [0.0, 1.05, 0, "Idle"], "aarav": [-1.15, 0.15, -60, "Idle"], "vihaan": [1.15, 0.2, 60, "Idle"],
                             "himank": [-3.4, 0.6, 90, "Idle"]}, light="morning", mood="happy")
card("intro", 3.2, sounds=[(0.2, tada(), 0.8)], cam="kitchen_wide")
say("vanu", "Good morning, team! Lunchbox time! Five tiffins, five names, zero confusion.", cam="close:vanu")
prop("tiffins", "show", sounds=[(0.1, clank(), 0.5)])
shot("insert:table")
say("vanu", "Aloo paratha for Aarav. Noodles for Vihaan. Cheese sandwich for Himank.", clip="-")
say("vanu", "Idli for me. And for Buddy, his nani's special laddoos!", clip="Agree Gesture", cam="close:vanu")
say("aarav", "Laddoos? Buddy is going to be the happiest kid in school.", cam="two:aarav:vanu")
say("vihaan", "Didi, I want laddoos too!", clip="Happy Jump Male", cam="close:vihaan")
do("vihaan", "Happy Jump Male", 1.6, sounds=[(0.3, boing(), 0.6)])
say("vanu", "Noodles, Vihaan. You begged for noodles yesterday.", clip="Finger Wag No", cam="two:vanu:vihaan")
say("vanu", "Now, name stickers on every box. Like this.", cam="insert:table")
prop("stickers", "stick", sounds=[(0.2, pop(), 0.6), (0.6, pop(), 0.6), (1.0, pop(), 0.6), (1.4, pop(), 0.6), (1.8, pop(), 0.6)])
wait(2.4)
move("himank", [-1.4, -0.9], 2.6, yaw=-20)
say("himank", "Hello hello! Detective Himank reporting for breakfast!", clip="Big Wave Hello", cam="kitchen_wide")
say("aarav", "You're not a detective, Himank. You just have new glasses.", clip="Hand on Hip Gesture", cam="two:aarav:himank")
say("himank", "A detective sees everything. For example... Vihaan has jam on his nose.", cam="close:himank")
do("vihaan", "Confused Scratch", 2.4, cam="close:vihaan")
wait(1.4); prop("jam", "hide", who="vihaan")
say("vihaan", "That's not jam. That's... decoration.", clip="Shrug", cam="close:vihaan")
do("himank", "Agree Gesture", 2.0)
# Buddy arrives in a rush
prop("door", "open", sounds=[(0.0, whoosh(), 0.6)])
scene("kitchen_buddy", "kitchen", {"vanu": [0.0, 1.05, 0, "Idle"], "aarav": [-1.15, 0.15, -60, "Idle"], "vihaan": [1.15, 0.2, 60, "Idle"],
                                   "himank": [-1.4, -0.9, -20, "Idle"], "buddy": [-4.2, 0.4, 90, "Idle"]}, light="morning", mood="funny")
move("buddy", [-2.0, 0.2], 1.3, clip="Running", yaw=90)
do("buddy", "Sprint and Sudden Stop", 1.6, cam="kitchen_wide")
wait(1.5)
say("buddy", "Bus! The bus is coming! Grab your boxes, fast fast fast!", clip="Talk Passionately", cam="close:buddy")
prop("stickers", "fall", sounds=[(0.1, whoosh(), 0.5)])
do("aarav", "Male Bend Over Pick Up", 2.2); do("vihaan", "Male Bend Over Pick Up", 2.2); do("himank", "Collect Object", 2.2); do("buddy", "Collect Object", 2.2)
shot("kitchen_wide"); wait(0.4); prop("tiffins", "grab_random"); wait(2.0)
say("vanu", "Wait! The stickers! They fell off!", clip="Stand Talking Angry", cam="close:vanu")
for k, p in (("aarav", [-4.2, 0.2]), ("vihaan", [-4.2, 0.6]), ("himank", [-4.2, -0.2]), ("buddy", [-4.4, 0.4])):
    move(k, p, 2.0, clip="Running", yaw=90)
shot("kitchen_wide"); wait(1.0)
say("vanu", "Oh no. This is going to be a disaster.", clip="Headache Relief", cam="close:vanu")
do("vanu", "Headache Relief", 1.2, block=True)
card("wipe", 0.8, sounds=[(0.0, whoosh(), 0.7)])

# ---- 2. SCHOOL BUS: the big bump ----
scene("bus", "bus", {"aarav": [-0.38, 0.0, 0, "Chair Sit Idle Male"], "vihaan": [0.38, 0.0, 0, "Chair Sit Idle Male"],
                     "vanu": [-0.38, 1.1, 0, "Chair Sit Idle Male"], "himank": [0.38, 1.1, 0, "Chair Sit Idle Male"],
                     "buddy": [0.38, 2.2, 0, "Chair Sit Idle Male"]}, light="day", mood="happy")
fx.append((T, engine_hum(36), 0.6))
shot("bus_wide"); wait(2.0)
say("himank", "Everyone hold your tiffins tight. I sense... danger.", clip="-", cam="close:himank")
say("aarav", "The only danger is you talking all the way to school.", clip="-", cam="close:aarav")
say("buddy", "I'm so hungry. I could eat a whole bus.", clip="-", cam="close:buddy")
say("vanu", "Buddy, school hasn't even started!", clip="-", cam="two:vanu:himank")
prop("bus", "bump", sounds=[(0.0, thump(), 1.0), (0.2, boing(), 0.7), (0.4, clank(), 0.6), (0.7, clank(), 0.5)])
for k in ("aarav", "vihaan", "vanu", "himank", "buddy"):
    do(k, "Sit Hands on Head Lean Back", 2.6)
shot("bus_wide"); prop("tiffins", "fly"); wait(2.8)
chorus(["aarav", "vihaan", "vanu", "himank"], "Whoaaa!", clip="-", cam="bus_wide")
say("vihaan", "My tiffin flew! It flew like a bird!", clip="-", cam="close:vihaan")
say("vanu", "Everyone, pick up a box. Any box. We'll sort it out at lunch.", clip="-", cam="close:vanu")
prop("tiffins", "settle")
do("buddy", "Sit and Drink", 3.0, cam="close:buddy", sounds=[(0.8, crunch(), 0.5), (1.9, crunch(), 0.5)])
wait(3.0)
say("buddy", "Mmm... nothing. Totally nothing. Just... practising chewing.", clip="-", cam="close:buddy")
do("vihaan", "Short Breathe and Look Around", 2.6, sounds=[(0.3, sniff(), 0.8)], cam="close:vihaan"); wait(2.0)
say("vihaan", "Sniff sniff. Why does the bus smell like laddoos?", clip="-")
card("wipe", 0.8, sounds=[(0.0, whoosh(), 0.7)])

# ---- 3. CLASSROOM: lunch bell, the swap revealed ----
scene("classroom", "classroom", {"aarav": [-1.1, 0.0, 0, "Chair Sit Idle Male"], "vihaan": [1.1, 0.0, 0, "Chair Sit Idle Male"],
                                 "vanu": [-1.1, 1.6, 0, "Chair Sit Idle Male"], "himank": [1.1, 1.6, 0, "Chair Sit Idle Male"],
                                 "buddy": [0.0, 3.0, 0, "Chair Sit Idle Male"]}, light="day", mood="happy")
fx.append((T + 0.3, bell(2.5), 0.9))
shot("class_wide"); wait(2.8)
chorus(["aarav", "vihaan", "himank"], "Lunch time!", clip="Seated Fist Pump", cam="class_wide")
prop("tiffins", "open", sounds=[(0.0, clank(), 0.4), (0.3, clank(), 0.4), (0.6, clank(), 0.4), (0.9, clank(), 0.4)])
wait(1.4)
say("aarav", "Idli? I don't have paratha. I have Didi's idli!", clip="Sitting Answering Questions", cam="close:aarav")
say("vanu", "And I have... noodles?", clip="-", cam="close:vanu")
say("vihaan", "My noodles! Didi, you have my noodles!", clip="Sit Shout Hands on Mouth", cam="close:vihaan")
say("himank", "I have a paratha. A very delicious... wrong paratha.", clip="-", cam="close:himank")
say("vihaan", "And I got a cheese sandwich. Hmm. Actually, not bad.", clip="Sit Thumbs Up Right", cam="close:vihaan")
shot("close:buddy")
do("buddy", "Sit Hands on Head Lean Back", 2.8, sounds=[(0.2, sfx("boing"), 0.4)])
say("buddy", "My box is EMPTY! Somebody stole my nani's laddoos!", clip="Sit Hands on Head Lean Back", cam="close:buddy")
prop("empty_box", "show"); shot("insert:buddy_box"); wait(2.2)
fx.append((T, suspense(3.0), 0.9))
chorus(["aarav", "vihaan", "vanu"], "Gasp!", clip="-", cam="class_wide")
wait(1.0)
# Himank takes the case
move("himank", [1.7, 0.9], 1.6, clip="Sit to Stand Transition Male", steps_sfx=False); wait(1.8)
prop("magnifier", "attach", who="himank", bone="RightHand", sounds=[(0.0, sfx("tada"), 0.6)])
say("himank", "Stand back, everyone. This is a job for Detective Himank!", clip="Hand on Hip Gesture", cam="close:himank")
say("aarav", "Here we go again.", clip="-", cam="close:aarav")
do("himank", "Walk Slowly and Look Around", 4.0, cam="class_wide")
move("himank", [0.2, 2.4], 4.0, clip="Walk Slowly and Look Around", yaw=170); wait(4.2)
say("himank", "Aha! Clue number one. Crumbs! Yellow, sweet, round crumbs.", clip="Thoughtful Walk", cam="insert:crumbs")
say("vanu", "Laddoo crumbs! The thief left a trail!", clip="-", cam="close:vanu")
say("himank", "The trail goes... out of the door. Towards the canteen. Follow me!", clip="Talk Passionately", cam="close:himank")
for k, p in (("himank", [-4.4, -0.8]),):
    move(k, p, 2.6, clip="Sneaky Walk", yaw=-110)
shot("class_wide"); wait(1.2)
chorus(["aarav", "vihaan", "vanu", "buddy"], "Follow the crumbs!", clip="-", cam="class_wide")
card("wipe", 0.8, sounds=[(0.0, whoosh(), 0.7)])

# ---- 4. CORRIDOR / CANTEEN chase ----
scene("canteen", "canteen", {"himank": [-4.0, -0.6, -90, "Sneaky Walk"], "aarav": [-5.0, -0.2, -90, "Idle"], "vihaan": [-5.6, -0.8, -90, "Idle"],
                             "vanu": [-6.2, -0.3, -90, "Idle"], "buddy": [-6.8, -0.7, -90, "Idle"]}, light="day", mood="mystery")
fx.append((T, suspense(4.0), 0.8))
move("himank", [-1.6, -0.6], 4.0, clip="Sneaky Walk", yaw=-90)
move("aarav", [-2.6, -0.2], 4.0, clip="Sneaky Walk", yaw=-90)
move("vihaan", [-3.2, -0.9], 4.0, clip="Sneaky Walk", yaw=-90)
move("vanu", [-3.8, -0.3], 4.0, clip="Sneaky Walk", yaw=-90)
move("buddy", [-4.4, -0.7], 4.0, clip="Sneaky Walk", yaw=-90)
shot("canteen_wide"); wait(4.2)
say("himank", "The crumbs get bigger here. We are close. Very close.", clip="Thoughtful Walk", cam="close:himank")
say("vihaan", "Is it a ghost? A laddoo ghost?", clip="Look Around Dumbfounded", cam="close:vihaan")
say("aarav", "Ghosts don't eat laddoos, Vihaan.", cam="two:aarav:vihaan")
say("vihaan", "How do you know? Have you asked one?", clip="Shrug", cam="close:vihaan")
say("himank", "Suspect number one: the canteen cat.", clip="Talk with Right Hand Open", cam="insert:cat")
prop("cat", "meow", sounds=[(0.1, tone(lambda t: 700 + 300 * np.sin(6 * t), 0.5, "sine", 0.15), 0.8)])
wait(1.0)
say("vanu", "Cats don't like laddoos. Next suspect.", clip="Hand on Hip Gesture", cam="close:vanu")
say("himank", "The trail stops... right here. Under the table. And the thief is...", clip="Thoughtful Walk", cam="insert:under_table")
fx.append((T, suspense(2.2), 1.0)); wait(2.2)
move("buddy", [0.9, 0.9], 2.0, clip="Walking", yaw=0); wait(0.3)
say("himank", "Wait. The trail goes in a circle. It goes to... Buddy's shoes.", clip="-", cam="insert:buddy_shoes")
chorus(["aarav", "vihaan", "vanu", "himank"], "BUDDY?!", clip="-", cam="canteen_wide")
prop("crumb_face", "show", who="buddy")
say("buddy", "Me? No way! I would never... ", clip="Finger Wag No", cam="close:buddy")
say("himank", "Then why do you have laddoo crumbs on your face?", clip="Talk with Right Hand Open", cam="two:himank:buddy")
do("buddy", "Confused Scratch", 2.4, cam="close:buddy"); wait(2.4)
say("buddy", "Ohhh. The big bump on the bus! My box flew open... into my mouth. I ate them all. Then I forgot!", clip="Talk Passionately", cam="close:buddy")
say("buddy", "I'm sorry, everyone. I was SO hungry.", clip="Shrug", cam="close:buddy")
do("aarav", "Happy Sway Standing", 3.0); do("vihaan", "Happy Jump Male", 2.0, sounds=[(0.3, boing(), 0.5)]); do("vanu", "Happy Sway Standing", 3.0)
say("vanu", "Buddy, you are the thief AND the victim. Case closed!", clip="Agree Gesture", cam="canteen_wide")
do("himank", "Victory Cheer", 2.6)
say("himank", "Detective Himank solves another case!", clip="Victory Cheer", cam="close:himank")
say("aarav", "You solved one case, Himank. This one.", clip="Hand on Hip Gesture", cam="two:aarav:himank")

# ---- 5. CANTEEN: share party ----
scene("share", "canteen", {"vanu": [0.0, 1.35, 0, "Idle"], "aarav": [-1.1, 1.3, 20, "Idle"], "vihaan": [1.1, 1.3, -20, "Idle"],
                           "himank": [-1.9, 0.7, 40, "Idle"], "buddy": [1.9, 0.7, -40, "Idle"]}, light="day", mood="happy")
prop("share_table", "show")
say("vanu", "New rule. Today we share everything. Paratha, noodles, idli, sandwich.", clip="Talk with Left Hand on Hip", cam="share_wide")
say("vihaan", "And Buddy shares... crumbs!", clip="Happy Jump Male", cam="close:vihaan")
do("vihaan", "Happy Jump Male", 1.6, sounds=[(0.3, boing(), 0.5)])
do("buddy", "Stand and Drink", 3.0, cam="close:buddy", sounds=[(1.0, crunch(), 0.5)]); prop("food", "attach", who="buddy", bone="RightHand"); wait(3.0)
say("buddy", "This paratha is amazing! Sharing is the best!", clip="Sitting Clap" if False else "Cheer with Both Hands", cam="close:buddy")
say("aarav", "And tomorrow, stickers with super glue!", clip="Agree Gesture", cam="close:aarav")
say("himank", "And I will guard the tiffins. Detective style.", clip="Hand on Hip Gesture", cam="close:himank")
chorus(["aarav", "vihaan", "vanu", "himank", "buddy"], "Sharing is caring!", clip="Cheer with Both Hands", cam="share_wide")
for k in ("aarav", "vihaan", "vanu", "himank", "buddy"):
    do(k, "Funny Dancing 1" if k in ("vihaan", "buddy", "himank") else "Joyful Dance with Hand Sway", 8.0)
shot("share_wide"); fx.append((T, tada(), 0.5)); wait(4.0); shot("dance_orbit"); wait(4.0)
say("vanu", "Bye bye friends! Don't forget to subscribe to Bro Bros Fun!", clip="Big Wave Hello", cam="share_wide")
for k in ("aarav", "vihaan", "himank", "buddy"):
    do(k, "Big Wave Hello", 3.0)
wait(0.5)
card("endcard", 6.0, sounds=[(0.2, tada(), 0.7)])
scenes[-1]["t1"] = round(T, 3)
TOTAL = T
print("TOTAL", round(TOTAL, 1), "events", len(ev), "shots", len(shots))

# ---------- mix ----------
n = int((TOTAL + 1) * SR); mixv = np.zeros(n, np.float32); mixf = np.zeros(n, np.float32)
for t0, a in voice:
    p = int(t0 * SR); mixv[p:p + len(a)] += a[:n - p]
for t0, a, g in fx:
    p = int(t0 * SR); mixf[p:p + len(a)] += (a * g)[:n - p]
mus = np.zeros(n, np.float32)
segs = moods + [(TOTAL, None)]
for (t0, m), (t1, _) in zip(segs, segs[1:]):
    if t1 - t0 < 0.5: continue
    mm = music(t1 - t0 + 0.5, m if m in ("happy", "funny", "mystery", "night") else "happy")
    p = int(t0 * SR); L = min(len(mm), n - p); mus[p:p + L] += mm[:L]
# duck music under voice
envv = np.convolve(np.abs(mixv), np.ones(4800) / 4800, mode="same")
duck = 1 - 0.6 * np.clip(envv / 0.03, 0, 1)
out = mixv * 1.0 + mixf * 0.9 + mus * 0.32 * duck
out = out / max(1e-6, np.abs(out).max()) * 0.92
sf.write(f"{OUT}/audio.wav", out, SR)
json.dump({"total": TOTAL, "scenes": scenes, "events": ev, "shots": shots}, open(f"{OUT}/timeline.json", "w"), indent=1)
