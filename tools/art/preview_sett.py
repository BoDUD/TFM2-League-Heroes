#!/usr/bin/env python3
"""Preview images for Sett, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_sett.py [--out docs/preview]

  league_sett_frames.png    every animation, frame by frame, 3x on the arena colour
  league_sett_effects.png   every effect animation, 3x
  league_sett_showcase.gif  a scripted fight against Darius with Garen behind him, timed like the kit
                            (tools/kit/sett_kit.py): Sett runs in and boxes Darius - a left jab, a quicker right cross;
                            Facebreaker pulls Darius in front and Garen behind into him (both stunned, the clap between
                            his fists), his fists catch fire (Knuckle Down) and his Grit heats the ground; two
                            empowered punches; Haymaker: the giant fist down its line, the true-damage hit in its
                            middle, the silver shield round him; The Show Stopper: he grabs Darius, throws him, leaps
                            after him and slams him into a crater; 3x
"""
import argparse
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from preview_annie import Held, OnFoe  # noqa: E402
from preview_ashe import Anim, tick  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_sett")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_sett_fx", "league_sett_big")}


class Him:
    """Sett's pivot for the views that follow him: where his body animation is at each moment."""

    def __init__(self, body):
        self.body = body

    def pos(self, t):
        for an in self.body:
            if an.frame(t) is not None:
                return an.pos(t)
        return self.body[-1].pos(t)


def showcase(out, z=3, step=40):
    sett = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_sett_fx"], fx["league_sett_big"]
    W, H = 320, 130
    gy = 86
    x0 = 130
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 26, gy)       # 25 px: his reach
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 - 40, gy - 6)    # behind him
    g.mirrored = False
    body, under, over = [], [], []
    him = Him(body)
    t = 0.0
    x = x0

    def a(tag, dur=None, loop=False, to=None):
        nonlocal t
        an = Anim(frames_of(sett, tag), t, x, gy, loop=loop, until=(t + dur) if dur else None, x1=to)
        body.append(an)
        t = an.until

    def on(unit, sp, tag, when, until=None, ground=False):
        an = OnFoe(frames_of(sp, tag), when, unit, z=-1 if ground else 1)
        if until is not None:
            an.loop, an.until = True, until
        (under if ground else over).append(an)
        return an

    def punches(hit_left, hit_right, foe):
        """A left jab (hit on its tick 12) and a right cross (the attack forced to attack2 from tick 3, hit on 9)."""
        t0 = t
        on(foe, small, hit_left, t0 + tick(12))
        foe.flinches.append(t0 + tick(12))
        a("attack")
        a("idle", tick(64 - 24), loop=True)
        t1 = t
        on(foe, small, hit_right, t1 + tick(9))
        foe.flinches.append(t1 + tick(9))
        a("attack", tick(3))
        a("attack2")
        a("idle", tick(64 - 24), loop=True)
        return t1 + tick(9)

    # he runs in; Darius and Garen wait
    body.append(Anim(frames_of(sett, "run"), 0.0, x - 50, gy, loop=True, until=1100, x1=x))
    t = 1100
    a("idle", 300, loop=True)
    punches("a_hit", "a2_hit", d)
    # Facebreaker: on tick 10 both are hit and pulled in (3 px a tick), stunned 60 ticks; the clap on tick 18
    e0 = t
    grab = e0 + tick(10)
    for foe, gap in ((d, 12), (g, -12)):
        on(foe, small, "e_hit", grab)
        dx = (x + gap) - foe.x
        foe.slides.append((grab, grab + tick(abs(dx) / 3.0), dx))
        foe.holds.append((grab, grab + tick(60)))
    over.append(Anim(frames_of(big, "e_smash"), e0 + tick(18), x, gy))
    glow = on(him, small, "q_glow", grab, until=grab + tick(300))
    heat = on(him, small, "grit", grab, until=grab + tick(600), ground=True)
    a("skill")
    a("idle", tick(10), loop=True)
    # Knuckle Down: the next two punches hit harder (the stunned Darius in front of him)
    last = punches("q_hit", "q_hit", d)
    glow.until = last
    # Haymaker: the fist's picture on its line (25 px ahead, from tick 2), the hit on tick 29, the shield for 180 ticks
    w0 = t
    heat.until = w0
    over.append(Anim(frames_of(big, "w_fist"), w0 + tick(2), x + 25, gy))
    on(d, small, "w_true", w0 + tick(29))
    d.flinches.append(w0 + tick(29))
    pre = on(him, small, "w_pre", w0 + tick(2))
    on(him, small, "w_loop", pre.until, until=w0 + tick(2 + 180) - 260)
    on(him, small, "w_remove", w0 + tick(2 + 180) - 260)
    a("skill2")
    a("idle", tick(20), loop=True)
    # The Show Stopper: the grab on tick 2, the throw on tick 8 (24 px in 8 ticks), his leap after him at 3 px a tick,
    # the slam 4 ticks after he lands: the crater under him, the hit on Darius, who falls
    r0 = t
    on(d, small, "r_grab", r0 + tick(2))
    toss = r0 + tick(8)
    d.slides.append((toss, toss + tick(8), 24))
    d.hops.append((toss, toss + tick(8), 8))
    land_x = d.pos(toss + tick(8))[0] - 9                       # beside where Darius comes down
    a("ult", tick(8))
    a("ult_dash", tick((land_x - x) / 3.0), loop=True, to=land_x)
    x = land_x
    slam = t + tick(4)
    d.holds.append((r0 + tick(2), slam))
    under.append(Anim(frames_of(big, "r_slam"), slam, x, gy, z=-1))
    on(d, small, "r_hit", slam)
    d.death = slam + tick(6)
    a("ult_slam")
    a("idle", 1400, loop=True)
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
    sample = frames[::6]                              # one palette for the whole clip
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
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    s = load(CHAMP)
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags],
                            os.path.join(args.out, "league_sett_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[12:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_sett_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_sett_showcase.gif")))


if __name__ == "__main__":
    main()
