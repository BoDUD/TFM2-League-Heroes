"""Jayce's four step-0 takes (Codex, 2026-10-15: hammer A1 / A2, cannon B1 / B2) cut to the game size for the review:
crown to soles BODY game rows at DENS squares a game pixel (the user's pick: PPU 1.5).

    python tools/art/design_jayce_cut.py [--review dist/jayce_packs/review]

Reads assets/source/jayce/codex_picture/jayce-*.png (squares 7-11 px, not the asked 12; alpha max 254 haze): hard alpha
(>= 128), a k-means palette of 32 (pixel_down.palette_of on Codex's raw is all dark: snap to k-means first),
pixel_down.pixelate so the man is ROWS squares crown to soles (CROWN = the hair top of each take, measured at 5x; the
weapon may stand higher), the outline of the edge. Writes assets/source/jayce/hd/cut_<take>.png - the review's game-size
look and the step-1 pack's guide for Codex's on-grid redraw (a cut from a bigger picture reads muddy: memory
muddy-design-grid-redraw), not the final design. With --review: <dir>/jayce_takes.png (the four takes side by side, 1/3)
and <dir>/jayce_lineup.png (the cuts at game size next to the top peers' game sheets, x4).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy.cluster.vq import kmeans2

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import pixel_down as PD  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "jayce")
BODY = 38          # game rows crown to soles (Darius 42 with his axe, Garen 41.6, Aatrox 40)
DENS = 1.5
ROWS = round(BODY * DENS)   # 57 squares
# take -> the hair top's row in the 1024x1536 / 1536x1024 picture (the soles = the lowest opaque row)
CROWN = {"hammer-A1": 388, "hammer-A2": 490, "cannon-B1": 148, "cannon-B2": 103}
# the cannon stance bends the knees (League's ranged idle stands ~5 % lower): the same man, so fewer rows crown-soles
BEND = {"cannon-B1": 0.95, "cannon-B2": 0.95, "cannon-side-1": 0.95, "cannon-side-2": 0.95}
# step 1 redo (Codex image_gen, 2026-10-15, assets/source/jayce/codex_side): the side-on takes, 3/4 to the right
SIDE = {"hammer-side-1": 375, "hammer-side-2": 487, "cannon-side-1": 60, "cannon-side-2": 65}
PEERS = [("darius", "idle", 1.0, 1.0), ("garen", "hd_idle", 1.9, 1.0), ("renekton", "idle", 1.0, 1.0),
         ("aatrox", "idle", 1.0, 1.0), ("sion", "idle", 1.0, 1.0)]


def kpal(a, n=32):
    px = a[a[..., 3] > 0][:, :3].astype(float)
    rng = np.random.default_rng(0)
    sub = px[rng.choice(len(px), min(60000, len(px)), replace=False)]
    c, _ = kmeans2(sub, n, seed=1, minit="++")
    return c


def cut(take):
    folder = "codex_side" if take in SIDE else "codex_picture"
    a = np.array(Image.open(os.path.join(SRC, folder, f"jayce-{take}.png")).convert("RGBA"))
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    op = a[..., 3] > 0
    ys = np.nonzero(op.any(1))[0]
    sole = ys.max() + 1
    k = ROWS * BEND.get(take, 1.0) / (sole - {**CROWN, **SIDE}[take])
    xs = np.nonzero(op[sole - 40:sole].any(0))[0]
    pivot = (int(round((xs.min() + xs.max()) / 2)), int(sole))
    f, piv = PD.pixelate(a, k, pivot, PD.edge_colour(a), kpal(a))
    yy, xx = np.nonzero(f[..., 3])
    f = f[yy.min():yy.max() + 1, xx.min():xx.max() + 1]
    return f, (piv[0] - xx.min(), piv[1] - yy.min())


def game_size(f):
    """The cut as the battlefield shows it: DENS squares a game pixel -> 1 (box mean, for the look only)."""
    im = Image.fromarray(f)
    return im.resize((round(im.width / DENS), round(im.height / DENS)), Image.BOX)


def peer(name, tag, ppu, size):
    import tfm2_ase as T
    sp = T.load_sprite(os.path.join(ROOT, "league", "champions", f"league_{name}#sheet.png"))
    im = sp.frames[sp.tag_frames(tag)[0]].convert("RGBA")
    im = im.crop(im.getbbox())
    if ppu != 1.0:
        im = im.resize((round(im.width / ppu * size), round(im.height / ppu * size)), Image.BOX)
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    os.makedirs(os.path.join(SRC, "hd"), exist_ok=True)
    cuts = {}
    for take in list(CROWN) + list(SIDE):
        f, piv = cut(take)
        Image.fromarray(f).save(os.path.join(SRC, "hd", f"cut_{take}.png"))
        cuts[take] = f
        print(take, "cut", f.shape[1], "x", f.shape[0], "standing col", piv[0],
              "colours", len(np.unique(f[f[..., 3] > 0][:, :3], axis=0)))
    if not a.review:
        return
    os.makedirs(a.review, exist_ok=True)
    bg = (200, 200, 200)
    # 1. the four takes at 1/3
    ims = [Image.open(os.path.join(SRC, "codex_picture", f"jayce-{t}.png")).convert("RGBA") for t in CROWN]
    w = sum(i.width for i in ims) // 3 + 30
    sheet = Image.new("RGB", (w, 1536 // 3 + 30), bg)
    x = 0
    d = ImageDraw.Draw(sheet)
    for t, im in zip(CROWN, ims):
        sm = im.resize((im.width // 3, im.height // 3), Image.LANCZOS)
        sheet.paste(sm, (x, 24), sm)
        d.text((x + 8, 4), t, fill=(0, 0, 0))
        x += sm.width + 10
    sheet.save(os.path.join(a.review, "jayce_takes.png"))
    # 2. game size x4 next to the peers, soles on one line; then the 1.5-density cuts themselves x4
    z = 4
    row = [(f"jayce {t}", game_size(cuts[t])) for t in CROWN] + [(p[0], peer(*p)) for p in PEERS]
    hmax = max(im.height for _, im in row)
    W = sum(im.width + 8 for _, im in row) * z + 20
    can = Image.new("RGB", (W, (hmax + 14) * z + 20), (90, 110, 70))
    d = ImageDraw.Draw(can)
    x = 10
    for name, im in row:
        big = im.resize((im.width * z, im.height * z), Image.NEAREST)
        can.paste(big, (x, 10 + (hmax - im.height) * z + 10 * z // 2), big)
        d.text((x, 4), f"{name} {im.height}", fill=(255, 255, 255))
        x += (im.width + 8) * z
    can.save(os.path.join(a.review, "jayce_lineup.png"))
    z = 6
    W = sum(f.shape[1] + 6 for f in cuts.values()) * z + 20
    H = max(f.shape[0] for f in cuts.values()) * z + 40
    can = Image.new("RGB", (W, H), bg)
    x = 10
    for t, f in cuts.items():
        im = Image.fromarray(f)
        big = im.resize((im.width * z, im.height * z), Image.NEAREST)
        can.paste(big, (x, H - 10 - big.height), big)
        x += (f.shape[1] + 6) * z
    can.save(os.path.join(a.review, "jayce_cuts_x6.png"))
    print("review written to", a.review)


if __name__ == "__main__":
    main()
