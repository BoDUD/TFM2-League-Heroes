# 超级机甲：18 张动作姿势原图

状态：18 个姿势均已通过 image_gen 绘制；原图文件交齐。严格像素/动画验收未通过，不能称为可直接入游戏的合格动画。

## 本轮范围与制作方式

按 mightymech_pose_pack.zip 的定稿、头部和逐姿势骨架制作：8 张战斗动作、8 张跑步、2 张死亡。只使用新包里的造型作为共同参考。使用内置 image_gen，逐姿势单独生成，共 18 次初稿和 3 次定向重绘。未用代码绘制身体、复制肢体、缩放、重采样、调色、裁切或修改 alpha。Python 只读取图片、计算检测数据；所有交付 PNG 均为生成模型原始字节。

## 文件清单

- mightymech-pose-a_up.png：双手举剑起手。
- mightymech-pose-a_down.png：向右下方重斩。
- mightymech-pose-q_brace.png：展开刃翼防御，补画双手按持的竖剑。
- mightymech-pose-e_crouch.png：低姿蓄力、刃翼竖起。
- mightymech-pose-e_air.png：空中抬腿，补画巨剑。
- mightymech-pose-e_land.png：低姿落地、双手握剑向右下。
- mightymech-pose-r_flare.png：站起展开刃翼、剑尖朝下。
- mightymech-pose-r_slash.png：巨剑向右横扫。
- mightymech-pose-run1.png 至 mightymech-pose-run8.png：8 张独立跑步姿势图。
- mightymech-pose-d_fall.png：失衡、碎甲、剑脱手。
- mightymech-pose-d_down.png：低头跪倒，眼罩和肩灯暗灰，剑在身旁。
- raw/：上述 18 张最终选图的逐字节副本。
- raw/earlier-attempts/：run2、run4、e_land 的初稿，仅作溯源，不替代主文件。
- generation-prompts.txt：18 张初始提示词。
- generation-prompts-run-continuity.txt：run2–run8 的连续性提示词，实际用 run1 作第 5 张参考。
- generation-prompts-leg-corrections.txt：run5–run8 的实际完整提示词，增加腿部要求。
- generation-prompts-revisions.txt：run2、run4、e_land 定向重绘的实际提示词。
- validation.json：逐图尺寸、alpha、非透明包围盒、严格 9px 网格检查、SHA-256、raw 字节一致性。
- review.html：18 张总览；浏览器显示尺寸变化不会修改源文件。

## 已核对

- 恰好 18 个不同姿势文件，每张都是 1254×1254 RGBA PNG。
- 每张都有真实 alpha 透明背景，不是画出的棋盘格或灰底。
- 主文件与 raw/ 对应最终原图逐字节一致。
- 逐张看过生成结果：保留红银黑机器人、头角和眼罩、肩甲、背部刃翼、尾巴和巨剑；没有参考骨架线或地面网格。
- e_land 初稿单手握剑且剑向近竖直，已用模型重绘为双手握剑、剑尖向右下。
- run2 和 run4 已重绘一次；重绘稿提高了抬膝/低脚姿势的区分，但左右腿仍未准确对应骨架。
- d_down 的眼罩和肩灯已熄灭，剑核也呈非发光状态。

## 明确未通过项

1. **硬 alpha 未通过**：18 张均有半透明像素，包括角色内部和轮廓。透明通道存在，但不是仅 0/255。具体数量见 validation.json。为保留原图，本轮没有阈值化处理。
2. **严格 9px 网格未通过**：18 张均不是从画布原点对齐的整齐 9×9 纯色方块；未再缩图或采样。
3. **骨架位置、尺度未严格锁定**：生成器重新安排了部分构图，头、剑、躯干的大小和坐标仍有变化；身体最低点并未都停在 y=1176。不同姿势的包围盒不能用于直接推断身体缩放。
4. **头部不是逐格复制**：红盔、银角、面甲、黄眼的识别特征保留，但不能称为同一个 FACE_BOX 在所有帧的无变化复用。
5. **跑步不是已验收的八帧循环**：能看到两侧腿抬落，但 run2/run4 等仍有支撑腿和骨架不对应、重复步态、脚底漂移，逐帧上半身也有变化。不能声称原始帧已经无抖动或正确循环。
6. **部分动作方向近似**：e_crouch 的剑朝前，未准确拖在骨架指定的一侧；e_air 并未双腿完全收紧；r_slash 的躯干前倾和剑的最远伸展仍属近似。e_land 低姿仍需核对单膝落地的关节位置。近远肢体的遮挡和明暗也没有逐关节通过验收。

这些文件适合作为后续读格、对齐和精修的绘画源。交齐原图不等于全部符合严格规格。没有修改 TFM2 项目、打包动作表、制作完整骨骼模型、运行游戏或执行附件中给其他代理的仓库接入指令。
