#!/usr/bin/env python3
"""Kindred's effects from Codex's step-3 delivery (assets/source/kindred/codex_fx, from kindred_fx_pack_done.zip of
2026-10-14) as the game sheets league_kindred_fx / league_kindred_big, and the pictures drawn into her frames
(assets/source/kindred/fx_bake, laid onto her restyled dense frames by tools/art/rig_kindred.py --pinholes).

    python tools/art/import_kindred_fx.py --prepare <delivery dir>   (once: copies what the import reads)
    python tools/art/import_kindred_fx.py [--review DIR]

Codex drew every effect as its own sheet (raw/kindred_fx_<name>.png: the frames side by side, squares of 13-18 px; its
manifest.json gives each frame's rectangle) and read them back itself onto the cells the pack asked for (pixel_1x/:
a fifth of a block's coverage counted as drawn, at the pack's sizes). Those sizes were too small for the arrows, the
marks and the Wolf's head (the art-spec's projectiles are 25-75 px): the arrows came out as 4-square capsules, the
swirls as blobs, the bite as specks. So those sheets are read again here from the raw pictures (READ): each frame round
its rectangle's middle at the sheet's one scale (the widest frame to WIDTH game pixels), a pixel drawn where half its
block is, its colour the block's commonest once every raw pixel is snapped to the effect's ramp (the manifest's
palette; white counted WHITE_W times, so the cores stay white), then mirrored - left to right, or top to bottom for the
arrows (they are turned to their flight) - and p_stack's stick cut off (it read as a lollipop). The swirls (e_mark,
p_stack) keep Codex's turn: a swirl has no front or back. The ground circles and the heal stay Codex's own read-backs
(pixel_1x: at 100-120 squares a frame it is about 1:1). Spots, sheets and times: FX.
The pictures for her frames are Codex's read-backs on the pack's guides (pixel_1x/kindred_bake_*.png: 256 x 170 or
170 x 256 dense squares, placed on the guide's crosses by Codex). q_trail ran 8-9 game px below the ground line (the
leap is level): its rows under the hind hooves are squashed so its end lies on the ground line.
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
from design_varus import srgb2lab  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "kindred")
CODEX = os.path.join(SRC, "codex_fx")
BAKE_DIR = os.path.join(SRC, "fx_bake")
CELLS = os.path.join(SRC, "fx_bake_cells.json")
MOD = os.path.join(ROOT, "league")
FEET = 11                       # game px from the pivot down to the soles
HD_PPU = 2.86                   # her dense frames' squares a game pixel (ppu_hd.PPU["kindred"])
ALPHA = 128                     # a raw pixel is drawn from this alpha up (Codex's glow is softer)
NEED = 0.5                      # a game pixel is drawn where this share of its block is
WHITE_W = 1.6                   # white's weight in a block's vote
SOLE = (0, FEET)

# name -> (read: None = Codex's pixel_1x, else (width in game px, mirror "lr" / "ud" / None)), frames, cell (pixel_1x),
#         sheet (big?), spot (the frame centre from the unit's pivot, game px; "feet": the last row on the soles row),
#         frame times (ms)
FX = {
    # in flight: Animated, looping (build_kindred P_)
    "a_arrow": ((22, "ud"), 4, (16, 6), False, (0, 0), [70] * 4),
    "q_arrow": ((24, "ud"), 4, (18, 7), False, (0, 0), [70] * 4),
    "e_arrow": ((26, "ud"), 4, (20, 8), False, (0, 0), [70] * 4),
    # on the target
    "a_hit": ((16, "lr"), 4, (14, 14), False, (0, -6), [40, 50, 60, 70]),
    "q_hit": ((18, "lr"), 4, (16, 16), False, (0, -6), [40, 50, 60, 70]),
    "e_hit": ((22, "lr"), 5, (20, 20), False, (0, -6), [40, 50, 60, 70, 80]),
    # the mark over the target's head: replayed every e_pic 20 ticks while it lasts - one 333-ms loop
    "e_mark": ((13, None), 4, (14, 14), False, (0, -27), [83, 83, 84, 83]),
    # a mark gained, over her head (a buff's Animated, looping for its 90 ticks)
    "p_stack": ((13, None), 4, (12, 14), False, (0, -31), [100] * 4),
    "e_bite": ((42, "lr"), 6, (30, 34), True, (0, -10), [60, 60, 70, 90, 100, 110]),
    "w_bite": ((22, "lr"), 5, (20, 20), False, (0, -8), [50, 60, 70, 80, 90]),
    # on the ground at her cast spot (z -1, not following)
    "q_dash": ((26, "lr"), 5, (26, 10), False, SOLE, [50, 60, 70, 80, 90]),
    "w_zone": (None, 10, (124, 50), True, SOLE, None),
    "r_zone": (None, 9, (104, 44), True, SOLE, None),
    "r_heal": (None, 6, (20, 34), False, "feet", [70, 80, 90, 100, 110, 130]),
}
# the zones: (frames that open it, the loop's frames, frames that close it) and the zone's whole time (ms; build_kindred
# w_t 510 and r_t 240 ticks): the loop runs as many whole times as fit, the last frame of it held for what is left
ZONE = {"w_zone": ([0, 1], [2, 3, 4, 5, 6, 7], [8, 9], 8500, 100, (100, 150)),
        "r_zone": ([0, 1], [2, 3, 4, 5], [6, 7, 8], 4000, 100, (100, 130))}
MOTE = 4                        # a picture for her frames keeps pieces of this many squares and more
BAKES = ["a_nock_2", "a_nock_3", "a_loose_4", "e_nock_2", "e_nock_3", "e_loose_4", "q_nock_5", "q_loose_6",
         "q_trail_3", "q_trail_4", "r_raise_5", "w_call_2"]


def load(path):
    return np.asarray(Image.open(path).convert("RGBA"))


def manifest():
    with open(os.path.join(CODEX, "manifest.json"), encoding="utf-8") as f:
        return {it["file"]: it for it in json.load(f)["items"]}


def hexes(pal):
    return np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in pal], float)


# ------------------------------------------------------------------------------------------- the raw sheets
SPECK = 40                      # raw pieces smaller than this (px) are the generator's noise, not the effect's sparkles


def split(drawn, rects):
    """Each frame's columns: in the middle part between two rectangles' middles (a frame can be empty in its own
    middle - e_bite's two smoke curls), the column with the fewest drawn pixels."""
    col = drawn.sum(0)
    mids = [(r[0] + r[2]) / 2.0 for r in rects]
    cuts = [0]
    for m0, m1 in zip(mids, mids[1:]):
        lo, hi = int(m0 + 0.3 * (m1 - m0)), int(m1 - 0.3 * (m1 - m0))
        cuts.append(lo + int(np.argmin(col[lo:hi])))
    cuts.append(drawn.shape[1])
    return [(cuts[k], cuts[k + 1]) for k in range(len(rects))]


def despeckle(drawn):
    lbl, n = ndimage.label(drawn, structure=np.ones((3, 3)))
    if not n:
        return drawn
    sizes = ndimage.sum(drawn, lbl, range(1, n + 1))
    keep = np.zeros(n + 1, bool)
    keep[1:] = sizes >= SPECK
    return keep[lbl]


def read(name, item, width, mirror):
    """The raw sheet's frames in game pixels: one scale for the sheet, each frame round its rectangle's middle."""
    a = load(os.path.join(CODEX, "raw", f"kindred_fx_{name}.png"))
    rects = item["source_rectangles"]
    pal = hexes(item["palette"])
    lab = srgb2lab(pal)
    drawn = despeckle(a[..., 3] >= ALPHA)
    cols = split(drawn, rects)
    # every raw pixel snapped to the ramp once
    flat = a[..., :3].reshape(-1, 3).astype(float)
    idx = np.full(flat.shape[0], -1)
    m = drawn.reshape(-1)
    d = ((srgb2lab(flat[m])[:, None, :] - lab[None, :, :]) ** 2).sum(-1)
    idx[m] = d.argmin(1)
    idx = idx.reshape(a.shape[:2])
    if name == "p_stack":
        idx = cut_stick(idx)
    pieces = []
    for (x0, x1), r in zip(cols, rects):
        sub = idx[:, x0:x1]
        ys, xs = np.nonzero(sub >= 0)
        cx, cy = (r[0] + r[2]) / 2.0 - x0, (r[1] + r[3]) / 2.0
        pieces.append((sub, ys, xs, cx, cy))
    widest = max(xs.max() - xs.min() + 1 for _, ys, xs, _, _ in pieces if len(xs))
    s = widest / float(width)                                   # raw px a game px
    white = int(np.argmax(pal.sum(1)))
    out = []
    for sub, ys, xs, cx, cy in pieces:
        if not len(xs):
            out.append(np.zeros((1, 1, 4), np.uint8))
            continue
        hw = int(np.ceil(max(cx - xs.min(), xs.max() + 1 - cx) / s)) + 1
        hh = int(np.ceil(max(cy - ys.min(), ys.max() + 1 - cy) / s)) + 1
        f = np.zeros((2 * hh + 1, 2 * hw + 1, 4), np.uint8)
        for j in range(2 * hh + 1):
            ya, yb = cy + (j - hh - 0.5) * s, cy + (j - hh + 0.5) * s
            r0, r1 = max(0, int(round(ya))), min(sub.shape[0], int(round(yb)))
            if r1 <= r0:
                continue
            for i in range(2 * hw + 1):
                xa, xb = cx + (i - hw - 0.5) * s, cx + (i - hw + 0.5) * s
                c0, c1 = max(0, int(round(xa))), min(sub.shape[1], int(round(xb)))
                if c1 <= c0:
                    continue
                blk = sub[r0:r1, c0:c1].reshape(-1)
                on = blk[blk >= 0]
                if len(on) < NEED * len(blk):
                    continue
                cnt = np.bincount(on, minlength=len(pal)).astype(float)
                cnt[white] *= WHITE_W
                f[j, i, :3] = pal[int(np.argmax(cnt))]
                f[j, i, 3] = 255
        out.append(mirrored(f, mirror))
    return out, s


def mirrored(f, how):
    """Left half onto the right (the middle column kept), or the top half onto the bottom."""
    f = f.copy()
    if how == "lr":
        w = f.shape[1]
        f[:, w - w // 2:] = f[:, :w // 2][:, ::-1]
    elif how == "ud":
        h = f.shape[0]
        f[h - h // 2:] = f[:h // 2][::-1]
    return f


def cut_stick(idx):
    """p_stack: Codex hung the swirl on a stick of light (a lollipop): in each frame's biggest piece, the rows under its
    middle no wider than STICK raw px go."""
    STICK = 70
    on = idx >= 0
    lbl, n = ndimage.label(on, structure=np.ones((3, 3)))
    if not n:
        return idx
    sizes = ndimage.sum(on, lbl, range(1, n + 1))
    out = idx.copy()
    for k in np.argsort(sizes)[::-1][:4]:                     # the four frames' swirls are the four biggest pieces
        piece = lbl == k + 1
        ys = np.nonzero(piece.any(1))[0]
        mid = (ys.min() + ys.max()) // 2
        for y in ys[ys > mid]:
            xs = np.nonzero(piece[y])[0]
            if xs.max() - xs.min() + 1 <= STICK:
                out[y, xs] = -1
        # what the cut left hanging under the swirl
        rest = (out >= 0) & piece
        lbl2, n2 = ndimage.label(rest, structure=np.ones((3, 3)))
        if n2 > 1:
            keep = 1 + int(np.argmax(ndimage.sum(rest, lbl2, range(1, n2 + 1))))
            out[rest & (lbl2 != keep)] = -1
    return out


def codex_frames(name, n, cell):
    """Codex's own read-back: the pixel_1x sheet's n cells. Its cells are an even number of squares wide, mirrored
    about the line between the two middle columns; one of those two goes, so the picture is mirrored about a column
    and its middle lands on the pivot's column (an even width would sit half a pixel off it)."""
    a = load(os.path.join(CODEX, "pixel_1x", f"kindred_fx_{name}.png"))
    cw, ch = cell
    if a.shape[1] != cw * n or a.shape[0] != ch:
        sys.exit(f"pixel_1x/kindred_fx_{name}.png is {a.shape[1]}x{a.shape[0]}, not {n} cells of {cw}x{ch}")
    out = []
    for k in range(n):
        f = a[:, k * cw:(k + 1) * cw].copy()
        if cw % 2 == 0 and (f == f[:, ::-1]).all():
            f = np.delete(f, cw // 2, axis=1)
        out.append(f)
    return out


# ------------------------------------------------------------------------------------------- the frames
def placed(f, spot):
    """The frame on a canvas whose centre is the unit's pivot: the picture's middle on `spot` (pivot-relative game
    px), or its last drawn row on the soles row ("feet")."""
    ys, xs = np.nonzero(f[..., 3] > 0)
    if not len(xs):
        return np.zeros((1, 1, 4), np.uint8)
    h, w = f.shape[:2]
    if spot == "feet":
        return G.centre_frame(f, -(w // 2), FEET - 1 - ys.max())
    return G.centre_frame(f, -(w // 2) + spot[0], spot[1] - h // 2)


def zone_times(name):
    """The zone's frame order and times: open, the loop as long as it lasts, close."""
    opening, loop, closing, total, ms, (open_ms, close_ms) = ZONE[name]
    order = [(k, open_ms) for k in opening]
    left = total - open_ms * len(opening) - close_ms * len(closing)
    while left >= ms * len(loop):
        order += [(k, ms) for k in loop]
        left -= ms * len(loop)
    i = 0
    while left >= ms:
        order.append((loop[i % len(loop)], ms))
        left -= ms
        i += 1
    if left:
        order[-1] = (order[-1][0], order[-1][1] + left)
    order += [(k, close_ms) for k in closing]
    return order


def effects():
    """{name: [(frame, ms)]} placed round the pivot; and notes."""
    man = manifest()
    out, notes = {}, []
    for name, (how, n, cell, big, spot, times) in FX.items():
        if how is None:
            frames = codex_frames(name, n, cell)
            src = "pixel_1x"
        else:
            frames, s = read(name, man[f"kindred_fx_{name}.png"], *how)
            src = f"raw at {s:.1f} px a game px"
        if len(frames) != n:
            sys.exit(f"{name}: {len(frames)} frames, not {n}")
        if name in ZONE:
            seq = [(frames[k], ms) for k, ms in zone_times(name)]
        else:
            seq = list(zip(frames, times))
        out[name] = [(placed(f, spot), float(ms)) for f, ms in seq]
        size = max(f.shape[1] for f in frames), max(f.shape[0] for f in frames)
        notes.append(f"{name}: {n} frames from {src}, up to {size[0]}x{size[1]}, {sum(m for _, m in seq):.0f} ms")
    return out, notes


def check(e):
    bad = []
    for name, seq in e.items():
        how = FX[name][0]
        mirror = how[1] if how else "lr"
        for k, (f, _) in enumerate(seq):
            al = f[..., 3]
            if not al.any():
                bad.append(f"{name} {k + 1} empty")
            if set(np.unique(al)) - {0, 255}:
                bad.append(f"{name} {k + 1} soft alpha")
            if mirror == "lr" and not (f == f[:, ::-1]).all() and name not in ("r_zone",):
                bad.append(f"{name} {k + 1} not symmetric left to right")
    return bad


# ------------------------------------------------------------------------------------------- her frames' pictures
def bakes():
    """{name_k: overlay on its guide canvas (RGBA)} from Codex's read-backs, q_trail squashed onto the ground."""
    with open(CELLS, encoding="utf-8") as f:
        cells = json.load(f)
    out = {}
    for key in BAKES:
        a = load(os.path.join(CODEX, "pixel_1x", f"kindred_bake_{key}.png")).copy()
        c = cells[key]
        if list(a.shape[1::-1]) != c["canvas"]:
            sys.exit(f"pixel_1x/kindred_bake_{key}.png is {a.shape[1]}x{a.shape[0]}, the guide {c['canvas']}")
        a[a[..., 3] < 128] = 0
        a[..., 3][a[..., 3] > 0] = 255
        # motes of 1-3 squares (a third of a game pixel each) would be left as specks on her frames (ppu_hd's check,
        # the user's 「别留多余的像素」): they go
        op = a[..., 3] > 0
        lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
        if n:
            sizes = ndimage.sum(op, lbl, range(1, n + 1))
            small = np.zeros(n + 1, bool)
            small[1:] = sizes < MOTE
            a[small[lbl]] = 0
        if key.startswith("q_trail"):
            x0, y0, W, H = c["frame"]
            ground = int(round(y0 + H / 2.0 + FEET * HD_PPU))
            a = squash(a, c["cyan"][1], ground)
        out[key] = a
    return out


def squash(a, top, ground):
    """The rows under `top` brought up so the lowest drawn row lands on `ground` (nearest rows, kept in order)."""
    rows = np.nonzero(a[..., 3].any(1))[0]
    low = rows.max()
    if low <= ground or top >= ground:
        return a
    k = (ground - top) / float(low - top)
    out = a.copy()
    out[top:] = 0
    for y in range(top, ground + 1):
        src = top + int(round((y - top) / k))
        out[y] = a[min(src, a.shape[0] - 1)]
        # the rows the squash skips over keep their pixels where the row it took is clear
        for s2 in range(top + int(round((y - top - 0.5) / k)), top + int(round((y - top + 0.5) / k)) + 1):
            if 0 <= s2 < a.shape[0]:
                m = (out[y, :, 3] == 0) & (a[s2, :, 3] > 0)
                out[y, m] = a[s2, m]
    return out


# ------------------------------------------------------------------------------------------- review
def review(out_dir, e, baked):
    from PIL import ImageDraw
    os.makedirs(out_dir, exist_ok=True)
    Z = 6
    rows = []
    for name, seq in e.items():
        firsts = []
        seen = set()
        for f, ms in seq:
            key = f.tobytes()
            if key in seen:
                continue
            seen.add(key)
            firsts.append(f)
        z = 2 if name in ("w_zone", "r_zone") else Z
        tiles = []
        for f in firsts:
            bg = Image.new("RGBA", (f.shape[1], f.shape[0]), (52, 60, 46, 255))
            bg.alpha_composite(Image.fromarray(f))
            d = ImageDraw.Draw(bg)
            cx, cy = f.shape[1] // 2, f.shape[0] // 2
            d.point((cx, cy), fill=(255, 0, 0, 255))
            tiles.append(bg.resize((f.shape[1] * z, f.shape[0] * z), Image.NEAREST))
        W = sum(t.width + 4 for t in tiles)
        H = max(t.height for t in tiles) + 14
        r = Image.new("RGB", (W, H), (16, 16, 16))
        ImageDraw.Draw(r).text((2, 1), f"{name} (red dot: the unit's pivot)", fill=(255, 255, 0))
        x = 0
        for t in tiles:
            r.paste(t.convert("RGB"), (x, 14))
            x += t.width + 4
        rows.append(r)
    W = max(r.width for r in rows)
    sheet = Image.new("RGB", (W, sum(r.height + 4 for r in rows)), (0, 0, 0))
    y = 0
    for r in rows:
        sheet.paste(r, (0, y))
        y += r.height + 4
    sheet.save(os.path.join(out_dir, "kindred_fx_frames.png"))
    print(os.path.join(out_dir, "kindred_fx_frames.png"), sheet.size)


def prepare(delivery):
    """The parts of Codex's delivery the import reads, into assets/source/kindred/codex_fx (the bakes' raw pictures,
    13 MB, stay in the delivery: their read-backs are on the guides' grid already)."""
    os.makedirs(os.path.join(CODEX, "raw"), exist_ok=True)
    os.makedirs(os.path.join(CODEX, "pixel_1x"), exist_ok=True)
    for f in sorted(os.listdir(os.path.join(delivery, "raw"))):
        if f.startswith("kindred_fx_"):
            shutil.copy2(os.path.join(delivery, "raw", f), os.path.join(CODEX, "raw", f))
    for f in sorted(os.listdir(os.path.join(delivery, "pixel_1x"))):
        shutil.copy2(os.path.join(delivery, "pixel_1x", f), os.path.join(CODEX, "pixel_1x", f))
    for f in ("HANDOFF.md", "manifest.json", "validation.json", "generation-prompts.txt"):
        shutil.copy2(os.path.join(delivery, f), os.path.join(CODEX, f))
    print("prepared", CODEX)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prepare", help="Codex's delivery folder (unzipped)")
    ap.add_argument("--review", help="write every effect's frames at 6x here")
    a = ap.parse_args()
    if a.prepare:
        prepare(a.prepare)
        return
    e, notes = effects()
    for line in notes:
        print(line)
    bad = check(e)
    if bad:
        sys.exit("\n".join(bad))
    tables = {"league_kindred_fx": {}, "league_kindred_big": {}}
    for name, seq in e.items():
        tables["league_kindred_big" if FX[name][3] else "league_kindred_fx"][name] = seq
    for sheet, tags in tables.items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags, share=True)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    baked = bakes()
    os.makedirs(BAKE_DIR, exist_ok=True)
    for old in os.listdir(BAKE_DIR):
        if old.endswith(".png"):
            os.remove(os.path.join(BAKE_DIR, old))
    for key, arr in baked.items():
        Image.fromarray(arr).save(os.path.join(BAKE_DIR, f"{key}.png"))
    print("baked", len(baked), "pictures ->", BAKE_DIR)
    if a.review:
        review(a.review, e, baked)


if __name__ == "__main__":
    main()
