#!/usr/bin/env python3
"""Preview images for LeBlanc, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_leblanc.py [--out docs/preview]

  league_leblanc_frames.png     every animation, frame by frame, 3x on the arena colour
  league_leblanc_effects.png    every effect animation, 3x
  league_leblanc_showcase.gif   a scripted fight against Darius and Garen, timed like the kit: she runs in and her
                                staff sends an orb at Darius; Sigil of Malice: the eye-shaped sigil flies and marks him
                                (the sigil glowing on his chest), and the combo goes on into Distortion: the magic
                                circle opens where she stood, she dashes onto him trailing light, the landing blast
                                bursts the sigil (the shattering sigil); 1.25 s after the cast she blinks back (the light
                                column where she was, the column at the circle) and rises from her cape; Ethereal
                                Chains in her next attack: the chain flies, its links run back to her for 1.5 s and the
                                chains root him; Mimicry repeats the chain, brighter; Garen walks up and, with two
                                champions on her, Mirror Image: she turns invisible (drawn faded), hops away and her
                                clone stands where she was; her orbs finish Darius; 3x
"""
import argparse
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from preview_annie import OnFoe  # noqa: E402
from preview_ashe import Anim, tick  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_shaco import Fleer, faded  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_leblanc")
FX = os.path.join(LEAGUE, "effects", "league_leblanc_fx")
BIG = os.path.join(LEAGUE, "effects", "league_leblanc_big")
STRIKE = 90                                           # the attack's cooldown, ticks
REACH = 52                                            # her attack range, px


def showcase(out, z=3, step=40):
    lb = load(CHAMP)
    fx, big = load(FX), load(BIG)
    W, H = 340, 130
    gy = 92                                            # her pivot row: the diadem's spike stands 31 px over it
    x = 70                                             # where she stands after running in
    d = Fleer(load(os.path.join(LEAGUE, "champions", "league_darius")), x + REACH, gy)
    g = Fleer(load(os.path.join(LEAGUE, "champions", "league_garen")), 380, gy - 6)     # off the edge, a row behind
    body, under, over = [], [], []
    hidden = []                                        # (t0, t1): invisible
    t = 0.0

    def a(tag, dur=None, loop=False, at=None, to=None):
        nonlocal t
        an = Anim(frames_of(lb, tag), t, at if at is not None else x, gy, loop=loop,
                  until=(t + dur) if dur else None, x1=to)
        body.append(an)
        t = an.until

    def idle_to(at):
        if at > t:
            a("idle", at - t, loop=True)

    def mine(sp, tag, at, follow=True, ground=False, until=None, loop=False, where=None):
        """A CasterViewEffect: following her (her body animation's place), or where she is when it plays."""
        an = Anim(frames_of(sp, tag), at, *(where or (x, gy)), loop=loop, until=until)
        if follow:
            an.pos = lambda tt: next((b.pos(tt) for b in body if b.frame(tt) is not None), (x, gy))
        (under if ground else over).append(an)

    def on(sp, tag, at, foe, z=2, until=None, loop=False):
        an = OnFoe(frames_of(sp, tag), at, foe, z=z)
        if loop:
            an.loop, an.until = True, until
        (under if z < 0 else over).append(an)

    def fly(tag, at, x0, y0, foe, speed, sp=None, dy=0):
        """A projectile from (x0, y0) to the foe's pivot (+dy) at `speed` px a tick; returns its arrival."""
        fx_ = sp or fx
        fxx, fyy = foe.pos(at)
        dist = max(1.0, ((fxx - x0) ** 2 + (fyy + dy - y0) ** 2) ** 0.5)
        arrive = at + tick(dist / speed)
        over.append(Anim(frames_of(fx_, tag), at, x0, y0, loop=True, until=arrive, x1=fxx, y1=fyy + dy))
        return arrive

    def orb(foe):
        """The attack: the orb leaves the staff on tick 12, 4.5 px a tick; the hit where it lands."""
        start = t
        rel = start + tick(11)
        mine(fx, "a_cast", rel)
        hit = fly("a_orb", rel, x, gy - 1, foe, 4.5)
        on(fx, "a_hit", hit, foe)
        foe.flinches.append(hit)
        a("attack")
        idle_to(start + tick(STRIKE))
        return hit

    def mark(foe, at, until, tag="q_mark"):
        k = at
        while k < until:
            on(fx, tag, k, foe)
            k += tick(12)

    # she runs in (move speed 920: 55 px a second)
    a("run", 1000, loop=True, at=15, to=x)
    orb(d)
    # Sigil of Malice: the sigil leaves on tick 12 (3.5 px a tick, 1.5 px up), marks Darius for 210 ticks
    q0 = t
    rel = q0 + tick(11)
    mine(fx, "q_cast", rel)
    land = fly("q_orb", rel, x, gy - 1, d, 3.5)
    on(fx, "q_hit", land, d)
    d.flinches.append(land)
    a("skill")
    # the combo: 24 ticks after the release, Distortion: the circle where she stood, the dash (4 px a tick) onto him
    w0 = rel + tick(24)
    idle_to(w0)
    w_land_x = d.x - 22
    dash = tick((w_land_x - x) / 4.0)
    mine(big, "w_pad", w0 + tick(4), follow=False, ground=True, where=(x, gy))
    pad_until = w0 + tick(4) + sum(ms for _, ms in frames_of(big, "w_pad"))
    mine(fx, "w_trail", w0 + tick(4))
    body.append(Anim(frames_of(lb, "skill2")[:1], w0, x, gy, until=w0 + tick(4)))
    body.append(Anim(frames_of(lb, "skill2")[1:4], w0 + tick(4), x, gy, loop=True, until=w0 + tick(4) + dash,
                     x1=w_land_x))
    t = w0 + tick(4) + dash
    x0, x = x, w_land_x
    blast = t
    under.append(Anim(frames_of(big, "w_blast"), blast, x, gy))
    on(fx, "w_hit", blast, d)
    d.flinches.append(blast)
    on(big, "q_pop", blast + tick(2), d)                # her spell hit bursts the sigil
    mark(d, land, blast + tick(2))
    body.append(Anim(frames_of(lb, "skill2")[4:], t, x, gy))
    t += sum(ms for _, ms in frames_of(lb, "skill2")[4:])
    # the return 75 ticks after the cast: the column where she was, the column at the circle, rising from her cape
    back = w0 + tick(75)
    idle_to(back)
    over.append(Anim(frames_of(fx, "w_out"), back, x, gy))
    x = x0
    over.append(Anim(frames_of(fx, "w_in"), back, x, gy))
    a("skill2_back")
    assert pad_until <= back + 200, "the circle should last till the return"
    # Ethereal Chains in the next attack: the throw on tick 12, the chain 3 px a tick, links back for 90 ticks, the root
    e0 = t
    throw = e0 + tick(12)
    mine(fx, "e_cast", throw)
    hit = fly("e_chain", throw, x, gy - 2, d, 3.0)
    on(fx, "e_hit", hit, d)
    d.flinches.append(hit)
    for k in range(7):
        s = hit + tick(1 + 12 * k)
        dx, _ = d.pos(s)
        over.append(Anim(frames_of(fx, "e_tether"), s, dx - 6, gy - 2, loop=True, until=s + tick((dx - x) / 1.8),
                         x1=x + 6, y1=gy - 2))
    a("e")
    root = hit + tick(90)
    idle_to(root)
    on(fx, "e_root", root, d, z=-1)
    d.flinches.append(root)
    # Mimicry: the last spell was the chain - R throws it again, brighter (the ult strip is Q's)
    r0 = t
    rthrow = r0 + tick(12)
    mine(fx, "re_cast", rthrow)
    rhit = fly("re_chain", rthrow, x, gy - 2, d, 3.0)
    on(fx, "re_hit", rhit, d)
    d.flinches.append(rhit)
    for k in range(7):
        s = rhit + tick(1 + 12 * k)
        dx, _ = d.pos(s)
        over.append(Anim(frames_of(fx, "re_tether"), s, dx - 6, gy - 2, loop=True, until=s + tick((dx - x) / 1.8),
                         x1=x + 6, y1=gy - 2))
    a("ult")
    rroot = rhit + tick(90)
    # Garen walks up beside Darius meanwhile
    g.walks_in.append((r0, r0 + 2600, (x + 34) - g.x))
    idle_to(rroot)
    on(fx, "re_root", rroot, d, z=-1)
    d.flinches.append(rroot)
    idle_to(r0 + 2700)
    # Mirror Image: two champions on her at an attack - invisible 60 ticks, a 24-px hop back, the clone where she was
    p0 = t + tick(1)
    under.append(Anim(frames_of(big, "p_clone"), p0, x, gy))
    hidden.append((p0, p0 + tick(60)))
    hop = tick(4)
    body.append(Anim(frames_of(lb, "idle")[:1], t, x, gy, until=p0))
    body.append(Anim(frames_of(lb, "run")[:2], p0, x, gy, loop=True, until=p0 + hop, x1=x - 24))
    t = p0 + hop
    x -= 24
    idle_to(p0 + tick(62))
    orb(d)
    death = orb(d)
    d.death = death + 60
    orb(g)
    idle_to(t + 600)
    end = t

    def place(img, f, px, py):
        img.alpha_composite(f, (px - f.width // 2, py - f.height // 2))

    gaps = [tt for tt in range(0, int(end), step) if not any(an.frame(tt) is not None for an in body)]
    assert not gaps, f"LeBlanc missing at {gaps[:10]} ms"

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
                            os.path.join(args.out, "league_leblanc_frames.png")))
    sp, bp = load(FX), load(BIG)
    print("effects", contact([(sp, t["name"], t["name"]) for t in sp.tags] +
                             [(bp, t["name"], t["name"]) for t in bp.tags],
                             os.path.join(args.out, "league_leblanc_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_leblanc_showcase.gif")))


if __name__ == "__main__":
    main()
