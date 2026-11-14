"""Procedural pixel art for the summoned units' sheets that are drawn by code rather than cut from effect frames
(tools/art/unit_malzahar_voidling.py, tools/art/unit_elise_spiderling.py; 2026-11-14, the user: 「马尔扎哈和蜘蛛的召唤物画高清
点啊 现在像什么 一个不像虫子 一个不像蜘蛛 模糊不清」).

A unit is drawn as shapes in game pixels (x right, y down, the pivot at 0, 0; a unit's ground row FEET under it) and every
frame is sampled twice: on the 1x grid (a square a game pixel, its centre on whole coordinates) and on the dense grid of
the unit's PPU (`d` squares a game pixel, d x d of them inside each 1x square), each square taking the shape over its
centre - hard edges, no blending, so both are crisp and both are the same drawing. The dense frame is exactly d times the
1x frame and both are centred on the pivot (hd_engine draws a frame's centre on the unit; tools/art/zyra_thicket_size.py
does the same for an effect), so the two grids line up square for square.

    Raster(d)                  the sample grid of one density
    ellipse / polygon / capsule / line_cells
                               masks and pixel runs on it
    Body                       solid parts back to front -> colours, a dark line where a part lies over another, the
                               silhouette outline
    shift / over               whole-square moves of a finished layer (a rigid part stays the same pixels)
    ik2                        a two-bone limb's knee from its hip and foot
    stroke                     a thin jointed limb, one square wide at 1x, two dense
    build_unit                 every pose at 1x and dense, with the rigid part's span and how much of it shows
    write_unit                 the 1x tags and their hd_ twins -> name#sheet.png + #anim.fanim (or --check)
    contact / beside           the review sheets (every frame of every tag at 3x, 1x and dense rows, the rigid part's
                               top and bottom across; the unit next to its summoner at game scale)
"""
import json
import os
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

FEET = 11                       # a unit's ground row under the pivot (a champion's): the soles' squares end at 11.5
GROUND = FEET + 0.5
CHAMPIONS = os.path.join(ROOT, "league", "champions")


# ----------------------------------------------------------------------------------------------------------- the grid
class Raster:
    """The sample grid of density `d`: 1x columns -half..half and rows -up..down, d x d squares in each; X, Y hold every
    square's centre in game pixels."""

    def __init__(self, d, half=24, up=24, down=14):
        self.d, self.half, self.up, self.down = d, half, up, down
        self.w, self.h = (2 * half + 1) * d, (up + down + 1) * d
        self.xs = (np.arange(self.w) + 0.5) / d - half - 0.5
        self.ys = (np.arange(self.h) + 0.5) / d - up - 0.5
        self.X, self.Y = np.meshgrid(self.xs, self.ys)

    def blank(self):
        return np.zeros((self.h, self.w, 4), np.uint8)

    def none(self):
        return np.zeros((self.h, self.w), bool)

    def cell(self, x, y):
        """(row, column) of the square holding game point x, y"""
        return int(np.floor((y + self.up + 0.5) * self.d)), int(np.floor((x + self.half + 0.5) * self.d))


def ellipse(R, cx, cy, rx, ry, a=0.0):
    """(mask, u, v): the ellipse's squares and every square's place in it, u along the axis turned `a` radians from x (y
    down), v across, both -1..1 inside"""
    dx, dy = R.X - cx, R.Y - cy
    c, s = np.cos(a), np.sin(a)
    u = (dx * c + dy * s) / rx
    v = (-dx * s + dy * c) / ry
    return u * u + v * v <= 1.0, u, v


def polygon(R, pts):
    """the squares whose centres are inside the polygon (even-odd)"""
    inside = R.none()
    n = len(pts)
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        if y0 == y1:
            continue
        cross = ((R.Y >= min(y0, y1)) & (R.Y < max(y0, y1)))
        xi = x0 + (R.Y - y0) * (x1 - x0) / (y1 - y0)
        inside ^= cross & (R.X < xi)
    return inside


def capsule(R, p, q, r0, r1=None):
    """the squares within r of the segment p-q (r going from r0 at p to r1 at q)"""
    r1 = r0 if r1 is None else r1
    (px, py), (qx, qy) = p, q
    vx, vy = qx - px, qy - py
    ll = vx * vx + vy * vy
    t = np.clip(((R.X - px) * vx + (R.Y - py) * vy) / ll, 0.0, 1.0) if ll > 0 else np.zeros_like(R.X)
    dx, dy = R.X - (px + t * vx), R.Y - (py + t * vy)
    return dx * dx + dy * dy <= (r0 + (r1 - r0) * t) ** 2


def line_cells(R, p, q):
    """the squares of a one-square line from game point p to q (Bresenham on the grid: one square a step of the longer
    axis, the ends the squares holding p and q)"""
    (r0, c0), (r1, c1) = R.cell(*p), R.cell(*q)
    out = []
    dr, dc = abs(r1 - r0), abs(c1 - c0)
    sr, sc = (1 if r1 > r0 else -1), (1 if c1 > c0 else -1)
    err = dc - dr
    r, c = r0, c0
    while True:
        out.append((r, c))
        if r == r1 and c == c1:
            break
        e2 = 2 * err
        if e2 > -dr:
            err -= dr
            c += sc
        if e2 < dc:
            err += dc
            r += sr
    return out


def poly_cells(R, pts):
    """a polyline's squares in order, each joint once"""
    out = []
    for p, q in zip(pts, pts[1:]):
        seg = line_cells(R, p, q)
        out.extend(seg[1:] if out else seg)
    return out


def ik2(hip, foot, l1, l2, toward=(0.0, -1.0)):
    """the knee of a two-bone limb from `hip` to `foot` (bones l1, l2), on the side of the line hip -> foot that faces
    `toward` (default up: y grows down); a foot out of reach stretches the limb straight toward it"""
    hx, hy = hip
    fx, fy = foot
    dx, dy = fx - hx, fy - hy
    dist = float(np.hypot(dx, dy)) or 1e-6
    dist_c = min(dist, l1 + l2 - 1e-6)
    a = (l1 * l1 - l2 * l2 + dist_c * dist_c) / (2 * dist_c)
    h = float(np.sqrt(max(l1 * l1 - a * a, 0.0)))
    ux, uy = dx / dist, dy / dist
    nx, ny = uy, -ux
    if nx * toward[0] + ny * toward[1] < 0:
        nx, ny = -nx, -ny
    return hx + ux * a + nx * h, hy + uy * a + ny * h


# ------------------------------------------------------------------------------------------------------------- layers
def over(under, top):
    out = under.copy()
    m = top[..., 3] > 0
    out[m] = top[m]
    return out


def shift(f, dr, dc):
    """f moved dr rows and dc columns (squares of its own grid), what leaves the canvas dropped"""
    out = np.zeros_like(f)
    h, w = f.shape[:2]
    ys, xs = slice(max(0, -dr), min(h, h - dr)), slice(max(0, -dc), min(w, w - dc))
    yd, xd = slice(max(0, dr), min(h, h + dr)), slice(max(0, dc), min(w, w + dc))
    out[yd, xd] = f[ys, xs]
    return out


def edge4(mask):
    """the squares of `mask` with a 4-neighbour outside it"""
    p = np.pad(mask, 1)
    inner = p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
    return mask & ~inner


class Body:
    """Solid parts painted back to front; finish() draws a dark line along every part where it lies over one painted
    before it, then the silhouette's outline (`width` squares deep)."""

    def __init__(self, R):
        self.R = R
        self.rgba = R.blank()
        self.ids = np.full((R.h, R.w), -1, np.int32)
        self.n = 0

    def part(self, mask, colours, seam=True):
        """paint `mask` with `colours` (an rgb tuple or an h x w x 3 array); seam=False: no line where it meets the
        parts under it (a plate drawn on its own part)"""
        col = np.asarray(colours, np.uint8)
        if col.ndim == 1:
            self.rgba[mask, :3] = col
        else:
            self.rgba[mask, :3] = col[mask]
        self.rgba[mask, 3] = 255
        if seam:
            self.ids[mask] = self.n
            self.n += 1
        else:
            self.ids[mask] = max(self.n - 1, 0)
        return mask

    def finish(self, outline, line=None, width=1, keep=None):
        """the lines between the parts, then the outline; `keep`: squares neither touches (an eye's glow)"""
        line = outline if line is None else line
        ids, solid = self.ids, self.ids >= 0
        keep = np.zeros_like(solid) if keep is None else keep
        p = np.pad(ids, 1, constant_values=-1)
        behind = np.zeros_like(solid)
        for nb in (p[:-2, 1:-1], p[2:, 1:-1], p[1:-1, :-2], p[1:-1, 2:]):
            behind |= (nb >= 0) & (nb < ids)
        seams = solid & behind & ~keep
        self.rgba[seams, :3] = line
        ring = np.zeros_like(solid)
        inside = solid.copy()
        for _ in range(width):
            e = edge4(inside)
            ring |= e
            inside &= ~e
        ring &= ~keep
        self.rgba[ring, :3] = outline
        return self.rgba


def tones(level, ramp):
    """an h x w x 3 array: ramp[level] per square (level clipped to the ramp)"""
    ramp = np.asarray(ramp, np.uint8)
    return ramp[np.clip(level, 0, len(ramp) - 1)]


def band(t, cuts):
    """the band of value t: 0 under cuts[0], 1 under cuts[1] ..."""
    out = np.zeros(t.shape, np.int32)
    for c in cuts:
        out += t >= c
    return out


def stroke(R, canvas, pts, core, edge=None, tip=None, tip_len=0.0, joint=None):
    """A thin limb along the polyline `pts` (game px) on `canvas`: at 1x one square wide in `core`; dense, two squares
    wide - the line in `core` with `edge` beside it, under and behind it - so the limb keeps its width in game pixels.
    `tip`: the last `tip_len` game px of it in that colour (a claw); `joint`: the colour of the inner joints' squares."""
    cells = poly_cells(R, pts)
    seg_len = [float(np.hypot(q[0] - p[0], q[1] - p[1])) for p, q in zip(pts, pts[1:])]
    total = sum(seg_len) or 1.0
    n = len(cells)
    h, w = canvas.shape[:2]

    def put(r, c, colour):
        if 0 <= r < h and 0 <= c < w:
            canvas[r, c, :3] = colour
            canvas[r, c, 3] = 255

    tip_from = n - max(1, int(round(n * tip_len / total))) if tip is not None and tip_len > 0 else n
    if R.d > 1 and edge is not None:
        for (r, c) in cells:
            put(r + 1, c, edge)
            put(r, c + 1, edge)
            put(r + 1, c + 1, edge)
    joints = set()
    if joint is not None:
        for p in pts[1:-1]:
            joints.add(R.cell(*p))
    for k, (r, c) in enumerate(cells):
        colour = tip if k >= tip_from else core
        if (r, c) in joints:
            colour = joint
        put(r, c, colour)
    return canvas


def span(mask, R):
    """(left, top, right, bottom) of a mask's squares in game px round the pivot (their outer edges)"""
    ys, xs = np.nonzero(mask)
    if not len(xs):
        return None
    d = R.d
    return (xs.min() / d - R.half - 0.5, ys.min() / d - R.up - 0.5,
            (xs.max() + 1) / d - R.half - 0.5, (ys.max() + 1) / d - R.up - 0.5)


def rigid_check(frame, layer, mask):
    """how much of the rigid part (`mask`: its squares where this frame put it; `layer`: its picture there) the frame
    shows as drawn: (squares shown unchanged, squares of the part)"""
    same = (frame[mask] == layer[mask]).all(axis=-1)
    return int(same.sum()), int(mask.sum())


# -------------------------------------------------------------------------------------------------------------- sheets
def extent(f, R):
    """(half width, rows up, rows down) in 1x squares of the opaque part of a canvas of grid R, round the pivot"""
    ys, xs = np.nonzero(f[..., 3])
    if not len(xs):
        return 0, 0, 0
    c0, c1 = xs.min() // R.d - R.half, xs.max() // R.d - R.half
    r0, r1 = ys.min() // R.d - R.up, ys.max() // R.d - R.up
    return max(-c0, c1, 0), max(-r0, 0), max(r1, 0)


def crop(f, R, hw, hh):
    """the canvas cut to (2 hw + 1) x (2 hh + 1) 1x squares round the pivot - d times that in its own squares"""
    d = R.d
    x0, y0 = (R.half - hw) * d, (R.up - hh) * d
    return f[y0:y0 + (2 * hh + 1) * d, x0:x0 + (2 * hw + 1) * d].copy()


def frame_pair(f1, R1, fd, Rd):
    """a 1x frame and its dense twin cut to one size: the dense one exactly d times the 1x one, both centred on the pivot;
    an empty frame 3 x 3 (and 3d x 3d)"""
    if not f1[..., 3].any() and not fd[..., 3].any():
        return np.zeros((3, 3, 4), np.uint8), np.zeros((3 * Rd.d, 3 * Rd.d, 4), np.uint8)
    e1, ed = extent(f1, R1), extent(fd, Rd)
    hw = max(e1[0], ed[0])
    hh = max(e1[1], e1[2], ed[1], ed[2])
    return crop(f1, R1, hw, hh), crop(fd, Rd, hw, hh)


def unit_tags(tags1, tagsd, R1, Rd):
    """{tag: [(1x frame, ms)]} and the same of the dense frames -> the sheet's tags: the five 1x tags, then their hd_
    twins (a hero sheet's order)"""
    out1, outd = {}, {}
    for tag in ("idle", "run", "attack", "hit", "dead"):
        a, b = tags1[tag], tagsd[tag]
        if len(a) != len(b) or any(x[1] != y[1] for x, y in zip(a, b)):
            sys.exit(f"{tag}: the 1x and dense frames differ in count or timing")
        pairs = [frame_pair(f1, R1, fd, Rd) for (f1, _), (fd, _) in zip(a, b)]
        out1[tag] = [(p[0], ms) for p, (_, ms) in zip(pairs, a)]
        outd["hd_" + tag] = [(p[1], ms) for p, (_, ms) in zip(pairs, a)]
    return {**out1, **outd}


def build_unit(drawer, poses, timing, ppu):
    """Every pose drawn at 1x and at `ppu`: drawer(R).frame(pose) -> (frame, the rigid part's picture where the frame
    put it, its squares); poses {tag: [pose, or None for an empty frame]}, timing {tag: [ms]}. -> (the sheet's tags, the
    rigid part per sheet tag and frame: (its span in game px, squares shown as drawn, its squares) or None)"""
    out, rigid = [], {}
    for d in (1, ppu):
        R = Raster(d, down=32)              # room under the ground for a part sunk out of sight (its squares still counted)
        D = drawer(R)
        tags = {}
        for tag, ps in poses.items():
            ms = timing[tag]
            if len(ms) != len(ps):
                sys.exit(f"{tag}: {len(ps)} poses, {len(ms)} timings")
            frames, parts = [], []
            for p, t in zip(ps, ms):
                if p is None:
                    frames.append((R.blank(), t))
                    parts.append(None)
                    continue
                f, layer, mask = D.frame(p)
                frames.append((f, t))
                sp = span(mask, R)
                parts.append((sp,) + rigid_check(f, layer, mask) if sp else None)
            tags[tag] = frames
            rigid[("" if d == 1 else "hd_") + tag] = parts
        out.append((R, tags))
    (R1, t1), (Rd, td) = out
    return unit_tags(t1, td, R1, Rd), rigid


def rigid_lines(rigid):
    """{sheet tag: [(top, bottom) of the rigid part, game px, or None]} for contact()"""
    return {tag: [(p[0][1], p[0][3]) if p else None for p in parts] for tag, parts in rigid.items()}


def rigid_text(rigid, name):
    """the rigid part's size in every frame (it must be one size) and how much of it each frame shows as drawn"""
    lines, sizes = [], set()
    for tag, parts in rigid.items():
        cells = []
        for p in parts:
            if p is None:
                cells.append("-")
                continue
            (x0, y0, x1, y1), shown, total = p
            sizes.add((round(x1 - x0, 3), round(y1 - y0, 3), tag.startswith("hd_")))
            cells.append("%.1fx%.1f@(%+.1f,%+.1f) %d%%" % (x1 - x0, y1 - y0, x0, y0, 100 * shown // max(total, 1)))
        lines.append("  %-10s %s" % (tag, " | ".join(cells)))
    one = {k: sorted({(w, h) for w, h, hd in sizes if hd == k}) for k in (False, True)}
    head = "%s rigid part, w x h game px @ (left, top), %% of its squares shown as drawn: 1x %s, dense %s" % (
        name, " / ".join("%gx%g" % s for s in one[False]), " / ".join("%gx%g" % s for s in one[True]))
    return "\n".join([head] + lines), all(len(v) == 1 for v in one.values())


def read_sheet(stem):
    with open(G.lp(stem + "#anim.fanim"), encoding="utf-8-sig") as fh:
        return np.array(Image.open(G.lp(stem + "#sheet.png")).convert("RGBA")), json.load(fh)


def write_unit(name, out_stem, tags, check):
    """write `out_stem`#sheet.png / #anim.fanim from `tags` ({tag: [(frame, ms)]}), or with `check` exit 1 when the
    repo's sheet is not what this writes"""
    if check:
        tmp = os.path.join(tempfile.mkdtemp(prefix="unit_"), name)
        G.write_sheet(tmp, tags)
        same = False
        if os.path.exists(G.lp(out_stem + "#sheet.png")) and os.path.exists(G.lp(out_stem + "#anim.fanim")):
            (px, an), (px2, an2) = read_sheet(out_stem), read_sheet(tmp)
            same = an == an2 and px.shape == px2.shape and bool((px == px2).all())
        print(f"{name}:", "up to date" if same else "stale")
        sys.exit(0 if same else 1)
    w, h = G.write_sheet(out_stem, tags)
    print("wrote %s#sheet.png (%d x %d) and #anim.fanim: %s" % (
        os.path.relpath(out_stem, ROOT), w, h,
        ", ".join("%s %d frames %.2f s" % (t, len(fr), sum(ms for _, ms in fr) / 1000.0) for t, fr in tags.items())))


# ------------------------------------------------------------------------------------------------------------- reviews
def sheet_frames(stem, tag):
    """[(frame, ms)] of a tag of a written sheet"""
    px, an = read_sheet(stem)
    out = []
    for f in an["anims"][tag]["frames"]:
        d = f["data"]
        x, y, w, h = int(d["x"]), int(d["y"]), int(d["w"]), int(d["h"])
        out.append((px[y:y + h, x:x + w], round(f["duration"] * 1000)))
    return out


def beside(figures, path, scale=3, bg=(74, 92, 70), gap=6):
    """Figures side by side at game scale (`scale` screen px a game px), their pivots on one line: each (label, frame,
    game px a square of it) - a 1x frame 1, a dense one 1 / PPU, a hero drawn at a SIZES size that times it. A frame is
    resampled to its game size (nearest, about its centre - the pivot), so a figure's height and width on the picture
    are what the battlefield shows."""
    shown = []
    for label, f, gpx in figures:
        w = max(1, int(round(f.shape[1] * gpx * scale)))
        h = max(1, int(round(f.shape[0] * gpx * scale)))
        shown.append((label, Image.fromarray(f, "RGBA").resize((w, h), Image.NEAREST)))
    up = max(im.height // 2 for _, im in shown)
    down = max(max(im.height - im.height // 2 for _, im in shown), int((FEET + 2) * scale))
    W = sum(im.width + gap * scale for _, im in shown) + gap * scale
    H = up + down + 30
    img = Image.new("RGBA", (W, H), bg + (255,))
    dr = ImageDraw.Draw(img)
    x = gap * scale
    gy = 18 + up + int(round(GROUND * scale))
    dr.line([(0, gy), (W, gy)], fill=(0, 230, 230, 255))
    for label, im in shown:
        img.alpha_composite(im, (x, 18 + up - im.height // 2))
        dr.text((x, 2), label, fill=(255, 255, 0, 255))
        x += im.width + gap * scale
    img.save(path)
    return path


def contact(tags, d, path, rigid=None, zoom=3, bg=(74, 92, 70)):
    """Every frame of every tag as written, 1x rows at `zoom` squares a pixel and the hd_ rows at `zoom` squares a dense
    pixel (so twice as big for d = 2), each on its ground line (cyan) under its pivot (magenta); `rigid`: {sheet tag: [(top,
    bottom) of the rigid part, pivot-relative game px, per frame]} drawn as yellow lines across the frame - the rigid part
    between them in every frame (rigid_lines())."""
    rows = []
    for tag in ("idle", "run", "attack", "hit", "dead"):
        for pre, s in (("", 1), ("hd_", d)):
            rows.append((pre + tag, s, tags[pre + tag], (rigid or {}).get(pre + tag)))
    up = max(max((f.shape[0] // s) // 2 for f, _ in fr) for _, s, fr, _ in rows) + 1
    down = FEET + 2
    cellw = [max(f.shape[1] // s for f, _ in fr) + 4 for _, s, fr, _ in rows]
    label_w = 120
    row_h = []
    for (_, s, fr, _), cw in zip(rows, cellw):
        row_h.append((up + down + 1) * s * zoom + 16)
    width = label_w + max(len(fr) * (cw * s * zoom + 8) for (_, s, fr, _), cw in zip(rows, cellw)) + 8
    img = Image.new("RGBA", (width, sum(row_h) + 8), (34, 34, 42, 255))
    dr = ImageDraw.Draw(img)
    y = 4
    for (tag, s, fr, rig), cw, rh in zip(rows, cellw, row_h):
        dr.text((6, y + rh // 2 - 6), tag, fill=(255, 255, 255, 255))
        x = label_w
        for i, (f, ms) in enumerate(fr):
            W, H = cw * s * zoom, (up + down + 1) * s * zoom
            cell = Image.new("RGBA", (W, H), bg + (255,))
            cd = ImageDraw.Draw(cell)
            hw, hh = (f.shape[1] // s) // 2, (f.shape[0] // s) // 2
            ox = (cw // 2 - hw) * s * zoom
            oy = (up - hh) * s * zoom
            im = Image.fromarray(f, "RGBA").resize((f.shape[1] * zoom, f.shape[0] * zoom), Image.NEAREST)
            cell.alpha_composite(im, (ox, oy))
            gy = (up + FEET + 1) * s * zoom
            cd.line([(0, gy), (W, gy)], fill=(0, 230, 230, 255))
            px, py = (cw // 2) * s * zoom, up * s * zoom
            cd.rectangle([px, py, px + s * zoom - 1, py + s * zoom - 1], outline=(255, 0, 255, 255))
            if rig is not None and i < len(rig) and rig[i] is not None:
                for ry in rig[i]:
                    yy = int(round((up + ry) * s * zoom))
                    cd.line([(0, yy), (W, yy)], fill=(255, 220, 0, 255))
            img.alpha_composite(cell, (x, y + 14))
            dr.text((x + 2, y + 1), "%d  %d ms" % (i, ms), fill=(255, 255, 0, 255))
            x += W + 8
        y += rh
    img.save(path)
    return path
