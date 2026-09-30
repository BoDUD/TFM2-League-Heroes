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
     the unit would stand at her heel;
  4. the blade and the hair (see BLADE): the idle's blade 2 squares back, clear of the hair; elsewhere a line of
     outline where they touch.
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
# the blade and the hair (the user: "皎月的武器和头发重叠了"; their pick of the variants: "待机 A2 + 其他 B"): both light,
# side by side down her back, they read as one mass. In the idle the blade (with its own outline) moves BLADE_BACK
# squares back, clear of the hair; in every other frame, where the blade is somewhere else each time and moving it
# would cut it, the hair squares touching it become outline.
BLADE = {(0xD0, 0xF6, 0xEE), (0x7B, 0xB2, 0xB9), (0x60, 0x63, 0x7E)}   # pale cyan, teal, steel
BLADE_LIGHT = {(0xD0, 0xF6, 0xEE), (0x7B, 0xB2, 0xB9)}
HAIR = {(0xF2, 0xE6, 0xCF), (0xC7, 0xB8, 0xA2), (0x55, 0x47, 0x43)}
LINE = {(0x0A, 0x04, 0x12), (0x0C, 0x05, 0x16)}
INK = (0x0A, 0x04, 0x12)
BLADE_BACK = 2
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


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


def blade_parts(f, least=5):
    """The blade's pieces: 4-connected runs of its colours holding one of its light ones, `least` squares or more."""
    h, w = f.shape[:2]
    seen = np.zeros((h, w), bool)
    parts = []
    for y, x in zip(*np.nonzero(f[..., 3] > 0)):
        if seen[y, x] or key(f[y, x]) not in BLADE:
            continue
        m = np.zeros((h, w), bool)
        m[y, x] = seen[y, x] = True
        todo, light = [(x, y)], False
        while todo:
            cx, cy = todo.pop()
            light |= key(f[cy, cx]) in BLADE_LIGHT
            for dx, dy in N4:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < w and 0 <= ny < h and not seen[ny, nx] and f[ny, nx, 3] and key(f[ny, nx]) in BLADE:
                    m[ny, nx] = seen[ny, nx] = True
                    todo.append((nx, ny))
        if light and m.sum() >= least:
            parts.append(m)
    return parts


def around(m):
    r = np.zeros_like(m)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            r |= np.roll(np.roll(m, dy, 0), dx, 1)
    return r


def line_between(f):
    """Hair squares 4-adjacent to the blade become outline; returns the frame and how many changed."""
    out, n = f.copy(), 0
    for m in blade_parts(f):
        for y, x in zip(*np.nonzero(around(m) & ~m)):
            if f[y, x, 3] and key(f[y, x]) in HAIR and any(
                    0 <= y + dy < f.shape[0] and 0 <= x + dx < f.shape[1] and m[y + dy, x + dx] for dx, dy in N4):
                out[y, x, :3] = INK
                n += 1
    return out, n


def move_blade(f, d=BLADE_BACK):
    """The biggest blade piece and its own outline d squares back (left), behind anything already there; the edges
    it uncovers get outline."""
    parts = blade_parts(f)
    if not parts:
        return f
    m = max(parts, key=lambda p: p.sum())
    h, w = m.shape
    op = f[..., 3] > 0
    own = np.zeros_like(m)                         # the outline round the blade...
    for y, x in zip(*np.nonzero(around(m) & ~m & op)):
        own[y, x] = key(f[y, x]) in LINE
    for y, x in zip(*np.nonzero(own)):             # ...but not where it also outlines the hair or the body
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w and op[ny, nx] and not m[ny, nx] and not own[ny, nx] \
                        and key(f[ny, nx]) not in LINE:
                    own[y, x] = False
    part = m | own
    assert not part[:, :d].any(), "no room to move the blade back"
    out = f.copy()
    out[part] = 0
    for y, x in zip(*np.nonzero(part)):
        if not out[y, x - d, 3]:
            out[y, x - d] = f[y, x]
    zone = around(around(part | np.roll(part, -d, 1)))
    op = out[..., 3] > 0
    ink = out.copy()
    for y, x in zip(*np.nonzero(zone & ~op)):
        for dx, dy in N4:
            ny, nx = y + dy, x + dx
            if 0 <= ny < f.shape[0] and 0 <= nx < f.shape[1] and op[ny, nx] and key(out[ny, nx]) not in LINE:
                ink[y, x] = (*INK, 255)
                break
    return ink


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
                f, n = line_between(f)
                if n:
                    notes[-1] += f" line{n}"
            else:
                f = move_blade(f)
                notes.append(f"{k + 1}:blade back {BLADE_BACK}")
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
