#!/usr/bin/env python3
"""Preview images for Teemo, built from the exported game sprites (so they also prove the sheets
load).

    python tools/art/preview_teemo.py [--out docs/preview]

  league_teemo_frames.png    every animation, frame by frame, 3x on the arena colour
  league_teemo_effects.png   every effect animation, 3x
  league_teemo_showcase.gif  a scripted fight against Darius and Garen, timed like the kit: Teemo runs in,
                             the Blinding Dart splashes on Darius and wraps his eyes in smoke, Toxic Shot darts poison
                             him, Move Quick kicks up dust and a whirl of leaves as Darius closes in and
                             Teemo fades into Camouflage (his darts come faster), a Noxious Trap is thrown
                             onto Garen's way in - it lands, arms, hides in the grass and bursts into a
                             toxic cloud when he steps on it (poisoned, slowed) - and Darius falls to the
                             poison; 3x
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from preview_ashe import Anim, tick  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_jinx import Arc, Walker  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_teemo")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_teemo_fx", "league_teemo_big")}


def faded(f, alpha=0.45):
    """A frame drawn see-through (Camouflage)."""
    a = np.asarray(f).copy()
    a[..., 3] = (a[..., 3] * alpha).astype(np.uint8)
    return Image.fromarray(a, "RGBA")


def showcase(out, z=3, step=40):
    teemo = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    W, H = 300, 130
    gy = 92                                           # Teemo's pivot row
    x = 44
    d = Walker(load(os.path.join(LEAGUE, "champions", "league_darius")), 100, gy)       # 56 px: in dart range
    g = Walker(load(os.path.join(LEAGUE, "champions", "league_garen")), 286, gy - 8)    # far off, walking in
    body, under, over, hidden = [], [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        an = Anim(frames_of(teemo, tag), t, x, gy, loop=loop, until=(t + dur) if dur else None)
        body.append(an)
        t = an.until

    def fx_at(sprite, tag, at, px, py=gy, ground=False, until=None, x1=None, y1=None, loop=None):
        an = Anim(frames_of(fx[sprite], tag), at, px, py, z=-1 if ground else 1,
                  loop=(until is not None) if loop is None else loop, until=until, x1=x1, y1=y1)
        (under if ground else over).append(an)
        return an

    def dart(start, fire=12, speed=6.0, tag="dart", hit="hit"):
        """A dart leaves the blowgun `fire` ticks into the action and flies to Darius."""
        launch = start + tick(fire)
        x0, y0 = x + 12, gy - 12                    # the blowgun at his mouth
        dx, dy = d.pos(launch)
        tx, ty = dx - 6, dy - 4
        arrive = launch + tick(max(1.0, (tx - x0) / speed))
        fx_at("league_teemo_fx", "q_dart" if tag == "q_dart" else "dart", launch, x0, y0, until=arrive, x1=tx, y1=ty)
        fx_at("league_teemo_fx", hit, arrive, *d.pos(arrive))
        d.flinches.append(arrive)
        return arrive

    # he runs in (the run's head on his shoulders, the feet on the ground)
    run_in = Anim(frames_of(teemo, "run"), 0.0, x - 34, gy, loop=True, until=632 * 1.5, x1=x)
    body.append(run_in)
    t = run_in.until
    a("idle", 300, loop=True)
    # Blinding Dart: fired on tick 12 at 5.5 px a tick; the splash on his head and 1.5 s of smoke over his eyes
    start = t
    hit = dart(start, speed=5.5, tag="q_dart", hit="q_hit")
    fx_at("league_teemo_fx", "blind", hit, *d.pos(hit))
    a("skill")
    a("idle", 120, loop=True)
    # Toxic Shot: a dart a second (the attack's cooldown, 60 ticks), fired on tick 12
    for _ in range(2):
        start = t
        dart(start)
        a("attack")
        a("idle", tick(60) - tick(24), loop=True)
    # Darius closes in to 30 px: Move Quick - dust, the whirl of leaves, 1.5 s of Camouflage, 40% faster darts
    d.walks.append((t - 500, t, -26))
    start = t
    over.append(Anim(frames_of(fx["league_teemo_fx"], "w_cast"), start + tick(4), x, gy, z=-1))
    over.append(Anim(frames_of(fx["league_teemo_fx"], "stealth"), start + tick(4), x, gy))
    hidden.append((start + tick(4), start + tick(94)))
    a("skill2")
    a("idle", 60, loop=True)
    for _ in range(3):
        start = t
        dart(start, fire=9)
        a("attack")
        a("idle", tick(43) - tick(24), loop=True)
    # Noxious Trap: Garen walks in; the mushroom is thrown on tick 15 (0.33 s through the air) onto his way,
    # arms for 1 s, waits in the grass, and bursts when he reaches it: poisoned, slowed 40%
    walk0 = t - 1200
    spot = x + 120
    start = t
    throw = start + tick(15)
    land = throw + tick(20)
    armed = land + tick(60)
    over.append(Arc(frames_of(fx["league_teemo_big"], "r_throw"), throw, x + 6, gy - 16, loop=True,
                    until=land, x1=spot, y1=g.y, h=22))
    fx_at("league_teemo_big", "r_arm", land, spot, g.y, ground=True)
    burst = armed + 900
    fx_at("league_teemo_big", "r_trap", armed, spot, g.y, ground=True, until=burst, loop=True)
    g.walks.append((walk0, burst, spot + 8 - g.x))
    fx_at("league_teemo_big", "r_burst", burst, spot, g.y)
    fx_at("league_teemo_fx", "poisoned", burst + 30, *g.pos(burst))
    g.flinches.append(burst)
    g.walks.append((burst + 200, burst + 2400, -30))      # slowed
    a("ult")
    a("idle", 400, loop=True)
    # Darius falls to the poison
    d.death = t + 200
    a("idle", burst + 2600 - t, loop=True)
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
        for foe in (g, d):
            place(img, foe.frame(tt), *foe.pos(tt))
        for an in body:
            f = an.frame(tt)
            if f is not None:
                if any(t0 <= tt < t1 for t0, t1 in hidden):
                    f = faded(f)
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
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_teemo_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_teemo_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_teemo_showcase.gif")))


if __name__ == "__main__":
    main()
