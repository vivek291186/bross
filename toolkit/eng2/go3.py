# exec in Blender console: apply update pack, then start the full Episode 2 render in the background (Mac kept awake)
import os, hashlib, tarfile, subprocess, shutil, bpy
P = os.path.expanduser("~/Downloads/.bbf/ep02pack/")
ROOT = os.path.expanduser("~/Downloads/.bbf/")
D = ROOT + "ep02/"
parts = ["part_%02d" % i for i in range(5)]
tarp = P + "upd.tar"
with open(tarp, "wb") as o:
    for x in parts: o.write(open(P + x, "rb").read())
md5 = hashlib.md5(open(tarp, "rb").read()).hexdigest()
ok = md5 == open(P + "pkg.md5").read().strip()
st = open(P + "STATUS3.txt", "w"); st.write("md5 %s ok=%s\n" % (md5, ok))
if ok:
    with tarfile.open(tarp) as t: t.extractall(ROOT)
    os.remove(tarp)
    # move stale test frames aside (rendered with old settings)
    os.makedirs(D + "old_test", exist_ok=True)
    for f in os.listdir(D + "frames"): shutil.move(D + "frames/" + f, D + "old_test/" + f)
    log = open(D + "render_out.txt", "w")
    pr = subprocess.Popen([bpy.app.binary_path, "-b", D + "ep02.blend", "-P", D + "render2.py"], stdout=log, stderr=subprocess.STDOUT)
    subprocess.Popen(["caffeinate", "-dimsu", "-w", str(pr.pid)])
    st.write("render started pid %d\n" % pr.pid)
st.close()
