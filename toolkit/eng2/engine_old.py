
# ---------------- multi-scene engine ----------------
SCN = TL["scenes"]; EV = TL["events"]
def tf(t): return F(t)

# world + sun (keyed per scene)
w = bpy.data.worlds.new("sky"); sc.world = w; w.use_nodes = True
BG = w.node_tree.nodes["Background"]
bpy.ops.object.light_add(type="SUN", location=(0, 0, 30), rotation=(math.radians(50), math.radians(-12), math.radians(30)))
SUN = bpy.context.object; SUN.data.angle = math.radians(3)
SKY = {"day": ((150, 200, 245), 1.0, 3.2), "morning": ((255, 214, 170), 0.9, 2.6), "evening": ((255, 160, 110), 0.6, 1.0),
       "night": ((20, 24, 60), 0.35, 0.0)}

def key_hold(idb, f):
    """freeze every animated channel of a datablock at frame f (so the next key does not blend into earlier frames)"""
    ad = getattr(idb, "animation_data", None)
    if not ad or not ad.action: return
    for fc in ad.action.fcurves:
        fc.keyframe_points.insert(f, fc.evaluate(f), options={"FAST"})

def kprop(owner, path, f, val):
    setattr(owner, path, val); owner.keyframe_insert(path, frame=f)

def set_light_state(setname, state, f):
    S = SETS[setname]; L = S["lights"]
    col, strength, sun = SKY[state]
    for idb in (w.node_tree, SUN.data): key_hold(idb, f - 1)
    BG.inputs["Color"].default_value = (*C(col), 1); BG.inputs["Color"].keyframe_insert("default_value", frame=f)
    BG.inputs["Strength"].default_value = strength; BG.inputs["Strength"].keyframe_insert("default_value", frame=f)
    kprop(SUN.data, "energy", f, sun)
    SUN.data.color = (1, 0.85, 0.7) if state in ("morning", "evening") else (1, 0.97, 0.92); SUN.data.keyframe_insert("color", frame=f)
    E = {"night": dict(lamp=45, win=0, fill=25, main=40), "morning": dict(lamp=0, win=900, fill=320, main=350),
         "evening": dict(lamp=160, win=200, fill=200, main=250), "day": dict(lamp=0, win=600, fill=380, main=420)}[state]
    for nm, lo in L.items():
        key_hold(lo.data, f - 1); kprop(lo.data, "energy", f, E.get(nm, 300))
    if "glass" in S:
        gm = S["glass"].active_material; nd = gm.node_tree.nodes["Principled BSDF"]
        key_hold(gm.node_tree, f - 1)
        gc = {"night": (25, 35, 90), "morning": (255, 225, 170), "evening": (255, 150, 90), "day": (190, 225, 255)}[state]
        nd.inputs["Base Color"].default_value = (*C(gc), 1); nd.inputs["Base Color"].keyframe_insert("default_value", frame=f)
        nd.inputs[EMI].default_value = (*C(gc), 1); nd.inputs[EMI].keyframe_insert("default_value", frame=f)
        for o, show in ((S["moon"], state == "night"), (S["sun"], state == "morning")):
            key_hold(o, f - 1); s = 1.0 if show else 0.0
            o.scale = (0.35 * s, 0.05 * s, 0.35 * s) if o is S["moon"] else (0.45 * s, 0.05 * s, 0.45 * s); o.keyframe_insert("scale", frame=f)

# ---------- character state ----------
def dims(k):
    J = R[k]["J"]; return J[("hip", 1)].z, J[("knee", 1)].z, R[k]["hz"], R[k]["top"]
STATE = {k: {"set": None, "pos": (0, 0), "pose": "away", "yaw": 0} for k in KIDS}
SEAT_H = {}

def seat_for(k, setname, x, y):
    hipz, kneez, hz, top = dims(k)
    style = SETS[setname].get("seat_style", "stool")
    if style == "bus": return 1.07
    h = kneez + 0.02
    wd = mat((240, 120, 80), name="stool") if style != "class" else mat((80, 150, 220), name="classchair")
    box(O(setname, x, y + 0.05, h - 0.05), (0.42, 0.36, 0.05), wd, bevel=0.03)
    for sx in (-1, 1):
        for sy in (-1, 1): cyl(O(setname, x + sx * 0.34, y + 0.05 + sy * 0.28, (h - 0.1) / 2), 0.035, h - 0.1, mat((70, 70, 80)))
    box(O(setname, x, y + 0.42, h + 0.55), (0.42, 0.04, 0.5), wd, bevel=0.03)
    if style == "class":
        dt = h + 0.62
        box(O(setname, x, y - 0.95, dt), (0.7, 0.38, 0.04), mat((210, 170, 120), name="desk"), bevel=0.02)
        for sx in (-1, 1): box(O(setname, x + sx * 0.62, y - 0.95, dt / 2), (0.04, 0.32, dt / 2), mat((90, 90, 100)))
        bk = box(O(setname, x, y - 0.9, dt + 0.05), (0.22, 0.16, 0.012), mat((250, 250, 245), name="book"))
        box(O(setname, x, y - 0.9, dt + 0.035), (0.23, 0.17, 0.012), mat([(230, 80, 80), (80, 140, 230), (90, 190, 110)][len(SEAT_H) % 3], name="bookcover"))
    return h

def place(k, setname, x, y, pose, f, yaw=0.0):
    rig = R[k]; root = rig["root"]
    for idb in (root,): key_hold(idb, f - 1)
    hipz, kneez, hz, top = dims(k)
    if pose == "away":
        kloc(root, f, (0, 0, -80)); krot(root, f, (0, 0, 0)); STATE[k].update(set=None, pose="away"); return
    P = O(setname, x, y)
    if pose == "stand":
        kloc(root, f, (P.x, P.y, 0)); krot(root, f, (0, 0, math.radians(yaw))); stand(k, f)
    elif pose == "sit":
        key = (k, setname, x, y)
        if key not in SEAT_H: SEAT_H[key] = seat_for(k, setname, x, y)
        h = SEAT_H[key]
        kloc(root, f, (P.x, P.y, h + 0.1 - hipz)); krot(root, f, (0, 0, math.radians(yaw)))
        set_legs(k, f, -1.5, 1.5, -1.5, 1.5); kloc(rig["body"], f, (0, 0, 0)); krot(rig["body"], f, (0, 0, 0))
    elif pose == "sleep":
        L_ = top
        kloc(root, f, (P.x, P.y - L_ * 0.55, 1.12)); krot(root, f, (math.radians(-90), 0, 0)); stand(k, f)
    set_arms(k, f, "idle"); krot(rig["head"], f, (0, 0, 0))
    STATE[k].update(set=setname, pos=(x, y), pose=pose, yaw=yaw)

def head_pos(k, setname, x, y, pose):
    hipz, kneez, hz, top = dims(k)
    if pose == "sit":
        key = (k, setname, x, y); h = SEAT_H.get(key, kneez)
        return O(setname, x, y, hz + h + 0.1 - hipz)
    if pose == "sleep": return O(setname, x, y + top * 0.35, 1.4)
    return O(setname, x, y, hz)

# ---------- positions over time (for cameras) ----------
MOVES = {k: [] for k in KIDS}
for e in EV:
    if e["type"] == "move":
        for k in ([e["who"]] if isinstance(e["who"], str) else e["who"]): MOVES[k].append(e)
def scene_at(t):
    for s in SCN:
        if s["t0"] <= t < s["t1"]: return s
    return SCN[-1]
def pos_at(k, t):
    s = scene_at(t); c = s["cast"].get(k)
    if not c: return None
    x, y = c[0], c[1]; pose = c[3]
    for m in MOVES[k]:
        if s["t0"] <= m["t"] <= t:
            if t >= m["t"] + m["dur"]: x, y = m["to"]; pose = "stand"
            else:
                a = (t - m["t"]) / m["dur"]; x, y = x + (m["to"][0] - x) * a, y + (m["to"][1] - y) * a; pose = "stand"
    for e in EV:   # explicit pose changes
        if e["type"] == "act" and s["t0"] <= e["t"] <= t and e.get("who") == k:
            if e["name"] == "lie_down": pose = "sleep"; x, y = (SETS[s["set"]]["anchors"][e["bed"]] - O(s["set"], 0, 0)).to_tuple()[:2]
            if e["name"] in ("aarav_jump", "vihaan_wakes"): pose = "stand"; x, y = WAKE_TO[k]
    return x, y, pose, s["set"]

WAKE_TO = {"aarav": (-0.9, 0.2), "vihaan": (1.4, 0.3)}

# ---------- props ----------
def prop_hide(o, f):
    key_hold(o, f - 1); o.scale = (0, 0, 0); o.keyframe_insert("scale", frame=f)
def prop_show(o, f, s=(1, 1, 1)):
    key_hold(o, f - 1); o.scale = s; o.keyframe_insert("scale", frame=f)
def prop_move(o, f, loc, hop=0.0, dur=6):
    key_hold(o, f - 1)
    a = o.matrix_world.translation.copy() if not o.animation_data else Vector([fc.evaluate(f - 1) for fc in o.animation_data.action.fcurves if fc.data_path == "location"] or o.location)
    if hop:
        mid = (a + Vector(loc)) / 2 + Vector((0, 0, hop)); kloc(o, f + dur // 2, tuple(mid))
    kloc(o, f + dur, tuple(loc))
def shake(o, f0, f1, amp=0.25, hop=0.04):
    key_hold(o, f0 - 1); base = o.location.copy()
    for f in range(f0, f1, 2):
        k = (f - f0) // 2
        krot(o, f, (0, amp * (1 if k % 2 else -1), 0)); kloc(o, f, (base.x, base.y, base.z + (hop if k % 2 else 0)))
    krot(o, f1, (0, 0, 0)); kloc(o, f1, tuple(base))

def attach_bone(o, k, bone, local):
    o.parent = R[k]["root"]; o.parent_type = "BONE"; o.parent_bone = bone
    o.location = local; o.rotation_euler = (0, 0, 0)

# ---------- generic acting ----------
def look_at(k, f, target_xy, f_back):
    st = STATE[k]
    if st["pose"] in ("away", "sleep") or st["set"] is None: return
    x, y = st["pos"]; dx, dy = target_xy[0] - x, target_xy[1] - y
    yaw = max(-0.8, min(0.8, math.atan2(dx, -dy) if abs(dx) + abs(dy) > 0.3 else 0))
    h = R[k]["head"]; key_hold(R[k]["root"], f)
    krot(h, f, (0, 0, -yaw * 0.9)); krot(h, f_back, (0, 0, -yaw * 0.9)); krot(h, f_back + 6, (0, 0, 0))

def jump(k, f, height=0.35, n=1):
    b = R[k]["body"]
    for i in range(n):
        g = f + i * 10
        kloc(b, g, (0, 0, 0)); kloc(b, g + 5, (0, 0, height)); kloc(b, g + 10, (0, 0, 0))
        set_arms(k, g + 2, "cheer"); set_arms(k, g + 9, "cheer")

def wake_up(k, f, to_xy, setname):
    rig = R[k]; root = rig["root"]; key_hold(root, f - 1)
    P = O(setname, *to_xy)
    kloc(root, f + 6, (P.x, P.y, 1.2)); krot(root, f + 6, (math.radians(-20), 0, 0))
    kloc(root, f + 12, (P.x, P.y, 0)); krot(root, f + 12, (0, 0, 0)); stand(k, f + 12)
    jump(k, f + 12, 0.4); STATE[k].update(pos=to_xy, pose="stand")

# extra arm poses used in this episode
ARM_POSES.update({
    "brush": [(-0.3, 0.32, -1.05), (0.16, -0.95, 0.05)],
    "eat": [(-0.25, 0.25, -1.1), (0.16, -0.95, 0.05)],
    "think": [(-0.25, 0.2, -1.0), (0.3, -0.6, 0.3)],
    "read": [(0.05, -0.35, -1.0), (0.05, -0.35, -1.0)],
    "flap": [(0.85, -0.2, 0.0), (0.85, -0.2, 0.0)],
    "hold_up": [(0.25, 0.9, -0.4), (0.16, -0.95, 0.05)],
})

# ---------- run scenes ----------
for si, s in enumerate(SCN):
    f0 = tf(s["t0"]); f1 = tf(s["t1"]); sn = s["set"]
    set_light_state(sn, s["light"], f0)
    for k in KIDS:
        c = s["cast"].get(k)
        if c: place(k, sn, c[0], c[1], c[3], f0, c[2])
        else: place(k, sn, 0, 0, "away", f0)
    evs = [e for e in EV if s["t0"] <= e["t"] < s["t1"]]
    present = [k for k in KIDS if k in s["cast"]]
    for e in evs:
        a, b = tf(e["t"]), tf(e["t"] + e.get("dur", 0))
        if e["type"] == "say":
            whos = e.get("whos") or (present if e["who"] == "all" else [e["who"]] if e["who"] in KIDS else [])
            for k in whos:
                if STATE[k]["pose"] in ("stand", "sit"): talk_motion(k, a, b, e["gesture"] if STATE[k]["pose"] == "stand" or e["gesture"] not in ("spin",) else "talk")
                elif STATE[k]["pose"] == "sleep":
                    m = R[k]["mouth"]
                    for g in range(a, b, 3): kscale(m, g, (1.1, 1, 1.6 if (g - a) // 3 % 2 == 0 else 0.8))
                    kscale(m, b, (1, 1, 1))
            if len(whos) == 1:
                sp = STATE[whos[0]]["pos"]
                for k in present:
                    if k not in whos: look_at(k, a + 4, sp, b)
        elif e["type"] == "move":
            k = e["who"]; x0, y0 = STATE[k]["pos"]
            walk(k, a, b, tuple(O(sn, x0, y0))[:2], tuple(O(sn, *e["to"]))[:2], run=e["run"])
            STATE[k].update(pos=tuple(e["to"]), pose="stand")
        elif e["type"] == "prop":
            o = CLOCKS.get(e["name"])
            if e["action"] == "place" and o is not None:
                anc = SETS["bedroom"]["anchors"][e["to"]]
                prop_move(o, a, anc, hop=0.4, dur=8)
            elif e["action"] == "ring" and o is not None:
                if e.get("at") == "class":
                    key_hold(o, a - 2); kloc(o, a - 1, tuple(SETS["classroom"]["anchors"]["bag_class"]))
                shake(o, a, b)
            elif e["name"] == "toaster" and e["action"] == "pop":
                for t_ in SETS["kitchen"]["toast"]:
                    key_hold(t_, a - 1); z = t_.location.z
                    kloc(t_, a + 3, (t_.location.x, t_.location.y, z + 0.55)); kloc(t_, a + 9, (t_.location.x, t_.location.y, z + 0.25))
        elif e["type"] == "act":
            nm = e["name"]; who = e.get("who"); whos = who if isinstance(who, list) else ([who] if who else [])
            if nm == "tiptoe_place":
                k = whos[0]; b_ = R[k]["body"]
                krot(b_, a, (0, 0, 0)); krot(b_, a + 8, (math.radians(25), 0, 0)); set_arms(k, a + 8, "reach")
                krot(b_, b - 4, (math.radians(25), 0, 0)); krot(b_, b + 4, (0, 0, 0)); set_arms(k, b + 4, "idle")
            elif nm == "lie_down":
                k = whos[0]; rig = R[k]; root = rig["root"]; key_hold(root, a - 1)
                anc = SETS[sn]["anchors"][e["bed"]]; top = dims(k)[3]
                kloc(root, a + 10, (anc.x, anc.y - top * 0.3, 1.4)); krot(root, a + 10, (math.radians(-45), 0, 0))
                kloc(root, b, (anc.x, anc.y - top * 0.55, 1.12)); krot(root, b, (math.radians(-90), 0, 0))
                set_arms(k, b, "idle"); STATE[k].update(pose="sleep", pos=(anc.x - O(sn, 0, 0).x, anc.y - O(sn, 0, 0).y))
            elif nm == "lights_off":
                L = SETS[sn]["lights"]["lamp"]; key_hold(L.data, a); kprop(L.data, "energy", a + 6, 8)
                Lf = SETS[sn]["lights"]["fill"]; key_hold(Lf.data, a); kprop(Lf.data, "energy", a + 6, 10)
            elif nm in ("aarav_jump", "vihaan_wakes"):
                k = "aarav" if nm == "aarav_jump" else "vihaan"; wake_up(k, a, WAKE_TO[k], sn)
            elif nm == "search_ring" or nm == "everyone_search":
                for k in (whos or present):
                    h = R[k]["head"]
                    for j, g in enumerate(range(a, b, 9)): krot(h, g, (0, 0, 0.6 * (1 if j % 2 else -1)))
                    krot(h, b, (0, 0, 0))
                    if STATE[k]["pose"] == "stand": set_arms(k, a, "shrug"); set_arms(k, b, "idle")
            elif nm in ("brush_race", "brush_song"):
                for k in whos:
                    for j, g in enumerate(range(a, b, 3)): set_arms(k, g, "brush", wob=(0.06 * (1 if j % 2 else -1), 0.0))
                    set_arms(k, b + 4, "idle")
            elif nm == "paste_splat":
                prop_show(SETS["bathroom"]["splat"], a + 4, (0.22, 0.02, 0.16))
            elif nm == "toast_pop_jump":
                k = whos[0]; jump(k, a, 0.3); set_arms(k, a + 4, "ears")
            elif nm == "eat":
                for n_, k in enumerate(whos):
                    for j, g in enumerate(range(a + n_ * 3, b, 10)): set_arms(k, g, "eat" if j % 2 == 0 else "talk")
                    set_arms(k, b + 3, "idle")
            elif nm == "think":
                k = whos[0]; set_arms(k, a, "think"); set_arms(k, b, "think"); krot(R[k]["head"], a + 6, (0, 0.2, 0.15)); krot(R[k]["head"], b, (0, 0, 0))
            elif nm == "bus_drive":
                sc_ = SETS["bus"]["scenery"]; key_hold(sc_, a - 1); kloc(sc_, a, tuple(sc_.location))
                stop = [x for x in evs if x["type"] == "act" and x["name"] == "bus_stop"][0]
                fs = tf(stop["t"] + 0.8); kloc(sc_, fs, (sc_.location.x, sc_.location.y + (fs - a) * 0.45, sc_.location.z))
                for fc in sc_.animation_data.action.fcurves:
                    for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
                    if fc.data_path == "location": fc.keyframe_points[-1].interpolation = "SINE"
            elif nm == "bus_bump":
                for k in whos:
                    bb = R[k]["body"]
                    for g in (a, a + 20):
                        kloc(bb, g, (0, 0, 0)); kloc(bb, g + 4, (0, 0, 0.25)); kloc(bb, g + 9, (0, 0, 0))
                    set_arms(k, a + 2, "shrug"); set_arms(k, b, "idle")
            elif nm == "school_bell":
                shake(SETS["street"]["bell"], a, b, amp=0.35, hop=0.0)
            elif nm in ("class_quiet", "reading"):
                for k in (whos or present):
                    set_arms(k, a, "read"); krot(R[k]["head"], a + 8, (math.radians(14), 0, 0)); set_arms(k, b, "read")
            elif nm == "class_ring":
                for k in present:
                    krot(R[k]["head"], a + 2, (0, 0, 0)); jump(k, a, 0.12); set_arms(k, a + 6, "ears"); set_arms(k, b, "ears")
            elif nm == "bag_reveal":
                o = CLOCKS["clock5"]; key_hold(o, a); kloc(o, a + 10, tuple(SETS["classroom"]["anchors"]["bag_class"] + Vector((0, 0, 0.9))))
                set_arms("aarav", a, "shrug"); set_arms("aarav", b, "point_right")
            elif nm in ("class_laugh", "jump_cheer", "dance", "rooster", "huddle", "walk_to_gate", "run_inside", "end_card"):
                ks = whos or present
                if nm == "class_laugh":
                    for k in ks: talk_motion(k, a, b, "laugh")
                elif nm == "jump_cheer":
                    for i, k in enumerate(ks): jump(k, a + i * 2, 0.4)
                elif nm == "dance":
                    for i, k in enumerate(ks):
                        for j, g in enumerate(range(a, b, 12)):
                            set_arms(k, g, ["cheer", "spin", "wave", "hips"][(j + i) % 4]); kloc(R[k]["body"], g, (0, 0, 0.18 if j % 2 else 0))
                            krot(R[k]["body"], g, (0, 0, math.radians(10 if j % 2 else -10)))
                        krot(R[k]["body"], b, (0, 0, 0)); kloc(R[k]["body"], b, (0, 0, 0))
                elif nm == "rooster":
                    k = ks[0]
                    for j, g in enumerate(range(a, b, 5)):
                        set_arms(k, g, "flap" if j % 2 else "idle"); krot(R[k]["head"], g, (math.radians(-15 if j % 2 else 10), 0, 0))
                    krot(R[k]["head"], b, (0, 0, 0))
                elif nm == "huddle":
                    for k in ks:
                        krot(R[k]["body"], a + 6, (math.radians(25), 0, 0)); krot(R[k]["body"], b - 4, (math.radians(25), 0, 0)); krot(R[k]["body"], b + 2, (0, 0, 0))
                elif nm == "end_card":
                    for k in ks:
                        for j, g in enumerate(range(a, b, 8)): set_arms(k, g, "wave" if j % 2 == 0 else "cheer")
    # props visible only in their scenes
    if sn == "bathroom":
        for k, br in BRUSHES.items(): prop_show(br, f0)
        prop_show(SETS["bathroom"]["water"], f0); prop_hide(SETS["bathroom"]["water"], f0 + 60)
    else:
        for k, br in BRUSHES.items(): prop_hide(br, f0)
    # hold everything at the end of the scene so the next scene's first keys don't blend backwards
    for k in KIDS:
        key_hold(R[k]["root"], f1 - 1)
        for pb in R[k]["root"].pose.bones: pass
    key_hold(R[KIDS[0]]["root"], f1 - 1)

# toothbrushes in the right hands
for k, br in BRUSHES.items():
    attach_bone(br, k, "hand.R", (0.0, 0.0, 0.05))
    br.rotation_euler = (math.radians(80), 0, 0)
# clocks start on the tray in the bedroom
tray = SETS["bedroom"]["anchors"]["clock_tray"]
for i, (nm, o) in enumerate(sorted(CLOCKS.items())):
    o.location = tray + Vector((-0.55 + i * 0.28, 0, 0.42)); o.keyframe_insert("location", frame=1)
# re-sort: prop keys inserted later than frame-1 keys are fine; make sure frame-1 key exists before other keys
for o in CLOCKS.values():
    for fc in o.animation_data.action.fcurves: fc.update()
for t_ in SETS["kitchen"]["toast"]:
    pass
splat = SETS["bathroom"]["splat"]
if not splat.animation_data: prop_hide(splat, 2)
else:
    splat.scale = (0, 0, 0); splat.keyframe_insert("scale", frame=1)
