"""Daily Song 02: "Splash Splash at the Beach!" (colours) — ORIGINAL lyrics + ORIGINAL melody, calypso backing (GM soundfont).
Learning hook: colours with call & echo (red bucket, yellow sun, blue sea, green ball, orange crab). Funny: a wave splashes Buddy.
Output: /mnt/user-data/outputs/song02/{timeline.json, audio.wav, voice.wav, lyrics.json}"""
import json, os, sys, numpy as np, soundfile as sf
sys.path.insert(0, "/home/claude/song"); sys.path.insert(0, "/home/claude/bbf")
from sing import sing_word, backing, SR
from engine import tts, sfx, VOICES
OUT = "/mnt/user-data/outputs/song02"; os.makedirs(OUT, exist_ok=True)
VOICES.update({"vanu": ("af_heart", 2, 1.0), "aarav": ("am_puck", 4, 1.05), "vihaan": ("af_jessica", 4, 1.08), "himank": ("am_echo", 5, 1.05), "buddy": ("af_kore", 3, 1.08)})
KV = {"vanu": "af_heart", "aarav": "am_puck", "vihaan": "af_jessica", "himank": "am_echo", "buddy": "af_kore"}
ALL = list(KV)
BPM = 112; B = 60 / BPM; BAR = 4 * B
ev, shots, lyr, cues, scenes, marks = [], [], [], [], [], {}
vox = []
T = 0.0
RED, YEL, BLUE, GRN, ORG = (235, 40, 40), (255, 210, 30), (40, 130, 245), (60, 200, 80), (255, 140, 20)
def shot(s, t=None): shots.append((round(T if t is None else t, 3), s))
def do(who, clip, dur, t=None): ev.append({"t": round(T if t is None else t, 3), "type": "clip", "who": who, "clip": clip, "dur": dur})
def line(whos, words, clip, cam=None, cue=None, text=None, clips2=None, cam2=None, cuecol=None):
    global T
    t0 = T
    if cam: shot(cam)
    total = sum(b for _, _, b in words) * B
    if cam2: shot(cam2, t0 + total * 0.5)
    for k in ALL: do(k, clip if (clips2 is None or k in whos) else clips2, total + 0.3)
    if cue: cues.append([round(t0, 3), round(t0 + total, 3), cue] + ([list(cuecol)] if cuecol else []))
    lyr.append((round(t0, 3), round(t0 + total, 3), text or " ".join(w for w, _, _ in words), whos))
    t = t0
    for w, notes, beats in words:
        notes = notes if isinstance(notes, list) else [notes]
        fr = [(m, 1 / len(notes)) for m in notes]
        d = beats * B * 0.93
        parts = [sing_word(w, fr, d, voice=KV[k]) for k in whos]
        n = max(len(p) for p in parts); a = sum(np.pad(p, (0, n - len(p))) for p in parts) / len(parts) ** 0.5
        vox.append((t + 0.02, a))
        ev.append({"t": round(t + 0.02, 3), "type": "say", "who": "+".join(whos), "whos": whos, "text": w, "dur": round(n / SR, 3), "clip": "-"})
        t += beats * B
    T = t0 + total
def speak(who, text, clip, cam=None, lyric=True):
    global T
    if cam: shot(cam)
    a = tts(who, text); d = len(a) / SR
    vox.append((T + 0.02, a)); do(who, clip, d + 0.4)
    ev.append({"t": round(T + 0.02, 3), "type": "say", "who": who, "text": text, "dur": round(d, 3), "clip": "-"})
    if lyric: lyr.append((round(T, 3), round(T + d, 3), text, [who]))
    return d

CAST = {"himank": [-1.9, 0.9, 12, "Happy Sway Standing"], "aarav": [-0.95, 0.45, 6, "Happy Sway Standing"], "vanu": [0.0, 0.25, 0, "Happy Sway Standing"],
        "vihaan": [0.95, 0.45, -6, "Happy Sway Standing"], "buddy": [1.9, 0.9, -12, "Happy Sway Standing"]}
scenes.append({"name": "beach", "set": "beach", "t0": 0.0, "cast": CAST, "light": "day"})

# ---------------- chorus (cold open = the hook) ----------------
C1 = [("Splash", 74, 1), ("splash", 74, 1), ("splash", 74, 1), ("at", 76, .5), ("the", 74, .5), ("beach", 71, 4)]
C2 = [("Sun", 67, 1), ("so", 69, .5), ("warm", 71, 1.5), ("and", 72, .5), ("the", 71, .5), ("sea", 69, 1), ("in", 67, .5), ("reach", [69, 67], 2.5)]
C3 = [("Waves", 74, 1), ("go", 76, .5), ("up", 79, 1.5), ("waves", 74, 1), ("come", 72, .5), ("down", 67, 3.5)]
C4 = [("Bro", 71, 1), ("Bros", 72, 1), ("splashing", [74, 71], 1.5), ("all", 69, .5), ("around", [71, 67], 4)]
def chorus(cam1="beach_wide", cam2="dance_orbit", short=False):
    line(ALL, C1, "Jump with Arms Open", cam=cam1, cue="SPLASH!", cuecol=BLUE, text="Splash, splash, splash at the beach!")
    line(ALL, C2, "Happy Sway Standing", text="Sun so warm and the sea in reach!")
    line(ALL, C3, "Cheer with Both Hands Up", cam=cam2, cue="WHOOSH!", text="Waves go up, waves come down,")
    line(ALL, C4, "Hip Hop Dance", cue="SPLASH!", cuecol=BLUE, text="Bro Bros splashing all around!")
chorus("beach_wide", "dance_orbit")
# ---------------- spoken call ----------------
T0 = T; T += 0.3
speak("himank", "Let's find colors at the beach!", "Motivational Cheer", cam="close:himank")
for k in ALL:
    if k != "himank": do(k, "Happy Sway Standing", 2 * BAR - 0.3, t=T0 + 0.3)
T = T0 + 2 * BAR
# ---------------- colour verses: lead sings, everybody echoes ----------------
def colour(who, words, text, insert, word, rgb, echo):
    line([who], words, "Talk with Left Hand Raised", cam=insert, cam2="close:" + who, cue=word, cuecol=rgb, text=text, clips2="Happy Sway Standing")
    line(ALL, echo, "Cheer with Both Hands", cam="low_wide", text=", ".join(w for w, _, _ in echo).capitalize() + "!", cue=word, cuecol=rgb)
colour("vanu", [("I", 67, .5), ("see", 71, .5), ("red", 74, 2), ("a", 72, .5), ("red", 71, .5), ("red", 69, 1), ("bucket", [67, 71], 3)],
       "I see red, a red, red bucket!", "insert:bucket", "RED!", RED, [("red", 74, 1), ("red", 76, 1), ("red", 79, 2)])
colour("aarav", [("I", 67, .5), ("see", 71, .5), ("yellow", [74, 72], 2), ("the", 71, .5), ("big", 69, .5), ("yellow", [69, 71], 1), ("sun", 74, 3)],
       "I see yellow, the big yellow sun!", "insert:sun", "YELLOW!", YEL, [("yellow", [74, 72], 1), ("yellow", [76, 74], 1), ("yellow", [79, 74], 2)])
colour("vihaan", [("I", 67, .5), ("see", 71, .5), ("blue", 74, 2), ("the", 72, .5), ("big", 71, .5), ("blue", 71, 1), ("sea", 72, 3)],
       "I see blue, the big blue sea!", "insert:sea", "BLUE!", BLUE, [("blue", 74, 1), ("blue", 76, 1), ("blue", 79, 2)])
chorus("low_wide", "beach_wide")
colour("himank", [("I", 67, .5), ("see", 71, .5), ("green", 74, 2), ("a", 72, .5), ("green", 71, .5), ("beach", 69, 1), ("ball", 71, 3)],
       "I see green, a green beach ball!", "insert:ball", "GREEN!", GRN, [("green", 74, 1), ("green", 76, 1), ("green", 79, 2)])
marks["crab_in"] = round(T, 3)
colour("buddy", [("I", 67, .5), ("see", 71, .5), ("orange", [74, 72], 2), ("a", 71, .5), ("little", [71, 69], .5), ("orange", [67, 69], 1), ("crab", 71, 3)],
       "I see orange, a little orange crab!", "insert:crab", "ORANGE!", ORG, [("orange", [74, 72], 1), ("orange", [76, 74], 1), ("orange", [79, 74], 2)])
# ---------------- funny moment: Buddy chases the crab... SPLASH! ----------------
tB = T
d = speak("buddy", "Here, crabby crabby!", "Collect Object", cam="insert:crab")
for k in ALL:
    if k != "buddy": do(k, "Happy Sway Standing", d + 0.3, t=tB)
T = tB + d + 0.25
tS = T; marks["splash"] = round(tS, 3)
shot("close:buddy", tS - 0.6)
do("buddy", "Fall Down", 2.6, t=tS)
for k in ALL:
    if k != "buddy": do(k, "Look Around Dumbfounded", 2.6, t=tS)
cues.append([round(tS, 3), round(tS + 1.8, 3), "SPLASH!", list(BLUE)])
T = tS + 1.7
d = speak("buddy", "Whoa! I'm all wet!", "Kneel on One Knee and Stand", cam="close:buddy")
T += d + 0.15
tL = T
d2 = max(len(tts(k, "Ha ha ha!")) for k in ("vanu", "aarav", "vihaan", "himank")) / SR
for k in ("vanu", "aarav", "vihaan", "himank"):
    a = tts(k, "Ha ha ha!"); vox.append((tL + 0.05 * ALL.index(k), a * 0.8)); do(k, "Victory Cheer", d2 + 0.6, t=tL)
    ev.append({"t": round(tL + 0.05 * ALL.index(k), 3), "type": "say", "who": k, "text": "Ha ha ha!", "dur": round(len(a) / SR, 3), "clip": "-"})
do("buddy", "Shrug", d2 + 0.6, t=tL); shot("beach_wide", tL)
lyr.append((round(tL, 3), round(tL + d2, 3), "Ha ha ha!", ["vanu", "aarav", "vihaan", "himank"]))
T = tL + d2 + 0.4
# re-align to the bar grid so the music stays tight
T = (int(T / BAR) + 1) * BAR
# ---------------- colour recap + last chorus ----------------
line(ALL, [("Red", 74, 1), ("yellow", [76, 74], 1), ("blue", 72, 1), ("green", 71, 1), ("orange", [69, 71], 1), ("too", 74, 3)], "Cheer with Both Hands Up",
     cam="dance_orbit", cue="COLOURS!", text="Red, yellow, blue, green, orange too!")
line(ALL, [("Beach", 72, 1), ("colors", [71, 69], 1), ("for", 67, .5), ("me", 69, .5), ("and", 71, 1), ("you", 67, 4)], "Big Heart Gesture",
     cam="low_wide", text="Beach colours for me and you!")
chorus("beach_wide", "dance_orbit")
# ---------------- outro + teaser ----------------
tE = T
for k in ALL: do(k, "Formal Bow", 2.6, t=tE)
shot("beach_wide", tE); T = tE + 2.6
speak("vanu", "Tomorrow, let's move like jungle animals! Bye bye!", "Big Wave Hello", cam="close:vanu")
for k in ("aarav", "vihaan", "himank", "buddy"): do(k, "Big Wave Hello", 2.5, t=T - 2.2)
T += 0.4
ev.append({"t": round(T, 3), "type": "card", "name": "endcard", "dur": 5.0}); shot("beach_wide"); T += 5.0
scenes[-1]["t1"] = round(T, 3); TOTAL = T
shots.sort()
print("TOTAL", round(TOTAL, 1), "events", len(ev), "lines", len(lyr))

# ---------------- music: ORIGINAL calypso backing in G (I–IV–V–I), steel drum + marimba + congas ----------------
CH = [[55, 59, 62], [48, 52, 55], [50, 54, 57], [55, 59, 62]]
drums, bass, steel, mar = [], [], [], []
nb = int(TOTAL / B) + 4
quiet = (tS - 0.2, tL + d2 + 0.2)
for i in range(nb):
    st = i * B
    if st > TOTAL - 5.0: break
    c = CH[(i // 4) % 4]; soft = quiet[0] < st < quiet[1]
    if not soft:
        drums += [(36, st, st + 0.1)] if i % 2 == 0 else [(39, st, st + 0.1)]
        drums += [(62 if i % 2 else 63, st + B / 2, st + B / 2 + 0.08), (64, st + 3 * B / 4, st + 3 * B / 4 + 0.08), (70, st + B / 4, st + B / 4 + 0.04), (70, st + 3 * B / 4, st + 3 * B / 4 + 0.04)]
        bass.append((c[0] - 12, st, st + B * 0.45)); bass.append((c[0] - 5, st + B * 0.75, st + B * 1.2))
        if i % 2 == 1:   # off-beat steel-drum stabs (calypso skank)
            for n_ in c: steel.append((n_ + 12, st + B / 2, st + B * 0.9))
    if i % 4 == 0:
        for j, n_ in enumerate(c + [c[0] + 12]): mar.append((n_ + 12, st + j * B / 2, st + j * B / 2 + B * 0.45))
bk = backing([(0, True, drums, 88), (33, False, bass, 98), (114, False, steel, 72), (12, False, mar, 58)], BPM, TOTAL + 1)
n = int((TOTAL + 1) * SR)
vv = np.zeros(n, np.float32)
for t, a in vox:
    p = int(t * SR); L = min(len(a), n - p); vv[p:p + L] += a[:L]
vv = vv / (np.abs(vv).max() + 1e-6) * 0.85
def splash_sfx():
    rng = np.random.default_rng(3); L = int(1.3 * SR); x = rng.standard_normal(L).astype(np.float32)
    from scipy.signal import butter, lfilter
    b_, a_ = butter(2, [400 / (SR / 2), 5000 / (SR / 2)], "band"); x = lfilter(b_, a_, x)
    env = np.exp(-np.linspace(0, 5, L)) * np.clip(np.linspace(0, 40, L), 0, 1)
    drops = np.zeros(L, np.float32)
    for k in range(14):
        p = int(rng.uniform(0.15, 1.1) * SR); f = rng.uniform(900, 2200); m = int(0.05 * SR)
        tt = np.arange(m) / SR; drops[p:p + m] += np.sin(2 * np.pi * (f + 4000 * tt) * tt) * np.exp(-tt * 70) * 0.5
    y = x * env + drops; return (y / np.abs(y).max() * 0.9).astype(np.float32)
fx = np.zeros(n, np.float32)
def put(t, a, g):
    p = int(t * SR); L = min(len(a), n - p); fx[p:p + L] += a[:L] * g
put(tS - 0.05, splash_sfx(), 0.85); put(tS + 0.9, sfx("boing"), 0.5)
put(TOTAL - 4.8, sfx("tada"), 0.7); put(TOTAL - 4.5, sfx("sparkle"), 0.6)
for t0_, _, w, *_ in cues:
    if w in ("RED!", "YELLOW!", "BLUE!", "GREEN!", "ORANGE!"): put(t0_, sfx("ding"), 0.25)
env = np.convolve(np.abs(vv), np.ones(2400) / 2400, mode="same")
duck = 1 - 0.35 * np.clip(env / 0.05, 0, 1)
mix = vv + 0.55 * bk[:n] * duck + fx
mix = mix / np.abs(mix).max() * 0.92
sf.write(f"{OUT}/audio.wav", mix, SR); sf.write(f"{OUT}/voice.wav", vv, SR)
json.dump({"total": TOTAL, "scenes": scenes, "events": ev, "shots": shots, "marks": marks}, open(f"{OUT}/timeline.json", "w"), indent=1)
json.dump({"lyrics": lyr, "cues": cues, "title": "SPLASH SPLASH!", "sub": "At the Beach", "next": "Tomorrow: Jungle Animal Moves!"}, open(f"{OUT}/lyrics.json", "w"), indent=1)
print("saved", OUT, "splash at", round(tS, 2))
