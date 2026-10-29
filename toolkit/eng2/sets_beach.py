# Song 02+: sunny BEACH set (sand, rolling sea with waves + foam, palm trees that sway, striped umbrella, sandcastle,
# red bucket, green beach ball, orange crab, seagulls, sailboat, big yellow sun). Origin x=1100.
import bpy, bmesh, math, random
from mathutils import Vector
import sets2
from sets2 import SETS, M, box, cyl, sph, plane, area, col

def _obj(name, bm, mats, coll, smooth=True):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    if smooth:
        for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); coll.objects.link(o); return o

def striped_sphere(name, r, loc, m1, m2, coll, n=6, scale=(1, 1, 1)):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=36, v_segments=18, radius=r)
    for f in bm.faces:
        c = f.calc_center_median(); a = math.atan2(c.y, c.x)
        f.material_index = int(((a + math.pi) / (2 * math.pi)) * n) % 2
    o = _obj(name, bm, [m1, m2], coll); o.location = loc; o.scale = scale; return o

def striped_cone(name, r1, r2, depth, loc, m1, m2, coll, n=8):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=48, radius1=r1, radius2=r2, depth=depth)
    for f in bm.faces:
        c = f.calc_center_median(); a = math.atan2(c.y, c.x)
        f.material_index = int(((a + math.pi) / (2 * math.pi)) * n) % 2
    o = _obj(name, bm, [m1, m2], coll); o.location = loc; return o

def cone(name, r1, r2, depth, loc, mat, coll, seg=32):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r1, radius2=r2, depth=depth)
    o = _obj(name, bm, [mat], coll); o.location = loc; return o

def grid(name, sx, sy, nx, ny, loc, mat, coll):
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=nx, y_segments=ny, size=1.0)
    for v in bm.verts: v.co.x *= sx / 2; v.co.y *= sy / 2
    o = _obj(name, bm, [mat], coll); o.location = loc; return o

def _sway(o, amp, period, phase, axis=0, frames=8000, step=12):
    for f in range(1, frames + 1, step):
        v = [0, 0, 0]; v[axis] = amp * math.sin((f + phase) / period * 2 * math.pi) + amp * 0.3 * math.sin((f + phase) / (period * 0.41) * 2 * math.pi)
        o.delta_rotation_euler = v; o.keyframe_insert("delta_rotation_euler", frame=f)

def palm(name, loc, coll, h=4.2, lean=12, yaw=0, seed=0):
    rnd = random.Random(seed)
    bark = M("bch_bark", (0.55, 0.40, 0.25), 0.9, bump=0.8, bump_scale=40)
    leaf = M("bch_leaf%d" % (seed % 2), (0.18, 0.55, 0.16) if seed % 2 else (0.25, 0.62, 0.18), 0.7)
    nut = M("bch_nut", (0.35, 0.22, 0.10), 0.6)
    piv = bpy.data.objects.new(name, None); coll.objects.link(piv); piv.location = loc; piv.rotation_euler = (0, 0, math.radians(yaw))
    p = Vector((0, 0, 0)); n = 9; seg = h / n; ang = 0.0
    for i in range(n):
        ang += math.radians(lean) / n * (1 + i / n)
        d = Vector((math.sin(ang), 0, math.cos(ang))) * seg
        c = cyl(name + f"_t{i}", 0.16 - 0.006 * i, seg * 1.08, p + d / 2, bark, coll, 12, bevel=0, rot=(0, ang, 0)); c.parent = piv
        p = p + d
    crown = bpy.data.objects.new(name + "_crown", None); coll.objects.link(crown); crown.parent = piv; crown.location = p
    for j in range(8):
        a = j / 8 * 2 * math.pi + rnd.uniform(-0.2, 0.2); droop = rnd.uniform(0.35, 0.65)
        lf = sph(name + f"_lf{j}", 0.6, (0, 0, 0), leaf, coll, scale=(1.9, 0.32, 0.05), seg=16)
        lf.parent = crown; lf.location = (math.cos(a) * 0.95, math.sin(a) * 0.95, -0.25 * droop)
        lf.rotation_euler = (0, droop, a)
    for j in range(3):
        a = j / 3 * 2 * math.pi
        s = sph(name + f"_nut{j}", 0.12, (math.cos(a) * 0.16, math.sin(a) * 0.16, -0.15), nut, coll, seg=12); s.parent = crown
    _sway(crown, 0.06, 80 + seed * 7, seed * 23, axis=0); _sway(piv, 0.012, 110 + seed * 5, seed * 11, axis=1)
    return piv

def build_beach(O=Vector((1100, 0, 0))):
    sn = "beach"; c = col(sn); rnd = random.Random(11)
    sand = M("bch_sand", (0.93, 0.80, 0.56), 0.95, bump=0.6, bump_scale=60)
    wet = M("bch_wet", (0.72, 0.58, 0.38), 0.35, bump=0.3, bump_scale=60)
    sea = M("bch_sea", (0.05, 0.42, 0.68), 0.08, coat=1.0)
    deep = M("bch_deep", (0.03, 0.28, 0.55), 0.1, coat=0.8)
    foam = M("bch_foam", (1, 1, 1), 0.6, emit=(1, 1, 1), emit_str=0.25)
    red = M("bch_red", (0.90, 0.08, 0.10), 0.35, coat=0.5); white = M("bch_white", (0.97, 0.97, 0.95), 0.5)
    yel = M("bch_yel", (1.0, 0.80, 0.08), 0.35, coat=0.5); blue = M("bch_blue", (0.12, 0.42, 0.92), 0.35, coat=0.5)
    green = M("bch_green", (0.12, 0.72, 0.22), 0.3, coat=0.6); orange = M("bch_orange", (1.0, 0.42, 0.05), 0.4, coat=0.4)
    dark = M("bch_dark", (0.03, 0.03, 0.03), 0.3)
    # ---- sand: big ground + gentle dunes behind the cast, wet-sand band at the shore ----
    box(sn + "_sand", (160, 60, 0.2), (O.x, O.y - 20, -0.1), sand, c, 0)
    box(sn + "_wet", (160, 2.2, 0.02), (O.x, O.y + 6.9, 0.0), wet, c, 0)
    for i, (x, y, r, hh) in enumerate([(-14, -9, 6, 0.9), (13, -10, 7, 1.0), (-22, 2, 6, 0.8), (22, 3, 7, 1.0)]):
        sph(sn + f"_dune{i}", r, (O.x + x, O.y + y, -r + hh), sand, c, seg=24, scale=(1.4, 1, 1))
    # ---- sea: near grid with animated waves (Wave modifier), far deep plane, foam lines that wash in and out ----
    s1 = grid(sn + "_sea", 160, 30, 120, 40, (O.x, O.y + 23, 0.02), sea, c)
    wv = s1.modifiers.new("waves", "WAVE"); wv.use_x = False; wv.use_y = True; wv.height = 0.08; wv.width = 2.4; wv.speed = 0.06; wv.narrowness = 1.2
    wv.start_position_y = -15; wv.time_offset = 0; wv.use_cyclic = True; wv.lifetime = 0; wv.damping_time = 0
    s1.modifiers.new("sm", "SUBSURF").levels = 0
    box(sn + "_deep", (400, 200, 0.02), (O.x, O.y + 135, 0.0), deep, c, 0)
    foams = []
    for i in range(3):
        fo = box(sn + f"_foam{i}", (160, 0.22 + 0.05 * i, 0.02), (O.x, O.y + 8.2 + i * 1.8, 0.04), foam, c, 0)
        for f in range(1, 8001, 6):
            ph = (f + i * 40) / 120.0 * 2 * math.pi
            fo.location.y = O.y + 8.2 + i * 1.8 - 0.55 * (0.5 + 0.5 * math.sin(ph)); fo.scale.y = 0.7 + 0.5 * (0.5 + 0.5 * math.cos(ph))
            fo.keyframe_insert("location", frame=f, index=1); fo.keyframe_insert("scale", frame=f, index=1)
        foams.append(fo)
    # ---- palm trees (sway), umbrella + towels, sandcastle, shells, starfish ----
    palms = [palm(sn + f"_palm{i}", (O.x + x, O.y + y, 0), c, h, lean, yaw, seed=i)
             for i, (x, y, h, lean, yaw) in enumerate([(-6.5, 3.0, 4.6, 16, 20), (-8.5, 0.5, 3.8, 10, 160), (6.8, 2.6, 4.8, 18, 160), (9.0, -0.5, 4.0, 12, 30), (-12, 5, 5.0, 14, 10), (13, 4.5, 4.4, 16, 170)])]
    UX, UY = O.x - 3.4, O.y + 2.4
    cyl(sn + "_umb_pole", 0.03, 2.2, (UX, UY, 1.1), white, c, 10)
    um = striped_cone(sn + "_umb", 1.25, 0.05, 0.45, (UX, UY, 2.1), red, white, c, n=8); _sway(um, 0.02, 90, 0, axis=0)
    box(sn + "_towel0", (0.8, 1.7, 0.01), (UX + 0.6, UY - 0.4, 0.01), blue, c, 0, rot=(0, 0, math.radians(15)))
    box(sn + "_towel1", (0.8, 1.7, 0.01), (UX - 0.7, UY - 0.2, 0.01), yel, c, 0, rot=(0, 0, math.radians(-10)))
    # sandcastle
    CX, CY = O.x + 3.6, O.y + 1.6
    cyl(sn + "_castle_base", 0.55, 0.35, (CX, CY, 0.17), sand, c, 32, bevel=0)
    for i in range(4):
        a = i / 4 * 2 * math.pi + 0.4; tx, ty = CX + math.cos(a) * 0.5, CY + math.sin(a) * 0.5
        cyl(sn + f"_castle_t{i}", 0.17, 0.6, (tx, ty, 0.3), sand, c, 20, bevel=0)
        for k in range(4):
            b_ = k / 4 * 2 * math.pi
            box(sn + f"_castle_c{i}{k}", (0.07, 0.07, 0.07), (tx + math.cos(b_) * 0.13, ty + math.sin(b_) * 0.13, 0.63), sand, c, 0)
    cyl(sn + "_castle_keep", 0.25, 0.85, (CX, CY, 0.42), sand, c, 24, bevel=0)
    cyl(sn + "_flagpole", 0.012, 0.5, (CX, CY, 1.08), white, c, 6)
    box(sn + "_flag", (0.01, 0.22, 0.13), (CX, CY + 0.11, 1.26), blue, c, 0)
    # RED bucket + yellow spade by the castle
    BX, BY = CX - 1.1, CY - 0.6
    bk = cone(sn + "_bucket", 0.13, 0.17, 0.26, (BX, BY, 0.13), red, c)
    hd = bpy.data.objects.new(sn + "_bucket_handle", bpy.data.curves.new(sn + "_bh", "CURVE")); c.objects.link(hd)
    hd.data.dimensions = "3D"; hd.data.bevel_depth = 0.008; sp = hd.data.splines.new("NURBS"); sp.points.add(4)
    for i_, (x_, z_) in enumerate([(-0.17, 0.26), (-0.14, 0.40), (0, 0.46), (0.14, 0.40), (0.17, 0.26)]): sp.points[i_].co = (BX + x_, BY, z_, 1)
    sp.use_endpoint_u = True; hd.data.materials.append(dark)
    box(sn + "_spade_h", (0.03, 0.03, 0.35), (BX + 0.3, BY - 0.05, 0.2), yel, c, 0.005, rot=(0, math.radians(20), 0))
    box(sn + "_spade_b", (0.12, 0.02, 0.14), (BX + 0.36, BY - 0.05, 0.05), yel, c, 0.01, rot=(0, math.radians(20), 0))
    # GREEN beach ball (bounces gently; props may override)
    ball = striped_sphere(sn + "_ball", 0.2, (O.x + 1.9, O.y - 0.9, 0.2), green, white, c, n=6)
    # shells + starfish scattered
    for i in range(18):
        x = rnd.uniform(-8, 8); y = rnd.uniform(-3, 6)
        if abs(x) < 2.6 and -1.5 < y < 1.5: continue
        sph(sn + f"_shell{i}", 0.05, (O.x + x, O.y + y, 0.01), M("bch_shell%d" % (i % 3), [(1, 0.85, 0.8), (0.95, 0.9, 0.75), (1, 0.7, 0.6)][i % 3], 0.4), c, scale=(1, 0.8, 0.4), seg=10)
    for i, (x, y) in enumerate([(-1.8, 3.6), (4.8, -1.2), (-4.6, -1.6)]):
        g = bpy.data.objects.new(sn + f"_star{i}", None); c.objects.link(g); g.location = (O.x + x, O.y + y, 0.02); g.rotation_euler = (0, 0, i)
        for k in range(5):
            a = k / 5 * 2 * math.pi; s = sph(sn + f"_star{i}_{k}", 0.09, (math.cos(a) * 0.08, math.sin(a) * 0.08, 0), M("bch_starm", (1.0, 0.55, 0.35), 0.6), c, scale=(1.4, 0.45, 0.3), seg=10)
            s.rotation_euler = (0, 0, a); s.parent = g
    # ---- ORANGE crab (props animate its walk) ----
    crab = bpy.data.objects.new(sn + "_crab", None); c.objects.link(crab); crab.location = (O.x + 5.5, O.y - 1.0, 0.0)
    b = sph(sn + "_crab_body", 0.16, (0, 0, 0.12), orange, c, scale=(1.3, 0.9, 0.55), seg=20); b.parent = crab
    for sx in (-1, 1):
        st = cyl(sn + f"_crab_stalk{sx}", 0.012, 0.09, (sx * 0.06, -0.08, 0.22), orange, c, 6); st.parent = crab
        ey = sph(sn + f"_crab_eye{sx}", 0.032, (sx * 0.06, -0.09, 0.28), white, c, seg=10); ey.parent = crab
        pu = sph(sn + f"_crab_pupil{sx}", 0.016, (sx * 0.06, -0.115, 0.285), dark, c, seg=8); pu.parent = crab
        cl = bpy.data.objects.new(sn + f"_crab_claw{sx}", None); c.objects.link(cl); cl.parent = crab; cl.location = (sx * 0.24, -0.12, 0.14)
        a_ = sph(sn + f"_crab_clawa{sx}", 0.07, (0, 0, 0.0), orange, c, scale=(1, 0.8, 0.7), seg=12); a_.parent = cl
        _sway(cl, 0.35, 14, 5 * sx, axis=0, step=3)
        for k in range(3):
            lg = cyl(sn + f"_crab_leg{sx}{k}", 0.012, 0.16, (sx * 0.2, -0.04 + k * 0.07, 0.06), orange, c, 6, rot=(0, sx * math.radians(60), 0)); lg.parent = crab
    # ---- sky dome, BIG YELLOW SUN with a friendly glow, clouds, seagulls, sailboat ----
    skym = sets2.M_sky_window("bch_skym", top=(0.18, 0.50, 0.98), bottom=(0.75, 0.90, 1.0), strength=2.6, trees=False)
    plane(sn + "_sky", (500, 180), (O.x, O.y + 160, 40), skym, c, rot=(math.radians(90), 0, 0))
    plane(sn + "_skyl", (400, 180), (O.x - 150, O.y + 30, 40), skym, c, rot=(math.radians(90), 0, math.radians(90)))
    plane(sn + "_skyr", (400, 180), (O.x + 150, O.y + 30, 40), skym, c, rot=(math.radians(90), 0, math.radians(90)))
    plane(sn + "_skyb", (400, 180), (O.x, O.y - 60, 40), skym, c, rot=(math.radians(90), 0, 0))
    SUN = Vector((O.x + 18, O.y + 120, 26))
    sunm = M("bch_sun", (1, 0.85, 0.1), 0.5, emit=(1.0, 0.82, 0.12), emit_str=6.0)
    sph(sn + "_sunball", 7.0, SUN, sunm, c, seg=32)
    halo = M("bch_halo", (1, 0.9, 0.4), 0.5, emit=(1.0, 0.9, 0.4), emit_str=1.2)
    for k in range(12):
        a = k / 12 * 2 * math.pi
        r_ = box(sn + f"_ray{k}", (1.0, 0.1, 4.5), (SUN.x + math.sin(a) * 11, SUN.y + 1, SUN.z + math.cos(a) * 11), halo, c, 0, rot=(0, a, 0))
    cloudm = M("bch_cloud", (1, 1, 1), 0.9, emit=(1, 1, 1), emit_str=0.9)
    clouds = []
    for i in range(8):
        g = bpy.data.objects.new(sn + f"_cloud{i}", None); c.objects.link(g)
        x0 = rnd.uniform(-110, 110); y0 = rnd.uniform(90, 150); z0 = rnd.uniform(20, 40)
        for j in range(5):
            s = sph(sn + f"_cl{i}_{j}", rnd.uniform(3, 6), (rnd.uniform(-6, 6), rnd.uniform(-2, 2), rnd.uniform(-1, 1.5)), cloudm, c, seg=12, scale=(1.5, 1.0, 0.6)); s.parent = g
        g.location = (O.x + x0, O.y + y0, z0); g.keyframe_insert("location", frame=1)
        g.location = (O.x + x0 + 30, O.y + y0, z0); g.keyframe_insert("location", frame=8000)
        clouds.append(g)
    gullm = M("bch_gull", (0.98, 0.98, 0.98), 0.6); gullt = M("bch_gullt", (0.3, 0.3, 0.32), 0.6)
    gulls = []
    for i in range(4):
        g = bpy.data.objects.new(sn + f"_gull{i}", None); c.objects.link(g)
        bd = sph(sn + f"_gullb{i}", 0.12, (0, 0, 0), gullm, c, scale=(1.6, 0.6, 0.6), seg=10); bd.parent = g
        for sx in (-1, 1):
            w_ = bpy.data.objects.new(sn + f"_gullwp{i}{sx}", None); c.objects.link(w_); w_.parent = g
            wm = box(sn + f"_gullw{i}{sx}", (0.2, 0.55, 0.015), (0, sx * 0.28, 0), gullm, c, 0); wm.parent = w_
            wt = box(sn + f"_gullwt{i}{sx}", (0.12, 0.12, 0.016), (0, sx * 0.52, 0), gullt, c, 0); wt.parent = w_
            for f in range(1, 8001, 4):
                w_.rotation_euler = (sx * 0.5 * math.sin((f + i * 7) / 9.0 * 2 * math.pi), 0, 0); w_.keyframe_insert("rotation_euler", frame=f)
        R_, H_, cx, cy = 6 + 2 * i, 7 + 1.5 * i, O.x + rnd.uniform(-4, 4), O.y + 14 + 4 * i
        for f in range(1, 8001, 12):
            t = (f + i * 200) / (500 + 60 * i) * 2 * math.pi
            g.location = (cx + math.cos(t) * R_, cy + math.sin(t) * R_ * 0.5, H_ + 0.4 * math.sin(t * 3)); g.rotation_euler = (0, 0, t + math.pi / 2)
            g.keyframe_insert("location", frame=f); g.keyframe_insert("rotation_euler", frame=f)
        gulls.append(g)
    boat = bpy.data.objects.new(sn + "_boat", None); c.objects.link(boat); boat.location = (O.x - 14, O.y + 45, 0.1)
    h_ = sph(sn + "_hull", 1.0, (0, 0, 0), red, c, scale=(2.2, 0.7, 0.45), seg=16); h_.parent = boat
    mast = cyl(sn + "_mast", 0.05, 3.2, (0, 0, 1.7), white, c, 8); mast.parent = boat
    sl = cone(sn + "_sail", 1.1, 0.02, 2.8, (0.5, 0, 1.8), white, c, seg=3); sl.scale = (0.7, 0.08, 1); sl.parent = boat
    for f in range(1, 8001, 8):
        boat.location.x = O.x - 14 + f * 0.0015; boat.rotation_euler = (0.05 * math.sin(f / 40.0), 0.03 * math.sin(f / 31.0), 0)
        boat.keyframe_insert("location", frame=f, index=0); boat.keyframe_insert("rotation_euler", frame=f)
    # ---- lights: warm sun + blue sky fill + sand bounce ----
    sun = bpy.data.objects.new(sn + "_sunlight", bpy.data.lights.new(sn + "_sunlight", "SUN")); c.objects.link(sun)
    sun.data.energy = 4.8; sun.data.color = (1.0, 0.93, 0.80); sun.data.angle = math.radians(3); sun.location = (O.x, O.y, 10)
    sun.rotation_euler = (math.radians(48), 0, math.radians(-150))
    area(sn + "_skyfill", (O.x, O.y - 4, 6.0), (O.x, O.y + 2, 0.5), 650, 8.0, c, (0.75, 0.86, 1.0))
    area(sn + "_front", (O.x - 1.5, O.y - 5.0, 2.4), (O.x, O.y + 1.0, 0.9), 380, 4.0, c, (1.0, 0.94, 0.86))
    area(sn + "_bounce", (O.x, O.y - 1.0, 0.05), (O.x, O.y - 1.0, 2.0), 120, 6.0, c, (1.0, 0.88, 0.65))
    SETS[sn] = dict(origin=O, coll=c, palms=palms, foams=foams, gulls=gulls, clouds=clouds, ball=ball, crab=crab, bucket=bk, sun=SUN, castle=(CX, CY),
                    cams={"beach_wide": ((O.x + 0.2, O.y - 4.0, 1.35), (O.x + 0.2, O.y + 1.6, 0.95), 30),
                          "low_wide": ((O.x - 1.4, O.y - 4.3, 0.55), (O.x + 0.3, O.y + 1.6, 1.0), 28),
                          "insert:bucket": ((BX + 0.25, BY - 1.25, 0.55), (BX + 0.1, BY, 0.18), 40),
                          "insert:sun": ((O.x + 0.5, O.y - 2.0, 1.2), (SUN.x, SUN.y, SUN.z - 4), 26),
                          "insert:sea": ((O.x - 0.5, O.y + 4.6, 1.3), (O.x - 2.0, O.y + 30, 0.6), 24),
                          "insert:ball": ((O.x + 1.4, O.y - 2.3, 0.7), (O.x + 1.9, O.y - 0.9, 0.35), 38),
                          "insert:crab": ((O.x + 4.0, O.y - 2.6, 0.5), (O.x + 3.4, O.y - 1.0, 0.15), 38),
                          "insert:castle": ((CX - 0.3, CY - 2.0, 0.7), (CX, CY, 0.45), 38)})
    return SETS[sn]

sets2.build_beach = build_beach
