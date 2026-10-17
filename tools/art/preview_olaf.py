#!/usr/bin/env python3
"""Preview images for Olaf, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_olaf.py [--out docs/preview] [--only frames|effects|showcase]

  league_olaf_frames.png    every animation, frame by frame, 3x on the arena colour
  league_olaf_effects.png   every effect animation, 3x
  league_olaf_showcase.gif  a scripted fight on Darius with Garen behind him, timed like the kit
                            (tools/kit/build_olaf.py, 60 ticks a second): R - the roar and the rage fire under him; he
                            charges in, Undertow - the axe spinning over Darius (the cut, the frost slow) and sticking
                            in the ground; Reckless Swing's slam; two chops, the first roaring Tough It Out; Darius
                            backs off, Olaf walks over his axe and picks it up; low on health, Berserker Rage; 3x
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
from build_olaf import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_olaf")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_olaf_fx", "league_olaf_big")}
ARC = 14                                        # the lobbed axe's height at mid-flight (px)


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_olaf_fx"], fx["league_olaf_big"]
    W, H = 260, 120
    gy = 92
    x0 = 20
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 130, gy)
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 205, gy)
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        x, y = me.pos(t)
        an = Anim(frames_of(sp, tag), t, x, y, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def hit(foe, tag, when, sheet=None):
        over.append(OnFoe(frames_of(sheet or small, tag), when, foe))
        foe.flinches.append(when)

    a("idle", 400, loop=True)
    # R: the roar; the rage fire burns under him from here on
    r0 = t
    over.append(OnMe(frames_of(big, "r_cast"), r0 + tick(1), me))
    a("ult", tick(P["r_dur"]))
    under.append(OnMe(frames_of(big, "r_on"), r0 + tick(1), me, until=r0 + tick(P["r_t"]) + 4000))
    # he charges in to Undertow's range
    run0 = t
    qx = d.pos(run0)[0] - P["q_range"] // 1000 + 4          # inside Undertow's range
    me.moves.append((run0, run0 + 700, me.pos(run0)[0], qx))
    a("run", 700, loop=True)
    # Q: the axe lobbed at Darius's spot (q_fly ticks), the hidden blade cutting him on the way, stuck there
    q0 = t
    throw = q0 + tick(P["q_at"])
    sx, tx = me.pos(throw)[0] + 8, d.pos(throw)[0]
    fly = tick(P["q_fly"])
    fr = frames_of(small, "q_fly")
    over.append(Anim(fr, throw, sx, gy - 10, until=throw + fly, x1=tx, y1=gy - 10 - ARC))
    hit(d, "q_hit", throw + fly * 0.8)
    over.append(OnFoe(frames_of(small, "q_slow"), throw + fly * 0.8, d, until=throw + fly * 0.8 + tick(P["q_slow_t"])))
    land = throw + fly
    spot = tx
    under.append(Anim(frames_of(small, "q_land"), land, spot, gy))
    a("skill", tick(P["q_dur"]))
    # in to Reckless Swing's range
    c0 = t
    ex = d.pos(c0)[0] - 24
    me.moves.append((c0, c0 + 400, me.pos(c0)[0], ex))
    a("run", 400, loop=True)
    # E: the slam on Darius
    e0 = t
    hit(d, "e_hit", e0 + tick(P["e_st"]), big)
    a("skill2", tick(P["e_dur"]))
    # two chops: the first roars Tough It Out (attack speed, lifesteal, the shield)
    a0 = t
    over.append(OnMe(frames_of(small, "w_cast"), a0 + tick(1), me))
    under.append(OnMe(frames_of(small, "w_on"), a0 + tick(1), me, until=a0 + tick(P["w_t"])))
    for _ in range(2):
        hit(d, "a_hit", t + tick(P["atk_st"]))
        a("attack", tick(P["atk_dur"]))
    # Darius backs off; Olaf walks over his axe and picks it up
    b0 = t
    d.walks.append((b0, b0 + 600, 36))
    me.moves.append((b0 + 100, b0 + 500, me.pos(b0)[0], spot))
    a("idle", 100, loop=True)
    a("run", 400, loop=True)
    pick = t
    over.append(OnMe(frames_of(small, "q_pick"), pick, me))
    when = land + tick(P["axe_step"]) - tick(P["axe_step"])
    while when < pick:
        under.append(Anim(frames_of(small, "q_axe"), when, spot, gy, until=min(pick, when + tick(P["axe_step"]))))
        when += tick(P["axe_step"])
    a("idle", 300, loop=True)
    # low on health: Berserker Rage at its top
    over.append(OnMe(frames_of(small, "p_4"), t, me, until=t + 1600))
    r1 = t
    me.moves.append((r1, r1 + 400, me.pos(r1)[0], d.pos(r1 + 400)[0] - 24))
    a("run", 400, loop=True)
    hit(d, "a_hit", t + tick(P["atk_st"]))
    a("attack", tick(P["atk_dur"]))
    a("idle", 800, loop=True)
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
        units = [(u.pos(tt)[1], u.frame(tt), u.pos(tt)) for u in (g, d)]
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
                                os.path.join(args.out, "league_olaf_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[12:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_olaf_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_olaf_showcase.gif")))


if __name__ == "__main__":
    main()
