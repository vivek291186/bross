"""Episode 6: Guess the Sound Challenge! Builds timeline.json + audio.wav for build6 + props_ep6.
Scenes: living room game (mystery sound box) -> balcony "sound walk" -> kitchen sounds round -> living room song + winner."""
import json, numpy as np, soundfile as sf, os, sys
sys.path.insert(0, "/home/claude/bbf")
from engine import tts, sfx, music, tone, noise, SR, VOICES

VOICES.update({"vanu": ("af_heart", 2, 1.0), "aarav": ("am_puck", 4, 1.05), "vihaan": ("af_jessica", 4, 1.08),
               "himank": ("am_echo", 5, 1.05), "buddy": ("af_kore", 3, 1.08)})
OUT = "/mnt/user-data/outputs/ep06"; os.makedirs(OUT, exist_ok=True)
T = 0.0; ev = []; shots = []; voice = []; fx = []; scenes = []; moods = []
ALL = ["vanu", "aarav", "vihaan", "himank", "buddy"]
TALK = ["Talk with Right Hand Open", "Talk Passionately", "Talk with Left Hand on Hip", "Agree Gesture"]
_tk = {}
def scene(name, set_, cast, light="day", mood="happy"):
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
def cat_(*xs): return np.concatenate(xs).astype(np.float32)
def steps(d, rate):
    out = np.zeros(int(d * SR) + 10, np.float32)
    for k in range(int(d * rate)):
        p = int(k / rate * SR); s = tone(lambda t: 150 - 200 * t, 0.06, "sine", 0.14, r=0.03); out[p:p + len(s)] += s[:len(out) - p]
    return out
whoosh = lambda: sfx("whoosh"); boing = lambda: sfx("boing"); pop = lambda: sfx("pop"); ding = lambda: sfx("ding"); tada = lambda: sfx("tada")
sparkle = lambda: sfx("sparkle"); cheer = lambda: sfx("cheer"); drumroll = lambda: sfx("drumroll"); buzz = lambda: sfx("buzz")
def silence(d): return np.zeros(int(d * SR), np.float32)
def doorbell():
    return cat_(tone(659, 0.45, "sine", 0.35, r=0.5), tone(523, 0.7, "sine", 0.35, r=0.7))
def meow():
    return tone(lambda t: 520 + 260 * np.sin(np.pi * t / 0.7) - 150 * t, 0.7, "saw", 0.16, a=0.05, r=0.5)
def dog():
    b = tone(lambda t: 420 - 300 * t, 0.16, "saw", 0.35, a=0.005, r=0.08)
    return cat_(b, silence(0.14), b, silence(0.5), b)
def rain(d=2.4):
    n = int(d * SR); t = np.arange(n) / SR
    env = np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.6)
    out = noise(d, 0.5, r=0.3, lp=7000)[:n] * env * 0.6
    rng = np.random.default_rng(6)
    for p in rng.integers(0, n - 300, int(d * 40)):
        out[p:p + 200] += tone(lambda t: 3000, 0.004, "sine", 0.08, r=0.004)[:200] if False else (rng.random(200) - 0.5) * 0.25 * np.exp(-np.arange(200) / 40)
    return out.astype(np.float32)
def thunder(): return sfx("thunder")
def horn():
    return cat_(tone(lambda t: 392 + 0 * t, 0.35, "square", 0.22, r=0.4) + tone(494, 0.35, "square", 0.18, r=0.4), silence(0.12), tone(392, 0.5, "square", 0.22, r=0.5) + tone(494, 0.5, "square", 0.18, r=0.5))
def clapping(d=1.6):
    out = np.zeros(int(d * SR) + 2000, np.float32); rng = np.random.default_rng(2)
    for k in range(int(d * 9)):
        p = int(k / 9 * SR + rng.integers(-800, 800)); s = (rng.random(1400) - 0.5) * np.exp(-np.arange(1400) / 250) * 0.9
        out[p:p + 1400] += s.astype(np.float32)
    return out
def popcorn(d=2.0):
    out = np.zeros(int(d * SR) + 4000, np.float32); rng = np.random.default_rng(9)
    for p in rng.integers(0, int(d * SR), int(d * 7)):
        s = tone(lambda t: 900 - 600 * t, 0.05, "sine", 0.3, r=0.02); out[p:p + len(s)] += s
    return out
def cooker_whistle():
    n = int(1.4 * SR); t = np.arange(n) / SR
    f = 1500 + 300 * np.minimum(1, t / 0.5); env = np.minimum(1, t / 0.3) * np.minimum(1, (1.4 - t) / 0.3)
    return ((np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3 + noise(1.4, 0.4, r=0.1, lp=9000)[:n] * 0.6) * env * 0.5).astype(np.float32)
def sizzle(d=2.0):
    n = int(d * SR); t = np.arange(n) / SR
    return (noise(d, 0.5, r=0.2, lp=8000)[:n] * (0.5 + 0.5 * np.abs(np.sin(t * 9))) * np.minimum(1, (d - t) / 0.5) * 0.45).astype(np.float32)
def pouring(d=1.6):
    n = int(d * SR); t = np.arange(n) / SR
    f = 300 + 500 * t / d
    return ((noise(d, 0.5, r=0.2, lp=3000)[:n] * 0.6 + np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.15) * np.minimum(1, t / 0.2) * np.minimum(1, (d - t) / 0.3) * 0.45).astype(np.float32)
def birds():
    out = []
    for f0, f1 in ((2400, 3200), (3000, 2200), (2600, 3400), (3100, 2500)):
        out += [tone(lambda t, a=f0, b=f1: a + (b - a) * t / 0.12, 0.12, "sine", 0.18, a=0.01, r=0.1), silence(0.08)]
    return cat_(*out)
def temple_bell():
    n = int(2.2 * SR); t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * t) * a * np.exp(-t * d) for f, a, d in ((660, 0.35, 1.2), (1320, 0.2, 2.0), (1980, 0.1, 3.0), (2640, 0.06, 4.0)))
    return (s * 0.5).astype(np.float32)
def drum():
    out = []
    for k in range(6):
        out += [tone(lambda t: 180 - 120 * t, 0.18, "sine", 0.6, a=0.002, r=0.12), silence(0.07 if k % 3 == 2 else 0.17)]
    return cat_(*out)
def laugh(): return sfx("cheer")

# ================= SCRIPT =================
# ---- 1. LIVING ROOM: the mystery sound box ----
scene("game", "living", {"vanu": [0.0, 1.5, 0, "Idle"], "aarav": [-1.4, 0.4, 20, "Idle"], "vihaan": [1.4, 0.4, -20, "Idle"],
                         "himank": [-2.2, 0.9, 30, "Idle"], "buddy": [2.2, 0.9, -30, "Idle"]}, light="day", mood="happy")
card("intro", 3.4, sounds=[(0.2, tada(), 0.8), (0.6, sparkle(), 0.6)], cam="living_wide")
prop("box", "show", sounds=[(0.2, pop(), 0.5)])
shot("insert:box"); wait(1.6)
say("vanu", "Bro Bros, welcome to the Guess the Sound Challenge! Inside this mystery box is a secret sound. Close your eyes, open your ears!", clip="Talk with Hands Open", cam="living_wide", emote="brows")
say("vihaan", "Ears open! Eyes closed! Hmm, I can hear my own tummy.", clip="Look Around Dumbfounded", cam="close:vihaan", emote="brows")
say("aarav", "Rules! One point for the right guess. No peeking, no shouting, and no guessing 'elephant' every time, Vihaan.", clip="Finger Wag No", cam="close:aarav")
say("vihaan", "I only did that twice.", clip="Shrug", cam="close:vihaan")
say("vanu", "Round one! Listen carefully.", clip="Talk with Right Hand Open", cam="living_wide")
# Round 1: doorbell
prop("box", "play", sound="bell", sounds=[(0.2, drumroll(), 0.5), (1.3, doorbell(), 0.9)]); shot("insert:box"); wait(3.2)
say("buddy", "Ding dong! That's the doorbell! Somebody is at the door!", clip="Hop with Arms Raised", cam="close:buddy", emote="brows")
prop("box", "reveal", sound="bell", sounds=[(0.1, ding(), 0.6)]); shot("insert:box"); wait(1.6)
say("vanu", "Correct! Doorbell. One point for Buddy!", clip="Cheer with Both Hands", cam="close:vanu")
prop("score", "set", buddy=1, sounds=[(0.0, pop(), 0.5)]); shot("insert:score"); wait(1.4)
say("himank", "Fun fact! The first doorbell was invented over a hundred and ninety years ago. Before that, people just knocked!", clip="Talk Passionately", cam="close:himank", emote="brows")
# Round 2: cat
say("vanu", "Round two. Shhh.", clip="Talk with Left Hand on Hip", cam="living_wide")
prop("box", "play", sound="cat", sounds=[(0.2, drumroll(), 0.5), (1.3, meow(), 0.9), (2.2, meow(), 0.8)]); shot("insert:box"); wait(3.4)
say("vihaan", "Elephant!", clip="Jump with Arms Open", cam="close:vihaan", emote="brows")
fx.append((T - 0.1, buzz(), 0.6))
say("aarav", "Vihaan!", clip="Hand on Hip Gesture", cam="two:aarav:vihaan")
say("himank", "That is a cat. A hungry cat, by the sound of it.", clip="Agree Gesture", cam="close:himank")
prop("box", "reveal", sound="cat", sounds=[(0.1, ding(), 0.6)]); shot("insert:box"); wait(1.6)
say("vanu", "Cat! Point for Himank!", clip="Cheer with Both Hands", cam="close:vanu")
prop("score", "set", buddy=1, himank=1, sounds=[(0.0, pop(), 0.5)])
# Round 3: rain + thunder
say("vanu", "Round three. This one is wet.", clip="Talk with Right Hand Open", cam="living_wide", emote="brows")
prop("box", "play", sound="rain", sounds=[(0.2, drumroll(), 0.5), (1.3, rain(2.6), 0.9), (3.0, thunder(), 0.6)]); shot("insert:box"); wait(4.4)
say("buddy", "Rain! And thunder! Everybody under the umbrella!", clip="Motivational Cheer", cam="close:buddy", emote="brows")
say("aarav", "Rain, correct. And remember, when there is thunder, we stay inside. Lightning is not a game.", clip="Talk with Left Hand Raised", cam="close:aarav")
prop("box", "reveal", sound="rain", sounds=[(0.1, ding(), 0.6)]); shot("insert:box"); wait(1.6)
prop("score", "set", buddy=2, himank=1, sounds=[(0.0, pop(), 0.5)]); shot("insert:score"); wait(1.2)
# Round 4: drum -> everyone dances
say("vanu", "Round four. Feet ready!", clip="Talk with Hands Open", cam="living_wide")
prop("box", "play", sound="drum", sounds=[(0.2, drumroll(), 0.5), (1.3, drum(), 0.9)]); shot("insert:box"); wait(3.6)
chorus(ALL, "Drum! Dhol! Dance!", clip="Cheer with Both Hands Up", cam="living_wide", gap=0.1)
for k in ALL: do(k, "Hip Hop Dance" if k in ("aarav", "himank") else "FunnyDancing 02", 4.6)
fx.append((T, drum(), 0.7)); fx.append((T + 1.8, drum(), 0.7))
shot("dance_orbit"); wait(2.4); shot("low_wide" if False else "living_wide"); wait(2.4)
say("vanu", "Everybody gets a point for that dance!", clip="Cheer with Both Hands", cam="close:vanu", emote="brows")
prop("score", "set", vanu=1, aarav=1, vihaan=1, himank=2, buddy=3, sounds=[(0.0, pop(), 0.5)]); shot("insert:score"); wait(1.4)
say("vihaan", "Finally! A point! My ears are warming up now.", clip="Victory Fist Pump", cam="close:vihaan", emote="brows")
say("vanu", "Bonus round outside! Sound walk on the balcony. Quiet feet!", clip="Talk with Right Hand Open", cam="living_wide")
card("wipe", 0.8, sounds=[(0.0, whoosh(), 0.7)])

# ---- 2. BALCONY: sound walk ----
scene("walk", "balcony", {"vanu": [0.0, 0.4, 0, "Idle"], "aarav": [-1.2, 0.2, 15, "Idle"], "vihaan": [1.2, 0.2, -15, "Idle"],
                          "himank": [-2.1, -0.2, 25, "Idle"], "buddy": [2.1, -0.2, -25, "Idle"]}, light="day", mood="happy")
shot("balcony_wide"); wait(1.0)
say("vanu", "Out here the city is full of sounds. Close your eyes. What do you hear first?", clip="Talk with Hands Open", cam="close:vanu", emote="brows")
fx.append((T + 0.2, birds(), 0.8)); shot("insert:sky"); wait(2.2)
say("aarav", "Birds! Little chirpy birds on the wire.", clip="Talk with Right Hand Open", cam="close:aarav")
prop("wave", "balcony", who="aarav")
fx.append((T + 0.2, horn(), 0.7)); shot("insert:city"); wait(2.0)
say("vihaan", "A car horn. Peep peep! That is Uncle's scooter, I know that horn!", clip="Hop with Arms Raised", cam="close:vihaan", emote="brows")
fx.append((T + 0.3, temple_bell(), 0.8)); shot("insert:city"); wait(2.4)
say("himank", "A temple bell. Fun fact! A bell rings because the metal shakes super fast, and the shaking travels through the air into your ears.", clip="Talk Passionately", cam="close:himank", emote="brows")
say("buddy", "So sound is... shaky air?", clip="Confused Scratch", cam="close:buddy", emote="brows")
say("himank", "Exactly! Shaky air. Put your hand on your throat and hum. Feel it?", clip="Agree Gesture", cam="two:himank:buddy")
chorus(ALL, "Hmmmmmm!", clip="Agree Gesture", cam="balcony_wide", gap=0.2)
say("buddy", "It tickles! My neck is a drum!", clip="Jump with Arms Open", cam="close:buddy", emote="brows")
say("vanu", "Points for everyone. Now, the trickiest round of all. The kitchen!", clip="Cheer with Both Hands", cam="balcony_wide")
card("wipe", 0.8, sounds=[(0.0, whoosh(), 0.7)])

# ---- 3. KITCHEN: kitchen sounds ----
scene("kitchen", "kitchen", {"vanu": [0.0, 1.35, 0, "Idle"], "aarav": [-1.2, 0.35, 0, "Idle"], "vihaan": [1.2, 0.35, 0, "Idle"],
                             "himank": [-0.6, 1.35, 0, "Idle"], "buddy": [0.6, 1.35, 0, "Idle"]}, light="day", mood="happy")
shot("kitchen_wide"); wait(1.0)
say("vanu", "Kitchen round. Eyes closed, no peeking at the stove. Grown-ups only near the fire.", clip="Finger Wag No", cam="close:vanu")
fx.append((T + 0.2, sizzle(2.2), 0.8)); prop("steam", "pan"); shot("insert:cooker"); wait(2.6)
say("buddy", "Sizzle sizzle! Something is frying. Pakoras?", clip="Hop with Arms Raised", cam="close:buddy", emote="brows")
say("vanu", "Frying, yes! Vegetables in the pan.", clip="Agree Gesture", cam="close:vanu")
fx.append((T + 0.2, pouring(1.8), 0.8)); shot("insert:table"); wait(2.2)
say("aarav", "Pouring water. Into a glass. A tall glass!", clip="Talk with Right Hand Open", cam="close:aarav")
say("himank", "Fun fact! The sound gets higher as the glass fills up. Listen next time!", clip="Talk Passionately", cam="close:himank", emote="brows")
fx.append((T + 0.2, cooker_whistle(), 0.9)); prop("steam", "cooker"); shot("insert:cooker"); wait(2.0)
chorus(ALL, "Pressure cooker whistle!", clip="Cheer with Both Hands Up", cam="kitchen_wide", gap=0.2)
say("vihaan", "Dal is ready! That whistle means food. I never get that one wrong.", clip="Victory Fist Pump", cam="close:vihaan", emote="brows")
fx.append((T + 0.2, popcorn(2.2), 0.9)); shot("insert:cooker"); wait(2.6)
say("vihaan", "Popcorn! Pop pop pop! Final answer!", clip="Jump with Arms Open", cam="close:vihaan", emote="brows")
say("vanu", "Popcorn it is. Vihaan, two points in a row!", clip="Cheer with Both Hands", cam="close:vanu")
say("aarav", "Movie night sound. Now we need a movie.", clip="Hand on Hip Gesture", cam="close:aarav")
say("vanu", "First, the final scores. Back to the living room!", clip="Talk with Right Hand Open", cam="kitchen_wide")
card("wipe", 0.8, sounds=[(0.0, whoosh(), 0.7)])

# ---- 4. LIVING ROOM: scores + Listen Song ----
scene("finale", "living", {"vanu": [0.0, 1.5, 0, "Idle"], "aarav": [-1.4, 0.4, 20, "Idle"], "vihaan": [1.4, 0.4, -20, "Idle"],
                           "himank": [-2.2, 0.9, 30, "Idle"], "buddy": [2.2, 0.9, -30, "Idle"]}, light="day", mood="happy")
prop("box", "show"); prop("score", "set", vanu=2, aarav=3, vihaan=4, himank=4, buddy=4)
shot("living_wide"); wait(1.0)
say("vanu", "Final scores! Aarav three. Vihaan four. Himank four. Buddy... four!", clip="Talk with Hands Open", cam="insert:score", emote="brows")
fx.append((T + 0.2, drumroll(), 0.6)); shot("insert:score"); wait(1.4)
say("vanu", "It's a three way tie! Which means the winner is... everybody's ears!", clip="Cheer with Both Hands", cam="living_wide", emote="brows")
fx.append((T - 0.2, tada(), 0.8)); fx.append((T + 0.1, cheer(), 0.6)); prop("confetti", "burst")
chorus(ALL, "Hooray for ears!", clip="Cheer with Both Hands Up", cam="low_wide" if False else "living_wide")
say("vihaan", "Can the mystery box do one more sound? Please please please?", clip="Big Heart Gesture", cam="close:vihaan", emote="brows")
say("vanu", "One more. The best sound in the whole world.", clip="Scheming Hand Rub", cam="close:vanu")
prop("box", "play", sound="laugh", sounds=[(0.2, drumroll(), 0.5), (1.3, laugh(), 0.9)]); shot("insert:box"); wait(3.2)
say("buddy", "That's us! Bro Bros laughing!", clip="Hop with Arms Raised", cam="close:buddy", emote="brows")
prop("box", "reveal", sound="laugh", sounds=[(0.1, ding(), 0.6)]); shot("insert:box"); wait(1.4)
say("vanu", "Correct! Now, the Listen Song. Everybody up!", clip="Stand Clap and Sit Down", cam="living_wide")
chorus(ALL, "Listen, listen, what's that sound? Shaky air is all around!", clip="Joyful Dance with Hand Sway", cam="dance_orbit")
for k in ALL: do(k, "Joyful Dance with Hand Sway" if k in ("vanu", "aarav") else "FunnyDancing 03", 4.0)
wait(2.0); shot("living_wide"); wait(2.0)
chorus(ALL, "Ding dong, meow, pitter patter rain, close your eyes and guess again!", clip="Happy Sway Standing", cam="living_wide")
for k in ALL: do(k, "FunnyDancing 03" if k in ("vanu", "aarav") else "Joyful Dance with Hand Sway", 4.0)
fx.append((T + 0.3, doorbell(), 0.5)); fx.append((T + 1.2, meow(), 0.5)); fx.append((T + 2.0, rain(1.2), 0.5))
wait(2.0); shot("dance_orbit"); wait(2.0)
chorus(ALL, "Guess the sound!", clip="Victory Cheer", cam="living_wide")
for k in ALL: do(k, "Formal Bow", 2.6)
wait(2.6)
say("vanu", "Bye bye friends! Play Guess the Sound at home, and ask a grown-up to subscribe to Bro Bros Fun!", clip="Big Wave Hello", cam="living_wide")
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
    mm = music(t1 - t0 + 0.5, m, bpm=120)
    p = int(t0 * SR); L = min(len(mm), n - p); mus[p:p + L] += mm[:L]
envv = np.convolve(np.abs(mixv), np.ones(4800) / 4800, mode="same")
envf = np.convolve(np.abs(mixf), np.ones(4800) / 4800, mode="same")
duck = 1 - 0.6 * np.clip(envv / 0.03, 0, 1) - 0.25 * np.clip(envf / 0.05, 0, 1)
out = mixv * 1.0 + mixf * 0.9 + mus * 0.28 * np.clip(duck, 0.15, 1)
out = out / max(1e-6, np.abs(out).max()) * 0.92
sf.write(f"{OUT}/audio.wav", out, SR); sf.write(f"{OUT}/voice.wav", mixv, SR)
json.dump({"total": TOTAL, "scenes": scenes, "events": ev, "shots": shots}, open(f"{OUT}/timeline.json", "w"), indent=1)
