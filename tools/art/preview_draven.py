#!/usr/bin/env python3
"""Preview images for Draven, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_draven.py [--out docs/preview] [--only frames|effects|showcase]

  league_draven_frames.png    every animation, frame by frame, 3x on the arena colour
  league_draven_effects.png   every effect animation, 3x
  league_draven_showcase.gif  a scripted fight with Darius in front and Garen behind him, timed like the kit
                              (tools/kit/build_draven.py, 60 ticks a second): Q - an axe spins up (the icon over his
                              head); the spinning axe flies at Darius (Blood Rush: the burst, the glow at his feet),
                              bounces up, the catch circle and the axe falling into it on a spot ahead of him (q_far:
                              toward an enemy), he runs in and catches it as it lands; again, the spot behind him
                              (q_far2: toward an ally) - he runs back; a plain axe; E - the pair of axes through both,
                              the knock-back hits and the slows; R - the blades out to Darius and back; the cash-in
                              (gold) and the full Adoration twinkles; 3x
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
from build_draven import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_draven")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_draven_fx", "league_draven_big")}
HAND = 18                                        # the throwing hand: px in front of his pivot (the axes leave there;
                                                 # attack frame 4's arm reaches out 20)
AXE = P["axe_speed"] / 1000                      # px a tick
EAXE = P["e_speed"] / 1000
ROUT = P["r_speed"] / 1000
RBACK = P["r_back"] / 1000


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_draven_fx"], fx["league_draven_big"]
    W, H = 240, 110
    gy = 76
    x0 = 40
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 50, gy)
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 100, gy)
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

    def fly(tag, sheet, when, x1, speed, x_from=None, y=gy):
        sx = (me.pos(when)[0] + HAND) if x_from is None else x_from
        arrive = when + tick(max(1, abs(x1 - sx) / speed))
        over.append(Anim(frames_of(sheet, tag), when, sx, y, until=arrive, x1=x1, y1=y))
        return arrive

    def spin_throw(icon_from, step):
        """A spinning-axe attack: the icon goes, the axe flies and bounces; the circle and the axe falling into it
        on a spot `step` px away, he runs in (the run tag, flipped going back) and catches it as it lands."""
        rel = t + tick(P["a_st"])
        land = fly("q_axe", small, rel, d.pos(rel)[0], AXE)
        hit(d, "q_hit", land)
        b = land + tick(1)                           # the bounce: the spot shows, he runs over from the next tick
        x0_, px = me.pos(b)[0], me.pos(b)[0] + step
        walk = tick(P["q_fly"] - 3)
        under.append(Anim(frames_of(small, "q_zone"), b, px, gy))
        over.append(Anim(frames_of(small, "q_fall"), b, px, gy))
        me.moves.append((b + tick(1), b + tick(1) + walk, x0_, px))
        run = Anim(frames_of(sp, "run"), b, 0, 0, loop=True, until=b + tick(1) + walk, flip=step < 0)
        run.pos = me.pos
        body.insert(0, run)                          # over the attack's tail, like the forced run in game
        catch = b + tick(P["q_fly"] - 1)
        over.append(OnMe(frames_of(small, "q_catch"), catch, me))
        over.append(OnMe(frames_of(small, "ax1"), icon_from, me, until=rel, loop=True))
        return catch

    a("idle", 400, loop=True)
    # Q: an axe spins up (the icon over his head until it is thrown)
    q0 = t
    a("skill", tick(P["q_dur"]))
    a("idle", 120, loop=True)
    # the spinning axe at Darius; Blood Rush goes off with it
    over.append(OnMe(frames_of(small, "w_cast"), t, me))
    under.append(OnMe(frames_of(small, "w_ms"), t, me, until=t + tick(P["w_ms_t"]), loop=True))
    catch = spin_throw(q0, P["q_far"] // 1000)
    a("attack", tick(P["atk_dur"]))
    a("idle", max(120, catch - t + 60), loop=True)
    # caught: spinning again (the icon), thrown again
    q1 = catch
    catch = spin_throw(q1, -(P["q_far2"] // 1000))
    a("attack", tick(P["atk_dur"]))
    a("idle", max(120, catch - t + 60), loop=True)
    # a plain axe
    rel = t + tick(P["a_st"])
    hit(d, "a_hit", fly("a_axe", small, rel, d.pos(rel)[0], AXE))
    a("attack", tick(P["atk_dur"]))
    a("idle", 300, loop=True)
    # E: the pair of axes through both, the knock-back hits and the slows
    rel = t + tick(P["e_rel"])
    sx = me.pos(rel)[0] + HAND
    reach = sx + P["e_len"] // 1000
    over.append(Anim(frames_of(small, "e_axes"), rel, sx, gy, until=rel + tick((reach - sx) / EAXE), x1=reach, y1=gy))
    for foe in (d, g):
        arrive = rel + tick((foe.pos(rel)[0] - sx) / EAXE)
        hit(foe, "e_hit", arrive)
        under.append(OnFoe(frames_of(small, "e_slow"), arrive, foe, until=arrive + tick(P["e_slow_t"])))
    a("skill2", tick(P["e_dur"]))
    a("idle", 300, loop=True)
    # R: the blades out to the first champion (Darius) and back through him
    rel = t + tick(P["r_rel"])
    sx = me.pos(rel)[0] + HAND
    turn = fly("r_axes", big, rel, d.pos(rel)[0], ROUT)
    hit(d, "r_hit", turn)
    back = fly("r_axes", big, turn, me.pos(turn)[0], RBACK, x_from=d.pos(turn)[0])
    hit(d, "r_hit", turn + tick(2))
    a("ult", tick(P["r_dur"]))
    a("idle", max(200, back - t + 200), loop=True)
    # the cash-in (League of Draven) and the full Adoration twinkles
    over.append(OnMe(frames_of(small, "p_cash"), t, me))
    over.append(OnMe(frames_of(small, "p_6"), t, me, until=t + 1600, loop=True))
    a("idle", 1600, loop=True)
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
                                os.path.join(args.out, "league_draven_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_draven_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_draven_showcase.gif")))


if __name__ == "__main__":
    main()
