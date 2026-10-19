#!/usr/bin/env python3
"""Preview images for Zoe, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_zoe.py [--out docs/preview] [--only frames|effects|showcase]

  league_zoe_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_zoe_effects.png   every effect animation, 3x
  league_zoe_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_zoe.py, 60 ticks a
                           second): a little star; Paddle Star flying across the lane; More Sparkles!'s big star; the
                           Sleepy Trouble Bubble - drowsy, then asleep with the snore bubble; a Paddle Star wakes him
                           (the wake-up burst); Portal Jump - the portal she leaps into, the one she drops out of near
                           him, the portal's star, Spell Thief's three missiles and her haste, the leap away and back
                           home through the portals; 3x
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
from build_zoe import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_zoe")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_zoe_fx", "league_zoe_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")


class Clip:
    """One scripted clip: her body's animations one after another, effects under / over the units, Darius."""

    def __init__(self, sp, d, me, small, big):
        self.sp, self.d, self.me, self.small, self.big = sp, d, me, small, big
        self.body, self.under, self.over, self.t = [], [], [], 0.0

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "zoe", z))
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

    def fly(self, tag, t0, t1, x0, x1, y, sheet=None):
        """A projectile's picture flying in a straight line (drawn going right: these fly right)."""
        self.over.append(Anim(frames_of(sheet or self.small, tag), t0, int(x0), int(y), loop=True, until=t1,
                              x1=int(x1), y1=int(y)))

    def shot(self, tag, hit_tag, rel, speed, fly_tag=None):
        """A projectile from her hand to Darius at `speed` (game units a tick), its hit on him."""
        x0, x1 = self.me.pos(rel)[0] + 4, self.d.pos(rel)[0]
        hit = rel + tick((x1 - x0) * 1000.0 / speed)
        self.fly(fly_tag or tag, rel, hit, x0, x1, self.me.y - 14)
        self.on(hit_tag, hit)
        self.d.flinches.append(hit)
        return hit

    def attack(self, sparkly=False):
        rel = self.t + tick(P["a_rel"])
        hit = self.shot("p_star" if sparkly else "a_star", "p_hit" if sparkly else "a_hit", rel, P["a_speed"])
        self.a("attack_p" if sparkly else "attack", tick(P["atk_dur"]))
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
    small, big = fx["league_zoe_fx"], fx["league_zoe_big"]
    W, H = 260, 110
    gy = 86
    x0 = 50
    fx_ = x0 + 120                                      # Darius across the lane: Paddle Star's far end
    d = Foe(load(DARIUS), fx_, gy)
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.wait(400)
    c.attack()
    # Q Paddle Star across the lane
    c.shot("q_star", "q_hit", c.t + tick(P["q_rel"] - 1), P["q_speed"])
    c.a("skill", tick(P["q_dur"]))
    c.wait(200)
    # More Sparkles!: the next attack is the big star
    c.attack(sparkly=True)
    # E: the bubble, drowsy, asleep with the snore bubble
    hit = c.shot("e_bubble", "e_hit", c.t + tick(P["e_rel"] - 1), P["e_speed"])
    c.on("e_drowsy", hit, until=hit + tick(P["e_drowsy"]))
    sleep = hit + tick(P["e_drowsy"])
    c.on("e_zz", sleep, until=sleep + tick(P["e_sleep"]))
    c.a("skill2", tick(P["e_dur"]))
    c.wait(sleep + 300 - c.t)
    # a Paddle Star wakes him: the wake-up burst
    woke = c.shot("q_star", "q_hit", c.t + tick(P["q_rel"] - 1), P["q_speed"])
    c.on("e_wake", woke)
    c.a("skill", tick(P["q_dur"]))
    c.wait(300)
    # R: the portal she leaps into, the one she drops out of 50 px short of him, the portal's star, W's missiles
    start = c.t
    jump = start + tick(P["r_rel"] - 1)
    land_x = fx_ - P["r_stop"] / 1000.0
    c.at_spot("r_portal_in", jump, x0, gy)
    arrive = jump + tick(max(1, (land_x - x0) * 1000.0 / P["r_jspeed"]))
    me.moves.append((arrive, arrive + 1, x0, land_x))
    c.at_spot("r_portal_out", arrive, land_x, gy)
    c.a("ult", tick(P["r_dur"]))
    throw = jump + tick(P["r_throw"])
    c.wait(throw - c.t)
    c.shot("q_star", "q_hit", throw + tick(P["q_rel"] - 1), P["r_speed"])
    c.a("skill", tick(P["r_w"]))
    w0 = c.t
    for k in range(P["w_n"]):
        c.shot("w_missile", "w_hit", w0 + tick(P["w_rel"] - 1 + P["w_gap"] * k), P["w_speed"])
    c.on_me("w_haste", w0, until=w0 + tick(P["w_ms_t"]), under=True)
    c.a("skill_w", tick(P["w_dur"]))
    back = jump + tick(P["r_back"])
    c.wait(back - tick(P["r_exit"]) - c.t)
    c.a("ult_exit", tick(P["r_exit"]))
    c.at_spot("r_portal_in", back, land_x, gy)
    me.moves.append((back, back + 1, land_x, x0))
    c.at_spot("r_portal_out", back, x0, gy)
    c.a("ult_back", tick(P["r_back_dur"]))
    d.death = back + 300
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_zoe_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[11:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_zoe_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_zoe_showcase.gif")))


if __name__ == "__main__":
    main()
