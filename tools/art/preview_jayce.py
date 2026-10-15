#!/usr/bin/env python3
"""Preview images for Jayce, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_jayce.py [--out docs/preview] [--only frames|effects|showcase]

  league_jayce_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_jayce_effects.png   every effect animation, 3x
  league_jayce_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_jayce.py, 60 ticks a
                             second): two hammer swings; To the Skies - the leap, the slam, the hit and the slow; Thundering
                             Blow - the blow and the knock-back; Lightning Field under him with its zaps; the turn into
                             the cannon (the flash, the haste); the first bolt and its shred; Shock Blast - the orb, the
                             blast; Hyper Charge and three quick bolts; 「加速电炮」 - the gate, the accelerated orb, the
                             big blast; the turn back into the hammer (the guard); 3x
Projectiles fly as the kit flies them: lifted 5000 - y_offset over his pivot, at the target's pivot, turned to their
way (champion-data section 6).
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
from preview_dense import dense, dense_rows, put  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_kindred import Turned, fx_contact  # noqa: E402
from preview_pyke import Me, OnFoe, OnMe  # noqa: E402
from build_jayce import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_jayce")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_jayce_fx", "league_jayce_big")}


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_jayce_fx"], fx["league_jayce_big"]
    W, H = 220, 112
    gy = 80
    x0 = 40
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 28, gy)        # in his hammer's reach
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0
    form = {"idle": "idle"}

    def a(tag, dur=None, loop=False):
        nonlocal t
        x, y = me.pos(t)
        an = Anim(dense(sp, tag, "jayce", z), t, x, y, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def wait(ms):
        a(form["idle"], ms, loop=True)

    def fly(tag, at, unit, y_offset, speed, sheet=None):
        """A projectile from over his pivot to the unit's pivot; its arrival."""
        lift = (5000 - y_offset) / 1000.0
        mx, my = me.pos(at)
        ux, uy = unit.pos(at)
        x1, y1 = mx, my - lift
        arrive = at + tick(max(1.0, ((ux - x1) ** 2 + (uy - y1) ** 2) ** 0.5 / (speed / 1000.0)))
        over.append(Turned(frames_of(sheet or small, tag), at, int(round(x1)), int(round(y1)), loop=True,
                           until=arrive, x1=ux, y1=uy))
        return arrive

    def on(unit, tag, when, sheet=None, under_=False, until=None):
        o = OnFoe(frames_of(sheet or small, tag), when, unit, until=until)
        (under if under_ else over).append(o)

    def at_spot(tag, when, x, y, sheet, under_=False, until=None):
        an = Anim(frames_of(sheet, tag), when, int(x), int(y), loop=until is not None, until=until)
        (under if under_ else over).append(an)

    def swing(then=True):
        hit = t + tick(P["a_st"])
        on(d, "a_hit", hit)
        d.flinches.append(hit)
        a("attack", tick(P["atk_dur"]))
        if then:
            wait(tick(P["atk_cd"] - P["atk_dur"]))

    def bolt(cd=None, shred=False):
        land = fly("c_bolt", t + tick(P["c_st"]), d, P["c_y"], P["c_speed"])
        on(d, "c_hit", land)
        if shred:
            on(d, "shred", land, until=land + tick(P["p_sh_t"]))
        d.flinches.append(land)
        a("c_attack", tick(P["c_atk_dur"]))
        wait(tick((cd or P["atk_cd"]) - P["c_atk_dur"]))

    wait(500)
    for _ in range(2):
        swing()
    # To the Skies: the leap starts on q_go, lands on Darius (the slam frame), the hit, the slow
    go = t + tick(P["q_go"])
    sx = me.pos(t)[0]
    tx = d.pos(t)[0] - 14
    land = go + tick(max(1.0, abs(tx - sx) / (P["q_speed"] / 1000.0)))
    me.moves.append((go, land, sx, tx))
    a("skill", tick(P["q_anim"]))
    at_spot("q_land", land, d.pos(land)[0], gy, big, under_=True)
    on(d, "q_hit", land)
    on(d, "q_slow", land, under_=True, until=land + tick(P["q_slow_t"]))
    d.flinches.append(land)
    wait(200)
    # Thundering Blow: the blow on e_at, the knock-back
    hit = t + tick(P["e_at"])
    on(d, "e_blow", hit)
    d.flinches.append(hit)
    kb = P["e_kb_speed"] * P["e_kb_t"] / 1000.0
    d.slides.append((hit, hit + tick(P["e_kb_t"]), kb))
    a("skill2", tick(P["e_anim"]))
    wait(200)
    # Lightning Field round him, its zaps on Darius (now farther off)
    start = t + tick(P["w_at"])
    under.append(OnMe(frames_of(big, "w_field"), start, me, until=start + tick(P["w_n"] * P["w_per"])))
    a("w_cast", tick(P["w_anim"]))
    for k in range(P["w_n"]):
        on(d, "w_zap", start + tick(P["w_per"] * k))
    # the turn into the cannon: the flash, the haste
    tf = t
    over.append(OnMe(frames_of(small, "tf_spark"), tf, me))
    under.append(OnMe(frames_of(small, "haste"), tf, me, until=tf + tick(P["p_mt"])))
    a("tf_c", tick(P["tf_dur"]))
    form["idle"] = "c_idle"
    wait(200)
    bolt(shred=True)
    # Shock Blast
    hit = fly("cq_orb", t + tick(P["cq_at"]), d, P["cq_y"], P["cq_speed"])
    at_spot("cq_boom", hit, d.pos(hit)[0], d.pos(hit)[1] - 4, big)
    on(d, "cq_hit", hit)
    d.flinches.append(hit)
    a("c_skill", tick(P["cq_anim"]))
    wait(200)
    # Hyper Charge and three quick bolts
    hc = t
    a("c_skill2", tick(P["cw_anim"]))
    over.append(OnMe(frames_of(small, "hyper"), hc, me, until=hc + tick(P["hc_t"])))
    quick = int(P["atk_cd"] * 100 / (100 + P["hc_as"]))
    for _ in range(3):
        bolt(cd=max(quick, P["c_atk_dur"]))
    # the ult: the gate, the accelerated orb, the big blast
    g0 = t
    mx, my = me.pos(g0)
    at_spot("gate", g0, mx, my, big, under_=True)
    under.append(OnMe(frames_of(small, "haste"), g0, me, until=g0 + tick(P["g_t"])))
    hit = fly("gq_orb", t + tick(P["r_at"]), d, P["r_y"], P["r_speed"], sheet=big)
    at_spot("gq_boom", hit, d.pos(hit)[0], d.pos(hit)[1] - 4, big)
    on(d, "gq_hit", hit)
    d.flinches.append(hit)
    a("ult", tick(P["r_anim"]))
    wait(400)
    # back into the hammer: the flash, the guard
    tf = t
    over.append(OnMe(frames_of(small, "tf_spark"), tf, me))
    over.append(OnMe(frames_of(small, "guard"), tf, me, until=tf + tick(P["p_arm_t"])))
    a("tf_h", tick(P["tf_dur"]))
    form["idle"] = "idle"
    wait(800)
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_jayce_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_jayce_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_jayce_showcase.gif")))


if __name__ == "__main__":
    main()
