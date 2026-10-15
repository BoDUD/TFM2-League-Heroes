"""Katarina's two step-0 takes (Codex, 2026-10-15: K1 / K2 from one prompt) cut to the game size for the review:
crown to soles BODY game rows at DENS squares a game pixel (the user's pick: PPU 1.5). design_jayce_cut.py's way.

    python tools/art/design_katarina_cut.py [--review <dir>]

Reads assets/source/katarina/codex_picture/katarina-K*.png (K1 on squares of ~12 px, K2 uneven 9-14 px; crown to soles
810 / 775 px, not the asked 684; alpha max 254 with a red haze round her): hard alpha
(>= 128), a k-means palette of 32 (pixel_down.palette_of on Codex's raw is all dark: snap to k-means first),
pixel_down.pixelate so the man is ROWS squares crown to soles (CROWN = the hair top of each take, measured at 5x; the
daggers may stand higher), the outline of the edge. Writes assets/source/katarina/hd/cut_<take>.png - the review's
game-size look and the step-1 pack's guide for Codex's on-grid redraw (a cut from a bigger picture reads muddy), not the
final design. With --review: <dir>/katarina_takes.png (both takes, 1/2) and <dir>/katarina_lineup.png (the cuts at game
size next to the mid peers' game sheets, x4).
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

SRC = os.path.join(ROOT, "assets", "source", "katarina")
BODY = 38          # game rows crown to soles (league_jayce 38, league_talon 40, league_zed 40)
DENS = 1.5
ROWS = round(BODY * DENS)   # 57 squares
# take -> the hair top's row in the 1024x1536 picture (the soles = the lowest opaque row)
CROWN = {"K1": 699, "K2": 725}
# step 1 (Codex image_gen, 2026-10-15, assets/source/katarina/codex_side): the side-on takes, 3/4 to the right
SIDE = {"side-1": 601, "side-2": 612}
BEND = {}
PEERS = [("talon", "idle", 1.0, 1.0), ("zed", "idle", 1.0, 1.0), ("akali", "idle", 1.0, 1.0),
         ("leblanc", "idle", 1.0, 1.0), ("kassadin", "hd_idle", 2.42, 1.0), ("jayce", "hd_idle", 1.5, 1.0)]


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def kpal(a, n=32):
    px = a[a[..., 3] > 0][:, :3].astype(float)
    rng = np.random.default_rng(0)
    sub = px[rng.choice(len(px), min(60000, len(px)), replace=False)]
    c, _ = kmeans2(sub, n, seed=1, minit="++")
    return c


def cut(take):
    folder = "codex_side" if take in SIDE else "codex_picture"
    a = np.array(Image.open(lp(os.path.join(SRC, folder, f"katarina-{take}.png"))).convert("RGBA"))
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
    sp = T.load_sprite(lp(os.path.join(ROOT, "league", "champions", f"league_{name}#sheet.png")))
    im = sp.frames[sp.tag_frames(tag)[0]].convert("RGBA")
    im = im.crop(im.getbbox())
    if ppu != 1.0:
        im = im.resize((round(im.width / ppu * size), round(im.height / ppu * size)), Image.BOX)
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    os.makedirs(lp(os.path.join(SRC, "hd")), exist_ok=True)
    cuts = {}
    for take in list(CROWN) + list(SIDE):
        f, piv = cut(take)
        Image.fromarray(f).save(lp(os.path.join(SRC, "hd", f"cut_{take}.png")))
        cuts[take] = f
        print(take, "cut", f.shape[1], "x", f.shape[0], "standing col", piv[0],
              "colours", len(np.unique(f[f[..., 3] > 0][:, :3], axis=0)))
    if not a.review:
        return
    os.makedirs(a.review, exist_ok=True)
    bg = (200, 200, 200)
    # 1. the four takes at 1/3
    ims = [Image.open(lp(os.path.join(SRC, "codex_picture", f"katarina-{t}.png"))).convert("RGBA") for t in CROWN]
    w = sum(i.width for i in ims) // 2 + 30
    sheet = Image.new("RGB", (w, 1536 // 2 + 30), bg)
    x = 0
    d = ImageDraw.Draw(sheet)
    for t, im in zip(CROWN, ims):
        sm = im.resize((im.width // 2, im.height // 2), Image.LANCZOS)
        sheet.paste(sm, (x, 24), sm)
        d.text((x + 8, 4), t, fill=(0, 0, 0))
        x += sm.width + 10
    sheet.save(os.path.join(a.review, "katarina_takes.png"))
    # 2. game size x4 next to the peers, soles on one line; then the 1.5-density cuts themselves x4
    z = 4
    row = [(f"katarina {t}", game_size(cuts[t])) for t in ["K1"] + list(SIDE)] + [(p[0], peer(*p)) for p in PEERS]
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
    can.save(os.path.join(a.review, "katarina_lineup.png"))
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
    can.save(os.path.join(a.review, "katarina_cuts_x6.png"))
    print("review written to", a.review)


if __name__ == "__main__":
    main()
