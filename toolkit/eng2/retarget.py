# Retarget Meshy (mixamorig, no-skin) clips onto Meshy smartrig characters by copying armature-space bone orientations.
import bpy, glob, os, re
from mathutils import Matrix, Vector

LOCO = ("Walking", "Running", "Sneaky_Walk", "Cautious_Crouch_Walk", "Excited_Walk", "Thoughtful_Walk", "Walk_Slowly", "Skip_Forward", "Sprint")

def clip_name(path):
    m = re.search(r"Animation_(.+?)_(without|with)(_s|S)kin", os.path.basename(path))
    return m.group(1).replace("_", " ") if m else os.path.basename(path)

def load_clip(path):
    """returns (name, frames list of {bone: Matrix armature-space}, hips_rest_height)"""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    arm = [o for o in new if o.type == "ARMATURE"][0]
    act = arm.animation_data.action
    f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
    sc = bpy.context.scene
    names = [pb.name for pb in arm.pose.bones]
    frames = []
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        frames.append({n.split(":")[-1]: arm.pose.bones[n].matrix.copy() for n in names})
    hips_h = frames[0]["Hips"].translation.z
    for o in new: bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.actions.remove(act)
    return clip_name(path), frames, hips_h

def retarget(frames, src_hips_h, tgt_arm, name, loco=False, smooth_root=True):
    bones = tgt_arm.data.bones
    order = []  # hierarchy order
    def walk(b):
        order.append(b)
        for c in b.children: walk(c)
    for b in bones:
        if b.parent is None: walk(b)
    short = {b.name: b.name.split(":")[-1] for b in bones}
    A = {b.name: b.matrix_local.copy() for b in bones}
    A_inv = {k: v.inverted() for k, v in A.items()}
    rel = {b.name: (A_inv[b.parent.name] @ A[b.name]) if b.parent else A[b.name] for b in bones}
    rel_inv = {k: v.inverted() for k, v in rel.items()}
    hips = [b for b in bones if short[b.name] == "Hips"][0]
    tgt_h = A[hips.name].translation.z
    k = tgt_h / src_hips_h
    p0 = frames[0]["Hips"].translation.copy()
    n = len(frames)
    if loco:
        p_end = frames[-1]["Hips"].translation
        drift = (p_end - p0) / max(1, n - 1)
    act = bpy.data.actions.new(name); act.use_fake_user = True
    curves = {}
    def fc(path, idx, grp):
        key = (path, idx)
        if key not in curves:
            c = act.fcurves.new(path, index=idx, action_group=grp); c.keyframe_points.add(n); curves[key] = c
        return curves[key]
    data = {}
    for fi, fr in enumerate(frames):
        P = {}
        for b in order:
            s = short[b.name]
            src = fr.get(s)
            if b.parent is None:
                if src is None: Pb = A[b.name].copy()
                else:
                    d = src.translation - p0
                    if loco: d = d - drift * fi
                    if loco: d.z = d.z
                    pos = A[b.name].translation + Vector((d.x * k, d.y * k, d.z * k))
                    Pb = Matrix.Translation(pos) @ src.to_3x3().to_4x4()
                L = A_inv[b.name] @ Pb
            else:
                Pp = P[b.parent.name]
                head = (Pp @ rel[b.name]).translation
                rot = src.to_3x3().to_4x4() if src is not None else (Pp @ rel[b.name]).to_3x3().to_4x4()
                Pb = Matrix.Translation(head) @ rot
                L = rel_inv[b.name] @ Pp.inverted() @ Pb
            P[b.name] = Pb
            q = L.to_quaternion()
            data.setdefault(b.name, []).append((q, L.translation.copy() if b.parent is None else None))
    for bname, seq in data.items():
        path = f'pose.bones["{bname}"].rotation_quaternion'
        # keep quaternion continuity
        prev = None
        for i, (q, t) in enumerate(seq):
            if prev is not None and prev.dot(q) < 0: q.negate()
            prev = q
            for j in range(4):
                fc(path, j, bname).keyframe_points[i].co = (i + 1, q[j])
            if t is not None:
                for j in range(3):
                    fc(f'pose.bones["{bname}"].location', j, bname).keyframe_points[i].co = (i + 1, t[j])
    for c in act.fcurves:
        for kp in c.keyframe_points: kp.interpolation = "LINEAR"
        c.update()
    act.frame_range = (1, n)
    return act

def import_char(path, name):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    arm = [o for o in new if o.type == "ARMATURE"][0]; mesh = [o for o in new if o.type == "MESH"][0]
    arm.name = name + "_rig"; mesh.name = name + "_body"
    for pb in arm.pose.bones: pb.rotation_mode = "QUATERNION"
    return arm, mesh
