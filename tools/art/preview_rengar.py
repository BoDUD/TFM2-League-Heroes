#!/usr/bin/env python3
"""Preview images for Rengar, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_rengar.py [--out docs/preview] [--only frames|effects|showcase]

  league_rengar_frames.png    every animation, frame by frame, 3x on the arena colour
  league_rengar_effects.png   every effect animation, 3x
  league_rengar_showcase.gif  a scripted hunt on Darius with Garen behind him, timed like the kit
                              (tools/kit/build_rengar.py, 60 ticks a second): the passive's eye, the pounce from afar
                              with Savagery ready (air Q: the rake, the rising slash, the attack-speed ring); a blade
                              swing; W - the roar on both, the heal; E - the bola, the slow; Savagery - the slam and
                              the rip that fills Ferocity, the triple Q at once (the empowered aura); he backs off, R -
                              the smoke, the hunter's eye on Darius, the crit pounce and the leap -> E root; the pips
                              over his head count Ferocity all along; 3x
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
from build_rengar import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_rengar")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_rengar_fx", "league_rengar_big")}
REACH = 32                                      # where his swings land from (px from Darius: he is 41 px wide)
BOLA_Y = P["e_y"] // 1000 + 5                   # the bola flies this far over the pivot
BOLA = P["e_speed"] / 1000                      # px a tick
SURE = P["e_combo_speed"] / 1000


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_rengar_fx"], fx["league_rengar_big"]
    W, H = 220, 104
    gy = 82
    x0 = 34
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 84, gy)
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 116, gy)
    me = Me(x0, gy)
    body, under, over = [], [], []
    pips = []                                    # (t0, t1, count)
    t = 0.0
    fero = [0, 0.0]                               # count, since

    def a(tag, dur=None, loop=False):
        nonlocal t
        x, y = me.pos(t)
        an = Anim(frames_of(sp, tag), t, x, y, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def hit(foe, tag, when, sheet=None):
        over.append(OnFoe(frames_of(sheet or small, tag), when, foe))
        foe.flinches.append(when)

    def gain(when):
        if fero[0]:
            pips.append((fero[1], when, fero[0]))
        fero[0], fero[1] = min(4, fero[0] + 1), when

    def spend(when):
        if fero[0]:
            pips.append((fero[1], when, fero[0]))
        fero[0], fero[1] = 0, when

    def pounce(crit):
        """The pounce: the dust, the dash from tick leap_go to leap_at, the rake (and R's crit) on Darius."""
        t0 = t
        sx = me.pos(t0)[0]
        under.append(Anim(frames_of(small, "l_dust"), t0, sx, gy))
        go, land = t0 + tick(P["leap_go"]), t0 + tick(P["leap_at"])
        me.moves.append((go, land, sx, d.pos(land)[0] - REACH))
        hit(d, "l_hit", land)
        if crit:
            hit(d, "r_hit", land, big)
        under.append(Anim(frames_of(small, "l_dust"), land, d.pos(land)[0] - REACH, gy))
        gain(land)
        a("leap", tick(P["leap_dur"]))
        return land

    # the passive's eye until the pounce; the pounce with Savagery ready: air Q
    eye = OnMe(frames_of(small, "p_ready"), 0, me, until=1)
    over.append(eye)
    a("idle", 600, loop=True)
    eye.until = t
    land = pounce(False)
    hit(d, "q_rip", land + 40)
    under.append(OnMe(frames_of(small, "q_buff"), land, me, until=land + tick(P["q_as_t"])))
    a("idle", 200, loop=True)
    hit(d, "a_hit", t + tick(P["a_st"]))
    a("attack", tick(P["atk_dur"]))
    # W: the roar on both, the heal
    w = t + tick(P["w_at"])
    under.append(OnMe(frames_of(big, "w_roar"), w, me))
    for foe in (d, g):
        hit(foe, "a_hit", w)
    over.append(OnMe(frames_of(small, "w_heal"), w, me))
    gain(w)
    a("skill_w", tick(P["w_dur"]))
    a("idle", 200, loop=True)
    # E: the bola (a line at Darius), the slow
    e = t + tick(P["e_at"])
    sx = me.pos(e)[0] + 8
    arrive = e + tick(max(1, (d.pos(e)[0] - sx) / BOLA))
    over.append(Anim(frames_of(small, "e_bola"), e, sx, gy - BOLA_Y, until=arrive, x1=d.pos(e)[0], y1=gy - BOLA_Y))
    d.flinches.append(arrive)
    over.append(OnFoe(frames_of(small, "e_slow"), arrive, d, until=arrive + tick(P["e_slow_t"])))
    gain(e)
    a("skill2", tick(P["e_dur"]))
    a("idle", 200, loop=True)
    # Savagery: the slam and the rip; the fourth point -> the triple Q at once
    for emp in (False, True):
        q0 = t
        under.append(Anim(frames_of(small, "q_slam"), q0 + tick(P["q_slam_at"]), d.pos(q0)[0], gy))
        hit(d, "q_rip", q0 + tick(P["q_rip_at"]))
        if emp:
            spend(q0 + tick(P["q_rip_at"]))
            over.append(OnMe(frames_of(big, "q_emp"), q0 + tick(P["q_rip_at"]), me, until=q0 + tick(P["q_rip_at"]) + 1500))
        else:
            gain(q0 + tick(P["q_rip_at"]))
        a("skill", tick(P["q_dur"]))
    a("idle", 300, loop=True)
    # he backs off; R: the smoke, the hunter's eye on Darius, the crit pounce, the leap -> E root
    b0 = t
    me.moves.append((b0, b0 + 500, me.pos(b0)[0], me.pos(b0)[0] - 40))
    a("run", 500, loop=True)
    r = t + tick(P["r_at"])
    over.append(OnMe(frames_of(big, "r_smoke"), r, me))
    over.append(OnFoe(frames_of(small, "r_mark"), r, d, until=r + 1400))
    a("ult", tick(P["r_dur"]))
    a("idle", 400, loop=True)
    land = pounce(True)
    a("idle", 100, loop=True)
    e = t + tick(P["e_at"])
    sx = me.pos(e)[0] + 8
    arrive = e + tick(max(1, (d.pos(e)[0] - sx) / SURE))
    over.append(Anim(frames_of(small, "e_bola"), e, sx, gy - BOLA_Y, until=arrive, x1=d.pos(e)[0], y1=gy - BOLA_Y))
    d.holds.append((arrive, arrive + tick(P["e_combo_t"])))
    over.append(OnFoe(frames_of(small, "e_root"), arrive, d, until=arrive + tick(P["e_combo_t"])))
    gain(e)
    a("skill2", tick(P["e_dur"]))
    hit(d, "a_hit", t + tick(P["a_st"]))
    a("attack", tick(P["atk_dur"]))
    a("idle", 900, loop=True)
    end = t
    spend(end)
    for t0, t1, k in pips:
        over.append(OnMe(frames_of(small, f"f{k}"), t0, me, until=t1))

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
                                os.path.join(args.out, "league_rengar_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_rengar_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_rengar_showcase.gif")))


if __name__ == "__main__":
    main()
