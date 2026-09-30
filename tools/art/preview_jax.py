#!/usr/bin/env python3
"""Preview images for Jax, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_jax.py [--out docs/preview]

  league_jax_frames.png    every animation, frame by frame, 3x on the arena colour
  league_jax_effects.png   every effect animation, 3x
  league_jax_showcase.gif  a scripted fight against Darius, timed like the kit (60 ticks a second): Jax runs in and
                           Leap Strike carries him onto Darius - the landing (tick 15) spends Empower, ready, on the
                           leap (the landing's dust and the charged smash); three attacks, the third Grandmaster's
                           proc (the gold star); Counter Strike: the lamppost spun overhead, 1.5 s of the violet whirl
                           under him while he keeps attacking (his stance swings), then the counter - the fire ring
                           round him (release on tick 4) and Darius stunned for 1 s; Empower is ready again: the
                           charged smash; Garen walks up behind Darius and Grandmaster-at-Arms leaps and slams (tick
                           15): the cracked ring under him, a hit on both, the gold aura under him from then on and
                           the reversed-grip thrusts, the proc on every second attack; Darius falls. 3x
"""
import argparse
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from preview_annie import Held, OnFoe  # noqa: E402
from preview_ashe import tick  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_jinx import Follow  # noqa: E402
from preview_yone import Path  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_jax")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_jax_fx", "league_jax_big")}
SPEED = 63.0                          # move speed 1050: 63 px a second
ATK_CD = 64                           # ticks between attacks, less 7% a Relentless Assault stack (eight at most)
STANCE = 90                           # Counter Strike's stance, ticks
STUN = 60                             # its stun, ticks
AURA = 480                            # Grandmaster-at-Arms' buff, ticks


def showcase(out, z=3, step=40):
    jax = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_jax_fx"], fx["league_jax_big"]
    W, H = 260, 150
    gy = 96                                           # the pivot row: the ult's raised lamppost stands 63 px over it
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), 186, gy)
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), 292, gy)
    body, under, over = [], [], []
    t = 0.0
    x = 30
    stacks = 0
    swings = 0                                        # attacks since the last Grandmaster proc
    r_on = False

    def a(tag, dur=None, loop=False, way=None):
        nonlocal t
        an = Path(frames_of(jax, tag), t, x, gy, loop=loop, until=(t + dur) if dur else None, way=way or ())
        body.append(an)
        t = an.until

    def hit_fx(name, at, foe=d):
        foe.flinches.append(at)
        over.append(OnFoe(frames_of(small, name), at, foe, z=3))

    def attack(tag="attack", empowered=False):
        """An attack: the swing picked on tick 1, the hit on tick 10, Grandmaster every third (second in R)."""
        nonlocal stacks, swings
        start = t
        hit = start + tick(10)
        swings += 1
        hit_fx("w_hit" if empowered else "hit", hit)
        if swings >= (2 if r_on else 3):
            swings = 0
            over.append(OnFoe(frames_of(small, "r_proc"), hit + 20, d, z=4))
        a("attack_w" if empowered else tag, tick(25))
        cd = ATK_CD / (1 + 0.07 * stacks)
        stacks = min(8, stacks + 1)
        a("idle", tick(max(0.0, cd - 25)), loop=True)

    # he runs in (63 px a second) and Leap Strike carries him onto Darius; the landing spends Empower
    a("run", 1270, loop=True, way=[(0, x), (1270, 110)])
    x = 110
    start = t
    a("skill", tick(31), way=[(start + tick(3), x), (start + tick(14), 150)])
    x = 150
    land = start + tick(15)
    over.append(OnFoe(frames_of(small, "q_hit"), land, d, z=3))
    hit_fx("w_hit", land + 10)
    a("idle", tick(10), loop=True)
    # three attacks, the third Grandmaster's proc
    for _ in range(3):
        attack()
    # Counter Strike: the spin overhead, the whirl under him for the stance while he keeps attacking, the counter
    start = t
    under.append(Follow(frames_of(small, "e_stance"), start, x, gy, loop=True, until=start + tick(STANCE + 2),
                        on=body, z=-1))
    a("skill2", tick(22))
    while t + tick(64) < start + tick(STANCE):
        attack("attack_e")
    a("idle", max(0.0, start + tick(STANCE) - t), loop=True)
    burst = t
    a("skill2_burst", tick(26))
    release = burst + tick(4)
    under.append(Follow(frames_of(big, "e_burst"), release, x, gy, on=body, z=-2))
    d.flinches.append(release)
    d.holds.append((release, release + tick(STUN)))
    over.append(OnFoe(frames_of(small, "stun"), release, d, z=3))
    a("idle", tick(8), loop=True)
    # Empower is ready again: the charged smash
    attack(empowered=True)
    # Garen walks up behind Darius; Grandmaster-at-Arms leaps and slams on tick 15, a hit on both
    g.walks.append((t - 900, t + 400, -86))
    a("idle", 300, loop=True)
    start = t
    a("ult", tick(31))
    slam = start + tick(15)
    under.append(Follow(frames_of(big, "r_slam"), slam, x, gy, on=body, z=-2))
    for foe in (d, g):
        hit_fx("r_hit", slam, foe)
    aura = Follow(frames_of(big, "r_aura"), slam, x, gy, loop=True, until=slam + tick(AURA), on=body, z=-3)
    under.append(aura)
    r_on = True
    swings = 0
    for _ in range(4):
        attack("attack_r")
    d.death = t - tick(20)
    a("idle", 800, loop=True)
    end = t
    aura.until = min(aura.until, end)

    def place(img, f, px, py):
        img.alpha_composite(f, (int(px) - f.width // 2, int(py) - f.height // 2))

    frames, tt = [], 0.0
    while tt < end:
        img = Image.new("RGBA", (W, H), ARENA)
        for an in sorted(under, key=lambda o: o.z):
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        units = [(1, d.frame(tt), d.pos(tt)), (2, g.frame(tt), g.pos(tt))]
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
    return len(frames), round(end / 1000.0, 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    s = load(CHAMP)
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_jax_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[11:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_jax_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_jax_showcase.gif")))


if __name__ == "__main__":
    main()
