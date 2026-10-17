#!/usr/bin/env python3
"""Preview images for Varus, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_varus.py [--out docs/preview]

  league_varus_frames.png    every animation, frame by frame, 3x on the arena colour
  league_varus_effects.png   every effect animation, 3x
  league_varus_showcase.gif  a scripted fight against Darius with Garen behind him, timed like the kit: Varus runs in;
                             two arrows stack Blight on Darius; Piercing Arrow drawn in full (the charge, Blighted Arrow's
                             crimson glow) pierces both and bursts the stacks with Blighted Arrow's blast; an arrow; Hail
                             of Arrows rains on them and leaves the corrupted ground (slowed); Chain of Corruption roots
                             Darius and spreads to Garen; arrows finish Darius - Living Vengeance flares; a quick
                             Piercing Arrow at Garen; 3x
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
CHAMP = os.path.join(LEAGUE, "champions", "league_varus")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_varus_fx", "league_varus_big")}


class At:
    """A fixed point for the views that stay where they were played (and his pivot while he stands)."""

    def __init__(self, x, y):
        self.x, self.y = x, y

    def pos(self, t):
        return self.x, self.y


def showcase(out, z=3, step=40):
    me_sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_varus_fx"], fx["league_varus_big"]
    W, H = 340, 150
    gy = 104
    x0 = 66
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 58, gy + 4)     # 57.5 px: his range
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 86, gy - 10)     # behind him
    body, under, over = [], [], []
    t = 0.0
    x = x0
    me = At(x, gy)

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

    def arrow(foe, mark=None):
        """One attack: the arrow leaves the bow on tick 9 (13 px out, 8 px up); then the rest of the 56-tick interval."""
        rel = t + tick(9)
        on(me, small, "a_flash", rel)
        tx, ty = foe.pos(rel)
        arrive = fly(small, "a_arrow", rel, x + 13, gy - 8, tx, ty - 8, 7.0)
        on(foe, small, "a_hit", arrive)
        if mark:
            on(foe, small, mark, arrive)
        foe.flinches.append(arrive)
        a("attack")
        a("idle", tick(56 - 24), loop=True)
        return arrive

    # he runs in; Darius and Garen wait
    walk = Anim(frames_of(me_sp, "run"), 0.0, x - 44, gy, loop=True, until=1400, x1=x)
    body.append(walk)
    t = walk.until
    a("idle", 300, loop=True)
    arrow(d, "b_v1")
    arrow(d, "b_v2")
    # Piercing Arrow, the full draw (66 ticks, Blighted Arrow ready): through both, Darius's two stacks burst
    q0 = t
    on(me, small, "q_charge", q0)
    on(me, small, "w_glow", q0)
    rel = q0 + tick(66)
    on(me, small, "q_fire", rel)
    over.append(Anim(frames_of(small, "q_arrow"), rel, x + 13, gy - 8, until=rel + tick(140 / 6.5), x1=x + 13 + 140,
                     y1=gy - 8))
    for k, foe in enumerate((d, g)):
        h = rel + tick((foe.pos(rel)[0] - x - 13) / 6.5)
        on(foe, small, "q_hit", h)
        foe.flinches.append(h)
        if k == 0:
            on(foe, small, "b_pop2", h + tick(1))
            on(foe, small, "w_pop", h + tick(2))
    a("skill")
    a("idle", 300, loop=True)
    arrow(d, "b_v1")
    # Hail of Arrows on them: the arrows land 20 ticks after the release (tick 10), the ground stays 240 ticks
    e0 = t
    rel = e0 + tick(10)
    on(me, small, "e_cast", rel)
    spot = At(int((d.pos(rel)[0] + g.pos(rel)[0]) // 2), gy)
    on(spot, big, "e_rain", rel)
    land = rel + tick(20)
    on(spot, big, "e_ground", rel, ground=True)          # empty until the landing, then the ground 240 ticks
    for k, foe in enumerate((d, g)):
        on(foe, small, "e_hit", land)
        on(foe, small, "e_slow", land, until=land + tick(240), ground=True)
        foe.flinches.append(land)
        if k == 0:
            on(foe, small, "b_pop1", land + tick(1))
    a("skill2")
    a("idle", 400, loop=True)
    # Chain of Corruption: the tendril at Darius (5.5 a tick), roots him 120 ticks, spreads to Garen 30 ticks later
    r0 = t
    rel = r0 + tick(15)
    on(me, small, "r_cast", rel)
    tx, ty = d.pos(rel)
    hit = fly(small, "r_chain", rel, x + 14, gy - 8, tx, ty - 8, 5.5)
    on(d, small, "r_hit", hit)
    on(d, small, "r_bind", hit, until=hit + tick(120))
    on(d, small, "b_v3", hit + tick(2))
    d.holds.append((hit, hit + tick(120)))
    d.flinches.append(hit)
    sp = At(*d.pos(hit))
    on(sp, big, "r_spread", hit + tick(30), ground=True)
    on(g, small, "r_spread_hit", hit + tick(31))
    on(g, small, "r_bind", hit + tick(31), until=hit + tick(121))
    g.holds.append((hit + tick(31), hit + tick(121)))
    g.flinches.append(hit + tick(31))
    a("ult")
    a("idle", 200, loop=True)
    # arrows finish Darius: Living Vengeance flares and his attack speed burns for 5 s
    arrow(d, "b_v1")
    last = arrow(d, "b_v2")
    d.death = last
    on(me, big, "p_rage_on", last + tick(5))
    on(me, small, "p_rage", last + tick(5), until=last + tick(300), ground=True)
    a("idle", 300, loop=True)
    # a quick Piercing Arrow at Garen (24 ticks: only minions near... here to show the quick draw)
    q1 = t
    on(me, small, "q_charge_s", q1)
    rel = q1 + tick(24)
    on(me, small, "q_fire", rel)
    over.append(Anim(frames_of(small, "q_arrow_s"), rel, x + 13, gy - 8, until=rel + tick(100 / 6.5), x1=x + 13 + 100,
                     y1=gy - 8))
    h = rel + tick((g.pos(rel)[0] - x - 13) / 6.5)
    on(g, small, "q_hit", h)
    g.flinches.append(h)
    a("skill_quick")
    a("idle", 900, loop=True)
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
                                os.path.join(args.out, "league_varus_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_varus_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_varus_showcase.gif")))


if __name__ == "__main__":
    main()
