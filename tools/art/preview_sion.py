#!/usr/bin/env python3
"""Preview images for Sion, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_sion.py [--out docs/preview] [--only frames|effects|showcase]

  league_sion_frames.png    every animation's dense frames (hd_, PPU 1.52, as league.dll shows them; drawn at 90 %)
  league_sion_effects.png   every effect animation, 3x
  league_sion_showcase.gif  a scripted fight with Darius, timed like the kit (tools/kit/build_sion.py, 60 ticks a
                            second): two axe chops; Decimating Smash - the charge with its line on the ground, the slam
                            cracking along it, Darius knocked up; Roar of the Slayer - the roar flying through Darius,
                            the armour-shred mark over him; Soul Furnace - the fire shield, its blast; Unstoppable
                            Onslaught - he backs off and charges in on the walking legs, the glow under him, the crash,
                            Darius thrown up; Glory in Death (the add-on) - the zombie's fire round him as he hacks on;
                            3x
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
from build_sion import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_sion")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_sion_fx", "league_sion_big")}


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_sion_fx"], fx["league_sion_big"]
    W, H = 220, 130
    gy = 100
    x0 = 110
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 46, gy)       # in his axe's reach
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        x, y = me.pos(t)
        an = Anim(dense(sp, tag, "sion", z), t, x, y, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def hit(tag, when, sheet=None, until=None):
        over.append(OnFoe(frames_of(sheet or small, tag), when, d, until=until))
        d.flinches.append(when)

    a("idle", 500, loop=True)
    # two chops
    for _ in range(2):
        hit("a_hit", t + tick(P["atk_st"]))
        a("attack", tick(P["atk_dur"]))
        a("idle", 200, loop=True)
    # Decimating Smash: the line on the ground through the charge, the slam cracking along it (its picture is centred
    # on the line, q_len ahead of him), Darius knocked up
    q0 = t
    cx = me.pos(q0)[0] + P["q_len"] // 2000
    under.append(Anim(frames_of(big, "q_warn"), q0, cx, gy, loop=True, until=q0 + tick(P["q_ch"] + P["q_hit"] + 2)))
    a("skill_charge", tick(P["q_ch"]))
    slam = t + tick(P["q_hit"])
    under.append(Anim(frames_of(big, "q_slam"), slam, cx, gy))
    hit("q_hit", slam)
    d.holds.append((slam, slam + tick(P["q_up"])))
    a("skill", tick(P["q_rel"]))
    a("idle", 600, loop=True)
    # Roar of the Slayer: the roar flies e_len through Darius (5 px over the pivot, as a line leaves), his armour shred
    rel = t + tick(P["e_at"])
    sx = me.pos(rel)[0] + 6
    ex = sx + P["e_len"] // 1000
    over.append(Anim(frames_of(small, "e_roar"), rel, sx, gy - 5, loop=True, until=rel + tick(P["e_len"] / P["e_speed"]),
                     x1=ex, y1=gy - 5))
    on = rel + tick((d.pos(rel)[0] - sx) * 1000 / P["e_speed"])
    hit("e_hit", on)
    over.append(OnFoe(frames_of(small, "e_shred"), on, d, until=on + 1800))
    a("skill2", tick(P["e_dur"]))
    a("idle", 500, loop=True)
    # Soul Furnace: the fire shield (held 1.2 s here, w_det 3 s in game), its blast round him, Darius burnt
    w0 = t
    hold = 1200
    over.append(OnMe(frames_of(big, "w_sh"), w0, me, until=w0 + hold))
    a("skill2_w", tick(P["w_anim"]))
    a("idle", hold - tick(P["w_anim"]), loop=True)
    over.append(OnMe(frames_of(big, "w_burst"), t, me))
    hit("w_hit", t + 40)
    a("idle", 600, loop=True)
    # Unstoppable Onslaught: he backs off, then charges in at r_speed on his walking legs, the glow under him, the crash
    # (z 2: over the units), Darius thrown up
    me.moves.append((t, t + 500, x0, x0 - 60))
    a("run", 500, loop=True)
    r0 = t
    hx = d.pos(r0)[0] - 30
    ticks = (hx - (x0 - 60)) * 1000 / P["r_speed"]
    me.moves.append((r0, r0 + tick(ticks), x0 - 60, hx))
    under.append(OnMe(frames_of(big, "r_go"), r0, me, until=r0 + tick(ticks)))
    a("ult", tick(ticks), loop=True)
    crash = t
    over.append(Anim(frames_of(big, "r_crash"), crash, hx, gy))
    hit("r_hit", crash)
    d.holds.append((crash, crash + tick(P["r_up2"])))
    a("ult_hit", tick(P["r_hitanim"]))
    a("idle", 500, loop=True)
    # Glory in Death (the add-on): the zombie's fire round him while he hacks on
    zt = t
    for _ in range(3):
        hit("a_hit", t + tick(P["atk_st"]))
        a("attack", tick(P["atk_dur"]))
    a("idle", 300, loop=True)
    over.append(OnMe(frames_of(big, "p_zombie"), zt, me, until=t))
    a("idle", 500, loop=True)
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
        units = [(d.pos(tt)[1], d.frame(tt), d.pos(tt))]
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_sion_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[12:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_sion_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_sion_showcase.gif")))


if __name__ == "__main__":
    main()
