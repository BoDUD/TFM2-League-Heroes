# B 包：背包机械臂与大招装置交接

## 交付状态

20张道具原画已用内置image_gen逐张生成，包含17张机械臂和3张R装置。尺寸检查20/20为1254×1254，主目录PNG与raw/逐字节一致，各文件SHA256不同。主目录最终稿目视检查只有道具，没有人物、灰色定位小人、网格或文字。

**严格像素验收未通过，仍是待整理原画。** 所有图都有透明像素，但alpha均包含0/255之外的值；全部未通过严格12px原点网格检查。位置、长度、关节尺寸和颜色未达到逐格统一。不能直接把整套宣称为可无缝接入的同一机械臂动画。

## 文件清单

主目录20张PNG：

- crane_peek、crane_peek2、crane_up、crane_up_empty、crane_up_back、crane_up_high
- crane_place、crane_lift、crane_return、crane_fold
- crane_cock、crane_throw、crane_recoil、crane_aim、crane_fire、crane_recover、crane_aim_empty
- gear_drum、gear_burst、gear_settle

文件名前缀均为heimerdinger-prop-，扩展名.png。另附raw/原图、generation-prompts.txt、image-qa.json和preview.png整画布总览。preview只作检查缩略图，没有改写任何交付原画。

rejected/隔离未选稿：crane-up-extra-R-base.png误带R底座；四张unwanted-rocket稿对应lift/return/fold/throw，错误多画了火箭；peek、peek2和place的pose-or-margin-drift稿分别因折叠不足或贴近边缘重画。不要把rejected当成动画候选。

## 目视检查

最终持弹图：peek、peek2、up、up_back、up_high、place、cock、aim均有火箭。最终空爪图：up_empty、lift、return、fold、throw、recoil、fire、recover、aim_empty均没有火箭，红爪空隙可见。炮弹、火光、烟雾、电光等效果未另行生成。

高举首稿误把R装置和机械臂合并，已重画去掉底座。对空爪图同时提供含火箭的游戏帧，会使模型复制多余火箭；已用引导图与空爪样式参考重画相关帧。peek/peek2因照搬高举姿势重画，place因右侧火箭过近边缘重画；最终下放稿火箭朝下且整体在画布内。

R三张分别为单独圆鼓、弹簧高展开、弹簧较低回弹。burst/settle画了前方红边圆弧，后方圆弧留空；没有画人物。但drum与展开/回弹中的鼓形状不完全一致，仍需统一尺寸和造型。

## 尚需修正

整套机械臂根部和关节的绝对坐标、粗细和像素节距仍有漂移，部分图被自动放大并居中，未精确照引导图。up/back/high之间差异偏小。peek最终稿火箭与夹爪连接偏弱，peek2的火箭与手爪连接和方向需按游戏参考复核。火箭长度、关节螺栓数量、臂段长度和配色仍非逐格统一，不能直接做连续动画而不整理。

接入前需统一成一套部件、调色板和实际网格，把各图对回guide并对齐机械臂根，修正夹持关系；机械臂放人物后层，R装置放前层。没有修改pack_heimerdinger_poses.py、rig_heimerdinger.py或游戏资产，也未运行游戏内验收。源包“Claude收到后”是后续背景说明。

## 本轮经验

机械臂与R装置的描述必须分开。空爪状态不应同时给含火箭的正面描述和游戏图，否则容易出现“空爪旁边仍有火箭”。图像参考会强烈锁定已有高举姿势，姿势引导必须优先，且要逐张检查折叠与根部坐标。结构正确、文件齐全、真实透明通道都不能替代严格网格及动画一致性验收。
