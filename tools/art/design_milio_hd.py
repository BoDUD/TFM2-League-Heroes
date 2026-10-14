"""Milio's design (step 1, the user's picks 2026-10-15): the front and the side-on view, read back from Codex's raws.

    python tools/art/design_milio_hd.py [--check out.png]

Codex's step-1 delivery (assets/source/milio/codex_model) shipped its own 12-px snap of each take - muddy again (the eyes
yellow blobs, the spirit's face gone) - so the raws are read here: raw/front.png on its own grid (regrid, ~11 px a
square: the boy 95 squares hair top to soles), raw/side-B.png (the user's pick, ~7 px a square) brought to the
same 95 rows with pixel_down.pixelate. One palette (k-means PAL_N on the front; pixel_down.palette_of on Codex's raw
is all dark), snapped everywhere. The frames stay at this density through steps 2-3 (crisp); ppu_restyle brings them to
2.2 squares a game pixel at the end (the user's density, 32 game rows), the Kindred way.
One face (memory one-face-all-frames): the side view gets the front's head - hair, face and neck above HEAD_CUT,
nothing of the shoulders - placed where it matches the side's own head best (masked colour distance over shifts),
the side's own head cleared under it first.
Writes assets/source/milio/hd/front.png (boy + spirit), front_boy.png, front_spirit.png (the same canvas each),
side.png (the boy only) and design.json (canvas, standing columns, soles row).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.cluster.vq import kmeans2

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import pixel_down as PD  # noqa: E402
import regrid as RG  # noqa: E402
import strips  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "milio")
RAW = os.path.join(SRC, "codex_model", "raw")
PAL_N = 40
HEAD_CUT = 37          # rows of the front boy (from his hair top) that make the head: hair, face, chin, neck top
SPECK = 2000           # raw px: smaller pieces are haze specks


def hard(path):
    a = np.array(Image.open(path).convert("RGBA"))
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    lab, n = ndimage.label(a[..., 3] > 0)
    s = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    a[~np.isin(lab, [i + 1 for i in range(n) if s[i] >= SPECK])] = 0
    return a


def kpal(a, n):
    px = a[a[..., 3] > 0][:, :3].astype(float)
    sub = px[np.random.default_rng(0).choice(len(px), min(60000, len(px)), replace=False)]
    return kmeans2(sub, n, seed=1, minit="++")[0]


def snap(a, pal):
    out = a.copy()
    m = a[..., 3] > 0
    d = ((a[m][:, None, :3].astype(float) - pal[None]) ** 2).sum(-1)
    out[m, :3] = np.clip(pal[d.argmin(1)].round(), 0, 255).astype(np.uint8)
    return out


def pieces(a):
    lab, n = ndimage.label(a[..., 3] > 0)
    s = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    order = list(np.argsort(-s) + 1)
    return lab, order


def boy_box(boy):
    ys, xs = np.nonzero(boy)
    y1 = ys.max()
    feet = np.nonzero(boy[y1 - 6:y1 + 1].any(0))[0]
    return ys.min(), y1, (feet.min() + feet.max()) / 2


def head_mask(f, top):
    """The front head: every opaque square above top + HEAD_CUT that hangs together with the hair (the shoulders and
    fists below the cut never)."""
    op = f[..., 3] > 0
    m = op.copy()
    m[top + HEAD_CUT:] = False
    lab, n = ndimage.label(m)
    hair = lab[top + 2][lab[top + 2] > 0]
    keep = np.isin(lab, np.unique(hair)) if len(hair) else m
    return keep


def paste_head(side, front, hm):
    """Shift the front head over the side's own head where the colours match best; clear the side's head first."""
    ys, xs = np.nonzero(hm)
    hy0, hx0 = ys.min(), xs.min()
    head = front[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    hmask = hm[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    sop = side[..., 3] > 0
    sy = np.nonzero(sop.any(1))[0].min()
    sx = np.nonzero(sop[sy:sy + hmask.shape[0]].any(0))[0]
    best = None
    H, W = side.shape[:2]
    for dy in range(-3, 6):
        for dx in range(sx.min() - 8, sx.max() - hmask.shape[1] + 9):
            y, x = sy + dy, dx
            if y < 0 or x < 0 or y + hmask.shape[0] > H or x + hmask.shape[1] > W:
                continue
            win = side[y:y + hmask.shape[0], x:x + hmask.shape[1]]
            both = hmask & (win[..., 3] > 0)
            miss = (hmask & (win[..., 3] == 0)).sum() + ((~hmask) & (win[..., 3] > 0)).sum() * 0.5
            dist = ((win[both][:, :3].astype(float) - head[both][:, :3]) ** 2).sum(-1).mean() if both.any() else 1e9
            score = dist + 400 * miss / max(1, hmask.sum()) * 100
            if best is None or score < best[0]:
                best = (score, y, x)
    _, y, x = best
    out = side.copy()
    # clear the side's own head above the front head's chin line (rows the head covers), within its columns +- 2
    hh, hw = hmask.shape
    region = np.zeros(sop.shape, bool)
    region[:y + hh - 3, max(0, x - 3):x + hw + 3] = True
    lab, n = ndimage.label(sop & region)
    top_ids = np.unique(lab[:y + 4][lab[:y + 4] > 0])
    out[np.isin(lab, top_ids) & region] = 0
    tgt = out[y:y + hh, x:x + hw]
    tgt[hmask] = head[hmask]
    return out, (y, x)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", help="write a review picture (front | side at 6x) here")
    a = ap.parse_args()
    front, size, _ = RG.regrid(hard(os.path.join(RAW, "front.png")))
    pal = kpal(front, PAL_N)
    front = snap(front, pal)
    lab, order = pieces(front)
    boy = lab == order[0]
    spirit = np.isin(lab, order[1:]) & (front[..., 3] > 0)
    top, sole, mid = boy_box(boy)
    rows = sole - top + 1
    print("front: squares ~%.1f px, boy rows %d (hair top %d, soles %d), standing col %.1f, spirit %d squares"
          % (size, rows, top, sole, mid, spirit.sum()))
    # the side, brought to the front boy's rows
    sraw = hard(os.path.join(RAW, "side-B.png"))
    lab_s, order_s = pieces(sraw)
    sb = lab_s == order_s[0]
    st, ss, smid = boy_box(sb)
    k = rows / (ss - st + 1)
    side, _ = PD.pixelate(sraw, k, (int(round(smid)), int(ss + 1)), PD.edge_colour(sraw), pal)
    side = snap(side, pal)
    hm = head_mask(front, top) & boy
    fb = front.copy()
    fb[~boy] = 0
    side, at = paste_head(side, fb, hm)
    outline = PD.edge_colour(front)
    side, added, _ = strips.complete_outline(side, color=outline)
    sy = np.nonzero(side[..., 3].any(1))[0]
    sfeet = np.nonzero(side[sy.max() - 6:sy.max() + 1, :, 3].any(0))[0]
    print("side: %dx%d, rows %d, head pasted at %s, outline +%d" % (side.shape[1], side.shape[0], sy.max() - sy.min() + 1,
                                                                  at, added))
    os.makedirs(os.path.join(SRC, "hd"), exist_ok=True)
    fb_only = front.copy()
    fb_only[~boy] = 0
    sp_only = front.copy()
    sp_only[~spirit] = 0
    Image.fromarray(front).save(os.path.join(SRC, "hd", "front.png"))
    Image.fromarray(fb_only).save(os.path.join(SRC, "hd", "front_boy.png"))
    Image.fromarray(sp_only).save(os.path.join(SRC, "hd", "front_spirit.png"))
    sc = np.nonzero(side[..., 3].any(0))[0]
    side = side[sy.min():sy.max() + 1, sc.min():sc.max() + 1]
    Image.fromarray(side).save(os.path.join(SRC, "hd", "side.png"))
    info = {"front": {"size": [int(front.shape[1]), int(front.shape[0])], "hair_top": int(top), "soles": int(sole),
                      "standing_col": float(mid)},
            "side": {"size": [int(side.shape[1]), int(side.shape[0])], "hair_top": 0, "soles": int(side.shape[0] - 1),
                     "standing_col": float((sfeet.min() + sfeet.max()) / 2 - sc.min())},
            "rows": int(rows), "game_rows": 32, "final_ppu": 2.2, "palette": [[int(v) for v in c] for c in pal.round()]}
    json.dump(info, open(os.path.join(SRC, "hd", "design.json"), "w"), indent=1)
    if a.check:
        z = 6
        ims = [Image.fromarray(front), Image.fromarray(side)]
        W = sum(i.width for i in ims) * z + 60
        H = max(i.height for i in ims) * z + 20
        can = Image.new("RGBA", (W, H), (205, 200, 185, 255))
        x = 20
        for i in ims:
            can.alpha_composite(i.resize((i.width * z, i.height * z), Image.NEAREST), (x, H - 10 - i.height * z))
            x += i.width * z + 20
        can.convert("RGB").save(a.check)


if __name__ == "__main__":
    main()
