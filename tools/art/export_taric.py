#!/usr/bin/env python3
"""Taric's game-size strips from Codex's approved high-detail delivery.

    python tools/art/export_taric.py <taric-approved.png> <taric-approved-animations folder> [--check]

The user gave Codex a picture of Taric ("这个很完美": taric-approved.png, the game-size design B2's head redrawn as
one form - middle part, small blue eyes with their own lids, a closed mouth, the bare hand with a palm and fingers) and
Codex drew the nine strips from it (assets/source/taric/codex_strips/HANDOFF.md): high-detail pixel art about 70
drawn squares tall, not on the game grid ("未强行压回 ... 40 格高、26 色、每格 8×8 纯色块 ... 实际游戏导入仍需按项目最终显示
比例处理"), placed in the pack's 768x768 cells at its pivots. This brings them to game size:
  1. the colours: the picture read back on its own grid (the skill's regrid.py, ~14 px squares), 28 colours
     (tools/art/design_riven.palette, k-means in Lab);
  2. every frame, the idle too: read at one step per strip - its standing frame's height / 40 source px per game
     pixel (the ult and the Bravado strike were drawn about 6% smaller than the others: their own standing frame
     decides) - each game pixel the colour most of its block maps to, on a grid anchored at the feet line. The first
     idle was the picture itself cut to 40 rows by deleting rows and columns (never the face's), as Riven and Akali
     were: its head kept 16 rows and every action's 11-12, so the head changed size whenever he acted (the user:
     "塔里克放技能头还会变大？"); now the idle is Codex's own idle frame at the strips' scale;
  3. the eyes: at this size a vote loses them to the skin round them, so the pair is found in the source (eye_spots)
     and set to EYE;
  4. the head: the vote also loses the 1-3 px lines of brows, lids and mouth and turns the lock of hair in front of
     his ear into the darkest brown, a line through the face (the user: "待机帧的这个头就很奇怪"). FACE_EDITS places the
     idle's face square by square, traced from Codex's idle (a lid over each eye, the nose's shadow, the mouth, the
     chin's edge, the lock in mid browns). Every other frame's head was voted on its own, so its hair and jaw
     changed shape from frame to frame (the user: "gif图里看脸怎么还会变形"): each frame whose eyes are level and 2-4
     apart - the head upright - loses its own head (the head's colours joined to its near eye, crown to chin) and
     gets the idle's, aligned on the near eye, on the squares left empty; detached bits of its old hair go. The
     death's thrown-back and bowed heads keep their own;
  5. the outline closed (strips.complete_outline); each frame put in its 96x96 cell at the manifest's pivot ->
     assets/source/native/taric_<tag>.png (8x blocks), taric_cells.json (pivots and durations from the manifest) and
     taric_native.png (the idle frame).
Codex drew six identical idle frames: the first is used for all six. --check compares with the files.
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
import design_riven as R  # noqa: E402
import regrid as G  # noqa: E402
import strips  # noqa: E402

NATIVE = os.path.join(ROOT, "assets", "source", "native")
ROWS = 40                        # the top of the hair to the soles
K = 28                           # design colours
EYE = (24, 44, 176)              # the eyes' blue, used nowhere else (import_native steadies the loops on it)
BELOW = {"dead": 2}             # rows a strip may reach under the soles (the death kneels and slumps: 2)
# the idle's face, square by square from the near (left) eye: (rows down, columns right, colour). The palette's
# outline, hair and skin colours; traced from Codex's idle frame at this scale (eyes 3 apart on one row)
LID, HAIR_MID, HAIR_LIGHT = (0x36, 0x1B, 0x29), (0x66, 0x39, 0x3D), (0x8D, 0x49, 0x41)
SKIN, SHADE, OUTLINE = (0xFD, 0xC6, 0x94), (0xF6, 0x9F, 0x74), (0x17, 0x0F, 0x1D)
FACE_EDITS = [
    (-1, 0, LID), (-1, 1, SKIN), (-1, 3, LID),                  # a lid over each eye, skin between the brows
    (1, 3, SKIN),                                               # the far cheek's edge (was a hair square)
    (1, 2, SHADE), (2, 2, SKIN), (2, -2, SKIN),                 # the nose's shadow under the far eye's inner corner
    (3, 1, SHADE), (3, 2, SHADE), (3, 3, SKIN), (4, -1, SKIN),  # the mouth, a short shadow line
    (5, -1, SHADE), (5, 0, SHADE), (6, 1, OUTLINE), (6, 2, OUTLINE),     # under the jaw; the chin's lower edge
    (0, -3, HAIR_MID), (0, -2, HAIR_LIGHT), (1, -3, HAIR_MID),  # the lock in front of the ear in mid browns
    (3, -3, HAIR_MID), (3, -2, HAIR_LIGHT), (4, -2, HAIR_MID),
]
HEAD_BOX = ((-10, 5), (-15, 7))  # the head's rows and columns from the near eye: crown to chin, the long hair to the far edge
SPECK = 12                       # detached bits of hair at most this big, left over from a frame's own head, go
CELL, Z, SOLES = 96, 8, 11       # the pack's cells (squares), 8 px a square, soles 11 rows under the pivot
TAGS = ["idle", "run", "attack", "attack_p", "skill", "skill2", "ult", "hit", "dead"]
STAND = {"idle": 1, "run": 1, "attack": 6, "attack_p": 6, "skill": 6, "skill2": 6, "ult": 7, "hit": 2, "dead": 1}


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def eye_blue(px):
    """The approved face's eye pixels: a dark saturated blue (about #0F1C90)."""
    r, g, b = px[..., 0].astype(int), px[..., 1].astype(int), px[..., 2].astype(int)
    return (r < 45) & (g < 70) & (b > 105) & (b < 200)


def eye_ish(px):
    """eye_blue, or the lighter lavender blue the far eye has when he looks up (the ult, about #7B82B4)."""
    r, g, b = px[..., 0].astype(int), px[..., 1].astype(int), px[..., 2].astype(int)
    return eye_blue(px) | ((b > 120) & (b - r > 30) & (b - g > 25))


def skin(px):
    r, g, b = px[..., 0].astype(int), px[..., 1].astype(int), px[..., 2].astype(int)
    return (r > 200) & (g > 130) & (b > 90) & (r - b > 60)


def palette(picture):
    """The approved picture's K colours: read back on its own grid, k-means in Lab."""
    src = np.asarray(Image.open(lp(picture)).convert("RGBA"))
    pal, _ = R.palette(G.regrid(src)[0], K)
    return np.array(sorted({tuple(int(v) for v in c) for c in pal}), np.uint8)


def eyes_of(g):
    """(row, column) of the near eye when the frame's two EYE squares are level (a row apart at most) and 2-4 apart -
    the head upright - else None."""
    ys, xs = np.nonzero(np.all(g[..., :3] == np.array(EYE, np.uint8), -1) & (g[..., 3] > 0))
    if len(ys) == 2 and abs(int(ys[0]) - int(ys[1])) <= 1 and 2 <= abs(int(xs[1]) - int(xs[0])) <= 4:
        k = int(np.argmin(xs))
        return int(ys[k]), int(xs[k])
    return None


def is_armour(rgb):
    """The armour's and cape's colours (blue-leaning, or light and grey): never part of the head."""
    r, g, b = (int(v) for v in rgb)
    return b > r + 20 or (min(r, g, b) > 150 and max(r, g, b) - min(r, g, b) < 60)


def head_mask(g, at, colours):
    """The head: the squares of the head's colours joined to the near eye inside HEAD_BOX."""
    (r0, r1), (c0, c1) = HEAD_BOX
    ey, ex = at
    H, W = g.shape[:2]
    ok = np.zeros((H, W), bool)
    for y in range(max(ey + r0, 0), min(ey + r1 + 1, H)):
        for x in range(max(ex + c0, 0), min(ex + c1 + 1, W)):
            ok[y, x] = g[y, x, 3] > 0 and tuple(int(v) for v in g[y, x, :3]) in colours
    m = np.zeros_like(ok)
    stack = [at]
    while stack:
        y, x = stack.pop()
        if 0 <= y < H and 0 <= x < W and ok[y, x] and not m[y, x]:
            m[y, x] = True
            stack += [(y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)]
    return m


def fix_face(g):
    """FACE_EDITS on the idle frame, in place; its head as (near eye, mask, pixels, the head's colours)."""
    at = eyes_of(g)
    ey, ex = at
    for dy, dx, rgb in FACE_EDITS:
        g[ey + dy, ex + dx, :3] = rgb
        g[ey + dy, ex + dx, 3] = 255
    (r0, r1), (c0, c1) = HEAD_BOX
    box = g[max(ey + r0, 0):ey + r1 + 1, max(ex + c0, 0):ex + c1 + 1].reshape(-1, 4)
    colours = {tuple(int(v) for v in p[:3]) for p in box if p[3] > 0 and not is_armour(p[:3])} | {EYE}
    return at, head_mask(g, at, colours), g.copy(), colours


def paste_head(g, head):
    """The idle's head on a frame whose head is upright, aligned on the near eye: the frame's own head (its colours
    joined to its eye) cleared, the idle's put on the empty squares, then detached bits of hair (SPECK) dropped."""
    at = eyes_of(g)
    if at is None:
        return False
    (iy, ix), mask, src, colours = head
    g[head_mask(g, at, colours)] = 0
    dy, dx = at[0] - iy, at[1] - ix
    H, W = g.shape[:2]
    for y, x in zip(*np.nonzero(mask)):
        Y, X = y + dy, x + dx
        if 0 <= Y < H and 0 <= X < W and g[Y, X, 3] == 0:
            g[Y, X] = src[y, x]
    op = g[..., 3] > 0
    seen = np.zeros_like(op)
    for y, x in zip(*np.nonzero(op)):
        if seen[y, x]:
            continue
        stack, part = [(y, x)], []
        seen[y, x] = True
        while stack:
            py, px = stack.pop()
            part.append((py, px))
            for ny in (py - 1, py, py + 1):
                for nx in (px - 1, px, px + 1):
                    if 0 <= ny < H and 0 <= nx < W and op[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((ny, nx))
        if len(part) <= SPECK and all(tuple(int(v) for v in g[p][:3]) in colours for p in part):
            for p in part:
                g[p] = 0
    return True


def vote(cell, step, feet_px, pal, plab, below=0):
    """Game pixels from one high-detail frame: the grid's rows end on the soles' bottom edge (feet_px), `below` more
    rows under it. Returns the pixels and the eye candidates (blocks holding enough of the eye blue among skin)."""
    H, W = cell.shape[:2]
    rows = int(np.ceil(feet_px / step))
    y_top = feet_px - rows * step
    rows += below
    cols = int(np.ceil(W / step))
    out = np.zeros((rows, cols, 4), np.uint8)
    cand = np.zeros((rows, cols), bool)
    for j in range(rows):
        y0, y1 = int(round(y_top + j * step)), int(round(y_top + (j + 1) * step))
        if y1 <= 0:
            continue
        for i in range(cols):
            x0, x1 = int(round(i * step)), int(round((i + 1) * step))
            blk = cell[max(y0, 0):y1, x0:min(x1, W)].reshape(-1, 4)
            if not len(blk):
                continue
            opq = blk[blk[:, 3] > 0]
            if len(opq) * 2 < len(blk):
                continue
            lab = R.to_lab(opq[:, :3])
            k = np.bincount(np.argmin(((lab[:, None] - plab[None]) ** 2).sum(-1), axis=1), minlength=len(pal)).argmax()
            out[j, i, :3] = pal[k]
            out[j, i, 3] = 255
    for cy, cx in eye_spots(cell):
        j, i = int((cy - y_top) // step), int(cx // step)
        if 0 <= j < rows and 0 <= i < cols:
            cand[j, i] = True
    return out, cand


def blobs(mask, lo, hi):
    """8-connected patches of mask with lo-hi pixels: [(centre y, centre x, box)]."""
    H, W = mask.shape
    seen = np.zeros_like(mask)
    out = []
    for y, x in zip(*np.nonzero(mask)):
        if seen[y, x]:
            continue
        stack, pts = [(y, x)], []
        seen[y, x] = True
        while stack:
            py, px = stack.pop()
            pts.append((py, px))
            for ny in (py - 1, py, py + 1):
                for nx in (px - 1, px, px + 1):
                    if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((ny, nx))
        if lo <= len(pts) <= hi:
            ys, xs = zip(*pts)
            out.append((sum(ys) / len(ys), sum(xs) / len(xs), (min(ys), max(ys), min(xs), max(xs)), len(pts)))
    return out


def eye_spots(cell):
    """The approved face's eyes in one high-detail frame, their centres. The eyes are two small blue patches about
    30 px apart, level or on a slant when the head tilts (the death throws it back 32 degrees), the nose's bridge
    between them (3/4 view: the far eye by the face's edge has less skin round it, and when he looks up it is a
    lighter lavender): the highest such pair with skin round them. The pendant at his throat is the same blue among
    skin, bigger and lower; the cape's navy and the gems have cloth or silver round them. With no pair, one eye: the
    highest dark-blue patch with skin round it (the face's box in the game frame drops a stray one)."""
    op = cell[..., 3] > 0
    sk = skin(cell[..., :3]) & op

    def share(box, n):
        y0, y1, x0, x1 = box
        win = sk[max(y0 - 8, 0):y1 + 9, max(x0 - 8, 0):x1 + 9]
        ring = op[max(y0 - 8, 0):y1 + 9, max(x0 - 8, 0):x1 + 9]
        return win.sum() / max(ring.sum() - n, 1)

    def bridge(a, b):
        """Share of skin on the line between two patches' centres (the nose's bridge between the eyes)."""
        n = int(b[1] - a[1])
        ys = np.round(np.linspace(a[0], b[0], n)).astype(int)
        xs = np.round(np.linspace(a[1], b[1], n)).astype(int)
        return sk[ys, xs].mean()

    cands = [(cy, cx, share(box, n)) for cy, cx, box, n in blobs(eye_ish(cell[..., :3]) & op, 3, 100)]
    cands = [c for c in cands if c[2] >= 0.05]
    pairs = [(a, b) for a in cands for b in cands
             if 20 <= b[1] - a[1] <= 46 and abs(a[0] - b[0]) <= 0.7 * (b[1] - a[1]) and max(a[2], b[2]) >= 0.3
             and bridge(a, b) >= 0.4]
    if pairs:
        a, b = min(pairs, key=lambda p: p[0][0] + p[1][0])
        return [a[:2], b[:2]]
    dark = [(cy, cx) for cy, cx, box, n in blobs(eye_blue(cell[..., :3]) & op, 4, 100) if share(box, n) >= 0.4]
    return [min(dark)] if dark else []


def face_box(g):
    """The face: the biggest 4-connected patch of skin in the figure's top 45% rows, its box grown by one."""
    op = g[..., 3] > 0
    ys, _ = np.nonzero(op)
    top = ys.min()
    lim = top + int(0.45 * (ys.max() - top + 1))
    sk = skin(g[..., :3]) & op
    sk[lim:] = False
    best, seen = None, np.zeros_like(sk)
    H, W = sk.shape
    for y, x in zip(*np.nonzero(sk)):
        if seen[y, x]:
            continue
        stack, pts = [(y, x)], []
        seen[y, x] = True
        while stack:
            cy, cx = stack.pop()
            pts.append((cy, cx))
            for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
                if 0 <= ny < H and 0 <= nx < W and sk[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    stack.append((ny, nx))
        if best is None or len(pts) > len(best):
            best = pts
    if not best:
        return None
    py, px = zip(*best)
    return min(py) - 1, max(py) + 1, min(px) - 1, max(px) + 1


def frame(img, fr, step, pal, plab, below):
    """One source frame at game size, its eyes set to EYE (not yet the face, not yet the outline)."""
    x, y, w, h = fr["rect"]
    g, cand = vote(img[y:y + h, x:x + w], step, fr["pivot_px"][1] + (SOLES + 1) * Z, pal, plab, below)
    box = face_box(g)
    if box is not None:
        y0, y1, x0, x1 = box
        inside = np.zeros_like(cand)
        inside[max(y0, 0):y1 + 1, max(x0, 0):x1 + 1] = True
        g[cand & inside, :3] = EYE
    return g


def export(picture, folder):
    pal = palette(picture)
    plab = R.to_lab(pal)
    man = json.load(open(os.path.join(folder, "manifest.json"), encoding="utf-8"))["animations"]
    sheets, table = {}, {"cell": [CELL, CELL], "scale": Z, "tags": {}}
    head = native = None
    pasted = {}
    for tag in TAGS:                                  # the idle first: its face goes on the others
        info = man[tag]
        img = np.asarray(Image.open(os.path.join(folder, info["file"])).convert("RGBA"))
        fr0 = info["frames"][STAND[tag] - 1]
        x0, y0, x1, y1 = fr0["bbox_px"]
        step = (y1 - y0) / ROWS
        n = len(info["frames"])
        ncol = info["columns"]
        nrow = -(-n // ncol)
        below = BELOW.get(tag, 0)
        sheet = np.zeros((nrow * CELL, ncol * CELL, 4), np.uint8)
        table["tags"][tag] = []
        pasted[tag] = []
        for k, fr in enumerate(info["frames"]):
            px, py = fr["pivot_native"]
            cx, cy = (k % ncol) * CELL, (k // ncol) * CELL
            src = info["frames"][0] if tag == "idle" else fr     # six identical idle frames: the first for all
            g = frame(img, src, step, pal, plab, below)
            if tag == "idle":
                head = fix_face(g)
            else:
                pasted[tag].append(paste_head(g, head))
            g, _, _ = strips.complete_outline(g, feet=g.shape[0] - 1 - below)
            if native is None:
                native = crop(g)
            # the frame's pixels keep their place across the cell: source x / step, the pivot on pivot_px
            gx = int(round(px - src["pivot_px"][0] / step))
            gy = py + SOLES + 1 + below - g.shape[0]
            m = g[..., 3] > 0
            ys, xs = np.nonzero(m)
            ys0, xs0 = ys + gy, xs + gx
            ok = (ys0 >= 0) & (ys0 < CELL) & (xs0 >= 0) & (xs0 < CELL)
            sheet[cy + ys0[ok], cx + xs0[ok]] = g[ys[ok], xs[ok]]
            table["tags"][tag].append({"pivot": [px, py], "ms": int(fr["duration_ms"])})
        sheets[tag] = sheet
    return native, sheets, table, pasted


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("picture")
    ap.add_argument("folder")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    fig, sheets, table, pasted = export(a.picture, a.folder)
    for tag, done in pasted.items():
        print(f"{tag:8s} head pasted in frames", [k + 1 for k, d in enumerate(done) if d])
    canvas = np.zeros((128, 128, 4), np.uint8)
    soles = np.nonzero(fig[-1, :, 3] > 0)[0]
    fx = (soles.min() + soles.max() + 1) // 2
    canvas[100 - fig.shape[0]:100, 64 - fx:64 - fx + fig.shape[1]] = fig
    outs = {"taric_native.png": canvas, **{f"taric_{t}.png": s for t, s in sheets.items()}}
    same = True
    for name, arr in outs.items():
        big = Image.fromarray(np.repeat(np.repeat(arr, Z, 0), Z, 1))
        path = os.path.join(NATIVE, name)
        if a.check:
            old = np.asarray(Image.open(lp(path)).convert("RGBA"))
            eq = old.shape == np.asarray(big).shape and np.array_equal(old, np.asarray(big))
            same &= eq
            print(name, "identical" if eq else "DIFFERENT")
        else:
            big.save(lp(path))
    if not a.check:
        with open(lp(os.path.join(NATIVE, "taric_cells.json")), "w", encoding="utf-8", newline="\n") as f:
            json.dump(table, f, indent=1)
        cols = len(np.unique(fig[fig[..., 3] > 0][:, :3], axis=0))
        print(f"idle {fig.shape[1]}x{fig.shape[0]}, {cols} colours; {len(sheets)} strips written")
    elif not same:
        sys.exit(1)


if __name__ == "__main__":
    main()
