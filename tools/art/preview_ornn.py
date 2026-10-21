#!/usr/bin/env python3
"""Preview images for Ornn, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_ornn.py [--out docs/preview] [--only frames|effects|showcase]

  league_ornn_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_ornn_effects.png   every effect animation, 3x
  league_ornn_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_ornn.py, 60 ticks a
                            second): Volcanic Rupture - the molten fist slams, the fissure runs through him and a magma
                            pillar rises behind him; Searing Charge into it (Q -> E) - the pillar shatters, the quake
                            knocks him up and leaves him Brittle; the hammer breaks Brittle (a knock-back); Bellows
                            Breath - the fire from his mouth, the shield of heat round him, five pulses, Brittle again;
                            Call of the Forge God - the ram bursts up far behind Darius and charges back through him to
                            Ornn, who headbutts it back (R1 -> R2): the second ram knocks him up; the hammer breaks
                            Brittle and Darius falls; 3x
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
from preview_pyke import Me, OnFoe, OnMe, mirrored  # noqa: E402
from preview_zyra import Walker  # noqa: E402
from build_ornn import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_ornn")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_ornn_fx", "league_ornn_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")
LIFT = 5                        # a LinearProjectile with y_offset 0 runs 5 px north of the pivots (champion-data.md)
CONTACT = 14                    # px between the pivots when his charge meets Darius
SECOND = 1000 / 60


def px(units):
    return units / 1000.0


class Clip:
    """One scripted clip: his body's animations one after another, effects under / over the units, Darius."""

    def __init__(self, sp, d, me, small, big):
        self.sp, self.d, self.me, self.small, self.big = sp, d, me, small, big
        self.body, self.under, self.over, self.t = [], [], [], 0.0

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "ornn", z))
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

    def at_spot(self, tag, when, x, y, sheet=None, under=True, until=None, loop=False):
        an = Anim(frames_of(sheet or self.big, tag), when, int(x), int(y), loop=loop, until=until)
        (self.under if under else self.over).append(an)

    def fly(self, fr, t0, t1, x0, x1, y):
        """A projectile's picture moving in a straight line (looped)."""
        self.over.append(Anim(fr, t0, int(x0), int(y), loop=True, until=t1, x1=int(x1), y1=int(y)))

    def brittle(self, when, until):
        """Brittle's mark over his head (import_ornn_fx HEAD) from `when` until it breaks or runs out."""
        self.on("brittle", when, until=min(until, when + tick(P["br_t"])))

    def attack(self, pop=None):
        """The hammer's blow: its hit on Darius at atk_st; `pop` (Brittle on him): it breaks - true damage, knocked
        back and up - and returns the tick (ms) it broke."""
        hit = self.t + tick(P["atk_st"])
        self.on("a_hit", hit)
        self.d.flinches.append(hit)
        if pop:
            self.on("br_pop", hit)
            back = px(P["br_kb_speed"] * P["br_kb_t"])
            self.d.slides.append((hit, hit + tick(P["br_kb_t"]), back))
            self.d.hops.append((hit, hit + tick(P["br_up"]), 5))
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
    small, big = fx["league_ornn_fx"], fx["league_ornn_big"]
    W, H = 260, 104
    gy = 70                                             # the pivot row
    x0 = 34
    d = Walker(load(DARIUS), x0 + 62, gy)               # far enough that the pillar rises just behind him
    me = Me(x0, gy)
    c = Clip(load(CHAMP), d, me, small, big)
    c.wait(400)

    # Q Volcanic Rupture: the fist slams on q_rel, the fissure runs q_len (through Darius), the pillar rises at its end
    rel = c.t + tick(P["q_rel"] - 1)
    c.at_spot("q_slam", rel, x0, gy)
    step = px(P["q_speed"])
    dx = d.x - x0
    hit = rel + tick(dx / step)
    end_q = rel + tick(px(P["q_len"]) / step)
    c.fly(frames_of(big, "q_fissure"), rel, end_q, x0, x0 + px(P["q_len"]), gy - LIFT)
    c.on("q_hit", hit)
    d.flinches.append(hit)
    c.a("skill", tick(P["q_dur"]))
    pillar_x = x0 + px(P["q_len"])

    # E Searing Charge into the pillar (Q -> E): he runs at Darius, the contact's blow, the quake breaks the pillar
    t_e = c.t
    to = d.x - CONTACT
    arrive = t_e + tick((to - x0) / px(P["e_speed"]))
    me.moves.append((t_e, arrive, x0, to))
    c.a("skill2", arrive - t_e, loop=True)
    c.on("e_hit", arrive)
    c.at_spot("e_quake", arrive, to, gy)
    d.hops.append((arrive, arrive + tick(P["e_up"]), 12))
    c.a("skill2_hit", tick(P["e_hit_t"]))
    # the pillar: risen at the fissure's end, a stamp every q_stamp ticks until the charge broke it
    c.at_spot("q_rise", end_q, pillar_x, gy, under=False)
    t = end_q + tick(P["q_stamp"])
    while t < arrive:
        c.at_spot("q_pillar", t, pillar_x, gy, under=False, until=min(arrive, t + tick(P["q_stamp"])))
        t += tick(P["q_stamp"])
    c.wait(arrive + tick(P["e_up"]) - c.t)

    # the hammer breaks Brittle (knocked back)
    pop = c.t + tick(P["atk_st"])
    c.brittle(arrive, pop)
    c.attack(pop=True)

    # W Bellows Breath (the fire drawn into his frames): the heat shield on him, five pulses, Brittle on the last
    t_w = c.t
    c.over.append(OnMe(frames_of(small, "w_shown"), t_w, me, until=t_w + tick(P["w_sh_t"])))
    last = None
    for k in range(P["w_n"]):
        ts = t_w + tick(P["w_first"] + k * P["w_gap"])
        c.on("w_hit", ts)
        d.flinches.append(ts)
        last = ts
    c.a("skill_w", tick(P["w_t"]))
    c.wait(300)

    # R Call of the Forge God: the call, the ram bursting up r_len away and charging back through Darius to him; the
    # headbutt sends the second ram out through Darius (R1 -> R2)
    t_r = c.t
    ox = me.pos(t_r)[0]
    rel = t_r + tick(P["r_rel"] - 1)
    c.at_spot("r_call", rel, ox, gy)
    out_t = math.ceil(P["r_len"] / P["r_out"])
    run_t = math.ceil(P["r_len"] / P["r_speed"])
    far = ox + px(P["r_len"])
    rise = rel + tick(out_t)
    c.at_spot("r_rise", rise, far, gy, under=False)
    back_at = t_r + tick(P["r_rel"] + out_t + run_t)
    c.fly(mirrored(frames_of(big, "r_ram")), rise, back_at, far, ox, gy)
    dist = d.pos(rise)[0] - ox
    hit1 = rise + tick((px(P["r_len"]) - dist) / px(P["r_speed"]))
    c.on("r_hit", hit1)
    d.flinches.append(hit1)
    c.a("ult", back_at - t_r)
    butt = back_at + tick(P["r_butt_rel"])
    c.at_spot("r_butt", butt, ox, gy, under=False)
    gone = butt + tick(px(P["r_len"]) / px(P["r2_speed"]))
    c.fly(frames_of(big, "r_ram2"), butt, gone, ox, far, gy - LIFT)
    hit2 = butt + tick(dist / px(P["r2_speed"]))
    c.on("r_hit", hit2)
    d.hops.append((hit2, hit2 + tick(P["r2_up"]), 14))
    c.a("ult_butt", tick(P["r_butt_t"]))
    c.wait(hit2 + tick(P["r2_up"]) - c.t)

    # the hammer breaks Brittle (left by the breath and both rams) and Darius falls
    pop = c.t + tick(P["atk_st"])
    c.brittle(last, pop)
    c.attack(pop=True)
    d.death = pop + tick(P["br_up"])
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_ornn_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[12:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_ornn_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_ornn_showcase.gif")))


if __name__ == "__main__":
    main()
