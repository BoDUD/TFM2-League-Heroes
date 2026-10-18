"""Camille's legs from Codex's drawing (assets/source/camille/codex_legs/<tag>.png, asked by
assets/source/camille/LEGS_PROMPT_PPU.md on tools/art/pack_camille_legs.py's templates) read back square by square on
the templates' 6-px grid -> assets/source/camille/hd/legs_<tag>.png (each frame's leg layer, rig-canvas-sized, side by
side). tools/art/rig_camille_hd.py puts its own body (the design's squares) over them.

    python tools/art/import_camille_legs.py [--tag run ...]

Codex kept the templates' frames, ground lines and grid (a phase of a pixel or two per cell, found here by the most
uniform blocks round the legs) but redrew the whole picture (its HANDOFF: the upper body's squares all differ a little)
with soft edges, so: each square = the median of its block's middle 4 x 4, green keyed, snapped to the design's own leg
colours (the design from LEG_FROM down); only squares outside the rig's body and within BAND squares of a leg's guide
(hip -> knee -> blade tip, the same frames the templates were drawn from) are taken.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pack_camille_legs as PL  # noqa: E402
import ppu_rig as R  # noqa: E402
import rig_camille_hd as C  # noqa: E402

SRC = os.path.join(R.ROOT, "assets", "source", "camille")
LEG_FROM = 40
BAND = 4.5


def near_guide(shape, g):
    """Canvas squares within BAND of any guide segment."""
    H, W = shape
    yy, xx = np.mgrid[0:H, 0:W]
    px, py = xx + 0.5, yy + 0.5
    m = np.zeros((H, W), bool)
    for hip, knee, tip in g.values():
        for (ax, ay), (bx, by) in ((hip, knee), (knee, tip)):
            vx, vy = bx - ax, by - ay
            L2 = vx * vx + vy * vy or 1.0
            t = np.clip(((px - ax) * vx + (py - ay) * vy) / L2, 0, 1)
            m |= np.hypot(px - (ax + t * vx), py - (ay + t * vy)) <= BAND
    return m


def green(col):
    return (col[1] > 150 and col[0] < 140 and col[2] < 140) or (col[1] > 90 and col[0] < 60 and col[2] < 60)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", action="append")
    a = ap.parse_args()
    D = C.design()
    rig = C.make_rig(D)
    joints = json.load(open(R.lp(os.path.join(SRC, "hd", "camille_joints.json")), encoding="utf-8"))
    drv = C.driver(rig, joints)
    sheet_ms = R.sheet_of(C.HERO)
    leg = D.d0[LEG_FROM:]
    pal = np.unique(leg[leg[..., 3] > 0][:, :3], axis=0).astype(int)
    full_pal = np.unique(D.d0[D.d0[..., 3] > 0][:, :3], axis=0).astype(int)
    z = PL.CELL_PX
    path = R.lp(os.path.join(SRC, "hd", "legs_shift.json"))
    shifts = json.load(open(path)) if os.path.exists(path) else {}
    wholes = shifts.pop("whole", {})
    for tag in a.tag or C.LEG_TAGS:
        shifts[tag] = []
        wholes[tag] = []
        rows = R.fit_rows(joints["tags"][tag], len(sheet_ms[tag]))
        made = [C.leg_guides(rig, drv, joints, r["j"]) for r in rows]
        xs = np.concatenate([np.nonzero(f[..., 3].any(0))[0] for f, _ in made])
        gx = [p[0] for _, g in made for lg in g.values() for p in lg]
        x0 = int(min(xs.min(), min(gx))) - 2
        x1 = int(max(xs.max(), max(gx))) + 3
        w = (x1 - x0) * z
        img = np.asarray(Image.open(R.lp(os.path.join(SRC, "codex_legs", tag + ".png"))).convert("RGB")).astype(int)
        H, W = made[0][0].shape[:2]
        out = np.zeros((H, W * len(made), 4), np.uint8)
        for i, (bare, g) in enumerate(made):
            cx, cy = (i % PL.GRID[0]) * PL.CELL[0], (i // PL.GRID[0]) * PL.CELL[1]
            left = cx + max(0, (PL.CELL[0] - w) // 2 // z * z)
            top = cy + PL.SOLE_Y - rig.GY * z
            # where Codex put this frame: mostly where the template had it, but a frame that ran out of its cell it
            # moved back in and redrew whole (attack_q 3: standing, a high kick) - the body's squares matched against
            # its picture's non-green squares; our body then moves rows with it (legs_shift.json), never columns
            by, bx = np.nonzero(bare[..., 3] > 0)
            best_s = None
            for dr in range(-12, 13):
                for dc in range(-45, 46):
                    hit = 0
                    for r, c in zip(by[::3], bx[::3]):
                        y, x = top + (r + dr) * z + z // 2, left + (c - x0 + dc) * z + z // 2
                        if 0 <= y < img.shape[0] and 0 <= x < img.shape[1] and not green(img[y, x]):
                            hit += 1
                    if best_s is None or hit > best_s[0] or (hit == best_s[0] and abs(dr) + abs(dc) < abs(best_s[1]) + abs(best_s[2])):
                        best_s = (hit, dr, dc)
            _, dr, dc = best_s
            moved = np.roll(bare, dr, axis=0)
            if dr > 0:
                moved[:dr] = 0
            elif dr < 0:
                moved[dr:] = 0
            gm = {k: tuple((x, y + dr) for x, y in pts) for k, pts in g.items()}
            if abs(dc) <= 3 and dr == 0:
                want = near_guide((H, W), gm) & (moved[..., 3] == 0)
                want[:, :x0] = False
                want[:, x1:] = False
            else:
                # a frame Codex moved and redrew whole (attack_q 3: standing, a high kick drawn in front of the body):
                # its own figure is taken as it is (the design's size, snapped to the design's colours)
                want = np.ones((H, W), bool)
            whole = not (abs(dc) <= 3 and dr == 0)
            shifts.setdefault(tag, []).append(int(dr))
            wholes.setdefault(tag, []).append(whole)
            ys_, xs_ = np.nonzero(want)
            ox = left + dc * z
            best = None
            for py in range(-2, 4):
                for px in range(-2, 4):
                    var = 0.0
                    for r, c in zip(ys_[::3], xs_[::3]):
                        y, x = top + py + r * z, ox + px + (c - x0) * z
                        if 0 <= y and y + z <= img.shape[0] and 0 <= x and x + z <= img.shape[1]:
                            var += float(img[y:y + z, x:x + z].reshape(-1, 3).var(axis=0).sum())
                    if best is None or var < best[0]:
                        best = (var, px, py)
            _, px, py = best
            n = 0
            for r, c in zip(ys_, xs_):
                y, x = top + py + r * z, ox + px + (c - x0) * z
                if not (cy <= y and y + z <= cy + PL.SOLE_Y + 2 and 0 <= x and x + z <= img.shape[1]):
                    continue
                col = np.median(img[y + 1:y + z - 1, x + 1:x + z - 1].reshape(-1, 3), axis=0)
                if green(col):
                    continue
                pl_ = full_pal if whole else pal
                out[r, i * W + c, :3] = pl_[int(np.argmin(((pl_ - col) ** 2).sum(1)))]
                out[r, i * W + c, 3] = 255
                n += 1
            # only what lies within 4 squares of the body: a neighbour's blade reached in a frame read wide (attack_q 3)
            lay = out[:, i * W:(i + 1) * W]
            near = ndimage.binary_dilation(moved[..., 3] > 0, iterations=4)
            lbl, k = ndimage.label(lay[..., 3] > 0, structure=np.ones((3, 3)))
            if whole and k:
                sz = ndimage.sum(lay[..., 3] > 0, lbl, range(1, k + 1))
                near = lbl == (int(np.argmax(sz)) + 1)
            keep = set(np.unique(lbl[near])) - {0}
            stray = (lay[..., 3] > 0) & ~np.isin(lbl, list(keep))
            lay[stray] = 0
            n -= int(stray.sum())
            print(f"{tag} {i}: Codex moved it ({dc}, {dr}) squares, phase ({px}, {py}), {n} leg squares")
        Image.fromarray(out).save(R.lp(os.path.join(SRC, "hd", f"legs_{tag}.png")))
    json.dump(dict(shifts, whole=wholes), open(path, "w"), indent=1)
    print("written hd/legs_<tag>.png, hd/legs_shift.json")


if __name__ == "__main__":
    main()
