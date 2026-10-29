"""Diwali crackers comedy (3D): builds timeline.json (dialogue, actions, shots, blocking) and the full audio mix."""
import json, numpy as np, soundfile as sf, random
from engine import tts, sfx, music, tone, noise, env, SR, VOICES

VOICES["papa"] = ("am_michael", 0, 1.0)
OUT = "/mnt/user-data/outputs/3d2"
import os; os.makedirs(OUT, exist_ok=True)

T = 0.0
ev = []          # timeline events
shots = []       # (t, shot)
voice = []       # (t, audio)
fx = []          # (t, audio, gain)

def shot(name):
    shots.append((round(T, 3), name))

def say(who, text, gesture="talk", gap=0.35, shot_name=None):
    global T
    if shot_name: shot(shot_name)
    a = tts(who, text)
    d = len(a) / SR
    voice.append((T + 0.05, a))
    ev.append({"t": round(T, 3), "type": "say", "who": who, "text": text, "dur": round(d, 3), "gesture": gesture})
    T += d + gap

def both(text, gap=0.35, shot_name=None):
    global T
    if shot_name: shot(shot_name)
    a1, a2 = tts("big", text), tts("lil", text)
    n = max(len(a1), len(a2)); a = (np.pad(a1, (0, n - len(a1))) + np.pad(a2, (0, n - len(a2)))) * 0.7
    voice.append((T + 0.05, a))
    ev.append({"t": round(T, 3), "type": "say", "who": "both", "text": text, "dur": round(n / SR, 3), "gesture": "cheer"})
    T += n / SR + gap

def act(name, dur, sounds=(), shot_name=None, **kw):
    global T
    if shot_name: shot(shot_name)
    e = {"t": round(T, 3), "type": "act", "name": name, "dur": dur}; e.update(kw); ev.append(e)
    for at, s, g in sounds: fx.append((T + at, s, g))
    T += dur

# ---------- extra SFX ----------
def hiss(d):
    n = noise(d, 0.12, r=d * 4, lp=None); hp = n - np.convolve(n, np.ones(8) / 8, mode="same"); return hp * 2.2
def fountain(d):
    n = noise(d, 0.25, r=d * 3, lp=900) + hiss(d) * 0.5
    k = np.minimum(1, np.linspace(0, d * 3, len(n))) * np.minimum(1, np.linspace(d * 2, 0, len(n)))
    return (n * k).astype(np.float32)
def crackle(d, dens=25, vol=0.25):
    out = np.zeros(int(d * SR), np.float32); r = random.Random(3)
    for _ in range(int(d * dens)):
        p = r.randint(0, len(out) - 900); out[p:p + 800] += noise(800 / SR, vol * r.uniform(0.4, 1), r=0.01, lp=None)[:800]
    return out
def boom(vol=0.9):
    b = noise(1.8, vol, r=0.5, lp=120); b[:int(0.02 * SR)] *= 2.0
    c = crackle(1.8, 30, 0.18); return (b + np.pad(c[: len(b)], (0, max(0, len(b) - len(c))))[: len(b)]).astype(np.float32)
def whistle(d=1.4):
    return tone(lambda t: 900 + 1400 * t / d, d, "sine", 0.22, a=0.05, r=d * 2) + hiss(d) * 0.4
def phuss():
    return noise(1.1, 0.35, r=0.35, lp=2500) * np.linspace(1, 0, int(1.1 * SR)).astype(np.float32)
def whirr(d):
    n = noise(d, 0.3, r=d * 3, lp=1500); t = np.arange(len(n)) / SR
    return (n * (0.6 + 0.4 * np.sin(2 * np.pi * 14 * t))).astype(np.float32) + crackle(d, 40, 0.15)
def sparkle_loop(d): return crackle(d, 90, 0.08) + hiss(d) * 0.25
def run_steps(d, rate=7):
    out = np.zeros(int(d * SR), np.float32)
    for k in range(int(d * rate)):
        p = int(k / rate * SR); s = tone(lambda t: 160 - 200 * t, 0.06, "sine", 0.18, r=0.03); out[p:p + len(s)] += s[: len(out) - p]
    return out

# ================= SCRIPT =================
shot("wide")
act("intro_card", 3.0, sounds=[(0.2, sfx("tada"), 0.8)])
act("kids_run_in", 2.6, sounds=[(0, run_steps(2.4, 8), 0.9)], shot_name="wide")
say("lil", "Happy Diwali, everybody!", "cheer", shot_name="two_kids")
say("big", "Happy Diwali! Tonight is cracker night!", "cheer")
act("papa_walk_in", 2.2, sounds=[(0, run_steps(2.0, 3), 0.7)], shot_name="wide")
say("papa", "Okay, Bro Bros. Crackers are fun, but we have rules.", shot_name="papa_close")
say("papa", "Rule number one. Only Papa lights the crackers.", "point")
say("papa", "Rule number two. You stand behind this white line. Far away!", "point")
say("big", "Behind the line. Got it, Papa!", "salute", shot_name="big_close")
say("lil", "Can I stand behind Big Bro? He's bigger. He can protect me.", "point_big", shot_name="lil_close")
say("big", "Don't worry. I'm not scared of anything!", "hips", shot_name="big_close")

# ---- 1. Anar ----
say("papa", "First, the anar. The flower pot!", "point", shot_name="papa_close")
act("papa_light", 4.2, target="anar", sounds=[(0, run_steps(1.2, 4), 0.6), (2.2, hiss(1.6), 0.8), (2.4, run_steps(1.4, 9), 0.8)], shot_name="cracker_low")
act("lil_ears", 0.6, shot_name="two_kids")
act("anar", 6.5, sounds=[(0, fountain(6.5), 1.0), (0.8, sfx("cheer"), 0.6)], shot_name="anar_wide")
say("big", "Wow! It's like a golden fountain!", "cheer", shot_name="two_kids")
say("lil", "So pretty! It's raining gold!", "ears")
say("big", "Lil Bro, why are you covering your ears? It's not even loud!", "point_lil", shot_name="big_close")
say("lil", "I'm being prepared. Preparation is very important!", "ears", shot_name="lil_close")

# ---- 2. Dud ----
say("papa", "Next, a big bomb cracker. Everybody, cover your ears!", "point", shot_name="papa_close")
act("papa_light", 4.0, target="bomb", sounds=[(0, run_steps(1.2, 4), 0.6), (2.0, hiss(2.0), 0.9), (2.2, run_steps(1.4, 9), 0.8)], shot_name="cracker_low")
act("all_ears_wait", 4.0, sounds=[(0, hiss(3.0), 0.6)], shot_name="three_wait")
act("dud_phuss", 2.2, sounds=[(0.1, phuss(), 1.0)], shot_name="cracker_low")
say("lil", "That's it? Phusss?", "shrug", shot_name="lil_close")
say("big", "Even Lil Bro's sneeze is louder than that!", "laugh", shot_name="big_close")
say("papa", "Ha ha! That one was a sleepy cracker. Happy Diwali, little cracker!", "wave", shot_name="papa_close")

# ---- 3. Rocket ----
say("papa", "Now, the rocket! Everyone, look up at the sky!", "point_up", shot_name="papa_close")
say("big", "Rockets are easy. I am super brave.", "hips", shot_name="big_close")
act("papa_light", 3.4, target="rocket", sounds=[(0, run_steps(1.0, 4), 0.6), (1.8, hiss(1.2), 0.9), (2.0, run_steps(1.2, 9), 0.8)], shot_name="cracker_low")
act("rocket_launch", 1.6, sounds=[(0, whistle(1.5), 1.0)], shot_name="two_kids_jump")
say("lil", "Big Bro! You jumped into my arms!", "carry", gap=0.2)
act("rocket_burst", 3.2, sounds=[(0.0, boom(0.9), 1.0), (0.3, crackle(2.5, 40, 0.2), 0.9)], shot_name="sky")
both("Wowww!", shot_name="two_kids_jump")
say("big", "I wasn't scared. I was... checking if you were okay.", "shrug", shot_name="big_close")
say("lil", "Sure, Big Bro. Sure.", "pat", shot_name="lil_close")

# ---- 4. Chakri ----
say("papa", "And now, the chakri! Watch it spin!", "point", shot_name="papa_close")
act("papa_light", 3.2, target="chakri", sounds=[(0, run_steps(1.0, 4), 0.6), (1.8, hiss(1.0), 0.8), (2.0, run_steps(1.2, 9), 0.8)], shot_name="cracker_low")
act("chakri", 6.0, sounds=[(0, whirr(6.0), 1.0)], shot_name="chakri_top")
say("lil", "It spins like me after three laddoos!", "spin", shot_name="two_kids")
say("big", "Chakri dance! Spin, spin, spin!", "spin")
act("kids_spin", 3.0, sounds=[(0, sfx("boing"), 0.5), (1.2, sfx("boing"), 0.5)], shot_name="two_kids")

# ---- 5. Sparklers + finale ----
say("papa", "Last one. Sparklers! Hold them far from your face, and Papa stays right here.", "point", shot_name="papa_close")
act("sparklers_on", 2.0, sounds=[(0.5, hiss(1.2), 0.6)], shot_name="three_wide")
act("sparkle_wave", 4.0, sounds=[(0, sparkle_loop(4.0), 0.9)], shot_name="three_wide")
say("big", "Look! I'm writing my name in the sky!", "sparkle", shot_name="big_close")
say("lil", "And I'm drawing a giant laddoo!", "sparkle", shot_name="lil_close")
act("finale", 5.0, sounds=[(0.2, boom(0.6), 0.7), (1.4, boom(0.5), 0.6), (2.6, boom(0.6), 0.7), (3.6, boom(0.5), 0.6)], shot_name="finale_crane")
both("Happy Diwali from the Bro Bros!", shot_name="three_wide")
say("papa", "Remember, friends. Always celebrate crackers with a grown up!", "wave", shot_name="papa_close")
act("end_card", 4.0, sounds=[(0, sfx("tada"), 0.8)], shot_name="finale_crane")
TOTAL = T + 0.5

# background distant fireworks every few seconds (neighbours)
rr = random.Random(5); bg_bursts = []
t = 6.0
while t < TOTAL - 3:
    bg_bursts.append(round(t, 2)); fx.append((t, boom(0.25), 0.35)); t += rr.uniform(4.5, 8.0)

# ---------- mix ----------
n = int(TOTAL * SR)
mixv = np.zeros(n, np.float32); mixf = np.zeros(n, np.float32)
for t, a in voice:
    p = int(t * SR); mixv[p:p + len(a)] += a[: max(0, n - p)]
for t, a, g in fx:
    p = int(t * SR); mixf[p:p + len(a)] += (a * g)[: max(0, n - p)]
m = music(TOTAL + 1, "festive")[:n] * 0.22
duck = np.ones(n, np.float32)
for e in ev:
    if e["type"] == "say":
        duck[int(e["t"] * SR): int((e["t"] + e["dur"]) * SR)] = 0.5
k = int(0.2 * SR); duck = np.convolve(duck, np.ones(k) / k, mode="same")
mixd = mixv + mixf * 0.85 + m * duck
mixd[: int(0.4 * SR)] *= np.linspace(0, 1, int(0.4 * SR)); mixd[-SR:] *= np.linspace(1, 0, SR)
mixd /= max(1, np.abs(mixd).max() / 0.95)
sf.write(f"{OUT}/audio.wav", mixd, SR)
json.dump({"fps": 24, "total": round(TOTAL, 3), "events": ev, "shots": shots, "bg_bursts": bg_bursts}, open(f"{OUT}/timeline.json", "w"), indent=1)
print("total seconds", round(TOTAL, 1), "events", len(ev), "shots", len(shots))
