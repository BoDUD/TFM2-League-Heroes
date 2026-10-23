#!/usr/bin/env python3
"""Preview images for Aurora, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_aurora.py [--out docs/preview] [--only frames|effects|showcase]

  league_aurora_frames.png    every animation's dense frames (hd_, PPU 2.25, as league.dll shows them)
  league_aurora_effects.png   every effect animation, 3x
  league_aurora_showcase.gif  a scripted fight against Darius in the mid lane, timed like the kit (tools/kit/build_aurora.py,
                              60 ticks a second): two spirit bolts (the spirit mark over his head); Twofold Hex - the hex
                              through him (the curse on his chest), its curse drawn back (the third hit exorcises his
                              spirit: the bunny spirit rising, her heal); Between Worlds - the leap onto him, the
                              shockwave and the realm under him, and at once The Weirding round her (the combo R -> E:
                              the window, the hit, the hop back); he falls; 3x.
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
from build_aurora import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_aurora")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_aurora_fx", "league_aurora_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")


class Her(Me):
    """preview_pyke's Me on whole game pixels (her leap and hops move her between them)."""

    def pos(self, t):
        x, y = super().pos(t)
        return int(round(x)), int(round(y))


class Aurora(Clip):
    """preview_gnar's clip with her own dense frames."""

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "aurora", z))
        if dur and not loop and dur > sum(ms for _, ms in fr):     # the last frame held to the action's end
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an

    def fly(self, tag, t0, t1, x0, x1, y, sheet=None):
        """A projectile's picture flying from x0 to x1 (drawn flying right; flying left the game turns it half round,
        which for a picture symmetric top to bottom is a mirror)."""
        self.over.append(Anim(frames_of(sheet or self.small, tag), t0, x0, y, loop=True, until=t1, x1=x1, y1=y,
                              flip=x1 < x0))

    def on_ground(self, tag, when, sheet=None, until=None):
        """A picture on the ground under him (under the units)."""
        self.under.append(OnFoe(frames_of(sheet or self.small, tag), when, self.d, until=until))


def px_ms(speed):
    """A projectile's speed (distance units a tick) in game px a ms."""
    return speed / 1000.0 * 60 / 1000


def showcase(out, z=3):
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_aurora_fx"], fx["league_aurora_big"]
    W, H = 260, 130
    gy = 108
    x0 = 92
    far = x0 + 52                                       # in her attack's reach (55 game px)
    shot_y = gy - 11 + P["a_y"] / 1000.0                # a projectile's height (the pivot 11 over the soles, y_offset)
    d = Foe(load(DARIUS), far, gy)
    me = Her(x0, gy)
    c = Aurora(load(CHAMP), d, me, small, big)
    c.wait(400)
    stacks = {"n": 0}

    def mark(when):
        """Spirit Abjuration: a champion hit counts; the third exorcises his spirit and heals her."""
        stacks["n"] += 1
        if stacks["n"] < 3:
            c.on("p_mark", when, until=when + tick(P["p_t"]))
            return
        stacks["n"] = 0
        c.on("p_spirit", when)
        c.on_me("p_heal", when + 200)

    # two spirit bolts
    for _ in range(2):
        t = c.t
        c.a("attack", tick(P["atk_dur"]))
        rel = t + tick(P["a_rel"] - 1)
        land = rel + (far - x0) / px_ms(P["a_speed"])
        c.fly("a_bolt", rel, land, x0 + 8, far - 4, shot_y)
        c.on("a_hit", land)
        c.d.flinches.append(land)
        mark(land)
        c.wait(tick(P["atk_cd"] - P["atk_dur"]) // 2)
    # Twofold Hex: the hex through him (the curse), then drawn back through him (the third hit: his spirit)
    t = c.t
    c.a("skill", tick(P["q_dur"]))
    rel = t + tick(P["q_rel"] - 1)
    out_end = x0 + 8 + P["q_len"] / 1000.0
    reach = rel + (out_end - x0 - 8) / px_ms(P["q_speed"])
    passed = rel + (far - x0 - 8) / px_ms(P["q_speed"])
    c.fly("q_out", rel, reach, x0 + 8, out_end, shot_y)
    c.on("q_hit", passed)
    c.on("q_curse", passed, until=passed + tick(P["q_hold"] + 30))
    c.d.flinches.append(passed)
    back0 = reach + tick(P["q_hold"])
    home = back0 + (out_end - x0) / px_ms(P["q_back_speed"])
    c.fly("q_back", back0, home, out_end, x0 + 4, shot_y)
    passed = back0 + (out_end - far) / px_ms(P["q_back_speed"])
    c.on("q_back_hit", passed)
    c.d.flinches.append(passed)
    mark(passed)
    c.wait(max(0, int(home) + 300 - c.t))
    # Between Worlds: the leap onto him, the shockwave, the realm; R -> E: The Weirding round her, the hop back
    t = c.t
    c.a("ult", tick(P["r_dur"]))
    leap0 = t + tick(P["r_rel"] - 1)
    land_x = far - 14
    leap1 = leap0 + (land_x - x0) / px_ms(P["r_speed"])
    me.moves.append((leap0, leap1, x0, land_x))
    c.on_me("r_shock", leap1, sheet=big, under=True)
    c.on("r_hit", leap1)
    c.on_ground("r_zone", leap1, sheet=big, until=leap1 + tick(P["r_t"]))
    c.on_ground("slow", leap1, until=leap1 + tick(P["r_t"]))
    c.d.flinches.append(leap1)
    weird = leap1 + tick(P["re_gap"])
    c.wait(max(0, int(weird) - c.t))
    c.a("skill2", tick(P["e_dur"]))
    c.on_me("e_burst", weird)
    c.on("e_hit", weird)
    c.d.flinches.append(weird)
    hop0 = weird + tick(2)
    hop1 = hop0 + tick(P["e_back_t"])
    back_x = land_x - P["e_back"] * P["e_back_t"] / 1000.0
    me.moves.append((hop0, hop1, land_x, back_x))
    d.death = weird + 400
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_aurora_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_aurora_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_aurora_showcase.gif")))


if __name__ == "__main__":
    main()
