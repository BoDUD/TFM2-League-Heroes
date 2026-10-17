#!/usr/bin/env python3
"""Preview images for Pantheon, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_pantheon.py [--out docs/preview] [--only frames|effects|showcase]

  league_pantheon_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_pantheon_effects.png   every effect animation, 3x
  league_pantheon_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_pantheon.py, 60
                                ticks a second): Mortal Will's flare (full at the start), a thrust; Comet Spear's tap
                                (the thrust's light along its line); Darius backs off - the throw, the comet spear; Shield
                                Vault onto him and the stun; the empowered attack's three thrusts; Aegis Assault - the
                                shield's light, the stabs, the bash's shockwave; Grand Starfall - the crouch's gathering
                                light, the leap, the landing ring and the spear falling on it, the landing's blast that
                                kills him; 3x
Projectiles fly as the kit flies them: lifted 5000 - y_offset over his pivot, at the target's pivot, turned to their
way (champion-data section 6).
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
from preview_kindred import Turned, fx_contact  # noqa: E402
from preview_leesin import Foe  # noqa: E402
from preview_pyke import Me, OnFoe, OnMe  # noqa: E402
from build_pantheon import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_pantheon")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_pantheon_fx", "league_pantheon_big")}


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_pantheon_fx"], fx["league_pantheon_big"]
    W, H = 300, 120
    gy = 86
    x0 = 90
    d = Foe(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 28, gy)     # in his reach
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        an = Anim(dense(sp, tag, "pantheon", z), t, 0, 0, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def wait(ms):
        a("idle", ms, loop=True)

    def on(unit, tag, when, sheet=None, under_=False, until=None):
        o = OnFoe(frames_of(sheet or small, tag), when, unit, until=until)
        (under if under_ else over).append(o)

    def at_spot(tag, when, x, y, sheet=None, under_=False):
        an = Anim(frames_of(sheet or small, tag), when, int(x), int(y))
        (under if under_ else over).append(an)

    # Mortal Will full at the start: the flare
    over.append(OnMe(frames_of(small, "p_ready"), 0, me))
    wait(500)
    # a thrust
    hit = t + tick(P["a_st"])
    on(d, "a_hit", hit)
    d.flinches.append(hit)
    a("attack", tick(P["atk_dur"]))
    wait(tick(P["atk_cd"] - P["atk_dur"]))
    # Comet Spear, the tap: the thrust's light along its line (q_len from him toward Darius, its middle on the line)
    rel = t + tick(1 + 2 + P["q_t_at"] - 3)
    mx, my = me.pos(rel)
    mid = mx + P["q_len"] / 2000.0
    over.append(Anim(frames_of(big, "q_thrust"), rel, int(round(mid)), my))
    on(d, "q_hit", rel + tick(1))
    d.flinches.append(rel + tick(1))
    a("skill", tick(P["q_dur"]))
    wait(300)
    # Darius backs off; the throw: the comet spear flies from over his pivot to Darius's pivot
    d.slides.append((t, t + 300, 40))
    wait(320)
    t0 = t + tick(3)
    a("idle", tick(3))
    rel = t + tick(P["q_hold"])
    mx, my = me.pos(rel)
    lift = (5000 + 3000) / 1000.0
    dx, dy = d.pos(rel)
    arrive = rel + tick(max(1.0, abs(dx - mx) / (P["q_speed"] / 1000.0)))
    over.append(Turned(frames_of(small, "q_spear"), rel, int(mx), int(my - lift), loop=True, until=arrive, x1=dx, y1=dy))
    on(d, "q_hit", arrive)
    d.flinches.append(arrive)
    a("skill_throw", tick(P["q_anim"]))
    wait(300)
    # Shield Vault: he leaps onto Darius (w_speed a tick), the slam stuns
    mx, _ = me.pos(t)
    dx, _ = d.pos(t)
    goal = dx - 22
    land = t + tick(max(2.0, (goal - mx) / (P["w_speed"] / 1000.0)))
    me.moves.append((t, land, mx, goal))
    on(d, "w_hit", land)
    d.flinches.append(land)
    d.flinches.append(land + tick(P["w_stun"]) / 2)
    a("skill2", tick(P["w_dur"]))
    wait(150)
    # the empowered attack: three thrusts
    base = t + tick(P["a_st"])
    for k in (1, 2, 3):
        hk = base + tick(P[f"w_tri_at{k}"])
        on(d, "a_hit", hk)
        d.flinches.append(hk)
    a("attack", tick(P["a_st"]))
    a("attack_w", tick(P["w_tri_anim"]))
    wait(300)
    # Aegis Assault: the shield's light while he holds it, the stabs, then the bash
    e0 = t
    under.append(OnMe(frames_of(big, "e_shield"), e0, me, until=e0 + tick(P["e_t"])))   # behind him (z -1)
    gap = P["e_t"] // (P["e_n"] + 1)
    for k in range(1, P["e_n"] + 1):
        on(d, "e_stab", e0 + tick(k * gap))
    a("e_hold", tick(P["e_t"]), loop=True)
    bash = t + tick(P["e_bash_at"])
    mx, my = me.pos(bash)
    at_spot("e_bash", bash, mx, my, big, under_=True)
    on(d, "e_hit", bash)
    d.flinches.append(bash)
    a("e_bash", tick(P["e_bash_t"]))
    over.append(OnMe(frames_of(small, "e_def"), t, me, until=t + 900))
    wait(700)
    # Grand Starfall: he steps back first (the spot he falls on is Darius's)
    me.moves.append((t, t + 250, me.pos(t)[0], me.pos(t)[0] - 60))
    a("run", 250, loop=True)
    r0 = t
    under.append(OnMe(frames_of(big, "r_cast"), r0, me))   # behind him (z -1)
    a("ult", tick(P["r_ch"]))
    leap = t
    a("ult_leap", tick(P["r_leap"]))
    dx, dy = d.pos(leap)
    at_spot("r_mark", leap, dx, dy, big, under_=True)
    at_spot("r_spear", leap, dx, dy, big)
    strike = leap + tick(P["r_sp"])
    on(d, "r_sp_hit", strike)
    d.flinches.append(strike)
    on(d, "r_slow", strike, under_=True, until=strike + tick(P["r_slow_t"]))
    # gone into the sky until the landing, then on the spot
    landing = leap + tick(P["r_fall"])
    t = landing
    me.moves.append((landing - 1, landing, me.pos(landing - 2)[0], dx))
    blast = landing + tick(P["r_hit_at"])
    at_spot("r_land", blast, dx, dy, big, under_=True)
    on(d, "r_hit", blast)
    d.death = blast + tick(2)
    a("ult_land", tick(P["r_land"]))
    wait(1200)
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_pantheon_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[16:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_pantheon_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_pantheon_showcase.gif")))


if __name__ == "__main__":
    main()
