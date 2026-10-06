#!/usr/bin/env python3
"""Gwen's design (assets/source/native/gwen_native.png): Codex's step-1 draft bd82c7f4 read back on its own grid and
traced down to 44 rows by block votes; the face, the hand and the scissors drawn over it.

    python tools/art/design_gwen.py [--check]

How it came about (2026-10-06): the user picked Codex's picture A (codex_picture/gwen-model-A.png: the open scissors held
at her side, the blades trailing down and back). Codex's step 1 (codex_model/) drew 9 drafts, all bigger than 40 rows;
its own 40-row candidates were sampled down (its HANDOFF says they fail), four drafts turned her into twin tails. My
whole-row/column cuts of drafts 2eb5 and 0fc0 (design_samira's way) were rejected: 「你那些都不合格 用这个」 with draft
bd82c7f4 (105 x 77 on its own 9-px grid), then 「你看看蛮王 莎米拉都怎么处理的 都是慢慢调好的」「你要用工具啊」. At 105 -> 44
rows deleting whole lines shreds her, so she is traced by block votes; the user picked base A of three (the whole figure
at one scale), then for the face 「脸部五官太奇怪了」「改不好就学隔壁oppi美术的技巧」 (oppi's eyes: 「这个可以」), then
「手部武器被像素遮挡严重 看不清 嘴和眼睛应该做成更可爱一点的」 -> the scissors drawn as parts and face "cute 1"; then League's long closed scissors and the neck. Steps:
  1. raw/exec-bd82c7f4-*.png read back on its own grid (the skill's regrid.py, alpha >= 128): 105 x 77;
  2. every square one of K colours of the read-back's own (design_varus.kmeans: CIELAB, farthest-point start, seed 1);
  3. to HEIGHT rows by block votes: each game pixel looks at the source block it covers (rows and columns cut evenly,
     the width in proportion): see-through when less than half of it is opaque; the outline colour when more than
     INK_SHARE of it is outline (so thin inner lines go and flat areas stay clean); a LINES colour (the hair's dark
     coil lines) when it holds that share of the rest; else the commonest colour of the rest;
  4. strips.complete_outline round the silhouette;
  5. the eyes the votes averaged away (FACE_1), then lone squares - a square none of its eight neighbours shares,
     inside the silhouette, not gold, not the face - take their four neighbours' commonest colour when two or more
     agree (two rounds);
  6. the hand and the scissors (SCISSORS): the votes had merged the glove into the skirt's dark and filled both ring
     handles. Columns 0-11 of rows 21-38 are cleared (the skin of the arm kept) and the parts drawn where the draft
     has them: each ring a 5-square loop with a see-through middle (white top-left, lilac, a shade bottom-right), two
     blades 4 squares wide at the rings tapering to their points (cyan, a blue middle, a navy lower edge), the glove a
     2 x 2 block gripping the upper ring; the outline closed round the parts;
  7. the face (FACE): skin flat; two 2 x 2 eyes under a near-black lash row that runs on over the outer corners, in
     the user's reference's way (「能不能把这个五官拿过来用 你慢慢手绘」 - the eyes were 「有点丑」): the white square top
     left (both eyes: one light), dark blue beside it, bright blue under them - dark on top, light below, looking the
     way she faces; a blush square under each eye, a one-square mouth in the middle, the chin closed with the
     outline's blue; the old neck dot that read as a mouth corner made skin (NECK);
  8. (the user: 「我记得格温是大剪刀把？」「你看原版英雄啊」) League's own scissors replace step 6's: closed, one long
     blade from behind her hip down to the lower left (about 1.1 times her height; League's is 1.6), two spiked ring
     handles behind her hip at image right, a shank from the hip to each ring - all drawn BEHIND the figure on a
     canvas widened by PAD, the hand at her side (LEAGUE["hand"]), the outline closed;
  9. the neck and the bodice as the draft has them (TORSO; the user: 「只剩脖子和身体那里有点怪了」, then 「OK了」): a
     2-square neck, a cyan choker, a skin V under it, black puffed sleeves, the dark bodice, the purple bow with the
     gold star;
 10. the blade's point closed (POINT: a detached last square read as broken, 「剪刀这里看起来像断的」);
 11. on the 128x128 canvas at 8x: the soles on row 99, the middle of the feet (the lowest three rows) on column 64.
--check compares the result with the committed gwen_native.png instead of writing it.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_varus as dv  # noqa: E402
import strips  # noqa: E402
from regrid import regrid  # noqa: E402

RAW_DIR = os.path.join(ROOT, "assets", "source", "gwen", "codex_model", "raw")
DRAFT = "bd82c7f4"
OUT = os.path.join(ROOT, "assets", "source", "native", "gwen_native.png")
K, HEIGHT, INK_SHARE = 28, 44, 0.5
SOLE_ROW, MID_COL, FEET_ROWS = 99, 64, 3


def hx(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


LINES = {hx("#020375"): 0.25, hx("#0b0baa"): 0.30}      # the hair's dark-blue coil lines: share of the non-outline
C = {"I": hx("#08021a"), "A": hx("#020375"), "G": hx("#fce3cd"), "N": hx("#f8b899"), "K": hx("#f6a6a0"),
     "C": hx("#0187fa"), "D": hx("#025ff8"), "B": hx("#0b0baa"), "L": hx("#f3f8fa"), "O": hx("#f33449"),
     "P": hx("#e0506a"), "M": hx("#cec1fa"), "J": hx("#aa93f3"), "Y": hx("#28ddfc"), "U": hx("#3c2a71"),
     "S": hx("#653a94")}
GOLD = {hx(h) for h in ("#fbe169", "#fabe38", "#e89620", "#b46621", "#fcf6cb")}
# step 5 (the figure's own coordinates: column, row of the 32 x 44 trace)
FACE_1 = {(17, 9): "A", (18, 9): "A", (20, 9): "A", (21, 9): "A", (19, 9): "G",
          (17, 10): "C", (18, 10): "L", (20, 10): "C", (21, 10): "L", (19, 10): "G",
          (17, 11): "D", (18, 11): "C", (20, 11): "D", (21, 11): "C", (19, 11): "G", (16, 10): "N", (20, 13): "O"}
# step 6: blades (base, point, width at the base), rings (centre, outer radius, hole radius), glove squares
SCISSORS = {"clear": (21, 39, 12),
            "blades": [((5.5, 26.0), (0.6, 35.6), 4.0), ((8.5, 30.0), (3.6, 37.8), 4.0)],
            "rings": [((9.5, 28.5), 2.6, 1.1), ((6.5, 24.5), 2.6, 1.1)],
            "glove": {(9, 22): "S", (10, 22): "U", (9, 23): "U", (10, 23): "U", (11, 22): "U", (11, 21): "G"}}
# step 7: rows of columns 16-22
FACE_X0 = 16
FACE = {8: "IIIGIII",
        9: "GLBGLBG",
        10: "GCCGCCG",
        11: "GKGGGKG",
        12: "GGGPGGG",
        13: "AGGGGGA"}
NECK = {(18, 14): "G"}
# step 9: League's scissors (closed: one long blade from behind her hip to the lower left, two spiked ring handles
# behind her hip at image right), drawn behind the figure on a canvas widened by PAD (left, right); figure columns
C.update({"y": hx("#8ff2fe"), "H": hx("#28ddfc"), "h": hx("#0187fa"), "R": hx("#fbe169"), "T": hx("#fabe38"),
          "S2": hx("#e89620"), "Ad": hx("#1d1444"), "Kp": hx("#653a94"), "Lb": hx("#4516eb")})
PAD = (18, 10)
LEAGUE = {"blade": ((20, 26), (-12, 40.5), 3.4),
          "rings": [((31.5, 21.5), 3.3, 1.3), ((33.5, 28.5), 3.3, 1.3)],
          "spikes": [((33.5, 20.5), (37.5, 18), 1.8), ((35.5, 28.5), (39.5, 28.5), 1.8), ((34, 31), (36.5, 34), 1.6),
                     ((29.5, 20), (29, 16.5), 1.6)],
          "shank": [((22, 25), (30, 24), 1.6), ((22, 26), (31, 28.5), 1.6)],
          "hand": {(11, 22): "U", (12, 22): "U", (11, 23): "S", (12, 23): "U", (12, 21): "G"}}
# step 10: neck and bodice as the draft has them (the user: 「只剩脖子和身体那里有点怪了」), columns 27.. of the final crop;
# rows 18-19 flat bodice under the V (they alternated dark and light columns: 「手臂这里颜色都对对齐看了好怪」) and the square
# between the near sleeve and the bodice filled
TORSO_X0 = 27
TORSO = {14: "---BDDB-----",
         15: "---BhHB-----",
         16: "--IPDDPI----",
         17: "-aaQPDPQaa--",
         18: "-aaQQPQQaa--",
         19: "-aIQQkQQIa--",
         20: "-lllTRTlll--",
         21: "-llkXTXkll--"}
# the blade's point (the user: 「剪刀这里看起来像断的」): the last blue square stood one clear square off the blade with an
# outline square under it; both go, the gap's square is outline - the point ends on row 39
POINT = {(0, 40): None, (0, 41): None, (1, 40): "I"}
TORSO_KEYS = {"B": "A", "D": "G", "P": "N", "I": "I", "a": "Ad", "Q": "U", "k": "Kp", "h": "h", "H": "H",
              "l": "Lb", "T": "T", "R": "R", "X": "S2"}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read_back():
    path = next(os.path.join(RAW_DIR, f) for f in os.listdir(RAW_DIR) if DRAFT in f)
    raw, _, _ = regrid(np.asarray(Image.open(lp(path)).convert("RGBA")))
    ys, xs = np.nonzero(raw[..., 3] >= 128)
    raw = raw[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    raw[..., 3] = np.where(raw[..., 3] >= 128, 255, 0)
    return raw


def votes(idx, pal, h):
    """Step 3: one palette index (or -1) per game pixel."""
    H, W = idx.shape
    ink = int(np.argmin((pal * [0.299, 0.587, 0.114]).sum(1)))
    lines = {int(np.argmin(np.abs(pal.astype(int) - np.array(c)).sum(1))): s for c, s in LINES.items()}
    w = round(W * h / H)
    ys, xs = np.linspace(0, H, h + 1), np.linspace(0, W, w + 1)
    out = np.full((h, w), -1)
    for j in range(h):
        for i in range(w):
            b = idx[int(ys[j]):int(np.ceil(ys[j + 1])), int(xs[i]):int(np.ceil(xs[i + 1]))].ravel()
            op = b[b >= 0]
            if len(op) * 2 < len(b) or not len(op):
                continue
            rest = op[op != ink]
            if (op == ink).sum() > INK_SHARE * len(op) or not len(rest):
                out[j, i] = ink
                continue
            hit = [c for c, s in lines.items() if (rest == c).sum() >= s * len(rest)]
            if hit:
                out[j, i] = hit[0]
                continue
            vals, cnt = np.unique(rest, return_counts=True)
            out[j, i] = vals[np.argmax(cnt)]
    return out, ink


def paint(a, table):
    for (x, y), ch in table.items():
        a[y, x, :3] = C[ch]
        a[y, x, 3] = 255


def lone(a, protect, rounds=2, need=2):
    """Step 5: squares no neighbour shares take their four neighbours' commonest colour."""
    for _ in range(rounds):
        b = a.copy()
        for y in range(1, a.shape[0] - 1):
            for x in range(1, a.shape[1] - 1):
                if a[y, x, 3] == 0 or (x, y) in protect:
                    continue
                p = tuple(int(v) for v in a[y, x, :3])
                if p in GOLD:
                    continue
                n8 = [a[y + dy, x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx]
                if any(q[3] == 0 for q in n8) or any(tuple(int(v) for v in q[:3]) == p for q in n8):
                    continue
                n4 = [tuple(int(v) for v in a[y + dy, x + dx, :3]) for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))]
                best = max(set(n4), key=n4.count)
                if n4.count(best) >= need and best not in GOLD:
                    b[y, x, :3] = best
        a = b
    return a


def blade(layer, p0, p1, w0):
    p0, p1 = np.array(p0, float), np.array(p1, float)
    d = p1 - p0
    n = np.linalg.norm(d)
    u = d / n
    v = np.array([-u[1], u[0]])
    if v[1] > 0:
        v = -v                                       # v points up the screen: the lit side
    for y in range(layer.shape[0]):
        for x in range(layer.shape[1]):
            q = np.array([x + 0.5, y + 0.5]) - p0
            t, s = q @ u / n, q @ v
            if not 0 <= t <= 1:
                continue
            half = max(0.5, w0 / 2 * (1 - t) + 0.5 * t)
            if abs(s) <= half:
                layer[y, x, :3] = C["Y"] if s > -0.1 * half else (C["C"] if s > -half + 0.9 else C["A"])
                layer[y, x, 3] = 255


def ring(layer, c, ro, ri):
    for y in range(layer.shape[0]):
        for x in range(layer.shape[1]):
            dx, dy = x + 0.5 - c[0], y + 0.5 - c[1]
            r = np.hypot(dx, dy)
            if ri < r <= ro:
                layer[y, x, :3] = C["L"] if dx + dy < -1.5 else (C["J"] if dx + dy > 1.5 else C["M"])
                layer[y, x, 3] = 255
            elif r <= ri:
                layer[y, x] = 0


def scissors(fig):
    """Step 6."""
    layer = np.zeros_like(fig)
    for b in SCISSORS["blades"]:
        blade(layer, *b)
    for r in SCISSORS["rings"]:
        ring(layer, *r)
    paint(layer, SCISSORS["glove"])
    can, _, _ = strips.complete_outline(np.pad(layer, ((1, 1), (1, 1), (0, 0))), color=C["I"], feet=fig.shape[0])
    layer = can[1:-1, 1:-1]
    y0, y1, x1 = SCISSORS["clear"]
    fig[y0:y1, :x1] = 0
    m = layer[..., 3] > 0
    fig[m] = layer[m]
    return fig


def league_blade(layer, p0, p1, w0):
    """Step 9's blade (and spikes, shank): light top, mid, blue lower third."""
    p0, p1 = np.array(p0, float), np.array(p1, float)
    d = p1 - p0
    n = np.linalg.norm(d)
    u = d / n
    v = np.array([-u[1], u[0]])
    if v[1] > 0:
        v = -v
    for y in range(layer.shape[0]):
        for x in range(layer.shape[1]):
            q = np.array([x + 0.5, y + 0.5]) - p0
            t, s = q @ u / n, q @ v
            if not 0 <= t <= 1:
                continue
            half = max(0.5, w0 / 2 * (1 - t) + 0.5 * t)
            if abs(s) <= half:
                layer[y, x, :3] = C["y"] if s > half * 0.35 else (C["H"] if s > -half * 0.35 else C["h"])
                layer[y, x, 3] = 255


# the rings' holes are hearts (the user: 「剪刀孔请用可爱的形状」), upright at any angle: rows from the top, columns
# from the left of the 5 x 4 middle of the ring's disc ("#" the hole; 3 x 3 in a 5-square disc read as a blot)
HEART = [".#.#.", "#####", ".###.", "..#.."]


def league_ring(layer, c, ro, ri):
    """A ring handle: a disc of radius ro on the square nearest c (so the heart sits on whole squares), lit top left,
    a heart-shaped hole (HEART) in its middle - the hole drawn in the outline colour (ri is the old round hole's
    radius, kept in the tables)."""
    cx, cy = np.floor(c[0]) + 0.5, np.floor(c[1]) + 0.5
    for y in range(layer.shape[0]):
        for x in range(layer.shape[1]):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            if np.hypot(dx, dy) <= ro:
                layer[y, x, :3] = C["y"] if dx + dy < -1.5 else (C["h"] if dx + dy > 1.5 else C["H"])
                layer[y, x, 3] = 255
    for r, row in enumerate(HEART):
        for i, ch in enumerate(row):
            if ch == "#":
                y, x = int(cy - 0.5) - 1 + r, int(cx - 0.5) - 2 + i
                if 0 <= y < layer.shape[0] and 0 <= x < layer.shape[1]:
                    layer[y, x, :3] = C["I"]
                    layer[y, x, 3] = 255


def league_scissors(fig, with_mask=False):
    """Step 9: the first scissors' columns cleared again, the hand at her side, League's scissors behind her.
    with_mask: also the squares the scissors add (blade, rings, shank and their outline) - tools/art/rig_gwen.py lifts
    them off the body."""
    y0, y1, x1 = SCISSORS["clear"]
    fig[y0:y1, :x1] = 0
    paint(fig, LEAGUE["hand"])
    H, W = fig.shape[:2]
    big = np.zeros((H, W + PAD[0] + PAD[1], 4), np.uint8)
    big[:, PAD[0]:PAD[0] + W] = fig
    layer = np.zeros_like(big)
    sh = lambda p: (p[0] + PAD[0], p[1])  # noqa: E731
    for c, ro, ri in LEAGUE["rings"]:
        league_ring(layer, sh(c), ro, ri)
    for b0, b1, w in LEAGUE["spikes"] + [LEAGUE["blade"]] + LEAGUE["shank"]:
        league_blade(layer, sh(b0), sh(b1), w)
    can, _, _ = strips.complete_outline(np.pad(layer, ((1, 1), (1, 1), (0, 0))), color=C["I"], feet=H)
    layer = can[1:-1, 1:-1]
    behind = (layer[..., 3] > 0) & (big[..., 3] == 0)
    big[behind] = layer[behind]
    was = big[..., 3] > 0
    can, _, _ = strips.complete_outline(np.pad(big, ((1, 1), (1, 1), (0, 0))), color=C["I"], feet=H)
    big = can[1:-1, 1:-1]
    added = behind | ((big[..., 3] > 0) & ~was)
    xs = np.nonzero((big[..., 3] > 0).any(0))[0]
    out = big[:, xs.min():xs.max() + 1].copy()
    return (out, added[:, xs.min():xs.max() + 1].copy()) if with_mask else out


N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
DARK, CRUMB = 60, 3                    # step 11: dark crumbs (the user: 「清理一下没用的黑色素」「弄干净点」)
FACE_BOX = (62, 70, 58, 70)            # rows r0..r1, columns c0..c1 on the canvas: the lashes, eyes and mouth stay


def clean_dark(a, protect):
    """Pieces (4-connected) of squares darker than DARK, CRUMB or fewer, inside the silhouette (not touching the
    transparent outside) and off `protect`, take their lighter neighbours' commonest colour; twice. Returns the count."""
    H, W = a.shape[:2]
    n = 0
    for _ in range(2):
        op = a[..., 3] > 0
        dk = op & ((0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]) < DARK)
        seen = np.zeros((H, W), bool)
        for y0, x0 in zip(*np.nonzero(dk)):
            if seen[y0, x0]:
                continue
            comp, st, out = [], [(y0, x0)], False
            seen[y0, x0] = True
            while st:
                y, x = st.pop()
                comp.append((y, x))
                for dy, dx in N4:
                    yy, xx = y + dy, x + dx
                    if not (0 <= yy < H and 0 <= xx < W) or not op[yy, xx]:
                        out = True
                    elif dk[yy, xx] and not seen[yy, xx]:
                        seen[yy, xx] = True
                        st.append((yy, xx))
            if out or len(comp) > CRUMB or any(protect[y, x] for y, x in comp):
                continue
            for y, x in comp:
                nb = [tuple(int(v) for v in a[y + dy, x + dx, :3]) for dy, dx in N4
                      if 0 <= y + dy < H and 0 <= x + dx < W and op[y + dy, x + dx] and not dk[y + dy, x + dx]]
                if nb:
                    a[y, x, :3] = max(set(nb), key=nb.count)
                    n += 1
    return n



def lone_ink(a, keep):
    """Step 12 (the user: 「最后清理一下没用的黑色素吧弄干净一点」): near-black squares inside the figure that join no line
    (one or no near-black 4-neighbour, every 4-neighbour opaque), off `keep` (the face, the scissors), take their
    4-neighbours' commonest colour - the dots at the neck's V, the sleeves' corners and the skirt's left edge; the lashes,
    the rings' holes and the boots' split are lines and stay. Returns the count."""
    ink = np.array(C["I"], np.uint8)
    op = a[..., 3] > 0
    isk = op & (a[..., :3] == ink).all(-1)
    H, W = op.shape
    hits = []
    for y, x in zip(*np.nonzero(isk & ~keep)):
        nb = [(y + dy, x + dx) for dy, dx in N4]
        if not all(0 <= yy < H and 0 <= xx < W and op[yy, xx] for yy, xx in nb):
            continue
        if sum(isk[yy, xx] for yy, xx in nb) > 1:
            continue
        cols = [tuple(int(v) for v in a[yy, xx, :3]) for yy, xx in nb if not isk[yy, xx]]
        hits.append((y, x, max(set(cols), key=cols.count)))
    for y, x, c in hits:
        a[y, x, :3] = c
    return len(hits)


# step 13 (the user, at the portrait: 「头像这里一大块是什么？」「头发」「像素缺失？」): the dark violet masses the
# votes left in the hair beside her head (the draft's shadowed back hair, darker than any hair colour) read as missing
# squares; in the hair's rows there the violet black takes the hair's navy and the violet the hair's blue
BACK_HAIR = {"rows": (59, 67), "cols": [(52, 59), (69, 75)],
             "map": {"#1d1444": "#020375", "#3c2a71": "#025ff8"}}


def back_hair(a):
    r0, r1 = BACK_HAIR["rows"]
    n = 0
    for c0, c1 in BACK_HAIR["cols"]:
        for y in range(r0, r1 + 1):
            for x in range(c0, c1 + 1):
                if a[y, x, 3]:
                    h = "#%02x%02x%02x" % tuple(int(v) for v in a[y, x, :3])
                    if h in BACK_HAIR["map"]:
                        a[y, x, :3] = hx(BACK_HAIR["map"][h])
                        n += 1
    return n

# step 14 (the user: 「你把我44行的精修一下吧」, then 「有点味道了 继续美化」, after their own picture of her): the head
# polished the picture's way and the skirt and legs cleaned. Canvas coordinates, the scissors' squares (mask) behind:
# 1. the dark masses beside her head (the draft's bows, navy since step 13) cleared, and in their place an end-on curl
#    each side by her shoulders - a disc lit top left with a navy line winding into its middle (the picture's spiral
#    ringlets) - the hair from the crown down to them filled;
# 2. a small bow on each side of the crown (5 x 3, violet lit on top, a gold knot) - big black ones read as blots
#    (「蝴蝶结这么大？？？？」);
# 3. the crown redrawn (CROWN): lit top left, darker to the right, a parting splitting two locks, strands, the bangs'
#    points on her forehead and a cyan ahoge curling up (it was a navy stub);
# 4. the skirt with fewer things on it (「裙子上元素可以少一点」): the white panels' gold edging and the gold under the
#    hem take the colours beside them, the middle hem ornament goes; the bow's star and two hem ornaments stay;
# 5. the stockings in three clean steps per leg (lit left edge, dark right edge), a lilac knee each, a gold star on the
#    far thigh; the boots' lone squares cleaned.
PAL = {"0": "#08021a", "a": "#020375", "b": "#1d1444", "c": "#0b0baa", "d": "#3c2a71", "e": "#4516eb", "f": "#653a94",
       "g": "#025ff8", "h": "#0187fa", "i": "#e0506a", "j": "#7f6be0", "k": "#03adfb", "l": "#e89620", "m": "#aa93f3",
       "n": "#28ddfc", "o": "#f39378", "p": "#f6a6a0", "q": "#fabe38", "r": "#f8b899", "s": "#cec1fa", "t": "#8ff2fe",
       "u": "#fbe169", "v": "#fce3cd", "w": "#fcf6cb", "x": "#f3f8fa"}
LETTER = {v: k for k, v in PAL.items()}
POLISH_FACE = (62, 68, 63, 69)                     # columns, rows of the face: kept
FACE_TURN = (62, 68)                               # the face's columns: its features moved one to the right
FACE_NEAR = ((61, 63, "g"), (62, 63, "h"), (63, 63, "k"),   # the bangs over the forehead's bare strip,
             (62, 64, "h"), (62, 65, "h"), (62, 66, "a"),   # a lock of the bangs down the near cheek,
             (63, 65, "0"), (63, 67, "p"),                   # a lash at the near eye's outer corner, the blush 2 wide,
             (62, 67, "r"), (62, 68, "r"))                   # the cheek's edge shaded
CURLS_ = [(57.5, 68.5, 3.9, True), (73.0, 68.5, 3.9, False)]   # centre, radius, winding
BOW_ = ["fd.df", "ddqdd", "bd.db"]
BOWS_AT = [(57, 60), (73, 60)]
SIDES = {62: ("0tnkhagh", "hgaknkh0"),
         63: ("0nkhgagh", "ggankhg0"),
         64: ("0khgaggh", "hgakhga0")}           # columns 54-61 and 69-76
THIGHS = (63, 66, 70)                         # rows 87-90 one block: the near thigh 63-66, the far 67-70
CALVES = {91: ((62, 65), (67, 70)), 92: ((62, 65), (67, 70)), 93: ((62, 65), (67, 70))}  # near, far: straight
BOOTS = {94: ((61, "sxxsm"), (67, "msxs")),   # (first column, colours): the near boot facing us, its toe out to
         95: ((61, "msqsb"), (67, "bmqm")),   # the left; the far boot turned to her front (image right), its toe
         96: ((61, "ssxsb"), (67, "bmss")),   # out to the right - a gold buckle each, a gold toe cap
         97: ((61, "qsssb"), (67, "bmsss")),
         98: ((61, "ssssb"), (68, "bmssq"))}
THIGH_STAR = ((69, 87, "u"), (68, 88, "q"), (69, 88, "u"), (70, 88, "q"), (69, 89, "l"))
CROWN = {54: "--.000.........",
         55: "--0ntn0........",
         56: "--0nn0.........",
         57: "-0nkn000000----",
         58: "0gnttnnhnkh0---",
         59: "--ntnnkhnkhhg--",
         60: "--nnhnaknnhgg--",
         61: "--knnhannkhhg--",
         62: "0ghnnkakknkhgg0",
         63: "0ghvvvknnkhggg0"}                  # from column 58; '-' keeps, '.' clears


def polish(canvas, mask):
    a = canvas

    def ch(y, x):
        if not a[y, x, 3]:
            return "."
        return LETTER.get("#%02x%02x%02x" % tuple(int(v) for v in a[y, x, :3]), "?")

    def put(x, y, c):
        if c == ".":
            a[y, x] = 0
        else:
            a[y, x] = (*hx(PAL[c]), 255)
        mask[y, x] = False

    fx0, fx1, fy0, fy1 = POLISH_FACE
    # 1. the side masses cleared (not the face, the scissors or the dress's dark at the shoulders)
    for y in range(59, 75):
        for x in list(range(50, 62)) + list(range(69, 80)):
            if (fx0 <= x <= fx1 and fy0 <= y <= fy1) or mask[y, x]:
                continue
            c = ch(y, x)
            if c in "acghkntqu0bdf" and not (y >= 72 and c in "bdf"):     # the draft's bows (violet) too
                put(x, y, ".")
    for cx, cy, r, cw in CURLS_:
        pitch = r / 1.5
        for y in range(int(cy - r - 1), int(cy + r + 2)):
            for x in range(int(cx - r - 1), int(cx + r + 2)):
                dx, dy = x + 0.5 - cx, y + 0.5 - cy
                d = np.hypot(dx, dy)
                if d > r:
                    continue
                th = np.arctan2(dy, dx) * (1 if cw else -1)
                u = (d + th / (2 * np.pi) * pitch) % pitch
                if u < pitch * 0.42 and d > 0.6:
                    c = "a"
                else:
                    lit = -(dx + dy) / (r * 1.4)
                    c = "t" if lit > 0.55 else ("n" if lit > 0.05 else ("k" if lit > -0.35 else ("h" if lit > -0.7 else "g")))
                if mask[y, x] or ch(y, x) in ".acghknt0" or y < 72:
                    put(x, y, c)
    for y in range(59, 66):
        for x in (59, 60, 61, 69, 70, 71):
            if ch(y, x) == ".":
                put(x, y, "h" if x in (61, 69) else "g")
    # 2. the bows
    for cx, cy in BOWS_AT:
        for r, row in enumerate(BOW_):
            for i, c in enumerate(row):
                if c != ".":
                    put(cx - 2 + i, cy - 1 + r, c)
    # outline round the head (rows 52-76), never over the scissors
    op = a[..., 3] > 0
    ring = np.zeros_like(op)
    for dy, dx in N4:
        ring |= np.roll(np.roll(op, dy, 0), dx, 1)
    ring &= ~op
    ring[:52] = False
    ring[77:] = False
    for y, x in zip(*np.nonzero(ring)):
        put(x, y, "0")
    # the hair behind the bows: the gaps between a bow and the crown and curls (filled with outline they made the
    # bows a black blot) take the hair's blue; then one outline ring outside again
    bows = {(cx - 2 + i, cy - 1 + r) for cx, cy in BOWS_AT for r, row in enumerate(BOW_) for i, c in enumerate(row)
            if c != "."}
    for x0, x1 in ((55, 59), (71, 75)):
        for y in range(62, 65):                    # under the bow down to the curl: above it only the outline
            for x in range(x0, x1 + 1):
                if (x, y) not in bows and ch(y, x) in ".0" and not mask[y, x]:
                    put(x, y, "g")
    for y in range(52, 77):
        for x in range(46, 86):
            if ch(y, x) == "0" and all(ch(y + dy, x + dx) not in "." for dy, dx in N4) and not mask[y, x] and                     not (fx0 <= x <= fx1 and fy0 <= y <= fy1) and 56 <= y <= 64 and (x <= 59 or x >= 71):
                put(x, y, "a")                     # an outline square now inside the hair: the hair's navy line
    # the hair from each bow down into its curl: locks lit on the left with a navy line (filled flat blue, the two
    # sides and the crown's edges read as a headband)
    for y, (left, right) in SIDES.items():
        for i, c in enumerate(left):
            put(54 + i, y, c)
        for i, c in enumerate(right):
            put(69 + i, y, c)
    # 3. the crown
    for y, row in CROWN.items():
        for i, c in enumerate(row):
            if c != "-":
                put(58 + i, y, c)
    op = (a[..., 3] > 0) & ~(a[..., :3] == hx(PAL["0"])).all(-1)   # colour, not outline: one ring, not two
    for y in range(53, 65):
        for x in range(54, 78):
            if not a[y, x, 3] and any(op[y + dy, x + dx] for dy, dx in N4):
                put(x, y, "0")
    # outline squares with no colour beside them (the first ring's outer squares now doubled) go
    for y in range(52, 66):
        for x in range(46, 86):
            if ch(y, x) == "0" and not mask[y, x] and not any(op[y + dy, x + dx] for dy, dx in N4) and                     not any(ch(y + dy, x + dx) == "0" and op[y + 2 * dy, x + 2 * dx] if 0 <= y + 2 * dy < 128 else False
                            for dy, dx in N4):
                put(x, y, ".")

    def common(y, x, skip):
        nb = [ch(y + dy, x + dx) for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))]
        nb = [n for n in nb if n not in skip]
        return min(set(nb), key=lambda c: (-nb.count(c), c)) if nb else None   # ties by letter: the same every run

    # 4. the skirt
    for y in list(range(79, 82)) + [86, 87]:
        for x in range(55, 80):
            if ch(y, x) in "qul" and not mask[y, x]:
                c = common(y, x, set("qul0."))
                if c:
                    put(x, y, c)
    if ch(84, 65) in "qul":
        put(65, 84, "b")
    # 5. the legs redrawn (the user: 「腿能更新吗」, the picture's): diamond-checked violet stockings lit on the left edge,
    # a small gold star on the far thigh, white boots with a gold buckle and toe cap - standing as the first design
    # did, a little turned (「你看看之前的格温的站姿」「你现在站的太正了」: the redrawn legs stood square, apart, toes out):
    # the thighs together, the near leg out to the left from the knee, its boot facing us, the far leg straight, its
    # boot turned to her front; under her middle (「腿移中间点呗」; the run splits them at column 66)
    for y in range(87, 100):
        for x in range(56, 76):
            if not mask[y, x] and (y >= 89 or 58 <= x <= 73):
                put(x, y, ".")
    legs = np.zeros(mask.shape, bool)

    def stocking(y, x0, x1, lit):
        for x in range(x0, x1 + 1):
            put(x, y, "f" if (x + y) % 2 == 0 else "d")
            legs[y, x] = True
        if lit:
            put(x0, y, "j")
        put(x1, y, "b" if (x1 + y) % 2 else "d")

    t0, t1, t2 = THIGHS
    for y in range(87, 91):
        stocking(y, t0, t1, True)
        stocking(y, t1 + 1, t2, False)
        if y >= 89:
            put(t1 + 1, y, "b")                           # the crease between the thighs
    for y, ((n0, n1), (f0, f1)) in CALVES.items():
        stocking(y, n0, n1, True)
        stocking(y, f0, f1, False)
    for x, y, c in THIGH_STAR:
        put(x, y, c)
    for y, segs in BOOTS.items():
        for x0, cols in segs:
            for i, c in enumerate(cols):
                put(x0 + i, y, c)
                legs[y, x0 + i] = True
    for y in range(87, 100):                              # one outline round them, never over the skirt or scissors
        for x in range(56, 76):
            if not (legs[y, x] or mask[y, x] or a[y, x, 3]) and any(
                    legs[y + dy, x + dx] for dy, dx in N4 if 0 <= y + dy < 128):
                put(x, y, "0")
    for y in range(91, 99):                               # and one column between them
        if not legs[y, 66]:
            put(66, y, "0")
    # the skirt's bottom edge closed: an outline square under each skirt square left over nothing - row 86 had a hole
    # above the near stocking and none under the two last squares on the right (「太奇怪了 找找分析修复一下」), row 87
    # where the legs moved from
    for y in (86, 87):
        for x in range(56, 76):
            if ch(y, x) == "." and ch(y - 1, x) not in ".0" and not mask[y, x]:
                put(x, y, "0")
    # outline squares the rings above left touching no colour (over the scissors' spikes, outside the near shoulder) go -
    # on the edge only: never the scissors' own (it punched their rings' hearts into a checker: 「剪刀孔请用可爱的形状」)
    # nor one with ink all round (that left a clear pinhole under the near curl; 「太奇怪了 找找分析修复一下」)
    ink = (a[..., :3] == hx(PAL["0"])).all(-1) & (a[..., 3] > 0)
    col = (a[..., 3] > 0) & ~ink
    for y, x in zip(*np.nonzero(ink)):
        if not 50 <= y <= 99 or mask[y, x]:
            continue
        nb = [(y + dy, x + dx) for dy, dx in N4 if 0 <= y + dy < 128 and 0 <= x + dx < 128]
        if not any(col[p] for p in nb) and any(not a[p][3] for p in nb):
            a[y, x] = 0
            mask[y, x] = False
    # a clear square with the outline on all four sides takes it (under the near curl the head's outline ring was put
    # all round a square it left clear: a pinhole of the ground)
    op = a[..., 3] > 0
    for y, x in zip(*np.nonzero(~op)):
        if 50 <= y <= 99 and all(op[y + dy, x + dx] and not mask[y + dy, x + dx] for dy, dx in N4):
            put(x, y, "0")
    # 6. the face turned a column to her front (image right) with the stance (「你现在站的太正了」, then 「加上」): the
    # brows, eyes, blush and mouth (columns 62-68, rows 64-68) one column right, the column they leave skin
    f0, f1 = FACE_TURN
    for y in range(64, 69):
        row = [ch(y, x) for x in range(f0, f1 + 1)]
        for i, c in enumerate(["v"] + row[:-1]):
            put(f0 + i, y, c)
    # its near side then two columns of bare skin (「左边脸部有点奇怪吧 再精致一点 感觉少了点什么」): a lock of the
    # bangs down the near cheek, the near eye the bigger (a lash at its outer corner), the blush two wide, the edge
    # shaded; the bangs over the strip of forehead left of them (a white bar over the lock: 「那块白的还有点奇怪」)
    for x, y, c in FACE_NEAR:
        put(x, y, c)


def build(with_mask=False):
    """The design canvas; with_mask also the scissors' squares on it (step 9's, the point's)."""
    raw = read_back()
    assert raw.shape[:2] == (105, 77), raw.shape
    idx, pal = dv.kmeans(raw, K)
    out, ink = votes(idx, pal, HEIGHT)
    img = np.zeros(out.shape + (4,), np.uint8)
    m = out >= 0
    img[m, :3] = pal[out[m]]
    img[m, 3] = 255
    can = np.pad(img, ((1, 1), (1, 1), (0, 0)))
    can, _, _ = strips.complete_outline(can, color=tuple(int(v) for v in pal[ink]), feet=img.shape[0])
    ys, xs = np.nonzero(can[..., 3] > 0)
    fig = can[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    paint(fig, FACE_1)
    fig = lone(fig, set(FACE_1))
    fig = scissors(fig)
    paint(fig, {(FACE_X0 + i, y): ch for y, row in FACE.items() for i, ch in enumerate(row) if ch != "-"})
    paint(fig, NECK)
    fig, sc = league_scissors(fig, with_mask=True)
    for (x, y), ch in POINT.items():
        fig[y, x] = 0 if ch is None else (*C[ch], 255)
        sc[y, x] = ch is not None
    paint(fig, {(TORSO_X0 + i, y): TORSO_KEYS[ch] for y, row in TORSO.items() for i, ch in enumerate(row) if ch != "-"})
    feet = np.nonzero((fig[-FEET_ROWS:, :, 3] > 0).any(0))[0]
    mid_x = (feet.min() + feet.max()) / 2
    canvas = np.zeros((128, 128, 4), np.uint8)
    y0, x0 = SOLE_ROW + 1 - fig.shape[0], int(round(MID_COL - mid_x))
    canvas[y0:y0 + fig.shape[0], x0:x0 + fig.shape[1]] = fig
    face = np.zeros((128, 128), bool)
    r0, r1, c0, c1 = FACE_BOX
    face[r0:r1 + 1, c0:c1 + 1] = True
    clean_dark(canvas, face)                           # step 11
    mask = np.zeros((128, 128), bool)
    mask[y0:y0 + fig.shape[0], x0:x0 + fig.shape[1]] = sc
    lone_ink(canvas, face | mask)                      # step 12
    polish(canvas, mask)                               # step 14 (supersedes step 13's recolouring)
    if with_mask:
        return canvas, mask
    return canvas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    can = build()
    ys, xs = np.nonzero(can[..., 3] > 0)
    info = (f"{xs.max() - xs.min() + 1} x {ys.max() - ys.min() + 1} (rows {ys.min()}-{ys.max()}, cols {xs.min()}-{xs.max()}), "
            f"{len({tuple(p[:3]) for p in can[can[..., 3] > 0]})} colours")
    if a.check:
        old = np.asarray(Image.open(lp(OUT)).convert("RGBA"))
        print("identical" if np.array_equal(old, can) else "DIFFERENT", info)
        return
    os.makedirs(os.path.dirname(lp(OUT)), exist_ok=True)
    Image.fromarray(can).save(lp(OUT))
    print(OUT, info)


if __name__ == "__main__":
    main()
