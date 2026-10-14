#!/usr/bin/env python3
"""Preview images for Nilah, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_nilah.py [--out docs/preview] [--only frames|effects|showcase]

  league_nilah_frames.png    every animation's dense frames (hd_, PPU 2.5, as league.dll shows them)
  league_nilah_effects.png   every effect animation, 3x
  league_nilah_showcase.gif  a scripted fight with Darius in front of her and Taric behind, timed like the kit
                             (tools/kit/build_nilah.py, 60 ticks a second): two whip attacks; Formless Blade's lash
                             down the line, its hit and the water round her; two empowered attacks with the cone's
                             fan; Slipstream through Darius, the spin cut round her as she lands; Slipstream back through
                             him; Jubilant Veil on her and on Taric; Apotheosis's storm with its cuts, the pull, the
                             burst and the heals on her and Taric; 3x
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
from build_nilah import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_nilah")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_nilah_fx", "league_nilah_big")}


def flipped(fr):
    """Dense frames turned to face left (the client mirrors her own frames), keeping their 1x size for put()."""
    out = []
    for f, ms in fr:
        g = f.transpose(Image.FLIP_LEFT_RIGHT)
        g.info["one"] = f.info["one"]
        out.append((g, ms))
    return out


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_nilah_fx"], fx["league_nilah_big"]
    W, H = 250, 110
    gy = 74
    x0 = 100
    xd = x0 + 26                                         # Darius in her whip's reach (atk_range 30000)
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), xd, gy)
    taric = load(os.path.join(LEAGUE, "champions", "league_taric"))
    tx = x0 - 46
    ally = Anim(frames_of(taric, "idle"), 0, tx, gy, loop=True)
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False, left=False):
        nonlocal t
        x, y = me.pos(t)
        fr = dense(sp, tag, "nilah", z)
        an = Anim(flipped(fr) if left else fr, t, x, y, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def hit(tag, when, sheet=None):
        over.append(OnFoe(frames_of(sheet or small, tag), when, d))
        d.flinches.append(when)

    a("idle", 400, loop=True)
    # two whip attacks
    for _ in range(2):
        hit("a_hit", t + tick(P["a_st"]))
        a("attack", tick(P["atk_dur"]))
        a("idle", 250, loop=True)
    # Formless Blade: the lash down the line, its hit, the water round her for q_t
    hit("q_hit", t + tick(P["q_at"]))
    over.append(OnMe(frames_of(small, "q_on"), t, me, until=t + tick(P["q_t"])))
    a("skill", tick(P["q_dur"]))
    a("idle", 200, loop=True)
    # two empowered attacks: the longer whip and the fan
    for _ in range(2):
        hit("qa_hit", t + tick(P["a_st"]))
        a("attack_q", tick(P["atk_dur"]))
        a("idle", 200, loop=True)
    # Slipstream through Darius, the spin cut round her as she lands (she turns to face him)
    e0 = t
    land = e0 + tick(P["e_tick"])
    me.moves.append((e0, land, x0, xd + 18))
    hit("e_hit", land)
    a("skill2", land - e0)
    over.append(OnMe(frames_of(big, "eq_spin"), t, me))
    hit("eq_hit", t + tick(P["q_spin_at"]))
    a("q_spin", tick(P["q_spin_dur"]), left=True)
    a("idle", 300, loop=True, left=True)
    # Slipstream back through him (Formless Blade is cooling down: no spin)
    e0 = t
    land = e0 + tick(P["e_tick"])
    me.moves.append((e0, land, xd + 18, x0))
    hit("e_hit", land)
    a("skill2", tick(P["e_anim"]), left=True)
    a("idle", 300, loop=True)
    # Jubilant Veil: on her, and on Taric whom it touches
    over.append(OnMe(frames_of(big, "w_on"), t, me, until=t + tick(P["w_t"])))
    over.append(Anim(frames_of(small, "w_ally"), t + 60, tx, gy))
    over.append(Anim(frames_of(big, "w_ally"), t + 60, tx, gy, loop=True, until=t + 60 + tick(P["w_ally_t"])))
    a("w_cast", tick(P["w_dur"]))
    a("idle", 900, loop=True)
    # Apotheosis: the storm, a cut every r_per ticks, the pull, the burst, the heals
    r0 = t
    fin = r0 + tick(P["r_final"])
    over.append(OnMe(frames_of(big, "r_spin"), r0, me))
    for k in range(1, P["r_final"] // P["r_per"] + 1):
        hit("r_hit", r0 + tick(k * P["r_per"]))
    hit("r_pull", fin)
    d.walks.append((fin, fin + 160, -8))
    over.append(OnMe(frames_of(big, "r_burst"), fin, me))
    over.append(OnMe(frames_of(small, "r_heal"), fin + 40, me))
    over.append(Anim(frames_of(small, "r_heal"), fin + 40, tx, gy))
    a("ult", tick(P["r_t"]))
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_nilah_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_nilah_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_nilah_showcase.gif")))


if __name__ == "__main__":
    main()
