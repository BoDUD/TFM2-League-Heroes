#!/usr/bin/env python3
"""Kog'Maw's void form (Icathian Surprise) as a unit of its own: league/champions/league_kogmaw_void#sheet.png + #anim.fanim,
his own frames recoloured by code into a void creature (2026-11-14, the user after a GIF of the old comet: 「大嘴死了还是看不到
炸人啊」 then 「按英雄联盟改」 - in League his body itself turns into a glowing void creature for 4 s that runs at the
nearest enemy and bursts).

    python -I tools/art/unit_kogmaw_void.py [--check] [--review <dir>]

The add-on league_kogmaw spawns the form through the mod API's spawn_unit under this name; the game draws a unit of a name
from asset/base/aseprite_resources/champions/<name> (the add-on's mod.override_info sends that here) with the tags the
engine's own summons play: idle, run, attack, hit and dead. league.dll registers the sheet (addons/league_main/src/hd.rs
HEROES, his own PPU 1.794): each tag's hd_ twin is drawn on the battlefield; without the DLL the 1x frames, the same size.

Nothing is drawn anew and nothing moves: every frame is one of his own (league/champions/league_kogmaw, 1x and hd_), cut
as it is, so the form is exactly his size in every frame (「模型不要变大变小」) and both densities stay the same drawing. Only
the colours change, by what each of his colours is:
  - his outline: the silhouette's outer ring (1 square at 1x, 2 dense squares - one game pixel at his 1.794) turns a light
    pink-lavender (EDGE) so the form reads at a glance on the grass and in a fight; the dark line inside it stays dark (INK);
  - his blue hide and teal belly: deep purple (BODY) by brightness; his bone skull and spines a lighter violet (SKIN), so
    his face stays readable;
  - what glows: the cyan crest and the bright blue rims violet (VIO), the mouth, eyes and lip magenta to white-hot (MAG).
  idle    4 frames of his still pose (idle_base): the glow pulses and the outline shimmers, the body does not move
          (「上下摆动全不要了啊」);
  run     his 8 run frames, the glow beating every other frame;
  attack  his 6 attack frames (the form never attacks: the add-on gives it none);
  hit     his 2 hit frames, glowing harder;
  dead    the still pose dissolving into violet sparks over 5 frames, then an empty one (the form normally bursts and is
          banished before its time runs out: this plays only if something ends it otherwise).
--check: exit 1 when the sheet in the repo is not what this writes. --review: contact sheets of every frame (1x and dense
at 3x), the form beside him (same size), at game scale.
"""
import argparse
import colorsys
import json
import os
import sys
import tempfile

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unit_draw as U  # noqa: E402

NAME = "league_kogmaw_void"
OUT_STEM = os.path.join(U.CHAMPIONS, NAME)
SRC_STEM = os.path.join(U.CHAMPIONS, "league_kogmaw")
PPU = 1.794                      # his own (hd.rs HEROES): the dense frames are his hd_ frames
G = U.G

INK = (14, 3, 30)
EDGE = [(244, 190, 255), (255, 226, 255)]
BODY = [(20, 5, 42), (34, 10, 70), (54, 18, 104), (78, 30, 142), (104, 46, 178)]
SKIN = [(58, 20, 104), (86, 34, 144), (118, 58, 184), (154, 94, 218), (194, 142, 244)]
MAG = [(84, 6, 66), (150, 18, 116), (222, 46, 172), (255, 112, 214), (255, 206, 246), (255, 242, 255)]
VIO = [(96, 36, 182), (142, 74, 236), (188, 122, 255), (224, 180, 255), (248, 232, 255)]

IDLE_MS = (180, 160, 180, 160)
IDLE_GLOW = (0, 1, 2, 1)
DEAD_MS = (80, 80, 80, 80, 90, 120)


def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def kind(c):
    """what one of his colours is: ink (his outline and dark lines), spike (the cyan crest), rim (the bright blue edges),
    mouth, eye, lip (the yellow-green line round the mouth), body (the blue hide, the teal belly) or skin (bone)"""
    h, s, v = colorsys.rgb_to_hsv(c[0] / 255, c[1] / 255, c[2] / 255)
    h *= 360
    if v < 0.2:
        return "ink"
    if 165 <= h <= 215 and s > 0.6 and v >= 0.55:
        return "spike"
    if 215 < h <= 250 and s > 0.55 and v >= 0.85:
        return "rim"
    if (h >= 325 or h <= 8) and s > 0.75:
        return "mouth"
    if 10 <= h <= 30 and s > 0.9:
        return "eye"
    if 38 <= h <= 62 and s > 0.6:
        return "lip"
    if 150 <= h <= 290:
        return "body"
    return "skin"


def band(level, cuts):
    return sum(level >= c for c in cuts)


def void_colour(c, glow):
    """his colour `c` in the void form; `glow` 0..2 brightens what glows"""
    k, L = kind(c), lum(c)
    if k == "ink":
        return INK
    if k == "spike":
        return VIO[min(4, 2 + band(L, (150, 200)) + glow)]
    if k == "rim":
        return VIO[min(4, band(L, (100, 125)) + glow)]
    if k == "mouth":
        return MAG[min(5, band(L, (28, 45, 70, 100)) + glow)]
    if k == "eye":
        return MAG[min(5, (4 if L > 100 else 3) + glow)]
    if k == "lip":
        return MAG[min(5, 1 + band(L, (70, 120, 170)) + glow)]
    if k == "body":
        return BODY[band(L, (40, 58, 80, 105))]
    return SKIN[band(L, (95, 125, 160, 205))]


def rings(alpha, depth):
    """the silhouette's outer `depth` rings of squares (4-neighbour)"""
    inside = alpha > 0
    out = np.zeros_like(inside)
    for _ in range(depth):
        e = U.edge4(inside)
        out |= e
        inside &= ~e
    return out


def recolour(f, dense, glow=0, edge=0):
    """one of his frames in the void form: same squares, same size; the outer ring light (two dense squares)"""
    out = f.copy()
    solid = f[..., 3] > 0
    cols, inv = np.unique(f[solid][:, :3], axis=0, return_inverse=True)
    mapped = np.array([void_colour(tuple(int(v) for v in c), glow) for c in cols], np.uint8)
    out[solid, :3] = mapped[inv.reshape(-1)]
    out[rings(f[..., 3], 2 if dense else 1), :3] = EDGE[edge]
    return out


def cells(f, dense):
    """every square's game pixel round the pivot (the frame's centre): (column, row) of whole game pixels"""
    h, w = f.shape[:2]
    s = PPU if dense else 1.0
    gx = (np.arange(w) + 0.5 - w / 2.0) / s
    gy = (np.arange(h) + 0.5 - h / 2.0) / s
    return np.meshgrid(np.floor(gx + 0.5).astype(int), np.floor(gy + 0.5).astype(int))


def dissolve(f, dense, k, n):
    """step k of n of the still pose dissolving: a game pixel goes when its own number (the same at both densities) is
    below k / n, the ones about to go flare violet"""
    cx, cy = cells(f, dense)
    t = np.modf(np.abs(np.sin(cx * 12.9898 + cy * 78.233) * 43758.5453))[0]
    out = recolour(f, dense, glow=1)
    gone = t < k / n
    flare = (t >= k / n) & (t < (k + 1) / n) & (f[..., 3] > 0)
    out[flare, :3] = VIO[4] if k % 2 else MAG[4]
    out[gone] = 0
    return out


def his_tags():
    px, an = U.read_sheet(SRC_STEM)
    out = {}
    for tag, a in an["anims"].items():
        fr = []
        for f in a["frames"]:
            d = f["data"]
            x, y, w, h = int(d["x"]), int(d["y"]), int(d["w"]), int(d["h"])
            fr.append((px[y:y + h, x:x + w].copy(), round(f["duration"] * 1000)))
        out[tag] = fr
    return out


def build():
    his = his_tags()
    tags = {}
    for pre in ("", "hd_"):
        dense = pre == "hd_"
        still = his[pre + "idle_base"][0][0]
        tags[pre + "idle"] = [(recolour(still, dense, glow=g, edge=k % 2), ms)
                              for k, (g, ms) in enumerate(zip(IDLE_GLOW, IDLE_MS))]
        tags[pre + "run"] = [(recolour(f, dense, glow=k % 2), ms) for k, (f, ms) in enumerate(his[pre + "run"])]
        tags[pre + "attack"] = [(recolour(f, dense, glow=1), ms) for f, ms in his[pre + "attack"]]
        tags[pre + "hit"] = [(recolour(f, dense, glow=2, edge=1), ms) for f, ms in his[pre + "hit"]]
        n = len(DEAD_MS) - 1
        dead = [(dissolve(still, dense, k, n), ms) for k, ms in zip(range(n), DEAD_MS)]
        empty = np.zeros((6, 6, 4) if dense else (3, 3, 4), np.uint8)
        tags[pre + "dead"] = dead + [(empty, DEAD_MS[-1])]
    order = ["idle", "run", "attack", "hit", "dead"]
    return {t: tags[t] for t in order + ["hd_" + t for t in order]}


def write(tags, check):
    if check:
        tmp = os.path.join(tempfile.mkdtemp(prefix="unit_"), NAME)
        G.write_sheet(tmp, tags, share=True)
        same = False
        if os.path.exists(G.lp(OUT_STEM + "#sheet.png")) and os.path.exists(G.lp(OUT_STEM + "#anim.fanim")):
            (a, b), (c, d) = U.read_sheet(OUT_STEM), U.read_sheet(tmp)
            same = b == d and a.shape == c.shape and bool((a == c).all())
        print(f"{NAME}:", "up to date" if same else "stale")
        sys.exit(0 if same else 1)
    w, h = G.write_sheet(OUT_STEM, tags, share=True)
    print("wrote %s#sheet.png (%d x %d) and #anim.fanim: %s" % (
        os.path.relpath(OUT_STEM, U.ROOT), w, h,
        ", ".join("%s %d frames %.2f s" % (t, len(fr), sum(ms for _, ms in fr) / 1000.0) for t, fr in tags.items())))


def sizes_text(tags):
    """every frame's size against his own: the form must be his size (the same squares)"""
    his = his_tags()
    src = {"idle": "idle_base", "run": "run", "attack": "attack", "hit": "hit"}
    lines, same = [], True
    for pre in ("", "hd_"):
        for t, s in src.items():
            mine = [f.shape[:2] for f, _ in tags[pre + t]]
            theirs = [f.shape[:2] for f, _ in his[pre + s]]
            if t == "idle":
                theirs = theirs[:1] * len(mine)
            ok = mine == theirs
            same &= ok
            lines.append("  %-10s %s %s" % (pre + t, "same as his" if ok else "DIFFERS", sorted(set(mine))))
    return "\n".join(lines), same


def review(tags, folder):
    """the contact sheet, every frame's size against his, and the form beside him at game scale (3x and 6x)"""
    os.makedirs(folder, exist_ok=True)
    print("review", U.contact(tags, 2, os.path.join(folder, "kogmaw_void_frames.png")))
    text, same = sizes_text(tags)
    print(text)
    if not same:
        sys.exit("the form is not his size in every frame")
    his = his_tags()
    figs = [("Kog'Maw 1x", his["idle_base"][0][0], 1.0),
            ("void 1x", tags["idle"][0][0], 1.0),
            ("Kog'Maw hd", his["hd_idle_base"][0][0], 1.0 / PPU),
            ("void hd", tags["hd_idle"][0][0], 1.0 / PPU),
            ("void hd glow", tags["hd_idle"][2][0], 1.0 / PPU),
            ("run 1", tags["hd_run"][1][0], 1.0 / PPU),
            ("run 4", tags["hd_run"][4][0], 1.0 / PPU),
            ("hit", tags["hd_hit"][0][0], 1.0 / PPU)]
    print("review", U.beside(figs, os.path.join(folder, "kogmaw_void_beside.png"), scale=3))
    print("review", U.beside(figs, os.path.join(folder, "kogmaw_void_beside_6x.png"), scale=6))
    # his own tags next to the form's, frame for frame, both densities at 3x (the dense ones at their game size)
    rows = []
    for pre, s in (("", 1.0), ("hd_", 1.0 / PPU)):
        for t, src in (("idle", "idle_base"), ("run", "run"), ("hit", "hit"), ("dead", "idle_base")):
            a = [f for f, _ in his[pre + src]][:len(tags[pre + t])]
            b = [f for f, _ in tags[pre + t]]
            rows.append(("%s%s: his / the form" % (pre, t), a, b, s))
    zoom = 3
    cell_w, cell_h = 56 * zoom, 56 * zoom          # game px a cell, at 3x: wider than any of his frames
    H = len(rows) * (2 * cell_h + 24) + 6
    W = 200 + max(max(len(a), len(b)) for _, a, b, _ in rows) * (cell_w + 6)
    img = Image.new("RGBA", (W, H), (74, 92, 70, 255))
    from PIL import ImageDraw
    dr = ImageDraw.Draw(img)
    y = 6
    for label, a, b, s in rows:
        dr.text((6, y + 4), label, fill=(255, 255, 0, 255))
        for line, fr in enumerate((a, b)):
            x = 200
            for f in fr:
                w = max(1, int(round(f.shape[1] * s * zoom)))
                h = max(1, int(round(f.shape[0] * s * zoom)))
                im = Image.fromarray(f, "RGBA").resize((w, h), Image.NEAREST)
                # centred on the cell's middle: the frame's centre is the pivot, as the game draws it
                img.alpha_composite(im, (x + (cell_w - w) // 2, y + line * cell_h + (cell_h - h) // 2))
                x += cell_w + 6
        y += 2 * cell_h + 24
    path = os.path.join(folder, "kogmaw_void_vs_his.png")
    img.save(path)
    print("review", path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review")
    a = ap.parse_args()
    tags = build()
    if a.review:
        review(tags, a.review)
    write(tags, a.check)


if __name__ == "__main__":
    main()
