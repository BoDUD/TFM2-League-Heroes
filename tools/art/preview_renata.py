#!/usr/bin/env python3
"""Preview images for Renata, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_renata.py [--out docs/preview] [--only frames|effects|showcase] [--fx DIR]

  league_renata_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_renata_effects.png   every effect animation, 3x
  league_renata_showcase.gif  a scripted fight, timed like the kit (tools/kit/build_renata.py, 60 ticks a second), as
                              the main pack shows it: Renata and Jinx against Darius and Garen - her pistol shots mark
                              Darius and Jinx's shot pops the mark (Leverage); Loyalty Program's missiles shield Jinx on
                              their way and burst on Darius (the slow puddle); Handshake grips him, flings him past
                              her and he crashes down; Bailout on Jinx; Hostile Takeover - the machine's gas, the wave,
                              Darius and Garen berserk, lashing out at each other; 3x
Projectiles fly as the kit flies them: lifted 5000 - y_offset over her pivot, turned to their way (champion-data
section 6).
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
from build_renata import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_renata")
SHEETS = ("league_renata_fx", "league_renata_big")


def showcase(out, fxdir, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(os.path.join(fxdir, k)) for k in SHEETS}
    small, big = fx["league_renata_fx"], fx["league_renata_big"]
    W, H = 200, 120
    gy = 80
    x0 = 46
    me = Me(x0, gy)
    jinx = Foe(load(os.path.join(LEAGUE, "champions", "league_jinx")), x0 + 24, gy + 14, mirror=False)  # ahead, lower
    d = Foe(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 58, gy)        # in her reach
    g = Foe(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 78, gy + 10)    # his ally, beside him
    body, under, over = [], [], []
    t = 0.0
    lift = lambda y: (5000 - y) / 1000.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        an = Anim(dense(sp, tag, "renata", z), t, 0, 0, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def wait(ms):
        if ms > 0:
            a("idle", ms, loop=True)

    def on(unit, tag, when, sheet=None, under_=False, until=None):
        o = OnFoe(frames_of(sheet or small, tag), when, unit, until=until)
        (under if under_ else over).append(o)

    def on_me(tag, when, sheet=None, under_=False, until=None):
        o = OnMe(frames_of(sheet or small, tag), when, me, until=until)
        (under if under_ else over).append(o)

    def at_spot(tag, when, x, y, sheet=None, under_=False):
        an = Anim(frames_of(sheet or small, tag), when, int(x), int(y))
        (under if under_ else over).append(an)

    def fly(tag, rel, y_off, speed, target=None, length=None, sheet=None):
        """A projectile from her pivot (lifted) to the target's pivot or `length` px on; its arrival."""
        mx, my = me.pos(rel)
        if target is not None:
            tx, ty = target.pos(rel)
            x1, y1 = tx, ty
        else:
            x1, y1 = mx + length, my - lift(y_off)
        arrive = rel + tick(max(1.0, abs(x1 - mx) / (speed / 1000.0)))
        over.append(Turned(frames_of(sheet or small, tag), rel, int(mx), int(my - lift(y_off)), loop=False,
                           until=arrive, x1=x1, y1=y1))
        return arrive

    def attack(mark=False):
        rel = t + tick(P["a_st"])
        arrive = fly("a_shot", rel, P["shot_y"], P["shot_speed"], d)
        on(d, "a_hit", arrive)
        d.flinches.append(arrive)
        a("attack", tick(P["atk_dur"]))
        wait(tick(P["atk_cd"] - P["atk_dur"]))
        return arrive

    wait(400)
    # Leverage: her shot marks Darius; Jinx's shot pops the mark (two of her champions near it)
    marked = attack()
    attack()
    pop = t + 220
    jinx.attacks.append(t)
    on(d, "p_mark", marked, until=pop)
    on(d, "p_pop", pop)
    d.flinches.append(pop)
    wait(500)
    # Loyalty Program: the missiles from the mechanical hand; the twin line shields Jinx on its way, the pair bursts on
    # Darius (the slow puddle under him)
    rel = t + tick(P["e_rel"])
    mx, _ = me.pos(rel)
    on(jinx, "e_shield", rel + tick(max(1.0, (jinx.x - mx) / (P["e_speed"] / 1000.0))))
    hit = fly("e_missile", rel, P["e_y"], P["e_speed"], d)
    at_spot("e_boom", hit, *d.pos(hit))
    on(d, "e_hit", hit)
    on(d, "e_slow", hit, under_=True, until=hit + tick(P["e_slow_t"]))
    d.flinches.append(hit)
    a("skill", tick(P["e_dur"]))
    wait(600)
    # Handshake: the hand grips Darius for the root, then flings him q_pull x q_pull_t toward and past her; he crashes
    rel = t + tick(P["q_rel"])
    hit = fly("q_hand", rel, P["q_y"], P["q_speed"], d)
    on(d, "q_hit", hit)
    d.flinches.append(hit)
    a("skill2", tick(P["q_dur"]))
    wait(max(0.0, hit + tick(P["q_root"]) - t))
    fling = t
    pull = P["q_pull"] * P["q_pull_t"] / 1000.0
    land = fling + tick(P["q_pull_t"])
    d.slides.append((fling, land, -pull))
    on(d, "q_fling", fling)
    a("skill2_fling", tick(P["q_fling_anim"]))
    at_spot("q_land", land, *d.pos(land + 1), under_=True)
    on(d, "q_crash_hit", land)
    d.flinches.append(land)
    back = land + tick(P["q_stun"])                         # stunned, then back to his place
    d.runs.append((back, back + 700))
    d.slides.append((back, back + 700, pull))
    wait(max(0.0, back + 700 - t) + 200)
    # Bailout on Jinx (an ally in a fight): the shot of stimulant, her aura, the heal at its end
    w0 = t + tick(6)
    on(jinx, "w_cast", w0)
    w_end = w0 + tick(P["w_t"])
    on(jinx, "w_buff", w0, under_=True, until=w_end)
    on(jinx, "w_save", w_end)
    a("skill_w", tick(P["w_anim"]))
    wait(500)
    # Hostile Takeover: the 3-tick gate, the machine and its gas round her, the wave on r_rel; Darius and Garen go
    # berserk and lash out every r_per ticks at the other one
    a("idle", tick(3))
    fire = t
    on_me("r_cast", fire, big, under_=True)
    rel = fire + tick(P["r_rel"])
    a("ult", tick(P["r_anim"]))
    mx, my = me.pos(rel)
    end = rel + tick(P["r_len"] / P["r_speed"])
    over.append(Turned(frames_of(big, "r_wave"), rel, int(mx), int(my - lift(0)), loop=False, until=end,
                       x1=int(mx + P["r_len"] / 1000), y1=int(my - lift(0))))
    for u, other in ((d, g), (g, d)):
        at = rel + tick((u.pos(rel)[0] - mx) / (P["r_speed"] / 1000.0))
        on(u, "r_hit", at)
        on(u, "r_berserk", at, until=at + tick(P["r_t"]))
        u.flinches.append(at)
        for k in range(1, P["r_t"] // P["r_per"] + 1):
            lash = at + tick(P["r_per"] * k)
            u.attacks.append(lash - 150)
            at_spot("r_lash", lash, *u.pos(lash), under_=True)
            if abs(u.pos(lash)[0] - other.pos(lash)[0]) * 1000 <= P["r_lash_r"]:
                on(other, "r_lash_hit", lash)
                other.flinches.append(lash)
    wait(max(0.0, w_end - t))
    wait(900)
    end_all = t

    def place(img, f, px, py):
        put(img, f, px, py, z)

    frames, tt = [], 0.0
    while tt < end_all:
        img = Image.new("RGBA", (W * z, H * z), ARENA)
        for an in under:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        units = [(u.pos(tt)[1], u.frame(tt), u.pos(tt)) for u in (d, g, jinx)]
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
    return len(frames), round(end_all / 1000.0, 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    ap.add_argument("--only", choices=["frames", "effects", "showcase"])
    ap.add_argument("--fx", default=os.path.join(LEAGUE, "effects"), help="the effect sheets' folder (a test)")
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    if args.only in (None, "frames"):
        s = load(CHAMP)
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_renata_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name in SHEETS:
            sp = load(os.path.join(args.fx, name))
            rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_renata_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_renata_showcase.gif"), args.fx))


if __name__ == "__main__":
    main()
