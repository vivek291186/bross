
# ---------------- characters: the user's GLB models, auto-rigged ----------------
from mathutils import Matrix, Euler
MODELS = {"vanu": "05_Burgundy_Top.glb", "aarav": "03_Floral_Shirt.glb", "vihaan": "02_Sage_Shirt.glb",
          "himank": "04_Blue_Tie_Dye.glb", "buddy": "01_Green_Shirt.glb"}
HOME = {"vanu": (-2.4, 1.35), "aarav": (-1.2, 1.3), "vihaan": (0.0, 1.3), "himank": (1.2, 1.3), "buddy": (2.4, 1.35)}
DOOR = (0, 5.6)
SCALE = 1.45
R = {}
import re as _re

def base(n): return _re.sub(r"( \d+)?(\.\d+)?$", "", n)
HEAD_P = ("Brown iris", "Dark pupil", "Ear", "Ear inner", "Eye light", "Eye white", "Eyebrow", "Head", "Nose", "Nose wing",
          "Upper eyelid", "Continuous hair cap", "Front fringe", "Swept hair lock", "Parted hair cap", "Parted side wave",
          "Long rounded back wave", "Eyeglass frame", "Glasses bridge", "Glasses temple")
MOUTH_P = ("Smile", "Lower lip")
UPPER_P = ("Upper arm", "Elbow", "Short sleeve")
FORE_P = ("Forearm", "Palm", "Finger", "Fingertip", "Thumb", "Wrist bracelet")
LEG_P = ("Trouser leg", "Trouser hem", "Trouser front seam", "Shorts leg", "Shorts cuff", "Knee", "Lower leg", "Foot", "Toe",
         "Shoe sole", "Flip flop Y strap", "Sandal pattern", "Slide sandal band", "Clog heel strap", "Clog upper", "Clog vent",
         "Ribbed slide strap", "Cargo pocket", "Pocket flap")

def wverts(o): return [o.matrix_world @ v.co for v in o.data.vertices]
def endpoints(pts):
    c = sum(pts, Vector()) / len(pts)
    # principal axis by power iteration
    ax = Vector((0.1, 0.2, 1.0))
    for _ in range(12):
        nv = Vector()
        for p in pts:
            d = p - c; nv += d * d.dot(ax)
        if nv.length < 1e-9: break
        ax = nv.normalized()
    ts = [(p - c).dot(ax) for p in pts]
    return c + ax * min(ts), c + ax * max(ts), c

def build_model(name):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=MD + MODELS[name])
    new = [o for o in bpy.data.objects if o not in before]
    root = [o for o in new if o.parent is None][0]
    root.scale = tuple(v * SCALE for v in root.scale); root.location = (0, 0, 0)
    bpy.context.view_layer.update()
    meshes = [o for o in new if o.type == "MESH"]
    parts = {}
    for o in meshes:
        pts = wverts(o); c = sum(pts, Vector()) / len(pts)
        parts.setdefault(base(o.name), []).append((o, pts, c))
    def side_of(c): return 1 if c.x > 0 else -1
    def find(nm, sx=None):
        for o, pts, c in parts.get(nm, []):
            if sx is None or side_of(c) == sx: return o, pts, c
    J = {}
    allz = [p.z for o in meshes for p in wverts(o)]
    J["top"] = max(allz)
    hp = find("Head")[1]; J["head_c"] = sum(hp, Vector()) / len(hp); J["head_bot"] = min(p.z for p in hp)
    npts = find("Neck")[1]; J["neck"] = Vector((0, sum(p.y for p in npts) / len(npts), min(p.z for p in npts)))
    for sx in (-1, 1):
        ua = find("Upper arm", sx); a, b, _ = endpoints(ua[1]); sh, el0 = (a, b) if a.z > b.z else (b, a)
        elg = find("Elbow", sx); el = elg[2] if elg else el0
        fa = find("Forearm", sx); a, b, _ = endpoints(fa[1]); wr = a if (a - el).length > (b - el).length else b
        J[("sh", sx)], J[("el", sx)], J[("wr", sx)] = sh, el, wr
        legs = [(o, pts, c) for nm in LEG_P for (o, pts, c) in parts.get(nm, []) if side_of(c) == sx]
        lp = [p for (_, pts, _) in legs for p in pts]
        hipz = min(p.z for p in find("Trouser hips")[1]) + 0.04 * SCALE
        foot = find("Foot", sx)[1]; ankz = max(p.z for p in foot)
        kn = find("Knee", sx)
        knz = kn[2].z if kn else ankz + 0.47 * (hipz - ankz)
        hx = sum(p.x for p in lp if p.z > hipz - 0.25 * SCALE) / max(1, len([p for p in lp if p.z > hipz - 0.25 * SCALE]))
        J[("hip", sx)] = Vector((hx, 0, hipz)); J[("knee", sx)] = Vector((hx, 0, knz))
    sm = find("Smile")[2]; J["mouth"] = sm
    lids = [c for (o, pts, c) in parts.get("Upper eyelid", [])]
    lidtop = max(p.z for (o, pts, c) in parts.get("Upper eyelid", []) for p in pts)
    J["lid"] = Vector((0, sum(c.y for c in lids) / len(lids), lidtop))
    J["body"] = Vector((0, 0, J[("hip", 1)].z))

    # --- armature (all bones point +Z, so their axes match world axes up to a fixed rotation) ---
    ad = bpy.data.armatures.new(name + "_arm"); arm = bpy.data.objects.new(name, ad); sc.collection.objects.link(arm)
    for o in bpy.context.selected_objects: o.select_set(False)
    bpy.context.view_layer.objects.active = arm; arm.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    def eb(nm, pos, parent=None):
        b = ad.edit_bones.new(nm); b.head = pos; b.tail = pos + Vector((0, 0, 0.1)); b.roll = 0
        if parent: b.parent = ad.edit_bones[parent]
        return b
    eb("body", J["body"]); eb("head", J["neck"], "body"); eb("mouth", J["mouth"], "head"); eb("lid", J["lid"], "head")
    for sx in (-1, 1):
        t = "R" if sx < 0 else "L"
        eb("sh." + t, J[("sh", sx)], "body"); eb("el." + t, J[("el", sx)], "sh." + t); eb("hand." + t, J[("wr", sx)], "el." + t)
        eb("hip." + t, J[("hip", sx)], "body"); eb("knee." + t, J[("knee", sx)], "hip." + t)
    bpy.ops.object.mode_set(mode="OBJECT")

    # --- vertex groups per part ---
    def wgt(o, pts, fn):
        groups = {}
        for i, p in enumerate(pts):
            for g, w in fn(p):
                if w > 0.001: groups.setdefault(g, []).append((i, w))
        for g, lst in groups.items():
            vg = o.vertex_groups.get(g) or o.vertex_groups.new(name=g)
            for i, w in lst: vg.add([i], w, "REPLACE")
    def blend(z, z0, band, lo, hi):
        t = max(0.0, min(1.0, (z - (z0 - band)) / (2 * band)))
        return [(hi, t), (lo, 1 - t)]
    for nm, lst in parts.items():
        for (o, pts, c) in lst:
            sx = side_of(c); t = "R" if sx < 0 else "L"
            if nm in MOUTH_P: wgt(o, pts, lambda p: [("mouth", 1.0)])
            elif nm == "Upper eyelid": wgt(o, pts, lambda p: [("lid", 1.0)])
            elif nm in HEAD_P: wgt(o, pts, lambda p: [("head", 1.0)])
            elif nm == "Neck": wgt(o, pts, lambda p: blend(p.z, J["neck"].z + 0.04 * SCALE, 0.03 * SCALE, "body", "head"))
            elif nm in FORE_P: wgt(o, pts, lambda p, t=t: [("el." + t, 1.0)])
            elif nm in UPPER_P or nm == "Tailored shoulder bridge":
                shz = J[("sh", sx)]
                if nm in ("Short sleeve", "Tailored shoulder bridge"):
                    wgt(o, pts, lambda p, t=t, shz=shz: [("sh." + t, max(0.0, min(1.0, 0.35 + (shz.z - p.z) / (0.08 * SCALE) + abs(p.x - shz.x) * 0.0))),
                                                        ("body", 1 - max(0.0, min(1.0, 0.35 + (shz.z - p.z) / (0.08 * SCALE))))])
                else: wgt(o, pts, lambda p, t=t: [("sh." + t, 1.0)])
            elif nm in LEG_P:
                kz = J[("knee", sx)].z
                wgt(o, pts, lambda p, t=t, kz=kz: blend(p.z, kz, 0.045 * SCALE, "hip." + t, "knee." + t))
            elif nm == "Trouser hips":
                hz = J[("hip", 1)].z
                wgt(o, pts, lambda p, sx=sx: [("body", max(0.0, min(1.0, (p.z - (hz - 0.06 * SCALE)) / (0.12 * SCALE)))),
                                              ("hip." + ("R" if p.x < 0 else "L"), 1 - max(0.0, min(1.0, (p.z - (hz - 0.06 * SCALE)) / (0.12 * SCALE))))])
            else: wgt(o, pts, lambda p: [("body", 1.0)])
    # --- join into one mesh, bind to armature ---
    for o in bpy.context.selected_objects: o.select_set(False)
    for o in meshes:
        mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw; o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.join()
    body = bpy.context.view_layer.objects.active; body.name = name + "_mesh"
    for o in new:
        if o.name in bpy.data.objects and o != body and o.type != "MESH":
            bpy.data.objects.remove(o, do_unlink=True)
    body.parent = arm
    md = body.modifiers.new("arm", "ARMATURE"); md.object = arm
    for p in body.data.polygons: p.use_smooth = True
    arm.data.display_type = "STICK"; arm.show_in_front = True
    P = arm.pose.bones
    for pb in P: pb.rotation_mode = "XYZ"
    rig = {"root": arm, "mesh": body, "body": P["body"], "head": P["head"], "mouth": P["mouth"], "lid": P["lid"],
           "arms": [(P["sh.R"], P["el.R"], P["hand.R"]), (P["sh.L"], P["el.L"], P["hand.L"])], "sx": [-1, 1],
           "legs": [(P["hip.R"], P["knee.R"]), (P["hip.L"], P["knee.L"])], "fingers": [[], []], "J": J}
    L1, L2 = [], []; rest = []
    for sx in (-1, 1):
        sh, el, wr = J[("sh", sx)], J[("el", sx)], J[("wr", sx)]
        L1.append((el - sh).length); L2.append((wr - el).length)
        pu = math.atan2(sx * (el.x - sh.x), -(el.z - sh.z)); pf = math.atan2(sx * (wr.x - el.x), -(wr.z - el.z))
        rest.append((pu, pf - pu))
    rig["L"] = (sum(L1) / 2, sum(L2) / 2); rig["rest"] = rest
    rig["hz"] = J["head_c"].z; rig["top"] = J["top"]
    return rig

for k in KIDS: R[k] = build_model(k)
ALL = list(KIDS)

# ---------------- animation helpers (bones keyed in world-aligned terms) ----------------
_B = Matrix(((1, 0, 0), (0, 0, -1), (0, 1, 0)))     # rest orientation of a +Z bone with roll 0
_Bi = _B.inverted()
def kloc(o, f, loc=None, idx=-1):
    if isinstance(o, bpy.types.PoseBone):
        if loc is not None: o.location = _Bi @ Vector(loc)
        o.keyframe_insert("location", frame=f); return
    if loc is not None: o.location = loc
    o.keyframe_insert("location", index=idx, frame=f)
def krot(o, f, rot=None, idx=-1):
    if isinstance(o, bpy.types.PoseBone):
        if rot is not None:
            Rw = Euler(rot, "XYZ").to_matrix()
            o.rotation_euler = (_Bi @ Rw @ _B).to_euler("XYZ", o.rotation_euler)
        o.keyframe_insert("rotation_euler", frame=f); return
    if rot is not None: o.rotation_euler = rot
    o.keyframe_insert("rotation_euler", index=idx, frame=f)
def kscale(pb, f, s):
    pb.scale = _Bi @ Vector(s) if False else (s[0], s[2], s[1]); pb.keyframe_insert("scale", frame=f)
def arm_ik(ox, oz, L1, L2):
    d = max(0.05, min(L1 + L2 - 0.01, math.hypot(ox, oz)))
    phi_t = math.atan2(ox, -oz)
    a = math.acos(max(-1, min(1, (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))))
    p1 = phi_t + a
    ex, ez = L1 * math.sin(p1), -L1 * math.cos(p1); tx, tz = d * math.sin(phi_t), -d * math.cos(phi_t)
    return p1, math.atan2(tx - ex, -(tz - ez)) - p1

ARM_POSES = {
    "idle": [(0.16, -0.95, 0.05), (0.16, -0.95, 0.05)], "talk": [(0.5, -0.45, -0.4), (0.16, -0.95, 0.05)],
    "talk2": [(0.55, -0.25, -0.5), (0.16, -0.95, 0.05)], "cheer": [(0.4, 0.88, -0.1), (0.4, 0.88, -0.1)],
    "point": [(0.06, -0.08, -1.25), (0.16, -0.95, 0.05)], "point_up": [(0.2, 0.92, -0.3), (0.16, -0.95, 0.05)],
    "point_left": [(0.92, 0.08, -0.25), (0.16, -0.95, 0.05)], "point_right": [(0.16, -0.95, 0.05), (0.92, 0.08, -0.25)],
    "hips": [(0.3, -0.6, 0.3), (0.3, -0.6, 0.3)], "ears": [(-0.05, 0.86, -0.1), (-0.05, 0.86, -0.1)],
    "shrug": [(0.6, -0.1, -0.3), (0.6, -0.1, -0.3)], "laugh": [(-0.15, -0.7, -0.6), (-0.15, -0.7, -0.6)],
    "wave": [(0.45, 0.8, -0.15), (0.16, -0.95, 0.05)], "carry": [(-0.05, 0.0, -1.1), (-0.05, 0.0, -1.1)],
    "pat": [(0.8, 0.35, -0.35), (0.16, -0.95, 0.05)], "spin": [(0.92, 0.0, 0), (0.92, 0.0, 0)],
    "sparkle": [(0.62, 0.05, -0.75), (0.16, -0.95, 0.05)], "reach": [(0.06, -0.8, -1.1), (0.16, -0.95, 0.05)],
    "walk": [(0.16, -0.95, 0.0), (0.16, -0.95, 0.0)],
}
def set_arms(who, f, pose, wob=(0, 0), fwd_add=0.0):
    rig = R[who]; L1, L2 = rig["L"]; Lt = L1 + L2
    for i, ((sh, el, hd), sx) in enumerate(zip(rig["arms"], rig["sx"])):
        ox, oz, fwd = ARM_POSES[pose][i]
        if i == 0: ox += wob[0]; oz += wob[1]
        p1, rel = arm_ik(ox * Lt, oz * Lt, L1, L2)
        pu, prel = rig["rest"][i]
        s = 1 if sx == 1 else -1
        krot(sh, f, (fwd + fwd_add * (1 if i else -1), -s * (p1 - pu), 0)); krot(el, f, (0, -s * (rel - prel), 0))

def set_legs(who, f, a_l=0.0, k_l=0.0, a_r=0.0, k_r=0.0):
    (h0, k0), (h1, k1) = R[who]["legs"]
    krot(h0, f, (a_l, 0, 0)); krot(k0, f, (k_l, 0, 0)); krot(h1, f, (a_r, 0, 0)); krot(k1, f, (k_r, 0, 0))
def stand(who, f):
    set_legs(who, f); kloc(R[who]["body"], f, (0, 0, 0)); krot(R[who]["body"], f, (0, 0, 0))

def walk(who, f0, f1, p0, p1, run=False, face_dir=True):
    rig = R[who]; root, body = rig["root"], rig["body"]
    kloc(root, f0, (p0[0], p0[1], 0)); kloc(root, f1, (p1[0], p1[1], 0))
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    yaw = math.atan2(dx, -dy) if face_dir and (abs(dx) + abs(dy)) > 0.05 else 0.0
    krot(root, max(1, f0 - 2), (0, 0, root.rotation_euler.z)); krot(root, f0 + 3, (0, 0, yaw))
    krot(root, f1 - 2, (0, 0, yaw)); krot(root, f1 + 4, (0, 0, 0))
    P = 10 if run else 16
    A, B, bob = (0.7, 1.2, 0.08) if run else (0.42, 0.75, 0.04)
    f = f0; i = 0
    while f < f1:
        ph = i % 4
        if ph == 0: set_legs(who, f, -A, 0.15, A, 0.4); kloc(body, f, (0, 0, -0.03))
        elif ph == 1: set_legs(who, f, 0, 0.1, 0, B); kloc(body, f, (0, 0, bob))
        elif ph == 2: set_legs(who, f, A, 0.4, -A, 0.15); kloc(body, f, (0, 0, -0.03))
        else: set_legs(who, f, 0, B, 0, 0.1); kloc(body, f, (0, 0, bob))
        set_arms(who, f, "walk", fwd_add=[-0.5, 0, 0.5, 0][ph] * (1.4 if run else 1.0))
        krot(body, f, (math.radians(-10 if run else -3), 0, 0))
        f += P // 4; i += 1
    stand(who, f1 + 2)

def talk_motion(who, f0, f1, gesture):
    rig = R[who]; body, head = rig["body"], rig["head"]
    k = 0; f = f0
    while f < f1:
        on = k % 2 == 0
        krot(head, f, (math.radians(-4 if on else 2), 0, math.radians(3 if on else -3)))
        krot(body, f, (0, 0, math.radians(3 if on else -3)))
        if gesture in ("talk", "talk2"): set_arms(who, f, "talk" if on else "talk2")
        elif gesture in ("wave", "sparkle"): set_arms(who, f, gesture, wob=(0.15 * math.cos(k * 1.7), 0.15 * math.sin(k * 1.7)))
        elif gesture == "laugh": set_arms(who, f, "laugh"); kloc(body, f, (0, 0, 0.05 if on else 0))
        else: set_arms(who, f, gesture if gesture in ARM_POSES else "talk")
        f += 5; k += 1
    krot(head, f1, (0, 0, 0)); krot(body, f1, (0, 0, 0))
    # mouth flaps faster than the gestures
    m = rig["mouth"]; f = f0; k = 0
    kscale(m, f0 - 1, (1, 1, 1))
    while f < f1:
        kscale(m, f, (1.15, 1, 1.9 if k % 2 == 0 else 0.8)); f += 3; k += 1
    kscale(m, f1, (1, 1, 1))

# idle life: blinks + breathing for everyone
for n_, k in enumerate(KIDS):
    lid = R[k]["lid"]; f = 20 + n_ * 17
    kscale(lid, 1, (1, 1, 1))
    while f < N:
        kscale(lid, f, (1, 1, 1)); kscale(lid, f + 2, (1, 1, 3.2)); kscale(lid, f + 4, (1, 1, 1))
        f += int(60 + rnd.random() * 50)
    for f in range(1, N, 48):
        kloc(R[k]["head"], f, (0, 0, 0)); kloc(R[k]["head"], f + 24, (0, 0, 0.006))

# sparklers attached to the right hand
def attach(o, rig, bone):
    mw = o.matrix_world.copy()
    o.parent = rig["root"]; o.parent_type = "BONE"; o.parent_bone = bone
    bpy.context.view_layer.update(); o.matrix_world = mw
SPARK = {}
for k in KIDS:
    wr = R[k]["J"][("wr", -1)]
    st = cyl((wr.x - 0.02, wr.y - 0.18, wr.z - 0.12), 0.008, 0.55, mat((140, 140, 150)), None, rot=(math.radians(70), 0, 0))
    tp = emitter("sparkler_" + k, (wr.x - 0.02, wr.y - 0.42, wr.z - 0.03), kind="sphere", size=0.03)
    Ls = plight((wr.x - 0.02, wr.y - 0.42, wr.z), 0, (1, 0.9, 0.7), 0.1)
    for o in (st, tp, Ls): attach(o, R[k], "hand.R")
    SPARK[k] = (st, tp, Ls)
