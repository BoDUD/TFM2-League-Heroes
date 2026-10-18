#!/usr/bin/env python3
"""Preview images for Wukong, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_wukong.py [--out docs/preview] [--only frames|effects|showcase]

  league_wukong_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_wukong_effects.png   every effect animation, 3x
  league_wukong_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_wukong.py, 60 ticks a
                              second): E - he rides his cloud onto Darius, the images strike, the landing's clouds; an
                              attack; the Crushing Blow - the staff shot out, the hit and the armour break over Darius's
                              head; W - the poof, he dashes behind Darius (turned round), the clone stands where he was and
                              taps Darius every second; R - he spins (the whirl round him, a hit every r_every ticks, the
                              first one knocking up), the clone spins with him; a second spin and Darius falls; 3x
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
from build_wukong import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_wukong")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_wukong_fx", "league_wukong_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")


class Clip:
    """One scripted clip: his body's animations one after another, effects under / over the units, Darius."""

    def __init__(self, sp, d, me, small, big):
        self.sp, self.d, self.me, self.small, self.big = sp, d, me, small, big
        self.body, self.under, self.over, self.t = [], [], [], 0.0
        self.turned = False

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "wukong", z))
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
    small, big = fx["league_wukong_fx"], fx["league_wukong_big"]
    W, H = 320, 120
    gy = 86
    x0 = 70
    fx_ = x0 + 90                                       # Darius within E's reach
    d = Foe(load(DARIUS), fx_, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.wait(400)
    # E Nimbus Strike: onto Darius on the cloud (e_speed a tick), the images' strike and the landing's clouds
    start = c.t
    stop = fx_ - 22
    arrive = start + tick(1 + (stop - x0) * 1000.0 / P["e_speed"])
    me.moves.append((start + tick(1), arrive, x0, stop))
    c.on_me("e_cloud", start, big)
    c.at_spot("e_land", arrive, stop, gy, under=True)
    c.on("e_hit", arrive)
    d.flinches.append(arrive)
    c.a("skill", tick(P["e_dur"]))
    c.wait(arrive + 200 - c.t)
    # an attack, then the Crushing Blow (the staff shot out): the hit and the armour break over Darius's head
    hit = c.t + tick(1 + 2 + P["a_hit"])
    c.on("a_hit", hit)
    d.flinches.append(hit)
    c.a("attack", tick(P["atk_dur"]))
    c.wait(tick(P["atk_cd"] - P["atk_dur"]))
    hit = c.t + tick(1 + 2 + P["q_hit"])
    c.on("q_hit", hit)
    c.on("q_shred", hit, until=hit + tick(P["q_shred_t"]))
    d.flinches.append(hit)
    c.a("q_attack", tick(P["q_anim"]))
    c.wait(300)
    # W Warrior Trickster: the poof where he stood, the dash through to Darius's back (turned round), the clone left
    # standing there for w_t ticks: a picture a slot, a tap on Darius every w_period
    start = c.t
    spot = me.pos(start)[0]
    behind = fx_ + 20
    c.at_spot("w_poof", start, spot, gy, under=False)
    me.moves.append((start + tick(1), start + tick(1 + (behind - spot) * 1000.0 / P["w_dash"]), spot, behind))
    clone0 = start + tick(1)
    c.turned = True
    c.a("skill2", tick(P["w_dur"]))
    c.wait(400)
    # R Cyclone: the spin with the whirl round him, a hit every r_every ticks (the first knocks up); the clone spins too
    spin0 = c.t
    spins = [spin0, spin0 + tick(P["r_t"]) + 700]

    def clone_pic(t):
        for s in spins:
            if s <= t < s + tick(P["r_t"]):
                return "w_clone_spin"
        return None
    slot_ms = tick(P["w_slot"])
    k = 0
    while clone0 + k * slot_ms < clone0 + tick(P["w_t"]):
        ts = clone0 + k * slot_ms
        tag = clone_pic(ts) or ("w_clone_atk" if k % (P["w_period"] // P["w_slot"]) == 0 else "w_clone")
        c.at_spot(tag, ts, spot, gy, under=True)
        if tag == "w_clone_atk":
            c.on("w_hit", ts + tick(8))
            d.flinches.append(ts + tick(8))
        k += 1
    for n, s in enumerate(spins):
        if s > c.t:
            c.wait(s - c.t)
        c.on_me("r_on", s, big, until=s + tick(P["r_t"]), under=True)
        for t_ in range(1, P["r_t"], P["r_every"]):
            c.on("r_hit", s + tick(t_))
            d.flinches.append(s + tick(t_))
        if n == len(spins) - 1:
            d.death = s + tick(P["r_t"] - 10)
        c.a("spin", tick(P["r_t"]), loop=True)
    end = c.t + 1200
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_wukong_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_wukong_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_wukong_showcase.gif")))


if __name__ == "__main__":
    main()
