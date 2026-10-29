# ===== Episode 4 (Diwali) props: executed inside build4 (has CH, SETS, TL, F, sets2, head_bone, Vector, Matrix, random, math, bpy) =====
import vfx, sets_diwali
def key_vis(obj, f, v):
    for o in [obj] + list(obj.children_recursive):
        o.hide_render = not v; o.hide_viewport = not v
        o.keyframe_insert("hide_render", frame=f); o.keyframe_insert("hide_viewport", frame=f)
def bone_of(k, name): return [b for b in CH[k]["arm"].pose.bones if b.name.endswith(":" + name)][0]
def attach(obj, k, bone, f, offset=(0, 0.06, 0.02), rot=(0, 0, 0)):
    obj.keyframe_insert("location", frame=f - 1); obj.keyframe_insert("rotation_euler", frame=f - 1)
    c = obj.constraints.new("CHILD_OF"); c.target = CH[k]["arm"]; c.subtarget = bone_of(k, bone).name
    c.use_scale_x = c.use_scale_y = c.use_scale_z = False; c.inverse_matrix = Matrix.Identity(4)
    c.influence = 0; c.keyframe_insert("influence", frame=f - 1); c.influence = 1; c.keyframe_insert("influence", frame=f)
    obj.location = offset; obj.rotation_euler = rot
    obj.keyframe_insert("location", frame=f); obj.keyframe_insert("rotation_euler", frame=f)
    for fc in obj.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = "CONSTANT"
    return c
def detach_to(obj, f, loc):
    """drop the object at a world location (constraint off) at frame f"""
    for c in obj.constraints:
        if c.type == "CHILD_OF":
            c.influence = 1; c.keyframe_insert("influence", frame=f - 1); c.influence = 0; c.keyframe_insert("influence", frame=f)
    obj.location = loc; obj.rotation_euler = (0, 0, 0)
    obj.keyframe_insert("location", frame=f); obj.keyframe_insert("rotation_euler", frame=f)
    for fc in obj.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = "CONSTANT"

coll_p = sets2.col("props")
liv = SETS.get("living_diwali"); bal = SETS.get("balcony"); night = SETS.get("balcony_night"); kitchen = SETS.get("kitchen")
puff_m = sets2.M("colourpuff", (0.95, 0.35, 0.6), 1.0, alpha=0.35)
def puff(loc, f, n=7, size=0.07, rise=0.6, spread=0.08, life=36, coll=coll_p, mat=None):
    rnd = random.Random(f)
    for i in range(n):
        s_ = sets2.sph(f"puff_{f}_{i}", size, loc, mat or puff_m, coll, seg=12)
        t0 = f + i * 2
        s_.scale = (0.01, 0.01, 0.01); s_.keyframe_insert("scale", frame=max(1, t0 - 1)); s_.keyframe_insert("location", frame=max(1, t0 - 1))
        s_.location = Vector(loc) + Vector((rnd.uniform(-spread, spread), rnd.uniform(-spread, spread), 0.05))
        s_.scale = (1, 1, 1); s_.keyframe_insert("scale", frame=t0 + 4); s_.keyframe_insert("location", frame=t0 + 4)
        s_.location = Vector(loc) + Vector((rnd.uniform(-spread, spread) * 3, rnd.uniform(-spread, spread) * 3, rise))
        s_.scale = (2.2, 2.2, 2.2); s_.keyframe_insert("location", frame=t0 + life * 0.7); s_.keyframe_insert("scale", frame=t0 + life * 0.7)
        s_.scale = (0.01, 0.01, 0.01); s_.keyframe_insert("scale", frame=t0 + life)

# --- kitchen: hide the Ep2 tiffins; laddoo tray appears on cue
if kitchen:
    for ob in kitchen["tiffins"].values(): key_vis(ob, 1, False)
# --- sunset balcony: rangoli (hidden layers) + 4 relay diyas on a tray
rg_layers = []; relay_diyas = {}
if bal:
    O = bal["origin"]; cb = bal["coll"]
    rg_layers = sets_diwali.rangoli("rg", (O.x, O.y + 0.2, 0.0), cb, R=0.6)
    for g in rg_layers:
        for ob in g:
            if isinstance(ob, dict):
                for o_ in ob.values(): key_vis(o_, 1, False)
            else: key_vis(ob, 1, False)
    tray = sets2.cyl("rg_tray", 0.3, 0.015, (O.x, O.y + 1.05, 0.9), sets2.M("brass", (0.85, 0.65, 0.25), 0.3, coat=0.8), cb, 40)
    sets2.box("rg_stand", (0.35, 0.35, 0.88), (O.x, O.y + 1.05, 0.44), sets2.M_wood("rg_standw"), cb, 0.01)
    for i, k in enumerate(("aarav", "himank", "vihaan", "buddy")):
        d = sets_diwali.diya(f"rd_{k}", (O.x - 0.18 + i * 0.12, O.y + 1.05, 0.91), cb, lit=True, r=0.035, light_energy=3.0)
        grp = bpy.data.objects.new(f"rdg_{k}", None); cb.objects.link(grp); grp.location = (O.x - 0.18 + i * 0.12, O.y + 1.05, 0.91)
        for o_ in d.values():
            mw = o_.matrix_world.copy(); o_.parent = grp; o_.matrix_parent_inverse = grp.matrix_world.inverted()
        relay_diyas[k] = (grp, d)
    bal["cams"]["insert:rangoli"] = ((O.x - 0.9, O.y - 1.1, 1.3), (O.x, O.y + 0.2, 0.05), 32)
    bal["cams"]["insert:diyas"] = ((O.x - 0.5, O.y + 0.3, 1.1), (O.x, O.y + 1.05, 0.92), 50)
    # the finished rangoli also sits on the night balcony (lit)
if night:
    On = night["origin"]
    for g in sets_diwali.rangoli("rgn", (On.x, On.y + 0.2, 0.0), night["coll"], R=0.6):
        for ob in g:
            if isinstance(ob, dict):
                ob["flame"].hide_render = False; ob["flame"].hide_viewport = False; ob["light"].hide_render = False; ob["light"].hide_viewport = False
if kitchen:
    TX, TY, TZ = kitchen["table"]
    kitchen["cams"]["insert:laddoos"] = ((TX - 0.6, TY - 0.9, TZ + 0.45), (TX, TY + 0.1, TZ + 0.05), 40)

placed = {}
for e in TL["events"]:
    if e["type"] != "prop": continue
    f = F(e["t"]); nm = e["name"]; a = e["action"]; who = e.get("who")
    if nm == "tangle" and liv:
        grp = bpy.data.objects.get("tangle_grp")
        if grp is None:
            grp = bpy.data.objects.new("tangle_grp", None); liv["coll"].objects.link(grp)
            cx = sum(o.location.x for o in liv["tangle"]) / len(liv["tangle"]); cy = sum(o.location.y for o in liv["tangle"]) / len(liv["tangle"])
            grp.location = (cx, cy, 0.0)
            for o_ in liv["tangle"]:
                o_.parent = grp; o_.matrix_parent_inverse = grp.matrix_world.inverted()
        if a == "grab":
            attach(grp, "buddy", "Spine2", f + 26, offset=(0, 0.02, 0.1), rot=(0, 0, 0))
        elif a == "free":
            key_vis(grp, 1, True); key_vis(grp, f + 40, False)
    elif nm == "rangoli" and bal:
        if a == "reveal":
            g = rg_layers[e["step"]]
            for ob in g:
                if isinstance(ob, dict):
                    key_vis(ob["bowl"], f + 30, True)
                else: key_vis(ob, f + 30, True)
        elif a == "light":
            for i, ob in enumerate(rg_layers[3]):
                key_vis(ob["flame"], f + 8 + i * 4, True); key_vis(ob["light"], f + 8 + i * 4, True)
        elif a == "puff":
            O = bal["origin"]; puff((O.x, O.y + 0.2, 0.05), f + 6, n=10, size=0.06, rise=0.5, spread=0.25, life=30, coll=bal["coll"])
    elif nm == "diya" and bal and who in relay_diyas:
        grp, d = relay_diyas[who]
        if a == "carry":
            attach(grp, who, "RightHand", f + 20, offset=(0, 0.07, 0.0), rot=(0, 0, 0))
        elif a == "place":
            O = bal["origin"]; x = e.get("x")
            # drop at the kid's current position in front of them
            sc.frame_set(f); hw = CH[who]["arm"].matrix_world.translation.copy()
            loc = (hw.x, hw.y - 0.35, 0.0); placed[who] = loc
            detach_to(grp, f, loc)
        elif a == "blowout":
            key_vis(d["flame"], f, False); key_vis(d["light"], f, False)
            sc.frame_set(f); hw = CH[who]["arm"].matrix_world.translation.copy()
            puff((hw.x, hw.y - 0.3, 0.9), f, n=5, size=0.03, rise=0.3, spread=0.04, life=24, coll=bal["coll"], mat=sets2.M("steam", (1, 1, 1), 1.0, alpha=0.14))
        elif a == "relight":
            key_vis(d["flame"], f + 10, True); key_vis(d["light"], f + 10, True)
    elif nm == "laddoo" and a == "show" and kitchen:
        TX, TY, TZ = kitchen["table"]
        grp = bpy.data.objects.new("laddooset", None); coll_p.objects.link(grp)
        plate_m = sets2.M("plate", (0.95, 0.95, 0.93), 0.25, coat=0.5); bowl_m = sets2.M("steelbowl", (0.66, 0.68, 0.72), 0.2, coat=0.7)
        for o_ in [sets2.cyl("ld_bigplate", 0.3, 0.015, (TX, TY + 0.12, TZ + 0.01), plate_m, coll_p, 40)] + \
                  [sets2.laddoo(f"ld_l{i}", (TX - 0.18 + (i % 5) * 0.09, TY + 0.03 + (i // 5) * 0.09, TZ + 0.035), coll_p) for i in range(10)] + \
                  [sets2.cyl("ld_bowl", 0.14, 0.09, (TX - 0.75, TY + 0.15, TZ + 0.045), bowl_m, coll_p, 32), sets2.cyl("ld_bowl2", 0.14, 0.09, (TX + 0.75, TY + 0.15, TZ + 0.045), bowl_m, coll_p, 32)]:
            o_.parent = grp
        key_vis(grp, 1, False); key_vis(grp, f, True)
    elif nm == "diyas" and a == "light" and night:
        for i, d in enumerate(night["diyas"]):
            key_vis(d["flame"], f + 6 + i * 3, True); key_vis(d["light"], f + 6 + i * 3, True)
    elif nm == "sparkler" and night:
        if a == "on":
            f1 = f + int(e["dur"] * 24)
            for k in e["whos"]:
                vfx.sparkler("spk_" + k, CH[k]["arm"], bone_of(k, "RightHand").name, night["coll"], f + 8, f1)
        # 'off' is implicit (emitter end); hide sticks
        if a == "off":
            for k in e["whos"]:
                st = bpy.data.objects.get("bn_spk_" + k)
                if st: key_vis(st, f + 12, False)
    elif nm == "anar" and a == "fire" and night:
        vfx.anar("anar_fx", night["anar_tip"], night["coll"], f + 6, e.get("dur", 3.5))
    elif nm == "chakri" and a == "spin" and night:
        vfx.chakri("chakri_fx", night["chakri"], night["coll"], f + 6, e.get("dur", 3.0))
    elif nm == "rocket" and a == "launch" and night:
        O = night["origin"]; i = e["idx"]
        colr = {"red": (1.0, 0.25, 0.3), "green": (0.3, 1.0, 0.4), "gold": (1.0, 0.8, 0.3)}[e.get("colour", "gold")]
        launch = (O.x + 2.6, O.y + 1.4, 0.1); burst = (O.x + 1.5 + (i % 3 - 1) * 4.0, O.y + 14.0 + (i % 2) * 4, 9.0 + (i % 3) * 1.5)
        vfx.rocket(f"rocket{i}", launch, burst, night["coll"], f + 6, 1.3, colr, big=1.0)
    elif nm == "city" and a == "fireworks" and night:
        O = night["origin"]; rnd = random.Random(f); dur_f = int(e.get("dur", 6) * 24)
        cols = [(1.0, 0.3, 0.3), (0.4, 1.0, 0.5), (1.0, 0.85, 0.3), (0.5, 0.6, 1.0), (1.0, 0.5, 0.9)]
        for j in range(max(3, dur_f // 20)):
            bp = (O.x + rnd.uniform(-45, 45), O.y + rnd.uniform(45, 75), rnd.uniform(14, 30))
            lp = (bp[0], bp[1], -8.0)
            vfx.rocket(f"city{f}_{j}", lp, bp, night["coll"], f + j * 20 + rnd.randint(0, 8), 1.0, rnd.choice(cols), big=7.0)
