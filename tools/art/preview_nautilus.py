#!/usr/bin/env python3
"""Preview images for Nautilus, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_nautilus.py [--out docs/preview] [--only frames|effects|showcase]

  league_nautilus_frames.png    every animation, frame by frame, 3x on the arena colour
  league_nautilus_effects.png   every effect animation, 3x
  league_nautilus_showcase.gif  a scripted fight against Darius with Garen behind him, timed like the kit
                                (tools/kit/build_nautilus.py, 60 ticks a second): an anchor swing on Darius - the
                                passive's surge and root; Q from afar - the anchor flies, hooks Darius and hauls him
                                the whole way to Nautilus; W + E - the shield round him, the three waves, Darius slowed, the
                                next swing splashing round him; R - the slam, the shockwave rushing under Darius
                                (knocked up) to Garen behind him, the eruption and the stun; 3x
"""
import argparse
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
from preview_annie import Held, OnFoe  # noqa: E402
from preview_ashe import Anim, tick  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_pyke import Me, OnMe  # noqa: E402
from build_nautilus import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_nautilus")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_nautilus_fx", "league_nautilus_big")}


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_nautilus_fx"], fx["league_nautilus_big"]
    W, H = 240, 110
    gy = 84
    x0 = 60
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 30, gy)       # in his anchor's reach
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 110, gy)       # far behind Darius
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

    def on(foe, tag, when, sheet=None, until=None):
        o = OnFoe(frames_of(sheet or small, tag), when, foe)
        if until is not None:
            o.loop, o.until = True, until
        over.append(o)

    def hit(foe, tag, when, sheet=None):
        on(foe, tag, when, sheet)
        foe.flinches.append(when)

    a("idle", 500, loop=True)
    # the swing on Darius: the passive's surge, the root under him
    sw = t + tick(P["a_st"])
    hit(d, "a_hit", sw)
    on(d, "p_hit", sw)
    on(d, "p_root", sw, until=sw + tick(P["p_root"]))
    d.holds.append((sw, sw + tick(P["p_root"])))
    a("attack", tick(P["atk_dur"]))
    a("idle", 300, loop=True)
    # back off, then Q: the anchor flies, hooks Darius, hauls him the whole way in
    me.moves.append((t, t + 600, me.pos(t)[0], me.pos(t)[0] - 34))
    a("run", 600, loop=True)
    q0 = t
    rel = q0 + tick(P["q_at"])
    sx = me.pos(rel)[0] + 10
    speed = P["q_speed"] / 1000
    arrive = rel + tick((d.pos(rel)[0] - sx) / speed)
    over.append(Anim(frames_of(small, "q_anchor"), rel, sx, gy - 8, until=arrive, x1=d.pos(rel)[0], y1=gy - 8))
    hit(d, "q_hit", arrive)
    gap = d.pos(arrive)[0] - me.pos(arrive)[0] - 14
    # the drag has no length of its own since 2026-10-17 (build_nautilus.py): Darius is hauled the whole gap at q_pull
    # a tick, and Nautilus's dash q_catch ticks later finds nothing left to close
    pull_t = tick(gap / (P["q_pull"] / 1000))
    d.slides.append((arrive, arrive + pull_t, -gap))
    a("skill", arrive - t)
    a("skill_pull", tick(P["q_anim"]))
    a("idle", 300, loop=True)
    # W + E: the shield, the slam's three waves, Darius slowed
    w0 = t
    over.append(OnMe(frames_of(small, "w_on"), w0, me, until=w0 + 5200))
    for k in range(3):
        under.append(Anim(frames_of(big, f"e_wave{k + 1}"), w0 + tick(P["e_at"] + k * P["e_gap"]), me.pos(w0)[0], gy))
    e_hit = w0 + tick(P["e_at"])
    hit(d, "e_hit", e_hit)
    on(d, "e_slow", e_hit, until=e_hit + tick(P["e_slow_t"]))
    a("skill2", tick(P["c_dur"]))
    a("idle", 200, loop=True)
    sw = t + tick(P["a_st"])
    hit(d, "a_hit", sw)
    on(d, "w_hit", sw)
    a("attack", tick(P["atk_dur"]))
    a("idle", 300, loop=True)
    # R: the slam, the shockwave under Darius to Garen
    r0 = t
    under.append(OnMe(frames_of(small, "r_cast"), r0 + tick(P["r_at"]), me))
    go = r0 + tick(P["r_at"])
    wsp = P["r_speed"] / 1000
    sx = me.pos(go)[0] + 8
    reach = go + tick((g.pos(go)[0] - sx) / wsp)
    over.append(Anim(frames_of(big, "r_wave"), go, sx, gy + 4, until=reach, x1=g.pos(go)[0], y1=gy + 4))
    past = go + tick((d.pos(go)[0] - sx) / wsp)
    on(d, "r_up", past)
    d.hops.append((past, past + tick(P["r_path_up"]), 6))
    on(g, "r_hit", reach, big)
    g.hops.append((reach, reach + tick(P["r_up"]), 10))
    on(g, "r_stun", reach + tick(P["r_up"]), until=reach + tick(P["r_up"] + P["r_stun"]))
    g.holds.append((reach + tick(P["r_up"]), reach + tick(P["r_up"] + P["r_stun"])))
    a("ult", tick(P["r_dur"]))
    a("idle", max(300, reach + tick(P["r_up"] + P["r_stun"]) - t + 300), loop=True)
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
                                os.path.join(args.out, "league_nautilus_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[16:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_nautilus_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_nautilus_showcase.gif")))


if __name__ == "__main__":
    main()
