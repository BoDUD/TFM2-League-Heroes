#!/usr/bin/env python3
"""Preview images for Syndra, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_syndra.py [--out docs/preview] [--only frames|effects|showcase]

  league_syndra_frames.png    every animation, frame by frame, 3x on the arena colour
  league_syndra_effects.png   every effect animation, 3x
  league_syndra_showcase.gif  a scripted fight beside Jinx against Darius with Garen behind him, timed like the kit
                              (tools/kit/build_syndra.py, 60 ticks a second): a dark bolt on Darius; Q - the sphere
                              forming under Darius, its blast, the sphere left floating there; W -> E - a sphere
                              thrown at Darius (both slowed, a second sphere where it lands), then the wave pushing
                              out from her: both knocked back and the spheres stunning them; she glides past them,
                              turns round - facing left from here, as on the red side - and casts R: the spheres
                              gather round her and 3 + 2 fly at Darius one after another; the Transcendent light; 3x
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
from build_syndra import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_syndra")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_syndra_fx", "league_syndra_big")}
HAND = 7                                          # her right hand at the release, px ahead of the pivot
SHOT_Y = -P["bolt_y"] // 1000 + 5                 # the bolt and the spheres fly this far over the pivot (5000 - y_offset)
BOLT = P["bolt_speed"] / 1000                     # px a tick
RSPEED = P["r_speed"] / 1000


def flipped(fr):
    return [(f.transpose(Image.FLIP_LEFT_RIGHT), ms) for f, ms in fr]


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_syndra_fx"], fx["league_syndra_big"]
    W, H = 330, 112
    gy = 88
    x0 = 70
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 60, gy)       # her attack range
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 84, gy)        # beside Darius, in reach
    jinx = Held(load(os.path.join(LEAGUE, "champions", "league_jinx")), x0 - 34, gy)      # her ally, behind her
    jinx.mirrored = False
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0
    face = [False]

    def a(tag, dur=None, loop=False):
        nonlocal t
        x, y = me.pos(t)
        an = Anim(frames_of(sp, tag), t, x, y, loop=loop, until=(t + dur) if dur else None, flip=face[0])
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def hit(foe, tag, when, sheet=None):
        over.append(OnFoe(frames_of(sheet or small, tag), when, foe))
        foe.flinches.append(when)

    def shot(tag, rel, speed, foe, hit_tag, left=False):
        hand = -HAND if left else HAND
        sx = me.pos(rel)[0] + hand
        arrive = rel + tick(max(1, abs(foe.pos(rel)[0] - sx) / speed))
        fr = frames_of(small, tag)
        over.append(Anim(flipped(fr) if left else fr, rel, sx, gy - SHOT_Y, until=arrive, x1=foe.pos(rel)[0],
                         y1=gy - SHOT_Y))
        hit(foe, hit_tag, arrive)
        return arrive

    spheres = []

    def sphere(x, when):
        """A Dark Sphere resting on its point for orb_t ticks (its picture plays once over those 6 s)."""
        over.append(Anim(frames_of(big, "orb"), when, x, gy + 11))
        spheres.append((x, when))

    a("idle", 500, loop=True)
    shot("a_bolt", t + tick(P["a_st"]), BOLT, d, "a_hit")
    a("attack", tick(P["atk_dur"]))
    a("idle", 300, loop=True)
    # Q: the sphere forms under Darius, falls, blasts him and Garen, and stays
    rel = t + tick(P["q_rel"])
    qx = d.pos(rel)[0]
    under.append(Anim(frames_of(big, "q_form"), rel, qx, gy + 11, until=rel + tick(P["q_fall"])))
    land = rel + tick(P["q_fall"])
    under.append(Anim(frames_of(big, "q_blast"), land, qx, gy + 11))
    for foe in (d, g):
        hit(foe, "q_hit", land + tick(1))
    sphere(qx, land)
    a("skill", tick(P["q_anim"]))
    a("idle", 500, loop=True)
    # W -> E: a sphere thrown at Darius (a lob), the slam and the slow, then the wave from her: knocked back, stunned
    w0 = t
    throw = w0 + tick(P["w_rel"])
    wx = d.pos(throw)[0] - 4
    sx = me.pos(throw)[0] + HAND
    over.append(Anim(frames_of(small, "w_throw"), throw, sx, gy - SHOT_Y, until=throw + tick(P["w_fly"]), x1=wx,
                     y1=gy))
    slam = throw + tick(P["w_fly"])
    under.append(Anim(frames_of(big, "w_land"), slam, wx, gy + 11))
    for foe in (d, g):
        hit(foe, "w_hit", slam + tick(1))
        under.append(OnFoe(frames_of(small, "w_slow"), slam, foe, until=slam + tick(P["w_slow_t"])))
    sphere(wx, slam)
    wave = w0 + tick(P["e_gap"] + P["e_rel"])
    under.append(Anim(frames_of(big, "e_wave"), wave, me.pos(wave)[0], gy))
    for foe in (d, g):
        hit(foe, "e_hit", wave + tick(1))
    stun = wave + tick(P["e_fly"] + 1)
    for foe in (d, g):
        over.append(OnFoe(frames_of(small, "e_stun"), stun, foe))
        foe.holds.append((stun, stun + tick(P["e_stun"])))
    a("skill2", tick(P["e_gap"]))
    a("skill2_e", tick(P["e_anim"]))
    a("idle", max(0, stun + tick(P["e_stun"]) - t), loop=True)
    # she glides past them and turns round (the red side's facing): R - the spheres gather, 3 + 2 fly at Darius
    walk_to = g.pos(t)[0] + 66
    me.moves.append((t, t + 900, me.pos(t)[0], walk_to))
    a("run", 900, loop=True)
    face[0] = True
    over.append(OnMe(frames_of(big, "r_cast"), t, me))
    rel = t + tick(P["r_rel"])
    for k in range(3 + len(spheres)):
        shot("r_orb", rel + tick(k * P["r_gap"]), RSPEED, d, "r_hit", left=True)
    a("ult", tick(P["r_anim"]))
    a("idle", 1300, loop=True)
    over.append(OnMe(frames_of(small, "evo"), t - 600, me))
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
        units = [(u.pos(tt)[1], u.frame(tt), u.pos(tt)) for u in (g, d, jinx)]
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
                                os.path.join(args.out, "league_syndra_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_syndra_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_syndra_showcase.gif")))


if __name__ == "__main__":
    main()
