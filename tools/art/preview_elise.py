#!/usr/bin/env python3
"""Preview images for Elise, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_elise.py [--out docs/preview] [--only frames|effects|showcase]

  league_elise_frames.png    every animation's dense frames (hd_, PPU 1.8, as league.dll shows them), both forms
  league_elise_effects.png   every effect animation, 3x
  league_elise_showcase.gif  a scripted fight with Darius in front of her, timed like the kit (tools/kit/build_elise.py,
                             60 ticks a second): two venom spits; Neurotoxin and its splash; the Cocoon flying at Darius
                             and wrapping him; a Volatile Spiderling crawling over and bursting; the turn into the
                             spider; Venomous Bite leaping on him; a bite with three spiderlings; Skittering Frenzy;
                             Rappel - up on her thread, gone, down on him; the turn back; 3x
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
from build_elise import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_elise")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_elise_fx", "league_elise_big")}
HAND = 10                                        # her casting hand: px in front of her pivot
SPIT = P["a_speed"] / 1000                       # px a tick
BOLT = P["q_speed"] / 1000
WEB = P["e_speed"] / 1000
CRAWL = P["w_speed"] / 1000
LEAP = P["cq_speed"] / 1000
GAP = 46                                         # the spider stands this far from Darius's pivot (she is ~60 px long)


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_elise_fx"], fx["league_elise_big"]
    W, H = 260, 120
    gy = 86
    x0 = 80
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 110, gy)
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        x, y = me.pos(t)
        an = Anim(dense(sp, tag, "elise", z), t, x, y, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def hit(tag, when, sheet=None, until=None):
        over.append(OnFoe(frames_of(sheet or small, tag), when, d, until=until))
        d.flinches.append(when)

    def shoot(tag, at, speed, view, dy=-16):
        rel = t + tick(at)
        sx = me.pos(rel)[0] + HAND
        arrive = rel + tick(max(1, (d.pos(rel)[0] - sx) / speed))
        over.append(Anim(frames_of(small, tag), rel, sx, gy + dy, until=arrive, x1=d.pos(rel)[0], y1=gy + dy))
        if view:
            hit(view, arrive)
        return arrive

    a("idle", 400, loop=True)
    # two venom spits
    for _ in range(2):
        shoot("a_spit", P["a_st"], SPIT, "a_hit")
        a("attack", tick(P["atk_dur"]))
        a("idle", 220, loop=True)
    # Neurotoxin
    shoot("q_bolt", P["q_at"], BOLT, "q_hit")
    a("skill", tick(P["q_dur"]))
    a("idle", 200, loop=True)
    # the Cocoon: it wraps Darius (the stun's long middle frame)
    arrive = shoot("e_web", P["e_at"], WEB, None)
    over.append(OnFoe(frames_of(small, "e_hit"), arrive, d))
    a("skill2", tick(P["e_anim"]))
    a("idle", 300, loop=True)
    # a Volatile Spiderling crawls over and bursts
    arrive = shoot("w_spider", P["w_at"], CRAWL, None, dy=-2)
    under.append(Anim(frames_of(big, "w_boom"), arrive, d.pos(arrive)[0], gy))
    hit("w_hit", arrive + 60)
    a("skill2", tick(P["w_anim"]))
    a("idle", max(200, arrive - t + 200), loop=True)
    # the turn into the spider
    over.append(OnMe(frames_of(big, "tf_spider"), t, me))
    a("transform", tick(P["tf_dur"]))
    a("c_idle", 250, loop=True)
    # Venomous Bite: the leap on him and the bite
    b0 = t
    go = b0 + tick(P["cq_go"])
    land = go + tick(max(1, (d.pos(go)[0] - GAP - me.pos(go)[0]) / LEAP))
    me.moves.append((go, land, me.pos(go)[0], d.pos(go)[0] - GAP))
    a("c_skill", max(tick(P["cq_dur"]), land - b0 + 60))
    hit("cq_hit", land)
    a("c_idle", 200, loop=True)
    # a bite with three spiderlings on him
    hit("c_hit", t + tick(P["c_atk_st"]))
    hit("sl_bite3", t + tick(P["c_atk_st"]))
    a("c_attack", tick(P["c_atk_dur"]))
    a("c_idle", 200, loop=True)
    # Skittering Frenzy: the flare, the ring under her, two quick bites
    over.append(OnMe(frames_of(small, "cw_frenzy"), t, me))
    under.append(OnMe(frames_of(small, "cw_on"), t, me, until=t + 1600))
    a("c_idle", 250, loop=True)
    for _ in range(2):
        hit("c_hit", t + tick(P["c_atk_st"]))
        hit("sl_bite2", t + tick(P["c_atk_st"]))
        a("c_attack", tick(P["c_atk_dur"]))
    a("c_idle", 250, loop=True)
    # Rappel: back off, up on her thread, gone, down on him
    me.moves.append((t, t + 1, me.pos(t)[0], me.pos(t)[0] - 40))
    a("c_idle", 200, loop=True)
    over.append(OnMe(frames_of(big, "ce_up"), t, me))
    a("c_skill2", tick(P["ce_anim"]))
    gone = t
    t += tick(P["ce_up"]) - (tick(P["ce_anim"]) - tick(P["ce_rise"]))
    me.moves.append((gone, t, me.pos(gone)[0], d.pos(t)[0] - GAP))
    under.append(Anim(frames_of(big, "ce_land"), t, d.pos(t)[0] - GAP, gy))
    hit("ce_hit", t + 60)
    a("c_land", tick(P["cl_anim"]))
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
        units = [(d.pos(tt)[1], d.frame(tt), d.pos(tt))]
        if not (gone <= tt < gone + tick(P["ce_up"]) - (tick(P["ce_anim"]) - tick(P["ce_rise"]))):
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_elise_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_elise_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_elise_showcase.gif")))


if __name__ == "__main__":
    main()
