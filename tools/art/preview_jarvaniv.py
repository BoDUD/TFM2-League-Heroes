#!/usr/bin/env python3
"""Preview images for Jarvan IV, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_jarvaniv.py [--out docs/preview] [--only frames|effects|showcase|ring]

  league_jarvaniv_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_jarvaniv_effects.png   every effect animation, 3x
  league_jarvaniv_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_jarvaniv.py, 60
                                ticks a second), as the main pack shows it: the R press arms the ult; E -> Q - the
                                standard lands where Darius stands (its hit, the attack-speed aura on Jarvan), two
                                ticks later the lance flies through him (armour shred, knock-up) and Jarvan dashes after
                                it to the flag; the knock-up opens the window, so the watch's next look leaps:
                                Cataclysm lands on him, the rock ring rises; Golden Aegis (his shield, Darius slowed);
                                a thrust with Martial Cadence; Darius runs for the edge and, still inside the rocks,
                                the ring's hold (r_leash) pulls him back; the thrusts finish him; the ring crumbles; 3x
  league_jarvaniv_ring.gif      the same fight with the add-on (league_jarvaniv): Darius runs into the real rock wall
                                and stands against it; Jarvan walks up and finishes him
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
from build_jarvaniv import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_jarvaniv")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_jarvaniv_fx", "league_jarvaniv_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")
BODY = 10                                       # px between his pivot and Darius's when he lands on / next to him


class Clip:
    """One scripted clip: his body's animations one after another, effects under / over the units, Darius."""

    def __init__(self, sp, d, me, small, big):
        self.sp, self.d, self.me, self.small, self.big = sp, d, me, small, big
        self.body, self.under, self.over, self.t = [], [], [], 0.0

    def a(self, tag, dur=None, loop=False, z=3):
        an = Anim(dense(self.sp, tag, "jarvaniv", z), self.t, 0, 0, loop=loop,
                  until=(self.t + dur) if dur else None)
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

    def attack(self, cadence=False):
        hit = self.t + tick(P["a_hit"])
        self.on("a_hit", hit)
        if cadence:
            self.on("p_hit", hit)
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


def showcase(out, z=3, native=False):
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_jarvaniv_fx"], fx["league_jarvaniv_big"]
    W, H = 260, 130
    gy = 86
    x0 = 70
    fx_ = x0 + 50                                       # Darius in E's range (e_range 55)
    d = Foe(load(DARIUS), fx_, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.wait(400)
    c.a("idle", tick(3))                                # the R press only arms the ult (the watch leaps)
    # E: the standard lobbed onto Darius's spot; its hit, the aura on him while he stays within f_r
    land = c.t + tick(P["e_rel"] - 1 + P["e_travel"])
    c.at_spot("e_flag", land, fx_, gy)
    c.on("e_hit", land)
    d.flinches.append(land)
    c.on_me("f_as", land + tick(1), until=land + tick(P["fl_t"]))
    c.a("skill", tick(P["e_dur"]))
    # Q: q_gap ticks after the landing the lance flies through him and Jarvan dashes after it onto the flag
    go = land + tick(P["q_gap"])
    c.wait(go - c.t)
    stop = fx_ - BODY
    dash_end = go + tick((stop - x0) * 1000.0 / P["q_speed"])
    me.moves.append((go, dash_end, x0, stop))
    pierce = go + tick((fx_ - x0) * 1000.0 / (P["q_speed"] + P["q_line"]))
    c.on("q_hit", pierce)
    c.on("q_shred", pierce, until=pierce + tick(P["q_shred_t"]))
    d.hops.append((pierce, pierce + tick(P["q_up"]), 9))
    c.a("skill_dash", dash_end - c.t, loop=True)
    c.at_spot("q_land", c.t, stop, gy)
    c.a("skill_land", tick(10))
    # the knock-up opens the window: the watch's next look (every watch_p ticks) leaps onto him
    leap = pierce + tick(P["watch_p"])
    c.wait(leap - c.t)
    c.a("ult", tick(P["r_dur"]))
    touch = leap + tick(P["r_dur"] - 4)
    me.moves.append((leap + tick(6), touch, stop, fx_ - BODY + 2))
    rx = fx_ - BODY + 2
    c.at_spot("r_ring", touch, rx, gy)
    c.on("r_hit", touch)
    d.flinches.append(touch)
    ring_end = touch + tick(P["r_t"])
    # Golden Aegis: in the fight with a champion close, the watch's next look
    aegis = touch + tick(P["watch_p"])
    c.wait(aegis - c.t)
    rel = c.t + tick(P["w_rel"])
    c.on_me("w_cast", rel, big)
    c.on_me("w_on", rel + tick(1), until=rel + tick(P["w_t"]))
    c.on("w_hit", rel)
    c.on("w_slow", rel + tick(1), until=rel + tick(P["w_slow_t"]))
    c.a("skill_w", tick(P["w_dur"]))
    c.attack(cadence=True)                             # his first attack on Darius after the rest
    # Darius runs for the edge (a pixel a tick). Main pack: the probe every r_lp ticks finds him past r_leash from
    # Jarvan (inside the ring) and the Grab pulls him r_gs a tick for r_gt ticks back toward Jarvan. Add-on: the real
    # wall stops his centre at r_r - his radius from the ring's centre and he stands against it
    run0 = c.t + 100
    gap = fx_ - rx
    if native:
        out_dx = (P["r_r"] - 6000) / 1000.0 - gap
        run1 = run0 + tick(out_dx)
        d.runs.append((run0, run1))
        d.slides.append((run0, run1, out_dx))
        c.wait(run1 - c.t)
        step = gap + out_dx - BODY - (rx - me.pos(run1)[0])
        me.moves.append((run1, run1 + tick(step), rx, rx + step))      # he walks up to hit him at the wall
        c.a("run", tick(step), loop=True)
    else:
        out_dx = (P["r_leash"] + P["r_lp"] * 1000) / 1000.0 - gap
        run1 = run0 + tick(out_dx)
        d.runs.append((run0, run1))
        d.slides.append((run0, run1, out_dx))
        pull = P["r_gs"] * P["r_gt"] / 1000.0
        back = run1 + tick(P["r_gt"])
        d.slides.append((run1, back, -pull))
        c.on("r_zap", run1)
        c.wait(back + 80 - c.t)
    c.attack()
    kill = c.attack()
    d.death = kill + 60
    end = max(ring_end, c.t) + 500                      # the ring crumbles
    c.wait(end - c.t)
    return c.render(out, W, H, end, z)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    ap.add_argument("--only", choices=["frames", "effects", "showcase", "ring"])
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    if args.only in (None, "frames"):
        s = load(CHAMP)
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_jarvaniv_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[16:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_jarvaniv_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_jarvaniv_showcase.gif")))
    if args.only in (None, "ring"):
        print("ring frames/seconds", showcase(os.path.join(args.out, "league_jarvaniv_ring.gif"), native=True))


if __name__ == "__main__":
    main()
