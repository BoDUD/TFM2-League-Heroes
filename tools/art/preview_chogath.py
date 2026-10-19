#!/usr/bin/env python3
"""Preview images for Cho'Gath, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_chogath.py [--out docs/preview] [--only frames|effects|showcase]

  league_chogath_frames.png    every animation's dense frames (hd_, PPU 1.2, as league.dll shows them)
  league_chogath_effects.png   every effect animation, 3x
  league_chogath_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_chogath.py, 60
                               ticks a second): Rupture - the ground cracks under Darius, the spikes burst out and
                               throw him up, the slow; Feral Scream - the cone of sound, the hit and the silence;
                               Vorpal Spikes - the spikes on his back light up, two attacks throw a volley through
                               Darius (the hit and the slow); Feast - the bite, Darius eaten and the void surge round
                               him; 3x
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
from build_chogath import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_chogath")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_chogath_fx", "league_chogath_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")
FLY = 8000 / 1000.0             # the homing blow and bite: 8 px a tick


class Clip:
    """One scripted clip: his body's animations one after another, effects under / over the units, Darius."""

    def __init__(self, sp, d, me, small, big):
        self.sp, self.d, self.me, self.small, self.big = sp, d, me, small, big
        self.body, self.under, self.over, self.t = [], [], [], 0.0
        self.turned = False

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "chogath", z))
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

    def at_spot(self, tag, when, x, y, sheet=None, under=True, until=None):
        an = Anim(frames_of(sheet or self.big, tag), when, int(x), int(y), loop=until is not None, until=until)
        (self.under if under else self.over).append(an)

    def flight(self):
        """Ticks the homing blow / bite takes from him to Darius."""
        return max(1, round(abs(self.d.x - self.me.x) / FLY))

    def blow(self, spiked=False):
        """One attack: the slam on Darius; spiked: the volley of Vorpal Spikes flies through him too (the hit, the
        slow), its picture on its line's middle."""
        start = self.t
        cast = start + tick((P["e_hit"] if spiked else P["a_hit"]) - 1)
        hit = cast + tick(self.flight())
        self.on("a_hit", hit)
        self.d.flinches.append(hit)
        if spiked:
            self.at_spot("e_pic", cast, self.me.x + P["e_len"] / 2000, self.me.y, self.small, under=False)
            self.on("e_hit", cast)
            self.on("e_slow", cast, until=cast + tick(P["e_slow_t"]))
            self.d.flinches.append(cast)
        self.a("attack_e" if spiked else "attack", tick(P["e_dur"] if spiked else P["atk_dur"]))
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
    small, big = fx["league_chogath_fx"], fx["league_chogath_big"]
    W, H = 220, 130
    gy = 100
    x0 = 66
    fx_ = x0 + 50                                       # Darius in his reach
    d = Foe(load(DARIUS), fx_, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.wait(400)
    # Rupture: the cracks on Darius's spot (q_rel), the spikes q_delay later: the hit, thrown up q_up, the slow
    crack = c.t + tick(P["q_rel"] - 1)
    burst = crack + tick(P["q_delay"])
    c.at_spot("q_crack", crack, fx_, gy, until=None)
    c.at_spot("q_spikes", burst, fx_, gy, under=False)
    c.on("q_hit", burst)
    c.on("q_slow", burst, until=burst + tick(P["q_slow_t"]))
    d.hops.append((burst, burst + tick(P["q_up"]), 12))
    d.flinches.append(burst)
    c.a("skill", tick(P["q_dur"]))
    c.wait(burst - c.t + 300)
    # Feral Scream: the cone from him (its line's picture on the line's middle), the hit and the silence
    scream = c.t + tick(P["w_rel"] - 1)
    c.at_spot("w_wave", scream, x0 + P["w_cone"] / 2000, gy, big, under=False)
    c.on("w_hit", scream)
    c.on("w_sil", scream, until=scream + tick(P["w_sil"]))
    d.flinches.append(scream)
    c.a("skill2", tick(P["w_dur"]))
    c.wait(300)
    # Vorpal Spikes: armed as the first attack starts (the spikes on his back light up), two spiked attacks
    c.on_me("e_arm", c.t)
    for _ in range(2):
        c.blow(spiked=True)
    # Feast: the bite flies at Darius (r_rel), eats him, the void surge round him a tick later
    bite = c.t + tick(P["r_rel"] - 1) + tick(c.flight())
    c.on("r_hit", bite, big)
    d.flinches.append(bite)
    d.death = bite + 120
    c.on_me("r_grow", bite + tick(1), big)
    c.a("ult", tick(P["r_dur"]))
    end = c.t + 1200
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_chogath_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[15:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_chogath_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_chogath_showcase.gif")))


if __name__ == "__main__":
    main()
