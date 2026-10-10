#!/usr/bin/env python3
"""Syndra's action strips posed from the approved design's own parts (2026-10-11): the casting body = the idle's.

    python tools/art/rig_syndra.py [--check] [--review DIR]

Codex's step-2 delivery (assets/source/syndra/codex_strips/) built every frame by script from the design's parts, but
it turned the arms by any angle (-30, -135, 5-8 degrees in the run: rounded rotations of a 1-square arm), took the
image-left arm off the hair in W, E and R and filled the hair it had covered with ONE flat lavender (a grey slab beside
her), hid that hand behind the body in W 3-4, E 2-3 and R 3-4, laid the death down through a 45-degree raster turn,
and its run moved squares no rig step names (87 changed squares in a frame with every transform at 0). The user:
「有问题的帮我修复 做到完美了喊我review」. So every frame here is the design (assets/source/native/syndra_native.png,
tools/art/design_syndra.py) with only what the action moves moved, nothing resampled (the pack's rules: a moved limb is
one rigid unit, posed by exact quarter turns, mirrors and whole-row / whole-column moves; no squares made up):
- the image-left arm lies OVER the long hair: taking it away would bare hair nobody drew, so it never moves.
- the image-right arm (ARM: Codex's own cut, 26 squares - the 1-square arm, the magenta glove and claws and the outline
  ring that is theirs) takes five poses about its shoulder: HANG (as drawn, down and forward), STEEP (transposed: a
  little more down), UP (a quarter turn counter-clockwise: raised forward beside her hair), UPF (mirrored top to
  bottom: raised forward, the glove a row lower) and LEVEL (whole columns moved up: held straight out in front).
- the whole figure moves: a column or two back / forward (the wind-ups, the throws, the hit's recoil) and up (Q's and
  R's rise - she floats); the idle is a hover (the whole figure 0-2 rows up, the hand drifting between HANG and STEEP;
  import_native's own breath, which takes rows out of the legs, is skipped for her); the run is League's glide: the
  whole figure bobs a row twice a loop and the hanging boot trails up to two columns behind (its rows moved whole, the
  more the lower: rigkit's leg shear) while the hand swings between HANG and STEEP.
- the death is League's: struck back, then she sinks onto her hanging leg - the boot's straight rows (SINK_ROWS) go
  and everything above comes down onto the toe (up to four rows: a kneel by whole rows, the toe and the ground kept).
Each built frame is finished only round what moved (rigkit.finish, every square further than 2 from a change kept):
the outline closed on the moved edges, pinholes filled, stray outline squares dropped. Then the audit: pieces, holes,
orphan outline squares, nothing under the soles, the head (HEAD_BOXES of pack_syndra_strips) the design's in every
frame, the image-left arm the design's in every frame.
Writes assets/source/native/syndra_<tag>.png (8x, 96 x 88 cells) and syndra_cells.json; then tools/art/import_native.py.
--check compares instead of writing; --review writes a review sheet and GIF.
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
SRC = os.path.join(ROOT, "assets", "source", "syndra", "codex_strips")
DESIGN = os.path.join(NATIVE, "syndra_native.png")
ARM_CUT = os.path.join(SRC, "rig", "right_arm.png")       # Codex's cut of the image-right arm (26 squares)
Z = 8
PIVOT = (64, 88)                 # the design's standing point (the lowest toe on row 99, column 64)
SOLES = 99
CELL = (96, 88)
CELL_PIVOT = (48, 64)            # the soles on cell row 75 (the references' feet line)
SHOULDER = (68.5, 80.5)          # the centre of the arm's shoulder square
HEAD_BOXES = [(58, 67, 54, 73), (68, 76, 59, 72)]   # rows r0..r1, columns c0..c1: the head pasted in every frame
LEFT_CUT = os.path.join(SRC, "rig", "left_arm.png")       # Codex's cut of the image-left arm: never moved, checked
TAGS = ["idle", "run", "attack", "skill", "skill2", "skill2_e", "ult", "hit", "dead"]
MS = {"idle": [140] * 8, "run": [133] * 8, "attack": [83, 84, 100, 100, 100], "skill": [67, 67, 100, 166],
      "skill2": [100] * 5, "skill2_e": [67, 67, 100, 166], "ult": [117, 116, 150, 150, 134], "hit": [100, 100],
      "dead": [100, 100, 100, 120, 150, 200, 300, 400]}
# per frame: (arm pose, dx, lift); release frames (3) as the kit times them: attack tick 10, Q 8, W 12, E 8, R 14
POSES = {
    "attack": [("hang", 0, 0), ("up", -1, 0), ("level", 1, 0), ("level", 1, 0), ("hang", 0, 0)],
    "skill": [("upf", 0, 0), ("up", 0, 1), ("level", 1, 0), ("hang", 0, 0)],
    "skill2": [("level", 1, 0), ("up", -1, 1), ("level", 2, 0), ("steep", 1, 0), ("hang", 0, 0)],
    "skill2_e": [("steep", -1, 0), ("up", -1, 0), ("level", 2, 0), ("hang", 0, 0)],
    "ult": [("upf", 0, 1), ("up", 0, 2), ("level", 1, 2), ("level", 1, 1), ("hang", 0, 0)],
    "hit": [("hang", -2, 0), ("hang", -1, 0)],
}
IDLE = [("hang", 0), ("hang", 1), ("hang", 1), ("steep", 2), ("steep", 2), ("steep", 1), ("hang", 1), ("hang", 0)]
RUN_BOB = [0, 1, 1, 0, 0, 1, 1, 0]
RUN_TRAIL = [0, -1, -2, -1, 0, -1, -2, -1]
RUN_ARM = ["hang", "hang", "steep", "steep", "hang", "hang", "steep", "steep"]
BOOT_TOP, TOE_ROW = 91, 99       # the hanging boot: its gold top to the toe
BOOT_COLS = (62, 67)             # its columns (the bent leg's boot is right of them, the skirt left)
SINK_ROWS = [96, 95, 94, 93]     # the boot's straight rows, taken out in this order as she sinks
DEAD = [(-1, 0), (-2, 1), (-2, 2), (-2, 3), (-2, 4), (-2, 4), (-2, 4), (-2, 4)]     # (dx, rows sunk)
N8 = tuple((a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if a or b)


def design():
    a = np.asarray(Image.open(K.lp(DESIGN)).convert("RGBA"))
    a = (a if a.shape[0] == 128 else a[Z // 2::Z, Z // 2::Z]).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    return a


def boxes(bx):
    m = np.zeros((128, 128), bool)
    for r0, r1, c0, c1 in bx:
        m[r0:r1 + 1, c0:c1 + 1] = True
    return m


class Parts:
    def __init__(self):
        d = design()
        self.design = d
        self.outline = K.Design(DESIGN).outline
        cut = np.asarray(Image.open(K.lp(ARM_CUT)).convert("RGBA"))
        self.arm_m = cut[..., 3] > 0
        assert (cut[self.arm_m] == d[self.arm_m]).all(), "Codex's arm cut is not the design's squares"
        self.body = d.copy()
        self.body[self.arm_m] = 0
        hang = K.Part.from_canvas(d, self.arm_m, SHOULDER)
        self.arm = {"hang": hang, "steep": hang.transpose(), "up": K.rot90(hang, 3), "upf": hang.flip_v(),
                    "level": K.level(hang.flip_h()).flip_h()}
        self.head_m = boxes(HEAD_BOXES) & (d[..., 3] > 0)
        left = np.asarray(Image.open(K.lp(LEFT_CUT)).convert("RGBA"))
        self.left_m = left[..., 3] > 0
        assert (left[self.left_m] == d[self.left_m]).all(), "Codex's left arm cut is not the design's squares"
        assert np.array_equal(self.put_arm("hang"), d)

    def put_arm(self, pose, base=None):
        c = (self.body if base is None else base).copy()
        K.place(c, self.arm[pose], SHOULDER)
        return c


def near(changed, r=2):
    m = changed.copy()
    for _ in range(r):
        g = m.copy()
        for dy, dx in N8:
            g |= np.roll(np.roll(m, dy, 0), dx, 1)
        m = g
    return m


def finish_near(a, ref, pinholes=4, protect=None):
    """rigkit.finish, but every square more than 2 from a square that differs from `ref` is kept as it is (and every
    `protect` square)."""
    keep = ~near((a != ref).any(-1))
    if protect is not None:
        keep |= protect
    return K.finish(a, OUTLINE, SOLES, keep=keep, pinholes=pinholes)


def posed(P, pose):
    """The design with the arm in `pose`, finished round the arm (the head and the image-left arm kept)."""
    return finish_near(P.put_arm(pose), P.design, protect=P.head_m | P.left_m)


def standing(P, pose):
    arm, dx, lift = pose
    c = posed(P, arm)
    return K.shifted(c, dx, -lift) if dx or lift else c


def idle_frames(P):
    return [K.shifted(posed(P, arm), 0, -up) if up else posed(P, arm) for arm, up in IDLE]


def boot_mask(P):
    """The hanging boot's squares from its gold top down (the bent leg and the skirt excluded)."""
    m = np.zeros((128, 128), bool)
    m[BOOT_TOP:TOE_ROW + 1, BOOT_COLS[0]:BOOT_COLS[1] + 1] = True
    return m & (P.design[..., 3] > 0)


def trailed(a, P, off):
    """The hanging boot's rows moved `off` columns (whole rows, in proportion from its top to the toe)."""
    if not off:
        return a
    m = boot_mask(P)
    boot = np.zeros_like(a)
    boot[m] = a[m]
    rest = a.copy()
    rest[m] = 0
    out = rest
    for y, x in zip(*np.nonzero(boot[..., 3] > 0)):
        sh = int(np.floor(off * (y - BOOT_TOP) / (TOE_ROW - BOOT_TOP) + 0.5))
        out[y, x + sh] = boot[y, x]
    return out


def run_frames(P):
    out = []
    for bob, trail, arm in zip(RUN_BOB, RUN_TRAIL, RUN_ARM):
        base = posed(P, arm)
        c = trailed(base, P, trail)
        c = finish_near(c, base, protect=P.head_m | P.left_m)
        out.append(K.shifted(c, 0, -bob) if bob else c)
    return out


def sunk(a, n):
    """She sinks n rows onto her toe: in the hanging boot's columns SINK_ROWS[:n] go and the rows above them come down
    over the gap; every other column comes down n rows whole (the skirt, the bent leg: nothing there is cut)."""
    if not n:
        return a
    gone = set(SINK_ROWS[:n])
    out = np.zeros_like(a)
    for y, x in zip(*np.nonzero(a[..., 3] > 0)):
        if BOOT_COLS[0] <= x <= BOOT_COLS[1]:
            if y in gone:
                continue
            yy = y + sum(1 for g in gone if g > y)
        else:
            yy = y + n
        if yy <= SOLES and out[yy, x, 3] == 0:
            out[yy, x] = a[y, x]
    return out


def dead_frames(P):
    """Struck back a column or two, then sinking up to four rows onto the toe; finished only round the boot's seam."""
    out = []
    for dx, n in DEAD:
        c = sunk(P.design.copy(), n)
        if n:
            seam = np.zeros((128, 128), bool)
            low = max(SINK_ROWS[:n]) + 1
            seam[low - 3:low + 3, BOOT_COLS[0] - 2:BOOT_COLS[1] + 3] = True
            c = K.finish(c, OUTLINE, SOLES, keep=~seam, pinholes=4)
        out.append(K.shifted(c, dx, 0) if dx else c)
    return out


def frames(P, tag):
    if tag == "idle":
        return idle_frames(P)
    if tag == "run":
        return run_frames(P)
    if tag == "dead":
        return dead_frames(P)
    return [standing(P, p) for p in POSES[tag]]


def head_ok(P, f):
    """(dx, dy, squares that differ) of the offset where the head's squares match best; the raised hand may lie over a
    few of them (the hair beside her face), nothing else may change."""
    ys, xs = np.nonzero(P.head_m)
    best = None
    for dy in range(-6, 7):
        for dx in range(-4, 5):
            bad = int((f[ys + dy, xs + dx] != P.design[ys, xs]).any(-1).sum())
            if best is None or bad < best[2]:
                best = (dx, dy, bad)
    return best


OUTLINE = None


def main():
    global OUTLINE
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", help="write a review sheet and GIF into this folder")
    a = ap.parse_args()
    P = Parts()
    OUTLINE = P.outline
    built = {tag: frames(P, tag) for tag in TAGS}
    bad_head = []
    for tag in TAGS:
        rows = K.audit(built[tag], P.design, OUTLINE, SOLES)
        heads = [head_ok(P, f) for f in built[tag]]
        bad_head += [f"{tag} {k + 1}" for k, h in enumerate(heads) if h[2] > 8]
        print(f"{tag:8s}", " ".join(f"{r['pieces']}p{r['holes']}h{r['orphans']}o{r['below']}b{r['area']}"
                                    for r in rows), "head", heads)
    if bad_head:
        print("HEAD CHANGED:", bad_head)
    bad = K.write_strips("syndra", built, MS, NATIVE, CELL, CELL_PIVOT, PIVOT, check=a.check)
    if a.check:
        print("differs:", bad or "nothing")
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        K.review_sheet([(t, built[t]) for t in TAGS], os.path.join(a.review, "syndra_rig_review.png"), z=4,
                       soles=SOLES)
    sys.exit(1 if a.check and bad else 0)


if __name__ == "__main__":
    main()
