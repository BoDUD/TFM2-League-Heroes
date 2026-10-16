#!/usr/bin/env python3
"""Codex's pictures made chibi (Q版) before they become PPU designs - the user, 2026-10-16: 「剑姬赵兴妖姬贾克斯要做成Q版的
现在太逼真了」「还有天使」 (Fiora, Xin Zhao, LeBlanc, Jax, Kayle; then 「锐雯记得模型做q版一点」). Of those, the user then kept only Jax and Riven
for now (「天使剑姬暂时不重做了」「赵兴妖姬也暂时不重做」); their specs stay for later.

    python tools/art/chibi_warp.py [--hero leblanc ...] [--preview DIR]   # writes assets/source/<hero>/hd/chibi.png

league_zeri's restyle (tools/art/ppu_restyle.py: the head scaled up evenly round the neck, the body below it wider and
shorter, a band between) done on the picture itself, where it is fine enough that nothing shows the resampling once the
design is brought to its PPU. What would bend under it stays rigid:
  * props (a staff, a lamp post, a spear, a sword, an arm holding a rapier out, wings) are cut out first (`props`:
    polygons in picture pixels, minus the `over` polygons - the hands gripping them), the body they hid filled from
    round it, and put back after: `rigid` props moved with their anchor (the grip, a shoulder, the back) at `scale`,
    `body` props (Xin Zhao's spear, gripped by both hands) through the body's own straight-line map, so both hands stay
    on a shaft that stays straight;
  * the gripping hands are drawn again over the props.
Head 1.7 x, body 0.82 x as tall and 1.15 x as wide round the soles' middle: the head about 40 % of the height, like the 1x pack (the picture ~4 heads tall).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402

HEAD, SHORT, WIDE, BAND = 1.7, 0.82, 1.15, 60
# the head's top in the picture (cropped), when something stands above it (wings, a lamp, a spear tip, a ponytail)
HEAD_TOP = {"kayle": 124, "jax": 185, "xinzhao": 153}
# per hero, in the picture's pixels (cropped to the figure, R.load_picture): neck = the chin's bottom middle; props =
# [dict(poly, kind "rigid" | "body", anchor, scale, z "front" | "back", over [polys])]
def band(p0, p1, hw0, hw1=None):
    """A polygon hugging the segment p0 -> p1, hw0 wide at p0 and hw1 at p1 (a shaft)."""
    hw1 = hw0 if hw1 is None else hw1
    (x0, y0), (x1, y1) = p0, p1
    L = max(1e-6, np.hypot(x1 - x0, y1 - y0))
    nx, ny = -(y1 - y0) / L, (x1 - x0) / L
    return [(x0 + nx * hw0, y0 + ny * hw0), (x1 + nx * hw1, y1 + ny * hw1), (x1 - nx * hw1, y1 - ny * hw1),
            (x0 - nx * hw0, y0 - ny * hw0)]


SPECS = {
    # 「锐雯记得模型做q版一点 模型别太大」: her stance is wide already, so no widening
    "riven": dict(neck=(300, 195), wide=1.0, props=[
        dict(poly=[(376, 384), (410, 372), (445, 405), (530, 422), (700, 556), (814, 596), (814, 749), (676, 704),
                   (556, 622), (438, 528), (418, 472), (388, 428)],
             kind="rigid", anchor=(442, 426), z="front", over=[[(414, 398), (476, 398), (476, 456), (414, 456)]])]),
    "leblanc": dict(neck=(490, 330), props=[
        dict(poly=[(95, 40), (250, 25), (310, 330), (305, 445), (262, 445), (200, 360), (95, 300)],
             kind="rigid", anchor=(285, 480), z="front", over=[[(250, 437), (342, 437), (345, 545), (255, 545)]]),
        dict(poly=band((292, 470), (370, 1060), 17), kind="rigid", anchor=(285, 480), z="front",
             over=[[(250, 437), (342, 437), (345, 545), (255, 545)]]),
        dict(poly=band((365, 1040), (395, 1200), 32, 22), kind="rigid", anchor=(285, 480), z="front", over=[])]),
    "jax": dict(neck=(525, 420), props=[
        dict(poly=[(0, 0), (232, 0), (232, 345), (0, 345)], kind="rigid", anchor=(205, 655), z="front", over=[]),
        dict(poly=band((150, 340), (300, 1110), 22), kind="rigid", anchor=(205, 655), z="front",
             over=[[(140, 583), (275, 583), (275, 733), (140, 733)]]),
        dict(poly=band((295, 1080), (330, 1200), 40, 30), kind="rigid", anchor=(205, 655), z="front", over=[])]),
    "xinzhao": dict(neck=(548, 338), props=[
        dict(poly=band((4, 994), (962, 262), 20), kind="body", z="front",
             over=[[(642, 472), (772, 472), (772, 595), (642, 595)], [(330, 650), (442, 650), (442, 758), (330, 758)]]),
        dict(poly=[(870, 345), (880, 250), (940, 170), (1000, 110), (1100, 30), (1181, -5), (1188, 40), (1100, 190),
                   (1112, 565), (1050, 582), (990, 440), (940, 345)], kind="body", z="front", over=[])]),
    "fiora": dict(neck=(425, 140), props=[
        dict(poly=[(500, 160), (560, 140), (660, 85), (720, 80), (760, 100), (1380, 68), (1380, 112), (770, 140),
                   (720, 215), (660, 230), (600, 215), (560, 230), (515, 265), (500, 250)],
             kind="rigid", anchor=(505, 215), z="front", over=[])]),
    "kayle": dict(neck=(662, 312), props=[
        dict(poly=[(395, 610), (480, 640), (470, 700), (430, 720), (70, 1290), (20, 1290), (330, 760), (360, 690)],
             kind="rigid", anchor=(440, 665), z="front", over=[[(400, 600), (483, 600), (483, 683), (400, 683)]]),
        dict(person=[(600, 140), (640, 128), (700, 120), (720, 180), (730, 265), (745, 295), (790, 290), (830, 320),
                     (860, 380), (850, 450), (845, 520), (860, 600), (885, 650), (885, 720), (860, 760), (900, 900),
                     (940, 1100), (970, 1291), (760, 1291), (700, 1180), (620, 1291), (480, 1291), (470, 1100),
                     (450, 950), (430, 850), (420, 720), (380, 620), (395, 560), (400, 480), (430, 420), (480, 350),
                     (530, 300), (565, 250), (585, 200)],
             kind="rigid", anchor=(655, 420), z="back", over=[])]),
}


def poly_mask(shape, pts):
    img = Image.new("L", (shape[1], shape[0]), 0)
    ImageDraw.Draw(img).polygon([tuple(p) for p in pts], fill=1)
    return np.asarray(img, bool)


def inpaint(a, hole, iters=200):
    """hole squares take the mean of their filled neighbours, ring by ring inward (premultiplied, alpha kept 255)."""
    out = a.astype(np.float32).copy()
    known = (a[..., 3] > 0) & ~hole
    todo = hole.copy()
    k = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]], np.float32)
    for _ in range(iters):
        if not todo.any():
            break
        w = ndimage.convolve(known.astype(np.float32), k, mode="constant")
        ring = todo & (w > 0)
        if not ring.any():
            break
        for c in range(3):
            s = ndimage.convolve(np.where(known, out[..., c], 0), k, mode="constant")
            out[..., c][ring] = s[ring] / w[ring]
        out[..., 3][ring] = 255
        known |= ring
        todo &= ~ring
    return out.round().astype(np.uint8)


def sample(img, xs, ys):
    """Bilinear sample of a premultiplied RGBA image at float coordinates (pixel centres at +0.5)."""
    a = img.astype(np.float32)
    al = a[..., 3:4] / 255
    pm = np.concatenate([a[..., :3] * al, a[..., 3:4]], -1)
    out = np.stack([ndimage.map_coordinates(pm[..., c], [ys - 0.5, xs - 0.5], order=1, mode="constant") for c in range(4)], -1)
    alpha = out[..., 3]
    rgb = out[..., :3] / np.maximum(alpha[..., None] / 255, 1e-3)
    res = np.zeros(out.shape, np.uint8)
    m = alpha >= 128
    res[m, :3] = np.clip(rgb[m], 0, 255)
    res[m, 3] = 255
    return res


def chibi(hero, spec, head=HEAD, short=SHORT, wide=WIDE, band=BAND):
    head, short, wide = spec.get("head", head), spec.get("short", short), spec.get("wide", wide)
    pic = R.load_picture(hero)
    H, W = pic.shape[:2]
    op = pic[..., 3] > 0
    ys, xs = np.nonzero(op[-max(4, H // 40):])
    px = (xs.min() + xs.max() + 1) / 2                     # the soles' middle
    G = float(H)
    nx, ny = spec["neck"]
    tb = lambda x, y: (px + (x - px) * wide, G - (G - y) * short)
    nox, noy = tb(nx, ny)
    props, over_all = [], np.zeros_like(op)
    body = pic.copy()
    removed = np.zeros_like(op)
    for p in spec["props"]:
        if "person" in p:
            m = op & ~poly_mask(op.shape, p["person"])
            for q in props:
                m &= ~q[0]
        else:
            m = poly_mask(op.shape, p["poly"]) & op
        over = np.zeros_like(op)
        for o in p.get("over", []):
            over |= poly_mask(op.shape, o)
        m &= ~over
        over_all |= over & op
        img = np.zeros_like(pic)
        img[m] = pic[m]
        props.append((m, img, p))
        removed |= m
    body[removed] = 0
    # the body the props hid: inside its own outline closed over the prop's width
    bop = body[..., 3] > 0
    closed = ndimage.binary_closing(bop, structure=np.ones((9, 9)), iterations=4)
    hole = removed & (closed | ndimage.binary_fill_holes(bop)) & ~bop
    body = inpaint(body, hole)
    # output canvas: wide enough for the wider body and the props
    padl, padr, padt = int(W * 0.25), int(W * 0.25), int(H * 0.2)
    OW, OH = W + padl + padr, H + padt
    oy, ox = np.mgrid[0:OH, 0:OW].astype(np.float32)
    ox_s, oy_s = ox + 0.5 - padl, oy + 0.5 - padt              # output coords in the picture's frame
    # inverse maps
    bx, by = px + (ox_s - px) / wide, G - (G - oy_s) / short
    hx, hy = nx + (ox_s - nox) / head, ny + (oy_s - noy) / head
    t = np.clip((oy_s - (noy - band / 2)) / band, 0, 1)      # 0 above the band (head), 1 below (body)
    sx, sy = hx * (1 - t) + bx * t, hy * (1 - t) + by * t
    warped = sample(body, sx, sy)
    out = np.zeros_like(warped)
    back = [q for q in props if q[2].get("z") == "back"]
    front = [q for q in props if q[2].get("z") != "back"]

    def place(q):
        m, img, p = q
        if p["kind"] == "body":
            return sample(img, bx, by)
        ax, ay = p["anchor"]
        tx, ty = tb(ax, ay)
        sc = p.get("scale", 1.0)
        return sample(img, ax + (ox_s - tx) / sc, ay + (oy_s - ty) / sc)

    for q in back:
        w = place(q)
        out[w[..., 3] > 0] = w[w[..., 3] > 0]
    out[warped[..., 3] > 0] = warped[warped[..., 3] > 0]
    for q in front:
        w = place(q)
        out[w[..., 3] > 0] = w[w[..., 3] > 0]
    if over_all.any():
        oimg = np.zeros_like(body)
        oimg[over_all] = body[over_all]
        ow = sample(oimg, sx, sy)
        out[ow[..., 3] > 0] = ow[ow[..., 3] > 0]
    ys, xs = np.nonzero(out[..., 3] > 0)
    y0, x0 = ys.min(), xs.min()
    ht = HEAD_TOP.get(hero, 0)
    meta = {"head_top": float(noy - (ny - ht) * head + padt - y0), "foot_x": float(px + padl - x0),
            "ground": float(G + padt - y0)}
    return out[y0:ys.max() + 1, x0:xs.max() + 1], meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hero", action="append")
    ap.add_argument("--preview")
    a = ap.parse_args()
    for hero in a.hero or list(SPECS):
        c, meta = chibi(hero, SPECS[hero])
        path = os.path.join(R.ROOT, "assets", "source", hero, "hd", "chibi.png")
        Image.fromarray(c).save(R.lp(path))
        with open(R.lp(path[:-4] + ".json"), "w", encoding="utf-8") as f:
            json.dump(meta, f)
        print(hero, c.shape[1], "x", c.shape[0])
        if a.preview:
            os.makedirs(a.preview, exist_ok=True)
            src = R.load_picture(hero)
            h = max(src.shape[0], c.shape[0])
            both = Image.new("RGBA", (src.shape[1] + c.shape[1] + 40, h), (96, 112, 96, 255))
            both.alpha_composite(Image.fromarray(src), (0, h - src.shape[0]))
            both.alpha_composite(Image.fromarray(c), (src.shape[1] + 40, h - c.shape[0]))
            both = both.resize((both.width // 3, both.height // 3), Image.LANCZOS)
            both.convert("RGB").save(os.path.join(a.preview, f"chibi_{hero}.png"))


if __name__ == "__main__":
    main()
