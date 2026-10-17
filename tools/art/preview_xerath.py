#!/usr/bin/env python3
"""Preview images for Xerath, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_xerath.py [--out docs/preview] [--only frames|effects|showcase]

  league_xerath_frames.png    every animation, frame by frame, 3x on the arena colour
  league_xerath_effects.png   every effect animation, 3x
  league_xerath_showcase.gif  a scripted fight against Darius with Garen behind him, timed like the kit
                              (tools/kit/build_xerath.py, 60 ticks a second): Xerath glides in; an orb; Arcanopulse
                              charged in full pierces both; an orb, then the Mana Surge orb; Shocking Orb stuns Darius
                              and the Eye of Destruction falls on him; Rite of the Arcane: he rises, the rune circle
                              under him, four shells called down on Darius and Garen (the warning ring, the falling bolt,
                              the blast) - the last finishes Darius; 3x
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
CHAMP = os.path.join(LEAGUE, "champions", "league_xerath")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_xerath_fx", "league_xerath_big")}
ATK_CD, ATK_REL, ATK_DUR = 90, 10, 28        # atk_cd, atk_st, atk_dur
Q_FULL, Q_REC = 54, 10                       # q_full_t, q_rec
E_REL, E_DUR, W_DELAY = 10, 30, 30           # c_st, c_dur, w_delay
R_DEPLOY, R_GAP, R_DELAY, R_SHOT = 30, 54, 36, 14
CLAW = (18, -15)                             # the front claw in the release frames


class At:
    """A fixed point for the views that stay where they were played (and his pivot while he stands)."""

    def __init__(self, x, y):
        self.x, self.y = x, y

    def pos(self, t):
        return self.x, self.y


def showcase(out, z=3, step=40):
    me_sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_xerath_fx"], fx["league_xerath_big"]
    W, H = 340, 160
    gy = 112
    x0 = 66
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 56, gy + 4)     # 55 px: his range
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 92, gy - 10)     # behind him
    body, under, over = [], [], []
    t = 0.0
    x = x0
    me = At(x, gy)
    claw = At(x + CLAW[0], gy + CLAW[1])

    def a(tag, dur=None, loop=False):
        nonlocal t
        an = Anim(frames_of(me_sp, tag), t, x, gy, loop=loop, until=(t + dur) if dur else None)
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
        span = ((tx - sx) ** 2 + (ty - sy) ** 2) ** 0.5
        arrive = launch + tick(max(1.0, span / speed))
        over.append(Anim(frames_of(sp, tag), launch, sx, sy, until=arrive, x1=tx, y1=ty))
        return arrive

    def orb(foe, surge=False):
        """One attack: the orb leaves the claw on tick 10 (8 px up as it flies); then the rest of the 90-tick interval."""
        rel = t + tick(ATK_REL)
        on(claw, small, "p_surge" if surge else "a_flash", rel)
        tx, ty = foe.pos(rel)
        arrive = fly(small, "a_orb_p" if surge else "a_orb", rel, x + CLAW[0], gy - 8, tx, ty - 8, 4.5)
        on(foe, small, "p_hit" if surge else "a_hit", arrive)
        foe.flinches.append(arrive)
        a("attack")
        a("idle", tick(ATK_CD - ATK_DUR), loop=True)
        return arrive

    # he glides in; Darius and Garen wait
    walk = Anim(frames_of(me_sp, "run"), 0.0, x - 44, gy, loop=True, until=1400, x1=x)
    body.append(walk)
    t = walk.until
    a("idle", 300, loop=True)
    orb(d)
    # Arcanopulse, the full charge (54 ticks): the beam out of the claw at 15 px a tick, through both
    q0 = t
    on(me, small, "q_charge", q0)
    rel = q0 + tick(Q_FULL)
    on(claw, small, "q_fire", rel)
    sx, sy = x + CLAW[0], gy + CLAW[1]
    over.append(Anim(frames_of(small, "q_beam"), rel, sx, sy, until=rel + tick(150 / 15), x1=sx + 150, y1=sy))
    for foe in (d, g):
        h = rel + tick((foe.pos(rel)[0] - sx) / 15)
        on(foe, small, "q_hit", h)
        foe.flinches.append(h)
    a("skill", tick(Q_FULL + Q_REC))
    a("idle", 200, loop=True)
    orb(d)
    orb(d, surge=True)
    # Shocking Orb at Darius (4 px a tick): stunned 80 ticks (mid range); the Eye opens on him a tick later and
    # bursts w_delay later
    e0 = t
    rel = e0 + tick(E_REL)
    on(claw, small, "e_cast", rel)
    tx, ty = d.pos(rel)
    hit = fly(small, "e_orb", rel, x + CLAW[0], gy + CLAW[1], tx, ty - 12, 4.0)
    on(d, small, "e_hit", hit)
    on(d, small, "e_stun", hit, until=hit + tick(80))
    d.holds.append((hit, hit + tick(80)))
    d.flinches.append(hit)
    eye = At(*d.pos(hit))
    w0 = hit + tick(1)
    on(eye, big, "w_mark", w0, ground=True)
    on(eye, big, "w_blast", w0 + tick(W_DELAY - 1))
    blast = w0 + tick(W_DELAY)
    on(d, small, "w_hit", blast)
    on(d, small, "w_slow", blast, until=blast + tick(150), ground=True)
    a("skill2")
    a("idle", max(300, blast + tick(10) - t), loop=True)
    # Rite of the Arcane: the rise, the rune circle under him through the channel, four shells
    r0 = t
    on(me, big, "r_rise", r0)
    a("ult", tick(R_DEPLOY))
    shots = [d, g, d, d]
    end_r = r0 + tick(R_DEPLOY) + tick(R_GAP) * len(shots)
    on(me, big, "r_chan", r0, until=end_r, ground=True)
    for k, foe in enumerate(shots):
        s0 = t
        on(claw, small, "r_cast_shot", s0)
        spot = At(*foe.pos(s0))
        on(spot, big, "r_mark", s0, ground=True)
        on(spot, big, "r_bolt", s0 + tick(R_DELAY - 8))
        land = s0 + tick(R_DELAY)
        on(foe, small, "r_hit", land)
        foe.flinches.append(land)
        if k == len(shots) - 1:
            d.death = land + tick(2)
        a("ult_shot", tick(R_SHOT))
        a("ult_loop", tick(R_GAP - R_SHOT), loop=True)
    on(me, small, "r_end", t)
    a("idle", 1300, loop=True)
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
    sample = frames[::6]
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
                                os.path.join(args.out, "league_xerath_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_xerath_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_xerath_showcase.gif")))


if __name__ == "__main__":
    main()
