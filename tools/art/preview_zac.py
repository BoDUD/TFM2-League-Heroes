#!/usr/bin/env python3
"""Preview images for Zac, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_zac.py [--out docs/preview] [--only frames|effects|showcase]

  league_zac_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_zac_effects.png   every effect animation, 3x
  league_zac_showcase.gif  a scripted gank on Darius, timed like the kit (tools/kit/build_zac.py, 60 ticks a second):
                           Elastic Slingshot - the arms planted, the pull, the fling onto him, the landing's splash and
                           his knock-up; at once (E -> W) Unstable Matter bursts round Zac and a blob flies off; the
                           knock-up calls Stretching Strikes (E -> Q): the rubber fist, the goo holding him, the pull
                           and the slam (his second knock-up); the slam starts Let's Bounce! (Q -> R): four bounces
                           onto him, each landing's splash, his knock-up and the slow, the last one bursting Unstable
                           Matter again (R -> W); a goo punch and Darius falls; Zac walks over the blobs he shed
                           (Cell Division: each one absorbed heals him); 3x.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
from preview_ashe import Anim, tick  # noqa: E402
from preview_dense import dense, dense_rows  # noqa: E402
from preview_garen import T, contact, frames_of, load  # noqa: E402
from preview_gnar import Clip  # noqa: E402
from preview_kindred import fx_contact  # noqa: E402
from preview_leesin import Foe  # noqa: E402
from preview_pyke import Me, OnFoe  # noqa: E402
from build_zac import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_zac")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_zac_fx", "league_zac_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")


class Him(Me):
    """preview_pyke's Me on whole game pixels (the slingshot and the bounces move him between them)."""

    def pos(self, t):
        x, y = super().pos(t)
        return int(round(x)), int(round(y))


class Zac(Clip):
    """preview_gnar's clip with his own dense frames."""

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "zac", z))
        if dur and not loop and dur > sum(ms for _, ms in fr):     # the last frame held to the action's end
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an

    def fly(self, tag, t0, t1, x0, x1, y, sheet=None):
        """A projectile's picture flying from x0 to x1 (drawn flying right)."""
        self.over.append(Anim(frames_of(sheet or self.small, tag), t0, x0, y, loop=True, until=t1, x1=x1, y1=y,
                              flip=x1 < x0))

    def on_ground(self, tag, when, sheet=None, until=None):
        """A picture on the ground under Darius (under the units)."""
        self.under.append(OnFoe(frames_of(sheet or self.small, tag), when, self.d, until=until))

    def at(self, tag, when, x, y, sheet=None, under=False, until=None):
        """A picture left where it was played (a not-following view: a landing's splash, a lying blob)."""
        (self.under if under else self.over).append(Anim(frames_of(sheet or self.small, tag), when, x, y,
                                                         loop=until is not None, until=until))


def px_ms(speed):
    """A speed (distance units a tick) in game px a ms."""
    return speed / 1000.0 * 60 / 1000


def showcase(out, z=3):
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_zac_fx"], fx["league_zac_big"]
    W, H = 280, 140
    gy = 112
    x0 = 70
    far = x0 + 70                                       # in the slingshot's reach (75 game px)
    shot_y = gy - 11 + P["q_y"] / 1000.0                # the fist's height (the pivot 11 over the soles, y_offset)
    d = Foe(load(DARIUS), far, gy + 3)                 # a step nearer the camera: drawn over Zac's big body
    me = Him(x0, gy)
    c = Zac(load(CHAMP), d, me, small, big)
    c.wait(400)
    blobs = []                                          # [x, lying from, absorbed at]

    def shed(when, x):
        """Cell Division: a blob flies b_far toward Darius (the controller throws it a pulse later) and lies there."""
        thrown = when + tick(P["ctl_p"])
        lands = thrown + tick(P["b_fly"])
        c.fly("b_fly", thrown, lands, x, x + P["b_far"] / 1000.0, gy - 6)
        blobs.append([x + P["b_far"] / 1000.0, lands, None])

    def burst(when):
        """Unstable Matter round him (over the units: under them his own body hid it), its hit on Darius."""
        c.on_me("w_burst", when, sheet=big)
        c.on("w_hit", when)
        c.d.flinches.append(when)

    # Elastic Slingshot: the arms planted and the pull, the fling onto him, the landing
    t = c.t
    fly0 = t + tick(P["e_wind"] - 1)
    c.a("skill2", fly0 - t)
    land_x = far - 22                                   # within the landing's knock-up (26 game px)
    land = fly0 + (land_x - x0) / px_ms(P["e_speed"])
    c.a("skill2_fly", land - fly0, loop=True)
    me.moves.append((fly0, land, x0, land_x))
    c.at("e_land", land, land_x, gy, sheet=big, under=True)
    c.on("e_hit", land)
    d.hops.append((land, land + tick(P["e_up"]), 12))
    d.flinches.append(land)
    shed(land, land_x)
    burst(land + tick(P["e_w_at"]))                     # E -> W
    # E -> Q: the knock-up calls Stretching Strikes a controller pulse later, over the landing pose
    q0 = land + tick(P["ctl_p"])
    c.a("skill2_land", q0 - land)
    c.a("skill", tick(P["q_dur"]))
    rel = q0 + tick(P["q_rel"] - 1)
    hit = rel + (far - 4 - land_x - 8) / px_ms(P["q_speed"])
    c.fly("q_fist", rel, hit, land_x + 8, far - 4, shot_y)
    c.on("q_hit", hit)
    c.on("q_held", hit, until=hit + tick(P["q_hold"] + P["q_drag"]))
    c.on_ground("slow", hit, until=hit + tick(P["q_slow_t"]))
    d.flinches.append(hit)
    pull = hit + tick(P["q_hold"])
    slam0 = pull + tick(P["q_drag"])
    d.slides.append((pull, slam0, -6))                  # flung to him
    c.wait(slam0 - c.t)
    slam = slam0 + tick(P["q_slam_at"])
    r0 = slam + tick(P["ctl_p"])                        # Q -> R a controller pulse after the slam lands
    c.a("skill_slam", r0 - slam0)
    c.at("q_slam", slam, land_x, gy, sheet=big)
    c.on("q_hit", slam)
    d.hops.append((slam, slam + tick(P["q_up"]), 14))
    d.flinches.append(slam)
    # Q -> R: Let's Bounce! - four bounces onto him, the last one bursting W (R -> W)
    x = land_x
    for k in range(P["r_n"]):
        b0 = r0 + tick(k * P["r_gap"])
        c.t = b0
        c.a("ult", tick(P["r_air"]))
        down = b0 + tick(P["r_air"])
        if k == 0:                                      # onto him: within reach of the first blob
            me.moves.append((b0 + tick(P["r_move_at"]), down, x, far - 16))
            x = far - 16
        c.a("ult_land", tick(P["r_land"]))
        c.at("r_land", down, x, gy, sheet=big, under=True)
        c.on("r_hit", down)
        c.on_ground("slow", down, until=down + tick(P["r_slow_t"]))
        d.hops.append((down, down + tick(P["r_up"]), 9))
        d.flinches.append(down)
        if k == 2:
            shed(down, x)                               # (b_gap 40 ticks: the 1st and 3rd landings shed, not the 2nd)
        if k == P["r_n"] - 1:
            burst(down + tick(1))
    # one more goo punch: he falls
    t = c.t
    c.a("attack", tick(P["atk_dur"]))
    blow = t + tick(P["a_hit"] - 1)
    c.on("a_hit", blow)
    d.flinches.append(blow)
    d.death = blow + 250
    # Darius falls; Zac walks over the blobs he shed and absorbs them
    c.wait(700)
    walk0 = c.t
    to = max(b[0] for b in blobs) + 2
    walk1 = walk0 + (to - x) / px_ms(P["ms"])
    c.a("run", walk1 - walk0, loop=True)
    me.moves.append((walk0, walk1, x, to))
    for b in blobs:                                     # absorbed the first moment he is within b_catch of it
        tt = b[1]
        while tt < walk1 and abs(me.pos(tt)[0] - b[0]) > P["b_catch"] / 1000.0:
            tt += 10
        b[2] = tt if tt < walk1 else None
    for bx, lies, gone in blobs:
        c.at("b_lie", lies, bx, gy, until=gone or lies + tick(P["b_lie"]))
        if gone:
            c.on_me("b_pick", gone)
    end = c.t + 1400
    c.wait(end - c.t)
    return c.render(out, W, H, end, z)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    ap.add_argument("--only", choices=["frames", "effects", "showcase"])
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    if args.only in (None, "frames"):
        s = load(CHAMP)
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_zac_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[11:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_zac_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_zac_showcase.gif")))


if __name__ == "__main__":
    main()
