import sys
from common import *

ep = Episode("halloween", mood="spooky")
sc = ep.sc
B, L, H = "big", "lil", "ann"
S = ep.say

# Palettes
ORANGE = ((255, 135, 25), (255, 170, 60))
PURP = ((95, 50, 190), (125, 80, 215))
NIGHT = ((40, 30, 105), (60, 48, 135))
SLIME = ((70, 185, 70), (105, 210, 95))
TEAL = ((20, 160, 170), (50, 190, 195))
RED = ((215, 50, 70), (240, 85, 95))
MAG = ((200, 50, 170), (225, 90, 200))
LIME = ((150, 200, 30), (180, 225, 70))
SKY = ((50, 175, 230), (95, 205, 245))
GOLD = ((240, 180, 20), (255, 210, 70))

intro(ep, "Spooky Silly Costume Challenge!", "Halloween is only 10 days away!")

set_hud_battle(ep, 10, icon_pumpkin)
sc.bg = ORANGE
S(H, "It's a spooky, silly Halloween battle! Ten rounds. Ten points. One pumpkin crown!")
S(B, "Hello friends! I'm Big Bro, and today I am going to win. Easy!", pose="wave")
S(L, "And I'm Lil Bro! Big Bro says easy, but he said easy last time too.", pose="wave")
S(B, "Last time doesn't count. Last time I had a sneeze in my brain.", pose="shrug")
S(L, "A sneeze in your brain? Is that why you're always confused?", pose="point_l")
S(B, "Hey! Okay, Show Host, tell us the rules before Lil Bro gets cheeky.", pose="idle", other_pose="idle")
S(H, "The rules are simple. Every round has a spooky challenge. Win the round, get a point.")
S(H, "The final round is worth double points. And the loser gets a funny punishment!")
S(L, "Punishment? Like no ice cream for a week?", pose="shrug")
S(H, "Even worse. The loser does the Chicken Monster Dance, wrapped up like a mummy!")
S(B, "Lil Bro, start practising your chicken dance. Bawk bawk!", pose="dance1")
S(L, "You practise. I'm saving my energy for winning.", pose="idle", other_pose="idle")
S(H, "Are you ready, Bro Bros? Are you ready, friends at home? Let's begin!")

# ---------------- Round 1: Mystery costume ----------------
round_start(ep, "Mystery Costume!", "Round one! Inside this box is a costume. Guess it from the clues!", PURP)
S(H, "Clue number one. This costume has a long, swishy cape.")
S(L, "A superhero! Super Lil Bro to the rescue!", pose="cheer")
S(H, "Clue number two. It sleeps all day, and it has pointy teeth.")
S(B, "Pointy teeth and sleeps all day? That sounds like Lil Bro on a Sunday.", pose="point_r")
S(L, "Hey! I only sleep till ten o'clock. Okay, eleven.", pose="shrug")
S(H, "Clue number three. It says, I vant to suck your... juice box!")
S(B, "I know! It's a vampire! A friendly vampire who loves juice boxes!", pose="cheer")
ep.action(3.4, gift_reveal(lambda im, d, k: (d.polygon([(560, 430 - 120 * k), (720, 430 - 120 * k), (680, 560 - 60 * k), (600, 560 - 60 * k)], fill=(150, 20, 40), outline=NAVY, width=4)), "VAMPIRE CAPE!"),
          sounds=[(0, "drumroll", 0.8), (1.7, "tada", 1.0)])
sc.cost[B] = ["cape", "fangs"]
award(ep, B, 1, "Correct! Big Bro wins round one and gets the vampire cape!")
S(B, "Look at me! I am Count Big Bro! Mwah ha ha!", pose="dance2")
S(L, "You look like a juice box with a blanket.", pose="point_l")
S(H, "Don't worry, Lil Bro. You get a costume too. A magic wizard hat!")
sc.cost[L] = ["wizard"]
ep.action(1.2, lambda im, u, ts: label(im, (965, 140), "WIZARD!", 44, YEL), sounds=[(0, "sparkle", 1.0)])
S(L, "Yes! With my wizard hat, I will magic all the points to me. Abracadabra!", pose="cheer")
clear_winner(ep)

# ---------------- Round 2: Pumpkin bowling ----------------
round_start(ep, "Pumpkin Bowling!", "Round two! Roll the pumpkin and knock down the pins. Most pins wins!", ORANGE)
S(B, "I'm a vampire. Vampires are amazing at bowling. Everyone knows that.", pose="point_r")
S(L, "Nobody knows that. You just made that up.", pose="shrug")
S(H, "Big Bro, you go first. Ten pins. Roll!")
ep.action(4.0, bowling(7), sounds=[(0, "slide", 0.7), (2.2, "boing", 0.6), (2.3, "pop", 0.8)], pre=lambda u, ts: sc.poses.update({B: "point_r" if u < 0.6 else "cheer"}))
S(B, "Seven pins! Seven! That's my lucky number!", pose="cheer")
S(L, "Your lucky number was three yesterday.", pose="idle")
S(H, "Lil Bro, your turn. You need eight pins to win.")
S(L, "Wizard power, activate! Pumpkin, go straight. Pumpkin, please go straight.", pose="think")
ep.action(4.0, bowling(10), sounds=[(0, "slide", 0.7), (2.2, "boing", 0.6), (2.3, "pop", 0.8), (2.4, "pop", 0.8), (2.6, "tada", 0.9)], pre=lambda u, ts: sc.poses.update({L: "point_l" if u < 0.6 else "cheer"}))
award(ep, L, 1, "A STRIKE! All ten pins! Lil Bro wins round two!")
S(L, "Did you see that? The pumpkin listened to me!", pose="dance1")
S(B, "The pumpkin was cheating. It had a wizard helping it.", pose="shrug")
S(L, "That's called talent, Big Bro.", pose="dance2")
clear_winner(ep)

# ---------------- Round 3: Mummy wrap race ----------------
round_start(ep, "Mummy Wrap Race!", "Round three! Wrap toilet paper around your brother. Fastest mummy maker wins!", TEAL)
S(L, "Wait. I wrap you, and you wrap me? At the same time?", pose="shrug")
S(H, "Exactly. Ready? Three, two, one... wrap!")
ep.action(4.0, countdown_321(), sounds=[(0, "tick", 1), (1, "tick", 1), (2, "tick", 1), (3, "ding", 1)])
def wrap_pre(u, ts):
    sc.poses[B] = "dance1" if int(ts * 4) % 2 else "dance2"
    sc.poses[L] = "dance2" if int(ts * 3) % 2 else "point_l"
    if u > 0.55: sc.cost[L] = ["wizard", "mummy"]
ep.action(7.0, race_bars(finals=(100, 64), title="MUMMY WRAP"), sounds=[(0, "whoosh", 0.6), (2, "whoosh", 0.6), (4, "whoosh", 0.6), (6.2, "ding", 1)], pre=wrap_pre)
award(ep, B, 1, "Big Bro wins! Lil Bro is now an official mummy!")
S(L, "Mmm mmm mm mmm! That means, help, I'm a mummy!", pose="shrug")
S(B, "Don't worry, little mummy. I will rescue you after I win the next round.", pose="point_r")
S(L, "I wrapped you too! Look, you have one piece of paper on your shoe.", pose="point_l")
S(B, "That's fashion.", pose="idle")
sc.cost[L] = ["wizard"]
clear_winner(ep)

# ---------------- Round 4: Monster dance-off ----------------
round_start(ep, "Monster Dance-Off!", "Round four! Show us your best monster dance. The Monster-o-meter will decide!", MAG)
S(B, "Watch this. It's called the Vampire Shuffle.", pose="dance1")
def dance_b(u, ts):
    sc.poses[B] = ["dance1", "cheer", "dance2", "shrug"][int(ts * 4) % 4]
ep.action(5.0, lambda im, u, ts: notes(im, ts), sounds=[(0, "boing", 0.4), (2.5, "boing", 0.4)], pre=dance_b)
sc.poses[B] = "idle"
S(H, "Interesting! Lots of flapping. Very vampire. Now, Lil Bro!")
S(L, "This is the Zombie Wizard Wiggle. Wiggle, wiggle, freeze!", pose="dance2")
def dance_l(u, ts):
    sc.poses[L] = ["dance2", "dance1", "cheer", "point_l", "dance1"][int(ts * 5) % 5]
ep.action(5.0, lambda im, u, ts: notes(im, ts, YEL), sounds=[(0, "boing", 0.4), (1.5, "boing", 0.4), (3, "boing", 0.4)], pre=dance_l)
sc.poses[L] = "idle"
S(H, "Monster-o-meter, who was the spookiest dancer?")
ep.action(5.0, meters("MONSTER-O-METER", (78, 94)), sounds=[(0, "drumroll", 0.8), (4.0, "ding", 1)])
award(ep, L, 1, "Ninety-four! Lil Bro wins the dance-off!")
S(B, "The meter is broken. It's scared of vampires.", pose="shrug")
S(L, "The meter loves wiggles. Everybody loves wiggles!", pose="dance1")
S(H, "The score is two to two! What a battle!")
clear_winner(ep)

# ---------------- Round 5: Spooky sound quiz ----------------
round_start(ep, "Spooky Sound Quiz!", "Round five! Listen carefully and guess the spooky sound!", NIGHT)
sc.stars = True
S(H, "Sound number one. Shhh. Listen.")
ep.action(2.6, lambda im, u, ts: label(im, (640, 400), "?", 120, YEL), sounds=[(0.2, "owl", 1.2)])
S(L, "That's Big Bro snoring!", pose="point_l")
S(B, "I don't snore! That's an owl. Hoo, hoo!", pose="think")
ep.action(3.0, quiz("Sound 1: What was it?", ["An owl", "A snoring brother", "A dog"], correct=0, picks={B: 0, L: 1}), sounds=[(1.9, "ding", 1)])
S(H, "Sound number two.")
ep.action(2.6, lambda im, u, ts: label(im, (640, 400), "?", 120, YEL), sounds=[(0.2, "door", 1.4)])
S(B, "A creaky old door in a haunted house!", pose="cheer")
S(L, "A creaky old door in a haunted house... that's what I was going to say.", pose="shrug")
ep.action(3.0, quiz("Sound 2: What was it?", ["A cat", "A creaky door", "A car"], correct=1, picks={B: 1, L: 1}), sounds=[(1.9, "ding", 1)])
S(H, "Last sound. Number three!")
ep.action(3.0, lambda im, u, ts: label(im, (640, 400), "?", 120, YEL), sounds=[(0.2, "thunder", 1.2)])
S(L, "Thunder! Big, loud, stormy thunder!", pose="cheer")
S(B, "That's my tummy. I skipped breakfast.", pose="shrug")
ep.action(3.0, quiz("Sound 3: What was it?", ["A hungry tummy", "Thunder", "A drum"], correct=1, picks={B: 0, L: 1}), sounds=[(1.9, "ding", 1)])
S(H, "Big Bro got two right. Lil Bro got two right too. It's a tie, so it's a bonus question!")
S(H, "Bonus question! Which animal says hoo hoo at night?")
S(B, "An owl!", pose="cheer")
S(L, "A wizard's owl!", pose="cheer")
S(H, "Big Bro said it first! Point to Big Bro!")
award(ep, B, 1)
S(L, "My owl was more magical. That should be worth extra.", pose="shrug")
sc.stars = False
clear_winner(ep)

# ---------------- Fun facts break ----------------
sc.bg = SKY
ep.title_card("FUN FACTS", "Halloween Break!", color=(120, 230, 120), dur=2.4, sound="sparkle")
S(H, "Halfway there! Time for a quick Halloween fun facts break!")
S(B, "Fun fact number one. A pumpkin is actually a fruit, not a vegetable!", pose="point_r")
S(L, "A fruit? So pumpkin is like a giant orange apple?", pose="shrug")
S(B, "Kind of! It has seeds inside, just like apples and melons.", pose="think")
S(L, "Fun fact number two. Long ago in Ireland, people carved faces into turnips, not pumpkins!", pose="point_l")
S(B, "Turnip lanterns? That sounds tiny and a little bit stinky.", pose="shrug")
S(B, "Fun fact number three. The biggest pumpkin ever grown was about as heavy as a small car!", pose="cheer")
S(L, "Whoa! You would need a crane to make that into a lantern!", pose="cheer")
S(L, "Fun fact number four. Owls can turn their heads almost all the way around!", pose="point_l")
S(B, "Lil Bro tried that once. He just got dizzy and fell on the sofa.", pose="point_r")
S(L, "Fun fact number five. Bats are the only mammals that can really fly!", pose="dance1")
S(H, "Great facts, Bro Bros! Now, back to the battle!")
clear_winner(ep)

# ---------------- Round 6: Candy count ----------------
round_start(ep, "Candy Count!", "Round six! How many candies are in the jar? Closest guess wins!", RED)
S(B, "Hmm. One, two, lots, lots more. I say fifty candies!", pose="think")
S(L, "I say thirty five. Because thirty five is my favourite number this week.", pose="think")
ep.action(5.5, jars((20, 20), title="COUNTING..."), sounds=[(0, "pop", 0.4), (1, "pop", 0.4), (2, "pop", 0.4), (3, "pop", 0.4)])
S(H, "Let's count them all. Twenty in this side, and twenty in that side. Twenty plus twenty is...")
S(B, "Forty!", pose="cheer")
S(H, "Forty! Big Bro guessed fifty. That's ten away. Lil Bro guessed thirty five. That's five away!")
award(ep, L, 1, "Lil Bro is closer! Lil Bro wins round six!")
S(B, "Wait a minute. Lil Bro, why is your mouth full?", pose="point_r")
S(L, "Mmm? No reason. Candy guessing makes me hungry.", pose="shrug")
S(B, "He ate the candies! That's why the number is smaller!", pose="point_r")
S(H, "Ha ha! Remember friends, ask a grown up before eating candy. Score is three to three!")
clear_winner(ep)

# ---------------- Round 7: Ring toss ----------------
round_start(ep, "Witch Hat Ring Toss!", "Round seven! Throw five rings onto the witch's hat!", LIME)
S(L, "I'm a wizard. Hats are my thing. This round is mine.", pose="point_l")
S(H, "Big Bro, you're first. Five rings. Go!")
ep.action(7.0, ring_toss((1, 1, 0, 1, 1)), sounds=[(0.8, "pop", 0.8), (2.2, "pop", 0.8), (3.6, "buzz", 0.5), (5.0, "pop", 0.8), (6.4, "pop", 0.8)], pre=lambda u, ts: sc.poses.update({B: "point_r" if int(ts * 2) % 2 else "idle"}))
S(B, "Four out of five! Vampires have super throwing arms!", pose="cheer")
S(H, "Lil Bro, you need five to win!")
S(L, "Easy. Wizard eyes. Focus. Focus.", pose="think")
ep.action(7.0, ring_toss((1, 0, 1, 0, 0)), sounds=[(0.8, "pop", 0.8), (2.2, "buzz", 0.5), (3.6, "pop", 0.8), (5.0, "buzz", 0.5), (6.4, "buzz", 0.5)], pre=lambda u, ts: sc.poses.update({L: "point_l" if int(ts * 2) % 2 else "idle"}))
S(L, "Two. My wizard eyes need glasses.", pose="shrug")
award(ep, B, 1, "Big Bro wins the ring toss! Big Bro leads four to three!")
S(B, "Lil Bro, would you like some throwing lessons? Only fifty candies.", pose="point_r")
S(L, "You owe me candies for calling me a candy thief.", pose="point_l")
clear_winner(ep)

# ---------------- Round 8: Ghost hide and seek ----------------
round_start(ep, "Ghost Hide and Seek!", "Round eight! A friendly ghost is hiding. Find it in one try!", PURP)
S(H, "The ghost could be behind the sofa, the curtain or inside the box. Lil Bro, you pick first.")
S(L, "Ghosts love curtains. Swishy, swishy. I pick the curtain!", pose="point_l")
ep.action(3.2, doors(3, ghost_at=1, open_seq=(1,)), sounds=[(1.0, "knock", 0.8), (1.3, "ghost", 1.0)])
S(H, "Boo! You found him! The ghost was behind the curtain!")
award(ep, L, 1)
S(B, "No fair! I didn't even get a turn!", pose="shrug")
S(L, "The ghost likes me more. We are both cute and mysterious.", pose="cheer")
S(H, "The ghost says, thanks for playing, and happy Halloween! Score is four to four!")
clear_winner(ep)

# ---------------- Round 9: Silly monster face ----------------
round_start(ep, "Silly Monster Face!", "Round nine! Make the silliest monster face. Horns and googly eyes allowed!", SLIME)
sc.cost[L] = ["wizard", "googly"]
ep.action(1.2, lambda im, u, ts: None, sounds=[(0, "boing", 0.8)])
S(L, "Look at my googly eyes! I can see you and the ceiling at the same time!", pose="dance1")
sc.cost[B] = ["cape", "fangs", "horns", "googly"]
ep.action(1.2, lambda im, u, ts: None, sounds=[(0, "boing", 0.8), (0.3, "boing", 0.8)])
S(B, "Horns, fangs and googly eyes! I'm a vampire, a dragon and a frog. At the same time!", pose="dance2")
S(L, "That's too many monsters for one face!", pose="shrug")
S(H, "Silly-o-meter, it's your turn!")
ep.action(5.0, meters("SILLY-O-METER", (97, 88)), sounds=[(0, "drumroll", 0.8), (4.0, "ding", 1)])
award(ep, B, 1, "Ninety-seven! The silliest face ever recorded! Big Bro leads five to four!")
S(B, "Ribbit. I mean, mwah ha ha. I mean, roar!", pose="cheer")
S(L, "He's so silly, even the meter is laughing.", pose="idle")
sc.cost[B] = ["cape", "fangs"]; sc.cost[L] = ["wizard"]
clear_winner(ep)

# ---------------- Round 10: Trick or treat door ----------------
round_start(ep, "Trick or Treat Door!", "The final round! It's worth DOUBLE points!", GOLD)
S(L, "Double points? So I can still win?", pose="cheer")
S(H, "Yes! There are two doors. One has a treat. One has a trick. Each of you picks one door.")
S(B, "I'm the leader, so I pick first. I choose the door on the left. Left is always right!", pose="point_r")
S(L, "Left is always right? That doesn't even make sense. I'll take the right door then.", pose="point_l")
S(H, "Knock knock! Big Bro, open your door!")
ep.action(3.2, doors(2, ghost_at=0, open_seq=(0,), labels=("LEFT", "RIGHT")), sounds=[(0.2, "knock", 0.8), (1.0, "ghost", 1.0)])
S(H, "It's a trick! A ghost says, boo, and tickles your toes!")
S(B, "Ha ha ha! Stop! Not the toes! Not the toes!", pose="shrug")
S(H, "Lil Bro, open your door!")
def treat(im, u, ts):
    d = ImageDraw.Draw(im)
    panel(im, (480, 300, 800, 560), fill=(255, 245, 215))
    for k in range(12):
        draw_candy(d, 530 + (k % 6) * 46, 380 + (k // 6) * 70, [PINK, YEL, CYAN, (120, 230, 120)][k % 4], r=13)
    label(im, (640, 520), "TREAT!", 46, YEL)
ep.action(3.4, treat, sounds=[(0, "knock", 0.8), (0.9, "tada", 1.0)])
award(ep, L, 2, "It's a treat! Lil Bro gets double points!")
S(H, "And that means... the final score is...")
ep.action(2.0, lambda im, u, ts: None, sounds=[(0, "drumroll", 1.0)])
sc.cost[L] = ["pumpkin_crown"]
S(H, "Big Bro five! Lil Bro six! Lil Bro wins the Spooky Silly Costume Challenge!")
ep.action(5.0, lambda im, u, ts: confetti(im, ts), sounds=[(0, "tada", 1.0), (0.3, "cheer", 0.8)], pre=lambda u, ts: sc.poses.update({L: ["cheer", "dance1", "dance2"][int(ts * 3) % 3], B: "shrug"}))
S(L, "I won! I won! I'm the Pumpkin King! Bow down to my pumpkin crown!", pose="cheer")
S(B, "I was winning the whole time. The door tricked me!", pose="shrug")
S(L, "That's why it's called trick or treat, Big Bro!", pose="point_l")

# ---------------- Punishment ----------------
sc.winner = None
sc.bg = ORANGE
S(H, "And now, the punishment! Big Bro, it's time for the Chicken Monster Dance, wrapped like a mummy!")
sc.cost[B] = ["cape", "fangs", "mummy"]
ep.action(1.5, lambda im, u, ts: None, sounds=[(0, "whoosh", 1.0)])
S(B, "Okay, okay. A real champion dances even when he loses. Music, please!", pose="shrug")
def chicken(u, ts):
    sc.poses[B] = ["dance1", "shrug", "dance2", "shrug"][int(ts * 5) % 4]
    sc.poses[L] = "cheer" if int(ts * 2) % 2 else "point_l"
ep.action(6.0, lambda im, u, ts: (notes(im, ts), label(im, (640, 300), "BAWK BAWK!", 50, YEL)), sounds=[(0, "boing", 0.5), (1.2, "boing", 0.5), (2.4, "boing", 0.5), (3.6, "boing", 0.5), (4.8, "boing", 0.5)], pre=chicken)
S(B, "Bawk bawk! I'm a mummy chicken! Bawk!", pose="dance2")
S(L, "That's the best dance I've ever seen! You should do this every day!", pose="cheer")
S(B, "Never again. Well... maybe at Diwali.", pose="shrug")
sc.cost[B] = ["cape", "fangs"]
clear_winner(ep)

# ---------------- Safety tips + outro ----------------
sc.bg = SKY
S(H, "Before you go, here are the Bro Bros Halloween safety tips!")
S(B, "Tip number one. Always go trick or treating with a grown up.", pose="point_r")
S(L, "Tip number two. Wear bright colours or carry a torch, so cars can see you.", pose="point_l")
S(B, "Tip number three. Show your candy to a grown up before you eat it.", pose="think")
S(L, "Tip number four. Be kind. Say thank you at every door!", pose="wave")
S(B, "And tip number five. Don't eat all the candy in one day. Right, Lil Bro?", pose="point_r")
S(L, "Who, me? I would never. Probably.", pose="shrug")
S(H, "Halloween is in ten days! What costume will you wear? Tell your family!")
S(B, "If you had fun, ask a grown up to subscribe to Bro Bros Fun!", pose="wave")
S(L, "We have a new battle every day! Next time, it's Diwali colours!", pose="wave")
S(B, "Bye friends! Happy Halloween!", pose="cheer", other_pose="cheer")
S(L, "Bye bye! Bawk bawk!", pose="cheer")
ep.action(3.5, lambda im, u, ts: (confetti(im, ts, seed=3), label(im, (640, 380), "SEE YOU TOMORROW!", 56, YEL)), sounds=[(0, "tada", 0.9)])

if __name__ == "__main__":
    print("timeline seconds:", round(ep.t, 1))
    if len(sys.argv) > 1 and sys.argv[1] == "render":
        ep.render(f"{ROOT}/out/Bro Bros Fun - Halloween Costume Challenge.mp4")
