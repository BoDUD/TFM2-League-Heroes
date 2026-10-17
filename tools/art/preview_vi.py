#!/usr/bin/env python3
"""Preview images for Vi, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_vi.py [--out docs/preview]

  league_vi_frames.png    every animation, frame by frame, 3x on the arena colour
  league_vi_effects.png   every effect animation, 3x
  league_vi_showcase.gif  a scripted fight against Darius and Garen (behind him), timed like the kit: she runs in;
                          Vault Breaker: the half-second charge glowing in the gauntlet pulled back by her hip, the dash
                          (dust where she leaves) that stops on Darius and knocks him back; Blast Shield lights round
                          her; Relentless Force punches at once (the Q -> E combo): the shock wave through Darius into
                          Garen behind him; three punches, the third Denting Blows (the blue arcs); Cease and Desist on
                          Garen: the launch burst, the charge with its trail through Darius (knocked aside, stunned),
                          the uppercut throws Garen up (the column), the slam cracks the ground, and the landing's free
                          E punch; 3x
Distances in px (1000 distance units a px): Q dashes 4 px a tick for 12 ticks, R 4 px a tick.
"""
import argparse
import math
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from preview_annie import OnFoe  # noqa: E402
from preview_ashe import Anim, tick  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_jinx import Follow  # noqa: E402
from preview_leesin import Foe  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_vi")
FX = os.path.join(LEAGUE, "effects", "league_vi_fx")
Q_SPEED, R_SPEED = 4.0, 4.0
WAVE = 68                                   # the E wave's line, px (league_vi_e_wave)
ATK_HIT, ATK_DUR, ATK_CD = 10, 24, 60


class Stunnable(Foe):
    """A foe that can also be held still (stunned or in the air: its first hit frame)."""

    def __init__(self, sp, x, y):
        super().__init__(sp, x, y)
        self.holds = []

    def frame(self, t):
        if self.death is None or t < self.death:
            for t0, t1 in self.holds:
                if t0 <= t < t1:
                    return self.flip(self.hit[0][0])
        return super().frame(t)


def showcase(out, z=3, step=40):
    vi = load(CHAMP)
    fx = load(FX)
    W, H = 300, 150
    gy = 112                                           # her pivot row: the uppercut's fist rises 41 px over it
    x = 14
    d = Stunnable(load(os.path.join(LEAGUE, "champions", "league_darius")), 150, gy)
    g = Stunnable(load(os.path.join(LEAGUE, "champions", "league_garen")), 196, gy - 4)    # just behind him
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False, to=None):
        nonlocal t, x
        an = Anim(frames_of(vi, tag), t, x, gy, loop=loop, until=(t + dur) if dur else None, x1=to)
        body.append(an)
        t = an.until
        if to is not None:
            x = to
        return an

    def idle_to(at):
        if at > t:
            a("idle", at - t, loop=True)

    def on_her(tag, at, until=None, behind=False):
        """A CasterViewEffect with is_follow: it rides her pivot."""
        an = Follow(frames_of(fx, tag), at, x, gy, on=body)
        if until is not None:
            an.loop, an.until = True, until
        (under if behind else over).append(an)
        return an

    def ground(tag, at, px, py=None):
        under.append(Anim(frames_of(fx, tag), at, px, gy if py is None else py))

    def on(foe, tag, at):
        over.append(OnFoe(frames_of(fx, tag), at, foe, z=2))

    def line(tag, at, foe, length=WAVE):
        """A view-only line's picture (league_vi_e_wave): centred on the line from her pivot toward the foe, turned to it."""
        fx_, fy = foe.pos(at)
        ang = math.atan2(fy - gy, fx_ - x)
        frames = [(f.rotate(-math.degrees(ang), resample=Image.NEAREST, expand=True) if abs(ang) > 1e-6 else f, ms)
                  for f, ms in frames_of(fx, tag)]
        over.append(Anim(frames, at, int(round(x + length / 2 * math.cos(ang))), int(round(gy + length / 2 * math.sin(ang)))))

    def punch(foe, cd=ATK_CD, e=False, behind=None):
        """An attack (or E's punch): the hit on tick 10 of the 24-tick action; the next one cd ticks later."""
        start = t
        land = start + tick(ATK_HIT)
        if e:
            line("e_wave", land - tick(1), foe)
            for f in [foe] + ([behind] if behind else []):
                on(f, "e_hit", land)
                f.flinches.append(land)
        else:
            on(foe, "hit", land)
            foe.flinches.append(land)
        a("attack_e" if e else "attack", tick(ATK_DUR))
        return start + tick(cd), land

    # she runs in (move speed 1050: 63 px a second) to Vault Breaker's reach of Darius
    a("run", 900, loop=True, to=x + 56)
    # Vault Breaker: the 30-tick charge (the gauntlet pulled back, its glow), then the dash, 4 px a tick, stopping on
    # the first champion: Darius, knocked back 2 px a tick for 10 ticks; the shield (3 s) and the Q -> E punch
    a("skill", tick(30))
    on_her("q_charge", t - tick(30))
    ground("q_go", t, x)
    stop = d.x - 22
    dash_ms = tick(max(1.0, (stop - x) / Q_SPEED))
    a("skill_dash", dash_ms, loop=True, to=stop)
    hit = t
    on(d, "q_stop", hit)
    on(d, "q_hit", hit)
    d.flinches.append(hit)
    d.slides.append((hit, hit + tick(10), 20))
    g.slides.append((hit, hit + tick(10), 8))                    # Garen steps back with him
    on_her("bs_on", hit)
    # Relentless Force at once (the Q -> E combo): she steps up, the next punch is the cone through both
    a("run", 260, loop=True, to=x + 14)
    nxt, land = punch(d, e=True, behind=g)
    idle_to(nxt)
    # three punches: the third is Denting Blows
    for k in range(3):
        nxt, land = punch(d)
        if k == 2:
            on(d, "w_proc", land)
        idle_to(nxt)
    idle_to(t + 300)
    # Cease and Desist on Garen: the 8-tick launch (the burst at her feet), unstoppable she charges with the trail,
    # through Darius (knocked aside and stunned 0.75 s), then the uppercut: Garen up for 1.25 s, the column, the slam
    r0 = t
    on_her("r_cast", r0)
    a("ult", tick(8))
    gx, _ = g.pos(t)
    to = gx - 18
    fly = tick(max(1.0, (to - x) / R_SPEED))
    on_her("r_trail", r0, until=t + fly, behind=True)          # from the ult's first tick (empty for the 7 ticks
                                                               # before the dash), looping behind her until she arrives
    passed = t + fly * max(0.0, min(1.0, (d.pos(t)[0] - 10 - x) / max(1.0, to - x)))
    on(d, "r_side", passed)
    d.flinches.append(passed)
    d.holds.append((passed, passed + tick(45)))
    d.slides.append((passed, passed + tick(4), -6))
    a("ult_dash", fly, loop=True, to=to)
    landed = t
    on(g, "r_hit", landed)
    g.holds.append((landed, landed + tick(75)))
    g.hops.append((landed, landed + tick(75), 18))
    ground("r_slam", landed + tick(10), x + 6)
    a("ult_slam", tick(20))
    # the landing arms a free E punch (the R -> E combo)
    nxt, land = punch(g, e=True)
    idle_to(nxt + 400)
    end = t

    def place(img, f, px, py):
        img.alpha_composite(f, (px - f.width // 2, py - f.height // 2))

    frames, tt = [], 0.0
    order = sorted((d, g), key=lambda f: f.y)                  # the one further back first
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
    sample = frames[::6]                                       # one palette for the whole clip
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
                            os.path.join(args.out, "league_vi_frames.png")))
    sp = load(FX)
    print("effects", contact([(sp, t["name"], t["name"]) for t in sp.tags],
                             os.path.join(args.out, "league_vi_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_vi_showcase.gif")))


if __name__ == "__main__":
    main()
