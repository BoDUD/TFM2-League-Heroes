#!/usr/bin/env python3
"""Preview images for Shaco, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_shaco.py [--out docs/preview]

  league_shaco_frames.png     every animation, frame by frame, 3x on the arena colour
  league_shaco_effects.png    every effect animation (the clone's too), 3x
  league_shaco_showcase.gif   a scripted fight against Darius and Garen, timed like the kit: he runs in and stabs
                              Darius; Two-Shiv Poison: the next attack throws the green shiv; Deceive: a puff where
                              he stood, he vanishes (drawn faded) and reappears behind Darius in a smaller puff, his
                              backstab crits (the red X); Garen walks up and Jack In The Box lands at his feet,
                              pops, fears him (the grinning swirl) and shoots him as he flees; Hallucinate: a puff,
                              Shaco faded again, his violet-lined clone appears behind Darius and strikes with every
                              stab of his; Darius falls and the clone blows up where he fell - the blast burns Garen,
                              who had come back, and three mini boxes pop, fear him again and shoot; 3x
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

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_shaco")
FX = os.path.join(LEAGUE, "effects", "league_shaco_fx")
BIG = os.path.join(LEAGUE, "effects", "league_shaco_big")
CLONE = os.path.join(LEAGUE, "effects", "league_shaco_clone")
FADED = 0.45                                          # his opacity while he is invisible
STAB = 52                                             # the attack's cooldown, ticks


class Fleer(Held):
    """A foe that can also flee to the right (feared: unmirrored run frames) by dx px between t0 and t1."""

    def __init__(self, sp, x, y):
        super().__init__(sp, x, y)
        self.flees = []
        self.walks_in = []                            # (t0, t1, dx): walking left toward the fight

    def pos(self, t):
        x, y = super().pos(t)
        for t0, t1, dx in self.flees + self.walks_in:
            if t >= t0:
                x += int(round(dx * min(1.0, (t - t0) / (t1 - t0))))
        return x, y

    def frame(self, t):
        if self.death is not None and t >= self.death:
            return super().frame(t)
        for t0, t1, _ in self.flees:
            if t0 <= t < t1:
                return self.pick(self.run, (t - t0) % sum(ms for _, ms in self.run))
        for t0, t1, _ in self.walks_in:
            if t0 <= t < t1:
                return self.flip(self.pick(self.run, (t - t0) % sum(ms for _, ms in self.run)))
        return super().frame(t)


def faded(f):
    g = f.copy()
    g.putalpha(g.getchannel("A").point(lambda v: int(v * FADED)))
    return g


def showcase(out, z=3, step=40):
    sh = load(CHAMP)
    fx, big, cl = load(FX), load(BIG), load(CLONE)
    W, H = 320, 130
    gy = 88                                            # his pivot row: the hat's crown stands 34 px over it
    x = 70                                             # where he stands after running in
    d = Fleer(load(os.path.join(LEAGUE, "champions", "league_darius")), 104, gy)
    g = Fleer(load(os.path.join(LEAGUE, "champions", "league_garen")), 340, gy - 6)     # off the edge, a row behind
    body, under, over = [], [], []
    hidden = []                                        # (t0, t1): invisible
    t = 0.0
    face_left = [False]

    def a(tag, dur=None, loop=False, at=None, to=None):
        nonlocal t
        an = Anim(frames_of(sh, tag), t, at if at is not None else x, gy, loop=loop,
                  until=(t + dur) if dur else None, x1=to, flip=face_left[0])
        body.append(an)
        t = an.until

    def idle_to(at):
        if at > t:
            a("idle", at - t, loop=True)

    def mine(sp, tag, at, px=None, ground=False):
        """A CasterViewEffect where he is when it plays (not following him)."""
        an = Anim(frames_of(sp, tag), at, x if px is None else px, gy, flip=face_left[0])
        (under if ground else over).append(an)
        return an

    def on(sp, tag, at, foe, z=2):
        an = OnFoe(frames_of(sp, tag), at, foe, z=z)
        (under if z < 0 else over).append(an)
        return an

    clone = {"on": False, "strikes": []}

    def stab(foe):
        """The dagger stab: the hit on tick 8 of the attack; the clone strikes with it."""
        start = t
        hit = start + tick(8)
        on(fx, "hit", hit, foe)
        foe.flinches.append(hit)
        if clone["on"]:
            clone["strikes"].append(hit + tick(2))
        a("attack", tick(STAB))
        return hit

    # he runs in (move speed 1100: 66 px a second) to 34 px from Darius
    a("run", 900, loop=True, at=12, to=x)
    stab(d)
    # Two-Shiv Poison (E ready): attack_e, the shiv leaves on tick 11 at 6 px a tick, 4 px over the pivot
    e0 = t
    rel = e0 + tick(11)
    dx_, dy_ = d.pos(rel)
    arrive = rel + tick(max(1.0, (dx_ - x - 6) / 6.0))
    over.append(Anim(frames_of(fx, "e_shiv"), rel, x + 6, gy - 4, loop=True, until=arrive, x1=dx_, y1=dy_ - 4))
    on(fx, "e_hit", arrive, d)
    d.flinches.append(arrive)
    a("attack_e", tick(STAB))
    # Deceive: the puff and the vanish on tick 7, the rush 15 px a tick to 15 px past Darius, the second puff on
    # tick 11; then the backstab (attack_q, the crit on tick 9)
    q0 = t
    vanish = q0 + tick(7)
    mine(fx, "q_vanish", vanish, ground=False)
    hidden.append((vanish, vanish + tick(90)))
    a("skill", tick(18))
    land_x = d.x + 15
    x = land_x
    face_left[0] = True
    mine(fx, "q_appear", q0 + tick(11))
    body[-1].x1 = body[-1].x                          # the strip itself stays; he is drawn at the landing below
    body[-1].pos = lambda tt, a0=70, a1=land_x, t1=vanish: (a0 if tt < t1 else a1, gy)
    b0 = t
    crit = b0 + tick(9)
    on(fx, "q_hit", crit, d)
    d.flinches.append(crit)
    a("attack_q", tick(24))
    idle_to(b0 + tick(STAB))
    # Garen walks up toward the fight
    g.walks_in.append((1800, 4100, 200 - g.x))
    stab(d)
    # Jack In The Box at Garen (he turns to him): the toss on tick 8, the box lands 12 ticks later, pops 10 ticks after
    face_left[0] = False
    w0 = t
    toss = w0 + tick(8)
    lands = toss + tick(12)
    bx, by = g.pos(lands)
    over.append(Anim(frames_of(fx, "w_throw"), toss, x + 6, gy - 10, loop=True, until=lands, x1=bx, y1=by - 4))
    under.append(Anim(frames_of(big, "w_land"), lands, bx, by))
    pop = lands + tick(10)
    under.append(Anim(frames_of(big, "w_box"), pop, bx, by))
    on(fx, "fear", pop, g)
    g.flees.append((pop, pop + tick(60), 48))
    on(fx, "shot_hit", pop + tick(30), g)              # the shot while he is still within 35 px
    a("skill2", tick(20))
    face_left[0] = True
    idle_to(w0 + tick(STAB))
    stab(d)
    # Hallucinate on Darius: the puff on tick 6, faded for 60 ticks, the clone 12 ticks later behind Darius
    r0 = t
    cast = r0 + tick(6)
    mine(fx, "r_poof", cast)
    hidden.append((cast, cast + tick(60)))
    a("ult", tick(24))
    appear = cast + tick(12)
    on(cl, "clone_in", appear, d, z=-1)
    clone["on"] = True
    clone["from"] = appear + 300
    idle_to(r0 + tick(STAB))
    # Garen comes back after his fear
    g.walks_in.append((pop + tick(60) + 300, pop + tick(60) + 1900, 130 - (200 + 48)))
    stab(d)
    idle_to(t + 200)
    stab(d)
    idle_to(t + 150)
    death = stab(d)
    d.death = death
    clone["on"] = False
    # the clone blows up where Darius fell (the lob lands 6 ticks after the last run): the blast, the burn on Garen,
    # three mini boxes that fear and shoot
    boom = death + tick(8)
    bx, by = d.pos(boom)
    under.append(Anim(frames_of(big, "r_boom"), boom, bx, by))
    under.append(Anim(frames_of(big, "r_mini"), boom, bx, by))
    on(fx, "r_burn", boom + tick(1), g)
    g.flinches.append(boom + tick(1))
    on(fx, "fear", boom + tick(2), g)
    g.flees.append((boom + tick(2), boom + tick(47), 36))
    on(fx, "shot_hit", boom + tick(32), g)
    idle_to(boom + 2600)
    end = t

    # the clone: in, idle, a strike with every stab while it lives, gone with the blast
    strikes = sorted(clone["strikes"])
    k = clone["from"]
    for s in strikes + [boom]:
        if s > k:
            under.append(Anim(frames_of(cl, "clone_idle"), k, 0, 0, loop=True, until=s))
            under[-1].pos = lambda tt, f=d: f.pos(tt)
        if s == boom:
            break
        under.append(Anim(frames_of(cl, "clone_attack"), s, 0, 0))
        under[-1].pos = lambda tt, f=d: f.pos(tt)
        k = s + sum(ms for _, ms in frames_of(cl, "clone_attack"))
        over.append(OnFoe(frames_of(fx, "bs_hit"), s + tick(7), d, z=2))      # the strike's backstab slash

    def place(img, f, px, py):
        img.alpha_composite(f, (px - f.width // 2, py - f.height // 2))

    frames, tt = [], 0.0
    order = sorted((d, g), key=lambda f: f.y)          # the one further back first
    while tt < end:
        img = Image.new("RGBA", (W, H), ARENA)
        for an in under:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        for foe in order:
            place(img, foe.frame(tt), *foe.pos(tt))
        for an in body:
            f = an.frame(tt)
            if f is not None:
                if any(h0 <= tt < h1 for h0, h1 in hidden):
                    f = faded(f)
                place(img, f, *an.pos(tt))
                break
        for an in over:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        frames.append(img.resize((W * z, H * z), Image.NEAREST).convert("RGB"))
        tt += step
    sample = frames[::6]                               # one palette for the whole clip
    strip = Image.new("RGB", (W * z, H * z * len(sample)))
    for i, f in enumerate(sample):
        strip.paste(f, (0, i * H * z))
    pal = strip.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q[0].save(T.long_path(out), save_all=True, append_images=q[1:], duration=step, loop=0)
    return len(frames), round(end / 1000.0, 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    s = load(CHAMP)
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags],
                            os.path.join(args.out, "league_shaco_frames.png")))
    sp, bp, cp = load(FX), load(BIG), load(CLONE)
    print("effects", contact([(sp, t["name"], t["name"]) for t in sp.tags] +
                             [(bp, t["name"], t["name"]) for t in bp.tags] +
                             [(cp, t["name"], t["name"]) for t in cp.tags],
                             os.path.join(args.out, "league_shaco_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_shaco_showcase.gif")))


if __name__ == "__main__":
    main()
