#!/usr/bin/env python3
"""Preview images for Yone, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_yone.py [--out docs/preview]

  league_yone_frames.png    every animation, frame by frame, 3x on the arena colour
  league_yone_effects.png   every effect animation, 3x
  league_yone_showcase.gif  a scripted fight against Darius and Garen, timed like the kit: Yone runs in and
                            thrusts Mortal Steel through Darius, cuts him with the steel katana and then the
                            demon blade (Way of the Hunter), and the second thrust gathers the storm round his
                            waist; the third cast dashes him through Darius behind a gust that throws him up,
                            and Darius falls. Spirit Cleave opens with Soul Unbound: his body stays where he
                            stands, his spirit dashes onto Garen, cleaves him (a shield for the champion hit)
                            and marks him, and cuts him twice more; after 4 s the spirit snaps back to the body
                            and the mark bursts. Fate Sealed's line cuts through Garen and throws him up, Yone
                            stands behind him, and Garen falls; 3x
  league_yone_combos.gif    the combos (tools/kit/yone_combos.py), labelled: Q3 throws Darius up, a thrust on him,
                            the quick R in Q3's window through Darius and Garen (Q3 R), and R's hits fill the storm
                            for Q3 again (R Q3); 3x
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from preview_annie import Held, OnFoe  # noqa: E402
from preview_ashe import Anim, tick  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_jinx import Follow  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_yone")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_yone_fx", "league_yone_big")}


class Path(Anim):
    """A body animation that stands, then moves between waypoints: [(ms, x)], linear in between. An action
    longer than its tag holds the last frame (Fate Sealed: 44 ticks, its tag 650 ms)."""

    def __init__(self, *args, way=(), **kw):
        super().__init__(*args, **kw)
        self.way = list(way)

    def frame(self, t):
        f = super().frame(t)
        if f is None and self.t0 <= t and self.until is not None and t < self.until:
            f = self.fr[-1][0]
        return f

    def pos(self, t):
        if not self.way or t <= self.way[0][0]:
            return (self.way[0][1] if self.way else self.x), self.y
        for (t0, x0), (t1, x1) in zip(self.way, self.way[1:]):
            if t < t1:
                return int(round(x0 + (x1 - x0) * (t - t0) / (t1 - t0))), self.y
        return self.way[-1][1], self.y


class OnFoeFor(Anim):
    """A view on a unit that plays (looping) until a given time: a buff's picture."""

    def __init__(self, fr, t0, foe, until, z=1):
        super().__init__(fr, t0, 0, 0, loop=True, until=until, z=z)
        self.foe = foe

    def pos(self, t):
        return self.foe.pos(t)


def showcase(out, z=3, step=40):
    yone = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_yone_fx"], fx["league_yone_big"]
    W, H = 330, 150
    gy = 104                                          # the pivot row
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), 150, gy)
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), 305, gy)
    g.walks.append((0.0, 2800.0, -90))                # Garen walks up to 215
    body, bodies, under, over = [], [], [], []
    t = 0.0
    x = 110

    def a(tag, dur=None, loop=False, at=None, way=None):
        nonlocal t
        an = Path(frames_of(yone, tag), t, at if at is not None else x, gy, loop=loop,
                  until=(t + dur) if dur else None, way=way or ())
        body.append(an)
        t = an.until

    def fx_at(sp, tag, at, px, py=gy, ground=False, until=None, x1=None, y1=None, loop=None):
        an = Anim(frames_of(sp, tag), at, px, py, z=-1 if ground else 1,
                  loop=(until is not None) if loop is None else loop, until=until, x1=x1, y1=y1)
        (under if ground else over).append(an)
        return an

    def on_yone(tag, t0, until, loop=True):
        an = Follow(frames_of(small, tag), t0, x, gy, loop=loop, until=until, on=body, z=1)
        over.append(an)

    def hit(foe, when, tag="hit", sp=None):
        over.append(OnFoe(frames_of(sp or small, tag), when, foe, z=1))
        foe.flinches.append(when)

    def knock(foe, when, ms):
        foe.hops.append((when, when + ms, 10))
        fx_at(small, "knockup", when, foe.pos(when)[0], gy)

    # he runs in (66 px a second)
    a("run", 1060, loop=True, way=[(0, 40), (1060, x)])
    # Mortal Steel: the thrust's picture on its 45000 rectangle from tick 1, Darius hit on tick 9
    start = t
    fx_at(big, "q_thrust", start + tick(1), x + 22, gy)
    hit(d, start + tick(9), "q_hit")
    a("skill", tick(24))
    a("run", 258, loop=True, way=[(t, x), (t + 258, 127)])
    x = 127
    # Way of the Hunter: the steel katana, then the demon blade (the hit 10 ticks in, an attack every 55)
    for tag, h in (("attack", "hit"), ("attack2", "hit2")):
        start = t
        hit(d, start + tick(10), h)
        a(tag, tick(20))
        a("idle", tick(35), loop=True)
    # the second thrust: the storm gathers round his waist
    start = t
    fx_at(big, "q_thrust", start + tick(1), x + 22, gy)
    hit(d, start + tick(9), "q_hit")
    ready = start + tick(9)
    a("skill", tick(24))
    a("idle", 400, loop=True)
    # the third cast: 8 ticks in, a gust and a 40 px dash at 3 px a tick; Darius thrown up for 1 s, and he falls
    start = t
    on_yone("q_ready", ready, start)
    go = start + tick(9)
    x1 = x + 40
    fx_at(big, "q3_wave", go, x, gy - 5, until=go + tick(46 / 3), x1=x + 46)
    up = go + tick((d.x - 12 - x) / 3)
    knock(d, up, 1000)
    d.death = up + 1000
    a("q3", tick(30), way=[(go, x), (go + tick(40 / 3), x1)])
    x = x1
    a("idle", 300, loop=True)
    # Spirit Cleave with Soul Unbound: the body stays, the spirit dashes onto Garen and cleaves him
    start = t
    home = x
    fx_at(small, "e_cast", start + tick(1), home, gy)
    bodies.append(Anim(frames_of(yone, "e_body"), start + tick(1), home, gy, until=start + tick(240)))
    back = start + tick(240)
    on_yone("spirit", start + tick(1), back)
    gx = g.pos(start)[0]
    spot = gx - 20
    dash = tick((spot - home) / 4)
    a("e_dash", tick(1) + dash, way=[(start + tick(1), home), (start + tick(1) + dash, spot)])
    x = spot
    swing = t
    fx_at(big, "w_cone", swing + tick(3), x + 22, gy)
    hit(g, swing + tick(8), "w_hit")
    on_yone("shield", swing + tick(8), swing + tick(8) + 1500, loop=False)
    pop = back + tick(12)
    over.append(OnFoe(frames_of(small, "e_mark_in"), swing + tick(8), g, z=2))
    over.append(OnFoeFor(frames_of(small, "e_mark"), swing + tick(8) + 240, g, pop, z=2))
    a("skill2", tick(24))
    a("idle", 400, loop=True)
    # the spirit cuts Garen twice more
    for tag, h in (("attack", "hit"), ("attack2", "hit2")):
        s = t
        hit(g, s + tick(10), h)
        a(tag, tick(20))
        a("idle", tick(35), loop=True)
    a("idle", back - t, loop=True)
    # back to the body; the mark bursts 2-22 ticks later (here 12)
    fx_at(small, "e_cast", back, x, gy)
    x = home
    over.append(Follow(frames_of(small, "e_return"), back, x, gy, on=body, z=1))
    hit(g, pop, "e_pop")
    over.append(OnFoe(frames_of(small, "e_mark_end"), pop, g, z=2))
    a("idle", 500, loop=True)
    # Fate Sealed at Garen: the warning line for 15 ticks, then the slash, Garen thrown up for 0.75 s (and he
    # falls), and Yone rushes to 15 px behind him at 12 px a tick
    start = t
    fx_at(big, "r_line", start + tick(1), x + 45, gy)
    cut = start + tick(16)
    hit(g, cut, "w_hit")
    knock(g, cut, 750)
    g.death = cut + 750
    behind = g.pos(cut)[0] + 15
    rush = tick((behind - x) / 12)
    a("ult", tick(44), way=[(cut, x), (cut + rush, behind)])
    x = behind
    a("idle", 1200, loop=True)
    end = t

    return film(out, W, H, gy, end, (g, d), body, bodies, under, over, z=z, step=step)


def film(out, W, H, gy, end, foes, body, bodies, under, over, labels=(), z=3, step=40):
    """Draw the clip: ground effects, the foes and Yone (and his left body) by depth, the other effects; labels =
    [(t0, t1, text)] in a corner."""
    font = ImageFont.load_default(size=8 * z) if labels else None

    def place(img, f, px, py):
        img.alpha_composite(f, (int(px) - f.width // 2, int(py) - f.height // 2))

    frames, tt = [], 0.0
    while tt < end:
        img = Image.new("RGBA", (W, H), ARENA)
        for an in under:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        units = [(fo.pos(tt)[1], fo.frame(tt), fo.pos(tt)) for fo in foes]
        for an in bodies:
            f = an.frame(tt)
            if f is not None:
                units.append((gy, f, an.pos(tt)))
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
        img = img.resize((W * z, H * z), Image.NEAREST).convert("RGB")
        for t0, t1, text in labels:
            if t0 <= tt < t1:
                ImageDraw.Draw(img).text((4 * z, 2 * z), text, font=font, fill=(255, 236, 160),
                                         stroke_width=z // 2 + 1, stroke_fill=(24, 20, 16))
        frames.append(img)
        tt += step
    sample = frames[::6]                              # one palette for the whole clip
    strip = Image.new("RGB", (W * z, H * z * len(sample)))
    for i, f in enumerate(sample):
        strip.paste(f, (0, i * H * z))
    pal = strip.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q[0].save(T.long_path(out), save_all=True, append_images=q[1:], duration=step, loop=0, optimize=False)
    return len(frames), round(end / 1000.0, 1)


def combos(out, z=3, step=40):
    """The combos (tools/kit/yone_combos.py), labelled: Q3 throws Darius up; a thrust on him in the air (a storm
    stack); the quick R inside Q3's window - Q3's dash pose, the slash on tick 8 through Darius and Garen behind him,
    Yone behind Darius (Q3 R); R's hits fill the storm, so the next Q is Q3 again, through Garen (R Q3)."""
    yone = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_yone_fx"], fx["league_yone_big"]
    W, H = 330, 150
    gy = 104
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), 155, gy)
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), 215, gy)
    body, bodies, under, over, labels = [], [], [], [], []
    t = 0.0
    x = 100

    def a(tag, dur=None, loop=False, at=None, way=None):
        nonlocal t
        an = Path(frames_of(yone, tag), t, at if at is not None else x, gy, loop=loop,
                  until=(t + dur) if dur else None, way=way or ())
        body.append(an)
        t = an.until

    def fx_at(sp, tag, at, px, py=gy, until=None, x1=None, loop=None):
        an = Anim(frames_of(sp, tag), at, px, py, z=1, loop=(until is not None) if loop is None else loop,
                  until=until, x1=x1)
        over.append(an)
        return an

    def on_yone(tag, t0, until):
        over.append(Follow(frames_of(small, tag), t0, x, gy, loop=True, until=until, on=body, z=1))

    def hit(foe, when, tag="hit", sp=None):
        over.append(OnFoe(frames_of(sp or small, tag), when, foe, z=1))
        foe.flinches.append(when)

    def knock(foe, when, ms):
        foe.hops.append((when, when + ms, 10))
        fx_at(small, "knockup", when, foe.pos(when)[0], gy)

    def q3(to, foe):
        """Q3: the gust and a 40 px dash at 3 px a tick from tick 9; foe thrown up for 1 s as the gust reaches him."""
        nonlocal x
        start = t
        go = start + tick(9)
        fx_at(big, "q3_wave", go, x, gy - 5, until=go + tick(46 / 3), x1=x + 46)
        knock(foe, go + tick(max(0.0, (foe.x - 12 - x) / 3)), 1000)
        a("q3", tick(30), way=[(go, x), (go + tick(abs(to - x) / 3), to)])
        x = to
        return start

    a("idle", 300, loop=True)
    on_yone("q_ready", 0, t)
    s0 = q3(x + 40, d)
    a("idle", tick(3), loop=True)
    # a thrust at Darius in the air: the spear from tick 1, the hit on tick 9 (a storm stack)
    q1 = t
    fx_at(big, "q_thrust", q1 + tick(1), x + 22, gy)
    hit(d, q1 + tick(9), "q_hit")
    a("skill", tick(24))
    # the quick R inside Q3's window: Q3's dash pose, the line from tick 1, the slash on tick 8 through both, the
    # rush to 15 px behind Darius at 12 px a tick
    r0 = t
    fx_at(big, "r_line", r0 + tick(1), x + 45, gy)
    cut = r0 + tick(8)
    for foe in (d, g):
        hit(foe, cut, "w_hit")
        knock(foe, cut, 750)
    d.death = cut + 750
    behind = d.x + 15
    a("q3", tick(30), way=[(cut, x), (cut + tick((behind - x) / 12), behind)])
    x = behind
    # R's hits fill the storm: the wind at his waist, and Q3 again, through Garen
    on_yone("q_ready", cut + tick(1), t + tick(4))
    a("idle", tick(4), loop=True)
    s1 = q3(x + 40, g)
    g.death = s1 + tick(9) + tick((g.x - 12 - (x - 40)) / 3) + 1000
    a("idle", 1300, loop=True)
    labels += [(s0, q1, "Q3"), (q1, r0, "Q3 Q"), (r0, s1, "Q3 R"), (s1, t, "R Q3")]
    return film(out, W, H, gy, t, (g, d), body, bodies, under, over, labels=labels, z=z, step=step)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    s = load(CHAMP)
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_yone_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[12:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_yone_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_yone_showcase.gif")))
    print("combos frames/seconds", combos(os.path.join(args.out, "league_yone_combos.gif")))


if __name__ == "__main__":
    main()
