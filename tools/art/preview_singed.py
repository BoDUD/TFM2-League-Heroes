#!/usr/bin/env python3
"""Preview images for Singed, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_singed.py [--out docs/preview] [--only frames|effects|showcase]

  league_singed_frames.png    every animation's dense frames (hd_, PPU 1.39, as league.dll shows them)
  league_singed_effects.png   every effect animation, 3x
  league_singed_showcase.gif  a scripted fight with Darius, timed like the kit (tools/kit/build_singed.py, 60 ticks a
                              second): Singed runs in leaving his Poison Trail (a cloud each time he leaves the last
                              one), throws Mega Adhesive on Darius (the vial, the glue, the slow), closes in - passing
                              him sets off Noxious Slipstream - and Flings him over his shoulder: the glue lies, so he is
                              rooted where he lands (W -> E; the fling also gives the slipstream's speed, E -> haste);
                              Singed turns, drinks Insanity Potion (the rush, the steam) and throws the glue again at
                              once (R -> W); his clouds now are the potion's - bigger, violet, Grievous Wounds on
                              Darius - and two blows of the plate finish him; 3x.
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
from build_singed import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_singed")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_singed_fx", "league_singed_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")


class Singed(Clip):
    """preview_gnar's clip with his own dense frames, facing left after he turns (flip)."""

    flip = False

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "singed", z))
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
        """A picture left where it was played (a not-following view: a cloud, the glue, a landing's dust)."""
        (self.under if under else self.over).append(Anim(frames_of(sheet or self.small, tag), when, x, y,
                                                         loop=until is not None, until=until))


def px_ms(speed):
    """A speed (distance units a tick) in game px a ms."""
    return speed / 1000.0 * 60 / 1000


def showcase(out, z=3):
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_singed_fx"], fx["league_singed_big"]
    W, H = 260, 120
    gy = 92
    x0 = 30
    far = x0 + 100                                      # Darius
    d = Foe(load(DARIUS), far, gy)
    me = Singed.me = None
    me = Me(x0, gy)
    c = Singed(load(CHAMP), d, me, small, big)
    c.wait(400)
    gap = P["q_gap"] / 1000.0                           # a new cloud once he has left the last one
    state = {"cloud": None, "strong": False}

    def run(x1):
        """He runs to x1, a cloud dropped every `gap` px (the potion's while it lasts)."""
        xa = me.pos(c.t)[0]
        t0 = c.t
        t1 = t0 + abs(x1 - xa) / px_ms(P["ms"])
        c.a("run", t1 - t0, loop=True)
        me.moves.append((t0, t1, xa, x1))
        tt = t0
        while tt < t1:
            x = me.pos(tt)[0]
            if state["cloud"] is None or abs(x - state["cloud"]) >= gap:
                cloud(tt, x)
            tt += 20
        return t1

    def cloud(when, x):
        state["cloud"] = x
        c.at("q_cloud_r" if state["strong"] else "q_cloud", when, x, gy, sheet=big, under=True)
        if state["strong"] and abs(d.pos(when)[0] - x) <= P["r_q_r"] / 1000.0 + 6:
            c.on("gw", when + tick(1), until=when + tick(P["q_p"] + 6))

    def glue(when, x_from):
        """Mega Adhesive: the vial thrown at Darius (w_rel), the glue lying w_t ticks under him, his slow."""
        rel = when + tick(P["w_rel"] - 1)
        lands = rel + tick(P["w_fly"])
        hand = (x_from + (-10 if c.flip else 10), gy - 26)
        c.fly("w_vial", rel, lands, hand[0], d.pos(lands)[0], hand[1], gy - 6)
        c.at("w_glue", lands, d.pos(lands)[0], gy, sheet=big, under=True)
        c.on_ground("slow", lands, until=lands + tick(P["w_t"]))
        return lands

    def slipstream(when):
        c.on_me("p_fast", when, under=True)
        c.on_me("haste", when, until=when + tick(P["p_t"]), under=True)

    # in, leaving his trail
    run(x0 + 40)
    # Mega Adhesive on Darius from 60 px
    t = c.t
    c.a("skill2", tick(P["w_dur"]))
    glue_at = glue(t, me.pos(t)[0])
    # closing in: within p_near of him the slipstream (once per p_gap)
    x_e = far - 18                                      # Fling's reach (20 game px)
    t_run = c.t
    run(x_e)
    near = t_run
    while near < c.t and abs(me.pos(near)[0] - far) > P["p_near"] / 1000.0:
        near += 10
    slipstream(near)
    # Fling: the grab at e_grab, Darius pulled over his shoulder to behind him for e_fly ticks; the glue lies (W -> E):
    # rooted where he lands; the throw gives the slipstream's speed (E -> haste)
    t = c.t
    c.a("skill", tick(P["e_dur"]))
    grab = t + tick(P["e_grab"] - 1)
    c.on("e_hit", grab)
    d.flinches.append(grab)
    behind = x_e - 26
    d.slides.append((grab, grab + tick(P["e_fly"]), behind - far))
    landed = grab + tick(P["e_fly"])
    c.at("e_land", landed, behind, gy, under=True)
    if landed < glue_at + tick(P["w_t"]):
        c.on("e_root", landed, until=landed + tick(P["e_root"]))
    slipstream(grab + tick(1))
    # he turns to Darius behind him; Insanity Potion (the rush, the steam), and the glue again at once (R -> W)
    c.flip = True
    t = c.t
    c.a("ult", tick(P["r_dur"]))
    c.on_me("r_drink", t + tick(2))
    c.on_me("r_aura", t + tick(4), until=t + tick(P["r_t"]), under=True)
    state["strong"] = True
    w2 = t + tick(P["r_w_at"])
    c.t = max(c.t, w2)
    c.a("skill2", tick(P["w_dur"]))
    glue(w2, me.pos(w2)[0])
    # a step toward him in the potion's clouds, two blows of the plate
    run(behind + 18)
    for k in range(2):
        t = c.t
        c.a("attack", tick(P["atk_dur"]))
        blow = t + tick(P["a_hit"] - 1)
        c.on("a_hit", blow)
        d.flinches.append(blow)
        cloud(blow, me.pos(blow)[0]) if k == 0 else None
    d.death = c.t + 150
    c.wait(1300)
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_singed_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_singed_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_singed_showcase.gif")))


if __name__ == "__main__":
    main()
