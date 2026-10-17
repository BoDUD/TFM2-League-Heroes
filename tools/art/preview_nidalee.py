#!/usr/bin/env python3
"""Preview images for Nidalee, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_nidalee.py [--out docs/preview] [--only frames|effects|showcase]

  league_nidalee_frames.png    every animation's dense frames (hd_, PPU 2.2, as league.dll shows them), both forms
  league_nidalee_effects.png   every effect animation, 3x
  league_nidalee_showcase.gif  a scripted fight with Darius in front and Taric behind her, timed like the kit
                               (tools/kit/build_nidalee.py, 60 ticks a second): two javelins thrown from range; Javelin
                               Toss flying at Darius, its burst, the hunter's mark over him and the gold ring under her;
                               Primal Surge on Taric (the leaves, his green swirl); Bushwhack lobbed under Darius, the
                               snare, its snap; the turn into the cougar; Pounce onto the hunted Darius (the dust, the
                               landing, the hit) and Swipe at once; Takedown readied and the bite; a claw; the turn back;
                               3x
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
from preview_pyke import Me, OnFoe, OnMe  # noqa: E402
from build_nidalee import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_nidalee")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_nidalee_fx", "league_nidalee_big")}
HAND = 10                                        # her throwing hand: px in front of her pivot (the javelins leave there)
SPEAR = P["a_speed"] / 1000                      # px a tick
JAV = P["q_speed"] / 1000
POUNCE = P["cw_speed"] / 1000


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_nidalee_fx"], fx["league_nidalee_big"]
    W, H = 260, 120
    gy = 86
    x0 = 90
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 100, gy)     # in her javelin's reach
    taric = load(os.path.join(LEAGUE, "champions", "league_taric"))
    tx = x0 - 50
    ally = Anim(frames_of(taric, "idle"), 0, tx, gy, loop=True)
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        x, y = me.pos(t)
        an = Anim(dense(sp, tag, "nidalee", z), t, x, y, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def hit(tag, when, sheet=None):
        over.append(OnFoe(frames_of(sheet or small, tag), when, d))
        d.flinches.append(when)

    def throw(tag, at, speed, view):
        rel = t + tick(at)
        sx = me.pos(rel)[0] + HAND
        arrive = rel + tick(max(1, (d.pos(rel)[0] - sx) / speed))
        over.append(Anim(frames_of(small, tag), rel, sx, gy - 16, until=arrive, x1=d.pos(rel)[0], y1=gy - 16))
        hit(view, arrive)
        return arrive

    a("idle", 400, loop=True)
    # two javelins thrown from range
    for _ in range(2):
        throw("a_spear", P["a_st"], SPEAR, "a_hit")
        a("attack", tick(P["atk_dur"]))
        a("idle", 250, loop=True)
    # Javelin Toss: the burst, the hunter's mark over Darius, the gold ring under her
    arrive = throw("q_spear", P["q_at"], JAV, "q_hit")
    over.append(OnFoe(frames_of(small, "hunted"), arrive, d, until=arrive + tick(P["p_t"])))
    under.append(OnMe(frames_of(small, "hunt"), arrive, me, until=arrive + tick(P["p_t"])))
    a("skill", tick(P["q_dur"]))
    a("idle", 200, loop=True)
    # Primal Surge on Taric
    e0 = t + tick(P["e_at"])
    over.append(Anim(frames_of(small, "e_heal"), e0, tx, gy))
    under.append(Anim(frames_of(small, "e_as"), e0, tx, gy, loop=True, until=e0 + 1800))
    a("skill2", tick(P["e_anim"]))
    a("idle", 200, loop=True)
    # Bushwhack lobbed under Darius: the snare, its snap
    w0 = t + tick(P["w_at"])
    land = w0 + tick(P["w_fly"])
    over.append(Anim(frames_of(small, "w_lob"), w0, me.pos(w0)[0] + HAND, gy - 20, until=land, x1=d.pos(w0)[0], y1=gy))
    under.append(Anim(frames_of(small, "w_trap"), land, d.pos(land)[0], gy, until=land + 1600))
    hit("w_snap", land + 200)
    a("skill2", tick(P["w_anim"]))
    a("idle", 300, loop=True)
    # the turn into the cougar
    over.append(OnMe(frames_of(big, "tf_cougar"), t, me))
    a("transform", tick(P["tf_dur"]))
    a("c_idle", 250, loop=True)
    # Pounce onto the hunted Darius (the dust, the landing, the hit) and Swipe at once
    p0 = t
    go = p0 + tick(P["cw_go"])
    land = go + tick(max(1, (d.pos(go)[0] - 30 - me.pos(go)[0]) / POUNCE))
    under.append(OnMe(frames_of(small, "cw_dust"), go, me))
    me.moves.append((go, land, me.pos(go)[0], d.pos(go)[0] - 30))
    a("c_pounce", land - p0)
    under.append(Anim(frames_of(big, "cw_land"), land, me.pos(land)[0], gy))
    hit("cw_hit", land)
    over.append(OnMe(frames_of(big, "ce_swipe"), t, me))
    hit("ce_hit", t + tick(P["ce_at"]))
    a("c_swipe", tick(P["ce_anim"]))
    a("c_idle", 250, loop=True)
    # Takedown readied, the bite
    over.append(OnMe(frames_of(small, "cq_arm"), t, me))
    a("c_idle", 300, loop=True)
    hit("cq_hit", t + tick(P["cq_st"]))
    a("c_skill", tick(P["cq_dur"]))
    a("c_idle", 200, loop=True)
    # a claw
    hit("c_hit", t + tick(P["c_atk_st"]))
    a("c_attack", tick(P["c_atk_dur"]))
    a("c_idle", 300, loop=True)
    # the turn back
    over.append(OnMe(frames_of(big, "tf_human"), t, me))
    a("c_transform", tick(P["tf_dur"]))
    a("idle", 900, loop=True)
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
        units = [(d.pos(tt)[1], d.frame(tt), d.pos(tt)), (ally.pos(tt)[1], ally.frame(tt), ally.pos(tt))]
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_nidalee_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[15:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_nidalee_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_nidalee_showcase.gif")))


if __name__ == "__main__":
    main()
