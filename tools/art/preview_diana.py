#!/usr/bin/env python3
"""Preview images for Diana, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_diana.py [--out docs/preview]

  league_diana_frames.png    every animation, frame by frame, 3x on the arena colour
  league_diana_effects.png   every effect animation, 3x
  league_diana_showcase.gif  a scripted fight, timed like the kit: Diana runs in and throws Crescent Strike - the
                             crescent passes through Darius and leaves Moonlight over his head; Lunar Rush onto him:
                             on landing Pale Cascade's three orbs circle her and her shield comes up, and with
                             Moonlight up she dashes again at once, onto Garen walking in behind him; the orbs burst
                             on them one by one; two attacks on Garen and the third, the cleave, sweeps him; Moonfall
                             draws both to her (Darius from behind) and slows them, and a second later the full moon
                             crashes on her and finishes Darius; 3x
"""
import argparse
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from preview_annie import OnFoe  # noqa: E402
from preview_ashe import Anim, tick  # noqa: E402
from preview_briar import Prey  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_jinx import Follow  # noqa: E402
from preview_yone import OnFoeFor, Path  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_diana")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_diana_fx", "league_diana_big")}


def showcase(out, z=3, step=40):
    diana = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_diana_fx"], fx["league_diana_big"]
    W, H = 300, 170
    gy = 128                                          # the pivot row: the moon falls from 128 px over her feet
    d = Prey(load(os.path.join(LEAGUE, "champions", "league_darius")), 150, gy)
    g = Prey(load(os.path.join(LEAGUE, "champions", "league_garen")), 345, gy + 6)     # off the right edge
    body, under, over = [], [], []
    t = 0.0
    x = 30

    def a(tag, dur=None, loop=False, at=None, way=None):
        nonlocal t
        an = Path(frames_of(diana, tag), t, at if at is not None else x, gy, loop=loop,
                  until=(t + dur) if dur else None, way=way or ())
        body.append(an)
        t = an.until

    def fx_at(sp, tag, at, px, py=gy, ground=False, until=None, x1=None, y1=None, loop=None, flip=False):
        an = Anim(frames_of(sp, tag), at, px, py, z=-1 if ground else 1,
                  loop=(until is not None) if loop is None else loop, until=until, x1=x1, y1=y1, flip=flip)
        (under if ground else over).append(an)
        return an

    def on_her(sp, tag, t0, until=None, loop=False, z=1):
        (under if z < 0 else over).append(Follow(frames_of(sp, tag), t0, x, gy, loop=loop, until=until, on=body, z=z))

    # she runs in (move speed 1100: 66 px a second)
    a("run", 1100, loop=True, way=[(0, x), (1100, 102)])
    x = 102
    # Crescent Strike: released on tick 11, the crescent flies 6 px a tick through Darius, 65 px in all
    start = t
    rel = start + tick(11)
    fx_at(small, "q_bolt", rel, x + 6, gy - 5, until=rel + tick(65 / 6.0), x1=x + 71, y1=gy - 5)
    hit = rel + tick((d.x - x - 6) / 6.0)
    over.append(OnFoe(frames_of(small, "q_hit"), hit, d, z=2))
    d.flinches.append(hit)
    over.append(OnFoeFor(frames_of(small, "moon_mark"), hit, d, hit + 3000, z=3))
    a("skill", tick(28))
    a("idle", tick(10), loop=True)
    # Lunar Rush onto Darius (4 px a tick), Pale Cascade on landing; Moonlight: again 8 ticks later, onto Garen
    g.moves.append((t - 900, t + 400, -125, 0))                  # Garen walks in behind Darius
    start = t
    to = d.x - 22
    land = start + tick(2 + (to - x) / 4.0)
    a("skill2", land - start, way=[(start + tick(2), x), (land, to)])
    x = to
    over.append(OnFoe(frames_of(small, "e_hit"), land, d, z=-1))
    d.flinches.append(land)
    on_her(small, "w_cast", land, z=-1)
    shield_end = land + 5000
    on_her(small, "w_shield", land, until=shield_end, loop=True, z=-1)
    again = land + tick(8)
    a("skill2_w", again - t)
    gx = g.pos(again)[0]
    to2 = gx - 20
    land2 = again + tick(max(1, (to2 - x) / 4.0))
    a("skill2", land2 - again, way=[(again, x), (land2, to2)])
    x = to2
    over.append(OnFoe(frames_of(small, "e_hit"), land2, g, z=-1))
    g.flinches.append(land2)
    # the orbs: 3 then 2 then 1 circling her, one bursting every 15 ticks from 6 ticks after the first landing
    orb_t = [land + tick(6 + 15 * k) for k in range(3)]
    for k, (t0, t1) in enumerate(zip([land] + orb_t[:2], orb_t)):
        on_her(small, f"w_orb{3 - k}", t0, until=t1, loop=True)
    for k, t0 in enumerate(orb_t):
        foe = d if k == 0 else g                   # the first while she still stands at Darius
        fx_at(small, "w_orb", t0, x, gy - 5, until=t0 + tick(4), x1=foe.pos(t0)[0], y1=gy - 5,
              flip=foe.pos(t0)[0] < x)
        over.append(OnFoe(frames_of(small, "w_boom"), t0 + tick(4), foe, z=2))
        foe.flinches.append(t0 + tick(4))
    a("idle", max(tick(4), orb_t[-1] + tick(4) - t), loop=True)
    # two attacks (the hit on tick 11) and the third, the cleave on tick 14 round the target (Garen and Darius)
    for k in range(3):
        if k < 2:
            h = t + tick(11)
            over.append(OnFoe(frames_of(small, "hit"), h, g, z=2))      # her target: Garen, in front
            g.flinches.append(h)
            a("attack", tick(26))
        else:
            h = t + tick(14)
            fx_at(big, "p_cleave", h, x, gy)
            over.append(OnFoe(frames_of(small, "p_hit"), h, g, z=2))    # Darius stands behind her, out of it
            g.flinches.append(h)
            a("attack_p", tick(28))
        a("idle", tick(12), loop=True)
    # Moonfall: the pull on tick 16 (2.5 px a tick into her), the moon falls from tick 56 and crashes on tick 76
    start = t
    pull = start + tick(16)
    fx_at(big, "r_draw", pull, x, gy, ground=True)
    for foe in (d, g):
        fx0 = foe.pos(pull)[0]
        dist = fx0 - x - (14 if fx0 > x else -14)
        foe.slides.append((pull, pull + tick(abs(dist) / 2.5), -dist))
    a("ult", tick(40))
    moon = pull + tick(40)
    on_her(big, "r_moon", moon)
    crash = pull + tick(60)
    for foe in (d, g):
        over.append(OnFoe(frames_of(small, "r_hit"), crash, foe, z=2))
        foe.flinches.append(crash)
    d.death = crash + 200
    a("idle", crash + 1600 - t, loop=True)
    end = t

    def place(img, f, px, py):
        img.alpha_composite(f, (int(px) - f.width // 2, int(py) - f.height // 2))

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
                units.append((gy, f, an.pos(tt)))
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
                            os.path.join(args.out, "league_diana_frames.png")))
    if args.frames_only:
        return
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_diana_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_diana_showcase.gif")))


if __name__ == "__main__":
    main()
