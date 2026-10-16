#!/usr/bin/env python3
"""Preview images for Kalista, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_kalista.py [--out docs/preview] [--only frames|effects|showcase]

  league_kalista_frames.png    every animation's dense frames (hd_, PPU 1.4, as league.dll shows them)
  league_kalista_effects.png   every effect animation, 3x
  league_kalista_showcase.gif  a scripted fight against Darius with Soraka as her Oathsworn, timed like the kit
                               (tools/kit/build_kalista.py, 60 ticks a second): a spear (the hit, the spear stuck in
                               him, Sentinel's soul mark with Soraka beside him); Darius steps in, the next spear and
                               her hop back; Pierce and the add-on's hop forward; Rend - the pull-in ring, the spears
                               ripped out, the slow ring; Fate's Call - Soraka bound and drawn into her, the shroud,
                               the hurl, the landing's shockwave and Darius knocked up; Rend after the landing kills him
                               and its reset flares over her head; 3x
Projectiles fly as the kit flies them: lifted 5000 - y_offset over her pivot, at the target's pivot, turned to their
way (champion-data section 6).
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
from preview_kindred import Turned, fx_contact  # noqa: E402
from preview_leesin import Foe  # noqa: E402
from preview_pyke import Me, OnFoe, OnMe  # noqa: E402
from build_kalista import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_kalista")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_kalista_fx", "league_kalista_big")}


class Ally(Foe):
    """Soraka: facing right, unseen while she is held inside Kalista."""

    def __init__(self, sprite, x, y):
        super().__init__(sprite, x, y, mirror=False)
        self.hidden = []

    def frame(self, t):
        for t0, t1 in self.hidden:
            if t0 <= t < t1:
                return None
        return super().frame(t)


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_kalista_fx"], fx["league_kalista_big"]
    W, H = 250, 104
    gy = 70
    x0 = 70
    d = Foe(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 52, gy)     # at her attack range
    s = Ally(load(os.path.join(LEAGUE, "champions", "league_soraka")), x0 + 14, gy - 14)
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        an = Anim(dense(sp, tag, "kalista", z), t, 0, 0, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def wait(ms):
        a("idle", ms, loop=True)

    def fly(tag, at, unit, y_offset, speed):
        """A projectile from over her pivot to the unit's pivot; its arrival."""
        lift = (5000 - y_offset) / 1000.0
        mx, my = me.pos(at)
        ux, uy = unit.pos(at)
        x1, y1 = mx, my - lift
        arrive = at + tick(max(1.0, ((ux - x1) ** 2 + (uy - y1) ** 2) ** 0.5 / (speed / 1000.0)))
        over.append(Turned(frames_of(small, tag), at, int(round(x1)), int(round(y1)), loop=True,
                           until=arrive, x1=ux, y1=uy))
        return arrive

    def on(unit, tag, when, sheet=None, under_=False, until=None):
        o = OnFoe(frames_of(sheet or small, tag), when, unit, until=until)
        (under if under_ else over).append(o)

    def at_spot(tag, when, x, y, sheet=None, under_=False):
        an = Anim(frames_of(sheet or small, tag), when, int(x), int(y))
        (under if under_ else over).append(an)

    marks = []

    def stick(when):
        """A spear stuck in Darius: sp_mark replayed every sp_pic ticks until Rend rips it."""
        marks.append(when)

    def throw(tag="attack", dur=P["atk_dur"], st=P["a_st"], proj="a_spear", hit_fx="a_hit", y=P["spear_y"],
              speed=P["spear_speed"], hop=None, soul=False):
        nonlocal t
        rel = t + tick(st)
        hit = fly(proj, rel, d, y, speed)
        on(d, hit_fx, hit)
        if soul:
            on(d, "w_hit", hit + tick(1))
        d.flinches.append(hit)
        stick(hit)
        if hop is None:
            a(tag, tick(dur))
            return
        # the hop leaves on the release: the throw's first frames, then hop_b / hop_f while she moves hop_v x hop_t
        a(tag, tick(st))
        mx = me.pos(t)[0]
        step_ = P["hop_v"] * P["hop_t"] / 1000.0
        me.moves.append((t, t + tick(P["hop_t"]), mx, mx - step_ if hop == "b" else mx + step_))
        a("hop_" + hop, tick(P["hop_t"] + 2))

    def rend(kill=False):
        nonlocal t
        pop = t + tick(P["e_rel"])
        mx, my = me.pos(pop)
        at_spot("e_cast", pop, mx, my, big, under_=True)
        on(d, "e_rip", pop)
        d.flinches.append(pop)
        rips.append(pop)
        if kill:
            d.death = pop + tick(2)
            over.append(OnMe(frames_of(small, "e_reset"), pop + tick(4), me))
        else:
            on(d, "e_slow", pop, under_=True, until=pop + tick(P["e_slow_t"]))
        a("skill2", tick(P["e_anim"]))

    rips = []
    wait(400)
    # a spear; Soraka beside Darius: Sentinel's soul mark
    throw(soul=True)
    wait(tick(P["atk_cd"] - P["atk_dur"]))
    # Darius steps in (inside hop_thr): the next spear and her hop back
    d.slides.append((t - 300, t, -16))
    throw(hop="b")
    wait(tick(P["atk_cd"] - P["a_st"] - P["hop_t"] - 2))
    # Pierce, and the add-on's hop forward (he is out at the edge of her reach)
    throw("skill", P["q_dur"], P["q_rel"], "q_spear", "q_hit", P["q_y"], P["q_speed"], hop="f")
    wait(200)
    # Rend: three spears in him
    rend()
    wait(400)
    # Fate's Call: Soraka bound and drawn into her, the shroud, the hurl
    r0 = t
    sx, sy = s.pos(r0)
    mx, my = me.pos(r0)
    grab = tick(max(1.0, abs(mx - sx) / (P["r_grab_v"] / 1000.0)))
    on(s, "r_take", r0, big)
    s.slides.append((r0, r0 + grab, mx - sx))
    held = r0 + tick(P["r_hold"])
    s.hidden.append((r0 + grab, held))
    over.append(OnMe(frames_of(big, "r_safe"), r0 + grab, me, until=held))
    a("ult", tick(P["r_anim"]))
    wait(max(0.0, held - t))
    # the hurl: Soraka flies to Darius at r_v a tick and lands in front of him
    dx, dy = d.pos(held)
    lx = dx - 10
    land = held + tick(max(1.0, abs(lx - mx) / (P["r_v"] / 1000.0)))
    s.slides.append((held, land, lx - mx))
    on(s, "r_fly", held, big, until=land)
    a("ult2", tick(P["r_throw"]))
    at_spot("r_land", land, dx, dy, big, under_=True)
    on(d, "r_up", land)
    d.hops.append((land, land + tick(P["r_up"]), 10))
    wait(max(0.0, land + tick(P["r_up"] // 2) - t))
    # Rend after the landing: it kills him, and the kill refunds it
    rend(kill=True)
    wait(1200)
    end = t

    # the spears stuck in him: sp_mark every sp_pic ticks from each spear's hit to the next Rend
    for h in marks:
        stop = min([r for r in rips if r > h] or [end])
        k = h
        while k < stop:
            on(d, "sp_mark", k)
            k += tick(P["sp_pic"])

    def place(img, f, px, py):
        put(img, f, px, py, z)

    frames, tt = [], 0.0
    while tt < end:
        img = Image.new("RGBA", (W * z, H * z), ARENA)
        for an in under:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        units = [(d.pos(tt)[1], d.frame(tt), d.pos(tt)), (s.pos(tt)[1], s.frame(tt), s.pos(tt))]
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


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    ap.add_argument("--only", choices=["frames", "effects", "showcase"])
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    if args.only in (None, "frames"):
        s = load(CHAMP)
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_kalista_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[15:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_kalista_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_kalista_showcase.gif")))


if __name__ == "__main__":
    main()
