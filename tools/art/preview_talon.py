#!/usr/bin/env python3
"""Preview images for Talon, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_talon.py [--out docs/preview] [--only frames|effects|showcase]

  league_talon_frames.png    every animation, frame by frame, 3x on the arena colour
  league_talon_effects.png   every effect animation, 3x
  league_talon_showcase.gif  a scripted gank on Darius with Garen behind him, timed like the kit
                             (tools/kit/build_talon.py, 60 ticks a second): W Rake - the fan of blades out through
                             Darius and back, the slow; the W -> Q leap as the blades turn back, the wounds over him;
                             the stab that makes him bleed; R - the blades out to the ring round his cast point,
                             hanging there through the stealth while he slips back and comes in, the stab that brings
                             them in to him; Assassin's Path - the vault away from Darius and Garen; 3x
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
from preview_pyke import Me, OnFoe, OnMe, mirrored  # noqa: E402
from build_talon import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_talon")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_talon_fx", "league_talon_big")}
REACH = 30                                      # where his stabs land from (px from Darius)
BLADE = P["w_speed"] / 1000                     # px a tick
BLADE_Y = P["w_y"] // 1000 + 8                  # the blades fly this far over the pivot


def faded(fr, alpha=90):
    """His frames while stealthed: drawn see-through (his own team sees him so)."""
    out = []
    for f, ms in fr:
        g = f.copy()
        a = g.getchannel("A").point(lambda v: v * alpha // 255)
        g.putalpha(a)
        out.append((g, ms))
    return out


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_talon_fx"], fx["league_talon_big"]
    W, H = 260, 110
    gy = 86
    x0 = 50
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 70, gy)
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 150, gy)
    me = Me(x0, gy)
    body, under, over = [], [], []
    face = [False]
    stealth = [None]
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        if dur is not None and dur <= 0:
            return None
        x, y = me.pos(t)
        fr = frames_of(sp, tag)
        if stealth[0] and stealth[0][0] <= t < stealth[0][1]:
            fr = faded(fr)
        an = Anim(fr, t, x, y, loop=loop, until=(t + dur) if dur else None, flip=face[0])
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def hit(foe, tag, when, sheet=None):
        over.append(OnFoe(frames_of(sheet or small, tag), when, foe))
        foe.flinches.append(when)

    def at(sheet, tag, when, x, y=gy, until=None, loop=False, layer=None):
        an = Anim(frames_of(sheet, tag), when, x, y, loop=loop, until=until)
        (layer if layer is not None else over).append(an)
        return an

    def fly(tag, when, x_from, x_to, left=False):
        dur = tick(max(1, abs(x_to - x_from) / BLADE))
        fr = frames_of(small, tag)
        over.append(Anim(mirrored(fr) if left else fr, when, x_from, gy - BLADE_Y, until=when + dur, x1=x_to,
                         y1=gy - BLADE_Y))
        return when + dur

    a("idle", 500, loop=True)
    # W Rake out through Darius and back, with the W -> Q leap as the blades turn back
    t0 = t
    out_t = t0 + tick(P["w_at"] - 1)
    x_me = me.pos(t0)[0]
    far = x_me + P["w_len"] // 1000
    end_out = fly("w_out", out_t, x_me + 6, far)
    hit(d, "w_hit", out_t + tick(max(1, (d.pos(out_t)[0] - x_me) / BLADE)))
    back_t = end_out + tick(P["w_wait"])
    a("skill", tick(P["w_dur"]))
    lead = t0 + tick(P["w_dur"] - 1)
    a("idle", max(0, lead - t), loop=True)
    # the leap
    at(small, "q_leap", t + tick(1), me.pos(t)[0], layer=under)
    land = t + tick(P["q_go"] + 4)
    me.moves.append((t + tick(1), land, me.pos(t)[0], d.pos(land)[0] - REACH))
    a("skill2", tick(P["q_dur"]))
    hit(d, "q_hit", land)
    over.append(OnFoe(frames_of(small, "p_wound"), out_t + tick(6), d, until=land + 1400))
    # the blades come back to where he is now
    fly("w_back", back_t, far, me.pos(back_t)[0] + 4, left=True)
    hit(d, "w_hit", back_t + tick(2))
    over.append(OnFoe(frames_of(small, "w_slow"), back_t + tick(2), d, until=back_t + tick(2 + P["w_slow_t"])))
    a("idle", 200, loop=True)
    # the third wound: the stab makes him bleed
    hit(d, "a_hit", t + tick(P["a_st"]))
    hit(d, "p_bleed", t + tick(P["a_st"]) + 20)
    a("attack", tick(P["atk_dur"]))
    a("idle", 400, loop=True)
    # R: the blades out to the ring, hanging on the cast point through the stealth, a stab brings them in to him
    r0 = t
    rx = me.pos(r0)[0]
    at(big, "r_out", r0 + tick(P["r_at"] - 1), rx)
    ring0 = r0 + tick(P["r_at"] - 1 + P["r_fly"])          # the anchor's first ring piece, then one every r_step
    hit(d, "r_hit", r0 + tick(P["r_at"]) + 60)
    a("ult", tick(P["r_dur"]))
    stealth[0] = (t, t + 900)
    under_on = Anim(frames_of(small, "r_on"), t, 0, 0, loop=True, until=t + 900)
    under_on.pos = me.pos
    under.append(under_on)
    s0 = t
    sx = me.pos(s0)[0]
    me.moves.append((s0, s0 + 400, sx, sx - 26))                # unseen, he slips back...
    face[0] = True
    a("run", 400, loop=True)
    a("idle", 150, loop=True)
    s1 = t
    me.moves.append((s1, s1 + 350, sx - 26, d.pos(s1)[0] - REACH))   # ...and comes in for the stab
    face[0] = False
    a("run", 350, loop=True)
    hit(d, "a_hit", t + tick(P["a_st"]))
    stab = t + tick(P["a_st"])
    a("attack", tick(P["atk_dur"]))
    stealth[0] = None
    at(big, "r_back", stab, me.pos(stab)[0])
    # the ring's pieces while r_on lasts: the stab's return takes it off, so the piece under way runs out
    k, when = 0, ring0
    while when < stab:
        at(big, f"r_ring{k % 4}", when, rx)
        k, when = k + 1, when + tick(P["r_step"])
    hit(d, "r_hit", stab + 120)
    a("idle", 300, loop=True)
    # Assassin's Path: two champions near - the vault away, then the haste
    v0 = t
    at(small, "e_vault", v0, me.pos(v0)[0], layer=under)
    me.moves.append((v0, v0 + tick(P["e_tick"]), me.pos(v0)[0], me.pos(v0)[0] - P["e_speed"] * P["e_tick"] // 1000))
    a("skill_e", tick(P["e_anim"]))
    h0 = t
    hst = OnMe(frames_of(small, "e_haste"), h0, me, until=h0 + 700)
    under.append(hst)
    face[0] = True
    me.moves.append((h0, h0 + 700, me.pos(h0)[0], me.pos(h0)[0] - 40))
    a("run", 700, loop=True)
    face[0] = False
    a("idle", 700, loop=True)
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
                                os.path.join(args.out, "league_talon_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_talon_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_talon_showcase.gif")))


if __name__ == "__main__":
    main()
