#!/usr/bin/env python3
"""Preview images for Akshan, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_akshan.py [--out docs/preview] [--only frames|effects|showcase]

  league_akshan_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_akshan_effects.png   every effect animation, 3x
  league_akshan_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_akshan.py, 60 ticks a
                              second): the double shot (two bullets, two hits); Q - the boomerang out through Darius and
                              back, a hit each way, the third hit's Sentinel burst and his shield, the catch; E - the hook
                              shot up, the swing with a shot at Darius every e_every ticks, the roll back; W - the
                              camouflage and the speed streaks as he steps back; R - the lock sigil, the channel, five
                              heavy rounds and Darius falls; 3x
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

    def fly(self, tag, t0, x0, x1, y, speed):
        """A projectile from x0 to x1 at `speed` units a tick (1000 a game px); returns its arrival time."""
        t1 = t0 + tick(abs(x1 - x0) * 1000.0 / speed)
        fr = frames_of(self.small, tag)
        if x1 < x0:
            fr = mirrored(fr)
        self.over.append(Anim(fr, t0, int(x0), int(y), loop=True, until=t1, x1=int(x1), y1=int(y)))
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
    small, big = fx["league_akshan_fx"], fx["league_akshan_big"]
    W, H = 360, 130
    gy = 100
    x0 = 70
    dx_ = x0 + 60                                       # Darius within his attack range (55000)
    d = Foe(load(DARIUS), dx_, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    muzzle = lambda: me.pos(c.t)[0] + 28
    c.wait(400)
    # the double shot: two bullets, a_hit1 and a_hit2 ticks in
    start = c.t
    for k in (P["a_hit1"], P["a_hit2"]):
        t1 = c.fly("a_shot", start + tick(1 + k), muzzle(), dx_, gy + GUN_Y, P["a_speed"])
        c.on("a_hit", t1)
        d.flinches.append(t1)
    c.a("attack", tick(P["atk_dur"]))
    c.wait(300)
    # Q Avengerang: out through Darius to its range, back to him; a hit each way - the out hit is the third (the burst
    # and his shield); the catch
    start = c.t + tick(3)
    sx = me.pos(c.t)[0] + 20
    far = sx + P["q_range"] / 1000.0
    turn = c.fly("q_rang", start, sx, far, gy + GUN_Y, P["q_speed"])
    back = c.fly("q_rang", turn, far, sx, gy + GUN_Y, P["q_back"])
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
    # E Heroic Swing: the hook up, the swing toward Darius shooting every e_every, the roll back off
    start = c.t
    spot = me.pos(start)[0]
    c.at_spot("e_hook", start, spot, gy)
    c.a("skill2", tick(P["e_hook"]))
    swing_t = P["e_n"] * P["e_every"]
    near = dx_ - 34
    me.moves.append((c.t, c.t + tick(swing_t), spot, near))
    for k in range(P["e_n"]):
        ts = c.t + tick(k * P["e_every"] + 2)
        x = spot + (near - spot) * (k * P["e_every"] + 2) / swing_t
        t1 = c.fly("a_shot", ts, x + 28, dx_, gy + GUN_Y - 6, P["e_shot"])
        c.on("a_hit", t1)
        d.flinches.append(t1)
    c.a("e_swing", tick(swing_t), loop=True)
    back_x = near - P["e_back"] * P["e_back_t"] / 1000.0
    me.moves.append((c.t, c.t + tick(P["e_back_t"]), near, back_x))
    t1 = c.fly("a_shot", c.t + tick(2), near + 28, dx_, gy + GUN_Y, P["e_shot"])
    c.on("a_hit", t1)
    d.flinches.append(t1)
    c.a("e_roll", tick(P["e_back_t"] + 4))
    c.wait(300)
    # W Going Rogue: the camouflage and the speed streaks as he steps back
    start = c.t
    c.at_spot("w_camo", start, me.pos(start)[0], gy)
    c.on_me("w_ms", start, until=start + tick(P["w_inv"]), under=True)
    x = me.pos(start)[0]
    me.moves.append((start, start + 700, x, x - 30))
    c.a("run", 700, loop=True)
    c.wait(300)
    # R Comeuppance: the lock sigil, the channel, five heavy rounds, Darius falls
    start = c.t
    c.at_spot("r_lock", start, me.pos(start)[0], gy)
    c.a("ult", tick(8))
    c.a("ult_ch", tick(P["r_ch"] - 8), loop=True)
    for k in range(P["r_n"]):
        ts = c.t + tick(k * P["r_gap"])
        t1 = c.fly("r_bullet", ts, me.pos(ts)[0] + 28, dx_, gy + GUN_Y + 2, P["r_speed"])
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
