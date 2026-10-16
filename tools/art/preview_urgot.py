#!/usr/bin/env python3
"""Preview images for Urgot, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_urgot.py [--out docs/preview] [--only frames|effects|showcase]

  league_urgot_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_urgot_effects.png   every effect animation, 3x
  league_urgot_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_urgot.py, 60 ticks a
                             second): a shot with a leg's blast (the fan along its line), a shot with the legs cooling;
                             Corrosive Charge - the canister lobbed, the ring where it lands, the fuse and the acid
                             blast, the slow; Purge opens - the heat ring under him, the machine gun's shots, a leg;
                             Disdain - the shield, the charge, the catch and the champion hurled behind him; Fear Beyond
                             Death - the drill, the leash, the reel and the execution, the fear wave; 3x
Projectiles fly as the kit flies them: lifted 5000 - y_offset over his pivot, at the target's pivot, turned to their
way (champion-data section 6). The muzzle flashes are in his own shot frames (tools/art/rig_urgot.py).
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
from build_urgot import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_urgot")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_urgot_fx", "league_urgot_big")}


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_urgot_fx"], fx["league_urgot_big"]
    W, H = 300, 120
    gy = 88
    x0 = 100
    d = Foe(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 54, gy)     # in his reach
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0
    lift = (5000 - P["shot_y"]) / 1000.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        an = Anim(dense(sp, tag, "urgot", z), t, 0, 0, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def wait(ms):
        a("idle", ms, loop=True)

    def on(unit, tag, when, sheet=None, under_=False, until=None):
        o = OnFoe(frames_of(sheet or small, tag), when, unit, until=until)
        (under if under_ else over).append(o)

    def at_spot(tag, when, x, y, sheet=None, under_=False):
        an = Anim(frames_of(sheet or small, tag), when, int(x), int(y))
        (under if under_ else over).append(an)

    def shot(tag, rel, speed, hit_tag):
        mx, my = me.pos(rel)
        dx, dy = d.pos(rel)
        arrive = rel + tick(max(1.0, abs(dx - mx) / (speed / 1000.0)))
        over.append(Turned(frames_of(small, tag), rel, int(mx), int(my - lift), loop=True, until=arrive, x1=dx, y1=dy))
        on(d, hit_tag, arrive)
        d.flinches.append(arrive)
        return arrive

    def leg(rel):
        mx, my = me.pos(rel)
        mid = mx + P["p_len"] / 2000.0
        over.append(Anim(frames_of(big, "p_fan"), rel, int(round(mid)), my))
        on(d, "p_hit", rel)

    wait(400)
    # a shot with a leg's blast, then one with the legs cooling
    for k in range(2):
        rel = t + tick(P["a_st"])
        shot("a_shot", rel, P["shot_speed"], "a_hit")
        if k == 0:
            leg(rel)
        a("attack", tick(P["atk_dur"]))
        wait(tick(P["atk_cd"] - P["atk_dur"]))
    # Corrosive Charge: the canister lobbed onto Darius's spot, the ring there while it flies, the fuse and the blast
    rel = t + tick(P["q_st"])
    mx, my = me.pos(rel)
    dx, dy = d.pos(rel)
    land = rel + tick(P["q_travel"])
    over.append(Turned(frames_of(small, "q_charge"), rel, int(mx), int(my - lift), loop=True, until=land, x1=dx, y1=dy))
    at_spot("q_mark", rel, dx, dy, under_=True)
    at_spot("q_blast", land, dx, dy, big)
    boom = land + tick(P["q_apply"])
    on(d, "q_hit", boom)
    d.flinches.append(boom)
    on(d, "q_slow", boom, under_=True, until=boom + tick(P["q_slow_t"]))
    a("skill", tick(P["q_dur"]))
    # Purge opens: the heat ring under him while the machine gun fires (attack speed w_as% more)
    w0 = boom
    under.append(OnMe(frames_of(small, "w_on"), w0, me, until=w0 + tick(P["w_t"])))
    wait(max(0.0, boom - t))
    gap = tick(P["atk_cd"] * 100 / (100 + P["w_as"]))
    for k in range(6):
        rel = t + tick(1)
        shot("w_shot", rel, P["shot_speed"], "w_hit")
        if k == 3:
            leg(rel)
        a("attack_w", min(gap, tick(10)))
        if gap > tick(10):
            wait(gap - tick(10))
    wait(300)
    # Disdain: the shield, the charge onto Darius, the stun and the fling over him
    e0 = t
    over.append(OnMe(frames_of(small, "e_shield"), e0, me))
    mx, _ = me.pos(t)
    dx, _ = d.pos(t)
    goal = dx - 36
    catch = t + tick(max(2.0, (goal - mx) / (P["e_speed"] / 1000.0)))
    me.moves.append((t, catch, mx, goal))
    on(d, "e_hit", catch)
    d.flinches.append(catch)
    fling = catch + tick(P["e_fling"])
    d.slides.append((fling, fling + tick(P["e_pull_t"]), -52))
    d.hops.append((fling, fling + tick(P["e_pull_t"]), 14))
    landed = fling + tick(P["e_pull_t"])
    on(d, "e_fling", landed)
    a("skill2", tick(P["e_dur"]))
    wait(max(0.0, landed - t) + 500)
    # Darius stands behind him now: Urgot steps away and turns to fire the drill (he faces right, so Darius is put in
    # front again by a short walk of Darius)
    d.slides.append((t, t + 400, 96))
    wait(450)
    rel = t + tick(P["r_st"] + P["r_aim"])
    mx, my = me.pos(rel)
    dx, dy = d.pos(rel)
    hit = rel + tick(max(1.0, abs(dx - mx) / (P["r_speed"] / 1000.0)))
    over.append(Turned(frames_of(small, "r_drill"), rel, int(mx), int(my - lift), loop=True, until=hit, x1=dx, y1=dy))
    on(d, "r_hit", hit)
    d.flinches.append(hit)
    leash_end = hit + tick(P["r_t"])
    on(d, "r_leash", hit, until=leash_end)
    a("ult", tick(P["r_dur"]))
    wait(max(0.0, leash_end - t))
    # the reel (Darius dragged to him) and the execution, the fear round him
    d.slides.append((leash_end, leash_end + tick(P["r_reel"]), -(d.pos(leash_end)[0] - me.pos(leash_end)[0] - 40)))
    on(d, "r_reel", leash_end)
    ex = leash_end + tick(P["r_reel"])
    on(d, "r_ex", ex, big)
    d.death = ex + tick(2)
    under.append(OnMe(frames_of(big, "r_fear"), ex + tick(4), me))
    wait(max(0.0, ex - t) + 1400)
    end = t

    def place(img, f, px, py):
        put(img, f, px, py, z)

    frames, tt = [], 0.0
    while tt < end:
        img = Image.new("RGBA", (W * z, H * z), ARENA)
        for an in under:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        units = [(d.pos(tt)[1], d.frame(tt), d.pos(tt))]
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_urgot_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_urgot_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_urgot_showcase.gif")))


if __name__ == "__main__":
    main()
