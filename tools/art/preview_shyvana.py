#!/usr/bin/env python3
"""Preview images for Shyvana, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_shyvana.py [--out docs/preview] [--only frames|effects|showcase]

  league_shyvana_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_shyvana_effects.png   every effect animation, 3x
  league_shyvana_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_shyvana.py, 60 ticks
                               a second): her claw twice, the first wrapping her in Inferno Aegis (it blows up round
                               her when it ends); Emberstrike's first strike and the second strike on her next attack
                               (the ring of fire); Molten Burst's fireball; full Fury - Dragon's Descent: she leaps,
                               turns dragon and flies onto Darius breathing fire, the landing; the dragon's claw, the
                               wing, the tail and the bite (Emberstrike's three strikes), its fireball through him; the
                               dragon running out - she turns back; 3x. The dragon only acts here: standing and running
                               it would be her in the main pack (a whole-body dragon needs an add-on).
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
from build_shyvana import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_shyvana")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_shyvana_fx", "league_shyvana_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")


class Shyvana(Clip):
    """preview_gnar's clip with her own dense frames."""

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "shyvana", z))
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


def showcase(out, z=3):
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_shyvana_fx"], fx["league_shyvana_big"]
    W, H = 300, 130
    gy = 104
    x0 = 70
    far = x0 + 26                                       # Darius in her claw's reach
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Shyvana(load(CHAMP), d, me, small, big)
    c.wait(400)
    # the claw twice; the first one wraps her in Inferno Aegis, which blows up round her w_t ticks later
    aegis_end = c.t + tick(P["w_t"])
    c.on_me("w_aegis", c.t, sheet=big, until=aegis_end)
    for _ in range(2):
        hit = c.t + tick(P["a_hit"])
        c.on("a_hit", hit)
        c.d.flinches.append(hit)
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]) // 2)
    c.on_me("w_blast", aegis_end, sheet=big, under=True)
    c.on("w_hit", aegis_end)
    c.d.flinches.append(aegis_end)
    # Q Emberstrike: the first strike (the cleave; its slash is in her frames), the second on her next attack
    hit = c.t + tick(P["q_at"] - 1)
    c.on("q_hit", hit)
    c.d.flinches.append(hit)
    c.a("skill", tick(P["q_dur"]))
    c.wait(200)
    slam = c.t + tick(P["q2_at"] - 1)
    c.on_me("q2_wave", slam, sheet=big, under=True)
    c.on("q2_hit", slam)
    c.d.flinches.append(slam)
    c.a("skill_b", tick(P["q2_dur"]))
    c.wait(250)
    # E Molten Burst: the fireball onto Darius, the burst there
    speed = P["e_speed"] / 1000.0 * 60 / 1000          # game px a ms
    rel = c.t + tick(P["e_rel"] - 1)
    hit = rel + (far - x0 - 8) / speed
    c.fly("e_ball", rel, hit, x0 + 8, far, gy - 4)
    c.on("e_hit", hit)
    c.on("e_blast", hit, sheet=big)
    c.d.flinches.append(hit)
    c.a("skill2", tick(P["e_dur"]))
    # full Fury: the flames round her, then a step back for the flight
    c.on_me("fury_full", c.t, until=c.t + 1100)
    back = x0 - 40
    me.moves.append((c.t, c.t + 500, x0, back))
    c.a("run", 500, loop=True)
    c.wait(600)
    # R Dragon's Descent: she leaps and turns dragon, flies onto Darius breathing fire, lands
    c.on_me("tf_dragon", c.t, sheet=big)
    r_speed = P["r_speed"] / 1000.0 * 60 / 1000
    go = c.t + tick(P["r_at"] - 1)
    land_x = far - 36                                  # the dragon's head (33 px ahead of its pivot) at Darius
    land = go + (land_x - back) / r_speed
    me.moves.append((go, land, back, land_x))
    reach = P["r_cast"] / 1000.0
    c.fly("r_breath", go, go + reach / r_speed, back + 14, back + 14 + reach, gy - 2, sheet=big)
    burn = go + (far - back - 14) / r_speed
    c.on("r_hit", burn)
    c.d.flinches.append(burn)
    c.on_me("r_land", land, sheet=big, under=True)
    c.a("ult", max(tick(P["r_dur"]), land - c.t))
    # the dragon: its claw, then Emberstrike's three strikes - the wing (the gust in its frames), the tail (the big
    # ring), the bite - and its fireball through Darius
    hit = c.t + tick(P["d_rel"])
    c.on("a_hit", hit)
    c.d.flinches.append(hit)
    c.a("d_attack", tick(P["d_atk_dur"]))
    hit = c.t + tick(P["d_q_at"] - 1)
    c.on("q_hit", hit)
    c.d.flinches.append(hit)
    c.a("d_skill", tick(P["q_dur"]))
    slam = c.t + tick(P["d_q2_at"] - 1)
    c.on_me("d_q2_wave", slam, sheet=big, under=True)
    c.on("q2_hit", slam)
    c.d.flinches.append(slam)
    c.a("d_skill_b", tick(P["q2_dur"]))
    bite = c.t + tick(P["q3_at"] - 1)
    c.on("q3_hit", bite)
    c.d.flinches.append(bite)
    c.a("d_bite", tick(P["q3_dur"]))
    rel = c.t + tick(P["de_rel"] - 1)
    end_x = land_x + 10 + P["de_range"] / 1000.0
    through = rel + (far - land_x - 10) / speed
    c.fly("de_ball", rel, rel + (end_x - land_x - 10) / speed, land_x + 10, end_x, gy - 2, sheet=big)
    c.on("de_hit", through)
    c.d.flinches.append(through)
    c.a("d_skill2", tick(P["e_dur"]))
    d.death = through + 200
    c.over.append(Anim(frames_of(big, "de_blast"), rel + (end_x - land_x - 10) / speed, end_x, gy))
    # the dragon runs out: she turns back
    c.on_me("tf_human", c.t, sheet=big)
    c.a("revert", tick(P["rv_dur"]))
    end = c.t + 1200
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_shyvana_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[15:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_shyvana_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_shyvana_showcase.gif")))


if __name__ == "__main__":
    main()
