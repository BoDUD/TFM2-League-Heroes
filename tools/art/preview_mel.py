#!/usr/bin/env python3
"""Preview images for Mel, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_mel.py [--out docs/preview] [--only frames|effects|showcase]

  league_mel_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_mel_effects.png   every effect animation, 3x
  league_mel_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_mel.py, 60 ticks a
                           second): a golden bolt, Rebuttal's mirror barrier rising on the first champion hit; Radiant
                           Volley - bolts raining on his spot, six bursts; the charged attack - the three motes at her
                           waist, the bolt and three small bolts after it; Solar Snare - the sun orb along the ground, he
                           is rooted, slowed and burning; Golden Eclipse - the eclipse over her head and a sky beam on
                           him for his Overwhelm stacks; 3x
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
from build_mel import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_mel")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_mel_fx", "league_mel_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")
BOLT_UP = (5000 - P["a_y"]) / 1000.0          # the bolts leave her far palm, this many px over her pivot


class Clip:
    """One scripted clip: her body's animations one after another, effects under / over the units, Darius."""

    def __init__(self, sp, d, me, small, big):
        self.sp, self.d, self.me, self.small, self.big = sp, d, me, small, big
        self.body, self.under, self.over, self.t = [], [], [], 0.0

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "mel", z))
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

    def on_me(self, tag, when, sheet=None, until=None, under=False):
        (self.under if under else self.over).append(OnMe(frames_of(sheet or self.small, tag), when, self.me,
                                                         until=until))

    def at_spot(self, tag, when, x, y, sheet=None, under=False):
        an = Anim(frames_of(sheet or self.big, tag), when, int(x), int(y))
        (self.under if under else self.over).append(an)

    def fly(self, tag, t0, t1, x0, x1, y0, y1=None, sheet=None):
        """A projectile's picture flying in a straight line (drawn going right: these fly right)."""
        self.over.append(Anim(frames_of(sheet or self.small, tag), t0, int(x0), int(y0), loop=True, until=t1,
                              x1=int(x1), y1=int(y0 if y1 is None else y1)))

    def bolt(self, tag, when, speed, hit_tag):
        """A bolt from her far palm homing on his pivot; returns the hit's time."""
        x0, x1 = self.me.pos(when)[0], self.d.pos(when)[0]
        hit = when + tick((x1 - x0) / (speed / 1000.0))
        self.fly(tag, when, hit, x0, x1, self.me.y - BOLT_UP, self.d.y)
        self.on(hit_tag, hit)
        self.d.flinches.append(hit)
        return hit

    def attack(self, charged=0):
        rel = self.t + tick(P["a_rel"] - 1)
        hit = self.bolt("a_bolt", rel, P["a_speed"], "a_hit")
        for k in range(charged):                            # the passive's bolts after a cast
            self.bolt("p_bolt", rel + tick(1 + k * P["p_gap"]), P["p_speed"], "p_hit")
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
    small, big = fx["league_mel_fx"], fx["league_mel_big"]
    W, H = 250, 124
    gy = 96
    x0 = 60
    xa = x0 + 76                                        # Darius at her attack's reach (55 px plus the two bodies)
    d = Foe(load(DARIUS), xa, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.wait(400)
    # a golden bolt; Rebuttal's barrier rises on her first champion hit
    hit = c.attack()
    c.on_me("w_on", hit, sheet=big, until=hit + tick(P["w_t"]))
    # Q Radiant Volley: the bolts rain on his spot from the release, six bursts q_gap ticks apart once the lob lands
    rel = c.t + tick(P["q_rel"] - 1)
    c.at_spot("q_volley", rel, xa, gy)
    land = rel + tick(P["q_fly"])
    for k in range(P["q_n"]):
        b = land + tick(1 + k * P["q_gap"])
        c.on("q_hit", b)
        d.flinches.append(b)
    c.a("skill", tick(P["q_dur"]))
    charged = c.t
    c.on_me("p_3", charged, until=charged + 700)
    c.wait(500)
    # the charged attack: the bolt and three small bolts after it
    c.attack(charged=P["p_n"])
    c.wait(300)
    # E Solar Snare: the sun orb along the pivots' line; he is rooted, slowed and burns
    rel = c.t + tick(P["e_rel"] - 1)
    step = P["e_speed"] / 1000.0
    c.fly("e_orb", rel, rel + tick(P["e_len"] / P["e_speed"]), x0, x0 + P["e_len"] / 1000.0,
          gy - (5000 - P["e_y"]) / 1000.0, sheet=big)
    hit = rel + tick((xa - x0) / step)
    c.on("e_bound", hit, until=hit + tick(P["e_root"]))
    c.on("e_slow", hit, until=hit + tick(P["e_slow_t"]), under=True)
    for k in range(P["e_dn"]):
        c.on("e_burn", hit + tick(1 + k * P["e_dper"]))
    d.flinches.append(hit)
    c.a("skill2", tick(P["e_dur"]))
    c.on_me("p_3", c.t, until=c.t + 500)
    c.wait(400)
    # R Golden Eclipse: the eclipse over her head; on the slam a sky beam on him for his stacks
    rel = c.t + tick(P["r_rel"] - 1)
    c.on_me("r_cast", rel - 200, sheet=big)
    c.on("r_hit", rel, sheet=big)
    d.flinches.append(rel)
    c.a("ult", tick(P["r_dur"]))
    d.death = rel + 120
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_mel_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[11:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_mel_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_mel_showcase.gif")))


if __name__ == "__main__":
    main()
