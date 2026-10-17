#!/usr/bin/env python3
"""Kai'Sa's second design: Codex's slimmer draft A, cut to 42 rows the way the first design was (2026-10-03).

    python tools/art/design_kaisa_v2.py [--check]

The user: 「卡萨也是同样问题 身宽体胖 脸大」 (the first design: 44 rows, the head 23 of them, 932 squares). Codex redrew
her after assets/source/kaisa/MODEL_V2.md; the user took draft A (codex_model_v2/kaisa_design_A.png: 52 rows on its own
22 px grid). Read first by sampling it at 42 rows (one game pixel the middle of a 1.24-square block), the face, the
shoulder gems and the claws broke into specks; the actions built on that read showed it (「各种模型丢失 走路怪异 模型异常
你真的修好了？？」). So, as the first design (tools/art/design_kaisa.py, "B44"), the draft is read on its own grid and
whole rows and columns are taken out until it is 42 rows (the user's pick among 42 / 44 / 46: 「42 格」):
1. the draft read back on its own grid (the skill's regrid.py), Codex's green ground and its fringe keyed out;
2. its colours merged to MAXC (design_kaisa.merge_palette, Lab), the eye squares as drawn (EYES);
3. whole rows, then columns (or the other way) deleted by design_akali.dp_keep: never two neighbours, never the face,
   the eyes, the magenta glow and the gold trims weighted (design_kaisa.cut);
4. one outline; on the 128x128 canvas at 8x: the soles on row 99, the middle of the feet on column 64;
5. the head top: where the hair meets the near pod's left side the cut left a notch of ground (the user, first to
   Codex 「头发这里少一块」, then 「卡莎头顶少一块模型」); fills of that corner stood up as a comb or a bump (「卡莎公鸡
   头？」「头顶凸出来的那一块 不难看吗」). The user: 「你把护翼往两侧扩出去一点不就能改了吗」 - so the pods move two squares
   apart (PODS_OUT) and the crown between them is drawn round by hand (CROWN, the user's pick 「用右图」 with its seams
   mended); the far eye as big as the near one (EYE_FAR: 「眼睛也是一大一小」); the face's two holes skin (FACE_FILL:
   「卡莎的脸部丢失了一块模型」「还有嘴的右下方也少」); the outline closed once more.
Writes assets/source/kaisa/design_v2/kaisa_design_v2.png and _1x. --check compares with the files.
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
import design_kaisa as D  # noqa: E402
import strips as G  # noqa: E402
from regrid import regrid  # noqa: E402

DRAFT = os.path.join(ROOT, "assets", "source", "kaisa", "codex_model_v2", "kaisa_design_A.png")
OUT = os.path.join(ROOT, "assets", "source", "kaisa", "design_v2", "kaisa_design_v2.png")
ROWS = 42
MAXC = 28
EYES = [(16, 17), (17, 17), (16, 18), (17, 18), (16, 22), (17, 22)]   # on the 52 x 30 read-back: the near eye's white
                                                                         # and iris, the far eye's iris, their lashes


def read_back():
    """Step 1-2: the draft on its own grid without its green ground, MAXC colours, the eye squares as drawn."""
    src = np.asarray(Image.open(D.lp(DRAFT)).convert("RGBA")).copy()
    r, g, b = (src[..., i].astype(int) for i in range(3))
    src[((g > 180) & (r < 90) & (b < 90)) | ((g > r + 40) & (g > b + 40)), 3] = 0
    a, _, _ = regrid(src)
    a = a.copy()
    on = a[..., 3] >= 128
    a[~on] = 0
    a[on, 3] = 255
    cols, inv, counts = np.unique(a[on][:, :3], axis=0, return_inverse=True, return_counts=True)
    label, rep = D.merge_palette(cols, counts, MAXC)
    out = a.copy()
    out[on, :3] = np.array([rep[label[i]] for i in inv.ravel()])
    for y, x in EYES:
        out[y, x] = a[y, x]
    return out


HAIR = {"a": (0x14, 0x01, 0x1B), "g": (0x34, 0x2C, 0x62), "k": (0x27, 0x1A, 0x43), "j": (0x4B, 0x36, 0x75)}   # outline, hair, its shade
EYE_FAR = {(3, -19): "FDFCFC", (4, -19): "440F52", (3, -18): "FDFCFD", (4, -18): "7B0D9F"}
# the far eye as big as the near one: its white beside the iris, its lash over it (「眼睛也是一大一小」)
FACE_FILL = {(-3, -18): "FCDDCD", (-3, -17): "FCDDCD", (3, -15): "FCDDCD"}
# the face's holes (「卡莎的脸部丢失了一块模型」, 2026-10-04): the near cheek's two skin squares stood apart, a column of
# hair between them and the eye's dark corner - that column is skin (the user's pick A: the corner stays dark); and
# under the mouth the skin stopped a square short of the row over it (「还有嘴的右下方也少」)
PODS_OUT = (-2, 2)          # the far pod two squares further left, the near one two further right (the user: 「你把护翼
                            # 往两侧扩出去一点不就能改了吗」); x from the pivot, the far pod the one left of column -4
CROWN = {-28: (-5, "aaaaa"), -27: (-6, "akjjjka"), -26: (-7, "akjjgggka"), -25: (-7, "kjggkggka."),
         -24: (-7, "kgggkggggaa"), -23: (-8, "kkg         a"), -22: (-7, "kg"), -21: (-8, "kggg"), -20: (-9, "kkj"),
         -19: (-9, "k"), -18: (-11, "a")}
# {row: (first column, squares)} from the pivot (64, 88), " " as it is, "." cleared: the crown between the pods drawn
# round by hand where they stood (the fills of the cut's notch stood up as a comb, a bump: 「卡莎公鸡头？」「头顶凸出来的
# 那一块 不难看吗」), the hair's edge closed under the far pod, the seam by the near pod outlined (「用右图 这里再修一修」)
POD_COLOURS = {(0xF7, 0xCA, 0x4E), (0xFB, 0x2C, 0xFB), (0x8F, 0x10, 0x89), (0xB5, 0x0E, 0xB1), (0x65, 0x1A, 0x68),
               (0x56, 0x1F, 0x67), (0x9D, 0x34, 0x6A)}   # gold rim, magenta panels and their plum shades
DARK = {(0x14, 0x01, 0x1B), (0x17, 0x01, 0x1E), (0x0F, 0x07, 0x15)}


def pods_out(canvas):
    """Step 5: the pods (over row -17, joined to a gold rim from row -22 up) and their outline moved PODS_OUT apart;
    outline squares that outlined only a pod go with it; then the crown."""
    d = {(int(x) - 64, int(y) - 88): canvas[y, x].copy() for y, x in zip(*np.nonzero(canvas[..., 3]))}
    rgb = lambda c: tuple(int(v) for v in c[:3])   # noqa: E731
    cand = {p for p, c in d.items() if p[1] <= -17 and rgb(c) in POD_COLOURS}
    pods = {p for p in cand if rgb(d[p]) == (0xF7, 0xCA, 0x4E) and p[1] <= -22}
    q = list(pods)
    while q:
        x, y = q.pop()
        for n in ((x + ox, y + oy) for ox in (-1, 0, 1) for oy in (-1, 0, 1)):
            if n in cand and n not in pods:
                pods.add(n)
                q.append(n)
    around = lambda x, y: [(x + ox, y + oy) for ox in (-1, 0, 1) for oy in (-1, 0, 1) if ox or oy]   # noqa: E731
    ring = {(x, y) for (x, y), c in d.items() if y <= -17 and rgb(c) in DARK and any(n in pods for n in around(x, y))}
    body = {p: c for p, c in d.items() if p not in pods}
    for p in [p for p in body if p in ring]:
        if not any(n in body and rgb(body[n]) not in DARK for n in around(*p)):
            del body[p]
    out = np.zeros_like(canvas)
    for (x, y) in pods | ring:
        out[88 + y, 64 + x + PODS_OUT[x > -4]] = d[(x, y)]
    for (x, y), c in body.items():
        out[88 + y, 64 + x] = c
    for y, (x0, s) in CROWN.items():
        for j, ch in enumerate(s):
            if ch == ".":
                out[88 + y, 64 + x0 + j] = 0
            elif ch != " ":
                out[88 + y, 64 + x0 + j] = HAIR[ch] + (255,)
    return out


def build():
    D.EYES, D.ROWS, D.KEEP_ROWS = EYES, ROWS, set()
    fig = D.cut(read_back())
    feet = np.nonzero(fig[-1, :, 3] > 0)[0]
    x0 = int(round(64 - (feet.min() + feet.max() + 1) / 2))
    canvas = np.zeros((128, 128, 4), np.uint8)
    canvas[100 - fig.shape[0]:100, x0:x0 + fig.shape[1]] = fig
    for (x, y), h in {**EYE_FAR, **FACE_FILL}.items():
        canvas[88 + y, 64 + x] = [int(h[i:i + 2], 16) for i in (0, 2, 4)] + [255]
    canvas = G.complete_outline(pods_out(canvas), color=HAIR["a"], feet=99)[0]
    return canvas, fig


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    canvas, fig = build()
    big = np.repeat(np.repeat(canvas, 8, 0), 8, 1)
    one = OUT.replace(".png", "_1x.png")
    op = fig[..., 3] > 0
    print(f"design v2: {fig.shape[1]} x {fig.shape[0]}, {len(np.unique(fig[op][:, :3], axis=0))} colours, "
          f"{int(op.sum())} squares")
    if a.check:
        same = all(os.path.exists(D.lp(p)) and np.array_equal(np.asarray(Image.open(D.lp(p)).convert("RGBA")), arr)
                   for p, arr in ((OUT, big), (one, canvas)))
        print("the files are what a run writes" if same else "DIFFERENT")
        sys.exit(0 if same else 1)
    os.makedirs(D.lp(os.path.dirname(OUT)), exist_ok=True)
    Image.fromarray(big).save(D.lp(OUT))
    Image.fromarray(canvas).save(D.lp(one))
    print("wrote", os.path.relpath(OUT, ROOT), "and", os.path.relpath(one, ROOT))


if __name__ == "__main__":
    main()
