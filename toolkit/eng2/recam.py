# Re-plan problem camera shots + swap clashing clips on an already-built episode blend.
# python3 recam.py <EPdir>   -> <EP>/recam.json (camera keys + strip swaps + frames to re-render), <EP>/<ep>_v2.blend
import bpy, json, sys, math, os
from mathutils import Vector
EP = sys.argv[-1].rstrip("/"); NAME = os.path.basename(EP)
bpy.ops.wm.open_mainfile(filepath=f"{EP}/{NAME}.blend")
sc = bpy.context.scene; cam = sc.camera
CL = json.load(open(f"{EP}/camlog.json"))["cams"]
TL = json.load(open(f"{EP}/timeline.json"))
KIDS = ["vanu", "aarav", "vihaan", "himank", "buddy"]
ARM = {k: bpy.data.objects[k + "_rig"] for k in KIDS}
SETO = {"kitchen": 0, "bus": 100, "classroom": 200, "canteen": 300, "living": 400, "balcony": 500}
BOUNDS = {"kitchen": (-3.9, 3.9, -4.5, 2.4), "bus": (-0.95, 0.95, -2.4, 5.2), "classroom": (-4.4, 4.4, -3.8, 3.9), "canteen": (-7.7, 7.7, -5.8, 3.1), "living": (-4.3, 4.3, -5.8, 2.4), "balcony": (-3.0, 3.0, -4.8, 1.45)}
FPS = 24; F = lambda t: int(round(t * FPS)) + 1
scenes = TL["scenes"]
def setname(f):
    s = [s for s in scenes if F(s["t0"]) <= f] or scenes[:1]; return s[-1]["set"]
def bone(k, short):
    a = ARM[k]
    for pb in a.pose.bones:
        if pb.name.split(":")[-1] == short: return a.matrix_world @ pb.head
def snap(f):
    sc.frame_set(f); ox = SETO[setname(f)]; out = {}
    for k in KIDS:
        h = bone(k, "Head")
        if h.z < -5 or abs(h.x - ox) > 9: continue
        out[k] = dict(head=h + Vector((0, 0, 0.07)), body=[bone(k, b) for b in ("Neck", "Spine2", "Spine", "Hips")],
                      hands=[bone(k, b) for b in ("LeftHand", "RightHand", "LeftHandMiddle4", "RightHandMiddle4", "LeftForeArm", "RightForeArm")])
    return out

# ---------- 1. clip swaps for hands crossing faces ----------
SWAPS = []
def hand_hits(f0, f1, step=3):
    hits = []
    for f in range(f0, f1, step):
        S = snap(f)
        for k in S:
            for o in S:
                if o == k: continue
                H = S[o]["head"] - Vector((0, 0, 0.05))
                for hp in S[k]["hands"]:
                    if (hp - H).length < 0.24 and abs(hp.z - H.z) < 0.16: hits.append((f, k, o)); break
    return hits
def swap_strip(k, f0, f1, newclip):
    for t in ARM[k].animation_data.nla_tracks:
        for s in t.strips:
            if s.frame_start < f1 and s.frame_end > f0 and "Listening" not in s.action.name and "Walking" not in s.action.name:
                fs, fe = s.frame_start, s.frame_end
                a = bpy.data.actions[f"{k}|{newclip}"]
                s.action = a; s.action_frame_start, s.action_frame_end = a.frame_range
                s.scale = 24 / 30; s.repeat = max(1.0, (fe - fs) / ((a.frame_range[1] - a.frame_range[0] + 1) * 24 / 30))
                s.frame_end = fe
                SWAPS.append(dict(kid=k, strip=s.name, track=t.name, clip=newclip, fs=fs, fe=fe)); return s
SAFE = ["Hand on Hip Gesture", "Listening Gesture", "Look Around Dumbfounded", "Shrug"]
hits = hand_hits(1, sc.frame_end + 1, 4)
fixed = set()
for (f, k, o) in hits:
    key = (k, f // 60)
    if key in fixed: continue
    # find the gesture strip active at f
    for t in ARM[k].animation_data.nla_tracks:
        for s in t.strips:
            if s.frame_start <= f < s.frame_end and "Listening" not in s.action.name and "Walking" not in s.action.name and "Sit" not in s.action.name:
                for c in SAFE:
                    if f"{k}|{c}" in bpy.data.actions and c not in s.action.name:
                        old = s.action.name
                        swap_strip(k, s.frame_start, s.frame_end, c)
                        if not hand_hits(int(s.frame_start), int(s.frame_end), 3):
                            print("swap", k, old, "->", c, s.frame_start, s.frame_end); break
                fixed.add(key)
print("hand hits", len(hits), "swaps", len(SWAPS))

# ---------- 2. camera scoring ----------
def fov(lens): return math.atan(18 / lens), math.atan(18 * 9 / 16 / lens)
def score(p, aims, lens, frames, targets, S_by_f):
    hf, vf = fov(lens); bad = 0
    for f in frames:
        S = S_by_f[f]; aim = aims[f]; fw = (aim - p).normalized()
        rt = fw.cross(Vector((0, 0, 1))).normalized(); up = rt.cross(fw)
        for t in targets:
            if t not in S: continue
            H = S[t]["head"]; ab = H - p
            x = math.atan2((H - p).dot(rt), (H - p).dot(fw)); y = math.atan2((H - p).dot(up), (H - p).dot(fw))
            if abs(x) > hf * 0.85 or abs(y) > vf * 0.85 or (H - p).dot(fw) < 0: bad += 4
            for o in S:
                if o in targets: continue
                for i, q in enumerate([S[o]["head"]] + S[o]["body"]):
                    u = (q - p).dot(ab) / ab.length_squared
                    if 0.03 < u < 0.93 and (p + ab * u - q).length < (0.17 if i == 0 else 0.2): bad += 4; break
        for o in S:   # out-of-focus foreground intruders filling the frame
            if o in targets: continue
            dT = min(((S[t]["head"] - p).length for t in targets if t in S), default=9)
            for q in [S[o]["head"], S[o]["body"][1]]:
                d = (q - p).dot(fw)
                if d <= 0.05 or d > dT * 0.8: continue
                x = abs(math.atan2((q - p).dot(rt), d)); y = abs(math.atan2((q - p).dot(up), d))
                if x < hf * 0.95 and y < vf * 1.1: bad += 1; break
    return bad
def clampin(p, setn):
    o = Vector((SETO[setn], 0, 0)); b = BOUNDS[setn]
    return Vector((min(max(p.x, o.x + b[0]), o.x + b[1]), min(max(p.y, o.y + b[2]), o.y + b[3]), min(max(p.z, 0.25), 2.5)))

NEW = []   # (f0, f1, keys[(f, loc, rot, lens, focus, fstop)])
for (f0, f1, spec) in CL:
    if not spec.startswith(("close:", "two:")): continue
    targets = spec.split(":")[1:]
    frames = list(range(f0, f1, 4)) + [f1 - 1]
    S_by_f = {f: snap(f) for f in frames}
    if not all(t in S_by_f[frames[0]] for t in targets): continue
    lens = 45 if spec.startswith("close:") else 40
    # old camera, evaluated as rendered
    def aim_old(f):
        sc.frame_set(f); m = cam.matrix_world; return m.translation + (m.to_3x3() @ Vector((0, 0, -1))) * 2
    olds = {}
    old_bad = 0
    for f in frames:
        sc.frame_set(f); p = cam.matrix_world.translation.copy(); olds[f] = p
        old_bad += score(p, {f: aim_old(f)}, cam.data.lens, [f], targets, S_by_f)
    if old_bad == 0: continue
    setn = setname(f0); O = Vector((SETO[setn], 0, 0))
    mids = {f: sum((S_by_f[f][t]["head"] for t in targets if t in S_by_f[f]), Vector()) / max(1, sum(t in S_by_f[f] for t in targets)) for f in frames}
    # smoothed aim (tracking), slightly below the eyes
    fl = sorted(mids); aims = {}
    for i, f in enumerate(fl):
        w = [mids[fl[j]] for j in range(max(0, i - 2), min(len(fl), i + 3))]
        aims[f] = sum(w, Vector()) / len(w) - Vector((0, 0, 0.12 if spec.startswith("close:") else 0.1))
    M = mids[frames[0]]
    d0 = (olds[frames[0]] - M); d0.z = 0
    if d0.length < 1e-3: d0 = Vector((0, -1, 0))
    d0.normalize(); side = Vector((-d0.y, d0.x, 0))
    if spec.startswith("close:"):
        base = 1.6; dists = (1.6, 1.35, 1.9); offs = (0.0, 0.3, -0.3, 0.55, -0.55, 0.8, -0.8); hts = (0.0, 0.3, 0.55)
    else:
        sp = max((S_by_f[frames[0]][a]["head"] - S_by_f[frames[0]][b]["head"]).length for a in targets for b in targets)
        base = 1.6 + sp * 1.25; dists = (base, base * 0.85, base * 1.2); offs = (0.0, 0.4, -0.4, 0.8, -0.8); hts = (0.08, 0.4, 0.7)
    best = None
    for dd in dists:
        for of in offs:
            for h in hts:
                p = clampin(M + (d0 * dd + side * of).normalized() * dd + Vector((0, 0, h)), setn)
                b = score(p, aims, lens, frames, targets, S_by_f)
                cost = b * 10 + abs(of) + h * 1.5 + abs(dd - base)
                if best is None or cost < best[0]: best = (cost, b, p)
    cost, b, p = best
    print(spec, f0, f1, "old_bad", old_bad, "new_bad", b, tuple(round(x, 2) for x in p))
    if b >= old_bad: continue
    push = 0.05
    keys = []
    for i, f in enumerate(fl):
        u = (f - f0) / max(1, f1 - 1 - f0)
        pp = p + (aims[f] - p).normalized() * push * u * (aims[f] - p).length
        rot = (aims[f] - pp).to_track_quat("-Z", "Y").to_euler()
        keys.append((f, tuple(pp), tuple(rot), lens, (S_by_f[f][targets[0]]["head"] - pp).length if targets[0] in S_by_f[f] else (aims[f] - pp).length))
    NEW.append(dict(f0=f0, f1=f1, spec=spec, keys=keys))

# ---------- 3. apply camera keys ----------
act = cam.animation_data.action; dact = cam.data.animation_data.action
def fcs(a, path): return [fc for fc in a.fcurves if fc.data_path == path]
for sh in NEW:
    f0, f1 = sh["f0"], sh["f1"]
    for a in (act, dact):
        for fc in a.fcurves:
            for kp in [kp for kp in fc.keyframe_points if f0 <= kp.co.x <= f1 - 1]: fc.keyframe_points.remove(kp, fast=True)
            fc.update()
    for (f, loc, rot, lens, foc) in sh["keys"]:
        cam.location = loc; cam.rotation_euler = rot
        cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f)
        cam.data.lens = lens; cam.data.keyframe_insert("lens", frame=f)
        cam.data.dof.focus_distance = foc; cam.data.dof.aperture_fstop = 2.4 if sh["spec"].startswith("close:") else 3.2
        cam.data.dof.keyframe_insert("focus_distance", frame=f); cam.data.dof.keyframe_insert("aperture_fstop", frame=f)
for fc in act.fcurves:
    for kp in fc.keyframe_points:
        if any(sh["f0"] <= kp.co.x < sh["f1"] for sh in NEW): kp.interpolation = "BEZIER"
        else: kp.interpolation = "LINEAR"
# keep cuts hard: key just before each new shot stays CONSTANT
for fc in list(act.fcurves) + list(dact.fcurves):
    pts = sorted(fc.keyframe_points, key=lambda k: k.co.x)
    starts = {sh["f0"] for sh in NEW} | {c[0] for c in CL}
    for p_, q_ in zip(pts, pts[1:]):
        if int(q_.co.x) in starts: p_.interpolation = "CONSTANT"
    if fc.data_path in ("lens", "dof.aperture_fstop"):
        for kp in fc.keyframe_points: kp.interpolation = "CONSTANT"

# frames to re-render: whole replanned shots + whole shots touching swapped strips
rer = set()
for sh in NEW: rer.update(range(sh["f0"], sh["f1"]))
for sw in SWAPS:
    for (a, b, spec) in CL:
        if a < sw["fe"] + 6 and b > sw["fs"] - 6: rer.update(range(a, b))
json.dump(dict(shots=NEW, swaps=SWAPS, frames=sorted(rer)), open(f"{EP}/recam.json", "w"))
bpy.ops.wm.save_as_mainfile(filepath=f"{EP}/{NAME}_v2.blend", compress=True)
print("replanned", len(NEW), "swaps", len(SWAPS), "frames", len(rer))
