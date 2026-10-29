# Song 02 (beach) props: executed inside build8 (has SETS, TL, F, vfx, Vector, math, bpy, sets2)
import vfx
bch = SETS["beach"]; O = bch["origin"]; c = bch["coll"]
MK = TL.get("marks", {})
fS = F(MK["splash"]); fC = F(MK["crab_in"])
# --- orange crab: scuttles sideways in from the right towards Buddy, then dashes away after the splash ---
crab = bch["crab"]
path = [(1, (5.8, -1.0)), (fC, (5.8, -1.0)), (fC + 70, (3.3, -0.9)), (fS - 30, (2.7, -0.6)), (fS + 6, (2.6, -0.6)), (fS + 60, (6.5, -1.6))]
for (fa, pa), (fb, pb) in zip(path, path[1:]):
    for f in range(fa, fb + 1, 2):
        k = (f - fa) / max(1, fb - fa); x = pa[0] + (pb[0] - pa[0]) * k; y = pa[1] + (pb[1] - pa[1]) * k
        moving = (pa != pb)
        crab.location = (O.x + x, O.y + y, 0.012 * abs(math.sin(f * 0.9)) if moving else 0.0)
        crab.rotation_euler = (0, 0, 0.12 * math.sin(f * 0.45) if moving else 0.0)
        crab.keyframe_insert("location", frame=f); crab.keyframe_insert("rotation_euler", frame=f)
# camera for the crab insert follows where the crab really is during Buddy's verse
bch["cams"]["insert:crab"] = ((O.x + 3.4, O.y - 2.7, 0.55), (O.x + 3.0, O.y - 0.8, 0.15), 36)
# --- green beach ball: small happy bounces ---
ball = bch["ball"]; bz = ball.location.z
for f in range(1, F(TL["total"]) + 2, 3):
    ball.location.z = bz + 0.10 * abs(math.sin(f / 18.0 * math.pi)); ball.rotation_euler = (0, 0, f * 0.03)
    ball.keyframe_insert("location", frame=f, index=2); ball.keyframe_insert("rotation_euler", frame=f, index=2)
# --- the SPLASH: a frothy wave rushes up the sand to Buddy, bursts into droplets, then slides back ---
BXY = Vector((O.x + 2.1, O.y + 0.9, 0))
wm = sets2.M("bch_wavefx", (0.55, 0.85, 1.0), 0.1, emit=(0.8, 0.95, 1.0), emit_str=0.4, coat=1.0)
fm = sets2.M("bch_foamfx", (1, 1, 1), 0.6, emit=(1, 1, 1), emit_str=0.5)
wave = bpy.data.objects.new("splash_wave", None); c.objects.link(wave)
body = sets2.sph("splash_wave_body", 1.0, (0, 0, 0), wm, c, scale=(1.6, 0.55, 0.45), seg=24); body.parent = wave
for i in range(7):
    a = i / 7 * math.pi
    s_ = sets2.sph(f"splash_wave_foam{i}", 0.28, (math.cos(a) * 1.3, -0.1, 0.35 + 0.12 * math.sin(a)), fm, c, seg=12); s_.parent = wave
keys = [(fS - 22, 6.8, 0.05), (fS - 2, 0.8, 1.0), (fS + 4, 0.5, 1.15), (fS + 14, 2.5, 0.6), (fS + 30, 6.8, 0.05)]
wave.location = (BXY.x, O.y + 6.8, 0); wave.scale = (0.05, 0.05, 0.05)
for f, y, s in [(1, 6.8, 0.001)] + keys + [(fS + 31, 6.8, 0.001)]:
    wave.location = (BXY.x, BXY.y + (y - 0.9 if y < 6 else y - 0.9), 0); wave.scale = (s, s, s)
    wave.keyframe_insert("location", frame=f); wave.keyframe_insert("scale", frame=f)
vfx.emitter("splash_drops", (BXY.x, BXY.y - 0.2, 0.4), c, 260, fS - 1, fS + 5, 26, (0.75, 0.92, 1.0), size=0.035, vel_normal=0.0,
            vel_rand=3.2, vel_obj=(0, -1.2, 3.2), gravity=1.0, strength=2.5, radius=0.35)
vfx.emitter("splash_mist", (BXY.x, BXY.y, 0.9), c, 120, fS, fS + 4, 18, (1, 1, 1), size=0.02, vel_rand=2.0, vel_obj=(0, -0.6, 1.8), gravity=0.6, strength=3.0, radius=0.3)
print("props_song2: crab", fC, "splash", fS)
