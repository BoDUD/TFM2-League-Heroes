#!/usr/bin/env python3
"""Preview images for Gnar, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_gnar.py [--out docs/preview] [--only frames|effects|showcase]

  league_gnar_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_gnar_effects.png   every effect animation, 3x
  league_gnar_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_gnar.py, 60 ticks a
                            second): Mini's boomerang twice and Hyper's third throw; Boomerang Throw out through Darius
                            and back into his hand; Rage full - the transform; Mega's punch; Crunch onto Darius with
                            Wallop straight after (the stun stars); GNAR! - the shockwave throwing Darius away; 3x.
                            Mega stands and waits as Mega (the add-on's whole-body Mega).
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
from build_gnar import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_gnar")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_gnar_fx", "league_gnar_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")


class Clip:
    """One scripted clip: his body's animations one after another, effects under / over the units, Darius."""

    def __init__(self, sp, d, me, small, big):
        self.sp, self.d, self.me, self.small, self.big = sp, d, me, small, big
        self.body, self.under, self.over, self.t = [], [], [], 0.0
        self.idle = "idle"

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "gnar", z))
        if dur and not loop and dur > sum(ms for _, ms in fr):     # the last frame held to the action's end
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an

    def wait(self, ms):
        if ms > 0:
            self.a(self.idle, ms, loop=True)

    def on(self, tag, when, sheet=None, until=None):
        self.over.append(OnFoe(frames_of(sheet or self.small, tag), when, self.d, until=until))

    def on_me(self, tag, when, sheet=None, until=None, under=False):
        (self.under if under else self.over).append(OnMe(frames_of(sheet or self.small, tag), when, self.me, until=until))

    def fly(self, tag, t0, t1, x0, x1, y):
        """A projectile's picture flying from x0 to x1 (drawn flying right: the right way here)."""
        self.over.append(Anim(frames_of(self.small, tag), t0, x0, y, loop=True, until=t1, x1=x1, y1=y))

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
    small, big = fx["league_gnar_fx"], fx["league_gnar_big"]
    W, H = 280, 130
    gy = 104
    x0 = 70
    far = x0 + 60                                       # Darius in Mini's boomerang reach
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.wait(400)
    speed = P["a_speed"] / 1000.0 * 60 / 1000          # game px a ms
    # Mini's boomerang twice, Hyper's third throw (the burst and the speed lines under him)
    for k in range(3):
        rel = c.t + tick(P["a_rel"])
        hit = rel + (far - x0) / speed
        c.fly("a_boom", rel, hit, x0 + 6, far, gy - 6)
        c.on("a_hyper" if k == 2 else "a_hit", hit)
        c.d.flinches.append(hit)
        if k == 2:
            c.on_me("hyper", hit, until=hit + tick(P["w_ms_t"]), under=True)
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]))
    # Q Boomerang Throw: out through Darius and on, then back into his hand (the catch)
    rel = c.t + tick(P["q_rel"])
    q_speed = P["q_speed"] / 1000.0 * 60 / 1000
    end_x = x0 + P["q_range"] / 1000.0
    out_t = rel + (end_x - x0) / q_speed
    c.fly("q_boom", rel, out_t, x0 + 6, end_x, gy - 6)
    c.on("q_hit", rel + (far - x0) / q_speed)
    c.d.flinches.append(rel + (far - x0) / q_speed)
    back_t = out_t + (end_x - x0) / q_speed
    c.fly("q_back", out_t, back_t, end_x, x0 + 6, gy - 6)
    c.on("q_hit", out_t + (end_x - far) / q_speed)
    c.a("skill", tick(P["q_dur"]))
    c.wait(back_t - c.t)
    c.on_me("q_catch", c.t)
    c.wait(300)
    # Rage full (the flames round him), then the attack turns him Mega
    c.on_me("full", c.t, until=c.t + 700)
    c.wait(700)
    c.on_me("tf_mega", c.t, sheet=big)
    c.a("transform", tick(P["tf_dur"]))
    c.idle = "m_idle"
    c.wait(300)
    # Mega's punch (he walks up first: melee)
    near = far - 40
    me.moves.append((c.t, c.t + 400, x0, near))
    c.a("m_run", 400, loop=True)
    hit = c.t + tick(P["m_rel"])
    c.on("m_hit", hit)
    c.d.flinches.append(hit)
    c.a("m_attack", tick(P["m_atk_dur"]))
    c.wait(300)
    # E Crunch from a step back onto Darius, Wallop straight after (the pros' E -> W)
    back = near - 30
    me.moves.append((c.t, c.t + 250, near, back))
    c.a("m_run", 250, loop=True)
    go = c.t + tick(P["c_go"])
    land = c.t + tick(P["c_land"])
    me.moves.append((go, land, back, near))
    c.on_me("c_slam", land, sheet=big, under=True)
    c.on("c_hit", land)
    c.d.flinches.append(land)
    c.a("m_skill2", tick(P["c_dur"]))
    smash = c.t + tick(P["w_at"])
    c.on_me("w_quake", smash, sheet=big, under=True)
    c.on("w_hit", smash)
    c.d.flinches.append(smash)
    c.a("m_wallop", tick(P["w_dur"]))
    c.wait(400)
    # R GNAR!: the shockwave round him, Darius thrown away
    throw = c.t + tick(P["r_at"])
    c.on_me("r_wave", throw, sheet=big, under=True)
    c.on("r_hit", throw)
    c.d.flinches.append(throw)
    c.d.slides.append((throw, throw + tick(P["r_push"] // P["r_push_v"]), P["r_push"] // 1000))
    c.a("ult", tick(P["r_dur"]))
    d.death = c.t + 300
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_gnar_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[12:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_gnar_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_gnar_showcase.gif")))


if __name__ == "__main__":
    main()
