#!/usr/bin/env python3
"""Preview images for Alistar, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_alistar.py [--out docs/preview] [--only showcase]

  league_alistar_frames.png    every animation, frame by frame, 3x on the arena colour
  league_alistar_effects.png   every effect animation, 3x
  league_alistar_showcase.gif  a scripted fight against Darius with Garen beside him, timed like the kit: Alistar trots
                               in; Trample into Pulverize (E -> Q): a stomp, the slam, both thrown up, the stomps go on
                               round him; two punches, the fifth champion stomp lights the chain glyph and the next punch
                               stuns Darius (stars over his head); his crowd control has landed three times: Triumphant
                               Roar heals him; Garen backs off, Headbutt -> Pulverize: the charge, the headbutt knocks
                               Garen back, the slam where he lands throws him up; Unbreakable Will: the roar, the rage
                               aura; 3x
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
from preview_yone import OnFoeFor, Path  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_alistar")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_alistar_fx", "league_alistar_big")}


class At:
    """A fixed point for the views that stay where they were played."""

    def __init__(self, x, y):
        self.x, self.y = x, y

    def pos(self, t):
        return self.x, self.y


class Me:
    """Alistar's pivot at time t (the body animation playing then)."""

    def __init__(self, body):
        self.body = body

    def pos(self, t):
        for an in self.body:
            if an.t0 <= t < an.until:
                return an.pos(t)
        return self.body[-1].pos(t)


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_alistar_fx"], fx["league_alistar_big"]
    W, H = 340, 160
    gy = 112
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), 168, gy)
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), 200, gy - 8)
    body, under, over = [], [], []
    me = Me(body)
    t = 0.0
    x = 40

    def a(tag, dur=None, loop=False, way=None):
        nonlocal t
        an = Path(frames_of(sp, tag), t, x, gy, loop=loop, until=(t + dur) if dur else None, way=way or ())
        body.append(an)
        t = an.until
        return an

    def fx_at(s, tag, at, unit, ground=False, until=None):
        if until is not None:
            an = OnFoeFor(frames_of(s, tag), at, unit, until, z=-1 if ground else 1)
        else:
            an = OnFoe(frames_of(s, tag), at, unit, z=-1 if ground else 1)
        (under if ground else over).append(an)
        return an

    def hit(foe, when, tag):
        fx_at(small, tag, when, foe)
        foe.flinches.append(when)

    # he trots in (66 px a second) to melee range of Darius
    x1 = 132
    a("run", (x1 - x) / 66 * 1000, loop=True, way=[(0, x), ((x1 - x) / 66 * 1000, x1)])
    x = x1
    a("idle", 300, loop=True)
    # Trample into Pulverize: a stomp at the cast, the slam on tick 14, both thrown up 60 ticks; stomps every 30 ticks
    q0 = t
    stomps = [q0 + tick(30 * k) for k in range(7)]
    for s_ in stomps:
        fx_at(big, "e_stomp", s_, At(x, gy), ground=True)
        for foe in (d, g):
            hit(foe, s_ + tick(1), "e_hit")
    slam = q0 + tick(14)
    fx_at(big, "q_slam", slam, At(x, gy), ground=True)
    for foe in (d, g):
        foe.hops.append((slam, slam + tick(60), 12))
        fx_at(small, "q_up", slam, foe)
    a("skill")
    a("idle", 150, loop=True)
    # two punches (hit on tick 12, an attack every 80 ticks); the fifth champion stomp lights the chain glyph
    for _ in range(2):
        hit(d, t + tick(12), "a_hit")
        a("attack")
        a("idle", tick(80 - 26), loop=True)
    ready = stomps[4] + tick(1)
    fx_at(small, "e_ready", ready, At(x, gy))
    # the stunning punch: Darius stunned 60 ticks, stars over his head
    p = t + tick(12)
    hit(d, p, "a_hit")
    fx_at(small, "e_hit_stun", p, d)
    fx_at(small, "e_stun", p, d, until=p + tick(60))
    d.holds.append((p, p + tick(60)))
    a("attack")
    # three crowd controls on champions (the two knock-ups and the stun): Triumphant Roar heals him
    roar = p + tick(1)
    fx_at(big, "p_roar", roar, At(x, gy))
    fx_at(small, "p_heal", roar, me)
    a("idle", tick(80 - 26) + 300, loop=True)
    # Garen backs off; Headbutt: the charge (3.5 px a tick), the headbutt knocks him back 20 px in 8 ticks, the slam
    # 6 ticks later where he landed throws him up
    g.walks.append((t - 600, t, 34))
    w0 = t
    gx = g.pos(w0)[0]
    reach = gx - 22
    dash = tick((reach - x) / 3.5)
    fx_at(big, "w_dash", w0, me)
    a("skill2", dash, loop=True, way=[(w0, x), (w0 + dash, reach)])
    x = reach
    butt = t
    fx_at(small, "w_butt", butt, At(x, gy))
    hit(g, butt, "w_hit")
    g.walks.append((butt, butt + tick(8), 20))
    a("butt", tick(6))
    slam2 = t + tick(5)
    fx_at(big, "w_slam", slam2, At(x, gy), ground=True)
    g.hops.append((slam2, slam2 + tick(60), 12))
    fx_at(small, "q_up", slam2, g)
    a("slam")
    a("idle", 400, loop=True)
    # Unbreakable Will: the roar, the rage aura for its 7 s (shown 2 s)
    r0 = t
    fx_at(big, "r_cast", r0, At(x, gy))
    fx_at(big, "r_on", r0 + tick(6), me, until=r0 + 2400, ground=True)      # drawn behind him (z -1)
    a("ult")
    a("idle", 2400 - tick(30), loop=True)
    a("idle", 500, loop=True)
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
        units = [(g.pos(tt)[1], g.frame(tt), g.pos(tt)), (d.pos(tt)[1], d.frame(tt), d.pos(tt))]
        for an in body:
            f = an.frame(tt)
            if f is not None:
                units.append((an.pos(tt)[1], f, an.pos(tt)))
                break
        for _, f, p_ in sorted(units, key=lambda u: u[0]):
            if f is not None:
                place(img, f, *p_)
        for an in over:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        frames.append(img.resize((W * z, H * z), Image.NEAREST).convert("RGB"))
        tt += step
    sample = frames[::6]
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
    ap.add_argument("--only", choices=["frames", "effects", "showcase"])
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    if args.only in (None, "frames"):
        s = load(CHAMP)
        print("frames", contact([(s, t["name"], t["name"]) for t in s.tags],
                                os.path.join(args.out, "league_alistar_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[15:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_alistar_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_alistar_showcase.gif")))


if __name__ == "__main__":
    main()
