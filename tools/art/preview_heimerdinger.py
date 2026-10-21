#!/usr/bin/env python3
"""Preview images for Heimerdinger, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_heimerdinger.py [--out docs/preview] [--only frames|effects|showcase]

  league_heimerdinger_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_heimerdinger_effects.png   every effect animation, 3x (the two turrets' lives included)
  league_heimerdinger_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_heimerdinger.py,
                                    60 ticks a second), as the add-on shows it: the H-28G turret set down in front of
                                    him, seen from the side facing Darius (league_heimerdinger_turret_r, PPU 1.75), firing
                                    its shots from the muzzle (t_shot); two hextech bolts and the third attack with
                                    the crane's five Micro-Rockets; the CH-2 grenade lobbed onto Darius (the blast, the
                                    stun, the slow) and at once the combo - the rockets on the stunned champion, the
                                    turret's charged beam (t_beam_line); a few steps back and UPGRADE!!! with one champion
                                    round him: the gear bursting from his backpack and the H-28Q apex turret (from the
                                    side too) firing its plasma (the slow) until Darius falls; 3x.
"""
import argparse
import json
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
from preview_pyke import Me  # noqa: E402
from build_heimerdinger import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_heimerdinger")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_heimerdinger_fx", "league_heimerdinger_big")}
# the add-on's side turrets facing right (Darius is to his right), at their own PPU (hd.rs EFFECTS)
TURRETS = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_heimerdinger_turret_r", "league_heimerdinger_apex_r")}
MUZZLES = os.path.join(ROOT, "assets", "source", "heimerdinger", "hd", "side_muzzles.json")
SIDE = os.path.join(ROOT, "assets", "source", "heimerdinger", "hd", "side_turrets.json")     # their PPU
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")
CLAW = (-18, -41)        # the crane's claw from his pivot when W fires (the attack_w frames' flash; the kit's w_y)


def dense_at(sp, tag, ppu, z):
    """preview_dense.dense for a sheet at its own ppu (the side turrets' 3, not the hero's 1.5)."""
    k = z / ppu
    out = []
    for (a, _), (b, ms) in zip(frames_of(sp, tag), frames_of(sp, "hd_" + tag)):
        f = b.resize((max(1, round(b.width * k)), max(1, round(b.height * k))), Image.NEAREST if k >= 1 else Image.BOX)
        f.info["one"] = (a.width, a.height)
        out.append((f, ms))
    return out


def px_ms(speed):
    """A projectile's speed (1000 a game px, a tick) in game px a ms."""
    return speed / 1000.0 * 60 / 1000


class Lob(Anim):
    """A lobbed grenade: x and y linear from (x, y) to (x1, y1), plus an arc `peak` px high."""

    def __init__(self, fr, t0, t1, a, b, peak):
        super().__init__(fr, t0, a[0], a[1], loop=True, until=t1, x1=b[0], y1=b[1])
        self.peak = peak

    def pos(self, t):
        x, y = super().pos(t)
        u = min(1.0, max(0.0, (t - self.t0) / (self.until - self.t0)))
        return x, int(round(y - 4 * self.peak * u * (1 - u)))


class Heimer(Clip):
    """preview_gnar's clip with his own dense frames and his turrets."""

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "heimerdinger", z))
        if dur and not loop and dur > sum(ms for _, ms in fr):     # the last frame held to the action's end
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an

    def fly(self, tag, t0, t1, a, b):
        """A projectile's picture flying from a to b (drawn flying right: the right way here)."""
        self.over.append(Anim(frames_of(self.small, tag), t0, a[0], a[1], loop=True, until=t1, x1=b[0], y1=b[1]))

    def shot(self, tag, hit_tag, t0, a, speed, dy=-5):
        """A shot from a at Darius (the projectile drawn 5 px over his pivot): its hit on arrival; -> the arrival."""
        b = (self.d.x, self.d.y + dy)
        t1 = t0 + abs(b[0] - a[0]) / px_ms(speed)
        self.fly(tag, t0, t1, a, b)
        self.on(hit_tag, t1)
        self.d.flinches.append(t1)
        return t1


def showcase(out, z=3):
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_heimerdinger_fx"], fx["league_heimerdinger_big"]
    tur = {k: load(v) for k, v in TURRETS.items()}
    with open(T.long_path(MUZZLES), encoding="utf-8") as f:
        mz = json.load(f)                                # each muzzle: game px ahead of and up from the pivot
    with open(T.long_path(SIDE), encoding="utf-8") as f:
        side_ppu = float(json.load(f)["ppu"])
    W, H = 210, 112
    gy = 90
    x0 = 100
    far = x0 + P["atk_range"] // 1000                   # Darius at his attack range (55 game px)
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Heimer(load(CHAMP), d, me, small, big)
    bolt = lambda t0, x: c.shot("a_bolt", "a_hit", t0, (x + 10, gy), P["a_speed"])

    def rockets(t0, x):
        return [c.shot("w_rocket", "w_hit", t0 + tick(k * P["w_gap"]), (x + CLAW[0], gy + CLAW[1]), P["w_speed"])
                for k in range(P["w_n"])]

    def turret(sheet, muzzle, at, t_stand, first, per, shoot, until):
        """A turret's life on the ground (under the units) and its shots at Darius from its muzzle from first on, every
        per, while shoot(t) gives the shot's (tag, hit, speed) and until it stops."""
        an = Anim(dense_at(sheet, "idle", side_ppu, z), t_stand, at, gy)
        c.under.append(an)
        t = t_stand + tick(first)
        while t < min(until, an.until):
            tag, hit, speed = shoot(t)
            c.shot(tag, hit, t, (round(at + muzzle[0]), round(gy - muzzle[1])), speed)
            t += tick(per)

    c.wait(400)
    # Q: the H-28G turret set down q_place in front of him (the hidden bolt's flight), its shots (the add-on's t_shot)
    q_at = x0 + P["q_place"] // 1000
    q_stand = c.t + tick(P["q_rel"] - 1) + tick(P["q_place"] / P["q_speed"])
    c.a("skill", tick(P["q_dur"]))
    c.wait(300)
    # two hextech bolts and the third attack with the crane's rockets
    for k in range(3):
        rel = c.t + tick(P["a_rel"] - 1)
        bolt(rel, x0)
        if k == 2:
            rockets(rel, x0)
        c.a("attack_w" if k == 2 else "attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]) // 2)
    # E: the grenade lobbed onto Darius - the blast under him, the stun, the slow
    rel = c.t + tick(P["e_rel"] - 1)
    land = rel + tick(P["e_travel"])
    c.over.append(Lob(frames_of(small, "e_grenade"), rel, land, (x0 + 8, gy - 12), (far, gy), 28))
    c.under.append(Anim(frames_of(big, "e_blast"), land, far, gy))
    c.on("e_hit", land)
    c.on("e_slow", land, until=land + tick(P["e_slow_t"]))
    stun_end = land + tick(P["e_stun"])
    d.flinches.append(land)
    c.a("skill2", tick(P["e_dur"]))
    c.wait(max(0, land - c.t + 60))
    # the combo E -> W: the next attack fires the rockets at the stunned champion at once
    rel = c.t + tick(P["a_rel"] - 1)
    bolt(rel, x0)
    rockets(rel, x0)
    c.a("attack_w", tick(P["atk_dur"]))
    c.wait(tick(P["atk_cd"] - P["atk_dur"]) // 2)
    # a few steps back, then R UPGRADE!!! with one champion round him: the gear, the apex turret q_place in front
    back = x0 - 44                                     # the apex clear of the Q turret
    me.moves.append((c.t, c.t + 700, x0, back))
    c.a("run", 700, loop=True)
    c.wait(150)
    r0 = c.t
    c.on_me("r_up", r0 + tick(P["r_up"]), sheet=big)
    x_at = back + P["q_place"] // 1000
    x_stand = r0 + tick(P["r_rel"]) + tick(P["q_place"] / P["q_speed"])
    c.a("ult", tick(P["r_dur"]))
    # Darius falls under the apex's plasma
    death = x_stand + tick(P["x_first"]) + tick(P["x_per"]) * 6 + 200
    d.death = death
    for k in range(7):
        c.on("e_slow", x_stand + tick(P["x_first"] + k * P["x_per"]) + 120, until=x_stand + tick(P["x_first"] + k * P["x_per"]) + 120 + tick(P["x_slow_t"]))
    turret(tur["league_heimerdinger_apex_r"], mz["apex"], x_at, x_stand, P["x_first"], P["x_per"],
           lambda t: ("x_shot", "x_hit", P["x_speed"]), death - 200)
    # the Q turret's shots all along: the beam while Darius is stunned (the turret's combo), its cannon otherwise
    turret(tur["league_heimerdinger_turret_r"], mz["turret"], q_at, q_stand, P["t_first"], P["t_per"],
           lambda t: ("t_beam_line", "t_beam", P["b_speed"]) if land <= t < stun_end
           else ("t_shot", "t_hit", P["t_speed"]), death - 200)
    end = death + 1500
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_heimerdinger_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        fronts = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_heimerdinger_turret", "league_heimerdinger_apex")}
        for name, path in {**FX, **fronts, **TURRETS}.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[20:]}:{t['name']}") for t in sp.tags if not t["name"].startswith("hd_")]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_heimerdinger_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_heimerdinger_showcase.gif")))


if __name__ == "__main__":
    main()
