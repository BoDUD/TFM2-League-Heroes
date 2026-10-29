# 塞薇卡动作姿势交付

已交付 23 张独立动作图：13 个攻击/技能姿势、8 个跑步姿势、2 个死亡姿势。

正式文件 `sevika-pose-<名称>.png` 均为 1254×1254 RGBA、12px 网格、硬透明，最低可见像素底边 y=1176。`pixel_1x/` 是 104×104 的逻辑像素图，右侧与底部不足一格的 6px 保持透明。跑步八帧统一到 76 格可见高度，避免首帧突然放大；非正方形的源稿等比装入画布，未拉伸身体。`raw/` 保存最终选用的生图原稿，未经处理；生成尺寸与包围盒请见 manifest。

`preview-*.png` 为分组预览；attack / flame / extendo / chomp / run / death-review.gif 为动作检查动画，预览速度不等同于游戏最终帧时长。`reference/` 保存本次使用的定稿和头部参考。生成使用内置 image_gen，未用代码画替代人物；整理仅涉及格子取色、硬透明和垂直基线定位。

钳击、喷火后坐力、伸缩拳蓄力和出手经过重画。伸缩拳出手只保留手腕接口，飞出的拳头和弹簧由独立特效承担。人物与特效没有合并进同一动作帧。

已检查：文件齐全、尺寸、硬透明、12px 方格与脚底基线；逐张查看了源图与分组预览。图像生成存在局部脸部像素与骨架投影偏差，不能将这些原画宣称为逐像素复制官方骨骼动画。后续导入仍应按实际 idle 头部位置和 PPU 检查身体密度、帧间尺度、跑步循环和游戏显示。

本次交付范围为这套素材包，不包含游戏内动作表、技能绑定或运行验收，也未修改现有游戏/模组文件。

## 文件清单
- `sevika-pose-a_wind.png`
- `sevika-pose-a_punch.png`
- `sevika-pose-a2_raise.png`
- `sevika-pose-a2_clamp.png`
- `sevika-pose-q_flame.png`
- `sevika-pose-q_flame2.png`
- `sevika-pose-e_wind.png`
- `sevika-pose-e_punch.png`
- `sevika-pose-e_back.png`
- `sevika-pose-r_dash.png`
- `sevika-pose-r_raise.png`
- `sevika-pose-r_bite.png`
- `sevika-pose-r_lift.png`
- `sevika-pose-run1.png`
- `sevika-pose-run2.png`
- `sevika-pose-run3.png`
- `sevika-pose-run4.png`
- `sevika-pose-run5.png`
- `sevika-pose-run6.png`
- `sevika-pose-run7.png`
- `sevika-pose-run8.png`
- `sevika-pose-d_fall.png`
- `sevika-pose-d_down.png`
