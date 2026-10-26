#!/usr/bin/env python3
"""Skarner's effects from the Gemini pictures (the user, 2026-10-26: 「gemini做的啊 你处理一下不就行了吗」「你拿着改一下不就行了吗
不对的地方」): every picture cleaned into game-size frames the import reads (pixel_1x + manifest.json, Codex's delivery shape).

    python tools/art/clean_skarner_fx.py [--review out.png]

The source: assets/source/skarner/gemini_fx/*.jpg (the user's Gemini run of assets/source/skarner/PROMPTS_FX.md, one
picture an effect, its frames side by side - p_quake's stacked - drawn at ~8x on black, a few on white or with grey
patches; JPEG, soft edges, glows). Per effect (SPECS):
  * the frames: the picture cut into equal cells (or the cells given);
  * the background: a black picture keeps what is brighter than BG_DARK; a white / patched one keeps the coloured
    squares (saturation) and, for a solid thing, its near-black outline next to them;
  * the size: every frame at ONE scale (the effect's widest / tallest drawn frame fits the pack's cell less a margin;
    `stretch` fits width and height apart, for a ground ring Gemini drew round), each square of the game cell the
    majority of its block (drawn if KEEP of it is drawn), its colour the block's median;
  * the colours: snapped to the pack's ramps (CRYSTAL, CORE, EARTH, STONE of pack_skarner_fx.py), squares too dark to
    read (glow fringes) dropped, a near-black outline kept only for the solid things (the boulders, the stingers);
  * symmetry: the half `half` (Gemini's pictures are near-symmetric: the half with the cleaner drawing) mirrored onto the
    other, left-right for every picture the game does not turn, top-bottom for the two projectiles;
  * stray single squares dropped.
Writes assets/source/skarner/gemini_fx/clean/pixel_1x/skarner_fx_<name>.png and manifest.json.
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
import pack_skarner_fx as PF  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "skarner", "gemini_fx")
OUT = os.path.join(SRC, "clean")
BG_DARK = 46          # a black picture's background and its glow fringes: max(r, g, b) at or under this
KEEP = 0.3            # a game square is drawn when this share of its block is drawn (thin shards survive)
EXT_Q = 98.0          # the extent read at this percentile of the drawn pixels (JPEG specks never set the scale)
OUTLINE = (20, 18, 24)

# name -> (picture, frames, cell (w, h) in game px, options)
SPECS = {
    "a_hit": ("5eauv55eauv55eau.jpg", 3, (14, 14), dict(ext_frames=(1,))),
    "p_quake": ("5eauv55eauv55eau_1.jpg", 4, (18, 8), dict(stack=True, stretch=True)),
    "p_burst": ("5eauv55eauv55eau_2.jpg", 5, (24, 24), {}),
    "q_hit": ("5eauv55eauv55eau_3.jpg", 4, (20, 18), {}),
    "q_land": ("5eauv55eauv55eau_4.jpg", 5, (36, 18), dict(stretch=True, ellipse=True)),
    "q_rock": ("5eauv55eauv55eau_5.jpg", 2, (20, 14), dict(sym="tb", half="top", solid=True)),
    "q_held": ("5eauv55eauv55eau_6.jpg", 4, (64, 56), dict(half="left", solid=True, box=(34, 22), at="top")),
    "slow": ("5eauv55eauv55eau_7.jpg", 4, (16, 8), dict(stretch=True)),
    "w_quake": ("5eauv55eauv55eau_8.jpg", 6, (84, 28), dict(stretch=True, ellipse=True, ring=(3, 4), drop=(5,))),
    "w_shield": ("5eauv55eauv55eau_9.jpg", 6, (54, 42), dict(bg="white", solid=True, stretch=True)),
    "w_hit": ("g5pu7lg5pu7lg5pu.jpg", 4, (18, 18), {}),
    "e_hit": ("g5pu7lg5pu7lg5pu_1.jpg", 4, (22, 20), dict(ellipse=True)),
    "e_slam": ("g5pu7lg5pu7lg5pu_2.jpg", 5, (28, 30), dict(ellipse=True)),
    "stun": ("g5pu7lg5pu7lg5pu_3.jpg", 4, (16, 8), dict(bg="white", stretch=True, recolor_outline=True)),
    "r_spike": ("g5pu7lg5pu7lg5pu_4.jpg", 3, (44, 15), dict(compose="spike")),
    "r_hit": ("g5pu7lg5pu7lg5pu_5.jpg", 5, (26, 30), {}),
    "r_held": ("g5pu7lg5pu7lg5pu_6.jpg", 6, (26, 34), {}),
    "r_haste": ("g5pu7lg5pu7lg5pu_7.jpg", 4, (50, 12), dict(stretch=True)),
}


def palette():
    cols = []
    for ramp in (PF.CRYSTAL, PF.CORE, PF.EARTH, PF.STONE):
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


def drawn_mask(a, opt):
    """Which source pixels are the effect (not the background)."""
    mx, mn = a.max(-1), a.min(-1)
    sat = (mx - mn) / np.maximum(mx, 1)
    if opt.get("bg") == "white":
        coloured = (sat > 0.28) & (mx > 70)
        dark = mx < 70
        m = coloured.copy()
        if opt.get("solid") or opt.get("recolor_outline"):   # its near-black outline: dark pixels next to the colour
            from numpy.lib.stride_tricks import sliding_window_view as W
            r = 6
            pad = np.pad(coloured, r)
            near = W(pad, (2 * r + 1, 2 * r + 1)).any(axis=(-1, -2))
            m |= dark & near
        return m
    return mx > BG_DARK


def frames_of(img, n, stack):
    H, W_ = img.shape[:2]
    if stack:
        return [img[k * H // n:(k + 1) * H // n] for k in range(n)]
    return [img[:, k * W_ // n:(k + 1) * W_ // n] for k in range(n)]


def clean(name):
    pic, n, (cw, ch), opt = SPECS[name]
    if opt.get("compose") == "spike":
        return compose_spike(cw, ch, n)
    a = np.asarray(Image.open(os.path.join(SRC, pic)).convert("RGB")).astype(float)
    fr = frames_of(a, n, opt.get("stack"))
    masks = [drawn_mask(f, opt) for f in fr]
    # one scale for every frame: the drawn extent about each cell's middle
    masks = [lines_off(m) for m in masks]
    # the scale from the bright drawing only (faint dust and JPEG specks never set it)
    bright = [m & (f.max(-1) > 90) for f, m in zip(fr, masks)]
    if "ext_frames" in opt:   # the scale from these frames (a burst whose last frame is a far, faint ring)
        bright = [b if k in opt["ext_frames"] else np.zeros_like(b) for k, b in enumerate(bright)]
    dx = np.concatenate([np.abs(np.nonzero(b)[1] - b.shape[1] / 2) for b in bright if b.any()])
    dy = np.concatenate([np.abs(np.nonzero(b)[0] - b.shape[0] / 2) for b in bright if b.any()])
    ext_x, ext_y = np.percentile(dx, EXT_Q), np.percentile(dy, EXT_Q)
    bw, bh = opt.get("box", (cw - 2, ch - 2))
    sx, sy = bw / (2 * ext_x), bh / (2 * ext_y)
    if not opt.get("stretch"):
        sx = sy = min(sx, sy)
    if opt.get("at") == "top":   # the boulder (the largest blob) sets the scale and the top; the sand falls below it
        y0_, y1_, x0_, x1_ = largest(masks[0])
        sx = sy = bw / (x1_ - x0_)
        top = y0_
        cxs = (x0_ + x1_) / 2
    out = []
    for f, m in zip(fr, masks):
        cell = np.zeros((ch, cw, 4), np.uint8)
        H, W_ = m.shape
        oy = 0 if opt.get("at") != "top" else 0
        for y in range(ch):
            for x in range(cw):
                # the source block of game square (x, y): about the cell's middle (or for `at` top, from the top)
                if opt.get("at") == "top":   # from the boulder's top, a square below the cell's top edge
                    y0 = (y - 1) / sy + top
                    y1 = y0 + 1 / sy
                else:
                    y0, y1 = H / 2 + (y - ch / 2) / sy, H / 2 + (y + 1 - ch / 2) / sy
                mid = cxs if opt.get("at") == "top" else W_ / 2
                x0, x1 = mid + (x - cw / 2) / sx, mid + (x + 1 - cw / 2) / sx
                ys, ye = int(max(0, np.floor(y0))), int(min(H, np.ceil(y1)))
                xs, xe = int(max(0, np.floor(x0))), int(min(W_, np.ceil(x1)))
                if ye <= ys or xe <= xs:
                    continue
                bm = m[ys:ye, xs:xe]
                if bm.mean() < KEEP:
                    continue
                cell[y, x, :3] = np.median(f[ys:ye, xs:xe][bm], axis=0)
                cell[y, x, 3] = 255
        del oy
        op = cell[..., 3] > 0
        rgb = cell[..., :3].astype(float)
        dark = rgb.max(-1) < 62
        if opt.get("solid"):   # the outline: dark squares touching the drawn colour (a dark trail is dropped)
            col_ = op & ~dark
            pc = np.pad(col_, 1)
            touch = pc[:-2, 1:-1] | pc[2:, 1:-1] | pc[1:-1, :-2] | pc[1:-1, 2:]
            keep_dark = dark & op & touch
            cell[dark & op & ~touch] = 0
            col = op & ~dark
            cell[col, :3] = snap(rgb[col]).astype(np.uint8)
            cell[keep_dark, :3] = OUTLINE
        elif opt.get("recolor_outline"):   # a black ring Gemini drew: in the crystal's deepest teal (no black outlines)
            col = op & ~dark
            cell[col, :3] = snap(rgb[col]).astype(np.uint8)
            cell[op & dark, :3] = (0x0B, 0x54, 0x68)
        else:
            cell[dark] = 0
            col = cell[..., 3] > 0
            cell[col, :3] = snap(rgb[col]).astype(np.uint8)
        if opt.get("ellipse"):   # Gemini's dust cut square at its cell's edges: kept inside the cell's ellipse
            yy, xx = np.mgrid[0:ch, 0:cw]
            e = ((xx + 0.5 - cw / 2) / (cw / 2)) ** 2 + ((yy + 0.5 - ch / 2) / (ch / 2)) ** 2
            cell[e > 1.0] = 0
        out.append(symmetric(despeckle(cell), opt))
    out = [c for k, c in enumerate(out) if k not in opt.get("drop", ()) and (c[..., 3] > 0).sum() >= 4]
    for k in opt.get("ring", ()):   # a filled dust block made a ring: only the ellipse's outer band kept
        c = out[k]
        yy, xx = np.mgrid[0:ch, 0:cw]
        e = ((xx + 0.5 - cw / 2) / (cw / 2)) ** 2 + ((yy + 0.5 - ch / 2) / (ch / 2)) ** 2
        c[e < opt.get("ring_in", 0.45)] = 0
    return out


SPIKE_SRC = (1590, 255, 1952, 455)   # the middle stinger of Gemini's first r_spike frame (source pixels)
SPIKE_W = 12                          # its length at game size


def stinger():
    """Gemini's crystal stinger cut out (its white and black background off), at game size, outlined."""
    a = np.asarray(Image.open(os.path.join(SRC, SPECS["r_spike"][0])).convert("RGB")).astype(float)
    x0, y0, x1, y1 = SPIKE_SRC
    f = a[y0:y1, x0:x1]
    m = drawn_mask(f, dict(bg="white", solid=True))
    ys, xs = np.nonzero(m & (f.max(-1) > 70))
    f, m = f[ys.min():ys.max() + 1, xs.min():xs.max() + 1], m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    k = SPIKE_W / f.shape[1]
    w, h = SPIKE_W, max(3, int(round(f.shape[0] * k)))
    h += 1 - h % 2
    c = np.zeros((h, w, 4), np.uint8)
    for y in range(h):
        for x in range(w):
            ys_, ye = int(y / k), max(int(y / k) + 1, int((y + 1) / k))
            xs_, xe = int(x / k), max(int(x / k) + 1, int((x + 1) / k))
            bm = m[ys_:ye, xs_:xe]
            if bm.size and bm.mean() >= 0.4:
                px = f[ys_:ye, xs_:xe][bm]
                c[y, x, :3] = np.median(px, axis=0)
                c[y, x, 3] = 255
    op = c[..., 3] > 0
    dark = c[..., :3].max(-1) < 62
    col = op & ~dark
    c[col, :3] = snap(c[col, :3].astype(float)).astype(np.uint8)
    c[op & dark, :3] = OUTLINE
    c = symmetric(c, dict(sym="tb", half="top"))
    # a 1-square near-black outline round it (it is a solid thing)
    o = c[..., 3] > 0
    po = np.pad(o, 1)
    ring = ~o & (po[:-2, 1:-1] | po[2:, 1:-1] | po[1:-1, :-2] | po[1:-1, 2:])
    c[ring] = OUTLINE + (255,)
    return c


def compose_spike(cw, ch, n):
    """Impale's lash: three of Gemini's stingers as an arrowhead (one in front, two behind above and below) and
    orange / teal speed lines behind them, the streaks' lengths changing frame to frame; symmetric top to bottom."""
    st = stinger()
    sh, sw = st.shape[:2]
    mid = ch // 2
    orange = [tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)) for v in PF.CORE.split(", ")]
    teal = [tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)) for v in PF.CRYSTAL.split(", ")]
    lines = [(0, orange[2], 26), (2, teal[2], 22), (4, orange[1], 16), (6, teal[3], 12)]
    out = []
    for k in range(n):
        c = np.zeros((ch, cw, 4), np.uint8)
        for dy, col, L in lines:
            L = L - 3 * ((k + dy // 2) % 3)
            x1 = cw - sw - 6
            for sgn in ((1,) if dy == 0 else (1, -1)):
                y = mid + sgn * dy
                if 0 <= y < ch:
                    c[y, max(0, x1 - L):x1, :3] = col
                    c[y, max(0, x1 - L):x1, 3] = 255
        for x0, yc in ((cw - sw - 8, mid - 4), (cw - sw - 8, mid + 4), (cw - sw, mid)):
            y0 = yc - sh // 2
            for y in range(sh):
                for x in range(sw):
                    if st[y, x, 3] and 0 <= y0 + y < ch and 0 <= x0 + x < cw:
                        c[y0 + y, x0 + x] = st[y, x]
        out.append(c)
    return out


def lines_off(m):
    """Gemini's thin frame separators (a column at most 4 px wide drawn nearly the whole height) taken out."""
    m = m.copy()
    full = m.mean(0) > 0.85
    x = 0
    while x < m.shape[1]:
        if full[x]:
            e = x
            while e < m.shape[1] and full[e]:
                e += 1
            if e - x <= 4:
                m[:, max(0, x - 2):min(m.shape[1], e + 2)] = False
            x = e
        else:
            x += 1
    return m


def largest(m):
    """The largest 4-connected blob of a mask (the boulder, not the sand under it), on a 4x-coarser grid."""
    c = m[::4, ::4]
    seen = np.zeros_like(c, bool)
    best = []
    for y0, x0 in zip(*np.nonzero(c)):
        if seen[y0, x0]:
            continue
        stack, blob = [(y0, x0)], []
        seen[y0, x0] = True
        while stack:
            y, x = stack.pop()
            blob.append((y, x))
            for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= yy < c.shape[0] and 0 <= xx < c.shape[1] and c[yy, xx] and not seen[yy, xx]:
                    seen[yy, xx] = True
                    stack.append((yy, xx))
        if len(blob) > len(best):
            best = blob
    ys, xs = np.array(best).T * 4
    return ys.min(), ys.max() + 4, xs.min(), xs.max() + 4


def despeckle(c):
    op = c[..., 3] > 0
    p = np.pad(op, 1)
    nb = p[:-2, 1:-1].astype(int) + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]
    c = c.copy()
    c[op & (nb == 0)] = 0
    return c


def symmetric(c, opt):
    c = c.copy()
    if opt.get("sym") == "tb":
        h = c.shape[0]
        top = c[: (h + 1) // 2]
        if opt.get("half", "top") == "top":
            c[h - top.shape[0]:] = top[::-1]
        else:
            c[: (h + 1) // 2] = c[h - (h + 1) // 2:][::-1]
        return c
    w = c.shape[1]
    half = opt.get("half")
    if half is None:   # the half with more drawn squares (the fuller drawing)
        l, r = (c[:, : w // 2, 3] > 0).sum(), (c[:, (w + 1) // 2:, 3] > 0).sum()
        half = "left" if l >= r else "right"
    if half == "left":
        c[:, w - (w + 1) // 2:] = c[:, : (w + 1) // 2][:, ::-1]
    else:
        c[:, : (w + 1) // 2] = c[:, w - (w + 1) // 2:][:, ::-1]
    return c


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
        strip = np.concatenate(cs, axis=1)
        f = f"skarner_fx_{name}.png"
        Image.fromarray(strip).save(os.path.join(OUT, "pixel_1x", f))
        man[f] = {"file": f, "frames": len(cs), "cell_1x": [cw, ch],
                  "symmetry": "top-bottom" if SPECS[name][3].get("sym") == "tb" else "left-right"}
        rows.append((name, cs))
        print(name, len(cs), "x", cw, ch)
    json.dump(sorted(man.values(), key=lambda e: e["file"]), open(man_path, "w", encoding="utf-8"), indent=1)
    if a.review:
        Z = 6
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
