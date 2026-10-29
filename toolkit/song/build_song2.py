"""Song timeline builder (rebuilt): lines.json (Suno aligned lyrics) + spec -> timeline.json, audio.wav (mix), voice.wav (lead vocal)
usage: python3 build_song2.py spec.py"""
import sys, json, runpy, numpy as np, soundfile as sf, subprocess, os
S = runpy.run_path(sys.argv[1]); OUT = S["OUT"]
L = json.load(open(S["LINES"]))["lines"]
mix, sr = sf.read(S["MIX"]); total = len(mix) / sr
sf.write(f"{OUT}/audio.wav", mix, sr)
v, vsr = sf.read(S["VOX"])
if v.ndim > 1: v = v.mean(1)
sf.write(f"{OUT}/voice.wav", v, vsr)
ALL = ["vanu", "aarav", "vihaan", "himank", "buddy"]
ev, shots, cues = [], [], []
SECT = S["SECT"]; cnt = {}
first = L[0]["t0"]
shots.append([0.0, S.get("INTRO_CAM", "high_wide")])
for k in ALL: ev.append({"t": 0.0, "type": "clip", "who": k, "clip": S.get("INTRO_CLIP", "Happy Sway Standing"), "dur": max(1.0, first - 0.2)})
for i, ln in enumerate(L):
    sec = ln["sect"]; spec = SECT.get(sec, SECT["default"]); j = cnt.get(sec, 0) % 4 if sec != "Chorus" else cnt.get(sec, 0) % 4
    cnt[sec] = cnt.get(sec, 0) + 1
    pick = lambda key, d=None: (spec[key][j % len(spec[key])] if isinstance(spec.get(key), list) else spec.get(key, d))
    w_ = spec.get("whos", ALL)
    whos = w_[j % len(w_)] if (w_ and isinstance(w_[0], list)) else list(w_)
    clip = pick("clip", "Happy Sway Standing"); cam = pick("cams", "wide")
    if cam == "close:lead": cam = "close:" + whos[0]
    t0, t1 = ln["t0"], ln["t1"]
    shots.append([round(max(0, t0 - 0.15), 3), cam])
    ev.append({"t": t0, "type": "say", "who": "+".join(whos), "whos": whos, "text": ln["text"], "dur": round(t1 - t0, 3), "clip": clip})
    others = [k for k in ALL if k not in whos]
    c2 = pick("clips2", "Happy Sway Standing")
    for k in others: ev.append({"t": t0, "type": "clip", "who": k, "clip": c2, "dur": round(t1 - t0 + 0.2, 3)})
    cue = pick("cue", "")
    if cue: cues.append([cue, round(t0 + (t1 - t0) * 0.35, 3), round(t1, 3), spec.get("cuecol", [255, 210, 30])])
lt = L[-1]["t1"]
shots.append([round(lt + 0.2, 3), S.get("OUTRO_CAM", "wide")])
for k in ALL: ev.append({"t": lt + 0.1, "type": "clip", "who": k, "clip": "Big Wave Hello", "dur": max(1.0, total - lt - 0.2)})
for t_, who_, c_, d_ in S.get("EXTRA", []): ev.append({"t": t_, "type": "clip", "who": who_, "clip": c_, "dur": d_})
scenes = [{"name": "song", "set": S["SET"], "t0": 0.0, "t1": round(total, 3), "cast": S["CAST"], "light": "day"}]
json.dump({"total": round(total, 3), "scenes": scenes, "events": sorted(ev, key=lambda e: e["t"]), "shots": shots, "cues": cues, "lines": L,
           "title": S["TITLE"], "sub": S.get("SUB", ""), "next": S.get("NEXT", "")}, open(f"{OUT}/timeline.json", "w"), indent=1)
print("song", OUT, "dur", round(total, 1), "lines", len(L), "cues", len(cues), "shots", len(shots))
