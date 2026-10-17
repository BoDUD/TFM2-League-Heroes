#!/usr/bin/env python3
"""Preview images for Viego, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_viego.py [--out docs/preview] [--only frames|effects|showcase]

  league_viego_frames.png    every animation, frame by frame, 3x on the arena colour
  league_viego_effects.png   every effect animation (the add-on's s_* too), 3x
  league_viego_showcase.gif  a scripted fight against Darius with Garen behind him, timed like the kit
                             (tools/kit/build_viego.py, 60 ticks a second): a sword hit on Darius; Q - the thrust
                             through both, Darius marked, the double strike; W + E - the black mist round him, the
                             dash and the maw biting Darius (stunned); R - the leap onto Darius, the stab and the
                             shockwave knocking Garen back; Darius falls and Viego takes his soul: untouchable a
                             moment, then the possession's mist round him; 3x
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
from build_viego import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_viego")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_viego_fx", "league_viego_big")}


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_viego_fx"], fx["league_viego_big"]
    W, H = 220, 100
    gy = 78
    x0 = 66
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 30, gy)       # in his sword's reach
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 62, gy)        # behind Darius, in line
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

    def line(tag, rel, speed, length):
        sx = me.pos(rel)[0] + 6
        until = rel + tick(length / speed)
        over.append(Anim(frames_of(small, tag), rel, sx, gy - 6, until=until, x1=sx + length, y1=gy - 6))
        return sx

    a("idle", 500, loop=True)
    hit(d, "a_hit", t + tick(P["atk_st"]))
    a("attack", tick(P["atk_dur"]))
    a("idle", 300, loop=True)
    # Q: the thrust through both, Darius marked; the double strike
    rel = t + tick(P["q_at"])
    sx = line("q_thrust", rel, P["q_speed"] / 1000, P["q_len"] / 1000)
    for foe in (d, g):
        hit(foe, "q_hit", rel + tick((foe.pos(rel)[0] - sx) / (P["q_speed"] / 1000)))
    mark = OnFoe(frames_of(small, "q_marked"), rel + tick(2), d, until=rel + 2600)
    over.append(mark)
    a("skill", tick(P["q_dur"]))
    a("idle", 300, loop=True)
    strike = t + tick(P["atk_st"])
    hit(d, "a_hit", strike)
    hit(d, "a_double", strike + tick(P["d_at"]))
    mark.until = strike + tick(P["d_at"])
    a("attack", tick(P["atk_dur"]))
    # W + E: back off, the mist, the dash and the maw
    me.moves.append((t, t + 500, me.pos(t)[0], me.pos(t)[0] - 30))
    a("run", 500, loop=True)
    w0 = t
    under.append(Anim(frames_of(big, "e_mist"), w0, me.pos(w0)[0], gy))         # the sheet sets it at his soles
    over.append(OnMe(frames_of(small, "e_on"), w0, me, until=w0 + 3000))
    dash0 = w0 + tick(P["w_wind"])
    dash_t = tick(P["w_dash"] / P["w_dspeed"])
    me.moves.append((dash0, dash0 + dash_t, me.pos(w0)[0], me.pos(w0)[0] + P["w_dash"] // 1000))
    fly0 = dash0 + dash_t
    sx = me.pos(fly0)[0] + 6
    arrive = fly0 + tick((d.pos(fly0)[0] - sx) / (P["w_speed"] / 1000))
    over.append(Anim(frames_of(small, "w_maw"), fly0, sx, gy - 6, until=arrive, x1=d.pos(fly0)[0], y1=gy - 6))
    hit(d, "w_hit", arrive)
    over.append(OnFoe(frames_of(small, "w_stun"), arrive, d, until=arrive + tick(P["w_stun"])))
    d.holds.append((arrive, arrive + tick(P["w_stun"])))
    a("skill2", tick(P["w_dur"]))
    a("idle", max(200, arrive - t + 200), loop=True)
    # R: the leap onto Darius, the stab, the shockwave knocking Garen back; Darius falls, his soul taken
    r0 = t
    over.append(OnMe(frames_of(small, "r_cast"), r0, me))
    land = r0 + tick(P["r_hit"])
    me.moves.append((r0 + tick(4), land, me.pos(r0)[0], d.pos(r0)[0] - 8))
    hit(d, "r_hit", land, big)
    under.append(Anim(frames_of(big, "r_land"), land, d.pos(r0)[0] - 8, gy))
    g.slides.append((land, land + tick(P["r_kb_t"]), P["r_kb_speed"] * P["r_kb_t"] // 1000))
    g.flinches.append(land)
    d.death = land + 60
    a("ult", tick(P["r_dur"]))
    take = t
    over.append(OnMe(frames_of(big, "p_take"), take, me))
    over.append(OnMe(frames_of(small, "p_safe"), take, me, until=take + tick(P["p_inv"])))
    a("possess", tick(P["p_anim"]))
    over.append(OnMe(frames_of(big, "p_on"), t, me, until=t + 2400))
    a("idle", 2400, loop=True)
    over.append(OnMe(frames_of(small, "p_end"), t, me))
    a("idle", 600, loop=True)
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
                                os.path.join(args.out, "league_viego_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_viego_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_viego_showcase.gif")))


if __name__ == "__main__":
    main()
