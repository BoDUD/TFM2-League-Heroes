# 泽丽特效交付

24 张特效、106 帧已整理。造型与动作使用本次包内定稿，没有改人物。

每张均先用内置 image_gen 生成，未用代码绘制电弧、光圈或子弹。raw 为完整生图原稿。为使生图可完成，将原稿排为 2×2、3×2，长条特效排为逐行；最终重新排成规格要求的单行 PNG。

后处理：按共同坐标范围对齐原稿各帧，以色板分类后的多数颜色读回游戏尺寸；覆盖率至少 15% 的细火花保留非透明多数色；透明度二值化、逐格镜像校正、清除人物中心及激光左半区，再将每格放大 16 倍。最终导入使用 pixel_1x/。没有把原稿当作严格网格输出。

## 每张完成情况

| 文件 | 帧数 | 单格原尺寸 | 使用的指令 |
|---|---|---|---|
| zeri_fx_a_burst.png | 4 | [20, 5] | 原 PROMPTS 第 1 条 + raw 网格排版覆盖 |
| zeri_fx_a_hit.png | 4 | [12, 12] | 原 PROMPTS 第 2 条 + raw 网格排版覆盖 |
| zeri_fx_p_spark.png | 4 | [14, 11] | 原 PROMPTS 第 3 条 + raw 网格排版覆盖 |
| zeri_fx_p_hit.png | 5 | [18, 18] | 原 PROMPTS 第 4 条 + raw 网格排版覆盖 |
| zeri_fx_p_ready.png | 6 | [32, 44] | 原 PROMPTS 第 5 条 + raw 网格排版覆盖 |
| zeri_fx_p_shv.png | 4 | [32, 46] | 原 PROMPTS 第 6 条 + raw 网格排版覆盖 |
| zeri_fx_p_slow.png | 4 | [16, 7] | 原 PROMPTS 第 7 条 + raw 网格排版覆盖 |
| zeri_fx_p_haste.png | 4 | [20, 8] | 原 PROMPTS 第 8 条 + raw 网格排版覆盖 |
| zeri_fx_w_cast.png | 5 | [32, 42] | 原 PROMPTS 第 9 条 + raw 网格排版覆盖 |
| zeri_fx_w_pulse.png | 4 | [18, 9] | 原 PROMPTS 第 10 条 + raw 网格排版覆盖 |
| zeri_fx_w_laser.png | 6 | [204, 15] | 原 PROMPTS 第 11 条 + raw 网格排版覆盖 |
| zeri_fx_w_wall.png | 4 | [42, 11] | 原 PROMPTS 第 12 条 + raw 网格排版覆盖 |
| zeri_fx_w_hit.png | 4 | [16, 16] | 原 PROMPTS 第 13 条 + raw 网格排版覆盖 |
| zeri_fx_w_slow.png | 4 | [18, 8] | 原 PROMPTS 第 14 条 + raw 网格排版覆盖 |
| zeri_fx_e_cast.png | 5 | [46, 20] | 原 PROMPTS 第 15 条 + raw 网格排版覆盖 |
| zeri_fx_e_on.png | 4 | [30, 42] | 原 PROMPTS 第 16 条 + raw 网格排版覆盖 |
| zeri_fx_e_shot.png | 4 | [20, 6] | 原 PROMPTS 第 17 条 + raw 网格排版覆盖 |
| zeri_fx_e_hit.png | 4 | [12, 12] | 原 PROMPTS 第 18 条 + raw 网格排版覆盖 |
| zeri_fx_r_nova.png | 6 | [152, 62] | 原 PROMPTS 第 19 条 + raw 网格排版覆盖 |
| zeri_fx_r_on.png | 4 | [36, 50] | 原 PROMPTS 第 20 条 + raw 网格排版覆盖 |
| zeri_fx_r_st2.png | 4 | [36, 50] | 原 PROMPTS 第 21 条 + raw 网格排版覆盖 |
| zeri_fx_r_shot.png | 4 | [20, 11] | 原 PROMPTS 第 22 条 + raw 网格排版覆盖 |
| zeri_fx_r_hit.png | 5 | [18, 18] | 原 PROMPTS 第 23 条 + raw 网格排版覆盖 |
| zeri_fx_r_zap.png | 4 | [16, 32] | 原 PROMPTS 第 24 条 + raw 网格排版覆盖 |

## 验证与限制

24 张数量、总帧数、最终尺寸、16×16 纯色网格、0/255 透明、逐帧对称均由最终文件检查。围人效果的 14×36 中间区域留空；护盾内部留空；R 新星上下左右对称；W 激光每格左 102 列严格透明。manifest 保存每帧 rect/bbox、绑定、原稿格子与 SHA-256。qa.json 保存面积、差异帧数及各项检查。

生图不是精确逐格动画：部分散射电弧、白芯、彩虹细边和闪动与文字描述有差异，细小细节在原尺寸下已简化；镜像校正会使电弧更规则。共同范围取色保留原稿的扩散/淡出变化，但每一帧的精确电弧长度和指定宽度未逐项人工量成完全一致。

提供的素材清单没有帧时长，GIF 统一以 80ms 演示，不能当作运行时参数。像素素材与人物合成预览已提供；没有执行仓库导入、技能数据修改、游戏内实战检查，不能据此宣称技能机制已经实现。包内给 Claude 的导入步骤只用作接口上下文。

原英雄联盟纹理参考仅本地查看，未打包交付。generation-prompts.json 保存各条原始完整提示词，generation-run.json 保存实际调用的排版调整指令。

## 交付结构

- 根目录：每格 16×16 的最终特效条、manifest、QA、预览接触表。
- pixel_1x/：游戏切格导入源。
- raw/：24 张生图原稿。
- previews/：逐张 GIF 与套在本次定稿上的合成 GIF。
- inputs/design/：本次定稿与枪口/尺寸对照。
- rebuild_pixel_strips.py：用 numpy/Pillow 从原稿重建像素条。
