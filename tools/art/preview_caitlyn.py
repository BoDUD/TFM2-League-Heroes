#!/usr/bin/env python3
"""Preview images for Caitlyn, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_caitlyn.py [--out docs/preview]

  league_caitlyn_frames.png    every animation, frame by frame, 3x on the arena colour
  league_caitlyn_effects.png   every effect animation, 3x
  league_caitlyn_showcase.gif  a scripted fight against Darius and Garen, timed like the kit: she runs in and two
                               rifle shots hit Darius from her long reach (the flash at the raised muzzle); he walks
                               up to her: the shot becomes the net (90 Caliber Net) - it slows him and she hops back
                               - and the next shot is a Headshot; a trap thrown at his feet lands, arms and snaps
                               shut on him, rooting him, and her next shot is a Headshot from the trap; Garen comes
                               up behind him; Piltover Peacemaker pierces both and Darius falls; Ace in the Hole:
                               the crosshair on Garen for the 1 s channel, then the long shot; 3x
Projectiles fly as the kit flies them: from over her pivot, lifted to the muzzle's height (5000 - y_offset), at the
target's pivot, turned to their way; their tags start empty while they cross her (tools/art/import_caitlyn.py).
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
from preview_jinx import Arc, Follow  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_caitlyn")
FX = os.path.join(LEAGUE, "effects", "league_caitlyn_fx")
# the kit's projectiles: speed in px a tick, lift over her pivot in px (5000 - y_offset)
BOLT, HS, NET, Q, R = (7.0, 6.5), (9.0, 8.0), (6.0, 11.5), (10.0, 7.5), (20.0, 9.0)


class Turned(Anim):
    """A projectile's picture turned to its flight from (x, y) to (x1, y1), as the game turns a view."""

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        deg = -math.degrees(math.atan2(self.y1 - self.y, self.x1 - self.x))
        self.fr = [(f.rotate(deg, resample=Image.NEAREST, expand=True) if f.width > 1 else f, ms) for f, ms in self.fr]


def showcase(out, z=3, step=40):
    ct = load(CHAMP)
    fx = load(FX)
    W, H = 300, 124
    gy = 88                                            # her pivot row: the hat stands 29 px over it
    x = 70                                             # where she stands after running in
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), 160, gy)
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), 330, gy - 6)      # a row behind, off the edge
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False, at=None, to=None):
        nonlocal t, x
        an = Anim(frames_of(ct, tag), t, at if at is not None else x, gy, loop=loop,
                  until=(t + dur) if dur else None, x1=to)
        body.append(an)
        t = an.until
        if to is not None:
            x = to
        return an

    def idle_to(at):
        if at > t:
            a("idle", at - t, loop=True)

    def flash(tag, at):
        """A CasterViewEffect with is_follow: it rides her pivot."""
        over.append(Follow(frames_of(fx, tag), at, x, gy, on=body))

    def fly(tag, at, foe, kind):
        """A TargetProjectile from over her pivot to the foe's pivot. Its arrival."""
        speed, lift = kind
        fx_, fy = foe.pos(at)
        x0, y0 = x, gy - lift
        arrive = at + tick(max(1.0, math.hypot(fx_ - x0, fy - y0) / speed))
        over.append(Turned(frames_of(fx, tag), at, x0, y0, until=arrive, x1=fx_, y1=fy))
        return arrive

    def on(foe, tag, at, until=None):
        an = OnFoe(frames_of(fx, tag), at, foe, z=2)
        if until is not None:
            an.loop, an.until = True, until
        over.append(an)
        return an

    def shot(foe, gap=850):
        """The rifle: the bullet leaves on tick 8 of the 24-tick strip, the flash at the raised muzzle."""
        start = t
        fire = start + tick(8)
        flash("shot", fire)
        land = fly("bolt", fire, foe, BOLT)
        on(foe, "hit", land)
        foe.flinches.append(land)
        a("attack", tick(24))
        return start + gap

    def headshot(foe, tag="hs_bolt", gap=850):
        """A Headshot: the passive strip (22 ticks), the shot on tick 10."""
        start = t
        fire = start + tick(10)
        flash("hs_shot", fire)
        land = fly(tag, fire, foe, HS)
        on(foe, "hs_hit", land)
        foe.flinches.append(land)
        a("passive", tick(22))
        return start + gap

    # she runs in (move speed 900: 54 px a second); Darius is 90 px away, in her reach
    a("run", 1000, loop=True, at=16, to=x)
    x = 70
    for _ in range(2):
        idle_to(shot(d))
    # he walks up to her (42 px): her next attack is the net
    walk0 = t
    d.walks.append((walk0, walk0 + 900, -48))
    idle_to(walk0 + 950)
    e0 = t
    flash("e_shot", e0 + tick(6))
    net_hit = fly("e_net", e0 + tick(6), d, NET)
    on(d, "e_hit", net_hit)
    on(d, "e_slow", net_hit, until=net_hit + tick(60))
    d.flinches.append(net_hit)
    # MoveBack 5000 x 6 from tick 7: 30 px straight away from him
    hop0, hop1, x0 = e0 + tick(7), e0 + tick(13), x
    an = a("e", tick(34))
    an.pos = lambda tt, a0=x0: (int(round(a0 - 30 * min(1.0, max(0.0, (tt - hop0) / (hop1 - hop0))))), gy)
    x = x0 - 30
    idle_to(e0 + 750)
    idle_to(headshot(d))                               # after the net: a Headshot
    # W at his feet: the throw leaves on tick 10, lands 15 ticks later, arms 30 ticks after that and snaps him
    w0 = t
    throw = w0 + tick(10)
    spot = d.pos(throw)
    land = throw + tick(15)
    over.append(Arc(frames_of(fx, "w_throw"), throw, x, gy, until=land, x1=spot[0], y1=spot[1], h=22))
    under.append(Anim(frames_of(fx, "w_land"), land, *spot))
    armed = land + tick(30)                            # he stands on it: it bites as it arms
    on(d, "w_snap", armed)
    d.holds.append((armed, armed + tick(75)))
    a("skill2", tick(24))
    idle_to(armed + 150)
    idle_to(headshot(d, "hs_bolt"))                    # the trap's Headshot (hs_trap_bolt: the same picture)
    # Garen comes up behind him
    g.walks.append((t - 1600, t + 200, 150 - g.x))
    idle_to(t + 250)
    # Piltover Peacemaker at Darius: the shot on tick 24 of the 40-tick strip, a piercing line 120 px long
    q0 = t
    qf = q0 + tick(24)
    flash("q_muzzle", qf)
    x1 = x + 120
    q_end = qf + tick(120 / Q[0])
    over.append(Turned(frames_of(fx, "q_bolt"), qf, x, gy - Q[1], until=q_end, x1=x1, y1=gy))
    for foe in (d, g):
        fx_, _ = foe.pos(qf)
        hit_at = qf + tick((fx_ - x) / Q[0])
        on(foe, "q_hit", hit_at)
        foe.flinches.append(hit_at)
        if foe is d:
            d.death = hit_at + tick(6)
    a("skill", tick(40))
    idle_to(t + 300)
    # Ace in the Hole on Garen: the crosshair for the 60-tick channel, the shot on tick 61, 20 px a tick
    r0 = t
    on(g, "r_mark", r0 + tick(1), until=r0 + tick(61))
    rf = r0 + tick(61)
    flash("r_muzzle", rf)
    gx, gy2 = g.pos(rf)
    r_hit = rf + tick(max(1.0, math.hypot(gx - x, gy2 - (gy - R[1])) / R[0]))
    over.append(Turned(frames_of(fx, "r_bullet"), rf, x, gy - R[1], until=r_hit, x1=gx, y1=gy2))
    on(g, "r_hit", r_hit)
    g.death = r_hit + tick(4)
    a("ult", tick(84))
    idle_to(t + 900)
    end = t

    def place(img, f, px, py):
        img.alpha_composite(f, (px - f.width // 2, py - f.height // 2))

    frames, tt = [], 0.0
    order = sorted((d, g), key=lambda f: f.y)          # the one further back first
    while tt < end:
        img = Image.new("RGBA", (W, H), ARENA)
        for an in under:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        for foe in order:
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
    sample = frames[::6]                               # one palette for the whole clip
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
                            os.path.join(args.out, "league_caitlyn_frames.png")))
    sp = load(FX)
    print("effects", contact([(sp, t["name"], t["name"]) for t in sp.tags],
                             os.path.join(args.out, "league_caitlyn_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_caitlyn_showcase.gif")))


if __name__ == "__main__":
    main()
