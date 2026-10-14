#!/usr/bin/env python3
"""Preview images for Malzahar, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_malzahar.py [--out docs/preview] [--only frames|effects|showcase]

  league_malzahar_frames.png    every animation's dense frames (hd_, PPU 1.38, as league.dll shows them)
  league_malzahar_effects.png   every effect animation, 3x
  league_malzahar_showcase.gif  a scripted fight, Darius in his reach, Garen a row behind him, timed like the kit
                                (tools/kit/build_malzahar.py, 60 ticks a second): Void Shift's shell round him; two
                                void bolts and their hits; Malefic Visions - the vision flying to Darius, its latch, the
                                wisps on him, the gate and the voidlings biting at his feet; Call of the Void on Garen -
                                the two rifts, the beams meeting, the blast; Nether Grasp on Darius - the start, the
                                channel and the beam between them, the hands round him every wave, the null zone
                                under him for 5 s; 3x
Projectiles fly as the kit flies them: from over his pivot, lifted 5000 - y_offset, at the target's pivot, turned to
their way (champion-data section 6).
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
from build_malzahar import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_malzahar")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_malzahar_fx", "league_malzahar_big")}


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_malzahar_fx"], fx["league_malzahar_big"]
    W, H = 200, 112
    gy = 78
    x0 = 70
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 50, gy)          # in his reach (52000)
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 76, gy - 8)       # a row behind him
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        x, y = me.pos(t)
        an = Anim(dense(sp, tag, "malzahar", z), t, x, y, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def wait(ms):
        a("idle", ms, loop=True)

    def fly(tag, at, foe, y_offset, speed):
        """A homing projectile from over his pivot to the foe's pivot; its arrival."""
        lift = (5000 - y_offset) / 1000.0
        mx, my = me.pos(at)
        fx_, fy = foe.pos(at)
        x1, y1 = mx, my - lift
        arrive = at + tick(max(1.0, ((fx_ - x1) ** 2 + (fy - y1) ** 2) ** 0.5 / (speed / 1000.0)))
        over.append(Turned(frames_of(small, tag), at, int(round(x1)), int(round(y1)), loop=True, until=arrive,
                           x1=fx_, y1=fy))
        return arrive

    def on(foe, tag, when, sheet=None, under_=False):
        (under if under_ else over).append(OnFoe(frames_of(sheet or small, tag), when, foe))

    def bolt(foe, then=True):
        """His attack: the bolt leaves on atk_st, its hit where it lands."""
        land = fly("a_bolt", t + tick(P["atk_st"]), foe, P["a_y"], P["a_speed"])
        on(foe, "a_hit", land)
        foe.flinches.append(land)
        a("attack", tick(P["atk_dur"]))
        if then:
            wait(tick(P["atk_cd"] - P["atk_dur"]))
        return land

    # Void Shift: the shell while it holds (Darius's first blow would break it; here it fades after the bolts)
    over.append(OnMe(frames_of(small, "p_shift"), 0, me, until=2600))
    wait(400)
    for _ in range(2):
        bolt(d)
    # Malefic Visions: the vision on e_lag, its latch; the wisps every 60 ticks, the gate and the voidlings (under him,
    # every 60 ticks) and their bites every w_p while they last
    land = fly("e_bolt", t + tick(P["e_lag"]), d, P["e_y"], P["e_speed"])
    a("skill", tick(P["e_dur"]))
    on(d, "e_hit", land)
    d.flinches.append(land)
    on(d, "w_spawn", land)
    for k in range(P["e_t"] // 60):
        on(d, "e_mark", land + tick(60 * k))
    for k in range(P["w_t"] // 60):
        on(d, "w_swarm", land + tick(60 * k), under_=True)
    for k in range(1, P["w_t"] // P["w_p"] + 1):
        on(d, "w_bite", land + tick(P["w_p"] * k))
        d.flinches.append(land + tick(P["w_p"] * k))
    wait(300)
    # Call of the Void on Garen: the rifts on his spot as the hands meet (q_wind), the beams q_lag later
    q0 = t
    gx, gyy = g.pos(q0)
    over.append(Anim(frames_of(big, "q_rift"), q0 + tick(P["q_wind"]), gx, gyy))
    on(g, "q_hit", q0 + tick(P["q_wind"] + P["q_lag"]))
    g.flinches.append(q0 + tick(P["q_wind"] + P["q_lag"]))
    a("skill2", tick(P["q_dur"]))
    wait(500)
    # Nether Grasp on Darius (his vision still on: the grasp r_wait ticks after the cast): the start, the channel, a
    # wave every r_p ticks with the hands round him, the null zone under him
    r0 = t + tick(P["r_wait"])
    wait(tick(P["r_wait"]))
    rx, ry = d.pos(r0)
    under.append(Anim(frames_of(big, "r_pool"), r0, rx, ry))
    d.holds.append((r0, r0 + tick(P["r_t"])))
    for k in range(P["r_t"] // P["r_p"]):
        on(d, "r_grasp", r0 + tick(P["r_p"] * k), sheet=big)
    # the beam: a link every r_lp ticks from his spot (a hidden bolt and a 1-tick lob: 2 ticks) back to Malzahar
    for k in range(P["r_t"] // P["r_lp"]):
        s0 = r0 + tick(P["r_lp"] * k + 2)
        (sx, sy), (ex, ey) = d.pos(s0), me.pos(s0)
        over.append(Turned(frames_of(small, "r_link"), s0, sx, sy, loop=True,
                           until=s0 + tick(abs(sx - ex) / (P["r_lspeed"] / 1000.0)), x1=ex, y1=ey))
    a("ult", tick(P["r_anim"]))
    a("ult_loop", tick(P["r_t"] - P["r_anim"]), loop=True)
    for _ in range(4):
        bolt(d)
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_malzahar_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[16:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_malzahar_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_malzahar_showcase.gif")))


if __name__ == "__main__":
    main()
