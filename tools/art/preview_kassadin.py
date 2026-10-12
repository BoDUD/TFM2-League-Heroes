#!/usr/bin/env python3
"""Preview images for Kassadin, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_kassadin.py [--out docs/preview] [--only frames|effects|showcase]

  league_kassadin_frames.png    every animation's dense frames (hd_, PPU 3.622, as league.dll shows them)
  league_kassadin_effects.png   every effect animation, 3x
  league_kassadin_showcase.gif  a scripted fight with Darius in front and Garen behind him, timed like the kit
                                (tools/kit/build_kassadin.py, 60 ticks a second): a claw swipe; Nether Blade's strike;
                                Null Sphere - the orb, its burst on Darius and his shield; Force Pulse - the cone of
                                waves, Darius slowed; the E -> Q combo silencing him; Riftwalk - the rift where he
                                stood, the landing by Garen in the back line and its blast; 3x
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
from preview_dense import dense, dense_rows, put  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_pyke import Me, OnFoe, OnMe  # noqa: E402
from build_kassadin import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_kassadin")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_kassadin_fx", "league_kassadin_big")}
HAND = 10                                        # his blade hand: px in front of his pivot (the orb leaves there)
ORB = P["q_speed"] / 1000                        # px a tick
CONE = P["e_r"] / 1000                           # the cone's picture spans him to e_r ahead: its middle e_r / 2 out


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_kassadin_fx"], fx["league_kassadin_big"]
    W, H = 250, 110
    gy = 80
    x0 = 50
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 26, gy)      # in his swipe's reach
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 120, gy)      # the back line
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        x, y = me.pos(t)
        an = Anim(dense(sp, tag, "kassadin", z), t, x, y, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def hit(foe, tag, when, sheet=None):
        over.append(OnFoe(frames_of(sheet or small, tag), when, foe))
        foe.flinches.append(when)

    a("idle", 500, loop=True)
    # a claw swipe, then Nether Blade's strike
    hit(d, "a_hit", t + tick(P["a_st"]))
    a("attack", tick(P["atk_dur"]))
    a("idle", 250, loop=True)
    hit(d, "w_hit", t + tick(P["a_st"]))
    a("attack_w", tick(P["atk_dur"]))
    a("idle", 300, loop=True)
    # Null Sphere: the orb to Darius, its burst; the shield round him from the cast
    rel = t + tick(P["q_at"])
    sx = me.pos(rel)[0] + HAND
    arrive = rel + tick(max(1, (d.pos(rel)[0] - sx) / ORB))
    over.append(Anim(frames_of(small, "q_orb"), rel, sx, gy - 12, until=arrive, x1=d.pos(rel)[0], y1=gy - 12))
    hit(d, "q_hit", arrive)
    over.append(OnMe(frames_of(small, "q_shield"), rel, me))
    a("skill", tick(P["q_dur"]))
    a("idle", 400, loop=True)
    # Force Pulse: the cone of waves from him toward Darius, who is slowed
    rel = t + tick(P["e_at"])
    over.append(Anim(frames_of(big, "e_cone"), rel, me.pos(rel)[0] + CONE / 2, gy))
    hit(d, "e_hit", rel + tick(3))
    under.append(OnFoe(frames_of(small, "e_slow"), rel + tick(3), d, until=rel + tick(3 + P["e_slow_t"])))
    a("skill2", tick(P["e_dur"]))
    # the combo E -> Q: the orb silences him
    rel = t + tick(P["q_at"])
    sx = me.pos(rel)[0] + HAND
    arrive = rel + tick(max(1, (d.pos(rel)[0] - sx) / ORB))
    over.append(Anim(frames_of(small, "q_orb"), rel, sx, gy - 12, until=arrive, x1=d.pos(rel)[0], y1=gy - 12))
    hit(d, "q_hit", arrive)
    over.append(OnFoe(frames_of(small, "q_sil"), arrive, d, until=arrive + tick(P["q_sil"])))
    over.append(OnMe(frames_of(small, "q_shield"), rel, me))
    a("skill", tick(P["q_dur"]))
    a("idle", 500, loop=True)
    # Riftwalk: the rift where he stood, then he stands by Garen in the back line, the blast round him
    r0 = t
    go = r0 + tick(P["r_at"] - 1)
    old = me.pos(go)[0]
    land_x = g.pos(go)[0] - 6
    over.append(Anim(frames_of(big, "r_out"), go, old, gy))
    me.moves.append((go, go + 1, old, land_x))
    over.append(Anim(frames_of(big, "r_in"), go, land_x, gy))
    hit(g, "r_hit", go + tick(1))
    a("ult", tick(P["r_dur"]))
    a("idle", 300, loop=True)
    # and the swipe on Garen
    hit(g, "a_hit", t + tick(P["a_st"]))
    a("attack", tick(P["atk_dur"]))
    a("idle", 700, loop=True)
    end = t

    def place(img, f, px, py):
        put(img, f, px, py, z)

    frames, tt = [], 0.0
    while tt < end:
        img = Image.new("RGBA", (W * z, H * z), ARENA)
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
        frames.append(img.convert("RGB"))
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_kassadin_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[16:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_kassadin_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_kassadin_showcase.gif")))


if __name__ == "__main__":
    main()
