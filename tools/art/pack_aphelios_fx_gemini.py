#!/usr/bin/env python3
"""Build aphelios_fx_rest_gemini.zip: the effects Codex's step-3 run left undrawn (its image quota ran out, HANDOFF of
2026-10-16 20:54: swap, r_cast, r_moon, r_boom, r_hit, mw, g_slow, q_s_haste, cre) as short Gemini prompts, the way the
user drew the first ten (memory gemini-skeleton-skin-prompts: 图1 a layout template, 图2 a style reference, a few
numbered rules, a solid background).

    python tools/art/pack_aphelios_fx_gemini.py [--out dist/aphelios_packs]

The pack: PROMPTS.md (one prompt an effect, in Chinese), template/<name>.png (the cells at up to 16 px a game px, at most 2000 px wide - the pack's
layout, tools/art/pack_aphelios_fx.py - thin grey cell lines, his idle as a dark grey figure where a figure stands,
90 % as the game shows him) and style/ (the user's own Gemini pictures of this hero's effects: the ring and the burst).
The pictures come back to assets/source/aphelios/codex_fx through tools/art/import_aphelios_fx.py (read at the cells'
size like Codex's pixel_1x).
"""
import argparse
import os
import shutil
import sys
import zipfile

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_aphelios_fx as PK  # noqa: E402

TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "ap_work", "fx", "aphelios_fx_rest_gemini")
CODEX = os.path.join(ROOT, "assets", "source", "aphelios", "codex_fx")
SQ = 16
SIZE = 0.90

# name -> (frames, symmetry, figure: None | "feet" (soles on the cell's bottom row), Chinese frame list, ramp, style ref)
REST = {
    "swap": ("左右对称", "feet", "换武器的月光：1 腰两侧几颗淡淡的光点；2 两道细细的月光弧从身体两侧往上扫；3 两道弧在头顶合成一弯约 14 格宽的月牙，最亮；"
             "4 月牙变淡，6 片小光羽往上飘；5 最后几片光羽。要淡，不要盖住人。", PK.MOON, "burst"),
    "r_cast": ("左右对称", "feet", "大招施放：1 脚下一个约 30×8 格的淡色椭圆光圈；2 头后面升起一弯约 24 格宽的大月牙；3 月牙最亮，外面一圈约 34 格的柔光，"
               "光点从两边往人身上飘；4 光点聚拢，脚下光圈发亮；5 变淡。", PK.MOON, "burst"),
    "r_moon": ("上下对称", None, "大招的月光弹，朝右飞，循环：一颗约 9 格的白色满月在格子右端，外面约 13 格的淡蓝光晕，后面一条约 18 格长的月光尾巴，"
               "几颗光点每帧闪烁。", PK.MOON, "burst"),
    "r_boom": ("左右对称", None, "大招在地上炸开：1 地上一团约 10 格的白光；2 一根约 8 格宽的白蓝光柱往上冲约 24 格，地上一个 24×8 格的扁光环；"
               "3 光柱约 32 格高，光环约 40 格宽、边最亮，环里地上一个月牙印记；4 光环约 48 格宽，光柱碎成光点；5 光点上升，月牙印记变淡；"
               "6 最后几颗光点。地上的光环中心在格子底边往上 5 格。", PK.MOON, "burst"),
    "r_hit": ("左右对称", None, "大招打中：1 约 5 格的白闪；2 约 12 格的淡蓝爆光，白芯；3 约 18 格的爆光，带 8 道往外的月光；4 光点散去。",
              PK.MOON, "burst"),
    "mw": ("左右对称", None, "主手武器在脚下的光环，循环：一个扁的光环约 20×5 格（暗绿色，要淡），环的前方正中一个约 4 格宽的小月牙，"
           "环上 4 颗较亮的光点轮流亮。", PK.GREEN, "ring"),
    "g_slow": ("左右对称", None, "被减速的人脚下，循环：一个约 14×4 格的扁椭圆淡紫色环，4 颗紫色光点往环上沉。要淡。", PK.VIOLET, "ring"),
    "q_s_haste": ("左右对称", None, "加速时脚下两侧的风痕，循环：两边各 3 道短短的红色风痕，中间空出约 16 格，每帧闪动。要淡。", PK.RED, "ring"),
    "cre": ("左右对称", "feet", "身边环绕的小回旋刃，循环：3 枚约 4 格大的银白色双刃小飞轮，在胸口高度、约 26×8 格的椭圆轨道上绕圈"
            "（两边各一枚、前面或后面一枚），每帧转一点。要小，不要盖住人。", PK.SILVER, "burst"),
}
STYLE = {"ring": "Gemini_Generated_Image_t4pc6rt4pc6rt4pc (7).jpg",    # Severum's Onslaught ring (q_s_on)
         "burst": "Gemini_Generated_Image_t4pc6rt4pc6rt4pc (6).jpg"}   # the Moonshot pop: the bolt and its burst


def cells():
    """name -> (frames, cell w, cell h) from the pack's layout lines."""
    import re
    pat = re.compile(r"row of (\d+) equal .*? cells, image size \d+x\d+ \(each cell (\d+)x(\d+)")
    out = {}
    for x in PK.FX:
        if x[0] in REST:
            n, w, h = (int(v) for v in pat.findall(x[-1])[0])
            out[x[0]] = (n, w // 16, h // 16)        # the layout's pixels are 16 a square
    return out


def figure():
    """His idle's mask at 90 %, a game px a square, soles on the last row."""
    f = PK.first_1x("idle")
    m = f[..., 3] > 0
    h, w = m.shape
    H, W = int(round(h * SIZE)), int(round(w * SIZE))
    ys = (np.arange(H) / SIZE).astype(int).clip(0, h - 1)
    xs = (np.arange(W) / SIZE).astype(int).clip(0, w - 1)
    return m[ys][:, xs]


def template(n, cw, ch, fig, path):
    SQ = max(4, min(16, 2000 // (n * cw)))           # at most 2000 px wide (Gemini's pictures)
    img = Image.new("RGB", (n * cw * SQ, ch * SQ), (0, 0, 0))
    d = ImageDraw.Draw(img)
    if fig is not None:
        fh, fw = fig.shape
        for k in range(n):
            x0 = k * cw + (cw - fw) // 2
            y0 = ch - fh
            for y, x in zip(*np.nonzero(fig)):
                d.rectangle([(x0 + x) * SQ, (y0 + y) * SQ, (x0 + x + 1) * SQ - 1, (y0 + y + 1) * SQ - 1], fill=(48, 48, 48))
    for k in range(1, n):
        d.line([(k * cw * SQ, 0), (k * cw * SQ, ch * SQ)], fill=(90, 90, 90), width=2)
    img.save(path)


def prompt(name, n, cw, ch, sym, fig, text, ramp):
    figure_ = "格子里深灰色的人影只是角色站的位置（脚在格子底边），" if fig else ""
    return (f"### `aphelios_fx_{name}.png`（{n} 帧，每格 {cw}×{ch} 格）\n\n"
            "附图：图1 `template/" + name + ".png`，图2 `style/" + ("ring" if REST[name][4] == "ring" else "burst") + ".jpg`\n\n"
            "```text\n"
            f"图1是布局模板：一行 {n} 个格子，每格 {cw}×{ch} 个像素方块（放大显示），{figure_}图2是同一个英雄的特效画风参考。\n"
            f"按图1的布局画 {n} 帧像素特效动画：{text}\n"
            "1. 每帧画在自己的格子里，大小按格子，不要出格，格子的顺序从左到右；\n"
            + ("2. 灰色人影的位置留空，不要画人，也不要画出灰色人影；\n" if fig else "2. 每帧的中心在格子正中；\n")
            + f"3. 画风和图2一致：粗方块像素、硬边、没有抗锯齿和模糊，发光的地方有白色的芯，光没有黑描边；颜色只用 {ramp}；\n"
            f"4. 每一帧都{sym}；\n"
            "5. 背景纯黑 #000000，去掉格子线，不要文字和编号。\n"
            "```\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "aphelios_packs"))
    a = ap.parse_args()
    if os.path.exists(TMP):
        shutil.rmtree(TMP)
    for sub in ("template", "style"):
        os.makedirs(os.path.join(TMP, sub))
    raw = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "ap_work", "fx_progress", "aphelios-fx", "raw", "provided")
    for k, fn in STYLE.items():
        shutil.copy2(os.path.join(raw, fn), os.path.join(TMP, "style", k + ".jpg"))
    fig = figure()
    lay = cells()
    doc = ["# 厄斐琉斯：剩下 9 张特效（Gemini 提示词）\n",
           "Codex 画到一半额度用完了（HANDOFF：swap、r_cast、r_moon、r_boom、r_hit、mw、g_slow、q_s_haste、cre 没画）。"
           "每条附两张图：图1 是布局模板（格子大小 = 游戏里的大小），图2 是你之前用 Gemini 画的这套特效（画风参考）。"
           "画好的图按名字保存（`aphelios_fx_<名字>.png` 或 jpg），发给我就行，我按格子读回、对称、换色。\n"]
    for name, (sym, f, text, ramp, _) in REST.items():
        n, cw, ch = lay[name]
        template(n, cw, ch, fig if f else None, os.path.join(TMP, "template", name + ".png"))
        doc.append(prompt(name, n, cw, ch, sym, f, text, ramp))
    with open(os.path.join(TMP, "PROMPTS.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(doc))
    zpath = os.path.join(a.out, "aphelios_fx_rest_gemini.zip")
    os.makedirs(a.out, exist_ok=True)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(TMP):
            for fn in sorted(files):
                p = os.path.join(root, fn)
                z.write(p, os.path.join("aphelios_fx_rest_gemini", os.path.relpath(p, TMP)).replace(os.sep, "/"))
    print(zpath, os.path.getsize(zpath) // 1024, "KB")


if __name__ == "__main__":
    main()
