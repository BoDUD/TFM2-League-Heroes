#!/usr/bin/env python3
"""Preview images for Orianna, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_orianna.py [--out docs/preview] [--only frames|effects|showcase]

  league_orianna_frames.png    every animation's dense frames (hd_, PPU 2.2, as league.dll shows them)
  league_orianna_effects.png   every effect animation, 3x
  league_orianna_showcase.gif  a scripted fight, Darius in her reach, Garen (her ally) a step ahead of her, timed like
                               the kit (tools/kit/build_orianna.py, 60 ticks a second): the Ball floating beside her,
                               two clockwork bolts and their hits; Command: Attack - the Ball flies to Darius's feet,
                               the landing burst and the hit, then it lies there; Command: Dissonance going off by
                               itself at the Ball - the pulse, the zap, the slow under Darius and the haste under Garen;
                               a bolt; Command: Protect - the Ball flies to Garen, the shield, the Ball riding him;
                               Command: Shockwave at the Ball on Garen - the gathering, the blast that flings Darius
                               toward it and kills him; 3x
Projectiles fly as the kit flies them: lifted 5000 - y_offset over her pivot, at the target's pivot, turned to their
way (champion-data section 6); the thrown Ball lands on the spot Darius stood on.
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
from build_orianna import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_orianna")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_orianna_fx", "league_orianna_big")}


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_orianna_fx"], fx["league_orianna_big"]
    W, H = 220, 128
    gy = 82
    x0 = 50
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + P["atk_range"] // 1000, gy)   # in her reach
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 34, gy + 22)     # her ally, ahead of her
    g.mirrored = False
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        x, y = me.pos(t)
        an = Anim(dense(sp, tag, "orianna", z), t, x, y, loop=loop, until=(t + dur) if dur else None)
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

    def bolt():
        land = fly("a_bolt", t + tick(P["a_st"]), d, P["bolt_y"], P["bolt_speed"])
        on(d, "a_hit", land)
        d.flinches.append(land)
        a("attack", tick(P["atk_dur"]))
        wait(tick(P["atk_cd"] - P["atk_dur"]))

    wait(500)
    bolt()
    bolt()
    # Command: Attack: the Ball leaves her side on the cast's start and lands q_travel ticks later where Darius stood
    throw = t + tick(P["q_st"])
    home_until = throw
    mx, my = me.pos(throw)
    spot = d.pos(throw)
    land = throw + tick(P["q_travel"])
    over.append(Turned(frames_of(small, "ball_fly"), throw, mx, my, loop=True, until=land, x1=spot[0], y1=spot[1]))
    at_spot("q_land", land, *spot, under_=True)
    on(d, "q_hit", land)
    d.flinches.append(land)
    a("skill", tick(P["q_dur"]))
    # Command: Dissonance: W is ready, an enemy champion stands at the Ball - it goes off at the next checkpoint
    w_at = land + tick(P["b_step"])
    wait(max(0.0, w_at - t))
    at_spot("w_ring", w_at, *spot, sheet=big, under_=True)
    on(d, "w_hit", w_at)
    d.flinches.append(w_at)
    on(d, "w_slow", w_at, under_=True, until=w_at + tick(P["w_t"]))
    on(g, "w_haste", w_at, under_=True, until=w_at + tick(P["w_t"]))
    a("skill_w", tick(P["w_anim"]))
    wait(200)
    bolt()
    # Command: Protect: the Ball leaves the ground and flies from her hand to Garen, the shield on arrival, then it rides him
    send = t + tick(P["e_st"])
    lying_until = send
    arrive = fly("ball_fly", send, g, P["e_y"], P["e_speed"])
    on(g, "e_shield", arrive)
    a("skill_e", tick(P["e_dur"]))
    wait(400)
    bolt()
    # Command: Shockwave at the Ball on Garen: the gathering, the blast r_delay ticks in flings Darius toward it
    r0 = t
    gx, gy_ = g.pos(r0)
    at_spot("r_wave", r0, gx, gy_, sheet=big, under_=True)
    blast = r0 + tick(P["r_delay"])
    on(d, "r_hit", blast)
    pull = -min(P["r_pull"] * P["r_pull_t"] / 1000.0, max(0.0, d.pos(blast)[0] - gx - 10))
    d.slides.append((blast, blast + tick(P["r_pull_t"]), pull))
    d.death = blast + tick(P["r_pull_t"])
    a("ult", tick(P["r_anim"]))
    wait(1300)
    end = t
    # the Ball's three places: beside her, lying on the ground (re-stamped every b_step), on Garen
    over.append(OnMe(frames_of(small, "ball_side"), 0, me, until=home_until))
    k = land
    while k < lying_until:
        at_spot("ball_ground", k, *spot)       # z 1: over the units
        k += tick(P["b_step"])
    over.append(OnFoe(frames_of(small, "ball_side"), arrive, g, until=end))

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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_orianna_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[15:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_orianna_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_orianna_showcase.gif")))


if __name__ == "__main__":
    main()
