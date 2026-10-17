#!/usr/bin/env python3
"""Preview images for Nasus, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_nasus.py [--out docs/preview] [--only frames|effects|showcase]

  league_nasus_frames.png    every animation's dense frames (hd_, PPU 1.2, as league.dll shows them)
  league_nasus_effects.png   every effect animation, 3x
  league_nasus_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_nasus.py, 60 ticks a
                             second), as the main pack shows it: staff blows; Wither - the far hand thrust, the strike
                             and the withering glyph over Darius; Siphoning Strike; Spirit Fire - the beam, the burst,
                             the burning rune circle under Darius and the cracked shield over him; Fury of the Sands -
                             the burst, the sandstorm round him, its bites every half second; the big body's blows and a
                             last Siphoning Strike that kills - the soul drawn into him; 3x
Main pack only: his idle stays the normal body between the big body's casts (the add-on swaps the whole body).
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
from build_nasus import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_nasus")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_nasus_fx", "league_nasus_big")}


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_nasus_fx"], fx["league_nasus_big"]
    W, H = 300, 136
    gy = 100
    x0 = 120
    d = Foe(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 30, gy)     # in his reach
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        an = Anim(dense(sp, tag, "nasus", z), t, 0, 0, loop=loop, until=(t + dur) if dur else None)
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

    def at_spot(tag, when, x, y, sheet=None, under_=False):
        an = Anim(frames_of(sheet or small, tag), when, int(x), int(y))
        (under if under_ else over).append(an)

    def attack(tag="attack"):
        hit = t + tick(P["a_hit"])
        on(d, "a_hit", hit)
        d.flinches.append(hit)
        a(tag, tick(P["atk_dur"]))
        wait(tick(P["atk_cd"] - P["atk_dur"]))
        return hit

    def strike(tag="skill"):
        hit = t + tick(P["q_hit"])
        on(d, "q_hit", hit)
        d.flinches.append(hit)
        a(tag, tick(P["q_dur"]))
        return hit

    wait(400)
    attack()
    # Wither: the watch casts it in the fight - the far hand thrust, the hidden bolt (6000 a tick), the glyph for w_t
    rel = t + tick(P["w_rel"])
    hit = rel + tick(max(1.0, (d.x - me.x) * 1000 / 6000))
    on(d, "w_hit", hit)
    d.flinches.append(hit)
    on(d, "w_slow", hit, until=hit + tick(P["w_t"]))
    a("skill_w", tick(P["w_dur"]))
    wait(300)
    attack()
    strike()
    wait(400)
    # Spirit Fire: the hidden lob lands where Darius stood (e_travel after e_rel): the burst, the circle for e_t,
    # the armour shred from its first burning tick
    land = t + tick(P["e_rel"] + P["e_travel"])
    at_spot("e_fire", land, *d.pos(land), big, under_=True)
    on(d, "e_hit", land)
    d.flinches.append(land)
    on(d, "e_shred", land + tick(P["e_p"]), until=land + tick(P["e_t"]))
    a("skill2", tick(P["e_dur"]))
    attack()
    # Fury of the Sands: the press arms it, the watch raises it (a fight with a champion close)
    a("idle", tick(3))
    rise = t
    at_spot("r_cast", rise, *me.pos(rise), big)
    on_t = rise + tick(P["r_on_at"])
    a("ult", tick(P["r_dur"]))
    wait(200)
    attack("b_attack")
    attack("b_attack")
    kill = strike("b_skill")
    d.death = kill + 60
    on_me("q_soul", kill + 160)
    wait(1400)
    end = t
    on_me("r_on", on_t, big, under_=True, until=end)
    k = 0
    while on_t + tick(P["r_p"] * k) < d.death:
        on(d, "r_hit", on_t + tick(P["r_p"] * k))
        k += 1
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_nasus_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_nasus_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_nasus_showcase.gif")))


if __name__ == "__main__":
    main()
