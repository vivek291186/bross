# procedural "jaw open" shape key for Meshy characters (no face rig)
import bpy
from mathutils import Vector

MOUTH_DZ = {"vanu": 0.026, "aarav": 0.037, "vihaan": 0.029, "himank": 0.034, "buddy": 0.032}

def smooth(a, b, x):
    if b == a: return 1.0 if x >= b else 0.0
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)

def add_jaw(mesh, arm, name, drop=0.009):
    hb = [b for b in arm.data.bones if b.name.endswith(":Head")][0]
    hz = hb.head_local.z; hx = hb.head_local.x
    mz = hz + MOUTH_DZ.get(name, 0.03)
    me = mesh.data
    # front surface depth: min y of verts near the mouth
    near = [v.co for v in me.vertices if abs(v.co.x - hx) < 0.03 and abs(v.co.z - mz) < 0.02]
    fy = min(c.y for c in near)
    if not me.shape_keys: mesh.shape_key_add(name="Basis")
    sk = mesh.shape_key_add(name="jaw", from_mix=False)
    n = 0
    for i, v in enumerate(me.vertices):
        c = v.co
        if c.y > fy + 0.035: continue                       # only the face front
        if c.z > mz + 0.004 or c.z < mz - 0.07: continue
        dx = abs(c.x - hx)
        if dx > 0.055: continue
        w = 1.0 - smooth(mz - 0.0015, mz + 0.0025, c.z)       # below lip line = 1
        w *= smooth(mz - 0.07, mz - 0.03, c.z)                # fade towards chin bottom
        w *= 1.0 - smooth(0.028, 0.055, dx)                   # fade at cheeks
        w *= 1.0 - smooth(fy + 0.015, fy + 0.035, c.y)        # fade going back
        if w <= 0: continue
        sk.data[i].co = c + Vector((0, -0.002 * w, -drop * w))
        n += 1
    sk.slider_max = 1.0
    return sk, n
