"""(tools/art/import_native.py TIDY; the user: 「风女 莫甘娜 不干净的黑色块也太多了」「莫甘娜头部有很多多余的方块」, approved 「风女莫甘娜也没问题」)
Tidy Morgana's game frames.

    tidy(tag, k, frame) -> frame        (HxWx4 uint8, odd size, pivot = centre pixel, soles row = pivot + 11)

What it does, in this order (all coordinates pivot-relative, x right, y down):
  1. HEAD    every idle/run/attack/skill/skill2/ult/hit frame gets one clean head: the approved idle head,
             tidied by hand (HEAD below), pasted at the frame's own eye position; the frame's old hair just
             outside the horns is cleared.  skill2 1-4 keep their raised arm, hit 0 its closed eyes
             (HEAD_KEEP).  The dead tag keeps its own (smaller, tilted, lying) heads: SPECK_ZONE + EDITS.
  2. EDITS   explicit per-frame edits (EDITS), each checked against the colour it expects before painting.
  3. MUD     the mauve (150,108,150) anti-alias left-overs take their neighbours' colour.
  4. SPECKS  1-2 px islands of gold / skin / white inside another material take that material's colour.
  5. BLACK   near-black pixels inside the silhouette (not 4-next to transparency) take the darkest
             neighbouring shade of the material they sit in (purple ramp for hair/gown/wing; skin -> skin
             shade; gold -> dark gold).  A black line between two light materials (skin|gold) stays.
             Faces (the pasted head, FACE_KEEP boxes, every eye pixel) are never touched.
  6. GROUND  nothing below the soles row (pivot + 11): the lying dead frames are lifted, the rest clipped.
  7. CRUMBS  loose opaque pieces of up to 8 px (not joined to the body) are cleared.
  8. RING    one 1-px near-black outline: edge pixels darker than lum 40 become the outline colour and
             strips.complete_outline closes every gap (the hem's bottom row takes the outline).
"""
import os
import sys

import numpy as np

G = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # the repo
sys.path.insert(0, G + "/.claude/skills/tfm2-hero-mod/scripts")
import strips  # noqa: E402

# ------------------------------------------------------------------------------------------- palette
PAL = {
    'K': (15, 1, 23), 'k': (13, 1, 19), 'j': (19, 1, 29),                         # near-blacks
    '1': (28, 13, 41), '2': (32, 16, 46), '3': (40, 20, 57), '4': (49, 23, 67),   # purple ramp, dark ...
    'w': (46, 30, 47), 'p': (59, 27, 79), 'q': (83, 33, 102), 'r': (87, 34, 107),
    's': (96, 35, 113), 'u': (77, 45, 81),                                          # ... to light
    'm': (118, 27, 118), 'M': (162, 30, 147),                                       # magenta (wing tips)
    'S': (242, 214, 234), 'n': (173, 130, 139), 'W': (248, 247, 249),               # skin, shade, white
    'v': (150, 108, 150),                                                           # mauve anti-alias mud
    'g': (209, 169, 105), 'G': (211, 173, 110), 'L': (231, 192, 138),               # gold
    'b': (157, 115, 71), 'B': (129, 91, 67), 'd': (93, 62, 49),                     # dark gold / brown
    'E': (200, 60, 166),                                                            # eyes
}
CH = {v: c for c, v in PAL.items()}
OUTLINE = PAL['K']
BLACK = set('Kkj')
MAT = {}
for _c in '1234wpqrsu':
    MAT[_c] = 'purple'
for _c in 'mM':
    MAT[_c] = 'magenta'
for _c in 'SWn':
    MAT[_c] = 'skin'
for _c in 'gGLbBd':
    MAT[_c] = 'gold'
MAT['v'] = 'mud'
MAT['E'] = 'eye'
for _c in BLACK:
    MAT[_c] = 'black'
DARKEST = {'skin': 'n', 'gold': 'b', 'magenta': 'm'}
SOLES = 11


def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


# ------------------------------------------------------------------------------- the clean head
# The approved idle head (idle 0: left eye's top-left pixel at (-2,-18)), tidied by hand.
# x = -11..7, y = -33..-14.  '.' = clear the frame there, '?' = keep the frame's pixel, else paint.
HEAD_X0, HEAD_Y0 = -11, -33
HEAD_EYE = (-2, -18)
HEAD = [
    "...........K.......",  # -33
    "..........KbK......",  # -32
    "....KK....KgK......",  # -31
    "...KbgK...KgK......",  # -30
    "..KgggK...KggK.....",  # -29
    "..Kggb1KKK1bggK....",  # -28
    "..KgGb1pqp1bgggK...",  # -27
    ".K133GL4pppp1gggK..",  # -26
    ".K212GG4pppp1gGbK..",  # -25
    ".K2gggb1ppp11ggbK..",  # -24
    ".K332bg1ppp11bb11K.",  # -23
    ".K332221pp4412213K.",  # -22
    "?K33222ppp1SS1122K?",  # -21
    "?K32222ppSSSSSS12K?",  # -20
    "?K2SSS2pSKKSSKK11??",  # -19
    "?K23nS2pSWESSWE12??",  # -18
    "?K44222pSEESSEE2p??",  # -17
    "?K411pp1SSSSSSS41??",  # -16
    "?K1ppp1p1SSSmSS11??",  # -15
    "?Kpp111411SSSS112??",  # -14
]
assert all(len(r) == 19 for r in HEAD)

# head offset (dx, dy) from idle 0 for frames whose eyes cannot be found (closed / no eyes)
HEAD_AT = {('hit', 0): (-1, 0)}
# frames that keep their own head: the whole dead tag (its heads are drawn 3-6 px shorter, falling/tilted/
# lying; the idle head pasted into dead 1 made it pop 4 px taller between dead 0 and dead 2)
NO_HEAD = {('dead', 0), ('dead', 1), ('dead', 2), ('dead', 3), ('dead', 4), ('dead', 5), ('dead', 6), ('dead', 7)}
# template cells (x, y in idle-0 head coordinates) left to the frame: a raised arm beside the head
HEAD_KEEP = {('skill2', k): {(-10, y) for y in range(-22, -13)} | {(-9, -14)} for k in (1, 2, 3, 4)}
# hit 0 keeps its own closed eyes (a pained look): the eye cells come from the frame
HEAD_KEEP[('hit', 0)] = {(x, y) for x in (-2, -1, 2, 3) for y in (-19, -18, -17)}
# faces of the frames that keep their own head: (x0, y0, x1, y1) boxes nobody repaints
FACE_KEEP = {
    ('hit', 0): [(-3, -18, 2, -18)],          # closed eyes
    ('dead', 0): [(-6, -24, 1, -20)],         # tilted face
    ('dead', 1): [(-2, -20, 5, -18)],         # brows + eyes
    ('dead', 2): [(3, -13, 10, -11)],         # brows + eyes
    ('dead', 3): [(8, -8, 15, -1)],           # closed eyes, mouth
    ('dead', 4): [(5, -3, 13, 4)],
    ('dead', 5): [(8, -3, 15, 5)],
    ('dead', 6): [(10, -1, 17, 6)],
}
# speck-rule zones for frames that keep their own head: (x0, y0, x1, y1)
SPECK_ZONE = {('dead', 0): (-18, -34, 6, -17), ('dead', 1): (-11, -31, 9, -14), ('dead', 2): (-6, -25, 14, -5)}
# explicit per-frame edits: (x, y, expected chars or None for "any", new char or '.' to clear)
_NECK = [(-3, -13, 'j', '1'), (-2, -13, 'n', '1'), (-1, -13, 'v', 'n'), (0, -13, 'K', 'n'), (1, -13, 'j', '1')]
EDITS = {
    # idle: the design's muddy neck -> skin shade under the chin, hair either side, the gold collar below
    ('idle', 0): _NECK, ('idle', 1): _NECK, ('idle', 5): _NECK,
    ('idle', 2): [(x, y + 1, w, n) for x, y, w, n in _NECK],
    ('idle', 3): [(x, y + 1, w, n) for x, y, w, n in _NECK],
    ('idle', 4): [(x, y + 1, w, n) for x, y, w, n in _NECK],
    ('dead', 0): [
        (-10, -32, 'G', '.'),                 # lone gold square outside the horn's outline
        (1, -23, 'W', 'S'),                   # white square right of the right eye
        (-13, -23, '2', 'g'),                 # hair speck inside the left horn
        (-8, -19, 'W', 'S'),                  # ear: skin, not white
    ],
    ('dead', 1): [
        (-6, -17, 'W', 'p'), (-5, -17, 'W', 'p'),   # the ear's white squares at chin level -> hair
        (-7, -25, '2', 'g'),                  # hair speck inside the left horn
        (-8, -23, 'd', 'b'), (-7, -23, 'd', 'b'),   # brown -> the horn's dark gold
    ],
    ('dead', 2): [
        (7, -16, 'n', '2'),                   # skin speck in the hair at the right horn's base
        (8, -16, 'd', 'b'), (9, -16, 'd', 'b'),     # brown -> the horn's dark gold
    ],
    # ult 2/3 rise to the canvas top (pivot - 44): the pasted horn tips would be cut flat there, so the
    # right horn ends one row lower with its outline on the top row
    ('ult', 2): [(0, -45, 'K', '.'), (0, -44, 'b', 'K')],
    ('ult', 3): [(0, -46, 'K', '.'), (-1, -45, 'K', '.'), (0, -45, 'b', '.'), (1, -45, 'K', '.'),
                 (0, -44, 'g', 'K')],
}


HEAD_OFF = {}
HAIRISH = set('Kkj1234wpqu')            # hair / outline colours (not the wing's r, s, m, M)


def _eye(a):
    """Top-left pixel of the left eye (pivot-relative), or None."""
    cy, cx = a.shape[0] // 2, a.shape[1] // 2
    m = (a[..., 3] > 0) & (a[..., 0] == 200) & (a[..., 1] == 60) & (a[..., 2] == 166)
    ys, xs = np.nonzero(m)
    if not len(xs):
        return None
    pts = sorted(zip((xs - cx).tolist(), (ys - cy).tolist()))
    lx = pts[0][0]
    left = [p for p in pts if p[0] <= lx + 1]
    return (min(p[0] for p in left), min(p[1] for p in left))


def _char(a, y, x):
    if a[y, x, 3] == 0:
        return '.'
    return CH.get(tuple(int(v) for v in a[y, x, :3]), '?')


def _clear4(op):
    p = np.pad(op, 1)
    return ~(p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:])


def head_offset(tag, k, a):
    if (tag, k) in NO_HEAD:
        return None
    if (tag, k) in HEAD_AT:
        return HEAD_AT[(tag, k)]
    e = _eye(a)
    if e is None:
        return None
    return (e[0] - HEAD_EYE[0], e[1] - HEAD_EYE[1])


def _paste_head(a, tag, k, log):
    H, W = a.shape[:2]
    cy, cx = H // 2, W // 2
    painted = np.zeros((H, W), bool)
    off = head_offset(tag, k, a)
    if off is None:
        return painted
    dx, dy = off
    HEAD_OFF[(tag, k)] = off
    keep = HEAD_KEEP.get((tag, k), set())
    ring = np.zeros((H, W), bool)
    cover = np.zeros((H, W), bool)
    n = clipped = 0
    for r, row in enumerate(HEAD):
        for c, ch in enumerate(row):
            hx, hy = HEAD_X0 + c, HEAD_Y0 + r
            if ch == '?' or (hx, hy) in keep:
                continue
            X, Y = cx + hx + dx, cy + hy + dy
            if not (0 <= X < W and 0 <= Y < H):
                clipped += ch != '.'
                continue
            cover[Y, X] = True
            old = a[Y, X].copy()
            if ch == '.':
                a[Y, X] = 0
            else:
                a[Y, X, :3] = PAL[ch]
                a[Y, X, 3] = 255
                painted[Y, X] = True
                ring[Y, X] = ch == 'K'
            n += int((old != a[Y, X]).any())
    # the frame's old hair just outside the head's top (beside the horns and crown): cleared, so no
    # one-pixel strand stands apart from the new outline
    stray = 0
    for hy in range(HEAD_Y0, -21):
        for hx in (HEAD_X0 - 2, HEAD_X0 - 1, HEAD_X0 + 19, HEAD_X0 + 20):
            X, Y = cx + hx + dx, cy + hy + dy
            if 0 <= X < W and 0 <= Y < H and _char(a, Y, X) in HAIRISH:
                a[Y, X] = 0
                stray += 1
    # the head's outline where the frame's own hair/wing continues past it: no black line inside hair
    clear4 = _clear4(a[..., 3] > 0)
    out4 = _clear4(cover)
    soft = 0
    for y, x in zip(*np.nonzero(ring & ~clear4 & out4)):
        nb = [(y + v, x + u) for v, u in ((-1, 0), (1, 0), (0, -1), (0, 1))
              if 0 <= y + v < H and 0 <= x + u < W and not cover[y + v, x + u]]
        if any(_char(a, yy, xx) not in BLACK | {'.'} for yy, xx in nb):
            a[y, x, :3] = PAL['1']
            soft += 1
    log['head'] = {'offset': [int(dx), int(dy)], 'pixels': n + stray, 'outline_into_hair': soft}
    if clipped:
        log['head']['clipped_off_array'] = int(clipped)   # pass a frame with a wider margin
    return painted


def _vote(a, y, x, skip):
    H, W = a.shape[:2]
    votes = {}
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if not (dy or dx):
                continue
            yy, xx = y + dy, x + dx
            if 0 <= yy < H and 0 <= xx < W:
                c = _char(a, yy, xx)
                if c in ('.', '?') or c in skip:
                    continue
                votes[c] = votes.get(c, 0) + (1 if dy and dx else 2)
    return max(votes, key=votes.get) if votes else None


def _mud(a, protect, log):
    n = 0
    for y, x in zip(*np.nonzero((a[..., 3] > 0) & ~protect)):
        if _char(a, y, x) == 'v':
            new = _vote(a, y, x, {'v'} | BLACK)
            if new:
                a[y, x, :3] = PAL[new]
                n += 1
    log['mud'] = n


def _specks(a, protect, zone, log):
    """1-2 px islands of gold / skin inside another material (all 8 neighbours opaque, none the same
    material) take the colour of the material round them."""
    H, W = a.shape[:2]
    op = a[..., 3] > 0
    mat = np.full((H, W), '.', dtype=object)
    for y, x in zip(*np.nonzero(op)):
        mat[y, x] = MAT.get(_char(a, y, x), '.')
    n = 0
    for m in ('gold', 'skin'):
        lab, cnt = strips.label(mat == m)
        for i in range(1, cnt + 1):
            ys, xs = np.nonzero(lab == i)
            if len(ys) > 2 or protect[ys, xs].any() or not zone[ys, xs].all():
                continue
            ok = all(0 <= y + v < H and 0 <= x + u < W and op[y + v, x + u]
                     for y, x in zip(ys, xs) for v in (-1, 0, 1) for u in (-1, 0, 1))
            if not ok:
                continue
            for y, x in zip(ys, xs):
                new = _vote(a, y, x, {c for c, mm in MAT.items() if mm in (m, 'mud')})
                if new and new not in BLACK:
                    a[y, x, :3] = PAL[new]
                    n += 1
    log['specks'] = n


def _recolor_black(a, protect, log):
    """Interior near-black -> darkest neighbouring shade of the surrounding material."""
    H, W = a.shape[:2]
    changed = 0
    for _ in range(16):
        op = a[..., 3] > 0
        clear4 = _clear4(op)
        todo = []
        for y, x in zip(*np.nonzero(op & ~clear4 & ~protect)):
            if _char(a, y, x) not in BLACK:
                continue
            votes = {}
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if (dy or dx) and 0 <= yy < H and 0 <= xx < W:
                        c = _char(a, yy, xx)
                        if c in ('.', '?') or c in BLACK:
                            continue
                        votes.setdefault(MAT.get(c, 'x'), []).append(c)
            if not votes:
                continue
            if 'purple' in votes or 'magenta' in votes:
                new = min(votes.get('purple', []) + votes.get('magenta', []), key=lambda c: lum(PAL[c]))
            else:
                light = {m for m in votes if m in ('skin', 'gold')}
                if len(light) != 1:
                    continue                   # a line between two light materials draws something
                new = DARKEST[light.pop()]
            todo.append((y, x, new))
        if not todo:
            break
        for y, x, new in todo:
            a[y, x, :3] = PAL[new]
        changed += len(todo)
    log['black'] = changed


def _crumbs(a, log):
    lab, cnt = strips.label(a[..., 3] > 0)
    n = 0
    for i in range(1, cnt + 1):
        m = lab == i
        if m.sum() <= 8:
            a[m] = 0
            n += int(m.sum())
    log['crumbs'] = n


def _edits(a, tag, k, log):
    cy, cx = a.shape[0] // 2, a.shape[1] // 2
    done, skipped = 0, []
    for x, y, want, new in EDITS.get((tag, k), []):
        Y, X = cy + y, cx + x
        if not (0 <= Y < a.shape[0] and 0 <= X < a.shape[1]):
            skipped.append([x, y, 'off'])
            continue
        have = _char(a, Y, X)
        if want is not None and have not in want:
            skipped.append([x, y, have])
            continue
        if new == '.':
            a[Y, X] = 0
        else:
            a[Y, X, :3] = PAL[new]
            a[Y, X, 3] = 255
        done += 1
    log['edits'] = done
    if skipped:
        log['edits_skipped'] = skipped


def _ground(a, tag, protect, log):
    feet = a.shape[0] // 2 + SOLES
    ys = np.nonzero((a[..., 3] > 0).any(1))[0]
    lift = 0
    if tag == 'dead' and len(ys) and ys.max() > feet:
        lift = int(ys.max() - feet)
        a[:-lift] = a[lift:].copy()
        a[-lift:] = 0
        protect[:-lift] = protect[lift:].copy()
        protect[-lift:] = False
    below = int((a[feet + 1:, :, 3] > 0).sum())
    a[feet + 1:] = 0
    log['ground'] = {'lifted': lift, 'clipped': below}


def _ring(a, protect, log):
    H, W = a.shape[:2]
    op = a[..., 3] > 0
    edge = op & _clear4(op)
    L = strips.lum(a[..., :3])
    isk = (a[..., :3] == np.array(OUTLINE, a.dtype)).all(-1)
    dark = edge & (L < 40) & ~isk & ~protect
    a[dark, :3] = OUTLINE
    out, added, darkened = strips.complete_outline(a, color=OUTLINE, dark=40, feet=H // 2 + SOLES,
                                                    keep=protect)
    a[:] = out
    border = np.zeros((H, W), bool)
    border[0, :] = border[-1, :] = border[:, 0] = border[:, -1] = True
    bl = border & (a[..., 3] > 0) & (strips.lum(a[..., :3]) >= 40) & ~protect
    a[bl, :3] = OUTLINE
    log['ring'] = {'edge_to_outline': int(dark.sum()), 'added': added, 'soles': darkened,
                   'border': int(bl.sum())}


def _head_zone(a, tag, k):
    """Where the speck rule may act: round the (pasted) head, from above the horns to the collar."""
    H, W = a.shape[:2]
    cy, cx = H // 2, W // 2
    z = np.zeros((H, W), bool)
    if (tag, k) in SPECK_ZONE:
        x0, y0, x1, y1 = SPECK_ZONE[(tag, k)]
        z[max(0, cy + y0):cy + y1 + 1, max(0, cx + x0):cx + x1 + 1] = True
        return z
    off = HEAD_OFF.get((tag, k))
    if off is None:
        return z
    dx, dy = off
    z[max(0, cy - 36 + dy):max(0, cy - 13 + dy), max(0, cx - 14 + dx):max(0, cx + 11 + dx)] = True
    return z


def _face_protect(a, tag, k):
    H, W = a.shape[:2]
    cy, cx = H // 2, W // 2
    m = (a[..., 3] > 0) & (a[..., 0] == 200) & (a[..., 1] == 60) & (a[..., 2] == 166)
    for x0, y0, x1, y1 in FACE_KEEP.get((tag, k), []):
        m[max(0, cy + y0):cy + y1 + 1, max(0, cx + x0):cx + x1 + 1] = True
    return m


def tidy(tag, k, frame, log=None):
    a = np.array(frame, dtype=np.uint8, copy=True)
    assert a.ndim == 3 and a.shape[2] == 4 and a.shape[0] % 2 == 1 and a.shape[1] % 2 == 1
    log = {} if log is None else log
    a[a[..., 3] < 128] = 0
    a[a[..., 3] >= 128, 3] = 255
    face = _face_protect(a, tag, k)
    head = _paste_head(a, tag, k, log)
    _edits(a, tag, k, log)
    protect = face | head
    _mud(a, protect, log)
    _specks(a, protect, _head_zone(a, tag, k), log)
    _recolor_black(a, protect, log)
    _ground(a, tag, face, log)
    _crumbs(a, log)
    _ring(a, face, log)
    return a
