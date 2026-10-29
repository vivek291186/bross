# Run with: blender -b ep02.blend -P render2.py -- [first_frame last_frame]
# Renders Episode 2 to frames/####.jpg scene by scene (only that scene's set enabled). Skips frames already done.
import bpy, json, os, sys, time
D = os.path.dirname(bpy.data.filepath) + "/"
OUTD = D + "frames/"; os.makedirs(OUTD, exist_ok=True)
TL = json.load(open(D + "timeline.json")); FPS = 24
F = lambda t: int(round(t * FPS)) + 1
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
A = int(args[0]) if len(args) > 0 else 1
B = int(args[1]) if len(args) > 1 else F(TL["total"])
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE_NEXT"
sc.render.use_motion_blur = False
sc.render.image_settings.file_format = "JPEG"; sc.render.image_settings.quality = 92
SETCOLS = ["kitchen", "bus", "classroom", "canteen"]
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
        t = time.time()
        sc.frame_set(f); sc.render.filepath = fn
        bpy.ops.render.render(write_still=True)
        log.write("%d %.2f\n" % (f, time.time() - t)); log.flush()
open(D + "RENDER_DONE_%d_%d" % (A, B), "w").write("ok")
