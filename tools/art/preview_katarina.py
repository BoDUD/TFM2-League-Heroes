#!/usr/bin/env python3
"""Preview images for Katarina, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_katarina.py [--out docs/preview] [--only frames|effects|showcase]

  league_katarina_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_katarina_effects.png   every effect animation, 3x
  league_katarina_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_katarina.py, 60
                                ticks a second): two stabs; Bouncing Blade - the spinning blade, the hit, the dagger
                                flying up off him and falling where he stood, Shunpo onto it (vanish, arrival), the
                                pick-up spin; Preparation with Shunpo in - the vanish, the arrival and strike beside
                                him, the dagger tossed up, the haste, two stabs, the dagger falling at her feet and the
                                spin; Death Lotus - the whirl of blades, a dagger at him every r_p ticks, the grievous
                                wounds; Voracity's reset; 3x
Projectiles fly as the kit flies them: lifted 5000 - y_offset over her pivot, at the target's pivot, turned to their
way (champion-data section 6).
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
from preview_kindred import Turned, fx_contact  # noqa: E402
from preview_pyke import Me, OnFoe, OnMe  # noqa: E402
from build_katarina import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_katarina")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_katarina_fx", "league_katarina_big")}
FEET = 11


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_katarina_fx"], fx["league_katarina_big"]
    W, H = 220, 112
    gy = 80
    x0 = 60
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 22, gy)        # in her dagger's reach
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        x, y = me.pos(t)
        an = Anim(dense(sp, tag, "katarina", z), t, x, y, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def wait(ms):
        a("idle", ms, loop=True)

    def fly(tag, at, unit, y_offset, speed):
        """A projectile from over her pivot to the unit's pivot; its arrival."""
        lift = (5000 - y_offset) / 1000.0
        mx, my = me.pos(at)
        ux, uy = unit.pos(at)
        x1, y1 = mx, my - lift
        arrive = at + tick(max(1.0, ((ux - x1) ** 2 + (uy - y1) ** 2) ** 0.5 / (speed / 1000.0)))
        over.append(Turned(frames_of(small, tag), at, int(round(x1)), int(round(y1)), loop=True,
                           until=arrive, x1=ux, y1=uy))
        return arrive

    def on(unit, tag, when, sheet=None, under_=False, until=None):
        o = OnFoe(frames_of(sheet or small, tag), when, unit, until=until)
        (under if under_ else over).append(o)

    def at_spot(tag, when, x, y, sheet=None, under_=False, until=None):
        an = Anim(frames_of(sheet or small, tag), when, int(x), int(y), loop=until is not None, until=until)
        (under if under_ else over).append(an)

    def stab():
        hit = t + tick(P["atk_st"])
        on(d, "a_hit", hit)
        d.flinches.append(hit)
        a("attack", tick(P["atk_dur"]))
        wait(tick(P["atk_cd"] - P["atk_dur"]))

    def blink(to_x, to_y=gy):
        """Shunpo: the vanish where she stands, the arrival where she lands."""
        mx, my = me.pos(t)
        at_spot("e_out", t, mx, my)
        me.moves.append((t, t + tick(1), mx, to_x))
        at_spot("e_in", t + tick(1), to_x, to_y)
        a("blink", tick(P["e_anim"]))

    def spin():
        nonlocal t
        mx, my = me.pos(t)
        at_spot("spin", t, mx, my, big)
        on(d, "p_hit", t + tick(2))
        d.flinches.append(t + tick(2))
        a("spin", tick(P["p_anim"]))

    wait(500)
    stab()
    stab()
    # Bouncing Blade: the blade from her hand to Darius, the hit, the dagger up off him and down where he stood
    throw = t + tick(P["q_at"])
    hit = fly("q_blade", throw, d, P["q_y"], P["q_speed"])
    on(d, "q_hit", hit)
    on(d, "q_arc", hit)
    d.flinches.append(hit)
    land = hit + tick(P["q_fall"])
    dx = d.pos(hit)[0]
    a("skill", tick(P["q_dur"]))
    wait(max(0, land - t))
    # Shunpo onto the landed dagger (it is under Darius): vanish, arrive, the pick-up spin
    at_spot("d_fall", land, dx, gy, under_=True)
    blink(dx - 2)
    spin()
    wait(300)
    # Preparation with Shunpo in: she steps back first (walks), then blinks beside him, strikes, tosses the dagger up
    sx = me.pos(t)[0]
    me.moves.append((t, t + 500, sx, sx - 30))
    a("run", 500, loop=True)
    on(d, "e_hit", t + tick(1))
    d.flinches.append(t + tick(1))
    blink(d.pos(t)[0] - 18)
    toss = t + tick(P["w_at"])
    mx, my = me.pos(toss)
    at_spot("w_toss", toss, mx, my)
    under.append(OnMe(frames_of(small, "w_ms"), t, me, until=t + tick(P["w_fall"])))
    a("skill2", tick(P["w_dur"]))
    fall = toss + tick(P["w_fall"])
    stab()
    wait(max(0, fall - t))
    at_spot("d_fall", fall, mx, gy, under_=True)
    spin()
    wait(300)
    # Death Lotus: the whirl, a dagger at Darius every r_p ticks, grievous wounds
    r0 = t
    for k in range(0, P["r_t"], P["r_ring"]):
        over.append(OnMe(frames_of(big, "r_lotus"), r0 + tick(k), me, until=r0 + tick(k + P["r_ring"])))
    for k in range(0, P["r_t"], P["r_p"]):
        h = fly("r_dagger", r0 + tick(k), d, P["r_y"], P["r_speed"])
        on(d, "r_hit", h)
        d.flinches.append(h)
    on(d, "r_gw", r0 + tick(8), until=r0 + tick(P["r_t"] + P["r_gw_t"]))
    a("ult", tick(P["r_t"]), loop=True)
    # Voracity: the reset
    over.append(OnMe(frames_of(small, "p_reset"), t, me))
    wait(1000)
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_katarina_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[16:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_katarina_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_katarina_showcase.gif")))


if __name__ == "__main__":
    main()
