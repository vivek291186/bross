OUT = "/mnt/user-data/outputs/song08"; LINES = OUT + "/lines.json"; MIX = OUT + "/audio_full.wav"; VOX = OUT + "/vox16.wav"
SET = "zoo"; TITLE = "LET'S GO TO THE ZOO!"; SUB = "Bro Bros"; NEXT = "New song tomorrow at 10 AM!"
CAST = {"himank": [-1.7, -1.1, 12, "Happy Sway Standing"], "aarav": [-0.85, -1.35, 6, "Happy Sway Standing"], "vanu": [0.0, -1.5, 0, "Happy Sway Standing"],
        "vihaan": [0.85, -1.35, -6, "Happy Sway Standing"], "buddy": [1.7, -1.1, -12, "Happy Sway Standing"]}
INTRO_CAM = "high_wide"; INTRO_CLIP = "Big Wave Hello"; OUTRO_CAM = "zoo_wide"
BLU, YEL, PINK, CYAN, GRN = [40, 150, 255], [255, 210, 30], [239, 61, 124], [40, 200, 236], [60, 200, 90]
ALL = ["vanu", "aarav", "vihaan", "himank", "buddy"]
SECT = {
 "Intro": {"whos": ["vanu"], "clip": "Big Wave Hello", "clips2": "Happy Sway Standing", "cams": ["close:lead"]},
 "Verse": {"whos": [["aarav"], ["aarav"], ["vihaan"], ["vihaan"]], "clip": ["Angry Ground Stomp", "Talk with Hands Open", "Jump with Arms Open", "Cheer with Both Hands Up"],
           "clips2": ["Happy Sway Standing", "Rhythmic Dance", "Happy Sway Standing", "Bubble Dance"],
           "cams": ["insert:elephant", "close:lead", "insert:giraffe", "close:lead"], "cue": ["ELEPHANT!", "SPRAY!", "GIRAFFE!", "SO TALL!"], "cuecol": YEL},
 "Chorus": {"whos": ALL, "clip": ["Happy Sway Standing", "Angry Ground Stomp", "Jumping Jacks", "Cheer with Both Hands Up"],
            "cams": ["zoo_wide", "low_wide", "zoo_wide", "high_wide"], "cue": ["ZOO ZOO ZOO!", "STOMP STOMP!", "WE CAN TOO!", "LET'S GO!"], "cuecol": PINK},
 "Verse2": {"whos": [["himank"], ["buddy"], ["vanu"], ["vanu", "aarav", "vihaan", "himank", "buddy"]], "clip": ["Hop with Arms Raised", "Shake It Off Dance", "Penguin Walk", "Penguin Walk"],
            "clips2": ["Rhythmic Dance", "Step Hip Hop Dance", "Penguin Walk", "Penguin Walk"],
            "cams": ["insert:monkeys", "close:lead", "insert:penguins", "zoo_wide"], "cue": ["OOH OOH AAH AAH!", "SWING!", "WADDLE!", "FLAP FLAP!"], "cuecol": BLU},
 "Bridge": {"whos": ALL, "clip": ["Angry Ground Stomp", "Regular Jump", "Penguin Walk"], "cams": ["low_wide", "zoo_wide", "high_wide"], "cue": ["ROAR!", "HOP HOP!", "STOP!"], "cuecol": GRN},
 "Outro": {"whos": ALL, "clip": ["Big Wave Hello", "Jump with Arms and Legs Open"], "cams": ["zoo_wide", "zoo_wide"], "cue": ["", "BYE BYE!"], "cuecol": YEL},
 "default": {"clip": "Happy Sway Standing"}}
EXTRA = []
