#!/usr/bin/env python3
"""Preview images for Volibear, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_volibear.py [--out docs/preview] [--only frames|effects|showcase]

  league_volibear_frames.png    every animation's dense frames (hd_, PPU 1.2, as league.dll shows them)
  league_volibear_effects.png   every effect animation, 3x
  league_volibear_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_volibear.py, 60
                                ticks a second): Thundering Smash - the charge on all fours crackling, the pounce, the
                                smash and the stun; Frenzied Maul - the bite marks him, the second bite heals; Sky
                                Splitter - the storm warning on his spot, the bolt from the sky, the hit and the slow;
                                five-stack attacks loosing lightning; Stormbringer - the leap, the landing quake, the hit
                                and the storm form; 3x
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
from preview_pyke import Me, OnFoe, OnMe, mirrored  # noqa: E402
from build_volibear import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_volibear")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_volibear_fx", "league_volibear_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")


class Clip:
    """One scripted clip: his body's animations one after another, effects under / over the units, Darius."""

    def __init__(self, sp, d, me, small, big):
        self.sp, self.d, self.me, self.small, self.big = sp, d, me, small, big
        self.body, self.under, self.over, self.t = [], [], [], 0.0
        self.turned = False

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "volibear", z))
        if self.turned:
            fr = mirrored(fr)
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

    def fly(self, tag, t0, t1, x0, x1, y, sheet=None):
        """A projectile's picture flying in a straight line (drawn going right: these fly right)."""
        self.over.append(Anim(frames_of(sheet or self.small, tag), t0, int(x0), int(y), loop=True, until=t1,
                              x1=int(x1), y1=int(y)))

    def at_spot(self, tag, when, x, y, sheet=None, under=True, until=None):
        an = Anim(frames_of(sheet or self.big, tag), when, int(x), int(y), loop=until is not None, until=until)
        (self.under if under else self.over).append(an)

    def blow(self, bolt=False):
        """One claw rake at him (bolt: the five-stack lightning flies from the claws to him)."""
        hit = self.t + tick(P["atk_st"])
        self.on("a_hit", hit)
        self.d.flinches.append(hit)
        if bolt:
            self.fly("p_bolt", hit, hit + 80, self.me.x + 10, self.d.x, self.d.y - 16)
            self.on("p_hit", hit + 80)
        self.a("attack", tick(P["atk_dur"]))
        self.wait(tick(P["atk_cd"] - P["atk_dur"]))

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
    small, big = fx["league_volibear_fx"], fx["league_volibear_big"]
    W, H = 220, 120
    gy = 98
    x0 = 70
    fx_ = x0 + 40                                       # Darius in his claws' reach
    d = Foe(load(DARIUS), fx_, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.wait(400)
    # Thundering Smash: the charge on all fours crackling, then the pounce: the smash (q_rel) and the stun
    run = 640
    c.on_me("q_ms", c.t, big, until=c.t + run + tick(P["q_dur"]), under=True)
    c.a("skill_run", run, loop=True)
    smash = c.t + tick(P["q_rel"])
    c.on("q_hit", smash)
    c.on("q_stun", smash, until=smash + tick(P["q_stun"]))
    d.flinches.append(smash)
    c.a("skill", tick(P["q_dur"]))
    c.wait(200)
    # Frenzied Maul: the bite marks him; the next maul (5 s later in a game) bites harder and heals him
    for second in (False, True):
        bite = c.t + tick(P["w_st"])
        c.on("w_hit", bite)
        d.flinches.append(bite)
        if second:
            c.on_me("w_heal", bite, big)
        else:
            c.on("w_mark", bite, until=bite + 1600)
        c.a("attack_w", tick(P["w_dur"]))
        c.wait(tick(P["atk_cd"] - P["w_dur"]))
    # Sky Splitter: the storm warning on his spot, the bolt from the sky e_delay later, the hit and the slow
    warn = c.t + tick(P["e_rel"])
    bolt = warn + tick(P["e_delay"])
    c.at_spot("e_cloud", warn, fx_, gy, until=bolt)
    c.at_spot("e_bolt", bolt, fx_, gy, under=False)
    c.on("e_hit", bolt)
    c.on("e_slow", bolt, until=bolt + tick(P["e_slow_t"]))
    d.flinches.append(bolt)
    c.a("skill2", tick(P["e_dur"]))
    c.wait(bolt - c.t + 200)
    # five stacks: two rakes loosing lightning
    for _ in range(2):
        c.blow(bolt=True)
    # Stormbringer: the leap (held in the air), the landing quake, the hit, the storm form round him
    c.a("ult", tick(P["r_up"]))
    land = c.t + tick(P["r_rel"])
    c.on_me("r_land", land, big, under=True)
    c.on("r_hit", land)
    d.flinches.append(land)
    c.on_me("r_form", land, big, until=land + 1800, under=True)
    c.a("ult_land", tick(P["r_land_t"]))
    d.death = land + 400
    end = c.t + 1600
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_volibear_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[16:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_volibear_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_volibear_showcase.gif")))


if __name__ == "__main__":
    main()
