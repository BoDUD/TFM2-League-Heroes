#!/usr/bin/env python3
"""Preview images for Lillia, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_lillia.py [--out docs/preview] [--only frames|effects|showcase]

  league_lillia_frames.png    every animation, frame by frame, 3x on the arena colour
  league_lillia_effects.png   every effect animation, 3x
  league_lillia_showcase.gif  a scripted fight against Darius with Garen behind him, timed like the kit
                              (tools/kit/build_lillia.py, 60 ticks a second): she trots in and swings her bough at
                              Darius; Q: the blooming ring opens round her feet and hits both, petals rise under
                              her hooves (Prance); E: the swirlseed lobbed from the bough's tip bursts on Darius
                              (the dream mist slows him); W: she rears, the warning circle round Darius, the slam -
                              the sweet spot's gold burst on Darius, the plain hit on Garen; she trots past them and
                              turns round - facing left from here, as on the red side - and R: the lullaby's dream
                              ribbons round her, both drowsy, then asleep (the bubbles); her swing wakes Garen
                              (the pop); 3x
"""
import argparse
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
from preview_annie import Held  # noqa: E402
from preview_ashe import Anim, tick  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_pyke import Me, OnFoe, OnMe  # noqa: E402
from build_lillia import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_lillia")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_lillia_fx", "league_lillia_big")}
TIP = (25, -32)                                  # the bough's tip at E's release, px from the pivot


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_lillia_fx"], fx["league_lillia_big"]
    W, H = 360, 150
    gy = 108
    x0 = 130
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 46, gy)
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 86, gy)
    me = Me(x0 - 90, gy)
    body, under, over = [], [], []
    t = 0.0
    face = [False]

    def a(tag, dur=None, loop=False):
        nonlocal t
        x, y = me.pos(t)
        an = Anim(frames_of(sp, tag), t, x, y, loop=loop, until=(t + dur) if dur is not None else None, flip=face[0])
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def hit(foe, tag, when, sheet=None):
        over.append(OnFoe(frames_of(sheet or small, tag), when, foe))
        foe.flinches.append(when)

    def strip_ms(tag):
        return sum(ms for _, ms in frames_of(sp, tag))

    # she trots in and swings at Darius twice
    me.moves.append((t, t + 700, me.pos(t)[0], x0))
    a("run", 700, loop=True)
    for _ in range(2):
        hit(d, "a_hit", t + tick(P["a_st"]))
        a("attack", strip_ms("attack"))
        a("idle", tick(25), loop=True)
    # Q: the ring opens round her feet, both hit at q_st; Prance from the first hit
    q0 = t
    under.append(OnMe(frames_of(big, "q_spin"), q0, me))
    for foe in (d, g):
        hit(foe, "q_hit", q0 + tick(P["q_st"]))
    prance = q0 + tick(P["q_st"])
    a("skill", strip_ms("skill"))
    a("idle", 200, loop=True)
    # E: the seed lobbed from the bough's tip onto Darius, the burst and his slow
    e0 = t
    rel = e0 + tick(P["e_rel"])
    land = rel + tick(P["e_travel"])
    hx, hy = me.pos(rel)[0] + TIP[0], gy + TIP[1]
    cx = d.pos(land)[0]
    up = (hx + cx) // 2
    over.append(Anim(frames_of(small, "e_seed"), rel, hx, hy, until=(rel + land) / 2, x1=up, y1=gy - 50))
    over.append(Anim(frames_of(small, "e_seed"), (rel + land) / 2, up, gy - 50, until=land, x1=cx, y1=gy - 6))
    under.append(OnFoe(frames_of(small, "e_land"), land, d))
    hit(d, "e_hit", land)
    under.append(OnFoe(frames_of(small, "e_slow"), land, d, until=land + tick(P["e_slow_t"])))
    a("skill2", strip_ms("skill2"))
    # W: she rears, the circle round Darius for w_wind ticks, the slam on its centre
    w0 = t
    under.append(OnFoe(frames_of(big, "w_mark"), w0, d))
    slam = w0 + tick(P["w_wind"])
    under.append(OnFoe(frames_of(big, "w_land"), slam, d))
    hit(d, "w_sweet", slam)
    hit(g, "w_hit", slam)
    a("skill2_w", strip_ms("skill2_w"))
    a("idle", 250, loop=True)
    # she trots past them and turns round (the red side's facing): R
    me.moves.append((t, t + 900, me.pos(t)[0], g.pos(t)[0] + 70))
    a("run", 900, loop=True)
    face[0] = True
    r0 = t
    over.append(OnMe(frames_of(big, "r_cast"), r0 + tick(P["r_rel"]), me))
    drowsy = r0 + tick(P["r_rel"])
    asleep = drowsy + tick(P["r_drowsy"])
    wake_at = asleep + 900
    for foe, end in ((g, wake_at), (d, asleep + tick(P["r_sleep"]))):
        over.append(OnFoe(frames_of(small, "drowsy"), drowsy, foe, until=asleep))
        over.append(OnFoe(frames_of(small, "sleep"), asleep, foe, until=end))
        foe.holds.append((asleep, end))
    a("ult", strip_ms("ult"))
    a("idle", asleep - t + 500, loop=True)
    # her swing wakes Garen, the nearer one: the pop
    me.moves.append((t, t + 500, me.pos(t)[0], g.pos(t)[0] + 30))
    a("run", 500, loop=True)
    a("idle", max(40.0, wake_at - tick(P["a_st"]) - t), loop=True)
    a("attack", strip_ms("attack"))
    hit(g, "a_hit", wake_at)
    over.append(OnFoe(frames_of(small, "wake"), wake_at, g))
    a("idle", 700, loop=True)
    under.append(OnMe(frames_of(small, "prance"), prance, me, until=t))
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
                units.append((an.pos(tt)[1] + 0.5, f, an.pos(tt)))
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
                                os.path.join(args.out, "league_lillia_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_lillia_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_lillia_showcase.gif")))


if __name__ == "__main__":
    main()
