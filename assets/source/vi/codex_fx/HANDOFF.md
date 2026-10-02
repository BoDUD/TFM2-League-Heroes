# 蔚特效交付

15 张特效条，共 85 帧。根目录 PNG 是等宽切片、二值透明的整理版；generated/ 保留未改动的生图原稿；logical/ 是 1 倍像素版；preview/ 是深色背景预览。原始 LoL 参考贴图未包含在交付中。

## 提示词与帧数

| 文件 | 使用包内提示词 | 帧数 |
|---|---|---|
| `vi_fx_hit.png` | PROMPTS.md 第 1 条；完整实际请求见 generation_prompts.json | 4 |
| `vi_fx_w_proc.png` | PROMPTS.md 第 2 条；完整实际请求见 generation_prompts.json | 6 |
| `vi_fx_bs_on.png` | PROMPTS.md 第 3 条；完整实际请求见 generation_prompts.json | 10 |
| `vi_fx_q_charge.png` | PROMPTS.md 第 4 条；完整实际请求见 generation_prompts.json | 5 |
| `vi_fx_q_go.png` | PROMPTS.md 第 5 条；完整实际请求见 generation_prompts.json | 6 |
| `vi_fx_q_hit.png` | PROMPTS.md 第 6 条；完整实际请求见 generation_prompts.json | 4 |
| `vi_fx_q_stop.png` | PROMPTS.md 第 7 条；完整实际请求见 generation_prompts.json | 6 |
| `vi_fx_e_arm.png` | PROMPTS.md 第 8 条；完整实际请求见 generation_prompts.json | 5 |
| `vi_fx_e_cone.png` | PROMPTS.md 第 9 条；完整实际请求见 generation_prompts.json | 6 |
| `vi_fx_e_hit.png` | PROMPTS.md 第 10 条；完整实际请求见 generation_prompts.json | 4 |
| `vi_fx_r_cast.png` | PROMPTS.md 第 11 条；完整实际请求见 generation_prompts.json | 5 |
| `vi_fx_r_trail.png` | PROMPTS.md 第 12 条；完整实际请求见 generation_prompts.json | 6 |
| `vi_fx_r_side.png` | PROMPTS.md 第 13 条；完整实际请求见 generation_prompts.json | 4 |
| `vi_fx_r_hit.png` | PROMPTS.md 第 14 条；完整实际请求见 generation_prompts.json | 6 |
| `vi_fx_r_slam.png` | PROMPTS.md 第 15 条；完整实际请求见 generation_prompts.json | 8 |

## 整理与检查

所有整理版按指定尺寸输出，采用每格 1/8 尺寸硬像素整理后整数 8 倍导出；按各自提示词限制色板。透明度仅 0/255，没有不透明黑色。123 项文件、色板、网格和切片检查通过，结果见 validation.json。

护盾原稿泡面过密，整理版清空内部，仅保留外环和少量点纹；补生成请求遇到额度限制，未产生第二张原稿。E 冲击波按源图实际帧间位置重新切片，避免第一帧混入第二帧。缩小原稿时部分细小火花被舍去，原稿保留供导入者调整。

## 导入与时间

manifest.json 给出输出尺寸、逐帧 rect、源图 source_rect、建议游戏尺寸、league_vi_* 绑定名和归一化锚点。绑定名是交接配置，尚未导入游戏。Q/E 拳头位置仍需结合动作条测量；E 冲击波从左侧中点向右，R 拖尾右端接角色；面朝左时镜像。护盾和 R 起步以底部中心对齐脚。

预览统一使用 100ms/帧，仅供检查。Q 蓄力 5 帧可覆盖 0.5 秒；护盾导入时将第 4–8 帧循环补足 180 tick / 3 秒，再播放破裂；R 拖尾在冲锋期间循环。其余实际帧时长由技能导入配置确定。

## 亮度与限制

蔚每张图平均亮度的均值 159.82，最亮一成均值 250.94；现有凯南包对应值 178.17 / 251.62（0–255）。详情见 brightness_report.json 和 brightness_comparison.json。尘土、裂缝和衰减末帧会降低平均值；两组形状、色板和处理阶段不同，数值仅供亮度参考。每种特效都有至少一帧白色或青白亮芯。

已检查全帧接触图中的发射方向、能量柱、地面椭圆和护盾透明内侧。尚未进行游戏内叠加、实际技能时序和运行测试，最终位置和时序需在导入时检查。
