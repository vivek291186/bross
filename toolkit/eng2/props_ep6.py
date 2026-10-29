# ===== Episode 6 (Guess the Sound) props: executed inside build6 (has CH, SETS, TL, F, sets2, Vector, random, math, bpy, scene_at, EP) =====
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
def puff(loc, f, n=7, size=0.07, rise=0.6, spread=0.08, life=36, coll=None, mat=None):
    rnd = random.Random(f)
    for i in range(n):
        s_ = sets2.sph(f"puff6_{f}_{i}", size, loc, mat, coll, seg=12)
        t0 = f + i * 2
        s_.scale = (0.01, 0.01, 0.01); s_.keyframe_insert("scale", frame=max(1, t0 - 1)); s_.keyframe_insert("location", frame=max(1, t0 - 1))
        s_.location = Vector(loc) + Vector((rnd.uniform(-spread, spread), rnd.uniform(-spread, spread), 0.05))
        s_.scale = (1, 1, 1); s_.keyframe_insert("scale", frame=t0 + 4); s_.keyframe_insert("location", frame=t0 + 4)
        s_.location = Vector(loc) + Vector((rnd.uniform(-spread, spread) * 3, rnd.uniform(-spread, spread) * 3, rise))
        s_.scale = (2.2, 2.2, 2.2); s_.keyframe_insert("location", frame=t0 + life * 0.7); s_.keyframe_insert("scale", frame=t0 + life * 0.7)
        s_.scale = (0.01, 0.01, 0.01); s_.keyframe_insert("scale", frame=t0 + life)

living = SETS.get("living"); balcony = SETS.get("balcony"); kitchen = SETS.get("kitchen")
steam_m = sets2.M("steam6", (1.0, 1.0, 1.0), 1.0, alpha=0.3)
try: FNT = ImageFont.truetype("/home/claude/bbf/assets/Fredoka.ttf", 64); FNT2 = ImageFont.truetype("/home/claude/bbf/assets/Fredoka.ttf", 46)
except Exception: FNT = FNT2 = ImageFont.load_default()
MT = f"{EP}/mtex"; os.makedirs(MT, exist_ok=True)
def img_mat(name, path, emit=1.2):
    m = sets2.M(name, (1, 1, 1), 0.5); nt = m.node_tree; p_ = nt.nodes["Principled BSDF"]
    t_ = nt.nodes.new("ShaderNodeTexImage"); t_.image = bpy.data.images.load(path)
    nt.links.new(t_.outputs["Color"], p_.inputs["Base Color"]); nt.links.new(t_.outputs["Color"], p_.inputs["Emission Color"]); p_.inputs["Emission Strength"].default_value = emit
    nt.links.new(t_.outputs["Alpha"], p_.inputs["Alpha"]); m.blend_method = "HASHED"
    return m

ICON = {"bell": ("DOORBELL", (255, 210, 80)), "cat": ("CAT", (255, 160, 90)), "rain": ("RAIN", (120, 190, 255)), "drum": ("DRUM", (255, 120, 120)), "laugh": ("BRO BROS!", (255, 120, 200))}
if living:
    O = living["origin"]; c = living["coll"]
    BX, BY, BZ = O.x + 1.35, O.y + 0.55, 0.40
    # ---- mystery sound box: bright box with a big "?" on every side, lid on top ----
    bm = sets2.M("box6_m", (0.95, 0.35, 0.45), 0.45, coat=0.4); lm = sets2.M("box6_lid", (0.98, 0.78, 0.2), 0.4, coat=0.5)
    qm = sets2.M("box6_q", (1.0, 1.0, 1.0), 0.4, emit=(1, 1, 0.9), emit_str=0.8)
    grp = bpy.data.objects.new("box6_grp", None); c.objects.link(grp); grp.location = (BX, BY, BZ)
    body = sets2.box("box6_body", (0.42, 0.42, 0.34), (0, 0, 0.17), bm, c, 0.02)
    lid = sets2.box("box6_lidb", (0.46, 0.46, 0.06), (0, 0, 0.37), lm, c, 0.015)
    knob = sets2.sph("box6_knob", 0.04, (0, 0, 0.42), lm, c)
    parts = [body, lid, knob]
    for i, (dx, dy, rz) in enumerate(((0, -0.215, 0), (-0.215, 0, math.pi / 2), (0.215, 0, -math.pi / 2))):
        tq = sets2.text(f"box6_q{i}", "?", (dx, dy, 0.17), 0.24, qm, c, rot=(math.radians(90), 0, rz)); tq.data.extrude = 0.004; parts.append(tq)
    for p_ in parts: p_.parent = grp
    # speaker grille dots on the front
    for i in range(3):
        for j in range(3):
            d_ = sets2.cyl(f"box6_dot{i}{j}", 0.012, 0.004, (-0.14 + i * 0.03, -0.212, 0.05 + j * 0.03), sets2.M("box6_dot", (0.15, 0.15, 0.18), 0.5), c, 12, bevel=0, rot=(math.radians(90), 0, 0)); d_.parent = grp
    key_vis(grp, 1, False)
    living["cams"]["insert:box"] = ((BX - 0.35, BY - 1.05, BZ + 0.75), (BX, BY, BZ + 0.22), 42)
    # sound rings (torus-like flat rings expanding from the box)
    ring_m = sets2.M("ring6", (1, 1, 1), 0.3, emit=(0.5, 0.9, 1.0), emit_str=6.0, alpha=0.6)
    rings = []
    for i in range(4):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.12, minor_radius=0.012, location=(BX, BY, BZ + 0.2), major_segments=48, minor_segments=8)
        r_ = bpy.context.object; r_.name = f"box6_ring{i}"; r_.data.materials.append(ring_m)
        for cc in r_.users_collection: cc.objects.unlink(r_)
        c.objects.link(r_); r_.rotation_euler = (math.radians(90), 0, 0); key_vis(r_, 1, False); rings.append(r_)
    # reveal label: image plane above the box
    labels = {}
    for key, (txt, col) in ICON.items():
        im = Image.new("RGBA", (640, 220), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((8, 8, 632, 212), 60, fill=(255, 255, 255, 235), outline=col + (255,), width=10)
        d.text((320, 110), txt, font=FNT, fill=(40, 30, 60), anchor="mm")
        p = f"{MT}/label6_{key}.png"; im.save(p)
        pl = sets2.plane(f"box6_label_{key}", (0.6, 0.206), (BX, BY - 0.05, BZ + 0.85), img_mat(f"label6_{key}", p), c, rot=(math.radians(80), 0, 0))
        key_vis(pl, 1, False); labels[key] = pl
    # ---- scoreboard on the back wall ----
    SBX, SBY, SBZ = O.x - 2.4, O.y + 2.55, 1.75
    def score_img(sc_):
        im = Image.new("RGBA", (900, 640), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((6, 6, 894, 634), 50, fill=(60, 40, 110, 245), outline=(255, 220, 90, 255), width=10)
        d.text((450, 78), "GUESS THE SOUND", font=FNT, fill=(255, 220, 90), anchor="mm")
        for i, k in enumerate(("vanu", "aarav", "vihaan", "himank", "buddy")):
            y = 170 + i * 92
            d.text((120, y), k.upper(), font=FNT2, fill=(255, 255, 255), anchor="lm")
            n_ = sc_.get(k, 0)
            for j in range(n_): d.ellipse((520 + j * 70, y - 26, 572 + j * 70, y + 26), fill=(255, 120, 200))
            if n_ == 0: d.text((520, y), "-", font=FNT2, fill=(180, 170, 210), anchor="lm")
        return im
    states = [dict()]
    for e in TL["events"]:
        if e["type"] == "prop" and e["name"] == "score":
            states.append({k: e[k] for k in ("vanu", "aarav", "vihaan", "himank", "buddy") if k in e})
    boards = []
    for i, st in enumerate(states):
        p = f"{MT}/score6_{i}.png"; score_img(st).save(p)
        pl = sets2.plane(f"score6_{i}", (1.35, 0.96), (SBX, SBY - 0.02, SBZ), img_mat(f"score6_{i}", p, emit=0.9), c, rot=(math.radians(90), 0, 0))
        key_vis(pl, 1, i == 0); boards.append(pl)
    sets2.box("score6_frame", (1.45, 0.03, 1.06), (SBX, SBY, SBZ), sets2.M("score6_fr", (0.95, 0.8, 0.3), 0.35, coat=0.4), c, 0.01)
    living["cams"]["insert:score"] = ((SBX + 0.1, SBY - 1.9, SBZ - 0.1), (SBX, SBY, SBZ), 40)
    sets2.area("score6_light", (SBX, SBY - 1.2, 2.6), (SBX, SBY, SBZ), 60, 1.0, c, (1, 0.95, 0.85))
    si = 0

def box_play(f):
    for i, r_ in enumerate(rings):
        t0 = f + i * 7
        r_.scale = (0.3, 0.3, 0.3); r_.keyframe_insert("scale", frame=t0); key_vis(r_, t0, True)
        r_.scale = (6, 6, 6); r_.keyframe_insert("scale", frame=t0 + 26); key_vis(r_, t0 + 27, False)
    # lid rattles
    for df, dz, rx in ((0, 0, 0), (4, 0.03, 0.12), (8, 0.0, -0.08), (12, 0.035, 0.1), (16, 0.0, -0.06), (20, 0.025, 0.08), (26, 0.0, 0.0)):
        lid.location = (0, 0, 0.37 + dz); lid.rotation_euler = (rx, 0, 0); lid.keyframe_insert("location", frame=f + df); lid.keyframe_insert("rotation_euler", frame=f + df)
        knob.location = (0, 0, 0.42 + dz); knob.keyframe_insert("location", frame=f + df)
    vfx.flash(f"box6_flash{f}", (BX, BY, BZ + 0.45), living["coll"], f + 4, 30, color=(0.6, 0.9, 1.0), dur=22)

def box_reveal(f, key):
    pl = labels.get(key)
    if not pl: return
    key_vis(pl, f, True); key_vis(pl, f + 60, False)
    pl.scale = (0.01, 0.01, 0.01); pl.keyframe_insert("scale", frame=f)
    pl.scale = (1.15, 1.15, 1.15); pl.keyframe_insert("scale", frame=f + 5)
    pl.scale = (1, 1, 1); pl.keyframe_insert("scale", frame=f + 9)
    pl.scale = (1, 1, 1); pl.keyframe_insert("scale", frame=f + 55); pl.scale = (0.01, 0.01, 0.01); pl.keyframe_insert("scale", frame=f + 60)
    vfx.flash(f"box6_rev{f}", (BX, BY, BZ + 0.8), living["coll"], f, 40, color=(1.0, 0.9, 0.5), dur=10)

for e in TL["events"]:
    if e["type"] != "prop": continue
    f = F(e["t"]); nm = e["name"]; a = e["action"]
    if nm == "box" and a == "show" and living:
        key_vis(grp, f, True)
        grp.scale = (0.01, 0.01, 0.01); grp.keyframe_insert("scale", frame=f); grp.scale = (1.1, 1.1, 1.1); grp.keyframe_insert("scale", frame=f + 6); grp.scale = (1, 1, 1); grp.keyframe_insert("scale", frame=f + 10)
    elif nm == "box" and a == "play" and living: box_play(f + 28)
    elif nm == "box" and a == "reveal" and living: box_reveal(f + 2, e.get("sound"))
    elif nm == "score" and a == "set" and living:
        si += 1
        for i, b_ in enumerate(boards): key_vis(b_, f + 3, i == si)
        vfx.flash(f"score6_fl{f}", (SBX, SBY - 0.3, SBZ), living["coll"], f + 3, 25, color=(1.0, 0.8, 0.9), dur=8)
    elif nm == "confetti" and a == "burst" and living:
        for i, col in enumerate(((1.0, 0.3, 0.5), (1.0, 0.85, 0.2), (0.3, 0.7, 1.0))):
            vfx.emitter(f"conf6_{i}", (O.x + 0.3 + (i - 1) * 1.2, O.y + 0.4, 2.7), living["coll"], 260, f, f + 10, 70, col, size=0.025, vel_rand=2.2, gravity=0.35, strength=12.0, radius=0.3)
    elif nm == "steam" and kitchen:
        cx_, cy_, cz_ = kitchen["cooker"]
        for k_ in range(3 if a == "pan" else 5): puff((cx_, cy_, 1.25), f + 4 + k_ * 10, n=4, size=0.025, rise=0.5, spread=0.04, life=40, coll=kitchen["coll"], mat=steam_m)
for ob in bpy.data.objects:
    if ob.name.startswith(("box6_", "score6_")): const_keys(ob) if not ob.name.startswith(("box6_ring", "box6_label", "box6_lidb", "box6_knob", "box6_grp")) else None
for ob in rings + list(labels.values()) + [grp]:
    if ob.animation_data and ob.animation_data.action:
        for fc in ob.animation_data.action.fcurves:
            if "hide" in fc.data_path:
                for kp in fc.keyframe_points: kp.interpolation = "CONSTANT"
