#!/usr/bin/env python3
"""Lulu slimmer, with League's eyes (the user, 2026-10-09: 「露露瘦身并且调整脸部五官」; from the options sheet she
picked 「删 5 列」 and 「B 英雄联盟眼」).

    python tools/art/slim_lulu.py            # edits assets/source/native/lulu_*.png (8x) in place, then
    python tools/art/import_native.py --hero lulu

Face, in every frame that shows it and in the design: the 2x2 lime eyes with a white corner become League's - a
yellow-green iris and a dark pupil on the top row, the green and a white catch-light under them; the lash line over
each eye one square longer outward; the dark red mouth violet like her lips. Every frame carries the design's face
square for square (work/lul/stage_lu.py pasted it whole after the 90% shrink), so the edit is one list of squares
counted from the far eye's top-left square (the green's top row, its first column).

Body: five whole columns out of every frame, never resampled - the same five counted from that square, two through
the hat's curl and three through the hair falling behind her, the brim and the robe's left side. The face and the
staff (right of the face in every frame) keep their place, and so does the pivot (right of every cut); whatever lies
left of a cut moves one square right. What a cut must not go through is lifted off first and put back whole, one
square right for each cut between its middle and the pivot: Pix (its own piece, or - where its tail touches the
brim, Q 2 and 4-6 - flooded from its magenta and pink, stopping at the hat's colours and the outline touching them),
every piece of skin left of the face (the far hand, the ear) and the far boot, each with the outline round it. COLS
are the cheapest such five over all the frames (work/ls/colsearch2_lu.py) that close no gap into a see-through hole:
the mock-up's first five (-19, -17, -13, -7, -3) cut the far boot and hand narrower and closed the gap inside the
hat's curl into pinholes. The deaths 4-8 (she is gone, the hat lies on the staff) keep their pictures.

Run twice, it changes nothing: a frame whose eyes are already the new ones is left alone.
"""
import json
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
NATIVE = os.path.join(ROOT, "assets", "source", "native")
Z = 8


def rgb(h):
    return np.array((int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)), np.uint8)


GREEN, WHITE, SKIN, LASH, MOUTH = rgb("8AD82A"), rgb("E6E6F6"), rgb("DCD4FF"), rgb("2A0E4A"), rgb("9A1830")
OUTLINE = rgb("180A14")
IRIS, PUPIL, GLINT, LIPS = rgb("D2EC3C"), rgb("1E3A10"), rgb("FFFFFF"), rgb("7A30B4")
# (dx, dy from the far eye's top-left square, the colours it may have now, its new colour)
FACE = [
    (1, -1, [SKIN], LASH), (6, -1, [SKIN], LASH), (7, -1, [OUTLINE, SKIN], LASH),   # the lashes a square longer
    (0, 0, [WHITE], IRIS), (1, 0, [GREEN], PUPIL), (4, 0, [WHITE], IRIS), (5, 0, [GREEN], PUPIL),
    (1, 1, [GREEN], GLINT), (5, 1, [GREEN], GLINT),
    (3, 2, [MOUTH], LIPS),
]
COLS = [-21, -19, -10, -7, -4]          # the columns cut, counted from the far eye's first column
PIX = [rgb("C030D0"), rgb("FF80FF")]    # Pix's magenta and pink (the pink is also her blush, inside the face)
HAT = [rgb(h) for h in ("D2283A", "9A1830", "F6C040", "8A4A12", "5A2E1A")]     # brim red, shade, gold, band browns


def load1x(path):
    return np.asarray(Image.open(path).convert("RGBA"))[::Z, ::Z].copy()


def save8x(a, path):
    Image.fromarray(np.repeat(np.repeat(a, Z, 0), Z, 1)).save(path)


def is_(c, col):
    return (c[..., :3] == col).all(-1) & (c[..., 3] > 0)


def anchor(c):
    """(row, column) of the far eye's top-left square, and whether the eyes are the new ones; None without eyes."""
    for col, new in ((IRIS, True), (GREEN, False)):
        ys, xs = np.nonzero(is_(c, col))
        if len(ys):
            return int(ys.min()), int(xs.min()), new
    return None


def face(c, ey, ex):
    """League's eyes on the frame (in place); the squares that did not hold what was expected, if any."""
    bad = [(dx, dy) for dx, dy, was, _ in FACE
           if not (c[ey + dy, ex + dx, 3] and any((c[ey + dy, ex + dx, :3] == w).all() for w in was))]
    if not bad:
        for dx, dy, _, new in FACE:
            c[ey + dy, ex + dx, :3] = new
    return bad


def pieces(op):
    """8-connected labels of the opaque squares (0 = empty) and the largest one's label (the body)."""
    H, W = op.shape
    lab = np.zeros((H, W), int)
    n = 0
    for y, x in zip(*np.nonzero(op)):
        if lab[y, x]:
            continue
        n += 1
        lab[y, x] = n
        todo = [(y, x)]
        while todo:
            v, u = todo.pop()
            for dv in (-1, 0, 1):
                for du in (-1, 0, 1):
                    q, w = v + dv, u + du
                    if 0 <= q < H and 0 <= w < W and op[q, w] and not lab[q, w]:
                        lab[q, w] = n
                        todo.append((q, w))
    sizes = np.bincount(lab.ravel())
    return lab, int(np.argmax(sizes[1:])) + 1 if n else 0


def pix_mask(c, ey, ex):
    """Pix's squares: its own piece when it floats free (run 3's Pix has a square of the hat's red); when its tail
    touches the brim (Q 2, 4-6), flooded (8 ways) from its magenta and pink outside the face, within 4 squares of
    them, never onto the hat's colours or an outline square touching them."""
    H, W = c.shape[:2]
    op = c[..., 3] > 0
    core = np.zeros((H, W), bool)
    for col in PIX:
        core |= is_(c, col)
    core[max(0, ey - 4):ey + 6, max(0, ex - 3):ex + 10] = False          # the blush on her cheek
    if not core.any():
        return core
    lab, body = pieces(op)
    free = {int(v) for v in np.unique(lab[core])} - {0, body}
    if free:
        return np.isin(lab, sorted(free))
    ys, xs = np.nonzero(core)
    box = (ys.min() - 4, ys.max() + 4, xs.min() - 4, xs.max() + 4)
    hat = np.zeros((H, W), bool)
    for col in HAT:
        hat |= is_(c, col)
    near_hat = np.zeros((H, W), bool)
    near_hat[1:] |= hat[:-1]
    near_hat[:-1] |= hat[1:]
    near_hat[:, 1:] |= hat[:, :-1]
    near_hat[:, :-1] |= hat[:, 1:]
    stop = hat | (near_hat & is_(c, OUTLINE))
    m = core.copy()
    todo = list(zip(ys, xs))
    while todo:
        y, x = todo.pop()
        for v in (-1, 0, 1):
            for u in (-1, 0, 1):
                q, w = y + v, x + u
                if (box[0] <= q <= box[1] and box[2] <= w <= box[3] and 0 <= q < H and 0 <= w < W
                        and op[q, w] and not m[q, w] and not stop[q, w]):
                    m[q, w] = True
                    todo.append((q, w))
    return m


SKINS = [rgb(h) for h in ("DCD4FF", "B4A8F0", "E6E6F6", "8A7AD8", "9A9AC8")]   # skin, its shades, the gloves' white
BOOTS = [rgb("4E3040")]                                                          # the boots' plum
STAFF = [rgb("B47A4E"), rgb("5A2E1A"), rgb("4E3040")]     # the staff's light and dark wood, the plum in its curl


def ring(m, c):
    """m and the outline squares 4-next to it."""
    out = m.copy()
    near = np.zeros_like(m)
    near[1:] |= m[:-1]
    near[:-1] |= m[1:]
    near[:, 1:] |= m[:, :-1]
    near[:, :-1] |= m[:, 1:]
    return out | (near & is_(c, OUTLINE))


def rigid(c, ey, ex, py):
    """The parts a cut must never go through, as (mask, kind) moved whole: Pix ("pix"), the staff (W 2 holds it up
    over her hat, its curl left of her face), every piece of skin outside the face (the far hand, the ear) and every
    boot, each with the outline round it - a boot's also along the soles row to the sole's ends (the sole stands a
    square out each side of the boot: cut, the foot became a block)."""
    H, W = c.shape[:2]
    parts = []
    pix = pix_mask(c, ey, ex)
    if pix.any():
        parts.append((pix, "pix"))
    skin = np.zeros((H, W), bool)
    for col in SKINS:
        skin |= is_(c, col)
    skin[max(0, ey - 4):ey + 6, max(0, ex - 3):] = False          # the face and everything right of it stays put
    skin &= ~pix
    boots = np.zeros((H, W), bool)
    for col in BOOTS:
        boots |= is_(c, col)
    boots[:py + 5] = False                                         # the boots stand on the soles row (pivot + 11)
    wood = np.zeros((H, W), bool)
    for col in STAFF:
        wood |= is_(c, col)
    wood[py + 5:] = False                                          # its foot between the boots is right of every cut
    wood &= ~pix
    lab, _ = pieces(wood)
    staff = np.zeros((H, W), bool)
    for i in range(1, lab.max() + 1):
        if (is_(c, STAFF[0]) & (lab == i)).sum() >= 8:            # the staff, not a brown speck of the robe or hat
            staff |= lab == i
    staff = ring(staff, c) & ~pix
    if staff.any():
        parts.append((staff, "staff"))
    skin &= ~staff
    boots &= ~staff
    sole = py + 11
    for kind, m in (("skin", skin), ("boot", boots)):
        lab, _ = pieces(m)
        for i in range(1, lab.max() + 1):
            part = ring(lab == i, c) & ~pix
            if kind == "boot" and 0 <= sole < H:
                for _ in range(2):                                  # along the soles row, out to the sole's ends
                    row = part[sole].copy()
                    grow = np.zeros_like(row)
                    grow[1:] |= row[:-1]
                    grow[:-1] |= row[1:]
                    part[sole] |= grow & is_(c[sole:sole + 1], OUTLINE)[0]
            if part.any():
                parts.append((part, kind))
    return parts


def slim(c, px, ex, parts):
    """The cell without the COLS columns (all left of the pivot); the rigid parts put back whole: a part embedded in
    the body one square right for every cut between its middle and the pivot, Pix (hovering apart) as much as the
    body square nearest to it, so it keeps its distance from the hat."""
    cw = c.shape[1]
    cuts = sorted(ex + d for d in COLS)
    assert cuts[-1] < px, f"a cut ({cuts[-1]}) right of the pivot ({px})"
    body = c.copy()
    for m, _ in parts:
        body[m] = 0
    keep = [x for x in range(cw) if x not in cuts]
    out = np.zeros_like(c)
    out[:, len(cuts):] = body[:, keep]
    by, bx = np.nonzero((body[..., 3] > 0) & ~np.isin(np.arange(cw), cuts)[None, :])
    for m, kind in parts:
        ys, xs = np.nonzero(m)
        if kind == "pix" and len(by):
            d = (by[:, None] - ys[None, :]) ** 2 + (bx[:, None] - xs[None, :]) ** 2
            x = bx[np.unravel_index(int(d.argmin()), d.shape)[0]]
        else:
            x = (xs.min() + xs.max()) / 2
        shift = sum(1 for cut in cuts if cut > x)
        out[ys, xs + shift] = c[ys, xs]
    return out


def main():
    with open(os.path.join(NATIVE, "lulu_cells.json"), encoding="utf-8") as f:
        cells = json.load(f)
    cw, ch = cells["cell"]
    dpath = os.path.join(NATIVE, "lulu_native.png")
    d = load1x(dpath)
    a = anchor(d)
    if a is None:
        raise SystemExit("lulu_native.png: no eyes found")
    if a[2]:
        print("lulu_native.png: the eyes are League's already")
    else:
        bad = face(d, a[0], a[1])
        if bad:
            raise SystemExit(f"lulu_native.png: the face is not the expected one at {bad}")
        save8x(d, dpath)
        print("lulu_native.png: League's eyes (the design keeps its width; the strips are cut)")
    for tag, rows in cells["tags"].items():
        path = os.path.join(NATIVE, f"lulu_{tag}.png")
        s = load1x(path)
        ncol = s.shape[1] // cw
        done, kept, skipped, report = [], [], [], []
        for k, r in enumerate(rows):
            y0, x0 = (k // ncol) * ch, (k % ncol) * cw
            c = s[y0:y0 + ch, x0:x0 + cw]
            a = anchor(c)
            if a is None:
                kept.append(k + 1)
                continue
            ey, ex, new = a
            if new:
                skipped.append(k + 1)
                continue
            bad = face(c, ey, ex)
            if bad:
                raise SystemExit(f"lulu_{tag}.png frame {k + 1}: the face is not the expected one at {bad}")
            parts = rigid(c, ey, ex, r["pivot"][1])
            s[y0:y0 + ch, x0:x0 + cw] = slim(c, r["pivot"][0], ex, parts)
            done.append(k + 1)
            report.append(f"{k + 1}:{len(parts)}")
        if done:
            save8x(s, path)
        print(f"lulu_{tag}.png: eyes + 5 columns in {done or '-'} (frame:parts moved whole)"
              + (f" ({' '.join(report)})" if report else "")
              + (f", no face (kept) {kept}" if kept else "") + (f", already done {skipped}" if skipped else ""))


if __name__ == "__main__":
    main()
