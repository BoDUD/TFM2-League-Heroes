#!/usr/bin/env python3
"""Bigger, clearer basic-attack projectiles for league_kaisa and league_kogmaw, drawn square by square.

    python tools/art/fx_attack_bolts.py [--preview OUT.png]

The user, 2026-10-13: 「卡莎和大嘴平A看起来不是很明显 加强一下弹道模型？」. Kai'Sa's bolt was 11 x 5 squares, Kog'Maw's glob
7 x 3 - half of league_ashe's arrow (23 x 7), lost next to 40-square heroes. Both redrawn in their own colours at the
pack's effect style (saturated, no outline, 1 square = 1 game pixel), facing right, the same above and below the middle
row (a projectile is turned with its flight: shot to the left it is mirrored top to bottom - the skill's "Both sides"
rule), every frame odd-sized round its centre. The tags keep their frame count and timing (league_kaisa_fx `bolt`, 18
frames, not repeating, its first 1 x 1 frame the spawn delay; league_kogmaw_fx `a_glob`, 8 frames, repeating).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import ppu_hd as P  # noqa: E402
import strips as G  # noqa: E402

FX = os.path.join(ROOT, "league", "effects")

# Kai'Sa: Void violet (her old bolt's colours, one step brighter at the core)
K_CORE = (255, 236, 255)
K_HOT = (255, 150, 250)
K_MAG = (236, 64, 236)
K_PUR = (168, 48, 214)
K_DEEP = (112, 30, 170)
# Kog'Maw: caustic green (his glob's greens, a yellow highlight)
G_HI = (246, 255, 190)
G_LIGHT = (196, 242, 74)
G_MID = (130, 208, 40)
G_DARK = (74, 144, 22)
G_DEEP = (44, 96, 14)


def mirror_rows(top, h):
    """A full frame from its rows above and on the middle one (h odd): the lower half the upper turned over."""
    half = (h + 1) // 2
    out = np.zeros((h, top.shape[1], 4), np.uint8)
    out[:half] = top[:half]
    out[half:] = top[:half - 1][::-1]
    return out


def put(img, x, y, c):
    if 0 <= y < img.shape[0] and 0 <= x < img.shape[1]:
        img[y, x] = (*c, 255)


def kaisa_frame(phase):
    """19 x 9: a plasma dart - white-pink core, magenta body, violet glow tapering into a tail; 4 phases of the tail's
    sparks."""
    W, H = 19, 9
    m = H // 2                                   # the middle row
    a = np.zeros((H, W, 4), np.uint8)
    hx = 14.0                                    # the head's centre
    for y in range(m + 1):
        for x in range(W):
            dy = m - y
            # the head: nested ellipses
            e = ((x - hx) / 4.2) ** 2 + (dy / 3.6) ** 2
            if e <= 0.18:
                put(a, x, y, K_CORE)
            elif e <= 0.42:
                put(a, x, y, K_HOT)
            elif e <= 0.75:
                put(a, x, y, K_MAG)
            elif e <= 1.0:
                put(a, x, y, K_PUR)
            # the body / tail: a streak along the middle getting thinner backwards
            elif x < hx:
                t = (hx - x) / hx                   # 0 at the head, 1 at the tail's end
                half = 2.4 * (1 - t) ** 1.2
                if dy <= half - 1.4:
                    put(a, x, y, K_HOT if t < 0.35 else K_MAG)
                elif dy <= half - 0.4:
                    put(a, x, y, K_MAG if t < 0.5 else K_PUR)
                elif dy <= half + 0.4 and t < 0.85:
                    put(a, x, y, K_PUR if t < 0.6 else K_DEEP)
    # the core line through the body
    for x in range(7, 14):
        put(a, x, m, K_CORE if x >= 10 else K_HOT)
    # sparks off the tail, moving back phase by phase
    for sx, sy in ((5 - phase, 1), (2 - phase % 2, 2), (8 - phase, 0)):
        put(a, sx % W if sx >= 0 else sx + 4, sy + 1, K_PUR if sy else K_HOT)
    return mirror_rows(a, H)


def kogmaw_frame(phase):
    """17 x 11: an acid glob - a round green ball, a pale highlight at its front, two drops trailing; the ball wobbles
    and the drops fall back over 4 phases."""
    W, H = 17, 11
    m = H // 2
    a = np.zeros((H, W, 4), np.uint8)
    cx = 11.5
    ry = (4.9, 4.6, 4.9, 5.2)[phase % 4]
    rx = (5.1, 5.4, 5.1, 4.8)[phase % 4]
    for y in range(m + 1):
        for x in range(W):
            dy = m - y
            e = ((x - cx) / rx) ** 2 + (dy / ry) ** 2
            if e <= 1.0:
                c = G_DARK if e > 0.78 else (G_MID if e > 0.45 else G_LIGHT)
                put(a, x, y, c)
    # the highlight towards the front, on the middle row and the one above
    for x, y in ((int(cx) + 1, m), (int(cx) + 2, m), (int(cx) + 3, m), (int(cx) + 1, m - 1), (int(cx) + 2, m - 1)):
        put(a, x, y, G_HI)
    # the drops behind, falling back
    d1 = 4 - phase % 2
    put(a, d1, m, G_MID)
    put(a, d1 + 1, m, G_LIGHT)
    put(a, d1 + 1, m - 1, G_MID)
    put(a, d1, m - 1, G_DARK)
    d2 = 1 - (phase // 2) % 2
    put(a, d2, m, G_MID)
    return mirror_rows(a, H)


def kaisa_frames(old):
    """old: [(frame, ms)] - the first (the 1 x 1 spawn delay) kept, the rest the dart in 4 phases."""
    out = [old[0]]
    for i, (_, ms) in enumerate(old[1:]):
        out.append((kaisa_frame(i % 4), ms))
    return out


def kogmaw_frames(old):
    out = []
    for i, (f, ms) in enumerate(old):
        if i == 0 and f.shape[0] * f.shape[1] <= 16:
            # the first, a small spawn frame: the ball alone, smaller
            g = kogmaw_frame(0)
            small = np.zeros((7, 7, 4), np.uint8)
            small[:, :] = g[2:9, 8:15]
            out.append((small, ms))
            continue
        out.append((kogmaw_frame(i % 4), ms))
    return out


TARGETS = [("league_kaisa_fx", "bolt", kaisa_frames), ("league_kogmaw_fx", "a_glob", kogmaw_frames)]


def preview(path, Z=6):
    rows = []
    for stem, tag, make in TARGETS:
        sheet = P.read_sheet(os.path.join(FX, stem))
        old = sheet[tag]
        new = make(old)
        hero = "kaisa" if "kaisa" in stem else "kogmaw"
        body = P.read_sheet(os.path.join(ROOT, "league", "champions", f"league_{hero}"))
        idle = body["hd_idle"][0][0] if "hd_idle" in body else body["idle"][0][0]
        k = P.PPU.get(hero, 1) if "hd_idle" in body else 1
        hb = Image.fromarray(idle)
        hb = hb.resize((max(1, round(hb.width * Z / k)), max(1, round(hb.height * Z / k))),
                       Image.NEAREST if Z / k >= 1 else Image.BOX)
        cells = [("hero", hb)]
        for lab, fr in (("old", old), ("new", new)):
            for j in (1, 2, 3):
                f = fr[min(j, len(fr) - 1)][0]
                cells.append((f"{lab}{j}", Image.fromarray(f).resize((f.shape[1] * Z, f.shape[0] * Z), Image.NEAREST)))
        cw = max(i.width for _, i in cells)
        ch = max(i.height for _, i in cells)
        im = Image.new("RGB", (len(cells) * (cw + 10) + 10, ch + 24), (88, 104, 88))
        d = ImageDraw.Draw(im)
        x = 10
        for n, c in cells:
            im.paste(c, (x, 4 + (ch - c.height) // 2 if n != "hero" else 4 + ch - c.height), c)
            d.text((x, ch + 8), n, fill=(255, 255, 255))
            x += cw + 10
        rows.append(im)
    W = max(r.width for r in rows)
    can = Image.new("RGB", (W, sum(r.height for r in rows)), (60, 70, 60))
    y = 0
    for r in rows:
        can.paste(r, (0, y))
        y += r.height
    can.save(path)
    print(path, can.size)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--preview", help="write a before / after sheet here and change nothing")
    a = ap.parse_args()
    if a.preview:
        preview(a.preview)
        return
    for stem, tag, make in TARGETS:
        path = os.path.join(FX, stem)
        sheet = P.read_sheet(path)
        sheet[tag] = make(sheet[tag])
        w, h = G.write_sheet(path, sheet)
        print(f"league/effects/{stem}#sheet.png {w}x{h}: {tag} redrawn ({len(sheet[tag])} frames)")


if __name__ == "__main__":
    main()
