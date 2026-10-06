#!/usr/bin/env python3
"""Preview images for Samira, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_samira.py [--out docs/preview] [--only frames|effects|showcase]

  league_samira_frames.png    every animation, frame by frame, 3x on the arena colour
  league_samira_effects.png   every effect animation, 3x
  league_samira_showcase.gif  a scripted fight against Darius with Garen behind him, timed like the kit
                              (tools/kit/build_samira.py, 60 ticks a second): Samira runs in; a shot (Style E); Q's
                              bullet down the line through both (D); E dashes through Darius (C) and lands behind him,
                              W's whirl cuts both (B); she turns on Darius - facing left from here, as on the red side:
                              her frames mirrored with what is drawn into them - a sword attack (A), Q's half-moon (S);
                              R: the storm round her, bullets at both every 12 ticks, Darius falls and E's reset flashes;
                              3x
"""
import argparse
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from preview_annie import Held  # noqa: E402
from preview_ashe import Anim, tick  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_samira")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_samira_fx", "league_samira_big")}
ATK_CD, ATK_DUR, A_SHOT, A_CUT = 58, 24, 12, 12        # atk_cd, atk_dur; bullet / sword cut ticks into the attack
Q_DUR, Q_SHOT, Q_CUT = 22, 9, 10
E_TICK, W_T, W1, W2 = 10, 45, 8, 40                    # the dash, then the whirl's two cuts after landing
R_T, R_PERIOD = 120, 12
BULLET_Y = -8                                          # the bullets' y_offset (8000)
GRADES = 6


class Me:
    """Samira's place over time: (t0, t1, x0, x1) moves, standing still between them."""

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
    def __init__(self, fr, t0, me, until=None, dy=0):
        super().__init__(fr, t0, 0, 0, loop=until is not None, until=until)
        self.me, self.dy = me, dy

    def pos(self, t):
        x, y = self.me.pos(t)
        return x, y + self.dy


class OnFoe(Anim):
    def __init__(self, fr, t0, foe):
        super().__init__(fr, t0, 0, 0)
        self.foe = foe

    def pos(self, t):
        return self.foe.pos(t)


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_samira_fx"], fx["league_samira_big"]
    W, H = 380, 150
    gy = 104
    x0 = 70
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 55, gy + 4)    # her attack range
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 112, gy - 8)    # behind him
    me = Me(x0, gy)
    body, over = [], []
    t = 0.0
    face = [False]                                     # flipped: facing left

    def a(tag, dur=None, loop=False):
        nonlocal t
        x, y = me.pos(t)
        an = Anim(frames_of(sp, tag), t, x, y, loop=loop, until=(t + dur) if dur else None, flip=face[0])
        body.append(an)
        t = an.until
        return an

    def fly(tag, launch, foe, speed, lead):
        """A bullet from her pivot, 8 px up, unseen for `lead` ticks (it leaves past the muzzle)."""
        sx, sy = me.pos(launch)
        tx, ty = foe.pos(launch)
        span = abs(tx - sx)
        arrive = launch + tick(max(1.0, span / speed))
        fr = [(f, ms) for f, ms in frames_of(small, tag)]
        if tx < sx:
            fr = [(f.transpose(Image.FLIP_LEFT_RIGHT), ms) for f, ms in fr]
        over.append(Anim(fr, launch, sx, sy + BULLET_Y, until=arrive, x1=tx, y1=ty + BULLET_Y))
        return arrive

    def hit(foe, tag, when):
        over.append(OnFoe(frames_of(small, tag), when, foe))
        foe.flinches.append(when)

    grade = [0]
    letters = []

    def climb(when):
        grade[0] = min(GRADES, grade[0] + 1)
        if letters:
            letters[-1].until = when
        lt = OnMe(frames_of(small, f"g{grade[0]}"), when, me, until=10 ** 9, dy=-36)
        letters.append(lt)
        over.append(lt)
        over.append(OnMe(frames_of(small, "g_s" if grade[0] == GRADES else "g_up"), when, me, dy=-36))

    # she runs in; Darius and Garen wait
    walk = Anim(frames_of(sp, "run"), 0.0, x0 - 50, gy, loop=True, until=1250, x1=x0)
    body.append(walk)
    t = walk.until
    a("idle", 300, loop=True)
    # a shot: the bullet leaves on tick 12 (the flash is in her frames)
    s0 = t
    arr = fly("a_bullet", s0 + tick(A_SHOT), d, 8, 3)
    hit(d, "a_hit", arr)
    climb(arr + tick(2))
    a("attack", tick(ATK_DUR))
    a("idle", tick(ATK_CD - ATK_DUR), loop=True)
    # Q, the gun: the bullet down the line through both
    q0 = t
    rel = q0 + tick(Q_SHOT)
    sx = me.pos(rel)[0]
    end_x = sx + 95
    over.append(Anim(frames_of(small, "q_bullet"), rel, sx, gy + BULLET_Y, until=rel + tick(95 / 9), x1=end_x,
                     y1=gy + BULLET_Y))
    for foe in (d, g):
        hit(foe, "q_hit", rel + tick((foe.pos(rel)[0] - sx) / 9))
    climb(rel + tick((d.pos(rel)[0] - sx) / 9) + tick(2))
    a("skill", tick(Q_DUR))
    a("idle", 300, loop=True)
    # E: through Darius to just behind him (the trail is in her frames), then W's whirl
    e0 = t
    land = e0 + tick(E_TICK)
    me.moves.append((e0, land, me.pos(e0)[0], d.pos(e0)[0] + 15))
    an = Anim(frames_of(sp, "skill2"), e0, me.pos(e0)[0], gy, until=e0 + tick(E_TICK + W_T),
              x1=d.pos(e0)[0] + 15)
    an.pos = me.pos                                     # she rides the dash, then stands
    body.append(an)
    pass_d = e0 + tick(E_TICK * 0.7)
    hit(d, "e_hit", pass_d)
    climb(land)
    over.append(OnMe(frames_of(big, "w_spin"), land, me, until=land + tick(W_T), dy=-3))
    for k, at in enumerate((W1, W2)):
        for foe in (d, g):
            hit(foe, "w_hit", land + tick(at))
    climb(land + tick(W2 + 2))
    t = an.until
    # she turns on Darius: facing left from here (the red side's way)
    face[0] = True
    a("idle", 250, loop=True)
    c0 = t
    hit(d, "a_slash_hit", c0 + tick(A_CUT))
    climb(c0 + tick(A_CUT + 2))
    a("attack_m", tick(22))
    a("idle", tick(ATK_CD - 22), loop=True)
    q1 = t
    hit(d, "q_slash_hit", q1 + tick(Q_CUT))
    climb(q1 + tick(Q_CUT + 2))
    a("skill_m", tick(20))
    a("idle", 250, loop=True)
    # R: the grades spent, the storm round her, a bullet at each foe within 55 px every 12 ticks
    r0 = t
    letters[-1].until = r0
    over.append(OnMe(frames_of(big, "r_on"), r0, me, until=r0 + tick(R_T), dy=-8))
    for k in range(R_T // R_PERIOD):
        s = r0 + tick(2 + k * R_PERIOD)
        for foe in ((d, g) if k < 7 else (g,)):
            arr = fly("r_bullet", s, foe, 12, 2)
            hit(foe, "r_hit", arr)
        if k == 6:
            d.death = arr + tick(2)
            over.append(OnMe(frames_of(small, "e_reset"), d.death + tick(4), me))
    a("ult", tick(R_T))
    a("idle", 1200, loop=True)
    end = t

    def place(img, f, px, py):
        img.alpha_composite(f, (px - f.width // 2, py - f.height // 2))

    frames, tt = [], 0.0
    while tt < end:
        img = Image.new("RGBA", (W, H), ARENA)
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
                                os.path.join(args.out, "league_samira_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_samira_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_samira_showcase.gif")))


if __name__ == "__main__":
    main()
