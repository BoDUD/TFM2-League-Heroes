#!/usr/bin/env python3
"""Preview images for Kindred, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_kindred.py [--out docs/preview] [--only frames|effects|showcase]

  league_kindred_frames.png    every animation's dense frames (hd_, PPU 2.86, as league.dll shows them)
  league_kindred_effects.png   every effect animation, 3x
  league_kindred_showcase.gif  a scripted fight, Darius in her reach, Garen a row behind him, Taric behind her, timed like
                               the kit (tools/kit/build_kindred.py, 60 ticks a second): two arrows (the arrow nocked,
                               the loosing flash, the spirit arrow flying, its hit); Dance of Arrows - the hop toward
                               them leaving its dust and trail, the volley at Darius and Garen; Mounting Dread - the
                               dread arrow, its hit, the mark over Darius, three arrows and the Wolf's pounce; Wolf's
                               Frenzy - the smoke called up, the hunting ground, the Wolf's bites; Lamb's Respite - the
                               star off the raised bow, the circle for 4 s, the heals on her and Taric; 3x
Projectiles fly as the kit flies them: from over her pivot, lifted 5000 - y_offset, at the target's pivot, turned to
their way (champion-data section 6).
"""
import argparse
import math
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
from preview_annie import Held  # noqa: E402
from preview_ashe import Anim, tick  # noqa: E402
from preview_dense import dense, dense_rows, put  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_pyke import Me, OnFoe, OnMe  # noqa: E402
from build_kindred import P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_kindred")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_kindred_fx", "league_kindred_big")}


class Turned(Anim):
    """A projectile's picture turned to its flight from (x, y) to (x1, y1), as the game turns a view."""

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        deg = -math.degrees(math.atan2(self.y1 - self.y, self.x1 - self.x))
        self.fr = [(f.rotate(deg, resample=Image.NEAREST, expand=True) if f.width > 1 else f, ms) for f, ms in self.fr]


def fx_contact(sprites, out, z=3, label_w=90):
    """preview_garen.contact with each tag's frames listed once: the zones repeat their loop for the whole time
    (w_zone 84 frames, r_zone 39), which made a 31000-px row."""
    rows = []
    for sp, tag, label in sprites:
        fr, seen = [], set()
        for f, ms in frames_of(sp, tag):
            key = f.tobytes()
            if key not in seen:
                seen.add(key)
                fr.append(f)
        whole = frames_of(sp, tag)
        boxes = [b for b in (f.getbbox() for f in fr) if b]
        x0, x1 = min(b[0] for b in boxes) - 2, max(b[2] for b in boxes) + 2
        y0, y1 = min(b[1] for b in boxes) - 2, max(b[3] for b in boxes) + 2
        cw, ch = x1 - x0, y1 - y0
        row = Image.new("RGBA", (label_w + len(fr) * (cw * z + 4), max(ch * z + 6, 40)), (28, 28, 28, 255))
        d = ImageDraw.Draw(row)
        d.text((4, 4), label, fill=(255, 255, 255, 255))
        d.text((4, 18), f"{len(fr)} / {len(whole)}f {sum(ms for _, ms in whole):.0f}ms", fill=(170, 170, 170, 255))
        for i, f in enumerate(fr):
            cell = Image.new("RGBA", (cw, ch), ARENA)
            cell.alpha_composite(f.crop((x0, y0, x1, y1)))
            row.paste(cell.resize((cw * z, ch * z), Image.NEAREST), (label_w + i * (cw * z + 4), 3))
        rows.append(row)
    W = max(r.width for r in rows)
    img = Image.new("RGBA", (W, sum(r.height for r in rows)), (28, 28, 28, 255))
    y = 0
    for r in rows:
        img.paste(r, (0, y))
        y += r.height
    img.save(T.long_path(out))
    return img.size


def showcase(out, z=3, step=40):
    sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_kindred_fx"], fx["league_kindred_big"]
    W, H = 200, 112
    gy = 78
    x0 = 80
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 48, gy)          # in her reach (55000)
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 66, gy - 8)       # a row behind him
    ally = Anim(frames_of(load(os.path.join(LEAGUE, "champions", "league_taric")), "idle"), 0, x0 - 28, gy - 10,
                loop=True)
    me = Me(x0, gy)
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        x, y = me.pos(t)
        an = Anim(dense(sp, tag, "kindred", z), t, x, y, loop=loop, until=(t + dur) if dur else None)
        an.pos = me.pos
        body.append(an)
        t = an.until
        return an

    def wait(ms):
        a("idle", ms, loop=True)

    def fly(tag, at, foe, y_offset, speed):
        """A TargetProjectile from over her pivot to the foe's pivot; its arrival."""
        lift = (5000 - y_offset) / 1000.0
        mx, my = me.pos(at)
        fx_, fy = foe.pos(at)
        x1, y1 = mx, my - lift
        arrive = at + tick(max(1.0, math.hypot(fx_ - x1, fy - y1) / (speed / 1000.0)))
        over.append(Turned(frames_of(small, tag), at, int(round(x1)), int(round(y1)), loop=True, until=arrive,
                           x1=fx_, y1=fy))
        return arrive

    def on(foe, tag, when, sheet=None, until=None):
        over.append(OnFoe(frames_of(sheet or small, tag), when, foe, until=until))

    def arrow(foe, then=True):
        """Her attack: the arrow leaves as the string goes straight (a_st + 1), its hit where it lands."""
        start = t
        land = fly("a_arrow", start + tick(P["a_st"] + 1), foe, P["a_y"], P["a_speed"])
        on(foe, "a_hit", land)
        foe.flinches.append(land)
        a("attack", tick(P["atk_dur"]))
        if then:
            wait(tick(P["atk_cd"] - P["atk_dur"]))
        return land

    wait(400)
    for _ in range(2):
        arrow(d)
    # Dance of Arrows: the hop toward them (the target stands beyond q_close), its dust left where she stood; the
    # arrows on q_at, one to each enemy champion in reach
    q0 = t
    hop = P["q_hop"] / 1000.0
    under.append(Anim(frames_of(small, "q_dash"), q0 + tick(P["q_go"]), x0, gy))
    me.moves.append((q0 + tick(P["q_go"]), q0 + tick(P["q_go"] + P["q_move_t"]), x0, x0 + hop))
    for foe in (d, g):
        land = fly("q_arrow", q0 + tick(P["q_at"]), foe, P["q_y"], P["q_speed"])
        on(foe, "q_hit", land)
        foe.flinches.append(land)
    a("skill", tick(P["q_anim"]))
    wait(300)
    # Mounting Dread: the dread arrow, its hit, the mark over him (replayed every e_pic ticks), three arrows, the pounce
    e0 = t
    land = fly("e_arrow", e0 + tick(P["e_at"]), d, P["e_y"], P["e_speed"])
    on(d, "e_hit", land)
    d.flinches.append(land)
    a("skill2", tick(P["e_anim"]))
    wait(200)
    lands = [arrow(d) for _ in range(3)]
    k = 0
    while land + tick(k * P["e_pic"]) < lands[-1]:
        on(d, "e_mark", land + tick(k * P["e_pic"]))
        k += 1
    on(d, "e_bite", lands[-1], sheet=big)
    # Wolf's Frenzy: the hunting ground where she stands, the Wolf's bites on Darius inside it
    w0 = t
    zx, _ = me.pos(w0)
    under.append(Anim(frames_of(big, "w_zone"), w0 + tick(P["w_at"]), zx, gy))
    a("w_cast", tick(P["w_anim"]))
    wait(200)
    arrow(d)
    arrow(d)
    # Lamb's Respite: the circle on r_at round her, the heals on her and Taric when it ends
    r0 = t
    zr, _ = me.pos(r0)
    under.append(Anim(frames_of(big, "r_zone"), r0 + tick(P["r_at"]), zr, gy))
    end_r = r0 + tick(P["r_at"] + P["r_t"])
    a("ult", tick(P["r_anim"]))
    while t < end_r - 900:
        arrow(d)
    wait(max(0.0, end_r - t))
    over.append(OnMe(frames_of(small, "r_heal"), end_r, me))
    over.append(Anim(frames_of(small, "r_heal"), end_r, ally.x, ally.y))
    wait(900)
    # the bites, every w_per ticks from w_first while the ground lasts
    b = w0 + tick(P["w_at"] + P["w_first"])
    while b < min(t, w0 + tick(P["w_at"] + P["w_t"])):
        on(d, "w_bite", b)
        d.flinches.append(b)
        b += tick(P["w_per"])
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
        units = [(d.pos(tt)[1], d.frame(tt), d.pos(tt)), (g.pos(tt)[1], g.frame(tt), g.pos(tt)),
                 (ally.pos(tt)[1], ally.frame(tt), ally.pos(tt))]
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
        print("frames", contact(dense_rows(s), os.path.join(args.out, "league_kindred_frames.png"), z=1))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[15:]}:{t['name']}") for t in sp.tags]
        print("effects", fx_contact(rows, os.path.join(args.out, "league_kindred_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_kindred_showcase.gif")))


if __name__ == "__main__":
    main()
