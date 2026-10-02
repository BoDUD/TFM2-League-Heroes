"""Tidy Ahri's game frames (tools/art/import_native.py TIDY; the user: "阿狸也是都给我清理干净", approved "狐狸没问题"): clear the dirty black inside her silhouette and the stray squares.

tidy(tag, k, frame) -> frame
  frame: HxWx4 uint8, odd size, the pivot at the centre pixel, soles row = centre + 11.

Order (deterministic):
  0  explicit per-frame edits (EDITS, checked against the expected colour first)
  1  holes: 1-2 px transparent pinholes inside the body are filled (the leg/arm gaps of 3+ stay)
  2  loose pieces: opaque components other than the main one under 12 px are cleared
  2b sticks: 1-px hair strands with no outline (clear on two opposite sides) are pulled back to an outlined
     edge, bits they leave hanging (4-connected, < 8 px) go too; a coloured square with no opaque
     4-neighbour is cleared; one hanging off a single 4-neighbour becomes an outline cap
  3  hair black: interior near-black (not 4-next to clear) whose coloured 4-neighbours are all hair turns
     hair0, repeated until stable - the black blob behind the body and the doubled hair rings melt into the
     hair; the black that touches another material survives as ONE 1-px line (tail edge, arm, face edge)
  4  one-material black: interior near-black whose coloured 4-neighbours are all ONE light material
     (tail slits, doubled rings on tails / clothes / skin) takes that material's darkest shade; a 1-px slit
     that enters from the ring keeps its first pixel as a notch so the tail lobes still part
  5  specks: a light pixel with no 8-neighbour of its own material sitting in the hair takes the hair's
     shade (the white/red crumbs in the hair); a 1-px black dot with no near-black 8-neighbour inside a
     light material takes that material's shade
  5b seam crumbs: a light pixel with no 4-neighbour of its own material, sitting in hair/black, takes the hair
     shade; a tail pixel poking through the tail/hair seam line (one tail 4-neighbour, the rest black/hair)
     becomes the outline black unless that makes a 2x2 black block
  6  black unify: every near-black that remains is the one outline black OUT (6,1,12)
  7  ring check: outline pixels left with no opaque 4-neighbour inside are cleared (1-px black spurs
     sticking out of nothing). No outline is added anywhere: nothing the steps clear leaves a light pixel
     on a new open edge (sticks/lone squares are cleared whole, step 2b caps hanging ones in black)
The dark brown (26,11,15) counts as black where it touches no red and no skin (stray seam pixels); on the
clothes/boots it stays the red's darkest shade.
Eyes (amber EYE/eye2 and the gold0 lid right above them) and every pixel 8-next to them never change.
"""
import os
import sys
import numpy as np

G = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # the repo
sys.path.insert(0, G + "/.claude/skills/tfm2-hero-mod/scripts")
from strips import label  # noqa: E402

OUT = (6, 1, 12)
BLACKS = {(6, 1, 12), (8, 1, 16), (3, 2, 3)}
RAMPS = {  # material -> colours, darkest first
    'hair': [(20, 19, 41), (40, 40, 74), (44, 46, 87), (60, 60, 115)],
    'tail': [(182, 182, 253), (188, 188, 252), (184, 182, 202), (207, 206, 253), (230, 224, 232),
             (249, 244, 252), (255, 255, 255)],
    'red': [(26, 11, 15), (59, 5, 14), (143, 26, 44), (191, 31, 51)],
    'skin': [(105, 69, 69), (177, 98, 103), (195, 162, 141), (210, 137, 126), (214, 90, 98), (252, 223, 204)],
    'gold': [(106, 48, 16), (123, 67, 21), (181, 85, 12), (196, 148, 81)],
    'eye': [(233, 162, 34), (232, 160, 32)],
}
DARKEST = {'hair': (20, 19, 41), 'tail': (182, 182, 253), 'red': (59, 5, 14), 'skin': (105, 69, 69),
           'gold': (106, 48, 16)}
GID = {'blk': 1, 'hair': 2, 'tail': 3, 'red': 4, 'skin': 5, 'gold': 6, 'eye': 7}
GNAME = {v: k for k, v in GID.items()}
LIGHT = {GID['tail'], GID['red'], GID['skin'], GID['gold'], GID['eye']}

# explicit edits: (tag, k) -> list of (x, y, expected colour or None for any opaque, new colour or None = clear)
# coordinates are game px from the pivot (x right, y down)
H0, H1, H2, H3 = RAMPS['hair']
SK, SK1, SKS, PK, WG, GR, GLD = (252, 223, 204), (210, 137, 126), (195, 162, 141), (214, 90, 98), (230, 224, 232),     (184, 182, 202), (196, 148, 81)
J2 = (44, 46, 87)
EDITS = {
    # skill f4: the left ear was a 1-px pink spike 2 rows too tall with no outline on its right; re-shaped
    # into a 3-px ear (tip one row lower, outline both sides, inner pink 3 rows like the idle ear) and the
    # white/grey crumbs in it removed
    ('skill', 4): [(-9, -30, 'blk', None), (-8, -30, H1, None), (-7, -30, 'blk', None),
                   (-9, -29, 'blk', None), (-8, -29, PK, OUT), (-7, -29, 'blk', None),
                   (-10, -28, H0, None), (-9, -28, H1, OUT), (-8, -28, PK, H1), (-7, -28, J2, OUT),
                   (-7, -25, (249, 244, 252), SK1), (-8, -24, GR, H1)],
    # dead f1: the gold bar and the pink sliver running down the left ear into the hair -> hair, the ear
    # keeps its 3 pink rows
    ('dead', 1): [(-7, -21, GLD, H1), (-6, -21, GLD, H1), (-7, -20, SK, H1), (-8, -19, SK, H1),
                  (-8, -18, SK, H1)],
    # dead f5: a white crumb with a black stub on top of the hair
    ('dead', 5): [(-11, -13, 'blk', None), (-10, -13, WG, None)],
    # skill2 f5: white crumb in the hanging hair strand
    ('skill2', 5): [(9, -6, WG, H0)],
}


def groups(a):
    al = a[..., 3] > 0
    g = np.zeros(al.shape, np.int8)
    rgb = a[..., :3]
    for c in BLACKS:
        g[al & (rgb == c).all(-1)] = GID['blk']
    for m, cols in RAMPS.items():
        for c in cols:
            g[al & (rgb == c).all(-1)] = GID[m]
    # the dark brown (26,11,15) is the red's darkest shade on the clothes/boots; where it touches no red
    # and no skin it is a stray near-black in a hair/tail seam -> treat as black
    db = al & (rgb == (26, 11, 15)).all(-1)
    if db.any():
        rs = np.isin(g, (GID['red'], GID['skin'])) & ~db
        p = np.pad(rs, 1)
        near = np.zeros_like(rs)
        for dy in (0, 1, 2):
            for dx in (0, 1, 2):
                near |= p[dy:dy + rs.shape[0], dx:dx + rs.shape[1]]
        g[db & ~near] = GID['blk']
    return g


def label4(mask):
    """4-connected component labels (BFS, raster order - deterministic)."""
    H, W = mask.shape
    lab = np.zeros((H, W), np.int32)
    n = 0
    for y0, x0 in zip(*np.nonzero(mask)):
        if lab[y0, x0]:
            continue
        n += 1
        lab[y0, x0] = n
        st = [(y0, x0)]
        while st:
            y, x = st.pop()
            for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= yy < H and 0 <= xx < W and mask[yy, xx] and not lab[yy, xx]:
                    lab[yy, xx] = n
                    st.append((yy, xx))
    return lab, n


def nb4(m):
    p = np.pad(m, 1)
    return p[:-2, 1:-1], p[2:, 1:-1], p[1:-1, :-2], p[1:-1, 2:]


def eye_guard(a, g):
    """Eyes + the lid pixel above + every 8-neighbour: never touched."""
    eye = g == GID['eye']
    ys, xs = np.nonzero(eye)
    guard = np.zeros_like(eye)
    H, W = eye.shape
    for y, x in zip(ys, xs):
        guard[max(0, y - 2):y + 2, max(0, x - 1):x + 2] = True
    return guard


def apply_edits(a, tag, k, log):
    H, W = a.shape[:2]
    py, px = H // 2, W // 2
    for x, y, exp, new in EDITS.get((tag, k), []):
        yy, xx = py + y, px + x
        if not (0 <= yy < H and 0 <= xx < W):
            continue
        cur = a[yy, xx]
        if exp is None:
            if cur[3] == 0:
                continue
        elif exp == 'blk':
            if cur[3] == 0 or tuple(int(v) for v in cur[:3]) not in BLACKS:
                log['skipped'].append((x, y))
                continue
        elif exp == 'clear':
            if cur[3] != 0:
                continue
        elif cur[3] == 0 or tuple(int(v) for v in cur[:3]) != tuple(exp):
            log['skipped'].append((x, y))
            continue
        if new is None:
            a[yy, xx] = 0
        else:
            a[yy, xx, :3] = new
            a[yy, xx, 3] = 255
        log['edits'] += 1


def tidy(tag, k, frame, log=None):
    a = frame.copy()
    if log is None:
        log = {}
    log.update(edits=0, skipped=[], holes=0, pieces=0, hair_black=0, mat_black=0, notch=0, specks=0,
               dots=0, crumbs=0, tips=0, sticks=0, caps=0, unify=0, spurs=0, closed=0)
    H, W = a.shape[:2]
    apply_edits(a, tag, k, log)
    cleared_by_edit = (frame[..., 3] > 0) & (a[..., 3] == 0)

    # 1 holes
    al = a[..., 3] > 0
    lab, n = label(~al)
    for i in range(1, n + 1):
        m = lab == i
        ys, xs = np.nonzero(m)
        if ys.min() == 0 or xs.min() == 0 or ys.max() == H - 1 or xs.max() == W - 1:
            continue
        if len(ys) > 2:
            continue
        for y, x in zip(ys, xs):
            win = a[max(0, y - 1):y + 2, max(0, x - 1):x + 2].reshape(-1, 4)
            cols = [tuple(int(v) for v in c[:3]) for c in win if c[3]]
            c = max(set(cols), key=cols.count)
            a[y, x, :3] = c
            a[y, x, 3] = 255
            log['holes'] += 1

    # 2 loose pieces
    al = a[..., 3] > 0
    lab, n = label(al)
    if n > 1:
        sizes = [(lab == i).sum() for i in range(1, n + 1)]
        big = int(np.argmax(sizes)) + 1
        for i in range(1, n + 1):
            if i != big and sizes[i - 1] < 12:
                a[lab == i] = 0
                log['pieces'] += int(sizes[i - 1])

    g = groups(a)
    guard = eye_guard(a, g)

    a0 = a.copy()
    # 2b sticks: 1-px hair strands with no outline (clear on both opposite sides) are pulled back until
    #    the strand ends at an outlined edge; a coloured square with no opaque 4-neighbour is cleared, one
    #    hanging off a single 4-neighbour (red ribbon / gold crumbs, no outline) becomes an outline cap
    for _ in range(8):
        al = a[..., 3] > 0
        u, d, l, r = nb4(al)
        st = (g == GID['hair']) & ((~u & ~d) | (~l & ~r)) & ~guard
        if not st.any():
            break
        a[st] = 0
        g[st] = 0
        log['sticks'] += int(st.sum())
    # what the sticks left hanging (4-connected bits < 8 px next to a cleared stick pixel) goes too
    cut = (a0[..., 3] > 0) & (a[..., 3] == 0)
    if cut.any():
        lab4, n4c = label4(a[..., 3] > 0)
        if n4c > 1:
            sizes = np.bincount(lab4.ravel())[1:]
            big = int(np.argmax(sizes)) + 1
            cp = np.pad(cut, 1)
            near = np.zeros_like(cut)
            for dy in (0, 1, 2):
                for dx in (0, 1, 2):
                    near |= cp[dy:dy + cut.shape[0], dx:dx + cut.shape[1]]
            for i in range(1, n4c + 1):
                m = lab4 == i
                if i != big and sizes[i - 1] < 8 and (m & near).any():
                    a[m] = 0
                    g[m] = 0
                    log['sticks'] += int(m.sum())
    al = a[..., 3] > 0
    u, d, l, r = nb4(al)
    n4 = u.astype(int) + d + l + r
    lone = al & (g != GID['blk']) & (n4 == 0) & ~guard
    a[lone] = 0
    g[lone] = 0
    log['sticks'] += int(lone.sum())
    al = a[..., 3] > 0
    u, d, l, r = nb4(al)
    n4 = u.astype(int) + d + l + r
    cap = al & (g > 1) & (g != GID['hair']) & (n4 == 1) & ~guard
    a[cap, :3] = OUT
    g[cap] = GID['blk']
    log['caps'] += int(cap.sum())

    def interior_black():
        al = a[..., 3] > 0
        u, d, l, r = nb4(al)
        return (g == GID['blk']) & u & d & l & r & ~guard

    # 3 hair black, simultaneous passes
    hid = GID['hair']
    while True:
        ib = interior_black()
        gu, gd, gl, gr = nb4(g)
        hasHair = (gu == hid) | (gd == hid) | (gl == hid) | (gr == hid)
        other = np.zeros_like(ib)
        for q in (gu, gd, gl, gr):
            other |= (q > 1) & (q != hid)
        sel = ib & hasHair & ~other
        if not sel.any():
            break
        a[sel, :3] = DARKEST['hair']
        g[sel] = hid
        log['hair_black'] += int(sel.sum())

    # 4 one-material black, sequential raster order
    ib = interior_black()
    ring = (g == GID['blk']) & ~ib
    for y, x in zip(*np.nonzero(ib)):
        nbr = [(y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)]
        mats = {int(g[q]) for q in nbr if g[q] > 1}
        if len(mats) != 1:
            continue
        m = mats.pop()
        if m == GID['eye']:
            continue
        # notch: a 1-px slit entering from the ring, material on both sides across it
        touches_ring = any(ring[q] for q in nbr)
        across = (g[y, x - 1] == m and g[y, x + 1] == m) or (g[y - 1, x] == m and g[y + 1, x] == m)
        if touches_ring and across and m == GID['tail']:
            log['notch'] += 1
            continue
        a[y, x, :3] = DARKEST[GNAME[m]]
        g[y, x] = m
        log['mat_black'] += 1

    # 5 specks
    gp = np.pad(g, 1)
    for y, x in zip(*np.nonzero(g > 1)):
        if guard[y, x] or g[y, x] in (hid, GID['eye']):
            continue
        win = gp[y:y + 3, x:x + 3].copy()
        win[1, 1] = -1
        if (win == g[y, x]).any():
            continue
        nh = int((win == hid).sum())
        nb = int((win == GID['blk']).sum())
        if nh >= 3 and nh + nb >= 7:
            cols = [tuple(int(v) for v in a[y + dy, x + dx, :3]) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                    if 0 <= y + dy < H and 0 <= x + dx < W and g[y + dy, x + dx] == hid]
            a[y, x, :3] = max(sorted(set(cols)), key=cols.count)
            g[y, x] = hid
            log['specks'] += 1
    ib = interior_black()
    gp = np.pad(g, 1)
    for y, x in zip(*np.nonzero(ib)):
        win = gp[y:y + 3, x:x + 3].copy()
        win[1, 1] = 0
        if (win == GID['blk']).any():
            continue
        mats = [int(v) for v in win.ravel() if v > 1]
        m = max(set(mats), key=mats.count)
        if m in (GID['eye'],):
            continue
        a[y, x, :3] = DARKEST[GNAME[m]]
        g[y, x] = m
        log['dots'] += 1

    # 5b seam crumbs: light pixels poking into the hair / the tail-hair seam
    #   lone   - no 4-neighbour of its own material, a hair pixel among its 8-neighbours, no clear
    #            4-neighbour -> the hair's shade (most common hair colour among the 8-neighbours)
    #   tip    - a tail-group pixel with exactly one tail 4-neighbour, the other three black or hair (>= 1
    #            black), hair among the 8-neighbours, no clear 4-neighbour: the tip of a tail lobe that broke
    #            through the seam line -> the outline black, unless that would make a 2x2 black block
    for _ in range(2):
        changed = 0
        al = a[..., 3] > 0
        for y, x in zip(*np.nonzero(np.isin(g, (GID['tail'], GID['red'], GID['skin'], GID['gold'])))):
            if guard[y, x] or y in (0, H - 1) or x in (0, W - 1):
                continue
            n4 = [(y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)]
            if not all(al[q] for q in n4):
                continue
            m = g[y, x]
            same = [q for q in n4 if g[q] == m]
            win = g[y - 1:y + 2, x - 1:x + 2]
            if not (win == hid).any():
                continue
            if not same and all(g[q] in (hid, GID['blk']) for q in n4):
                cols = [tuple(int(v) for v in a[y + dy, x + dx, :3]) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                        if g[y + dy, x + dx] == hid]
                a[y, x, :3] = max(sorted(set(cols)), key=cols.count)
                g[y, x] = hid
                log['crumbs'] += 1
                changed += 1
                continue
            if m == GID['tail'] and len(same) == 1:
                rest = [q for q in n4 if q != same[0]]
                if all(g[q] in (hid, GID['blk']) for q in rest) and any(g[q] == GID['blk'] for q in rest):
                    bl = g == GID['blk']
                    bl[y, x] = True
                    blk2 = False
                    for dy in (-1, 0):
                        for dx in (-1, 0):
                            if bl[y + dy:y + dy + 2, x + dx:x + dx + 2].all():
                                blk2 = True
                    if blk2:
                        continue
                    a[y, x, :3] = OUT
                    g[y, x] = GID['blk']
                    log['tips'] += 1
                    changed += 1
        if not changed:
            break

    # 6 one black
    blk = g == GID['blk']
    diff = blk & ~(a[..., :3] == OUT).all(-1)
    a[diff, :3] = OUT
    log['unify'] = int(diff.sum())

    # 7 spurs: an outline pixel with no opaque 4-neighbour that is not outline itself and 3 clear sides
    for _ in range(3):
        al = a[..., 3] > 0
        u, d, l, r = nb4(al)
        nclear = 4 - (u.astype(int) + d + l + r)
        nonblk = (g > 1)
        bu, bd, bl, br = nb4(nonblk)
        sp = blk & al & (nclear >= 3) & ~(bu | bd | bl | br)
        if not sp.any():
            break
        a[sp] = 0
        g[sp] = 0
        blk &= ~sp
        log['spurs'] += int(sp.sum())
    return a
