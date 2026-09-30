#!/usr/bin/env python3
"""Tidy Codex's strips of Briar and write them to the native strips.

    python tools/art/tidy_briar.py <Codex's delivery folder>

Briar's design is Codex's 76-row drawing of the user's picture, shrunk by Claude to 46 rows by deleting whole rows and
columns and tidied (assets/source/briar/MODEL_STRIPS.md): 38x46 with the pillory, 23 colours, the milky eyes in two
colours used nowhere else (#F0FCFF, the glint #C5E6F5). Codex drew the ten strips from it on the reference cells
(96x96 game pixels, every pixel an 8x8 block) and pasted the design's head into every upright frame
(briar_animation_pack: strips, briar_cells.json, manifest.json with each frame's head_rect_1x,
reference_design/briar_head_1x.png). Two fixes on the game pixels:
  - the head window: Codex pasted the head's whole 16x15 rectangle, and everything in it but the head - plus one
    square round it on the left, right and top - became transparent, so the pillory and the body behind the head
    showed a square hole with straight edges (a box round the face in play). In each row of that window the gap
    between its edge and the head is filled with the material just outside (the commonest non-outline colour of the
    3 squares outside) when the pillory or the body reaches the edge; the rows under the chin are filled up from the
    row under the window the same way; a transparent pocket no path joins to the outside is filled from its
    neighbours; new edges against a real opening get the outline colour;
    Where Codex's raw drawing (generated_originals/) rebuilds the delivered frame - the raw frame centre-sampled to
    the delivered bbox and snapped to the design's palette, Codex's own steps, at least 92% of the squares outside
    the window the same within a 3-square shift - the frame is that rebuild with the head mask on top (nothing
    cut, no seam; a patch of the raw drawing inside the window alone left seams); the fills above are the
    fallback (the run's frames, where Codex also shortened the shins, and the falls);
  - the last frame of attack, skill, skill2_scream, ult, ult_land and hit is the design's stance (Codex's choice):
    the exact design is put back there (the window had cut it too).
  - one outline (tools/art/tidy_codex18.py's one_outline plus the outline completion the Ahri session's fix added):
    Codex drew only 49-86% of each frame's silhouette edge dark (the design 99%), so every opaque edge square that
    is not near-black becomes the outline colour (inside the silhouette: the frame does not grow), outline spurs go,
    a near-black square just inside the outline takes the darkest of its lighter neighbours (the material's own
    dark shade, never a second black ring) and lone specks take their area's colour; the eyes and the face
    round them are left alone, the design frames too.
Then each strip is checked - flat blocks, alpha 0 or 255, only the design's colours, the eye white in every upright
frame, nothing under the feet line (the fall may reach two rows under it) - and the design's idle, the ten strips and
the cells are written to assets/source/native/. Then run import_native.py --hero briar.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "native")
Z, CELL = 8, 96
TAGS = ["idle", "run", "attack", "skill", "skill2", "skill2_scream", "ult", "ult_fly", "ult_land", "hit", "dead"]
EYE = (0xF0, 0xFC, 0xFF)
FALL = {"dead": 2}              # rows a frame may reach under the feet line
NO_EYES = {("hit", 0)} | {("dead", k) for k in range(4, 8)}   # shut eyes / lying down (Codex's own heads)
# the lunge's two bite frames: Codex re-fitted them to the cell after sampling (60-66% of the squares match the
# rebuild), but the rebuild is clean and whole - take it there too
LEAST = {("attack", 2): 0.55, ("attack", 3): 0.55}
OUTLINE = (0x16, 0x0F, 0x19)
DARKS = {(0x16, 0x0F, 0x19), (0x21, 0x1C, 0x29)}
N4 = ((0, 1), (0, -1), (1, 0), (-1, 0))
N8 = N4 + ((1, 1), (1, -1), (-1, 1), (-1, -1))


def blocks(path):
    a = np.asarray(Image.open(G.lp(path)).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"{path}: not made of flat {Z}x{Z} blocks")
    if not np.isin(a[..., 3], [0, 255]).all():
        sys.exit(f"{path}: semi-transparent pixels")
    return b[:, 0, :, 0].copy()


def up(a):
    return Image.fromarray(np.repeat(np.repeat(a, Z, 0), Z, 1))


def layout(n):
    return {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)


def colours(a):
    return {tuple(int(v) for v in p) for p in a[a[..., 3] > 0][:, :3]}


def col(a, y, x):
    return tuple(int(v) for v in a[y, x, :3])


def material(cell, pts):
    cs = [col(cell, y, x) for y, x in pts if 0 <= y < CELL and 0 <= x < CELL and cell[y, x, 3]]
    body = [c for c in cs if c not in DARKS]
    pool = body or cs
    return max(set(pool), key=pool.count) if pool else None


def paint(cell, filled, Y, X, c):
    if cell[Y, X, 3] == 0 and c:
        cell[Y, X, :3] = c
        cell[Y, X, 3] = 255
        filled[Y, X] = True


def close_window(cell, rect, hm, grow=1):
    """Fill the hole Codex's rectangular head paste cut round the head (see the module docstring)."""
    hx0, hy0, w, h = rect
    head = np.zeros((CELL, CELL), bool)
    head[hy0:hy0 + h, hx0:hx0 + w] = hm
    x0, y0 = max(0, hx0 - grow), max(0, hy0 - grow)
    x1, y1 = min(CELL - 1, hx0 + w - 1 + grow), min(CELL - 1, hy0 + h - 1 + grow)
    inside = np.zeros((CELL, CELL), bool)
    inside[y0:y1 + 1, x0:x1 + 1] = True
    filled = np.zeros((CELL, CELL), bool)
    head_rows = [Y for Y in range(y0, y1 + 1) if head[Y].any()]
    for Y in head_rows:
        hx = np.nonzero(head[Y])[0]
        if x0 - 1 >= 0 and cell[Y, x0 - 1, 3]:
            c = material(cell, [(Y, x0 - 1), (Y, x0 - 2), (Y, x0 - 3)])
            for X in range(x0, hx.min()):
                paint(cell, filled, Y, X, c)
        if x1 + 1 < CELL and cell[Y, x1 + 1, 3]:
            c = material(cell, [(Y, x1 + 1), (Y, x1 + 2), (Y, x1 + 3)])
            for X in range(x1, hx.max(), -1):
                paint(cell, filled, Y, X, c)
    last = max(head_rows)
    for X in range(x0, x1 + 1):
        if y1 + 1 < CELL and cell[y1 + 1, X, 3]:
            c = material(cell, [(y1 + 1, X), (y1 + 2, X), (y1 + 3, X)])
            hy = np.nonzero(head[:, X])[0]
            stop = hy.max() if len(hy) else last - 2
            for Y in range(y1, stop, -1):
                paint(cell, filled, Y, X, c)
    outside = np.zeros((CELL, CELL), bool)
    stack = [(Y, X) for Y in range(CELL) for X in range(CELL) if not inside[Y, X] and cell[Y, X, 3] == 0]
    for Y, X in stack:
        outside[Y, X] = True
    while stack:
        Y, X = stack.pop()
        for dy, dx in N4:
            yy, xx = Y + dy, X + dx
            if 0 <= yy < CELL and 0 <= xx < CELL and not outside[yy, xx] and cell[yy, xx, 3] == 0:
                outside[yy, xx] = True
                stack.append((yy, xx))
    pocket = inside & (cell[..., 3] == 0) & ~outside
    while pocket.any():
        grew = False
        for Y, X in zip(*np.nonzero(pocket)):
            nb = [col(cell, Y + dy, X + dx) for dy, dx in N8
                  if 0 <= Y + dy < CELL and 0 <= X + dx < CELL and cell[Y + dy, X + dx, 3] and not head[Y + dy, X + dx]]
            body = [c for c in nb if c not in DARKS]
            pool = body or nb
            if pool:
                paint(cell, filled, Y, X, max(set(pool), key=pool.count))
                pocket[Y, X] = False
                grew = True
        if not grew:
            break
    # what is left of the window and is walled in on all four sides (the pillory above, the head below, the arms
    # beside) is the cut too: its edges are the rectangle's straight lines - fill it from its neighbours as well
    def walled(Y, X):
        op = cell[..., 3] > 0
        return (op[:Y, X].any() and op[Y + 1:, X].any() and op[Y, :X].any() and op[Y, X + 1:].any())
    todo = [(Y, X) for Y, X in zip(*np.nonzero(inside & (cell[..., 3] == 0))) if walled(Y, X)]
    while todo:
        rest = []
        for Y, X in todo:
            nb = [col(cell, Y + dy, X + dx) for dy, dx in N8
                  if 0 <= Y + dy < CELL and 0 <= X + dx < CELL and cell[Y + dy, X + dx, 3] and not head[Y + dy, X + dx]]
            body = [c for c in nb if c not in DARKS]
            pool = body or nb
            if pool:
                paint(cell, filled, Y, X, max(set(pool), key=pool.count))
            else:
                rest.append((Y, X))
        if len(rest) == len(todo):
            break
        todo = rest
    return int(filled.sum())


DARK = 40
EYES = {(0xF0, 0xFC, 0xFF), (0xC5, 0xE6, 0xF5)}


def lum(rgb):
    rgb = rgb.astype(float)
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


def shifted(m, dy, dx):
    out = np.zeros_like(m)
    H, W = m.shape
    ys, yd = (slice(0, H - dy), slice(dy, H)) if dy >= 0 else (slice(-dy, H), slice(0, H + dy))
    xs, xd = (slice(0, W - dx), slice(dx, W)) if dx >= 0 else (slice(-dx, W), slice(0, W + dx))
    out[yd, xd] = m[ys, xs]
    return out


def face_mask(cell):
    """The eyes and the face round them: 2 rows over the eyes to 4 under, 3 columns either side."""
    op = cell[..., 3] > 0
    m = np.zeros(op.shape, bool)
    for c in EYES:
        m |= op & np.all(cell[..., :3] == np.array(c, np.uint8), -1)
    grown = m.copy()
    for dy in range(-2, 5):
        for dx in range(-3, 4):
            grown |= shifted(m, dy, dx)
    return grown


def one_outline(cell):
    """Complete the 1-px outline inside the silhouette, then despur, thin the second black ring, despeckle."""
    a = cell.copy()
    keep = face_mask(a)
    op = a[..., 3] > 0
    edge = np.zeros_like(op)
    for dy, dx in N4:
        edge |= op & ~shifted(op, dy, dx)
    light = edge & (lum(a[..., :3]) >= DARK) & ~keep
    a[light, :3] = OUTLINE
    for _ in range(2):
        op = a[..., 3] > 0
        cnt = sum(shifted(op, dy, dx).astype(int) for dy, dx in N4)
        a[op & (lum(a[..., :3]) < DARK) & (cnt <= 1) & ~keep] = 0
    op = a[..., 3] > 0
    L = lum(a[..., :3])
    edge = np.zeros_like(op)
    for dy, dx in N4:
        edge |= op & ~shifted(op, dy, dx)
    ring2 = np.zeros_like(op)
    for dy, dx in N4:
        ring2 |= shifted(edge, dy, dx)
    ring2 &= op & ~edge & (L < DARK) & ~keep
    out = a.copy()
    for y, x in zip(*np.nonzero(ring2)):
        cols = [col(a, y + dy, x + dx) for dy, dx in N8
                if 0 <= y + dy < CELL and 0 <= x + dx < CELL and op[y + dy, x + dx] and L[y + dy, x + dx] >= DARK]
        if len(cols) >= 2:
            out[y, x, :3] = min(cols, key=lambda c: (lum(np.array(c)), -cols.count(c)))
    res = out.copy()
    for y in range(1, CELL - 1):
        for x in range(1, CELL - 1):
            if not out[y, x, 3] or keep[y, x]:
                continue
            nb = [tuple(int(v) for v in out[y + dy, x + dx]) for dy, dx in N4]
            me = tuple(int(v) for v in out[y, x])
            if me in nb or any(n[3] == 0 for n in nb):
                continue
            best = max(set(nb), key=nb.count)
            if nb.count(best) >= 3:
                res[y, x] = best
    cell[:] = res
    return int(light.sum())


def rebuild(raw, fr_m, grid, palette):
    """The raw drawing's figure for one frame, centre-sampled to the delivered frame's bbox and snapped to the design's
    palette without the eye colours - Codex's own steps before its head paste (93-99% of the squares outside the head
    rectangle come out the same)."""
    cols, rows = grid
    H, W = raw.shape[:2]
    k = fr_m["index"] - 1
    cw, ch = W / cols, H / rows
    x0, y0 = int((k % cols) * cw), int((k // cols) * ch)
    cell = raw[y0:int(y0 + ch), x0:int(x0 + cw)]
    op = cell[..., 3] >= 220
    if not op.any():
        return None
    ys, xs = np.nonzero(op)
    blob = cell[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    bx0, by0, bx1, by1 = fr_m["bbox_1x"]
    bw, bh = bx1 - bx0, by1 - by0
    sy = ((np.arange(bh) + 0.5) * blob.shape[0] / bh).astype(int)
    sx = ((np.arange(bw) + 0.5) * blob.shape[1] / bw).astype(int)
    smp = blob[sy][:, sx]
    pal = np.array(sorted(c for c in palette if c not in EYES), float)
    out = np.zeros((bh, bw, 4), np.uint8)
    o = smp[..., 3] >= 220
    d = ((smp[o][:, None, :3].astype(float) - pal[None]) ** 2).sum(-1)
    out[o, :3] = pal[d.argmin(-1)].astype(np.uint8)
    out[o, 3] = 255
    return out


def restore_window(cell, fr_m, rebuilt, hm, grow=1):
    """Put the raw drawing back inside the head window (aligned on the ring round it), then the head mask on top.
    Returns the ring's agreement (share of equal squares) or None when it is too poor to trust."""
    x, y, w, h = fr_m["head_rect_1x"]
    bx0, by0 = fr_m["bbox_1x"][:2]
    ring = np.zeros((CELL, CELL), bool)
    ring[max(0, y - grow - 3):y + h + grow + 3, max(0, x - grow - 3):x + w + grow + 3] = True
    win = np.zeros((CELL, CELL), bool)
    win[max(0, y - grow):y + h + grow, max(0, x - grow):x + w + grow] = True
    ring &= ~win
    best = None
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            rc = np.zeros((CELL, CELL, 4), np.uint8)
            X0, Y0 = bx0 + dx, by0 + dy
            sx0, sy0 = max(0, -X0), max(0, -Y0)
            X0c, Y0c = max(0, X0), max(0, Y0)
            hh = min(rebuilt.shape[0] - sy0, CELL - Y0c)
            ww = min(rebuilt.shape[1] - sx0, CELL - X0c)
            if hh <= 0 or ww <= 0:
                continue
            rc[Y0c:Y0c + hh, X0c:X0c + ww] = rebuilt[sy0:sy0 + hh, sx0:sx0 + ww]
            agree = (np.all(rc == cell, -1) & ring).sum() / max(1, ring.sum())
            if best is None or agree > best[0]:
                best = (agree, rc)
    if best is None or best[0] < 0.6:
        return None
    rc = best[1]
    head = np.zeros((CELL, CELL), bool)
    head[y:y + h, x:x + w] = hm
    put = win & ~head
    cell[put] = rc[put]
    return round(float(best[0]), 2)


def whole_rebuild(cell, fr_m, rebuilt, hm, grow=1, least=0.92):
    """When the raw rebuild is Codex's frame everywhere outside the head window (at least `least` of the squares,
    aligned within 3 squares), the frame becomes the rebuild with the head mask on top: nothing was cut, so no seam.
    Returns the agreement or None."""
    x, y, w, h = fr_m["head_rect_1x"]
    bx0, by0 = fr_m["bbox_1x"][:2]
    away = np.ones((CELL, CELL), bool)
    away[max(0, y - grow):y + h + grow, max(0, x - grow):x + w + grow] = False
    best = None
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            rc = np.zeros((CELL, CELL, 4), np.uint8)
            X0, Y0 = bx0 + dx, by0 + dy
            sx0, sy0 = max(0, -X0), max(0, -Y0)
            X0c, Y0c = max(0, X0), max(0, Y0)
            hh = min(rebuilt.shape[0] - sy0, CELL - Y0c)
            ww = min(rebuilt.shape[1] - sx0, CELL - X0c)
            if hh <= 0 or ww <= 0:
                continue
            rc[Y0c:Y0c + hh, X0c:X0c + ww] = rebuilt[sy0:sy0 + hh, sx0:sx0 + ww]
            both = away & ((rc[..., 3] > 0) | (cell[..., 3] > 0))
            agree = (np.all(rc == cell, -1) & both).sum() / max(1, both.sum())
            if best is None or agree > best[0]:
                best = (agree, rc)
    if best is None or best[0] < least:
        return None
    rc = best[1]
    head = np.zeros((CELL, CELL), bool)
    head[y:y + h, x:x + w] = hm
    rc[head] = cell[head]
    cell[:] = rc
    return round(float(best[0]), 3)


def design_at(design, ipiv, piv):
    """The idle frame (the design) moved from the idle pivot to another pivot."""
    out = np.zeros((CELL, CELL, 4), np.uint8)
    dx, dy = piv[0] - ipiv[0], piv[1] - ipiv[1]
    ys, xs = np.nonzero(design[..., 3] > 0)
    for y, x in zip(ys, xs):
        if 0 <= y + dy < CELL and 0 <= x + dx < CELL:
            out[y + dy, x + dx] = design[y, x]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("delivery", help="Codex's briar_animation_pack folder")
    args = ap.parse_args()
    d = args.delivery
    with open(G.lp(os.path.join(d, "briar_cells.json")), encoding="utf-8") as f:
        cells_json = json.load(f)
    cells = cells_json["tags"]
    with open(G.lp(os.path.join(d, "manifest.json")), encoding="utf-8") as f:
        manifest = json.load(f)["animations"]
    head = np.asarray(Image.open(G.lp(os.path.join(d, "reference_design", "briar_head_1x.png"))).convert("RGBA"))
    ys, xs = np.nonzero(head[..., 3] > 0)
    hm = head[ys.min():ys.max() + 1, xs.min():xs.max() + 1, 3] > 0
    design = blocks(os.path.join(SRC, "briar_native.png"))
    palette = colours(design)
    idle = blocks(os.path.join(d, "briar_idle.png"))
    ipiv = cells["idle"][0]["pivot"]
    design_cell = idle[:CELL, :CELL]
    idle_area = int((design_cell[..., 3] > 0).sum())
    problems, out = [], {}
    for name in TAGS:
        a = blocks(os.path.join(d, f"briar_{name}.png"))
        rp = os.path.join(d, "generated_originals", f"briar_{name}_raw.png")
        raw = np.asarray(Image.open(G.lp(rp)).convert("RGBA")) if name != "idle" and os.path.exists(G.lp(rp)) else None
        frames = cells[name]
        cols = layout(len(frames))
        fills, areas, lines = [], [], []
        for k, fr in enumerate(frames):
            cx, cy = (k % cols) * CELL, (k // cols) * CELL
            cell = a[cy:cy + CELL, cx:cx + CELL]
            mf = manifest[name]["frames"][k]
            if name != "idle" and mf.get("head_rect_1x"):
                want = design_at(design_cell, ipiv, fr["pivot"])
                x, y, w, h = mf["head_rect_1x"]
                away = np.ones((CELL, CELL), bool)
                away[max(0, y - 1):y + h, max(0, x - 1):x + w + 1] = False
                if np.all(cell == want, -1)[away].mean() > 0.995:
                    cell[:] = want
                    fills.append("design")
                elif mf.get("head_pasted"):
                    r = None
                    if raw is not None:
                        rb = rebuild(raw, mf, manifest[name]["grid"], palette)
                        r = (whole_rebuild(cell, mf, rb, hm, least=LEAST.get((name, k), 0.92))
                             if rb is not None else None)
                    fills.append(f"raw {r}" if r is not None else close_window(cell, mf["head_rect_1x"], hm))
            if name != "idle" and fills and fills[-1] == "design":
                pass
            elif name != "idle":
                lines.append(one_outline(cell))
            op = cell[..., 3] > 0
            if not op.any():
                problems.append(f"briar_{name}.png frame {k + 1}: empty")
                continue
            low = int(np.nonzero(op.any(1))[0].max()) - (fr["pivot"][1] + 11)
            eyes = int(((cell[..., :3] == EYE).all(-1) & op).sum())
            areas.append(int(op.sum()))
            if low > FALL.get(name, 0):
                problems.append(f"briar_{name}.png frame {k + 1}: {low} rows under the feet line")
            if (name, k) not in NO_EYES and eyes != 4:
                problems.append(f"briar_{name}.png frame {k + 1}: {eyes} eye-white pixels, not the two eyes (4)")
        extra = colours(a) - palette
        if extra:
            problems.append(f"briar_{name}.png: colours not in the design: {sorted(extra)[:6]}")
        out[name] = a
        print(f"briar_{name}.png: {len(colours(a))} colours, areas vs idle "
              + " ".join(f"{v / idle_area:.2f}" for v in areas) + (f"; window fills {fills}" if fills else "")
              + (f"; outline squares {lines}" if lines else ""))
    if problems:
        print("\n".join(problems))
        sys.exit(f"{len(problems)} problems - nothing written")
    for name, a in out.items():
        up(a).save(G.lp(os.path.join(SRC, f"briar_{name}.png")))
    with open(G.lp(os.path.join(SRC, "briar_cells.json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump(cells_json, f, indent=1)
    print("wrote", len(TAGS), "strips and briar_cells.json to assets/source/native/")


if __name__ == "__main__":
    main()
