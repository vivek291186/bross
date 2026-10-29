# Song 05 (moon base) props: the countdown board shows each number exactly when it is sung (whisper word times),
# and the rocket blasts off (flame + smoke + rise) on every "Blast off", then is quietly back on the pad for the next one.
# executed inside build8 (has SETS, TL, F, CH, Vector, math, bpy, sets2, vfx, END)
import json, re, vfx
import sets_space
sp = SETS["space"]; c = sp["coll"]; rocket = sp["rocket"]; flames = sp["flames"]; digits = sp["digits"]
W = json.load(open("/mnt/user-data/outputs/song05/whisper.json"))
NUM = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
words = [(re.sub(r"[^a-z]", "", w["word"].lower()), w["start"]) for s in W["segments"] for w in s["words"]]
def vis(o, f, v):
    o.hide_render = not v; o.hide_viewport = not v
    o.keyframe_insert("hide_render", frame=max(1, f)); o.keyframe_insert("hide_viewport", frame=max(1, f))
for d in digits.values(): vis(d, 1, False)
shown = None; last_t = -9
for wd, t in words:
    if wd in NUM:
        if t - last_t < 0.12: continue   # whisper double-hit ("five, five")
        f = F(t)
        if shown is not None: vis(digits[shown], f, False)
        vis(digits[NUM[wd]], f, True); shown = NUM[wd]; last_t = t
# digit pops in with a little scale bounce each time it changes (scale the whole board digit group via each digit object)
for n, d in digits.items():
    d.scale = (1, 1, 1); d.keyframe_insert("scale", frame=1)
# rocket launches: every "blast" word
R0 = rocket.location.copy()
launches = []
for wd, t in words:
    if wd == "blast" and (not launches or t - launches[-1] > 3.0): launches.append(t)
rocket.keyframe_insert("location", frame=1); rocket.keyframe_insert("rotation_euler", frame=1)
for fl in flames: vis(fl, 1, False)
for t in launches:
    f0 = F(t) - 6; n = 24 * 4
    rocket.location = R0; rocket.keyframe_insert("location", frame=f0)
    for fl in flames: vis(fl, f0, True)
    for i in range(0, n + 1, 2):   # shake, then accelerate upward
        u = i / n; z = 0.0 if u < 0.15 else 14.0 * ((u - 0.15) / 0.85) ** 2
        rocket.location = R0 + Vector((0.02 * math.sin(i * 2.1) * (1 - u), 0.02 * math.cos(i * 1.7) * (1 - u), z))
        rocket.keyframe_insert("location", frame=f0 + i)
    for fl in flames: vis(fl, f0 + n + 1, False)
    rocket.location = R0; rocket.keyframe_insert("location", frame=f0 + n + 24 * 3)   # quietly back on the pad 3 s later (off screen)
    rocket.keyframe_insert("location", frame=f0 + n + 24 * 3 - 1) if False else None
    vfx.emitter(f"smoke5_{f0}", tuple(R0 + Vector((0, 0, 0.1))), c, 500, f0, f0 + 40, 60, (0.95, 0.95, 1.0), size=0.12, vel_normal=1.2, vel_rand=1.0, gravity=-0.05, strength=2.0, radius=0.5)
    vfx.flash(f"launch5_{f0}", tuple(R0 + Vector((0, 0, 0.4))), c, f0 + 2, 1500, color=(1.0, 0.6, 0.2), dur=60)
# make the return jump instant (constant interpolation at the return key)
if rocket.animation_data and rocket.animation_data.action:
    for fc in rocket.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
    for t in launches:
        f0 = F(t) - 6; n = 24 * 4
        for fc in rocket.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                if int(kp.co.x) == f0 + n: kp.interpolation = "CONSTANT"
for ob in bpy.data.objects:
    if ob.animation_data and ob.animation_data.action:
        for fc in ob.animation_data.action.fcurves:
            if "hide" in fc.data_path:
                for kp in fc.keyframe_points: kp.interpolation = "CONSTANT"
print("props_song5 ok: numbers", sum(1 for w, _ in words if w in NUM), "launches", [round(t, 1) for t in launches])
