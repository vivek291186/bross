# Build the character + animation library (bbf_lib.blend) from the finished episode/song blends.
# Characters (rig, body with shape keys + mouth materials) come from ep12; every retargeted "kid|Clip" action from ep07+ blends.
import bpy, glob, re, os, json
KIDS = ["vanu", "aarav", "vihaan", "himank", "buddy"]
def norm(s): return re.sub(r"[^a-z0-9]", "", re.sub(r"\.\d{3}$", "", s).lower().replace(".fbx", ""))
bpy.ops.wm.read_factory_settings(use_empty=True)
BASE = "/mnt/user-data/outputs/ep12/ep12.blend"
with bpy.data.libraries.load(BASE, link=False) as (src, dst):
    dst.objects = [n for n in src.objects if any(n == f"{k}_rig" or n == f"{k}_body" for k in KIDS)]
for o in dst.objects:
    bpy.context.scene.collection.objects.link(o)
    if o.type == "ARMATURE": o.animation_data_clear(); o.location = (0, 0, 0); o.rotation_euler = (0, 0, 0)
    if o.type == "MESH" and o.data.shape_keys and o.data.shape_keys.animation_data: o.data.shape_keys.animation_data_clear()
for im in bpy.data.images:
    fn = os.path.basename(im.filepath)
    if os.path.exists(f"/home/claude/lib/tex/{fn}"): im.filepath = f"/home/claude/lib/tex/{fn}"
# hips heights
HH = {k: [b for b in bpy.data.objects[f"{k}_rig"].data.bones if b.name.endswith("Hips")][0].head_local.z for k in KIDS}
# actions: newest blend wins
blends = sorted(glob.glob("/mnt/user-data/outputs/ep*/ep*.blend") + glob.glob("/mnt/user-data/outputs/song*/song*.blend"), key=os.path.getmtime, reverse=True)
have = {}
for p in blends:
    with bpy.data.libraries.load(p, link=False) as (src, dst):
        want = []
        for a in src.actions:
            if "|" not in a: continue
            k, c = a.split("|", 1)
            if k in KIDS and (k, norm(c)) not in have: want.append(a); have[(k, norm(c))] = None
        dst.actions = want
    for a in dst.actions:
        if a is None: continue
        if not any("mixamorig:" in fc.data_path for fc in a.fcurves):   # older smartrig actions -> drop
            k, c = a.name.split("|", 1); have.pop((k, norm(c)), None); bpy.data.actions.remove(a); continue
        k, c = a.name.split("|", 1); a.name = f"{k}|{norm(c)}"; a.use_fake_user = True; have[(k, norm(c))] = a.name
    print("loaded", os.path.basename(p), len(have))
clips = sorted({c for (k, c) in have})
json.dump({"hips": HH, "clips": {c: [k for k in KIDS if (k, c) in have] for c in clips}}, open("/home/claude/lib/lib_index.json", "w"), indent=0)
bpy.ops.wm.save_as_mainfile(filepath="/home/claude/lib/bbf_lib.blend", compress=False)
print("LIB saved: clips", len(clips), "actions", len([a for a in bpy.data.actions if "|" in a.name]))
