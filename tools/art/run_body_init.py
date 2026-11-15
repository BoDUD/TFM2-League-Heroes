#!/usr/bin/env python3
"""A first data file for tools/art/run_body_anim.py from the hero's own run frames (`run_body_anim.py --init HERO`):
what can be read off the frames is decided here, what cannot is listed under "notes" -> "undecided" for a person.

- The drawn run: the sheet's hd_run (or, with --drawn-from REV, the sheet at that git revision - league_jinx's drawn run
  is main's, her tree holds a re-posed one), kept as assets/source/<hero>/hd/<hero>_run_drawn.png + .json with its 1x
  and lo_ sizes.
- The steps: a frame's stride is how far apart its lowest rows reach (the feet's band, the bottom 12 % of the figure);
  the widest is a contact, the other contact half a cycle on.
- The waist: frames are compared two by two, each pair matched on the head's band first (the best whole-square shift);
  per row the share of squares that differ - legs are redrawn each frame, the upper body far less (the base game's runs:
  the head 94 % the same, the torso 73 %, the legs 49 %). The waist is the first row from which that share stays over
  the midpoint between the head's and the feet's, at least half a figure under the top.
- The upper body every frame gets (`from`): the frame whose upper body is closest to the standing frame's
  (hd_idle_base[0], else hd_idle[0]) at the best shift, among the frames it fits in (its columns inside every frame).
- What hangs below the waist (`below`): per frame, her squares below the waist her feet do not reach (4-connected through
  her squares that are not outline) and that touch the upper body - a fist, a weapon, a sleeve - each in a rect.
- The back hair (`chains`): the colours behind the face (left of its first skin column) in the head's band but skin and
  outline, from the top down to the waist.
- The bob: 1.6 game px from low to high in whole squares (2 at least), two beats - low the frame after each contact,
  high half a step on - moved as little as can be from the drawn place while the head stays in every rect (and in the
  1x frame made from it).
Never decided here: parts that lag the body (fists, a held weapon), a cape or a tail, a knee raised over the waist
(that leg would go under the laid body) - all listed.
"""
import json
import math
import os
import subprocess
import sys

import numpy as np
from scipy import ndimage

import run_body_anim as R

T = R.T


def skin(c):
    r, g, b = (int(v) for v in c[:3])
    return r > g > b and r - b >= 40 and r >= 150 and g >= 90


def outline_colour(hid, frames):
    st = T.load_state().get(hid, {})
    if st.get("outline"):
        return tuple(st["outline"][0])
    oc = T.outline_colours([a for a, _ in frames])
    return tuple(oc[0])


def strides(frames):
    """Per frame: the spread of its feet's band (the bottom 12 % of the figure), in squares."""
    out = []
    for a, _ in frames:
        op = a[..., 3] > 0
        ys = np.nonzero(op.any(1))[0]
        top, bot = ys.min(), ys.max()
        band = op[max(top, bot - max(2, int(0.12 * (bot - top + 1)))):bot + 1]
        xs = np.nonzero(band.any(0))[0]
        out.append(int(xs.max() - xs.min() + 1))
    return out


def contacts(st):
    n = len(st)
    c0 = int(np.argmax(st))
    half = n // 2
    cand = [(c0 + half + d) % n for d in (-1, 0, 1)]
    c1 = max(cand, key=lambda i: (st[i], -abs(((i - c0) % n) - half)))
    return sorted({c0, c1})


def best_shift(a, b, rows_a, rows_b, search=4):
    """The (dy, dx) laying b's band rows_b on a's band rows_a best (most squares alike) -> (dy, dx, share alike)."""
    best = (0, 0, -1.0)
    A = a[rows_a[0]:rows_a[1]]
    for dy in range(-search, search + 1):
        for dx in range(-search, search + 1):
            y0, y1 = rows_b[0] + dy, rows_b[1] + dy
            if y0 < 0 or y1 > b.shape[0]:
                continue
            B = np.zeros_like(A)
            src = b[y0:y1]
            xa0, xb0 = max(0, dx), max(0, -dx)
            w = min(A.shape[1] - xa0, src.shape[1] - xb0)
            if w <= 0:
                continue
            B[:, xa0:xa0 + w] = src[:, xb0:xb0 + w]
            ma, mb = A[..., 3] > 0, B[..., 3] > 0
            both = ma | mb
            if not both.any():
                continue
            same = (ma & mb & (A[..., :3] == B[..., :3]).all(-1)).sum() / float(both.sum())
            if same > best[2]:
                best = (dy, dx, same)
    return best


def waist_rows(frames):
    """-> (the waist row from each frame's centre, the per-row differing share profile)."""
    n = len(frames)
    prof = {}
    for i in range(n):
        a, b = frames[i][0], frames[(i + 1) % n][0]
        oa = np.nonzero((a[..., 3] > 0).any(1))[0]
        ob = np.nonzero((b[..., 3] > 0).any(1))[0]
        ha = (oa.min(), oa.min() + max(6, int(0.3 * (oa.max() - oa.min() + 1))))
        hb = (ob.min(), ob.min() + (ha[1] - ha[0]))
        # b laid on a by its head
        dy, dx, _ = best_shift(a, b, ha, hb)
        for r in range(oa.min(), oa.max() + 1):
            rb = r + (ob.min() - oa.min()) + dy
            if not 0 <= rb < b.shape[0]:
                continue
            ra, rbv = a[r], np.zeros_like(a[r])
            src = b[rb]
            xa0, xb0 = max(0, dx), max(0, -dx)
            w = min(ra.shape[0] - xa0, src.shape[0] - xb0)
            if w > 0:
                rbv[xa0:xa0 + w] = src[xb0:xb0 + w]
            ma, mb = ra[..., 3] > 0, rbv[..., 3] > 0
            both = ma | mb
            if both.sum() < 2:
                continue
            diff = (both & ~(ma & mb & (ra[..., :3] == rbv[..., :3]).all(-1))).sum() / float(both.sum())
            key = r - a.shape[0] // 2
            prof.setdefault(key, []).append(diff)
    rows = sorted(prof)
    D = np.array([np.mean(prof[r]) for r in rows])
    Ds = np.convolve(D, np.ones(3) / 3.0, mode="same")
    top, bot = rows[0], rows[-1]
    head = Ds[:max(3, int(0.3 * len(rows)))]
    feet = Ds[-max(3, int(0.25 * len(rows))):]
    thr = (np.median(head) + np.median(feet)) / 2.0
    start = int(0.45 * len(rows))
    w = None
    for j in range(start, len(rows) - 6):
        if np.mean(Ds[j:j + 6]) >= thr and Ds[j] >= thr * 0.9:
            w = rows[j]
            break
    if w is None:
        w = rows[int(0.55 * len(rows))]
    return w, {"rows": rows, "share": [round(float(v), 3) for v in Ds], "threshold": round(float(thr), 3),
               "top": int(top), "bottom": int(bot)}


def legs_from_feet(a, oc, wr):
    """Her squares from row wr down that her feet reach (4-connected through her squares that are not outline)."""
    op = a[..., 3] > 0
    ink = R.colour_mask(a, [oc])
    low = np.zeros(op.shape, bool)
    low[wr:] = True
    through = op & ~ink & low
    lab, _ = ndimage.label(through)
    ys = np.nonzero(op.any(1))[0]
    feet = np.zeros(op.shape, bool)
    feet[max(wr, ys.max() - 2):ys.max() + 1] = True
    hit = np.unique(lab[through & feet])
    return np.isin(lab, hit[hit > 0])


def hanging(a, oc, wr):
    """Rects (top None, last row, first col, last col) round her squares below the waist that her feet do not reach and
    that touch her above the waist."""
    op = a[..., 3] > 0
    ink = R.colour_mask(a, [oc])
    legs = legs_from_feet(a, oc, wr)
    low = np.zeros(op.shape, bool)
    low[wr:] = True
    rest = op & ~ink & low & ~legs
    lab, n = ndimage.label(rest, structure=R.K8)
    above = np.zeros(op.shape, bool)
    above[:wr] = True
    near_up = ndimage.binary_dilation(op & above, structure=R.K8, iterations=2)
    rects = []
    room = int((op & low).sum())
    for j in range(1, n + 1):
        m = lab == j
        # a fist, a weapon: a piece touching her above the waist, not a quarter of all she has under it
        if m.sum() < 8 or m.sum() > 0.25 * room or not (m & near_up).any():
            continue
        ys, xs = np.nonzero(m)
        rects.append([None, int(min(a.shape[0] - 1, ys.max() + 1)), int(max(0, xs.min() - 1)),
                      int(min(a.shape[1] - 1, xs.max() + 1))])
    # merge overlapping rects
    merged = True
    while merged:
        merged = False
        for p in range(len(rects)):
            for q in range(p + 1, len(rects)):
                A, B = rects[p], rects[q]
                if A[2] <= B[3] + 1 and B[2] <= A[3] + 1:
                    rects[p] = [None, max(A[1], B[1]), min(A[2], B[2]), max(A[3], B[3])]
                    rects.pop(q)
                    merged = True
                    break
            if merged:
                break
    return rects


def init(hero, rev=None, force=False, dry=False):
    hid, pack, ppu, size = T.resolve(hero, T.all_heroes())
    name = R.short(hid)
    path = R.data_file(name)
    if os.path.isfile(R.lp(path)) and not force and not dry:
        sys.exit(f"{path} is there already (--force to write it again)")
    k = size / ppu
    an, px = R.sheet(hid, pack, rev)
    frames = R.frames_of(an, px, "hd_run")
    n = len(frames)
    one = [[int(f["data"]["w"]), int(f["data"]["h"])] for f in an["run"]["frames"]]
    lo = [[int(f["data"]["w"]), int(f["data"]["h"])] for f in an["lo_run"]["frames"]]
    head_rev = rev or subprocess.run(["git", "-C", R.ROOT, "rev-parse", "--short=9", "HEAD"], capture_output=True,
                                     text=True).stdout.strip()
    drawn = (f"assets/source/{name}/hd/{name}_run_drawn" if dry else
             R.keep_drawn(name, frames, one, lo, f"{head_rev} {pack}/champions/{hid}#sheet.png hd_run"))
    oc = outline_colour(hid, frames)
    notes, undecided = {}, []
    # the steps
    st = strides(frames)
    cs = contacts(st)
    notes["contacts"] = f"frames {cs} (feet's band spread {st})"
    # the waist
    w, prof = waist_rows(frames)
    waist = [w] * n
    notes["waist"] = (f"row {w} from the centre in every frame: per-row differing share passes {prof['threshold']} "
                      f"there (figure rows {prof['top']}..{prof['bottom']})")
    # the base frame
    idle_tag = "hd_idle_base" if "hd_idle_base" in an else "hd_idle"
    idle = R.frames_of(an, px, idle_tag)[0][0]
    scores = []
    for i, (a, _) in enumerate(frames):
        wr = a.shape[0] // 2 + w
        ys = np.nonzero((a[..., 3] > 0).any(1))[0]
        rows_a = (int(ys.min()), wr)
        iys = np.nonzero((idle[..., 3] > 0).any(1))[0]
        rows_b = (int(iys.min()), int(iys.min()) + (wr - int(ys.min())))
        # the idle laid on the run frame's upper body (centres on each other first)
        pad = np.zeros((max(a.shape[0], idle.shape[0]) + 20, max(a.shape[1], idle.shape[1]) + 20, 4), np.uint8)
        b = pad.copy()
        oy, ox = (b.shape[0] - idle.shape[0]) // 2, (b.shape[1] - idle.shape[1]) // 2
        b[oy:oy + idle.shape[0], ox:ox + idle.shape[1]] = idle
        A = pad.copy()
        ay, ax = (A.shape[0] - a.shape[0]) // 2, (A.shape[1] - a.shape[1]) // 2
        A[ay:ay + a.shape[0], ax:ax + a.shape[1]] = a
        dy, dx, same = best_shift(A, b, (rows_a[0] + ay, rows_a[1] + ay), (rows_b[0] + oy, rows_b[1] + oy), search=6)
        del dy, dx
        # does its upper body fit every frame (its columns inside each frame's width)?
        up = (a[..., 3] > 0).copy()
        up[wr:] = False
        xs = np.nonzero(up.any(0))[0]
        fits = all(0 <= xs.min() + (f.shape[1] // 2 - a.shape[1] // 2) and
                   xs.max() + (f.shape[1] // 2 - a.shape[1] // 2) < f.shape[1] for f, _ in frames)
        scores.append((round(float(same), 3), fits))
    ok = [i for i in range(n) if scores[i][1]] or list(range(n))
    base = max(ok, key=lambda i: scores[i][0])
    notes["from"] = f"frame {base}: closest to {idle_tag}[0] (alike share per frame {[s for s, _ in scores]}" + \
        (f"; fits every frame: {[i for i in range(n) if scores[i][1]]})" if len(ok) < n else ")")
    src = frames[base][0]
    # what hangs below the waist
    below = []
    for i, (a, _) in enumerate(frames):
        wr = a.shape[0] // 2 + w
        rects = hanging(a, oc, wr)
        below.append(rects)
    notes["below"] = f"rects per frame {[len(r) for r in below]} (her squares under the waist her feet do not reach)"
    undecided.append("a knee or a foot raised over the waist row goes under the laid body: check the review's frames")
    # the back hair
    sop = src[..., 3] > 0
    ys = np.nonzero(sop.any(1))[0]
    top = int(ys.min())
    hb = (top, top + max(6, int(0.3 * (ys.max() - top + 1))))
    sk = np.zeros(sop.shape, bool)
    for y in range(hb[0], hb[1]):
        for x in range(src.shape[1]):
            if sop[y, x] and skin(src[y, x]):
                sk[y, x] = True
    chains = []
    if sk.any():
        root = int(np.nonzero(sk.any(0))[0].min())
        band = sop.copy()
        band[:hb[0]] = False
        band[hb[1]:] = False
        band[:, root:] = False
        band &= ~R.colour_mask(src, [oc])
        cols = {}
        for y, x in zip(*np.nonzero(band)):
            c = tuple(int(v) for v in src[y, x, :3])
            if not skin(c):
                cols[c] = cols.get(c, 0) + 1
        tot = sum(cols.values())
        hair = [list(c) for c, m in sorted(cols.items(), key=lambda q: -q[1]) if tot and m >= 0.04 * tot]
        if hair:
            wr0 = src.shape[0] // 2 + w
            m = R.colour_mask(src, [tuple(c) for c in hair])
            m[:, root:] = False
            m[wr0:] = False
            lab, nn = ndimage.label(m, structure=R.K8)
            big = 0
            if nn:
                big = int(max(ndimage.sum(m, lab, range(1, nn + 1))))
            if big >= 30:
                chains.append({"name": "hair", "colours": hair, "root": root, "side": "left", "rows": [0, wr0],
                               "lag": 1.0, "whip": 0.2})
                notes["chains"] = f"hair: {len(hair)} colours behind the face (root column {root}), {big} squares"
            else:
                notes["chains"] = f"none: the hair behind the face is {big} squares"
    else:
        notes["chains"] = "none: no skin in the head's band to find the face by"
        undecided.append("back hair: no face found - set a chain by hand if the hero has hair, a cape or a tail")
    # the bob
    A = max(2, int(round(R.GAME_BOB / k)))
    m_ = max(1, n // 2)
    tmpl = []
    for i in range(n):
        t = ((i - cs[0]) % m_) / float(m_)
        tmpl.append(int(round(A / 2.0 * (1 + math.cos(2 * math.pi * (t - 0.27))))))
    import ppu_hd as P
    import ppu_one as O
    shown = P.PPU[name] / min(1.0, O.sizes().get(name, 1.0))
    up0 = (src[..., 3] > 0).copy()
    up0[src.shape[0] // 2 + w:] = False
    for rs in below[base]:
        r0, r1, c0, c1 = rs
        up0[src.shape[0] // 2 + w:r1 + 1, c0:c1 + 1] |= (src[src.shape[0] // 2 + w:r1 + 1, c0:c1 + 1, 3] > 0)
    uys = np.nonzero(up0.any(1))[0]
    utop, ubot = int(uys.min()), int(uys.max())
    need = []
    for i, ((a, _), (w1, h1)) in enumerate(zip(frames, one)):
        dy = a.shape[0] // 2 - src.shape[0] // 2
        t_min = max(0, int(math.ceil(a.shape[0] / 2.0 - h1 * shown / 2.0 - 1e-6)))
        need.append(t_min - (utop + dy) - tmpl[i])            # c must be at least this
        # (and the bottom inside the frame)
    c = max(max(need), -int(round(np.mean(tmpl))))
    bob = [v + c for v in tmpl]
    lows = [frames[i][0].shape[0] - 1 - (ubot + frames[i][0].shape[0] // 2 - src.shape[0] // 2) for i in range(n)]
    if any(bob[i] > lows[i] for i in range(n)):
        undecided.append(f"the bob {bob} takes the upper body's bottom out of a frame (room {lows})")
    notes["bob"] = (f"{A} squares low to high ({A * k:.2f} game px), low the frame after the contacts {cs}, moved by "
                    f"{c} so the head stays in every rect: {bob}")
    undecided.append("parts that lag the body (fists, a held weapon): none set - add `parts` (a polygon each in frame "
                     f"{base}) where the hero holds something by the body")
    undecided.append("a cape or a tail: not looked for - add a chain by hand")
    notes["undecided"] = undecided
    cfg = {"hero": name, "tag": "run", "drawn": drawn, "from": base, "outline": list(oc), "waist": waist, "bob": bob,
           "below": below, "parts": [], "chains": chains, "notes": notes}
    if not dry:
        R.save(name, cfg)
    print(f"{path} {'(dry: not written)' if dry else 'written'}")
    for k_, v in notes.items():
        if k_ != "undecided":
            print(f"  {k_}: {v}")
    print("  undecided:")
    for u in undecided:
        print(f"   - {u}")
    return cfg
