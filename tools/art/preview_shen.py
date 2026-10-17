#!/usr/bin/env python3
"""Preview images for Shen, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_shen.py [--out docs/preview] [--only frames|effects|showcase]

  league_shen_frames.png    every animation, frame by frame, 3x on the arena colour
  league_shen_effects.png   every effect animation, 3x
  league_shen_showcase.gif  top lane against Darius, timed like the kit (tools/kit/build_shen.py, 60 ticks a
                            second): Q - the spirit blade flies back to him through Darius (the hit, the slow), Ki
                            Barrier, Spirit's Refuge opening round him as the blade comes home, the empowered
                            attacks; E - the shadow dash and the taunt, a plain attack; R - Garen far away in trouble:
                            the call, Garen's shield, the channel, the landing beside Garen; 3x
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
from build_shen import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_shen")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_shen_fx", "league_shen_big")}
REACH = 24                                      # where his sword lands from (px from Darius)
BLADE = P["q_speed"] / 1000                     # px a tick
BLADE_Y = P["q_y"] // 1000                      # the blade flies this far over the pivot
DASH = P["e_speed"] / 1000


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_shen_fx"], fx["league_shen_big"]
    W, H = 330, 120
    gy = 92
    x0 = 50
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 64, gy)
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 230, gy - 6)
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        if dur is not None and dur <= 0:
            return None
        an = Anim(frames_of(sp, tag), t, *me.pos(t), loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def hit(foe, tag, when, sheet=None):
        over.append(OnFoe(frames_of(sheet or small, tag), when, foe))
        foe.flinches.append(when)

    def on_me(sheet, tag, when, until=None, layer=None):
        (layer if layer is not None else over).append(OnMe(frames_of(sheet, tag), when, me, until=until))

    a("idle", 500, loop=True)
    # Q: the blade appears ahead of him and flies home through Darius
    q0 = t
    on_me(small, "p_on", q0, until=q0 + tick(P["p_sh_t"]))
    at_t = q0 + tick(P["q_at"])
    x_me = me.pos(q0)[0]
    far = x_me + P["q_out"] // 1000 + 20
    dur = tick((far - x_me) / BLADE)
    over.append(Anim([(f.transpose(Image.FLIP_LEFT_RIGHT), ms) for f, ms in frames_of(small, "q_blade")], at_t,
                     far, gy - BLADE_Y, loop=True, until=at_t + dur, x1=x_me + 4, y1=gy - BLADE_Y))
    pass_t = at_t + tick((far - d.pos(at_t)[0]) / BLADE)
    hit(d, "q_hit", pass_t)
    under.append(OnFoe(frames_of(small, "q_slow"), pass_t, d, until=pass_t + tick(P["q_slow_t"])))
    home = at_t + dur
    a("skill", tick(P["q_dur"]))
    a("idle", max(0, home - t), loop=True)
    # the blade home with Darius near: Spirit's Refuge round him, the empowered attacks ready
    under.append(Anim(frames_of(big, "w_zone"), home, *me.pos(home)))
    on_me(small, "w_safe", home, until=home + tick(P["w_t"]))
    charged = OnMe(frames_of(small, "q_1"), home, me, until=None, loop=True)
    over.append(charged)
    me.moves.append((t, t + 300, me.pos(t)[0], d.pos(t)[0] - REACH))
    a("run", 300, loop=True)
    for _ in range(2):
        hit(d, "a_emp", t + tick(P["atk_st"]))
        a("attack", tick(P["atk_dur"]))
        a("idle", tick(P["atk_cd"] - P["atk_dur"]), loop=True)
    charged.until = t
    # back off, then E through Darius: the shadow dash and the taunt
    me.moves.append((t, t + 400, me.pos(t)[0], me.pos(t)[0] - 34))
    a("run", 400, loop=True)
    a("idle", 200, loop=True)
    e0 = t
    ex = me.pos(e0)[0]
    e_len = min(P["e_len"] // 1000, d.pos(e0)[0] - 12 - ex)       # MoveTo runs to the target's spot: stop at him
    e_dur = tick(e_len / DASH)
    me.moves.append((e0, e0 + e_dur, ex, ex + e_len))
    dash = Anim(frames_of(small, "e_dash"), e0, ex, gy, loop=True, until=e0 + e_dur, x1=ex + e_len)
    under.append(dash)
    on_me(small, "p_on", e0, until=e0 + tick(P["p_sh_t"]))
    hit(d, "e_hit", e0 + tick(max(1, (d.pos(e0)[0] - ex) / DASH)))
    a("skill2", max(tick(P["e_dur"]), e_dur))
    a("idle", 150, loop=True)
    hit(d, "a_hit", t + tick(P["atk_st"]))
    a("attack", tick(P["atk_dur"]))
    a("idle", 300, loop=True)
    # R: Garen far away in trouble - the call, his shield, the channel, the landing beside him
    r0 = t
    for k in range(4):
        g.flinches.append(r0 + 120 * k)
    over.append(OnFoe(frames_of(big, "r_shield"), r0, g, until=r0 + tick(P["r_sh_t"])))
    on_me(big, "r_cast", r0)
    on_me(big, "r_ch", r0, until=r0 + tick(P["r_ch"]))
    on_me(small, "p_on", r0, until=r0 + tick(P["p_sh_t"]))
    a("ult", tick(P["r_wind"]))
    a("ult_loop", tick(P["r_ch"] - P["r_wind"]), loop=True)
    land = t
    gx = g.pos(land)[0] - 22
    me.moves.append((land, land + 1, me.pos(land)[0], gx))
    over.append(Anim(frames_of(big, "r_land"), land, gx, gy))
    a("idle", 900, loop=True)
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
                                os.path.join(args.out, "league_shen_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[12:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_shen_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_shen_showcase.gif")))


if __name__ == "__main__":
    main()
