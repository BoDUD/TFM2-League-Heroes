#!/usr/bin/env python3
"""Preview images for Naafiri, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_naafiri.py [--out docs/preview] [--only frames|effects|showcase]

  league_naafiri_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them), her pack in them
  league_naafiri_effects.png   every effect animation, 3x
  league_naafiri_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_naafiri.py, 60 ticks
                               a second): her bite twice, the pack biting with her (We Are More); Darkin Daggers - the
                               dagger, the bleed, the pack leaping onto him and mauling him - and the second dagger on her
                               next attack (the heal), Eviscerate at once (the combo: the dash, the two shreds); a few
                               steps back, The Call of the Pack (the roar, four hounds - league_naafiri's view hook; the
                               main pack keeps two) and Hounds' Pursuit onto him (the bite, the armour shred); he falls
                               and her eyes flare - the pounce ready again; 3x.
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
from build_naafiri import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_naafiri")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_naafiri_fx", "league_naafiri_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")


class Naafiri(Clip):
    """preview_gnar's clip with her own dense frames."""

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "naafiri", z))
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
    small, big = fx["league_naafiri_fx"], fx["league_naafiri_big"]
    W, H = 360, 120
    gy = 98
    x0 = 190
    far = x0 + 44                                       # Darius in her bite's reach, clear of her head
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Naafiri(load(CHAMP), d, me, small, big)
    c.wait(400)
    # her bite twice, the pack biting with her
    for _ in range(2):
        hit = c.t + tick(P["a_hit"])
        c.on("a_hit", hit)
        c.on("pk_bite", hit + 30)
        c.d.flinches.append(hit)
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]) // 2)
    # Q Darkin Daggers: the dagger flung mid-leap, the bleed, the pack leaping onto him and mauling him
    speed = P["q_speed"] / 1000.0 * 60 / 1000           # game px a ms
    rel = c.t + tick(P["q_rel"] - 1)
    hit = rel + (far - x0 - 20) / speed
    c.fly("q_dagger", rel, hit, x0 + 20, far, gy - 16)
    c.fly("q_leap", rel, hit, x0 - 20, far, gy - 4)
    c.on("q_hit", hit)
    c.on("pk_leap", hit + 40)
    c.d.flinches.append(hit)
    for k in range(4):
        c.on("q_bleed", hit + 500 * (k + 1))
    ride = tick(P["pk_period"])
    for k in range(P["pk_ride"] // P["pk_period"]):
        c.over.append(Anim(frames_of(big, "pk_ride"), hit + 200 + k * ride, far, gy))
    c.a("skill", tick(P["q_dur"]))
    c.wait(250)
    # the second dagger on her next attack, the heal; Eviscerate at once (the combo): the dash, the two shreds
    rel = c.t + tick(P["q2_rel"] - 1)
    hit = rel + (far - x0 - 20) / speed
    c.fly("q2_dagger", rel, hit, x0 + 20, far, gy - 16)
    c.on("q2_hit", hit)
    c.on_me("q_heal", hit + 40)
    c.d.flinches.append(hit)
    c.a("skill", tick(P["q2_dur"]))
    e_speed = P["e_speed"] / 1000.0 * 60 / 1000
    near = far - 30                                      # her head at his front
    t_go = c.t
    t_land = t_go + (near - x0) / e_speed
    me.moves.append((t_go, t_land, x0, near))
    s1 = t_land + tick(P["e_at"])
    s2 = t_land + tick(P["e2_at"])
    c.on_me("e_slash", s1, sheet=big, under=True)
    c.on("e_hit", s1)
    c.on("pk_bite", s1 + 30)
    c.on_me("e_slash2", s2, sheet=big, under=True)
    c.on("e_hit", s2)
    c.d.flinches += [s1, s2]
    c.a("skill2", max(tick(P["e_dur"]), s2 - c.t + 100))
    # a few steps back for the pursuit
    back = near - 70
    me.moves.append((c.t, c.t + 600, near, back))
    c.a("run", 600, loop=True)
    c.wait(300)
    # R: The Call of the Pack (the roar) and Hounds' Pursuit onto him
    roar = c.t
    c.on_me("r_roar", roar, sheet=big)
    c.on_me("pack_aura", roar + 100, sheet=big, until=roar + tick(P["roar_t"]), under=True)
    c.a("p4_ult", tick(P["r_roar"]))                     # the roar doubles the pack (the add-on's p4_* frames)
    r_speed = P["r_speed"] / 1000.0 * 60 / 1000
    go = c.t
    land = go + (near - back) / r_speed + 60
    me.moves.append((go, land, back, near))
    bite = land + tick(P["r_at"])
    c.on("r_hit", bite)
    c.on("pk_bite4", bite + 40)
    c.on("r_shred", bite + 100, until=bite + 1500)
    c.d.flinches.append(bite)
    c.a("p4_ult_b", max(tick(P["r_dur"]), bite - c.t + 150))
    # two more bites with the pack doubled, and he falls: her eyes flare - the pounce ready again
    for _ in range(2):
        hit = c.t + tick(P["a_hit"])
        c.on("a_hit", hit)
        c.on("pk_bite4", hit + 30)
        c.d.flinches.append(hit)
        c.a("p4_attack", tick(P["atk_dur"]))
    d.death = c.t + 60
    c.on_me("r_reset", c.t + 150)
    end = c.t + 1400
    c.idle = "p4_idle"
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_naafiri_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[15:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_naafiri_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_naafiri_showcase.gif")))


if __name__ == "__main__":
    main()
