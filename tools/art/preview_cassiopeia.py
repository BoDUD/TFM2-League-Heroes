#!/usr/bin/env python3
"""Preview images for Cassiopeia, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_cassiopeia.py [--out docs/preview] [--only frames|effects|showcase]

  league_cassiopeia_frames.png    every animation's dense frames (hd_, PPU 1.3, as league.dll shows them)
  league_cassiopeia_effects.png   every effect animation, 3x
  league_cassiopeia_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_cassiopeia.py, 60
                                  ticks a second): Q - the warning ring at his feet, the blast, the poison on him; Twin
                                  Fangs flying at him (bigger while he is poisoned); W - the acid bolt, its splat and the
                                  miasma lying round him (slowed and grounded); more fangs; R - her eyes' glare, the wave
                                  flying out, the hit and the stone crust on him (petrified); fangs until he falls; 3x
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
from build_cassiopeia import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_cassiopeia")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_cassiopeia_fx", "league_cassiopeia_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")


class Clip:
    """One scripted clip: his body's animations one after another, effects under / over the units, Darius."""

    def __init__(self, sp, d, me, small, big):
        self.sp, self.d, self.me, self.small, self.big = sp, d, me, small, big
        self.body, self.under, self.over, self.t = [], [], [], 0.0
        self.turned = False

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "cassiopeia", z))
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

    def fang(self):
        """One Twin Fang: the attack's flick, the fang flying from her front claw, its bite."""
        rel = self.t + tick(P["a_rel"])
        x0, x1 = self.me.pos(rel)[0] + 12, self.d.pos(rel)[0]
        hit = rel + tick((x1 - x0) * 1000.0 / P["e_speed"])
        self.fly("a_fang", rel, hit, x0, x1, self.me.y - 20)
        self.on("a_hit", hit)
        self.d.flinches.append(hit)
        self.a("attack", tick(P["atk_dur"]))
        self.wait(tick(P["atk_cd"] - P["atk_dur"]))

    def at_spot(self, tag, when, x, y, sheet=None, under=True, until=None):
        an = Anim(frames_of(sheet or self.big, tag), when, int(x), int(y), loop=until is not None, until=until)
        (self.under if under else self.over).append(an)

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
    small, big = fx["league_cassiopeia_fx"], fx["league_cassiopeia_big"]
    W, H = 210, 110
    gy = 88
    x0 = 62                                             # her tail lies ~45 px behind her
    fx_ = x0 + 62                                       # Darius within her fangs' reach
    d = Foe(load(DARIUS), fx_, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.wait(400)
    # Q Noxious Blast: the warning ring at his feet through the delay, the blast, the poison puffs while it lasts
    rel = c.t + tick(P["q_rel"])
    boom = rel + tick(P["q_delay"])
    c.at_spot("q_warn", rel, fx_, gy, under=True)
    c.at_spot("q_blast", boom, fx_, gy, under=False)
    for k in range(0, P["q_t"], P["q_p"]):
        c.on("q_hit", boom + tick(k))
        d.flinches.append(boom + tick(k))
    c.a("skill", tick(P["q_dur"]))
    c.wait(boom - c.t)
    # Twin Fang while he is poisoned
    for _ in range(3):
        c.fang()
    # W Miasma: the acid bolt, its splat and the cloud lying round him (slowed, grounded)
    rel = c.t + tick(P["w_rel"])
    land = rel + tick(P["w_travel"])
    c.fly("w_bolt", rel, land, me.pos(rel)[0] + 10, fx_, gy - 24)
    c.at_spot("w_land", land, fx_, gy, under=True)
    for k in range(0, P["w_t"], P["w_show"]):
        c.at_spot("w_field", land + tick(k), fx_, gy, under=True)
    c.on("w_slow", land, until=land + tick(P["w_t"]))
    c.a("skill2", tick(P["w_dur"]))
    for _ in range(3):
        c.fang()
    # R Petrifying Gaze: her eyes' glare, the wave flying out at him, the hit and the stone crust while he is petrified
    start = c.t
    rel = start + tick(P["r_rel"])
    c.on_me("r_cast", start, big)
    reach = me.pos(rel)[0] + P["r_range"] // 1000
    c.fly("r_wave", rel, rel + tick(P["r_fly"]), me.pos(rel)[0] + 10, reach, gy - 20, sheet=big)
    hit = rel + tick(P["r_fly"] * (fx_ - me.pos(rel)[0]) * 1000 // P["r_range"])
    c.on("r_hit", hit)
    c.on("r_stone", hit, until=hit + tick(P["r_stun"]))
    d.flinches.append(hit)
    c.a("ult", tick(P["r_dur"]))
    for _ in range(4):
        c.fang()
    d.death = c.t - 200
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_cassiopeia_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[18:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_cassiopeia_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_cassiopeia_showcase.gif")))


if __name__ == "__main__":
    main()
