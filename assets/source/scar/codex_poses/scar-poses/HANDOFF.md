# 刀疤动作姿势交付

22 张关键姿势已完成：12 张攻击/技能姿势、8 张走路、2 张死亡。全部角色图由内置 image_gen 生成；原始素材包内的 B 造型为本轮唯一造型依据。

## 文件

- scar-pose-*.png：22 张 1254×1254 RGBA 成品，每个逻辑像素严格为 12×12，网格从左上角起。
- pixel_1x/：对应 105×105 的逻辑网格图；因为 1254 除以 12 余 6，最末行列透明，成品最后 6 像素透明。
- approved-head-1x.png：包内定稿头部读回的 27×29 逻辑像素；20 张非死亡姿势均复制其不透明像素，保持眼窝、白瞳孔、牙齿、红耳及尖发一致。透明角落保留后方手臂和长矛，不把它们抹掉。
- raw/：22 张最终采用的生成原图，未修改。raw/iterations/ 是被替换的尝试，留作追溯，不导入游戏。
- generation-prompts.txt、correction-prompts*.txt、rework-prompts.txt：实际提示词及重画要求。
- manifest.json：每张的尺寸、放置位置、头部位置、源文件和 SHA-256。
- validation.json：本次交付的机械校验记录。
- preview-1.png 至 preview-3.png：全部姿势预览；walk-preview.gif：走路循环预览，133ms/帧，仅供审阅。

## 处理与校验

角色绘制由图像生成完成。脚本只做源图调色板取样、硬透明、缩放、按格对齐与定稿头部复制。走路帧以同一头部横坐标、固定脚底和 ±1 格的头部起伏做源行重采样，保留各帧原始腿部姿势；未使用代码绘制替代身体或腿。

普通姿势最低点 y=1176；surf / surf_hit 的滑板最低点 y=1140，离地 3 格。所有成品 alpha 仅 0/255；完整 12×12 块内颜色一致；不透明像素与左、上、右画布边缘留有至少一格余量。20 张定稿头部的不透明像素与模板逐像素一致。

走路已重画为单只绷带手持矛，矛尖朝下；起跳不带滑板；q_wind 不带炸弹并修正双手分工；q_throw 的矛尖已改为向右下倾斜；d_down 为头左脚右的仰面平躺。两张滑板帧以外没有滑板；特效独立在另一个交付包。

这是关键姿势素材包；与骨架参考的轮廓位置为生成近似，未宣称是骨骼的逐点描摹。此包不包含引擎动画表、补间帧或游戏内运行验证；导入时仍需按现有动作时长组帧。

## 姿势清单

- scar-pose-a_wind.png
- scar-pose-a_thrust.png
- scar-pose-a_back.png
- scar-pose-surf.png
- scar-pose-surf_hit.png
- scar-pose-q_wind.png
- scar-pose-q_throw.png
- scar-pose-q_hold.png
- scar-pose-e_wind.png
- scar-pose-e_sweep.png
- scar-pose-r_jump.png
- scar-pose-r_land.png
- scar-pose-run1.png
- scar-pose-run2.png
- scar-pose-run3.png
- scar-pose-run4.png
- scar-pose-run5.png
- scar-pose-run6.png
- scar-pose-run7.png
- scar-pose-run8.png
- scar-pose-d_fall.png
- scar-pose-d_down.png
