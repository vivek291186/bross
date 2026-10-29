# Song 04: bright kids' BATHROOM (origin x=1500): aqua/white tiles, long counter with 3 sinks + big mirror,
# 5 colourful toothbrushes in cups, giant toothpaste tube, bathtub full of bubbles + rubber duck, towels on hooks,
# round window with morning sky, bath mat, step stool, floating soap bubbles. Song-friendly: kids dance in front.
import bpy, math, random
from mathutils import Vector
import sets2, sets_beach
from sets2 import SETS, M, M_tiles, box, cyl, sph, plane, area, col, point

def toothbrush(name, loc, colr, coll, rot=(0, 0, 0), s=1.0):
    g = bpy.data.objects.new(name, None); coll.objects.link(g); g.location = loc; g.rotation_euler = rot
    h = cyl(name + "_h", 0.011 * s, 0.17 * s, (0, 0, 0.085 * s), M(name + "_hm", colr, 0.35, coat=0.6), coll, 12); h.parent = g
    b = box(name + "_head", (0.02 * s, 0.014 * s, 0.035 * s), (0, 0, 0.185 * s), M("tb_head", (0.95, 0.95, 0.97), 0.4), coll, 0.004); b.parent = g
    br = box(name + "_bristle", (0.018 * s, 0.018 * s, 0.03 * s), (0, 0.014 * s, 0.185 * s), M(name + "_bm", (0.45, 0.85, 1.0), 0.7), coll, 0.003); br.parent = g
    return g

def build_bathroom(O=Vector((1500, 0, 0))):
    sn = "bathroom"; c = col(sn); rnd = random.Random(4)
    tileW = M_tiles("bt_wall", (0.62, 0.86, 0.88), (0.56, 0.80, 0.84), (0.95, 0.97, 0.97), 7.0, 0.18)
    tileW2 = M_tiles("bt_wall2", (0.97, 0.97, 0.95), (0.93, 0.93, 0.92), (0.75, 0.82, 0.84), 7.0, 0.18)
    floor = M_tiles("bt_floor", (0.95, 0.95, 0.93), (0.35, 0.62, 0.78), (0.8, 0.8, 0.8), 3.0, 0.2)
    ceil = M("bt_ceil", (0.98, 0.98, 0.97), 0.9)
    white = M("bt_white", (0.97, 0.97, 0.96), 0.15, coat=1.0)
    chrome = M("bt_chrome", (0.9, 0.9, 0.92), 0.08, 1.0)
    counter = M("bt_counter", (0.98, 0.78, 0.35), 0.35, coat=0.5)
    W, D, H = 7.0, 5.0, 2.8
    box(sn + "_floor", (W, D + 6, 0.1), (O.x, O.y, -0.05), floor, c, 0)
    box(sn + "_ceil", (W, D + 6, 0.1), (O.x, O.y, H + 0.05), ceil, c, 0)
    # walls: lower aqua tiles, upper white tiles
    for nm, size, loc in (("_back", (W, 0.12, H), (O.x, O.y + 2.4, H / 2)), ("_left", (0.12, D + 6, H), (O.x - W / 2, O.y, H / 2)),
                          ("_right", (0.12, D + 6, H), (O.x + W / 2, O.y, H / 2)), ("_front", (W, 0.12, H), (O.x, O.y - 5.5, H / 2))):
        box(sn + nm, size, loc, tileW2, c, 0)
    box(sn + "_backlow", (W, 0.02, 1.2), (O.x, O.y + 2.33, 0.6), tileW, c, 0)
    box(sn + "_leftlow", (0.02, D + 6, 1.2), (O.x - W / 2 + 0.07, O.y, 0.6), tileW, c, 0)
    box(sn + "_rightlow", (0.02, D + 6, 1.2), (O.x + W / 2 - 0.07, O.y, 0.6), tileW, c, 0)
    box(sn + "_trim", (W, 0.04, 0.05), (O.x, O.y + 2.31, 1.22), M("bt_trim", (0.2, 0.5, 0.85), 0.3, coat=0.5), c, 0.01)
    # counter with 3 sinks along back wall (left half), big mirror above
    CX, CY = O.x - 1.0, O.y + 2.05
    box(sn + "_cab", (3.4, 0.55, 0.62), (CX, CY, 0.31), M("bt_cab", (0.35, 0.65, 0.95), 0.4, coat=0.4), c, 0.03)
    for i in range(4): box(sn + f"_door{i}", (0.78, 0.02, 0.5), (CX - 1.25 + i * 0.83, CY - 0.28, 0.31), M("bt_door", (0.45, 0.75, 1.0), 0.35, coat=0.5), c, 0.02)
    box(sn + "_top", (3.5, 0.6, 0.06), (CX, CY, 0.65), counter, c, 0.02)
    for i, x in enumerate((-1.1, 0.0, 1.1)):
        sph(sn + f"_sink{i}", 0.2, (CX + x, CY - 0.02, 0.66), white, c, scale=(1.2, 0.9, 0.35))
        cyl(sn + f"_tap{i}", 0.018, 0.18, (CX + x, CY + 0.2, 0.76), chrome, c, 16)
        box(sn + f"_spout{i}", (0.03, 0.12, 0.03), (CX + x, CY + 0.14, 0.85), chrome, c, 0.012)
    box(sn + "_mirrorframe", (3.3, 0.04, 1.05), (CX, O.y + 2.32, 1.62), M("bt_mframe", (0.98, 0.55, 0.3), 0.3, coat=0.5), c, 0.04)
    box(sn + "_mirror", (3.15, 0.02, 0.92), (CX, O.y + 2.29, 1.62), M("bt_mirror", (0.95, 0.97, 1.0), 0.02, 1.0), c, 0.005)
    for i in range(6): sph(sn + f"_bulb{i}", 0.045, (CX - 1.45 + i * 0.58, O.y + 2.27, 2.2), M("bt_bulb", (1, 0.95, 0.8), 0.3, emit=(1, 0.9, 0.7), emit_str=6.0), c)
    # toothbrush cups + 5 toothbrushes (kid colours) + giant toothpaste tube
    kidc = [(0.95, 0.3, 0.55), (0.25, 0.75, 0.95), (1.0, 0.82, 0.2), (0.65, 0.4, 0.95), (0.35, 0.85, 0.45)]
    brushes = []
    for i, cc in enumerate(kidc):
        x = CX - 1.45 + i * 0.22 if i < 3 else CX + 0.55 + (i - 3) * 0.22
        cyl(sn + f"_cup{i}", 0.04, 0.1, (x, CY + 0.12, 0.73), M(f"bt_cup{i}", cc, 0.3, coat=0.6), c, 20)
        brushes.append(toothbrush(sn + f"_brush{i}", (x, CY + 0.12, 0.7), cc, c, rot=(0.25, 0.15 * (i - 2), 0)))
    tube = bpy.data.objects.new(sn + "_tube", None); c.objects.link(tube); tube.location = (CX + 1.55, CY - 0.05, 0.74); tube.rotation_euler = (0, math.radians(90), math.radians(15))
    t1 = cyl(sn + "_tubeb", 0.06, 0.32, (0, 0, 0), M("bt_tube", (0.95, 0.95, 0.97), 0.3), c, 24); t1.parent = tube; t1.scale = (1, 0.55, 1)
    t2 = cyl(sn + "_tubes", 0.065, 0.03, (0, 0, 0.0), M("bt_stripe", (0.9, 0.2, 0.25), 0.3), c, 24); t2.parent = tube; t2.scale = (1, 0.58, 1)
    t3 = cyl(sn + "_tubec", 0.03, 0.05, (0, 0, -0.18), M("bt_capb", (0.2, 0.5, 0.9), 0.3), c, 16); t3.parent = tube
    # soap dispenser + small plant
    cyl(sn + "_soap", 0.045, 0.14, (CX + 1.3, CY + 0.15, 0.75), M("bt_soap", (0.4, 0.85, 0.55), 0.15, coat=1.0), c, 20)
    sets2.plant("bt_plant", (CX - 1.6, CY + 0.12, 0.68), c, 0.35)
    # bathtub (right) with bubbles + rubber duck
    TX, TY = O.x + 2.15, O.y + 1.45
    box(sn + "_tub", (2.2, 1.0, 0.55), (TX, TY, 0.28), white, c, 0.12)
    box(sn + "_tubwater", (2.0, 0.82, 0.02), (TX, TY, 0.5), M("bt_water", (0.55, 0.85, 1.0), 0.05, emit=(0.5, 0.8, 1.0), emit_str=0.3, coat=1.0), c, 0.01)
    foam = M("bt_foam", (0.99, 0.99, 1.0), 0.5, emit=(1, 1, 1), emit_str=0.15)
    for i in range(46):
        r_ = rnd.uniform(0.06, 0.15); sph(sn + f"_foam{i}", r_, (TX + rnd.uniform(-0.95, 0.95), TY + rnd.uniform(-0.38, 0.38), 0.52 + rnd.uniform(0, 0.12)), foam, c, seg=12)
    duck = bpy.data.objects.new(sn + "_duck", None); c.objects.link(duck); duck.location = (TX - 0.5, TY - 0.25, 0.62)
    yel = M("bt_duck", (1.0, 0.85, 0.1), 0.35, coat=0.6)
    d1 = sph(sn + "_duckb", 0.09, (0, 0, 0), yel, c, scale=(1.3, 1, 0.8)); d1.parent = duck
    d2 = sph(sn + "_duckh", 0.06, (-0.08, 0, 0.09), yel, c); d2.parent = duck
    d3 = sph(sn + "_duckbeak", 0.03, (-0.14, 0, 0.085), M("bt_beak", (1, 0.45, 0.1), 0.4), c, scale=(1.4, 1, 0.5)); d3.parent = duck
    for sy in (-1, 1): e_ = sph(sn + f"_ducke{sy}", 0.012, (-0.12, sy * 0.03, 0.11), M("eye_black", (0.02, 0.02, 0.02), 0.2), c); e_.parent = duck
    for f in range(1, 8001, 8):
        duck.location.z = 0.62 + 0.015 * math.sin(f / 9.0); duck.rotation_euler = (0.06 * math.sin(f / 13.0), 0, 0.2 * math.sin(f / 40.0))
        duck.keyframe_insert("location", frame=f); duck.keyframe_insert("rotation_euler", frame=f)
    cyl(sn + "_tubtap", 0.025, 0.25, (TX + 1.0, TY + 0.35, 0.65), chrome, c, 16)
    # towels on hooks (left wall) + round window (right wall high) + bath mat + step stool
    for i, cc in enumerate(((0.95, 0.4, 0.5), (0.3, 0.7, 0.95), (1.0, 0.8, 0.3))):
        box(sn + f"_towel{i}", (0.06, 0.5, 0.75), (O.x - W / 2 + 0.12, O.y + 0.9 - i * 0.65, 1.15), M(f"bt_towel{i}", cc, 0.95, bump=0.5, bump_scale=300), c, 0.03)
        sph(sn + f"_hook{i}", 0.03, (O.x - W / 2 + 0.1, O.y + 0.9 - i * 0.65, 1.55), chrome, c)
    win = cyl(sn + "_win", 0.45, 0.05, (O.x + 1.0, O.y + 2.33, 2.05), sets2.M_sky_window("bt_sky", (0.45, 0.72, 1.0), (0.95, 0.95, 0.85), 3.5, trees=True), c, 40, rot=(math.radians(90), 0, 0))
    cyl(sn + "_winframe", 0.5, 0.04, (O.x + 1.0, O.y + 2.34, 2.05), M("bt_wf", (0.98, 0.98, 0.98), 0.3), c, 40, rot=(math.radians(90), 0, 0))
    box(sn + "_mat", (1.8, 0.9, 0.02), (O.x + 0.3, O.y + 0.3, 0.01), M_tiles("bt_matm", (0.95, 0.55, 0.3), (0.98, 0.7, 0.35), (1, 0.9, 0.6), 2.0, 0.95), c, 0.01)
    box(sn + "_stool", (0.45, 0.32, 0.22), (CX + 0.6, CY - 0.55, 0.11), M("bt_stool", (0.4, 0.85, 0.5), 0.35, coat=0.4), c, 0.04)
    # floating soap bubbles (iridescent), drifting up
    bub = M("bt_bubble", (0.85, 0.95, 1.0), 0.02, emit=(0.8, 0.9, 1.0), emit_str=0.2, alpha=0.35, coat=1.0)
    for i in range(18):
        b = sph(sn + f"_bub{i}", rnd.uniform(0.04, 0.09), (0, 0, 0), bub, c, seg=14)
        x0, y0, sp, ph = rnd.uniform(-3, 3), rnd.uniform(-1.0, 2.0), rnd.uniform(0.004, 0.009), rnd.uniform(0, 600)
        for f in range(1, 8001, 10):
            z = ((f + ph) * sp) % 2.4 + 0.3
            b.location = (O.x + x0 + 0.15 * math.sin((f + ph) / 40.0), O.y + y0, z); b.keyframe_insert("location", frame=f)
    # lights: bright morning
    area(sn + "_key", (O.x - 2.2, O.y - 3.4, 2.4), (O.x, O.y + 1.0, 0.9), 380, 2.5, c, (1, 0.95, 0.88))
    area(sn + "_fill", (O.x + 2.6, O.y - 3.0, 1.8), (O.x, O.y + 1.0, 0.9), 180, 3.0, c, (0.88, 0.95, 1.0))
    area(sn + "_top", (O.x, O.y + 0.6, H - 0.1), (O.x, O.y + 0.6, 0), 260, 2.2, c, (1, 0.98, 0.92))
    area(sn + "_win", (O.x + 1.0, O.y + 1.8, 2.1), (O.x, O.y, 0.6), 120, 0.8, c, (1, 0.95, 0.8))
    SETS[sn] = dict(origin=O, coll=c, brushes=brushes, duck=duck, tube=tube, sinks=[(CX + x, CY) for x in (-1.1, 0, 1.1)],
                    cams={"bath_wide": ((O.x + 0.0, O.y - 4.0, 1.45), (O.x + 0.0, O.y + 1.2, 1.0), 26),
                          "low_wide": ((O.x - 1.2, O.y - 4.2, 0.6), (O.x + 0.2, O.y + 1.2, 1.1), 26),
                          "high_wide": ((O.x + 0.0, O.y - 4.3, 2.55), (O.x, O.y + 0.6, 0.7), 26),
                          "insert:sink": ((CX - 0.3, CY - 1.0, 1.05), (CX - 0.5, CY + 0.1, 0.75), 32),
                          "insert:tub": ((TX - 1.1, TY - 1.4, 1.1), (TX - 0.3, TY, 0.55), 32),
                          "insert:duck": ((TX - 0.9, TY - 0.9, 0.85), (TX - 0.5, TY - 0.25, 0.62), 45)})
    return SETS[sn]

sets2.build_bathroom = build_bathroom
