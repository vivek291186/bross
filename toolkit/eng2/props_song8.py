# Song 08 (Let's Go to the Zoo): animals come alive on their lyrics - giraffe nods, elephant trunk swings + sprays, monkeys bounce, penguins waddle.
import json, vfx
gd = SETS["zoo"]; c = gd["coll"]; O = gd["origin"]
LN = json.load(open("/mnt/user-data/outputs/song08/lines.json"))["lines"]
gir = gd["giraffe"]; G0 = gir.rotation_euler.copy(); trunk = gd["trunk"]
for f in range(1, END + 1, 12):
    gir.rotation_euler = (G0.x + 0.08 * math.sin(f / 20), G0.y, G0.z + 0.1 * math.sin(f / 33)); gir.keyframe_insert("rotation_euler", frame=f)
    trunk.rotation_euler = (math.radians(-25) * (0.5 + 0.5 * math.sin(f / 9)), 0, 0.25 * math.sin(f / 13)); trunk.keyframe_insert("rotation_euler", frame=f)
for i, m_ in enumerate(gd["monkeys"]):
    z0 = m_.location.z
    for f in range(1, END + 1, 6):
        m_.location.z = z0 + 0.12 * abs(math.sin(f / 6.0 + i)); m_.keyframe_insert("location", index=2, frame=f)
for j, p in enumerate(gd["penguins"]):
    L0 = p.location.copy()
    for f in range(1, END + 1, 4):
        p.location.x = L0.x + 0.25 * math.sin(f / 40 + j); p.rotation_euler = (0, 0.2 * math.sin(f * 0.5 + j), 0)
        p.keyframe_insert("location", index=0, frame=f); p.keyframe_insert("rotation_euler", frame=f)
for ln in LN:
    if "sprays" in ln["text"]:
        f0 = F(ln["t0"] + 1.0); bpy.context.scene.frame_set(f0); bpy.context.view_layer.update()
        tip = trunk.matrix_world.translation + Vector((0, -0.5, -0.2))
        vfx.emitter(f"spray8_{f0}", tuple(tip), c, 220, f0, f0 + 40, 18, (0.6, 0.85, 1.0), size=0.015, vel_obj=(0, -0.6, 0.9), vel_rand=0.3, gravity=0.6, strength=1.2, radius=0.04)
print("props_song8 ok")
