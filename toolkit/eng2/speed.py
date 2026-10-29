# blender -b ep02.blend -P speed.py : benchmark render settings on a kitchen frame
import bpy, time, os
D = os.path.dirname(bpy.data.filepath) + "/"
sc = bpy.context.scene; ee = sc.eevee
vl = sc.view_layers[0]
for lc in vl.layer_collection.children:
    if lc.name in ("bus", "classroom", "canteen"): lc.exclude = True
sc.frame_set(600)
log = open(D + "speed_log.txt", "w")
def run(tag):
    for i in range(2):
        t = time.time(); sc.render.filepath = D + "speed_%s_%d.jpg" % (tag, i); bpy.ops.render.render(write_still=True)
        log.write("%s %d %.2f\n" % (tag, i, time.time() - t)); log.flush()
ee.taa_render_samples = 32; run("base")
ee.taa_render_samples = 16; run("s16")
ee.use_raytracing = False; run("s16_nort")
try:
    ee.shadow_resolution_scale = 0.5
except Exception as e: log.write("err %s\n" % e)
for o in sc.objects:
    if o.type == "LIGHT" and any(k in o.name for k in ("fill", "rim", "tube", "roof", "top")): o.data.use_shadow = False
run("s16_nort_lowshadow")
ee.use_raytracing = True; run("s16_rt_lowshadow")
log.write("done\n")
