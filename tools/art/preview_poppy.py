#!/usr/bin/env python3
"""Preview images for Poppy, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_poppy.py [--out docs/preview] [--only frames|effects|showcase]

  league_poppy_frames.png    every animation's dense frames (hd_, PPU 1.3, as league.dll shows them)
  league_poppy_effects.png   every effect animation, 3x
  league_poppy_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_poppy.py, 60 ticks a
                             second): Steadfast Presence's dome and aura as she closes in; Iron Ambassador - the buckler
                             flying at him, lying on the ground, picked up (her gold shield); Heroic Charge - the
                             impact and the stun stars; Hammer Shock - the slam, the cracked ground, the rupture; two
                             blows; Keeper's Verdict - the charge, the swing's shockwave flying at him, the hit; 3x
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
from build_poppy import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_poppy")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_poppy_fx", "league_poppy_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")


class Clip:
    """One scripted clip: her body's animations one after another, effects under / over the units, Darius."""

    def __init__(self, sp, d, me, small, big):
        self.sp, self.d, self.me, self.small, self.big = sp, d, me, small, big
        self.body, self.under, self.over, self.t = [], [], [], 0.0
        self.turned = False

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "poppy", z))
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

    def blow(self):
        """One hammer swing at him."""
        hit = self.t + tick(P["atk_st"])
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
    small, big = fx["league_poppy_fx"], fx["league_poppy_big"]
    W, H = 200, 110
    gy = 88
    x0 = 70                                             # her hammer stands ~20 px behind her
    fx_ = x0 + 44                                       # Darius within her buckler's reach
    d = Foe(load(DARIUS), fx_, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.wait(400)
    # Steadfast Presence: the dome rising and the aura round her for w_t
    c.on_me("w_cast", c.t, big, under=True)
    c.on_me("w_on", c.t, big, until=c.t + tick(P["w_t"]), under=True)
    # Iron Ambassador: the buckler flying at him, its clang, lying between them, picked up -> her shield
    rel = c.t + tick(P["atk_st"])
    hit = rel + tick((fx_ - x0) * 1000.0 / P["p_speed"])
    c.fly("p_buckler", rel, hit, x0 + 8, fx_, gy - 18)
    c.on("a_hit", hit)
    d.flinches.append(hit)
    land = hit + tick(P["p_fly"])
    spot = x0 + 14
    for k in range(0, 36, 15):
        c.at_spot("p_lie", land + tick(k), spot, gy, sheet=small)
    pick = land + tick(36)
    c.on_me("p_pick", pick)
    c.on_me("p_shown", pick, until=pick + tick(P["p_sh_t"]), under=True)
    c.a("attack", tick(P["atk_dur"]))
    c.wait(pick - c.t + 200)
    # Heroic Charge: the dash into him, the impact, the stun stars (the main pack's short stun at the carry's end)
    contact_t = c.t + tick(6)
    c.on("e_hit", contact_t)
    d.flinches.append(contact_t)
    stun = contact_t + tick(P["e_kb_t"])
    c.on("e_stun", stun, until=stun + tick(P["e_stun_m"]))
    c.a("skill2", tick(P["e_anim"]))
    c.wait(300)
    # Hammer Shock: the slam on his spot, the cracked ground for q_t, the rupture
    slam = c.t + tick(P["q_rel"])
    c.at_spot("q_slam", slam, fx_, gy, under=False)
    for k in range(0, P["q_t"], 15):
        c.at_spot("q_crack", slam + tick(k), fx_, gy)
    c.at_spot("q_burst", slam + tick(P["q_t"]), fx_, gy, under=False)
    for t_ in (slam, slam + tick(P["q_t"])):
        c.on("q_hit", t_)
        d.flinches.append(t_)
    c.a("skill", tick(P["q_dur"]))
    c.wait(slam + tick(P["q_t"]) - c.t + 100)
    for _ in range(2):
        c.blow()
    # Keeper's Verdict: the charge, the swing, the shockwave flying at him, the hit
    c.on_me("r_charge", c.t, big, until=c.t + tick(P["r_ch"]))
    c.a("ult_charge", tick(P["r_ch"]), loop=True)
    rel = c.t + tick(P["r_rel"])
    reach = fx_ + 40
    c.fly("r_wave", rel, rel + tick(P["r_len"] / P["r_speed"]), x0 + 12, reach, gy - 14, sheet=big)
    hit = rel + tick((fx_ - x0 - 12) * 1000.0 / P["r_speed"])
    c.on("r_hit", hit)
    d.flinches.append(hit)
    c.a("ult", tick(P["r_rel"] + P["r_rec"]))
    d.death = hit + 300
    end = c.t + 1400
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_poppy_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_poppy_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_poppy_showcase.gif")))


if __name__ == "__main__":
    main()
