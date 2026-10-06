#!/usr/bin/env python3
"""Preview images for Gwen, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_gwen.py [--out docs/preview] [--only frames|effects|showcase]

  league_gwen_frames.png    every animation, frame by frame, 3x on the arena colour
  league_gwen_effects.png   every effect animation, 3x
  league_gwen_showcase.gif  a scripted fight against Darius with Garen behind him, timed like the kit
                            (tools/kit/build_gwen.py, 60 ticks a second): Gwen runs in; four snips stack Q (the marks
                            over her head); Q snips five times and the big one; E skips past Darius onto Garen, snips
                            him as she lands, the Hallowed Mist settles round her; she turns on them - facing left from
                            here, as on the red side: her frames mirrored with what is drawn into them - an attack, R's
                            three volleys (1, 3, 5 needles) down the line through both with attacks between them; Darius
                            falls; 3x
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
CHAMP = os.path.join(LEAGUE, "champions", "league_gwen")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_gwen_fx", "league_gwen_big")}
ATK_CD, ATK_DUR, A_HIT = 56, 24, 11                    # atk_cd, atk_dur, the hit tick
Q_DUR, Q_T0, Q_GAP, Q_FINAL, Q_N = 30, 6, 3, 22, 4
E_TICK, E_T, W_T = 8, 240, 240
R_T0, R_GAP, R_ANIM, R_APPLY = 10, 36, 24, 4
LINE = 80                                              # r_len 80000


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_gwen_fx"], fx["league_gwen_big"]
    W, H = 340, 150
    gy = 100
    x0 = 70
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 26, gy)     # her attack range
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 70, gy - 6)   # behind him
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0
    face = [False]                                     # flipped: facing left

    def a(tag, dur=None, loop=False):
        nonlocal t
        x, y = me.pos(t)
        an = Anim(frames_of(sp, tag), t, x, y, loop=loop, until=(t + dur) if dur else None, flip=face[0])
        body.append(an)
        t = an.until
        return an

    def hit(foe, tag, when):
        over.append(OnFoe(frames_of(small, tag), when, foe))
        foe.flinches.append(when)

    marks = []

    def stack(when):
        k = len([m for m in marks if m.until is None or m.until > when]) + 1
        if k <= Q_N:
            m = OnMe(frames_of(small, f"qs{k}"), when, me, until=10 ** 9)
            marks.append(m)
            over.append(m)

    def spend(when):
        for m in marks:
            if m.until is None or m.until > when:
                m.until = when

    def attack(foe):
        s0 = t
        hit(foe, "a_hit", s0 + tick(A_HIT))
        stack(s0 + tick(A_HIT))
        a("attack", tick(ATK_DUR))
        a("idle", tick(ATK_CD - ATK_DUR), loop=True)

    # she runs in; Darius and Garen wait
    walk = Anim(frames_of(sp, "run"), 0.0, x0 - 60, gy, loop=True, until=1300, x1=x0)
    body.append(walk)
    t = walk.until
    a("idle", 300, loop=True)
    for _ in range(Q_N):
        attack(d)
    # Q: 1 + 4 snips and the big one (the cuts are in her frames); the stacks are spent
    q0 = t
    for k in range(Q_N + 1):
        hit(d, "q_hit", q0 + tick(Q_T0 + k * Q_GAP))
    hit(d, "q_true", q0 + tick(Q_FINAL))
    spend(q0 + tick(1))
    a("skill", tick(Q_DUR))
    a("idle", 300, loop=True)
    # E: the skip past Darius onto Garen's far side (the trail is in her frames); she lands snipping him, the mist
    e0 = t
    land = e0 + tick(E_TICK)
    gx = g.pos(e0)[0] + 18
    me.moves.append((e0, land, me.pos(e0)[0], gx))
    an = Anim(frames_of(sp, "skill2"), e0, me.pos(e0)[0], gy, x1=gx)          # the whole strip (skip and W)
    an.pos = me.pos
    body.append(an)
    hit(g, "a_hit", land + tick(1))
    stack(land + tick(1))
    under.append(Anim(frames_of(big, "w_mist"), land, gx, gy))
    over.append(OnMe(frames_of(small, "e_on"), land, me, until=land + tick(E_T)))
    over.append(OnMe(frames_of(small, "w_in"), land + tick(6), me, until=land + tick(W_T)))
    t = an.until
    # she turns on them: facing left from here (the red side's way)
    face[0] = True
    attack(g)
    # R: three volleys to the left, attacks woven between them
    r0 = t
    for k, tag in enumerate(("r_v1", "r_v2", "r_v3")):
        thr = r0 + tick(R_T0 + k * R_GAP)
        cx = me.pos(thr)[0] - LINE // 2
        fr = [(f.transpose(Image.FLIP_LEFT_RIGHT), ms) for f, ms in frames_of(big, tag)]
        over.append(Anim(fr, thr, cx, gy))
        for foe in (g, d):
            if foe.death is None or foe.death > thr:
                hit(foe, "r_hit", thr + tick(R_APPLY - 1))
                over.append(OnFoe(frames_of(small, "r_slow"), thr + tick(R_APPLY), foe))
                over[-1].loop, over[-1].until = True, thr + tick(R_APPLY + 60)
        if k == 2:
            d.death = thr + tick(R_APPLY + 2)
    u = a("ult")                                       # the strip is shorter than R_T0 + R_ANIM: the idle after it
    a("idle", max(1.0, tick(R_T0 + R_ANIM) - u.total), loop=True)   # (she vanished for those frames)
    for _ in range(2):
        a("idle", tick(R_GAP - R_ANIM - 4), loop=True)
        attack(g)
    a("idle", 1000, loop=True)
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
                                os.path.join(args.out, "league_gwen_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[12:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_gwen_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_gwen_showcase.gif")))


if __name__ == "__main__":
    main()
