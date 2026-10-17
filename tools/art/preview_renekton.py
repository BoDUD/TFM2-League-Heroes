#!/usr/bin/env python3
"""Preview images for Renekton, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_renekton.py [--out docs/preview] [--only frames|effects|showcase]

  league_renekton_frames.png    every animation, frame by frame, 3x on the arena colour
  league_renekton_effects.png   every effect animation, 3x
  league_renekton_showcase.gif  a scripted fight against Darius with Garen behind him, timed like the kit
                                (tools/kit/build_renekton.py, 60 ticks a second): he runs in and slashes Darius
                                (the slash in his frames), Fury fills (the red glow behind him); Q sweeps both with the
                                plain ring; E: he dashes through Darius (the streak in his frames), W empowered by the
                                full Fury - the red flare, three chops, Darius stunned 1.5 s (the stars) - and Dice back
                                through him; he turns round - facing left from here, as on the red side - and R: the
                                sand burst, the sand aura under him burning both every half second, slashes, Darius
                                falls; 3x
"""
import argparse
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
from preview_annie import Held  # noqa: E402
from preview_ashe import Anim, tick  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_pyke import Me, OnFoe, OnMe  # noqa: E402
from build_renekton import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_renekton")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_renekton_fx", "league_renekton_big")}


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_renekton_fx"], fx["league_renekton_big"]
    W, H = 330, 150
    gy = 104
    x0 = 135
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 50, gy)
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 92, gy)
    me = Me(x0 - 90, gy)
    body, under, over = [], [], []
    t = 0.0
    face = [False]

    def a(tag, dur=None, loop=False):
        nonlocal t
        x, y = me.pos(t)
        fr = frames_of(sp, tag)
        an = Anim(fr, t, x, y, loop=loop, until=(t + dur) if dur else None, flip=face[0])
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def hit(foe, tag, when, sheet=None):
        over.append(OnFoe(frames_of(sheet or small, tag), when, foe))
        foe.flinches.append(when)

    def strip_ms(tag):
        return sum(ms for _, ms in frames_of(sp, tag))

    # he runs in and slashes Darius; the third hit fills the Fury (the glow until W spends it)
    me.moves.append((t, t + 700, me.pos(t)[0], x0 + 8))
    a("run", 700, loop=True)
    fury = None
    for k in range(3):
        hit(d, "a_hit", t + tick(P["atk_st"]))
        a("attack", strip_ms("attack"))
        a("idle", tick(30), loop=True)
        if k == 1:
            fury = t
    # Q: the plain ring, both hit (the Fury is kept for W, which is ready)
    q0 = t
    under.append(OnMe(frames_of(big, "q_spin"), q0, me))
    for foe in (d, g):
        hit(foe, "q_hit", q0 + tick(P["q_hit"]))
    a("skill", strip_ms("skill"))
    a("idle", 250, loop=True)
    # E: back off a little, then dash through Darius
    me.moves.append((t, t + 300, me.pos(t)[0], x0 - 20))
    a("run", 300, loop=True)
    e0 = t
    me.moves.append((e0, e0 + tick(P["e_tick"]), me.pos(e0)[0], d.pos(e0)[0] + 22))
    hit(d, "e_hit", e0 + tick(P["e_tick"]) * 0.6)
    a("skill2", tick(P["e_tick"] + 4))
    # W empowered: the flare, three chops, Darius stunned 1.5 s; he turns back toward Darius to chop
    face[0] = True
    w0 = t
    over.append(OnMe(frames_of(small, "w_glow"), w0, me))
    for k in range(3):
        hit(d, "w_hit", w0 + tick(P["w_h1"] + k * P["w_gap"]))
    stun0 = w0 + tick(P["w_h1"] + 2 * P["w_gap"])
    d.holds.append((stun0, stun0 + tick(P["w_stun_e"])))
    over.append(OnFoe(frames_of(small, "w_stun"), stun0, d, until=stun0 + tick(P["w_stun_e"])))
    a("skill2_w", tick(P["w_dur"] + 2 * P["w_gap"] - 1))
    if fury is not None:
        under.append(OnMe(frames_of(small, "f5"), fury, me, until=w0))
    a("idle", tick(P["d_gap"]), loop=True)
    # Dice: back through Darius
    dx = t
    me.moves.append((dx, dx + tick(P["e_tick"]), me.pos(dx)[0], d.pos(dx)[0] - 26))
    hit(d, "e_hit", dx + tick(P["e_tick"]) * 0.6)
    a("skill2", tick(P["e_tick"] + 4))
    a("idle", 300, loop=True)
    # R, facing right again (blue side), then the red side's facing for the slashes: the burst, the aura burning both
    face[0] = False
    r0 = t
    over.append(OnMe(frames_of(big, "r_cast"), r0 + tick(10), me))
    r_end = r0 + 3200
    under.append(OnMe(frames_of(big, "r_on"), r0, me, until=r_end))
    for k in range(int((r_end - r0) // tick(P["r_period"]))):
        for foe in (d, g):
            hit(foe, "r_burn", r0 + tick(P["r_anim"]) + k * tick(P["r_period"]))
    a("ult", tick(P["r_anim"]))
    for k in range(4):
        hit(d, "a_hit", t + tick(P["atk_st"]))
        a("attack", strip_ms("attack"))
        a("idle", tick(20), loop=True)
    d.death = t - 300
    a("idle", r_end - t + 600, loop=True)
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
                units.append((an.pos(tt)[1] + 0.5, f, an.pos(tt)))
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
                                os.path.join(args.out, "league_renekton_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[16:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_renekton_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_renekton_showcase.gif")))


if __name__ == "__main__":
    main()
