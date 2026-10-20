#!/usr/bin/env python3
"""Preview images for Sylas, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_sylas.py [--out docs/preview] [--only frames|effects|showcase]

  league_sylas_frames.png    every animation's dense frames (hd_, PPU 1.2, as league.dll shows them)
  league_sylas_effects.png   every effect animation, 3x
  league_sylas_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_sylas.py, 60 ticks a
                             second): a chain swing; Chain Lash - up and down slamming, the two chains flying, Darius
                             lashed and slowed, the crossing glowing under him and bursting; the whirl of Petricite
                             Burst the cast charged; Abscond / Abduct - the dash, the chain, Darius knocked up and Sylas
                             pulled onto him, Kingslayer's stab and its heal at once; Hijack - the chain steals Darius's
                             ultimate (the sigil over his head), then the stolen blast at Darius; 3x
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
from build_sylas import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_sylas")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_sylas_fx", "league_sylas_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")


class Clip:
    """One scripted clip: his body's animations one after another, effects under / over the units, Darius."""

    def __init__(self, sp, d, me, small, big):
        self.sp, self.d, self.me, self.small, self.big = sp, d, me, small, big
        self.body, self.under, self.over, self.t = [], [], [], 0.0

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "sylas", z))
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

    def shot(self, tag, rel, speed):
        """A projectile from his manacle to Darius at `speed` (game units a tick): the tick it lands."""
        x0, x1 = self.me.pos(rel)[0] + 6, self.d.pos(rel)[0]
        hit = rel + tick((x1 - x0) * 1000.0 / speed)
        self.fly(tag, rel, hit, x0, x1, self.me.y)
        return hit

    def attack(self):
        hit = self.t + tick(P["a_rel"])
        self.on("a_hit", hit)
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
    small, big = fx["league_sylas_fx"], fx["league_sylas_big"]
    W, H = 280, 120
    gy = 92
    x0 = 80
    fx_ = x0 + 64                                       # Darius in chain reach (26 px plus the two bodies)
    d = Foe(load(DARIUS), fx_, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.wait(400)
    c.attack()
    # Q Chain Lash: up and down slamming, the chains fly at Darius (lashed, slowed), the crossing under him bursts
    rel = c.t + tick(P["q_rel"] - 1)
    lash = c.shot("q_chain", rel, P["q_speed"])
    c.on("q_hit", lash)
    c.d.flinches.append(lash)
    c.on("q_slow", lash, until=lash + tick(P["q_slow_t"]))
    land = rel + tick(P["q_fly"])
    c.at_spot("q_cross", land, d.x, gy)
    burst = land + tick(P["q_wait"]) - 1000 / 60
    c.on("q_hit2", burst)
    c.d.flinches.append(burst)
    c.a("skill", tick(P["q_dur"]))
    c.on_me("p_1", c.t - tick(P["q_dur"]), until=c.t + 600)
    c.wait(200)
    # the charge it stored: the next attack whirls the chains
    spin = c.t + tick(P["p_rel"] - 1)
    c.on_me("p_spin", spin, sheet=big, under=True)
    c.on("p_hit", spin)
    c.on("a_hit", spin)
    c.d.flinches.append(spin)
    c.a("attack_p", tick(P["p_dur"]))
    c.wait(500)
    # E Abscond / Abduct: from further back, the dash, the chain, Darius knocked up, pulled onto him, the stab at once
    back = x0 - 56
    me.moves.append((c.t, c.t + 200, x0, back))
    c.wait(400)
    dash_t = -(-P["e_dash"] // P["e_dspeed"])
    me.moves.append((c.t, c.t + tick(dash_t), back, back + 18))
    throw = c.t + tick(dash_t + P["e_wind"])
    c.a("skill2", tick(dash_t + P["e_wind"]))
    caught = c.shot("e_chain", throw, P["e_speed"])
    c.wait(caught - c.t)
    c.on("e_hit", caught)
    c.d.hops.append((caught, caught + tick(P["e_up"]), 8))
    pull = tick(P["e_pull_dur"])
    me.moves.append((caught, caught + pull, back + 18, x0))
    c.a("skill2_pull", pull)
    stab = c.t
    c.on("w_hit", stab)
    c.on_me("w_heal", stab)
    c.d.flinches.append(stab)
    c.a("skill_w", tick(P["w_dur"]))
    c.wait(500)
    # R Hijack: the steal (the chain, the stun, the stolen power home, the sigil over him), then the stolen blast
    rel = c.t + tick(P["r_rel"] - 1)
    stolen = c.shot("r_hook", rel, P["r_speed"])
    c.on("r_steal", stolen)
    c.d.flinches.append(stolen)
    c.on_me("r_got", stolen)
    c.a("ult", tick(P["r_dur"]))
    c.on_me("r_have", stolen, until=c.t + 700)
    c.wait(600)
    blast = c.t + tick(P["r2_rel"] - 1 + P["r2_fly"])
    c.at_spot("r2_boom", blast, d.x, gy)
    c.on("r2_hit", blast)
    c.d.hops.append((blast, blast + tick(P["r2_up"]), 12))
    c.a("ult_cast", tick(P["r2_dur"]))
    d.death = blast + tick(P["r2_up"])
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_sylas_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_sylas_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_sylas_showcase.gif")))


if __name__ == "__main__":
    main()
