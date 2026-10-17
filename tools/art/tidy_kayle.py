#!/usr/bin/env python3
"""Tidy Codex's redraw of Kayle (assets/source/kayle/MODEL_REDRAW.md) into the native strips.

    python tools/art/tidy_kayle.py <Codex's delivery folder> [--out DIR] [--review DIR]

Codex delivered the 63 frames of the approved design (assets/source/kayle/kayle_model_design.png) as one canvas
each: the six idle frames are the design itself, the other 57 raw image-model output - 948x1659 with soft edges,
tens of thousands of colours, "pixels" 14-16 px wide that drift off any grid, and the head, the size and the place
changing from frame to frame (its HANDOFF.md says so). Here, on the game pixels:
  - the grid: every game pixel of the 64x112 canvas takes the colour at its centre in the raw frame, dark as the
    outline colour, the rest the nearest of the design's 21 colours (Codex's squares are 11-16 px, not the 14.8
    of the canvas: merging whole cells doubled outline columns, the centre never does);
  - the head: the design's head (hair, face, eyes, mouth and their outline, holes filled) replaces the drawn
    one where it matches best (searched round the drawn hair, upright or turned a quarter for the frames lying on
    the ground), so the eyes and the face are the same in every frame; eye colours left elsewhere take the gold's;
  - the place: sideways the eyes' middle stands on League's head joint of that frame (cells table), as in the
    design; up and down the lowest row of the body (not the sword, not the wings) matches the current frame's,
    which keeps League's float in the move;
  - single stray squares (no neighbour) go.
The canvases then go through tools/art/native_frames.py join (into assets/source/native) and
tools/art/import_native.py --hero kayle.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import native_frames as F  # noqa: E402

DESIGN = os.path.join(ROOT, "assets", "source", "kayle", "kayle_model_design.png")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
GW, GH = 64, 112
PAL = ["1E1624", "F6F8FA", "E4EDF3", "ADBAC7", "FBDCC4", "F2B48E", "5A2E08", "E28A08", "D0203A", "FBD764",
       "F2BE4C", "D99A34", "A86E23", "CED3BC", "A3AA97", "B6E8F5", "96B4F9", "8C90E0", "B296F5", "6DF9F1", "43E6DE"]
RGB = np.array([[int(c[i:i + 2], 16) for i in (0, 2, 4)] for c in PAL], np.uint8)
OUTLINE = 0
HAIR = {1, 2, 3}
FACE = {4, 5, 6, 7, 8}
EYES = {6, 7}
SWORD = {19, 20}
WINGS = {15, 16, 17, 18}
EYE_TO = {6: 12, 7: 11}                 # eye colours away from the face: dark eye -> dark gold, amber -> gold
HEAD_ROWS = (55, 71)                    # the design's head: rows 55-70 (hair top to the outline under the chin)


def labels(rgba):
    """RGBA game pixels -> palette index per pixel (-1 transparent)."""
    out = np.full(rgba.shape[:2], -1, int)
    op = rgba[..., 3] > 0
    d = ((rgba[..., None, :3].astype(int) - RGB[None, None].astype(int)) ** 2).sum(-1)
    out[op] = d[op].argmin(-1)
    return out


def to_rgba(lab):
    out = np.zeros(lab.shape + (4,), np.uint8)
    op = lab >= 0
    out[op, :3] = RGB[lab[op]]
    out[op, 3] = 255
    return out


def snap(path):
    """A delivered frame -> 64x112 palette labels: every game pixel takes the colour at its centre in the raw
    frame (the median of the 3x3 pixels there; clear when most are clear), dark as the outline, else the nearest
    of the palette. Codex's squares are 11-16 px wide, not the canvas's 14.8, so merging whole cells doubled an
    outline column here and there (a black line down the move's 11th frame); the centre drops a row or a
    column now and then but never doubles one."""
    img = Image.open(path).convert("RGBA")
    if img.size == (GW * 8, GH * 8):
        return labels(np.asarray(img)[4::8, 4::8])
    im = np.asarray(img).astype(float)
    H, W = im.shape[:2]
    px, py = W / GW, H / GH
    lab = np.full((GH, GW), -1, int)
    for y in range(GH):
        for x in range(GW):
            cy, cx = int((y + 0.5) * py), int((x + 0.5) * px)
            patch = im[max(0, cy - 1):cy + 2, max(0, cx - 1):cx + 2].reshape(-1, 4)
            op = patch[patch[:, 3] >= 128]
            if len(op) * 2 < len(patch):
                continue
            c = np.median(op[:, :3], axis=0)
            lab[y, x] = OUTLINE if c.max() < 70 else int(((RGB.astype(float) - c) ** 2).sum(1).argmin())
    return lab


def fill(mask):
    """The mask with its enclosed holes filled (4-connected flood from the border)."""
    h, w = mask.shape
    out = np.zeros((h + 2, w + 2), bool)
    out[1:-1, 1:-1] = mask
    seen = np.zeros_like(out)
    todo = [(0, 0)]
    seen[0, 0] = True
    while todo:
        y, x = todo.pop()
        for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if 0 <= ny < h + 2 and 0 <= nx < w + 2 and not seen[ny, nx] and not out[ny, nx]:
                seen[ny, nx] = True
                todo.append((ny, nx))
    return ~seen[1:-1, 1:-1]


def design_head():
    """(labels, mask) of the design's head in its bounding box, and the eyes' middle column in that box."""
    lab = labels(np.asarray(Image.open(DESIGN).convert("RGBA"))[4::8, 4::8])
    core = np.isin(lab, list(HAIR | FACE))
    core[:HEAD_ROWS[0]] = False
    core[HEAD_ROWS[1]:] = False
    m = core.copy()
    for y, x in zip(*np.nonzero(lab == OUTLINE)):
        if core[max(0, y - 1):y + 2, max(0, x - 1):x + 2].any():
            m[y, x] = True
    m = fill(m)
    ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    box, mask = lab[y0:y1, x0:x1].copy(), m[y0:y1, x0:x1]
    ex = np.nonzero(np.isin(box, list(EYES)))[1]
    return box, mask, (ex.min() + ex.max()) / 2.0


def near(mask, ys, xs, r):
    """For each (y, x): is any mask pixel within r squares (Chebyshev)?"""
    out = []
    for y, x in zip(ys, xs):
        out.append(bool(mask[max(0, y - r):y + r + 1, max(0, x - r):x + r + 1].any()))
    return np.array(out, bool)


def drawn_eyes(lab):
    """The drawn eyes' middle (row, column) when two amber squares beside skin sit 2-4 columns apart on one row
    (or rows next to each other), else None."""
    skin = np.isin(lab, [4, 5])
    ys, xs = np.nonzero(lab == 7)
    ok = near(skin, ys, xs, 2)
    pts = sorted(zip(ys[ok].tolist(), xs[ok].tolist()))
    best = None
    for i, (y1, x1) in enumerate(pts):
        for y2, x2 in pts[i + 1:]:
            if abs(y1 - y2) <= 1 and 2 <= abs(x1 - x2) <= 4:
                cand = ((y1 + y2) / 2.0, (x1 + x2) / 2.0)
                if best is None or cand[0] < best[0]:
                    best = cand
    return best


def components(mask):
    """4-connected groups of mask squares, as lists of (y, x)."""
    seen = np.zeros_like(mask, bool)
    groups = []
    for y0, x0 in zip(*np.nonzero(mask)):
        if seen[y0, x0]:
            continue
        todo, g = [(y0, x0)], []
        seen[y0, x0] = True
        while todo:
            y, x = todo.pop()
            g.append((y, x))
            for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= ny < mask.shape[0] and 0 <= nx < mask.shape[1] and mask[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    todo.append((ny, nx))
        groups.append(g)
    return groups


def face_middle(lab, top, x0, x1, rows):
    """The middle column of the skin (and eyes and mouth) under a head's top, within its columns (+3)."""
    c0 = max(0, x0 - 3)
    ys, xs = np.nonzero(np.isin(lab[top:top + rows, c0:x1 + 4], list(FACE)))
    return xs.mean() + c0 if len(xs) else (x0 + x1) / 2.0


def place_head(lab, head, mask):
    """Where the design's head goes: its eyes on the drawn eyes when two are found; else its hair's top on the
    drawn hair's top (the biggest group of hair squares) and its face's middle column on the drawn face's.
    (y, x, how) or None."""
    ey, ex = np.nonzero(np.isin(head, list(EYES)))
    eyes = drawn_eyes(lab)
    if eyes is not None:
        y, x = int(round(eyes[0] - ey.max())), int(round(eyes[1] - (ex.min() + ex.max()) / 2.0))
        how = "on the drawn eyes"
    else:
        groups = components(np.isin(lab, list(HAIR)))
        if not groups or len(max(groups, key=len)) < 12:
            return None
        g = max(groups, key=len)
        top = min(p[0] for p in g)
        gx = [p[1] for p in g]
        hy = np.nonzero(np.isin(head, list(HAIR)).any(1))[0].min()
        hhair = np.nonzero(np.isin(head, list(HAIR)))[1]
        hface = face_middle(head, hy, hhair.min(), hhair.max(), head.shape[0])
        cx = face_middle(lab, top, min(gx), max(gx), head.shape[0] - hy)
        y, x = int(top - hy), int(round(cx - hface))
        how = "on the drawn hair and face"
    if y < 0 or x < 0 or y + head.shape[0] > GH or x + head.shape[1] > GW:
        return None
    return y, x, how


def body_low(lab):
    """The lowest row with body colour (not the outline, the sword or the wings)."""
    rows = np.nonzero(((lab > 0) & ~np.isin(lab, list(SWORD | WINGS))).any(1))[0]
    return int(rows.max())


def now_body_low(rgba):
    """The same on a current frame (the restyled palette): not the outline, not the teal blade, not the wings."""
    op = rgba[..., 3] > 0
    r, g, b = [rgba[..., i].astype(int) for i in range(3)]
    dark = op & (np.maximum(np.maximum(r, g), b) < 60)
    teal = op & (g > r + 40) & (b > r + 20)
    wing = op & (b > r + 25) & (b > g - 10) & ~teal
    rows = np.nonzero((op & ~dark & ~teal & ~wing).any(1))[0]
    return int(rows.max())


def shift(lab, dy, dx):
    out = np.full_like(lab, -1)
    ys, xs = np.nonzero(lab >= 0)
    ny, nx = ys + dy, xs + dx
    ok = (ny >= 0) & (ny < GH) & (nx >= 0) & (nx < GW)
    if (~ok).any():
        print(f"    {int((~ok).sum())} squares fall off the canvas")
    out[ny[ok], nx[ok]] = lab[ys[ok], xs[ok]]
    return out


def tidy(lab, head, mask, now_low, keep_head=False):
    """One frame: the design's head pasted (not for keep_head: the hit's shut eyes, the death lying down), eye
    colours away from the face and lone squares cleared, moved up or down onto the current frame's lowest body
    row. Sideways the drawing stays where Codex put it (the idle and the move are steadied on the eyes at import)."""
    notes = []
    fit = None if keep_head else place_head(lab, head, mask)
    inside = np.zeros_like(lab, bool)
    if fit is not None:
        y, x, how = fit
        # the drawn head's hair and face go first (its rows and 2 above, 3 columns either side), then the design's
        sub = lab[max(0, y - 2):y + head.shape[0], max(0, x - 3):min(GW, x + head.shape[1] + 3)]
        sub[np.isin(sub, list(HAIR | FACE))] = -1
        region = lab[y:y + head.shape[0], x:x + head.shape[1]]
        region[mask] = head[mask]
        inside[y:y + head.shape[0], x:x + head.shape[1]] = mask
        # outline squares the drawn head left with no colour beside them
        op = lab >= 0
        col = op & (lab != OUTLINE)
        near_col = np.zeros_like(col)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                near_col |= np.roll(np.roll(col, dy, 0), dx, 1)
        lab[(lab == OUTLINE) & ~near_col] = -1
        notes.append(f"head at ({x},{y}) {how}")
    else:
        notes.append("head kept as drawn")
    # eye colours stay only on the face (the pasted head; on a drawn head, beside skin): the rest take the gold's,
    # so the amber is the eyes' alone (tools/art/import_native.py steadies the idle and the move on it)
    ys, xs = np.nonzero(np.isin(lab, list(EYES)) & ~inside)
    face = near(np.isin(lab, [4, 5]), ys, xs, 2) if fit is None else np.zeros(len(ys), bool)
    stray = np.zeros_like(lab, bool)
    stray[ys[~face], xs[~face]] = True
    for k, to in EYE_TO.items():
        lab[stray & (lab == k)] = to
    if stray.any():
        notes.append(f"{int(stray.sum())} eye squares off the face")
    # single squares with no neighbour
    op = lab >= 0
    nb = np.zeros_like(op, int)
    nb[1:] += op[:-1]; nb[:-1] += op[1:]; nb[:, 1:] += op[:, :-1]; nb[:, :-1] += op[:, 1:]
    lab[op & (nb == 0)] = -1
    dy = now_low - body_low(lab)
    notes.append(f"moved {dy:+d} rows")
    return shift(lab, dy, 0), notes


TARGETS = os.path.join(ROOT, "assets", "source", "kayle", "codex_model", "kayle_targets.json")


def load_targets(cells, design):
    """Per frame: the column the eyes' middle goes to and the body's lowest row. Measured once on the frames
    the redraw replaced (the restyled strips) and kept in kayle_targets.json, so this runs again after the join."""
    if os.path.exists(TARGETS):
        return json.load(open(TARGETS, encoding="utf-8"))
    import tempfile
    now_dir = tempfile.mkdtemp()
    F.split("kayle", now_dir, GW, 8)
    idle = cells["tags"]["idle"][0]
    design_eye = np.nonzero(np.isin(design, list(EYES)))[1]
    offset = (design_eye.min() + design_eye.max()) / 2.0 - (idle["head"][0] - (idle["pivot"][0] - GW // 2))
    out = {}
    for tag, rows in cells["tags"].items():
        for k, r in enumerate(rows):
            name = f"kayle_{tag}_{k + 1:02d}"
            now = np.asarray(Image.open(os.path.join(now_dir, name + ".png")).convert("RGBA"))[4::8, 4::8]
            out[name] = {"eyes_x": round(r["head"][0] - (r["pivot"][0] - GW // 2) + offset, 2),
                         "body_low": now_body_low(now)}
    os.makedirs(os.path.dirname(TARGETS), exist_ok=True)
    with open(TARGETS, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=0)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("delivery")
    ap.add_argument("--out", help="write the tidied canvases here (default: a 'tidy' folder beside the delivery)")
    args = ap.parse_args()
    src = os.path.join(args.delivery, "frames") if os.path.isdir(os.path.join(args.delivery, "frames")) else args.delivery
    out = args.out or os.path.join(args.delivery, "tidy")
    os.makedirs(out, exist_ok=True)
    head, mask, _ = design_head()
    cells = F.load_cells("kayle")
    table = F.frames_table(cells, GW)
    design = labels(np.asarray(Image.open(DESIGN).convert("RGBA"))[4::8, 4::8])
    targets = load_targets(cells, design)
    for tag, rows in cells["tags"].items():
        for k, r in enumerate(rows):
            name = f"kayle_{tag}_{k + 1:02d}"
            lab = snap(os.path.join(src, name + ".png"))
            if tag == "idle":
                res, notes = design.copy(), ["the design"]
            else:
                res, notes = tidy(lab, head, mask, targets[name]["body_low"], keep_head=tag in ("hit", "dead"))
            Image.fromarray(to_rgba(res), "RGBA").resize((GW * 8, GH * 8), Image.NEAREST).save(
                os.path.join(out, name + ".png"))
            print(f"{name:22s} " + "; ".join(notes))
    json.dump(table, open(os.path.join(out, "kayle_frames.json"), "w"), indent=1)
    print("canvases in", out)


if __name__ == "__main__":
    main()
