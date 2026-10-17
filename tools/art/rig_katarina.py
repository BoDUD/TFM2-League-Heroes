#!/usr/bin/env python3
"""league_katarina's frames: Codex's step-2 strips + the designs -> the dense strips and the 1x sheet (rig_jayce.py's way).

    python tools/art/rig_katarina.py --prepare <delivery>/katarina-strips   (once: Codex's 1x frames -> codex_strips/)
    python tools/art/rig_katarina.py [--review DIR]
    python tools/art/rig_katarina.py --pinholes                            (after ppu_restyle.py --hero katarina)

The delivery (Codex, outputs/katarina_strips_done.zip): 42 frames drawn by image_gen after the pack's skeletons
(tools/art/pack_katarina_strips.py), each read back by Codex on the pack's 8-px grid into the design's colours
(<frame>_1x.png, 192 x 128, the soles on row SOLE, the standing point on column PIV; its raw drafts in raw/). Those 1x
frames are this tool's input (kept in assets/source/katarina/codex_strips, the pack's cells.json beside them):
  * the size: the design's head (hd/head.png, memory one-face-all-frames) matched in every frame over SCALES; one scale
    per action (the median), the frames brought back to the design's size when it is off by more than SCALE_TOL;
  * one face: the design's head brought down once (HEAD2) goes back where the head matched, Codex's own head squares
    cleared under it (a dagger or an arm crossing it stays in front); NO_HEAD frames keep Codex's head (lying dead);
  * the density: the frames are on the design's grid (68 squares crown to soles = 38 game rows, NATIVE a game pixel)
    and brought to the user's PPU 1.5 here (pixelate on a grid through the pivot, the design's colours);
  * idle: the front design breathing (everything above the waist up BREATH squares at PPU); hit: the side design moved
    HIT_DX back, a white flash on the first frame;
  * tidy: the outline closed, holes up to HOLE_FILL filled, loose specks off.
Writes assets/source/ppu/orig/katarina_<tag>.png / .json (the frames at PPU, each round(PPU x its 1x frame) round the
pivot) and league/champions/league_katarina#sheet.png / #anim.fanim (the 1x tags, the fallback without league.dll).
Then tools/art/ppu_restyle.py --hero katarina, rig_katarina.py --pinholes and tools/art/ppu_hd.py --hero katarina.
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
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile: long paths
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import pixel_down as PD  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "katarina")
HD = os.path.join(SRC, "hd")
CODEX = os.path.join(SRC, "codex_strips")
STEM = os.path.join(ROOT, "league", "champions", "league_katarina")
ORIG = os.path.join(ROOT, "assets", "source", "ppu", "orig")
COLS, ROWS = 192, 128             # the pack's canvas in design squares
PIV, SOLE = 90, 118               # the standing column and the soles' row
PIVOT = (PIV + 0.5, SOLE + 1)     # the native pivot: the standing column's middle on the ground line
INFO = json.load(open(os.path.join(HD, "design.json"), encoding="utf-8"))
NATIVE = INFO["rows"] / INFO["game_rows"]     # design squares a game pixel (68 / 38)
PPU = 1.5                         # the user's pick: 1.5 first, then 「脸部用PPU调清晰点吧」 -> the design's own density
                                  # 1.7895 (68 / 38, the frames as Codex drew them); then 「卡特琳娜太高清了 降低点像素」,
                                  # shown 1.79 / 1.6 / 1.5 / 1.4 side by side: 「卡特琳娜用 PPU 1.5」
K = PPU / NATIVE
FEET = 11                         # 1x rows from the pivot down to the ground row (the pack's 128-canvas heroes)

TAGS = {"run": 8, "attack": 5, "skill": 5, "skill2": 5, "blink": 3, "spin": 4, "ult": 6, "dead": 6}
ORDER = ["idle", "run", "attack", "skill", "skill2", "blink", "spin", "ult", "hit", "dead"]
SCALES = [0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15]
SCALE_TOL = 9.0                   # never (league_jayce: Codex drew the heads 0.85-1.15 of the design's, the bodies at its size)
                                  # (w_cast / ult bodies stand as tall as the design with 0.9 heads) - so the frames
                                  # keep their size and only the head is replaced
SCALE_FIX = {}                    # tag -> scale, where the median head match is wrong
NO_HEAD = {("dead", 4), ("dead", 5), ("dead", 6)}
DROP = {}                         # (tag, k) -> native rows down (feet floating over the ground)
SHAFT = {}
IDLE_MS = 150
BREATH = [0, 0, 1, 1, 1, 1, 0, 0]
HIT_DX = 4
HIT = [(HIT_DX, True, 90), (HIT_DX // 2, False, 120)]
HOLE_FILL = 12
CROSS_MIN = 6


def rgba(path):
    return np.asarray(Image.open(path).convert("RGBA")).copy()


def palette():
    cols = []
    for n in ("front", "side"):
        a = rgba(os.path.join(HD, n + ".png"))
        cols.append(a[a[..., 3] > 0][:, :3])
    pal = np.unique(np.concatenate(cols), axis=0)
    return pal[np.argsort(pal.astype(int).sum(1), kind="stable")]


PAL = palette()
PALF = PAL.astype(float)
OUTLINE = tuple(int(v) for v in PAL[0])
HEAD = rgba(os.path.join(HD, "head.png"))


def snap1(c):
    return PAL[int(((PALF - np.asarray(c, float)) ** 2).sum(1).argmin())]


def is_skin(a):
    rgb = a[..., :3].astype(int)
    return (a[..., 3] > 0) & (rgb[..., 0] > 170) & (rgb[..., 0] > rgb[..., 2] + 30) & (rgb[..., 1] > 110) & \
        (rgb[..., 1] < 225) & (rgb[..., 0] - rgb[..., 1] > 20)


def is_hair(a):
    """Her crimson hair, light to wine."""
    rgb = a[..., :3].astype(int)
    return (a[..., 3] > 0) & (rgb[..., 0] > rgb[..., 1] + 75) & (rgb[..., 0] > rgb[..., 2] + 60)


# ------------------------------------------------------------------------------------------------- the delivery
def prepare(delivery):
    os.makedirs(CODEX, exist_ok=True)
    pack = os.path.join(delivery, "cells.json")
    if not os.path.isfile(pack):              # Codex's delivery carries only the frames: the pack's own table
        pack = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "kt_packs", "katarina_strips_pack", "cells.json")
    cells = json.load(open(pack, encoding="utf-8"))
    shutil.copyfile(pack, os.path.join(CODEX, "cells.json"))
    for f in cells["frames"]:
        name = f["file"][:-4]
        shutil.copyfile(os.path.join(delivery, name + "_1x.png"), os.path.join(CODEX, name + ".png"))
    meta = {f["file"][len("katarina_"):-4]: f["ms"] for f in cells["frames"]}
    with open(os.path.join(CODEX, "timing.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(meta, fh, indent=0)
    print(len(meta), "frames ->", CODEX)


def frame(tag, k):
    return rgba(os.path.join(CODEX, f"katarina_{tag}_{k}.png"))


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
    """a drawn s times the design's size -> the design's size, round the pivot (pixelate to shrink; to enlarge,
    nearest neighbour - pixelate leaves cells without a pixel there: clear seams)."""
    if s < 1.0:
        H, W = a.shape[:2]
        k = 1.0 / s
        ys = np.floor((np.arange(H) + 0.5 - PIVOT[1]) / k + PIVOT[1]).astype(int)
        xs = np.floor((np.arange(W) + 0.5 - PIVOT[0]) / k + PIVOT[0]).astype(int)
        ok = (ys[:, None] >= 0) & (ys[:, None] < H) & (xs[None, :] >= 0) & (xs[None, :] < W)
        out = np.zeros_like(a)
        out[ok] = a[np.clip(ys, 0, H - 1)[:, None], np.clip(xs, 0, W - 1)[None, :]][ok]
        return out
    out, (nx0, ny0) = PD.pixelate(a, 1.0 / s, PIVOT, OUTLINE, PALF)
    can = np.zeros_like(a)
    r0, c0 = int(round(PIVOT[1] - ny0)), int(round(PIVOT[0] - nx0))
    paste_over(can, out, r0, c0)
    return can


# ------------------------------------------------------------------------------------------------- the grid
LIGHT = 600                       # r + g + b over this: the cream fur collar, eye whites, the shafts' light rows
LIGHT_SHARE = 0.34                # a PPU square at least this much light in the native frame turns light: pixelate's
                                  # mean and dark rules eat thin light lines (league_jayce's fur crescent; here the daggers' silver edges) (review
                                  # round 1: a white "+" in c_idle, dark brown in c_hit)


def down2(a, pivot=PIVOT):
    if abs(K - 1.0) < 1e-3:                   # PPU = the design's density: no resampling, the frame as drawn
        return a.copy(), (float(pivot[0]), float(pivot[1]))
    out, (nx0, ny0) = PD.pixelate(a, K, pivot, OUTLINE, PALF)
    H, W = a.shape[:2]
    c = 1.0 / K
    px, py = pivot
    cx = np.floor((np.arange(W) + 0.5 - px) / c).astype(int) + nx0
    cy = np.floor((np.arange(H) + 0.5 - py) / c).astype(int) + ny0
    Hn, Wn = out.shape[:2]
    ok_x, ok_y = (cx >= 0) & (cx < Wn), (cy >= 0) & (cy < Hn)
    rgb = a[..., :3].astype(int)
    # only the fur's creams and whites (grey-ish: little spread between the channels), not the golds, the muzzle
    # rings' lights or the shafts (review round 2: the rule lit inner outlines all over)
    light = (a[..., 3] > 0) & (rgb.sum(-1) > LIGHT) & (rgb.max(-1) - rgb.min(-1) < 60)
    if light.any():
        cell = (cy[:, None] * Wn + cx[None, :])
        valid = ok_y[:, None] & ok_x[None, :]
        tot = np.bincount(cell[valid], minlength=Hn * Wn).reshape(Hn, Wn)
        n = np.bincount(cell[valid & light], minlength=Hn * Wn).reshape(Hn, Wn)
        isline = np.all(out[..., :3] == np.array(OUTLINE, np.uint8), axis=-1)
        turn = (n >= LIGHT_SHARE * np.maximum(tot, 1)) & (out[..., 3] > 0) &             (out[..., :3].astype(int).sum(-1) <= LIGHT) & ~isline
        if turn.any():
            ys, xs = np.nonzero(light & valid)
            keys = cy[ys] * Wn + cx[xs]
            for k in np.unique(cell[valid & light]):
                r, q = divmod(int(k), Wn)
                if not turn[r, q]:
                    continue
                cols, cnt = np.unique(a[ys[keys == k], xs[keys == k], :3], axis=0, return_counts=True)
                out[r, q, :3] = snap1(cols[cnt.argmax()])
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
    hairy = is_skin(native) | is_hair(native) | (rgb.sum(-1) < 90)
    cross = hm & (native[..., 3] > 0) & np.any(native[..., :3] != tpl[..., :3], axis=-1) & ~hairy
    # only real crossings stay in front: pieces of CROSS_MIN squares or more that join something outside the head
    # (an arm, the shaft) - Codex's own eye whites, teeth and nose specks are not (review round 1)
    lbl, n = ndimage.label(cross)
    outside = ndimage.binary_dilation((native[..., 3] > 0) & ~hm, structure=np.ones((3, 3), bool))
    for k in range(1, n + 1):
        piece = lbl == k
        if piece.sum() < CROSS_MIN or not (piece & outside).any():
            cross &= ~piece
    body = native.copy()
    body[hm & ~cross] = 0
    if old is not None:
        om = ndimage.binary_dilation(codex_head_mask(hm.shape, old), iterations=1)
        body[om & hairy & ~cross] = 0
        # Codex's hair standing up over the design head's crown: up to 5 rows over the old head, its hair reds only
        # (league_jayce's review rounds: not the outline or raised arms)
        up_m = np.zeros_like(om)
        for up in range(1, 6):
            up_m[:-up] |= om[up:]
        hair_only = is_hair(native)
        lone = up_m & ~om & hair_only & ~cross & (native[..., 3] > 0)
        # only pieces of it that touch the old head (her long hair down the back stays)
        lbl, n = ndimage.label(lone)
        near = ndimage.binary_dilation(om, iterations=1)
        for k in range(1, n + 1):
            if (lbl == k)[near].any():
                body[lbl == k] = 0
    small, corner = down2(body)
    am = np.zeros_like(native)
    am[cross] = (255, 255, 255, 255)
    cross2 = down2(am)[0][..., 3] > 0
    r2, c2 = to_grid(hr, hc, corner)
    out = small.copy()
    paste_over(out, HEAD2, r2, c2, keep=cross2 & (small[..., 3] > 0))
    return out, corner


def cracks(a):
    """1-square slits of ground into the body (review round 1, memory gap-check): a clear square with drawn squares
    on both sides (left and right, or above and below) and inside the figure's own row / column extent, filled with the
    outline - twice, for 2-square-long slits seen as one."""
    out = a.copy()
    for _ in range(2):
        op = out[..., 3] > 0
        lr = np.zeros_like(op)
        lr[:, 1:-1] = op[:, :-2] & op[:, 2:]
        ud = np.zeros_like(op)
        ud[1:-1] = op[:-2] & op[2:]
        m = (lr | ud) & ~op
        if not m.any():
            break
        out[m, :3] = OUTLINE
        out[m, 3] = 255
    return out


def tidy(a):
    out = G.complete_outline(cracks(a), color=OUTLINE)[0]
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


FRAME_SCALE = {}                  # (tag, k) -> scale of a frame drawn off the design's size
ALIGN = {"run"}                   # loops held by the head: each frame moved across so its head sits at the loop's median


def shift_x(a, dx):
    out = np.zeros_like(a)
    if dx > 0:
        out[:, dx:] = a[:, :-dx]
    elif dx < 0:
        out[:, :dx] = a[:, -dx:]
    else:
        out = a.copy()
    return out


def matched(tag, n):
    """The tag's frames at the design's size and where the head sits in each: (frames, heads, scale)."""
    raw = [frame(tag, k) for k in range(1, n + 1)]
    raw = [rescale(a, FRAME_SCALE[(tag, k)]) if (tag, k) in FRAME_SCALE else a for k, a in enumerate(raw, 1)]
    ms = [head_match(a) for a in raw]
    if tag in ALIGN:
        mid = float(np.median([m[3] + HEAD.shape[1] * m[1] / 2.0 for m in ms]))
        dxs = [int(round(mid - (m[3] + HEAD.shape[1] * m[1] / 2.0))) for m in ms]
        raw = [shift_x(a, dx) for a, dx in zip(raw, dxs)]
        ms = [(m[0], m[1], m[2], m[3] + dx) for m, dx in zip(ms, dxs)]
    s = SCALE_FIX.get(tag, float(np.median([m[1] for m in ms])))
    if abs(s - 1.0) > SCALE_TOL:
        raw = [rescale(a, s) for a in raw]
        ms = [head_match(a, scales=[1.0]) for a in raw]
    MATCH[tag] = {"scale": s, "codex_heads": [[m[1], int(m[2]), int(m[3])] for m in ms],
                  "scores": [round(m[0]) for m in ms]}
    return raw, [(m[1], m[2], m[3]) for m in ms], s


def drop(a, d):
    """a moved d rows down; what falls under the ground row is cut and the cut edge gets the
    outline on the ground row."""
    out = np.zeros_like(a)
    out[d:] = a[:-d]
    cut = (out[SOLE + 1:, :, 3] > 0).any(0)
    out[SOLE + 1:] = 0
    edge = cut & (out[SOLE, :, 3] > 0)
    out[SOLE, edge, :3] = OUTLINE
    return out


def shaft(small, native, corner, box):
    """The shaft redrawn on the PPU frame (SHAFT): 4 rows, its colours per column from the native one."""
    r0, c0, c1 = box
    out = small.copy()
    y, _ = to_grid(r0, c0, corner)
    _, x0 = to_grid(r0, c0, corner)
    _, x1 = to_grid(r0, c1, corner)
    for x in range(x0, x1 + 1):
        nc = int(round((x + 0.5 - corner[0]) / K + PIVOT[0] - 0.5))
        lo, hi = max(c0, nc - 1), min(c1, nc + 1)
        light = native[r0 + 1, lo:hi + 1]
        mid = native[r0 + 2:r0 + 4, lo:hi + 1].reshape(-1, 4)
        if not (light[..., 3] > 0).any() or not (mid[..., 3] > 0).any():
            continue
        lc = snap1(np.median(light[light[..., 3] > 0][:, :3], 0))
        mc = snap1(np.median(mid[mid[..., 3] > 0][:, :3], 0))
        for dy, col in enumerate((OUTLINE, lc, mc, OUTLINE)):
            out[y + dy, x, :3] = col
            out[y + dy, x, 3] = 255
    return out


def action(tag, n, ms):
    frames, heads, _ = matched(tag, n)
    out = []
    for k, (a, head) in enumerate(zip(frames, heads), 1):
        if (tag, k) in DROP:
            d = DROP[(tag, k)]
            a = drop(a, d)
            head = (head[0], head[1] + d, head[2])
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


def idle_frames():
    can, head = on_canvas("front")
    a0, corner = with_head(can, head)
    IDLE_HEAD["front"] = (to_grid(head[0], head[1], corner), corner)
    waist = waist_row(a0)
    return [(tidy(breathe(a0, waist, b)), corner, IDLE_MS) for b in BREATH]


def waist_row(a):
    """Her belts in the idle's PPU frame: everything above them breathes - the row 55 % of the way down from the crown
    to the soles."""
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


def hit_frames():
    can, head = on_canvas("side")
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
    out = {"idle": idle_frames(), "hit": hit_frames()}
    for tag, n in TAGS.items():
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


def sole_stubs(a):
    """Outline squares hanging under the soles (the restyle's grown outline, review round 2): below the lowest row
    with 3 or more drawn squares, a square with no lit square right above it is cleared."""
    out = a.copy()
    op = out[..., 3] > 0
    rows = np.nonzero(op.sum(1) >= 3)[0]
    if not len(rows):
        return out
    base = rows.max()
    lit = op & (out[..., :3].astype(int).sum(-1) >= 90)
    for y in range(base + 1, out.shape[0]):
        for x in np.nonzero(op[y])[0]:
            if not lit[y - 1, x] or not lit[y, x]:
                out[y, x] = 0
                op[y, x] = False
    return out


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
        meta = json.load(open(os.path.join(src, f"katarina_{tag}.json"), encoding="utf-8"))
        strip = rgba(os.path.join(src, f"katarina_{tag}.png"))
        x, frames = 0, []
        for W, H in meta["sizes"]:
            f = strip[:H, x:x + W].copy()
            f = sole_stubs(cracks(f))
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
    print(f"katarina: {total} squares of the restyled frames and {n1} 1x pixels filled")
    print(f"katarina: {bake(hds, sheet)} pictures laid into her frames")
    for tag in ORDER:
        Image.fromarray(strip_of(hds[tag])).save(os.path.join(src, f"katarina_{tag}.png"))
        with open(os.path.join(src, f"katarina_{tag}.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"sizes": [[a.shape[1], a.shape[0]] for a in hds[tag]]}, f)
    G.write_sheet(STEM, sheet)


BAKE_DIR = os.path.join(SRC, "fx_bake")
BAKE_CELLS = os.path.join(SRC, "fx_bake_cells.json")


def bake(hds, sheet):
    """tools/art/import_katarina_fx.py's pictures for her frames (assets/source/katarina/fx_bake/<name>_<k>.png on the guide
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
        ov = rgba(path)
        x0, y0, W, H = c["frame"]
        f = hds[tag][k - 1]
        drawn_at = c.get("ppu", PPU)
        if abs(drawn_at - PPU) > 1e-6:
            # the pack's guides were her frames at PPU 1.5 (sent before the switch to 1.7895): the picture scaled by
            # PPU / drawn_at about the old frame's centre (nearest), onto the new frame's box round the same centre
            s = PPU / drawn_at
            cx, cy = x0 + W / 2.0, y0 + H / 2.0
            im = Image.fromarray(ov)
            ov = np.asarray(im.resize((round(im.width * s), round(im.height * s)), Image.NEAREST)).copy()
            W, H = f.shape[1], f.shape[0]
            x0, y0 = int(round(cx * s - W / 2.0)), int(round(cy * s - H / 2.0))
        if (f.shape[1], f.shape[0]) != (W, H):
            sys.exit(f"{key}: {tag} frame {k} is {f.shape[1]}x{f.shape[0]}, its guide's {W}x{H}: the frames changed "
                     "since the effects pack (tools/art/pack_katarina_fx.py)")
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
        Image.fromarray(strip_of(hds)).save(os.path.join(ORIG, f"katarina_{tag}.png"))
        with open(os.path.join(ORIG, f"katarina_{tag}.json"), "w", encoding="utf-8", newline="\n") as f:
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
            big.convert("RGB").save(os.path.join(a.review, f"katarina_{tag}.png"))
    w, h = G.write_sheet(STEM, sheet)
    print(f"league/champions/league_katarina#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))
    print("face point (crown):", face_point(IDLE_HEAD["front"]))


if __name__ == "__main__":
    main()
