#!/usr/bin/env python3
"""Preview images for Senna, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_senna.py [--out docs/preview] [--only frames|effects|showcase]

  league_senna_frames.png    every animation, frame by frame, 3x on the arena colour
  league_senna_effects.png   every effect animation, 3x
  league_senna_showcase.gif  a scripted fight with Darius in front and Garen (an ally) beside her, timed like the kit
                             (tools/kit/build_senna.py, 60 ticks a second): an attack marks Darius (Absolution);
                             Q - the beam from the muzzle through Darius (hit, slow) and Garen on its line (heal); the
                             next attack tears the soul out of the marked Darius and the Mist comes to her cannon; W -
                             the Black Mist flies, clings to Darius and bursts a second later (root); E - the Mist
                             wells up round her (her and Garen faster); R - the dark core and the wall of holy light
                             roll down the line: Darius hit, Garen shielded; 3x
"""
import argparse
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
from preview_annie import Held  # noqa: E402
from preview_ashe import Anim, tick  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_pyke import Me, OnFoe, OnMe  # noqa: E402
from build_senna import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_senna")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_senna_fx", "league_senna_big")}
SHOT = P["a_speed"] / 1000                       # px a tick
MIST = P["w_speed"] / 1000
LIGHT = P["r_speed"] / 1000
LIFT = (5000 - P["a_y"]) // 1000                 # the shots fly 7 px over the pivot


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_senna_fx"], fx["league_senna_big"]
    W, H = 260, 110
    gy = 80
    x0 = 36
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 64, gy + 2)    # in her attack's reach
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 34, gy - 16)    # her ally, inside Q's band
    g.mirrored = False                                                                      # facing the foe with her
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        x, y = me.pos(t)
        an = Anim(frames_of(sp, tag), t, x, y, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def fly(tag, sheet, when, x1, speed, lift=LIFT):
        """A shot from her pivot (the lead frames hide it inside the cannon) to x1; returns its arrival."""
        sx, y = me.pos(when)
        arrive = when + tick(max(1, abs(x1 - sx) / speed))
        over.append(Anim(frames_of(sheet, tag), when, sx, y - lift, until=arrive, x1=x1, y1=y - lift))
        return arrive

    def hit(foe, tag, when, sheet=None):
        over.append(OnFoe(frames_of(sheet or small, tag), when, foe))
        foe.flinches.append(when)

    a("idle", 400, loop=True)
    # an attack marks Darius
    rel = t + tick(P["a_st"])
    marked = fly("a_shot", small, rel, d.x, SHOT)
    hit(d, "a_hit", marked)
    a("attack", tick(P["atk_dur"]))
    a("idle", 160, loop=True)
    # Q: the beam from the muzzle through Garen (heal) and Darius (hit, slow)
    rel = t + tick(P["q_st"])
    over.append(Anim(frames_of(big, "q_beam"), rel, me.pos(rel)[0] + P["q_len"] // 2000, gy))
    hit(d, "q_hit", rel + tick(1))
    under.append(OnFoe(frames_of(small, "q_slow"), rel + tick(1), d, until=rel + tick(1 + P["q_slow_t"])))
    over.append(OnFoe(frames_of(small, "q_heal"), rel + tick(1), g))
    a("skill", tick(P["q_dur"]))
    a("idle", 160, loop=True)
    # the next attack takes the mark: the soul torn out, the Mist to her cannon
    rel = t + tick(P["a_st"])
    took = fly("a_shot", small, rel, d.x, SHOT)
    over.append(OnFoe(frames_of(small, "p_mark"), marked, d, until=took))
    hit(d, "a_hit", took)
    over.append(OnFoe(frames_of(small, "p_take"), took, d))
    over.append(OnMe(frames_of(small, "p_gain"), took + 300, me))
    a("attack", tick(P["atk_dur"]))
    a("idle", 300, loop=True)
    # W: the Black Mist clings to Darius, bursts w_wait ticks later and roots him
    rel = t + tick(P["w_st"])
    land = fly("w_mist", small, rel, d.x, MIST)
    hit(d, "w_hit", land)
    over.append(OnFoe(frames_of(small, "w_cling"), land, d, until=land + tick(P["w_wait"])))
    burst = land + tick(P["w_wait"])
    over.append(Anim(frames_of(big, "w_burst"), burst, d.x, d.y))
    under.append(OnFoe(frames_of(small, "w_root"), burst + tick(2), d, until=burst + tick(2 + P["w_root"])))
    d.holds.append((burst + tick(2), burst + tick(2 + P["w_root"])))
    a("skill2", tick(P["w_dur"]))
    a("idle", max(200, burst - t + 300), loop=True)
    # E: the Mist wells up round her, she and Garen faster
    under.append(Anim(frames_of(big, "e_mist"), t, *me.pos(t)))
    under.append(OnMe(frames_of(small, "e_ms"), t, me, until=t + 1200))
    under.append(OnFoe(frames_of(small, "e_ms"), t, g, until=t + 1200))
    a("idle", 1000, loop=True)
    # R: the core and the light roll down the line
    rel = t + tick(P["r_rel"])
    far = W + 60
    over.append(Anim(frames_of(big, "r_light"), rel, me.pos(rel)[0], gy - 5, until=rel + tick((far - x0) / LIGHT),
                     x1=far, y1=gy - 5))
    over.append(Anim(frames_of(big, "r_core"), rel, me.pos(rel)[0], gy - 5, until=rel + tick((far - x0) / LIGHT),
                     x1=far, y1=gy - 5))
    hit(d, "r_hit", rel + tick((d.x - x0) / LIGHT))
    shielded = rel + tick(max(1, (g.x - x0) / LIGHT))
    over.append(OnFoe(frames_of(small, "r_sh"), shielded, g))
    over.append(OnFoe(frames_of(small, "r_shield"), shielded + 330, g, until=shielded + 1800))
    a("ult", tick(P["r_dur"]))
    a("idle", 1500, loop=True)
    end = t

    def place(img, f, px, py):
        img.alpha_composite(f, (px - f.width // 2, py - f.height // 2))

    frames, tt = [], 0.0
    while tt < end:
        img = Image.new("RGBA", (W, H), ARENA)
        for an in under:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        units = [(u.pos(tt)[1], u.frame(tt), u.pos(tt)) for u in (g, d)]
        for an in body:
            f = an.frame(tt)
            if f is not None:
                units.append((an.pos(tt)[1] + 0.5, f, an.pos(tt)))
                break
        for _, f, p in sorted(units, key=lambda u: u[0]):
            if f is not None:
                place(img, f, *p)
        for an in over:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        frames.append(img.resize((W * z, H * z), Image.NEAREST).convert("RGB"))
        tt += step
    sample = frames[::6]
    strip = Image.new("RGB", (W * z, H * z * len(sample)))
    for i, f in enumerate(sample):
        strip.paste(f, (0, i * H * z))
    pal = strip.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q_ = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q_[0].save(T.long_path(out), save_all=True, append_images=q_[1:], duration=step, loop=0)
    return len(frames), round(end / 1000.0, 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    ap.add_argument("--only", choices=["frames", "effects", "showcase"])
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    if args.only in (None, "frames"):
        s = load(CHAMP)
        print("frames", contact([(s, t["name"], t["name"]) for t in s.tags],
                                os.path.join(args.out, "league_senna_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_senna_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_senna_showcase.gif")))


if __name__ == "__main__":
    main()
