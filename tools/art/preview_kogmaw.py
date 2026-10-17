#!/usr/bin/env python3
"""Preview images for Kog'Maw, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_kogmaw.py [--out docs/preview] [--only frames|effects|showcase]

  league_kogmaw_frames.png    every animation, frame by frame, 3x on the arena colour
  league_kogmaw_effects.png   every effect animation, 3x
  league_kogmaw_showcase.gif  a scripted fight with Darius in front and Garen behind him, timed like the kit
                              (tools/kit/build_kogmaw.py, 60 ticks a second): an attack turns Bio-Arcane Barrage on
                              (the burst, the ring at his feet) and the W -> Q combo follows (the spittle, the acid
                              on Darius); two more globs; E - the ooze through both, the trail, the slows, and the
                              E -> R combo's shell on Darius; R - two shells on Garen; he falls, the void form wakes,
                              chases Darius and bursts on him (Garen caught in it); 3x
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
from build_kogmaw import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_kogmaw")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_kogmaw_fx", "league_kogmaw_big")}
MOUTH = 22                                       # the tube's end: px in front of his pivot (the globs leave there)
GLOB = P["glob_speed"] / 1000                    # px a tick
SPIT = P["q_speed"] / 1000
OOZE = P["e_speed"] / 1000
FORM = P["p_speed"] / 1000


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_kogmaw_fx"], fx["league_kogmaw_big"]
    W, H = 240, 110
    gy = 76
    x0 = 40
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 70, gy)
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 150, gy)
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        x, y = me.pos(t)
        an = Anim(frames_of(sp, tag), t, x, y, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def hit(foe, tag, when, sheet=None):
        over.append(OnFoe(frames_of(sheet or small, tag), when, foe))
        foe.flinches.append(when)

    def fly(tag, sheet, when, x1, speed, y=gy):
        """A straight / homing flight from the tube's end to x1 at the pivot's height; returns the arrival."""
        sx = me.pos(when)[0] + MOUTH
        arrive = when + tick(max(1, (x1 - sx) / speed))
        over.append(Anim(frames_of(sheet, tag), when, sx, y, until=arrive, x1=x1, y1=y))
        return arrive

    def shell(foe, when):
        """R's shell: the mark on the foe's spot, the fall, the blast r_delay ticks later."""
        fx_ = foe.pos(when)[0]
        under.append(Anim(frames_of(big, "r_mark"), when, fx_, gy))
        blast = when + tick(P["r_delay"])
        over.append(Anim(frames_of(big, "r_fall"), blast - tick(8), fx_, gy))
        hit(foe, "r_hit", blast)
        return blast

    a("idle", 500, loop=True)
    # an attack turns Bio-Arcane Barrage on: the burst on him, the ring at his feet for the rest of the fight
    w0 = t
    over.append(OnMe(frames_of(small, "w_cast"), w0, me))
    rel = t + tick(P["a_st"])
    hit(d, "a_hit", fly("a_glob", small, rel, d.pos(rel)[0], GLOB))
    a("attack", tick(P["atk_dur"]))
    # W -> Q: the spittle follows the attack
    rel = t + tick(P["q_rel"])
    land = fly("q_spit", small, rel, d.pos(rel)[0], SPIT)
    hit(d, "q_hit", land)
    over.append(OnFoe(frames_of(small, "q_shred"), land, d, until=land + 2400))
    a("skill", tick(P["q_dur"]))
    for _ in range(2):
        a("idle", 120, loop=True)
        rel = t + tick(P["a_st"])
        hit(d, "a_hit", fly("a_glob", small, rel, d.pos(rel)[0], GLOB))
        a("attack", tick(P["atk_dur"]))
    a("idle", 200, loop=True)
    # E: the ooze through both, the trail on the ground, the slows; E -> R: a shell on Darius
    rel = t + tick(P["e_rel"])
    sx = me.pos(rel)[0] + MOUTH
    reach = sx + P["e_len"] // 1000
    over.append(Anim(frames_of(small, "e_ooze"), rel, sx, gy, until=rel + tick((reach - sx) / OOZE), x1=reach, y1=gy))
    under.append(Anim(frames_of(big, "e_trail"), rel, sx + P["e_len"] // 2000, gy, loop=True,
                      until=rel + tick(P["e_trail"])))
    for foe in (d, g):
        arrive = rel + tick((foe.pos(rel)[0] - sx) / OOZE)
        hit(foe, "e_hit", arrive)
        under.append(OnFoe(frames_of(small, "e_slow"), arrive, foe, until=arrive + tick(P["e_slow_t"])))
    d_arrive = rel + tick((d.pos(rel)[0] - sx) / OOZE)
    a("skill2", tick(P["e_dur"]))
    shell(d, d_arrive + tick(P["e_r_wait"]))
    a("idle", 300, loop=True)
    # R: two shells on Garen, a volley's pace
    for _ in range(2):
        shell(g, t + tick(P["r_rel"]))
        a("ult", tick(P["r_dur"]))
        a("idle", tick(P["r_gap"]) - tick(P["r_dur"]) + 200, loop=True)
    a("idle", 300, loop=True)
    # he falls: the void form wakes, chases Darius and bursts on him, Garen caught in it
    dead = frames_of(sp, "dead")
    t_die = t
    x, y = me.pos(t)
    an = Anim(dead[:-1] + [(dead[-1][0], 60000)], t, x, y)
    an.pos = me.pos
    body.append(an)
    wake = t_die + tick(7)
    over.append(Anim(frames_of(big, "p_wake"), wake, x, gy))
    go = wake + 200
    arrive = go + tick(max(1, (d.pos(go)[0] - x) / FORM))
    over.append(Anim(frames_of(big, "p_form"), go, x, gy - 6, until=arrive, x1=d.pos(go)[0], y1=gy - 6))
    hit(d, "p_boom", arrive, big)
    hit(g, "p_hit", arrive + 40)
    end = arrive + 1400
    for w in (w0,):
        under.append(OnMe(frames_of(small, "w_on"), w, me, until=t_die))

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
                                os.path.join(args.out, "league_kogmaw_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_kogmaw_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_kogmaw_showcase.gif")))


if __name__ == "__main__":
    main()
