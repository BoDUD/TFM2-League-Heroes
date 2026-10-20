# 梅尔特效素材交付

本包完成 18 张特效帧表，共 79 帧。画面均由内置 image_gen 生成，随后按格取色、限制色板、二值化透明度和校正对称；未用代码绘制替代特效。日期：2026-10-20。

## 文件与导入

- 根目录的 18 张 `mel_fx_*.png` 为 8 倍最近邻预览。
- `pixel_1x/` 为对应的游戏原尺寸横向帧表，优先从此目录按帧切格。每张无间隔、无边框，从左到右播放。
- `manifest.json` 记录每帧尺寸 `cell_1x`、帧数、对称、绑定参考、处理方式和文件哈希。
- `qa.json` 记录文件规格检查；`overview.png` 为静态总览；`animation-preview.gif` 为动画总览。
- `raw/` 为最终采用的生图原稿；`raw/superseded/` 保留小光弹和九球环的旧稿，不能用于导入。
- `generation-prompts.txt` 为最终采用的实际提示词。生成模式：内置 image_gen。仅使用素材包的本地参考，未将参考贴图复制进交付包。

## 检查

18/18 张通过尺寸、帧数、每帧非空、0/255 硬 alpha、8 倍最近邻尺寸检查。所有要求左右对称的帧逐像素一致；E 法球另做上下对称。两张朝右光弹保持方向性。静态总览已经目视检查。

小光弹白芯与九颗蓄力光球在检查后补画。R 施放日蚀按等比缩放移入帧上部，下方保留 43 行透明空间供角色站位。W 保留开放底边与镜面亮边；原稿中的柔光通过高透明度阈值去除。日蚀深色中心保留。

## 处理与适用范围

生成器未稳定遵守原提示词的输出尺寸和 16 px 逻辑格。为避免极长图的比例失真，四/六/八帧原稿先按 2×2、3×2、4×2 排列，再切分并归一到每帧指定游戏尺寸，最终组装为一排。因此交付的 1 倍素材是从生成图重采样得到的，并非声称原稿严格落在 16 px 网格上。

取格采用前景多数色：源像素 alpha≥240 才参与取色；一个输出格的有效覆盖达到 10% 才保留，以防尾帧小火花被透明多数吞掉；颜色从该特效允许的色板中选择。此方法不同于将透明背景一起参与全格多数投票，已在 manifest 中记录。对称校正保留左半生成画面并镜像，不代表原稿本身完全对称。

正式动画的精确时间、光雨六次命中的同步、绑定锚点及角色遮挡需要导入游戏后校准。动画总览统一用每帧 140 ms 循环，只为检查画面变化，不是建议的游戏时长。本次交付完成素材制作与文件验证，没有执行文档中面向后续开发者的游戏绑定、构建或运行验收。

## 帧表清单

| 文件 | 帧数 | 每帧游戏像素 | 对称 |
|---|---:|---|---|
| mel_fx_a_bolt.png | 3 | 12 × 7 | none (a projectile, turned by the game) |
| mel_fx_p_bolt.png | 3 | 8 × 5 | none (a projectile, turned by the game) |
| mel_fx_a_hit.png | 4 | 16 × 16 | left-right |
| mel_fx_p_hit.png | 3 | 10 × 10 | left-right |
| mel_fx_p_3.png | 4 | 44 × 14 | left-right |
| mel_fx_p_6.png | 4 | 48 × 18 | left-right |
| mel_fx_p_9.png | 4 | 52 × 22 | left-right |
| mel_fx_q_volley.png | 8 | 48 × 56 | left-right |
| mel_fx_q_hit.png | 3 | 14 × 14 | left-right |
| mel_fx_e_orb.png | 4 | 28 × 28 | left-right and top-bottom |
| mel_fx_e_bound.png | 4 | 26 × 30 | left-right |
| mel_fx_e_slow.png | 4 | 26 × 10 | left-right |
| mel_fx_e_burn.png | 3 | 12 × 14 | left-right |
| mel_fx_r_cast.png | 8 | 64 × 80 | left-right |
| mel_fx_r_hit.png | 6 | 24 × 60 | left-right |
| mel_fx_w_on.png | 4 | 60 × 64 | left-right |
| mel_fx_m_mark.png | 4 | 14 × 12 | left-right |
| mel_fx_x_hit.png | 6 | 40 × 48 | left-right |
