# 阿萝拉特效交接：20组 / 92帧

## 交付
20张 aurora_fx_*.png 为8倍最近邻预览；pixel_1x/ 中同名20张为原生游戏像素序列，每张单行、按 manifest.json 的 frames 和 cell_1x 切帧。raw/ 保存20张内置 image_gen 原始输出，未经改写。generation-prompts.txt 为20次实际提示词及参考图顺序；fx-overview.png 为总览；QA.json 为重新读取文件后的验证结果。

## 读取与处理
所有特效形状先由 image_gen 绘制，没有用代码构造光弹、圆环、灵兔或其他替代图形。按包内要求，对原稿进行读取：去除上下透明留白；在等分点附近用alpha列投影低谷寻找帧边界；每帧按指定cell_1x取格，多数取色前映射到该组提示词的允许调色板；alpha以128分界硬化为0/255；每帧从内容较多的一半镜像得到要求的精确对称。manifest.json 记录原始尺寸、实际读取区域、帧边界及处理导致的对称像素改动数量。

## 验证结果
全部20张/92帧均非空。重新读取 pixel_1x 后，单帧/整张尺寸、0/255透明度、逐像素对称、允许调色板全部通过；预览确认为原生图严格8倍放大。a_bolt、q_out、q_back、e_wave朝右且上下对称，其余左右对称。R领域和冲击波的上下透明留白已重新裁定读取范围，避免被压成过扁的条。

## 说明
生成器的原稿尺寸、方格及对称不精确，因此请导入 pixel_1x，不能对 raw/ 按提示词中的16px直接切格。游戏逻辑、持续时间、绑定位置、层级、跟随关系和渲染效果尚未在引擎内验证；绑定建议按 manifest.json 的 binding 及原包说明执行。艺术形状是像素化近似，光墙、灵兔和星点的可读性以pixel_1x/及8倍预览为准。未安装到游戏工程。

## 序列表
| 文件 | 帧数 | 单帧像素 | 对称 |
|---|---:|---|---|
| aurora_fx_a_bolt.png | 4 | 14 × 8 | top-bottom |
| aurora_fx_a_hit.png | 3 | 12 × 12 | left-right |
| aurora_fx_q_out.png | 4 | 22 × 12 | top-bottom |
| aurora_fx_q_back.png | 4 | 24 × 12 | top-bottom |
| aurora_fx_q_hit.png | 4 | 16 × 16 | left-right |
| aurora_fx_q_back_hit.png | 4 | 18 × 22 | left-right |
| aurora_fx_q_curse.png | 4 | 12 × 12 | left-right |
| aurora_fx_p_mark.png | 4 | 12 × 8 | left-right |
| aurora_fx_p_spirit.png | 6 | 20 × 30 | left-right |
| aurora_fx_p_heal.png | 6 | 28 × 48 | left-right |
| aurora_fx_w_veil.png | 5 | 30 × 40 | left-right |
| aurora_fx_w_haste.png | 4 | 20 × 8 | left-right |
| aurora_fx_e_wave.png | 4 | 30 × 22 | top-bottom |
| aurora_fx_e_burst.png | 5 | 30 × 30 | left-right |
| aurora_fx_e_hit.png | 4 | 16 × 20 | left-right |
| aurora_fx_slow.png | 4 | 16 × 8 | left-right |
| aurora_fx_r_shock.png | 6 | 60 × 26 | left-right |
| aurora_fx_r_zone.png | 8 | 80 × 34 | left-right |
| aurora_fx_r_hit.png | 4 | 16 × 20 | left-right |
| aurora_fx_r_blink.png | 5 | 24 × 44 | left-right |

