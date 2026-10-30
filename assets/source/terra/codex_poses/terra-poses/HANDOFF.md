# 泰拉动作稿交付

已生成18张独立动作稿，使用内置 image_gen。每张使用包内定稿、头部、对应模型渲染、对应骨架和定稿骨架作为参考。没有用代码绘制角色，也没有执行附件中交给 Claude 的游戏导入操作。

## 验收状态

完成的是18张生成稿及完整原始记录；严格动作美术验收尚未通过。

- 18张均为1254×1254 RGBA。
- 交付层仅将原稿alpha以128为阈值二值化，alpha只有0或255。RGB、像素坐标、图像大小保持不变；没有缩放、网格重采样或移动角色。
- raw/中的18张原始生成PNG逐字节保留，哈希已与生成器原文件核对。
- **严格9px网格：0/18通过。脚底下边界严格y=1176：0/18通过。** 实际包围盒与底线见manifest.json和qa.json。没有通过缩放或重新取样来掩盖偏差。
- 头部没有做到逐格复制定稿，跨帧头、躯干和腿的尺度仍有变化；移动六帧不是锁定同一躯干的确定性变形；d_fall的侧倒程度不够。部分展翼与骨架角度、尾巴姿势也有近似。
- 因此这些文件应作为后续读raw和精修的动作来源，不能当作已验证可直接导入游戏的统一动画帧。没有做游戏内验证。

## 18张动作文件

- `terra-pose-a_wind.png`
- `terra-pose-a_hit.png`
- `terra-pose-q_crouch.png`
- `terra-pose-q_pounce.png`
- `terra-pose-q_bite.png`
- `terra-pose-e_spread.png`
- `terra-pose-e_roar.png`
- `terra-pose-r_rear.png`
- `terra-pose-r_stomp.png`
- `terra-pose-r_roar.png`
- `terra-pose-run1.png`
- `terra-pose-run2.png`
- `terra-pose-run3.png`
- `terra-pose-run4.png`
- `terra-pose-run5.png`
- `terra-pose-run6.png`
- `terra-pose-d_fall.png`
- `terra-pose-d_down.png`

## 其他文件

- raw/：上述18张原始生图，未经处理。
- generation-prompts.txt：实际逐张提示词和参考图路径。
- manifest.json：画布、实际包围盒、原始alpha、交付alpha、网格检查和导出方式。
- qa.json：逐张技术校验结果。
- preview.jpg：18张便览。这里只为查看而按各自主体缩放；不能用便览图量身体比例或像素网格。最终PNG和raw没有缩放。

下一步严格制作需要以包内定稿头部和实际骨架逐帧修正，或使用能锁定像素网格与部件的制作流程。本轮没有通过代码拼块替代绘画。
