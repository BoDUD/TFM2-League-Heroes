#!/usr/bin/env python3
"""Preview images for Graves, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_graves.py [--out docs/preview] [--only frames|effects|showcase]

  league_graves_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_graves_effects.png   every effect animation, 3x
  league_graves_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_graves.py, 60 ticks
                              a second): two shells of the shotgun (the muzzle blast in his frames, the pellet, the
                              hit; the second shell's reload), Smoke Screen thrown with a shot (the canister, the cloud,
                              the slowed feet); End of the Line - the shell through Darius, the bomb waiting a second and
                              blowing up; Quickdraw - the dust where he set off, True Grit's gold ring; Collateral Damage -
                              the shell onto Darius and the blast; 3x
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
from build_graves import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_graves")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_graves_fx", "league_graves_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")
MUZZLE = (26, -6)       # the muzzle from his standing point on the shot frame (game px, x forward, y up from the pivot)


class Clip:
    """One scripted clip: his body's animations one after another, effects under / over the units, Darius."""

    def __init__(self, sp, d, me, small, big):
        self.sp, self.d, self.me, self.small, self.big = sp, d, me, small, big
        self.body, self.under, self.over, self.t = [], [], [], 0.0

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "graves", z))
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

    def shot(self, tag, hit_tag, rel, speed):
        """A projectile from his muzzle to Darius at `speed` (game units a tick), its hit on him."""
        x0, x1 = self.me.pos(rel)[0] + MUZZLE[0], self.d.pos(rel)[0]
        hit = rel + tick(max(1.0, (x1 - x0) * 1000.0 / speed))
        self.fly(tag, rel, hit, x0, x1, self.me.y - 11 + MUZZLE[1])
        self.on(hit_tag, hit)
        self.d.flinches.append(hit)
        return hit

    def attack(self, second=False, smoke=False):
        rel = self.t + tick(P["a_hit"])
        hit = self.shot("a_shot", "a_hit", rel, P["a_speed"])
        if smoke:                                  # Smoke Screen thrown at the champion the shot hits
            land = hit + tick(1 + P["w_fly"])
            self.at_spot("w_smoke", land, self.d.x, self.d.y, under=False)
            self.on("w_slow", land, until=land + tick(P["w_slow_t"] + 60))
        self.a("attack2" if second else "attack", tick(P["a2_dur"] if second else P["atk_dur"]))
        self.wait(tick(P["atk_cd"] - P["atk_dur"]) + (tick(P["a_reload"]) if second else 0))
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
    small, big = fx["league_graves_fx"], fx["league_graves_big"]
    W, H = 220, 120
    gy = 98
    x0 = 50
    fx_ = x0 + 42                                       # Darius in his reach
    d = Foe(load(DARIUS), fx_, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.wait(400)
    c.attack()
    c.attack(second=True, smoke=True)
    # Q End of the Line: the shell through Darius to its end, the bomb there waiting q_fuse, then blowing up on him
    rel = c.t + tick(P["q_at"])
    reach = c.me.pos(rel)[0] + MUZZLE[0] + P["q_range"] / 1000
    stop = rel + tick(P["q_range"] / P["q_speed"])
    c.fly("q_shell", rel, stop, c.me.pos(rel)[0] + MUZZLE[0], reach, gy - 11 + MUZZLE[1])
    passed = rel + tick((fx_ - c.me.pos(rel)[0] - MUZZLE[0]) * 1000 / P["q_speed"])
    c.on("q_hit", passed)
    d.flinches.append(passed)
    c.at_spot("q_blast", stop, min(reach, W - 20), gy, under=False)
    c.a("skill", tick(P["q_dur"]))
    c.wait(stop - c.t + tick(P["q_fuse"]) + 400)
    # E Quickdraw: the dust where he set off, True Grit's ring under him
    go = c.t + tick(P["e_at"])
    c.on_me("e_dust", go, under=True)
    c.on_me("e_grit", go + tick(4), until=go + tick(P["e_t"]), under=True)
    c.a("skill2", tick(P["e_dur"]))
    c.attack()
    # R Collateral Damage: the shell onto Darius, the hit and the blast round him
    rel = c.t + tick(P["r_at"])
    hit = c.shot("r_shell", "r_hit", rel, P["r_speed"])
    c.at_spot("r_blast", hit + tick(1), fx_, gy, under=False)
    d.death = hit + 300
    c.a("ult", tick(P["r_dur"]))
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_graves_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_graves_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_graves_showcase.gif")))


if __name__ == "__main__":
    main()
