#!/usr/bin/env python3
"""Preview images for Neeko, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_neeko.py [--out docs/preview] [--only frames|effects|showcase]

  league_neeko_frames.png    every animation's dense frames (hd_, PPU 2.5, as league.dll shows them)
  league_neeko_effects.png   every effect animation, 3x
  league_neeko_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_neeko.py, 60 ticks a
                             second): two bolts and the third, empowered one (Shapesplitter: the flower burst, the
                             haste); Tangle-Barbs rooting him and Blooming Burst onto him at once (the E -> Q combo: the
                             seed bursts and blooms twice more on the champion); Pop Blossom - the charge, the leap onto
                             him, the stunning landing - and the seed again at once (R -> Q); he falls; 3x.
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
from preview_pyke import Me  # noqa: E402
from build_neeko import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_neeko")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_neeko_fx", "league_neeko_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")


class Neeko(Clip):
    """preview_gnar's clip with her own dense frames."""

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "neeko", z))
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

    def seed(self, rel, travel, x0, x1, gy):
        """Blooming Burst: the seed lobbed onto him, the burst, a bloom q_rep ticks later and another (he is held)."""
        land = rel + travel
        self.fly("q_seed", rel, land, x0, x1, gy - 22)
        rep = tick(P["q_rep"])
        for k, (pic, at) in enumerate((("q_burst", land), ("q_bloom", land + rep), ("q_bloom", land + 2 * rep))):
            self.on(pic, at, sheet=self.big)
            self.on("q_hit", at + 30)
            self.d.flinches.append(at)


def showcase(out, z=3):
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_neeko_fx"], fx["league_neeko_big"]
    W, H = 360, 130
    gy = 108
    x0 = 120
    far = x0 + 55                                       # Darius in her bolt's reach (55 game px)
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Neeko(load(CHAMP), d, me, small, big)
    c.wait(400)
    a_speed = P["a_speed"] / 1000.0 * 60 / 1000         # game px a ms
    # two bolts and the third, empowered one: the flower burst on him, the haste round her feet
    for k in range(3):
        rel = c.t + tick(P["a_rel"] - 1)
        hit = rel + (far - x0 - 12) / a_speed
        c.fly("a_bolt", rel, hit, x0 + 12, far, gy - 22)
        c.on("a_hit", hit)
        c.d.flinches.append(hit)
        if k == 2:
            c.on("w_hit", hit)
            c.on_me("w_haste", rel, until=rel + tick(P["w_ms_t"]), under=True)
        c.a("attack_w" if k == 2 else "attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]) // 2)
    # E Tangle-Barbs: the barbs through him and on, the root; Blooming Burst at once onto the rooted champion (E -> Q)
    e_speed = P["e_speed"] / 1000.0 * 60 / 1000
    rel = c.t + tick(P["e_rel"] - 1)
    hit = rel + (far - x0 - 10) / e_speed
    c.fly("e_barbs", rel, rel + (P["e_len"] / 1000.0) / e_speed, x0 + 10, x0 + 10 + P["e_len"] / 1000.0, gy - 17)
    c.on("e_hit", hit)
    c.on("e_bound", hit, until=hit + tick(P["e_root"]))
    c.d.flinches.append(hit)
    c.a("skill2", tick(P["e_dur"]))
    rel = c.t + tick(P["q_rel"] - 1)
    c.seed(rel, tick(P["q_fast"]), x0 + 10, far, gy)
    c.a("skill", tick(P["q_dur"]))
    c.wait(900)
    # R Pop Blossom: the charge (the bud round her), the leap onto him, the landing - the burst, the stun - and the seed
    # again at once (R -> Q)
    c.on_me("r_charge", c.t, sheet=big, until=c.t + tick(P["r_charge"]))
    c.a("ult", tick(P["r_charge"]))
    go = c.t
    r_speed = P["r_speed"] / 1000.0 * 60 / 1000
    near = far - 14
    land = go + (near - x0) / r_speed
    me.moves.append((go, land, x0, near))
    c.on_me("r_jump", go, sheet=big)
    burst = land + tick(P["r_at"])
    c.on_me("r_land", burst, sheet=big, under=True)
    c.on("r_hit", burst + 20)
    c.d.flinches.append(burst)
    c.a("ult_b", max(tick(P["r_dur"]), burst - c.t + 150))
    rel = c.t + tick(P["q_rel"] - 1)
    c.seed(rel, tick(P["q_fast"]), near + 10, far, gy)
    c.a("skill", tick(P["q_dur"]))
    d.death = c.t + 900
    end = c.t + 2200
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_neeko_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_neeko_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_neeko_showcase.gif")))


if __name__ == "__main__":
    main()
