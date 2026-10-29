# Song 03: JUNGLE clearing set (origin x=1300): mossy ground, dense trees + palms that sway, giant leaves, hanging vines,
# rocks, a little waterfall + pool, big colourful flowers, fireflies/butterflies, warm god-ray lighting.
import bpy, bmesh, math, random
from mathutils import Vector
import sets2, sets_park, sets_beach
from sets2 import SETS, M, box, cyl, sph, plane, area, col

def leaf_plant(name, loc, coll, n=7, size=0.9, seed=0, mat=None):
    rnd = random.Random(seed)
    g = bpy.data.objects.new(name, None); coll.objects.link(g); g.location = loc
    for i in range(n):
        a = i / n * 2 * math.pi + rnd.uniform(-0.3, 0.3); tilt = rnd.uniform(0.5, 1.0)
        lf = sph(f"{name}_l{i}", size * rnd.uniform(0.7, 1.1), (0, 0, 0), mat, coll, scale=(1.0, 0.38, 0.04), seg=14)
        lf.parent = g; lf.location = (math.cos(a) * size * 0.7, math.sin(a) * size * 0.7, size * 0.45 * tilt); lf.rotation_euler = (0, -tilt * 0.6, a)
    sets_beach._sway(g, 0.03, 70 + seed * 3, seed * 13, axis=0)
    return g

def build_jungle(O=Vector((1300, 0, 0))):
    sn = "jungle"; c = col(sn); rnd = random.Random(21)
    moss = M("jg_moss", (0.22, 0.42, 0.14), 0.95, bump=0.7, bump_scale=30)
    dirt = M("jg_dirt", (0.42, 0.30, 0.18), 0.95, bump=0.6, bump_scale=40)
    rock = M("jg_rock", (0.45, 0.45, 0.42), 0.8, bump=0.8, bump_scale=12)
    leafA = M("jg_leafA", (0.12, 0.50, 0.15), 0.6); leafB = M("jg_leafB", (0.25, 0.62, 0.12), 0.6); leafC = M("jg_leafC", (0.08, 0.38, 0.20), 0.6)
    vine = M("jg_vine", (0.18, 0.40, 0.10), 0.8)
    water = M("jg_water", (0.25, 0.65, 0.85), 0.05, emit=(0.5, 0.85, 1.0), emit_str=0.6, coat=1.0)
    box(sn + "_ground", (80, 60, 0.2), (O.x, O.y + 10, -0.1), moss, c, 0)
    cyl(sn + "_clearing", 4.2, 0.02, (O.x, O.y + 0.3, 0.0), dirt, c, 48, bevel=0)
    # back wall of jungle: many trees + palms in layers
    trees = []
    for i in range(16):
        x = -9 + i * 1.2 + rnd.uniform(-0.4, 0.4); y = 4.5 + rnd.uniform(0, 4.5)
        trees.append(sets_park.tree(sn + f"_tree{i}", (O.x + x, O.y + y, 0), c, rnd.uniform(3.5, 5.5), rnd.uniform(1.2, 1.8), i, seed=i + 40))
    for i, (x, y, h, lean, yaw) in enumerate([(-5.2, 2.8, 5.0, 14, 20), (5.4, 3.0, 5.2, 16, 160), (-7.0, 0.5, 4.2, 10, 160), (7.2, 0.8, 4.4, 12, 30), (-2.6, 5.5, 5.6, 8, 90), (2.9, 5.8, 5.4, 10, 100)]):
        sets_beach.palm(sn + f"_palm{i}", (O.x + x, O.y + y, 0), c, h, lean, yaw, seed=i + 7)
    # giant leaf plants framing the clearing + foreground
    for i, (x, y, s_) in enumerate([(-4.2, 1.2, 1.1), (4.3, 1.4, 1.2), (-3.0, 3.4, 0.9), (3.4, 3.6, 1.0), (-6.0, -1.5, 1.3), (6.2, -1.2, 1.3), (-1.2, 4.2, 0.8), (1.6, 4.0, 0.9), (-5.0, -3.6, 1.0), (5.2, -3.4, 1.1)]):
        leaf_plant(sn + f"_plant{i}", (O.x + x, O.y + y, 0), c, n=8, size=s_, seed=i, mat=[leafA, leafB, leafC][i % 3])
    # hanging vines from above (curves with leaves)
    for i in range(12):
        x = -5 + i * 0.95 + rnd.uniform(-0.2, 0.2); y = rnd.uniform(2.0, 4.5); top = 5.5; L = rnd.uniform(1.8, 3.4)
        cu = bpy.data.curves.new(sn + f"_vine{i}", "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = 0.018
        sp = cu.splines.new("NURBS"); sp.points.add(5)
        for k in range(6):
            z = top - L * k / 5; sp.points[k].co = (O.x + x + 0.15 * math.sin(k + i), O.y + y + 0.1 * math.cos(k * 1.3 + i), z, 1)
        sp.use_endpoint_u = True
        ob = bpy.data.objects.new(sn + f"_vine{i}", cu); c.objects.link(ob); cu.materials.append(vine)
        for k in range(4):
            lf = sph(sn + f"_vl{i}_{k}", 0.09, (O.x + x + 0.06, O.y + y, top - L * (k + 1) / 5), leafB, c, scale=(1.0, 0.4, 0.06), seg=8); lf.rotation_euler = (0, 0.6, k)
    # rocks + waterfall + pool on the back-left
    for i, (x, y, r_) in enumerate([(-3.4, 3.6, 0.9), (-2.4, 4.0, 1.2), (-4.4, 4.3, 1.1), (3.8, 2.6, 0.5), (-1.0, -2.6, 0.35)]):
        sph(sn + f"_rock{i}", r_, (O.x + x, O.y + y, r_ * 0.35), rock, c, scale=(1.2, 1.0, 0.75), seg=16)
    fall = plane(sn + "_fall", (0.9, 2.2), (O.x - 3.2, O.y + 4.05, 1.4), water, c, rot=(math.radians(85), 0, 0))
    pool = cyl(sn + "_pool", 1.2, 0.03, (O.x - 3.1, O.y + 3.0, 0.01), water, c, 40, bevel=0)
    # big colourful flowers
    petal = [M("jg_p0", (1.0, 0.25, 0.45), 0.5), M("jg_p1", (1.0, 0.75, 0.1), 0.5), M("jg_p2", (0.65, 0.3, 1.0), 0.5), M("jg_p3", (1.0, 0.45, 0.1), 0.5)]
    for i in range(26):
        x = rnd.uniform(-6.5, 6.5); y = rnd.uniform(-3.8, 4.5)
        if math.hypot(x, y - 0.3) < 3.4: continue
        h = rnd.uniform(0.25, 0.6); cyl(sn + f"_fst{i}", 0.012, h, (O.x + x, O.y + y, h / 2), vine, c, 6)
        for k in range(5):
            a = k / 5 * 2 * math.pi; p_ = sph(sn + f"_fp{i}_{k}", 0.06, (O.x + x + math.cos(a) * 0.06, O.y + y + math.sin(a) * 0.06, h), petal[i % 4], c, scale=(1, 0.5, 0.25), seg=8); p_.rotation_euler = (0, 0, a)
        sph(sn + f"_fc{i}", 0.03, (O.x + x, O.y + y, h + 0.01), M("jg_fc", (1, 0.9, 0.2), 0.5, emit=(1, 0.8, 0.2), emit_str=0.5), c, seg=8)
    # butterflies (flapping, wandering)
    wing = [M("jg_bw0", (0.2, 0.6, 1.0), 0.4, emit=(0.2, 0.5, 1.0), emit_str=0.6), M("jg_bw1", (1.0, 0.6, 0.1), 0.4, emit=(1, 0.5, 0.1), emit_str=0.6)]
    for i in range(6):
        g = bpy.data.objects.new(sn + f"_bfly{i}", None); c.objects.link(g)
        for sx in (-1, 1):
            w_ = bpy.data.objects.new(sn + f"_bfw{i}{sx}", None); c.objects.link(w_); w_.parent = g
            wm = sph(sn + f"_bfwm{i}{sx}", 0.05, (sx * 0.05, 0, 0), wing[i % 2], c, scale=(1, 0.8, 0.08), seg=8); wm.parent = w_
            for f in range(1, 8001, 3):
                w_.rotation_euler = (0, sx * 0.9 * math.sin((f + i * 5) / 2.5), 0); w_.keyframe_insert("rotation_euler", frame=f)
        cx, cy, cz = rnd.uniform(-3, 3), rnd.uniform(1.0, 3.5), rnd.uniform(1.2, 2.4)
        for f in range(1, 8001, 12):
            t = (f + i * 300) / 260.0
            g.location = (O.x + cx + 1.2 * math.sin(t), O.y + cy + 0.6 * math.sin(t * 1.7), cz + 0.3 * math.sin(t * 2.3)); g.rotation_euler = (0, 0, t * 2)
            g.keyframe_insert("location", frame=f); g.keyframe_insert("rotation_euler", frame=f)
    # sky / canopy light
    skym = sets2.M_sky_window("jg_skym", top=(0.35, 0.65, 0.95), bottom=(0.75, 0.92, 0.8), strength=2.2, trees=False)
    plane(sn + "_sky", (400, 160), (O.x, O.y + 60, 40), skym, c, rot=(math.radians(90), 0, 0))
    plane(sn + "_skyl", (300, 160), (O.x - 60, O.y + 20, 40), skym, c, rot=(math.radians(90), 0, math.radians(90)))
    plane(sn + "_skyr", (300, 160), (O.x + 60, O.y + 20, 40), skym, c, rot=(math.radians(90), 0, math.radians(90)))
    sun = bpy.data.objects.new(sn + "_sunlight", bpy.data.lights.new(sn + "_sunlight", "SUN")); c.objects.link(sun)
    sun.data.energy = 4.2; sun.data.color = (1.0, 0.92, 0.75); sun.data.angle = math.radians(3); sun.rotation_euler = (math.radians(42), 0, math.radians(-30))
    area(sn + "_skyfill", (O.x, O.y - 4, 6.0), (O.x, O.y + 2, 0.5), 600, 8.0, c, (0.8, 0.95, 0.85))
    area(sn + "_front", (O.x + 1.5, O.y - 5.0, 2.4), (O.x, O.y + 1.0, 0.9), 380, 4.0, c, (1.0, 0.95, 0.86))
    SETS[sn] = dict(origin=O, coll=c, trees=trees,
                    cams={"jungle_wide": ((O.x + 0.2, O.y - 4.0, 1.4), (O.x + 0.2, O.y + 1.6, 1.0), 30),
                          "low_wide": ((O.x - 1.3, O.y - 4.3, 0.55), (O.x + 0.3, O.y + 1.6, 1.05), 28),
                          "high_wide": ((O.x + 0.0, O.y - 4.6, 3.0), (O.x, O.y + 0.6, 0.6), 30),
                          "insert:fall": ((O.x - 1.4, O.y + 0.6, 1.2), (O.x - 3.2, O.y + 3.8, 1.2), 32)})
    return SETS[sn]

sets2.build_jungle = build_jungle
