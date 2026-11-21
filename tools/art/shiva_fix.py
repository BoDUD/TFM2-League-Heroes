#!/usr/bin/env python3
"""湿婆（ragnarok_shiva）Codex 交的图收色：常态、轮回舞踊的燃烧形态两张身体图和特效。

    python tools/art/shiva_fix.py            # 读 assets/source/shiva/runtime/sprites，写 assets/source/shiva/snapped
    python tools/art/shiva_fix.py --check    # 和现在的 snapped/ 不一样就退出 1
    然后 tools/art/import_shiva.py、ppu_hd.py --hero shiva、hero_reels.py --hero shiva

Codex 2026-11-22 交的（shiva_packs/outputs/shiva_assets_done.zip）：一格 256，脚底 (128, 232)，常态 8 个动作、燃烧形态 8 个动作
（h_*）各 8 帧，特效八组各 8 帧。和小次郎一样（tools/art/kojiro_fix.py 有来由）收色：两张身体图合起来 64 色（同一套调色板，
变身时颜色不跳），特效每组 32 色。Codex 的原样在 runtime/sprites，只读。

收完色再改一处：燃烧形态的跑步（h_run）Codex 画成了五条胳膊，见 EXTRA_ARM。
"""
import os
import sys
from collections import deque

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_repixel as R  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "shiva", "runtime", "sprites")
OUT = os.path.join(ROOT, "assets", "source", "shiva", "snapped")
BODY = ("ragnarok_shiva_native", "ragnarok_shiva_tandava_native")
FX = "ragnarok_shiva_fx_native"

# h_run 八帧身后都是三条胳膊：举起来的一条，垂着的两条。别的动作（两个形态）都是四条。外侧垂着的那条（戴手镯、手张开）
# 和燃烧形态的待机一样，留着；里面那条贴着腰、颜色深一点，是多的，擦掉。
# 每帧：手上一点（从这里往外涂）、顶上几行各自能擦的 x 范围（那几行贴着上身和外侧胳膊，要切开）、再往下各行的 x 范围。
# 往下靠颜色挡住：腰带（偏蓝）、裤子（金色）不擦，贴着它们的黑描边算它们的。坐标是一格（256）里的。
EXTRA_ARM = [
    ((110, 180), {165: (120, 122), 166: (118, 122), 167: (117, 122), 168: (116, 122)}, (106, 121)),
    ((112, 178), {164: (120, 121), 165: (120, 122), 166: (118, 122), 167: (117, 120)}, (107, 121)),
    ((110, 177), {163: (119, 121), 164: (118, 121), 165: (117, 120)}, (106, 121)),
    ((110, 177), {163: (120, 121), 164: (119, 121), 165: (119, 121), 166: (117, 121), 167: (116, 121),
                  168: (116, 121)}, (106, 121)),
    ((110, 178), {163: (115, 119), 164: (113, 119), 165: (115, 120), 166: (114, 120), 167: (113, 120),
                  168: (113, 119)}, (105, 119)),
    ((109, 178), {163: (114, 119), 164: (115, 120), 165: (114, 120), 166: (113, 119), 167: (113, 119)}, (105, 119)),
    ((110, 177), {162: (115, 119), 163: (114, 120), 164: (114, 120), 165: (114, 120)}, (107, 120)),
    ((109, 177), {163: (114, 119), 164: (112, 120), 165: (114, 120), 166: (114, 119), 167: (113, 119),
                  168: (112, 119)}, (105, 119)),
]
OUTLINE = (15, 6, 5)  # 调色板里本来就有的深描边色


def near4(m):
    o = np.zeros_like(m)
    o[1:] |= m[:-1]
    o[:-1] |= m[1:]
    o[:, 1:] |= m[:, :-1]
    o[:, :-1] |= m[:, 1:]
    return o


def flood(start, ok):
    """从 start 起八方向涂满 ok 里连着的格子。"""
    got = np.zeros_like(ok)
    h, w = ok.shape
    got[start] = True
    q = deque([start])
    while q:
        y, x = q.popleft()
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w and ok[ny, nx] and not got[ny, nx]:
                    got[ny, nx] = True
                    q.append((ny, nx))
    return got


def drop_arm(cell, seed, rows, span):
    rgb = cell[..., :3].astype(int)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    solid = cell[..., 3] > 0
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    body = solid & ((b > r) | ((r > 80) & (g > 0.55 * r) & (b < 0.45 * g)))  # 腰带、裤子
    dark = solid & (lum < 40)
    skin = solid & ~body & ~dark & (r > 1.3 * g)
    room = np.zeros_like(solid)
    for y in range(min(rows), cell.shape[0]):
        x0, x1 = rows.get(y, span)
        room[y, x0:x1 + 1] = True
    arm = flood((seed[1], seed[0]), solid & room & ~body & ~(dark & near4(body)))
    out = cell.copy()
    out[arm] = 0
    # 擦完以后胳膊范围里落单的碎点（六个像素以内）一起去掉
    ys, xs = np.nonzero(arm)
    box = np.zeros_like(solid)
    box[ys.min() - 2:ys.max() + 3, xs.min() - 2:xs.max() + 3] = True
    left = out[..., 3] > 0
    seen = np.zeros_like(solid)
    for y, x in zip(*np.nonzero(left & box)):
        if seen[y, x]:
            continue
        part = flood((y, x), left)
        seen |= part
        if part.sum() <= 6 and not (part & ~box).any():
            out[part] = 0
            arm |= part
    # 原来被胳膊挡着、现在露在外面的皮肤边，补上描边
    edge = (out[..., 3] > 0) & near4(arm) & skin & (lum > 55)
    out[edge, :3] = OUTLINE
    return out


def drop_extra_arm(sheet, fanim):
    sheet = sheet.copy()
    frames = fanim["anims"]["h_run"]["frames"]
    assert len(frames) == len(EXTRA_ARM)
    for f, (seed, rows, span) in zip(frames, EXTRA_ARM):
        x, y, w, h = (int(f["data"][k]) for k in "xywh")
        sheet[y:y + h, x:x + w] = drop_arm(sheet[y:y + h, x:x + w], seed, rows, span)
    return sheet


def make(_up=None):
    outs = R.snap_delivery(SRC, OUT, BODY, FX)
    stem, sheet, fanim = outs[1]
    outs[1] = (stem, drop_extra_arm(sheet, fanim), fanim)
    return outs


if __name__ == "__main__":
    R.run(__doc__, make, 2)
