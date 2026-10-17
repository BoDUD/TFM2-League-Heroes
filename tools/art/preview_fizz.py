#!/usr/bin/env python3
"""Preview images for Fizz, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_fizz.py [--out docs/preview] [--frames-only]

  league_fizz_frames.png    every animation, frame by frame, 3x on the arena colour
  league_fizz_effects.png   every effect animation, 3x
  league_fizz_showcase.gif  a scripted fight with Darius, timed like the kit (60 ticks a second), League's combo: Fizz
                            runs in and throws Chum the Waters from 70 px - the fish flies 10 ticks, past both caster
                            windows, so it is the big shark: the fish on Darius's chest and the ring of teeth under
                            him for 2 s; Urchin Strike through him (the wake where he set off; Seastone Trident's
                            strike rides the hit, W being ready), Darius turns to him, two jabs; the shark bursts
                            where Darius stands and throws him up for 1 s; he lands and swings, Fizz has Playful held -
                            the swing breaks the 1-point shield, the hop goes 4 ticks later: the splash where he stood,
                            faded (invisible) for 38 ticks while he vaults onto Darius, the slam on tick 42 and Darius
                            slowed; a last jab and Darius falls. Fizz is drawn in front: the dash leaves him 15 px past
                            Darius's centre, inside his sprite. 3x
  league_fizz_combos.gif    the combos (tools/kit/fizz_combos.py), labelled: Urchin Strike through Darius and Playful
                            at once, no wait for a hit (Q E); a cut; the fish stuck on him and Playful at once, the
                            slam before the shark (R E); 3x
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from preview_annie import Held, OnFoe  # noqa: E402
from preview_ashe import Anim, tick  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_yone import OnFoeFor, Path  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_fizz")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_fizz_fx", "league_fizz_big")}
SPEED = 66.0                                  # move speed 1100: 66 px a second
ATK_DUR, ATK_CD, ATK_HIT = 24, 55, 9          # the jab: the action, ticks between jabs, its hit (a tick of carrier)
Q_DUR, Q_ST, Q_SPEED, Q_BACK = 22, 4, 4.5, 15  # Urchin Strike: the action, the dash's tick, px a tick, px past him
TOUCH = 13                                    # a dash touches a unit 13 px short of its centre (RushMoveToBack's hit)
E_ANIM, E_UP, E_LAND, E_SLAM, E_VAULT = 50, 6, 38, 42, 3.0   # Playful: the strip, vault, the end of the air, slam
E_RELEASE = 4                                 # the hop after the hit that breaks the shield (flag 2 ticks, pulse 3)
R_DUR, R_THROW, R_SPEED, R_WIDTH = 30, 7, 6.0, 10   # Chum the Waters: the action, the throw, px a tick, the fish's radius
R_T1, R_T2, R_WAIT, R_AIR = 3, 5, 120, 60     # the caster windows, the wait for the shark, the knock-up
DARIUS_HIT = 12                               # Darius's swing lands 12 ticks after it starts
FADED = 0.45                                  # his opacity while he is invisible


class Turning(Held):
    """Darius: faces left (towards Fizz) until `turn`, then right - Urchin Strike leaves Fizz behind him."""

    def __init__(self, sp, x, y):
        super().__init__(sp, x, y)
        self.turn = None

    def frame(self, t):
        self.mirrored = self.turn is None or t < self.turn
        return super().frame(t)


def showcase(out, z=3, step=40):
    fizz = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_fizz_fx"], fx["league_fizz_big"]
    W, H = 300, 120
    gy = 84                                   # the pivot row: the shark's fin rises 50 px over Darius's feet
    d = Turning(load(os.path.join(LEAGUE, "champions", "league_darius")), 180, gy)
    body, under, over = [], [], []
    hidden = []                               # (t0, t1): Playful's hop hides him
    t = 0.0
    x = 40

    def a(tag, dur=None, loop=False, way=None, flip=False):
        nonlocal t
        an = Path(frames_of(fizz, tag), t, x, gy, loop=loop, until=(t + dur) if dur else None, way=way or (),
                  flip=flip)
        body.append(an)
        t = an.until

    def run_to(to, flip=False):
        nonlocal x
        dur = abs(to - x) / SPEED * 1000.0
        a("run", dur, loop=True, way=[(t, x), (t + dur, to)], flip=flip)
        x = to

    def fx_at(sp, tag, at, px, py=gy, ground=False, until=None, x1=None, loop=False, flip=False):
        an = Anim(frames_of(sp, tag), at, px, py, z=-1 if ground else 1, loop=loop, until=until, x1=x1, flip=flip)
        (under if ground else over).append(an)
        return an

    def on_foe(sp, tag, at, z=2):
        over.append(OnFoe(frames_of(sp, tag), at, d, z=z))
        d.flinches.append(at)

    def jab(flip=True):
        hit = t + tick(ATK_HIT)
        on_foe(small, "hit", hit)
        a("attack", tick(ATK_DUR), flip=flip)
        return hit

    # he runs in to 70 px off Darius and throws Chum the Waters: the fish leaves on tick 7 and flies 6 px a tick until
    # it is within its radius of him - 10 ticks, past both windows (3 and 5): the big shark
    run_to(d.x - 70)
    r = t
    launch = r + tick(R_THROW)
    flight = (d.x - R_WIDTH - x) / R_SPEED
    stick = launch + tick(flight)
    k = 1 if flight <= R_T1 else 2 if flight <= R_T2 else 3
    fx_at(small, "r_fish", launch, x, gy, until=stick, x1=d.x - R_WIDTH, loop=True)
    a("ult", tick(R_DUR))
    # the fish on his chest and the ring of teeth under him until the shark (a 120-tick wait, a one-tick lob)
    shark = stick + tick(R_WAIT + 1)
    over.append(OnFoeFor(frames_of(small, "r_stuck"), stick, d, shark, z=3))
    under.append(OnFoeFor(frames_of(big, f"r_ring{k}"), stick, d, shark, z=-1))
    # Urchin Strike from 45 px: the wake where he set off, the dash from tick 4 at 4.5 px a tick through him to 15 px
    # past; the hit as he touches him (13 px short of his centre) takes Seastone Trident's strike (W ready)
    run_to(d.x - 45)
    q = t
    go = q + tick(Q_ST)
    to = d.x + Q_BACK
    fx_at(small, "q_dash", go, x, gy, ground=True)
    passing = go + tick((d.x - TOUCH - x) / Q_SPEED)
    on_foe(small, "q_hit", passing + tick(1))
    on_foe(small, "w_hit", passing + tick(1), z=3)
    a("skill", tick(Q_DUR), way=[(go, x), (go + tick((to - x) / Q_SPEED), to)])
    d.turn = go + tick((d.x - x) / Q_SPEED)          # he turns as Fizz passes his centre
    x = to
    # a jab from behind (turned to him), the next on the attack cooldown
    jab()
    a("idle", tick(ATK_CD - ATK_DUR), loop=True, flip=True)
    jab()
    # the shark bursts where he stands, the knock-up 2 ticks later (the bite's delay) for 1 s
    fx_at(big, f"r_shark{k}", shark, *d.pos(shark))
    up = shark + tick(2)
    d.hops.append((up, up + tick(R_AIR), 16))
    d.flinches.append(up)
    a("idle", up + tick(R_AIR) - t, loop=True, flip=True)
    # he lands and swings; Playful is held (a 3-tick cast, the 1-point shield) - the swing breaks it, the hop follows
    a("idle", tick(3), flip=True)
    swing = t + tick(4)
    d.attacks.append(swing)
    hop = swing + tick(DARIUS_HIT + E_RELEASE)
    a("idle", hop - t, loop=True, flip=True)
    fx_at(small, "e_up", hop, x, gy, ground=True)
    hidden.append((hop, hop + tick(E_LAND)))
    perch = d.x + TOUCH                               # the vault onto him, 3 px a tick from tick 6
    a("skill2", tick(E_ANIM), way=[(hop + tick(E_UP), x), (hop + tick(E_UP + (x - perch) / E_VAULT), perch)], flip=True)
    x = perch
    slam = hop + tick(E_SLAM)
    fx_at(big, "e_slam", slam, x, gy, ground=True)
    on_foe(small, "e_slow", slam)
    # a last jab: he falls
    last = jab()
    d.death = last + 150
    a("idle", 1400, loop=True, flip=True)
    end = t

    return film(out, W, H, end, d, body, under, over, hidden, z=z, step=step) + (f"shark {k}", round(flight, 1))


def film(out, W, H, end, d, body, under, over, hidden, labels=(), z=3, step=40):
    """Draw the clip: ground effects, Darius and Fizz (in front, faded while hidden), the other effects; labels =
    [(t0, t1, text)] in a corner."""
    font = ImageFont.load_default(size=8 * z) if labels else None

    def faded(f, tt):
        for t0, t1 in hidden:
            if t0 <= tt < t1:
                g = f.copy()
                g.putalpha(g.getchannel("A").point(lambda v: int(v * FADED)))
                return g
        return f

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
                units.append((0, faded(f, tt), an.pos(tt)))
                break
        for _, f, p in sorted(units, key=lambda u: -u[0]):         # Fizz in front: Urchin Strike leaves him 15 px past
            if f is not None:                                       # Darius's centre, inside his sprite
                place(img, f, *p)
        for an in sorted(over, key=lambda o: o.z):
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        img = img.resize((W * z, H * z), Image.NEAREST).convert("RGB")
        for t0, t1, text in labels:
            if t0 <= tt < t1:
                ImageDraw.Draw(img).text((4 * z, 2 * z), text, font=font, fill=(255, 236, 160),
                                         stroke_width=z // 2 + 1, stroke_fill=(24, 20, 16))
        frames.append(img)
        tt += step
    sample = frames[::6]                              # one palette for the whole clip
    strip = Image.new("RGB", (W * z, H * z * len(sample)))
    for i, f in enumerate(sample):
        strip.paste(f, (0, i * H * z))
    pal = strip.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q[0].save(T.long_path(out), save_all=True, append_images=q[1:], duration=step, loop=0, optimize=False)
    return len(frames), round(end / 1000.0, 1)


def combos(out, z=3, step=40):
    """The combos (tools/kit/fizz_combos.py), labelled: Urchin Strike through Darius, then Playful at once - no
    1 s wait for a hit - the hop back onto him and the slam (Q E); a cut; Chum the Waters sticks the fish on him and
    Playful goes at once, vaulting onto him, the slam before the shark bursts under him (R E)."""
    fizz = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_fizz_fx"], fx["league_fizz_big"]
    W, H = 300, 120
    gy = 84
    d = Turning(load(os.path.join(LEAGUE, "champions", "league_darius")), 180, gy)
    body, under, over, hidden, labels = [], [], [], [], []
    t = 0.0
    x = d.x - 45

    def a(tag, dur=None, loop=False, way=None, flip=False):
        nonlocal t
        an = Path(frames_of(fizz, tag), t, x, gy, loop=loop, until=(t + dur) if dur else None, way=way or (),
                  flip=flip)
        body.append(an)
        t = an.until

    def fx_at(sp, tag, at, px, py=gy, ground=False, until=None, x1=None, loop=False, flip=False):
        an = Anim(frames_of(sp, tag), at, px, py, z=-1 if ground else 1, loop=loop, until=until, x1=x1, flip=flip)
        (under if ground else over).append(an)
        return an

    def on_foe(sp, tag, at, z=2):
        over.append(OnFoe(frames_of(sp, tag), at, d, z=z))
        d.flinches.append(at)

    def hop(perch, flip):
        """Playful at once: the 3-tick cast, the splash, 38 ticks hidden, the vault from tick 6 at 3 px a tick onto
        perch, the slam on tick 42."""
        nonlocal x
        a("idle", tick(3), flip=flip)
        up = t
        fx_at(small, "e_up", up, x, gy, ground=True)
        hidden.append((up, up + tick(E_LAND)))
        a("skill2", tick(E_ANIM), way=[(up + tick(E_UP), x), (up + tick(E_UP + abs(x - perch) / E_VAULT), perch)],
          flip=flip)
        x = perch
        fx_at(big, "e_slam", up + tick(E_SLAM), x, gy, ground=True)
        on_foe(small, "e_slow", up + tick(E_SLAM))
        return up

    a("idle", 300, loop=True)
    # Q E: Urchin Strike through him (W rides the hit), E right after it
    q0 = t
    go = q0 + tick(Q_ST)
    to = d.x + Q_BACK
    fx_at(small, "q_dash", go, x, gy, ground=True)
    passing = go + tick((d.x - TOUCH - x) / Q_SPEED)
    on_foe(small, "q_hit", passing + tick(1))
    on_foe(small, "w_hit", passing + tick(1), z=3)
    a("skill", tick(Q_DUR), way=[(go, x), (go + tick((to - x) / Q_SPEED), to)])
    turn1 = go + tick((d.x - x) / Q_SPEED)            # he turns as Fizz passes his centre
    x = to
    e0 = t
    hop(d.x + TOUCH, flip=True)
    a("idle", 700, loop=True, flip=True)
    labels += [(q0, e0, "Q"), (e0, t, "Q E")]
    cut = t
    t += 240
    # R E: back in front of him (he turns to face her again), the fish from 70 px, E at once
    x = d.x - 70
    a("idle", 300, loop=True)
    r0 = t
    launch = r0 + tick(R_THROW)
    flight = (d.x - R_WIDTH - x) / R_SPEED
    stick = launch + tick(flight)
    k = 1 if flight <= R_T1 else 2 if flight <= R_T2 else 3
    fx_at(small, "r_fish", launch, x, gy, until=stick, x1=d.x - R_WIDTH, loop=True)
    shark = stick + tick(R_WAIT + 1)
    over.append(OnFoeFor(frames_of(small, "r_stuck"), stick, d, shark, z=3))
    under.append(OnFoeFor(frames_of(big, f"r_ring{k}"), stick, d, shark, z=-1))
    a("ult", tick(R_DUR))
    e1 = t
    hop(d.x - TOUCH, flip=False)
    a("idle", shark - t, loop=True)
    fx_at(big, f"r_shark{k}", shark, *d.pos(shark))
    d.hops.append((shark + tick(2), shark + tick(2 + R_AIR), 16))
    d.flinches.append(shark + tick(2))
    d.death = shark + tick(2 + R_AIR) + 100
    a("idle", tick(R_AIR) + 1000, loop=True)
    labels += [(r0, e1, "R"), (e1, t, "R E")]
    blank = [(cut, cut + 240)]

    class Cut:
        """Darius off stage during the cut, turned back to face her for the second scene."""
        def frame(self, tt):
            if any(a0 <= tt < a1 for a0, a1 in blank):
                return None
            d.turn = turn1 if tt < cut else None
            return d.frame(tt)

        def pos(self, tt):
            return d.pos(tt)

    return film(out, W, H, t, Cut(), body, under, over, hidden, labels=labels, z=z, step=step)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    ap.add_argument("--frames-only", action="store_true", help="only the frames sheet (before the effects exist)")
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    s = load(CHAMP)
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_fizz_frames.png")))
    if args.frames_only:
        return
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[12:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_fizz_effects.png")))
    print("showcase frames/seconds/shark/flight ticks", showcase(os.path.join(args.out, "league_fizz_showcase.gif")))
    print("combos frames/seconds", combos(os.path.join(args.out, "league_fizz_combos.gif")))


if __name__ == "__main__":
    main()
