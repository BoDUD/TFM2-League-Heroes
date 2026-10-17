#!/usr/bin/env python3
"""Vi's action strips from Codex's v4 frames (assets/source/vi/STRIPS_V4.md), read onto the design's grid.

    python tools/art/strips_vi.py [--src FRAMES_DIR] [--out assets/source/native] [--review PNG] [--no-head]

Codex drew every action frame as its own 1254 px picture like the approved master (the same size and placement:
the soles on the master's ground line, the standing point on its column), so each frame is read exactly like the
design (tools/art/design_vi.py grid(), tools/art/shrink_vi.py): every canvas square reads the source block it covers,
snapped to the master's palette; specks merged; the outline closed. Then the design's head (rows 60-70, columns 52-69
of the canvas: the goggles to the chin, the hair falling behind the neck; her approved eyes) is pasted where the frame's
own head matches it best (exact-colour share over the head, offsets within 20 squares), if at least HEAD_SURE of it
matches: every upright frame wears the same face (Codex's heads at its own size came out squinting, like the first
shrink of the master); the frame's own hair and skin squares within 2 squares round the pasted head are cleared (no
halo), then the outline closed again. The idle is the design six times (import_native ORDER/BOB breathe it).
Writes OUT/vi_<tag>.png (8x, 96 x 88 cells, native_refs.layout) and OUT/vi_cells.json (the pivot (48, 64) in every
cell = canvas (64, 88); the durations of STRIPS_V4.md).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_vi as D  # noqa: E402
import shrink_vi as S  # noqa: E402
import strips as G  # noqa: E402
from native_refs import layout  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "vi", "codex_strips_v4", "frames")
OUT = os.path.join(ROOT, "assets", "source", "native")
CELL = (96, 88)
PIVOT = (48, 64)                          # in the cell; the canvas's (64, 88)
OFF = (64 - PIVOT[0], 88 - PIVOT[1])      # canvas = cell + OFF
TIMES = {"idle": [200] * 6, "run": [105] * 8, "attack": [60, 60, 70, 70, 70, 70],
         "attack_e": [60, 60, 50, 80, 80, 70], "skill": [125] * 4, "skill_dash": [90, 90, 87], "ult": [66, 67],
         "ult_dash": [125] * 6, "ult_slam": [60, 70, 70, 70, 63], "hit": [100, 100],
         "dead": [100, 100, 110, 120, 130, 150, 200, 500]}
HEAD_BOX = (60, 71, 52, 70)               # rows 60-70, columns 52-69 of the design canvas
HEAD_SURE = 0.55
HAIR = {"FB5D99", "E22467"}
SKIN = {"FCC9A2", "DA9666"}
# a head's own squares: hair, skin, the hair's browns, the dark lines, the eyes (gold and steel stay: gauntlets come
# close to her head)
HEAD_STUFF = HAIR | SKIN | {"47241A", "643826", "200C05", "1F1E2F", "2C1E3F", "2A272C", "005DE7", "007CFC", "0067F8",
                            "006CFB", "FBF2E6", "F4E9DA"}
FACE_STUFF = SKIN | {"005DE7", "007CFC", "0067F8", "006CFB", "FBF2E6", "F4E9DA"}
# her own heads stay: the death bows and slumps the head (an upright face pasted there would stare out of a heap)
OWN_HEAD = {"dead"}
FLIGHT = {"run", "ult_dash"}              # strides that may leave the ground


def lp(path):
    return D.lp(path)


def design_canvas():
    canvas, _ = D.build()
    return canvas


def head_sprite(design):
    y0, y1, x0, x1 = HEAD_BOX
    h = design[y0:y1, x0:x1].copy()
    return h, (x0, y0)


def read_frame(src, g, flight=False):
    """One frame on the 128 x 128 canvas. Codex's soles land within half a square of the ground line in most frames;
    a frame more than half a square below it moves up by whole squares (its lowest row would be cut at row 99: run 4,
    R charge 4, R slam 4, death 6), one more than half a square above it moves down onto it - unless `flight` (a run
    or the R charge may leave the ground)."""
    left0, bottom, px_col, px_row, cols, pal = g
    ys = np.nonzero((src[..., 3] > 128).any(1))[0]
    if len(ys):
        rows = int(round((ys.max() + 1 - bottom) / px_row))
        if rows > 0 or (rows < 0 and not flight):
            bottom += rows * px_row
    fig, feat = S.read_blocks(src, left0, bottom, px_col, px_row, 128, 100, cols, pal)
    fig = S.despeckle(fig, feat)
    canvas = np.zeros((128, 128, 4), np.uint8)
    canvas[:100] = fig
    canvas, _, _ = G.complete_outline(canvas, feet=99)
    return canvas


def classes(img):
    """Hair 1, skin 2, anything else drawn 3, clear 0: what locates a head drawn a little differently."""
    out = np.zeros(img.shape[:2], np.int8)
    for y, x in zip(*np.nonzero(img[..., 3])):
        h = S.hexs(img[y, x])
        out[y, x] = 1 if h in HAIR else 2 if h in SKIN else 3
    return out


def paste_head(canvas, head, at, reach=20):
    """The design's head where the frame's own head is: the offset whose hair and skin squares agree most with the
    design head's (Codex's heads are the same head drawn again, a square off here and there, so exact colours
    matched 0.2-0.6 where hair and skin match 0.6-0.9). Returns (canvas, share matched, (dx, dy) or None)."""
    m = head[..., 3] > 0
    hc = classes(head)
    key = m & (hc < 3)
    cc = classes(canvas)
    hh, hw = head.shape[:2]
    best = (0.0, 0, 0)
    for dy in range(-reach - 10, reach + 1):
        for dx in range(-reach, reach + 1):
            y, x = at[1] + dy, at[0] + dx
            if y < 0 or x < 0 or y + hh > canvas.shape[0] or x + hw > canvas.shape[1]:
                continue
            s = ((cc[y:y + hh, x:x + hw] == hc) & key).sum() / key.sum()
            if s > best[0]:
                best = (s, dx, dy)
    s, dx, dy = best
    if s < HEAD_SURE:
        return canvas, s, None
    out = canvas.copy()
    y, x = at[1] + dy, at[0] + dx
    placed = np.zeros(canvas.shape[:2], bool)
    placed[y:y + hh, x:x + hw] = m
    # her own head goes first: its hair, skin, eyes and their dark lines within 2 squares of the design head, over the
    # chin's row (Codex drew it a few squares off: its edge was left as dark specks and strands beside the face)
    near = placed.copy()
    for _ in range(2):
        g = near.copy()
        g[1:] |= near[:-1]
        g[:-1] |= near[1:]
        g[:, 1:] |= near[:, :-1]
        g[:, :-1] |= near[:, 1:]
        near = g
    near[y + hh - 1:] = False
    # on the face's side (she faces right) all of it; behind the head only the skin and eyes - the hair she trails
    # in a dash stays whole (cut at 2 squares it hung in broken strands)
    face_side = x + hw // 2
    for yy, xx in zip(*np.nonzero(near & (out[..., 3] > 0))):
        h = S.hexs(out[yy, xx])
        if h in HEAD_STUFF and (xx >= face_side or h in FACE_STUFF):
            out[yy, xx] = 0
    region = out[y:y + hh, x:x + hw]
    region[m] = head[m]
    out, _, _ = G.complete_outline(out, feet=99)
    return specks(out), s, (dx, dy)


def specks(c, limit=8):
    """Pieces of fewer than `limit` squares apart from her go."""
    m = c[..., 3] > 0
    seen = np.zeros(m.shape, bool)
    pieces = []
    for y, x in zip(*np.nonzero(m)):
        if seen[y, x]:
            continue
        st, pts = [(y, x)], []
        seen[y, x] = True
        while st:
            cy, cx = st.pop()
            pts.append((cy, cx))
            for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                if 0 <= ny < m.shape[0] and 0 <= nx < m.shape[1] and m[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    st.append((ny, nx))
        pieces.append(pts)
    pieces.sort(key=len, reverse=True)
    out = c.copy()
    for p in pieces[1:]:
        if len(p) < limit:
            for y, x in p:
                out[y, x] = 0
    return out


def to_cell(canvas):
    return canvas[OFF[1]:OFF[1] + CELL[1], OFF[0]:OFF[0] + CELL[0]]


def strip(cells):
    cols, rows = layout(len(cells))
    out = np.zeros((rows * CELL[1], cols * CELL[0], 4), np.uint8)
    for k, c in enumerate(cells):
        r, cc = divmod(k, cols)
        out[r * CELL[1]:(r + 1) * CELL[1], cc * CELL[0]:(cc + 1) * CELL[0]] = c
    return np.repeat(np.repeat(out, 8, 0), 8, 1)


def build(src_dir, paste=True):
    """{tag: [canvas]} and a report {tag: [(head share, offset)]}."""
    design = design_canvas()
    g = D.grid()
    head, at = head_sprite(design)
    out, report = {"idle": [design.copy() for _ in TIMES["idle"]]}, {}
    for tag, ms in TIMES.items():
        if tag == "idle":
            continue
        frames, rep = [], []
        for k in range(1, len(ms) + 1):
            src = np.asarray(Image.open(lp(os.path.join(src_dir, f"vi_{tag}_{k}.png"))).convert("RGBA"))
            c = read_frame(src, g, flight=tag in FLIGHT)
            if paste and tag not in OWN_HEAD:
                c, s, off = paste_head(c, head, at)
                rep.append((round(s, 2), off))
            frames.append(c)
        out[tag], report[tag] = frames, rep
    return out, report


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", default=SRC)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--no-head", action="store_true")
    a = ap.parse_args()
    sheets, report = build(a.src, not a.no_head)
    spec = {"cell": list(CELL), "scale": 8, "tags": {}}
    for tag, frames in sheets.items():
        Image.fromarray(strip([to_cell(c) for c in frames])).save(lp(os.path.join(a.out, f"vi_{tag}.png")))
        spec["tags"][tag] = [{"pivot": list(PIVOT), "ms": ms} for ms in TIMES[tag]]
        print(f"{tag:10s} {len(frames)} frames", report.get(tag, ""))
    with open(lp(os.path.join(a.out, "vi_cells.json")), "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
