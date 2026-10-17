"""Katarina's design (step 1, the user's picks 2026-10-15): the front and the side-on view, read back from Codex.

    python tools/art/design_katarina_hd.py [--check out.png]

The picks: front = step-0 take K1 (assets/source/katarina/codex_picture, ~12 px a square), side = side-1
(assets/source/katarina/codex_side: image_gen, 3/4 to the right, drawn taller than K1: 911 px crown to soles against
810). Each is read on its own grid (regrid.py), then brought to the front's own rows (crown to soles ~67 squares,
about 1.77 squares a game pixel at 38 game rows) - pixel_down.pixelate where a take's own grid differs. One palette
(k-means PAL_N over both), snapped everywhere. The frames stay at this density through steps 2-3; ppu_restyle brings
them to PPU 1.5 at the end (the user's pick), Milio's and Jayce's way (design_jayce_hd.py).
One face (memory one-face-all-frames): the front's head (HEAD box: hair and face down to the chin, without the raised
dagger, the hilts on her back and the long hair below the chin) goes onto the side view, placed where it matches its
own head best (masked colour distance over shifts), its own head cleared under it first.
Writes assets/source/katarina/hd/{front,side}.png, head.png (the template every action frame gets) and design.json
(sizes, crown / soles rows, standing columns, the head's top-left in each).
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

SRC = os.path.join(ROOT, "assets", "source", "katarina")
TAKES = {  # design -> (file, the hair top's row in the picture)
    "front": ("codex_picture/katarina-K1.png", 699),
    "side": ("codex_side/katarina-side-1.png", 601),
}
PAL_N = 40
SPECK = 2000           # raw px: smaller pieces are haze specks
GAME_ROWS = 38
FINAL_PPU = 1.5
# the head on the front (regridded, its own rows): rows HEAD_ROWS from the crown, columns HEAD_COLS from the head's own
# middle (the hair's columns in the top rows); inside the box only hair reds, skin, the green eyes, the lips and the
# outline touching them count (the dagger's greys, the hilts' browns and the leather stay with the body)
HEAD_ROWS = 21
HEAD_COLS = (-12, 12)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def hard(path):
    a = np.array(Image.open(lp(path)).convert("RGBA"))
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    lab, n = ndimage.label(a[..., 3] > 0)
    s = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    a[~np.isin(lab, [i + 1 for i in range(n) if s[i] >= SPECK])] = 0
    return a


def kpal(arrays, n):
    px = np.concatenate([a[a[..., 3] > 0][:, :3] for a in arrays]).astype(float)
    sub = px[np.random.default_rng(0).choice(len(px), min(80000, len(px)), replace=False)]
    return kmeans2(sub, n, seed=1, minit="++")[0]


def snap(a, pal):
    out = a.copy()
    m = a[..., 3] > 0
    d = ((a[m][:, None, :3].astype(float) - pal[None]) ** 2).sum(-1)
    out[m, :3] = np.clip(pal[d.argmin(1)].round(), 0, 255).astype(np.uint8)
    return out


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()


def read(name):
    """The take on its own grid, cropped; with the crown's row in it (the raw crown row / the square size)."""
    path, crown = TAKES[name]
    raw = hard(os.path.join(SRC, path))
    g, size, _ = RG.regrid(raw)
    g = crop(g)
    ys = np.nonzero(raw[..., 3].any(1))[0]
    crown_g = int(round((crown - ys.min()) / size))
    return g, crown_g, size


def feet_mid(a):
    ys = np.nonzero(a[..., 3].any(1))[0]
    xs = np.nonzero(a[ys.max() - 5:ys.max() + 1, :, 3].any(0))[0]
    return (xs.min() + xs.max()) / 2.0


def to_rows(a, crown, rows, pal):
    """a (cropped, crown row given) brought to `rows` crown to soles."""
    have = a.shape[0] - crown
    k = rows / have
    if abs(k - 1) < 0.02:
        return a, crown
    piv = (int(round(feet_mid(a))), a.shape[0])
    b, _ = PD.pixelate(a, k, piv, PD.edge_colour(a), pal)
    b = crop(b)
    return b, b.shape[0] - rows


def head_mid(f, crown):
    xs = np.nonzero(f[crown:crown + 4, :, 3].any(0))[0]
    return int(round((xs.min() + xs.max()) / 2))


def face_colours(f):
    rgb = f[..., :3].astype(int)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    hair = (r > g + 75) & (r > b + 60)                              # the reds, light to wine (not the hilts' browns)
    skin = (r > 170) & (g > 110) & (b > 80) & (r > b + 30)
    eyes = (g > r + 15) & (g > b)
    return hair | skin | eyes


def head_mask(f, crown):
    mid = head_mid(f, crown)
    box = np.zeros(f.shape[:2], bool)
    box[crown:crown + HEAD_ROWS, max(0, mid + HEAD_COLS[0]):mid + HEAD_COLS[1]] = True
    op = f[..., 3] > 0
    col = face_colours(f) & box & op
    lab, n = ndimage.label(col)
    top = lab[crown:crown + 4][lab[crown:crown + 4] > 0]
    keep = np.isin(lab, np.unique(top)) if len(top) else col
    keep = ndimage.binary_fill_holes(keep)
    # its outline: dark squares in the box touching the kept head
    dark = op & (f[..., :3].astype(int).sum(-1) < 120) & box
    keep |= dark & ndimage.binary_dilation(keep, structure=np.ones((3, 3), bool))
    return ndimage.binary_fill_holes(keep) & op


def paste_head(dst, crown, head, hmask):
    """The head where it matches dst's own head best (rows crown-3 .. crown+5), dst's own head cleared under it."""
    hh, hw = hmask.shape
    H, W = dst.shape[:2]
    op = dst[..., 3] > 0
    xs = np.nonzero(op[crown:crown + hh].any(0))[0]
    best = None
    for dy in range(-3, 6):
        for x in range(max(0, xs.min() - 10), min(W - hw, xs.max() - hw + 10) + 1):
            y = crown + dy
            if y < 0 or y + hh > H:
                continue
            win = dst[y:y + hh, x:x + hw]
            both = hmask & (win[..., 3] > 0)
            miss = (hmask & (win[..., 3] == 0)).sum() + ((~hmask) & (win[..., 3] > 0) & (np.arange(hh)[:, None] < hh // 2)).sum() * 0.5
            dist = ((win[both][:, :3].astype(float) - head[both][:, :3]) ** 2).sum(-1).mean() if both.any() else 1e9
            score = dist + 40000 * miss / max(1, hmask.sum())
            if best is None or score < best[0]:
                best = (score, y, x)
    _, y, x = best
    out = dst.copy()
    # dst's own head cleared: above the template's cheek rows (hh - 7) everything in its columns +- 2 except the weapon
    # (golds and greys); below that, down to the chin, only hair / skin (the collar and scarf stay)
    rgb = dst[..., :3].astype(int)
    grey = (np.abs(rgb[..., 0] - rgb[..., 1]) < 22) & (np.abs(rgb[..., 1] - rgb[..., 2]) < 26) & (rgb.sum(-1) > 150)
    gold = (rgb[..., 0] > 90) & (rgb[..., 0] < 170) & (rgb[..., 1] > 40) & (rgb[..., 2] < rgb[..., 1])  # the hilts' browns
    face = face_colours(dst)
    skin, hair = face, face
    reg = np.zeros(op.shape, bool)
    reg[max(0, y - 3):y + hh - 2, max(0, x - 2):x + hw + 2] = True
    upper = np.zeros(op.shape, bool)
    upper[max(0, y - 3):y + hh - 7, max(0, x - 2):x + hw + 2] = True
    out[upper & op & face] = 0          # only her old hair and face: the hilts and the blade stay
    out[reg & ~upper & op & (skin | hair)] = 0
    tgt = out[y:y + hh, x:x + hw]
    tgt[hmask] = head[hmask]
    # the old head's outline left floating: dark squares in the region touching no light square of the body (the
    # template's own squares do not count: its edge gets its outline back from complete_outline), twice
    templ = np.zeros(op.shape, bool)
    templ[y:y + hh, x:x + hw] = hmask
    for _ in range(2):
        a = out[..., 3] > 0
        dark = a & (out[..., :3].astype(int).sum(-1) < 90)
        light = ndimage.binary_dilation(a & ~dark & ~templ, structure=np.ones((3, 3), bool))
        wide = np.zeros(op.shape, bool)
        wide[max(0, y - 4):y + hh, max(0, x - 2):x + hw + 2] = True   # her hilts beside the head stay
        drop = wide & dark & ~light & ~templ
        out[drop] = 0
    return out, (int(y), int(x))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", help="write a review picture (both designs at 5x) here")
    a = ap.parse_args()
    got = {n: read(n) for n in TAKES}
    for n, (g, c, s) in got.items():
        print(f"{n}: own grid ~{s:.1f} px, {g.shape[1]}x{g.shape[0]}, crown row {c}, crown-soles {g.shape[0] - c}")
    pal = kpal([g for g, _, _ in got.values()], PAL_N)
    ff, fcrown, _ = got["front"]
    rows = ff.shape[0] - fcrown
    out, crowns = {}, {}
    for n, (g, c, _) in got.items():
        b, bc = to_rows(g, c, rows, pal)
        out[n], crowns[n] = snap(b, pal), bc
    hm = head_mask(out["front"], crowns["front"])
    ys, xs = np.nonzero(hm)
    head = out["front"][ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    hmask = hm[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    head[~hmask] = 0
    info = {"rows": rows, "game_rows": GAME_ROWS, "final_ppu": FINAL_PPU, "dense_per_game_px": rows / GAME_ROWS,
            "designs": {}}
    outline = PD.edge_colour(ff)
    for n in TAKES:
        d = out[n]
        at = (int(ys.min()), int(xs.min()))
        if n != "front":
            d, at = paste_head(d, crowns[n], head, hmask)
            # the old hair's outline specks left apart from her (pieces of 3 squares or less, 8-connected)
            lab, k = ndimage.label(d[..., 3] > 0, structure=np.ones((3, 3), bool))
            size = ndimage.sum(np.ones(lab.shape), lab, range(1, k + 1))
            d[np.isin(lab, [i + 1 for i in range(k) if size[i] <= 3])] = 0
            d, added, _ = strips.complete_outline(d, color=outline)
        out[n] = d
        info["designs"][n] = {"size": [int(d.shape[1]), int(d.shape[0])], "crown": int(crowns[n]),
                              "soles": int(d.shape[0] - 1), "standing_col": float(feet_mid(d)), "head_at": list(at)}
        print(n, "->", d.shape[1], "x", d.shape[0], "crown", crowns[n], "head at", at)
    os.makedirs(lp(os.path.join(SRC, "hd")), exist_ok=True)
    for n, d in out.items():
        Image.fromarray(d).save(lp(os.path.join(SRC, "hd", n + ".png")))
    Image.fromarray(head).save(lp(os.path.join(SRC, "hd", "head.png")))
    info["palette"] = [[int(v) for v in c] for c in pal.round()]
    json.dump(info, open(lp(os.path.join(SRC, "hd", "design.json")), "w"), indent=1)
    if a.check:
        z = 5
        ims = [Image.fromarray(out[n]) for n in TAKES] + [Image.fromarray(head)]
        W = sum(i.width for i in ims) * z + 120
        H = max(i.height for i in ims) * z + 20
        can = Image.new("RGBA", (W, H), (205, 200, 185, 255))
        x = 20
        for i in ims:
            can.alpha_composite(i.resize((i.width * z, i.height * z), Image.NEAREST), (x, H - 10 - i.height * z))
            x += i.width * z + 20
        can.convert("RGB").save(a.check)


if __name__ == "__main__":
    main()
