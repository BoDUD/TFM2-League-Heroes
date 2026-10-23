#!/usr/bin/env python3
"""Preview images for Azir, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_azir.py [--out docs/preview] [--only frames|effects|showcase]

  league_azir_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_azir_effects.png   every effect animation, 3x (his effects, the soldier's, the guards', the Sun Disc's sheets)
  league_azir_showcase.gif  a scripted fight against Darius in the mid lane, timed like the kit (tools/kit/build_azir.py,
                            60 ticks a second): two attacks - a sand soldier rises in front of him and stabs for him
                            (the sand spear on Darius); Conquering Sands - the sand rush through Darius (the quicksand),
                            the soldier moved to his spot rising there and stabbing at once (Q -> stab); Shifting Sands
                            - the sand shield, the dash onto him, the geyser, one more soldier (E -> a soldier); at once
                            Emperor's Divide pushing back (E -> R): Azir steps behind him and the guards' wall charges back
                            toward where Azir came from, knocking Darius away (the guards facing left: the add-on's tags);
                            he falls; 3x.
Every picture goes on its view's layer in the kit (z below 0 under the units, else over them, a higher z on top): the
soldiers stand over the units, so the ones moved onto Darius stand in front of him, as in the game.
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
from preview_pyke import Me, OnFoe, OnMe  # noqa: E402
from build_azir import P, build  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_azir")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_azir_fx", "league_azir_big")}
SUMMONS = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_azir_soldier", "league_azir_guard", "league_azir_disc")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")
KIT = build(P)
Z = {v["tag"]: v["z"] for v in KIT["view_effects"] + KIT["view_projectiles"]}   # a picture's layer in the game


class Him(Me):
    """preview_pyke's Me on whole game pixels (his dash and his step behind move him between them)."""

    def pos(self, t):
        x, y = super().pos(t)
        return int(round(x)), int(round(y))


class Azir(Clip):
    """preview_gnar's clip with his own dense frames (turned round after he steps behind Darius) and his summons."""

    def __init__(self, *a):
        super().__init__(*a)
        self.flip_from = None
        self.soldier, self.guard = load(SUMMONS["league_azir_soldier"]), load(SUMMONS["league_azir_guard"])

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "azir", z))
        if dur and not loop and dur > sum(ms for _, ms in fr):     # the last frame held to the action's end
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        flip = self.flip_from is not None and self.t >= self.flip_from
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None, flip=flip)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an

    def put(self, an, tag):
        """An effect on its picture's layer in the kit: under the units below z 0, else over them above lower z."""
        an.z = Z[tag]
        if an.z < 0:
            self.under.append(an)
            return an
        k = len(self.over)
        while k and self.over[k - 1].z > an.z:
            k -= 1
        self.over.insert(k, an)
        return an

    def on(self, tag, when, sheet=None, until=None):
        return self.put(OnFoe(frames_of(sheet or self.small, tag), when, self.d, until=until), tag)

    def on_me(self, tag, when, sheet=None, until=None):
        return self.put(OnMe(frames_of(sheet or self.small, tag), when, self.me, until=until), tag)

    def fly(self, tag, t0, t1, x0, x1, y):
        return self.put(Anim(frames_of(self.small, tag), t0, x0, y, loop=True, until=t1, x1=x1, y1=y), tag)

    def at(self, tag, when, x, y, sheet=None, until=None):
        """An effect picture on a fixed spot."""
        return self.put(Anim(frames_of(sheet or self.small, tag), when, x, y, loop=until is not None, until=until), tag)

    def on_ground(self, tag, when, sheet=None, until=None):
        """A picture on the ground under Darius (under the units)."""
        self.under.append(OnFoe(frames_of(sheet or self.small, tag), when, self.d, until=until))

    def stand(self, slot, when, x, y, until):
        """A soldier rising on (x, y) at `when`, then standing until `until` (the sheet's dense frames): the standing one."""
        rise = dense(self.soldier, f"soldier_{slot}_rise", "azir", 3)
        stand = dense(self.soldier, f"soldier_{slot}", "azir", 3)
        end = when + sum(ms for _, ms in rise)
        self.put(Anim(rise, when, x, y), f"soldier_{slot}_rise")
        return self.put(Anim(stand, end, x, y, loop=True, until=until), f"soldier_{slot}")

    def guards(self, when, x, y, left):
        """R's wall: the guards' hops (r_stamps of them, each its step's picture) from (x, y), the dust under them."""
        side = "l" if left else "r"
        hop = P["r_len"] // P["r_stamps"] / 1000.0
        ms = tick(P["r_len"] // P["r_stamps"] // P["r_speed"])
        for i in range(1, P["r_stamps"] + 1):
            tag = f"charge_{side}_{'ab'[i % 2]}"
            hx = x + (-hop if left else hop) * i
            t = when + ms * i
            self.put(Anim(dense(self.guard, tag, "azir", 3), t, int(round(hx)), y, loop=True, until=t + ms), tag)
            self.at("r_dust", t, int(round(hx)), y)


def px_ms(speed):
    """A projectile's speed (distance units a tick) in game px a ms."""
    return speed / 1000.0 * 60 / 1000


def showcase(out, z=3):
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_azir_fx"], fx["league_azir_big"]
    W, H = 300, 140
    gy = 112
    x0 = 90
    far = x0 + 50                                       # in his attack's reach (52.5 game px)
    d = Foe(load(DARIUS), far, gy)
    me = Him(x0, gy)
    c = Azir(load(CHAMP), d, me, small, big)
    c.wait(400)
    end_all = 12000
    sx = x0 + P["s_place"] / 1000.0                     # Arise!: the soldier s_place in front of him
    # two attacks: the first raises a soldier (the hidden bolt's stop), both stab Darius
    for k in range(2):
        t = c.t
        c.a("attack", tick(P["atk_dur"]))
        if k == 0:
            rose = t + (P["s_place"] / P["s_speed"]) * 1000 / 60
            c.at("s_spawn", rose, int(sx), gy)
            soldier_a = c.stand("a", rose, int(sx), gy, until=None)
        stab = t + tick(P["a_rel"] - 1)
        c.on("s_stab", stab)
        c.d.flinches.append(stab)
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))
    # Conquering Sands: the sand rush through Darius (his slow), the soldier moved onto his spot and stabbing at once
    t = c.t
    c.a("skill", tick(P["q_dur"]))
    rel = t + tick(P["q_rel"] - 1)
    reach = rel + (far - x0 - 8) / px_ms(P["q_speed"])
    c.fly("q_wave", rel, reach + 80, x0 + 8, far + 8, gy - 11)
    c.on("q_hit", reach)
    c.on_ground("slow", reach, until=reach + tick(P["q_slow_t"]))
    c.d.flinches.append(reach)
    land = rel + tick(3 + P["q_travel"])                # the controller's next run, then the lob
    soldier_a.until = land                              # the old soldier stops at its next checkpoint
    c.at("q_land", land, far, gy)
    c.stand("a", land, far, gy, until=end_all)
    c.on("s_stab", land + tick(2))
    c.d.flinches.append(land + tick(2))
    c.wait(500)
    # Shifting Sands (his ult ready): the sand shell, the dash onto Darius, the geyser, one more soldier there
    t = c.t
    c.a("skill2", tick(P["e_dur"]))
    c.on_me("e_shield", t, until=t + tick(P["e_t"]))
    dash0 = t + tick(P["e_go_at"] - 1)
    stop = far - 12
    dash1 = dash0 + (stop - x0) / px_ms(P["e_speed"])
    me.moves.append((dash0, dash1, x0, stop))
    c.on_me("e_land", dash1)
    c.on("e_hit", dash1)
    c.d.flinches.append(dash1)
    c.stand("b", dash1 + tick(4), far, gy, until=end_all)
    c.wait(max(0, int(dash1) + 60 - c.t))
    # Emperor's Divide right after (E -> R): he steps behind Darius, the guards charge back the way he came
    t = c.t
    rush0 = t + tick(P["r_rush_at"] - 1)
    behind = far + 15
    rush1 = rush0 + (behind - stop) / px_ms(P["r_rush"])
    me.moves.append((rush0, rush1, stop, behind))
    c.flip_from = t
    c.a("ult", tick(P["r_dur"]))
    wall = t + tick(P["r_at"] - 1)
    c.on_me("r_rise", wall, sheet=big)
    c.guards(wall, behind, gy, left=True)
    hit = wall + tick(max(1, 15 // (P["r_speed"] // 1000)))
    c.on("r_hit", hit)
    c.d.flinches.append(hit)
    kb = P["r_kb_speed"] * P["r_kb"] / 1000.0
    c.d.slides.append((hit, hit + tick(P["r_kb"]), -kb))
    d.death = hit + tick(P["r_kb"]) + 500
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_azir_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in {**FX, **SUMMONS}.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[12:]}:{t['name']}") for t in sp.tags if not t["name"].startswith("hd_")]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_azir_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_azir_showcase.gif")))


if __name__ == "__main__":
    main()
