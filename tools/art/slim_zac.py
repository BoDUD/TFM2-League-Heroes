#!/usr/bin/env python3
"""league_zac made slimmer, carved square by square from his own pictures (the user, 2026-11-16: 「感觉扎克模型有点问题？
有点胖？扎克身体应该是瘦的」, after a Codex redraw: 「扎克你自己调整吧 codex画不好」, then on the direction sample:
「扎克选B」 - the clearly slimmer one, 16 columns narrower, the legs as long as they were).

    python tools/art/slim_zac.py                  # hd/wide/ -> hd/idle.png (+ idle_4x.png), hd/pose_<name>.png (+ .json)
    python tools/art/slim_zac.py --check          # exit 1 when a written picture is not what this makes
    python tools/art/slim_zac.py --review DIR     # before / after x6 and the seams on the wide pictures (nothing written)
    python tools/art/slim_zac.py --only idle,a_wind --review DIR

The wide pictures (assets/source/zac/hd/wide/: the design tools/art/design_zac_model.py wrote and Codex's key poses
tools/art/design_zac_poses.py read back, each pose with the design's head pasted at its json's head_at) are not
redrawn: whole seams come out of them, one square a line, nothing resampled (seam carving with forward energy):

- a seam runs along every line of its picture (rows: a vertical seam, columns out; columns: a horizontal one, rows
  out) and takes one square out of each, the squares beyond it moving one square in; a partial seam (`domain`) cuts only
  some lines and leaves the rest as they are (an arm stretched sideways thinned without moving the body);
- it cuts a part's flat shading runs: a square of a run of three or more of its colour (a run of two of the outline, or
  a single highlight, never - the 2-square outline, the highlights and the veins stay); a part narrower than MINW is
  never cut; changing column between two lines costs the vertical continuities it breaks there (a jog in an outline or
  a band), more where earlier seams already jogged (the steps spread along an outline);
- the head, the face, the grin and the tendril (design_zac_poses POLY and TENDRIL where the pose has the design's head,
  else KEEP the pose's own face) and a square round them are never cut, and every line through them is cut on the same
  side of them, so they move whole, square for square as drawn;
- `bands` aim each seam at a part (labels: NA near arm, FA far arm, T torso, NL near leg, FL far leg - each pose's
  `parts` polygons on its wide picture, the rest of the figure T). The design is sample B as the user picked it (the
  near arm 5, the near shoulder, back and waist 7, the near thigh and shin 4, the far ones 5, the far arm 2-4, the hands
  1-2: `idle_plan`); a pose loses B's share of each of its parts' own width (SHARE: auto_counts), a limb stretched
  sideways thinned by horizontal seams across it instead (its length kept, tapering to its root and its hand), a hand
  or a foot only where it is wide; a pose that is one mass of slime (the ball, the splat, the melt, the puddle) as many
  columns narrower on each side of its face (`blob`).
A seam crossing a line without its part cuts clear squares there that move nothing of him (past his last square, or
past his first on the torso's side): a line moved whole against its neighbours would jut out. Specks a seam shuts in
(1-3 squares) take the outline. hd/slim_zac.json keeps what rig_zac.py needs of the cut (the design's standing column,
its near arm's last column by rows, where each pose stands - its head where it was against the design's - and the
RUBBER and PARTS boxes), and every pose's head_at is written into its json.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
HD = os.path.join(ROOT, "assets", "source", "zac", "hd")
WIDE = os.path.join(HD, "wide")
MAPS = os.path.join(HD, "slim_zac.json")

# the design's head and tendril on the wide hd/idle.png (design_zac_poses.POLY / TENDRIL / FACE, kept here as they
# were: rig_zac.py reads the slim ones from slim_zac.json)
POLY = [(49.0, 13.0), (58.0, 12.0), (62.0, 15.0), (66.0, 19.0), (69.5, 22.0), (70.0, 30.0), (69.5, 38.0), (66.0, 42.0),
        (56.0, 42.0), (51.0, 39.0), (49.0, 32.0)]
TENDRIL = [(41.0, 0.0), (64.0, 0.0), (64.0, 8.0), (57.0, 9.0), (53.0, 8.0), (51.0, 11.0), (55.0, 13.0), (49.0, 14.0),
           (43.0, 10.0), (41.0, 5.0)]
FACE = (48, 12)                            # the face box's top-left square on the wide idle (rig_zac FACE)

INF = 1e9
AIR, NA, T, HEAD, TEND, FA, NL, FL = range(8)
NAMES = ["air", "NA", "T", "HEAD", "TEND", "FA", "NL", "FL"]
OUTLINE = {(1, 12, 15), (1, 15, 21), (6, 25, 16), (2, 28, 32)}
HIGH = {(225, 250, 102), (226, 251, 108), (182, 240, 96), (149, 231, 94), (252, 252, 248), (99, 219, 80)}
VEIN = {(1, 47, 63), (0, 56, 68), (1, 71, 75), (1, 82, 79), (1, 95, 85)}
OUT_KEYS = np.array([(r << 16) | (g << 8) | b for r, g, b in OUTLINE], np.int64)
RUN_COST = {"out": {1: INF, 2: INF, 3: 2.5}, "high": {1: INF, 2: 8.0, 3: 4.0, 4: 1.5},
            "vein": {1: 8.0, 2: 4.0, 3: 1.2}, "mid": {1: 6.0, 2: 2.5, 3: 0.7}, "gap": {1: INF, 2: 6.0, 3: 2.0}}
RUN_LONG = {"out": 0.4, "high": 0.8, "vein": 0.3, "mid": 0.15, "gap": 0.2}
MINW = {NA: 11, T: 7, FA: 9, NL: 9, FL: 9}
AIR_IN_BAND = 0.3                         # a clear square where a part may be cut too: a little dearer
XK = [0.15, 0.3, 0.5, 0.75, 1.0, 0.75, 0.5, 0.3, 0.15]   # a crossing's cost spread to the lines round it
W_HITS, W_MOVE, W_SH, W_X, C_X = 0.35, 0.08, 0.6, 0.25, 3.0


def lp(path):
    """Long-path safe (Windows)."""
    p = os.path.abspath(path)
    return "\\\\?\\" + p if os.name == "nt" and not p.startswith("\\\\?\\") and len(p) > 240 else p


def load(path):
    return np.asarray(Image.open(lp(path)).convert("RGBA")).copy()


def poly_mask(shape, pts):
    img = Image.new("L", (shape[1], shape[0]), 0)
    ImageDraw.Draw(img).polygon([tuple(p) for p in pts], fill=255)
    return np.asarray(img) > 0


# ------------------------------------------------------------------------------------------------- costs
def keys_of(d):
    k = (d[..., 0].astype(np.int64) << 16) | (d[..., 1].astype(np.int64) << 8) | d[..., 2].astype(np.int64)
    k[d[..., 3] == 0] = -1
    return k


def kind(key):
    if key < 0:
        return "air"
    rgb = ((key >> 16) & 255, (key >> 8) & 255, key & 255)
    if rgb in OUTLINE:
        return "out"
    if rgb in HIGH:
        return "high"
    if rgb in VEIN:
        return "vein"
    return "mid"


def local_cost(keys, gap=None):
    """Cutting a square: by the run of its colour along its line (short runs dear, the outline's two never); `gap`:
    the costs of a clear run shut in by the figure (by its length)."""
    gap = gap or RUN_COST["gap"]
    H, W = keys.shape
    C = np.zeros((H, W))
    for y in range(H):
        k = keys[y]
        x = 0
        while x < W:
            e = x
            while e + 1 < W and k[e + 1] == k[x]:
                e += 1
            n = e - x + 1
            kd = kind(k[x])
            if kd == "air":
                c = 0.0 if (x == 0 or e == W - 1) else gap.get(n, RUN_LONG["gap"])
            else:
                c = RUN_COST[kd].get(n, RUN_LONG[kd])
            C[y, x:e + 1] = c
            x = e + 1
    return C


def pair_cost(a, b):
    diff = a != b
    hard = (a < 0) | (b < 0) | np.isin(a, OUT_KEYS) | np.isin(b, OUT_KEYS)
    return np.where(diff, np.where(hard, 1.5, 1.0), 0.0)


def shear_tables(keys):
    """Per line pair: s1[x] (the first line cut left of the second's: its square x + 1 comes over the second's x) and
    s2[x] (the other way), counted where a continuity across the lines at x or x + 1 breaks."""
    H, W = keys.shape
    s1 = np.zeros((H - 1, W - 1))
    s2 = np.zeros((H - 1, W - 1))
    for y in range(H - 1):
        t, b = keys[y], keys[y + 1]
        base = np.minimum(pair_cost(t[:-1], b[:-1]), pair_cost(t[1:], b[1:]))
        s1[y] = np.maximum(0, pair_cost(t[1:], b[:-1]) - base)
        s2[y] = np.maximum(0, pair_cost(t[:-1], b[1:]) - base)
    return s1, s2


def edge_counts(keys):
    cat = np.where(keys < 0, 0, np.where(np.isin(keys, OUT_KEYS), 1, 2))
    e = (cat[:, :-1] != cat[:, 1:]).astype(int)
    z = np.zeros((keys.shape[0], 1), int)
    return np.concatenate([z, np.cumsum(e, 1), z], 1)[:, :keys.shape[1] + 1]


def edge_air(row):
    """The clear squares of a line that reach its ends through clear squares."""
    air = row == AIR
    out = np.zeros(len(row), bool)
    i = 0
    while i < len(row) and air[i]:
        out[i] = True
        i += 1
    i = len(row) - 1
    while i >= 0 and air[i]:
        out[i] = True
        i -= 1
    return out


def label_runs(L):
    H, W = L.shape
    R = np.zeros((H, W), int)
    for y in range(H):
        x = 0
        while x < W:
            e = x
            while e + 1 < W and L[y, e + 1] == L[y, x]:
                e += 1
            R[y, x:e + 1] = e - x + 1
            x = e + 1
    return R


# ------------------------------------------------------------------------------------------------- orientation
# a seam's side: L (rows cut, what is right of the cut moves left), R (rows, the left part moves right), U (columns
# cut, what is below moves up), D (columns, what is above moves down). Canonical: lines are rows, the part after the cut
# moves towards it, one clear square past each line's end (the cut there: the line stays as it was).
def canon(a, side):
    if side == "L":
        return a
    if side == "R":
        return a[:, ::-1]
    t = np.swapaxes(a, 0, 1)
    return t if side == "U" else t[:, ::-1]


def uncanon(a, side):
    if side in ("L", "R"):
        return canon(a, side)
    t = a if side == "U" else a[:, ::-1]
    return np.swapaxes(t, 0, 1)


# ------------------------------------------------------------------------------------------------- one seam
def seam(keys, C, allowed, sh, xh):
    """The least-cost seam (one cut a line) in canonical arrays (C: the cost of cutting each square) -> (path, cost,
    sheared, crossed)."""
    H, W = keys.shape
    Bc = edge_counts(keys)
    C = np.where(allowed, C, INF)
    s1, s2 = shear_tables(keys)
    dp = C[0].copy()
    back = np.zeros((H, W), int)
    ar = np.arange(W)
    a, b = ar[:, None], ar[None, :]
    shear0, cross0 = [], []
    for y in range(1, H):
        S1 = np.concatenate([[0.0], np.cumsum(s1[y - 1])])
        S2 = np.concatenate([[0.0], np.cumsum(s2[y - 1])])
        M0 = np.where(a < b, S1[b] - S1[a], S2[a] - S2[b])
        lo, hi = np.minimum(a, b), np.maximum(a, b)
        X = np.maximum(Bc[y - 1][hi] - Bc[y - 1][lo], Bc[y][hi] - Bc[y][lo])
        M = M0 + W_MOVE * np.abs(a - b) + W_SH * sh[y - 1] * (M0 > 0) + W_X * X * (1 + C_X * xh[y - 1])
        shear0.append(M0)
        cross0.append(X)
        tot = dp[:, None] + M
        best = tot.argmin(0)
        dp = tot[best, ar] + C[y]
        back[y] = best
    x = int(dp.argmin())
    cost = float(dp[x])
    if cost >= INF:
        raise SystemExit("no seam fits (a line with nowhere to cut)")
    path = [x]
    for y in range(H - 1, 0, -1):
        x = int(back[y, x])
        path.append(x)
    path = path[::-1]
    sheared = np.array([shear0[y][path[y], path[y + 1]] > 0 for y in range(H - 1)], float)
    crossed = np.array([cross0[y][path[y], path[y + 1]] for y in range(H - 1)], float)
    return path, cost, sheared, crossed


class Picture:
    """A wide picture being carved: its squares, labels and where each square came from."""

    def __init__(self, name, d, L):
        self.name = name
        self.img = d.copy()
        self.L = L.copy()
        H, W = L.shape
        self.oy, self.ox = np.mgrid[0:H, 0:W]
        self.hits, self.spread = {}, {}
        self.log = []
        self.fallback = "air" if name == "idle" else "parts"
        # a pose's narrow gaps (between fingers, a hooked hand and its palm) stay open
        self.gap = None if name == "idle" else {1: INF, 2: INF, 3: 8.0}

    def allowed(self, side, bands, domain, prot):
        """Canonical mask of the squares a seam may cut (+ the clear square past each line's end)."""
        L = canon(self.L, side)
        keys = canon(keys_of(self.img), side)
        lines, W = L.shape
        prot_m = (L == HEAD) | (L == TEND)
        R = label_runs(L)
        wide = np.ones(L.shape, bool)
        for k, n in MINW.items():
            wide &= ~((L == k) & (R < n))
        cost = local_cost(keys, self.gap)
        if self.name != "idle":
            # a long run of outline (a dome's top, a sole) is the edge of a part, not a thin part: it may be cut
            wide |= np.isin(keys, OUT_KEYS) & (cost <= RUN_LONG["out"])
        real = canon(self.oy, side) >= 0
        A = np.zeros((lines, W + 1), bool)
        extra = np.zeros((lines, W + 1))
        oline = self.line_index(side)
        for i in range(lines):
            o = oline[i]
            if domain is not None and not (domain[0] <= o <= domain[1]):
                A[i, W] = True                          # outside the domain: the line stays as it is
                continue
            xs = np.nonzero(prot_m[i])[0]
            ok_side = np.ones(W, bool)
            if len(xs):
                if prot == "shift":
                    ok_side[xs.min():] = False
                else:
                    ok_side[:xs.max() + 1] = False
            labs = None
            for (l0, l1), lab in bands:
                if l0 <= o <= l1:
                    labs = lab
                    break
            labs = labs or ["air"]
            want = np.isin(L[i], [NAMES.index(n) for n in labs if not n.startswith("air")])
            air = L[i] == AIR
            fig = np.nonzero(L[i] != AIR)[0]
            if len(fig):
                # (canonical lines: what is past the cut moves) clear squares past the line's first square of him
                # ("air+": what is before it stays), before it ("air<") or past his last ("air>": nothing moves -
                # for an R seam that is the clear squares before him on the picture's left)
                idx = np.arange(W)
                for name, m in (("air+", idx >= fig[0]), ("air<", idx < fig[0]), ("air>", idx > fig[-1])):
                    if name in labs:
                        want |= air & m
            elif any(n.startswith("air") for n in labs):
                want |= air
            ok = (want & wide[i] | (air if "air" in labs else False)) & ok_side & (cost[i] < INF)
            if "air" in labs and len(labs) > 1:
                extra[i, :W][air] += AIR_IN_BAND
            if not (ok & real[i]).any() and domain is not None:
                A[i, W] = True                          # a partial seam: a line where its part is too thin stays
                continue
            if not (ok & real[i]).any() and self.fallback == "air":
                ok = air & ok_side & (cost[i] < INF)       # (the design: sample B as the user picked it)
            if not (ok & real[i]).any():
                # none of its parts on this line: any part there (not air at the picture's edge - a line moved whole
                # against its neighbours juts out), else clear squares
                inner = air & ~edge_air(L[i])
                ok = ((L[i] > 0) & (L[i] != HEAD) & (L[i] != TEND) & wide[i] | inner) & ok_side & (cost[i] < INF)
                if not (ok & real[i]).any():
                    ok = air & ok_side & (cost[i] < INF)
            ok &= real[i]                               # never the clear squares a partial seam left at a line's end
            if not ok.any() and (len(xs) == 0 or prot == "stay"):
                A[i, W] = True                          # nothing to cut here: the line keeps its squares
                continue
            if not ok.any():
                raise SystemExit(f"{self.name}: line {o} ({side}): nowhere to cut ({labs})")
            A[i, :W] = ok
        return A, extra

    def line_index(self, side):
        """For each canonical line, its line number in the wide picture's terms (rows for L / R, columns for U / D) -
        the commonest original row / column of the squares along it."""
        src = canon(self.oy if side in "LR" else self.ox, side)
        op = canon(self.img[..., 3] > 0, side)
        out = []
        for i in range(src.shape[0]):
            v = src[i][op[i]] if op[i].any() else src[i][src[i] >= 0]
            out.append(int(np.bincount(v).argmax()) if len(v) else -1)
        # lines with nothing on them: their neighbours' numbering
        out = np.array(out)
        for i in range(len(out)):
            if out[i] < 0:
                j = i - 1 if i > 0 else i + 1
                out[i] = out[j] + (1 if j < i else -1) if 0 <= j < len(out) else i
        return out

    def cut(self, side, bands, domain=None, prot="shift", n=1, tag=""):
        """n seams on `side` (L R U D), each line's cut in its `bands` [((first, last line), [labels])] (lines: rows for
        L / R, columns for U / D, numbered as in the wide picture); `domain` (first, last line): only those lines cut;
        `prot`: the head and tendril move with the cut ("shift": cut before them on every line through them) or stay
        ("stay": cut past them)."""
        pad = lambda a, v: np.concatenate([a, np.full((a.shape[0], 1) + a.shape[2:], v, a.dtype)], 1)
        for _ in range(n):
            A, extra = self.allowed(side, bands, domain, prot)
            img, L = canon(self.img, side), canon(self.L, side)
            oy, ox = canon(self.oy, side), canon(self.ox, side)
            lines, W = L.shape
            hits = self.hits.get(side)
            if hits is None or hits.shape != (lines, W):
                hits = np.zeros((lines, W))
            sh, xh = self.spread.get(side, (None, None))
            if sh is None or len(sh) != lines - 1:
                sh, xh = np.zeros(lines - 1), np.zeros(lines - 1)
            imgp, Lp, oyp, oxp, hp = pad(img, 0), pad(L, AIR), pad(oy, -1), pad(ox, -1), pad(hits, 0.0)
            keys = keys_of(imgp)
            C = local_cost(keys, self.gap) + W_HITS * hp + extra
            path, cost, sheared, crossed = seam(keys, C, A, sh, xh)
            sh = sh + np.convolve(sheared, [0.3, 0.6, 1.0, 0.6, 0.3], mode="same")
            xh = xh + np.convolve(np.minimum(crossed, 2.0), XK, mode="same")
            rows = np.arange(lines)
            for y, x in zip(rows, path):
                if x < W:
                    hp[y, max(0, x - 1)] += 1
                    hp[y, x + 1] += 1
            keep = np.ones((lines, W + 1), bool)
            keep[rows, path] = False
            cut_ = lambda a: a[keep].reshape((lines, W) + a.shape[2:])
            # the line ends every line has as padding go (a full seam): the picture one square narrower
            o_after = cut_(oyp)
            n_trail = 0
            while n_trail < W and (o_after[:, W - 1 - n_trail] < 0).all():
                n_trail += 1
            if n_trail:
                cut0 = cut_
                cut_ = lambda a, c=cut0, k=n_trail: c(a)[:, :W - k]
            removed = [[int(oy[y, x]), int(ox[y, x]), NAMES[L[y, x]]] for y, x in zip(rows, path) if x < W]
            self.img, self.L = uncanon(cut_(imgp), side), uncanon(cut_(Lp), side)
            self.oy, self.ox = uncanon(cut_(oyp), side), uncanon(cut_(oxp), side)
            self.hits[side] = cut_(hp)
            self.spread[side] = (sh, xh)
            self.log.append({"tag": tag, "side": side, "cost": round(cost, 2), "removed": removed})

    def finish(self):
        """Specks shut in -> outline; the clear border cropped."""
        op = self.img[..., 3] > 0
        lab, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
        shut = 0
        for j in range(1, n + 1):
            h = lab == j
            if h.sum() <= 3:
                self.img[h] = (1, 12, 15, 255)
                shut += int(h.sum())
        op = self.img[..., 3] > 0
        ys, xs = np.nonzero(op)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        for k in ("img", "L", "oy", "ox"):
            setattr(self, k, getattr(self, k)[y0:y1, x0:x1])
        return shut

    def where(self, y, x):
        """Where the wide picture's square (x, y) went (None: cut)."""
        m = (self.oy == y) & (self.ox == x)
        if not m.any():
            return None
        ys, xs = np.nonzero(m)
        return int(xs[0]), int(ys[0])


# ------------------------------------------------------------------------------------------------- the parts
def head_masks(d, at):
    """The design's head (POLY) and tendril (TENDRIL) where a picture has them, its face box at `at` (FACE on the
    design), each with a square round it; only the picture's own squares."""
    op = d[..., 3] > 0
    cross = ndimage.generate_binary_structure(2, 1)
    dx, dy = at[0] - FACE[0], at[1] - FACE[1]
    head = poly_mask(d.shape, [(x + dx, y + dy) for x, y in POLY])
    tend = poly_mask(d.shape, [(x + dx, y + dy) for x, y in TENDRIL])
    head = ndimage.binary_dilation(head & op, cross) & op
    tend = ndimage.binary_dilation(tend & op, cross) & op & ~head
    return head, tend


def idle_arm_right(y):
    """The design's near arm: its last column a row (its outline against the torso / the near foot)."""
    if 19 <= y <= 29:
        return 25
    if 30 <= y <= 33:
        return 24
    if 34 <= y <= 56:
        return 23
    return {57: 22, 58: 21, 59: 21, 60: 20}.get(y, 14 if 61 <= y <= 64 else -1)


def idle_labels(d):
    H, W = d.shape[:2]
    op = d[..., 3] > 0
    head, tend = head_masks(d, FACE)
    L = np.zeros((H, W), np.int8)
    L[op] = T
    L[head], L[tend] = HEAD, TEND
    prot = head | tend
    for y in range(H):
        xs = np.nonzero(prot[y])[0]
        pr = xs.max() if len(xs) else None
        for x in range(W):
            if not op[y, x] or prot[y, x]:
                continue
            if 19 <= y <= 64 and x <= idle_arm_right(y):
                L[y, x] = NA
            elif y >= 45:
                L[y, x] = -1
            elif (pr is not None and x > pr) or (y in (43, 44) and x >= 66):
                L[y, x] = FA
    for y in range(45, H):
        nr = 42 if y == 45 else 43 if y in (46, 47) else next(x for x in range(30, W) if not op[y, x]) - 1
        for x in range(W):
            if L[y, x] == -1:
                L[y, x] = NL if x <= nr else FA if (y <= 58 and x >= 66) else FL
    return L


def poly_labels(d, at, parts, keep_face=None, keep_tendril=None):
    """A pose's labels: its head and tendril (or `keep_face`: a polygon round the pose's own face and tendril), then
    each part's polygons in order (a square in two is the first's), the rest of the figure T."""
    op = d[..., 3] > 0
    L = np.zeros(d.shape[:2], np.int8)
    L[op] = T
    for name in ("FL", "NL", "FA", "NA"):
        for pts in parts.get(name, ())[::-1]:
            L[poly_mask(d.shape, pts) & op] = NAMES.index(name)
    if keep_face is not None:                    # Codex's own face and tendril: one polygon or several
        polys = keep_face if isinstance(keep_face[0][0], (tuple, list)) else [keep_face]
        for pts in polys:
            L[poly_mask(d.shape, pts) & op] = HEAD
    else:
        head, tend = head_masks(d, at)
        L[tend], L[head] = TEND, HEAD
        # what the paste left of Codex's own tendril beside the design's (a second knob, an outline bit at its
        # root): any loose piece of him touching the tendril above the face box moves with it
        prot = (L == HEAD) | (L == TEND)
        lab, n = ndimage.label(op & ~prot, structure=np.ones((3, 3)))
        near = ndimage.binary_dilation(L == TEND, structure=np.ones((3, 3)))
        for i in set(lab[near & (lab > 0)].tolist()):
            m = lab == i
            if np.nonzero(m)[0].max() <= at[1] + 2:
                L[m] = TEND
    if keep_tendril is not None:                 # Codex's own tendril (design_zac_poses NO_TENDRIL)
        L[poly_mask(d.shape, keep_tendril) & op & (L != HEAD)] = TEND
    return L


# ------------------------------------------------------------------------------------------------- the plans
# a band: ((first line, last line), labels); lines numbered as in the wide picture.
B_ORDER = ["NA", "TNL", "FA", "NA", "TFL", "FAFL", "NA", "TNL", "FA", "NA", "TFL", "FAFL", "NA", "TNL", "TNL", "TFL"]
END = 999


def stand(P, hip, t_top, na, fa, order=B_ORDER, na_h=None, fa_h=None, far_leg="FAFL", tfl_air=False, over=None,
          counts=None, flp=None, nap=None, na_exit=None):
    """Sample B's seams on a picture standing as the design does (the design: sample B itself, C:/t/par_work/zac_slim):
    NA - 5 through the near arm (rows `na`: its top, the last row of its way in, its hand's first row, its last row -
    clear squares allowed at the top and the hand, so the seam goes in and out through them), TNL - 4 from the near
    shoulder dome (`t_top`) down the back to the hips (`hip`) and on down the near leg, TFL - 3 down the far leg, FA - 2
    through the far arm (rows `fa`: its top, its fingers' first row) and its hand, FAFL - 2 through the far upper arm
    and down the far leg. A limb stretched sideways (`na_h`, `fa_h`: {"side": "D" / "U", "cols": (first, last),
    "taper": (end, step)}) is thinned by as many horizontal seams across it instead, each cutting the columns of
    `cols` (its ends stepped `step` columns in a seam - "lo", "hi" or "both": the limb tapers to its root and its
    hand instead of stepping); `far_leg` "TFL": the far upper arm is stretched, so the far leg's two go down the
    back instead; `over`: bands of a kind replaced (a pose whose thigh rises beside the torso)."""
    na_top, na_entry, na_hand, na_bot = na
    fa_top, fa_fing = fa
    bands = {
        "NA": [((0, na_top - 1), ["air"]), ((na_top, na_entry), ["NA", "air"]), ((na_entry + 1, na_hand - 1), ["NA"]),
               ((na_hand, na_bot), ["NA", "air"]), ((na_bot + 1, END), ["air"])],
        "TNL": [((0, t_top - 1), ["air"]), ((t_top, t_top + 7), ["T", "air"]), ((t_top + 8, hip), ["T"]),
                ((hip + 1, END), ["NL"] + (["air"] if tfl_air else []))],
        "TFL": [((0, t_top - 1), ["air"]), ((t_top, t_top + 7), ["T", "air"]), ((t_top + 8, hip), ["T"]),
                ((hip + 1, END), ["FL"] + (["air"] if tfl_air else []))],
        "FA": [((0, fa_top - 1), ["air"]), ((fa_top, fa_fing - 1), ["FA"]), ((fa_fing, END), ["FA", "air"])],
        "FAFL": [((0, fa_top - 1), ["air"]), ((fa_top, hip), ["FA"]), ((hip + 1, END), ["FL"])]}
    if P.name != "idle":
        # a pose's limbs lie anywhere: a seam crossing a line without its part cuts there clear squares that move
        # nothing of him (the torso's past the near arm, the far arm's past his far side, the near arm's before him)
        for k in ("TNL", "TFL"):
            bands[k] = [(r, ["air+" if n == "air" else n for n in labs]) for r, labs in bands[k]]
        for k in ("FA", "FAFL"):
            bands[k] = [(r, ["air>" if n == "air" else n for n in labs]) for r, labs in bands[k]]
        bands["NA"] = [(r, ["air>"] if labs == ["air"] else labs) for r, labs in bands["NA"]]
    bands.update(over or {})
    prot = {"NA": "shift", "TNL": "shift", "TFL": "shift", "FA": "stay", "FAFL": "stay"}
    hs = {"NA": na_h, "FA": fa_h}
    done = {"NA": 0, "FA": 0, "FLp": 0, "NAp": 0}
    if isinstance(counts, dict) and counts.get("auto"):
        fix = {k: v for k, v in counts.items() if k != "auto"}
        counts = dict(auto_counts(P, na_h, fa_h, far_leg), **fix)
        P.counts = counts
    elif counts == "auto":
        counts = auto_counts(P, na_h, fa_h, far_leg)
    if counts:
        order = spread_order(counts)
    for k in order:
        if k == "NAp":                                 # the near hand alone (`nap`: first row, last row, step), its
            r0, r1, step = nap                         # outer side moving in
            i = done["NAp"]
            done["NAp"] += 1
            P.cut("R", [((0, END), ["NA"])], domain=(r0 + i * step, r1), prot="stay", tag="NAp")
            continue
        if k == "TX":                                  # the torso, then out of the figure under the hips (clear squares)
            P.cut("L", [((0, t_top - 1), ["air"]), ((t_top, t_top + 7), ["T", "air"]), ((t_top + 8, hip), ["T"]),
                        ((hip + 1, END), ["air"])], prot="shift", tag="TX")
            continue
        if k == "FLp":                                 # the far leg from `flp` (first row, step, last row - above the
            r0, step, r1 = flp                         # foot: its toes stay whole): its own seams
            i = done["FLp"]
            done["FLp"] += 1
            P.cut("L", [((0, END), ["FL"])], domain=(r0 + i * step, r1), prot="stay", tag="FLp")
            continue
        if k == "FAFL" and far_leg == "TFL":
            k = "TFL"
        h = hs.get(k)
        if h:
            c0, c1 = h["cols"]
            end, step = h.get("taper", (None, 0))
            i = done[k]
            done[k] += 1
            lo, hi = {"hi": (c0, c1 - i * step), "lo": (c0 + i * step, c1),
                      "both": (c0 + i * step, c1 - i * step)}.get(end, (c0, c1))
            P.cut(h["side"], [((lo, hi), [k])], domain=(lo, hi), prot="stay", tag=k + "h")
            continue
        if k == "NA" and na_exit:                       # each seam leaves the arm on its own row (`na_exit`: the
            first, step = na_exit                       # first row, rows between): the arm's outer side steps in
            i = done["NA"]                              # a square at a time down a long stretch
            done["NA"] += 1
            last = first + i * step
            P.cut("R", [((0, na_top - 1), ["air>"]), ((na_top, na_entry), ["NA", "air"]),
                        ((na_entry + 1, last), ["NA"]), ((last + 1, END), ["air>"])], prot="stay", tag=k)
            continue
        if k == "NA" and P.name != "idle":
            # the near arm's outer side moves in (lines without it stay as they are): a raised or swung arm's end
            # never juts out of the body below it (the design: sample B's own seams, the arm the whole height)
            P.cut("R", bands[k], prot="stay", tag=k)
            continue
        P.cut("L", bands[k], prot=prot[k], tag=k)


# each part's share of its width the design lost in sample B (the median width a row: near arm 19 -> 14, torso 22 -> 15,
# far arm 11 -> 8, near leg 16 -> 12, far leg 18 -> 13): a pose's part is cut by as many squares of its own width
SHARE = {NA: 0.26, T: 0.32, FA: 0.27, NL: 0.25, FL: 0.28}


def part_width(L, op, k, axis):
    """A part's median width: squares a row (axis 1) or a column (axis 0) where it has 3 or more."""
    per = ((L == k) & op).sum(axis)
    per = per[per >= 3]
    return float(np.median(per)) if len(per) else 0.0


def auto_counts(P, na_h=None, fa_h=None, far_leg="FAFL"):
    """B's share of each part of this pose -> seams of each kind: TNL as many as the near leg's, TFL the torso's
    rest, the far leg's rest down the far upper arm (FAFL) or on its own (FLp: `far_leg` "FLp"), the far arm's rest
    through it (FA); a sideways limb's across it (its width a column)."""
    op = P.wide[..., 3] > 0
    n = {k: int(round(part_width(P.L0, op, k, 0 if (k == NA and na_h) or (k == FA and fa_h) else 1) * SHARE[k]))
         for k in SHARE}
    c = {"NA": n[NA], "TNL": min(n[NL], n[T])}
    c["TFL"] = n[T] - c["TNL"]
    rest = max(0, n[FL] - c["TFL"])
    if far_leg == "FAFL" and not fa_h:
        c["FAFL"] = rest
        c["FA"] = max(0, n[FA] - rest)
    else:
        c["FLp"] = rest if far_leg == "FLp" else 0
        c["FA"] = n[FA]
    P.counts = c
    return c


def spread_order(counts):
    """Each kind's seams spread evenly through the run (the kind furthest behind its share goes next)."""
    cycle = ["NA", "NAp", "TNL", "FA", "TFL", "TX", "FAFL", "FLp"]
    total = {k: n for k, n in counts.items() if n}
    done = {k: 0 for k in total}
    out = []
    for _ in range(sum(total.values())):
        k = min(total, key=lambda k: ((done[k] + 1) / total[k], cycle.index(k)))
        done[k] += 1
        out.append(k)
    return out


def blob(P, left, right, rows=0):
    """A pose that is one mass of slime (balled up, splatted, melted, a puddle): `left` seams through it on the near
    side of his face, `right` on the far side, `rows` horizontal ones under his face (a ball smaller, not taller)."""
    # (canonical lines: clear squares past his first square on a line move nothing before them, past his last
    # nothing at all - a line moved whole against its neighbours juts out of him)
    for k in spread_order({"TNL": left, "FA": right, "TX": rows}):
        if k == "TNL":
            P.cut("L", [((0, END), ["T", "air+"])], prot="shift", tag="TNL")
        elif k == "FA":
            P.cut("L", [((0, END), ["T", "air>"])], prot="stay", tag="FA")
        else:
            P.cut("U", [((0, END), ["T", "air>"])], prot="stay", tag="TX")


def idle_plan(P):
    stand(P, hip=44, t_top=12, na=(19, 29, 53, 64), fa=(12, 53))


PICTURES = {"idle": (idle_labels, idle_plan)}
POSES = {
    # the crouch before R's hop (and after E's landing): the design's stance, lower
    "r_crouch": dict(parts={"NA": [[(0, 14), (31, 14), (31, 35), (28.5, 36), (28.5, 62), (0, 62)]],
                            "FA": [[(64, 10), (98, 10), (98, 62), (79, 62), (79, 50), (72, 44), (64, 44)]],
                            "NL": [[(28.5, 38), (46.5, 38), (46.5, 62), (28.5, 62)]],
                            "FL": [[(46.5, 38), (66, 38), (79, 50), (79, 62), (46.5, 62)]]},
                     plan=lambda P: stand(P, hip=42, t_top=12, na=(14, 28, 51, 61), fa=(14, 53), counts="auto")),
    # Q's slam: both arms down on the ground, wide
    "q_slam": dict(parts={"NA": [[(0, 10), (33, 10), (33, 33), (29, 36), (26.5, 45), (26.5, 64), (0, 64)]],
                          "FA": [[(62, 10), (102, 10), (102, 64), (75, 64), (75, 42), (70, 40), (62, 40)]],
                          "NL": [[(26.5, 36), (49, 36), (51, 64), (26.5, 64)]],
                          "FL": [[(49, 36), (75, 42), (75, 64), (51, 64)]]},
                   plan=lambda P: stand(P, hip=40, t_top=11, na=(12, 28, 49, 63), fa=(12, 52), counts="auto")),
    # E's wind-up: the arms planted on the ground, the near thigh raised beside the torso
    "e_plant": dict(parts={"NA": [[(0, 18), (29, 18), (29, 41), (30.5, 41), (30.5, 64), (0, 64)]],
                           "NL": [[(29, 20), (43.5, 20), (43.5, 46), (61, 52), (61, 74), (30.5, 74), (30.5, 41),
                                   (29, 41)]],
                           "FL": [[(43.5, 41), (78, 41), (78, 74), (61, 74), (61, 52), (43.5, 46)]],
                           "FA": [[(70, 10), (110, 10), (110, 74), (78, 74), (78, 41), (70, 41)]]},
                    plan=lambda P: stand(P, hip=40, t_top=11, na=(18, 30, 41, 63), fa=(14, 57),
                                         counts={"auto": True, "NA": 0, "NAp": 2}, nap=(42, 63, 3),
                                         over={"TNL": [((0, 10), ["air"]), ((11, 18), ["T", "air"]),
                                                       ((19, 40), ["T", "NL"]), ((41, END), ["NL"])]})),
    # Q's wind-up: the near arm raised high behind him (its hand at the top)
    "q_wind": dict(parts={"NA": [[(0, 0), (60, 0), (64, 48), (56, 58), (42, 70), (0, 70)]],
                          "FA": [[(86, 55), (112, 55), (112, 115), (90, 115), (88, 95)]],
                          "NL": [[(28, 88), (60, 88), (60, 115), (28, 115)]],
                          "FL": [[(60, 88), (88, 95), (90, 115), (60, 115)]]},
                   plan=lambda P: stand(P, hip=90, t_top=50, na=(0, 4, 64, 72), fa=(60, 100), counts="auto",
                                        # the arm's underside runs on into his flank: the seams leave it one by one
                                        # down a long stretch (no step where the arm meets the flank); the torso's
                                        # seams pass right of the raised arm (or nick its inner side) above the torso
                                        na_exit=(46, 6),
                                        over={k: [((0, 57), ["air+", "NA"]), ((58, 65), ["T", "air+"]),
                                                  ((66, 90), ["T"]), ((91, END), [leg])]
                                              for k, leg in (("TNL", "NL"), ("TFL", "FL"))})),
    # Q's lift: both arms raised over his head, the tendril between them
    "q_lift": dict(parts={"NA": [[(0, 0), (32, 0), (32, 28), (28.5, 40), (26.5, 41), (26.5, 73), (0, 73)]],
                          "FA": [[(38, 0), (72, 0), (72, 73), (58, 73), (58, 45), (40, 28)]],
                          "NL": [[(0, 72), (29, 72), (29, 96), (0, 96)]],
                          "FL": [[(29, 72), (72, 72), (72, 96), (29, 96)]]},
                   plan=lambda P: stand(P, hip=72, t_top=41, na=(0, 4, 66, 72), fa=(4, 58), counts="auto")),
    # R's hop: in the air, the arms spread down to both sides
    "r_jump": dict(parts={"NA": [[(0, 15), (45, 15), (49, 28), (44, 40), (34, 62), (0, 62)]],
                          "FA": [[(86, 10), (122, 10), (122, 66), (95, 66), (92, 45), (86, 45)]],
                          "NL": [[(44, 38), (62, 38), (64, 66), (34, 66), (34, 62), (44, 40)]],
                          "FL": [[(62, 38), (88, 38), (92, 45), (95, 66), (64, 66)]]},
                   plan=lambda P: stand(P, hip=42, t_top=12, na=(15, 26, 46, 62), fa=(14, 48), counts="auto")),
    # the attack's wind-up: the near arm swung back over his shoulder (its upper arm lying sideways: thinned across,
    # tapering to the shoulder and the hand), the hand hanging behind
    "a_wind": dict(parts={"NA": [[(0, 0), (44, 0), (46, 25), (40, 32), (28, 40), (0, 40)]],
                          "NL": [[(15, 40), (56, 40), (58, 52), (52, 68), (15, 68)]],
                          "FL": [[(56, 40), (82, 44), (84, 68), (52, 68), (58, 52)]],
                          "FA": [[(84, 13), (106, 13), (106, 68), (86, 68), (82, 44)]]},
                   plan=lambda P: stand(P, hip=44, t_top=10, na=(0, 0, 0, 0), fa=(25, 52), counts="auto",
                                        na_h={"side": "D", "cols": (4, 42), "taper": ("both", 2)})),
    # the attack's punch: the fist thrown out on the far arm (sideways: thinned across, its forearm level for
    # rig_zac's RUBBER), the near leg lunging back
    "a_punch": dict(parts={"NA": [[(0, 10), (36, 10), (36, 26), (25, 38), (15, 48), (0, 48)]],
                           "NL": [[(0, 48), (15, 48), (25, 38), (36, 30), (50, 36), (52, 48), (45, 63), (0, 63)]],
                           "FL": [[(52, 44), (86, 44), (86, 63), (45, 63)]],
                           "FA": [[(84, 10), (117, 10), (117, 44), (84, 44)]]},
                    plan=lambda P: stand(P, hip=44, t_top=10, na=(12, 24, 40, 47), fa=(12, 40), counts="auto",
                                         fa_h={"side": "D", "cols": (86, 102), "taper": ("lo", 3)},
                                         far_leg="FLp", flp=(47, 2, 54))),
    # Q's reach: the far arm shot out along the ground (thinned across, tapering to the shoulder)
    "q_reach": dict(parts={"NA": [[(0, 8), (40, 8), (40, 26), (30, 34), (25.5, 42), (25.5, 60), (0, 60)]],
                           "NL": [[(25.5, 34), (51, 34), (52, 60), (25.5, 60)]],
                           "FL": [[(51, 34), (80, 38), (82, 60), (52, 60)]],
                           "FA": [[(78, 10), (126, 10), (126, 62), (86, 62), (82, 42), (76, 36)]]},
                    plan=lambda P: stand(P, hip=40, t_top=9, na=(10, 22, 42, 58), fa=(14, 50), counts="auto",
                                         fa_h={"side": "D", "cols": (88, 112), "taper": ("both", 2)},
                                         far_leg="FLp", flp=(44, 1, 50))),
    # E's pull: the body pulled back, the far arm stretched far out to the ground (thinned across)
    "e_pull": dict(parts={"NA": [[(0, 12), (34, 12), (34, 38), (25, 48), (22, 68), (0, 68)]],
                          "NL": [[(25, 45), (52, 45), (52, 77), (22, 77), (22, 68)]],
                          "FL": [[(52, 45), (75, 50), (88, 77), (52, 77)]],
                          "FA": [[(70, 12), (126, 12), (126, 77), (98, 77), (90, 64), (75, 50), (70, 45)]]},
                   plan=lambda P: stand(P, hip=46, t_top=12, na=(14, 30, 48, 67), fa=(14, 60), counts="auto",
                                        fa_h={"side": "D", "cols": (86, 108), "taper": ("both", 2)},
                                        far_leg="FLp", flp=(50, 2, 66))),
    # E's flight: lying in the air, both arms reaching out sideways (thinned across), the legs trailing under
    "e_fly": dict(parts={"NA": [[(0, 10), (44, 10), (44, 46), (0, 46)]],
                         "FA": [[(96, 10), (125, 10), (125, 48), (96, 48)]],
                         "NL": [[(55, 42), (106, 42), (106, 61), (55, 61)]]},
                  plan=lambda P: stand(P, hip=41, t_top=13, na=(0, 0, 0, 0), fa=(0, 0),
                                       counts={"auto": True, "TNL": 3, "TFL": 0, "TX": 6, "FLp": 0},
                                       na_h={"side": "D", "cols": (16, 42), "taper": ("both", 2)},
                                       fa_h={"side": "D", "cols": (98, 116), "taper": ("both", 2)}, far_leg="FLp",
                                       flp=(42, 2, 50))),
    # E's landing: both arms flung out sideways (thinned across)
    "e_land": dict(parts={"NA": [[(0, 10), (58, 10), (58, 32), (48, 36), (34, 44), (34, 52), (0, 52)]],
                          "FA": [[(100, 10), (137, 10), (137, 48), (100, 48)]],
                          "NL": [[(30, 40), (66, 40), (66, 66), (30, 66)]],
                          "FL": [[(66, 42), (118, 42), (118, 66), (66, 66)]]},
                   plan=lambda P: stand(P, hip=42, t_top=12, na=(0, 0, 0, 0), fa=(0, 0), counts="auto",
                                        na_h={"side": "D", "cols": (30, 56), "taper": ("both", 2)},
                                        fa_h={"side": "D", "cols": (102, 122), "taper": ("both", 2)}, far_leg="FLp",
                                        flp=(46, 2, 57))),
    # the death's stagger: the far arm flung out sideways (thinned across)
    "d_stagger": dict(parts={"NA": [[(0, 12), (27, 12), (28, 31), (25.5, 33), (25.5, 51), (22.5, 52), (22.5, 67),
                                     (0, 67)]],
                             "FA": [[(64, 10), (99, 10), (99, 48), (75, 48), (66, 43)]],
                             "NL": [[(25.5, 38), (40.5, 38), (40.5, 67), (22.5, 67), (22.5, 52), (25.5, 51)]],
                             "FL": [[(40.5, 38), (60, 38), (75, 52), (75, 67), (40.5, 67)]]},
                      plan=lambda P: stand(P, hip=40, t_top=12, na=(13, 27, 52, 66), fa=(13, 46),
                                           counts={"auto": True, "FA": 3},
                                           fa_h={"side": "D", "cols": (72, 92), "taper": ("both", 2)},
                                           far_leg="FLp", flp=(47, 2, 59))),
    # R's ball: balled up in the air - narrower and lower, still round (Codex's own tendril, tucked, kept)
    "r_ball": dict(keep_tendril=[(29.5, 0), (51, 0), (51, 6), (37.5, 6), (37.5, 9.5), (43, 10), (43, 11.5),
                                 (30, 11.5), (29.5, 5)],
                   plan=lambda P: blob(P, left=5, right=2, rows=5)),
    # R's landing: splatted flat (Codex's own squashed face and tendril kept)
    "r_splat": dict(keep_face=[[(61.5, 0), (85, 0), (85, 8), (72, 8), (76, 12), (63, 12), (61.5, 9)],
                               [(63, 15), (93, 15), (93, 34), (63, 34)]],
                    plan=lambda P: blob(P, left=13, right=5)),
    # the death's melt (Codex's half-closed eyes and drooping tendril kept)
    "d_melt": dict(keep_face=[[(61.5, 0), (88, 0), (88, 10), (79, 10), (78, 12), (69, 12), (65.5, 9), (61.5, 7)],
                              [(66, 22), (100, 22), (100, 47), (66, 47)]],
                   plan=lambda P: blob(P, left=11, right=5)),
    # the puddle (the melted face and the limp tendril in its middle kept)
    "d_puddle": dict(keep_face=[(43, 0), (62, 0), (62, 14), (43, 14)],
                     plan=lambda P: blob(P, left=8, right=6)),
}


def make(name):
    """The wide picture carved -> Picture."""
    if name == "idle":
        d = load(os.path.join(WIDE, "idle.png"))
        labels, plan = PICTURES["idle"]
        P = Picture(name, d, labels(d))
        P.head_at0 = list(FACE)
    else:
        d = load(os.path.join(WIDE, f"pose_{name}.png"))
        with open(lp(os.path.join(WIDE, f"pose_{name}.json")), encoding="utf-8") as f:
            at = json.load(f).get("head_at")
        spec = POSES[name]
        P = Picture(name, d, poly_labels(d, at, spec.get("parts", {}), spec.get("keep_face"),
                                         spec.get("keep_tendril")))
        plan = spec["plan"]
        P.head_at0 = at
    P.L0 = P.L.copy()
    P.wide = d
    plan(P)
    P.shut = P.finish()
    return P


# ------------------------------------------------------------------------------------------------- review
TINT = {NA: (0, 255, 120), T: (255, 255, 255), HEAD: (255, 0, 0), TEND: (60, 200, 255), FA: (255, 220, 0),
        NL: (255, 0, 255), FL: (255, 120, 0)}
SEAM_COL = {"NA": (255, 0, 255), "TNL": (0, 200, 255), "TFL": (0, 120, 255), "FA": (255, 140, 0),
            "FAFL": (255, 200, 0), "NAh": (255, 80, 160), "FAh": (255, 60, 0)}


def big(a, z, bg=(200, 205, 195)):
    im = Image.fromarray(np.repeat(np.repeat(a, z, 0), z, 1))
    can = Image.new("RGBA", im.size, bg + (255,))
    can.alpha_composite(im)
    return can.convert("RGB")


def review(P, wide, out_dir, z=6):
    """<name>_review.png: the wide picture with its labels tinted, the seams on it, the slim one (x z)."""
    L0 = P.L0
    t = wide.copy()
    for k, c in TINT.items():
        m = (L0 == k) & (wide[..., 3] > 0)
        t[m, :3] = (t[m, :3].astype(float) * 0.45 + np.array(c) * 0.55).astype(np.uint8)
    s = wide.copy()
    for e in P.log:
        for y, x, _ in e["removed"]:
            if 0 <= y < s.shape[0] and 0 <= x < s.shape[1] and s[y, x, 3]:
                s[y, x, :3] = SEAM_COL.get(e["tag"], (255, 255, 255))
    ims = [big(t, z), big(s, z), big(P.img, z)]
    W = sum(i.width for i in ims) + 40
    H = max(i.height for i in ims) + 10
    can = Image.new("RGB", (W, H), (245, 245, 240))
    x = 10
    for i in ims:
        can.paste(i, (x, H - 5 - i.height))
        x += i.width + 10
    can.save(lp(os.path.join(out_dir, f"{P.name}_review.png")))


# ------------------------------------------------------------------------------------------------- what rig_zac needs
# rig_zac.py's numbers on the wide pictures (as they were before the cut): the design's standing column, its near arm's
# last column by rows, the column between its legs, the far arm's fill starting at or right of FAR_X; where each pose
# stands (AT: dx squares off the design's middle, rows off the ground), the arm RUBBER stretches and the PARTS an
# in-between slides (pose squares)
WIDE_RIG = {"stand": 44, "leg_split": 44, "far_x": 58,
            "near_arm": {(19, 29): 25, (30, 33): 24, (34, 65): 22},
            "at": {"a_wind": (0, 0), "a_punch": (2, 0), "q_wind": (-1, 0), "q_reach": (2, 0), "q_lift": (4, 0),
                   "q_slam": (1, 0), "e_plant": (1, 0), "e_pull": (-4, 0), "e_fly": (0, 12), "e_land": (0, 0),
                   "r_crouch": (0, 0), "r_jump": (0, 10), "r_ball": (6, 22), "r_splat": (0, 0), "d_stagger": (0, 0),
                   "d_melt": (0, 0), "d_puddle": (0, 0)},
            "rubber": {"a_wind": (18, 36, (0, 41)), "a_punch": (84, 99, (0, 47))},
            "parts": {"q_reach": {"arm": [(83, 22, 130, 66)]}}}


def middle(a):
    return float(np.nonzero(a[..., 3] > 0)[1].mean())


def lowest(a):
    return int(np.nonzero((a[..., 3] > 0).any(1))[0].max()) + 1


def head_shift(P):
    """The protected squares' move (dx, dy): one for all of them (checked: each square as drawn)."""
    prot = (P.L0 == HEAD) | (P.L0 == TEND)
    ys, xs = np.nonzero(prot)
    keep = P.oy >= 0
    pos = {(int(y), int(x)): (int(nx), int(ny))
           for (ny, nx), y, x in zip(zip(*np.nonzero(keep)), P.oy[keep], P.ox[keep])}
    moves = set()
    for y, x in zip(ys, xs):
        nxy = pos.get((int(y), int(x)))
        if nxy is None:
            raise SystemExit(f"{P.name}: protected square ({x}, {y}) cut")
        nx, ny = nxy
        if not np.array_equal(P.img[ny, nx], P.wide[y, x]):
            raise SystemExit(f"{P.name}: protected square ({x}, {y}) changed")
        moves.add((nx - int(x), ny - int(y)))
    if len(moves) != 1:
        raise SystemExit(f"{P.name}: the head moved apart {sorted(moves)}")
    return moves.pop()


def new_col(P, y, x):
    """Where the wide picture's column x on row y went (from the nearest square left of it still there)."""
    for xx in range(x, -1, -1):
        w = P.where(y, xx)
        if w is not None:
            return w[0] + (x - xx)
    return 0


def rig_maps(pics):
    """slim_zac.json: rig_zac's numbers on the slim pictures."""
    D = pics["idle"]
    dshift = head_shift(D)
    face_new = (FACE[0] + dshift[0], FACE[1] + dshift[1])
    near = {}
    for (r0, r1), x in WIDE_RIG["near_arm"].items():
        for y in range(r0, r1 + 1):
            near[y] = new_col(D, y, x)
    idle = {"size": [int(D.img.shape[1]), int(D.img.shape[0])], "face": list(face_new),
            "stand": new_col(D, 64, WIDE_RIG["stand"]), "leg_split": new_col(D, 55, WIDE_RIG["leg_split"]),
            "far_x": new_col(D, 30, WIDE_RIG["far_x"]), "near_arm": {str(y): near[y] for y in sorted(near)},
            "head_shift": list(dshift)}
    mid0, mid1 = middle(D.wide), middle(D.img)
    poses = {}
    for name, P in pics.items():
        if name == "idle":
            continue
        sx, sy = head_shift(P)
        prot = (P.L0 == HEAD) | (P.L0 == TEND)
        ax0 = int(np.nonzero(prot)[1].min())               # the head's (or kept face's) first column, wide
        ay0 = int(np.nonzero(prot)[0].min())
        dx0, lift0 = WIDE_RIG["at"][name]
        # its head where it was against the design's head (the lunges, the pulls), the design's head moved with it
        rel = round(mid0 - middle(P.wide)) + dx0 + ax0 - FACE[0]
        dx1 = rel - round(mid1 - middle(P.img)) - (ax0 + sx) + face_new[0]
        # and as high over the ground: the rows taken out of the ball under its face lift it back up
        lift1 = lift0 + (lowest(P.wide) - ay0) - (lowest(P.img) - (ay0 + sy)) if lift0 else 0
        e = {"size": [int(P.img.shape[1]), int(P.img.shape[0])], "head_shift": [sx, sy], "at": [int(dx1), int(lift1)]}
        if P.head_at0:
            e["head_at"] = [P.head_at0[0] + sx, P.head_at0[1] + sy]
        if name in WIDE_RIG["rubber"]:
            x0, x1, (r0, r1) = WIDE_RIG["rubber"][name]
            ref = 20 if name == "a_wind" else 30
            e["rubber"] = [new_col(P, ref, x0), new_col(P, ref, x1), [r0, r1]]
        if name in WIDE_RIG["parts"]:
            e["parts"] = {k: [[new_col(P, 40, b[0]), b[1], b[2], b[3]] for b in boxes]
                          for k, boxes in WIDE_RIG["parts"][name].items()}
        poses[name] = e
    return {"idle": idle, "poses": poses}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review")
    ap.add_argument("--only", help="pictures (comma separated): with --review")
    a = ap.parse_args()
    names = ["idle"] + list(POSES)
    if a.only:
        names = [n for n in names if n in a.only.split(",")]
    pics = {n: make(n) for n in names}
    for n, P in pics.items():
        print(f"{n}: {P.wide.shape[1]} x {P.wide.shape[0]} -> {P.img.shape[1]} x {P.img.shape[0]}, "
              f"{len(P.log)} seams, specks shut {P.shut}, head moved {head_shift(P)}")
    if a.review:
        os.makedirs(lp(a.review), exist_ok=True)
        for P in pics.values():
            review(P, P.wide, a.review)
        return
    if a.only:
        sys.exit("--only is for --review (the maps need every picture)")
    maps = rig_maps(pics)
    files = []                                             # (path, picture or None, json data or None)
    for n, P in pics.items():
        if n == "idle":
            files.append((os.path.join(HD, "idle.png"), P.img, None))
            files.append((os.path.join(HD, "idle_4x.png"), np.repeat(np.repeat(P.img, 4, 0), 4, 1), None))
        else:
            files.append((os.path.join(HD, f"pose_{n}.png"), P.img, None))
            at = maps["poses"][n].get("head_at")
            files.append((os.path.join(HD, f"pose_{n}.json"), None, {"head_at": at}))
    files.append((MAPS, None, maps))
    bad = []
    for path, img, data in files:
        if a.check:
            if not os.path.isfile(lp(path)):
                bad.append(path)
            elif img is not None and not np.array_equal(load(path), img):
                bad.append(path)
            elif data is not None and json.load(open(lp(path), encoding="utf-8")) != json.loads(json.dumps(data)):
                bad.append(path)
            continue
        if img is not None:
            Image.fromarray(img).save(lp(path))
        else:
            with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(data, indent=1 if path == MAPS else None) + "\n")
    if a.check:
        if bad:
            sys.exit("not what tools/art/slim_zac.py makes: " + ", ".join(os.path.relpath(b, ROOT) for b in bad))
        print("slim_zac: every picture as it makes them")
        return
    print(f"written: {len(pics)} pictures and {os.path.relpath(MAPS, ROOT)}")


if __name__ == "__main__":
    main()
