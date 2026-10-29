# ===== Episode 9 (WHERE'S ZOOMY? backyard garden) props: executed inside build8 (has CH, SETS, TL, F, sets2, Vector, math, bpy, random, head_world, vfx, END) =====
import vfx, colorsys
from mathutils import Euler
gd = SETS["garden"]; O = gd["origin"]; c = gd["coll"]
def key_vis(obj, f, v):
    for o in [obj] + list(obj.children_recursive):
        o.hide_render = not v; o.hide_viewport = not v
        o.keyframe_insert("hide_render", frame=max(1, f)); o.keyframe_insert("hide_viewport", frame=max(1, f))
def W(x, y, z=0.0): return Vector((O.x + x, O.y + y, z))
EV = sorted([e for e in TL["events"] if e["type"] == "prop"], key=lambda e: e["t"])
PX, PY = gd["pool"][0] - O.x, gd["pool"][1] - O.y
POOL_Z = 0.24   # Zoomy's base height when floating

# ---------------- Zoomy (same design as Ep 8) ----------------
body_m = sets2.M("zoomy9_body", (0.93, 0.94, 0.96), 0.25, coat=0.8)
top_m = sets2.M("zoomy9_top", (0.12, 0.13, 0.16), 0.2, coat=1.0)
bump_m = sets2.M("zoomy9_bump", (0.25, 0.25, 0.28), 0.5)
eye_m = sets2.M("zoomy9_eye", (1, 1, 1), 0.3, emit=(0.3, 0.7, 1.0), emit_str=4.0)
pupil_m = sets2.M("zoomy9_pupil", (0.02, 0.02, 0.03), 0.3)
zoomy = bpy.data.objects.new("zoomy9", None); c.objects.link(zoomy)
parts = [sets2.cyl("zoomy9_body", 0.19, 0.07, (0, 0, 0.045), body_m, c, 48, bevel=0.01),
         sets2.cyl("zoomy9_top", 0.15, 0.012, (0, 0, 0.083), top_m, c, 48, bevel=0.003),
         sets2.cyl("zoomy9_bumper", 0.195, 0.03, (0, 0, 0.03), bump_m, c, 48, bevel=0.004)]
for sx in (-1, 1):
    parts.append(sets2.sph(f"zoomy9_eye{sx}", 0.035, (sx * 0.06, -0.15, 0.085), eye_m, c, scale=(1, 0.6, 1), seg=16))
    parts.append(sets2.sph(f"zoomy9_pup{sx}", 0.016, (sx * 0.06, -0.172, 0.09), pupil_m, c, seg=10))
parts.append(sets2.cyl("zoomy9_led", 0.155, 0.006, (0, 0, 0.09), eye_m, c, 48, bevel=0))
# mud coat that appears on Zoomy in MUD MODE and washes off in the pool
mudcoat_m = sets2.M("zoomy9_mudc", (0.26, 0.16, 0.08), 0.5, bump=0.8, bump_scale=20)
mudcoat = []
for k in range(7):
    a = k / 7 * 2 * math.pi
    b_ = sets2.sph(f"zoomy9_mud{k}", 0.05 + 0.015 * (k % 3), (0.13 * math.cos(a), 0.13 * math.sin(a), 0.07), mudcoat_m, c, scale=(1, 1, 0.45), seg=10); mudcoat.append(b_)
for p_ in parts + mudcoat: p_.parent = zoomy
for b_ in mudcoat: key_vis(b_, 1, False)
brush = bpy.data.objects.new("zoomy9_brushp", None); c.objects.link(brush); brush.parent = zoomy; brush.location = (0.13, -0.12, 0.01)
for k in range(3):
    b_ = sets2.box(f"zoomy9_br{k}", (0.09, 0.006, 0.006), (0, 0, 0), bump_m, c, 0); b_.rotation_euler = (0, 0, k * 2.094); b_.parent = brush
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
def water_bucket(name):
    g = bpy.data.objects.new(name, None); c.objects.link(g)
    b1 = sets2.cyl(name + "_b", 0.11, 0.18, (0, 0, -0.17), sets2.M("wbucket9", (0.2, 0.5, 0.95), 0.35, coat=0.5), c, 24, bevel=0.005); b1.parent = g
    b2 = sets2.cyl(name + "_w", 0.1, 0.01, (0, 0, -0.09), sets2.M("wbucket9_w", (0.45, 0.8, 1.0), 0.05, coat=1.0, emit=(0.4, 0.75, 1.0), emit_str=0.3), c, 24, bevel=0); b2.parent = g
    h_ = sets2.box(name + "_h", (0.008, 0.008, 0.1), (0, 0, -0.04), sets2.M("wbucket9_h", (0.6, 0.6, 0.62), 0.3, 0.8), c, 0); h_.parent = g
    return g
# giant prize carrot in the veggie patch
carrot = bpy.data.objects.new("bigcarrot9", None); c.objects.link(carrot)
CR0 = (-1.85, 2.05, 0.22); carrot.location = W(*CR0)
cr_ = sets2.cyl("bigcarrot9_b", 0.07, 0.36, (0, 0, -0.1), sets2.M("bigcarrot9_m", (1.0, 0.45, 0.06), 0.5, bump=0.4, bump_scale=40), c, 20, bevel=0.02); cr_.parent = carrot
cr_.scale = (1, 1, 1)
tip = sets2.sph("bigcarrot9_tip", 0.07, (0, 0, -0.28), sets2.M("bigcarrot9_m", (1.0, 0.45, 0.06), 0.5), c, scale=(1, 1, 1.4), seg=14); tip.parent = carrot
for j in range(5):
    l_ = sets2.box(f"bigcarrot9_l{j}", (0.03, 0.008, 0.3), (0.02 * (j - 2), 0, 0.22), sets2.M("gd_leaf2", (0.25, 0.65, 0.18), 0.7), c, 0.003, rot=(0.3 * (j - 2), 0.2 * (j - 2), j)); l_.parent = carrot
# crumbs
crumb_m = sets2.M("crumb9", (0.6, 0.38, 0.15), 0.9)
track_m = sets2.M("track9", (0.2, 0.12, 0.05), 0.6)
mudblob_m = sets2.M("mudblob9", (0.27, 0.17, 0.08), 0.55, bump=0.6, bump_scale=25)
poolw = gd["poolwater"]; poolw.location.z = 0.2; poolw.keyframe_insert("location", frame=1)
spr = gd["sprinkler"]; SPX, SPY = gd["spr_xy"]

# ---------------- events ----------------
EYE = {"blue": (0.3, 0.7, 1.0), "red": (1.0, 0.1, 0.1), "green": (0.2, 1.0, 0.35), "orange": (1.0, 0.5, 0.05)}
ec = eye_m.node_tree.nodes["Principled BSDF"].inputs["Emission Color"]
ec.default_value = (*EYE["blue"], 1); ec.keyframe_insert("default_value", frame=1)
key_vis(bucket, 1, False)
float_f = None
for e in EV:
    f = F(e["t"]); nm = e["name"]; a = e["action"]
    if nm == "zoomy":
        if a == "place": zkey(f, *e["at"], 0.0, 0.0); zkey(f + 1, *e["at"], 0.0, 0.0)
        elif a == "path": path(f, e["pts"], e["dur"], e.get("turbo", False), e.get("tracks", False))
        elif a == "spin":
            x_, y_, yw = zpos(f); n = int(e["dur"] * 24); z0 = zz(f); slow = e.get("slow", False)
            for i in range(n + 1):
                if slow: zkey(f + i, x_ + 0.05 * math.sin(i / 14.0), y_ + 0.05 * math.cos(i / 17.0), yw + i * 0.06, z0 + 0.015 * math.sin(i / 6.0))
                else: zkey(f + i, x_ + 0.15 * math.sin(i / 8.0), y_ + 0.1 * math.cos(i / 11.0), yw + i * 0.35, z0)
        elif a == "float":   # hop over the inflatable ring and land floating in the middle of the pool
            x_, y_, yw = zpos(f); n = 17
            for i in range(n + 1):
                u = i / n; zkey(f + i, x_ + (PX - x_) * u, y_ + (PY - y_) * u, yw + u * 1.2, POOL_Z * u + 0.55 * math.sin(u * math.pi))
            for i in range(n + 1, n + 24 * 3):
                zkey(f + i, PX, PY, yw + 1.2 + (i - n) * 0.03, POOL_Z + 0.015 * math.sin(i / 6.0))
            float_f = f + n
            vfx.emitter("pool9_spl", tuple(W(PX, PY, 0.32)), c, 160, f + n, f + n + 3, 22, (0.6, 0.85, 1.0), size=0.02, vel_normal=2.2, vel_rand=0.8, gravity=1.0, strength=2.0, radius=0.12)
            for b_ in mudcoat: key_vis(b_, f + n + 2, False)
        elif a == "eyes":
            col_ = e["color"]
            if col_ == "rainbow":
                for i in range(0, 24 * 9, 3):
                    r_, g_, b_ = colorsys.hsv_to_rgb((i / 30.0) % 1, 1, 1); ec.default_value = (r_, g_, b_, 1); ec.keyframe_insert("default_value", frame=f + i)
            else:
                ec.default_value = (*EYE[col_], 1); ec.keyframe_insert("default_value", frame=f)
    elif nm == "bucket":
        if a == "cover": BUCKET["cover"] = f; key_vis(bucket, f, True)
        elif a == "off": BUCKET["off"] = f
        elif a == "hide": key_vis(bucket, f, False)
    elif nm == "sprinkler":
        if a == "on":
            n = int(e["dur"] * 24)
            spr.keyframe_insert("rotation_euler", frame=f)
            for i in range(0, n + 1, 3): spr.rotation_euler = (0, 0, 1.1 * math.sin(i / 10.0)); spr.keyframe_insert("rotation_euler", frame=f + i)
            vfx.emitter("spr9", tuple(W(SPX - O.x, SPY - O.y, 0.14)), c, 1400, f, f + n, 20, (0.6, 0.85, 1.0), size=0.012, vel_normal=3.2, vel_rand=0.5, gravity=1.0, strength=2.0, radius=0.06)
        elif a == "off":
            spr.keyframe_insert("rotation_euler", frame=f)
    elif nm == "drips":
        n = int(e["dur"] * 24)
        h = head_world(e["who"], f + 6)
        vfx.emitter("drip9_" + e["who"], tuple(h + Vector((0, 0, 0.08))), c, 220, f + 6, f + n, 18, (0.6, 0.85, 1.0), size=0.012, vel_normal=0.6, vel_rand=0.6, gravity=1.0, strength=2.0, radius=0.12)
    elif nm == "mudspray":
        n = int(e["dur"] * 24); x_, y_, _ = zpos(f)
        vfx.emitter("mud9_spray", tuple(W(x_, y_, 0.06)), c, 260, f, f + n, 16, (0.3, 0.19, 0.09), size=0.025, vel_normal=1.8, vel_rand=0.9, gravity=1.0, strength=2.0, radius=0.2)
        for b_ in mudcoat: key_vis(b_, f + 12, True)
    elif nm == "mud" and a == "splat":
        who = e["who"]; arm = CH[who]["arm"]; sf_ = f + 18
        blobs = []
        for j, (dx, dz, r_) in enumerate(((0.0, 0.0, 0.05), (0.045, 0.03, 0.035), (-0.05, 0.02, 0.032), (0.02, -0.05, 0.03), (-0.03, 0.065, 0.028), (0.05, -0.02, 0.025))):
            bl_ = sets2.sph(f"mud9_b{j}", r_, (0, 0, 0), mudblob_m, c, scale=(1, 0.55, 1), seg=12); key_vis(bl_, 1, False); key_vis(bl_, sf_, True); blobs.append((bl_, dx, dz))
        for ff in range(sf_, END + 1, 2):
            h = head_world(who, ff); yw = arm.matrix_world.to_euler().z
            fwd = Vector((math.sin(yw), -math.cos(yw), 0)); side = Vector((math.cos(yw), math.sin(yw), 0))
            for bl_, dx, dz in blobs:
                bl_.location = h + fwd * 0.105 + side * dx + Vector((0, 0, dz)); bl_.rotation_euler = (0, 0, yw)
                bl_.keyframe_insert("location", frame=ff); bl_.keyframe_insert("rotation_euler", frame=ff)
        vfx.emitter("mud9_spl", tuple(head_world(who, sf_)), c, 90, sf_ - 6, sf_ - 3, 16, (0.3, 0.19, 0.09), size=0.025, vel_rand=1.6, gravity=1.0, strength=2.0, radius=0.1)
    elif nm == "bigcarrot":
        if a == "pull":
            n = int(e["dur"] * 24)
            carrot.keyframe_insert("location", frame=f); carrot.keyframe_insert("rotation_euler", frame=f)
            for i in range(2, n + 1, 2):
                u = i / n; carrot.location = W(CR0[0], CR0[1], CR0[2] + 0.12 * u * u); carrot.rotation_euler = (0.08 * math.sin(i * 1.7), 0.08 * math.cos(i * 1.3), 0)
                carrot.keyframe_insert("location", frame=f + i); carrot.keyframe_insert("rotation_euler", frame=f + i)
        elif a == "fly":
            n = int(e["dur"] * 24); src = carrot.location.copy() if False else W(CR0[0], CR0[1], CR0[2] + 0.12); dst = W(PX - 0.3, PY + 0.2, 0.36)
            for i in range(0, n + 1, 2):
                u = i / n; p_ = src.lerp(dst, u) + Vector((0, 0, 2.2 * math.sin(u * math.pi)))
                carrot.location = p_; carrot.rotation_euler = (u * 9.0, u * 3.0, 0)
                carrot.keyframe_insert("location", frame=f + i); carrot.keyframe_insert("rotation_euler", frame=f + i)
            for i in range(n + 2, n + 24 * 60, 6):   # floating, bobbing, lying on its side
                carrot.location = dst + Vector((0.05 * math.sin(i / 30.0), 0.04 * math.cos(i / 37.0), 0.012 * math.sin(i / 7.0)))
                carrot.rotation_euler = (math.radians(90), 0, i * 0.01); carrot.keyframe_insert("location", frame=f + i); carrot.keyframe_insert("rotation_euler", frame=f + i)
            vfx.emitter("carrot9_spl", tuple(dst), c, 120, f + n - 1, f + n + 2, 20, (0.6, 0.85, 1.0), size=0.02, vel_normal=2.0, vel_rand=0.8, gravity=1.0, strength=2.0, radius=0.1)
            vfx.emitter("carrot9_dirt", tuple(src), c, 70, f, f + 3, 14, (0.3, 0.19, 0.09), size=0.02, vel_normal=1.5, vel_rand=1.0, gravity=1.0, strength=2.0, radius=0.08)
    elif nm == "pumpkin" and a == "wobble":
        pk = gd["pumpkin"]; n = int(e["dur"] * 24)
        pk.keyframe_insert("rotation_euler", frame=f)
        for i in range(2, n + 1, 2):
            pk.rotation_euler = (0.12 * math.sin(i * 0.9) * (1 - i / n), 0.08 * math.cos(i * 1.1) * (1 - i / n), 0); pk.keyframe_insert("rotation_euler", frame=f + i)
        pk.rotation_euler = (0, 0, 0); pk.keyframe_insert("rotation_euler", frame=f + n + 2)
    elif nm == "pool" and a == "fill":
        n = int(e["dur"] * 24); poolw.keyframe_insert("location", frame=f); poolw.location.z = 0.3; poolw.keyframe_insert("location", frame=f + n)
        vfx.emitter("pool9_fill", tuple(W(PX - 0.6, PY - 0.5, 0.45)), c, 120, f, f + n, 16, (0.6, 0.85, 1.0), size=0.018, vel_normal=0.6, vel_rand=0.6, gravity=1.0, strength=2.0, radius=0.15)
    elif nm == "wbucket" and a == "carry":
        who = e["who"]; n = int(e["dur"] * 24)
        sc_ = bpy.context.scene; sc_.frame_set(f + 2); bpy.context.view_layer.update()
        arm = CH[who]["arm"]; pb = [b for b in arm.pose.bones if b.name.endswith("RightHand")][0]
        Mh = arm.matrix_world @ pb.matrix
        wb = water_bucket("wbucket9_" + who); wb.location = Mh.translation; bpy.context.view_layer.update()
        con = wb.constraints.new("CHILD_OF"); con.target = arm; con.subtarget = pb.name; con.inverse_matrix = Mh.inverted()
        key_vis(wb, 1, False); key_vis(wb, f + 2, True); key_vis(wb, f + n + 30, False)
    elif nm == "crumbs":
        pts = [e["at"]] if a == "drop" else e["pts"]; k = 0
        for (p0, p1) in (zip(pts, pts[1:]) if len(pts) > 1 else [(pts[0], pts[0])]):
            for j in range(6):
                u = j / 6; x_ = p0[0] + (p1[0] - p0[0]) * u + random.uniform(-0.08, 0.08); y_ = p0[1] + (p1[1] - p0[1]) * u + random.uniform(-0.08, 0.08)
                cr = sets2.sph(f"crumb9_{f}_{k}", 0.02, W(x_, y_, 0.014), crumb_m, c, seg=6); k += 1
                key_vis(cr, 1, False); key_vis(cr, f + k * 2, True); key_vis(cr, f + 24 * 6 + k * 2, False)
# bucket follows Zoomy while covering him, then pops off and lands upside-up beside the path
if BUCKET["cover"]:
    f0, f1 = BUCKET["cover"], BUCKET["off"] or END
    for ff in range(f0, f1 + 1, 1):
        x_, y_, yw = zpos(ff); bucket.location = W(x_, y_, 0.0); bucket.rotation_euler = (0, 0, 0)
        bucket.keyframe_insert("location", frame=ff); bucket.keyframe_insert("rotation_euler", frame=ff)
    if BUCKET["off"]:
        x_, y_, _ = zpos(f1); src = W(x_, y_, 0.0); dst = W(x_ - 0.7, y_ - 0.5, 0.31)
        for i in range(0, 21, 2):
            u = i / 20; bucket.location = src.lerp(dst, u) + Vector((0, 0, 1.2 * math.sin(u * math.pi))); bucket.rotation_euler = (u * math.pi, 0.3 * u, 0)
            bucket.keyframe_insert("location", frame=f1 + i); bucket.keyframe_insert("rotation_euler", frame=f1 + i)
# muddy tyre tracks
for i, (ft, x_, y_, yw) in enumerate(TRACKS):
    for sx in (-1, 1):
        tr = sets2.box(f"track9_{i}_{sx}", (0.05, 0.13, 0.004), (0, 0, 0), track_m, c, 0.001)
        tr.location = W(x_ + sx * 0.14 * math.cos(yw), y_ + sx * 0.14 * math.sin(yw), 0.011); tr.rotation_euler = (0, 0, yw)
        key_vis(tr, 1, False); key_vis(tr, ft + 3, True)
# write Zoomy keys
for fz in sorted(ZK):
    x_, y_, yw = ZK[fz]; zoomy.location = W(x_, y_, zz(fz)); zoomy.rotation_euler = (0, 0, yw)
    zoomy.keyframe_insert("location", frame=fz); zoomy.keyframe_insert("rotation_euler", frame=fz)
if zoomy.animation_data and zoomy.animation_data.action:
    for fc in zoomy.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
# dynamic cameras that follow Zoomy
def _zcam(f0, f1, dist=0.8, h=0.34, lens=30):
    x_, y_, yw = zpos(f0 + 2); z_ = zz(f0 + 2); p = W(x_, y_ - dist, h + z_); t = W(x_, y_, 0.08 + z_)
    return (tuple(p), tuple(t), lens)
gd["cams"]["insert:zoomy"] = lambda f0, f1: _zcam(f0, f1)
for ob in bpy.data.objects:
    if ob.animation_data and ob.animation_data.action:
        for fc in ob.animation_data.action.fcurves:
            if "hide" in fc.data_path:
                for kp in fc.keyframe_points: kp.interpolation = "CONSTANT"
print("props_ep9 ok: zoomy keys", len(ZK), "tracks", len(TRACKS))
