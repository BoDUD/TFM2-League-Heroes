#!/usr/bin/env python3
"""Daisy as a unit of her own: league/champions/league_ivern_daisy#sheet.png + #anim.fanim.

    python tools/art/unit_ivern_daisy.py [--check] [--preview <png>]

The add-on league_ivern spawns Daisy through the mod API's spawn_unit under the name league_ivern_daisy; the game draws a
unit of that name from asset/base/aseprite_resources/champions/league_ivern_daisy (the add-on's mod.override_info sends
that here) with the tags a champion has. The engine's own summons (base `ghoul`) carry idle, run, attack, hit and dead;
league_ivern 0.3.0 plays `drop` too (an Animation CC as she is spawned). Each tag twice: the dense `hd_` frames at PPU
1.333 (57 game px from her sprout to her feet; league.dll hd.rs HEROES registers the sheet) and the 1x frames (a square a
game pixel) made from them by pixel_down.pixelate, for wherever the dense frames are off.

Since 2026-11-21 (the user: 「小菊做成召唤物的话 行走动作也没做 都要补」「起码像安妮的熊那样吧 方向也不对」) the frames are
Codex's 3/4 view facing right (assets/source/ivern/codex_side: 15 pictures from the approved front design, its 40
colours, read back on their 12 px grid to 104 x 104, 76 rows sprout to soles = the dense size) - like Tibbers, the game
flips them when she faces left. Before that she was the riding effects' front view (league_ivern_daisy_drop / _punch /
_bye), which never turned and whose run only lifted a shin two pixels.

  idle    the standing picture (0). No breath: her near fist rests on the ground, a row lower above the knees would
          squeeze it;
  run     the walk (1 step, 2 pass, 3 the other step, 4 pass), 0.12 s each;
  attack  the raised fist (5) 0.35 s, the punch (6) 0.2 s - the fist lands 0.35 s in (the add-on's unit attack: tick 21
          of 42) - and the standing picture (0) 0.15 s;
  hit     the guard (9);
  dead    the collapse (13) and the heap (14), the heap sinking a third and two thirds into the ground, an empty frame
          (base's dead tags end so);
  drop    falling (10, first 16 rows higher, then as drawn: her soles 20 rows up), landing (11) and standing (0): 0.9 s,
          the add-on's D_DROP.

Codex's frames share one body axis: column 48 (the standing picture's centre) is the pivot in every frame, their soles'
row 99 lands FEET rows under it (11 game px: 15 dense rows, the 1x frames 11). --check: exit 1 when the sheet in the repo
is not what this writes. --preview: the frames at 6x / 4.5x on their ground line.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import pixel_down as D  # noqa: E402

SIDE = os.path.join(ROOT, "assets", "source", "ivern", "codex_side", "pixel_1x", "daisy-side-")
OUT = os.path.join(ROOT, "league", "champions", "league_ivern_daisy")
D_PPU = 1.333               # her dense frames are this many pixels a game pixel
FEET = 11                   # a unit's soles: this many game px under the pivot
NAMES = ["0_design", "1_walk1", "2_walk2", "3_walk3", "4_walk4", "5_punch_up", "6_punch_down", "7_slam_up", "8_slam",
         "9_hit", "10_fall", "11_land", "12_wave", "13_slump", "14_crumble"]
AXIS, SOLES = 48, 99        # Codex's frames: the body axis column, the soles' row
RISE = 16                   # the first drop frame this many dense rows above the drawn fall
IDLE_MS, RUN_MS, HIT_MS = 640, 120, 100
ATTACK = [(5, 350), (6, 200), (0, 150)]
DROP_MS = [100, 150, 300, 350]


class Scale:
    """One of the two frame sizes: the 1x frames (tag `idle`) or the dense ones (`hd_idle`)."""

    def __init__(self, tag, ppu, canvas):
        self.tag, self.ppu, self.S = tag, ppu, canvas
        self.C = canvas // 2
        self.feet = int(round(FEET * ppu))


DENSE, ONE = Scale("hd_idle", D_PPU, 270), Scale("idle", 1, 200)


def side(n):
    """Codex's picture n on the dense canvas: its body axis on the pivot column, its soles' row FEET dense rows under it."""
    pic = np.array(Image.open(G.lp(SIDE + NAMES[n] + ".png")).convert("RGBA"))
    c = np.zeros((DENSE.S, DENSE.S, 4), np.uint8)
    top, left = DENSE.C + DENSE.feet - SOLES, DENSE.C - AXIS
    h, w = pic.shape[:2]
    c[top:top + h, left:left + w] = pic
    c[c[..., 3] == 0] = 0
    return c


def moved(f, dy):
    """The frame moved dy rows (down if positive)."""
    out = np.zeros_like(f)
    if dy >= 0:
        out[dy:] = f[:f.shape[0] - dy]
    else:
        out[:dy] = f[-dy:]
    return out


def sunk(f, frac):
    """The frame sinking `frac` of its height into the ground: moved down, nothing under the soles' line."""
    rows = np.nonzero(f[..., 3].any(1))[0]
    out = moved(f, int(round((rows.max() - rows.min() + 1) * frac)))
    out[DENSE.C + DENSE.feet + 1:] = 0
    return out


def one_of(f, outline):
    """The 1x frame of a dense one: pixel_down's squares of 1 / D_PPU dense pixels through the pivot, on the 1x canvas."""
    out = np.zeros((ONE.S, ONE.S, 4), np.uint8)
    if not f[..., 3].any():
        return out
    lo, (px, py) = D.pixelate(f, 1.0 / D_PPU, (DENSE.C, DENSE.C), outline)
    ox, oy = ONE.C - px, ONE.C - py
    ys, xs = np.nonzero(lo[..., 3] > 0)
    ok = (ys + oy >= 0) & (ys + oy < ONE.S) & (xs + ox >= 0) & (xs + ox < ONE.S)
    out[ys[ok] + oy, xs[ok] + ox] = lo[ys[ok], xs[ok]]
    return out


def build():
    pics = [side(n) for n in range(len(NAMES))]
    stand = pics[0]
    blank = np.zeros_like(stand)
    dense = {
        "idle": [(stand, IDLE_MS)],
        "run": [(pics[n], RUN_MS) for n in (1, 2, 3, 4)],
        "attack": [(pics[n], ms) for n, ms in ATTACK],
        "hit": [(pics[9], HIT_MS)],
        "dead": [(pics[13], 250), (pics[14], 250), (sunk(pics[14], 1 / 3), 100), (sunk(pics[14], 2 / 3), 100), (blank, 100)],
        "drop": list(zip([moved(pics[10], -RISE), pics[10], pics[11], stand], DROP_MS)),
    }
    outline = D.edge_colour(stand)
    tags = {}
    for t, frames in dense.items():
        tags[t] = [(one_of(f, outline), ms) for f, ms in frames]
    for t, frames in dense.items():
        tags["hd_" + t] = frames
    return tags, [ONE, DENSE]


def centred(tags, scales):
    out = {}
    for tag, frames in tags.items():
        sc = scales[1] if tag.startswith("hd_") else scales[0]
        out[tag] = [(G.centre_frame(f, -sc.C, -sc.C) if f[..., 3].any() else np.zeros((3, 3, 4), np.uint8), ms)
                    for f, ms in frames]
    return out


def preview(tags, scales, path):
    cells = [(tag, i, f) for tag, frames in tags.items() for i, (f, _) in enumerate(frames)]
    per_row = 6
    W, H = 6 * 80, 6 * 95 + 14
    rows = (len(cells) + per_row - 1) // per_row
    img = Image.new("RGBA", (per_row * W, rows * H), (58, 70, 58, 255))
    dr = ImageDraw.Draw(img)
    for n, (tag, i, f) in enumerate(cells):
        sc = scales[1] if tag.startswith("hd_") else scales[0]
        z = 6 / sc.ppu
        ox, oy = (n % per_row) * W, (n // per_row) * H + 14
        half_w, up, down = int(38 * sc.ppu), int(80 * sc.ppu), int(13 * sc.ppu)
        crop = Image.fromarray(f[sc.C - up:sc.C + down + 1, sc.C - half_w:sc.C + half_w + 1], "RGBA")
        img.alpha_composite(crop.resize((int(crop.width * z), int(crop.height * z)), Image.NEAREST), (ox, oy))
        gy = oy + int((up + sc.feet + 1) * z)
        dr.line([(ox, gy), (ox + W - 2, gy)], fill=(0, 255, 255, 255))
        dr.text((ox + 3, oy - 13), "%s %d" % (tag, i), fill=(255, 255, 0, 255))
    img.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--preview")
    a = ap.parse_args()
    tags, scales = build()
    if a.preview:
        preview(tags, scales, a.preview)
        print("preview", a.preview)
    out = centred(tags, scales)
    if a.check:
        import tempfile
        tmp = os.path.join(tempfile.mkdtemp(prefix="daisy_"), "league_ivern_daisy")
        G.write_sheet(tmp, out)

        def read(stem):
            with open(G.lp(stem + "#anim.fanim"), encoding="utf-8-sig") as fh:
                return np.array(Image.open(G.lp(stem + "#sheet.png")).convert("RGBA")), json.load(fh)

        same = False
        if os.path.exists(G.lp(OUT + "#sheet.png")) and os.path.exists(G.lp(OUT + "#anim.fanim")):
            (px, an), (px2, an2) = read(OUT), read(tmp)
            same = an == an2 and px.shape == px2.shape and bool((px == px2).all())
        print("league_ivern_daisy:", "up to date" if same else "stale")
        sys.exit(0 if same else 1)
    w, h = G.write_sheet(OUT, out)
    print("wrote %s#sheet.png (%d x %d) and #anim.fanim: %s" % (
        os.path.relpath(OUT, ROOT), w, h, ", ".join("%s %d frames %.2f s" % (t, len(fr), sum(ms for _, ms in fr) / 1000.0)
                                                    for t, fr in out.items())))


if __name__ == "__main__":
    main()
