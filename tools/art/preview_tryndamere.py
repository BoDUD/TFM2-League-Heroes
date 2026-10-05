#!/usr/bin/env python3
"""Preview images for Tryndamere, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_tryndamere.py [--out docs/preview]

  league_tryndamere_frames.png    every animation, frame by frame, 3x on the arena colour
  league_tryndamere_effects.png   every effect animation, 3x
  league_tryndamere_showcase.gif  a scripted fight against Darius with Garen behind him, timed like the kit
                                  (tools/kit/build_tryndamere.py, 60 ticks a second): Tryndamere runs in; Spinning Slash
                                  dashes him onto Darius (a Fury stack); swings; Mocking Shout roars - both lose attack,
                                  Garen (the far one) is slowed; more swings fill Fury (the full-Fury glow); in danger
                                  Undying Rage erupts and burns for 5 s while he keeps swinging, Darius falls, and at its
                                  end Bloodlust drinks the Fury; 3x
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
from preview_jinx import Follow  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_tryndamere")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_tryndamere_fx", "league_tryndamere_big")}
ATK_CD, ATK_REL = 62, 12            # the attack's interval and its hit tick (atk_cd, atk_st)
E_REL, E_TICKS = 2, 12              # E: the dash starts on tick e_st and runs e_tick ticks (4000 a tick: 48 px)
W_REL = 10                          # W: the roar on tick w_st
R_T, R_Q = 300, 290                 # R: undying ticks, Bloodlust that far in


class At:
    """A fixed point for the views that stay where they were played."""

    def __init__(self, x, y):
        self.x, self.y = x, y

    def pos(self, t):
        return self.x, self.y


def showcase(out, z=3, step=40):
    me_sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_tryndamere_fx"], fx["league_tryndamere_big"]
    W, H = 330, 150
    gy = 104
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), 182, gy + 4)
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), 216, gy - 12)     # behind him
    body, under, over = [], [], []
    t = 0.0
    x = 60

    def a(tag, dur=None, loop=False, to=None):
        nonlocal t, x
        an = Anim(frames_of(me_sp, tag), t, x, gy, loop=loop, until=(t + dur) if dur else None, x1=to)
        body.append(an)
        t = an.until
        if to is not None:
            x = to
        return an

    def on(unit, sp, tag, when, until=None, ground=False):
        an = OnFoe(frames_of(sp, tag), when, unit, z=-1 if ground else 1)
        if until is not None:
            an.loop, an.until = True, until
        (under if ground else over).append(an)
        return an

    def mine(sp, tag, when, until=None, ground=False):
        """A view on him that follows his body (e_spin through the dash, the buffs)."""
        an = Follow(frames_of(sp, tag), when, x, gy, loop=until is not None, until=until, on=body)
        (under if ground else over).append(an)
        return an

    def swing(foe):
        h = t + tick(ATK_REL)
        on(foe, small, "a_hit", h)
        foe.flinches.append(h)
        a("attack")
        a("idle", tick(ATK_CD - 24), loop=True)
        return h

    # he runs in; Darius and Garen wait
    a("run", 1100, loop=True, to=96)
    a("idle", 200, loop=True)
    # Spinning Slash: 48 px in 12 ticks onto Darius (his attack range 25 px off), a Fury stack
    e0 = t
    mine(big, "e_spin", e0)
    body.append(Anim(frames_of(me_sp, "skill"), e0, x, gy, until=e0 + tick(E_REL + E_TICKS), x1=x + 48))
    hit = e0 + tick(E_REL + 10)
    on(d, small, "e_hit", hit)
    d.flinches.append(hit)
    t = e0 + tick(E_REL + E_TICKS)
    x += 48
    a("idle", tick(10), loop=True)
    swing(d)                                            # Fury 2
    # Mocking Shout: both within 40 px lose attack for 4 s; Garen, the far one, slowed 2 s
    w0 = t
    rel = w0 + tick(W_REL)
    mine(big, "w_shout", rel)
    for foe in (d, g):
        on(foe, small, "w_hit", rel + tick(2))
        on(foe, small, "w_weak", rel + tick(2), until=rel + tick(240))
    on(g, small, "w_slow", rel + tick(2), until=rel + tick(120), ground=True)
    a("skill2")
    a("idle", tick(20), loop=True)
    swing(d)                                            # Fury 3
    swing(d)                                            # Fury 4
    full = swing(d)                                     # Fury 5: the full-Fury glow under him
    mine(small, "f_5", full, until=full + 20000, ground=True)
    swing(d)
    # danger: Undying Rage - the eruption, then 5 s of flames under him; he keeps swinging
    r0 = t
    mine(big, "r_cast", r0)
    mine(big, "r_rage", r0 + tick(2), until=r0 + tick(R_T), ground=True)
    a("ult")
    last = None
    while t + tick(ATK_CD) < r0 + tick(R_Q):
        last = swing(d)
        if d.death is None and t > r0 + tick(150):
            d.death = last
    a("idle", max(0.0, r0 + tick(R_Q) - t), loop=True)
    # Bloodlust at the rage's end: the Fury drunk
    mine(small, "q_heal", t)
    a("skill_q")
    a("idle", 1200, loop=True)
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
                                os.path.join(args.out, "league_tryndamere_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[18:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_tryndamere_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_tryndamere_showcase.gif")))


if __name__ == "__main__":
    main()
