# Merge a Meshy Smart-Rig GLB (68 unnamed bones incl. fingers) onto the Meshy Humanoid FBX (4K textures, quads, 28 named bones).
# Result: FBX with "smartrig:" named bones (same convention as the old characters) + 4K textures beside it.
#   python3 smartmerge.py <humanoid.fbx> <smart.glb> <outdir> <name>
import bpy, sys, os, math
from mathutils import Vector, Matrix

fbx, glb, outdir, name = sys.argv[-4:]
os.makedirs(outdir, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)

def imp(fn):
    before = set(bpy.data.objects)
    fn()
    new = [o for o in bpy.data.objects if o not in before]
    arm = [o for o in new if o.type == "ARMATURE"][0]
    mesh = max([o for o in new if o.type == "MESH"], key=lambda o: len(o.data.vertices))
    for o in new:
        if o not in (arm, mesh): bpy.data.objects.remove(o, do_unlink=True)
    return arm, mesh

armF, meshF = imp(lambda: bpy.ops.import_scene.fbx(filepath=fbx))
armG, meshG = imp(lambda: bpy.ops.import_scene.gltf(filepath=glb))
print("FBX", meshF.name, len(meshF.data.vertices), "GLB", meshG.name, len(meshG.data.vertices), len(armG.data.bones), "bones")

# ---- apply transforms, then scale/offset GLB to match the FBX bounding box ----
for o in (armF, meshF, armG, meshG):
    bpy.context.view_layer.objects.active = o; o.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in bpy.data.objects: o.select_set(False)
def bbox(o):
    vs = [o.matrix_world @ Vector(c) for c in o.bound_box]
    lo = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs)))
    hi = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
    return lo, hi
loF, hiF = bbox(meshF); loG, hiG = bbox(meshG)
s = (hiF.z - loF.z) / (hiG.z - loG.z)
print("scale", s, "fbx height", hiF.z - loF.z, "glb height", hiG.z - loG.z)
cF = (loF + hiF) / 2; cG = (loG + hiG) / 2
M = Matrix.Translation(cF - cG * s) @ Matrix.Scale(s, 4)
for o in (armG, meshG):
    o.matrix_world = M @ o.matrix_world
    bpy.context.view_layer.objects.active = o; o.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True); o.select_set(False)
loG, hiG = bbox(meshG); print("after fit: fbx", loF[:], hiF[:], "glb", loG[:], hiG[:])

# ---- name the smart-rig bones ----
# body bones: nearest head position to the humanoid FBX bones
FBX2SMART = {"Hips": "Hips", "Spine": "Spine", "Spine01": "Spine1", "Spine02": "Spine2", "neck": "Neck", "Head": "Head", "head_end": "HeadTop_End",
             "LeftShoulder": "LeftShoulder", "LeftArm": "LeftArm", "LeftForeArm": "LeftForeArm", "LeftHand": "LeftHand",
             "RightShoulder": "RightShoulder", "RightArm": "RightArm", "RightForeArm": "RightForeArm", "RightHand": "RightHand",
             "LeftUpLeg": "LeftUpLeg", "LeftLeg": "LeftLeg", "LeftFoot": "LeftFoot", "LeftToeBase": "LeftToeBase", "LeftToe_end": "LeftToe_End",
             "RightUpLeg": "RightUpLeg", "RightLeg": "RightLeg", "RightFoot": "RightFoot", "RightToeBase": "RightToeBase", "RightToe_end": "RightToe_End"}
G = {b.name: b for b in armG.data.bones}
heads = {n: armG.matrix_world @ b.head_local for n, b in G.items()}
used = set(); newname = {}
# hips = root's first child with 3 children (or the bone whose head is nearest FBX Hips)
fh = {b.name: armF.matrix_world @ b.head_local for b in armF.data.bones}
def nearest(p, cand):
    return min(cand, key=lambda n: (heads[n] - p).length)
hips = nearest(fh["Hips"], [n for n in G if len(G[n].children) == 3])
newname[hips] = "Hips"; used.add(hips)
root = G[hips].parent
if root: newname[root.name] = "Root"; used.add(root.name)
for fn, sn in FBX2SMART.items():
    if sn == "Hips" or fn not in fh: continue
    n = nearest(fh[fn], [n for n in G if n not in used])
    newname[n] = sn; used.add(n)
# spine chain sanity: all bones between Hips and Neck get Spine, Spine1, Spine2, (Spine3...)
chain = []; b = G[newname and [k for k, v in newname.items() if v == "Neck"][0]].parent
while b and newname.get(b.name) != "Hips":
    chain.append(b.name); b = b.parent
chain.reverse()
for i, n in enumerate(chain): newname[n] = "Spine" if i == 0 else "Spine%d" % i
# fingers: chains hanging from each hand
for side in ("Left", "Right"):
    hand = [k for k, v in newname.items() if v == side + "Hand"][0]
    chains = [c for c in G[hand].children]
    hp = heads[hand]
    # thumb = chain base nearest the hand head (and highest); the rest sorted along the hand's lateral axis (y)
    thumb = min(chains, key=lambda c: (heads[c.name] - hp).length)
    rest = sorted([c for c in chains if c != thumb], key=lambda c: -heads[c.name].y)  # index .. pinky along -y
    order = [("Thumb", thumb)] + list(zip(("Index", "Middle", "Ring", "Pinky"), rest))
    for fname, base in order:
        b = base; i = 1
        while b:
            newname[b.name] = "%sHand%s%d" % (side, fname, i); i += 1
            b = b.children[0] if b.children else None
# headfront helper (old rigs had one): skip; everything else keeps Bone_ name
for n, v in newname.items():
    G[n].name = "smartrig:" + v if v != "Root" else "Root"
print("named", len(newname), "of", len(G), "bones; unnamed:", [n for n in G if n.startswith("Bone_")])

# ---- transfer weights GLB mesh -> FBX mesh ----
# vertex groups on meshG were renamed with the bones (armature modifier keeps them in sync)
bpy.context.view_layer.objects.active = meshF; meshF.select_set(True)
for vg in list(meshF.vertex_groups): meshF.vertex_groups.remove(vg)
dt = meshF.modifiers.new("dt", "DATA_TRANSFER"); dt.object = meshG; dt.use_vert_data = True
dt.data_types_verts = {"VGROUP_WEIGHTS"}; dt.vert_mapping = "POLYINTERP_NEAREST"; dt.layers_vgroup_select_src = "ALL"; dt.layers_vgroup_select_dst = "NAME"
bpy.ops.object.datalayout_transfer(modifier="dt")
bpy.ops.object.modifier_apply(modifier="dt")
# clean tiny weights + normalize
bpy.ops.object.vertex_group_clean(group_select_mode="ALL", limit=0.01)
bpy.ops.object.vertex_group_normalize_all(lock_active=False)
meshF.select_set(False)
# re-parent to the smart armature
for m in list(meshF.modifiers):
    if m.type == "ARMATURE": meshF.modifiers.remove(m)
am = meshF.modifiers.new("Armature", "ARMATURE"); am.object = armG
meshF.parent = armG; meshF.matrix_parent_inverse = armG.matrix_world.inverted()
bpy.data.objects.remove(meshG, do_unlink=True); bpy.data.objects.remove(armF, do_unlink=True)
armG.name = name + "_rig"; meshF.name = name + "_body"
print("vgroups on body:", len(meshF.vertex_groups))

# ---- textures: save the 4K images beside the FBX with the old naming ----
for im in bpy.data.images:
    if im.size[0] == 0: continue
    tag = {"texture_0.png": "texture_0", "texture_0_normal.png": "texture_0_normal", "texture_0_roughness.png": "texture_0_roughness", "texture_0_metallic.png": "texture_0_metallic"}.get(im.name)
    if tag is None: continue
    im.filepath_raw = os.path.join(outdir, "%s_%s.png" % (name, tag)); im.file_format = "PNG"; im.save()
    print("saved", im.filepath_raw, im.size[:])
out = os.path.join(outdir, name + ".fbx")
for o in bpy.data.objects: o.select_set(o in (armG, meshF))
bpy.ops.export_scene.fbx(filepath=out, use_selection=True, add_leaf_bones=False, path_mode="COPY", embed_textures=False, mesh_smooth_type="FACE", bake_anim=False, apply_scale_options="FBX_SCALE_ALL")
print("wrote", out, os.path.getsize(out) // 1024, "KB")
