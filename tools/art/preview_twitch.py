#!/usr/bin/env python3
"""Preview images for Twitch, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_twitch.py [--out docs/preview] [--only frames|effects|showcase]

  league_twitch_frames.png    every animation, frame by frame, 3x on the arena colour
  league_twitch_effects.png   every effect animation, 3x
  league_twitch_showcase.gif  a scripted fight against Darius with Garen behind him, timed like the kit
                              (tools/kit/build_twitch.py, 60 ticks a second): Q - the smoke, he creeps in hidden (drawn
                              faint), the first bolt reveals him (the flash, the attack speed glow) and two bolts poison
                              Darius; W -> E: the cask lobbed between them, the splash and the puddle, both slowed, then
                              Contaminate bursts the venom on both; he turns round - facing left from here, as on the red
                              side - and casts R: the surge, the aura, piercing bolts through Darius and Garen; Darius
                              falls and Ambush resets; 3x
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
from build_twitch import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_twitch")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_twitch_fx", "league_twitch_big")}
MUZZLE = 19                                      # the crossbow's tip, px ahead of the pivot, at the pivot's row
BOLT = P["bolt_speed"] / 1000                    # px a tick
RBOLT = P["r_speed"] / 1000


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
    small, big = fx["league_twitch_fx"], fx["league_twitch_big"]
    W, H = 400, 150
    gy = 108
    x0 = 110
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 55, gy)       # his attack range
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 92, gy)        # behind Darius, in line
    me = Me(x0 - 60, gy)
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

    def bolt(foe, when, tag="a_bolt", speed=BOLT, last=None):
        """A bolt from the crossbow's tip to the foe (or on to `last`, the piercing one)."""
        sx = me.pos(when)[0] + (-MUZZLE if face[0] else MUZZLE)
        tx = (last or foe).pos(when)[0]
        arrive = when + tick(max(1, abs(tx - sx) / speed))
        fr = frames_of(small, tag)
        if face[0]:
            fr = [(f.transpose(Image.FLIP_LEFT_RIGHT), ms) for f, ms in fr]
        over.append(Anim(fr, when, sx, gy, until=arrive, x1=tx, y1=gy))
        return arrive

    # Q Ambush: the smoke, he creeps in hidden, Darius ahead
    q0 = t
    over.append(OnMe(frames_of(small, "q_cast"), q0, me))
    a("skill", tick(P["q_anim"]))
    creep = 900
    hidden.append((q0 + 120, t + creep))
    me.moves.append((t, t + creep, me.pos(t)[0], x0))
    a("run", creep, loop=True)
    # the first bolt reveals him: the flash, the attack speed glow; two bolts poison Darius
    over.append(OnMe(frames_of(small, "q_out"), t, me))
    over.append(OnMe(frames_of(small, "q_as"), t, me, until=t + 2600))
    for k in range(2):
        hit(d, "a_hit", bolt(d, t + tick(P["a_st"])))
        a("attack", tick(P["atk_dur"]))
        a("idle", tick(40), loop=True)
    # W -> E: the cask lobbed between them, the splash, the puddle, both slowed; E bursts the venom on both
    rel = t + tick(P["w_rel"])
    land = rel + tick(P["w_travel"])
    sx, cx = me.pos(rel)[0] + 5, (d.pos(rel)[0] + g.pos(rel)[0]) // 2
    up = (sx + cx) // 2
    over.append(Anim(frames_of(small, "w_cask"), rel, sx, gy - 18, until=(rel + land) / 2, x1=up, y1=gy - 40))
    over.append(Anim(frames_of(small, "w_cask"), (rel + land) / 2, up, gy - 40, until=land, x1=cx, y1=gy - 4))
    a("skill2", tick(P["w_dur"]))
    pool = land + tick(P["w_pool"])
    under.append(Anim(frames_of(big, "w_pool"), land, cx, gy + 9, loop=True, until=pool))
    for foe in (d, g):
        hit(foe, "w_hit", land)
        under.append(OnFoe(frames_of(small, "w_slow"), land, foe, until=pool))
    a("idle", land + tick(P["e_wait"]) - t, loop=True)
    e0 = t
    pop = e0 + tick(P["e_rel"])
    under.append(OnMe(frames_of(big, "e_cast"), pop, me))
    for foe in (d, g):
        hit(foe, "v_pop", pop, big)
    a("skill2_e", tick(P["e_anim"]))
    a("idle", 300, loop=True)
    # he turns round (the red side's facing), walks past them, and R: the surge, the aura, piercing bolts through both
    face[0] = True
    walk_to = g.pos(t)[0] + 55
    me.moves.append((t, t + 700, me.pos(t)[0], walk_to))
    a("run", 700, loop=True)
    r0 = t
    over.append(OnMe(frames_of(big, "r_cast"), r0 + tick(P["r_anim"]) // 2, me))
    over.append(OnMe(frames_of(big, "r_on"), r0, me, until=r0 + 2200))
    a("ult", tick(P["r_anim"]))
    for k in range(3):
        when = t + tick(P["a_st"])
        far = bolt(g, when, "r_bolt", RBOLT, last=d)
        sxx = me.pos(when)[0] - MUZZLE
        for foe in (g, d):
            hit(foe, "r_hit", when + tick(max(1, abs(sxx - foe.pos(when)[0]) / RBOLT)))
        a("attack", tick(P["atk_dur"]))
        a("idle", tick(20), loop=True)
    # Darius falls: Ambush resets over his head
    d.death = t - 200
    over.append(OnMe(frames_of(small, "q_reset"), d.death + tick(P["k_read"]), me))
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
                if any(h0 <= tt < h1 for h0, h1 in hidden):
                    f = faint([(f, 0)])[0][0]
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
                                os.path.join(args.out, "league_twitch_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_twitch_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_twitch_showcase.gif")))


if __name__ == "__main__":
    main()
