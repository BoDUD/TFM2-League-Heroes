#!/usr/bin/env python3
"""Preview images for Briar, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_briar.py [--out docs/preview]

  league_briar_frames.png    every animation, frame by frame, 3x on the arena colour
  league_briar_effects.png   every effect animation, 3x
  league_briar_showcase.gif  a scripted fight, timed like the kit: Briar runs in and Head Rushes onto Darius - the
                             headbutt stuns him and she lands in Blood Frenzy (the crimson aura), biting him fast;
                             2 s in, Snack Attack's jaws snap on him and heal her; Chilling Scream: she charges a
                             second behind her shell, the scream knocks him back and stuns him; he runs off -
                             Certain Death: she kicks the gem, it stops on Darius and marks him her prey, she
                             flies to him and lands in a crimson blast that hits him and Garen, walking in on the
                             front row, and fears Garen (not her prey) off the field; in Hemomania she bites
                             Darius until Snack Attack finishes him; 3x
"""
import argparse
import math
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


class Prey(Held):
    """A foe that also runs: moves (t0, t1, dx, dy) in League's run frames, facing the way it runs."""

    def __init__(self, sp, x, y):
        super().__init__(sp, x, y)
        self.moves = []

    def pos(self, t):
        x, y = super().pos(t)
        for t0, t1, dx, dy in self.moves:
            if t >= t0:
                u = min(1.0, (t - t0) / (t1 - t0))
                x, y = x + int(round(dx * u)), y + int(round(dy * u))
        return x, y

    def frame(self, t):
        if self.death is None or t < self.death:
            for t0, t1, dx, _ in self.moves:
                if t0 <= t < t1:
                    f = self.pick(self.run, (t - t0) % sum(ms for _, ms in self.run))
                    return self.flip(f) if dx < 0 else f
        return super().frame(t)


def showcase(out, z=3, step=40):
    briar = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_briar_fx"], fx["league_briar_big"]
    W, H = 300, 118
    gy = 80                                           # the pivot row: her pillory's gem stands 46 px tall
    d = Prey(load(os.path.join(LEAGUE, "champions", "league_darius")), 150, gy)
    g = Prey(load(os.path.join(LEAGUE, "champions", "league_garen")), 330, gy + 10)     # off the right edge, in front
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

    def bites(n, foe, snack_at, gap):
        """n basic attacks on foe (the hit on tick 8, one every `gap` ticks in a frenzy): the first one landing
        2 s into the frenzy is Snack Attack; the time of the last hit."""
        snacked, hit = False, None
        for _ in range(n):
            hit = t + tick(8)
            if not snacked and hit >= snack_at:
                over.append(OnFoe(frames_of(small, "snack"), hit, foe, z=2))
                on_her("snack_heal", hit)
                snacked = True
            else:
                over.append(OnFoe(frames_of(small, "hit"), hit, foe, z=2))
            foe.flinches.append(hit)
            a("attack", tick(25))
            a("idle", tick(max(1, gap - 25)), loop=True)
        return hit

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
    bites(6, d, land + 2000, 43)
    # Chilling Scream: 1 s charge behind her shell, the scream on tick 64 (knockback 40 px, then a 1 s stun)
    start = t
    on_her("e_guard", start, until=start + 1000, loop=True)
    scream = start + tick(64)
    fx_at(big, "e_wave", scream, x + 25, gy - 10)
    over.append(OnFoe(frames_of(small, "e_hit"), scream, d, z=2))
    d.slides.append((scream, scream + tick(16), 40))
    stun_end = scream + tick(16) + 1000
    d.holds.append((scream + tick(16), stun_end))
    over.append(OnFoe(frames_of(small, "e_stun"), scream + tick(16), d, z=3))
    a("skill2", tick(60))
    a("skill2_scream", tick(20))
    # Darius runs off, up and to the right, and turns round
    d.moves.append((stun_end, stun_end + 900, 54, -18))
    a("idle", stun_end + 800 - t, loop=True)
    # Certain Death: the kick sends the gem on tick 8; it stops on the first champion, Darius, and marks him her
    # prey; she flies to him (5 px a tick) and lands in a crimson blast that hits both and fears Garen, who was
    # walking in on the front row (35 px from her as she lands)
    start = t
    kick = start + tick(8)
    dx_, dy_ = d.pos(kick)
    arrive = kick + tick(math.hypot(dx_ - 8 - (x + 10), dy_ - gy) / 9.0)
    fx_at(small, "r_gem", kick, x + 10, gy - 14, until=arrive, x1=dx_ - 8, y1=dy_ - 14)
    mark = OnFoeFor(frames_of(small, "r_mark"), arrive, d, arrive + 6000, z=3)
    over.append(mark)
    a("ult", arrive - start)
    to = dx_ - 22                                    # 28 px from him (he stands 18 px further back)
    fly_end = t + tick((to - x) / 5.0)
    a("ult_fly", fly_end - t, loop=True, way=[(t, x), (fly_end, to)])
    x = to
    blast = t
    g.moves.append((blast - 1600, blast, -74, 0))
    fx_at(big, "r_boom", blast, x, gy, ground=True)
    for foe in (d, g):
        over.append(OnFoe(frames_of(small, "r_hit"), blast, foe, z=2))
        foe.flinches.append(blast)
    over.append(OnFoe(frames_of(small, "r_fear"), blast, g, z=3))
    g.moves.append((blast + 240, blast + 1500, 80, 4))           # off the right edge (66 px a second)
    on_her("hema", blast, until=blast + 6000, loop=True, z=-1)
    a("ult_land", tick(26))
    # Hemomania: a bite every 35 ticks (attack speed +70%), Snack Attack 2 s in finishes him
    d.death = bites(4, d, blast + 2000, 35) + 150
    mark.until = d.death                              # the buff view goes with him
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
        units = [(g.pos(tt)[1], g.frame(tt), g.pos(tt)), (d.pos(tt)[1], d.frame(tt), d.pos(tt))]
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
                            os.path.join(args.out, "league_briar_frames.png")))
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
