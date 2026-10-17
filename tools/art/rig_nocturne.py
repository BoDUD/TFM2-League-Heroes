#!/usr/bin/env python3
"""Nocturne's run, attack, Q, E, R and R landing posed after League's clips with the approved design's own pixels.

    python tools/art/rig_nocturne.py [--check] [--review DIR --renders DIR]

Why: Codex's strips (assets/source/nocturne/codex_strips, its HANDOFF.md) moved only the arms of the frontal design -
"并非逐帧复刻英雄联盟 3D 模型的转身和透视形变". The user: "感觉梦魇平A的姿势和英雄联盟不一样？ 改一改吧", "所以你能改吗？
不用 codex", "剩下的有不一样的地方也拜托你改了 走路姿势这种". Set beside League's clips rendered at game size
(tools/lol/native_pose.py on assets/source/nocturne/poses.json, also from yaw 45 and 75 to see the lean), six strips were
far off: League's run is a hunched glide with the arms spread in an arch and the blades out and back (Codex: the idle
bobbing), attack1 is a spinning slash (wind-up, lunge, a turn with the back to the camera and a blade raised high,
back to the front), Spell1 flings the arms out level and swings them down to throw, Spell3 raises both arms high and
then crouches reaching forward, Spell4 raises both blades and dives leaning far forward, attack3 (the landing) is a
wide level slash. The cleave (crit: the arms spread level), the hit and the death (sinking into smoke) were close
enough and stay Codex's; the idle is the design.

How: the design (assets/source/native/nocturne_native.png, 33x40) is cut along its own outline into the head (crest,
skull, eyes), the two pauldrons, the two arms (blade and hand), the torso with the tabard and the tail; an outline
square goes to every part it touches. Each frame of POSES moves the parts: shifts, quarter turns and mirroring
(lossless), RotSprite turns for other angles (Scale2x three times, turned by nearest neighbour about the joint,
sampled back: the blades keep their pixel clusters), row shears for a lean, and "bridges" - a navy upper arm with its
outline from the pauldron to an arm moved out. The spin's two frames use the design from behind: mirrored about its
middle column, the eyes, the tabard's eye and the pauldrons' gems painted over. Pockets the frame's edge cannot reach
take the body's navy; tools/art/import_native.py then closes the outline (COMPLETE). Frame counts and durations are
the strips' as before, so the kit's hit ticks still land on the same frames (attack 3, Q 3, E 3, R launch 3, landing 1).

Writes assets/source/native/nocturne_<tag>.png (8x) for RIGGED and their entries in nocturne_cells.json (standing
point CPIV in every cell); tools/art/fix_nocturne_strips.py writes the other four from Codex and leaves these alone.
--check compares with the committed files. --review DIR writes rig_<tag>.png (League's frame over the rig's, 4x) from
native_pose.py --alpha renders in --renders.
"""
import argparse
import json
import os
import sys
from collections import deque

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
from native_refs import layout  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(SRC, "nocturne_native.png")
Z = 8
PIVOT = (64, 88)                 # the design's standing point on its 128x128 canvas
CELL = (120, 104)
CPIV = (60, 77)                  # the standing point in every rigged cell
OUTLINE = (0x08, 0x06, 0x11)
NAVY = (0x10, 0x10, 0x29)
SKULL = (0x17, 0x1C, 0x43)
PURPLE = (0x58, 0x32, 0x62)
# the head on the design canvas, row by row (x0, x1): the crest, the skull with the eyes, down to the chin
HEAD_ROWS = {60: (57, 61), 61: (56, 62), 62: (59, 64), 63: (60, 65), 64: (58, 67), 65: (58, 67), 66: (58, 69),
             67: (58, 69), 68: (59, 69), 69: (59, 69), 70: (60, 69), 71: (60, 69), 72: (60, 69), 73: (60, 69),
             74: (60, 68), 75: (60, 69), 76: (60, 67), 77: (62, 66)}
# where each part turns and is placed: the neck, the pauldrons' inner corners, the arms' tops (the shoulders), the
# standing point, the tail's root
JOINT = {"head": (64, 77), "pl": (58, 74), "pr": (70, 74), "al": (52, 77), "ar": (74, 78), "body": (64, 88),
         "tail": (64, 94)}
MIRROR = 124                     # the back view: x -> 124 - x (the design's middle column is 62)
EYE_UP = 6                       # the eyes' rows over the head's joint (the neck)

BOB = [0, -1, -1, 0, 0, -1, -1, 0]
ARM = [-1, -1, 0, 1, 1, 1, 0, -1]
TAILX = [-1, -2, -2, -1, -1, -2, -2, -1]
SPREAD = [((54, 75), (49, 78)), ((71, 75), (77, 79))]
# per frame: "view" front/back, "order" (back to front), part: [("at", dx, dy) | ("rot", quarter turns) |
# ("deg", degrees counter-clockwise) | ("flip",) | ("shear", k)], "lean" (a shear of the whole frame about the
# standing point: + leans the top forward), "move" (dx, dy), "bridges" [((x0, y0), (x1, y1))]
POSES = {
    # League's run: hunched (the head sunk between the pauldrons), arms spread wide in an arch with the blades out and
    # back, a forward lean, the arms rising and falling against each other, the tail trailing
    "run": [{"lean": 0.08, "move": (0, BOB[k]),
             "head": [("at", 1, 3)], "pl": [("at", -1, 0)], "pr": [("at", 1, 0)],
             "al": [("deg", -28), ("at", -5, ARM[k] - 1)],
             "ar": [("deg", 28), ("at", 5, -ARM[k] - 1)],
             "bridges": [((54, 75), (47, 76 + ARM[k])), ((71, 75), (79, 77 - ARM[k]))],
             "tail": [("at", TAILX[k], 0)]} for k in range(8)],
    # League's attack1: the wind-up (blade drawn back), the crouch (blade raised behind), the lunge with the thrust
    # (the hit, frame 3), the spin seen from behind (one blade high), rising, back to the front with the arms spread
    "attack": [
        {"lean": -0.05, "al": [("deg", -100), ("at", -1, -3)], "ar": [("deg", 12), ("at", 1, 1)]},
        {"lean": 0.06, "move": (1, 2), "head": [("at", 1, 1)], "order": ["tail", "al", "body", "ar", "pl", "pr", "head"],
         "al": [("deg", -160), ("at", 0, -2)], "ar": [("at", 0, 1)]},
        {"lean": 0.15, "move": (5, 2), "head": [("at", 1, 2)],
         "ar": [("deg", 80), ("at", 2, -1)], "al": [("deg", -110), ("at", -1, 0)]},
        {"view": "back", "lean": 0.05, "move": (3, 0),
         "al": [("deg", 165), ("at", 0, -2)], "ar": [("deg", -40), ("at", -2, 1)]},
        {"view": "back", "move": (2, -2),
         "al": [("deg", 180), ("at", 0, -4)], "ar": [("deg", -95), ("at", -1, -1)]},
        {"move": (1, 0), "al": [("deg", -35), ("at", -3, 1)], "ar": [("deg", 35), ("at", 3, 1)], "bridges": SPREAD},
    ],
    # League's Spell1 (Q): the arms flung out level, a little higher, then swung down and forward to throw (the
    # release, frame 3), the follow-through low and forward, the arms spread low
    "skill": [
        {"lean": -0.03, "al": [("deg", -90), ("at", -1, -3)], "ar": [("deg", 90), ("at", 1, -3)]},
        {"lean": -0.05, "al": [("deg", -105), ("at", -1, -4)], "ar": [("deg", 105), ("at", 1, -4)]},
        {"lean": 0.12, "move": (2, 2), "head": [("at", 1, 1)],
         "al": [("deg", -25), ("at", -2, 1)], "ar": [("deg", 60), ("at", 2, 0)]},
        {"lean": 0.08, "move": (1, 1), "head": [("at", 1, 1)],
         "al": [("deg", -15), ("at", -1, 1)], "ar": [("deg", 35), ("at", 1, 1)]},
        {"al": [("deg", -35), ("at", -3, 1)], "ar": [("deg", 35), ("at", 3, 1)], "bridges": SPREAD},
    ],
    # League's Spell3 (E): arms low and spread, both raised high beside the head, then crouched reaching down and
    # forward (the grip, frame 3), lower still, the arms flung out level
    "skill2": [
        {"al": [("deg", -30), ("at", -2, 0)], "ar": [("deg", 30), ("at", 2, 0)],
         "bridges": [((54, 75), (50, 77)), ((71, 75), (76, 78))]},
        {"lean": -0.04, "order": ["tail", "al", "ar", "body", "pl", "pr", "head"],
         "al": [("deg", -150), ("at", 0, -3)], "ar": [("deg", 150), ("at", 0, -3)]},
        {"lean": 0.07, "move": (1, 3), "head": [("at", 0, 2)],
         "al": [("deg", -60), ("at", -1, 1)], "ar": [("deg", 75), ("at", 2, 1)]},
        {"lean": 0.07, "move": (1, 3), "head": [("at", 0, 2)],
         "al": [("deg", -50), ("at", -1, 2)], "ar": [("deg", 62), ("at", 2, 2)]},
        {"al": [("deg", -90), ("at", -1, -2)], "ar": [("deg", 90), ("at", 1, -2)]},
    ],
    # League's Spell4_activate then Spell4 (R): arms spread low, both blades raised up beside him, then the dive:
    # leaning far forward, the blades swept back and low, the tail streaming behind (frames 3-6 repeat in flight)
    "ult": [
        {"al": [("deg", -30), ("at", -2, 1)], "ar": [("deg", 30), ("at", 2, 1)],
         "bridges": [((54, 75), (50, 78)), ((71, 75), (76, 79))]},
        {"lean": -0.03, "order": ["tail", "al", "ar", "body", "pl", "pr", "head"],
         "al": [("deg", -170), ("at", 0, -3)], "ar": [("deg", 170), ("at", 0, -3)]},
    ] + [
        {"lean": 0.22, "move": (2, 0), "head": [("at", 2, 2)], "order": ["tail", "ar", "body", "al", "pl", "pr", "head"],
         "al": [("deg", -62 + f), ("at", -3, 0)], "ar": [("deg", 18 - f), ("at", 0, 0)],
         "tail": [("at", -3 - (f > 0), 0)]} for f in (0, 4, 0, -4)
    ],
    # League's attack3 (the landing): a wide level slash - one blade swept forward, the other back - opening to both
    # arms level, then spread low
    "ult_hit": [
        {"lean": 0.1, "move": (2, 0), "ar": [("deg", 70), ("at", 2, -1)], "al": [("deg", -70), ("at", -2, -1)]},
        {"lean": 0.05, "move": (1, 0), "ar": [("deg", 100), ("at", 1, -2)], "al": [("deg", -110), ("at", -1, -2)]},
        {"al": [("deg", -90), ("at", -1, -2)], "ar": [("deg", 90), ("at", 1, -2)]},
        {"al": [("deg", -45), ("at", -3, 0)], "ar": [("deg", 45), ("at", 3, 0)],
         "bridges": [((54, 75), (49, 77)), ((71, 75), (77, 78))]},
    ],
}
RIGGED = list(POSES)
MS = {"run": [100] * 8, "attack": [60, 60, 60, 70, 80, 90], "skill": [60, 70, 70, 80, 100],
      "skill2": [60, 70, 70, 80, 100], "ult": [60, 70, 155, 155, 155, 155], "ult_hit": [80, 80, 80, 100]}


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def load():
    a = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))[Z // 2::Z, Z // 2::Z].copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    return a


def label(fill):
    """4-neighbour components of a mask: (labels, count)."""
    H, W = fill.shape
    lab = np.zeros((H, W), int)
    n = 0
    for y, x in zip(*np.nonzero(fill)):
        if lab[y, x]:
            continue
        n += 1
        q = deque([(y, x)])
        lab[y, x] = n
        while q:
            cy, cx = q.popleft()
            for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                if 0 <= ny < H and 0 <= nx < W and fill[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = n
                    q.append((ny, nx))
    return lab, n


def is_col(a, c):
    return np.all(a[..., :3] == c, axis=-1) & (a[..., 3] > 0)


def part_masks(a):
    """{part: mask} on the design canvas, from the regions its outline encloses; outline squares go to every part
    they touch (8 neighbours), a thick corner touching none to the nearest."""
    ol = is_col(a, OUTLINE)
    lab, n = label((a[..., 3] > 0) & ~ol)
    head = np.zeros(ol.shape, bool)
    for y, (x0, x1) in HEAD_ROWS.items():
        head[y, x0:x1 + 1] = True
    own = {k: np.zeros(ol.shape, bool) for k in ("head", "pl", "pr", "al", "ar", "body")}
    for k in range(1, n + 1):
        m = lab == k
        ys, xs = np.nonzero(m)
        cx, cy = xs.mean(), ys.mean()
        if cy < 79 and xs.max() > 70 and xs.min() < 60:        # the head runs into the right pauldron
            own["head"] |= m & head
            own["pr"] |= m & ~head
        elif cy < 76 and cx < 60:
            own["pl"] |= m
        elif cx < 58 and cy >= 74:
            own["al"] |= m
        elif cx > 66 and 77 <= cy < 95:
            own["ar"] |= m
        else:
            own["body"] |= m
    own["tail"] = own["body"].copy()
    own["tail"][:95] = False
    own["body"] &= ~own["tail"]
    masks = {}
    for name, m in own.items():
        p = np.pad(m, 1)
        touch = np.zeros_like(m)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                touch |= p[1 + dy:1 + dy + m.shape[0], 1 + dx:1 + dx + m.shape[1]]
        masks[name] = m | (ol & touch)
    left = (a[..., 3] > 0) & ~np.any(np.stack(list(masks.values())), 0)
    for y, x in zip(*np.nonzero(left)):
        best = min(own, key=lambda k: np.min(np.abs(np.argwhere(own[k]) - (y, x)).sum(1)))
        masks[best][y, x] = True
    return masks


def back_of(a):
    """The design from behind: the eyes, the tabard's eye and the pauldrons' gems painted over, mirrored."""
    b = a.copy()
    b[is_col(b, (0xFF, 0xFF, 0xFF)), :3] = SKULL
    tabard = np.zeros(b.shape[:2], bool)
    tabard[80:95, 60:68] = True
    b[tabard & (b[..., 3] > 0) & ~is_col(b, OUTLINE), :3] = NAVY
    for c in ((0x46, 0x5D, 0xAC), (0x28, 0x4C, 0x85), (0x30, 0x43, 0x7B)):
        m = is_col(b, c)
        m[:, 58:71] = False
        b[m, :3] = PURPLE
    return np.roll(b[:, ::-1], MIRROR - 127, axis=1)


def sprite(a, mask, joint):
    ys, xs = np.nonzero(mask)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    s = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
    sub = mask[y0:y1, x0:x1]
    s[sub] = a[y0:y1, x0:x1][sub]
    return s, (joint[0] - x0, joint[1] - y0)


def scale2x(s):
    """EPX / Scale2x: each pixel becomes 2x2, a corner taking a neighbour's colour where two edges agree."""
    key = (s[..., 0].astype(np.int64) << 24) | (s[..., 1].astype(np.int64) << 16) | \
          (s[..., 2].astype(np.int64) << 8) | s[..., 3].astype(np.int64)
    p = np.pad(key, 1, mode="edge")
    A, Bv, C, D = p[:-2, 1:-1], p[1:-1, 2:], p[1:-1, :-2], p[2:, 1:-1]      # up, right, left, down
    pk = np.pad(s, ((1, 1), (1, 1), (0, 0)), mode="edge")
    up, right, left, down = pk[:-2, 1:-1], pk[1:-1, 2:], pk[1:-1, :-2], pk[2:, 1:-1]
    h, w = s.shape[:2]
    out = np.zeros((h * 2, w * 2, 4), np.uint8)
    out[0::2, 0::2] = np.where(((C == A) & (C != D) & (A != Bv))[..., None], up, s)
    out[0::2, 1::2] = np.where(((A == Bv) & (A != C) & (Bv != D))[..., None], right, s)
    out[1::2, 0::2] = np.where(((D == C) & (D != Bv) & (C != A))[..., None], left, s)
    out[1::2, 1::2] = np.where(((Bv == D) & (Bv != A) & (D != C))[..., None], down, s)
    return out


def rotsprite(s, j, deg):
    """RotSprite about the joint, + counter-clockwise on screen: Scale2x three times, nearest neighbour, back to 1x."""
    big = scale2x(scale2x(scale2x(s)))
    h, w = s.shape[:2]
    r = int(np.ceil(np.hypot(max(j[0], w - j[0]), max(j[1], h - j[1])))) + 2
    t = np.radians(deg)
    oy, ox = np.mgrid[-r:r + 1, -r:r + 1]
    sx = np.cos(t) * ox - np.sin(t) * oy
    sy = np.sin(t) * ox + np.cos(t) * oy
    bx = np.floor((sx + j[0] + 0.5) * 8).astype(int)
    by = np.floor((sy + j[1] + 0.5) * 8).astype(int)
    ok = (bx >= 0) & (bx < w * 8) & (by >= 0) & (by < h * 8)
    out = np.zeros((2 * r + 1, 2 * r + 1, 4), np.uint8)
    out[ok] = big[by[ok], bx[ok]]
    return out, (r, r)


def op(s, j, o):
    """One transform of a sprite about its joint j (x, y in the sprite): (sprite, joint)."""
    jx, jy = j
    if o[0] == "deg":
        return rotsprite(s, j, o[1])
    if o[0] == "rot":                           # quarter turns, counter-clockwise
        h, w = s.shape[:2]
        for _ in range(o[1] % 4):
            s = np.rot90(s)
            jx, jy = jy, w - 1 - jx
            h, w = w, h
        return s, (jx, jy)
    if o[0] == "flip":
        return s[:, ::-1].copy(), (s.shape[1] - 1 - jx, jy)
    if o[0] == "shear":                         # rows moved by k x (rows above the joint): + leans the top right
        h, w = s.shape[:2]
        sh = [int(round(o[1] * (jy - y))) for y in range(h)]
        lo = min(sh)
        out = np.zeros((h, w + max(sh) - lo, 4), np.uint8)
        for y in range(h):
            out[y, sh[y] - lo:sh[y] - lo + w] = s[y]
        return out, (jx - lo, jy)
    raise ValueError(o)


def paste(canvas, s, j, at):
    ys, xs = np.nonzero(s[..., 3])
    cy, cx = ys + at[1] - j[1], xs + at[0] - j[0]
    ok = (cy >= 0) & (cy < canvas.shape[0]) & (cx >= 0) & (cx < canvas.shape[1])
    canvas[cy[ok], cx[ok]] = s[ys[ok], xs[ok]]


def fill_holes(c, limit=40):
    """Empty pockets the frame's edge cannot reach (up to `limit` squares) take the body's navy."""
    lab, n = label(c[..., 3] == 0)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
    for k in range(1, n + 1):
        m = lab == k
        if k not in edge and m.sum() <= limit:
            c[m] = (*NAVY, 255)
    return c


def bridge(c, a, b):
    """A navy upper arm two squares thick from a to b, outlined where it meets nothing."""
    n = max(abs(b[0] - a[0]), abs(b[1] - a[1]), 1)
    pts = {(int(round(a[0] + (b[0] - a[0]) * t / n)), int(round(a[1] + (b[1] - a[1]) * t / n))) for t in range(n + 1)}
    limb = {(x + dx, y + dy) for x, y in pts for dx in (0, 1) for dy in (0, 1)}
    for x, y in limb:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if (x + dx, y + dy) not in limb:
                    c[y + dy, x + dx] = (*OUTLINE, 255)
    for x, y in limb:
        c[y, x] = (*SKULL, 255)


def frame(src, masks, joints, pose):
    """One pose on the design canvas."""
    c = np.zeros_like(src)
    for a, b in pose.get("bridges", []):
        bridge(c, a, b)
    placed = {}
    for name in pose.get("order", ["tail", "body", "al", "ar", "pl", "pr", "head"]):
        s, j = sprite(src, masks[name], joints[name])
        dx = dy = 0
        for o in pose.get(name, []):
            if o[0] == "at":
                dx, dy = o[1], o[2]
            else:
                s, j = op(s, j, o)
        if name == "head":                      # the face is never sheared: it goes on after the lean
            placed[name] = (s, j, dx, dy)
            continue
        paste(c, s, j, (joints[name][0] + dx, joints[name][1] + dy))
    c = fill_holes(c)
    lean = pose.get("lean", 0)
    if lean:
        sh, (jx, _) = op(c, PIVOT, ("shear", lean))
        wide = np.zeros((128, 256 + sh.shape[1], 4), np.uint8)
        wide[:, 128:128 + sh.shape[1]] = sh
        c = wide[:, 128 + jx - PIVOT[0]:128 + jx - PIVOT[0] + 128]
    s, j, dx, dy = placed["head"]
    hx, hy = joints["head"][0] + dx, joints["head"][1] + dy
    paste(c, s, j, (hx + int(round(lean * (PIVOT[1] - (hy - EYE_UP)))), hy))   # moved as its eye row is
    mx, my = pose.get("move", (0, 0))
    return np.roll(np.roll(c, my, 0), mx, 1)


def to_cell(c):
    """Design canvas -> a CELL with the standing point on CPIV."""
    cell = np.zeros((CELL[1], CELL[0], 4), np.uint8)
    paste(cell, c, PIVOT, CPIV)
    return cell


def build():
    """{tag: [cell]} for every rigged tag."""
    design = load()
    back = back_of(design)
    front = part_masks(design)
    views = {"front": (design, front, JOINT),
             "back": (back, {k: np.roll(m[:, ::-1], MIRROR - 127, axis=1) for k, m in front.items()},
                      {k: (MIRROR - x, y) for k, (x, y) in JOINT.items()})}
    return {tag: [to_cell(frame(*views[p.get("view", "front")], p)) for p in poses] for tag, poses in POSES.items()}


def strip(cells):
    cols, rows = layout(len(cells))
    out = np.zeros((rows * CELL[1], cols * CELL[0], 4), np.uint8)
    for k, cell in enumerate(cells):
        r, cc = divmod(k, cols)
        out[r * CELL[1]:(r + 1) * CELL[1], cc * CELL[0]:(cc + 1) * CELL[0]] = cell
    return np.repeat(np.repeat(out, Z, 0), Z, 1)


def entries(tag):
    return [{"pivot": list(CPIV), "ms": ms} for ms in MS[tag]]


def review(sheets, out, renders):
    """League's frame (a native_pose.py --alpha render) over the rig's, 4x, per tag."""
    lc = json.load(open(os.path.join(renders, "nocturne_cells.json"), encoding="utf-8"))
    for tag, cells in sheets.items():
        im = np.asarray(Image.open(os.path.join(renders, f"nocturne_pose_{tag}.png")).convert("RGBA"))[4::8, 4::8]
        cols = im.shape[1] // CELL[0]
        W, H = 70, 64
        sheet = Image.new("RGBA", (W * len(cells), H * 2 + 2), (40, 40, 44, 255))
        for k, cell in enumerate(cells):
            r, c = divmod(k, cols)
            px, py = lc["tags"][tag][k]["pivot"]
            for row, (img, (x, y)) in enumerate(((im[r * CELL[1]:(r + 1) * CELL[1], c * CELL[0]:(c + 1) * CELL[0]],
                                                 (px, py)), (cell, CPIV))):
                box = Image.new("RGBA", (W, H), (93, 99, 85, 255))
                box.alpha_composite(Image.fromarray(np.ascontiguousarray(img)), (W // 2 - x, H - 12 - y))
                sheet.paste(box, (k * W, row * (H + 2)))
        sheet.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).convert("RGB").save(
            os.path.join(out, f"rig_{tag}.png"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review")
    ap.add_argument("--renders")
    a = ap.parse_args()
    sheets = build()
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        review(sheets, a.review, a.renders)
    cells_path = os.path.join(SRC, "nocturne_cells.json")
    spec = json.load(open(lp(cells_path), encoding="utf-8"))
    same = True
    for tag, cells in sheets.items():
        big = strip(cells)
        path = os.path.join(SRC, f"nocturne_{tag}.png")
        if a.check:
            ok = np.array_equal(np.asarray(Image.open(lp(path)).convert("RGBA")), big) and spec["tags"][tag] == entries(tag)
            same &= ok
            print(f"{tag:8s} {'identical' if ok else 'DIFFERENT'}")
        else:
            Image.fromarray(big).save(lp(path))
            spec["tags"][tag] = entries(tag)
            print(f"{tag:8s} {len(cells)} frames")
    if a.check:
        print("all identical" if same else "DIFFERENT")
    else:
        with open(lp(cells_path), "w", encoding="utf-8") as f:
            json.dump(spec, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
