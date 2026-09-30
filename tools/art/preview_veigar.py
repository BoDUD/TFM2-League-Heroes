#!/usr/bin/env python3
"""Preview images for Veigar, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_veigar.py [--out docs/preview]

  league_veigar_frames.png    every animation, frame by frame, 3x on the arena colour
  league_veigar_effects.png   every effect animation, 3x
  league_veigar_showcase.gif  a scripted fight against Darius, timed like the kit: Veigar walks up and throws an
                              attack bolt; Baleful Strike's bolt goes through Darius and Phenomenal Evil's glow
                              lights on him (a stack); Event Horizon: 0.4 s after his cast the cage stands round
                              Darius and stuns him 1 s (a stack), and 0.75 s later Dark Matter falls into the
                              cage and bursts on him (a stack); another bolt while he is held; Primordial Burst:
                              the primal magic gathers at the staff raised over his head, the orb leaves at the
                              top of his leap and explodes on Darius, who falls (a stack for the hit, five for
                              the kill); 3x
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
from preview_yone import Path  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_veigar")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_veigar_fx", "league_veigar_big")}
SPEED = 54.0                                          # move speed 900: 54 px a second
LIFT = 4                                              # a projectile's picture 5000 - y_offset (1200) over the pivot
R_LIFT = 20                                           # the ult's orb: y_offset -15000


def showcase(out, z=3, step=40):
    veigar = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_veigar_fx"], fx["league_veigar_big"]
    W, H = 200, 150
    gy = 112                                          # the pivot row: Dark Matter starts 111 px over it
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), 135, gy)
    body, under, over = [], [], []
    t = 0.0
    x = 30

    def a(tag, dur=None, loop=False, way=None):
        nonlocal t
        an = Path(frames_of(veigar, tag), t, x, gy, loop=loop, until=(t + dur) if dur else None, way=way or ())
        body.append(an)
        t = an.until

    def fx_at(sp, tag, at, px, py=gy, ground=False, until=None, x1=None, y1=None, loop=None):
        an = Anim(frames_of(sp, tag), at, px, py, z=-1 if ground else 1,
                  loop=(until is not None) if loop is None else loop, until=until, x1=x1, y1=y1)
        (under if ground else over).append(an)
        return an

    def on_him(tag, t0, z=1):
        """A caster view: drawn on Veigar's pivot wherever he stands."""
        over.append(Follow(frames_of(small, tag), t0, x, gy, on=body, z=z))

    def on_foe(sp, tag, at, z=1):
        over.append(OnFoe(frames_of(sp, tag), at, d, z=z))

    def shoot(start, tag, speed, fire, reach=None, lift=LIFT):
        """A bolt leaves him `fire` ticks into the action and flies at `speed` px a tick: to Darius (the time of
        the hit returned), or `reach` px on through him (a line)."""
        launch = start + tick(fire)
        x0 = x + 4
        fx_, _ = d.pos(launch)
        arrive = launch + tick(max(1.0, (fx_ - 6 - x0) / speed))
        x1 = x0 + reach if reach else fx_ - 6
        fx_at(small, tag, launch, x0, gy - lift, until=launch + tick((x1 - x0) / speed), x1=x1, y1=gy - lift)
        return arrive

    def attack():
        hit = shoot(t, "orb", 4.5, 12)
        on_foe(small, "hit", hit)
        d.flinches.append(hit)
        a("attack", tick(28))
        return hit

    # he walks up to his range (55000; move speed 900)
    run = abs(d.x - 55 - x) / SPEED * 1000.0
    a("run", run, loop=True, way=[(0, x), (run, d.x - 55)])
    x = d.x - 55
    attack()
    a("idle", tick(20), loop=True)
    # Baleful Strike: the bolt leaves on tick 12 (7 px a tick) and flies its 95 px through him; a spell hit on a
    # champion: a stack and a rung of the ladder
    hit = shoot(t, "q_bolt", 7, 12, reach=95)
    on_foe(small, "q_hit", hit)
    d.flinches.append(hit)
    on_him("p_gain", hit)
    a("skill", tick(29))
    a("idle", tick(16), loop=True)
    # Event Horizon: cast on tick 12, the cage stands 24 ticks later round his spot for 3 s and stuns him 1 s
    # (a stack); Dark Matter falls with it and bursts 45 ticks later (a stack)
    form = t + tick(12 + 24)
    fx_at(big, "e_cage", form, d.x, gy, ground=True)
    fx_at(big, "w_mark", form, d.x, gy, ground=True)
    fx_at(big, "w_fall", form, d.x, gy)
    on_foe(small, "e_stun", form, z=2)
    d.holds.append((form, form + 1000))
    on_him("p_gain", form)
    blast = form + tick(45)
    on_foe(small, "w_hit", blast)
    on_him("p_gain", blast)
    a("skill2", tick(33))
    a("idle", form + tick(20) - t, loop=True)
    attack()
    a("idle", tick(24), loop=True)
    # Primordial Burst: the gathering orb from tick 2 at the raised staff, the bolt on tick 12 (5 px a tick), the
    # explosion on him - three rungs (Q, the cage, Dark Matter): +75%; he falls (a stack for the hit, five more
    # for the kill)
    on_him("r_cast", t + tick(2))
    hit = shoot(t, "r_bolt", 5, 12, lift=R_LIFT)
    on_foe(big, "r_hit", hit, z=2)
    d.flinches.append(hit)
    d.death = hit + 120
    on_him("p_gain", hit)
    on_him("p_gain", hit + 300)
    a("ult", tick(34))
    a("idle", 1800, loop=True)
    end = t

    def place(img, f, px, py):
        img.alpha_composite(f, (int(px) - f.width // 2, int(py) - f.height // 2))

    frames, tt = [], 0.0
    while tt < end:
        img = Image.new("RGBA", (W, H), ARENA)
        for an in under:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        units = [(d.pos(tt)[1], d.frame(tt), d.pos(tt))]
        for an in body:
            f = an.frame(tt)
            if f is not None:
                units.append((gy, f, an.pos(tt)))
                break
        for _, f, p in sorted(units, key=lambda u: u[0]):
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
    ap.add_argument("--frames-only", action="store_true", help="only the frames sheet (before the effects exist)")
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    s = load(CHAMP)
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags],
                            os.path.join(args.out, "league_veigar_frames.png")))
    if args.frames_only:
        return
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_veigar_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_veigar_showcase.gif")))


if __name__ == "__main__":
    main()
