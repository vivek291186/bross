# exec in Blender console: join parts, verify, extract, start full Ep3 render in background (Mac kept awake)
import os, hashlib, tarfile, subprocess, bpy
P = os.path.expanduser("~/Downloads/.bbf/ep03pack/")
ROOT = os.path.expanduser("~/Downloads/.bbf/")
parts = ["part_%02d" % i for i in range(8)]
tarp = P + "pkg.tar"
with open(tarp, "wb") as o:
    for x in parts: o.write(open(P + x, "rb").read())
md5 = hashlib.md5(open(tarp, "rb").read()).hexdigest()
ok = md5 == open(P + "pkg.md5").read().strip()
st = open(P + "STATUS.txt", "w"); st.write("md5 %s ok=%s\n" % (md5, ok))
if ok:
    with tarfile.open(tarp) as t: t.extractall(ROOT)
    os.remove(tarp)
    D = ROOT + "ep03/"
    log = open(D + "render_out.txt", "w")
    pr = subprocess.Popen([bpy.app.binary_path, "-b", D + "ep03.blend", "-P", D + "render2.py"], stdout=log, stderr=subprocess.STDOUT)
    subprocess.Popen(["caffeinate", "-dimsu", "-w", str(pr.pid)])
    st.write("render started pid %d\n" % pr.pid)
st.close()
