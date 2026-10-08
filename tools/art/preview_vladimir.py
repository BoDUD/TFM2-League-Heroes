#!/usr/bin/env python3
"""Preview images for Vladimir, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_vladimir.py [--out docs/preview] [--only frames|effects|showcase]

  league_vladimir_frames.png    every animation, frame by frame, 3x on the arena colour
  league_vladimir_effects.png   every effect animation, 3x
  league_vladimir_showcase.gif  a scripted fight against Darius with Garen behind him, timed like the kit
                                (tools/kit/build_vladimir.py, 60 ticks a second): a blood bolt on Darius; Q - the drain,
                                the blood flying back, the heal, the half-full bar under him; Q again - Crimson Rush;
                                E - the sphere of the charge, the nova, a bolt to each of them; E -> Q - a Crimson Rush at
                                once; the pros' Flash R E - the mist blink in, Hemoplague's cloud on Darius, the marks,
                                the combo's nova, the burst and the blood coming back; then the pool (2 s on the ground,
                                both drained) and, E ready, the nova as he rises out of it (E-W); 3x
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
from build_vladimir import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_vladimir")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_vladimir_fx", "league_vladimir_big")}
HAND = 14                                        # his raised hand at the release, px ahead of the pivot
BOLT_Y = -P["bolt_y"] // 1000 + 5                # the bolts fly this far over the pivot (5000 - y_offset)
BOLT = P["bolt_speed"] / 1000                    # px a tick
EBOLT = P["e_speed"] / 1000
ORB = P["orb_speed"] / 1000


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_vladimir_fx"], fx["league_vladimir_big"]
    W, H = 190, 104
    gy = 82
    x0 = 62
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 48, gy)       # his attack range
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 72, gy)        # behind Darius
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

    def bolt(tag, rel, speed, foe, hit_tag):
        sx = me.pos(rel)[0] + HAND
        arrive = rel + tick(max(1, (foe.pos(rel)[0] - sx) / speed))
        over.append(Anim(frames_of(small, tag), rel, sx, gy - BOLT_Y, until=arrive, x1=foe.pos(rel)[0], y1=gy - BOLT_Y))
        if hit_tag:
            hit(foe, hit_tag, arrive)
        return arrive

    def drain(rush):
        """Q: the drain on Darius, the blood flying back (turned: it flies left), the heal when it reaches him."""
        rel = t + tick(P["q_st"])
        hit(d, "q_drain", rel)
        fx_x = d.pos(rel)[0]
        back = rel + tick(max(1, (fx_x - me.pos(rel)[0]) / ORB))
        orb = frames_of(small, "q_rush" if rush else "q_orb")
        orb = [(f.transpose(Image.ROTATE_180), ms) for f, ms in orb]       # turned to its flight, top-bottom symmetric
        over.append(Anim(orb, rel, fx_x, gy - 10, until=back, x1=me.pos(rel)[0], y1=gy - 10))
        over.append(OnMe(frames_of(small, "q_heal"), back, me))
        a("skill", tick(P["q_dur"]))
        return back

    def nova(at, pct_tag="e_burst"):
        over.append(OnMe(frames_of(big, pct_tag), at, me))
        for foe in (d, g):
            bolt("e_bolt", at, EBOLT, foe, "e_hit")

    a("idle", 500, loop=True)
    bolt("a_bolt", t + tick(P["atk_st"]), BOLT, d, "a_hit")
    a("attack", tick(P["atk_dur"]))
    a("idle", 300, loop=True)
    # Q, then the half-full bar under him until the second Q: Crimson Rush
    back = drain(False)
    bar = OnMe(frames_of(small, "q1"), back, me, until=back + 1)
    under.append(bar)
    a("idle", 500, loop=True)
    bar.until = t + tick(P["q_st"])
    drain(True)
    a("idle", 400, loop=True)
    # E: the charge's sphere, the nova; E -> Q: a Crimson Rush at once
    e0 = t
    under.append(OnMe(frames_of(small, "e_chg"), e0, me, until=e0 + tick(P["e_rel"])))
    nova(e0 + tick(P["e_rel"]))
    a("skill2", tick(P["e_dur"]))
    drain(True)
    a("idle", 500, loop=True)
    # Flash R E: the mist blink in, the cloud on Darius, the marks, the combo's nova, the burst, the blood back
    r0 = t
    over.append(OnMe(frames_of(small, "c_blink"), r0, me))
    hop = min(P["r_blink"] // 1000, d.pos(r0)[0] - me.pos(r0)[0] - P["r_stop"] // 1000)
    hop = max(hop, 0)
    me.moves.append((r0 + 1, r0 + 2, me.pos(r0)[0], me.pos(r0)[0] + hop))
    over.append(OnMe(frames_of(small, "c_blink"), r0 + 20, me))
    land = r0 + tick(P["r_st"])
    over.append(Anim(frames_of(big, "r_cloud"), land, d.pos(land)[0], gy))      # z 2: over the units
    for foe in (d, g):
        over.append(OnFoe(frames_of(small, "r_mark"), land, foe, until=land + tick(P["r_t"])))
    nova(r0 + tick(P["r_st"] + P["r_ring"]))
    a("ult", tick(P["r_dur"]))
    a("idle", tick(P["r_t"]) - tick(P["r_dur"]) + tick(P["r_st"]), loop=True)
    burst = land + tick(P["r_t"])
    for foe in (d, g):
        hit(foe, "r_burst", burst)
    over.append(OnMe(frames_of(small, "r_heal_on"), burst, me))
    a("idle", 600, loop=True)
    # the pool: 2 s on the ground, both drained; E ready, the nova as he rises (E-W)
    w0 = t
    over.append(OnMe(frames_of(big, "w_splash"), w0, me, dy=0))
    under.append(OnMe(frames_of(big, "w_in"), w0, me, until=w0 + tick(P["w_t"])))
    for foe in (d, g):
        over.append(OnFoe(frames_of(small, "w_drain"), w0 + tick(15), foe, until=w0 + tick(P["w_t"])))
    over.append(OnMe(frames_of(big, "w_splash"), w0 + tick(P["w_t"] - 6), me))
    nova(w0 + tick(P["w_t"] - 6))
    a("skill_w", tick(P["w_t"]))
    a("idle", 900, loop=True)
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
                                os.path.join(args.out, "league_vladimir_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[16:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_vladimir_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_vladimir_showcase.gif")))


if __name__ == "__main__":
    main()
