#!/usr/bin/env python3
"""Preview images for Aatrox, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_aatrox.py [--out docs/preview]

  league_aatrox_frames.png    every animation, frame by frame, 3x on the arena colour
  league_aatrox_effects.png   every effect animation, 3x
  league_aatrox_showcase.gif  a scripted fight against Darius with Garen behind him, timed like the kit: Aatrox
                              walks in and swings twice; the empowered strike (Deathbringer Stance) thrusts a streak
                              from the blade and bursts on Darius; The Darkin Blade three times with Umbral Dash in
                              each wind-up - Q1 hops back so Darius stands on the long slam's edge (the arc, the
                              line on the ground, the edge's pillar and knock-up), Q2's sweep and fan catch him on
                              the rim, Q3 rushes in and slams the ring onto him; Infernal Chains: the claw's flash,
                              the chain flies and hits, the ring lies under him and links run to its centre while he
                              walks off inside it (he had backed off first), and at 1.5 s the chains snap him back to the
                              centre (Garen, by the ring, is left alone); World Ender: the transformation, the wings and the aura,
                              two more strikes, Darius falls and the renewal flares; 3x
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
CHAMP = os.path.join(LEAGUE, "champions", "league_aatrox")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_aatrox_fx", "league_aatrox_big")}


class Body(Anim):
    """Aatrox's animation with slides (t0, t1, dx) along the way (E's hop and rush)."""

    def __init__(self, *args, slides=(), **kw):
        super().__init__(*args, **kw)
        self.slides = list(slides)

    def pos(self, t):
        x, y = self.x, self.y
        for t0, t1, dx in self.slides:
            if t >= t0:
                x += dx * min(1.0, (t - t0) / max(1.0, t1 - t0))
        return int(round(x)), y


class Me:
    """Aatrox's pivot for the views that follow him: the body animation playing at that moment."""

    def __init__(self, body):
        self.body = body

    def pos(self, t):
        last = None
        for an in self.body:
            if an.t0 <= t:
                last = an
            if an.frame(t) is not None:
                return an.pos(t)
        return last.pos(t) if last else (0, 0)


def showcase(out, z=3, step=40):
    aatrox = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_aatrox_fx"], fx["league_aatrox_big"]
    W, H = 330, 150
    gy = 104                                          # the pivot row: the transformation rises ~65 px over his soles
    x = 96
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x + 26, gy + 2)      # 26 px: attack range
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x + 112, gy - 22)     # behind, past W's ring
    body, under, over = [], [], []
    me = Me(body)
    t = 0.0

    def a(tag, dur=None, loop=False, slides=()):
        nonlocal t, x
        an = Body(frames_of(aatrox, tag), t, x, gy, loop=loop, until=(t + dur) if dur else None, slides=slides)
        body.append(an)
        t = an.until
        x = an.pos(t)[0]
        return an

    def on(unit, sp, tag, when, until=None, ground=False):
        an = OnFoe(frames_of(sp, tag), when, unit, z=-1 if ground else 1)
        if until is not None:
            an.loop, an.until = True, until
        (under if ground else over).append(an)
        return an

    def at(sp, tag, when, px, py, ground=False, until=None, x1=None, y1=None, flip=False):
        an = Anim(frames_of(sp, tag), when, px, py, z=-1 if ground else 1, loop=until is not None and x1 is None,
                  until=until, x1=x1, y1=y1, flip=flip)
        (under if ground else over).append(an)
        return an

    def hit_on(foe, tag, when):
        on(foe, small, tag, when)
        foe.flinches.append(when)

    # he walks in; Darius and Garen wait
    run_in = Body(frames_of(aatrox, "run"), 0.0, x - 50, gy, loop=True, until=1000, slides=[(0.0, 1000.0, 50)])
    body.append(run_in)
    t = run_in.until
    a("idle", 300, loop=True)
    # two swings (the hit on tick 12), 66 ticks apart
    for _ in range(2):
        hit_on(d, "a_hit", t + tick(12))
        a("attack")
        a("idle", tick(66 - 26), loop=True)
    # Deathbringer Stance: the streak from the blade's tip 4 ticks before the hit (tick 18)
    on(me, small, "p_swing", t + tick(14))
    hit_on(d, "p_hit", t + tick(18))
    a("attack_p")
    a("idle", 400, loop=True)

    def q(tag, k, hit_t, slide, edge_up):
        """A Q cast: E's slide in the wind-up (6-7 ticks at 3 px), the slash 4 ticks before the hit, the ground
        shape on the hit and the edge's pillar + knock-up on Darius."""
        nonlocal t
        q0 = t
        an = a(tag, slides=[(q0, q0 + tick(abs(slide) / 3.0), slide)] if slide else ())
        if slide:
            on(me, small, "e_dash", q0)
        on(me, small, f"q{k}_slash", q0 + tick(hit_t - 4))
        hx, hy = an.pos(q0 + tick(hit_t))
        if k == 1:
            at(big, "q1_body", q0 + tick(hit_t), hx + 23, hy, ground=True)
        elif k == 2:
            at(big, "q2_body", q0 + tick(hit_t), hx + 15, hy, ground=True)
        else:
            at(big, "q3_body", q0 + tick(hit_t), hx + 24, hy, ground=True)
        hit_on(d, "q_hit", q0 + tick(hit_t))
        on(d, small, "q_edge", q0 + tick(hit_t))
        d.hops.append((q0 + tick(hit_t), q0 + tick(hit_t + edge_up), 8 if k < 3 else 11))

    # Q1: Darius 26 px away, the edge 46: E hops back 18 px first
    q("skill", 1, 22, -18, 20)
    a("idle", 300, loop=True)
    # Q2: the rim at 38 +-10: Darius at 44 is on it
    q("q2", 2, 22, 0, 20)
    a("idle", 300, loop=True)
    # Q3: the slam's middle 24 ahead: E rushes 21 px in
    q("q3", 3, 24, 21, 30)
    a("idle", 500, loop=True)

    # Darius backs off 40 px; Infernal Chains after him: the chain on tick 14 from the claw, 5 px a tick, raised 8 px
    d.runs.append((t, t + 700))
    d.slides.append((t, t + 700, 40))
    a("idle", 800, loop=True)
    w0 = t
    on(me, small, "w_throw", w0 + tick(14))
    mx, my = x, gy
    dx, dy = d.pos(w0 + tick(14))
    fly = max(1.0, (dx - mx) / 5.0)
    hit = w0 + tick(14 + fly)
    at(small, "w_chain", w0 + tick(14), mx, my - 8, until=hit, x1=dx, y1=dy)
    hit_on(d, "w_hit", hit)
    on(d, small, "w_slowed", hit, until=hit + tick(90), ground=True)
    # the ring under him, 3 px toward Aatrox; he walks off 18 px inside it (radius 33); Garen, by the ring's far edge,
    # is untouched (the chain holds only the one it hit)
    cx, cy = dx - 3, dy
    at(big, "w_ring_in", hit, cx, cy, ground=True)
    for k in range(24, 90, 16):
        if k + 16 <= 90 + 8:
            at(big, "w_ring_beat", hit + tick(k), cx, cy, ground=True)
    d.runs.append((hit + tick(10), hit + tick(70)))
    d.slides.append((hit + tick(10), hit + tick(70), 18))
    # the links: every 4 ticks one flies from his feet to the ring's centre at 2.5 px a tick
    for k in range(0, 90, 4):
        lt = hit + tick(k)
        lx, ly = d.pos(lt)
        span = max(1.0, abs(lx - cx))
        at(small, "w_link", lt, lx, ly + 9, until=lt + tick(span / 2.5), x1=cx, y1=cy + 9, flip=lx > cx)
    # 1.5 s: the snap, the second hit and the pull back to the centre (8 ticks)
    snap = hit + tick(90)
    at(big, "w_snap", snap, cx, cy, ground=True)
    hit_on(d, "w_yank", snap)
    px = d.pos(snap)[0]
    d.slides.append((snap, snap + tick(8), cx - px))
    a("skill2")
    a("idle", snap + tick(30) - t, loop=True)
    # he walks up to Darius (attack range)
    walk = d.pos(t)[0] - 26 - x
    a("run", walk / 0.06, loop=True, slides=[(t, t + walk / 0.06, walk)])

    # World Ender: the transformation (40 ticks), then the wings under him for the rest
    r0 = t
    on(me, big, "r_transform", r0)
    a("ult")
    aura = OnFoe(frames_of(big, "r_aura"), r0 + tick(20), me, z=-1)
    aura.loop, aura.until = True, None
    under.append(aura)
    a("idle", 300, loop=True)
    for _ in range(2):
        hit_on(d, "a_hit", t + tick(12))
        a("attack")
        a("idle", tick(66 - 26), loop=True)
    d.death = t - tick(66 - 26 - 1)
    on(me, small, "r_renew", d.death + tick(6))
    a("idle", 1400, loop=True)
    aura.until = t
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
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_aatrox_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_aatrox_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_aatrox_showcase.gif")))


if __name__ == "__main__":
    main()
