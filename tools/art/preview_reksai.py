#!/usr/bin/env python3
"""Preview images for Rek'Sai, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_reksai.py [--out docs/preview] [--only frames|effects|showcase]

  league_reksai_frames.png    every animation's dense frames (hd_, PPU 1.58, as league.dll shows them)
  league_reksai_effects.png   every effect animation, 3x
  league_reksai_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_reksai.py, 60 ticks a
                              second): two bites (the prey mark over him); Queen's Wrath - the whirl at her feet, the
                              pounce and two splashing attacks; full Fury - the flames on her crest, Furious Bite;
                              Darius backs off - Prey Seeker from the ground, its burst flying at him; Burrow - into the
                              ground (her Fury healing her), the mound tunnelling to him, Unburrow knocking him up; Void
                              Rush - into the Void, the lunge out of the ground, the crossed claws; 3x
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
from build_reksai import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_reksai")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_reksai_fx", "league_reksai_big")}


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_reksai_fx"], fx["league_reksai_big"]
    W, H = 300, 110
    gy = 86
    x0 = 90
    reach = 44
    d = Foe(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + reach, gy)     # in her reach
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0
    lift = (5000 - 2000) / 1000.0                    # Prey Seeker's y_offset 2000

    def a(tag, dur=None, loop=False):
        nonlocal t
        an = Anim(dense(sp, tag, "reksai", z), t, 0, 0, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def wait(ms):
        a("idle", ms, loop=True)

    def on(unit, tag, when, sheet=None, under_=False, until=None):
        o = OnFoe(frames_of(sheet or small, tag), when, unit, until=until)
        (under if under_ else over).append(o)

    def mine(tag, when, sheet=None, under_=False, until=None, follow=True):
        if follow:
            o = OnMe(frames_of(sheet or small, tag), when, me, until=until)
        else:
            x, y = me.pos(when)
            o = Anim(frames_of(sheet or small, tag), when, x, y)
        (under if under_ else over).append(o)

    def mark(when):
        on(d, "r_mark", when, until=when + tick(P["mark_t"]))

    def bite(tag, hit_at, fx_tag, sheet=None):
        hit = t + tick(hit_at)
        on(d, fx_tag, hit, sheet)
        d.flinches.append(hit)
        mark(hit)
        a(tag, tick(P["atk_dur"] if tag == "attack" else P["e_dur"]))
        return hit

    wait(400)
    # two bites, the prey mark over Darius
    for _ in range(2):
        bite("attack", P["a_hit"], "a_hit")
        wait(tick(P["atk_cd"] - P["atk_dur"]))
    # Queen's Wrath: the whirl under her for q_t, the pounce, two splashing attacks
    q0 = t
    under.append(OnMe(frames_of(small, "q_buff"), q0, me, until=q0 + tick(P["q_t"])))
    hit = t + tick(P["q_hit"])
    on(d, "q_hit", hit)
    d.flinches.append(hit)
    mark(hit)
    a("skill", tick(P["q_dur"]))
    gap = tick(P["atk_cd"] * 100 / (100 + P["q_as"]))
    for _ in range(2):
        bite("attack", P["a_hit"], "q_hit")
        wait(max(0.0, gap - tick(P["atk_dur"])))
    # full Fury: the flames on her crest, then Furious Bite
    full = t
    over.append(OnMe(frames_of(small, "p_full"), full, me, until=full + 700))
    wait(500)
    bite("bite", P["e_hit"], "e_hit")
    wait(300)
    # Darius backs off; Prey Seeker from the ground, its burst flying at him
    d.slides.append((t, t + 400, 70))
    wait(450)
    rel = t + tick(P["q2_at"])
    mine("q2_cast", rel, under_=True, follow=False)
    mx, my = me.pos(rel)
    dx, dy = d.pos(rel)
    arrive = rel + tick(max(1.0, abs(dx - mx) / (P["q2_speed"] / 1000.0)))
    over.append(Turned(frames_of(small, "q2_shot"), rel, int(mx), int(my - lift), loop=True, until=arrive, x1=dx, y1=dy))
    on(d, "q2_hit", arrive)
    d.flinches.append(arrive)
    a("skill_q2", tick(P["q2_dur"]))
    wait(300)
    # Burrow: into the ground (her Fury healing her), the mound tunnelling to him, Unburrow knocking him up
    w0 = t
    mine("w_dig", w0, big, under_=True, follow=False)
    mine("w_heal", w0, follow=True)
    go = w0 + tick(P["w_go"])
    mx, _ = me.pos(go)
    dx, _ = d.pos(go)
    goal = dx - 30
    arrive = go + tick(max(2.0, (goal - mx) / (P["w_speed"] / 1000.0)))
    me.moves.append((go, arrive, mx, goal))
    a("skill2", arrive - t)
    mine("w_burst", arrive, big, under_=True, follow=False)
    on(d, "w_up", arrive, until=arrive + tick(P["w_up"]))
    d.hops.append((arrive, arrive + tick(P["w_up"]), 16))
    d.flinches.append(arrive)
    mark(arrive)
    a("skill2_up", tick(P["w_up_t"]))
    wait(max(0.0, arrive + tick(P["w_up"]) - t) + 300)
    # Void Rush: into the Void (r_hide), the lunge out at him, the crossed claws
    r0 = t
    mine("r_dive", r0, big, under_=True, follow=False)
    a("ult", tick(P["r_hide"]))
    d.slides.append((r0, r0 + 600, 40))
    mx, _ = me.pos(t)
    dx, _ = d.pos(t)
    goal = dx - 26
    land = t + tick(max(2.0, (goal - mx) / (P["r_speed"] / 1000.0)))
    me.moves.append((t, land, mx, goal))
    mine("r_burst", land, big, follow=False)
    on(d, "r_hit", land, big)
    d.flinches.append(land)
    d.death = land + tick(6)
    a("ult_hit", tick(P["r_dur"]))
    wait(1400)
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_reksai_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_reksai_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_reksai_showcase.gif")))


if __name__ == "__main__":
    main()
