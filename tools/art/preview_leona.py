#!/usr/bin/env python3
"""Preview images for Leona, built from the exported game sprites (so they also prove the sheets
load).

    python tools/art/preview_leona.py [--out docs/preview]

  league_leona_frames.png    every animation, frame by frame, 3x on the arena colour
  league_leona_effects.png   every effect animation, 3x
  league_leona_showcase.gif  a scripted fight against Darius and Garen, timed like the kit: Zenith Blade
                             pierces Darius, roots him and pulls Leona in, Eclipse's shell rises round her
                             as she casts it, the Shield of Daybreak bash stuns him, her sword strikes
                             follow, the Eclipse bursts after 3 s, and the Solar Flare falls on Garen as
                             he walks in: slowed, and stunned in its centre. Every spell hit leaves the
                             Sunlight mark over its target; 3x
"""
import argparse
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from preview_ashe import Anim, tick  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_jinx import Follow, Walker  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_leona")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_leona_fx", "league_leona_big")}


class Held(Walker):
    """A foe that can also be held still (stunned or rooted: its first hit frame)."""

    def __init__(self, sp, x, y):
        super().__init__(sp, x, y)
        self.holds = []

    def frame(self, t):
        if self.death is None or t < self.death:
            for t0, t1 in self.holds:
                if t0 <= t < t1:
                    return self.flip(self.hit[0][0])
        return super().frame(t)


def showcase(out, z=3, step=40):
    leona = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    W, H = 300, 170
    gy = 128                                          # Leona's pivot row: the Solar Flare's beam is 113 px tall
    x = 40
    foes = {
        "darius": Held(load(os.path.join(LEAGUE, "champions", "league_darius")), 100, gy),    # 60 px: Zenith Blade
        "garen": Held(load(os.path.join(LEAGUE, "champions", "league_garen")), 262, gy - 10),  # far off
    }
    d, g = foes["darius"], foes["garen"]
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False, at=None, to=None):
        nonlocal t
        an = Anim(frames_of(leona, tag), t, at if at is not None else x, gy, loop=loop,
                  until=(t + dur) if dur else None, x1=to)
        body.append(an)
        t = an.until

    def fx_at(sprite, tag, at, px, py=gy, ground=False, until=None, x1=None, y1=None, loop=None):
        an = Anim(frames_of(fx[sprite], tag), at, px, py, z=-1 if ground else 1,
                  loop=(until is not None) if loop is None else loop, until=until, x1=x1, y1=y1)
        (under if ground else over).append(an)
        return an

    marks = {"darius": [], "garen": []}

    def sunlight(foe, at):
        """The Sunlight mark (1.5 s) over a foe a spell hit; a new hit renews it."""
        marks[foe].append(at)

    a("idle", 400, loop=True)
    # Zenith Blade + Eclipse (one cast, read on tick 9): the blade flies 6 px a tick and pierces Darius,
    # the hidden twin stops on him: rooted 0.5 s, and Leona dashes to him (4 px a tick, e_dash for 16
    # ticks); the Eclipse buff and its shell start on the cast, the burst 178 ticks later
    start = t
    launch = start + tick(9)
    x0 = x + 4
    hit = launch + tick((d.x - 8 - x0) / 6)
    fx_at("league_leona_fx", "e_blade", launch, x0, gy - 2, until=launch + tick(65 / 6), x1=x0 + 65)
    fx_at("league_leona_fx", "e_hit", hit, d.x, d.y)
    fx_at("league_leona_fx", "e_root", hit, d.x, d.y, ground=True)
    d.holds.append((hit, hit + tick(30)))
    sunlight("darius", hit)
    over.append(Follow(frames_of(fx["league_leona_fx"], "eclipse"), launch, x, gy, loop=True,
                       until=launch + tick(180), on=body))
    burst = launch + tick(178)
    body.append(Anim(frames_of(leona, "skill2"), start, x, gy, until=hit))
    t = hit
    to = d.x - 22                                     # the dash stops at her reach
    a("e_dash", tick(16), loop=True, to=to)
    x = to
    a("idle", max(0.0, start + tick(36) - t) + 120, loop=True)
    # Shield of Daybreak: the bash on tick 11 - stunned 1 s, the Sunlight mark
    start = t
    bash = start + tick(11)
    fx_at("league_leona_fx", "q_hit", bash, d.x, d.y)
    d.holds.append((bash, bash + tick(60)))
    d.flinches.append(bash)
    sunlight("darius", bash)
    a("skill")
    a("idle", 120, loop=True)
    # sword strikes (hit on tick 8, one every 80 ticks) until the Eclipse bursts round her
    while t + tick(80) < burst:
        start = t
        fx_at("league_leona_fx", "hit", start + tick(8), d.x, d.y)
        d.flinches.append(start + tick(8))
        a("attack")
        a("idle", tick(80) - tick(24), loop=True)
    a("idle", max(0.0, burst - t), loop=True)
    over.append(Follow(frames_of(fx["league_leona_big"], "w_burst"), burst, x, gy, on=body))
    d.flinches.append(burst)
    sunlight("darius", burst)
    a("idle", 300, loop=True)
    # Garen walks in (1.6 px a tick); the Solar Flare at him, 80 px off: cast on tick 12, the beam
    # lands 37 ticks later - slowed, marked, stunned 1.75 s in the centre
    walk0 = burst - 1500
    cast = t
    flare = cast + tick(12)
    land = flare + tick(37)
    gx = x + 78                                       # where he is when the flare falls
    g.walks.append((walk0, land, gx - g.x))
    fx_at("league_leona_big", "r_flare", flare, gx, g.y, until=flare + tick(59), loop=False)
    fx_at("league_leona_fx", "r_stun", land, gx, g.y)
    g.holds.append((land, land + tick(105)))
    g.flinches.append(land)
    sunlight("garen", land)
    a("ult")
    a("idle", 1300, loop=True)
    end = t
    for name, hits in marks.items():
        foe = foes[name]
        hits.sort()
        for i, h in enumerate(hits):
            stop = h + tick(90)
            if i + 1 < len(hits):
                stop = min(stop, hits[i + 1])
            fx_at("league_leona_fx", "sunlight", h, *foe.pos(h), until=stop, loop=True)

    def place(img, f, px, py):
        img.alpha_composite(f, (px - f.width // 2, py - f.height // 2))

    frames, tt = [], 0.0
    order = sorted(foes.values(), key=lambda f: f.y)   # the one further back first
    while tt < end:
        img = Image.new("RGBA", (W, H), ARENA)
        for an in under:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        for foe in order:
            place(img, foe.frame(tt), *foe.pos(tt))
        for an in body:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
                break
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
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_leona_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_leona_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_leona_showcase.gif")))


if __name__ == "__main__":
    main()
