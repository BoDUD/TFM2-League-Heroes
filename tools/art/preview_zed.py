#!/usr/bin/env python3
"""Preview images for Zed, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_zed.py [--out docs/preview] [--only frames|effects|showcase]

  league_zed_frames.png    every animation, frame by frame, 3x on the arena colour
  league_zed_effects.png   every effect animation, 3x
  league_zed_showcase.gif  a scripted gank on Darius with Garen behind him, timed like the kit
                           (tools/kit/build_zed.py, 60 ticks a second): W-E-Q - the shadow flung onto Darius, the two
                           slash rings, his shuriken and the shadow's crossing on Darius; the W2 swap onto the shadow; a stab with Contempt for the Weak; R - the shadow left behind, the dash
                           through Darius, the Death Mark over him, the automatic Shadow Slash and stabs meanwhile, the
                           burst, the R2 swap back to the shadow; 3x
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
from preview_pyke import Me, OnFoe, OnMe, mirrored  # noqa: E402
from build_zed import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_zed")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_zed_fx", "league_zed_big")}
REACH = 28                                      # where his stabs land from (px from Darius)
STAR = P["q_speed"] / 1000                      # px a tick
STAR_Y = P["q_y"] // 1000 + 6                   # the shurikens fly this far over the pivot


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_zed_fx"], fx["league_zed_big"]
    W, H = 240, 110
    gy = 86
    x0 = 40
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 76, gy)
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 160, gy)
    me = Me(x0, gy)
    body, under, over = [], [], []
    face = [False]
    t = 0.0

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

    def at(sheet, tag, when, x, y=gy, until=None, loop=False, layer=None):
        an = Anim(frames_of(sheet, tag), when, x, y, loop=loop, until=until)
        (layer if layer is not None else over).append(an)
        return an

    def fly(tag, when, x_from, x_to, left=False):
        dur = tick(max(1, abs(x_to - x_from) / STAR))
        fr = frames_of(small, tag)
        over.append(Anim(mirrored(fr) if left else fr, when, x_from, gy - STAR_Y, until=when + dur, x1=x_to,
                         y1=gy - STAR_Y))
        return when + dur

    a("idle", 500, loop=True)
    # W-E-Q: the shadow flung onto Darius, the slash rings, the two shurikens crossing on him
    t0 = t
    at(small, "w_dash", t0 + tick(P["w_at"] - 1), me.pos(t0)[0])
    land = t0 + tick(P["w_at"] - 1 + P["w_fly"])
    spot = d.pos(land)[0]
    at(small, "sh_in", land, spot, layer=under)
    e = t0 + tick(P["c_e"])
    at(big, "e_spin", e, me.pos(e)[0], layer=under)
    at(big, "sh_spin", e + tick(1), spot, layer=under)
    hit(d, "e_hit", e + tick(1))
    q = t0 + tick(P["w_dur"] + P["q_at"])
    arrive = fly("q_star", q, me.pos(q)[0] + 10, d.pos(q)[0])
    hit(d, "q_hit", arrive)
    at(small, "sh_throw", q + tick(1), spot)
    fly("sh_star", q + tick(1), spot + 4, me.pos(q)[0] + 6, left=True)
    hit(d, "q_hit", q + tick(2))
    a("skill", tick(P["w_dur"]))
    a("skill2", tick(P["q_dur"]))
    # the shadow stands; the W2 swap onto it (one enemy near it, none near him)
    stand_from = land + 750
    swap = land + tick(P["swap_step"])
    at(small, "sh_stand", stand_from, spot, until=swap, loop=True, layer=under)
    a("idle", max(0, swap - t), loop=True)
    at(small, "w_swap", swap, me.pos(swap)[0])
    at(small, "w_swap", swap, spot)
    me.moves.append((swap, swap + 1, me.pos(swap)[0], spot - 4))
    a("idle", 120, loop=True)
    # a stab with Contempt for the Weak
    hit(d, "a_hit", t + tick(P["a_st"]))
    hit(d, "cw_hit", t + tick(P["a_st"]) + 20)
    a("attack", tick(P["atk_dur"]))
    a("idle", 300, loop=True)
    # he steps back, then R: the shadow left behind, the dash through Darius, the mark, stabs and a slash, the burst
    b0 = t
    me.moves.append((b0, b0 + 480, me.pos(b0)[0], me.pos(b0)[0] - 44))
    face[0] = True
    a("run", 480, loop=True)
    face[0] = False
    r0 = t
    rx = me.pos(r0)[0]
    r_shadow = at(small, "r_shadow", r0 + tick(1), rx, layer=under)
    go = r0 + tick(P["r_go"])
    behind = d.pos(go)[0] + 16
    me.moves.append((go, go + tick(8), rx, behind))
    hit(d, "r_hit", go + tick(6), big)
    mark_end = go + tick(6) + tick(P["r_pop"])
    over.append(OnFoe(frames_of(small, "r_mark"), go + tick(6), d, until=mark_end))
    a("ult", tick(P["r_dur"]))
    face[0] = True
    hit(d, "a_hit", t + tick(P["a_st"]))
    a("attack", tick(P["atk_dur"]))
    e2 = t + tick(P["e_at"])
    at(big, "e_spin", e2, me.pos(e2)[0], layer=under)
    hit(d, "e_hit", e2)
    a("skill_e", tick(P["e_dur"]))
    hit(d, "a_hit", t + tick(P["a_st"]))
    a("attack", tick(P["atk_dur"]))
    a("idle", max(0, mark_end - t), loop=True)
    hit(d, "r_pop", mark_end, big)
    a("idle", 300, loop=True)
    # R2: outnumbered, back to the shadow
    s2 = t
    at(small, "w_swap", s2, me.pos(s2)[0])
    at(small, "w_swap", s2, rx)
    r_shadow.until = s2
    me.moves.append((s2, s2 + 1, me.pos(s2)[0], rx))
    face[0] = False
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
                                os.path.join(args.out, "league_zed_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[11:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_zed_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_zed_showcase.gif")))


if __name__ == "__main__":
    main()
