#!/usr/bin/env python3
"""Preview images for Illaoi, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_illaoi.py [--out docs/preview] [--only frames|effects|showcase]

  league_illaoi_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them), the tentacle's two
                              sheets after them (hd_idle, PPU 1.5)
  league_illaoi_effects.png   every effect animation, 3x
  league_illaoi_showcase.gif  a scripted fight against Darius in the top lane, timed like the kit (tools/kit/build_illaoi.py,
                              60 ticks a second): two idol swings - the first grows a tentacle before her (its cracks)
                              and it lashes Darius on its period (her heal); Test of Spirit - the ghost tentacle tears his
                              spirit out (slowed) - and at once Harsh Lesson (the combo E -> W): she leaps onto him, the
                              Elder God's eye over his head and the tentacle lashes him; Leap of Faith - the crater, a
                              tentacle growing on him, her glyph ring and the tentacles striking faster; he falls; 3x.
"""
import argparse
import os
import sys

from PIL import Image

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
from build_illaoi import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_illaoi")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_illaoi_fx", "league_illaoi_big")}
TENT = {k: os.path.join(LEAGUE, "effects", f"league_illaoi_{k}") for k in ("tentacle", "lash")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")
T_PPU = 1.5


def tent_frames(sp, z):
    """The tentacle's hd_idle frames at zoom z (z / 1.5 of their sheet size), each with its 1x frame's size for
    preview_dense.put (centred where the 1x frame's centre is: the spot or the unit struck)."""
    out = []
    for (a, _), (b, ms) in zip(frames_of(sp, "idle"), frames_of(sp, "hd_idle")):
        k = z / T_PPU
        f = b.resize((max(1, round(b.width * k)), max(1, round(b.height * k))), Image.NEAREST)
        f.info["one"] = (a.width, a.height)
        out.append((f, ms))
    return out


class Spot:
    """A ground spot (a tentacle's): it stays where it is."""

    def __init__(self, x, y):
        self.x, self.y = int(round(x)), int(round(y))

    def pos(self, t):
        return self.x, self.y


class Her(Me):
    """preview_pyke's Me on whole game pixels (her leap moves her between them)."""

    def pos(self, t):
        x, y = super().pos(t)
        return int(round(x)), int(round(y))


class Illaoi(Clip):
    """preview_gnar's clip with her own dense frames and the tentacle's."""

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "illaoi", z))
        if dur and not loop and dur > sum(ms for _, ms in fr):     # the last frame held to the action's end
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an

    def fly(self, tag, t0, t1, x0, x1, y, sheet=None):
        """A projectile's picture flying from x0 to x1 (drawn flying right: the right way here)."""
        self.over.append(Anim(frames_of(sheet or self.small, tag), t0, x0, y, loop=True, until=t1, x1=x1, y1=y))

    def tentacle(self, sp, when, where, z=3, under=True):
        """One of the tentacle's sheets on a spot or a unit (the kit's views: z 1 standing, z 3 lashing)."""
        (self.under if under else self.over).append(OnFoe(tent_frames(sp, z), when, where))


def px_ms(speed):
    """A projectile's speed (distance units a tick) in game px a ms."""
    return speed / 1000.0 * 60 / 1000


def showcase(out, z=3):
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_illaoi_fx"], fx["league_illaoi_big"]
    tent = {k: load(v) for k, v in TENT.items()}
    W, H = 190, 140
    gy = 118
    x0 = 62
    far = x0 + 34                                       # in her attack's reach (25 game px) and their two bodies'
    d = Foe(load(DARIUS), far, gy)
    me = Her(x0, gy)
    c = Illaoi(load(CHAMP), d, me, small, big)
    c.wait(400)
    lashes = []

    def lash(when):
        c.tentacle(tent["lash"], when, d, under=False)
        c.on("p_slam", when + 150, sheet=big)
        c.on("p_hit", when + 150)
        c.on_me("p_heal", when + 150)
        c.d.flinches.append(when + 150)
        lashes.append(when)

    # two idol swings: the first grows a tentacle before her (between them), struck every t_per
    spot = Spot(x0 + P["t_place"] / 1000.0, gy - 6)
    for k in range(2):
        t = c.t
        c.a("attack", tick(P["atk_dur"]))
        hit = t + tick(P["a_hit"] - 1)
        c.on("a_hit", hit)
        c.d.flinches.append(hit)
        if k == 0:
            c.tentacle(tent["tentacle"], hit, spot)
            c.over.append(OnFoe(frames_of(big, "p_spawn"), hit, spot))
            grown = hit
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))
    lash(grown + tick(P["t_first"]))
    # Test of Spirit: the ghost tentacle tears his spirit out (slowed); E -> W at once - the leap, the lesson
    t = c.t
    c.a("skill2", tick(P["e_dur"]))
    rel = t + tick(P["e_rel"] - 1)
    hit = rel + (far - x0) / px_ms(P["e_speed"])
    c.fly("e_grab", rel, hit, x0 + 10, far - 4, gy - 22)
    c.on("e_spirit", hit, until=hit + tick(P["e_t"]))
    c.on("e_slow", hit, until=hit + tick(P["e_slow_t"]))
    lash(grown + tick(P["t_first"] + P["t_per"]))
    t = max(c.t, hit + 30)
    c.wait(t - c.t)
    c.a("skill", tick(P["w_dur"]))
    leap0 = t + tick(P["w_dash"] - 1)
    leap1 = leap0 + 140
    me.moves.append((leap0, leap1, x0, far - 14))
    land = leap1 + tick(P["w_hit"])
    c.on("w_slam", land, sheet=big)
    c.on("w_mark", land, until=land + tick(P["w_mark_t"]))
    c.d.flinches.append(land)
    lash(land + 100)                                    # W -> tentacles: the standing one lashes the lesson
    c.wait(500)
    # Leap of Faith: the crater, a tentacle on him, her glyph ring; the tentacles strike every r_per
    t = c.t
    c.a("ult", tick(P["r_dur"]))
    slam = t + tick(P["r_at"] - 1)
    c.on_me("r_slam", slam, sheet=big, under=True)
    c.on_me("r_aura", slam, sheet=big, until=slam + tick(P["r_on"]), under=True)
    c.on("r_hit", slam)
    c.d.flinches.append(slam)
    on_him = Spot(far + 4, gy - 4)
    c.tentacle(tent["tentacle"], slam, on_him)
    c.over.append(OnFoe(frames_of(big, "p_spawn"), slam, on_him))
    for k in range(3):
        lash(slam + tick(P["t_first"] + k * P["r_per"]))
    d.death = slam + tick(P["t_first"] + 2 * P["r_per"]) + 300
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
        rows = dense_rows(s) + [(load(v), "hd_idle", k) for k, v in TENT.items()]
        print("frames", contact(rows, os.path.join(args.out, "league_illaoi_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_illaoi_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_illaoi_showcase.gif")))


if __name__ == "__main__":
    main()
