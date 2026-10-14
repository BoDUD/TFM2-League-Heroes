#!/usr/bin/env python3
"""Import Sion's effects (assets/source/sion/PROMPTS_FX.md, 15 sheets) as the game sheets league_sion_fx and
league_sion_big, from Codex's step-3 delivery (assets/source/sion/codex_fx: pixel_1x/, manifest.json, HANDOFF.md).

    python tools/art/import_sion_fx.py [--review out.png]

Codex delivered every sheet at game size (pixel_1x/: one game pixel a square, a row of equal cells, hard alpha, the
prompt's ramps, every cell symmetric) - tools/art/import_bard_fx.py's way: each cell is cut out, checked, made odd
across its mirror axis, given its anchor and placed on its spot. Its read-back took each whole tile of its 2-column
drafts down to the cell, margins and all, so the smaller pictures came out well under the prompt's size (the cleave
8 x 11 squares for 12, the roar 12 x 18 for 14 x 22, Q's ground line 47 x 12 for 52 x 24): those (REREAD) are read
again from its drafts (the manifest's `raw`) - the drawing's bounds over all frames brought to
the prompt's size (keeping the drawing's own proportions), every square the majority of the draft's opaque pixels
snapped to the sheet's palette, mirrored squares voting together (import_bard_fx.reread on a tile grid); those drafts
are kept in assets/source/sion/codex_fx/raw.
Q's line keeps its border and arrows solid and its flat dark fill at Q_FILL_ALPHA (the prompt: the inside see-through).
Red side and blue side alike: the client never mirrors an effect picture and turns a flying or ground-line one with
its direction, so q_warn, q_slam and e_roar are symmetric top to bottom, everything else left to right (check()).
Spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it. Times from the kit
(tools/kit/build_sion.py P, 60 ticks a second).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import import_jhin as J  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "sion", "codex_fx")
RAW = SRC                       # raw/ holds the drafts of the re-read sheets (and Codex's jobs.json: their grids)
MOD = os.path.join(ROOT, "league")

# sheet -> (frames, anchor: "core" (the cell's middle), "glow" (the middle column, the white core's row in the frame
# with the most white), "foot" (the lowest drawn row of all frames), "widest" (the row with the most squares in the
# fullest frame: a ground ring's middle), symmetry)
SHEETS = {
    "a_hit": (4, "core", "lr"), "k_soul": (5, "glow", "lr"), "q_warn": (4, "core", "tb"),
    "q_slam": (5, "core", "tb"), "q_hit": (5, "glow", "lr"), "e_roar": (4, "core", "tb"),
    "e_hit": (4, "core", "lr"), "e_shred": (4, "core", "lr"), "w_sh": (4, "foot", "lr"),
    "w_burst": (5, "widest", "lr"), "w_hit": (4, "core", "lr"), "r_go": (4, "widest", "lr"),
    "r_crash": (6, "widest", "lr"), "r_hit": (4, "glow", "lr"), "p_zombie": (4, "widest", "lr"),
}
# read again from the drafts at the prompt's size (w, h in game px: the drawing fits inside, its proportions kept);
# the cleave and the furnace's hit 16 (the prompt's 12 and 14 left the cleave's crescents and sparks thinner than a
# square: they broke up)
REREAD = {"a_hit": (16, 16), "k_soul": (14, 24), "q_warn": (52, 24), "e_roar": (14, 22), "w_hit": (16, 16)}
MARGIN = 1                      # clear squares round a re-read drawing
BRIGHT = 200                    # a colour this light (0.3 R + 0.59 G + 0.11 B) is a core, a ray or a spark
Q_FILL = (0x8E, 0x0E, 0x1E)     # Q's line: its flat dark fill ...
Q_FILL_ALPHA = 110              # ... drawn see-through
HIT = (0, -12)                  # a hit on the upper body of a 36-44 px unit
OVER = (0, -32)                 # over a unit's head
CHEST = (0, -8)                 # his furnace (90 %: 19 px over his soles)
SOLES = (0, 11)                 # on the ground under a unit or a point
seq = J.seq

FX = {
    "a_hit": ("a_hit", seq(range(4), [40, 50, 60, 70]), HIT),
    # a kill's soul into his furnace (400 ms)
    "k_soul": ("k_soul", seq(range(5), [60, 70, 80, 90, 100]), CHEST),
    "q_hit": ("q_hit", seq(range(5), [40, 50, 60, 70, 80]), HIT),
    # E's roar flies e_len 52000 at 3000 a tick (~17 ticks), looped
    "e_roar": ("e_roar", seq(range(4), [60] * 4), (0, 0)),
    "e_hit": ("e_hit", seq(range(4), [40, 50, 60, 70]), HIT),
    "w_hit": ("w_hit", seq(range(4), [40, 50, 60, 70]), HIT),
    "r_hit": ("r_hit", seq(range(4), [40, 50, 60, 70]), HIT),
    # the shredded armour's mark over the head, looped for e_shred_t
    "e_shred": ("e_shred", seq(range(4), [100] * 4), OVER),
}
BIG = {
    # Q: the line on the ground while he charges (looped, q_ch + q_hit + 2 ticks); the smash along it once (500 ms)
    "q_warn": ("q_warn", seq(range(4), [100] * 4), (0, 0)),
    "q_slam": ("q_slam", seq(range(5), [60, 80, 100, 120, 140]), (0, 0)),
    # W: the shield on him, looped while it holds; its blast at his feet
    "w_sh": ("w_sh", seq(range(4), [100] * 4), SOLES),
    "w_burst": ("w_burst", seq(range(5), [40, 50, 60, 80, 90]), SOLES),
    # R: the aura while he charges (looped), the crash where he hits, held to read (Galio's landing)
    "r_go": ("r_go", seq(range(4), [80] * 4), SOLES),
    "r_crash": ("r_crash", seq(range(6), [40, 60, 160, 120, 100, 90]), SOLES),
    # the add-on's zombie (looped while it lasts)
    "p_zombie": ("p_zombie", seq(range(4), [100] * 4), SOLES),
}
TB_TAGS = {"q_warn", "q_slam", "e_roar"}


def lp(p):
    return G.lp(p)


def manifest():
    with open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8") as f:
        return {a["file"][len("sion_fx_"):-len(".png")]: a for a in json.load(f)["assets"]}


def palette(a):
    return np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in a["palette"]], float)


def cells(name, n):
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"sion_fx_{name}.png"))).convert("RGBA")).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    w = a.shape[1] // n
    if w * n != a.shape[1]:
        sys.exit(f"sion_fx_{name}.png: {a.shape[1]} px is not {n} equal cells")
    return [a[:, k * w:(k + 1) * w].copy() for k in range(n)]


def jobs(raw_dir):
    with open(lp(os.path.join(raw_dir, "raw", "jobs.json")), encoding="utf-8") as f:
        return {j["file"][len("sion_fx_"):-len(".png")]: j for j in json.load(f)}


def LUM(pal):
    return pal @ np.array([0.3, 0.59, 0.11])


def reread(name, want, sym, raw_dir):
    """The sheet read again from Codex's draft (a grid of `columns` x `rows` tiles, frame k at column k % columns):
    the drawing's bounds over all frames (each tile's own, pieces of a neighbour's drawing reaching in left out)
    brought inside `want` (w, h game px) with its proportions, MARGIN clear squares round it."""
    a = manifest()[name]
    j = jobs(raw_dir)[name]
    raw = np.asarray(Image.open(lp(os.path.join(raw_dir, a["raw"]))).convert("RGBA")).astype(float)
    pal = palette(a)
    n, cols, rows = a["frames"], j["columns"], j["rows"]
    H, W = raw.shape[:2]
    tw, th = W / cols, H / rows
    op = raw[..., 3] >= 128
    b = []
    for k in range(n):
        x0, x1 = int(round((k % cols) * tw)), int(round((k % cols + 1) * tw))
        y0, y1 = int(round((k // cols) * th)), int(round((k // cols + 1) * th))
        sub = op[y0:y1, x0:x1]
        lab, m = ndimage.label(sub, structure=np.ones((3, 3)))
        edge = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])) - {0}
        area = np.bincount(lab.ravel())
        for i in edge:
            if area[i] < 0.03 * area[1:].sum():
                sub[lab == i] = False
        yy, xx = np.nonzero(sub)
        b.append((xx.min(), xx.max() + 1, yy.min(), yy.max() + 1))
    gx0, gx1 = min(x[0] for x in b), max(x[1] for x in b)
    gy0, gy1 = min(x[2] for x in b), max(x[3] for x in b)
    # symmetric about the tile's own axis: the bounds centred on it, as wide each side
    if sym == "lr":
        cx = tw / 2
        hw = max(cx - gx0, gx1 - cx)
        gx0, gx1 = cx - hw, cx + hw
    if sym == "tb":
        cy = th / 2
        hh = max(cy - gy0, gy1 - cy)
        gy0, gy1 = cy - hh, cy + hh
    s = min(want[0] / (gx1 - gx0), want[1] / (gy1 - gy0))      # game px a draft px
    W0, H0 = max(1, round((gx1 - gx0) * s)), max(1, round((gy1 - gy0) * s))
    sx, sy = (gx1 - gx0) / W0, (gy1 - gy0) / H0
    Wc, Hc = W0 + 2 * MARGIN, H0 + 2 * MARGIN
    snap = ((raw[..., None, :3] - pal[None, None]) ** 2).sum(-1).argmin(-1)
    bright = LUM(pal) >= BRIGHT
    out = []
    for k in range(n):
        ox, oy = (k % cols) * tw, (k // cols) * th
        votes = np.zeros((Hc, Wc, len(pal)))
        cover = np.zeros((Hc, Wc))
        for jy in range(Hc):
            y0 = max(0, int(round(oy + gy0 + (jy - MARGIN) * sy)))
            y1 = max(0, int(round(oy + gy0 + (jy + 1 - MARGIN) * sy)))
            for ix in range(Wc):
                x0 = max(0, int(round(ox + gx0 + (ix - MARGIN) * sx)))
                x1 = max(0, int(round(ox + gx0 + (ix + 1 - MARGIN) * sx)))
                o = op[y0:y1, x0:x1]
                if o.size:
                    cover[jy, ix] = o.mean()
                    if o.any():
                        votes[jy, ix] = np.bincount(snap[y0:y1, x0:x1][o], minlength=len(pal))
        if sym == "lr":
            votes, cover = votes + votes[:, ::-1], (cover + cover[:, ::-1]) / 2
        else:
            votes, cover = votes + votes[::-1], (cover + cover[::-1]) / 2
        c = np.zeros((Hc, Wc, 4), np.uint8)
        tot = votes.sum(-1)
        share = votes / np.maximum(tot, 1)[..., None] * cover[..., None]
        lit = share[..., bright].sum(-1)
        for jy in range(Hc):
            for ix in range(Wc):
                if lit[jy, ix] >= 0.2:          # a bright core or a thin ray: the brightest colour with a tenth or more
                    ids = [q for q in np.argsort(-LUM(pal)) if share[jy, ix, q] >= 0.1 and bright[q]]
                    best = ids[0] if ids else int(np.argmax(np.where(bright, share[jy, ix], -1)))
                elif cover[jy, ix] >= 0.45:     # else the commonest, a brighter one from 35 %
                    best = int(np.argmax(share[jy, ix]))
                    for q in np.argsort(-LUM(pal)):
                        if share[jy, ix, q] / max(cover[jy, ix], 1e-9) >= 0.35:
                            if LUM(pal)[q] > LUM(pal)[best]:
                                best = int(q)
                            break
                else:
                    continue
                c[jy, ix, :3] = pal[best].astype(np.uint8)
                c[jy, ix, 3] = 255
        out.append(c)
    return out


def check_cells(name, strip, sym):
    for k, c in enumerate(strip):
        if sym == "lr" and not (c == c[:, ::-1]).all():
            sys.exit(f"sion_fx_{name} cell {k + 1} is not symmetric left to right")
        if sym == "tb" and not (c == c[::-1]).all():
            sys.exit(f"sion_fx_{name} cell {k + 1} is not symmetric top to bottom")


def odd(c, sym):
    """An even cell made odd across its mirror axis: the column (row) left of (above) the axis doubled."""
    if sym == "lr" and c.shape[1] % 2 == 0:
        k = c.shape[1] // 2 - 1
        c = np.concatenate([c[:, :k + 1], c[:, k:k + 1], c[:, k + 1:]], 1)
    if sym == "tb" and c.shape[0] % 2 == 0:
        k = c.shape[0] // 2 - 1
        c = np.concatenate([c[:k + 1], c[k:k + 1], c[k + 1:]], 0)
    return c


def anchor(strip, kind):
    h, w = strip[0].shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    if kind == "glow":
        white = [((c[..., 3] > 0) & (c[..., :3] >= 250).all(-1)) for c in strip]
        k = int(np.argmax([m.sum() for m in white]))
        ys = np.nonzero(white[k])[0]
        return [(w - 1) / 2, float(ys.mean()) if len(ys) else (h - 1) / 2]
    if kind == "foot":
        return [(w - 1) / 2, max(int(np.nonzero((c[..., 3] > 0).any(1))[0].max()) for c in strip)]
    k = int(np.argmax([(c[..., 3] > 0).sum() for c in strip]))
    return [(w - 1) / 2, int(np.argmax((strip[k][..., 3] > 0).sum(1)))]


def see_through(c):
    """Q's line: its flat dark fill at Q_FILL_ALPHA, the border and the arrows solid."""
    m = (c[..., 3] > 0) & (c[..., :3] == Q_FILL).all(-1)
    c[m, 3] = Q_FILL_ALPHA
    return c


def build(table, raw_dir):
    out = {}
    for tag, (src, frames, spot) in table.items():
        n, kind, sym = SHEETS[src]
        strip = reread(src, REREAD[src], sym, raw_dir) if src in REREAD else cells(src, n)
        check_cells(src, strip, sym)
        strip = [odd(c, sym) for c in strip]
        if src == "q_warn":
            strip = [see_through(c) for c in strip]
        anc = anchor(strip, kind)
        out[tag] = [(J.place(strip[k], anc, [spot]), ms) for k, ms in frames]
    return out


def check(tags):
    bad = []
    for name, frames in tags.items():
        for k, (a, _) in enumerate(frames):
            if a.shape[0] % 2 == 0 or a.shape[1] % 2 == 0:
                bad.append(f"{name} {k + 1}: even size {a.shape[:2]}")
            if name in TB_TAGS and not (a == a[::-1]).all():
                bad.append(f"{name} {k + 1}: not symmetric top to bottom")
            if name not in TB_TAGS and not (a == a[:, ::-1]).all():
                bad.append(f"{name} {k + 1}: not symmetric left to right")
    return bad


def review(sheets, path, z=6):
    """Every tag's frames at z on the arena's colour, cropped to what the tag draws, the pivot's column marked."""
    rows = []
    for tags in sheets:
        for name, frames in tags.items():
            fr = [a for a, _ in frames]
            H = max(f.shape[0] for f in fr)
            W = max(f.shape[1] for f in fr)
            pad = []
            for f in fr:
                c = np.zeros((H, W, 4), np.uint8)
                y0, x0 = (H - f.shape[0]) // 2, (W - f.shape[1]) // 2
                c[y0:y0 + f.shape[0], x0:x0 + f.shape[1]] = f
                pad.append(c)
            op = np.zeros((H, W), bool)
            for c in pad:
                op |= c[..., 3] > 0
            ys, xs = np.nonzero(op)
            rows.append((name, [c[ys.min():ys.max() + 1, xs.min():xs.max() + 1] for c in pad]))
    W = max(sum(f.shape[1] + 2 for f in fr) for _, fr in rows) * z + 90
    H = sum(max(f.shape[0] for f in fr) * z + 8 for _, fr in rows)
    img = Image.new("RGBA", (W, H), (104, 112, 72, 255))
    d = ImageDraw.Draw(img)
    y = 0
    for name, fr in rows:
        d.text((4, y + 2), name, fill=(255, 255, 255, 255))
        x = 90
        for f in fr:
            img.alpha_composite(Image.fromarray(np.ascontiguousarray(f)).resize((f.shape[1] * z, f.shape[0] * z),
                                                                               Image.NEAREST), (x, y))
            x += (f.shape[1] + 2) * z
        y += max(f.shape[0] for f in fr) * z + 8
    img.convert("RGB").save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game frames at 6x here")
    ap.add_argument("--raw", default=RAW, help="Codex's delivery folder holding raw/ (for the re-read sheets)")
    a = ap.parse_args()
    used = {v[0] for table in (FX, BIG) for v in table.values()}
    if used != set(SHEETS):
        sys.exit(f"sheets not imported: {sorted(set(SHEETS) - used)}")
    out, bad = [], []
    for sheet, table in (("league_sion_fx", FX), ("league_sion_big", BIG)):
        tags = build(table, a.raw)
        bad += check(tags)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags, share=True)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
        out.append(tags)
    for b in bad:
        print("BAD", b)
    if a.review:
        review(out, a.review)
    if bad:
        sys.exit(1)


if __name__ == "__main__":
    main()
