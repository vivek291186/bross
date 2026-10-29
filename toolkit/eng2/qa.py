# QA pass on a built episode blend: python3 qa.py <blend> <camlog.json>
# flags (a) hands intersecting another kid's head, (b) close/two shots where target heads are blocked or out of frame
import bpy, json, sys, math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
blend, camlog = sys.argv[1], sys.argv[2]
bpy.ops.wm.open_mainfile(filepath=blend)
sc = bpy.context.scene; cam = sc.camera
KIDS = ["vanu", "aarav", "vihaan", "himank", "buddy"]
ARM = {}
for o in bpy.data.objects:
    if o.type == "ARMATURE":
        for k in KIDS:
            if o.name.lower().startswith(k): ARM[k] = o
def bone(k, short):
    a = ARM[k]
    for pb in a.pose.bones:
        if pb.name.split(":")[-1] == short: return a.matrix_world @ pb.head
    return None
CL = json.load(open(camlog))["cams"]
def visible(k):  # kid has hips above floor-ish and is not parked far away
    h = bone(k, "Head"); return h is not None and h.z > -5
hand_flags, occ_flags = [], []
for (f0, f1, spec) in CL:
    for f in range(f0, f1, 4):
        sc.frame_set(f)
        pres = [k for k in ARM if visible(k)]
        heads = {k: bone(k, "Head") for k in pres}
        # hands into heads
        for k in pres:
            for hs in ("LeftHand", "RightHand", "LeftForeArm", "RightForeArm"):
                hp = bone(k, hs)
                if hp is None: continue
                for o in pres:
                    if o == k: continue
                    hc = heads[o] + Vector((0, 0, 0.07))
                    if abs((hp - heads[o]).x) < 3 and (hp - hc).length < 0.12:
                        hand_flags.append((f, spec, k, hs, o))
        # occlusion / framing
        if spec.startswith(("close:", "two:")):
            tg = [x for x in spec.split(":")[1:] if x in heads]
            cp = cam.matrix_world.translation
            for t in tg:
                H = heads[t] + Vector((0, 0, 0.05))
                v = world_to_camera_view(sc, cam, H)
                if not (0.03 < v.x < 0.97 and 0.05 < v.y < 0.98 and v.z > 0):
                    occ_flags.append((f, spec, "out", t, round(v.x, 2), round(v.y, 2))); continue
                ab = H - cp
                for o in pres:
                    if o in tg: continue
                    for bs in ("Head", "Neck", "Spine2", "Spine1", "Spine", "Hips"):
                        p = bone(o, bs)
                        if p is None: continue
                        if bs == "Head": p = p + Vector((0, 0, 0.07))
                        u = (p - cp).dot(ab) / ab.length_squared
                        r = 0.11 if bs == "Head" else 0.13
                        if 0.05 < u < 0.97 and (cp + ab * u - p).length < r:
                            occ_flags.append((f, spec, "blocked", t, o, bs)); break
json.dump({"hand": hand_flags, "occ": occ_flags}, open(blend + ".qa.json", "w"))
def summarize(fl, key):
    out = {}
    for x in fl:
        sh = [c for c in CL if c[0] <= x[0] < c[1]][0]
        out.setdefault((sh[0], sh[1], sh[2]), []).append(x[0])
    for k, v in sorted(out.items()): print(key, k, len(v), v[:6])
summarize(hand_flags, "HAND"); summarize(occ_flags, "OCC")
print("shots", len(CL))
