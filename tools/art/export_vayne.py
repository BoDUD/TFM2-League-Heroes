#!/usr/bin/env python3
"""Export Codex's raw strips of Vayne to game pixels with the design's FACE pasted, not its whole head.

    python tools/art/export_vayne.py <strips_raw folder> <delivery folder> <out folder>

Codex's own export (VayneExport.cs in its work folder) samples each raw generation (magenta ground, ~10 px squares)
onto the 96x96 cells - the square pitch from the standing frame (48 rows), the frame placed by its drawn lenses and
its feet - then, before pasting the design's head, clears every hair, skin and bodysuit square round the eyes (30 rows
above them, 6 below): the neck and the collar under the chin went with them and the pasted head sat on the body like a
sticker (the user: "头和身体有点分离" "不协调"; league_morgana's first strips the same, "头和身体像分离").
This is the same export, square for square (the pitch, the boxes, the placement, the 3x3 median, the palette without
the lens reds, the design itself in the last frames, the specks, the feet line), except the head: nothing is cleared,
Codex's drawn hair, head, neck and collar stay with the body, and only the design's face - the glasses (lenses, their
shade and frame), the face's skin, its profile and the mouth, under the fringe and above the collar - is pasted where
Codex's own face is, so the glasses and the mouth are the same in every frame while the head moves with the body
(Morgana's fix and tidy_codex18's for the 18: paste only the face). Codex's eye marks are no guide to that: they were
off by up to 10 squares (Condemn's shot, the fall) and a face pasted there left the drawn one beside it, two faces;
the face is looked for by colour within REACH of the mark (the design's match box round its lenses, the lenses in the cape's red that
Codex's own lenses become once snapped) and pasted where it matches best, and Codex's lens squares left round it go.
The rolls' tucked frames and the lying death keep Codex's drawing, as before, and so does HIDDEN (her head thrown
back as she falls: the upright face turned her chin into a second one).
The size is the design's (assets/source/native/vayne_native.png): Codex drew for 48 rows, the user then found her a
head too tall in game and picked 40 (tools/art/shrink_vayne.py deletes whole rows and columns of the 48-row design,
never the face's). Every sheet's square pitch is its standing frame's height over the design's rows, so the raw
drawings are read at the new size straight from their own squares; the face, the boxes round it and the design's
place on the canvas are measured on the design (from its lenses), and the idle strip is the design in the
delivery idle's places (soles on the feet line, the same middle).
Writes <out>/vayne_<tag>.png (8x), native/vayne_<tag>_1x.png and manifest.json (the delivery's, with each frame's
exact_head_origin replaced by face_origin: the cell offset of the 128 canvas the face was cut from, like Codex's
headOrigin); then run tidy_vayne.py on <out>.
"""
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "native")
LENS = {(0xF8, 0x30, 0x3C), (0xB0, 0x10, 0x2A)}
# the face under the fringe: skin and its shade, the lenses and their dark shade, the mouth, and the outline blacks
# of the glasses' frame and the profile; not the hair, the chin's hair-dark contour or the collar's reds
FACE_COLOURS = {(0xFB, 0xD7, 0xBF), (0xBE, 0x92, 0x82), (0xF8, 0x30, 0x3C), (0xB0, 0x10, 0x2A), (0x24, 0x06, 0x11),
                (0x92, 0x01, 0x15), (0x0B, 0x04, 0x10), (0x0D, 0x05, 0x13)}
# boxes from the design's lens centre (x0, y0, x1, y1; on the 48-row design, lenses at 24.89, 12.56: the face 21-29 x
# 10-17, the match 20-30 x 9-17): the face is the same square for square at every size
FACE_REL = (-3.8889, -2.5556, 4.1111, 4.4444)       # the face under the fringe, pasted
MATCH_REL = (-4.8889, -3.5556, 5.1111, 4.4444)      # the face and the fringe's edge round it: looked for in each frame
DRAWN_LENS = (0xCD, 0x06, 0x2B)        # Codex's own lenses once snapped (the palette has no lens reds): the cape's red
REACH = 10                             # how far from Codex's eye mark the face is looked for, in squares
FACE_OK = 130                          # mean colour distance over the match box above which the face is not found (Vayne's
                                       # upright faces 14-97, the falling ones 102-126)
HIDDEN = {"dead": (1,)}                # frames (1-based) whose drawn face stays: her head thrown back as she falls
TAGS =["attack", "attack_q", "run", "skill", "skill_back", "skill2", "ult", "hit", "dead"]


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


class Design:
    """The design on its 128 canvas, 1x, and what is measured on it: its corner and rows, the lens centre, the face,
    match and head boxes (canvas coordinates)."""

    def __init__(self, path=None):
        c = np.asarray(Image.open(lp(path or os.path.join(SRC, "vayne_native.png"))).convert("RGBA"))[4::8, 4::8]
        self.canvas = c.copy()
        ys, xs = np.nonzero(c[..., 3] > 0)
        self.at = (int(xs.min()), int(ys.min()))
        self.height = int(ys.max() - ys.min() + 1)
        lens = np.zeros(c.shape[:2], bool)
        for col in LENS:
            lens |= (c[..., :3] == col).all(-1) & (c[..., 3] > 0)
        ly, lx = np.nonzero(lens)
        self.lens = (float(lx.mean()), float(ly.mean()))
        box = lambda r: tuple(int(round(self.lens[k % 2] + r[k])) for k in range(4))  # noqa: E731
        self.face_box, self.match_box = box(FACE_REL), box(MATCH_REL)
        # the head Codex pasted: its specks stay, as in Codex's export (12 columns behind the lenses at 48 rows)
        self.head_box = (int(round(self.lens[0] - 12 * self.height / 48)), self.at[1], int(round(self.lens[0] + 8)),
                         self.face_box[3])


def face_patch(design):
    """The face's pixels as (x, y, rgba) on the 128 canvas."""
    fx0, fy0, fx1, fy1 = design.face_box
    face = []
    for y in range(fy0, fy1 + 1):
        for x in range(fx0, fx1 + 1):
            c = design.canvas[y, x]
            if c[3] and tuple(int(v) for v in c[:3]) in FACE_COLOURS:
                face.append((x, y, c.copy()))
    return face


def match_template(design):
    """The face as Codex's frames have it once snapped: the design's match box, its lens reds as the cape's red."""
    x0, y0, x1, y1 = design.match_box
    t = design.canvas[y0:y1 + 1, x0:x1 + 1].copy()
    for c in LENS:
        t[(t[..., :3] == c).all(-1) & (t[..., 3] > 0), :3] = DRAWN_LENS
    return t


def locate(cell, tmpl, guess):
    """(mean colour distance, x, y): the best place for the template's corner within REACH of guess (the nearer
    of two equal places)."""
    m = tmpl[..., 3] > 0
    th, tw = tmpl.shape[:2]
    best = (1e9, 0, 0)
    for y in range(guess[1] - REACH, guess[1] + REACH + 1):
        for x in range(guess[0] - REACH, guess[0] + REACH + 1):
            if x < 0 or y < 0 or x + tw > cell.shape[1] or y + th > cell.shape[0]:
                continue
            win = cell[y:y + th, x:x + tw]
            d = np.sqrt(((win[..., :3].astype(float) - tmpl[..., :3]) ** 2).sum(-1))
            d[win[..., 3] == 0] = 255
            s = float(d[m].mean()) + 0.01 * (abs(x - guess[0]) + abs(y - guess[1]))
            if s < best[0]:
                best = (s, x, y)
    return best


def scrub(cell, box, pasted, margin=2):
    """Codex's own lenses where they stick out of the pasted face (the cape's red within `margin` of it) take the
    commonest other colour round them."""
    x0, y0, x1, y1 = box
    lens = lambda y, x: cell[y, x, 3] > 0 and tuple(int(v) for v in cell[y, x, :3]) == DRAWN_LENS  # noqa: E731
    n = 0
    for _ in range(2):
        for y in range(max(0, y0 - margin), min(96, y1 + margin + 1)):
            for x in range(max(0, x0 - margin), min(96, x1 + margin + 1)):
                if pasted[y, x] or not lens(y, x):
                    continue
                nb = [tuple(int(v) for v in cell[y + dy, x + dx]) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                      if (dy or dx) and 0 <= y + dy < 96 and 0 <= x + dx < 96 and cell[y + dy, x + dx, 3] > 0
                      and not lens(y + dy, x + dx)]
                if nb:
                    cell[y, x] = max(set(nb), key=nb.count)
                    n += 1
    return n


def key(a):
    """Codex's Key: transparent, the magenta ground and its fringes (a boolean array over an RGBA image)."""
    r, g, b, al = (a[..., k].astype(int) for k in range(4))
    mag = (r > 140) & (b > 120) & (r - g > 65) & (b - g > 65)
    fringe = (r >= 70) & (b >= 50) & (b > g * 1.7) & (r > g * 2) & (b > r * 0.5)
    return (al < 128) | mag | fringe


def box(k, left, top, right, bottom):
    ys, xs = np.nonzero(~k[top:bottom, left:right])
    return left + xs.min(), top + ys.min(), left + xs.max() + 1, top + ys.max() + 1


def refine_eye(a, k, x, y, pitch):
    """Codex's RefineEye: the centroid of the drawn lenses' reds near the eye it marked."""
    rad = int(max(10, pitch * 3.5))
    y0, y1 = max(0, int(y) - rad), min(a.shape[0], int(y) + rad)
    x0, x1 = max(0, int(x) - rad), min(a.shape[1], int(x) + rad)
    sub = a[y0:y1, x0:x1].astype(int)
    r, g, b = sub[..., 0], sub[..., 1], sub[..., 2]
    ys, xs = np.nonzero(~k[y0:y1, x0:x1] & (r > 155) & (g < 100) & (b < 110) & (r > g * 1.7))
    if len(ys) > 3:
        return x0 + xs.mean(), y0 + ys.mean()
    return x, y


class Palette:
    """Codex's Snap: the nearest design colour, green weighted, never the lens reds."""

    def __init__(self, design_c):
        cols = sorted({tuple(int(v) for v in c) for c in design_c[design_c[..., 3] > 0][:, :3]})
        self.cols = [c for c in cols if c not in LENS]
        self.arr = np.array(self.cols, float)

    def snap(self, rgb):
        d = ((self.arr - rgb) ** 2 * np.array([2.0, 3.0, 2.0])).sum(1)
        return self.cols[int(np.argmin(d))]


def sample(a, k, pal, x, y):
    """Codex's Sample: clear on the ground, else the 3x3 per-channel median snapped to the palette."""
    ix, iy = int(round(x)), int(round(y))
    if ix < 0 or iy < 0 or ix >= a.shape[1] or iy >= a.shape[0] or k[iy, ix]:
        return None
    ys, xs = slice(max(0, iy - 1), iy + 2), slice(max(0, ix - 1), ix + 2)
    win = a[ys, xs][~k[ys, xs]][:, :3]
    return pal.snap(np.sort(win, axis=0)[len(win) // 2].astype(float))


def clean_specks(cell, protect):
    """Codex's CleanSpecks: 8-connected pieces of at most 9 squares go, unless they touch a protected square."""
    op = cell[..., 3] > 0
    seen = np.zeros(op.shape, bool)
    H, W = op.shape
    for sy, sx in zip(*np.nonzero(op)):
        if seen[sy, sx]:
            continue
        stack, pts, prot = [(sy, sx)], [], False
        seen[sy, sx] = True
        while stack:
            y, x = stack.pop()
            pts.append((y, x))
            prot |= bool(protect[y, x])
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < H and 0 <= xx < W and op[yy, xx] and not seen[yy, xx]:
                        seen[yy, xx] = True
                        stack.append((yy, xx))
        if len(pts) <= 9 and not prot:
            for y, x in pts:
                cell[y, x] = 0


def export_cell(a, k, pal, bx, eye, pitch, tag, i, n, piv, target_x, design, face, tmpl):
    """One 96x96 cell as VayneExport.Export draws it, the face pasted instead of the head where Codex's own face is
    found near its eye mark; (cell, face origin or None, match distance or None, lens squares scrubbed)."""
    ex, ey = eye
    use_face = not (tag in ("skill", "skill_back") and 1 <= i <= 3) and not (tag == "dead" and i >= 4)
    target_bottom = 83 if (tag == "dead" and i >= 3) else 81
    if tag in ("skill", "skill_back") and 1 <= i <= 3:
        target_bottom = 79
    target_ex = piv[0] - 7 if tag == "run" else round(target_x) - 9
    tx = target_ex - ex / pitch
    # every body stands on the feet line - the run too since its redraw (vayne_run_redo): Codex's first export hung the
    # run from its eyes (row 47, 48 in frames 2 and 6), and the redrawn run's head sits 1-2 rows higher over its soles,
    # which that put under the feet line
    ty = target_bottom - (bx[3] - 1) / pitch
    cell = np.zeros((96, 96, 4), np.uint8)
    for y in range(96):
        ry = (y - ty) * pitch
        if ry < bx[1] or ry >= bx[3]:
            continue
        for x in range(96):
            rx = (x - tx) * pitch
            if rx < bx[0] or rx >= bx[2]:
                continue
            c = sample(a, k, pal, rx, ry)
            if c is not None:
                cell[y, x, :3], cell[y, x, 3] = c, 255
    # the cell offset of the canvas: the design's lens centre on Codex's (refined) eye mark
    hx = int(round(target_ex - design.lens[0]))
    hy = int(round(ey / pitch + ty - design.lens[1]))
    protect = np.zeros((96, 96), bool)
    origin = score = None
    scrubbed = 0

    def keep_head():
        x0, y0, x1, y1 = design.head_box
        protect[max(0, y0 + hy):max(0, y1 + hy + 1), max(0, x0 + hx):max(0, x1 + hx + 1)] = True

    if use_face:
        # Codex's eye marks are off by up to 10 squares in the fall and Condemn's shot (its whole-head paste cleared
        # the drawn head, so it never showed): the face goes where Codex's own face is, found by colour near the mark
        mx, my = design.match_box[:2]
        score, fx, fy = locate(cell, tmpl, (hx + mx, hy + my))
        if i + 1 in HIDDEN.get(tag, ()):
            score = None
            keep_head()
        elif score <= FACE_OK:
            hx, hy = fx - mx, fy - my
            pasted = np.zeros((96, 96), bool)
            for x, y, c in face:
                xx, yy = x + hx, y + hy
                if 0 <= xx < 96 and 0 <= yy < 96:
                    cell[yy, xx] = c
                    pasted[yy, xx] = True
            fx0, fy0, fx1, fy1 = design.face_box
            scrubbed = scrub(cell, (fx0 + hx, fy0 + hy, fx1 + hx, fy1 + hy), pasted)
            keep_head()
            origin = [hx, hy]
    if (i == n - 1 or (tag == "attack" and i == n - 2)) and tag not in ("run", "dead"):
        cell[:] = 0                     # Codex's exact return to the design stance (its soles on canvas row 99)
        ddx, ddy = piv[0] - 73, -18
        for y, x in zip(*np.nonzero(design.canvas[..., 3] > 0)):
            if 0 <= y + ddy < 96 and 0 <= x + ddx < 96:
                cell[y + ddy, x + ddx] = design.canvas[y, x]
                protect[y + ddy, x + ddx] = True
        origin = score = None
    clean_specks(cell, protect)
    cell[target_bottom + 1:] = 0
    return cell, origin, score, scrubbed


def idle(delivery, design, out):
    """The idle strip: the design in every cell where the delivery's idle has the design Codex drew for (the soles on
    the same row, the same middle column) - the delivery's own idle when the design is that one."""
    a = np.asarray(Image.open(os.path.join(delivery, "native", "vayne_idle_1x.png")).convert("RGBA"))
    ys, xs = np.nonzero(design.canvas[..., 3] > 0)
    fig = design.canvas[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    res = np.zeros_like(a)
    for cy in range(0, a.shape[0], 96):
        for cx in range(0, a.shape[1], 96):
            cell = a[cy:cy + 96, cx:cx + 96]
            yy, xx = np.nonzero(cell[..., 3] > 0)
            if not len(yy):
                continue
            x0 = int(round((xx.min() + xx.max() + 1) / 2 - fig.shape[1] / 2))
            y0 = yy.max() + 1 - fig.shape[0]
            res[cy + y0:cy + y0 + fig.shape[0], cx + x0:cx + x0 + fig.shape[1]] = fig
    Image.fromarray(res).save(os.path.join(out, "native", "vayne_idle_1x.png"))
    Image.fromarray(np.repeat(np.repeat(res, 8, 0), 8, 1)).save(os.path.join(out, "vayne_idle.png"))


def main():
    raw_dir, delivery, out = sys.argv[1:4]
    design = Design()
    pal = Palette(design.canvas)
    face = face_patch(design)
    tmpl = match_template(design)
    eyes = json.load(open(os.path.join(raw_dir, "strip_eyes.json"), encoding="utf-8-sig"))
    man = json.load(open(os.path.join(delivery, "manifest.json"), encoding="utf-8-sig"))
    os.makedirs(os.path.join(out, "native"), exist_ok=True)
    shutil.copyfile(os.path.join(delivery, "vayne_cells.json"), os.path.join(out, "vayne_cells.json"))
    idle(delivery, design, out)
    print(f"design {design.canvas[design.canvas[..., 3] > 0].shape[0]} px, {design.height} rows, lenses at "
          f"{design.lens[0]:.2f},{design.lens[1]:.2f}, face box {design.face_box}")
    for tag in TAGS:
        a = np.asarray(Image.open(os.path.join(raw_dir, f"{tag}.png")).convert("RGBA"))
        k = key(a)
        anim = man["animations"][tag]
        frames, cols = anim["frames"], anim["columns"]
        rows = (len(frames) + cols - 1) // cols
        split = a.shape[0] if rows == 1 else int(round(a.shape[0] * (0.62 if tag == "dead" else 0.55)))
        boxes = []
        for i in range(len(frames)):
            cx, cy = i % cols, i // cols
            left, right = int(round(cx * a.shape[1] / cols)), int(round((cx + 1) * a.shape[1] / cols))
            top, bottom = (0, split) if cy == 0 else (split, a.shape[0])
            boxes.append(box(k, left, top, right, bottom))
        stand = 0 if tag in ("dead", "run") else len(boxes) - 1
        pitch = (boxes[stand][3] - boxes[stand][1]) / design.height      # the standing frame is the design's height
        atlas = np.zeros((rows * 96, cols * 96, 4), np.uint8)
        report = []
        for i, fr in enumerate(frames):
            eye = refine_eye(a, k, eyes[tag][i][0], eyes[tag][i][1], pitch)
            old = fr.pop("exact_head_origin", None)
            cell, origin, score, scrubbed = export_cell(a, k, pal, boxes[i], eye, pitch, tag, i, len(frames),
                                                        fr["pivot"], eyes[tag][i][2], design, face, tmpl)
            r, c = divmod(i, cols)
            atlas[r * 96:(r + 1) * 96, c * 96:(c + 1) * 96] = cell
            fr["face_origin"] = origin
            fr["head_method"] = "Codex's drawn head, the design's face pasted" if origin else "Codex's drawing"
            fr["opaque_area"] = int((cell[..., 3] > 0).sum())
            if score is None:
                report.append(f"{i + 1}:-")
            else:
                moved = f" {origin[0] - old[0]:+d},{origin[1] - old[1]:+d}" if origin and old else ""
                report.append(f"{i + 1}:{score:.0f}{'' if origin else '(not found)'}{moved}"
                              + (f" s{scrubbed}" if scrubbed else ""))
        Image.fromarray(atlas).save(os.path.join(out, "native", f"vayne_{tag}_1x.png"))
        Image.fromarray(np.repeat(np.repeat(atlas, 8, 0), 8, 1)).save(os.path.join(out, f"vayne_{tag}.png"))
        print(f"{tag:10s} pitch {pitch:.2f}  " + " | ".join(report))
    with open(os.path.join(out, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(man, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
