#!/usr/bin/env python3
"""Preview images for Pyke, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_pyke.py [--out docs/preview] [--only frames|effects|showcase]

  league_pyke_frames.png    every animation, frame by frame, 3x on the arena colour
  league_pyke_effects.png   every effect animation, 3x
  league_pyke_showcase.gif  a scripted fight against Darius with Garen behind him, timed like the kit
                            (tools/kit/build_pyke.py, 60 ticks a second): Pyke runs in and slashes Darius; Q held:
                            the harpoon flies at Garen, hooks him and drags him in, the harpoon comes back; W -> E: the
                            water bursts at his feet, he dives through Darius, the puddle where he started sends the
                            phantom back to him, Darius stunned; he turns on Darius - facing left from here, as on the
                            red side - and stabs him (Q tap, the slow); R: the X on Darius, the strike, Darius
                            executed, Pyke blinks onto him, the bounty; the grey health comes back; 3x
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
from build_pyke import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_pyke")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_pyke_fx", "league_pyke_big")}
HOOK_Y = -5                                            # the harpoon's y_offset (0: 5 px over the pivot, his hand)


class Me:
    """Pyke's place over time: (t0, t1, x0, x1) moves, standing still between them."""

    def __init__(self, x, y):
        self.x, self.y, self.moves = x, y, []

    def pos(self, t):
        x = self.x
        for t0, t1, x0, x1 in self.moves:
            if t >= t1:
                x = x1
            elif t >= t0:
                x = x0 + (x1 - x0) * (t - t0) / (t1 - t0)
        return int(round(x)), self.y


class OnMe(Anim):
    def __init__(self, fr, t0, me, until=None, dy=0, loop=False):
        super().__init__(fr, t0, 0, 0, loop=loop or until is not None, until=until)
        self.me, self.dy = me, dy

    def pos(self, t):
        x, y = self.me.pos(t)
        return x, y + self.dy


class OnFoe(Anim):
    def __init__(self, fr, t0, foe, until=None):
        super().__init__(fr, t0, 0, 0, loop=until is not None, until=until)
        self.foe = foe

    def pos(self, t):
        return self.foe.pos(t)


def mirrored(fr):
    return [(f.transpose(Image.FLIP_LEFT_RIGHT), ms) for f, ms in fr]


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_pyke_fx"], fx["league_pyke_big"]
    W, H = 400, 150
    gy = 108
    x0 = 80
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 34, gy + 2)    # in his reach
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 150, gy - 8)    # far behind
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

    def hit(foe, tag, when):
        over.append(OnFoe(frames_of(small, tag), when, foe))
        foe.flinches.append(when)

    # he runs in
    walk = Anim(frames_of(sp, "run"), 0.0, x0 - 60, gy, loop=True, until=1100, x1=x0)
    body.append(walk)
    t = walk.until
    a("idle", 300, loop=True)
    # the harpoon slash
    hit(d, "a_hit", t + tick(P["a_st"]))
    a("attack", tick(P["atk_dur"]))
    a("idle", tick(P["atk_cd"] - P["atk_dur"]), loop=True)
    # Q held: the charge (the glow on the raised blade), the throw at Garen, the drag, the harpoon back
    q0 = t
    rel = q0 + tick(P["q_hold"])
    sx = me.pos(rel)[0]
    gx = g.pos(rel)[0] - 8
    arrive = rel + tick((gx - sx) / (P["q_speed"] / 1000))
    over.append(Anim(frames_of(small, "q_hook"), rel, sx, gy + HOOK_Y, until=arrive, x1=gx, y1=gy + HOOK_Y))
    hit(g, "q_hit", arrive)
    stop = d.pos(arrive)[0] + 26                 # pulled in until just past Darius (not on top of him)
    drag = tick((gx - stop) / (P["q_grab"] / 1000))
    g.holds.append((arrive, arrive + drag))
    g.walks.append((arrive, arrive + drag, -(gx - stop)))
    over.append(Anim(mirrored(frames_of(small, "q_return")), arrive, gx, gy + HOOK_Y, until=arrive + drag,
                     x1=sx + 6, y1=gy + HOOK_Y))
    over.append(OnFoe(frames_of(small, "q_slow"), arrive, g, until=arrive + tick(P["q_slow_t"])))
    a("skill", tick(P["q_hold"] + P["q_throw_t"]))
    a("idle", max(300, arrive + drag - t + 200), loop=True)
    # W -> E: the water at his feet, the lead, the dive through Darius, the phantom back from the puddle
    w0 = t
    over.append(OnMe(frames_of(small, "w_cast"), w0, me))
    a("idle", tick(P["c_lead"]), loop=True)
    e0 = t
    start = me.pos(e0)[0]
    land_x = d.pos(e0)[0] + 18
    land = e0 + tick((land_x - start) / (P["e_speed"] / 1000))
    me.moves.append((e0, land, start, land_x))
    under.append(Anim(frames_of(big, "e_left"), e0, start, gy + 11))
    for k in range(1, P["e_t"], 2):              # the wake: a streak dropped every 2 ticks of the dash
        under.append(Anim(frames_of(small, "e_trail"), e0 + tick(k), me.pos(e0 + tick(k))[0], gy + 9))
    a("skill2", tick(P["e_t"]))
    back = e0 + tick(P["e_ret"])
    reach = back + tick((land_x - start) / (P["e_ph_speed"] / 1000))
    over.append(Anim(frames_of(big, "e_phantom"), back, start, gy, until=reach, x1=land_x, y1=gy))
    pass_d = back + tick((d.pos(back)[0] - start) / (P["e_ph_speed"] / 1000))
    hit(d, "e_hit", pass_d)
    d.holds.append((pass_d, pass_d + tick(P["e_stun"])))
    over.append(OnFoe(frames_of(small, "e_stun"), pass_d, d, until=pass_d + tick(P["e_stun"])))
    # he turns on Darius: facing left from here (the red side's way)
    face[0] = True
    a("idle", 250, loop=True)
    s0 = t
    hit(d, "q_stab_hit", s0 + tick(P["q_stab_at"]))
    over.append(OnFoe(frames_of(small, "q_slow"), s0 + tick(P["q_stab_at"]), d,
                      until=s0 + tick(P["q_stab_at"] + P["q_slow_t"])))
    a("skill_stab", tick(P["q_stab_t"]))
    a("idle", 300, loop=True)
    # R: the X on Darius, the strike, the execute, the blink, the bounty
    r0 = t
    dx_, dy_ = d.pos(r0)
    under.append(Anim(frames_of(big, "r_mark"), r0, dx_, dy_ + 11, until=r0 + tick(P["r_delay"])))
    over.append(Anim(frames_of(big, "r_strike"), r0 + tick(P["r_delay"] - 6), dx_, dy_ + 11))
    strike = r0 + tick(P["r_delay"] + 1)
    hit(d, "r_hit", strike)
    d.death = strike + tick(1)
    a("ult", tick(P["r_anim"]))
    blink = strike + tick(P["k_read"])
    me.moves.append((blink, blink + 1, me.pos(blink)[0], dx_ + 4))
    over.append(OnMe(frames_of(small, "r_reset"), blink, me, dy=-9))
    a("idle", 600, loop=True)
    # the grey health comes back while nobody hits him
    over.append(OnMe(frames_of(small, "p_heal"), t, me))
    a("idle", 1200, loop=True)
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
                                os.path.join(args.out, "league_pyke_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[12:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_pyke_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_pyke_showcase.gif")))


if __name__ == "__main__":
    main()
