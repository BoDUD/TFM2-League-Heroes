#!/usr/bin/env python3
"""Preview images for Maokai, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_maokai.py [--out docs/preview] [--only frames|effects|showcase]

  league_maokai_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_maokai_effects.png   every effect animation, 3x
  league_maokai_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_maokai.py, 60 ticks a
                              second), as the main pack shows it: Sapling Toss - the sapling flying, landing, standing
                              guard and pouncing on Darius; Twisted Advance - he sinks into the ground, the roots run to
                              Darius under it, he bursts out and roots him; Bramble Smash - the slam, Darius knocked back,
                              the shockwave running on; Sap Magic's blow and heal; Nature's Grasp - the slam, the wall
                              of brambles advancing, rooting Darius, his haste; 3x
"""
import argparse
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
from preview_ashe import Anim, tick  # noqa: E402
from preview_dense import dense, dense_rows, put  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_kindred import fx_contact  # noqa: E402
from preview_leesin import Foe  # noqa: E402
from preview_pyke import Me, OnFoe, OnMe  # noqa: E402
from build_maokai import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_maokai")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_maokai_fx", "league_maokai_big")}
U = 1000.0                                            # world units a game pixel


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_maokai_fx"], fx["league_maokai_big"]
    W, H = 300, 136
    gy = 100
    x0 = 80
    d = Foe(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 70, gy)
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        an = Anim(dense(sp, tag, "maokai", z), t, 0, 0, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def wait(ms):
        if ms > 0:
            a("idle", ms, loop=True)

    def on(unit, tag, when, sheet=None, under_=False, until=None):
        o = OnFoe(frames_of(sheet or small, tag), when, unit, until=until)
        (under if under_ else over).append(o)

    def on_me(tag, when, sheet=None, under_=False, until=None):
        o = OnMe(frames_of(sheet or small, tag), when, me, until=until)
        (under if under_ else over).append(o)

    def at_spot(tag, when, x, y, sheet=None, under_=False, until=None):
        an = Anim(frames_of(sheet or small, tag), when, int(x), int(y), loop=until is not None, until=until)
        (under if under_ else over).append(an)

    def fly(tag, when, sx, x1, speed, sheet=None, under_=False):
        """A projectile from (sx, gy) to x1 at `speed` world units a tick, its picture looping."""
        arrive = when + tick(max(1.0, abs(x1 - sx) * U / speed))
        an = Anim(frames_of(sheet or small, tag), when, int(sx), gy, loop=True, until=arrive, x1=int(x1), y1=gy)
        (under if under_ else over).append(an)
        return arrive

    def attack(sap=False):
        hit = t + tick(P["a_hit"])
        on(d, "a_hit", hit)
        d.flinches.append(hit)
        if sap:
            on(d, "p_hit", hit)
            on_me("p_heal", hit, big)
        a("attack", tick(P["atk_dur"]))
        wait(tick(P["atk_cd"] - P["atk_dur"]))
        return hit

    wait(500)
    # Sapling Toss (the watch throws it): the lob to a spot in front of Darius, it plants, stands guard e_arm ticks,
    # Darius is within e_trig: it pounces, the blast and the slow
    rel = t + tick(P["e_rel"])
    spot = d.x - 10
    land = rel + tick(P["e_travel"])
    over.append(Anim(frames_of(small, "e_lob"), rel, me.pos(rel)[0] + 8, gy - 24, loop=True, until=land, x1=spot, y1=gy))
    at_spot("e_land", land, spot, gy, under_=True)
    armed = land + tick(P["e_arm"])
    at_spot("e_idle", armed, spot, gy, under_=True, until=armed + 500)
    burst = armed + 500
    on(d, "e_burst", burst, big)
    on(d, "e_hit", burst + 180)
    d.flinches.append(burst + 180)
    on(d, "e_slow", burst + 180, under_=True, until=burst + 180 + tick(P["e_slow_t"]))
    a("skill_e", tick(P["e_dur"]))
    wait(burst + 900 - t)
    # Twisted Advance: he sinks, the roots run under the ground to Darius at w_speed, he bursts out beside him: the root
    go = t
    stop = d.x - 30
    arrive = fly("w_trail", go, me.pos(go)[0], stop, P["w_speed"], big, under_=True)
    me.moves.append((go, arrive, me.pos(go)[0], stop))
    a("skill2", max(tick(P["w_dash"]), arrive - go))
    on_me("w_land", t, big, under_=True)
    on(d, "w_hit", t)
    d.flinches.append(t)
    on(d, "root", t, until=t + tick(P["w_root"]))
    a("skill2_land", tick(P["w_land"]))
    # the pro combo W -> Q: Bramble Smash at once - the slam, Darius knocked back, the shockwave running on
    rel = t + tick(P["q_rel"])
    on_me("q_cast", rel, big, under_=True)
    fly("q_wave", rel, me.pos(rel)[0], me.pos(rel)[0] + P["q_len"] / U, P["q_speed"], big, under_=True)
    on(d, "q_hit", rel + tick(2))
    d.slides.append((rel, rel + tick(P["q_kb_t"]), P["q_kb_s"] * P["q_kb_t"] / U))
    on(d, "q_slow", rel + tick(2), under_=True, until=rel + tick(P["q_s2t"]))
    a("skill", tick(P["q_dur"]))
    wait(300)
    # Sap Magic: the next blow deals more and heals him (his reach: he steps after Darius knocked back)
    step_to = d.pos(t)[0] - 30
    me.moves.append((t, t + 240, me.pos(t)[0], step_to))
    a("run", 240, loop=True)
    attack(sap=True)
    attack()
    # Nature's Grasp: the slam, the wall advancing at r_speed, rooting Darius (the longer step: it went farther), haste
    rel = t + tick(P["r_rel"])
    on_me("r_cast", rel, big, under_=True)
    sx = me.pos(rel)[0]
    reach = fly("r_wall", rel, sx, d.pos(rel)[0], P["r_speed"], big, under_=True)
    fly("r_wall", reach, d.pos(rel)[0], d.pos(rel)[0] + 30, P["r_speed"], big, under_=True)
    on(d, "r_hit", reach)
    d.flinches.append(reach)
    on(d, "root", reach, until=reach + tick(P["r_b2"]))
    on_me("r_haste", reach, big, under_=True, until=reach + tick(P["r_ms_t"]))
    a("ult", tick(P["r_dur"]))
    wait(reach + 1400 - t)
    end_all = t

    def place(img, f, px, py):
        put(img, f, px, py, z)

    frames, tt = [], 0.0
    while tt < end_all:
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
    return len(frames), round(end_all / 1000.0, 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    ap.add_argument("--only", choices=["frames", "effects", "showcase"])
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    if args.only in (None, "frames"):
        s = load(CHAMP)
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_maokai_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_maokai_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_maokai_showcase.gif")))


if __name__ == "__main__":
    main()
