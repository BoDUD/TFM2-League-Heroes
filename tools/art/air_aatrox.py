#!/usr/bin/env python3
"""World Ender in the air: Aatrox's R strips rebuilt airborne from the approved frames (2026-10-04).

    python tools/art/air_aatrox.py [--check] [--report] [--out DIR] [--tag TAG ...]

Why. League's Aatrox flies for the whole of World Ender (measured from the client: ULT_Idle's lowest foot 39-73 units
over the floor, ULT_Run 88-117, ULT_Attack1 60-70; only the Q slams touch down). The user: 「剑魔的大招应该一直在天上
的吧？」. Codex's airborne redraw (assets/source/aatrox/REDO3.md, at_work/codex10-11) flew, but on a different body:
「剑魔开大后身材变胖」 (torso, chest plate, thighs and arms 3-5 squares wider than the idle) and a broken neck in q3_r 3 -
rejected. So here the R strips are made from what the user approved, and only lifted:

- attack_r, attack_p_r, skill2_r (new): the approved rig frames (aatrox_attack / attack_p / skill2.png, rig_aatrox.py)
  square for square above the hips - upper body, arms, blade, head - over the idle's own two legs DANGLING (DANGLE):
  each leg turned a little back about its hip with RotSprite as the run turns them (rig_aatrox.run_legs), its foot
  first tipped toe-down about the ankle (FOOT_TIP), the hips a little in so the feet hang <= ~6 apart, the far foot a
  row or two higher, every turned leg cleaned like the run's (knees kept two coloured squares wide), the red hip plates
  laid back on their turned thighs. The approved R wings behind: the wings loop (assets/source/aatrox/
  aatrox_fx_r_aura.png, the picture World Ender's aura plays between casts) on the standing point - the torso stays on
  the idle's place in these frames, so the pair sits behind the shoulders - one loop frame per frame (FLAP: a beat
  down for the take-off, spread at the top, at rest on landing). The whole figure is then lifted to the AIR table's
  feet height. The last frame is REST: the idle with the wings at rest (loop frame 1) on the ground - the picture the
  aura loop goes on from.
- skill_r, q2_r, q3_r: Codex's approved Q casts (aatrox_skill / q2 / q3.png) with the wings of Codex's redo2 R forms
  (assets/source/aatrox/codex_redo2/: the base squares untouched, wings added where the base was clear), every frame
  lifted to the AIR table before the slam (frames 6-7 on the ground as drawn), frame 8 REST.
- ult (the transformation): Codex's frames 2-7 were a slim dark body with a red rod for a sword. Now: frame 1 the
  idle taking off (the wings unfolding from behind the shoulders, still folded down), 2-7 the idle's own body
  (rig_aatrox: the design, the head exact, the gauntlet arm and the design's greatsword in the near fist in its
  exact directions, the red claw thrown out - League's ULT_into roar) on the dangling legs, the loop's wings turned
  out of their fold about their roots (ULT: degrees, + = raised) to the loop's spread and raised for the roar - at
  most ~55 squares across, never more than ~15 rows over the helmet -, lifted per AIR; frame 8 REST. The body never
  leaves the standing point's column (the head at the idle's offset from the pivot: no sideways jump).

Every frame is finished the same way (finish_r): wing pieces cut off by the body and one-square strands go, enclosed
pockets of 1-6 squares are filled, the outline closes round the light edges (design_aatrox.OUTLINE_DARK), outline
squares hanging off one square go (a stray one of Codex's Q frames too) - the approved head and the base frame's upper
body never repainted. Frames already higher than the AIR table keep their height; nothing goes under the feet line
(pivot + 11).
aatrox_cells.json: skill2_r gets skill2's pivots and timings (no other tag changes); build_aatrox.py plays it for W
under R (and its throw's flash, like the passive's streak on attack_p_r, has a copy drawn on the lifted body:
import_aatrox.py P_TIP_R / CLAW_R). --check rebuilds and compares with assets/source/native/ (exit 1 on a difference);
--report prints every frame's checks (one piece, no pockets, no hanging outline, palette, alpha, dark edge, the head
square for square and where it sits, the feet height, the rig forms' upper body against their base frames, the legs,
the transformation's wings); --out writes elsewhere.
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
import rig_aatrox as R  # noqa: E402
import design_aatrox as D  # noqa: E402
import strips  # noqa: E402  (design_aatrox puts the skill's scripts on the path)

NATIVE = os.path.join(ROOT, "assets", "source", "native")
SRC = os.path.join(ROOT, "assets", "source", "aatrox")
REDO2 = os.path.join(SRC, "codex_redo2")
CELLS = os.path.join(NATIVE, "aatrox_cells.json")
Z = 8
PIVOT = R.PIVOT
FEET = 11                                   # the feet line under the pivot (canvas row 99 = R.SOLES)

# feet over the feet line per frame (the user's table, REDO3.md): take off, fight in the air, land on the last
AIR = {"ult": [0, 2, 5, 8, 8, 6, 3, 0],
       "attack_r": [2, 5, 6, 6, 3, 0],
       "attack_p_r": [2, 5, 6, 6, 3, 0],
       "skill_r": [3, 6, 8, 6, 2, 0, 0, 0],
       "q2_r": [3, 6, 8, 6, 2, 0, 0, 0],
       "q3_r": [4, 8, 11, 7, 2, 0, 0, 0],
       "skill2_r": [2, 5, 6, 6, 4, 0]}
RIG_FORMS = {"attack_r": "attack", "attack_p_r": "attack_p", "skill2_r": "skill2"}
Q_FORMS = {"skill_r": "skill", "q2_r": "q2", "q3_r": "q3"}
SLAM = {"skill_r": (5, 6), "q2_r": (5, 6), "q3_r": (5, 6)}      # frames (from 0) on the ground as drawn
TAGS = ["attack_r", "attack_p_r", "skill2_r", "skill_r", "q2_r", "q3_r", "ult"]
# the wings loop's frame (1-6) per frame of the six-frame forms: the beat down as he takes off, spread in the air,
# folding as he lands, at rest on the ground (REST = loop frame 1)
FLAP = [2, 3, 4, 3, 2, 1]
# the dangling legs per frame (cycled): (near degrees, far degrees) about the hips (+ = the foot ahead; back = the toes
# tip down), a small sway so a held pose still breathes
DANGLE = [(-8, -22), (-10, -24), (-12, -26), (-10, -24)]
HIP_IN = {"near": 3, "far": 2}              # squares each hip comes in under the waist: feet <= ~6 apart
FAR_UP = 2                                  # the far leg a row up: one foot hangs lower than the other
FOOT_TIP = {"near": -30, "far": -30}        # the feet tipped toe-down about the ankle before the leg turns
FOOT_ROW = {"near": 96, "far": 96}          # the foot's rows from here down (the design's boots start on row 97)
ANKLE = {"near": (57.0, 96.0), "far": (69.0, 96.0)}
# the wings' roots (canvas) behind the shoulders, where the loop's two wings join the back
WING_ROOT = {"near": (56.0, 70.0), "far": (72.0, 70.0)}
WING_SPLIT = 64                             # the loop's middle column on the canvas (its anchor on the pivot)
# the transformation per frame: arms (blade angle, near fist, far claw) or None (the idle's), the wings (loop frame,
# degrees turned out of the fold: - folded down behind him, + raised), legs dangling (True) or the idle's (False)
ULT = [(None, (1, -25), False),
       ((156, (53, 83), (75, 80)), (2, -20), True),
       ((156, (49, 81), (78, 77)), (3, 0), True),
       ((156, (49, 81), (78, 77)), (4, 10), True),
       ((156, (49, 81), (78, 77)), (5, 18), True),
       ((156, (53, 83), (75, 80)), (3, 0), True),
       (None, (2, 0), True),
       "rest"]
WING_MAX_W = 55                             # squares across, the ult's widest
WING_MAX_UP = 15                            # rows over the helmet's top, the ult's highest
FRAGMENT = 8                                # wing pieces this small, cut off by the body, go


def lp(p):
    return R.lp(p)


def load(path):
    with Image.open(lp(path)) as im:
        return np.asarray(im.convert("RGBA"))


def cells():
    with open(lp(CELLS), encoding="utf-8") as f:
        return json.load(f)


def cut(big, cw, ch, n):
    cols = big.shape[1] // (cw * Z)
    out = []
    for i in range(n):
        X, Y = (i % cols) * cw * Z, (i // cols) * ch * Z
        b = big[Y:Y + ch * Z, X:X + cw * Z]
        f = b[Z // 2::Z, Z // 2::Z].copy()
        assert np.array_equal(np.repeat(np.repeat(f, Z, 0), Z, 1), b), f"frame {i} is not made of {Z}x{Z} blocks"
        out.append(f)
    return out


def to_canvas(f, pivot):
    """A cell frame on the 128 canvas, its pivot on PIVOT (nothing may be lost)."""
    a = np.zeros((128, 128, 4), np.uint8)
    R.over(a, f, PIVOT[0] - pivot[0], PIVOT[1] - pivot[1])
    assert (a[..., 3] > 0).sum() == (f[..., 3] > 0).sum(), "the frame does not fit the canvas"
    return a


def to_cell(a, pivot, cw, ch):
    c = np.zeros((ch, cw, 4), np.uint8)
    R.over(c, a, pivot[0] - PIVOT[0], pivot[1] - PIVOT[1])
    assert (c[..., 3] > 0).sum() == (a[..., 3] > 0).sum(), "the frame does not fit the cell"
    return c


# ------------------------------------------------------------------------------------------------ the wings
AURA = None


def aura():
    """The wings loop's six frames and its anchor (the standing point)."""
    global AURA
    if AURA is None:
        with open(lp(os.path.join(SRC, "aatrox_fx_anchors.json")), encoding="utf-8") as f:
            a = json.load(f)["r_aura"]
        (w, h), anchor, n = a["cell"], a["anchor"], a["frames"]
        big = load(os.path.join(SRC, "aatrox_fx_r_aura.png"))
        AURA = ([cut(big[:, i * w * Z:(i + 1) * w * Z], w, h, 1)[0] for i in range(n)], tuple(anchor))
    return AURA


def wings(k, turn=0.0):
    """Loop frame k (1-6) on the canvas, its anchor on PIVOT; each wing turned `turn` degrees about its root
    (+ = raised up and out, - = folded down behind the back)."""
    fr, (ax, ay) = aura()
    a = np.zeros((128, 128, 4), np.uint8)
    R.over(a, fr[k - 1], PIVOT[0] - ax, PIVOT[1] - ay)
    if not turn:
        return a
    out = np.zeros_like(a)
    for side, sign in (("near", -1), ("far", 1)):
        part = a.copy()
        if side == "near":
            part[:, WING_SPLIT:] = 0
        else:
            part[:, :WING_SPLIT] = 0
        R.over(out, R.turned(part, WING_ROOT[side], sign * turn, WING_ROOT[side]))
    return out


# ------------------------------------------------------------------------------------------------ the legs
def leg_mask(des, sm):
    rows = np.arange(128)[:, None]
    cols = np.arange(128)[None, :]
    return ((des[..., 3] > 0) & ~sm & (rows >= R.LEG_TOP) & (cols >= R.NEAR_LEG["cols"][0])
            & (cols < R.FAR_LEG["cols"][1]))


def dangle_legs(i, des, sm):
    """Frame i's two dangling legs [(canvas, plates)], far then near: each of the idle's legs (the near one with its
    foot turned toe-forward, rig_aatrox.leg_piece), its foot tipped toe-down about the ankle, turned about its hip
    (DANGLE), the hip HIP_IN squares in; cleaned like the run's legs; the far one FAR_UP rows up."""
    nd, fd = DANGLE[i % len(DANGLE)]
    out = []
    for L, side, deg in ((R.FAR_LEG, "far", fd), (R.NEAR_LEG, "near", nd)):
        near = side == "near"
        leg = R.leg_piece(des, sm, L, near)
        row = FOOT_ROW[side]
        foot = np.zeros_like(leg)
        foot[row:] = leg[row:]
        leg[row:] = 0
        s, (jx, jy) = R.turn(foot, ANKLE[side], FOOT_TIP[side])
        R.over_soft(leg, R.over(np.zeros_like(leg), s, int(round(ANKLE[side][0] - jx)),
                                int(round(ANKLE[side][1] - jy))))
        dx = HIP_IN[side] if near else -HIP_IN[side]
        up = 0 if near else FAR_UP
        hip = (L["hip"][0] + dx, L["hip"][1] - up)
        a = R.run_leg(leg, L, deg, hip)
        R.loose_ink(a)
        a = R.clean_leg(R.crumbs(a))
        plates = []
        for x, y in R.HIP_PLATES[side]:
            px, py = R.about((x, y), L["hip"], deg)
            plates.append((int(round(px + dx)), int(round(py)) - up, des[y, x].copy()))
        out.append((a, plates))
    return out


def airborne(base, des, sm, i):
    """A base frame (canvas) on the dangling legs: the base's squares above the hips kept square for square, the idle
    legs it stands on taken off (where the base still has them as the design draws them), the dangling legs under it,
    the red hip plates on their thighs. Returns (frame, the kept upper-body mask)."""
    lm = leg_mask(des, sm) & (base == des).all(-1)
    upper = base.copy()
    upper[lm] = 0
    um = upper[..., 3] > 0
    out = np.zeros_like(des)
    c0, c1 = R.HIP_BAND
    out[R.LEG_TOP, c0:c1 + 1] = des[R.LEG_TOP, c0:c1 + 1]
    legs = dangle_legs(i, des, sm)
    for a, _ in legs:                                   # the near leg over the far one
        R.over(out, a)
    out = R.over(out, upper)
    near = R.colm(legs[1][0])
    for k, (a, plates) in enumerate(legs):
        push = max(0, R.LEG_TOP - min(y for _, y, _ in plates))
        for x, y, c in plates:
            if out[y + push, x, 3] and not um[y + push, x] and not (k == 0 and near[y + push, x]):
                out[y + push, x] = c
    keep = um | R.head_mask(des)
    out = R.finish(out, des, keep)
    out = R.fold_ticks(R.hip_spur(out, des, 0), des, keep, 0)
    out[um] = upper[um]
    return out, um


# ------------------------------------------------------------------------------------------------ finishing
def pieces8(m):
    H, W = m.shape
    lab = np.zeros((H, W), int)
    sizes = [0]
    for y0, x0 in zip(*np.nonzero(m)):
        if lab[y0, x0]:
            continue
        k = len(sizes)
        lab[y0, x0] = k
        st, n = [(y0, x0)], 0
        while st:
            y, x = st.pop()
            n += 1
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < H and 0 <= xx < W and m[yy, xx] and not lab[yy, xx]:
                        lab[yy, xx] = k
                        st.append((yy, xx))
        sizes.append(n)
    return lab, sizes


def nb4(m):
    p = np.pad(m, 1).astype(int)
    return p[:-2, 1:-1] + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]


def nb8(m):
    p = np.pad(m, 1).astype(int)
    H, W = m.shape
    return sum(p[1 + dy:H + 1 + dy, 1 + dx:W + 1 + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx)


def ink(a):
    return (a[..., 3] > 0) & (a[..., :3] == D.COL["o"]).all(-1)


def holes(a, most=6):
    """Enclosed background pockets (4-connected) of `most` squares or fewer."""
    bg = a[..., 3] == 0
    H, W = bg.shape
    seen = np.zeros_like(bg)
    out = []
    for y0, x0 in zip(*np.nonzero(bg)):
        if seen[y0, x0]:
            continue
        st, part, edge = [(y0, x0)], [], False
        seen[y0, x0] = True
        while st:
            y, x = st.pop()
            part.append((y, x))
            edge |= y in (0, H - 1) or x in (0, W - 1)
            for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= yy < H and 0 <= xx < W and bg[yy, xx] and not seen[yy, xx]:
                    seen[yy, xx] = True
                    st.append((yy, xx))
        if not edge and len(part) <= most:
            out.append(part)
    return out


def finish_r(a, body, head, wing, feet_row):
    """A winged frame finished. `body` = squares never repainted (the base frame's / the rigged figure's), `head` = the
    pasted head (its own pinhole stays), `wing` = the wings' squares (only these and new outline change):
    wing pieces of FRAGMENT squares or fewer cut off from the main wing by the body go; one-square strands (a wing
    square with at most one opaque 4-neighbour, repeated) go; enclosed pockets of 1-6 squares are filled (the wing's
    colour inside a wing, else the outline); the outline closes round the light edges outside `head`; outline
    squares hanging off one square (8-neighbours) go; bits of two squares or fewer go."""
    a = a.copy()
    wing = wing & (a[..., 3] > 0) & ~body
    lab, sizes = pieces8(wing)
    for k in range(1, len(sizes)):
        if sizes[k] <= FRAGMENT:
            a[lab == k] = 0
            wing[lab == k] = False
    for _ in range(12):
        op = a[..., 3] > 0
        strand = wing & (nb4(op) <= 1)
        if not strand.any():
            break
        a[strand] = 0
        wing &= ~strand
    for _ in range(6):
        changed = False
        for part in holes(a):
            ring = {(yy, xx) for y, x in part for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1))} \
                - set(part)
            if all(head[yy, xx] for yy, xx in ring):
                continue                                    # the head's own pinhole
            if all(wing[yy, xx] for yy, xx in ring):
                cs = [tuple(int(v) for v in a[yy, xx]) for yy, xx in ring if not ink(a[yy:yy + 1, xx:xx + 1])[0, 0]]
                c = max(set(cs), key=cs.count) if cs else tuple(D.COL["o"]) + (255,)
                for y, x in part:
                    a[y, x] = c
                    wing[y, x] = True
            else:
                for y, x in part:
                    a[y, x] = list(D.COL["o"]) + [255]
            changed = True
        a, n, d = strips.complete_outline(a, color=D.COL["o"], dark=D.OUTLINE_DARK, feet=feet_row, keep=head)
        op = a[..., 3] > 0
        hang = ink(a) & (nb8(op) <= 1) & ~head
        a[hang] = 0
        lab, sizes = pieces8(a[..., 3] > 0)
        for k in range(1, len(sizes)):
            if sizes[k] <= 2:
                a[lab == k] = 0
                changed = True
        if not (changed or n or d or hang.any()):
            break
    return a


def lift(a, h):
    """The frame moved up h rows (nothing may leave the top)."""
    if h <= 0:
        return a
    assert not a[:h, :, 3].any(), "lifted out of the cell"
    b = np.zeros_like(a)
    b[:-h] = a[h:]
    return b


def feet_height(a, feet_row):
    ys = np.nonzero(a[..., 3].any(1))[0]
    return feet_row - int(ys.max())


def head_in(a, des):
    """The approved head's squares in a frame (found by its shape, square for square), or None."""
    hm = R.head_mask(des)
    ys, xs = np.nonzero(hm)
    vals = des[ys, xs]
    H, W = a.shape[:2]
    for dy in range(-ys.min(), H - ys.max()):
        for dx in range(-xs.min(), W - xs.max()):
            if np.array_equal(a[ys + dy, xs + dx], vals):
                m = np.zeros(a.shape[:2], bool)
                m[ys + dy, xs + dx] = True
                return m
    return None


# ------------------------------------------------------------------------------------------------ frames
def rest(des):
    """The idle with the wings at rest (loop frame 1) on the ground: every form's last frame."""
    w = wings(1)
    fig = des.copy()
    body = fig[..., 3] > 0
    a = fig.copy()
    put = (w[..., 3] > 0) & ~body
    a[put] = w[put]
    return finish_r(a, body, R.head_mask(des), put, R.SOLES)


def winged(fig, body, w, des):
    put = (w[..., 3] > 0) & ~(fig[..., 3] > 0)
    a = fig.copy()
    a[put] = w[put]
    return finish_r(a, body, R.head_mask(des), put, R.SOLES)


def rig_form(tag, base_frames, rows, des, sm, cw, ch):
    """attack_r, attack_p_r, skill2_r: the base frames on dangling legs with the loop's wings, lifted; REST last."""
    out = []
    n = len(rows)
    for i, (f, r) in enumerate(zip(base_frames, rows)):
        if i == n - 1:
            a = rest(des)
            h = 0
        else:
            base = to_canvas(f, r["pivot"])
            fig, um = airborne(base, des, sm, i)
            body = fig[..., 3] > 0
            a = winged(fig, body, wings(FLAP[i] if n == 6 else FLAP[min(i, 4)]), des)
            h = max(0, AIR[tag][i] - feet_height(fig, R.SOLES))
        out.append(lift(to_cell(a, r["pivot"], cw, ch), h))
    return out


def ult_frame(i, des, sm):
    arms, (k, turn), dangle = ULT[i]
    if arms is None:
        base = des.copy()
    else:
        angle, fist, claw = arms
        keep = R.head_mask(des)
        b = R.body(des, sm, far_arm=True)
        b = R.over(b, R.blade(des, sm, fist, angle))
        b = R.near_arm(b, fist, keep)
        b = R.far_arm(b, claw, claw=True, keep=keep)
        base = R.fill_blocks(R.finish(b, des, keep), des, keep)
    fig = airborne(base, des, sm, i)[0] if dangle else base
    body = fig[..., 3] > 0
    return winged(fig, body, wings(k, turn), des), fig


def ult(rows, des, sm, cw, ch):
    out = []
    for i, r in enumerate(rows):
        if ULT[i] == "rest":
            a, h = rest(des), 0
        else:
            a, fig = ult_frame(i, des, sm)
            h = max(0, AIR["ult"][i] - feet_height(fig, R.SOLES))
        out.append(lift(to_cell(a, r["pivot"], cw, ch), h))
    return out


def q_form(tag, base_frames, r_frames, rows, des, cw, ch):
    """skill_r, q2_r, q3_r: Codex's Q frames with the redo2 wings, lifted before the slam; REST last."""
    out = []
    n = len(rows)
    feet_row = rows[0]["pivot"][1] + FEET
    for i, (b, w2, r) in enumerate(zip(base_frames, r_frames, rows)):
        if i == n - 1:
            out.append(to_cell(rest(des), r["pivot"], cw, ch))
            continue
        body = b[..., 3] > 0
        assert np.array_equal(w2[body], b[body]), f"{tag} {i + 1}: redo2 changed the base"
        h = 0 if i in SLAM[tag] else max(0, AIR[tag][i] - feet_height(b, feet_row))
        a = lift(w2, h)
        bm = lift(b, h)[..., 3] > 0
        hm = head_in(a, des)
        assert hm is not None, f"{tag} {i + 1}: the head is not the approved one"
        wing = (a[..., 3] > 0) & ~bm
        a = finish_r(a, bm, hm, wing, feet_row)
        if i not in SLAM[tag]:                              # the outline closed under a lifted foot: up again
            a = lift(a, max(0, AIR[tag][i] - feet_height(a, feet_row)))
        out.append(a)
    return out


def layout(n):
    return R.layout(n)


def sheet(frames, cw, ch):
    cols, rows = layout(len(frames))
    s = np.zeros((rows * ch, cols * cw, 4), np.uint8)
    for i, f in enumerate(frames):
        X, Y = (i % cols) * cw, (i // cols) * ch
        s[Y:Y + ch, X:X + cw] = f
    return np.repeat(np.repeat(s, Z, 0), Z, 1)


def build(tags=None):
    c = cells()
    cw, ch = c["cell"]
    des = R.design()
    sm = R.sword_mask(des)
    out = {}
    rows_of = dict(c["tags"])
    rows_of["skill2_r"] = [{"pivot": r["pivot"], "ms": r["ms"]} for r in c["tags"]["skill2"]]
    for tag in TAGS:
        if tags and tag not in tags:
            continue
        rows = rows_of[tag]
        if tag in RIG_FORMS:
            base = cut(load(os.path.join(NATIVE, f"aatrox_{RIG_FORMS[tag]}.png")), cw, ch, len(rows))
            fr = rig_form(tag, base, rows, des, sm, cw, ch)
        elif tag in Q_FORMS:
            b = Q_FORMS[tag]
            base = cut(load(os.path.join(NATIVE, f"aatrox_{b}.png")), cw, ch, len(rows))
            r2 = cut(load(os.path.join(REDO2, f"aatrox_{tag}.png")), cw, ch, len(rows))
            fr = q_form(tag, base, r2, rows, des, cw, ch)
        else:
            fr = ult(rows, des, sm, cw, ch)
        out[tag] = fr
    return out, rows_of


def frame_checks(a, des, pivot, feet_row):
    """One frame's numbers: 8-connected pieces, enclosed 1-6 pockets (the head's own pinhole aside), outline squares
    hanging off one square, off-palette squares, alpha other than 0/255, the dark share of the silhouette's edge
    (luminance < 40), the head found square for square and its column from the pivot, the feet over the feet line."""
    op = a[..., 3] > 0
    _, sizes = pieces8(op)
    hm = head_in(a, des)
    pockets = 0
    for part in holes(a):
        ring = {(yy, xx) for y, x in part for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1))} - set(part)
        if hm is None or not all(hm[yy, xx] for yy, xx in ring):
            pockets += 1
    pal = {tuple(v) for v in D.COL.values()}
    off = sum(tuple(int(v) for v in c) not in pal for c in a[op][:, :3])
    q = np.pad(op, 1)
    edge = op & ~(q[:-2, 1:-1] & q[2:, 1:-1] & q[1:-1, :-2] & q[1:-1, 2:])
    dark = float((edge & (strips.lum(a[..., :3]) < 40)).sum()) / max(1, int(edge.sum()))
    head_x = None if hm is None else int(np.nonzero(hm)[1].min()) - pivot[0]
    return {"pieces": len(sizes) - 1, "pockets": pockets, "hang": int((ink(a) & (nb8(op) <= 1)).sum()),
            "off": off, "alpha": int(((a[..., 3] != 0) & (a[..., 3] != 255)).sum()), "edge": round(dark, 3),
            "head_x": head_x, "feet": feet_height(a, feet_row)}


def report(out, rows_of):
    """Every new frame checked (frame_checks), the rig forms' upper body against their base frames, the dangling
    legs (feet apart, one foot lower, knees), the transformation's wings (span, rows over the helmet)."""
    c = cells()
    cw, ch = c["cell"]
    des = R.design()
    sm = R.sword_mask(des)
    idle_x = int(np.nonzero(R.head_mask(des))[1].min()) - PIVOT[0]
    bad = 0
    for tag, fr in out.items():
        rows = rows_of[tag]
        base = None
        if tag in RIG_FORMS:
            base = cut(load(os.path.join(NATIVE, f"aatrox_{RIG_FORMS[tag]}.png")), cw, ch, len(rows))
        for i, (a, r) in enumerate(zip(fr, rows)):
            m = frame_checks(a, des, r["pivot"], r["pivot"][1] + FEET)
            want = AIR[tag][i]
            note = []
            if base is not None and i < len(fr) - 1:
                b = to_canvas(base[i], r["pivot"])
                um = (b[..., 3] > 0) & ~(leg_mask(des, sm) & (b == des).all(-1))
                g = to_canvas(a, r["pivot"]) if (a[..., 3] > 0).sum() else a
                best = min(((int((g[np.roll(um, -dy, 0)] != b[um]).any(-1).sum()), dy) for dy in range(0, 14)))
                note.append(f"upper body {int(um.sum())} squares, {best[0]} differ (lifted {best[1]})")
            ok = (m["pieces"] == 1 and not m["pockets"] and not m["hang"] and not m["off"] and not m["alpha"]
                  and m["edge"] >= 0.94 and m["head_x"] is not None and m["feet"] >= want
                  and (tag in Q_FORMS or m["head_x"] == idle_x))
            bad += not ok
            print(f"{tag:10s} {i + 1}  feet {m['feet']:2d} (table {want:2d})  pieces {m['pieces']}  pockets "
                  f"{m['pockets']}  hang {m['hang']}  off {m['off']}  alpha {m['alpha']}  edge {m['edge']:.3f}  "
                  f"head x {m['head_x']} (idle {idle_x})  {'; '.join(note)}{'' if ok else '  <-- CHECK'}")
    for i in range(len(DANGLE)):
        legs = dangle_legs(i, des, sm)
        info = []
        for (a, _), side in zip(legs, ("far", "near")):
            col = R.colm(a)
            ys = np.nonzero(col.any(1))[0]
            low = int(ys.max())
            foot_x = float(np.nonzero(col[low - 1:low + 1])[1].mean())
            thin = min(int(col[y].sum()) for y in range(ys.min() + 2, low))
            info.append((side, low, foot_x, thin))
        (_, lf, xf, tf), (_, ln, xn, tn) = info
        print(f"dangle {i + 1}: feet {abs(xf - xn):.1f} apart, the near foot {ln - lf} rows lower, the thinnest leg "
              f"row: far {tf}, near {tn} coloured squares")
    hm = R.head_mask(des)
    helmet = int(np.nonzero(hm)[0].min())
    for i, u in enumerate(ULT):
        if u == "rest":
            continue
        _, (k, turn), _ = u
        w = wings(k, turn)[..., 3] > 0
        ys, xs = np.nonzero(w)
        print(f"ult {i + 1}: wings {int(xs.max() - xs.min() + 1)} across, {helmet - int(ys.min())} rows over the helmet")
    print("all frames pass" if not bad else f"{bad} frames to check")
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--report", action="store_true", help="print every frame's checks")
    ap.add_argument("--out", help="write the strips to this folder instead of assets/source/native")
    ap.add_argument("--tag", action="append", help="only these tags")
    args = ap.parse_args()
    out, rows_of = build(args.tag)
    if args.report:
        report(out, rows_of)
    c = cells()
    cw, ch = c["cell"]
    same = True
    for tag, fr in out.items():
        big = sheet(fr, cw, ch)
        path = os.path.join(args.out or NATIVE, f"aatrox_{tag}.png")
        if args.check:
            ok = os.path.exists(lp(path)) and np.array_equal(load(path), big)
            same &= ok
            print(tag, "same" if ok else "DIFFERS")
        else:
            Image.fromarray(big).save(lp(path))
            print(tag, len(fr), "frames ->", path)
    want = [{"pivot": r["pivot"], "ms": r["ms"]} for r in c["tags"]["skill2"]]
    if args.check:
        ok = c["tags"].get("skill2_r") == want
        same &= ok
        print("cells skill2_r", "same" if ok else "DIFFERS")
        sys.exit(0 if same else 1)
    if not args.out and c["tags"].get("skill2_r") != want:
        c["tags"]["skill2_r"] = want
        with open(lp(CELLS), "w", encoding="utf-8", newline="\n") as f:
            json.dump(c, f, indent=1)
        print("aatrox_cells.json: skill2_r added (skill2's pivots and timings)")


if __name__ == "__main__":
    main()
