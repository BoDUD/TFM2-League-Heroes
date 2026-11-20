"""Galio's run legs cleaned (the user, 2026-11-19: 「这里腿部像素缺失没处理？还有走路会出来不干净的黑边也没清理」): Codex's run
redraw left (1) loose specks in the gap between the legs, (2) a porous inner thigh / crotch (dark grey and clear squares
mixed: 「像素缺失」) and (3) black heaped 3-5 squares thick on the legs' outer edges and feet, a different shape in every
frame (「不干净的黑边」). Inside the region box only (the legs), in this order:
  1. opaque 8-connected pieces of <= SPECK squares not joined to the figure go;
  2. a clear square with >= 5 opaque of its 8 neighbours is filled (its non-black neighbours' commonest colour when
     >= 3 of them are not black, else black), repeated until nothing changes (pinholes, the porous patch);
  3. a black square touching the clear (4-way) with no non-black square within 2 (8-way rings) is cleared, from the
     outside in, until nothing changes: the black on the silhouette ends <= 2 squares from the stone, like the stance's;
     black between two parts never touches the clear and stays.
    clean(c, box) -> picture
"""
import numpy as np

BLACK = (3, 2, 1)
SPECK = 4


def isblack(p):
    return p[3] > 0 and int(p[0]) + int(p[1]) + int(p[2]) < 40


def clean(c, box):
    x0, y0, x1, y1 = box
    new = c.copy()
    h, w = c.shape[:2]
    inbox = lambda y, x: x0 <= x <= x1 and y0 <= y <= y1
    n8 = [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if a or b]
    # 1. specks
    op = new[..., 3] > 0
    seen = np.zeros((h, w), bool)
    comps = []
    for y, x in zip(*np.nonzero(op)):
        if seen[y, x]:
            continue
        comp, st = [], [(y, x)]
        seen[y, x] = True
        while st:
            q, p = st.pop()
            comp.append((q, p))
            for a, b in n8:
                qq, pp = q + a, p + b
                if 0 <= qq < h and 0 <= pp < w and op[qq, pp] and not seen[qq, pp]:
                    seen[qq, pp] = True
                    st.append((qq, pp))
        comps.append(comp)
    biggest = max(len(cc) for cc in comps)
    removed = 0
    for cc in comps:
        if len(cc) <= SPECK and len(cc) < biggest and all(inbox(q, p) for q, p in cc):
            for q, p in cc:
                new[q, p] = 0
            removed += len(cc)
    # 2. fill pinholes / porous patches
    filled = 0
    for _ in range(6):
        op = new[..., 3] > 0
        adds = []
        for y in range(max(1, y0), min(h - 1, y1 + 1)):
            for x in range(max(1, x0), min(w - 1, x1 + 1)):
                if op[y, x]:
                    continue
                nb = [new[y + a, x + b] for a, b in n8 if op[y + a, x + b]]
                if len(nb) < 5:
                    continue
                colour = [tuple(int(v) for v in p) for p in nb if not isblack(p)]
                if len(colour) >= 3:
                    vals, cnt = np.unique(np.array(colour), axis=0, return_counts=True)
                    adds.append((y, x, vals[cnt.argmax()]))
                else:
                    adds.append((y, x, np.array([*BLACK, 255])))
        if not adds:
            break
        for y, x, col in adds:
            new[y, x] = col
        filled += len(adds)
    # 3. thin the black on the silhouette to <= 2 squares from the stone
    cleared = 0
    for _ in range(8):
        op = new[..., 3] > 0
        colour = op & ~np.array([[isblack(new[y, x]) for x in range(w)] for y in range(h)])
        near = np.zeros((h, w), bool)
        for a in range(-2, 3):
            for b in range(-2, 3):
                near |= np.roll(np.roll(colour, a, 0), b, 1)
        dels = []
        for y in range(max(1, y0), min(h - 1, y1 + 1)):
            for x in range(max(1, x0), min(w - 1, x1 + 1)):
                if not (op[y, x] and isblack(new[y, x])) or near[y, x]:
                    continue
                if any(not op[y + a, x + b] for a, b in ((-1, 0), (1, 0), (0, -1), (0, 1))):
                    dels.append((y, x))
        if not dels:
            break
        for y, x in dels:
            new[y, x] = 0
        cleared += len(dels)
    return new, dict(specks=removed, filled=filled, black_cleared=cleared)


def clean2(c, box, passes=2):
    """v2: the ragged inner-thigh patches resolved by the local fill of the 3 x 3 window: a clear square with >= 5 of 9
    opaque is filled (non-black neighbours' commonest colour, else black); a non-black square with <= 3 of 9 opaque
    goes; then every non-black square touching the clear (4-way) gets its outline (black) on that clear square; then the
    black on the silhouette is thinned to <= 2 squares from the stone (clean()'s step 3)."""
    x0, y0, x1, y1 = box
    new = c.copy()
    h, w = c.shape[:2]
    n8 = [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if a or b]
    stats = dict(filled=0, removed=0, outlined=0)
    for _ in range(passes):
        op = new[..., 3] > 0
        dens = sum(np.roll(np.roll(op, a, 0), b, 1).astype(int) for a in (-1, 0, 1) for b in (-1, 0, 1))
        adds, dels = [], []
        for y in range(max(1, y0), min(h - 1, y1 + 1)):
            for x in range(max(1, x0), min(w - 1, x1 + 1)):
                if not op[y, x] and dens[y, x] >= 5:
                    nb = [tuple(int(v) for v in new[y + a, x + b]) for a, b in n8 if op[y + a, x + b] and not isblack(new[y + a, x + b])]
                    if len(nb) >= 3:
                        vals, cnt = np.unique(np.array(nb), axis=0, return_counts=True); adds.append((y, x, vals[cnt.argmax()]))
                    else:
                        adds.append((y, x, np.array([*BLACK, 255])))
                elif op[y, x] and not isblack(new[y, x]) and dens[y, x] <= 3:
                    dels.append((y, x))
        for y, x, col in adds:
            new[y, x] = col
        for y, x in dels:
            new[y, x] = 0
        stats["filled"] += len(adds); stats["removed"] += len(dels)
    # outline every non-black square that touches the clear
    op = new[..., 3] > 0
    for y in range(max(1, y0), min(h - 1, y1 + 1)):
        for x in range(max(1, x0), min(w - 1, x1 + 1)):
            if op[y, x]:
                continue
            if any(op[y + a, x + b] and not isblack(new[y + a, x + b]) for a, b in ((-1, 0), (1, 0), (0, -1), (0, 1))):
                new[y, x] = (*BLACK, 255); stats["outlined"] += 1
    new2, info = clean(new, box)
    stats.update({"specks": info["specks"], "black_cleared": info["black_cleared"], "filled_after": info["filled"]})
    return new2, stats
