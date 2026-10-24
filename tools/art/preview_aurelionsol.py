#!/usr/bin/env python3
"""Preview images for Aurelion Sol, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_aurelionsol.py [--out docs/preview] [--only frames|effects|showcase]

  league_aurelionsol_frames.png    every animation's dense frames (hd_, PPU 1.75, as league.dll shows them)
  league_aurelionsol_effects.png   every effect animation, 3x
  league_aurelionsol_showcase.gif  a scripted fight with Darius, timed like the kit (tools/kit/build_aurelionsol.py, 60
                                   ticks a second): Aurelion Sol flies in and throws two stars; Singularity (the seed
                                   flying, the black hole on the ground, the core crushing Darius, the slow) and at
                                   once the breath on him (E -> Q: Breath of Light, the beam's segments every q_p
                                   ticks, the sear on him, stardust drawn in); Falling Star (the star called over his
                                   head, the star coming down, the impact and the stun) and the black hole on the
                                   same spot (R -> E); the stardust full (the Skies charged, the stars over his
                                   head); The Skies Descend (the giant star, Darius knocked up, the shockwave); Darius
                                   falls and he takes flight (takedown -> Astral Flight: the lift, the stardust
                                   stream); 3x.
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
from build_aurelionsol import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_aurelionsol")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_aurelionsol_fx", "league_aurelionsol_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")


class Sol(Clip):
    """preview_gnar's clip with his own dense frames, facing left after he turns (flip)."""

    flip = False

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "aurelionsol", z))
        if dur and not loop and dur > sum(ms for _, ms in fr):     # the last frame held to the action's end
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None, flip=self.flip)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an

    def fly(self, tag, t0, t1, x0, x1, y0, y1=None, sheet=None):
        """A projectile's picture flying from (x0, y0) to (x1, y1) (drawn flying right)."""
        self.over.append(Anim(frames_of(sheet or self.small, tag), t0, x0, y0, loop=True, until=t1, x1=x1,
                              y1=y0 if y1 is None else y1, flip=x1 < x0))

    def on_ground(self, tag, when, sheet=None, until=None):
        """A picture on the ground under Darius (under the units)."""
        self.under.append(OnFoe(frames_of(sheet or self.small, tag), when, self.d, until=until))

    def at(self, tag, when, x, y, sheet=None, under=False, until=None):
        """A picture left where it was played (a not-following view: the black hole, the star, the impact)."""
        (self.under if under else self.over).append(Anim(frames_of(sheet or self.small, tag), when, x, y,
                                                         loop=until is not None, until=until))


def px_ms(speed):
    """A speed (distance units a tick) in game px a ms."""
    return speed / 1000.0 * 60 / 1000


def showcase(out, z=3):
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_aurelionsol_fx"], fx["league_aurelionsol_big"]
    W, H = 300, 150
    gy = 118
    x0 = 30
    far = x0 + 150                                      # Darius
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Sol(load(CHAMP), d, me, small, big)
    c.wait(400)

    def flight(x1, haste=0):
        xa = me.pos(c.t)[0]
        t0 = c.t
        t1 = t0 + abs(x1 - xa) / (px_ms(P["ms"]) * (1 + haste / 100))
        c.a("run", t1 - t0, loop=True)
        me.moves.append((t0, t1, xa, x1))

    def gain(when):
        c.on_me("d_gain", when)

    def stars(n):
        for _ in range(n):
            t = c.t
            c.a("attack", tick(P["atk_dur"]))
            rel = t + tick(P["a_rel"] - 1)
            x = me.pos(rel)[0]
            hit = rel + abs(d.pos(rel)[0] - x) / px_ms(P["a_speed"])
            c.fly("a_bolt", rel, hit, x + 8, d.pos(rel)[0], gy + P["a_y"] / 1000)
            c.on("a_hit", hit)
            d.flinches.append(hit)

    def breath():
        """Breath of Light: the channel (q_t), a beam segment every q_p ticks from q_rel, the sear on him."""
        t = c.t
        c.a("skill", tick(P["q_t"]))
        x = me.pos(t)[0]
        y = gy + P["q_y"] / 1000
        for k in range(0, P["q_t"] - P["q_rel"], P["q_p"]):
            go = t + tick(P["q_rel"] - 1 + k)
            end = go + P["q_len"] / 1000 / px_ms(P["q_speed"])
            c.fly("q_beam", go, end, x, x + P["q_len"] / 1000, y)
            hit = go + abs(d.pos(go)[0] - x) / px_ms(P["q_speed"])
            c.on("q_hit", hit)
            d.flinches.append(hit)
            if k == 0:
                gain(hit)

    def hole(when, x):
        """The black hole on the ground at x for e_t: the core on him every e_cp, the slow while he is in it."""
        c.at("e_hole", when, x, gy, sheet=big, under=True)
        for k in range(P["e_cp"], P["e_t"], P["e_cp"]):
            c.on("e_core", when + tick(k))
        c.on_ground("slow", when, until=when + tick(P["e_t"]))
        gain(when + tick(60))

    # in, then two stars
    flight(x0 + 70)
    stars(2)
    # Singularity: the seed lobbed onto him, the black hole there; at once the breath (E -> Q)
    t = c.t
    c.a("skill2", tick(P["e_dur"]))
    rel = t + tick(P["e_rel"] - 1)
    land = rel + tick(P["e_fly"])
    c.fly("e_orb", rel, land, me.pos(rel)[0] + 8, d.pos(rel)[0], gy - 12, gy)
    hole(land, d.pos(land)[0])
    c.t = max(c.t, land + tick(3))
    breath()
    c.wait(200)
    # Falling Star: the star called over his head, coming down on Darius r_fall ticks later, the impact and the stun;
    # the black hole on the same spot at once (R -> E)
    t = c.t
    c.a("ult", tick(P["r_dur"]))
    rel = t + tick(P["r_rel"] - 1)
    c.on_me("r_call", rel)
    spot = d.pos(rel)[0]
    c.at("r_fall", rel, spot, gy, sheet=big)
    land = rel + tick(P["r_fall"])
    c.at("r_impact", land, spot, gy, sheet=big, under=True)
    c.on("r_hit", land)
    d.flinches += [land + k * 100 for k in range(int(tick(P["r_stun"]) // 100))]
    gain(land + 100)
    hole(land + tick(1), spot)
    c.wait(900)
    # the stardust full: the Skies charged, the stars over his head until the next R
    t_sky = c.t
    c.on_me("sky_ready", t_sky)
    c.wait(600)
    # The Skies Descend: the giant star, Darius knocked up, the shockwave from the edge r_wave_at ticks later
    t = c.t
    c.a("ult", tick(P["r_dur"]))
    rel = t + tick(P["r_rel"] - 1)
    c.on_me("r_call", rel)
    c.on_me("sky_glow", t_sky + 400, until=rel)
    spot = d.pos(rel)[0]
    c.at("r_fall", rel, spot, gy, sheet=big)
    land = rel + tick(P["r_fall"])
    c.at("r_sky", land, spot, gy, sheet=big, under=True)
    c.on("r_hit", land)
    d.hops.append((land, land + tick(P["r_up"]), 12))
    wave = land + tick(P["r_wave_at"])
    c.at("r_wave", wave, spot, gy, sheet=big, under=True)
    c.on_ground("slow", wave, until=wave + tick(P["r_wslow_t"]))
    # he falls: the takedown lifts Aurelion Sol into flight (the lift, the stardust stream while it lasts)
    d.death = land + tick(P["r_up"]) + 100
    c.wait(500)
    t = c.t
    c.on_me("w_lift", t)
    c.flip = True
    flight(x0 - 10, haste=P["w_ms"])
    c.on_me("w_trail", t, under=True, until=c.t)
    c.flip = False
    c.wait(1200)
    end = c.t
    return c.render(out, W, H, end, z)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    ap.add_argument("--only", choices=["frames", "effects", "showcase"])
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    if args.only in (None, "frames"):
        s = load(CHAMP)
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_aurelionsol_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[19:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_aurelionsol_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_aurelionsol_showcase.gif")))


if __name__ == "__main__":
    main()
