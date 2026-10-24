#!/usr/bin/env python3
"""Preview images for Sejuani, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_sejuani.py [--out docs/preview] [--only frames|effects|showcase]

  league_sejuani_frames.png    every animation's dense frames (hd_, PPU 2.0, as league.dll shows them)
  league_sejuani_effects.png   every effect animation, 3x
  league_sejuani_showcase.gif  a scripted fight with Darius, timed like the kit (tools/kit/build_sejuani.py, 60 ticks a
                               second, the add-on's League rules): out of combat she wears the Frost Armour; Arctic
                               Assault (the snow kicked up where she starts, the charge stopping on Darius, the tusk
                               impact, the knock-up, the glint) gives Winter's Wrath at once (Q -> W: the sweep's ring,
                               the ice line racing ahead, the bursts, the slow, a Frost stack each swing); her flail
                               brings the Frost to four and freezes him (W -> freeze); the next blow shatters him (stun
                               -> shatter); Glacial Prison (the bola, the prison, the ice storm) gives Arctic Assault
                               back and she charges him again (R -> Q); he falls; 3x.
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
from build_sejuani import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_sejuani")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_sejuani_fx", "league_sejuani_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")


class Sejuani(Clip):
    """preview_gnar's clip with her own dense frames."""

    flip = False

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "sejuani", z))
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

    def on_foe(self, tag, when, sheet=None, until=None, under=False):
        """A picture following Darius (the frozen prison held, a Frost stack over his head)."""
        (self.under if under else self.over).append(OnFoe(frames_of(sheet or self.small, tag), when, self.d,
                                                          until=until))

    def at(self, tag, when, x, y, sheet=None, under=False, until=None):
        """A picture left where it was played (a not-following view: the snow kick-up, the ice storm)."""
        (self.under if under else self.over).append(Anim(frames_of(sheet or self.small, tag), when, x, y,
                                                         loop=until is not None, until=until))


def px_ms(speed):
    """A speed (distance units a tick) in game px a ms."""
    return speed / 1000.0 * 60 / 1000


def showcase(out, z=3):
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_sejuani_fx"], fx["league_sejuani_big"]
    W, H = 320, 130
    gy = 100
    x0 = 40
    far = x0 + 150                                      # Darius
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Sejuani(load(CHAMP), d, me, small, big)
    frost = {"n": 0}
    fight = {"from": None}

    def stack(when):
        """A Frost stack on Darius (the add-on's snowflake over him); the fourth freezes him."""
        frost["n"] += 1
        if frost["n"] < P["f_n"]:
            c.on_foe("frost", when, until=when + tick(P["f_t"]))
            return None
        frost["n"] = 0
        c.on_foe("e_freeze", when, until=when + tick(P["e_stun"]))
        return when

    def charge(x_stop):
        """Arctic Assault: the snow where she starts (q_go), the charge stopping on Darius (the add-on), the impact,
        the knock-up and the glint on him."""
        t = c.t
        c.a("skill", tick(P["q_dur"]))
        go = t + tick(P["q_go"] - 1)
        xa = me.pos(go)[0]
        c.at("q_dash", go, xa, gy, under=True)
        me.moves.append((go, go + tick(P["q_t"]), xa, x_stop))
        hit = go + tick(P["q_t"])
        c.on("q_hit", hit)
        c.on_foe("f_mark", hit)
        d.hops.append((hit, hit + tick(P["q_up"]), 12))
        return hit

    def wrath():
        """Winter's Wrath: the sweep round her on w_rel1, the slam's ice line on w_rel2; a burst, a slow and a Frost
        stack on Darius for each swing."""
        t = c.t
        c.a("skill2", tick(P["w_dur"]))
        r1 = t + tick(P["w_rel1"] - 1)
        c.on_me("w_sweep", r1, sheet=big, under=True)
        c.on("w_hit", r1)
        d.flinches.append(r1)
        c.on_foe("slow", r1, until=r1 + tick(P["w_slow_t"]), under=True)
        stack(r1)
        r2 = t + tick(P["w_rel2"] - 1)
        x = me.pos(r2)[0]
        x_end = x + P["w_len"] / 1000.0
        c.fly("w_line", r2, r2 + abs(x_end - x) / px_ms(P["w_speed"]), x, x_end, gy - 11)
        hit = r2 + abs(d.pos(r2)[0] - x) / px_ms(P["w_speed"])
        c.on("w_hit", hit)
        d.flinches.append(hit)
        return stack(hit)

    def blow(n):
        frozen = None
        for _ in range(n):
            t = c.t
            c.a("attack", tick(P["atk_dur"]))
            b = t + tick(P["a_hit"] - 1)
            c.on("a_hit", b)
            d.flinches.append(b)
            f = stack(b)
            frozen = frozen or f
        return frozen

    # out of combat: the Frost Armour on her as she rides in
    c.wait(300)
    xa = me.pos(c.t)[0]
    t0 = c.t
    run_to = far - 70
    t1 = t0 + abs(run_to - xa) / px_ms(P["ms"])
    c.a("run", t1 - t0, loop=True)
    me.moves.append((t0, t1, xa, run_to))
    # Arctic Assault into him, stopping on him (the add-on); Q -> W at once
    fight["from"] = c.t
    charge(far - 24)
    wrath()
    # her flail brings the Frost to four: frozen (W -> freeze); the next blow shatters him (stun -> shatter)
    frozen = blow(2)
    if frozen is None:
        frozen = blow(1)
    t = c.t
    c.a("attack", tick(P["atk_dur"]))
    b = t + tick(P["a_hit"] - 1)
    c.on("a_hit", b)
    c.on("sh_hit", b + tick(1))
    d.flinches.append(b)
    # she backs off; Glacial Prison: the bola, the prison held while he is stunned, the ice storm round him
    c.wait(200)
    xb = me.pos(c.t)[0]
    me.moves.append((c.t, c.t + 500, xb, xb - 60))
    c.a("run", 500, loop=True)
    t = c.t
    c.a("ult", tick(P["r_dur"]))
    rel = t + tick(P["r_rel"] - 1)
    xs = me.pos(rel)[0]
    reach = rel + abs(d.pos(rel)[0] - xs) / px_ms(P["r_speed"])
    c.fly("r_bola", rel, reach, xs, d.pos(rel)[0], gy - 12)
    c.on_foe("r_hit", reach, until=reach + tick(P["r_stun"]))
    c.at("r_storm", reach, d.pos(reach)[0], gy, sheet=big, under=True, until=reach + tick(P["r_storm"]))
    c.on_foe("slow", reach, until=reach + tick(P["r_storm"]), under=True)
    # R -> Q: Arctic Assault back at once, at the frozen one
    c.t = max(c.t, reach + tick(2))
    charge(far - 24)
    c.wait(200)
    blow(1)
    d.death = c.t + 40
    c.wait(1500)
    end = c.t
    c.on_me("fa_armour", 0, until=fight["from"] + tick(P["fa_keep"]))
    return c.render(out, W, H, end, z)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    ap.add_argument("--only", choices=["frames", "effects", "showcase"])
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    if args.only in (None, "frames"):
        s = load(CHAMP)
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_sejuani_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[15:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_sejuani_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_sejuani_showcase.gif")))


if __name__ == "__main__":
    main()
