#!/usr/bin/env python3
"""LeBlanc's design (assets/source/native/leblanc_native.png): Codex's design B cut to game size by whole rows and
columns, the face kept, the staff straightened and given back its right wing, the outline closed and cleaned.

    python tools/art/design_leblanc.py [--check] [--review OUT.png]

How it came about (2026-10-02): the user picked Codex's picture A (codex_picture/leblanc-model-A.png: League's idle,
the staff upright at her far side). Asked for a 45-row game-size sprite (MODEL_PROMPTS.md), Codex's image model drew
both versions on a ~17 px grid: A 86 rows, B 75 (codex_model/HANDOFF.md). The user liked them ("这两版我挺喜欢的 ...
就请使用这两版吧 可以牺牲其他部分的色素 脸部 法杖做好点"), picked B cut to 43 rows ("B 43 行") and then asked for the
staff to stand straight, the hole in the cape to go and the outline to be clean ("还有法杖是歪的 下面的披风那里少了一块",
"清理黑边保持干净"). Steps, all on Codex's own squares (no pixel redrawn but the shaft below the hand):
  1. codex_model/leblanc_design_B_1x.png: Codex's nine near-blacks -> one outline colour, shades closer than 16 merged;
  2. whole rows and columns deleted (league_camille's way, about 10% a step, the cheapest lines first - lines that
     differ least from a neighbour - never two neighbours in one step, a line whose deletion splits the figure
     charged): rows by region quotas (above the hair 1.3, the head 0.8, the torso 1.1, the skirt 1.3), columns by
     quotas left of the face / the face / right of it, until 38 rows from the hair's top to the soles (43 in all);
     never deleted: the lash, eye and mouth rows and the eyes' and mouth's columns (Codex's face stays as drawn) and
     the staff's two columns;
  3. the staff: the row cut moved the one-square gold shaft below the hand sideways and left dark squares in it
     ("歪") - redrawn straight with a darker gold every fourth row; the column cut took the right bat wing and the
     crystal's right outline - the left wing's squares mirrored about the shaft, 2 rows lower as Codex drew it;
  4. enclosed clear squares in the body (rows 24 down), and single enclosed squares anywhere, filled with the colour
     round them (a 6-square hole in the cape's lower left, one square between the staff's guard and its right wing); the far gold ear-cuff moved 3 rows down to the eyes' height (the row cut had left it above
     them: "耳边耳朵位置有点偏高了吧", the user picked "下移 3 行" of 2 / 3);
  5. strips.complete_outline (one outline square outside every light edge, nothing under the soles), then
     strips.clean_outline (one black ring, no crumbs, no doubled corners), the face's box never touched; then
     black pieces touching no colour (8-connected, up to 4 squares) go - the mirrored wing's tip outline landed
     apart from the wing ("法杖旁边多了一块黑色素") - and so does every edge square of the outline with no coloured
     square among its 8 neighbours (it outlines nothing: "这里也有多余的黑色方框", the left wing's tip);
  6. on the 128x128 canvas at 8x: the soles on row 99, the middle of the feet on column 64.
--check compares the result with the committed leblanc_native.png instead of writing it.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips  # noqa: E402

DRAFT = os.path.join(ROOT, "assets", "source", "leblanc", "codex_model", "leblanc_design_B_1x.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "leblanc_native.png")
OUTLINE = (6, 2, 18)
SOLE_ROW, MID_COL = 99, 64
# on Codex's 128x128 canvas: the hair's top row, the chin, the torso's last row; protected lines
HAIR, CHIN, TORSO = 33, 55, 74
FACE_ROWS = [46, 47, 48, 49, 51]                 # the lashes, the eyes, the mouth
FACE_COLS = [55, 56, 57, 60, 62, 63]             # the eyes and the mouth
SHAFT_COLS = [78, 79]                            # the staff's shaft (a two-column gold spiral)
COL_REGIONS = [(41, 50), (51, 66), (67, 87)]     # left of the face, the face, right of it
ROW_WEIGHTS = [1.3, 0.8, 1.1, 1.3]
TARGET_HAIR = 38                                 # rows from the hair's top to the soles
SPLIT_COST = 1000
# after the cut (cut coordinates): the left wing's box, the mirror axis (2x), the crystal's missing outline squares
WING_BOX, WING_AXIS2, WING_DY = (8, 16, 18, 21), 49, 2
CRYSTAL_OUTLINE, CRYSTAL_COLOUR = [(r, 27) for r in range(6, 12)], (0x2B, 0x01, 0x0E)
NAVY = {"2C40A3", "130F31", "1C1948", "201D4E", "060212"}
SHAFT = {"col": 24, "rows": range(26, 42), "wrap": (29, 33, 37), "clear": [(r, 26) for r in range(31, 42)]}
GOLD, GOLD_D, GOWN_EDGE = (0xF4, 0xAA, 0x45), (0xDE, 0x8D, 0x36), (0x39, 0x0C, 0x20)
FACE_BOX = (9, 19, 5, 15)                        # rows / cols of the face on the cut, kept by the outline passes
HOLES_FROM = 24
EAR = [(8, 16), (9, 16), (9, 17), (10, 16), (10, 17), (11, 16), (12, 16)]      # the far ear-cuff (cut coordinates)
EAR_OUTLINE = [(7, 16), (8, 17), (9, 18), (10, 18), (11, 17), (12, 17)]
EAR_DY = 3
FEET_MID = 10                                    # the cut's column between the two heels


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1], ys.min(), xs.min()


def clean(a, tol=16):
    a = a.copy()
    op = a[..., 3] > 0
    dark = op & (a[..., :3].astype(int).max(-1) < 34)
    a[dark, :3] = OUTLINE
    cols, inv, cnt = np.unique(a[op][:, :3].astype(np.int32), axis=0, return_inverse=True, return_counts=True)
    keep, mapping = [], np.zeros(len(cols), np.int32)
    for k in np.argsort(-cnt):
        for j, kc in enumerate(keep):
            if np.sqrt(((kc - cols[k]) ** 2).sum()) <= tol:
                mapping[k] = j
                break
        else:
            keep.append(cols[k])
            mapping[k] = len(keep) - 1
    a[op, :3] = np.array(keep, np.uint8)[mapping[inv.ravel()]]
    a[op, 3] = 255
    a[~op] = 0
    return a


def pieces(op):
    H, W = op.shape
    big = H * W + 1
    lab = np.where(op, np.arange(H * W).reshape(H, W), big)
    while True:
        p = np.pad(lab, 1, constant_values=big)
        m = lab.copy()
        for dy in (0, 1, 2):
            for dx in (0, 1, 2):
                m = np.minimum(m, p[dy:dy + H, dx:dx + W])
        m = np.where(op, m, big)
        if (m == lab).all():
            return len(np.unique(lab[op]))
        lab = m


def line_cost(a, axis):
    b = a if axis == 0 else a.transpose(1, 0, 2)
    key = np.where(b[..., 3:4] > 0, b[..., :3].astype(np.int32), -1)
    diff = (key[1:] != key[:-1]).any(-1).sum(1)
    n = b.shape[0]
    return np.array([min(diff[i - 1] if i > 0 else 1e6, diff[i] if i < n - 1 else 1e6) for i in range(n)], float)


def pick(cost, k, allowed):
    n, INF = len(cost), float("inf")
    c = np.array([cost[i] if i in allowed else INF for i in range(n)])
    dp = np.full((n + 1, k + 1), INF)
    take = np.zeros((n + 1, k + 1), bool)
    dp[0][0] = 0.0
    for i in range(1, n + 1):
        for j in range(k + 1):
            best, tk = dp[i - 1][j], False
            if j > 0 and c[i - 1] < INF:
                prev = dp[i - 2][j - 1] if i >= 2 else (0.0 if j == 1 else INF)
                if prev + c[i - 1] < best:
                    best, tk = prev + c[i - 1], True
            dp[i][j], take[i][j] = best, tk
    if dp[n][k] == INF:
        return []
    out, i, j = [], n, k
    while j > 0 and i > 0:
        if take[i][j]:
            out.append(i - 1)
            i -= 2
            j -= 1
        else:
            i -= 1
    return sorted(out)


def delete(a, axis, sets, protect):
    cost = line_cost(a, axis)
    op = a[..., 3] > 0
    base = pieces(op)
    tested = set()
    gone = []
    for _ in range(12):
        gone, carry = [], 0
        for s, q in sets:
            want, got = q + carry, []
            while want > 0:
                got = pick(cost, want, (s - protect) - {x for g in gone for x in (g - 1, g, g + 1)})
                if got:
                    break
                want -= 1
            carry = q + carry - len(got)
            gone += got
        bad = False
        for i in gone:
            if i not in tested:
                tested.add(i)
                if pieces(np.delete(op, i, axis=axis)) > base:
                    cost[i] += SPLIT_COST
                    bad = True
        if not bad:
            break
    keep = [i for i in range(a.shape[axis]) if i not in set(gone)]
    return np.take(a, keep, axis=axis), keep


def quotas(k, sizes):
    q = [int(round(k * s / sum(sizes))) for s in sizes]
    while sum(q) > k:
        q[int(np.argmax(q))] -= 1
    while sum(q) < k:
        q[int(np.argmax(sizes))] += 1
    return q


def shrink(a, rows_t, cols_t, row_regions, prot_rows, prot_cols, col_regions, step=0.9):
    rid, cid = np.arange(a.shape[0]), np.arange(a.shape[1])
    while a.shape[0] > rows_t or a.shape[1] > cols_t:
        shape0 = a.shape
        k_r = a.shape[0] - max(rows_t, int(round(a.shape[0] * step)))
        k_c = a.shape[1] - max(cols_t, int(round(a.shape[1] * step)))
        if k_r:
            groups = [[i for i in range(a.shape[0]) if lo <= rid[i] <= hi] for lo, hi in row_regions]
            q = quotas(k_r, [len(g) * w for g, w in zip(groups, ROW_WEIGHTS)])
            prot = {i for i in range(a.shape[0]) if rid[i] in prot_rows} | {0, a.shape[0] - 1}
            a, keep = delete(a, 0, [(set(g), n) for g, n in zip(groups, q)], prot)
            rid = rid[keep]
        if k_c:
            groups = [[i for i in range(a.shape[1]) if lo <= cid[i] <= hi] for lo, hi in col_regions]
            q = quotas(k_c, [len(g) for g in groups])
            prot = {i for i in range(a.shape[1]) if cid[i] in prot_cols} | {0, a.shape[1] - 1}
            a, keep = delete(a, 1, [(set(g), n) for g, n in zip(groups, q)], prot)
            cid = cid[keep]
        if a.shape == shape0:
            break
    return a


def hexs(p):
    return "%02X%02X%02X" % tuple(int(v) for v in p[:3])


def staff(a):
    out = np.zeros((a.shape[0], max(a.shape[1], WING_AXIS2 - WING_BOX[2] + 1), 4), np.uint8)
    out[:, :a.shape[1]] = a
    for r, c in CRYSTAL_OUTLINE:
        if out[r, c, 3] == 0:
            out[r, c] = CRYSTAL_COLOUR + (255,)
    r0, r1, c0, c1 = WING_BOX
    for r in range(r0, r1 + 1):
        for c in range(c0, c1 + 1):
            if a[r, c, 3] and hexs(a[r, c]) in NAVY and out[r + WING_DY, WING_AXIS2 - c, 3] == 0:
                out[r + WING_DY, WING_AXIS2 - c] = a[r, c]
    c = SHAFT["col"]
    for r, cc in SHAFT["clear"]:
        out[r, cc] = 0
    for r in SHAFT["rows"]:
        out[r, c] = (GOLD_D if r in SHAFT["wrap"] else GOLD) + (255,)
        for side in (c - 1, c + 1):
            if not (out[r, side, 3] and tuple(out[r, side, :3]) == GOWN_EDGE):
                out[r, side] = OUTLINE + (255,)
    return out


def fill_holes(a):
    a = a.copy()
    H, W = a.shape[:2]
    clear = a[..., 3] == 0
    seen = np.zeros_like(clear)
    for y in range(H):
        for x in range(W):
            if not clear[y, x] or seen[y, x]:
                continue
            stack, reg, edge = [(y, x)], [], False
            seen[y, x] = True
            while stack:
                cy, cx = stack.pop()
                reg.append((cy, cx))
                edge |= cy in (0, H - 1) or cx in (0, W - 1)
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < H and 0 <= nx < W and clear[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((ny, nx))
            if edge or len(reg) > 12 or (min(r for r, _ in reg) < HOLES_FROM and len(reg) > 1):
                continue
            cols = {}
            for cy, cx in reg:
                rng = (-1, 0, 1) if len(reg) == 1 else range(-2, 3)
                for dy in rng:
                    for dx in rng:
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < H and 0 <= nx < W and a[ny, nx, 3] and (len(reg) == 1 or a[ny, nx, :3].max() > 40):
                            cols[hexs(a[ny, nx])] = cols.get(hexs(a[ny, nx]), 0) + 1
            if cols:
                best = max(cols, key=cols.get)
                for cy, cx in reg:
                    a[cy, cx] = tuple(int(best[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
    return a


def black_crumbs(a, keep):
    """Clear dark pieces that touch no coloured square (8-connected, at most 4 squares) and dark squares whose only
    opaque neighbour is one dark square (a tail hanging off the outline), outside `keep`."""
    a = a.copy()
    H, W = a.shape[:2]
    dark = (a[..., 3] > 0) & (a[..., :3].max(-1) < 40)
    seen = np.zeros_like(dark)
    for y in range(H):
        for x in range(W):
            if not dark[y, x] or seen[y, x]:
                continue
            stack, reg, touches = [(y, x)], [], False
            seen[y, x] = True
            while stack:
                cy, cx = stack.pop()
                reg.append((cy, cx))
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = cy + dy, cx + dx
                        if (dy or dx) and 0 <= ny < H and 0 <= nx < W and a[ny, nx, 3]:
                            if dark[ny, nx]:
                                if not seen[ny, nx]:
                                    seen[ny, nx] = True
                                    stack.append((ny, nx))
                            else:
                                touches = True
            if not touches and len(reg) <= 4 and not any(keep[r, c] for r, c in reg):
                for r, c in reg:
                    a[r, c] = 0
    # an edge square of the outline that outlines nothing - no coloured square among its 8 neighbours - is a stray
    # (the wing tip's black square: "这里也有多余的黑色方框"); repeated so a chain of them goes too
    while True:
        op = a[..., 3] > 0
        dark = op & (a[..., :3].max(-1) < 40)
        colour = op & ~dark
        gone = []
        for y in range(H):
            for x in range(W):
                if not dark[y, x] or keep[y, x]:
                    continue
                edge = any(not (0 <= y + dy < H and 0 <= x + dx < W) or not op[y + dy, x + dx]
                           for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                near = any(0 <= y + dy < H and 0 <= x + dx < W and colour[y + dy, x + dx]
                           for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx)
                if edge and not near:
                    gone.append((y, x))
        if not gone:
            return a
        for y, x in gone:
            a[y, x] = 0


def fill_single(a):
    """A clear square with all four neighbours drawn (left by the outline passes) takes their commonest colour."""
    a = a.copy()
    op = a[..., 3] > 0
    H, W = op.shape
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if not op[y, x] and op[y - 1, x] and op[y + 1, x] and op[y, x - 1] and op[y, x + 1]:
                nb = [hexs(a[y + dy, x + dx]) for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))]
                best = max(set(nb), key=nb.count)
                a[y, x] = tuple(int(best[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
    return a


def build():
    raw = clean(np.asarray(Image.open(lp(DRAFT)).convert("RGBA")))
    des, top, left = crop(raw)
    regions = [(0, HAIR - top - 1), (HAIR - top, CHIN - top), (CHIN - top + 1, TORSO - top),
               (TORSO - top + 1, des.shape[0] - 1)]
    hair0 = des.shape[0] - (HAIR - top)
    f = TARGET_HAIR / hair0
    cut = shrink(des.copy(), int(round(des.shape[0] * f)), int(round(des.shape[1] * f ** 0.9)), regions,
                 {r - top for r in FACE_ROWS}, {c - left for c in FACE_COLS + SHAFT_COLS},
                 [(lo - left, hi - left) for lo, hi in COL_REGIONS])
    a = fill_holes(staff(cut))
    ear = {p: a[p].copy() for p in EAR}
    for p in EAR + EAR_OUTLINE:
        a[p] = 0
    for (r, c), v in ear.items():
        a[r + EAR_DY, c] = v
    a = np.pad(a, ((2, 2), (2, 2), (0, 0)))
    keep = np.zeros(a.shape[:2], bool)
    r0, r1, c0, c1 = FACE_BOX
    keep[r0 + 2:r1 + 2, c0 + 2:c1 + 2] = True
    feet = int(np.nonzero(a[..., 3].any(1))[0].max())
    b, _, _ = strips.complete_outline(a, color=OUTLINE, feet=feet, keep=keep)
    b, _ = strips.clean_outline(b, OUTLINE, keep=keep)
    b = fill_single(black_crumbs(b, keep))
    fig, ftop, fleft = crop(b)
    mid = FEET_MID + 2 - fleft
    can = np.zeros((128, 128, 4), np.uint8)
    y0, x0 = SOLE_ROW + 1 - fig.shape[0], MID_COL - mid
    can[y0:y0 + fig.shape[0], x0:x0 + fig.shape[1]] = fig
    return can, fig


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review")
    a = ap.parse_args()
    can, fig = build()
    big = Image.fromarray(can).resize((1024, 1024), Image.NEAREST)
    n = len({tuple(c) for c in fig[fig[..., 3] > 0][:, :3]})
    print(f"design {fig.shape[0]} x {fig.shape[1]}, {n} colours")
    if a.check:
        old = np.asarray(Image.open(lp(OUT)).convert("RGBA"))
        same = np.array_equal(old, np.asarray(big))
        print("same as", OUT, same)
        sys.exit(0 if same else 1)
    big.save(lp(OUT))
    print("written", OUT)
    if a.review:
        Z = 8
        im = Image.new("RGB", (fig.shape[1] * Z + 40, fig.shape[0] * Z + 40), (92, 98, 86))
        f = Image.fromarray(fig).resize((fig.shape[1] * Z, fig.shape[0] * Z), Image.NEAREST)
        im.paste(f, (20, 20), f)
        ImageDraw.Draw(im).text((4, 4), "leblanc_native", fill=(255, 255, 255))
        im.save(a.review)


if __name__ == "__main__":
    main()
