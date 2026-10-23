#!/usr/bin/env python3
"""Preview images for Akshan, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_akshan.py [--out docs/preview] [--only frames|effects|showcase]

  league_akshan_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_akshan_effects.png   every effect animation, 3x
  league_akshan_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_akshan.py, 60 ticks a
                              second): the double shot (two bullets, two hits); Q - the boomerang out through Darius and
                              back, a hit each way, the third hit's Sentinel burst and his shield, the catch; E - the hook
                              shot up, the swing with a shot at Darius every e_every ticks, the roll back; W - the
                              camouflage and the speed streaks as he steps back; R - the lock sigil, the lock on Darius through the channel, five
                              heavy rounds and Darius falls; 3x
"""
import argparse
import math
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
from build_akshan import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_akshan")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_akshan_fx", "league_akshan_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")
GUN_Y = -20                                         # the level gun's height over his soles (game px)
HIT_Y = -14

ROPE_R = 42.0                                       # the add-on's swing (addons/league_akshan: ROPE_R 42000, SWEEP 120 deg)
SWEEP = 2.0 * math.pi / 3.0
HOOK_OFF = math.pi / 3.0
HAND = 20


class ArcMe(Me):
    """Me with arcs: (t0, t1, hook, a0, dir) - round the hook point at ROPE_R (the add-on's swing)."""

    def __init__(self, x, y):
        super().__init__(x, y)
        self.arcs = []

    def pos(self, t):
        for t0, t1, a, a0, d in self.arcs:
            if t0 <= t < t1:
                th = a0 + d * SWEEP * (t - t0) / (t1 - t0)
                return int(round(a[0] + ROPE_R * math.cos(th))), int(round(a[1] + ROPE_R * math.sin(th)))
            if t >= t1:
                th = a0 + d * SWEEP
                self.x, self.y = a[0] + ROPE_R * math.cos(th), a[1] + ROPE_R * math.sin(th)
        x, y = self.x, self.y
        for t0, t1, x0, x1 in self.moves:
            if t >= t1:
                x = x1
            elif t >= t0:
                x = x0 + (x1 - x0) * (t - t0) / (t1 - t0)
        return int(round(x)), int(round(y))


def swing_plan(me, target, mid=(180.0, 100.0)):
    dx, dy = target[0] - me[0], target[1] - me[1]
    base = math.atan2(dy, dx)
    best = None
    for side in (1, -1):
        h = base + side * HOOK_OFF
        a = (me[0] + ROPE_R * math.cos(h), me[1] + ROPE_R * math.sin(h))
        a0 = math.atan2(me[1] - a[1], me[0] - a[0])
        for d in (1, -1):
            th = a0 + d * SWEEP
            end = (a[0] + ROPE_R * math.cos(th), a[1] + ROPE_R * math.sin(th))
            score = math.dist(end, target) + (100.0 if a[1] > me[1] else 0.0) + 0.1 * math.dist(a, mid)
            if best is None or score < best[0]:
                best = (score, a, a0, d)
    return best[1:]


class Rope:
    """The rope drawn each frame from his hand to the hook (the add-on spawns it every tick, turned to the hook)."""

    def __init__(self, pic, t0, t1, me, a):
        self.pic, self.t0, self.until, self.me, self.a = pic, t0, t1, me, a

    def _ends(self, t):
        x, y = self.me.pos(t)
        return (x, y - HAND), (self.a[0], self.a[1] - HAND)

    def frame(self, t):
        if not (self.t0 <= t < self.until):
            return None
        (x, y), (ax, ay) = self._ends(t)
        ang = math.degrees(math.atan2(-(ay - y), ax - x))
        return self.pic.rotate(ang, resample=Image.NEAREST, expand=False)

    def pos(self, t):
        (x, y), (ax, ay) = self._ends(t)
        return int(round((x + ax) / 2)), int(round((y + ay) / 2))


class Clip:
    """One scripted clip: his body's animations one after another, effects under / over the units, Darius."""

    def __init__(self, sp, d, me, small, big):
        self.sp, self.d, self.me, self.small, self.big = sp, d, me, small, big
        self.body, self.under, self.over, self.t = [], [], [], 0.0

    def a(self, tag, dur=None, loop=False):
        fr = list(dense(self.sp, tag, "akshan", 3))
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

    def at_spot(self, tag, when, x, y, sheet=None, under=False, until=None):
        an = Anim(frames_of(sheet or self.big, tag), when, int(x), int(y), loop=until is not None, until=until)
        (self.under if under else self.over).append(an)

    def fly(self, tag, t0, x0, x1, y, speed, y1=None):
        """A projectile from (x0, y) to (x1, y1) at `speed` units a tick (1000 a game px), its picture turned along the
        flight like the game does; returns its arrival time."""
        y1 = y if y1 is None else y1
        t1 = t0 + tick(math.hypot(x1 - x0, y1 - y) * 1000.0 / speed)
        fr = frames_of(self.small, tag)
        ang = math.degrees(math.atan2(-(y1 - y), x1 - x0))
        if abs(ang) > 90:
            fr = mirrored(fr)
            ang = ang - 180 if ang > 0 else ang + 180
        if abs(ang) >= 1:
            fr = [(f.rotate(ang, resample=Image.NEAREST, expand=True), ms) for f, ms in fr]
        self.over.append(Anim(fr, t0, int(x0), int(y), loop=True, until=t1, x1=int(x1), y1=int(y1)))
        return t1

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
    small, big = fx["league_akshan_fx"], fx["league_akshan_big"]
    W, H = 360, 130
    gy = 100
    x0 = 70
    dx_ = x0 + 60                                       # Darius within his attack range (55000)
    d = Foe(load(DARIUS), dx_, gy)
    me = ArcMe(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    muzzle = lambda: me.pos(c.t)[0] + 28
    c.wait(400)
    # the double shot: two bullets, a_hit1 and a_hit2 ticks in
    start = c.t
    for k in (P["a_hit1"], P["a_hit2"]):
        t1 = c.fly("a_shot", start + tick(1 + k), muzzle(), dx_, me.pos(c.t)[1] + GUN_Y, P["a_speed"], gy + GUN_Y)
        c.on("a_hit", t1)
        d.flinches.append(t1)
    c.a("attack", tick(P["atk_dur"]))
    c.wait(300)
    # Q Avengerang: out through Darius to its range, back to him; a hit each way - the out hit is the third (the burst
    # and his shield); the catch
    start = c.t + tick(3)
    sx = me.pos(c.t)[0] + 20
    far = sx + P["q_range"] / 1000.0
    turn = c.fly("q_rang", start, sx, far, me.pos(c.t)[1] + GUN_Y, P["q_speed"])
    back = c.fly("q_rang", turn, far, sx, me.pos(c.t)[1] + GUN_Y, P["q_back"])
    out_hit = start + tick((dx_ - sx) * 1000.0 / P["q_speed"])
    back_hit = turn + tick((far - dx_) * 1000.0 / P["q_back"])
    for t_ in (out_hit, back_hit):
        c.on("q_hit", t_)
        d.flinches.append(t_)
    c.on("p_hit", out_hit + 30)
    c.on_me("p_sh", out_hit + 30, until=out_hit + 30 + tick(P["p_sh_t"]))
    c.on_me("q_catch", back)
    c.a("skill", tick(P["q_dur"]))
    c.wait(back + 200 - c.t)
    # E Heroic Swing (the add-on's): the hook point beside the line to Darius, the swing round it on an arc with the rope
    # from his hand to the hook every frame, a shot at Darius every e_every ticks, then the roll back off
    start = c.t
    here = me.pos(start)
    a, a0, dirn = swing_plan((float(here[0]), float(here[1])), (float(dx_), float(gy)))
    c.a("skill2", tick(P["e_hook"]))
    swing_t = P["e_n"] * P["e_every"]
    t0, t1 = start + tick(2), c.t + tick(swing_t)
    me.arcs.append((t0, t1, a, a0, dirn))
    rope_pic = frames_of(small, "e_rope")[0][0]
    c.over.append(Rope(rope_pic, t0, t1, me, a))
    for k in range(P["e_n"]):
        ts = c.t + tick(k * P["e_every"] + 2)
        x, y = me.pos(ts)
        t_hit = c.fly("a_shot", ts, x + 28, dx_, y + GUN_Y - 6, P["e_shot"], gy + GUN_Y)
        c.on("a_hit", t_hit)
        d.flinches.append(t_hit)
    c.a("e_swing", tick(swing_t), loop=True)
    near = me.pos(c.t)[0]
    back_x = near - P["e_back"] * P["e_back_t"] / 1000.0
    me.moves.append((c.t, c.t + tick(P["e_back_t"]), near, back_x))
    t_hit = c.fly("a_shot", c.t + tick(2), near + 28, dx_, me.pos(c.t)[1] + GUN_Y, P["e_shot"], gy + GUN_Y)
    c.on("a_hit", t_hit)
    d.flinches.append(t_hit)
    c.a("e_roll", tick(P["e_back_t"] + 4))
    c.wait(300)
    # W Going Rogue: the camouflage and the speed streaks as he steps back
    start = c.t
    c.at_spot("w_camo", start, *me.pos(start))
    c.on_me("w_ms", start, until=start + tick(P["w_inv"]), under=True)
    x = me.pos(start)[0]
    me.moves.append((start, start + 700, x, x - 30))
    c.a("run", 700, loop=True)
    c.wait(300)
    # R Comeuppance: the lock sigil, the lock on Darius through the channel, five heavy rounds, Darius falls
    start = c.t
    c.at_spot("r_lock", start, *me.pos(start))
    c.a("ult", tick(8))
    c.a("ult_ch", tick(P["r_ch"] - 8), loop=True)
    c.on("r_sight", start, until=c.t)                   # the lock on Darius while he aims, off as he fires
    for k in range(P["r_n"]):
        ts = c.t + tick(k * P["r_gap"])
        t1 = c.fly("r_bullet", ts, me.pos(ts)[0] + 28, dx_, me.pos(ts)[1] + GUN_Y + 2, P["r_speed"], gy + GUN_Y + 2)
        c.on("r_hit", t1)
        d.flinches.append(t1)
        if k == P["r_n"] - 1:
            d.death = t1 + 60
    c.a("ult_shot", tick(P["r_n"] * P["r_gap"]), loop=True)
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_akshan_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_akshan_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_akshan_showcase.gif")))


if __name__ == "__main__":
    main()
