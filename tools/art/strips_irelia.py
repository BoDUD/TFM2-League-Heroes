#!/usr/bin/env python3
"""Irelia's game strips from Codex's telekinetic redraw (assets/source/irelia/codex_strips_v2).

    python tools/art/strips_irelia.py               # write assets/source/native/irelia_<tag>.png, irelia_cells.json
                                                    # and irelia_native.png (the idle's first frame)
    python tools/art/strips_irelia.py --check       # compare with the committed files instead of writing
    python tools/art/strips_irelia.py --review DIR  # irelia_strips_review.gif and _frames.png (every frame at 4x)
    python tools/art/strips_irelia.py --base DIR    # the action frames as the automatic steps make them, <tag>.txt
                                                    # (what the hand finish in design_v2/frames started from)

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
    shape); the head bigger (2:1 leaves the face as specks);
  * the head: one head in every frame, the idle's (the user: 「在正脸的基础上 做后续的run动作不就行了吗」「剑姬卡密尔都没
    单独做侧面啊」) - design_v2/head_front.txt; head_idle.txt is the same head with what lies beside it in the idle (the
    upper-left blade's tip, the shoulder hook, the hand at her cheek). It is the idle read-back's head (head_mask) with
    the face kept square for square, from the tiara's gem to the neck - shrunk to 3/4 with the rest, the face had lost
    a forehead row and a cheek row and stood wide (「这两边凸出来真的好怪」; the user, showing the read-back's face:
    「这样子的脸 你手描还原不出来吗」) - and the hair over it brought to 5 rows, the columns beside it dropped (whole lines,
    the least loss: design_riven.pick), the crest's tip and the dome's top outline drawn back where the drops took
    them; the eyes' dark cyan as t (the importer steadies the run on it), the neck the draft's shadow row under the
    chin as skin in shade (「脖子画一个啊」, then 「参考之前codex的图做吧」). Each action frame's own head is found
    (find_head: the face, the hair touching it within 19 rows over the chin, 10 columns left and 5 right of the face -
    the flowing hair behind a running Irelia is one piece with her crown -, small ornaments touching them) and taken
    away, and the head set with its neck on the draft's chin row and its face's middle on the draft's; the death's
    lying frames are read standing (the draft turned a quarter) and turned back. Before it: each draft's own head (the
    face differing frame to frame, 「跑动时嘴巴脸型一样啊」), then a side head made from run 7 (「侧脸非常的怪」「这是骷髅
    脸了吧」「而且侧面头和身体都不协调」), and first a big front head at twice the body's scale (「模型感觉还有点变形吧看起来
    好奇怪」「眼睛画风好奇怪」);
  * the idle is drawn by hand (the user: 「都给我精修好了 每个部位」): design_v2/body_idle.txt, every 2:1 square decided
    from its block of design_v2/idle_readback.txt (the read-back the user liked) and the part it belongs to (collar and
    gem, breastplates, tabard with white edges and its tip, the shoulder hook, the raised forearm to the hand at her
    cheek, the arm hanging to the open hand, the long hair, the hip flaps, knee stars, boots with white ankle bands and
    toe caps), head_idle.txt, and the four blades redrawn clean (BLADES), the top and upper-left ones moved out from
    behind the head; the eight idle frames are that one still figure with each blade bobbing a row, out of step
    (BOB);
  * the actions: the draft split into its body and the floating blades (the pieces apart from the body), each reduced,
    a blade the head would cover moved away from it; the outline stays where the drafts draw it (a block on the
    silhouette holding outline is outline) and is closed where the vote dropped it (close_open: the edge square itself
    turns outline where the part is thick, the square outside where it is thin - an ink ring added all round made
    every limb a square thicker each side, 「身体感觉也变形？」); the hair's strand tips, sticks at 2:1, trimmed
    (trim_spurs);
  * then finished by hand, frame by frame (design_v2/frames/<tag>.txt, the user: 「你给我一帧一帧改到完美」「不要有变形
    奇怪的地方全部手描 补」), each looked at against its draft square for square (the 2x2 draft squares under every
    square): the one-square holes walled by outline filled (the head is bigger than the draft's, so the gap to a
    blade behind it closed to a square or two), the hair behind a running Irelia given back the strand tips the vote
    cut (run 5 and 7 were flat blocks), a blade tip the draft's crop cut off taken away (skill 1). --base writes the
    automatic frames.
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
OFFSET = {"top": (-2, -3), "upper_left": (0, -2), "lower_left": (0, 0), "lower_right": (0, 0)}
BOB = {"upper_left": [0, 0, -1, -1, -1, -1, 0, 0], "top": [0, -1, -1, -1, 0, 0, 0, 0],
       "lower_left": [0, 0, 0, -1, -1, -1, -1, 0], "lower_right": [-1, -1, 0, 0, 0, 0, -1, -1]}
BODY_AT = (9, 10)                # the idle's 2:1 body square (r, c) -> work square (r + 9, c + 10)
FRAMES = os.path.join(DESIGN, "frames")     # the action frames finished by hand, <tag>.txt


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
    for r in range(R):                  # a block on the silhouette (1-2 clear squares) holding outline stays outline
        for c in range(C):
            blk = [P[2 * r + i, 2 * c + j] for i in range(2) for j in range(2)]
            if 1 <= blk.count(".") <= 2 and "0" in blk:
                out[r, c] = "0"
    return out


def trim_spurs(L, steps=3):
    """Hair tips: a navy or outline square with one neighbour (4-way) at the end of a one-square-wide run is cut, up
    to `steps` squares - the 2:1 vote draws the drafts' fine strand tips as straight sticks."""
    L = L.copy()
    for _ in range(steps):
        op = L != "."
        n4 = np.zeros(L.shape, int)
        n4[1:] += op[:-1]
        n4[:-1] += op[1:]
        n4[:, 1:] += op[:, :-1]
        n4[:, :-1] += op[:, 1:]
        cut = op & (n4 <= 1) & np.isin(L, list("0abcd"))
        if not cut.any():
            break
        L[cut] = "."
    return L


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


def close_open(G):
    """The outline closed where the 2:1 vote dropped it (the drafts are outlined all round; a block holding a quarter
    of outline votes clear): a coloured square 4-next to clear turns outline itself where its material goes on two
    squares behind it, else the clear square outside turns outline - an ink ring all round made every limb a square
    thicker each side (「身体感觉也变形？」)."""
    out = G.copy()
    H, W = G.shape
    for y, x in zip(*np.nonzero((G != ".") & (G != "0"))):
        m = MAT[G[y, x]]
        for dy, dx in N4:
            yy, xx = y + dy, x + dx
            if 0 <= yy < H and 0 <= xx < W and G[yy, xx] != ".":
                continue
            behind = [(y - dy, x - dx), (y - 2 * dy, x - 2 * dx)]
            if all(0 <= by < H and 0 <= bx < W and MAT[G[by, bx]] == m for by, bx in behind):
                out[y, x] = "0"
            elif 0 <= yy < H and 0 <= xx < W:
                out[yy, xx] = "0"
    return out


# ------------------------------------------------------------------------------------------------- heads
def face_box(L):
    """The draft's face: the topmost skin piece of 8+ squares with cyan beside it (eyes, tiara) in the figure's top
    45%: (top, bottom, left, right, mask) or None."""
    ys, _ = np.nonzero(L != ".")
    top, bot = ys.min(), ys.max()
    sk = np.isin(L, list("qrs"))
    near = ndimage.binary_dilation(np.isin(L, list("nop")), np.ones((3, 3)))
    lab, n = ndimage.label(sk, np.ones((3, 3)))
    best = None
    for i in range(1, n + 1):
        m = lab == i
        yy, xx = np.nonzero(m)
        if m.sum() < 8 or yy.min() > top + 0.45 * (bot - top) or not (m & near).any():
            continue
        if best is None or yy.min() < best[0]:
            best = (yy.min(), yy.max(), xx.min(), xx.max(), m)
    return best


def head_mask(L, body, face, fy0, eye_bottom):
    """The head's squares in the draft: the face (skin of the face piece down to 4 rows under the eyes: an arm held
    up can join the face's skin), the hair touching it (the navy pieces), the small red / silver / cyan / skin pieces
    touching those (crest, ornament, tiara, the hand at the cheek: at most 25 squares - a blade or the cape is bigger),
    and their outline."""
    chin = eye_bottom + 4
    f = face.copy()
    f[chin + 1:] = False
    k3 = np.ones((3, 3))
    fys, fxs = np.nonzero(f)
    near_face = np.zeros(L.shape, bool)         # the head's reach: 19 rows over the chin, 10 columns left of the face,
    near_face[max(0, chin - 19):chin + 1, max(0, fxs.min() - 10):fxs.max() + 6] = True   # 5 right (the flowing hair
    body = body & near_face                     # behind a running Irelia is one piece with her crown)
    navy = np.isin(L, list("abcd")) & body
    lab, n = ndimage.label(navy, k3)
    near = ndimage.binary_dilation(f, k3)
    m = f.copy()
    for i in range(1, n + 1):
        piece = lab == i
        if (piece & near).any():
            m |= piece
    m[chin + 1:] = False
    for mat in ("efgh", "ijklm", "nop", "qrs"):
        lab, n = ndimage.label(np.isin(L, list(mat)) & body & ~m, k3)
        touch = ndimage.binary_dilation(m, k3)
        for i in range(1, n + 1):
            piece = lab == i
            if piece.sum() <= 25 and (piece & touch).any():
                m |= piece
    m[chin + 1:] = False
    m |= ndimage.binary_dilation(m, k3) & (L == "0") & body
    m[chin + 1:] = False
    return m, chin


def find_head(L, body):
    """Where the draft's head is: (its box in L - top, chin, left, right -, the face's middle column, its squares
    (head_mask)) or None."""
    fb = face_box(L)
    if fb is None:
        return None
    fy0, fy1, fx0, fx1, face = fb
    cyan = np.isin(L, list("nop")) & ndimage.binary_dilation(face, np.ones((3, 3)))
    cyan[:fy0 + 2] = False                      # the tiara gem sits on the face's top row; the eyes lower
    if not cyan.any():                          # eyes not drawn in cyan by the face (a turned or lowered head): its
        cyan[min(fy1 - 2, fy0 + 3), (fx0 + fx1) // 2] = True       # middle stands in for them
    eye_bottom = int(np.nonzero(cyan.any(1))[0].max())
    hm, chin = head_mask(L, body, face, fy0, eye_bottom)
    ys, xs = np.nonzero(hm)
    return (ys.min(), min(chin, ys.max()), xs.min(), xs.max()), (fx0 + fx1) / 2.0, hm


def paste_head(G, found, oy, ox, at, head):
    """Set head = (table, its face's middle column) on the work table G where find_head found the draft's: its last
    row (the neck) on the 2:1 row of the chin, its face's middle on the 2:1 column of the draft's (at = the 2:1
    table's place in G). Returns the head's box in G."""
    (y0, y1, x0, x1), fcx = found[:2]
    tab, hc = head
    r0 = at[0] + (y1 + oy) // 2 - (tab.shape[0] - 1)
    c0 = at[1] + int(round((fcx + ox) / 2.0)) - hc
    m = tab != "."
    G[r0:r0 + tab.shape[0], c0:c0 + tab.shape[1]][m] = tab[m]
    return r0, c0, tab.shape[0], tab.shape[1]


def heads():
    """head_front.txt (every action frame's head) and head_idle.txt (the same head with the blade's tip, the
    shoulder hook and the hand at her cheek beside it), each with its face's middle column: the middle of the skin
    in the front head's last three rows (cheek, chin, neck)."""
    front = table(os.path.join(DESIGN, "head_front.txt"))
    fx = np.nonzero(np.isin(front[-3:], list("qrs")).any(0))[0]
    mid = int(round((fx.min() + fx.max()) / 2.0))
    return (front, mid), (table(os.path.join(DESIGN, "head_idle.txt")), mid)


# ------------------------------------------------------------------------------------------------- the idle
def idle_frame(body, head, found, k):
    G = np.full((52, 60), ".", "<U1")
    for name in ("top", "upper_left", "lower_left", "lower_right"):          # behind the body
        oy, ox = OFFSET[name]
        for r, c0, s in BLADES[name]:
            for i, ch in enumerate(s):
                G[r + BODY_AT[0] + oy + BOB[name][k], c0 + i + BODY_AT[1] + ox] = ch
    m = body != "."
    G[BODY_AT[0]:BODY_AT[0] + body.shape[0], BODY_AT[1]:BODY_AT[1] + body.shape[1]][m] = body[m]
    paste_head(G, found, 0, 0, BODY_AT, head)
    return G


def idle_place():
    """Where the idle's head goes: find_head on the idle read-back (the figure's biggest piece)."""
    rb = table(os.path.join(DESIGN, "idle_readback.txt"))
    lab, n = ndimage.label(rb != ".", np.ones((3, 3)))
    sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    return find_head(rb, lab == int(np.argmax(sizes)) + 1)


# ------------------------------------------------------------------------------------------------- the actions
def action_frame(L, head, lying=False):
    """A draft at game size: body and blades at 2:1, the head (heads()) where the draft's own head was - that one
    found by find_head and taken away; a blade the head would cover moved away from it. lying: read standing (the
    draft turned a quarter, crown up) and turned back. Returns the work table and the 2:1 table's box in it (row,
    col, rows, cols)."""
    if lying:
        G, (r0, c0, H, W) = action_frame(np.rot90(L, 1), head)
        Gt = np.rot90(G, -1)
        return Gt, (c0, G.shape[0] - r0 - H, W, H)
    pad = 24
    oy, ox = best_phase(L)
    lab, n = ndimage.label(L != ".", np.ones((3, 3)))
    sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    body_id = int(np.argmax(sizes)) + 1
    bm = lab == body_id
    body = trim_spurs(despeckle(reduce2(np.where(bm, L, "."), oy, ox)))
    H, W = body.shape
    G = np.full((H + 2 * pad, W + 2 * pad), ".", "<U1")
    found = find_head(L, bm)
    hm = np.zeros(G.shape, bool)
    if found is not None:
        hp = np.pad(found[2], ((oy, 2), (ox, 2)))
        for r in range(H):                      # its 2:1 self goes: every square whose block is half head or more
            for c in range(W):
                if hp[2 * r:2 * r + 2, 2 * c:2 * c + 2].sum() >= 2:
                    body[r, c] = "."
        probe = np.full(G.shape, ".", "<U1")
        hr0, hc0, hh, hw = paste_head(probe, found, oy, ox, (pad, pad), head)
        hm = probe != "."
        hcy, hcx = hr0 + hh / 2.0, hc0 + hw / 2.0
    for i in range(1, n + 1):
        if i == body_id or sizes[i - 1] < 6:
            continue
        piece = despeckle(reduce2(np.where(lab == i, L, "."), oy, ox))
        m = np.zeros(G.shape, bool)
        m[pad:pad + H, pad:pad + W] = piece != "."
        if not m.any():
            continue
        dy = dx = 0
        if found is not None and (m & hm).sum() > 0.15 * m.sum():
            ys, xs = np.nonzero(m)
            vy, vx = ys.mean() - hcy, xs.mean() - hcx
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
    if found is not None:
        paste_head(G, found, oy, ox, (pad, pad), head)
    return close_open(G), (pad, pad, H, W)


def place(G, px):
    """A work table onto the 128 canvas: its lowest row on SOLES, column px on PIVOT[0]."""
    ys, xs = np.nonzero(G != ".")
    out = np.full((128, 128), ".", "<U1")
    out[ys + SOLES - ys.max(), xs + PIVOT[0] - int(round(px))] = G[ys, xs]
    return out


def read_frames(path):
    """A finished tag (design_v2/frames/<tag>.txt): per frame a line '# <k> <row> <col>' (where its table's top-left
    lies on the 128 canvas) and the table's rows. Returns the canvases."""
    blocks = []
    for line in open(K.lp(path), encoding="utf-8"):
        line = line.rstrip("\r\n")
        if line.startswith("#"):
            _, r, c = (int(v) for v in line[1:].split())
            blocks.append((r, c, []))
        elif line.strip():
            blocks[-1][2].append(line)
    out = []
    for r, c, rows in blocks:
        w = max(len(x) for x in rows)
        G = np.full((128, 128), ".", "<U1")
        G[r:r + len(rows), c:c + w] = np.array([list(x.ljust(w, ".")) for x in rows])
        out.append(G)
    return out


def write_frames(path, frames):
    with open(K.lp(path), "w", encoding="utf-8", newline="\n") as f:
        for k, G in enumerate(frames):
            ys, xs = np.nonzero(G != ".")
            f.write(f"# {k} {ys.min()} {xs.min()}\n")
            for r in range(ys.min(), ys.max() + 1):
                f.write("".join(G[r, xs.min():xs.max() + 1]) + "\n")
            f.write("\n")


def auto_actions(rb, head):
    """The action frames as the automatic steps make them (the start of the hand finish)."""
    frames = {}
    for t in TAGS[1:]:
        res = []
        for k, (L, fr) in enumerate(rb[t]):
            G, (r0, c0, H, W) = action_frame(L, head, lying=(t == "dead" and k >= 4))
            x0, x1 = fr["bbox"][0], fr["bbox"][2]
            res.append(place(G, c0 + (fr["pivot"][0] - x0) / float(x1 - x0) * W))
        frames[t] = res
    return frames


def build(base=None):
    """The strips: the idle from its hand-drawn body, its head and the bobbing blades; the actions from their
    finished tables (FRAMES), or the automatic steps for a tag not finished yet. base: write the automatic action
    frames there as tables instead."""
    body = table(os.path.join(DESIGN, "body_idle.txt"))
    front, idle_h = heads()
    found = idle_place()
    rb = readbacks()
    frames, ms = {}, {}
    f0 = idle_frame(body, idle_h, found, 0)
    ys, xs = np.nonzero(f0 != ".")
    feet = np.nonzero((f0[ys.max() - 2:ys.max() + 1] != ".").any(0))[0]
    mid = (feet.min() + feet.max()) / 2.0
    frames["idle"] = [place(idle_frame(body, idle_h, found, k), mid) for k in range(8)]
    ms["idle"] = [fr["ms"] for _, fr in rb["idle"]]
    if base:
        os.makedirs(K.lp(base), exist_ok=True)
        for t, frs in auto_actions(rb, front).items():
            write_frames(os.path.join(base, f"{t}.txt"), frs)
        return None, None
    auto = None
    for t in TAGS[1:]:
        path = os.path.join(FRAMES, f"{t}.txt")
        if os.path.exists(K.lp(path)):
            frames[t] = read_frames(path)
        else:
            auto = auto or auto_actions(rb, front)
            frames[t] = auto[t]
        ms[t] = [fr["ms"] for _, fr in rb[t]]
    return {t: [rgba(L) for L in frs] for t, frs in frames.items()}, ms


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review")
    ap.add_argument("--base")
    a = ap.parse_args()
    built, ms = build(a.base)
    if a.base:
        print("wrote the automatic action frames in", a.base)
        return
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
