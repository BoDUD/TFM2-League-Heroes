# 索姆动作素材交付

15 张动作图已绘制并整理，使用原生 image_gen；以输入包内定稿和各姿势渲染/骨架为参考。画面由生图模型绘制，处理程序只取格子颜色、清理 alpha 并对齐底线，没有用代码画龙。

## 文件

- `sohm-pose-a_rear.png`
- `sohm-pose-a_spit.png`
- `sohm-pose-q_rise.png`
- `sohm-pose-q_send.png`
- `sohm-pose-e_gather.png`
- `sohm-pose-e_push.png`
- `sohm-pose-r_coil.png`
- `sohm-pose-r_rise.png`
- `sohm-pose-r_swirl.png`
- `sohm-pose-d_fall.png`
- `sohm-pose-d_down.png`
- `sohm-pose-run1.png`
- `sohm-pose-run2.png`
- `sohm-pose-run3.png`
- `sohm-pose-run4.png`

- `raw/`：最终选用的原始生成图，保持原样。
- `raw/iterations/`：重画前的版本，仅留作过程记录，不应导入。
- `contact-sheet.png`：逐姿势裁切后等框放大的总览，用于看造型；此图不能用来判断原始身体比例。
- `run-review.gif`：四张游动帧，按 1-2-3-4-3-2 顺序预览。
- `reference/`：输入包中的定稿与头部参考。
- `generation-prompts.txt`：最终选用图的实际提示词及参考图路径。
- `manifest.json`：每张图的尺寸、网格、实际边界和垂直平移值。
- `validation.json`：两包的文件技术检查结果。

## 处理与校验

最终 PNG 均为 1254×1254、RGBA；透明度只有 0/255；左上角对齐 8px 网格；最后 6px 的非完整网格边缘留空。可见像素底边统一对齐 y=1176。采用 8px 方格的多数颜色取回，没有按每个姿势的外接框缩小身体。raw/ 中仍保留原始位置和原始 alpha。

## 导入说明与边界

这是动作图片素材交付，没有修改游戏、动作表或 DLL，也没有声称完成游戏内验证。每个动作单独生成，头部像素、鬃毛、身体粗细和骨架位置存在重绘差异，不能声称已逐像素复用同一个头或严格绑定输入骨架。特别是大招回旋、死亡姿势和游动四帧，导入时仍应按定稿头部与同一身体尺度复核。技术检查通过不等于动作契约和游戏内验收通过。
