#!/usr/bin/env python3
"""A hero's idle from Codex's skin swap -> assets/source/native/<hero>_idle.png + the idle rows of <hero>_cells.json.

    python tools/art/idle_swap.py garen [lux ...]

Players saw the pack in ban/pick 「清一色的不动 不然就是动两个像素点」: the idles were the design six times with a 1-row
bob (art-spec "Idle and run are drawn animations"). Codex redrew them from a pack (assets/source/<hero>/codex_idle/:
the prompt, our design image and `idle.json`; oppi's frames used as the skeleton are not redistributed): mode A skins
oppi's idle of the same champion with our design, mode B animates our design after an oppi idle. Its picture
(`raw.png`, cells of `cell` squares in `cols` columns on #00FF00; `idle.json` also keeps the old idle's colours) is read here on the pack's own grid (no resampling),
every square snapped to the colours of our idle (CIELAB nearest), specks off, the frames set on the idle's pivot (the
pack put our soles on row `feet` and our pivot column on the cell's centre line), the outline closed and 1-2 square
pinholes shut. `drop` leaves out frames whose body jumps in size (Jinx 4 and 6 shrink, Darius 3 stretches).
import_native.py takes the idle as drawn (IDLE_SWAP: no ORDER / BOB / retouch / head steadying on it).
"""
import argparse
import json
import os
import sys
from collections import deque

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import regrid as RG  # noqa: E402
import strips as G  # noqa: E402
from native_refs import layout  # noqa: E402

NATIVE = os.path.join(ROOT, "assets", "source", "native")
SOURCE = os.path.join(ROOT, "assets", "source")
Z = 8
OUTLINE = (0x12, 0x03, 0x19)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def lab(rgb):
    c = np.asarray(rgb, float) / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ M.T / np.array([0.9505, 1.0, 1.089])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def pieces(op):
    labs = np.zeros(op.shape, int)
    n = 0
    for y, x in zip(*np.nonzero(op)):
        if labs[y, x]:
            continue
        n += 1
        st = [(y, x)]
        labs[y, x] = n
        while st:
            cy, cx = st.pop()
            for ny in (cy - 1, cy, cy + 1):
                for nx in (cx - 1, cx, cx + 1):
                    if 0 <= ny < op.shape[0] and 0 <= nx < op.shape[1] and op[ny, nx] and not labs[ny, nx]:
                        labs[ny, nx] = n
                        st.append((ny, nx))
    return labs, n


def pinholes(op, most=2):
    """Transparent pockets the outside cannot reach, `most` squares or smaller (larger ones are drawn gaps)."""
    H, W = op.shape
    out = np.zeros_like(op)
    q = deque((y, x) for y in range(H) for x in range(W) if (y in (0, H - 1) or x in (0, W - 1)) and not op[y, x])
    for p in q:
        out[p] = True
    while q:
        y, x = q.popleft()
        for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if 0 <= ny < H and 0 <= nx < W and not op[ny, nx] and not out[ny, nx]:
                out[ny, nx] = True
                q.append((ny, nx))
    labs, n = pieces(~op & ~out)
    return [list(zip(*np.nonzero(labs == i))) for i in range(1, n + 1) if (labs == i).sum() <= most]


def our_idle(hero):
    cells = json.load(open(lp(os.path.join(NATIVE, f"{hero}_cells.json")), encoding="utf-8"))
    cw, ch = cells["cell"]
    a = np.asarray(Image.open(lp(os.path.join(NATIVE, f"{hero}_idle.png"))).convert("RGBA"))[Z // 2::Z, Z // 2::Z]
    return a[0:ch, 0:cw], cells


def read_cells(hero, spec, pal, pal_lab):
    im = np.asarray(Image.open(lp(os.path.join(SOURCE, hero, "codex_idle", "raw.png"))).convert("RGB")).astype(int)
    H, W = im.shape[:2]
    cols, n, S = spec["cols"], spec["n"], spec["cell"]
    rows = -(-n // cols)
    cw, ch = W / cols, H / rows
    s = cw / S
    out = []
    for k in range(n):
        x0, y0 = round((k % cols) * cw), round((k // cols) * ch)
        c = im[y0:round(y0 + ch), x0:round(x0 + cw)]
        r, g, b = c[..., 0], c[..., 1], c[..., 2]
        green = (g > r * 1.25 + 20) & (g > b * 1.25 + 20)
        a = np.zeros(c.shape[:2] + (4,), np.uint8)
        a[..., :3] = c
        a[..., 3] = (~green) * 255
        grid, _, (bx, by) = RG.regrid(a, s)
        op = grid[..., 3] > 127
        d = ((lab(grid[..., :3])[..., None, :] - pal_lab[None, None]) ** 2).sum(-1)
        f = np.zeros_like(grid)
        f[..., :3] = pal[d.argmin(-1)]
        f[..., 3] = op * 255
        labs, m = pieces(op)
        sizes = [(labs == i).sum() for i in range(1, m + 1)]
        for i in range(1, m + 1):
            if sizes[i - 1] < 6:
                f[labs == i] = 0
        out.append((f, bx[0] / s, by[-1] / s))
    return out


def head_mask(design, head):
    """The design's head: its pixels from the crown down to the chin (as far under the head point as the crown is above
    it), within a head-wide band round the head point's column. `head` = the cells' head point, or None (the top rows'
    middle column, 7 rows down)."""
    ys, xs = np.nonzero(design[..., 3])
    top = ys.min()
    if head is None:
        hx = float(np.median(xs[ys < top + 8]))
        hy = top + 7
    else:
        hx, hy = head
    chin = int(round(2 * hy - top))
    half = int(round(hy - top)) + 2
    m = np.zeros(design.shape[:2], bool)
    m[top:chin + 1, max(0, int(hx) - half):int(hx) + half + 2] = True
    return m & (design[..., 3] > 0), top, chin


def paste_head(can, design, mask, top, chin, reach=4):
    """Our design's head pasted where it fits the frame best (colour matches within +-reach); the redrawn head's pixels
    in the rows above the chin's last 2 rows, within the head's columns +-1, are cleared first. Returns (dx, dy, match)."""
    ys, xs = np.nonzero(mask)
    best = None
    for dy in range(-reach, reach + 1):
        for dx in range(-reach, reach + 1):
            Y, X = ys + dy, xs + dx
            ok = (Y >= 0) & (Y < can.shape[0]) & (X >= 0) & (X < can.shape[1])
            same = (can[Y[ok], X[ok], 3] > 0) & (np.abs(can[Y[ok], X[ok], :3].astype(int)
                                                       - design[ys[ok], xs[ok], :3]).sum(-1) == 0)
            score = same.sum() - 0.5 * (can[Y[ok], X[ok], 3] == 0).sum()
            if best is None or score > best[0]:
                best = (score, dx, dy, same.mean())
    _, dx, dy, match = best
    for y in range(top, chin - 1):
        row = xs[ys == y]
        if len(row):
            can[y + dy, row.min() + dx - 1:row.max() + dx + 2] = 0
    can[ys + dy, xs + dx] = design[ys, xs]
    return dx, dy, round(float(match), 2)


def build(hero):
    spec = json.load(open(lp(os.path.join(SOURCE, hero, "codex_idle", "idle.json")), encoding="utf-8"))
    idle0, cells = our_idle(hero)
    cw, ch = cells["cell"]
    px, py = cells["tags"]["idle"][0]["pivot"]
    pal = np.array(spec["palette"])                       # the colours of the idle the pack was made from
    pal_lab = lab(pal)
    soles = py - spec["pivot"]["dy"]                       # our soles row in the cell
    keep = [k for k in range(spec["n"]) if k + 1 not in spec.get("drop", [])]
    design = np.asarray(Image.open(lp(os.path.join(SOURCE, hero, "codex_idle", "design.png"))).convert("RGBA"))
    mask, top, chin = head_mask(design, cells["tags"]["idle"][0].get("head"))
    frames = []
    for k, (f, left, bottom) in enumerate(read_cells(hero, spec, pal, pal_lab)):
        if k not in keep:
            continue
        X = int(round(left)) - spec["mid"] + px
        Y = int(round(bottom)) - (spec["feet"] + 1) + soles + 1 - f.shape[0]
        can = np.zeros((ch, cw, 4), np.uint8)
        ys, xs = np.nonzero(f[..., 3])
        if Y + ys.min() < 0 or X + xs.min() < 0 or Y + ys.max() >= ch or X + xs.max() >= cw:
            raise SystemExit(f"{hero} frame {k + 1} leaves its {cw}x{ch} cell")
        can[ys + Y, xs + X] = f[ys, xs]
        if spec.get("head", True):
            spec.setdefault("pasted", []).append(paste_head(can, design, mask, top, chin))
        pad = np.pad(can, ((2, 2), (2, 2), (0, 0)))
        pad, _, _ = G.complete_outline(pad, color=OUTLINE, feet=soles + 2)
        can = pad[2:-2, 2:-2].copy()
        can[soles + 1:] = 0
        for hole in pinholes(can[..., 3] > 0):
            for y, x in hole:
                can[y, x] = (*OUTLINE, 255)
        op = can[..., 3] > 0
        labs, n = pieces(op)
        for i in range(1, n + 1):                          # loose squares the head paste or the key left
            if (labs == i).sum() <= 3:
                can[labs == i] = 0
        frames.append(can)
    return frames, cells, (px, py), spec


def write(hero, frames, cells, pivot, spec):
    cw, ch = cells["cell"]
    cols, rows = layout(len(frames))
    strip = np.zeros((rows * ch, cols * cw, 4), np.uint8)
    for k, f in enumerate(frames):
        strip[(k // cols) * ch:(k // cols + 1) * ch, (k % cols) * cw:(k % cols + 1) * cw] = f
    Image.fromarray(strip).resize((strip.shape[1] * Z, strip.shape[0] * Z), Image.NEAREST).save(
        lp(os.path.join(NATIVE, f"{hero}_idle.png")))
    old = cells["tags"]["idle"][0]
    row = {k: v for k, v in old.items() if k not in ("ms",)}
    row["pivot"] = list(pivot)
    cells["tags"]["idle"] = [dict(row, ms=spec["ms"]) for _ in frames]
    path = lp(os.path.join(NATIVE, f"{hero}_cells.json"))
    raw = open(path, encoding="utf-8").read()
    if raw.startswith('{"cell"'):                         # the compact style: a line per tag
        top = {k: v for k, v in cells.items() if k != "tags"}
        text = json.dumps(top, ensure_ascii=False)[:-1] + ', "tags": {\n' + ",\n".join(
            f"  {json.dumps(t)}: {json.dumps(v, ensure_ascii=False)}" for t, v in cells["tags"].items()) + "\n}}\n"
    else:
        indent = next((len(l) - len(l.lstrip(" ")) for l in raw.splitlines()[1:] if l.startswith(" ")), 1)
        text = json.dumps(cells, ensure_ascii=False, indent=indent) + "\n"
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("hero", nargs="+")
    a = ap.parse_args()
    for hero in a.hero:
        frames, cells, pivot, spec = build(hero)
        write(hero, frames, cells, pivot, spec)
        hs = []
        for f in frames:
            ys = np.nonzero(f[..., 3].any(1))[0]
            hs.append(int(ys.max() - ys.min() + 1))
        print(f"{hero}: {len(frames)} frames x {spec['ms']} ms (mode {spec['mode']}), heights {hs}, "
              f"head pasted at (dx, dy, match) {spec.get('pasted')}")


if __name__ == "__main__":
    main()
