#!/usr/bin/env python3
"""Preview images for Zeri, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_zeri.py [--out docs/preview] [--only frames|effects|showcase]

  league_zeri_frames.png    every animation, frame by frame, 3x on the arena colour
  league_zeri_effects.png   every effect animation, 3x
  league_zeri_showcase.gif  a scripted fight against Darius with Garen behind him, timed like the kit
                            (tools/kit/build_zeri.py, 60 ticks a second): bursts of rounds into Darius charge the pack
                            (the crackle), the charged spark (the blast, the slow; her shield and haste); W - the
                            charge, the pulse into Darius (the hit, the slow); E - the dash burst, the piercing round
                            through Darius into Garen; she runs past them, turns round - facing left from here, as on
                            the red side - and fires R: the nova round her hits both, the overcharge, triple shots
                            chaining lightning; 3x
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
from build_zeri import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_zeri")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_zeri_fx", "league_zeri_big")}
MUZZLE = 26                                      # the levelled rifle's muzzle, px ahead of the pivot
ROUND = P["burst_speed"] / 1000                  # px a tick
SPARK = P["p_speed"] / 1000
PULSE = P["w_speed"] / 1000


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_zeri_fx"], fx["league_zeri_big"]
    W, H = 420, 150
    gy = 108
    x0 = 110
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 60, gy)       # her attack range
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 95, gy)        # behind Darius, in line
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0
    face = [False]

    def a(tag, dur=None, loop=False):
        nonlocal t
        x, y = me.pos(t)
        an = Anim(frames_of(sp, tag), t, x, y, loop=loop, until=(t + dur) if dur else None, flip=face[0])
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def hit(foe, tag, when, sheet=None):
        over.append(OnFoe(frames_of(sheet or small, tag), when, foe))
        foe.flinches.append(when)

    def shot(foe, when, tag, speed, last=None, y=-6):
        """A round from the muzzle to the foe (or on to `last`)."""
        sx = me.pos(when)[0] + (-MUZZLE if face[0] else MUZZLE)
        tx = (last or foe).pos(when)[0]
        arrive = when + tick(max(1, abs(tx - sx) / speed))
        fr = [(f, ms) for f, ms in frames_of(small, tag) if f.width > 3]      # the import's empty lead ticks off
        if face[0]:
            fr = [(f.transpose(Image.FLIP_LEFT_RIGHT), ms) for f, ms in fr]
        over.append(Anim(fr, when, sx, gy + y, loop=True, until=arrive, x1=tx, y1=gy + y))
        return arrive

    # bursts charge the pack; the fifth shot is the charged spark (the blast, the slow; her shield and haste)
    for k in range(P["p_need"] - 1):
        hit(d, "a_hit", shot(d, t + tick(P["a_st"]), "a_burst", ROUND))
        a("attack", tick(P["atk_dur"]))
        a("idle", tick(20), loop=True)
    over.append(OnMe(frames_of(small, "p_ready"), t - tick(20), me))
    arrive = shot(d, t + tick(P["a_st"]), "p_spark", SPARK)
    hit(d, "p_hit", arrive)
    under.append(OnFoe(frames_of(small, "p_slow"), arrive, d, until=arrive + tick(P["p_slow_t"])))
    over.append(OnMe(frames_of(small, "p_shv"), arrive, me, until=arrive + 1500))
    under.append(OnMe(frames_of(small, "p_haste"), arrive, me, until=arrive + tick(P["p_haste_t"])))
    a("attack", tick(P["atk_dur"]))
    a("idle", tick(30), loop=True)
    # W: the charge, the pulse into Darius
    over.append(OnMe(frames_of(small, "w_cast"), t, me))
    arrive = shot(d, t + tick(P["w_rel"]), "w_pulse", PULSE)
    hit(d, "w_hit", arrive)
    under.append(OnFoe(frames_of(small, "w_slow"), arrive, d, until=arrive + tick(P["w_slow_t"])))
    a("skill", tick(P["w_dur"]))
    a("idle", tick(20), loop=True)
    # E: the dash burst, a hop forward, then a piercing round through Darius into Garen
    under.append(OnMe(frames_of(big, "e_cast"), t, me))
    me.moves.append((t, t + tick(P["e_dur"]), me.pos(t)[0], me.pos(t)[0] + 14))
    a("skill2", tick(P["e_dur"]))
    e_end = t + 1600
    over.append(OnMe(frames_of(small, "e_on"), t, me, until=e_end))
    when = t + tick(P["a_st"])
    shot(d, when, "e_shot", ROUND, last=g)
    sxx = me.pos(when)[0] + MUZZLE
    for foe in (d, g):
        hit(foe, "e_hit", when + tick(max(1, abs(foe.pos(when)[0] - sxx) / ROUND)))
    a("attack", tick(P["atk_dur"]))
    a("idle", e_end - t, loop=True)
    # she runs past them, turns round (the red side's facing) and fires R: the nova, the overcharge, triple shots
    walk_to = g.pos(t)[0] + 50
    me.moves.append((t, t + 900, me.pos(t)[0], walk_to))
    a("run", 900, loop=True)
    face[0] = True
    r0 = t
    nova = r0 + tick(P["r_rel"])
    under.append(OnMe(frames_of(big, "r_nova"), nova, me))
    for foe in (d, g):
        hit(foe, "r_hit", nova + 60)
    over.append(OnMe(frames_of(big, "r_on"), nova, me, until=nova + 2400))
    a("ult", tick(P["r_anim"]))
    for k in range(3):
        when = t + tick(P["a_st"])
        arrive = shot(g, when, "r_shot", ROUND)
        hit(g, "a_hit", arrive)
        hit(d, "r_zap", arrive + 40)
        a("attack", tick(P["atk_dur"]))
        a("idle", tick(16), loop=True)
    a("idle", 1200, loop=True)
    end = t

    def place(img, f, px, py):
        img.alpha_composite(f, (int(px - f.width // 2), int(py - f.height // 2)))

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
                                os.path.join(args.out, "league_zeri_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[12:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_zeri_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_zeri_showcase.gif")))


if __name__ == "__main__":
    main()
