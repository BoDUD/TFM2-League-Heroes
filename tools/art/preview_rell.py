#!/usr/bin/env python3
"""Preview images for Rell, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_rell.py [--out docs/preview] [--only frames|effects|showcase]

  league_rell_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_rell_effects.png   every effect animation, 3x
  league_rell_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_rell.py, 60 ticks a
                            second): a lance thrust (Break the Mold's cracked plate on him); Full Tilt with Shattering
                            Strike (the surge, the speed, the sigil, the line's guide and the strike, the stun, the
                            blast); Crash Down (the take-off dust, the horse bursting into armour, her landing on foot
                            on him: the crater, the knock-up, her shields, then mounted with the iron scraps round her as
                            the main pack shows the state); Mount Up (the scraps gathering, the charge, the fling and the
                            stun); Magnet Storm (the burst, the field, the yank, the pulses) that kills him; 3x
Spots as tools/art/import_rell_fx.py places them (hits on the body, marks over the head, rings on the ground).
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
from build_rell import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_rell")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_rell_fx", "league_rell_big")}


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_rell_fx"], fx["league_rell_big"]
    W, H = 220, 110
    gy = 84
    x0 = 70
    d = Foe(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 50, gy)     # in her reach (the lance)
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        an = Anim(dense(sp, tag, "rell", z), t, 0, 0, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def wait(ms):
        a("idle", ms, loop=True)

    def on(unit, tag, when, sheet=None, under_=False, until=None):
        o = OnFoe(frames_of(sheet or small, tag), when, unit, until=until)
        (under if under_ else over).append(o)

    wait(500)
    # a lance thrust: Break the Mold's plate over him for p_t ticks
    hit = t + tick(P["atk_st"])
    on(d, "a_hit", hit)
    on(d, "p_shred", hit, until=hit + tick(P["p_t"]))
    d.flinches.append(hit)
    a("attack", tick(P["atk_dur"]))
    wait(tick(P["atk_cd"] - P["atk_dur"]))
    # Full Tilt rides the cast (2 ticks in), then Shattering Strike: the line laid at the cast, its middle q_len / 2 ahead
    q0 = t
    e0 = q0 + tick(2)
    over.append(OnMe(frames_of(small, "e_cast"), e0, me))
    under.append(OnMe(frames_of(small, "e_ms"), e0, me, until=e0 + tick(P["e_t1"] + P["e_t2"])))
    mx, my = me.pos(q0)
    over.append(Anim(frames_of(big, "q_line"), q0 + tick(1), int(round(mx + P["q_len"] / 2000.0)), my))
    strike = q0 + tick(P["q_at"])
    over.append(OnMe(frames_of(small, "e_ready"), e0, me, until=strike))
    on(d, "q_hit", strike)
    on(d, "e_boom", strike)
    on(d, "q_stun", strike, until=strike + tick(P["q_stun"]))
    d.flinches.append(strike)
    a("skill", tick(P["q_anim"]))
    wait(500)
    # Crash Down: the jump on w_jump, the leap onto him (w_speed a tick), the crash where he stands
    w0 = t
    over.append(OnMe(frames_of(big, "w_jump"), w0 + tick(P["w_jump"]), me))
    mx, _ = me.pos(w0)
    dx, dy = d.pos(w0)
    goal = dx - 22
    lift = w0 + tick(P["w_jump"])
    land = max(lift + tick(max(2.0, (goal - mx) / (P["w_speed"] / 1000.0))), w0 + 440)
    me.moves.append((lift, land, mx, goal))
    under.append(Anim(frames_of(big, "w_crash"), land, dx, dy))
    on(d, "w_hit", land)
    d.hops.append((land, land + tick(P["w_up"]), 10))
    over.append(OnMe(frames_of(small, "w_shield"), land, me, until=land + tick(P["w_sh_t"])))
    a("skill2", tick(P["w_anim"]))
    # on foot (the main pack: mounted on screen, the iron scraps round her) - an attack
    foot0 = t
    hit = t + tick(P["atk_st"])
    on(d, "a_hit", hit)
    d.flinches.append(hit)
    a("attack", tick(P["atk_dur"]))
    wait(600)
    # Mount Up: the scraps gather, she charges him: the fling and the stun
    m0 = t
    over.append(OnMe(frames_of(small, "foot"), foot0, me, until=m0))
    over.append(OnMe(frames_of(small, "w2_mount"), m0, me))
    mx, _ = me.pos(m0)
    dx, _ = d.pos(m0)
    arrive = m0 + tick(max(2.0, (dx - 32 - mx) / (P["w2_speed"] / 1000.0)) + 6)
    me.moves.append((m0 + tick(6), arrive, mx, dx - 32))
    on(d, "w2_hit", arrive)
    on(d, "q_stun", arrive, until=arrive + tick(P["w2_stun"]))
    d.slides.append((arrive, arrive + tick(P["w2_kb_t"]), 10))
    d.flinches.append(arrive)
    a("skill2_up", tick(P["w2_anim"]))
    wait(500)
    # Magnet Storm: the burst, the field round her for r_n x r_period ticks, the yank, a pulse every r_period
    r0 = t
    under.append(OnMe(frames_of(big, "r_cast"), r0, me))
    under.append(OnMe(frames_of(big, "r_on"), r0, me, until=r0 + tick(P["r_n"] * P["r_period"])))
    mx, _ = me.pos(r0)
    dx, _ = d.pos(r0)
    d.slides.append((r0 + tick(1), r0 + tick(8), (mx + 34) - dx))
    on(d, "r_yank", r0 + tick(1))
    for k in range(1, P["r_n"] + 1):
        on(d, "r_hit", r0 + tick(k * P["r_period"]))
        d.flinches.append(r0 + tick(k * P["r_period"]))
    d.death = r0 + tick(P["r_n"] * P["r_period"]) + 20
    a("ult", tick(P["r_anim"]))
    wait(tick(P["r_n"] * P["r_period"] - P["r_anim"]) + 1200)
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_rell_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[12:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_rell_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_rell_showcase.gif")))


if __name__ == "__main__":
    main()
