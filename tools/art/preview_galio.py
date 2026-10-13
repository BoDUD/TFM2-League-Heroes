#!/usr/bin/env python3
"""Preview images for Galio, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_galio.py [--out docs/preview] [--only frames|effects|showcase]

  league_galio_frames.png    every animation's dense frames (hd_, PPU 2.0, as league.dll shows them; drawn at 85 %)
  league_galio_effects.png   every effect animation, 3x
  league_galio_showcase.gif  a scripted fight with Darius in front and Taric beyond him, timed like the kit
                             (tools/kit/build_galio.py, 60 ticks a second): two stone punches; Colossal Smash - the
                             leap and slam, the blue hit on Darius and the shock ring on the ground; Winds of War - the
                             windblasts to Darius, their burst and the tornado on him; Justice Punch - the dust, the
                             charge, Darius knocked up; Shield of Durand - the dome while he braces, the shockwave,
                             Darius taunted; Hero's Entrance - Taric shielded, the golden light while he channels, the
                             flight onto Taric, the landing ring, Darius thrown up; 3x
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
from build_galio import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_galio")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_galio_fx", "league_galio_big")}


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_galio_fx"], fx["league_galio_big"]
    W, H = 300, 130
    gy = 100
    x0 = 90
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 40, gy)       # in his punch's reach
    taric = load(os.path.join(LEAGUE, "champions", "league_taric"))
    tx = x0 + 84
    ally = Anim(frames_of(taric, "idle"), 0, tx, gy, loop=True)                           # his ally, beyond Darius
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        x, y = me.pos(t)
        an = Anim(dense(sp, tag, "galio", z), t, x, y, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def hit(tag, when, sheet=None, until=None):
        over.append(OnFoe(frames_of(sheet or small, tag), when, d, until=until))
        d.flinches.append(when)

    a("idle", 500, loop=True)
    # two punches
    for _ in range(2):
        hit("a_hit", t + tick(P["atk_st"]))
        a("attack", tick(P["atk_dur"]))
        a("idle", 200, loop=True)
    # Colossal Smash: the leap and the slam, the blue hit, the shock ring under him
    slam = t + tick(P["p_st"])
    hit("p_hit", slam)
    under.append(OnMe(frames_of(big, "p_ring"), slam, me))
    a("attack2", tick(P["p_anim"]))
    a("idle", 300, loop=True)
    # Winds of War: the windblasts to Darius, the burst and the tornado on him
    rel = t + tick(P["q_at"])
    land = rel + tick(P["q_fly"])
    sx = me.pos(rel)[0] + 10
    over.append(Anim(frames_of(small, "q_wind"), rel, sx, gy - 24, until=land, x1=d.pos(rel)[0], y1=gy - 4))
    over.append(OnFoe(frames_of(big, "q_burst"), land, d))
    over.append(OnFoe(frames_of(big, "q_tornado"), land, d))
    hit("q_hit", land)
    a("skill", tick(P["q_dur"]))
    a("idle", 1700, loop=True)
    # Justice Punch: the dust, the charge (he steps back first), Darius knocked up
    e0 = t
    go = e0 + tick(P["e_at"])
    reach = go + tick(4)
    under.append(OnMe(frames_of(small, "e_dash"), go, me))
    me.moves.append((e0, go, me.pos(e0)[0], me.pos(e0)[0] - 6))
    me.moves.append((go, reach, me.pos(e0)[0] - 6, d.pos(go)[0] - 24))
    hit("e_hit", reach)
    d.holds.append((reach, reach + tick(P["e_up"])))
    a("skill2", tick(P["e_dur"]))
    me.moves.append((t, t + 400, d.pos(t)[0] - 24, x0))
    a("idle", 600, loop=True)
    # Shield of Durand: the dome while he braces, the shockwave, Darius taunted
    w0 = t
    over.append(OnMe(frames_of(big, "w_charge"), w0, me, until=w0 + tick(P["w_ch"])))
    a("w_charge", tick(P["w_ch"]), loop=True)
    burst = t + tick(P["w_bt"])
    over.append(OnMe(frames_of(big, "w_burst"), burst, me))
    over.append(OnFoe(frames_of(small, "w_taunt"), burst, d, until=burst + tick(P["w_taunt"])))
    d.holds.append((burst, burst + tick(P["w_taunt"])))
    a("w_burst", tick(P["w_rel"]))
    a("idle", 900, loop=True)
    # Hero's Entrance: Taric shielded, the golden light while he channels, the flight, the landing
    r0 = t
    over.append(Anim(frames_of(small, "r_shield"), r0, tx, gy, loop=True, until=r0 + 3000))
    over.append(OnMe(frames_of(small, "r_cast"), r0, me))
    a("ult", tick(P["r_wind"]))
    a("ult_loop", tick(P["r_ch"] - P["r_wind"]), loop=True)
    arrive = t
    me.moves.append((arrive - 1, arrive, x0, tx - 18))
    lt = arrive + tick(P["r_lt"])
    under.append(Anim(frames_of(big, "r_land"), lt, tx - 18, gy))
    hit("r_hit", lt)
    d.holds.append((lt, lt + tick(P["r_up"])))
    a("ult_land", tick(P["r_land"]))
    a("idle", 1000, loop=True)
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
        units = [(d.pos(tt)[1], d.frame(tt), d.pos(tt)), (ally.pos(tt)[1], ally.frame(tt), ally.pos(tt))]
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_galio_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_galio_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_galio_showcase.gif")))


if __name__ == "__main__":
    main()
