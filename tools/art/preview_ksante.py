#!/usr/bin/env python3
"""Preview images for K'Sante, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_ksante.py [--out docs/preview] [--only frames|effects|showcase]

  league_ksante_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_ksante_effects.png   every effect animation, 3x
  league_ksante_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_ksante.py, 60 ticks
                              a second): two attacks; Ntofo Strikes twice (the crack in his frames, the slow under
                              Darius), the marked attack (Dauntless Instinct's ring, the bigger hit); Q3's shockwave
                              pulling Darius in - Q3 -> W: Path Maker's brace cut short, the ram, the knockback; All Out:
                              the kick, the ntofos breaking in the burst, the chase and the slam - R -> W: the All Out
                              stance's ram, its sweeps and smash with the aura under him, Darius down; 3x. All Out's
                              standing and running are the add-on's (league_ksante); here his All Out actions only.
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
from build_ksante import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_ksante")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_ksante_fx", "league_ksante_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")


def px_ms(speed):
    """A kit speed (units a tick) in game px a ms."""
    return speed / 1000.0 * 60 / 1000


class KSante(Clip):
    """preview_gnar's clip with his own dense frames."""

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "ksante", z))
        if dur and not loop and dur > sum(ms for _, ms in fr):     # the last frame held to the action's end
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an

    def under_foe(self, tag, when, until=None, sheet=None):
        self.under.append(OnFoe(frames_of(sheet or self.small, tag), when, self.d, until=until))

    def fly(self, tag, t0, t1, x0, x1, y, sheet=None):
        """A projectile's picture flying from x0 to x1 (drawn flying right: the right way here)."""
        self.over.append(Anim(frames_of(sheet or self.small, tag), t0, x0, y, loop=True, until=t1, x1=x1, y1=y))

    def hit(self, tag, when, sheet=None):
        self.on(tag, when, sheet=sheet)
        self.d.flinches.append(when)


def showcase(out, z=3):
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_ksante_fx"], fx["league_ksante_big"]
    W, H = 340, 140
    gy = 108
    x0 = 70
    reach = 32                                          # Darius in his attack's reach (25000 and the bodies)
    far = x0 + reach
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = KSante(load(CHAMP), d, me, small, big)
    c.wait(400)
    # two attacks
    for _ in range(2):
        c.hit("a_hit", c.t + tick(P["a_hit"]))
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]) // 2)
    # Ntofo Strikes twice: the crack is in his frames; each strike slows Darius and arms the passive
    for tag in ("skill", "skill_b"):
        strike = c.t + tick(P["q_at"] - 1)
        c.hit("q_hit", strike)
        c.under_foe("q_slow", strike, until=strike + tick(P["q_slow_t"]))
        c.a(tag, tick(P["q_dur"]))
        c.wait(180)
    # the marked attack: Dauntless Instinct's ring under him from the strike that armed it until the attack lands
    land = c.t + tick(P["a_hit"])
    c.on_me("p_mark", strike, until=land, under=True)
    c.hit("a_hit", land)
    c.on("p_hit", land)
    c.a("attack", tick(P["atk_dur"]))
    c.wait(250)
    # Q3: the shockwave rolls out, pulls Darius in (q3_pull a tick for q3_pull_t ticks)
    rel = c.t + tick(P["q3_rel"] - 1)
    wave = px_ms(P["q3_speed"])
    reach_q3 = P["q3_range"] / 1000.0
    c.fly("q3_wave", rel, rel + reach_q3 / wave, x0 + 6, x0 + 6 + reach_q3, gy + 3, sheet=big)
    cross = rel + (far - x0 - 6) / wave
    c.hit("q3_hit", cross)
    pull = P["q3_pull"] * P["q3_pull_t"] / 1000.0
    d.slides.append((cross, cross + tick(P["q3_pull_t"]), -min(pull, reach - 18)))
    c.a("skill_c", tick(P["q3_dur"]))
    near = far - min(pull, reach - 18)
    # Q3 -> W: the brace cut short (w_fast), the ram onto Darius, the landing, the knockback
    c.on_me("w_brace", c.t, sheet=big, until=c.t + tick(P["w_fast"] + P["w_dash_dur"]), under=True)
    c.a("skill2", tick(P["w_fast"]))
    go, ram = c.t, px_ms(P["w_speed"])
    stop = near - 14                                    # his ntofos against Darius
    arrive = go + max(1.0, stop - x0) / ram
    me.moves.append((go, arrive, x0, stop))
    c.on_me("w_land", arrive, sheet=big, under=True)
    c.hit("w_hit", arrive)
    kb = P["w_kb"] * P["w_kb_t"] / 1000.0
    d.slides.append((arrive, arrive + tick(P["w_kb_t"]), kb))
    c.a("skill2_dash", max(tick(P["w_dash_dur"]), arrive - go))
    x = stop
    c.wait(300)
    # R All Out: the kick (the ntofos break in All Out's burst), the champion flies back, he dashes after it and slams it
    kick = c.t + tick(P["r_at"] - 1)
    c.hit("r_hit", kick)
    rkb = P["r_kb"] * P["r_kb_t"] / 1000.0
    d.slides.append((kick, kick + tick(P["r_kb_t"]), rkb))
    c.on_me("ao_on", kick, sheet=big)
    aura_from = kick
    c.a("ult", tick(P["r_at"] + P["r_chase"] - 1))
    c.idle = "ao_idle"                                  # All Out from the kick on (the add-on's swap)
    go, chase = c.t, px_ms(P["r_speed"])
    target = near + kb + rkb
    stop = target - 16
    arrive = go + max(1.0, stop - x) / chase
    me.moves.append((go, arrive, x, stop))
    c.under_foe("r_slam", arrive, sheet=big)
    c.hit("r_hit", arrive)
    c.a("ult_dash", max(tick(P["r_dash_dur"]), arrive - go))
    x = stop
    c.wait(200)
    # R -> W in All Out: the brace cut short, the ram (no knockback in All Out: more of his health instead)
    c.on_me("w_brace", c.t, sheet=big, until=c.t + tick(P["w_fast"] + P["w_dash_dur"]), under=True)
    c.a("ao_skill2", tick(P["w_fast"]))
    go = c.t
    stop2 = target - 12
    arrive = go + max(1.0, stop2 - x) / ram
    me.moves.append((go, arrive, x, stop2))
    c.on_me("w_land", arrive, sheet=big, under=True)
    c.hit("w_hit", arrive)
    c.a("ao_skill2_dash", max(tick(P["w_dash_dur"]), arrive - go))
    # All Out's sweeps and smash
    for _ in range(2):
        c.hit("a_hit", c.t + tick(P["a_hit"]))
        c.a("ao_attack", tick(P["atk_dur"]))
        c.wait(120)
    smash = c.t + tick(P["q_at"] - 1)
    c.hit("q_hit", smash)
    c.a("ao_skill", tick(P["q_dur"]))
    d.death = smash + 150
    c.under.append(Anim(frames_of(big, "ao_aura"), aura_from, 0, 0, loop=True, until=c.t + 900))
    c.under[-1].pos = me.pos
    c.wait(900)
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_ksante_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_ksante_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_ksante_showcase.gif")))


if __name__ == "__main__":
    main()
