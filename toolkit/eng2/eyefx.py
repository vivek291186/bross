# Eyes + hair for Meshy characters: blinking eyelids and eyebrow raises (no mesh cutting), plus a hair shader mask.
# Eyes are found from the painted texture (bright eye whites); lids are drawn in the shader through a per-vertex "eyeuv" frame.
import bpy, math
import numpy as np
from mathutils import Vector

def _tex_and_uv(mesh):
    me = mesh.data; mat = mesh.material_slots[0].material
    p = [n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"][0]
    base = None
    for n in mat.node_tree.nodes:
        if n.type == "TEX_IMAGE" and n.image and n.image.colorspace_settings.name != "Non-Color" and "nomouth" not in n.image.name and "mouths" not in n.image.name:
            base = n.image; break
    w, h = base.size
    px = np.array(base.pixels[:], dtype=np.float32).reshape(h, w, 4)[:, :, :3]
    uvl = me.uv_layers.active.data
    vuv = {}
    for poly in me.polygons:
        for li, vi in zip(poly.loop_indices, poly.vertices):
            vuv.setdefault(vi, uvl[li].uv.copy())
    def samp(vi):
        uv = vuv.get(vi)
        if uv is None: return None
        x = min(w - 1, max(0, int(uv[0] % 1.0 * w))); y = min(h - 1, max(0, int(uv[1] % 1.0 * h)))
        return px[y, x]
    return p, base, samp

def build(mesh, arm, name, mouth_z):
    me = mesh.data
    hb = [b for b in arm.data.bones if b.name.endswith(":Head")][0]
    hx, hy, hz = hb.head_local
    p, base, samp = _tex_and_uv(mesh)
    nt = mesh.material_slots[0].material.node_tree
    # ---- find eye whites: bright, unsaturated, on the front of the face above the mouth ----
    front = [v for v in me.vertices if (Vector((v.co.x, v.co.y, v.co.z)) - Vector((hx, hy, hz))).length < 0.16 and v.co.z > mouth_z + 0.015 and v.co.z < mouth_z + 0.075]
    fy = min(v.co.y for v in front)
    cand = []
    for v in front:
        if v.co.y > fy + 0.03: continue
        c = samp(v.index)
        if c is None: continue
        L = 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]; sat = c.max() - c.min()
        if L > 0.62 and sat < 0.22: cand.append(v)
    eyes = []
    for side in (-1, 1):
        vs = [v for v in cand if (v.co.x - hx) * side > 0.004]
        if len(vs) < 3: continue
        xs = np.array([v.co.x for v in vs]); zs = np.array([v.co.z for v in vs])
        cx, cz = float(np.median(xs)), float(np.median(zs))
        keep = (np.abs(xs - cx) < 0.02) & (np.abs(zs - cz) < 0.012)
        xs, zs = xs[keep], zs[keep]
        if len(xs) < 3: continue
        cx, cz = float(xs.mean()), float(zs.mean())
        rx = min(0.021, max(0.011, float(np.abs(xs - cx).max()) * 1.45 + 0.003))
        rz = min(0.013, max(0.0065, float(np.abs(zs - cz).max()) * 1.7 + 0.003))
        # lid skin colour: texture just above the eye
        above = [samp(v.index) for v in front if abs(v.co.x - cx) < rx and cz + rz * 1.2 < v.co.z < cz + rz * 2.4 and v.co.y < fy + 0.03]
        above = [a for a in above if a is not None and (a.max() - a.min()) > 0.05]
        skin = np.median(np.array(above), axis=0) if above else np.array([0.75, 0.55, 0.45])
        eyes.append(dict(cx=cx, cz=cz, rx=rx, rz=rz, skin=[float(x) for x in skin]))
    if not eyes: raise RuntimeError(f"no eyes found for {name}")
    skin = np.mean([e["skin"] for e in eyes], axis=0) * 0.93
    # ---- per-vertex eye frame ----
    att = me.attributes.new("eyeuv", "FLOAT2", "POINT")
    for v in me.vertices:
        att.data[v.index].vector = (-10.0, -10.0)
        if v.co.y > fy + 0.035 or abs(v.co.z - hz) > 0.2: continue
        for e in eyes:
            u = (v.co.x - e["cx"]) / e["rx"]; w_ = (v.co.z - e["cz"]) / e["rz"]
            if u * u + w_ * w_ < 2.6: att.data[v.index].vector = (u, w_); break
    # ---- shader: lid from the top, lash line, inside the ellipse only ----
    src = p.inputs["Base Color"].links[0].from_socket
    attr = nt.nodes.new("ShaderNodeAttribute"); attr.attribute_name = "eyeuv"; attr.attribute_type = "GEOMETRY"
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(attr.outputs["Vector"], sep.inputs[0])
    blink = nt.nodes.new("ShaderNodeValue"); blink.name = "blink"; blink.outputs[0].default_value = 0.0
    def m(op, a, b=None, v=None):
        n = nt.nodes.new("ShaderNodeMath"); n.operation = op
        if isinstance(a, float): n.inputs[0].default_value = a
        else: nt.links.new(a, n.inputs[0])
        if b is not None:
            if isinstance(b, float): n.inputs[1].default_value = b
            else: nt.links.new(b, n.inputs[1])
        if v is not None: n.inputs[2].default_value = v
        return n.outputs[0]
    u2 = m("MULTIPLY", sep.outputs["X"], sep.outputs["X"]); v2 = m("MULTIPLY", sep.outputs["Y"], sep.outputs["Y"])
    r2 = m("ADD", u2, v2); inside = m("LESS_THAN", r2, 1.08)
    lidline = m("ADD", m("MULTIPLY", blink.outputs[0], -2.4), 1.1)         # 1.1 (open) -> -1.3 (closed)
    lid = m("MULTIPLY", m("GREATER_THAN", sep.outputs["Y"], lidline), inside)
    lash = m("MULTIPLY", lid, m("LESS_THAN", sep.outputs["Y"], m("ADD", lidline, 0.32)))
    lidc = nt.nodes.new("ShaderNodeRGB"); lidc.outputs[0].default_value = (*[float(x) for x in skin], 1.0)
    lashc = nt.nodes.new("ShaderNodeRGB"); lashc.outputs[0].default_value = (0.09, 0.05, 0.04, 1.0)
    mx1 = nt.nodes.new("ShaderNodeMix"); mx1.data_type = "RGBA"; nt.links.new(lid, mx1.inputs[0]); nt.links.new(src, mx1.inputs[6]); nt.links.new(lidc.outputs[0], mx1.inputs[7])
    mx2 = nt.nodes.new("ShaderNodeMix"); mx2.data_type = "RGBA"; nt.links.new(m("MULTIPLY", lash, 0.75), mx2.inputs[0]); nt.links.new(mx1.outputs[2], mx2.inputs[6]); nt.links.new(lashc.outputs[0], mx2.inputs[7])
    nt.links.new(mx2.outputs[2], p.inputs["Base Color"])
    # ---- eyebrow raise shape key ----
    if not me.shape_keys: mesh.shape_key_add(name="Basis")
    sk = mesh.shape_key_add(name="brows", from_mix=False)
    for v in me.vertices:
        if v.co.y > fy + 0.035: continue
        best = 0.0
        for e in eyes:
            dx = abs(v.co.x - e["cx"]) / (e["rx"] * 1.6); dz = (v.co.z - (e["cz"] + e["rz"] * 1.9)) / (e["rz"] * 1.3)
            wgt = max(0.0, 1 - dx * dx) * max(0.0, 1 - dz * dz)
            best = max(best, wgt)
        if best > 0: sk.data[v.index].co = v.co + Vector((0, 0, 0.0055 * best))
    # blink driver: shape key "blink" (no geometry) drives the shader value so it can be keyframed like everything else
    bk = mesh.shape_key_add(name="blink", from_mix=False)
    d = blink.outputs[0].driver_add("default_value").driver
    d.type = "SCRIPTED"; var = d.variables.new(); var.name = "b"; var.type = "SINGLE_PROP"
    var.targets[0].id_type = "KEY"; var.targets[0].id = me.shape_keys; var.targets[0].data_path = 'key_blocks["blink"].value'
    d.expression = "b"
    return dict(eyes=eyes, brows=sk, blink=bk)

def hair(mesh, arm, name, mouth_z):
    """Mask dark pixels around the head as hair and give them a glossy anisotropic shader."""
    me = mesh.data
    hb = [b for b in arm.data.bones if b.name.endswith(":Head")][0]
    hx, hy, hz = hb.head_local
    p, base, samp = _tex_and_uv(mesh)
    mat = mesh.material_slots[0].material; nt = mat.node_tree
    att = me.attributes.new("hair", "FLOAT", "POINT")
    n_hair = 0
    for v in me.vertices:
        att.data[v.index].value = 0.0
        d = (v.co - Vector((hx, hy, hz))).length
        if d > 0.34 or v.co.z < hz - 0.16: continue
        c = samp(v.index)
        if c is None: continue
        L = 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
        # front-of-face dark pixels (brows, irises, nostrils) are small; exclude the eye/mouth band on the front
        if L < 0.30 and not (v.co.y < hy - 0.03 and mouth_z - 0.02 < v.co.z < mouth_z + 0.075 and abs(v.co.x - hx) < 0.05):
            att.data[v.index].value = 1.0; n_hair += 1
    out = [n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"][0]
    hp = nt.nodes.new("ShaderNodeBsdfPrincipled")
    col = p.inputs["Base Color"].links[0].from_socket
    nt.links.new(col, hp.inputs["Base Color"])
    hp.inputs["Roughness"].default_value = 0.32; hp.inputs["Specular IOR Level"].default_value = 0.7
    hp.inputs["Anisotropic"].default_value = 0.85; hp.inputs["Anisotropic Rotation"].default_value = 0.25
    hp.inputs["Coat Weight"].default_value = 0.35; hp.inputs["Coat Roughness"].default_value = 0.15
    if p.inputs["Normal"].links: nt.links.new(p.inputs["Normal"].links[0].from_socket, hp.inputs["Normal"])
    attr = nt.nodes.new("ShaderNodeAttribute"); attr.attribute_name = "hair"; attr.attribute_type = "GEOMETRY"
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(attr.outputs["Fac"], mix.inputs[0]); nt.links.new(p.outputs[0], mix.inputs[1]); nt.links.new(hp.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return n_hair
