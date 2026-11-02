# 苍蓝哨戒 · 动作姿态交付

## 交付内容

15 张独立 PNG：普攻 a_rise/a_fire；技能 q_open/q_beam1/q_beam2、e_split/e_close、r_open/r_blast；飘移 run1–run4；死亡 d_split/d_down。文件名均为 sentry-pose-<名称>.png。

另含 raw/ 原始生成图（含未选用与修订前版本）、generation-prompts.txt、revision-prompts.json、pose-checks.json、approved-design-reference.png、pose-overview.png。

## 制作与检查

所有姿态均由内置 image_gen 逐张绘制。分裂、张开及倒地四张又通过 image_gen 修正了内侧白色旋转断边。没有使用代码逐格绘制角色，也没有缩放或重采样姿态。最终 PNG 只将 alpha 规范化为 0/255，RGB 和空间像素与所选 raw 一致。15 张画布全部为 1254×1254；无背景、地面、文字、激光或碎石特效。分开处透明，死亡蓝核变暗并最终熄灭。

## 导入边界

生图的边缘并非严格统一的 12px 方格，石块大小、切面与布局参考也有少量差异；没有为了凑 12px 网格而重新取样。此包完成的是姿态原稿制作，不应视为逐格和逐部件尺寸均已完全通过的最终游戏帧。按源包原定导入流程，先测 raw 的实际格子，再分别对齐定稿的左右石块尺寸、核位置和地面。pose-checks.json 同时记录实际包围盒和目标布局包围盒，strict_12px_grid_guaranteed=false 明确保留这一限制。

raw 中同名文件是最终选用原图；带 attempt1 / before-edge-fix 的是保留的历史版本，不用于最终导入。总览只是预览，不用于读格。未修改游戏或模组文件。
