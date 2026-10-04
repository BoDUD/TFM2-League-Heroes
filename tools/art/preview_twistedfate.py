#!/usr/bin/env python3
"""Preview images for Twisted Fate, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_twistedfate.py [--out docs/preview]

  league_twistedfate_frames.png    every animation, frame by frame, 3x on the arena colour
  league_twistedfate_effects.png   every effect animation, 3x
  league_twistedfate_showcase.gif  a scripted fight against Darius with Garen behind him, timed like the kit: Twisted Fate
                                   walks in; Pick a Card shuffles blue, red and gold over his head and locks the gold
                                   card, his next attack throws it and stuns Darius (gold stars over his head); a card;
                                   the blue card (a blue splash on him: his cooldowns back); Stacked Deck's fourth (the
                                   magenta flash at his hand); Wild Cards fly through both; Pick a Card again, the red
                                   card bursts on the ground under them and slows them; Destiny marks
                                   both, the Gate opens round him, its mark on the ground ahead, he vanishes and lands
                                   there with a gold card that finishes Darius - Loaded Dice rolls a 4 over his head; 3x
"""
import argparse
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from preview_annie import Held, OnFoe  # noqa: E402
from preview_ashe import Anim, tick  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_twistedfate")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_twistedfate_fx", "league_twistedfate_big")}


class At:
    """A fixed point for the views that stay where they were played (and his pivot while he stands)."""

    def __init__(self, x, y):
        self.x, self.y = x, y

    def pos(self, t):
        return self.x, self.y


def showcase(out, z=3, step=40):
    tf = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_twistedfate_fx"], fx["league_twistedfate_big"]
    W, H = 320, 140
    gy = 96
    x0 = 70
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 55, gy + 4)     # 55 px: attack range
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 84, gy - 10)     # behind him
    body, under, over = [], [], []
    t = 0.0
    x = x0
    me = At(x, gy)

    def a(tag, dur=None, loop=False):
        nonlocal t
        an = Anim(frames_of(tf, tag), t, x, gy, loop=loop, until=(t + dur) if dur else None)
        body.append(an)
        t = an.until
        return an

    def on(unit, sp, tag, when, until=None, ground=False):
        an = OnFoe(frames_of(sp, tag), when, unit, z=-1 if ground else 1)
        if until is not None:
            an.loop, an.until = True, until
        (under if ground else over).append(an)
        return an

    def fly(sp, tag, launch, sx, sy, tx, ty, speed):
        """A picture flying from (sx, sy) to (tx, ty) at `speed` px a tick; returns its arrival."""
        span = ((tx - sx) ** 2 + (ty - sy) ** 2) ** 0.5
        arrive = launch + tick(max(1.0, span / speed))
        over.append(Anim(frames_of(sp, tag), launch, sx, sy, until=arrive, x1=tx, y1=ty))
        return arrive

    def card(tag, launch, foe, hit):
        tx, ty = foe.pos(launch)
        arrive = fly(small, tag, launch, x, gy - 3, tx, ty - 3, 5.5)
        if hit:
            on(foe, small, hit, arrive)
        foe.flinches.append(arrive)
        return arrive

    def attack(tag, foe, hit="a_hit", e=False):
        """One attack: the card leaves on tick 12 (the start of frame 4); then the rest of the 66-tick interval."""
        rel = t + tick(12)
        if e:
            on(me, small, "e_cast", rel)
        arrive = card(tag, rel, foe, hit)
        a("attack")
        a("idle", tick(66 - 26), loop=True)
        return arrive

    def shuffle(cards):
        """Pick a Card: the cast, then the cards over his head every 30 ticks; the last one locks."""
        a("skill2")
        for c in cards[:-1]:
            on(me, small, f"w_show_{c}", t, until=t + tick(30))
            a("idle", tick(30), loop=True)
        on(me, small, f"w_{cards[-1]}", t, until=t + tick(24))
        a("idle", tick(24), loop=True)
        return t

    # he walks in; Darius and Garen wait
    walk = Anim(frames_of(tf, "run"), 0.0, x - 44, gy, loop=True, until=1300, x1=x)
    body.append(walk)
    t = walk.until
    a("idle", 300, loop=True)
    # Pick a Card: blue, red, gold - locked; the next attack throws it: Darius stunned 100 ticks
    shuffle(["blue", "red", "gold"])
    on(me, small, "w_gold", t, until=t + tick(12))
    hit = attack("wg_card", d, "wg_hit")
    d.holds.append((hit, hit + tick(100)))
    on(d, small, "wg_stun", hit)
    # a card; Pick a Card again: the blue card comes up first - locked; it hits hard and hands him back his cooldowns
    # (the blue splash on him); then Stacked Deck's fourth
    attack("a_card", d)
    shuffle(["blue"])
    on(me, small, "w_blue", t, until=t + tick(12))
    hit = attack("wb_card", d, "wb_hit")
    on(me, small, "wb_back", hit)
    attack("a_card_e", d, "e_hit", e=True)
    # Wild Cards: 115 px at 4 a tick, through both
    q = t + tick(12)
    on(me, small, "q_cast", q)
    over.append(Anim(frames_of(big, "q_cards"), q, x, gy, until=q + tick(115 / 4.0), x1=x + 115, y1=gy))
    for foe in (d, g):
        h = q + tick((foe.pos(q)[0] - x) / 4.0)
        on(foe, small, "q_hit", h)
        foe.flinches.append(h)
    a("skill")
    a("idle", 400, loop=True)
    # Pick a Card again: blue, red - locked; the red card bursts on the ground under Darius, both slowed 2 s
    shuffle(["blue", "red"])
    on(me, small, "w_red", t, until=t + tick(12))
    hit = attack("wr_card", d, None)
    burst = At(*d.pos(hit))
    on(burst, big, "wr_burst", hit, ground=True)
    for foe in (d, g):
        on(foe, small, "wr_hit", hit)
        on(foe, small, "wr_slow", hit, until=hit + tick(120), ground=True)
        foe.flinches.append(hit)
    a("idle", 300, loop=True)
    # Destiny: the cast, the eye over both; the Gate opens round him, its mark where he will land
    r0 = t
    on(me, big, "r_cast", r0)
    for foe in (d, g):
        on(foe, small, "r_seen", r0 + tick(6), until=r0 + tick(6) + 4000)
    a("ult")
    land_x = x + 26
    dest = At(land_x, gy)
    g0 = t
    on(me, big, "r_gate", g0)
    on(dest, big, "r_dest", g0, ground=True)
    a("ult_gate")
    on(At(x, gy), big, "r_out", t)
    x = land_x
    me = At(x, gy)                                  # a new point: the views played before stay where they were
    on(me, big, "r_in", t)
    a("ult_land")
    # the gold card he lands with finishes Darius; Loaded Dice: a 4 over his head
    on(me, small, "w_gold", t, until=t + tick(12))
    last = attack("wg_card", d, "wg_hit")
    d.death = last
    roll = on(me, small, "dice_roll", last + tick(3))
    on(me, small, "dice_4", roll.until, until=roll.until + tick(54) - roll.total)
    on(me, small, "dice_out", roll.until + tick(54) - roll.total)
    a("idle", 1400, loop=True)
    end = t

    def place(img, f, px, py):
        img.alpha_composite(f, (px - f.width // 2, py - f.height // 2))

    frames, tt = [], 0.0
    while tt < end:
        img = Image.new("RGBA", (W, H), ARENA)
        for an in under:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        units = [(g.pos(tt)[1], g.frame(tt), g.pos(tt)), (d.pos(tt)[1], d.frame(tt), d.pos(tt))]
        for an in body:
            f = an.frame(tt)
            if f is not None:
                units.append((an.pos(tt)[1], f, an.pos(tt)))
                break
        for _, f, p in sorted(units, key=lambda u: u[0]):
            if f is not None:
                place(img, f, *p)
        for an in over:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        frames.append(img.resize((W * z, H * z), Image.NEAREST).convert("RGB"))
        tt += step
    sample = frames[::6]                              # one palette for the whole clip
    strip = Image.new("RGB", (W * z, H * z * len(sample)))
    for i, f in enumerate(sample):
        strip.paste(f, (0, i * H * z))
    pal = strip.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q_ = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q_[0].save(T.long_path(out), save_all=True, append_images=q_[1:], duration=step, loop=0)
    return len(frames), round(end / 1000.0, 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    ap.add_argument("--only", choices=["frames", "effects", "showcase"])
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    if args.only in (None, "frames"):
        s = load(CHAMP)
        print("frames", contact([(s, t["name"], t["name"]) for t in s.tags],
                                os.path.join(args.out, "league_twistedfate_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[19:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_twistedfate_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_twistedfate_showcase.gif")))


if __name__ == "__main__":
    main()
