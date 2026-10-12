#!/usr/bin/env python3
"""Preview images for Irelia, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_irelia.py [--out docs/preview] [--only frames|effects|showcase]

  league_irelia_frames.png    every animation, frame by frame, 3x on the arena colour: the 1x tags and the dense hd_
                              ones the game plays with league.dll
  league_irelia_effects.png   every effect animation, 3x
  league_irelia_showcase.gif  a scripted fight against Darius with Garen behind him, timed like the kit
                              (tools/kit/build_irelia.py, 60 ticks a second): a blade strike on Darius; E - a blade at
                              her feet, the two blades meeting along the line through Darius and Garen (both struck,
                              Darius stunned and marked); Q - the dash onto the marked Darius, the mark spent, a second
                              dash on to Garen; W - the guard of blades, then the slash along the line; R - the volley
                              flying to Darius, the burst on both (slowed, marked) and the blade wall round him; 3x.
                              She is drawn as the game draws her on the battlefield: her dense (hd_) frames at PPU 2
                              and 85% (league_main hd.rs SIZES).
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
from build_irelia import P  # noqa: E402
import ppu_irelia  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_irelia")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_irelia_fx", "league_irelia_big")}


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_irelia_fx"], fx["league_irelia_big"]
    W, H = 190, 110
    gy = 80
    x0 = 40
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 42, gy)       # in her blades' reach
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 82, gy)        # behind him, on the line
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        x, y = me.pos(t)
        # her dense frames at the battlefield's size (PPU 2, then 85%: league_main hd.rs SIZES), as the game draws her
        an = Anim(frames_of(sp, "hd_" + tag), t, x, y, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        an.scale = z * ppu_irelia.SIZE / ppu_irelia.PPU
        body.append(an)
        t = an.until
        return an

    def hit(foe, tag, when, sheet=None):
        over.append(OnFoe(frames_of(sheet or small, tag), when, foe))
        foe.flinches.append(when)

    def lasting(foe, tag, when, ticks, sheet=None):
        over.append(OnFoe(frames_of(sheet or small, tag), when, foe, until=when + tick(ticks)))

    a("idle", 500, loop=True)
    # a blade strike on Darius
    hit(d, "a_hit", t + tick(P["atk_st"]))
    a("attack", tick(P["atk_dur"]))
    a("idle", 300, loop=True)
    # E: a blade at her feet, the two meeting along the line through Darius and Garen
    e0 = t
    over.append(OnMe(frames_of(small, "e_cast"), e0, me))
    x, y = me.pos(e0)
    over.append(Anim(frames_of(big, "e_line"), e0, x + P["e_len"] / 2000.0, y, loop=True,
                     until=e0 + tick(P["e_rel"] + 6)))
    strike = e0 + tick(P["e_rel"])
    for u in (d, g):
        hit(u, "e_hit", strike)
        lasting(u, "e_stun", strike, P["e_stun"])
        u.holds.append((strike, strike + tick(P["e_stun"])))
    lasting(d, "mark", strike, 90)
    lasting(g, "mark", strike, 140)
    a("skill2", tick(P["e_dur"]))
    a("idle", 200, loop=True)
    # Q: the dash onto marked Darius (the mark spent), on to Garen
    for foe in (d, g):
        q0 = t
        x0_, _ = me.pos(q0)
        to = foe.pos(q0)[0] - 22
        me.moves.append((q0, q0 + tick(P["q_dur"]) * 0.7, x0_, to))
        hit(foe, "q_hit", q0 + tick(P["q_dur"]) * 0.7)
        a("skill", tick(P["q_dur"]))
        a("idle", 120, loop=True)
    # back off, then W: the guard of blades, the slash along the line toward Darius
    me.moves.append((t, t + 700, me.pos(t)[0], x0))
    a("run", 700, loop=True)
    w0 = t
    over.append(OnMe(frames_of(small, "w_on"), w0, me, until=w0 + tick(P["w_charge"])))
    rel = w0 + tick(P["w_charge"])
    over.append(OnMe(frames_of(big, "w_slash"), rel, me))
    x, y = me.pos(rel)
    over.append(Anim(frames_of(big, "w_line"), rel, x + P["w_len"] / 2000.0, y))
    hit(d, "w_hit", rel + tick(2))
    a("skill2_w", tick(P["w_dur"]))
    a("idle", 300, loop=True)
    # R: the volley to Darius, the burst on both, the blade wall round him
    r0 = t
    go = r0 + tick(P["r_rel"])
    x, y = me.pos(go)
    tx = d.pos(go)[0]
    land = go + tick((tx - x) / (P["r_speed"] / 1000.0))
    over.append(Anim(frames_of(big, "r_blades"), go, x, y, loop=True, until=land, x1=tx, y1=y))
    under.append(Anim(frames_of(big, "r_wall_v"), land, tx, gy))
    for u in (d, g):
        hit(u, "r_hit", land)
        lasting(u, "r_slow", land, P["r_slow_t"])
    lasting(d, "mark", land, 120)
    a("ult", tick(P["r_anim"]))
    a("idle", max(400, land - t + 1600), loop=True)
    end = t

    def place(img, f, px, py, k=z):
        """f (centred on its pivot) drawn k times its size with its centre on (px, py) game px."""
        if k != 1:
            f = f.resize((max(1, round(f.width * k)), max(1, round(f.height * k))), Image.NEAREST)
        img.alpha_composite(f, (round(px * z + z / 2 - f.width / 2), round(py * z + z / 2 - f.height / 2)))

    frames, tt = [], 0.0
    while tt < end:
        img = Image.new("RGBA", (W * z, H * z), ARENA)
        for an in under:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        units = [(u.pos(tt)[1], u.frame(tt), u.pos(tt), z) for u in (g, d)]
        for an in body:
            f = an.frame(tt)
            if f is not None:
                units.append((an.pos(tt)[1] + 0.5, f, an.pos(tt), an.scale))
                break
        for _, f, p, k in sorted(units, key=lambda u: u[0]):
            if f is not None:
                place(img, f, *p, k)
        for an in over:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        frames.append(img.convert("RGB"))
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
                                os.path.join(args.out, "league_irelia_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_irelia_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_irelia_showcase.gif")))


if __name__ == "__main__":
    main()
