# ===== Episode 13 (THE ZOO) props: executed inside build8 (has CH, SETS, TL, F, sets2, Vector, math, bpy, random, head_world, vfx, END) =====
import vfx, colorsys
from mathutils import Euler
gd = SETS["zoo"]; O = gd["origin"]; c = gd["coll"]
def key_vis(obj, f, v):
    for o in [obj] + list(obj.children_recursive):
        o.hide_render = not v; o.hide_viewport = not v
        o.keyframe_insert("hide_render", frame=max(1, f)); o.keyframe_insert("hide_viewport", frame=max(1, f))
def W(x, y, z=0.0): return Vector((O.x + x, O.y + y, z))
EV = sorted([e for e in TL["events"] if e["type"] == "prop"], key=lambda e: e["t"])

# ---------------- Zoomy (same design as Ep 8) ----------------
body_m = sets2.M("zoomy13_body", (0.93, 0.94, 0.96), 0.25, coat=0.8)
top_m = sets2.M("zoomy13_top", (0.12, 0.13, 0.16), 0.2, coat=1.0)
bump_m = sets2.M("zoomy13_bump", (0.25, 0.25, 0.28), 0.5)
eye_m = sets2.M("zoomy13_eye", (1, 1, 1), 0.3, emit=(0.3, 0.7, 1.0), emit_str=4.0)
pupil_m = sets2.M("zoomy13_pupil", (0.02, 0.02, 0.03), 0.3)
zoomy = bpy.data.objects.new("zoomy13", None); c.objects.link(zoomy)
parts = [sets2.cyl("zoomy13_body", 0.19, 0.07, (0, 0, 0.045), body_m, c, 48, bevel=0.01),
         sets2.cyl("zoomy13_top", 0.15, 0.012, (0, 0, 0.083), top_m, c, 48, bevel=0.003),
         sets2.cyl("zoomy13_bumper", 0.195, 0.03, (0, 0, 0.03), bump_m, c, 48, bevel=0.004)]
for sx in (-1, 1):
    parts.append(sets2.sph(f"zoomy13_eye{sx}", 0.035, (sx * 0.06, -0.15, 0.085), eye_m, c, scale=(1, 0.6, 1), seg=16))
    parts.append(sets2.sph(f"zoomy13_pup{sx}", 0.016, (sx * 0.06, -0.172, 0.09), pupil_m, c, seg=10))
parts.append(sets2.cyl("zoomy13_led", 0.155, 0.006, (0, 0, 0.09), eye_m, c, 48, bevel=0))
# mud coat that appears on Zoomy in MUD MODE and washes off in the pool
mudcoat_m = sets2.M("zoomy13_mudc", (0.26, 0.16, 0.08), 0.5, bump=0.8, bump_scale=20)
mudcoat = []
for k in range(7):
    a = k / 7 * 2 * math.pi
    b_ = sets2.sph(f"zoomy13_mud{k}", 0.05 + 0.015 * (k % 3), (0.13 * math.cos(a), 0.13 * math.sin(a), 0.07), mudcoat_m, c, scale=(1, 1, 0.45), seg=10); mudcoat.append(b_)
for p_ in parts + mudcoat: p_.parent = zoomy
for b_ in mudcoat: key_vis(b_, 1, False)
brush = bpy.data.objects.new("zoomy13_brushp", None); c.objects.link(brush); brush.parent = zoomy; brush.location = (0.13, -0.12, 0.01)
for k in range(3):
    b_ = sets2.box(f"zoomy13_br{k}", (0.09, 0.006, 0.006), (0, 0, 0), bump_m, c, 0); b_.rotation_euler = (0, 0, k * 2.094); b_.parent = brush
for f in range(1, END + 1, 2): brush.rotation_euler = (0, 0, f * 0.9); brush.keyframe_insert("rotation_euler", frame=f)
ZK = {}; ZZ = {}   # frame -> (x, y, yaw) ; frame -> z
def zkey(f, x, y, yaw, z=None):
    ZK[int(f)] = (x, y, yaw)
    if z is not None: ZZ[int(f)] = z
def zpos(f):
    ks = sorted(k for k in ZK if k <= f)
    return ZK[ks[-1]] if ks else (0.3, 0.5, 0.0)
def zz(f):
    ks = sorted(k for k in ZZ if k <= f)
    return ZZ[ks[-1]] if ks else 0.0
def heading(a, b): return math.atan2(-(b[0] - a[0]), (b[1] - a[1])) + math.pi
TRACKS = []
def path(f0, pts, dur, turbo, tracks=False):
    seg = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    lens = [math.dist(a, b) for a, b in seg]; tot = sum(lens) or 1
    n = max(2, int(dur * 24)); last = None
    for i in range(n + 1):
        u = i / n * tot; acc = 0
        for (a, b), L_ in zip(seg, lens):
            if acc + L_ >= u or (a, b) == seg[-1]:
                k = (u - acc) / L_ if L_ else 0; k = min(1, k)
                x = a[0] + (b[0] - a[0]) * k; y = a[1] + (b[1] - a[1]) * k
                yaw = heading(a, b) + (0.18 * math.sin(i * 1.3) if turbo else 0)
                zkey(f0 + i, x, y, yaw, 0.0)
                if tracks and (last is None or math.dist(last, (x, y)) > 0.22):
                    TRACKS.append((f0 + i, x, y, yaw)); last = (x, y)
                break
            acc += L_

# ---------------- items ----------------
# upside-down green bucket Zoomy hides under (cold open)
bucket_m = sets2.M("bucket9", (0.25, 0.8, 0.35), 0.35, coat=0.5)
bucket = bpy.data.objects.new("bucket9", None); c.objects.link(bucket)
bk_ = sets2.cyl("bucket9_b", 0.23, 0.3, (0, 0, 0.15), bucket_m, c, 32, bevel=0.01); bk_.parent = bucket
bk2 = sets2.cyl("bucket9_rim", 0.245, 0.03, (0, 0, 0.015), bucket_m, c, 32, bevel=0.005); bk2.parent = bucket
BUCKET = {"cover": None, "off": None}
# water buckets the kids carry (blue, with water inside)
EYE = {"blue": (0.3, 0.7, 1.0), "red": (1.0, 0.1, 0.1), "green": (0.2, 1.0, 0.35), "orange": (1.0, 0.5, 0.05)}
ec = eye_m.node_tree.nodes["Principled BSDF"].inputs["Emission Color"]
ec.default_value = (*EYE["blue"], 1); ec.keyframe_insert("default_value", frame=1)
gir = gd["giraffe"]; G0 = gir.rotation_euler.copy(); gir.keyframe_insert("rotation_euler", frame=1)
trunk = gd["trunk"]; trunk.rotation_euler = (0, 0, 0); trunk.keyframe_insert("rotation_euler", frame=1)
monk = gd["monkeys"][1]; MK0 = monk.location.copy(); monk.keyframe_insert("location", frame=1); monk.keyframe_insert("rotation_euler", frame=1)
for i, m_ in enumerate(gd["monkeys"]):   # idle bobbing
    z0 = m_.location.z
    for f in range(1, END + 1, 12):
        if m_ is monk: continue
        m_.location.z = z0 + 0.04 * abs(math.sin(f / 12.0 + i)); m_.keyframe_insert("location", index=2, frame=f)
PEN = gd["penguins"]; P0 = [p.location.copy() for p in PEN]
for p in PEN: p.keyframe_insert("location", frame=1); p.keyframe_insert("rotation_euler", frame=1)
def waddle(p, f, loc, yaw):
    p.location = loc; p.rotation_euler = (0, 0.18 * math.sin(f * 0.6), yaw); p.keyframe_insert("location", frame=f); p.keyframe_insert("rotation_euler", frame=f)
def cone_obj(name):
    g = bpy.data.objects.new(name, None); c.objects.link(g)
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.04, radius2=0.0, depth=0.14, location=(0, 0, -0.07), rotation=(math.pi, 0, 0))
    cn = bpy.context.active_object; cn.name = name + "_cone"
    for cc in list(cn.users_collection): cc.objects.unlink(cn)
    c.objects.link(cn); cn.data.materials.append(sets2.M("ic_cone", (0.85, 0.6, 0.3), 0.8)); cn.parent = g
    sc_ = sets2.sph(name + "_scoop", 0.05, (0, 0, 0.02), sets2.M("ic_straw", (1.0, 0.6, 0.75), 0.5), c, seg=12); sc_.parent = g
    return g
ice = cone_obj("icecream13"); key_vis(ice, 1, False)
def hand(k, f):
    sc_ = bpy.context.scene; sc_.frame_set(f); bpy.context.view_layer.update()
    arm = CH[k]["arm"]; pb = [b for b in arm.pose.bones if b.name.endswith("RightHand")][0]
    return (arm.matrix_world @ pb.matrix).translation.copy()
for e in EV:
    f = F(e["t"]); nm = e["name"]; a = e["action"]
    if nm == "zoomy":
        if a == "place": zkey(f, *e["at"], 0.0, 0.0); zkey(f + 1, *e["at"], 0.0, 0.0)
        elif a == "path": path(f, e["pts"], e["dur"], e.get("turbo", False))
        elif a == "spin":
            x_, y_, yw = zpos(f); n = int(e["dur"] * 24)
            for i in range(n + 1): zkey(f + i, x_ + 0.08 * math.sin(i / 8.0), y_ + 0.06 * math.cos(i / 11.0), yw + i * 0.3, 0.0)
        elif a == "eyes":
            col_ = e["color"]
            if col_ == "rainbow":
                for i in range(0, 24 * 6, 3):
                    r_, g_, b_ = colorsys.hsv_to_rgb((i / 30.0) % 1, 1, 1); ec.default_value = (r_, g_, b_, 1); ec.keyframe_insert("default_value", frame=f + i)
                ec.default_value = (*EYE["blue"], 1); ec.keyframe_insert("default_value", frame=f + 24 * 6)
            else: ec.default_value = (*EYE[col_], 1); ec.keyframe_insert("default_value", frame=f)
    elif nm == "giraffe":
        if a == "bend":
            n = int(e["dur"] * 24); gir.rotation_euler = G0; gir.keyframe_insert("rotation_euler", frame=f)
            gir.rotation_euler = (G0.x + math.radians(28), G0.y, G0.z + math.radians(25)); gir.keyframe_insert("rotation_euler", frame=f + n)
        elif a == "up":
            gir.keyframe_insert("rotation_euler", frame=f); gir.rotation_euler = G0; gir.keyframe_insert("rotation_euler", frame=f + int(e["dur"] * 24))
    elif nm == "trunk":
        if a == "aim":
            trunk.rotation_euler = (0, 0, 0); trunk.keyframe_insert("rotation_euler", frame=f)
            trunk.rotation_euler = (math.radians(-75), 0, math.radians(-20)); trunk.keyframe_insert("rotation_euler", frame=f + 18)
        elif a == "rest":
            trunk.keyframe_insert("rotation_euler", frame=f); trunk.rotation_euler = (0, 0, 0); trunk.keyframe_insert("rotation_euler", frame=f + 18)
    elif nm == "spray" and a == "on":
        n = int(e["dur"] * 24); bpy.context.scene.frame_set(f); bpy.context.view_layer.update()
        tip = trunk.matrix_world.translation + Vector((0, -0.6, -0.3))
        if e["to"] == "zoomy": x_, y_, _ = zpos(f); tgt = W(x_, y_, 0.1)
        else: tgt = head_world(e["to"], f)
        vel = (tgt - tip); vel.z += 1.0
        vfx.emitter(f"spray13_{f}", tuple(tip), c, 260, f, f + n, 18, (0.6, 0.85, 1.0), size=0.016, vel_obj=tuple(vel.normalized() * 1.0), vel_rand=0.25,
                    gravity=0.6, strength=1.2, radius=0.04)
        vfx.emitter(f"splsh13_{f}", tuple(tgt), c, 120, f + 8, f + n + 4, 16, (0.6, 0.85, 1.0), size=0.014, vel_rand=1.3, gravity=1.0, strength=1.2, radius=0.1)
    elif nm == "icecream" and a == "give":
        con = ice.constraints.new("COPY_LOCATION"); arm = CH[e["who"]]["arm"]
        con.target = arm; con.subtarget = [b for b in arm.pose.bones if b.name.endswith("RightHand")][0].name
        key_vis(ice, f, True); ICE_CON = con
    elif nm == "monkey":
        if a == "steal":
            n = int(e["dur"] * 24); h = hand(e["who"], f + n // 2)
            mid = (MK0 + h) / 2 + Vector((0, 0, 1.2))
            for i in range(0, n // 2 + 1, 2):
                u = i / (n // 2); monk.location = (MK0.lerp(mid, u) if u < 0.5 else mid.lerp(h - Vector((0, 0, 0.35)), (u - 0.5) * 2)) if False else MK0.lerp(h - Vector((0, 0.15, 0.4)), u) + Vector((0, 0, 1.0 * math.sin(u * math.pi)))
                monk.keyframe_insert("location", frame=f + i)
            fg = f + n // 2
            ICE_CON.influence = 1.0; ICE_CON.keyframe_insert("influence", frame=fg)
            ICE_CON.influence = 0.0; ICE_CON.keyframe_insert("influence", frame=fg + 1)
            ice.parent = None
            for i in range(0, n // 2 + 1, 2):
                u = i / (n // 2); p_ = (h - Vector((0, 0.15, 0.4))).lerp(MK0, u) + Vector((0, 0, 1.0 * math.sin(u * math.pi)))
                monk.location = p_; monk.keyframe_insert("location", frame=fg + i)
                ice.location = p_ + Vector((0.1, -0.12, 0.45)); ice.keyframe_insert("location", frame=fg + i)
            ice.location = MK0 + Vector((0.1, -0.12, 0.45)); ice.keyframe_insert("location", frame=fg + n // 2 + 2)
        elif a == "lick":
            for i in range(0, 48, 6):
                monk.rotation_euler = (0.25 * (i // 6 % 2), 0, 0); monk.keyframe_insert("rotation_euler", frame=f + i)
    elif nm == "penguins":
        if a == "follow":
            n = int(e["dur"] * 24)
            for j, p in enumerate(PEN):
                lag = 10 + j * 9
                for i in range(0, n + 1, 3):
                    x_, y_, yw = zpos(max(1, f + i - lag)); waddle(p, f + i, W(x_, y_ + 0.0, 0.0), yw)
        elif a == "home":
            for j, p in enumerate(PEN): waddle(p, f, P0[j], 0.0)
for fz in sorted(ZK):
    x_, y_, yw = ZK[fz]; zoomy.location = W(x_, y_, zz(fz)); zoomy.rotation_euler = (0, 0, yw)
    zoomy.keyframe_insert("location", frame=fz); zoomy.keyframe_insert("rotation_euler", frame=fz)
if zoomy.animation_data and zoomy.animation_data.action:
    for fc in zoomy.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
def _zcam(f0, f1, dist=0.85, h=0.36, lens=30):
    x_, y_, yw = zpos(f0 + 2); p = W(x_ + 0.15, y_ - dist, h); t = W(x_, y_, 0.1)
    return (tuple(p), tuple(t), lens)
gd["cams"]["insert:zoomy"] = lambda f0, f1: _zcam(f0, f1)
for ob in list(bpy.data.objects):
    ad = ob.animation_data
    if ad and ad.action:
        for fc in ad.action.fcurves:
            if "hide" in fc.data_path or "influence" in fc.data_path:
                for kp in fc.keyframe_points: kp.interpolation = "CONSTANT"
print("props_ep13 ok: zoomy keys", len(ZK))
