#!/usr/bin/env python3
"""Preview images for Mordekaiser, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_mordekaiser.py [--out docs/preview] [--only frames|effects|showcase]

  league_mordekaiser_frames.png    every animation's dense frames (hd_, PPU 5, 110%: as league.dll shows them)
  league_mordekaiser_effects.png   every effect animation, 3x
  league_mordekaiser_showcase.gif  a scripted fight with Darius in front and Garen behind him, timed like the kit
                                   (tools/kit/build_mordekaiser.py, 60 ticks a second): three mace swings stack
                                   Darkness Rise (the aura's pulses then burn Darius); Obliterate slams a crack at Darius
                                   alone (the isolated hit); Death's Grasp's claw; Indestructible's shield and its heal;
                                   Realm of Death - the curse on Darius, the add-on's realm (both gone, the vortex where
                                   they stood), Darius dead inside and Mordekaiser back with the soul; 3x
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
from build_mordekaiser import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_mordekaiser")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_mordekaiser_fx", "league_mordekaiser_big")}
Q_MID = P["q_len"] / 2000                        # the crack's picture sits at the line's middle (game px ahead)
E_MID = P["e_len"] / 2000


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_mordekaiser_fx"], fx["league_mordekaiser_big"]
    W, H = 240, 110
    gy = 78
    x0 = 90
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 30, gy)
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 95, gy)
    me = Me(x0, gy)
    body, under, over = [], [], []
    gone = []                                    # (t0, t1): both in the realm, off the battlefield
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        x, y = me.pos(t)
        an = Anim(dense(sp, tag, "mordekaiser", z), t, x, y, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def hit(foe, tag, when, sheet=None):
        over.append(OnFoe(frames_of(sheet or small, tag), when, foe))
        foe.flinches.append(when)

    def aura(t0, t1):
        k = t0
        while k < t1:
            under.append(OnMe(frames_of(big, "p_aura"), k, me))
            hit(d, "p_hit", k + 60)
            k += tick(P["p_per"])

    a("idle", 600, loop=True)
    # three swings: Darkness Rise at three stacks, its aura from the next action on
    for _ in range(3):
        hit(d, "a_hit", t + tick(P["a_st"]))
        a("attack", tick(P["atk_dur"]))
        a("idle", 150, loop=True)
    aura(t, t + 9000)
    # Obliterate: the slam at his feet, the crack along the line, Darius alone in it: the isolated hit
    q = t + tick(P["q_at"])
    under.append(Anim(frames_of(big, "q_slam"), q, me.pos(q)[0] + 8, gy))
    under.append(Anim(frames_of(big, "q_crack"), q, me.pos(q)[0] + Q_MID, gy))
    hit(d, "q_iso_hit", q + tick(2))
    a("skill", tick(P["q_dur"]))
    a("idle", 300, loop=True)
    # Death's Grasp: the claw from his hand at Garen behind Darius
    e = t + tick(P["e_at"])
    over.append(Anim(frames_of(big, "e_beam"), e, me.pos(e)[0] + E_MID, gy))
    hit(g, "e_hit", e + tick(3))
    a("skill2", tick(P["e_dur"]))
    a("idle", 300, loop=True)
    # Indestructible: the shield, the heal w_heal_at ticks later
    over.append(OnMe(frames_of(small, "w_shield"), t, me))
    over.append(OnMe(frames_of(small, "w_heal"), t + tick(P["w_heal_at"]), me))
    a("skill2_w", tick(P["w_dur"]))
    a("idle", tick(P["w_heal_at"]) - tick(P["w_dur"]) + 400, loop=True)
    # Realm of Death: the burst, the curse; the add-on takes both into the realm (the vortex where they stood)
    r = t + tick(P["r_at"])
    over.append(Anim(frames_of(big, "r_cast"), r, me.pos(r)[0], gy))
    hit(d, "r_mark", r + tick(1))
    a("ult", tick(P["r_dur"]))
    realm0, realm1 = t, t + 2400
    gone.append((realm0, realm1))
    under.append(Anim(frames_of(big, "r_realm"), realm0, (me.pos(realm0)[0] + d.pos(realm0)[0]) / 2, gy,
                      until=realm1, loop=True))
    t = realm1
    # back alone: Darius died in the realm, the soul taken
    over.append(OnMe(frames_of(small, "r_win"), t, me))
    a("idle", 1600, loop=True)
    end = t

    def place(img, f, px, py):
        put(img, f, px, py, z)

    def away(tt):
        return any(t0 <= tt < t1 for t0, t1 in gone)

    frames, tt = [], 0.0
    while tt < end:
        img = Image.new("RGBA", (W * z, H * z), ARENA)
        for an in under:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        units = [(g.pos(tt)[1], g.frame(tt), g.pos(tt))]
        if not away(tt) and tt < (gone[0][0] if gone else end):
            units.append((d.pos(tt)[1], d.frame(tt), d.pos(tt)))
        if not away(tt):
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_mordekaiser_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[19:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_mordekaiser_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_mordekaiser_showcase.gif")))


if __name__ == "__main__":
    main()
