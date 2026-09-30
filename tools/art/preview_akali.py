#!/usr/bin/env python3
"""Preview images for Akali, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_akali.py [--out docs/preview]

  league_akali_frames.png    every animation, frame by frame, 3x on the arena colour
  league_akali_effects.png   every effect animation, 3x
  league_akali_showcase.gif  a scripted fight, timed like the kit: Akali runs in and throws Five Point Strike at
                             Darius - the kunai fan hits him, the Assassin's Mark ring opens under his feet and her
                             motes light up; Twilight Shroud (folded into Q) spreads its smoke at her feet and she
                             fades in it; she flings the kama from twice her range, closes in and slashes twice;
                             Shuriken Flip: she flips back, the shuriken hits and marks him, half a second later
                             she dashes in and cuts; the mark again, the long-reach strike; Perfect Execution: she
                             rushes through him, turns, strikes twice more and 2.5 s after the first rush rushes
                             back through him for the execution; 3x
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
from preview_jinx import Follow  # noqa: E402
from preview_yone import OnFoeFor, Path  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_akali")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_akali_fx", "league_akali_big")}
SPEED = 66.0                                          # move speed 1100: 66 px a second
SMOKE_R = 30                                          # the shroud's radius (30000)
FADED = 0.45                                          # her opacity while the smoke hides her


def showcase(out, z=3, step=40):
    akali = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_akali_fx"], fx["league_akali_big"]
    W, H = 280, 112
    gy = 78                                           # the pivot row: the ponytail's tip stands 47 px over the soles
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), 176, gy)
    body, under, over = [], [], []
    t = 0.0
    x = 60
    smoke = []                                        # (t0, t1, x): where the shroud hides her

    def a(tag, dur=None, loop=False, way=None, flip=False):
        nonlocal t
        an = Path(frames_of(akali, tag), t, x, gy, loop=loop, until=(t + dur) if dur else None, way=way or (),
                  flip=flip)
        body.append(an)
        t = an.until

    def run_to(to, flip=False):
        nonlocal x
        dur = abs(to - x) / SPEED * 1000.0
        a("run", dur, loop=True, way=[(t, x), (t + dur, to)], flip=flip)
        x = to

    def fx_at(sp, tag, at, px, py=gy, ground=False, until=None, x1=None, y1=None, loop=None, flip=False):
        an = Anim(frames_of(sp, tag), at, px, py, z=1, loop=(until is not None) if loop is None else loop,
                  until=until, x1=x1, y1=y1, flip=flip)
        (under if ground else over).append(an)
        return an

    ready = []                                        # Assassin's Mark on her: (from, until)

    def mark(at):
        """A skill hit on a champion: the ring opens under him and her motes light up for 4 s (or until used)."""
        under.append(OnFoe(frames_of(small, "p_ring"), at, d, z=-1))
        ready.append([at, at + 4000])

    def use_mark(at):
        for r in ready:
            if r[0] <= at < r[1]:
                r[1] = at

    def strike(foe_hit_tag, anim, dur, hit_tick, flip=False):
        """An attack: the hit on its tick, the foe flinching."""
        hit = t + tick(hit_tick)
        over.append(OnFoe(frames_of(small, foe_hit_tag), hit, d, z=2))
        d.flinches.append(hit)
        a(anim, tick(dur), flip=flip)
        return hit

    # she runs in to Q's range (38000)
    run_to(d.x - 38)
    # Five Point Strike: the fan leaves on tick 10 (a 14-tick line, its view on the line's middle); the cone hits him
    # there; W folded in: a champion within 40000, so the shroud spreads at her feet for 5 s
    q = t
    fan = q + tick(10)
    fx_at(big, "q_fan", fan, x + 22, gy - 6)
    over.append(OnFoe(frames_of(small, "q_hit"), fan, d, z=2))
    d.flinches.append(fan)
    mark(fan)
    fx_at(big, "w_smoke", fan, x, gy, until=fan + 5000, loop=False)
    smoke.append((fan, fan + 5000, x))
    a("skill", tick(25))
    # the long-reach strike: twice her range (48000), the kama flung out, the hit on tick 8
    use_mark(t)
    strike("p_hit", "attack_p", 29, 8)
    a("idle", tick(10), loop=True)
    # in to her range (24000) and two slashes (the hit on tick 7, one every 55 ticks)
    run_to(d.x - 24)
    for _ in range(2):
        strike("hit", "attack", 25, 7)
        a("idle", tick(30), loop=True)
    # Shuriken Flip: back 3000 a tick for 7 ticks from tick 3, the shuriken on tick 14 (6000 a tick), then 30 ticks
    # later the dash to the marked foe (6000 a tick) and the cut
    e = t
    back_to = x - 21
    a("skill2", tick(23), way=[(e + tick(3), x), (e + tick(10), back_to)])
    x = back_to
    throw = e + tick(14)
    hand = (x + 8, gy - 8)
    arrive = throw + tick((d.x - 6 - hand[0]) / 6.0)
    fx_at(small, "e_shuriken", throw, hand[0], hand[1], until=arrive, x1=d.x - 6, y1=gy - 8)
    over.append(OnFoe(frames_of(small, "e_hit"), arrive, d, z=2))
    d.flinches.append(arrive)
    over.append(OnFoeFor(frames_of(small, "e_mark"), arrive, d, arrive + tick(42), z=3))
    mark(arrive)
    a("idle", arrive + tick(30) - t, loop=True)
    dash_to = d.x - 16
    dash_end = t + tick((dash_to - x) / 6.0)
    fx_at(big, "e_dash", t, x, gy)
    over.append(OnFoe(frames_of(small, "e2_hit"), dash_end, d, z=2))
    d.flinches.append(dash_end)
    a("skill2_dash", tick(19), way=[(t, x), (dash_end, dash_to)])
    x = dash_to
    use_mark(t)
    strike("p_hit", "attack_p", 29, 8)
    a("idle", tick(20), loop=True)
    # Perfect Execution: the first rush on tick 2 (8000 a tick for 9 ticks) through him, the passive armed as it ends
    r1 = t
    rush_end = r1 + tick(11)
    through = x + 72
    fx_at(big, "r_dash", r1 + tick(2), x, gy)
    hit1 = r1 + tick(2) + tick((d.x - x) / 8.0)
    over.append(OnFoe(frames_of(small, "r1_hit"), hit1, d, z=2))
    d.flinches.append(hit1)
    a("ult", tick(26), way=[(r1 + tick(2), x), (rush_end, through)])
    x = through
    mark(rush_end)
    # she turns: the long-reach strike from 48000, in again, one slash
    run_to(d.x + 40, flip=True)
    use_mark(t)
    strike("p_hit", "attack_p", 29, 8, flip=True)
    run_to(d.x + 20, flip=True)
    strike("hit", "attack", 25, 7, flip=True)
    a("idle", r1 + 2500 - t, loop=True, flip=True)
    # the execution 2.5 s after the first rush: back through him, the hit where she passes him
    r2 = t
    fx_at(big, "r_dash", r2, x, gy, flip=True)
    back = x - 72
    hit2 = r2 + tick((x - d.x) / 8.0)
    over.append(OnFoe(frames_of(small, "r2_hit"), hit2, d, z=2))
    d.death = hit2 + 60
    a("ult2", tick(19), way=[(r2, x), (r2 + tick(9), back)], flip=True)
    x = back
    a("idle", 1600, loop=True, flip=True)
    end = t
    for r in ready:
        over.append(Follow(frames_of(small, "p_ready"), r[0], x, gy, loop=True, until=r[1], on=body, z=1))

    def faded(f, bx, tt):
        for t0, t1, sx in smoke:
            if t0 <= tt < t1 and abs(bx - sx) <= SMOKE_R:
                g = f.copy()
                g.putalpha(g.getchannel("A").point(lambda v: int(v * FADED)))
                return g
        return f

    def place(img, f, px, py):
        img.alpha_composite(f, (int(px) - f.width // 2, int(py) - f.height // 2))

    frames, tt = [], 0.0
    while tt < end:
        img = Image.new("RGBA", (W, H), ARENA)
        for an in sorted(under, key=lambda o: o.z):
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        units = [(gy, d.frame(tt), d.pos(tt))]
        for an in body:
            f = an.frame(tt)
            if f is not None:
                p = an.pos(tt)
                units.append((gy + 0.5, faded(f, p[0], tt), p))
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
    ap.add_argument("--frames-only", action="store_true", help="only the frames sheet (before the effects exist)")
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    s = load(CHAMP)
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags],
                            os.path.join(args.out, "league_akali_frames.png")))
    if args.frames_only:
        return
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_akali_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_akali_showcase.gif")))


if __name__ == "__main__":
    main()
