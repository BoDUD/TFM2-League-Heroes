#!/usr/bin/env python3
"""Preview images for Corki, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_corki.py [--out docs/preview] [--only frames|effects|showcase]

  league_corki_frames.png    every animation's dense frames (hd_, PPU 5, the game at 1x: as league.dll shows them)
  league_corki_effects.png   every effect animation, 3x
  league_corki_showcase.gif  a scripted fight with Darius in front and Garen behind him, timed like the kit
                             (tools/kit/build_corki.py, 60 ticks a second): a hextech shot; the Phosphorus Bomb lobbed at
                             Darius (the blast, the splash); the Gatling Gun's sweep (a hit every quarter second, the
                             shred over his head); the Package when Darius closes in (the take-off blast knocks him back,
                             Corki flies off backwards leaving the big fire); Missile Barrage - two missiles and the Big
                             One at Garen behind him; 3x
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
from build_corki import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_corki")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_corki_fx", "league_corki_big")}
MUZZLE = (19, 1)                                 # the gun's mouth from his pivot (game px; a_y / r_y 6000)
BULLET = P["a_speed"] / 1000                     # px a tick
MISSILE = P["r_speed"] / 1000


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_corki_fx"], fx["league_corki_big"]
    W, H = 260, 110
    gy = 72
    x0 = 100
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 60, gy)
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 120, gy)
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        x, y = me.pos(t)
        an = Anim(dense(sp, tag, "corki", z), t, x, y, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def hit(foe, tag, when, sheet=None):
        over.append(OnFoe(frames_of(sheet or small, tag), when, foe))
        foe.flinches.append(when)

    def fly(tag, when, x1, speed, sheet=None):
        sx, sy = me.pos(when)[0] + MUZZLE[0], gy + MUZZLE[1]
        arrive = when + tick(max(1, (x1 - sx) / speed))
        over.append(Anim(frames_of(sheet or small, tag), when, sx, sy, until=arrive, x1=x1, y1=sy))
        return arrive

    a("idle", 600, loop=True)
    # a hextech shot
    rel = t + tick(P["a_st"])
    hit(d, "a_hit", fly("a_bolt", rel, d.pos(rel)[0], BULLET))
    a("attack", tick(P["atk_dur"]))
    a("idle", 200, loop=True)
    # Phosphorus Bomb: lobbed onto Darius's spot, the blast and the splash
    rel = t + tick(P["q_at"])
    tx = d.pos(rel)[0]
    sx = me.pos(rel)[0] + 4
    land = rel + tick(P["q_fly"])
    over.append(Anim(frames_of(small, "q_bomb"), rel, sx, gy - 10, until=land, x1=tx, y1=gy))
    over.append(Anim(frames_of(big, "q_boom"), land, tx, gy))
    hit(d, "q_hit", land + 40)
    a("skill", tick(P["q_dur"]))
    a("idle", 300, loop=True)
    # Gatling Gun: the spin-up, then a hit every e_per ticks (2 s of it here) and the shred over Darius
    e0 = t + tick(P["e_at"])
    a("skill2", tick(P["e_dur"]))
    for k in range(0, 120, P["e_per"]):
        hit(d, "e_hit", e0 + tick(k))
    over.append(OnFoe(frames_of(small, "e_shred"), e0, d, until=e0 + tick(120 + P["e_shred_t"])))
    a("idle", tick(120) - tick(P["e_dur"] - P["e_at"]), loop=True)
    # the Package: the take-off blast knocks Darius back, Corki flies off backwards leaving the big fire
    w0 = t + tick(P["w_at"])
    under.append(Anim(frames_of(big, "pk_blast"), t, me.pos(t)[0], gy))
    hit(d, "pk_hit", t + 60)
    reach = P["pk_speed"] * P["pk_tick"] / 1000
    xs = me.pos(w0)[0]
    me.moves.append((w0, w0 + tick(P["pk_tick"]), xs, xs - reach))
    for k in range(1, P["pk_tick"] + 1, P["w_gap"]):
        when = w0 + tick(k)
        under.append(Anim(frames_of(big, "w_fire_big"), when, me.pos(when)[0], gy))
    a("skill2_w", tick(P["w_dur"]))
    a("idle", 400, loop=True)
    # Missile Barrage: two missiles at Darius, the Big One at Garen behind him
    for k, (foe, kind) in enumerate([(d, "r"), (d, "r"), (g, "r_big")]):
        rel = t + tick(P["r_at"])
        land = fly(kind + "_missile", rel, foe.pos(rel)[0], MISSILE, big if kind == "r_big" else None)
        over.append(Anim(frames_of(big if kind == "r_big" else small, kind + "_boom"), land, foe.pos(land)[0], gy))
        hit(foe, "r_hit", land + 40)
        a("ult", tick(P["r_dur"]))
        a("idle", 250, loop=True)
    a("idle", 1200, loop=True)
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_corki_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_corki_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_corki_showcase.gif")))


if __name__ == "__main__":
    main()
