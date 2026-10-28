# 石甲虫姿态源图交付
日期：2026-10-28

本轮按 krug_pose_pack.zip 的定稿与姿态参考，使用内置 image_gen 绘制 15 张独立姿态源图；防御帧另做一次修订，共 16 次生成。全部原始输出保留。没有用 Python 逐格绘制、替换模型或修整生成图；Python 仅复制文件、读取图像数据与生成检查报告。

## 交付文件
| 文件 | 内容 | 对应未修改原始输出 |
|---|---|---|
| krug-pose-a_rear.png | 普攻起手 | raw/exec-a2569ae9-363c-4987-af1b-3e22aed7b31a.png |
| krug-pose-a_slam.png | 岩拳砸地 | raw/exec-f4b1851c-1a37-4066-9f2e-38a211f230b1.png |
| krug-pose-a_back.png | 收势 | raw/exec-9b403a6d-acbe-4ec4-ab14-77fbcaa24eed.png |
| krug-pose-q_ball.png | 缩成石球 | raw/exec-d752e09c-b36c-4d0f-b397-e9b15631c46a.png |
| krug-pose-q_unfold.png | 石球展开 | raw/exec-27bfa116-022c-4e84-bef4-3843d143a47c.png |
| krug-pose-q_ram.png | 前冲撞击 | raw/exec-bfa52014-45a8-4ddc-985e-e98123a39961.png |
| krug-pose-e_shell.png | 坚岩外壳（修订版） | raw/exec-fe8dc891-eace-4313-9c46-4b452223c416.png |
| krug-pose-r_crouch.png | 起跳蓄力 | raw/exec-2c306c14-970d-4be7-93e3-830dbfa72e6e.png |
| krug-pose-run1.png | 奔跑 1 | raw/exec-62be378f-fd8f-4f89-bf44-af384f2bd9cf.png |
| krug-pose-run2.png | 奔跑 2 | raw/exec-ba4593ca-710b-4a49-b3b9-0afaecf951e1.png |
| krug-pose-run3.png | 奔跑 3 | raw/exec-9f5019ab-4bcd-46f3-aa5f-1097bd0a88b2.png |
| krug-pose-run4.png | 奔跑 4 | raw/exec-4cdb661d-7db1-4417-8f2f-6f936a863281.png |
| krug-pose-d_sink.png | 死亡下沉 | raw/exec-bbd1b98b-a0b1-4225-9797-0ab011feb4b3.png |
| krug-pose-d_crack.png | 背壳碎裂 | raw/exec-085fd05c-b831-4158-98c2-21af7d6a484c.png |
| krug-pose-d_down.png | 倒地残骸 | raw/exec-6433de73-782a-4de6-b0d6-cac974c7a1d7.png |

附带：
- raw/：16 张原始生成 PNG，包含未采用的第一次 e_shell。
- generation-prompts.txt：每次实际提示词和输入参考文件清单；末尾单列 e_shell 修订提示词。
- validation.json：每张图的尺寸、alpha、边界、12 px 网格检查和 SHA256。
- VALIDATION.md：便于查看的检查表。
- HANDOFF.md：本说明。

## 已做的视觉检查
逐张看过生成结果：普攻有立起、落拳、恢复变化；滚动有缩球、展开、前冲变化；四张奔跑有四肢位置和背部高低差异；死亡有下沉、裂开、残骸变化。全组沿用砂岩背壳、橙金裂缝、紫褐色身体、硬壳脸和弯钳的外观。
第一次 e_shell 背壳偏高、露脸较多，因此重画，最终采用修订版；第一次输出仅保留在 raw/。
这些是视觉源图检查，并未证明已经构成游戏中无跳动的动画。

## 规格检查结果：仍需校正
- 文件齐全：15/15 姿态，16 张原始输出。
- 画布：15/15 为 1254×1254 RGBA。
- 真实透明背景存在；但 15/15 含半透明像素，全硬 alpha 要求未通过。
- 严格从画布原点对齐的 12×12 像素格：15/15 未通过，不能按固定 12 px 直接无损逐格读取。
- 最低可见点（alpha≥128）各帧不同，详见 VALIDATION.md，未统一在 y=1176。
- 头部保留同类设计，但不是 1_head.png 的逐格复制；头大小、脸向、钳子形状与部件尺度仍有生成差异，需要逐帧对齐。
- 姿态是对参考与骨架的生成近似，未通过骨骼坐标逐点匹配；部分动作力度与遮挡关系仍需最终像素整理。
- 没有缩放或硬化 alpha 来掩盖这些未通过项。所交 PNG 与各自 raw 图逐字节相同。

## 后续使用范围
本包可作为逐帧像素整理和动画拼接的源素材，不能直接称为最终可入游戏的动画资源。需要以包内 0_design.png 与 1_head.png 为统一基准，校正像素密度、脸部、石臂厚度、背壳体积、锚点与透明边缘，再接入动画并验证实际循环、攻击节奏及死亡过渡。
本轮未执行参考文档中写给其他代理的入库、缩图或游戏部署操作；未更改仓库、已安装模组、动作表或游戏设置，也没有进行游戏内验收。

