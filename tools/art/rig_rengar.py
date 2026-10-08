#!/usr/bin/env python3
"""Rengar's action strips posed from the approved design's own parts (2026-10-09): the casting body = the idle's.

    python tools/art/rig_rengar.py [--check] [--review DIR] [--parts PNG]

Codex's step-2 delivery (assets/source/rengar/codex_strips/) pasted the design's head on bodies it drew anew: the run
45-47 rows tall (the design 40) and 50-55 wide, the legs not the design's, the three claw blades, the serrated blade, the
pauldron and the chest strap simplified, old outlines round the pasted heads, loose specks; its own HANDOFF marked every
action "needs visual revision before import". The user: 「有问题的地方你帮忙修复」. So, as for Vladimir (rig_vladimir.py),
every frame is the design with only what the action moves moved, nothing resampled (no-deformation rule: translation,
quarter turns, mirrors, whole-row shifts, layering):
- the parts are cut square for square with the outline squares that ring them alone: the head piece (the mane, the horns,
  the face, the beard: work/rg/head_rg.py's ranges), the BLADE arm (image right: the fur arm, the bracer, the fist and
  the serrated blade with its blood edge), the CLAW arm (image left: the fur arm under the pauldron, the bracer and the
  three claw blades), the tail (from the hip to the white tuft) and the two lower legs (the laced shin wraps and the
  clawed feet); the pauldron, the chest strap, the belt, the kilt and the knees stay the torso's;
- arm poses are rigid units turned about the shoulder: HANG (as drawn), OUT (a quarter turn: the blade / the claws
  pointing to the right, or the claw arm back to the left), UP (mirrored about the shoulder: raised over the head), IN
  (pulled to the chest), FWD (the claw arm brought across the body, its claws pointing right);
- whole-figure moves: a lunge / recoil (columns), a hop (rows: the leap and Q leave the ground), a crouch (everything
  above the feet sunk over them, layering), the lower legs swung back or tucked (rigkit.swing_leg: whole rows);
- the death: struck back, then the figure turned exactly a quarter counter-clockwise about the feet (on his back, the
  head to the left), the blade cut off and lying on the ground by his hand;
- the run: the design's own lower legs swung about the knees (whole rows), the arms swinging a column, the tail
  swaying, the body dropping a row at each contact.
Writes assets/source/native/rengar_<tag>.png (8x, 112x96 cells, soles on cell row 81) and rengar_cells.json; then
tools/art/import_native.py. --check compares instead of writing; --review writes a review sheet and GIF.
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
DESIGN = os.path.join(NATIVE, "rengar_native.png")
Z = 8
PIVOT = (64, 88)                 # the design's standing point (the soles on row 99, the feet's middle on column 64)
SOLES = 99
OUT = K.rgb("#0E0206")
CELL = (112, 96)
CELL_PIVOT = (56, 70)            # the soles on cell row 81 (the references' feet line)
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
N8 = tuple((a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if a or b)

# the head piece: per row (first, last) column on the design canvas (= work/rg/head_rg.py)
HEAD = {**{y: (53, 77) for y in range(60, 69)}, 69: (58, 71), 70: (59, 71), 71: (59, 71), 72: (59, 71), 73: (60, 71),
        **{y: (60, 73) for y in range(74, 82)}, 82: (61, 71), 83: (67, 69)}
BLADE_SHOULDER = (75.0, 80.0)    # (x, y): the top of the blade arm, under the shoulder plates
CLAW_SHOULDER = (50.0, 77.0)     # the top of the claw arm, under the pauldron
TAIL_ROOT = (54.5, 87.0)         # where the tail leaves the hip
KNEE_ROW, ANKLE_ROW = 92, 96     # the lower legs: the laced shin wraps (92-95) and the clawed feet (96-98)


def design():
    a = np.asarray(Image.open(K.lp(DESIGN)).convert("RGBA"))
    a = (a if a.shape[0] == 128 else a[Z // 2::Z, Z // 2::Z]).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    return a


def region(rows_cols):
    m = np.zeros((128, 128), bool)
    for y, (c0, c1) in rows_cols.items():
        m[y, c0:c1 + 1] = True
    return m


class Parts:
    def __init__(self):
        d = design()
        self.design = d
        op = d[..., 3] > 0
        ink = op & (d[..., :3] == np.array(OUT, np.uint8)).all(-1)
        colour = op & ~ink
        R, C = np.mgrid[0:128, 0:128]
        blade_c = colour & (R >= 80) & (R <= 97) & (C >= 73)
        claw_c = colour & (((R >= 76) & (R <= 78) & (C <= 51)) | ((R >= 79) & (R <= 91) & (C <= 52)))
        tail_c = colour & (((R >= 87) & (R <= 91) & (C == 54)) | ((R == 92) & (C == 53)) |
                           ((R >= 92) & (R <= 95) & (C >= 46) & (C <= 53)))
        lleg_c = colour & (R >= KNEE_ROW) & (C >= 54) & (C <= 60) & ~tail_c
        rleg_c = colour & (R >= KNEE_ROW) & (C >= 61) & (C <= 72)
        head_c = colour & region(HEAD)
        self.colour = colour
        parts_c = {"blade": blade_c, "claw": claw_c, "tail": tail_c, "lleg": lleg_c, "rleg": rleg_c, "head": head_c}
        taken = np.zeros((128, 128), bool)
        for k, m in parts_c.items():
            assert not (m & taken).any(), k
            taken |= m
        body_c = colour & ~taken

        def ring(c, others):
            """The outline squares round c that no square of `others` touches (4-neighbours)."""
            m = np.zeros_like(c)
            for y, x in zip(*np.nonzero(ink)):
                if any(c[y + a, x + b] for a, b in N8) and not any(others[y + a, x + b] for a, b in N4):
                    m[y, x] = True
            return m

        self.masks = {}
        for k, c in parts_c.items():
            others = body_c | (taken & ~c)
            self.masks[k] = c | ring(c, others)
        self.body = d.copy()
        for k in ("blade", "claw", "tail", "lleg", "rleg"):
            self.body[self.masks[k]] = 0
        self.blade = K.Part.from_canvas(d, self.masks["blade"], BLADE_SHOULDER)
        self.claw = K.Part.from_canvas(d, self.masks["claw"], CLAW_SHOULDER)
        self.tail = K.Part.from_canvas(d, self.masks["tail"], TAIL_ROOT)

    def overlay(self, path, z=12):
        """The design with every part tinted (blade red, claw green, tail yellow, legs cyan / magenta, head blue)."""
        d = self.design.astype(float)
        tint = {"blade": (255, 0, 0), "claw": (0, 200, 0), "tail": (255, 220, 0), "lleg": (0, 220, 255),
                "rleg": (255, 0, 255), "head": (60, 90, 255)}
        out = d.copy()
        for k, col in tint.items():
            m = self.masks[k]
            out[m, :3] = d[m, :3] * 0.45 + np.array(col) * 0.55
        sub = out[58:101, 38:83].astype(np.uint8)
        Image.fromarray(sub).resize((sub.shape[1] * z, sub.shape[0] * z), Image.NEAREST).save(path)


def finish_near(a, ref, pinholes=4):
    """rigkit.finish, but every square more than 2 from a square that differs from `ref` keeps ref's (the design's own
    gaps stay open, the untouched body stays the design's square for square)."""
    changed = (a != ref).any(-1)
    near = changed.copy()
    for _ in range(2):
        g = near.copy()
        for dy, dx in N8:
            g |= np.roll(np.roll(near, dy, 0), dx, 1)
        near = g
    out = K.finish(a, OUT, SOLES, keep=~near, pinholes=pinholes)
    out[~near] = a[~near]
    return out


FEET_ROW = 96                    # the toes' rows (96-98) stay on the ground when the body crouches


def arm_unit(P, which, how):
    """(Part, joint offset from the shoulder, drawn behind the body?) for an arm pose."""
    u = P.blade if which == "blade" else P.claw
    if how in (None, "hang"):
        return u, (0, 0), False
    if how == "out":             # the blade pointing right / the claw arm back to the left, at the shoulder's height
        return (K.rot90(u, 3) if which == "blade" else K.rot90(u, 1)), (0, 1), False
    if how == "up":              # raised over the shoulder: the blade beside the head (in front), the claws behind
        return (u.flip_v(), (3, 0), False) if which == "blade" else (u.flip_v(), (0, 0), True)
    if how == "in":              # pulled up toward the chest
        return u, ((-2, -3) if which == "blade" else (3, -3)), which == "claw"
    if how == "fwd":             # the claw arm brought across the body in front of the belt, the claws pointing right
        return K.rot90(u, 3), (12, 5), False
    if how == "low":             # the blade driven down in front: the arm turned out, held lower
        return K.rot90(u, 3), (0, 3), False
    raise ValueError(how)


def build(P, f):
    """One frame from a pose dict: blade / claw (arm poses), bdy / cdy (arm rows), legs ((dx, lift) left, right),
    tail (the tuft's columns), sink (rows, the feet stay), dx / dy (the whole figure)."""
    c = P.body.copy()
    legs_spec = f.get("legs", ((0, 0), (0, 0)))
    (lx, ll), (rx, rl) = legs_spec
    for m, dx, lift in ((P.masks["lleg"], lx, ll), (P.masks["rleg"], rx, rl)):
        K.put(c, K.swing_leg(P.design, m, KNEE_ROW - 1, FEET_ROW, dx, lift), 0, 0, under=True)
    K.put(c, K.swing_leg(P.design, P.masks["tail"], int(TAIL_ROOT[1]), 99, f.get("tail", 0)), 0, 0, under=True)
    behind, front = [], []
    for which, sh in (("claw", CLAW_SHOULDER), ("blade", BLADE_SHOULDER)):
        u, (ox, oy), back = arm_unit(P, which, f.get(which))
        at = (sh[0] + ox, sh[1] + oy + f.get("bdy" if which == "blade" else "cdy", 0))
        (behind if back else front).append((u, at))
    for u, at in behind:
        K.place(c, u, at, under=True)
    for u, at in front:
        K.place(c, u, at)
    if f.get("sink"):
        n = f["sink"]
        R = np.arange(128)[:, None]
        feet_m = (P.masks["lleg"] | P.masks["rleg"]) & (R >= FEET_ROW)
        moved_legs = any(v for pair in legs_spec for v in pair)
        feet = np.zeros_like(c)
        top = c.copy()
        if not moved_legs:
            feet[feet_m] = P.design[feet_m]
            top[feet_m] = 0
        c = K.put(K.shifted(top, 0, n), feet, 0, 0)     # the feet in front of the sunk shins: the toes stay
        c[SOLES + 1:] = 0
    if f.get("dx") or f.get("dy"):
        c = K.shifted(c, f.get("dx", 0), f.get("dy", 0))
    return c


def frame(P, f):
    if f is None:
        return P.design.copy()
    c = build(P, f)
    return finish_near(c, K.shifted(P.design, f.get("dx", 0), f.get("dy", 0)))


# ------------------------------------------------------------------------------------------------ the actions
TAGS = ["idle", "run", "attack", "leap", "skill", "skill2", "skill_w", "ult", "hit", "dead"]
MS = {"idle": [140] * 8, "run": [120] * 8, "attack": [60, 60, 60, 70, 80, 90], "leap": [50, 50, 60, 60, 60, 70, 80, 80],
      "skill": [50, 50, 60, 50, 50, 70, 70, 80], "skill2": [70, 70, 80, 70, 80, 90],
      "skill_w": [60, 70, 80, 120, 120, 90, 80], "ult": [70, 90, 150, 100], "hit": [120, 120],
      "dead": [100, 100, 100, 120, 120, 150, 200, 500]}
TUCK = ((-3, 2), (-2, 2))        # the lower legs tucked back in the air
POSES = {
    # League's attack1: the blade held low in front, the claws up; a spring; the slash to the right; the follow-through
    "attack": [dict(claw="up", sink=1), dict(claw="up", blade="in", sink=1),
               dict(claw="out", blade="up", dx=1), dict(claw="out", blade="out", dx=2),
               dict(blade="low", dx=1, sink=1), None],
    # the pounce (passive + R): crouch, launch, three frames in the air (legs tucked, blade and claws reaching right),
    # the landing rake, rising
    "leap": [dict(sink=2), dict(blade="out", claw="out", dy=-2, legs=((-2, 1), (-1, 1)), tail=-1),
             dict(blade="out", claw="out", dy=-5, dx=1, legs=TUCK, tail=-2),
             dict(blade="out", claw="out", dy=-7, dx=1, legs=TUCK, tail=-2),
             dict(blade="out", claw="out", dy=-4, dx=2, legs=((-1, 1), (0, 1)), tail=-1),
             dict(blade="low", claw="out", sink=2, dx=2), dict(sink=1, dx=1), None],
    # Q: a jump with the blade raised, the slam, the rising rip
    "skill": [dict(sink=1), dict(blade="up", claw="up", dy=-3, legs=((-1, 1), (-1, 1))),
              dict(blade="up", claw="up", dy=-5, legs=TUCK), dict(blade="up", claw="out", dy=-2),
              dict(blade="low", claw="out", sink=2, dx=1), dict(blade="up", sink=1, dx=2),
              dict(blade="up", dx=1), None],
    # E: the claw arm swung up behind the head, whirled, thrown forward across the body
    "skill2": [dict(claw="in", sink=1), dict(claw="up"), dict(claw="up", cdy=-1),
               dict(claw="fwd", dx=1), dict(dx=1), None],
    # W: gathering, then both arms flung out, roaring
    "skill_w": [dict(blade="in", claw="in", sink=1), dict(sink=0), dict(blade="out", claw="out"),
                dict(blade="out", claw="out", bdy=-1, tail=1), dict(blade="out", claw="out", cdy=-1, tail=-1),
                dict(blade="in", claw="in"), None],
    # R: the stalking crouch
    "ult": [dict(sink=1), dict(sink=2, tail=-1), dict(sink=2, tail=-1), dict(sink=1)],
    "hit": [dict(claw="out", dx=-2), dict(dx=-1)],
}


def dead(P, k):
    """Struck back, knocked up, then on his back: the body without the arms turned exactly a quarter counter-clockwise
    about the feet (the head to the left), the claw arm laid along the body, the blade arm dropped on the ground in
    front of him (Rengar's arms spread as wide as he is tall: turned with them he would stand 41 rows high)."""
    steps = [dict(dx=-1), dict(claw="out", dx=-2, dy=-2), dict(claw="out", dx=-3, dy=-1)]
    if k < 3:
        return frame(P, steps[k])
    above = [4, 1, 0, 0, 0][k - 3]
    body = P.body.copy()
    for m in ("lleg", "rleg", "tail"):
        body[P.masks[m]] = P.design[P.masks[m]]
    fig = K.Part.from_canvas(body, body[..., 3] > 0, (64.0, 100.0))
    t = K.turn(fig, 90)
    c = np.zeros_like(P.design)
    K.place(c, t, (64.0 + 4, 100.0))
    low = int(np.nonzero(c[..., 3].any(1))[0].max())
    c = K.shifted(c, 0, SOLES - above - low)
    ys, xs = np.nonzero(c[..., 3] > 0)
    top, left, right = ys.min(), xs.min(), xs.max()
    # the claw arm along his chest (turned: the claws toward his feet), the blade arm on the ground past his side
    K.place(c, K.rot90(P.claw, 3), (left + 14.0, top + 3.0))
    blade = K.rot90(P.blade, 3)
    K.place(c, blade, (right - 4.0, SOLES - above - blade.s.shape[0] + 1 + blade.j[1]), under=True)
    c[SOLES + 1:] = 0
    return K.finish(c, OUT, SOLES, keep=None, pinholes=4)


# the run (League's pace: Rengar_run1 cycles in 0.968 s -> 8 x 120 ms). The design's feet stand 12-15 columns apart (a wide
# beast's stance): swinging only the lower legs the near foot never passes the far one (run-crossing-root-causes), so two
# variants for the user: TROT - the lower legs alternate forward and back in place (no crossing); CROSS - the whole legs
# (thigh, knee pad, shin, foot) brought in under the body and swung about the hip (whole-row shifts), the feet changing
# places twice a cycle at most 12 apart.
STRIDE = [4, 3, 0, -3, -4, -3, 0, 3]
R_LIFT = [0, 0, 0, 0, 0, 2, 3, 2]
L_LIFT = [0, 2, 3, 2, 0, 0, 0, 0]
DROP = [1, 0, 0, 0, 1, 0, 0, 0]
ARM = [-2, -1, 0, 1, 2, 1, 0, -1]
TAIL = [-1, 0, 1, 0, -1, 0, 1, 0]
RUN = {"trot": dict(hip=KNEE_ROW - 1, l_in=0, r_in=0, stride=0.75, full=False),
       "cross": dict(hip=87, l_in=4, r_in=-5, stride=1.0, full=True)}
RUN_VARIANT = "trot"          # the user (2026-10-09): 「不对选A 不用交叉步」


def leg_masks(P, full):
    if not full:
        return P.masks["lleg"], P.masks["rleg"]
    R, C = np.mgrid[0:128, 0:128]
    op = P.design[..., 3] > 0
    tail = P.masks["tail"]
    lm = op & (R >= 88) & (C >= 55) & (C <= 60) & ~tail
    rm = op & (R >= 88) & (C >= 64) & (C <= 72) & ~P.masks["blade"]
    return lm, rm


def run_frames(P, variant=None):
    v = RUN[variant or RUN_VARIANT]
    lm, rm = leg_masks(P, v["full"])
    out = []
    for k in range(8):
        st = int(round(STRIDE[k] * v["stride"]))
        legs = np.zeros_like(P.design)
        # the far (image-left) leg drawn first, the near one over it
        K.put(legs, K.swing_leg(P.design, lm, v["hip"], FEET_ROW, v["l_in"] - st, L_LIFT[k]), 0, 0)
        K.put(legs, K.swing_leg(P.design, rm, v["hip"], FEET_ROW, v["r_in"] + st, R_LIFT[k]), 0, 0)
        top = P.body.copy()
        top[lm | rm] = 0
        K.put(top, K.swing_leg(P.design, P.masks["tail"], int(TAIL_ROOT[1]), 99, TAIL[k]), 0, 0, under=True)
        K.put(top, K.swing_leg(P.design, P.masks["claw"], 77, 91, -ARM[k]), 0, 0, under=True)
        K.put(top, K.swing_leg(P.design, P.masks["blade"], 80, 97, ARM[k]), 0, 0)
        c = K.put(K.shifted(top, 0, DROP[k]), legs, 0, 0, under=True)
        c[SOLES + 1:] = 0
        keep = np.zeros((128, 128), bool)
        keep[:79 + DROP[k]] = True
        out.append(K.finish(c, OUT, SOLES, keep=keep, pinholes=4))
    return out


# the idle breathes here (as league_xayah's): the shared idle_breathe cuts a row in the shins and leans the body a column
# on the lowest shin row - on Rengar's short legs the lean smeared the toes into bars and the carried blade, hanging to
# two rows over the soles, went under them. So the whole figure but the feet sinks 0 0 1 2 2 2 1 0 rows over the feet
# (layering, like the crouch), the arms and their weapons with it; the base game's pace (8 x 140 ms); import_native
# skips him (BREATHE_SKIP).
BREATH = [0, 0, 1, 2, 2, 2, 1, 0]


def frames(P, tag):
    if tag == "idle":
        return [P.design.copy() if n == 0 else frame(P, dict(sink=n)) for n in BREATH]
    if tag == "run":
        return run_frames(P)
    if tag == "dead":
        return [dead(P, k) for k in range(len(MS["dead"]))]
    return [frame(P, f) for f in POSES[tag]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts", help="write the part overlay PNG and stop")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", help="write a review sheet and GIF into this folder")
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args()
    P = Parts()
    if a.parts:
        P.overlay(a.parts)
        print({k: int(m.sum()) for k, m in P.masks.items()})
        return
    built = {tag: frames(P, tag) for tag in TAGS}
    for tag in TAGS:
        rows = K.audit(built[tag], P.design, OUT, SOLES)
        print(f"{tag:8s}", " ".join(f"{r['pieces']}p{r['holes']}h{r['orphans']}o{r['below']}b{r['area']}" for r in rows))
    if not a.no_write:
        bad = K.write_strips("rengar", built, MS, NATIVE, CELL, CELL_PIVOT, PIVOT, check=a.check)
        if a.check:
            print("differs:", bad or "nothing")
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        K.review_sheet([(t, built[t]) for t in TAGS], os.path.join(a.review, "rengar_strips_review.png"), z=4,
                       soles=SOLES)
        K.review_gif([(t, built[t]) for t in TAGS], MS, os.path.join(a.review, "rengar_strips_review.gif"), z=4)


if __name__ == "__main__":
    main()
