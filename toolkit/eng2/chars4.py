# v4 character prep: chars3 (weld, clean normals, talking mouths) + smooth deformation, skin SSS, blinking eyes/brows, hair shader.
import bpy, importlib
import chars3, mouthfx, eyefx
importlib.reload(eyefx)

def prep(path, name, outdir):
    arm, mesh, sk = chars3.prep(path, name, outdir)
    me = mesh.data
    hb = [b for b in arm.data.bones if b.name.endswith(":Head")][0]
    mouth_z = hb.head_local.z + mouthfx.MOUTH[name][0]
    # skin: real subsurface, no plastic sheen
    for slot in mesh.material_slots:
        p = [n for n in slot.material.node_tree.nodes if n.type == "BSDF_PRINCIPLED"][0]
        p.subsurface_method = "RANDOM_WALK_SKIN"
        p.inputs["Subsurface Weight"].default_value = 0.2
        p.inputs["Subsurface Radius"].default_value = (1.0, 0.25, 0.1)
        p.inputs["Subsurface Scale"].default_value = 0.02
        p.inputs["Specular IOR Level"].default_value = 0.4
    eyes = eyefx.build(mesh, arm, name, mouth_z)
    nh = eyefx.hair(mesh, arm, name, mouth_z)
    # deformation: corrective smooth after the armature, then subdivision for smooth joints/silhouettes
    cs = mesh.modifiers.new("csmooth", "CORRECTIVE_SMOOTH")
    cs.factor = 0.6; cs.iterations = 8; cs.smooth_type = "LENGTH_WEIGHTED"; cs.use_only_smooth = True; cs.rest_source = "ORCO"
    sd = mesh.modifiers.new("subd", "SUBSURF"); sd.levels = 1; sd.render_levels = 2; sd.use_limit_surface = True
    print(f"[chars4] {name}: eyes={[(round(e['cx'],3), round(e['cz'],3), round(e['rx'],3), round(e['rz'],3)) for e in eyes['eyes']]} hair_verts={nh}")
    return arm, mesh, sk, eyes
