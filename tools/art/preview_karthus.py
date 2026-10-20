#!/usr/bin/env python3
"""Preview images for Karthus, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_karthus.py [--out docs/preview] [--only frames|effects|showcase]

  league_karthus_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_karthus_effects.png   every effect animation, 3x
  league_karthus_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_karthus.py, 60
                               ticks a second): a soul bolt; Lay Waste - the warning circle on Darius's spot, the blast,
                               doubled on him alone; Wall of Pain in the attack - the wall on him, the grasping hands and
                               the cracked shield; Defile - the soul vortex under him burning Darius; Requiem - he rises
                               and sings 3 s, the souls round him, the beam on Darius; 3x
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
from build_karthus import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_karthus")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_karthus_fx", "league_karthus_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")


class Clip:
    """One scripted clip: his body's animations one after another, effects under / over the units, Darius."""

    def __init__(self, sp, d, me, small, big):
        self.sp, self.d, self.me, self.small, self.big = sp, d, me, small, big
        self.body, self.under, self.over, self.t = [], [], [], 0.0

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "karthus", z))
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

    def at_spot(self, tag, when, x, y, sheet=None, under=True):
        an = Anim(frames_of(sheet or self.big, tag), when, int(x), int(y))
        (self.under if under else self.over).append(an)

    def fly(self, tag, t0, t1, x0, x1, y, sheet=None):
        """A projectile's picture flying in a straight line (drawn going right: these fly right)."""
        self.over.append(Anim(frames_of(sheet or self.small, tag), t0, int(x0), int(y), loop=True, until=t1,
                              x1=int(x1), y1=int(y)))

    def shot(self, tag, hit_tag, rel, speed, fly_tag=None):
        """A projectile from his staff's crystal (held level at his shoulder) to Darius at `speed` (game units a tick),
        its hit on him."""
        x0, x1 = self.me.pos(rel)[0] + 22, self.d.pos(rel)[0]
        hit = rel + tick(max(1.0, (x1 - x0) * 1000.0 / speed))
        self.fly(fly_tag or tag, rel, hit, x0, x1, self.me.y - 22)
        self.on(hit_tag, hit)
        self.d.flinches.append(hit)
        return hit

    def attack(self):
        rel = self.t + tick(P["a_rel"])
        hit = self.shot("a_bolt", "a_hit", rel, P["a_speed"])
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
    small, big = fx["league_karthus_fx"], fx["league_karthus_big"]
    W, H = 200, 120
    gy = 98
    x0 = 60
    fx_ = x0 + 44                                       # Darius in his reach (and in Defile's ring)
    d = Foe(load(DARIUS), fx_, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.wait(400)
    c.attack()
    # Q Lay Waste: the warning circle on Darius's spot for the lob's flight, then the blast - him alone: doubled
    rel = c.t + tick(P["q_rel"] - 1)
    boom = rel + tick(P["q_delay"])
    c.at_spot("q_mark", rel, fx_, gy)
    c.at_spot("q_boom", boom, fx_, gy, under=False)
    c.on("q_hit", boom)
    c.on("q_lone", boom + tick(1))
    d.flinches.append(boom)
    c.a("skill", tick(P["q_dur"]))
    c.wait(boom - c.t + 300)
    # W Wall of Pain in the attack: the wall on him, the hands at his feet and the cracked shield over his head
    wall = c.t + tick(P["w_rel"] - 1)
    c.at_spot("w_wall", wall, fx_, gy)
    c.on("w_slow", wall, until=wall + tick(P["w_slow_t"] + 60))
    c.on("w_shred", wall, until=wall + tick(P["w_mr_t"]))
    c.shot("a_bolt", "a_hit", wall, P["a_speed"])
    c.a("attack_w", tick(P["w_dur"]))
    c.wait(tick(P["atk_cd"] - P["w_dur"]))
    # E Defile: the vortex under him for e_t, a burn on Darius every e_per
    on = c.t + tick(P["e_rel"] - 1)
    c.on_me("e_on", on, big, until=on + tick(P["e_t"]), under=True)
    for k in range(P["e_per"], P["e_t"] + 1, P["e_per"] * 2):
        c.on("e_hit", on + tick(k))
        d.flinches.append(on + tick(k))
    c.a("skill2", tick(P["e_dur"]))
    c.attack()
    c.wait(on + tick(P["e_t"]) - c.t)
    # R Requiem: he rises and sings (the souls round him) for r_ch, then the beam falls on Darius
    cast = c.t + tick(P["r_rel"])
    c.on_me("r_cast", cast, big, under=True)
    toll = c.t + tick(P["r_ch"])
    c.on("r_hit", toll, big)
    d.flinches.append(toll)
    d.death = toll + 200
    c.a("ult", tick(P["r_ch"] + 6))
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_karthus_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[15:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_karthus_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_karthus_showcase.gif")))


if __name__ == "__main__":
    main()
