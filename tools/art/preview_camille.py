#!/usr/bin/env python3
"""Preview images for Camille, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_camille.py [--out docs/preview]

  league_camille_frames.png     every animation, frame by frame, 3x on the arena colour
  league_camille_effects.png    every effect animation, 3x
  league_camille_showcase.gif   a scripted fight against Garen and Darius, timed like the kit: she runs in and kicks
                                Garen - Adaptive Defenses wraps her in its hex shield; Precision Protocol's first
                                kick (the cyan star), a plain kick while it charges, the charged second kick (the
                                true-damage burst); Tactical Sweep's crescent catches Garen on its outer edge and he
                                falls. Darius walks up behind; Hookshot's claw flies to him, she is pulled across and
                                lands with a shock ring, Darius stunned under the hex stars. The Hextech Ultimatum:
                                a short leap, the arena rises round them and stays with her, the mark at his feet;
                                her kicks add true damage, he tries to walk out, hits the wall and is dragged back,
                                and falls; 3x
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

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_camille")
FX = os.path.join(LEAGUE, "effects", "league_camille_fx")
BIG = os.path.join(LEAGUE, "effects", "league_camille_big")
KICK = 64                                             # the attack's cooldown, ticks
KICK_E = 50                                           # with Hookshot's 30% attack speed


class Fleer(Held):
    """A foe that can also walk in (mirrored run frames, from the right) and walk off to the right (unmirrored)."""

    def __init__(self, sp, x, y):
        super().__init__(sp, x, y)
        self.flees = []                               # (t0, t1, dx): walking off to the right
        self.walks_in = []                            # (t0, t1, dx): walking left toward the fight

    def pos(self, t):
        x, y = super().pos(t)
        for t0, t1, dx in self.flees + self.walks_in:
            if t >= t0:
                x += int(round(dx * min(1.0, (t - t0) / (t1 - t0))))
        return x, y

    def frame(self, t):
        if self.death is not None and t >= self.death:
            return super().frame(t)
        for t0, t1, _ in self.flees:
            if t0 <= t < t1:
                return self.pick(self.run, (t - t0) % sum(ms for _, ms in self.run))
        for t0, t1, _ in self.walks_in:
            if t0 <= t < t1:
                return self.flip(self.pick(self.run, (t - t0) % sum(ms for _, ms in self.run)))
        return super().frame(t)


def turned(frames, angle):
    """A projectile's frames turned to its flight (degrees, counter-clockwise on screen)."""
    if abs(angle) < 0.5:
        return frames
    return [(f.rotate(angle, resample=Image.NEAREST, expand=True), ms) for f, ms in frames]


def showcase(out, z=3, step=40):
    cam = load(CHAMP)
    fx, big = load(FX), load(BIG)
    W, H = 300, 130
    gy = 92                                            # her pivot row: the crown stands 34 px over it
    back = gy - 12                                     # the back row, where Darius comes in
    g = Fleer(load(os.path.join(LEAGUE, "champions", "league_garen")), 102, gy)
    d = Fleer(load(os.path.join(LEAGUE, "champions", "league_darius")), 340, back)
    body, under, over = [], [], []
    t = 0.0
    spot = {"x": 70, "y": gy}

    def a(tag, dur=None, loop=False, at=None, to=None):
        nonlocal t
        an = Anim(frames_of(cam, tag), t, at if at is not None else spot["x"], spot["y"], loop=loop,
                  until=(t + dur) if dur else None, x1=to)
        body.append(an)
        t = an.until
        return an

    def idle_to(at):
        if at > t:
            a("idle", at - t, loop=True)

    def on(sp, tag, at, foe, z=2):
        an = OnFoe(frames_of(sp, tag), at, foe, z=z)
        (under if z < 0 else over).append(an)
        return an

    def kick(foe, tag="attack", hit_tick=8, ticks=None, view="hit", gap=KICK, extra=None):
        """A kick: its strip, the hit on hit_tick, idle until the next attack."""
        start = t
        hit = start + tick(hit_tick)
        on(fx, view, hit, foe)
        foe.flinches.append(hit)
        if extra:
            on(fx, extra, hit + tick(1), foe)
        a(tag, tick(ticks) if ticks else None)
        idle_to(start + tick(gap))
        return hit

    # she runs in (move speed 1040: 62 px a second) to 32 px from Garen
    a("run", 900, loop=True, at=14, to=70)
    first = kick(g)
    # Adaptive Defenses: the shield (and its picture) for 120 ticks on the first champion hit
    over.append(Follow(frames_of(fx, "p_shield"), first, 0, 0, loop=True, until=first + tick(120), on=body))
    # Precision Protocol: Q1 (25 ticks, the hit on 8), a plain kick while Q2 charges 90 ticks, the charged Q2 (27, on 9)
    kick(g, "attack_q", 8, 25, "q_hit")
    kick(g)
    kick(g, "attack_q2", 9, 27, "q2_hit")
    # Darius walks up behind, to the back row 58 px ahead of her
    d.walks_in.append((2600, 5600, 128 - d.x))
    # Tactical Sweep: the sweep on tick 22 - the crescent (a line's picture, centred 30 px ahead) and the outer edge
    w0 = t
    sweep = w0 + tick(22)
    over.append(Anim(frames_of(fx, "w_arc"), sweep, spot["x"] + 30, gy))
    on(fx, "w_edge", sweep, g)
    g.flinches.append(sweep)
    g.death = sweep + 120
    a("skill", tick(40))
    # Hookshot at Darius: the claw leaves on tick 9 (5 px over her pivot) at 6 px a tick; the pull at 3.5 px a tick
    e0 = t
    rel = e0 + tick(9)
    sx, sy = spot["x"], gy - 5
    tx, ty = d.pos(rel)
    dist = math.hypot(tx - sx, ty - sy)
    arrive = rel + tick(dist / 6.0)
    over.append(Anim(turned(frames_of(fx, "e_hook"), math.degrees(math.atan2(sy - ty, tx - sx))), rel, sx, sy,
                     until=arrive, x1=tx, y1=ty))
    a("skill2", arrive - e0)
    land_x, land_y = tx - 18, back
    pull = math.hypot(land_x - spot["x"], land_y - gy)
    landed = arrive + tick(pull / 3.5)
    dash = a("skill2_dash", tick(26), loop=True)         # a forced tag loops past its 430 ms
    x0, y0 = spot["x"], gy
    dash.pos = lambda tt, t0=arrive, t1=landed: (
        (int(round(x0 + (land_x - x0) * min(1.0, max(0.0, (tt - t0) / (t1 - t0))))),
         int(round(y0 + (land_y - y0) * min(1.0, max(0.0, (tt - t0) / (t1 - t0)))))))
    spot["x"], spot["y"] = land_x, land_y
    under.append(Anim(frames_of(big, "e_land"), landed, land_x, land_y))
    on(fx, "e_hit", landed, d)
    on(fx, "e_stun", landed, d)
    d.holds.append((landed, landed + tick(30)))
    # The Hextech Ultimatum on Darius: the leap on tick 5 (4 px a tick, onto him), the arena on tick 14, standing
    # pieces every 30 ticks after it while it lasts (180 ticks from the landing), the mark on him from 3 ticks after
    r0 = t
    hop_to = tx - 14
    reach = r0 + tick(5) + tick(max(1.0, (hop_to - land_x) / 4.0))
    ult = a("ult", tick(30))
    ult.pos = lambda tt, t0=r0 + tick(5), t1=reach: (
        int(round(land_x + (hop_to - land_x) * min(1.0, max(0.0, (tt - t0) / (t1 - t0))))), land_y)
    spot["x"] = hop_to
    on_until = reach + tick(180)
    under.append(Anim(frames_of(big, "r_land"), r0 + tick(14), hop_to, land_y))
    k = 1
    while r0 + tick(14 + 30 * k) < on_until:
        under.append(Follow(frames_of(big, "r_zone"), r0 + tick(14 + 30 * k), 0, 0, on=body))
        k += 1
    under.append(OnFoe(frames_of(fx, "r_mark"), reach + tick(3), d, z=-1))
    under[-1].loop, under[-1].until = True, on_until
    # kicks in the arena, 30% faster: each adds R's true damage; Darius walks off, the wall drags him back
    kick(d, gap=KICK_E, extra="r_hit")
    k2 = t
    kick(d, gap=KICK_E, extra="r_hit")
    flee0 = k2 + 333                                   # after the second kick's flinch: 14 px off, 28 from her
    d.flees.append((flee0, flee0 + 400, 14))
    zap = flee0 + 400                                  # past r_leash 25000: a 4-tick Grab back and the wall's zap
    d.slides.append((zap, zap + tick(4), -12))
    on(fx, "r_wall", zap, d)
    last = kick(d, gap=KICK_E, extra="r_hit")
    d.death = last + 120
    idle_to(max(on_until, d.death) + 700)
    end = t

    def place(img, f, px, py):
        img.alpha_composite(f, (px - f.width // 2, py - f.height // 2))

    gaps = [tt for tt in range(0, int(end), step) if not any(an.frame(tt) is not None for an in body)]
    assert not gaps, f"Camille missing at {gaps[:10]} ms"

    frames, tt = [], 0.0
    while tt < end:
        img = Image.new("RGBA", (W, H), ARENA)
        for an in under:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        her = next((an for an in body if an.frame(tt) is not None), None)
        units = [(foe.pos(tt)[1], 0, foe) for foe in (d, g)] + [(her.pos(tt)[1], 1, her)]
        for _, _, u in sorted(units, key=lambda v: (v[0], v[1])):
            place(img, u.frame(tt), *u.pos(tt))
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
                            os.path.join(args.out, "league_camille_frames.png")))
    sp, bp = load(FX), load(BIG)
    print("effects", contact([(sp, t["name"], t["name"]) for t in sp.tags] +
                             [(bp, t["name"], t["name"]) for t in bp.tags],
                             os.path.join(args.out, "league_camille_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_camille_showcase.gif")))


if __name__ == "__main__":
    main()
