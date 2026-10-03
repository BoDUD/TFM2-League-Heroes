#!/usr/bin/env python3
"""Jhin's action strips: Codex's step-2 strips (codex_strips/), with the frames that came out wrong rebuilt here from the
approved design's own pixels (the user, 2026-10-03: 「奇怪的地方你帮我修复 比如走路的步伐我看到已经有点奇怪了」).

    python tools/art/rig_jhin.py [--review DIR]

  run     Codex's walk swapped the legs by mirroring the lower body of frames 5-8 (its HANDOFF says so) and redrew the
          body in every frame. Rebuilt from the design (assets/source/native/jhin_native.png): the upper body - head,
          cape, both arms, the cane and Whisper - is the design, a row up in the frames between the steps; the two legs
          are the design's own leg pixels (the trousers, the gold braces, the feet), each turned about its hip by a
          shear that moves its foot `dx` columns, the swinging foot lifted. League's walk (Jhin_WalkRun, 8 x 100 ms):
          frames 1-4 the near leg carries him, sliding back, while the far leg swings through; frames 5-8 the other
          way; the legs a little closer than in the stance so the near foot passes behind the far one (the feet cross:
          near minus far changes sign twice a cycle) and the feet stay at most 12 columns apart. Layers, back to front:
          the cane, the far leg, the body (the cape and its crimson lining), the near leg, Whisper.
Writes assets/source/native/jhin_<tag>.png (8x) and jhin_cells.json; then tools/art/import_native.py --hero jhin.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402
SRC = os.path.join(ROOT, "assets", "source", "jhin")
CODEX = os.path.join(SRC, "codex_strips")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "jhin_native.png")
Z = 8
PIVOT = (64, 88)                # the design's standing point on its 128x128 canvas (the soles on row 99)
TAGS = ["idle", "run", "attack", "attack4", "skill", "skill2", "ult", "ult_aim", "ult_shot", "hit", "dead"]

# the legs on the design's canvas, row -> (first column, last column), outline included
FAR_LEG = {84: (55, 58), 85: (55, 58), 86: (56, 58), 87: (56, 58), 88: (55, 58), 89: (55, 58), 90: (55, 57),
           91: (54, 58), 92: (54, 58), 93: (55, 57), 94: (55, 57), 95: (56, 56), 96: (55, 57), 97: (55, 57),
           98: (55, 57), 99: (55, 58)}
NEAR_LEG = {84: (62, 65), 85: (61, 66), 86: (61, 67), 87: (61, 67), 88: (61, 68), 89: (62, 68), 90: (62, 68),
            91: (61, 68), 92: (61, 68), 93: (62, 68), 94: (62, 67), 95: (63, 67), 96: (63, 67), 97: (64, 68),
            98: (63, 68), 99: (63, 69)}
HIP, KNEE, SOLE = 84, 91, 99
CANE_COLS = (49, 54)            # the cane under the gold fist (rows 83-99)
CANE_ROWS = (83, 99)
# Whisper: everything right of column 68 in rows 82-99, and column 68 where the near leg does not reach
WHISPER = (82, 99, 68)
NARROW = (2, -3)                # the legs closer than in the stance: far hip +2, near hip -3 columns (4.5 apart)
# per frame: (near foot dx, far foot dx, near lift, far lift, body dy)
# the supporting foot slides back 3 / 2 / 2 / 1 columns a frame while the other swings through lifted 1 / 2 / 1 rows;
# the feet's middles (near minus far): 11.5, 7.5, 3.5, -0.5, -2.5, 1.5, 5.5, 9.5 - two crossings a cycle, at most 12
RUN = [(3, -4, 0, 0, 0), (1, -2, 0, 1, 0), (-1, 0, 0, 2, -1), (-3, 2, 0, 1, -1),
       (-4, 3, 0, 0, 0), (-2, 1, 1, 0, 0), (0, -1, 2, 0, -1), (2, -3, 1, 0, -1)]

# Codex's frames that are the design itself (the idle, the actions' first and last frames: checked pixel for pixel
# against the design at their pivots), drawn again from the design so its later touches reach them (the right hand,
# design_jhin.py HAND)
DESIGN_FRAMES = {"idle": [1, 2, 3, 4, 5, 6], "attack": [1, 6], "attack4": [6], "skill": [6], "skill2": [8], "hit": [2]}
# frame times (ms) that keep a muzzle flash on a level gun (the user, 2026-10-03: 「攻击特效不太对」 - the flash outlived the
# shot frame and hung where the muzzle had been while the gun kicked up): the shot frames longer, the totals as before
# (attack 400 ms: the shot on tick 9 in frame 3, now 110-220 ms; W 800 ms: the shot on tick 43 in frame 7, now 620-770;
# the R shot 250 ms: frame 1, the shot, 90 ms before the recoil)
RETIME = {"attack": [50, 60, 110, 60, 60, 60], "skill2": [100, 100, 100, 100, 130, 90, 150, 30], "ult_shot": [90, 60, 60, 40]}
# Codex's palette (codex_model/jhin_palette.hex) by character: 0 the outline, 4/5 the dark purples, 7-9 the crimsons,
# a-c the cape's creams and tan, d-g the golds, h/i the skin, j/k the gunmetal, n the eyes
CH = "0123456789abcdefghijklmn"
# The frames Codex got wrong, mended on its 1x cells (cell coordinates), in order:
#   ("draw", x, y, rows)          from (x, y): a palette character, "." cleared, " " left as it is
#   ("clear", x0, y0, x1, y1)     the rectangle cleared (inclusive)
#   ("piece", tag, k, (x, y), dx, dy)   the 8-connected piece through (x, y) of Codex's frame k of tag, moved by (dx, dy)
#   ("move", [(x0, y0, x1, y1), ...], dx, dy)   what Codex drew in the rectangles, lifted out and put down moved
#   ("tie",)                      every loose piece under 20 squares hung back on: outline squares up to the body
#   ("plug", x0, y0, x1, y1, c)   the clear squares in the rectangle that the figure shuts in, painted c
#   ("gap", x0, y0, x1, y1, c)    the same once the import's outline is closed (an opening a square wide is shut by it)
FIX = {
    # the shot: Codex lifted the near forearm level with the gun but left the idle's arm hanging two columns off the
    # body (rows 48-57, no outline); hung from the shoulder it made an L, a right angle at the hip (the user,
    # 2026-10-03: 「手臂怎么90度角？看着一股怪味」). Traced from League's shot at game size: the upper arm slants down and
    # forward from the shoulder, the elbow a little bent (the user's pick B over a straight arm), the forearm nearly
    # level to the grip, the purple cuff before the hand; Whisper stays (the muzzle 7.5 rows over the pivot)
    ("attack", 3): [("clear", 48, 45, 58, 56),
                    ("draw", 47, 42, ["   0",
                                      "   0"]),
                    ("draw", 49, 43, ["ii0",
                                      "hii0",
                                      "0ii0",
                                      "0hii0",
                                      " 0ii00",
                                      " 0hiii000",
                                      "  0hiiiii0",
                                      "   00hi6ii",
                                      "     000hi",
                                      "        00"]),
                    ("draw", 49, 57, ["0."])],
    # the fourth shot's flourish: Whisper held up on an arm 16 rows long (the design's is 6) - the gun, the hand and
    # the tassel come down 7 rows, the arm under the hand 9 rows
    ("attack4", 2): [("clear", 33, 27, 37, 32),
                     ("move", [(29, 5, 43, 26), (29, 27, 32, 32)], 0, 7)],
    # the fourth shot: the same hanging arm, its forearm a gold-and-skin line with nothing over it (a thin bright
    # stick): bare skin like the design's arm, outlined, one straight line from the shoulder down to the grip (the
    # hanging arm's top had stood 2 rows over the forearm at the shoulder - the same L); the black cord hanging under
    # the barrel out
    ("attack4", 4): [("clear", 47, 48, 57, 53),
                     ("draw", 47, 46, ["  0",
                                       " ii000",
                                       "hiiiii0000",
                                       "0hiiiiiii60",
                                       " 0000hiiiii",
                                       "     0000hi",
                                       "         00"]),
                     ("clear", 77, 51, 77, 54)],
    ("attack4", 5): [("draw", 51, 44, [" 0000000",
                                       " iiiii",
                                       "  iii",
                                       " 0 00000"])],
    # the grenade's throw: Codex's gold arm ran 23 columns across, past his near shoulder to a speckled blob at
    # column 64; now the gold forearm (2 rows, the purple cuff of the design's bracer) ends in a 4-row gold fist a
    # hand past the body, the follow-through (frame 4) a column further
    ("skill", 3): [("clear", 58, 43, 66, 50),
                   ("draw", 47, 44, ["       000",
                                     "       fgf0",
                                     "  ff5ffgff0",
                                     "  ee5efffe0",
                                     "0000000eed0",
                                     " ......000"])],
    ("skill", 4): [("clear", 61, 43, 69, 49),
                   ("draw", 51, 44, ["      000",
                                     "      fgf0",
                                     "ff5fffgff0",
                                     "ee5effffe0",
                                     "000000eed0",
                                     "......000."])],
    # the fall: Whisper flew out to 19-43 columns past the pivot and then lay at 5-25 - it flies 5 columns nearer
    # (its tassel clear of his knee); a crumb of the hood floating over his head out; Whisper, squashed to two rows on
    # the ground in frames 3-4, lies where it lies from frame 5 on (the same place by the pivot)
    ("dead", 2): [("clear", 61, 53, 85, 62),
                  ("piece", "dead", 2, (75, 58), -5, 0)],
    ("dead", 3): [("clear", 35, 35, 42, 36),
                  ("clear", 50, 66, 70, 67),
                  ("piece", "dead", 5, (60, 63), -4, 0)],
    ("dead", 4): [("clear", 55, 66, 75, 67),
                  ("piece", "dead", 5, (60, 63), 1, 0)],
    # the bow (the user, 2026-10-03: 「死亡时候还有模型缺失」): the cape curls round an empty middle - the ground showed
    # between the cape and the bowed head (frames 6-8 the same drawing 3 and 7 columns further left, 42 squares shut
    # in; frame 5 open under the chin); his dark clothes there, an outline square along the cape's inner edge
    ("dead", 5): [("draw", 39, 46, ["4444",
                                    "4444",
                                    "04444",
                                    "044",
                                    "0444",
                                    "0444",
                                    "04",
                                    "0444",
                                    "044444",
                                    "044444444",
                                    "0444444440"])],
    **{("dead", k): [("draw", x, 48, ["04444",
                                      "0444",
                                      "04444",
                                      "0444",
                                      "04444",
                                      "044",
                                      "044",
                                      "0444",
                                      "04",
                                      "044",
                                      "04444"])] for k, x in ((6, 39), (7, 36), (8, 32))},
    # the big cannon's tassel hangs a square under the barrel in five frames: tied on
    ("ult", 4): [("tie",)],
    ("ult_aim", 1): [("tie",)],
    ("ult_aim", 3): [("tie",)],
    ("ult_shot", 1): [("tie",)],
    ("ult_shot", 4): [("tie",)],
    # the deploy: a loose sliver standing over the near hand out
    ("ult", 1): [("clear", 56, 42, 57, 46)],
}
# the ground showing through: one-square slits between the hood's hair and the mask, and gaps Codex left in the body
# (between the gold arm and the cape, in the dark middle) - painted the hood's or the clothes' dark purple (4), or
# outline (0) where the cape's cream meets the clothes. Gaps that belong to the drawing stay open: Whisper's grip loop
# (the design's own), the cane against the leg, the arms against the body, the rifle over the forearm, the raised arms
# round the cannon in the deploy
PLUG = {("dead", 1): [(30, 40, 50, 54, "4")], ("hit", 1): [(30, 30, 40, 48, "4")], ("skill", 4): [(40, 38, 44, 46, "4")],
        ("skill", 5): [(40, 38, 44, 46, "4"), (32, 43, 36, 47, "4")], ("ult", 1): [(30, 54, 35, 62, "4")],
        ("ult", 3): [(36, 42, 40, 50, "4")], ("attack4", 1): [(42, 47, 48, 55, "4")],
        ("skill2", 3): [(44, 26, 48, 34, "4")], ("attack", 2): [(36, 32, 42, 41, "4")],
        ("attack", 3): [(36, 32, 42, 41, "4")], ("attack", 4): [(55, 54, 57, 56, "0")], ("dead", 3): [(38, 55, 41, 64, "0")]}
for _key, _boxes in PLUG.items():
    FIX.setdefault(_key, []).extend(("plug", *b) for b in _boxes)
# slits the import's outline shuts (seen on the game frames, 2026-10-03): the near arm against his side in Q (as the
# idle's, design_jhin.py HAND), the slit under the cannon's arm in the kneeling aim (the aim loop's frame 3, open there,
# filled the same rows so it does not blink), the cape against the leg in the deploy, beside the head and the knee in
# the fall - his dark side. Gaps between the legs (the fourth shot's jump), the rifle and the body (W), the cane and
# the leg (the walk) and the arms round the raised cannon stay
GAP = {("skill", 1): [(46, 49, 51, 56)], ("skill", 2): [(48, 51, 56, 59)], ("skill", 3): [(46, 53, 50, 56)],
       ("skill", 5): [(48, 50, 55, 58)], ("ult", 3): [(30, 58, 34, 63)], ("dead", 4): [(40, 45, 44, 49), (45, 60, 47, 66)],
       **{key: [(46, 54, 54, 58)] for key in (("ult", 4), ("ult_aim", 1), ("ult_aim", 2), ("ult_aim", 4),
                                               ("ult_shot", 1), ("ult_shot", 4))}}
for _key, _boxes in GAP.items():
    FIX.setdefault(_key, []).extend(("gap", *b, "4") for b in _boxes)
FIX.setdefault(("ult_aim", 3), []).append(("draw", 47, 55, ["44444", "4444"]))
# Codex's head in every action but the idle leaves specks of ground (3 + 1 squares) between the hood's back, the jaw
# and the cape's collar, where the design has outline: shut-in specks of at most HEAD_SPECK squares within HEAD_BOX
# (rows, columns from the far eye) are painted outline
HEAD_SPECK = 4
HEAD_BOX = (-8, 8, -12, 2)
EYE = (0xFF, 0x6E, 0xB4)


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + p if os.name == "nt" and not p.startswith(pre) else p


def read1x(path):
    a = np.asarray(Image.open(lp(path)).convert("RGBA"))
    if a.shape[0] % 128 == 0 and a.shape[0] != 128 and a.shape[0] == a.shape[1]:
        a = a[Z // 2::Z, Z // 2::Z]
    a = a.copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    return a


def strip1x(path):
    """A strip at 1x (codex_strips/ keeps Codex's 1x copies)."""
    a = np.asarray(Image.open(lp(path)).convert("RGBA")).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    return a


def layout(n):
    cols = {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)
    return cols, -(-n // cols)


def split(strip, cell, n):
    cw, ch = cell
    cols, _ = layout(n)
    return [strip[(i // cols) * ch:(i // cols) * ch + ch, (i % cols) * cw:(i % cols) * cw + cw].copy() for i in range(n)]


def join(frames, cell):
    cw, ch = cell
    cols, rows = layout(len(frames))
    out = np.zeros((rows * ch, cols * cw, 4), np.uint8)
    for i, f in enumerate(frames):
        out[(i // cols) * ch:(i // cols) * ch + ch, (i % cols) * cw:(i % cols) * cw + cw] = f
    return out


def mask_of(shape, rows):
    m = np.zeros(shape[:2], bool)
    for r, (c0, c1) in rows.items():
        m[r, c0:c1 + 1] = True
    return m


def parts(des):
    """The design split into layers: cane, far leg, body, near leg, Whisper (each a 128x128 canvas)."""
    op = des[..., 3] > 0
    far = mask_of(des.shape, FAR_LEG) & op
    near = mask_of(des.shape, NEAR_LEG) & op
    cane = np.zeros_like(op)
    cane[CANE_ROWS[0]:CANE_ROWS[1] + 1, CANE_COLS[0]:CANE_COLS[1] + 1] = True
    cane &= op & ~far
    r0, r1, c = WHISPER
    whisper = np.zeros_like(op)
    whisper[r0:r1 + 1, c:] = True
    whisper &= op & ~near
    body = op & ~far & ~near & ~cane & ~whisper
    layer = lambda m: np.where(m[..., None], des, 0).astype(np.uint8)
    return {"cane": layer(cane), "far": layer(far), "body": layer(body), "near": layer(near), "whisper": layer(whisper)}


def paste(dst, src, dx, dy):
    ys, xs = np.nonzero(src[..., 3])
    ty, tx = ys + dy, xs + dx
    ok = (ty >= 0) & (ty < dst.shape[0]) & (tx >= 0) & (tx < dst.shape[1])
    dst[ty[ok], tx[ok]] = src[ys[ok], xs[ok]]


def leg_pose(leg, dx, lift, body_dy, base):
    """One leg turned about its hip: row y moves dx * (y - HIP) / (SOLE - HIP) columns (rounded), the shin and foot
    (rows from KNEE) `lift` rows up, the thigh's top following the body; gaps closed by repeating the row above."""
    out = np.zeros_like(leg)
    rows = sorted({int(y) for y in np.nonzero(leg[..., 3])[0]})
    placed = {}
    for y in rows:
        t = (y - HIP) / (SOLE - HIP)
        sx = int(round(dx * t)) + base
        if y < KNEE:
            ty = y + int(round(body_dy * (1 - (y - HIP) / (KNEE - HIP))))
        else:
            ty = y - lift
        row = leg[y]
        xs = np.nonzero(row[..., 3])[0]
        for x in xs:
            if 0 <= x + sx < out.shape[1]:
                out[ty, x + sx] = row[x]
        placed[y] = ty
    # rows the moves left empty between two placed rows: repeat the row above, shifted like it
    filled = {placed[y] for y in rows}
    lo, hi = min(filled), max(filled)
    for ty in range(lo, hi + 1):
        if ty not in filled and out[ty - 1, :, 3].any():
            out[ty] = out[ty - 1]
    return out


def run_frame(p, spec):
    near_dx, far_dx, near_lift, far_lift, dy = spec
    f = np.zeros_like(p["body"])
    paste(f, p["cane"], 0, dy)
    paste(f, leg_pose(p["far"], far_dx, far_lift, dy, NARROW[0]), 0, 0)
    paste(f, p["body"], 0, dy)
    paste(f, leg_pose(p["near"], near_dx, near_lift, dy, NARROW[1]), 0, 0)
    paste(f, p["whisper"], 0, dy)
    return f


def to_cell(canvas, cell, pivot):
    """A 128-canvas figure into a cell, the design's pivot on the cell's."""
    cw, ch = cell
    out = np.zeros((ch, cw, 4), np.uint8)
    paste(out, canvas, pivot[0] - PIVOT[0], pivot[1] - PIVOT[1])
    return out


def palette():
    with open(lp(os.path.join(SRC, "codex_model", "jhin_palette.hex"))) as f:
        return [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in f.read().split()]


def label(op):
    """8-connected pieces of a mask: (labels, -1 where clear; sizes)."""
    H, W = op.shape
    lab = -np.ones((H, W), int)
    sizes = []
    for y, x in zip(*np.nonzero(op)):
        if lab[y, x] >= 0:
            continue
        n = len(sizes)
        lab[y, x] = n
        todo, size = [(y, x)], 0
        while todo:
            cy, cx = todo.pop()
            size += 1
            for ny in (cy - 1, cy, cy + 1):
                for nx in (cx - 1, cx, cx + 1):
                    if 0 <= ny < H and 0 <= nx < W and op[ny, nx] and lab[ny, nx] < 0:
                        lab[ny, nx] = n
                        todo.append((ny, nx))
        sizes.append(size)
    return lab, sizes


def shut_in(op):
    """Clear squares the figure closes in (not 4-connected to the cell's border)."""
    H, W = op.shape
    out = np.zeros_like(op)
    todo = [(y, x) for y in range(H) for x in (0, W - 1)] + [(y, x) for x in range(W) for y in (0, H - 1)]
    todo = [(y, x) for y, x in todo if not op[y, x]]
    for y, x in todo:
        out[y, x] = True
    while todo:
        cy, cx = todo.pop()
        for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
            if 0 <= ny < H and 0 <= nx < W and not op[ny, nx] and not out[ny, nx]:
                out[ny, nx] = True
                todo.append((ny, nx))
    return ~op & ~out


def mend(frames, codex):
    """FIX on the 1x cells in place (codex: Codex's untouched cells, the source of "piece"); the squares changed."""
    pal = palette()
    changed = 0
    for (tag, k), ops in FIX.items():
        f = frames[tag][k - 1]
        before = f.copy()
        for op in ops:
            if op[0] == "draw":
                _, x, y, rows = op
                for dy, row in enumerate(rows):
                    for dx, c in enumerate(row):
                        if c != " ":
                            f[y + dy, x + dx] = (0, 0, 0, 0) if c == "." else pal[CH.index(c)] + (255,)
            elif op[0] == "clear":
                _, x0, y0, x1, y1 = op
                f[y0:y1 + 1, x0:x1 + 1] = 0
            elif op[0] == "piece":
                _, st, sk, (x, y), dx, dy = op
                src = codex[st][sk - 1]
                lab, _ = label(src[..., 3] > 0)
                ys, xs = np.nonzero(lab == lab[y, x])
                f[ys + dy, xs + dx] = src[ys, xs]
            elif op[0] == "move":
                _, rects, dx, dy = op
                src = codex[tag][k - 1]
                m = np.zeros(f.shape[:2], bool)
                for x0, y0, x1, y1 in rects:
                    m[y0:y1 + 1, x0:x1 + 1] = True
                m &= src[..., 3] > 0
                f[m] = 0
                ys, xs = np.nonzero(m)
                f[ys + dy, xs + dx] = src[ys, xs]
            elif op[0] in ("plug", "gap"):
                _, x0, y0, x1, y1, c = op
                g = f
                if op[0] == "gap":                  # the import's outline pass (import_native COMPLETE), feet line 67
                    g, _, _ = G.complete_outline(np.pad(f, ((1, 1), (1, 1), (0, 0))), color=pal[0], feet=68)
                    g = g[1:-1, 1:-1]
                hole = shut_in(g[..., 3] > 0)
                box = np.zeros_like(hole)
                box[y0:y1 + 1, x0:x1 + 1] = True
                f[hole & box] = pal[CH.index(c)] + (255,)
            elif op[0] == "tie":
                lab, sizes = label(f[..., 3] > 0)
                body = int(np.argmax(sizes))
                for p, size in enumerate(sizes):
                    if p == body or size >= 20:
                        continue
                    ys, xs = np.nonzero(lab == p)
                    for x in xs[ys == ys.min()]:
                        path = [y for y in range(ys.min() - 1, ys.min() - 4, -1)]
                        hit = next((i for i, y in enumerate(path) if lab[y, x] == body), None)
                        if hit is not None:
                            for y in path[:hit]:
                                f[y, x] = pal[0] + (255,)
                            break
        changed += int((f != before).any(-1).sum())
    for tag, frs in frames.items():
        if tag in ("idle", "run"):
            continue
        for f in frs:
            ys, xs = np.nonzero((f[..., :3] == EYE).all(-1) & (f[..., 3] > 0))
            if not len(ys):
                continue
            ey, ex = int(ys[xs == xs.min()].min()), int(xs.min())
            lab, sizes = label(shut_in(f[..., 3] > 0))
            for p, size in enumerate(sizes):
                hy, hx = np.nonzero(lab == p)
                if size <= HEAD_SPECK and (hy >= ey + HEAD_BOX[0]).all() and (hy <= ey + HEAD_BOX[1]).all() \
                        and (hx >= ex + HEAD_BOX[2]).all() and (hx <= ex + HEAD_BOX[3]).all():
                    f[hy, hx] = pal[0] + (255,)
                    changed += size
    return changed


def build():
    cells = json.load(open(lp(os.path.join(CODEX, "jhin_cells.json")), encoding="utf-8"))
    cell = tuple(cells["cell"])
    des = read1x(DESIGN)
    p = parts(des)
    out = {}
    for tag in TAGS:
        n = len(cells["tags"][tag])
        out[tag] = split(strip1x(os.path.join(CODEX, f"jhin_{tag}.png")), cell, n)
    codex = {t: [f.copy() for f in v] for t, v in out.items()}
    for tag, ks in DESIGN_FRAMES.items():
        for k in ks:
            out[tag][k - 1] = to_cell(des, cell, cells["tags"][tag][k - 1]["pivot"])
    mend(out, codex)
    out["run"] = [to_cell(run_frame(p, s), cell, fr["pivot"]) for s, fr in zip(RUN, cells["tags"]["run"])]
    return out, cells, cell, codex


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write a 4x review sheet of every strip into this folder")
    a = ap.parse_args()
    out, cells, cell, _ = build()
    for tag, frs in out.items():
        strip = join(frs, cell)
        Image.fromarray(np.repeat(np.repeat(strip, Z, 0), Z, 1)).save(lp(os.path.join(NATIVE, f"jhin_{tag}.png")))
    for tag, ms in RETIME.items():
        assert sum(ms) == sum(f["ms"] for f in cells["tags"][tag]) and len(ms) == len(cells["tags"][tag]), tag
        for f, m in zip(cells["tags"][tag], ms):
            f["ms"] = m
    with open(lp(os.path.join(NATIVE, "jhin_cells.json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump(cells, f, indent=1)
    print("written", ", ".join(f"{t} {len(v)}" for t, v in out.items()))
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        cw, ch = cell
        rows = []
        for tag, frs in out.items():
            piv = [f["pivot"] for f in cells["tags"][tag]]
            rows.append(np.concatenate([f[:, max(0, pv[0] - 40):pv[0] + 40] if f.shape[1] >= 80 else f
                                        for f, pv in zip(frs, piv)], axis=1))
        W = max(r.shape[1] for r in rows)
        sheet = np.zeros((sum(r.shape[0] for r in rows), W, 4), np.uint8)
        y = 0
        for r in rows:
            sheet[y:y + r.shape[0], :r.shape[1]] = r
            y += r.shape[0]
        im = Image.fromarray(sheet).resize((W * 3, sheet.shape[0] * 3), Image.NEAREST)
        bg = Image.new("RGBA", im.size, (104, 112, 72, 255))
        bg.alpha_composite(im)
        bg.convert("RGB").save(os.path.join(a.review, "jhin_rig.png"))


if __name__ == "__main__":
    main()
