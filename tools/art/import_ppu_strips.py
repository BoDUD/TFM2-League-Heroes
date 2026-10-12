#!/usr/bin/env python3
"""A Codex delivery of dense (PPU) action strips -> assets/source/ppu/<hero>_<tag>.png, the drawn strips ppu_hd.py uses.

The user, 2026-10-12: 「接下来使用PPU修复吸血鬼和卡尔玛和艾希 做到所有动作帧一致 待机一致」. tools/art/pack_ppu_strips.py
made the pack (every 1x frame scaled by PPU as a skeleton in a cell, cells.json); Codex drew the design over every cell
at the pack's square size. This reads every image back square for square (each block's most common colour, clear
included), maps the colours to the design's, and puts each cell into its frame by the pivot: the frame is
round(PPU x the 1x frame) and its centre is the pivot, as in the game. A cell that starts above the frame
(frame_top < 0: room for the design's head) grows the frame by as much at the top and the bottom, so the pivot stays
its centre; the grown sizes go to <hero>_<tag>.json next to the strip. The idle is the design itself, still in every
frame (「待机一致」; an importer's breathing deforms the body: memory rig-deformation-checks), standing where the 1x idle
stands (its soles on the 1x soles, across where it overlaps the scaled 1x idle most).

    python tools/art/import_ppu_strips.py --hero vladimir --delivery <outputs>/vladimir-ppu-strips
    python tools/art/import_ppu_strips.py --hero yasuo --delivery <...> --scale 2     # pack PPU 1.5 -> game PPU 3

Then: python tools/art/ppu_hd.py --hero <hero> (the hd_ tags into the sheet) and the hero in
addons/league_main/src/hd.rs.
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
import ppu_hd as P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "ppu")
PACKS = os.path.join(ROOT, "dist", "ppu_packs")


def squares(path, px):
    """The image read back one pixel per drawn px x px square: each block's most common colour (clear counts)."""
    a = np.asarray(Image.open(path).convert("RGBA"))
    H, W = a.shape[0] // px, a.shape[1] // px
    b = a[:H * px, :W * px].reshape(H, px, W, px, 4).transpose(0, 2, 1, 3, 4).reshape(H, W, px * px, 4).copy()
    b[b[..., 3] < 128] = 0
    b[..., 3] = np.where(b[..., 3] > 0, 255, 0)
    out = np.zeros((H, W, 4), np.uint8)
    mixed = 0
    keys = b.astype(np.uint32)
    keys = (keys[..., 0] << 24) | (keys[..., 1] << 16) | (keys[..., 2] << 8) | keys[..., 3]
    for y in range(H):
        for x in range(W):
            v, n = np.unique(keys[y, x], return_counts=True)
            if len(v) > 1:
                mixed += 1
            k = int(v[n.argmax()])
            out[y, x] = ((k >> 24) & 255, (k >> 16) & 255, (k >> 8) & 255, k & 255)
    return out, mixed


def to_palette(a, pal):
    """Every opaque pixel to its nearest design colour. -> (image, pixels changed)."""
    op = a[..., 3] > 0
    rgb = a[op][:, :3].astype(int)
    d = ((rgb[:, None, :] - pal[None, :, :]) ** 2).sum(axis=2)
    near = pal[d.argmin(axis=1)]
    out = a.copy()
    out[op, :3] = near
    return out, int((near != rgb).any(axis=1).sum())


def place_idle(design, idle1, k):
    """The design in a frame of round(k x the 1x idle): soles on the 1x soles, across at the most overlap."""
    H, W = round(idle1.shape[0] * k), round(idle1.shape[1] * k)
    sk = P.scale_any(idle1, k)[..., 3] > 0
    sole = np.nonzero(sk.any(axis=1))[0].max()
    dh, dw = design.shape[:2]
    y0 = sole - dh + 1
    if dw > W:
        sys.exit(f"the design ({dw}x{dh}) is wider than the idle frame {W}x{H}")
    if y0 < 0:
        # taller than the frame (karma's jade ring over her head): the frame grown alike at the top and the bottom
        g = -y0
        H, y0 = H + 2 * g, 0
        sk = np.pad(sk, ((g, g), (0, 0)))
    dm = design[..., 3] > 0
    best = max(range(0, W - dw + 1), key=lambda x0: int((sk[y0:y0 + dh, x0:x0 + dw] & dm).sum()))
    out = np.zeros((H, W, 4), np.uint8)
    out[y0:y0 + dh, best:best + dw] = design
    return out, (best, y0)


def write_strip(hero, tag, frames, want):
    """frames left to right, 1 px apart, top-aligned; <hero>_<tag>.json lists the sizes when any is not `want`."""
    h = max(f.shape[0] for f in frames)
    w = sum(f.shape[1] for f in frames) + len(frames) - 1
    s = np.zeros((h, w, 4), np.uint8)
    x = 0
    for f in frames:
        s[:f.shape[0], x:x + f.shape[1]] = f
        x += f.shape[1] + 1
    Image.fromarray(s).save(os.path.join(SRC, f"{hero}_{tag}.png"))
    side = os.path.join(SRC, f"{hero}_{tag}.json")
    sizes = [[int(f.shape[1]), int(f.shape[0])] for f in frames]
    if sizes != [list(v) for v in want]:
        with open(side, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"sizes": sizes}, fh)
    elif os.path.isfile(side):
        os.remove(side)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hero", required=True)
    ap.add_argument("--delivery", required=True, help="Codex's folder: cells.json and the <hero>_<tag>_<n>.png images")
    ap.add_argument("--design", help="the design, 1 px per square (default: the pack's design/<hero>_design_1x.png)")
    ap.add_argument("--scale", type=int, default=1, help="game pixels per drawn square (yasuo: 2)")
    ap.add_argument("--head-rows", type=int, default=0,
                    help="the design's top rows Codex pasted whole into the frames (vladimir: 35, head and collar): "
                         "where a frame holds them pixel for pixel, the outline of the head Codex drew first and "
                         "pasted over is cleared - parts next to the block in its rows that never reach more than 4 "
                         "pixels from it (「吸血鬼走路有残影？没清理干净吧」); an arm or a claw reaches far")
    ap.add_argument("--design-run", action="store_true",
                    help="the run is the design itself, its legs stepping (RUN_LEGS; Codex's run bodies changed width "
                         "and arm length frame to frame: 「吸血鬼走路时模型变形」)")
    ap.add_argument("--same", action="append", default=[], metavar="TAG:I=J",
                    help="frame I of TAG is frame J's drawing, its lowest row on frame I's skeleton's lowest row (a "
                         "drawing that does not match its neighbours; vladimir dead:5=4 dead:6=4 dead:7=4 - Codex drew "
                         "the last three lying frames apart, a different crumpled body from frames 3-4)")
    a = ap.parse_args()
    hero, s = a.hero, a.scale
    with open(os.path.join(a.delivery, "cells.json"), encoding="utf-8") as f:
        cells = json.load(f)
    px, k = cells["px_per_square"], cells["ppu"] * s
    if hero not in P.PPU or abs(P.PPU[hero] - k) > 1e-3:
        sys.exit(f"{hero}: PPU in tools/art/ppu_hd.py must be {k:g} (the pack's {cells['ppu']:g} x --scale {s})")
    dpath = a.design or os.path.join(PACKS, hero, "design", f"{hero}_design_1x.png")
    design = np.asarray(Image.open(dpath).convert("RGBA")).copy()
    design[..., 3] = np.where(design[..., 3] > 0, 255, 0)
    pal = np.unique(design[design[..., 3] > 0][:, :3], axis=0).astype(int)
    sheet = P.read_sheet(os.path.join(ROOT, "league", "champions", f"league_{hero}"))
    got = {}
    for im in cells["images"]:
        p = os.path.join(a.delivery, im["file"])
        if not os.path.isfile(p):
            sys.exit(f"missing {p}")
        sq, mixed = squares(p, px)
        sq, recoloured = to_palette(sq, pal)
        if tuple(sq.shape[1::-1]) != tuple(im["squares"]):
            sys.exit(f"{im['file']}: {sq.shape[1]}x{sq.shape[0]} squares, the pack's {im['squares']}")
        inside = np.zeros(sq.shape[:2], bool)
        for m in im["cells"]:
            x, y, w, h = m["rect"]
            inside[y:y + h, x:x + w] = True
        lost = int((sq[..., 3] > 0)[~inside].sum())
        print(f"{im['file']}: {mixed} mixed squares, {recoloured} recoloured, {lost} drawn outside the cells (dropped)")
        for m in im["cells"]:
            x, y, w, h = m["rect"]
            cell = up(sq[y:y + h, x:x + w], s)
            fw, fh = m["frame_size"]
            one = sheet[m["tag"]][m["frame"]][0]
            FW, FH = round(one.shape[1] * k), round(one.shape[0] * k)
            g = max(0, -m["frame_top"] * s)
            FH += 2 * g
            # the cell's origin so that its pivot (fw/2, fh/2 - top in squares) is the frame's centre
            ox = round(FW / 2 - fw * s / 2)
            oy = round(FH / 2 - (fh / 2 - m["frame_top"]) * s)
            fr = np.zeros((FH, FW, 4), np.uint8)
            cy0, cx0 = max(0, -oy), max(0, -ox)
            cy1, cx1 = min(cell.shape[0], FH - oy), min(cell.shape[1], FW - ox)
            cut = int((cell[..., 3] > 0).sum()) - int((cell[cy0:cy1, cx0:cx1, 3] > 0).sum())
            if cut:
                print(f"  {m['tag']}[{m['frame']}]: {cut} pixels past the frame (dropped)")
            fr[oy + cy0:oy + cy1, ox + cx0:ox + cx1] = cell[cy0:cy1, cx0:cx1]
            specks = drop_specks(fr)
            if specks:
                print(f"  {m['tag']}[{m['frame']}]: specks of {specks} pixels apart from the figure (dropped)")
            got.setdefault(m["tag"], {})[m["frame"]] = fr
    for spec in a.same:
        tag, ij = spec.split(":")
        i, j = (int(v) for v in ij.split("="))
        got[tag][i] = same_as(got[tag][j], got[tag][i].shape[:2], sheet[tag][i][0], k)
        print(f"{tag}[{i}]: frame {j}'s drawing, on its own skeleton's lowest row")
    design_s = up(design, s)
    if a.head_rows:
        for tag in got:
            for i in got[tag]:
                n = clear_head_ghost(got[tag][i], design_s, a.head_rows * s)
                if n:
                    print(f"{tag}[{i}]: {n} pixels of the old head's outline round the pasted head (cleared)")
    idle = sheet["idle"]
    if a.design_run:
        run = design_run(design_s, RUN_LEGS[hero], len(sheet["run"]), s)
        base, (x0, y0) = place_idle(design_s, idle[0][0], k)
        for i, f in enumerate(run):
            H, W = got["run"][i].shape[:2]
            # the idle's place against the frame's centre: the same in the run (no sway); the frame grown alike at
            # both sides when the design is wider than it
            reach = max(base.shape[1] / 2 - x0, x0 + f.shape[1] - base.shape[1] / 2)
            while W < 2 * reach:
                W += 2
            cx = x0 - base.shape[1] / 2 + W / 2
            cy = y0 - base.shape[0] / 2 + H / 2
            out = np.zeros((H, W, 4), np.uint8)
            fy, fx = round(cy), round(cx)
            out[fy:fy + f.shape[0], fx:fx + f.shape[1]] = f
            got["run"][i] = out
        print(f"run: the design with its legs stepping, {len(run)} frames")
    fr, at = place_idle(design_s, idle[0][0], k)
    got["idle"] = {i: fr for i in range(len(idle))}
    print(f"idle: the design ({design_s.shape[1]}x{design_s.shape[0]}) at {at} in every one of {len(idle)} frames")
    os.makedirs(SRC, exist_ok=True)
    for tag, frames in sheet.items():
        if tag.startswith(P.PREFIX):
            continue
        have = got.get(tag, {})
        if sorted(have) != list(range(len(frames))):
            sys.exit(f"{tag}: frames {sorted(have)} delivered, {len(frames)} in the sheet")
        want = [(round(f.shape[1] * k), round(f.shape[0] * k)) for f, _ in frames]
        write_strip(hero, tag, [have[i] for i in range(len(frames))], want)
        print(f"assets/source/ppu/{hero}_{tag}.png: {len(frames)} frames")


def clear_head_ghost(fr, design, rows, far=4, allow=5):
    """Where `fr` holds the design's top `rows` (its opaque pixels) exactly: clear the other parts in those rows
    that keep within `far` pixels of the block (at most `allow` pixels beyond). -> pixels cleared."""
    from scipy import ndimage
    ys, xs = np.nonzero(design[..., 3] > 0)
    t = design[ys.min():ys.min() + rows]
    ty, tx = np.nonzero(t[..., 3] > 0)
    want = t[ty, tx].astype(int)
    H, W = fr.shape[:2]
    at = None
    for dy in range(-ty.min(), H - ty.max()):
        for dx in range(-tx.min(), W - tx.max()):
            if (fr[ty + dy, tx + dx].astype(int) == want).all():
                at = (dx, dy)
                break
        if at:
            break
    if at is None:
        return 0
    dx, dy = at
    M = np.zeros((H, W), bool)
    M[ty + dy, tx + dx] = True
    band = np.zeros((H, W), bool)
    band[max(0, dy):dy + rows] = True
    rest = (fr[..., 3] > 0) & ~M & band
    lab, n = ndimage.label(rest, structure=np.ones((3, 3)))
    dist = ndimage.distance_transform_edt(~M)
    gone = np.zeros((H, W), bool)
    for v in range(1, n + 1):
        z = lab == v
        if int((dist[z] > far).sum()) <= allow:
            gone |= z
    fr[gone] = 0
    return int(gone.sum())


# The run legs drawn from the design (--design-run): per leg the design's own pixels, row -> (first, last column) -
# the shin (swung about the knee row: each row moved in proportion) and the boot (from `boot` down, moved whole);
# `dx` = the foot's range forward and back (the near foot never reaches the far one: 「那走路时候脚也变形了啊」),
# `phase` = where in the cycle it starts. `lining` = the coat's inside colour left behind the shins inside the coat.
RUN_LEGS = {
    "vladimir": {
        "knee": 69, "boot": 75, "lift": 2, "inside_to": 72, "lining": (0x42, 0x00, 0x12),
        "legs": [
            {"name": "far", "phase": 0.5, "dx": (-1, 3),
             "rows": {70: (27, 31), 71: (27, 31), 72: (28, 32), 73: (29, 31), 74: (29, 31), 75: (28, 32),
                      76: (28, 33), 77: (27, 34), 78: (27, 37), 79: (27, 38), 80: (27, 39), 81: (27, 39)}},
            {"name": "near", "phase": 0.0, "dx": (-3, 1),
             "rows": {70: (17, 22), 71: (18, 22), 72: (18, 22), 73: (18, 21), 74: (18, 21), 75: (17, 21),
                      76: (17, 21), 77: (16, 22), 78: (16, 22), 79: (15, 23), 80: (15, 23), 81: (15, 23)}},
        ],
    },
}


def design_run(design, spec, n, s=1):
    """`n` run frames of the design: the body as it is (no part of it moves), the legs of `spec` (RUN_LEGS) stepping
    half a cycle apart. A foot slides back on the ground (dx from its front to its back end) and swings forward in
    the air (lifted up to `lift`); its shin leans from the knee to it, rows moved in proportion, and shortens as the
    foot lifts (rows dropped, its top and its bottom kept) - the boot is never drawn over the shin, never cut, never
    sheared. Far leg first, near leg over it; where a shin was inside the coat the coat's lining shows."""
    H, W = design.shape[:2]
    knee, boot, lift = spec["knee"] * s, spec["boot"] * s, spec["lift"] * s
    body = design.copy()
    masks = []
    for leg in spec["legs"]:
        m = np.zeros((H, W), bool)
        for r, (c0, c1) in leg["rows"].items():
            for k in range(s):
                m[r * s + k, c0 * s:(c1 + 1) * s] = True
        m &= design[..., 3] > 0
        masks.append(m)
        inside = m.copy()
        inside[(spec["inside_to"] + 1) * s:] = False
        body[m] = 0
        body[inside] = spec["lining"] + (255,)
    from scipy import ndimage
    op0 = design[..., 3] > 0
    holes0 = ndimage.binary_fill_holes(op0) & ~op0
    frames = []
    for i in range(n):
        out = body.copy()
        for leg, m in zip(spec["legs"], masks):
            a = 2 * np.pi * (i / n + leg["phase"])
            lo, hi = leg["dx"]
            dx = ((lo + hi) / 2 + (hi - lo) / 2 * np.cos(a)) * s
            up_ = lift * max(0.0, -np.sin(a))
            lay = np.zeros_like(design)
            for y in range(H):
                xs = np.nonzero(m[y])[0]
                if not len(xs):
                    continue
                t = min(1.0, max(0.0, (y - knee + 1) / (boot - knee + 1)))
                ny = y - int(np.floor(up_ * t + 0.5))
                sh = int(np.floor(dx * t + 0.5))
                ok = (xs + sh >= 0) & (xs + sh < W)
                if 0 <= ny < H:
                    lay[ny, xs[ok] + sh] = design[y, xs[ok]]
            out[lay[..., 3] > 0] = lay[lay[..., 3] > 0]
        # ground shut in between a moved boot or shin and the coat that the design does not have (a crack, memory
        # gap-check) takes the lining's shade
        from scipy import ndimage
        o = out[..., 3] > 0
        pockets, n_ = ndimage.label(ndimage.binary_fill_holes(o) & ~o & ~holes0)
        for v in range(1, n_ + 1):
            z = pockets == v
            if z.sum() <= 8 * s * s:
                out[z] = spec["lining"] + (255,)
        frames.append(out)
    return frames


def same_as(src, shape, one, k):
    """`src` (a frame) in a frame of `shape`, centred across, its lowest opaque row on the lowest row of the 1x
    frame `one` scaled by k (the frame grown alike at both ends: the 1x frame centred in it)."""
    H, W = shape
    sk = P.scale_any(one, k)
    want = np.nonzero(sk[..., 3].any(axis=1))[0].max() + (H - sk.shape[0]) // 2
    have = np.nonzero(src[..., 3].any(axis=1))[0]
    dy, dx = want - have.max(), (W - src.shape[1]) // 2
    out = np.zeros((H, W, 4), np.uint8)
    ys, xs = np.nonzero(src[..., 3] > 0)
    ok = (ys + dy >= 0) & (ys + dy < H) & (xs + dx >= 0) & (xs + dx < W)
    if not ok.all():
        sys.exit(f"the drawing does not fit the frame {W}x{H}")
    out[ys + dy, xs + dx] = src[ys, xs]
    return out


def drop_specks(fr, below=4):
    """Clear the parts of fewer than `below` pixels (8-connected) - a dot left floating by the image model
    (「别留多余的像素」). -> their sizes."""
    from scipy import ndimage
    op = fr[..., 3] > 0
    lab, n = ndimage.label(op, structure=np.ones((3, 3)))
    sizes = ndimage.sum(op, lab, range(1, n + 1))
    small = [v + 1 for v, z in enumerate(sizes) if z < below]
    fr[np.isin(lab, small)] = 0
    return [int(sizes[v - 1]) for v in small]


def up(a, s):
    return a if s == 1 else np.repeat(np.repeat(a, s, axis=0), s, axis=1)


if __name__ == "__main__":
    main()
