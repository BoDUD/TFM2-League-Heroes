# 艾达丝动作姿势交接

状态：11 个姿势均已用 image_gen 生成候选原画；严格像素规格尚未通过。没有使用脚本绘制角色或改动生成图片。

文件：
- `idas-pose-a_wind.png`
- `idas-pose-a_claw.png`
- `idas-pose-q_rear.png`
- `idas-pose-q_breath.png`
- `idas-pose-e_open.png`
- `idas-pose-e_roar.png`
- `idas-pose-r_wrap.png`
- `idas-pose-r_hold.png`
- `idas-pose-r_burst.png`
- `idas-pose-d_fall.png`
- `idas-pose-d_down.png`

原始生成结果在 `raw/`，实际提示词在 `generation-prompts.txt` 和各帧 `*-prompt.json`。a_claw 正式文件采用 v2，第一版多余髋部手爪已由画图模型移除；a_wind 首版也因多余手臂被替换。

## 验证结果与限制

11 张均为 1254×1254 RGBA，背景有真实透明区域。但逐文件读取发现所有帧都有大量半透明像素；从画布原点检查 7×7 格块也没有通过常量像素测试。详细数值见 `validation.json`。脚底和主体大小没有严格服从参考位置，不能按提示词中的 y1176 或 7px 直接读格。

目视可区分起手、扑击、仰头蓄力、张嘴龙息、振翅、吼叫、收翼、保持、展开、后仰和倒地。部分头部/鬃冠轮廓和金翼大小仍相对定稿发生变化，无法认定头部逐格一致；蓄力、后仰的闭嘴形状也需进一步校对。生成图保留作为姿势候选，不声称符合游戏帧标准。

需要后续完成真正7px像素格、硬Alpha、定稿头部统一和画布定位，再做游戏接入。当前没有生成技能特效或修改游戏。

## 中断原因

11 姿势生成后，开始 run1 时图像服务返回 HTTP429 `usage_limit_reached`。服务给出的恢复时间是 2026-10-30 12:45:13（Asia/Tokyo）。受此限制，无法再用图像模型修正上述技术问题或继续走路帧。没有切换模型或调用付费API。

