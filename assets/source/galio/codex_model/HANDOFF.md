# HANDOFF — 加里奥第 1 步模型图

交付时间：2026-10-13（Asia/Tokyo）。状态：三稿与原稿已保存，机械约束检查通过；有未完全达到的视觉约束，详见 SELF_CHECK.md，不能视为全部验收通过。

文件：
- galio-front.png：参考逐格保留，局部闭合石拳。
- galio-side-A.png：紧叠翼的右朝向侧身稿。
- galio-side-B.png：错开叠翼的右朝向侧身稿。
- raw/galio-front-generated.png
- raw/galio-side-A-generated.png
- raw/galio-side-B-generated.png
- generation-prompts.txt：实际成功调用的完整提示词、附件对应关系、逐格后处理说明。
- validation.json：尺寸、alpha、格子、调色板、正面差分、侧身头部和定位检查。
- SELF_CHECK.md：按“交回前请检查”逐项检查及未通过项。
- preview.png：灰底三稿对照预览；不是游戏透明资产。

技术结果：三个最终 PNG 均 1024×1536、12px 格、硬 alpha，右侧 4px 透明；拳头外正面差异为 0 格；侧身宽 65/69 格，翅尖行 14、头冠行 40、脚底行 115，使用相同原头且无新增颜色。

视觉限制：A 近侧拳头仍偏左中部；石拳四指节分离度有限；并非所有描边均 2 格/所有细节均 2×2。原参考逐格保留与统一收敛色阶/加粗轮廓存在冲突，本轮优先保留原参考。没有进行动作条、第 2 步打包、安装或游戏验收。

本文件在其他交付文件和自查结果保存后最后写入。
