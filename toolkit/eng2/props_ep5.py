# ===== Episode 5 (Fly to the Moon) props: executed inside build5 (has CH, SETS, TL, F, sets2, head_bone, Vector, Matrix, random, math, bpy) =====
import vfx
from PIL import Image, ImageDraw, ImageFont
def key_vis(obj, f, v):
    for o in [obj] + list(obj.children_recursive):
        o.hide_render = not v; o.hide_viewport = not v
        o.keyframe_insert("hide_render", frame=f); o.keyframe_insert("hide_viewport", frame=f)
def const_keys(obj):
    if obj.animation_data and obj.animation_data.action:
        for fc in obj.animation_data.action.fcurves:
            for kp in fc.keyframe_points: kp.interpolation = "CONSTANT"
def puff(loc, f, n=7, size=0.07, rise=0.6, spread=0.08, life=36, coll=None, mat=None):
    rnd = random.Random(f)
    for i in range(n):
        s_ = sets2.sph(f"puff5_{f}_{i}", size, loc, mat, coll, seg=12)
        t0 = f + i * 2
        s_.scale = (0.01, 0.01, 0.01); s_.keyframe_insert("scale", frame=max(1, t0 - 1)); s_.keyframe_insert("location", frame=max(1, t0 - 1))
        s_.location = Vector(loc) + Vector((rnd.uniform(-spread, spread), rnd.uniform(-spread, spread), 0.05))
        s_.scale = (1, 1, 1); s_.keyframe_insert("scale", frame=t0 + 4); s_.keyframe_insert("location", frame=t0 + 4)
        s_.location = Vector(loc) + Vector((rnd.uniform(-spread, spread) * 3, rnd.uniform(-spread, spread) * 3, rise))
        s_.scale = (2.2, 2.2, 2.2); s_.keyframe_insert("location", frame=t0 + life * 0.7); s_.keyframe_insert("scale", frame=t0 + life * 0.7)
        s_.scale = (0.01, 0.01, 0.01); s_.keyframe_insert("scale", frame=t0 + life)

coll_p = sets2.col("props")
living = SETS.get("living"); night = SETS.get("balcony_night"); moon = SETS.get("moon"); kitchen = SETS.get("kitchen")
smoke_m = sets2.M("smoke5", (0.9, 0.9, 0.92), 1.0, alpha=0.4)
steam_m = sets2.M("steam5", (1.0, 1.0, 1.0), 1.0, alpha=0.3)

# ---- big Sharad Purnima moon on the night balcony + a camera for it ----
if night:
    On = night["origin"]; mo = bpy.data.objects.get("balcony_night_moon")
    if mo:
        mo.scale = (3.2, 3.2, 3.2); mo.location = (On.x - 9.0, On.y + 86, 27.0)
    night["cams"]["insert:moon"] = ((On.x + 0.2, On.y + 0.5, 1.3), (On.x - 9.0, On.y + 86, 27.0), 38)
    # a soft extra moon fill so faces read under the big moon
    sets2.area("bn_moonfill5", (On.x - 2.0, On.y - 2.5, 2.4), (On.x, On.y + 0.4, 0.9), 70, 4.0, night["coll"], (0.7, 0.78, 1.0))

# ---- pillow rocket: ring of cushions + block fins + lampshade nose, grouped under an empty ----
CUSH = [(0.85, 0.30, 0.35), (0.95, 0.75, 0.25), (0.35, 0.60, 0.90), (0.45, 0.75, 0.40), (0.90, 0.50, 0.70), (0.95, 0.60, 0.30)]
def rocket_build(prefix, center, coll, visible_from=None, step=8):
    grp = bpy.data.objects.new(prefix + "_grp", None); coll.objects.link(grp); grp.location = center
    parts = []
    for i, cc in enumerate(CUSH):
        a = i / 6 * 2 * math.pi + math.pi / 6
        m = sets2.M(f"{prefix}_cush{i}", cc, 0.9, bump=0.5, bump_scale=300)
        b = sets2.box(f"{prefix}_cush{i}", (0.62, 0.22, 0.42), (math.cos(a) * 0.95, math.sin(a) * 0.95, 0.21), m, coll, 0.07, rot=(0, 0, a + math.pi / 2))
        parts.append(b)
    for i, cc in enumerate([(0.9, 0.2, 0.2), (0.2, 0.5, 0.9), (0.95, 0.8, 0.2), (0.3, 0.7, 0.3)]):
        a = i / 4 * 2 * math.pi
        m = sets2.M(f"{prefix}_fin{i}", cc, 0.5, coat=0.3)
        parts.append(sets2.box(f"{prefix}_fin{i}", (0.13, 0.4, 0.13), (math.cos(a) * 1.25, math.sin(a) * 1.25, 0.07), m, coll, 0.01, rot=(0, 0, a)))
    pole = sets2.cyl(f"{prefix}_pole", 0.02, 1.5, (0, 0.95, 1.0), sets2.M(f"{prefix}_polem", (0.12, 0.12, 0.13), 0.35, 1.0), coll)
    cone = sets2.cyl(f"{prefix}_cone", 0.28, 0.4, (0, 0.95, 1.9), sets2.M(f"{prefix}_conem", (1, 0.95, 0.85), 0.6, emit=(1, 0.85, 0.6), emit_str=1.2), coll)
    cone.scale = (1, 1, 1)
    tip = sets2.sph(f"{prefix}_tip", 0.1, (0, 0.95, 2.18), sets2.M(f"{prefix}_tipm", (0.95, 0.3, 0.3), 0.3, coat=0.5), coll)
    parts += [pole, cone, tip]
    for p_ in parts: p_.parent = grp
    if visible_from is not None:
        for i, p_ in enumerate(parts):
            key_vis(p_, 1, False); key_vis(p_, visible_from + i * step, True); const_keys(p_)
    return grp, parts
def rocket_launch(grp, f, coll, up=3.5, dur=28):
    grp.keyframe_insert("location", frame=f)
    loc0 = Vector(grp.location)
    for k in range(6):   # shake
        grp.location = loc0 + Vector((random.Random(f + k).uniform(-0.04, 0.04), 0, 0)); grp.keyframe_insert("location", frame=f + 2 + k * 2)
    grp.location = loc0; grp.keyframe_insert("location", frame=f + 14)
    grp.location = loc0 + Vector((0, 0, up)); grp.keyframe_insert("location", frame=f + 14 + dur)
    for i in range(3): puff((loc0.x + random.Random(i).uniform(-0.5, 0.5), loc0.y + random.Random(i + 9).uniform(-0.5, 0.5), 0.1), f + 12 + i * 3, n=10, size=0.12, rise=0.9, spread=0.25, life=40, coll=coll, mat=smoke_m)
    vfx.flash(f"{grp.name}_flash", (loc0.x, loc0.y, 0.3), coll, f + 14, 400, color=(1, 0.75, 0.4), dur=10)

rockets = {}
if living:
    Ol = living["origin"]; rockets["living"] = rocket_build("rkt_l", (Ol.x + 0.0, Ol.y + 0.3, 0.0), living["coll"], visible_from=None)
    living["cams"]["insert:rocket"] = ((Ol.x - 1.6, Ol.y - 2.4, 1.1), (Ol.x + 0.0, Ol.y + 0.5, 0.7), 32)
    living["cams"]["low_wide"] = ((Ol.x - 0.3, Ol.y - 3.4, 0.5), (Ol.x + 0.2, Ol.y + 0.8, 1.0), 24)
    living["cams"]["dance_orbit"] = living["cams"]["living_wide"]
if moon:
    Om = moon["origin"]; rockets["moon"] = rocket_build("rkt_m", (Om.x - 2.9, Om.y + 1.6, 0.0), moon["coll"], visible_from=None)
    # footprint near Buddy's spot
    fpm = sets2.M("footprint5", (0.28, 0.28, 0.27), 0.95)
    for i, (dx, dy) in enumerate(((0.0, 0.0), (0.13, 0.3))):
        sets2.box(f"moon_fp{i}", (0.11, 0.26, 0.012), (Om.x + 2.2 + dx, Om.y - 0.4 + dy, 0.0), fpm, moon["coll"], 0.004, rot=(0, 0, 0.3))
    # moon-phase screen (floating "space screen" plane with a generated texture)
    W_, H_ = 1200, 700; im = Image.new("RGB", (W_, H_), (8, 10, 30)); d = ImageDraw.Draw(im)
    try: fnt = ImageFont.truetype("/home/claude/bbf/assets/Fredoka.ttf", 56); fnt2 = ImageFont.truetype("/home/claude/bbf/assets/Fredoka.ttf", 40)
    except Exception: fnt = fnt2 = ImageFont.load_default()
    d.text((W_ // 2, 60), "WHY DOES THE MOON CHANGE SHAPE?", font=fnt, fill=(255, 220, 90), anchor="mm")
    labels = ["NEW MOON", "CRESCENT", "HALF MOON", "FULL MOON"]
    for i, lab in enumerate(labels):
        cx, cy, r = 160 + i * 295, 360, 105
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(40, 42, 60), outline=(120, 130, 170), width=4)
        if i == 1: d.pieslice((cx - r, cy - r, cx + r, cy + r), 270, 90, fill=(255, 245, 200)); d.ellipse((cx - r * 0.55 - r, cy - r, cx + r - r * 0.55, cy + r), fill=(40, 42, 60)) if False else None; d.ellipse((cx - r * 1.45, cy - r, cx + r * 0.55, cy + r), fill=(40, 42, 60))
        if i == 2: d.pieslice((cx - r, cy - r, cx + r, cy + r), 270, 90, fill=(255, 245, 200))
        if i == 3: d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 245, 200))
        d.text((cx, cy + r + 50), lab, font=fnt2, fill=(220, 230, 255), anchor="mm")
    d.text((W_ // 2, H_ - 70), "The sun lights one half of the moon. We see more of it each night!", font=fnt2, fill=(160, 200, 255), anchor="mm")
    sp = f"{EP}/mtex/moon_screen.png"; os.makedirs(os.path.dirname(sp), exist_ok=True); im.save(sp)
    scm = sets2.M("moon_screen_m", (1, 1, 1), 0.4)
    nt = scm.node_tree; p_ = nt.nodes["Principled BSDF"]; t_ = nt.nodes.new("ShaderNodeTexImage"); t_.image = bpy.data.images.load(sp)
    nt.links.new(t_.outputs["Color"], p_.inputs["Base Color"]); nt.links.new(t_.outputs["Color"], p_.inputs["Emission Color"]); p_.inputs["Emission Strength"].default_value = 1.6
    screen = sets2.plane("moon_screen", (1.5, 0.875), (Om.x + 2.1, Om.y + 1.6, 1.25), scm, moon["coll"], rot=(math.radians(90), 0, 0))
    frame_ = sets2.box("moon_screenf", (1.58, 0.04, 0.95), (Om.x + 2.1, Om.y + 1.62, 1.25), sets2.M("screen_frame", (0.8, 0.82, 0.9), 0.3, 0.8), moon["coll"], 0.01)
    key_vis(screen, 1, False); key_vis(frame_, 1, False)
if kitchen:
    Ok = kitchen["origin"]; cx_, cy_, cz_ = kitchen["cooker"]
    # hide the pressure cooker, put a wide pot of kheer on the burner
    for nm in ("kitchen_cooker", "kitchen_cookerlid", "kitchen_cookhandle"):
        ob = bpy.data.objects.get(nm)
        if ob: ob.hide_render = True; ob.hide_viewport = True
    steel = bpy.data.materials.get("steel") or sets2.M("steel5", (0.66, 0.68, 0.72), 0.2, coat=0.7)
    pot = sets2.cyl("kheer_pot", 0.17, 0.16, (cx_, cy_, 1.08), steel, kitchen["coll"], 32)
    sets2.cyl("kheer_top", 0.16, 0.01, (cx_, cy_, 1.16), sets2.M("kheer_m", (0.98, 0.95, 0.85), 0.35, coat=0.6), kitchen["coll"], 32, bevel=0)
    for i in range(2): sets2.box(f"kheer_handle{i}", (0.05, 0.03, 0.02), (cx_ + (0.19 if i else -0.19), cy_, 1.12), steel, kitchen["coll"], 0.005)
    for i in range(6): sets2.sph(f"kheer_nut{i}", 0.012, (cx_ + random.Random(i).uniform(-0.1, 0.1), cy_ + random.Random(i + 5).uniform(-0.1, 0.1), 1.17), sets2.M("kheer_nut", (0.55, 0.35, 0.15), 0.6), kitchen["coll"], seg=8)
    for ob in list(kitchen.get("tiffins", {}).values()): key_vis(ob, 1, False)
    TX, TY, TZ = kitchen["table"]; bowls_k = []
    for i in range(5):
        bw = sets2.cyl(f"kbowl{i}", 0.06, 0.05, (TX - 0.4 + i * 0.2, TY + 0.05, TZ + 0.025), steel, kitchen["coll"], 24)
        kt = sets2.cyl(f"kbowlt{i}", 0.055, 0.008, (TX - 0.4 + i * 0.2, TY + 0.05, TZ + 0.05), bpy.data.materials["kheer_m"], kitchen["coll"], 24, bevel=0)
        bowls_k += [bw, kt]
    for ob in bowls_k: key_vis(ob, 1, False)
    kitchen["cams"]["insert:bowls"] = ((TX - 0.5, TY - 0.9, TZ + 0.5), (TX, TY + 0.05, TZ + 0.05), 40)
if night:
    On = night["origin"]; steel = bpy.data.materials.get("steel") or sets2.M("steel5b", (0.66, 0.68, 0.72), 0.2, coat=0.7)
    kheer_m = bpy.data.materials.get("kheer_m") or sets2.M("kheer_m", (0.98, 0.95, 0.85), 0.35, coat=0.6)
    bowls_b = []
    for i, x in enumerate((0.0, -1.1, 1.1, -2.0, 2.0)):
        bw = sets2.cyl(f"bbowl{i}", 0.07, 0.05, (On.x + x, On.y + 0.1, 0.025), steel, night["coll"], 24)
        kt = sets2.cyl(f"bbowlt{i}", 0.065, 0.008, (On.x + x, On.y + 0.1, 0.05), kheer_m, night["coll"], 24, bevel=0)
        bowls_b += [bw, kt]
    for ob in bowls_b: key_vis(ob, 1, False)

for e in TL["events"]:
    if e["type"] != "prop": continue
    f = F(e["t"]); nm = e["name"]; a = e["action"]; who = e.get("who")
    if nm == "rocket" and a == "build" and living:
        grp, parts = rockets["living"]
        for i, p_ in enumerate(parts): key_vis(p_, 1, False); key_vis(p_, f + 4 + i * 6, True); const_keys(p_)
    elif nm == "rocket" and a == "launch":
        s_ = scene_at(f)["set"]
        if s_ in rockets: rocket_launch(rockets[s_][0], f + 4, SETS[s_]["coll"])
    elif nm == "rocket" and a == "landed" and moon:
        pass   # the moon copy is visible from the start of the moon scene
    elif nm == "buddy" and a == "float":
        arm = CH["buddy"]["arm"]
        arm.delta_location = (0, 0, 0); arm.keyframe_insert("delta_location", frame=f)
        arm.delta_location = (0, 0, 0.55); arm.keyframe_insert("delta_location", frame=f + 22)
        arm.delta_location = (0, 0, 0.45); arm.keyframe_insert("delta_location", frame=f + 48)
        arm.delta_location = (0, 0, 0.0); arm.keyframe_insert("delta_location", frame=f + 70)
    elif nm == "screen" and a == "phases" and moon:
        key_vis(bpy.data.objects["moon_screen"], f, True); key_vis(bpy.data.objects["moon_screenf"], f, True)
        vfx.flash("screen_flash", (moon["origin"].x + 2.1, moon["origin"].y + 1.2, 1.25), moon["coll"], f, 60, color=(0.6, 0.8, 1.0), dur=8)
    elif nm == "kheer" and a == "pot" and kitchen:
        for k_ in range(6): puff((cx_, cy_, 1.2), f + 10 + k_ * 40, n=4, size=0.025, rise=0.45, spread=0.03, life=48, coll=kitchen["coll"], mat=steam_m)
    elif nm == "kheer" and a == "bowls" and kitchen:
        for ob in bowls_k: key_vis(ob, f + 8, True)
    elif nm == "kheer" and a == "balcony" and night:
        for ob in bowls_b: key_vis(ob, f, True)
    elif nm in ("moon", "city"):
        pass
for ob in bpy.data.objects:
    if ob.name.startswith(("kbowl", "bbowl", "moon_screen")): const_keys(ob)
