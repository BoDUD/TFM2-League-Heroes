#!/usr/bin/env python3
"""Codex's step-2 strips of Renekton cleaned into assets/source/native/renekton_<tag>.png, which import_native.py reads.
The strips are Codex's rig (codex_strips/rig/rebuild.py) run again on the narrowed design (design_renekton.py step 7,
the ban/pick card: 「雷克顿在BP画面里太大了」), in assets/source/renekton/codex_strips_narrow/ (its rig/rebuild.py gives
the blade arm and the tail every square left of the body that the old outlines left to the core, so a swung blade
leaves no ghost behind; its idle is the narrowed design six times).

    python tools/art/fix_renekton_strips.py [--check]

Codex drew the actions as a rig of the approved design's parts (codex_strips/rig: head, core, near arm with the
blade, far arm, both legs, tail; whole-part moves and nearest-neighbour turns). Two things the user pointed at,
2026-10-07, each fixed alone (every other square stays Codex's):
  1. 「腿上有多余的像素 清理干净一点」: loose outline ink left where a part's outline was cut from its part.
     STRAY: a near-black cluster (8-connected, at most STRAY_MAX squares) that touches no coloured square goes (beside
     the front knee in the run, attack, Q, E and R frames; three in the fall). LEGS: in the legs' rows (LEG_ROWS above
     the feet line) a near-black square with no opaque 4-neighbour - hanging on by a corner - goes (the back leg in
     the run). A wider "dangling outline tip" rule also clipped the blade's spike tips: not used.
  2. 「死亡的时候尾巴有点怪啊」: in the corpse frames (dead 4-8, the body turned 90 degrees onto his back) the rig
     turned the tail with the body, so it stuck straight down under the back leg. Its squares (the rig's own tail
     part, placed as the rig places the frame) are taken out and turned TAIL_TURN degrees about its root (the tail
     square nearest the back leg) to lie along the ground beside the feet, drawn behind the body.
  3. 「鳄鱼走路有点僵硬啊」: Codex's run moved only the two legs (whole pieces crossing over) and lifted the whole
     frame a row on two of the eight; the body, both arms, the blade and the tail stood still. The run is recomposed
     from the same rig parts with Codex's leg moves kept and RUN's additions: the upper body (core, head, arms, tail)
     sinks a row on each landing (frames 1 and 5) with the feet on the ground in every frame, the far arm swings
     forward and back against the legs (whole, up to 2 columns), the blade arm the other way (1 column, a row up while
     the legs pass). 「尾巴都变形了」 then 「尾巴跟着后腿太怪了 还不如翘起来」: the tail is the small hooked strip at
     the lower left (TAIL_BOX: columns <= 44, rows >= 91 of the design; Codex's back-leg part had swallowed most of it,
     so it stepped with the leg); in the run it is its own piece, raised RUN_TAIL degrees about its root at the hip
     and riding with the body, behind everything (most of it tucks behind the blade, its tip shows).
     「还有走路时候腿部模型严重变形」: the rig only moved the shins (up to 24 columns, to cross them) while the thighs stayed
     in the body piece; the user picked a leg pack for Codex (tools/art/pack_renekton_run.py, RUN_SWAP.md). The run is
     now Codex's (assets/source/renekton/codex_run/renekton_run.png: whole legs redrawn crossing, the tail raised behind
     him, our upper body pasted back), recomposed here from its layers (codex_run/layers: the legs per frame, one
     upper body with a shift per frame; the tail is what the finished frame holds beyond the two). 「这里还是有问题啊
     腿的连接处 之前别的英雄有过处理方法啊」: the upper body still carried the tops of both thighs and a stub of the
     right kilt flap (design rows 83-86, left in by my cut at row 87), hanging in the air when Codex's legs stepped away
     (league_brand's belt-and-seat case): THIGH_TOPS trims them before the legs go on; import_native closes the outline.
     run_frame (the parts recomposition) stays for reference.
  4. 「待机时攻击时放技能时尾巴看不到啊」: the narrowed design's only tail was the small hook under the blade. The tail
     Codex drew for the run (codex_run/raw/tail.png, frame 1: a 32 x 22 crocodile tail, root lower right, tip upper
     left; read back on its grid, its chroma fringe to ink, every square to the design's nearest colour) is drawn
     behind him in every frame (the user's pick 「A 斜向后上翘」): its root at TAIL_AT behind the hip, raised back and up,
     its tip out past the blade. In the rig's frames the body's place comes from matching the rig's core piece (the
     body never turns there); the run uses Codex's upper-body shifts. The falling and lying death frames (dead 3-8)
     keep their own (fix 2).
  5. 「鳄鱼放大时这里有点缺失像素啊」 (R's frames 2-5): where the blade arm swung away, the body it had covered in the
     design was never drawn, so the background showed through between the body and the hip. VACATED: squares of a frame
     that are clear, enclosed by the figure, and sat under the blade arm in the design (its rig part, placed by the
     body's offset; only the body side, design columns >= ARM_BODY_X) are filled from their filled neighbours,
     outward in, with the body's teal (the commonest teal next to each square, else the shade); the rest of the
     frame is untouched.
"""
import argparse
import json
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "renekton", "codex_strips_narrow")
RIG = os.path.join(SRC, "rig", "source_parts")
OUT = os.path.join(ROOT, "assets", "source", "native")
Z = 8
DARK = 25            # luminance under which a square is outline ink
STRAY_MAX = 6
FEET = 81            # the feet line in a cell (codex_strips/manifest.json feet_row)
LEG_ROWS = 14
TAIL_TURN = 90       # degrees counter-clockwise, about the tail's root
CORPSE = range(3, 8)  # dead frames (0-based) lying at 90 degrees
# the rig's death (codex_strips/rig/rebuild.py config 'dead'): body turn, whole-body x offset, near arm
D_ROT = [0, 0, 45, 90, 90, 90, 90, 90]
D_DX = [-1, -3, -3, -3, -3, -3, -3, -3]
# the rig's run (rebuild.py config 'run'): each leg piece moved whole, crossing over
R_NEAR = [(23, 0), (19, -1), (13, -2), (7, -2), (1, 0), (5, 0), (11, 1), (17, 0)]       # the back (near) leg
R_FAR = [(-25, 0), (-21, 0), (-15, 1), (-9, 0), (-3, 0), (-7, -1), (-13, -2), (-19, -2)]  # the front leg, a shade darker
# fix 3: the upper body's sink, the far arm's and the blade arm's swing (dx, dy), the tail's sway
RUN = {"body_dy": [1, 0, 0, 0, 1, 0, 0, 0],
       "far": [(2, 0), (1, 0), (0, 0), (-1, 0), (-2, 0), (-1, 0), (0, 0), (1, 0)],
       "near": [(-1, 0), (-1, 0), (0, -1), (1, 0), (1, 0), (1, 0), (0, -1), (-1, 0)]}
TAIL_BOX = (44, 91)      # the design's tail: columns <= 44, rows >= 91
TAIL_ROOT = (45, 92)     # its root at the hip
RUN_TAIL = -60           # degrees (clockwise: raised behind him)
DESIGN = os.path.join(OUT, "renekton_native.png")
CODEX_RUN = os.path.join(ROOT, "assets", "source", "renekton", "codex_run")
TAIL_AT = (54, 90)       # fix 4: the tail picture's lower-right corner (its root) on the design canvas
NO_TAIL = {("dead", i) for i in range(2, 8)}
ARM_BODY_X = 44          # fix 5: the blade arm's squares from this design column on lie over the body
BODY_TEAL = [(1, 128, 132), (2, 89, 95)]   # fix 5: the side of his body behind the arm - its teal, light and shade
BLADE_COLOURS = {(249, 238, 219), (238, 207, 161), (203, 163, 116), (247, 164, 11), (243, 130, 2), (168, 110, 8),
                 (69, 58, 4), (2, 24, 178), (1, 14, 132)}
CELL_DY = 18             # a design row - CELL_DY = its row in a run cell (the feet on row 81, the design's on 99)
# design rows 83-86: the thigh tops under the belt - the left thigh's teal (columns 55-59) and everything right of the
# kilt (the right kilt flap's stub from its top at the belt, the right thigh's top and their outline)
THIGH_ROWS = range(83, 87)
LEFT_THIGH = range(55, 60)
RIGHT_OF_KILT = {83: 71, 84: 70, 85: 70, 86: 70}
TEAL = {(1, 128, 132), (2, 89, 95)}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def label(m):
    h, w = m.shape
    lab = np.zeros((h, w), int)
    n = 0
    for y0, x0 in zip(*np.nonzero(m)):
        if lab[y0, x0]:
            continue
        n += 1
        st = [(y0, x0)]
        lab[y0, x0] = n
        while st:
            y, x = st.pop()
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h and 0 <= nx < w and m[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = n
                        st.append((ny, nx))
    return lab, n


def grow4(m):
    g = np.zeros_like(m)
    g[1:] |= m[:-1]
    g[:-1] |= m[1:]
    g[:, 1:] |= m[:, :-1]
    g[:, :-1] |= m[:, 1:]
    return g


def ink(c):
    op = c[..., 3] > 0
    return op, op & ((c[..., :3] * [0.299, 0.587, 0.114]).sum(-1) < DARK)


def clean(c):
    """Fix 1 on one frame (1x RGBA): returns the cleaned frame and the squares removed."""
    c = c.copy()
    gone = []
    op, dark = ink(c)
    lab, n = label(dark)
    for j in range(1, n + 1):
        m = lab == j
        if m.sum() <= STRAY_MAX and not (grow4(m) & op & ~dark).any():
            gone += [tuple(p) for p in np.argwhere(m)]
            c[m] = 0
    op, dark = ink(c)
    nb = np.zeros(op.shape, int)
    nb[1:] += op[:-1]
    nb[:-1] += op[1:]
    nb[:, 1:] += op[:, :-1]
    nb[:, :-1] += op[:, 1:]
    rows = np.zeros(op.shape, bool)
    rows[FEET - LEG_ROWS:FEET + 1] = True
    corner = dark & (nb == 0) & rows
    gone += [tuple(p) for p in np.argwhere(corner)]
    c[corner] = 0
    return c, gone


# ---------------------------------------------------------------------------------------------- fix 2: the tail
def moved(im, dx=0, dy=0, angle=0, anchor=(64, 88)):
    """The rig's own move/turn (rebuild.py)."""
    canvas = Image.new("RGBA", (256, 256))
    canvas.alpha_composite(im, (64 + int(dx), 64 + int(dy)))
    if angle:
        canvas = canvas.rotate(angle, Image.Resampling.NEAREST, center=(64 + anchor[0] + dx, 64 + anchor[1] + dy))
    return canvas.crop((64, 64, 192, 192))


def placed(parts, i, pivot, layer):
    """The rig's placement of dead frame i (whole model's box -> tx, ty) applied to one part."""
    full = Image.new("RGBA", (128, 128))
    for n in ("tail", "frontleg", "rearleg", "core", "far"):
        full.alpha_composite(parts[n])
    full.alpha_composite(moved(parts["near"], 9 if i >= 3 else 0, 0, -90, anchor=(55, 71)))
    full.alpha_composite(parts["head"])
    bx = moved(full, angle=D_ROT[i]).getbbox()
    tx, ty = pivot[0] - 64 + D_DX[i], pivot[1] - 88
    if bx[3] + ty > FEET + 1:
        ty -= bx[3] + ty - FEET - 1
    f = Image.new("RGBA", (128, 96))
    f.alpha_composite(moved(parts[layer], angle=D_ROT[i]), (tx, ty))
    return np.array(f)


def lay_tail(c, parts, i, pivot):
    tail = placed(parts, i, pivot, "tail")
    rear = placed(parts, i, pivot, "rearleg")
    shown = (tail[..., 3] > 0) & (np.abs(c.astype(int) - tail.astype(int)).sum(-1) == 0)
    ys, xs = np.nonzero(tail[..., 3] > 0)
    ry, rx = np.nonzero(rear[..., 3] > 0)
    _, oy, ox = min((min((y - a) ** 2 + (x - b) ** 2 for a, b in zip(ry, rx)), y, x) for y, x in zip(ys, xs))
    body = c.copy()
    body[shown] = 0
    out = Image.fromarray(tail).rotate(TAIL_TURN, Image.Resampling.NEAREST, center=(int(ox), int(oy)))
    out.alpha_composite(Image.fromarray(body))
    return np.array(out), int(shown.sum())


# ---------------------------------------------------------------------------------------------- fix 3: the run
def darken(im):
    """The rig's far-leg shade (rebuild.py darken)."""
    a = np.array(im)
    mp = {(1, 128, 132): (2, 89, 95), (2, 89, 95): (2, 89, 95), (194, 192, 192): (147, 145, 145),
          (147, 145, 145): (75, 72, 80), (2, 24, 178): (1, 14, 132)}
    for old, new in mp.items():
        m = (a[:, :, :3] == old).all(2) & (a[:, :, 3] > 0)
        a[m, :3] = new
    return Image.fromarray(a)


def run_parts(parts):
    """The rig's parts with the design's tail strip taken out of every part and made a piece of its own."""
    d = np.array(Image.open(lp(DESIGN)).convert("RGBA"))
    yy, xx = np.indices(d.shape[:2])
    m = (d[..., 3] > 0) & (xx <= TAIL_BOX[0]) & (yy >= TAIL_BOX[1])
    out = {}
    for name, im in parts.items():
        a = np.array(im)
        a[m] = 0
        out[name] = Image.fromarray(a)
    tail = np.zeros_like(d)
    tail[m] = d[m]
    out["tail"] = Image.fromarray(tail)
    return out


def run_frame(parts, i, pivot):
    by = RUN["body_dy"][i]
    im = Image.new("RGBA", (128, 128))
    im.alpha_composite(moved(parts["tail"], 0, by, RUN_TAIL, anchor=TAIL_ROOT))    # raised, with the body
    im.alpha_composite(moved(darken(parts["frontleg"]), *R_FAR[i]))
    im.alpha_composite(moved(parts["rearleg"], *R_NEAR[i]))
    im.alpha_composite(moved(parts["core"], 0, by))
    fx, fy = RUN["far"][i]
    im.alpha_composite(moved(parts["far"], fx, by + fy))
    nx, ny = RUN["near"][i]
    im.alpha_composite(moved(parts["near"], nx, by + ny))
    im.alpha_composite(moved(parts["head"], 0, by))
    tx, ty = pivot[0] - 64, pivot[1] - 88
    bx = im.getbbox()
    if bx[3] + ty > FEET + 1:
        ty -= bx[3] + ty - FEET - 1
    f = Image.new("RGBA", (128, 96))
    f.alpha_composite(im, (tx, ty))
    return np.array(f)


def raised_tail():
    """Fix 4: Codex's run tail (raw/tail.png, the first of its 4 x 2 cells) read back on its grid, in the design's colours."""
    import sys
    sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
    from regrid import regrid
    im = np.array(Image.open(lp(os.path.join(CODEX_RUN, "raw", "tail.png"))).convert("RGBA"))
    green = (im[..., 1] > 200) & (im[..., 0] < 90) & (im[..., 2] < 90)
    im[green, 3] = 0
    r, _, _ = regrid(im[:im.shape[0] // 2, :im.shape[1] // 4])
    r[r[..., 3] < 128] = 0
    r[r[..., 3] > 0, 3] = 255
    ys, xs = np.nonzero(r[..., 3] > 0)
    t = r[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    op = t[..., 3] > 0
    fringe = op & (t[..., 1].astype(int) > t[..., 0].astype(int) + 40) & (t[..., 1].astype(int) > t[..., 2].astype(int) + 40)
    t[fringe] = (4, 4, 3, 255)
    d = np.array(Image.open(lp(DESIGN)).convert("RGBA"))
    pal = np.array(sorted({tuple(c) for c in d[d[..., 3] > 0][:, :3].tolist()}))
    op = t[..., 3] > 0
    t[op, :3] = pal[np.argmin(((t[op][:, None, :3].astype(int) - pal[None]) ** 2).sum(-1), 1)]
    return t


def tail_behind(c, tail, x, y):
    """The tail with its lower-right corner on (x, y) of cell c, only where c is clear (behind everything)."""
    h, w = tail.shape[:2]
    x0, y0 = x - w + 1, y - h + 1
    out = c.copy()
    for ty in range(h):
        for tx in range(w):
            cy, cx = y0 + ty, x0 + tx
            if tail[ty, tx, 3] and 0 <= cy < out.shape[0] and 0 <= cx < out.shape[1] and not out[cy, cx, 3]:
                out[cy, cx] = tail[ty, tx]
    return out


def body_offset(c, core, pivot):
    """Where the rig put the design in cell c: the translation (design -> cell) under which most of the core piece's
    squares match, searched round the pivot's own placement."""
    ys, xs = np.nonzero(core[..., 3] > 0)
    bx, by = pivot[0] - 64, pivot[1] - 88
    best = (-1, bx, by)
    for dy in range(-6, 7):
        for dx in range(-8, 9):
            cy, cx = ys + by + dy, xs + bx + dx
            ok = (cy >= 0) & (cy < c.shape[0]) & (cx >= 0) & (cx < c.shape[1])
            n = int((c[cy[ok], cx[ok]] == core[ys[ok], xs[ok]]).all(-1).sum())
            if n > best[0]:
                best = (n, bx + dx, by + dy)
    return best[1], best[2], best[0] / len(xs)


def enclosed(c):
    """Clear squares the figure closes in (not reachable from the cell's border through clear squares)."""
    op = c[..., 3] > 0
    h, w = op.shape
    out = np.zeros_like(op)
    st = [(y, x) for y in range(h) for x in (0, w - 1)] + [(y, x) for x in range(w) for y in (0, h - 1)]
    st = [p for p in st if not op[p]]
    for p in st:
        out[p] = True
    while st:
        y, x = st.pop()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not op[ny, nx] and not out[ny, nx]:
                out[ny, nx] = True
                st.append((ny, nx))
    return ~op & ~out


def fill_vacated(c, near, ox, oy):
    """Fix 5: enclosed clear squares where the blade arm lay over the body in the design, filled outward in from their
    filled 4-neighbours with the commonest body colour among them (blade colours and outline ink never spread)."""
    ys, xs = np.nonzero(near[..., 3] > 0)
    keep = xs >= ARM_BODY_X
    was = np.zeros(c.shape[:2], bool)
    cy, cx = ys[keep] + oy, xs[keep] + ox
    ok = (cy >= 0) & (cy < c.shape[0]) & (cx >= 0) & (cx < c.shape[1])
    was[cy[ok], cx[ok]] = True
    todo = enclosed(c) & was
    out = c.copy()
    n = int(todo.sum())
    while todo.any():
        done = []
        for y, x in zip(*np.nonzero(todo)):
            cols = []
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < out.shape[0] and 0 <= nx < out.shape[1] and out[ny, nx, 3] and not todo[ny, nx]:
                    col = tuple(int(v) for v in out[ny, nx, :3])
                    if col not in BLADE_COLOURS and (np.array(col) * [0.299, 0.587, 0.114]).sum() >= 25:
                        cols.append(col)
            cols = [col for col in cols if col in BODY_TEAL]
            if cols:
                done.append((y, x, max(set(cols), key=cols.count)))
            elif any(0 <= y + dy < out.shape[0] and 0 <= x + dx < out.shape[1] and out[y + dy, x + dx, 3]
                     and not todo[y + dy, x + dx] for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                done.append((y, x, BODY_TEAL[1]))
        if not done:
            break
        for y, x, col in done:
            out[y, x, :3] = col
            out[y, x, 3] = 255
            todo[y, x] = False
    return out, n


def codex_run():
    """Codex's run (1x sheet) recomposed from its layers with the upper body's thigh tops trimmed."""
    legs = np.array(Image.open(lp(os.path.join(CODEX_RUN, "layers", "redrawn_legs_1x.png"))).convert("RGBA"))
    upper = np.array(Image.open(lp(os.path.join(CODEX_RUN, "layers", "upper_body_clean_1x.png"))).convert("RGBA"))
    final = np.array(Image.open(lp(os.path.join(CODEX_RUN, "renekton_run_1x.png"))).convert("RGBA"))
    with open(lp(os.path.join(CODEX_RUN, "manifest.json")), encoding="utf-8") as f:
        frames = json.load(f)["frames"]
    trimmed = upper.copy()
    for y in THIGH_ROWS:
        r = y - CELL_DY
        for x in range(trimmed.shape[1]):
            c = tuple(int(v) for v in trimmed[r, x, :3])
            if x >= RIGHT_OF_KILT[y] or (x in LEFT_THIGH and c in TEAL):
                trimmed[r, x] = 0
    out = np.zeros_like(final)
    for fr in frames:
        k = fr["frame"] - 1
        X, Y = (k % 4) * 128, (k // 4) * 96
        leg = Image.fromarray(legs[Y:Y + 96, X:X + 128])
        before = Image.new("RGBA", (128, 96))
        before.alpha_composite(leg)
        before.alpha_composite(Image.fromarray(upper), tuple(fr["upper_shift"]))
        cell = Image.new("RGBA", (128, 96))
        cell.alpha_composite(leg)
        cell.alpha_composite(Image.fromarray(trimmed), tuple(fr["upper_shift"]))
        sx, sy = fr["upper_shift"]
        out[Y:Y + 96, X:X + 128] = tail_behind(np.array(cell), TAIL, TAIL_AT[0] + sx, TAIL_AT[1] - CELL_DY + sy)
    return out


def layout(n):
    return {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    cells = json.load(open(lp(os.path.join(OUT, "renekton_cells.json")), encoding="utf-8"))
    parts = {n: Image.open(lp(os.path.join(RIG, f"{n}.png"))).convert("RGBA")
             for n in ("core", "far", "frontleg", "head", "near", "rearleg", "tail")}
    rparts = run_parts(parts)
    global TAIL
    TAIL = raised_tail()
    core = np.array(parts["core"])
    near = np.array(parts["near"])
    cw, ch = cells["cell"]
    total = 0
    for tag, frs in cells["tags"].items():
        if tag == "run":
            img = np.repeat(np.repeat(codex_run(), Z, 0), Z, 1)
        else:
            img = np.array(Image.open(lp(os.path.join(SRC, f"renekton_{tag}.png"))).convert("RGBA"))
        small = img[Z // 2::Z, Z // 2::Z].copy()
        cols = layout(len(frs))
        for i in range(len(frs)):
            y0, x0 = (i // cols) * ch, (i % cols) * cw
            c = small[y0:y0 + ch, x0:x0 + cw]
            if tag == "dead" and i in CORPSE:
                c, moved_n = lay_tail(c, parts, i, frs[i]["pivot"])
                print(tag, i + 1, "tail turned", TAIL_TURN, "degrees,", moved_n, "squares")
            if tag != "run" and (tag, i) not in NO_TAIL:
                ox, oy, share = body_offset(c, core, frs[i]["pivot"])
                if share < 0.9:
                    raise SystemExit(f"{tag} {i + 1}: the body piece matches only {share:.0%} - where is he?")
                c = tail_behind(c, TAIL, TAIL_AT[0] + ox, TAIL_AT[1] + oy)
                c, filled = fill_vacated(c, near, ox, oy)       # after the tail: it closes the gap behind the arm
                if filled:
                    print(tag, i + 1, "vacated squares filled", filled)
            c, gone = clean(c)
            if gone:
                print(tag, i + 1, len(gone), [(int(y), int(x)) for y, x in gone])
                total += len(gone)
            small[y0:y0 + ch, x0:x0 + cw] = c
        if not a.check:
            Image.fromarray(np.repeat(np.repeat(small, Z, 0), Z, 1)).save(lp(os.path.join(OUT, f"renekton_{tag}.png")))
    print("removed", total, "squares" + (" (check only)" if a.check else ""))


if __name__ == "__main__":
    main()
