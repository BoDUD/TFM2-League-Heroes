#!/usr/bin/env python3
"""Preview images for Quinn, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_quinn.py [--out docs/preview] [--only frames|effects|showcase]

  league_quinn_frames.png    every animation's dense frames (hd_, as league.dll shows them)
  league_quinn_effects.png   every effect animation, 3x
  league_quinn_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_quinn.py, 60 ticks a
                             second), Valor circling over her head whenever he is with her: a bolt; Harrier - Valor
                             dives on Darius, the marked bolt, Heightened Senses at her feet; Blinding Assault - Valor
                             flies out, bursts on Darius (the disarmed eye over him) and flies home; Vault - the dash,
                             the kick, the slow at his feet, the somersault back; Behind Enemy Lines - the call, the
                             ride at him, Skystrike's landing; 3x
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
from build_quinn import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_quinn")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_quinn_fx", "league_quinn_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")


def mirrored(frames):
    """A projectile's frames flying left: turned half round by the game - for these top-to-bottom symmetric pictures
    the same as mirrored left to right."""
    return [(f.transpose(Image.FLIP_LEFT_RIGHT), ms) for f, ms in frames]


class Clip:
    """One scripted clip: her body's animations one after another, effects under / over the units, Darius."""

    def __init__(self, sp, d, me, small, big):
        self.sp, self.d, self.me, self.small, self.big = sp, d, me, small, big
        self.body, self.under, self.over, self.t = [], [], [], 0.0

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "quinn", z))
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

    def fly(self, tag, t0, t1, x0, x1, y, sheet=None, back=False):
        """A projectile's picture flying in a straight line (drawn going right; back: flying left)."""
        fr = frames_of(sheet or self.small, tag)
        self.over.append(Anim(mirrored(fr) if back else fr, t0, int(x0), int(y), loop=True, until=t1, x1=int(x1),
                              y1=int(y)))

    def shot(self, tag, hit_tag, rel, speed):
        """A projectile from her crossbow to Darius at `speed` (game units a tick), its hit on him."""
        x0, x1 = self.me.pos(rel)[0] + 6, self.d.pos(rel)[0]
        hit = rel + tick((x1 - x0) * 1000.0 / speed)
        self.fly(tag, rel, hit, x0, x1, self.me.y - 12)
        if hit_tag:
            self.on(hit_tag, hit)
        self.d.flinches.append(hit)
        return hit

    def attack(self, harrier=False):
        rel = self.t + tick(P["a_hit"] - 1)
        if harrier:
            self.on("p_dive", self.t, sheet=self.big)
        hit = self.shot("a_bolt", "p_hit" if harrier else "a_hit", rel, P["a_speed"])
        if harrier:
            self.on_me("w_haste", hit, until=hit + tick(P["w_t"]), under=True)
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
    small, big = fx["league_quinn_fx"], fx["league_quinn_big"]
    W, H = 260, 110
    gy = 86
    x0 = 60
    fx_ = x0 + 70                                       # Darius in her attack range (52500)
    d = Foe(load(DARIUS), fx_, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    away = []                                           # spans Valor is away from her head

    c.wait(400)
    c.attack()
    # Harrier: Valor dives on Darius, the marked bolt, Heightened Senses
    dive = c.t
    away.append((dive, dive + tick(P["dive_t"])))
    c.attack(harrier=True)
    c.wait(200)
    # Q Blinding Assault: Valor out, the burst, the disarmed eye, Valor home
    q0 = c.t
    rel = q0 + tick(P["q_rel"] - 1)
    x_from, x_to = me.pos(rel)[0] + 4, d.pos(rel)[0]
    hit = rel + tick((x_to - x_from) * 1000.0 / P["q_speed"])
    c.fly("q_bird", rel, hit, x_from, x_to, gy - 22)
    c.at_spot("q_burst", hit, x_to, gy)
    c.on("q_hit", hit)
    c.on("q_blind", hit, until=hit + tick(P["q_blind"]))
    d.flinches.append(hit)
    home = hit + tick((x_to - x_from) * 1000.0 / P["q_back"])
    c.fly("q_bird", hit, home, x_to, x_from, gy - 22, back=True)
    away.append((q0, home))
    c.a("skill", tick(P["q_dur"]))
    c.wait(home - c.t + 200)
    # E Vault: the dash, the kick, the slow, the somersault back
    e0 = c.t
    start = me.pos(e0)[0]
    reach_x = d.pos(e0)[0] - 10
    arrive = e0 + tick(max(1, (reach_x - start) * 1000.0 / P["e_speed"]))
    me.moves.append((e0, arrive, start, reach_x))
    c.a("skill2", arrive - e0, loop=True)
    c.on("e_hit", arrive)
    c.on("e_slow", arrive, until=arrive + tick(P["e_slow_t"]))
    d.flinches.append(arrive)
    back_x = reach_x - P["e_back"] * P["e_back_t"] / 1000.0
    me.moves.append((arrive, arrive + tick(P["e_back_t"]), reach_x, back_x))
    c.a("e_flip", tick(P["e_flip"]))
    c.wait(500)
    # R Behind Enemy Lines: the call, the ride, Skystrike
    r0 = c.t
    c.on_me("r_call", r0, sheet=big)
    c.a("ult", tick(P["r_mount"]))
    ride0 = c.t
    from_x = me.pos(ride0)[0]
    land_x = d.pos(ride0)[0] - 14
    land = ride0 + tick(max(1, (land_x - from_x) * 1000.0 / P["r_speed"]))
    me.moves.append((ride0, land, from_x, land_x))
    c.a("ult_ride", land - ride0, loop=True)
    c.at_spot("r_land", land, land_x, gy)
    c.on("r_hit", land)
    d.flinches.append(land)
    c.a("ult_land", tick(P["r_land"]))
    away.append((r0, c.t))
    d.death = land + 300
    end = d.death + 1400
    c.wait(end - c.t)
    # Valor over her head the rest of the time
    t = 0.0
    for a0, a1 in sorted(away):
        if a0 > t:
            c.on_me("valor", t, sheet=big, until=a0)
        t = max(t, a1)
    if t < end:
        c.on_me("valor", t, sheet=big, until=end)
    return c.render(out, W, H, end, z)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    ap.add_argument("--only", choices=["frames", "effects", "showcase"])
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    if args.only in (None, "frames"):
        s = load(CHAMP)
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_quinn_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_quinn_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_quinn_showcase.gif")))


if __name__ == "__main__":
    main()
