#!/usr/bin/env python3
"""Preview images for Lulu, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_lulu.py [--out docs/preview] [--only showcase]

  league_lulu_frames.png    every animation, frame by frame, 3x on the arena colour
  league_lulu_effects.png   every effect animation, 3x
  league_lulu_showcase.gif  a scripted fight behind Garen against Darius, timed like the kit (work/lul/build_lulu.py):
                            Lulu skips in; two attacks: her bolt runs along the staff out of its hook and Pix's three
                            bolts follow it; Glitterlance: her lance and Pix's beside it pierce Darius and slow him (the
                            glitter ring at his feet); Whimsy + Help, Pix!: the bolt turns Darius into the critter in a
                            puff, Pix flies to Garen - his shield ring with Pix on top and the golden haste at his feet;
                            the critter turns back; Wild Growth on Garen with the ult's frame 3: the green pillar on
                            him, Darius knocked up, the growth ring under Garen; 3x
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
CHAMP = os.path.join(LEAGUE, "champions", "league_lulu")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_lulu_fx", "league_lulu_big")}
# the kit (build_lulu.P): ticks, px a tick, lifts (5000 - y_offset, in px)
ATK_ST, ATK_CD, Q_ST, W_ST = 11, 90, 10, 10
A_SPEED, P_SPEED, Q_SPEED, W_SPEED, E_SPEED = 5.0, 5.5, 5.0, 5.0, 4.5
A_LIFT, P_LIFT, Q_LIFT, QP_LIFT, W_LIFT = 6, 9, 5, 9, 9
P_N, P_GAP = 3, 4
Q_REACH = 70
W_T, E_T, W_HT, R_LAG, R_UP = 105, 150, 210, 7, 60


def showcase(out, z=3, step=40):
    lulu = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_lulu_fx"], fx["league_lulu_big"]
    W, H = 240, 130
    gy = 92                                           # her pivot row: R's pillar stands 52 px over Garen's soles
    x = 88
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x + 28, gy - 14)   # her lane partner, ahead (further up)
    g.mirrored = False
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x + 55, gy + 4)   # 55 px: her attack range
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False, at=None, to=None):
        nonlocal t
        an = Anim(frames_of(lulu, tag), t, at if at is not None else x, gy, loop=loop,
                  until=(t + dur) if dur else None, x1=to)
        body.append(an)
        t = an.until

    def on(unit, sp, tag, when, until=None, ground=False):
        an = OnFoe(frames_of(sp, tag), when, unit, z=-1 if ground else 1)
        if until is not None:
            an.loop, an.until = True, until
        (under if ground else over).append(an)
        return an

    def three(unit, sp, tag, when, until, ground=False):
        """A ThreePhase buff view: <tag>_in, then <tag> looped while the buff lasts, then <tag>_out."""
        pre = on(unit, sp, tag + "_in", when, ground=ground)
        on(unit, sp, tag, pre.until, until=until, ground=ground)
        on(unit, sp, tag + "_out", until, ground=ground)

    def homing(tag, launch, lift, unit, speed):
        """A TargetProjectile: from her pivot lifted `lift` px at the unit's pivot; returns its arrival."""
        tx, ty = unit.pos(launch)
        sx, sy = x, gy - lift
        arrive = launch + tick(max(1.0, ((tx - sx) ** 2 + (ty - sy) ** 2) ** 0.5 / speed))
        over.append(Anim(frames_of(small, tag), launch, sx, sy, until=arrive, x1=tx, y1=ty))
        return arrive

    def line(tag, launch, lift, reach, speed):
        """A LinearProjectile: from her pivot lifted `lift` px to `reach` px ahead at pivot height."""
        end = launch + tick(reach / speed)
        over.append(Anim(frames_of(small, tag), launch, x, gy - lift, until=end, x1=x + reach, y1=gy))
        return end

    # Garen and Darius trade blows while she skips in
    for k in range(7):
        g.attacks.append(300 + k * 1300)
    for k in range(3):
        d.attacks.append(900 + k * 1400)
    run_in = Anim(frames_of(lulu, "run"), 0.0, x - 40, gy, loop=True, until=700, x1=x)
    body.append(run_in)
    t = run_in.until
    a("idle", 200, loop=True)
    # two attacks: her bolt on tick 11, Pix's three 4 ticks apart
    for _ in range(2):
        launch = t + tick(ATK_ST)
        hit = homing("a_bolt", launch, A_LIFT, d, A_SPEED)
        on(d, small, "a_hit", hit)
        d.flinches.append(hit)
        for i in range(P_N):
            on(d, small, "p_hit", homing("p_bolt", launch + tick(i * P_GAP), P_LIFT, d, P_SPEED))
        a("attack")
        a("idle", tick(ATK_CD - 24), loop=True)
    # Glitterlance: both lances on tick 10, Darius hit as hers passes him, slowed 90 ticks
    launch = t + tick(Q_ST)
    line("q_lance", launch, Q_LIFT, Q_REACH, Q_SPEED)
    line("q_pix", launch, QP_LIFT, Q_REACH, Q_SPEED)
    hit = launch + tick((d.x - 6 - x) / Q_SPEED)
    on(d, small, "q_hit", hit)
    d.flinches.append(hit)
    on(d, small, "q_slow2", hit, until=hit + tick(90))
    a("skill")
    a("idle", 300, loop=True)
    # Whimsy + Help, Pix!: the polymorph on Darius (105 ticks: no attacks), Pix to Garen (shield 150, haste 210)
    launch = t + tick(W_ST)
    hit = homing("w_bolt", launch, W_LIFT, d, W_SPEED)
    three(d, small, "w_poly", hit, hit + tick(W_T))
    d.attacks = [s for s in d.attacks if not hit - 600 <= s < hit + tick(W_T)]
    land = homing("e_pix", launch, P_LIFT, g, E_SPEED)
    on(g, small, "e_land", land)
    on(g, small, "e_on", land, until=land + tick(E_T))
    on(g, small, "w_haste", land, until=land + tick(W_HT))
    a("skill2")
    a("idle", hit + tick(W_T) + 300 - t, loop=True)
    # Wild Growth on Garen: the ult's frame 3 (7 ticks): the pillar on him, Darius knocked up 60 ticks, the ring
    # under Garen (shown 2.4 s of its 7)
    r0 = t
    grow = r0 + tick(R_LAG)
    on(g, big, "r_burst", grow)
    on(d, small, "r_hit", grow)
    d.hops.append((grow, grow + tick(R_UP), 12))
    d.attacks = [s for s in d.attacks if not grow - 600 <= s < grow + tick(R_UP)]
    three(g, big, "r_on", grow, grow + 2400, ground=True)
    a("ult")
    a("idle", grow + 2400 + 400 - t, loop=True)
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
        units = [(u.pos(tt)[1], u.frame(tt), u.pos(tt)) for u in (g, d)]
        for an in body:
            f = an.frame(tt)
            if f is not None:
                units.append((an.pos(tt)[1], f, an.pos(tt)))
                break
        for _, f, p_ in sorted(units, key=lambda u: u[0]):
            if f is not None:
                place(img, f, *p_)
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
                                os.path.join(args.out, "league_lulu_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[12:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_lulu_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_lulu_showcase.gif")))


if __name__ == "__main__":
    main()
