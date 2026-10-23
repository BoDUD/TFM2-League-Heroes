#!/usr/bin/env python3
"""Preview images for Bel'Veth, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_belveth.py [--out docs/preview] [--only frames|effects|showcase]

  league_belveth_frames.png    every animation's dense frames (hd_, PPU 1.75, as league.dll shows them)
  league_belveth_effects.png   every effect animation, 3x
  league_belveth_showcase.gif  a scripted fight with Darius, timed like the kit (tools/kit/build_belveth.py, 60 ticks a
                               second): Bel'Veth glides in and slams her tail (Above and Below: the slam round her, the
                               rift wave running along the line, Darius knocked up and slowed, her frenzy at her feet);
                               the knock-up gives Void Surge back at once (W -> Q): she dashes through him (the launch
                               where she starts, the cut on him) - and through a champion, her tail again at once
                               when it is ready (Q -> W, shown on the next pass); she turns and slashes twice; Endless
                               Banquet (the coral burst, the hit, the slow, the true form's aura behind her); in the true
                               form Void Surge reaches farther (true form -> Q); at bay she storms (Royal Maelstrom:
                               the slashes round her, the cuts on him); he falls and she eats his coral (the true form
                               renewed); 3x.
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
from build_belveth import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_belveth")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_belveth_fx", "league_belveth_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")


class Belveth(Clip):
    """preview_gnar's clip with her own dense frames, facing left after she turns (flip)."""

    flip = False

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "belveth", z))
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
        """A picture left where it was played (a not-following view: the launch, the slam, the burst)."""
        (self.under if under else self.over).append(Anim(frames_of(sheet or self.small, tag), when, x, y,
                                                         loop=until is not None, until=until))


def px_ms(speed):
    """A speed (distance units a tick) in game px a ms."""
    return speed / 1000.0 * 60 / 1000


def showcase(out, z=3):
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_belveth_fx"], fx["league_belveth_big"]
    W, H = 300, 130
    gy = 100
    x0 = 40
    far = x0 + 110                                      # Darius
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Belveth(load(CHAMP), d, me, small, big)
    c.wait(400)
    true_form = {"on": False}

    def glide(x1):
        xa = me.pos(c.t)[0]
        t0 = c.t
        t1 = t0 + abs(x1 - xa) / px_ms(P["ms"])
        c.a("run", t1 - t0, loop=True)
        me.moves.append((t0, t1, xa, x1))

    def frenzy(when):
        """Death in Lavender: attack speed after a spell (the swirl at her feet)."""
        c.on_me("p_as", when, under=True, until=when + tick(P["p_t"]))

    def tail():
        """Above and Below: the slam round her on w_rel, the rift wave along the line through Darius, the knock-up."""
        t = c.t
        c.a("skill2", tick(P["w_dur"]))
        frenzy(t)
        rel = t + tick(P["w_rel"] - 1)
        x = me.pos(rel)[0]
        c.at("w_slam", rel, x, gy, sheet=big, under=True)
        step = -1 if c.flip else 1
        x_end = x + step * P["w_len"] / 1000.0
        reach = rel + abs(x_end - x) / px_ms(P["w_speed"])
        c.fly("w_tail", rel, reach, x, x_end, gy - 2)
        hit = rel + abs(d.pos(rel)[0] - x) / px_ms(P["w_speed"])
        d.hops.append((hit, hit + tick(P["w_up"]), 14))
        c.on_ground("w_hit", hit)
        c.on_ground("slow", hit, until=hit + tick(P["w_slow_t"]))
        return hit

    def surge(x_to):
        """Void Surge: the launch where she starts (q_go), the dash through Darius, the cut as she passes him."""
        t = c.t
        c.a("skill", tick(P["q_dur"]))
        frenzy(t)
        go = t + tick(P["q_go"] - 1)
        xa = me.pos(go)[0]
        c.at("q_dash", go, xa, gy, under=True)
        ticks = P["q_t_r"] if true_form["on"] else P["q_t"]
        me.moves.append((go, go + tick(ticks), xa, x_to))
        xd = d.pos(go)[0]
        passed = go + tick(ticks) * abs(xd - xa) / max(1, abs(x_to - xa))
        c.on("q_hit", passed)
        d.flinches.append(passed)

    def slash(n):
        for _ in range(n):
            t = c.t
            c.a("attack", tick(P["atk_dur"]))
            blow = t + tick(P["a_hit"] - 1)
            c.on("a_hit", blow)
            d.flinches.append(blow)

    # in, then the tail from 50 px: Darius knocked up
    glide(x0 + 50)
    up = tail()
    # W -> Q: the knock-up gives Void Surge back - she dashes through him while he is in the air
    c.t = max(c.t, up + tick(2))
    surge(far + 26)
    c.wait(120)
    # she turns and slashes twice
    c.flip = True
    slash(2)
    # Endless Banquet: the coral burst round her on r_hit, the hit and the slow on Darius, the true form's aura
    t = c.t
    c.a("ult", tick(P["r_dur"]))
    frenzy(t)
    rh = t + tick(P["r_hit"] - 1)
    xm = me.pos(rh)[0]
    c.at("r_burst", rh, xm, gy, sheet=big, under=True)
    c.on("r_hit", rh + tick(1))
    d.flinches.append(rh + tick(1))
    c.on_ground("slow", rh + tick(1), until=rh + tick(P["r_slow_t"]))
    true_form["on"] = True
    aura_from = rh
    # in the true form Void Surge reaches farther (q_t_r): back through him to his other side (true form -> Q)
    c.wait(150)
    surge(far - 40)
    # Q -> W: through a champion with the tail ready again - she turns and slams at once
    c.flip = False
    c.wait(80)
    tail()
    # at bay: Royal Maelstrom, the slashes round her, a cut on him every e_p ticks
    c.wait(120)
    t = c.t
    c.a("skill_e", tick(P["e_t"]), loop=True)
    frenzy(t)
    c.on_me("e_storm", t, sheet=big, until=t + tick(P["e_t"]))
    for k in range(0, P["e_t"], P["e_p"]):
        c.on("e_hit", t + tick(k + 1))
        d.flinches.append(t + tick(k + 1))
    # he falls: she eats his coral (the true form renewed)
    d.death = c.t + 60
    c.on_me("c_eat", c.t + 260)
    c.wait(1500)
    end = c.t
    c.on_me("r_aura", aura_from, under=True, until=end)
    return c.render(out, W, H, end, z)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    ap.add_argument("--only", choices=["frames", "effects", "showcase"])
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    if args.only in (None, "frames"):
        s = load(CHAMP)
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_belveth_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[15:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_belveth_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_belveth_showcase.gif")))


if __name__ == "__main__":
    main()
