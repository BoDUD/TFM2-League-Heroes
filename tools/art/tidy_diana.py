#!/usr/bin/env python3
"""Diana's strips from Codex's delivery (assets/source/diana/MODEL_STRIPS.md) into assets/source/native/.

    python tools/art/tidy_diana.py assets/source/diana/codex_strips --run assets/source/diana/codex_run
                                   [--tags run,attack,...] [--check]

The delivery (diana_animation_candidates.zip, kept in codex_strips/: native/diana_<tag>_1x.png in 96x96 cells,
manifest.json with an eye_mark per frame, the pack's diana_cells.json) is already on the grid and in the design's 26
colours; Codex drew every frame whole - no head paste, no erase round the head, as the pack asked. What it could not
keep is the face: its eyes change size and place from frame to frame (one eye, two, a heavy brow). Per frame:
  1. face: the design's face - the moon disc, the lashes, both eyes, the cheeks (FACE_ROWS x FACE_COLS of the idle
     cell, 6x7 squares) - goes where Codex's own face is: searched within 3 squares of the manifest's eye mark,
     scored by the design's eye squares falling on Codex's eye squares and its skin on skin; only over opaque squares,
     so the silhouette never grows. Frames whose face is turned away or lying (NO_FACE) keep Codex's. Then any
     eye-coloured square left outside the pasted face takes the skin colour (the eye colours stay the eyes' own);
  2. feet: Codex placed frames by an eye anchor and the run floated 2-4 rows: a frame that should stand (not in
     AIRBORNE) moves down until its lowest square is on the soles row (pivot + 11);
  3. place: the cells' pivots move 9 squares left - the design's feet stand 9 squares left of the pivot the pack's
     idle strip was laid on (its blade on the left pulled it across the League silhouette, as with Vayne), so in game
     the unit would stand at her heel.
The run came back a second time (diana_run_redo.zip, kept in codex_run/; the prompt:
assets/source/diana/RUN_REDO.md): Codex's first run had the same legs in all 8 frames; the redo swaps the planted
leg (near in 1-4, far in 5-8, strides opposite in 4 and 8) with the hips up kept square for square and the soles on
the ground. --run takes the run from it (its flat manifest).
Writes assets/source/native/diana_<tag>.png (8x blocks) and diana_cells.json; the idle strip is the design's.
--check compares with the files there instead of writing.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "native")
Z = 8
SOLES = 11
SHIFT = -9                                   # pivot x: the design's feet middle in the idle cell (41 against 50)
EYES = {(0xF9, 0xF7, 0xFB), (0x72, 0x11, 0xB0), (0xA9, 0x50, 0xD9)}
SKIN = (0xF2, 0xBA, 0x94)
SKINS = {SKIN, (0x86, 0x57, 0x44)}
FACE_ROWS, FACE_COLS = range(45, 52), range(40, 46)     # the design's face in the idle cell (pivot 50, 68)
IDLE_EYE = (40, 48)                                     # its eye mark there (the near eye's white)
NO_FACE = {("dead", k) for k in range(2, 8)}            # 0-based frames lying down or turned away
AIRBORNE = {("skill2", 1), ("skill2", 2), ("skill2", 3), ("skill2_w", 1), ("skill2_w", 2), ("skill2_w", 3),
            ("skill2_w", 4), ("ult", 1), ("ult", 2)}
LYING = {("dead", k) for k in range(3, 8)}              # may stay up to 2 rows under the soles row


def lp(p):
    p = os.path.abspath(p)
    return p if p.startswith(chr(92) * 2) else chr(92) * 2 + "?" + chr(92) + p


def key(c):
    return tuple(int(v) for v in c[:3])


def face_patch(idle):
    return idle[FACE_ROWS.start:FACE_ROWS.stop, FACE_COLS.start:FACE_COLS.stop].copy()


def paste_face(f, patch, mark):
    """Best spot within 3 squares of the eye mark; (score, ox, oy) and the frame with the face pasted."""
    ph, pw = patch.shape[:2]
    oy0, ox0 = mark[1] - (IDLE_EYE[1] - FACE_ROWS.start), mark[0] - (IDLE_EYE[0] - FACE_COLS.start)
    pk = [[key(patch[y, x]) if patch[y, x, 3] else None for x in range(pw)] for y in range(ph)]
    best = None
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            y0, x0 = oy0 + dy, ox0 + dx
            if y0 < 0 or x0 < 0 or y0 + ph > f.shape[0] or x0 + pw > f.shape[1]:
                continue
            s = 0
            for y in range(ph):
                for x in range(pw):
                    c = pk[y][x]
                    if c is None or not f[y0 + y, x0 + x, 3]:
                        continue
                    g = key(f[y0 + y, x0 + x])
                    if c in EYES and g in EYES:
                        s += 3
                    elif c in SKINS and g in SKINS:
                        s += 1
            if best is None or s > best[0]:
                best = (s, x0, y0)
    s, x0, y0 = best
    out = f.copy()
    for y in range(ph):
        for x in range(pw):
            if patch[y, x, 3] and out[y0 + y, x0 + x, 3]:
                out[y0 + y, x0 + x] = patch[y, x]
    # eye colours outside the pasted face become skin
    m = np.zeros(out.shape[:2], bool)
    m[y0:y0 + ph, x0:x0 + pw] = True
    for y, x in zip(*np.nonzero(out[..., 3] > 0)):
        if not m[y, x] and key(out[y, x]) in EYES:
            out[y, x, :3] = SKIN
    return s, x0 - ox0, y0 - oy0, out


def ground(f, py):
    ys = np.nonzero(f[..., 3].any(1))[0]
    n = py + SOLES - ys.max()
    if n <= 0:
        return f, 0
    out = np.zeros_like(f)
    out[n:] = f[:-n]
    return out, n


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("delivery")
    ap.add_argument("--run", help="the run redo delivery (its native/diana_run_1x.png and manifest.json)")
    ap.add_argument("--tags", default="run,attack,attack_p,skill,skill2,skill2_w,ult,hit,dead")
    ap.add_argument("--check", action="store_true")
    o = ap.parse_args()
    man = json.load(open(lp(os.path.join(o.delivery, "manifest.json")), encoding="utf-8"))
    cells = json.load(open(lp(os.path.join(o.delivery, "diana_cells.json")), encoding="utf-8"))
    cw, ch = cells["cell"]
    idle = np.asarray(Image.open(lp(os.path.join(o.delivery, "native", "diana_idle_1x.png"))).convert("RGBA")).copy()
    patch = face_patch(idle[:ch, :cw])
    tags = ["idle"] + o.tags.split(",")
    same = True
    for tag in tags:
        root, an = o.delivery, man["animations"][tag]
        if tag == "run" and o.run:
            root, an = o.run, json.load(open(lp(os.path.join(o.run, "manifest.json")), encoding="utf-8"))
        strip = np.asarray(Image.open(lp(os.path.join(root, an["native_file"]))).convert("RGBA")).copy()
        strip[strip[..., 3] < 128] = 0
        strip[strip[..., 3] > 0, 3] = 255
        cols = strip.shape[1] // cw
        notes = []
        for k, fr in enumerate(an["frames"]):
            x0, y0 = (k % cols) * cw, (k // cols) * ch
            f = strip[y0:y0 + ch, x0:x0 + cw]
            if tag != "idle":
                if (tag, k) not in NO_FACE and fr.get("eye_mark"):
                    s, dx, dy, f = paste_face(f, patch, fr["eye_mark"])
                    notes.append(f"{k + 1}:face{s}({dx:+d},{dy:+d})")
                else:
                    notes.append(f"{k + 1}:own face")
                if (tag, k) not in AIRBORNE and (tag, k) not in LYING:
                    f, n = ground(f, fr["pivot"][1])
                    if n:
                        notes[-1] += f" down{n}"
            strip[y0:y0 + ch, x0:x0 + cw] = f
        big = np.repeat(np.repeat(strip, Z, 0), Z, 1)
        out = os.path.join(SRC, f"diana_{tag}.png")
        if o.check:
            now = np.asarray(Image.open(lp(out)).convert("RGBA"))
            same &= now.shape == big.shape and bool((now == big).all())
        else:
            Image.fromarray(big).save(lp(out))
        print(tag.ljust(9), " ".join(notes))
    for tag, rows in cells["tags"].items():
        for r in rows:
            r["pivot"][0] += SHIFT
            if "head" in r:
                r["head"][0] += SHIFT
    text = json.dumps(cells, indent=1)
    path = os.path.join(SRC, "diana_cells.json")
    if o.check:
        with open(lp(path), encoding="utf-8") as f:
            same &= f.read() == text
        print("same as the committed files:", same)
    else:
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)


if __name__ == "__main__":
    main()
