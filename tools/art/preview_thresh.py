#!/usr/bin/env python3
"""Preview images for Thresh, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_thresh.py [--out docs/preview]

  league_thresh_frames.png    every animation, frame by frame, 3x on the arena colour
  league_thresh_effects.png   every effect animation, 3x
  league_thresh_showcase.gif  a scripted fight against Darius and Garen with Ashe behind him, timed like the kit:
                              Thresh walks in past Ashe and Darius runs right up to him: Flay pushes him away,
                              and an empowered lash (no attack for 2 s) follows. Garen walks up; Death
                              Sentence's hook flies at him, its chain growing out of Thresh's hand, and the
                              lantern flies to Ashe (Dark Passage: a shield on both). The hook catches Garen: the
                              chains bind him, he is stunned and dragged in while the chain shortens. The Box
                              rises round Thresh: Garen, the first champion in it, is hit and shackled (99% slow,
                              2 s), Darius only slowed for 1 s. Garen backs off toward the walls; the next Flay,
                              with nobody right on Thresh, pulls both back in and Darius falls; an empowered lash
                              hits Garen and the walls shatter after 5 s; 3x. Projectile pictures are turned to
                              their direction like the game does (the lantern flies left to Ashe, the hook comes
                              back leftward).
"""
import argparse
import math
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from preview_annie import Held, OnFoe  # noqa: E402
from preview_ashe import Anim, tick  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_jinx import Follow  # noqa: E402
from preview_yone import OnFoeFor, Path  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_thresh")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_thresh_fx", "league_thresh_big")}


def turned(fr, dx, dy):
    """A projectile's frames turned to its direction, as the game draws them."""
    deg = math.degrees(math.atan2(dy, dx))
    if abs(deg) < 0.5:
        return fr
    return [(f.rotate(-deg, resample=Image.NEAREST, expand=True), ms) for f, ms in fr]


class Drawings:
    """A tag cut down to some of its frames: the Box's 46 frames are its ten drawings, the standing four ten times."""

    def __init__(self, sp, tag, keep):
        idx = sp.tag_frames(tag)
        self.frames, self.durations, self.h = sp.frames, sp.durations, sp.h
        self.keep = [idx[k] for k in keep]

    def tag_frames(self, tag):
        return self.keep


class Backing(Held):
    """Garen: also backs off (walks away to the right, his run frames facing right)."""

    def __init__(self, sp, x, y):
        super().__init__(sp, x, y)
        self.backs = []

    def pos(self, t):
        x, y = super().pos(t)
        for t0, t1, dx in self.backs:
            if t >= t0:
                x += int(round(dx * min(1.0, (t - t0) / (t1 - t0))))
        return x, y

    def frame(self, t):
        for t0, t1, _ in self.backs:
            if t0 <= t < t1:
                return self.pick(self.run, (t - t0) % sum(ms for _, ms in self.run))
        return super().frame(t)


def showcase(out, z=3, step=40):
    th = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_thresh_fx"], fx["league_thresh_big"]
    W, H = 270, 150
    gy = 100                                          # the pivot row
    ashe = frames_of(load(os.path.join(LEAGUE, "champions", "league_ashe")), "idle")
    ax, ay = 78, gy - 16                              # Ashe, 44 px behind him (Dark Passage reaches 50000)
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), 200, gy + 10)
    g = Backing(load(os.path.join(LEAGUE, "champions", "league_garen")), 262, gy - 8)
    d.walks.append((400.0, 1400.0, -64))              # Darius runs up to 136, right on him
    g.walks.append((1600.0, 3000.0, -76))             # Garen walks up to 186
    body, under, over = [], [], []
    t = 0.0
    x = 30

    def a(tag, dur=None, loop=False, way=None):
        nonlocal t
        an = Path(frames_of(th, tag), t, x, gy, loop=loop, until=(t + dur) if dur else None, way=way or ())
        body.append(an)
        t = an.until

    def fly(tag, t0, x0, y0, x1, y1, speed, loop=True):
        """A projectile from (x0, y0) to (x1, y1) at `speed` px a tick; returns its arrival."""
        t1 = t0 + tick(math.hypot(x1 - x0, y1 - y0) / speed)
        over.append(Anim(turned(frames_of(small, tag), x1 - x0, y1 - y0), t0, x0, y0, loop=loop, until=t1,
                         x1=x1, y1=y1, z=1))
        return t1

    def hit(foe, when, tag="hit", z=1):
        over.append(OnFoe(frames_of(small, tag), when, foe, z=z))
        foe.flinches.append(when)

    def lash(tag, view, foe, start):
        fx0, fy0 = foe.pos(start + tick(14))
        arrive = fly(tag, start + tick(14), x, gy - 2, fx0 - 6, fy0 - 2, 6)
        hit(foe, arrive, view)

    def flay(push, foes):
        """Flay: the sweep from tick 8, the hit 5 ticks later (2.5 px a tick for 12 ticks) and a 1 s slow."""
        start = t
        over.append(Follow(frames_of(big, "e_sweep"), start + tick(8), x, gy, on=body, z=1))
        swept = start + tick(13)
        for foe, dx in foes:
            hit(foe, swept, "e_hit")
            foe.slides.append((swept, swept + tick(12), dx if push else -dx))
        a("skill2", tick(30))
        return swept

    # he walks in past Ashe (60 px a second); Darius runs right up to him
    a("run", 1500, loop=True, way=[(0, 30), (1500, 120)])
    x = 120
    # Flay with a champion right on him: pushed away (30 px)
    flay(True, [(d, 30)])
    a("idle", 50, loop=True)
    # an empowered lash (no attack for 2 s) at tick 14; Darius walks back in, 34 px off
    lash("lash_flay", "flay_hit", d, t)
    d.walks.append((2600.0, 3400.0, -14))
    a("attack", tick(30))
    a("idle", 3100 - t, loop=True)
    # Death Sentence at Garen (tick 16): the hook at 5.5 px a tick, its chain growing; the lantern to Ashe at 5
    start = t
    go = start + tick(16)
    gx, gyy = g.pos(go)
    dist = math.hypot(gx - x, gyy - gy)
    reach = dist - 10                                 # the hook's circle meets his body 10 px short of his middle
    hx, hy = x + (gx - x) * reach / dist, gy - 2 + (gyy - gy) * reach / dist
    caught = fly("q_hook", go, x, gy - 2, hx, hy, 5.5, loop=False)
    landed = fly("w_lantern", go, x, gy - 2, ax, ay - 2, 5)
    over.append(Follow(frames_of(small, "w_shield"), go, x, gy, loop=True, until=go + tick(150), on=body, z=1))
    over.append(Anim(frames_of(small, "w_shield"), landed, ax, ay, loop=True, until=landed + tick(150), z=1))
    # caught: bound in chains, stunned 1 s and dragged at 1.5 px a tick to 20 px from him; the hook comes back
    over.append(OnFoe(frames_of(small, "q_hit"), caught, g, z=2))
    g.holds.append((caught, caught + 1000))
    pull = gx - (x + 22)
    g.slides.append((caught, caught + tick(pull / 1.5), -pull))
    fly("q_return", caught, hx, hy, x, gy - 2, 1.5, loop=False)
    a("skill", tick(40))
    a("idle", 4200 - t, loop=True)
    # The Box at tick 17 (a caster view where he stands, 5 s): Garen first (hit, 99% slow for 2 s), Darius half (1 s)
    start = t
    box = start + tick(17)
    under.append(Anim(frames_of(big, "r_box"), box, x, gy, z=-1))
    for foe, slow in ((g, 120), (d, 60)):
        over.append(OnFoe(frames_of(small, "r_hit"), box, foe, z=2))
        over.append(OnFoeFor(frames_of(small, "r_slow"), box, foe, box + tick(slow), z=1))
        foe.holds.append((box, box + tick(slow)))
    a("ult", tick(40))
    # Garen, free again, backs off toward the walls; Flay with nobody right on him pulls both back in (and Darius
    # through), and Darius falls; an empowered lash catches Garen; the walls shatter
    g.backs.append((box + tick(120) + 100, box + tick(120) + 800, 22))
    a("idle", 1500 + 6000 - t, loop=True)
    swept = flay(False, [(g, 30), (d, 26)])
    d.death = swept + 300
    a("idle", 300, loop=True)
    lash("lash_flay", "flay_hit", g, t)
    a("attack", tick(30))
    a("idle", box + 5000 + 300 - t, loop=True)
    end = t

    def place(img, f, px, py):
        img.alpha_composite(f, (int(px) - f.width // 2, int(py) - f.height // 2))

    frames, tt = [], 0.0
    ashe_total = sum(ms for _, ms in ashe)
    while tt < end:
        img = Image.new("RGBA", (W, H), ARENA)
        for an in under:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        units = [(ay, Held.pick(ashe, tt % ashe_total), (ax, ay)), (g.pos(tt)[1], g.frame(tt), g.pos(tt)),
                 (d.pos(tt)[1], d.frame(tt), d.pos(tt))]
        for an in body:
            f = an.frame(tt)
            if f is not None:
                units.append((gy, f, an.pos(tt)))
                break
        for _, f, p in sorted(units, key=lambda u: u[0]):
            if f is not None:
                place(img, f, *p)
        for an in sorted(over, key=lambda o: o.z):
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
    q[0].save(T.long_path(out), save_all=True, append_images=q[1:], duration=step, loop=0, optimize=False)
    return len(frames), round(end / 1000.0, 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    s = load(CHAMP)
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_thresh_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        for t in sp.tags:
            if t["name"] == "r_box":
                rows.append((Drawings(sp, "r_box", [0, 1, 2, 3, 4, 5, 6, 43, 44, 45]), "r_box", "big:r_box 5s"))
            else:
                rows.append((sp, t["name"], f"{name[14:]}:{t['name']}"))
    print("effects", contact(rows, os.path.join(args.out, "league_thresh_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_thresh_showcase.gif")))


if __name__ == "__main__":
    main()
