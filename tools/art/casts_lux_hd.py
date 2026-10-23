#!/usr/bin/env python3
"""Lux's cast frames (attack, Light Binding, Lucent Singularity, Final Spark) from Codex's whole-frame redraw
(assets/source/lux/hd/casts: tools/art/pack_lux_actions.py's pack, delivered 2026-10-23; the user:
「Codex 重画施法动作」, then 「codex已经交付 有问题的地方你帮忙修复吧」), mended onto the design (rig_lux_hd.py takes them):

1. read square for square (6-px blocks, phase x 0 / y 4; the ground under row 145);
2. Codex's staff taken off (it bends, its length and end pieces change frame to frame): the squares of staff colours
   along its line (SPEC gem -> grips / via -> end, CORRIDOR across) and round its end pieces, her gloves left; the
   body under it filled from both sides of the line, the bits left apart from her dropped;
3. brought to the design's size (each new square the Lab mean of the old ones it covers, snapped to the design's
   colours, the outline where it covers enough of it - design_lux_hd's read): Codex scaled each sheet of two frames on
   its own, so a sheet with a frame standing upright takes the scale that sets her near eye as high over the ground as
   the design's, the others SCALE_ALL;
4. the design's head (rows above HEAD_ROWS, staff apart) set on, its near eye on Codex's near eye (the left of a level
   pair of irises with skin round them), Codex's own head under it cleared (her sleeves and gloves beside it kept, and
   kept over it where SPEC over_head says her arm crosses in front);
5. the design's staff (staff_lux.Staffs: twelve directions, every one the same length) through her grip(s), in the
   direction nearest Codex's, slid along its line so the crescent head lands nearest Codex's (a thrown staff: at
   Codex's crescent), in front of her or behind (SPEC z), never over her face, her gloves over it; a bit of it left
   over past what hides it dropped;
6. onto the rig's canvas: soles on the design's ground, each tag's first frame between the design's boots, then her
   rear boot planted (offsets()).

    python tools/art/casts_lux_hd.py [--review DIR]     # the frames (and the bare ones) as npz in DIR
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage
from skimage import color

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import design_jinx_hd as JD  # noqa: E402
import design_lux_hd as DL  # noqa: E402
import staff_lux  # noqa: E402

SRC = os.path.join(DL.HD, "casts")
TAGS = ["attack", "skill", "skill2", "ult"]
SQ, PHASE_X, PHASE_Y = 6, 0, 4
CELL = (768, 1024)
CX, GY = 64, 145                 # Codex's standing column, the row under its soles
SCALE_ALL = 0.91
SCALE = SCALE_ALL               # the frame being mended
O = DL.OUTLINE


def hexes(a):
    return np.array([["%02X%02X%02X" % tuple(int(v) for v in a[y, x, :3]) for x in range(a.shape[1])]
                     for y in range(a.shape[0])])


IRIS = {"127FE0", "0255E0", "1C2F70", "4AB8F2"}
SKIN = {"FBD0A9", "EFA07E", "C1614C", "C33B3A"}
GOLD = {"F4B33C", "FACA40", "FCCF59", "E4992D", "CD7E25", "BB933C", "AE6120", "FDF084", "EBC880", "F0D7A9",
        "8A401B", "AD834D", "6B401D", "5A2914"}
CREAM = {"FBF9F7", "F0D7A9", "EBC880", "FDF084", "DACECD"}
BLUE = {"127FE0", "0255E0", "4AB8F2", "ADE6FD", "1C2F70", "A99CAA", "5E5473", "806C72"}
GLOVE = {"FBF9F7", "DACECD", "A99CAA", "806C72", "5E5473", "AB9085"}
OUT_HEX = "%02X%02X%02X" % O
STAFFISH = GOLD | CREAM | BLUE | {OUT_HEX}

# ------------------------------------------------------------------------------------------------ the frames' staffs
# per frame, Codex's squares: its staff's crescent (gem) and the far end of its line (end), her hand(s) on it (grips;
# none: thrown), the new staff in front of her ("front") or behind ("back"), its direction (deg: the crescent head's,
# counter-clockwise from her front; None: Codex's own snapped), extra: squares to keep or to take with the staff
SPEC = json.load(open(os.path.join(SRC, "spec.json"), encoding="utf-8")) if os.path.exists(
    os.path.join(SRC, "spec.json")) else {}
CORRIDOR = 1.6                   # squares either side of Codex's line taken with the staff
ENDS_R = 10.0                    # round each end piece


def read():
    sheets = json.load(open(os.path.join(SRC, "sheets.json"), encoding="utf-8"))["sheets"]
    out = {}
    for sh in sheets:
        a = np.asarray(Image.open(DL.lp(os.path.join(SRC, sh["name"] + ".png"))).convert("RGBA"))
        for k, fno in enumerate(sh["frames"]):
            cell = a[:, k * CELL[0]:(k + 1) * CELL[0]]
            g = cell[PHASE_Y:PHASE_Y + ((CELL[1] - PHASE_Y) // SQ) * SQ:SQ,
                     PHASE_X:PHASE_X + (CELL[0] // SQ) * SQ:SQ].copy()
            if g[..., 3].any():
                out[f"{sh['tag']}_{fno}"] = g
    return out


def order(names):
    return sorted(names, key=lambda n: (["attack", "skill", "skill2", "ult"].index(n.rsplit("_", 1)[0]),
                                        int(n.rsplit("_", 1)[1])))


# ------------------------------------------------------------------------------------------------ 2. the old staff off
def staff_mask(f, s):
    """Codex's staff squares: staff colours within CORRIDOR of its line - gem, through the grips (Codex bends it at
    her hand), to the end - and within ENDS_R of the gem / the end, the grips' gloves apart. -> (mask, the line's
    unit (gem -> end), its normal)."""
    H, W = f.shape[:2]
    hx = hexes(f)
    op = f[..., 3] > 0
    g, e = np.array(s["gem"], float), np.array(s["end"], float)
    u = (e - g) / np.hypot(*(e - g))
    n = np.array((-u[1], u[0]))
    mid = [np.array(p, float) for p in s.get("grips", []) + s.get("via", [])]
    pts = [g] + sorted(mid, key=lambda p: float((p - g) @ u)) + [e]
    yy, xx = np.mgrid[0:H, 0:W]
    P = np.stack([xx + 0.5, yy + 0.5], -1)
    dist = np.full((H, W), 1e9)
    for a, b in zip(pts[:-1], pts[1:]):
        v = b - a
        L2 = float(v @ v)
        t = np.clip(((P - a) @ v) / max(L2, 1e-9), 0, 1)
        q = a + t[..., None] * v
        dist = np.minimum(dist, np.hypot(*(P - q).transpose(2, 0, 1)))
    col = np.isin(hx, list(STAFFISH)) & op
    m = col & (dist <= s.get("corridor", CORRIDOR))
    for c, r in ((g, s.get("gem_r", ENDS_R)), (e, s.get("end_r", ENDS_R if s.get("end_piece", True) else 0))):
        if r:
            m |= col & (np.hypot(xx + 0.5 - c[0], yy + 0.5 - c[1]) <= r)
    for cx, cy, r in s.get("pieces", []):           # Codex's end piece showing past her body (its line hidden)
        m |= col & (np.hypot(xx + 0.5 - cx, yy + 0.5 - cy) <= r)
    for gx, gy in s.get("grips", []) + s.get("hands", []):
        near = np.hypot(xx + 0.5 - gx, yy + 0.5 - gy) <= s.get("grip_r", 2.6)
        m &= ~(near & np.isin(hx, list(GLOVE)))
    for x0, y0, x1, y1 in s.get("keep", []):
        m[y0:y1 + 1, x0:x1 + 1] = False
    for x0, y0, x1, y1 in s.get("take", []):
        m[y0:y1 + 1, x0:x1 + 1] |= op[y0:y1 + 1, x0:x1 + 1]
    return m, u, n


def unstaff(f, s):
    """f with Codex's staff off, the body under it filled from both sides of the line."""
    m, u, n = staff_mask(f, s)
    out = f.copy()
    out[m] = 0
    body = (f[..., 3] > 0) & ~m
    H, W = body.shape
    filled = np.zeros_like(m)
    for y, x in zip(*np.nonzero(m)):
        got = []
        for sgn in (1, -1):
            for k in range(1, 5):
                qx = int(math.floor(x + 0.5 + sgn * n[0] * k))
                qy = int(math.floor(y + 0.5 + sgn * n[1] * k))
                if not (0 <= qx < W and 0 <= qy < H):
                    break
                if body[qy, qx]:
                    got.append((k, qy, qx))
                    break
                if not m[qy, qx]:
                    break
        if len(got) == 2:
            k, qy, qx = min(got)
            out[y, x] = f[qy, qx]
            filled[y, x] = True
    # what is left inside the body: the commonest of its body neighbours, a few passes
    for _ in range(3):
        op = out[..., 3] > 0
        todo = m & ~filled & ~op
        for y, x in zip(*np.nonzero(todo)):
            win = [(yy, xx) for yy in range(y - 1, y + 2) for xx in range(x - 1, x + 2)
                   if (yy, xx) != (y, x) and 0 <= yy < H and 0 <= xx < W and op[yy, xx]
                   and not (m[yy, xx] and not filled[yy, xx])]
            if len(win) >= 6:
                cols = [tuple(out[yy, xx]) for yy, xx in win]
                out[y, x] = max(set(cols), key=cols.count)
                filled[y, x] = True
    return detached_off(out, m), m


def detached_off(f, m, most=60):
    """Pieces the staff's removal left apart from her (end pieces' rims, the shaft past the corridor): pieces of fewer
    than `most` squares not joined to the biggest, if they lie within 4 of what was taken."""
    op = f[..., 3] > 0
    lbl, k = ndimage.label(op, structure=np.ones((3, 3)))
    if k <= 1:
        return f
    sizes = ndimage.sum(op, lbl, range(1, k + 1))
    big = 1 + int(np.argmax(sizes))
    near = ndimage.binary_dilation(m, iterations=6)
    out = f.copy()
    for j, n in enumerate(sizes, 1):
        if j != big and n < most and (near & (lbl == j)).any():
            out[lbl == j] = 0
    return out


# -------------------------------------------------------------------------------------------- 3. to the design's size
def palette():
    d = staff_lux.design()
    return np.unique(d[d[..., 3] > 0][:, :3], axis=0)


def cover(n, centre, scale, count):
    w = np.zeros((count, n))
    for t in range(count):
        a = centre + (t - centre) / scale
        b = centre + (t + 1 - centre) / scale
        for s in range(int(np.floor(a)), int(np.ceil(b))):
            if 0 <= s < n:
                w[t, s] = max(0.0, min(b, s + 1) - max(a, s))
    return w


def rescale(f, pal):
    H, W = f.shape[:2]
    plab = color.rgb2lab(pal[None].astype(float) / 255.0)[0]
    op = (f[..., 3] > 0).astype(float)
    isout = (op > 0) & (np.abs(f[..., :3].astype(int) - np.array(O)).sum(-1) < 30)
    lab = color.rgb2lab(f[..., :3] / 255.0)
    wy, wx = cover(H, GY, SCALE, H), cover(W, CX, SCALE, W)
    cov = wy @ op @ wx.T
    oc = wy @ isout.astype(float) @ wx.T
    inner = op * (1 - isout)
    wi = wy @ inner @ wx.T
    area = wy.sum(1)[:, None] * wx.sum(1)[None, :]
    mean = np.stack([wy @ (lab[..., c] * inner) @ wx.T for c in range(3)], -1) / np.maximum(wi, 1e-9)[..., None]
    k = np.argmin(((mean[..., None, :] - plab[None, None]) ** 2).sum(-1), -1)
    keep = (cov >= 0.5 * np.maximum(area, 1e-9)) & (area > 0)
    g = np.zeros((H, W, 4), np.uint8)
    g[keep, :3] = pal[k[keep]]
    g[keep & ((oc >= DL.OUTLINE_SHARE * cov) | (wi < 0.2 * area)), :3] = O
    g[keep, 3] = 255
    return JD.clean(g)


def scaled(p):
    """A point in Codex's squares (continuous) on the scaled grid."""
    return np.array((CX + (p[0] - CX) * SCALE, GY + (p[1] - GY) * SCALE))


# ------------------------------------------------------------------------------------------------ 4. the head
HEAD_ROWS = 31
DEYE = (35.0, 22.5)              # the design's near eye: the middle of its iris squares


def eye_pair(f, s):
    """Codex's near eye (continuous, its squares): iris clusters with skin round them, the left of a pair level and
    4-8 apart; s["eye"] overrides."""
    if "eye" in s:
        return np.array(s["eye"], float)
    hx = hexes(f)
    m = np.isin(hx, list(IRIS)) & (f[..., 3] > 0)
    m[GY - 20:] = False
    lbl, k = ndimage.label(m, structure=np.ones((3, 3)))
    cl = []
    for j in range(1, k + 1):
        yy, xx = np.nonzero(lbl == j)
        if xx.max() - xx.min() > 3:              # the two eyes run together: the left three columns
            sel = xx <= xx.min() + 2
            yy, xx = yy[sel], xx[sel]
        win = hx[max(0, yy.min() - 3):yy.max() + 4, max(0, xx.min() - 3):xx.max() + 4]
        sk = int(np.isin(win, list(SKIN)).sum())
        if sk >= 18:
            cl.append((xx.mean() + 0.5, yy.mean() + 0.5, len(xx), sk))
    pairs = [(a, b) for a in cl for b in cl if 3.5 <= b[0] - a[0] <= 8 and abs(b[1] - a[1]) <= 2.5]
    if pairs:
        a, _ = max(pairs, key=lambda p: p[0][3] + p[1][3])
        return np.array(a[:2])
    if cl:
        a = max(cl, key=lambda c: c[3])
        return np.array(a[:2])
    raise SystemExit("no eye found")


def head_piece(d):
    band, head_p, end_p = DL.staff_masks(d)
    h = d.copy()
    h[HEAD_ROWS:] = 0
    h[band | head_p | end_p] = 0
    return h


ARM = {"141637", "1C2655", "32242F", "FBF9F7", "DACECD", "A99CAA", "806C72", "5E5473"}   # sleeves, gloves


def set_head(g, head, eye_s, s):
    """The design's head on g, its near eye on eye_s (scaled grid); Codex's head under it (the head grown by `clear`
    squares, above the chin; its sleeves and gloves beside the head kept) cleared first. -> (g, (dx, dy))."""
    dx = int(round(eye_s[0] - DEYE[0])) + s.get("head_dx", 0)
    dy = int(round(eye_s[1] - DEYE[1])) + s.get("head_dy", 0)
    hm = head[..., 3] > 0
    grown = ndimage.binary_dilation(hm, iterations=s.get("clear", 1))
    H, W = g.shape[:2]
    hx = hexes(g)
    out = g.copy()
    for y, x in zip(*np.nonzero(grown)):
        Y, X = y + dy, x + dx
        if 0 <= Y < H and 0 <= X < W and y < HEAD_ROWS - 1 and (hm[y, x] or hx[Y, X] not in ARM):
            out[Y, X] = 0
    for y, x in zip(*np.nonzero(hm)):
        Y, X = y + dy, x + dx
        if 0 <= Y < H and 0 <= X < W:
            out[Y, X] = head[y, x]
    # her arm in front of the head (scaled squares, boxes x0, y0, x1, y1): Codex's sleeve and glove squares there,
    # and the outline squares beside them, stay on top
    for x0, y0, x1, y1 in s.get("over_head", []):
        box = g[y0:y1 + 1, x0:x1 + 1]
        arm = np.isin(hx[y0:y1 + 1, x0:x1 + 1], list(ARM)) & (box[..., 3] > 0)
        rim = ndimage.binary_dilation(arm) & (hx[y0:y1 + 1, x0:x1 + 1] == OUT_HEX) & (box[..., 3] > 0)
        top = out[y0:y1 + 1, x0:x1 + 1]
        top[arm | rim] = box[arm | rim]
    return out, (dx, dy)


# ------------------------------------------------------------------------------------------------ 5. the new staff
def nearest_deg(u_head):
    a = math.degrees(math.atan2(-u_head[1], u_head[0])) % 360
    return int(round(a / 30.0) * 30) % 360


def set_staff(g, staffs, s, gloves, head=None):
    """The design's staff on g (scaled grid) for spec s; gloves: squares kept over it. -> (g, info)."""
    gem = scaled(s["gem"])
    end = scaled(s["end"])
    uh = (gem - end) / np.hypot(*(gem - end))              # toward the crescent
    deg = s.get("deg", nearest_deg(uh))
    img, M, hu = staffs.at(deg)
    hu = np.asarray(hu, float)
    ys, xs = np.nonzero(img[..., 3] > 0)
    # the crescent's gem in the staff picture: the blue squares' middle
    hxi = hexes(img)
    bl = np.isin(hxi, ["127FE0", "0255E0", "4AB8F2", "ADE6FD"])
    by, bx = np.nonzero(bl)
    gem_img = np.array((bx.mean() + 0.5, by.mean() + 0.5))
    grips = [scaled(p) for p in s.get("grips", [])]
    if grips:
        c = np.mean(grips, 0)
        # the line through the grip(s); along it the gem nearest Codex's
        along = float((gem - c) @ hu)
        off = float((gem_img - np.asarray(M)) @ hu)
        Mpos = c + hu * (along - off)
        Mpos += hu * s.get("slide", 0.0)
    else:
        Mpos = gem - (gem_img - np.asarray(M)) + hu * s.get("slide", 0.0)
    ox = int(round(Mpos[0] - M[0]))
    oy = int(round(Mpos[1] - M[1]))
    out = g.copy()
    H, W = g.shape[:2]
    front = s.get("z", "front") == "front"
    drawn = np.zeros((H, W), bool)
    for y, x in zip(ys, xs):
        Y, X = y + oy, x + ox
        if not (0 <= Y < H and 0 <= X < W):
            continue
        if gloves[Y, X] or (head is not None and head[Y, X] and not s.get("staff_over_head")):
            continue
        if front or out[Y, X, 3] == 0:
            out[Y, X] = img[y, x]
            drawn[Y, X] = True
    # a bit of the staff left over past what hides it (the end's tip over her head): off
    lbl, k = ndimage.label(drawn | ndimage.binary_dilation(gloves), structure=np.ones((3, 3)))   # (her hands join it)
    if k > 1:
        sizes = ndimage.sum(drawn, lbl, range(1, k + 1))
        for j, n in enumerate(sizes, 1):
            if 0 < n < s.get("stub", 30):
                m = (lbl == j) & drawn
                out[m] = g[m]
    return out, dict(deg=deg, at=(ox, oy))


def glove_mask(g, s):
    """Her gloves on the staff (scaled grid): glove-coloured squares within 2.5 of a grip."""
    hx = hexes(g)
    H, W = g.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    m = np.zeros((H, W), bool)
    for p in s.get("grips", []):
        q = scaled(p)
        m |= (np.hypot(xx + 0.5 - q[0], yy + 0.5 - q[1]) <= s.get("glove_r", 2.5)) & np.isin(hx, list(GLOVE))
    return m


# ------------------------------------------------------------------------------------------------ 6. tidy, place
def drop_specks(g, keep_min=4):
    """Pieces of fewer than keep_min squares (8-connected) off."""
    op = g[..., 3] > 0
    lbl, k = ndimage.label(op, structure=np.ones((3, 3)))
    sizes = ndimage.sum(op, lbl, range(1, k + 1))
    out = g.copy()
    for j, n in enumerate(sizes, 1):
        if n < keep_min:
            out[lbl == j] = 0
    return out


def build(review=None):
    frames = read()
    pal = palette()
    d = staff_lux.design()
    head = head_piece(d)
    staffs = staff_lux.Staffs(d)
    out, info = {}, {}
    steps = {}
    # Codex scaled each of its sheets (two frames drawn together) on its own: a sheet with a frame standing upright
    # (SPEC "stand": her near eye as high over the ground as the design's) takes that frame's scale, the rest SCALE_ALL
    scales = {}
    for sh in json.load(open(os.path.join(SRC, "sheets.json"), encoding="utf-8"))["sheets"]:
        names = [f"{sh['tag']}_{k}" for k in sh["frames"]]
        st = [(DESIGN_GROUND - DEYE[1]) / (GY - eye_pair(frames[n], SPEC[n])[1]) for n in names if SPEC[n].get("stand")]
        for n in names:
            scales[n] = st[0] if st else SCALE_ALL
    for name in order(frames):
        f = frames[name]
        s = SPEC.get(name)
        if s is None:
            raise SystemExit(f"no spec for {name}")
        eye = eye_pair(f, s)
        global SCALE
        SCALE = scales[name]
        bare, m = unstaff(f, s)
        g = rescale(bare, pal)
        g, hd = set_head(g, head, scaled(eye), s)
        hm = np.zeros(g.shape[:2], bool)
        ys, xs = np.nonzero(head[..., 3] > 0)
        Y, X = ys + hd[1], xs + hd[0]
        ok = (Y >= 0) & (Y < hm.shape[0]) & (X >= 0) & (X < hm.shape[1])
        hm[Y[ok], X[ok]] = True
        gl = glove_mask(g, s)
        g, st = set_staff(g, staffs, s, gl, hm)
        g = drop_specks(g)
        out[name] = g
        info[name] = dict(eye=eye.tolist(), head=hd, scale=round(SCALE, 3), **st)
        steps[name] = (f, bare, g, SCALE)
    return out, info, steps


# ------------------------------------------------------------------------------------------------ placing
DESIGN_GROUND = 81               # the design's soles' bottom edge
DESIGN_MID = 34.5                # between the design's boots (19-26, 41-50)
FEET_ROWS = 6                    # the rows over the ground the boots are found in


def feet(bare_scaled):
    """The boots on the ground (scaled grid): [rear middle or None, front middle or None]; a boot counts within
    FEET_ROWS of the lowest square."""
    ys = np.nonzero(bare_scaled[..., 3].any(1))[0]
    low = ys.max() + 1
    m = (bare_scaled[low - FEET_ROWS:low, :, 3] > 0).any(0)
    xs = np.nonzero(m)[0]
    groups = [g_ for g_ in np.split(xs, np.where(np.diff(xs) > 1)[0] + 1) if len(g_) >= 4]
    mids = [(g_.min() + g_.max() + 1) / 2.0 for g_ in groups]
    if len(mids) >= 2:
        return [mids[0], mids[-1]]
    return None


def offsets(bares):
    """Per frame the columns from the scaled grid to the design's: each tag's first frame stands between the design's
    boots, then her rear boot stays planted where it stood (she steps in with the front one); SPEC "anchor": "front"
    keeps the front boot where the frame before had it (the rear one lifted); off the ground (Final Spark's leap) the
    shift runs straight between the frames either side."""
    out = {}
    tags = {}
    for n in order(bares):
        tags.setdefault(n.rsplit("_", 1)[0], []).append(n)
    for tag, names in tags.items():
        ft = {n: feet(bares[n]) for n in names}
        first = ft[names[0]]
        rear = first[0] + DESIGN_MID - (first[0] + first[1]) / 2.0
        known = {}
        for i, n in enumerate(names):
            if SPEC[n].get("anchor") == "front":
                prev = names[i - 1]
                known[i] = known[i - 1] + ft[prev][1] - SPEC[n]["front"]
            elif ft[n] is not None and not SPEC[n].get("air"):
                known[i] = rear - ft[n][0]
        for i, n in enumerate(names):
            if i in known:
                v = known[i]
            else:
                lo = max(k for k in known if k < i)
                hi = min(k for k in known if k > i)
                v = known[lo] + (known[hi] - known[lo]) * (i - lo) / (hi - lo)
            out[n] = int(round(v))
    return out


def placed(rig):
    """{frame name: rig canvas}: the mended frames, soles on the design's ground, shifted by offsets()."""
    out, info, steps = build()
    pal = palette()
    bares = {}
    global SCALE
    for n, v in steps.items():
        SCALE = v[3]
        bares[n] = rescale(v[1], pal)
    off = offsets(bares)
    res = {}
    for n, g in out.items():
        can = rig.canvas()
        ys, xs = np.nonzero(g[..., 3] > 0)
        low = np.nonzero(bares[n][..., 3].any(1))[0].max() + 1
        drop = GY - low if 0 < GY - low <= 3 else 0          # a hair over the ground: her soles on it
        Y = ys + drop - GY + DESIGN_GROUND + rig.oy
        X = xs + off[n] + rig.ox
        ok = (Y >= 0) & (Y < can.shape[0]) & (X >= 0) & (X < can.shape[1])
        if not ok.all():
            raise SystemExit(f"{n}: {int((~ok).sum())} squares off the canvas")
        can[Y, X] = g[ys, xs]
        can[rig.GY:] = 0
        res[n] = can
    return res, off


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    out, info, steps = build()
    for n in order(out):
        print(n, info[n])
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        np.savez_compressed(os.path.join(a.review, "casts.npz"), **out)
        np.savez_compressed(os.path.join(a.review, "bare.npz"), **{n: v[1] for n, v in steps.items()})


if __name__ == "__main__":
    main()
