#!/usr/bin/env python3
"""Pyke's action strips posed from the approved design's own parts (the casting body = the idle's).

    python tools/art/rig_pyke.py [--check] [--review DIR] [--tags attack,skill]

Codex's step-2 round (assets/source/pyke/codex_strips/) rigged him from the design too, but its parts read badly at game
size: the front claw arm turned level into a stick, the harpoon's blade hidden behind the body in the stab and the ult,
the run's legs turned 45 degrees by nearest-neighbour (jagged, no crossing), the dive and the fall a whole-body 45-degree
turn under an upright head. The user: 「有问题的地方你帮忙修复 和之前做英雄一样 灵活运用工具」. Here:
- one rigid unit, REAR: the far arm with its fist and the harpoon (the design holds it raised behind him); it turns about
  the far shoulder by RotSprite in whole 15-45 degree steps (rigkit.turn) and is never bent or sheared. Pointing forward
  (-45) it lies level over his head, its root behind the big spike on his back (lifted to RAISED), the blade forward;
  cocked back (+45) it stands upright behind him. Without the harpoon (ARM) for the frames after the hook leaves.
- the near arm (the claw hanging by the near knee) never moves: the idle's.
- the head is pasted last in every standing frame (the design's own squares).
- the run: the design's own legs moved whole only slid (a deep, wide crouch, short legs under baggy trousers), so
  Codex drew the legs over oppi's Rengar run (tools/art/pack_pyke_run.py, a skin swap; the user: 「你直接拿过来修吧」
  before its HANDOFF): codex_run/raw/pyke_run_phase_fix_raw.png read back square by square (RUN_PITCH source px a
  square, the majority colour of each, mapped to the design's palette), its legs kept below the belt (RUN_SEAM) and
  the design's own upper body pasted on them where Codex's head stood (one head column for the loop, bob 0-1 row),
  the claw arm and the coat's hem the design's; crumbs under 12 squares dropped.
- the death (league_sivir's): struck back, knocked back, falling (the whole figure turned 45 degrees, RotSprite),
  lying on his back (a quarter turn, exact), the harpoon on the ground beside him.
Every frame is finished alike (rigkit.finish). Writes assets/source/native/pyke_<tag>.png (8x, 128x96 cells) and
pyke_cells.json; then tools/art/import_native.py.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rigkit as K  # noqa: E402

NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "pyke_native.png")
HERO = "pyke"
PIVOT = (64, 88)                       # the standing point on the 128 canvas (the soles on row 99)
CELL, CELL_PIVOT = (128, 96), (64, 70)
SOLES = 99
MS = {"idle": [200] * 6, "run": [135] * 8, "attack": [60, 60, 80, 70, 70, 60],
      "skill_stab": [70, 70, 80, 70, 77], "skill": [150, 150, 150, 150, 120, 113], "skill2": [60, 60, 60, 53],
      "ult": [150, 175, 175, 60, 60, 47], "hit": [100, 100], "dead": [100, 110, 120, 130, 150, 200, 300, 400]}
TAGS = list(MS)

SHOULDER = (55.5, 63.5)                # the far shoulder, where REAR turns
FRONT_SHOULDER = (83.5, 81.5)          # the near shoulder (the claw arm hangs from it)
RAISED = (63.5, 59.5)                  # where the shoulder joint sits when the harpoon is swung over his head


RUN_RAW = os.path.join(ROOT, "assets", "source", "pyke", "codex_run", "raw", "pyke_run_phase_fix_raw.png")
RUN_PITCH, RUN_SEAM = 4.87, 83
CLAW_END = 84                                               # nothing of Codex's from here right: its arm's outline
CLAW_X = 74                                                 # right of this the near side: the claw arm and the hem
TRAIL_HIP, TRAIL_X, TRAIL_FROM = (55.5, 86.5), 54, 44     # the trailing leg: hip joint, columns left of TRAIL_X,
                                                            # turned down when it reaches out past TRAIL_FROM


def read_run(palette):
    """Codex's 4 x 2 run sheet (green ground, squares of RUN_PITCH px off any grid) as 8 one-px-a-square figures."""
    from collections import Counter
    a = np.asarray(Image.open(K.lp(RUN_RAW)).convert("RGBA")).copy()
    rgb = a[..., :3].astype(int)
    a[(rgb[..., 1] > 170) & (rgb[..., 0] < 150) & (rgb[..., 2] < 150) & (rgb[..., 1] - rgb[..., 0] > 60)] = 0
    pal = np.array(palette)
    near = {}

    def nearest(c):
        c = tuple(int(v) for v in c)
        if c not in near:
            near[c] = tuple(int(v) for v in pal[((pal - np.array(c)) ** 2).sum(1).argmin()])
        return near[c]

    cw, ch = a.shape[1] // 4, a.shape[0] // 2
    out = []
    for i in range(8):
        cell = a[(i // 4) * ch:(i // 4 + 1) * ch, (i % 4) * cw:(i % 4 + 1) * cw]
        ys, xs = np.nonzero(cell[..., 3] > 0)
        bot, P = ys.max() + 1, RUN_PITCH
        H, W = int(np.ceil((bot - ys.min()) / P)) + 1, int(np.ceil((xs.max() - xs.min()) / P)) + 2
        x0 = xs.min() - P
        sm = np.zeros((H, W, 4), np.uint8)
        for r in range(H):
            yA = bot - (H - r) * P
            for c in range(W):
                xA = x0 + c * P
                blk = cell[max(0, int(round(yA))):int(round(yA + P)), max(0, int(round(xA))):int(round(xA + P))]
                al = blk[..., 3] > 0
                if blk.size == 0 or al.mean() < 0.5:
                    continue
                sm[r, c, :3] = Counter(nearest(p[:3]) for p in blk[al]).most_common(1)[0][0]
                sm[r, c, 3] = 255
        ys, xs = np.nonzero(sm[..., 3])
        out.append(sm[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
    return out


def drop_crumbs(a, most):
    """Opaque pieces of up to `most` squares cleared."""
    for comp in K.pieces(a)[1:]:
        if len(comp) <= most:
            for y, x in comp:
                a[y, x] = 0
    return a


def masks(a):
    yy, xx = np.mgrid[0:128, 0:128]
    op = a[..., 3] > 0
    rear = op & ((yy <= 54) | ((yy == 55) & (xx <= 60)) | ((yy >= 56) & (yy <= 66) & (xx <= 55))
                 | ((yy >= 67) & (yy <= 77) & (xx <= 46)))
    return rear


def head_mask(a):
    """The bald head, the eyes and the mask down to the chin (rows 59-72, the face's columns), not the spikes."""
    yy, xx = np.mgrid[0:128, 0:128]
    m = (yy >= 59) & (yy <= 80) & (xx >= 64) & (xx <= 81) & (a[..., 3] > 0)
    keep = np.zeros_like(m)
    # the head and mask squares: skin, red, bone stripes, eyes and the outline round them, by rows
    rows = {59: (69, 76), 60: (66, 79), 61: (65, 79), 62: (65, 80), 63: (65, 80), 64: (65, 80), 65: (65, 80),
            66: (65, 80), 67: (65, 80), 68: (65, 80), 69: (66, 80), 70: (66, 79), 71: (67, 78), 72: (67, 78),
            73: (68, 77), 74: (68, 77), 75: (68, 76), 76: (69, 76), 77: (70, 75), 78: (71, 74), 79: (72, 73)}
    for r, (c0, c1) in rows.items():
        keep[r, c0:c1 + 1] = True
    return m & keep


def darker(s, L):
    """One shade darker in the leg's own materials (the far leg)."""
    m = {L["k"]: L["e"], L["e"]: L["a"], L["a"]: L["0"], L["l"]: L["f"], L["f"]: L["b"], L["p"]: L["n"],
         L["n"]: L["k"], L["u"]: L["r"], L["r"]: L["p"], L["x"]: L["u"]}
    out = s.copy()
    for src, dst in m.items():
        sel = (s[..., :3] == np.array(src, np.uint8)).all(-1) & (s[..., 3] > 0)
        out[sel, :3] = dst
    return out


class Rig:
    def __init__(self):
        self.d = K.Design(DESIGN)
        a = self.d.a
        self.a = a
        self.out = self.d.outline
        rear = masks(a)
        self.body = a.copy()
        self.body[rear] = 0
        self.rear = K.Part.from_canvas(a, rear, SHOULDER)
        pal = {k: v for k, v in self.d.letters().items()}
        weapon_cols = [pal[k] for k in "jgcmuxrnpvtyzAsqlk"]           # gold, red, bone, gem: the harpoon
        arm = rear & ~K.colour_mask(a, weapon_cols) & (np.mgrid[0:128, 0:128][0] >= 59)
        self.arm = K.Part.from_canvas(a, arm, SHOULDER)
        skin = K.colour_mask(a, [pal[k] for k in "imo"])        # the arm's skin: the glove stays as the grip
        self.harpoon = K.Part.from_canvas(a, rear & ~(skin & (np.mgrid[0:128, 0:128][1] >= 46)), SHOULDER)
        yy, xx = np.mgrid[0:128, 0:128]
        front = (a[..., 3] > 0) & (xx >= 83) & (yy >= 80) & (yy <= 96)
        self.front_m = front
        self.front = K.Part.from_canvas(a, front, FRONT_SHOULDER)
        hm = head_mask(a)
        self.head = np.where(hm[..., None], a, 0).astype(np.uint8)
        self.hm = hm
        self.head_at = set()                   # every offset the head is pasted at (the shrink keeps clear of them)

    # ---------------------------------------------------------------- a standing frame
    def stand(self, rear=0, at=None, dx=0, dy=0, part=None, under=True):
        """The idle body moved dx, dy; REAR (or `part`) turned `rear` degrees (counter-clockwise) at `at`."""
        c = np.zeros_like(self.a)
        K.put(c, self.body, dx, dy)
        p = part if part is not None else self.rear
        if p is not False:
            p = K.turn(p, rear) if rear else p
            jx, jy = at if at is not None else SHOULDER
            K.place(c, p, (jx + dx, jy + dy), under=under)
        K.put(c, self.head, dx, dy)
        self.head_at.add((dx, dy))
        keep = K.shifted(np.repeat(self.hm[..., None], 4, -1).astype(np.uint8) * 255, dx, dy)[..., 3] > 0
        return K.finish(c, self.out, SOLES, keep=keep)

    def run(self):
        """Codex's legs under the design's own upper body: matched on the belt (the legs hang from the hips) for the
        column, the upper body at the idle's height (a row lower in Codex's low frames) with the legs' top rows under it."""
        des = self.a
        dys, dxs = np.nonzero(des[..., 3])
        mid = (dxs.min() + dxs.max()) // 2
        yy, xx = np.mgrid[0:128, 0:128]
        belt = (yy >= 76) & (yy <= 84) & (xx >= 50) & (xx <= 80) & (des[..., 3] > 0)
        belt4 = np.repeat(belt[..., None], 4, -1).astype(np.uint8) * 255
        placed = []
        for sm in read_run(self.d.palette):
            c = np.zeros_like(des)
            K.put(c, sm, mid - sm.shape[1] // 2, SOLES - sm.shape[0] + 1)
            best = max((int(((c[..., :3] == K.shifted(des, dx, dy)[..., :3]).all(-1)
                             & (K.shifted(belt4, dx, dy)[..., 3] > 0)).sum()), dx, dy)
                       for dx in range(-8, 9) for dy in range(-5, 5))
            placed.append((c, best[1], best[2]))
        top = min(p[2] for p in placed)
        up = des.copy()
        up[RUN_SEAM:] = 0
        hang = des.copy()
        hang[(yy < RUN_SEAM) | (xx < 76)] = 0
        hm4 = np.repeat(self.hm[..., None], 4, -1).astype(np.uint8) * 255
        L = self.d.letters()
        not_legs = [L[k] for k in "imobdhw"]          # skin, the coat's navy and teal
        frames = []
        for c, dx, dy in placed:
            # the upper body at the idle's height, a row lower where Codex's body is low: the run never stands taller
            # than the idle (on Codex's own height it stood up to two rows taller, 「移动时模型有点变形」); the legs' top
            # rows go under it
            at = 0 if dy <= top else 1
            out = np.zeros_like(des)
            legs = c.copy()
            legs[:RUN_SEAM + at] = 0                   # Codex's legs from just under where our upper body ends
            # Codex's own claw arm and coat hem on the near side: they lay 1-2 squares off the design's and doubled the
            # arm (「移动时手变形了」) - legs have no skin or navy, so those colours there go, the design's arm stays
            legs[(xx >= CLAW_X) & K.colour_mask(legs, not_legs)] = 0
            legs[:, CLAW_END:] = 0                     # and its arm's outline beside the design's (no leg reaches there)
            legs = drop_crumbs(legs, 6)
            K.put(out, legs, 0, 0)
            K.put(out, hang, dx, at)
            K.put(out, up, dx, at)
            keep = K.shifted(hm4, dx, at)[..., 3] > 0
            self.head_at.add((dx, at))
            out = self.trail_down(out, at)
            f = K.finish(out, self.out, SOLES, keep=keep)
            for comp in K.pieces(f)[1:]:
                if len(comp) < 12:
                    for y, x in comp:
                        f[y, x] = 0
            frames.append(f)
        return frames

    def trail_down(self, f, at):
        """The leg kicked back level behind him (Codex drew the trailing thigh flat, the boot hanging in the air:
        「这里腿都歪了吧？？」) turned down whole about the hip (RotSprite, no bend) until its boot is near the ground."""
        hip = (TRAIL_HIP[0], TRAIL_HIP[1] + at)
        m = np.zeros(f.shape[:2], bool)
        m[RUN_SEAM + at:, :TRAIL_X + 1] = True          # all of it under the upper body (no strip left at the hip)
        m &= f[..., 3] > 0
        ys, xs = np.nonzero(m)
        if not len(xs) or xs.min() > TRAIL_FROM:      # no leg out behind him
            return f
        leg = K.Part.from_canvas(f, m, hip)
        rest = f.copy()
        rest[m] = 0
        p = None
        for deg in range(5, 61, 5):                  # counter-clockwise: a leg pointing back (left) swings down
            q = K.turn(leg, deg)
            py = np.nonzero(q.s[..., 3].any(1))[0]
            low = int(np.floor(hip[1] - q.j[1] + 1e-9)) + int(py.max())
            if low > SOLES:
                break
            p = q
            if low >= SOLES - 2:
                break
        if p is None:
            return f
        out = np.zeros_like(f)
        K.place(out, p, hip)
        K.put(out, rest, 0, 0)
        return out

    def build(self):
        S = self.stand
        idle = [self.a.copy() for _ in MS["idle"]]
        attack = [S(), S(30, dx=-1), S(45, dx=-1), S(-45, RAISED, dx=2), S(-45, RAISED, dx=2), S(-15, dx=1)]
        stab = [S(15, dx=-1), S(30, dx=-2), S(-15, RAISED, dx=0), S(-45, RAISED, dx=3), S(0, dx=1)]
        skill = [S(15), S(45, dx=-1), S(45, dx=-2), S(45, dx=-1), S(-45, RAISED, dx=1, part=self.arm),
                 S(0, part=self.arm)]
        dive = [S(15, dx=-1), S(-45, RAISED, dx=2), S(-45, RAISED, dx=3), S(0, dx=1)]
        ult = [S(45), S(45, dy=-5), S(30, dy=-6), S(-45, RAISED, dx=2), S(-45, RAISED, dx=2), S(0, dx=1)]
        hit = [S(15, dx=-2), S(0, dx=-1)]
        return {"idle": idle, "run": self.run(), "attack": attack, "skill_stab": stab, "skill": skill, "skill2": dive, "ult": ult,
                "hit": hit, "dead": self.death()}

    def death(self):
        """league_sivir's: struck, knocked back (the harpoon slipping), falling (the figure turned 45 degrees back),
        lying on his back (a quarter turn), the harpoon on the ground beside him."""
        S = self.stand
        fig = np.zeros_like(self.a)                     # the figure without the harpoon: the far arm empty
        K.put(fig, self.body, 0, 0)
        K.place(fig, self.arm, SHOULDER, under=True)
        K.put(fig, self.head, 0, 0)
        whole = K.Part.from_canvas(fig, fig[..., 3] > 0, PIVOT)
        # lying: the legs together and straight - the design's near leg (the knee guard, drawn upright) twice under
        # the hips, the far one a shade darker behind it; the crouched legs and the coat's hem below the belt go
        yy, xx = np.mgrid[0:128, 0:128]
        upper = np.zeros_like(fig)
        K.put(upper, self.body, 0, 0)
        K.place(upper, K.turn(self.arm, 90), SHOULDER, under=True)   # the far arm down by his side
        K.put(upper, self.head, 0, 0)
        upper[self.front_m] = 0
        upper[yy >= 84] = 0
        K.place(upper, K.turn(self.front, -45), FRONT_SHOULDER)    # the claw arm straight down by his side
        leg_m = (yy >= 81) & (xx >= 47) & (xx <= 58) & (self.a[..., 3] > 0)
        leg = np.where(leg_m[..., None], self.a, 0).astype(np.uint8)
        straight = np.zeros_like(fig)
        K.put(straight, darker(leg, self.d.letters()), 8, -6)
        K.put(straight, upper, 0, 0)
        K.put(straight, leg, 4, -5)
        flat = K.Part.from_canvas(straight, straight[..., 3] > 0, PIVOT)
        harpoon = K.turn(self.harpoon, -45)             # level, lying on the ground (no hand on it)

        def lie(deg, dx, ground=True):
            c = np.zeros_like(self.a)
            p = K.turn(flat if deg == 90 else whole, deg)
            ys, xs = np.nonzero(p.s[..., 3])
            # the lowest square on the soles' row, the figure's middle dx left of the standing point
            top = SOLES - ys.max()
            left = int(round(PIVOT[0] + dx - (xs.min() + xs.max()) / 2))
            if ground:
                hy = np.nonzero(harpoon.s[..., 3].any(1))[0]
                K.put(c, harpoon.s, PIVOT[0] + 4, SOLES - int(hy.max()))
            K.put(c, p.s, left, top)
            return K.finish(c, self.out, SOLES)

        return [S(15, dx=-2), S(45, dx=-4), lie(45, -6, False), lie(70, -8), lie(90, -9), lie(90, -9), lie(90, -9),
                lie(90, -9)]


# the whole figure a little smaller (the user: 「然后看看整体模型能不能缩小点 略微缩小」; at the design's size he stood
# 53 x 62 squares, Darius 42 x 36): one square row in every SHRINK above the soles and one column in every SHRINK each
# side of the standing column comes out of every frame of every strip alike - in each such band the row (column) most
# like its neighbour over all the frames (the idle and the run counted thrice), never through the head (drops), so the
# face is the idle's in every frame; the soles and the standing column never move (47 x 55 now). No resampling: what is
# left is the design's own squares.
SHRINK = 8


def bands(start, stop, step):
    """Whole bands of |step| squares from `start` outward (step < 0: towards smaller indices), none past `stop`."""
    res, d = [], 1 if step > 0 else -1
    while True:
        b = [start + d * j for j in range(abs(step))]
        if (b[-1] - stop) * d > 0:
            return res
        res.append(b)
        start += step


def drops(built, k, head=None):
    """The rows and columns to drop: one per band, the least different from the square row / column beyond it. Never
    a row or column through the head where any frame has it (`head`: (mask, offsets)): cut there, the eyes changed
    from frame to frame as the run bobbed a row and the swings moved him a column (「派克移动时眼睛那变形？」) - a
    band all over the head gives its square to the nearest free row (column) beyond it."""
    frs, w = [], []
    for tag, fl in built.items():
        for f in fl:
            frs.append(f)
            w.append(3 if tag in ("idle", "run") else 1)
    alpha = np.array([f[..., 3] > 0 for f in frs])
    ys = np.nonzero(alpha.any((0, 2)))[0]
    xs = np.nonzero(alpha.any((0, 1)))[0]
    W = np.array(w, float)[:, None]
    st = np.stack(frs).astype(int)

    def cost(axis, i, j):
        a = np.take(st, i, axis=axis + 1)
        b = np.take(st, j, axis=axis + 1)
        diff = (np.abs(a - b).sum(-1) > 0)
        return float((diff * W).sum())

    hr, hc = set(), set()
    if head is not None:
        m, offs = head
        my, mx = np.nonzero(m)
        for dx, dy in offs:
            hr.update(range(int(my.min()) + dy, int(my.max()) + dy + 1))
            hc.update(range(int(mx.min()) + dx, int(mx.max()) + dx + 1))

    def pick(bs, free, key, lo, hi):
        got = []
        ok = lambda r: r not in free and all(g is None or abs(r - g) > 1 for g in got)
        for b in bs:
            c = [r for r in b if ok(r)]
            got.append(min(c, key=key) if c else None)
        for i, g in enumerate(got):
            if g is None:
                c = [r for r in range(lo, hi + 1) if ok(r)]
                got[i] = min(c, key=lambda r: (min(abs(r - x) for x in bs[i]), key(r)))
        return sorted(got)

    rows = pick(bands(SOLES - 1, int(ys.min()), -k), hr, lambda r: cost(0, r, r - 1), int(ys.min()), SOLES - 1)
    left = pick(bands(PIVOT[0] - 1, int(xs.min()), -k), hc, lambda c: cost(1, c, c + 1), int(xs.min()), PIVOT[0] - 1)
    right = pick(bands(PIVOT[0] + 1, int(xs.max()), k), hc, lambda c: cost(1, c, c - 1), PIVOT[0] + 1, int(xs.max()))
    return rows, left, right


def shrink(f, rows, left, right):
    """The frame without those rows (the rest dropped down onto the soles) and columns (closed in on the standing
    column)."""
    h, w = f.shape[:2]
    keep_r = [r for r in range(h) if r not in rows]
    keep_c = [c for c in range(w) if c not in left and c not in right]
    g = f[keep_r][:, keep_c]
    out = np.zeros_like(f)
    out[len(rows):, len(left):len(left) + g.shape[1]] = g
    return out


def shrunk_xy(x, y, rows, left, right):
    """Where a canvas square (x, y) lands after shrink."""
    return (x + sum(1 for c in left if c > x) - sum(1 for c in right if c < x),
            y + sum(1 for r in rows if r > y))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", help="folder for the review sheet")
    ap.add_argument("--tags")
    a = ap.parse_args()
    rig = Rig()
    built = rig.build()
    if SHRINK:
        cut = drops(built, SHRINK, (rig.hm, rig.head_at))
        built = {t: [shrink(f, *cut) for f in fl] for t, fl in built.items()}
        print("shrink: rows", cut[0], "columns", cut[1], cut[2])
    if a.tags:
        built = {t: built[t] for t in a.tags.split(",")}
    for tag, frs in built.items():
        rows = K.audit(frs, rig.a, rig.out, SOLES)
        print(tag, [(r["pieces"], r["holes"], r["orphans"], r["below"], r["area"]) for r in rows])
    if a.review:
        K.review_sheet(list(built.items()), os.path.join(a.review, "pyke_rig.png"), z=4, soles=SOLES)
        return
    bad = K.write_strips(HERO, built, {t: MS[t] for t in built}, NATIVE, CELL, CELL_PIVOT, PIVOT, check=a.check)
    print("differs:" if a.check else "written", bad if a.check else NATIVE)


if __name__ == "__main__":
    main()
