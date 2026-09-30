#!/usr/bin/env python3
"""Preview images for Briar, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_briar.py [--out docs/preview]

  league_briar_frames.png    every animation, frame by frame, 3x on the arena colour
  league_briar_effects.png   every effect animation, 3x
  league_briar_showcase.gif  a scripted fight, timed like the kit: Briar runs in and Head Rushes onto Darius - the
                             headbutt stuns him and she lands in Blood Frenzy (the crimson aura), biting him fast;
                             2 s in, Snack Attack's jaws snap on him and heal her; Chilling Scream: she charges a
                             second behind her shell, the scream knocks him back and stuns him; Garen walks in far
                             away - Certain Death: she kicks the gem at him, flies to him and lands in a crimson
                             blast, Darius (not her prey) runs off in fear, Garen carries the prey mark, and she
                             bites him in Hemomania; Darius falls to the bleeds; 3x
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
CHAMP = os.path.join(LEAGUE, "champions", "league_briar")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_briar_fx", "league_briar_big")}


def showcase(out, z=3, step=40):
    briar = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_briar_fx"], fx["league_briar_big"]
    W, H = 300, 150
    gy = 104                                          # the pivot row: her pillory's gem stands 46 px tall
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), 150, gy)
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), 290, gy)
    body, under, over = [], [], []
    t = 0.0
    x = 30

    def a(tag, dur=None, loop=False, at=None, way=None):
        nonlocal t
        an = Path(frames_of(briar, tag), t, at if at is not None else x, gy, loop=loop,
                  until=(t + dur) if dur else None, way=way or ())
        body.append(an)
        t = an.until

    def fx_at(sp, tag, at, px, py=gy, ground=False, until=None, x1=None, y1=None, loop=None):
        an = Anim(frames_of(sp, tag), at, px, py, z=-1 if ground else 1,
                  loop=(until is not None) if loop is None else loop, until=until, x1=x1, y1=y1)
        (under if ground else over).append(an)
        return an

    def on_her(tag, t0, until=None, loop=False, z=1):
        over.append(Follow(frames_of(small, tag), t0, x, gy, loop=loop, until=until, on=body, z=z))

    def bites(n, foe, frenzy_start, snack_at=None, gap=43):
        """n basic attacks on foe (the hit on tick 8, one every `gap` ticks in a frenzy); the first attack at or
        after snack_at is Snack Attack."""
        nonlocal t
        snacked = False
        for _ in range(n):
            start = t
            hit = start + tick(8)
            if snack_at is not None and not snacked and hit >= snack_at:
                over.append(OnFoe(frames_of(small, "snack"), hit, foe, z=2))
                on_her("snack_heal", hit)
                snacked = True
            else:
                over.append(OnFoe(frames_of(small, "hit"), hit, foe, z=2))
            foe.flinches.append(hit)
            a("attack", tick(25))
            a("idle", tick(max(1, gap - 25)), loop=True)

    # she runs in (move speed 1100: 66 px a second)
    a("run", 1200, loop=True, way=[(0, x), (1200, 100)])
    x = 100
    # Head Rush (leaps from tick 3, lands on him, stuns 0.5 s) and Blood Frenzy for 5 s
    start = t
    land = start + tick(14)
    a("skill", tick(24), way=[(start + tick(3), x), (land, 128)])
    x = 128
    over.append(OnFoe(frames_of(small, "q_hit"), land, d, z=2))
    d.holds.append((land, land + 500))
    on_her("frenzy", land, until=land + 5000, loop=True, z=-1)
    # the frenzied bites (attack speed +40%: one every 43 ticks), Snack Attack 2 s in
    bites(6, d, land, snack_at=land + 2000)
    # Chilling Scream: 1 s charge behind her shell, the scream on tick 64 (knockback 40 px, then a 1 s stun)
    start = t
    on_her("e_guard", start, until=start + 1000, loop=True)
    scream = start + tick(64)
    fx_at(big, "e_wave", scream, x + 25, gy - 10)
    over.append(OnFoe(frames_of(small, "e_hit"), scream, d, z=2))
    d.slides.append((scream, scream + tick(16), 40))
    d.holds.append((scream + tick(16), scream + tick(16) + 1000))
    over.append(OnFoe(frames_of(small, "e_stun"), scream + tick(16), d, z=3))
    a("skill2", tick(60))
    a("skill2_scream", tick(20))
    a("idle", 400, loop=True)
    # Garen walks in; Certain Death: the kick (the gem leaves on tick 8), the flight, the landing blast
    g.walks.append((t - 1500, t + 200, -60))
    start = t
    kick = start + tick(8)
    gx, gyy = g.pos(kick + 300)
    arrive = kick + 300
    fx_at(small, "r_gem", kick, x + 10, gy - 14, until=arrive, x1=gx - 8, y1=gyy - 14)
    over.append(OnFoe(frames_of(small, "r_mark"), arrive, g, z=3))
    over.append(OnFoeFor(frames_of(small, "r_mark"), arrive, g, arrive + 6000, z=3))
    a("ult", tick(30))
    fly_end = t + 400
    a("ult_fly", 400, loop=True, way=[(t, x), (fly_end, gx - 26)])
    x = gx - 26
    blast = t
    fx_at(big, "r_boom", blast, x, gy, ground=True)
    for foe in (g, d):
        over.append(OnFoe(frames_of(small, "r_hit"), blast, foe, z=2))
        foe.flinches.append(blast)
    over.append(OnFoe(frames_of(small, "r_fear"), blast, d, z=3))
    d.walks.append((blast, blast + 1500, -50))
    on_her("hema", blast, until=blast + 6000, loop=True, z=-1)
    a("ult_land", tick(26))
    bites(5, g, blast, snack_at=blast + 2000)
    d.death = blast + 1800
    a("idle", 1500, loop=True)
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
        units = [(d.pos(tt)[1], d.frame(tt), d.pos(tt)), (g.pos(tt)[1] - 0.5, g.frame(tt), g.pos(tt))]
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
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_briar_frames.png")))
    if args.frames_only:
        return
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_briar_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_briar_showcase.gif")))


if __name__ == "__main__":
    main()
