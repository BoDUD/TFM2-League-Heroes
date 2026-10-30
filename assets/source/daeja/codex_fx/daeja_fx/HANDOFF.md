# 迭嘉特效与图标交接

## 本包内容

12组特效序列，共58帧；3个64×64技能图标。全部使用内置 image_gen 绘制，共21次成功生图（15份首稿、6份修订）。程序只对生图进行读回、裁格、色板取色、透明清理、对称化和排版，没有用几何方块替代生成特效。

- 根目录 `daeja_fx_*.png`：12张水平序列，严格8倍最近邻显示，不能把原提示词的16倍生图尺寸当作最终尺寸。
- `pixel_1x/daeja_fx_*.png`：导入应使用的12张1倍水平序列。每张无间隔、无边框，帧宽高为 manifest 的 `cell_1x`，从左往右切。
- 根目录 `daeja_icon_skill.png`、`daeja_icon_skill2.png`、`daeja_icon_ult.png`：均64×64，2px整格。
- `raw/`：21份原始生图，其中6份 `attempt1-*` 是被修订的旧稿。部分选用原图采用包内允许的纯黑底；1倍成品均已转换为真正透明背景。
- `manifest.json`：帧数、每格尺寸、最终尺寸、原图分行方式、取图区域、逐帧hash、对称、色板和原绑定说明。
- `preview.png`、`effects-loop.gif`：总览和动态预览（预览不是导入图）。
- `generation-prompts.txt`、`generation-history.json`：全部21次实际提示词与生图路径。
- `validation.json`：两包联检报告。

## 读回方法与验收

为避免超长生图丢帧，4帧原图通常为2×2、6帧为3×2、3帧为3×1、5帧为3×2且最后一格为空；原始布局以manifest的raw_grid为准。最终已排回一行，直接用pixel_1x切格。

先将每格生图取到规定色板，再以透明覆盖率判断逻辑格占用，取占用颜色中的多数色；使用同组共享取图范围维持各帧的膨胀/消散关系。以源图的一侧作为基准逐格镜像，确保飞行特效上下完全对称，其余左右完全对称。所有颜色和形状均来自生成图；缩到游戏格后细线与末帧碎风会比原图简化。

已通过：12序列/58帧/3图标齐全；1倍尺寸与cell_1x吻合；8倍图逐像素等于1倍最近邻放大；每帧非空；所有序列具有帧间变化；RGBA硬alpha；逐帧严格对称；削魔抗符印第8行以下身体区域全空；图标64×64且2px整格。

被动风弹为4帧，其中两帧在1倍取色后相同，保留了3种不同画面；其他序列的独立帧数量见manifest。未把重复帧算成额外生图。

本轮仅交付图像素材，未在工程中创建view_projectiles/view_effects/view_buffs绑定，未调整时长、伤害、方向旋转或播放层级，也未做游戏内验收。实际战场亮度和角色遮挡应在导入后核对。

## 清单

| 文件 | 帧数 | cell_1x（宽高） | 对称 |
|---|---:|---|---|
| daeja_fx_a_bolt.png | 4 | [10, 8] | top-bottom (pointing right) |
| daeja_fx_a_hit.png | 4 | [14, 14] | left-right |
| daeja_fx_p_bolt.png | 4 | [8, 6] | top-bottom (pointing right) |
| daeja_fx_p_hit.png | 3 | [10, 10] | left-right |
| daeja_fx_p_shred.png | 6 | [14, 30] | left-right |
| daeja_fx_q_wave.png | 4 | [16, 22] | top-bottom (pointing right) |
| daeja_fx_q_hit.png | 5 | [20, 20] | left-right |
| daeja_fx_e_gust.png | 6 | [46, 16] | top-bottom (pointing right) |
| daeja_fx_e_slow.png | 6 | [20, 10] | left-right |
| daeja_fx_r_wave.png | 4 | [22, 30] | top-bottom (pointing right) |
| daeja_fx_r_hit.png | 6 | [30, 30] | left-right |
| daeja_fx_r_fly.png | 6 | [44, 14] | left-right |
| daeja_icon_skill.png | 1 | [64, 64] | 图标 |
| daeja_icon_skill2.png | 1 | [64, 64] | 图标 |
| daeja_icon_ult.png | 1 | [64, 64] | 图标 |
