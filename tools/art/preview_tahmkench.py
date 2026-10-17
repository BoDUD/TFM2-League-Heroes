#!/usr/bin/env python3
"""Preview images for Tahm Kench, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_tahmkench.py [--out docs/preview] [--only frames|effects|showcase]

  league_tahmkench_frames.png    every animation's dense frames (hd_, PPU 1.2, as league.dll shows them)
  league_tahmkench_effects.png   every effect animation, 3x
  league_tahmkench_showcase.gif  a scripted fight with Darius in front of him, timed like the kit
                                 (tools/kit/build_tahmkench.py, 60 ticks a second): three tongue slaps stacking An
                                 Acquired Taste (the fish marks), Tongue Lash flying, hitting, healing him, slowing and
                                 at three stacks stunning; Abyssal Dive - under, the red marker at Darius, up out of the
                                 water, Darius thrown up; two slaps to three stacks; Devour - the chomp, Darius pulled
                                 into the whirl and gone while he digests, spat out; Thick Skin's shell; 3x
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
from build_tahmkench import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_tahmkench")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_tahmkench_fx", "league_tahmkench_big")}
MOUTH = 18                                       # where the tongue leaves: px in front of his pivot
TONGUE = P["q_speed"] / 1000                     # px a tick
GAP = 50                                         # Darius stands this far from his pivot (Tahm is ~50 px wide)


class Foe(Held):
    """Darius, who can also be gone (swallowed)."""

    def __init__(self, sp, x, y):
        super().__init__(sp, x, y)
        self.gone = []

    def frame(self, t):
        if any(t0 <= t < t1 for t0, t1 in self.gone):
            return None
        return super().frame(t)


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_tahmkench_fx"], fx["league_tahmkench_big"]
    W, H = 260, 120
    gy = 88
    x0 = 70
    d = Foe(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + GAP, gy)
    me = Me(x0, gy)
    body, under, over = [], [], []
    hidden = []                                   # Tahm under the ground
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        x, y = me.pos(t)
        an = Anim(dense(sp, tag, "tahmkench", z), t, x, y, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def hit(tag, when, sheet=None, until=None):
        over.append(OnFoe(frames_of(sheet or small, tag), when, d, until=until))
        d.flinches.append(when)

    pips = []

    def stacks(k, when):
        """The fish marks over Darius from `when` (each slot until replaced)."""
        for t0, t1, _ in pips:
            pass
        for i in range(1, k + 1):
            over.append(OnFoe(frames_of(small, f"t_pip{i}"), when, d, until=when + 1e9))
            pips.append((when, None, over[-1]))

    def clear_stacks(when):
        for _, _, an in pips:
            if an.until > when:
                an.until = when
        pips.clear()

    a("idle", 500, loop=True)
    # three slaps: one stack each
    for k in (1, 2, 3):
        land = t + tick(P["atk_st"])
        hit("a_hit", land)
        clear_stacks(land)
        stacks(k, land)
        a("attack", tick(P["atk_dur"]))
        a("idle", 160, loop=True)
    # Tongue Lash: at three stacks it stuns (and eats them)
    rel = t + tick(P["q_at"])
    sx = me.pos(rel)[0] + MOUTH
    arrive = rel + tick(max(1, (d.pos(rel)[0] - sx) / TONGUE))
    over.append(Anim(frames_of(small, "q_tongue"), rel, sx, gy - 5, until=arrive, x1=d.pos(rel)[0], y1=gy - 5))
    hit("q_hit", arrive)
    clear_stacks(arrive)
    over.append(OnFoe(frames_of(small, "q_stun"), arrive, d, until=arrive + tick(P["q_stun"])))
    under.append(OnFoe(frames_of(small, "q_slow"), arrive, d, until=arrive + tick(P["q_slow_t"])))
    over.append(OnMe(frames_of(small, "q_heal"), arrive, me))
    d.holds.append((arrive, arrive + tick(P["q_stun"])))
    a("skill", tick(P["q_dur"]))
    a("idle", 900, loop=True)
    # Abyssal Dive: back off, under, up at Darius, Darius thrown up
    me.moves.append((t, t + 1, me.pos(t)[0], me.pos(t)[0] - 30))
    a("idle", 300, loop=True)
    over.append(OnMe(frames_of(big, "w_down"), t, me))
    sink = t + tick(P["w_sink"])
    a("skill2", tick(P["w_anim"]))
    under.append(Anim(frames_of(big, "w_warn"), sink, d.pos(sink)[0], gy, loop=True, until=sink + tick(P["w_up"])))
    up = sink + tick(P["w_up"])
    hidden.append((t, up))
    t = up
    me.moves.append((up - 1, up, me.pos(up - 1)[0], d.pos(up)[0] - GAP + 14))
    over.append(OnMe(frames_of(big, "w_up"), up, me))
    hit("w_hit", up)
    d.holds.append((up, up + tick(P["w_air"])))
    stacks(1, up)
    a("w_land", tick(P["w_land"]))
    a("idle", 300, loop=True)
    # two slaps to three stacks
    for k in (2, 3):
        land = t + tick(P["atk_st"])
        hit("a_hit", land)
        clear_stacks(land)
        stacks(k, land)
        a("attack", tick(P["atk_dur"]))
        a("idle", 160, loop=True)
    # Devour: the chomp, Darius gone while Tahm digests, spat out
    over.append(OnMe(frames_of(small, "r_gulp"), t, me))
    over.append(OnFoe(frames_of(small, "r_in"), t + 100, d))
    clear_stacks(t + 100)
    gulp = t + 300
    d.gone.append((gulp, gulp + tick(P["r_t"])))
    over.append(OnMe(frames_of(small, "r_full"), gulp, me, until=gulp + tick(P["r_t"])))
    a("ult", tick(P["r_anim"]))
    a("idle", gulp + tick(P["r_t"]) - t, loop=True)
    hit("r_spit", t)
    a("idle", 600, loop=True)
    # Thick Skin
    over.append(OnMe(frames_of(small, "e_shield"), t, me))
    a("idle", 1900, loop=True)
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
        if not any(h0 <= tt < h1 for h0, h1 in hidden):
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_tahmkench_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp_ = load(path)
            rows += [(sp_, t["name"], f"{name[17:]}:{t['name']}") for t in sp_.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_tahmkench_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_tahmkench_showcase.gif")))


if __name__ == "__main__":
    main()
