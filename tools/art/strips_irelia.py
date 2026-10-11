#!/usr/bin/env python3
"""Irelia's game strips from Codex's telekinetic redraw (assets/source/irelia/codex_strips_v2).

    python tools/art/strips_irelia.py               # write assets/source/native/irelia_<tag>.png, irelia_cells.json
                                                    # and irelia_native.png (the idle's first frame)
    python tools/art/strips_irelia.py --check       # compare with the committed files instead of writing
    python tools/art/strips_irelia.py --review DIR  # irelia_strips_review.gif and _frames.png (every frame at 4x)

How it came about (2026-10-12). The user redid the model (reference/user_model.png): in League Irelia drives the
blades floating round her by will, her hands stay empty (「英雄联盟里面刀妹是通过意念驱动身后的武器来攻击的 我们现在做的全
是错的」), and Codex redrew every strip from it (raw/*.png, manifest.json: 51 frames, the source crop of each). Codex's
own 1x frames were the commonest colour of 8x8 tiles laid over drafts drawn at about 5.6 px a square - specks; read
back on their own grid the drafts are clean, 84 rows from the blade tips to the soles, which the user called the best
(「这个最完美」) - but twice the height of the other heroes. So:
  * read-back: each frame's crop on its own grid (design_riven's border peaks with a fixed 5.6 px square - its own size
    estimate failed on half the frames), the chroma-key green of the skill / ult / death sheets made clear, every
    square snapped to Codex's 20 colours (letters KEYS);
  * the size: the body at 2:1 - each game square from the 2x2 read-back squares under it (the phase with the fewest
    split blocks; a tie between colours goes to the colour most of its decided neighbours share, so specks follow the
    shape) - and the head at the drafts' own size, as the pack's other heroes carry a big head;
  * the head: one head for every frame (design_v2/head.txt), the drafts' 3/4 face looking right with the tiara gem and
    two-square cyan eyes; the user on the first tries: 「嘴这里凸出来一块有点怪」, 「我说的是这种圆滑一点的」, 「你这替换的
    也不对啊 你自己做一个自然点的像刀妹的吧」, then on this one 「脸部差不多了 脖子画一个啊」 and, on a two-row neck that
    lifted the head, 「参考之前codex的图做吧」: the neck as in the draft, one row of skin in shadow under the chin and
    the red high collar at once. The idle keeps her hand at the cheek (as drawn); the actions use head_nohand.txt,
    placed from each draft's eyes; lying (the death's last four frames) it is turned a quarter, crown to the right;
  * the idle is drawn by hand (the user: 「都给我精修好了 每个部位」): design_v2/body_idle.txt, every 2:1 square decided
    from its block and the part it belongs to (collar and gem, breastplates, tabard with white edges and its tip, the
    shoulder hook, the arm hanging to the open hand, the long hair, the hip flaps, knee stars, boots with white ankle
    bands and toe caps), and the four blades redrawn clean (BLADES), the top and upper-left ones moved out from behind
    the head; the eight idle frames are that one still figure with each blade bobbing a row, out of step (BOB);
  * the actions: the draft split into its body and the floating blades (the pieces apart from the body), each reduced,
    a blade the head would cover moved away from it, the outline closed round the silhouette (a clear square next to a
    coloured one turns ink: the block vote drops the drafts' one-pixel lines).
Every frame stands with its lowest row on 99 and its standing point on column 64 (the idle: the feet's middle; an
action: Codex's pivot at the same fraction of the figure's width); cells 112x84, the point at (52, 66).
"""
import argparse
import json
import math
import os
import sys
from collections import Counter

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import design_riven as DR  # noqa: E402
import rigkit as K  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "irelia")
CODEX = os.path.join(SRC, "codex_strips_v2")
DESIGN = os.path.join(SRC, "design_v2")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
HERO = "irelia"
TAGS = ["idle", "run", "attack", "skill", "skill2", "skill2_w", "ult", "hit", "dead"]
PIVOT, SOLES = (64, 88), 99
CELL, CELL_PIVOT = (112, 84), (52, 66)
SQUARE = 5.6                     # the drafts' own pixel size, in source pixels

PAL_HEX = json.load(open(K.lp(os.path.join(CODEX, "palette.json"))))
KEYS = "0abcdefghijklmnopqrst"   # ink; navy a-d; crimson e-h; silver i-m; cyan n-p; skin q-s (palette.json order);
EYE = (9, 144, 186)              # t: the eyes' dark cyan, one step off n so it is theirs alone (import_native.EYES)
RGB = np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in PAL_HEX] + [list(EYE)], int)
MAT = {".": "."}
for _m, _ls in {"ink": "0", "navy": "abcd", "red": "efgh", "silver": "ijklm", "cyan": "nopt", "skin": "qrs"}.items():
    for _l in _ls:
        MAT[_l] = _m
PRI = {c: i for i, c in enumerate("topnmlskrqhgjfieddcba0")}      # a tie in a block: the thin bright detail first
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
N8 = [(dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx]

# the idle's four blades at 2:1: (2:1 row, first 2:1 column, squares); OFFSET moves a blade in game squares
BLADES = {
    "top": [(0, 12, "0"), (1, 10, "0l0"), (2, 9, "0mk0"), (3, 9, "0lg0"), (4, 8, "0kgg0"), (5, 8, "0bbgl0"),
            (6, 8, "0bbbg0"), (7, 9, "0bblg0"), (8, 10, "0bko0"), (9, 11, "0nk0"), (10, 12, "00")],
    "upper_left": [(5, 1, "0"), (6, 1, "0g0"), (7, 1, "0hg0"), (8, 1, "0bgl0"), (9, 2, "0bbl0"), (10, 2, "0abbl0"),
                   (11, 3, "0abgl0"), (12, 4, "0aoo0"), (13, 5, "0bg0"), (14, 6, "0bg0"), (15, 7, "00")],
    "lower_left": [(20, 6, "0"), (21, 5, "0g0"), (22, 5, "0g0"), (23, 3, "0po0"), (24, 2, "0kol0"), (25, 1, "0bba0"),
                   (26, 0, "0bbgg0"), (27, 0, "0gbg0"), (28, -1, "0ggf0"), (29, -1, "0gg0"), (30, -1, "0g0"),
                   (31, -1, "00")],
    "lower_right": [(21, 25, "0"), (22, 24, "0gg0"), (23, 25, "0gk0"), (24, 25, "0bbl0"), (25, 26, "0blo0"),
                    (26, 26, "0goo0"), (27, 27, "0bkg0"), (28, 28, "0gg0"), (29, 29, "0gg0"), (30, 29, "0g0"),
                    (31, 30, "00")],
}
OFFSET = {"top": (-3, -6), "upper_left": (0, -3), "lower_left": (0, 0), "lower_right": (0, 0)}
BOB = {"upper_left": [0, 0, -1, -1, -1, -1, 0, 0], "top": [0, -1, -1, -1, 0, 0, 0, 0],
       "lower_left": [0, 0, 0, -1, -1, -1, -1, 0], "lower_right": [-1, -1, 0, 0, 0, 0, -1, -1]}
BODY_AT = (9, 10)                # the idle's 2:1 body square (r, c) -> work square (r + 9, c + 10)
HEAD_NECK = 16                   # the head table's neck row; in the idle on the work row over the collar (21)


def table(path):
    rows = [r.rstrip("\r\n") for r in open(K.lp(path), encoding="utf-8")]     # a checkout may bring CRLF
    w = max(len(r) for r in rows)
    return np.array([list(r.ljust(w, ".")) for r in rows])


def rgba(L):
    a = np.zeros(L.shape + (4,), np.uint8)
    for k, ch in enumerate(KEYS):
        m = L == ch
        a[m, :3] = RGB[k]
        a[m, 3] = 255
    return a


# ------------------------------------------------------------------------------------------------- read-back
def regrid(a):
    op = a[..., 3] >= 128
    ys, xs = np.nonzero(op)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    bx = DR.boundaries(DR.profile(a, op, 1), x0, x1, SQUARE)
    by = DR.boundaries(DR.profile(a, op, 0), y0, y1, SQUARE)
    out = np.full((len(by) - 1, len(bx) - 1), ".", "<U1")
    for j in range(len(by) - 1):
        cy = (by[j] + by[j + 1]) // 2
        for i in range(len(bx) - 1):
            cx = (bx[i] + bx[i + 1]) // 2
            win = a[max(0, cy - 1):cy + 2, max(0, cx - 1):cx + 2].reshape(-1, 4)
            opq = win[:, 3] >= 128
            if opq.sum() * 2 > len(win):
                c = np.median(win[opq][:, :3], axis=0)
                out[j, i] = KEYS[int(((RGB[:20] - c) ** 2).sum(1).argmin())]     # never the eyes' own t
    ys, xs = np.nonzero(out != ".")
    return out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def readbacks():
    man = json.load(open(K.lp(os.path.join(CODEX, "manifest.json"))))
    sheets, out = {}, {}
    for t in TAGS:
        res = []
        for fr in man["animations"][t]["frames"]:
            src = fr["source"]
            if src not in sheets:
                a = np.asarray(Image.open(K.lp(os.path.join(CODEX, src))).convert("RGBA")).copy()
                rgb = a[..., :3].astype(int)
                a[(rgb[..., 1] - np.maximum(rgb[..., 0], rgb[..., 2])) > 90, 3] = 0     # the chroma-key green
                sheets[src] = a
            x0, y0, x1, y1 = fr["source_crop"]
            res.append((regrid(sheets[src][y0:y1, x0:x1].copy()), fr))
        out[t] = res
    return out


# ------------------------------------------------------------------------------------------------- 2:1 reduction
def split_count(L, oy, ox):
    H, W = L.shape
    P = np.pad(L, ((oy, 2), (ox, 2)), constant_values=".")
    n = 0
    for r in range((H + oy + 1) // 2):
        for c in range((W + ox + 1) // 2):
            blk = [P[2 * r + i, 2 * c + j] for i in range(2) for j in range(2)]
            if blk.count(".") >= 2:
                continue
            cnt = Counter(blk).most_common()
            if not (cnt[0][1] >= 3 or (cnt[0][1] == 2 and len(cnt) == 3)):
                n += 1
    return n


def best_phase(L):
    return min(((oy, ox) for oy in (0, 1) for ox in (0, 1)), key=lambda p: split_count(L, *p))


def reduce2(L, oy, ox, rounds=3):
    """Each square from its 2x2 block: 3+ clear -> clear; a letter with 3+, or 2 against two different -> it; a tie
    -> the block's letter that most of its decided 8 neighbours share (same letter x2, same material x1, its own count
    x1.5), the brighter detail first on an equal score."""
    H, W = L.shape
    P = np.pad(L, ((oy, 2), (ox, 2)), constant_values=".")
    R, C = (H + oy + 1) // 2, (W + ox + 1) // 2
    out = np.full((R, C), "?", "<U1")
    ties = {}
    for r in range(R):
        for c in range(C):
            blk = [P[2 * r + i, 2 * c + j] for i in range(2) for j in range(2)]
            cnt = Counter(blk).most_common()
            if blk.count(".") >= 3:
                out[r, c] = "."
            elif cnt[0][1] >= 3 or (cnt[0][1] == 2 and len(cnt) == 3 and cnt[0][0] != "."):
                out[r, c] = cnt[0][0]
            else:
                ties[(r, c)] = blk
    for _ in range(rounds):
        for (r, c), blk in ties.items():
            best = None
            for x in sorted(set(blk)):
                s = blk.count(x) * 1.5
                for dy, dx in N8:
                    y2, x2 = r + dy, c + dx
                    if 0 <= y2 < R and 0 <= x2 < C and out[y2, x2] != "?":
                        v = out[y2, x2]
                        s += 2 if v == x else (1 if MAT.get(v) == MAT.get(x) else 0)
                key = (s, -PRI.get(x, 50) if x != "." else -60)
                if best is None or key > best[0]:
                    best = (key, x)
            out[r, c] = best[1]
    out[out == "?"] = "."
    return out


def despeckle(L, passes=2):
    """A square whose material none of its 4 neighbours share, with 3+ of them one other material (not ink), takes
    that material's commonest shade around it; a shade speck among 5+ squares of its material in one other shade takes
    that shade. Cyan (eyes, gems) never changes."""
    L = L.copy()
    H, W = L.shape
    for _ in range(passes):
        out = L.copy()
        for y in range(1, H - 1):
            for x in range(1, W - 1):
                c = L[y, x]
                if c == "." or MAT[c] == "cyan":
                    continue
                m = MAT[c]
                n4 = [L[y + dy, x + dx] for dy, dx in N4]
                n8 = [L[y + dy, x + dx] for dy, dx in N8]
                if not any(MAT[v] == m for v in n4):
                    mats = Counter(MAT[v] for v in n4 if v != ".")
                    if mats:
                        best, cnt = mats.most_common(1)[0]
                        if cnt >= 3 and best != "ink":
                            out[y, x] = Counter(v for v in n8 if MAT[v] == best).most_common(1)[0][0]
                            continue
                if m != "ink" and c not in n8:
                    same = Counter(v for v in n8 if MAT[v] == m)
                    if same and same.most_common(1)[0][1] >= 5:
                        out[y, x] = same.most_common(1)[0][0]
        L = out
    return L


def close_outline(G):
    out = G.copy()
    H, W = G.shape
    for y, x in zip(*np.nonzero(G == ".")):
        for dy, dx in N4:
            yy, xx = y + dy, x + dx
            if 0 <= yy < H and 0 <= xx < W and G[yy, xx] not in (".", "0"):
                out[y, x] = "0"
                break
    return out


# ------------------------------------------------------------------------------------------------- the idle
def idle_frame(head, body, k):
    G = np.full((52, 60), ".", "<U1")
    for name in ("top", "upper_left", "lower_left", "lower_right"):          # behind the body
        oy, ox = OFFSET[name]
        for r, c0, s in BLADES[name]:
            for i, ch in enumerate(s):
                G[r + BODY_AT[0] + oy + BOB[name][k], c0 + i + BODY_AT[1] + ox] = ch
    m = body != "."
    G[BODY_AT[0]:BODY_AT[0] + body.shape[0], BODY_AT[1]:BODY_AT[1] + body.shape[1]][m] = body[m]
    r0 = 12 + BODY_AT[0] - HEAD_NECK
    m = head != "."
    G[r0:r0 + head.shape[0], 20:20 + head.shape[1]][m] = head[m]
    return G


# ------------------------------------------------------------------------------------------------- the actions
def eyes(L):
    """The draft's eyes: cyan squares touching the topmost face (a skin piece of 8+ squares) in the figure's top 45%."""
    ys, _ = np.nonzero(L != ".")
    sk = np.isin(L, list("qrs"))
    e = np.isin(L, list("nop")) & ndimage.binary_dilation(sk, np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]))
    e[int(ys.min() + 0.45 * (ys.max() - ys.min())):] = False
    if not e.any():
        return None
    lab, _ = ndimage.label(sk, np.ones((3, 3)))
    best = None
    for y, x in zip(*np.nonzero(e)):
        for dy, dx in N4:
            if 0 <= y + dy < L.shape[0] and 0 <= x + dx < L.shape[1] and lab[y + dy, x + dx]:
                k = lab[y + dy, x + dx]
                if (lab == k).sum() >= 8 and (best is None or y < best[0]):
                    best = (y, k)
    if best is None:
        return None
    yy, xx = np.nonzero(ndimage.binary_dilation(lab == best[1], np.ones((3, 3))) & e)
    return float(yy.mean()), float(xx.mean())


def action_frame(L, head, lying_head, mode):
    """mode: "head" (upright head on the eyes), "lying" (the quarter-turned head) or None. Returns the work table,
    the reduction's box in it (row, col, rows, cols)."""
    pad = 24
    oy, ox = best_phase(L)
    lab, n = ndimage.label(L != ".", np.ones((3, 3)))
    sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    body_id = int(np.argmax(sizes)) + 1
    body = despeckle(reduce2(np.where(lab == body_id, L, "."), oy, ox))
    H, W = body.shape
    G = np.full((H + 2 * pad, W + 2 * pad), ".", "<U1")
    hm = np.zeros(G.shape, bool)
    hpos = None
    if mode == "head":
        e = eyes(L)
        if e is not None:
            r0 = int(round((e[0] + oy) / 2.0 + 1.5)) - HEAD_NECK + pad
            c0 = int(round((e[1] + ox) / 2.0)) - 10 + pad
            hpos = (r0, c0)
            hm[r0:r0 + head.shape[0], c0:c0 + head.shape[1]] = head != "."
    for i in range(1, n + 1):
        if i == body_id or sizes[i - 1] < 6:
            continue
        piece = despeckle(reduce2(np.where(lab == i, L, "."), oy, ox))
        m = np.zeros(G.shape, bool)
        m[pad:pad + H, pad:pad + W] = piece != "."
        if not m.any():
            continue
        dy = dx = 0
        if hpos is not None and (m & hm).sum() > 0.15 * m.sum():
            ys, xs = np.nonzero(m)
            vy, vx = ys.mean() - (hpos[0] + 9), xs.mean() - (hpos[1] + 9)
            norm = math.hypot(vy, vx) or 1.0
            for step in range(1, 16):
                sy, sx = int(round(vy / norm * step)), int(round(vx / norm * step))
                if (np.roll(np.roll(m, sy, 0), sx, 1) & hm).sum() <= 0.15 * m.sum():
                    dy, dx = sy, sx
                    break
        sub = np.full(G.shape, ".", "<U1")
        sub[pad:pad + H, pad:pad + W] = piece
        sub = np.roll(np.roll(sub, dy, 0), dx, 1)
        G = np.where(sub != ".", sub, G)
    G[pad:pad + H, pad:pad + W] = np.where(body != ".", body, G[pad:pad + H, pad:pad + W])
    if hpos is not None:
        m = head != "."
        G[hpos[0]:hpos[0] + head.shape[0], hpos[1]:hpos[1] + head.shape[1]][m] = head[m]
    if mode == "lying":
        ys, xs = np.nonzero(np.isin(G, list("nop")))
        sel = xs > pad + W * 0.6
        if sel.any():
            r0, c0 = int(ys[sel].mean()) - 11, int(xs[sel].mean()) - 5
        else:       # no eye left in the reduction (the last frame): where it sits a frame before, from the bottom right
            r0, c0 = pad + H - 16, pad + W - 11
        m = lying_head != "."
        G[r0:r0 + lying_head.shape[0], c0:c0 + lying_head.shape[1]][m] = lying_head[m]
    return close_outline(G), (pad, pad, H, W)


def place(G, px):
    """A work table onto the 128 canvas: its lowest row on SOLES, column px on PIVOT[0]."""
    ys, xs = np.nonzero(G != ".")
    out = np.full((128, 128), ".", "<U1")
    out[ys + SOLES - ys.max(), xs + PIVOT[0] - int(round(px))] = G[ys, xs]
    return out


def build():
    head = table(os.path.join(DESIGN, "head.txt"))
    head_nohand = table(os.path.join(DESIGN, "head_nohand.txt"))
    lying = np.rot90(head_nohand, k=-1)
    body = table(os.path.join(DESIGN, "body_idle.txt"))
    rb = readbacks()
    frames, ms = {}, {}
    f0 = idle_frame(head, body, 0)
    ys, xs = np.nonzero(f0 != ".")
    feet = np.nonzero((f0[ys.max() - 2:ys.max() + 1] != ".").any(0))[0]
    mid = (feet.min() + feet.max()) / 2.0
    frames["idle"] = [place(idle_frame(head, body, k), mid) for k in range(8)]
    ms["idle"] = [fr["ms"] for _, fr in rb["idle"]]
    for t in TAGS[1:]:
        res = []
        for k, (L, fr) in enumerate(rb[t]):
            mode = "lying" if (t == "dead" and k >= 4) else "head"
            G, (r0, c0, H, W) = action_frame(L, head_nohand, lying, mode)
            x0, x1 = fr["bbox"][0], fr["bbox"][2]
            res.append(place(G, c0 + (fr["pivot"][0] - x0) / float(x1 - x0) * W))
        frames[t] = res
        ms[t] = [fr["ms"] for _, fr in rb[t]]
    return {t: [rgba(L) for L in frs] for t, frs in frames.items()}, ms


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review")
    a = ap.parse_args()
    built, ms = build()
    if a.review:
        os.makedirs(K.lp(a.review), exist_ok=True)
        K.review_gif([(t, built[t]) for t in TAGS], ms, K.lp(os.path.join(a.review, f"{HERO}_strips_review.gif")))
        sheet(built, os.path.join(a.review, f"{HERO}_strips_review_frames.png"))
        print("wrote the review in", a.review)
        return
    bad = K.write_strips(HERO, built, ms, NATIVE, CELL, CELL_PIVOT, PIVOT, check=a.check)
    design = Image.fromarray(built["idle"][0])
    dpath = os.path.join(NATIVE, f"{HERO}_native.png")
    if a.check:
        if not np.array_equal(np.asarray(Image.open(K.lp(dpath)).convert("RGBA")), np.asarray(design)):
            bad.append("native")
        print("differs:", bad or "nothing")
    else:
        design.save(K.lp(dpath))
        print("wrote", ", ".join(f"{t} {len(built[t])}" for t in TAGS))


def sheet(built, path, z=4):
    rows = [(t, built[t]) for t in TAGS]
    x0, x1, y0, y1 = K.crop_box([f for _, frs in rows for f in frs])
    W, H = (x1 - x0) * z, (y1 - y0) * z
    n = max(len(frs) for _, frs in rows)
    img = Image.new("RGB", (70 + n * (W + 4), len(rows) * (H + 6) + 6), (40, 40, 40))
    d = ImageDraw.Draw(img)
    for r, (t, frs) in enumerate(rows):
        Y = 6 + r * (H + 6)
        d.text((4, Y + 4), t, fill=(255, 255, 255))
        for i, f in enumerate(frs):
            tile = Image.new("RGBA", (W, H), (110, 120, 108, 255))
            tile.alpha_composite(Image.fromarray(f[y0:y1, x0:x1]).resize((W, H), Image.NEAREST))
            img.paste(tile.convert("RGB"), (70 + i * (W + 4), Y))
    img.save(K.lp(path))


if __name__ == "__main__":
    main()
