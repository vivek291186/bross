# Song 7 (THANK YOU SONG): sunny hilltop PICNIC MEADOW (origin x=2700). Rolling green hills, a big round shade tree with a rope swing,
# a red-and-white checkered picnic blanket with a basket, sandwiches, juice cups, fruit bowl and a cake; a "THANK YOU" letter-flag
# bunting strung between two poles; wild-flower field, hay bales, balloons tied to the basket, kite in the sky.
import bpy, math, random
from mathutils import Vector
import sets2, sets_park
from sets2 import SETS, M, M_wood, box, cyl, sph, plane, area, col

def checker_mat(name, c1, c2, scale):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]; bsdf.inputs["Roughness"].default_value = 0.9
    ck = nt.nodes.new("ShaderNodeTexChecker"); ck.inputs["Scale"].default_value = scale
    ck.inputs["Color1"].default_value = (*c1, 1); ck.inputs["Color2"].default_value = (*c2, 1)
    tc = nt.nodes.new("ShaderNodeTexCoord"); nt.links.new(tc.outputs["Generated"], ck.inputs["Vector"])
    nt.links.new(ck.outputs["Color"], bsdf.inputs["Base Color"]); return m

def text_obj(name, s, loc, size, mat, coll, rot=(math.radians(90), 0, 0)):
    cu = bpy.data.curves.new(name, "FONT"); cu.body = s; cu.size = size; cu.align_x = "CENTER"; cu.align_y = "CENTER"; cu.extrude = 0.004
    try: cu.font = bpy.data.fonts.load("/home/claude/bbf/assets/Fredoka.ttf", check_existing=True)
    except Exception: pass
    o = bpy.data.objects.new(name, cu); coll.objects.link(o); o.location = loc; o.rotation_euler = rot; o.data.materials.append(mat); return o

def build_picnic(O=Vector((2700, 0, 0))):
    sn = "picnic"; c = col(sn); rnd = random.Random(7)
    grass = M("pc_grass", (0.36, 0.66, 0.22), 0.9, bump=0.8, bump_scale=22)
    grass2 = M("pc_grass2", (0.44, 0.72, 0.26), 0.9, bump=0.8, bump_scale=22)
    hillm = M("pc_hill", (0.30, 0.58, 0.20), 0.9, bump=0.6, bump_scale=8)
    cyl(sn + "_ground", 70, 0.2, (O.x, O.y + 8, -0.1), grass, c, 96, bevel=0)
    cyl(sn + "_lawn", 6.0, 0.02, (O.x, O.y + 0.3, 0.0), grass2, c, 64, bevel=0)
    for i, (x, y, r, h) in enumerate([(-14, 22, 12, 4.0), (4, 30, 16, 5.5), (22, 20, 11, 3.6), (-30, 34, 14, 5.0), (36, 36, 15, 4.5)]):
        sph(sn + f"_hill{i}", r, (O.x + x, O.y + y, -r + h), hillm, c, seg=40, scale=(1.6, 1.0, 1.0))
    # sky, sun, clouds, kite
    skym = sets2.M_sky_window("pc_skym", top=(0.25, 0.55, 1.0), bottom=(0.85, 0.94, 1.0), strength=2.6, trees=False)
    plane(sn + "_sky", (400, 160), (O.x, O.y + 120, 40), skym, c, rot=(math.radians(90), 0, 0))
    plane(sn + "_skyl", (300, 160), (O.x - 120, O.y + 30, 40), skym, c, rot=(math.radians(90), 0, math.radians(90)))
    plane(sn + "_skyr", (300, 160), (O.x + 120, O.y + 30, 40), skym, c, rot=(math.radians(90), 0, math.radians(90)))
    sph(sn + "_sunball", 4.0, (O.x - 30, O.y + 110, 46.0), M("pc_sun", (1, 1, 0.9), 0.5, emit=(1.0, 0.95, 0.8), emit_str=14.0), c)
    cloudm = M("pc_cloud", (1, 1, 1), 0.9, emit=(1, 1, 1), emit_str=0.9)
    for i in range(8):
        g = bpy.data.objects.new(sn + f"_cloud{i}", None); c.objects.link(g)
        g.location = (O.x + rnd.uniform(-80, 80), O.y + rnd.uniform(60, 110), rnd.uniform(16, 30))
        for j in range(5):
            s = sph(sn + f"_cl{i}_{j}", rnd.uniform(2.5, 5.0), (rnd.uniform(-5, 5), rnd.uniform(-2, 2), rnd.uniform(-1, 1.5)), cloudm, c, seg=12, scale=(1.4, 1.0, 0.7)); s.parent = g
    kite = bpy.data.objects.new(sn + "_kite", None); c.objects.link(kite); kite.location = (O.x + 3.5, O.y + 9.0, 6.0)
    kb = box(sn + "_kiteb", (0.9, 0.02, 0.9), (0, 0, 0), M("pc_kite", (1.0, 0.3, 0.35), 0.5), c, 0, rot=(0, math.radians(45), 0)); kb.parent = kite
    for i in range(5):
        t_ = box(sn + f"_kt{i}", (0.12, 0.01, 0.08), (0.0, 0, -0.75 - i * 0.22), M(f"pc_kt{i % 2}", [(1, 0.85, 0.2), (0.3, 0.7, 1)][i % 2], 0.5), c, 0); t_.parent = kite
    # big shade tree with a rope swing (back left)
    trees = [sets_park.tree(sn + f"_tree{i}", (O.x + x, O.y + y, 0), c, h, r, i, seed=i + 70)
             for i, (x, y, h, r) in enumerate([(-3.4, 3.2, 4.2, 1.9), (6.5, 8.0, 3.8, 1.4), (-8.5, 7.0, 3.6, 1.3), (10.0, 3.5, 3.4, 1.2)])]
    rope = M("pc_rope", (0.85, 0.75, 0.55), 0.9)
    swing = bpy.data.objects.new(sn + "_swing", None); c.objects.link(swing); swing.location = (O.x - 2.6, O.y + 3.0, 2.6)
    for sx in (-0.25, 0.25):
        r_ = cyl(sn + f"_rope{sx}", 0.012, 2.2, (sx, 0, -1.1), rope, c, 8); r_.parent = swing
    seat = box(sn + "_seat", (0.62, 0.22, 0.04), (0, 0, -2.2), M_wood("pc_seatw", (0.6, 0.38, 0.2), (0.48, 0.3, 0.15), scale=3), c, 0.01); seat.parent = swing
    for f, a in ((1, 0.12), (40, -0.12), (80, 0.12)):
        swing.rotation_euler = (a, 0, 0); swing.keyframe_insert("rotation_euler", frame=f)
    try:
        for fc in swing.animation_data.action.fcurves: fc.modifiers.new("CYCLES")
    except Exception: pass
    # THANK YOU bunting between two poles (back)
    pole_m = M("pc_pole", (0.95, 0.95, 0.95), 0.4)
    for sx in (-2.6, 2.6): cyl(sn + f"_bpole{sx}", 0.035, 2.4, (O.x + sx, O.y + 2.4, 1.2), pole_m, c, 12)
    cyl(sn + "_bstring", 0.006, 5.2, (O.x, O.y + 2.4, 2.25), rope, c, 6, rot=(0, math.radians(90), 0))
    letters = "THANK YOU"; flagc = [(1, 0.3, 0.35), (1, 0.75, 0.15), (0.3, 0.75, 0.35), (0.3, 0.6, 1.0), (0.85, 0.45, 0.95)]
    white = M("pc_letter", (1, 1, 1), 0.4, emit=(1, 1, 1), emit_str=0.3)
    flags = []
    for i, ch in enumerate(letters):
        x = -2.2 + i * 0.55; z = 2.22 - 0.12 * math.sin(i / (len(letters) - 1) * math.pi)
        if ch == " ": continue
        fm = M(f"pc_flag{i % 5}", flagc[i % 5], 0.6)
        bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=0.26, depth=0.01, location=(O.x + x, O.y + 2.38, z - 0.2), rotation=(math.radians(90), 0, math.radians(180)))
        fl = bpy.context.active_object; fl.name = sn + f"_flag{i}"
        for cc in list(fl.users_collection): cc.objects.unlink(fl)
        c.objects.link(fl); fl.data.materials.append(fm); fl.rotation_euler = (math.radians(90), math.radians(180), 0); flags.append(fl)
        text_obj(sn + f"_let{i}", ch, (O.x + x, O.y + 2.36, z - 0.12), 0.2, white, c)
    # picnic blanket (front centre) + food
    BX, BY = O.x, O.y - 1.15
    box(sn + "_blanket", (2.6, 1.5, 0.015), (BX, BY, 0.01), checker_mat("pc_check", (0.9, 0.12, 0.15), (0.98, 0.96, 0.92), 8.0), c, 0.004)
    wick = M("pc_wicker", (0.72, 0.5, 0.26), 0.85, bump=0.8, bump_scale=60)
    basket = box(sn + "_basket", (0.55, 0.35, 0.3), (BX - 0.85, BY + 0.25, 0.16), wick, c, 0.03)
    box(sn + "_basketlid", (0.57, 0.37, 0.03), (BX - 0.85, BY + 0.3, 0.33), wick, c, 0.01, rot=(math.radians(-20), 0, 0))
    bpy.ops.mesh.primitive_torus_add(major_radius=0.2, minor_radius=0.018, location=(BX - 0.85, BY + 0.25, 0.32), rotation=(math.radians(90), 0, 0))
    hd = bpy.context.active_object; hd.name = sn + "_handle"
    for cc in list(hd.users_collection): cc.objects.unlink(hd)
    c.objects.link(hd); hd.data.materials.append(wick)
    plate = M("pc_plate", (1, 1, 1), 0.3, coat=0.5)
    for i, (x, y) in enumerate([(-0.25, -0.35), (0.35, -0.35), (0.9, 0.15)]):
        cyl(sn + f"_plate{i}", 0.15, 0.015, (BX + x, BY + y, 0.025), plate, c, 24)
    bread = M("pc_bread", (0.95, 0.82, 0.55), 0.9); fill = M("pc_fill", (0.4, 0.75, 0.3), 0.7)
    for i, (x, y) in enumerate([(-0.25, -0.35), (0.35, -0.35)]):
        for z, m_ in ((0.04, bread), (0.055, fill), (0.07, bread)):
            bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=0.1, depth=0.015 if m_ is bread else 0.01, location=(BX + x, BY + y, z))
            o = bpy.context.active_object; o.name = sn + f"_sw{i}_{z}"
            for cc in list(o.users_collection): cc.objects.unlink(o)
            c.objects.link(o); o.data.materials.append(m_)
    # cake on the third plate
    cyl(sn + "_cake", 0.12, 0.12, (BX + 0.9, BY + 0.15, 0.09), M("pc_cake", (0.98, 0.75, 0.82), 0.5), c, 32)
    cyl(sn + "_icing", 0.125, 0.02, (BX + 0.9, BY + 0.15, 0.155), M("pc_icing", (1, 1, 1), 0.3), c, 32)
    sph(sn + "_cherry", 0.025, (BX + 0.9, BY + 0.15, 0.18), M("pc_cherry", (0.9, 0.05, 0.1), 0.2, coat=1.0), c, seg=12)
    # juice cups + fruit bowl
    for i, (x, y) in enumerate([(0.0, 0.25), (0.25, 0.3), (0.5, 0.2)]):
        cyl(sn + f"_cup{i}", 0.045, 0.11, (BX + x, BY + y, 0.065), M(f"pc_cup{i}", [(0.3, 0.6, 1.0), (1, 0.75, 0.2), (0.4, 0.85, 0.4)][i], 0.4), c, 16)
    cyl(sn + "_bowl", 0.17, 0.07, (BX - 0.35, BY + 0.25, 0.04), M("pc_bowl", (0.95, 0.9, 0.8), 0.4), c, 24)
    for i in range(7):
        sph(sn + f"_fruit{i}", 0.05, (BX - 0.35 + rnd.uniform(-0.09, 0.09), BY + 0.25 + rnd.uniform(-0.09, 0.09), 0.1), M(f"pc_fr{i % 3}", [(0.95, 0.15, 0.15), (1, 0.6, 0.1), (0.5, 0.8, 0.2)][i % 3], 0.4, coat=0.5), c, seg=12)
    # balloons tied to the basket
    for i, (dx, dz, cc) in enumerate([(-0.2, 1.7, (1, 0.25, 0.4)), (0.05, 1.85, (0.3, 0.6, 1.0)), (0.25, 1.65, (1, 0.8, 0.2))]):
        sph(sn + f"_bal{i}", 0.16, (BX - 0.85 + dx, BY + 0.35, dz), M(f"pc_bal{i}", cc, 0.2, coat=1.0), c, seg=20, scale=(1, 1, 1.18))
        cyl(sn + f"_bals{i}", 0.003, dz - 0.35, (BX - 0.85 + dx / 2, BY + 0.3, (dz + 0.3) / 2), rope, c, 4)
    # flowers + hay bales
    fcol = [(1, 0.3, 0.4), (1, 0.85, 0.2), (0.9, 0.5, 0.95), (1, 1, 1), (0.4, 0.6, 1.0)]
    stem = M("pc_stem", (0.2, 0.5, 0.15), 0.8)
    for i in range(140):
        a = rnd.uniform(0, 2 * math.pi); r = rnd.uniform(3.0, 9.0); x, y = math.cos(a) * r, math.sin(a) * r * 0.8 + 1.5
        if y < -2.5 and abs(x) < 4: continue
        sph(sn + f"_fl{i}", 0.045, (O.x + x, O.y + y, 0.16), M(f"pc_fl{i % 5}", fcol[i % 5], 0.5), c, seg=8, scale=(1, 1, 0.6))
    hay = M("pc_hay", (0.9, 0.75, 0.35), 0.95, bump=0.8, bump_scale=80)
    for i, (x, y) in enumerate([(3.6, 1.6), (4.3, 2.2), (-4.5, 0.4)]):
        box(sn + f"_hay{i}", (0.9, 0.55, 0.5), (O.x + x, O.y + y, 0.25), hay, c, 0.06)
    # lights: sunny late morning
    sun = bpy.data.objects.new(sn + "_sunlight", bpy.data.lights.new(sn + "_sunlight", "SUN")); c.objects.link(sun)
    sun.data.energy = 4.5; sun.data.color = (1.0, 0.95, 0.85); sun.data.angle = math.radians(2.5); sun.location = (O.x, O.y, 10)
    sun.rotation_euler = (math.radians(45), 0, math.radians(-25))
    area(sn + "_skyfill", (O.x, O.y - 4, 6.0), (O.x, O.y + 2, 0.5), 600, 8.0, c, (0.75, 0.85, 1.0))
    area(sn + "_front", (O.x + 2.0, O.y - 5.0, 2.5), (O.x, O.y + 1.0, 0.9), 350, 4.0, c, (1.0, 0.95, 0.9))
    SETS[sn] = dict(origin=O, coll=c, trees=trees, swing=swing, kite=kite, flags=flags, blanket=(BX, BY),
                    cams={"picnic_wide": ((O.x + 0.0, O.y - 4.3, 1.45), (O.x + 0.0, O.y + 1.2, 1.0), 26),
                          "low_wide": ((O.x - 1.2, O.y - 4.3, 0.45), (O.x + 0.2, O.y + 1.4, 1.2), 24),
                          "high_wide": ((O.x + 0.0, O.y - 4.6, 2.8), (O.x, O.y + 0.6, 0.5), 26),
                          "insert:blanket": ((O.x + 0.4, O.y - 2.6, 0.9), (BX, BY, 0.05), 32),
                          "insert:banner": ((O.x + 0.0, O.y - 1.8, 1.6), (O.x, O.y + 2.4, 2.0), 30),
                          "insert:sky": ((O.x, O.y - 2, 1.4), (O.x + 3.5, O.y + 9.0, 5.5), 30)})
    return SETS[sn]

sets2.build_picnic = build_picnic
