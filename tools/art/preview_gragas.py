#!/usr/bin/env python3
"""Preview images for Gragas, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_gragas.py [--out docs/preview] [--only frames|effects|showcase]

  league_gragas_frames.png    every animation, frame by frame, 3x on the arena colour (the hd_ tags included)
  league_gragas_effects.png   every effect animation, 3x
  league_gragas_showcase.gif  a scripted fight against Darius with Garen behind him, timed like the kit
                              (tools/kit/build_gragas.py, 60 ticks a second): a punch on Darius; Q - the barrel lobbed
                              at him, fizzing on the ground, the blast and the sticky puddle; E + W - the dust where he
                              sets off, the belly slam (Darius stunned), the drink, the rage steam and the next punch's
                              ale burst; R - the cask hurled behind Darius onto Garen, the explosion flinging both toward
                              him; the swig's heal at every skill; 3x. He is drawn as the game draws him on the
                              battlefield: his dense (hd_) frames at PPU 2 and 85% (league_main hd.rs SIZES).
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
from build_gragas import P  # noqa: E402
import ppu_gragas  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_gragas")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_gragas_fx", "league_gragas_big")}


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_gragas_fx"], fx["league_gragas_big"]
    W, H = 260, 110
    gy = 84
    x0 = 60
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 34, gy)       # in his punch's reach
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 120, gy)       # far behind Darius
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        x, y = me.pos(t)
        # his dense frames at the battlefield's size (PPU 2, then 85%: league_main hd.rs SIZES), as the game draws him
        an = Anim(frames_of(sp, "hd_" + tag), t, x, y, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        an.scale = z * ppu_gragas.SIZE / ppu_gragas.K
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

    def swig(when):
        over.append(OnMe(frames_of(small, "p_heal"), when, me))

    a("idle", 500, loop=True)
    # a punch on Darius
    hit(d, "a_hit", t + tick(P["a_st"]))
    a("attack", tick(P["atk_dur"]))
    a("idle", 300, loop=True)
    # back off, then Q: the barrel lobbed at Darius, fizzing, the blast, the puddle
    me.moves.append((t, t + 500, me.pos(t)[0], me.pos(t)[0] - 30))
    a("run", 500, loop=True)
    q0 = t
    swig(q0)
    rel = q0 + tick(P["q_at"])
    land = rel + tick(P["q_fly"])
    sx = me.pos(rel)[0] + 8
    over.append(Anim(frames_of(small, "q_barrel"), rel, sx, gy - 14, until=land, x1=d.pos(rel)[0], y1=gy - 2))
    under.append(Anim(frames_of(small, "q_land"), land, d.pos(land)[0], gy - 2))
    boom = land + tick(P["q_wait"])
    over.append(Anim(frames_of(big, "q_boom"), boom, d.pos(land)[0], gy - 2))
    hit(d, "q_hit", boom)
    on(d, "q_slow", boom, until=boom + tick(P["q_slow_t"]))
    a("skill", tick(P["q_dur"]))
    a("idle", max(200, boom - t + 300), loop=True)
    # E + W: the dust, the slam (Darius stunned), the drink, the rage, the next punch's burst
    e0 = t
    swig(e0)
    start = e0 + tick(P["e_at"])
    under.append(Anim(frames_of(small, "e_dust"), start, me.pos(start)[0], gy))
    gap = d.pos(start)[0] - me.pos(start)[0] - 16
    slam = e0 + tick(8)
    me.moves.append((start, slam, me.pos(start)[0], me.pos(start)[0] + gap))
    hit(d, "e_hit", slam)
    on(d, "e_stun", slam, until=slam + tick(P["e_stun"]))
    d.holds.append((slam, slam + tick(P["e_stun"])))
    drink = e0 + tick(P["w_at"])
    over.append(OnMe(frames_of(small, "w_drink"), drink, me))
    over.append(OnMe(frames_of(small, "w_on"), drink, me, until=drink + 2600))
    a("skill2", tick(P["e_dur"]))
    a("idle", 200, loop=True)
    hit(d, "a_hit", t + tick(P["a_st"]))
    over.append(OnFoe(frames_of(big, "w_hit"), t + tick(P["a_st"]), d))
    a("attack", tick(P["atk_dur"]))
    a("idle", 400, loop=True)
    # R: the cask hurled onto Garen behind Darius, both flung toward him
    r0 = t
    swig(r0)
    go = r0 + tick(P["r_at"])
    land = go + tick(P["r_fly"])
    sx = me.pos(go)[0] + 8
    over.append(Anim(frames_of(big, "r_cask"), go, sx, gy - 16, until=land, x1=g.pos(go)[0], y1=gy - 4))
    over.append(Anim(frames_of(big, "r_boom"), land, g.pos(land)[0], gy - 2))
    for u in (g, d):
        hit(u, "r_hit", land)
        dist = min(P["r_grab"] * P["r_grab_t"] / 1000, max(0, u.pos(land)[0] - me.pos(land)[0] - 20))
        u.slides.append((land, land + tick(P["r_grab_t"]), -dist))
    a("ult", tick(P["r_dur"]))
    a("idle", max(300, land - t + 600), loop=True)
    end = t

    def place(img, f, px, py, k=z):
        """f (centred on its pivot) drawn k times its size with its centre on (px, py) game px."""
        if k != 1:
            f = f.resize((max(1, round(f.width * k)), max(1, round(f.height * k))), Image.NEAREST)
        img.alpha_composite(f, (round(px * z + z / 2 - f.width / 2), round(py * z + z / 2 - f.height / 2)))

    frames, tt = [], 0.0
    while tt < end:
        img = Image.new("RGBA", (W * z, H * z), ARENA)
        for an in under:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        units = [(u.pos(tt)[1], u.frame(tt), u.pos(tt), z) for u in (g, d)]
        for an in body:
            f = an.frame(tt)
            if f is not None:
                units.append((an.pos(tt)[1] + 0.5, f, an.pos(tt), an.scale))
                break
        for _, f, p, k in sorted(units, key=lambda u: u[0]):
            if f is not None:
                place(img, f, *p, k)
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
        print("frames", contact([(s, t["name"], t["name"]) for t in s.tags if not t["name"].startswith("hd_")],
                                os.path.join(args.out, "league_gragas_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_gragas_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_gragas_showcase.gif")))


if __name__ == "__main__":
    main()
