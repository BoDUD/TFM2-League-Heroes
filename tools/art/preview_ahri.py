#!/usr/bin/env python3
"""Preview images for Ahri, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_ahri.py [--out docs/preview]

  league_ahri_frames.png    every animation, frame by frame, 3x on the arena colour
  league_ahri_effects.png   every effect animation, 3x
  league_ahri_showcase.gif  a scripted fight against Darius and Garen, timed like the kit: Ahri runs in and
                            blows a kiss at Darius (Charm: the hearts over his head, he walks to her); Orb of
                            Deception flies out through him and back (the return's true hit), and Fox-Fire's
                            three fires circle her and seek the charmed Darius; an attack. Three spells have hit,
                            so Essence Theft glows round her waist. Spirit Rush three times: Darius is right on
                            her, so the first dash goes back (the spirit cloud left where she stood), essence
                            bolts hit him and the charged Essence Theft heals her; the second dashes in (bolts
                            on Darius and Garen behind him), the third back out again, and Darius falls. Garen
                            walks up: another kiss charms him, an orb flies through him and back, three attacks; 3x. Projectile pictures are turned to their
                            direction like the game does (the orb comes back leftward).
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
from preview_thresh import turned  # noqa: E402
from preview_yone import OnFoeFor, Path  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_ahri")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_ahri_fx", "league_ahri_big")}


def showcase(out, z=3, step=40):
    ah = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_ahri_fx"], fx["league_ahri_big"]
    W, H = 300, 150
    gy = 100                                          # the pivot row
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), 215, gy + 6)
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), 292, gy - 10)
    d.walks.append((200.0, 1300.0, -35))              # Darius walks up to 180
    g.walks.append((2200.0, 4600.0, -60))             # Garen walks up to 232
    body, under, over = [], [], []
    t = 0.0
    x = 20

    def a(tag, dur=None, loop=False, way=None):
        nonlocal t
        an = Path(frames_of(ah, tag), t, x, gy, loop=loop, until=(t + dur) if dur else None, way=way or ())
        body.append(an)
        t = an.until

    def fly(tag, t0, x0, y0, x1, y1, speed, loop=True):
        """A projectile from (x0, y0) to (x1, y1) at `speed` px a tick; returns its arrival."""
        t1 = t0 + tick(math.hypot(x1 - x0, y1 - y0) / speed)
        over.append(Anim(turned(frames_of(small, tag), x1 - x0, y1 - y0), t0, x0, y0, loop=loop, until=t1,
                         x1=x1, y1=y1, z=1))
        return t1

    def at_foe(foe, when):
        fx0, fy0 = foe.pos(when)
        return fx0 - 4, fy0 - 8

    def hit(foe, when, tag, z=1):
        over.append(OnFoe(frames_of(small, tag), when, foe, z=z))
        foe.flinches.append(when)

    heals = []

    def essence_until(when):
        over.append(OnFoeFor(frames_of(small, "essence"), glow_from, me, when, z=1))

    class Me:                                         # Ahri's place, for the pictures that follow her
        def pos(self, tt):
            for an in body:
                if an.frame(tt) is not None:
                    return an.pos(tt)
            return x, gy
    me = Me()

    # she runs in (1.1 px a tick)
    a("run", 1300, loop=True, way=[(0, 20), (1300, 110)])
    x = 110
    # Charm: the kiss leaves on tick 9 at 4 px a tick; Darius walks to her for 1.25 s
    start = t
    tx, ty = at_foe(d, start + tick(9))
    kissed = fly("e_kiss", start + tick(9), x + 6, gy - 8, tx, ty, 4)
    over.append(OnFoe(frames_of(small, "e_charm"), kissed, d, z=2))
    d.walks.append((kissed, kissed + 1250, -40))
    a("skill2", tick(31))
    # Orb of Deception on tick 10: out 75 px at 4 px a tick through Darius, back at 4.5; Fox-Fire with it
    start = t
    go = start + tick(10)
    far = x + 75
    back_at = fly("q_orb", go, x + 6, gy - 8, far, gy - 8, 4, loop=True)
    dx_hit = d.pos(go + tick(10))[0]
    hit(d, go + tick(max(1, (dx_hit - x - 6) / 4)), "q_hit")
    home = fly("q_orb", back_at, far, gy - 8, x + 6, gy - 8, 4.5, loop=True)
    hit(d, back_at + tick(max(1, (far - d.pos(back_at + tick(8))[0]) / 4.5)), "q_true")
    over.append(Follow(frames_of(small, "w_orbit"), go, x, gy, on=body, z=1))
    for k in range(3):
        f0 = go + tick(8 + 4 * k)
        tx, ty = at_foe(d, f0 + tick(6))
        arrived = fly("w_fire", f0, x, gy - 10, tx, ty, 3.5)
        hit(d, arrived, "w_hit")
    glow_from = back_at                               # the third spell hit: Essence Theft charged
    a("skill", tick(30))
    # an attack (the orb on tick 14)
    start = t
    tx, ty = at_foe(d, start + tick(14))
    arrived = fly("orb", start + tick(14), x + 6, gy - 8, tx, ty, 4.5)
    hit(d, arrived, "hit")
    a("attack", tick(28))
    a("idle", 300, loop=True)
    # Spirit Rush three times: with Darius right on her she dashes back 24 px over 12 ticks from tick 3, else in
    # toward him; the essence bolts leave on tick 19
    for n_dash, (dx, foes) in enumerate([(-24, (d, d, d)), (24, (d, g, d)), (-24, (d, d, g))]):
        start = t
        under.append(Anim(frames_of(big, "r_dash"), start + tick(3), x, gy, z=1))
        a("ult", tick(34), way=[(start, x), (start + tick(3), x), (start + tick(15), x + dx), (start + tick(34), x + dx)])
        x += dx
        for k, foe in enumerate(foes):
            b0 = start + tick(19)
            tx, ty = at_foe(foe, b0 + tick(8))
            arrived = fly("r_bolt", b0, x + 4, gy - 10, tx, ty, 4.5)
            hit(foe, arrived, "r_hit")
            if n_dash == 0 and k == 0:
                essence_until(start)
                heals.append(arrived)
    d.death = t + 200
    for h in heals:
        over.append(Follow(frames_of(small, "heal"), h, x, gy, on=body, z=1))
    a("idle", 600, loop=True)
    # Garen walks up: another kiss charms him, an orb flies through him and back
    start = t
    tx, ty = at_foe(g, start + tick(9))
    kissed = fly("e_kiss", start + tick(9), x + 6, gy - 8, tx, ty, 4)
    over.append(OnFoe(frames_of(small, "e_charm"), kissed, g, z=2))
    g.walks.append((kissed, kissed + 1250, -30))
    a("skill2", tick(31))
    start = t
    go = start + tick(10)
    far = x + 75
    back_at = fly("q_orb", go, x + 6, gy - 8, far, gy - 8, 4, loop=True)
    hit(g, go + tick(max(1, (g.pos(go + tick(12))[0] - x - 6) / 4)), "q_hit")
    fly("q_orb", back_at, far, gy - 8, x + 6, gy - 8, 4.5, loop=True)
    hit(g, back_at + tick(max(1, (far - g.pos(back_at + tick(6))[0]) / 4.5)), "q_true")
    a("skill", tick(30))
    for _ in range(3):                                # three attacks at her 1.5 s attack interval
        start = t
        tx, ty = at_foe(g, start + tick(14))
        arrived = fly("orb", start + tick(14), x + 6, gy - 8, tx, ty, 4.5)
        hit(g, arrived, "hit")
        a("attack", tick(28))
        a("idle", tick(90 - 28), loop=True)
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
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_ahri_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        for t in sp.tags:
            rows.append((sp, t["name"], f"{name[12:]}:{t['name']}"))
    print("effects", contact(rows, os.path.join(args.out, "league_ahri_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_ahri_showcase.gif")))


if __name__ == "__main__":
    main()
