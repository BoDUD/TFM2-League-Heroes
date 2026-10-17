#!/usr/bin/env python3
"""Veigar's action strips, posed from the approved design's own pixels (Codex's part rig, with the staff fixed).

    python tools/art/rig_veigar.py

Codex drew image-model drafts of the seven actions from assets/source/veigar/MODEL_STRIPS.md, found they redesigned
him (a thicker body, swapped hands, a new head per frame) and delivered strips posed from the design instead
(assets/source/veigar/codex_strips/build_veigar_strips.py): the design cut into layers - head, torso, both legs,
the far arm with its gauntlet, the near sleeve, the staff with the near hand - each moved and turned per frame by
the poses below (nearest neighbour, the design's colours only). The user found the staff crooked ("法杖有点歪",
then "法杖末尾多了一截"): its layer also carried the robe's left edge, it turned to angles like 6, 18 or 84 degrees
(a one-square jog in the shaft), and the design's staff ended in a piece one column off. This script re-runs that
rig with:
  - the design's last staff piece (rows 34-37, one column right of the shaft) removed - assets/source/native/
    veigar_native.png already has it gone (the user: "用下面这个就可以");
  - the staff as a layer of its own (claw head, crystal, collars, shaft) turned to the nearest eighth of a turn:
    straight up, level, or 45 / 135 degrees drawn RotSprite-style (Scale2x three times, turned, back to one pixel
    per block by the commonest colour); the glove moves with the hand without turning; the robe stays on the body;
  - E's second frame raised straight (26 degrees would round to 45 and hide the claw behind the hat);
  - the standing point 10 columns left of Codex's (its idle was placed by overlap with League's idle, whose staff
    towers over the hat: the feet stood 10 px left of the unit).
Reads assets/source/native/veigar_native.png and veigar_cells.json, writes assets/source/native/veigar_<tag>.png
(import_native.py's layout, 8x). Then run import_native.py --hero veigar.
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

NATIVE = os.path.join(ROOT, "assets", "source", "native")
Z = 8
OX, OY = 46, 60                   # the design's top-left on the 128x128 canvas the rig works on
SHIFT = 10                        # Codex's standing point was this many columns right of the feet
EYES = [(255, 209, 50), (255, 242, 138)]
# the head (hat and black face) in the design's own rows and columns; the staff's claw stands left of the brim
HEAD_ROWS = {**{y: (0, 36) for y in range(0, 7)}, 7: (9, 36), 8: (9, 36),
             **{y: (10, 27) for y in range(9, 13)}, 13: (12, 25), **{y: (12, 24) for y in range(14, 18)}}
# the staff alone, read off the design square by square (the glove hides rows 21-24 of it)
STAFF = [((7, 8), (6, 7)), ((9, 9), (2, 3)), ((9, 9), (6, 8)), ((10, 10), (1, 3)), ((10, 10), (5, 9)),
         ((11, 12), (0, 9)), ((13, 13), (2, 9)), ((14, 14), (3, 8)), ((15, 16), (4, 7)), ((17, 19), (5, 8)),
         ((20, 20), (4, 8)), ((25, 25), (4, 8)), ((26, 26), (4, 7)), ((27, 27), (5, 8)), ((28, 33), (7, 9)),
         ((34, 36), (8, 10)), ((37, 37), (8, 9))]
GLOVE = [((21, 24), (3, 10))]


def pose(**kw):
    p = dict(body=(0, 0), body_angle=0, head=(0, 0), head_angle=0, hand=(52, 83), staff_angle=0, far_angle=0,
             far_delta=(0, 0), near_leg=(0, 0, 0), far_leg=(0, 0, 0), squint=False, ground=81, air=0, whole_angle=0,
             exact=False)
    p.update(kw)
    return p


P = pose
# Codex's poses (codex_strips/pose_parameters.json), E frame 2's staff raised straight
POSES = {
    "run": [
        P(near_leg=(3, 0, -12), far_leg=(-2, -2, 14), far_angle=3),
        P(body=(0, -1), head=(0, -1), hand=(52, 82), near_leg=(2, -1, 4), far_leg=(-1, 0, -9), far_angle=-2),
        P(body=(0, -2), head=(0, -2), hand=(52, 81), near_leg=(0, -2, 17), far_leg=(0, -2, -3), far_angle=-4),
        P(body=(0, -1), head=(0, -1), hand=(52, 82), near_leg=(-1, -1, 8), far_leg=(2, -1, -9), far_angle=-1),
        P(near_leg=(-2, -2, 14), far_leg=(3, 0, -12), far_angle=3),
        P(body=(0, -1), head=(0, -1), hand=(52, 82), near_leg=(-1, 0, -9), far_leg=(2, -1, 4), far_angle=5),
        P(body=(0, -2), head=(0, -2), hand=(52, 81), near_leg=(0, -2, -3), far_leg=(0, -2, 17), far_angle=5),
        P(body=(0, -1), head=(0, -1), hand=(52, 82), near_leg=(2, 0, -9), far_leg=(-1, -1, 8), far_angle=2),
    ],
    "attack": [
        P(exact=True),
        P(body=(-1, 0), head=(-1, 0), hand=(54, 77), staff_angle=18, far_angle=-10),
        P(body=(-1, 1), head=(-1, 1), hand=(55, 78), staff_angle=-38, far_angle=-12),
        P(body=(1, 1), head=(1, 1), hand=(64, 83), staff_angle=90, far_angle=-8, far_delta=(2, 0), near_leg=(-1, 0, 0),
          far_leg=(2, 0, 0)),
        P(body=(1, 0), head=(1, 0), hand=(63, 83), staff_angle=84, far_angle=-5, far_delta=(2, 0), far_leg=(1, 0, 0)),
        P(exact=True),
    ],
    "skill": [
        P(exact=True),
        P(body=(-1, 2), head=(-1, 2), hand=(53, 87), staff_angle=-75, far_angle=-4, near_leg=(-1, 0, 0)),
        P(body=(-1, 3), head=(-1, 3), hand=(52, 87), staff_angle=-92, far_angle=-10, near_leg=(-2, 0, 0)),
        P(body=(2, 2), head=(2, 2), hand=(65, 84), staff_angle=92, far_angle=-6, far_delta=(3, 0), near_leg=(-2, 0, 0),
          far_leg=(3, 0, -4)),
        P(body=(2, 1), head=(2, 1), hand=(64, 84), staff_angle=90, far_angle=-3, far_delta=(3, 0), near_leg=(-1, 0, 0),
          far_leg=(2, 0, 0)),
        P(exact=True),
    ],
    "skill2": [
        P(exact=True),
        P(hand=(53, 77), staff_angle=0, far_angle=-8),
        P(body=(0, 2), head=(0, 2), hand=(54, 83), staff_angle=-66, far_angle=9),
        P(body=(0, 2), head=(0, 2), hand=(53, 84), staff_angle=-125, far_angle=3),
        P(body=(-1, 0), head=(-1, 0), hand=(49, 84), staff_angle=-95, far_angle=12),
        P(hand=(51, 83), staff_angle=-34, far_angle=5),
        P(exact=True),
    ],
    "ult": [
        P(body=(0, 1), head=(0, 1), hand=(52, 84), far_angle=3),
        P(body=(0, 3), head=(0, 3), hand=(54, 84), staff_angle=12, far_angle=11),
        P(body=(0, -5), head=(0, -5), hand=(54, 76), staff_angle=8, far_angle=-18, near_leg=(1, -7, 14),
          far_leg=(-1, -5, -12), air=4),
        P(body=(0, -10), head=(0, -10), hand=(55, 62), staff_angle=16, far_angle=-30, far_delta=(2, -7),
          near_leg=(2, -10, 24), far_leg=(-1, -9, -18), air=9),
        P(body=(0, -2), head=(0, -2), hand=(53, 79), staff_angle=6, far_angle=-7, near_leg=(1, -1, 8),
          far_leg=(-1, -2, -8)),
        P(body=(0, 3), head=(0, 3), hand=(52, 85), staff_angle=-8, far_angle=10),
        P(exact=True),
    ],
    "hit": [
        P(body=(-2, 0), head=(-3, 0), hand=(50, 82), staff_angle=-8, far_angle=-8, far_delta=(-1, 0), squint=True),
        P(exact=True),
    ],
    "dead": [
        P(exact=True),
        P(body=(-2, 0), head=(-3, 0), hand=(51, 84), staff_angle=-28, far_angle=-14, near_leg=(1, -1, 15)),
        P(body=(-2, 2), head=(-3, 2), hand=(51, 86), staff_angle=-60, far_angle=-25, near_leg=(2, -1, 22)),
        P(body=(-1, 4), head=(-2, 4), hand=(51, 87), staff_angle=-80, far_angle=18, near_leg=(2, 0, 28),
          far_leg=(1, 0, -18)),
        P(hand=(52, 85), staff_angle=-75, whole_angle=-32, far_angle=15),
        P(hand=(52, 85), staff_angle=-55, whole_angle=-58, far_angle=65, ground=83),
        P(hand=(52, 84), staff_angle=-20, whole_angle=-79, far_angle=100, ground=83),
        P(hand=(52, 84), staff_angle=-10, whole_angle=-88, far_angle=118, ground=83),
    ]}


def layout(n):
    cols = {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)
    return cols, -(-n // cols)


def matrix(angle=0, pivot=(0, 0), delta=(0, 0)):
    a = math.radians(angle)
    c, s = math.cos(a), math.sin(a)
    if angle % 90 == 0:
        c, s = round(c), round(s)
    px, py = pivot
    dx, dy = delta
    return np.array([[c, -s, px - c * px + s * py + dx], [s, c, py - s * px - c * py + dy], [0, 0, 1]], float)


def warp(layer, m):
    inv = np.linalg.inv(m)
    return np.array(Image.fromarray(layer).transform((128, 128), Image.Transform.AFFINE, tuple(inv[:2].reshape(-1)),
                                                     Image.Resampling.NEAREST))


def scale2x(a):
    h, w = a.shape[:2]
    p = np.pad(a, ((1, 1), (1, 1), (0, 0)), mode="edge")
    B, D, E, F, H = p[:-2, 1:-1], p[1:-1, :-2], p[1:-1, 1:-1], p[1:-1, 2:], p[2:, 1:-1]
    eq = lambda u, v: np.all(u == v, axis=2)  # noqa: E731
    cond = ~eq(B, H) & ~eq(D, F)
    out = np.zeros((h * 2, w * 2, a.shape[2]), a.dtype)
    out[0::2, 0::2] = np.where((cond & eq(D, B))[..., None], D, E)
    out[0::2, 1::2] = np.where((cond & eq(B, F))[..., None], F, E)
    out[1::2, 0::2] = np.where((cond & eq(D, H))[..., None], D, E)
    out[1::2, 1::2] = np.where((cond & eq(H, F))[..., None], F, E)
    return out


def warp_rs(layer, m):
    """RotSprite-style: Scale2x three times (8x), turn by nearest neighbour, back to 1x by each block's commonest
    colour (a block at least half covered is opaque). Right angles stay exact."""
    if all(abs(v - round(v)) < 1e-9 for v in m[:2, :2].reshape(-1)):
        return warp(layer, m)
    big = scale2x(scale2x(scale2x(layer)))
    S = np.diag([8.0, 8.0, 1.0])
    inv = np.linalg.inv(S @ m @ np.linalg.inv(S))
    r = np.array(Image.fromarray(big).transform((1024, 1024), Image.Transform.AFFINE, tuple(inv[:2].reshape(-1)),
                                                Image.Resampling.NEAREST))
    out = np.zeros((128, 128, 4), np.uint8)
    blk = r.reshape(128, 8, 128, 8, 4).transpose(0, 2, 1, 3, 4).reshape(128, 128, 64, 4)
    for y in range(128):
        for x in range(128):
            px = blk[y, x]
            op = px[:, 3] > 0
            if op.sum() < 32:
                continue
            vals, counts = np.unique(px[op].view(np.uint32).reshape(-1), return_counts=True)
            out[y, x] = np.frombuffer(np.uint32(vals[counts.argmax()]).tobytes(), np.uint8)
    return out


def snap(a):
    """The staff's angle on the nearest eighth of a turn: straight up, level or a clean 45 / 135."""
    return int(round(a / 45.0)) * 45


def over(dst, src):
    m = src[:, :, 3] > 0
    dst[m] = src[m]


def segment_matrix(a, b, c, d):
    """Codex's sleeve warp between two joint pairs, the sleeve's thickness kept."""
    a, b, c, d = (np.array(v, dtype=float) for v in (a, b, c, d))
    u, v = b - a, d - c
    scale = max(.78, min(1.5, np.linalg.norm(v) / max(1, np.linalg.norm(u))))
    ang = math.atan2(v[1], v[0]) - math.atan2(u[1], u[0])
    co, si = math.cos(ang) * scale, math.sin(ang) * scale
    A = np.array([[co, -si], [si, co]])
    t = c - A @ a
    return np.array([[A[0, 0], A[0, 1], t[0]], [A[1, 0], A[1, 1], t[1]], [0, 0, 1]])


def components(alpha):
    pts = set(zip(*np.where(alpha)))
    groups = []
    while pts:
        start = pts.pop()
        group, q = [start], [start]
        while q:
            y, x = q.pop()
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    z = (y + dy, x + dx)
                    if z in pts:
                        pts.remove(z)
                        q.append(z)
                        group.append(z)
        groups.append(group)
    return sorted(groups, key=len, reverse=True)


def canvas_design():
    a = np.asarray(Image.open(G.lp(os.path.join(NATIVE, "veigar_native.png"))).convert("RGBA"))[Z // 2::Z, Z // 2::Z]
    ys, xs = np.nonzero(a[..., 3] > 0)
    fig = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    base = np.zeros((128, 128, 4), np.uint8)
    base[OY:OY + fig.shape[0], OX:OX + fig.shape[1]] = fig
    return base


def mask(spec, shape):
    m = np.zeros(shape, bool)
    for (r0, r1), (c0, c1) in spec:
        m[OY + r0:OY + r1 + 1, OX + c0:OX + c1 + 1] = True
    return m


def layers(base):
    h, w = base.shape[:2]
    Y, X = np.mgrid[:h, :w]
    op = base[..., 3] > 0
    head = np.zeros((h, w), bool)
    for y, (x0, x1) in HEAD_ROWS.items():
        head[OY + y, OX + x0:OX + x1 + 1] = True
    head &= op
    remaining = op & ~head
    masks = {"head": head}
    for name, m in (("staff", mask(STAFF, (h, w))), ("glove", mask(GLOVE, (h, w))),
                    ("near_leg", (Y >= 96) & (X < 65)), ("far_leg", (Y >= 96) & (X >= 65)),
                    ("far_arm", (X >= 72) & (Y <= 89)), ("near_arm", (X <= 60) & (Y >= 79) & (Y <= 84))):
        masks[name] = remaining & m
        remaining &= ~m
    masks["torso"] = remaining
    out = {}
    for n, m in masks.items():
        a = np.zeros_like(base)
        a[m] = base[m]
        out[n] = a
    return out


def render(p, base, L):
    if p["exact"]:
        return base.copy(), L["head"].copy()
    dst = np.zeros_like(base)
    bx, by = p["body"]
    for name, anchor, params in (("far_leg", (70, 96), p["far_leg"]), ("near_leg", (59, 96), p["near_leg"])):
        dx, dy, a = params
        over(dst, warp(L[name], matrix(a, anchor, (dx, dy))))
    over(dst, warp(L["far_arm"], matrix(p["far_angle"], (71, 83), (bx + p["far_delta"][0], by + p["far_delta"][1]))))
    over(dst, warp(L["torso"], matrix(p["body_angle"], (65, 88), p["body"])))
    over(dst, warp(L["near_arm"], segment_matrix((59, 82), (53, 84), (59 + bx, 82 + by), p["hand"])))
    hand = (p["hand"][0] - 52, p["hand"][1] - 83)
    over(dst, warp_rs(L["staff"], matrix(snap(p["staff_angle"]), (52, 83), hand)))
    over(dst, warp(L["glove"], matrix(0, (52, 83), hand)))
    head = L["head"].copy()
    if p["squint"]:
        Y = np.mgrid[:128, :128][0]
        for e in EYES:
            em = np.all(head[:, :, :3] == e, axis=2) & (head[:, :, 3] > 0) & (Y == 75)
            head[em] = (17, 16, 32, 255)
    head = warp(head, matrix(p["head_angle"], (65, 76), p["head"]))
    over(dst, head)
    if p["whole_angle"]:
        wa = p["whole_angle"]
        near = int(round(wa / 90.0)) * 90
        wm = matrix(near if abs(wa - near) <= 12 else wa, (65, 90))
        dst, head = warp_rs(dst, wm), warp_rs(head, wm)
    for group in components(dst[:, :, 3] > 0)[1:]:          # bits of robe the moved staff left in the air
        if len(group) <= 6:
            for yy, xx in group:
                if head[yy, xx, 3] == 0:
                    dst[yy, xx] = 0
    return dst, head


def place(src, p, pivot, tag):
    tx, ty = pivot[0] + SHIFT - 74, pivot[1] - 88
    yy, xx = np.where(src[:, :, 3] > 0)
    if tag == "dead" and p["whole_angle"]:
        ty += p["ground"] - (int(yy.max()) + ty)
    frame = np.zeros((96, 96, 4), np.uint8)
    nx, ny = xx + tx, yy + ty
    ok = (nx >= 0) & (nx < 96) & (ny >= 0) & (ny <= p["ground"])
    frame[ny[ok], nx[ok]] = src[yy[ok], xx[ok]]
    return frame


def main():
    cells = json.load(open(G.lp(os.path.join(NATIVE, "veigar_cells.json")), encoding="utf-8"))
    cw, ch = cells["cell"]
    base = canvas_design()
    L = layers(base)
    poses = dict(POSES, idle=[P(exact=True)] * len(cells["tags"]["idle"]))
    for tag, meta in cells["tags"].items():
        frames = [place(render(p, base, L)[0], p, fr["pivot"], tag) for p, fr in zip(poses[tag], meta)]
        cols, rows = layout(len(frames))
        sheet = np.zeros((rows * ch, cols * cw, 4), np.uint8)
        for k, f in enumerate(frames):
            sheet[k // cols * ch:(k // cols + 1) * ch, k % cols * cw:(k % cols + 1) * cw] = f
        Image.fromarray(np.repeat(np.repeat(sheet, Z, 0), Z, 1)).save(G.lp(os.path.join(NATIVE, f"veigar_{tag}.png")))
        print(f"{tag:7s} {len(frames)} frames, pieces", [len(components(f[..., 3] > 0)) for f in frames])


if __name__ == "__main__":
    main()
