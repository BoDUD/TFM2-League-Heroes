#!/usr/bin/env python3
"""Preview images for Malphite, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_malphite.py [--out docs/preview]

  league_malphite_frames.png    every animation, frame by frame, 3x on the arena colour
  league_malphite_effects.png   every effect animation, 3x
  league_malphite_showcase.gif  a scripted fight against Darius and Garen, timed like the kit: he runs in under
                                Granite Shield (the ring of stone plates); Seismic Shard hits Darius; an attack,
                                and Darius's axe breaks the shield; Ground Slam cracks the ground round him and
                                jolts Darius, and two Thunderclap attacks follow while his fists crackle; Garen
                                walks up behind Darius, and Unstoppable Force charges into them: the crater opens
                                where he lands and both are thrown up for 1.25 s; 3x
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
CHAMP = os.path.join(LEAGUE, "champions", "league_malphite")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_malphite_fx", "league_malphite_big")}


def showcase(out, z=3, step=40):
    mp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    W, H = 300, 136
    gy = 100                                           # his pivot row
    x = 64
    d = Walker(load(os.path.join(LEAGUE, "champions", "league_darius")), 112, gy)        # in melee range
    g = Walker(load(os.path.join(LEAGUE, "champions", "league_garen")), 296, gy - 10)    # walks up behind him
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False, x1=None):
        nonlocal t, x
        an = Anim(frames_of(mp, tag), t, x, gy, loop=loop, until=(t + dur) if dur else None, x1=x1)
        body.append(an)
        t = an.until
        if x1 is not None:
            x = x1

    def fx_at(sprite, tag, at, px, py, ground=False, until=None, x1=None, y1=None, loop=None):
        an = Anim(frames_of(fx[sprite], tag), at, px, py, z=-1 if ground else 1,
                  loop=(until is not None) if loop is None else loop, until=until, x1=x1, y1=y1)
        (under if ground else over).append(an)
        return an

    # he runs in under Granite Shield while Garen starts walking toward them
    shield = Follow(frames_of(fx["league_malphite_fx"], "granite"), 0.0, x, gy, loop=True, until=4200, on=body)
    over.append(shield)
    body.append(Anim(frames_of(mp, "run"), 0.0, x - 44, gy, loop=True, until=1100, x1=x))
    t = 1100.0
    g.walks.append((2600.0, 6600.0, 216 - g.x))
    a("idle", 300, loop=True)
    # Seismic Shard: thrown on tick 12, 5 px a tick, shatters on Darius
    launch = t + tick(12)
    dx_, dy_ = d.pos(launch)
    arrive = launch + tick(max(1.0, (dx_ - 6 - (x + 10)) / 5.0))
    fx_at("league_malphite_fx", "q_shard", launch, x + 10, gy - 14, until=arrive, x1=dx_ - 6, y1=dy_ - 8)
    fx_at("league_malphite_fx", "q_hit", arrive, *d.pos(arrive))
    d.flinches.append(arrive)
    a("skill")
    a("idle", 300, loop=True)
    # an attack (the fist lands on tick 8), then Darius's axe breaks the shield (the ring goes)
    hit = t + tick(8)
    fx_at("league_malphite_fx", "hit", hit, *d.pos(hit))
    d.flinches.append(hit)
    a("attack")
    a("idle", tick(70) - tick(24), loop=True)
    shield.until = t
    # Ground Slam on tick 11: the ring round him, the jolt under Darius; Thunderclap's fists for 4 s
    slam = t + tick(11)
    fx_at("league_malphite_big", "e_slam", slam, x, gy, ground=True)
    fx_at("league_malphite_fx", "e_hit", slam, *d.pos(slam))
    d.flinches.append(slam)
    over.append(Follow(frames_of(fx["league_malphite_fx"], "thunder"), slam, x, gy, loop=True, until=slam + tick(240), on=body))
    a("skill2")
    for _ in range(2):
        a("idle", 160, loop=True)
        hit = t + tick(8)
        fx_at("league_malphite_fx", "w_hit", hit, *d.pos(hit))
        d.flinches.append(hit)
        a("attack")
        a("idle", tick(70) - tick(24) - 160, loop=True)
    # Darius backs off to Garen, who has walked up behind him
    d.walks.append((t, t + 900, 200 - d.x))
    a("idle", 1100, loop=True)
    # Unstoppable Force: the charge starts on tick 4 at 4 px a tick; he lands against Darius, Garen 16 px behind
    start = t
    a("ult", tick(4), loop=True)
    dx_, _ = d.pos(t)
    land_x = dx_ - 24
    travel = tick(max(1.0, (land_x - x) / 4.0))
    a("ult", travel, loop=True, x1=land_x)
    land = t
    impact = land + tick(4)
    fx_at("league_malphite_big", "r_slam", impact, x, gy, ground=True)
    for foe in (d, g):
        fx_at("league_malphite_fx", "r_knockup", impact, *foe.pos(impact))
        foe.hops.append((impact, impact + tick(75), 16))
    a("ult_slam")
    a("idle", 1500, loop=True)
    end = t
    del start

    def place(img, f, px, py):
        img.alpha_composite(f, (px - f.width // 2, py - f.height // 2))

    frames, tt = [], 0.0
    while tt < end:
        img = Image.new("RGBA", (W, H), ARENA)
        for an in under:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        for foe in sorted((d, g), key=lambda f: f.y):
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
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags],
                            os.path.join(args.out, "league_malphite_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[16:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_malphite_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_malphite_showcase.gif")))


if __name__ == "__main__":
    main()
