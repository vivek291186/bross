# v5 character prep for the hi-poly Smart-Rig kids (/home/claude/m3/chars): weld + smooth normals, clean materials,
# skin SSS, talking mouths, blinking eyes/brows, hair shader, light corrective smooth (no subsurf needed at 150-200k quads).
import bpy, bmesh, glob, os, importlib
import retarget as R, mouthfx, eyefx
importlib.reload(mouthfx); importlib.reload(eyefx)

# measured on /home/claude/m3/test/faces_zoom.jpg (cm grid, origin = Head bone head)
MOUTH = {"vanu": (0.004, 0.024, 0.0), "aarav": (0.001, 0.016, -0.002), "vihaan": (0.020, 0.025, 0.0), "himank": (-0.005, 0.030, -0.013), "buddy": (0.0125, 0.025, 0.003)}
MH = {"himank": 0.020, "vanu": 0.011}
EYES = {"vanu": (0.0295, 0.048, 0.017, 0.010, -0.0145), "aarav": (0.0305, 0.055, 0.016, 0.009, -0.002), "vihaan": (0.033, 0.050, 0.018, 0.011, 0.0),
        "himank": (0.026, 0.047, 0.017, 0.010, -0.020), "buddy": (0.032, 0.055, 0.017, 0.0105, 0.003)}
mouthfx.MOUTH.update(MOUTH); mouthfx.MH.update(MH); eyefx.EYES_MANUAL.update(EYES)

def _rss(tag): print("MEM5", tag, int(open("/proc/self/statm").read().split()[1]) * 4 // 1024, "MB", flush=True)

def prep(path, name, outdir):
    _rss("pre " + name)
    arm, mesh = R.import_char(path, name)
    me = mesh.data
    bpy.context.view_layer.objects.active = mesh
    for o in bpy.context.selected_objects: o.select_set(False)
    mesh.select_set(True)
    bpy.ops.mesh.customdata_custom_splitnormals_clear()
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.000002)
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    me.update(); _rss("weld")
    for slot in mesh.material_slots:
        nt = slot.material.node_tree
        for n in nt.nodes:
            if n.type == "NORMAL_MAP": n.inputs["Strength"].default_value = 0.35   # 4K normal map: keep a little cloth detail
        p = [n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"][0]
        rp = glob.glob(os.path.dirname(path) + "/*roughness.png")
        if rp and not p.inputs["Roughness"].links:
            t = nt.nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(rp[0]); t.image.colorspace_settings.name = "Non-Color"
            nt.links.new(t.outputs["Color"], p.inputs["Roughness"])
        p.inputs["Specular IOR Level"].default_value = 0.4
        p.subsurface_method = "RANDOM_WALK_SKIN"
        p.inputs["Subsurface Weight"].default_value = 0.2
        p.inputs["Subsurface Radius"].default_value = (1.0, 0.25, 0.1)
        p.inputs["Subsurface Scale"].default_value = 0.02
    hb = [b for b in arm.data.bones if b.name.endswith(":Head")][0]
    mouth_z = hb.head_local.z + mouthfx.MOUTH[name][0]
    sk, info = mouthfx.build(mesh, arm, name, outdir); _rss("mouth")
    eyes = eyefx.build(mesh, arm, name, mouth_z); _rss("eyes")
    nh = eyefx.hair(mesh, arm, name, mouth_z); _rss("hair")
    cs = mesh.modifiers.new("csmooth", "CORRECTIVE_SMOOTH")
    cs.factor = 0.5; cs.iterations = 3; cs.smooth_type = "LENGTH_WEIGHTED"; cs.use_only_smooth = True; cs.rest_source = "ORCO"
    cs.show_viewport = False
    print(f"[chars5] {name}: eyes={[(round(e['cx'],3), round(e['cz'],3), round(e['rx'],3), round(e['rz'],3)) for e in eyes['eyes']]} hair_verts={nh}", flush=True)
    return arm, mesh, sk, eyes
