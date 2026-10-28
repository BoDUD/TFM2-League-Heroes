#!/usr/bin/env python3
"""The Ancient Krug's effects from the user's Gemini pictures (2026-10-28, 「gemini生成的特效这是 你要处理一下」): every
picture cleaned into game-size frames the import reads (pixel_1x + manifest.json, Codex's delivery shape) -
clean_skarner_fx.py's way.

    python tools/art/clean_krug_fx.py [--review out.png] [--only a_hit,q_hit]

The source: assets/source/krug/gemini_fx/00-17.jpg, the user's Gemini run of assets/source/krug/PROMPTS_FX.md in the
pack's order but the icons first (00 a_hit, 01-03 the ult / skill2 / skill icons, 04 p_mini, 05 p_up, 06 p_burst, 07
r_rock_hit, 08 r_rocks, 09 r_hit, 10 r_slam, 11 r_mark, 12 r_jump, 13 e_taunt, 14 q_shield, 15 e_cast, 16 q_hit; 17
drew his whole body inside a stone shell - the body cannot ride over his frames, so e_shell is made from q_shield's
own ring instead). Drawn at ~8x on black, a dark checkerboard, flat grey or white, a few with frame separators and
p_mini / r_mark / r_slam laid out as grids; JPEG, soft edges, glows. Per effect (SPECS):
  * the frames: the picture cut into equal cells (`grid` (cols, rows) for the grid layouts, `pick` the cells kept in
    order: r_mark drew ten rings, the left column dim to bright and the right one brighter, six kept);
  * the background: each frame's own (the median of its edge pixels: black, the checker's greys, the flat grey, white),
    the effect = what differs from it by more than BG_DIFF (or, for the dark checker, is brighter than it);
  * the size: every frame at ONE scale (the effect's widest / tallest bright frame fits the pack's cell less a margin;
    `stretch` fits width and height apart, for a ground ring Gemini drew round), each square of the game cell the
    majority of its block, its colour the block's median; `top` lays the drawing in the cell's top `box` rows (the
    taunt mark over a unit's head);
  * the colours: snapped to the pack's ramps (LAVA, SAND, STONE, DUST of pack_krug_fx.py), squares too dark to read
    (glow fringes) dropped, a near-black outline kept only for the solid things (the rocks);
  * symmetry: the fuller half mirrored onto the other (every picture is left-right symmetric: the client never mirrors
    an effect picture); stray single squares dropped.
The three icons: the 2000 px tile (a white JPEG margin cut off) brought to 64 x 64 (LANCZOS).
Writes assets/source/krug/gemini_fx/clean/pixel_1x/krug_fx_<name>.png, krug_icon_<name>.png and manifest.json.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_krug_fx as PF  # noqa: E402
from clean_skarner_fx import despeckle, lines_off, symmetric  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "krug", "gemini_fx")
OUT = os.path.join(SRC, "clean")
BG_DIFF = 42          # a pixel this far (max channel) from its frame's background is the effect
KEEP = 0.3            # a game square is drawn when this share of its block is drawn
EXT_Q = 98.0          # the extent read at this percentile of the bright pixels (JPEG specks never set the scale)
EDGE = 7              # edge_off: a part this near a frame's side was cut there
DARK = 62             # a square darker than this (max channel) is a glow fringe (dropped) or, on a solid, the outline
OUTLINE = (24, 18, 20)

# name -> (picture, frames, cell (w, h) in game px, options)
SPECS = {
    "a_hit": ("00.jpg", 4, (16, 16), {}),
    "q_shield": ("14.jpg", 6, (48, 44), dict(stretch=True, solid=True)),
    "q_hit": ("16.jpg", 5, (28, 24), {}),
    "e_cast": ("15.jpg", 5, (50, 20), dict(stretch=True, ellipse=True)),
    "e_taunt": ("13.jpg", 6, (18, 44), dict(crop=(0, 0, 2000, 330), top=True, box=(16, 11), solid=True)),
    "r_jump": ("12.jpg", 5, (40, 30), dict(solid=True)),
    "r_mark": ("11.jpg", 6, (36, 14), dict(grid=(2, 5), pick=[(0, 0), (0, 1), (0, 2), (0, 4), (1, 2), (1, 4)],
                                          stretch=True, ellipse=True)),
    "r_slam": ("10.jpg", 8, (96, 34), dict(grid=(4, 2), stretch=True, ellipse=True, solid=True)),
    "r_hit": ("09.jpg", 4, (20, 24), {}),
    "r_rocks": ("08.jpg", 8, (80, 60), dict(solid=True, edge_off=True)),
    "r_rock_hit": ("07.jpg", 4, (18, 30), dict(solid=True)),
    "p_burst": ("06.jpg", 6, (52, 46), dict(solid=True, ellipse=True, drop=(4,))),
    "p_up": ("05.jpg", 6, (44, 40), dict(solid=True)),
    "p_mini": ("04.jpg", 6, (34, 10), dict(grid=(2, 3), stretch=True, ellipse=True)),
}
# e_shell (the shell held, a 6-frame loop): q_shield's set ring (frames 2 and 3: the bright and the glowing one) in turn,
# only its outer band, the glow dimmed a step
SHELL_FROM = ("q_shield", (2, 3, 2, 3, 2, 3))
ICONS = {"ult": "01.jpg", "skill2": "02.jpg", "skill": "03.jpg"}


def palette():
    cols = []
    for ramp in (PF.LAVA, PF.SAND, PF.STONE, PF.DUST):
        cols += [tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in ramp.split(", ")]
    return np.array(cols, float)


PAL = palette()


def lab(rgb):
    """A cheap perceptual space (weights on the channels and on the brightness) for the nearest ramp colour."""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    y = 0.299 * r + 0.587 * g + 0.114 * b
    return np.stack([y * 1.6, (r - y) * 1.0, (b - y) * 1.0], -1)


def snap(rgb):
    d = ((lab(rgb)[:, None, :] - lab(PAL)[None, :, :]) ** 2).sum(-1)
    return PAL[d.argmin(1)]


def drawn_mask(f):
    """The effect in one frame: what differs from the frame's own background (its edge pixels' median)."""
    edge = np.concatenate([f[0], f[-1], f[:, 0], f[:, -1]])
    bg = np.median(edge, axis=0)
    diff = np.abs(f - bg).max(-1)
    m = diff > BG_DIFF
    if bg.max() < 60:   # a dark background (black or the checker's greys): only what is brighter than it
        m &= f.max(-1) > bg.max() + BG_DIFF / 2
    return m


def frames_of(img, n, opt):
    H, W_ = img.shape[:2]
    if "grid" in opt:
        c, r = opt["grid"]
        cells = opt.get("pick") or [(i, j) for j in range(r) for i in range(c)]
        return [img[j * H // r:(j + 1) * H // r, i * W_ // c:(i + 1) * W_ // c] for i, j in cells][:n]
    return [img[:, k * W_ // n:(k + 1) * W_ // n] for k in range(n)]


def clean(name):
    pic, n, (cw, ch), opt = SPECS[name]
    im = Image.open(os.path.join(SRC, pic)).convert("RGB")
    if "crop" in opt:
        im = im.crop(opt["crop"])
    a = np.asarray(im).astype(float)
    fr = frames_of(a, n, opt)
    masks = [lines_off(drawn_mask(f)) for f in fr]
    bright = [m & (f.max(-1) > 90) for f, m in zip(fr, masks)]
    dx = np.concatenate([np.abs(np.nonzero(b)[1] - b.shape[1] / 2) for b in bright if b.any()])
    dy = np.concatenate([np.abs(np.nonzero(b)[0] - b.shape[0] / 2) for b in bright if b.any()])
    ext_x, ext_y = np.percentile(dx, EXT_Q), np.percentile(dy, EXT_Q)
    bw, bh = opt.get("box", (cw - 2, ch - 2))
    if opt.get("top"):   # the drawing's own box (all frames) fits `box`, laid at the cell's top
        ys = np.concatenate([np.nonzero(b)[0] for b in bright if b.any()])
        xs = np.concatenate([np.abs(np.nonzero(b)[1] - b.shape[1] / 2) for b in bright if b.any()])
        y_lo, y_hi = np.percentile(ys, 100 - EXT_Q), np.percentile(ys, EXT_Q)
        sx = sy = min(bw / (2 * np.percentile(xs, EXT_Q)), bh / (y_hi - y_lo))
    else:
        sx, sy = bw / (2 * ext_x), bh / (2 * ext_y)
        if not opt.get("stretch"):
            sx = sy = min(sx, sy)
    out = []
    for f, m in zip(fr, masks):
        cell = np.zeros((ch, cw, 4), np.uint8)
        H, W_ = m.shape
        for y in range(ch):
            for x in range(cw):
                if opt.get("top"):
                    y0 = y_lo + (y - 0.5) / sy
                else:
                    y0 = H / 2 + (y - ch / 2) / sy
                y1 = y0 + 1 / sy
                x0 = W_ / 2 + (x - cw / 2) / sx
                x1 = x0 + 1 / sx
                ys_, ye = int(max(0, np.floor(y0))), int(min(H, np.ceil(y1)))
                xs_, xe = int(max(0, np.floor(x0))), int(min(W_, np.ceil(x1)))
                if ye <= ys_ or xe <= xs_:
                    continue
                bm = m[ys_:ye, xs_:xe]
                if bm.mean() < KEEP:
                    continue
                cell[y, x, :3] = np.median(f[ys_:ye, xs_:xe][bm], axis=0)
                cell[y, x, 3] = 255
        op = cell[..., 3] > 0
        rgb = cell[..., :3].astype(float)
        dark = rgb.max(-1) < DARK
        if opt.get("solid"):   # the outline: dark squares touching the drawn colour (a dark trail is dropped)
            col_ = op & ~dark
            pc = np.pad(col_, 1)
            touch = pc[:-2, 1:-1] | pc[2:, 1:-1] | pc[1:-1, :-2] | pc[1:-1, 2:]
            keep_dark = dark & op & touch
            cell[dark & op & ~touch] = 0
            cell[col_, :3] = snap(rgb[col_]).astype(np.uint8)
            cell[keep_dark, :3] = OUTLINE
        else:
            cell[dark] = 0
            col = cell[..., 3] > 0
            cell[col, :3] = snap(rgb[col]).astype(np.uint8)
        if opt.get("ellipse"):   # dust cut square at the cell's edges: kept inside the cell's ellipse
            yy, xx = np.mgrid[0:ch, 0:cw]
            e = ((xx + 0.5 - cw / 2) / (cw / 2)) ** 2 + ((yy + 0.5 - ch / 2) / (ch / 2)) ** 2
            cell[e > 1.0] = 0
        if opt.get("edge_off"):   # rocks Gemini drew across a frame's edge (its frames overlap): the ones reaching within EDGE columns of it dropped
            from scipy import ndimage
            lb, k = ndimage.label(cell[..., 3] > 0, structure=np.ones((3, 3), bool))
            for j in set(lb[:, :EDGE].ravel()) | set(lb[:, -EDGE:].ravel()):
                ys, xs = np.nonzero(lb == j)
                if j and xs.max() - xs.min() < 16:   # a rock, not the wide ground dust
                    cell[lb == j] = 0
        out.append(symmetric(despeckle(cell), {}))
    return [c for k, c in enumerate(out) if k not in opt.get("drop", ()) and (c[..., 3] > 0).sum() >= 4]


def shell(rings):
    """e_shell from q_shield's set ring: its outer band (the inner 45% of the ellipse cleared), the lava a step dimmer."""
    src, order = SHELL_FROM
    lava = [tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in PF.LAVA.split(", ")]
    dim = {lava[k]: lava[min(k + 1, len(lava) - 1)] for k in range(len(lava))}
    out = []
    for j, k in enumerate(order):
        c = rings[k].copy()
        ch, cw = c.shape[:2]
        yy, xx = np.mgrid[0:ch, 0:cw]
        e = ((xx + 0.5 - cw / 2) / (cw / 2)) ** 2 + ((yy + 0.5 - ch / 2) / (ch / 2)) ** 2
        c[e < 0.55] = 0
        if j % 2:
            for y, x in zip(*np.nonzero(c[..., 3] > 0)):
                t = tuple(int(v) for v in c[y, x, :3])
                if t in dim:
                    c[y, x, :3] = dim[t]
        out.append(c)
    return out


def icon(pic):
    """A 2000 px icon tile -> 64 x 64 (LANCZOS from the tile, tft_violet's way: 32 squares of medians lost the fist and
    the eye)."""
    im = Image.open(os.path.join(SRC, pic)).convert("RGB")
    a = np.asarray(im)
    ys, xs = np.nonzero(a.max(-1) < 245)   # the tile, not a white margin the JPEG left at an edge
    im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).resize((64, 64), Image.LANCZOS)
    return np.asarray(im.convert("RGBA"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--only")
    a = ap.parse_args()
    os.makedirs(os.path.join(OUT, "pixel_1x"), exist_ok=True)
    names = a.only.split(",") if a.only else list(SPECS) + ["e_shell"]
    man_path = os.path.join(OUT, "manifest.json")
    man = {e["file"]: e for e in json.load(open(man_path, encoding="utf-8"))} if os.path.isfile(man_path) else {}
    rows, done = [], {}
    for name in names:
        if name == "e_shell":
            cs = shell(done.get("q_shield") or clean("q_shield"))
            cw, ch = SPECS["q_shield"][2]
        else:
            cs = clean(name)
            cw, ch = SPECS[name][2]
        done[name] = cs
        f = f"krug_fx_{name}.png"
        Image.fromarray(np.concatenate(cs, axis=1)).save(os.path.join(OUT, "pixel_1x", f))
        man[f] = {"file": f, "frames": len(cs), "cell_1x": [cw, ch], "symmetry": "left-right"}
        rows.append((name, cs))
        print(name, len(cs), "x", cw, ch)
    if not a.only:
        for name, pic in ICONS.items():
            Image.fromarray(icon(pic)).save(os.path.join(OUT, f"krug_icon_{name}.png"))
    json.dump(sorted(man.values(), key=lambda e: e["file"]), open(man_path, "w", encoding="utf-8"), indent=1)
    if a.review:
        Z = 5
        W = max(sum(c.shape[1] + 3 for c in cs) for _, cs in rows) * Z + 110
        H = sum(max(c.shape[0] for c in cs) * Z + 10 for _, cs in rows)
        sheet = Image.new("RGB", (W, H), (70, 78, 52))
        d = ImageDraw.Draw(sheet)
        y = 0
        for name, cs in rows:
            x = 110
            h = max(c.shape[0] for c in cs)
            for c in cs:
                d.rectangle([x - 1, y - 1, x + c.shape[1] * Z, y + c.shape[0] * Z], outline=(100, 110, 80))
                im = Image.fromarray(c).resize((c.shape[1] * Z, c.shape[0] * Z), Image.NEAREST)
                sheet.paste(im, (x, y), im)
                x += (c.shape[1] + 3) * Z
            d.text((4, y + 4), name, fill=(255, 255, 255))
            y += h * Z + 10
        sheet.save(a.review)
        print("review", a.review, sheet.size)


if __name__ == "__main__":
    main()
