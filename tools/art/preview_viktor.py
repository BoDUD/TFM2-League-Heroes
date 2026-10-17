#!/usr/bin/env python3
"""Preview images for Viktor, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_viktor.py [--out docs/preview] [--only frames|effects|showcase]

  league_viktor_frames.png    every animation, frame by frame, 3x on the arena colour
  league_viktor_effects.png   every effect animation, 3x
  league_viktor_showcase.gif  a scripted fight beside Jinx against Darius with Garen behind him, timed like the kit
                              (tools/kit/build_viktor.py, 60 ticks a second): an arcane bolt on Darius; Q - the hextech
                              bolt, the shield lighting up round him and the sparks of the charge, then the charged
                              attack; W -> E - the gravity field under Darius (both slowed), the ray from Darius on
                              through Garen, the aftershock a second later, the field's burst stunning both; he walks
                              past them, turns round - facing left from here, as on the red side - and casts R: the
                              storm falls on Darius and strikes once a second; the evolution's gold light; 3x
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
from build_viktor import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_viktor")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_viktor_fx", "league_viktor_big")}
HAND = 18                                        # his far hand at the release, px ahead of the pivot
BOLT_Y = -P["bolt_y"] // 1000 + 5                # the bolts fly this far over the pivot (5000 - y_offset)
BOLT = P["bolt_speed"] / 1000                    # px a tick
QBOLT = P["q_speed"] / 1000


def flipped(fr):
    return [(f.transpose(Image.FLIP_LEFT_RIGHT), ms) for f, ms in fr]


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_viktor_fx"], fx["league_viktor_big"]
    W, H = 330, 112
    gy = 88
    x0 = 70
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 60, gy)       # his attack range
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 92, gy)        # behind Darius, in line
    jinx = Held(load(os.path.join(LEAGUE, "champions", "league_jinx")), x0 - 34, gy)      # his ally, behind him
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

    def bolt(tag, rel, speed, foe, hit_tag):
        sx = me.pos(rel)[0] + HAND
        arrive = rel + tick(max(1, (foe.pos(rel)[0] - sx) / speed))
        over.append(Anim(frames_of(small, tag), rel, sx, gy - BOLT_Y, until=arrive, x1=foe.pos(rel)[0],
                         y1=gy - BOLT_Y))
        hit(foe, hit_tag, arrive)

    a("idle", 500, loop=True)
    bolt("a_bolt", t + tick(P["a_st"]), BOLT, d, "a_hit")
    a("attack", tick(P["atk_dur"]))
    a("idle", 300, loop=True)
    # Q: the bolt, the shield and the charge, then the charged attack
    rel = t + tick(P["q_rel"])
    bolt("q_bolt", rel, QBOLT, d, "q_hit")
    landed = rel + tick((d.pos(rel)[0] - me.pos(rel)[0] - HAND) / QBOLT)
    over.append(OnMe(frames_of(small, "q_shield"), landed, me))
    charge = OnMe(frames_of(small, "q_charged"), landed, me, until=landed + 2000)
    over.append(charge)
    a("skill", tick(P["q_anim"]))
    a("idle", 300, loop=True)
    rel = t + tick(P["a_st"])
    bolt("a_blast", rel, BOLT, d, "a_blast_hit")
    charge.until = rel
    a("attack", tick(P["atk_dur"]))
    a("idle", 400, loop=True)
    # W -> E: the field under Darius, the ray from him on through Garen, the aftershock, the burst's stun
    w0 = t
    lay = w0 + tick(P["w_rel"])
    fx_x = d.pos(lay)[0]
    under.append(Anim(frames_of(big, "w_field"), lay, fx_x, gy + 11))
    for foe in (d, g):
        under.append(OnFoe(frames_of(small, "w_slow"), lay, foe, until=lay + 1500))
    ray = w0 + tick(P["e_gap"] + P["e_rel"])
    under.append(Anim(frames_of(big, "e_ray"), ray, fx_x, gy))
    for foe in (d, g):
        hit(foe, "e_hit", ray + tick(P["e_apply"]))
    after = ray + tick(P["e_after"])
    under.append(Anim(frames_of(big, "e_after"), after, fx_x, gy))
    for foe in (d, g):
        hit(foe, "e_after_hit", after + tick(8))
    burst = lay + tick(P["w_stun_at"])
    under.append(Anim(frames_of(big, "w_burst"), burst, fx_x, gy + 11))
    for foe in (d, g):
        over.append(OnFoe(frames_of(small, "w_stun"), burst, foe))
        foe.holds.append((burst, burst + tick(P["w_stun"])))
    a("skill2", tick(P["e_gap"]))
    a("skill2_e", tick(P["e_anim"]))
    a("idle", max(0, burst + tick(P["w_stun"]) - t), loop=True)
    # he walks past them and turns round (the red side's facing): R - the storm on Darius, a strike each second
    walk_to = g.pos(t)[0] + 70
    me.moves.append((t, t + 900, me.pos(t)[0], walk_to))
    a("run", 900, loop=True)
    face[0] = True
    rel = t + tick(P["r_rel"])
    fall = rel + tick(P["r_fall"])
    under.append(Anim(frames_of(big, "r_land"), fall, d.pos(fall)[0], gy + 11))
    for foe in (d, g):
        hit(foe, "r_hit", fall + tick(1))
    for k in range(3):
        when = fall + tick(60 * (k + 1))
        over.append(OnFoe(frames_of(big, "r_storm"), when, d))
        for foe in (d, g):
            hit(foe, "r_hit", when + tick(2))
    a("ult", tick(P["r_anim"]))
    a("idle", tick(60 * 3) - tick(P["r_anim"]) + 600, loop=True)
    over.append(OnMe(frames_of(small, "evo"), t - 500, me))
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
                                os.path.join(args.out, "league_viktor_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_viktor_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_viktor_showcase.gif")))


if __name__ == "__main__":
    main()
