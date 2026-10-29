# Ep 13: THE ZOO (origin x=3100). Sunny zoo plaza with a curved path, a "BRO BROS ZOO" entrance arch, and four habitats:
# GIRAFFE paddock (back-left, tall acacia tree), ELEPHANT pool (back-centre, with a water trough), MONKEY island (right, climbing
# frame + palm tree + 3 monkeys) and a PENGUIN pool with ice blocks (front-right). Ice-cream cart, benches, signposts, balloons.
# All animals are built from primitives and returned as empties so props can animate them.
import bpy, math, random
from mathutils import Vector
import sets2, sets_park
from sets2 import SETS, M, M_wood, M_tiles, box, cyl, sph, plane, area, col

def _cone(name, r1, r2, h, loc, mat, coll, rot=(0, 0, 0), verts=16):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=h, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name
    for cc in list(o.users_collection): cc.objects.unlink(o)
    coll.objects.link(o); o.data.materials.append(mat)
    for p in o.data.polygons: p.use_smooth = True
    return o

def _text(name, s, loc, size, mat, coll, rot=(math.radians(90), 0, 0)):
    cu = bpy.data.curves.new(name, "FONT"); cu.body = s; cu.size = size; cu.align_x = "CENTER"; cu.align_y = "CENTER"; cu.extrude = 0.01
    o = bpy.data.objects.new(name, cu); coll.objects.link(o); o.location = loc; o.rotation_euler = rot; o.data.materials.append(mat); return o

def _group(name, c, loc):
    g = bpy.data.objects.new(name, None); c.objects.link(g); g.location = loc; return g

def giraffe(name, c, loc, s=1.0):
    g = _group(name, c, loc)
    body = M("zo_gir", (0.98, 0.78, 0.35), 0.8); spot = M("zo_girspot", (0.62, 0.36, 0.14), 0.8); dark = M("zo_dark", (0.08, 0.06, 0.05), 0.4)
    ps = [sph(name + "_body", 0.45 * s, (0, 0, 1.55 * s), body, c, scale=(0.75, 1.25, 0.75), seg=18)]
    for lx in (-0.22, 0.22):
        for ly in (-0.35, 0.35): ps.append(cyl(name + f"_leg{lx}{ly}", 0.06 * s, 1.3 * s, (lx * s, ly * s, 0.65 * s), body, c, 10))
    neck = cyl(name + "_neck", 0.1 * s, 1.35 * s, (0, -0.62 * s, 2.4 * s), body, c, 12, rot=(math.radians(18), 0, 0)); ps.append(neck)
    ps.append(sph(name + "_head", 0.2 * s, (0, -0.8 * s, 3.05 * s), body, c, scale=(0.8, 1.4, 0.8), seg=14))
    for sx in (-0.07, 0.07):
        ps.append(cyl(name + f"_oss{sx}", 0.02 * s, 0.18 * s, (sx * s, -0.72 * s, 3.25 * s), dark, c, 6))
        ps.append(sph(name + f"_eye{sx}", 0.035 * s, (sx * 2.0 * s, -0.95 * s, 3.1 * s), dark, c, seg=8))
    rnd = random.Random(hash(name) & 0xff)
    for i in range(14): ps.append(sph(name + f"_sp{i}", 0.09 * s, (rnd.choice([-0.33, 0.33]) * s, rnd.uniform(-0.45, 0.45) * s, rnd.uniform(1.4, 1.75) * s), spot, c, scale=(0.3, 1, 1), seg=8))
    for p_ in ps: p_.parent = g
    return g

def elephant(name, c, loc, s=1.0):
    g = _group(name, c, loc)
    grey = M("zo_ele", (0.55, 0.58, 0.64), 0.75, bump=0.4, bump_scale=30); dark = M("zo_dark", (0.08, 0.06, 0.05), 0.4)
    ps = [sph(name + "_body", 0.7 * s, (0, 0, 1.05 * s), grey, c, scale=(1.0, 1.35, 0.9), seg=20)]
    for lx in (-0.38, 0.38):
        for ly in (-0.5, 0.5): ps.append(cyl(name + f"_leg{lx}{ly}", 0.17 * s, 0.7 * s, (lx * s, ly * s, 0.35 * s), grey, c, 14))
    head = sph(name + "_head", 0.45 * s, (0, -1.0 * s, 1.35 * s), grey, c, seg=18); ps.append(head)
    for sx in (-1, 1):
        ps.append(sph(name + f"_ear{sx}", 0.42 * s, (sx * 0.45 * s, -0.85 * s, 1.4 * s), M("zo_ear", (0.6, 0.55, 0.62), 0.8), c, scale=(0.15, 1.0, 1.1), seg=14))
        ps.append(sph(name + f"_eye{sx}", 0.05 * s, (sx * 0.2 * s, -1.38 * s, 1.5 * s), dark, c, seg=8))
    trunk = _group(name + "_trunk", c, (0, -1.35 * s, 1.15 * s)); trunk.parent = g
    for i in range(6):
        seg_ = cyl(name + f"_tr{i}", (0.13 - i * 0.012) * s, 0.16 * s, (0, -0.05 * i * s, -0.14 * i * s), grey, c, 12); seg_.parent = trunk
    for p_ in ps: p_.parent = g
    return g, trunk

def monkey(name, c, loc, s=1.0):
    g = _group(name, c, loc)
    fur = M("zo_monk", (0.45, 0.28, 0.14), 0.9, bump=0.5, bump_scale=60); face = M("zo_mface", (0.95, 0.78, 0.6), 0.6); dark = M("zo_dark", (0.08, 0.06, 0.05), 0.4)
    ps = [sph(name + "_body", 0.16 * s, (0, 0, 0.3 * s), fur, c, scale=(0.9, 0.8, 1.15), seg=14), sph(name + "_head", 0.13 * s, (0, -0.02 * s, 0.56 * s), fur, c, seg=14),
          sph(name + "_face", 0.09 * s, (0, -0.1 * s, 0.54 * s), face, c, scale=(1.1, 0.6, 0.9), seg=12)]
    for sx in (-1, 1):
        ps.append(sph(name + f"_ear{sx}", 0.05 * s, (sx * 0.14 * s, -0.01 * s, 0.6 * s), face, c, scale=(0.5, 1, 1), seg=8))
        ps.append(sph(name + f"_eye{sx}", 0.02 * s, (sx * 0.035 * s, -0.17 * s, 0.58 * s), dark, c, seg=6))
        ps.append(cyl(name + f"_arm{sx}", 0.035 * s, 0.32 * s, (sx * 0.17 * s, 0, 0.26 * s), fur, c, 8, rot=(0, sx * 0.4, 0)))
        ps.append(cyl(name + f"_leg{sx}", 0.04 * s, 0.22 * s, (sx * 0.08 * s, 0, 0.08 * s), fur, c, 8))
    ps.append(cyl(name + "_tail", 0.02 * s, 0.4 * s, (0, 0.18 * s, 0.35 * s), fur, c, 6, rot=(math.radians(-35), 0, 0)))
    for p_ in ps: p_.parent = g
    return g

def penguin(name, c, loc, s=1.0):
    g = _group(name, c, loc)
    blk = M("zo_peng", (0.06, 0.07, 0.1), 0.4); wht = M("zo_pwhite", (0.97, 0.97, 0.97), 0.5); org = M("zo_porange", (1.0, 0.55, 0.05), 0.5)
    ps = [sph(name + "_body", 0.17 * s, (0, 0, 0.24 * s), blk, c, scale=(0.95, 0.85, 1.4), seg=16),
          sph(name + "_belly", 0.13 * s, (0, -0.06 * s, 0.22 * s), wht, c, scale=(0.9, 0.6, 1.3), seg=14),
          sph(name + "_head", 0.11 * s, (0, 0, 0.5 * s), blk, c, seg=14),
          _cone(name + "_beak", 0.035 * s, 0.0, 0.08 * s, (0, -0.13 * s, 0.49 * s), org, c, rot=(math.radians(90), 0, 0), verts=10)]
    for sx in (-1, 1):
        ps.append(sph(name + f"_eye{sx}", 0.03 * s, (sx * 0.045 * s, -0.09 * s, 0.53 * s), wht, c, seg=8))
        ps.append(sph(name + f"_pup{sx}", 0.015 * s, (sx * 0.045 * s, -0.115 * s, 0.53 * s), blk, c, seg=6))
        ps.append(sph(name + f"_wing{sx}", 0.1 * s, (sx * 0.17 * s, 0, 0.26 * s), blk, c, scale=(0.25, 0.6, 1.2), seg=10))
        ps.append(sph(name + f"_foot{sx}", 0.05 * s, (sx * 0.06 * s, -0.05 * s, 0.015 * s), org, c, scale=(1, 1.5, 0.3), seg=8))
    for p_ in ps: p_.parent = g
    return g

def build_zoo(O=Vector((3100, 0, 0))):
    sn = "zoo"; c = col(sn); rnd = random.Random(13)
    grass = M("zo_grass", (0.36, 0.64, 0.22), 0.9, bump=0.8, bump_scale=22)
    pathm = M_tiles("zo_path", (0.86, 0.78, 0.62), (0.8, 0.72, 0.56), (0.62, 0.55, 0.45), 2.4, 0.85)
    sand = M("zo_sand", (0.9, 0.8, 0.55), 0.95, bump=0.5, bump_scale=40)
    wood = M_wood("zo_wood", (0.6, 0.4, 0.22), (0.48, 0.3, 0.15), scale=3)
    fence = M("zo_fence", (0.25, 0.45, 0.3), 0.6)
    water = M("zo_water", (0.25, 0.6, 0.85), 0.05, coat=1.0)
    cyl(sn + "_ground", 70, 0.2, (O.x, O.y + 8, -0.1), grass, c, 96, bevel=0)
    box(sn + "_plaza", (8.0, 4.0, 0.02), (O.x, O.y - 1.6, 0.01), pathm, c, 0)
    for i, (x, y, r, h) in enumerate([(-16, 26, 13, 4.5), (6, 34, 17, 6.0), (24, 22, 12, 4.0)]):
        sph(sn + f"_hill{i}", r, (O.x + x, O.y + y, -r + h), M("zo_hill", (0.32, 0.56, 0.22), 0.9, bump=0.5, bump_scale=8), c, seg=40, scale=(1.6, 1.0, 1.0))
    skym = sets2.M_sky_window("zo_skym", top=(0.28, 0.56, 1.0), bottom=(0.88, 0.93, 1.0), strength=2.6, trees=False)
    plane(sn + "_sky", (400, 160), (O.x, O.y + 120, 40), skym, c, rot=(math.radians(90), 0, 0))
    plane(sn + "_skyl", (300, 160), (O.x - 120, O.y + 30, 40), skym, c, rot=(math.radians(90), 0, math.radians(90)))
    plane(sn + "_skyr", (300, 160), (O.x + 120, O.y + 30, 40), skym, c, rot=(math.radians(90), 0, math.radians(90)))
    sph(sn + "_sunball", 4.0, (O.x - 35, O.y + 110, 44.0), M("zo_sun", (1, 1, 0.9), 0.5, emit=(1.0, 0.95, 0.8), emit_str=14.0), c)
    cloudm = M("zo_cloud", (1, 1, 1), 0.9, emit=(1, 1, 1), emit_str=0.9)
    for i in range(6):
        g = _group(sn + f"_cloud{i}", c, (O.x + rnd.uniform(-80, 80), O.y + rnd.uniform(60, 110), rnd.uniform(16, 30)))
        for j in range(5):
            s_ = sph(sn + f"_cl{i}_{j}", rnd.uniform(2.5, 5.0), (rnd.uniform(-5, 5), rnd.uniform(-2, 2), rnd.uniform(-1, 1.5)), cloudm, c, seg=12, scale=(1.4, 1.0, 0.7)); s_.parent = g
    # ---- entrance arch (front-left, seen in the cold open) ----
    AX, AY = O.x - 3.0, O.y - 3.4
    archm = M("zo_arch", (0.95, 0.55, 0.15), 0.5)
    for sx in (-1.1, 1.1): cyl(sn + f"_apost{sx}", 0.12, 2.8, (AX + sx, AY, 1.4), archm, c, 16)
    box(sn + "_asign", (2.6, 0.12, 0.6), (AX, AY, 2.75), M("zo_asign", (0.2, 0.55, 0.3), 0.5), c, 0.04)
    _text(sn + "_atext", "BRO BROS ZOO", (AX, AY - 0.08, 2.75), 0.32, M("zo_atext", (1, 0.95, 0.4), 0.4, emit=(1, 0.9, 0.3), emit_str=0.6), c)
    # ---- GIRAFFE paddock (back-left) ----
    GX, GY = O.x - 2.6, O.y + 2.4
    cyl(sn + "_gsand", 2.0, 0.02, (GX, GY, 0.012), sand, c, 40, bevel=0)
    for i in range(16):
        a = math.pi * (0.9 + i / 15 * 1.2); cyl(sn + f"_gf{i}", 0.04, 1.0, (GX + math.cos(a) * 2.0, GY + math.sin(a) * 1.2 - 0.2, 0.5), wood, c, 8)
    box(sn + "_gfrail", (3.8, 0.05, 0.08), (GX, GY - 1.35, 0.85), wood, c, 0.01)
    gir = giraffe(sn + "_giraffe", c, (GX + 0.2, GY + 0.6, 0), 1.0); gir.rotation_euler = (0, 0, math.radians(-20))
    acacia = sets_park.tree(sn + "_acacia", (GX - 2.2, GY + 2.6, 0), c, 4.6, 1.6, 0, seed=31)
    # ---- ELEPHANT pool (back-centre-right) ----
    EX, EY = O.x + 0.9, O.y + 3.0
    cyl(sn + "_epool", 1.4, 0.03, (EX - 0.6, EY - 0.4, 0.015), water, c, 40, bevel=0)
    box(sn + "_ewall", (4.0, 0.3, 0.55), (EX, EY - 1.6, 0.27), M("zo_stone", (0.7, 0.66, 0.6), 0.85, bump=0.6, bump_scale=12), c, 0.05)
    ele, trunk = elephant(sn + "_elephant", c, (EX + 0.6, EY + 0.3, 0), 1.0); ele.rotation_euler = (0, 0, math.radians(15))
    # ---- MONKEY island (right) ----
    MX, MY = O.x + 3.4, O.y + 0.9
    cyl(sn + "_mmoat", 1.6, 0.02, (MX, MY, 0.01), water, c, 40, bevel=0)
    cyl(sn + "_misland", 1.15, 0.25, (MX, MY, 0.12), M("zo_rock", (0.55, 0.5, 0.44), 0.9, bump=0.7, bump_scale=10), c, 30)
    for sx in (-0.5, 0.5): cyl(sn + f"_mpole{sx}", 0.05, 1.8, (MX + sx, MY + 0.2, 1.1), wood, c, 10)
    cyl(sn + "_mbar", 0.04, 1.1, (MX, MY + 0.2, 1.9), wood, c, 10, rot=(0, math.radians(90), 0))
    rope = M("zo_rope", (0.85, 0.75, 0.55), 0.9)
    for sx in (-0.25, 0.25): cyl(sn + f"_mrope{sx}", 0.012, 0.8, (MX + sx, MY + 0.2, 1.5), rope, c, 6)
    monkeys = [monkey(sn + f"_monkey{i}", c, (MX + x, MY + y, z), 1.0) for i, (x, y, z) in enumerate([(-0.3, -0.3, 0.25), (0.35, -0.1, 0.25), (0.0, 0.2, 1.95)])]
    sets_park.tree(sn + "_palm", (MX + 0.7, MY + 0.8, 0), c, 3.6, 1.0, 1, seed=44)
    # ---- PENGUIN pool (front-right) ----
    PX, PY = O.x + 2.4, O.y - 1.6
    box(sn + "_ppoolrim", (2.2, 1.4, 0.3), (PX, PY, 0.15), M("zo_ice", (0.85, 0.93, 1.0), 0.2, coat=0.6), c, 0.06)
    box(sn + "_ppool", (1.8, 1.0, 0.02), (PX, PY, 0.31), M("zo_pwater", (0.3, 0.7, 0.95), 0.05, coat=1.0), c, 0)
    for i, (x, y) in enumerate([(-0.5, 0.2), (0.4, -0.15)]): box(sn + f"_iceb{i}", (0.35, 0.3, 0.2), (PX + x, PY + y, 0.4), M("zo_iceb", (0.9, 0.97, 1.0), 0.15, coat=0.8), c, 0.04)
    penguins = [penguin(sn + f"_penguin{i}", c, (PX - 0.9 + i * 0.35, PY - 0.95, 0.0), 1.0) for i in range(4)]
    # ---- ice-cream cart, benches, signposts, balloons ----
    CX, CY = O.x - 0.9, O.y + 0.9
    box(sn + "_cart", (1.0, 0.6, 0.7), (CX, CY, 0.55), M("zo_cart", (0.98, 0.6, 0.75), 0.4, coat=0.5), c, 0.05)
    for sx in (-0.35, 0.35): cyl(sn + f"_cwheel{sx}", 0.18, 0.06, (CX + sx, CY - 0.31, 0.18), M("zo_wheel", (0.2, 0.2, 0.22), 0.5), c, 20, rot=(math.radians(90), 0, 0))
    _cone(sn + "_cumb", 0.75, 0.0, 0.35, (CX, CY, 1.75), M("zo_umb", (1.0, 0.85, 0.2), 0.5), c, verts=12)
    cyl(sn + "_cumbpole", 0.025, 0.9, (CX, CY, 1.35), M("zo_pole", (0.95, 0.95, 0.95), 0.4), c, 8)
    for i, cc in enumerate([(1, 0.6, 0.75), (0.6, 0.4, 0.25), (0.6, 0.9, 0.6)]): sph(sn + f"_scoop{i}", 0.07, (CX - 0.3 + i * 0.3, CY - 0.15, 0.95), M(f"zo_sc{i}", cc, 0.5), c, seg=10)
    for i, (x, y, r) in enumerate([(-4.2, -0.6, 90), (4.4, -2.4, -90)]):
        b = box(sn + f"_bench{i}", (1.2, 0.4, 0.06), (O.x + x, O.y + y, 0.45), wood, c, 0.01, rot=(0, 0, math.radians(r)))
    for i, (x, y, txt) in enumerate([(-1.4, 1.2, "GIRAFFE"), (0.2, 1.9, "ELEPHANT"), (2.1, 0.0, "MONKEYS"), (3.7, -2.6, "PENGUINS")]):
        cyl(sn + f"_spost{i}", 0.03, 1.2, (O.x + x, O.y + y, 0.6), wood, c, 8)
        box(sn + f"_sboard{i}", (0.7, 0.04, 0.22), (O.x + x, O.y + y - 0.02, 1.15), M("zo_sb", (0.95, 0.92, 0.8), 0.6), c, 0.01)
        _text(sn + f"_stxt{i}", txt, (O.x + x, O.y + y - 0.05, 1.15), 0.1, M("zo_stx", (0.15, 0.3, 0.2), 0.5), c)
    for i in range(30):
        a = rnd.uniform(0.15 * math.pi, 0.85 * math.pi); r = rnd.uniform(6.0, 10.0)
        sph(sn + f"_bush{i}", rnd.uniform(0.3, 0.6), (O.x + math.cos(a) * r, O.y + math.sin(a) * r * 0.6 + 3, 0.2), M(f"zo_bush{i % 2}", [(0.25, 0.5, 0.18), (0.3, 0.58, 0.2)][i % 2], 0.85), c, seg=12, scale=(1.2, 1, 0.8))
    # ---- lights: bright midday ----
    sun = bpy.data.objects.new(sn + "_sunlight", bpy.data.lights.new(sn + "_sunlight", "SUN")); c.objects.link(sun)
    sun.data.energy = 4.6; sun.data.color = (1.0, 0.95, 0.85); sun.data.angle = math.radians(2.5); sun.location = (O.x, O.y, 10)
    sun.rotation_euler = (math.radians(45), 0, math.radians(-30))
    area(sn + "_skyfill", (O.x, O.y - 4, 6.0), (O.x, O.y + 2, 0.5), 600, 8.0, c, (0.75, 0.85, 1.0))
    area(sn + "_front", (O.x + 1.5, O.y - 5.0, 2.5), (O.x, O.y + 1.0, 0.9), 350, 4.0, c, (1.0, 0.95, 0.9))
    SETS[sn] = dict(origin=O, coll=c, giraffe=gir, elephant=ele, trunk=trunk, monkeys=monkeys, penguins=penguins, cart=(CX, CY),
                    gir_xy=(GX, GY), ele_xy=(EX, EY), monk_xy=(MX, MY), peng_xy=(PX, PY), arch=(AX, AY),
                    cams={"zoo_wide": ((O.x + 0.0, O.y - 5.4, 1.7), (O.x + 0.0, O.y + 1.4, 1.1), 22),
                          "low_wide": ((O.x - 1.0, O.y - 5.0, 0.5), (O.x + 0.2, O.y + 1.4, 1.3), 20),
                          "high_wide": ((O.x + 0.0, O.y - 6.0, 3.6), (O.x, O.y + 1.0, 0.4), 22),
                          "insert:arch": ((AX + 0.8, AY - 3.2, 1.6), (AX, AY, 1.8), 24),
                          "insert:giraffe": ((GX + 1.6, GY - 2.4, 2.0), (GX + 0.2, GY + 0.4, 2.4), 26),
                          "insert:elephant": ((EX - 0.2, EY - 3.4, 1.3), (EX + 0.5, EY + 0.1, 1.2), 26),
                          "insert:monkeys": ((MX - 1.6, MY - 2.6, 1.2), (MX, MY, 0.8), 28),
                          "insert:penguins": ((PX - 0.4, PY - 2.9, 1.3), (PX - 0.4, PY - 0.9, 0.3), 28),
                          "insert:cart": ((CX + 0.8, CY - 2.2, 1.1), (CX, CY, 0.8), 30)})
    return SETS[sn]

sets2.build_zoo = build_zoo
