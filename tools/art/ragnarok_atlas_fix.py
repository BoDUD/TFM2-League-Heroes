#!/usr/bin/env python3
"""终末包 Codex 逻辑像素图集的修正（现在只有坂田金时）：只在 Codex 自己的像素上整格地挪、拷，不缩放、不重画。

    python -I tools/art/ragnarok_atlas_fix.py [--check]

为什么：Codex 2026-11-27 交的金时（assets/source/kintoki）的生图每帧单独画，待机八帧里有四帧脸的朝向、眼睛的位置、头型都
不一样，循环起来脸会抖（用户 11-26 看索尔：「跑步时脸部像素别变形」「待机时候的动作 脸部变形也严重」）。所以：
- 待机、跑步每帧换成同一个头：母版是待机第 1 帧、跑步第 3 帧的头（按行写的范围 IDLE_ROWS / RUN_ROWS），每帧按头发和脸对齐
  （上下左右 3 格以内找最像的位置），清掉原来的头再整格贴上母版的像素；头的范围里一律是母版的头（这些帧的斧柄在脸旁边、
  不在脸前面），发带尾巴、领口不动，贴完补上 3 格以内的小洞。待机的头也换给别的动作里和待机差不多的站姿（普攻的前三帧和
  收手、下劈和终结技的前三帧、受击开头：tools/art/hero_reels.py 拼的待机里会插这几帧），不然每次出招一开始、一收招脸就跳一下。
- 待机第 3 帧整张换成第 4 帧的画：那一帧是另一版画，人窄一圈、斧头小一号，循环时一缩一放。
没有缩放：用户看了按 1.25 倍重出像素的那一版（Scale2x 加多数色取样，想让他和全包一样细又一样高）：「codex画出来的美术质量
很高啊 为什么你像素处理后质量这么差这两个英雄」——像素画按小数倍缩放，原来一格有的变一格、有的变两格，线条和描边都不匀了。
改成 Codex 原样的像素、两倍读进来、PPU 2.4（用户在三种 PPU 的对比图里选的）。

写 assets/source/kintoki/fix/atlases/（frames.json 和特效图照 Codex 的，角色图是修过的）；tools/art/import_kintoki.py 从这里读。
--check 只重算一遍和仓库里的比，不写文件。
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

# 金时：母版的头，行 -> (左, 右)（含两端），逻辑图的坐标
KINTOKI_IDLE_ROWS = {49: (46, 54), 50: (44, 55), 51: (43, 57), 52: (43, 58), 53: (43, 58), 54: (41, 58), 55: (41, 58),
                     56: (41, 58), 57: (41, 57), 58: (42, 57), 59: (42, 57), 60: (45, 56), 61: (45, 56), 62: (46, 56),
                     63: (47, 56), 64: (48, 55), 65: (49, 55)}
KINTOKI_RUN_ROWS = {48: (48, 52), 49: (48, 54), 50: (45, 55), 51: (45, 58), 52: (43, 58), 53: (43, 59), 54: (42, 59),
                    55: (41, 58), 56: (42, 58), 57: (43, 58), 58: (45, 58), 59: (46, 58), 60: (46, 58), 61: (47, 58),
                    62: (48, 58), 63: (49, 57), 64: (51, 56)}
# 和待机差不多的站姿（人和待机第 1 帧的重合度 0.77 以上），加上 hero_reels 拼待机时插的普攻、下劈第 2、3 帧
KINTOKI_NEAR_IDLE = [("attack", 0), ("attack", 1), ("attack", 2), ("attack", 7), ("skill", 0), ("skill", 1),
                     ("skill", 2), ("ult", 0), ("ult", 1), ("ult", 2), ("hit", 0), ("hit", 1), ("hit", 6)]
# heads：(母版的动作, 第几帧, 头的范围, 换哪些帧)；same_as：(动作, 这一帧, 换成哪一帧的画)
HEROES = {
    "kintoki": {"heads": [("idle", 0, KINTOKI_IDLE_ROWS, [("idle", i) for i in range(8)] + KINTOKI_NEAR_IDLE),
                          ("run", 2, KINTOKI_RUN_ROWS, [("run", i) for i in range(8)])],
                "same_as": [("idle", 2, 3)]},
}


def rows_mask(shape, rows):
    m = np.zeros(shape, bool)
    for y, (x0, x1) in rows.items():
        m[y, x0:x1 + 1] = True
    return m


def align(M, mask, T, search=3):
    """母版的头（mask 里的像素）挪多少最像 T 的头：同色的格数，减去一边透明一边不透明的一半，再稍微偏向不挪。"""
    ys, xs = np.nonzero(mask)
    best = None
    for dy in range(-search, search + 1):
        for dx in range(-search, search + 1):
            ty, tx = ys + dy, xs + dx
            ok = (ty >= 0) & (ty < T.shape[0]) & (tx >= 0) & (tx < T.shape[1])
            a = M[ys[ok], xs[ok]].astype(int)
            b = T[ty[ok], tx[ok]].astype(int)
            both = (a[:, 3] > 0) & (b[:, 3] > 0)
            same = both & (np.abs(a[:, :3] - b[:, :3]).sum(axis=1) < 45)
            miss = (a[:, 3] > 0) != (b[:, 3] > 0)
            s = same.sum() - 0.5 * miss.sum() - 0.2 * (abs(dx) + abs(dy))
            if best is None or s > best[0]:
                best = (s, dx, dy)
    return best[1], best[2]


def label4(mask):
    """四连通标号。"""
    H, W = mask.shape
    lab = np.zeros((H, W), int)
    n = 0
    for y0, x0 in zip(*np.nonzero(mask)):
        if lab[y0, x0]:
            continue
        n += 1
        st = [(y0, x0)]
        lab[y0, x0] = n
        while st:
            y, x = st.pop()
            for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= yy < H and 0 <= xx < W and mask[yy, xx] and not lab[yy, xx]:
                    lab[yy, xx] = n
                    st.append((yy, xx))
    return lab, n


def fill_small(a, region, most=3):
    """region 里 most 格以内、三面以上被包住的透明小洞补上（取四邻最多的颜色）。"""
    tr = (a[..., 3] == 0) & region
    lab, n = label4(tr)
    out = a.copy()
    H, W = tr.shape
    for i in range(1, n + 1):
        pts = np.argwhere(lab == i)
        if len(pts) > most:
            continue
        for y, x in pts:
            near = [tuple(a[yy, xx]) for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))
                    if 0 <= yy < H and 0 <= xx < W and a[yy, xx, 3] > 0]
            if len(near) >= 3:
                out[y, x] = max(sorted(set(near)), key=near.count)
    return out


def steady_head(M, mask, rows, T, grow=1):
    """T 的头换成 M 的头（mask 里的像素，整格贴）。-> (新的帧, 挪了多少)。"""
    top = min(rows)
    dx, dy = align(M, mask, T)
    R = T.copy()
    region = np.zeros(T.shape[:2], bool)
    for y, (x0, x1) in rows.items():
        yy = y + dy
        if 0 <= yy < T.shape[0]:
            g = grow if y < top + 11 else 0     # 头发那几行左右各放宽一格（原来的头比母版宽一点也清干净）
            region[yy, max(0, x0 + dx - g):x1 + dx + g + 1] = True
    R[region] = 0
    ys, xs = np.nonzero(mask)
    ty, tx = ys + dy, xs + dx
    ok = (ty >= 0) & (ty < T.shape[0]) & (tx >= 0) & (tx < T.shape[1])
    R[ty[ok], tx[ok]] = M[ys[ok], xs[ok]]
    grown = region.copy()
    grown[1:] |= region[:-1]
    grown[:-1] |= region[1:]
    grown[:, 1:] |= region[:, :-1]
    grown[:, :-1] |= region[:, 1:]
    return fill_small(R, grown), (dx, dy)


def cells_of(atlas, clip):
    return [atlas[f["y"]:f["y"] + f["h"], f["x"]:f["x"] + f["w"]].copy() for f in clip["frames"]]


def build(hero):
    """-> (修过的角色图, 说明)。"""
    src = os.path.join(ROOT, "assets", "source", hero, "atlases")
    with open(os.path.join(src, "frames.json"), encoding="utf-8") as f:
        meta = json.load(f)
    cfg = HEROES[hero]
    actor = np.array(Image.open(os.path.join(src, f"{hero}_actor.png")).convert("RGBA"))
    banks = {t: cells_of(actor, c) for t, c in meta["actor"].items()}
    notes = []
    for tag, master, rows, targets in cfg["heads"]:
        M = banks[tag][master].copy()
        mask = rows_mask(M.shape[:2], rows) & (M[..., 3] > 0)
        moved = []
        for t, i in targets:
            if (t, i) == (tag, master):
                continue
            banks[t][i], off = steady_head(M, mask, rows, banks[t][i])
            moved.append(f"{t} {i + 1} {off}")
        notes.append(f"{tag} frame {master + 1}'s head on: " + ", ".join(moved))
    for tag, i, j in cfg["same_as"]:
        banks[tag][i] = banks[tag][j].copy()
        notes.append(f"{tag}: frame {i + 1} = frame {j + 1}")
    for t, clip in meta["actor"].items():
        for cell, f in zip(banks[t], clip["frames"]):
            actor[f["y"]:f["y"] + f["h"], f["x"]:f["x"] + f["w"]] = cell
    return actor, notes


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    bad = 0
    for hero in sorted(HEROES):
        actor, notes = build(hero)
        src = os.path.join(ROOT, "assets", "source", hero, "atlases")
        out = os.path.join(ROOT, "assets", "source", hero, "fix", "atlases")
        same = {"frames.json": os.path.join(src, "frames.json"), f"{hero}_fx.png": os.path.join(src, f"{hero}_fx.png")}
        if a.check:
            p = os.path.join(out, f"{hero}_actor.png")
            if not os.path.isfile(p) or not np.array_equal(np.asarray(Image.open(p).convert("RGBA")), actor):
                print(f"{p}: differs")
                bad += 1
            for name, s in same.items():
                p = os.path.join(out, name)
                if not os.path.isfile(p) or open(p, "rb").read() != open(s, "rb").read():
                    print(f"{p}: differs from {s}")
                    bad += 1
            continue
        os.makedirs(out, exist_ok=True)
        Image.fromarray(actor).save(os.path.join(out, f"{hero}_actor.png"), optimize=True)
        for name, s in same.items():
            shutil.copyfile(s, os.path.join(out, name))
        print(hero)
        for n in notes:
            print("  " + n)
    if a.check:
        print("ragnarok_atlas_fix: ok" if not bad else f"ragnarok_atlas_fix: {bad} file(s) out of date")
        sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
