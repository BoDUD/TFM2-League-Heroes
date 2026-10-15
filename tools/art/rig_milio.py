#!/usr/bin/env python3
"""Milio's game sheets from his dense frames (tools/art/import_milio_strips.py -> assets/source/milio/frames) and the
designs (tools/art/design_milio_hd.py -> assets/source/milio/hd) - league_kindred's and league_malzahar's way.

    python tools/art/rig_milio.py [--review DIR]

Density: the user picked 32 game rows from the hair top to the soles at 2.2 squares a game pixel (2026-10-15); the
frames are drawn on Codex's own grid (the boy 95 squares tall, NATIVE = 95 / 32 a game pixel) and brought to PPU here
(pixel_down.pixelate on a grid through the pivot, the design's 40 colours), so ppu_restyle.py changes no density.
One face (memory one-face-all-frames): the head is cut from every frame before the downscale and the design's head,
brought down once (HEAD2), goes back in its place - the same squares in every frame; where Codex's arm passes over
the hair (ult_2's fists) the arm stays in front.
The fire spirit (the user's pick: picture B, the spirit floating behind his shoulder) is a layer of its own: Codex's
four-frame flicker loop (codex_strips/spirit, the design's spirit with its flame tips moving and the 0/1/2/1 float),
brought down once each and laid UNDER the boy: in the idle where the front design has it; in the actions it follows
him a beat behind (FOLLOW of the way a frame towards its place by his head - the front design's own offset from the
head - from its idle place), pushed back while less than SPIRIT_SHOW of it shows; in the death it stays where it was,
sinks and shrinks away.
  idle   the front design (hd/front_boy.png) breathing (everything above WAIST2 up BREATH squares, the squares it
         uncovers taking the colour under them), the spirit flickering at its own place;
  hit    the side design moved HIT_DX back, a white flash on the first frame;
  the rest  the action frames as imported.
Writes assets/source/ppu/orig/milio_<tag>.png / .json (the frames at PPU, each round(PPU x its 1x frame) round the
pivot) and league/champions/league_milio#sheet.png / #anim.fanim (the 1x tags: each 1x pixel the commonest colour of
its squares; the fallback without league.dll). Then tools/art/ppu_restyle.py --hero milio (RESTYLE: the outer
outline grown a square, the face point), python tools/art/rig_milio.py --pinholes (the gaps the grown outline pinched
shut) and tools/art/ppu_hd.py --hero milio.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import pixel_down as PD  # noqa: E402
import import_milio_strips as I  # noqa: E402

NATIVE = 95 / 32                  # the frames' squares a game pixel (the boy 95 squares = 32 game rows)
PPU = 2.2                         # the user's density
K = PPU / NATIVE
FEET = 11                         # 1x rows from the pivot down to the ground row (the pack's 128-canvas heroes)
STEM = os.path.join(ROOT, "league", "champions", "league_milio")
ORIG = os.path.join(ROOT, "assets", "source", "ppu", "orig")
HD = os.path.join(I.SRC, "hd")
SPIRIT_DIR = os.path.join(I.SRC, "codex_strips", "spirit")
PIVOT = (I.PIV + 0.5, I.SOLE + 1)  # the native pivot: the standing column's middle on the ground line
PALF = I.PAL.astype(float)
OUTLINE = tuple(int(v) for v in I.PAL[I.OUTLINE])
TIMING = {"run": [117] * 8, "attack": [80, 80, 100, 100, 110], "skill": [70, 70, 70, 90, 100, 110],
          "skill2": [90, 90, 110, 110, 110], "ult": [90, 100, 100, 120, 120, 130],
          "dead": [110, 110, 120, 150, 200, 400]}
ORDER = ["idle", "run", "attack", "skill", "skill2", "ult", "hit", "dead"]
IDLE_MS = 150
BREATH = [0, 0, 1, 1, 1, 1, 0, 0]  # the idle's upper body, squares up (eight frames: the spirit's loop twice)
HIT_DX = 4                        # native squares back
HIT = [(HIT_DX, True, 90), (HIT_DX // 2, False, 120)]
SPIRIT_SHOW = 0.85               # at least this share of it shows past him
RUN_BACK = 3                      # the run: the spirit a little further back (it follows him)
DEAD_FADE = [1.0, 1.0, 0.7, 0.4, 0.0, 0.0]
DEAD_SINK = [0, 2, 5, 8, 0, 0]    # native squares down while it fades


def rgba(path):
    return np.asarray(Image.open(path).convert("RGBA")).copy()


def design_info():
    return json.load(open(os.path.join(HD, "design.json"), encoding="utf-8"))


# ------------------------------------------------------------------------------------------------- the grid
def down2(a, pivot=PIVOT):
    """A native picture brought to PPU on the grid through `pivot` -> (picture, the pivot's corner (x, y))."""
    out, (nx0, ny0) = PD.pixelate(a, K, pivot, OUTLINE, PALF)
    return out, (nx0, ny0)


def to_grid(r, c, corner):
    """A native (row, col) -> its square on the PPU grid whose pivot corner is `corner` (x, y)."""
    return int(round((r - PIVOT[1]) * K + corner[1])), int(round((c - PIVOT[0]) * K + corner[0]))


def paste_over(dst, src, r0, c0, keep=None):
    ys, xs = np.nonzero(src[..., 3] > 0)
    r, c = ys + r0, xs + c0
    ok = (r >= 0) & (r < dst.shape[0]) & (c >= 0) & (c < dst.shape[1])
    r, c, ys, xs = r[ok], c[ok], ys[ok], xs[ok]
    if keep is not None:
        free = ~keep[r, c]
        r, c, ys, xs = r[free], c[free], ys[free], xs[free]
    dst[r, c] = src[ys, xs]


def paste_under(dst, src, r0, c0):
    ys, xs = np.nonzero(src[..., 3] > 0)
    r, c = ys + r0, xs + c0
    ok = (r >= 0) & (r < dst.shape[0]) & (c >= 0) & (c < dst.shape[1])
    r, c, ys, xs = r[ok], c[ok], ys[ok], xs[ok]
    free = dst[r, c, 3] == 0
    dst[r[free], c[free]] = src[ys[free], xs[free]]


HEAD2 = down2(I.HEAD, pivot=(0.0, 0.0))[0]      # the design's head on its own grid (its top-left on a corner)


def with_head(native, head):
    """The native frame without its head (the design's head squares cleared, Codex's arms over it kept) brought to
    PPU, and the design's head brought down once (HEAD2) pasted on its square - under any arm that crosses it."""
    hr, hc = head
    hm = np.zeros(native.shape[:2], bool)
    ys, xs = np.nonzero(I.HEAD[..., 3] > 0)
    r, c = ys + hr, xs + hc
    ok = (r >= 0) & (r < hm.shape[0]) & (c >= 0) & (c < hm.shape[1])
    hm[r[ok], c[ok]] = True
    tpl = np.zeros_like(native)
    tpl[r[ok], c[ok]] = I.HEAD[ys[ok], xs[ok]]
    arm = hm & (native[..., 3] > 0) & np.any(native[..., :3] != tpl[..., :3], axis=-1)
    body = native.copy()
    body[hm & ~arm] = 0
    small, corner = down2(body)
    am = np.zeros_like(native)
    am[arm] = (255, 255, 255, 255)
    arm2 = down2(am)[0][..., 3] > 0
    r2, c2 = to_grid(hr, hc, corner)
    out = small.copy()
    paste_over(out, HEAD2, r2, c2, keep=arm2 & (small[..., 3] > 0))
    return out, corner


HOLE_FILL = 12                    # enclosed holes up to this many squares are filled (memory gap-check: at game size
                                  # they are specks of ground - the spirit against his shoulder, between fingers, crossed
                                  # legs); bigger ones (an arm held off the body, a palm beside the face) are real gaps


def tidy(a):
    """The outline closed, holes of up to HOLE_FILL squares filled (up to 4 with the colour round them, the rest with
    the darkest one), loose squares (pieces under 3) off - the joins of the pasted head and the spirit."""
    out = G.complete_outline(a, color=OUTLINE)[0]
    op = out[..., 3] > 0
    holes = ndimage.binary_fill_holes(op) & ~op
    lbl, n = ndimage.label(holes)
    for k in range(1, n + 1):
        m = lbl == k
        if m.sum() > HOLE_FILL:
            continue
        ring = ndimage.binary_dilation(m, structure=np.ones((3, 3))) & op
        cols, cnt = np.unique(out[ring][:, :3], axis=0, return_counts=True)
        if m.sum() <= 4:
            out[m, :3] = cols[cnt.argmax()]
        else:                     # the darkest colour round it that is not the outline (a shadow, not a black blot)
            lit = [c for c in cols if tuple(int(v) for v in c) != OUTLINE]
            out[m, :3] = min(lit, key=lambda c: int(c.astype(int).sum())) if lit else OUTLINE
        out[m, 3] = 255
    op = out[..., 3] > 0
    lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
    if n > 1:
        sz = ndimage.sum(op, lbl, range(1, n + 1))
        for k in range(1, n + 1):
            if sz[k - 1] < 3:
                out[lbl == k] = 0
    return out


# ------------------------------------------------------------------------------------------------- the spirit
def spirit_native(k, fade=1.0):
    """Codex's spirit frame k (1-4) on its 28 x 36 box (its float drawn in), and the same at `fade` of its size."""
    s = rgba(os.path.join(SPIRIT_DIR, f"spirit_float_{k}.png"))
    if fade >= 1.0:
        return s
    if fade <= 0:
        return np.zeros_like(s)
    ys, xs = np.nonzero(s[..., 3] > 0)
    piv = ((xs.min() + xs.max() + 1) / 2.0, (ys.min() + ys.max() + 1) / 2.0)
    pal = np.unique(s[s[..., 3] > 0][:, :3], axis=0).astype(float)
    small, (nx, ny) = PD.pixelate(s, fade, piv, OUTLINE, pal)
    out = np.zeros_like(s)
    r0, c0 = int(round(piv[1] - ny)), int(round(piv[0] - nx))
    paste_over(out, small, r0, c0)
    return out


SPIRIT2 = {}


def spirit2(k, fade=1.0):
    """The spirit frame brought to PPU once (its box's top-left on a grid corner)."""
    key = (k, round(fade, 3))
    if key not in SPIRIT2:
        SPIRIT2[key] = down2(spirit_native(k, fade), pivot=(0.0, 0.0))[0]
    return SPIRIT2[key]


def spirit_offset():
    """The spirit's box top-left from the head's top-left in the front design (rows, cols), and its box's offset from
    the spirit's own top-left (the box is 28 x 36; the spirit inside it)."""
    info = design_info()
    sp = rgba(os.path.join(HD, "front_spirit.png"))
    ys, xs = np.nonzero(sp[..., 3] > 0)
    hy, hx = info["head"]["front_at"]
    box = rgba(os.path.join(SPIRIT_DIR, "spirit_float_1.png"))
    by, bx = np.nonzero(box[..., 3] > 0)
    return (int(ys.min() - hy - by.min()), int(xs.min() - hx - bx.min()))


def shown(boy, r0, c0, k):
    """The share of spirit frame k at native (r0, c0) the boy leaves clear."""
    s = spirit_native(k)
    ys, xs = np.nonzero(s[..., 3] > 0)
    r, c = ys + r0, xs + c0
    ok = (r >= 0) & (r < boy.shape[0]) & (c >= 0) & (c < boy.shape[1])
    return float((boy[r[ok], c[ok], 3] == 0).sum()) / len(ys)


def idle_spirit_place():
    """The spirit box's native top-left in the idle (the front design's own place)."""
    info = design_info()
    x0 = int(round(I.PIV - info["front"]["standing_col"]))
    y0 = I.SOLE - info["front"]["soles"]
    hy, hx = info["head"]["front_at"]
    dy, dx = spirit_offset()
    return (y0 + hy + dy, x0 + hx + dx)


def spirit_places(boys, heads, back=0, loop=False):
    """Per frame: the spirit box's native top-left. It follows him a beat behind, the way a floating companion does:
    each frame it goes FOLLOW of the way from where it was to its place by him (SPIRIT_OFF from the head, `back`
    further back), starting from its idle place (a loop: from its own last place, three times round); then pushed back
    (left) while less than SPIRIT_SHOW of it shows past him."""
    dy, dx = spirit_offset()
    targets = [(hr + dy, hc + dx - back) for hr, hc in heads]
    n = len(targets)
    pos = np.array(idle_spirit_place(), float) if not loop else np.array(targets[-1], float)
    path = []
    for _ in range(3 if loop else 1):
        path = []
        for t in targets:
            pos = pos + FOLLOW * (np.array(t, float) - pos)
            path.append(pos.copy())
    out = []
    for i, (b, (r, c)) in enumerate(zip(boys, path)):
        r, c = int(round(r)), int(round(c))
        k = i % 4 + 1
        while shown(b, r, c, k) < SPIRIT_SHOW and c > -40:
            c -= 1
        out.append((r, c))
    return out


FOLLOW = 0.6


# ------------------------------------------------------------------------------------------------- the tags
def frame_heads(tag, n):
    meta = json.load(open(os.path.join(I.OUT, "frames.json"), encoding="utf-8"))
    out = []
    for k in range(1, n + 1):
        name = f"{tag}_{k}"
        if tag == "run" and "run_redo" in meta:          # tools/art/import_milio_run.py (the legs crossing)
            out.append(tuple(meta["run_redo"][k - 1]["head_at"]))
            continue
        if tag == "run":
            name = meta["run_order"][k - 1][0]
        out.append(tuple(meta["heads"][name]["at"]))
    return out


def action(tag):
    n = len(TIMING[tag])
    boys = [rgba(os.path.join(I.OUT, f"{tag}_{k}.png")) for k in range(1, n + 1)]
    heads = frame_heads(tag, n)
    if tag == "dead":
        p0 = spirit_places(boys[:1], heads[:1])[0]
        places = [(p0[0] + DEAD_SINK[i], p0[1]) for i in range(n)]
    else:
        places = spirit_places(boys, heads, back=RUN_BACK if tag == "run" else 0, loop=tag == "run")
    out = []
    for i, (b, head, (sr, sc), ms) in enumerate(zip(boys, heads, places, TIMING[tag])):
        a, corner = with_head(b, head)
        fade = DEAD_FADE[i] if tag == "dead" else 1.0
        if fade > 0:
            r2, c2 = to_grid(sr, sc, corner)
            paste_under(a, spirit2(i % 4 + 1, fade), r2, c2)
        out.append((tidy(a), corner, ms))
    return out


IDLE_HEAD = [None]


def idle_frames():
    """The front design (boy only) on the canvas, its head the design's (HEAD2), breathing; the spirit at its own place
    in the front design, flickering."""
    info = design_info()
    boy = rgba(os.path.join(HD, "front_boy.png"))
    can = np.zeros((I.ROWS, I.COLS, 4), np.uint8)
    x0 = int(round(I.PIV - info["front"]["standing_col"]))
    y0 = I.SOLE - info["front"]["soles"]
    paste_over(can, boy, y0, x0)
    hy, hx = info["head"]["front_at"]
    head = (y0 + hy, x0 + hx)
    a0, corner = with_head(can, head)
    IDLE_HEAD[0] = (to_grid(head[0], head[1], corner), corner)
    sr, sc = idle_spirit_place()
    waist = waist_row(a0)
    out = []
    for i, b in enumerate(BREATH):
        a = breathe(a0, waist, b)
        r2, c2 = to_grid(sr, sc, corner)
        paste_under(a, spirit2(i % 4 + 1), r2, c2)
        out.append((tidy(a), corner, IDLE_MS))
    return out


def waist_row(a):
    """The row under the sash (the teal band) in the idle's PPU frame: everything above it breathes."""
    idx = I.to_idx(a) if a.dtype == np.uint8 else a
    teal = np.isin(idx, [13, 19])
    rows = np.nonzero(teal.sum(1) >= 3)[0]
    ys = np.nonzero(a[..., 3] > 0)[0]
    lower = rows[rows > ys.min() + (ys.max() - ys.min()) * 0.45]
    return int(lower.max()) + 1 if len(lower) else int(ys.min() + (ys.max() - ys.min()) * 0.6)


def breathe(a, waist, k):
    """The squares above `waist` moved k rows up; the squares they uncover take the colour of the square under them."""
    if k == 0:
        return a.copy()
    out = a.copy()
    mask = np.zeros(a.shape[:2], bool)
    mask[:waist] = a[:waist, :, 3] > 0
    ys, xs = np.nonzero(mask)
    out[ys, xs] = 0
    out[ys - k, xs] = a[ys, xs]
    hole = (out[..., 3] == 0) & mask
    for y in sorted(set(np.nonzero(hole)[0]), reverse=True):
        for x in np.nonzero(hole[y])[0]:
            if y + 1 < a.shape[0] and out[y + 1, x, 3] > 0:
                out[y, x] = out[y + 1, x]
    return out


def hit_frames():
    info = design_info()
    side = rgba(os.path.join(HD, "side.png"))
    can = np.zeros((I.ROWS, I.COLS, 4), np.uint8)
    x0 = int(round(I.PIV - info["side"]["standing_col"]))
    y0 = I.SOLE - info["side"]["soles"]
    paste_over(can, side, y0, x0)
    hy, hx = info["head"]["side_at"]
    head = (y0 + hy, x0 + hx)
    sr, sc = spirit_places([can], [head])[0]
    out = []
    for i, (dx, flash, ms) in enumerate(HIT):
        b = np.roll(can, -dx, axis=1)
        a, corner = with_head(b, (head[0], head[1] - dx))
        r2, c2 = to_grid(sr, sc - dx, corner)
        paste_under(a, spirit2(i % 4 + 1), r2, c2)
        a = tidy(a)
        if flash:
            m = a[..., 3] > 0
            a[m, :3] = (a[m, :3].astype(int) * 0.45 + 255 * 0.55).astype(np.uint8)
        out.append((a, corner, ms))
    return out


# ------------------------------------------------------------------------------------------------- the sheets
def one_of(can, px, py, hw, hh, need=0.5):
    """The 1x frame (2 hw + 1 by 2 hh + 1, centred on (px, py)): every pixel the commonest colour of the squares under
    it, clear when fewer than `need` of them are drawn."""
    w1, h1 = 2 * hw + 1, 2 * hh + 1
    one = np.zeros((h1, w1, 4), np.uint8)
    for j in range(h1):
        ya, yb = py + (j - hh - 0.5) * PPU, py + (j - hh + 0.5) * PPU
        for i in range(w1):
            xa, xb = px + (i - hw - 0.5) * PPU, px + (i - hw + 0.5) * PPU
            blk = can[max(0, int(np.floor(ya + 0.5))):max(0, int(np.floor(yb + 0.5))),
                      max(0, int(np.floor(xa + 0.5))):max(0, int(np.floor(xb + 0.5)))].reshape(-1, 4)
            if not len(blk) or (blk[:, 3] > 0).sum() < need * len(blk):
                continue
            cols, n = np.unique(blk[blk[:, 3] > 0][:, :3], axis=0, return_counts=True)
            one[j, i, :3] = cols[n.argmax()]
            one[j, i, 3] = 255
    return one


def crop_hd(can, px, py, W, H):
    hx0, hy0 = int(round(px - W / 2.0)), int(round(py - H / 2.0))
    hd = np.zeros((H, W, 4), np.uint8)
    sx0, sy0 = max(0, hx0), max(0, hy0)
    sub = can[sy0:min(can.shape[0], hy0 + H), sx0:min(can.shape[1], hx0 + W)]
    hd[sy0 - hy0:sy0 - hy0 + sub.shape[0], sx0 - hx0:sx0 - hx0 + sub.shape[1]] = sub
    return hd


def down(can, corner):
    """The PPU canvas -> (the 1x frame centred on the pivot, the PPU frame round(PPU x its size)). The pivot: the
    standing column's middle (the grid corner the native pivot went to), FEET 1x rows above the ground line."""
    px, py = float(corner[0]), corner[1] - FEET * PPU
    ys, xs = np.nonzero(can[..., 3] > 0)
    hw = int(np.ceil(max(px - xs.min(), xs.max() + 1 - px) / PPU - 0.5))
    hh = int(np.ceil(max(py - ys.min(), ys.max() + 1 - py) / PPU - 0.5))
    one = G.complete_outline(one_of(can, px, py, hw, hh))[0]
    W, H = round((2 * hw + 1) * PPU), round((2 * hh + 1) * PPU)
    return one, crop_hd(can, px, py, W, H)


def strip_of(frames):
    H = max(h.shape[0] for h in frames)
    strip = np.zeros((H, sum(h.shape[1] + 1 for h in frames) - 1, 4), np.uint8)
    x = 0
    for h in frames:
        strip[:h.shape[0], x:x + h.shape[1]] = h
        x += h.shape[1] + 1
    return strip


def actions():
    out = {"idle": idle_frames(), "hit": hit_frames()}
    for tag in TIMING:
        out[tag] = action(tag)
    return {t: out[t] for t in ORDER}


def face_point(head_corner):
    """The champion_view face point (1x px from the pivot): the crown of the idle's head (HEAD2's first row at least
    half as wide as the head) and the head's middle 1.5 px ahead (text-audio.md: base champions' face sits at the crown).
    head_corner: HEAD2's top-left (row, col) on the idle's first frame and that frame's pivot corner (x, y)."""
    (r2, c2), corner = head_corner
    op = HEAD2[..., 3] > 0
    w = op.sum(1)
    crown = next(y for y in range(op.shape[0]) if w[y] >= op.shape[1] / 2)
    xs = np.nonzero(op[crown:crown + 8].any(0))[0]
    mid = c2 + (xs.min() + xs.max() + 1) / 2.0
    fx = (mid - corner[0]) / PPU + 1.5
    fy = (r2 + crown - corner[1]) / PPU
    return int(round(fx)), int(round(fy))


PIN_FILL = 30                     # after the restyle: its grown outline pinches the narrow gaps (an arm off the side, a
                                  # leg off the hip) shut into pockets - those up to this size are filled


def fill_holes(a, most, shade=True):
    """Enclosed holes of `most` squares or fewer filled: up to 3 with the colour round them, the rest with the darkest
    colour round them that is not the outline. -> squares filled."""
    op = a[..., 3] > 0
    holes = ndimage.binary_fill_holes(op) & ~op
    lbl, n = ndimage.label(holes)
    done = 0
    for k in range(1, n + 1):
        m = lbl == k
        if m.sum() > most:
            continue
        ring = ndimage.binary_dilation(m, structure=np.ones((3, 3))) & op
        cols, cnt = np.unique(a[ring][:, :3], axis=0, return_counts=True)
        if m.sum() <= 3 or not shade:
            a[m, :3] = cols[cnt.argmax()]
        else:
            lit = [c for c in cols if tuple(int(v) for v in c) != OUTLINE]
            a[m, :3] = min(lit, key=lambda c: int(c.astype(int).sum())) if lit else OUTLINE
        a[m, 3] = 255
        done += int(m.sum())
    return done


def pinholes():
    """After tools/art/ppu_restyle.py: the restyled strips' (assets/source/ppu/milio_<tag>.png, what ppu_hd.py reads)
    enclosed holes up to PIN_FILL squares filled (fill_holes), and the 1x sheet's up to 2 pixels (memory gap-check);
    then the effects drawn into his frames go on (bake)."""
    src = os.path.join(ROOT, "assets", "source", "ppu")
    total = 0
    hds = {}
    for tag in ORDER:
        path = os.path.join(src, f"milio_{tag}.png")
        meta = json.load(open(os.path.join(src, f"milio_{tag}.json"), encoding="utf-8"))
        strip = np.asarray(Image.open(path).convert("RGBA")).copy()
        x, frames = 0, []
        for W, H in meta["sizes"]:
            f = strip[:H, x:x + W].copy()
            total += fill_holes(f, PIN_FILL)
            frames.append(f)
            x += W + 1
        hds[tag] = frames
    import ppu_hd as P
    sheet = P.read_sheet(STEM)
    n1 = 0
    for tag in ORDER:
        for a, _ in sheet[tag]:
            n1 += fill_holes(a, 2, shade=False)
    print(f"milio: {total} squares of the restyled frames and {n1} 1x pixels filled")
    print(f"milio: {bake(hds, sheet)} pictures laid into his frames")
    for tag in ORDER:
        Image.fromarray(strip_of(hds[tag])).save(os.path.join(src, f"milio_{tag}.png"))
        with open(os.path.join(src, f"milio_{tag}.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"sizes": [[a.shape[1], a.shape[0]] for a in hds[tag]]}, f)
    G.write_sheet(STEM, sheet)


BAKE_DIR = os.path.join(I.SRC, "fx_bake")
BAKE_CELLS = os.path.join(I.SRC, "fx_bake_cells.json")


def bake(hds, sheet):
    """tools/art/import_milio_fx.py's pictures for his frames (assets/source/milio/fx_bake/<name>_<k>.png on the guide
    canvas of fx_bake_cells.json, drawn by Codex on his finished dense frames at this PPU) laid over the restyled frames -
    after the restyle's outline, so they get none; a frame they reach out of is grown alike at both ends (its centre,
    the pivot, kept). The 1x frame (the fallback) takes each pixel's commonest colour of the picture's squares under it
    where half of them are drawn, inside its own box (league_kindred's rig_kindred.bake)."""
    if not os.path.isfile(BAKE_CELLS):
        return 0
    with open(BAKE_CELLS, encoding="utf-8") as f:
        cells = json.load(f)
    n = 0
    for key, c in cells.items():
        path = os.path.join(BAKE_DIR, key + ".png")
        if not os.path.isfile(path):
            continue
        name, k = key.rsplit("_", 1)
        k = int(k)
        tag = c["into"].split()[0][len("hd_"):]
        if abs(c.get("ppu", PPU) - PPU) > 1e-6:
            sys.exit(f"{key}: drawn at PPU {c.get('ppu')}, the frames are at {PPU}: redo the effects pack")
        ov = rgba(path)
        x0, y0, W, H = c["frame"]
        f = hds[tag][k - 1]
        if (f.shape[1], f.shape[0]) != (W, H):
            sys.exit(f"{key}: {tag} frame {k} is {f.shape[1]}x{f.shape[0]}, its guide's {W}x{H}: the frames changed "
                     "since the effects pack (tools/art/pack_milio_fx.py)")
        ys, xs = np.nonzero(ov[..., 3] > 0)
        if not len(xs):
            continue
        fx, fy = xs - x0, ys - y0
        colours = ov[ys, xs]
        gx = int(max(0, -fx.min(), fx.max() + 1 - W))
        gy = int(max(0, -fy.min(), fy.max() + 1 - H))
        if gx or gy:
            f = np.pad(f, ((gy, gy), (gx, gx), (0, 0)))
        px, py = fx + gx, fy + gy
        f[py, px] = colours
        hds[tag][k - 1] = f
        a = sheet[tag][k - 1][0]
        h1, w1 = a.shape[:2]
        i = np.floor((fx + 0.5 - W / 2.0) / PPU + w1 / 2.0).astype(int)
        j = np.floor((fy + 0.5 - H / 2.0) / PPU + h1 / 2.0).astype(int)
        inside = (i >= 0) & (i < w1) & (j >= 0) & (j < h1)
        cell = {}
        for ii, jj, col in zip(i[inside], j[inside], colours[inside]):
            cell.setdefault((jj, ii), []).append(tuple(int(v) for v in col[:3]))
        for (jj, ii), cols in cell.items():
            if len(cols) < 0.5 * PPU * PPU:
                continue
            vals, cnt = np.unique(np.array(cols), axis=0, return_counts=True)
            a[jj, ii, :3] = vals[cnt.argmax()]
            a[jj, ii, 3] = 255
        n += 1
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every tag's PPU frames at 3x here")
    ap.add_argument("--pinholes", action="store_true",
                    help="only fill the holes of the restyled strips (after ppu_restyle.py, before ppu_hd.py)")
    a = ap.parse_args()
    if a.pinholes:
        pinholes()
        return
    acts = actions()
    sheet = {}
    os.makedirs(ORIG, exist_ok=True)
    for tag, frames in acts.items():
        ones, hds = [], []
        for can, corner, t in frames:
            one, hd = down(can, corner)
            ones.append((one, float(t)))
            hds.append(hd)
        sheet[tag] = ones
        Image.fromarray(strip_of(hds)).save(os.path.join(ORIG, f"milio_{tag}.png"))
        with open(os.path.join(ORIG, f"milio_{tag}.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"sizes": [[h.shape[1], h.shape[0]] for h in hds], "ppu": PPU}, f)
        if a.review:
            os.makedirs(a.review, exist_ok=True)
            Z = 3
            w = max(h.shape[1] for h in hds)
            hgt = max(h.shape[0] for h in hds)
            big = Image.new("RGBA", (len(hds) * (w + 4) * Z, hgt * Z), (96, 112, 96, 255))
            for j, h in enumerate(hds):
                big.alpha_composite(Image.fromarray(h).resize((h.shape[1] * Z, h.shape[0] * Z), Image.NEAREST),
                                    (j * (w + 4) * Z, (hgt - h.shape[0]) * Z))
            big.convert("RGB").save(os.path.join(a.review, f"milio_{tag}.png"))
    w, h = G.write_sheet(STEM, sheet)
    print(f"league/champions/league_milio#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))
    print("face point (crown):", face_point(IDLE_HEAD[0]))


if __name__ == "__main__":
    main()
