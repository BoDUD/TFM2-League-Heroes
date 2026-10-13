#!/usr/bin/env python3
"""Irelia's dense frames (PPU 2): assets/source/ppu/irelia_<tag>.png, the drawn strips tools/art/ppu_hd.py puts in as
the `hd_<tag>` tags of her sheet.

    python tools/art/ppu_irelia.py                  # write the strips (after tools/art/import_native.py --hero irelia)
    python tools/art/ppu_irelia.py --check          # compare with the committed strips
    python tools/art/ppu_irelia.py --review DIR     # irelia_hd_review.gif and irelia_hd_frames.png (hd at 2x)

The user, 2026-10-12: 「刀妹参考修正的亚索用PPU吧」, then picked B of the mock (dist/irelia_packs/review/
irelia_ppu_mock.png): Codex's drafts as they are - their read-back on its own grid is 84 rows, twice the 1x sprite, the
picture the user called the best (「这个最完美」) - shown at PPU 2, so the same size in game at twice the density; head
and body in Codex's own proportions, and one face in every frame (the idle's, as the 1x frames have it). So:
  * the idle: design_v2/idle_readback.txt as it is, its three loose blades bobbing two hd pixels out of step as the 1x
    idle's (strips_irelia.BOB);
  * the run: the 1x run's way at twice the size (strips_irelia.run_frame): the idle read-back down to the hips (the
    tabard's tip and the left hip flap's kept), legs in the same eight phases at twice the lengths and widths, its
    right boot (toe forward) flat on each ankle, the body down two hd pixels as a foot lands;
  * the other actions: each frame's read-back with its own head taken away (strips_irelia.find_head) and the idle's
    head set in its place (design_v2/hd_head.txt: the idle read-back's head without the hand at her cheek, the blade
    behind it and the shoulder hook; its eyes the 1x eyes' dark cyan, the neck's shadow row skin in shade), its chin
    on the draft's chin row and its face's middle on the draft's; the lying death frames read standing and turned back;
    skill 1's blade tip cut off by the draft's crop left out (as in the 1x frame).
Each hd frame lies where its 1x frame does: a read-back square (i, j) of an action sits at hd (i + oy, j + ox) from
twice the 2:1 table's place on the canvas (the 1x frame's square (r, c) covers hd 2r..2r+1, 2c..2c+1), and is cut
2x the 1x sheet frame's size round 2x its centre (the canvas point (64, 88)), as ppu_hd.py reads it.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rigkit as K  # noqa: E402
import strips_irelia as S  # noqa: E402

PPU = 2
OUT = os.path.join(ROOT, "assets", "source", "ppu", "orig")  # the dense frames as drawn; tools/art/ppu_restyle.py makes the strips ppu_hd.py reads from them (2026-10-13)
STEM = os.path.join(ROOT, "league", "champions", "league_irelia")
CENTRE = (64, 88)                # the canvas point at the 1x sheet frames' centre (strips_irelia.PIVOT)
# the run in the idle read-back's own squares (its waist is higher than twice the hand-drawn 1x body's): the legs are
# cut from row HD_RUN_TOP down - the navy thighs in their columns (HD_THIGH_COLS), everything from HD_KNEES down - and
# the hair, the red sash beside it, the hand and the tabard hanging to row 58 stay with the upper body
HD_RUN_TOP = 47
HD_KNEES = 59
HD_THIGH_COLS = [(29, 37), (46, 50)]
HD_HIP = (46.5, 33.5, 46.5)      # the hips' row, near and far columns: the tops of the read-back's thighs
HD_LEG = (14.5, 14.5)            # thigh and shin, hip -> knee -> the ankle band
HD_ANKLE = 75.0                  # the ankle band's top row (its right boot's)
HD_FAR = 9.0                     # the far foot: this many squares right of the near one at the same phase
HD_THIGH = {False: (8, 6), True: (7, 6)}
HD_SHIN = (6, 4)                 # the greave from the knee to the ankle band
HD_SEAT = 29                     # the near thigh's back reaches this column in its first rows (under the sash)
BOOT_BOX = (75, 83, 45, 56)      # the idle read-back's right boot with its ankle band (rows, columns, ends included)
BOOT_TOP_MID = 49.5              # the band's middle column in the read-back
SKILL1_DROP = (40, 0)            # skill 1: read-back pieces from this row and column down/right that touch the crop's
                                 # bottom-right edge (the blade tip the crop cut off)


def sheet_frames():
    """The 1x sheet: {tag: [(w, h)]} in the fanim's order."""
    with open(K.lp(STEM + "#anim.fanim"), encoding="utf-8-sig") as f:
        anims = json.load(f)["anims"]
    return {t: [(int(fr["data"]["w"]), int(fr["data"]["h"])) for fr in a["frames"]]
            for t, a in anims.items() if not t.startswith("hd_")}


def cut(C2, w, h):
    """An hd frame from an hd canvas (twice the 128 canvas): PPU x the 1x frame's size round PPU x its centre."""
    r0, c0 = PPU * (CENTRE[1] - h // 2), PPU * (CENTRE[0] - w // 2)
    return C2[r0:r0 + PPU * h, c0:c0 + PPU * w]


def put(C2, T, r0, c0):
    """T's squares onto C2 with its top-left at (r0, c0), clipped to C2."""
    ys, xs = np.nonzero(T != ".")
    yy, xx = ys + r0, xs + c0
    ok = (yy >= 0) & (yy < C2.shape[0]) & (xx >= 0) & (xx < C2.shape[1])
    C2[yy[ok], xx[ok]] = T[ys[ok], xs[ok]]


# ------------------------------------------------------------------------------------------------- the head
def hd_head():
    """design_v2/hd_head.txt, its chin row (the last skin row but the neck) and its face's middle column."""
    tab = S.table(os.path.join(S.DESIGN, "hd_head.txt"))
    skin = np.isin(tab, list("qrs"))
    rows = np.nonzero(skin.any(1))[0]
    fx = np.nonzero(skin[rows[-3]:rows[-1] + 1].any(0))[0]
    return tab, int(rows[-1]), (fx.min() + fx.max()) / 2.0


def regead(L, head):
    """A draft with its own head taken away and the idle's set on its chin and face middle (strips_irelia.find_head).
    Returns the new table, padded (the head can reach past the draft's box), and the padding."""
    lab, n = ndimage.label(L != ".", np.ones((3, 3)))
    sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    bm = lab == int(np.argmax(sizes)) + 1
    found = S.find_head(L, bm)
    pad = 24
    G = np.full((L.shape[0] + 2 * pad, L.shape[1] + 2 * pad), ".", "<U1")
    G[pad:pad + L.shape[0], pad:pad + L.shape[1]] = L
    if found is None:
        return G, pad
    (y0, y1, x0, x1), fcx, hm = found
    # red and silver pieces find_head took a part of: mostly outside the head they are a blade or the body (keep them
    # whole - a blade behind the head lost its silver edge), mostly inside a head ornament (take it whole, above the chin)
    rs = np.isin(L, list("efghijklm"))
    rlab, rn = ndimage.label(rs, np.ones((3, 3)))
    hm = hm.copy()
    for i in set(np.unique(rlab[hm & rs])) - {0}:
        piece = rlab == i
        inside = (piece & hm).sum()
        if inside * 2 < piece.sum():
            hm &= ~piece
        else:
            take = piece.copy()
            take[y1 + 1:] = False
            hm |= take
    # the draft's bow at the back of the head (two red lobes, on some frames as big as the head): red pieces down to the
    # chin and up to 16 squares behind the head, not joined to a cyan gem (a blade's red, silver and gem are one)
    red = np.isin(L, list("efgh")) & ~hm
    trim = np.isin(L, list("efghijklmnop")) & ~hm          # a blade: its red, silver edge and cyan gem in one piece
    tlab, tn = ndimage.label(trim, np.ones((3, 3)))
    gem = set(np.unique(tlab[np.isin(L, list("nop")) & ~hm])) - {0}
    rlab2, rn2 = ndimage.label(red, np.ones((3, 3)))
    zone = np.zeros(L.shape, bool)
    zone[max(0, y0 - 12):y1 + 1, max(0, x0 - 16):x1 + 4] = True
    for i in range(1, rn2 + 1):
        piece = rlab2 == i
        if (piece & ~zone).any() or set(np.unique(tlab[piece])) & gem:
            continue
        hm = hm | piece
    G[pad:pad + L.shape[0], pad:pad + L.shape[1]][hm] = "."
    tab, chin, mid = head
    r0 = pad + y1 - chin
    c0 = pad + int(round(fcx - mid))
    put(G, tab, r0, c0)
    # an arm, hand or blade find_head took with the head (lying by the face): what of it lies 2 or more pixels clear of
    # the new head and joins a coloured part outside the head (a sleeve going on to the hand, a blade's other half) comes
    # back with its outline (a lying frame's outstretched hand was left floating, the blade beside her head cut)
    newm = np.zeros(G.shape, bool)
    newm[r0:r0 + tab.shape[0], c0:c0 + tab.shape[1]] = tab != "."
    away = ~ndimage.binary_dilation(newm, iterations=2)[pad:pad + L.shape[0], pad:pad + L.shape[1]]
    colour = np.isin(L, list("efghijklmnopqrs"))
    cand = hm & colour & away
    clab, cn = ndimage.label(cand, np.ones((3, 3)))
    body_col = ndimage.binary_dilation(colour & ~hm, np.ones((3, 3)))
    back = np.isin(clab, list(set(np.unique(clab[body_col & cand])) - {0}))
    back |= ndimage.binary_dilation(back, np.ones((3, 3))) & (L == "0") & hm & away
    G[pad:pad + L.shape[0], pad:pad + L.shape[1]][back] = L[back]
    # the draft's own head's ornaments, face and crest round the new head (above its chin, where it does not cover
    # them): gone - its hair stays (a second silver clip showed behind the new head's)
    newm = np.zeros(G.shape, bool)
    newm[r0:r0 + tab.shape[0], c0:c0 + tab.shape[1]] = tab != "."
    oldm = np.zeros(G.shape, bool)
    oldm[pad:pad + L.shape[0], pad:pad + L.shape[1]] = ndimage.binary_dilation(hm, np.ones((3, 3)), iterations=4)
    oldm[r0 + chin:] = False
    G[oldm & ~newm & np.isin(G, list("efghijklmnopqrs"))] = "."
    for _ in range(6):                  # their outline with nothing coloured left beside it: gone too
        col = (G != ".") & (G != "0")
        n4 = np.zeros(G.shape, int)
        n4[1:] += col[:-1]
        n4[:-1] += col[1:]
        n4[:, 1:] += col[:, :-1]
        n4[:, :-1] += col[:, 1:]
        orphan = oldm & ~newm & (G == "0") & (n4 == 0)
        if not orphan.any():
            break
        G[orphan] = "."
    near = np.zeros(G.shape, bool)
    near[max(0, r0 - 6):r0 + tab.shape[0] + 6, max(0, c0 - 6):c0 + tab.shape[1] + 6] = True
    lab, n = ndimage.label(G != ".", np.ones((3, 3)))
    for i in range(1, n + 1):
        m = lab == i
        if m.sum() <= 15 and (m & near).sum() == m.sum():
            G[m] = "."
    return G, pad


# ------------------------------------------------------------------------------------------------- the idle and run
def idle_place(built_idle):
    """Where the idle read-back sits on the hd canvas: read-back (i, j) -> hd (2 (9 + dy) + i, 2 (10 + dx) + j), dy and
    dx the 1x idle's place() shift (body_idle square (r, c) is read-back (2r, 2c); strips_irelia.BODY_AT)."""
    body = S.table(os.path.join(S.DESIGN, "body_idle.txt"))
    front, idle_h = S.heads()
    found = S.idle_place()
    G = S.idle_frame(body, idle_h, found, 0)
    ys, xs = np.nonzero(G != ".")
    feet = np.nonzero((G[ys.max() - 2:ys.max() + 1] != ".").any(0))[0]
    mid = (feet.min() + feet.max()) / 2.0
    dy, dx = S.SOLES - ys.max(), S.PIVOT[0] - int(round(mid))
    return PPU * (S.BODY_AT[0] + dy), PPU * (S.BODY_AT[1] + dx)


def blades_and_body(rb):
    lab, n = ndimage.label(rb != ".", np.ones((3, 3)))
    sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    body_id = int(np.argmax(sizes)) + 1
    ctr = np.array([rb.shape[0] / 2.0, rb.shape[1] / 2.0])
    pieces = {}
    for i in range(1, n + 1):
        if i == body_id:
            continue
        ys, xs = np.nonzero(lab == i)
        cy, cx = ys.mean(), xs.mean()
        name = ("upper_left" if cy < ctr[0] * 0.8 else "lower_left") if cx < ctr[1] else "lower_right"
        pieces[name] = lab == i
    return lab == body_id, pieces


def idle_hd(rb, k):
    body, pieces = blades_and_body(rb)
    T = np.full(rb.shape, ".", "<U1")
    T[body] = rb[body]
    out = np.full((rb.shape[0] + 8, rb.shape[1]), ".", "<U1")
    for name, m in pieces.items():                  # the blades behind, bobbing as the 1x idle's
        b = PPU * S.BOB[name][k]
        ys, xs = np.nonzero(m)
        out[ys + 4 + b, xs] = rb[ys, xs]
    m = T != "."
    out[4:4 + T.shape[0]][m] = T[m]
    return out, 4


def hd_leg(phase, far, step, boot):
    """strips_irelia.run_leg at twice the size: {(row, col): letter} in read-back squares."""
    hy, hx = HD_HIP[0] + step, HD_HIP[2] if far else HD_HIP[1]
    ax, lift = S.RUN_PHASES[phase]
    ax, ay = HD_HIP[1] + (HD_FAR if far else 0.0) + PPU * ax, HD_ANKLE - PPU * lift
    lt, ls = HD_LEG
    k1, _ = K.elbow((hx, hy), (ax, ay), lt, ls, bend=-1)
    k2, _ = K.elbow((hx, hy), (ax, ay), lt, ls, bend=1)
    kx, ky = k1 if k1[0] >= k2[0] else k2
    cells = {}
    for p0, p1, (w0, w1), (hi, lit, dark) in (((hx, hy), (kx, ky), HD_THIGH[far], ("c", "b", "a")),
                                             ((kx, ky), (ax, ay), HD_SHIN, ("h", "g", "f"))):
        n = int(max(abs(p1[0] - p0[0]), abs(p1[1] - p0[1])) * 4) + 1
        steep = abs(p1[1] - p0[1]) >= abs(p1[0] - p0[0])
        for i in range(n + 1):
            x = p0[0] + (p1[0] - p0[0]) * i / n
            y = p0[1] + (p1[1] - p0[1]) * i / n
            xi, yi = int(math.floor(x)), int(math.floor(y))
            w = int(round(w0 + (w1 - w0) * i / n))
            for j in range(w):
                ch = hi if j == w - 1 else (dark if j < 2 else lit)       # lit from the front (right), shaded behind
                cells.setdefault((yi, xi - (w - 2) + j) if steep else (yi - (w - 2) + j, xi), ch)
    if not far:
        for r in range(int(math.floor(hy)) + 1, int(math.floor(hy)) + 6):
            xs = [c for (rr, c) in cells if rr == r]
            for c in range(HD_SEAT, min(xs) if xs else HD_SEAT):
                cells[(r, c)] = "a"
    kxi, kyi = int(math.floor(kx)), int(math.floor(ky))
    guard = [".lll.", "lmmkk", "kkkji", ".iii."]    # the knee guard, silver, lit from the top
    for i, row in enumerate(guard):
        for j, ch in enumerate(row):
            if ch != ".":
                cells[(kyi - 1 + i, kxi - 2 + j)] = ch
    axi, ayi = int(math.floor(ax)), int(math.floor(ay))
    bt, mid = boot
    for i in range(bt.shape[0]):
        for j in range(bt.shape[1]):
            if bt[i, j] != ".":
                cells[(ayi + i, axi - int(round(mid)) + j)] = bt[i, j]
    return cells


def run_hd(rb, k):
    """Run frame k at twice the size, in read-back squares (the idle read-back's place)."""
    step = PPU * S.RUN_STEP[k]
    body, pieces = blades_and_body(rb)
    up = np.where(body, rb, ".")
    legs_m = np.zeros(up.shape, bool)
    legs_m[HD_KNEES:] = True
    for c0, c1 in HD_THIGH_COLS:
        legs_m[HD_RUN_TOP:HD_KNEES, c0:c1 + 1] |= np.isin(up[HD_RUN_TOP:HD_KNEES, c0:c1 + 1], list("abcd0"))
    kept = (up != ".") & ~legs_m
    near = ndimage.binary_dilation(kept & (up != "0"), np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]))
    legs_m &= ~(near & (up == "0") & ~np.isin(np.arange(up.shape[0])[:, None] >= HD_KNEES, [True]))
    up[legs_m] = "."
    r0, r1, c0, c1 = BOOT_BOX
    bt = rb[r0:r1 + 1, c0:c1 + 1].copy()
    bt[bt == "0"] = "."                              # its own outline: the leg's ring outlines it
    boot = (bt, BOOT_TOP_MID - c0)
    pad = 8
    G = np.full((rb.shape[0] + 2 * pad, rb.shape[1] + 2 * pad), ".", "<U1")
    for name, m in pieces.items():
        ys, xs = np.nonzero(m)
        G[ys + pad + PPU * S.BOB[name][k] + step, xs + pad] = rb[ys, xs]
    legs = np.full(G.shape, ".", "<U1")
    for phase, far in (((k + 4) % 8, True), (k, False)):
        cells = hd_leg(phase, far, step, boot)
        for y, x in cells:
            for dy, dx in S.N4:
                if (y + dy, x + dx) not in cells:
                    legs[y + dy + pad, x + dx + pad] = "0"
        for (y, x), ch in cells.items():
            legs[y + pad, x + pad] = ch
    for _ in range(2):
        op = legs != "."
        n4 = np.zeros(G.shape, int)
        n4[1:] += op[:-1]
        n4[:-1] += op[1:]
        n4[:, 1:] += op[:, :-1]
        n4[:, :-1] += op[:, 1:]
        legs[~op & (n4 >= 3)] = "0"
    G = np.where(legs != ".", legs, G)
    m = up != "."
    G[pad + step:pad + step + up.shape[0], pad:pad + up.shape[1]][m] = up[m]
    lab, n = ndimage.label(G == ".")
    for i in range(1, n + 1):
        hole = lab == i
        ys, xs = np.nonzero(hole)
        if ys.min() >= pad + HD_RUN_TOP and hole.sum() <= 24 and xs.min() > 0 and xs.max() < G.shape[1] - 1 \
                and ys.max() < G.shape[0] - 1:
            G[hole] = "a"
    return G, pad


# ------------------------------------------------------------------------------------------------- the actions
def action_hd(tag, k, L, fr, head):
    """An action's hd canvas (twice the 128 canvas)."""
    lying = tag == "dead" and k >= 4
    front, _ = S.heads()
    G1, (r0, c0, H, W) = S.action_frame(L, front, lying=lying)
    x0, x1 = fr["bbox"][0], fr["bbox"][2]
    px = c0 + (fr["pivot"][0] - x0) / float(x1 - x0) * W
    ys, xs = np.nonzero(G1 != ".")
    dyc, dxc = S.SOLES - ys.max(), S.PIVOT[0] - int(round(px))
    D = np.rot90(L, 1) if lying else L
    oy, ox = S.best_phase(D)
    if tag == "skill" and k == 1:
        D = drop_cut_blade(D)
    T, tp = regead(D, head)
    # the standing 2:1 table G' (pad 24) holds read-back (i, j) at hd (i + oy + 48, j + ox + 48)
    Gs_shape = (G1.shape[1], G1.shape[0]) if lying else G1.shape
    hd = np.full((PPU * Gs_shape[0], PPU * Gs_shape[1]), ".", "<U1")
    put(hd, T, oy + 48 - tp, ox + 48 - tp)
    if lying:
        hd = np.rot90(hd, -1)
    C2 = np.full((PPU * 128, PPU * 128), ".", "<U1")
    put(C2, hd, PPU * dyc, PPU * dxc)
    return C2


def tidy(F):
    """What ppu_hd.strays calls leftovers in a dense frame (亚索's 「像素缺失了啊」「别留多余的像素」): a pocket of ground
    of up to 40 pixels shut in by the figure (between hair strands, an arm and the body) takes the commonest colour
    round it; a pixel sticking out alone (6 or more of its 8 neighbours clear: a 1-pixel spur on a tip) goes, until none is left."""
    F = F.copy()
    op = F != "."
    holes = ndimage.binary_fill_holes(op) & ~op
    lab, n = ndimage.label(holes)
    for i in range(1, n + 1):
        m = lab == i
        if m.sum() > 40:
            continue
        ring = ndimage.binary_dilation(m) & ~m
        vals, cnt = np.unique(F[ring], return_counts=True)
        F[m] = vals[np.argmax(cnt)]
    for _ in range(40):
        op = F != "."
        p = np.pad(op, 1)
        clear = sum((~p[1 + a:1 + a + op.shape[0], 1 + c:1 + c + op.shape[1]]).astype(int)
                    for a in (-1, 0, 1) for c in (-1, 0, 1) if a or c)
        spur = op & (clear >= 6)
        if not spur.any():
            break
        F[spur] = "."
    return F


def loose_out(C2, most=39):
    """Loose bits under 40 squares (an outline crumb of a blade the draft's crop cut, a dot left of a head, the hand of
    lying death frame 5 whose forearm runs under the new head): gone - ppu_hd.strays calls a part under 40 pixels a
    speck."""
    lab, n = ndimage.label(C2 != ".", np.ones((3, 3)))
    sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    for i, sz in enumerate(sizes, 1):
        if sz <= most:
            C2[lab == i] = "."
    return C2


def drop_cut_blade(D):
    lab, n = ndimage.label(D != ".", np.ones((3, 3)))
    out = D.copy()
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if ys.max() == D.shape[0] - 1 and xs.max() == D.shape[1] - 1 and ys.min() >= SKILL1_DROP[0]:
            out[lab == i] = "."
    return out


# ------------------------------------------------------------------------------------------------- build
def build():
    sizes = sheet_frames()
    rb = S.readbacks()
    idle_rb = S.table(os.path.join(S.DESIGN, "idle_readback.txt"))
    head = hd_head()
    R0, C0 = idle_place(None)
    out = {}
    for tag in S.TAGS:
        frames = []
        for k, (w, h) in enumerate(sizes[tag]):
            C2 = np.full((PPU * 128, PPU * 128), ".", "<U1")
            if tag == "idle":
                T, p = idle_hd(idle_rb, k)
                put(C2, T, R0 - p, C0)
            elif tag == "run":
                T, p = run_hd(idle_rb, k)
                put(C2, T, R0 - p, C0 - p)
            else:
                L, fr = rb[tag][k]
                C2 = action_hd(tag, k, L, fr, head)
            frames.append(tidy(cut(loose_out(C2), w, h)))
        out[tag] = frames
    return out


def strip(frames):
    W = sum(f.shape[1] + 1 for f in frames) - 1
    H = max(f.shape[0] for f in frames)
    a = np.zeros((H, W, 4), np.uint8)
    x = 0
    for f in frames:
        a[:f.shape[0], x:x + f.shape[1]] = S.rgba(f)
        x += f.shape[1] + 1
    return a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review")
    a = ap.parse_args()
    built = build()
    if a.review:
        review(built, a.review)
        return
    os.makedirs(K.lp(OUT), exist_ok=True)
    bad = []
    for tag, frames in built.items():
        path = os.path.join(OUT, f"irelia_{tag}.png")
        s = strip(frames)
        if a.check:
            if not (os.path.exists(K.lp(path)) and np.array_equal(np.asarray(Image.open(K.lp(path)).convert("RGBA")), s)):
                bad.append(tag)
        else:
            Image.fromarray(s).save(K.lp(path))
    print("differs:", bad or "nothing") if a.check else print("wrote", ", ".join(f"{t} {len(f)}" for t, f in built.items()))


def review(built, out_dir, z=2):
    os.makedirs(K.lp(out_dir), exist_ok=True)
    rows = [(t, built[t]) for t in S.TAGS]
    W = max(sum(f.shape[1] * z + 6 for f in frs) for _, frs in rows) + 70
    H = sum(max(f.shape[0] for f in frs) * z + 8 for _, frs in rows)
    img = Image.new("RGB", (W, H), (40, 40, 40))
    d = ImageDraw.Draw(img)
    y = 0
    for t, frs in rows:
        d.text((4, y + 4), t, fill=(255, 255, 255))
        x = 70
        for f in frs:
            tile = Image.new("RGBA", (f.shape[1] * z, f.shape[0] * z), (110, 120, 108, 255))
            tile.alpha_composite(Image.fromarray(S.rgba(f)).resize((f.shape[1] * z, f.shape[0] * z), Image.NEAREST))
            img.paste(tile.convert("RGB"), (x, y))
            x += f.shape[1] * z + 6
        y += max(f.shape[0] for f in frs) * z + 8
    img.save(K.lp(os.path.join(out_dir, "irelia_hd_frames.png")))
    print("wrote", os.path.join(out_dir, "irelia_hd_frames.png"))


if __name__ == "__main__":
    main()
