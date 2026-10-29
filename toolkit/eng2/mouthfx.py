# Clean talking mouths for Meshy characters without stretching or cutting the mesh.
# Closed: original painted mouth.  Talking: lips inpainted out of the texture + drawn open-mouth sprites pinned to the face.
import bpy, os, math
import numpy as np, cv2
from PIL import Image, ImageDraw
from mathutils import Vector

# per kid: (lip-line height above Head bone head, mouth half width)  -- measured from front face renders
MOUTH = {"vanu": (0.026, 0.0175), "aarav": (0.035, 0.020), "vihaan": (0.029, 0.021), "himank": (0.032, 0.025), "buddy": (0.032, 0.019)}
N = 3   # sprite frames: small, medium, wide

def _base_image_node(mat):
    p = [n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"][0]
    l = p.inputs["Base Color"].links
    return p, (l[0].from_node if l else None)

def _draw_atlas(path, lipc, W, H, name):
    S = 4; fw, fh = 256, int(256 * H / (2 * W))
    im = Image.new("RGBA", (fw * N * S, fh * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    lip = tuple(int(c * 255) for c in lipc) + (255,)
    lipd = tuple(int(c * 255 * 0.8) for c in lipc) + (255,)
    cav = (60, 12, 16, 255); teeth = (238, 232, 222, 255); tongue = (200, 80, 90, 255)
    # decal space: x in [-W, W] -> [0, fw]; z in [mz-0.018, mz+0.012] -> [fh, 0]
    def P(x, z, k): return ((x / (2 * W) + 0.5 + k) * fw * S, (1 - (z + 0.018) / H) * fh * S)
    hw = W / 1.5
    for k, open_ in enumerate((0.0045, 0.008, 0.012)):
        # outer lips: lens shape from corners, upper edge slightly above line, lower edge drops with opening
        def lens(top, bot, w, steps=40):
            pts = []
            for i in range(steps + 1):
                t = -1 + 2 * i / steps; x = t * w
                pts.append(P(x, top * (1 - t * t) ** 0.8, k))
            for i in range(steps, -1, -1):
                t = -1 + 2 * i / steps; x = t * w
                pts.append(P(x, -bot * (1 - t * t) ** 0.7, k))
            return pts
        d.polygon(lens(0.0045, open_ + 0.004, hw * 1.02), fill=lip)
        d.polygon(lens(0.0016, open_, hw * 0.86), fill=cav)
        # teeth along the top of the cavity
        tp = []
        for i in range(31):
            t = -1 + 2 * i / 30; tp.append(P(t * hw * 0.62, 0.0012 * (1 - t * t) ** 0.8, k))
        for i in range(30, -1, -1):
            t = -1 + 2 * i / 30; tp.append(P(t * hw * 0.62, -min(0.0032, open_ * 0.45) * (1 - t * t) ** 0.5, k))
        d.polygon(tp, fill=teeth)
        # tongue at the bottom
        d.ellipse([P(-hw * 0.45, -open_ * 0.55, k)[0], P(0, -open_ * 0.55, k)[1], P(hw * 0.45, 0, k)[0], P(0, -open_ * 1.05, k)[1]], fill=tongue)
        # lip line shading
        d.line([P(-hw * 0.86, 0.0, k), P(hw * 0.86, 0.0, k)], fill=lipd, width=2 * S) if False else None
    im = im.resize((fw * N, fh), Image.LANCZOS)
    im.save(path)
    return fw, fh

def build(mesh, arm, name, outdir):
    me = mesh.data
    hb = [b for b in arm.data.bones if b.name.endswith(":Head")][0]
    hx, hy, hz = hb.head_local
    dz, hw = MOUTH[name]; mz = hz + dz
    W = hw * 1.5; H = 0.03
    near = [v.co for v in me.vertices if abs(v.co.x - hx) < 0.02 and abs(v.co.z - mz) < 0.01]
    fy = min(c.y for c in near)
    mat = mesh.material_slots[0].material; nt = mat.node_tree
    p, tex = _base_image_node(mat)
    img = tex.image
    w, h = img.size
    px = (np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)[::-1, :, :3] * 255).clip(0, 255).astype(np.uint8)
    # --- mask of texture pixels covering the painted lips ---
    uvl = me.uv_layers.active.data
    mask = np.zeros((h, w), np.uint8)
    lipsamples = []
    for poly in me.polygons:
        c = poly.center
        if c.y > fy + 0.015: continue
        e = ((c.x - hx) / (hw * 1.3)) ** 2 + ((c.z - mz) / 0.0105) ** 2
        if e > 1.0: continue
        pts = np.array([[uvl[li].uv[0] * w, (1 - uvl[li].uv[1]) * h] for li in poly.loop_indices], np.int32)
        cv2.fillPoly(mask, [pts], 255)
    mask = cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=2)
    lp = px[mask > 0]
    red = lp[:, 0].astype(float) - (lp[:, 1].astype(float) + lp[:, 2]) / 2
    lipc = (np.median(lp[red > np.percentile(red, 70)], axis=0) / 255.0) if len(lp) else np.array([0.7, 0.4, 0.4])
    bgr = cv2.cvtColor(px, cv2.COLOR_RGB2BGR)
    inp = cv2.inpaint(bgr, mask, 9, cv2.INPAINT_TELEA)
    nm_path = os.path.join(outdir, f"{name}_nomouth.png"); cv2.imwrite(nm_path, inp)
    at_path = os.path.join(outdir, f"{name}_mouths.png"); _draw_atlas(at_path, lipc, W, H, name)
    # --- per-vertex decal coordinates from rest pose ---
    att = me.attributes.new("mouthuv", "FLOAT2", "POINT")
    for i, v in enumerate(me.vertices):
        c = v.co
        if c.y > fy + 0.02 or abs(c.x - hx) > W * 1.2 or abs(c.z - mz) > 0.04: att.data[i].vector = (-10, -10)
        else: att.data[i].vector = ((c.x - hx) / (2 * W) + 0.5, (c.z - (mz - 0.018)) / H)
    # --- shader ---
    t2 = nt.nodes.new("ShaderNodeTexImage"); t2.image = bpy.data.images.load(nm_path); t2.image.colorspace_settings.name = tex.image.colorspace_settings.name
    uvsrc = tex.inputs["Vector"].links[0].from_socket if tex.inputs["Vector"].links else None
    if uvsrc: nt.links.new(uvsrc, t2.inputs["Vector"])
    at = nt.nodes.new("ShaderNodeTexImage"); at.image = bpy.data.images.load(at_path); at.extension = "CLIP"; at.interpolation = "Linear"
    attr = nt.nodes.new("ShaderNodeAttribute"); attr.attribute_name = "mouthuv"; attr.attribute_type = "GEOMETRY"
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(attr.outputs["Vector"], sep.inputs[0])
    idx = nt.nodes.new("ShaderNodeValue"); idx.name = "mouth_idx"
    talk = nt.nodes.new("ShaderNodeValue"); talk.name = "mouth_talk"
    add = nt.nodes.new("ShaderNodeMath"); add.operation = "ADD"; nt.links.new(sep.outputs["X"], add.inputs[0]); nt.links.new(idx.outputs[0], add.inputs[1])
    div = nt.nodes.new("ShaderNodeMath"); div.operation = "DIVIDE"; nt.links.new(add.outputs[0], div.inputs[0]); div.inputs[1].default_value = N
    # keep u inside its own frame: mask when x outside [0,1]
    inx = nt.nodes.new("ShaderNodeMath"); inx.operation = "LESS_THAN"; nt.links.new(sep.outputs["X"], inx.inputs[0]); inx.inputs[1].default_value = 1.0
    inx2 = nt.nodes.new("ShaderNodeMath"); inx2.operation = "GREATER_THAN"; nt.links.new(sep.outputs["X"], inx2.inputs[0]); inx2.inputs[1].default_value = 0.0
    comb = nt.nodes.new("ShaderNodeCombineXYZ"); nt.links.new(div.outputs[0], comb.inputs[0]); nt.links.new(sep.outputs["Y"], comb.inputs[1])
    nt.links.new(comb.outputs[0], at.inputs["Vector"])
    a1 = nt.nodes.new("ShaderNodeMath"); a1.operation = "MULTIPLY"; nt.links.new(at.outputs["Alpha"], a1.inputs[0]); nt.links.new(talk.outputs[0], a1.inputs[1])
    a2 = nt.nodes.new("ShaderNodeMath"); a2.operation = "MULTIPLY"; nt.links.new(a1.outputs[0], a2.inputs[0]); nt.links.new(inx.outputs[0], a2.inputs[1])
    a3 = nt.nodes.new("ShaderNodeMath"); a3.operation = "MULTIPLY"; nt.links.new(a2.outputs[0], a3.inputs[0]); nt.links.new(inx2.outputs[0], a3.inputs[1])
    m1 = nt.nodes.new("ShaderNodeMix"); m1.data_type = "RGBA"
    nt.links.new(talk.outputs[0], m1.inputs[0]); nt.links.new(tex.outputs["Color"], m1.inputs[6]); nt.links.new(t2.outputs["Color"], m1.inputs[7])
    m2 = nt.nodes.new("ShaderNodeMix"); m2.data_type = "RGBA"
    nt.links.new(a3.outputs[0], m2.inputs[0]); nt.links.new(m1.outputs[2], m2.inputs[6]); nt.links.new(at.outputs["Color"], m2.inputs[7])
    nt.links.new(m2.outputs[2], p.inputs["Base Color"])
    # --- drivers from the 'jaw' shape key (subtle 2.5mm chin motion only) ---
    if not me.shape_keys: mesh.shape_key_add(name="Basis")
    sk = mesh.shape_key_add(name="jaw", from_mix=False)
    for v in me.vertices:
        c = v.co
        if c.y > fy + 0.03 or c.z > mz - 0.006 or c.z < mz - 0.06 or abs(c.x - hx) > 0.04: continue
        wgt = (1 - abs(c.x - hx) / 0.04) * min(1.0, (mz - 0.006 - c.z) / 0.01) * min(1.0, (c.z - (mz - 0.06)) / 0.02)
        sk.data[v.index].co = c + Vector((0, 0, -0.0025 * max(0.0, wgt)))
    for node, expr in ((talk, "1.0 if j > 0.06 else 0.0"), (idx, "0.0 if j < 0.35 else (1.0 if j < 0.65 else 2.0)")):
        d = node.outputs[0].driver_add("default_value").driver
        d.type = "SCRIPTED"; v = d.variables.new(); v.name = "j"; v.type = "SINGLE_PROP"
        v.targets[0].id_type = "KEY"; v.targets[0].id = me.shape_keys; v.targets[0].data_path = 'key_blocks["jaw"].value'
        d.expression = expr
    return sk, dict(nomouth=nm_path, atlas=at_path, lipc=[round(float(x), 2) for x in lipc])
