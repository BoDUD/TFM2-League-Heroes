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
the face is looked for by colour within REACH of the mark (the design's MATCH_BOX, its lenses in the cape's red that
Codex's own lenses become once snapped) and pasted where it matches best, and Codex's lens squares left round it go.
The rolls' tucked frames and the lying death keep Codex's drawing, as before, and so does HIDDEN (her head thrown
back as she falls: the upright face turned her chin into a second one).
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
FACE_BOX = (21, 10, 29, 17)            # x0, y0, x1, y1 in the design's own coordinates (36x48)
MATCH_BOX = (20, 9, 30, 17)            # the face and the fringe's edge round it: what is looked for in each frame
HEAD_BOX = (13, 0, 33, 17)             # the head Codex pasted (tidy_vayne.HEAD_BOX): its specks stay, as in Codex's
DESIGN_AT = (41, 52)                   # where the design stands on the 128 canvas
LENS_CENTRE = (65.8888889, 64.5555556)  # the design's lens centre on the 128 canvas (Codex's constants)
DRAWN_LENS = (0xCD, 0x06, 0x2B)        # Codex's own lenses once snapped (the palette has no lens reds): the cape's red
REACH = 10                             # how far from Codex's eye mark the face is looked for, in squares
FACE_OK = 130                          # mean colour distance over MATCH_BOX above which the face is not found (Vayne's
                                       # upright faces 14-97, the falling ones 102-126)
HIDDEN = {"dead": (1,)}                # frames (1-based) whose drawn face stays: her head thrown back as she falls
TAGS =["attack", "attack_q", "run", "skill", "skill_back", "skill2", "ult", "hit", "dead"]


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def design_canvas():
    """The design on its 128 canvas, 1x (Codex's design/vayne_design_1x.png)."""
    return np.asarray(Image.open(lp(os.path.join(SRC, "vayne_native.png"))).convert("RGBA"))[4::8, 4::8].copy()


def face_patch(design_c):
    """The face's pixels as (x, y, rgba) on the 128 canvas."""
    dx0, dy0 = DESIGN_AT
    fx0, fy0, fx1, fy1 = FACE_BOX
    face = []
    for y in range(fy0 + dy0, fy1 + dy0 + 1):
        for x in range(fx0 + dx0, fx1 + dx0 + 1):
            c = design_c[y, x]
            if c[3] and tuple(int(v) for v in c[:3]) in FACE_COLOURS:
                face.append((x, y, c.copy()))
    return face


def match_template(design_c):
    """The face as Codex's frames have it once snapped: the design's MATCH_BOX, its lens reds as the cape's red."""
    x0, y0, x1, y1 = MATCH_BOX
    t = design_c[y0 + DESIGN_AT[1]:y1 + DESIGN_AT[1] + 1, x0 + DESIGN_AT[0]:x1 + DESIGN_AT[0] + 1].copy()
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


def export_cell(a, k, pal, bx, eye, pitch, tag, i, n, piv, target_x, design_c, face, tmpl):
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
    hx = int(round(target_ex - LENS_CENTRE[0]))
    hy = int(round(ey / pitch + ty - LENS_CENTRE[1]))
    protect = np.zeros((96, 96), bool)
    origin = score = None
    scrubbed = 0
    if use_face:
        # Codex's eye marks are off by up to 10 squares in the fall and Condemn's shot (its whole-head paste cleared
        # the drawn head, so it never showed): the face goes where Codex's own face is, found by colour near the mark
        mx, my = MATCH_BOX[0] + DESIGN_AT[0], MATCH_BOX[1] + DESIGN_AT[1]
        score, fx, fy = locate(cell, tmpl, (hx + mx, hy + my))
        x0, y0, x1, y1 = HEAD_BOX
        if i + 1 in HIDDEN.get(tag, ()):
            score = None
            protect[max(0, y0 + DESIGN_AT[1] + hy):max(0, y1 + DESIGN_AT[1] + hy + 1),
                    max(0, x0 + DESIGN_AT[0] + hx):max(0, x1 + DESIGN_AT[0] + hx + 1)] = True
        elif score <= FACE_OK:
            hx, hy = fx - mx, fy - my
            pasted = np.zeros((96, 96), bool)
            for x, y, c in face:
                xx, yy = x + hx, y + hy
                if 0 <= xx < 96 and 0 <= yy < 96:
                    cell[yy, xx] = c
                    pasted[yy, xx] = True
            fx0, fy0, fx1, fy1 = FACE_BOX
            scrubbed = scrub(cell, (fx0 + DESIGN_AT[0] + hx, fy0 + DESIGN_AT[1] + hy,
                                    fx1 + DESIGN_AT[0] + hx, fy1 + DESIGN_AT[1] + hy), pasted)
            protect[max(0, y0 + DESIGN_AT[1] + hy):max(0, y1 + DESIGN_AT[1] + hy + 1),
                    max(0, x0 + DESIGN_AT[0] + hx):max(0, x1 + DESIGN_AT[0] + hx + 1)] = True
            origin = [hx, hy]
    if (i == n - 1 or (tag == "attack" and i == n - 2)) and tag not in ("run", "dead"):
        cell[:] = 0                     # Codex's exact return to the design stance
        ddx, ddy = piv[0] - 73, -18
        for y, x in zip(*np.nonzero(design_c[..., 3] > 0)):
            if 0 <= y + ddy < 96 and 0 <= x + ddx < 96:
                cell[y + ddy, x + ddx] = design_c[y, x]
                protect[y + ddy, x + ddx] = True
        origin = score = None
    clean_specks(cell, protect)
    cell[target_bottom + 1:] = 0
    return cell, origin, score, scrubbed


def main():
    raw_dir, delivery, out = sys.argv[1:4]
    design_c = design_canvas()
    pal = Palette(design_c)
    face = face_patch(design_c)
    tmpl = match_template(design_c)
    eyes = json.load(open(os.path.join(raw_dir, "strip_eyes.json"), encoding="utf-8-sig"))
    man = json.load(open(os.path.join(delivery, "manifest.json"), encoding="utf-8-sig"))
    os.makedirs(os.path.join(out, "native"), exist_ok=True)
    for f in ("vayne_idle.png", "vayne_cells.json", os.path.join("native", "vayne_idle_1x.png")):
        shutil.copyfile(os.path.join(delivery, f), os.path.join(out, f))
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
        pitch = (boxes[stand][3] - boxes[stand][1]) / 48.0
        atlas = np.zeros((rows * 96, cols * 96, 4), np.uint8)
        report = []
        for i, fr in enumerate(frames):
            eye = refine_eye(a, k, eyes[tag][i][0], eyes[tag][i][1], pitch)
            old = fr.pop("exact_head_origin", None)
            cell, origin, score, scrubbed = export_cell(a, k, pal, boxes[i], eye, pitch, tag, i, len(frames),
                                                        fr["pivot"], eyes[tag][i][2], design_c, face, tmpl)
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
