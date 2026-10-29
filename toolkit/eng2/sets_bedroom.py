# Ep 11: SLEEPOVER BEDROOM at night (origin x=2500). Navy starry wallpaper, wooden floor + round rug, a big bunk bed (back-left),
# sleeping bags on the floor, a PILLOW FORT (right) with a draped blanket roof, twinkling fairy lights, a window with the moon,
# a glowing moon night-light, a dresser with a COOKIE JAR, a toy box, a door (left) with a light strip that opens for Mummy.
# Lighting: cosy night (moonlight + warm lamps); props switch to MORNING (sun through window) at the end.
import bpy, math, random
from mathutils import Vector
import sets2
from sets2 import SETS, M, M_wood, box, cyl, sph, plane, area, col, point

def build_bedroom(O=Vector((2500, 0, 0))):
    sn = "bedroom"; c = col(sn); rnd = random.Random(11)
    W, D, H = 8.0, 6.0, 2.9
    wall = M("bd_wall", (0.16, 0.2, 0.42), 0.8, bump=0.1, bump_scale=80)
    floor = M_wood("bd_floor", (0.55, 0.36, 0.2), (0.44, 0.28, 0.15), rough=0.4, scale=1.6, coat=0.3)
    box(sn + "_floor", (W, D + 6, 0.1), (O.x, O.y, -0.05), floor, c, 0)
    box(sn + "_ceil", (W, D + 6, 0.1), (O.x, O.y, H + 0.05), M("bd_ceil", (0.2, 0.22, 0.4), 0.9), c, 0)
    for nm, size, loc in (("_back", (W, 0.12, H), (O.x, O.y + 2.9, H / 2)), ("_left", (0.12, D + 6, H), (O.x - W / 2, O.y, H / 2)),
                          ("_right", (0.12, D + 6, H), (O.x + W / 2, O.y, H / 2)), ("_front", (W, 0.12, H), (O.x, O.y - 6.0, H / 2))):
        box(sn + nm, size, loc, wall, c, 0)
    # painted stars on the walls
    starm = M("bd_starpaint", (1.0, 0.92, 0.5), 0.5, emit=(1.0, 0.9, 0.45), emit_str=1.2)
    for i in range(46):
        x, z = rnd.uniform(-3.8, 3.8), rnd.uniform(1.2, 2.8)
        sph(sn + f"_wst{i}", rnd.uniform(0.015, 0.035), (O.x + x, O.y + 2.83, z), starm, c, seg=6)
    box(sn + "_rugbase", (0.01, 0.01, 0.01), (O.x, O.y, -5), floor, c, 0)
    cyl(sn + "_rug", 1.9, 0.015, (O.x + 0.2, O.y + 0.3, 0.008), M("bd_rug", (0.55, 0.3, 0.75), 0.95, bump=0.4, bump_scale=200), c, 64, bevel=0)
    cyl(sn + "_rug2", 1.4, 0.016, (O.x + 0.2, O.y + 0.3, 0.009), M("bd_rug2", (0.95, 0.65, 0.3), 0.95, bump=0.4, bump_scale=200), c, 64, bevel=0)
    # window with the moon (back centre-right)
    WX = O.x + 1.0
    sky = sets2.M_sky_window("bd_nightsky", top=(0.02, 0.03, 0.12), bottom=(0.1, 0.12, 0.3), strength=1.2, trees=False)
    win = box(sn + "_win", (1.4, 0.02, 1.0), (WX, O.y + 2.83, 1.75), sky, c, 0)
    for nm_, sz, lc in (("t", (1.55, 0.08, 0.08), (0, 0, 0.54)), ("b", (1.55, 0.08, 0.08), (0, 0, -0.54)), ("l", (0.08, 0.08, 1.1), (-0.74, 0, 0)), ("r", (0.08, 0.08, 1.1), (0.74, 0, 0)), ("m", (0.05, 0.06, 1.0), (0, 0, 0))):
        box(sn + "_wf" + nm_, sz, (WX + lc[0], O.y + 2.8, 1.75 + lc[2]), M("bd_wframe", (0.95, 0.95, 0.95), 0.4), c, 0.01)
    moon = sph(sn + "_moon", 0.18, (WX + 0.35, O.y + 2.81, 1.95), M("bd_moon", (1, 0.97, 0.85), 0.5, emit=(1, 0.96, 0.8), emit_str=6), c, seg=20, scale=(1, 0.2, 1))
    for i in range(10): sph(sn + f"_wstar{i}", 0.015, (WX + rnd.uniform(-0.6, 0.6), O.y + 2.81, 1.75 + rnd.uniform(-0.4, 0.45)), M("bd_wstarm", (1, 1, 1), 0.5, emit=(1, 1, 1), emit_str=8), c, seg=6)
    morning = box(sn + "_winday", (1.4, 0.01, 1.0), (WX, O.y + 2.82, 1.75), sets2.M_sky_window("bd_daysky", top=(0.35, 0.65, 1.0), bottom=(1.0, 0.85, 0.6), strength=3.0, trees=False), c, 0)
    curtm = M("bd_curtain", (0.95, 0.75, 0.3), 0.9)
    for sx in (-1, 1): box(sn + f"_curt{sx}", (0.35, 0.05, 1.5), (WX + sx * 0.95, O.y + 2.76, 1.6), curtm, c, 0.02)
    # BUNK BED (back-left)
    BX, BY = O.x - 2.5, O.y + 2.0
    wood = M_wood("bd_bedwood", (0.62, 0.42, 0.25), (0.5, 0.32, 0.18), scale=3)
    for dx in (-1.0, 1.0):
        for dy in (-0.45, 0.45): box(sn + f"_bpost{dx}{dy}", (0.08, 0.08, 2.1), (BX + dx, BY + dy, 1.05), wood, c, 0.01)
    for z, cc in ((0.35, (0.3, 0.6, 0.95)), (1.45, (0.95, 0.4, 0.45))):
        box(sn + f"_bframe{z}", (2.1, 1.0, 0.12), (BX, BY, z), wood, c, 0.01)
        box(sn + f"_mattress{z}", (1.95, 0.88, 0.16), (BX, BY, z + 0.13), M("bd_matt", (0.95, 0.95, 0.95), 0.8), c, 0.04)
        box(sn + f"_duvet{z}", (1.5, 0.92, 0.08), (BX + 0.22, BY, z + 0.24), M(f"bd_duvet{z}", cc, 0.85, bump=0.3, bump_scale=60), c, 0.04)
        box(sn + f"_pillow{z}", (0.4, 0.62, 0.12), (BX - 0.72, BY, z + 0.27), M("bd_pil", (1, 1, 1), 0.9), c, 0.05)
    for i in range(6): box(sn + f"_ladder{i}", (0.06, 0.4, 0.04), (BX + 1.08, BY - 0.2, 0.3 + i * 0.3), wood, c, 0.01)
    box(sn + "_rail", (2.0, 0.05, 0.25), (BX, BY - 0.48, 1.8), wood, c, 0.01)
    # sleeping bags on the floor (front, where the kids will lie)
    bags = []
    for i, (x, y, cc) in enumerate([(-1.6, -0.3, (0.2, 0.7, 0.4)), (-0.6, -0.5, (0.95, 0.55, 0.15)), (0.4, -0.5, (0.35, 0.5, 0.95)), (1.4, -0.3, (0.9, 0.3, 0.55))]):
        b = box(sn + f"_bag{i}", (0.7, 1.7, 0.12), (O.x + x, O.y + y, 0.06), M(f"bd_bag{i}", cc, 0.6, coat=0.2), c, 0.05)
        box(sn + f"_bagp{i}", (0.55, 0.32, 0.1), (O.x + x, O.y + y + 0.75, 0.14), M("bd_pil", (1, 1, 1), 0.9), c, 0.04)
        bags.append((O.x + x, O.y + y))
    # PILLOW FORT (right): stacked cushions + draped blanket roof + a flag
    FX, FY = O.x + 2.6, O.y + 1.4
    pcs = [(0.95, 0.4, 0.45), (0.4, 0.75, 0.95), (1.0, 0.85, 0.3), (0.55, 0.9, 0.5), (0.8, 0.5, 0.95)]
    k = 0
    for row in range(3):
        for j in range(5):
            a = j / 4 * math.pi; x = FX + math.cos(a) * 0.95; y = FY + math.sin(a) * 0.6
            p_ = box(sn + f"_fp{k}", (0.5, 0.25, 0.32), (x, y, 0.17 + row * 0.3), M(f"bd_fp{k % 5}", pcs[k % 5], 0.85), c, 0.08); p_.rotation_euler = (0, 0, a + math.pi / 2); k += 1
    blanket = box(sn + "_blanket", (2.3, 1.6, 0.03), (FX, FY + 0.15, 1.05), M("bd_blanket", (0.98, 0.9, 0.7), 0.9, bump=0.3, bump_scale=100), c, 0.05)
    blanket.rotation_euler = (math.radians(8), 0, 0)
    cyl(sn + "_flagpole", 0.012, 0.6, (FX + 0.6, FY + 0.4, 1.35), M("bd_pole", (0.9, 0.9, 0.9), 0.4), c, 8)
    box(sn + "_flag", (0.3, 0.01, 0.2), (FX + 0.76, FY + 0.4, 1.55), M("bd_flag", (1, 0.25, 0.3), 0.6), c, 0)
    # dresser + COOKIE JAR (right wall, front of the fort)
    DX, DY = O.x + 3.45, O.y - 0.6
    box(sn + "_dresser", (0.8, 1.3, 0.85), (DX, DY, 0.425), M("bd_dresser", (0.95, 0.95, 0.92), 0.4), c, 0.03)
    for i in range(3): sph(sn + f"_knob{i}", 0.03, (DX - 0.41, DY, 0.2 + i * 0.27), M("bd_knob", (0.9, 0.7, 0.2), 0.3, 0.8), c, seg=8)
    jar = bpy.data.objects.new(sn + "_cookiejar", None); c.objects.link(jar); jar.location = (DX - 0.05, DY + 0.25, 0.85)
    j1 = cyl(sn + "_jar", 0.14, 0.28, (0, 0, 0.14), M("bd_jar", (0.85, 0.95, 1.0), 0.05, coat=1.0, alpha=0.45), c, 24); j1.parent = jar
    lid = cyl(sn + "_jarlid", 0.15, 0.04, (0, 0, 0.3), M("bd_lid", (0.95, 0.4, 0.45), 0.4), c, 24); lid.parent = jar
    for i in range(6): ck = cyl(sn + f"_ck{i}", 0.06, 0.015, (rnd.uniform(-0.05, 0.05), rnd.uniform(-0.05, 0.05), 0.04 + i * 0.035), M("bd_cookie", (0.75, 0.5, 0.25), 0.8), c, 16, rot=(rnd.uniform(-0.3, 0.3), 0, 0)); ck.parent = jar
    # toy box + teddy
    box(sn + "_toybox", (0.9, 0.55, 0.5), (O.x - 3.2, O.y - 0.4, 0.25), M("bd_toybox", (0.95, 0.3, 0.3), 0.4, coat=0.4), c, 0.03)
    tb = sph(sn + "_teddy", 0.16, (O.x - 3.2, O.y - 0.4, 0.66), M("bd_teddy", (0.65, 0.42, 0.25), 0.95, bump=0.5, bump_scale=200), c, seg=14)
    sph(sn + "_teddyh", 0.11, (O.x - 3.2, O.y - 0.42, 0.88), M("bd_teddy", (0.65, 0.42, 0.25), 0.95, bump=0.5, bump_scale=200), c, seg=14)
    # moon night-light on a stool + fairy lights along the back wall
    cyl(sn + "_stool", 0.18, 0.45, (O.x - 1.0, O.y + 2.5, 0.225), wood, c, 20)
    nl = sph(sn + "_nightlight", 0.14, (O.x - 1.0, O.y + 2.5, 0.6), M("bd_nl", (1, 0.85, 0.5), 0.4, emit=(1, 0.8, 0.45), emit_str=5), c, seg=16, scale=(1, 0.6, 1))
    fairy = []
    fc_ = [(1, 0.35, 0.4), (1, 0.85, 0.3), (0.4, 0.85, 1), (0.6, 1, 0.5), (1, 0.55, 0.95)]
    for i in range(34):
        x = -3.7 + i * 0.22; z = 2.55 - 0.18 * math.sin((i % 11) / 10 * math.pi)
        f_ = sph(sn + f"_fairy{i}", 0.025, (O.x + x, O.y + 2.8, z), M(f"bd_fairy{i % 5}", fc_[i % 5], 0.3, emit=fc_[i % 5], emit_str=10), c, seg=8); fairy.append(f_)
    # door (left wall, front) with a light strip for Mummy's entrance
    door_piv = bpy.data.objects.new(sn + "_door", None); c.objects.link(door_piv); door_piv.location = (O.x - 3.93, O.y - 1.6, 0)
    dp = box(sn + "_doorp", (0.05, 0.95, 2.1), (0, 0.475, 1.05), M_wood("bd_door", (0.85, 0.85, 0.85), (0.78, 0.78, 0.78), scale=3), c, 0.01); dp.parent = door_piv
    dlight = box(sn + "_doorlight", (0.01, 0.93, 2.08), (O.x - 3.98, O.y - 1.13, 1.05), M("bd_dl", (1, 1, 1), 0.5, emit=(1.0, 0.92, 0.75), emit_str=8.0), c, 0)
    # lights: cool moonlight through the window, warm night-light, soft fill, fairy glow; MORNING sun (energy 0, keyed by props)
    moonl = area(sn + "_moonlight", (WX + 0.2, O.y + 2.4, 2.2), (O.x, O.y - 0.5, 0.0), 180, 1.4, c, (0.6, 0.7, 1.0))
    sets2.point(sn + "_nlpoint", (O.x - 1.0, O.y + 2.3, 0.7), 60, c, color=(1, 0.75, 0.4), radius=0.2)
    area(sn + "_front", (O.x + 0.5, O.y - 5.0, 2.4), (O.x, O.y + 0.8, 0.8), 230, 4.0, c, (0.75, 0.75, 1.0))
    area(sn + "_fairyfill", (O.x, O.y + 2.4, 2.4), (O.x, O.y, 0.6), 60, 6.0, c, (1.0, 0.8, 0.6))
    sund = bpy.data.lights.new(sn + "_morningsun", "AREA"); sund.energy = 0; sund.size = 2.0; sund.color = (1.0, 0.88, 0.65)
    sun = bpy.data.objects.new(sn + "_morningsun", sund); c.objects.link(sun); sun.location = (WX, O.y + 2.3, 2.0)
    sun.rotation_euler = (Vector((O.x, O.y - 1.0, 0)) - sun.location).to_track_quat("-Z", "Y").to_euler(); sund.keyframe_insert("energy", frame=1)
    SETS[sn] = dict(origin=O, coll=c, bags=bags, fort=(FX, FY), jar=jar, dresser=(DX, DY), fairy=fairy, door=door_piv, doorlight=dlight, moon=moon,
                    window_day=morning, sun=sun, moonlight=moonl, bunk=(BX, BY),
                    cams={"bed_wide": ((O.x + 0.0, O.y - 4.4, 1.5), (O.x + 0.0, O.y + 1.2, 0.9), 24),
                          "low_wide": ((O.x - 1.2, O.y - 4.2, 0.5), (O.x + 0.2, O.y + 1.4, 1.0), 24),
                          "high_wide": ((O.x + 0.0, O.y - 4.6, 2.6), (O.x, O.y + 0.6, 0.3), 24),
                          "insert:fort": ((FX - 1.2, FY - 2.6, 1.0), (FX, FY, 0.6), 30),
                          "insert:jar": ((DX - 1.5, DY - 1.2, 1.2), (DX - 0.05, DY + 0.25, 0.95), 38),
                          "insert:window": ((WX - 0.4, O.y + 0.2, 1.5), (WX, O.y + 2.8, 1.8), 32),
                          "insert:door": ((O.x - 1.8, O.y - 2.8, 1.3), (O.x - 3.9, O.y - 1.1, 1.0), 30),
                          "insert:bunk": ((BX + 1.4, BY - 2.6, 1.3), (BX, BY, 1.0), 30)})
    return SETS[sn]

sets2.build_bedroom = build_bedroom
