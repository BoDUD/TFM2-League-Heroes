#!/usr/bin/env python3
"""Tidy Codex's strips of Vayne and write them to the native strips.

    python tools/art/tidy_vayne.py <export_vayne.py's output folder> [--check]

Vayne's design is Codex's own game-size drawing of the user's picture, read back square for square
(assets/source/vayne/MODEL_PROMPTS.md, art-spec "A design drawn at game size"): 36x48 with the ponytail and the
crossbow on her back, 26 colours, the lenses in two reds used nowhere else (#F8303C, the shade #B0102A). Codex drew the
nine strips from it on the reference cells (96x96 game pixels, every pixel an 8x8 block, assets/source/vayne/
MODEL_STRIPS.md). Its own export pasted the design's whole head into every upright frame after clearing the drawn one
with the neck and the collar ("头和身体有点分离" "不协调"), so the strips are exported again from its raw generations by
export_vayne.py: Codex's drawn head stays with the body and only the design's face is pasted where Codex's face is
(manifest.json: each frame's face_origin; none in the tucked frames of the rolls, the fall's first frame and the last
four of the death). 26 colours, flat blocks, alpha 0/255, nothing under the feet line, the lens reds only in the
face. What the frames still lack against the design, fixed on the game pixels here:
  - stray squares: bits of the crossbow on her back and of the cape came loose from the body (at most 4 squares
    joined to the figure by a corner or not at all: 4-connected components) - removed, before and after the outline;
  - pinholes: transparent pockets of at most 6 squares that no path joins to the outside (in the cape, between the
    straps) - filled with the commonest colour round them;
  - one outline: Codex drew only 53-94% of the silhouette's edge in the outline colour (the design 95%), so every
    edge square that is not one of the design's two outline blacks (#0B0410, #0D0513) takes #0B0410 - inside the
    silhouette, so no frame grows; then an outline black just inside that ring, between lighter squares, takes the
    darkest of them (the material's own dark shade, never a second black ring: 34-67% of that ring was black, the
    design 25% by luma), and outline spurs and lone specks go. Her hair and bodysuit are dark materials (luma
    11-47), so "black" here is the outline's two colours, never a luma threshold (tidy_codex18's 40 would repaint
    them);
  - the move floated: Codex drew the run 1-2 rows above the ground, so each run frame goes down until its lowest row
    is on the feet line (League's run, the reference, has a foot on the ground in every frame);
  - the pasted face, the squares round its lenses and the frames that are the design itself (the last frame of most
    strips) are left alone.
Then every strip is checked again - flat blocks, alpha 0 or 255, only the design's colours, the lens reds only in
the pasted face or the design, nothing under the feet line (the fall may reach two rows under it) - and the strips,
the idle (the pack's, the design in all six) and the cells are written to assets/source/native/. Then run
import_native.py --hero vayne.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

import export_vayne as X

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "native")
Z = 8
TAGS = ["run", "attack", "attack_q", "skill", "skill_back", "skill2", "ult", "hit", "dead"]
OUTLINES = {(0x0B, 0x04, 0x10), (0x0D, 0x05, 0x13)}
OUT = (0x0B, 0x04, 0x10)
LENS = {(0xF8, 0x30, 0x3C), (0xB0, 0x10, 0x2A)}
FALL = {"dead": 2}
GROUND = {"run"}            # strips whose lowest row must be on the feet line in every frame
ISLAND, HOLE = 4, 6
EDGE_LUM = 40       # an edge square this light (silver, skin, bright red, brown) needs the outline; darker materials
                    # (the hair, the suit's shadow, the cape's darkest reds) already read as one, as in the design
N4 = ((0, 1), (0, -1), (1, 0), (-1, 0))
N8 = N4 + ((1, 1), (1, -1), (-1, 1), (-1, -1))


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def load(path):
    return np.asarray(Image.open(lp(path)).convert("RGBA")).copy()


def blocks(a):
    """8x strip -> 1x (and whether every block is flat)."""
    small = a[Z // 2::Z, Z // 2::Z].copy()
    flat = (np.repeat(np.repeat(small, Z, 0), Z, 1)[:a.shape[0], :a.shape[1]] == a).all()
    return small, bool(flat)


def up(a):
    return Image.fromarray(np.repeat(np.repeat(a, Z, 0), Z, 1))


def col(a, y, x):
    return tuple(int(v) for v in a[y, x, :3])


def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def design():
    """The design, 1x, cropped to the figure."""
    d = load(os.path.join(SRC, "vayne_native.png"))[Z // 2::Z, Z // 2::Z]
    ys, xs = np.nonzero(d[..., 3] > 0)
    return d[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def components(mask, conn):
    """Label connected regions of mask (conn = N4 or N8): (labels, sizes)."""
    lab = np.full(mask.shape, -1, int)
    sizes = []
    H, W = mask.shape
    for sy, sx in zip(*np.nonzero(mask)):
        if lab[sy, sx] >= 0:
            continue
        k = len(sizes)
        stack = [(sy, sx)]
        lab[sy, sx] = k
        n = 0
        while stack:
            y, x = stack.pop()
            n += 1
            for dy, dx in conn:
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and mask[yy, xx] and lab[yy, xx] < 0:
                    lab[yy, xx] = k
                    stack.append((yy, xx))
        sizes.append(n)
    return lab, sizes


def islands(cell, keep):
    """Remove bits of at most ISLAND squares that only touch the figure at a corner or not at all (4-connected);
    the number of squares removed."""
    op = cell[..., 3] > 0
    lab, sizes = components(op, N4)
    gone = 0
    if sizes:
        body = int(np.argmax(sizes))
        for k, s in enumerate(sizes):
            if k != body and s <= ISLAND and not (keep & (lab == k)).any():
                cell[lab == k] = 0
                gone += s
    return gone


def tidy(cell, keep):
    """The fixes of the module docstring on one 1x cell (RGBA, changed in place); counts of what changed."""
    H, W = cell.shape[:2]
    n = dict(islands=0, holes=0, edge=0, ring=0, specks=0)
    n["islands"] += islands(cell, keep)
    op = cell[..., 3] > 0
    hl, hs = components(~op, N4)
    border = set(hl[0, :]) | set(hl[-1, :]) | set(hl[:, 0]) | set(hl[:, -1])
    for k, s in enumerate(hs):
        if k in border or s > HOLE:
            continue
        pts = list(zip(*np.nonzero(hl == k)))
        for _ in range(4):
            left = []
            for y, x in pts:
                nb = [col(cell, y + dy, x + dx) for dy, dx in N4
                      if 0 <= y + dy < H and 0 <= x + dx < W and cell[y + dy, x + dx, 3]
                      and col(cell, y + dy, x + dx) not in OUTLINES]
                if nb:
                    cell[y, x, :3] = max(set(nb), key=nb.count)
                    cell[y, x, 3] = 255
                    n["holes"] += 1
                else:
                    left.append((y, x))
            pts = left
            if not pts:
                break
        for y, x in pts:                       # enclosed by outline only: outline it is
            cell[y, x, :3], cell[y, x, 3] = OUT, 255
            n["holes"] += 1
    op = cell[..., 3] > 0
    pad = np.pad(op, 1)
    edge = op & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
    for y, x in zip(*np.nonzero(edge & ~keep)):
        c = col(cell, y, x)
        if c not in OUTLINES and lum(c) >= EDGE_LUM:
            cell[y, x, :3] = OUT
            n["edge"] += 1
    # outline spurs: an outline square with at most one opaque 4-neighbour sticking out of the figure
    for _ in range(2):
        op = cell[..., 3] > 0
        for y, x in zip(*np.nonzero(op & ~keep)):
            if col(cell, y, x) in OUTLINES:
                cnt = sum(1 for dy, dx in N4 if 0 <= y + dy < H and 0 <= x + dx < W and op[y + dy, x + dx])
                if cnt <= 1:
                    cell[y, x] = 0
                    n["edge"] += 1
    n["islands"] += islands(cell, keep)
    op = cell[..., 3] > 0
    pad = np.pad(op, 1)
    edge = op & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
    pe = np.pad(edge, 1)
    ring = op & ~edge & (pe[:-2, 1:-1] | pe[2:, 1:-1] | pe[1:-1, :-2] | pe[1:-1, 2:])
    out = cell.copy()
    for y, x in zip(*np.nonzero(ring & ~keep)):
        if col(cell, y, x) not in OUTLINES:
            continue
        nb = [col(cell, y + dy, x + dx) for dy, dx in N8
              if 0 <= y + dy < H and 0 <= x + dx < W and op[y + dy, x + dx] and not edge[y + dy, x + dx]
              and col(cell, y + dy, x + dx) not in OUTLINES]
        if len(nb) >= 2:
            out[y, x, :3] = min(nb, key=lambda c: (lum(c), -nb.count(c)))
            n["ring"] += 1
    cell[:] = out
    op = cell[..., 3] > 0
    out = cell.copy()
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if not op[y, x] or keep[y, x]:
                continue
            me = col(cell, y, x)
            nb = [col(cell, y + dy, x + dx) if op[y + dy, x + dx] else None for dy, dx in N4]
            if None in nb or me in nb:
                continue
            best = max(set(nb), key=nb.count)
            if nb.count(best) >= 3:
                out[y, x, :3] = best
                n["specks"] += 1
    cell[:] = out
    return n


def edge_share(cell):
    """Share of the silhouette's edge squares darker than EDGE_LUM (the design: 95%)."""
    op = cell[..., 3] > 0
    pad = np.pad(op, 1)
    edge = op & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
    c = cell[..., :3].astype(float)
    dark = (0.299 * c[..., 0] + 0.587 * c[..., 1] + 0.114 * c[..., 2]) < EDGE_LUM
    return (dark & edge).sum() / max(1, edge.sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("delivery")
    ap.add_argument("--check", action="store_true", help="report only, write nothing")
    o = ap.parse_args()
    man = json.load(open(os.path.join(o.delivery, "manifest.json"), encoding="utf-8-sig"))
    cells = json.load(open(os.path.join(o.delivery, "vayne_cells.json"), encoding="utf-8"))
    cw, ch = cells["cell"][0], cells["cell"][1]
    fig0 = design()
    face = X.face_patch(X.Design())
    pal = {col(fig0, y, x) for y, x in zip(*np.nonzero(fig0[..., 3] > 0))}
    darea = int((fig0[..., 3] > 0).sum())
    bad = []
    out_strips = {}
    for tag in TAGS:
        big = load(os.path.join(o.delivery, f"vayne_{tag}.png"))
        a, flat = blocks(big)
        if not flat:
            bad.append(f"{tag}: blocks not flat")
        frames = man["animations"][tag]["frames"]
        cols = a.shape[1] // cw
        report = []
        for i, fr in enumerate(frames):
            cy, cx = (i // cols) * ch, (i % cols) * cw
            cell = a[cy:cy + ch, cx:cx + cw]
            px, py = fr["pivot"]
            keep = np.zeros(cell.shape[:2], bool)
            org = fr.get("face_origin")          # the cell offset of the 128 canvas the pasted face was cut from
            if org:
                for x, y, c in face:
                    xx, yy = x + org[0], y + org[1]
                    if 0 <= xx < cw and 0 <= yy < ch and (cell[yy, xx] == c).all():
                        keep[yy, xx] = True
            for y, x in zip(*np.nonzero(cell[..., 3] > 0)):
                if col(cell, y, x) in LENS:
                    keep[max(0, y - 2):y + 3, max(0, x - 2):x + 3] = True
            ys, xs = np.nonzero(cell[..., 3] > 0)
            fig = cell[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
            is_design = fig.shape == fig0.shape and (fig == fig0).all()
            before = edge_share(cell)
            n = dict(islands=0, holes=0, edge=0, ring=0, specks=0) if is_design else tidy(cell, keep)
            if tag in GROUND:
                # Codex drew the move 1-2 rows above the ground; League's run (the reference, "flat") has a foot on
                # the feet line in every frame: move the frame down onto it
                low = np.nonzero((cell[..., 3] > 0).any(1))[0].max()
                drop = py + 11 - low
                if drop > 0:
                    cell[drop:] = cell[:-drop].copy()
                    cell[:drop] = 0
            area = int((cell[..., 3] > 0).sum())
            report.append(f"{i + 1}:{'design' if is_design else ''}{before:.0%}->{edge_share(cell):.0%} "
                          f"a{area}({area / darea:.0%}) i{n['islands']} h{n['holes']} e{n['edge']} r{n['ring']} "
                          f"s{n['specks']}")
            cols_used = {col(cell, y, x) for y, x in zip(*np.nonzero(cell[..., 3] > 0))}
            if cols_used - pal:
                bad.append(f"{tag} {i + 1}: colours not in the design {sorted(cols_used - pal)}")
            if not set(np.unique(cell[..., 3])) <= {0, 255}:
                bad.append(f"{tag} {i + 1}: alpha not 0/255")
            feet = py + 11
            low = np.nonzero((cell[..., 3] > 0).any(1))[0].max()
            if low > feet + FALL.get(tag, 0):
                bad.append(f"{tag} {i + 1}: {low - feet} rows under the feet line")
            lens = np.zeros(cell.shape[:2], bool)
            for c in LENS:
                lens |= (cell[..., :3] == c).all(-1) & (cell[..., 3] > 0)
            if lens.any() and not org and not is_design:
                bad.append(f"{tag} {i + 1}: lens colour in a frame without the pasted face")
        print(f"{tag:10s} " + " | ".join(report))
        out_strips[tag] = a
    if bad:
        print("PROBLEMS:\n  " + "\n  ".join(bad))
    if o.check:
        return
    for tag, a in out_strips.items():
        up(a).save(lp(os.path.join(SRC, f"vayne_{tag}.png")))
    idle = load(os.path.join(o.delivery, "vayne_idle.png"))
    Image.fromarray(idle).save(lp(os.path.join(SRC, "vayne_idle.png")))
    # the standing point: the pack's idle strip put the design where it overlapped League's idle most, and her cape and
    # the crossbow on her back pulled it 9 squares left of the pivot (Codex's HANDOFF: the lenses 9 squares left of
    # League's head joint); every other frame stands the same way, so each pivot moves by the one offset that puts the
    # idle's feet (the middle of its lowest row) on it - in game she stands on her unit, under her health bar
    small, _ = blocks(idle)
    p0 = cells["tags"]["idle"][0]["pivot"]
    first = small[:ch, :cw]
    low = np.nonzero(first[..., 3].any(1))[0].max()
    xs = np.nonzero(first[low, :, 3] > 0)[0]
    dx = int(round((xs.min() + xs.max()) / 2)) - p0[0]
    for rows in cells["tags"].values():
        for fr in rows:
            fr["pivot"] = [fr["pivot"][0] + dx, fr["pivot"][1]]
    print("pivots moved by", dx)
    with open(lp(os.path.join(SRC, "vayne_cells.json")), "w", encoding="utf-8") as f:
        json.dump(cells, f, indent=1)
    print("written to", SRC)


if __name__ == "__main__":
    main()
