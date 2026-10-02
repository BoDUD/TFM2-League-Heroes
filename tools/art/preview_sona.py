#!/usr/bin/env python3
"""Preview images for Sona, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_sona.py [--out docs/preview]

  league_sona_frames.png    every animation, frame by frame, 3x on the arena colour
  league_sona_effects.png   every effect animation, 3x
  league_sona_showcase.gif  a scripted fight with Lucian beside her against Darius and Garen, timed like the kit:
                            Sona walks in and strums two notes at Darius; Hymn of Valor sends two blue waves at
                            Darius and Garen, its ring round her feet blessing her and Lucian (blue notes); Aria of
                            Perseverance with Song of Celerity heals them both, the green and the pink ring shield
                            and hasten them; three spells ready the Power Chord (golden notes round the etwahl): her
                            next attack strums the gold note, Tempo slows Darius (the pink staff ring at his feet);
                            Crescendo throws the etwahl over her head in a golden burst and the golden wave stuns
                            both (notes circling their heads); 3x
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
CHAMP = os.path.join(LEAGUE, "champions", "league_sona")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_sona_fx", "league_sona_big")}


class Ally:
    """A unit standing still facing right (Lucian): its idle on a loop."""

    def __init__(self, sprite, x, y):
        self.fr = frames_of(sprite, "idle")
        self.x, self.y = x, y
        self.total = sum(ms for _, ms in self.fr)

    def pos(self, t):
        return self.x, self.y

    def frame(self, t):
        dt = t % self.total
        for f, ms in self.fr:
            if dt < ms:
                return f
            dt -= ms
        return self.fr[-1][0]


def showcase(out, z=3, step=40):
    sona = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_sona_fx"], fx["league_sona_big"]
    W, H = 300, 150
    gy = 104                                          # the pivot row: R's burst rises 59 px over it
    x = 80
    lucian = Ally(load(os.path.join(LEAGUE, "champions", "league_lucian")), x - 30, gy - 10)  # inside the 35 px ring
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x + 50, gy + 12)     # 51 px: attack range
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), 284, gy - 16)        # walking in
    body, under, over = [], [], []
    t = 0.0
    me = Ally(sona, x, gy)                            # her pivot, for the views that follow her

    def a(tag, dur=None, loop=False, at=None, to=None):
        nonlocal t
        an = Anim(frames_of(sona, tag), t, at if at is not None else x, gy, loop=loop,
                  until=(t + dur) if dur else None, x1=to)
        body.append(an)
        t = an.until

    def on(unit, sp, tag, at, until=None, ground=False):
        an = OnFoe(frames_of(sp, tag), at, unit, z=-1 if ground else 1)
        if until is not None:
            an.loop, an.until = True, until
        (under if ground else over).append(an)
        return an

    def shot(sp, tag, launch, foe, speed, hit=None, y0=2):
        """A homing shot from her pivot (1.5 px up) to the foe's pivot at `speed` px a tick; returns its arrival."""
        tx, ty = foe.pos(launch)
        arrive = launch + tick(max(1.0, ((tx - x) ** 2 + (ty - gy) ** 2) ** 0.5 / speed))
        over.append(Anim(frames_of(sp, tag), launch, x, gy - y0, loop=True, until=arrive, x1=tx, y1=ty - y0))
        if hit:
            on(foe, small, hit, arrive)
        foe.flinches.append(arrive)
        return arrive

    # she walks in; Garen walks up behind Darius
    run_in = Anim(frames_of(sona, "run"), 0.0, x - 40, gy, loop=True, until=1000, x1=x)
    body.append(run_in)
    t = run_in.until
    g.walks.append((400.0, 2600.0, (x + 56) - g.x))  # 58 px off: inside Hymn of Valor's 65, R's wave 20 px wide
    a("idle", 300, loop=True)
    for _ in range(2):                                # two notes: they leave on tick 6, 90-tick cooldown
        shot(small, "note", t + tick(6), d, 5.0, "hit")
        a("attack")
        a("idle", tick(90) - tick(28), loop=True)
    # Hymn of Valor: on tick 7 a wave at each of the two nearest foes; the blue ring follows her 3 s, blessing every
    # allied champion it touches for 3 s
    start = t + tick(7)
    for foe in (d, g):
        shot(small, "q_note", start, foe, 5.0, "q_hit")
    on(me, big, "q_aura", start, until=start + tick(180), ground=True)
    for u in (me, lucian):
        on(u, small, "q_mel", start, until=start + tick(180))
    a("skill")
    a("idle", 700, loop=True)
    # Aria of Perseverance + Song of Celerity: on tick 8 she and Lucian heal; the green ring shields everyone it
    # touches for 1.5 s, the pink one hastens them for 3 s
    start = t + tick(8)
    for u in (me, lucian):
        on(u, small, "w_heal", start)
        on(u, small, "w_mel", start, until=start + tick(90))
        on(u, small, "e_ally", start, until=start + tick(180), ground=True)
    on(me, big, "w_aura", start, until=start + tick(180), ground=True)
    on(me, big, "e_aura", start, until=start + tick(180), ground=True)
    a("skill2")
    ready = t                                         # the third spell: the Power Chord waits
    a("idle", 900, loop=True)
    # the Power Chord: the next attack strums the gold note on tick 10; the last song was Celerity: Tempo slows
    # Darius for 2 s; the golden notes leave her when it lands
    hit = shot(small, "pc_note", t + tick(10), d, 5.0, "pc_e")
    on(me, small, "pc_glow", ready, until=hit)
    on(d, small, "pc_tempo", hit, until=hit + tick(120), ground=True)
    a("attack_p")
    a("idle", 900, loop=True)
    # Crescendo: on tick 8 the burst over the etwahl she throws up; the golden wave flies 95 px at 5 px a tick and
    # stuns every champion within 20 px of its path for 1.5 s
    start = t + tick(8)
    on(me, big, "r_cast", start)
    over.append(Anim(frames_of(big, "r_wave"), start, x, gy, loop=True, until=start + tick(95 / 5.0), x1=x + 95))
    for foe in (d, g):
        fx_, _ = foe.pos(start)
        hit = start + tick(max(1.0, (fx_ - x) / 5.0))
        foe.holds.append((hit, hit + tick(90)))
        on(foe, small, "r_hit", hit)
    a("ult")
    a("idle", 1700, loop=True)
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
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_sona_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[12:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_sona_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_sona_showcase.gif")))


if __name__ == "__main__":
    main()
