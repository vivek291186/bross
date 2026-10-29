# Song 06: RAINY STREET (origin x=2300). Row of colourful town houses with lit windows, a glossy wet road + pavement, shiny puddles
# right where the kids dance, lamp posts, a red post box, dark rain clouds, falling-rain sheets (scrolling streak shader, cheap),
# lightning light, and a hidden blue sky + sun + RAINBOW that the props switch on when "the sun is back".
import bpy, math, random
from mathutils import Vector
import sets2, sets_park
from sets2 import SETS, M, box, cyl, sph, plane, area, col

def rain_mat(name, density=60.0, alpha=0.32):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; Lk = nt.links
    for n in list(N): N.remove(n)
    out = N.new("ShaderNodeOutputMaterial"); mix = N.new("ShaderNodeMixShader"); tr = N.new("ShaderNodeBsdfTransparent"); em = N.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0.85, 0.9, 1.0, 1); em.inputs["Strength"].default_value = 1.6
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (density, density, 2.2)
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.0; nz.inputs["Detail"].default_value = 0.0
    cr = N.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].position = 0.62; cr.color_ramp.elements[1].position = 0.7
    mul = N.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = alpha
    Lk.new(tc.outputs["Object"], mp.inputs["Vector"]); Lk.new(mp.outputs["Vector"], nz.inputs["Vector"]); Lk.new(nz.outputs["Fac"], cr.inputs["Fac"])
    Lk.new(cr.outputs["Color"], mul.inputs[0]); Lk.new(mul.outputs[0], mix.inputs["Fac"]); Lk.new(tr.outputs[0], mix.inputs[1]); Lk.new(em.outputs[0], mix.inputs[2])
    Lk.new(mix.outputs[0], out.inputs["Surface"])
    try: m.surface_render_method = "BLENDED"
    except Exception: pass
    # falling: scroll the mapping location in Z over the whole timeline
    loc = mp.inputs["Location"]; loc.default_value = (0, 0, 0); loc.keyframe_insert("default_value", frame=1)
    loc.default_value = (0, 0, 8000 * 0.55); loc.keyframe_insert("default_value", frame=8000)
    if nt.animation_data and nt.animation_data.action:
        for fc in nt.animation_data.action.fcurves:
            for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
    return m

def build_rainy(O=Vector((2300, 0, 0))):
    sn = "rainy"; c = col(sn); rnd = random.Random(6)
    road = M("rn_road", (0.16, 0.17, 0.2), 0.12, coat=0.9)
    pave = M("rn_pave", (0.45, 0.46, 0.5), 0.25, coat=0.6, bump=0.3, bump_scale=8)
    water = M("rn_puddle", (0.35, 0.5, 0.65), 0.02, 0.2, coat=1.0)
    box(sn + "_ground", (60, 60, 0.1), (O.x, O.y + 20, -0.06), M("rn_grass", (0.2, 0.42, 0.18), 0.6), c, 0)
    box(sn + "_road", (30, 5.5, 0.04), (O.x, O.y + 0.2, 0.0), road, c, 0)
    for i in range(14):   # dashed centre line
        box(sn + f"_dash{i}", (0.8, 0.08, 0.005), (O.x - 13 + i * 2.0, O.y - 1.4, 0.022), M("rn_dash", (0.95, 0.85, 0.3), 0.3), c, 0)
    box(sn + "_pave", (30, 1.8, 0.14), (O.x, O.y + 3.85, 0.07), pave, c, 0.01)
    box(sn + "_kerb", (30, 0.12, 0.16), (O.x, O.y + 2.95, 0.08), M("rn_kerb", (0.6, 0.6, 0.62), 0.3, coat=0.5), c, 0.01)
    # puddles where the kids dance (x = -1.7 .. 1.7) + a few more
    puddles = []
    for i, (x, y, r) in enumerate([(-1.7, 0.55, 0.5), (-0.85, 0.25, 0.45), (0.0, 0.1, 0.55), (0.85, 0.25, 0.45), (1.7, 0.55, 0.5), (-3.5, 1.4, 0.7), (3.4, 1.2, 0.8), (-2.6, -1.8, 0.6), (2.5, -2.0, 0.5)]):
        p_ = cyl(sn + f"_pud{i}", r, 0.012, (O.x + x, O.y + y, 0.024), water, c, 40, bevel=0); p_.scale = (1.3, 0.8, 1); puddles.append((O.x + x, O.y + y))
    # houses along the back (behind the pavement)
    hcols = [(0.95, 0.55, 0.45), (0.98, 0.85, 0.45), (0.55, 0.75, 0.95), (0.7, 0.9, 0.6), (0.9, 0.6, 0.85), (0.98, 0.7, 0.4), (0.6, 0.85, 0.85)]
    roofc = M("rn_roof", (0.45, 0.22, 0.2), 0.6); winm = M("rn_win", (1.0, 0.85, 0.5), 0.3, emit=(1.0, 0.8, 0.45), emit_str=3.0)
    x = -10.5; i = 0
    while x < 10.5:
        w = rnd.uniform(2.2, 3.0); h = rnd.uniform(2.6, 3.6); hc = hcols[i % len(hcols)]
        box(sn + f"_h{i}", (w - 0.08, 2.4, h), (O.x + x + w / 2, O.y + 5.95, h / 2), M(f"rn_h{i % 7}", hc, 0.7), c, 0.02)
        rf = cyl(sn + f"_rf{i}", w * 0.62, 2.5, (O.x + x + w / 2, O.y + 5.95, h + w * 0.18), roofc, c, 3, bevel=0.02, rot=(math.radians(90), 0, math.radians(90)))
        rf.scale = (0.6, 1, 1); rf.rotation_euler = (math.radians(90), math.radians(90), 0)
        for r_ in range(2):
            for k in range(2):
                box(sn + f"_w{i}{r_}{k}", (0.5, 0.04, 0.55), (O.x + x + w * (0.3 + 0.4 * k), O.y + 4.73, 0.9 + r_ * 1.25), winm, c, 0.01)
        box(sn + f"_door{i}", (0.55, 0.04, 1.0), (O.x + x + w / 2, O.y + 4.72, 0.5), M(f"rn_door{i % 3}", [(0.2, 0.35, 0.7), (0.6, 0.15, 0.15), (0.15, 0.45, 0.25)][i % 3], 0.4), c, 0.01)
        x += w; i += 1
    # lamp posts (lit), post box
    for j, lx in enumerate((-4.5, 0.6, 5.2)):
        cyl(sn + f"_lp{j}", 0.05, 3.0, (O.x + lx, O.y + 3.3, 1.5), M("rn_lpost", (0.12, 0.12, 0.14), 0.4, 0.6), c, 12)
        sph(sn + f"_lb{j}", 0.2, (O.x + lx, O.y + 3.3, 3.05), M("rn_lbulb", (1, 0.9, 0.6), 0.3, emit=(1, 0.85, 0.5), emit_str=8), c, seg=14)
        sets2.point(sn + f"_lpl{j}", (O.x + lx, O.y + 3.1, 2.8), 120, c, color=(1, 0.8, 0.5), radius=0.3)
    cyl(sn + "_postbox", 0.25, 1.1, (O.x - 6.4, O.y + 3.5, 0.68), M("rn_postbox", (0.85, 0.08, 0.1), 0.35, coat=0.5), c, 24)
    sph(sn + "_postboxtop", 0.25, (O.x - 6.4, O.y + 3.5, 1.23), M("rn_postbox", (0.85, 0.08, 0.1), 0.35, coat=0.5), c, scale=(1, 1, 0.45))
    for k, (tx, ty) in enumerate([(-12, 9), (12, 9), (-8, 10), (8, 10.5)]):
        sets_park.tree(sn + f"_tree{k}", (O.x + tx, O.y + ty, 0), c, 4.0, 1.5, k, seed=k + 60)
    # skies: grey rain sky (default) + blue sunny sky (hidden; props switch at the "sun is back")
    grey = sets2.M_sky_window("rn_skygrey", top=(0.28, 0.3, 0.36), bottom=(0.6, 0.62, 0.68), strength=1.4, trees=False)
    blue = sets2.M_sky_window("rn_skyblue", top=(0.25, 0.55, 1.0), bottom=(0.8, 0.92, 1.0), strength=2.6, trees=False)
    skies = {}
    for nm_, mt in (("grey", grey), ("blue", blue)):
        g = [plane(sn + f"_sky{nm_}", (400, 160), (O.x, O.y + 120, 40), mt, c, rot=(math.radians(90), 0, 0)),
             plane(sn + f"_sky{nm_}l", (300, 160), (O.x - 120, O.y + 30, 40), mt, c, rot=(math.radians(90), 0, math.radians(90))),
             plane(sn + f"_sky{nm_}r", (300, 160), (O.x + 120, O.y + 30, 40), mt, c, rot=(math.radians(90), 0, math.radians(90)))]
        skies[nm_] = g
    # rain clouds (dark) hanging low over the houses
    cm = M("rn_cloud", (0.42, 0.44, 0.5), 0.9)
    clouds = []
    for k in range(9):
        g = bpy.data.objects.new(sn + f"_cloud{k}", None); c.objects.link(g); g.location = (O.x - 16 + k * 4.2, O.y + 22, rnd.uniform(9, 12))
        for j in range(5):
            s = sph(sn + f"_cl{k}_{j}", rnd.uniform(1.6, 2.8), (rnd.uniform(-2.2, 2.2), rnd.uniform(-1, 1), rnd.uniform(-0.6, 0.8)), cm, c, seg=12, scale=(1.4, 1.0, 0.7)); s.parent = g
        clouds.append(g)
    # rain sheets (front-to-back)
    rains = []
    for k, (y, dens) in enumerate([(-2.4, 70), (0.9, 60), (3.0, 55), (8.0, 45)]):
        rp = plane(sn + f"_rain{k}", (24, 8), (O.x, O.y + y, 4.0), rain_mat(f"rn_rain{k}", dens, 0.3 if k else 0.18), c, rot=(math.radians(90), 0, 0))
        rains.append(rp)
    # sun + rainbow (hidden until the sun comes back)
    sunball = sph(sn + "_sunball", 4.0, (O.x + 28, O.y + 110, 46.0), M("rn_sun", (1, 1, 0.9), 0.5, emit=(1.0, 0.95, 0.8), emit_str=14.0), c)
    bowcols = [(1, 0.15, 0.15), (1, 0.55, 0.1), (1, 0.95, 0.2), (0.25, 0.85, 0.3), (0.2, 0.55, 1), (0.6, 0.3, 0.95)]
    rainbow = bpy.data.objects.new(sn + "_rainbow", None); c.objects.link(rainbow); rainbow.location = (O.x + 2.0, O.y + 40, -4.0)
    for k, cc in enumerate(bowcols):
        bpy.ops.mesh.primitive_torus_add(major_radius=22 - k * 0.9, minor_radius=0.45, major_segments=96, minor_segments=8, location=(0, 0, 0))
        t_ = bpy.context.active_object; t_.name = sn + f"_bow{k}"
        for cc_ in list(t_.users_collection): cc_.objects.unlink(t_)
        c.objects.link(t_); t_.data.materials.append(M(f"rn_bow{k}", cc, 0.5, emit=cc, emit_str=2.5)); t_.rotation_euler = (math.radians(90), 0, 0); t_.parent = rainbow
    # lights: soft overcast key + window glow fill; a lightning light (energy keyed by props); sunny key (keyed by props)
    sun = bpy.data.objects.new(sn + "_sunlight", bpy.data.lights.new(sn + "_sunlight", "SUN")); c.objects.link(sun)
    sun.data.energy = 1.6; sun.data.color = (0.82, 0.86, 0.95); sun.data.angle = math.radians(12); sun.location = (O.x, O.y, 10)
    sun.rotation_euler = (math.radians(55), 0, math.radians(-20))
    area(sn + "_front", (O.x + 0.5, O.y - 5.0, 2.6), (O.x, O.y + 1.0, 0.9), 420, 5.0, c, (0.95, 0.97, 1.0))
    area(sn + "_fill", (O.x, O.y - 3, 6.0), (O.x, O.y + 1, 0.0), 320, 8.0, c, (0.8, 0.85, 1.0))
    ld = bpy.data.lights.new(sn + "_lightning", "AREA"); ld.energy = 0; ld.size = 12; ld.color = (0.85, 0.9, 1.0)
    lo = bpy.data.objects.new(sn + "_lightning", ld); c.objects.link(lo); lo.location = (O.x, O.y + 4, 9); lo.rotation_euler = (0, 0, 0)
    ld.keyframe_insert("energy", frame=1)
    SETS[sn] = dict(origin=O, coll=c, puddles=puddles, skies=skies, clouds=clouds, rains=rains, sunball=sunball, rainbow=rainbow, sunlight=sun, lightning=lo,
                    cams={"rain_wide": ((O.x + 0.0, O.y - 4.2, 1.45), (O.x + 0.0, O.y + 1.4, 1.0), 26),
                          "low_wide": ((O.x - 1.2, O.y - 4.3, 0.45), (O.x + 0.2, O.y + 1.4, 1.1), 24),
                          "high_wide": ((O.x + 0.0, O.y - 4.5, 2.8), (O.x, O.y + 0.8, 0.5), 26),
                          "insert:puddle": ((O.x + 0.6, O.y - 1.6, 0.5), (O.x + 0.0, O.y + 0.1, 0.05), 32),
                          "insert:sky": ((O.x, O.y - 2, 1.4), (O.x + 4, O.y + 40, 9), 24),
                          "insert:houses": ((O.x - 1.0, O.y - 1.2, 1.5), (O.x - 1.0, O.y + 5.0, 1.6), 30)})
    return SETS[sn]

sets2.build_rainy = build_rainy
