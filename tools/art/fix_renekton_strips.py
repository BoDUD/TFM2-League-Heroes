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
    cw, ch = cells["cell"]
    total = 0
    for tag, frs in cells["tags"].items():
        img = np.array(Image.open(lp(os.path.join(SRC, f"renekton_{tag}.png"))).convert("RGBA"))
        small = img[Z // 2::Z, Z // 2::Z].copy()
        cols = layout(len(frs))
        for i in range(len(frs)):
            y0, x0 = (i // cols) * ch, (i % cols) * cw
            c = small[y0:y0 + ch, x0:x0 + cw]
            if tag == "run":
                c = run_frame(rparts, i, frs[i]["pivot"])
            if tag == "dead" and i in CORPSE:
                c, moved_n = lay_tail(c, parts, i, frs[i]["pivot"])
                print(tag, i + 1, "tail turned", TAIL_TURN, "degrees,", moved_n, "squares")
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
