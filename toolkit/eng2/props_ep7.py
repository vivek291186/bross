# ===== Episode 7 (Park Treasure Hunt) props: executed inside build6/7 (has CH, SETS, TL, F, sets2, Vector, random, math, bpy, scene_at, EP, vfx) =====
import vfx, os
from PIL import Image, ImageDraw, ImageFont
def key_vis(obj, f, v):
    for o in [obj] + list(obj.children_recursive):
        o.hide_render = not v; o.hide_viewport = not v
        o.keyframe_insert("hide_render", frame=f); o.keyframe_insert("hide_viewport", frame=f)
def const_keys(obj):
    if obj.animation_data and obj.animation_data.action:
        for fc in obj.animation_data.action.fcurves:
            for kp in fc.keyframe_points: kp.interpolation = "CONSTANT"
def img_mat(name, path, emit=0.6):
    m = sets2.M(name, (1, 1, 1), 0.6); nt = m.node_tree; p_ = nt.nodes["Principled BSDF"]
    t_ = nt.nodes.new("ShaderNodeTexImage"); t_.image = bpy.data.images.load(path)
    nt.links.new(t_.outputs["Color"], p_.inputs["Base Color"]); nt.links.new(t_.outputs["Color"], p_.inputs["Emission Color"]); p_.inputs["Emission Strength"].default_value = emit
    nt.links.new(t_.outputs["Alpha"], p_.inputs["Alpha"]); m.blend_method = "HASHED"
    return m
try: FNT = ImageFont.truetype("/home/claude/bbf/assets/Fredoka.ttf", 54); FNT2 = ImageFont.truetype("/home/claude/bbf/assets/Fredoka.ttf", 40)
except Exception: FNT = FNT2 = ImageFont.load_default()
MT = f"{EP}/mtex"; os.makedirs(MT, exist_ok=True)
living = SETS.get("living"); park = SETS.get("park")

# ---- treasure map (parchment with doodles) ----
def map_img(path):
    im = Image.new("RGBA", (800, 560), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 10, 790, 550), 30, fill=(236, 214, 160, 255), outline=(120, 80, 30, 255), width=8)
    d.text((400, 60), "TREASURE MAP", font=FNT, fill=(110, 60, 20), anchor="mm")
    pts = [(120, 420), (250, 300), (420, 360), (560, 220), (660, 300)]
    for a, b in zip(pts, pts[1:]):
        for i in range(0, 10, 2):
            t0 = i / 10; t1 = (i + 1) / 10
            d.line([(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0), (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)], fill=(150, 60, 40), width=6)
    d.text((120, 470), "SWINGS", font=FNT2, fill=(60, 40, 20), anchor="mm"); d.text((420, 410), "DUCKS", font=FNT2, fill=(60, 40, 20), anchor="mm"); d.text((560, 170), "SLIDE", font=FNT2, fill=(60, 40, 20), anchor="mm")
    d.line([(640, 280), (680, 320)], fill=(200, 30, 30), width=10); d.line([(680, 280), (640, 320)], fill=(200, 30, 30), width=10)
    d.text((400, 510), "Where the swings fly high, the first clue waits nearby", font=FNT2, fill=(90, 50, 20), anchor="mm")
    im.save(path)
def card_img(path, txt):
    im = Image.new("RGBA", (800, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 8, 792, 292), 40, fill=(255, 250, 230, 255), outline=(200, 60, 90, 255), width=10)
    d.text((400, 110), "CLUE!", font=FNT, fill=(200, 60, 90), anchor="mm"); d.text((400, 200), txt, font=FNT2, fill=(50, 40, 60), anchor="mm")
    im.save(path)

if living:
    O = living["origin"]; c = living["coll"]
    mp = f"{MT}/map7.png"; map_img(mp)
    mapo = sets2.plane("map7", (0.5, 0.35), (O.x + 1.6, O.y + 0.6, 0.43), img_mat("map7_m", mp, 0.5), c, rot=(0, 0, math.radians(-12)))
    key_vis(mapo, 1, False)
    living["cams"]["insert:map"] = ((O.x + 1.4, O.y - 0.4, 1.25), (O.x + 1.6, O.y + 0.6, 0.43), 40)
if park:
    Op = park["origin"]; cp = park["coll"]; SX, SY = park["slide"]; PX, PY = park["pond"]
    # clue card under the swings
    cl = f"{MT}/clue7.png"; card_img(cl, "Three yellow friends who paddle and float...")
    clue = sets2.plane("clue7", (0.5, 0.19), (Op.x - 2.8, Op.y + 3.1, 0.3), img_mat("clue7_m", cl, 0.8), cp, rot=(math.radians(75), 0, math.radians(10)))
    key_vis(clue, 1, False)
    # paper boat on the pond
    boat = bpy.data.objects.new("boat7", None); cp.objects.link(boat); boat.location = (PX + 1.1, PY + 0.9, 0.04)
    pm = sets2.M("paper7", (0.98, 0.98, 0.95), 0.7)
    for i, (sz, loc) in enumerate((((0.22, 0.09, 0.03), (0, 0, 0.015)), ((0.12, 0.02, 0.12), (0, 0, 0.08)), ((0.1, 0.1, 0.02), (0, 0, 0.14)))):
        b_ = sets2.box(f"boat7_{i}", sz, loc, pm, cp, 0.003); b_.parent = boat
    key_vis(boat, 1, False)
    # treasure chest under the slide + coins + glow
    chest = bpy.data.objects.new("chest7", None); cp.objects.link(chest); chest.location = (SX, SY + 0.2, 0.0)
    wood = sets2.M_wood("chest7_w", (0.5, 0.3, 0.12), (0.35, 0.2, 0.08), scale=5); gold = sets2.M("chest7_gold", (1.0, 0.8, 0.25), 0.25, 0.9)
    body = sets2.box("chest7_body", (0.5, 0.34, 0.26), (0, 0, 0.13), wood, cp, 0.015); body.parent = chest
    for i in range(2): b_ = sets2.box(f"chest7_band{i}", (0.04, 0.36, 0.28), (-0.15 + i * 0.3, 0, 0.13), gold, cp, 0.004); b_.parent = chest
    lid = bpy.data.objects.new("chest7_lid", None); cp.objects.link(lid); lid.location = (0, 0.17, 0.26); lid.parent = chest
    l_ = sets2.box("chest7_lidb", (0.5, 0.34, 0.1), (0, -0.17, 0.05), wood, cp, 0.015); l_.parent = lid
    for i in range(2): b_ = sets2.box(f"chest7_lband{i}", (0.04, 0.36, 0.12), (-0.15 + i * 0.3, -0.17, 0.05), gold, cp, 0.004); b_.parent = lid
    coins = []
    rnd = random.Random(77)
    for i in range(18):
        cn = sets2.cyl(f"chest7_coin{i}", 0.035, 0.008, (rnd.uniform(-0.18, 0.18), rnd.uniform(-0.1, 0.1), 0.2 + rnd.uniform(0, 0.06)), gold, cp, 16, bevel=0, rot=(rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4), 0)); cn.parent = chest; coins.append(cn)
    glow = sets2.sph("chest7_glow", 0.2, (0, 0, 0.3), sets2.M("chest7_glm", (1, 0.9, 0.5), 0.5, emit=(1.0, 0.85, 0.4), emit_str=6.0, alpha=0.35), cp, seg=16); glow.parent = chest
    key_vis(chest, 1, False); key_vis(glow, 1, False)
    park["cams"]["insert:chest"] = ((SX - 1.3, SY - 1.6, 0.9), (SX, SY + 0.2, 0.2), 38)
    # dark cloud group that rolls in + a "shadow" figure behind the big tree
    cloudm = sets2.M("park_darkcloud", (0.35, 0.36, 0.4), 0.9, emit=(0.3, 0.3, 0.35), emit_str=0.5)
    dark = bpy.data.objects.new("darkcloud7", None); cp.objects.link(dark)
    for j in range(7):
        s_ = sets2.sph(f"darkcloud7_{j}", rnd.uniform(4, 7), (rnd.uniform(-9, 9), rnd.uniform(-3, 3), rnd.uniform(-1, 2)), cloudm, cp, seg=12, scale=(1.5, 1.0, 0.7)); s_.parent = dark
    dark.location = (Op.x - 110, Op.y + 95, 34); key_vis(dark, 1, False)
    shadow = sets2.box("shadow7", (0.5, 0.25, 1.5), (Op.x + 7.9, Op.y + 6.6, 0.75), sets2.M("shadow7_m", (0.08, 0.08, 0.1), 0.9), cp, 0.1)
    sh_head = sets2.sph("shadow7_h", 0.22, (Op.x + 7.9, Op.y + 6.6, 1.7), sets2.M("shadow7_m", (0.08, 0.08, 0.1), 0.9), cp, seg=12)
    key_vis(shadow, 1, False); key_vis(sh_head, 1, False)
    sunl = bpy.data.objects.get("park_sunlight")

for e in TL["events"]:
    if e["type"] != "prop": continue
    f = F(e["t"]); nm = e["name"]; a = e["action"]
    if nm == "map" and a == "found" and living:
        key_vis(mapo, f, True)
        mapo.scale = (0.01, 0.01, 0.01); mapo.keyframe_insert("scale", frame=f); mapo.scale = (1.15, 1.15, 1.15); mapo.keyframe_insert("scale", frame=f + 6); mapo.scale = (1, 1, 1); mapo.keyframe_insert("scale", frame=f + 10)
        vfx.flash("map7_fl", (living["origin"].x + 1.6, living["origin"].y + 0.6, 0.7), living["coll"], f + 2, 30, color=(1.0, 0.9, 0.6), dur=10)
    elif nm == "clue" and a == "swings" and park:
        key_vis(clue, f, True)
        clue.scale = (0.01, 0.01, 0.01); clue.keyframe_insert("scale", frame=f); clue.scale = (1.2, 1.2, 1.2); clue.keyframe_insert("scale", frame=f + 6); clue.scale = (1, 1, 1); clue.keyframe_insert("scale", frame=f + 10)
        vfx.flash("clue7_fl", (Op.x - 2.8, Op.y + 3.1, 0.5), cp, f + 2, 25, color=(1.0, 0.8, 0.9), dur=10)
    elif nm == "boat" and a == "show" and park:
        key_vis(boat, f, True)
        for ff in range(f, f + 400, 12):
            boat.location = (PX + 1.1 + 0.03 * math.sin(ff / 9.0), PY + 0.9, 0.04 + 0.01 * math.sin(ff / 6.0)); boat.rotation_euler = (0.05 * math.sin(ff / 7.0), 0, 0.2)
            boat.keyframe_insert("location", frame=ff); boat.keyframe_insert("rotation_euler", frame=ff)
    elif nm == "sky" and a == "cloud" and park:
        key_vis(dark, f, True)
        dark.location = (Op.x - 110, Op.y + 95, 34); dark.keyframe_insert("location", frame=f)
        dark.location = (Op.x - 25, Op.y + 90, 32); dark.keyframe_insert("location", frame=f + 140)
        dark.location = (Op.x + 10, Op.y + 85, 30); dark.keyframe_insert("location", frame=f + 1400)
        if sunl:
            sunl.data.energy = 4.5; sunl.data.keyframe_insert("energy", frame=f + 40)
            sunl.data.energy = 2.6; sunl.data.keyframe_insert("energy", frame=f + 160)
            sunl.data.color = (1.0, 0.95, 0.85); sunl.data.keyframe_insert("color", frame=f + 40)
            sunl.data.color = (0.8, 0.85, 0.95); sunl.data.keyframe_insert("color", frame=f + 160)
    elif nm == "buddy" and a == "climb" and park:
        arm = CH["buddy"]["arm"]
        # walk the ladder: snap root to the ladder foot then rise to the platform
        arm.delta_location = (0, 0, 0); arm.keyframe_insert("delta_location", frame=f)
        arm.delta_location = (0, 0, 1.3); arm.keyframe_insert("delta_location", frame=f + 48)
        arm.delta_location = (0, 0, 1.3); arm.keyframe_insert("delta_location", frame=f + 200)
    elif nm == "buddy" and a == "slide" and park:
        arm = CH["buddy"]["arm"]
        arm.delta_location = (0, 0, 1.3); arm.keyframe_insert("delta_location", frame=f)
        arm.delta_location = (0, -1.6, 0.55); arm.keyframe_insert("delta_location", frame=f + 14)
        arm.delta_location = (0, -2.6, 0.0); arm.keyframe_insert("delta_location", frame=f + 26)
        arm.delta_location = (0, -2.6, 0.0); arm.keyframe_insert("delta_location", frame=f + 60)
        arm.delta_location = (0, 0, 0); arm.keyframe_insert("delta_location", frame=f + 80)
        for k_ in range(3):
            s_ = sets2.sph(f"slide7_puff{k_}", 0.06, (SX, SY - 1.4 + k_ * 0.2, 0.3), sets2.M("slide7_puffm", (0.95, 0.9, 0.8), 1.0, alpha=0.5), cp, seg=10)
            key_vis(s_, 1, False); key_vis(s_, f + 20 + k_ * 3, True); key_vis(s_, f + 50 + k_ * 3, False)
            s_.scale = (0.3, 0.3, 0.3); s_.keyframe_insert("scale", frame=f + 20 + k_ * 3); s_.scale = (3, 3, 3); s_.keyframe_insert("scale", frame=f + 50 + k_ * 3)
    elif nm == "chest" and a == "show" and park:
        key_vis(chest, f, True); key_vis(glow, f, False)
        vfx.flash("chest7_fl", (SX, SY + 0.2, 0.5), cp, f + 2, 30, color=(1.0, 0.85, 0.4), dur=10)
    elif nm == "chest" and a == "open" and park:
        lid.rotation_euler = (0, 0, 0); lid.keyframe_insert("rotation_euler", frame=f + 6)
        lid.rotation_euler = (math.radians(-110), 0, 0); lid.keyframe_insert("rotation_euler", frame=f + 22)
        key_vis(glow, f + 14, True)
        glow.scale = (0.2, 0.2, 0.2); glow.keyframe_insert("scale", frame=f + 14); glow.scale = (1.6, 1.6, 1.6); glow.keyframe_insert("scale", frame=f + 30); glow.scale = (1.2, 1.2, 1.2); glow.keyframe_insert("scale", frame=f + 60)
        vfx.flash("chest7_fl2", (SX, SY + 0.2, 0.6), cp, f + 16, 90, color=(1.0, 0.85, 0.4), dur=18)
        vfx.emitter("chest7_spk", (SX, SY + 0.2, 0.35), cp, 140, f + 16, f + 40, 40, (1.0, 0.85, 0.4), size=0.012, vel_rand=1.4, gravity=0.3, strength=30.0, radius=0.15)
    elif nm == "shadow" and a == "tree" and park:
        key_vis(shadow, f, True); key_vis(sh_head, f, True)
        for ob in (shadow, sh_head):
            ob.delta_location = (0.6, 0, 0); ob.keyframe_insert("delta_location", frame=f)
            ob.delta_location = (0.0, 0, 0); ob.keyframe_insert("delta_location", frame=f + 20)
            ob.delta_location = (0.6, 0, 0); ob.keyframe_insert("delta_location", frame=f + 48)
for ob in bpy.data.objects:
    if ob.animation_data and ob.animation_data.action and ob.name.startswith(("map7", "clue7", "boat7", "chest7", "darkcloud7", "shadow7", "slide7")):
        for fc in ob.animation_data.action.fcurves:
            if "hide" in fc.data_path:
                for kp in fc.keyframe_points: kp.interpolation = "CONSTANT"
