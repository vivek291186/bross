from engine import *
from actions import *

_photo = None
def family_photo():
    global _photo
    if _photo is None:
        src = Image.open("/mnt/user-data/uploads/Downloads/.bbf/ep2/full_3.jpg").convert("RGB")
        ph = src.crop((236, 146, 524, 522))
        def fn(d, s, im):
            d.rectangle([0, 0, 340 * s, 470 * s], fill=WHITE, outline=NAVY, width=6 * s)
            im.paste(ph.resize((300 * s, 392 * s)), (20 * s, 20 * s))
            d.text((170 * s, 442 * s), "THE BRO BROS", font=FD(30 * s), fill=NAVY, anchor="mm")
        card = aa(340, 470, fn)
        _photo = card.rotate(4, expand=True, resample=Image.BICUBIC)
    return _photo

def intro(ep, line1, line2, bg=((255, 190, 40), (255, 215, 90))):
    sc = ep.sc
    save = (sc.show_chars, sc.hud, sc.strip, sc.bg)
    sc.show_chars = False; sc.hud = None; sc.strip = None; sc.bg = bg
    ph = family_photo()
    def ov(im, u, ts):
        k = ease(min(1, ts / 0.6))
        im.alpha_composite(ph, (int(lerp(-420, 150, k)), 105))
        d = ImageDraw.Draw(im)
        k2 = ease(min(1, max(0, ts - 0.4) / 0.6))
        text_outline(d, (870, int(lerp(-100, 210, k2))), "BRO BROS", FD(110), YEL, ow=9, shadow=8)
        text_outline(d, (880, int(lerp(-100, 345, k2))), "FUN!", FD(150), PINK, ow=10, shadow=8)
        if ts > 1.4:
            text_outline(d, (880, 470), line1, FD(40), WHITE, ow=6, shadow=4)
            text_outline(d, (880, 525), line2, FD(30), YEL, ow=5, shadow=3)
    ep.action(4.6, ov, sounds=[(0.0, "whoosh", 1.0), (0.5, "tada", 0.9)])
    a = tts("ann", "Welcome to Bro Bros Fun! Two brothers. Double fun. Unlimited madness!")
    ep.voice.append((ep.t - 2.8, a)); ep.speech_spans.append((ep.t - 2.8, ep.t - 2.8 + len(a) / SR))
    ep.action(max(0.5, len(a) / SR - 2.6), ov)
    sc.show_chars, sc.hud, sc.strip, sc.bg = save

def set_hud_battle(ep, total_rounds=10, icon=icon_pumpkin):
    sc = ep.sc
    ep.score = {"big": 0, "lil": 0}; ep.round = 0; ep.total_rounds = total_rounds
    def hud(im):
        lab = f"ROUND {ep.round}/{total_rounds}" if ep.round else "GET READY"
        im.alpha_composite(scoreboard(ep.score["big"], ep.score["lil"], lab), (410, 8))
    def stripf(im):
        s_ = strip(total_rounds, max(0, ep.round - 1), icon, current=ep.round - 1 if ep.round else None)
        im.alpha_composite(s_, ((W - s_.width) // 2, 630))
    sc.hud = hud; sc.strip = stripf

def round_start(ep, name, sub, bg, mood_sfx="whoosh"):
    ep.round += 1
    ep.sc.bg = bg; ep.sc.winner = None
    ep.sc.poses = {"big": "idle", "lil": "idle"}
    ep.title_card(f"ROUND {ep.round}", name, dur=2.4, sound=mood_sfx)
    ep.say("ann", sub)

def award(ep, who, pts=1, line=None):
    ep.score[who] += pts
    ep.sc.winner = who
    ep.sc.poses[who] = "cheer"
    other = "lil" if who == "big" else "big"
    ep.sc.poses[other] = "shrug"
    ep.action(1.6, score_pop(who, pts), sounds=[(0, "ding", 1.0), (0.2, "cheer", 0.6)])
    if line:
        ep.say("ann", line)

def clear_winner(ep):
    ep.sc.winner = None
    ep.sc.poses = {"big": "idle", "lil": "idle"}
