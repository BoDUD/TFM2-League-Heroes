#!/usr/bin/env python3
"""Preview images for Powder (the tft pack), built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_powder.py [--out docs/preview] [--only frames|effects|showcase]

  tft_powder_frames.png    every animation's dense frames (hd_, PPU 1.75, as league.dll shows them)
  tft_powder_effects.png   every effect animation, 3x
  tft_powder_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_powder.py, 60 ticks a
                           second): a firecracker; the Monkey Bomb lobbed onto him - the blast, the burning hit, the
                           burn-and-wound mark; he closes in and Run, Powder! - the flash-smoke bomb at her feet, his
                           blinding, her hop back; the Hex Crystal Bomb - the glint as she winds up, the bag lobbed with
                           the warning ring under it, the fizzing fuse, the blue blast knocking him up; 3x
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
from preview_ashe import tick  # noqa: E402
from preview_dense import dense_rows  # noqa: E402
from preview_garen import T, contact, load  # noqa: E402
from preview_kindred import fx_contact  # noqa: E402
from preview_leesin import Foe  # noqa: E402
from preview_pyke import Me  # noqa: E402
import preview_zoe as Z  # noqa: E402
from build_powder import P  # noqa: E402

ROOT = Z.ROOT
TFT = os.path.join(ROOT, "tft")
CHAMP = os.path.join(TFT, "champions", "tft_powder")
FX = {n: os.path.join(TFT, "effects", n) for n in ("tft_powder_fx", "tft_powder_big")}
DARIUS = os.path.join(ROOT, "league", "champions", "league_darius")


class Clip(Z.Clip):
    def a(self, tag, dur=None, loop=False, z=3):
        from preview_ashe import Anim
        from preview_dense import dense
        fr = list(dense(self.sp, tag, "powder", z))
        if dur and not loop and dur > sum(ms for _, ms in fr):
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an


def showcase(out, z=3):
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["tft_powder_fx"], fx["tft_powder_big"]
    W, H = 250, 110
    gy = 86
    x0 = 90
    fx_ = x0 + 70                                       # Darius in her attack range
    d = Foe(load(DARIUS), fx_, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.wait(400)
    # a firecracker
    rel = c.t + tick(P["a_rel"])
    c.shot("a_pop", "a_hit", rel, P["a_speed"])
    c.a("attack", tick(P["atk_dur"]))
    c.wait(300)
    # Monkey Bomb lobbed at his feet: the blast, the burn and the wound
    rel = c.t + tick(P["q_rel"] - 1)
    land = rel + tick(P["q_travel"])
    c.fly("q_monkey", rel, land, me.pos(rel)[0] + 4, fx_, gy - 18)
    c.at_spot("q_blast", land, fx_, gy, under=False)
    c.on("q_hit", land)
    c.on("q_wound", land + 100, until=land + tick(P["q_wound_t"]))
    d.flinches.append(land)
    c.a("skill", tick(P["q_dur"]))
    c.wait(500)
    # he closes in: Run, Powder! - the smoke at her feet, his blinding, her hop back
    t_in = c.t
    d.slides.append((t_in, t_in + 300, -(fx_ - x0 - 20)))
    c.wait(300)
    rel = c.t + tick(P["e_rel"] - 1)
    c.on_me("e_smoke", rel, sheet=big)
    c.on("e_blind", rel, until=rel + tick(P["e_blind"]))
    me.moves.append((rel, rel + tick(P["e_hop_t"]), x0, x0 - P["e_hop"] * P["e_hop_t"] / 1000.0))
    c.a("skill2", tick(P["e_dur"]))
    c.wait(600)
    # The Hex Crystal Bomb: the glint, the bag lobbed over the warning ring, the fuse, the blue blast
    spot = d.pos(c.t)[0]
    c.on_me("r_cast", c.t)
    rel = c.t + tick(P["r_rel"] - 1)
    land = rel + tick(P["r_travel"])
    c.fly("r_bag", rel, land, me.pos(rel)[0] + 4, spot, gy - 18)
    c.at_spot("r_warn", rel, spot, gy)
    for k in range(0, P["r_fuse"], P["r_show"]):
        c.at_spot("r_fuse", land + tick(k), spot, gy, sheet=small)
    boom = land + tick(P["r_fuse"])
    c.at_spot("r_blast", boom, spot, gy, under=False)
    c.on("r_hit", boom)
    d.hops.append((boom, boom + tick(P["r_up"]), 14))
    c.a("ult", tick(P["r_dur"]))
    d.death = boom + tick(P["r_up"]) + 200
    end = d.death + 1400
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "tft_powder_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[11:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "tft_powder_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "tft_powder_showcase.gif")))


if __name__ == "__main__":
    main()
