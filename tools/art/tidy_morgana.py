#!/usr/bin/env python3
"""Tidy Codex's Morgana frames (assets/source/morgana/MODEL_PROMPTS.md, 2-9) into the native strips.

    python tools/art/tidy_morgana.py <Codex's delivery folder> [--review DIR]

Codex delivered the eight animations as raw image-model sheets (its HANDOFF.md and manifest.json say so): 3x2
sheets of 1536x1024 on a magenta key, 4x2 and 2x1 sheets of 1774x887 with soft alpha, the frames in the manifest's
rectangles, tens of thousands of colours, and each sheet drawn at a scale of its own (a game pixel is 7-11 source
pixels) with the figure bigger than the cells asked for. On the game pixels of the 96x96 cells (the cells table,
assets/source/native/morgana_cells.json, and the design, assets/source/native/morgana_native.png):
  - the frames: the key and soft alpha cleared; every connected drawing goes to the rectangle holding its middle
    (the 4x2 sheets' rows touch: a foot of the top row reaches into the rectangle below);
  - the scale: per sheet, from the frames that stand (the design is 45 rows from the crest to the soles), so every
    animation is the design's size;
  - the ground: per sheet, the standing frames' lowest row goes on the cells' soles row (the pivot's row + 11), and
    every frame of the sheet keeps its height above it (the ult's rise, the death's fall);
  - the grid: every game pixel takes the colour at its centre (the median of 3x3 source pixels), the nearest of the
    design's 20 colours;
  - the head: the design's head (rows 0-19 of the design: crest, horn, hair, ear, face) replaces the drawn one,
    placed on the drawn eyes when two are found, else on the drawn hair's top and the face's middle - one face in
    every frame; not for the hit's shut eyes nor the death on the ground;
  - sideways: the eyes' middle on League's head joint of that frame (the cells table's "head"), so the lunges are
    League's; frames without eyes keep the sheet's median offset;
  - eye colour off the face becomes the gown's; lone squares go; an outline ring closes the silhouette; nothing
    below the soles row except in death (2 rows);
  - idle: the six frames are the design itself (tools/art/import_native.py adds the breath);
  - death: Codex's 4th frame (flat on the ground) and 5th (on her hands) swap places, so she goes down in one
    movement as League's head does (its 4th frame is higher than its 5th) instead of pushing up again.
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
SPEC = os.path.join(ROOT, "assets", "source", "morgana", "morgana_design.json")
DESIGN = os.path.join(NATIVE, "morgana_native.png")
CELLS = os.path.join(NATIVE, "morgana_cells.json")
TARGETS = os.path.join(ROOT, "assets", "source", "morgana", "morgana_targets.json")
Z = 8
DESIGN_ROWS = 45                          # the design: crest top to soles
HEAD_ROWS = 20                            # its rows 0-19: crest, horn, hair, ear, face (row 19 the chin)
STANDING = {"idle": None, "run": None, "attack": [0, 5], "skill": [0, 5], "skill2": [0, 5], "ult": [6, 7],
            "hit": [1], "dead": [0]}      # None: every frame
KEEP_HEAD = {("hit", 0)} | {("dead", k) for k in range(3, 8)}
LIFTED = {"run", "ult"}
FROM = {"dead": [0, 1, 2, 4, 3, 5, 6, 7]}   # Codex's frame in each cell (see the docstring)


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


with open(lp(SPEC), encoding="utf-8") as _f:
    _spec = json.load(_f)
LETTERS = list(_spec["palette"])
RGB = np.array([[int(_spec["palette"][c][i:i + 2], 16) for i in (0, 2, 4)] for c in LETTERS], float)
L = {c: k for k, c in enumerate(LETTERS)}
OUTLINE = L["#"]
EYE = L["e"]
SKIN = {L["s"], L["S"], L["k"]}
HAIR = {L["h"], L["H"], L["V"]}
FACE = SKIN | {L["e"], L["o"]}


# ----------------------------------------------------------------------------- the raw sheets
def load_sheet(path):
    a = np.asarray(Image.open(lp(path)).convert("RGBA")).astype(int)
    key = (a[..., 0] > 200) & (a[..., 1] < 70) & (a[..., 2] > 200)
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
    masks = []
    for i in range(len(rects)):
        ks = [k for k, o in owner.items() if o == i]
        masks.append(fg & np.isin(full, ks))
    return masks


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
            px = a[ry - 1:ry + 2, rx - 1:rx + 2][m][:, :3]
            c = np.median(px, axis=0)
            lab[gy, gx] = int(((RGB - c) ** 2).sum(1).argmin())
    return lab


# ----------------------------------------------------------------------------- the design and its head
def design_labels():
    a = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))[4::8, 4::8]
    lab = np.full(a.shape[:2], -1, int)
    op = a[..., 3] > 0
    lab[op] = (((a[..., :3][op][:, None, :].astype(float) - RGB[None]) ** 2).sum(-1)).argmin(1)
    return lab


def design_head(dl):
    """(block, mask, eye row, eyes' middle column) of the design's head, cut from its top HEAD_ROWS rows."""
    ys, xs = np.nonzero(dl >= 0)
    top = ys.min()
    block = dl[top:top + HEAD_ROWS]
    cols = np.nonzero((block >= 0).any(0))[0]
    block = block[:, cols.min():cols.max() + 1].copy()
    mask = block >= 0
    ey, ex = np.nonzero(block == EYE)
    return block, mask, int(ey.max()), (ex.min() + ex.max()) / 2.0


CLASS = {"#": 1, "h": 2, "H": 2, "V": 2, "s": 3, "S": 3, "k": 3, "o": 3, "y": 4, "Y": 4, "r": 5, "e": 6}
WEIGHT = {1: 0.5, 2: 1.0, 3: 1.5, 4: 2.0, 5: 2.0, 6: 3.0}


def classes(lab):
    """Label -> material class (0 clear, 7 body: gown, hem, wings, stole)."""
    table = np.array([CLASS.get(c, 7) for c in LETTERS])
    out = np.zeros(lab.shape, int)
    op = lab >= 0
    out[op] = table[lab[op]]
    return out


def find_head(lab, head, mask, rows=(0, 70)):
    """Where the design's head best fits the drawn one: the offset (y, x) that matches most of its squares by
    material (eyes, gold and the crest's red count most, the outline least), a square over clear ground costing."""
    fc = classes(lab)
    hc = classes(head)
    h, w = head.shape
    best, at = -1e9, None
    wts = np.vectorize(lambda c: WEIGHT.get(c, 0.0))(hc) * mask
    for y in range(rows[0], min(rows[1], lab.shape[0] - h)):
        for x in range(0, lab.shape[1] - w):
            win = fc[y:y + h, x:x + w]
            score = (wts * (win == hc)).sum() - 0.5 * (mask & (win == 0)).sum()
            if score > best:
                best, at = score, (y, x)
    return at, best / max(1.0, wts.sum())


def skin_from_outside(lab, box):
    """Skin squares inside `box` that reach skin outside it (an arm coming in from the shoulder)."""
    y0, y1, x0, x1 = box
    skin = np.isin(lab, list(SKIN))
    keep = np.zeros_like(skin)
    todo = [(y, x) for y, x in zip(*np.nonzero(skin)) if not (y0 <= y < y1 and x0 <= x < x1)]
    for y, x in todo:
        keep[y, x] = True
    while todo:
        y, x = todo.pop()
        for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if 0 <= ny < lab.shape[0] and 0 <= nx < lab.shape[1] and skin[ny, nx] and not keep[ny, nx]:
                keep[ny, nx] = True
                todo.append((ny, nx))
    return keep


def arms(lab, top, bottom):
    """Skin reaching into the head's rows from below (a hand raised beside the head, Black Shield's cast): skin
    groups with squares both in rows top..bottom and under them, plus the gold (bracelets) and outline squares
    touching them in those rows. A bracelet (gold with skin at most two rows above and two below) joins the hand
    to its forearm."""
    skin = np.isin(lab, list(SKIN))
    above = np.zeros_like(skin)
    below = np.zeros_like(skin)
    for d in (1, 2):
        above[d:] |= skin[:-d]
        below[:-d] |= skin[d:]
    skin |= np.isin(lab, [L["y"], L["Y"]]) & above & below
    out = np.zeros_like(skin)
    seen = np.zeros_like(skin)
    for y0, x0 in zip(*np.nonzero(skin[top:bottom])):
        y0 += top
        if seen[y0, x0]:
            continue
        todo, g = [(y0, x0)], []
        seen[y0, x0] = True
        while todo:
            y, x = todo.pop()
            g.append((y, x))
            for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= ny < lab.shape[0] and 0 <= nx < lab.shape[1] and skin[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    todo.append((ny, nx))
        if any(y >= bottom for y, _ in g) and any(y < bottom - 2 for y, _ in g):
            for y, x in g:
                if y < bottom:
                    out[y, x] = True
    grow = np.zeros_like(out)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        grow |= np.roll(np.roll(out, dy, 0), dx, 1)
    extra = grow & np.isin(lab, [L["y"], L["Y"], OUTLINE])
    extra[:top] = False
    extra[bottom:] = False
    return out | extra


def paste_head(lab, head, mask, at):
    """The drawn head cleared round `at`, then the design's head pasted there. Cleared: the head's colours on the
    design's head and one square round it (skin coming in from outside below the chin stays: the shoulders), and
    the ones joined to them above the chin (Codex's heads are often bigger: an ear or crest sticking out); a hand
    raised beside the head stays, in front of the pasted head."""
    y, x = at
    h, w = head.shape
    box = (max(0, y - 1), min(lab.shape[0], y + h + 1), max(0, x - 2), min(lab.shape[1], x + w + 2))
    keep = skin_from_outside(lab, box)
    keep[:y + h - 2] = False
    near_head = np.zeros(lab.shape, bool)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            ys, xs = np.nonzero(mask)
            ny, nx = ys + y + dy, xs + x + dx
            ok = (ny >= 0) & (ny < lab.shape[0]) & (nx >= 0) & (nx < lab.shape[1])
            near_head[ny[ok], nx[ok]] = True
    kinds = np.isin(lab, list(HAIR | FACE) + [L["r"], L["y"], L["Y"], L["D"], L["G"]])   # D, G: the hair's shade too
    kill = near_head & (kinds | (lab == OUTLINE)) & ~keep
    above = np.zeros(lab.shape, bool)
    above[:max(0, y + h - 2), max(0, x - 8):x + w + 8] = True
    through = kinds | (lab == OUTLINE)       # the outline too: an ear's tip is walled off by it (clean() redraws it)
    todo = list(zip(*np.nonzero(kill)))
    while todo:
        yy, xx = todo.pop()
        for ny, nx in ((yy + 1, xx), (yy - 1, xx), (yy, xx + 1), (yy, xx - 1)):
            if 0 <= ny < lab.shape[0] and 0 <= nx < lab.shape[1] and above[ny, nx] and through[ny, nx] \
                    and not kill[ny, nx]:
                kill[ny, nx] = True
                todo.append((ny, nx))
    box = (0, y + h + 1) + box[2:]
    arm = arms(lab, y, y + h)
    before = lab.copy()
    lab[kill] = -1
    sub = lab[y:y + h, x:x + w]
    sub[mask] = head[mask]
    lab[arm] = before[arm]          # a hand raised beside the head stays in front of it
    # specks of one or two squares walled in by the outline round the head (an ear's shading)
    col = (lab >= 0) & (lab != OUTLINE)
    pasted = np.zeros(lab.shape, bool)
    pasted[y:y + h, x:x + w] = mask
    seen = np.zeros_like(col)
    for y0, x0 in zip(*np.nonzero(col & above)):
        if seen[y0, x0]:
            continue
        todo, g = [(y0, x0)], []
        seen[y0, x0] = True
        while todo:
            yy, xx = todo.pop()
            g.append((yy, xx))
            for ny, nx in ((yy + 1, xx), (yy - 1, xx), (yy, xx + 1), (yy, xx - 1)):
                if 0 <= ny < lab.shape[0] and 0 <= nx < lab.shape[1] and col[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    todo.append((ny, nx))
        if len(g) <= 2 and not any(pasted[p] or arm[p] for p in g):
            for p in g:
                lab[p] = -1
    # outline squares left with no colour beside them
    col = (lab >= 0) & (lab != OUTLINE)
    near = np.zeros_like(col)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            near |= np.roll(np.roll(col, dy, 0), dx, 1)
    lonely = (lab == OUTLINE) & ~near
    lonely[:box[0]] = False
    lonely[box[1]:] = False
    lab[lonely] = -1


# ----------------------------------------------------------------------------- clean-up
def shift(lab, dx, dy=0):
    out = np.full_like(lab, -1)
    ys, xs = np.nonzero(lab >= 0)
    ny, nx = ys + dy, xs + dx
    ok = (ny >= 0) & (ny < lab.shape[0]) & (nx >= 0) & (nx < lab.shape[1])
    out[ny[ok], nx[ok]] = lab[ys[ok], xs[ok]]
    return out


def clean(lab, head_box=None, floor=78):
    lab = lab.copy()
    # eye colour only on the face
    inside = np.zeros_like(lab, bool)
    if head_box is not None:
        y, x, h, w = head_box
        inside[max(0, y):y + h, max(0, x):x + w] = True
    lab[(lab == EYE) & ~inside] = L["g"]
    # nothing under the floor
    lab[floor + 1:] = -1
    # lone squares
    op = lab >= 0
    nb = np.zeros_like(op, int)
    nb[1:] += op[:-1]; nb[:-1] += op[1:]; nb[:, 1:] += op[:, :-1]; nb[:, :-1] += op[:, 1:]
    lab[op & (nb == 0)] = -1
    # a square of a colour none of its four neighbours has, inside a patch: the neighbours' majority
    for yy, xx in zip(*np.nonzero(op & (nb == 4))):
        c = lab[yy, xx]
        n4 = [lab[yy - 1, xx], lab[yy + 1, xx], lab[yy, xx - 1], lab[yy, xx + 1]]
        if c not in n4 and c not in (EYE, L["o"], OUTLINE):
            vals, cnt = np.unique(n4, return_counts=True)
            if cnt.max() >= 3:
                lab[yy, xx] = vals[cnt.argmax()]
    # one outline ring
    col = (lab >= 0) & (lab != OUTLINE)
    ring = np.zeros_like(col)
    ring[1:] |= col[:-1]; ring[:-1] |= col[1:]; ring[:, 1:] |= col[:, :-1]; ring[:, :-1] |= col[:, 1:]
    lab[ring & (lab < 0)] = OUTLINE
    lab[floor + 1:] = -1
    return lab


def to_rgba(lab):
    out = np.zeros(lab.shape + (4,), np.uint8)
    op = lab >= 0
    out[op, :3] = RGB[lab[op]].astype(np.uint8)
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
            elif (tag, k) in KEEP_HEAD and tag == "dead":   # on the ground: may dip two rows
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
    ap.add_argument("--review", help="also write every frame at 4x here, with the feet line")
    ap.add_argument("--out", default=NATIVE)
    ap.add_argument("--renders", help="native_pose's output folder: measure morgana_targets.json from it (once)")
    args = ap.parse_args()
    os.makedirs(lp(args.out), exist_ok=True)
    with open(os.path.join(args.delivery, "manifest.json"), encoding="utf-8-sig") as f:
        manifest = {a["tag"]: a for a in json.load(f)["assets"]}
    with open(lp(CELLS), encoding="utf-8") as f:
        cells = json.load(f)
    targets = load_targets(cells, args.renders)
    dl = design_labels()
    head, hmask, eye_row, eye_mid = design_head(dl)
    ys, xs = np.nonzero(dl >= 0)
    d_top, d_left = ys.min(), xs.min()
    d_eyes = np.nonzero(dl == EYE)
    design_eye_mid = (d_eyes[1].min() + d_eyes[1].max()) / 2.0
    cw, ch = cells["cell"]
    for tag, rows in cells["tags"].items():
        soles = rows[0]["pivot"][1] + 11
        frames = []
        if tag == "idle":
            for r in rows:
                lab = np.full((ch, cw), -1, int)
                y0 = soles - (ys.max() - d_top)
                x0 = int(round(r["head"][0] - (design_eye_mid - d_left)))
                block = dl[d_top:ys.max() + 1, d_left:xs.max() + 1]
                sub = lab[y0:y0 + block.shape[0], x0:x0 + block.shape[1]]
                sub[block >= 0] = block[block >= 0]
                frames.append((lab, "the design"))
        else:
            a = manifest[tag]
            img, fg = load_sheet(os.path.join(args.delivery, a["file"]))
            rects = [fr["rect"] for fr in a["frames"]]
            masks = frame_masks(fg, rects)
            order = FROM.get(tag, range(len(rects)))
            rects, masks = [rects[i] for i in order], [masks[i] for i in order]
            stand = STANDING[tag] if STANDING[tag] is not None else range(len(rects))
            hs, gs = [], []
            for k in stand:
                yy = np.nonzero(masks[k].any(1))[0]
                hs.append(yy.max() - yy.min() + 1)
                gs.append(yy.max() - rects[k][1])
            s = float(np.median(hs)) / DESIGN_ROWS
            ground = float(np.median(gs))
            offsets = []
            snapped = []
            for k, (x, y, w, h) in enumerate(rects):
                lab = snap(img, masks[k], s, y + ground, x + w / 2.0, ch, cw, soles)
                note = []
                box = None
                if (tag, k) not in KEEP_HEAD:
                    at, fit = find_head(lab, head, hmask)
                    paste_head(lab, head, hmask, at)
                    eyes_x = at[1] + eye_mid
                    dx = int(round(rows[k]["head"][0] - eyes_x))
                    offsets.append(dx)
                    note.append(f"head at ({at[1]},{at[0]}) fit {fit:.2f}, moved {dx:+d}")
                    lab = shift(lab, dx)
                    box = (at[0], at[1] + dx, head.shape[0], head.shape[1])
                snapped.append((lab, box, note))
            med = int(np.median(offsets)) if offsets else 0
            for k, (lab, box, note) in enumerate(snapped):
                if box is None:
                    lab = shift(lab, med)
                    note.append(f"kept as drawn, moved {med:+d} (the sheet's median)")
                floor = soles + (2 if tag == "dead" else 0)
                low = int(np.nonzero((lab >= 0).any(1))[0].max())
                dy = targets[tag][k] - low
                lab = shift(lab, 0, dy)
                if box is not None:
                    box = (box[0] + dy, box[1], box[2], box[3])
                note.append(f"lowest row {low} -> {targets[tag][k]}")
                frames.append((clean(lab, box, floor), "; ".join(note)))
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
