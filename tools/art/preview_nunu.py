#!/usr/bin/env python3
"""Preview images for Nunu & Willump, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_nunu.py [--out docs/preview] [--only frames|effects|showcase]

  league_nunu_frames.png    every animation's dense frames (hd_, PPU 1.37, as league.dll shows them)
  league_nunu_effects.png   every effect animation, 3x
  league_nunu_showcase.gif  a scripted gank on Darius, timed like the kit (tools/kit/build_nunu.py, 60 ticks a second):
                            Biggest Snowball Ever! - Willump packs the snowball, rolls it at him (the snow kicked up),
                            it bursts big and knocks him up; at once (W -> E) the Snowball Barrage - six snowballs, the
                            snowflake mark over him, the ice bursting up and the shackles; the root opens the quick
                            channel (E -> R): Absolute Zero - the blizzard ring under them, the ice shell, his frost,
                            the burst; then (R -> Q) Willump's bite with the Freljord's wind under him; Darius falls; 3x.
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
from build_nunu import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_nunu")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_nunu_fx", "league_nunu_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")


class Them(Me):
    """preview_pyke's Me on whole game pixels (the roll moves them between them)."""

    def pos(self, t):
        x, y = super().pos(t)
        return int(round(x)), int(round(y))


class Nunu(Clip):
    """preview_gnar's clip with their own dense frames."""

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "nunu", z))
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
        """A picture on the ground under him (under the units)."""
        self.under.append(OnFoe(frames_of(sheet or self.small, tag), when, self.d, until=until))

    def at(self, tag, when, x, y, sheet=None, under=False):
        """A picture left where it was played (a not-following view: the snow kicked up, a burst)."""
        (self.under if under else self.over).append(Anim(frames_of(sheet or self.small, tag), when, x, y))


def px_ms(speed):
    """A speed (distance units a tick) in game px a ms."""
    return speed / 1000.0 * 60 / 1000


def showcase(out, z=3):
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_nunu_fx"], fx["league_nunu_big"]
    W, H = 280, 140
    gy = 116
    x0 = 70
    far = x0 + 96                                       # in the snowball's reach (70 game px), out of a swipe's
    d = Foe(load(DARIUS), far, gy)
    me = Them(x0, gy)
    c = Nunu(load(CHAMP), d, me, small, big)
    c.wait(400)

    # Biggest Snowball Ever!: packing it, then rolling at him (the snow kicked up at the start)
    t = c.t
    c.a("skill", tick(P["w_in"]))
    roll0 = t + tick(P["w_in"] - 1)
    stop = far - 30                                     # Willump's place when the ball (on his image right) hits
    roll1 = roll0 + (stop - x0) / px_ms(P["w_speed"])
    c.at("w_dust", roll0, x0, gy, under=True)
    c.t = roll0
    c.a("skill_roll", roll1 - roll0, loop=True)
    me.moves.append((roll0, roll1, x0, stop))
    big_ball = roll1 - roll0 >= tick(P["w_g1"])         # rolled long enough to grow (w1)
    c.a("skill_hit", tick(P["w_end"]))
    c.at("w_big" if big_ball else "w_burst", roll1, stop + 16, gy, sheet=big)
    c.on("w_hit", roll1)
    up = tick(P["w_up"])
    d.hops.append((roll1, roll1 + up, 14))
    d.flinches.append(roll1)
    # W -> E: the barrage at once, six snowballs, the mark over him, then the root
    t = c.t
    c.a("skill2", tick(P["e_dur"]))
    shot_y = gy - 11 + P["e_y"] / 1000.0
    for k in range(P["e_n"]):
        rel = t + tick(P["e_rel"] + k * P["e_per"] - 1)
        land = rel + (far - stop - 10) / px_ms(P["e_speed"])
        c.fly("e_ball", rel, land, stop + 10, far - 4, shot_y)
        c.on("e_hit", land)
        c.d.flinches.append(land)
        if k == 0:
            c.on_ground("e_slow", land, until=land + tick(P["e_slow_t"]))
            c.on("e_mark", land, until=t + tick(P["e_t"]))
    root = t + tick(P["e_t"])
    c.on("e_root_hit", root)
    c.on("e_root", root, until=root + tick(P["e_root"]))
    # E -> R: the root opens the quick channel - the blizzard round them, the shell, his frost, the burst
    c.wait(max(0, int(root) - c.t))
    t = c.t
    ch = tick(P["r_tf"])
    c.a("ult", ch, loop=True)
    c.on_me("r_storm", t, sheet=big, until=t + ch, under=True)
    c.on_me("r_shield", t, until=t + ch)
    c.on("r_slow", t + tick(P["r_pp"]), until=t + ch)
    c.a("ult_end", tick(P["r_end"]))
    c.on_me("r_burst", t + ch, sheet=big)
    c.on("r_hit", t + ch)
    c.d.flinches.append(t + ch)
    # R -> Q: Willump's bite, the Freljord's call under him
    c.wait(tick(P["r_end"]) // 2)
    t = c.t
    c.a("attack_bite", tick(P["b_dur"]))
    bite = t + tick(P["b_hit"] - 1)
    c.on("q_hit", bite)
    c.d.flinches.append(bite)
    c.on_me("p_on", bite, until=bite + tick(P["p_t"]) // 2, under=True)
    d.death = bite + 300
    end = d.death + 1600
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_nunu_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[12:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_nunu_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_nunu_showcase.gif")))


if __name__ == "__main__":
    main()
