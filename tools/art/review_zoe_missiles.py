#!/usr/bin/env python3
"""league_zoe 0.7.0's Spell Thief missiles drawn as the add-on flies them, to look at before a game.

    python tools/art/review_zoe_missiles.py --out C:/t/zoe_missiles.gif

The user, 2026-11-09: 「还有佐伊的飞弹做的要像英雄联盟那样啊 从背后过来的 现在不太像」. League's missile (ZoeWPassiveMissile)
circles round her from her chest (CircleMovement), then ZoeWPassiveMissileTwo chases the target. The add-on's path
(addons/league_zoe/src/lib.rs: orbit_at, chase - the numbers below are its ORBIT_* / CHEST / AIM_LIFT and the data's
w_n / w_gap / w_speed): each missile appears behind her, swings over her head to her front in ORBIT_T ticks round her
chest, then chases the target's chest at w_speed. Drawn here: Zoe's sprite now and a target (Garen, mirrored) on their
pivots (a sheet frame's centre OLD_SOLES px over the soles), the missile picture (league_zoe_fx w_missile) turned to its
flight as the game turns a projectile's picture, the path so far as faint dots, w_hit where one lands. 1000 game units
= 1 px, Z px a game px; one GIF frame a tick (50 ms, slower than the game's 60 a second).
"""
import argparse
import json
import math
import os

from PIL import Image, ImageDraw

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
# addons/league_zoe/src/lib.rs
ORBIT_T, ORBIT_RX, ORBIT_RY, ORBIT_SHRINK, ORBIT_GROW = 12, 15_000.0, 20_000.0, 2_500.0, 3
CHEST, AIM_LIFT = 17_000.0, 12_000.0
# the champion data (tools/kit/build_zoe.py P)
W_N, W_GAP, W_SPEED = 3, 5, 4000.0
OLD_SOLES = 11.5
Z = 4


def frame(stem, tag, k=0):
    a = json.load(open(stem + "#anim.fanim", encoding="utf-8-sig"))["anims"][tag]["frames"][k]["data"]
    x, y, w, h = (int(a[q]) for q in ("x", "y", "w", "h"))
    return Image.open(stem + "#sheet.png").convert("RGBA").crop((x, y, x + w, y + h))


def unit(v):
    d = math.hypot(*v)
    return (v[0] / d, v[1] / d) if d > 1e-9 else None


def up_of(f):
    a, b = (f[1], -f[0]), (-f[1], f[0])
    return a if a[1] <= b[1] else b


def orbit_at(c, f, p, age, k):
    phi = math.pi * min(1.0, (age + 1) / ORBIT_T)
    g = min(1.0, (age + 1) / ORBIT_GROW)
    rx, ry = (max(4_000.0, r0 - ORBIT_SHRINK * k) * g for r0 in (ORBIT_RX, ORBIT_RY))
    return (c[0] - rx * f[0] * math.cos(phi) + ry * p[0] * math.sin(phi),
            c[1] - rx * f[1] * math.cos(phi) + ry * p[1] * math.sin(phi))


def chase(at, aim, speed):
    dx, dy = aim[0] - at[0], aim[1] - at[1]
    d = math.hypot(dx, dy)
    return None if d <= speed else (at[0] + dx / d * speed, at[1] + dy / d * speed)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="the GIF to write")
    ap.add_argument("--ticks", type=int, default=60)
    a = ap.parse_args()
    champs, fx = os.path.join(REPO, "league", "champions"), os.path.join(REPO, "league", "effects")
    zoe = frame(os.path.join(champs, "league_zoe"), "idle_base")
    foe = frame(os.path.join(champs, "league_garen"), "idle_base").transpose(Image.FLIP_LEFT_RIGHT)
    comet = frame(os.path.join(fx, "league_zoe_fx"), "w_missile", 1)
    hit = [frame(os.path.join(fx, "league_zoe_fx"), "w_hit", k) for k in range(3)]
    her, them = (90_000.0, 110_000.0), (150_000.0, 104_000.0)
    sw, sh = 230, 150
    missiles, hits, frames = [], [], []
    for tick in range(a.ticks):
        for k in range(W_N):
            if tick == k * W_GAP:
                c = (her[0], her[1] - CHEST)
                f = unit((them[0] - c[0], them[1] - AIM_LIFT - c[1])) or (1.0, 0.0)
                missiles.append(dict(k=k, born=tick, at=c, last=c, f=f, p=up_of(f), trail=[]))
        can = Image.new("RGBA", (sw * Z, sh * Z), (70, 92, 70, 255))
        d = ImageDraw.Draw(can)
        for im, pos in ((zoe, her), (foe, them)):
            big = im.resize((im.width * Z, im.height * Z), Image.NEAREST)
            can.alpha_composite(big, (int(pos[0] / 1000 * Z - big.width / 2),
                                      int((pos[1] / 1000 - OLD_SOLES) * Z - big.height / 2)))
        keep = []
        for m in missiles:
            age = tick - m["born"]
            c = (her[0], her[1] - CHEST)
            nxt = (orbit_at(c, m["f"], m["p"], age, m["k"]) if age < ORBIT_T
                   else chase(m["at"], (them[0], them[1] - AIM_LIFT), W_SPEED))
            if nxt is None:
                hits.append((tick, (them[0], them[1] - AIM_LIFT)))
                continue
            m["last"], m["at"] = m["at"], nxt
            m["trail"] = (m["trail"] + [nxt])[-6:]
            keep.append(m)
        missiles = keep
        for m in missiles:
            for q in m["trail"][:-1]:
                x, y = q[0] / 1000 * Z, q[1] / 1000 * Z
                d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(160, 220, 255, 120))
            v = unit((m["at"][0] - m["last"][0], m["at"][1] - m["last"][1])) or m["f"]
            pic = comet.resize((comet.width * Z, comet.height * Z), Image.NEAREST)
            pic = pic.rotate(math.degrees(math.atan2(-v[1], v[0])), expand=True, resample=Image.NEAREST)
            can.alpha_composite(pic, (int(m["at"][0] / 1000 * Z - pic.width / 2), int(m["at"][1] / 1000 * Z - pic.height / 2)))
        for t0, at in hits:
            if tick - t0 < 6:
                im = hit[min(2, (tick - t0) // 2)]
                big = im.resize((im.width * Z, im.height * Z), Image.NEAREST)
                can.alpha_composite(big, (int(at[0] / 1000 * Z - big.width / 2), int(at[1] / 1000 * Z - big.height / 2)))
        d.text((8, 8), f"tick {tick}", fill=(255, 255, 255, 255))
        frames.append(can.convert("RGB"))
    frames[0].save(a.out, save_all=True, append_images=frames[1:], duration=50, loop=0)
    print("written", a.out, len(frames), "frames; hits at ticks", [t for t, _ in hits])


if __name__ == "__main__":
    main()
