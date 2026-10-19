#!/usr/bin/env python3
"""Quinn's legs, round 2 (tools/art/pack_quinn_legs2.py): Codex's legs drawn along the skeletons, sampled back on the
pack's own grid, under the idle's own body and cape.

    python tools/art/design_quinn_legs2.py [--check DIR]   # writes assets/source/quinn/hd/legs2_<name>_only.png,
                                                          # legs2.json; --check: every cell at 8x with its skeleton

Codex (assets/source/quinn/codex_legs2/quinn-legs2, 2026-10-19, new-chat-4) returned the sheets resized (poses 1638 x
960 for 1386 x 812, the run 1891 x 831 for 1848 x 812) and redrew them on coarser squares of its own (about 9.25 and 7.8
px against 8.27 and 7.16), but it drew the legs where the skeleton lines lay on the page. Read on Codex's own squares the
legs would come back a tenth shorter than the skeletons (the idle's own lengths); so each cell is sampled on the pack's
grid stretched to the returned size (7 px x the sheet's scale), each square the commonest of its pixels snapped to the
idle's colours (the majority of a block of opaque pixels; under half opaque -> empty). The body is laid on the idle's
by the offset (within OFF squares) whose upper body matches best; the legs are the squares below the hip row where the
idle's body (with its cape's hem) has none. Ground closed in between the legs takes the outline's dark (gap-check).
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_quinn_legs2 as PK  # noqa: E402
import pixel_down as PD  # noqa: E402
from design_quinn_hd import lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "quinn", "codex_legs2", "quinn-legs2")
OUT = os.path.join(ROOT, "assets", "source", "quinn", "hd")
SHEETS = {"poses": (["crouch", "kneel", "lunge", "wide", "tuck", "step"], 3, (1386, 812)),
          "run": ([f"run{k}" for k in range(8)], 4, (1848, 812))}
OFF = 3
PADX = 12


def load(path):
    return np.asarray(Image.open(lp(path)).convert("RGBA")).copy()


def keyed(path):
    a = np.asarray(Image.open(lp(path)).convert("RGB")).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    green = (g > 150) & (g - r > 70) & (g - b > 70)
    line = (g > 60) & (g - r > 40) & (g - b > 40) & (r < 70) & (b < 70)
    out = np.zeros(a.shape[:2] + (4,), np.uint8)
    out[..., :3] = a
    out[..., 3] = np.where(green | line, 0, 255)
    return out


def sample(a, x0, y0, px, py, W, H, pal):
    """W x H squares from a, square (i, j) = pixels [x0 + i px, x0 + (i+1) px) x [y0 + j py, ...): the commonest of the
    opaque pixels snapped to pal; under half opaque -> empty."""
    out = np.zeros((H, W, 4), np.uint8)
    for j in range(H):
        ya, yb = int(round(y0 + j * py)), int(round(y0 + (j + 1) * py))
        for i in range(W):
            xa, xb = int(round(x0 + i * px)), int(round(x0 + (i + 1) * px))
            blk = a[ya:yb, xa:xb].reshape(-1, 4)
            if blk.size == 0:
                continue
            op = blk[:, 3] > 0
            if op.mean() < 0.5:
                continue
            c = blk[op, :3].astype(int)
            k = np.argmin(((c[:, None, :] - pal[None, :, :]) ** 2).sum(-1), axis=1)
            out[j, i, :3] = pal[np.bincount(k).argmax()]
            out[j, i, 3] = 255
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check")
    a = ap.parse_args()
    idle = load(os.path.join(OUT, "idle.png"))
    H, W = idle.shape[:2]
    pal = np.array(sorted({tuple(int(v) for v in c) for c in idle[idle[..., 3] > 0][:, :3]}), int)
    body = PK.body(idle)
    ink = (*PD.edge_colour(idle), 255)
    P = PK.poses()
    R = PK.run_frames()
    skel = {n: P[n] for n in P}
    skel.update({f"run{k}": R[k] for k in range(8)})
    meta, checks = {}, []
    ox, oy = PK.STAND[0] - PK.STAND_COL, PK.STAND[1] - PK.GROUND     # the idle's (0, 0) in a cell
    for sheet, (names, cols, (w0, h0)) in SHEETS.items():
        img = keyed(os.path.join(SRC, f"quinn-legs2-{sheet}.png"))
        sx, sy = img.shape[1] / w0, img.shape[0] / h0
        px, py = PK.PX * sx, PK.PX * sy
        for n, name in enumerate(names):
            drop = skel[name][0]
            dr = int(round(drop))
            cx0, cy0 = (n % cols) * PK.CW * px, (n // cols) * PK.CH * py
            cellsq = sample(img, cx0, cy0, px, py, PK.CW, PK.CH, pal)
            # the idle's body where the pack put it, and the offset laying Codex's body on it
            mine = np.zeros((PK.CH, PK.CW, 4), np.uint8)
            mine[oy + dr:oy + dr + H, ox:ox + W] = body[:PK.CH - oy - dr]
            upper = np.zeros((PK.CH, PK.CW), bool)
            upper[oy + dr:oy + dr + PK.HIP_ROW, ox:ox + W] = body[:PK.HIP_ROW, :, 3] > 0
            best = None
            for ddy in range(-OFF, OFF + 1):
                for ddx in range(-OFF, OFF + 1):
                    sh = np.roll(np.roll(cellsq, ddy, 0), ddx, 1)
                    both = upper & (sh[..., 3] > 0)
                    err = (upper != (sh[..., 3] > 0))[upper.any(1)].sum() * 20 + np.abs(
                        sh[..., :3].astype(int) - mine[..., :3].astype(int))[both].sum() / 60
                    if best is None or err < best[0]:
                        best = (err, ddy, ddx)
            _, ddy, ddx = best
            cellsq = np.roll(np.roll(cellsq, ddy, 0), ddx, 1)
            hip = oy + dr + PK.HIP_ROW
            legs = cellsq.copy()
            legs[:hip - 1] = 0
            legs[mine[..., 3] > 0] = 0
            full = legs.copy()
            m = mine[..., 3] > 0
            full[m] = mine[m]
            op = full[..., 3] > 0
            holes = ndimage.binary_fill_holes(op) & ~op
            holes[:hip - 2] = False
            full[holes] = ink
            legs[holes] = ink
            # in the idle's frame: rows from her top (before the drop), columns + PADX
            lay = np.zeros((H + 4, W + 2 * PADX, 4), np.uint8)
            sub = legs[oy:oy + H + 4, max(0, ox - PADX):ox + W + PADX]
            lay[:sub.shape[0], PADX - (ox - max(0, ox - PADX)):PADX - (ox - max(0, ox - PADX)) + sub.shape[1]] = sub
            Image.fromarray(lay).save(lp(os.path.join(OUT, f"legs2_{name}_only.png")))
            meta[name] = {"drop": dr, "padx": PADX, "offset": [int(ddy), int(ddx)], "holes": int(holes.sum())}
            print(name, "drop", dr, "offset", ddy, ddx, "holes closed", int(holes.sum()))
            checks.append((name, full, skel[name], dr, (ox, oy)))
    with open(lp(os.path.join(OUT, "legs2.json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump(meta, f, indent=1)
    if a.check:
        os.makedirs(a.check, exist_ok=True)
        z = 8
        tiles = []
        for name, full, sk, dr, (ox, oy) in checks:
            t = full[18:, 6:46]
            im = Image.new("RGBA", (t.shape[1] * z, t.shape[0] * z), (200, 200, 200, 255))
            im.alpha_composite(Image.fromarray(np.repeat(np.repeat(t, z, 0), z, 1)))
            d = ImageDraw.Draw(im)
            for pts, c in ((sk[2], PK.BLUE), (sk[1], PK.RED)):
                q = [((x + ox - 6 + 0.5) * z, (y + oy - 18 + 0.5) * z) for x, y in pts]
                d.line(q, fill=c + (160,), width=2)
                for x, y in q[:3]:
                    d.ellipse([x - 4, y - 4, x + 4, y + 4], outline=c + (255,))
            d.text((4, 4), name, fill=(0, 0, 0, 255))
            tiles.append(im)
        for g, part in (("poses", tiles[:6]), ("run", tiles[6:])):
            Wt = sum(t.width + 10 for t in part)
            sheet = Image.new("RGB", (Wt, max(t.height for t in part)), (255, 255, 255))
            x = 0
            for t in part:
                sheet.paste(t.convert("RGB"), (x, 0))
                x += t.width + 10
            sheet.save(os.path.join(a.check, f"legs2_check_{g}.png"))


if __name__ == "__main__":
    main()
