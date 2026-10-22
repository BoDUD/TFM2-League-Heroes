#!/usr/bin/env python3
"""Preview images for Udyr, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_udyr.py [--out docs/preview] [--only frames|effects|showcase]

  league_udyr_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them), his four stances
  league_udyr_effects.png   every effect animation, 3x
  league_udyr_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_udyr.py, 60 ticks a
                            second): Blazing Stampede from afar - the stamp, the ram's sigil, the charge with its fire
                            trail, the stunning blow (Iron Mantle's jade shell closing round him: his first ability);
                            Wilding Claw awakened at once (the combo E -> Q: the bear's roar and its lightning), two
                            bear swipes calling lightning on him; Wingborne Storm (the combo Q -> R: the phoenix taking
                            wing, the glacial storm whirling round him, faster), two phoenix strikes, the storm unleashed
                            at him as it ends - he falls; 3x. Idle, run and the stance's own frames as the add-on's view
                            hook shows them (q_idle, e_idle, r_idle).
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
from preview_ashe import Anim, tick  # noqa: E402
from preview_dense import dense, dense_rows  # noqa: E402
from preview_garen import T, contact, frames_of, load  # noqa: E402
from preview_gnar import Clip  # noqa: E402
from preview_kindred import fx_contact  # noqa: E402
from preview_leesin import Foe  # noqa: E402
from preview_pyke import Me  # noqa: E402
from build_udyr import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_udyr")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_udyr_fx", "league_udyr_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")


class Udyr(Clip):
    """preview_gnar's clip with his own dense frames."""

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "udyr", z))
        if dur and not loop and dur > sum(ms for _, ms in fr):     # the last frame held to the action's end
            fr[-1] = (fr[-1][0], fr[-1][1] + dur - sum(ms for _, ms in fr))
        an = Anim(fr, self.t, 0, 0, loop=loop, until=(self.t + dur) if dur else None)
        an.pos = self.me.pos
        self.body.append(an)
        self.t = an.until
        return an

    def fly(self, tag, t0, t1, x0, x1, y, sheet=None):
        """A projectile's picture flying from x0 to x1 (drawn flying right: the right way here)."""
        self.over.append(Anim(frames_of(sheet or self.small, tag), t0, x0, y, loop=True, until=t1, x1=x1, y1=y))


def showcase(out, z=3):
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_udyr_fx"], fx["league_udyr_big"]
    W, H = 300, 120
    gy = 100
    x0 = 100
    far = x0 + 110
    near = far - 26                                     # in his punch's reach (25 game px)
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Udyr(load(CHAMP), d, me, small, big)
    c.wait(400)
    # E Blazing Stampede: the stamp and the ram's sigil, Iron Mantle (his first ability), the charge with its fire
    # trail, the stunning blow
    t = c.t
    c.on_me("e_on", t, )
    c.on_me("w_on", t, sheet=big)
    c.on_me("w_sh", t + 470, sheet=big, until=t + tick(P["w_sh_t"]))
    c.on_me("e_ms", t, until=t + tick(P["e_t"]), under=True)
    c.a("skill2", tick(P["e_dur"]))
    e_speed = P["e_speed"] / 1000.0 * 60 / 1000          # game px a ms
    go = c.t
    land = go + (near - x0) / e_speed
    me.moves.append((go, land, x0, near))
    c.a("e_charge", land - go)
    blow = c.t + tick(P["e_hit"])
    c.on("e_hit", blow)
    c.on("e_stun", blow + 60, until=blow + tick(P["e_stun"]))
    c.d.flinches.append(blow)
    c.a("e_stun", tick(P["e_hit_dur"]))
    c.idle = "e_idle"
    c.wait(120)
    # Q Wilding Claw, awakened by the stun (E -> Q): the bear's roar and its lightning round him, two swipes calling
    # lightning on him
    t = c.t
    c.on_me("q_wake", t, sheet=big)
    c.on_me("q_as", t + 200, until=t + tick(P["q_t"]), under=True)
    c.a("skill", tick(P["q_dur"]))
    c.idle = "q_idle"
    for _ in range(2):
        hit = c.t + tick(P["a_hit"])
        c.on("q_hit", hit)
        c.on("q_bolt_hit", hit + 60, sheet=big)
        c.d.flinches.append(hit)
        c.a("q_attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]) // 2)
    # R Wingborne Storm (Q -> R: the storm whirls faster): the phoenix taking wing, the storm round him, two strikes,
    # the storm unleashed at him as it ends
    t = c.t
    c.on_me("r_on", t)
    gap = tick(P["r_fast"])
    k = P["r_t"] // P["r_fast"]
    first = t + tick(P["r_at"])
    c.on_me("r_storm", first - 100, sheet=big, until=first + k * gap)
    for i in range(k):
        c.on("r_hit", first + i * gap)
    c.on("r_slow", first, until=first + k * gap + 600)
    c.a("ult", tick(P["r_dur"]))
    c.idle = "r_idle"
    while c.t < first + k * gap - tick(P["atk_dur"]):
        hit = c.t + tick(P["a_hit"])
        c.on("a_hit", hit)
        c.d.flinches.append(hit)
        c.a("r_attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]) // 2)
    rel = first + k * gap
    c.wait(max(0, rel - c.t))
    speed = P["r2_speed"] / 1000.0 * 60 / 1000
    hit = rel + 20 / speed
    c.fly("r_rel", rel, hit, near - 4, far, gy - 16, sheet=big)
    c.on("r_rel_hit", hit, sheet=big)
    c.d.flinches.append(hit)
    d.death = hit + 200
    end = hit + 1600
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_udyr_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[12:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_udyr_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_udyr_showcase.gif")))


if __name__ == "__main__":
    main()
