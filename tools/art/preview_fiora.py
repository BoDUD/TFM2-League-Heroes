#!/usr/bin/env python3
"""Preview images for Fiora, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_fiora.py [--out docs/preview]

  league_fiora_frames.png    every animation, frame by frame, 3x on the arena colour
  league_fiora_effects.png   every effect animation, 3x
  league_fiora_showcase.gif  a scripted duel with Darius, timed like the kit (60 ticks a second): Fiora walks in and
                             Lunges onto him (the dust where she set off, the stab on arrival): the stab reveals a Vital
                             on him and folds Bladework in (the glint round her); the first attack slows and strikes
                             the Vital (the shatter, the speed lines at her heels), the second is the critical thrust
                             (the glint goes), then a plain one; Riposte: the parry crescent for 0.75 s, Darius's swing
                             into it, the thrust down the line and Darius stunned for 1 s - the stab also reveals the
                             next Vital (3 s since the last was struck); Grand Challenge, its pace following the fight:
                             the salute, the ring of four Vitals round him and Bladework's two quick attacks (Vitals 1
                             and 2, the gold shatter, one crest fewer at the next piece); Lunge is back and stabs the
                             third, which caps its cooldown at half; Darius backs off and she follows, slower, until
                             that Lunge is back and catches him: the fourth leaves the victory zone under him; he
                             falls. 3x
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
from preview_jinx import Follow  # noqa: E402
from preview_yone import OnFoeFor, Path  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_fiora")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_fiora_fx", "league_fiora_big")}
ATK_CD, ATK_DUR, ATK_HIT = 62, 24, 9  # ticks between attacks, the action, its hit
E_AS = 1.5                            # Bladework: +50% attack speed until the critical thrust
Q_CD, Q_DUR, Q_SPEED = 330, 26, 4     # Lunge: cooldown, the action, px a tick from its first tick
W_PARRY, W_STAB, W_DUR = 45, 47, 64   # Riposte: the parry, the stab's tick, the action
STUN = 60                             # the stun of a parried Riposte
R_ANIM, R_FIRST, R_LINK = 18, 22, 20  # Grand Challenge: the salute; the remaining Vitals' first piece, piece length
R_CAP = 0.5                           # a Vital struck in the challenge caps Q's and W's cooldowns at half
V_LINK, V_CD = 20, 180               # a Vital's pieces, the wait for the next
REACH = 24                            # where a Lunge stops, px off the target


class Duelist(Held):
    """Darius: can also back off (turned away, running right) by dx px between t0 and t1."""

    def __init__(self, sp, x, y):
        super().__init__(sp, x, y)
        self.backs = []

    def pos(self, t):
        x, y = super().pos(t)
        for t0, t1, dx in self.backs:
            if t >= t0:
                x += int(round(dx * min(1.0, (t - t0) / (t1 - t0))))
        return x, y

    def frame(self, t):
        if self.death is None or t < self.death:
            for t0, t1, _ in self.backs:
                if t0 <= t < t1:
                    return self.pick(self.run, (t - t0) % sum(ms for _, ms in self.run))
        return super().frame(t)


def showcase(out, z=3, step=40):
    fiora = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_fiora_fx"], fx["league_fiora_big"]
    W, H = 330, 120
    gy = 84                                           # the pivot row
    d = Duelist(load(os.path.join(LEAGUE, "champions", "league_darius")), 172, gy)
    body, under, over = [], [], []
    t = 0.0
    x = 28

    def a(tag, dur=None, loop=False, way=None):
        nonlocal t
        an = Path(frames_of(fiora, tag), t, x, gy, loop=loop, until=(t + dur) if dur else None, way=way or ())
        body.append(an)
        t = an.until

    def on_foe(name, at, z=3):
        over.append(OnFoe(frames_of(small, name), at, d, z=z))

    def on_her(name, at, until, z=1):
        an = Follow(frames_of(small, name), at, x, gy, loop=True, until=until, on=body, z=z)
        (over if z > 0 else under).append(an)
        return an

    def vital(at, until):
        """A revealed Vital: its picture in V_LINK pieces from the reveal's first link until it is struck."""
        over.append(OnFoeFor(frames_of(small, "vital_mark"), at + tick(2), d, until, z=3))

    def strike(at, name="vital_hit"):
        """A struck Vital: the shatter, the heal and the speed lines at her heels (a caster picture: each plays out)."""
        on_foe(name, at, z=4)
        under.append(Follow(frames_of(small, "v_ms"), at, x, gy, on=body, z=-1))

    def attack(kind="plain", cd=ATK_CD):
        start = t
        hit = start + tick(ATK_HIT)
        a("attack_e" if kind == "crit" else "attack", tick(ATK_DUR))
        d.flinches.append(hit)
        on_foe({"plain": "hit", "first": "e_hit", "crit": "e_crit"}[kind], hit)
        a("idle", tick(cd - ATK_DUR), loop=True)
        return start, hit

    def lunge(to):
        """Lunge from here to `to` (4 px a tick from its first tick): the dust where she set off, the stab on arrival."""
        nonlocal x
        start = t
        arrive = start + tick(1 + abs(to - x) / Q_SPEED)
        under.append(Anim(frames_of(small, "q_dash"), start + tick(1), x, gy, z=-1))
        a("skill", tick(Q_DUR), way=[(start + tick(1), x), (arrive, to)])
        x = to
        d.flinches.append(arrive)
        on_foe("q_hit", arrive)
        return start, arrive

    # she walks in and Lunges onto him from 80 px: the dust where she set off, the stab on arrival
    a("run", 1016, loop=True, way=[(0, x), (1016, 92)])
    x = 92
    q1, arrive = lunge(138)                           # 34 px off Darius: attack range 25000 and his size
    # the stab reveals a Vital and folds Bladework in: the glint round her until the critical thrust starts
    glint = arrive
    _, h1 = attack("first", ATK_CD / E_AS)             # the slow, and the Vital struck
    vital(arrive, h1)
    strike(h1)
    struck = h1
    crit, _ = attack("crit", ATK_CD / E_AS)
    over.append(Follow(frames_of(small, "e_glint"), glint, x, gy, loop=True, until=crit, on=body, z=1))
    attack()
    # Riposte: the parry, Darius's swing into it, the stab on tick 47 down the line (its middle 27.5 px ahead)
    start = t
    on_her("w_parry", start, start + tick(W_PARRY), z=2)
    d.attacks.append(start + tick(12))
    a("skill2", tick(W_DUR))
    stab = start + tick(W_STAB)
    over.append(Anim(frames_of(small, "w_line"), stab, x + 28, gy, z=2))
    on_foe("w_hit", stab + tick(1))
    d.flinches.append(stab + tick(1))
    stun = stab + tick(2)                              # the first-champion thrust (20 px a tick) lands a tick later
    d.holds.append((stun, stun + tick(STUN)))
    on_foe("w_stun", stun, z=4)
    revealed = stun if stun - struck >= tick(V_CD) else None
    # Grand Challenge: the salute, the challenge on him (the passive's Vital goes), Bladework's two quick attacks
    start = t
    a("ult", tick(R_ANIM))
    if revealed is not None:
        vital(revealed, start)
    on_foe("r_on", start)
    _, v1 = attack("first", ATK_CD / E_AS)
    crit, v2 = attack("crit", ATK_CD / E_AS)
    over.append(Follow(frames_of(small, "e_glint"), start, x, gy, loop=True, until=crit, on=body, z=1))
    # Lunge is back: its stab strikes the third, and that Vital caps Lunge's new cooldown at half
    ready = q1 + tick(Q_CD)
    if t < ready:
        a("idle", ready - t, loop=True)
    q2, v3 = lunge(x + 34 - REACH)
    ready = v3 + tick(Q_CD * R_CAP)
    # he backs off and she follows, slower, out of her attack range, until that Lunge is back and catches him
    back = v3 + 120
    d.backs.append((back, ready - 100, 100))
    chase_to = d.x + 100 - 42                          # 42 px off: Lunge's reach
    a("run", ready - t, loop=True, way=[(t, x), (ready, chase_to)])
    x = chase_to
    _, v4 = lunge(d.x + 100 - REACH)
    hits = [v1, v2, v3, v4]
    for h in hits:
        strike(h, "r_hit")
    a("idle", 900, loop=True)
    # the remaining Vitals, a piece every 20 ticks showing how many were left when it started
    k = 0
    while True:
        p0 = start + tick(R_FIRST + k * R_LINK)
        left = 4 - sum(h <= p0 for h in hits)
        if not left:
            break
        on_foe(f"r_m{left}", p0)
        k += 1
    # the fourth: the victory zone where he stands (a lob landing the next tick); he falls
    zone = v4 + tick(2)
    under.append(Anim(frames_of(big, "r_zone"), zone, *d.pos(zone), z=-2))
    d.death = v4 + tick(14)
    end = t

    def place(img, f, px, py):
        img.alpha_composite(f, (int(px) - f.width // 2, int(py) - f.height // 2))

    frames, tt = [], 0.0
    while tt < end:
        img = Image.new("RGBA", (W, H), ARENA)
        for an in sorted(under, key=lambda o: o.z):
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        units = [(1, d.frame(tt), d.pos(tt))]
        for an in body:
            f = an.frame(tt)
            if f is not None:
                units.append((0, f, an.pos(tt)))
                break
        for _, f, p in sorted(units, key=lambda u: -u[2][0]):      # the farther right, the further back
            if f is not None:
                place(img, f, *p)
        for an in sorted(over, key=lambda o: o.z):
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
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q[0].save(T.long_path(out), save_all=True, append_images=q[1:], duration=step, loop=0, optimize=False)
    return len(frames), round(end / 1000.0, 1), [round(h / 1000.0, 2) for h in hits]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    s = load(CHAMP)
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_fiora_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_fiora_effects.png")))
    print("showcase frames/seconds/Vitals", showcase(os.path.join(args.out, "league_fiora_showcase.gif")))


if __name__ == "__main__":
    main()
