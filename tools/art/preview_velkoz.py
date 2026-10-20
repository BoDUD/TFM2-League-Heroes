#!/usr/bin/env python3
"""Preview images for Vel'Koz, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_velkoz.py [--out docs/preview] [--only frames|effects|showcase]

  league_velkoz_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_velkoz_effects.png   every effect animation, 3x
  league_velkoz_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_velkoz.py, 60 ticks a
                              second): two void bolts from his eye, the third tearing a Void Rift that bursts; Plasma
                              Fission - the plasma orb strikes him and splits up and down, slowing him (the research
                              mark's first segment lights); Tectonic Disruption - the ground cracks under him and erupts,
                              knocking him up (two segments); Life Form Disintegration Ray - the beam from the eye held on
                              him, its first wave bursting the research mark (true damage); 3x
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
from preview_pyke import Me, OnFoe  # noqa: E402
from preview_zyra import Walker  # noqa: E402
from build_velkoz import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_velkoz")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_velkoz_fx", "league_velkoz_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")
WALK = 0.9                      # Darius's walk, game px a tick
BOLT_LEAD = 2                   # ticks the bolts are hidden (import_velkoz_fx.py): they leave his pivot behind his eye
EYE_UP = (5000 - P["a_y"]) / 1000.0
BEAM_UP = (5000 - P["r_by"]) / 1000.0


class Clip:
    """One scripted clip: his body's animations one after another, effects under / over the units, Darius."""

    def __init__(self, sp, d, me, small, big):
        self.sp, self.d, self.me, self.small, self.big = sp, d, me, small, big
        self.body, self.under, self.over, self.t = [], [], [], 0.0
        self.stacks = 0

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "velkoz", z))
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

    def on(self, tag, when, sheet=None, until=None, under=False):
        (self.under if under else self.over).append(OnFoe(frames_of(sheet or self.small, tag), when, self.d,
                                                          until=until))

    def at_spot(self, tag, when, x, y, sheet=None, under=True):
        an = Anim(frames_of(sheet or self.big, tag), when, int(x), int(y))
        (self.under if under else self.over).append(an)

    def fly(self, tag, t0, t1, x0, x1, y0, y1=None, sheet=None, loop=True):
        """A projectile's picture moving in a straight line (drawn going right: these fly right)."""
        self.over.append(Anim(frames_of(sheet or self.small, tag), t0, int(x0), int(y0), loop=loop, until=t1,
                              x1=int(x1), y1=int(y0 if y1 is None else y1)))

    def mark(self, when):
        """A spell hit on him: the research mark's next segment, the third bursting."""
        self.stacks += 1
        if self.stacks == 3:
            self.stacks = 0
            self.on("p_full", when)
        else:
            self.on(f"p_s{self.stacks}", when)      # placed over the head by import_velkoz_fx (HEAD)

    def bolt(self, tag, speed, rel, sheet=None):
        """A bolt from his eye to Darius, its first ticks hidden; -> the tick (ms) it hits."""
        x0, x1 = self.me.pos(rel)[0], self.d.pos(rel)[0]
        step = speed / 1000.0
        hit = rel + tick((x1 - x0) / step)
        show = rel + tick(BOLT_LEAD)
        lift = EYE_UP * (1 - BOLT_LEAD * step / (x1 - x0))
        self.fly(tag, show, hit, x0 + BOLT_LEAD * step, x1, self.me.y - lift, self.d.y, sheet=sheet)
        return hit

    def attack(self, rift=False):
        rel = self.t + tick(P["a_rel"] - 1)
        hit = self.bolt("a_bolt", P["a_speed"], rel)
        self.on("a_hit", hit)
        self.d.flinches.append(hit)
        if rift:
            # the rift's picture on the line's middle (the pivots' line), its two bursts on Darius
            mid = self.me.pos(rel)[0] + P["w_len"] / 2000.0
            self.at_spot("w_rift", rel, mid, self.me.y, under=False)
            for k in ("w_ap1", "w_det"):
                ts = rel + tick(P[k] - 1)
                self.on("w_hit", ts)
                self.d.flinches.append(ts)
                self.mark(ts)
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
    small, big = fx["league_velkoz_fx"], fx["league_velkoz_big"]
    W, H = 250, 96
    gy = 62                                             # the pivot row
    x0 = 40
    xa = x0 + 70                                        # Darius at his reach, then walking in
    xb = xa - 18
    d = Walker(load(DARIUS), xa, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.wait(400)
    c.attack()
    c.attack()
    c.attack(rift=True)
    # Q Plasma Fission: the orb from his eye strikes him, splits up and down there, slows him
    rel = c.t + tick(P["q_rel"] - 1)
    hit = c.bolt("q_bolt", P["q_speed"], rel)
    c.on("q_hit", hit)
    c.at_spot("q_split", hit, d.pos(hit)[0], gy, under=False)   # on the struck point (import_velkoz_fx SPLIT)
    c.on("q_slow", hit, until=hit + tick(P["q_slow_t"]), under=True)
    d.flinches.append(hit)
    c.mark(hit)
    c.a("skill", tick(P["q_dur"]))
    # he walks in, slowed
    w0 = hit + 200
    w1 = w0 + tick((xa - xb) / (WALK / 2))
    d.walks.append((w0, w1, xb - xa))
    c.wait(w1 + 100 - c.t)
    # E Tectonic Disruption: the ground cracks under him, erupts e_delay ticks later, knocking him up
    rel = c.t + tick(P["e_rel"] - 1)
    c.at_spot("e_mark", rel, xb, gy)                   # on the ground under the point (import_velkoz_fx SOLES)
    boom = rel + tick(P["e_delay"])
    c.at_spot("e_boom", boom, xb, gy, under=False)
    c.on("e_hit", boom)
    d.hops.append((boom, boom + tick(P["e_air"]), 10))
    d.flinches.append(boom)
    c.mark(boom)
    c.a("skill2", tick(P["e_dur"]))
    c.wait(boom + tick(P["e_air"]) + 100 - c.t)
    # R Life Form Disintegration Ray: the wind-up, then the channel - a beam wave every r_p ticks from his eye, held on
    # Darius (each wave's projectile creeps 1 px a tick toward him), the first wave bursting the research mark
    start = c.t
    t0 = start + tick(P["r_rel"] - 1)
    waves = P["r_t"] // P["r_p"]
    beam = frames_of(big, "r_beam")
    for k in range(waves):
        ts = t0 + tick(k * P["r_p"])
        x, y = me.pos(ts)[0], gy - BEAM_UP
        c.over.append(Anim(beam, ts, int(x), int(y), until=ts + tick(P["r_p"] + 1), x1=int(x + P["r_p"] + 1),
                           y1=int(y)))
        c.on("r_hit", ts)
        d.flinches.append(ts)
        if k % P["r_mark"] == 0:
            c.mark(ts)
    c.a("ult", tick(P["r_anim"]))
    c.a("ult_loop", t0 + tick(P["r_t"]) - c.t, loop=True)
    d.death = t0 + tick(P["r_t"] - P["r_p"])
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_velkoz_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_velkoz_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_velkoz_showcase.gif")))


if __name__ == "__main__":
    main()
