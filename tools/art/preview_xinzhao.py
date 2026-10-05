#!/usr/bin/env python3
"""Preview images for Xin Zhao, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_xinzhao.py [--out docs/preview] [--only frames|effects|showcase|red]

  league_xinzhao_frames.png    every animation, frame by frame, 3x on the arena colour
  league_xinzhao_effects.png   every effect animation, 3x
  league_xinzhao_showcase.gif  a scripted fight against Darius with Garen behind him, timed like the kit
                               (tools/kit/build_xinzhao.py, 60 ticks a second): Xin Zhao runs in; Audacious Charge leaps
                               him onto Darius (the streak, the landing ring, the slow) and arms Three Talon Strike (the
                               talon marks over his head count down); the three thrusts, the third knocking Darius up;
                               Determination's third swing heals him; Wind Becomes Lightning slashes and thrusts its bolt
                               down the line; Crescent Guard sweeps round him - Darius, challenged, stays beside him,
                               Garen is knocked back - and the guard's glow holds 3 s; Darius falls; 3x
  league_xinzhao_red.gif       the same fight mirrored (he faces left, as on the red side): the caster pictures played
                               after the first tick (not following) are drawn mirrored by his facing, the thrust's line
                               picture turned half round - nothing may stand upside down or backwards
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
CHAMP = os.path.join(LEAGUE, "champions", "league_xinzhao")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_xinzhao_fx", "league_xinzhao_big")}
ATK_CD = 60                         # the attack's interval (atk_cd)
A_HIT, P_HIT, Q_HIT, Q3_HIT = 11, 13, 11, 13      # hit ticks of the plain thrust, Determination, Q1/Q2 and Q3
E_ANIM, E_SPEED = 16, 3.5           # E: the leap's strip, 3500 a tick
W_SLASH, W_THRUST = 13, 17          # W: the slash and the thrust
R_AT, R_GUARD = 10, 180             # R: the sweep, the guard's ticks


def showcase(out, z=3, step=40, mirror=False):
    me_sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_xinzhao_fx"], fx["league_xinzhao_big"]
    W, H = 340, 150
    gy = 104
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), 200, gy + 4)
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), 232, gy - 10)     # behind him
    d.walks, g.walks = [], []
    body, under, over = [], [], []
    t = 0.0
    x = 56

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
        """A view on him that follows his body (the leap's streak, R's tell, the buffs)."""
        an = Follow(frames_of(sp, tag), when, x, gy, loop=until is not None, until=until, on=body)
        (under if ground else over).append(an)
        return an

    def here(sp, tag, when, px=None, ground=False):
        """A view played where he stands, not following (played after the action's first tick)."""
        an = Anim(frames_of(sp, tag), when, x if px is None else px, gy, z=-1 if ground else 1)
        (under if ground else over).append(an)
        return an

    def strike(tag, hit_tick, fx_tags, foe):
        h = t + tick(hit_tick)
        for f in fx_tags:
            on(foe, small, f, h)
        foe.flinches.append(h)
        a(tag)
        a("idle", max(0.0, tick(ATK_CD) - sum(ms for _, ms in frames_of(me_sp, tag))), loop=True)
        return h

    # he runs in; Darius and Garen wait
    a("run", 1100, loop=True, to=104)
    a("idle", 200, loop=True)
    # Audacious Charge: the leap onto Darius (his attack range 26 px off), the landing ring, the slow; Q armed
    e0 = t
    dist = (d.x - 26) - x
    flight = tick(dist / E_SPEED)
    mine(big, "e_dash", e0)
    body.append(Anim(frames_of(me_sp, "skill"), e0, x, gy, until=e0 + max(flight, tick(E_ANIM)), x1=x + dist))
    t = e0 + max(flight, tick(E_ANIM))
    x += dist
    here(big, "e_land", t, ground=True)
    on(d, small, "e_hit", t)
    on(d, small, "e_slow", t, until=t + tick(30), ground=True)
    d.flinches.append(t)
    a("idle", tick(6), loop=True)
    # Three Talon Strike: the marks over his head count 3, 2, 1
    q1 = strike("q1", Q_HIT, ["a_hit", "q_hit"], d)
    mine(small, "q_1", e0 + tick(E_ANIM), until=q1)
    q2 = strike("q2", Q_HIT, ["a_hit", "q_hit"], d)
    mine(small, "q_2", q1, until=q2)
    q3 = strike("q3", Q3_HIT, ["a_hit", "q_hit", "q3_up"], d)              # the third: Determination too
    mine(small, "q_3", q2, until=q3)
    on(d, small, "p_hit", q3)
    here(small, "p_heal", q3)
    d.holds.append((q3, q3 + tick(45)))
    strike("attack", A_HIT, ["a_hit"], d)
    strike("attack", A_HIT, ["a_hit"], d)
    p = strike("attack_p", P_HIT, ["a_hit", "p_hit"], d)                   # Determination's third swing heals
    here(small, "p_heal", p)
    # Wind Becomes Lightning: the slash in front of him, then the bolt down the line (60 px from him)
    w0 = t
    here(big, "w_slash", w0 + tick(W_SLASH))
    on(d, small, "w_hit", w0 + tick(W_SLASH))
    line = Anim(frames_of(big, "w_thrust"), w0 + tick(W_THRUST), x + 30, gy, z=1)
    over.append(line)
    for foe in (d, g):
        on(foe, small, "w_hit2", w0 + tick(W_THRUST + 1))
        on(foe, small, "w_slow", w0 + tick(W_THRUST + 1), until=w0 + tick(W_THRUST + 91), ground=True)
        foe.flinches.append(w0 + tick(W_THRUST + 1))
    a("skill2")
    a("idle", tick(10), loop=True)
    strike("attack", A_HIT, ["a_hit"], d)
    # Crescent Guard: the tell from the first tick (following), the sweep round him on tick 10; Darius challenged and
    # kept beside him, Garen knocked back (2500 a tick for 8 ticks: 20 px); the guard's glow 3 s under him
    r0 = t
    mine(big, "r_tell", r0)
    rs = r0 + tick(R_AT)
    here(big, "r_sweep", rs)
    for foe in (d, g):
        on(foe, small, "r_hit", rs)
        foe.flinches.append(rs)
    on(d, small, "r_chal", rs, until=rs + tick(90))
    g.walks.append((rs, rs + tick(8), 20))
    mine(big, "r_guard", rs, until=rs + tick(R_GUARD), ground=True)
    a("ult")
    while t < rs + tick(R_GUARD) - tick(ATK_CD):
        last = strike("attack", A_HIT, ["a_hit"], d)
    d.death = last
    a("idle", 1200, loop=True)
    end = t

    def place(img, f, px, py, flip=False):
        if flip:
            f = f.transpose(Image.FLIP_LEFT_RIGHT)
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
        for _, f, pnt in sorted(units, key=lambda u: u[0]):
            if f is not None:
                place(img, f, *pnt)
        for an in over:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        if mirror:      # the red side: the whole scene seen from the other side (he faces left)
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
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
    ap.add_argument("--only", choices=["frames", "effects", "showcase", "red"])
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    if args.only in (None, "frames"):
        s = load(CHAMP)
        print("frames", contact([(s, t["name"], t["name"]) for t in s.tags],
                                os.path.join(args.out, "league_xinzhao_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[15:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_xinzhao_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_xinzhao_showcase.gif")))
    if args.only == "red":
        print("red side frames/seconds", showcase(os.path.join(args.out, "league_xinzhao_red.gif"), mirror=True))


if __name__ == "__main__":
    main()
