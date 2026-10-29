# ===== Episode 8 (ZOOMY the robot vacuum) props: executed inside build8 (has CH, SETS, TL, F, sets2, Vector, math, bpy, random, head_world, vfx, END) =====
import vfx, colorsys
living = SETS["living"]; O = living["origin"]; c = living["coll"]
def key_vis(obj, f, v):
    for o in [obj] + list(obj.children_recursive):
        o.hide_render = not v; o.hide_viewport = not v
        o.keyframe_insert("hide_render", frame=max(1, f)); o.keyframe_insert("hide_viewport", frame=max(1, f))
def W(x, y, z=0.0): return Vector((O.x + x, O.y + y, z))
EV = sorted([e for e in TL["events"] if e["type"] == "prop"], key=lambda e: e["t"])

# ---------------- Zoomy: round robot vacuum with a cute face + LED eye strip ----------------
body_m = sets2.M("zoomy_body", (0.93, 0.94, 0.96), 0.25, coat=0.8)
top_m = sets2.M("zoomy_top", (0.12, 0.13, 0.16), 0.2, coat=1.0)
bump_m = sets2.M("zoomy_bump", (0.25, 0.25, 0.28), 0.5)
eye_m = sets2.M("zoomy_eye", (1, 1, 1), 0.3, emit=(0.3, 0.7, 1.0), emit_str=4.0)
pupil_m = sets2.M("zoomy_pupil", (0.02, 0.02, 0.03), 0.3)
zoomy = bpy.data.objects.new("zoomy8", None); c.objects.link(zoomy)
parts = [sets2.cyl("zoomy8_body", 0.19, 0.07, (0, 0, 0.045), body_m, c, 48, bevel=0.01),
         sets2.cyl("zoomy8_top", 0.15, 0.012, (0, 0, 0.083), top_m, c, 48, bevel=0.003),
         sets2.cyl("zoomy8_bumper", 0.195, 0.03, (0, 0, 0.03), bump_m, c, 48, bevel=0.004)]
for sx in (-1, 1):   # two big googly eyes on the front (front = -Y local)
    parts.append(sets2.sph(f"zoomy8_eye{sx}", 0.035, (sx * 0.06, -0.15, 0.085), eye_m, c, scale=(1, 0.6, 1), seg=16))
    parts.append(sets2.sph(f"zoomy8_pup{sx}", 0.016, (sx * 0.06, -0.172, 0.09), pupil_m, c, seg=10))
parts.append(sets2.cyl("zoomy8_led", 0.155, 0.006, (0, 0, 0.09), eye_m, c, 48, bevel=0))
brush = bpy.data.objects.new("zoomy8_brushp", None); c.objects.link(brush); brush.parent = zoomy; brush.location = (0.13, -0.12, 0.01)
for k in range(3):
    b_ = sets2.box(f"zoomy8_br{k}", (0.09, 0.006, 0.006), (0, 0, 0), bump_m, c, 0); b_.rotation_euler = (0, 0, k * 2.094); b_.parent = brush
for p_ in parts: p_.parent = zoomy
for f in range(1, END + 1, 2): brush.rotation_euler = (0, 0, f * 0.9); brush.keyframe_insert("rotation_euler", frame=f)
ZK = {}   # frame -> (x, y, yaw)
def zkey(f, x, y, yaw): ZK[int(f)] = (x, y, yaw)
def zpos(f):
    ks = sorted(k for k in ZK if k <= f)
    return ZK[ks[-1]] if ks else (2.9, -0.4, 0.0)
def heading(a, b): return math.atan2(-(b[0] - a[0]), (b[1] - a[1])) + math.pi   # local front (-Y) points along travel
def path(f0, pts, dur, turbo):
    seg = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    lens = [math.dist(a, b) for a, b in seg]; tot = sum(lens) or 1
    n = max(2, int(dur * 24))
    for i in range(n + 1):
        u = i / n * tot; acc = 0
        for (a, b), L_ in zip(seg, lens):
            if acc + L_ >= u or (a, b) == seg[-1]:
                k = (u - acc) / L_ if L_ else 0; k = min(1, k)
                x = a[0] + (b[0] - a[0]) * k; y = a[1] + (b[1] - a[1]) * k
                yaw = heading(a, b) + (0.18 * math.sin(i * 1.3) if turbo else 0)
                zkey(f0 + i, x, y, yaw); break
            acc += L_
# ---------------- items ----------------
sock_m = sets2.M("sock8", (0.95, 0.3, 0.45), 0.8); stripe_m = sets2.M("sock8s", (1, 1, 1), 0.8)
def sock(name, x, y):
    g = bpy.data.objects.new(name, None); c.objects.link(g); g.location = W(x, y, 0.02); g.rotation_euler = (0, 0, 0.6)
    a = sets2.box(name + "_a", (0.09, 0.2, 0.035), (0, 0, 0), sock_m, c, 0.015); a.parent = g
    b = sets2.box(name + "_b", (0.09, 0.08, 0.036), (0, -0.12, 0), stripe_m, c, 0.015); b.parent = g
    return g
socks = {"sock": sock("sock8_1", -0.75, -1.5), "sock2": sock("sock8_2", 1.45, -1.0)}
car = bpy.data.objects.new("car8", None); c.objects.link(car); car.location = W(0.95, -0.55, 0.0); car.rotation_euler = (0, 0, 0.4)
redc = sets2.M("car8_red", (0.9, 0.1, 0.1), 0.3, coat=0.8); blk = sets2.M("car8_blk", (0.05, 0.05, 0.05), 0.5)
for nm_, sz, loc in (("b", (0.2, 0.1, 0.05), (0, 0, 0.045)), ("c", (0.1, 0.09, 0.04), (-0.02, 0, 0.09))):
    o_ = sets2.box("car8_" + nm_, sz, loc, redc, c, 0.01); o_.parent = car
for wx in (-0.07, 0.07):
    for wy in (-0.055, 0.055):
        w_ = sets2.cyl(f"car8_w{wx}{wy}", 0.025, 0.02, (wx, wy, 0.025), blk, c, 16, bevel=0, rot=(math.radians(90), 0, 0)); w_.parent = car
ITEM = {"sock": socks["sock"], "sock2": socks["sock2"], "car": car}
# cardboard box Zoomy arrives in
box_m = sets2.M("box8", (0.72, 0.55, 0.36), 0.8)
boxg = bpy.data.objects.new("box8", None); c.objects.link(boxg); boxg.location = W(3.3, 1.9, 0)
bb = sets2.box("box8_b", (0.5, 0.5, 0.22), (0, 0, 0.11), box_m, c, 0.005); bb.parent = boxg
flaps = []
for i, (dx, dy, rz) in enumerate(((0, 0.26, 0), (0, -0.26, 0), (0.26, 0, 1.5708), (-0.26, 0, 1.5708))):
    fl = sets2.box(f"box8_f{i}", (0.5, 0.25, 0.008), (dx * 0.5, dy * 0.5, 0.225), box_m, c, 0); fl.parent = boxg; fl.rotation_euler = (0, 0, rz); flaps.append(fl)
# birthday cake on a round side table (back-left corner)
CX, CY = -2.95, 1.1
tw = sets2.M_wood("table8", (0.6, 0.38, 0.2), (0.45, 0.26, 0.12), scale=3)
sets2.cyl("table8_top", 0.42, 0.04, W(CX, CY, 0.72), tw, c, 40); sets2.cyl("table8_leg", 0.05, 0.7, W(CX, CY, 0.36), tw, c, 16); sets2.cyl("table8_foot", 0.25, 0.03, W(CX, CY, 0.015), tw, c, 32)
cake = bpy.data.objects.new("cake8", None); c.objects.link(cake); cake.location = W(CX, CY, 0.74)
plate = sets2.cyl("cake8_plate", 0.3, 0.015, (0, 0, 0.008), sets2.M("plate8", (0.97, 0.97, 0.97), 0.2, coat=1.0), c, 40); plate.parent = cake
pink = sets2.M("cake8_pink", (1.0, 0.55, 0.7), 0.5); cream = sets2.M("cake8_cream", (1.0, 0.96, 0.9), 0.5)
for i, (r_, h_, z_) in enumerate(((0.24, 0.14, 0.085), (0.17, 0.12, 0.215))):
    t_ = sets2.cyl(f"cake8_t{i}", r_, h_, (0, 0, z_), pink, c, 40, bevel=0.01); t_.parent = cake
    for k in range(14):
        a = k / 14 * 2 * math.pi; d_ = sets2.sph(f"cake8_d{i}{k}", 0.025, (math.cos(a) * r_, math.sin(a) * r_, z_ + h_ / 2), cream, c, seg=8); d_.parent = cake
for k in range(5):
    a = k / 5 * 2 * math.pi
    cd = sets2.cyl(f"cake8_cd{k}", 0.008, 0.07, (math.cos(a) * 0.1, math.sin(a) * 0.1, 0.31), sets2.M(f"cand8{k % 3}", [(0.3, 0.6, 1), (1, 0.85, 0.2), (0.4, 0.9, 0.4)][k % 3], 0.4), c, 8); cd.parent = cake
    fl_ = sets2.sph(f"cake8_fl{k}", 0.012, (math.cos(a) * 0.1, math.sin(a) * 0.1, 0.355), sets2.M("flame8", (1, 0.8, 0.3), 0.5, emit=(1, 0.7, 0.2), emit_str=12), c, scale=(1, 1, 1.6), seg=8); fl_.parent = cake
straw = sets2.M("straw8", (0.9, 0.08, 0.15), 0.4, coat=0.6)
for k in range(3):
    s_ = sets2.sph(f"cake8_sb{k}", 0.025, (0.05 * math.cos(k * 2.1), 0.05 * math.sin(k * 2.1), 0.285), straw, c, seg=10); s_.parent = cake
living["cams"]["insert:cake"] = (tuple(W(CX + 1.25, CY - 1.35, 1.05)), tuple(W(CX, CY, 0.85)), 34)
# mess for the "dinosaur party": blocks scattered, a ball, cushions on the floor
mess = []
for i, b_ in enumerate(living["blocks"]):
    ang = i * 1.7; b_.location = W(-1.6 + 0.8 * i - 0.2 * (i % 2), -1.6 + 0.5 * (i % 3), 0.065); b_.rotation_euler = (0, 0, ang)
    b_.keyframe_insert("location", frame=1); mess.append(b_)
ball = sets2.sph("ball8", 0.11, W(2.2, -0.2, 0.11), sets2.M("ball8m", (0.2, 0.6, 1.0), 0.3, coat=0.6), c, seg=20); mess.append(ball)
for i, (x_, y_) in enumerate(((-0.4, -2.0), (2.6, -1.9))):
    cu = sets2.box(f"cush8_{i}", (0.42, 0.42, 0.12), W(x_, y_, 0.06), sets2.M(f"cush8m{i}", [(0.95, 0.75, 0.2), (0.4, 0.75, 0.6)][i], 0.9), c, 0.05)
    cu.rotation_euler = (0, 0, 0.5 * i + 0.3); mess.append(cu)
# crumbs
crumb_m = sets2.M("crumb8", (0.6, 0.38, 0.15), 0.9)
# front-door light (right wall near the front) + door panel that swings open
door_piv = bpy.data.objects.new("door8", None); c.objects.link(door_piv); door_piv.location = W(4.43, -3.9, 0)
dp = sets2.box("door8_p", (0.05, 0.95, 2.1), (0, -0.475, 1.05), sets2.M_wood("door8_w", (0.55, 0.35, 0.2), (0.42, 0.26, 0.14), scale=3), c, 0.01); dp.parent = door_piv
light_pl = sets2.box("door8_light", (0.01, 0.93, 2.08), W(4.445, -4.37, 1.05), sets2.M("door8_lm", (1, 1, 1), 0.5, emit=(1.0, 0.97, 0.88), emit_str=6.0), c, 0)
living["cams"]["insert:door"] = (tuple(W(1.6, -1.6, 0.9)), tuple(W(4.2, -4.4, 0.5)), 30)
# disco lights
disco = []
for i, (x_, y_, col_) in enumerate(((-2.0, 0.5, (1, 0.2, 0.6)), (0.5, -1.0, (0.2, 0.6, 1)), (2.4, 0.4, (0.3, 1, 0.4)), (0.0, 1.2, (1, 0.8, 0.2)))):
    d_ = bpy.data.lights.new(f"disco8_{i}", "SPOT"); d_.energy = 0; d_.color = col_; d_.spot_size = math.radians(55); d_.spot_blend = 0.6
    o_ = bpy.data.objects.new(f"disco8_{i}", d_); c.objects.link(o_); o_.location = W(x_, y_, 2.7); disco.append(o_)
    d_.keyframe_insert("energy", frame=1)
dball = sets2.sph("disco8_ball", 0.16, W(0.3, 0.2, 2.45), sets2.M("disco8_bm", (0.85, 0.85, 0.9), 0.05, 1.0), c, seg=16); key_vis(dball, 1, False)

# ---------------- events ----------------
EYE = {"blue": (0.3, 0.7, 1.0), "red": (1.0, 0.1, 0.1), "green": (0.2, 1.0, 0.35)}
ec = eye_m.node_tree.nodes["Principled BSDF"].inputs["Emission Color"]
ec.default_value = (*EYE["blue"], 1); ec.keyframe_insert("default_value", frame=1)
key_vis(socks["sock"], 1, False); key_vis(socks["sock2"], 1, False); key_vis(boxg, 1, False)
key_vis(light_pl, 1, False)
splat_f = None
for e in EV:
    f = F(e["t"]); nm = e["name"]; a = e["action"]
    if nm == "zoomy":
        if a == "place": zkey(f, *e["at"], 0.0); zkey(f + 1, *e["at"], 0.0)
        elif a == "path": path(f, e["pts"], e["dur"], e.get("turbo", False))
        elif a == "circle":
            cx_, cy_ = e["center"]; r_ = e["r"]; n = int(e["dur"] * 24)
            for i in range(n + 1):
                th = i / n * 2 * math.pi * 1.5 - math.pi / 2
                zkey(f + i, cx_ + r_ * math.cos(th), cy_ + r_ * math.sin(th), th + math.pi)
        elif a == "spin":
            x_, y_, yw = zpos(f); n = int(e["dur"] * 24)
            for i in range(n + 1): zkey(f + i, x_ + 0.15 * math.sin(i / 8.0), y_ + 0.1 * math.cos(i / 11.0), yw + i * 0.35)
        elif a == "zigzag":
            f0 = F(e["t0"]); n = int(e["dur"] * 24); rnd = random.Random(8)
            pts = [(rnd.uniform(-2.8, 3.0), rnd.uniform(-2.2, 0.8)) for _ in range(14)] + [(-0.4, -0.6)]
            path(f0, pts, e["dur"], True)
        elif a == "eyes":
            col_ = e["color"]
            if col_ == "rainbow":
                for i in range(0, 24 * 9, 3):
                    r_, g_, b_ = colorsys.hsv_to_rgb((i / 30.0) % 1, 1, 1); ec.default_value = (r_, g_, b_, 1); ec.keyframe_insert("default_value", frame=f + i)
            else:
                ec.default_value = (*EYE[col_], 1); ec.keyframe_insert("default_value", frame=f)
    elif nm in ("sock", "sock2", "car") and a == "eat":
        ob = ITEM[nm]
        if nm != "car": key_vis(ob, f - 14, True)
        ob.keyframe_insert("location", frame=f + 2); ob.scale = (1, 1, 1); ob.keyframe_insert("scale", frame=f + 2)
        x_, y_, _ = zpos(f + 12); ob.location = W(x_, y_, 0.06); ob.keyframe_insert("location", frame=f + 12)
        ob.scale = (0.05, 0.05, 0.05); ob.keyframe_insert("scale", frame=f + 12); key_vis(ob, f + 13, False)
    elif nm == "box":
        if a == "show": key_vis(boxg, f, True); key_vis(zoomy, f, False)
        elif a == "open":
            for i, fl in enumerate(flaps):
                fl.keyframe_insert("rotation_euler", frame=f); fl.keyframe_insert("location", frame=f)
                fl.location.z += 0.6 + 0.1 * i; fl.rotation_euler.x += 2.5 * (1 if i % 2 else -1); fl.keyframe_insert("rotation_euler", frame=f + 10); fl.keyframe_insert("location", frame=f + 10)
            key_vis(zoomy, f + 2, True); key_vis(boxg, f + 40, False)
            vfx.flash("box8_fl", W(3.3, 1.9, 0.6), c, f + 2, 25, color=(1.0, 0.9, 0.7), dur=10)
    elif nm == "crumbs":
        pts = [e["at"]] if a == "drop" else e["pts"]
        k = 0
        for (p0, p1) in (zip(pts, pts[1:]) if len(pts) > 1 else [(pts[0], pts[0])]):
            for j in range(6):
                u = j / 6; x_ = p0[0] + (p1[0] - p0[0]) * u + random.uniform(-0.08, 0.08); y_ = p0[1] + (p1[1] - p0[1]) * u + random.uniform(-0.08, 0.08)
                cr = sets2.sph(f"crumb8_{f}_{k}", 0.018, W(x_, y_, 0.012), crumb_m, c, seg=6); k += 1
                key_vis(cr, 1, False); key_vis(cr, f + k * 2, True); key_vis(cr, f + 24 * 5 + k * 2, False)
    elif nm == "cake" and a == "fly":
        n = int(e["dur"] * 24)
        cake.keyframe_insert("location", frame=f); cake.keyframe_insert("rotation_euler", frame=f)
        for i in range(1, n + 1, 2):
            u = i / n; cake.location = W(CX + 0.15 * math.sin(u * math.pi), CY - 0.1 * math.sin(u * math.pi), 0.74 + 0.9 * math.sin(u * math.pi))
            cake.rotation_euler = (0.15 * math.sin(u * 6), 0, u * 2 * math.pi); cake.keyframe_insert("location", frame=f + i); cake.keyframe_insert("rotation_euler", frame=f + i)
        cake.location = W(CX, CY, 0.74); cake.rotation_euler = (0, 0, 0)
        cake.keyframe_insert("location", frame=f + n + 1); cake.keyframe_insert("rotation_euler", frame=f + n + 1)
        fly_f = f
    elif nm == "frosting" and a == "fly":
        n = int(e["dur"] * 24); fb = sets2.sph(f"frost8_fly", 0.06, W(CX, CY, 1.2), pink, c, seg=12); key_vis(fb, 1, False)
        f0 = f + int(0.6 * 24); key_vis(fb, f0, True)
        tgt = head_world("buddy", f0 + n); src = W(CX, CY, 1.4)
        for i in range(0, n + 1, 2):
            u = i / n; p_ = src.lerp(tgt, u) + Vector((0, 0, 0.9 * math.sin(u * math.pi)))
            fb.location = p_; fb.keyframe_insert("location", frame=f0 + i)
        key_vis(fb, f0 + n + 1, False); splat_f = f0 + n
    elif nm == "frosting" and a == "splat":
        sf_ = splat_f or f
        arm = CH["buddy"]["arm"]
        blobs = []
        for j, (dx, dz, r_) in enumerate(((0.0, 0.0, 0.05), (0.04, 0.03, 0.035), (-0.045, 0.02, 0.03), (0.02, -0.045, 0.03), (-0.02, 0.06, 0.025))):
            bl_ = sets2.sph(f"frost8_b{j}", r_, (0, 0, 0), pink if j % 2 == 0 else cream, c, scale=(1, 0.55, 1), seg=12); key_vis(bl_, 1, False); key_vis(bl_, sf_, True); blobs.append((bl_, dx, dz))
        for ff in range(sf_, END + 1, 2):
            h = head_world("buddy", ff); yw = arm.matrix_world.to_euler().z
            fwd = Vector((math.sin(yw), -math.cos(yw), 0)); side = Vector((math.cos(yw), math.sin(yw), 0))
            for bl_, dx, dz in blobs:
                bl_.location = h + fwd * 0.105 + side * dx + Vector((0, 0, 0.0 + dz)); bl_.rotation_euler = (0, 0, yw)
                bl_.keyframe_insert("location", frame=ff); bl_.keyframe_insert("rotation_euler", frame=ff)
        vfx.emitter("frost8_spl", tuple(head_world("buddy", sf_)), c, 60, sf_, sf_ + 3, 14, (1.0, 0.6, 0.75), size=0.02, vel_rand=1.4, gravity=1.0, strength=2.0, radius=0.08)
    elif nm == "disco":
        if a == "on":
            n = int(e["dur"] * 24); key_vis(dball, f, True)
            for i, o_ in enumerate(disco):
                for ff in range(f, f + n, 6):
                    o_.data.energy = 900 if ((ff // 6 + i) % 2 == 0) else 250; o_.data.keyframe_insert("energy", frame=ff)
            for ff in range(f, f + n, 2): dball.rotation_euler = (0, 0, (ff - f) * 0.2); dball.keyframe_insert("rotation_euler", frame=ff)
        elif a == "off":
            for o_ in disco: o_.data.energy = 0; o_.data.keyframe_insert("energy", frame=f)
            key_vis(dball, f, False)
    elif nm == "blocks" and a == "clean":
        f0 = F(e["t0"]); n = int(e["dur"] * 24)
        for i, ob in enumerate(mess):
            fc_ = f0 + int((i + 1) / (len(mess) + 1) * n)
            ob.scale = (1, 1, 1); ob.keyframe_insert("scale", frame=fc_ - 3); ob.scale = (0.01, 0.01, 0.01); ob.keyframe_insert("scale", frame=fc_)
            key_vis(ob, fc_ + 1, False)
            vfx.flash(f"clean8_{i}", tuple(ob.location) if ob.parent is None else tuple(ob.matrix_world.translation), c, fc_, 8, color=(0.8, 1.0, 0.9), dur=5)
    elif nm == "door" and a == "open":
        door_piv.keyframe_insert("rotation_euler", frame=f); key_vis(light_pl, f, True)
        door_piv.rotation_euler = (0, 0, math.radians(-80)); door_piv.keyframe_insert("rotation_euler", frame=f + 18)
# write Zoomy keys
for fz in sorted(ZK):
    x_, y_, yw = ZK[fz]; zoomy.location = W(x_, y_, 0.0); zoomy.rotation_euler = (0, 0, yw)
    zoomy.keyframe_insert("location", frame=fz); zoomy.keyframe_insert("rotation_euler", frame=fz)
if zoomy.animation_data and zoomy.animation_data.action:
    for fc in zoomy.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
# dynamic cameras that follow where Zoomy is at the start of the shot
def _zcam(f0, f1, dist=0.75, h=0.32, lens=30):
    x_, y_, yw = zpos(f0 + 2); p = W(x_, y_ - dist, h); t = W(x_, y_, 0.08)
    if p.y < O.y - 5.6: p = W(x_ + 0.4, y_ + dist * 0.6, h)
    return (tuple(p), tuple(t), lens)
living["cams"]["insert:zoomy"] = lambda f0, f1: _zcam(f0, f1)
living["cams"]["insert:feet"] = lambda f0, f1: _zcam(f0, f1, dist=1.25, h=0.55, lens=28)
living["cams"]["insert:buddyfeet"] = lambda f0, f1: _zcam(f0, f1, dist=1.4, h=0.6, lens=28)
for ob in bpy.data.objects:
    if ob.animation_data and ob.animation_data.action:
        for fc in ob.animation_data.action.fcurves:
            if "hide" in fc.data_path:
                for kp in fc.keyframe_points: kp.interpolation = "CONSTANT"
print("props_ep8 ok: zoomy keys", len(ZK))
