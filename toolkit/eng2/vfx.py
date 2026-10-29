# Fireworks VFX for Blender/Eevee: sparklers, anar (flower pot), chakri, rockets with bursts, far city bursts.
# All based on particle systems rendered as tiny emissive spheres; call bake_all() after the timeline is keyed.
import bpy, math, random
from mathutils import Vector
from sets2 import M, _link

FPS = 24
_inst = {}
def _spark(name, color, strength=40.0, r=1.0):
    """instance object for particles: small emissive sphere (hidden from direct render; only instanced)"""
    key = (name, color)
    if key in _inst: return _inst[key]
    m = bpy.data.materials.new("spark_" + name); m.use_nodes = True; nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"]); em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1); em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs[0], [n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"][0].inputs["Surface"])
    bpy.ops.mesh.primitive_ico_sphere_add(radius=r, subdivisions=1, location=(0, 0, -200))
    o = bpy.context.object; o.name = "sparkinst_" + name; o.data.materials.append(m)
    o.hide_render = True
    _inst[key] = o; return o

def emitter(name, loc, coll, count, f0, f1, life, color, size=0.01, vel_normal=0.0, vel_rand=1.0, vel_obj=(0, 0, 0), gravity=0.5, damp=0.02, strength=40.0, life_rand=0.3, size_rand=0.5, radius=0.01, tangent=0.0):
    bpy.ops.mesh.primitive_ico_sphere_add(radius=radius, subdivisions=2, location=loc)
    e = bpy.context.object; e.name = name; _link(e, coll); e.show_instancer_for_render = False; e.show_instancer_for_viewport = False
    e.hide_render = False
    mod = e.modifiers.new("ps", "PARTICLE_SYSTEM"); ps = e.particle_systems[0]; st = ps.settings
    st.count = count; st.frame_start = f0; st.frame_end = f1; st.lifetime = life; st.lifetime_random = life_rand
    st.emit_from = "FACE"; st.use_emit_random = True; st.distribution = "RAND"
    st.normal_factor = vel_normal; st.factor_random = vel_rand; st.object_align_factor = vel_obj; st.tangent_factor = tangent
    st.physics_type = "NEWTON"; st.mass = 0.02; st.effector_weights.gravity = gravity; st.damping = damp
    st.render_type = "OBJECT"; st.instance_object = _spark(name, color, strength); st.particle_size = size; st.size_random = size_rand
    st.use_rotation_instance = False
    st.display_method = "DOT"
    ps.seed = hash(name) & 0xffff
    return e

def flash(name, loc, coll, f0, peak, color=(1, 0.8, 0.5), dur=6):
    d = bpy.data.lights.new(name, "POINT"); d.energy = 0; d.color = color; d.shadow_soft_size = 0.5
    o = bpy.data.objects.new(name, d); coll.objects.link(o); o.location = loc
    for f, e in ((f0 - 1, 0), (f0 + 1, peak), (f0 + dur, 0)):
        d.energy = e; d.keyframe_insert("energy", frame=f)
    return o

def sparkler(name, parent_arm, bone_name, coll, f0, f1, color=(1.0, 0.92, 0.7)):
    """spark shower at the tip of a stick held in a hand; returns (stick, emitter)"""
    stick = bpy.data.objects.get("bn_spk_" + name.split("_")[-1])
    e = emitter(name + "_em", (0, 0, 0), coll, int((f1 - f0) * 90), f0, f1, 7, color, size=0.004, vel_normal=0.9, vel_rand=1.3, gravity=0.35, damp=0.05, strength=60.0, life_rand=0.5, radius=0.012)
    for o, off in ((stick, Vector((0.0, -0.03, 0.17))), (e, Vector((0.0, -0.03, 0.33)))):
        if o is None: continue
        c = o.constraints.new("CHILD_OF"); c.target = parent_arm; c.subtarget = bone_name
        o.location = off; o.rotation_euler = (math.radians(-20), 0, 0)
        c.inverse_matrix.identity()
    if stick:
        stick.hide_render = False; stick.hide_viewport = False
    # tip glow
    g = bpy.data.lights.new(name + "_glow", "POINT"); g.energy = 0; g.color = color; g.shadow_soft_size = 0.05
    go = bpy.data.objects.new(name + "_glow", g); coll.objects.link(go)
    c = go.constraints.new("CHILD_OF"); c.target = parent_arm; c.subtarget = bone_name; go.location = Vector((0.0, -0.03, 0.33)); c.inverse_matrix.identity()
    for f, en in ((f0 - 1, 0), (f0 + 2, 18), (f1 - 2, 18), (f1 + 1, 0)):
        g.energy = en; g.keyframe_insert("energy", frame=f)
    return stick, e

def anar(name, tip, coll, f0, dur_s=3.5, color=(1.0, 0.75, 0.25)):
    f1 = f0 + int(dur_s * FPS)
    e = emitter(name, tip, coll, 4500, f0, f1, 22, color, size=0.012, vel_normal=0.0, vel_rand=1.2, vel_obj=(0, 0, 4.5), gravity=1.0, damp=0.04, strength=45.0, life_rand=0.4, radius=0.02)
    # rising intensity: second emitter for the big middle part
    e2 = emitter(name + "_big", tip, coll, 3000, f0 + int(0.8 * FPS), f1 - int(0.6 * FPS), 26, (1.0, 0.55, 0.15), size=0.016, vel_rand=1.6, vel_obj=(0, 0, 6.5), gravity=1.0, damp=0.04, strength=45.0, radius=0.03)
    g = bpy.data.lights.new(name + "_lt", "POINT"); g.energy = 0; g.color = color; g.shadow_soft_size = 0.3
    go = bpy.data.objects.new(name + "_lt", g); coll.objects.link(go); go.location = Vector(tip) + Vector((0, 0, 0.6))
    for f, en in ((f0 - 1, 0), (f0 + 6, 150), (f0 + int(1.5 * FPS), 400), (f1 - 4, 120), (f1 + 6, 0)):
        g.energy = en; g.keyframe_insert("energy", frame=f)
    return e, e2

def chakri(name, obj, coll, f0, dur_s=3.0, color=(1.0, 0.85, 0.4)):
    f1 = f0 + int(dur_s * FPS)
    obj.rotation_euler = (0, 0, 0); obj.keyframe_insert("rotation_euler", frame=f0)
    obj.rotation_euler = (0, 0, math.radians(360 * 14)); obj.keyframe_insert("rotation_euler", frame=f1)
    for fc in obj.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
    loc = obj.location.copy() + Vector((0, 0, 0.02))
    e = emitter(name, loc, coll, 3500, f0, f1, 9, color, size=0.006, vel_normal=0.0, vel_rand=0.6, vel_obj=(0, 0, 0.8), gravity=0.6, damp=0.05, strength=50.0, radius=0.06, tangent=3.5)
    e.parent = obj
    g = bpy.data.lights.new(name + "_lt", "POINT"); g.energy = 0; g.color = color; g.shadow_soft_size = 0.2
    go = bpy.data.objects.new(name + "_lt", g); coll.objects.link(go); go.location = loc + Vector((0, 0, 0.25))
    for f, en in ((f0 - 1, 0), (f0 + 4, 120), (f1 - 4, 120), (f1 + 4, 0)):
        g.energy = en; g.keyframe_insert("energy", frame=f)
    return e

def rocket(name, launch, burst, coll, f0, rise_s=1.3, color=(1.0, 0.3, 0.4), big=1.0):
    """rocket from launch point to burst point, trail + spherical burst + flash"""
    fb = f0 + int(rise_s * FPS)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.01 * big, depth=0.12 * big, location=launch)
    body = bpy.context.object; body.name = name + "_body"; _link(body, coll); body.data.materials.append(M("rocket_body", (0.9, 0.2, 0.2), 0.5))
    body.hide_render = True; body.keyframe_insert("hide_render", frame=f0 - 2)
    body.hide_render = False; body.keyframe_insert("hide_render", frame=f0 - 1)
    body.location = launch; body.keyframe_insert("location", frame=f0)
    body.location = burst; body.keyframe_insert("location", frame=fb)
    body.hide_render = True; body.keyframe_insert("hide_render", frame=fb)
    for fc in body.animation_data.action.fcurves:
        if fc.data_path == "location":
            for kp in fc.keyframe_points: kp.interpolation = "BEZIER"; kp.easing = "EASE_IN"
    tr = emitter(name + "_trail", launch, coll, 900, f0, fb, 10, (1.0, 0.8, 0.5), size=0.012 * big, vel_rand=0.4, gravity=0.3, damp=0.1, strength=35.0, radius=0.01)
    tr.parent = body
    e = emitter(name + "_burst", burst, coll, int(420 * big), fb, fb + 1, int(1.7 * FPS), color, size=0.03 * big, vel_normal=0.0, vel_rand=5.5 * big, gravity=0.35, damp=0.12, strength=40.0, life_rand=0.35, radius=0.05)
    e2 = emitter(name + "_burst2", burst, coll, int(220 * big), fb + 1, fb + 2, int(1.3 * FPS), (1.0, 0.95, 0.8), size=0.02 * big, vel_rand=3.5 * big, gravity=0.35, damp=0.1, strength=50.0, radius=0.05)
    flash(name + "_flash", burst, coll, fb, 2500 * big, color, 8)
    return body, e

def bake_all():
    try:
        bpy.ops.ptcache.bake_all(bake=True)
    except Exception as ex:
        print("bake_all failed:", ex)

def compositor_bloom(sc, threshold=1.2, size=7, mix=0.0, streaks=False):
    sc.use_nodes = True; nt = sc.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    rl = nt.nodes.new("CompositorNodeRLayers"); out = nt.nodes.new("CompositorNodeComposite")
    gl = nt.nodes.new("CompositorNodeGlare"); gl.glare_type = "BLOOM"; gl.threshold = threshold; gl.size = size; gl.mix = mix; gl.quality = "HIGH"
    nt.links.new(rl.outputs["Image"], gl.inputs["Image"])
    last = gl.outputs["Image"]
    if streaks:
        st = nt.nodes.new("CompositorNodeGlare"); st.glare_type = "STREAKS"; st.threshold = 2.5; st.streaks = 4; st.angle_offset = math.radians(15); st.mix = -0.4; st.quality = "MEDIUM"
        nt.links.new(last, st.inputs["Image"]); last = st.outputs["Image"]
    # gentle vignette + warmth
    cb = nt.nodes.new("CompositorNodeColorBalance"); cb.correction_method = "LIFT_GAMMA_GAIN"; cb.gain = (1.03, 1.0, 0.96); cb.lift = (1.0, 1.0, 1.01)
    nt.links.new(last, cb.inputs["Image"]); last = cb.outputs["Image"]
    nt.links.new(last, out.inputs["Image"])
    return nt
