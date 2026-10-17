#!/usr/bin/env python3
"""Preview images for Yunara, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_yunara.py [--out docs/preview] [--only frames|effects|showcase]

  league_yunara_frames.png    every animation's dense frames (hd_, PPU 1.5, as league.dll shows them)
  league_yunara_effects.png   every effect animation, 3x
  league_yunara_showcase.gif  a scripted fight against Darius, timed like the kit (tools/kit/build_yunara.py, 60 ticks
                              a second): two bead attacks fill her Unleash and Cultivation of Spirit flares on (the
                              spirit embers on her hands); an empowered bead and its ripple spreading under him; Arc of
                              Judgment - the spinning bead through him (the slow ring) and on to where it stops and
                              spins; Kanmei's Steps (the gust at her feet, the speed); Transcend One's Self (the gold
                              star behind her, the aura); Arc of Ruin - the charge star over her head, the aiming line,
                              the blast through him; Untouchable Shadow's flip back; empowered beads until he falls; 3x
Projectiles fly as the kit flies them: lifted 5000 - y_offset over her pivot, at the target's pivot, turned to their
way (champion-data section 6); the laser is its LineRangeProjectile's picture, centred on the line.
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
from build_yunara import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_yunara")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_yunara_fx", "league_yunara_big")}


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_yunara_fx"], fx["league_yunara_big"]
    W, H = 300, 110
    gy = 78
    x0 = 92
    d = Foe(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 54, gy)     # in her attack range
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        an = Anim(dense(sp, tag, "yunara", z), t, 0, 0, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def wait(ms):
        a("idle", ms, loop=True)

    def fly(tag, at, x1, y1, y_offset, speed, sheet=None, loop=True):
        """A projectile from over her pivot to (x1, y1); its arrival."""
        lift = (5000 - y_offset) / 1000.0
        mx, my = me.pos(at)
        xs, ys = mx, my - lift
        arrive = at + tick(max(1.0, ((x1 - xs) ** 2 + (y1 - ys) ** 2) ** 0.5 / (speed / 1000.0)))
        over.append(Turned(frames_of(sheet or small, tag), at, int(round(xs)), int(round(ys)), loop=loop,
                           until=arrive, x1=x1, y1=y1))
        return arrive

    def on(unit, tag, when, sheet=None, under_=False, until=None):
        o = OnFoe(frames_of(sheet or small, tag), when, unit, until=until)
        (under if under_ else over).append(o)

    def mine(tag, when, sheet=None, under_=False, until=None):
        o = OnMe(frames_of(sheet or small, tag), when, me, until=until)
        (under if under_ else over).append(o)

    def at_spot(tag, when, x, y, sheet=None, under_=False):
        an = Anim(frames_of(sheet or small, tag), when, int(x), int(y))
        (under if under_ else over).append(an)

    q_on = []      # (from, to) of Cultivation of Spirit

    def empowered(when):
        return any(f <= when < u for f, u in q_on)

    def bead(kill=False):
        """A basic attack: the bead (empowered while Q is on: its hit, the ripple under him)."""
        nonlocal t
        rel = t + tick(P["a_st"])
        q = empowered(rel)
        ux, uy = d.pos(rel)
        hit = fly("q_bead" if q else "a_bead", rel, ux, uy, P["bead_y"], P["bead_speed"])
        on(d, "q_hit" if q else "a_hit", hit)
        if q:
            dx, dy = d.pos(hit)
            at_spot("q_spread", hit + tick(1), dx, dy, big, under_=True)
        d.flinches.append(hit)
        if kill:
            d.death = hit + tick(2)
        a("attack", tick(P["atk_dur"]))
        return hit

    wait(400)
    bead()
    wait(tick(P["atk_cd"] - P["atk_dur"]))
    hit = bead()
    # the second champion hit fills Unleash in this script (four in League's count): Cultivation of Spirit flares on
    mine("q_burst", hit + tick(1), big)
    q_on.append((hit + tick(1), hit + tick(1 + P["q_t"])))
    mine("q_on", hit + tick(1), until=hit + tick(1 + P["q_t"]))
    wait(tick(P["atk_cd"] - P["atk_dur"]))
    bead()
    wait(300)
    # Arc of Judgment: the lock, the bead flying through him and on, the spin where it stops
    rel = t + tick(P["w_rel"])
    mx, my = me.pos(rel)
    end_x = mx + P["w_len"] / 1000.0
    lift = (5000 - P["w_y"]) / 1000.0
    stop = fly("w_bead", rel, end_x, my - lift, P["w_y"], P["w_speed"])
    dx, _ = d.pos(rel)
    through = rel + tick((dx - mx) / (P["w_speed"] / 1000.0))
    on(d, "w_hit", through)
    on(d, "w_slow0", through, under_=True, until=through + tick(30))
    d.flinches.append(through)
    at_spot("w_end", stop, end_x, my, under_=True)
    a("skill", tick(P["w_dur"]))
    wait(500)
    # Kanmei's Steps: the gust and the speed (a few steps toward him)
    e0 = t
    mine("e_cast", e0, under_=True)
    mine("e_ms", e0, under_=True, until=e0 + tick(P["e_t"]))
    a("skill2", tick(12))
    me.moves.append((t, t + 300, me.pos(t)[0], me.pos(t)[0] + 8))
    a("run", 300, loop=True)
    wait(200)
    # Transcend One's Self: the star behind her, the aura and Cultivation of Spirit for its whole time
    r0 = t
    mine("r_burst", r0, big, under_=True)
    mine("r_on", r0, big, under_=True, until=r0 + tick(P["r_t"]))
    q_on.append((r0, r0 + tick(P["r_t"])))
    mine("q_on", r0, until=r0 + tick(P["r_t"]))
    a("ult", tick(P["r_anim"]))
    wait(200)
    # Arc of Ruin: the charge over her head, the aiming line from the cast, the blast at rw_apply
    l0 = t
    mx, my = me.pos(l0)
    mine("rw_charge", l0, big)
    at_spot("rw_beam", l0, mx + P["rw_len"] / 2000.0, my, big)
    hit = l0 + tick(P["rw_apply"] - 1)
    on(d, "rw_hit", hit)
    on(d, "rw_slow0", hit, under_=True, until=hit + tick(30))
    d.flinches.append(hit)
    a("skill_r", tick(P["rw_dur"]))
    wait(200)
    # Untouchable Shadow: the flip, moved back by the dash
    f0 = t
    mine("re_trail", f0, big, under_=True)
    mx = me.pos(f0)[0]
    me.moves.append((f0, f0 + tick(P["re_t"]), mx, mx - P["re_v"] * P["re_t"] / 1000.0))
    a("skill2_r", tick(P["re_t"] + 2))
    wait(200)
    # empowered beads from further back until he falls
    bead()
    wait(tick(P["atk_cd"] - P["atk_dur"]))
    bead(kill=True)
    wait(1200)
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_yunara_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_yunara_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_yunara_showcase.gif")))


if __name__ == "__main__":
    main()
