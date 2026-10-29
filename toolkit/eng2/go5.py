# exec in Blender console after render: verify frames, then build the final MP4 in the background
import os, subprocess, json, bpy
D = os.path.expanduser("~/Downloads/.bbf/ep02/")
tl = json.load(open(D + "timeline.json")); N = int(round(tl["total"] * 24)) + 1
bad = [f for f in range(1, N + 1) if not os.path.exists(D + "frames/%05d.jpg" % f) or os.path.getsize(D + "frames/%05d.jpg" % f) < 20000]
st = open(D + "VSE_STATUS.txt", "w"); st.write("frames expected %d bad/missing %d %s\n" % (N, len(bad), bad[:30]))
if not bad:
    log = open(D + "vse_out.txt", "w")
    subprocess.Popen([bpy.app.binary_path, "-b", "-P", D + "vse2.py"], stdout=log, stderr=subprocess.STDOUT)
    st.write("vse started\n")
st.close()
