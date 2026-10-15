"""Jayce's design (step 1, the user's picks 2026-10-15): both forms' fronts and side-on views, read back from Codex.

    python tools/art/design_jayce_hd.py [--check out.png]

The picks: hammer front = step-0 take A2 (assets/source/jayce/codex_picture, ~10 px a square), cannon front = B2 (~8 px),
hammer side = side-2, cannon side = side-2 (assets/source/jayce/codex_side: image_gen, 3/4 to the right; the script-drawn
step-1 delivery in codex_model was not used). Each is read on its own grid (regrid.py), then brought to one density:
the hammer front's own rows (crown to soles HAMMER_ROWS, about 2.65 squares a game pixel at 38 game rows), the cannon
stance BEND of that (knees bent) - pixel_down.pixelate where a take's own grid differs. One palette (k-means PAL_N over
all four), snapped everywhere. The frames stay at this density through steps 2-3; ppu_restyle brings them to PPU 1.5
at the end (the user's pick), Milio's way.
One face (memory one-face-all-frames): the hammer front's head (HEAD box: hair, face and chin, without the fur collar,
the scarf and the hammer beside it) goes onto the cannon front and both side views, placed where it matches their own
head best (masked colour distance over shifts), their own head cleared under it first.
Writes assets/source/jayce/hd/{hammer_front,hammer_side,cannon_front,cannon_side}.png, head.png (the template every
action frame gets) and design.json (sizes, crown / soles rows, standing columns, the head's top-left in each).
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

SRC = os.path.join(ROOT, "assets", "source", "jayce")
TAKES = {  # design -> (file, the hair top's row in the picture)
    "hammer_front": ("codex_picture/jayce-hammer-A2.png", 490),
    "cannon_front": ("codex_picture/jayce-cannon-B2.png", 103),
    "hammer_side": ("codex_side/jayce-hammer-side-2.png", 487),
    "cannon_side": ("codex_side/jayce-cannon-side-2.png", 65),
}
BEND = 0.95            # the cannon stance's crown-to-soles against the hammer's (League's ranged idle)
PAL_N = 40
SPECK = 2000           # raw px: smaller pieces are haze specks
GAME_ROWS = 38
FINAL_PPU = 1.5
# the head on the hammer front (regridded, its own rows): rows HEAD_ROWS from the crown, columns HEAD_COLS from the
# standing column; cream fur-collar squares right of COLLAR_COL and the scarf's reds are left to the body
HEAD_ROWS = 22          # crown .. the chin (row 46 of hammer_front: the scarf starts under it)
HEAD_COLS = (-16, 17)   # the ear on the image left (cols 42-46) to the right cheek; the hammer's grey shaft left out
COLLAR_COL = 10
SCARF_FROM = 17         # rows from the crown: the scarf's reds below this are the body's (the lips above are the face)


def hard(path):
    a = np.array(Image.open(path).convert("RGBA"))
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


def head_mask(f, crown):
    mid = int(round(feet_mid(f)))
    m = np.zeros(f.shape[:2], bool)
    c0, c1 = mid + HEAD_COLS[0], mid + HEAD_COLS[1]
    m[crown:crown + HEAD_ROWS, c0:c1] = True
    m &= f[..., 3] > 0
    rgb = f[..., :3].astype(int)
    cols = np.arange(f.shape[1])[None, :]
    rows_ = np.arange(f.shape[0])[:, None]
    cream = (rgb.sum(-1) > 560) & (cols >= mid + COLLAR_COL)
    scarf = (rgb[..., 0] > 110) & (rgb[..., 1] < 60) & (rgb[..., 2] < 60) & (rows_ >= crown + SCARF_FROM)
    grey = (np.abs(rgb[..., 0] - rgb[..., 1]) < 22) & (np.abs(rgb[..., 1] - rgb[..., 2]) < 26) & (rgb.sum(-1) > 150)
    m &= ~cream & ~scarf & ~grey
    # the collar's / shaft's outline left in the box: dark squares touching no light square of the head
    # (only at the box's sides, where the collar and the shaft are: dark hair inside the head stays)
    dark = (rgb.sum(-1) < 90) & ((cols >= mid + COLLAR_COL - 2) | (cols <= mid + HEAD_COLS[0] + 4))
    for _ in range(2):
        m &= ~(dark & ~ndimage.binary_dilation(m & ~dark, structure=np.ones((3, 3), bool)))
    lab, n = ndimage.label(m)
    top = lab[crown:crown + 3][lab[crown:crown + 3] > 0]
    return np.isin(lab, np.unique(top)) if len(top) else m


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
    gold = (rgb[..., 0] > 150) & (rgb[..., 1] > 110) & (rgb[..., 2] < rgb[..., 1] - 30)
    skin = (rgb[..., 0] > 150) & (rgb[..., 0] > rgb[..., 2] + 50) & (rgb[..., 1] > 80) & (rgb[..., 1] < 200)
    hair = (rgb[..., 0] < 130) & (rgb[..., 0] > rgb[..., 2]) & (rgb.sum(-1) < 260)
    reg = np.zeros(op.shape, bool)
    reg[max(0, y - 3):y + hh - 2, max(0, x - 2):x + hw + 2] = True
    upper = np.zeros(op.shape, bool)
    upper[max(0, y - 3):y + hh - 7, max(0, x - 2):x + hw + 2] = True
    out[upper & op & ~grey & ~gold] = 0
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
        wide[max(0, y - 4):y + hh, max(0, x - 8):x + hw + 8] = True
        drop = wide & dark & ~light & ~templ
        out[drop] = 0
    return out, (int(y), int(x))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", help="write a review picture (the four designs at 6x) here")
    a = ap.parse_args()
    got = {n: read(n) for n in TAKES}
    for n, (g, c, s) in got.items():
        print(f"{n}: own grid ~{s:.1f} px, {g.shape[1]}x{g.shape[0]}, crown row {c}, crown-soles {g.shape[0] - c}")
    pal = kpal([g for g, _, _ in got.values()], PAL_N)
    hf, hcrown, _ = got["hammer_front"]
    rows = hf.shape[0] - hcrown
    out, crowns = {}, {}
    for n, (g, c, _) in got.items():
        want = rows if n.startswith("hammer") else int(round(rows * BEND))
        b, bc = to_rows(g, c, want, pal)
        out[n], crowns[n] = snap(b, pal), bc
    hm = head_mask(out["hammer_front"], crowns["hammer_front"])
    ys, xs = np.nonzero(hm)
    head = out["hammer_front"][ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    hmask = hm[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    head[~hmask] = 0
    info = {"rows": rows, "cannon_rows": int(round(rows * BEND)), "game_rows": GAME_ROWS, "final_ppu": FINAL_PPU,
            "dense_per_game_px": rows / GAME_ROWS, "designs": {}}
    outline = PD.edge_colour(hf)
    for n in TAKES:
        d = out[n]
        at = (int(ys.min()), int(xs.min()))
        if n != "hammer_front":
            d, at = paste_head(d, crowns[n], head, hmask)
            d, added, _ = strips.complete_outline(d, color=outline)
        out[n] = d
        info["designs"][n] = {"size": [int(d.shape[1]), int(d.shape[0])], "crown": int(crowns[n]),
                              "soles": int(d.shape[0] - 1), "standing_col": float(feet_mid(d)), "head_at": list(at)}
        print(n, "->", d.shape[1], "x", d.shape[0], "crown", crowns[n], "head at", at)
    os.makedirs(os.path.join(SRC, "hd"), exist_ok=True)
    for n, d in out.items():
        Image.fromarray(d).save(os.path.join(SRC, "hd", n + ".png"))
    Image.fromarray(head).save(os.path.join(SRC, "hd", "head.png"))
    info["palette"] = [[int(v) for v in c] for c in pal.round()]
    json.dump(info, open(os.path.join(SRC, "hd", "design.json"), "w"), indent=1)
    if a.check:
        z = 5
        ims = [Image.fromarray(out[n]) for n in TAKES]
        W = sum(i.width for i in ims) * z + 100
        H = max(i.height for i in ims) * z + 20
        can = Image.new("RGBA", (W, H), (205, 200, 185, 255))
        x = 20
        for i in ims:
            can.alpha_composite(i.resize((i.width * z, i.height * z), Image.NEAREST), (x, H - 10 - i.height * z))
            x += i.width * z + 20
        can.convert("RGB").save(a.check)


if __name__ == "__main__":
    main()
