#!/usr/bin/env python3
"""Preview images for Fiddlesticks, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_fiddlesticks.py [--out docs/preview]

  league_fiddlesticks_frames.png    every animation, frame by frame, 3x on the arena colour
  league_fiddlesticks_effects.png   every effect animation, 3x (the fear eye's and the stitched mouth's drawings
                                    once; the game plays them two and three times)
  league_fiddlesticks_showcase.gif  a scripted fight against Darius and Garen, timed like the kit: Fiddlesticks
                                    walks in and his first bolt after standing still frightens Darius (1 s), who
                                    runs off. Terrify's crow flies at Garen: the ghost screams out of him and he
                                    flees for 1.25 s. Both come back; Fiddlesticks steps up and Reap slashes
                                    through them (Darius, in its middle, silenced), then Bountiful Harvest pulls
                                    their souls for 2 s along soul chains (a link from each of them back to him
                                    every 0.25 s), the harvest ripping them out at the end. They back off;
                                    Crowstorm marks the ground between them for 1 s, he bursts into crows and lands
                                    there, both flee in fear from the storm, and Darius falls in it; 3x.
                                    Projectile pictures are turned to their direction like the game does.
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
CHAMP = os.path.join(LEAGUE, "champions", "league_fiddlesticks")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_fiddlesticks_fx", "league_fiddlesticks_big")}


def turned(fr, dx, dy):
    """A projectile's frames turned to its direction, as the game draws them."""
    deg = math.degrees(math.atan2(dy, dx))
    if abs(deg) < 0.5:
        return fr
    return [(f.rotate(-deg, resample=Image.NEAREST, expand=True), ms) for f, ms in fr]


class Drawings:
    """A tag cut down to some of its frames: the fear eye's twelve frames are its six drawings twice."""

    def __init__(self, sp, tag, keep):
        idx = sp.tag_frames(tag)
        self.frames, self.durations, self.h = sp.frames, sp.durations, sp.h
        self.keep = [idx[k] for k in keep]

    def tag_frames(self, tag):
        return self.keep


class Fleeing(Held):
    """A foe that also runs away (its run frames facing the way it goes) by dx px between t0 and t1."""

    def __init__(self, sp, x, y):
        super().__init__(sp, x, y)
        self.flees = []

    def pos(self, t):
        x, y = super().pos(t)
        for t0, t1, dx in self.flees:
            if t >= t0:
                x += int(round(dx * min(1.0, (t - t0) / (t1 - t0))))
        return x, y

    def frame(self, t):
        if self.death is None or t < self.death:
            for t0, t1, dx in self.flees:
                if t0 <= t < t1:
                    f = self.pick(self.run, (t - t0) % sum(ms for _, ms in self.run))
                    return f if dx > 0 else self.flip(f)
        return super().frame(t)


def showcase(out, z=3, step=40):
    fd = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_fiddlesticks_fx"], fx["league_fiddlesticks_big"]
    W, H = 320, 150
    gy = 96                                           # his pivot row
    d = Fleeing(load(os.path.join(LEAGUE, "champions", "league_darius")), 190, gy + 10)
    g = Fleeing(load(os.path.join(LEAGUE, "champions", "league_garen")), 240, gy - 12)
    body, under, over = [], [], []
    t = 0.0
    x, y = 20, gy

    def a(tag, dur=None, loop=False, way=None):
        nonlocal t
        an = Path(frames_of(fd, tag), t, x, y, loop=loop, until=(t + dur) if dur else None, way=way or ())
        body.append(an)
        t = an.until

    def fly(tag, t0, x0, y0, x1, y1, speed):
        """A projectile from (x0, y0) to (x1, y1) at `speed` px a tick; returns its arrival."""
        t1 = t0 + tick(math.hypot(x1 - x0, y1 - y0) / speed)
        over.append(Anim(turned(frames_of(small, tag), x1 - x0, y1 - y0), t0, x0, y0, loop=True, until=t1,
                         x1=x1, y1=y1, z=1))
        return t1

    def chain(t0, foe):
        """W's soul chain: one link from the foe back to him at 1.6 px a tick, over the units (the game's z 1)."""
        fx0, fy0 = foe.pos(t0)
        x0, y0, x1, y1 = fx0, fy0 - 5, x, y - 5
        t1 = t0 + tick(math.hypot(x1 - x0, y1 - y0) / 1.6)
        over.append(Anim(turned(frames_of(small, "w_chain"), x1 - x0, y1 - y0), t0, x0, y0, loop=True, until=t1,
                          x1=x1, y1=y1, z=1))

    def bolt(foe, start):
        """An attack: the bolt leaves at tick 8 (5 px a tick) and hits; returns the hit's time."""
        fx0, fy0 = foe.pos(start + tick(8))
        arrive = fly("bolt", start + tick(8), x + 6, y - 4, fx0 - 6, fy0 - 4, 5)
        over.append(OnFoe(frames_of(small, "hit"), arrive, foe, z=1))
        foe.flinches.append(arrive)
        return arrive

    def fear(foe, when, ticks, dx):
        """Frightened: the eye over the head (1.2 s) and a run away from him for the fear's length."""
        over.append(OnFoe(frames_of(small, "fear"), when, foe, z=2))
        foe.flees.append((when, when + tick(ticks), dx))

    # he walks in (1 px a tick)
    a("run", 1260, loop=True, way=[(0, 20), (1260, 96)])
    x = 96
    a("idle", 40, loop=True)
    # A Harmless Scarecrow: the first bolt after 3 s without acting frightens Darius for 1 s
    hit = bolt(d, t)
    fear(d, hit, 60, 30)
    d.walks.append((hit + tick(60), hit + tick(60) + 900, -46))           # back to 174
    a("attack", tick(26))
    a("idle", 1900 - t, loop=True)
    # Terrify at Garen: the crow leaves at tick 13 (9 px a tick), the ghost screams out of him, fear 1.25 s a tick later
    start = t
    gx, gyy = g.pos(start + tick(13))
    caught = fly("q_crow", start + tick(13), x + 6, y - 4, gx - 6, gyy - 4, 9)
    over.append(OnFoe(frames_of(small, "q_hit"), caught, g, z=2))
    g.flinches.append(caught)
    fear(g, caught + tick(1), 75, 24)
    g.walks.append((caught + tick(76), caught + tick(76) + 1300, -78))    # back to 186
    a("skill", tick(32))
    a("idle", 2600 - t, loop=True)
    # he steps up to 150 and bolts Darius again
    a("run", 900, loop=True, way=[(t, 96), (t + 900, 150)])
    x = 150
    a("idle", 3700 - t, loop=True)
    bolt(d, t)
    a("attack", tick(26))
    a("idle", 4400 - t, loop=True)
    # Reap on Garen from tick 13, the hit 5 ticks later: Garen in its middle is silenced, Darius 25 px off only
    # hurt and slowed; Bountiful Harvest from tick 25: a pulse every 15 ticks for 2 s on everyone within 40 px
    # (Darius 26, Garen 38), the eighth one the harvest
    start = t
    reap = start + tick(13)
    px, py = g.pos(reap)
    over.append(Anim(frames_of(big, "e_reap"), reap, px, py, until=reap + tick(23), z=1))
    slashed = reap + tick(5)
    for foe in (d, g):
        foe.flinches.append(slashed)
    over.append(OnFoe(frames_of(small, "silence"), slashed, g, z=2))
    a("skill2", tick(25))
    for k in range(8):
        pulse = start + tick(25 + 15 * k)
        over.append(Follow(frames_of(big, "w_souls"), pulse, x, y, on=body, z=1))
        for foe in (d, g):
            over.append(OnFoe(frames_of(small, "w_drain" if k < 7 else "w_final"), pulse, foe, z=1))
            chain(pulse + tick(1), foe)                   # the soul chain leaves the foe a tick later
    for foe in (d, g):
        foe.flinches.append(start + tick(25 + 15 * 7))
    a("w_loop", tick(122))
    # they back off
    d.flees.append((t + 150, t + 850, 30))                                # to 204
    g.flees.append((t + 250, t + 1150, 40))                               # to 226
    a("idle", 7900 - t, loop=True)
    # Crowstorm on Garen (77 px off, range 80): 1 s channel (the mark on the ground there), then he bursts into
    # crows, lands on the spot and the storm turns round him for 5 s (a pulse every 30 ticks, radius 45); its
    # first pulse frightens both for 1 s, Darius falls in the fifth
    start = t
    lx, ly = g.pos(start)
    under.append(Anim(frames_of(big, "r_mark"), start + tick(1), lx, ly, z=-1))
    a("ult", tick(61))
    landed = t
    over.append(Anim(frames_of(big, "r_depart"), landed, x, y, z=1))
    x, y = lx, ly
    a("ult_land", tick(30))
    for k in range(10):
        over.append(Follow(frames_of(big, "r_storm"), landed + tick(30 * k), x, y, on=body, z=1))
    fear(d, landed, 60, -30)
    fear(g, landed, 60, 30)
    d.flinches.append(landed + tick(90))
    d.death = landed + tick(120)
    g.walks.append((landed + tick(60) + 300, landed + tick(60) + 1000, -12))
    a("idle", landed + tick(300) + 400 - t, loop=True)
    end = t

    def place(img, f, px, py):
        img.alpha_composite(f, (int(px) - f.width // 2, int(py) - f.height // 2))

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
        for an in sorted(over, key=lambda o: o.z):
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        frames.append(img.resize((W * z, H * z), Image.NEAREST).convert("RGB"))
        tt += step
    sample = frames[::4]                              # one palette for the whole clip
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
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags],
                            os.path.join(args.out, "league_fiddlesticks_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        for t in sp.tags:
            if t["name"] in ("fear", "silence"):
                n = 6 if t["name"] == "fear" else 4
                rows.append((Drawings(sp, t["name"], range(n)), t["name"], f"{name[20:]}:{t['name']} x{12 // n}"))
            else:
                rows.append((sp, t["name"], f"{name[20:]}:{t['name']}"))
    print("effects", contact(rows, os.path.join(args.out, "league_fiddlesticks_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_fiddlesticks_showcase.gif")))


if __name__ == "__main__":
    main()
