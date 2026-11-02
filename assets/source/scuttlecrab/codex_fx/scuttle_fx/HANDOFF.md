# 迅捷蟹特效与技能图标交付

10 组特效图集，共 57 帧；3 个 64×64 技能图标。所有美术主体由内置 image_gen 生成，未用代码绘制或拼造替代特效。原始生成稿和实际提示词见 raw/ 与 generation-prompts.txt。

## 文件与导入

- 根目录 scuttle_fx_*.png：8 倍整数放大图集，一行从左到右按时间排列。
- pixel_1x/scuttle_fx_*.png：真实游戏像素版本，按 manifest.json 的 cell_1x 切格导入；不要从预览缩图读取。
- scuttle_icon_skill.png、scuttle_icon_skill2.png、scuttle_icon_ult.png：64×64 图标，逻辑格 2×2 px。
- manifest.json：帧数、尺寸、对称方式、原稿分帧边界、绑定说明、循环帧区间和文件哈希。
- qa.json：尺寸、硬透明、逐格对称、帧差异检查。
- preview.png、icons-preview.png、preview-*.gif：展示图。GIF 使用演示速度，不代表最终游戏播放时长。
- raw/earlier-attempts/：被简化版本替代的图标原稿，不用于导入。

## 制作方式与验证

为避免超长原稿导致模型漏帧，生成时采用两列多行的动画稿；沿透明间隔分开后转换为一行图集。每个目标逻辑格将原稿颜色归到提示词指定的材质色阶，再按多数颜色读取。随后镜像生成稿的左半边，使左右逐像素完全对称；q_shrine 还镜像上半边，保证上下对称。没有添加代码绘制的光环、碎片、泥土或角色身体。

全部 10 组图集通过逐帧左右对称检查，q_shrine 同时通过上下对称检查；透明度只有 0 / 255；57 帧均有可见内容，每组内部所有帧均不同。三个图标通过 64×64 检查。

r_dig 第 1–2 帧为钻入阶段，第 3–8 帧为土包循环（零起始索引 2–7）。其他循环特效为 q_shrine、q_haste、e_shell、e_slow。

## 清单

| 文件 | 帧数 | 每帧游戏像素 | 对称 |
|---|---:|---|---|
| scuttle_fx_a_hit.png | 4 | 18×14 | left-right |
| scuttle_fx_p_heal.png | 5 | 26×34 | left-right |
| scuttle_fx_q_shrine.png | 6 | 96×30 | left-right and top-bottom |
| scuttle_fx_q_haste.png | 6 | 26×10 | left-right |
| scuttle_fx_e_shell.png | 6 | 54×40 | left-right |
| scuttle_fx_e_burst.png | 5 | 70×44 | left-right |
| scuttle_fx_e_slow.png | 6 | 24×8 | left-right |
| scuttle_fx_r_dig.png | 8 | 60×26 | left-right |
| scuttle_fx_r_burst.png | 6 | 84×48 | left-right |
| scuttle_fx_r_up.png | 5 | 22×28 | left-right |
| scuttle_icon_skill.png | 1 | 64×64 | none |
| scuttle_icon_skill2.png | 1 | 64×64 | none |
| scuttle_icon_ult.png | 1 | 64×64 | none |

## 使用边界

已完成素材制作和文件层检查。未修改游戏、DLL、技能逻辑或导入脚本，未宣称已在实机验证。小尺寸的加速和减速特效有意保持淡且低，治疗的叶子和十字在多数色读取后较小；导入时应在暗色战场确认识别度和实际播放时长。源包内的特效贴图参考只在本地使用，没有重新分发。
