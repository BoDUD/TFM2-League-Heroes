# 弗拉基米尔特效交付说明

完成本包第 3 步的 **19 张生图原稿，共 88 帧**。采用清单明确允许的原稿交付方式，由导入端转换为游戏原尺寸条。全部视觉均由内置 imagegen 生成；没有用代码拼血丝、血环、血云或方块形状。共 22 次生图，选用 19 张；E 命中、W 吸血、R 标记各修订一次。

## 包内容

根目录：19 张对应文件名的 RGBA PNG。`manifest.json`：每张图的绑定、目标大小、实际尺寸、提示词编号和 `assets[].frames[].rect = [x,y,宽,高]`。`prompts/01.txt`–`19.txt`：实际使用的完整提示词。`reference/`：用户提供的清单、规格和定稿造型。`previews/`：19 个单项 GIF、总览 GIF、静态总览。`validation.json`：透明度、亮度、颜色数量和结构检查结果。

## 检查结果与原稿限制

清单 19 个文件名全部对应；88 帧全部非空；切帧矩形在图内并覆盖源条；单项 GIF 帧数一致；全部 PNG 都有真正透明的 RGBA 通道；交付 PNG 与生图原件 SHA-256 一致。预览只做裁切、缩放和暗底展示，资产 PNG 保持原像素。

**原稿未达到严格的游戏像素规范**：实际尺寸与要求尺寸不同，像素块不在统一原生网格上；色彩不是精确限色，边缘含半透明像素和少量杂点；左右/上下是近似对称，循环尚未进行游戏内无缝验证。部分条的帧间间距不均，因此必须用 manifest 的实际 rect 切分。这些检查没有标成通过。

按 alpha ≥128 的可见像素测量，19 张图平均亮度最低为 56.42/255，最亮一成的平均亮度最低为 184.73/255；逐张数值见 validation。原包没有其他英雄的成品特效，无法做同口径横向比较。

## 逐张对应

| 文件 | 原规格提示词 | 帧数 | 检查备注 |
|---|---:|---:|---|
| `vladimir_fx_a_bolt.png` | 第 1 条 / `prompts/01.txt` | 3 | 右向弹头与短尾迹完成；上下仅近似对称。 |
| `vladimir_fx_a_hit.png` | 第 2 条 / `prompts/02.txt` | 4 | 闪光→血花→散点→残留完成；散点未逐像素镜像。 |
| `vladimir_fx_q_drain.png` | 第 3 条 / `prompts/03.txt` | 5 | 胸口闪光、抽血丝、血结、消散完成；旋转与对称为近似。 |
| `vladimir_fx_q_orb.png` | 第 4 条 / `prompts/04.txt` | 4 | 右向白芯血球完成；四分之一圈旋转为近似。 |
| `vladimir_fx_q_rush.png` | 第 5 条 / `prompts/05.txt` | 4 | 大白芯、长尾迹完成；绕球血丝数量和旋转为近似。 |
| `vladimir_fx_q_heal.png` | 第 6 条 / `prompts/06.txt` | 5 | 回血竖环与上升光点完成；边缘有半透明杂点。 |
| `vladimir_fx_q_ready.png` | 第 7 条 / `prompts/07.txt` | 4 | 脚下光环与血泡完成；部分血泡升得较高。 |
| `vladimir_fx_e_charge.png` | 第 8 条 / `prompts/08.txt` | 4 | 血球罩中心留空完成；边缘血带偏厚，导入时需看遮挡。 |
| `vladimir_fx_e_burst.png` | 第 9 条 / `prompts/09.txt` | 5 | 地面扩散血环完成；原稿椭圆偏扁，需按目标比例调整。 |
| `vladimir_fx_e_bolt.png` | 第 10 条 / `prompts/10.txt` | 3 | 右向月牙弹头完成；上下仅近似对称。 |
| `vladimir_fx_e_hit.png` | 第 11 条 / `prompts/11.txt` | 4 | 已重画，去掉初稿明显柔光；末帧残留血滴较多。 |
| `vladimir_fx_w_splash.png` | 第 12 条 / `prompts/12.txt` | 5 | 进出池喷溅五阶段完成；原稿帧间间距不均，使用 rect。 |
| `vladimir_fx_w_pool.png` | 第 13 条 / `prompts/13.txt` | 6 | 冒泡血池六帧完成；原稿椭圆偏扁，需按目标范围调整。 |
| `vladimir_fx_w_drain.png` | 第 14 条 / `prompts/14.txt` | 4 | 已重画，收细血丝，中心留空；主血丝为两条，未严格达到三至四条。 |
| `vladimir_fx_r_cloud.png` | 第 15 条 / `prompts/15.txt` | 7 | 酒红血云扩张、翻滚、消散完成；帧间间距不均，使用 rect。 |
| `vladimir_fx_r_mark.png` | 第 16 条 / `prompts/16.txt` | 4 | 已把实心星形改为空心带刺血环；旋转、刺数及逐像素镜像为近似。 |
| `vladimir_fx_r_burst.png` | 第 17 条 / `prompts/17.txt` | 6 | 白粉闪光、红紫爆发、残滴完成；第五帧雾团仍较实。 |
| `vladimir_fx_r_heal.png` | 第 18 条 / `prompts/18.txt` | 6 | 四面血带收束、胸口闪光、光点完成；第五帧保留额外亮芯。 |
| `vladimir_fx_c_blink.png` | 第 19 条 / `prompts/19.txt` | 5 | 血雾卷起与散开完成；末帧仍有较明显雾块，可再清理。 |

## 导入时

1. 使用 manifest 中的实际 rect，从左到右切帧；rect 包含原稿透明留白。不要直接把完整源格拉满目标大小。
2. 同一条动画采用共同缩放系数和固定锚点；不要按每帧包围盒分别拉满，否则会产生大小跳动。转成指定游戏格尺寸、硬边、固定色阶后再验收。
3. 依原提示词清理最深色外圈、半透明边和孤立噪点，保持白粉亮芯。E 血环与 W 血池需重新核对椭圆比例。
4. 飞行的 a_bolt / q_orb / q_rush / e_bolt 朝右；游戏可按飞行方向转。挂人物、地面、命中及回血图不旋转、不随红色方翻转。
5. q_ready、w_pool 画在人物下面；e_burst、r_cloud、w_splash 使用地面 ViewEffect，不能绑到会旋转的 RangeProjectile。
6. 手部出弹高度依 `reference/design/vladimir_shots.png`；人物基准为 28×40 格。E 蓄力 1 秒，W 血池 2 秒，R 标记 3 秒。
7. 预览统一使用 100 ms/帧，仅供审图。循环项持续时间和一次性特效节奏由工程导入配置决定。

本次完成特效原稿交付；没有附游戏工程，因此没有执行工程导入或实机验收。
