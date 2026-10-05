#!/usr/bin/env python3
"""Preview images for Lissandra, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_lissandra.py [--out docs/preview]

  league_lissandra_frames.png    every animation, frame by frame, 3x on the arena colour
  league_lissandra_effects.png   every effect animation, 3x
  league_lissandra_showcase.gif  a scripted fight against Darius with Garen behind him, timed like the kit: Lissandra
                                 glides in; an ice bolt; Ice Shard flies through both (frost at their feet); Glacial
                                 Path's claw slides to Darius, she blinks after it and the Ring of Frost roots both; a
                                 bolt; Frozen Tomb encases Darius (the black ice bursts round him, the frozen field under
                                 them slows Garen); a bolt finishes Darius and he rises as her thrall, which shatters on
                                 Garen; crowded, she freezes herself in ice; 3x
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
CHAMP = os.path.join(LEAGUE, "champions", "league_lissandra")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_lissandra_fx", "league_lissandra_big")}


class At:
    """A fixed point for the views that stay where they were played (and her pivot while she stands)."""

    def __init__(self, x, y):
        self.x, self.y = x, y

    def pos(self, t):
        return self.x, self.y


def showcase(out, z=3, step=40):
    me_sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_lissandra_fx"], fx["league_lissandra_big"]
    W, H = 340, 150
    gy = 104
    x0 = 70
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 55, gy + 4)     # 55 px: her range
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 84, gy - 10)     # behind him
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

    def bolt(foe):
        """One attack: the bolt leaves on tick 13 (the start of frame 4) 8 px up; then the rest of the 85-tick interval."""
        rel = t + tick(13)
        tx, ty = foe.pos(rel)
        arrive = fly(small, "a_bolt", rel, x + 10, gy - 8, tx, ty - 8, 5.0)
        on(foe, small, "a_hit", arrive)
        foe.flinches.append(arrive)
        a("attack")
        a("idle", tick(85 - 26), loop=True)
        return arrive

    # she glides in; Darius and Garen wait
    walk = Anim(frames_of(me_sp, "run"), 0.0, x - 44, gy, loop=True, until=1500, x1=x)
    body.append(walk)
    t = walk.until
    a("idle", 300, loop=True)
    bolt(d)
    # Ice Shard: 88 px at 5 a tick, through both, frost at their feet 90 ticks
    q = t + tick(12)
    on(me, small, "q_cast", q)
    over.append(Anim(frames_of(small, "q_shard"), q, x + 17, gy - 15, until=q + tick(88 / 5.0), x1=x + 17 + 88, y1=gy - 15))
    for foe in (d, g):
        h = q + tick((foe.pos(q)[0] - x) / 5.0)
        on(foe, small, "q_hit", h)
        on(foe, small, "q_slow", h, until=h + tick(90), ground=True)
        foe.flinches.append(h)
    a("skill")
    a("idle", 300, loop=True)
    # Glacial Path: the claw slides to Darius (3.5 a tick), she blinks after it; the Ring of Frost roots both 75 ticks
    e0 = t
    on(me, small, "e_cast", e0 + tick(4))
    dx_, _ = d.pos(e0)
    land = dx_ - 22
    arrive = fly(small, "e_claw", e0 + tick(4), x + 17, gy - 2, dx_, gy - 2, 3.5)
    on(d, small, "e_hit", arrive)
    d.flinches.append(arrive)
    a("skill2_e", arrive - e0)
    x = land
    me = At(x, gy)
    on(me, big, "e_port", t)
    ring = t + tick(4)
    a("idle", tick(4))
    on(me, big, "w_ring_late", ring, ground=True)
    for foe in (d, g):
        on(foe, small, "w_hit", ring)
        on(foe, small, "w_root", ring, until=ring + tick(75), ground=False)
        foe.holds.append((ring, ring + tick(75)))
        foe.flinches.append(ring)
    a("skill2")
    a("idle", 300, loop=True)
    bolt(d)
    # Frozen Tomb on Darius: stunned 90 ticks in the tomb, the black ice bursts round him, the field slows 3 s
    r0 = t
    on(me, big, "r_cast", r0)
    hit = r0 + tick(10)
    on(d, big, "r_tomb", hit, until=hit + tick(90))
    d.holds.append((hit, hit + tick(90)))
    spot = At(*d.pos(hit))
    on(spot, big, "r_burst", hit + tick(1), ground=True)
    on(spot, big, "r_field", hit + tick(1), until=hit + tick(181), ground=True)
    on(g, small, "r_slow", hit + tick(2), until=hit + tick(180), ground=True)
    g.flinches.append(hit + tick(1))
    a("ult")
    a("idle", 900, loop=True)
    # a bolt finishes Darius; he rises as her thrall and shatters 90 ticks later on Garen
    last = bolt(d)
    d.death = last
    corpse = At(*d.pos(last))
    on(corpse, big, "p_thrall", last + tick(4))
    boom = last + tick(94)
    on(corpse, big, "p_burst", boom, ground=True)
    on(g, small, "p_slow", boom + tick(1), until=boom + tick(91), ground=True)
    g.flinches.append(boom + tick(1))
    a("idle", max(0.0, boom - t) + 300, loop=True)
    # crowded: she freezes herself 150 ticks
    s0 = t
    on(me, big, "r_self_cast", s0)
    on(me, big, "r_stasis", s0 + 300, until=s0 + tick(150))
    a("ult_self", tick(150), loop=True)
    a("idle", 800, loop=True)
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
                                os.path.join(args.out, "league_lissandra_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[17:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_lissandra_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_lissandra_showcase.gif")))


if __name__ == "__main__":
    main()
