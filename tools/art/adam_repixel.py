#!/usr/bin/env python3
"""亚当的像素图照 Codex 的原画按两倍密度重出：抠图和定位照 Codex 的，取样和清理用 tools/art/ragnarok_repixel.py。

    python tools/art/adam_repixel.py [--check] [--up 2] [--out-dir 文件夹]

为什么：用户 2026-11-21 看了跑步的动图：「这个跑步时候像素怎么看起来有点奇怪」「我要像素图风格但是你这种也太模糊了
不像吕布 索尔那样」。Codex 的 build_art.py 把 300 多像素高的原画按站高 54 格缩成 128 格，用的是最近邻：每 5、6 个原画
像素只取一个。原画里细的描边时有时无，皮肤、头发全是杂色点，跑步那张原画还带一块灰绿底，抠完边上留一圈发浅的杂色。
量出来（待机、跑步、普攻）：每帧 48 色，边缘是深描边的只有 0.59，和上下左右都不同色的杂点 0.62；索尔是 40 色、0.95、
0.38，吕布 40 色、0.92、0.47。后来又按两倍密度出（「都模糊成啥了 用PPU提高像素后再处理吧」，看过 1.5 倍和两倍的
对比后「亚当就3.3吧」）：一格 256、站高 108 格，游戏里 PPU 3.3，个子还是 33 个游戏像素。

亚当自己的设定：部位分皮肤、头发、绿叶裙、深色线条、其他（指虎、眼睛的蓝）；头发只认连成一大片的那块；描边是同色系的
深一档。特效照两倍用 Codex 自己的 effect_frames 出（每段特效一个缩放），身体和特效的像素一样细。

写 assets/source/adam/repixel/ragnarok_adam_native、ragnarok_adam_fx_native（#sheet.png + #anim.fanim），格子排法照
Codex 的放大两倍。tools/art/import_adam.py 从这里读。--check 只重算一遍，和仓库里的比，不写文件（要几分钟）。
"""
import os
import statistics
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_repixel as R  # noqa: E402

ADAM = os.path.join(ROOT, "assets", "source", "adam")
CODEX = os.path.join(ADAM, "runtime", "sprites", "ragnarok_adam_native")
CODEX_FX = os.path.join(ADAM, "runtime", "sprites", "ragnarok_adam_fx_native")
OUT_DIR = os.path.join(ADAM, "repixel")
OUT = os.path.join(OUT_DIR, "ragnarok_adam_native")
FX_OUT = os.path.join(OUT_DIR, "ragnarok_adam_fx_native")
# 密度：Codex 的两倍。tools/art/import_adam.py 的 UP 要一样
UP = 2.0

# 部位：0 透明、1 皮肤、2 头发、3 绿叶裙、4 深色线条、5 其他（指虎、眼睛的蓝）；每个部位留几档明暗
SKIN, HAIR, GREEN, INK, OTHER = 1, 2, 3, 4, 5
TONES = {SKIN: 5, HAIR: 5, GREEN: 3, INK: 2, OTHER: 3}
# 描边：同色系的深一档，不用一圈近黑的线（用户看 PPU 3.3 的跑步：「身体周围那个描边还是太厚了太浓了」：密度高了以后
# 一圈近黑的线显得又粗又重）。皮肤深红棕、头发深金棕、绿叶裙深绿、指虎这类深灰；往里一格是深色线条的按皮肤算
OUTLINE = {SKIN: (112, 62, 50), HAIR: (110, 86, 50), GREEN: (46, 76, 28), INK: (112, 62, 50), OTHER: (72, 72, 78)}


def codex_tool():
    return R.load(os.path.join(ADAM, "tools", "build_art.py"), "adam_build_art")


def parts_of(rgb):
    """原画每个像素属于哪个部位：很暗的是线条，偏绿的是绿叶裙，其余有颜色的按色相分，偏红（30 度以内）是皮肤、偏黄是
    头发，暗处一样（背光的皮肤是红棕、头发是橄榄棕）；几乎没颜色的白、灰（反光、指虎）和偏蓝的（眼睛）算其他。"""
    r, g, b = (rgb[..., i].astype(np.float32) for i in range(3))
    lum = (r * 30 + g * 59 + b * 11) / 100
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    sat = (mx - mn) / np.maximum(mx, 1)
    hue = np.degrees(np.arctan2(np.sqrt(3) * (g - b), 2 * r - g - b)) % 360
    lab = np.full(r.shape, OTHER, np.uint8)
    ink = lum < 72
    green = (g > r + 8) & (g > b + 5) & ~ink
    warm = ~ink & ~green & (sat >= 0.08) & ((hue < 75) | (hue > 340))
    skin = warm & ((hue < 30) | (hue > 340))
    lab[skin], lab[warm & ~skin], lab[green], lab[ink] = SKIN, HAIR, GREEN, INK
    return lab


def parts_of_tile(a):
    """一整格原画的部位图：parts_of 之外，头发只认连成一大片的那块（和离它不远的发梢、呆毛），别处被分成头发的
    零散像素（身上偏黄的肌肉阴影线）算皮肤。透明的是 0。"""
    from scipy import ndimage
    lab = parts_of(a[..., :3])
    lab[a[..., 3] == 0] = 0
    hair = lab == HAIR
    comp, n = ndimage.label(hair, structure=np.ones((3, 3), bool))
    if n:
        sizes = ndimage.sum(hair, comp, range(1, n + 1))
        main = comp == (int(np.argmax(sizes)) + 1)
        reach = max(4, round(0.04 * a.shape[0]))
        near = ndimage.binary_dilation(main, iterations=reach)
        keep = np.zeros(n + 1, bool)
        keep[1:] = ndimage.maximum(near, comp, range(1, n + 1)) > 0
        lab[hair & ~keep[comp]] = SKIN
    return lab


def style(up):
    # 头顶往下 16 行里的单个深色、蓝色像素是眼睛、眉毛，不当杂点清掉
    return R.Style(parts_of, TONES, INK, OUTLINE, up=up, tile_parts=parts_of_tile, head_keep=(INK, OTHER), head_rows=16)


def places(B, action, tiles, samples, up):
    """Codex 的 actor_frames 用的那套位置：每帧原画里对应一格的（缩放, 左上角 x, 左上角 y），密度乘 up。"""
    boxes = [t.getbbox() for t in tiles]
    heights = [b[3] - b[1] for b in boxes]
    standing = statistics.median(heights[i] for i in (samples or range(len(tiles))))
    scale = B.STANDING * up / standing
    hips = [B.body_x(t, standing) for t in tiles]
    center = statistics.median(hips[i] for i in (samples or range(len(tiles))))
    out = []
    for i, (box, hip) in enumerate(zip(boxes, hips)):
        ground = B.FOOT * up - (round(up) if action == "run" and i in (3, 7) else 0)
        if action in ("idle", "run"):
            pivot = hip
        elif action == "dead" and i >= 3:
            pivot = (box[0] + box[2]) / 2
        else:
            pivot = hip + np.clip(center - hip, -2 / scale, 2 / scale)
        out.append((scale, pivot - B.CELL * up / 2 / scale, box[3] - ground / scale))
    return out


def build(st):
    """{动作: [8 帧 RGBA]}，按 Codex 的 ACTORS 顺序。"""
    B = codex_tool()
    jobs, order = [], []
    for action, (file, rows, start, samples) in B.ACTORS.items():
        tiles = list(B.grid(Image.open(B.SOURCE / f"{file}.png").convert("RGBA"), 4, rows))
        tiles = [B.dominant(t, file == "run") for t in tiles[start:start + 8]]
        jobs += [(t, *pl) for t, pl in zip(tiles, places(B, action, tiles, samples, st.up))]
        order.append(action)
    flat = R.repixel(st, jobs, round(B.CELL * st.up))
    return {a: flat[i * 8:(i + 1) * 8] for i, a in enumerate(order)}


def effects(up):
    """Codex 的特效按 up 倍出：用它自己的 effect_frames（每段特效一个缩放），格子和尺寸都乘 up。"""
    B = codex_tool()
    B.CELL = round(B.CELL * up)
    out = {}
    for file, specs in B.FX.items():
        tiles = list(B.grid(Image.open(B.SOURCE / f"{file}.png").convert("RGBA"), 4, 4))
        for i, (name, size, _ms) in enumerate(specs):
            out[name] = [np.asarray(f) for f in B.effect_frames(tiles[i * 8:(i + 1) * 8], size * up, file == "fxc")]
    return out


def make(up):
    return [(OUT, *R.sheet_of(build(style(up)), CODEX, up)), (FX_OUT, *R.sheet_of(effects(up), CODEX_FX, up))]


if __name__ == "__main__":
    R.run(__doc__, make, UP)
