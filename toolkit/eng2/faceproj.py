# MPFB2 cast builder: shape a kid, then project the reference portrait onto the face UVs so the skin texture carries the real likeness.
import bpy, sys, importlib, os, math, json
import numpy as np, cv2
from mathutils import Vector

def dyn(p, k):
    for amod in list(sys.modules):
        if amod.endswith(p): return getattr(importlib.import_module(amod), k)

ASSETS = "/home/claude/m4/assets"
TARGETS = None

def services():
    global TARGETS
    S = dict(Human=dyn("mpfb.services.humanservice", "HumanService"), Target=dyn("mpfb.services.targetservice", "TargetService"),
             Asset=dyn("mpfb.services.assetservice", "AssetService"), HOP=dyn("mpfb.entities.objectproperties", "HumanObjectProperties"),
             Loc=dyn("mpfb.services.locationservice", "LocationService"))
    TARGETS = S["Loc"].get_mpfb_data("targets")
    return S

def build_kid(name, macros, targets, skin, hair, clothes, eyes="high-poly.mhclo", eyebrows="eyebrow004.mhclo", eyelashes="eyelashes02.mhclo", eye_mat="brown.mhmat"):
    S = services()
    h = S["Human"].create_human(); h.name = name
    for k, v in macros.items(): S["HOP"].set_value(k, v, entity_reference=h)
    S["Target"].reapply_macro_details(h)
    for grp, tname, w in targets:
        S["Target"].load_target(h, os.path.join(TARGETS, grp, tname + ".target.gz"), weight=w)
    rig = S["Human"].add_builtin_rig(h, "mixamo")
    for pb in rig.pose.bones: pb.rotation_mode = "QUATERNION"
    S["Human"].set_character_skin(S["Asset"].find_asset_absolute_path(skin, asset_subdir="skins"), h, skin_type="ENHANCED_SSS")
    items = [("eyes", eyes, "Eyes"), ("eyebrows", eyebrows, "Eyebrows"), ("eyelashes", eyelashes, "Eyelashes"), ("teeth", "teeth_base.mhclo", "Teeth"), ("tongue", "tongue01.mhclo", "Tongue")]
    if hair: items.append(("hair", hair, "Hair"))
    for c in clothes: items.append(("clothes", c, "Clothes"))
    for subdir, fname, atype in items:
        p = S["Asset"].find_asset_absolute_path(fname, asset_subdir=subdir)
        if p: S["Human"].add_mhclo_asset(p, h, asset_type=atype)
        else: print("MISSING asset", subdir, fname)
    # visemes + face units as shape keys
    for sub in ("visemes", "faceunits"):
        d = f"{ASSETS}/targets/{sub}"
        for f in sorted(os.listdir(d)):
            if f.endswith(".target"): S["Target"].load_target(h, f"{d}/{f}", weight=0.0, name=f"{sub}:{f[:-7]}")
    return h, rig

def eval_verts(h):
    dg = bpy.context.evaluated_depsgraph_get(); me = h.evaluated_get(dg).data
    return np.array([list(h.matrix_world @ v.co) for v in me.vertices], np.float32), me

def model_landmarks(h):
    """eye centres from the eye objects, mouth centre from the lips material polygons, chin + top of head"""
    V, me = eval_verts(h)
    top = V[:, 2].max()
    head = V[V[:, 2] > top - 0.28]
    eyesobj = [o for o in bpy.data.objects if o.parent in (h, h.parent) and "poly" in o.name.lower() and o.type == "MESH"]
    dg = bpy.context.evaluated_depsgraph_get()
    ev = np.array([list(eyesobj[0].matrix_world @ v.co) for v in eyesobj[0].evaluated_get(dg).data.vertices])
    left = ev[ev[:, 0] < ev[:, 0].mean()]; right = ev[ev[:, 0] >= ev[:, 0].mean()]
    eyeL, eyeR = left.mean(0), right.mean(0)   # eyeL = character's left (= +x in Blender when facing -y)
    lips_idx = [i for i, m in enumerate(h.data.materials) if m and m.name.endswith(".lips")]
    lp = [p for p in me.polygons if p.material_index in lips_idx]
    mouth = np.mean([V[i] for p in lp for i in p.vertices], 0) if lp else (eyeL + eyeR) / 2 + np.array([0, 0, -0.06])
    front = head[(np.abs(head[:, 0] - mouth[0]) < 0.015)]
    chin = front[front[:, 2] < mouth[2] - 0.02]; chin = chin[chin[:, 1].argsort()][: max(1, len(chin) // 10)]   # most forward low verts
    chin = np.array([mouth[0], chin[:, 1].mean(), chin[:, 2].min()])
    return dict(eyeL=eyeL, eyeR=eyeR, mouth=mouth, chin=chin, top=top, face_y=front[:, 1].min())

def photo_landmarks(img):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY); cc = cv2.data.haarcascades
    fs = cv2.CascadeClassifier(cc + "haarcascade_frontalface_default.xml").detectMultiScale(g, 1.05, 3, minSize=(60, 60))
    x, y, w, hh = max(fs, key=lambda r: r[2] * r[3]) if len(fs) else (0, 0, img.shape[1], img.shape[0])
    es = cv2.CascadeClassifier(cc + "haarcascade_eye.xml").detectMultiScale(g[y:y + int(hh * 0.65), x:x + w], 1.05, 5, minSize=(int(w * 0.1), int(w * 0.1)))
    es = sorted([(x + ex + ew / 2, y + ey + eh / 2) for ex, ey, ew, eh in es], key=lambda e: e[0])
    if len(es) >= 2: eL, eR = es[0], es[-1]
    else: eL, eR = (x + w * 0.32, y + hh * 0.42), (x + w * 0.68, y + hh * 0.42)
    # mouth: lip redness centroid in the lower face box
    sub = img[y + int(hh * 0.62): y + int(hh * 0.92), x + int(w * 0.25): x + int(w * 0.75)].astype(int)
    red = sub[..., 2] - (sub[..., 1] + sub[..., 0]) / 2
    m = red > np.percentile(red, 92)
    ys, xs = np.where(m); mouth = (x + w * 0.25 + xs.mean(), y + hh * 0.62 + ys.mean()) if len(xs) else (x + w / 2, y + hh * 0.78)
    return dict(eyeL=np.array(eL, float), eyeR=np.array(eR, float), mouth=np.array(mouth, float), box=(x, y, w, hh))

def similarity(src_pts, dst_pts):
    """2D similarity (scale, rotation, translation) least squares, src->dst (Nx2)"""
    s = np.asarray(src_pts, float); d = np.asarray(dst_pts, float)
    sm, dm = s.mean(0), d.mean(0); s0, d0 = s - sm, d - dm
    a = (s0 * d0).sum(); b = (s0[:, 0] * d0[:, 1] - s0[:, 1] * d0[:, 0]).sum(); n = (s0 ** 2).sum()
    sc = math.hypot(a, b) / n; th = math.atan2(b, a)
    R = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]]) * sc
    t = dm - R @ sm
    return R, t

def project_face(h, photo_path, out_tex_path, feather=0.012, debug=None):
    """paint the reference face onto the body's diffuse texture. Photo pixel (u,v) <-> world (x,z) via similarity on eye/mouth landmarks."""
    img = cv2.imread(photo_path); H, W = img.shape[:2]
    lm = model_landmarks(h); pl = photo_landmarks(img)
    # photo: the character's left eye appears on the viewer's RIGHT; world +x is the character's left when facing -y
    src = [pl["eyeR"], pl["eyeL"], pl["mouth"]]          # photo pixels (viewer right = char left)
    dst = [[lm["eyeL"][0], lm["eyeL"][2]], [lm["eyeR"][0], lm["eyeR"][2]], [lm["mouth"][0], lm["mouth"][2]]]
    R, t = similarity(src, dst)              # photo px -> world (x,z)
    Rinv = np.linalg.inv(R)
    def world_to_px(x, z): return Rinv @ (np.array([x, z]) - t)
    # texture
    mat = [m for m in h.data.materials if m and m.name.endswith(".body")][0]
    tex = [n for n in mat.node_tree.nodes if n.type == "TEX_IMAGE" and n.image and "diffuse" in n.image.name.lower()]
    if not tex: tex = [n for n in mat.node_tree.nodes if n.type == "TEX_IMAGE" and n.image]
    im = tex[0].image; TW, TH = im.size
    base = (np.array(im.pixels[:], np.float32).reshape(TH, TW, 4)[::-1, :, :3] * 255).clip(0, 255).astype(np.uint8)   # RGB top-down
    base_bgr = cv2.cvtColor(base, cv2.COLOR_RGB2BGR)
    V, me = eval_verts(h); uv = me.uv_layers.active.data
    # skin colour match: photo cheek vs texture cheek (sample under the eyes)
    cheek_px = [(pl["eyeL"] + pl["eyeR"]) / 2 + np.array([-(pl["eyeR"][0] - pl["eyeL"][0]) * 0.75, (pl["mouth"][1] - pl["eyeL"][1]) * 0.45]),
                (pl["eyeL"] + pl["eyeR"]) / 2 + np.array([(pl["eyeR"][0] - pl["eyeL"][0]) * 0.75, (pl["mouth"][1] - pl["eyeL"][1]) * 0.45])]
    pc = np.mean([img[int(p[1]) - 4:int(p[1]) + 5, int(p[0]) - 4:int(p[0]) + 5].reshape(-1, 3).mean(0) for p in cheek_px], 0)
    # texture cheek: polygons near the cheek in world
    out = base_bgr.copy().astype(np.float32); acc = np.zeros((TH, TW), np.float32)
    face_c = (lm["eyeL"] + lm["eyeR"]) / 2; fy = lm["face_y"]
    tex_cheek = []
    nrm = np.array([list(p.normal) for p in me.polygons], np.float32)
    for p in me.polygons:
        if p.material_index != [i for i, m in enumerate(h.data.materials) if m and m.name.endswith(".body")][0] and p.material_index not in [i for i, m in enumerate(h.data.materials) if m and m.name.endswith((".lips", ".ears"))]: continue
        vs = [V[i] for i in p.vertices]; c = np.mean(vs, 0)
        if c[2] < lm["chin"][2] - 0.01 or c[2] > lm["top"] + 0.01 or abs(c[0] - face_c[0]) > 0.11 or c[1] > fy + 0.075: continue
        n = p.normal
        if n.y > -0.15: continue
        # per-polygon blend weight: facing and distance from the face centre
        w_face = min(1.0, max(0.0, (-n.y - 0.15) / 0.45))
        dx = abs(c[0] - face_c[0]) / 0.085; dz = (c[2] - face_c[2]) / 0.11 if c[2] > face_c[2] else (face_c[2] - c[2]) / 0.13
        w_dist = 1.0 - max(0.0, (math.hypot(dx, dz) - 0.85) / 0.35)
        w = max(0.0, min(1.0, w_face * w_dist))
        if w <= 0: continue
        # triangles fan
        loops = list(p.loop_indices); vidx = list(p.vertices)
        for k in range(1, len(vidx) - 1):
            tri_v = [vidx[0], vidx[k], vidx[k + 1]]; tri_l = [loops[0], loops[k], loops[k + 1]]
            src_px = np.array([world_to_px(V[i][0], V[i][2]) for i in tri_v], np.float32)
            dst_px = np.array([[uv[l].uv[0] * TW, (1 - uv[l].uv[1]) * TH] for l in tri_l], np.float32)
            if (src_px[:, 0] < 0).any() or (src_px[:, 1] < 0).any() or (src_px[:, 0] >= W).any() or (src_px[:, 1] >= H).any(): continue
            M = cv2.getAffineTransform(src_px, dst_px)
            x0, y0 = np.floor(dst_px.min(0)).astype(int) - 1; x1, y1 = np.ceil(dst_px.max(0)).astype(int) + 2
            x0, y0 = max(0, x0), max(0, y0); x1, y1 = min(TW, x1), min(TH, y1)
            if x1 <= x0 or y1 <= y0: continue
            Mo = M.copy(); Mo[:, 2] -= [x0, y0]
            warped = cv2.warpAffine(img, Mo, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            mask = np.zeros((y1 - y0, x1 - x0), np.float32); cv2.fillConvexPoly(mask, np.round(dst_px - [x0, y0]).astype(np.int32), 1.0)
            if mask.sum() == 0: continue
            mask *= w
            out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * (1 - mask[..., None]) + warped.astype(np.float32) * mask[..., None]
            acc[y0:y1, x0:x1] = np.maximum(acc[y0:y1, x0:x1], mask)
            if 0.55 < dz < 0.75 and 0.5 < dx < 0.9: tex_cheek.append(p.index)
    # tint the untouched skin toward the photo's cheek colour (ratio in linear-ish space)
    tc = base_bgr[acc < 0.05]
    face_tex_cheek = np.mean([base_bgr[int((1 - uv[l].uv[1]) * TH) % TH, int(uv[l].uv[0] * TW) % TW] for pi in tex_cheek[:200] for l in me.polygons[pi].loop_indices], 0) if tex_cheek else base_bgr.reshape(-1, 3).mean(0)
    ratio = (pc + 1) / (face_tex_cheek + 1)
    tinted = (base_bgr.astype(np.float32) * ratio).clip(0, 255)
    out = out * acc[..., None] + tinted * (1 - acc[..., None])
    # feather the projected region edge
    soft = cv2.GaussianBlur(acc, (0, 0), max(1, int(TW * feather)))
    out = out * soft[..., None] + tinted * (1 - soft[..., None])
    cv2.imwrite(out_tex_path, out.clip(0, 255).astype(np.uint8))
    newim = bpy.data.images.load(out_tex_path); newim.colorspace_settings.name = im.colorspace_settings.name
    for m in h.data.materials:
        if not m or not m.node_tree: continue
        for n in m.node_tree.nodes:
            if n.type == "TEX_IMAGE" and n.image == im: n.image = newim
    if debug:
        dbg = img.copy()
        for k_, c_ in (("eyeL", (0, 255, 0)), ("eyeR", (0, 0, 255)), ("mouth", (255, 0, 0))): cv2.circle(dbg, tuple(np.round(pl[k_]).astype(int)), 5, c_, 2)
        cv2.imwrite(debug, dbg)
    return dict(photo=pl, model={k: (v.tolist() if hasattr(v, "tolist") else v) for k, v in lm.items()}, cheek_photo=pc.tolist(), covered=float((acc > 0.5).mean()))
