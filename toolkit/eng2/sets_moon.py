# Ep5 "Fly to the Moon": a small lunar surface set (dream sequence) — grey cratered ground, black starry sky, Earth hanging above.
import bpy, math, random
from mathutils import Vector
import sets2
from sets2 import SETS, M, box, cyl, sph, plane, area, point, col

def build_moon(O=Vector((800, 0, 0))):
    sn = "moon"; c = col(sn)
    ground = M("moon_ground", (0.52, 0.52, 0.50), 0.95, bump=0.6, bump_scale=40)
    dark = M("moon_dark", (0.30, 0.30, 0.29), 0.95, bump=0.4, bump_scale=60)
    rim = M("moon_rim", (0.62, 0.62, 0.60), 0.9, bump=0.5, bump_scale=50)
    cyl(sn + "_ground", 60.0, 0.2, (O.x, O.y, -0.1), ground, c, 96, bevel=0)
    rnd = random.Random(11)
    # craters: dark floor disc + raised rim ring; keep the acting area (|x|<2.8, -2.5<y<2.2) clear
    craters = [(-4.2, 3.0, 0.9), (4.6, 2.4, 1.1), (-3.6, -3.4, 0.7), (3.9, -3.2, 0.8), (0.4, 5.0, 1.6), (-7.5, 6.0, 2.2), (8.0, 7.5, 2.6), (-1.5, 3.6, 0.45), (2.2, 4.0, 0.5)]
    for i, (x, y, r) in enumerate(craters):
        cyl(sn + f"_cr{i}", r, 0.06, (O.x + x, O.y + y, -0.02), dark, c, 32, bevel=0)
        for j in range(14):
            a = j / 14 * 2 * math.pi
            sph(sn + f"_crr{i}_{j}", r * 0.16, (O.x + x + math.cos(a) * r, O.y + y + math.sin(a) * r, 0.0), rim, c, seg=10, scale=(1.2, 1.2, 0.5))
    # scattered rocks
    for i in range(26):
        x = rnd.uniform(-14, 14); y = rnd.uniform(-6, 16)
        if abs(x) < 3.0 and -2.8 < y < 2.6: continue
        s = rnd.uniform(0.06, 0.3)
        sph(sn + f"_rock{i}", s, (O.x + x, O.y + y, s * 0.4), rim if i % 3 else dark, c, seg=8, scale=(1.0, rnd.uniform(0.6, 1.3), 0.7))
    # sky: black dome backdrop + stars + Earth
    skym = M("moon_sky", (0.0, 0.0, 0.01), 1.0, emit=(0.0, 0.0, 0.015), emit_str=1.0)
    plane(sn + "_sky", (300, 140), (O.x, O.y + 90, 30), skym, c, rot=(math.radians(90), 0, 0))
    plane(sn + "_skyl", (200, 140), (O.x - 90, O.y + 20, 30), skym, c, rot=(math.radians(90), 0, math.radians(90)))
    plane(sn + "_skyr", (200, 140), (O.x + 90, O.y + 20, 30), skym, c, rot=(math.radians(90), 0, math.radians(90)))
    starm = M("moon_star", (1, 1, 1), 0.5, emit=(1, 0.97, 0.9), emit_str=40.0)
    for i in range(140):
        sph(sn + f"_star{i}", rnd.uniform(0.05, 0.14), (O.x + rnd.uniform(-100, 100), O.y + 88, rnd.uniform(4, 70)), starm, c, seg=6)
    earthm = M("moon_earth", (0.25, 0.45, 0.95), 0.6, bump=0.35, bump_scale=6, emit=(0.22, 0.42, 0.9), emit_str=2.2)
    E = Vector((O.x + 9.0, O.y + 62.0, 24.0))
    sph(sn + "_earth", 7.0, E, earthm, c, seg=48)
    landm = M("moon_land", (0.3, 0.6, 0.25), 0.8, emit=(0.25, 0.55, 0.2), emit_str=2.2)
    cloudm = M("moon_cloud", (1, 1, 1), 0.9, emit=(1, 1, 1), emit_str=2.6)
    for i, (dx, dz, sx, sz) in enumerate([(-2.5, 1.5, 2.2, 1.6), (1.8, -0.8, 2.6, 2.0), (3.0, 3.2, 1.3, 1.1), (-3.6, -2.8, 1.5, 1.2)]):
        sph(sn + f"_land{i}", 1.0, (E.x + dx, E.y - 6.4, E.z + dz), landm, c, seg=16, scale=(sx, 0.6, sz))
    for i, (dx, dz, sx, sz) in enumerate([(-4.0, 0.2, 1.8, 0.5), (0.5, 3.8, 2.5, 0.6), (2.6, -3.5, 2.0, 0.5), (-1.0, -1.8, 1.2, 0.4), (4.2, 1.6, 1.2, 0.45)]):
        sph(sn + f"_cloud{i}", 1.0, (E.x + dx, E.y - 6.9, E.z + dz), cloudm, c, seg=12, scale=(sx, 0.5, sz))
    # lights: hard "sun" from the right/back, blue Earth-shine fill, soft top
    area(sn + "_sun", (O.x + 6.0, O.y + 4.0, 7.0), (O.x, O.y + 0.3, 0.8), 1400, 2.0, c, (1.0, 0.98, 0.92))
    area(sn + "_earthshine", (O.x - 3.0, O.y - 3.5, 3.0), (O.x, O.y + 0.4, 0.9), 220, 4.0, c, (0.55, 0.7, 1.0))
    area(sn + "_top", (O.x, O.y, 4.0), (O.x, O.y, 0), 120, 3.0, c, (0.9, 0.92, 1.0))
    SETS[sn] = dict(origin=O, coll=c, earth=E,
                    cams={"moon_wide": ((O.x + 0.0, O.y - 3.6, 1.3), (O.x, O.y + 0.8, 0.9), 28),
                          "low_wide": ((O.x - 0.5, O.y - 3.3, 0.45), (O.x, O.y + 0.9, 1.1), 24),
                          "insert:earth": ((O.x + 0.0, O.y + 0.2, 1.2), (E.x, E.y, E.z), 35),
                          "insert:screen": ((O.x + 1.2, O.y - 0.6, 1.25), (O.x + 2.1, O.y + 1.6, 1.25), 40),
                          "insert:footprint": ((O.x + 1.6, O.y - 1.2, 0.7), (O.x + 2.2, O.y - 0.4, 0.0), 40),
                          "insert:bite": ((O.x + 0.6, O.y - 0.9, 0.5), (O.x + 1.3, O.y + 0.1, 0.25), 40)})
    return SETS[sn]

sets2.build_moon = build_moon
