#!/usr/bin/env python3
"""Preview images for Warwick, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_warwick.py [--out docs/preview] [--only frames|effects|showcase]

  league_warwick_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_warwick_effects.png   every effect animation, 3x
  league_warwick_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_warwick.py, 60 ticks
                               a second): two claw swipes with Blood Hunt's red scent under him; Jaws of the Beast -
                               reared back, the leap onto Darius, the bite and the blood heal; Primal Howl - the guard
                               shell, then the howl's shockwave and sound waves, Darius afraid; Infinite Duress - the
                               coil, the leap, pinned in the blood shackles, three claws with a heal each; 3x
"""
import argparse
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
from preview_ashe import Anim, tick  # noqa: E402
from preview_dense import dense, dense_rows, put  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_kindred import fx_contact  # noqa: E402
from preview_leesin import Foe  # noqa: E402
from preview_pyke import Me, OnFoe, OnMe  # noqa: E402
from build_warwick import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_warwick")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_warwick_fx", "league_warwick_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")


class Clip:
    """One scripted clip: his body's animations one after another, effects under / over the units, Darius."""

    def __init__(self, sp, d, me, small, big):
        self.sp, self.d, self.me, self.small, self.big = sp, d, me, small, big
        self.body, self.under, self.over, self.t = [], [], [], 0.0

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "warwick", z))
        if dur and not loop and dur > sum(ms for _, ms in fr):     # the last frame held to the action's end
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an

    def wait(self, ms):
        if ms > 0:
            self.a("idle", ms, loop=True)

    def on(self, tag, when, sheet=None, until=None):
        self.over.append(OnFoe(frames_of(sheet or self.small, tag), when, self.d, until=until))

    def on_me(self, tag, when, sheet=None, until=None, under=False):
        (self.under if under else self.over).append(OnMe(frames_of(sheet or self.small, tag), when, self.me, until=until))

    def attack(self):
        hit = self.t + tick(P["a_hit"])
        self.on("a_hit", hit)
        self.d.flinches.append(hit)
        self.a("attack", tick(P["atk_dur"]))
        self.wait(tick(P["atk_cd"] - P["atk_dur"]))
        return hit

    def render(self, out, W, H, end, z=3, step=40):
        frames, tt = [], 0.0
        while tt < end:
            img = Image.new("RGBA", (W * z, H * z), ARENA)
            for an in self.under:
                f = an.frame(tt)
                if f is not None:
                    put(img, f, *an.pos(tt), z)
            units = [(self.d.y, self.d.frame(tt), self.d.pos(tt))]
            for an in self.body:
                f = an.frame(tt)
                if f is not None:
                    units.append((self.me.y + 0.5, f, an.pos(tt)))
                    break
            for _, f, p in sorted(units, key=lambda u: u[0]):
                if f is not None:
                    put(img, f, *p, z)
            for an in self.over:
                f = an.frame(tt)
                if f is not None:
                    put(img, f, *an.pos(tt), z)
            frames.append(img.convert("RGB"))
            tt += step
        sample = frames[::6]
        strip = Image.new("RGB", (W * z, H * z * len(sample)))
        for i, f in enumerate(sample):
            strip.paste(f, (0, i * H * z))
        pal = strip.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        q_ = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
        q_[0].save(T.long_path(out), save_all=True, append_images=q_[1:], duration=step, loop=0)
        return len(frames), round(end / 1000.0, 1)


def showcase(out, z=3):
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_warwick_fx"], fx["league_warwick_big"]
    W, H = 260, 120
    gy = 96
    x0 = 70
    fx_ = x0 + 62                                       # Darius in claw reach (25 px plus the two bodies)
    d = Foe(load(DARIUS), fx_, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.wait(400)
    # two claw swipes; Blood Hunt's scent under him while he hunts
    c.on_me("w_hunt", c.t, until=c.t + 2400, under=True)
    c.attack()
    c.attack()
    # Q Jaws of the Beast: from a step back, reared, the leap onto Darius, the bite with the blood heal
    back = x0 - 30
    me.moves.append((c.t, c.t + 200, x0, back))
    c.wait(400)
    go = c.t + tick(P["q_at"])
    arrive = c.t + tick(P["q_bite"])
    me.moves.append((go, arrive, back, x0))
    c.a("skill", tick(P["q_bite"]))
    bite = c.t
    c.on("q_hit", bite)
    c.on_me("q_heal", bite)
    c.d.flinches.append(bite)
    c.a("skill_bite", tick(P["q_dur"] - P["q_bite"]))
    c.wait(300)
    # E Primal Howl: the guard shell, then the howl - the shockwave under him, the sound waves over his head, Darius afraid
    c.a("skill2", tick(P["e_dur"]))
    guard = c.t - tick(P["e_dur"] - P["e_at"])
    c.on_me("e_guard", guard, sheet=big, until=guard + 1100)
    c.wait(guard + 1100 - c.t)
    howl = c.t
    c.on_me("e_howl", howl, sheet=big, under=True)
    c.on_me("e_roar", howl)
    c.on("e_fear", howl + 60, until=howl + 60 + tick(P["e_fear"]))
    c.a("skill2_howl", tick(P["e_howl"]))
    c.wait(500)
    # R Infinite Duress: from further back, the coil, the leap onto Darius, pinned in the shackles, three claws
    back = x0 - 50
    me.moves.append((c.t, c.t + 200, x0, back))
    c.wait(400)
    c.a("ult", tick(P["r_at"]) + 120)
    go = c.t
    arrive = go + tick(P["r_range"] / 1000.0 * 0 + 12)
    me.moves.append((go, arrive, back, x0))
    c.on("r_bind", go, until=go + tick(P["r_sup"]) + 200)
    c.a("ult_dash", arrive - go)
    for k in range(3):
        claw = c.t + tick(k * P["r_gap"] + 1)
        c.on("r_hit", claw)
        c.on_me("q_heal", claw)
        c.d.flinches.append(claw)
    c.a("ult_hold", tick(P["r_sup"]))
    d.death = c.t - 200
    end = d.death + 1500
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_warwick_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[15:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_warwick_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_warwick_showcase.gif")))


if __name__ == "__main__":
    main()
