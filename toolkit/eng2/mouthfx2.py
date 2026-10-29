# Mouth v2 for Meshy characters: 7-viseme shaded sprite atlas + real 3D jaw opening + phoneme-driven selection.
# Builds on mouthfx (lip inpainting / decal frame) but replaces the atlas, the jaw key and the drivers.
import bpy, os, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
from mathutils import Vector
import mouthfx

# atlas frames
REST, MBP, SMALL, MED, WIDE, ROUND, EE = range(7)
N = 7

def _lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))

def draw_atlas(path, lipc, W, H):
    """W: mouth half width (decal spans [-W,W]); H: decal height (z from mz-0.018 to mz+0.012)"""
    S = 4; fw, fh = 256, int(256 * H / (2 * W))
    im = Image.new("RGBA", (fw * N * S, fh * S), (0, 0, 0, 0))
    lip = tuple(int(c * 255) for c in lipc) + (255,)
    lipd = tuple(int(c * 255 * 0.72) for c in lipc) + (255,)   # lower lip shadow / lip line
    lipl = tuple(min(255, int(c * 255 * 1.18)) for c in lipc) + (255,)   # highlight
    cav = (52, 10, 14, 255); cav2 = (28, 5, 8, 255); teeth = (242, 238, 228, 255); teethd = (205, 196, 184, 255); tongue = (205, 85, 95, 255); tongued = (170, 60, 70, 255)
    def P(x, z, k): return ((x / (2 * W) + 0.5 + k) * fw * S, (1 - (z + 0.018) / H) * fh * S)
    hw = W / 1.5
    # (half width factor, upper lip rise, opening, lower lip thickness, teeth visible, tongue, corner lift)
    SHAPES = {REST: (1.0, 0.0038, 0.0, 0.0042, 0, 0, 0.0025), MBP: (0.92, 0.0030, 0.0, 0.0034, 0, 0, 0.001),
              SMALL: (0.95, 0.0045, 0.004, 0.0042, 1, 0, 0.002), MED: (1.0, 0.0050, 0.0085, 0.0045, 1, 1, 0.002),
              WIDE: (1.05, 0.0055, 0.0135, 0.0048, 1, 1, 0.001), ROUND: (0.62, 0.0060, 0.0095, 0.0055, 0, 1, -0.002), EE: (1.15, 0.0040, 0.0030, 0.0036, 1, 0, 0.0035)}
    for k in range(N):
        wf, rise, op, lt, tv, tg, corner = SHAPES[k]
        w = hw * wf
        d = ImageDraw.Draw(im)
        def curve(top, bot, w, steps=48, bow=True):
            pts = []
            for i in range(steps + 1):
                t = -1 + 2 * i / steps; x = t * w
                z = top * (1 - t * t) ** 0.75 + corner * (t * t)
                if bow: z -= top * 0.18 * math.exp(-(t * 7) ** 2)   # cupid's bow dip at the centre
                pts.append(P(x, z, k))
            for i in range(steps, -1, -1):
                t = -1 + 2 * i / steps; x = t * w
                pts.append(P(x, -bot * (1 - t * t) ** 0.65 + corner * (t * t), k))
            return pts
        # outer lips
        d.polygon(curve(rise, op + lt, w * 1.02), fill=lip)
        # lower lip shade band + highlight on the lower lip
        d.polygon(curve(-op * 0.98 + 0.0004, op + lt, w * 0.98, bow=False), fill=lipd)
        d.polygon(curve(-op * 0.98 - lt * 0.15, op + lt * 0.72, w * 0.9, bow=False), fill=lip)
        d.polygon(curve(-op * 0.98 - lt * 0.35, op + lt * 0.55, w * 0.7, bow=False), fill=lipl)
        # upper lip body (darker underside)
        d.polygon(curve(rise, op * 0.98 - 0.0003, w * 0.98), fill=lip)
        d.polygon(curve(rise * 0.45, op * 0.98, w * 0.95), fill=lipd)
        if op > 0:
            # cavity
            d.polygon(curve(0.0012, op, w * 0.86, bow=False), fill=cav)
            d.polygon(curve(0.0006, op * 0.55, w * 0.8, bow=False), fill=cav2)
            if tv:
                tp = []
                for i in range(31):
                    t = -1 + 2 * i / 30; tp.append(P(t * w * 0.66, 0.0014 * (1 - t * t) ** 0.8, k))
                for i in range(30, -1, -1):
                    t = -1 + 2 * i / 30; tp.append(P(t * w * 0.66, -min(0.0034, op * 0.42) * (1 - t * t) ** 0.45, k))
                d.polygon(tp, fill=teeth)
                # tooth separations
                for t in (-0.6, -0.36, -0.12, 0.12, 0.36, 0.6):
                    x = t * w * 0.66
                    d.line([P(x, 0.001, k), P(x, -min(0.0034, op * 0.42) * (1 - t * t) ** 0.45 * 0.9, k)], fill=teethd, width=S)
            if tg:
                d.ellipse([P(-w * 0.42, -op * 0.5, k)[0], P(0, -op * 0.5, k)[1], P(w * 0.42, 0, k)[0], P(0, -op * 1.08, k)[1]], fill=tongue)
                d.ellipse([P(-w * 0.3, -op * 0.72, k)[0], P(0, -op * 0.72, k)[1], P(w * 0.3, 0, k)[0], P(0, -op * 1.06, k)[1]], fill=tongued)
        else:
            # closed: lip line
            pts = [P(t * w * 0.96, 0.0002 * (1 - t * t) + corner * 0.6 * t * t - 0.0003, k) for t in np.linspace(-1, 1, 40)]
            d.line(pts, fill=lipd, width=int(2.2 * S))
    im = im.resize((fw * N, fh), Image.LANCZOS)
    # soften the alpha edge a touch so the decal blends into the skin
    r, g, b, a = im.split(); a = a.filter(ImageFilter.GaussianBlur(0.6)); im = Image.merge("RGBA", (r, g, b, a))
    im.save(path)
    return fw, fh

def upgrade(mesh, arm, name, outdir, info):
    """replace the v1 atlas/drivers on an already mouthfx-built mesh. info: dict from mouthfx.build (atlas path, lipc)."""
    me = mesh.data
    hb = [b for b in arm.data.bones if b.name.endswith(":Head")][0]
    hx, hy, hz = hb.head_local
    dz, hw, *rest = mouthfx.MOUTH[name]; mz = hz + dz
    hx += rest[0] if rest else 0.0
    W = hw * 1.5; H = 0.03
    near = [v.co for v in me.vertices if abs(v.co.x - hx) < 0.02 and abs(v.co.z - mz) < 0.01]
    fy = min(c.y for c in near)
    # new atlas
    at_path = info["atlas"]; draw_atlas(at_path, np.array(info["lipc"], float), W, H)
    mat = mesh.material_slots[0].material; nt = mat.node_tree
    at = [n for n in nt.nodes if n.type == "TEX_IMAGE" and n.image and n.image.filepath == at_path or (n.type == "TEX_IMAGE" and n.image and os.path.basename(n.image.filepath) == os.path.basename(at_path))][0]
    at.image.reload()
    # divide by new frame count
    for n in nt.nodes:
        if n.type == "MATH" and n.operation == "DIVIDE" and abs(n.inputs[1].default_value - mouthfx.N) < 0.01: n.inputs[1].default_value = N
    # --- real 3D jaw: chin + lower lip region drops (up to 9 mm) and swings slightly back ---
    jaw = me.shape_keys.key_blocks["jaw"]
    for v in me.vertices:
        c = v.co
        jaw.data[v.index].co = c
        if c.y > fy + 0.065 or c.z > mz + 0.004 or c.z < mz - 0.085 or abs(c.x - hx) > 0.05: continue
        wx = max(0.0, 1 - (abs(c.x - hx) / 0.05) ** 2)
        wz = min(1.0, (mz + 0.004 - c.z) / 0.012) * min(1.0, (c.z - (mz - 0.085)) / 0.03)
        wy = min(1.0, max(0.0, (fy + 0.065 - c.y) / 0.03))
        wgt = wx * wz * wy
        jaw.data[v.index].co = c + Vector((0, 0.0025 * wgt, -0.009 * wgt))
    # --- viseme channel: a geometry-less shape key 'vis' (0..6) ---
    vis = mesh.shape_key_add(name="vis", from_mix=False); vis.slider_max = 10.0
    for n in nt.nodes:
        if n.name in ("mouth_idx", "mouth_talk"):
            n.outputs[0].driver_remove("default_value")
            d = n.outputs[0].driver_add("default_value").driver; d.type = "SCRIPTED"
            v = d.variables.new(); v.name = "j"; v.type = "SINGLE_PROP"; v.targets[0].id_type = "KEY"; v.targets[0].id = me.shape_keys; v.targets[0].data_path = 'key_blocks["jaw"].value'
            v2 = d.variables.new(); v2.name = "s"; v2.type = "SINGLE_PROP"; v2.targets[0].id_type = "KEY"; v2.targets[0].id = me.shape_keys; v2.targets[0].data_path = 'key_blocks["vis"].value'
            d.expression = "round(s)" if n.name == "mouth_idx" else "1.0 if s > 0.5 or j > 0.08 else 0.0"
    return vis

# viseme name (lipsync5) -> atlas frame, base jaw opening
VMAP = {"p_b_m_21": (MBP, 0.0), "f_v_18": (SMALL, 0.08), "th_dh_17": (SMALL, 0.12), "d_t_n_19": (SMALL, 0.12), "k_g_ng_20": (SMALL, 0.15), "s_z_15": (EE, 0.08), "sh_ch_jh_zh_16": (ROUND, 0.15), "l_14": (SMALL, 0.18), "r_13": (ROUND, 0.12), "h_12": (MED, 0.3),
        "y_iy_ih_ix_06": (EE, 0.15), "ey_eh_uh_04": (MED, 0.35), "er_05": (ROUND, 0.3), "aa_02": (WIDE, 0.7), "aa_ah_ax_01": (MED, 0.5), "ao_03": (ROUND, 0.5), "ow_08": (ROUND, 0.45), "w_uw_07": (ROUND, 0.3), "ay_11": (WIDE, 0.6), "aw_09": (WIDE, 0.6), "oy_10": (ROUND, 0.5)}

def key_speech(mesh, phones, t_offset, fps, gain=1.0):
    """keyframe 'jaw' (openness) and 'vis' (atlas index) from lipsync5.align() output; t_offset: seconds where the clip starts"""
    kb = mesh.data.shape_keys.key_blocks; jaw, vis = kb["jaw"], kb["vis"]
    F = lambda t: int(round((t + t_offset) * fps)) + 1
    if not phones: return
    f_start, f_end = F(phones[0][0]) - 3, F(phones[-1][0]) + 4
    jaw.value = 0.0; vis.value = 0.0
    jaw.keyframe_insert("value", frame=f_start); vis.keyframe_insert("value", frame=f_start)
    vis.value = REST; vis.keyframe_insert("value", frame=f_start + 1)
    last_f = None
    for i, (t, v, loud) in enumerate(phones):
        f = F(t)
        if last_f is not None and f <= last_f: f = last_f + 1
        last_f = f
        if v is None:
            idx, op = REST, 0.0
        else:
            idx, op = VMAP.get(v, (SMALL, 0.2)); op = min(1.0, op * (0.55 + 0.75 * loud) * gain)
            if idx in (MED, WIDE) and loud < 0.25: idx = SMALL
        vis.value = idx; vis.keyframe_insert("value", frame=f)
        jaw.value = round(op, 3); jaw.keyframe_insert("value", frame=f)
    vis.value = REST; vis.keyframe_insert("value", frame=f_end - 1); jaw.value = 0.0; jaw.keyframe_insert("value", frame=f_end - 1)
    vis.value = 0.0; vis.keyframe_insert("value", frame=f_end); jaw.keyframe_insert("value", frame=f_end)
    ad = mesh.data.shape_keys.animation_data
    for fc in ad.action.fcurves:
        if 'key_blocks["vis"]' in fc.data_path:
            for kp in fc.keyframe_points: kp.interpolation = "CONSTANT"
        elif 'key_blocks["jaw"]' in fc.data_path:
            for kp in fc.keyframe_points: kp.interpolation = "BEZIER"; kp.easing = "AUTO"
