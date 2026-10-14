#!/usr/bin/env python3
"""Preview images for Bard, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_bard.py [--out docs/preview] [--only frames|effects|showcase]

  league_bard_frames.png    every animation's frames (1x, as the game draws them), 3x
  league_bard_effects.png   every effect animation, 3x
  league_bard_showcase.gif  a scripted fight with Darius in front of him, Jinx behind Darius and Garen behind Bard,
                            timed like the kit (tools/kit/build_bard.py, 60 ticks a second): a star bolt with a Meep
                            (the burst, the slow); Cosmic Binding through Darius into Jinx (both bound); the Caretaker's
                            Shrine on Garen (the heal, the haste); Tempered Fate on the two of them (the orb, the dome,
                            the golden statues, freed); then the add-on's Magical Journey (addons/league_bard): the
                            portal opens at his back, he stands in it, flies through with Garen and comes out of the
                            exit portal, both hasted; 3x
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
from preview_dense import put  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_jinx import Arc  # noqa: E402
from preview_pyke import Me, OnFoe, OnMe  # noqa: E402
from build_bard import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_bard")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_bard_fx", "league_bard_big")}
HAND = 8                                         # the bolts leave 8 px in front of his pivot
STAND, OUT_STAND = 24, 24                        # addons/league_bard: ticks in the open portal / at the exit


class Unit(Held):
    """A champion that can also be hidden (banished: only the statue shows)."""

    def __init__(self, sp, x, y, mirror=True):
        super().__init__(sp, x, y)
        self.mirrored = mirror
        self.hides = []

    def frame(self, t):
        if any(t0 <= t < t1 for t0, t1 in self.hides):
            return None
        return super().frame(t)


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_bard_fx"], fx["league_bard_big"]
    W, H = 300, 120
    gy = 84
    x0 = 150
    d = Unit(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 68, gy)
    j = Unit(load(os.path.join(LEAGUE, "champions", "league_jinx")), x0 + 104, gy)
    g = Unit(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 - 40, gy, mirror=False)
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        an = Anim(frames_of(sp, tag), t, 0, 0, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def hit(foe, tag, when, sheet=None):
        over.append(OnFoe(frames_of(sheet or small, tag), when, foe))
        foe.flinches.append(when)

    def fly(tag, when, x1, speed, dy=-1):
        sx = me.pos(when)[0] + HAND
        arrive = when + tick(max(1, (x1 - sx) / speed))
        over.append(Anim(frames_of(small, tag), when, sx, gy + dy, until=arrive, x1=x1, y1=gy + dy))
        return arrive

    a("idle", 500, loop=True)
    # a star bolt and a Meep: the burst on Darius slows him (and Jinx beside him)
    rel = t + tick(P["atk_st"])
    land = fly("a_bolt", rel, d.pos(rel)[0], P["a_speed"] / 1000)
    hit(d, "a_hit", land)
    meep = fly("p_meep", rel + tick(4), d.pos(rel)[0], P["p_speed"] / 1000, dy=-3)
    over.append(OnFoe(frames_of(small, "p_hit"), meep, d))
    for foe in (d, j):
        under.append(OnFoe(frames_of(small, "p_slow"), meep, foe, until=meep + tick(P["p_slow_t"])))
    a("attack", tick(P["atk_dur"]))
    a("idle", 300, loop=True)
    # Cosmic Binding: through Darius into Jinx behind him - both bound
    rel = t + tick(P["q_st"])
    first = fly("q_bolt", rel, d.pos(rel)[0], P["q_speed"] / 1000)
    hit(d, "q_hit", first)
    second = first + tick((j.x - d.x) * 1000 / P["q_speed"])
    hit(j, "q_hit", second)
    for foe, at in ((j, second), (d, first + tick(P["q_win"] + 1))):
        over.append(OnFoe(frames_of(small, "q_bind"), at, foe, until=at + tick(P["q_stun"])))
        foe.holds.append((at, at + tick(P["q_stun"])))
    a("skill", tick(P["q_dur"]))
    a("idle", 200, loop=True)
    # the Caretaker's Shrine on Garen: the heal and the haste
    rel = t + tick(P["w_lag"])
    land = rel + tick((me.pos(rel)[0] - g.x) * 1000 / P["w_speed"])
    over.append(Arc(frames_of(small, "w_shrine"), rel, me.pos(rel)[0], gy - 6, until=land, x1=g.x, y1=gy, h=10))
    over.append(OnFoe(frames_of(small, "w_land"), land, g))
    under.append(OnFoe(frames_of(small, "w_haste"), land, g, until=land + tick(P["w_ms_t"])))
    a("skill2", tick(P["w_dur"]))
    a("idle", max(300, d.holds[0][1] - t - 600), loop=True)
    # Tempered Fate on the two of them: the orb, the dome, the statues, freed
    rel = t + tick(P["r_lag"])
    mid = (d.x + j.x) // 2
    land = rel + tick(P["r_travel"])
    over.append(Arc(frames_of(big, "r_orb"), rel, me.pos(rel)[0] + HAND, gy - 8, until=land, x1=mid, y1=gy - 6, h=16))
    under.append(Anim(frames_of(big, "r_mark"), rel, mid, gy, until=land, loop=True))
    end_r = land + tick(P["r_t"])
    under.append(Anim(frames_of(big, "r_dome"), land, mid, gy, until=end_r))
    for foe in (d, j):
        foe.hides.append((land, end_r))
        over.append(OnFoe(frames_of(big, "r_lock"), land, foe, until=end_r))
        over.append(OnFoe(frames_of(big, "r_free"), end_r, foe))
    a("ult", tick(P["r_anim"]))
    a("idle", end_r - t + 300, loop=True)
    # Magical Journey (the add-on): the portal at his back, he stands in it, flies through with Garen, the exit portal
    door = me.pos(t)[0]
    exit_x = 70
    under.append(Anim(frames_of(big, "e_portal"), t + tick(P["e_wind"]), door, gy, until=t + tick(STAND)))
    a("skill2_e", tick(STAND))
    go = t
    dur = tick((door - exit_x) * 1000 / P["e_fly"])
    me.moves.append((go, go + dur, door, exit_x))
    g.slides.append((go, go + dur, exit_x - 34 - g.x))
    over.append(OnFoe(frames_of(small, "e_ride"), go, g, until=go + dur))
    a("run", dur, loop=True)
    arrive = t
    under.append(Anim(frames_of(big, "e_portal_out"), arrive, exit_x, gy, until=arrive + tick(OUT_STAND)))
    a("skill2_e", tick(OUT_STAND))
    for who in (me, g):
        under.append(OnFoe(frames_of(small, "e_haste"), arrive, who, until=arrive + tick(P["e_ms_t"])))
    a("idle", tick(P["e_ms_t"]) + 400, loop=True)
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
        units = [(u.pos(tt)[1], u.frame(tt), u.pos(tt)) for u in (g, d, j)]
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
        print("frames", contact([(s, t["name"], t["name"]) for t in s.tags],
                                os.path.join(args.out, "league_bard_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[12:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_bard_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_bard_showcase.gif")))


if __name__ == "__main__":
    main()
