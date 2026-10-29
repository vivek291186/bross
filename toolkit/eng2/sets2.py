# ===== eng2 sets: kitchen, bus, classroom, canteen (detailed, PBR-ish procedural) =====
import bpy, math, random
from mathutils import Vector, Euler

SETS = {}          # name -> dict(origin=Vector, cams={}, marks={}, lights=[...])
_MATS = {}

def col(name):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c)
    return c

def _link(o, coll):
    for c in o.users_collection: c.objects.unlink(o)
    coll.objects.link(o)

# ---------- materials ----------
def _P(m): return m.node_tree.nodes["Principled BSDF"]
def M(name, color=(0.8, 0.8, 0.8), rough=0.6, metal=0.0, bump=0.0, bump_scale=60.0, emit=None, emit_str=1.0, alpha=None, coat=0.0):
    key = name
    if key in _MATS: return _MATS[key]
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; p = _P(m)
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if coat: p.inputs["Coat Weight"].default_value = coat
    if emit:
        p.inputs["Emission Color"].default_value = (*emit, 1); p.inputs["Emission Strength"].default_value = emit_str
    if alpha is not None:
        p.inputs["Alpha"].default_value = alpha; m.blend_method = "BLEND" if hasattr(m, "blend_method") else None
        try: m.surface_render_method = "BLENDED"
        except Exception: pass
    if bump:
        n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = bump_scale; n.inputs["Detail"].default_value = 8
        b = nt.nodes.new("ShaderNodeBump"); b.inputs["Strength"].default_value = bump; b.inputs["Distance"].default_value = 0.02
        nt.links.new(n.outputs["Fac"], b.inputs["Height"]); nt.links.new(b.outputs["Normal"], p.inputs["Normal"])
        # subtle colour variation
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.inputs[0].default_value = 0.12
        mx.inputs[6].default_value = (*color, 1); mx.inputs[7].default_value = (color[0] * 0.85, color[1] * 0.85, color[2] * 0.85, 1)
        nt.links.new(n.outputs["Fac"], mx.inputs[0]); nt.links.new(mx.outputs[2], p.inputs["Base Color"])
    _MATS[key] = m; return m

def M_wood(name, c1=(0.45, 0.26, 0.12), c2=(0.30, 0.16, 0.07), rough=0.45, scale=3.0, coat=0.2):
    if name in _MATS: return _MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; p = _P(m)
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1, 1, 6)
    w = nt.nodes.new("ShaderNodeTexWave"); w.inputs["Scale"].default_value = scale; w.inputs["Distortion"].default_value = 6; w.inputs["Detail"].default_value = 4
    w.wave_type = "RINGS"
    r = nt.nodes.new("ShaderNodeValToRGB"); r.color_ramp.elements[0].color = (*c2, 1); r.color_ramp.elements[1].color = (*c1, 1)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], w.inputs["Vector"])
    nt.links.new(w.outputs["Fac"], r.inputs["Fac"]); nt.links.new(r.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = rough; p.inputs["Coat Weight"].default_value = coat
    _MATS[name] = m; return m

def M_tiles(name, c1=(0.85, 0.85, 0.82), c2=(0.6, 0.6, 0.58), mortar=(0.35, 0.35, 0.35), scale=4.0, rough=0.25, brick=False):
    if name in _MATS: return _MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; p = _P(m)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    b = nt.nodes.new("ShaderNodeTexBrick"); b.inputs["Scale"].default_value = scale
    b.offset = 0.5 if brick else 0.0; b.squash = 1.0
    b.inputs["Color1"].default_value = (*c1, 1); b.inputs["Color2"].default_value = (*c2, 1); b.inputs["Mortar"].default_value = (*mortar, 1)
    b.inputs["Mortar Size"].default_value = 0.012; b.inputs["Brick Width"].default_value = 0.5; b.inputs["Row Height"].default_value = 0.25 if brick else 0.5
    nt.links.new(tc.outputs["Object"], b.inputs["Vector"]); nt.links.new(b.outputs["Color"], p.inputs["Base Color"])
    bm = nt.nodes.new("ShaderNodeBump"); bm.inputs["Strength"].default_value = 0.4; bm.invert = True
    nt.links.new(b.outputs["Fac"], bm.inputs["Height"]); nt.links.new(bm.outputs["Normal"], p.inputs["Normal"])
    p.inputs["Roughness"].default_value = rough
    _MATS[name] = m; return m

def M_img_text(name, text, bg, fg):
    return M(name, bg, 0.7)

def M_sky_window(name, top=(0.45, 0.68, 1.0), bottom=(0.9, 0.95, 1.0), strength=3.0, trees=True):
    """emissive backdrop seen through windows: gradient sky + soft green tree blobs"""
    if name in _MATS: return _MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial"); em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = strength
    tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.color_ramp.elements[0].color = (*bottom, 1); ramp.color_ramp.elements[1].color = (*top, 1)
    nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
    if trees:
        vor = nt.nodes.new("ShaderNodeTexVoronoi"); vor.inputs["Scale"].default_value = 6.0; vor.feature = "F1"
        nt.links.new(tc.outputs["Generated"], vor.inputs["Vector"])
        mskz = nt.nodes.new("ShaderNodeMath"); mskz.operation = "LESS_THAN"; mskz.inputs[1].default_value = 0.45
        nt.links.new(sep.outputs["Z"], mskz.inputs[0])
        blob = nt.nodes.new("ShaderNodeMath"); blob.operation = "LESS_THAN"; blob.inputs[1].default_value = 0.42
        nt.links.new(vor.outputs["Distance"], blob.inputs[0])
        mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
        nt.links.new(mskz.outputs[0], mul.inputs[0]); nt.links.new(blob.outputs[0], mul.inputs[1])
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"
        mx.inputs[7].default_value = (0.18, 0.42, 0.12, 1)
        nt.links.new(mul.outputs[0], mx.inputs[0]); nt.links.new(ramp.outputs["Color"], mx.inputs[6])
        nt.links.new(mx.outputs[2], em.inputs["Color"])
    else:
        nt.links.new(ramp.outputs["Color"], em.inputs["Color"])
    nt.links.new(em.outputs[0], out.inputs[0])
    _MATS[name] = m; return m

# ---------- primitives ----------
def _fin(o, mat, coll, bevel, smooth=True):
    if mat: o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new("bev", "BEVEL"); b.width = bevel; b.segments = 3; b.limit_method = "ANGLE"
        try: o.modifiers.new("wn", "WEIGHTED_NORMAL")
        except Exception: pass
    if smooth:
        for p in o.data.polygons: p.use_smooth = True
    _link(o, coll); return o

def box(name, size, loc, mat, coll, bevel=0.01, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    return _fin(o, mat, coll, bevel)

def cyl(name, r, h, loc, mat, coll, verts=32, bevel=0.004, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=verts, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name
    return _fin(o, mat, coll, bevel)

def sph(name, r, loc, mat, coll, scale=(1, 1, 1), seg=24):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=seg, ring_count=seg // 2)
    o = bpy.context.object; o.name = name; o.scale = scale
    return _fin(o, mat, coll, 0)

def plane(name, size, loc, mat, coll, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.scale = (size[0], size[1], 1)
    bpy.ops.object.transform_apply(scale=True)
    return _fin(o, mat, coll, 0, smooth=False)

def text(name, body, loc, size, mat, coll, rot=(math.radians(90), 0, 0), extrude=0.005, align="CENTER"):
    cu = bpy.data.curves.new(name, "FONT"); cu.body = body; cu.size = size; cu.extrude = extrude; cu.align_x = align; cu.align_y = "CENTER"
    o = bpy.data.objects.new(name, cu); o.location = loc; o.rotation_euler = rot; coll.objects.link(o)
    cu.materials.append(mat); return o

def area(name, loc, target, energy, size, coll, color=(1, 1, 1), shape="RECTANGLE", sy=None):
    d = bpy.data.lights.new(name, "AREA"); d.energy = energy; d.size = size; d.color = color; d.shape = shape
    if sy: d.size_y = sy
    o = bpy.data.objects.new(name, d); coll.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler(); return o

def point(name, loc, energy, coll, color=(1, 0.9, 0.75), radius=0.1):
    d = bpy.data.lights.new(name, "POINT"); d.energy = energy; d.color = color; d.shadow_soft_size = radius
    o = bpy.data.objects.new(name, d); coll.objects.link(o); o.location = loc; return o

def room(sn, O, w, d, h, wall_m, floor_m, ceil_m, coll, skirting=None, open_front=True):
    """room spanning x in [-w/2,w/2], y in [-d/2, d/2] relative to origin O. front (−y) open for the camera."""
    ox, oy = O.x, O.y
    box(sn + "_floor", (w, d + 4, 0.1), (ox, oy + 1.0, -0.05), floor_m, coll, 0)
    box(sn + "_back", (w, 0.12, h), (ox, oy + d / 2, h / 2), wall_m, coll, 0)
    box(sn + "_left", (0.12, d + 4, h), (ox - w / 2, oy + 1.0, h / 2), wall_m, coll, 0)
    box(sn + "_right", (0.12, d + 4, h), (ox + w / 2, oy + 1.0, h / 2), wall_m, coll, 0)
    box(sn + "_ceil", (w, d + 4, 0.1), (ox, oy + 1.0, h + 0.05), ceil_m, coll, 0)
    if skirting:
        box(sn + "_skb", (w, 0.03, 0.1), (ox, oy + d / 2 - 0.07, 0.05), skirting, coll, 0.003)
        box(sn + "_skl", (0.03, d + 4, 0.1), (ox - w / 2 + 0.07, oy + 1.0, 0.05), skirting, coll, 0.003)
        box(sn + "_skr", (0.03, d + 4, 0.1), (ox + w / 2 - 0.07, oy + 1.0, 0.05), skirting, coll, 0.003)
    # front wall behind camera (gives bounce + reflections) – far back so it rarely shows
    box(sn + "_front", (w, 0.12, h), (ox, oy - d / 2 - 2.0, h / 2), wall_m, coll, 0)

def window_hole(sn, O, wall_x_or_y, along, z, ww, wh, coll, axis="y", frame_m=None, sky_m=None, depth=0.12):
    """Build a window by placing frame + emissive backdrop just outside a wall; the wall must have been split around it."""
    pass

def wall_with_window(name, O, axis, pos, a0, a1, h, wins, wall_m, frame_m, sky_m, coll, thick=0.12):
    """axis 'y': wall at y=pos spanning x a0..a1. axis 'x': wall at x=pos spanning y a0..a1. wins: list of (center_along, z0, z1, width)."""
    segs = []  # build as rectangles around window holes
    cuts = sorted(wins, key=lambda w: w[0]); cur = a0
    for (c, z0, z1, wd) in cuts:
        l, r = c - wd / 2, c + wd / 2
        segs.append((cur, l, 0, h)); segs.append((l, r, 0, z0)); segs.append((l, r, z1, h)); cur = r
    segs.append((cur, a1, 0, h))
    for i, (u0, u1, z0, z1) in enumerate(segs):
        if u1 - u0 < 1e-3 or z1 - z0 < 1e-3: continue
        cu, cz = (u0 + u1) / 2, (z0 + z1) / 2
        if axis == "y": box(f"{name}_{i}", (u1 - u0, thick, z1 - z0), (O.x + cu, O.y + pos, cz), wall_m, coll, 0)
        else: box(f"{name}_{i}", (thick, u1 - u0, z1 - z0), (O.x + pos, O.y + cu, cz), wall_m, coll, 0)
    for j, (c, z0, z1, wd) in enumerate(cuts):
        hgt = z1 - z0; cz = (z0 + z1) / 2; fr = 0.05
        if axis == "y":
            P = lambda du, dz: (O.x + c + du, O.y + pos, cz + dz)
            for k, (sz, off) in enumerate([((wd + 2 * fr, 0.16, fr), (0, hgt / 2)), ((wd + 2 * fr, 0.22, fr), (0, -hgt / 2)), ((fr, 0.16, hgt), (-wd / 2, 0)), ((fr, 0.16, hgt), (wd / 2, 0)), ((0.03, 0.1, hgt), (0, 0))]):
                box(f"{name}_wf{j}_{k}", sz, P(*off), frame_m, coll, 0.004)
            plane(f"{name}_sky{j}", (wd * 3.0, hgt * 2.2), (O.x + c, O.y + pos + 1.2, cz + 0.3), sky_m, coll, rot=(math.radians(90), 0, 0))
        else:
            P = lambda du, dz: (O.x + pos, O.y + c + du, cz + dz)
            for k, (sz, off) in enumerate([((0.16, wd + 2 * fr, fr), (0, hgt / 2)), ((0.22, wd + 2 * fr, fr), (0, -hgt / 2)), ((0.16, fr, hgt), (-wd / 2, 0)), ((0.16, fr, hgt), (wd / 2, 0)), ((0.1, 0.03, hgt), (0, 0))]):
                box(f"{name}_wf{j}_{k}", sz, P(*off), frame_m, coll, 0.004)
            sgn = 1 if pos > 0 else -1
            plane(f"{name}_sky{j}", (wd * 3.0, hgt * 2.2), (O.x + pos + sgn * 1.2, O.y + c, cz + 0.3), sky_m, coll, rot=(math.radians(90), 0, math.radians(90)))

# ---------- common props ----------
LID = {"aarav": (0.95, 0.45, 0.10), "vihaan": (0.20, 0.62, 0.30), "himank": (0.15, 0.45, 0.95), "vanu": (0.85, 0.15, 0.35), "buddy": (0.98, 0.78, 0.10)}
def tiffin(name, loc, lidc, coll, scale=1.0):
    """two-tier steel tiffin with coloured lid and handle clip; returns root empty"""
    steel = M("steel", (0.78, 0.79, 0.82), 0.18, 1.0)
    lm = M("lid_" + name, lidc, 0.35, 0.0, coat=0.4)
    e = bpy.data.objects.new(name, None); coll.objects.link(e); e.location = loc; e.empty_display_size = 0.08
    r = 0.075 * scale
    parts = [cyl(name + "_t1", r, 0.07 * scale, (0, 0, 0.035 * scale), steel, coll), cyl(name + "_t2", r, 0.07 * scale, (0, 0, 0.108 * scale), steel, coll),
             cyl(name + "_lid", r * 1.03, 0.025 * scale, (0, 0, 0.155 * scale), lm, coll),
             box(name + "_h1", (0.012 * scale, 0.012 * scale, 0.2 * scale), (r + 0.006, 0, 0.1 * scale), steel, coll, 0.003),
             box(name + "_h2", (0.012 * scale, 0.012 * scale, 0.2 * scale), (-r - 0.006, 0, 0.1 * scale), steel, coll, 0.003),
             box(name + "_h3", (2 * r + 0.024, 0.014 * scale, 0.012 * scale), (0, 0, 0.2 * scale), steel, coll, 0.003)]
    for p in parts: p.parent = e
    return e

def laddoo(name, loc, coll, r=0.018):
    m = M("laddoo", (0.95, 0.62, 0.12), 0.7, bump=0.6, bump_scale=300)
    return sph(name, r, loc, m, coll, seg=12)

def chair_kid(name, loc, yaw, coll, seat_h=0.40, mat=None, legm=None):
    mat = mat or M("chair_blue", (0.12, 0.38, 0.75), 0.4, coat=0.3); legm = legm or M("metal_dark", (0.12, 0.12, 0.13), 0.35, 1.0)
    e = bpy.data.objects.new(name, None); coll.objects.link(e); e.location = loc; e.rotation_euler = (0, 0, math.radians(yaw))
    ps = [box(name + "_seat", (0.40, 0.38, 0.03), (0, 0, seat_h), mat, coll, 0.01), box(name + "_back", (0.40, 0.025, 0.28), (0, 0.19, seat_h + 0.2), mat, coll, 0.01)]
    for sx in (-0.18, 0.18):
        for sy in (-0.16, 0.18):
            ps.append(cyl(name + f"_l{sx}{sy}", 0.012, seat_h, (sx, sy, seat_h / 2), legm, coll, 12))
    for p in ps: p.parent = e
    return e

def plant(name, loc, coll, h=0.6):
    pot = M("pot", (0.75, 0.38, 0.22), 0.6, bump=0.2)
    leaf = M("leaf", (0.12, 0.42, 0.14), 0.5)
    ps = [cyl(name + "_pot", 0.12, 0.22, (loc[0], loc[1], loc[2] + 0.11), pot, coll)]
    rnd = random.Random(hash(name) & 999)
    for i in range(9):
        a = i * 0.7; rr = 0.08 + rnd.random() * 0.06
        ps.append(sph(name + f"_lf{i}", 0.09, (loc[0] + rr * math.cos(a), loc[1] + rr * math.sin(a), loc[2] + 0.25 + rnd.random() * h * 0.6), leaf, coll, scale=(1, 0.6, 1.4)))
    return ps

def clock(name, loc, rot, coll):
    face = M("clockface", (0.96, 0.96, 0.94), 0.4); rim = M("clockrim", (0.85, 0.2, 0.2), 0.3, coat=0.5); hand = M("ink", (0.05, 0.05, 0.06), 0.5)
    cyl(name + "_rim", 0.2, 0.05, loc, rim, coll, rot=rot)
    o = cyl(name + "_face", 0.18, 0.055, loc, face, coll, rot=rot)
    return o

def poster(name, loc, size, rot, colr, coll, label=None, txtc=(1, 1, 1)):
    p = box(name, (size[0], 0.01, size[1]), loc, M("poster_" + name, colr, 0.6), coll, 0.002, rot=rot)
    if label:
        n = Vector((0, -1, 0)); n.rotate(Euler(rot))
        t = text(name + "_t", label, Vector(loc) + n * 0.012, size[1] * 0.28, M("ptxt_" + name, txtc, 0.5), coll, rot=(math.radians(90), 0, rot[2]))
    return p

# ================= KITCHEN =================
def build_kitchen(O=Vector((0, 0, 0))):
    sn = "kitchen"; c = col(sn)
    wall = M("k_wall", (0.98, 0.86, 0.66), 0.85, bump=0.15, bump_scale=120)
    floor = M_tiles("k_floor", (0.86, 0.80, 0.70), (0.80, 0.74, 0.64), (0.55, 0.5, 0.45), scale=3.0, rough=0.3)
    ceil = M("k_ceil", (0.97, 0.96, 0.93), 0.9)
    wood = M("k_skirt", (0.55, 0.32, 0.16), 0.5)
    sky = M_sky_window("k_sky", strength=4.0)
    frame = M("k_frame", (0.95, 0.95, 0.95), 0.4)
    W, D, H = 8.4, 5.4, 2.9
    box(sn + "_floor", (W, D + 4, 0.1), (O.x, O.y + 0.8, -0.05), floor, c, 0)
    box(sn + "_ceil", (W, D + 4, 0.1), (O.x, O.y + 0.8, H + 0.05), ceil, c, 0)
    wall_with_window(sn + "_back", O, "y", D / 2, -W / 2, W / 2, H, [(-0.2, 1.25, 2.25, 1.5)], wall, frame, sky, c)
    # left wall with door opening (door at y=0.4)
    wall_with_window(sn + "_left", O, "x", -W / 2, -D / 2 - 2, D / 2, H, [(0.4, 0.0, 2.15, 1.0)], wall, frame, M_sky_window("k_out", (0.55, 0.75, 1), (1, 1, 0.95), 5.0), c)
    wall_with_window(sn + "_right", O, "x", W / 2, -D / 2 - 2, D / 2, H, [(-0.6, 1.0, 2.2, 1.3)], wall, frame, sky, c)
    box(sn + "_front", (W, 0.12, H), (O.x, O.y - D / 2 - 2.0, H / 2), wall, c, 0)
    # back splash tiles behind counter
    box(sn + "_splash", (5.2, 0.02, 0.6), (O.x - 0.2, O.y + D / 2 - 0.07, 1.2), M_tiles("k_splash", (0.30, 0.62, 0.70), (0.28, 0.58, 0.66), (0.92, 0.92, 0.9), 8.0, 0.15, brick=True), c, 0)
    # counter run along back wall
    cab = M("k_cab", (0.36, 0.55, 0.45), 0.45, coat=0.15); top = M("k_granite", (0.16, 0.15, 0.15), 0.25, bump=0.3, bump_scale=200)
    handle = M("brass", (0.85, 0.68, 0.35), 0.25, 1.0)
    cy = O.y + D / 2 - 0.36
    box(sn + "_base", (5.2, 0.6, 0.86), (O.x - 0.2, cy, 0.43), cab, c, 0.008)
    box(sn + "_top", (5.3, 0.66, 0.04), (O.x - 0.2, cy - 0.02, 0.88), top, c, 0.006)
    for i in range(6):
        x = O.x - 2.55 + i * 0.86
        box(sn + f"_door{i}", (0.8, 0.02, 0.7), (x + 0.43, cy - 0.31, 0.43), cab, c, 0.01)
        box(sn + f"_hd{i}", (0.12, 0.02, 0.015), (x + 0.43, cy - 0.33, 0.72), handle, c, 0.004)
    # upper cabinets (left & right of window)
    for i, x in enumerate((-2.2, 1.75)):
        box(sn + f"_up{i}", (1.3, 0.35, 0.7), (O.x + x, O.y + D / 2 - 0.2, 2.0), cab, c, 0.008)
        box(sn + f"_uph{i}", (0.015, 0.02, 0.12), (O.x + x, O.y + D / 2 - 0.39, 1.75), handle, c, 0.003)
    # stove + pressure cooker + kadhai
    steel = M("steel", (0.78, 0.79, 0.82), 0.18, 1.0); black = M("k_black", (0.03, 0.03, 0.035), 0.35)
    box(sn + "_stove", (0.7, 0.42, 0.08), (O.x + 1.5, cy, 0.94), steel, c, 0.01)
    for dx in (-0.17, 0.17): cyl(sn + f"_burn{dx}", 0.07, 0.02, (O.x + 1.5 + dx, cy, 0.99), black, c)
    cyl(sn + "_cooker", 0.12, 0.2, (O.x + 1.33, cy, 1.1), steel, c); cyl(sn + "_cookerlid", 0.08, 0.04, (O.x + 1.33, cy, 1.22), black, c)
    box(sn + "_cookhandle", (0.25, 0.03, 0.03), (O.x + 1.1, cy, 1.18), black, c, 0.008)
    sph(sn + "_kadhai", 0.15, (O.x + 1.68, cy, 1.04), steel, c, scale=(1, 1, 0.45))
    # sink
    box(sn + "_sink", (0.7, 0.42, 0.02), (O.x - 0.2, cy, 0.905), steel, c, 0.01)
    cyl(sn + "_tap", 0.015, 0.3, (O.x - 0.2, cy + 0.2, 1.05), steel, c); cyl(sn + "_spout", 0.013, 0.2, (O.x - 0.2, cy + 0.12, 1.19), steel, c, rot=(math.radians(90), 0, 0))
    # spice jars & steel dabbas on counter
    jarc = [(0.85, 0.2, 0.1), (0.95, 0.75, 0.1), (0.4, 0.6, 0.15), (0.6, 0.25, 0.1), (0.9, 0.5, 0.2)]
    for i, jc in enumerate(jarc):
        cyl(sn + f"_jar{i}", 0.045, 0.12, (O.x - 2.3 + i * 0.12, cy + 0.1, 0.96), M(f"spice{i}", jc, 0.6, bump=0.3, bump_scale=200), c)
        cyl(sn + f"_jarl{i}", 0.047, 0.02, (O.x - 2.3 + i * 0.12, cy + 0.1, 1.03), steel, c)
    for i in range(3): cyl(sn + f"_dabba{i}", 0.09, 0.22 - i * 0.04, (O.x + 0.6 + i * 0.22, cy + 0.12, 0.9 + (0.22 - i * 0.04) / 2), steel, c)
    # fridge
    fr = M("k_fridge", (0.92, 0.25, 0.25), 0.3, coat=0.6)
    box(sn + "_fridge", (0.75, 0.7, 1.85), (O.x + 3.55, O.y + 1.9, 0.925), fr, c, 0.04)
    box(sn + "_fridgeline", (0.76, 0.71, 0.01), (O.x + 3.55, O.y + 1.9, 1.3), black, c, 0)
    box(sn + "_fh", (0.03, 0.03, 0.5), (O.x + 3.3, O.y + 1.53, 1.0), steel, c, 0.01)
    for i, mc in enumerate([(0.2, 0.6, 1), (1, 0.85, 0.1), (0.3, 0.8, 0.3)]):
        sph(sn + f"_mag{i}", 0.03, (O.x + 3.45 + i * 0.1, O.y + 1.54, 1.55 - i * 0.07), M(f"mag{i}", mc, 0.3), c, scale=(1, 0.4, 1))
    # dining table (lunchbox table) + chairs
    tw = M_wood("k_table", (0.62, 0.38, 0.18), (0.45, 0.25, 0.10))
    TX, TY = O.x, O.y + 0.45
    box(sn + "_ttop", (1.9, 0.95, 0.05), (TX, TY, 0.74), tw, c, 0.015)
    for sx in (-0.85, 0.85):
        for sy in (-0.4, 0.4): box(sn + f"_tleg{sx}{sy}", (0.06, 0.06, 0.72), (TX + sx, TY + sy, 0.36), tw, c, 0.006)
    # table cloth runner
    box(sn + "_runner", (1.95, 0.35, 0.006), (TX, TY, 0.768), M_tiles("k_runner", (0.95, 0.85, 0.3), (0.95, 0.6, 0.2), (0.85, 0.3, 0.2), 10.0, 0.8), c, 0)
    # tiffins on table (prop roots), in order vanu..buddy
    tif = {}
    for i, k in enumerate(["aarav", "vihaan", "himank", "vanu", "buddy"]):
        tif[k] = tiffin(f"tif_{k}", (TX - 0.6 + i * 0.3, TY - 0.12, 0.772), LID[k], c)
    # bottles
    for i, bc in enumerate([(0.2, 0.6, 0.95), (0.95, 0.4, 0.6)]):
        cyl(sn + f"_bottle{i}", 0.035, 0.22, (TX + 0.75, TY + 0.1 + i * 0.12, 0.88), M(f"bottle{i}", bc, 0.25, coat=0.5), c)
    # fruit bowl
    sph(sn + "_bowl", 0.14, (TX - 0.75, TY + 0.25, 0.8), steel, c, scale=(1, 1, 0.4))
    for i, fc in enumerate([(0.95, 0.75, 0.1), (0.9, 0.2, 0.15), (0.95, 0.5, 0.1), (0.3, 0.7, 0.2)]):
        sph(sn + f"_fruit{i}", 0.045, (TX - 0.75 + 0.05 * math.cos(i * 1.6), TY + 0.25 + 0.05 * math.sin(i * 1.6), 0.86), M(f"fruit{i}", fc, 0.35, coat=0.3), c)
    # door (swings open)
    dm = M_wood("k_door", (0.55, 0.30, 0.14), (0.40, 0.20, 0.08), scale=2.0)
    hinge = bpy.data.objects.new("k_door_hinge", None); c.objects.link(hinge); hinge.location = (O.x - W / 2 + 0.06, O.y + 0.4 - 0.5, 0)
    dr = box("k_door", (0.05, 1.0, 2.13), (O.x - W / 2 + 0.06, O.y + 0.4, 1.07), dm, c, 0.01); dr.parent = hinge; dr.location = (0, 0.5, 1.07)
    box("k_door_knob", (0.06, 0.06, 0.06), (0, 0.9, 1.0), handle, c, 0.02).parent = hinge
    # wall decor
    clock("k_clock", (O.x + 1.2, O.y + D / 2 - 0.08, 2.35), (math.radians(90), 0, 0), c)
    poster("k_chart", (O.x - 3.0, O.y + D / 2 - 0.07, 1.5), (0.7, 0.5), (0, 0, 0), (1.0, 0.55, 0.2), c, "HEALTHY\nFOOD", (1, 1, 1))
    plant("k_plant", (O.x - 3.6, O.y + 2.0, 0), c)
    # ceiling lamp
    cyl(sn + "_lamp", 0.3, 0.08, (TX, TY, H - 0.06), M("lamp_e", (1, 1, 1), 0.5, emit=(1, 0.95, 0.85), emit_str=3.0), c)
    # lights
    area(sn + "_key", (O.x - 2.5, O.y - 3.0, 2.6), (TX, TY, 1.0), 260, 2.2, c, (1, 0.93, 0.82))
    area(sn + "_fill", (O.x + 2.8, O.y - 2.6, 1.8), (TX, TY, 1.0), 120, 2.6, c, (0.85, 0.9, 1.0))
    area(sn + "_top", (TX, TY, H - 0.15), (TX, TY, 0), 180, 1.2, c, (1, 0.95, 0.85))
    area(sn + "_win", (O.x - 0.2, O.y + D / 2 + 0.3, 1.8), (TX, TY, 0.9), 350, 1.6, c, (1, 0.97, 0.9))
    area(sn + "_rim", (O.x + 0.5, O.y + 2.2, 2.6), (TX, TY - 0.5, 1.2), 160, 1.0, c, (1, 0.95, 0.9))
    SETS[sn] = dict(origin=O, coll=c, tiffins=tif, table=(TX, TY, 0.77), door="k_door_hinge",
                    cams={"kitchen_wide": ((O.x + 0.0, O.y - 4.2, 1.45), (O.x, O.y + 0.3, 0.95), 30),
                          "insert:table": ((TX + 0.1, TY - 1.0, 1.25), (TX, TY - 0.1, 0.82), 50)})
    return SETS[sn]

# ================= SCHOOL BUS (interior) =================
def build_bus(O=Vector((100, 0, 0))):
    sn = "bus"; c = col(sn)
    yellow = M("bus_yel", (0.98, 0.72, 0.08), 0.4, coat=0.4); inner = M("bus_inner", (0.92, 0.9, 0.84), 0.6, bump=0.1)
    floor = M("bus_floor", (0.25, 0.27, 0.3), 0.7, bump=0.5, bump_scale=80); seat = M("bus_seat", (0.15, 0.32, 0.65), 0.55, bump=0.25, bump_scale=150)
    rail = M("steel", (0.78, 0.79, 0.82), 0.18, 1.0); sky = M_sky_window("bus_sky", strength=5.0)
    L = 7.0; Wd = 2.5; H = 2.15
    box(sn + "_floor", (Wd, L, 0.1), (O.x, O.y + 2.0, -0.05), floor, c, 0)
    box(sn + "_aisle", (0.5, L, 0.012), (O.x, O.y + 2.0, 0.006), M("bus_mat", (0.12, 0.12, 0.12), 0.8, bump=0.6, bump_scale=40), c, 0)
    box(sn + "_roof", (Wd, L, 0.1), (O.x, O.y + 2.0, H + 0.05), inner, c, 0)
    for side in (-1, 1):
        wins = [(y, 0.95, 1.75, 0.95) for y in (-0.6, 0.5, 1.6, 2.7, 3.8, 4.9)]
        wall_with_window(sn + f"_side{side}", O, "x", side * Wd / 2, -1.5, 5.5, H, wins, inner, rail, sky, c)
        box(sn + f"_stripe{side}", (0.02, L, 0.08), (O.x + side * (Wd / 2 - 0.07), O.y + 2.0, 0.8), yellow, c, 0)
        # overhead handrail
        cyl(sn + f"_rail{side}", 0.018, L, (O.x + side * 0.45, O.y + 2.0, 1.95), rail, c, 16, rot=(math.radians(90), 0, 0))
    box(sn + "_back", (Wd, 0.1, H), (O.x, O.y + 5.5, H / 2), inner, c, 0)
    box(sn + "_backwin", (1.6, 0.02, 0.7), (O.x, O.y + 5.44, 1.35), sky, c, 0)
    box(sn + "_front", (Wd, 0.1, H), (O.x, O.y - 3.0, H / 2), inner, c, 0)
    # seats: rows at y = 0, 1.1, 2.2, 3.3, 4.4 ; benches left x∈[-1.15,-0.2], right x∈[0.2,1.15]; seat top z=0.42
    for r, y in enumerate((0.0, 1.1, 2.2, 3.3, 4.4)):
        for side in (-1, 1):
            cx = O.x + side * 0.68
            box(sn + f"_cush{r}{side}", (0.92, 0.42, 0.12), (cx, O.y + y + 0.02, 0.40), seat, c, 0.03)
            box(sn + f"_sback{r}{side}", (0.92, 0.10, 0.62), (cx, O.y + y + 0.27, 0.72), seat, c, 0.035)
            box(sn + f"_sbase{r}{side}", (0.86, 0.36, 0.34), (cx, O.y + y + 0.04, 0.17), M("metal_dark", (0.12, 0.12, 0.13), 0.35, 1.0), c, 0.01)
            cyl(sn + f"_grab{r}{side}", 0.014, 0.8, (cx, O.y + y + 0.34, 1.05), rail, c, 12, rot=(0, math.radians(90), 0))
    # school bags on window seats
    bagc = [(0.9, 0.2, 0.25), (0.2, 0.5, 0.9), (0.2, 0.7, 0.35), (0.95, 0.55, 0.1), (0.55, 0.25, 0.75)]
    for i, (bx, by) in enumerate([(-0.9, 0.05), (0.9, 0.05), (-0.9, 1.15), (0.9, 1.15), (0.9, 2.25)]):
        box(sn + f"_bag{i}", (0.3, 0.18, 0.38), (O.x + bx, O.y + by, 0.65), M(f"bag{i}", bagc[i], 0.7, bump=0.3, bump_scale=200), c, 0.06)
    # tiffins on laps get placed by props system; keep spares here
    tif = {}
    for i, k in enumerate(["aarav", "vihaan", "vanu", "himank", "buddy"]):
        tif[k] = tiffin(f"btif_{k}", (O.x + (-0.45 if i % 2 == 0 else 0.45), O.y + [0, 0, 1.1, 1.1, 2.2][i] - 0.22, 0.47), LID[k], c, 0.9)
    # dashboard/driver area hint near camera
    box(sn + "_dash", (Wd, 0.6, 0.9), (O.x, O.y - 2.6, 0.45), M("bus_dash", (0.18, 0.18, 0.2), 0.6), c, 0.02)
    text(sn + "_sign", "SCHOOL BUS", (O.x, O.y + 5.42, 1.92), 0.16, M("bus_signt", (0.1, 0.1, 0.1), 0.5), c)
    box(sn + "_signbg", (1.4, 0.02, 0.24), (O.x, O.y + 5.44, 1.92), yellow, c, 0.004)
    # lights: strong daylight from windows + soft roof
    area(sn + "_key", (O.x - 1.0, O.y - 1.8, 1.9), (O.x, O.y + 1.0, 0.9), 220, 1.6, c, (1, 0.96, 0.88))
    area(sn + "_fill", (O.x + 1.0, O.y - 1.6, 1.4), (O.x, O.y + 1.0, 0.9), 110, 1.8, c, (0.88, 0.92, 1.0))
    for i, y in enumerate((0.0, 2.2, 4.4)):
        area(sn + f"_roof{i}", (O.x, O.y + y, H - 0.05), (O.x, O.y + y, 0), 120, 0.8, c, (1, 0.98, 0.95), sy=1.4)
    for side in (-1, 1):
        area(sn + f"_sun{side}", (O.x + side * 1.6, O.y + 1.6, 1.4), (O.x, O.y + 1.6, 0.8), 260, 2.0, c, (1, 0.95, 0.85), sy=4.0)
    # moving scenery: posts that slide past windows (animated by builder)
    post_m = M("bus_post", (0.25, 0.5, 0.2), 0.7)
    movers = []
    for side in (-1, 1):
        for i in range(8):
            t = cyl(sn + f"_tree{side}_{i}", 0.35, 2.4, (O.x + side * 3.0, O.y - 4 + i * 1.6, 1.4), post_m, c, 10)
            movers.append(t)
    SETS[sn] = dict(origin=O, coll=c, tiffins=tif, movers=movers, seat_z=0.46,
                    cams={"bus_wide": ((O.x + 0.0, O.y - 1.7, 1.55), (O.x, O.y + 1.6, 0.85), 24)})
    return SETS[sn]

# ================= CLASSROOM =================
def build_classroom(O=Vector((200, 0, 0))):
    sn = "classroom"; c = col(sn)
    wall = M("c_wall", (0.80, 0.90, 0.80), 0.85, bump=0.12, bump_scale=120)
    floor = M_tiles("c_floor", (0.72, 0.60, 0.48), (0.68, 0.56, 0.44), (0.4, 0.33, 0.27), 2.0, 0.35, brick=True)
    ceil = M("c_ceil", (0.97, 0.97, 0.95), 0.9); frame = M("c_frame", (0.95, 0.95, 0.95), 0.4); sky = M_sky_window("c_sky", strength=4.5)
    W, D, H = 9.4, 6.4, 3.0
    box(sn + "_floor", (W, D + 4, 0.1), (O.x, O.y + 1.0, -0.05), floor, c, 0)
    box(sn + "_ceil", (W, D + 4, 0.1), (O.x, O.y + 1.0, H + 0.05), ceil, c, 0)
    box(sn + "_back", (W, 0.12, H), (O.x, O.y + 4.2, H / 2), wall, c, 0)
    wall_with_window(sn + "_right", O, "x", W / 2, -3.2, 4.2, H, [(-1.4, 0.95, 2.35, 1.4), (1.0, 0.95, 2.35, 1.4), (3.2, 0.95, 2.35, 1.2)], wall, frame, sky, c)
    wall_with_window(sn + "_left", O, "x", -W / 2, -3.2, 4.2, H, [(-0.8, 0.0, 2.2, 1.1)], wall, frame, M_sky_window("c_corr", (0.85, 0.88, 0.9), (0.95, 0.95, 0.92), 2.0, trees=False), c)
    box(sn + "_front", (W, 0.12, H), (O.x, O.y - 4.0, H / 2), wall, c, 0)
    # dado band
    box(sn + "_dado", (W, 0.02, 1.0), (O.x, O.y + 4.13, 0.5), M("c_dado", (0.35, 0.55, 0.40), 0.6), c, 0)
    # blackboard on front wall (seen in reverse shots) + soft board on back wall
    box(sn + "_board", (3.2, 0.04, 1.2), (O.x, O.y - 3.92, 1.6), M("c_board", (0.08, 0.22, 0.14), 0.7, bump=0.2), c, 0.01)
    text(sn + "_abc", "Lunch = Share & Care", (O.x, O.y - 3.89, 1.7), 0.18, M("chalk", (0.95, 0.95, 0.92), 0.8), c, rot=(math.radians(90), 0, math.radians(180)))
    box(sn + "_cork", (3.0, 0.03, 1.1), (O.x - 1.2, O.y + 4.12, 1.75), M("c_cork", (0.75, 0.55, 0.32), 0.9, bump=0.6, bump_scale=300), c, 0.01)
    rnd = random.Random(4)
    for i in range(7):
        cc = [(1, 0.4, 0.4), (0.4, 0.7, 1), (1, 0.85, 0.3), (0.5, 0.9, 0.5), (1, 0.6, 0.85)][i % 5]
        box(sn + f"_note{i}", (0.32, 0.01, 0.42), (O.x - 2.4 + i * 0.4, O.y + 4.10, 1.7 + rnd.uniform(-0.25, 0.25)), M(f"note{i}", cc, 0.8), c, 0.002,
            rot=(0, rnd.uniform(-0.12, 0.12), 0))
    poster(sn + "_abcchart", (O.x + 2.4, O.y + 4.12, 1.75), (1.2, 0.9), (0, 0, 0), (0.98, 0.82, 0.25), c, "A B C\nD E F", (0.15, 0.2, 0.5))
    text(sn + "_cls", "CLASS 3-B", (O.x - 1.2, O.y + 4.1, 2.5), 0.2, M("c_title", (0.9, 0.25, 0.2), 0.4), c)
    clock("c_clock", (O.x + 2.4, O.y + 4.12, 2.6), (math.radians(90), 0, 0), c)
    # desks for 5 kids (desk in front of each seat: kid at (x,y), desk at y-0.42)
    deskw = M_wood("c_desk", (0.80, 0.58, 0.32), (0.66, 0.45, 0.22), scale=4.0); legm = M("metal_dark", (0.12, 0.12, 0.13), 0.35, 1.0)
    seats = {"aarav": (-1.1, 0.0), "vihaan": (1.1, 0.0), "vanu": (-1.1, 1.6), "himank": (1.1, 1.6), "buddy": (0.0, 3.0)}
    extra = [(-3.0, 0.0), (3.0, 0.0), (-3.0, 1.6), (3.0, 1.6), (-2.0, 3.0), (2.0, 3.0)]
    tif = {}
    for k, (x, y) in list(seats.items()) + [(f"x{i}", p) for i, p in enumerate(extra)]:
        dx, dy = O.x + x, O.y + y - 0.45
        box(f"c_dtop_{k}", (0.9, 0.5, 0.035), (dx, dy, 0.6), deskw, c, 0.008)
        box(f"c_dfront_{k}", (0.9, 0.02, 0.3), (dx, dy - 0.24, 0.43), deskw, c, 0.005)
        for sx in (-0.42, 0.42):
            box(f"c_dleg_{k}{sx}", (0.03, 0.45, 0.03), (dx + sx, dy, 0.02), legm, c, 0.006)
            box(f"c_dlegv_{k}{sx}", (0.03, 0.03, 0.58), (dx + sx, dy, 0.3), legm, c, 0.006)
        chair_kid(f"c_chair_{k}", (O.x + x, O.y + y + 0.02, 0), 0, c)
        if k in LID: tif[k] = tiffin(f"ctif_{k}", (dx + 0.18, dy - 0.05, 0.618), LID[k], c, 0.95)
        # books
        box(f"c_book_{k}", (0.2, 0.26, 0.03), (dx - 0.22, dy, 0.632), M(f"book{hash(k) % 5}", [(0.85, 0.2, 0.2), (0.2, 0.5, 0.85), (0.95, 0.75, 0.15), (0.3, 0.7, 0.3), (0.6, 0.3, 0.8)][hash(k) % 5], 0.6), c, 0.004)
    # laddoo crumb trail (classroom floor towards left door)
    crumbs = []
    rnd = random.Random(11)
    path = [(0.1, 2.6), (-0.6, 1.9), (-1.6, 1.1), (-2.6, 0.2), (-3.4, -0.4), (-4.3, -0.8)]
    for a, b in zip(path, path[1:]):
        for t in range(6):
            u = t / 6; x = a[0] + (b[0] - a[0]) * u + rnd.uniform(-0.08, 0.08); y = a[1] + (b[1] - a[1]) * u + rnd.uniform(-0.08, 0.08)
            crumbs.append(laddoo(f"c_crumb{len(crumbs)}", (O.x + x, O.y + y, 0.008), c, 0.012))
    # lights
    area(sn + "_key", (O.x - 2.8, O.y - 3.0, 2.7), (O.x, O.y + 1.2, 0.8), 380, 2.5, c, (1, 0.95, 0.86))
    area(sn + "_fill", (O.x + 3.2, O.y - 2.6, 2.0), (O.x, O.y + 1.2, 0.8), 160, 3.0, c, (0.85, 0.9, 1.0))
    for i, (x, y) in enumerate([(-1.6, 0.6), (1.6, 0.6), (-1.6, 2.6), (1.6, 2.6)]):
        area(sn + f"_tube{i}", (O.x + x, O.y + y, H - 0.08), (O.x + x, O.y + y, 0), 90, 0.25, c, (1, 1, 0.97), sy=1.3)
        box(sn + f"_tubefix{i}", (0.18, 1.3, 0.04), (O.x + x, O.y + y, H - 0.03), M("tube_e", (1, 1, 1), 0.4, emit=(1, 1, 0.97), emit_str=4.0), c, 0.005)
    area(sn + "_sun", (O.x + W / 2 + 1.0, O.y + 0.2, 2.2), (O.x + 0.5, O.y + 1.0, 0.4), 500, 2.5, c, (1, 0.93, 0.8), sy=5.0)
    SETS[sn] = dict(origin=O, coll=c, tiffins=tif, crumbs=crumbs, seat_z=0.42,
                    cams={"class_wide": ((O.x + 0.2, O.y - 3.2, 1.7), (O.x, O.y + 1.4, 0.7), 26),
                          "insert:crumbs": ((O.x - 0.6, O.y + 0.6, 0.7), (O.x - 1.4, O.y + 1.4, 0.0), 35),
                          "insert:buddy_box": ((O.x + 0.05, O.y + 2.0, 1.15), (O.x + 0.15, O.y + 2.5, 0.62), 45)})
    return SETS[sn]

# ================= CANTEEN =================
def build_canteen(O=Vector((300, 0, 0))):
    sn = "canteen"; c = col(sn)
    wall = M("n_wall", (0.98, 0.92, 0.80), 0.85, bump=0.12, bump_scale=120)
    floor = M_tiles("n_floor", (0.92, 0.92, 0.9), (0.25, 0.28, 0.32), (0.5, 0.5, 0.5), 3.0, 0.25)
    ceil = M("n_ceil", (0.97, 0.97, 0.95), 0.9); frame = M("n_frame", (0.95, 0.95, 0.95), 0.4); sky = M_sky_window("n_sky", strength=4.5)
    W, D, H = 16.0, 6.4, 3.2
    box(sn + "_floor", (W, D + 4, 0.1), (O.x, O.y + 1.0, -0.05), floor, c, 0)
    box(sn + "_ceil", (W, D + 4, 0.1), (O.x, O.y + 1.0, H + 0.05), ceil, c, 0)
    wall_with_window(sn + "_back", O, "y", 3.4, -W / 2, W / 2, H, [(-5.0, 1.0, 2.4, 2.0), (5.2, 1.0, 2.4, 2.0)], wall, frame, sky, c)
    box(sn + "_left", (0.12, D + 4, H), (O.x - W / 2, O.y + 1.0, H / 2), wall, c, 0)
    box(sn + "_right", (0.12, D + 4, H), (O.x + W / 2, O.y + 1.0, H / 2), wall, c, 0)
    box(sn + "_front", (W, 0.12, H), (O.x, O.y - 4.0, H / 2), wall, c, 0)
    box(sn + "_dado", (W, 0.02, 1.1), (O.x, O.y + 3.33, 0.55), M_tiles("n_dado", (0.95, 0.55, 0.2), (0.9, 0.5, 0.18), (0.95, 0.95, 0.9), 8.0, 0.2), c, 0)
    # serving counter along back middle
    ctr = M("n_ctr", (0.20, 0.45, 0.75), 0.4, coat=0.3); top = M("steel", (0.78, 0.79, 0.82), 0.18, 1.0)
    box(sn + "_counter", (5.0, 0.7, 1.0), (O.x + 0.0, O.y + 2.85, 0.5), ctr, c, 0.02)
    box(sn + "_ctop", (5.1, 0.8, 0.04), (O.x + 0.0, O.y + 2.85, 1.02), top, c, 0.006)
    foods = [((0.95, 0.75, 0.25), "samosa"), ((0.95, 0.85, 0.6), "idli"), ((0.85, 0.35, 0.1), "curry"), ((0.98, 0.95, 0.85), "rice"), ((0.95, 0.6, 0.15), "jalebi")]
    for i, (fc, nm) in enumerate(foods):
        x = O.x - 2.0 + i * 1.0
        box(sn + f"_tray{i}", (0.6, 0.4, 0.06), (x, O.y + 2.85, 1.07), top, c, 0.01)
        for j in range(5):
            sph(sn + f"_food{i}_{j}", 0.05, (x - 0.2 + j * 0.1, O.y + 2.85 + (j % 2) * 0.08 - 0.04, 1.11), M("food_" + nm, fc, 0.55, bump=0.4, bump_scale=150), c, scale=(1, 1, 0.6))
    box(sn + "_menu", (2.6, 0.04, 0.8), (O.x, O.y + 3.32, 2.3), M("n_menu", (0.12, 0.12, 0.14), 0.6), c, 0.01)
    text(sn + "_menut", "CANTEEN\nSamosa 10  Idli 15  Jalebi 10", (O.x, O.y + 3.29, 2.3), 0.16, M("n_menutxt", (1, 0.9, 0.3), 0.5, emit=(1, 0.9, 0.3), emit_str=0.6), c)
    # long tables + benches
    tw = M_wood("n_table", (0.85, 0.65, 0.40), (0.70, 0.50, 0.28), scale=3.0); legm = M("metal_dark", (0.12, 0.12, 0.13), 0.35, 1.0)
    tables = [(-5.0, 1.2), (5.0, 1.2), (0.0, 0.55)]
    for i, (x, y) in enumerate(tables):
        box(sn + f"_t{i}", (3.0, 0.85, 0.05), (O.x + x, O.y + y, 0.68), tw, c, 0.012)
        for sx in (-1.35, 1.35):
            box(sn + f"_tl{i}{sx}", (0.06, 0.7, 0.66), (O.x + x + sx, O.y + y, 0.33), legm, c, 0.006)
        if i < 2:
            for sy in (-0.65, 0.65):
                box(sn + f"_b{i}{sy}", (2.8, 0.3, 0.05), (O.x + x, O.y + y + sy, 0.4), tw, c, 0.01)
                for sx in (-1.2, 1.2): box(sn + f"_bl{i}{sy}{sx}", (0.05, 0.25, 0.38), (O.x + x + sx, O.y + y + sy, 0.19), legm, c, 0.005)
    # ceiling fans
    for i, x in enumerate((-4.0, 0.0, 4.0)):
        cyl(sn + f"_fanrod{i}", 0.02, 0.5, (O.x + x, O.y + 1.0, H - 0.25), legm, c)
        hub = cyl(sn + f"_fanhub{i}", 0.1, 0.08, (O.x + x, O.y + 1.0, H - 0.5), M("fan", (0.95, 0.95, 0.95), 0.4), c)
        for b in range(3):
            bl = box(sn + f"_fanbl{i}{b}", (0.6, 0.12, 0.01), (0.35, 0, 0), M("fan", (0.95, 0.95, 0.95), 0.4), c, 0.005)
            pv = bpy.data.objects.new(sn + f"_fanpv{i}{b}", None); c.objects.link(pv); pv.parent = hub; pv.rotation_euler = (0, 0, b * 2.094)
            bl.parent = pv
        hub.animation_data_create()
    # posters
    poster(sn + "_p1", (O.x - 7.9, O.y + 1.0, 1.7), (1.0, 0.8), (0, 0, math.radians(-90)), (0.25, 0.65, 0.95), c, "WASH\nHANDS")
    poster(sn + "_p2", (O.x + 3.2, O.y + 3.32, 1.75), (0.9, 0.7), (0, 0, 0), (0.95, 0.35, 0.45), c, "EAT\nHEALTHY")
    poster(sn + "_p3", (O.x - 3.2, O.y + 3.32, 1.75), (0.9, 0.7), (0, 0, 0), (0.35, 0.75, 0.35), c, "SHARE\nFOOD")
    plant("n_plant1", (O.x - 7.4, O.y + 2.8, 0), c); plant("n_plant2", (O.x + 7.4, O.y + 2.8, 0), c)
    # cat (simple stylised) near counter
    catm = M("cat", (0.95, 0.6, 0.25), 0.7, bump=0.4, bump_scale=300); dk = M("ink", (0.05, 0.05, 0.06), 0.5)
    cat = bpy.data.objects.new("n_cat", None); c.objects.link(cat); cat.location = (O.x - 2.8, O.y + 2.2, 0)
    parts = [sph("cat_body", 0.16, (0, 0, 0.16), catm, c, scale=(1.5, 0.9, 0.9)), sph("cat_head", 0.11, (-0.22, -0.02, 0.3), catm, c)]
    for sx in (-0.05, 0.05): parts.append(sph(f"cat_ear{sx}", 0.04, (-0.24, -0.02 + sx, 0.4), catm, c, scale=(0.6, 0.6, 1.3)))
    for sx in (-0.04, 0.04): parts.append(sph(f"cat_eye{sx}", 0.018, (-0.31, -0.06 + sx * 0.9, 0.32), dk, c))
    parts.append(cyl("cat_tail", 0.025, 0.35, (0.26, 0, 0.3), catm, c, rot=(0, math.radians(-35), 0)))
    for p in parts: p.parent = cat
    cat.rotation_euler = (0, 0, math.radians(-60))
    # crumb trail across canteen floor (x -6 -> under share table -> circle to buddy)
    crumbs = []; rnd = random.Random(5)
    path = [(-7.0, -0.5), (-5.0, -0.5), (-3.0, -0.4), (-1.0, 0.0), (0.0, 0.25), (0.6, 0.6), (0.9, 0.9)]
    for a, b in zip(path, path[1:]):
        for t in range(5):
            u = t / 5; crumbs.append(laddoo(f"n_crumb{len(crumbs)}", (O.x + a[0] + (b[0] - a[0]) * u + rnd.uniform(-0.1, 0.1), O.y + a[1] + (b[1] - a[1]) * u + rnd.uniform(-0.08, 0.08), 0.008 + (0.012 if u > 0.6 else 0.0)), c, 0.012 + 0.004 * len(crumbs) / 30))
    # share-party food on middle table
    steel = top; foodset = []
    for i, (fc, nm) in enumerate(foods[:4]):
        x = O.x - 1.0 + i * 0.66
        foodset.append(cyl(sn + f"_plate{i}", 0.13, 0.015, (x, O.y + 0.6, 0.715), steel, c))
        for j in range(3): foodset.append(sph(sn + f"_pf{i}{j}", 0.04, (x - 0.05 + j * 0.05, O.y + 0.6, 0.74), M("food_" + nm, fc, 0.55, bump=0.4, bump_scale=150), c, scale=(1, 1, 0.6)))
    tif = {}
    for i, k in enumerate(["aarav", "vihaan", "vanu", "himank", "buddy"]):
        tif[k] = tiffin(f"ntif_{k}", (O.x - 1.25 + i * 0.62, O.y + 0.35, 0.705), LID[k], c, 0.9)
    # lights
    area(sn + "_key", (O.x - 3.0, O.y - 3.4, 2.8), (O.x - 1.0, O.y + 0.6, 0.8), 520, 3.0, c, (1, 0.94, 0.84))
    area(sn + "_fill", (O.x + 3.4, O.y - 3.0, 2.0), (O.x - 1.0, O.y + 0.6, 0.8), 220, 3.5, c, (0.86, 0.9, 1.0))
    for i, x in enumerate((-6.0, -2.0, 2.0, 6.0)):
        area(sn + f"_top{i}", (O.x + x, O.y + 1.0, H - 0.08), (O.x + x, O.y + 1.0, 0), 160, 1.2, c, (1, 0.98, 0.94), sy=1.2)
    area(sn + "_win1", (O.x - 5.0, O.y + 4.3, 2.0), (O.x - 4.0, O.y + 0.5, 0.6), 400, 2.2, c, (1, 0.95, 0.85))
    area(sn + "_win2", (O.x + 5.2, O.y + 4.3, 2.0), (O.x + 4.0, O.y + 0.5, 0.6), 400, 2.2, c, (1, 0.95, 0.85))
    SETS[sn] = dict(origin=O, coll=c, tiffins=tif, crumbs=crumbs, cat=cat, foodset=foodset,
                    cams={"canteen_wide": ((O.x - 1.6, O.y - 4.6, 1.5), (O.x - 1.8, O.y + 0.4, 0.75), 24),
                          "share_wide": ((O.x + 0.0, O.y - 3.0, 1.45), (O.x, O.y + 1.0, 0.95), 30),
                          "insert:cat": ((O.x - 3.3, O.y + 1.1, 0.55), (O.x - 2.8, O.y + 2.2, 0.25), 45),
                          "insert:under_table": ((O.x + 0.4, O.y - 0.9, 0.32), (O.x + 0.1, O.y + 0.4, 0.1), 32),
                          "insert:buddy_shoes": ((O.x + 0.6, O.y + 0.1, 0.35), (O.x + 0.9, O.y + 0.9, 0.05), 40)})
    return SETS[sn]

def build_all(which=("kitchen", "bus", "classroom", "canteen")):
    for w_ in which: globals()["build_" + w_]()
    return SETS
