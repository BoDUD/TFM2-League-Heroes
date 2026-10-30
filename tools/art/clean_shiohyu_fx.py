#!/usr/bin/env python3
"""Shi Oh Yu's effects from the user's Gemini pictures (2026-10-30, 「这是gemini做的特效 你导入后处理一下吧」): every
picture cleaned into game-size frames the import reads (pixel_1x + manifest.json, Codex's delivery shape) -
clean_krug_fx.py's way.

    python tools/art/clean_shiohyu_fx.py [--review out.png] [--only a_hit,q_hit]

The source: assets/source/shiohyu/gemini_fx/raw/g01-g16.jpg, the user's Gemini run of assets/source/shiohyu/PROMPTS_FX.md
in the pack's order (g01 a_hit, g02 q_hit, g03 e_slam, g04 e_hit, g05 e_slow, g06 r, g07 r_jade, g08 r1_hit, g09 r2_hit,
g10 r3_wave, g11 r3_hit, g12 p, g13 p_skin, g14-g16 the skill / skill2 / ult icons). Drawn at ~8x on black, white or
flat grey, some with thin separators (lines_off) or grey boxes round the cells (`boxes`: each frame's own inner box);
JPEG, soft edges, glows. Per effect (SPECS), clean_krug_fx's steps: the frames cut; each frame's background (the median
of its edge pixels, or `bg`) and what differs from it; e_slam and e_slow painted the ground under the effect as a flat disc
(`fill`: a tan disc; e_slow's is near-black on a white page, so its `bg` is the disc and the page is the `fill`) - the disc's colour is taken out, the cracks,
the ring and the rocks on it kept (a flat disc would cover the arena); one scale per effect (its widest / tallest bright
frame fits the cell less a margin; `stretch` fits width and height apart); each game square drawn when `keep` (KEEP;
lower for the thin claw marks and rings) of its block is,
its colour the block's median, snapped to the pack's ramps (JADE, GOLD, ROCK of pack_shiohyu_fx.py); squares too dark
to read dropped, a near-black outline kept only for the solid things (rocks, crystal spikes); symmetry: left-right for
every picture on a unit or the ground, top-bottom for r3_wave (the line the game turns with the cast); stray single
squares dropped.
The three icons: the 2000 px tile (cut to its frame) brought to 64 x 64 (LANCZOS).
Writes assets/source/shiohyu/gemini_fx/clean/pixel_1x/shiohyu_fx_<name>.png, shiohyu_icon_<name>.png and manifest.json.
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
import pack_shiohyu_fx as PF  # noqa: E402
from clean_skarner_fx import despeckle, lines_off, symmetric  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "shiohyu", "gemini_fx")
RAW = os.path.join(SRC, "raw")
OUT = os.path.join(SRC, "clean")
BG_DIFF = 42          # a pixel this far (max channel) from its frame's background is the effect
KEEP = 0.3            # a game square is drawn when this share of its block is drawn
EXT_Q = 98.0          # the extent read at this percentile of the bright pixels (JPEG specks never set the scale)
DARK = 62             # a square darker than this (max channel) is a glow fringe (dropped) or, on a solid, the outline
FILL_TOL = 18         # a pixel this close (max channel) to a painted ground disc's colour is the disc
OUTLINE = (20, 26, 24)


def cells_of(x0, x1s, y0, y1, pad=14):
    """Frame boxes between grey cell borders: (x start, x end) pairs, one row."""
    return [(a + pad, y0 + pad, b - pad, y1 - pad) for a, b in x1s]


# name -> (picture, frames, cell (w, h) in game px, options)
SPECS = {
    "a_hit": ("g01.jpg", 4, (16, 16), dict(keep=0.12)),
    "q_hit": ("g02.jpg", 3, (12, 12), dict(keep=0.12, boxes=cells_of(0, [(44, 906), (939, 1812), (1845, 2718)], 360, 1187))),
    "e_slam": ("g03.jpg", 6, (52, 22), dict(stretch=True, ellipse=True, solid=True, fill=[(98, 94, 78)])),
    "e_hit": ("g04.jpg", 4, (18, 14), dict(solid=True)),
    "e_slow": ("g05.jpg", 6, (20, 8), dict(stretch=True, ellipse=True, keep=0.15, bg=(2, 4, 3), fill=[(253, 254, 253)])),
    "r": ("g06.jpg", 6, (44, 52), {}),
    "r_jade": ("g07.jpg", 6, (40, 50), {}),
    "r1_hit": ("g08.jpg", 5, (22, 22), dict(boxes=cells_of(0, [(18, 820), (838, 1645), (1658, 2471), (2481, 3291),
                                                              (3309, 4109)], 13, 1024))),
    "r2_hit": ("g09.jpg", 5, (20, 24), {}),
    "r3_wave": ("g10.jpg", 6, (92, 24), dict(stretch=True, sym="tb")),
    "r3_hit": ("g11.jpg", 4, (18, 18), dict(solid=True, boxes=cells_of(0, [(0, 1023), (1035, 2059), (2071, 3094),
                                                                          (3106, 4128)], 0, 1024))),
    "p": ("g12.jpg", 5, (40, 50), dict(solid=True)),
    "p_skin": ("g13.jpg", 6, (38, 48), dict(solid=True)),
}
ICONS = {"skill": ("g14.jpg", None), "skill2": ("g15.jpg", None), "ult": ("g16.jpg", (152, 152, 1896, 1896))}


def palette():
    cols = []
    for ramp in (PF.JADE, PF.GOLD, PF.ROCK):
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


def drawn_mask(f, opt):
    """The effect in one frame: what differs from the frame's own background (its edge pixels' median), less a painted
    ground disc."""
    edge = np.concatenate([f[0], f[-1], f[:, 0], f[:, -1]])
    bg = np.array(opt["bg"], float) if "bg" in opt else np.median(edge, axis=0)
    m = np.abs(f - bg).max(-1) > BG_DIFF
    if bg.max() < 60:   # a dark background: only what is brighter than it
        m &= f.max(-1) > bg.max() + BG_DIFF / 2
    for c in opt.get("fill", ()):
        m &= np.abs(f - np.array(c, float)).max(-1) > FILL_TOL
    return m


def frames_of(img, n, opt):
    if "boxes" in opt:
        return [img[y0:y1, x0:x1] for x0, y0, x1, y1 in opt["boxes"]][:n]
    W_ = img.shape[1]
    return [img[:, k * W_ // n:(k + 1) * W_ // n] for k in range(n)]


def clean(name):
    pic, n, (cw, ch), opt = SPECS[name]
    a = np.asarray(Image.open(os.path.join(RAW, pic)).convert("RGB")).astype(float)
    fr = frames_of(a, n, opt)
    masks = [lines_off(drawn_mask(f, opt)) for f in fr]
    bright = [m & (f.max(-1) > 90) for f, m in zip(fr, masks)]
    dx = np.concatenate([np.abs(np.nonzero(b)[1] - b.shape[1] / 2) for b in bright if b.any()])
    dy = np.concatenate([np.abs(np.nonzero(b)[0] - b.shape[0] / 2) for b in bright if b.any()])
    ext_x, ext_y = np.percentile(dx, EXT_Q), np.percentile(dy, EXT_Q)
    bw, bh = cw - 2, ch - 2
    sx, sy = bw / (2 * ext_x), bh / (2 * ext_y)
    if not opt.get("stretch"):
        sx = sy = min(sx, sy)
    out = []
    for f, m in zip(fr, masks):
        cell = np.zeros((ch, cw, 4), np.uint8)
        H, W_ = m.shape
        for y in range(ch):
            for x in range(cw):
                y0 = H / 2 + (y - ch / 2) / sy
                x0 = W_ / 2 + (x - cw / 2) / sx
                ys_, ye = int(max(0, np.floor(y0))), int(min(H, np.ceil(y0 + 1 / sy)))
                xs_, xe = int(max(0, np.floor(x0))), int(min(W_, np.ceil(x0 + 1 / sx)))
                if ye <= ys_ or xe <= xs_:
                    continue
                bm = m[ys_:ye, xs_:xe]
                if bm.mean() < opt.get("keep", KEEP):
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
        out.append(symmetric(despeckle(cell), {"sym": opt.get("sym")}))
    return [c for c in out if (c[..., 3] > 0).sum() >= 4]


def icon(pic, box):
    """A 2000 px icon tile -> 64 x 64 (LANCZOS from the tile, tft_violet's way)."""
    im = Image.open(os.path.join(RAW, pic)).convert("RGB")
    if box:
        im = im.crop(box)
    return np.asarray(im.resize((64, 64), Image.LANCZOS).convert("RGBA"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--only")
    a = ap.parse_args()
    os.makedirs(os.path.join(OUT, "pixel_1x"), exist_ok=True)
    names = a.only.split(",") if a.only else list(SPECS)
    man_path = os.path.join(OUT, "manifest.json")
    man = {e["file"]: e for e in json.load(open(man_path, encoding="utf-8"))} if os.path.isfile(man_path) else {}
    rows = []
    for name in names:
        cs = clean(name)
        cw, ch = SPECS[name][2]
        f = f"shiohyu_fx_{name}.png"
        Image.fromarray(np.concatenate(cs, axis=1)).save(os.path.join(OUT, "pixel_1x", f))
        man[f] = {"file": f, "frames": len(cs), "cell_1x": [cw, ch],
                  "symmetry": "top-bottom" if SPECS[name][3].get("sym") == "tb" else "left-right"}
        rows.append((name, cs))
        print(name, len(cs), "x", cw, ch)
    if not a.only:
        for name, (pic, box) in ICONS.items():
            Image.fromarray(icon(pic, box)).save(os.path.join(OUT, f"shiohyu_icon_{name}.png"))
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
