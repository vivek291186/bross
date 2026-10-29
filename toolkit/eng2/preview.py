# blender -b ep04.blend -P preview.py  : renders a spread of full-quality test frames to preview/ and logs seconds per frame
import bpy, json, os, sys, time
D = os.path.dirname(bpy.data.filepath) + "/"
OUTD = D + "preview/"; os.makedirs(OUTD, exist_ok=True)
TL = json.load(open(D + "timeline.json")); FPS = 24
F = lambda t: int(round(t * FPS)) + 1
CL = json.load(open(D + "camlog.json"))["cams"]
sc = bpy.context.scene
SETCOLS = ["kitchen", "bus", "classroom", "canteen", "living", "balcony", "living_diwali", "balcony_night"]
vl = sc.view_layers[0]
def setname(f):
    return [s for s in TL["scenes"] if F(s["t0"]) <= f][-1]["set"]
def only(setname_):
    for lc in vl.layer_collection.children:
        if lc.name in SETCOLS: lc.exclude = (lc.name != setname_)
# frames: middle of every 4th shot + the VFX moments
frames = sorted({(a + b) // 2 for i, (a, b, n) in enumerate(CL) if i % 4 == 0} | {F(e["t"]) + 30 for e in TL["events"] if e["type"] == "prop" and e["name"] in ("sparkler", "anar", "chakri", "rocket", "diyas", "rangoli")})
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if args: frames = [int(x) for x in args]
log = open(D + "preview_log.txt", "a")
for f in frames:
    only(setname(f)); t = time.time(); sc.frame_set(f); sc.render.filepath = OUTD + "%05d.jpg" % f
    bpy.ops.render.render(write_still=True)
    log.write("%d %.2f\n" % (f, time.time() - t)); log.flush()
open(D + "PREVIEW_DONE", "w").write("ok")
