#!/usr/bin/env python3
"""Preview images for Ziggs, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_ziggs.py [--out docs/preview] [--only frames|effects|showcase]

  league_ziggs_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_ziggs_effects.png   every effect animation, 3x
  league_ziggs_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_ziggs.py, 60 ticks a
                             second): Q - the bomb hops along the line (its stamps at build_ziggs.air_heights), the first
                             landing too far from him bounces, the second blows up on him; E - the minefield lands on
                             his spot (it lies e_t ticks), he steps on a mine (the first whole, slowed) and walks in
                             through it; W - he closes in, the satchel goes off at Ziggs's feet: Darius knocked back, Ziggs
                             blown away; a Short Fuse attack; R - the big bomb over his head, the red warning on Darius's
                             spot for the flight, the blast; 3x
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
from build_ziggs import P, air_heights  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_ziggs")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_ziggs_fx", "league_ziggs_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")


class Walker(Foe):
    """Darius walking toward Ziggs (mirrored run) while `walks` (t0, t1) lasts."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.walks = []

    def frame(self, t):
        if self.death is None or t < self.death:
            for t0, t1 in self.walks:
                if t0 <= t < t1:
                    return self.flip(self.pick(self.run, (t - t0) % sum(ms for _, ms in self.run)))
        return super().frame(t)


class Clip:
    """One scripted clip: his body's animations one after another, effects under / over the units, Darius."""

    def __init__(self, sp, d, me, small, big):
        self.sp, self.d, self.me, self.small, self.big = sp, d, me, small, big
        self.body, self.under, self.over, self.t = [], [], [], 0.0

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "ziggs", z))
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

    def on_me(self, tag, when, sheet=None, until=None):
        self.over.append(OnMe(frames_of(sheet or self.small, tag), when, self.me, until=until))

    def at_spot(self, tag, when, x, y, sheet=None, under=True):
        an = Anim(frames_of(sheet or self.big, tag), when, int(x), int(y))
        (self.under if under else self.over).append(an)

    def fly(self, tag, t0, t1, x0, x1, y, sheet=None):
        """A projectile's picture flying in a straight line (drawn going right: these fly right)."""
        self.over.append(Anim(frames_of(sheet or self.small, tag), t0, int(x0), int(y), loop=True, until=t1,
                              x1=int(x1), y1=int(y)))

    def attack(self, fuse=False):
        rel = self.t + tick(P["a_rel"])
        x0, x1 = self.me.pos(rel)[0] + 4, self.d.pos(rel)[0]
        hit = rel + tick((x1 - x0) * 1000.0 / P["a_speed"])
        self.fly("p_bomb" if fuse else "a_bomb", rel, hit, x0, x1, self.me.y - 14)
        self.on("p_hit" if fuse else "a_hit", hit)
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
    small, big = fx["league_ziggs_fx"], fx["league_ziggs_big"]
    W, H = 300, 120
    gy = 84
    x0 = 70
    fx_ = x0 + 64                                       # Darius past Q's first landing (40), on its second (62)
    d = Walker(load(DARIUS), fx_, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.wait(400)
    # Q: the hops' stamps along the line, the first landing too far from him (a bounce), the second on him
    rel = c.t + tick(P["q_rel"] - 1)
    for k, dist, t_, h in air_heights(P):
        if k > 2:
            break
        hh = min(h, 18) // 2 * 2
        c.over.append(Anim(frames_of(small, f"q_air{hh}"), rel + tick(t_), x0 + dist / 1000.0, gy))
    land1 = rel + tick(P["q_t1"])
    c.at_spot("q_bounce", land1, x0 + P["q_l1"] / 1000.0, gy, sheet=small, under=False)
    land2 = rel + tick(P["q_t1"] + P["q_t2"])
    c.at_spot("q_blast", land2 + tick(2), x0 + P["q_l2"] / 1000.0, gy, under=False)
    c.on("q_hit", land2 + tick(1))
    d.flinches.append(land2 + tick(1))
    c.a("skill", tick(P["q_dur"]))
    c.wait(land2 + 300 - c.t)
    # E: the mines lobbed onto his spot, lying e_t ticks; armed after e_arm: his first mine whole, slowed
    rel = c.t + tick(P["e_rel"] - 1)
    land = rel + tick(P["e_travel"])
    c.fly("e_throw", rel, land, x0 + 4, fx_, gy - 14)
    c.at_spot("e_land", land, fx_, gy)
    for k in range(0, P["e_t"], P["e_show"]):
        c.at_spot("e_field", land + tick(k), fx_, gy)
    armed = land + tick(P["e_arm"])
    c.on("e_hit", armed)
    c.on("e_slow", armed + tick(1), until=armed + tick(P["e_slow_t"]))
    d.flinches.append(armed)
    c.a("skill2", tick(P["e_dur"]))
    # he walks in through the field (slowed: half a pixel a tick), a second mine on the way
    w0, close = armed + 200, x0 + P["w_trig"] / 1000.0 + 4
    w1 = w0 + tick((fx_ - close) * 2)
    d.walks.append((w0, w1))
    d.slides.append((w0, w1, close - fx_))
    c.on("e_hit", w0 + tick(P["e_p"]))
    c.wait(w1 - c.t)
    # W: he is within w_trig - the watch sets the satchel off at Ziggs's feet: Darius knocked back, Ziggs blown away
    blast = c.t + tick(P["w_rel"] - 1)
    c.at_spot("w_blast", blast, x0, gy, under=False)
    c.on("w_hit", blast + tick(1))
    d.flinches.append(blast + tick(1))
    kb = P["w_kb"] * P["w_kb_t"] / 1000.0
    d.slides.append((blast + tick(1), blast + tick(1 + P["w_kb_t"]), kb))
    hop = P["w_hop"] * P["w_hop_t"] / 1000.0
    me.moves.append((blast + tick(1), blast + tick(1 + P["w_hop_t"]), x0, x0 - hop))
    c.a("skill_w", tick(P["w_dur"]))
    c.wait(200)
    # a Short Fuse attack from where he landed
    c.attack(fuse=True)
    # R: the big bomb over his head, the warning on Darius's spot for the flight, the blast
    c.wait(200)
    start = c.t
    c.on_me("r_cast", start, big)
    rel = start + tick(P["r_rel"] - 1)
    spot = d.pos(rel)[0]
    boom = rel + tick(P["r_travel"])
    c.at_spot("r_warn", rel, spot, gy)
    c.fly("r_bomb", rel, boom, me.pos(rel)[0] + 4, spot, gy - 30, sheet=big)
    c.at_spot("r_boom", boom, spot, gy, under=False)
    c.on("r_hit", boom + tick(1))
    d.death = boom + tick(2)
    c.a("ult", tick(P["r_dur"]))
    end = boom + 1400
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_ziggs_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_ziggs_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_ziggs_showcase.gif")))


if __name__ == "__main__":
    main()
