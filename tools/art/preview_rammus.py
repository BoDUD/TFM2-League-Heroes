#!/usr/bin/env python3
"""Preview images for Rammus, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_rammus.py [--out docs/preview] [--only frames|effects|showcase]

  league_rammus_frames.png    every animation's dense frames (hd_, PPU 1.2, as league.dll shows them)
  league_rammus_effects.png   every effect animation, 3x
  league_rammus_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_rammus.py, 60 ticks a
                              second): Powerball - he curls up, rolls at him over the dust, the sand ring of the impact,
                              Darius knocked back and slowed; Defensive Ball Curl - the flare and the spiked shell;
                              Frenzying Taunt - the flare on him and the anger mark; two tumbling blows; Soaring Slam -
                              the leap as the ball, the crater and its aftershocks, the cracked ground at his feet; 3x
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
from build_rammus import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_rammus")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_rammus_fx", "league_rammus_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")


class Clip:
    """One scripted clip: his body's animations one after another, effects under / over the units, Darius."""

    def __init__(self, sp, d, me, small, big):
        self.sp, self.d, self.me, self.small, self.big = sp, d, me, small, big
        self.body, self.under, self.over, self.t = [], [], [], 0.0
        self.turned = False

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "rammus", z))
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

    def blow(self):
        """One tumble into him."""
        hit = self.t + tick(P["a_hit"])
        self.on("a_hit", hit)
        self.d.flinches.append(hit)
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
    small, big = fx["league_rammus_fx"], fx["league_rammus_big"]
    W, H = 220, 110
    gy = 88
    x0 = 40
    fx_ = 160                                           # Darius across the lane: room for the roll
    d = Foe(load(DARIUS), fx_, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.wait(400)
    # Powerball: he curls up, rolls at Darius over the dust (q_speed: 4 game px a tick), the impact
    c.a("skill", tick(P["q_curl"]))
    stop = fx_ - 30
    roll_t = tick((stop - x0) * 1000.0 / P["q_speed"])
    t0 = c.t
    me.moves.append((t0, t0 + roll_t, x0, stop))
    for k in range(0, int(roll_t) + 1, 400):
        c.on_me("q_dust", t0 + k, under=True)
    c.a("skill_roll", roll_t, loop=True)
    hit = c.t
    c.on_me("q_burst", hit, big, under=True)
    c.on("q_hit", hit)
    d.flinches.append(hit)
    kb = P["q_kb_speed"] * P["q_kb_t"] / 1000.0
    d.slides.append((hit, hit + tick(P["q_kb_t"]), kb))
    c.on("q_slow", hit, until=hit + tick(P["q_slow_t"]))
    c.a("skill_hit", tick(P["q_end"]))
    c.wait(200)
    # Defensive Ball Curl: the watch curls him up - the flare and the spiked shell
    c.on_me("w_cast", c.t, big)
    c.on_me("w_on", c.t, until=c.t + 2600)
    c.a("skill_w", tick(P["w_dur"]))
    c.wait(200)
    # Frenzying Taunt: the flare on him, the anger mark over his head
    tt = c.t + tick(P["e_rel"])
    c.on("e_hit", tt)
    c.on("e_taunt", tt, until=tt + tick(P["e_taunt"]))
    c.a("skill2", tick(P["e_dur"]))
    for _ in range(2):
        c.blow()
    # Soaring Slam: the leap as the ball onto him, the crater and its aftershocks, the cracked ground at his feet
    spot = fx_ + kb
    leap = c.t
    me.moves.append((leap, leap + tick(P["r_dur"]), stop, spot - 12))
    c.a("ult", tick(P["r_dur"]))
    land = c.t
    c.at_spot("r_land", land, spot, gy)
    c.on("r_hit", land)
    d.flinches.append(land)
    c.on("r_slow", land, until=land + tick(P["r_slow_t"]))
    for k in range(1, P["r_pulses"] + 1):
        c.at_spot("r_shock", land + tick(k * P["r_pp"]), spot, gy)
    c.a("ult_land", tick(P["r_end"]))
    d.death = land + tick(P["r_pulses"] * P["r_pp"]) + 200
    end = d.death + 1200
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_rammus_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_rammus_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_rammus_showcase.gif")))


if __name__ == "__main__":
    main()
