# Real opening mouth for Meshy characters: subdivide face region, cut along the painted lip line (found from the texture),
# add a mouth cavity + teeth behind, and a "jaw" shape key that moves the lower lip/chin as a block (no texture stretching).
import bpy, bmesh, math
import numpy as np
from mathutils import Vector

def smooth(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a))) if b != a else (1.0 if x >= b else 0.0)
    return t * t * (3 - 2 * t)

def _tex_image(mesh):
    m = mesh.material_slots[0].material
    for n in m.node_tree.nodes:
        if n.type == "TEX_IMAGE" and n.image and n.image.colorspace_settings.name != "Non-Color":
            return n.image
    return None

def _sample(img, px, uv):
    w, h = img.size
    x = min(w - 1, max(0, int(uv[0] % 1.0 * w))); y = min(h - 1, max(0, int(uv[1] % 1.0 * h)))
    p = px[y, x]; return 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2], p

def build_mouth(mesh, arm, name, half_w=None, drop=0.010):
    me = mesh.data
    hb = [b for b in arm.data.bones if b.name.endswith(":Head")][0]
    hx, hy, hz = hb.head_local
    img = _tex_image(mesh)
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    # ---- 1. subdivide the lower-face region twice (keeps UVs, weights) ----
    bm = bmesh.new(); bm.from_mesh(me)
    uvl = bm.loops.layers.uv.active
    def region_faces(r_x, z0, z1):
        out = []
        for f in bm.faces:
            c = f.calc_center_median()
            if abs(c.x - hx) < r_x and z0 < c.z < z1 and c.y < hy - 0.03: out.append(f)
        return out
    for it in range(2):
        fs = region_faces(0.06, hz - 0.06, hz + 0.08)
        edges = list({e for f in fs for e in f.edges})
        bmesh.ops.subdivide_edges(bm, edges=edges, cuts=1, use_grid_fill=True, use_only_quads=False, smooth=0.0)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    bm.verts.ensure_lookup_table()
    # ---- 2. find lip line from texture darkness ----
    vuv = {}
    for f in bm.faces:
        for l in f.loops: vuv.setdefault(l.vert.index, l[uvl].uv.copy())
    cand = [v for v in bm.verts if abs(v.co.x - hx) < 0.035 and hz - 0.03 < v.co.z < hz + 0.07 and v.co.y < hy - 0.03]
    fy = min(v.co.y for v in cand)
    cand = [v for v in cand if v.co.y < fy + 0.018]
    lum = {v.index: _sample(img, px, vuv[v.index])[0] for v in cand if v.index in vuv}
    # lips are the reddest/darkest band below the nose: score = darkness + redness
    def score(v):
        L, p = _sample(img, px, vuv[v.index]); red = p[0] - (p[1] + p[2]) / 2
        return -L + 0.6 * red
    bins = {}
    for v in cand:
        if v.index not in vuv: continue
        b = int(round((v.co.x - hx) / 0.003))
        bins.setdefault(b, []).append(v)
    # mouth vertical centre guess from the existing table (keeps search local)
    line = {}
    for b, vs in bins.items():
        vs2 = [v for v in vs if hz - 0.005 < v.co.z < hz + 0.06]
        if not vs2: continue
        # darkest pixel along the column -> the gap between lips
        best = min(vs2, key=lambda v: _sample(img, px, vuv[v.index])[0])
        line[b] = best.co.z
    if not line: raise RuntimeError("no lip line")
    # robust: keep the central dark run, fit a parabola z(x)
    xs = np.array([b * 0.003 for b in line]); zs = np.array([line[b] for b in line])
    zc = np.median(zs[np.abs(xs) < 0.008]) if (np.abs(xs) < 0.008).any() else np.median(zs)
    keep = np.abs(zs - zc) < 0.008
    co = np.polyfit(xs[keep], zs[keep], 2) if keep.sum() >= 3 else np.array([0, 0, zc])
    zline = lambda x: co[0] * x * x + co[1] * x + co[2]
    # mouth half width: darkness above skin level along the line
    if half_w is None:
        darkness = []
        for b in sorted(line):
            x = b * 0.003
            vs = [v for v in bins[b] if abs(v.co.z - zline(x)) < 0.003]
            if vs: darkness.append((abs(x), min(_sample(img, px, vuv[v.index])[0] for v in vs)))
        skin = np.median([d for x, d in darkness if x > 0.03]) if any(x > 0.03 for x, d in darkness) else 0.5
        dark_x = [x for x, d in darkness if d < skin * 0.75]
        half_w = max(0.014, min(0.026, max(dark_x) if dark_x else 0.018))
    # ---- 3. cut along the lip line ----
    def side(v):  # +1 above line, -1 below
        return 1 if v.co.z > zline(v.co.x - hx) else -1
    lower_faces = set()
    for f in bm.faces:
        c = f.calc_center_median()
        if abs(c.x - hx) < half_w + 0.004 and c.y < fy + 0.02 and zline(c.x - hx) - 0.05 < c.z < zline(c.x - hx):
            lower_faces.add(f)
    cut = []
    for e in bm.edges:
        lf = [f for f in e.link_faces]
        if len(lf) != 2: continue
        a, b = (lf[0] in lower_faces), (lf[1] in lower_faces)
        if a == b: continue
        mx = (e.verts[0].co.x + e.verts[1].co.x) / 2 - hx
        mz = (e.verts[0].co.z + e.verts[1].co.z) / 2
        if abs(mx) < half_w - 0.002 and abs(mz - zline(mx)) < 0.006: cut.append(e)
    bmesh.ops.split_edges(bm, edges=cut)
    bm.verts.ensure_lookup_table()
    lower_verts = {v.index for f in lower_faces if f.is_valid for v in f.verts}
    bm.to_mesh(me); bm.free()
    me.update()
    # ---- 4. jaw shape key: lower lip/chin block moves down, tapering at corners & towards jaw line ----
    if not me.shape_keys: mesh.shape_key_add(name="Basis")
    sk = mesh.shape_key_add(name="jaw", from_mix=False)
    for v in me.vertices:
        c = v.co; dx = c.x - hx
        if c.y > fy + 0.05: continue
        zl = zline(dx)
        if c.z > zl + 0.004 or c.z < zl - 0.075: continue
        corner = 1 - smooth(half_w * 0.55, half_w + 0.012, abs(dx))
        below = 1.0 if (v.index in lower_verts or c.z < zl - 0.0005) else 0.0
        if below == 0.0:
            # upper lip lifts a hair
            wu = (1 - smooth(0.0, 0.006, c.z - zl)) * corner * (1 - smooth(fy + 0.004, fy + 0.02, c.y))
            sk.data[v.index].co = c + Vector((0, 0, 0.0015 * wu)); continue
        depth = smooth(zl - 0.075, zl - 0.03, c.z)            # fade toward under-chin
        back = 1 - smooth(fy + 0.02, fy + 0.05, c.y)
        wgt = corner * depth * back
        # jaw rotates about a pivot behind/under the ear: approximate as down + slightly back
        sk.data[v.index].co = c + Vector((0, 0.0025 * wgt, -drop * wgt))
    # ---- 5. cavity + teeth parented to head bone ----
    mz0 = zline(0.0)
    def mat(nm, col, rough=0.6, emit=None):
        m = bpy.data.materials.get(nm) or bpy.data.materials.new(nm); m.use_nodes = True
        p = m.node_tree.nodes["Principled BSDF"]; p.inputs["Base Color"].default_value = (*col, 1); p.inputs["Roughness"].default_value = rough
        return m
    coll = mesh.users_collection[0]
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=24, ring_count=12, location=(hx, fy + 0.016, mz0 - 0.004))
    cav = bpy.context.object; cav.name = f"{name}_mouthcav"; cav.scale = (half_w * 1.05, 0.016, 0.012)
    cav.data.materials.append(mat("mouth_inside", (0.16, 0.025, 0.03), 0.5))
    bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=1, vertices=24, location=(hx, fy + 0.006, mz0 + 0.0015))
    th = bpy.context.object; th.name = f"{name}_teeth"; th.scale = (half_w * 0.8, 0.008, 0.0028)
    th.data.materials.append(mat("teeth", (0.92, 0.9, 0.86), 0.3))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=16, ring_count=8, location=(hx, fy + 0.016, mz0 - 0.012))
    tg = bpy.context.object; tg.name = f"{name}_tongue"; tg.scale = (half_w * 0.7, 0.013, 0.005)
    tg.data.materials.append(mat("tongue", (0.75, 0.25, 0.28), 0.45))
    for o in (cav, th, tg):
        for c in o.users_collection: c.objects.unlink(o)
        coll.objects.link(o)
        for p in o.data.polygons: p.use_smooth = True
        mw = o.matrix_world.copy()
        o.parent = arm; o.parent_type = "BONE"; o.parent_bone = hb.name
        o.matrix_world = mw
    # tongue follows jaw: drive its z with the shape key
    d = tg.driver_add("delta_location", 2).driver
    d.type = "SCRIPTED"; v = d.variables.new(); v.name = "j"; v.targets[0].id_type = "KEY"; v.targets[0].id = me.shape_keys
    v.targets[0].data_path = 'key_blocks["jaw"].value'; d.expression = f"-{drop * 0.6:.4f}*j"
    sk.slider_max = 1.0
    return sk, dict(half_w=half_w, cut=len(cut), mz=mz0, fy=fy)
