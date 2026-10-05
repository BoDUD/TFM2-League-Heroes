#!/usr/bin/env python3
"""rigkit: pose a hero's action strips from the approved design's own pixels (the casting body = the idle's).

A shared library for the tools/art/rig_<hero>.py scripts (the rule the user set across the pack: standing actions keep
the idle's body and legs square for square, only what the action moves is moved; weapons are never resampled). It
collects what rig_twistedfate, rig_sivir, rig_aatrox and rig_varus each wrote for themselves:

  canvas      Design(path): the 128x128 design read back from its 8x PNG; mask_rows / mask_box / colour classes
  parts       Part: a sprite cut from the design with a joint (a grip, a shoulder, a hip) in canvas coordinates
  weapons     orientations(part, slope): a drawn diagonal weapon in its 4 exact quarter turns (rot90, the blade's
              curve kept; mirrors, flips and a whole-column shear to level only on request) - never RotSprite (it
              breaks blades into teeth and dots)
  limbs       rot90(part, k): an arm cut out WITH its weapon as one rigid unit and turned about the shoulder - first
              choice (Tryndamere 2026-10-05: drawn bones and a sheared arm, 「左手右手释放技能都变形」; the rigid
              quarter-turned units were taken at once); flip_v / flip_h for an arm without a curved weapon
  arms        bone_arm(): an arm drawn along shoulder -> elbow -> hand in the design's own materials (lit / mid / dark
              across the bone, bands along it), one outline ring; elbow(): the elbow for a hand within reach - only
              where no quarter turn of the design's own arm will do: on a small design it reads as a different arm
  legs        swing_leg(): a leg turned about its hip by row shear (the boot moved whole, lifted when it swings)
  whole       turn(): RotSprite of a whole figure (deaths), quarter turns exact; place(): a sprite by its joint
  finish      finish(): pinholes filled, the outline closed (strips.complete_outline), stray outline squares and crumbs
              gone; audit(): pieces, enclosed holes, orphan outline squares and area against the idle, per frame
  output      write_strips(): 8x strips in the cells layout + <hero>_cells.json for tools/art/import_native.py;
              review_sheet() and review_gif() for the user

Coordinates are (x, y) on the 128x128 canvas, pixel centres at integer + 0.5 where a joint is continuous.
"""
import json
import math
import os
import sys
from collections import Counter

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips  # noqa: E402

Z = 8
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return p if os.name != "nt" or p.startswith(pre) else pre + p


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[k:k + 2], 16) for k in (0, 2, 4))


# ------------------------------------------------------------------------------------------------ canvas
class Design:
    """The approved design on its 128x128 canvas (read from the 8x PNG, one pixel per block)."""

    def __init__(self, path):
        a = np.asarray(Image.open(lp(path)).convert("RGBA"))
        if a.shape[0] != 128:
            a = a[Z // 2::Z, Z // 2::Z]
        a = a.copy()
        a[a[..., 3] < 128] = 0
        a[a[..., 3] > 0, 3] = 255
        self.a = a
        op = a[..., 3] > 0
        lum = lambda c: 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
        self.palette = sorted({tuple(int(v) for v in p[:3]) for p in a[op]}, key=lum)
        self.outline = self.palette[0]
        ys = np.nonzero(op.any(1))[0]
        self.soles = int(ys.max())
        self.top = int(ys.min())

    def letters(self, keys="0abcdefghijklmnopqrstuvwxyzABCDEFGHIJ"):
        """{letter: rgb} with the palette sorted dark to light, the letters the review prints use."""
        return {keys[i]: c for i, c in enumerate(self.palette)}

    def grid(self, r0, r1, c0, c1):
        """The design's squares as letters (for writing masks and bone strips by hand)."""
        inv = {c: k for k, c in self.letters().items()}
        rows = []
        for y in range(r0, r1):
            rows.append(f"{y:3d} " + "".join(inv[tuple(int(v) for v in self.a[y, x, :3])] if self.a[y, x, 3] else "."
                                             for x in range(c0, c1)))
        return "\n".join(rows)


def mask_rows(spec, shape=(128, 128)):
    """{row: (first, last)} or {row: [cols]} -> bool mask."""
    m = np.zeros(shape, bool)
    for r, cols in spec.items():
        if isinstance(cols, tuple) and len(cols) == 2:
            m[r, cols[0]:cols[1] + 1] = True
        else:
            m[r, list(cols)] = True
    return m


def mask_box(r0, r1, c0, c1, shape=(128, 128)):
    m = np.zeros(shape, bool)
    m[r0:r1 + 1, c0:c1 + 1] = True
    return m


def colour_mask(a, colours):
    """Squares of the picture in one of the colours (rgb tuples)."""
    m = np.zeros(a.shape[:2], bool)
    for c in colours:
        m |= (a[..., :3] == np.array(c, np.uint8)).all(-1) & (a[..., 3] > 0)
    return m


def cut(a, mask):
    """(the part: mask's squares, the rest: everything else)."""
    part = np.zeros_like(a)
    part[mask] = a[mask]
    rest = a.copy()
    rest[mask] = 0
    return part, rest


# ------------------------------------------------------------------------------------------------ parts
class Part:
    """A sprite (RGBA, cropped) with a joint in sprite coordinates (pixel centres = integer + 0.5)."""

    def __init__(self, s, joint):
        self.s = s
        self.j = joint

    @classmethod
    def from_canvas(cls, a, mask, joint):
        ys, xs = np.nonzero(mask & (a[..., 3] > 0))
        y0, x0 = ys.min(), xs.min()
        s = np.zeros((ys.max() - y0 + 1, xs.max() - x0 + 1, 4), np.uint8)
        s[ys - y0, xs - x0] = a[ys, xs]
        return cls(s, (joint[0] - x0, joint[1] - y0))

    def flip_h(self):
        return Part(self.s[:, ::-1].copy(), (self.s.shape[1] - self.j[0], self.j[1]))

    def flip_v(self):
        return Part(self.s[::-1].copy(), (self.j[0], self.s.shape[0] - self.j[1]))

    def transpose(self):
        return Part(self.s.transpose(1, 0, 2).copy(), (self.j[1], self.j[0]))


def put(dst, src, ox, oy, under=False):
    """src's opaque squares onto dst at top-left (ox, oy); under=True only where dst is clear."""
    ys, xs = np.nonzero(src[..., 3])
    cy, cx = ys + oy, xs + ox
    ok = (cy >= 0) & (cy < dst.shape[0]) & (cx >= 0) & (cx < dst.shape[1])
    ys, xs, cy, cx = ys[ok], xs[ok], cy[ok], cx[ok]
    if under:
        free = dst[cy, cx, 3] == 0
        ys, xs, cy, cx = ys[free], xs[free], cy[free], cx[free]
    dst[cy, cx] = src[ys, xs]
    return dst


def place(dst, part, at, under=False):
    """The part with its joint on the canvas point `at` (continuous)."""
    return put(dst, part.s, int(math.floor(at[0] - part.j[0] + 1e-9)), int(math.floor(at[1] - part.j[1] + 1e-9)), under)


def shifted(a, dx, dy):
    out = np.zeros_like(a)
    return put(out, a, dx, dy)


# ------------------------------------------------------------------------------------------------ weapons
def level(part, slope=1.0):
    """A diagonal weapon drawn going down-left from its joint (rows grow as columns fall) made level (pointing left):
    every column moved up by slope x its distance left of the joint - whole columns, no resampling."""
    s, (jx, jy) = part.s, part.j
    H, W = s.shape[:2]
    shifts = [int(math.floor(max(0.0, jx - (x + 0.5)) * slope + 0.5)) for x in range(W)]
    top = max(shifts)
    out = np.zeros((H + top, W, 4), np.uint8)
    for x in range(W):
        col = s[:, x]
        out[top - shifts[x]:top - shifts[x] + H, x] = col
    ys = np.nonzero(out[..., 3].any(1))[0]
    out = out[ys.min():ys.max() + 1]
    return Part(out, (jx, jy + top - ys.min()))


def rot90(part, k):
    """The part turned k quarter turns clockwise on screen about its joint - lossless, and unlike a mirror it keeps
    a curved blade's shape (which edge is serrated, which way it bends)."""
    s, (jx, jy) = part.s, part.j
    for _ in range(k % 4):
        H = s.shape[0]
        s = np.rot90(s, -1)                  # clockwise: (x, y) -> (H - y, x)
        jx, jy = H - jy, jx
    return Part(s.copy(), (jx, jy))





def orientations(part, slope=1.0, mirrored=False):
    """The weapon (drawn pointing down-left from its joint) in the four diagonal directions, named by where its tip
    points: dl as drawn, ul / ur / dr its exact quarter turns (the blade keeps its shape). mirrored=True adds the
    mirror images (dl_m ...) and the levelled copies (l, r, u, d: a whole-column shear - fatter and shorter, use only
    where the weapon is small)."""
    o = {"dl": part, "ul": rot90(part, 1), "ur": rot90(part, 2), "dr": rot90(part, 3)}
    if mirrored:
        o.update({"dl_m": part.flip_h(), "ul_m": part.flip_v(), "ur_m": part.flip_h().flip_v(),
                  "dr_m": part.flip_h().flip_v().flip_h()})
        lv = level(part, slope)
        o.update({"l": lv, "r": lv.flip_h(), "u": lv.transpose()})
        o["d"] = o["u"].flip_v()
    return o


# ------------------------------------------------------------------------------------------------ arms
def elbow(shoulder, hand, upper, fore, bend=1):
    """The elbow for a hand at `hand` (pulled into reach), bones of lengths upper / fore; bend +1 / -1 picks the side."""
    sx, sy = shoulder
    hx, hy = hand
    d = math.hypot(hx - sx, hy - sy)
    reach = upper + fore - 0.3
    if d > reach:
        hx, hy = sx + (hx - sx) * reach / d, sy + (hy - sy) * reach / d
        d = reach
    d = max(d, abs(upper - fore) + 0.3)
    a = (upper ** 2 - fore ** 2 + d ** 2) / (2 * d)
    h = math.sqrt(max(0.0, upper ** 2 - a ** 2))
    ux, uy = (hx - sx) / d, (hy - sy) / d
    mx, my = sx + a * ux, sy + a * uy
    return (mx - bend * h * uy, my + bend * h * ux), (hx, hy)


def bone_arm(dst, shoulder, elb, hand, mats, width=(3.2, 2.8), outline=None, light=(-0.6, -0.8)):
    """Draw an arm along shoulder -> elbow -> hand into dst. mats: {"upper": [(t0, t1, (lit, mid, dark)), ...],
    "fore": [...]} - bands along each bone (t from 0 at its start to 1 at its end), each band three shades across the
    bone (the side toward `light` lit). Every square within width/2 of the bone takes a shade; then one outline ring
    (where outline is given). Returns the arm's mask."""
    m = np.zeros(dst.shape[:2], bool)
    col = {}
    lx, ly = light
    for name, p0, p1, w in (("upper", shoulder, elb, width[0]), ("fore", elb, hand, width[1])):
        vx, vy = p1[0] - p0[0], p1[1] - p0[1]
        L = max(1e-6, math.hypot(vx, vy))
        nx, ny = -vy / L, vx / L
        side = 1 if nx * lx + ny * ly > 0 else -1
        x0, x1 = int(min(p0[0], p1[0]) - w - 1), int(max(p0[0], p1[0]) + w + 2)
        y0, y1 = int(min(p0[1], p1[1]) - w - 1), int(max(p0[1], p1[1]) + w + 2)
        for y in range(max(0, y0), min(dst.shape[0], y1)):
            for x in range(max(0, x0), min(dst.shape[1], x1)):
                px, py = x + 0.5 - p0[0], y + 0.5 - p0[1]
                t = (px * vx + py * vy) / (L * L)
                if t < -0.15 or t > 1.15:
                    continue
                across = px * nx + py * ny
                if abs(across) > w / 2:
                    continue
                tt = min(1.0, max(0.0, t))
                shades = mats[name][-1][2]
                for b0, b1, sh in mats[name]:
                    if b0 <= tt <= b1:
                        shades = sh
                        break
                k = across * side / (w / 2)
                c = shades[0] if k > 0.35 else (shades[2] if k < -0.45 else shades[1])
                if (y, x) not in col or name == "fore":
                    col[(y, x)] = c
                m[y, x] = True
    for (y, x), c in col.items():
        dst[y, x] = (*c, 255)
    if outline is not None:
        ring = ~m & np.pad(m, 1)[2:, 1:-1] | ~m & np.pad(m, 1)[:-2, 1:-1] | ~m & np.pad(m, 1)[1:-1, 2:] | \
            ~m & np.pad(m, 1)[1:-1, :-2]
        ring &= dst[..., 3] == 0
        dst[ring] = (*outline, 255)
    return m


# ------------------------------------------------------------------------------------------------ legs
def swing_leg(a, mask, hip_row, ankle_row, dx, lift=0, drop=0):
    """The leg's squares as a straight leg turned about hip_row: rows above ankle_row moved in proportion, the boot
    (ankle_row down) moved dx columns whole and lifted `lift` rows; everything dropped `drop` rows with the body."""
    shin = np.zeros_like(a)
    boot = np.zeros_like(a)
    for r, c in zip(*np.nonzero(mask & (a[..., 3] > 0))):
        if r < ankle_row:
            sh = int(math.floor(dx * max(0, r - hip_row) / max(1, ankle_row - hip_row) + 0.5))
            rr, tgt = r + drop, shin
        else:
            sh = int(math.floor(dx + 0.5))
            rr, tgt = r - lift + drop, boot
        if 0 <= rr < a.shape[0] and 0 <= c + sh < a.shape[1]:
            tgt[rr, c + sh] = a[r, c]
    return put(shin, boot, 0, 0)


# ------------------------------------------------------------------------------------------------ whole figure
def scale2x(s):
    """EPX / Scale2x."""
    H, W = s.shape[:2]
    out = np.zeros((H * 2, W * 2, 4), np.uint8)
    p = np.pad(s, ((1, 1), (1, 1), (0, 0)))
    eq = lambda u, v: (u == v).all(-1)
    for y in range(H):
        for x in range(W):
            P = p[y + 1, x + 1]
            A, B, C, D = p[y, x + 1], p[y + 1, x + 2], p[y + 1, x], p[y + 2, x + 1]
            o = [P, P, P, P]
            if eq(C, A) and not eq(C, D) and not eq(A, B):
                o[0] = A
            if eq(A, B) and not eq(A, C) and not eq(B, D):
                o[1] = B
            if eq(D, C) and not eq(D, B) and not eq(C, A):
                o[2] = C
            if eq(B, D) and not eq(B, A) and not eq(D, C):
                o[3] = D
            out[2 * y, 2 * x], out[2 * y, 2 * x + 1], out[2 * y + 1, 2 * x], out[2 * y + 1, 2 * x + 1] = o
    return out


def turn(part, deg):
    """RotSprite: the part turned deg counter-clockwise on screen about its joint (quarter turns exact)."""
    q = deg / 90.0
    if abs(q - round(q)) < 1e-9:
        k = int(round(q)) % 4
        s = np.rot90(part.s, k).copy()
        jx, jy = part.j
        H, W = part.s.shape[:2]
        for _ in range(k):
            jx, jy = jy, W - jx
            H, W = W, H
        return Part(s, (jx, jy))
    big = scale2x(scale2x(scale2x(part.s)))
    f = 8
    th = math.radians(deg)
    c, s_ = math.cos(th), math.sin(th)
    H, W = part.s.shape[:2]
    jx, jy = part.j
    corners = [(-jx, -jy), (W - jx, -jy), (-jx, H - jy), (W - jx, H - jy)]
    rx = [x * c + y * s_ for x, y in corners]
    ry = [-x * s_ + y * c for x, y in corners]
    x0, x1, y0, y1 = math.floor(min(rx)) - 1, math.ceil(max(rx)) + 1, math.floor(min(ry)) - 1, math.ceil(max(ry)) + 1
    out = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
    for y in range(y1 - y0):
        for x in range(x1 - x0):
            X, Y = x + x0 + 0.5, y + y0 + 0.5
            sx = X * c - Y * s_ + jx
            sy = X * s_ + Y * c + jy
            bx, by = int(math.floor(sx * f)), int(math.floor(sy * f))
            if 0 <= bx < W * f and 0 <= by < H * f:
                out[y, x] = big[by, bx]
    return Part(out, (-x0, -y0))


# ------------------------------------------------------------------------------------------------ finish + audit
def holes(a):
    """Enclosed clear components (4-connected), as lists of (y, x)."""
    op = a[..., 3] > 0
    H, W = op.shape
    seen = np.zeros((H, W), bool)
    st = [(y, x) for y in range(H) for x in (0, W - 1)] + [(y, x) for x in range(W) for y in (0, H - 1)]
    st = [p for p in st if not op[p]]
    for p in st:
        seen[p] = True
    while st:
        y, x = st.pop()
        for dy, dx in N4:
            ny, nx = y + dy, x + dx
            if 0 <= ny < H and 0 <= nx < W and not op[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                st.append((ny, nx))
    hole = ~op & ~seen
    out, lab = [], np.zeros((H, W), bool)
    for y, x in zip(*np.nonzero(hole)):
        if lab[y, x]:
            continue
        comp, st = [], [(y, x)]
        lab[y, x] = True
        while st:
            cy, cx = st.pop()
            comp.append((cy, cx))
            for dy, dx in N4:
                ny, nx = cy + dy, cx + dx
                if hole[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = True
                    st.append((ny, nx))
        out.append(comp)
    return out


def pieces(a):
    """8-connected opaque components, largest first."""
    op = a[..., 3] > 0
    H, W = op.shape
    lab = np.zeros((H, W), bool)
    comps = []
    for y, x in zip(*np.nonzero(op)):
        if lab[y, x]:
            continue
        comp, st = [], [(y, x)]
        lab[y, x] = True
        while st:
            cy, cx = st.pop()
            comp.append((cy, cx))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < H and 0 <= nx < W and op[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = True
                        st.append((ny, nx))
        comps.append(comp)
    return sorted(comps, key=len, reverse=True)


def fill_pinholes(a, most, outline):
    """Enclosed gaps of up to `most` squares take the commonest non-outline colour round them."""
    for comp in holes(a):
        if len(comp) > most:
            continue
        cs = set(comp)
        nb = Counter()
        for y, x in comp:
            for dy, dx in N4:
                q = (y + dy, x + dx)
                if q not in cs and a[q][3] and tuple(int(v) for v in a[q][:3]) != tuple(outline):
                    nb[tuple(int(v) for v in a[q])] += 1
        col = np.array(nb.most_common(1)[0][0] if nb else tuple(outline) + (255,), np.uint8)
        for y, x in comp:
            a[y, x] = col
    return a


def orphan_outline(a, outline):
    """Outline squares with no coloured square among their 8 neighbours."""
    op = a[..., 3] > 0
    ink = op & (a[..., :3] == np.array(outline, np.uint8)).all(-1)
    col = np.pad(op & ~ink, 1)
    H, W = op.shape
    near = np.zeros((H, W), bool)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy or dx:
                near |= col[1 + dy:1 + dy + H, 1 + dx:1 + dx + W]
    return ink & ~near


def finish(a, outline, soles, keep=None, pinholes=3):
    """Pinholes filled, the outline closed round moved edges (never under the soles), stray outline squares and
    crumbs under 3 squares gone, pinholes the completion shut filled. `keep` squares (a pasted head) never change."""
    a = fill_pinholes(a.copy(), pinholes, outline)
    low = int(np.nonzero(a[..., 3].any(1))[0].max())
    a, _, _ = strips.complete_outline(a, color=tuple(outline), feet=max(soles, low), keep=keep)
    while True:
        gone = orphan_outline(a, outline)
        if keep is not None:
            gone &= ~keep
        if not gone.any():
            break
        a[gone] = 0
    for comp in pieces(a)[1:]:
        if len(comp) < 3:
            for y, x in comp:
                a[y, x] = 0
    return fill_pinholes(a, 2, outline)


def audit(frames, idle, outline, soles):
    """Per frame: pieces, enclosed holes, orphan outline squares, squares below the soles, area / idle area."""
    base = int((idle[..., 3] > 0).sum())
    rows = []
    for f in frames:
        op = f[..., 3] > 0
        rows.append(dict(pieces=len(pieces(f)), holes=sum(len(h) for h in holes(f)),
                         orphans=int(orphan_outline(f, outline).sum()), below=int(op[soles + 1:].sum()),
                         area=round(int(op.sum()) / base, 2)))
    return rows


# ------------------------------------------------------------------------------------------------ output
def layout(n):
    cols = {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)
    return cols, -(-n // cols)


def to_sheet(frames, cell, cell_pivot, pivot):
    """Frames (128x128 canvases, the standing point at `pivot`) into a strip of cells, the point at cell_pivot."""
    cw, ch = cell
    cols, rows = layout(len(frames))
    out = np.zeros((rows * ch, cols * cw, 4), np.uint8)
    for i, f in enumerate(frames):
        X, Y = (i % cols) * cw, (i // cols) * ch
        y0, x0 = pivot[1] - cell_pivot[1], pivot[0] - cell_pivot[0]
        src = np.zeros((ch, cw, 4), np.uint8)
        ys0, xs0 = max(0, y0), max(0, x0)
        ys1, xs1 = min(128, y0 + ch), min(128, x0 + cw)
        src[ys0 - y0:ys1 - y0, xs0 - x0:xs1 - x0] = f[ys0:ys1, xs0:xs1]
        if int(f[..., 3].astype(bool).sum()) != int(src[..., 3].astype(bool).sum()):
            raise SystemExit(f"frame {i + 1}: part of it falls outside the {cw}x{ch} cell")
        out[Y:Y + ch, X:X + cw] = src
    return out


def write_strips(hero, built, ms, out_dir, cell, cell_pivot, pivot, check=False):
    """<hero>_<tag>.png (8x) and <hero>_cells.json; with check, compare instead of writing. Returns the tags that
    differ."""
    bad = []
    for tag, frs in built.items():
        big = Image.fromarray(np.repeat(np.repeat(to_sheet(frs, cell, cell_pivot, pivot), Z, 0), Z, 1))
        path = os.path.join(out_dir, f"{hero}_{tag}.png")
        if check:
            same = os.path.exists(lp(path)) and np.array_equal(np.asarray(Image.open(lp(path)).convert("RGBA")),
                                                                np.asarray(big))
            if not same:
                bad.append(tag)
        else:
            big.save(lp(path))
    cells = {"cell": list(cell), "scale": Z,
             "tags": {tag: [{"pivot": list(cell_pivot), "ms": m} for m in ms[tag]] for tag in built}}
    text = json.dumps(cells, indent=1) + "\n"
    cpath = os.path.join(out_dir, f"{hero}_cells.json")
    if check:
        if not (os.path.exists(lp(cpath)) and open(lp(cpath), encoding="utf-8").read() == text):
            bad.append("cells")
    else:
        with open(lp(cpath), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    return bad


def crop_box(frames, pad=2):
    ys, xs = [], []
    for f in frames:
        y, x = np.nonzero(f[..., 3] > 0)
        ys += [y.min(), y.max()]
        xs += [x.min(), x.max()]
    return max(0, min(xs) - pad), min(128, max(xs) + pad + 1), max(0, min(ys) - pad), min(128, max(ys) + pad + 1)


def review_sheet(rows, path, z=4, soles=None, bg=(110, 120, 108)):
    """rows: [(label, [frames])] -> one PNG, every tile cropped to the real extent of all frames, the soles line."""
    allf = [f for _, frs in rows for f in frs]
    x0, x1, y0, y1 = crop_box(allf)
    W, H = (x1 - x0) * z, (y1 - y0) * z
    n = max(len(frs) for _, frs in rows)
    img = Image.new("RGB", (n * (W + 6) + 6, len(rows) * (H + 20) + 4), (40, 40, 40))
    d = ImageDraw.Draw(img)
    for r, (label, frs) in enumerate(rows):
        Y = r * (H + 20) + 18
        d.text((4, Y - 15), label, fill=(255, 255, 255))
        for i, f in enumerate(frs):
            tile = Image.new("RGBA", (W, H), bg + (255,))
            tile.alpha_composite(Image.fromarray(f[y0:y1, x0:x1]).resize((W, H), Image.NEAREST))
            if soles is not None:
                ImageDraw.Draw(tile).line([(0, (soles + 1 - y0) * z), (W, (soles + 1 - y0) * z)], fill=(60, 60, 200, 255))
            img.paste(tile.convert("RGB"), (6 + i * (W + 6), Y))
    img.save(path)


def review_gif(rows, ms, path, z=4, bg=(110, 120, 108)):
    """rows: [(tag, [frames])], ms: {tag: [ms]} -> one GIF playing every strip in turn at its own timing."""
    allf = [f for _, frs in rows for f in frs]
    x0, x1, y0, y1 = crop_box(allf)
    W, H = (x1 - x0) * z, (y1 - y0) * z
    imgs, durs = [], []
    for tag, frs in rows:
        for _ in range(2):
            for f, m in zip(frs, ms[tag]):
                tile = Image.new("RGBA", (W, H + 16), bg + (255,))
                tile.alpha_composite(Image.fromarray(f[y0:y1, x0:x1]).resize((W, H), Image.NEAREST), (0, 16))
                ImageDraw.Draw(tile).text((4, 2), tag, fill=(255, 255, 255, 255))
                imgs.append(tile.convert("P", palette=Image.ADAPTIVE))
                durs.append(max(20, int(m)))
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=durs, loop=0, disposal=2)
