#!/usr/bin/env python3
"""Preview images for Nocturne, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_nocturne.py [--out docs/preview]

  league_nocturne_frames.png     every animation, frame by frame, 3x on the arena colour
  league_nocturne_effects.png    every effect animation, 3x
  league_nocturne_showcase.gif   a scripted fight against Darius and Garen, timed like the kit: he glides in and strikes
                                 Darius (the slash in front of him); Duskbringer: the shadow blade flies through Darius
                                 and the dusk trail lies on the ground behind it, Darius trails dusk at his feet;
                                 Umbra Blades: the fourth attack cleaves round him; Unspeakable Horror: the claw grips
                                 Darius, the tether's links run back to Nocturne for 2 s with its pulses, the Shroud of
                                 Darkness rises round him and bursts when a blow lands on it, then Darius is feared (the
                                 nightmare eyes over his head) and flees, Nocturne gliding after him; Darius falls;
                                 Garen walks up and Paranoia: darkness bursts round Nocturne, he turns invisible (drawn
                                 faded) under the veil while the ult plays (the flight and the landing's burst), the
                                 dark mist rings Garen's head as long, he dives at Garen trailing shadow and lands with
                                 the crossing strike; 3x
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
CHAMP = os.path.join(LEAGUE, "champions", "league_nocturne")
FX = os.path.join(LEAGUE, "effects", "league_nocturne_fx")
BIG = os.path.join(LEAGUE, "effects", "league_nocturne_big")
STRIKE = 48                                           # the attack's cooldown, ticks


def fr(sp, tag):
    """The tag's frames, or [] while the effect is not drawn yet."""
    return frames_of(sp, tag) if any(t["name"] == tag for t in sp.tags) else []


def showcase(out, z=3, step=40):
    nc = load(CHAMP)
    fx, big = load(FX), load(BIG)
    W, H = 340, 130
    gy = 92                                            # his pivot row: the crest stands 28 px over it
    x = 70                                             # where he stands after gliding in
    d = Fleer(load(os.path.join(LEAGUE, "champions", "league_darius")), 104, gy)
    g = Fleer(load(os.path.join(LEAGUE, "champions", "league_garen")), 360, gy - 6)     # off the edge, a row behind
    body, under, over = [], [], []
    hidden = []                                        # (t0, t1): invisible
    t = 0.0

    def a(tag, dur=None, loop=False, at=None, to=None):
        nonlocal t
        an = Anim(frames_of(nc, tag), t, at if at is not None else x, gy, loop=loop,
                  until=(t + dur) if dur else None, x1=to)
        body.append(an)
        t = an.until

    def idle_to(at):
        if at > t:
            a("idle", at - t, loop=True)

    def mine(sp, tag, at, follow=True, ground=False, until=None, loop=False):
        """A CasterViewEffect: following him (his body animation's place), or where he is when it plays."""
        frames = fr(sp, tag)
        if not frames:
            return
        an = Anim(frames, at, x, gy, loop=loop, until=until)
        if follow:
            an.pos = lambda tt: next((b.pos(tt) for b in body if b.frame(tt) is not None), (x, gy))
        (under if ground else over).append(an)

    def on(sp, tag, at, foe, z=2, until=None, loop=False):
        frames = fr(sp, tag)
        if not frames:
            return
        an = OnFoe(frames, at, foe, z=z)
        if loop:
            an.loop, an.until = True, until
        (under if z < 0 else over).append(an)

    def strike(foe, tag="attack", hit_tick=8, hit_tag="hit"):
        start = t
        hit = start + tick(hit_tick + 1)
        on(fx, hit_tag, hit, foe)
        foe.flinches.append(hit)
        a(tag)
        idle_to(start + tick(STRIKE))
        return hit

    # he glides in (move speed 1100: 66 px a second) to 34 px from Darius
    a("run", 900, loop=True, at=12, to=x)
    s0 = t
    mine(fx, "swing", s0)
    strike(d)
    # Duskbringer: the blade leaves on tick 10, 4.5 px a tick, 3 px over his pivot, 66 px; the trail lies 5 s
    q0 = t
    rel = q0 + tick(10)
    fly = tick(66 / 4.5)
    over.append(Anim(fr(fx, "q_blade"), rel, x + 4, gy - 3, loop=True, until=rel + fly, x1=x + 70, y1=gy - 3))
    if fr(big, "q_path"):
        under.append(Anim(fr(big, "q_path"), rel, x + 33, gy, loop=True, until=rel + 5000))
    passes = rel + tick((d.x - x) / 4.5)
    on(fx, "q_hit", passes, d)
    d.flinches.append(passes)
    on(fx, "q_dusk", passes, d, z=-1, until=passes + 5000, loop=True)
    a("skill", tick(22))
    idle_to(q0 + tick(STRIKE))
    # Garen starts walking toward the fight
    g.walks_in.append((2400, 6400, 230 - g.x))
    mine(fx, "swing", t)
    strike(d)
    mine(fx, "swing", t)
    strike(d)
    # the fourth attack: Umbra Blades, the ring round him, the hit on tick 9
    p0 = t
    mine(fx, "p_spin", p0)
    strike(d, "attack_p", 8, "p_hit")
    # Unspeakable Horror + Shroud of Darkness on tick 8: the grip, links from Darius every 12 ticks (1.6 px a tick),
    # 4 pulses, the shroud for 90 ticks (a blow lands on it on tick 30: the burst), the fear on tick 128 (80 ticks)
    e0 = t
    cast = e0 + tick(8)
    on(fx, "e_grip", cast, d)
    mine(fx, "w_shroud", cast, ground=True)
    mine(fx, "w_proc", cast + tick(30))
    for k in range(10):
        s = cast + tick(1 + 12 * k)
        dist = d.x - x - 6
        over.append(Anim(fr(fx, "e_chain"), s, d.x - 6, gy - 5, loop=True, until=s + tick(dist / 1.6), x1=x + 6,
                         y1=gy - 5))
    for k in range(4):
        on(fx, "e_tick", cast + tick(15 + 30 * k), d)
    a("skill2", tick(20))
    idle_to(e0 + tick(STRIKE))
    mine(fx, "swing", t)
    strike(d)
    fear = cast + tick(121)
    idle_to(fear)
    on(fx, "e_fear", fear, d, until=fear + tick(80), loop=True)
    d.flees.append((fear, fear + tick(80), 44))
    # he glides after him (E's passive: faster toward the feared)
    a("run", tick(60), loop=True, to=x + 40)
    x += 40
    idle_to(fear + tick(80))
    mine(fx, "swing", t)
    strike(d)
    p1 = t
    mine(fx, "p_spin", p1)
    death = strike(d, "attack_p", 8, "p_hit")
    d.death = death + 60
    # Paranoia at Garen: darkness on tick 8, invisible only while the ult plays (the flight, at most 32 ticks, and the
    # landing's 20-tick burst: 「魔腾不放大的时候也全队隐身」), the mist on Garen as long, the dive 3.5 px a tick
    idle_to(t + 300)
    r0 = t
    launch = r0 + tick(8)
    mine(fx, "r_veil", launch)
    if fr(big, "r_burst"):
        under.append(Anim(fr(big, "r_burst"), launch, x, gy))
    dark = fr(fx, "r_dark_in") + fr(fx, "r_dark") * 2 + fr(fx, "r_dark_out")
    if dark:
        over.append(OnFoe(dark, launch, g, z=2))
    gx, gyy = g.pos(launch)
    land_x = gx - 30
    flight = tick(max(1.0, (land_x - x) / 3.5))
    hidden.append((launch, launch + max(tick(32), flight + tick(20))))
    mine(fx, "r_trail", launch, until=launch + flight)
    body.append(Anim(frames_of(nc, "ult")[:2], r0, x, gy, loop=True, until=launch))
    fly = frames_of(nc, "ult")[2:]
    an = Anim(fly, launch, x, gy, loop=True, until=launch + flight, x1=land_x, y1=gyy)
    body.append(an)
    t = launch + flight
    x = land_x
    land = t
    on(big, "r_hit", land, g)
    g.flinches.append(land)
    a("ult_hit")
    idle_to(land + tick(STRIKE))
    for _ in range(3):
        mine(fx, "swing", t)
        strike(g)
    idle_to(t + 600)
    end = t

    def place(img, f, px, py):
        img.alpha_composite(f, (px - f.width // 2, py - f.height // 2))

    gaps = [tt for tt in range(0, int(end), step) if not any(an.frame(tt) is not None for an in body)]
    assert not gaps, f"Nocturne missing at {gaps[:10]} ms"

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
                            os.path.join(args.out, "league_nocturne_frames.png")))
    sp, bp = load(FX), load(BIG)
    print("effects", contact([(sp, t["name"], t["name"]) for t in sp.tags] +
                             [(bp, t["name"], t["name"]) for t in bp.tags],
                             os.path.join(args.out, "league_nocturne_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_nocturne_showcase.gif")))


if __name__ == "__main__":
    main()
