#!/usr/bin/env python3
"""炼金跑步的交叉步（用户 2026-11-21：「没有交叉步明显换腿啊」）。

    python tools/art/cross_singed_legs.py --frames <放好的 8 帧> --design <design_1x.png> --out <dir>

Codex 重画的 8 帧是同一条腿的两遍"马步"：亮的那条一直在前（落地、踩在身下，下一帧又抬膝往前），暗的那条一直在后，
从来不交换，而且两条腿只差半档亮度。腿画得好，不重画；照凯特琳跑步的办法（一条腿走一整圈，另一条晚半圈）只重排：

- Codex 的前半圈（第 1-4 帧）是对的：撑地那条腿（X）第 1 帧在前面落地，一路往身后滑（靴底 34 -> 33 -> 20 -> 10），另一条
  （Y）身后离地 -> 脚跟踢到身后 -> 挡在后面 -> 抬膝在前；后半圈（第 5-8 帧）落地的脚在身前停两帧又一下跳到身后 20 格，不用。
- 新的 8 帧 = 第 1-4 帧两遍（整张用，上半身、盾、药瓶手都是那一帧自己的），第二遍 X、Y 身份对调：近侧腿（亮）一整圈是
  前脚落地 -> 踩在身下 -> 斜在身后 -> 身后蹬地 -> 离地 -> 脚跟踢到身后 -> 挡在后面 -> 抬膝在前 -> 落地，远侧腿（暗）晚半圈。
- 每帧的两条腿（X / Y）：
  第 1 帧 X = 前面落地那条（右边那堆），Y = 身后刚离地那条（左边那堆）；
  第 2 帧 X = 踩在身下那条（腰以下全部），Y = 盾左边露出来的脚跟（HEEL_BOX，踢得比腰还高，不在腰以下）；
  第 3 帧 两条交叉：Y 抬着脚从 X 前面过（膝盖在前、脚往后收，鞋底离地 6 行），X 只露出左下的小腿和脚（撑地），
  按两条腿之间的描边分开（C3_STANCE），Y 再加上腰以上那段蓝色大腿（C3_THIGH_BOX）；
  第 4 帧 X = 身后蹬地那条（左边那堆），Y = 抬膝在前那条（右边那堆）。
- 亮暗：设计图的两条腿一样亮，近侧腿照它，远侧腿比它暗看得出的一档（FAR）。Codex 每帧每条腿画得亮暗不一（第 3、4 帧整体暗一两档），
  所以不是统一挪几档：每帧、每条腿、每种材质各自在那一串颜色里挪一个整数档，挑平均档位最接近目标的那个（一样近挑挪得少的）。
  挪完不比设计图的腿更亮：每种材质最亮只到设计图腿上用到的那一档（红色到 C41E30，最亮的 FA1726 设计图的腿上没有）。

腿：腰（鞋底往上 HIP 行）以下、裤子 / 靴子颜色的像素（描边、盾不算），连通块按横向重心分两堆，右边那堆是前腿。
"""
import argparse
import json
import os

import numpy as np
from PIL import Image
from scipy import ndimage

HIP = 17                                  # 腰在鞋底上面多少行（设计图：脚底第 61 行，裤子从第 45 行起）
# 远侧腿比近侧暗几格（每种材质那一串里）：红色最亮两档 C41E30 / A9292C 亮度（L*）只差 5，挪两格才看得出；
# 其他材质一格就差 10 左右
FAR = {0: -1, 1: -2, 2: -1, 3: -1}
HEEL_BOX = (0, 43, 12, 53)                # Codex 第 2 帧踢到身后的脚跟：x0, y0, x1, y1（不含 x1 / y1），盾的左边
C3_THIGH_BOX = (24, 43, 37, 51)           # Codex 第 3 帧摆动腿的大腿（腰以上那段蓝色弧线）


def c3_stance(y, x):
    """Codex 第 3 帧里撑地那条看得见的部分：第 62 行以下，和第 59-61 行第 22 列以左（两条腿之间隔着描边）。"""
    return y >= 62 or (y >= 59 and x <= 22)


def hexes(*h):
    return [tuple(int(x[i:i + 2], 16) for i in (0, 2, 4)) for x in h]


# 每种材质的颜色，从暗到亮（设计图的 36 色里）
FAMILIES = [
    hexes("343848", "3A476D", "626D94", "8F9BC3"),                                  # 裤子
    hexes("4D0B19", "631721", "751C24", "8F1F27", "A9292C", "C41E30", "FA1726"),    # 靴子红
    hexes("331821", "582920", "6C341B", "984A19", "AE5A18", "CF800C", "F6AA09"),    # 靴子棕、橙
    hexes("B68B18", "FDC117"),                                                      # 扣子金
]
NAMES = ["pants", "red", "brown", "gold"]
WHERE = {c: (f, i) for f, cs in enumerate(FAMILIES) for i, c in enumerate(cs)}
# 新帧 -> (用 Codex 的第几帧, 这一帧 X 当近侧还是远侧)；Y 是另一侧
PLAN = [(1, "near"), (2, "near"), (3, "near"), (4, "near"),
        (1, "far"), (2, "far"), (3, "far"), (4, "far")]


def leg_px(a, y, x):
    return a[y, x, 3] > 0 and tuple(int(v) for v in a[y, x, :3]) in WHERE


def legs(a):
    """(前腿, 后腿) 两个掩码。"""
    op = a[..., 3] > 0
    soles = np.nonzero(op.any(1))[0].max()
    m = np.zeros(op.shape, bool)
    for y, x in zip(*np.nonzero(op)):
        if y >= soles - HIP and leg_px(a, y, x):
            m[y, x] = True
    lab, n = ndimage.label(m, structure=np.ones((3, 3)))
    idx = [j for j in range(1, n + 1) if (lab == j).sum() >= 3]
    cx = np.array([ndimage.center_of_mass(m, lab, j)[1] for j in idx])
    w = np.array([(lab == j).sum() for j in idx], float)
    lo, hi = cx.min(), cx.max()
    right = cx > (lo + hi) / 2
    for _ in range(20):                    # 一维两分：从最左、最右的块开始，按大小加权
        if right.all() or (~right).all():
            break
        lo, hi = np.average(cx[~right], weights=w[~right]), np.average(cx[right], weights=w[right])
        right = np.abs(cx - hi) < np.abs(cx - lo)
    front, back = np.zeros_like(m), np.zeros_like(m)
    for j, r in zip(idx, right):
        (front if r else back)[lab == j] = True
    return front, back


def x_and_y(k, a):
    """Codex 第 k 帧的 (X 撑地那条, Y 摆动那条) 掩码。"""
    front, back = legs(a)
    if k == 1:
        return front, back
    if k == 4:
        return back, front
    box = np.zeros(front.shape, bool)
    x0, y0, x1, y1 = HEEL_BOX
    box[y0:y1, x0:x1] = True
    if k == 2:
        heel = np.zeros_like(box)
        for y, x in zip(*np.nonzero(box)):
            heel[y, x] = leg_px(a, y, x)
        return (front | back) & ~box, heel
    legs_ = front | back
    stance = np.zeros_like(legs_)
    for y, x in zip(*np.nonzero(legs_)):
        stance[y, x] = c3_stance(y, x)
    swing = legs_ & ~stance
    x0, y0, x1, y1 = C3_THIGH_BOX
    for y in range(y0, y1):
        for x in range(x0, x1):
            if leg_px(a, y, x) and WHERE[tuple(int(v) for v in a[y, x, :3])][0] == 0:
                swing[y, x] = True
    return stance, swing


def design_levels(design):
    """设计图两条腿每种材质的 (平均档位, 最亮用到第几档)：近侧腿的目标和上限。"""
    front, back = legs(design)
    m = front | back
    caps = {}
    for y, x in zip(*np.nonzero(m)):
        f, i = WHERE[tuple(int(v) for v in design[y, x, :3])]
        caps[f] = max(caps.get(f, 0), i)
    return levels(design, m), caps


def levels(a, mask):
    by = {}
    for y, x in zip(*np.nonzero(mask)):
        f, i = WHERE[tuple(int(v) for v in a[y, x, :3])]
        by.setdefault(f, []).append(i)
    return {f: float(np.mean(i)) for f, i in by.items()}


def fit(a, mask, target, caps):
    """mask 里每种材质各挪一个整数档（最亮到 caps[材质]），平均档位最接近 target[材质]。-> (新图, {材质: 挪了几档})。"""
    out = a.copy()
    by = {}
    for y, x in zip(*np.nonzero(mask)):
        f, i = WHERE[tuple(int(v) for v in a[y, x, :3])]
        by.setdefault(f, []).append((y, x, i))
    moved = {}
    for f, px in by.items():
        top = caps.get(f, len(FAMILIES[f]) - 1)
        ii = np.array([i for _, _, i in px])
        best = min(range(-4, 5), key=lambda s: (abs(np.clip(ii + s, 0, top).mean() - target[f]), abs(s)))
        for y, x, i in px:
            out[y, x, :3] = FAMILIES[f][min(max(i + best, 0), top)]
        moved[NAMES[f]] = best
    return out, moved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", required=True)
    ap.add_argument("--design", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    near, caps = design_levels(np.array(Image.open(a.design).convert("RGBA")))
    target = {"near": near, "far": {f: v + FAR[f] for f, v in near.items()}}
    print("near-leg target levels:", {NAMES[f]: round(v, 2) for f, v in sorted(near.items())},
          "brightest shade:", {NAMES[f]: v for f, v in sorted(caps.items())})
    src = {k: np.array(Image.open(os.path.join(a.frames, f"frame_{k}.png")).convert("RGBA")) for k in {p[0] for p in PLAN}}
    parts = {k: x_and_y(k, img) for k, img in src.items()}
    info = []
    for n, (k, x_role) in enumerate(PLAN, 1):
        y_role = "far" if x_role == "near" else "near"
        xm, ym = parts[k]
        out, x_moved = fit(src[k], xm, target[x_role], caps)
        y_moved = None
        if ym is not None:
            out, y_moved = fit(out, ym, target[y_role], caps)
        Image.fromarray(out).save(os.path.join(a.out, f"frame_{n}.png"))
        info.append(dict(frame=n, codex_frame=k, X=dict(role=x_role, px=int(xm.sum()), moved=x_moved),
                         Y=None if ym is None else dict(role=y_role, px=int(ym.sum()), moved=y_moved)))
        print(f"new frame {n}: Codex frame {k}; X {x_role} {x_moved}; Y " + ("hidden" if ym is None else f"{y_role} {y_moved}"))
    with open(os.path.join(a.out, "legs.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=1)


if __name__ == "__main__":
    main()
