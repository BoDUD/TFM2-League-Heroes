#!/usr/bin/env python3
"""Rakan's action strips: Codex's delivery (assets/source/rakan/codex_strips, 2026-10-04 20:19) with Claude's fixes
-> assets/source/native/rakan_<tag>.png (8x) and rakan_cells.json, for tools/art/import_native.py.

    python tools/art/fix_rakan_strips.py [--check] [--review DIR]

The user, on Codex's strips: 「不对的地方你帮我修复 codex太笨了 不想让他返工了」. Codex drew each strip with image_gen, read
it back on its grid and pasted the design's head over its own; the bodies, the cloak and the poses are its own and
stay. Fixes, in order:
  1. HALO: bits of Codex's own head stuck out round the pasted design head - an extra red ear tip floating beside the
     ear in attack 1 and Q 3, a dark-red + black pair outside the ear in most frames, which flickers as the frames
     play. Every group of non-head squares of at most HALO_MAX that touches the pasted head (8-neighbours) or lies
     within HALO_GAP of it, and is not joined to the rest of the figure except through the head, goes.
  2. HOLES: the ground showed through a triangle behind the head (between the nape, the cloak and the collar) in 18
     frames; an enclosed hole next to the head takes the high collar's dark red. Pinholes (at most PIN squares) take
     their 4-neighbours' commonest colour.
  3. ARMS: Q 4 and 5 raised the near forearm and hand beside the face with no upper arm (a hand floating apart): a
     short upper arm in the skin's colours, outlined, from the shoulder to the elbow (ARMS, letter maps).
  4. R LEGS: Codex drew the R sprint's legs thin and dark like League's, but some shins were solid outline (3-square
     black bars in R 5-8, a 1-square black line for the back leg in R 7), some had the trousers' green as an outline,
     and none had the red band the idle and the run wear below the knee. Per frame (R_LEGS): the bars get an inner
     column of the wraps' colour inside their own outline (no wider), the shin's first 2 squares below the knee the
     band's dark red, the green outline squares the outline; R 7's back foot ends in the boots' purple.
  5. DEATH: in frames 5-8 bits of Codex's own head stayed beside the pasted, turned design head - its ear tip and a
     slice of its hair standing up like a stick (DEAD_CLEAR) - and the turned head stood 1-3 columns apart from the
     shoulders: the remnants go, and a gap of at most GAP_MAX squares along a row between head and body takes the
     high collar's dark red.
  6. BLACK FILL: Codex drew the R back thigh (R 1-3, 7, 8) and a few knees as solid outline bands 3 rows thick - a
     black block where the leg is: a pixel of the outline colour between the waist and the ankles (rows BLACK_ROWS)
     with no light 8-neighbour and the outline on both sides along its row or its column takes the trousers' green
     above the knees (rows under KNEE_ROW: the thighs, as in the idle) and lower down the commonest leg colour within
     3 squares (the wraps' grey-violet or the band's red); bands 2 rows thick stay, they have no middle.
  7. SEAT (the user, in game: 「移动的时候头和身体不协调」, 「受击的时候身体和腿几乎分离」): Codex kept the pasted head
     in one column through the run while the body swayed under it - 1-2 squares left of where the idle's collar,
     shoulders and chest sit under the chin, a row lower in 3 frames - so the head is moved onto the body (SEAT, the
     offsets measured per frame against the idle under the chin; tools/art/import_native.py no longer re-steadies
     the run on the head, which would move the body back). Done first, so the clean-ups below see the moved head.
  8. HIT (「受击的时候身体和腿几乎分离」, then 「这里你真不修吗」 on the cloak and 「身体都变形了」): Codex shifted the
     whole upper body 5-7 squares right of the legs (the design's own legs, pasted) and drew its own narrower body
     and cloak; moved back over the legs they still read as another, deformed body. By the user's rule (a casting
     body is the idle's body, only the moved limbs from Codex) the hit frames are the idle: frame 1 with Codex's
     raised forearm and fist (HIT_ARM, taken after moving Codex's body back over the legs, SEAT) in place of the
     idle's hand and feather at the chin (HIT_HAND), frame 2 the idle as it is; both 1 square back (HIT_RECOIL).
--check compares the result with the committed strips instead of writing them; --review DIR writes, per tag, the
delivery and the fixed frames side by side at 4x with every changed square marked.
"""
import argparse
import json
import os
import shutil
import sys
from collections import Counter, deque

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "rakan", "codex_strips")
DESIGN = os.path.join(ROOT, "assets", "source", "native", "rakan_native.png")
OUT = os.path.join(ROOT, "assets", "source", "native")
Z = 8
TAGS = ["idle", "run", "attack", "skill", "skill2", "w_spin", "e_dash", "e_land", "ult", "hit", "dead"]
OUTLINE = (0x16, 0x0A, 0x0E)
COLLAR = (0x8E, 0x0E, 0x14)        # the high collar's dark red (also the leg bands)
WRAP = (0x3B, 0x2F, 0x38)          # the leg wraps
HALO_MAX = 12
HALO_GAP = 3
PIN = 3
GAP_MAX = 3
BLACK_ROWS = (56, 73)
KNEE_ROW = 64
TROUSERS = (0x1E, 0x30, 0x2B)
LEG_MATERIALS = {TROUSERS, (0x3E, 0x63, 0x46), WRAP, COLLAR}
LETTERS = {"A": OUTLINE, "E": (0xF6, 0xC7, 0x9A), "H": (0xE3, 0x9A, 0x62), "G": (0xB0, 0x66, 0x3F),
           "C": COLLAR, "K": WRAP}
# (tag, frame index): (x0, y0, rows) - a letter sets that colour where the square is clear or the outline ('a' only
# where clear), '.' keeps the square
ARMS = {
    # Q 4: the forearm's bracer and hand rise at x 73-81 beside the face; the shoulder's top is at (68-70, 47-49)
    ("skill", 3): (68, 43, ["....A.",
                            "...AHA",
                            "..AEHA",
                            ".AEHA.",
                            "AEHA..",
                            ".HA..."]),
    # Q 5: the forearm runs down-left from the hand at (71-76, 41-46) to (65, 50-51); the shoulder's top is at (59-61,
    # 51-52)
    ("skill", 4): (60, 49, ["..AAAA",
                            ".AEEHA",
                            "AEHHA.",
                            "HHAA..",
                            ]),
}


# (tag, frame index): {"head": (dx, dy)} moves the pasted head, {"body": (dx, dy)} everything but the head and the idle's
# own legs (rows LEGS_ROW and lower, columns from LEGS_LEFT left of the pivot, that equal the idle frame's at the same
# place from the pivot: Codex pasted the design's legs; its cloak beside them is its own, matching here and there by
# chance)
SEAT = {
    ("run", 0): {"head": (-1, 0)}, ("run", 1): {"head": (-1, 1)}, ("run", 2): {"head": (-1, 0)},
    ("run", 3): {"head": (0, 1)}, ("run", 4): {"head": (-1, 0)}, ("run", 5): {"head": (-1, 1)},
    ("run", 6): {"head": (-2, 0)}, ("run", 7): {"head": (-2, 0)},
    ("hit", 0): {"body": (-5, 0), "head": (-3, -1)},
}
LEGS_ROW = 60
LEGS_LEFT = 8
# the hit frames from the idle: (x0, x1, y0, y1) boxes from the pivot (x1, y1 excluded). HIT_HAND: the idle's right hand
# and the golden feather at the chin, cleared in frame 1; HIT_ARM: Codex's raised forearm and fist (frame 1, moved
# back over the legs by SEAT) laid in their place
HIT_HAND = [(3, 12, -13, -8), (3, 12, -8, -3)]
HIT_ARM = [(2, 14, -17, -9)]
HIT_RECOIL = -1
# hit frame 1, after the recoil (cell squares): the shoulder between the idle's chest and Codex's forearm, where the
# ground showed through (skin, like the Q 4-5 upper arms)
HIT_PATCH = [(50, 64, "E"), (50, 65, "E"), (51, 64, "H"), (51, 65, "H"), (52, 64, "H"), (52, 65, "G")]


def _col(x, ys, ch):
    return [(y, x, ch) for y in ys]


# R frame index: [(y, x, letter)] - '#' outline, 'w' wraps, 'c' band, 'f' boots
R_LEGS = {
    0: [(65, 61, "c"), (66, 61, "c"), (71, 60, "#"), (71, 61, "w")],
    1: [(64, 62, "c"), (65, 60, "c"), (65, 61, "c")] + _col(57, range(68, 72), "#"),
    2: [(63, 63, "c"), (64, 63, "c"), (64, 64, "c"), (65, 65, "#")],
    3: [(65, 54, "c"), (66, 54, "c"), (72, 54, "w"), (63, 57, "w")] + _col(53, range(66, 71), "#"),
    4: _col(54, range(64, 71), "#") + _col(55, (64, 65), "c") + _col(55, range(66, 71), "w") + [(72, 53, "#")],
    5: (_col(62, (64, 65), "c") + _col(62, range(66, 73), "w")
        + _col(43, range(65, 72), "#") + _col(44, (65, 66), "c") + _col(44, range(67, 72), "w")
        + _col(45, range(65, 72), "#") + [(72, 44, "#"), (75, 43, "#")]),
    6: (_col(59, (64, 65), "c") + _col(59, range(66, 71), "w")
        + [(64, 44, "c"), (64, 45, "c"), (65, 44, "c")]
        + _col(43, range(66, 71), "#") + _col(44, range(66, 69), "w") + _col(44, (69, 70), "f")
        + _col(45, range(66, 71), "#") + [(71, 44, "#")]),
    7: _col(60, (66, 67), "c") + _col(60, range(68, 71), "w") + [(71, 58, "#")],
}
LEG_COLS = {"#": OUTLINE, "w": WRAP, "c": COLLAR, "f": (0x5C, 0x4A, 0x6A)}

# death frame index: squares of Codex's own head left beside the pasted one (never a pasted-head square)
DEAD_CLEAR = {
    4: [(y, x) for y in range(50, 58) for x in range(67, 70)] + [(58, 69)],
    5: [(y, x) for y in range(54, 59) for x in range(81, 84)] + [(y, x) for y in range(59, 63) for x in (82, 83)],
    6: [(59, 85), (60, 85)],
    7: [(59, 85), (60, 85)],
}


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + p if os.name == "nt" and not p.startswith(pre) else p


def layout(n):
    cols = {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)
    return cols, -(-n // cols)


def head_mask_design(des):
    """The head on the design's canvas (the strips pack's head: the crest, the white hair, the near ear and the face,
    rows 60-75; the feather and the hand by the chin and the collar beside the chin left out)."""
    m = np.zeros(des.shape[:2], bool)
    for r in range(60, 76):
        for c in range(40, 80):
            if not des[r, c, 3]:
                continue
            lr, lc = r - 60, c - 42
            if lr >= 13 and lc >= 26:
                continue
            if lr >= 15 and (lc < 17 or lc > 25):
                continue
            m[r, c] = True
    return m


def components(mask, conn8=True):
    H, W = mask.shape
    seen = np.zeros_like(mask)
    nb = [(dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx] if conn8 else \
        [(1, 0), (-1, 0), (0, 1), (0, -1)]
    out = []
    for y, x in zip(*np.nonzero(mask)):
        if seen[y, x]:
            continue
        q = deque([(y, x)])
        seen[y, x] = True
        pts = []
        while q:
            cy, cx = q.popleft()
            pts.append((cy, cx))
            for dy, dx in nb:
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    q.append((ny, nx))
        out.append(pts)
    return sorted(out, key=len, reverse=True)


def enclosed(op):
    """Clear squares the border cannot reach (4-neighbours)."""
    H, W = op.shape
    clear = ~op
    seen = np.zeros_like(clear)
    q = deque((y, x) for y in range(H) for x in (0, W - 1) if clear[y, x])
    q.extend((y, x) for x in range(W) for y in (0, H - 1) if clear[y, x])
    for y, x in q:
        seen[y, x] = True
    while q:
        cy, cx = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = cy + dy, cx + dx
            if 0 <= ny < H and 0 <= nx < W and clear[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                q.append((ny, nx))
    return clear & ~seen


def find_head(f, head, rects):
    """The pasted head's squares in a frame: the design head (its squares relative to its box), upright or turned a
    quarter, matched exactly near Codex's recorded head box. Returns a mask or None."""
    for k in (0, -1, 1):
        h = np.rot90(head, k)
        pts = np.argwhere(h)
        for (x0, y0) in rects:
            for dy in range(-3, 4):
                for dx in range(-3, 4):
                    oy, ox = y0 + dy, x0 + dx
                    if oy < 0 or ox < 0 or oy + h.shape[0] > f.shape[0] or ox + h.shape[1] > f.shape[1]:
                        continue
                    ok = True
                    for y, x in pts:
                        if not f[oy + y, ox + x, 3] or tuple(f[oy + y, ox + x, :3]) != HEADCOL[k][y, x]:
                            ok = False
                            break
                    if ok:
                        m = np.zeros(f.shape[:2], bool)
                        m[oy + pts[:, 0], ox + pts[:, 1]] = True
                        return m
    return None


HEADCOL = {}


def fix_halo(f, hm):
    op = f[..., 3] > 0
    rest = op & ~hm
    parts = components(rest)
    if not parts:
        return 0
    near = hm.copy()
    for _ in range(HALO_GAP):
        n2 = near.copy()
        n2[1:] |= near[:-1]
        n2[:-1] |= near[1:]
        n2[:, 1:] |= near[:, :-1]
        n2[:, :-1] |= near[:, 1:]
        near = n2
    gone = 0
    for pts in parts[1:]:
        if len(pts) <= HALO_MAX and any(near[y, x] for y, x in pts):
            for y, x in pts:
                f[y, x] = 0
            gone += len(pts)
    return gone


def fix_holes(f, hm):
    op = f[..., 3] > 0
    filled = 0
    for pts in components(enclosed(op), conn8=False):
        by_head = hm is not None and any(hm[max(0, y - 1):y + 2, max(0, x - 1):x + 2].any() for y, x in pts)
        if by_head:
            for y, x in pts:
                f[y, x] = (*COLLAR, 255)
            filled += len(pts)
        elif len(pts) <= PIN:
            for y, x in pts:
                cs = Counter(tuple(f[ny, nx, :3]) for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1))
                             if f[ny, nx, 3])
                f[y, x] = (*cs.most_common(1)[0][0], 255)
            filled += len(pts)
    return filled


def fix_arm(f, spec):
    x0, y0, rows = spec
    n = 0
    for dy, row in enumerate(rows):
        for dx, ch in enumerate(row):
            if ch == ".":
                continue
            y, x = y0 + dy, x0 + dx
            cur = tuple(f[y, x, :3]) if f[y, x, 3] else None
            col = LETTERS[ch.upper()]
            if cur is None or (ch.isupper() and cur == OUTLINE and col != OUTLINE):
                f[y, x] = (*col, 255)
                n += 1
    return n


def fix_r_legs(f, edits):
    for y, x, ch in edits:
        f[y, x] = (*LEG_COLS[ch], 255)
    return len(edits)


def fix_dead_gap(f, hm, clear):
    """Codex's head remnants cleared; then clear runs of at most GAP_MAX squares along a row with the pasted head at
    one end and the body at the other take the collar's dark red."""
    gone = 0
    for y, x in clear:
        if f[y, x, 3] and not hm[y, x]:
            f[y, x] = 0
            gone += 1
    op = f[..., 3] > 0
    n = 0
    for y in range(f.shape[0]):
        x = 1
        while x < f.shape[1] - 1:
            if op[y, x] or not op[y, x - 1]:
                x += 1
                continue
            e = x
            while e < f.shape[1] and not op[y, e]:
                e += 1
            if e < f.shape[1] and e - x <= GAP_MAX and hm[y, x - 1] != hm[y, e]:
                f[y, x:e] = (*COLLAR, 255)
                n += e - x
            x = e
    return gone, n


def fix_black(f):
    op = f[..., 3] > 0
    dark = op & (f[..., :3] == np.array(OUTLINE)).all(-1)
    light = op & ~dark
    p = np.pad(light, 1)
    nb = np.zeros_like(light)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy or dx:
                nb |= p[1 + dy:1 + dy + light.shape[0], 1 + dx:1 + dx + light.shape[1]]
    d = np.pad(dark, 1)
    inner = dark & ~nb & ((d[:-2, 1:-1] & d[2:, 1:-1]) | (d[1:-1, :-2] & d[1:-1, 2:]))
    inner[:BLACK_ROWS[0]] = False
    inner[BLACK_ROWS[1]:] = False
    g = f.copy()
    n = 0
    for y, x in zip(*np.nonzero(inner)):
        if y < KNEE_ROW:
            g[y, x] = (*TROUSERS, 255)
            n += 1
            continue
        win = f[max(0, y - 3):y + 4, max(0, x - 3):x + 4].reshape(-1, 4)
        cs = Counter(tuple(int(v) for v in q[:3]) for q in win if q[3] and tuple(int(v) for v in q[:3]) in LEG_MATERIALS)
        if cs:
            g[y, x] = (*cs.most_common(1)[0][0], 255)
            n += 1
    f[:] = g
    return n


def fix_seat(f, hm, spec, legs):
    """The body block and the head moved by SEAT's offsets (the idle's legs stay; the head on top). Returns the moved
    pixels' count and the head's new mask."""
    H, W = f.shape[:2]
    op = f[..., 3] > 0
    block = op & ~hm & ~legs if "body" in spec else np.zeros_like(op)
    out = f.copy()
    out[hm] = 0
    out[block] = 0

    def put(mask, d, under):
        ys, xs = np.nonzero(mask)
        ny, nx = ys + d[1], xs + d[0]
        ok = (ny >= 0) & (ny < H) & (nx >= 0) & (nx < W)
        ys, xs, ny, nx = ys[ok], xs[ok], ny[ok], nx[ok]
        keep = ~under[ny, nx]
        out[ny[keep], nx[keep]] = f[ys[keep], xs[keep]]
        moved = np.zeros_like(mask)
        moved[ny, nx] = True
        return moved

    if block.any():
        put(block, spec["body"], legs)
    new_hm = put(hm, spec.get("head", (0, 0)), np.zeros_like(hm))
    n = int((out != f).any(-1).sum())
    f[:] = out
    return n, new_hm


def load_strip(tag, cells):
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"rakan_{tag}_1x.png"))).convert("RGBA")).copy()
    cw, ch = cells["cell"]
    n = len(cells["tags"][tag])
    cols, _ = layout(n)
    return a, [(slice((k // cols) * ch, (k // cols + 1) * ch), slice((k % cols) * cw, (k % cols + 1) * cw))
               for k in range(n)]


def build():
    cells = json.load(open(lp(os.path.join(SRC, "rakan_cells.json")), encoding="utf-8"))
    man = json.load(open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8"))["animations"]
    des = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))[Z // 2::Z, Z // 2::Z]
    hmd = head_mask_design(des)
    ys, xs = np.nonzero(hmd)
    box = des[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    head = hmd[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    for k in (0, -1, 1):
        cols = np.rot90(box, k)
        HEADCOL[k] = {(y, x): tuple(int(v) for v in cols[y, x, :3]) for y, x in np.argwhere(np.rot90(head, k))}
    out, log = {}, []
    idle = None
    for tag in TAGS:
        a, slots = load_strip(tag, cells)
        orig = a.copy()
        if tag == "idle":
            idle = (orig[slots[0][0], slots[0][1]].copy(), cells["tags"]["idle"][0]["pivot"])
        for k, (sy, sx) in enumerate(slots):
            f = a[sy, sx]
            rect = man[tag]["frames"][k]["head_rect"]
            hm = find_head(f, head, [(rect[0], rect[1])])
            if hm is None and tag != "idle":
                log.append(f"{tag} {k + 1}: head not found")
            notes = []
            if (tag, k) in SEAT and hm is not None:
                px, py = cells["tags"][tag][k]["pivot"]
                ref = np.roll(np.roll(idle[0], py - idle[1][1], 0), px - idle[1][0], 1)
                legs = (f[..., 3] > 0) & (f == ref).all(-1)
                legs[:LEGS_ROW] = False
                legs[:, :px - LEGS_LEFT] = False
                n, hm = fix_seat(f, hm, SEAT[(tag, k)], legs)
                notes.append(f"seat {SEAT[(tag, k)]} ({n} squares)")
            if tag == "hit":
                px, py = cells["tags"][tag][k]["pivot"]
                ref = np.roll(np.roll(idle[0], py - idle[1][1], 0), px - idle[1][0], 1)
                g = f.copy()
                f[:] = ref
                if k == 0:
                    for x0, x1, y0, y1 in HIT_HAND:
                        f[py + y0:py + y1, px + x0:px + x1] = 0
                    for x0, x1, y0, y1 in HIT_ARM:
                        box = g[py + y0:py + y1, px + x0:px + x1]
                        m = box[..., 3] > 0
                        f[py + y0:py + y1, px + x0:px + x1][m] = box[m]
                f[:] = np.roll(f, HIT_RECOIL, 1)
                if k == 0:
                    for y, x, ch in HIT_PATCH:
                        f[y, x] = (*LETTERS[ch], 255)
                hm = np.roll(find_head(ref, head, [(man["idle"]["frames"][0]["head_rect"][0] + px - idle[1][0],
                                                   man["idle"]["frames"][0]["head_rect"][1] + py - idle[1][1])]),
                             HIT_RECOIL, 1)
                notes.append("the idle" + (" + Codex's raised fist" if k == 0 else "") + f", {HIT_RECOIL:+d} back")
            if tag not in ("idle", "hit") and hm is not None:
                g = fix_halo(f, hm)
                if g:
                    notes.append(f"halo -{g}")
            if (tag, k) in ARMS:
                notes.append(f"arm +{fix_arm(f, ARMS[(tag, k)])}")
            if tag == "ult" and k in R_LEGS:
                notes.append(f"legs {fix_r_legs(f, R_LEGS[k])}")
            if tag == "dead" and hm is not None and k >= 4:
                gone, n = fix_dead_gap(f, hm, DEAD_CLEAR.get(k, []))
                notes.append(f"remnant -{gone}, gap +{n}")
            if tag not in ("idle", "hit"):
                b = fix_black(f)
                if b:
                    notes.append(f"black -{b}")
            if tag not in ("idle", "hit"):
                h = fix_holes(f, hm)
                if h:
                    notes.append(f"holes +{h}")
            if notes:
                log.append(f"{tag} {k + 1}: " + ", ".join(notes))
        out[tag] = (orig, a, slots)
    return cells, out, log


def review(cells, out, d):
    os.makedirs(d, exist_ok=True)
    S = 4
    for tag, (orig, a, slots) in out.items():
        tiles = []
        for sy, sx in slots:
            o, f = orig[sy, sx], a[sy, sx]
            op = (o[..., 3] > 0) | (f[..., 3] > 0)
            yy, xx = np.nonzero(op)
            y0, y1, x0, x1 = max(0, yy.min() - 2), yy.max() + 3, max(0, xx.min() - 2), xx.max() + 3
            pair = []
            for img, mark in ((o, False), (f, True)):
                c = img[y0:y1, x0:x1]
                im = Image.new("RGBA", ((x1 - x0) * S, (y1 - y0) * S), (98, 106, 70, 255))
                im.alpha_composite(Image.fromarray(c).resize(im.size, Image.NEAREST))
                if mark:
                    dr = ImageDraw.Draw(im)
                    diff = np.any(o[y0:y1, x0:x1] != f[y0:y1, x0:x1], -1)
                    for y, x in np.argwhere(diff):
                        dr.rectangle((x * S, y * S, x * S + S - 1, y * S + S - 1), outline=(255, 0, 255, 255))
                pair.append(im)
            t = Image.new("RGB", (pair[0].width * 2 + 6, pair[0].height), (40, 40, 40))
            t.paste(pair[0], (0, 0))
            t.paste(pair[1], (pair[0].width + 6, 0))
            tiles.append(t)
        W = max(t.width for t in tiles)
        H = sum(t.height + 6 for t in tiles)
        sheet = Image.new("RGB", (W, H), (40, 40, 40))
        y = 0
        for t in tiles:
            sheet.paste(t, (0, y))
            y += t.height + 6
        sheet.save(os.path.join(d, f"fix_{tag}.png"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review")
    a = ap.parse_args()
    cells, out, log = build()
    print("\n".join(log))
    if a.review:
        review(cells, out, a.review)
    same = True
    for tag, (_, img, _) in out.items():
        big = Image.fromarray(np.repeat(np.repeat(img, Z, 0), Z, 1))
        path = os.path.join(OUT, f"rakan_{tag}.png")
        if a.check:
            old = np.asarray(Image.open(lp(path)).convert("RGBA"))
            same &= np.array_equal(old, np.asarray(big))
        else:
            big.save(lp(path))
    if a.check:
        print("same as the committed files" if same else "DIFFERS from the committed files")
        sys.exit(0 if same else 1)
    shutil.copyfile(lp(os.path.join(SRC, "rakan_cells.json")), lp(os.path.join(OUT, "rakan_cells.json")))
    print("written")


if __name__ == "__main__":
    main()
