#!/usr/bin/env python3
"""Preview GIF of league_yasuo_wall's Wind Wall at game size: Yasuo, an enemy Ashe shooting arrows at him, the wall
going up (the gust at his feet, the pieces of rising wind along the bowed ground line), the arrows flashing where they
cross it (they fly on: the game cannot delete a missile, the add-on gives the damage back) and the wall dispersing.

    python tools/art/preview_yasuo_wall.py [--out C:/t/lu_yw/gif/yasuo_windwall.gif] [--zoom 4]

Two scenes side by side: the enemy to the right (the wall stands up and down) and down to the right (slanting). The
wall's place and shape are import_yasuo_wall.layout's (the add-on's `pieces`); pictures from
addons/league_yasuo_wall/effects/league_yasuo_wall_fx, the heroes' idles from league/champions. Every picture's middle
is its pivot, as in the game.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import import_yasuo_wall as YW  # noqa: E402
import pack_squill_windwall as P  # noqa: E402

FX = os.path.join(ROOT, "addons", "league_yasuo_wall", "effects", "league_yasuo_wall_fx")
LIFE = 4.0
SHOTS = [0.4, 1.6, 2.8]            # seconds the arrows leave Ashe
SPEED = 4.0                        # game px a tick
W, H = 150, 95


def anim(path, tag):
    a = json.load(open(P.lp(path + "#anim.fanim"), encoding="utf-8-sig"))["anims"][tag]["frames"]
    return P.frames(path, tag), [f["duration"] for f in a]


def at_time(fd, t, loop=True):
    frs, durs = fd
    tot = sum(durs)
    if loop:
        t = t % tot
    elif t >= tot or t < 0:
        return None
    acc = 0
    for f, d in zip(frs, durs):
        acc += d
        if t < acc:
            return f
    return frs[-1]


def cross(p0, p1, line):
    for a, b in zip(line, line[1:]):
        r, s = p1 - p0, b - a
        den = r[0] * s[1] - r[1] * s[0]
        if abs(den) < 1e-9:
            continue
        t = ((a - p0)[0] * s[1] - (a - p0)[1] * s[0]) / den
        u = ((a - p0)[0] * r[1] - (a - p0)[1] * r[0]) / den
        if 0 <= t <= 1 and 0 <= u <= 1:
            return p0 + r * t
    return None


def scene(me, foe, label):
    d = np.array(foe, float) - np.array(me, float)
    d /= np.linalg.norm(d)
    mid = np.array(me, float) * 1000 + d * YW.AHEAD
    pl, dots = YW.layout(tuple(mid), tuple(d))
    side = np.array([-d[1], d[0]])
    line = [(mid + side * YW.HALF * t + d * YW.BOW * (1 - t * t)) / 1000 for t in np.linspace(-1, 1, 9)]
    return dict(me=np.array(me, float), foe=np.array(foe, float), pl=[p / 1000 for p in pl],
                dots=[p / 1000 for p in dots], line=line, label=label, blocks={})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/lu_yw/gif/yasuo_windwall.gif")
    ap.add_argument("--zoom", type=int, default=4)
    a = ap.parse_args()
    Z = a.zoom
    yas = anim(os.path.join(ROOT, "league", "champions", "league_yasuo"), "idle")
    ashe = anim(os.path.join(ROOT, "league", "champions", "league_ashe"), "idle")
    ashe = ([f[:, ::-1].copy() for f in ashe[0]], ashe[1])                       # facing left, at Yasuo
    arrow = anim(os.path.join(ROOT, "league", "effects", "league_ashe_fx"), "arrow")
    plumes = [anim(FX, f"plume_{k}") for k in range(len(YW.WIDTHS))]
    ground = P.frames(FX, "ground")[0]
    cast, block, fade = anim(FX, "cast"), anim(FX, "block"), anim(FX, "fade")
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)

    def paste(img, f, cx, cy):
        if f is None:
            return
        h, w = f.shape[:2]
        img.alpha_composite(P.up(np.ascontiguousarray(f), Z), (int(round((cx - w / 2) * Z)), int(round((cy - h / 2) * Z))))

    scenes = [scene((32, 52), (122, 52), "敌人在右边"), scene((32, 30), (118, 80), "敌人在右下")]
    frames, DT, T = [], 0.05, LIFE + 0.6
    for i in range(int(T / DT)):
        t = i * DT
        row = []
        for sc in scenes:
            img = Image.new("RGBA", (W * Z, H * Z), P.ARENA)
            up = t < LIFE
            if up:
                for p in sc["dots"]:
                    paste(img, ground, p[0], p[1])
            me, foe = sc["me"], sc["foe"]
            items = [(me[1], "yas"), (foe[1], "ashe")] + ([(p[1], k) for k, p in enumerate(sc["pl"])] if up else [])
            for _, it in sorted(items, key=lambda x: x[0]):
                if it == "yas":
                    paste(img, at_time(yas, t), *me)
                elif it == "ashe":
                    paste(img, at_time(ashe, t), *foe)
                else:
                    paste(img, at_time(plumes[it], t), *sc["pl"][it])
            paste(img, at_time(cast, t, loop=False), *me)
            for j, s0 in enumerate(SHOTS):
                dist = np.linalg.norm(me - foe)
                run = (t - s0) * 60 * SPEED
                if t < s0 or run >= dist:
                    continue
                dv = (me - foe) / dist
                pos, prev = foe + dv * run, foe + dv * max(0.0, run - 3 * SPEED)
                f = Image.fromarray(np.ascontiguousarray(at_time(arrow, t)))
                f = f.rotate(math.degrees(math.atan2(-dv[1], dv[0])), expand=True, resample=Image.NEAREST)
                paste(img, np.asarray(f), *pos)
                if up and j not in sc["blocks"]:
                    c = cross(prev, pos, sc["line"])
                    if c is not None:
                        sc["blocks"][j] = (t, c)
            for tb, c in sc["blocks"].values():
                paste(img, at_time(block, t - tb, loop=False), *c)
            if not up:
                for p in sc["pl"][1::2]:
                    paste(img, at_time(fade, t - LIFE, loop=False), *p)
            ImageDraw.Draw(img).text((8, 6), sc["label"], fill=(255, 255, 255, 255), font=font)
            row.append(img)
        fr = Image.new("RGB", (W * Z * 2 + 8, H * Z), (40, 44, 36))
        fr.paste(row[0].convert("RGB"), (0, 0))
        fr.paste(row[1].convert("RGB"), (W * Z + 8, 0))
        frames.append(fr)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    frames[0].save(a.out, save_all=True, append_images=frames[1:], duration=int(DT * 1000), loop=0)
    print(a.out, len(frames), frames[0].size, [len(s["blocks"]) for s in scenes])


if __name__ == "__main__":
    main()
