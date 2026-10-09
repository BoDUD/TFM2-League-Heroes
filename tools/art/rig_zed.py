#!/usr/bin/env python3
"""Zed's action strips posed from the approved design's own parts (2026-10-09): the casting body = the idle's.

    python tools/art/rig_zed.py [--check] [--review DIR] [--parts PNG] [--run trot|cross]

Codex's step-2 delivery (assets/source/zed/codex_strips/) pasted the design's head on bodies it drew anew: bigger than
the idle in W, Q and E, the legs not the design's (its own HANDOFF: design_legs_square_for_square false), the wrist
blades unclear, old outlines possible round the pasted heads. The user: 「有问题的地方帮我修复」. So, as for Rengar
(rig_rengar.py), every frame is the design with only what the action moves moved, nothing resampled (no-deformation
rule: translation, quarter turns, mirrors, whole-row shifts, layering):
- the parts are cut square for square with the outline squares that ring them alone: the two FOREARMS (the gold bracer
  with its silver spurs and the two wrist blades; the red sleeve and the pauldron above stay the torso's), the two
  LOWER LEGS (the greaves and the pointed boots) and the head (work/zd/head_zd.py's ranges: the hood and the helmet);
- forearm poses are rigid units turned about the elbow (the bracer's top): HANG (as drawn), OUT (a quarter turn: the
  blades pointing right - or, for the image-left arm, left), UP (mirrored about the elbow: raised, the blades up),
  IN (pulled to the chest), FWD (the image-left forearm brought across the body, its blades pointing right), BACK (the
  image-right forearm turned to point left behind the body), LOW (OUT held lower);
- whole-figure moves: a lunge / recoil (columns), a hop (rows), a crouch (everything above the boots sunk over them,
  layering), the lower legs swung back or tucked (rigkit.swing_leg: whole rows);
- the death: struck back, sunk to his knees, then the figure turned exactly a quarter clockwise about the feet (face
  down, the head to the right, League's fall forward);
- the run: two variants for the user (run-crossing-root-causes: his boots stand 11-12 columns apart) - TROT, the
  design's own lower legs swung about the knees in place, and CROSS, the whole legs from the hips brought in and swung
  so the boots pass each other; the forearms swing opposite the legs, the body drops a row at each contact.
Writes assets/source/native/zed_<tag>.png (8x, 112x96 cells, soles on cell row 81) and zed_cells.json; then
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
DESIGN = os.path.join(NATIVE, "zed_native.png")
Z = 8
PIVOT = (64, 88)                 # the design's standing point (the soles on row 99, the feet's middle on column 64)
SOLES = 99
OUT = K.rgb("#100F19")               # the grid design's outline
CELL = (112, 96)
CELL_PIVOT = (56, 70)            # the soles on cell row 81 (the references' feet line)
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
N8 = tuple((a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if a or b)

# the head piece: per row (first, last) column on the design canvas (= work/zd/head_zd.py)
# 2026-10-09 design B (Codex's grid redraw after picture A, assets/source/zed/codex_grid/zed-grid-B_1x.png, de-speckled by
# work/zd4/polish_b_zd.py): the hood's point row 54, the mask rows 62-66 with the eyes at (66,64) (68,64), the scarf
# rows 65-70, the back blades rows 56-66 (part of the body), bracers rows 73-80, claws down to row 92, legs from
# row 81, boots rows 95-99
HEAD = {54: (62, 64), 55: (61, 65), 56: (61, 65), 57: (60, 66), 58: (60, 66), **{y: (59, 70) for y in range(59, 70)},
        70: (60, 69)}
L_ELBOW = (53.5, 76.0)           # (x, y): the top of the image-left bracer
R_ELBOW = (74.5, 78.0)           # the top of the image-right bracer
KNEE_ROW, FEET_ROW = 90, 95      # the lower legs: the greaves (93-95) and the boots (96-98)
TABARD = set()   # the tabard's hem squares among the near leg's rows


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
        lfore_c = colour & (R >= 76) & (R <= 94) & (C <= 57)
        # the tabard hem reaches column 71 from row 89 down: the forearm keeps to 72+ there
        rfore_c = colour & (R >= 78) & (R <= 97) & (C >= 72)
        tab = np.zeros((128, 128), bool)
        for y, x in TABARD:
            tab[y, x] = True
        lleg_c = colour & (R >= KNEE_ROW) & (C >= 57) & (C <= 64) & ~lfore_c
        rleg_c = colour & (R >= KNEE_ROW) & (C >= 65) & (C <= 74) & ~tab & ~rfore_c
        head_c = colour & region(HEAD)
        silver = np.zeros((128, 128), bool)        # the back ornament's prongs above the brows ride on the body
        for y, x in zip(*np.nonzero(head_c)):
            if False:
                silver[y, x] = True
        head_c &= ~silver
        self.colour = colour
        parts_c = {"lfore": lfore_c, "rfore": rfore_c, "lleg": lleg_c, "rleg": rleg_c, "head": head_c}
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
        for k in ("lfore", "rfore", "lleg", "rleg"):
            self.body[self.masks[k]] = 0
        self.lfore = K.Part.from_canvas(d, self.masks["lfore"], L_ELBOW)
        self.rfore = K.Part.from_canvas(d, self.masks["rfore"], R_ELBOW)

    def overlay(self, path, z=12):
        """The design with every part tinted (forearms red / green, legs cyan / magenta, head blue)."""
        d = self.design.astype(float)
        tint = {"rfore": (255, 0, 0), "lfore": (0, 200, 0), "lleg": (0, 220, 255), "rleg": (255, 0, 255),
                "head": (60, 90, 255)}
        out = d.copy()
        for k, col in tint.items():
            m = self.masks[k]
            out[m, :3] = d[m, :3] * 0.45 + np.array(col) * 0.55
        sub = out[58:101, 44:82].astype(np.uint8)
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


def arm_unit(P, which, how):
    """(Part, joint offset from the elbow, drawn behind the body?) for a forearm pose."""
    u = P.rfore if which == "r" else P.lfore
    if how in (None, "hang"):
        return u, (0, 0), False
    if how == "out":             # the image-right blades pointing right / the image-left ones pointing left
        return (K.rot90(u, 3) if which == "r" else K.rot90(u, 1)), (0, 1), which == "l"
    if how == "low":             # pointing right, held lower (a low throw, a follow-through)
        return K.rot90(u, 3), (0, 4), False
    if how == "up":              # raised beside the helmet: the forearm mirrored about the elbow, the blades up
        return u.flip_v(), ((1, -5) if which == "r" else (-1, -4)), which == "l"
    if how == "in":              # pulled up toward the chest
        return u, ((-3, -2) if which == "r" else (3, -2)), which == "l"
    if how == "fwd":             # the image-left forearm brought across in front, its blades pointing right
        return K.rot90(u, 3), (9, 3), False
    if how == "back":            # the image-right forearm turned to point left, behind the body
        return K.rot90(u, 1), (-2, 1), True
    raise ValueError(how)


def build(P, f):
    """One frame from a pose dict: r / l (forearm poses), rdy / ldy (forearm rows), legs ((dx, lift) left, right),
    sink (rows, the boots stay), dx / dy (the whole figure)."""
    c = P.body.copy()
    legs_spec = f.get("legs", ((0, 0), (0, 0)))
    (lx, ll), (rx, rl) = legs_spec
    for m, dx, lift in ((P.masks["lleg"], lx, ll), (P.masks["rleg"], rx, rl)):
        K.put(c, K.swing_leg(P.design, m, KNEE_ROW - 1, FEET_ROW, dx, lift), 0, 0, under=True)
    behind, front = [], []
    for which, el in (("l", L_ELBOW), ("r", R_ELBOW)):
        u, (ox, oy), back = arm_unit(P, which, f.get(which))
        at = (el[0] + ox, el[1] + oy + f.get(which + "dy", 0))
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
        c = K.put(K.shifted(top, 0, n), feet, 0, 0)     # the boots in front of the sunk greaves: the toes stay
        c[SOLES + 1:] = 0
    if f.get("mirror"):                     # the whole figure turned to face left (League's Q wind-up turns his
        c = mirrored(c)                      # back, E spins): a lossless flip about the standing column
    if f.get("dx") or f.get("dy"):
        c = K.shifted(c, f.get("dx", 0), f.get("dy", 0))
    return c


def mirrored(c):
    m = c[:, ::-1].copy()                    # x -> 127 - x: the standing column 64 lands on 63
    return K.shifted(m, 1, 0)


def frame(P, f):
    if f is None:
        return P.design.copy()
    c = build(P, f)
    ref = mirrored(P.design) if f.get("mirror") else P.design
    return finish_near(c, K.shifted(ref, f.get("dx", 0), f.get("dy", 0)))


# ------------------------------------------------------------------------------------------------ the actions
TAGS = ["idle", "run", "attack", "skill", "skill2", "skill_e", "ult", "hit", "dead"]
# frame lengths = assets/source/zed/poses.json (the release frames land on the kit's ticks: attack 9, W 3, Q 10, E 8,
# R 6)
MS = {"idle": [140] * 8, "run": [120] * 8, "attack": [60, 50, 40, 80, 100, 110], "skill": [50, 60, 80, 90],
      "skill2": [60, 50, 60, 80, 100, 120], "skill_e": [50, 40, 43, 70, 70, 100],
      "ult": [50, 50, 80, 80, 80, 90, 110], "hit": [120, 120], "dead": [100, 100, 120, 150, 200, 150, 150, 500]}
TUCK = ((-2, 1), (-1, 1))        # the lower legs trailing back in the dash (design B: a boot swung 3 came off the shin)
LUNGE = ((-3, 0), (1, 0))        # the back leg swung back, the front one a column forward
POSES = {
    # League's attack1 (head +9 rows at the stab): coiled low, the stab a low lunge forward, rising back
    "attack": [dict(r="in", sink=1), dict(r="in", dx=-1, sink=2), dict(r="out", dx=1, sink=1),
               dict(r="out", dx=3, sink=4, legs=LUNGE), dict(r="out", dx=2, sink=3, legs=LUNGE), dict(sink=1)],
    # W: the near arm raised by the head with a small rise, flung forward, the follow-through low
    "skill": [dict(r="up"), dict(r="out", dx=1, dy=-1), dict(r="low", dx=1, sink=1), None],
    # Q (League turns his back winding up, then throws from a deep crouch, head +23): the hand to the ornament, the
    # wind-up turned away (mirrored), the throw crouched low and lunging, rising
    "skill2": [dict(r="up", sink=1), dict(r="up", mirror=True, sink=1), dict(r="in", mirror=True, sink=2, dx=1),
               dict(r="low", l="out", sink=5, dx=3, legs=LUNGE), dict(r="low", sink=3, dx=2, legs=LUNGE), dict(sink=1)],
    # E (a leaping spin, both blades out): pulled in, the crouch, the leap forward with the blades out, mid-spin
    # turned away in the air, facing again, the landing crouch
    "skill_e": [dict(r="in", l="in"), dict(r="in", l="in", sink=2), dict(r="out", l="out", dx=2, dy=-2, legs=TUCK),
                dict(r="out", l="out", mirror=True, dy=-3, legs=TUCK), dict(r="out", l="out", dx=-1, dy=-1, legs=TUCK),
                dict(r="out", l="hang", sink=2)],
    # R (the lead-in coils back, the dash, the strike a deep lunging crouch, head +12): the crouch, the coil back,
    # the dash with both blades forward, still dashing, the low strike, the landing crouch, rising
    "ult": [dict(r="in", l="in", sink=1), dict(r="in", l="in", dx=-2, sink=2),
            dict(r="out", l="fwd", dx=3, dy=-2, legs=TUCK), dict(r="out", l="fwd", dx=5, dy=-1, legs=TUCK),
            dict(r="out", l="fwd", dx=4, sink=4, legs=LUNGE), dict(r="low", l="out", dx=3, sink=3, legs=LUNGE),
            dict(r="out", l="out", dx=1, sink=1)],
    "hit": [dict(l="out", r="back", dx=-2), dict(dx=-1)],
}


def lying(P, above):
    """The whole figure (arms hanging) turned exactly a quarter clockwise about the feet: face down, the head to the
    right (League's fall forward), `above` rows over the ground."""
    fig = K.Part.from_canvas(P.design, P.design[..., 3] > 0, (64.0, 100.0))
    t = K.turn(fig, -90)
    c = np.zeros_like(P.design)
    K.place(c, t, (60.0, 100.0))
    low = int(np.nonzero(c[..., 3].any(1))[0].max())
    c = K.shifted(c, 0, SOLES - above - low)
    c[SOLES + 1:] = 0
    return K.finish(c, OUT, SOLES, keep=None, pinholes=4)


def dead(P, k):
    """Struck back, sinking to his knees, kneeling slumped, then falling forward face down."""
    steps = [dict(dx=-1, l="out"), dict(dx=-1, sink=2), dict(sink=4, legs=((-3, 0), (0, 0))),
             dict(sink=5, legs=((-3, 0), (0, 0)), r="low"), dict(sink=5, legs=((-3, 0), (0, 0)), r="low")]
    if k < len(steps):
        return frame(P, steps[k])
    return lying(P, [3, 0, 0][k - len(steps)])


# the run (League's pace: Zed_run cycles in 0.968 s -> 8 x 120 ms). The design's boots stand 11-12 columns apart:
# swinging only the lower legs the near boot never passes the far one (run-crossing-root-causes), so two variants for
# the user: TROT - the lower legs alternate forward and back in place (no crossing); CROSS - the whole legs (thigh,
# greave, boot) brought in under the body and swung about the hip (whole-row shifts), the boots changing places twice a
# cycle at most 12 apart.
STRIDE = [4, 3, 0, -3, -4, -3, 0, 3]
R_LIFT = [0, 0, 0, 0, 0, 2, 3, 2]
L_LIFT = [0, 2, 3, 2, 0, 0, 0, 0]
DROP = [1, 0, 0, 0, 1, 0, 0, 0]
ARM = [-2, -1, 0, 1, 2, 1, 0, -1]
RUN = {"trot": dict(hip=KNEE_ROW - 1, l_in=0, r_in=0, stride=0.5, full=False),
       "cross": dict(hip=88, l_in=4, r_in=-5, stride=1.0, full=True)}
RUN_VARIANT = "cross"         # the user (2026-10-09): 「用B吧」


def leg_masks(P, full):
    if not full:
        return P.masks["lleg"], P.masks["rleg"]
    R, C = np.mgrid[0:128, 0:128]
    op = P.design[..., 3] > 0
    lm = op & (R >= 89) & (C >= 55) & (C <= 61) & ~P.masks["lfore"]
    rm = P.masks["rleg"]
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
        K.put(top, K.swing_leg(P.design, P.masks["lfore"], 81, 94, -ARM[k]), 0, 0, under=True)
        K.put(top, K.swing_leg(P.design, P.masks["rfore"], 83, 95, ARM[k]), 0, 0)
        c = K.put(K.shifted(top, 0, DROP[k]), legs, 0, 0, under=True)
        c[SOLES + 1:] = 0
        keep = np.zeros((128, 128), bool)
        keep[:80 + DROP[k]] = True
        out.append(K.finish(c, OUT, SOLES, keep=keep, pinholes=4))
    return out


# the idle breathes here (as league_rengar's): the shared idle_breathe cut a row through the wrist blades (they hang to
# the shins) and shortened them as he bobbed, so the whole figure but the boots sinks 0 0 1 2 2 2 1 0 rows over the
# boots (layering, like the crouch), the forearms and their blades with it, rigid; the base game's pace (8 x 140 ms);
# import_native skips him (BREATHE_SKIP).
BREATH = [0, 0, 1, 2, 2, 2, 1, 0]


def frames(P, tag, run=None):
    if tag == "idle":
        return [P.design.copy() if n == 0 else frame(P, dict(sink=n)) for n in BREATH]
    if tag == "run":
        return run_frames(P, run)
    if tag == "dead":
        return [dead(P, k) for k in range(len(MS["dead"]))]
    return [frame(P, f) for f in POSES[tag]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts", help="write the part overlay PNG and stop")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", help="write a review sheet and GIF into this folder")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--run", choices=sorted(RUN), help="the run variant (default RUN_VARIANT)")
    a = ap.parse_args()
    P = Parts()
    if a.parts:
        P.overlay(a.parts)
        print({k: int(m.sum()) for k, m in P.masks.items()})
        return
    built = {tag: frames(P, tag, a.run) for tag in TAGS}
    for tag in TAGS:
        rows = K.audit(built[tag], P.design, OUT, SOLES)
        print(f"{tag:8s}", " ".join(f"{r['pieces']}p{r['holes']}h{r['orphans']}o{r['below']}b{r['area']}" for r in rows))
    if not a.no_write:
        bad = K.write_strips("zed", built, MS, NATIVE, CELL, CELL_PIVOT, PIVOT, check=a.check)
        if a.check:
            print("differs:", bad or "nothing")
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        K.review_sheet([(t, built[t]) for t in TAGS], os.path.join(a.review, "zed_strips_review.png"), z=4,
                       soles=SOLES)
        K.review_gif([(t, built[t]) for t in TAGS], MS, os.path.join(a.review, "zed_strips_review.gif"), z=4)


if __name__ == "__main__":
    main()
