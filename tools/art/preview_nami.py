#!/usr/bin/env python3
"""Preview images for Nami, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_nami.py [--out docs/preview]

  league_nami_frames.png    every animation, frame by frame, 3x on the arena colour
  league_nami_effects.png   every effect animation, 3x
  league_nami_showcase.gif  a scripted fight with Lucian behind her against Darius and Garen, timed like the kit: Nami
                            swims in and her orb shoots two water bolts at Darius; Ebb and Flow's stream hits Darius,
                            leaps to Lucian - healing him, blessing him for 4 s and hastening him (Surging Tides) - and
                            on to Garen, walking in; Aqua Prison's bubble arcs onto Darius over its landing ring,
                            bursts and holds him and Garen afloat in bubbles for 1.25 s; when both come at her, Tidal
                            Wave rolls out from her planted staff and throws them up; 3x
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
CHAMP = os.path.join(LEAGUE, "champions", "league_nami")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_nami_fx", "league_nami_big")}


class Arc(Anim):
    """A lobbed projectile: straight across from (x, y) to (x1, y1), lifted by a parabola `h` px high at the middle."""

    def __init__(self, *args, h=0, **kw):
        super().__init__(*args, **kw)
        self.h = h

    def pos(self, t):
        x, y = super().pos(t)
        u = min(1.0, max(0.0, (t - self.t0) / (self.until - self.t0)))
        return x, int(round(y - 4 * self.h * u * (1 - u)))


def showcase(out, z=3, step=40):
    nami = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_nami_fx"], fx["league_nami_big"]
    W, H = 300, 150
    gy = 104                                          # the pivot row
    x = 72
    lucian_x, lucian_y = 36, gy - 4                   # Lucian behind her (drawn before her as she swims past)
    lucian = Anim(frames_of(load(os.path.join(LEAGUE, "champions", "league_lucian")), "idle"), 0.0, lucian_x, lucian_y,
                  loop=True, until=None)
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), 127, gy)          # 55 px: attack range
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), 284, gy - 8)       # walking in
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False, at=None, to=None):
        nonlocal t
        an = Anim(frames_of(nami, tag), t, at if at is not None else x, gy, loop=loop,
                  until=(t + dur) if dur else None, x1=to)
        body.append(an)
        t = an.until

    def fx_at(sp, tag, at, px, py, ground=False, until=None, x1=None, y1=None, loop=None):
        an = Anim(frames_of(sp, tag), at, px, py, z=-1 if ground else 1,
                  loop=(until is not None) if loop is None else loop, until=until, x1=x1, y1=y1)
        (under if ground else over).append(an)
        return an

    def leg(launch, tag, x0, y0, foe_pos, speed):
        """A picture flying from (x0, y0) to a unit's body at `speed` px a tick; returns its arrival."""
        tx, ty = foe_pos
        arrive = launch + tick(max(1.0, abs(tx - x0) / speed))
        fx_at(small, tag, launch, x0, y0, until=arrive, x1=tx, y1=ty - 8)
        return arrive

    orb = (x + 16, gy - 20)                           # the staff's orb when she thrusts it
    # she swims in; Garen walks up behind Darius
    run_in = Anim(frames_of(nami, "run"), 0.0, x - 44, gy, loop=True, until=1000, x1=x)
    body.append(run_in)
    t = run_in.until
    g.walks.append((600.0, 3000.0, 144 - g.x))
    a("idle", 400, loop=True)
    for _ in range(2):                                # two attacks: the bolt leaves on tick 11, 90-tick cooldown
        launch = t + tick(11)
        arrive = leg(launch, "bolt", *orb, d.pos(launch), 5.0)
        over.append(OnFoe(frames_of(small, "hit"), arrive, d, z=1))
        d.flinches.append(arrive)
        a("attack")
        a("idle", tick(90) - tick(30), loop=True)
    # Ebb and Flow: on tick 8 the stream flies at Darius, leaps to Lucian (heal, 4 s blessing, haste) and on to Garen
    start = t
    hit1 = leg(start + tick(8), "w_stream", *orb, d.pos(start + tick(8)), 4.5)
    over.append(OnFoe(frames_of(small, "w_hit"), hit1, d, z=1))
    d.flinches.append(hit1)
    dx, dy = d.pos(hit1)
    heal = leg(hit1, "w_stream", dx, dy - 8, (lucian_x, lucian_y), 4.5)
    fx_at(small, "w_heal", heal, lucian_x, lucian_y)
    fx_at(small, "e_blessing", heal, lucian_x, lucian_y, until=heal + tick(240))
    fx_at(small, "p_haste", heal, lucian_x, lucian_y, ground=True, until=heal + tick(90))
    hit3 = leg(heal, "w_stream", lucian_x, gy - 4, g.pos(heal), 4.5)
    over.append(OnFoe(frames_of(small, "w_hit"), hit3, g, z=1))
    g.flinches.append(hit3)
    a("skill")
    a("idle", 600, loop=True)
    # Aqua Prison: on tick 11 the bubble arcs onto Darius in 24 ticks over its landing ring; it bursts and holds
    # everyone within 22 px afloat for 75 ticks
    start = t
    launch = start + tick(11)
    land = launch + tick(24)
    lx, ly = d.pos(launch)
    fx_at(small, "q_mark", launch, lx, ly, ground=True)
    bubble = Arc(frames_of(small, "q_bubble"), launch, orb[0], orb[1], loop=True, until=land, x1=lx, y1=ly - 8, h=22)
    over.append(bubble)
    fx_at(small, "q_burst", land, lx, ly, ground=True)
    for foe in (d, g):
        fx_, _ = foe.pos(land)
        if abs(fx_ - lx) <= 22:
            foe.hops.append((land, land + tick(75), 6))
            over.append(OnFoe(frames_of(small, "q_prison"), land, foe, z=1))
    a("skill2")
    a("idle", 900, loop=True)
    # both come at her
    for foe, to in ((d, x + 30), (g, x + 44)):
        foe.walks.append((t, t + 900, to - foe.pos(t)[0]))
    a("idle", 1000, loop=True)
    # Tidal Wave: on tick 17 the wave rolls out at 2.5 px a tick for 160 px, knocking up everyone it passes
    start = t
    launch = start + tick(17)
    x0, x1 = x + 8, x + 8 + 160
    fx_at(big, "r_wave", launch, x0, gy + 5, until=launch + tick(160 / 2.5), x1=x1)
    for foe in (d, g):
        fx_, _ = foe.pos(launch)
        if x0 <= fx_ <= x1:
            hit = launch + tick((fx_ - x0) / 2.5)
            foe.hops.append((hit, hit + tick(30), 12))
            over.append(OnFoe(frames_of(small, "r_hit"), hit, foe, z=1))
    a("ult")
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
        units = [(g.pos(tt)[1], g.frame(tt), g.pos(tt)), (d.pos(tt)[1], d.frame(tt), d.pos(tt)),
                 (lucian.y, lucian.frame(tt), lucian.pos(tt))]
        for an in body:
            f = an.frame(tt)
            if f is not None:
                units.append((gy, f, an.pos(tt)))
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
    sample = frames[::6]                              # one palette for the whole clip
    strip = Image.new("RGB", (W * z, H * z * len(sample)))
    for i, f in enumerate(sample):
        strip.paste(f, (0, i * H * z))
    pal = strip.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q[0].save(T.long_path(out), save_all=True, append_images=q[1:], duration=step, loop=0)
    return len(frames), round(end / 1000.0, 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    s = load(CHAMP)
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_nami_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[12:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_nami_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_nami_showcase.gif")))


if __name__ == "__main__":
    main()
