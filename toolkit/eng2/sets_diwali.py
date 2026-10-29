# Diwali set variants + festive props: decorated living room (day), balcony at night with diyas, rangoli, lanterns and fireworks.
import bpy, math, random
from mathutils import Vector, Matrix
import sets2
from sets2 import SETS, M, M_sky_window, box, cyl, sph, plane, area, point, col, _link

def _mat_flame():
    m = bpy.data.materials.get("diya_flame")
    if m: return m
    m = bpy.data.materials.new("diya_flame"); m.use_nodes = True; nt = m.node_tree
    p = nt.nodes["Principled BSDF"]; nt.nodes.remove(p)
    em = nt.nodes.new("ShaderNodeEmission"); out = [n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"][0]
    grad = nt.nodes.new("ShaderNodeTexGradient"); tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Rotation"].default_value = (0, -math.pi / 2, 0)
    ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.color_ramp.elements[0].color = (1.0, 0.95, 0.6, 1); ramp.color_ramp.elements[1].color = (1.0, 0.35, 0.05, 1)
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], grad.inputs["Vector"])
    nt.links.new(grad.outputs["Fac"], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], em.inputs["Color"])
    em.inputs["Strength"].default_value = 18.0; nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m

def diya(name, loc, coll, lit=True, r=0.045, light_energy=6.0):
    """clay lamp with a flame + warm point light; returns dict(flame, light, bowl)"""
    clay = M("diya_clay", (0.62, 0.30, 0.16), 0.75, bump=0.25, bump_scale=200)
    bowl = cyl(name + "_bowl", r, r * 0.55, (loc[0], loc[1], loc[2] + r * 0.27), clay, coll, 20, bevel=0.006)
    bowl.scale = (1.0, 0.8, 1.0)
    inner = cyl(name + "_oil", r * 0.8, 0.004, (loc[0], loc[1], loc[2] + r * 0.5), M("diya_oil", (0.95, 0.75, 0.35), 0.1, coat=1.0), coll, 20, bevel=0)
    inner.scale = (1.0, 0.8, 1.0)
    fl = sph(name + "_flame", r * 0.32, (loc[0] + r * 0.55, loc[1], loc[2] + r * 0.5 + r * 0.45), _mat_flame(), coll, scale=(0.6, 0.6, 1.5), seg=12)
    lt = point(name + "_lt", (loc[0] + r * 0.55, loc[1], loc[2] + r * 1.3), light_energy, coll, (1.0, 0.62, 0.25), 0.04)
    if not lit: fl.hide_render = True; fl.hide_viewport = True; lt.hide_render = True; lt.hide_viewport = True
    return dict(flame=fl, light=lt, bowl=bowl)

def toran(name, p0, p1, coll, n=None, sag=0.12):
    """marigold + mango-leaf garland hanging between two points"""
    mar = [M("marigold_o", (1.0, 0.45, 0.05), 0.8, bump=0.6, bump_scale=400), M("marigold_y", (1.0, 0.75, 0.1), 0.8, bump=0.6, bump_scale=400)]
    leaf = M("mango_leaf", (0.15, 0.45, 0.15), 0.5)
    p0, p1 = Vector(p0), Vector(p1); L = (p1 - p0).length; n = n or int(L / 0.07)
    objs = []
    for i in range(n + 1):
        t = i / n; p = p0.lerp(p1, t) + Vector((0, 0, -sag * 4 * t * (1 - t)))
        objs.append(sph(f"{name}_m{i}", 0.032, p, mar[i % 2], coll, seg=10))
        if i % 3 == 1:
            lf = sph(f"{name}_l{i}", 0.05, p + Vector((0, 0, -0.06)), leaf, coll, scale=(0.35, 0.12, 1.0), seg=8)
            lf.rotation_euler = (0, 0, random.Random(i).uniform(-0.4, 0.4))
    return objs

def string_lights(name, p0, p1, coll, n=None, sag=0.08, energy=0.0):
    cols = [(1, 0.25, 0.2), (0.2, 0.9, 0.3), (0.3, 0.5, 1.0), (1, 0.85, 0.2), (1, 0.4, 0.9)]
    wire = M("sl_wire", (0.05, 0.08, 0.05), 0.5)
    p0, p1 = Vector(p0), Vector(p1); L = (p1 - p0).length; n = n or int(L / 0.18)
    bulbs = []
    for i in range(n + 1):
        t = i / n; p = p0.lerp(p1, t) + Vector((0, 0, -sag * 4 * t * (1 - t)))
        c = cols[i % len(cols)]
        b = sph(f"{name}_b{i}", 0.018, p + Vector((0, 0, -0.03)), M(f"sl_{i % 5}", c, 0.3, emit=c, emit_str=8.0), coll, scale=(1, 1, 1.4), seg=10)
        bulbs.append(b)
        if energy and i % 2 == 0: point(f"{name}_lt{i}", p + Vector((0, -0.05, -0.05)), energy, coll, c, 0.03)
    cyl(name + "_wire", 0.003, L, (p0 + p1) / 2 + Vector((0, 0, -sag * 0.5)), wire, coll, 6, bevel=0, rot=(0, math.radians(90), math.atan2(p1.y - p0.y, p1.x - p0.x)))
    return bulbs

def lantern(name, loc, coll, color=(1.0, 0.3, 0.2)):
    pap = M(f"kandil_{name}", color, 0.6, emit=color, emit_str=4.0)
    body = sph(name + "_body", 0.14, loc, pap, coll, scale=(1, 1, 1.25), seg=16)
    cyl(name + "_top", 0.05, 0.03, (loc[0], loc[1], loc[2] + 0.18), M("kandil_gold", (0.95, 0.75, 0.25), 0.3, coat=0.6), coll)
    cyl(name + "_str", 0.003, 0.35, (loc[0], loc[1], loc[2] + 0.36), M("rope", (0.9, 0.9, 0.85), 0.8), coll, 6, bevel=0)
    for i in range(5): cyl(name + f"_tail{i}", 0.004, 0.3, (loc[0] - 0.04 + i * 0.02, loc[1], loc[2] - 0.3), M(f"kandil_tail{i % 2}", (1, 0.8, 0.2) if i % 2 else (1, 0.3, 0.2), 0.7), coll, 6, bevel=0)
    point(name + "_lt", loc, 25.0, coll, color, 0.1)
    return body

def rangoli(name, loc, coll, R=0.6):
    """concentric rangoli; returns list of layer groups (outer -> inner) so it can be revealed step by step"""
    cols = [(0.95, 0.15, 0.25), (1.0, 0.65, 0.05), (0.2, 0.6, 0.25), (0.25, 0.4, 0.95), (0.9, 0.2, 0.7), (1.0, 0.9, 0.3)]
    layers = []
    z = loc[2] + 0.003
    # 1 outer ring of petals, 2 ring, 3 inner flower, 4 centre diya
    g = []
    for i in range(16):
        a = i * math.pi / 8
        g.append(sph(f"{name}_p{i}", R * 0.16, (loc[0] + R * 0.86 * math.cos(a), loc[1] + R * 0.86 * math.sin(a), z), M("rang0", cols[0], 0.9), coll, scale=(1.4, 0.7, 0.03), seg=12))
        g[-1].rotation_euler = (0, 0, a)
    layers.append(g)
    g = [cyl(f"{name}_ring1", R * 0.72, 0.004, (loc[0], loc[1], z), M("rang1", cols[1], 0.9), coll, 48, bevel=0)]
    g.append(cyl(f"{name}_ring1b", R * 0.62, 0.0045, (loc[0], loc[1], z), M("rang2", cols[2], 0.9), coll, 48, bevel=0))
    layers.append(g)
    g = []
    for i in range(8):
        a = i * math.pi / 4
        g.append(sph(f"{name}_q{i}", R * 0.2, (loc[0] + R * 0.38 * math.cos(a), loc[1] + R * 0.38 * math.sin(a), z + 0.002), M("rang3", cols[3], 0.9), coll, scale=(1.3, 0.75, 0.03), seg=12))
        g[-1].rotation_euler = (0, 0, a)
    g.append(cyl(f"{name}_core", R * 0.2, 0.006, (loc[0], loc[1], z), M("rang4", cols[4], 0.9), coll, 32, bevel=0))
    layers.append(g)
    layers.append([diya(f"{name}_cd{i}", (loc[0] + R * 0.95 * math.cos(i * math.pi / 2 + math.pi / 4), loc[1] + R * 0.95 * math.sin(i * math.pi / 2 + math.pi / 4), loc[2]), coll, lit=False, r=0.04, light_energy=4.0) for i in range(4)])
    return layers

# ================= LIVING ROOM, DIWALI =================
def build_living_diwali(O=Vector((400, 0, 0))):
    s = sets2.build_living(O)
    c = s["coll"]; W, D, H = 9.0, 6.0, 2.9
    # torans along the back wall and over the balcony door, string lights on the ceiling edge
    toran("ld_toran1", (O.x - 4.3, O.y + 2.5, 2.75), (O.x - 0.2, O.y + 2.5, 2.75), c, sag=0.18)
    toran("ld_toran2", (O.x + 1.6, O.y + 2.5, 2.75), (O.x + 4.3, O.y + 2.5, 2.75), c, sag=0.15)
    string_lights("ld_sl1", (O.x - 4.4, O.y + 2.45, 2.55), (O.x + 4.4, O.y + 2.45, 2.55), c, sag=0.12)
    string_lights("ld_sl2", (O.x - 4.4, O.y - 0.2, 2.8), (O.x - 4.4, O.y + 2.4, 2.8), c, sag=0.0)
    # diyas on the coffee table + a brass thali of diyas on the TV unit
    for i in range(3): diya(f"ld_td{i}", (O.x + 1.25 + i * 0.3, O.y + 0.42, 0.40), c, r=0.04, light_energy=3.0)
    th = cyl("ld_thali", 0.28, 0.015, (O.x - W / 2 + 0.3, O.y - 0.3, 0.51), M("brass", (0.85, 0.65, 0.25), 0.3, coat=0.8), c, 40)
    for i in range(6): diya(f"ld_th{i}", (O.x - W / 2 + 0.3 + 0.17 * math.cos(i), O.y - 0.3 + 0.17 * math.sin(i), 0.52), c, r=0.035, light_energy=2.0)
    # lanterns hanging near the balcony door, gift boxes and a sweets box on the table
    lantern("ld_kandil1", (O.x + 2.9, O.y + 2.1, 2.1), c, (1.0, 0.3, 0.2)); lantern("ld_kandil2", (O.x + 3.5, O.y + 2.0, 1.9), c, (1.0, 0.75, 0.2))
    for i, (x, cc) in enumerate(((-0.9, (0.9, 0.2, 0.3)), (-0.55, (0.2, 0.5, 0.9)), (-0.2, (0.95, 0.75, 0.2)))):
        b = box(f"ld_gift{i}", (0.26, 0.22, 0.2), (O.x + x, O.y + 0.1, 0.1), M(f"gift{i}", cc, 0.5, coat=0.5), c, 0.01)
        box(f"ld_ribbon{i}", (0.27, 0.05, 0.21), (O.x + x, O.y + 0.1, 0.1), M("ribbon", (1, 0.85, 0.2), 0.4, coat=0.6), c, 0.002)
    box("ld_sweets", (0.34, 0.24, 0.07), (O.x + 1.95, O.y + 0.7, 0.435), M("sweetbox", (0.75, 0.15, 0.2), 0.4, coat=0.6), c, 0.006)
    for i in range(6): sets2.laddoo(f"ld_laddoo{i}", (O.x + 1.85 + (i % 3) * 0.09, O.y + 0.65 + (i // 3) * 0.09, 0.49), c)
    # unlit "fairy light" bundle on the floor for the Buddy gag (a tangled ball)
    tangle = []
    for i in range(14):
        a = i * 1.9; r = 0.14 + 0.05 * math.sin(i)
        tangle.append(sph(f"ld_tangle{i}", 0.018, (O.x - 1.6 + r * math.cos(a), O.y + 0.4 + r * math.sin(a), 0.03 + 0.06 * (i % 3)), M(f"sl_{i % 5}", [(1, 0.25, 0.2), (0.2, 0.9, 0.3), (0.3, 0.5, 1.0), (1, 0.85, 0.2), (1, 0.4, 0.9)][i % 5], 0.3, emit=[(1, 0.25, 0.2), (0.2, 0.9, 0.3), (0.3, 0.5, 1.0), (1, 0.85, 0.2), (1, 0.4, 0.9)][i % 5], emit_str=8.0), c, seg=8))
    s["tangle"] = tangle
    s["cams"]["insert:thali"] = ((O.x - W / 2 + 1.1, O.y - 0.9, 0.9), (O.x - W / 2 + 0.3, O.y - 0.3, 0.55), 40)
    s["cams"]["insert:sweets"] = ((O.x + 1.6, O.y - 0.3, 0.85), (O.x + 1.95, O.y + 0.7, 0.47), 45)
    return s

# ================= BALCONY, NIGHT =================
def build_balcony_night(O=Vector((600, 0, 0))):
    sn = "balcony_night"; c = col(sn)
    floor = sets2.M_tiles("bn_floor", (0.55, 0.40, 0.32), (0.50, 0.36, 0.28), (0.4, 0.3, 0.25), 2.5, 0.35)
    wall = M("bn_wall", (0.80, 0.72, 0.60), 0.85, bump=0.12, bump_scale=120)
    rail = M("bn_rail", (0.15, 0.15, 0.17), 0.35, 0.6)
    box(sn + "_floor", (6.5, 7.0, 0.12), (O.x, O.y - 1.5, -0.06), floor, c, 0)
    box(sn + "_wl", (0.15, 7.0, 2.9), (O.x - 3.25, O.y - 1.5, 1.45), wall, c, 0)
    box(sn + "_wr", (0.15, 7.0, 2.9), (O.x + 3.25, O.y - 1.5, 1.45), wall, c, 0)
    box(sn + "_ceil", (6.5, 7.0, 0.15), (O.x, O.y - 1.5, 2.95), wall, c, 0)
    box(sn + "_slab", (6.5, 0.1, 0.5), (O.x, O.y + 1.6, 3.1), wall, c, 0)
    box(sn + "_railtop", (6.4, 0.08, 0.06), (O.x, O.y + 1.6, 1.0), rail, c, 0.01)
    box(sn + "_railbot", (6.4, 0.06, 0.05), (O.x, O.y + 1.6, 0.08), rail, c, 0.01)
    for i in range(33): cyl(sn + f"_bal{i}", 0.012, 0.95, (O.x - 3.2 + i * 0.2, O.y + 1.6, 0.52), rail, c, 8)
    for i, x in enumerate((-2.7, 2.7)): sets2.plant(f"bn_plant{i}", (O.x + x, O.y + 1.2, 0), c, 1.0)
    # night sky: deep blue gradient, stars, moon; city with lit windows and dark silhouettes
    skym = M_sky_window("bn_skym", top=(0.02, 0.03, 0.10), bottom=(0.10, 0.08, 0.22), strength=1.2, trees=False)
    plane(sn + "_sky", (260, 90), (O.x, O.y + 90, 10), skym, c, rot=(math.radians(90), 0, 0))
    rnd = random.Random(7)
    starm = M("bn_star", (1, 1, 1), 0.5, emit=(1, 0.97, 0.9), emit_str=30.0)
    for i in range(70):
        sph(sn + f"_star{i}", rnd.uniform(0.06, 0.16), (O.x + rnd.uniform(-90, 90), O.y + 88, rnd.uniform(8, 48)), starm, c, seg=6)
    sph(sn + "_moon", 2.6, (O.x - 30, O.y + 86, 30), M("bn_moon", (1, 1, 0.95), 0.5, emit=(1.0, 0.97, 0.85), emit_str=6.0), c)
    bld = []
    winm = M("bn_win", (1, 0.85, 0.55), 0.5, emit=(1, 0.8, 0.45), emit_str=6.0)
    for i in range(18):
        x = -60 + i * 7.0 + rnd.uniform(-1.5, 1.5); d = rnd.uniform(35, 70); hgt = rnd.uniform(14, 30); w = rnd.uniform(4.0, 7.0)
        b = box(sn + f"_bld{i}", (w, 5.0, hgt), (O.x + x, O.y + d, hgt / 2 - 18.0), M(f"bn_bld{i % 3}", (0.08, 0.08, 0.12), 0.9), c, 0.02)
        for r in range(int(hgt // 1.6)):
            for q in range(2):
                if rnd.random() < 0.6: box(sn + f"_bw{i}_{r}_{q}", (0.8, 0.02, 1.0), (O.x + x - w / 4 + q * w / 2, O.y + d - 2.52, -17.2 + r * 1.6), winm, c, 0)
        bld.append((O.x + x, O.y + d - 2.6, hgt - 18.0 + 0.3))
    # diyas along the railing + on the floor edge, lanterns, string lights across the ceiling
    diyas = []
    for i in range(11): diyas.append(diya(f"bn_rd{i}", (O.x - 3.0 + i * 0.6, O.y + 1.52, 1.03), c, lit=False, r=0.04, light_energy=5.0))
    for i in range(6): diyas.append(diya(f"bn_fd{i}", (O.x - 2.5 + i * 1.0, O.y + 1.35, 0.0), c, lit=False, r=0.045, light_energy=5.0))
    string_lights("bn_sl", (O.x - 3.2, O.y + 1.45, 2.8), (O.x + 3.2, O.y + 1.45, 2.8), c, sag=0.15)
    lantern("bn_kandil1", (O.x - 2.6, O.y + 0.9, 2.2), c, (1.0, 0.3, 0.2)); lantern("bn_kandil2", (O.x + 2.6, O.y + 0.9, 2.3), c, (1.0, 0.75, 0.2))
    # safety kit: bucket of water + sand tray, matches box on a stool (grown-up zone), a clay pot "anar" and a chakri on the floor
    bucket = cyl(sn + "_bucket", 0.16, 0.3, (O.x - 2.95, O.y + 0.2, 0.15), M("bucket", (0.2, 0.45, 0.85), 0.35, coat=0.3), c, 24)
    cyl(sn + "_water", 0.145, 0.01, (O.x - 2.95, O.y + 0.2, 0.29), M("water", (0.5, 0.75, 0.95), 0.05, coat=1.0), c, 24, bevel=0)
    box(sn + "_sand", (0.5, 0.35, 0.06), (O.x + 2.9, O.y + 0.3, 0.03), M("sandtray", (0.75, 0.65, 0.45), 0.95, bump=0.3, bump_scale=300), c, 0.005)
    anar = cyl(sn + "_anar", 0.055, 0.11, (O.x + 0.0, O.y + 1.2, 0.055), M("anar_clay", (0.55, 0.28, 0.15), 0.8, bump=0.3), c, 16)
    anar.scale = (1, 1, 1); anar_tip = Vector((O.x + 0.0, O.y + 1.2, 0.115))
    chakri = cyl(sn + "_chakri", 0.06, 0.012, (O.x + 1.4, O.y + 1.1, 0.006), M("chakri_m", (0.8, 0.15, 0.15), 0.6), c, 24)
    # unlit sparklers: thin grey sticks (one per kid, attached later by props)
    sparklers = {}
    for i, k in enumerate(("vanu", "aarav", "vihaan", "himank", "buddy")):
        st = cyl(f"bn_spk_{k}", 0.003, 0.3, (O.x - 2.0 + i * 0.5, O.y - 2.0, 0.15), M("spk_stick", (0.45, 0.45, 0.5), 0.4, 0.6), c, 8, bevel=0)
        st.hide_render = True; st.hide_viewport = True; sparklers[k] = st
    # lights: cool moon fill, warm low key from the diya side, soft top; the diya point lights do the rest once lit
    area(sn + "_moon", (O.x - 3.0, O.y + 5.0, 4.0), (O.x, O.y + 0.4, 0.8), 180, 4.0, c, (0.55, 0.65, 1.0))
    area(sn + "_key", (O.x + 2.2, O.y - 2.6, 2.4), (O.x, O.y + 0.5, 0.9), 220, 2.5, c, (1.0, 0.75, 0.5))
    area(sn + "_fill", (O.x - 2.6, O.y - 2.8, 1.8), (O.x, O.y + 0.5, 0.9), 90, 3.0, c, (0.6, 0.65, 0.9))
    area(sn + "_top", (O.x, O.y - 0.3, 2.85), (O.x, O.y - 0.3, 0), 60, 2.0, c, (1, 0.85, 0.7))
    SETS[sn] = dict(origin=O, coll=c, buildings=bld, diyas=diyas, sparklers=sparklers, anar=anar, anar_tip=anar_tip, chakri=chakri, bucket=bucket,
                    cams={"balcony_wide": ((O.x + 0.0, O.y - 3.4, 1.35), (O.x, O.y + 0.8, 0.95), 28),
                          "insert:city": ((O.x + 0.3, O.y + 0.6, 1.35), (O.x - 6.0, O.y + 50, 2.0), 35),
                          "insert:sky": ((O.x + 0.0, O.y + 0.6, 1.3), (O.x + 10.0, O.y + 80, 14.0), 28),
                          "insert:diyas": ((O.x - 1.2, O.y + 0.4, 1.25), (O.x + 0.6, O.y + 1.52, 1.03), 50),
                          "insert:bucket": ((O.x - 2.0, O.y - 0.8, 0.8), (O.x - 2.95, O.y + 0.2, 0.25), 40),
                          "insert:anar": ((O.x - 0.9, O.y - 0.4, 0.55), (O.x, O.y + 1.2, 0.25), 35),
                          "insert:chakri": ((O.x + 0.9, O.y - 0.3, 0.6), (O.x + 1.4, O.y + 1.1, 0.05), 35),
                          "low_wide": ((O.x - 0.4, O.y - 3.2, 0.5), (O.x, O.y + 0.9, 1.1), 24)})
    return SETS[sn]

sets2.build_living_diwali = build_living_diwali
sets2.build_balcony_night = build_balcony_night
