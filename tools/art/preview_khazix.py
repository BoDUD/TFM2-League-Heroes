#!/usr/bin/env python3
"""Preview images for Kha'Zix, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_khazix.py [--out docs/preview] [--only frames|effects|showcase]

  league_khazix_frames.png    every animation, frame by frame, 3x on the arena colour
  league_khazix_effects.png   every effect animation, 3x
  league_khazix_showcase.gif  a scripted fight against Darius with Garen behind him, timed like the kit
                              (tools/kit/build_khazix.py, 60 ticks a second): Kha'Zix runs in, the Unseen Threat flames
                              on him, and claws Darius (the passive bursts, Darius slowed); Q on the isolated Darius (the
                              heavier hit); E -> W: he leaps onto Garen, the shockwave where he lands, the spike thrown
                              at Garen (the hit, the slow, his heal); he turns on Darius - facing left from here, as on
                              the red side - and claws him with Q; R: the void burst, the shimmer while he is hidden (drawn
                              faint), out of it a claw with the passive; Darius falls, E resets; an evolution; 3x
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
from build_khazix import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_khazix")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_khazix_fx", "league_khazix_big")}
SPIKE_Y = P["w_y"] // 1000                      # the spike's y_offset in px (down from the pivot)


def faint(fr):
    """Hidden: drawn at a third of its alpha (the game shows his own team a faded figure)."""
    out = []
    for f, ms in fr:
        g = f.copy()
        g.putalpha(g.getchannel("A").point(lambda v: v // 3))
        out.append((g, ms))
    return out


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_khazix_fx"], fx["league_khazix_big"]
    W, H = 400, 150
    gy = 108
    x0 = 90
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 38, gy + 2)     # in his reach, alone
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 130, gy - 6)     # behind him
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0
    face = [False]
    hidden = []                                   # (t0, t1): drawn faint

    def a(tag, dur=None, loop=False):
        nonlocal t
        x, y = me.pos(t)
        fr = frames_of(sp, tag)
        an = Anim(fr, t, x, y, loop=loop, until=(t + dur) if dur else None, flip=face[0])
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def hit(foe, tag, when, sheet=None):
        over.append(OnFoe(frames_of(sheet or small, tag), when, foe))
        foe.flinches.append(when)

    def slow(foe, when, ticks):
        under.append(OnFoe(frames_of(small, "slow"), when, foe, until=when + tick(ticks)))

    # he runs in, the passive ready (the flames on him from the start of his life)
    walk = Anim(frames_of(sp, "run"), 0.0, x0 - 70, gy, loop=True, until=1100, x1=x0)
    body.append(walk)
    t = walk.until
    ut0 = 0.0
    a("idle", 250, loop=True)
    # the first claw on Darius: Unseen Threat bursts, the slow
    a1 = t + tick(P["a_st"])
    hit(d, "a_hit", a1)
    over.append(OnFoe(frames_of(small, "p_hit"), a1, d))
    slow(d, a1, P["ut_slow_t"])
    over.append(OnMe(frames_of(small, "ut"), ut0, me, until=a1, dy=0))
    a("attack", tick(P["atk_dur"]))
    a("idle", tick(P["atk_cd"] - P["atk_dur"]), loop=True)
    # Q on the isolated Darius: the heavier hit
    hit(d, "q_iso_hit", t + tick(P["q_at"]), big)
    a("skill", tick(P["q_dur"]))
    a("idle", 300, loop=True)
    # E -> W: the leap onto Garen, the shockwave where he lands, the spike, Garen slowed, his heal
    e0 = t
    start = me.pos(e0)[0]
    land_x = g.pos(e0)[0] - 18
    land = e0 + tick(P["e_t"])
    me.moves.append((e0, land, start, land_x))
    a("skill2", tick(P["e_t"] + P["w_t"]))
    under.append(Anim(frames_of(big, "e_land"), land, land_x, gy + 11))
    hit(g, "e_hit", land)
    rel = e0 + tick(P["e_t"] + P["w_at"])
    gx = g.pos(rel)[0]
    arrive = rel + tick(max(1, (gx - land_x) / (P["w_speed"] / 1000)))
    over.append(Anim(frames_of(small, "w_spike"), rel, land_x, gy + SPIKE_Y, until=arrive, x1=gx, y1=gy + SPIKE_Y))
    hit(g, "w_hit", arrive)
    slow(g, arrive, P["w_slow_t"])
    over.append(OnMe(frames_of(small, "w_heal"), arrive, me))
    a("idle", 400, loop=True)
    # he turns on Darius: facing left from here (the red side's way), runs back and claws him with Q
    face[0] = True
    r_start = t
    back_x = d.pos(t)[0] + 34
    run_ms = 450
    me.moves.append((r_start, r_start + run_ms, me.pos(r_start)[0], back_x))
    a("run", run_ms, loop=True)
    hit(d, "q_iso_hit", t + tick(P["q_at"]), big)
    a("skill", tick(P["q_dur"]))
    a("idle", 300, loop=True)
    # R: the burst as he vanishes, the shimmer while hidden, out of it a claw with the passive
    r0 = t
    over.append(OnMe(frames_of(big, "r_cast"), r0, me))
    hide = tick(P["r_inv"])
    hidden.append((r0 + 30, r0 + hide))
    over.append(OnMe(frames_of(big, "r_on"), r0, me, until=r0 + hide))
    over.append(OnMe(frames_of(small, "ut"), r0, me, until=r0 + hide + 200))
    a("ult", tick(P["r_anim"]))
    a("idle", hide - tick(P["r_anim"]), loop=True)
    a2 = t + tick(P["a_st"])
    hit(d, "a_hit", a2)
    over.append(OnFoe(frames_of(small, "p_hit"), a2, d))
    slow(d, a2, P["ut_slow_t"])
    a("attack", tick(P["atk_dur"]))
    # Darius falls; (Wings evolved) E resets
    d.death = a2 + tick(2)
    over.append(OnMe(frames_of(small, "e_reset"), a2 + tick(P["k_read"]), me, dy=-11))
    a("idle", 700, loop=True)
    # an evolution
    over.append(OnMe(frames_of(big, "evo"), t, me))
    a("idle", 1300, loop=True)
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
        units = [(g.pos(tt)[1], g.frame(tt), g.pos(tt)), (d.pos(tt)[1], d.frame(tt), d.pos(tt))]
        for an in body:
            f = an.frame(tt)
            if f is not None:
                if any(h0 <= tt < h1 for h0, h1 in hidden):
                    f = faint([(f, 0)])[0][0]
                units.append((an.pos(tt)[1], f, an.pos(tt)))
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
                                os.path.join(args.out, "league_khazix_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_khazix_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_khazix_showcase.gif")))


if __name__ == "__main__":
    main()
