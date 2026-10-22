#!/usr/bin/env python3
"""Preview images for Qiyana, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_qiyana.py [--out docs/preview] [--only frames|effects|showcase]

  league_qiyana_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_qiyana_effects.png   every effect animation, 3x
  league_qiyana_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_qiyana.py, 60 ticks a
                              second): Audacity from afar - the dash with the ring trailing, the slash, Terrashape's
                              swirl and the river on her ring; Edge of Ixtal at once (the combo E -> Q: the water sweep,
                              the freezing splash rooting him, the cold puddle slowing him), two attacks with the
                              enchant's extra strike and Royal Privilege's crown on the first; Supreme Display of Talent
                              (the great swing, the ground burst, the rolling shockwave knocking him back and stunning
                              him), Audacity again onto the stunned champion and the rock sweep (the combo R -> E -> Q:
                              the rock spikes, the rock burst) - he falls; 3x.
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
from build_qiyana import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_qiyana")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_qiyana_fx", "league_qiyana_big")}
DARIUS = os.path.join(LEAGUE, "champions", "league_darius")


class Qiyana(Clip):
    """preview_gnar's clip with her own dense frames."""

    def a(self, tag, dur=None, loop=False, z=3):
        fr = list(dense(self.sp, tag, "qiyana", z))
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
    small, big = fx["league_qiyana_fx"], fx["league_qiyana_big"]
    W, H = 300, 120
    gy = 100
    x0 = 90
    far = x0 + 120
    near = far - 26                                     # in her ring's reach (25 game px)
    d = Foe(load(DARIUS), far, gy)
    me = Me(x0, gy)
    c = Qiyana(load(CHAMP), d, me, small, big)
    c.wait(400)
    e_speed = P["e_speed"] / 1000.0 * 60 / 1000          # game px a ms

    def audacity(start_x, element):
        """E: the dash onto him, the slash, Terrashape's swirl and the element on her ring."""
        go = c.t
        land = go + (near - start_x) / e_speed
        me.moves.append((go, land, start_x, near))
        c.a("skill2", max(tick(P["e_dur"]), land - go + tick(P["e_at"])))
        hit = land + tick(P["e_at"])
        c.on("e_hit", hit)
        c.on("p_hit", hit)
        c.d.flinches.append(hit)
        c.on_me("w_on", hit)
        c.on_me(element, hit, until=c.t + tick(P["q_at"]))    # held until the Q that follows spends it
        return hit

    def sweep(tag, hit_fx):
        """Q by the element on her ring: the cast's own tag (the sweep is in her frames), its hit on him."""
        t = c.t
        c.a(tag, tick(P["q_dur"]))
        hit = t + tick(P["q_at"])
        c.on(hit_fx, hit)
        c.d.flinches.append(hit)
        return hit

    # E -> Q: the dash with the river on her ring, the water sweep at once - rooted, then slowed
    audacity(x0, "el_w")
    hit = sweep("skill_w", "q_w_hit")
    c.on("q_slow", hit + tick(P["q_root"]), until=hit + tick(P["q_root"] + P["q_slow_t"]))
    # two attacks with the enchant gone (Q spent it) - the plain strike
    for _ in range(2):
        h = c.t + tick(P["a_hit"])
        c.on("a_hit", h)
        c.d.flinches.append(h)
        c.a("attack", tick(P["atk_dur"]))
        c.wait(tick(P["atk_cd"] - P["atk_dur"]) // 2)
    # R: the great swing and the ground burst (in her frames), the shockwave rolling at him, knocked back and stunned
    t = c.t
    c.a("ult", tick(P["r_dur"]))
    rel = t + tick(P["r_at"])
    speed = P["r_speed"] / 1000.0 * 60 / 1000
    hit = rel + (far - near) / speed
    c.fly("r_wave", rel, hit + 120, near, far + 10, gy - 11, sheet=big)
    c.on("r_hit", hit)
    c.d.flinches.append(hit)
    # R -> E -> Q: the dash onto the stunned champion with rock on her ring, the rock sweep
    c.wait(max(0, hit + tick(P["r_kb_t"]) - c.t))
    audacity(near, "el_r")
    h = sweep("skill_r", "q_r_hit")
    d.death = h + 200
    end = h + 1600
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_qiyana_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_qiyana_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_qiyana_showcase.gif")))


if __name__ == "__main__":
    main()
