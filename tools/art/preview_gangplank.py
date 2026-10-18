#!/usr/bin/env python3
"""Preview images for Gangplank, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_gangplank.py [--out docs/preview] [--only frames|effects|showcase]

  league_gangplank_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_gangplank_effects.png   every effect animation, 3x
  league_gangplank_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_gangplank.py, 60
                                 ticks a second): E - a keg lobbed onto Darius's spot, re-stamped every e_link ticks,
                                 its fuse lit e_arm ticks after it lands; Q - the shot (the muzzle flash is in his
                                 frames) hits Darius and the lit keg beside him blows: the blast, Trial by Fire's burn,
                                 the slow; Darius walks in (slowed); W - the orange (in his frames), crowd-control
                                 immunity under him; two cutlass slashes; R - the flare (in his frames), the warning on
                                 Darius's spot for the call, then the barrage's waves; 3x
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
from build_gangplank import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_gangplank")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_gangplank_fx", "league_gangplank_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")


class Walker(Foe):
    """Darius walking toward Gangplank (mirrored run) while `walks` (t0, t1) lasts."""

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
        fr = list(dense(self.sp, tag, "gangplank", z))
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

    def attack(self, fire=False):
        hit = self.t + tick(P["a_hit"])
        self.on("a_hit", hit)
        if fire:
            self.on("p_hit", hit)
            self.on_me("p_ms", hit, until=hit + tick(P["p_ms_t"]))
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
    small, big = fx["league_gangplank_fx"], fx["league_gangplank_big"]
    W, H = 260, 120
    gy = 84
    x0 = 70
    fx_ = x0 + 56                                       # Darius in Q's reach
    d = Walker(load(DARIUS), fx_, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.wait(400)
    # E: the keg lobbed onto Darius's spot, its pictures re-stamped every e_link ticks, lit after e_arm
    rel = c.t + tick(P["e_rel"] - 1)
    land = rel + tick(P["e_travel"])
    keg = fx_ - 4
    c.fly("e_throw", rel, land, x0 + 4, keg, gy - 14)
    c.at_spot("e_land", land, keg, gy, sheet=small)
    c.a("skill2", tick(P["e_dur"]))
    lit = land + tick(P["e_arm"])
    shot = lit + 200                                    # Q a little after the fuse is lit
    rel_q = shot - tick(P["q_rel"] - 1)
    c.wait(rel_q - c.t)
    hit = shot + tick((fx_ - x0 - 21) * 1000.0 / P["q_speed"]) + tick(1)
    k = 0
    while land + tick(k) < hit:
        c.at_spot("e_keg_lit" if land + tick(k) >= lit else "e_keg", land + tick(k), keg, gy, sheet=small,
                  under=False)
        k += P["e_link"]
    # Q: the bullet from the muzzle; the hit sets off the lit keg beside him
    c.fly("q_bullet", shot, hit, x0 + 21, fx_, gy - 16)
    c.on("q_hit", hit)
    c.on("p_hit", hit)
    c.on_me("p_ms", hit, until=hit + tick(P["p_ms_t"]))
    c.at_spot("e_boom", hit + tick(1), keg, gy, under=False)
    c.on("e_hit", hit + tick(1))
    c.on("e_slow", hit + tick(2), until=hit + tick(P["e_slow_t"]))
    d.flinches += [hit, hit + tick(1)]
    c.a("skill", tick(P["q_dur"]))
    # he walks in, slowed, to the cutlass's reach
    w0, close = hit + 300, x0 + P["atk_range"] / 1000.0 + 4
    w1 = w0 + tick((fx_ - close) * 2)
    d.walks.append((w0, w1))
    d.slides.append((w0, w1, close - fx_))
    c.wait(w1 - c.t)
    # W: the orange (drawn in his frames 2 ticks after the decision), crowd-control immunity under him
    eat = c.t + tick(2)
    c.wait(tick(2))
    c.on_me("w_imm", eat, until=eat + tick(P["w_imm"]))
    c.a("skill_w", tick(P["w_dur"]))
    c.wait(150)
    c.attack()
    c.attack()
    # R: the flare (in his frames), the warning on Darius's spot for the call, then the waves
    start = c.t
    rel = start + tick(P["r_rel"] - 1)
    spot = d.pos(rel)[0]
    call = rel + tick(P["r_call"])
    c.at_spot("r_warn", rel, spot, gy)
    c.a("ult", tick(P["r_dur"]))
    waves = 4
    for k in range(waves):
        t_ = call + tick(k * P["r_p"])
        c.at_spot("r_wave", t_, spot, gy, under=False)
        c.on("r_hit", t_ + tick(1))
        c.on("r_slow", t_ + tick(1), until=t_ + tick(P["r_slow_t"]))
        d.flinches.append(t_ + tick(1))
    d.death = call + tick((waves - 1) * P["r_p"] + 2)
    end = call + tick((waves - 1) * P["r_p"]) + 1400
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_gangplank_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[17:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_gangplank_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_gangplank_showcase.gif")))


if __name__ == "__main__":
    main()
