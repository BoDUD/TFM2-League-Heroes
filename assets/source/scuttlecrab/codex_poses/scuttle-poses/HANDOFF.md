# 迅捷蟹 20 张动作姿势交付

使用本次包内 0_design.png 高清定稿，未使用上一轮 46×32 小图。所有姿势美术由内置 image_gen 逐张生成，结合定稿、脸部、该帧模型与骨架参考；没有用代码绘制身体或逐格拼造替代模型。

## 文件

- scuttle-pose-a_rise.png
- scuttle-pose-a_hop.png
- scuttle-pose-a_stomp.png
- scuttle-pose-q_raise.png
- scuttle-pose-q_call.png
- scuttle-pose-e_tuck.png
- scuttle-pose-e_shell.png
- scuttle-pose-e_pop.png
- scuttle-pose-r_up1.png
- scuttle-pose-r_up2.png
- scuttle-pose-r_up3.png
- scuttle-pose-run1.png
- scuttle-pose-run2.png
- scuttle-pose-run3.png
- scuttle-pose-run4.png
- scuttle-pose-run5.png
- scuttle-pose-run6.png
- scuttle-pose-run7.png
- scuttle-pose-run8.png
- scuttle-pose-d_down.png

- raw/<姿势>-original.png：原始生成文件，保留原样；请从这些图量实际像素格。
- raw/<姿势>-prompt.txt 与 generation-prompts.txt：实际使用的提示词。
- raw/earlier-attempts/：已替换的起身与死亡尝试，不用于导入。
- export-manifest.json：每张的整数平移量与地下裁切记录。
- qa.json：尺寸、透明度、基线、原稿/成品哈希和未验证项。
- preview.jpg：20 张缩略接触表，仅用于查看。
- run-preview.gif：8 帧跑步演示，80ms/帧，仅用于观察姿势变化。

## 导出与通过的检查

20 张均为 1254×1254 真透明 PNG，透明度只有 0 / 255，最低可见边界统一为 y=1100（右下边界不含，最下面一行可见像素 y=1099）。底部 154px 透明。r_up1、r_up2 的 y≥1100 地下部分已整齐裁去。

没有对姿势成品缩放、重新取样、变形或逐像素重画。导出只做整数像素平移、alpha 128 阈值转为硬透明，以及上述两帧地下裁切；其余 RGB 像素不变。原始生成稿原样保存在 raw/。起身原稿过高的版本已用新的 image_gen 原稿替换，未缩小旧图来塞画布。

8 张跑步图均为不同图像，接触表检查可见腿部位置变化。缩壳帧只剩甲壳；死亡帧已重画为甲壳和两根瘫下的触角，没有脸、眼睛、腿和钳子。两张地下冒出帧、站立帧、缩壳帧、举触角帧均分别生成。

## 精度边界，导入时须保留

图像生成稿的“每格8px”和“同一张脸逐格复制”是生成目标，不能由生成模型保证严格成立。本交付没有通过重新采样伪装成严格8px格，也没有把脸部跨帧逐像素一致性、甲壳尺寸完全恒定或骨架坐标完全一致标成检查通过。实际原稿仍有局部阶梯尺寸、脸部细节和跨帧比例差异；应按 raw/ 实际格子读取，并在引擎拼帧时复核这些差异。qa.json 中两项 exact_8px_grid_verified / face_pixel_identity_verified 均如实为 false。

本次完成动作美术源稿和定位导出，不包含游戏骨架绑定、自动插帧、动画数据、碰撞盒、PPU、DLL 或实机测试。原包中给其他代理的工程导入说明仅作上下文参考，未操作其中的工程目录。
