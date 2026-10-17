#!/usr/bin/env python3
"""Preview images for Anivia, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_anivia.py [--out docs/preview] [--only frames|effects|showcase|rebirth]

  league_anivia_frames.png    every animation's dense frames (hd_, PPU 1.2, as league.dll shows them)
  league_anivia_effects.png   every effect animation, 3x
  league_anivia_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_anivia.py, 60 ticks a
                              second), as the main pack shows it: an ice bolt; Flash Frost - the orb stops on Darius
                              and bursts, the stun's ice crust and the Iced snowflake over him; Crystallize - the wall
                              rises on the blast point two ticks later and drags him off it toward her (the wall
                              behind him), the combo's Frostbite
                              doubled on the stunned champion; Glacial Storm dropped by the watch on him (in crowd
                              control), growing, then formed; Frostbite; the stun over, he runs for it and sticks at
                              the wall's edge (drawn under the units); the bolts finish him in the storm; the wall
                              melts; 3x
  league_anivia_rebirth.gif   the add-on's Rebirth (league_anivia): Darius's lethal blow - the flash, she curls into
                              the egg (egg_t ticks, his blows on it), the egg breaks open and she flies on; 3x
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
from preview_kindred import Turned, fx_contact  # noqa: E402
from preview_leesin import Foe  # noqa: E402
from preview_pyke import Me, OnFoe, OnMe  # noqa: E402
from build_anivia import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_anivia")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_anivia_fx", "league_anivia_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")
lift = lambda y: (5000 - y) / 1000.0           # a projectile's picture over the ground (its y_offset 0)


class Clip:
    """One scripted clip: her body's animations one after another, effects under / over the units, Darius."""

    def __init__(self, sp, d, me, small, big):
        self.sp, self.d, self.me, self.small, self.big = sp, d, me, small, big
        self.body, self.ground, self.under, self.over, self.t = [], [], [], [], 0.0

    def a(self, tag, dur=None, loop=False, z=3):
        an = Anim(dense(self.sp, tag, "anivia", z), self.t, 0, 0, loop=loop,
                  until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an

    def wait(self, ms):
        if ms > 0:
            self.a("idle", ms, loop=True)

    def on(self, tag, when, sheet=None, under=False, until=None, frames=None):
        o = OnFoe(frames or frames_of(sheet or self.small, tag), when, self.d, until=until)
        (self.under if under else self.over).append(o)

    def on_me(self, tag, when, sheet=None, under=False, until=None, frames=None):
        o = OnMe(frames or frames_of(sheet or self.small, tag), when, self.me, until=until)
        (self.under if under else self.over).append(o)

    def at_spot(self, tag, when, x, y, sheet=None, under=False, ground=False):
        """under: z -1, under the units; ground: z -2, under those too (the storm under the wall)."""
        an = Anim(frames_of(sheet or self.small, tag), when, int(x), int(y))
        (self.ground if ground else self.under if under else self.over).append(an)

    def fly(self, tag, rel, speed, end=None):
        """A projectile from her at rel: homing on Darius's pivot, or straight to end = (x, y); its arrival."""
        mx, my = self.me.pos(rel)
        ex, ey = end or self.d.pos(rel)
        arrive = rel + tick(max(1.0, abs(ex - mx) / (speed / 1000.0)))
        self.over.append(Turned(frames_of(self.small, tag), rel, int(mx), int(my - lift(0)), loop=False,
                                until=arrive, x1=int(ex), y1=int(ey)))
        return arrive

    def attack(self):
        arrive = self.fly("a_bolt", self.t + tick(P["a_rel"]), P["a_speed"])
        self.on("a_hit", arrive)
        self.d.flinches.append(arrive)
        self.a("attack", tick(P["atk_dur"]))
        self.wait(tick(P["atk_cd"] - P["atk_dur"]))
        return arrive

    def render(self, out, W, H, end, z=3, step=40):
        frames, tt = [], 0.0
        while tt < end:
            img = Image.new("RGBA", (W * z, H * z), ARENA)
            for an in self.ground + self.under:
                f = an.frame(tt)
                if f is not None:
                    put(img, f, *an.pos(tt), z)
            units = [(self.d.pos(tt)[1], self.d.frame(tt), self.d.pos(tt))]
            for an in self.body:
                f = an.frame(tt)
                if f is not None:
                    units.append((an.pos(tt)[1] + 0.5, f, an.pos(tt)))
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
    small, big = fx["league_anivia_fx"], fx["league_anivia_big"]
    W, H = 280, 146
    gy = 84
    x0 = 100
    d = Foe(load(DARIUS), x0 + 55, gy)                  # at her attack range
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.wait(400)
    c.attack()
    c.a("idle", tick(3))                                # the R press only arms the ult (the watch drops it)
    # Flash Frost: the seen orb stops on Darius (its radius on his) and bursts there
    rel = c.t + tick(P["q_rel"])
    mx, my = me.pos(rel)
    stop = d.pos(rel)[0] - 4
    blast = c.fly("q_ball", rel, P["q_speed"], end=(stop, my - lift(0)))
    c.at_spot("q_blast", blast, stop, gy, big)
    c.on("q_stun", blast)
    d.flinches.append(blast)
    stun_end = blast + tick(P["q_stun"])
    # Crystallize: two ticks later the wall on the blast point; its drag-out field hauls him toward her (w_go a tick)
    # until his body is off it (half its width and a champion's radius, 15000, from its line)
    rise = blast + tick(2)
    c.at_spot("w_wall", rise, stop, gy, big, under=True)
    edge = stop - (P["w_w"] / 2 + 15000) / 1000.0
    gap = d.pos(rise)[0] - (edge - 0.5)
    d.slides.append((rise + tick(1), rise + tick(1 + gap * 1000 / P["w_go"]), -gap))
    # the combo's Frostbite on the stunned champion: the shard and its double
    hit = c.fly("e_shard", blast + tick(P["e_combo_at"]), P["e_speed"])
    c.on("e_hit", hit)
    c.on("e_iced", hit)
    d.flinches.append(hit)
    c.a("skill", tick(P["q_dur"]))
    # Glacial Storm: the watch's next look (every watch_p ticks) finds him in crowd control within r_range
    drop = blast + tick(6)
    c.wait(drop - c.t)
    c.on_me("r_cast", drop)
    launch = drop + tick(P["r_rel"] - 1)
    land = launch + tick(1)
    sx, sy = d.pos(launch)
    formed = land + tick(3 * P["r_grow"])
    storm_end = land + tick(P["r_t"])
    c.at_spot("r_storm", land, sx, sy, big, ground=True)
    c.at_spot("r_formed", formed, sx, sy, big, ground=True)
    c.a("ult", tick(P["r_dur"]))
    # Frostbite: still stunned -> doubled
    rel = c.t + tick(P["e_rel"])
    hit = c.fly("e_shard", rel, P["e_speed"])
    c.on("e_hit", hit)
    c.on("e_iced", hit)
    d.flinches.append(hit)
    c.a("skill2", tick(P["e_dur"]))
    # the stun over, he runs for it and sticks at once: the wall's 99% slow holds him at its edge
    x_now = d.pos(stun_end)[0]
    d.slides.append((stun_end, stun_end + tick(4), max(0.0, edge - x_now)))
    c.attack()
    c.attack()
    kill = c.attack()
    d.death = kill + 60
    d.runs.append((stun_end, d.death))
    k = 0
    while land + tick(1 + P["r_p"] * k) < min(storm_end, d.death):      # the storm's bites every r_p ticks
        d.flinches.append(land + tick(1 + P["r_p"] * k))
        k += 1
    c.on("iced", blast, until=d.death)                  # Q's mark, then the formed storm's every bite renews it
    end = rise + tick(P["w_t"]) + 300                   # the wall melts
    c.wait(end - c.t)
    return c.render(out, W, H, end, z)


def rebirth(out, z=3):
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_anivia_fx"], fx["league_anivia_big"]
    dfx = load(os.path.join(LEAGUE, "effects", "league_darius_fx"))
    W, H = 220, 116
    gy = 80
    x0 = 90
    d = Foe(load(DARIUS), x0 + 40, gy)                  # in his reach (her near wing reaches 30 px)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)

    def blow(at):
        d.attacks.append(at)
        hit = at + 250
        c.on_me("hit", hit, frames=frames_of(dfx, "hit"))
        return hit

    c.wait(300)
    blow(300)
    c.attack()
    lethal = blow(1600)
    c.wait(lethal - c.t)
    # the add-on catches the lethal blow: the flash, she curls up (egg_in), the egg (egg_idle; egg_hit on his blows),
    # the hatching - all drawn by the add-on's display hook (game 0.6.4), the data plays no cast animation
    c.on_me("p_egg_in", lethal)
    c.a("egg_in", tick(P["egg_in"] + 2))
    out_at = lethal + tick(P["egg_t"])
    at = lethal + 900
    while at + 250 + 200 < out_at - 300:
        h = blow(at)
        c.a("egg_idle", h - c.t, loop=True)
        c.a("egg_hit", 200)
        at += 1200
    c.a("egg_idle", out_at - c.t, loop=True)
    c.on_me("p_hatch", out_at)
    c.a("hatch", tick(P["egg_out"]))
    c.attack()
    c.wait(300)
    return c.render(out, W, H, c.t, z)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    ap.add_argument("--only", choices=["frames", "effects", "showcase", "rebirth"])
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    if args.only in (None, "frames"):
        s = load(CHAMP)
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_anivia_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_anivia_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_anivia_showcase.gif")))
    if args.only in (None, "rebirth"):
        print("rebirth frames/seconds", rebirth(os.path.join(args.out, "league_anivia_rebirth.gif")))


if __name__ == "__main__":
    main()
