#!/usr/bin/env python3
"""Preview images for Braum, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_braum.py [--out docs/preview] [--only frames|effects|showcase]

  league_braum_frames.png    every animation's dense frames (hd_, PPU 2.881, as league.dll shows them)
  league_braum_effects.png   every effect animation, 3x
  league_braum_showcase.gif  a scripted fight with Darius in front and Taric behind him, timed like the kit
                             (tools/kit/build_braum.py, 60 ticks a second): two shield bashes stacking Concussive Blows
                             on Darius; Winter's Bite - the ice, its burst, the frozen ground under Darius, the third
                             stack; the fourth bash - the ice shell shattering, Darius stunned; a bash on the stunned
                             Darius with the bonus damage; Unbreakable - the burst of cold, the ice shell round him,
                             Taric behind the shield; Stand Behind Me - the leap back to Taric, the landing ring, both
                             guarded; Glacial Fissure - the slam, the ice rushing along the line, the cracks left behind,
                             Darius thrown up and slowed; 3x
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
from preview_pyke import Me, OnFoe, OnMe, mirrored  # noqa: E402
from build_braum import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_braum")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_braum_fx", "league_braum_big")}
SHIELD = 16                                      # his shield's face: px in front of his pivot (the ice leaves there)
ICE = P["q_speed"] / 1000                        # px a tick
WAVE = P["r_speed"] / 1000
STEP = P["r_len"] // P["r_n"] / 1000             # the fissure's stamps, px apart


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_braum_fx"], fx["league_braum_big"]
    W, H = 250, 120
    gy = 86
    x0 = 100
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 54, gy)      # in his bash's reach
    taric = load(os.path.join(LEAGUE, "champions", "league_taric"))
    tx = x0 - 62
    ally = Anim(frames_of(taric, "idle"), 0, tx, gy, loop=True)                         # his ally, behind him
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False, flip=False):
        nonlocal t
        x, y = me.pos(t)
        fr = dense(sp, tag, "braum", z)
        if flip:                                 # turned toward where he leaps (put() needs the 1x size kept)
            fl = mirrored(fr)
            for (f, _), (g, _) in zip(fl, fr):
                f.info["one"] = g.info["one"]
            fr = fl
        an = Anim(fr, t, x, y, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def hit(tag, when, sheet=None, until=None):
        over.append(OnFoe(frames_of(sheet or small, tag), when, d, until=until))
        d.flinches.append(when)

    def stack(when):
        over.append(OnFoe(frames_of(small, "p_mark"), when, d, until=when + tick(P["p_hold"]) // 3))

    a("idle", 500, loop=True)
    # two bashes: a stack each
    for _ in range(2):
        when = t + tick(P["atk_st"])
        hit("a_hit", when)
        stack(when)
        a("attack", tick(P["atk_dur"]))
        a("idle", 200, loop=True)
    # Winter's Bite: the ice to Darius, its burst, the frozen ground, the third stack
    rel = t + tick(P["q_at"])
    sx = me.pos(rel)[0] + SHIELD
    arrive = rel + tick(max(1, (d.pos(rel)[0] - sx) / ICE))
    over.append(Anim(frames_of(small, "q_ice"), rel, sx, gy - 14, until=arrive, x1=d.pos(rel)[0], y1=gy - 14))
    hit("q_hit", arrive)
    stack(arrive)
    under.append(OnFoe(frames_of(small, "q_slow"), arrive, d, until=arrive + tick(P["q_slow1_t"] + P["q_slow2_t"])))
    a("skill", tick(P["q_dur"]))
    a("idle", 300, loop=True)
    # the fourth bash: the shell shatters, Darius stunned
    when = t + tick(P["atk_st"])
    hit("a_hit", when)
    over.append(OnFoe(frames_of(small, "p_proc"), when, d))
    over.append(OnFoe(frames_of(small, "p_stun"), when, d, until=when + tick(P["p_stun"])))
    d.holds.append((when, when + tick(P["p_stun"])))
    a("attack", tick(P["atk_dur"]))
    a("idle", 150, loop=True)
    # a bash on the stunned Darius: the bonus damage
    when = t + tick(P["atk_st"])
    hit("a_hit", when)
    over.append(OnFoe(frames_of(small, "p_extra"), when, d))
    a("attack", tick(P["atk_dur"]))
    a("idle", 300, loop=True)
    # Unbreakable: the burst of cold, the ice shell round him, Taric behind the shield
    e0 = t
    over.append(OnMe(frames_of(small, "e_raise"), e0, me))
    over.append(OnMe(frames_of(big, "e_on"), e0, me, until=e0 + 1400))
    over.append(Anim(frames_of(small, "e_ally"), e0, tx, gy, loop=True, until=e0 + 1400))
    a("skill2", tick(P["e_anim"]))
    a("idle", 1400 - tick(P["e_anim"]), loop=True)
    # Stand Behind Me: the leap back to Taric (he turns to him), the landing ring, both guarded
    w0 = t
    land = w0 + tick(P["w_anim"])
    under.append(OnMe(frames_of(small, "w_dash"), w0, me))
    me.moves.append((w0, land, me.pos(w0)[0], tx + 30))
    over.append(Anim(frames_of(small, "w_land"), land, tx, gy))
    over.append(Anim(frames_of(small, "w_guard"), land, tx, gy, loop=True, until=land + 1200))
    over.append(OnMe(frames_of(small, "w_guard"), land, me, until=land + 1200))
    a("w_leap", tick(P["w_anim"]), flip=True)
    a("idle", 600, loop=True)
    # Glacial Fissure: the slam, the ice rushing to Darius and past him, the cracks, Darius thrown up and slowed
    r0 = t
    slam = r0 + tick(P["r_at"])
    mx = me.pos(slam)[0]
    under.append(Anim(frames_of(big, "r_slam"), slam, mx, gy))
    end_x = mx + P["r_len"] / 1000
    over.append(Anim(frames_of(big, "r_wave"), slam, mx + 6, gy, until=slam + tick((end_x - mx) / WAVE), x1=end_x, y1=gy))
    for i in range(1, P["r_n"] + 1):
        cx = mx + STEP * i
        under.append(Anim(frames_of(big, "r_crack"), slam + tick(STEP * i / WAVE), cx, gy))
    reach = slam + tick(max(1, (d.pos(slam)[0] - mx) / WAVE))
    hit("r_hit", reach)
    d.holds.append((reach, reach + tick(P["r_up1"])))
    under.append(OnFoe(frames_of(small, "q_slow"), reach, d, until=reach + 1500))
    a("ult", tick(P["r_dur"]))
    a("idle", 1200, loop=True)
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
        units = [(d.pos(tt)[1], d.frame(tt), d.pos(tt)), (ally.pos(tt)[1], ally.frame(tt), ally.pos(tt))]
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_braum_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_braum_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_braum_showcase.gif")))


if __name__ == "__main__":
    main()
