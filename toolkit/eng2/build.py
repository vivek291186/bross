# Bro Bros Fun - "Diwali Cracker Night" 3D comedy scene (Blender 3.4)
# Reads timeline.json (dialogue, actions, shots) and builds + animates the whole scene.
import bpy, math, random, json, os
from mathutils import Vector

D = "/Users/vivekkhatri/Downloads/.bbf/3d2/"
TL = json.load(open(D + "timeline.json"))
FPS = 24
def F(t): return 1 + int(round(t * FPS))
N = F(TL["total"])
rnd = random.Random(11)

# ---------------- reset ----------------
sc = bpy.context.scene
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras, bpy.data.curves, bpy.data.images, bpy.data.particles):
    for x_ in list(coll):
        try: coll.remove(x_)
        except Exception: pass
for c_ in list(bpy.data.collections): bpy.data.collections.remove(c_)

sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1280, 720, 100
sc.render.fps = FPS; sc.frame_start, sc.frame_end = 1, N
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"
sc.render.filepath = D + "frames/f_"
sc.view_settings.view_transform = "Filmic"; sc.view_settings.look = "Medium High Contrast"
sc.view_settings.exposure = 0.35
ee = sc.eevee
ee.taa_render_samples = 12
ee.use_gtao = True; ee.gtao_distance = 1.0
ee.use_bloom = True; ee.bloom_intensity = 0.09; ee.bloom_threshold = 0.9; ee.bloom_radius = 6.0
ee.use_soft_shadows = True; ee.shadow_cube_size = "512"; ee.shadow_cascade_size = "2048"

# ---------------- helpers ----------------
def C(c): return tuple((x / 255) ** 2.2 for x in c)
_mats = {}
def mat(rgb, rough=0.55, emit=0.0, name=None):
    key = name or (tuple(rgb), rough, emit)
    if key in _mats: return _mats[key]
    m = bpy.data.materials.new(str(name or rgb)); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*C(rgb), 1); b.inputs["Roughness"].default_value = rough
    b.inputs["Specular"].default_value = 0.3
    if emit:
        b.inputs["Emission"].default_value = (*C(rgb), 1); b.inputs["Emission Strength"].default_value = emit
    _mats[key] = m; return m

def face_mat(png):
    m = bpy.data.materials.new("face_" + png); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(D + png)
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"]); nt.links.new(tex.outputs["Alpha"], b.inputs["Alpha"])
    nt.links.new(tex.outputs["Color"], b.inputs["Emission"]); b.inputs["Emission Strength"].default_value = 0.55
    b.inputs["Roughness"].default_value = 0.8
    m.blend_method = "CLIP"; m.shadow_method = "CLIP"; return m

def smooth(o):
    if o.type == "MESH":
        for p in o.data.polygons: p.use_smooth = True
    return o

def put(o, m=None, parent=None):
    if m: o.data.materials.append(m)
    if parent: o.parent = parent
    return smooth(o)

def sph(loc, scale, m, parent=None, seg=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=max(8, seg // 2), location=loc)
    o = bpy.context.object; o.scale = scale; return put(o, m, parent)

def ico(r, m, loc=(0, 0, -200)):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=r, location=loc); o = bpy.context.object
    o.data.materials.append(m); return o

def box(loc, scale, m, parent=None, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc); o = bpy.context.object; o.scale = scale
    if bevel:
        md = o.modifiers.new("b", "BEVEL"); md.width = bevel; md.segments = 2
    o.data.materials.append(m)
    if parent: o.parent = parent
    return o

def cyl(loc, r, depth, m, parent=None, rot=(0, 0, 0), verts=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    return put(bpy.context.object, m, parent)

def cone(loc, r1, r2, depth, m, parent=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=r1, radius2=r2, depth=depth, location=loc, rotation=rot)
    return put(bpy.context.object, m, parent)

def emp(name, loc, parent=None):
    o = bpy.data.objects.new(name, None); o.location = loc; sc.collection.objects.link(o)
    if parent: o.parent = parent
    return o

def text(body, loc, size, m, parent=None):
    bpy.ops.object.text_add(location=loc, rotation=(math.radians(90), 0, 0))
    t = bpy.context.object; t.data.body = body; t.data.size = size; t.data.align_x = "CENTER"; t.data.align_y = "CENTER"
    t.data.extrude = 0.005; t.data.materials.append(m)
    if parent: t.parent = parent
    return t

def plight(loc, energy, color, size=0.2, shadow=False):
    bpy.ops.object.light_add(type="POINT", location=loc); L = bpy.context.object
    L.data.energy = energy; L.data.color = color; L.data.shadow_soft_size = size; L.data.use_shadow = shadow
    return L

def key_vis(o, f_on, f_off=None):
    """Scale-pop an object in at f_on (and out at f_off)."""
    s = tuple(o.scale)
    o.scale = (0, 0, 0); o.keyframe_insert("scale", frame=max(1, f_on - 1))
    o.scale = s; o.keyframe_insert("scale", frame=f_on + 3)
    if f_off:
        o.keyframe_insert("scale", frame=f_off - 3); o.scale = (0, 0, 0); o.keyframe_insert("scale", frame=f_off)
    o.scale = s

def emitter(name, loc, parent=None, kind="disc", size=0.05):
    if kind == "disc":
        bpy.ops.mesh.primitive_circle_add(vertices=8, radius=size, fill_type="NGON", location=loc)
    elif kind == "ring":
        bpy.ops.mesh.primitive_circle_add(vertices=12, radius=size, fill_type="NOTHING", location=loc)
    else:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=size, location=loc)
    o = bpy.context.object; o.name = name
    if parent: o.parent = parent
    o.show_instancer_for_render = False; o.show_instancer_for_viewport = False
    return o

def particles(em, count, f0, f1, life, inst=None, coll=None, size=1.0, normal=0.0, align=(0, 0, 0), rand=0.0,
              grav=1.0, emit_from="FACE", obj_factor=0.0, life_rand=0.3, drag=0.0):
    ps = em.modifiers.new("ps", "PARTICLE_SYSTEM").particle_system.settings
    ps.count = count; ps.frame_start = f0; ps.frame_end = max(f0 + 1, f1); ps.lifetime = life; ps.lifetime_random = life_rand
    ps.emit_from = emit_from; ps.use_emit_random = True
    ps.normal_factor = normal; ps.object_align_factor = align; ps.factor_random = rand; ps.object_factor = obj_factor
    ps.effector_weights.gravity = grav; ps.drag_factor = drag
    ps.particle_size = size; ps.size_random = 0.5
    if coll:
        ps.render_type = "COLLECTION"; ps.instance_collection = coll; ps.use_collection_pick_random = True
    else:
        ps.render_type = "OBJECT"; ps.instance_object = inst
    return ps

HIDE = bpy.data.collections.new("instances"); sc.collection.children.link(HIDE)
def hidden(o):
    for c in o.users_collection: c.objects.unlink(o)
    HIDE.objects.link(o); return o

# spark instance objects
SPK_GOLD = hidden(ico(0.03, mat((255, 200, 80), emit=14, name="spk_gold")))
SPK_WHITE = hidden(ico(0.022, mat((255, 245, 220), emit=18, name="spk_white")))
SPK_ORANGE = hidden(ico(0.03, mat((255, 140, 40), emit=14, name="spk_orange")))
SMOKE = hidden(ico(0.12, mat((120, 115, 125), rough=1.0, name="smoke")))
FW = bpy.data.collections.new("fw_cols"); sc.collection.children.link(FW)
for i, c in enumerate([(255, 60, 90), (80, 200, 255), (120, 255, 120), (255, 220, 60), (210, 110, 255), (255, 150, 40)]):
    o = ico(0.09, mat(c, emit=22, name=f"fw{i}"))
    for cc in o.users_collection: cc.objects.unlink(o)
    FW.objects.link(o)
STAR = hidden(ico(0.08, mat((255, 250, 230), emit=6, name="star")))

# ---------------- world & lights ----------------
w = bpy.data.worlds.new("night"); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes["Background"]; bg.inputs["Color"].default_value = (*C((22, 24, 70)), 1); bg.inputs["Strength"].default_value = 0.7
bpy.ops.object.light_add(type="SUN", location=(0, 0, 20), rotation=(math.radians(55), math.radians(-15), math.radians(25)))
moon = bpy.context.object; moon.data.energy = 0.9; moon.data.color = (0.65, 0.75, 1.0); moon.data.angle = math.radians(4)
bpy.ops.object.light_add(type="AREA", location=(0, 2.0, 4.2), rotation=(math.radians(-60), 0, 0))
house_l = bpy.context.object; house_l.data.energy = 650; house_l.data.size = 9; house_l.data.color = (1.0, 0.72, 0.42)
bpy.ops.object.light_add(type="AREA", location=(0, -9, 5), rotation=(math.radians(58), 0, 0))
fill = bpy.context.object; fill.data.energy = 420; fill.data.size = 14; fill.data.color = (0.7, 0.75, 1.0)

# ---------------- set ----------------
bpy.ops.mesh.primitive_plane_add(size=120, location=(0, 20, 0)); put(bpy.context.object, mat((60, 55, 70)))
box((0, 0.2, 0.005), (6.5, 4.5, 0.01), mat((150, 85, 60), rough=0.8))          # courtyard tiles
for i in range(-6, 7):
    box((i, 0.2, 0.012), (0.012, 4.5, 0.002), mat((110, 60, 45)))
box((0, 0.55, 0.02), (3.4, 0.05, 0.01), mat((250, 250, 250), emit=0.6, name="line"))   # safety line
# house
box((0, 6.0, 2.4), (6.5, 1.0, 2.4), mat((245, 225, 190)), bevel=0.05)
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=7.6, depth=2.2, location=(0, 6.0, 5.9), rotation=(0, 0, math.radians(45)))
r_ = bpy.context.object; r_.scale = (1.0, 0.25, 1.0); r_.data.materials.append(mat((150, 40, 50)))
box((0, 4.98, 1.15), (0.75, 0.05, 1.15), mat((120, 60, 30)))                    # door
box((0, 4.94, 1.15), (0.6, 0.02, 1.0), mat((255, 190, 110), emit=1.2, name="doorglow"))
for wx in (-4.2, -2.4, 2.4, 4.2):
    box((wx, 4.97, 2.2), (0.6, 0.04, 0.6), mat((255, 200, 120), emit=2.0, name="win"))
    box((wx, 4.95, 2.2), (0.62, 0.02, 0.03), mat((90, 50, 30)))
    box((wx, 4.95, 2.2), (0.03, 0.02, 0.62), mat((90, 50, 30)))
# string lights along roof edge + toran
lcols = [(255, 220, 80), (255, 80, 120), (90, 210, 255), (130, 255, 140)]
for k in range(44):
    x = -6.4 + k * 0.3; z = 4.75 - 0.12 * abs(math.sin(k * 0.5))
    sph((x, 4.92, z), (0.05, 0.05, 0.05), mat(lcols[k % 4], emit=9, name=f"bulb{k%4}"), seg=10)
for k in range(15):
    x = -0.75 + k * 0.107
    cone((x, 4.9, 2.18), 0.05, 0.0, 0.16, mat((40, 150, 60)), rot=(math.radians(180), 0, 0))
    sph((x, 4.9, 2.32), (0.05, 0.05, 0.05), mat([(255, 150, 0), (255, 200, 30)][k % 2]), seg=10)
# diyas along house front + side walls
for i, x in enumerate([-5.5, -4.5, -3.5, -2.5, -1.5, 1.5, 2.5, 3.5, 4.5, 5.5]):
    sph((x, 4.6, 0.08), (0.17, 0.17, 0.09), mat((200, 100, 40)))
    sph((x, 4.6, 0.22), (0.045, 0.045, 0.09), mat((255, 190, 60), emit=25, name="flame"), seg=10)
for x in (-4.5, -1.5, 1.5, 4.5):
    plight((x, 4.4, 0.6), 30, (1.0, 0.65, 0.3), shadow=False)
for sx in (-1, 1):
    box((sx * 6.6, 0.2, 0.55), (0.12, 4.5, 0.55), mat((235, 215, 185)))
    for k in range(5):
        y = -3.5 + k * 1.7
        sph((sx * 6.6, y, 1.15), (0.14, 0.14, 0.08), mat((200, 100, 40)))
        sph((sx * 6.6, y, 1.27), (0.04, 0.04, 0.08), mat((255, 190, 60), emit=25, name="flame"), seg=10)
# rangoli
rc = [(230, 40, 80), (255, 190, 0), (40, 170, 90), (60, 110, 230), (150, 60, 210), (255, 130, 20)]
cyl((-3.6, 2.4, 0.02), 0.9, 0.01, mat((250, 245, 235)))
for i in range(8):
    a = i * math.pi / 4; cyl((-3.6 + math.cos(a) * 0.62, 2.4 + math.sin(a) * 0.62, 0.03), 0.16, 0.01, mat(rc[i % 6]))
cyl((-3.6, 2.4, 0.035), 0.36, 0.01, mat((255, 210, 30))); cyl((-3.6, 2.4, 0.045), 0.17, 0.01, mat((230, 40, 80)))
# trees + far houses + moon + stars
for (tx, ty) in ((-9, 4), (9.5, 3.5), (-12, 10), (12, 11)):
    cyl((tx, ty, 1.4), 0.22, 2.8, mat((80, 50, 30)))
    sph((tx, ty, 3.6), (1.6, 1.6, 1.8), mat((25, 70, 40)), seg=16)
for i in range(9):
    x = -24 + i * 6; h = rnd.uniform(3, 7)
    box((x, 26, h / 2), (2.4, 1.5, h / 2), mat((45, 40, 75)))
    for k in range(3):
        box((x - 1.2 + k * 1.2, 24.45, h * 0.6), (0.25, 0.02, 0.3), mat((255, 200, 110), emit=1.5, name="farwin"))
sph((-20, 60, 26), (3, 3, 3), mat((255, 250, 225), emit=4, name="moon"), seg=32)
st = emitter("stars", (0, 70, 30), kind="disc", size=1)
st.scale = (60, 1, 1); st.rotation_euler = (math.radians(90), 0, 0)
bpy.ops.object.mode_set(mode="OBJECT")
particles(st, 260, 1, 2, 100000, inst=STAR, grav=0, emit_from="FACE", life_rand=0)

# ---------------- characters ----------------
L1, L2 = 0.34, 0.32
def arm_ik(ox, oz):
    d = max(0.05, min(L1 + L2 - 0.02, math.hypot(ox, oz)))
    phi_t = math.atan2(ox, -oz)
    a = math.acos(max(-1, min(1, (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))))
    p1 = phi_t + a
    ex, ez = L1 * math.sin(p1), -L1 * math.cos(p1)
    tx, tz = d * math.sin(phi_t), -d * math.cos(phi_t)
    p2 = math.atan2(tx - ex, -(tz - ez))
    return p1, p2 - p1

def build_char(name, kind, x, y, scale=1.0):
    adult = kind == "papa"
    root = emp(name, (x, y, 0)); root.scale = (scale, scale, scale)
    body = emp(name + "_body", (0, 0, 0), root)
    if kind == "big": cloth, cloth_d = (64, 192, 235), (40, 140, 190)
    elif kind == "lil": cloth, cloth_d = (238, 72, 128), (190, 45, 95)
    else: cloth, cloth_d = (250, 246, 232), (220, 214, 196)
    mc, mcd = mat(cloth), mat(cloth_d)
    skin = mat((176, 118, 78)) if not adult else mat((190, 135, 95))
    pants = mcd if not adult else mat((240, 236, 225))
    shoe = mat((250, 250, 250)) if not adult else mat((120, 70, 40))
    rig = {"root": root, "body": body, "legs": [], "arms": [], "fingers": [], "sx": []}
    # legs
    hip_z = 0.74
    for sx in (-1, 1):
        hip = emp(f"{name}_hip{sx}", (sx * 0.2, 0, hip_z), body)
        sph((0, 0, -0.18), (0.14, 0.14, 0.22), pants, hip)
        knee = emp(f"{name}_knee{sx}", (0, 0, -0.37), hip)
        sph((0, 0, -0.16), (0.12, 0.12, 0.2), pants, knee)
        sph((0, -0.08, -0.34), (0.13, 0.2, 0.08), shoe, knee)
        rig["legs"].append((hip, knee))
    # torso / kurta
    sph((0, 0, 0.82), (0.38, 0.3, 0.2), pants, body)
    if adult:
        cone((0, 0, 1.05), 0.48, 0.36, 0.95, mc, body)
        sph((0, 0, 1.55), (0.45, 0.33, 0.25), mc, body)
        for k in range(4): sph((0, -0.36, 1.5 - k * 0.15), (0.025, 0.02, 0.025), mat((200, 160, 60)), body, seg=8)
    else:
        sph((0, 0, 1.22), (0.5, 0.38, 0.52), mc, body)
        sph((0, 0, 0.9), (0.46, 0.35, 0.2), mcd, body)
        box((0, -0.37, 1.22), (0.25, 0.015, 0.075), mat((255, 255, 255)), body)
        text("BIG BRO" if kind == "big" else "LIL BRO", (0, -0.39, 1.215), 0.12, mat((34, 22, 79)), body)
        for k in range(11):
            a = math.pi * (0.12 + 0.76 * k / 10)
            sph((math.cos(a) * 0.3, -math.sin(a) * 0.26 - 0.06, 1.62 - 0.12 * math.sin(a)), (0.06, 0.06, 0.06),
                mat([(255, 150, 0), (255, 200, 30), (240, 110, 0)][k % 3]), body, seg=10)
    # arms with finger hands
    sh_z = 1.62
    for sx in (-1, 1):
        sh = emp(f"{name}_sh{sx}", (sx * 0.44, 0, sh_z), body)
        sph((0, 0, -L1 / 2), (0.1, 0.1, L1 / 2 + 0.04), mc, sh)
        el = emp(f"{name}_el{sx}", (0, 0, -L1), sh)
        sph((0, 0, -L2 / 2), (0.09, 0.09, L2 / 2 + 0.03), mc if adult else mc, el)
        sph((0, 0, -L2 + 0.02), (0.08, 0.08, 0.05), mcd, el)
        wr = emp(f"{name}_wr{sx}", (0, 0, -L2 - 0.03), el)
        sph((0, 0, -0.06), (0.07, 0.045, 0.075), skin, wr)
        fl = []
        for i, fx in enumerate((-0.042, -0.014, 0.014, 0.042)):
            k1 = emp(f"{name}_k1_{sx}_{i}", (fx, 0, -0.12), wr)
            ln = 0.05 if i in (1, 2) else 0.042
            sph((0, 0, -ln), (0.017, 0.017, ln + 0.008), skin, k1, seg=10)
            k2 = emp(f"{name}_k2_{sx}_{i}", (0, 0, -ln * 2), k1)
            sph((0, 0, -0.03), (0.015, 0.015, 0.035), skin, k2, seg=10)
            fl.append((k1, k2))
        th = emp(f"{name}_th{sx}", (sx * 0.062, -0.02, -0.04), wr)
        th.rotation_euler = (0, -sx * math.radians(50), 0)
        sph((0, 0, -0.04), (0.019, 0.019, 0.05), skin, th, seg=10)
        rig["arms"].append((sh, el, wr)); rig["fingers"].append(fl); rig["sx"].append(sx)
    # head
    head = emp(name + "_head", (0, 0, 2.28 if not adult else 2.15), body)
    if adult:
        sph((0, 0, 0), (0.42, 0.4, 0.48), skin, head, seg=32)
        sph((0, 0.04, 0.2), (0.43, 0.41, 0.34), mat((30, 25, 30)), head, seg=24)              # hair
        for sx in (-1, 1):
            sph((sx * 0.15, -0.37, 0.08), (0.075, 0.03, 0.085), mat((255, 255, 255)), head, seg=12)
            sph((sx * 0.15, -0.395, 0.07), (0.035, 0.02, 0.04), mat((20, 15, 20)), head, seg=10)
            bpy.ops.mesh.primitive_torus_add(major_radius=0.11, minor_radius=0.012, location=(sx * 0.15, -0.41, 0.08), rotation=(math.radians(90), 0, 0))
            put(bpy.context.object, mat((30, 30, 40)), head)
            box((sx * 0.15, -0.38, 0.22), (0.08, 0.02, 0.015), mat((30, 25, 30)), head)            # eyebrow
            sph((sx * 0.1, -0.38, -0.12), (0.12, 0.05, 0.04), mat((25, 20, 25)), head, seg=12)    # moustache
            sph((sx * 0.42, 0, 0.0), (0.06, 0.08, 0.1), skin, head, seg=12)                      # ears
        sph((0, -0.42, -0.02), (0.06, 0.05, 0.07), skin, head, seg=12)                           # nose
        mouth = sph((0, -0.37, -0.24), (0.09, 0.03, 0.04), mat((90, 20, 30)), head, seg=12)
        rig["mouth"] = mouth
    else:
        sph((0, 0, 0), (0.6, 0.52, 0.6), mat((255, 255, 255)), head, seg=32)
        bpy.ops.mesh.primitive_torus_add(major_radius=0.56, minor_radius=0.04, location=(0, -0.57, 0), rotation=(math.radians(90), 0, 0))
        put(bpy.context.object, mat((34, 22, 79)), head)
        bpy.ops.mesh.primitive_plane_add(size=1.08, location=(0, -0.6, 0), rotation=(math.radians(90), 0, 0))
        fp = bpy.context.object; fp.data.materials.append(face_mat("face_big.png" if kind == "big" else "face_lil.png")); fp.parent = head
    rig["head"] = head
    return rig

HOME = {"big": (-1.6, 1.3), "lil": (-0.4, 1.3), "papa": (1.9, 1.0)}
DOOR = (0, 4.4)
R = {"big": build_char("BigBro", "big", *HOME["big"]),
     "lil": build_char("LilBro", "lil", *HOME["lil"], scale=0.9),
     "papa": build_char("Papa", "papa", *HOME["papa"], scale=1.18)}

# agarbatti (lighting stick) in Papa's right hand
pw = R["papa"]["arms"][0][2]
stick = cyl((0, -0.12, -0.14), 0.012, 0.5, mat((110, 60, 30)), pw, rot=(math.radians(-70), 0, 0))
tip = sph((0, -0.36, -0.22), (0.025, 0.025, 0.025), mat((255, 120, 30), emit=30, name="tip"), pw, seg=8)
key_vis(stick, 1); key_vis(tip, 1)

# ---------------- camera ----------------
bpy.ops.object.camera_add(location=(0, -12, 3.6)); cam = bpy.context.object; sc.camera = cam
cam.data.lens = 32; cam.data.clip_end = 300
tgt = emp("cam_tgt", (0, 1, 1.8))
tc = cam.constraints.new("TRACK_TO"); tc.target = tgt; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
for k in ("big", "lil", "papa"):
    c = R[k]["head"].constraints.new("DAMPED_TRACK"); c.target = cam; c.track_axis = "TRACK_NEGATIVE_Y"

# ---------------- animation helpers ----------------
def kloc(o, f, loc=None, idx=-1):
    if loc is not None: o.location = loc
    o.keyframe_insert("location", index=idx, frame=f)
def krot(o, f, rot=None, idx=-1):
    if rot is not None: o.rotation_euler = rot
    o.keyframe_insert("rotation_euler", index=idx, frame=f)

ARM_POSES = {  # per arm: (ox, oz, fwd)  index 0 = arm at -x (character's right), 1 = +x
    "idle": [(0.16, -0.62, 0.05), (0.16, -0.62, 0.05)],
    "talk": [(0.38, -0.3, -0.35), (0.16, -0.6, 0.05)],
    "talk2": [(0.42, -0.15, -0.45), (0.16, -0.6, 0.05)],
    "cheer": [(0.3, 0.6, -0.1), (0.3, 0.6, -0.1)],
    "point": [(0.05, -0.05, -1.0), (0.16, -0.6, 0.05)],
    "point_up": [(0.15, 0.65, -0.3), (0.16, -0.6, 0.05)],
    "salute": [(-0.2, 0.62, -0.5), (0.16, -0.6, 0.05)],
    "point_big": [(0.62, 0.05, -0.2), (0.16, -0.6, 0.05)],
    "point_lil": [(0.16, -0.6, 0.05), (0.62, 0.05, -0.2)],
    "hips": [(0.2, -0.42, 0.25), (0.2, -0.42, 0.25)],
    "ears": [(0.02, 0.62, -0.05), (0.02, 0.62, -0.05)],
    "shrug": [(0.42, -0.08, -0.25), (0.42, -0.08, -0.25)],
    "laugh": [(-0.12, -0.5, -0.55), (-0.12, -0.5, -0.55)],
    "wave": [(0.32, 0.55, -0.15), (0.16, -0.6, 0.05)],
    "carry": [(-0.02, 0.0, -0.9), (-0.02, 0.0, -0.9)],
    "pat": [(0.55, 0.25, -0.3), (0.16, -0.6, 0.05)],
    "spin": [(0.62, 0.0, 0), (0.62, 0.0, 0)],
    "sparkle": [(0.3, 0.35, -0.6), (0.16, -0.6, 0.05)],
    "reach": [(0.05, -0.55, -0.9), (0.16, -0.6, 0.05)],
    "walk": [(0.16, -0.62, 0.0), (0.16, -0.62, 0.0)],
}
CURL = {"idle": 0.35, "talk": 0.15, "talk2": 0.1, "cheer": 0.05, "point": 0.2, "point_up": 0.2, "salute": 0.0, "point_big": 0.2,
        "point_lil": 0.2, "hips": 1.1, "ears": 0.25, "shrug": 0.05, "laugh": 0.9, "wave": 0.0, "carry": 0.5, "pat": 0.1,
        "spin": 0.0, "sparkle": 1.3, "reach": 1.3, "walk": 0.5}

def set_arms(who, f, pose, wob=(0, 0), fwd_add=0.0):
    rig = R[who]
    for i, ((sh, el, wr), sx) in enumerate(zip(rig["arms"], rig["sx"])):
        ox, oz, fwd = ARM_POSES[pose][i]
        ox += wob[0] if i == 0 else 0; oz += wob[1] if i == 0 else 0
        p1, rel = arm_ik(ox, oz)
        s = 1 if sx == 1 else -1      # +x arm swings with negative Y-rotation to go outward
        krot(sh, f, (fwd + fwd_add * (1 if i else -1), -s * p1, 0))
        krot(el, f, (0, -s * rel, 0))
        c = CURL[pose] if not (pose in ("point", "point_big", "point_lil", "point_up") and i == (0 if pose != "point_lil" else 1)) else 0.0
        if pose in ("point", "point_big", "point_up", "pat", "sparkle", "reach") and i == 1: c = CURL["idle"]
        for j, (k1, k2) in enumerate(rig["fingers"][i]):
            cc = c if not (pose in ("point", "point_big", "point_lil", "point_up") and j == 1 and c == 0.0) else 0
            if pose in ("point", "point_big", "point_lil", "point_up") and ((i == 0 and pose != "point_lil") or (i == 1 and pose == "point_lil")):
                cc = 0.0 if j == 1 else 1.3
            krot(k1, f, (-cc, 0, 0)); krot(k2, f, (-cc * 1.1, 0, 0))

def set_legs(who, f, a_l=0.0, k_l=0.05, a_r=0.0, k_r=0.05):
    (h0, k0), (h1, k1) = R[who]["legs"]
    krot(h0, f, (a_l, 0, 0)); krot(k0, f, (k_l, 0, 0))
    krot(h1, f, (a_r, 0, 0)); krot(k1, f, (k_r, 0, 0))

def stand(who, f):
    set_legs(who, f); kloc(R[who]["body"], f, (0, 0, 0)); krot(R[who]["body"], f, (0, 0, 0))

def walk(who, f0, f1, p0, p1, run=False, face_dir=True):
    """Move root from p0 to p1 between frames with a stepping cycle."""
    rig = R[who]; root, body = rig["root"], rig["body"]
    kloc(root, f0, (p0[0], p0[1], 0)); kloc(root, f1, (p1[0], p1[1], 0))
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    yaw = math.atan2(dx, -dy) if face_dir and (abs(dx) + abs(dy)) > 0.05 else 0.0
    krot(root, max(1, f0 - 2), (0, 0, root.rotation_euler.z)); krot(root, f0 + 3, (0, 0, yaw))
    krot(root, f1 - 2, (0, 0, yaw)); krot(root, f1 + 4, (0, 0, 0))
    P = 10 if run else 16
    A, B, bob = (0.75, 1.3, 0.12) if run else (0.45, 0.8, 0.06)
    f = f0
    i = 0
    while f < f1:
        ph = i % 4
        if ph == 0: set_legs(who, f, -A, 0.1, A, 0.35); kloc(body, f, (0, 0, 0), 2)
        elif ph == 1: set_legs(who, f, 0, 0.1, 0, B); kloc(body, f, (0, 0, bob), 2)
        elif ph == 2: set_legs(who, f, A, 0.35, -A, 0.1); kloc(body, f, (0, 0, 0), 2)
        else: set_legs(who, f, 0, B, 0, 0.1); kloc(body, f, (0, 0, bob), 2)
        # arm swing opposite to legs
        sw = [-0.5, 0, 0.5, 0][ph] * (1.4 if run else 1.0)
        set_arms(who, f, "walk", fwd_add=sw)
        krot(body, f, (math.radians(12 if run else 4), 0, 0))
        f += P // 4; i += 1
    stand(who, f1 + 2)

def talk_motion(who, f0, f1, gesture):
    rig = R[who]; body, head = rig["body"], rig["head"]
    hz = head.location.z
    k = 0; f = f0
    while f < f1:
        on = k % 2 == 0
        kloc(head, f, (0, 0, hz + (0.035 if on else 0)), 2)
        krot(body, f, (0, 0, math.radians(3 if on else -3)))
        if gesture in ("talk", "talk2"):
            set_arms(who, f, "talk" if on else "talk2")
        elif gesture in ("wave", "sparkle"):
            set_arms(who, f, gesture, wob=(0.12 * math.cos(k * 1.7), 0.12 * math.sin(k * 1.7)))
        elif gesture == "laugh":
            set_arms(who, f, "laugh"); kloc(body, f, (0, 0, 0.05 if on else 0), 2)
        else:
            set_arms(who, f, gesture)
        if "mouth" in rig:
            m = rig["mouth"]; m.scale = (0.09, 0.03, 0.07 if on else 0.02); m.keyframe_insert("scale", frame=f)
        f += 5; k += 1
    kloc(head, f1, (0, 0, hz), 2); krot(body, f1, (0, 0, 0))
    if "mouth" in rig:
        m = rig["mouth"]; m.scale = (0.09, 0.03, 0.03); m.keyframe_insert("scale", frame=f1)

def idle_all(f):
    for k in R: set_arms(k, f, "idle")

# ---------------- crackers ----------------
CR = {"anar": (0.3, -1.5), "bomb": (-0.6, -1.7), "rocket": (1.1, -1.9), "chakri": (0.1, -1.3)}
anar = cone((CR["anar"][0], CR["anar"][1], 0.2), 0.18, 0.06, 0.4, mat((230, 60, 60)))
for z in (0.1, 0.25): cyl((CR["anar"][0], CR["anar"][1], z), 0.155 - z * 0.25, 0.03, mat((255, 210, 60)))
bomb = cyl((CR["bomb"][0], CR["bomb"][1], 0.12), 0.09, 0.24, mat((200, 30, 40)))
cyl((CR["bomb"][0], CR["bomb"][1], 0.26), 0.008, 0.08, mat((230, 220, 200)))
bottle = cyl((CR["rocket"][0], CR["rocket"][1], 0.25), 0.11, 0.5, mat((80, 160, 90), rough=0.15))
rocket = emp("rocket", (CR["rocket"][0], CR["rocket"][1], 0.55))
cyl((0, 0, 0.18), 0.035, 0.28, mat((240, 60, 80)), rocket); cone((0, 0, 0.38), 0.045, 0.0, 0.12, mat((255, 220, 60)), rocket)
cyl((0.06, 0, -0.1), 0.006, 0.9, mat((150, 110, 60)), rocket)
chakri = emp("chakri", (CR["chakri"][0], CR["chakri"][1], 0.05))
bpy.ops.mesh.primitive_torus_add(major_radius=0.16, minor_radius=0.03, location=(0, 0, 0)); put(bpy.context.object, mat((60, 160, 230)), chakri)
cyl((0, 0, 0), 0.05, 0.04, mat((255, 210, 60)), chakri)
for o in (anar, bomb, bottle, rocket, chakri): o.scale = (1, 1, 1)

def ev_where(cond):
    return [e for e in TL["events"] if cond(e)]
def first(name, **kw):
    for e in TL["events"]:
        if e["type"] == "act" and e["name"] == name and all(e.get(k) == v for k, v in kw.items()): return e
def tf(e, dt=0.0): return F(e["t"] + dt)
def tend(e): return F(e["t"] + e["dur"])

# visibility windows: cracker appears when Papa announces, disappears after its scene
light_ev = {e["target"]: e for e in TL["events"] if e["type"] == "act" and e["name"] == "papa_light"}
anar_e, dud_e, launch_e, burst_e, chak_e, spin_e = first("anar"), first("dud_phuss"), first("rocket_launch"), first("rocket_burst"), first("chakri"), first("kids_spin")
spk_on, spk_wave, fin_e, end_e = first("sparklers_on"), first("sparkle_wave"), first("finale"), first("end_card")
key_vis(anar, tf(light_ev["anar"], -3), tend(anar_e) + 80)
key_vis(bomb, tf(light_ev["bomb"], -3), tend(dud_e) + 60)
key_vis(bottle, tf(light_ev["rocket"], -3), tend(burst_e) + 60)
key_vis(rocket, tf(light_ev["rocket"], -3))
key_vis(chakri, tf(light_ev["chakri"], -3), tend(spin_e) + 30)

# ---- anar fountain ----
em = emitter("anar_em", (CR["anar"][0], CR["anar"][1], 0.42), size=0.04)
particles(em, 2600, tf(anar_e), tend(anar_e) + 60, 26, inst=SPK_GOLD, normal=0, align=(0, 0, 5.2), rand=1.4, grav=1.0)
La = plight((CR["anar"][0], CR["anar"][1], 0.8), 0, (1.0, 0.75, 0.35), 0.3)
for f in range(tf(anar_e) - 1, tend(anar_e) + 66, 3):
    on = tf(anar_e) <= f <= tend(anar_e) + 60
    La.data.energy = (220 + 120 * rnd.random()) if on else 0; La.data.keyframe_insert("energy", frame=f)
# ---- fuse sparks for each lit cracker ----
def fuse(e, x, y, z, until):
    em = emitter("fuse_" + e["target"], (x, y, z), size=0.02)
    particles(em, 220, tf(e, 2.0), until, 8, inst=SPK_WHITE, normal=0, align=(0, 0, 1.2), rand=1.2, grav=0.6)
    L = plight((x, y, z + 0.2), 0, (1, 0.8, 0.5), 0.1)
    L.data.keyframe_insert("energy", frame=tf(e, 1.9)); L.data.energy = 40; L.data.keyframe_insert("energy", frame=tf(e, 2.1))
    L.data.keyframe_insert("energy", frame=until); L.data.energy = 0; L.data.keyframe_insert("energy", frame=until + 2)
fuse(light_ev["anar"], CR["anar"][0], CR["anar"][1], 0.42, tf(anar_e))
fuse(light_ev["bomb"], CR["bomb"][0], CR["bomb"][1], 0.3, tf(dud_e))
fuse(light_ev["rocket"], CR["rocket"][0], CR["rocket"][1], 0.45, tf(launch_e))
fuse(light_ev["chakri"], CR["chakri"][0], CR["chakri"][1], 0.1, tf(chak_e))
# ---- dud: tiny smoke puff ----
sm = emitter("dud_smoke", (CR["bomb"][0], CR["bomb"][1], 0.3), size=0.05)
particles(sm, 18, tf(dud_e), tf(dud_e, 0.4), 40, inst=SMOKE, normal=0, align=(0, 0, 0.6), rand=0.3, grav=-0.05, size=1.0)
# ---- rocket flight + burst ----
f_l0, f_l1 = tf(launch_e), tend(launch_e)
kloc(rocket, f_l0, (CR["rocket"][0], CR["rocket"][1], 0.55)); kloc(rocket, f_l1, (CR["rocket"][0] + 0.8, CR["rocket"][1] + 2.0, 22))
rocket.animation_data.action.fcurves[0].keyframe_points[-1].interpolation = "LINEAR"
for fc in rocket.animation_data.action.fcurves:
    for kp in fc.keyframe_points: kp.interpolation = "QUAD"
trail = emitter("trail", (0, 0, 0), rocket, size=0.02)
particles(trail, 500, f_l0, f_l1, 14, inst=SPK_ORANGE, normal=0, align=(0, 0, -1.0), rand=0.6, grav=0.4)
key_vis(rocket, f_l0 - 30, f_l1 + 1)
bx, by, bz = CR["rocket"][0] + 0.8, CR["rocket"][1] + 2.0, 22
be = emitter("burst", (bx, by, bz), kind="sphere", size=0.3)
particles(be, 900, tf(burst_e), tf(burst_e) + 2, 70, coll=FW, normal=9.0, rand=0.4, grav=0.35, drag=0.35, life_rand=0.4)
Lb = plight((bx, by, bz), 0, (1, 0.8, 0.9), 2.0)
Lb.data.keyframe_insert("energy", frame=tf(burst_e) - 1); Lb.data.energy = 60000; Lb.data.keyframe_insert("energy", frame=tf(burst_e) + 1)
Lb.data.energy = 0; Lb.data.keyframe_insert("energy", frame=tf(burst_e) + 40)
# ---- chakri spin ----
krot(chakri, tf(chak_e), (0, 0, 0)); krot(chakri, tend(spin_e) + 24, (0, 0, math.radians(360 * 40)))
for fc in chakri.animation_data.action.fcurves:
    for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
cre = emitter("chakri_em", (0, 0, 0), chakri, kind="ring", size=0.17)
particles(cre, 3000, tf(chak_e), tend(spin_e) + 20, 12, inst=SPK_GOLD, normal=0.0, rand=0.2, grav=0.3, emit_from="VERT", obj_factor=1.0)
Lc = plight((CR["chakri"][0], CR["chakri"][1], 0.5), 0, (1, 0.7, 0.3), 0.4)
Lc.data.keyframe_insert("energy", frame=tf(chak_e) - 1); Lc.data.energy = 260; Lc.data.keyframe_insert("energy", frame=tf(chak_e) + 2)
Lc.data.keyframe_insert("energy", frame=tend(spin_e) + 18); Lc.data.energy = 0; Lc.data.keyframe_insert("energy", frame=tend(spin_e) + 22)
# ---- sparklers in the kids' hands ----
sp_f0, sp_f1 = tf(spk_on, 0.6), tend(end_e)
for kid in ("big", "lil"):
    wr = R[kid]["arms"][0][2]
    s_ = cyl((0, -0.05, -0.32), 0.008, 0.5, mat((140, 140, 150)), wr, rot=(math.radians(-25), 0, 0))
    key_vis(s_, sp_f0 - 10, sp_f1)
    tipe = emitter("sparkler_" + kid, (0, -0.16, -0.55), wr, kind="sphere", size=0.03)
    particles(tipe, 2400, sp_f0, sp_f1, 9, inst=SPK_WHITE, normal=1.6, rand=1.0, grav=0.5, emit_from="FACE")
    Ls = plight((0, -0.16, -0.55), 0, (1, 0.9, 0.7), 0.1); Ls.parent = wr
    Ls.data.keyframe_insert("energy", frame=sp_f0 - 1); Ls.data.energy = 70; Ls.data.keyframe_insert("energy", frame=sp_f0 + 2)
# ---- neighbours' fireworks in the sky ----
for i, t in enumerate(TL["bg_bursts"] + [fin_e["t"] + 0.2, fin_e["t"] + 1.4, fin_e["t"] + 2.6, fin_e["t"] + 3.6, end_e["t"] + 0.4, end_e["t"] + 1.8]):
    x = rnd.uniform(-16, 16); z = rnd.uniform(14, 22)
    e2 = emitter(f"bg{i}", (x, 30, z), kind="sphere", size=0.3)
    particles(e2, 420, F(t), F(t) + 2, 60, coll=FW, normal=7.0, rand=0.4, grav=0.3, drag=0.3)

# ---------------- blocking & acting ----------------
for k, (x, y) in HOME.items():
    kloc(R[k]["root"], 1, (x, y, 0)); stand(k, 1); idle_all(1)
# kids run out of the house, papa walks in
kr = first("kids_run_in"); pw_ = first("papa_walk_in")
for k in ("big", "lil"):
    kloc(R[k]["root"], 1, (DOOR[0] + (-0.4 if k == "big" else 0.4), DOOR[1], 0))
    walk(k, tf(kr), tend(kr), (DOOR[0] + (-0.4 if k == "big" else 0.4), DOOR[1]), HOME[k], run=True)
kloc(R["papa"]["root"], 1, (DOOR[0], DOOR[1] + 0.3, 0))
kloc(R["papa"]["root"], tf(pw_) - 1, (DOOR[0], DOOR[1] + 0.3, 0))
walk("papa", tf(pw_), tend(pw_), DOOR, HOME["papa"])

for e in TL["events"]:
    f0, f1 = tf(e), tend(e)
    if e["type"] == "say":
        whos = ["big", "lil"] if e["who"] == "both" else [e["who"]]
        for wh in whos:
            g = e["gesture"]
            if g not in ARM_POSES and g not in ("talk", "spin", "carry"): g = "talk"
            talk_motion(wh, f0, f1, g)
            if g == "spin":
                krot(R[wh]["root"], f0, (0, 0, 0)); krot(R[wh]["root"], f1, (0, 0, math.radians(360)))
                krot(R[wh]["root"], f1 + 1, (0, 0, 0))
    elif e["name"] == "papa_light":
        x, y = CR[e["target"]]
        stand_pt = (x + 0.75, y + 0.35)
        walk("papa", f0, tf(e, 1.2), HOME["papa"], stand_pt)
        # bend and reach with the agarbatti
        b = R["papa"]["body"]
        krot(b, tf(e, 1.3), (0, 0, 0)); krot(b, tf(e, 1.6), (math.radians(-28), 0, 0))
        krot(R["papa"]["root"], tf(e, 1.3), (0, 0, math.radians(35)))
        set_arms("papa", tf(e, 1.3), "idle"); set_arms("papa", tf(e, 1.7), "reach"); set_arms("papa", tf(e, 2.1), "reach")
        krot(b, tf(e, 2.15), (math.radians(-28), 0, 0)); krot(b, tf(e, 2.3), (0, 0, 0))
        # comic run back
        walk("papa", tf(e, 2.25), tf(e, 2.25 + (1.4 if e["target"] != "rocket" else 1.2)), stand_pt, HOME["papa"], run=True)
        for kid in ("big", "lil"):
            set_arms(kid, f0, "idle"); set_arms(kid, tf(e, 2.0), "cheer" if e["target"] == "anar" else "idle")
    elif e["name"] == "lil_ears":
        set_arms("lil", f0, "ears"); set_arms("lil", f1 + 40, "ears")
    elif e["name"] == "anar":
        for k in ("big",):
            for j in range(0, int(e["dur"] * FPS), 8):
                set_arms(k, f0 + j, "cheer" if (j // 8) % 2 == 0 else "spin")
                kloc(R[k]["body"], f0 + j, (0, 0, 0.18 if (j // 8) % 2 == 0 else 0), 2)
        set_arms("lil", f0, "ears"); set_arms("lil", f1, "ears")
        set_arms("papa", f0, "hips"); set_arms("papa", f1, "hips")
    elif e["name"] == "all_ears_wait":
        for k in R:
            set_arms(k, f0, "ears"); set_arms(k, f1, "ears")
        # nervous shuffle
        for j in range(0, int(e["dur"] * FPS), 6):
            for k in R: krot(R[k]["body"], f0 + j, (0, 0, math.radians(4 if (j // 6) % 2 else -4)))
    elif e["name"] == "dud_phuss":
        for k in R: set_arms(k, f0, "ears"); set_arms(k, tf(e, 0.6), "shrug")
    elif e["name"] == "rocket_launch":
        # brave Big Bro jumps into Lil Bro's arms
        rb = R["big"]["root"]
        kloc(rb, f0, (HOME["big"][0], HOME["big"][1], 0)); kloc(rb, tf(e, 0.3), (HOME["lil"][0] - 0.35, HOME["lil"][1] - 0.15, 0.95))
        krot(rb, f0, (0, 0, 0)); krot(rb, tf(e, 0.3), (0, math.radians(-25), 0))
        set_arms("big", f0, "idle"); set_arms("big", tf(e, 0.25), "cheer")
        set_arms("lil", f0, "idle"); set_arms("lil", tf(e, 0.3), "carry")
        set_legs("big", tf(e, 0.3), -0.9, 1.4, -0.6, 1.2)
        set_arms("papa", f0, "point_up")
    elif e["name"] == "rocket_burst":
        set_arms("lil", f0, "carry"); set_arms("lil", f1, "carry"); set_arms("big", f0, "cheer"); set_arms("big", f1, "cheer")
        set_arms("papa", f0, "point_up"); set_arms("papa", f1, "cheer")
    elif e["name"] == "chakri":
        for k in ("big", "lil"):
            for j in range(0, int(e["dur"] * FPS), 10):
                set_arms(k, f0 + j, "cheer" if (j // 10) % 2 == 0 else "spin")
                kloc(R[k]["body"], f0 + j, (0, 0, 0.15 if (j // 10) % 2 == 0 else 0), 2)
    elif e["name"] == "kids_spin":
        for k in ("big", "lil"):
            krot(R[k]["root"], f0, (0, 0, 0)); krot(R[k]["root"], f1, (0, 0, math.radians(720 if k == "lil" else -720)))
            krot(R[k]["root"], f1 + 1, (0, 0, 0))
            set_arms(k, f0, "spin"); set_arms(k, f1, "spin")
    elif e["name"] == "sparklers_on":
        walk("papa", f0, tf(e, 1.6), HOME["papa"], (0.6, 1.1))
        HOME["papa"] = (0.6, 1.1)
        for k in ("big", "lil"): set_arms(k, f0, "idle"); set_arms(k, f1, "sparkle")
    elif e["name"] in ("sparkle_wave", "finale"):
        for k in ("big", "lil"):
            for j in range(0, int(e["dur"] * FPS), 4):
                a = j * 0.35 + (0 if k == "big" else 1.5)
                set_arms(k, f0 + j, "sparkle", wob=(0.16 * math.cos(a), 0.16 * math.sin(a)))
        set_arms("papa", f0, "hips"); set_arms("papa", f1, "cheer" if e["name"] == "finale" else "hips")
    elif e["name"] == "end_card":
        for k in R:
            for j in range(0, int(e["dur"] * FPS), 8):
                set_arms(k, f0 + j, "wave" if (j // 8) % 2 == 0 else "cheer")

# Big Bro climbs back down before he claims he wasn't scared
wb = [ev for ev in TL["events"] if ev["type"] == "say" and ev["who"] == "big" and ev["text"].startswith("I wasn't scared")][0]
rb = R["big"]["root"]
kloc(rb, tf(wb) - 8, (HOME["lil"][0] - 0.35, HOME["lil"][1] - 0.15, 0.95)); kloc(rb, tf(wb) + 4, (HOME["big"][0], HOME["big"][1], 0))
krot(rb, tf(wb) - 8, (0, math.radians(-25), 0)); krot(rb, tf(wb) + 4, (0, 0, 0)); set_legs("big", tf(wb) + 4)

# ---------------- camera shots ----------------
SH = {
    "wide": ((0, -12, 3.6), (0, 1.8, 1.8)),
    "two_kids": ((-1.0, -6.2, 2.4), (-1.0, 1.3, 1.9)),
    "big_close": ((-2.3, -3.4, 2.5), (-1.6, 1.3, 2.25)),
    "lil_close": ((0.2, -3.6, 2.3), (-0.4, 1.3, 2.05)),
    "papa_close": ((3.0, -3.0, 3.0), (1.9, 1.0, 2.6)),
    "cracker_low": ((0.9, -6.4, 0.9), (0.4, -1.4, 0.7)),
    "anar_wide": ((-0.4, -8.8, 1.5), (0.0, -0.3, 1.5)),
    "three_wait": ((0.2, -8.0, 2.0), (0.2, 0.2, 1.6)),
    "two_kids_jump": ((-0.6, -6.6, 2.6), (-0.7, 1.3, 2.4)),
    "sky": ((0.4, -9.5, 1.4), (1.9, 0.1, 18.0)),
    "chakri_top": ((0.1, -4.6, 3.2), (0.1, -1.3, 0.1)),
    "three_wide": ((0.0, -7.6, 2.3), (0.0, 0.9, 1.9)),
    "finale_crane": ((0.0, -8.5, 2.0), (0.0, 2.5, 4.5)),
}
shots = TL["shots"] + [[TL["total"], "end"]]
for i in range(len(shots) - 1):
    t0, nm = shots[i]; t1 = shots[i + 1][0]
    if nm not in SH: continue
    if nm == "papa_close":
        px, py = HOME["papa"] if t0 > first("sparklers_on")["t"] else (1.9, 1.0)
        cpos, ctgt = (px + 1.1, py - 4.0, 3.0), (px, py, 2.6)
    else:
        cpos, ctgt = SH[nm]
    f0, f1 = F(t0), max(F(t0) + 1, F(t1) - 1)
    c0 = Vector(cpos); g = Vector(ctgt)
    push = 0.1 if nm != "finale_crane" else -0.6
    c1 = c0 + (g - c0) * push
    if nm == "finale_crane": c1 = c0 + Vector((0, -4, 5))
    for (f, c) in ((f0, c0), (f1, c1)):
        cam.location = c; cam.keyframe_insert("location", frame=f)
        tgt.location = g; tgt.keyframe_insert("location", frame=f)
for o in (cam, tgt):
    for fc in o.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = "LINEAR"

bpy.ops.wm.save_as_mainfile(filepath=D + "cracker_night.blend")
print("BUILD_OK frames", N)
