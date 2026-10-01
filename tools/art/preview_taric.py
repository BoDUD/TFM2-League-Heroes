#!/usr/bin/env python3
"""Preview images for Taric, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_taric.py [--out docs/preview] [--frames-only]

  league_taric_frames.png    every animation, frame by frame, 3x on the arena colour
  league_taric_effects.png   every effect animation, 3x
  league_taric_showcase.gif  a scripted fight with Ashe behind him against Darius and Garen, timed like the kit: Taric
                             walks up and strikes Darius; Starlight's Touch and Bastion: the gem flies to Ashe and binds
                             her (shield, the link's sigil under her feet), the starlight circle heals him and, through
                             the link, her; Bravado's two quick empowered strikes; Garen walks round to Ashe; Dazzle:
                             the beam charges along the ground and bursts on Darius, and the link bursts round Ashe on
                             the same tick, stunning Garen beside her; two more empowered strikes; with two enemies on
                             them, Cosmic Radiance: the heavens' light descends on Taric and on Ashe for 2.5 s, then
                             both shine invulnerable for 2.5 s while he strikes twice more; 3x
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

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_taric")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_taric_fx", "league_taric_big")}
SPEED = 60.0                                          # move speed 1000: 60 px a second
LIFT = 3                                              # the gem's picture: 5000 - y_offset (2000) over the pivot
LINK = 2                                              # ticks from his cast to the link's picture on the ally (the lob)


def showcase(out, z=3, step=40):
    taric = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_taric_fx"], fx["league_taric_big"]
    W, H = 260, 140
    gy = 100                                          # Taric's pivot row: R's halo rises 53 px over it
    xa, ya = 46, gy - 6                               # Ashe, linked, behind him
    ashe = Anim(frames_of(load(os.path.join(LEAGUE, "champions", "league_ashe")), "idle"), 0.0, xa, ya,
                loop=True, until=None)
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), 140, gy)          # 28 px: his reach
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), 236, gy - 12)      # walking round to Ashe
    body, under, over = [], [], []
    t = 0.0
    x = 60

    def a(tag, dur=None, loop=False, to=None):
        nonlocal t
        an = Anim(frames_of(taric, tag), t, x, gy, loop=loop, until=(t + dur) if dur else None, x1=to)
        body.append(an)
        t = an.until

    def fx_at(sp, tag, at, px, py, ground=False, until=None, x1=None, y1=None, loop=None, flip=False):
        an = Anim(frames_of(sp, tag), at, px, py, z=-1 if ground else 1,
                  loop=(until is not None) if loop is None else loop, until=until, x1=x1, y1=y1, flip=flip)
        (under if ground else over).append(an)
        return an

    def on_him(sp, tag, t0, until=None, z=1):
        """A view on Taric (is_follow, or a buff's while it lasts)."""
        an = Follow(frames_of(sp, tag), t0, x, gy, on=body, z=z, loop=until is not None, until=until)
        (under if z < 0 else over).append(an)

    def on_ashe(sp, tag, t0, until=None, ground=False):
        fx_at(sp, tag, t0, xa, ya, ground=ground, until=until)

    def strike(empowered, t0):
        """A basic attack on Darius from t0: the plain one's hit on tick 10; Bravado's strike on tick 9."""
        if empowered:
            hit = t0 + tick(9)
            over.append(OnFoe(frames_of(small, "p_hit"), hit, d, z=1))
            an = Anim(frames_of(taric, "attack_p"), t0, x, gy)
        else:
            hit = t0 + tick(10)
            over.append(OnFoe(frames_of(small, "hit"), hit, d, z=1))
            an = Anim(frames_of(taric, "attack"), t0, x, gy)
        d.flinches.append(hit)
        body.append(an)
        return an.until

    def idle_until(t1):
        nonlocal t
        if t1 > t:
            a("idle", t1 - t, loop=True)

    def bravado(t0):
        """Two empowered strikes after a spell (attack speed +100%: a strike every 40 ticks); the glow from the spell
        until the second strike starts."""
        nonlocal t
        first = max(t, t0)
        on_him(small, "p_glow", t0, until=first + tick(40))
        for k in range(2):
            idle_until(first + tick(40) * k)
            t = strike(True, t)
        idle_until(first + tick(40) + tick(26))

    # he walks up to Darius; Garen walks round to Ashe
    run = (112 - x) / SPEED * 1000.0
    a("run", run, loop=True, to=112)
    x = 112
    g.walks.append((0.0, 3400.0, (xa + 22) - g.x))
    t0 = t
    t = strike(False, t)
    idle_until(t0 + tick(80))
    # Starlight's Touch + Bastion, on tick 12: the gem flies to Ashe (6 px a tick) and binds her there and then
    # (shield, armour, the link's sigil for 12 s); the circle heals him, and the link heals her 2 ticks later
    cast = t + tick(12)
    arrive = cast + tick((x - xa) / 6.0)
    fx_at(small, "w_bolt", cast, x + 4, gy - LIFT, until=arrive, x1=xa + 4, y1=ya - LIFT, flip=True)
    on_ashe(small, "w_bind", cast)
    on_ashe(small, "w_link", cast, until=1e9, ground=True)
    on_him(big, "q_cast", cast, z=-1)
    on_him(small, "q_heal", cast)
    on_ashe(small, "q_heal", cast + tick(LINK))
    a("skill2")
    bravado(cast)
    # Dazzle, on tick 12: the beam charges along the ground and bursts 44 ticks later on Darius (stunned 75 ticks);
    # round Ashe the link's burst starts 2 ticks later and hits on the same tick: Garen, beside her, is stunned too
    cast = t + tick(12)
    fx_at(big, "e_beam", cast, x + 31, gy, ground=True)
    burst = cast + tick(44)
    fx_at(big, "e_ally", cast + tick(LINK), xa, ya, ground=True)
    for foe in (d, g):
        over.append(OnFoe(frames_of(small, "e_hit"), burst, foe, z=1))
        foe.holds.append((burst, burst + tick(75)))
    a("skill")
    bravado(cast)
    # Cosmic Radiance, both foes within reach: the call on him and, through the link, on Ashe; 150 ticks later both
    # shine and stay invulnerable for 150 ticks; the spell arms Bravado again
    start = t
    on_him(big, "r_call", start)
    on_ashe(big, "r_call", start + tick(LINK))
    shine = start + tick(150)
    on_him(small, "r_shine", shine)
    on_him(small, "r_invuln", shine, until=shine + tick(150))
    on_ashe(small, "r_shine", shine + tick(LINK))
    on_ashe(small, "r_invuln", shine + tick(LINK), until=shine + tick(LINK + 150))
    a("ult", tick(40))
    idle_until(start + tick(90))
    bravado(start)
    idle_until(shine + tick(160))
    a("idle", 800, loop=True)
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
        units = [(g.pos(tt)[1], g.frame(tt), g.pos(tt)), (d.pos(tt)[1], d.frame(tt), d.pos(tt)),
                 (ya, ashe.frame(tt), ashe.pos(tt))]
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
                            os.path.join(args.out, "league_taric_frames.png")))
    if args.frames_only:
        return
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_taric_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_taric_showcase.gif")))


if __name__ == "__main__":
    main()
