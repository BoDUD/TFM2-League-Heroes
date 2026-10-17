#!/usr/bin/env python3
"""Preview images for Evelynn, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_evelynn.py [--out docs/preview] [--only frames|effects|showcase]

  league_evelynn_frames.png    every animation, frame by frame, 3x on the arena colour
  league_evelynn_effects.png   every effect animation, 3x
  league_evelynn_showcase.gif  a scripted fight against Darius with Garen behind him, timed like the kit
                               (work/ev/build_evelynn.py): Evelynn runs in and whips Darius (Whiplash: the whip's hit
                               and the haste under her feet); Allure's curse flies to him and marks him (the dim heart
                               over his head); Hate Spike's lash marks him (the thorn crown), then three spikes fly
                               through both; her attacks add the mark's bonus; the heart ripens (it fills and glows) and
                               the next hit charms him (it bursts; three hearts circle his head while he walks to her,
                               the cracked ring under his feet); Last Caress: the burst, the X slash before her, both hit,
                               her shadow left where she stood as she warps back, Darius falls; 1.25 s later Demon Shade
                               rises round her (the empowered whip's glow); Garen walks up and her empowered whip dashes
                               out of the shade at him (the trail left behind, the burst on him); 3x
"""
import argparse
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from preview_annie import Held, OnFoe  # noqa: E402
from preview_ashe import Anim, tick  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_jinx import Follow  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_evelynn")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_evelynn_fx", "league_evelynn_big")}


class At:
    """A fixed point for the views that stay where they were played."""

    def __init__(self, x, y):
        self.x, self.y = x, y

    def pos(self, t):
        return self.x, self.y


def showcase(out, z=3, step=40):
    ev = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_evelynn_fx"], fx["league_evelynn_big"]
    W, H = 300, 140
    gy = 96
    x = 96
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x + 24, gy + 2)      # 24 px: her reach
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x + 62, gy - 8)       # behind him
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False, to=None):
        nonlocal t, x
        an = Anim(frames_of(ev, tag), t, x, gy, loop=loop, until=(t + dur) if dur else None, x1=to)
        body.append(an)
        t = an.until
        if to is not None:
            x = to
        return an

    def on(unit, sp, tag, when, until=None, ground=False):
        an = OnFoe(frames_of(sp, tag), when, unit, z=-1 if ground else 1)
        if until is not None:
            an.loop, an.until = True, until
        (under if ground else over).append(an)
        return an

    def mine(sp, tag, when, until=None, ground=False):
        """A view on her (a buff's picture), following her body wherever it goes."""
        fr = frames_of(sp, tag)
        an = Follow(fr, when, x, gy, loop=until is not None, until=until, on=body)
        (under if ground else over).append(an)
        return an

    def left(sp, tag, when, px, py=None, ground=False):
        """A view played on her that stays where it was played (is_follow false)."""
        an = Anim(frames_of(sp, tag), when, px, gy if py is None else py, z=-1 if ground else 1)
        (under if ground else over).append(an)
        return an

    def fly(sp, tag, launch, sx, sy, tx, ty, speed):
        span = ((tx - sx) ** 2 + (ty - sy) ** 2) ** 0.5
        arrive = launch + tick(max(1.0, span / speed))
        over.append(Anim(frames_of(sp, tag), launch, sx, sy, until=arrive, x1=tx, y1=ty))
        return arrive

    def strike(tag, foe, hit, at_tick=10, extra=()):
        """An attack: the blow on tick 10 (the start of frame 4), then the rest of the 55-tick interval."""
        rel = t + tick(at_tick)
        on(foe, small, hit, rel)
        for ex in extra:
            on(foe, small, ex, rel)
        foe.flinches.append(rel)
        an = a(tag)
        a("idle", tick(55) - an.total, loop=True)
        return rel

    # she runs in; Darius waits, Garen behind him
    run = Anim(frames_of(ev, "run"), 0.0, x - 50, gy, loop=True, until=1100, x1=x)
    body.append(run)
    t = run.until
    a("idle", 200, loop=True)
    # Whiplash: the attack is the whip (her max-health damage, then 2 s of haste)
    hit = strike("attack_e", d, "e_hit")
    mine(small, "e_haste", hit, until=hit + tick(120), ground=True)
    # Allure: the curse leaves her hand on tick 6, homes on Darius (9 px a tick) and marks him; ripe 150 ticks later
    w0 = t
    left(small, "w_cast", w0 + tick(6), x + 13, gy - 12)
    landed = fly(small, "w_bolt", w0 + tick(6), x + 13, gy - 12, d.x - 2, gy - 10, 9.0)
    on(d, small, "w_hit", landed)
    ripe = landed + tick(150)
    on(d, small, "w_mark", landed, until=ripe)
    a("skill2")
    a("idle", 150, loop=True)
    # Hate Spike: the lash leaves on tick 10 (5 px a tick) and marks Darius (her next three attacks hit harder); three
    # spikes fire by themselves 22, 40 and 58 ticks in, each through both
    q0 = t
    left(small, "q_cast", q0 + tick(10), x + 17, gy - 12)
    lashed = fly(small, "q_lash", q0 + tick(10), x + 17, gy - 12, d.x - 2, gy - 10, 5.0)
    on(d, small, "q_hit", lashed)
    d.flinches.append(lashed)
    on(d, small, "q_mark", lashed, until=lashed + 3000)
    for k in range(3):
        s0 = q0 + tick(22 + 18 * k)
        left(small, "sp_cast", s0, x, gy - 10)
        end = fly(small, "q_spike", s0, x + 4, gy - 8, x + 58, gy - 8, 6.0)
        for foe in (d, g):
            h = s0 + tick(max(1.0, (foe.x - x - 4) / 6.0))
            on(foe, small, "sp_hit", h)
            foe.flinches.append(h)
    a("skill")
    a("idle", tick(58) - tick(18) + 100, loop=True)
    # her attacks, each with the mark's bonus; the heart ripens (150 ticks after it landed) and the first hit after that
    # charms him (75 ticks, walking to her) and cuts his magic resistance (240 ticks)
    on(d, small, "w_ripen", ripe)
    ripened = ripe + sum(ms for _, ms in frames_of(small, "w_ripen"))
    charm = None
    for _ in range(3):
        if t + tick(10) >= ripened:
            on(d, small, "w_ripe", ripened, until=t + tick(10))
            charm = strike("attack", d, "a_hit", extra=("qb_hit", "w_pop"))
            break
        strike("attack", d, "a_hit", extra=("qb_hit",))
    on(d, small, "w_charmed", charm, until=charm + tick(75))
    on(d, small, "w_shred", charm, until=charm + tick(240), ground=True)
    d.walks.append((charm, charm + tick(75), -6))
    # Last Caress: from her next attack - the burst, the slash crawling at Darius, both hit on tick 13, her shadow left
    # behind as she warps 45 px back (5 ticks), the landing a tick later; Darius falls
    r0 = t
    left(big, "r_cast", r0, x, gy)
    left(big, "r_slash", r0, x, gy)
    hit = r0 + tick(13)
    for foe in (d, g):
        on(foe, small, "r_hit", hit)
        foe.flinches.append(hit)
    d.death = hit + tick(4)
    a("ult", tick(13))
    left(big, "r_blink", t, x, gy, ground=True)
    a("ult", tick(5), to=x - 45)
    left(big, "r_land", t + tick(1), x, gy, ground=True)
    a("ult", tick(12))
    a("idle", tick(75) - tick(12), loop=True)
    # Demon Shade 75 ticks after the warp: the shade rises round her, the empowered whip ready (its glow)
    sh = t
    mine(big, "sh_in", sh)
    sh_in = sum(ms for _, ms in frames_of(big, "sh_in"))
    a("idle", 1700, loop=True)
    out_at = t
    mine(big, "sh_loop", sh + sh_in, until=out_at)
    mine(small, "e_emp", sh + sh_in, until=out_at)
    # Garen walks up; the empowered whip dashes out of the shade at him (4.5 px a tick), the trail left behind
    g.walks.append((sh + 300, sh + 1500, -16))
    mine(big, "sh_out", out_at)
    left(big, "e2_trail", out_at, x, gy)
    gx = g.pos(out_at)[0]
    dash_to = gx - 22
    arrive = out_at + tick(max(1.0, (dash_to - x) / 4.5))
    on(g, small, "e2_hit", arrive)
    g.flinches.append(arrive)
    a("attack_e2", arrive - out_at, to=dash_to)
    rest = frames_of(ev, "attack_e2")
    a("attack_e2", max(0.0, sum(ms for _, ms in rest) - (arrive - out_at)))
    mine(small, "e_haste", arrive, until=arrive + tick(120), ground=True)
    a("idle", 1200, loop=True)
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
        units = [(g.pos(tt)[1], g.frame(tt), g.pos(tt)), (d.pos(tt)[1], d.frame(tt), d.pos(tt))]
        for an in body:
            f = an.frame(tt)
            if f is not None:
                units.append((an.pos(tt)[1], f, an.pos(tt)))
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
                                os.path.join(args.out, "league_evelynn_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[15:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_evelynn_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_evelynn_showcase.gif")))


if __name__ == "__main__":
    main()
