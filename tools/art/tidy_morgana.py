#!/usr/bin/env python3
"""Tidy Codex's Morgana strips (assets/source/morgana/MODEL_REDESIGN_STRIPS.md, the redesign A) into the native
strips.

    python tools/art/tidy_morgana.py <Codex's delivery folder> [--out DIR] [--review DIR]

Codex delivered the eight animations as raw image-model sheets on a magenta key (its HANDOFF.md and manifest.json,
kept as codex_model/animations_A_*, say so): 3x2 sheets of 1536x1024, 4x2 and 2x1 sheets of 1774x887, the frames
in the manifest's rectangles, tens of thousands of colours, each sheet drawn at a scale of its own (a game pixel is
4.4-7.2 source pixels). On the game pixels of the 96x96 cells (the cells table, assets/source/native/
morgana_cells.json, and the design, assets/source/native/morgana_native.png: 35x45 squares, 26 colours):
  - the key: pixels near #FF00FF cleared (the wing tips' and the eyes' own magentas are darker and stay);
  - the frames: every connected drawing goes to the rectangle holding its middle;
  - the scale: per sheet, from the frames that stand (the design is 45 rows from the horn tips to the soles);
  - the grid: every game pixel takes the colour at its centre (the median of 3x3 source pixels), the nearest of the
    design's 26 colours;
  - the face: the design's face (FACE: forehead, both lash rows, both eyes, cheeks, mouth, chin) pasted where it
    fits the drawn one best, so every frame has the same face in the eye colour; Codex's hair and horns stay - they
    move with the body (a whole pasted head floated over the shoulders in the first strips). The hit's jolt and the
    death from her knees down get the face with the eyes shut (SHUT: two short lash-coloured lines), the death's
    last frame (face down) keeps Codex's;
  - sideways: the eyes' middle on League's head joint of that frame (the cells table's "head"), so the lunges are
    League's; the hit and the death (PLANTED) take the sheet's median offset from each frame's pivot instead, as
    import_native.py stands every frame on its pivot: the body stays where Codex put it and does not slide;
  - the ground: the lowest row on the frame's target row (morgana_targets.json: the soles row, League's rise in the
    ult and the move's bob, at most 2 rows lower on the ground in death);
  - the dark purples of hair, wings and gown flattened as the design's were: a 3x3 majority (FLAT_NEED of the
    window, FLAT_PASSES times; gold, skin, the magentas and the outline kept);
  - clean-up: the eye colour only in the face; lone squares off; one outline ring; single walled-in holes filled;
    then the one-outline rules of the 18 redraws (tools/art/tidy_codex18.py on the ahri branch, from the study of
    oppi's packs): outline spurs off, the black ring inside the outline turned into the material's own dark shade,
    lone pixels to the colour their neighbours share, the face kept;
  - idle: the six frames are the design itself (tools/art/import_native.py adds the breath).
Writes assets/source/native/morgana_<tag>.png (8x, native_refs.layout grids). Then:
tools/art/import_native.py --hero morgana.
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
from native_refs import layout  # noqa: E402

NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "morgana_native.png")
CELLS = os.path.join(NATIVE, "morgana_cells.json")
TARGETS = os.path.join(ROOT, "assets", "source", "morgana", "morgana_targets.json")
Z = 8
DESIGN_ROWS = 45                          # the design: horn tips to soles
STANDING = {"idle": None, "run": None, "attack": [0, 5], "skill": [0, 5], "skill2": [0, 5], "ult": [6, 7],
            "hit": [1], "dead": [0]}      # None: every frame
LYING = {("hit", 0)} | {("dead", k) for k in range(3, 8)}   # no open-eyed upright face
SHUT = {("hit", 0)} | {("dead", k) for k in range(3, 7)}    # the face with the eyes shut (not face down: dead 8)
LIFTED = {"run", "ult"}
PLANTED = {"hit", "dead"}                 # one sideways offset from the pivot for the whole sheet: the body stays
FLAT_NEED, FLAT_PASSES = 4, 3             # the dark purples: a 3x3 majority of at least 4, three times (the design: 4)
EYE = (0xC8, 0x3C, 0xA6)                  # the eye colour: only in the eyes
# the design's face, rows and columns from its top-left square (35x45): forehead, lashes, eyes, cheeks, mouth, chin
FACE = {12: (21, 23), 13: (19, 25), 14: (18, 25), 15: (18, 25), 16: (18, 25), 17: (18, 25), 18: (19, 25), 19: (20, 24)}
DARK = 40                                 # luma under this is black (outline, black shadow)
N4 = ((0, 1), (0, -1), (1, 0), (-1, 0))
N8 = N4 + ((1, 1), (1, -1), (-1, 1), (-1, -1))


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def design():
    """(labels of the design on its canvas, palette RGB (k x 3), top, left) - one label per colour."""
    a = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))[4::8, 4::8]
    op = a[..., 3] > 0
    pal = np.unique(a[op][:, :3], axis=0)
    lab = np.full(op.shape, -1, int)
    lab[op] = [int(np.flatnonzero((pal == c).all(1))[0]) for c in a[op][:, :3]]
    ys, xs = np.nonzero(op)
    return lab, pal.astype(float), ys.min(), xs.min()


DLAB, PAL, DTOP, DLEFT = design()
EYE_I = int(np.flatnonzero((PAL == np.array(EYE)).all(1))[0])
LUMA = PAL @ np.array([0.299, 0.587, 0.114])
SKIN = set(np.flatnonzero((LUMA > 150) & (PAL[:, 2] > PAL[:, 0] - 40)))                   # pink skin, white
MAGENTA = set(np.flatnonzero((PAL[:, 0] > 140) & (PAL[:, 1] < 90) & (PAL[:, 2] > 110)))   # the eyes and wing tips


def outline_colour():
    """The design's outline: the commonest colour on the edge of its silhouette."""
    op = DLAB >= 0
    edge = op & ~(np.roll(op, 1, 0) & np.roll(op, -1, 0) & np.roll(op, 1, 1) & np.roll(op, -1, 1))
    return int(np.bincount(DLAB[edge]).argmax())


OUTLINE = outline_colour()
# kept as drawn by the flattening (as for the design, work of the redesign): gold, skin, the magentas, the outline
R_, G_, B_ = PAL[:, 0], PAL[:, 1], PAL[:, 2]
FIXED = set(np.flatnonzero(((R_ > B_ + 20) & (LUMA > 70)) | (LUMA > 150) |
                           ((R_ > 110) & (G_ < 70) & (B_ > 90) & (R_ > B_ - 30)))) | {OUTLINE}


def face_patch():
    """(rows, cols, labels) of the face in design coordinates, the same with the eyes shut (two short dark lines on
    the eyes' upper row, the lashes gone), and the eyes' middle column."""
    pts = [(r, c, DLAB[DTOP + r, DLEFT + c]) for r, (c0, c1) in FACE.items() for c in range(c0, c1)]
    ex = [(r, c) for r, c, v in pts if v == EYE_I]
    top = min(r for r, _ in ex)
    skin = max(SKIN, key=lambda v: int((DLAB == v).sum()))
    lash = DLAB[DTOP + top - 1, DLEFT + min(c for _, c in ex)]
    eye_cols = {c for _, c in ex}
    shut = []
    for r, c, v in pts:
        if top - 1 <= r <= top + 1 and c in eye_cols:
            v = lash if r == top else skin
        shut.append((r, c, v))
    return pts, shut, (min(eye_cols) + max(eye_cols)) / 2.0


FACE_PTS, SHUT_PTS, FACE_EYE_MID = face_patch()


# ----------------------------------------------------------------------------- the raw sheets
def load_sheet(path):
    a = np.asarray(Image.open(lp(path)).convert("RGBA")).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    key = (r > 170) & (b > 170) & (g < 110) & (np.abs(r - b) < 70)
    return a, (a[..., 3] >= 128) & ~key


def frame_masks(fg, rects, step=4):
    """Per rectangle, the foreground that belongs to it: connected drawings (8-connected on a coarse grid of
    step x step blocks) go to the rectangle that holds their middle."""
    H, W = fg.shape
    h, w = -(-H // step), -(-W // step)
    pad = np.zeros((h * step, w * step), bool)
    pad[:H, :W] = fg
    coarse = pad.reshape(h, step, w, step).any((1, 3))
    lab = np.zeros((h, w), int)
    n = 0
    for y0, x0 in zip(*np.nonzero(coarse)):
        if lab[y0, x0]:
            continue
        n += 1
        todo = [(y0, x0)]
        lab[y0, x0] = n
        while todo:
            y, x = todo.pop()
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h and 0 <= nx < w and coarse[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = n
                        todo.append((ny, nx))
    owner = {}
    for k in range(1, n + 1):
        ys, xs = np.nonzero(lab == k)
        cy, cx = (ys.mean() + 0.5) * step, (xs.mean() + 0.5) * step
        for i, (x, y, rw, rh) in enumerate(rects):
            if x <= cx < x + rw and y <= cy < y + rh:
                owner[k] = i
                break
    full = np.kron(lab, np.ones((step, step), int))[:H, :W]
    return [fg & np.isin(full, [k for k, o in owner.items() if o == i]) for i in range(len(rects))]


def snap(a, mask, s, ground, cx, rows=96, cols=96, soles=78):
    """Game-pixel labels (-1 clear) of one frame: game row `soles` is the raw row `ground` (the lowest drawn one),
    game column 48 is raw column cx, a game pixel is s raw pixels."""
    lab = np.full((rows, cols), -1, int)
    H, W = mask.shape
    for gy in range(rows):
        ry = int(ground + 1 - (soles + 0.5 - gy) * s)
        if ry < 1 or ry >= H - 1:
            continue
        for gx in range(cols):
            rx = int(cx + (gx - 48 + 0.5) * s)
            if rx < 1 or rx >= W - 1:
                continue
            m = mask[ry - 1:ry + 2, rx - 1:rx + 2]
            if m.sum() < 5:
                continue
            c = np.median(a[ry - 1:ry + 2, rx - 1:rx + 2][m][:, :3], axis=0)
            lab[gy, gx] = int(((PAL - c) ** 2).sum(1).argmin())
    return lab


# ----------------------------------------------------------------------------- the face
def kind(v):
    """0 clear, 1 skin, 2 eye (any of the magentas), 3 dark, 4 other."""
    if v < 0:
        return 0
    if v in SKIN:
        return 1
    if v in MAGENTA:
        return 2
    if LUMA[v] < 50:
        return 3
    return 4


def find_face(lab, pts):
    """(score, y, x): where the face `pts` (its top-left corner in design coordinates at y, x of the frame) fits
    the drawn face best - eyes count most, then skin and dark; clear squares cost. For the shut face any eye or dark
    square counts for its lines (Codex drew the shut eyes in either)."""
    K = np.vectorize(kind)(lab)
    shut = pts is SHUT_PTS
    if shut:
        K[K == 2] = 3
    want = [(r, c, kind(v), {1: 1.0, 2: 3.0, 3: 3.0 if shut else 1.0}.get(kind(v), 0.5)) for r, c, v in pts]
    best = (-1e9, 0, 0)
    for y in range(-12, 60):
        for x in range(-18, 96 - 25):
            sc = 0.0
            for r, c, k, w in want:
                yy, xx = y + r, x + c
                if not (0 <= yy < 96 and 0 <= xx < 96):
                    sc -= 1.0
                    continue
                f = K[yy, xx]
                sc += w if f == k else (-0.5 if f == 0 else 0.0)
            if sc > best[0]:
                best = (sc, y, x)
    return best


def paste_face(lab, pts, y, x):
    for r, c, v in pts:
        if 0 <= y + r < lab.shape[0] and 0 <= x + c < lab.shape[1]:
            lab[y + r, x + c] = v


def flatten(lab, keep):
    """The dark purples of hair, wings and gown flattened as for the design: a square not of the FIXED colours takes
    the colour at least FLAT_NEED of the 3x3 around it share (FIXED colours not counted), FLAT_PASSES times; `keep`
    untouched."""
    H, W = lab.shape
    fixed = np.isin(lab, list(FIXED))
    for _ in range(FLAT_PASSES):
        new = lab.copy()
        for y in range(1, H - 1):
            for x in range(1, W - 1):
                v = lab[y, x]
                if v < 0 or fixed[y, x] or keep[y, x]:
                    continue
                win = lab[y - 1:y + 2, x - 1:x + 2][~fixed[y - 1:y + 2, x - 1:x + 2]]
                win = win[win >= 0]
                vals, cnt = np.unique(win, return_counts=True)
                j = int(np.argmax(cnt))
                if vals[j] != v and cnt[j] >= FLAT_NEED:
                    new[y, x] = vals[j]
        lab = new
    return lab


# ----------------------------------------------------------------------------- clean-up
def shift(lab, dx, dy=0):
    out = np.full_like(lab, -1)
    ys, xs = np.nonzero(lab >= 0)
    ny, nx = ys + dy, xs + dx
    ok = (ny >= 0) & (ny < lab.shape[0]) & (nx >= 0) & (nx < lab.shape[1])
    out[ny[ok], nx[ok]] = lab[ys[ok], xs[ok]]
    return out


def clean(lab, face, floor):
    """face: a mask of the pasted face (the eye colour allowed only there)."""
    lab = lab.copy()
    # the eye colour off the face: the colour most of its non-eye neighbours have
    for yy, xx in zip(*np.nonzero((lab == EYE_I) & ~face)):
        n = [lab[yy + dy, xx + dx] for dy, dx in N8 if 0 <= yy + dy < lab.shape[0] and 0 <= xx + dx < lab.shape[1]]
        n = [v for v in n if v >= 0 and v != EYE_I]
        lab[yy, xx] = max(set(n), key=n.count) if n else -1
    lab[floor + 1:] = -1
    # lone squares
    op = lab >= 0
    nb = np.zeros_like(op, int)
    nb[1:] += op[:-1]; nb[:-1] += op[1:]; nb[:, 1:] += op[:, :-1]; nb[:, :-1] += op[:, 1:]
    lab[op & (nb == 0)] = -1
    # one outline ring
    col = (lab >= 0) & (lab != OUTLINE)
    ring = np.zeros_like(col)
    ring[1:] |= col[:-1]; ring[:-1] |= col[1:]; ring[:, 1:] |= col[:, :-1]; ring[:, :-1] |= col[:, 1:]
    lab[ring & (lab < 0)] = OUTLINE
    # a single clear square walled in on all four sides: the walls' majority
    op = lab >= 0
    for yy, xx in zip(*np.nonzero(~op[1:-1, 1:-1])):
        yy, xx = yy + 1, xx + 1
        n4 = [lab[yy - 1, xx], lab[yy + 1, xx], lab[yy, xx - 1], lab[yy, xx + 1]]
        if min(n4) >= 0:
            lab[yy, xx] = max(set(n4), key=n4.count)
    lab[floor + 1:] = -1
    return one_outline(lab, face)


def shifted(m, dy, dx):
    out = np.zeros_like(m)
    H, W = m.shape
    ys, yd = (slice(0, H - dy), slice(dy, H)) if dy >= 0 else (slice(-dy, H), slice(0, H + dy))
    xs, xd = (slice(0, W - dx), slice(dx, W)) if dx >= 0 else (slice(-dx, W), slice(0, W + dx))
    out[yd, xd] = m[ys, xs]
    return out


def one_outline(lab, keep):
    """The one-outline rules of the 18 redraws on labels: outline spurs off (a black square with at most one
    neighbour), the black ring right inside the outline turned into the darkest of its brighter neighbours (the
    material's own dark shade), lone squares to the colour 3 of their 4 neighbours share; `keep` untouched."""
    lab = lab.copy()
    L = np.where(lab >= 0, LUMA[np.maximum(lab, 0)], 255)
    for _ in range(2):
        op = lab >= 0
        cnt = sum(shifted(op, dy, dx).astype(int) for dy, dx in N4)
        lab[op & (L < DARK) & (cnt <= 1) & ~keep] = -1
    op = lab >= 0
    edge = np.zeros_like(op)
    for dy, dx in N4:
        edge |= op & ~shifted(op, dy, dx)
    ring2 = np.zeros_like(op)
    for dy, dx in N4:
        ring2 |= shifted(edge, dy, dx)
    ring2 &= op & ~edge & (L < DARK) & ~keep
    out = lab.copy()
    H, W = lab.shape
    for y, x in zip(*np.nonzero(ring2)):
        n = [lab[y + dy, x + dx] for dy, dx in N8
             if 0 <= y + dy < H and 0 <= x + dx < W and lab[y + dy, x + dx] >= 0 and L[y + dy, x + dx] >= DARK]
        if len(n) >= 2:
            out[y, x] = min(n, key=lambda v: (LUMA[v], -n.count(v)))
    lab = out
    op = lab >= 0
    out = lab.copy()
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if not op[y, x] or keep[y, x]:
                continue
            n4 = [lab[y + dy, x + dx] for dy, dx in N4]
            if lab[y, x] in n4 or min(n4) < 0:
                continue
            best = max(set(n4), key=n4.count)
            if n4.count(best) >= 3:
                out[y, x] = best
    return out


def to_rgba(lab):
    out = np.zeros(lab.shape + (4,), np.uint8)
    op = lab >= 0
    out[op, :3] = PAL[lab[op]].astype(np.uint8)
    out[op, 3] = 255
    return out


def load_targets(cells, renders=None):
    """Per frame, the row its lowest square goes to: the soles row, but League's frame's lowest row (native_pose's
    morgana_native_<tag>.png, game pixels at 8x on grey) where she leaves the ground (the ult's rise, the walk's
    bob; never under the soles row) and in the death on the ground (at most two rows under). Codex drew Q and E
    standing, where League hops.
    Measured once from the renders (local only: Riot's model) and kept in morgana_targets.json."""
    if renders is None and os.path.exists(lp(TARGETS)):
        with open(lp(TARGETS), encoding="utf-8") as f:
            return json.load(f)
    if renders is None:
        sys.exit("no morgana_targets.json yet: pass --renders <native_pose output folder> once")
    cw, ch = cells["cell"]
    out = {}
    for tag, rows in cells["tags"].items():
        a = np.asarray(Image.open(os.path.join(renders, f"morgana_native_{tag}.png")).convert("RGB"))[4::8, 4::8].astype(int)
        fig = np.abs(a - 225).sum(2) > 0
        gc, _ = layout(len(rows))
        soles = rows[0]["pivot"][1] + 11
        lows = []
        for k in range(len(rows)):
            c, r = k % gc, k // gc
            ys = np.nonzero(fig[r * ch:(r + 1) * ch, c * cw:(c + 1) * cw].any(1))[0]
            if tag in LIFTED:                  # League's rise (the ult) and the walk's bob
                lows.append(int(min(ys.max(), soles)))
            elif (tag, k) in LYING and tag == "dead":   # on the ground: may dip two rows
                lows.append(int(min(ys.max(), soles + 2)))
            else:                              # Codex drew her standing: on the soles row
                lows.append(soles)
        out[tag] = lows
    with open(lp(TARGETS), "w", encoding="utf-8", newline=chr(10)) as f:
        f.write("{" + chr(10) + ("," + chr(10)).join(f'  "{t}": {json.dumps(v)}' for t, v in out.items()) + chr(10) + "}" + chr(10))
    return out


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("delivery")
    ap.add_argument("--review", help="also write every strip at 4x here")
    ap.add_argument("--out", default=NATIVE)
    ap.add_argument("--renders", help="native_pose's output folder: measure morgana_targets.json from it (once)")
    args = ap.parse_args()
    os.makedirs(lp(args.out), exist_ok=True)
    with open(os.path.join(args.delivery, "manifest.json"), encoding="utf-8-sig") as f:
        manifest = {a["tag"]: a for a in json.load(f)["assets"]}
    with open(lp(CELLS), encoding="utf-8") as f:
        cells = json.load(f)
    targets = load_targets(cells, args.renders)
    ys, xs = np.nonzero(DLAB >= 0)
    d_top, d_bot, d_left, d_right = ys.min(), ys.max(), xs.min(), xs.max()
    block = DLAB[d_top:d_bot + 1, d_left:d_right + 1]
    cw, ch = cells["cell"]
    for tag, rows in cells["tags"].items():
        soles = rows[0]["pivot"][1] + 11
        frames = []
        if tag == "idle":
            for r in rows:
                lab = np.full((ch, cw), -1, int)
                y0 = soles - (d_bot - d_top)
                x0 = int(round(r["head"][0] - FACE_EYE_MID))
                sub = lab[y0:y0 + block.shape[0], x0:x0 + block.shape[1]]
                sub[block >= 0] = block[block >= 0]
                frames.append((lab, "the design"))
        else:
            a = manifest[tag]
            img, fg = load_sheet(os.path.join(args.delivery, a["file"]))
            rects = [fr["rect"] for fr in a["frames"]]
            masks = frame_masks(fg, rects)
            stand = STANDING[tag] if STANDING[tag] is not None else range(len(rects))
            hs, gs = [], []
            for k in stand:
                yy = np.nonzero(masks[k].any(1))[0]
                hs.append(yy.max() - yy.min() + 1)
                gs.append(yy.max() - rects[k][1])
            s = float(np.median(hs)) / DESIGN_ROWS
            ground = float(np.median(gs))
            snapped, offsets = [], []
            for k, (x, y, w, h) in enumerate(rects):
                lab = snap(img, masks[k], s, y + ground, x + w / 2.0, ch, cw, soles)
                note, face, dx = [], None, None
                pts = SHUT_PTS if (tag, k) in SHUT else None if (tag, k) in LYING else FACE_PTS
                if pts is not None:
                    sc, fy, fx = find_face(lab, pts)
                    paste_face(lab, pts, fy, fx)
                    face = (fy, fx)
                    note.append(f"{'shut ' if pts is SHUT_PTS else ''}face at ({fx},{fy}) score {sc:.0f}")
                    if pts is FACE_PTS:
                        dx = int(round(rows[k]["head"][0] - (fx + FACE_EYE_MID)))
                        offsets.append(dx - rows[k]["pivot"][0])
                else:
                    note.append("face down: as drawn")
                snapped.append((lab, face, dx, note))
            med = int(np.median(offsets)) if offsets else 0
            for k, (lab, face, dx, note) in enumerate(snapped):
                if dx is None or tag in PLANTED:       # the game stands every frame on its pivot
                    dx = med + rows[k]["pivot"][0]
                    note.append(f"moved {dx:+d} (the sheet's median from the pivot)")
                else:
                    note.append(f"moved {dx:+d} (the eyes on League's head)")
                lab = shift(lab, dx)
                floor = max(soles, targets[tag][k])     # on the ground in death: down to its target row
                low = int(np.nonzero((lab >= 0).any(1))[0].max())
                dy = targets[tag][k] - low
                lab = shift(lab, 0, dy)
                keep = np.zeros(lab.shape, bool)
                if face is not None:
                    for r, c, _ in FACE_PTS:
                        yy, xx = face[0] + dy + r, face[1] + dx + c
                        if 0 <= yy < ch and 0 <= xx < cw:
                            keep[yy, xx] = True
                note.append(f"lowest row {low} -> {targets[tag][k]}")
                frames.append((clean(flatten(lab, keep), keep, floor), "; ".join(note)))
            print(f"{tag}: scale {s:.2f} source px a game pixel, ground {ground:.0f} px into the cells")
        n = len(frames)
        gc, gr = layout(n)
        strip = np.zeros((gr * ch, gc * cw, 4), np.uint8)
        for k, (lab, note) in enumerate(frames):
            cx, cy = k % gc, k // gc
            strip[cy * ch:(cy + 1) * ch, cx * cw:(cx + 1) * cw] = to_rgba(lab)
            print(f"  {tag} {k + 1}: {note}")
        Image.fromarray(strip, "RGBA").resize((gc * cw * Z, gr * ch * Z), Image.NEAREST).save(
            lp(os.path.join(args.out, f"morgana_{tag}.png")))
        if args.review:
            os.makedirs(args.review, exist_ok=True)
            Image.fromarray(strip, "RGBA").resize((gc * cw * 4, gr * ch * 4), Image.NEAREST).save(
                os.path.join(args.review, f"morgana_{tag}_4x.png"))


if __name__ == "__main__":
    main()
