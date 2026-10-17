"""Step-0 read-back of Codex's Smolder pictures (assets/source/smolder/codex_picture/raw): every take brought to the
PPU 1.5 design size, shown at game size beside this pack's heroes, for the user's A / B pick.

    python tools/art/design_smolder_cut.py [--rows 51] [--out dist/smolder_packs/review]

Codex drew finer than asked (squares 6-11 px, figures 820-940 px tall instead of 612) with a soft alpha haze, so a
take is read like this: alpha cut at 128, the head top found under the horn flames (bright orange/yellow pieces at
the top), the figure brought to --rows squares from head top to soles by pixel_down.pixelate (cell mean snapped to
its own colours, outline where dark), then pixel_down.crisp (one palette, majority passes, edge lines) - the PPU
heroes' look. Writes <out>/smolder_cut_<take>.png (x6) and <out>/smolder_lineup.png (game size x4: Smolder's dense
squares at 4 / 1.5, other heroes at their own density).
"""
import argparse
import glob
import io
import json
import os
import re
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import pixel_down as P  # noqa: E402

RAW = os.path.join(REPO, "assets", "source", "smolder", "codex_picture", "raw")
PPU = 1.5
STAND = 0.95        # standing on four legs / sitting up, head top to soles (League's model: 1189 / 1250)


def head_top(a):
    """First row of the figure that is not horn flame (flames = bright orange / yellow, alone at the top)."""
    op = a[..., 3] > 0
    r, g, b = (a[..., i].astype(int) for i in range(3))
    flame = op & (r > 200) & (g > 110) & (b < 120) & (r - b > 120)
    rows = np.nonzero(op.any(1))[0]
    for y in rows:
        line = op[y]
        if (line & ~flame[y]).sum() >= max(3, 0.25 * line.sum()) and not flame[y:y + 6].any():
            return y
    return rows[0]


def kmeans_palette(a, n=32, seed=0):
    """The take's own n colours (k-means in Lab on its opaque pixels; the near-black outline kept as one of them):
    pixel_down.palette_of on a raw take gives only dark colours (league_kindred's lesson)."""
    px = a[a[..., 3] > 0][:, :3].astype(float)
    rng = np.random.default_rng(seed)
    s = px[rng.choice(len(px), min(len(px), 30000), replace=False)]
    lab = P._lab(s)
    c = lab[rng.choice(len(lab), n, replace=False)]
    for _ in range(30):
        idx = ((lab[:, None] - c[None]) ** 2).sum(-1).argmin(1)
        for j in range(n):
            if (idx == j).any():
                c[j] = lab[idx == j].mean(0)
    idx = ((lab[:, None] - c[None]) ** 2).sum(-1).argmin(1)
    return np.array([s[idx == j].mean(0) for j in range(n) if (idx == j).any()])


def cut(path, rows):
    a = np.array(Image.open(path).convert("RGBA"))
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    ys, xs = np.nonzero(a[..., 3])
    sole, top = ys.max() + 1, head_top(a)
    k = rows / (sole - top)
    cx = (xs.min() + xs.max()) / 2
    pal = kmeans_palette(a)
    out, piv = P.pixelate(a, k, (cx, sole), tuple(int(v) for v in pal[pal.sum(1).argmin()]), pal=pal)
    out = P.crisp([out], n=24, passes=1, contrast=1.1)[0]
    ys, xs = np.nonzero(out[..., 3])
    return out[ys.min():ys.max() + 1, xs.min():xs.max() + 1], (sole - top, k)


def sheet_frame(hero, tag):
    base = os.path.join(REPO, "league", "champions", hero)
    sheet = np.array(Image.open(base + "#sheet.png").convert("RGBA"))
    f = json.load(open(base + "#anim.fanim", encoding="utf-8-sig"))["anims"][tag]["frames"][0]["data"]
    x, y, w, h = (int(f[k]) for k in "xywh")
    fr = sheet[y:y + h, x:x + w]
    ys, xs = np.nonzero(fr[..., 3])
    return fr[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def hd_table():
    src = open(os.path.join(REPO, "addons", "league_main", "src", "hd.rs"), encoding="utf-8").read()
    ppu = dict((h, float(p)) for h, p in re.findall(r'\("(league_[a-z]+)", ([0-9.]+), include_str', src))
    return ppu, {"league_" + h: v for h, v in P.sizes_of().items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=51)
    ap.add_argument("--out", default=os.path.join(REPO, "dist", "smolder_packs", "review"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    cuts = {}
    for path in sorted(glob.glob(os.path.join(RAW, "*.png"))):
        tag = re.sub(r"smolder-model-|attempt-", "", os.path.basename(path)[:-4])
        im, (h, k) = cut(path, a.rows if "-A-" in path else round(a.rows * STAND))
        cuts[tag] = im
        Image.fromarray(im).resize((im.shape[1] * 6, im.shape[0] * 6), Image.NEAREST).save(
            os.path.join(a.out, f"smolder_cut_{tag}.png"))
        print(f"{tag}: head->soles {h} raw px, k {k:.3f}, cut {im.shape[1]}x{im.shape[0]}, "
              f"game {im.shape[1] / PPU:.0f}x{im.shape[0] / PPU:.0f}")
    ppu, sizes = hd_table()
    Z, GY = 4, 300
    peers = ["league_twitch", "league_kogmaw", "league_jinx", "league_zeri", "league_nilah", "league_bard"]
    W = 60 + sum(c.shape[1] * Z / PPU + 40 for c in cuts.values()) + 170 * len(peers)
    img = Image.new("RGBA", (int(W), 380), (104, 112, 72, 255))
    d = ImageDraw.Draw(img)

    def put(fr, scale, x, label):
        im = Image.fromarray(fr)
        im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.NEAREST)
        img.alpha_composite(im, (round(x), GY - im.height))
        d.text((x, GY + 14), label, fill=(255, 255, 255, 255))
        return im.width

    x = 30
    for tag, c in cuts.items():
        x += put(c, Z / PPU, x, tag) + 40
    for hero in peers:
        if hero in ppu:
            fr, s = sheet_frame(hero, "hd_idle"), Z * sizes.get(hero, 1.0) / ppu[hero]
        else:
            fr, s = sheet_frame(hero, "idle"), Z
        x += put(fr, s, x, hero[7:]) + 40
    d.line([(0, GY), (img.width, GY)], fill=(60, 66, 40, 255))
    img = img.crop((0, 0, int(x), img.height))
    img.convert("RGB").save(os.path.join(a.out, "smolder_lineup.png"))
    print("written", os.path.join(a.out, "smolder_lineup.png"), img.size)


if __name__ == "__main__":
    main()
