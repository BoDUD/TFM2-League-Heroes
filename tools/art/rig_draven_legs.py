#!/usr/bin/env python3
"""Draven's run legs, drawn on League's own run skeleton in the design's leg materials.

    python tools/art/rig_draven_legs.py OUT_DIR     # the 8 legs layers + a preview

Why (2026-10-10): Codex's legs came out thin and broken (it resampled them into the pack's boot boxes), its raw legs
never crossed and read deformed beside the design (the user: 「我要的是交叉步啊」「走路时候下半身还严重变形」). League's run
(assets/source/draven/run_joints.json: tools/lol/pose_joints.py on poses.json's run - hip, knee, foot, toe of the near
leg L_ and the far leg R_, game px from the pivot, the soles on y 11) crosses the legs every half cycle; each leg is
drawn on it as two straight bones of the design's own leg colours, one square wide outline:
  thigh  the black trousers (d d d D: the lit front edge D), from above the belt's underside to the knee;
  shin   the silver-blue greave (D e E W, a lit front), a knee plate (E W E) across the knee;
  boot   the design's small dark boot (b, toe B) under the ankle, toe forward (image right).
The far leg is drawn first and one shade darker (its greave D D e E), the near leg over it with its outline.
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
JOINTS = os.path.join(ROOT, "assets", "source", "draven", "run_joints.json")
HEX = {"0": "1A0E0E", "d": "292A32", "D": "474958", "e": "71829D", "E": "B0C6DE", "W": "F5F8FF", "b": "443631",
       "B": "695044"}
RGB = {k: tuple(int(v[i:i + 2], 16) for i in (0, 2, 4)) for k, v in HEX.items()}
PIVOT = (64, 88)
X_SHIFT = 3                        # League's legs run ~3 px behind its pivot; centred under our belt
TOP = 75                           # every thigh reaches up to this row (hidden under the belt and the ribbons)
HALF = {"thigh": 2.5, "shin": 2.0}  # a bone's interior: |d| < HALF (thigh 5, shin 4 squares), its outline to HALF + 1
NEAR = {"thigh": "ddddD", "shin": "DeEW", "plate": "EWE"}
FAR = {"thigh": "ddddd", "shin": "DDeE", "plate": "eEe"}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def joints():
    return json.load(open(lp(JOINTS), encoding="utf-8"))


def pt(j, bob):
    return np.array([PIVOT[0] + j[0] + X_SHIFT, PIVOT[1] + j[1]], float)


def bone_pixels(a, b, half):
    """Squares near the segment a-b: (y, x, t along 0..1, signed distance across, + = the front/right side)."""
    out = []
    v = b - a
    L = np.hypot(*v) or 1.0
    n = np.array([v[1], -v[0]]) / L          # the normal pointing image-right for a bone going down
    if n[0] < 0:
        n = -n
    x0, x1 = int(min(a[0], b[0]) - half - 2), int(max(a[0], b[0]) + half + 3)
    y0, y1 = int(min(a[1], b[1]) - half - 2), int(max(a[1], b[1]) + half + 3)
    for y in range(y0, y1):
        for x in range(x0, x1):
            p = np.array([x + 0.5, y + 0.5])
            t = np.clip(np.dot(p - a, v) / (L * L), 0, 1)
            q = a + t * v
            d = p - q
            dist = np.hypot(*d)
            if dist <= half + 1.0:
                out.append((y, x, t, float(np.dot(d, n)), dist))
    return out


def leg(canvas, hip, knee, foot, toe, mat):
    """One leg painted onto canvas (128 x 128 x 4): outline ring first, then the bones, the knee plate, the boot."""
    top = hip + (hip - knee) / (np.hypot(*(hip - knee)) or 1) * max(0.0, hip[1] - TOP)
    ankle = foot.copy()
    bones = [("thigh", top, knee), ("shin", knee, ankle)]
    inner, ring = {}, set()
    for name, a, b in bones:
        prof, h = mat[name], HALF[name]
        for y, x, t, s, dist in bone_pixels(a, b, h):
            if not (0 <= y < 128 and 0 <= x < 128):
                continue
            if abs(s) < h and dist < h + 0.35:
                k = int(np.clip(np.floor((s + h) / (2 * h) * len(prof)), 0, len(prof) - 1))
                if (y, x) not in inner or name == "shin":
                    inner[(y, x)] = prof[k]
            else:
                ring.add((y, x))
    # the knee plate: three squares across the knee, on the shin's line
    kx, ky = int(np.floor(knee[0])), int(np.floor(knee[1]))
    for i, ch in enumerate(mat["plate"]):
        inner[(ky, kx - 1 + i)] = ch
    # the boot: the sole on the foot's row + 1, heel one square behind the ankle, toe 3 ahead (image right)
    fy = int(np.floor(max(foot[1], toe[1]))) + 1
    fx = int(np.floor(ankle[0]))
    for x in range(fx - 1, fx + 4):
        inner[(fy, x)] = "b" if x < fx + 3 else "B"
        inner[(fy - 1, x)] = "b" if x < fx + 2 else "B"
    for y, x in list(inner):
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if (y + dy, x + dx) not in inner:
                    ring.add((y + dy, x + dx))
    for y, x in ring:
        if 0 <= y < 128 and 0 <= x < 128 and (y, x) not in inner:
            canvas[y, x] = RGB["0"] + (255,)
    for (y, x), ch in inner.items():
        if 0 <= y < 128 and 0 <= x < 128:
            canvas[y, x] = RGB[ch] + (255,)


def legs(k, bob=0):
    f = joints()[k]["joints"]
    c = np.zeros((128, 128, 4), np.uint8)
    for side, mat in (("R", FAR), ("L", NEAR)):
        P = {n: pt(f[f"{side}_{n}"], bob) for n in ("Hip", "Knee", "Foot", "Toe")}
        leg(c, P["Hip"], P["Knee"], P["Foot"], P["Toe"], mat)
    ys = np.nonzero(c[..., 3])[0]
    low = ys.max()
    if low != 99:                              # the planted sole on row 99
        c = np.roll(c, 99 - low, axis=0)
        if 99 - low > 0:
            c[:99 - low] = 0
    return c


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    tiles = []
    for k in range(8):
        c = legs(k)
        Image.fromarray(c).save(os.path.join(out, f"legs_{k + 1}.png"))
        tiles.append(c[70:101, 40:90])
    z = 8
    sheet = Image.new("RGBA", (len(tiles) * (50 * z + 8), 31 * z), (225, 225, 225, 255))
    for i, t in enumerate(tiles):
        sheet.alpha_composite(Image.fromarray(np.ascontiguousarray(t)).resize((50 * z, 31 * z), Image.NEAREST),
                              (i * (50 * z + 8), 0))
    sheet.convert("RGB").save(os.path.join(out, "legs_preview.png"))
    print("ok")


if __name__ == "__main__":
    main()
