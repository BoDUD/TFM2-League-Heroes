#!/usr/bin/env python3
"""Xayah's action strips posed from the approved design's own parts (2026-10-08): the casting body = the idle's.

    python tools/art/rig_xayah.py [--check] [--review DIR]

Codex's step-2 delivery (assets/source/xayah/codex_strips/) built every frame by moving the design's parts by script, but
the arms came out as flat slabs (a 1-square skin row between two outline rows, 「白棍」), the far arm a plank floating
beside the body, the feather cloak turned whole into a level bar at head height in standing frames (attack 3-4, E 1-2,
W 2, R 6-7: 「像火把」), and the death laid the body flat under an upright head. The user: 「完成下一步 有奇怪的地方你帮忙
修复」. Here (rigkit's way, league_varus / league_lissandra) every frame is the design (tools/art/design_xayah.py) with
only what the action moves moved:
- NEAR_ARM (image right: the arm under the bird skull, its bracer, the hand and the two feather blades) is taken off the
  design as one rigid unit and turned about the shoulder in exact quarter turns only (rigkit.rot90 - the user's pick on
  Tryndamere: never redrawn, never sheared): hanging (as drawn), FORWARD (pointing right at shoulder height: the throw)
  and BACK (pointing left, laid behind the body: the wind-up, and in R's leap). A raised arm (UP) was tried: a quarter
  turn stands it straight up over the hood and the blades covered the face, so Q and R wind up behind instead. After a throw the blades
  (BLADES, the unit's squares from row 89 down right of column 77) are left off for that frame and the next.
- the cloak, the legs and the head stay as the design has them in every standing frame (the cloak hangs; no bar);
  Q and R lift the whole figure (League's spring and leap: R up to 9 rows, inside the cell), the hit pushes it back.
- the death: the whole figure turned about the middle of the soles (rigkit.turn, RotSprite; quarter turns exact) as
  League's falls back - 0, 8, 20, 40, 65, then 90 degrees counter-clockwise: lying on her back, the head to the left
  and turned with the body (league_rakan's lying death), set down on the soles' row; the blades fall from the hand on
  frame 3 and lie flat on the ground beside her.
- the run is Codex's skin swap on oppi's Vayne run (6 x 135 ms, assets/source/xayah/codex_strips/xayah_run.png), only
  finished like the rest.
Every built frame is finished alike (rigkit.finish): pinholes filled, the outline closed round moved edges, stray
outline squares and crumbs dropped. Writes assets/source/native/xayah_<tag>.png (8x, 128x96 cells) and xayah_cells.json;
then tools/art/import_native.py. --check compares instead of writing; --review writes a review sheet and GIF.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rigkit as K  # noqa: E402

NATIVE = os.path.join(ROOT, "assets", "source", "native")
SRC = os.path.join(ROOT, "assets", "source", "xayah", "codex_strips")
DESIGN = os.path.join(NATIVE, "xayah_native.png")
Z = 8
PIVOT = (64, 88)                 # the design's standing point (the soles on row 99, the feet's middle on column 64)
SOLES = 99
OUT = (0x0B, 0x04, 0x0E)
CELL = (128, 96)
CELL_PIVOT = (64, 69)            # the soles on cell row 80 (the references' feet line)
SHOULDER = (76.5, 80.5)          # the near arm's joint, under the bird skull
TAGS = ["idle", "run", "attack", "skill", "skill_e", "skill2", "ult", "hit", "dead"]
MS = {"idle": [200] * 6, "run": [135] * 6, "attack": [70, 70, 80, 70, 60, 50], "skill": [70, 70, 80, 80],
      "skill_e": [80, 80, 90, 83], "skill2": [100] * 4, "ult": [120, 130, 150, 200, 200, 150, 120, 97],
      "hit": [100, 100], "dead": [100, 110, 110, 120, 130, 150, 200, 300]}
# per frame: (arm, blades, dx, lift) - arm "hang" | "fwd" | "up" | "back"; None = the design itself
POSES = {
    "attack": [("hang", True, 0, 0), ("back", True, -1, 0), ("fwd", False, 1, 0), ("fwd", False, 1, 0),
               ("hang", True, 0, 0), None],
    "skill": [("back", True, 0, 0), ("back", True, 0, 2), ("fwd", False, 1, 1), None],
    "skill_e": [("fwd", False, 0, 0), ("back", False, 0, 0), ("hang", True, 0, 0), None],
    "skill2": [("back", True, 0, 0), ("fwd", True, 1, 0), ("hang", True, 0, 0), None],
    "ult": [("hang", True, 0, 0), ("back", True, 0, 3), ("back", True, 0, 7), ("back", True, 0, 9), ("back", True, 0, 9),
            ("fwd", False, 1, 5), ("hang", False, 0, 2), None],
    "hit": [("hang", True, -2, 0), ("hang", True, -1, 0)],
}
DEAD = [(0, -1, True), (8, -1, True), (20, -1, False), (40, 0, False), (65, 0, False), (90, 0, False), (90, 0, False),
        (90, 0, False)]                  # (degrees counter-clockwise, dx, blades still in the hand)


def lp(p):
    return K.lp(p)


def design():
    a = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))
    a = (a if a.shape[0] == 128 else a[Z // 2::Z, Z // 2::Z]).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    return a


class Parts:
    def __init__(self):
        d = design()
        self.design = d
        op = d[..., 3] > 0
        R, C = np.mgrid[0:128, 0:128]
        arm = op & (R >= 80) & (R <= 95) & (C >= 74) & (C <= 84) & ~((R >= 89) & (C <= 77)) & \
            ~((R >= 83) & (R <= 88) & (C <= 75))
        self.blades_m = arm & (R >= 89) & (C >= 78)
        self.arm_m = arm
        self.body = d.copy()
        self.body[arm] = 0
        self.arm = K.Part.from_canvas(d, arm, SHOULDER)
        bare = d.copy()
        bare[~(arm & ~self.blades_m)] = 0
        self.arm_bare = K.Part.from_canvas(bare, arm & ~self.blades_m, SHOULDER)
        self.blades = K.Part.from_canvas(d, self.blades_m, (79.0, 89.0))
        self.no_blades = d.copy()
        self.no_blades[self.blades_m] = 0


def arm_unit(P, how, blades):
    u = P.arm if blades else P.arm_bare
    return {"hang": u, "fwd": K.rot90(u, 3), "up": K.rot90(u, 2), "back": K.rot90(u, 1)}[how]


def standing(P, pose):
    if pose is None:
        return P.design.copy()
    how, blades, dx, lift = pose
    c = np.zeros((128, 128, 4), np.uint8)
    unit = arm_unit(P, how, blades)
    if how == "back":
        K.place(c, unit, SHOULDER)                   # behind the body
        K.put(c, P.body, 0, 0)
    else:
        K.put(c, P.body, 0, 0)
        K.place(c, unit, SHOULDER)
    if dx or lift:
        c = K.shifted(c, dx, -lift)
    return c


def dead(P, k):
    deg, dx, blades = DEAD[k]
    src = P.design if blades else P.no_blades
    ys, xs = np.nonzero(src[..., 3] > 0)
    fig = K.Part.from_canvas(src, src[..., 3] > 0, (64.0, 100.0))
    t = K.turn(fig, deg) if deg else fig
    c = np.zeros((128, 128, 4), np.uint8)
    K.place(c, t, (64.0 + dx, 100.0))
    low = int(np.nonzero(c[..., 3].any(1))[0].max())
    if low != SOLES:
        c = K.shifted(c, 0, SOLES - low)
    if not blades:                                   # the dropped blades lie flat on the ground in front of her
        lying = K.rot90(P.blades, 3).s
        right = int(np.nonzero(c[SOLES - 3:SOLES + 1, :, 3].any(0))[0].max())
        K.put(c, lying, min(right + 1, 127 - lying.shape[1]), SOLES + 1 - lying.shape[0], under=True)
    return c


def codex_run():
    """Codex's run frames (64x64 cells, 3x2; the soles on row 47, the feet's middle on column 32) on the design canvas."""
    a = np.asarray(Image.open(lp(os.path.join(SRC, "xayah_run.png"))).convert("RGBA"))
    a = a[Z // 2::Z, Z // 2::Z]
    out = []
    for i in range(6):
        f = a[(i // 3) * 64:(i // 3 + 1) * 64, (i % 3) * 64:(i % 3 + 1) * 64]
        c = np.zeros((128, 128, 4), np.uint8)
        K.put(c, f, 64 - 32, SOLES - 47)
        out.append(c)
    return out


def finish(a, pinholes=3):
    return K.finish(a, OUT, SOLES, pinholes=pinholes)


def frames(P, tag):
    if tag == "idle":
        return [P.design.copy() for _ in MS[tag]]
    if tag == "run":
        return [finish(f) for f in codex_run()]
    if tag == "dead":
        return [finish(dead(P, k)) for k in range(len(MS[tag]))]
    # pinholes 6: the hip's gap the arm leaves when it swings out (4 squares between the tabard and the leg) is filled
    return [finish(standing(P, p), 6) if p is not None else P.design.copy() for p in POSES[tag]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", help="write a review sheet and GIF into this folder")
    a = ap.parse_args()
    P = Parts()
    built = {tag: frames(P, tag) for tag in TAGS}
    for tag in TAGS:
        rows = K.audit(built[tag], P.design, OUT, SOLES)
        print(f"{tag:8s}", " ".join(f"{r['pieces']}p{r['holes']}h{r['orphans']}o{r['area']}" for r in rows))
    bad = K.write_strips("xayah", built, MS, NATIVE, CELL, CELL_PIVOT, PIVOT, check=a.check)
    if a.check:
        print("differs:", bad or "nothing")
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        K.review_sheet([(t, built[t]) for t in TAGS], os.path.join(a.review, "xayah_strips_review.png"), z=3,
                       soles=SOLES)
        K.review_gif([(t, built[t]) for t in TAGS], MS, os.path.join(a.review, "xayah_strips_review.gif"), z=3)
    sys.exit(1 if a.check and bad else 0)


if __name__ == "__main__":
    main()
