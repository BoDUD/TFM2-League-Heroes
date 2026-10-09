#!/usr/bin/env python3
"""Preview images for Hecarim, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_hecarim.py [--out docs/preview] [--only frames|effects|showcase]

  league_hecarim_frames.png    every animation, frame by frame, 3x on the arena colour
  league_hecarim_effects.png   every effect animation, 3x
  league_hecarim_showcase.gif  a scripted fight with Darius in front and Garen behind him, timed like the kit
                               (tools/kit/build_hecarim.py, 60 ticks a second): Devastating Charge from afar (the dust,
                               the ghost fire under the hooves, the full-power smash knocking Darius back, the haste);
                               a glaive swing; Rampage twice (the sweep, the stacks on his flanks) - the first with
                               Darius near starts Spirit of Dread (the ghosts, the circle, the drain every second); then
                               Onslaught of Shadows at Garen (the shadows rising, the riders cutting through Darius, the
                               landing's shockwave and the fear: Garen flees); 3x
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
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_pyke import Me, OnFoe, OnMe  # noqa: E402
from build_hecarim import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_hecarim")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_hecarim_fx", "league_hecarim_big")}
REACH = 46                                       # his pivot to a foe's in melee (the horse is wide)


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_hecarim_fx"], fx["league_hecarim_big"]
    W, H = 330, 130
    gy = 100
    x0 = 40
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), 160, gy)
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), 270, gy)
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        an = Anim(frames_of(sp, tag), t, 0, gy, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def hit(foe, tag, when, sheet=None):
        over.append(OnFoe(frames_of(sheet or small, tag), when, foe))
        foe.flinches.append(when)

    def at_me(sheet, tag, when, layer, until=None):
        """A picture left where he stands (is_follow false)."""
        x, y = me.pos(when)
        layer.append(Anim(frames_of(sheet, tag), when, x, y, loop=until is not None, until=until))

    def move(t0, x1, speed):
        x = me.pos(t0)[0]
        t1 = t0 + tick(abs(x1 - x) / speed)
        me.moves.append((t0, t1, x, x1))
        return t1

    dread_until = [0.0]

    def dread(when):
        """Spirit of Dread, started by a skill with Darius near (w_cd longer than this fight: once)."""
        if dread_until[0]:
            return
        dread_until[0] = when + tick(P["w_t"])
        at_me(big, "w_start", when, under)
        under.append(OnMe(frames_of(big, "w_aura"), when, me, until=dread_until[0]))
        for k in range(60, P["w_t"] + 1, 60):
            hit(d, "w_hit", when + tick(k))

    a("idle", 500, loop=True)
    # Devastating Charge from afar: dust where he sets off, ghost fire under the hooves, the third rung's smash
    go = t + tick(P["e_go"] - 1)
    at_me(small, "e_dust", t, under)
    land = move(go, d.pos(go)[0] - REACH, P["e_speed"] / 1000)
    under.append(OnMe(frames_of(small, "e_ride"), t, me, until=land))
    a("skill2", land - t, loop=True)
    smash = land + tick(P["e_smash"])
    hit(d, "e_hit", smash)
    kb = P["e_kb_speed"] / 1000 * P["e_kb_t"]
    d.walks.append((smash, smash + tick(P["e_kb_t"]), kb))
    d.holds.append((smash, smash + tick(P["e_kb_t"]) + 200))
    under.append(OnMe(frames_of(small, "e_haste"), land, me, until=land + tick(P["e_haste_t"])))
    a("skill2_hit", tick(14))
    # he follows the knocked-back Darius in, swings, then Rampage (Spirit of Dread starts) and Rampage again
    a("run", move(t, me.pos(t)[0] + kb, 1.2) - t, loop=True)
    hit(d, "a_hit", t + tick(P["a_st"]))
    a("attack", tick(P["atk_dur"]))
    for k in range(2):
        spin = t + tick(P["q_at"])
        at_me(big, "q_spin", spin - tick(2), over)
        hit(d, "q_hit", spin)
        dread(spin)
        over.append(OnMe(frames_of(small, "q2" if k else "q1"), spin, me, until=spin + (tick(P["q_stk_t"]) if k else 900)))
        a("skill", tick(P["q_dur"]))
        if not k:
            hit(d, "a_hit", t + tick(P["a_st"]))
            a("attack", tick(P["atk_dur"]))
    a("idle", 300, loop=True)
    # Onslaught of Shadows at Garen: shadows where he rears, the riders with him, through Darius; the landing fears
    at_me(big, "r_cast", t + tick(1), under)
    go = t + tick(P["r_go"] - 1)
    x_go = me.pos(go)[0]
    land = move(go, g.pos(go)[0] - REACH, P["r_speed"] / 1000)
    under.append(OnMe(frames_of(big, "r_riders"), go, me, until=land, dy=-4))
    passed = go + tick(max(0, (d.pos(go)[0] - x_go) / (P["r_speed"] / 1000)))
    hit(d, "r_hit", passed)
    a("ult", tick(P["r_dur"]))
    if t < land:
        a("ult", land - t)
    at_me(big, "r_land", land, under)
    fear = tick(P["r_fear_far"])
    for foe in (g,):
        hit(foe, "r_fear", land)
        foe.walks.append((land, land + fear, 24))
    over.append(OnMe(frames_of(small, "q2"), land, me, until=land + 1400))
    hit(g, "q_hit", land)
    a("idle", 1600, loop=True)
    end = t

    def place(img, f, px, py):
        img.alpha_composite(f, (px - f.width // 2, py - f.height // 2))

    frames, tt = [], 0.0
    while tt < end:
        img = Image.new("RGBA", (W, H), ARENA)
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
        frames.append(img.resize((W * z, H * z), Image.NEAREST).convert("RGB"))
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
                                os.path.join(args.out, "league_hecarim_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[15:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_hecarim_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_hecarim_showcase.gif")))


if __name__ == "__main__":
    main()
