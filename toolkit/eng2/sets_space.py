# Song 05: colourful MOON BASE launch pad (origin x=1900). New look vs Ep5's grey moon: pastel lilac moon ground with candy craters,
# deep blue-purple starry sky with a big ringed planet + Earth, a giant red/white cartoon ROCKET on a launch pad (blasts off with
# flame + smoke), a glowing COUNTDOWN BOARD whose digits are driven by the song, landing lights, a flag, floating sparkly asteroids.
import bpy, math, random
from mathutils import Vector
import sets2
from sets2 import SETS, M, box, cyl, sph, plane, area, col, text

def build_space(O=Vector((1900, 0, 0))):
    sn = "space"; c = col(sn); rnd = random.Random(5)
    ground = M("sp_ground", (0.72, 0.66, 0.86), 0.85, bump=0.6, bump_scale=10)
    crater = M("sp_crater", (0.58, 0.52, 0.76), 0.9, bump=0.6, bump_scale=14)
    # ground disc + candy craters
    cyl(sn + "_ground", 60, 0.2, (O.x, O.y + 8, -0.1), ground, c, 96, bevel=0)
    for i in range(26):
        x, y = rnd.uniform(-9, 9), rnd.uniform(-3, 14)
        if abs(x) < 3.2 and -2.5 < y < 2.0: continue
        r = rnd.uniform(0.3, 1.2)
        o = cyl(sn + f"_cr{i}", r, 0.06, (O.x + x, O.y + y, 0.0), crater, c, 32, bevel=0.03); o.scale = (1, 0.8, 1)
        cyl(sn + f"_crr{i}", r * 1.12, 0.04, (O.x + x, O.y + y, 0.01), M("sp_rim", (0.8, 0.74, 0.92), 0.85), c, 32, bevel=0.02).scale = (1, 0.8, 1)
    for i in range(8):
        x, y, r = rnd.uniform(-14, 14), rnd.uniform(12, 30), rnd.uniform(2, 5)
        sph(sn + f"_hill{i}", r, (O.x + x, O.y + y, -r * 0.7), M("sp_hill", (0.62, 0.56, 0.82), 0.9, bump=0.4, bump_scale=6), c, seg=20)
    # sky: deep gradient window + stars + ringed planet + Earth
    skym = sets2.M_sky_window("sp_skym", top=(0.05, 0.03, 0.22), bottom=(0.35, 0.18, 0.55), strength=1.6, trees=False)
    plane(sn + "_sky", (400, 200), (O.x, O.y + 110, 40), skym, c, rot=(math.radians(90), 0, 0))
    plane(sn + "_skyl", (300, 200), (O.x - 110, O.y + 30, 40), skym, c, rot=(math.radians(90), 0, math.radians(90)))
    plane(sn + "_skyr", (300, 200), (O.x + 110, O.y + 30, 40), skym, c, rot=(math.radians(90), 0, math.radians(90)))
    starm = M("sp_star", (1, 1, 1), 0.5, emit=(1, 0.97, 0.9), emit_str=12)
    stars = []
    for i in range(160):
        x, z = rnd.uniform(-110, 110), rnd.uniform(4, 75)
        s = sph(sn + f"_st{i}", rnd.uniform(0.12, 0.35), (O.x + x, O.y + 100, z), starm, c, seg=6); stars.append(s)
    planet = sph(sn + "_planet", 9, (O.x + 32, O.y + 85, 30), M("sp_planet", (1.0, 0.55, 0.3), 0.6, emit=(1.0, 0.5, 0.25), emit_str=0.6), c, seg=32)
    ring = cyl(sn + "_ring", 15, 0.15, (O.x + 32, O.y + 85, 30), M("sp_ringm", (1.0, 0.85, 0.5), 0.5, emit=(1, 0.8, 0.4), emit_str=0.8), c, 64, bevel=0, rot=(math.radians(75), math.radians(-20), 0))
    sph(sn + "_earth", 5, (O.x - 30, O.y + 80, 34), M("sp_earth", (0.2, 0.55, 1.0), 0.5, emit=(0.25, 0.55, 1.0), emit_str=0.8), c, seg=32)
    for k in range(5):
        sph(sn + f"_land{k}", 2.2, (O.x - 30 + rnd.uniform(-2.5, 2.5), O.y + 76.5, 34 + rnd.uniform(-2.5, 2.5)), M("sp_land", (0.3, 0.8, 0.35), 0.6, emit=(0.3, 0.8, 0.3), emit_str=0.6), c, seg=16, scale=(1, 0.4, 0.8))
    # ---- ROCKET on the launch pad (back-left) ----
    RX, RY = O.x - 2.6, O.y + 2.6
    box(sn + "_pad", (2.4, 2.4, 0.18), (RX, RY, 0.09), M("sp_pad", (0.35, 0.35, 0.42), 0.5, 0.4), c, 0.04)
    for i in range(8):
        a = i / 8 * 2 * math.pi
        sph(sn + f"_padl{i}", 0.06, (RX + 1.05 * math.cos(a), RY + 1.05 * math.sin(a), 0.2), M("sp_padlight", (1, 0.9, 0.3), 0.3, emit=(1, 0.8, 0.2), emit_str=10), c, seg=10)
    rocket = bpy.data.objects.new(sn + "_rocket", None); c.objects.link(rocket); rocket.location = (RX, RY, 0.18)
    red = M("sp_red", (0.95, 0.15, 0.18), 0.3, coat=0.8); white = M("sp_white", (0.96, 0.96, 0.98), 0.25, coat=0.8)
    win = M("sp_win", (0.5, 0.85, 1.0), 0.05, emit=(0.4, 0.8, 1.0), emit_str=2.0, coat=1.0)
    parts = [cyl(sn + "_rbody", 0.55, 2.6, (0, 0, 1.6), white, c, 40, bevel=0.03),
             cyl(sn + "_rband", 0.565, 0.3, (0, 0, 2.2), red, c, 40, bevel=0.02),
             cyl(sn + "_rband2", 0.565, 0.18, (0, 0, 0.55), red, c, 40, bevel=0.02),
             sph(sn + "_rnose", 0.55, (0, 0, 2.9), red, c, scale=(1, 1, 1.7), seg=32),
             cyl(sn + "_rwinr", 0.25, 0.08, (0, -0.53, 1.65), M("sp_winrim", (0.9, 0.75, 0.2), 0.3, 0.8), c, 32, bevel=0.01, rot=(math.radians(90), 0, 0)),
             cyl(sn + "_rwin", 0.2, 0.09, (0, -0.545, 1.65), win, c, 32, bevel=0.01, rot=(math.radians(90), 0, 0)),
             cyl(sn + "_rnozz", 0.4, 0.35, (0, 0, 0.18), M("sp_nozz", (0.3, 0.3, 0.35), 0.4, 0.8), c, 32, bevel=0.02)]
    for k in range(4):
        a = k / 4 * 2 * math.pi + math.pi / 4
        f = box(sn + f"_rfin{k}", (0.08, 0.7, 0.9), (0.62 * math.cos(a), 0.62 * math.sin(a), 0.6), red, c, 0.03); f.rotation_euler = (0, 0, a + math.pi / 2); parts.append(f)
    # BRO BROS letters on the rocket
    tx = text(sn + "_rtext", "BRO BROS", (0, -0.57, 1.05), 0.17, M("sp_txt", (0.15, 0.35, 0.95), 0.4), c); parts.append(tx)
    flame_m = M("sp_flame", (1.0, 0.6, 0.1), 0.5, emit=(1.0, 0.55, 0.1), emit_str=25)
    flame = sph(sn + "_flame", 0.38, (0, 0, -0.35), flame_m, c, scale=(1, 1, 2.2), seg=20); parts.append(flame)
    flame2 = sph(sn + "_flame2", 0.22, (0, 0, -0.25), M("sp_flame2", (1, 1, 0.7), 0.5, emit=(1, 0.95, 0.6), emit_str=40), c, scale=(1, 1, 2.0), seg=16); parts.append(flame2)
    for p_ in parts: p_.parent = rocket
    for o_ in (flame, flame2): o_.hide_render = True; o_.keyframe_insert("hide_render", frame=1)
    # launch tower
    for z in range(6):
        box(sn + f"_tw{z}", (0.12, 0.12, 0.6), (RX + 1.25, RY + 0.4, 0.5 + z * 0.6), M("sp_tower", (1.0, 0.75, 0.15), 0.4, 0.5), c, 0.01)
        box(sn + f"_twb{z}", (0.6, 0.06, 0.06), (RX + 1.0, RY + 0.4, 0.5 + z * 0.6), M("sp_tower", (1.0, 0.75, 0.15), 0.4, 0.5), c, 0.01)
    # ---- COUNTDOWN BOARD (back-right): a frame with a big glowing number per value 0..10, toggled by props ----
    BX, BY = O.x + 2.6, O.y + 3.0
    box(sn + "_board", (2.0, 0.2, 1.4), (BX, BY, 1.6), M("sp_boardm", (0.12, 0.1, 0.25), 0.4, coat=0.6), c, 0.05)
    box(sn + "_boardrim", (2.15, 0.16, 1.55), (BX, BY + 0.03, 1.6), M("sp_boardrim", (0.2, 0.85, 1.0), 0.3, emit=(0.2, 0.8, 1.0), emit_str=3), c, 0.05)
    for x_ in (-0.8, 0.8): cyl(sn + f"_bleg{x_}", 0.06, 0.9, (BX + x_, BY, 0.45), M("sp_bleg", (0.4, 0.4, 0.5), 0.4, 0.6), c, 12)
    digit_m = M("sp_digit", (1.0, 0.85, 0.2), 0.3, emit=(1.0, 0.85, 0.2), emit_str=8)
    digits = {}
    for n in range(0, 11):
        d = text(sn + f"_dg{n}", str(n), (BX, BY - 0.12, 1.32), 0.95, digit_m, c, extrude=0.02)
        d.hide_render = True; d.hide_viewport = True; d.keyframe_insert("hide_render", frame=1); d.keyframe_insert("hide_viewport", frame=1)
        digits[n] = d
    # flag + landing lights + floating asteroids
    cyl(sn + "_flagp", 0.025, 1.6, (O.x + 4.2, O.y + 0.8, 0.8), M("sp_flagp", (0.85, 0.85, 0.9), 0.3, 0.8), c, 10)
    fl = box(sn + "_flag", (0.6, 0.02, 0.4), (O.x + 4.5, O.y + 0.8, 1.4), M("sp_flagm", (1.0, 0.35, 0.6), 0.6), c, 0.01)
    sets2_key = None
    for i in range(10):
        x = -4.5 + i
        sph(sn + f"_ll{i}", 0.05, (O.x + x, O.y - 2.3, 0.04), M(f"sp_ll{i % 3}", [(0.3, 0.9, 1), (1, 0.4, 0.8), (1, 0.9, 0.3)][i % 3], 0.3, emit=[(0.3, 0.9, 1), (1, 0.4, 0.8), (1, 0.9, 0.3)][i % 3], emit_str=12), c, seg=8)
    rockm = M("sp_rock", (0.55, 0.45, 0.7), 0.8, bump=0.6, bump_scale=8)
    for i in range(7):
        a = sph(sn + f"_ast{i}", rnd.uniform(0.15, 0.4), (0, 0, 0), rockm, c, seg=10, scale=(1.2, 0.9, 0.8))
        x0, y0, z0, ph = rnd.uniform(-6, 6), rnd.uniform(4, 9), rnd.uniform(2.5, 5), rnd.uniform(0, 600)
        for f in range(1, 8001, 12):
            a.location = (O.x + x0 + 0.4 * math.sin((f + ph) / 90), O.y + y0, z0 + 0.25 * math.sin((f + ph) / 60)); a.rotation_euler = (f * 0.01, f * 0.013, 0)
            a.keyframe_insert("location", frame=f); a.keyframe_insert("rotation_euler", frame=f)
    # twinkle: a few stars pulse in size
    for i, s in enumerate(stars[:40]):
        for f in range(1, 8001, 24):
            k_ = 0.6 + 0.5 * abs(math.sin((f + i * 37) / 40)); s.scale = (k_, k_, k_); s.keyframe_insert("scale", frame=f)
    # lights: cool moonlight key + magenta/cyan rims for a party feel
    sun = bpy.data.objects.new(sn + "_sunlight", bpy.data.lights.new(sn + "_sunlight", "SUN")); c.objects.link(sun)
    sun.data.energy = 3.2; sun.data.color = (0.92, 0.92, 1.0); sun.data.angle = math.radians(3); sun.location = (O.x, O.y, 10)
    sun.rotation_euler = (math.radians(50), 0, math.radians(-25))
    area(sn + "_front", (O.x + 0.5, O.y - 5.0, 2.6), (O.x, O.y + 1.0, 0.9), 420, 4.0, c, (1.0, 0.96, 0.95))
    area(sn + "_rimL", (O.x - 4.5, O.y + 2.5, 2.5), (O.x, O.y, 0.9), 260, 2.0, c, (1.0, 0.4, 0.85))
    area(sn + "_rimR", (O.x + 4.5, O.y + 2.5, 2.5), (O.x, O.y, 0.9), 260, 2.0, c, (0.3, 0.8, 1.0))
    area(sn + "_fill", (O.x, O.y - 3, 5.5), (O.x, O.y + 1, 0.0), 300, 6.0, c, (0.8, 0.8, 1.0))
    SETS[sn] = dict(origin=O, coll=c, rocket=rocket, flames=(flame, flame2), rocket_xy=(RX, RY), digits=digits, board=(BX, BY), flag=fl,
                    cams={"space_wide": ((O.x + 0.0, O.y - 4.0, 1.45), (O.x + 0.0, O.y + 1.3, 1.05), 26),
                          "low_wide": ((O.x - 1.2, O.y - 4.2, 0.55), (O.x + 0.2, O.y + 1.5, 1.2), 24),
                          "high_wide": ((O.x + 0.0, O.y - 4.4, 2.7), (O.x, O.y + 0.8, 0.6), 26),
                          "insert:rocket": ((RX + 1.6, RY - 3.4, 1.4), (RX, RY, 1.9), 28),
                          "insert:board": ((BX - 0.7, BY - 2.6, 1.4), (BX, BY, 1.55), 32),
                          "insert:sky": ((O.x, O.y - 2, 1.4), (O.x + 10, O.y + 85, 28), 26)})
    return SETS[sn]

sets2.build_space = build_space
