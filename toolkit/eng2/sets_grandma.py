# Ep 12: GRANDMA'S GARDEN (origin x=2900). Village cottage garden, very different from the Ep 9 suburban backyard:
# cream cottage with a red tiled roof, wooden porch + rocking chair and a glowing kitchen window (Grandma talks from there),
# a big MANGO TREE with hanging mangoes, vegetable beds with TOMATO plants (pickable), pumpkins and cabbages,
# a stone WELL with a little roof and a bucket, a funny SCARECROW, a MUD patch, a low stone boundary wall, hills behind.
import bpy, math, random
from mathutils import Vector
import sets2, sets_park
from sets2 import SETS, M, M_wood, M_tiles, box, cyl, sph, plane, area, col

def build_grandma(O=Vector((2900, 0, 0))):
    sn = "grandma"; c = col(sn); rnd = random.Random(12)
    grass = M("gm_grass", (0.38, 0.62, 0.22), 0.9, bump=0.8, bump_scale=22)
    dirtp = M("gm_path", (0.62, 0.48, 0.32), 0.95, bump=0.6, bump_scale=30)
    soil = M("gm_soil", (0.32, 0.2, 0.11), 0.95, bump=0.8, bump_scale=35)
    mud = M("gm_mud", (0.25, 0.15, 0.07), 0.4, bump=0.9, bump_scale=14, coat=0.15)
    stone = M("gm_stone", (0.66, 0.63, 0.58), 0.85, bump=0.7, bump_scale=12)
    wood = M_wood("gm_wood", (0.58, 0.38, 0.2), (0.45, 0.28, 0.14), scale=3)
    cyl(sn + "_ground", 70, 0.2, (O.x, O.y + 8, -0.1), grass, c, 96, bevel=0)
    # dirt path from front to the porch
    box(sn + "_path", (1.2, 5.0, 0.02), (O.x - 2.6, O.y - 0.2, 0.005), dirtp, c, 0.0)
    for i, (x, y, r, h) in enumerate([(-16, 26, 13, 4.5), (6, 32, 17, 6.0), (24, 22, 12, 4.0)]):
        sph(sn + f"_hill{i}", r, (O.x + x, O.y + y, -r + h), M("gm_hill", (0.32, 0.56, 0.22), 0.9, bump=0.5, bump_scale=8), c, seg=40, scale=(1.6, 1.0, 1.0))
    skym = sets2.M_sky_window("gm_skym", top=(0.3, 0.58, 1.0), bottom=(0.9, 0.93, 1.0), strength=2.6, trees=False)
    plane(sn + "_sky", (400, 160), (O.x, O.y + 120, 40), skym, c, rot=(math.radians(90), 0, 0))
    plane(sn + "_skyl", (300, 160), (O.x - 120, O.y + 30, 40), skym, c, rot=(math.radians(90), 0, math.radians(90)))
    plane(sn + "_skyr", (300, 160), (O.x + 120, O.y + 30, 40), skym, c, rot=(math.radians(90), 0, math.radians(90)))
    sph(sn + "_sunball", 4.0, (O.x + 40, O.y + 110, 42.0), M("gm_sun", (1, 1, 0.9), 0.5, emit=(1.0, 0.95, 0.8), emit_str=14.0), c)
    cloudm = M("gm_cloud", (1, 1, 1), 0.9, emit=(1, 1, 1), emit_str=0.9)
    for i in range(6):
        g = bpy.data.objects.new(sn + f"_cloud{i}", None); c.objects.link(g)
        g.location = (O.x + rnd.uniform(-80, 80), O.y + rnd.uniform(60, 110), rnd.uniform(16, 30))
        for j in range(5):
            s = sph(sn + f"_cl{i}_{j}", rnd.uniform(2.5, 5.0), (rnd.uniform(-5, 5), rnd.uniform(-2, 2), rnd.uniform(-1, 1.5)), cloudm, c, seg=12, scale=(1.4, 1.0, 0.7)); s.parent = g
    # ---- COTTAGE (back-left) ----
    HX, HY = O.x - 2.6, O.y + 4.2
    wallm = M("gm_cwall", (0.96, 0.9, 0.76), 0.85, bump=0.2, bump_scale=60)
    box(sn + "_cottage", (4.4, 2.6, 2.4), (HX, HY + 1.0, 1.2), wallm, c, 0.02)
    roofm = M_tiles("gm_roof", (0.78, 0.26, 0.18), (0.68, 0.2, 0.14), (0.5, 0.15, 0.1), 6.0, 0.9)
    for sy in (-1, 1):
        box(sn + f"_roof{sy}", (4.9, 1.75, 0.1), (HX, HY + 1.0 + sy * 0.68, 2.85), roofm, c, 0.01, rot=(math.radians(sy * -38), 0, 0))
    box(sn + "_chimney", (0.35, 0.35, 0.9), (HX + 1.4, HY + 1.4, 3.3), M("gm_brick", (0.7, 0.35, 0.25), 0.8), c, 0.01)
    box(sn + "_door", (0.9, 0.06, 1.8), (HX - 0.0, HY - 0.32, 0.9), M_wood("gm_doorw", (0.35, 0.55, 0.45), (0.3, 0.48, 0.4), scale=3), c, 0.01)
    sph(sn + "_knob", 0.04, (HX + 0.3, HY - 0.37, 0.9), M("gm_knob", (0.9, 0.7, 0.2), 0.3, 0.8), c, seg=8)
    winm = M("gm_win", (1.0, 0.85, 0.55), 0.3, emit=(1.0, 0.82, 0.5), emit_str=2.5)
    win = box(sn + "_window", (1.0, 0.04, 0.8), (HX + 1.35, HY - 0.31, 1.45), winm, c, 0)
    for nm_, sz, lc in (("t", (1.12, 0.08, 0.07), (0, 0.42)), ("b", (1.2, 0.14, 0.07), (0, -0.42)), ("l", (0.07, 0.08, 0.9), (-0.53, 0)), ("r", (0.07, 0.08, 0.9), (0.53, 0)), ("m", (0.05, 0.06, 0.8), (0, 0))):
        box(sn + "_wf" + nm_, sz, (HX + 1.35 + lc[0], HY - 0.34, 1.45 + lc[1]), M("gm_wframe", (0.98, 0.98, 0.98), 0.4), c, 0.01)
    for i in range(5): sph(sn + f"_wpf{i}", 0.07, (HX + 1.0 + i * 0.18, HY - 0.42, 1.06), M(f"gm_wpf{i % 3}", [(0.95, 0.25, 0.35), (1.0, 0.8, 0.2), (0.95, 0.5, 0.85)][i % 3], 0.5), c, seg=10)
    # porch + rocking chair
    box(sn + "_porch", (3.2, 1.2, 0.12), (HX - 0.2, HY - 0.9, 0.06), wood, c, 0.01)
    for sx in (-1.7, 1.3): cyl(sn + f"_ppost{sx}", 0.06, 2.2, (HX + sx, HY - 1.4, 1.1), wood, c, 12)
    box(sn + "_proof", (3.6, 1.4, 0.08), (HX - 0.2, HY - 0.85, 2.25), roofm, c, 0.01, rot=(math.radians(12), 0, 0))
    rc = bpy.data.objects.new(sn + "_rocker", None); c.objects.link(rc); rc.location = (HX - 1.1, HY - 0.9, 0.12)
    for p_ in [box(sn + "_rseat", (0.5, 0.45, 0.05), (0, 0, 0.42), wood, c, 0.01), box(sn + "_rback", (0.5, 0.05, 0.6), (0, 0.22, 0.75), wood, c, 0.01),
               box(sn + "_rcush", (0.45, 0.4, 0.06), (0, 0, 0.47), M("gm_cush", (0.85, 0.3, 0.35), 0.8), c, 0.02)]:
        p_.parent = rc
    for sx in (-0.22, 0.22):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.35, minor_radius=0.02, location=(sx, 0, 0.32), rotation=(0, math.radians(90), 0))
        t_ = bpy.context.active_object; t_.name = sn + f"_rock{sx}"
        for cc in list(t_.users_collection): cc.objects.unlink(t_)
        c.objects.link(t_); t_.data.materials.append(wood); t_.parent = rc
        for lg in (-0.18, 0.18): l_ = box(sn + f"_rleg{sx}{lg}", (0.04, 0.04, 0.38), (sx, lg, 0.2), wood, c, 0.005); l_.parent = rc
    for f, a in ((1, 0.08), (36, -0.08), (72, 0.08)):
        rc.rotation_euler = (a, 0, 0); rc.keyframe_insert("rotation_euler", frame=f)
    try:
        for fc in rc.animation_data.action.fcurves: fc.modifiers.new("CYCLES")
    except Exception: pass
    # ---- MANGO TREE (right) ----
    trees = [sets_park.tree(sn + "_mango", (O.x + 3.6, O.y + 2.8, 0), c, 4.4, 2.0, 0, seed=121)]
    mango_m = M("gm_mango", (1.0, 0.62, 0.1), 0.45, coat=0.4)
    mangoes = []
    for i in range(14):
        a = rnd.uniform(0, 2 * math.pi); r = rnd.uniform(0.6, 1.6)
        mangoes.append(sph(sn + f"_mangofr{i}", 0.09, (O.x + 3.6 + math.cos(a) * r, O.y + 2.8 + math.sin(a) * r * 0.6 - 0.6, rnd.uniform(2.4, 3.2)), mango_m, c, seg=12, scale=(0.8, 0.8, 1.15)))
    trees += [sets_park.tree(sn + f"_tree{i}", (O.x + x, O.y + y, 0), c, h, r, i + 1, seed=i + 130) for i, (x, y, h, r) in enumerate([(9.0, 8.0, 3.8, 1.4), (-9.5, 9.0, 3.6, 1.3)])]
    # ---- VEGETABLE BEDS (centre back) with tomato plants ----
    VX, VY = O.x + 0.4, O.y + 2.0
    leaf = M("gm_leaf", (0.22, 0.52, 0.16), 0.8, bump=0.5, bump_scale=14)
    tom_m = M("gm_tomato", (0.92, 0.12, 0.08), 0.3, coat=0.8)
    tomatoes = []
    for row, dy in enumerate((0.0, 0.9)):
        box(sn + f"_bed{row}", (3.2, 0.6, 0.18), (VX, VY + dy, 0.09), soil, c, 0.03)
        for k in range(5):
            x = VX - 1.3 + k * 0.65
            if row == 0:
                cyl(sn + f"_stake{k}", 0.012, 0.9, (x, VY, 0.6), wood, c, 6)
                sph(sn + f"_tplant{k}", 0.24, (x, VY, 0.55), leaf, c, seg=12, scale=(1, 1, 1.4))
                for j in range(3):
                    tomatoes.append(sph(sn + f"_tom{k}_{j}", 0.055, (x + rnd.uniform(-0.17, 0.17), VY - 0.2, rnd.uniform(0.4, 0.75)), tom_m, c, seg=12))
            else:
                sph(sn + f"_cab{k}", 0.17, (x, VY + dy, 0.3), M("gm_cab", (0.55, 0.78, 0.35), 0.7, bump=0.6, bump_scale=30), c, seg=14, scale=(1, 1, 0.8))
    pump_m = M("gm_pump", (1.0, 0.5, 0.05), 0.5, bump=0.2, bump_scale=8)
    for i, (x, y) in enumerate([(2.2, 1.4), (2.5, 1.9)]):
        sph(sn + f"_pumpkin{i}", 0.26 - 0.06 * i, (O.x + x, O.y + y, 0.2 - 0.04 * i), pump_m, c, seg=20, scale=(1.2, 1.2, 0.85))
    # ---- MUD patch (front right of the beds) ----
    MX, MY = O.x + 1.6, O.y + 0.5
    cyl(sn + "_mud", 0.85, 0.02, (MX, MY, 0.012), mud, c, 40, bevel=0)
    # ---- WELL (front left) with bucket ----
    WX, WY = O.x - 3.2, O.y + 0.6
    cyl(sn + "_well", 0.55, 0.7, (WX, WY, 0.35), stone, c, 32)
    cyl(sn + "_wellwater", 0.47, 0.02, (WX, WY, 0.62), M("gm_water", (0.2, 0.4, 0.55), 0.05, coat=1.0), c, 32, bevel=0)
    for sx in (-0.5, 0.5): box(sn + f"_wpost{sx}", (0.08, 0.08, 1.2), (WX + sx, WY, 1.2), wood, c, 0.01)
    box(sn + "_wroofa", (1.3, 0.6, 0.06), (WX, WY - 0.22, 1.9), roofm, c, 0.01, rot=(math.radians(35), 0, 0))
    box(sn + "_wroofb", (1.3, 0.6, 0.06), (WX, WY + 0.22, 1.9), roofm, c, 0.01, rot=(math.radians(-35), 0, 0))
    cyl(sn + "_wcrank", 0.05, 1.0, (WX, WY, 1.4), wood, c, 12, rot=(0, math.radians(90), 0))
    bucket = bpy.data.objects.new(sn + "_bucket", None); c.objects.link(bucket); bucket.location = (WX + 0.75, WY - 0.3, 0)
    b1 = cyl(sn + "_bucketb", 0.16, 0.26, (0, 0, 0.13), M("gm_bucket", (0.45, 0.6, 0.85), 0.35, 0.4), c, 20); b1.parent = bucket
    # ---- SCARECROW (back right of the beds) ----
    SX, SY = O.x + 2.0, O.y + 3.4
    sc_ = bpy.data.objects.new(sn + "_scarecrow", None); c.objects.link(sc_); sc_.location = (SX, SY, 0)
    shirt = M("gm_shirt", (0.3, 0.45, 0.85), 0.9, bump=0.4, bump_scale=40); straw = M("gm_straw", (0.92, 0.78, 0.4), 0.95, bump=0.6, bump_scale=60)
    parts = [cyl(sn + "_scpole", 0.04, 1.9, (0, 0, 0.95), wood, c, 8), cyl(sn + "_scarm", 0.035, 1.4, (0, 0, 1.35), wood, c, 8, rot=(0, math.radians(90), 0)),
             box(sn + "_scshirt", (0.55, 0.22, 0.55), (0, 0, 1.2), shirt, c, 0.05), box(sn + "_scsleeves", (1.2, 0.16, 0.16), (0, 0, 1.38), shirt, c, 0.04),
             box(sn + "_scpants", (0.45, 0.2, 0.4), (0, 0, 0.78), M("gm_pants", (0.55, 0.35, 0.2), 0.9), c, 0.04),
             sph(sn + "_schead", 0.2, (0, 0, 1.68), M("gm_sack", (0.9, 0.8, 0.6), 0.95, bump=0.5, bump_scale=60), c, seg=16),
             cyl(sn + "_schat", 0.34, 0.03, (0, 0, 1.84), straw, c, 24), cyl(sn + "_schattop", 0.16, 0.16, (0, 0, 1.93), straw, c, 20)]
    for sx in (-0.07, 0.07): parts.append(sph(sn + f"_sceye{sx}", 0.03, (sx, -0.18, 1.72), M("gm_btn", (0.1, 0.1, 0.1), 0.3), c, seg=8))
    parts.append(box(sn + "_scmouth", (0.12, 0.02, 0.015), (0, -0.19, 1.6), M("gm_btn", (0.1, 0.1, 0.1), 0.3), c, 0))
    for sx in (-1, 1):
        for j in range(3): parts.append(cyl(sn + f"_scstraw{sx}{j}", 0.012, 0.16, (sx * 0.64, -0.0, 1.38 - 0.05 + j * 0.05), straw, c, 6, rot=(0, math.radians(90 + sx * (j - 1) * 20), 0)))
    for p_ in parts: p_.parent = sc_
    # ---- low stone wall boundary + flowers + chicken coop ----
    for i in range(30):
        x = -7.5 + i * 0.52
        box(sn + f"_sw{i}", (0.5, 0.35, 0.45 + 0.08 * math.sin(i * 1.7)), (O.x + x, O.y + 6.8, 0.22), stone, c, 0.06)
    coop = box(sn + "_coop", (1.1, 0.8, 0.8), (O.x + 4.6, O.y + 0.4, 0.5), M_wood("gm_coopw", (0.75, 0.3, 0.2), (0.65, 0.25, 0.15), scale=4), c, 0.02)
    box(sn + "_cooproof", (1.3, 1.0, 0.06), (O.x + 4.6, O.y + 0.4, 0.95), roofm, c, 0.01, rot=(math.radians(10), 0, 0))
    box(sn + "_coopdoor", (0.3, 0.02, 0.35), (O.x + 4.3, O.y - 0.01, 0.3), M("gm_dark", (0.08, 0.05, 0.03), 0.9), c, 0)
    for i in range(60):
        a = rnd.uniform(0, 2 * math.pi); r = rnd.uniform(5.0, 9.0)
        sph(sn + f"_fl{i}", 0.045, (O.x + math.cos(a) * r, O.y + math.sin(a) * r * 0.7 + 2, 0.15), M(f"gm_fl{i % 4}", [(1, 0.3, 0.4), (1, 0.85, 0.2), (0.9, 0.5, 0.95), (1, 1, 1)][i % 4], 0.5), c, seg=8, scale=(1, 1, 0.6))
    # ---- lights: warm morning ----
    sun = bpy.data.objects.new(sn + "_sunlight", bpy.data.lights.new(sn + "_sunlight", "SUN")); c.objects.link(sun)
    sun.data.energy = 4.6; sun.data.color = (1.0, 0.93, 0.8); sun.data.angle = math.radians(2.5); sun.location = (O.x, O.y, 10)
    sun.rotation_euler = (math.radians(50), 0, math.radians(35))
    area(sn + "_skyfill", (O.x, O.y - 4, 6.0), (O.x, O.y + 2, 0.5), 600, 8.0, c, (0.75, 0.85, 1.0))
    area(sn + "_front", (O.x - 1.5, O.y - 5.0, 2.5), (O.x, O.y + 1.5, 0.9), 350, 4.0, c, (1.0, 0.95, 0.9))
    SETS[sn] = dict(origin=O, coll=c, trees=trees, mangoes=mangoes, tomatoes=tomatoes, mud=(MX, MY), well=(WX, WY), bucket=bucket,
                    scarecrow=sc_, coop=(O.x + 4.3, O.y - 0.05), window=win, rocker=rc,
                    cams={"grandma_wide": ((O.x + 0.0, O.y - 4.6, 1.5), (O.x + 0.0, O.y + 1.6, 1.0), 24),
                          "low_wide": ((O.x - 1.2, O.y - 4.4, 0.45), (O.x + 0.2, O.y + 1.6, 1.2), 22),
                          "high_wide": ((O.x + 0.0, O.y - 5.2, 3.2), (O.x, O.y + 1.2, 0.4), 24),
                          "insert:veg": ((VX - 0.4, VY - 2.2, 0.9), (VX, VY, 0.5), 32),
                          "insert:scarecrow": ((SX - 0.6, SY - 2.4, 1.5), (SX, SY, 1.4), 32),
                          "insert:well": ((WX + 1.4, WY - 2.0, 1.2), (WX, WY, 0.7), 30),
                          "insert:window": ((HX + 0.6, HY - 3.0, 1.5), (HX + 1.35, HY - 0.3, 1.45), 32),
                          "insert:coop": ((O.x + 3.0, O.y - 1.8, 0.7), (O.x + 4.4, O.y + 0.2, 0.4), 30),
                          "insert:tree": ((O.x + 2.6, O.y - 0.4, 1.4), (O.x + 3.6, O.y + 2.4, 2.8), 26)})
    return SETS[sn]

sets2.build_grandma = build_grandma
