# 呲呲动作姿势交付

## 内容

22 张姿势图：12 张技能/普攻动作、8 张跑步、2 张死亡。所有美术由内置 image_gen 根据本次压缩包的定稿、头部、姿势参考与骨架生成，没有用脚本逐格绘制身体，没有用旧造型替换本次定稿。

## 通过的技术检查

- 22 张交付 PNG 均为 1254×1254 RGBA，alpha 只有 0 和 255。
- 不缩放、不重新取样、不拉伸、不压扁；没有用代码拼接头、腿或羽毛。
- 交付版仅把 alpha 按 128 阈值转为硬透明，并作整数像素 Y 平移，使有效像素下边界为 y=1176（最后一个不透明行 y=1175）。没有裁掉角色有效像素。
- `raw/` 保留生成返回的原始 PNG 字节；前后翻转、落地和 run8 的首稿也保留为 `*-first.png`。
- 骨架线、地面线、网格与文字不作为游戏素材交付。

## 必须说明的美术限制

这是一套已生成、整理并检查的姿势美术素材，尚未达到“头逐像素相同、躯干逐帧固定、每格严格 10 px”的完整动画验收要求。image_gen 没有严格锁定网格和头部像素：部分轮廓块宽不一致，头/羽毛/身体在各帧之间有重绘差异，跑步各帧也有躯干角度、比例和轮廓变化。不能把 `run-preview.gif` 当作已经完成固定躯干与骨骼配准的最终循环动画。

已针对 q_flip 的后仰翻转、q_kick 的头下双脚上踢及张嘴、q_land/run8 的闭嘴返修。q_kick、r_open 张嘴；d_down 闭眼。颜色与主要识别部件尽量保持本包定稿，但不能宣称每个头都逐格等同 `1_head.png`。

`manifest.json` 逐张记录平移量、原稿路径、尺寸及哈希；`validation.json` 明确区分通过项目与未通过的严格一致性项目。后续需要按 raw 的实际格子读取、对齐定稿头部并统一身体尺度；该步骤没有在此包中伪装为完成。

## 文件

- `zippy-pose-a_wind.png`
- `zippy-pose-a_kick.png`
- `zippy-pose-q_crouch.png`
- `zippy-pose-q_flip.png`
- `zippy-pose-q_kick.png`
- `zippy-pose-q_land.png`
- `zippy-pose-e_curl.png`
- `zippy-pose-e_ball.png`
- `zippy-pose-r_crouch.png`
- `zippy-pose-r_spring.png`
- `zippy-pose-r_open.png`
- `zippy-pose-r_land.png`
- `zippy-pose-run1.png`
- `zippy-pose-run2.png`
- `zippy-pose-run3.png`
- `zippy-pose-run4.png`
- `zippy-pose-run5.png`
- `zippy-pose-run6.png`
- `zippy-pose-run7.png`
- `zippy-pose-run8.png`
- `zippy-pose-d_fall.png`
- `zippy-pose-d_down.png`

- `raw/`：22 个选中原稿及 4 个返修前首稿，原始尺寸与 alpha 均未改动。
- `generation-prompts.txt`：选中版本的实际提示词及每次参考图路径。
- `initial-generation-prompts.json`：初轮提示词及参考图清单，供首稿溯源。
- `manifest.json`、`validation.json`、`raw-inventory.json`：资产与技术检查记录。
- `poses-preview.jpg`：22 张总览；仅预览进行了缩小。
- `run-preview.gif`：8 帧检查预览，每帧 120 ms，仅用于观察；不是指定游戏时序。

## 范围

本次只制作图像；文档中给 Claude 的导入、游戏代码及骨架包重建步骤作为上下文，未修改仓库或游戏。未执行外部文档中对其他代理的操作指令。
