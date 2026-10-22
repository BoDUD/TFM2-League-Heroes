#!/usr/bin/env python3
"""Preview images for Hwei, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_hwei.py [--out docs/preview] [--only frames|effects|showcase]

  league_hwei_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_hwei_effects.png   every effect animation, 3x
  league_hwei_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_hwei.py, 60 ticks a
                            second): Subject: Torment from afar - Gaze of the Abyss (the eye opening over him, its beam
                            rooting him) with Serenity's pool under Hwei, the signature's seal under Darius; at once
                            Severing Bolt on the rooted champion (the combo 悚 -> 灾: the gathering cloud, the gold bolt)
                            and the signature bursting; two flicks of ink; Spiraling Despair (the paint flung, the
                            canvas spreading under him and slowing him, a new seal) and Devastating Fire at once (the
                            combo R -> 灾: the fireball bursting the signature again), the canvas bursting - he falls; 3x.
                            A seal stays its whole sig_t as in the game (the data cannot take a buff off him), until he
                            dies.
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
from build_hwei import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_hwei")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_hwei_fx", "league_hwei_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")


class Hwei(Clip):
    """preview_gnar's clip with his own dense frames."""

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "hwei", z))
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


def px_ms(speed):
    """A projectile's speed (distance units a tick) in game px a ms."""
    return speed / 1000.0 * 60 / 1000


def showcase(out, z=3):
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_hwei_fx"], fx["league_hwei_big"]
    W, H = 240, 120
    gy = 100
    x0 = 92
    far = x0 + 52                                       # in his attack's reach (55 game px)
    shot_y = gy - 11 + P["a_y"] / 1000.0                # a projectile's height (the pivot 11 over the soles, y_offset)
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Hwei(load(CHAMP), d, me, small, big)
    c.wait(400)
    signed = {"until": None}
    seals = []

    def sign(when):
        """The signature: a champion hit signs him (the seal under him); a second hit bursts it sig_at ticks later."""
        if signed["until"] is not None and when < signed["until"]:
            c.on("p_burst", when + tick(P["sig_at"]), sheet=big)
            c.d.flinches.append(when + tick(P["sig_at"]))
            signed["until"] = None
            return
        signed["until"] = when + tick(P["sig_t"])
        c.on("p_mark", when, until=signed["until"])
        seals.append(c.over[-1])

    # Subject: Torment from afar - Gaze of the Abyss: the eye opens over him, the gaze roots him; Serenity's pool
    t = c.t
    c.on_me("w_pool", t, sheet=big, under=True)
    c.a("skill2", tick(P["e_dur"]))
    rel = t + tick(P["e_rel"] - 1)
    arrive = rel + (far - x0) / px_ms(20000)
    c.on("e_w_open", arrive, until=arrive + tick(P["e_w_setup"]))
    hit = arrive + tick(P["e_w_setup"])
    c.on("e_w_hit", hit)
    c.on("e_bound", hit, until=hit + tick(P["e_root"]))
    c.d.flinches.append(hit)
    sign(hit)
    # 悚 -> 灾: Severing Bolt on the rooted champion at once - the gathering cloud, the gold bolt; the signature bursts
    bolt = hit + tick(P["eq_gap"])
    c.on("q_w_tell", bolt, until=bolt + tick(P["q_w_at"]))
    strike = bolt + tick(P["q_w_at"])
    c.on("q_w_hit", strike, sheet=big)
    c.d.flinches.append(strike)
    sign(strike)
    # two flicks of ink
    c.wait(max(0, strike - 300 - c.t))
    for _ in range(2):
        t = c.t
        c.a("attack", tick(P["atk_dur"]))
        rel = t + tick(P["a_rel"] - 1)
        land = rel + (far - x0) / px_ms(P["a_speed"])
        c.fly("a_ink", rel, land, x0 + 8, far - 4, shot_y)
        c.on("a_hit", land)
        c.d.flinches.append(land)
        c.wait(tick(P["atk_cd"] - P["atk_dur"]) // 2)
    # Spiraling Despair: the paint flung at him, the canvas spreading under him, slowing him; R -> 灾: Devastating Fire
    t = c.t
    c.a("ult", tick(P["r_dur"]))
    rel = t + tick(P["r_rel"] - 1)
    hit = rel + (far - x0) / px_ms(P["r_speed"])
    c.fly("r_paint", rel, hit, x0 + 8, far - 4, shot_y)
    c.on("r_canvas", hit, sheet=big, until=hit + tick(P["r_t"]))
    c.on("slow", hit, until=hit + tick(P["r_t"]))
    sign(hit)
    go = hit + tick(P["r_q_gap"])
    land = go + (far - x0) / px_ms(P["q_q_speed"])
    c.fly("q_q_ball", go, land, x0 + 8, far - 4, shot_y)
    c.on("q_q_hit", land)
    c.d.flinches.append(land)
    sign(land)
    burst = hit + tick(P["r_t"])
    c.on("r_burst", burst, sheet=big)
    c.on("r_hit", burst)
    d.death = burst + 150
    for s in seals:                                     # his buffs go with him
        s.until = min(s.until, d.death)
    end = burst + 1600
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_hwei_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[12:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_hwei_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_hwei_showcase.gif")))


if __name__ == "__main__":
    main()
