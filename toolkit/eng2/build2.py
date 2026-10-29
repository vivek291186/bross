# ===== Episode builder (eng2): Meshy characters + mocap clips + detailed sets -> one .blend =====
import bpy, sys, os, json, glob, math, re, random
import numpy as np
from mathutils import Vector, Matrix, Euler
sys.path.insert(0, "/home/claude/eng2")
import sets2, retarget as R, mouth

FPS = 24
EP = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "/mnt/user-data/outputs/ep02"
CHARS = "/home/claude/m2/chars"; CLIPS = "/home/claude/m2/clips"
KIDS = ["vanu", "aarav", "vihaan", "himank", "buddy"]
TL = json.load(open(f"{EP}/timeline.json"))
F = lambda t: int(round(t * FPS)) + 1
END = F(TL["total"])

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = FPS; sc.frame_start = 1; sc.frame_end = END

# ---------------- sets ----------------
SETS = sets2.build_all()
SETNAME = {"kitchen": "kitchen", "bus": "bus", "classroom": "classroom", "canteen": "canteen"}

# ---------------- clips ----------------
def norm(s): return re.sub(r"[^a-z0-9]", "", s.lower().replace("male", "m").replace("dancing1", "dancing01").replace("dancing 1", "dancing01"))
CLIPFILES = {norm(R.clip_name(p)): p for p in glob.glob(CLIPS + "/*.fbx")}
ALIAS = {"idle": "Listening Gesture", "funnydancing1": "FunnyDancing 01", "funnydancing01": "FunnyDancing 01"}
def clipfile(name):
    k = norm(ALIAS.get(norm(name), name))
    if k in CLIPFILES: return CLIPFILES[k]
    for kk, p in CLIPFILES.items():
        if kk.startswith(k) or k.startswith(kk): return p
    raise KeyError(name)
used = {"Idle", "Short Breathe and Look Around", "Chair Sit Idle Male", "Walking", "Running"}
for e in TL["events"]:
    if e.get("clip") and e["clip"] != "-": used.add(e["clip"])
for s in TL["scenes"]:
    for v in s["cast"].values(): used.add(v[3])
used_files = sorted({clipfile(u) for u in used})
print("clips used:", len(used_files))
SRC = {}
for p in used_files:
    nm, frames, hh = R.load_clip(p); SRC[p] = (nm, frames, hh)

# ---------------- characters ----------------
CH = {}
for k in KIDS:
    arm, mesh = R.import_char(f"{CHARS}/{k}/{k}.fbx", k)
    arm.location = (0, 0, -50)
    sk, _ = mouth.add_jaw(mesh, arm, k, drop=0.011); mouth.add_mouth_dark(mesh, arm, k, sk)
    # material polish: roughness map + slight sheen
    for slot in mesh.material_slots:
        m = slot.material; nt = m.node_tree; p = [n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"][0]
        rp = glob.glob(f"{CHARS}/{k}/*roughness.png")
        if rp and not p.inputs["Roughness"].links:
            t = nt.nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(rp[0]); t.image.colorspace_settings.name = "Non-Color"
            nt.links.new(t.outputs["Color"], p.inputs["Roughness"])
        p.inputs["Specular IOR Level"].default_value = 0.35
    acts = {}
    for path, (nm, frames, hh) in SRC.items():
        loco = any(x in path for x in R.LOCO)
        acts[path] = R.retarget(frames, hh, arm, f"{k}|{nm}", loco=loco)
    arm.animation_data_create()
    CH[k] = dict(arm=arm, mesh=mesh, sk=sk, acts=acts)
    print("char", k, "actions", len(acts))

def nframes(act): return int(act.frame_range[1] - act.frame_range[0] + 1)
SPEED = 24 / 30.0   # clips are 30fps

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
SEATED_SETS = {"bus": SETS["bus"]["seat_z"], "classroom": SETS["classroom"]["seat_z"]}

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
            z = sit_z(k, clipfile(base), SEATED_SETS.get(s["set"], 0.42)); yawr = 0.0
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
    r = [p for p in ROOT[k] if p[0] <= f]
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
        tx, ty = O.x + e["to"][0], O.y + e["to"][1]
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
            ROOT[k].append((f1, tx, ty, 0.0, dyaw))
            REQ[k].append((f0, f1, clip, 4))
            if e.get("yaw") is not None:
                fyaw = math.radians(e["yaw"]) if abs(e["yaw"]) <= 180 else dyaw
                # arrive: face toward camera side of travel
                ROOT[k].append((f1 + 8, tx, ty, 0.0, yaw_face((tx, ty), (O.x + (tx - O.x) * 0.3, O.y - 2.5))))
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
    tracks = [ad.nla_tracks.new(), ad.nla_tracks.new()]
    tracks[0].name = "A"; tracks[1].name = "B"
    segs = resolve(REQ[k])
    for i, (a, b, clip) in enumerate(segs):
        act = CH[k]["acts"][clipfile(clip)]
        n = nframes(act)
        start = max(1, a - (BLEND if i else 0))
        length = b - start
        tr = tracks[i % 2]
        st = tr.strips.new(f"{i}_{clip}", start, act)
        st.scale = SPEED
        one = n * SPEED
        st.repeat = max(1.0, length / one)
        st.frame_end = start + length
        st.blend_in = BLEND if i else 0; st.blend_out = BLEND if i < len(segs) - 1 else 0
        st.extrapolation = "NOTHING"; st.use_auto_blend = False
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

# ---------------- lip sync ----------------
import soundfile as sf
voice, sr = sf.read(f"{EP}/voice.wav")
if voice.ndim > 1: voice = voice.mean(1)
hop = sr // FPS
env = np.array([np.sqrt(np.mean(voice[i * hop:(i + 1) * hop] ** 2)) if i * hop < len(voice) else 0 for i in range(END + 2)])
peak = np.percentile(env[env > 0.002], 95) if (env > 0.002).any() else 0.1
for k in KIDS:
    sk = CH[k]["sk"]; sk.value = 0; sk.keyframe_insert("value", frame=1)
for (f0, f1, whos) in speakers:
    for k in whos:
        if k not in CH: continue
        sk = CH[k]["sk"]
        sk.value = 0; sk.keyframe_insert("value", frame=max(1, f0 - 1))
        prev = 0
        for f in range(f0, f1 + 1):
            v = min(1.0, env[f - 1] / peak * 1.1)
            v = 0.6 * v + 0.4 * prev; prev = v
            if f % 2 == 0 or f == f1:  # 12 key/s gives snappy flaps
                sk.value = round(v, 3); sk.keyframe_insert("value", frame=f)
        sk.value = 0; sk.keyframe_insert("value", frame=f1 + 2)

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
        t = CH[k]["look"]; t.location = p; t.keyframe_insert("location", frame=f0 + 3)

# ---------------- props ----------------
def key_vis(obj, f, v):
    for o in [obj] + list(obj.children_recursive):
        o.hide_render = not v; o.hide_viewport = not v
        o.keyframe_insert("hide_render", frame=f); o.keyframe_insert("hide_viewport", frame=f)

def bone_of(k, name): return [b for b in CH[k]["arm"].pose.bones if b.name.endswith(":" + name)][0]

def attach(obj, k, bone, f, offset=(0, 0.06, 0.02)):
    c = obj.constraints.new("CHILD_OF"); c.target = CH[k]["arm"]; c.subtarget = bone_of(k, bone).name
    c.use_scale_x = c.use_scale_y = c.use_scale_z = False
    c.inverse_matrix = Matrix.Identity(4)
    obj.location = offset; obj.rotation_euler = (0, 0, 0)
    c.influence = 0; c.keyframe_insert("influence", frame=f - 1); c.influence = 1; c.keyframe_insert("influence", frame=f)
    return c

coll_p = sets2.col("props")
# magnifying glass
mg = bpy.data.objects.new("magnifier", None); coll_p.objects.link(mg)
ring = sets2.cyl("mag_ring", 0.055, 0.012, (0, 0, 0), sets2.M("brass", (0.85, 0.68, 0.35), 0.25, 1.0), coll_p, rot=(math.radians(90), 0, 0))
glass = sets2.cyl("mag_glass", 0.05, 0.004, (0, 0, 0), sets2.M("mag_glass", (0.85, 0.95, 1.0), 0.02, 0.0, alpha=0.25), coll_p, rot=(math.radians(90), 0, 0))
handle = sets2.cyl("mag_handle", 0.01, 0.11, (0, 0, -0.1), sets2.M_wood("mag_wood"), coll_p)
for p in (ring, glass, handle): p.parent = mg
key_vis(mg, 1, False)
# jam on vihaan's nose, crumbs on buddy's face
jam = sets2.sph("jam", 0.008, (0, 0, 0), sets2.M("jam", (0.75, 0.05, 0.1), 0.2, coat=0.6), coll_p); key_vis(jam, 1, False)
crumbface = bpy.data.objects.new("crumbface", None); coll_p.objects.link(crumbface)
for i in range(6):
    c = sets2.laddoo(f"cf{i}", (0.0, 0.0, 0.0), coll_p, 0.004); c.parent = crumbface
    c.location = (random.uniform(-0.03, 0.03), 0, random.uniform(-0.02, 0.01))
key_vis(crumbface, 1, False)
food = sets2.cyl("paratha_piece", 0.04, 0.006, (0, 0, 0), sets2.M("paratha", (0.85, 0.62, 0.3), 0.6, bump=0.5, bump_scale=150), coll_p, rot=(math.radians(90), 0, 0))
key_vis(food, 1, False)

def head_front_offset(k, fwd=0.075, up=0.03):
    return (0, up, -fwd)

kitchen = SETS["kitchen"]; bus = SETS["bus"]; classroom = SETS["classroom"]; canteen = SETS["canteen"]
for e in TL["events"]:
    if e["type"] != "prop": continue
    f = F(e["t"]); nm = e["name"]; a = e["action"]
    s = scene_at(f)
    if nm == "door" and a == "open":
        h = bpy.data.objects[kitchen["door"]]
        h.rotation_euler = (0, 0, 0); h.keyframe_insert("rotation_euler", frame=f)
        h.rotation_euler = (0, 0, math.radians(-100)); h.keyframe_insert("rotation_euler", frame=f + 10)
    elif nm == "jam" and a == "hide":
        key_vis(jam, f, False)
    elif nm == "tiffins" and a == "grab_random" and s["set"] == "kitchen":
        order = {"vanu": "himank", "aarav": "vanu", "vihaan": "buddy", "himank": "aarav", "buddy": "vihaan"}   # wrong boxes!
        for kid, box in order.items():
            if kid == "vanu": continue
            ob = kitchen["tiffins"][box]
            attach(ob, kid, "RightHand", f + 20, offset=(0.0, 0.09, 0.04))
    elif nm == "bus" and a == "bump":
        for kid in s["cast"]:
            arm = CH[kid]["arm"]; base = arm.location.copy()
        for kid in s["cast"]:
            arm = CH[kid]["arm"]; sc.frame_set(f); z0 = arm.location.z
            for df, dz in ((0, 0), (3, 0.12), (7, -0.02), (10, 0.04), (14, 0)):
                arm.location.z = z0 + dz; arm.keyframe_insert("location", index=2, frame=f + df)
    elif nm == "tiffins" and a == "fly" and s["set"] == "bus":
        for i, (kid, ob) in enumerate(bus["tiffins"].items()):
            p0 = ob.location.copy()
            ob.keyframe_insert("location", frame=f); ob.keyframe_insert("rotation_euler", frame=f)
            ob.location = p0 + Vector((random.uniform(-0.2, 0.2), random.uniform(0.1, 0.5), 0.9 + 0.2 * i)); ob.rotation_euler = (random.uniform(-3, 3), random.uniform(-3, 3), random.uniform(-3, 3))
            ob.keyframe_insert("location", frame=f + 12); ob.keyframe_insert("rotation_euler", frame=f + 12)
            tgt = list(bus["tiffins"].values())[(i + 2) % 5]   # land on someone else's lap
            ob.location = tgt.location.copy() if False else p0 + Vector((0, 0, 0)); ob.location.x = p0.x + (0.9 if p0.x < bus["origin"].x else -0.9) * (i % 2)
            ob.rotation_euler = (0, 0, random.uniform(-0.5, 0.5))
            ob.keyframe_insert("location", frame=f + 26); ob.keyframe_insert("rotation_euler", frame=f + 26)
    elif nm == "tiffins" and a == "open" and s["set"] == "classroom":
        for kid, ob in classroom["tiffins"].items():
            lid = [c for c in ob.children if c.name.endswith("_lid")][0]
            lid.keyframe_insert("location", frame=f); lid.keyframe_insert("rotation_euler", frame=f)
            lid.location = lid.location + Vector((0.16, 0.05, -0.12)); lid.rotation_euler = (math.radians(70), 0, 0)
            lid.keyframe_insert("location", frame=f + 8); lid.keyframe_insert("rotation_euler", frame=f + 8)
    elif nm == "magnifier" and a == "attach":
        key_vis(mg, f, True); attach(mg, e["who"], "RightHand", f, offset=(0.0, 0.12, 0.03))
    elif nm == "crumb_face" and a == "show":
        key_vis(crumbface, f, True); attach(crumbface, e["who"], "Head", f, offset=(0.0, 0.035, -0.085))
    elif nm == "food" and a == "attach":
        key_vis(food, f, True); attach(food, e["who"], "RightHand", f, offset=(0.0, 0.09, 0.03))
    elif nm == "cat" and a == "meow":
        cat = canteen["cat"]; head = [c for c in cat.children if c.name == "cat_head"][0]
        for df, r in ((0, 0), (6, 0.35), (14, -0.2), (22, 0)):
            head.rotation_euler = (r, 0, 0); head.keyframe_insert("rotation_euler", frame=f + df)

# jam visible during kitchen until hidden
key_vis(jam, F(0), True); attach(jam, "vihaan", "Head", 1, offset=head_front_offset("vihaan", 0.088, 0.02))
for e in TL["events"]:
    if e["type"] == "prop" and e["name"] == "jam": key_vis(jam, F(e["t"]), False)

# classroom food in boxes (buddy's empty)
FOODC = {"aarav": ((0.95, 0.95, 0.9), "idli"), "vanu": ((0.95, 0.8, 0.3), "noodles"), "vihaan": ((0.95, 0.85, 0.55), "sandwich"), "himank": ((0.85, 0.62, 0.3), "paratha")}
for kid, ob in classroom["tiffins"].items():
    if kid in FOODC:
        c, n = FOODC[kid]
        for j in range(3):
            fb = sets2.sph(f"cfood_{kid}{j}", 0.03, (0, 0, 0), sets2.M("food_" + n, c, 0.6, bump=0.4, bump_scale=150), sets2.col("classroom"), scale=(1, 1, 0.5))
            fb.parent = ob; fb.location = (-0.03 + j * 0.03, 0, 0.13)

# bus scenery movers
for t in bus["movers"]:
    y0 = t.location.y
    t.keyframe_insert("location", index=1, frame=1); t.location.y = y0 + 12.8; t.keyframe_insert("location", index=1, frame=1 + 96)
    fc = t.animation_data.action.fcurves.find("location", index=1)
    for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
    fc.modifiers.new("CYCLES")
# canteen fans
for o in bpy.data.objects:
    if o.name.startswith("canteen_fanhub"):
        o.rotation_euler = (0, 0, 0); o.keyframe_insert("rotation_euler", index=2, frame=1)
        o.rotation_euler = (0, 0, 2 * math.pi); o.keyframe_insert("rotation_euler", index=2, frame=1 + 30)
        fc = o.animation_data.action.fcurves.find("rotation_euler", index=2)
        for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
        fc.modifiers.new("CYCLES")

# ---------------- world ----------------
w = bpy.data.worlds.new("world"); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.62, 0.72, 0.88, 1); bg.inputs[1].default_value = 0.35

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
    return False

def shot_cam(spec, f0, f1):
    global CURF
    s = scene_at(f0); setn = s["set"]; O = origin(s); main = set_main_cam(setn)
    CURF = f0 + min(12, (f1 - f0) // 2)
    present = list(s["cast"])
    if spec in SETS[setn]["cams"]:
        p, t, lens = SETS[setn]["cams"][spec]; p, t = Vector(p), Vector(t)
        return p, t, lens, (3.2 if spec.startswith("insert") else 5.6), (0.10 if not spec.startswith("insert") else 0.05)
    if spec.startswith("close:"):
        k = spec.split(":")[1]
        if k not in present: return shot_cam(main_name(setn), f0, f1)
        H = head_world(k, CURF); mp = Vector(main[0])
        d = (mp - H); d.z = 0; d.normalize()
        side = Vector((-d.y, d.x, 0))
        for off in (0.28, -0.28, 0.5, -0.5, 0.0):
            p = H + d * 1.35 + side * off + Vector((0, 0, 0.02))
            if not occluded(p, H, present, [k]): break
        return p, H - Vector((0, 0, 0.04)), 55, 2.2, 0.06
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
    return shot_cam(main_name(setn), f0, f1)

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
for i, (f, spec) in enumerate(final):
    nf = final[i + 1][0] if i + 1 < len(final) else END + 1
    s = scene_at(f)
    if spec in SETS[s["set"]]["cams"] or spec.startswith(("close:", "two:", "dance")): pass
    else: spec = main_name(s["set"])
    p, t, lens, fstop, push = shot_cam(spec, f, nf)
    CAMLOG.append((f, nf, spec))
    for (ff, pp) in ((f, p), (nf - 1, p + (t - p).normalized() * push * (t - p).length)):
        cam.location = pp; cam.rotation_euler = (t - pp).to_track_quat("-Z", "Y").to_euler()
        cam.keyframe_insert("location", frame=ff); cam.keyframe_insert("rotation_euler", frame=ff)
        cam.data.lens = lens; cam.data.keyframe_insert("lens", frame=ff)
        cam.data.dof.focus_distance = (t - pp).length; cam.data.dof.aperture_fstop = fstop
        cam.data.dof.keyframe_insert("focus_distance", frame=ff); cam.data.dof.keyframe_insert("aperture_fstop", frame=ff)
for fc in cam.animation_data.action.fcurves:
    for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
for fc in cam.data.animation_data.action.fcurves:
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

json.dump({"cams": CAMLOG, "end": END}, open(f"{EP}/camlog.json", "w"))

# ---------------- render settings ----------------
sc.render.resolution_x = 1920; sc.render.resolution_y = 1080; sc.render.resolution_percentage = 100
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"; sc.view_settings.exposure = -0.9
try:
    sc.render.engine = "BLENDER_EEVEE_NEXT"
    ee = sc.eevee; ee.taa_render_samples = 32; ee.use_raytracing = True
    ee.ray_tracing_options.resolution_scale = "2"; ee.use_shadows = True; ee.shadow_ray_count = 2; ee.shadow_step_count = 6
    ee.fast_gi_method = "GLOBAL_ILLUMINATION"; ee.use_fast_gi = True
    sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.4
except Exception as ex:
    print("eevee settings", ex)
sc.render.image_settings.file_format = "JPEG"; sc.render.image_settings.quality = 92
sc.frame_set(1)
out = f"{EP}/ep02.blend"
bpy.ops.file.pack_all() if False else None
bpy.ops.wm.save_as_mainfile(filepath=out, compress=True)
print("SAVED", out, "frames", END)
