#!/usr/bin/env python3
"""Preview images for Ivern, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_ivern.py [--out docs/preview] [--only frames|effects|showcase]

  league_ivern_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them), Daisy's four
                             sheets after them (hd_idle, PPU 1.9)
  league_ivern_effects.png   every effect animation, 3x
  league_ivern_showcase.gif  a scripted fight against Darius in the jungle, timed like the kit (tools/kit/build_ivern.py,
                             60 ticks a second): Rootcaller from afar - the vine roots him - and at once Triggerseed (the
                             combo Q -> E: no ally beside him, so the seed shield is his own) growing the brush at his
                             feet; two seeds thrown from the brush (their magic on-hit); the seed bursting; Daisy! - she
                             rises out of the ground behind Darius, punches, punches and slams (the shockwave, the
                             knock-up), he falls, she waves goodbye and sinks; 3x.
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
from build_ivern import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_ivern")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_ivern_fx", "league_ivern_big")}
DAISY = {k: os.path.join(LEAGUE, "effects", f"league_ivern_daisy_{k}") for k in ("drop", "punch", "slam", "bye")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")
D_PPU = 1.9


def daisy_frames(sp, z):
    """Daisy's hd_idle frames for a clip at zoom z (z / 1.9 of their sheet size), each with its 1x frame's size for
    preview_dense.put (centred where the 1x frame's centre is: the champion's spot)."""
    out = []
    for (a, _), (b, ms) in zip(frames_of(sp, "idle"), frames_of(sp, "hd_idle")):
        k = z / D_PPU
        f = b.resize((max(1, round(b.width * k)), max(1, round(b.height * k))), Image.NEAREST)
        f.info["one"] = (a.width, a.height)
        out.append((f, ms))
    return out


class Ivern(Clip):
    """preview_gnar's clip with his own dense frames and Daisy's."""

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "ivern", z))
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

    def daisy(self, sp, when, z=3):
        """One of Daisy's sheets on the champion, under him (the kit's z -1)."""
        self.under.append(OnFoe(daisy_frames(sp, z), when, self.d))


def px_ms(speed):
    """A projectile's speed (distance units a tick) in game px a ms."""
    return speed / 1000.0 * 60 / 1000


def showcase(out, z=3):
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_ivern_fx"], fx["league_ivern_big"]
    daisy = {k: load(v) for k, v in DAISY.items()}
    W, H = 240, 130
    gy = 108
    x0 = 92
    far = x0 + 46                                       # in his attack's reach (47.5 game px)
    shot_y = gy - 11 + P["a_y"] / 1000.0                # a projectile's height (the pivot 11 over the soles, y_offset)
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Ivern(load(CHAMP), d, me, small, big)
    c.wait(400)
    # Rootcaller: the vine roots him; Q -> E at once on the hit - the seed shield his own, the brush at his feet
    t = c.t
    c.a("skill2", tick(P["q_dur"]))
    rel = t + tick(P["q_rel"] - 1)
    hit = rel + (far - x0) / px_ms(P["q_speed"])
    c.fly("q_vine", rel, hit, x0 + 8, far - 4, shot_y)
    c.on("q_hit", hit)
    c.on("q_root", hit, until=hit + tick(P["q_root"]))
    c.d.flinches.append(hit)
    c.on_me("e_seed", hit, until=hit + tick(P["e_t"]))
    c.on_me("w_brush", hit, sheet=big, under=True)
    burst = hit + tick(P["e_t"])
    # two seeds from the brush (his magic on-hit while it stands)
    c.wait(max(0, hit + 150 - c.t))
    for _ in range(2):
        t = c.t
        c.a("attack", tick(P["atk_dur"]))
        rel = t + tick(P["a_rel"] - 1)
        land = rel + (far - x0) / px_ms(P["a_speed"])
        c.fly("a_seed", rel, land, x0 + 8, far - 4, shot_y)
        c.on("a_hit", land)
        c.on("w_hit", land)
        c.d.flinches.append(land)
        c.wait(tick(P["atk_cd"] - P["atk_dur"]) // 2)
    c.on_me("e_burst", burst, sheet=big)
    c.wait(max(0, burst + 300 - c.t))
    # Daisy!: she rises behind him (the dust), knocks him up; a punch every second, the third a slam
    t = c.t
    c.a("ult", tick(P["r_dur"]))
    drop = t + tick(P["r_rel"] - 1) + 30
    c.daisy(daisy["drop"], drop)
    c.on("r_dust", drop, sheet=big)
    c.d.hops.append((drop, drop + tick(P["r_up"]), 8))
    for k in range(3):
        go = drop + tick(P["r_per"] * (k + 1))
        if k < 2:
            c.daisy(daisy["punch"], go)
            land = go + tick(P["r_hit_at"])
        else:
            c.daisy(daisy["slam"], go)
            land = go + tick(P["r_slam_at"])
            c.on("r_shock", land, sheet=big)
            c.d.hops.append((land, land + tick(P["r_up"]), 10))
        c.on("r_hit", land)
        c.d.flinches.append(land)
    d.death = land + tick(P["r_up"]) + 100
    c.daisy(daisy["bye"], land + 400)
    end = land + 2000
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
        rows = dense_rows(s) + [(load(v), "hd_idle", f"daisy_{k}") for k, v in DAISY.items()]
        print("frames", contact(rows, os.path.join(args.out, "league_ivern_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_ivern_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_ivern_showcase.gif")))


if __name__ == "__main__":
    main()
