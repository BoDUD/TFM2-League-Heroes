#!/usr/bin/env python3
"""Preview images for Milio, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_milio.py [--out docs/preview] [--only frames|effects|showcase]

  league_milio_frames.png    every animation's dense frames (hd_, PPU 2.2, as league.dll shows them)
  league_milio_effects.png   every effect animation, 3x
  league_milio_showcase.gif  a scripted fight, Darius in his reach, Garen (his ally) a step ahead of him, timed like
                             the kit (tools/kit/build_milio.py, 60 ticks a second): two fireballs and their hits; Warm
                             Hugs - the warm flame flying from his raised palm to Garen, the hug, the shield on him
                             for e_t, Fired Up! on him, and (W ready) Cozy Campfire under him for w_t with a heal
                             pulse every w_p; Ultra Mega Fire Kick at Darius - the ball, the impact and the knock-back,
                             the ball falling back onto him for q_fall ticks, the landing burst, the flames on him and
                             the embers under his feet (q_slow_t); Breath of Life - the heal on both of them; 3x
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
from preview_annie import Held  # noqa: E402
from preview_ashe import Anim, tick  # noqa: E402
from preview_dense import dense, dense_rows, put  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_kindred import Turned, fx_contact  # noqa: E402
from preview_pyke import Me, OnFoe  # noqa: E402
from build_milio import P, ATK_REL, Q_REL, E_REL, R_REL  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_milio")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_milio_fx", "league_milio_fx_big")}


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_milio_fx"], fx["league_milio_fx_big"]
    W, H = 200, 112
    gy = 80
    x0 = 50
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 53, gy)          # in his reach (53000)
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 22, gy + 6)       # his ally, ahead of him
    g.mirrored = False
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        x, y = me.pos(t)
        an = Anim(dense(sp, tag, "milio", z), t, x, y, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def wait(ms):
        a("idle", ms, loop=True)

    def fly(tag, at, unit, y_offset, speed, sheet=None):
        """A projectile from over his pivot to the unit's pivot; its arrival."""
        lift = (5000 - y_offset) / 1000.0
        mx, my = me.pos(at)
        ux, uy = unit.pos(at)
        x1, y1 = mx, my - lift
        arrive = at + tick(max(1.0, ((ux - x1) ** 2 + (uy - y1) ** 2) ** 0.5 / (speed / 1000.0)))
        over.append(Turned(frames_of(sheet or small, tag), at, int(round(x1)), int(round(y1)), loop=True,
                           until=arrive, x1=ux, y1=uy))
        return arrive

    def on(unit, tag, when, sheet=None, under_=False, until=None):
        o = OnFoe(frames_of(sheet or small, tag), when, unit, until=until)
        (under if under_ else over).append(o)

    def ball(foe, then=True):
        land = fly("a_ball", t + tick(ATK_REL), foe, P["a_y"], P["a_speed"])
        on(foe, "a_hit", land)
        foe.flinches.append(land)
        a("attack", tick(P["atk_dur"]))
        if then:
            wait(tick(P["atk_cd"] - P["atk_dur"]))
        return land

    wait(500)
    for _ in range(2):
        ball(d)
    # Warm Hugs on Garen, Cozy Campfire with it (W ready): the flame leaves his raised palm on E_REL
    land = fly("e_ball", t + tick(E_REL), g, P["e_y"], P["e_speed"])
    a("skill2", tick(P["e_dur"]))
    on(g, "e_hug", land)
    on(g, "e_on", land, until=land + tick(P["e_t"]))
    on(g, "fired", land, until=land + tick(P["p_t"]))
    on(g, "w_fire", land, sheet=big, under_=True, until=land + tick(P["w_t"]))
    for k in range(1, P["w_t"] // P["w_p"] + 1):
        on(g, "w_heal", land + tick(P["w_p"] * k))
    wait(300)
    ball(d)
    # Ultra Mega Fire Kick at Darius: the ball off his foot on Q_REL, the impact and the knock-back, the fall q_fall
    # ticks on where the push left him, the burst, the flames and the embers
    hit = fly("q_ball", t + tick(Q_REL), d, P["q_y"], P["q_speed"])
    a("skill", tick(P["q_dur"]))
    on(d, "q_hit", hit)
    d.flinches.append(hit)
    kb = P["q_kb_speed"] * P["q_kb_t"] / 1000.0
    d.slides.append((hit, hit + tick(P["q_kb_t"]), kb))
    spot = hit + tick(P["q_kb_t"])
    fall = hit + tick(P["q_fall"])
    dx, dyy = d.x + kb, d.y
    over.append(Anim(frames_of(big, "q_fall"), spot, int(dx), dyy, until=fall))
    over.append(Anim(frames_of(big, "q_land"), fall, int(dx), dyy))
    on(d, "q_burn", fall)
    on(d, "q_slow", fall, under_=True, until=fall + tick(P["q_slow_t"]))
    d.flinches.append(fall)
    wait(500)
    ball(d)
    # Breath of Life: the heal on him and Garen R_REL into the cast
    r = t + tick(R_REL)
    on(me, "r_hit", r)
    on(g, "r_hit", r)
    a("ult", tick(P["r_anim"]))
    wait(300)
    for _ in range(2):
        ball(d)
    wait(600)
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
        units = [(d.pos(tt)[1], d.frame(tt), d.pos(tt)), (g.pos(tt)[1], g.frame(tt), g.pos(tt))]
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_milio_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_milio_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_milio_showcase.gif")))


if __name__ == "__main__":
    main()
