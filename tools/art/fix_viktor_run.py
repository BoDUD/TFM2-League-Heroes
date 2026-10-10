#!/usr/bin/env python3
"""Viktor's run on League's own walk, the pelvis put back between the torso and the legs (the user, 2026-10-08:
「我们现在这个走路感觉腿部是变形的啊」「你觉得修好了？？？你能好好看吗」「走2这里有点脱节吧 之前英雄出现过这问题」
「没有明显交叉步的感觉 感觉像是平滑」).

Run v8 (fix_viktor_strips.run_frames_codex) drew the design's near leg twice where Codex's walk had its feet. Read from
the pivot, those feet stood still for a frame and then jumped 6-7 columns (the near one +7.3, +7.1, +4.6, -2.0, -4.6
over its planted frames): the body walks on at one speed in game, so a planted foot that stops under it is carried
along and then slips back - a glide; and the feet changed places within one frame (near - far +7.3 -> -7.3), so no
frame showed a leg coming past the other. With both legs the same, frames 1 and 5 were one picture.

The feet now follow League's run (tools/lol/pose_joints.py on the run tag's Run@0..933): each foot's centre (the mean
of its Foot and Toe joints) from its own hip, the right and left legs averaged into one cycle (TRAJ), the far leg half
a cycle after the near one - planted in frames 1-4 sliding back 2.3-2.5 columns a frame, lifted behind in 5-6, coming
past the planted leg in 7, reaching in 8. LIFT keeps the lifted foot up through the pass (2, 3, 3, 2 rows), so it
steps over the planted one; League kicks it higher behind (4-5 rows at this size), where the staff and the cape would
hide it. Everything else is run v8's: the same leg drawn twice (bent2, the hips drawn in to HIP_X, the knee bend), the
design's body bobbing as Codex's (upper_shift), the cells' pivots - except that a lifted leg's rows are kept within a
column of each other (bent_joined): bent2's three-square knee row and the shin under it jumped 2-3 columns a row, so
knee and shin met at a corner (the user: 「就是膝盖和腿感觉是脱节的」).

The leg parts taken out of the body also took the cape's inner edge by the staff (the pivot's column -5, the six leg
rows: outline, four dark reds, outline): the far leg's part reaches under it, and with the hips drawn in nothing
covered it again, so every frame had a see-through slot between the staff and the body (the user, at frame 2:
「走2这里有点脱节吧」, and again at frames 6-7: 「还是老问题这里空出来了」). That column stays in the body (CAPE), the
near leg still drawn over it.

Every run cell carries the design's rows 0-29 pixel for pixel (head to the torso's bottom), but not the design's
pelvis armour - rows 30-32, the gold / orange plates and navy under the core: run v8 took the leg parts out of the
body, and in six of its eight cells a transparent row opened between the torso and the legs, which complete_outline
closed into a black line across the waist, each leg carrying its own scrap of gold plate like a stick pushed under
the body. Each cell gets the design's own rows 30-32 back at its torso's own offset (only opaque design pixels are
written), so the torso, the pelvis and the legs are one figure as in the idle.

Under the pelvis the legs do not always meet it: a hidden far thigh left the pelvis's rear half over bare outline
(the user: 「走2这里有点脱节吧」 - Kayn's and Rakan's runs). As there, the design's own thighs are underlaid in the
three rows under the pelvis (design rows 33-35, leg colours only, the cape's red between the legs left out), only
where the cell is empty or bare outline, so the run's legs stay in front and nothing opens between the belt and the
legs.

Rebuilds the run strip from the design (run after fix_viktor_strips.py):

    python tools/art/fix_viktor_run.py
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
NATIVE = os.path.join(ROOT, "assets", "source", "native")
sys.path.insert(0, HERE)
import fix_viktor_strips as S  # noqa: E402
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

Z = 8
# League's run, frames 1-8: a foot's centre in columns from its hip (+ = forward) and the rows it is off the ground
TRAJ = [5.0, 2.5, 0.2, -2.15, -4.45, -5.45, -2.1, 1.5]
# League's ankle heights over its swing (5.6, 7.1, 4.4, 1.9 rows on legs 20 rows tall) scaled to our 12-row legs
# (~x0.6, the pass a row higher so the two 10-px boots never stack): a first [2, 3, 3, 2] kept the boot skimming 1-2
# rows over the ground as it slid back and put the swinging boot directly on the planted one in the passing frames,
# one navy lump (the user: 「感觉还是有点奇怪」)
LIFT = [0, 0, 0, 0, 3, 4, 4, 2]
HIP = 1               # both hips' column from the pivot, as HIP_X draws them in
# Run v10 (the user, 2026-10-10: 「维克托腿部走路好像有点变形的」): both feet had walked one line (each boot's centre at
# the pivot + 1 + TRAJ) from hips drawn 3 in, so the two 10-px boots met at every pass, and a lifted leg folded its
# thigh's top away and hung the boot under the knee. Now each leg is posed as league_zed's run legs: the thigh's rows
# shifted in proportion from the hip down to the knee, the shin leaning on to the boot, the boot rows moved whole,
# the shin + boot raised `lift` rows behind the thigh (a bent knee, the thigh kept whole). The hips come in 2 each; per
# frame (boot_dx, lift) from the leg's own place, League's order (planted 1-4 sliding back, heel up 5, up 6, past the
# planted boot a row clear of it in 7, reaching in 8); the far leg half a cycle later. The knee: half the boot's lean
# when planted, a column ahead of the boot when lifted.
HIPS2 = {"near": -2, "far": 2}         # in 2 each so the boots trade places front / back each half cycle
# The pace (the user again: 「有点怪啊走路 你没感觉吗」): run v10 kept run v9's 8 x 133 ms, a slow shuffle whose small
# steps slid along the ground. oppi's own Viktor walks 10 x 65 ms with feet lifted 1-2 px; at 80 ms a frame the same
# steps come quick (a cycle in 0.64 s). Lifting higher stacks his two 10-px boots into two slabs (tried: heel kicks up
# 2-3 behind the thigh).
RUN_MS = 80
STEP2 = [(4, 0), (2, 0), (0, 0), (-2, 0), (-4, 1), (-2, 1), (0, 1), (2, 0)]
CAPE = (-5, 6)        # the cape's inner edge kept in the body: its column from the pivot, rows from the leg top
TORSO = 30            # design rows 0..29 (from the design's top) are in every run cell as they are
PELVIS = (30, 33)     # design rows 30..32: the pelvis armour put back
BODY = (11, 24)       # design columns of the pelvis (from the design's left edge): right of the cape, left of the claw
THIGHS = (33, 36)     # design rows under the pelvis: the design's thigh tops underlaid
UNDERLAY = False      # run v10's legs keep their thighs whole: the design's still thigh tops would show beside them
OUT = (0x0B, 0x09, 0x10)
LEG = {(0x3E, 0x42, 0x70), (0x5B, 0x61, 0x94), (0x3A, 0x2C, 0x40), (0x7E, 0x86, 0xB8), (0x1A, 0x14, 0x20),
       (0x6A, 0x4A, 0x5A), (0x6F, 0x86, 0xAE)}   # the legs' navies, greys and shadows (not the cape's red)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def load(name):
    return np.asarray(Image.open(lp(os.path.join(NATIVE, name))).convert("RGBA"))[Z // 2::Z, Z // 2::Z].copy()


def feet():
    """{side: [(foot centre from the pivot, rows lifted)] * 8}: the far leg half a cycle after the near one."""
    near = [(HIP + TRAJ[k], LIFT[k]) for k in range(8)]
    return {"near": near, "far": [near[(k + 4) % 8] for k in range(8)]}


def bent_joined(part, hip, ankle, lift, bend):
    """fix_viktor_strips.bent2 with every drawn row at most one column off the row under it: bent2's knee row (three
    squares wide) and the shin under it jumped 2-3 columns a row on a lifted leg and met only at a corner."""
    knee = (hip + ankle) / 2 + bend
    rows = list(range(S.LEG_TOP + lift, S.SOLES + 1))       # the rows left after the thigh's top folds away
    want = []
    for y in rows:
        if y <= S.KNEE_ROW:
            dx = hip + (knee - hip) * (y - S.LEG_TOP) / (S.KNEE_ROW - S.LEG_TOP)
        elif y < S.BOOT_ROW:
            dx = knee + (ankle - knee) * (y - S.KNEE_ROW) / (S.BOOT_ROW - S.KNEE_ROW)
        else:
            dx = ankle
        want.append(int(np.floor(dx + 0.5)))
    got = want[:]
    for i in range(len(rows) - 2, -1, -1):                   # from the boot up
        got[i] = min(max(want[i], got[i + 1] - 1), got[i + 1] + 1)
    out = np.zeros_like(part)
    for y, dx in zip(rows, got):
        row = np.roll(part[y], dx, axis=0)
        m = row[:, 3] > 0
        out[y - lift][m] = row[m]
    if lift:
        shin(out)
    return out


def shin(leg):
    """The design's shin is one dark square between the knee and the gold ankle ring ('O s O'); stacked straight in
    the idle it reads, but on a bent lifted leg the three dark squares in a row read as outline - the knee hanging
    loose over the boot (the user: 「就是膝盖和腿感觉是脱节的」「感觉还是有点奇怪」). On lifted legs that row is
    widened to three squares of the leg's own navy round the shadow, as wide as the knee above and the ring below."""
    for y in range(S.LEG_TOP, S.BOOT_ROW):
        xs = [x for x in np.nonzero(leg[y, :, 3])[0] if tuple(int(v) for v in leg[y, x, :3]) != OUT]
        if len(xs) == 1:
            x = xs[0]
            leg[y, x - 1] = leg[y, x + 1] = (0x3E, 0x42, 0x70, 255)
            for e in (x - 2, x + 2):
                if not leg[y, e, 3]:
                    leg[y, e] = (*OUT, 255)


def zleg(part, hip_dx, boot_dx, lift):
    """league_zed's run_leg on Viktor's 12-row leg: thigh rows LEG_TOP..KNEE_ROW-1 shifted from hip_dx to the knee's,
    the shin leaning on to boot_dx at BOOT_ROW, the boot rows whole, the shin + boot `lift` rows up behind the thigh."""
    # the whole leg swings from the hip (the user: 「只有脚动上面的腿不动 不协调」 when the knee went half as far as the
    # boot): the knee as far as the boot, a column further when the leg is lifted
    knee_dx = hip_dx + boot_dx + (1 if lift else 0)
    boot_dx = hip_dx + boot_dx
    thigh = np.zeros_like(part)
    low = np.zeros_like(part)
    for r, c in zip(*np.nonzero(part[..., 3])):
        if r < S.KNEE_ROW:
            sh = hip_dx + int(np.floor((knee_dx - hip_dx) * (r - S.LEG_TOP) / (S.KNEE_ROW - S.LEG_TOP) + 0.5))
            if 0 <= c + sh < part.shape[1]:
                thigh[r, c + sh] = part[r, c]
        else:
            t = min(1.0, (r - S.KNEE_ROW) / (S.BOOT_ROW - S.KNEE_ROW))
            sh = int(np.floor(knee_dx + (boot_dx - knee_dx) * t + 0.5))
            if 0 <= c + sh < part.shape[1]:
                low[r - lift, c + sh] = part[r, c]
    m = (thigh[..., 3] == 0) & (low[..., 3] > 0)
    thigh[m] = low[m]
    return thigh


def fill_gaps(c, top):
    """A one- or two-square gap walled in (where the two legs cross, or between the pelvis and a thigh) from row
    `top` down: filled with the commonest colour round it (the outline colour there would stand alone)."""
    clear = c[..., 3] == 0
    H, W = clear.shape
    seen = np.zeros_like(clear)
    stack = [(y, x) for y in range(H) for x in (0, W - 1)] + [(y, x) for x in range(W) for y in (0, H - 1)]
    while stack:
        y, x = stack.pop()
        if 0 <= y < H and 0 <= x < W and clear[y, x] and not seen[y, x]:
            seen[y, x] = True
            stack += [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]
    hole = clear & ~seen
    lab = np.zeros_like(hole)
    for y, x in zip(*np.nonzero(hole)):
        if lab[y, x] or y < top:
            continue
        comp, st = [], [(y, x)]
        lab[y, x] = True
        while st:
            cy, cx = st.pop()
            comp.append((cy, cx))
            for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (cy + a, cx + b)
                if hole[q] and not lab[q]:
                    lab[q] = True
                    st.append(q)
        if len(comp) <= 2:
            cs = set(comp)
            votes = {}
            for cy, cx in comp:
                for a in (-1, 0, 1):
                    for b in (-1, 0, 1):
                        q = (cy + a, cx + b)
                        if q not in cs and c[q][3] and tuple(int(v) for v in c[q][:3]) != OUT:
                            k3 = tuple(int(v) for v in c[q][:4])
                            votes[k3] = votes.get(k3, 0) + 1
            fill = max(votes, key=votes.get) if votes else (*OUT, 255)
            for q in comp:
                c[q] = fill


def run_frames(design, bob):
    """The design's body over its near leg drawn twice (fix_viktor_strips.run_frames_codex), the feet from feet()."""
    near, far = S.legs()
    body = design.copy()
    body[(near[..., 3] > 0) | (far[..., 3] > 0)] = 0
    x, rows = S.PIVOT[0] + CAPE[0], slice(S.LEG_TOP, S.LEG_TOP + CAPE[1])
    body[rows, x] = design[rows, x]
    far = np.roll(near, S.FAR_FROM, axis=1)
    at = feet()
    out = []
    for k in range(8):
        f = STEP2[(k + 4) % 8]
        c = zleg(far, HIPS2["far"], *f)
        b = np.roll(body, bob[k], axis=0)
        m = b[..., 3] > 0
        c[m] = b[m]
        n = zleg(near, HIPS2["near"], *STEP2[k])
        m = n[..., 3] > 0
        c[m] = n[m]
        # the far boot's sole row left under the near boot raised over it: outline touching no colour - gone
        op = c[..., 3] > 0
        ink = op & (c[..., :3] == np.array(OUT, np.uint8)).all(-1)
        col = np.pad(op & ~ink, 1)
        near_col = np.zeros_like(op)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                near_col |= col[1 + dy:1 + dy + op.shape[0], 1 + dx:1 + dx + op.shape[1]]
        stray = ink & ~near_col
        stray[:S.LEG_TOP] = False
        c[stray] = 0
        fill_gaps(c, S.LEG_TOP)
        out.append(c)
    return out


def seat(a, cells):
    """The design's pelvis rows at each cell's torso offset, its thigh tops under them where the cell is bare."""
    cw, ch = cells["cell"]
    design = load("viktor_idle.png")[0:ch, 0:cw]
    ys, xs = np.nonzero(design[..., 3])
    top, left, right = int(ys.min()), int(xs.min()), int(xs.max())
    torso = design[top:top + TORSO, left:right + 1]
    colls = a.shape[1] // cw
    for k in range(len(cells["tags"]["run"])):
        cell = a[(k // colls) * ch:(k // colls) * ch + ch, (k % colls) * cw:(k % colls) * cw + cw]
        hit = None                                   # the torso's own offset in this cell (an exact match)
        for dy in range(-4, 4):
            for dx in range(-10, 10):
                y0, x0 = top + dy, left + dx
                win = cell[y0:y0 + TORSO, x0:x0 + torso.shape[1]]
                m = torso[..., 3] > 0
                if win.shape == torso.shape and np.array_equal(win[m], torso[m]):
                    hit = (dy, dx)
                    break
            if hit:
                break
        assert hit is not None, f"run cell {k + 1}: the design's torso is not in it"
        dy, dx = hit
        put = 0
        for y in range(*PELVIS):
            for x in range(left + BODY[0], left + BODY[1]):
                if design[top + y, x, 3]:
                    cell[top + y + dy, x + dx] = design[top + y, x]
                    put += 1
        under = 0
        for y in range(*THIGHS) if UNDERLAY else ():
            for x in range(left + BODY[0], left + BODY[1]):
                if design[top + y, x, 3] and tuple(int(v) for v in design[top + y, x, :3]) in LEG:
                    Y, X = top + y + dy, x + dx
                    if not cell[Y, X, 3] or tuple(int(v) for v in cell[Y, X, :3]) == OUT:
                        cell[Y, X] = design[top + y, x]
                        under += 1
        fill_gaps(cell, top + PELVIS[0] + dy)
        # the import closes the outline (complete_outline, dark 70): closed here first, so a gap that closure would
        # wall in is filled too and the import adds nothing new under the pelvis
        low = int(np.nonzero(cell[..., 3].any(1))[0].max())
        closed = G.complete_outline(cell, color=OUT, dark=70, feet=low)[0]
        fill_gaps(closed, top + PELVIS[0] + dy)
        cell[...] = closed
        print(f"run cell {k + 1}: torso at dy {dy} dx {dx}, pelvis {put} px, thighs underlaid {under} px")


def main():
    design = np.array(Image.open(S.D.lp(S.D.OUT)).convert("RGBA"))
    with open(lp(os.path.join(NATIVE, "viktor_cells.json")), encoding="utf-8") as f:
        cells = json.load(f)
    with open(lp(S.RUN_MANIFEST), encoding="utf-8") as f:
        bob = [fr["upper_shift"][1] for fr in json.load(f)["frames"]]
    at = feet()
    for k in range(8):
        print(f"frame {k + 1}: near {at['near'][k][0]:+.2f} up {at['near'][k][1]}, far {at['far'][k][0]:+.2f} up "
              f"{at['far'][k][1]}")
    for fr in cells["tags"]["run"]:
        fr["ms"] = RUN_MS
    with open(lp(os.path.join(NATIVE, "viktor_cells.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(cells, indent=1, ensure_ascii=False))
    a = load("viktor_run.png")
    S.place_run(a, cells, run_frames(design, bob))
    seat(a, cells)
    Image.fromarray(a).resize((a.shape[1] * Z, a.shape[0] * Z), Image.NEAREST).save(lp(os.path.join(NATIVE, "viktor_run.png")))


if __name__ == "__main__":
    main()
