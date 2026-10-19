#!/usr/bin/env python3
"""Preview images for Yuumi, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_yuumi.py [--out docs/preview] [--only frames|effects|showcase]

  league_yuumi_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them; the blank a_* the
                             add-on swaps in are left out)
  league_yuumi_effects.png   every effect animation, 3x (the ride picture too when its sheet is there)
  league_yuumi_showcase.gif  a scripted fight, Jinx beside her against Darius, timed like the kit
                             (tools/kit/build_yuumi.py, 60 ticks a second): a page bolt with Feline Friendship (the
                             star-and-heart hit, her hearts); Prowling Projectile flying across the lane, empowered on
                             arrival (the big hit, the slow ring); You and Me! - she leaps onto Jinx (the puff where she
                             was), Zoomies' shield and speed swirl on Jinx, the cat on her book riding Jinx's head, the
                             healing hearts every second, the jump off; Final Chapter - the magic circle under her, five
                             waves flying across, the third rooting Darius, the waves healing Jinx as they pass; 3x
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
from build_yuumi import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_yuumi")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_yuumi_fx", "league_yuumi_big")}
RIDE = os.path.join(LEAGUE, "effects", "league_yuumi_ride")
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")
JINX = os.path.join(LEAGUE, "champions", "league_jinx")


class Clip:
    """One scripted clip: her body's animations one after another, effects under / over the units, Darius and Jinx."""

    def __init__(self, sp, d, ally, me, small, big, ride):
        self.sp, self.d, self.ally, self.me, self.small, self.big, self.ride = sp, d, ally, me, small, big, ride
        self.body, self.under, self.over, self.t = [], [], [], 0.0

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "yuumi", z))
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

    def hidden(self, ms):
        """She is banished: nothing of her drawn."""
        self.t += ms

    def on(self, tag, when, sheet=None, until=None, unit=None):
        self.over.append(OnFoe(frames_of(sheet or self.small, tag), when, unit or self.d, until=until))

    def under_unit(self, tag, when, unit, until=None, sheet=None):
        self.under.append(OnFoe(frames_of(sheet or self.small, tag), when, unit, until=until))

    def on_me(self, tag, when, sheet=None, until=None, under=False):
        (self.under if under else self.over).append(OnMe(frames_of(sheet or self.small, tag), when, self.me, until=until))

    def at_spot(self, tag, when, x, y, sheet=None, under=False):
        an = Anim(frames_of(sheet or self.small, tag), when, int(x), int(y))
        (self.under if under else self.over).append(an)

    def fly(self, tag, t0, t1, x0, x1, y, sheet=None):
        """A projectile's picture flying in a straight line (drawn going right: these fly right)."""
        self.over.append(Anim(frames_of(sheet or self.small, tag), t0, int(x0), int(y), loop=True, until=t1,
                              x1=int(x1), y1=int(y)))

    def shot(self, tag, hit_tag, rel, speed, sheet=None, y=-6):
        """A projectile from her to Darius at `speed` (game units a tick), its hit on him."""
        x0, x1 = self.me.pos(rel)[0] + 3, self.d.pos(rel)[0]
        hit = rel + tick((x1 - x0) * 1000.0 / speed)
        self.fly(tag, rel, hit, x0, x1, self.me.y + y, sheet)
        if hit_tag:
            self.on(hit_tag, hit)
            self.d.flinches.append(hit)
        return hit

    def render(self, out, W, H, end, z=3, step=40):
        frames, tt = [], 0.0
        while tt < end:
            img = Image.new("RGBA", (W * z, H * z), ARENA)
            for an in self.under:
                f = an.frame(tt)
                if f is not None:
                    put(img, f, *an.pos(tt), z)
            units = [(self.d.y, self.d.frame(tt), self.d.pos(tt)), (self.ally.y, self.ally.frame(tt), self.ally.pos(tt))]
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
    small, big = fx["league_yuumi_fx"], fx["league_yuumi_big"]
    ride = load(RIDE) if os.path.isfile(T.long_path(RIDE + "#sheet.png")) else None
    W, H = 280, 112
    gy = 88
    x0 = 46
    dx_ = x0 + 170                                      # Darius across the lane: the missile flies long enough
    d = Foe(load(DARIUS), dx_, gy)
    ally = Foe(load(JINX), x0 + 34, gy + 4, mirror=False)    # Jinx a step ahead of her, facing Darius
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, ally, me, small, big, ride)
    c.wait(400)
    # the attack with Feline Friendship: the bolt, the star-and-heart hit on him, her hearts
    rel = c.t + tick(P["atk_st"])
    hit = c.shot("a_bolt", "a_hit", rel, P["a_speed"])
    c.on("p_hit", hit)
    c.on_me("p_heal", hit)
    c.a("attack", tick(P["atk_dur"]))
    c.wait(tick(P["atk_cd"] - P["atk_dur"]))
    # Q Prowling Projectile across the lane: long enough in the air to be empowered
    rel = c.t + tick(P["q_st"])
    hit = c.shot("q_missile", "q_ehit", rel, P["q_speed"])
    c.under_unit("q_eslow", hit, d, until=hit + tick(P["q_eslow_t"]))
    c.a("skill", tick(P["q_dur"]))
    c.wait(500)
    # W You and Me!: the leap onto Jinx, Zoomies on her, the ride, the heals, the jump off
    leave = c.t + tick(P["w_st"])
    c.at_spot("w_jump", c.t + tick(4), x0, gy)
    c.a("skill2", tick(P["w_st"]))
    on = c.t
    ax, ay = ally.pos(on)
    me.moves.append((on - 1, on, x0, ax))
    c.on("e_hit", on, unit=ally)
    c.under_unit("e_haste", on, ally, until=on + tick(P["e_t"]))
    c.on("p_heal", on, unit=ally)                       # the heal Feline Friendship kept for her next ally
    if ride is not None:
        c.over.append(OnFoe(frames_of(ride, "idle"), on, ally, until=on + tick(P["w_t"])))
    for k in range(P["w_p"], P["w_t"] + 1, P["w_p"]):
        c.on("w_heal", on + tick(k), unit=ally)
    c.hidden(tick(P["w_t"]))
    off = c.t
    c.at_spot("w_land", off, ax, gy)
    c.a("w_off", tick(P["w_off"]))
    me.moves.append((c.t, c.t + 300, ax, x0))
    c.a("run", 300, loop=True)
    c.wait(300)
    # R Final Chapter: the magic circle, five waves at him, the third rooting him, Jinx healed as they pass
    start = c.t
    c.on_me("r_cast", start, sheet=big, under=True)
    c.a("ult", tick(P["r_dur"]))
    for k in range(P["r_n"]):
        rel = start + tick(P["r_st"] + k * P["r_gap"])
        hit = c.shot("r_wave", "r_hit", rel, P["r_speed"], sheet=big, y=-10)
        x_ally = ally.pos(rel)[0]
        passed = rel + tick(max(0, x_ally - me.pos(rel)[0]) * 1000.0 / P["r_speed"])
        c.on("r_heal", passed, unit=ally)
        if k + 1 == P["r_root_k"]:
            c.under_unit("r_root", hit, d, until=hit + tick(P["r_root"]))
    last = start + tick(P["r_st"] + (P["r_n"] - 1) * P["r_gap"])
    c.wait(last + 600 - c.t)
    d.death = c.t
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
        rows = [r for r in dense_rows(s) if not r[1].startswith("hd_a_")]
        print("frames", contact(rows, os.path.join(args.out, "league_yuumi_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in list(FX.items()) + ([("league_yuumi_ride", RIDE)]
                                               if os.path.isfile(T.long_path(RIDE + "#sheet.png")) else []):
            sp = load(path)
            rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_yuumi_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_yuumi_showcase.gif")))


if __name__ == "__main__":
    main()
