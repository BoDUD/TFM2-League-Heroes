#!/usr/bin/env python3
"""Draven's action strips from Codex's step-2 frames (assets/source/draven/codex_strips) + the approved design.

    python tools/art/fix_draven_strips.py [--run M|V] [--review DIR]

Writes assets/source/native/draven_<tag>.png (every frame a 128 x 128 canvas cell at 8x, the soles on row 99, the
standing point on column 64) and draven_cells.json; then tools/art/import_native.py --hero draven.

Codex drew every frame as one image after League's pose (STRIPS_PROMPTS: assets/source/draven/MODEL_STRIPS.md). The
user on the delivery (2026-10-10): 「Codex做的东西有点奇怪 请你帮忙修复」 and, on the run, 「我记得德莱文在联盟里的走路
姿势不是这样的」. What was off, and what this script does about it:
  - run: the pack kept the design's upper body (the far axe raised over the head) and asked only for the legs - League
    runs (and oppi's Draven runs) with both axes held low at his sides. RUN: the design's head, mantle, torso and near
    arm square for square, the far arm and its axe brought down (variant "M": the near arm + axe mirrored onto the far
    shoulder - both axes low at the sides like oppi's run; "V": the raised arm flipped upside down about the shoulder),
    Codex's crossing legs (it drew them into the pack's boot boxes) under it, the upper body bobbing BOB rows.
  - skill (Q, 4 x 50 ms): Codex redrew the whole body every frame (one frame 1.7 times the design, the raised arm on
    the other side in another) - it flickered. SPIN: the design itself, its raised axe spinning in the fist (lossless
    quarter turns about the fist, behind the body), the way oppi's Q keeps the body still.
  - attack: Codex raised the FAR axe in frames 2-3 and threw with the NEAR hand in frame 4, frame 5 had the axes in
    the other hands again and frame 6 mirrored the design. ATTACK: frame 1 (crouch, both axes low), frame 6 (the near
    axe raised - the wind-up for the near hand), frame 4 (the throw, the near hand empty), then the idle.
  - skill2 / ult: their last frame was the design mirrored (attack 6, skill2 6) or another man (ult 7, slim, front-on,
    no axes): dropped, the previous frame held longer.
  - dead: the three lying frames were three different jumbles: frame 4 held for all of them.
Timings: the release frames start where the kit fires (attack 180 ms = tick 11, E 180 ms = tick 11, R 270 ms = tick 16).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "draven", "codex_strips", "1x")
DESIGN = os.path.join(ROOT, "assets", "source", "native", "draven_native.png")
OUT = os.path.join(ROOT, "assets", "source", "native")
sys.path.insert(0, HERE)
Z = 8
SOLES, MID = 99, 64
PIVOT = (MID, SOLES - 11)          # 11 rows over the soles, as tools/lol/native_pose.py puts it
BOB = [0, 1, 1, 0, 0, 1, 1, 0]     # the run's upper body (the pack's a_upper_body.png per frame)
HIP_ROW, AXE_X, AXE_LOW = 81, 80, 93   # the pack kept the design's rows < 81 and the near axe (rows 81-93, cols >= 80)

# (tag, [(source, ms)]): a source is a Codex frame name, "design", ("spin", quarter turns) or ("run", k)
TAGS = {
    "idle": [("design", 140)],
    "run": [(("run", k), 100) for k in range(8)],
    "attack": [("attack_1", 80), ("attack_6", 100), ("attack_4", 220)],
    "skill": [(("spin", 1), 50), (("spin", 2), 50), (("spin", 3), 50), ("design", 50)],
    "skill2": [("skill2_1", 60), ("skill2_2", 60), ("skill2_3", 60), ("skill2_4", 80), ("skill2_5", 140)],
    "ult": [("ult_1", 60), ("ult_2", 70), ("ult_3", 70), ("ult_4", 70), ("ult_5", 80), ("ult_6", 150)],
    "hit": [("hit_1", 100)],
    "dead": [("dead_1", 100), ("dead_2", 100), ("dead_3", 120), ("dead_4", 750)],
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def load(path):
    a = np.asarray(Image.open(lp(path)).convert("RGBA"))
    a = a[Z // 2::Z, Z // 2::Z] if a.shape[0] == 128 * Z else a
    a = a.copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] >= 128, 3] = 255
    return a


def box(a, rows, cols):
    m = np.zeros(a.shape[:2], bool)
    m[rows[0]:rows[1] + 1, cols[0]:cols[1] + 1] = True
    return m & (a[..., 3] > 0)


# ---------------------------------------------------------------- the design's parts (canvas rows / columns)
def far_arm(d):
    """The raised far arm with its axe: the axe and fist (rows 46-62 left of the head), the wrap and the upper arm
    down to the shoulder (rows 63-69, left of the mantle's teal/fur)."""
    m = box(d, (46, 62), (36, 57))
    m |= box(d, (63, 64), (36, 54))
    m |= box(d, (65, 65), (36, 53)) | box(d, (66, 66), (36, 52)) | box(d, (67, 67), (36, 53))
    m |= box(d, (68, 69), (36, 52))
    return m


def far_axe(d):
    """The raised axe alone (the fist and wrist, rows 56-62 columns 47-53, stay with the arm)."""
    return box(d, (46, 55), (36, 57)) | box(d, (56, 62), (36, 46))


FAR_FIST = (48.5, 56.5)            # the far fist's middle (both halves: a quarter turn maps squares onto squares)


def near_arm(d):
    """The near arm (upper arm from the mantle's edge, forearm, fist) with its axe - without the near leg's outline
    squares the box catches (pieces under 10 squares)."""
    m = box(d, (72, 83), (72, 84)) | box(d, (73, 93), (78, 91))
    lab, n = ndimage.label(m, structure=np.ones((3, 3)))
    for i in range(1, n + 1):
        if (lab == i).sum() < 10:
            m[lab == i] = False
    return m


M_ARM = (-4, -2)                   # the mirrored far arm's place: its skin upper arm shows left of the mantle


def TASSEL(d):
    """The crimson cloth hanging behind the far shoulder."""
    return box(d, (71, 80), (44, 55))


def turn(part, mask, centre, q):
    """`part` (masked) turned q quarter turns clockwise on screen about centre (x, y): lossless."""
    out = np.zeros_like(part)
    om = np.zeros(mask.shape, bool)
    cx, cy = centre
    for y, x in zip(*np.nonzero(mask)):
        dx, dy = x - cx, y - cy
        for _ in range(q % 4):
            dx, dy = -dy, dx
        X, Y = int(round(cx + dx)), int(round(cy + dy))
        if 0 <= X < 128 and 0 <= Y < 128:
            out[Y, X] = part[y, x]
            om[Y, X] = True
    return out, om


def flip(part, mask, axis, at):
    """Mirrored about column `at` (axis "h") or row `at` (axis "v")."""
    out = np.zeros_like(part)
    om = np.zeros(mask.shape, bool)
    for y, x in zip(*np.nonzero(mask)):
        X, Y = (2 * at - x, y) if axis == "h" else (x, 2 * at - y)
        if 0 <= X < 128 and 0 <= Y < 128:
            out[Y, X] = part[y, x]
            om[Y, X] = True
    return out, om


def shift(a, dx, dy):
    out = np.zeros_like(a)
    H, W = a.shape[:2]
    ys0, ys1 = max(0, dy), min(H, H + dy)
    xs0, xs1 = max(0, dx), min(W, W + dx)
    out[ys0:ys1, xs0:xs1] = a[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
    return out


def over(dst, src):
    """src drawn over dst (src's opaque squares win)."""
    out = dst.copy()
    m = src[..., 3] > 0
    out[m] = src[m]
    return out


# ---------------------------------------------------------------- Q: the raised axe spinning in the fist
def spin(d, q):
    """The design with its raised axe turned q quarter turns about the fist, drawn behind the body."""
    ax = far_axe(d)
    body = d.copy()
    body[ax] = 0
    part = np.zeros_like(d)
    part[ax] = d[ax]
    t, tm = turn(part, ax, FAR_FIST, q)
    return over(t, body)


# ---------------------------------------------------------------- the run
def run_upper(d, variant):
    """The run's upper body: the design without its raised far arm, the far arm + axe brought down, the legs gone
    (everything under the belt but the near axe)."""
    fm = far_arm(d)
    body = d.copy()
    body[fm] = 0
    if variant == "V":                                   # the raised arm flipped upside down about the shoulder row
        part = np.zeros_like(d)
        part[fm] = d[fm]
        arm, am = flip(part, fm, "v", 70)
    else:                                                # the near arm + axe mirrored onto the far shoulder
        nm = near_arm(d)
        part = np.zeros_like(d)
        part[nm] = d[nm]
        arm, am = flip(part, nm, "h", 64)
        arm = shift(arm, *M_ARM)
        # the crimson cloth hanging behind the far shoulder goes under the arm (over it, the arm's skin was hidden
        # and only its red wrap showed: a red stump)
        cloth = TASSEL(d)
        under = np.zeros_like(d)
        under[cloth] = d[cloth]
        body[cloth] = 0
        arm = over(under, arm)
    legs = np.zeros(d.shape[:2], bool)
    legs[HIP_ROW:] = True
    legs[HIP_ROW:AXE_LOW + 1, AXE_X:] = False
    body[legs] = 0
    return arm, body


def codex_legs(d, k):
    """Codex's legs in run frame k: its frame minus the pack's upper body (the design's rows < 81 and the near axe,
    moved down BOB[k]) wherever that upper body is opaque and Codex kept it."""
    fr = load(os.path.join(SRC, f"run_{k + 1}.png"))
    up = d.copy()
    keep = np.zeros(d.shape[:2], bool)
    keep[:HIP_ROW] = True
    keep[HIP_ROW:AXE_LOW + 1, AXE_X:] = True
    up[~keep] = 0
    up = shift(up, 0, BOB[k])
    same = (up[..., 3] > 0) & (fr == up).all(-1)
    legs = fr.copy()
    legs[same] = 0
    return legs


WAIST = (70, 92, 44, 64)           # rows, columns by the far hip: gaps there are closed with the trousers' shadow
SHADOW = (0x29, 0x2A, 0x32)


RAW = os.path.join(ROOT, "assets", "source", "draven", "codex_strips", "raw")
PITCH = 1254 / 128                 # the generator drew the 1024 canvas at 1254 px: one game square = 9.8 px


def raw_legs(d, k):
    """The legs as the generator drew them in run frame k (raw/run_<k>.png read on the 128 grid: each square the
    median of its middle 3 x 3, the nearest design colour in CIELAB) - Codex's own 1x had moved and resampled them
    into the pack's boot boxes, which broke them into thin specks (the user: 「腿部严重变形」). Everything under the
    belt but the near axe, lifted so the soles stand on row 99."""
    import design_rengar as R
    pal = np.unique(d[d[..., 3] > 0][:, :3], axis=0)
    pl = R.lab(pal.astype(float))
    im = np.asarray(Image.open(lp(os.path.join(RAW, f"run_{k + 1}.png"))).convert("RGBA")).astype(float)
    a = np.zeros((128, 128, 4), np.uint8)
    for y in range(HIP_ROW - 2, 128):
        for x in range(128):
            cy, cx = int((y + 0.5) * PITCH), int((x + 0.5) * PITCH)
            if not (1 <= cy < im.shape[0] - 1 and 1 <= cx < im.shape[1] - 1):
                continue
            blk = im[cy - 1:cy + 2, cx - 1:cx + 2].reshape(-1, 4)
            if (blk[:, 3] >= 128).mean() < 0.5:
                continue
            c = np.median(blk[blk[:, 3] >= 128][:, :3], axis=0)
            a[y, x, :3] = pal[((R.lab(c[None]) - pl) ** 2).sum(-1).argmin()]
            a[y, x, 3] = 255
    b = BOB[k]
    a[:HIP_ROW + b] = 0
    a[:AXE_LOW + b + 1, AXE_X:] = 0
    ys = np.nonzero(a[..., 3])[0]
    return shift(a, 0, SOLES - ys.max()) if len(ys) and ys.max() > SOLES else a


# the raw legs of frames 1-4 make one whole stride (the near foot lands in 4, pushes back through 1-2, swings in 3;
# the far one lands in 3, pushes back in 4, kicks up in 1, swings in 2); frames 5-8 kept both feet where 1-4 had
# them (no swap), so the run plays 1-4 twice (two legs alike: a stride and its half-cycle twin look the same)
LEG_SRC = [0, 1, 2, 3, 0, 1, 2, 3]
LEGS = "rig"                       # "rig": rig_draven_legs.py on League's skeleton; "raw": the generator's legs


RIBBONS = (80, 93, 57, 67)          # rows, columns: the belt's ribbons hanging between the legs in the design
RIBBON_COLOURS = {(0xCA, 0x22, 0x4A), (0x74, 0x23, 0x42), (0x9C, 0x34, 0x4C), (0x08, 0x70, 0x82), (0x06, 0x48, 0x53),
                  (0x42, 0x1D, 0x30), (0x1A, 0x0E, 0x0E)}


def ribbons(d):
    """The design's ribbons under the belt (crimson, teal and their outline), drawn over the rigged legs."""
    r0, r1, c0, c1 = RIBBONS
    out = np.zeros_like(d)
    for y in range(r0, r1 + 1):
        for x in range(c0, c1 + 1):
            if d[y, x, 3] and tuple(int(v) for v in d[y, x, :3]) in RIBBON_COLOURS:
                out[y, x] = d[y, x]
    return out


def run_frame(d, k, variant):
    arm, body = run_upper(d, variant)
    if LEGS == "rig":
        import rig_draven_legs as RL
        legs = over(RL.legs(k), shift(ribbons(d), 0, BOB[k]))
    else:
        legs = raw_legs(d, LEG_SRC[k])
    up = over(shift(arm, 0, BOB[k]), shift(body, 0, BOB[k]))   # the body over the far arm's root
    fr = over(legs, up)
    # Codex's hips were drawn for the raised-arm body: lowered, the far arm closes a pocket by the far hip in the
    # bobbing frames - the far hip's shadow fills it (the axes' ring holes stay open)
    op = fr[..., 3] > 0
    holes = ndimage.binary_fill_holes(op) & ~op
    lab, n = ndimage.label(holes)
    r0, r1, c0, c1 = WAIST
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if len(ys) >= 3 and r0 <= ys.min() and ys.max() <= r1 and c0 <= xs.min() and xs.max() <= c1:
            fr[ys, xs, :3] = SHADOW
            fr[ys, xs, 3] = 255
    return fr


# ---------------------------------------------------------------- the strips
def frame_of(d, src, variant):
    if src == "design":
        return d.copy()
    if isinstance(src, tuple) and src[0] == "spin":
        return spin(d, src[1])
    if isinstance(src, tuple) and src[0] == "run":
        return run_frame(d, src[1], variant)
    return load(os.path.join(SRC, f"{src}.png"))


def layout(n):
    cols = {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)
    return cols, -(-n // cols)


def build(variant="M"):
    d = load(DESIGN)
    return {tag: [(frame_of(d, src, variant), ms) for src, ms in rows] for tag, rows in TAGS.items()}


def write(sheet):
    cells = {"cell": [128, 128], "scale": Z, "tags": {}}
    for tag, frames in sheet.items():
        cols, rows = layout(len(frames))
        strip = np.zeros((rows * 128, cols * 128, 4), np.uint8)
        for k, (a, ms) in enumerate(frames):
            r, c = divmod(k, cols)
            strip[r * 128:(r + 1) * 128, c * 128:(c + 1) * 128] = a
        Image.fromarray(strip).resize((cols * 128 * Z, rows * 128 * Z), Image.NEAREST).save(
            lp(os.path.join(OUT, f"draven_{tag}.png")))
        cells["tags"][tag] = [{"pivot": list(PIVOT), "ms": ms} for _, ms in frames]
    with open(lp(os.path.join(OUT, "draven_cells.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write("{" + json.dumps({"cell": cells["cell"], "scale": Z})[1:-1] + ', "tags": {\n')
        f.write(",\n".join(f'  "{t}": ' + json.dumps(v) for t, v in cells["tags"].items()))
        f.write("\n}}\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", default="M", choices=["M", "V"])
    ap.add_argument("--review", help="write <tag>_<k>.png (128 x 128) here instead of the strips")
    a = ap.parse_args()
    sheet = build(a.run)
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        for tag, frames in sheet.items():
            for k, (fr, _) in enumerate(frames):
                Image.fromarray(fr).save(os.path.join(a.review, f"{tag}_{k + 1}.png"))
        print("review frames in", a.review)
        return
    write(sheet)
    print("wrote", ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))


if __name__ == "__main__":
    main()
