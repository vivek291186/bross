# exec in Blender console: joins parts, verifies, extracts to ~/Downloads/.bbf/, renders a timing test frame in the background
import os, hashlib, tarfile, subprocess, bpy
P = os.path.expanduser("~/Downloads/.bbf/ep02pack/")
ROOT = os.path.expanduser("~/Downloads/.bbf/")
parts = sorted(x for x in os.listdir(P) if x.startswith("part_"))
tarp = P + "pkg.tar"
with open(tarp, "wb") as o:
    for x in parts:
        o.write(open(P + x, "rb").read())
md5 = hashlib.md5(open(tarp, "rb").read()).hexdigest()
ok = md5 == open(P + "pkg.md5").read().strip()
open(P + "STATUS.txt", "w").write("md5 %s ok=%s parts=%d\n" % (md5, ok, len(parts)))
if ok:
    with tarfile.open(tarp) as t: t.extractall(ROOT)
    os.remove(tarp)
    D = ROOT + "ep02/"
    log = open(D + "test_log.txt", "w")
    subprocess.Popen([bpy.app.binary_path, "-b", D + "ep02.blend", "-P", D + "render2.py", "--", "600", "601"], stdout=log, stderr=log)
    open(P + "STATUS.txt", "a").write("extracted + test render started\n")
