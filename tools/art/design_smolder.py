"""league_smolder's 3/4 front design at PPU 1.5 (the user's pick) from Codex's step-1 take 3.

    python tools/art/design_smolder.py [--review dist/smolder_packs/review]

Codex drew take 3 (assets/source/smolder/codex_model/raw/smolder-front-attempt-03.png) on ~12-px squares, not the
16-px grid asked: horn tips to soles 75 of its squares, 1:1 that is PPU 2.3 at 32 game rows. The user kept PPU 1.5
(「PPU 1.5」 after a density sheet where the 1.5 cut's face was mush), so the figure comes down to 48 rows:
  1. read 1:1 on its own grid (regrid.py), hard alpha at 128, its own 32 k-means colours, one majority pass (own());
  2. brought to 48 rows horn tips -> soles by AREA VOTES, not means (a mean mixes neighbours into muddy new colours):
     each new square takes the commonest drawn colour it covers, the near-black one where dark covers 40 % or more,
     clear where half or more is clear; the grid sits on the soles and the figure's middle column;
  3. the face redrawn by hand (FACE: the near eye 7 x 5 with rim, white, teal iris, pupil and a highlight; the far
     eye 5 x 4 by the head's edge; the grin one dark line with its corners up and two teeth under it), letters from
     the design's own colours;
  4. the outline closed (strips.complete_outline, the soles kept on their row).
Writes assets/source/smolder/hd/front.png (+ palette.json letter table) and, with --review, x8 / game-size pictures.
"""
import argparse
import json
import os
import string
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import pixel_down as P  # noqa: E402
import strips  # noqa: E402
from design_smolder_cut import kmeans_palette  # noqa: E402

SRC = os.path.join(REPO, "assets", "source", "smolder")
TAKE = os.path.join(SRC, "codex_model", "raw", "smolder-front-attempt-03.png")
ROWS = 48                    # horn tips -> soles (32 game rows at PPU 1.5)
PPU = 1.5
L = string.ascii_letters + string.digits
# hand edits after the vote: (row, first column, letters of the vote's own colour table)
FACE = [
    (13, 44, "zgggggu"),      # near eye: rim
    (14, 44, "gvvjcvgu"),     #   white, teal iris, pupil, highlight
    (15, 44, "gvvjccgu"),
    (16, 44, "ugvjjigu"),
    (17, 44, "uugggguA"),     #   lower rim
    (12, 56, "ugggu"),        # far eye by the head's edge
    (13, 56, "gvjcu"),
    (14, 56, "gvjcu"),
    (15, 56, "ugiju"),
    (18, 50, "gAAAAAAAAg"),   # the grin's corners
    (19, 51, "gggggggg"),     #   its line
    (20, 51, "zzvppvAA"),     #   two teeth, the open mouth between
]


def own():
    """Take 3 read 1:1 on its own grid: hard alpha, its own 32 colours, one majority pass."""
    with tempfile.TemporaryDirectory() as tmp:
        dst = os.path.join(tmp, "own.png")
        subprocess.run([sys.executable, os.path.join(REPO, ".claude", "skills", "tfm2-hero-mod", "scripts",
                                                     "regrid.py"), TAKE, dst], check=True, capture_output=True)
        a = np.array(Image.open(dst).convert("RGBA"))
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    pal = kmeans_palette(a)
    op = a[..., 3] > 0
    px = a[op][:, :3].astype(float)
    a[op, :3] = pal[((px[:, None] - pal[None]) ** 2).sum(-1).argmin(1)].round().astype(np.uint8)
    return P.crisp([a], n=28, passes=1, contrast=1.0, lines=False)[0]


def vote(a, rows):
    """`a` brought to `rows` squares from the horn tips (the first teal row) to the soles by area votes."""
    H, W = a.shape[:2]
    op = a[..., 3] > 0
    r, g, b = (a[..., i].astype(int) for i in range(3))
    sole = np.nonzero(op.any(1))[0][-1] + 1
    horn = np.nonzero((op & (g > r + 20) & (b > r)).any(1))[0][0]
    c = (sole - horn) / rows
    cols, inv = np.unique(a.reshape(-1, 4), axis=0, return_inverse=True)
    inv = inv.reshape(H, W)
    dark = cols[:, :3].astype(int).sum(1) < 120
    clear = cols[:, 3] == 0
    xs = np.nonzero(op.any(0))[0]
    Hn, Wn = int(np.ceil(sole / c)), int(np.ceil(W / c)) + 2
    ox, oy = (xs[0] + xs[-1] + 1) / 2 - Wn / 2 * c, sole - Hn * c
    out = np.zeros((Hn, Wn, 4), np.uint8)
    for j in range(Hn):
        for i in range(Wn):
            x0, x1, y0, y1 = ox + i * c, ox + (i + 1) * c, oy + j * c, oy + (j + 1) * c
            w = np.zeros(len(cols))
            for yy in range(max(0, int(np.floor(y0))), min(H, int(np.ceil(y1)))):
                fy = min(y1, yy + 1) - max(y0, yy)
                for xx in range(max(0, int(np.floor(x0))), min(W, int(np.ceil(x1)))):
                    fx = min(x1, xx + 1) - max(x0, xx)
                    if fx > 0 and fy > 0:
                        w[inv[yy, xx]] += fx * fy
            wc = w[clear].sum()
            if w.sum() == 0 or wc >= 0.5 * c * c:
                continue
            pick = dark if w[dark].sum() >= 0.4 * (w.sum() - wc) else ~dark & ~clear
            out[j, i] = cols[np.where(pick, w, 0).argmax()]
    ys, xs = np.nonzero(out[..., 3])
    return out[ys.min():, xs.min():xs.max() + 1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    args = ap.parse_args()
    v = vote(own(), ROWS)
    cols = np.unique(v.reshape(-1, 4), axis=0)
    lut = {L[i]: c for i, c in enumerate(cols) if c[3]}
    for r, c0, s in FACE:
        for i, ch in enumerate(s):
            v[r, c0 + i] = lut[ch]
    v = np.pad(v, ((2, 0), (2, 2), (0, 0)))
    v, added, _ = strips.complete_outline(v, feet=np.nonzero(v[..., 3].any(1))[0][-1])
    os.makedirs(os.path.join(SRC, "hd"), exist_ok=True)
    Image.fromarray(v).save(os.path.join(SRC, "hd", "front.png"))
    json.dump({k: [int(x) for x in c] for k, c in lut.items()}, open(os.path.join(SRC, "hd", "palette.json"), "w"),
              indent=0)
    n = len(np.unique(v[v[..., 3] > 0][:, :3], axis=0))
    print(f"hd/front.png {v.shape[1]}x{v.shape[0]}, {n} colours, outline +{added}, game "
          f"{v.shape[1] / PPU:.0f}x{v.shape[0] / PPU:.0f}")
    if args.review:
        os.makedirs(args.review, exist_ok=True)
        Image.fromarray(v).resize((v.shape[1] * 8, v.shape[0] * 8), Image.NEAREST).save(
            os.path.join(args.review, "smolder_front_x8.png"))


if __name__ == "__main__":
    main()
