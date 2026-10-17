# 弗拉基米尔游戏精灵重画 v2

本轮成稿为直接在 24×40 原尺寸网格上逐像素绘制的静态待机造型。曾试一次原生 image_gen，生成稿仍过大，保存为 `generator_attempt.png`，未用作最终像素来源。

没有从大图抽样、平均缩小或删行取得最终成稿。头发、脸、高领、礼服、爪刃、裤子和鞋均在目标网格上直接定义，最终只进行整数最近邻放大。

| 文件版本 | 读回可见宽度 | 尖顶至脚底 | 色数 | 脚底行 |
|---|---|---|---|---|
| 1 高尖顶 | 24 px | 40 行 | 20 | 99 |
| 2 矮尖顶 | 24 px | 37 行 | 20 | 99 |

两版原尺寸画布为 128×128，放大图为 1024×1024，每像素严格对应纯色 8×8 方块。alpha 仅 0/255。脚底以下为空；两鞋间隙覆盖 x=64 原像素列，放大后对应 x=512。短发尖版仅改动顶部头发，脸及下方所有像素完全一致。

## 交付文件

- `vladimir_design_1.png`、`vladimir_design_2.png`：定位后的 8 倍图。
- `vladimir_design_1_1x.png`、`vladimir_design_2_1x.png`：定位后的原尺寸图。
- `vladimir_design_1_sprite.png`、`vladimir_design_2_sprite.png`：24×40 公共框；矮尖顶版本顶部 3 行透明。
- `vladimir_design_1_grid.txt`、`vladimir_design_2_grid.txt`：24 列、40 行字母网格，`.` 表示透明。
- `palette.hex`、`palette-letters.json`：24 色允许色板及字母映射，成稿实际使用 20 色。
- `redraw_vladimir.py`：可复用原尺寸绘制和验证脚本，在本文件夹运行可重新生成。
- `vladimir_design_comparison.png`：暗底 8 倍对比及灰褐底原尺寸预览。
- `validation.json`：尺寸、色数、透明度验证结果。
- `generator_attempt.png`、`generation-prompt.txt`：未选用的生图尝试及实际提示词。

已验证：40/37 行、24 列；严格 8 倍网格；20 色；alpha 0/255；两个同尺寸红眼同一行且眼色不出现在其它部位；三个 2 像素宽银扣；两版脸和身体一致。

设计为本轮待机造型；没有制作动作帧或修改游戏文件，尚未做游戏内显示和动画测试。
