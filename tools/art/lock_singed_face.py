#!/usr/bin/env python3
"""炼金跑步的脸锁成设计图那一张：Codex 重画的 8 帧，脸每帧都画得不一样（有的一个白眼、有的两只黑框眼、有的眼睛看不清），
跑起来会闪。用设计图（游戏里高清待机第 0 帧）自己的脸——光头、两只眼睛、面罩——每帧按最吻合的位置贴上去。

    python tools/art/lock_singed_face.py --frames <read_singed_run.py 的输出> --design <design_1x.png> --out <dir>

脸的范围在设计图（design_1x，人物裁好的 45 x 62）的第 13-23 行、第 22-31 列里：只取皮肤、眼白、描边、面罩、围巾的像素，
红色、橙色、金色（领子、护肩）和药罐的绿不算。位置：用皮肤和面罩像素比，每帧在头附近 ±12 x ±8 的范围里找对上最多的那个
偏移。贴上以后，脸那一块周围 2 格里还剩的旧脸颜色（Codex 那张脸多出来的边）改成描边色。
"""
import argparse
import json
import os

import numpy as np
from PIL import Image

FACE = (22, 13, 32, 24)                  # 设计图里脸那一块：x0, y0, x1, y1（不含 x1 / y1）
OUTLINE = (15, 11, 15)


def kinds(rgb):
    """每个像素是什么：皮肤、面罩（灰绿）、深色描边、其他。"""
    r, g, b = (rgb[..., i].astype(int) for i in range(3))
    skin = (r > 200) & (g > 120) & (g < 205) & (b > 100) & (b < 185)
    white = (r > 220) & (g > 220) & (b > 220)
    mask = (abs(r - g) < 30) & (abs(g - b) < 30) & (g > 80) & (g < 175) & (g >= r - 5)
    dark = (r + g + b) < 120
    warm = (r > 120) & (b < 100) & ~skin              # 领子、护肩的红橙金
    green = (g > 170) & (b < 90) & (r < 235)          # 药罐
    return skin, white, mask, dark, warm, green


def face_patch(design):
    """设计图的脸：[(x, y, rgba)]（设计图坐标）、用来对位的像素。"""
    x0, y0, x1, y1 = FACE
    sub = design[y0:y1, x0:x1]
    skin, white, mask, dark, warm, green = kinds(sub[..., :3])
    keep = (sub[..., 3] > 0) & ~warm & ~green
    pts = [(x0 + x, y0 + y, tuple(int(v) for v in sub[y, x])) for y, x in zip(*np.nonzero(keep))]
    probe = [(x0 + x, y0 + y) for y, x in zip(*np.nonzero(keep & (skin | mask)))]
    return pts, probe


def head_guess(frame):
    """这一帧光头的大概位置：上半身里皮肤像素的中位数。"""
    op = frame[..., 3] > 0
    skin = kinds(frame[..., :3])[0] & op
    top = np.nonzero(op.any(1))[0].min()
    skin[top + 30:] = False
    ys, xs = np.nonzero(skin)
    return int(np.median(xs)), int(np.median(ys))


def lock(frame, design, pts, probe):
    """在 frame 上找设计图的脸对上最多的偏移，贴上，收边。-> (新帧, 偏移, 对上的比例)。"""
    dx0, dy0 = head_guess(design)
    fx0, fy0 = head_guess(frame)
    fk = kinds(frame[..., :3])
    dk = kinds(design[..., :3])
    best = None
    for dy in range(fy0 - dy0 - 8, fy0 - dy0 + 9):
        for dx in range(fx0 - dx0 - 12, fx0 - dx0 + 13):
            hit = 0
            for x, y in probe:
                X, Y = x + dx, y + dy
                if 0 <= X < frame.shape[1] and 0 <= Y < frame.shape[0] and frame[Y, X, 3]:
                    same_skin = dk[0][y, x] and fk[0][Y, X]
                    same_mask = dk[2][y, x] and fk[2][Y, X]
                    hit += int(same_skin or same_mask)
            if best is None or hit > best[0]:
                best = (hit, dx, dy)
    hit, dx, dy = best
    out = frame.copy()
    placed = np.zeros(frame.shape[:2], bool)
    for x, y, c in pts:
        X, Y = x + dx, y + dy
        if 0 <= X < frame.shape[1] and 0 <= Y < frame.shape[0]:
            out[Y, X] = c
            placed[Y, X] = True
    # 收边：贴上的脸周围 2 格里，旧脸留下的皮肤 / 面罩颜色改成描边
    ys, xs = np.nonzero(placed)
    y0, y1, x0, x1 = max(ys.min() - 2, 0), ys.max() + 3, max(xs.min() - 2, 0), xs.max() + 3
    skin, white, mask, dark, warm, green = kinds(out[..., :3])
    fixed = 0
    for Y in range(y0, min(y1, out.shape[0])):
        for X in range(x0, min(x1, out.shape[1])):
            if placed[Y, X] or not out[Y, X, 3]:
                continue
            if skin[Y, X] or white[Y, X]:
                out[Y, X, :3] = OUTLINE
                fixed += 1
    return out, (dx, dy), hit / max(len(probe), 1), fixed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", required=True)
    ap.add_argument("--design", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    design = np.array(Image.open(a.design).convert("RGBA"))
    pts, probe = face_patch(design)
    info = []
    for k in range(1, 9):
        frame = np.array(Image.open(os.path.join(a.frames, f"frame_{k}.png")).convert("RGBA"))
        out, (dx, dy), share, fixed = lock(frame, design, pts, probe)
        Image.fromarray(out).save(os.path.join(a.out, f"frame_{k}.png"))
        info.append(dict(frame=k, offset=[dx, dy], matched=round(share, 2), outline_fixed=fixed))
        print(f"frame {k}: face at offset ({dx}, {dy}), {share:.0%} of the face matched before, {fixed} leftover px outlined")
    with open(os.path.join(a.out, "face.json"), "w", encoding="utf-8") as f:
        json.dump(dict(face=FACE, pixels=len(pts), frames=info), f, indent=1)


if __name__ == "__main__":
    main()
