"""(tools/art/import_native.py TIDY; the user: 「风女 莫甘娜 不干净的黑色块也太多了」「风女的武器待机的姿势看起来少了一块」, approved 「风女莫甘娜也没问题」)
Tidy Janna's (league_janna) game frames: fewer dirty black blocks, a whole staff in the idle.

    tidy(tag, k, frame, log=None) -> frame
        frame: HxWx4 uint8, odd size, pivot = centre pixel, soles row = centre + 11 (the sheet's cells,
        trimmed and centred). Returns a new array of the same shape. Deterministic, no randomness.

Order of work
  1. explicit PRE edits keyed by (tag, frame): the idle staff (head refill, collar-to-hand shaft, the lower
     shaft below the hand), the hit ribbon bridge. Every pixel is checked against the colour it is expected
     to have and skipped (logged) when it differs.
  2. rule - interior black: near-black outline colours that are not on the silhouette ring (not 4-next to a
     clear pixel) are recoloured with the shade of the material they sit in:
        * pixels of solid clumps (2x2 black) take the material reached first from the clump's edge (BFS);
          one 1-px black line is kept where two materials meet inside the clump or the clump touches
          another material;
        * 1-px black lines/specks inside ONE material take that material's darkest shade; a 1-px line with
          different materials on opposite sides is a real separation line and stays; black lines in skin
          (limb / finger gaps) stay.
     The face (a box round the iris colour) is never touched.
  3. rule - stray squares: a pixel (or 2-px pair) of a material none of its neighbours share, sitting
     inside hair or skin, takes the surrounding colour.
  4. explicit POST edits (hand fixes after the rules, same expected-colour check).
  5. the outline is closed again (strips.complete_outline: new outline pixels only on clear pixels, never
     below the soles row) and nothing is left below the soles row.
"""
import os
import sys
import numpy as np

_G = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # the repo
sys.path.insert(0, _G + "/.claude/skills/tfm2-hero-mod/scripts")
import strips  # noqa: E402

# ----------------------------------------------------------------------------- palette (all from the sprite)
C = {
    '#': (2, 1, 20), '%': (2, 2, 33), '&': (3, 3, 37),             # outline near-blacks
    'W': (253, 253, 253), 'L': (183, 213, 253), 'l': (181, 211, 251), 'c': (80, 203, 250),
    'u': (81, 138, 214), 'v': (57, 107, 183), 'D': (4, 42, 112), 'N': (1, 11, 78), 'n': (1, 11, 62),
    'i': (2, 48, 203),                                               # cloth / staff blues
    'H': (253, 244, 191), 'h': (253, 232, 166), 'y': (245, 209, 134), 'B': (196, 149, 97),
    'b': (189, 136, 85), 'd': (105, 54, 20),                         # hair (d = its strand dark)
    'k': (56, 43, 34),                                               # dark brown (shaft sides, strand gaps)
    's': (253, 220, 192), 't': (169, 145, 124),                      # skin
    'G': (238, 160, 7), 'g': (218, 160, 29), 'o': (175, 93, 14),     # gold
    'I': (3, 51, 207),                                               # near-eye iris (face marker)
}
CH = {v: k for k, v in C.items()}
BLACKS = {C['#'], C['%'], C['&']}
OUT = C['#']
MAT = {}
for ch in 'WLlcuvDNni':
    MAT[C[ch]] = 'cloth'
for ch in 'HhyBbd':
    MAT[C[ch]] = 'hair'
for ch in 'st':
    MAT[C[ch]] = 'skin'
for ch in 'Ggo':
    MAT[C[ch]] = 'gold'
MAT[C['I']] = 'face'
# shade for a recoloured black: (1-px line inside the material, clump edge, clump core)
SHADE = {'cloth': ('v', 'v', 'D'), 'hair': ('d', 'b', 'd'), 'skin': ('t', 't', 't'),
         'gold': ('o', 'o', 'o'), 'face': ('t', 't', 't')}
STRAY_IN = ('hair', 'skin')
N4 = ((-1, 0), (1, 0), (0, -1), (0, 1))
N8 = tuple((dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx)
OPP = ((0, 1), (1, 0), (1, 1), (1, -1))


def _key(px):
    return (int(px[0]), int(px[1]), int(px[2]))


# ----------------------------------------------------------------------------- explicit edits
# Coordinates are pivot-relative (x right, y down) in idle 0; idle 2-4 are the same drawing 1 row lower.
IDLE_DY = {0: 0, 1: 0, 2: 1, 3: 1, 4: 1, 5: 0}

# (x, y, expected char or '#' for any outline black or '.' for clear, new char or '.' to clear)
IDLE_PRE = [
    # --- staff head: the crescent's middle was a 14-px black hole (read as a bite out of the head). Refill it
    #     as the blade face (as Codex draws the same pose in skill2 0), keep a small diagonal notch (11..12,-25),
    #     (11,-24) so it still reads as a crescent, and soften the black bar under the blade.
    (10, -26, '#', 'v'), (11, -26, '#', 'u'), (12, -26, '#', 'c'),
    (10, -25, '#', 'u'), (11, -25, '#', 'n'), (12, -25, '#', 'n'),
    (10, -24, '#', 'u'), (11, -24, '#', 'n'), (12, -24, '#', 'u'),
    (11, -23, '#', 'u'), (12, -23, '#', 'u'),
    (11, -22, '#', 'v'), (12, -22, '#', 'v'), (13, -22, '#', 'D'),
    # --- the gold spiral under the head: hair/blue specks on the shaft -> gold
    (12, -20, '#', 'o'), (11, -19, 'b', 'o'),
    # --- shaft from the spiral to the hand: one continuous 2-px line, light gold left, dark gold right
    (9, -17, 'N', 'g'), (10, -17, 'h', 'o'),
    (10, -16, 'D', 'g'), (11, -16, 'g', 'o'),
    (8, -13, 'D', 'g'),
    (8, -12, 'i', 'g'), (9, -12, '#', 'o'),
    # --- shaft below the hand (was missing): continues down-left in front of the drape to the butt (5,-4)
    (7, -10, 'k', 'g'), (8, -10, 'k', 'o'),
    (6, -9, '#', 'g'), (7, -9, 'u', 'o'),
    (6, -8, '#', 'g'), (7, -8, 'u', 'o'),
    (5, -7, 'l', 'g'), (6, -7, 'v', 'o'),
    (5, -6, 'l', 'g'), (6, -6, 'v', 'o'),
    (5, -5, '#', 'g'), (6, -5, 'b', 'o'),
    # --- the black mass between the hair and the staff: the hair lock right of the face goes on down,
    #     the ribbon off the staff head goes on down beside the shaft, one 1-px black line between them
    (5, -17, '#', 'b'), (7, -17, '#', 'u'),
    (5, -16, '#', 'B'), (6, -16, '#', 'b'), (8, -16, '#', 'u'),
    (8, -15, '#', 'u'),
    (5, -12, '#', 'b'), (6, -12, '#', 'b'),
]
IDLE_POST = [
    # left skirt panel: the rest of the black band becomes the panel's blue; one black line stays over the hem
    (-9, -4, '#', 'v'), (-8, -4, '#', 'v'), (-7, -4, '#', 'v'), (-8, -3, 'o', '#'),
    # bodice: one black line (x -3) between the left sleeve and the bodice, the rest in the bodice's blues
    (-3, -10, 'v', '#'), (-2, -11, '#', 'D'), (-2, -10, '#', 'v'), (-1, -10, '#', 'u'),
]
HIT_PRE = {
    # the trailing left ribbon tip floated 2 columns off the skirt: bridge it with the ribbon's light blue
    0: [(-11, -2, '.', 'l'), (-10, -2, '.', 'l'), (-9, -2, '#', 'l'), (-11, -3, '.', '#'), (-10, -1, '.', '#')],
    1: [(-14, -2, '#', 'L'), (-13, -2, '#', 'L'), (-12, -2, '.', 'L'), (-11, -2, '#', 'L'),
        (-12, -3, '.', '#'), (-12, -1, '.', '#')],
}
POST = {}


def _apply(f, edits, dy, log, tag):
    H, W = f.shape[:2]
    cy, cx = H // 2, W // 2
    n = 0
    for x, y, exp, new in edits:
        yy, xx = y + dy + cy, x + cx
        if not (0 <= yy < H and 0 <= xx < W):
            log.append(f"{tag}: skip ({x},{y + dy}) off canvas")
            continue
        cur = None if f[yy, xx, 3] == 0 else _key(f[yy, xx, :3])
        if exp == '.':
            ok = cur is None
        elif exp == '#':
            ok = cur in BLACKS
        else:
            ok = cur == C[exp]
        if not ok:
            log.append(f"{tag}: skip ({x},{y + dy}) found {CH.get(cur, cur)} expected {exp}")
            continue
        if new == '.':
            f[yy, xx] = 0
        else:
            f[yy, xx, :3] = C[new]
            f[yy, xx, 3] = 255
        n += 1
    return n


# ----------------------------------------------------------------------------- helpers
def _black(f):
    k = f[..., 0].astype(np.int32) * 65536 + f[..., 1].astype(np.int32) * 256 + f[..., 2]
    m = np.zeros(f.shape[:2], bool)
    for c in BLACKS:
        m |= k == c[0] * 65536 + c[1] * 256 + c[2]
    return m & (f[..., 3] > 0)


def _ring4(op):
    p = np.pad(op, 1)
    return op & ~(p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:])


def _face_box(f):
    H, W = f.shape[:2]
    m = (f[..., 3] > 0) & (f[..., :3] == np.array(C['I'], np.uint8)).all(-1)
    box = np.zeros((H, W), bool)
    if m.any():
        ys, xs = np.nonzero(m)
        box[max(0, ys.min() - 2):ys.max() + 3, max(0, xs.min() - 2):xs.max() + 3] = True
    return box


def _matmap(f):
    H, W = f.shape[:2]
    mm = np.empty((H, W), object)
    for y in range(H):
        for x in range(W):
            mm[y, x] = MAT.get(_key(f[y, x, :3])) if f[y, x, 3] else None
    return mm


# ----------------------------------------------------------------------------- rule: interior black
def _recolour_black(f, keep, st, clumps_only=False):
    H, W = f.shape[:2]
    op = f[..., 3] > 0
    blk = _black(f)
    cand = blk & ~_ring4(op) & ~keep
    mm = _matmap(f)
    new = f.copy()

    def mat(y, x):
        return mm[y, x] if 0 <= y < H and 0 <= x < W and not blk[y, x] else None

    sq = blk[:-1, :-1] & blk[1:, :-1] & blk[:-1, 1:] & blk[1:, 1:]
    clump = np.zeros((H, W), bool)
    clump[:-1, :-1] |= sq
    clump[1:, :-1] |= sq
    clump[:-1, 1:] |= sq
    clump[1:, 1:] |= sq
    clump &= cand

    # multi-source BFS from the material pixels into the candidate blacks (4-connected)
    lab = {}
    dist = {}
    front = []
    for y, x in zip(*np.nonzero(cand)):
        v = {}
        for dy, dx in N4:
            m = mat(y + dy, x + dx)
            if m and m != 'face':
                v[m] = v.get(m, 0) + 2
        for dy, dx in N8:
            if dy and dx:
                m = mat(y + dy, x + dx)
                if m and m != 'face':
                    v[m] = v.get(m, 0) + 1
        if v:
            lab[(y, x)] = max(sorted(v), key=lambda m: v[m])
            dist[(y, x)] = 1
            front.append((y, x))
    d = 1
    while front:
        nxt = {}
        for y, x in front:
            for dy, dx in N4:
                q = (y + dy, x + dx)
                if 0 <= q[0] < H and 0 <= q[1] < W and cand[q] and q not in dist:
                    nxt.setdefault(q, {})
                    nxt[q][lab[(y, x)]] = nxt[q].get(lab[(y, x)], 0) + 1
        d += 1
        front = sorted(nxt)
        for q in front:
            v = nxt[q]
            lab[q] = max(sorted(v), key=lambda m: v[m])
            dist[q] = d

    for (y, x) in sorted(lab):
        m = lab[(y, x)]
        if clump[y, x]:
            sep = False
            for dy, dx in ((1, 0), (0, 1)):
                q = (y + dy, x + dx)
                if q in lab and lab[q] != m:
                    sep = True
            for dy, dx in N4:
                m2 = mat(y + dy, x + dx)
                if m2 and m2 not in (m, 'face'):
                    sep = True
            if sep:
                st['clump_line_kept'] += 1
                continue
            new[y, x, :3] = C[SHADE[m][1 if dist[(y, x)] == 1 else 2]]
            st['clump'] += 1
            continue
        # 1-px line / speck
        if clumps_only:
            continue
        sep = False
        for dy, dx in OPP:
            ma, mb = mat(y + dy, x + dx), mat(y - dy, x - dx)
            if ma and mb and ma != mb:
                sep = True
        mats = {mat(y + dy, x + dx) for dy, dx in N8} - {None}
        if mats == {'skin'} or 'face' in mats:
            sep = True                      # limb / finger gaps, lines next to the face
        if sep:
            st['line_kept'] += 1
            continue
        new[y, x, :3] = C[SHADE[m][0]]
        st['line'] += 1
    return new


# ----------------------------------------------------------------------------- rule: stray squares
def _strays(f, keep, st):
    H, W = f.shape[:2]
    op = f[..., 3] > 0
    blk = _black(f)
    mm = _matmap(f)
    new = f.copy()
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            own = mm[y, x]
            if keep[y, x] or not op[y, x] or blk[y, x] or own in (None, 'face'):
                continue
            nb = [(y + dy, x + dx) for dy, dx in N8]
            same = [p for p in nb if op[p] and not blk[p] and mm[p] == own]
            if len(same) > 1:
                continue
            if len(same) == 1:
                p = same[0]
                pn = [(p[0] + dy, p[1] + dx) for dy, dx in N8]
                if sum(1 for q in pn if 0 <= q[0] < H and 0 <= q[1] < W and op[q] and not blk[q]
                       and mm[q] == own) > 1:
                    continue
            cnt = {}
            for p in nb:
                if op[p] and not blk[p] and mm[p]:
                    cnt[mm[p]] = cnt.get(mm[p], 0) + 1
            if sum(1 for p in nb if op[p]) < 7 or not cnt:
                continue
            m, k = max(sorted(cnt.items()), key=lambda t: t[1])
            if m not in STRAY_IN or k < 5 or m == own:
                continue
            cols = {}
            for p in nb:
                if op[p] and not blk[p] and mm[p] == m:
                    c = _key(f[p][:3])
                    cols[c] = cols.get(c, 0) + (2 if (p[0] == y or p[1] == x) else 1)
            new[y, x, :3] = max(sorted(cols), key=lambda c: cols[c])
            st['stray'] += 1
    return new


# ----------------------------------------------------------------------------- entry point
def tidy(tag, k, frame, log=None):
    f = np.array(frame, np.uint8, copy=True)
    H, W = f.shape[:2]
    cy = H // 2
    st = {'pre': 0, 'clump': 0, 'clump_line_kept': 0, 'line': 0, 'line_kept': 0, 'stray': 0, 'post': 0,
          'outline_added': 0, 'outline_darkened': 0, 'below_soles_cleared': 0}
    notes = [] if log is None else log
    dy = IDLE_DY.get(k, 0) if tag == 'idle' else 0
    if tag == 'idle':
        st['pre'] += _apply(f, IDLE_PRE, dy, notes, f"{tag}{k}")
    elif tag == 'hit' and k in HIT_PRE:
        st['pre'] += _apply(f, HIT_PRE[k], 0, notes, f"{tag}{k}")
    keep = _face_box(f)
    f = _recolour_black(f, keep, st)
    f = _strays(f, keep, st)
    if tag == 'idle':
        st['post'] += _apply(f, IDLE_POST, dy, notes, f"{tag}{k}")
    if (tag, k) in POST:
        st['post'] += _apply(f, POST[(tag, k)], 0, notes, f"{tag}{k}")
    f, add, dk = strips.complete_outline(f, color=OUT, feet=cy + 11, keep=keep)
    st['outline_added'], st['outline_darkened'] = add, dk
    # closing the outline can fill 1-px clear notches next to old outline pixels and so build new 2x2 black
    # blocks inside the silhouette: give those the material shade too (clumps only, separation lines stay)
    st2 = dict.fromkeys(st, 0)
    f = _recolour_black(f, keep, st2, clumps_only=True)
    st['clump_after_outline'] = st2['clump']
    st['below_soles_cleared'] = int((f[cy + 12:, :, 3] > 0).sum())
    f[cy + 12:] = 0
    notes.append(st)
    return f
