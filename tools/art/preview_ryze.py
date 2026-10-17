#!/usr/bin/env python3
"""Preview images for Ryze, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_ryze.py [--out docs/preview]

  league_ryze_frames.png    every animation, frame by frame, 3x on the arena colour
  league_ryze_effects.png   every effect animation, 3x
  league_ryze_showcase.gif  a scripted fight with Lucian beside him against Darius and Garen, timed like the kit:
                            Ryze walks in and throws a rune orb at Darius; Overload's bolt hits him; the combo: Spell
                            Flux's violet orb bursts on Darius and marks him and Garen (violet runes circling their
                            chests), Rune Prison roots the Flux'd Darius in a cage of blue bars, the reset Overload
                            bursts the Flux on both (a lightning strike and a violet blast each), the two runes he
                            charged (circling his waist) burst out and hasten him, a second Spell Flux and Overload
                            burst it again (E-W-Q-E-Q); Darius and Garen back off, and once
                            Darius has left his reach Realm Warp chases him: a portal under Ryze and Lucian and one
                            where the line toward Darius touches him, he and Lucian blink through (a column where they
                            stood, the arrival round him, a flash on Lucian) and his landing Spell Flux marks Darius
                            again; 3x
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
CHAMP = os.path.join(LEAGUE, "champions", "league_ryze")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_ryze_fx", "league_ryze_big")}


class Ally:
    """A unit facing right on its idle loop; `moves` = [(t0, t1, x1, y1)] slides it (Realm Warp's pull)."""

    def __init__(self, sprite, x, y):
        self.fr = frames_of(sprite, "idle") if sprite is not None else [(None, 1)]
        self.x, self.y = x, y
        self.total = sum(ms for _, ms in self.fr)
        self.moves = []

    def pos(self, t):
        x, y = self.x, self.y
        for t0, t1, x1, y1 in self.moves:
            if t >= t1:
                x, y = x1, y1
            elif t > t0:
                u = (t - t0) / (t1 - t0)
                return int(round(x + (x1 - x) * u)), int(round(y + (y1 - y) * u))
        return x, y

    def frame(self, t):
        dt = t % self.total
        for f, ms in self.fr:
            if dt < ms:
                return f
            dt -= ms
        return self.fr[-1][0]


def showcase(out, z=3, step=40):
    ryze = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_ryze_fx"], fx["league_ryze_big"]
    W, H = 300, 150
    gy = 100                                          # the pivot row: R's column rises 54 px over it
    x0 = 72
    reach_stop = 46                                   # R lands r_stop (38000: in his reach) + Darius's body short of him
    lucian = Ally(load(os.path.join(LEAGUE, "champions", "league_lucian")), x0 - 24, gy - 8)   # in the 30 px portal
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 54, gy + 8)      # 55 px: attack range
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), 286, gy - 14)         # walking in
    body, under, over = [], [], []
    t = 0.0
    me = Ally(None, x0, gy)                           # his pivot, for the views that follow him
    x = x0

    def a(tag, dur=None, loop=False, to=None, at=None):
        nonlocal t
        px, py = at if at else (x, gy)
        an = Anim(frames_of(ryze, tag), t, px, py, loop=loop, until=(t + dur) if dur else None, x1=to)
        body.append(an)
        t = an.until

    def on(unit, sp, tag, at, until=None, ground=False):
        an = OnFoe(frames_of(sp, tag), at, unit, z=-1 if ground else 1)
        if until is not None:
            an.loop, an.until = True, until
        (under if ground else over).append(an)
        return an

    def at(sp, tag, when, px, py, ground=False):
        an = Anim(frames_of(sp, tag), when, px, py, z=-1 if ground else 1)
        (under if ground else over).append(an)
        return an

    def shot(tag, launch, foe, speed, hit=None, y0=2, at=None):
        """A shot from his pivot (y0 px up) to the foe's pivot at `speed` px a tick; returns its arrival."""
        px, py = at if at else (x, gy)
        tx, ty = foe.pos(launch)
        arrive = launch + tick(max(1.0, ((tx - px) ** 2 + (ty - py) ** 2) ** 0.5 / speed))
        over.append(Anim(frames_of(small, tag), launch, px, py - y0, loop=True, until=arrive, x1=tx, y1=ty - y0))
        if hit:
            on(foe, small, hit, arrive)
        foe.flinches.append(arrive)
        return arrive

    def flux(start, end, foes=None):
        """Flux on Darius and Garen (both inside the 25 px zone round Darius): the mark replayed every 12 ticks."""
        for foe in foes or (d, g):
            k = start
            while k < end:
                on(foe, small, "flux", k)
                k += tick(12)

    # he walks in; Garen walks up behind Darius
    run_in = Anim(frames_of(ryze, "run"), 0.0, x - 40, gy, loop=True, until=1000, x1=x)
    body.append(run_in)
    t = run_in.until
    g.walks.append((300.0, 2400.0, (x + 78) - g.x))  # 24 px behind Darius: inside Flux's 25 px spread
    a("idle", 300, loop=True)
    # the attack: the orb leaves on tick 9 at 4.5 px a tick
    shot("orb", t + tick(9), d, 4.5, "hit")
    a("attack")
    a("idle", tick(90) - tick(28), loop=True)
    # Overload alone: on tick 7 the flash at his palm and the bolt (6 px a tick, stops on the first enemy)
    start = t + tick(7)
    on(me, small, "q_cast", start)
    shot("q_bolt", start, d, 6.0, "q_hit")
    a("skill")
    a("idle", 600, loop=True)
    # the combo E -> W -> Q -> E -> Q (2026-10-05): E on tick 6, W on 16, Q on 26, E again on 36, Q again on 46
    c0 = t
    on(me, small, "e_cast", c0 + tick(6))
    land = shot("e_orb", c0 + tick(6), d, 4.5, "e_hit")
    marked = land + tick(3)                           # the lob (1 tick) and the zone's 2-tick delay
    on(me, small, "rune1", c0 + tick(6), until=c0 + tick(16))
    on(d, small, "w_root", c0 + tick(16))             # Flux is up: rooted 75 ticks in the cage
    d.holds.append((c0 + tick(16), c0 + tick(16 + 75)))
    on(me, small, "rune2", c0 + tick(16), until=c0 + tick(26))
    q = c0 + tick(26)
    on(me, small, "q_cast", q)
    on(me, small, "rune_out", q)
    on(me, small, "q_haste", q, until=q + tick(120), ground=True)
    hit = shot("q_bolt", q, d, 6.0, "q_hit")
    flux(marked, hit)
    for foe in (d, g):                                # the burst on every Flux'd enemy
        on(foe, small, "q_pop", hit)
        foe.flinches.append(hit)
    # the second Spell Flux marks them again, the second Overload bursts it
    on(me, small, "e_cast", c0 + tick(36))
    on(me, small, "rune1", c0 + tick(36), until=c0 + tick(46))
    land2 = shot("e_orb", c0 + tick(36), d, 4.5, "e_hit")
    q2 = c0 + tick(46)
    on(me, small, "q_cast", q2)
    on(me, small, "rune_out", q2)
    hit2 = shot("q_bolt", q2, d, 6.0, "q_hit")
    flux(land2 + tick(3), hit2)
    for foe in (d, g):
        on(foe, small, "q_pop", hit2)
        foe.flinches.append(hit2)
    a("skill2")
    a("idle", 900, loop=True)
    # Realm Warp, the chase: out of the cage Darius runs off, Garen with him; once Darius has left Ryze's reach (60 px
    # with the bodies) the next check (every 10 ticks) opens the portals - his own, and one where the line toward
    # Darius touches him - and after the 60-tick channel he blinks there, Lucian (in his portal) is pulled through
    # (15 px a tick) and the landing Spell Flux leaves 3 ticks later
    flee, flee_t, flee_px = t, tick(66), 64
    for foe, px in ((d, flee_px), (g, flee_px + 6)):
        foe.runs.append((flee, flee + flee_t))
        foe.slides.append((flee, flee + flee_t, px))
    r0 = flee + tick(6 + 10)
    dx_, dy_ = d.pos(r0)
    span = ((dx_ - x) ** 2 + (dy_ - gy) ** 2) ** 0.5
    u = (span - reach_stop) / span                    # the line stops r_stop + his body short of him
    dest = (int(round(x + (dx_ - x) * u)), int(round(gy + (dy_ - gy) * u)))
    a("idle", r0 - t, loop=True)
    at(big, "r_portal", r0, x, gy, ground=True)
    at(big, "r_dest", r0, *dest, ground=True)
    a("ult", tick(61), loop=True)
    jump = t
    at(big, "r_out", jump, x, gy)
    x, y = dest
    me.moves.append((jump - 1, jump, x, y))
    on(me, big, "r_in", jump)
    lx, ly = lucian.pos(jump)
    pull = jump + tick(max(1.0, (abs(x - 24 - lx) + abs(y - 8 - ly)) / 15.0))
    lucian.moves.append((jump, pull, x - 24, y - 8))
    on(lucian, small, "r_ally", jump)
    e = jump + tick(3)
    land = shot("e_orb", e, d, 4.5, "e_hit", at=(x, y))
    near = [f for f in (d, g) if abs(f.pos(land)[0] - d.pos(land)[0]) <= 25]
    flux(land + tick(3), land + tick(3 + 96), near)
    a("ult_land", at=(x, y))
    a("idle", 1700, loop=True, at=(x, y))
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
                 (lucian.pos(tt)[1], lucian.frame(tt), lucian.pos(tt))]
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
    sample = frames[::6]                              # one palette for the whole clip
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
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    s = load(CHAMP)
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_ryze_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[12:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_ryze_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_ryze_showcase.gif")))


if __name__ == "__main__":
    main()
