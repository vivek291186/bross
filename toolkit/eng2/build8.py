# ===== Episode builder (eng2): Meshy characters + mocap clips + detailed sets -> one .blend =====
import bpy, sys, os, json, glob, math, re, random
import numpy as np
from mathutils import Vector, Matrix, Euler
sys.path.insert(0, "/home/claude/eng2")
import sets2, sets_diwali, sets_moon, sets_park, sets_beach, sets_jungle, sets_bathroom, vfx, retarget as R

FPS = 24
def _rss(tag): print("MEM", tag, int(open("/proc/self/statm").read().split()[1]) * 4 // 1024, "MB", flush=True)
EP = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "/mnt/user-data/outputs/ep04"
PROPS = sys.argv[sys.argv.index("--") + 2] if "--" in sys.argv and len(sys.argv) > sys.argv.index("--") + 2 else "/home/claude/eng2/props_ep7.py"
CHARS = "/home/claude/m5/chars"; CLIPS = "/home/claude/m2/clips"; CLIPS2 = "/home/claude/m3/clips"; NATIVE = "/home/claude/m5"   # m5: Humanoid rigs + per-character native 24fps clips
KIDS = ["vanu", "aarav", "vihaan", "himank", "buddy"]
TL = json.load(open(f"{EP}/timeline.json"))
F = lambda t: int(round(t * FPS)) + 1
END = F(TL["total"])

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = FPS; sc.frame_start = 1; sc.frame_end = END

# ---------------- sets ----------------
_rss("start")
SETS = sets2.build_all(tuple(dict.fromkeys(s_["set"] for s_ in TL["scenes"])))
SETNAME = {"kitchen": "kitchen", "bus": "bus", "classroom": "classroom", "canteen": "canteen"}

# ---------------- clips ----------------
def norm(s): return re.sub(r"[^a-z0-9]", "", s.lower().replace("male", "m").replace("dancing1", "dancing01").replace("dancing 1", "dancing01"))
CLIPFILES = {norm(R.clip_name(p)): p for p in glob.glob(CLIPS2 + "/*.fbx")}; CLIPFILES.update({norm(R.clip_name(p)): p for p in glob.glob(CLIPS + "/*.fbx")})
NCLIPS = {k: {norm(os.path.basename(p)[:-4]): p for p in glob.glob(f"{NATIVE}/{k}/clips/*.fbx")} for k in KIDS}
ALIAS = {"idle": "Idle 02", "funnydancing1": "FunnyDancing 03", "funnydancing01": "FunnyDancing 03", "joyfuldancewithhandsway": "Hip Hop Dance",
         "shortbreatheandlookaround": "Idle 02", "chairsitidlem": "Sit Cross Legged", "listeninggesture": "Listening Gesture"}
SUBST = {norm(a): b for a, b in {"Jumping Jacks": "Hop with Arms Raised", "Mirror Viewing": "Happy Sway Standing",
         "Half Squat with Thumb Up": "Victory Cheer", "Show Both Arm Muscles": "Motivational Cheer", "Victory": "Victory Fist Pump"}.items()}
def _find(table, k):
    if k in table: return table[k]
    for kk, p in table.items():
        if kk.startswith(k) or k.startswith(kk): return p
def clipfile(name, kid=None):
    """native (per-character, no retarget error) first; generic 30fps library as fallback"""
    k = norm(ALIAS.get(norm(name), name))
    if kid is not None:
        p = _find(NCLIPS[kid], k)
        if p: return p
        sub = SUBST.get(k)   # kid hasn't got this new clip yet -> nearest native look-alike
        if sub:
            p = _find(NCLIPS[kid], norm(sub))
            if p: print(f"SUBST {kid}: {name} -> {sub}"); return p
    p = _find(CLIPFILES, k)
    if p: return p
    raise KeyError(name)
def is_native(path): return path.startswith(NATIVE)
def speed(path): return 1.0 if is_native(path) else 24 / 30.0
used = {"Idle", "Walking", "Running"}
for e in TL["events"]:
    if e.get("clip") and e["clip"] != "-": used.add(e["clip"])
for s in TL["scenes"]:
    for v in s["cast"].values(): used.add(v[3])
used_files = sorted({clipfile(u, kid) for u in used for kid in KIDS})
missing_native = sorted({u for u in used for kid in KIDS if not is_native(clipfile(u, kid))}); print("clips without native version (generic fallback):", missing_native)
print("clips used:", len(used_files)); _rss("sets")
SRC = {}
for p in used_files:
    nm, frames, hh = R.load_clip(p)
    if "Chair_Sit_Idle" in p:   # keep the upright part only, ping-pong for breathing
        frames = frames[:28] + frames[26:0:-1]
    SRC[p] = (nm, frames, hh)

_rss("clips")
# ---------------- characters ----------------
CH = {}
import chars6 as chars5
MTEX = EP + "/mtex"; os.makedirs(MTEX, exist_ok=True)
for k in KIDS:
    arm, mesh, sk, eyes = chars5.prep(f"{CHARS}/{k}/{k}.fbx", k, MTEX)
    import mouthfx2
    mouthfx2.upgrade(mesh, arm, k, MTEX, dict(atlas=f"{MTEX}/{k}_mouths.png", nomouth=f"{MTEX}/{k}_nomouth.png", lipc=chars5.LIPC.get(k, [0.72, 0.38, 0.36])))
    for m_ in mesh.modifiers:
        if m_.type == "ARMATURE": m_.use_deform_preserve_volume = True
        if m_.type == "CORRECTIVE_SMOOTH": m_.factor = 0.6; m_.iterations = 4
    arm.location = (0, 0, -50)
    arm.animation_data_create()
    CH[k] = dict(arm=arm, mesh=mesh, sk=sk, acts={}, eyes=eyes)
    print("char", k); _rss("char " + k)

def get_act(k, path):
    acts = CH[k]["acts"]
    if path not in acts:
        nm, frames, hh = SRC[path]; loco = any(x in path for x in R.LOCO) or (os.environ.get("BBF_INPLACE") == "1" and "Sit" not in path)
        acts[path] = R.retarget(frames, hh, CH[k]["arm"], f"{k}|{nm}", loco=loco)
    return acts[path]
def nframes(act): return int(act.frame_range[1] - act.frame_range[0] + 1)
SPEED = 1.0   # native clips are exported at 24fps; see speed(path) for the generic fallback

# head facing axis for look-at
def head_bone(k): return [b for b in CH[k]["arm"].data.bones if b.name.endswith(":Head")][0]
def facing_axis(k):
    b = head_bone(k); M = b.matrix_local.to_3x3()
    best = None
    for name, v in (("TRACK_X", Vector((1, 0, 0))), ("TRACK_NEGATIVE_X", Vector((-1, 0, 0))), ("TRACK_Z", Vector((0, 0, 1))), ("TRACK_NEGATIVE_Z", Vector((0, 0, -1)))):
        d = (M @ v).normalized().dot(Vector((0, -1, 0)))
        if best is None or d > best[1]: best = (name, d)
    return best[0]

# ---------------- scene schedule ----------------
scenes = TL["scenes"]
for s in scenes: s["f0"] = F(s["t0"]); s["f1"] = F(s.get("t1", TL["total"]))
def scene_at(f):
    for s in scenes:
        if s["f0"] <= f < s["f1"]: return s
    return scenes[-1]
def origin(s): return SETS[s["set"]]["origin"]
SEATED_SETS = {k_: v_["seat_z"] for k_, v_ in SETS.items() if "seat_z" in v_}

def yaw_face(src, dst):
    d = Vector(dst) - Vector(src); return math.atan2(d.x, -d.y)

# per-character requests: (f0, f1, clip, prio)
REQ = {k: [] for k in KIDS}
ROOT = {k: [] for k in KIDS}   # keyframes: (frame, x, y, z, yaw)
VIS = {k: [] for k in KIDS}    # (frame, visible)
LOOK = {k: [] for k in KIDS}   # (frame, target-kid or None)

def sit_z(k, clip_path, seat_z):
    nm, frames, hh = SRC[clip_path]
    arm = CH[k]["arm"]; hips = [b for b in arm.data.bones if b.name.endswith(":Hips")][0]
    kk = hips.head_local.z / hh
    hz = frames[0]["Hips"].translation.z * kk
    return seat_z + 0.10 - hz

for s in scenes:
    O = origin(s); cast = s["cast"]
    cx = sum(v[0] for v in cast.values()) / len(cast); cy = sum(v[1] for v in cast.values()) / len(cast)
    for k in KIDS:
        if k not in cast:
            VIS[k].append((s["f0"], False)); continue
        x, y, yaw, base = cast[k]
        VIS[k].append((s["f0"], True))
        seated = "sit" in base.lower()
        z = 0.0
        if seated:
            z = sit_z(k, clipfile(base, k), SEATED_SETS.get(s["set"], 0.42)); yawr = 0.0
        else:
            # face between group centre and camera side
            tgt = Vector((cx, cy - 1.6)) if (abs(x - cx) > 0.2 or abs(y - cy) > 0.2) else Vector((x, y - 2))
            yawr = yaw_face((x, y), tgt)
            if x < -3.0: yawr = yaw_face((x, y), (x + 2, y - 0.3))
        ROOT[k].append((s["f0"], O.x + x, O.y + y, z, yawr))
        REQ[k].append((s["f0"], s["f1"], base, 0))
        CH[k].setdefault("seat", {})[s["name"]] = (seated, z)

POS = {}  # helper to know current planar pos per kid when building moves
def last_root(k, f):
    r = sorted([p for p in ROOT[k] if p[0] <= f], key=lambda p: p[0])
    return r[-1] if r else (f, 0, 0, 0, 0)

speakers = []  # (f0, f1, [kids])
for e in TL["events"]:
    f0 = F(e["t"])
    if e["type"] == "say":
        whos = e.get("whos") or [e["who"]]
        f1 = F(e["t"] + e["dur"])
        speakers.append((f0, f1, whos))
        if e.get("clip") and e["clip"] != "-":
            for k in whos:
                REQ[k].append((f0, f1 + 6, e["clip"], 2))
    elif e["type"] == "clip":
        f1 = F(e["t"] + e["dur"]); REQ[e["who"]].append((f0, f1, e["clip"], 3))
    elif e["type"] == "move":
        k = e["who"]; f1 = F(e["t"] + e["dur"])
        lr = last_root(k, f0); s = scene_at(f0); O = origin(s)
        tx, ty = O.x + e["to"][0], O.y + e["to"][1]; tz = e["to"][2] if len(e["to"]) > 2 else 0.0
        dyaw = yaw_face((lr[1], lr[2]), (tx, ty))
        clip = e.get("clip", "Walking")
        standing_clip = "Sit to Stand" in clip
        if standing_clip:
            REQ[k].append((f0, f1, clip, 4))
            ROOT[k].append((f0, lr[1], lr[2], lr[3], lr[4]))
            ROOT[k].append((f1, tx, ty, 0.0, lr[4]))
        else:
            ROOT[k].append((f0, lr[1], lr[2], lr[3], lr[4]))
            ROOT[k].append((min(f0 + 6, f1), lr[1], lr[2], lr[3], dyaw))
            ROOT[k].append((f1, tx, ty, tz, dyaw))
            REQ[k].append((f0, f1, clip, 4))
            # arrive: always turn to face the camera side (unless leaving through a door)
            if abs(tx - O.x) < 4.0:
                ROOT[k].append((f1 + 8, tx, ty, tz, yaw_face((tx, ty), (O.x + (tx - O.x) * 0.3, O.y - 2.5))))
        # after moving, base becomes Idle
        REQ[k].append((f1, scene_at(f0)["f1"], "Idle", 1))
    elif e["type"] == "turn":
        k = e["who"]; lr = last_root(k, f0)
        ROOT[k].append((f0, lr[1], lr[2], lr[3], lr[4])); ROOT[k].append((F(e["t"] + e["dur"]), lr[1], lr[2], lr[3], math.radians(e["yaw"])))

# ---------------- NLA assembly ----------------
BLEND = 6
def resolve(reqs):
    """later/higher-priority requests override; returns contiguous segments [(f0,f1,clip)]"""
    marks = sorted({r[0] for r in reqs} | {r[1] for r in reqs} | {1, END + 1})
    segs = []
    for a, b in zip(marks, marks[1:]):
        if b <= a: continue
        act = [r for r in reqs if r[0] <= a < r[1]]
        if not act: clip = "Idle"
        else:
            act.sort(key=lambda r: (r[3], r[0])); clip = act[-1][2]
        if segs and segs[-1][2] == clip and segs[-1][1] == a: segs[-1] = (segs[-1][0], b, clip)
        else: segs.append((a, b, clip))
    return segs

for k in KIDS:
    arm = CH[k]["arm"]; ad = arm.animation_data
    tracks = []; ends = []
    segs = resolve(REQ[k])
    # merge tiny segments into previous
    m = []
    for sg in segs:
        if m and sg[1] - sg[0] < 4: m[-1] = (m[-1][0], sg[1], m[-1][2])
        else: m.append(sg)
    segs = m
    for i, (a, b, clip) in enumerate(segs):
        cp = clipfile(clip, k); act = get_act(k, cp); SPEED = speed(cp)
        n = nframes(act)
        start = max(1, a - (BLEND if i else 0))
        ti = next((j for j, e in enumerate(ends) if e <= start - 1), None)
        if ti is None:
            tracks.append(ad.nla_tracks.new()); ends.append(-1e9); ti = len(tracks) - 1
        tr = tracks[ti]
        st = tr.strips.new(f"{i}_{clip}", start, act)
        st.scale = SPEED
        one = n * SPEED
        st.repeat = max(1.0, (b - start) / one)
        st.frame_end = b
        st.blend_in = min(BLEND, (b - start) // 2) if i else 0
        st.blend_out = BLEND if i < len(segs) - 1 else 0
        st.extrapolation = "NOTHING"; st.use_auto_blend = False
        ends[ti] = b + BLEND
    print(k, "segments", len(segs))

# ---------------- root transforms ----------------
for k in KIDS:
    arm = CH[k]["arm"]
    keys = sorted(ROOT[k], key=lambda r: r[0])
    for (f, x, y, z, yw) in keys:
        arm.location = (x, y, z); arm.rotation_euler = (0, 0, yw)
        arm.keyframe_insert("location", frame=f); arm.keyframe_insert("rotation_euler", frame=f)
    # scene cuts must be instant: make keys at scene starts constant from previous frame
    if arm.animation_data.action:
        for fc in arm.animation_data.action.fcurves:
            for kp in fc.keyframe_points: kp.interpolation = "BEZIER"; kp.easing = "AUTO"
    # visibility
    mesh = CH[k]["mesh"]
    for (f, v) in VIS[k]:
        mesh.hide_render = not v; mesh.hide_viewport = not v
        mesh.keyframe_insert("hide_render", frame=f); mesh.keyframe_insert("hide_viewport", frame=f)
        if not v:
            arm.location = (0, 0, -50); arm.keyframe_insert("location", frame=f)

# fix: teleports at scene starts -> constant interpolation on the key before each scene start
for k in KIDS:
    act = CH[k]["arm"].animation_data.action
    starts = {s["f0"] for s in scenes}
    for fc in act.fcurves:
        pts = sorted(fc.keyframe_points, key=lambda p: p.co.x)
        for p, q in zip(pts, pts[1:]):
            if int(q.co.x) in starts: p.interpolation = "CONSTANT"

# ---------------- lip sync (phoneme-aligned visemes + 3D jaw) ----------------
import soundfile as sf, lipsync5, mouthfx2
from kokoro_onnx.tokenizer import Tokenizer
TOK = Tokenizer()
voice, sr = sf.read(f"{EP}/voice.wav")
if voice.ndim > 1: voice = voice.mean(1)
hop = sr // FPS
env = np.array([np.sqrt(np.mean(voice[i * hop:(i + 1) * hop] ** 2)) if i * hop < len(voice) else 0 for i in range(END + 2)])
for k in KIDS:
    kb_ = CH[k]["mesh"].data.shape_keys.key_blocks
    for nm_ in ("jaw", "vis"): kb_[nm_].value = 0; kb_[nm_].keyframe_insert("value", frame=1)
NOD = {k: [] for k in KIDS}   # (frame, strength) head nods on stressed vowels
for e in TL["events"]:
    if e["type"] != "say": continue
    whos = e.get("whos") or [e["who"]]
    t0, t1 = e["t"], e["t"] + e["dur"]
    seg = voice[int(t0 * sr): int(t1 * sr)]
    if len(seg) < sr // 10: continue
    try:
        ph, span = lipsync5.align(e["text"], seg, sr, TOK)
    except Exception as ex:
        print("align failed", ex); ph = []
    for k in whos:
        if k not in CH: continue
        if ph: mouthfx2.key_speech(CH[k]["mesh"], ph, t0, FPS)
        # nods: loud vowels, at most one per 0.45 s
        last = -9
        for (t, v, loud) in ph:
            if v in lipsync5.VOWELS and loud > 0.75 and t - last > 0.45:
                NOD[k].append((F(t0 + t), min(1.0, loud))); last = t
# ---------------- blinks + eyebrows ----------------
for k in KIDS:
    kb = CH[k]["mesh"].data.shape_keys.key_blocks; bl = kb["blink"]; br = kb["brows"]
    rnd = random.Random(KIDS.index(k) * 17 + 3)
    bl.value = 0; bl.keyframe_insert("value", frame=1); br.value = 0; br.keyframe_insert("value", frame=1)
    f = int(rnd.uniform(20, 70))
    while f < END - 6:
        for df, v in ((-2, 0.0), (0, 1.0), (1, 1.0), (4, 0.0)):
            bl.value = v; bl.keyframe_insert("value", frame=f + df)
        f += int(rnd.uniform(2.2, 5.0) * FPS)
        if rnd.random() < 0.18: f -= int(1.4 * FPS)   # occasional double blink
for (f0, f1, whos) in speakers:
    for k in whos:
        if k not in CH: continue
        br = CH[k]["mesh"].data.shape_keys.key_blocks["brows"]
        for df, v in ((-1, 0.0), (3, 0.5), (10, 0.5), (16, 0.0)):
            br.value = v; br.keyframe_insert("value", frame=max(1, f0 + df))
for e in TL["events"]:
    if e["type"] == "say" and e.get("emote") == "brows":
        f0 = F(e["t"]); f1 = F(e["t"] + e["dur"])
        for k in (e.get("whos") or [e["who"]]):
            if k not in CH: continue
            br = CH[k]["mesh"].data.shape_keys.key_blocks["brows"]
            for ff, v in ((f0 - 1, 0.0), (f0 + 3, 1.0), (f1, 1.0), (f1 + 8, 0.0)):
                br.value = v; br.keyframe_insert("value", frame=max(1, ff))
for k in KIDS:
    for fc in CH[k]["mesh"].data.shape_keys.animation_data.action.fcurves:
        if "blink" in fc.data_path:
            for kp in fc.keyframe_points: kp.interpolation = "LINEAR"

# ---------------- head look-at ----------------
for k in KIDS:
    arm = CH[k]["arm"]
    tgt = bpy.data.objects.new(f"look_{k}", None); sc.collection.objects.link(tgt); tgt.empty_display_size = 0.05
    hb = head_bone(k)
    c = arm.pose.bones[hb.name].constraints.new("LOCKED_TRACK")
    c.target = tgt; c.track_axis = facing_axis(k); c.lock_axis = "LOCK_Y"; c.influence = 0.55
    CH[k]["look"] = tgt; CH[k]["lookc"] = c

def head_world(k, f):
    sc.frame_set(f)
    arm = CH[k]["arm"]; hb = head_bone(k)
    return arm.matrix_world @ arm.pose.bones[hb.name].head

for s_ in scenes:
    for k in s_["cast"]:
        sc.frame_set(s_["f0"]); a_ = CH[k]["arm"]; yw = a_.matrix_world.to_euler().z
        CH[k]["look"].location = head_world(k, s_["f0"]) + Vector((math.sin(yw), -math.cos(yw), 0)) * 2.0
        CH[k]["look"].keyframe_insert("location", frame=s_["f0"])
# key look targets: at each speaker change, listeners look at speaker, speaker looks at nearest listener
for (f0, f1, whos) in speakers:
    s = scene_at(f0)
    present = [k for k in s["cast"]]
    hw = {k: head_world(k, f0) for k in present}
    for k in present:
        if k in whos:
            others = [o for o in present if o not in whos]
            if others:
                o = min(others, key=lambda o: (hw[o] - hw[k]).length); p = hw[o].copy()
            else:
                p = hw[k] + Vector((0, -2, 0))
            p = p.lerp(hw[k] + Vector((0, -2.5, 0)), 0.5)   # half toward camera side
        else:
            sp = whos[0] if whos[0] in hw else None
            p = hw[sp] if sp else hw[k] + Vector((0, -2, 0))
        # clamp head turn to +-55 deg from body facing
        sc.frame_set(f0); yw = CH[k]["arm"].matrix_world.to_euler().z
        fwd = Vector((math.sin(yw), -math.cos(yw), 0))
        v = p - hw[k]; vz = v.z; v.z = 0
        if v.length > 1e-4:
            ang = math.atan2(fwd.x * v.y - fwd.y * v.x, fwd.dot(v))
            ang = max(-math.radians(55), min(math.radians(55), ang))
            dirv = Matrix.Rotation(ang, 3, "Z") @ fwd
            p = hw[k] + dirv * 2.0 + Vector((0, 0, max(-0.6, min(0.6, vz))))
        else:
            p = hw[k] + fwd * 2.0
        t = CH[k]["look"]; t.location = p; t.keyframe_insert("location", frame=f0 + 3)

# ---------------- speech nods (small head dips on stressed syllables) ----------------
for k in KIDS:
    t = CH[k]["look"]
    for (f, st) in NOD[k]:
        for df, dz in ((-2, 0.0), (1, -0.09 * st), (5, 0.0)):
            t.delta_location = (0, 0, dz); t.keyframe_insert("delta_location", frame=f + df)

# ---------------- props ----------------
exec(open(PROPS).read())

# ---------------- world ----------------
w = bpy.data.worlds.new("world"); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes["Background"]
for s_ in scenes:
    col_, st_ = {"balcony": ((1.0, 0.68, 0.45, 1), 0.55), "balcony_night": ((0.04, 0.05, 0.12, 1), 0.35), "living_diwali": ((0.95, 0.8, 0.6, 1), 0.3), "moon": ((0.0, 0.0, 0.01, 1), 0.15), "park": ((0.55, 0.72, 1.0, 1), 0.5), "beach": ((0.5, 0.72, 1.0, 1), 0.5), "jungle": ((0.55, 0.8, 0.7, 1), 0.45), "bathroom": ((0.85, 0.92, 0.98, 1), 0.35)}.get(s_["set"], ((0.62, 0.72, 0.88, 1), 0.35))
    bg.inputs[0].default_value = col_; bg.inputs[1].default_value = st_
    bg.inputs[0].keyframe_insert("default_value", frame=s_["f0"]); bg.inputs[1].keyframe_insert("default_value", frame=s_["f0"])
for fc in w.node_tree.animation_data.action.fcurves:
    for kp in fc.keyframe_points: kp.interpolation = "CONSTANT"

# ---------------- cameras ----------------
cam = bpy.data.objects.new("CAM", bpy.data.cameras.new("CAM")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.dof.use_dof = True; cam.data.sensor_width = 36
shots = TL["shots"] + [[TL["total"], None]]
def set_main_cam(setn):
    c = SETS[setn]["cams"]
    for nm in c:
        if nm.endswith("_wide"): return c[nm]
    return list(c.values())[0]

def occluded(p, target, kids_present, me):
    for o in kids_present:
        if o in me: continue
        h = head_world(o, CURF) - Vector((0, 0, 0.25))
        ab = target - p; t = max(0, min(1, (h - p).dot(ab) / ab.length_squared))
        if (p + ab * t - h).length < 0.28 and 0.05 < t < 0.95: return True
    # props / furniture between lens and face (scene ray cast, ignoring characters and tiny objects)
    try:
        dg = bpy.context.evaluated_depsgraph_get(); ab = target - p
        hit, loc, nrm, idx, ob, mw = sc.ray_cast(dg, p, ab.normalized(), distance=ab.length * 0.9)
        if hit and ob is not None and not ob.name.endswith("_body") and max(ob.dimensions) > 0.12: return True
    except Exception: pass
    return False

BOUNDS = {"kitchen": (-3.9, 3.9, -4.5, 2.4), "bus": (-0.95, 0.95, -2.4, 5.2), "classroom": (-4.4, 4.4, -3.8, 3.9), "canteen": (-7.7, 7.7, -5.8, 3.1), "living": (-4.3, 4.3, -5.8, 2.4), "balcony": (-3.0, 3.0, -4.8, 1.45),
          "living_diwali": (-4.3, 4.3, -5.8, 2.4), "balcony_night": (-3.0, 3.0, -4.8, 1.45), "moon": (-4.5, 4.5, -5.0, 3.0), "park": (-8.0, 8.0, -5.5, 6.0), "beach": (-8.0, 8.0, -5.5, 5.2), "jungle": (-8.0, 8.0, -5.5, 3.6), "bathroom": (-3.3, 3.3, -5.2, 2.1)}
def clampin(p, setn):
    O = SETS[setn]["origin"]; b = BOUNDS[setn]
    return Vector((min(max(p.x, O.x + b[0]), O.x + b[1]), min(max(p.y, O.y + b[2]), O.y + b[3]), min(max(p.z, 0.25), 2.5)))
def shot_cam(spec, f0, f1):
    r = _shot_cam(spec, f0, f1)
    s = scene_at(f0)
    return (clampin(r[0], s["set"]),) + tuple(r[1:])
def _shot_cam(spec, f0, f1):
    global CURF
    s = scene_at(f0); setn = s["set"]; O = origin(s); main = set_main_cam(setn)
    CURF = f0 + min(12, (f1 - f0) // 2)
    present = list(s["cast"])
    if spec in SETS[setn]["cams"]:
        cv_ = SETS[setn]["cams"][spec]
        if callable(cv_): cv_ = cv_(f0, f1)
        p, t, lens = cv_; p, t = Vector(p), Vector(t)
        return p, t, lens, (3.2 if spec.startswith("insert") else 5.6), (0.10 if not spec.startswith("insert") else 0.05)
    if setn == "bus" and spec.startswith(("close:", "two:")):
        ks = [x for x in spec.split(":")[1:] if x in present] or present[:1]
        Hs = [head_world(x, CURF) for x in ks]; M = sum(Hs, Vector()) / len(Hs)
        dy = 0.72 if spec.startswith("close:") else 1.45
        p = Vector((O.x + 0.02, M.y - dy, M.z + 0.10))
        return p, M - Vector((0, 0, 0.05)), (45 if spec.startswith("close:") else 30), 2.4, 0.05
    if spec.startswith("close:"):
        k = spec.split(":")[1]
        if k not in present: return _shot_cam(main_name(setn), f0, f1)
        H = head_world(k, CURF); mp = Vector(main[0])
        d0 = (mp - H); d0.z = 0; d0.normalize()
        arm = CH[k]["arm"]; pb = arm.pose.bones[head_bone(k).name]
        ax = {"TRACK_X": Vector((1, 0, 0)), "TRACK_NEGATIVE_X": Vector((-1, 0, 0)), "TRACK_Z": Vector((0, 0, 1)), "TRACK_NEGATIVE_Z": Vector((0, 0, -1))}[facing_axis(k)]
        fv = arm.matrix_world.to_3x3() @ pb.matrix.to_3x3() @ ax; fv.z = 0
        d = fv.normalized() if fv.length > 1e-3 else d0
        if fv.length < 1e-3: d = d0
        elif fv.normalized().dot(d0) < 0.2: d = fv.normalized()   # face turned well away from the main cam: swing round to the front
        d.normalize()
        side = Vector((-d.y, d.x, 0))
        for off in (0.15, -0.15, 0.4, -0.4, 0.0):
            p = clampin(H + d * 1.5 + side * off, setn)
            if not occluded(p, H, present, [k]): break
        return p, H - Vector((0, 0, 0.12)), 45, 4.0, 0.05
    if spec.startswith("two:"):
        _, a, b = spec.split(":")
        a = a if a in present else present[0]; b = b if b in present else present[-1]
        Ha, Hb = head_world(a, CURF), head_world(b, CURF); M = (Ha + Hb) / 2
        mp = Vector(main[0]); d = (mp - M); d.z = 0; d.normalize()
        dist = 1.6 + (Ha - Hb).length * 1.25
        p = M + d * dist + Vector((0, 0, 0.08))
        return p, M - Vector((0, 0, 0.12)), 40, 3.2, 0.08
    if spec == "dance_orbit":
        M = sum((head_world(k, CURF) for k in present), Vector()) / len(present)
        return M + Vector((-2.2, -2.6, 0.4)), M - Vector((0, 0, 0.35)), 28, 5.6, 0.0
    return _shot_cam(main_name(setn), f0, f1)

def main_name(setn):
    for nm in SETS[setn]["cams"]:
        if nm.endswith("_wide"): return nm
    return list(SETS[setn]["cams"])[0]

# resolve shot list: also force a cut at every scene start
cuts = []
for (t, spec) in shots:
    if spec is None: continue
    cuts.append((F(t), spec))
for s in scenes:
    if not any(c[0] == s["f0"] for c in cuts): cuts.append((s["f0"], main_name(s["set"])))
cuts.sort()
# drop cuts that conflict with scene (a cut inside scene but naming a cam of another set -> main)
final = []
for i, (f, spec) in enumerate(cuts):
    nf = cuts[i + 1][0] if i + 1 < len(cuts) else END + 1
    if nf - f < 1: continue
    # avoid ultra-short shots (<0.9s): merge into previous
    if final and nf - f < 20 and not spec.startswith("insert"):
        continue
    final.append((f, spec))
CAMLOG = []
# ---- occlusion/framing-aware planner for close/two shots (ported from recam.py) ----
def _bone(k, short):
    a_ = CH[k]["arm"]
    for pb in a_.pose.bones:
        if pb.name.split(":")[-1] == short: return a_.matrix_world @ pb.head
def _snap(f, setn):
    sc.frame_set(f); ox = SETS[setn]["origin"].x; out = {}
    for k in KIDS:
        h = _bone(k, "Head")
        if h is None or h.z < -5 or abs(h.x - ox) > 9: continue
        hf = _bone(k, "headfront"); fw = (hf - h) if hf is not None else Vector((0, -1, 0)); fw.z = 0
        out[k] = dict(fwd=fw.normalized() if fw.length > 1e-4 else Vector((0, -1, 0)), head=h + Vector((0, 0, 0.07)), body=[_bone(k, b_) for b_ in ("Neck", "Spine2", "Spine", "Hips")])
    return out
def _fov(lens): return math.atan(18 / lens), math.atan(18 * 9 / 16 / lens)
def _score(p, aims, lens, frames, targets, S_by_f):
    hf, vf = _fov(lens); bad = 0
    for f in frames:
        S = S_by_f[f]; aim = aims[f]; fw = (aim - p).normalized()
        rt = fw.cross(Vector((0, 0, 1))).normalized(); up = rt.cross(fw)
        for t in targets:
            if t not in S: continue
            H = S[t]["head"]; ab = H - p; d_ = ab.dot(fw)
            x = math.atan2(ab.dot(rt), d_); y = math.atan2(ab.dot(up), d_)
            if abs(x) > hf * 0.85 or abs(y) > vf * 0.85 or d_ < 0: bad += 4
            tc = (p - H); tc.z = 0
            if tc.length > 1e-3 and tc.normalized().dot(S[t]["fwd"]) < 0.15: bad += 2
            for o in S:
                if o in targets: continue
                for i, q in enumerate([S[o]["head"]] + S[o]["body"]):
                    if q is None: continue
                    u = (q - p).dot(ab) / ab.length_squared
                    if 0.03 < u < 0.93 and (p + ab * u - q).length < (0.17 if i == 0 else 0.2): bad += 4; break
        for o in S:
            if o in targets: continue
            dT = min(((S[t]["head"] - p).length for t in targets if t in S), default=9)
            for q in [S[o]["head"], S[o]["body"][1]]:
                if q is None: continue
                d_ = (q - p).dot(fw)
                if d_ <= 0.05 or d_ > dT * 0.8: continue
                x = abs(math.atan2((q - p).dot(rt), d_)); y = abs(math.atan2((q - p).dot(up), d_))
                if x < hf * 0.95 and y < vf * 1.1: bad += 1; break
    return bad
def plan_tracking(spec, f0, f1, p_init, lens):
    """returns list of (frame, loc, rot, lens, focus) for a close/two shot, or None"""
    targets = [t for t in spec.split(":")[1:]]
    s = scene_at(f0); setn = s["set"]
    frames = list(range(f0, f1, 4)) + [f1 - 1]
    S_by_f = {f: _snap(f, setn) for f in frames}
    targets = [t for t in targets if t in S_by_f[frames[0]]]
    if not targets: return None
    mids = {f: sum((S_by_f[f][t]["head"] for t in targets if t in S_by_f[f]), Vector()) / max(1, sum(t in S_by_f[f] for t in targets)) for f in frames}
    fl = sorted(mids); aims = {}
    for i, f in enumerate(fl):
        w_ = [mids[fl[j]] for j in range(max(0, i - 2), min(len(fl), i + 3))]
        aims[f] = sum(w_, Vector()) / len(w_) - Vector((0, 0, 0.12 if spec.startswith("close:") else 0.1))
    zr = max(m.z for m in mids.values()) - min(m.z for m in mids.values())
    mv = max((a_ - b_).length for a_ in mids.values() for b_ in mids.values())   # any big head travel (bend forward, kneel, hop): frame wider
    if mv > 0.22: zr = max(zr, 0.26)
    if zr > 0.25:
        za = sum(a_.z for a_ in aims.values()) / len(aims)
        for f in aims: aims[f] = Vector((aims[f].x, aims[f].y, za - 0.15))
    M_ = mids[frames[0]]
    d0 = (p_init - M_); d0.z = 0
    if d0.length < 1e-3: d0 = Vector((0, -1, 0))
    d0.normalize(); side = Vector((-d0.y, d0.x, 0))
    if spec.startswith("close:") and zr > 0.25:
        lens = 30; base = 2.6; dists = (2.6, 2.2, 3.0); offs = (0.0, 0.4, -0.4, 0.8, -0.8); hts = (0.1, 0.4)
    elif spec.startswith("close:"):
        base = 1.5; dists = (1.5, 1.3, 1.8); offs = (0.0, 0.25, -0.25, 0.5, -0.5, 0.8, -0.8); hts = (0.0, 0.25, 0.5)
    else:
        sp = max((S_by_f[frames[0]][a_]["head"] - S_by_f[frames[0]][b_]["head"]).length for a_ in targets for b_ in targets)
        base = 1.6 + sp * 1.25; dists = (base, base * 0.85, base * 1.2); offs = (0.0, 0.4, -0.4, 0.8, -0.8); hts = (0.08, 0.4, 0.7)
    best = None
    for dd in dists:
        for of in offs:
            for h_ in hts:
                p = clampin(M_ + (d0 * dd + side * of).normalized() * dd + Vector((0, 0, h_)), setn)
                b_ = _score(p, aims, lens, frames, targets, S_by_f)
                cost = b_ * 10 + abs(of) + h_ * 1.5 + abs(dd - base)
                if best is None or cost < best[0]: best = (cost, b_, p)
    cost, b_, p = best
    keys = []
    for f in fl:
        u = (f - f0) / max(1, f1 - 1 - f0)
        pp = p + (aims[f] - p).normalized() * 0.05 * u * (aims[f] - p).length
        rot = (aims[f] - pp).to_track_quat("-Z", "Y").to_euler()
        foc = (S_by_f[f][targets[0]]["head"] - pp).length if targets[0] in S_by_f[f] else (aims[f] - pp).length
        keys.append((f, tuple(pp), tuple(rot), lens, foc))
    return keys

for i, (f, spec) in enumerate(final):
    nf = final[i + 1][0] if i + 1 < len(final) else END + 1
    s = scene_at(f)
    if spec in SETS[s["set"]]["cams"] or spec.startswith(("close:", "two:", "dance")): pass
    else: spec = main_name(s["set"])
    p, t, lens, fstop, push = shot_cam(spec, f, nf)
    CAMLOG.append((f, nf, spec))
    keys = plan_tracking(spec, f, nf, p, lens) if (spec.startswith(("close:", "two:")) and s["set"] != "bus") else None
    if keys:
        for (ff, loc, rot, ln, foc) in keys:
            cam.location = loc; cam.rotation_euler = rot
            cam.keyframe_insert("location", frame=ff); cam.keyframe_insert("rotation_euler", frame=ff)
            cam.data.lens = ln; cam.data.keyframe_insert("lens", frame=ff)
            cam.data.dof.focus_distance = foc; cam.data.dof.aperture_fstop = fstop
            cam.data.dof.keyframe_insert("focus_distance", frame=ff); cam.data.dof.keyframe_insert("aperture_fstop", frame=ff)
        continue
    for (ff, pp) in ((f, p), (nf - 1, p + (t - p).normalized() * push * (t - p).length)):
        cam.location = pp; cam.rotation_euler = (t - pp).to_track_quat("-Z", "Y").to_euler()
        cam.keyframe_insert("location", frame=ff); cam.keyframe_insert("rotation_euler", frame=ff)
        cam.data.lens = lens; cam.data.keyframe_insert("lens", frame=ff)
        cam.data.dof.focus_distance = (t - pp).length; cam.data.dof.aperture_fstop = fstop
        cam.data.dof.keyframe_insert("focus_distance", frame=ff); cam.data.dof.keyframe_insert("aperture_fstop", frame=ff)
# speakers play to the lens: in a close:<k> shot, pull k's look target 65% toward the camera (eyes/head to camera, not the listener)
for (f_, nf_, spec_) in CAMLOG:
    if not spec_.startswith("close:"): continue
    k_ = spec_.split(":")[1]
    if k_ not in CH: continue
    sc.frame_set(f_); cp_ = cam.matrix_world.translation.copy()
    t_ = CH[k_]["look"]; ac_ = t_.animation_data.action if t_.animation_data else None
    if not ac_: continue
    kfs_ = sorted({int(kp.co.x) for fc in ac_.fcurves for kp in fc.keyframe_points if f_ <= kp.co.x < nf_})
    if f_ not in kfs_: kfs_ = [f_] + kfs_
    for kf_ in kfs_:
        sc.frame_set(kf_); cur_ = t_.location.copy(); hw_ = head_world(k_, kf_)
        # keep the +-55 deg clamp against body facing
        yw_ = CH[k_]["arm"].matrix_world.to_euler().z; fwd_ = Vector((math.sin(yw_), -math.cos(yw_), 0))
        v_ = cur_.lerp(cp_, 0.65) - hw_; vz_ = v_.z; v_.z = 0
        if v_.length > 1e-4:
            ang_ = math.atan2(fwd_.x * v_.y - fwd_.y * v_.x, fwd_.dot(v_)); ang_ = max(-math.radians(55), min(math.radians(55), ang_))
            t_.location = hw_ + (Matrix.Rotation(ang_, 3, "Z") @ fwd_) * 2.0 + Vector((0, 0, max(-0.6, min(0.6, vz_ * 2.0 / max(0.3, v_.length)))))
            t_.keyframe_insert("location", frame=kf_)
for fc in cam.animation_data.action.fcurves:
    for kp in fc.keyframe_points: kp.interpolation = "BEZIER"
# hard cuts: the key before each shot start is CONSTANT
starts_ = {c_[0] for c_ in CAMLOG}
for fc in list(cam.animation_data.action.fcurves) + list(cam.data.animation_data.action.fcurves):
    pts = sorted(fc.keyframe_points, key=lambda k_: k_.co.x)
    for p_, q_ in zip(pts, pts[1:]):
        if int(q_.co.x) in starts_: p_.interpolation = "CONSTANT"
for fc in cam.data.animation_data.action.fcurves:
    if fc.data_path in ("lens", "dof.aperture_fstop"):
        for kp in fc.keyframe_points: kp.interpolation = "CONSTANT"
# bus bump camera shake
for e in TL["events"]:
    if e["type"] == "prop" and e["name"] == "bus" and e["action"] == "bump":
        f = F(e["t"])
        for df, dz in ((0, 0), (2, 0.05), (4, -0.04), (6, 0.03), (9, -0.015), (12, 0)):
            sc.frame_set(f + df); z = cam.location.z
        # additive shake via a delta-location
        for df, dz in ((0, 0), (2, 0.06), (4, -0.05), (6, 0.03), (9, -0.015), (12, 0)):
            cam.delta_location = (0, 0, dz); cam.keyframe_insert("delta_location", frame=f + df)

# ---------------- cinematic extras: rim light per shot + handheld micro-motion ----------------
rim = bpy.data.objects.new("RIM", bpy.data.lights.new("RIM", "AREA")); sc.collection.objects.link(rim)
rim.data.energy = 260; rim.data.size = 1.2; rim.data.color = (1.0, 0.92, 0.82)
for (f_, nf_, spec_) in CAMLOG:
    sc.frame_set(f_ + 1)
    s_ = scene_at(f_); present_ = list(s_["cast"])
    if present_:
        hs_ = [head_world(k_, f_ + 1) for k_ in present_ if head_world(k_, f_ + 1).z > -5]
        aim_ = sum(hs_, Vector()) / max(1, len(hs_)) if hs_ else cam.matrix_world.translation + Vector((0, 2, 0))
    else: aim_ = cam.matrix_world.translation + Vector((0, 2, 0))
    cp_ = cam.matrix_world.translation.copy(); d_ = (aim_ - cp_); d_.z = 0
    d_ = d_.normalized() if d_.length > 1e-3 else Vector((0, 1, 0))
    side_ = Vector((-d_.y, d_.x, 0))
    pos_ = clampin(aim_ + d_ * 2.2 + side_ * 1.4 + Vector((0, 0, 1.6)), s_["set"])
    rim.location = pos_; rim.rotation_euler = (aim_ - pos_).to_track_quat("-Z", "Y").to_euler()
    rim.keyframe_insert("location", frame=f_); rim.keyframe_insert("rotation_euler", frame=f_)
    rim.data.energy = 140 if s_["set"] in ("balcony_night", "moon") else 260; rim.data.keyframe_insert("energy", frame=f_)
for fc in list(rim.animation_data.action.fcurves) + list(rim.data.animation_data.action.fcurves):
    for kp in fc.keyframe_points: kp.interpolation = "CONSTANT"
# handheld micro-motion on the camera (tiny noise on delta rotation)
cam.delta_rotation_euler = (0, 0, 0); cam.keyframe_insert("delta_rotation_euler", frame=1)
for i_, fc in enumerate([f for f in cam.animation_data.action.fcurves if f.data_path == "delta_rotation_euler"]):
    m_ = fc.modifiers.new("NOISE"); m_.scale = 55 + 11 * i_; m_.strength = 0.0035; m_.phase = 7 * i_; m_.depth = 1

json.dump({"cams": CAMLOG, "end": END}, open(f"{EP}/camlog.json", "w"))

# ---------------- render settings ----------------
sc.render.resolution_x = 1920; sc.render.resolution_y = 1080; sc.render.resolution_percentage = 100
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"; sc.view_settings.exposure = -0.9
try:
    sc.render.engine = "BLENDER_EEVEE_NEXT"
    ee = sc.eevee; ee.taa_render_samples = 48; ee.use_raytracing = True
    ee.ray_tracing_options.resolution_scale = "2"; ee.ray_tracing_options.trace_max_roughness = 0.5
    ee.use_shadows = True; ee.shadow_ray_count = 2; ee.shadow_step_count = 6
    try: ee.use_fast_gi = True; ee.fast_gi_method = "GLOBAL_ILLUMINATION"
    except Exception: pass
    ee.use_gtao = True
    try: ee.fast_gi_method = "GLOBAL_ILLUMINATION"
    except Exception: pass
except Exception as ex:
    print("eevee settings", ex)
sc.render.use_motion_blur = False
sc.render.image_settings.file_format = "JPEG"; sc.render.image_settings.quality = 92
vfx.compositor_bloom(sc, threshold=1.3, size=7, mix=0.0, streaks=True)
vfx.bake_all()
sc.frame_set(1)
import shutil
TEXD = f"{EP}/tex"; os.makedirs(TEXD, exist_ok=True)
for im in bpy.data.images:
    fp = bpy.path.abspath(im.filepath)
    if im.source == "FILE" and os.path.exists(fp):
        k = fp.split("/chars/")[1].split("/")[0] if "/chars/" in fp else "x"
        nm = k + "_" + os.path.basename(fp).replace("Meshy_AI_", "")
        shutil.copy(fp, f"{TEXD}/{nm}")
        im.filepath = "//tex/" + nm
out = f"{EP}/" + os.path.basename(EP) + ".blend"
bpy.ops.file.pack_all() if False else None
bpy.ops.wm.save_as_mainfile(filepath=out, compress=True)
print("SAVED", out, "frames", END)
