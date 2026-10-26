#!/usr/bin/env python3
"""Zaahen's effects from the Gemini pictures (the user, 2026-10-26: 「亚恒的特效包交付了 gemini做的 你得处理一下」): every
picture cleaned into game-size frames the import reads (pixel_1x + manifest.json, Codex's delivery shape) -
tools/art/clean_skarner_fx.py's way.

    python tools/art/clean_zaahen_fx.py [--review out.png] [--only a,b]

The source: assets/source/zaahen/gemini_fx/zaahen_fx_<name>.jpg (the user's Gemini run of assets/source/zaahen/
PROMPTS_FX.md, one picture an effect, saved under the effect it draws). Its frames in a row, or in a grid (`grid`
(cols, rows), inside `crop` when Gemini framed them), drawn at ~8x on black - rv_glow and p_aura on white, r_rise with
white patches. Per effect (SPECS):
  * the background: everything joined to the cell's border through background pixels (black, Gemini's dark grey
    separators, and on `white` pictures / `patches` the near-white too) goes - a flood fill, so a white highlight inside
    a wing stays while a white patch at the cell's edge does not;
  * the size: every frame at ONE scale (the widest / tallest drawn extent fits the pack's cell less a margin; `stretch`
    fits width and height apart, for a ground ring), each game square the majority of its block (drawn if KEEP of it is
    drawn), its colour the block's median;
  * the colours: snapped to the pack's ramps (GOLD, CRIMSON, NAVY, STAR, DUST of pack_zaahen_fx.py), squares too dark to
    read (glow fringes) dropped;
  * symmetry: the fuller half mirrored onto the other, left-right for every picture the game does not turn, top-bottom
    for the W projectile;
  * stray single squares dropped; `keep` lowers KEEP for an effect of thin lines (a_hit's and e_hit's last frames).
rv_glow is drawn from its parts (compose_rv: Gemini's pale light on white cannot be told from the white): it stands
behind him, who is banished meanwhile and drawn over it by rig_zaahen.py.
Writes assets/source/zaahen/gemini_fx/clean/pixel_1x/zaahen_fx_<name>.png and manifest.json.
"""
import argparse
import json
import os
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_zaahen_fx as PF  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "zaahen", "gemini_fx")
OUT = os.path.join(SRC, "clean")
BG_DARK = 46          # a black picture's background and its glow fringes: max(r, g, b) at or under this
KEEP = 0.3            # a game square is drawn when this share of its block is drawn (thin shards survive)
EXT_Q = 98.0          # the extent read at this percentile of the drawn pixels (JPEG specks never set the scale)

# name -> (frames, cell (w, h) in game px, options); the cells are the pack's (pack_zaahen_fx.FX)
SPECS = {
    "w_glaive": (4, (32, 10), dict(grid=(2, 2), crop=(20, 130, 1980, 990), sym="tb", recentre=True)),
    "a_hit": (3, (16, 16), dict(keep=0.15)),
    "q_hit": (3, (20, 16), {}),
    "q_hit2": (3, (20, 20), dict(crop=(0, 198, 2000, 859))),
    "q_uphit": (5, (20, 44), {}),
    "w_hit": (4, (18, 18), dict(crop=(0, 280, 2000, 838))),
    "e_spin": (6, (56, 30), dict(grid=(3, 2), stretch=True)),
    "e_hit": (3, (16, 16), dict(keep=0.15)),
    "r_rise": (6, (64, 56), dict(patches=True)),
    "r_slam": (8, (64, 34), dict(grid=(4, 2), stretch=True)),
    "r_hit": (4, (18, 20), {}),
    "p_full": (6, (44, 52), {}),
    "p_aura": (6, (44, 52), dict(bg="white")),
    "p_shield": (4, (44, 52), dict(stretch=True)),
    "rv_glow": (8, (56, 70), dict(compose="rv")),
}


def palette():
    cols = []
    for ramp in (PF.GOLD, PF.CRIMSON, PF.NAVY, PF.STAR, PF.DUST):
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
    """Which source pixels of a cell are the effect: not joined to the cell's border through background pixels."""
    mx, mn = a.max(-1), a.min(-1)
    sat = (mx - mn) / np.maximum(mx, 1)
    bg = (mx <= BG_DARK) | ((sat < 0.15) & (mx < 90))              # black and Gemini's dark grey separators
    if opt.get("bg") == "white" or opt.get("patches"):
        bg |= (mn > 225) & (sat < 0.12)                             # near-white
    if opt.get("bg") == "white":
        bg |= (sat < 0.10) & (mx > 150)                             # the grey disc / haze Gemini drew on white
    seen = np.zeros_like(bg)
    q = deque()
    H, W_ = bg.shape
    for y in range(H):
        for x in (0, W_ - 1):
            if bg[y, x] and not seen[y, x]:
                seen[y, x] = True
                q.append((y, x))
    for x in range(W_):
        for y in (0, H - 1):
            if bg[y, x] and not seen[y, x]:
                seen[y, x] = True
                q.append((y, x))
    while q:
        y, x = q.popleft()
        for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if 0 <= yy < H and 0 <= xx < W_ and bg[yy, xx] and not seen[yy, xx]:
                seen[yy, xx] = True
                q.append((yy, xx))
    if opt.get("bg") == "white":   # on white every white pixel is background, closed shapes' insides too
        return ~bg & (mx > BG_DARK)
    return ~seen & (mx > BG_DARK)


def frames_of(img, n, opt):
    if "crop" in opt:
        x0, y0, x1, y1 = opt["crop"]
        img = img[y0:y1, x0:x1]
    H, W_ = img.shape[:2]
    cols, rows = opt.get("grid", (n, 1))
    out = []
    for r in range(rows):
        for c in range(cols):
            out.append(img[r * H // rows:(r + 1) * H // rows, c * W_ // cols:(c + 1) * W_ // cols])
    return out[:n]


def hexes(ramp):
    return [tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in ramp.split(", ")]


def compose_rv(cw, ch, n):
    """rv_glow drawn from its parts (Gemini's pale light on white cannot be told from the white): the ring of gold
    and crimson runes on the ground (its runes stepping round frame by frame), the column of light rising from it
    (white edges, gold glow outside, the palest gold inside: he is drawn over it), crimson petals drifting up inside,
    mirrored left to right. Frames 1-3 the column rising, 4-8 its loop. Inside the column every third column of squares
    is a streak of pale gold, the others clear but for glints running up (a solid pale slab behind him read flat)."""
    gold, crim = hexes(PF.GOLD), hexes(PF.CRIMSON)
    cx, gy = cw / 2, ch - 8                      # the ring's middle on the ground
    rx, ry = 22.0, 6.0
    c0, c1 = int(cx - 15), int(cx + 15)         # the column, 30 wide
    out = []
    for k in range(n):
        c = np.zeros((ch, cw, 4), np.uint8)

        def put(x, y, col):
            for xx in (x, cw - 1 - x):         # mirrored
                if 0 <= xx < cw and 0 <= y < ch:
                    c[y, xx, :3] = col
                    c[y, xx, 3] = 255
        top = {0: gy, 1: int(gy * 0.65), 2: int(gy * 0.25)}.get(k, 0)
        for y in range(top, int(gy) + 1):
            for x in range(c0 - 1, int(cx)):
                d = x - c0
                if d > 2 and d % 3 != 0:          # inside: streaks of light, not a solid slab (he stands in front)
                    if (y + k * 2 + d) % 11 == 0:
                        put(x, y, gold[0])        # a glint running up between the streaks
                    continue
                col = gold[3] if d == -1 else gold[0] if d in (0, 1) else gold[2] if d == 2 else gold[1]
                put(x, y, col)
        # the ring: an ellipse band, runes (crimson) every 6 degrees-steps moving round with the frames
        for t in range(0, 360, 3):
            r = np.radians(t)
            x, y = int(round(cx + rx * np.cos(r))), int(round(gy + ry * np.sin(r)))
            if x >= cx:
                continue
            rune = (t // 3 + k * 2) % 7 in (0, 1)
            put(x, y, crim[2] if rune else gold[2])
            put(x, y + 1, crim[3] if rune else gold[3])
        # petals drifting up inside the column (2 x 1, crimson), from frame 3 on
        if k >= 2:
            for p0 in (8, 26, 44, 60):
                y = int(gy - 4 - ((p0 + 7 * k) % int(gy - 6)))
                x = int(cx - 6 - (p0 % 7))
                put(x, y, crim[1])
                put(x - 1, y, crim[2])
        out.append(c)
    return out


def clean(name):
    n, (cw, ch), opt = SPECS[name]
    if opt.get("compose") == "rv":
        return compose_rv(cw, ch, n)
    a = np.asarray(Image.open(os.path.join(SRC, f"zaahen_fx_{name}.jpg")).convert("RGB")).astype(float)
    fr = frames_of(a, n, opt)
    masks = [drawn_mask(f, opt) for f in fr]
    # one scale for every frame: the drawn extent about each cell's middle
    masks = [lines_off(m) for m in masks]
    # the scale from the bright drawing only (faint dust and JPEG specks never set it)
    bright = [m & (f.max(-1) > 90) for f, m in zip(fr, masks)]
    if "ext_frames" in opt:   # the scale from these frames (a burst whose last frame is a far, faint ring)
        bright = [b if k in opt["ext_frames"] else np.zeros_like(b) for k, b in enumerate(bright)]
    dx = np.concatenate([np.abs(np.nonzero(b)[1] - b.shape[1] / 2) for b in bright if b.any()])
    # each frame's vertical middle: the cell's, or (`recentre`, the W projectile) its drawing's, so the top-bottom
    # mirror folds the drawing onto itself (Gemini drew the last two frames lower in their cells)
    cys = [((np.nonzero(b)[0].min() + np.nonzero(b)[0].max()) / 2 if opt.get("recentre") and b.any() else b.shape[0] / 2)
           for b in bright]
    dy = np.concatenate([np.abs(np.nonzero(b)[0] - cy) for b, cy in zip(bright, cys) if b.any()])
    ext_x, ext_y = np.percentile(dx, EXT_Q), np.percentile(dy, EXT_Q)
    bw, bh = opt.get("box", (cw - 2, ch - 2))
    sx, sy = bw / (2 * ext_x), bh / (2 * ext_y)
    if not opt.get("stretch"):
        sx = sy = min(sx, sy)
    out = []
    keep = opt.get("keep", KEEP)
    for f, m, cy in zip(fr, masks, cys):
        cell = np.zeros((ch, cw, 4), np.uint8)
        H, W_ = m.shape
        for y in range(ch):
            for x in range(cw):
                # the source block of game square (x, y): about the cell's middle
                y0, y1 = cy + (y - ch / 2) / sy, cy + (y + 1 - ch / 2) / sy
                mid = W_ / 2
                x0, x1 = mid + (x - cw / 2) / sx, mid + (x + 1 - cw / 2) / sx
                ys, ye = int(max(0, np.floor(y0))), int(min(H, np.ceil(y1)))
                xs, xe = int(max(0, np.floor(x0))), int(min(W_, np.ceil(x1)))
                if ye <= ys or xe <= xs:
                    continue
                bm = m[ys:ye, xs:xe]
                if bm.mean() < keep:
                    continue
                cell[y, x, :3] = np.median(f[ys:ye, xs:xe][bm], axis=0)
                cell[y, x, 3] = 255
        op = cell[..., 3] > 0
        rgb = cell[..., :3].astype(float)
        dark = rgb.max(-1) < 62
        cell[dark] = 0
        col = cell[..., 3] > 0
        cell[col, :3] = snap(rgb[col]).astype(np.uint8)
        if opt.get("fill_column"):
            fill_column(cell)
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


PALE = tuple(int(PF.GOLD.split(", ")[1][i:i + 2], 16) for i in (1, 3, 5))   # #FFF2C2


def fill_column(c):
    """rv_glow's light column: every row between the column's two edges (the drawn squares nearest the middle on
    each side, above the rune ring's rows) filled in the palest gold."""
    h, w = c.shape[:2]
    mid = w // 2
    for y in range(int(h * 0.75)):
        row = c[y, :, 3] > 0
        left = [x for x in range(mid, max(-1, mid - w // 3), -1) if row[x]]
        right = [x for x in range(mid, min(w, mid + w // 3)) if row[x]]
        if left and right and right[0] - left[0] > 2:
            for x in range(left[0] + 1, right[0]):
                if c[y, x, 3] == 0:
                    c[y, x] = PALE + (255,)


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
        cw, ch = SPECS[name][1]
        strip = np.concatenate(cs, axis=1)
        f = f"zaahen_fx_{name}.png"
        Image.fromarray(strip).save(os.path.join(OUT, "pixel_1x", f))
        man[f] = {"file": f, "frames": len(cs), "cell_1x": [cw, ch],
                  "symmetry": "top-bottom" if SPECS[name][2].get("sym") == "tb" else "left-right"}
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
