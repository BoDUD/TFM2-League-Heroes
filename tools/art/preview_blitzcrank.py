#!/usr/bin/env python3
"""Preview images for Blitzcrank, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_blitzcrank.py [--out docs/preview] [--frames-only]

  league_blitzcrank_frames.png    every animation, frame by frame, 3x on the arena colour
  league_blitzcrank_effects.png   every effect animation, 3x
  league_blitzcrank_showcase.gif  a scripted fight with Darius and Garen, timed like the kit (60 ticks a second): Blitzcrank
                                  walks in and throws Rocket Grab at Darius 69 px off - thrown on tick 11, the claw
                                  leaves his raised arm at 6 px a tick, its chain behind it, and stops 12 px short of
                                  him 9 ticks after the throw - stunned, the claw closes on him and brings him back
                                  along its line, the chain running back into the arm, until it is on the arm again
                                  (the hold) and Darius stands in front of him, in reach; Overdrive starts (the steam
                                  every second) and Power Fist throws Darius up for 1 s; a punch marks
                                  him and the bolt strikes a second later (Static Field's passive); Garen walks up -
                                  two champions on him: Mana Barrier's shield; Static Field: the charge, the field on
                                  tick 23, both hit and silenced (1 s); a last punch and Darius falls. 3x. Projectile
                                  pictures are turned to their flight like the game does; the claws go over the units
                                  and the chains under them, as in the kit.
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
from preview_yone import OnFoeFor, Path  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_blitzcrank")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_blitzcrank_fx", "league_blitzcrank_big")}
SPEED = 60.0                                  # move speed 1000: 60 px a second
ATK_DUR, ATK_HIT = 26, 8                      # the punch: the action, its hit
Q_DUR, Q_ST, Q_SPEED, Q_DRAG = 40, 11, 6.0, 1.5   # Rocket Grab: the action, the throw, px a tick out and dragging
Q_LIFT, Q_RANGE = 16.5, 78                    # the hook leaves 16.5 px over his pivot (y_offset -11500, his raised arm)
                                              # and slopes down to his pivot's height at the range's end
TOUCH = 12                                    # the hook stops 12 px short of a champion's centre
E_DUR, E_HIT, E_AIR = 32, 12, 60              # Power Fist: the action, the uppercut, the knock-up
RP_DELAY = 60                                 # Static Field's passive: the bolt a second after the punch
R_DUR, R_HIT, R_SILENCE = 35, 23, 60          # Static Field: the action, the field, the silence
Q_DOCK, Q_HOLD = 32, 8                        # the claw back on the arm (px along the line), the hold (ticks)
Q_STOP = 33                                   # the catch stops this far from him, in reach (the kit's q_stop)
WAYS_SHOWN = {"q_hc9", "q_hn9", "q_mc12", "q_mn12"}   # the 14 ways back differ only in where they start: one each


def turned(fr, dx, dy):
    """A projectile's frames turned to its direction, as the game draws them."""
    deg = math.degrees(math.atan2(dy, dx))
    if abs(deg) < 0.5:
        return fr
    return [(f.rotate(-deg, resample=Image.NEAREST, expand=True), ms) for f, ms in fr]


def showcase(out, z=3, step=40):
    bz = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_blitzcrank_fx"], fx["league_blitzcrank_big"]
    W, H = 300, 130
    gy = 92                                   # the pivot row: the field's ellipse reaches 36 px under it
    x = 32
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), 0, gy)
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), 330, gy - 14)    # off screen, walks in
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False, way=None):
        nonlocal t
        an = Path(frames_of(bz, tag), t, x, gy, loop=loop, until=(t + dur) if dur else None, way=way or ())
        body.append(an)
        t = an.until

    def run_to(to):
        nonlocal x
        dur = abs(to - x) / SPEED * 1000.0
        a("run", dur, loop=True, way=[(t, x), (t + dur, to)])
        x = to

    def on_foe(sp, tag, at, foe, z=2, until=None):
        if until is None:
            over.append(OnFoe(frames_of(sp, tag), at, foe, z=z))
        else:
            over.append(OnFoeFor(frames_of(sp, tag), at, foe, until, z=z))

    def punch(foe, passive=True):
        """The punch: the hit on tick 8; with Static Field's passive the mark and, a second later, the bolt."""
        hit = t + tick(ATK_HIT)
        on_foe(small, "hit", hit, foe)
        foe.flinches.append(hit)
        if passive:
            on_foe(small, "p_mark", hit, foe)
            bolt = hit + tick(RP_DELAY)
            on_foe(small, "p_bolt", bolt, foe, z=3)
            foe.flinches.append(bolt)
        a("attack", tick(ATK_DUR))
        return hit

    # he walks in; Darius stands 69 px ahead of where he stops
    run_to(96)
    d.x = x + 69
    # Rocket Grab, tick by tick as the kit runs it: thrown on tick 11 from 16.5 px over his pivot toward his pivot's
    # height Q_RANGE px ahead, 6 px along that line on every tick from the throw (that one too) - the claw on the
    # hook, its chain on the twin; it stops TOUCH px short of Darius h ticks after the throw (stunned). The twin lands
    # a tick later: the pull pose and the drag, 1.5 px a tick until the claw is back at Q_DOCK px along. 2 ticks after
    # the stop two projectiles leave along the same line (1.5 px a tick) with the way back the kit picks for h: the
    # closed claw with Darius and its chain; then the hold (the claw on the arm) for Q_HOLD ticks
    start = t
    throw = start + tick(Q_ST)
    full = math.hypot(Q_RANGE, Q_LIFT)
    ux, uy = Q_RANGE / full, Q_LIFT / full                            # the line's direction

    def on_line(px_along):
        return x + px_along * ux, gy - Q_LIFT + px_along * uy

    h = next(k for k in range(20) if Q_SPEED * (k + 1) * ux >= d.x - TOUCH - x)
    reach = Q_SPEED * (h + 1)                                         # where it stopped, px along
    hit = throw + tick(h)
    out_fr = {k: turned(frames_of(big, k), Q_RANGE, Q_LIFT) for k in ("q_hand", "q_twin")}
    over.append(Anim(out_fr["q_hand"], throw, *on_line(Q_SPEED), until=hit, x1=on_line(reach)[0], y1=on_line(reach)[1],
                     z=1))
    under.append(Anim(out_fr["q_twin"], throw, *on_line(Q_SPEED), until=hit + tick(1),
                      x1=on_line(reach + Q_SPEED)[0], y1=on_line(reach + Q_SPEED)[1], z=-1))
    drag = max(0, round((reach + TOUCH - Q_STOP) / Q_DRAG))           # ticks
    pull, back = hit + tick(1), hit + tick(2)
    held = back + tick(max(0, drag - 1))                              # the claw on the arm again
    life = int(reach // Q_DRAG)                                       # the way back's projectiles reach the stop
    for tag, layer, zz in ((f"q_hc{h}", over, 1), (f"q_hn{h}", under, -1)):
        layer.append(Anim(turned(frames_of(big, tag), Q_RANGE, Q_LIFT), back, *on_line(Q_DRAG), until=back + tick(life),
                          x1=on_line(Q_DRAG * (life + 1))[0], y1=on_line(Q_DRAG * (life + 1))[1], z=zz))
    a("skill", pull - t)                                              # the cast until the pull pose takes over
    a("q_pull", held - pull, loop=True)
    a("q_hold", tick(Q_HOLD), loop=True)
    on_foe(small, "q_grab", pull, d)
    d.holds.append((hit, hit + tick(40)))                             # the stun
    d.slides.append((pull, pull + tick(drag), -Q_DRAG * drag))
    a("idle", 150, loop=True)
    # Overdrive: his first action with Darius in reach starts it - the steam each second for 4 s - and Power Fist
    # throws him up on tick 12 for 1 s
    od = t
    for s in range(4):
        over.append(Anim(frames_of(small, "w_steam"), od + s * 1000.0, x, gy, z=3))
    up = t + tick(E_HIT)
    on_foe(small, "e_hit", up, d, z=3)
    d.hops.append((up, up + tick(E_AIR), 18))
    a("skill2", tick(E_DUR))
    a("idle", up + tick(E_AIR) - t + 60, loop=True)
    # a punch: the static mark, the bolt a second later
    punch(d)
    a("idle", 500, loop=True)
    # Garen walks up behind Darius: two champions on him, Mana Barrier's shield (it holds 10 s)
    g.walks.append((t - 1800, t, (x + 34) - g.x))
    shield = t + 100
    over.append(Anim(frames_of(small, "mb_on"), shield, x, gy, loop=True, until=shield + 3000, z=3))
    punch(d)
    a("idle", 300, loop=True)
    # Static Field: armed by the slot, it goes at once with them this close - the charge, the field on tick 23 round
    # him, both hit and silenced for 1 s; the passive is off until the cooldown ends
    r = t
    over.append(Anim(frames_of(big, "r_charge"), r, x, gy, z=3))
    field = r + tick(R_HIT)
    under.append(Anim(frames_of(big, "r_field"), field, x, gy, z=-1))
    for foe in (d, g):
        on_foe(small, "r_hit", field, foe)
        on_foe(small, "r_silence", field, foe, until=field + tick(R_SILENCE))
        foe.flinches.append(field)
    a("ult", tick(R_DUR))
    a("idle", 400, loop=True)
    last = punch(d, passive=False)
    d.death = last + 150
    a("idle", 1500, loop=True)
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
        units = [(gy - 14, g.frame(tt), g.pos(tt)), (gy, d.frame(tt), d.pos(tt))]
        for an in body:
            f = an.frame(tt)
            if f is not None:
                units.append((gy + 0.5, f, an.pos(tt)))
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
    return len(frames), round(end / 1000.0, 1), f"q_hc{h}", reach


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    ap.add_argument("--frames-only", action="store_true", help="only the frames sheet (before the effects exist)")
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    s = load(CHAMP)
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags],
                            os.path.join(args.out, "league_blitzcrank_frames.png")))
    if args.frames_only:
        return
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[18:]}:{t['name']}") for t in sp.tags
                 if t["name"][:4] not in ("q_hc", "q_hn", "q_mc", "q_mn") or t["name"] in WAYS_SHOWN]
    print("effects", contact(rows, os.path.join(args.out, "league_blitzcrank_effects.png")))
    print("showcase frames/seconds/return/px",
          showcase(os.path.join(args.out, "league_blitzcrank_showcase.gif")))


if __name__ == "__main__":
    main()
