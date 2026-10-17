#!/usr/bin/env python3
"""Preview images for Dr. Mundo, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_drmundo.py [--out docs/preview] [--only frames|effects|showcase]

  league_drmundo_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_drmundo_effects.png   every effect animation, 3x
  league_drmundo_showcase.gif  a scripted fight with Darius in front of him, timed like the kit
                               (tools/kit/build_drmundo.py, 60 ticks a second): two chops; Infected Bonesaw spinning
                               out, hitting, slowing and healing him; Blunt Force Trauma's bag swing and a corpse flung
                               on past Darius; Heart Zapper - the shock, the crackling ring while he keeps chopping, a
                               zap a pulse, the discharge and the grey health back; Goes Where He Pleases - the control
                               shaken off, the chem-tank landing, lying there, picked up; Maximum Dosage; 3x
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
from build_drmundo import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_drmundo")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_drmundo_fx", "league_drmundo_big")}
HAND = (14, -20)                                 # where the saw leaves: px from his pivot
SAW = P["q_speed"] / 1000                        # px a tick
FLING = P["e_fling_v"] / 1000
GAP = 52                                         # Darius stands this far from his pivot (Mundo is ~54 px wide)


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_drmundo_fx"], fx["league_drmundo_big"]
    W, H = 300, 120
    gy = 90
    x0 = 80
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + GAP, gy)
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        x, y = me.pos(t)
        an = Anim(dense(sp, tag, "drmundo", z), t, x, y, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def hit(tag, when, sheet=None, until=None):
        over.append(OnFoe(frames_of(sheet or small, tag), when, d, until=until))
        d.flinches.append(when)

    def chop():
        hit("a_hit", t + tick(P["atk_st"]))
        a("attack", tick(P["atk_dur"]))
        a("idle", 200, loop=True)

    a("idle", 500, loop=True)
    chop()
    chop()
    # Infected Bonesaw: the saw spinning out to Darius, the hit, the slow, the heal
    rel = t + tick(P["q_at"])
    sx, sy = me.pos(rel)[0] + HAND[0], gy + HAND[1]
    arrive = rel + tick(max(1, (d.pos(rel)[0] - sx) / SAW))
    over.append(Anim(frames_of(small, "q_saw"), rel, sx, sy, loop=True, until=arrive, x1=d.pos(rel)[0], y1=gy - 14))
    hit("q_hit", arrive)
    under.append(OnFoe(frames_of(small, "q_slow"), arrive, d, until=arrive + tick(P["q_slow_t"])))
    over.append(OnMe(frames_of(small, "q_heal"), arrive, me))
    a("skill", tick(P["q_dur"]))
    a("idle", 400, loop=True)
    # Blunt Force Trauma: the bag swing; a corpse flung on past Darius
    land = t + tick(P["e_st"])
    hit("e_hit", land)
    fx0 = d.pos(land)[0] + 8
    fx1 = fx0 + 70
    over.append(Anim(frames_of(small, "e_fling"), land + 150, fx0, gy - 8, loop=True,
                     until=land + 150 + tick(70 / FLING), x1=fx1, y1=gy - 8))
    over.append(Anim(frames_of(small, "e_fling_hit"), land + 150 + tick(70 / FLING), fx1, gy - 14))
    a("attack_e", tick(P["e_dur"]))
    a("idle", 500, loop=True)
    # Heart Zapper: the shock, the ring while he chops on, a zap a pulse, the discharge, the grey health back
    w0 = t
    w_end = w0 + tick(P["w_n"] * P["w_per"])
    over.append(OnMe(frames_of(big, "w_start"), w0, me))
    under.append(OnMe(frames_of(big, "w_on"), w0, me, until=w_end, loop=True))
    for k in range(1, P["w_n"]):
        over.append(OnFoe(frames_of(small, "w_zap"), w0 + tick(k * P["w_per"]), d))
    a("skill2", tick(P["w_anim"]))
    while t + tick(P["atk_dur"]) + 200 < w_end:
        chop()
    a("idle", w_end - t, loop=True)
    over.append(OnMe(frames_of(big, "w_burst"), t, me))
    hit("w_end_hit", t + 30)
    over.append(OnMe(frames_of(small, "q_heal"), t + 60, me))
    a("skill2_end", tick(P["w_end_anim"]))
    a("idle", 500, loop=True)
    # Goes Where He Pleases: a control shaken off, the tank thrown down beside him, lying there, picked up
    over.append(OnMe(frames_of(small, "p_shake"), t, me))
    tank_x, tank_y = me.pos(t)[0] - 20, gy
    drop = t + tick(P["p_fly"])
    over.append(Anim(frames_of(small, "p_land"), drop, tank_x, tank_y))
    under.append(Anim(frames_of(small, "p_tank"), drop, tank_x, tank_y, loop=True, until=drop + 1200))
    a("idle", 900, loop=True)
    me.moves.append((t, t + 300, me.pos(t)[0], tank_x))
    a("run", 300, loop=True)
    over.append(Anim(frames_of(small, "p_pick"), t, tank_x, tank_y))
    me.moves.append((t + 300, t + 600, tank_x, x0))
    a("run", 600, loop=True)
    a("idle", 300, loop=True)
    # Maximum Dosage
    over.append(OnMe(frames_of(big, "r_cast"), t, me))
    over.append(OnMe(frames_of(small, "r_on"), t + tick(P["r_anim"]), me, until=t + tick(P["r_anim"]) + 2000,
                     loop=True))
    a("ult", tick(P["r_anim"]))
    chop()
    chop()
    a("idle", 900, loop=True)
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_drmundo_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp_ = load(path)
            rows += [(sp_, t["name"], f"{name[15:]}:{t['name']}") for t in sp_.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_drmundo_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_drmundo_showcase.gif")))


if __name__ == "__main__":
    main()
