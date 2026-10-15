#!/usr/bin/env python3
"""league_jayce's frames: Codex's step-2 strips (both forms) + the designs -> the dense strips and the 1x sheet.

    python tools/art/rig_jayce.py --prepare <delivery>/jayce-strips      (once: Codex's 1x frames -> codex_strips/)
    python tools/art/rig_jayce.py [--review DIR]
    python tools/art/rig_jayce.py --pinholes                             (after ppu_restyle.py --hero jayce)

The delivery (Codex, 2026-10-15, outputs/jayce_strips_done.zip): 71 frames drawn by image_gen after the pack's
skeletons (tools/art/pack_jayce_strips.py), each read back by Codex on the pack's 5-px grid into the design's 41
colours (<frame>_1x.png, 307 x 204, the soles on row SOLE, the standing point on column PIV; its raw drafts in raw/).
Those 1x frames are this tool's input (kept in assets/source/jayce/codex_strips). Codex's own notes: the head is not
the design's square for square and the size drifts (HANDOFF), so here, Milio's way (tools/art/rig_milio.py):
  * the size: the design's head (hd/head.png, memory one-face-all-frames) matched in every frame over SCALES (a masked
    colour distance, around the frame's face - its largest skin piece); one scale per action (the median of its frames,
    SCALE_FIX overriding), the frames brought back to the design's size by pixel_down.pixelate when it is off by
    more than SCALE_TOL;
  * one face: the design's head brought down once (HEAD2) goes back where the head matched after the downscale,
    Codex's own head squares cleared under it (an arm crossing it stays in front); NO_HEAD frames keep Codex's head
    (the body lying: dead 3-6);
  * the density: the frames are on the design's grid (98 squares crown to soles = 38 game rows, NATIVE a game pixel)
    and brought to the user's PPU 1.5 here (pixelate on a grid through the pivot, the design's colours), so
    ppu_restyle.py changes no density;
  * idle / c_idle: the hammer / cannon front design breathing (everything above the waist up BREATH squares at PPU);
    hit / c_hit: the side design moved HIT_DX back, a white flash on the first frame;
  * tidy: the outline closed, holes up to HOLE_FILL filled, loose specks off.
Writes assets/source/ppu/orig/jayce_<tag>.png / .json (the frames at PPU, each round(PPU x its 1x frame) round the
pivot) and league/champions/league_jayce#sheet.png / #anim.fanim (the 1x tags, the fallback without league.dll).
Then tools/art/ppu_restyle.py --hero jayce, python tools/art/rig_jayce.py --pinholes and tools/art/ppu_hd.py --hero jayce.
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
import pixel_down as PD  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "jayce")
HD = os.path.join(SRC, "hd")
CODEX = os.path.join(SRC, "codex_strips")
STEM = os.path.join(ROOT, "league", "champions", "league_jayce")
ORIG = os.path.join(ROOT, "assets", "source", "ppu", "orig")
COLS, ROWS = 307, 204             # the pack's canvas in design squares
PIV, SOLE = 120, 196              # the standing column and the soles' row
PIVOT = (PIV + 0.5, SOLE + 1)     # the native pivot: the standing column's middle on the ground line
INFO = json.load(open(os.path.join(HD, "design.json"), encoding="utf-8"))
NATIVE = INFO["rows"] / INFO["game_rows"]     # design squares a game pixel (98 / 38)
PPU = 1.5                         # the user's pick
K = PPU / NATIVE
FEET = 11                         # 1x rows from the pivot down to the ground row (the pack's 128-canvas heroes)

HAMMER = {"run": 8, "attack": 6, "skill": 6, "skill2": 6, "w_cast": 4, "tf_c": 4, "dead": 6}
CANNON = {"c_run": 8, "c_attack": 4, "c_skill": 5, "c_skill2": 4, "ult": 6, "tf_h": 4}
ORDER = ["idle", "run", "attack", "skill", "skill2", "w_cast", "tf_c", "hit", "dead",
         "c_idle", "c_run", "c_attack", "c_skill", "c_skill2", "ult", "tf_h", "c_hit"]
SCALES = [0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15]
SCALE_TOL = 9.0                   # never: Codex drew the heads 0.85-1.15 of the design's but the bodies at its size
                                  # (w_cast / ult bodies stand as tall as the design with 0.9 heads) - so the frames
                                  # keep their size and only the head is replaced
SCALE_FIX = {}                    # tag -> scale, where the median head match is wrong
NO_HEAD = {("dead", 3), ("dead", 4), ("dead", 5), ("dead", 6)}
IDLE_MS = 150
BREATH = [0, 0, 1, 1, 1, 1, 0, 0]
HIT_DX = 4
HIT = [(HIT_DX, True, 90), (HIT_DX // 2, False, 120)]
HOLE_FILL = 12


def rgba(path):
    return np.asarray(Image.open(path).convert("RGBA")).copy()


def palette():
    cols = []
    for n in ("hammer_front", "hammer_side", "cannon_front", "cannon_side"):
        a = rgba(os.path.join(HD, n + ".png"))
        cols.append(a[a[..., 3] > 0][:, :3])
    pal = np.unique(np.concatenate(cols), axis=0)
    return pal[np.argsort(pal.astype(int).sum(1), kind="stable")]


PAL = palette()
PALF = PAL.astype(float)
OUTLINE = tuple(int(v) for v in PAL[0])
HEAD = rgba(os.path.join(HD, "head.png"))


def is_skin(a):
    rgb = a[..., :3].astype(int)
    return (a[..., 3] > 0) & (rgb[..., 0] > 170) & (rgb[..., 0] > rgb[..., 2] + 60) & (rgb[..., 1] > 90) & \
        (rgb[..., 1] < 200) & (rgb[..., 0] - rgb[..., 1] > 30)


# ------------------------------------------------------------------------------------------------- the delivery
def prepare(delivery):
    os.makedirs(CODEX, exist_ok=True)
    cells = json.load(open(os.path.join(delivery, "cells.json"), encoding="utf-8"))
    for f in cells["frames"]:
        name = f["file"][:-4]
        shutil.copyfile(os.path.join(delivery, name + "_1x.png"), os.path.join(CODEX, name + ".png"))
    meta = {f["file"][len("jayce_"):-4]: f["ms"] for f in cells["frames"]}
    with open(os.path.join(CODEX, "timing.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(meta, fh, indent=0)
    print(len(meta), "frames ->", CODEX)


def frame(tag, k):
    return rgba(os.path.join(CODEX, f"jayce_{tag}_{k}.png"))


def timing():
    return json.load(open(os.path.join(CODEX, "timing.json"), encoding="utf-8"))


# ------------------------------------------------------------------------------------------------- the head
def scaled_head(s):
    im = Image.fromarray(HEAD)
    if s != 1.0:
        im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.NEAREST)
    t = np.asarray(im).astype(float)
    return t, t[..., 3] > 0


def head_match(a, scales=SCALES):
    """-> (score, scale, row, col) of the design's head in frame a, searched round its face (the largest skin piece)."""
    sk = is_skin(a)
    lbl, n = ndimage.label(sk)
    if not n:
        return (1e18, 1.0, 0, 0)
    sz = ndimage.sum(sk, lbl, range(1, n + 1))
    face = lbl == (int(np.argmax(sz)) + 1)
    fy, fx = np.nonzero(face)
    hs = is_skin(HEAD)
    hy, hx = np.nonzero(hs)
    af = a.astype(float)
    op = a[..., 3] > 0
    best = (1e18, 1.0, 0, 0)
    for s in scales:
        t, m = scaled_head(s)
        h, w = m.shape
        # the template's face top-left -> the frame's face top-left, +- 6
        cy, cx = fy.min() - hy.min() * s, fx.min() - hx.min() * s
        for y in range(int(cy) - 6, int(cy) + 7):
            for x in range(int(cx) - 8, int(cx) + 9):
                if y < 0 or x < 0 or y + h > a.shape[0] or x + w > a.shape[1]:
                    continue
                win = af[y:y + h, x:x + w]
                wm = op[y:y + h, x:x + w]
                both = m & wm
                if both.sum() < 0.6 * m.sum():
                    continue
                d = ((win[..., :3] - t[..., :3]) ** 2).sum(-1)[both].mean()
                d += 20000 * (m & ~wm).sum() / m.sum()
                if d < best[0]:
                    best = (d, s, y, x)
    return best


def rescale(a, s):
    """a drawn s times the design's size -> the design's size, round the pivot."""
    out, (nx0, ny0) = PD.pixelate(a, 1.0 / s, PIVOT, OUTLINE, PALF)
    can = np.zeros_like(a)
    r0, c0 = int(round(PIVOT[1] - ny0)), int(round(PIVOT[0] - nx0))
    paste_over(can, out, r0, c0)
    return can


# ------------------------------------------------------------------------------------------------- the grid
def down2(a, pivot=PIVOT):
    out, (nx0, ny0) = PD.pixelate(a, K, pivot, OUTLINE, PALF)
    return out, (nx0, ny0)


def to_grid(r, c, corner):
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


HEAD2 = down2(HEAD, pivot=(0.0, 0.0))[0]      # the design's head on its own grid (its top-left on a corner)


def design_place(match):
    """Codex's head (scale s, top-left y, x) -> the design head's top-left: the chin's row and the head's middle kept."""
    s, y, x = match
    h, w = HEAD.shape[:2]
    hs, ws = round(h * s), round(w * s)
    return int(round(y + hs - h)), int(round(x + ws / 2.0 - w / 2.0))


def codex_head_mask(shape, match):
    s, y, x = match
    _, m = scaled_head(s)
    out = np.zeros(shape, bool)
    ys, xs = np.nonzero(m)
    r, c = ys + y, xs + x
    ok = (r >= 0) & (r < shape[0]) & (c >= 0) & (c < shape[1])
    out[r[ok], c[ok]] = True
    return out


def with_head(native, head, old=None):
    """The native frame without its head (the design's head squares - and Codex's own head where `old` gives it -
    cleared, Codex's arms / weapon over it kept: the squares unlike the template that are not hair or skin) brought
    to PPU, and HEAD2 pasted on its square - under whatever crosses it."""
    hr, hc = head
    hm = np.zeros(native.shape[:2], bool)
    ys, xs = np.nonzero(HEAD[..., 3] > 0)
    r, c = ys + hr, xs + hc
    ok = (r >= 0) & (r < hm.shape[0]) & (c >= 0) & (c < hm.shape[1])
    hm[r[ok], c[ok]] = True
    tpl = np.zeros_like(native)
    tpl[r[ok], c[ok]] = HEAD[ys[ok], xs[ok]]
    rgb = native[..., :3].astype(int)
    hairy = is_skin(native) | ((rgb[..., 0] < 130) & (rgb[..., 0] > rgb[..., 2]) & (rgb.sum(-1) < 260)) | \
        (rgb.sum(-1) < 90)
    cross = hm & (native[..., 3] > 0) & np.any(native[..., :3] != tpl[..., :3], axis=-1) & ~hairy
    body = native.copy()
    body[hm & ~cross] = 0
    if old is not None:
        om = ndimage.binary_dilation(codex_head_mask(hm.shape, old), iterations=1)
        body[om & hairy & ~cross] = 0
    # Codex's own head reaching out of the template (hair a square wider, the old ear): its hair / skin squares
    # touching the template's box within 2 squares cleared too
    ring = ndimage.binary_dilation(hm, iterations=2) & ~hm
    body[ring & hairy & (native[..., 3] > 0) & ~cross] = 0
    small, corner = down2(body)
    am = np.zeros_like(native)
    am[cross] = (255, 255, 255, 255)
    cross2 = down2(am)[0][..., 3] > 0
    r2, c2 = to_grid(hr, hc, corner)
    out = small.copy()
    paste_over(out, HEAD2, r2, c2, keep=cross2 & (small[..., 3] > 0))
    return out, corner


def tidy(a):
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
        else:
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


# ------------------------------------------------------------------------------------------------- the frames
MATCH = {}


def matched(tag, n):
    """The tag's frames at the design's size and where the head sits in each: (frames, heads, scale)."""
    raw = [frame(tag, k) for k in range(1, n + 1)]
    ms = [head_match(a) for a in raw]
    s = SCALE_FIX.get(tag, float(np.median([m[1] for m in ms])))
    if abs(s - 1.0) > SCALE_TOL:
        raw = [rescale(a, s) for a in raw]
        ms = [head_match(a, scales=[1.0]) for a in raw]
    MATCH[tag] = {"scale": s, "codex_heads": [[m[1], int(m[2]), int(m[3])] for m in ms],
                  "scores": [round(m[0]) for m in ms]}
    return raw, [(m[1], m[2], m[3]) for m in ms], s


def action(tag, n, ms):
    frames, heads, _ = matched(tag, n)
    out = []
    for k, (a, head) in enumerate(zip(frames, heads), 1):
        if (tag, k) in NO_HEAD:
            small, corner = down2(a)
        else:
            small, corner = with_head(a, design_place(head), old=head)
        out.append((tidy(small), corner, ms[f"{tag}_{k}"]))
    return out


def on_canvas(name):
    d = INFO["designs"][name]
    a = rgba(os.path.join(HD, name + ".png"))
    can = np.zeros((ROWS, COLS, 4), np.uint8)
    x0 = int(round(PIV - d["standing_col"]))
    y0 = SOLE - d["soles"]
    paste_over(can, a, y0, x0)
    hy, hx = d["head_at"]
    return can, (y0 + hy, x0 + hx)


IDLE_HEAD = {}


def idle_frames(form):
    can, head = on_canvas(f"{form}_front")
    a0, corner = with_head(can, head)
    IDLE_HEAD[form] = (to_grid(head[0], head[1], corner), corner)
    waist = waist_row(a0)
    return [(tidy(breathe(a0, waist, b)), corner, IDLE_MS) for b in BREATH]


def waist_row(a):
    """The belt (the brown band with the gold buckle) in the idle's PPU frame: everything above it breathes - the
    row 55 % of the way down from the crown to the soles."""
    ys = np.nonzero(a[..., 3] > 0)[0]
    return int(ys.min() + (ys.max() - ys.min()) * 0.55)


def breathe(a, waist, k):
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


def hit_frames(form):
    can, head = on_canvas(f"{form}_side")
    out = []
    for dx, flash, ms in HIT:
        b = np.roll(can, -dx, axis=1)
        a, corner = with_head(b, (head[0], head[1] - dx))
        a = tidy(a)
        if flash:
            m = a[..., 3] > 0
            a[m, :3] = (a[m, :3].astype(int) * 0.45 + 255 * 0.55).astype(np.uint8)
        out.append((a, corner, ms))
    return out


# ------------------------------------------------------------------------------------------------- the sheets
def one_of(can, px, py, hw, hh, need=0.5):
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
    ms = timing()
    out = {"idle": idle_frames("hammer"), "c_idle": idle_frames("cannon"), "hit": hit_frames("hammer"),
           "c_hit": hit_frames("cannon")}
    for tag, n in list(HAMMER.items()) + list(CANNON.items()):
        out[tag] = action(tag, n, ms)
    return {t: out[t] for t in ORDER}


def face_point(head_corner):
    (r2, c2), corner = head_corner
    op = HEAD2[..., 3] > 0
    w = op.sum(1)
    crown = next(y for y in range(op.shape[0]) if w[y] >= op.shape[1] / 2)
    xs = np.nonzero(op[crown:crown + 8].any(0))[0]
    mid = c2 + (xs.min() + xs.max() + 1) / 2.0
    fx = (mid - corner[0]) / PPU + 1.5
    fy = (r2 + crown - corner[1]) / PPU
    return int(round(fx)), int(round(fy))


PIN_FILL = 30


def fill_holes(a, most, shade=True):
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
    src = os.path.join(ROOT, "assets", "source", "ppu")
    total = 0
    hds = {}
    for tag in ORDER:
        meta = json.load(open(os.path.join(src, f"jayce_{tag}.json"), encoding="utf-8"))
        strip = rgba(os.path.join(src, f"jayce_{tag}.png"))
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
    print(f"jayce: {total} squares of the restyled frames and {n1} 1x pixels filled")
    for tag in ORDER:
        Image.fromarray(strip_of(hds[tag])).save(os.path.join(src, f"jayce_{tag}.png"))
        with open(os.path.join(src, f"jayce_{tag}.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"sizes": [[a.shape[1], a.shape[0]] for a in hds[tag]]}, f)
    G.write_sheet(STEM, sheet)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prepare", metavar="DELIVERY")
    ap.add_argument("--review", help="write every tag's PPU frames at 3x here")
    ap.add_argument("--pinholes", action="store_true")
    a = ap.parse_args()
    if a.prepare:
        prepare(a.prepare)
        return
    if a.pinholes:
        pinholes()
        return
    acts = actions()
    with open(os.path.join(CODEX, "match.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(MATCH, fh, indent=1)
    for tag, m in MATCH.items():
        print(f"{tag}: head scales {[h[0] for h in m['codex_heads']]} scores {m['scores']}")
    sheet = {}
    os.makedirs(ORIG, exist_ok=True)
    for tag, frames in acts.items():
        ones, hds = [], []
        for can, corner, t in frames:
            one, hd = down(can, corner)
            ones.append((one, float(t)))
            hds.append(hd)
        sheet[tag] = ones
        Image.fromarray(strip_of(hds)).save(os.path.join(ORIG, f"jayce_{tag}.png"))
        with open(os.path.join(ORIG, f"jayce_{tag}.json"), "w", encoding="utf-8", newline="\n") as f:
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
            big.convert("RGB").save(os.path.join(a.review, f"jayce_{tag}.png"))
    w, h = G.write_sheet(STEM, sheet)
    print(f"league/champions/league_jayce#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))
    print("face point (crown):", face_point(IDLE_HEAD["hammer"]))


if __name__ == "__main__":
    main()
