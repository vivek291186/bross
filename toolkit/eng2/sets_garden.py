# Ep 9+: sunny BACKYARD GARDEN (origin x=1700). New look vs park: wooden picket fence + house patio, raised veggie patch
# (carrot tops, cabbages, big pumpkin), sloppy MUD PUDDLE, inflatable KIDDIE POOL, rotating SPRINKLER with a hose to a tap,
# washing line with swaying clothes, garden gnome, wheelbarrow, stepping-stone path, sunflowers, fluttering butterflies.
import bpy, math, random
from mathutils import Vector
import sets2, sets_park
from sets2 import SETS, M, M_wood, M_tiles, box, cyl, sph, plane, area, col

def torus(name, loc, R, r, mat, coll, seg=40, rseg=14):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=seg, minor_segments=rseg, location=loc)
    o = bpy.context.active_object; o.name = name
    for cc in list(o.users_collection): cc.objects.unlink(o)
    coll.objects.link(o); o.data.materials.append(mat)
    for p in o.data.polygons: p.use_smooth = True
    return o

def build_garden(O=Vector((1700, 0, 0))):
    sn = "garden"; c = col(sn); rnd = random.Random(9)
    grass = M("gd_grass", (0.33, 0.62, 0.20), 0.9, bump=0.8, bump_scale=22)
    grass2 = M("gd_grass2", (0.40, 0.68, 0.24), 0.9, bump=0.8, bump_scale=22)
    soil = M("gd_soil", (0.30, 0.19, 0.11), 0.95, bump=0.8, bump_scale=35)
    mud = M("gd_mud", (0.32, 0.21, 0.11), 0.18, bump=0.5, bump_scale=10, coat=0.6)
    stone = M("gd_stone", (0.72, 0.70, 0.66), 0.8, bump=0.4, bump_scale=20)
    fence_m = M("gd_fence", (0.97, 0.95, 0.90), 0.55)
    wood = M_wood("gd_wood", (0.62, 0.40, 0.22), (0.48, 0.30, 0.15), scale=3)
    # ground
    cyl(sn + "_ground", 70, 0.2, (O.x, O.y + 8, -0.1), grass, c, 96, bevel=0)
    cyl(sn + "_lawn", 6.5, 0.02, (O.x + 0.2, O.y + 0.2, 0.0), grass2, c, 64, bevel=0)
    # house patio behind camera-left: tiled patio + brick wall with a glass door and a window box
    box(sn + "_patio", (5.0, 3.2, 0.04), (O.x - 4.8, O.y - 2.2, 0.02), M_tiles("gd_patio", (0.86, 0.72, 0.58), (0.78, 0.62, 0.48), (0.6, 0.55, 0.5), 2.0, 0.7), c, 0.005)
    brick = M_tiles("gd_brick", (0.78, 0.38, 0.28), (0.70, 0.32, 0.24), (0.9, 0.85, 0.78), 5.0, 0.85, brick=True)
    box(sn + "_house", (0.3, 9.0, 3.2), (O.x - 7.3, O.y - 1.0, 1.6), brick, c, 0)
    box(sn + "_hdoor", (0.04, 1.4, 2.2), (O.x - 7.14, O.y - 1.6, 1.1), M("gd_glass", (0.75, 0.88, 0.95), 0.05, 0.3, coat=1.0), c, 0)
    box(sn + "_hdoorf", (0.06, 1.5, 2.3), (O.x - 7.16, O.y - 1.6, 1.15), M("gd_frame", (0.98, 0.98, 0.98), 0.4), c, 0.01)
    box(sn + "_wbox", (0.25, 1.2, 0.2), (O.x - 7.05, O.y + 1.4, 1.0), wood, c, 0.01)
    for i in range(6): sph(sn + f"_wbf{i}", 0.07, (O.x - 7.0, O.y + 0.9 + i * 0.2, 1.15), M(f"gd_wbf{i % 3}", [(0.95, 0.25, 0.35), (1.0, 0.8, 0.2), (0.95, 0.5, 0.85)][i % 3], 0.5), c, seg=10)
    # picket fence around the back + right
    for i in range(38):
        x = -7.0 + i * 0.4
        box(sn + f"_pk{i}", (0.1, 0.03, 0.95), (O.x + x, O.y + 4.6, 0.48), fence_m, c, 0.01)
        sph(sn + f"_pkt{i}", 0.05, (O.x + x, O.y + 4.6, 0.96), fence_m, c, scale=(1, 0.3, 0.8), seg=8)
    for z in (0.3, 0.75): box(sn + f"_pkbar{z}", (15.2, 0.03, 0.07), (O.x + 0.4, O.y + 4.63, z), fence_m, c, 0.005)
    for i in range(22):
        y = 4.4 - i * 0.4
        box(sn + f"_pkr{i}", (0.03, 0.1, 0.95), (O.x + 7.6, O.y + y, 0.48), fence_m, c, 0.01)
    box(sn + "_pkrbar", (0.03, 8.8, 0.07), (O.x + 7.63, O.y + 0.2, 0.75), fence_m, c, 0.005)
    # trees and sky beyond the fence
    trees = [sets_park.tree(sn + f"_tree{i}", (O.x + x, O.y + y, 0), c, h, r, i, seed=i + 20)
             for i, (x, y, h, r) in enumerate([(-6.0, 7.5, 3.8, 1.4), (-1.5, 8.5, 4.4, 1.6), (3.2, 7.2, 3.6, 1.3), (7.5, 8.0, 4.0, 1.5), (10.5, 3.0, 3.4, 1.2), (-10, 6, 3.6, 1.3)])]
    skym = sets2.M_sky_window("gd_skym", top=(0.28, 0.55, 0.98), bottom=(0.82, 0.92, 1.0), strength=2.6, trees=False)
    plane(sn + "_sky", (400, 160), (O.x, O.y + 120, 40), skym, c, rot=(math.radians(90), 0, 0))
    plane(sn + "_skyl", (300, 160), (O.x - 120, O.y + 30, 40), skym, c, rot=(math.radians(90), 0, math.radians(90)))
    plane(sn + "_skyr", (300, 160), (O.x + 120, O.y + 30, 40), skym, c, rot=(math.radians(90), 0, math.radians(90)))
    sph(sn + "_sunball", 4.0, (O.x + 35, O.y + 110, 44.0), M("gd_sun", (1, 1, 0.9), 0.5, emit=(1.0, 0.95, 0.8), emit_str=14.0), c)
    cloudm = M("gd_cloud", (1, 1, 1), 0.9, emit=(1, 1, 1), emit_str=0.9)
    for i in range(7):
        g = bpy.data.objects.new(sn + f"_cloud{i}", None); c.objects.link(g)
        x0, y0, z0 = rnd.uniform(-80, 80), rnd.uniform(60, 110), rnd.uniform(18, 32)
        for j in range(5):
            s = sph(sn + f"_cl{i}_{j}", rnd.uniform(2.5, 5.0), (rnd.uniform(-5, 5), rnd.uniform(-2, 2), rnd.uniform(-1, 1.5)), cloudm, c, seg=12, scale=(1.4, 1.0, 0.7)); s.parent = g
        g.location = (O.x + x0, O.y + y0, z0); g.keyframe_insert("location", frame=1)
        g.location = (O.x + x0 + 22, O.y + y0, z0); g.keyframe_insert("location", frame=8000)
    # ---- raised VEGGIE PATCH (back-left) ----
    VX, VY = O.x - 2.7, O.y + 2.7
    for nm_, sz, lc in (("f", (3.0, 0.08, 0.32), (0, -0.85, 0.16)), ("b", (3.0, 0.08, 0.32), (0, 0.85, 0.16)), ("l", (0.08, 1.78, 0.32), (-1.5, 0, 0.16)), ("r", (0.08, 1.78, 0.32), (1.5, 0, 0.16))):
        box(sn + "_vb" + nm_, sz, (VX + lc[0], VY + lc[1], lc[2]), wood, c, 0.01)
    box(sn + "_vsoil", (2.92, 1.62, 0.26), (VX, VY, 0.13), soil, c, 0.02)
    leaf = M("gd_leaf", (0.25, 0.62, 0.18), 0.7); orange = M("gd_carrot", (1.0, 0.48, 0.08), 0.5)
    carrots = []
    for row in range(2):
        for k in range(7):
            x = VX - 1.2 + k * 0.4; y = VY - 0.45 + row * 0.35
            sph(sn + f"_ct{row}{k}", 0.035, (x, y, 0.27), orange, c, seg=8)
            for j in range(3):
                l_ = box(sn + f"_cl{row}{k}{j}", (0.02, 0.006, 0.16), (x, y, 0.35), leaf, c, 0.002, rot=(0.35 * (j - 1), 0.25 * (j - 1), j))
            carrots.append((x, y))
    cab = M("gd_cabbage", (0.55, 0.8, 0.35), 0.6, bump=0.6, bump_scale=30)
    for k in range(4): sph(sn + f"_cab{k}", 0.13, (VX - 1.1 + k * 0.72, VY + 0.5, 0.33), cab, c, seg=14, scale=(1, 1, 0.8))
    pump = M("gd_pumpkin", (1.0, 0.5, 0.06), 0.45, coat=0.3)
    pk = bpy.data.objects.new(sn + "_pumpkin", None); c.objects.link(pk); pk.location = (VX + 1.95, VY - 0.2, 0.0)
    for k in range(8):
        a = k / 8 * 2 * math.pi; s_ = sph(sn + f"_pk{k}", 0.22, (math.cos(a) * 0.14, math.sin(a) * 0.14, 0.26), pump, c, seg=14, scale=(0.75, 0.75, 1.0)); s_.parent = pk
    st_ = cyl(sn + "_pkstem", 0.03, 0.12, (0, 0, 0.52), M("gd_stem", (0.35, 0.45, 0.15), 0.7), c, 8); st_.parent = pk
    # ---- MUD PUDDLE (centre-right, where the action is) ----
    MX, MY = O.x + 1.5, O.y + 0.9
    cyl(sn + "_mudrim", 1.05, 0.03, (MX, MY, 0.0), soil, c, 40, bevel=0).scale = (1.25, 0.85, 1)
    cyl(sn + "_mud", 0.92, 0.03, (MX, MY, 0.012), mud, c, 40, bevel=0).scale = (1.25, 0.85, 1)
    for k in range(9): sph(sn + f"_mudb{k}", rnd.uniform(0.04, 0.09), (MX + rnd.uniform(-0.9, 0.9), MY + rnd.uniform(-0.55, 0.55), 0.02), mud, c, seg=10, scale=(1, 1, 0.35))
    # ---- KIDDIE POOL (right-back) ----
    PX, PY = O.x + 3.6, O.y + 2.5
    ring_b = M("gd_ringb", (0.15, 0.55, 0.98), 0.25, coat=0.8); ring_y = M("gd_ringy", (1.0, 0.82, 0.15), 0.25, coat=0.8)
    torus(sn + "_pool1", (PX, PY, 0.12), 1.0, 0.12, ring_b, c)
    torus(sn + "_pool2", (PX, PY, 0.36), 1.0, 0.12, ring_y, c)
    cyl(sn + "_poolfloor", 1.02, 0.02, (PX, PY, 0.01), M("gd_poolfloor", (0.55, 0.85, 1.0), 0.3), c, 40, bevel=0)
    water = M("gd_water", (0.35, 0.72, 0.95), 0.03, coat=1.0, alpha=0.75, emit=(0.4, 0.75, 1.0), emit_str=0.15)
    poolw = cyl(sn + "_poolwater", 0.98, 0.02, (PX, PY, 0.3), water, c, 40, bevel=0)
    beachball = sph(sn + "_bball", 0.17, (PX + 0.4, PY - 0.2, 0.42), M("gd_bball", (1.0, 0.25, 0.25), 0.3, coat=0.7), c, seg=18)
    for f in range(1, 8001, 10):
        beachball.location.z = 0.42 + 0.02 * math.sin(f / 11.0); beachball.keyframe_insert("location", frame=f)
    # ---- SPRINKLER + hose to tap on the fence ----
    SX, SY = O.x - 0.6, O.y + 1.9
    cyl(sn + "_spbase", 0.12, 0.05, (SX, SY, 0.025), M("gd_spbase", (0.2, 0.75, 0.3), 0.4, coat=0.5), c, 20)
    sp = bpy.data.objects.new(sn + "_sprinkler", None); c.objects.link(sp); sp.location = (SX, SY, 0.1)
    a1 = box(sn + "_sparm", (0.42, 0.04, 0.03), (0, 0, 0.0), M("gd_sparm", (1.0, 0.85, 0.2), 0.3, coat=0.5), c, 0.01); a1.parent = sp
    cyl(sn + "_spstem", 0.02, 0.1, (SX, SY, 0.06), M("gd_spstem", (0.6, 0.6, 0.62), 0.3, 0.8), c, 8)
    hose_m = M("gd_hose", (0.2, 0.7, 0.25), 0.4, coat=0.4)
    pts = [(SX, SY), (SX - 0.4, SY + 0.5), (SX - 0.1, SY + 1.2), (SX - 0.7, SY + 1.8), (SX - 0.9, O.y + 4.45)]
    for i, (p0, p1) in enumerate(zip(pts, pts[1:])):
        L_ = math.dist(p0, p1); a_ = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        cyl(sn + f"_hose{i}", 0.025, L_, ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, 0.025), hose_m, c, 10, rot=(0, math.radians(90), a_))
    cyl(sn + "_tap", 0.04, 0.2, (SX - 0.9, O.y + 4.5, 0.55), M("gd_tap", (0.85, 0.85, 0.88), 0.15, 1.0), c, 12, rot=(math.radians(90), 0, 0))
    # ---- washing line with clothes that sway (right) ----
    for x_ in (4.4, 7.2): cyl(sn + f"_wlpost{x_}", 0.04, 2.0, (O.x + x_, O.y + 3.9, 1.0), wood, c, 10)
    cyl(sn + "_wline", 0.006, 2.8, (O.x + 5.8, O.y + 3.9, 1.85), M("gd_line", (0.95, 0.95, 0.95), 0.6), c, 6, rot=(0, math.radians(90), 0))
    clothes = []
    for i, (x_, cc, sz) in enumerate(((4.8, (0.95, 0.35, 0.45), (0.42, 0.02, 0.5)), (5.4, (0.3, 0.65, 0.98), (0.35, 0.02, 0.42)), (6.0, (1.0, 0.85, 0.25), (0.5, 0.02, 0.36)), (6.6, (0.6, 0.9, 0.5), (0.3, 0.02, 0.5)))):
        piv = bpy.data.objects.new(sn + f"_cloth{i}", None); c.objects.link(piv); piv.location = (O.x + x_, O.y + 3.9, 1.85)
        cl = box(sn + f"_clothm{i}", sz, (0, 0, -sz[2] / 2), M(f"gd_cloth{i}", cc, 0.9), c, 0.005); cl.parent = piv
        sets_park._key_sway(piv, amp=0.12, period=60 + i * 7, phase=i * 25, frames=8000, axis=0); clothes.append(piv)
    # ---- props: gnome, wheelbarrow, stepping stones, sunflowers, flower bed, bucket ----
    G = bpy.data.objects.new(sn + "_gnome", None); c.objects.link(G); G.location = (O.x - 4.2, O.y + 0.4, 0); G.rotation_euler = (0, 0, math.radians(-20))
    for nm_, ob_ in (("b", sph(sn + "_gnb", 0.13, (0, 0, 0.16), M("gd_gnblue", (0.2, 0.35, 0.85), 0.5), c, scale=(1, 1, 1.25))),
                     ("h", sph(sn + "_gnh", 0.08, (0, 0, 0.36), M("gd_gnskin", (1.0, 0.78, 0.62), 0.5), c)),
                     ("hat", cyl(sn + "_gnhat", 0.08, 0.22, (0, 0, 0.5), M("gd_gnred", (0.9, 0.12, 0.12), 0.4), c, 16)),
                     ("beard", sph(sn + "_gnbeard", 0.07, (0, -0.05, 0.3), M("gd_gnbeard", (0.97, 0.97, 0.97), 0.8), c, scale=(1, 0.6, 1.1)))):
        ob_.parent = G
    W_ = bpy.data.objects.new(sn + "_barrow", None); c.objects.link(W_); W_.location = (O.x - 4.6, O.y + 3.0, 0); W_.rotation_euler = (0, 0, math.radians(25))
    for ob_ in (box(sn + "_wbtub", (0.7, 0.5, 0.25), (0, 0, 0.4), M("gd_wbred", (0.85, 0.2, 0.15), 0.35, coat=0.5), c, 0.05),
                cyl(sn + "_wbwheel", 0.16, 0.06, (0.45, 0, 0.16), M("gd_black", (0.05, 0.05, 0.05), 0.6), c, 20, rot=(math.radians(90), 0, 0)),
                box(sn + "_wbh1", (0.7, 0.03, 0.03), (-0.55, 0.2, 0.42), wood, c, 0.01), box(sn + "_wbh2", (0.7, 0.03, 0.03), (-0.55, -0.2, 0.42), wood, c, 0.01)):
        ob_.parent = W_
    for i in range(8):
        a = i * 0.45; x = -4.6 + i * 0.7; y = -1.6 + 0.35 * math.sin(a)
        cyl(sn + f"_stone{i}", 0.22, 0.03, (O.x + x, O.y + y, 0.012), stone, c, 18, bevel=0.01).scale = (1.15, 0.85, 1)
    sun_c = M("gd_sunfl", (1.0, 0.8, 0.05), 0.5); sun_d = M("gd_sunfd", (0.35, 0.2, 0.08), 0.8)
    for i, x in enumerate((-5.6, -5.0, -0.2, 0.6, 2.2, 6.6)):
        y = 4.25; h = 1.2 + 0.25 * (i % 3)
        cyl(sn + f"_sfs{i}", 0.02, h, (O.x + x, O.y + y, h / 2), M("gd_sfstem", (0.25, 0.55, 0.15), 0.7), c, 8)
        cyl(sn + f"_sfp{i}", 0.17, 0.03, (O.x + x, O.y + y - 0.05, h), sun_c, c, 24, rot=(math.radians(80), 0, 0))
        cyl(sn + f"_sfd{i}", 0.08, 0.04, (O.x + x, O.y + y - 0.07, h), sun_d, c, 20, rot=(math.radians(80), 0, 0))
    for i in range(34):
        x = rnd.uniform(-6.5, 7.0); y = rnd.uniform(3.6, 4.3)
        cc = rnd.choice([(0.95, 0.2, 0.3), (0.98, 0.85, 0.2), (0.9, 0.4, 0.8), (1.0, 1.0, 1.0), (0.5, 0.4, 0.95)])
        sph(sn + f"_bed{i}", 0.06, (O.x + x, O.y + y, 0.25 + rnd.uniform(0, 0.12)), M(f"gd_bf{i % 5}", cc, 0.5), c, seg=8)
        box(sn + f"_bedl{i}", (0.12, 0.12, 0.25), (O.x + x, O.y + y, 0.12), leaf, c, 0.03)
    # butterflies fluttering around the garden
    for i in range(4):
        bf = bpy.data.objects.new(sn + f"_bfly{i}", None); c.objects.link(bf)
        cc = [(1.0, 0.55, 0.1), (0.4, 0.7, 1.0), (1.0, 0.4, 0.75), (1.0, 0.95, 0.3)][i]
        wings = []
        for sgn in (-1, 1):
            wp = bpy.data.objects.new(sn + f"_bfw{i}{sgn}", None); c.objects.link(wp); wp.parent = bf
            w_ = box(sn + f"_bfwm{i}{sgn}", (0.07, 0.05, 0.004), (sgn * 0.04, 0, 0), M(f"gd_bfw{i}", cc, 0.5), c, 0.002); w_.parent = wp; wings.append((wp, sgn))
        cx_, cy_, r_ = rnd.uniform(-3, 3), rnd.uniform(0.5, 3.0), rnd.uniform(0.7, 1.4)
        for f in range(1, 8001, 3):
            t = (f + i * 211) / 180.0
            bf.location = (O.x + cx_ + r_ * math.cos(t) + 0.2 * math.sin(t * 3.1), O.y + cy_ + 0.7 * r_ * math.sin(t), 0.9 + 0.35 * math.sin(t * 2.3) + 0.1 * math.sin(f / 2.0))
            bf.rotation_euler = (0, 0, t + math.pi / 2); bf.keyframe_insert("location", frame=f); bf.keyframe_insert("rotation_euler", frame=f)
            for wp, sgn in wings:
                wp.rotation_euler = (0, sgn * (0.2 + 0.9 * abs(math.sin(f * 0.9))), 0); wp.keyframe_insert("rotation_euler", frame=f)
    # ---- lights: sunny afternoon ----
    sun = bpy.data.objects.new(sn + "_sunlight", bpy.data.lights.new(sn + "_sunlight", "SUN")); c.objects.link(sun)
    sun.data.energy = 4.5; sun.data.color = (1.0, 0.94, 0.82); sun.data.angle = math.radians(2.5); sun.location = (O.x, O.y, 10)
    sun.rotation_euler = (math.radians(48), 0, math.radians(30))
    area(sn + "_skyfill", (O.x, O.y - 4, 6.0), (O.x, O.y + 2, 0.5), 600, 8.0, c, (0.75, 0.85, 1.0))
    area(sn + "_front", (O.x - 2.0, O.y - 5.0, 2.5), (O.x, O.y + 1.5, 0.9), 350, 4.0, c, (1.0, 0.95, 0.9))
    SETS[sn] = dict(origin=O, coll=c, trees=trees, clothes=clothes, sprinkler=sp, spr_xy=(SX, SY), mud=(MX, MY), pool=(PX, PY), poolwater=poolw,
                    veg=(VX, VY), carrots=carrots, pumpkin=pk, gnome=G, barrow=W_,
                    cams={"garden_wide": ((O.x + 0.4, O.y - 4.0, 1.4), (O.x + 0.4, O.y + 1.4, 0.8), 28),
                          "low_wide": ((O.x - 1.4, O.y - 4.2, 0.55), (O.x + 0.4, O.y + 1.6, 0.9), 26),
                          "high_wide": ((O.x + 0.4, O.y - 4.4, 2.8), (O.x + 0.4, O.y + 1.0, 0.4), 26),
                          "insert:veg": ((VX + 1.4, VY - 2.2, 1.1), (VX + 0.3, VY, 0.35), 32),
                          "insert:mud": ((MX - 0.6, MY - 2.2, 0.9), (MX, MY, 0.05), 32),
                          "insert:pool": ((PX - 1.4, PY - 2.4, 1.2), (PX, PY, 0.3), 32),
                          "insert:sprinkler": ((SX + 0.9, SY - 1.6, 0.8), (SX, SY, 0.2), 32),
                          "insert:gnome": ((O.x - 3.6, O.y - 0.6, 0.45), (O.x - 4.2, O.y + 0.4, 0.3), 40),
                          "insert:fence": ((O.x + 0.4, O.y - 1.0, 1.0), (O.x + 0.4, O.y + 4.6, 0.7), 30)})
    return SETS[sn]

sets2.build_garden = build_garden
