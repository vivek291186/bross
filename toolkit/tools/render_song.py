# blender -b song01.blend -P render_song.py -- [first last] : full-quality render, scene by scene, skipping done frames
import bpy, json, os, sys, time
D = os.path.dirname(bpy.data.filepath) + "/"
OUTD = D + "frames_sd/"; os.makedirs(OUTD, exist_ok=True)
TL = json.load(open(D + "timeline.json")); FPS = 24
F = lambda t: int(round(t * FPS)) + 1
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
A = int(args[0]) if len(args) > 0 else 1
B = int(args[1]) if len(args) > 1 else F(TL["total"])
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE_NEXT"; sc.render.use_motion_blur = False
ee = sc.eevee; ee.taa_render_samples = int(os.environ.get("BBF_SAMPLES", "24")); ee.use_raytracing = False   # SD: screen-space only
ee.ray_tracing_options.resolution_scale = "2"; ee.use_shadows = True; ee.shadow_ray_count = 1; ee.shadow_step_count = 4
try: ee.shadow_resolution_scale = 0.75
except Exception: pass
for o in sc.objects:
    if o.type == "LIGHT" and any(k in o.name for k in ("fill", "tube", "roof", "top")): o.data.use_shadow = False
sc.render.image_settings.file_format = "JPEG"; sc.render.image_settings.quality = 92
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 854, 480, 100   # SD

# --- quality/speed patch (measured on the Mac: OpenSubdiv limit surface cost 20s/frame; glare mix 0 washes out the image)
for o_ in bpy.data.objects:
    for m_ in o_.modifiers:
        if m_.type == "SUBSURF": m_.render_levels = 1; m_.use_limit_surface = False; m_.quality = 2
        if m_.type == "CORRECTIVE_SMOOTH": m_.iterations = 2; m_.show_render = True
if sc.use_nodes and sc.node_tree:
    for n_ in sc.node_tree.nodes:
        if n_.type == "GLARE":
            if n_.glare_type == "BLOOM": n_.mix = -0.82; n_.threshold = 1.8; n_.size = 6; n_.quality = "MEDIUM"
            elif n_.glare_type == "STREAKS": n_.mix = -0.92; n_.threshold = 3.0; n_.quality = "LOW"
SETCOLS = ["jungle", "beach", "park", "kitchen", "bus", "classroom", "canteen", "living", "balcony", "living_diwali", "balcony_night", "moon"]
vl = sc.view_layers[0]
def only(setname):
    for lc in vl.layer_collection.children:
        if lc.name in SETCOLS: lc.exclude = (lc.name != setname)
log = open(D + "render_log.txt", "a")
scenes = TL["scenes"]
for i, s in enumerate(scenes):
    f0 = F(s["t0"]); f1 = F(scenes[i + 1]["t0"]) if i + 1 < len(scenes) else F(TL["total"]) + 1
    f0, f1 = max(f0, A), min(f1, B + 1)
    if f0 >= f1: continue
    only(s["set"])
    for f in range(f0, f1):
        fn = OUTD + "%05d.jpg" % f
        if os.path.exists(fn) and os.path.getsize(fn) > 10000: continue
        t = time.time(); sc.frame_set(f); sc.render.filepath = fn
        bpy.ops.render.render(write_still=True)
        log.write("%d %.2f\n" % (f, time.time() - t)); log.flush()
open(D + "RENDER_DONE_%d_%d" % (A, B), "w").write("ok")
