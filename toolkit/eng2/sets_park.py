# Ep7+: outdoor PARK set (playground, pond, trees that sway, moving clouds, path, benches, hills), day lighting.
import bpy, math, random
from mathutils import Vector
import sets2
from sets2 import SETS, M, M_wood, box, cyl, sph, plane, area, point, col, text

def _key_sway(o, amp=0.012, period=96, phase=0.0, frames=8000, axis=0):
    for f in range(1, frames + 1, 12):
        v = [0, 0, 0]; v[axis] = amp * math.sin((f + phase) / period * 2 * math.pi) + amp * 0.35 * math.sin((f + phase) / (period * 0.37) * 2 * math.pi)
        o.delta_rotation_euler = v; o.keyframe_insert("delta_rotation_euler", frame=f)

def tree(name, loc, coll, h=3.2, r=1.1, kind=0, seed=0):
    rnd = random.Random(seed)
    bark = M("park_bark", (0.36, 0.24, 0.14), 0.9, bump=0.5, bump_scale=30)
    leaf = [M("park_leaf0", (0.25, 0.55, 0.18), 0.8, bump=0.5, bump_scale=14), M("park_leaf1", (0.35, 0.62, 0.2), 0.8, bump=0.5, bump_scale=14), M("park_leaf2", (0.2, 0.5, 0.22), 0.8, bump=0.5, bump_scale=14)][kind % 3]
    pivot = bpy.data.objects.new(name + "_pivot", None); coll.objects.link(pivot); pivot.location = loc
    t = cyl(name + "_trunk", 0.14 * h / 3.2, h * 0.55, (0, 0, h * 0.275), bark, coll, 12); t.parent = pivot
    for i in range(5):
        a = rnd.uniform(0, 2 * math.pi); d = rnd.uniform(0.0, r * 0.45); zz = h * 0.55 + rnd.uniform(0.1, r * 0.8)
        s = sph(name + f"_c{i}", r * rnd.uniform(0.55, 0.8), (math.cos(a) * d, math.sin(a) * d, zz), leaf, coll, seg=16); s.parent = pivot
    s = sph(name + "_top", r * 0.6, (0, 0, h * 0.55 + r * 1.1), leaf, coll, seg=16); s.parent = pivot
    _key_sway(pivot, amp=0.012 + 0.004 * (seed % 3), period=90 + 11 * (seed % 5), phase=seed * 17.0)
    return pivot

def bench(name, loc, yaw, coll):
    wood = M_wood("park_benchw", (0.6, 0.4, 0.2), (0.45, 0.28, 0.12), scale=4)
    iron = M("park_iron", (0.12, 0.12, 0.13), 0.4, 0.7)
    g = bpy.data.objects.new(name, None); coll.objects.link(g); g.location = loc; g.rotation_euler = (0, 0, math.radians(yaw))
    for i, z in enumerate((0.42, 0.47)): pass
    for i in range(3): b = box(name + f"_s{i}", (1.5, 0.11, 0.03), (0, -0.14 + i * 0.14, 0.44), wood, coll, 0.006); b.parent = g
    for i in range(2): b = box(name + f"_b{i}", (1.5, 0.03, 0.11), (0, 0.22, 0.62 + i * 0.14), wood, coll, 0.006); b.parent = g
    for x in (-0.62, 0.62):
        l = box(name + f"_l{x}", (0.05, 0.4, 0.42), (x, 0, 0.21), iron, coll, 0.005); l.parent = g
        l2 = box(name + f"_bk{x}", (0.05, 0.05, 0.45), (x, 0.22, 0.6), iron, coll, 0.005); l2.parent = g
    return g

def build_park(O=Vector((900, 0, 0))):
    sn = "park"; c = col(sn)
    grass = M("park_grass", (0.30, 0.58, 0.20), 0.9, bump=0.7, bump_scale=18)
    grass2 = M("park_grass2", (0.36, 0.62, 0.22), 0.9, bump=0.7, bump_scale=18)
    sand = M("park_sand", (0.85, 0.75, 0.55), 0.95, bump=0.5, bump_scale=40)
    path = M("park_path", (0.72, 0.66, 0.58), 0.85, bump=0.4, bump_scale=25)
    water = M("park_water", (0.25, 0.55, 0.75), 0.05, coat=1.0); water.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.8
    try: water.surface_render_method = "BLENDED"
    except Exception: pass
    red = M("park_red", (0.85, 0.15, 0.15), 0.35, coat=0.5); yel = M("park_yel", (0.98, 0.78, 0.12), 0.35, coat=0.5); blue = M("park_blue", (0.15, 0.45, 0.9), 0.35, coat=0.5)
    steel = M("park_steel", (0.75, 0.77, 0.8), 0.25, 0.9); rope = M("park_rope", (0.6, 0.5, 0.35), 0.9)
    # ground: big grass disc + a lighter lawn patch; gentle hills in the distance
    cyl(sn + "_ground", 80, 0.2, (O.x, O.y + 10, -0.1), grass, c, 96, bevel=0)
    cyl(sn + "_lawn", 7.5, 0.02, (O.x, O.y + 0.5, 0.0), grass2, c, 64, bevel=0)
    rnd = random.Random(7)
    for i, (x, y, r, hgt) in enumerate([(-30, 55, 26, 7), (10, 62, 30, 9), (42, 50, 22, 6), (-55, 45, 20, 5), (70, 60, 28, 7)]):
        sph(sn + f"_hill{i}", r, (O.x + x, O.y + y, -r + hgt), M("park_hill", (0.32, 0.55, 0.25), 0.95, bump=0.3, bump_scale=4), c, seg=24)
    # winding path (segments)
    for i in range(9):
        a = i * 0.35; px = O.x - 4.5 + i * 1.15; py = O.y - 2.2 + math.sin(a) * 0.8
        box(sn + f"_path{i}", (1.3, 1.1, 0.03), (px, py, 0.01), path, c, 0.01, rot=(0, 0, math.cos(a) * 0.25))
    # sand pit for the playground
    cyl(sn + "_sand", 3.2, 0.04, (O.x + 2.6, O.y + 2.6, 0.0), sand, c, 48, bevel=0)
    # ---- slide ----
    SX, SY = O.x + 3.4, O.y + 3.2
    box(sn + "_slide_ramp", (0.7, 2.6, 0.06), (SX, SY - 0.2, 0.75), yel, c, 0.02, rot=(math.radians(-28), 0, 0))
    for s_ in (-0.33, 0.33): box(sn + f"_slide_rail{s_}", (0.05, 2.6, 0.18), (SX + s_, SY - 0.2, 0.84), red, c, 0.01, rot=(math.radians(-28), 0, 0))
    box(sn + "_slide_top", (0.8, 0.8, 0.06), (SX, SY + 1.3, 1.38), blue, c, 0.02)
    for x_ in (-0.35, 0.35):
        for y_ in (0.95, 1.65): cyl(sn + f"_slide_post{x_}{y_}", 0.035, 1.4, (SX + x_, SY + y_, 0.7), steel, c, 10)
    for i in range(5): cyl(sn + f"_slide_rung{i}", 0.02, 0.7, (SX, SY + 1.72, 0.25 + i * 0.26), steel, c, 8, rot=(0, math.radians(90), 0))
    for x_ in (-0.35, 0.35): box(sn + f"_slide_ladder{x_}", (0.04, 0.04, 1.4), (SX + x_, SY + 1.72, 0.7), red, c, 0.005)
    box(sn + "_slide_roof", (1.0, 1.0, 0.05), (SX, SY + 1.3, 2.25), red, c, 0.02, rot=(0, math.radians(8), 0))
    # ---- swings ----
    WX, WY = O.x - 2.8, O.y + 3.4
    for x_ in (-1.2, 1.2):
        for dy in (-0.55, 0.55): cyl(sn + f"_swA{x_}{dy}", 0.04, 2.6, (WX + x_, WY + dy * 0.6, 1.2), blue, c, 10, rot=(math.radians(14) * (1 if dy > 0 else -1), 0, 0))
    cyl(sn + "_swbar", 0.04, 2.8, (WX, WY, 2.35), blue, c, 10, rot=(0, math.radians(90), 0))
    swings = []
    for i, x_ in enumerate((-0.45, 0.45)):
        piv = bpy.data.objects.new(sn + f"_swing{i}", None); c.objects.link(piv); piv.location = (WX + x_, WY, 2.35)
        for rx in (-0.2, 0.2):
            r_ = cyl(sn + f"_swrope{i}{rx}", 0.012, 1.75, (rx, 0, -0.88), rope, c, 6); r_.parent = piv
        seat = box(sn + f"_swseat{i}", (0.46, 0.18, 0.04), (0, 0, -1.77), red if i else yel, c, 0.01); seat.parent = piv
        _key_sway(piv, amp=0.35 if i == 0 else 0.22, period=70 if i == 0 else 60, phase=i * 30, frames=8000, axis=0)
        swings.append(piv)
    # ---- see-saw ----
    EX, EY = O.x + 0.2, O.y + 4.6
    box(sn + "_ss_base", (0.5, 0.3, 0.5), (EX, EY, 0.25), steel, c, 0.02)
    ssp = bpy.data.objects.new(sn + "_seesaw", None); c.objects.link(ssp); ssp.location = (EX, EY, 0.5)
    pl_ = box(sn + "_ss_plank", (3.0, 0.3, 0.06), (0, 0, 0), yel, c, 0.01); pl_.parent = ssp
    for x_ in (-1.35, 1.35):
        h_ = box(sn + f"_ss_h{x_}", (0.06, 0.3, 0.25), (x_, 0, 0.15), red, c, 0.01); h_.parent = ssp
    _key_sway(ssp, amp=0.16, period=85, phase=20, frames=8000, axis=1)
    # ---- pond with lily pads and ducks ----
    PX, PY = O.x - 4.0, O.y - 0.6
    cyl(sn + "_pondrim", 2.5, 0.05, (PX, PY, 0.0), M("park_mud", (0.45, 0.38, 0.25), 0.95, bump=0.4, bump_scale=30), c, 48, bevel=0)
    cyl(sn + "_pond", 2.25, 0.02, (PX, PY, 0.02), water, c, 48, bevel=0)
    for i in range(6):
        a = i / 6 * 2 * math.pi; cyl(sn + f"_lily{i}", 0.18, 0.01, (PX + math.cos(a) * 1.5, PY + math.sin(a) * 1.5, 0.035), M("park_lily", (0.2, 0.5, 0.2), 0.7), c, 16, bevel=0)
    ducks = []
    for i in range(3):
        d = bpy.data.objects.new(sn + f"_duck{i}", None); c.objects.link(d); d.location = (PX + 0.6 * i - 0.6, PY + 0.4 * (i % 2), 0.05)
        bd = sph(sn + f"_duckb{i}", 0.14, (0, 0, 0.08), yel, c, seg=14, scale=(1.3, 0.9, 0.8)); bd.parent = d
        hd = sph(sn + f"_duckh{i}", 0.08, (0.14, 0, 0.24), yel, c, seg=12); hd.parent = d
        bk = box(sn + f"_duckbk{i}", (0.08, 0.05, 0.03), (0.23, 0, 0.23), M("park_beak", (0.95, 0.5, 0.1), 0.4), c, 0.004); bk.parent = d
        # slow drifting circle
        for f in range(1, 8001, 24):
            t = (f + i * 300) / 900.0 * 2 * math.pi
            d.location = (PX + math.cos(t) * (0.9 + 0.3 * i), PY + math.sin(t) * (0.7 + 0.2 * i), 0.05); d.rotation_euler = (0, 0, t + math.pi / 2)
            d.keyframe_insert("location", frame=f); d.keyframe_insert("rotation_euler", frame=f)
        ducks.append(d)
    # ---- trees, hedges, flowers, benches, lamp, fence, bin ----
    trees = []
    for i, (x, y, h, r) in enumerate([(-7.5, 6.5, 3.6, 1.3), (7.5, 7.0, 4.0, 1.5), (-9.0, 1.0, 3.0, 1.1), (9.5, 1.5, 3.4, 1.2), (0.0, 9.0, 4.4, 1.6), (-4.5, 9.5, 3.2, 1.2), (5.0, 10.5, 3.8, 1.4), (-12, 8, 3.5, 1.3), (12, 9, 3.6, 1.3), (-6.5, -4.5, 2.8, 1.0), (7.0, -4.8, 3.0, 1.1)]):
        trees.append(tree(sn + f"_tree{i}", (O.x + x, O.y + y, 0), c, h, r, i, seed=i))
    hedge = M("park_hedge", (0.22, 0.45, 0.16), 0.9, bump=0.6, bump_scale=20)
    for i in range(10): box(sn + f"_hedge{i}", (1.4, 0.5, 0.6), (O.x - 7 + i * 1.5, O.y + 8.0, 0.3), hedge, c, 0.08)
    for i in range(40):
        x = rnd.uniform(-9, 9); y = rnd.uniform(-3.5, 8)
        if math.hypot(x - 2.6, y - 2.6) < 3.6 or math.hypot(x + 4, y + 0.6) < 2.8 or abs(y + 2.2) < 0.9: continue
        cc = rnd.choice([(0.95, 0.2, 0.3), (0.98, 0.85, 0.2), (0.9, 0.4, 0.8), (1.0, 1.0, 1.0)])
        cyl(sn + f"_fstem{i}", 0.01, 0.18, (O.x + x, O.y + y, 0.09), M("park_stem", (0.2, 0.5, 0.15), 0.8), c, 6)
        sph(sn + f"_flower{i}", 0.05, (O.x + x, O.y + y, 0.2), M(f"park_fl{i % 4}", cc, 0.5), c, seg=8)
    bench(sn + "_bench0", (O.x - 1.2, O.y - 0.9, 0), 180, c); bench(sn + "_bench1", (O.x + 6.0, O.y - 0.4, 0), 160, c)
    cyl(sn + "_lamp", 0.05, 3.2, (O.x - 3.2, O.y - 2.9, 1.6), M("park_lampm", (0.1, 0.1, 0.12), 0.4, 0.6), c, 10)
    sph(sn + "_lampglass", 0.22, (O.x - 3.2, O.y - 2.9, 3.3), M("park_lampg", (1, 0.95, 0.8), 0.3, emit=(1, 0.9, 0.7), emit_str=0.6), c, seg=14)
    cyl(sn + "_bin", 0.22, 0.6, (O.x + 4.6, O.y - 1.4, 0.3), M("park_bin", (0.2, 0.5, 0.25), 0.5), c, 16)
    for i in range(26): box(sn + f"_fence{i}", (0.08, 0.04, 0.7), (O.x - 10 + i * 0.8, O.y + 11.5, 0.35), M("park_fence", (0.95, 0.95, 0.9), 0.6), c, 0.01)
    box(sn + "_fencebar", (21, 0.04, 0.06), (O.x, O.y + 11.5, 0.55), M("park_fence", (0.95, 0.95, 0.9), 0.6), c, 0.01)
    # ---- sky dome, sun, clouds (drift) ----
    skym = sets2.M_sky_window("park_skym", top=(0.30, 0.55, 0.98), bottom=(0.80, 0.90, 1.0), strength=2.6, trees=False)
    plane(sn + "_sky", (400, 160), (O.x, O.y + 120, 40), skym, c, rot=(math.radians(90), 0, 0))
    plane(sn + "_skyl", (300, 160), (O.x - 120, O.y + 30, 40), skym, c, rot=(math.radians(90), 0, math.radians(90)))
    plane(sn + "_skyr", (300, 160), (O.x + 120, O.y + 30, 40), skym, c, rot=(math.radians(90), 0, math.radians(90)))
    sunm = M("park_sun", (1, 1, 0.9), 0.5, emit=(1.0, 0.95, 0.8), emit_str=14.0)
    sph(sn + "_sunball", 4.0, (O.x - 30, O.y + 110, 42.0), sunm, c)
    cloudm = M("park_cloud", (1, 1, 1), 0.9, emit=(1, 1, 1), emit_str=0.9)
    clouds = []
    for i in range(9):
        g = bpy.data.objects.new(sn + f"_cloud{i}", None); c.objects.link(g)
        x0 = rnd.uniform(-90, 90); y0 = rnd.uniform(60, 110); z0 = rnd.uniform(18, 34)
        for j in range(5):
            s = sph(sn + f"_cl{i}_{j}", rnd.uniform(2.5, 5.0), (rnd.uniform(-5, 5), rnd.uniform(-2, 2), rnd.uniform(-1, 1.5)), cloudm, c, seg=12, scale=(1.4, 1.0, 0.7)); s.parent = g
        g.location = (O.x + x0, O.y + y0, z0); g.keyframe_insert("location", frame=1)
        g.location = (O.x + x0 + 24, O.y + y0, z0); g.keyframe_insert("location", frame=8000)
        clouds.append(g)
    # ---- lights: sun + sky fill + ground bounce ----
    sun = bpy.data.objects.new(sn + "_sunlight", bpy.data.lights.new(sn + "_sunlight", "SUN")); c.objects.link(sun)
    sun.data.energy = 4.5; sun.data.color = (1.0, 0.95, 0.85); sun.data.angle = math.radians(2.5); sun.location = (O.x, O.y, 10)
    sun.rotation_euler = (math.radians(50), 0, math.radians(-35))
    area(sn + "_skyfill", (O.x, O.y - 4, 6.0), (O.x, O.y + 2, 0.5), 600, 8.0, c, (0.75, 0.85, 1.0))
    area(sn + "_front", (O.x + 2.0, O.y - 5.0, 2.5), (O.x, O.y + 1.5, 0.9), 350, 4.0, c, (1.0, 0.95, 0.9))
    SETS[sn] = dict(origin=O, coll=c, trees=trees, swings=swings, ducks=ducks, clouds=clouds, slide=(SX, SY), pond=(PX, PY), seesaw=ssp,
                    cams={"park_wide": ((O.x + 0.4, O.y - 5.2, 1.6), (O.x + 0.2, O.y + 1.5, 0.8), 26),
                          "low_wide": ((O.x - 1.5, O.y - 4.2, 0.6), (O.x + 0.3, O.y + 1.5, 0.9), 28),
                          "insert:slide": ((SX - 2.2, SY - 2.0, 1.2), (SX, SY + 0.6, 1.1), 35),
                          "insert:swings": ((WX + 1.5, WY - 3.0, 1.1), (WX, WY, 1.2), 32),
                          "insert:pond": ((PX + 1.6, PY - 2.4, 1.0), (PX - 0.3, PY + 0.3, 0.1), 35),
                          "insert:sky": ((O.x, O.y - 2, 1.4), (O.x - 20, O.y + 100, 40), 30),
                          "insert:seesaw": ((EX - 2.4, EY - 2.0, 0.9), (EX, EY, 0.5), 35)})
    return SETS[sn]

sets2.build_park = build_park
