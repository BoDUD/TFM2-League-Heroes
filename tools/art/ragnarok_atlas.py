#!/usr/bin/env python3
"""终末包里按「逻辑像素图集」交付的英雄（冲田总司、须佐之男）：读 Codex 的 atlases/ 给 tools/art/ragnarok_art.py 用。

Codex 2026-11-23 起的交付不再是 #sheet.png / #anim.fanim，而是：
- atlases/<名>_actor.png、atlases/<名>_fx.png：一个动作（或一个特效）一行，每行 8 格，格子大小 frames.json 的 cell；
- atlases/frames.json：每格的矩形和秒数（actor / fx 两组），脚底点 ground，特效格的中心 fx_cell_anchor；
- *_4x.png 是严格的四倍最近邻，不用（和逻辑图一模一样，只是大）。

这里按整数倍 ZOOM 最近邻放大成「密度帧」交给引擎（像素画不能按小数缩放，不然像素大小不一）；英雄在游戏里多大由
import_<英雄>.py 的 PPU 定（逻辑图 56 格高、放大两倍 112 格，PPU 8/3 就是 42 个游戏像素，和别的终末英雄一样）。
"""
import json
import os

import numpy as np
from PIL import Image

ZOOM = 2


def meta(root):
    with open(os.path.join(root, "atlases", "frames.json"), encoding="utf-8") as f:
        return json.load(f)


def fill_holes(a, most=3):
    """身体里面被不透明像素整圈围住的透明小洞（不超过 most 个像素，不连着格子外面）补上：每个洞的像素取它四周不透明
    像素里最多的那个颜色。用户 2026-11-26 看补画：「模型像素看起来有缺失？能修复的地方你帮忙修复吧」——补画里不少帧身子
    中间漏着 1-3 个像素的透明点（Q 版的待机没有），透出地面。大一点的透明块（手臂和身子之间、两腿之间）是画出来的空隙，不动。"""
    from scipy import ndimage
    tr = a[..., 3] == 0
    lab, n = ndimage.label(tr)
    if n == 0:
        return a
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])).tolist())
    sizes = ndimage.sum(tr, lab, range(1, n + 1))
    out = a.copy()
    H, W = tr.shape
    for i, size in enumerate(sizes, 1):
        if i in edge or size > most:
            continue
        for y, x in zip(*np.nonzero(lab == i)):
            near = [tuple(a[yy, xx]) for yy in range(max(0, y - 1), min(H, y + 2)) for xx in range(max(0, x - 1), min(W, x + 2))
                    if a[yy, xx, 3] > 0]
            if near:
                out[y, x] = max(set(near), key=near.count)
    return out


def bank(root, kind, png, zoom=ZOOM, scale=1, fill=False):
    """{标签: [(放大后的帧, 秒)]}：kind 是 frames.json 里的 actor 或 fx。
    scale 是这张图一个逻辑像素占几格（*_4x.png 是 4：frames.json 的矩形照逻辑图写，切的时候乘上去）；fill 补身体里的小洞
    （fill_holes，在逻辑像素上补，补完再放大）。"""
    m = meta(root)
    px = np.asarray(Image.open(os.path.join(root, "atlases", png)).convert("RGBA"))
    out = {}
    for tag, clip in m[kind].items():
        frames = []
        for f in clip["frames"]:
            a = px[f["y"] * scale:(f["y"] + f["h"]) * scale, f["x"] * scale:(f["x"] + f["w"]) * scale]
            if fill and scale == 1:
                a = fill_holes(a)
            frames.append((np.repeat(np.repeat(a, zoom, 0), zoom, 1).copy(), float(f["duration"])))
        out[tag] = frames
    return out


def reader(root, name, hero_id, zoom=ZOOM):
    """给 ragnarok_art 的 READ：<id>_native 是角色图，<id>_fx_native 是特效图。"""
    def read(stem):
        if stem == f"{hero_id}_native":
            return bank(root, "actor", f"{name}_actor.png", zoom)
        if stem == f"{hero_id}_fx_native":
            return bank(root, "fx", f"{name}_fx.png", zoom)
        raise KeyError(stem)
    return read


def scaled(point, zoom=ZOOM):
    """逻辑图上的点 -> 放大后的点。"""
    return (point[0] * zoom, point[1] * zoom)


def mult(root, k=None):
    """补画按几倍放到他 hd_ 的密度：给了 k 用 k，不然读 frames.json 的 hd_multiplier。"""
    return k or int(meta(root).get("hd_multiplier", 4))


def atlas(root, png, kind, k):
    """(图名, 切的时候乘几, 放大几倍)：有 <名>_<kind>_<k>x.png 就用它（一格就是 hd_ 一格），没有就把逻辑图最近邻放大 k 倍
    （返工版的 <名>_<kind>_hd.png 就是逻辑图严格最近邻放大的，和这样放大一模一样）。"""
    big = f"{png}_{kind}_{k}x.png"
    if os.path.isfile(os.path.join(root, "atlases", big)):
        return big, k, 1
    return f"{png}_{kind}.png", 1, k


def redraw(root, png, names, k=None):
    """照原作补画的动作（2026-11-26 Codex 交的 ragnarok_fidelity_redraw_v3，老英雄的 13 条按 Q 版的像素格返工过：
    ragnarok_fidelity_redraw_fix，assets/source/<英雄>/fidelity）：-> ({本表的标签: [(帧, 秒)]}, {本表的标签: 脚底点})。

    k 是放到他 hd_ 密度的倍数（不给就读 frames.json 的 hd_multiplier）：返工版是他 Q 版的像素格（2，零福／波旬 3；v3 是 4，
    一个逻辑像素占 hd_ 4x4 格，比 Q 版粗一倍）；冲田、海耶的逻辑图按两倍放大（k = 2，和他们别的动作一样，frames.json 写的 4 不对）。
    names {它的动作: 本表的标签}。脚底点是 frames.json 的 ground 乘 k（每个动作也可以有自己的 ground）。"""
    m = meta(root)
    k = mult(root, k)
    png_, scale, zoom = atlas(root, png, "actor", k)
    got = bank(root, "actor", png_, zoom, scale, fill=True)
    frames, soles = {}, {}
    for theirs, ours in names.items():
        clip = m["actor"][theirs]
        g = clip.get("ground", m["ground"])
        frames[ours] = got[theirs]
        soles[ours] = (g[0] * k, g[1] * k)
    return frames, soles


def redraw_fx(root, png, names, k=None):
    """补画的特效（同上的倍数）：{本表的名字: [(帧, 秒)]}，names {它的名字: 本表的名字}（和英雄原来的特效重名时改个名）。"""
    k = mult(root, k)
    png_, scale, zoom = atlas(root, png, "fx", k)
    got = bank(root, "fx", png_, zoom, scale)
    return {ours: got[theirs] for theirs, ours in names.items()}


def redraw_point(root, kind, name, k=None, point=None):
    """补画里一个特效的挂点（frames.json 的 anchor，特效格里的点）乘 k；point 给了就换算那个点。"""
    m = meta(root)
    k = mult(root, k)
    p = point if point is not None else m[kind][name]["anchor"]
    return (p[0] * k, p[1] * k)


def redraw_offset(root, name, k=None, frame=None, nudge=(0, 0)):
    """补画里一个特效离脚底点的偏移（frames.json 的 offset，或者 frame_offsets 里第 frame 帧（从 1 数）的）乘 k，
    再加 nudge（hd_ 像素：我们自己挪的，比如不压脸）。"""
    m = meta(root)
    k = mult(root, k)
    fx = m["fx"][name]
    o = fx["offset"]
    if frame is not None:
        o = fx.get("frame_offsets", {}).get(str(frame), o)
    return (o[0] * k + nudge[0], o[1] * k + nudge[1])


def redraw_shift(root, theirs, k=None):
    """补画动作每帧画进格子里的前移（frames.json 的 placement_changes 的 dx，往前为正）-> SHIFT 用的一串（每帧往回挪 dx x k）：
    技能自己真的位移（冲刺、跳刺、后跳）时，人画在原地，不然位移算两遍、收招时往回一跳。"""
    m = meta(root)
    k = mult(root, k)
    return [-c["dx"] * k for c in m["actor"][theirs]["placement_changes"]]
