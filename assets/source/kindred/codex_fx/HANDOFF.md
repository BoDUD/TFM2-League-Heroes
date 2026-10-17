# 千珏 · 第 3 步特效素材交付

本次按 kindred_fx_pack.zip 制作14张独立特效表（74帧）和12张动作叠加层，共26项。使用内置 image_gen 逐项生成，原稿完整保留。交付的是特效图，不包含游戏导入或实战验证。

## 文件

- 顶层26张PNG：独立特效为逐格8倍放大；动作叠加层为6倍，尺寸与包内定位图一致。
- pixel_1x/：26张逐格对应的原尺寸图。
- raw/：26张未经修改的生图原稿，已与生成器保存文件核对SHA256。
- previews/：14组GIF、14张帧对照图、12张叠加定位预览。定位图中的灰色人物、网格和十字只存在于预览，交付的透明叠加层不包含这些内容。
- index.html：离线预览，可切换素材、逐帧播放、查看定位合成。100ms/帧仅为预览速度。
- manifest.json：绑定、帧数、逻辑尺寸、色板、源图区域、叠加位置、循环提示、逐帧检查和文件SHA256。
- generation-log.json / generation-prompts.txt：26次生成的实际提示词与参考路径。
- validation.json：完整性、尺寸、透明、色板、对称及1×/大图一致性检查。

## 处理方法与限制

生成器未严格返回提示词中的超宽画布或叠加定位，因此不能直接把原稿当作可导入文件。动画表在低透明列谷处分帧、隔离相邻帧，按整张表统一比例取回指定格数；叠加层按给定坐标对生成的栅格图做尺寸、角度与位置校准。没有用代码新画箭、狼、圆环或光点。

逐格处理以alpha≥160排除软光晕，排除近黑边/底；格内前景覆盖至少20%才保留，再按许可色板中的多数颜色取回。此覆盖阈值用于保留细光线和小亮点，不是把全部背景透明像素参加颜色投票。随后统一alpha为0或255。按指定轴逐格镜像，印记及R中央漩涡保留不对称例外。治疗特效中央8×26格清空以给身体留位。

小型箭、光点和羽毛在固定游戏格数下有细节简化；少数淡出帧/小光点投票后以青蓝而非纯白表现亮部，亮芯抽样结果逐帧保留在manifest，不将颜色检查当作亮度全部通过。定位距离是锚点到非透明像素的距离，不证明整幅特效与人物完全贴合；12张定位合成预览用于人工复核。

## 已验证

26/26文件齐全；14张表合计74帧且无空白帧；12层尺寸与定位表一致；所有大图和1×图逐格一致；透明通道仅0/255；颜色限于每项允许色板；指定左右/上下对称逐格通过（按漩涡例外区排除）。

| 文件 | 帧数 | 单帧1×格数 | 大图px |
|---|---:|---|---|
| kindred_fx_a_arrow.png | 4 | 16 × 6 | 512 × 48 |
| kindred_fx_q_arrow.png | 4 | 18 × 7 | 576 × 56 |
| kindred_fx_e_arrow.png | 4 | 20 × 8 | 640 × 64 |
| kindred_fx_a_hit.png | 4 | 14 × 14 | 448 × 112 |
| kindred_fx_q_hit.png | 4 | 16 × 16 | 512 × 128 |
| kindred_fx_e_hit.png | 5 | 20 × 20 | 800 × 160 |
| kindred_fx_e_mark.png | 4 | 14 × 14 | 448 × 112 |
| kindred_fx_p_stack.png | 4 | 12 × 14 | 384 × 112 |
| kindred_fx_e_bite.png | 6 | 30 × 34 | 1440 × 272 |
| kindred_fx_w_bite.png | 5 | 20 × 20 | 800 × 160 |
| kindred_fx_q_dash.png | 5 | 26 × 10 | 1040 × 80 |
| kindred_fx_w_zone.png | 10 | 124 × 50 | 9920 × 400 |
| kindred_fx_r_zone.png | 9 | 104 × 44 | 7488 × 352 |
| kindred_fx_r_heal.png | 6 | 20 × 34 | 960 × 272 |
| kindred_bake_a_nock_2.png | 1 | 256 × 170 | 1536 × 1020 |
| kindred_bake_a_nock_3.png | 1 | 256 × 170 | 1536 × 1020 |
| kindred_bake_a_loose_4.png | 1 | 256 × 170 | 1536 × 1020 |
| kindred_bake_e_nock_2.png | 1 | 256 × 170 | 1536 × 1020 |
| kindred_bake_e_nock_3.png | 1 | 256 × 170 | 1536 × 1020 |
| kindred_bake_e_loose_4.png | 1 | 256 × 170 | 1536 × 1020 |
| kindred_bake_q_nock_5.png | 1 | 256 × 170 | 1536 × 1020 |
| kindred_bake_q_loose_6.png | 1 | 256 × 170 | 1536 × 1020 |
| kindred_bake_q_trail_3.png | 1 | 170 × 256 | 1020 × 1536 |
| kindred_bake_q_trail_4.png | 1 | 256 × 170 | 1536 × 1020 |
| kindred_bake_r_raise_5.png | 1 | 170 × 256 | 1020 × 1536 |
| kindred_bake_w_call_2.png | 1 | 170 × 256 | 1020 × 1536 |

## 叠加定位距离（格）

| 文件 | 到非透明像素的距离 |
|---|---|
| kindred_bake_a_nock_2.png | cyan=0.0, yellow=0.0 |
| kindred_bake_a_nock_3.png | cyan=0.0, yellow=0.0 |
| kindred_bake_a_loose_4.png | yellow=0.0 |
| kindred_bake_e_nock_2.png | cyan=0.0, yellow=0.0 |
| kindred_bake_e_nock_3.png | cyan=0.0, yellow=0.0 |
| kindred_bake_e_loose_4.png | yellow=0.0 |
| kindred_bake_q_nock_5.png | cyan=0.0, yellow=0.0 |
| kindred_bake_q_loose_6.png | yellow=1.0 |
| kindred_bake_q_trail_3.png | cyan=1.0 |
| kindred_bake_q_trail_4.png | cyan=0.0 |
| kindred_bake_r_raise_5.png | yellow=0.0 |
| kindred_bake_w_call_2.png | cyan=3.61 |

## 导入提示

绑定与over/under层序沿用输入fx_list.json，见manifest。W领域第3–8帧为维持循环，输入说明为510tick；R法阵第3–6帧为维持循环，输入说明为240tick。图像方向/对称按红色方不镜像的约束处理。

尚未把素材写入游戏图集、烘焙到运行时动作表、修改技能时序、编译/安装DLL或开展实战验证。应在项目导入后核对材质亮度、图层、触发点与范围；本交付不代表千珏运行时机制或前两轮模型问题已经全部验收。
