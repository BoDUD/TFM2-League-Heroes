#!/usr/bin/env python3
"""Preview images for Kennen, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_kennen.py [--out docs/preview]

  league_kennen_frames.png    every animation, frame by frame, 3x on the arena colour
  league_kennen_effects.png   every effect animation (both sheets), 3x
  league_kennen_showcase.gif  a scripted fight against Darius and Garen, timed like the kit: he runs in and throws
                              Thundering Shuriken (the flash at his claw, the lightning star, the hit and one mark over
                              Darius's head); the hit sets off Electrical Surge (the ring round him, the shock and the
                              second mark); Lightning Rush: the flash where he stood, the ball round him as he rushes
                              in, the zap and the third mark - Darius is stunned (the lightning columns); two attacks,
                              the second the charged fifth (violet flash and shock, a new mark); Garen walks up;
                              Slicing Maelstrom: the storm round him for 3 s, a bolt on every champion inside each
                              0.5 s with a mark - the third stuns them both, Darius falls; 3x
Projectiles fly as the kit flies them: from his pivot lifted 3.5 px (5000 - y_offset 1500), the star at 5 px a tick,
Q's at 8, empty until they reach his hand (tools/art/import_kennen.py).
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
from preview_caitlyn import Turned  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_jinx import Follow  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_kennen")
FX = os.path.join(LEAGUE, "effects", "league_kennen_fx")
BIG = os.path.join(LEAGUE, "effects", "league_kennen_big")
STAR, QSTAR = 5.0, 8.0          # px a tick (star_speed 5000, q_speed 8000)
LIFT = 3.5                      # 5000 - y_offset 1500
RUSH = 2.5                      # E's RushTime, px a tick, for 16 ticks
SPEED = 60.0                    # move speed 1000: px a second


def showcase(out, z=3, step=40):
    kn = load(CHAMP)
    fx, big = load(FX), load(BIG)
    W, H = 320, 160
    gy = 100                                           # his pivot row: the storm's bolts rise 80 px over it
    x = 45
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), 185, gy)
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), 330, gy - 6)    # a row behind, off the edge
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False, to=None):
        nonlocal t, x
        an = Anim(frames_of(kn, tag), t, x, gy, loop=loop, until=(t + dur) if dur else None, x1=to)
        body.append(an)
        t = an.until
        if to is not None:
            x = to
        return an

    def idle_to(at):
        if at > t:
            a("idle", at - t, loop=True)

    def flash(tag, at, sheet=None, ground=False):
        """A CasterViewEffect with is_follow: it rides his pivot (ground: under the units)."""
        an = Follow(frames_of(sheet or fx, tag), at, x, gy, on=body)
        (under if ground else over).append(an)
        return an

    def left(tag, at, px):
        """A CasterViewEffect without is_follow: it stays where it was played."""
        over.append(Anim(frames_of(fx, tag), at, px, gy))

    def fly(tag, at, foe, speed):
        """A projectile from his pivot (lifted) at the foe's pivot; its arrival."""
        fx_, fy = foe.pos(at)
        x0, y0 = x, gy - LIFT
        arrive = at + tick(max(1.0, (math.hypot(fx_ - x0, fy - y0) - 6) / speed))
        over.append(Turned(frames_of(fx, tag), at, x0, y0, until=arrive, x1=fx_ - 6, y1=fy))
        return arrive

    def on(foe, tag, at, sheet=None):
        over.append(OnFoe(frames_of(sheet or fx, tag), at, foe, z=2))

    marks = {"n": 0, "stunned": {}}

    def mark(foes, at):
        """One mark from one cast (counted on him): the pips over their heads, the third stuns them all - 1.25 s, or
        0.5 s for one stunned in the last 7 s."""
        marks["n"] += 1
        for foe in foes:
            if marks["n"] < 3:
                on(foe, f"k_mark{marks['n']}", at)
                continue
            on(foe, "k_stun", at)
            last = marks["stunned"].get(id(foe))
            foe.holds.append((at, at + (500 if last is not None and at - last < 7000 else 1250)))
            marks["stunned"][id(foe)] = at
        if marks["n"] >= 3:
            marks["n"] = 0

    # he runs in (move speed 1000: 60 px a second) to 45 px from Darius
    a("run", tick(95 / SPEED * 60), loop=True, to=140)
    # Thundering Shuriken: the 26-tick throw, the flash and the star on tick 10; its hit marks him and, the surge being
    # ready, Electrical Surge comes 4 ticks later: the pose at once, the burst on its tick 6
    q0 = t
    flash("q_cast", q0 + tick(10))
    hit = fly("q_star", q0 + tick(10), d, QSTAR)
    on(d, "q_hit", hit)
    d.flinches.append(hit)
    mark([d], hit)
    a("skill", hit + tick(4) - q0)
    w0 = t
    burst = w0 + tick(6)
    flash("w_burst", burst, big, ground=True)
    on(d, "w_hit", burst)
    d.flinches.append(burst)
    mark([d], burst)
    a("w", tick(17))
    idle_to(w0 + 900)
    # Lightning Rush: the flash where he stood, the ball round him, 40 px in 16 ticks at Darius; the zap as he reaches
    # him is the third mark: Darius is stunned; the ball breaks where he ends (no surge: it is cooling down)
    e0 = t
    left("e_in", e0, x)
    flash("e_ball", e0)
    zap = e0 + tick(14)
    on(d, "e_hit", zap)
    mark([d], zap)
    a("skill2", tick(16), to=x + 40)
    left("e_out", e0 + tick(17), x)
    a("skill2", tick(2))
    # two attacks: the star leaves his hand on tick 11 of the 24-tick throw; the second is the charged fifth
    for k in range(2):
        s0 = t
        flash("a_cast2" if k else "a_cast", s0 + tick(11))
        land = fly("a_star", s0 + tick(11), d, STAR)
        on(d, "a_hit2" if k else "a_hit", land)
        d.flinches.append(land)
        if k:
            mark([d], land)
        a("attack", tick(24))
        idle_to(s0 + tick(70) if not k else s0 + tick(40))
    # Garen walks up behind Darius
    g.walks.append((t - 900, t + 1100, 215 - g.x))
    # Slicing Maelstrom: the storm on him for 3 s; a bolt on every champion within 55 px each 30 ticks, each strike
    # one mark
    r0 = t
    flash("r_storm", r0, big, ground=True)
    a("ult", tick(24))
    for k in range(6):
        at = r0 + tick(30 * k)
        inside = [f for f in (d, g) if abs(f.pos(at)[0] - x) <= 55 and (f.death is None or at < f.death)]
        for f in inside:
            on(f, "r_hit", at, big)
            f.flinches.append(at)
        if inside:
            mark(inside, at)
        if k == 3:
            d.death = at + tick(6)
    idle_to(r0 + 3300)
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
                            os.path.join(args.out, "league_kennen_frames.png")))
    sp, bp = load(FX), load(BIG)
    print("effects", contact([(sp, t["name"], t["name"]) for t in sp.tags] +
                             [(bp, t["name"], t["name"]) for t in bp.tags],
                             os.path.join(args.out, "league_kennen_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_kennen_showcase.gif")))


if __name__ == "__main__":
    main()
