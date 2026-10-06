#!/usr/bin/env python3
"""Preview images for Brand, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_brand.py [--out docs/preview] [--only frames|effects|showcase]

  league_brand_frames.png    every animation, frame by frame, 3x on the arena colour
  league_brand_effects.png   every effect animation, 3x
  league_brand_showcase.gif  a scripted fight against Darius with Garen close behind him, timed like the kit
                             (tools/kit/build_brand.py, 60 ticks a second): Brand walks in and throws two fireballs;
                             W's warning circle and the pillar on Darius (ablaze, one stack); E sets him ablaze and the
                             fire spreads to Garen (two stacks), Q's fireball stuns him (the third stack: he turns
                             unstable and blows up two seconds later, Garen caught in the blast); Brand walks round
                             them - facing left from here, as on the red side: his frames mirrored with what is drawn
                             into them - and casts R: the seed hits Garen and bounces between them, each hit burning and
                             slowing; Darius falls; 3x
"""
import argparse
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from preview_annie import Held  # noqa: E402
from preview_ashe import Anim, tick  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_samira import Me, OnFoe, OnMe  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_brand")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_brand_fx", "league_brand_big")}
ATK_CD, ATK_DUR, ATK_ST = 90, 28, 11                    # atk_cd, atk_dur, the throw tick
BOLT_T = 12                                             # the bolt's flight (52 px at 4.5 a tick)
W_DUR, W_REL, W_DELAY = 20, 11, 36
C_DUR, E_REL, Q_REL, Q_T = 32, 6, 17, 6                 # skill2; Q's flight to the target (48 px at 8 a tick)
P_WAIT = 120                                            # the unstable champion blows up
R_REL, R_ANIM, R_T, R_GAP, R_FALL, R_N = 11, 30, 14, 16, 6, 5
HAND = (17, -2)                                         # the throwing hand from his pivot (attack 4)
HIGH = (18, -13)                                        # Q's and R's shots leave 13 px up


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_brand_fx"], fx["league_brand_big"]
    W, H = 360, 150
    gy = 104
    x0 = 80
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 60, gy)        # in his range
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 90, gy - 6)     # in E's spread
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0
    face = [False]                                     # flipped: facing left
    sign = lambda: -1 if face[0] else 1

    def a(tag, dur=None, loop=False):
        nonlocal t
        x, y = me.pos(t)
        an = Anim(frames_of(sp, tag), t, x, y, loop=loop, until=(t + dur) if dur else None, flip=face[0])
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def flip(fr):
        return [(f.transpose(Image.FLIP_LEFT_RIGHT), ms) for f, ms in fr] if face[0] else fr

    def shot(tag, when, frm, foe, ticks):
        x, y = me.pos(when)
        fx_, fy = foe.pos(when + tick(ticks))
        over.append(Anim(flip(frames_of(small, tag)), when, x + sign() * frm[0], y + frm[1], x1=fx_, y1=fy - 12,
                         until=when + tick(ticks)))

    def hit(foe, tag, when, sheet=None):
        over.append(OnFoe(frames_of(sheet or small, tag), when, foe))
        foe.flinches.append(when)

    def burn(foe, when, ticks=240):
        b = OnFoe(frames_of(small, "p_burn"), when, foe)
        b.loop, b.until = True, when + tick(ticks)
        over.append(b)

    def pip(foe, k, when):
        over.append(OnFoe(frames_of(small, f"p_s{k}"), when, foe))

    # he walks in; Darius and Garen wait
    walk = Anim(frames_of(sp, "run"), 0.0, x0 - 70, gy, loop=True, until=1200, x1=x0)
    body.append(walk)
    t = walk.until
    a("idle", 300, loop=True)
    for _ in range(2):                                 # two fireballs
        s0 = t
        shot("a_bolt", s0 + tick(ATK_ST), HAND, d, BOLT_T)
        hit(d, "a_hit", s0 + tick(ATK_ST + BOLT_T))
        a("attack", tick(ATK_DUR))
        a("idle", tick(ATK_CD - ATK_DUR), loop=True)
    # W on Darius: the circle at his feet, the pillar 36 ticks later
    w0 = t
    land = w0 + tick(W_REL)
    under.append(Anim(frames_of(big, "w_mark"), land, *d.pos(land)))
    over.append(Anim(frames_of(big, "w_pillar"), land + tick(W_DELAY - 4), *d.pos(land)))
    hit(d, "w_hit", land + tick(W_DELAY + 1))
    burn(d, land + tick(W_DELAY + 1))
    pip(d, 1, land + tick(W_DELAY + 1))
    a("skill", tick(W_DUR))
    a("idle", 900, loop=True)
    # E -> Q on Darius: the spread reaches Garen; the fireball stuns him - the third stack
    c0 = t
    e_at = c0 + tick(E_REL)
    over.append(Anim(frames_of(big, "e_flare"), e_at, *d.pos(e_at)))
    for foe in (d, g):
        hit(foe, "e_hit", e_at + tick(1))
        burn(foe, e_at + tick(1))
    pip(d, 2, e_at + tick(1))
    q_at = c0 + tick(Q_REL)
    shot("q_ball", q_at, HIGH, d, Q_T)
    q_hit = q_at + tick(Q_T)
    hit(d, "q_hit", q_hit)
    pip(d, 3, q_hit)
    st = OnFoe(frames_of(small, "q_stun"), q_hit, d)
    st.loop, st.until = True, q_hit + tick(50)
    over.append(st)
    d.holds.append((q_hit, q_hit + tick(50)))
    un = OnFoe(frames_of(small, "p_unstable"), q_hit, d)
    un.loop, un.until = True, q_hit + tick(P_WAIT)
    under.append(un)
    boom = q_hit + tick(P_WAIT)
    over.append(Anim(frames_of(big, "p_boom"), boom, *d.pos(boom)))
    for foe in (d, g):
        hit(foe, "p_hit", boom + tick(1))
    a("skill2", tick(C_DUR))
    a("idle", 500, loop=True)
    # he walks round them to their right (in front of them), and turns: facing left from here (the red side's way)
    face[0] = True
    r_from, r_to = me.pos(t)[0], g.pos(t)[0] + 70
    walk2 = t + 1500
    me.moves.append((t, walk2, r_from, r_to))
    an = Anim(frames_of(sp, "run"), t, r_from, gy, loop=True, until=walk2, flip=False)
    an.pos = me.pos
    body.append(an)
    t = walk2
    a("idle", 300, loop=True)
    # R: the swirl round him, the seed at Garen, then bounces between them (the falling seed on each)
    r0 = t
    over.append(OnMe(frames_of(small, "r_cast"), r0 + tick(4), me))
    rel = r0 + tick(4 + R_REL)
    shot("r_ball", rel, HIGH, g, R_T)
    order = [g, d, g, d, g]
    when = rel + tick(R_T)
    for k, foe in enumerate(order):
        if k:
            over.append(OnFoe(frames_of(small, "r_drop"), when - tick(R_FALL), foe))
        hit(foe, "r_hit", when)
        sl = OnFoe(frames_of(small, "r_slow"), when, foe)
        sl.loop, sl.until = True, when + tick(30)
        under.append(sl)
        when += tick(R_GAP)
    d.death = when - tick(R_GAP) + tick(2)
    a("idle", tick(4), loop=True)
    a("ult", tick(R_ANIM))
    a("idle", 1500, loop=True)
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
                if an.fr is frames_of(sp, "run") and face[0] is False:
                    pass
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
                                os.path.join(args.out, "league_brand_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_brand_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_brand_showcase.gif")))


if __name__ == "__main__":
    main()
