#!/usr/bin/env python3
"""Preview images for Karma, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_karma.py [--out docs/preview] [--only frames|effects|showcase]

  league_karma_frames.png    every animation, frame by frame, 3x on the arena colour
  league_karma_effects.png   every effect animation, 3x
  league_karma_showcase.gif  a scripted fight with Darius in front and Garen behind him, timed like the kit
                             (tools/kit/build_karma.py, 60 ticks a second): a spirit bolt, and Inspire shields her
                             (the bubble, the haste at her feet); Inner Flame bursts on Darius (the slow); Focused
                             Resolve tethers him (the beam, the mark, the tether flowing back to her) and roots him;
                             Mantra (the flash, the aura) and the root -> Soulflare combo: the bigger flame, the circle
                             that blows 1.5 s later with Garen walking into it; 3x
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
from build_karma import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_karma")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_karma_fx", "league_karma_big")}
HAND = 12                                        # her palm: px in front of her pivot (the bolts leave there)
BOLT = P["a_speed"] / 1000                       # px a tick
FLAME = P["q_speed"] / 1000
TETHER = 3.0                                     # the tether's segments fly back at 3000 a tick


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_karma_fx"], fx["league_karma_big"]
    W, H = 240, 110
    gy = 76
    x0 = 40
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 70, gy)
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 150, gy)
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

    def fly(tag, when, x1, speed, dy=0):
        sx = me.pos(when)[0] + HAND
        arrive = when + tick(max(1, (x1 - sx) / speed))
        over.append(Anim(frames_of(small, tag), when, sx, gy + dy, until=arrive, x1=x1, y1=gy + dy))
        return arrive

    def inspire(when):
        over.append(OnMe(frames_of(small, "e_land"), when, me))
        over.append(OnMe(frames_of(small, "e_on"), when + 300, me, until=when + tick(P["e_t"])))
        under.append(OnMe(frames_of(small, "e_haste"), when, me, until=when + tick(P["e_ht"])))

    a("idle", 500, loop=True)
    # a spirit bolt; Inspire answers (she is pressed): the shield and the haste on her
    rel = t + tick(P["atk_st"])
    hit(d, "a_hit", fly("a_bolt", rel, d.pos(rel)[0], BOLT, -1))
    a("attack", tick(P["atk_dur"]))
    inspire(t - 100)
    a("skill_e", tick(P["e_anim"] + 8))
    a("idle", 200, loop=True)
    # Inner Flame: it bursts on Darius, the slow at his feet
    rel = t + tick(P["q_st"])
    land = fly("q_ball", rel, d.pos(rel)[0], FLAME, -4)
    over.append(Anim(frames_of(big, "q_boom"), land, d.pos(land)[0], gy))
    hit(d, "q_hit", land)
    under.append(OnFoe(frames_of(small, "q_slow"), land, d, until=land + tick(P["q_slow_t"])))
    a("skill", tick(P["q_dur"]))
    a("idle", 300, loop=True)
    # Focused Resolve: the beam, the mark, the tether flowing back; held, the root
    rel = t + tick(P["w_st"])
    dx = d.pos(rel)[0]
    over.append(Anim(frames_of(small, "w_beam"), rel, me.pos(rel)[0] + HAND, gy - 2, until=rel + tick(1), x1=dx,
                     y1=gy - 2))
    hit(d, "w_hit", rel + tick(1))
    over.append(OnFoe(frames_of(small, "w_mark"), rel + tick(1), d, until=rel + tick(P["w_hold"])))
    for k in range(0, P["w_hold"], 6):
        s = rel + tick(k)
        sx, ex = dx, me.pos(s)[0] + HAND
        over.append(Anim(frames_of(small, "w_tether"), s, sx, gy - 2, until=s + tick((sx - ex) / TETHER), x1=ex,
                         y1=gy - 2))
    snap = rel + tick(P["w_hold"])
    hit(d, "w_snap", snap)
    under.append(OnFoe(frames_of(small, "w_root"), snap, d, until=snap + tick(P["w_root"])))
    d.holds.append((snap, snap + tick(P["w_root"])))
    a("skill2", tick(P["w_dur"]))
    a("idle", 200, loop=True)
    # Mantra just before the root lands: the flash, the aura; the root -> Soulflare combo at the rooted Darius
    t = max(t, snap - tick(P["r_anim"]) - 400)
    r0 = t
    over.append(OnMe(frames_of(small, "r_cast"), r0 + tick(3), me))
    a("ult", tick(P["r_anim"]))
    a("idle", max(0.0, snap - t), loop=True)
    over.append(OnMe(frames_of(small, "mantra"), r0 + tick(6), me, until=t))
    rel = t + tick(P["q_st"])
    land = fly("rq_ball", rel, d.pos(rel)[0], FLAME, -4)
    over.append(Anim(frames_of(big, "rq_boom"), land, d.pos(land)[0], gy))
    hit(d, "q_hit", land)
    fx_ = d.pos(land)[0]
    under.append(Anim(frames_of(big, "rq_field"), land, fx_, gy))
    blast = land + tick(P["rq_wait"] - 4)
    over.append(Anim(frames_of(big, "rq_blast"), blast, fx_, gy))
    for foe in (d,):
        hit(foe, "q_hit", blast + tick(4))
        under.append(OnFoe(frames_of(small, "rq_slow"), blast + tick(4), foe, until=blast + tick(4 + P["rq_slow_t"])))
    a("skill", tick(P["q_dur"]))
    a("idle", blast + 1200 - t, loop=True)
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
                                os.path.join(args.out, "league_karma_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_karma_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_karma_showcase.gif")))


if __name__ == "__main__":
    main()
