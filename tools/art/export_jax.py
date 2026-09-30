#!/usr/bin/env python3
"""Export Codex's raw strips of Jax to game pixels: one design size, the design's mask pasted, placed by League.

    python tools/art/export_jax.py <delivery folder> <out folder> [--np <native_pose folder>] [--fix <folder>]

Codex's jax_action_strips.zip (step 2) holds its image model's raw generations, as its HANDOFF says: sheets of
1536x1024 or 1774x887 (the pack asked for 2304x1536 / 3072x1536 at 8x), a magenta or a transparent ground, soft
edges, ~5-9 px squares, and Jax drawn a size bigger than the design (44-52 rows against the design's 41). This reads
them the way tools/art/export_vayne.py read Vayne's raw sheets:
  1. the ground keyed out - pure magenta and its fringe toward the outline (b >= r - 15, so the hood's and vest's
     magentas, which are redder than blue, stay; green under 16, the blend of magenta and the near-black outline, so
     the lamppost's violet, 9C1EA3 and the like, stays too) or alpha under 128;
  2. the figures found as 8-connected pieces of the rest, each piece given to the cell its middle falls in (Codex's
     figures reach over the equal cells);
  3. one square pitch per sheet: the median over its frames of sqrt(figure area in the sheet / the design's area in
     squares), so every strip comes out at the design's size (Codex drew the hit strip at ~11 px a square, the rest
     at 5.4-6.5). Heights mislead here: League's renders stand 51 rows with their long plume and lamppost where the
     design stands 41, and the size of the drawn mask set the bodies too small (Codex drew the heads a little big);
     the area came out at the size of Codex's own squares and of the design, side by side;
  4. every game pixel the per-channel median of the 3x3 source pixels round its sample point, figure when most of
     them are, snapped to the design's 24 colours without the eye cyan; Codex drew the lamppost violet (bluer than
     red, so apart from the hood's magentas) and it takes the design's pole colour, not the hood's light magenta;
  5. the design's mask (the bronze faceplate with its four cyan lights, 6x7 squares) pasted where Codex's four cyan
     lights are, so the face is the same in every frame; frames where no cyan was drawn (Jax turned away, lying
     down) keep Codex's drawing;
  6. placed in the 96x96 cell of jax_cells.json: across by the mask on League's head (the design's mask is DX, DY
     squares from League's head joint in the idle), up and down by the lowest square on the feet line (pivot + 11)
     for frames League has on the ground, by the mask for frames in the air; a figure that would be cut by the
     cell's side moved back in by the least it takes (in the air also down: League's own lamppost leaves the frame);
  7. specks of up to 9 squares off the body cleared (again after the outline pass); nothing under the feet line
     but in the death's last frames; pieces still apart joined through squares the source mostly covers (mend);
  8. the lamppost mended where it came out thin or broken, the user's pick "灯柱断口和细灯柱我按像素补": a clear
     square whose own patch is a quarter lamppost violet takes the pole colour (the 1-square pole ran between the
     sample points), Counter Strike's spun pole redrawn along its line (E_POLES), a redrawn frame's pink pole put in
     the pole colour (RECOLOUR);
  9. one outline (tools/art/design_riven.one_outline: spurs off, a black ring inside the outline turned into the
     material's own dark, lone specks taken by their area), the pasted mask kept.
With --install the strips, the cells table and the pack's idle (the design on every idle pivot) are written to
assets/source/native/ for tools/art/import_native.py (which closes the outline, strips.complete_outline).
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "native")
sys.path.insert(0, HERE)
import design_riven as R  # noqa: E402
Z = 8
FEET = 11
EYE = (0x46, 0xF0, 0xFF)
MASK_COLOURS = {(0x70, 0x4A, 0x23), (0xA1, 0x73, 0x37), (0xB4, 0x83, 0x40), (0x2C, 0x18, 0x20), EYE}
GREY = (225, 225, 225)
TAGS = ["run", "attack", "attack_w", "attack_e", "attack_r", "skill", "skill2", "skill2_burst", "ult", "hit", "dead"]
LOW_OK = {"dead": {6: 2, 7: 2, 8: 2}}          # frames (1-based) allowed that many rows under the feet line
AREA_FRAMES = {"dead": 6}                       # frames whose area sets the pitch (default all)
POLE = (0x69, 0x3A, 0x5D)                       # the design's lamppost pole
# frames Codex drew again one by one (jax_fix1_pack, the user's pick "小返修包给 Codex"; --fix <folder>): ult 3-4 turned
# to the camera, attack_w 3 with a straight pole. Each is read like a strip frame, its mask found from the cyan lights
# of 5 pixels or more, at one of two pitches: "area" gives it the area of the frame it replaces; "lights" puts the
# four lights two squares apart as in the design. The first round takes the area (the lights, which Codex drew small
# there, made ult 3-4 1.4 times too big)
FIXES = {("ult", 3): ("jax_ult_3.png", "area"), ("ult", 4): ("jax_ult_4.png", "area"),
         ("attack_w", 3): ("jax_attack_w_3.png", "area")}
# jax_fix2_pack (the user: "攻击的时候武器是歪的"): the frames whose lamppost was lost, shrunk to a lump or ball, or
# carried its lantern upright on a slanted pole. Drawn from cards that carry the pasted design mask, so the four
# lights set their size ("lights"); the area would count the whole lamppost the old frames lacked and put the body
# 1-19% under its neighbours
for _t, _n in (("attack", 1), ("attack", 4), ("attack", 5), ("attack", 6), ("attack_r", 1), ("attack_r", 2),
               ("attack_r", 6), ("skill", 2), ("dead", 1)):
    FIXES[(_t, _n)] = (f"jax_{_t}_{_n}.png", "lights")
# frames moved off League's place (squares): the redrawn attack_w 3 holds its straight lamppost out past the cell's
# right edge by two squares
SHIFT = {("attack_w", 3): (-3, 0)}
# colours put right after placing (cell squares): the redrawn attack_w 3 has its pole in the hood's pink - the hood's
# colours within 1.6 squares of the pole's line become the pole's, and the one outline row across it (a notch at game
# size) too; the red glass of its lantern the lantern's glow
HOOD = {(0xBB, 0x1E, 0x8E), (0x7E, 0x02, 0x60), (0x55, 0x03, 0x43), (0xC6, 0x2D, 0x57)}
GLOW = (0x8A, 0x29, 0x01)
POLISH = {(0xBB, 0x1E, 0x8E), (0x7E, 0x02, 0x60), (0x55, 0x03, 0x43), (0xC6, 0x2D, 0x57), (0x1B, 0x24, 0x96),
          (0x24, 0x2E, 0xB4), (0x12, 0x16, 0x6B), (0x34, 0x19, 0x5F), (0x5D, 0x59, 0xAE), (0x31, 0x11, 0x35)}
# Counter Strike's start (skill2): Codex drew the spun lamppost pink toward the hook and blue toward the lantern, and
# frames 2-3 broke it at the hands; along each pole's line (hook end -> lantern end) the pole's middle squares take
# the pole colour and the clear ones on the line are filled - the fists, rings and fingers stay in front
E_POLES = {1: ((30, 56), (71, 56)), 2: ((38, 30), (67, 19)), 3: ((43, 21), (69, 37)), 4: ((34, 27), (67, 27)),
           5: ((54, 16), (54, 25)), 6: ((34, 28), (63, 32))}
RECOLOUR = {("attack_w", 3): [("line", (88, 28), (70, 48), 1.6, HOOD, POLE),
                              ("box", (78, 40), (80, 41), 0, {(0x11, 0x03, 0x15), (0x0F, 0x02, 0x13),
                                                             (0x17, 0x02, 0x1C)}, POLE),
                              ("box", (83, 10), (96, 29), 0, {(0xC6, 0x2D, 0x57)}, GLOW)]}
OUTLINES = {(0x0F, 0x02, 0x13), (0x11, 0x03, 0x15), (0x17, 0x02, 0x1C)}
for _n, (_p0, _p1) in E_POLES.items():            # (an outline square on the middle would go as a spur, a gap)
    RECOLOUR[("skill2", _n)] = [("line", _p0, _p1, 0.5, POLISH | OUTLINES, POLE), ("fill", _p0, _p1, 0.5, None, POLE)]
# cape claws whose thin strip was lost (Leap Strike's landing, the death's second frame): a strip of the cape's
# magenta back to the cape
CAPE = (0x7E, 0x02, 0x60)
RECOLOUR[("skill", 5)] = [("fill", (30, 41), (33, 41), 0.5, None, CAPE)]
RECOLOUR[("dead", 2)] = [("fill", (38, 64), (40, 64), 0.5, None, CAPE)]


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def key(a):
    """True where the ground is: alpha under 128, pure magenta, or magenta blended toward the outline."""
    r, g, b, al = (a[..., k].astype(int) for k in range(4))
    mag = (r > 190) & (b > 190) & (g < 110)
    fringe = (r - g > 80) & (b - g > 80) & (b >= r - 15) & (g < 16)
    return (al < 128) | mag | fringe


def pieces(fg, min_px=20):
    """8-connected pieces of a boolean image: [(ys, xs)] with at least min_px pixels."""
    H, W = fg.shape
    lab = np.zeros((H, W), np.int32)
    out = []
    n = 0
    for sy, sx in zip(*np.nonzero(fg)):
        if lab[sy, sx]:
            continue
        n += 1
        stack = [(sy, sx)]
        lab[sy, sx] = n
        ys, xs = [], []
        while stack:
            y, x = stack.pop()
            ys.append(y)
            xs.append(x)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < H and 0 <= xx < W and fg[yy, xx] and not lab[yy, xx]:
                        lab[yy, xx] = n
                        stack.append((yy, xx))
        if len(ys) >= min_px:
            out.append((np.array(ys), np.array(xs)))
    return out


class Design:
    def __init__(self):
        c = np.asarray(Image.open(lp(os.path.join(SRC, "jax_native.png"))).convert("RGBA"))[4::8, 4::8]
        self.canvas = c.copy()
        op = c[..., 3] > 0
        eye = np.all(c[..., :3] == EYE, -1) & op
        ey, ex = np.nonzero(eye)
        self.eye = (float(ex.mean()), float(ey.mean()))                 # the four lights' middle, canvas squares
        x0, x1 = int(ex.min()) - 2, int(ex.max()) + 1                   # the faceplate round them
        y0, y1 = int(ey.min()) - 2, int(ey.max()) + 2
        self.mask = []
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                col = tuple(int(v) for v in c[y, x, :3])
                if c[y, x, 3] and col in MASK_COLOURS:
                    self.mask.append((x - self.eye[0], y - self.eye[1], c[y, x].copy()))
        cols = sorted({tuple(int(v) for v in p[:3]) for p in c[op][:, :3]})
        self.pal = [p for p in cols if p != EYE]
        self.parr = np.array(self.pal, float)

    def snap(self, rgb):
        r, g, b = (float(v) for v in rgb)
        if b >= r - 15 and r - g > 50 and b - g > 50 and max(r, b) > 100:
            return POLE                         # Codex's lamppost violet (9C1EA3 and the like) is the design's pole
        d = ((self.parr - rgb) ** 2 * np.array([2.0, 3.0, 2.0])).sum(1)
        return self.pal[int(np.argmin(d))]


def league_frames(np_dir, tag, cells):
    """Per frame of League's strip: (top, bottom) rows of the figure in its cell (game squares)."""
    im = np.asarray(Image.open(os.path.join(np_dir, f"jax_native_{tag}.png")).convert("RGB")).astype(int)
    one = im[Z // 2::Z, Z // 2::Z]
    cw, ch = cells["cell"]
    cols = one.shape[1] // cw
    res = []
    for i in range(len(cells["tags"][tag])):
        c = one[(i // cols) * ch:(i // cols + 1) * ch, (i % cols) * cw:(i % cols + 1) * cw]
        fig = np.abs(c - np.array(GREY)).sum(2) > 10
        ys, xs = np.nonzero(fig)
        res.append((int(ys.min()), int(ys.max()), float(xs.mean())))
    return res


def cyan_middle(a, fg, least=1):
    """The middle of Codex's drawn cyan lights (source pixels; clusters of at least `least` pixels), or None."""
    r, g, b = (a[..., k].astype(int) for k in range(3))
    cy = fg & (g > 170) & (b > 170) & (r < 150)
    if least > 1:
        keep = np.zeros(cy.shape, bool)
        for ys, xs in pieces(cy, least):
            keep[ys, xs] = True
        cy = keep
    ys, xs = np.nonzero(cy)
    if len(ys) < 12:
        return None
    return float(xs.mean()), float(ys.mean())


def violet(px):
    """Codex's lamppost violet (bluer than red, so apart from the hood's magentas): a boolean per pixel."""
    r, g, b = (px[..., k].astype(int) for k in range(3))
    return (b >= r - 15) & (r - g > 50) & (b - g > 50) & (np.maximum(r, b) > 100)


def sample(a, fg, design, bx, pitch):
    """The frame at game size: (1x RGBA, x0, y0) where x0, y0 is the source point of square (0, 0)'s corner.
    A square left clear whose own pitch x pitch patch is a quarter lamppost violet or more takes the pole's colour:
    the thin pole ran between the sample points in places and came out in pieces."""
    x0, y0, x1, y1 = bx
    W = int(np.ceil((x1 - x0) / pitch)) + 1
    H = int(np.ceil((y1 - y0) / pitch)) + 1
    out = np.zeros((H, W, 4), np.uint8)
    cov = np.zeros((H, W))                      # clear squares: the share of figure in their own patch
    col = np.zeros((H, W, 3), np.uint8)         # ... and its colour
    pole = fg & violet(a)
    for j in range(H):
        cy = int(round(y0 + (j + 0.5) * pitch))
        for i in range(W):
            cx = int(round(x0 + (i + 0.5) * pitch))
            ys, xs = slice(max(0, cy - 1), cy + 2), slice(max(0, cx - 1), cx + 2)
            m = fg[ys, xs]
            if m.size == 0 or m.sum() * 2 <= m.size:
                py0, px0 = int(round(y0 + j * pitch)), int(round(x0 + i * pitch))
                win = (slice(max(0, py0), max(0, int(round(y0 + (j + 1) * pitch)))),
                       slice(max(0, px0), max(0, int(round(x0 + (i + 1) * pitch)))))
                patch = pole[win]
                if patch.size and patch.mean() >= 0.25:
                    out[j, i, :3] = POLE
                    out[j, i, 3] = 255
                elif patch.size:
                    f = fg[win]
                    cov[j, i] = f.mean()
                    if f.any():
                        col[j, i] = design.snap(np.median(a[win][f][:, :3], axis=0))
                continue
            px = a[ys, xs][m][:, :3]
            out[j, i, :3] = design.snap(np.median(px, axis=0))
            out[j, i, 3] = 255
    mend(out, cov, col)
    return out


def mend(out, cov, col, least=0.3, steps=4):
    """Join pieces apart from the body (more than 2 squares: a cape's claw tip, a pole's end) through clear squares
    whose own patch is at least `least` figure - the thin strip Codex drew there fell between the sample points -
    by the shortest such path of at most `steps` squares, in the patch's colour."""
    H, W = cov.shape
    for _ in range(4):
        parts = sorted(pieces(out[..., 3] > 0, 1), key=lambda q: -len(q[0]))
        if len(parts) < 2:
            return
        body = np.zeros((H, W), bool)
        body[parts[0]] = True
        joined = False
        for ys, xs in parts[1:]:
            if len(ys) <= 2:
                continue
            prev = {(int(y), int(x)): None for y, x in zip(ys, xs)}
            front, end = list(prev), None
            for _step in range(steps + 1):
                nxt = []
                for y, x in front:
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            yy, xx = y + dy, x + dx
                            if not (0 <= yy < H and 0 <= xx < W) or (yy, xx) in prev:
                                continue
                            if body[yy, xx]:
                                end = (y, x)
                                break
                            if out[yy, xx, 3] == 0 and cov[yy, xx] >= least:
                                prev[(yy, xx)] = (y, x)
                                nxt.append((yy, xx))
                        if end:
                            break
                    if end:
                        break
                if end or not nxt:
                    break
                front = nxt
            while end is not None and prev[end] is not None:
                out[end[0], end[1], :3] = col[end]
                out[end[0], end[1], 3] = 255
                end = prev[end]
                joined = True
        if not joined:
            return


def recolour(cell, rules):
    """RECOLOUR's rules on a placed cell: ("line", p0, p1, reach, from, to), ("fill", p0, p1, reach, None, to): the clear
    squares within reach of the line, or ("box", (x0, y0), (x1, y1), _, from, to)."""
    H, W = cell.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    for kind, p0, p1, reach, old, new in rules:
        if kind in ("line", "fill"):
            (x0, y0), (x1, y1) = p0, p1
            dx, dy = x1 - x0, y1 - y0
            t = np.clip(((xx - x0) * dx + (yy - y0) * dy) / float(dx * dx + dy * dy), 0, 1)
            near = np.hypot(xx - (x0 + t * dx), yy - (y0 + t * dy)) <= reach
        else:
            near = (xx >= p0[0]) & (xx < p1[0]) & (yy >= p0[1]) & (yy < p1[1])
        if old is None:                         # "fill": the clear squares on the line
            hit = near & (cell[..., 3] == 0)
            cell[hit, 3] = 255
        else:
            hit = near & (cell[..., 3] > 0) & np.isin(cell[..., 0].astype(int) * 65536 + cell[..., 1].astype(int) * 256
                                                     + cell[..., 2], [r * 65536 + g * 256 + b for r, g, b in old])
        cell[hit, :3] = new


def clean_specks(cell, protect, most=9):
    op = cell[..., 3] > 0
    H, W = op.shape
    seen = np.zeros(op.shape, bool)
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
        if len(pts) <= most and not prot:
            for y, x in pts:
                cell[y, x] = 0


def fix_frame(path, mode, squares):
    """A frame Codex drew again on its own: (image, figure mask, box, pitch). The pitch gives it `squares` squares
    ("area") or puts the four cyan lights two squares apart ("lights": half the mean distance of each light to its
    nearest one)."""
    b = np.asarray(Image.open(path).convert("RGBA"))
    m = np.zeros(b.shape[:2], bool)
    for ys, xs in pieces(~key(b)):
        m[ys, xs] = True
    ys, xs = np.nonzero(m)
    box = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    if mode == "lights":
        r, g, bl = (b[..., k].astype(int) for k in range(3))
        lights = sorted(pieces(m & (g > 170) & (bl > 170) & (r < 150), 5), key=lambda q: -len(q[0]))[:4]
        c = np.array([(q[1].mean(), q[0].mean()) for q in lights])
        d = np.sqrt(((c[:, None] - c[None]) ** 2).sum(-1)) + np.eye(len(c)) * 1e9
        return b, m, box, float(d.min(1).mean() / 2)
    return b, m, box, float(np.sqrt(m.sum() / squares))


def export_tag(tag, delivery, np_dir, cells, design, head0, fix=None):
    a = np.asarray(Image.open(os.path.join(delivery, f"jax_{tag}.png")).convert("RGBA"))
    bg = key(a)
    fg = ~bg
    frames = cells["tags"][tag]
    cw, ch = cells["cell"]
    now = Image.open(os.path.join(np_dir, f"jax_native_{tag}.png"))
    cols, rows = now.size[0] // (cw * Z), now.size[1] // (ch * Z)
    H, W = a.shape[:2]
    owner = [[] for _ in frames]
    for ys, xs in pieces(fg):
        c = int(xs.mean() * cols // W) + cols * int(ys.mean() * rows // H)
        if c < len(frames):
            owner[c].append((ys, xs))
    league = league_frames(np_dir, tag, cells)
    boxes, masks = [], []
    for i in range(len(frames)):
        m = np.zeros((H, W), bool)
        for ys, xs in owner[i]:
            m[ys, xs] = True
        masks.append(m)
        ys, xs = np.nonzero(m)
        boxes.append((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))
    # the pitch that gives each frame the design's area; the sheet takes the median (the lying frames of the death,
    # whose limbs overlap, left out)
    darea = int((design.canvas[..., 3] > 0).sum())
    ratios = [np.sqrt(m.sum() / darea) for m in masks]
    pitch = float(np.median(ratios[:AREA_FRAMES.get(tag, len(ratios))]))
    atlas = np.zeros((rows * ch, cols * cw, 4), np.uint8)
    report = []
    for i, fr in enumerate(frames):
        src, m, bx, p, least = a, masks[i], boxes[i], pitch, 1
        name, mode = FIXES.get((tag, i + 1), (None, None))
        if fix and name and os.path.exists(os.path.join(fix, name)):
            src, m, bx, p = fix_frame(os.path.join(fix, name), mode, masks[i].sum() / pitch ** 2)
            least = 5
        one = sample(src, m, design, bx, p)
        mid = cyan_middle(src, m, least)
        pasted = np.zeros(one.shape[:2], bool)
        if mid is not None:
            ex = (mid[0] - bx[0]) / p - 0.5
            ey = (mid[1] - bx[1]) / p - 0.5
            for dx, dy, c in design.mask:
                x, y = int(round(ex + dx)), int(round(ey + dy))
                if 0 <= y < one.shape[0] and 0 <= x < one.shape[1]:
                    one[y, x] = c
                    pasted[y, x] = True
        else:
            ex = ey = None
        px, py = fr["pivot"]
        feet = py + FEET
        top, bottom, lx = league[i]
        grounded = bottom >= feet - 1
        op = one[..., 3] > 0
        oys, oxs = np.nonzero(op)
        if ex is not None:
            tx = fr["head"][0] + head0[0] - ex
            ty = fr["head"][1] + head0[1] - ey
        else:
            tx = lx - oxs.mean()
            ty = top - oys.min()
        if grounded or ex is None:
            ty = feet - oys.max()
        tx, ty = int(round(tx)) + SHIFT.get((tag, i + 1), (0, 0))[0], int(round(ty)) + SHIFT.get((tag, i + 1), (0, 0))[1]
        # kept inside the cell: a figure that would be cut at a side is moved back by the least it takes (up and
        # down only in the air - the grounded keep the feet line): the raised lamppost of the ult's jump and of
        # Leap Strike's rise, a cape tail at the left
        kept = [0, 0]                           # (a clear square left at the side for the outline)
        if oxs.min() + tx < 1:
            kept[0] = 1 - (oxs.min() + tx)
        elif oxs.max() + tx > cw - 2:
            kept[0] = cw - 2 - (oxs.max() + tx)
        if not grounded and ex is not None and oys.min() + ty < 1:
            kept[1] = 1 - (oys.min() + ty)
        tx, ty = tx + kept[0], ty + kept[1]
        cell = np.zeros((ch, cw, 4), np.uint8)
        prot = np.zeros((ch, cw), bool)
        for y, x in zip(oys, oxs):
            yy, xx = y + ty, x + tx
            if 0 <= yy < ch and 0 <= xx < cw:
                cell[yy, xx] = one[y, x]
                prot[yy, xx] = pasted[y, x]
        recolour(cell, RECOLOUR.get((tag, i + 1), ()))
        clean_specks(cell, prot)
        low = LOW_OK.get(tag, {}).get(i + 1, 0)
        cell[feet + 1 + low:] = 0
        cell = R.one_outline(cell, prot)
        clean_specks(cell, prot)                # bits the outline pass cut off (the counter's claw by the plume)
        r, c = divmod(i, cols)
        atlas[r * ch:(r + 1) * ch, c * cw:(c + 1) * cw] = cell
        report.append(f"{i + 1}:{'M' if ex is not None else '-'}{'g' if grounded else 'a'}"
                      f"{f'(fix {p:.2f})' if src is not a else ''}{f'(in {kept[0]:+d},{kept[1]:+d})' if any(kept) else ''}")
    return atlas, pitch, report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("delivery")
    ap.add_argument("out")
    ap.add_argument("--np", default=os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "jx_work", "np"))
    ap.add_argument("--idle", help="the pack's jax_idle.png (8x): the design on every idle pivot")
    ap.add_argument("--fix", help="a folder with frames Codex drew again (FIXES)")
    ap.add_argument("--install", action="store_true", help="also write the strips into assets/source/native/")
    a = ap.parse_args()
    cells = json.load(open(os.path.join(a.np, "jax_cells.json"), encoding="utf-8"))
    design = Design()
    # the design's mask from League's head joint in the idle (the design stands on the idle's pivot)
    idle = cells["tags"]["idle"][0]
    px, py = idle["pivot"]
    ex, ey = design.eye
    head0 = (ex - 64 + px - idle["head"][0], ey - 88 + py - idle["head"][1])
    os.makedirs(os.path.join(a.out, "native"), exist_ok=True)
    print(f"design eyes {ex:.1f},{ey:.1f} on the canvas; mask {len(design.mask)} squares, {head0[0]:+.1f},{head0[1]:+.1f} "
          f"from League's head")
    for tag in TAGS:
        atlas, pitch, report = export_tag(tag, a.delivery, a.np, cells, design, head0, a.fix)
        Image.fromarray(atlas).save(os.path.join(a.out, "native", f"jax_{tag}_1x.png"))
        Image.fromarray(np.repeat(np.repeat(atlas, Z, 0), Z, 1)).save(os.path.join(a.out, f"jax_{tag}.png"))
        print(f"{tag:13s} pitch {pitch:.2f}  " + " ".join(report))
        if a.install:
            Image.fromarray(np.repeat(np.repeat(atlas, Z, 0), Z, 1)).save(lp(os.path.join(SRC, f"jax_{tag}.png")))
    if a.install:
        with open(lp(os.path.join(SRC, "jax_cells.json")), "w", encoding="utf-8", newline="\n") as f:
            json.dump(cells, f, indent=1)
            f.write("\n")
        if a.idle:
            shutil.copyfile(a.idle, lp(os.path.join(SRC, "jax_idle.png")))


if __name__ == "__main__":
    main()
