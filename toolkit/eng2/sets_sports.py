# Ep 10: SCHOOL SPORTS DAY field (origin x=2100). Running track with 4 coloured lanes along X, start line + finish line with a
# breakable ribbon, 3 hurdles, a mini soccer goal + ball, winners' podium (1-2-3), colourful bunting on poles, a scoreboard,
# bleachers with cheering cut-out crowd (bobbing), cones, a big balloon arch at the finish, sunny sky.
import bpy, math, random
from mathutils import Vector
import sets2, sets_park
from sets2 import SETS, M, M_wood, box, cyl, sph, plane, area, col, text

def build_sports(O=Vector((2100, 0, 0))):
    sn = "sports"; c = col(sn); rnd = random.Random(10)
    grass = M("spt_grass", (0.3, 0.62, 0.22), 0.9, bump=0.7, bump_scale=20)
    track = M("spt_track", (0.82, 0.32, 0.22), 0.85, bump=0.5, bump_scale=40)
    white = M("spt_white", (0.97, 0.97, 0.97), 0.5)
    cyl(sn + "_ground", 70, 0.2, (O.x, O.y + 8, -0.1), grass, c, 96, bevel=0)
    # track: 4 lanes along X (y from 0.0 to 2.4), lane lines
    TY0, LW = 0.0, 0.6
    box(sn + "_track", (16, 4 * LW + 0.2, 0.02), (O.x, O.y + TY0 + 2 * LW, 0.01), track, c, 0)
    for k in range(5):
        box(sn + f"_lane{k}", (16, 0.04, 0.005), (O.x, O.y + TY0 + k * LW, 0.022), white, c, 0)
    SX, FX = -5.0, 4.5   # start / finish x
    box(sn + "_startline", (0.12, 4 * LW, 0.005), (O.x + SX, O.y + TY0 + 2 * LW, 0.023), white, c, 0)
    for i in range(12):   # chequered finish line
        for j in range(2):
            if (i + j) % 2 == 0: box(sn + f"_fin{i}{j}", (0.1, 0.2, 0.005), (O.x + FX - 0.05 + j * 0.1, O.y + TY0 + i * 0.2 + 0.1, 0.023), M("spt_black", (0.05, 0.05, 0.05), 0.5), c, 0)
            else: box(sn + f"_fin{i}{j}", (0.1, 0.2, 0.005), (O.x + FX - 0.05 + j * 0.1, O.y + TY0 + i * 0.2 + 0.1, 0.023), white, c, 0)
    for k in range(4):
        text(sn + f"_ln{k}", str(k + 1), (O.x + SX - 0.45, O.y + TY0 + k * LW + 0.3, 0.025), 0.3, white, c, rot=(0, 0, math.radians(-90)), extrude=0.002)
    # finish posts + ribbon (ribbon broken by props) + balloon arch
    for y in (TY0 - 0.15, TY0 + 4 * LW + 0.15):
        cyl(sn + f"_fpost{y}", 0.05, 1.4, (O.x + FX, O.y + y, 0.7), M("spt_post", (0.95, 0.95, 0.95), 0.4), c, 12)
    ribbon = box(sn + "_ribbon", (0.02, 4 * LW + 0.3, 0.05), (O.x + FX, O.y + TY0 + 2 * LW, 0.9), M("spt_ribbon", (1.0, 0.2, 0.25), 0.5), c, 0)
    bcols = [(1, 0.3, 0.35), (1, 0.85, 0.2), (0.3, 0.7, 1), (0.4, 0.9, 0.4), (0.9, 0.45, 1)]
    for i in range(23):
        a = i / 22 * math.pi; y = O.y + TY0 + 2 * LW + math.cos(a) * 1.55; z = 0.2 + math.sin(a) * 2.2
        sph(sn + f"_bal{i}", 0.17, (O.x + FX, y, z), M(f"spt_bal{i % 5}", bcols[i % 5], 0.3, coat=0.8), c, seg=12, scale=(1, 1, 1.15))
    # hurdles (lane 2 & 3 area), x = -2.5, -0.5, 1.5
    hurdles = []
    for i, x in enumerate((-2.6, -0.6, 1.4)):
        g = bpy.data.objects.new(sn + f"_hurdle{i}", None); c.objects.link(g); g.location = (O.x + x, O.y + TY0 + 1.5, 0)
        for dy in (-0.42, 0.42):
            l_ = cyl(sn + f"_hl{i}{dy}", 0.02, 0.45, (0, dy, 0.225), M("spt_hleg", (0.85, 0.85, 0.88), 0.3, 0.8), c, 8); l_.parent = g
        b_ = box(sn + f"_hb{i}", (0.06, 0.9, 0.09), (0, 0, 0.45), M("spt_hbar", (1.0, 0.85, 0.1), 0.4), c, 0.01); b_.parent = g
        hurdles.append(g)
    # mini soccer goal (back right) + ball
    GX, GY = O.x + 3.4, O.y + 4.4
    for dx in (-0.9, 0.9): cyl(sn + f"_gp{dx}", 0.04, 1.0, (GX + dx, GY, 0.5), white, c, 12)
    cyl(sn + "_gbar", 0.04, 1.84, (GX, GY, 1.0), white, c, 12, rot=(0, math.radians(90), 0))
    box(sn + "_gnet", (1.8, 0.02, 0.98), (GX, GY + 0.45, 0.5), M("spt_net", (0.95, 0.95, 0.95), 0.6, alpha=0.35), c, 0)
    ball = bpy.data.objects.new(sn + "_ball", None); c.objects.link(ball); ball.location = (GX - 0.2, GY - 2.2, 0.11)
    bm = sph(sn + "_ballm", 0.11, (0, 0, 0), white, c, seg=16); bm.parent = ball
    for k in range(6):
        a = k / 6 * 2 * math.pi
        p_ = sph(sn + f"_ballp{k}", 0.045, (0.09 * math.cos(a), 0.09 * math.sin(a), 0.05 * ((-1) ** k)), M("spt_black", (0.05, 0.05, 0.05), 0.5), c, seg=8, scale=(1, 1, 0.4)); p_.parent = ball
    # podium (back left): 2 - 1 - 3
    PX, PY = O.x - 3.0, O.y + 4.4
    pod = {}
    for place, dx, h, colr in ((1, 0.0, 0.6, (1.0, 0.8, 0.15)), (2, -0.75, 0.4, (0.8, 0.82, 0.88)), (3, 0.75, 0.25, (0.85, 0.5, 0.25))):
        box(sn + f"_pod{place}", (0.72, 0.7, h), (PX + dx, PY, h / 2), M(f"spt_pod{place}", colr, 0.35, coat=0.4), c, 0.02)
        text(sn + f"_podn{place}", str(place), (PX + dx, PY - 0.36, h * 0.45), 0.28, white, c, extrude=0.01)
        pod[place] = (PX + dx, PY, h)
    # bunting on poles along the back
    for i in range(6): cyl(sn + f"_bp{i}", 0.04, 2.6, (O.x - 7 + i * 2.8, O.y + 6.0, 1.3), M("spt_bpole", (0.95, 0.95, 0.95), 0.4), c, 10)
    for i in range(5):
        for j in range(8):
            x = O.x - 7 + i * 2.8 + 0.18 + j * 0.33; sag = 0.25 * math.sin((j + 0.5) / 8 * math.pi)
            f_ = box(sn + f"_flag{i}{j}", (0.22, 0.01, 0.26), (x, O.y + 6.0, 2.45 - sag - 0.13), M(f"spt_fl{(i + j) % 5}", bcols[(i + j) % 5], 0.6), c, 0)
    # scoreboard (top right of the back)
    box(sn + "_sboard", (2.4, 0.15, 1.2), (O.x + 5.6, O.y + 6.4, 2.4), M("spt_sb", (0.1, 0.25, 0.15), 0.4), c, 0.04)
    for x_ in (-1.0, 1.0): cyl(sn + f"_sbl{x_}", 0.06, 1.9, (O.x + 5.6 + x_, O.y + 6.4, 0.95), M("spt_sbl", (0.4, 0.4, 0.45), 0.4, 0.6), c, 12)
    text(sn + "_sbt", "SPORTS DAY", (O.x + 5.6, O.y + 6.31, 2.55), 0.32, M("spt_sbtx", (1, 0.85, 0.2), 0.3, emit=(1, 0.8, 0.2), emit_str=4), c, extrude=0.01)
    text(sn + "_sbt2", "BRO BROS", (O.x + 5.6, O.y + 6.31, 2.1), 0.26, M("spt_sbtx2", (0.4, 0.85, 1), 0.3, emit=(0.4, 0.85, 1), emit_str=4), c, extrude=0.01)
    # bleachers with a bobbing cut-out crowd (back, behind the track)
    for r in range(3):
        box(sn + f"_bl{r}", (9.0, 0.6, 0.3 + r * 0.35), (O.x - 0.5, O.y + 7.2 + r * 0.6, (0.3 + r * 0.35) / 2), M("spt_bleach", (0.25, 0.45, 0.85), 0.4), c, 0.02)
    crowd = []
    for r in range(3):
        for i in range(14):
            x = O.x - 4.7 + i * 0.65 + rnd.uniform(-0.1, 0.1)
            g = bpy.data.objects.new(sn + f"_fan{r}{i}", None); c.objects.link(g); g.location = (x, O.y + 7.2 + r * 0.6, 0.3 + r * 0.35)
            b_ = sph(sn + f"_fanb{r}{i}", 0.17, (0, 0, 0.2), M(f"spt_fan{(r * 3 + i) % 5}", bcols[(r * 3 + i) % 5], 0.6), c, seg=10, scale=(1, 0.6, 1.3)); b_.parent = g
            h_ = sph(sn + f"_fanh{r}{i}", 0.1, (0, 0, 0.5), M("spt_skin", rnd.choice([(0.95, 0.75, 0.6), (0.75, 0.52, 0.38), (0.55, 0.38, 0.28)]), 0.6), c, seg=10); h_.parent = g
            ph = rnd.uniform(0, 50)
            for f in range(1, 8001, 6):
                g.location.z = 0.3 + r * 0.35 + 0.06 * abs(math.sin((f + ph) / 7.0)); g.keyframe_insert("location", frame=f)
            crowd.append(g)
    # cones + trees
    for i, x in enumerate((-6.2, -5.6, 5.4, 6.0)):
        cyl(sn + f"_cone{i}", 0.12, 0.35, (O.x + x, O.y - 0.6, 0.17), M("spt_cone", (1, 0.45, 0.05), 0.4), c, 16)
    for i, (x, y, h, r) in enumerate([(-9, 9, 4.0, 1.5), (9.5, 9, 4.2, 1.6), (-12, 4, 3.6, 1.3), (12, 3, 3.8, 1.4), (0, 12, 4.4, 1.7)]):
        sets_park.tree(sn + f"_tree{i}", (O.x + x, O.y + y, 0), c, h, r, i, seed=i + 40)
    skym = sets2.M_sky_window("spt_skym", top=(0.25, 0.52, 0.98), bottom=(0.8, 0.9, 1.0), strength=2.6, trees=False)
    plane(sn + "_sky", (400, 160), (O.x, O.y + 120, 40), skym, c, rot=(math.radians(90), 0, 0))
    plane(sn + "_skyl", (300, 160), (O.x - 120, O.y + 30, 40), skym, c, rot=(math.radians(90), 0, math.radians(90)))
    plane(sn + "_skyr", (300, 160), (O.x + 120, O.y + 30, 40), skym, c, rot=(math.radians(90), 0, math.radians(90)))
    sph(sn + "_sunball", 4.0, (O.x - 25, O.y + 110, 44.0), M("spt_sun", (1, 1, 0.9), 0.5, emit=(1.0, 0.95, 0.8), emit_str=14.0), c)
    sun = bpy.data.objects.new(sn + "_sunlight", bpy.data.lights.new(sn + "_sunlight", "SUN")); c.objects.link(sun)
    sun.data.energy = 4.5; sun.data.color = (1.0, 0.95, 0.85); sun.data.angle = math.radians(2.5); sun.location = (O.x, O.y, 10)
    sun.rotation_euler = (math.radians(50), 0, math.radians(-30))
    area(sn + "_skyfill", (O.x, O.y - 4, 6.0), (O.x, O.y + 2, 0.5), 600, 8.0, c, (0.75, 0.85, 1.0))
    area(sn + "_front", (O.x + 1.5, O.y - 5.0, 2.5), (O.x, O.y + 1.5, 0.9), 350, 4.0, c, (1.0, 0.95, 0.9))
    SETS[sn] = dict(origin=O, coll=c, ribbon=ribbon, hurdles=hurdles, ball=ball, goal=(GX, GY), podium=pod, crowd=crowd, start_x=SX, finish_x=FX, lane_y0=TY0, lane_w=LW,
                    cams={"sports_wide": ((O.x + 0.0, O.y - 4.6, 1.5), (O.x + 0.0, O.y + 1.6, 0.8), 24),
                          "low_wide": ((O.x - 1.4, O.y - 4.4, 0.55), (O.x + 0.2, O.y + 1.6, 0.9), 24),
                          "high_wide": ((O.x + 0.0, O.y - 4.8, 3.0), (O.x, O.y + 1.4, 0.4), 24),
                          "insert:start": ((O.x + SX + 1.6, O.y - 1.8, 0.9), (O.x + SX, O.y + 1.2, 0.5), 30),
                          "insert:finish": ((O.x + FX - 1.4, O.y - 2.2, 1.1), (O.x + FX, O.y + 1.2, 0.8), 30),
                          "insert:hurdles": ((O.x - 0.6, O.y - 2.6, 1.0), (O.x - 0.6, O.y + 1.5, 0.4), 28),
                          "insert:goal": ((GX - 0.4, GY - 4.0, 1.0), (GX, GY, 0.5), 30),
                          "insert:podium": ((PX + 0.0, PY - 3.4, 1.4), (PX, PY, 1.1), 30),
                          "insert:crowd": ((O.x - 0.5, O.y + 3.0, 1.2), (O.x - 0.5, O.y + 8.0, 1.0), 32),
                          "insert:scoreboard": ((O.x + 4.0, O.y + 2.0, 1.8), (O.x + 5.6, O.y + 6.4, 2.3), 34)})
    return SETS[sn]

sets2.build_sports = build_sports
