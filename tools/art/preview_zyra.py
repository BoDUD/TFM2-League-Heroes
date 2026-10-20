#!/usr/bin/env python3
"""Preview images for Zyra, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_zyra.py [--out docs/preview] [--only frames|effects|showcase]

  league_zyra_frames.png    every animation's dense frames (hd_, PPU 1.7, as league.dll shows them)
  league_zyra_effects.png   every effect animation, 3x
  league_zyra_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_zyra.py, 60 ticks a
                            second): a thorn seed off her whip; Deadly Spines - the spines burst under him and a Thorn
                            Spitter grows there, spitting at him every second as he walks in; Grasping Roots - the vines
                            tear along the ground and root him, a Vine Lasher grows on his spot and lashes him (slowed);
                            Stranglethorns - the thicket bursts round him and snaps shut 2 s later, knocking him up; a
                            last seed; 3x
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
from build_zyra import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_zyra")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_zyra_fx", "league_zyra_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")
THICKET = os.path.join(LEAGUE, "effects", "league_zyra_thicket")     # dense: hd_idle at PPU 2 (league.dll hd.rs EFFECTS)
WALK = 0.9                      # Darius's walk, game px a tick
SEED_LEAD = 4                   # ticks the seed is hidden (import_zyra_fx.py): it shows past her whip's tip
SEED_UP = (5000 - P["a_y"]) / 1000.0


class Walker(Foe):
    """Darius walking in (his run turned to the left) over (t0, t1, dx) walks."""

    def __init__(self, sprite, x, y):
        super().__init__(sprite, x, y)
        self.walks = []

    def pos(self, t):
        x, y = super().pos(t)
        return int(round(x + sum(dx * min(1.0, max(0.0, (t - t0) / (t1 - t0))) for t0, t1, dx in self.walks))), y

    def frame(self, t):
        if self.death is None or t < self.death:
            for t0, t1, _ in self.walks:
                if t0 <= t < t1:
                    return self.flip(self.pick(self.run, (t - t0) % sum(ms for _, ms in self.run)))
        return super().frame(t)


class Clip:
    """One scripted clip: her body's animations one after another, effects under / over the units, Darius."""

    def __init__(self, sp, d, me, small, big):
        self.sp, self.d, self.me, self.small, self.big = sp, d, me, small, big
        self.body, self.under, self.over, self.t = [], [], [], 0.0
        self.plants = []

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "zyra", z))
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

    def at_spot(self, tag, when, x, y, sheet=None, under=True):
        an = Anim(frames_of(sheet or self.big, tag), when, int(x), int(y))
        (self.under if under else self.over).append(an)

    def fly(self, tag, t0, t1, x0, x1, y0, y1=None, sheet=None):
        """A projectile's picture flying in a straight line (drawn going right: these fly right)."""
        self.over.append(Anim(frames_of(sheet or self.small, tag), t0, int(x0), int(y0), loop=True, until=t1,
                              x1=int(x1), y1=int(y0 if y1 is None else y1)))

    def attack(self):
        """A thorn seed homing on him from SEED_UP over her pivot, its first ticks hidden (past her whip's tip)."""
        rel = self.t + tick(P["a_rel"] - 1)
        x0, x1 = self.me.pos(rel)[0], self.d.pos(rel)[0]
        step = P["a_speed"] / 1000.0
        hit = rel + tick((x1 - x0) / step)
        show = rel + tick(SEED_LEAD)
        lift = SEED_UP * (1 - SEED_LEAD * step / (x1 - x0))          # where it shows on its way down to his pivot
        self.fly("a_seed", show, hit, x0 + SEED_LEAD * step, x1, self.me.y - lift, self.d.y)
        self.on("a_hit", hit)
        self.d.flinches.append(hit)
        self.a("attack", tick(P["atk_dur"]))
        self.wait(tick(P["atk_cd"] - P["atk_dur"]))
        return hit

    def plant(self, tag, when, x, first, period, life, reach, hit_tag, slow=False):
        """A plant on (x, the pivot row) from `when`: its picture (the whole life in one tag), its strikes resolved
        once Darius's walks are known (strike_all)."""
        self.at_spot(tag, when, x, self.me.y)
        self.plants.append((when, x, first, period, life, reach, hit_tag, slow))

    def strike_all(self):
        """Every plant's strike on Darius, each period from its first, while he is alive and within its reach."""
        for when, x, first, period, life, reach, hit_tag, slow in self.plants:
            k = 0
            while first + k * period < life:
                ts = when + tick(first + k * period)
                k += 1
                if self.d.death is not None and ts >= self.d.death:
                    break
                if abs(self.d.pos(ts)[0] - x) * 1000 > reach:
                    continue
                self.on(hit_tag, ts)
                self.d.flinches.append(ts)
                if slow:
                    self.on("v_slow", ts, until=ts + tick(P["v_slow_t"]), under=True)

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


def dense_fx(sp, z, ppu=2):
    """A dense effect sheet's hd_idle frames for a clip at zoom z, drawn as league.dll draws them (put() centres them)."""
    out = []
    for (a, _), (b, ms) in zip(frames_of(sp, "idle"), frames_of(sp, "hd_idle")):
        f = b.resize((round(b.width * z / ppu), round(b.height * z / ppu)), Image.NEAREST)
        f.info["one"] = (a.width, a.height)
        out.append((f, ms))
    return out


def showcase(out, z=3):
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_zyra_fx"], fx["league_zyra_big"]
    W, H = 250, 118
    gy = 80                                             # the pivot row: the thicket's cage rises 40 px over the soles
    x0 = 44
    xa = x0 + 80                                        # Darius at Q's reach, then walking in
    xb = xa - 24
    xc = xb - 8                                         # out of the Lasher, R's ring short of her
    d = Walker(load(DARIUS), xa, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.wait(400)
    c.attack()
    # Q Deadly Spines: the spines burst on his spot q_delay ticks after the fling, a Thorn Spitter grows there
    land = c.t + tick(P["q_rel"] - 1 + P["q_delay"])
    c.at_spot("q_burst", land, xa, gy)
    c.on("q_hit", land)
    d.flinches.append(land)
    c.plant("t_plant", land, xa, P["t_first"], P["t_per"], P["t_life"], P["t_r"], "t_hit")
    c.a("skill", tick(P["q_dur"]))
    # he walks in
    w0 = land + 300
    w1 = w0 + tick((xa - xb) / WALK)
    d.walks.append((w0, w1, xb - xa))
    c.wait(w1 + 120 - c.t)
    # E Grasping Roots: the vines tear along the pivots' line from her and on, rooting him; a Vine Lasher on his spot
    rel = c.t + tick(P["e_rel"] - 1)
    step = P["e_speed"] / 1000.0
    c.fly("e_roots", rel, rel + tick(P["e_len"] / P["e_speed"]), x0, x0 + P["e_len"] / 1000.0, gy)
    hit = rel + tick((xb - x0) / step)
    unroot = hit + tick(P["e_root"])
    c.on("e_bound", hit, until=unroot)
    d.flinches.append(hit)
    c.plant("v_plant", rel + tick(P["e_grow"]), xb, P["v_first"], P["v_per"], P["v_life"], P["v_r"], "v_hit",
            slow=True)
    c.a("skill2", tick(P["e_dur"]))
    # free again, he steps off the Lasher toward her
    w0 = unroot + 80
    w1 = w0 + tick((xb - xc) / WALK)
    d.walks.append((w0, w1, xc - xb))
    c.wait(w1 + 200 - c.t)
    # R Stranglethorns: the thicket bursts round him, snaps shut r_knock ticks later and knocks him up
    land = c.t + tick(P["r_rel"] - 1 + 1)
    c.under.append(Anim(dense_fx(load(THICKET), z), land, xc, gy))
    c.on("r_hit", land)
    d.flinches.append(land)
    snap = land + tick(P["r_knock"])
    c.at_spot("r_knock", snap, xc, gy, sheet=small, under=False)
    d.hops.append((snap, snap + tick(P["r_air"]), 12))
    c.a("ult", tick(P["r_dur"]))
    c.wait(snap + tick(P["r_air"]) + 150 - c.t)
    # a last seed
    hit = c.attack()
    d.death = hit + 60
    c.strike_all()
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_zyra_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in list(FX.items()) + [("league_zyra_thicket", THICKET)]:
            sp = load(path)
            rows += [(sp, t["name"], f"{name[12:]}:{t['name']}") for t in sp.tags if t["name"] != "hd_idle"]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_zyra_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_zyra_showcase.gif")))


if __name__ == "__main__":
    main()
