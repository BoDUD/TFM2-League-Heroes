# 峡谷先锋：18 个动作原稿交付

本包已补齐全部 18 个指定姿势，并完成旋转、背甲冲锋、腾空翻身和侧翻倒下的定向重画。所有角色图由原生 image_gen 绘制；没有脚本逐格绘画，没有缩放、重新采样、调色或阈值透明处理。每个交付 PNG 与 raw/ 同名文件逐字节一致。

**交付状态：18 张源图齐全，但严格像素网格、硬 alpha 和帧间一致性仍未全部达标。本包是动作原稿交接，不是可直接发布的游戏动画。**

## 18 张姿势

| 文件 | 内容 |
|---|---|
| riftherald-pose-a_raise.png | 普攻举钳 |
| riftherald-pose-a_strike.png | 普攻下砸 |
| riftherald-pose-q_wind.png | 横扫起手 |
| riftherald-pose-q_spin.png | 半转背身横扫，背甲竖眼可见；重画版 |
| riftherald-pose-q_end.png | 横扫收势，尾巴扫过身前 |
| riftherald-pose-e_rear.png | 直立长啸 |
| riftherald-pose-e_flip.png | 腾空翻身、头朝下；第三版 |
| riftherald-pose-e_charge.png | 背甲在前、头朝下的冲锋；重画版 |
| riftherald-pose-r_crouch.png | 缩身蓄力 |
| riftherald-pose-r_slam.png | 双钳猛击 |
| riftherald-pose-run1.png | 小跑第 1 帧 |
| riftherald-pose-run2.png | 小跑第 2 帧 |
| riftherald-pose-run3.png | 小跑第 3 帧 |
| riftherald-pose-run4.png | 小跑第 4 帧 |
| riftherald-pose-run5.png | 小跑第 5 帧 |
| riftherald-pose-run6.png | 小跑第 6 帧 |
| riftherald-pose-d_fall.png | 向后侧翻、后腿抬起；重画版 |
| riftherald-pose-d_down.png | 翻倒在甲壳上，眼睛与甲壳斑点变暗 |

## 其余文件

- raw/：18 张选定生成图，未经修改。
- raw/attempts/：被替换的 q_spin、e_charge、e_flip、d_fall 初稿，以及 e_flip 第二版。供追溯，不作为当前选定帧。
- preview.html：离线原稿浏览和六帧小跑循环播放器。先解压整个文件夹，再打开；可暂停、逐张切换、调整帧间隔、显示地面参考线。浏览器显示尺寸不改变 PNG 文件。
- reference/：包内已定稿造型与头部原图副本。
- generation-prompts.txt：实际提示词，含初次 18 个请求和后续修订。
- revision-prompts.txt、death-revision-prompt.txt、flip-airborne-revision-prompt.txt：修订提示词的独立副本。
- generation-history.json：生成来源和选定版本记录。
- QA.json：18 张的画布、alpha、主体边界、网格检查、原稿一致性与 SHA256。
- STATUS.json：本次状态、选定源文件和剩余质量限制。
- history/：上次额度中断时的进度快照，仅供历史追溯，不是当前缺图清单。

## 已验证

18 张全部为 1254×1254 RGBA，包含真实透明通道。每张选定 PNG 与 raw/ 备份完全相同，18 个文件名无遗漏。预览中 18 个姿势路径已核对，脚本通过 Node 语法检查。

腾空翻身最后一版的主体边界（alpha>=128）是 (232,19)-(1085,1094)，最低点在参考地面 y=1176 上方 82px，已修正前两版延伸到底部的问题。这个边界是像素检查值，不是骨骼或实际格子测量。

## 必须保留的质量说明

生成器没有严格遵循每格 8px、从画布原点整齐对齐的要求；18 张严格网格检查均未通过。图中存在半透明像素，也没有满足 alpha 只能是 0 或 255 的要求。遵照本次不能缩放和重新采样原图的要求，没有用后处理强制制造合格网格或硬 alpha。

脸部并非逐格复制同一张脸；甲壳、腿、钳爪和身体尺度也存在帧间漂移。一部分站立帧没有精确落在 y=1176。q_spin 重画优先表现文字要求的半转背身和横向扫击，因此与模型参考图的投影角度并不完全重合。

六张小跑帧已分别生成，能够按顺序预览，但没有通过连续动画验收：脚步交替、两次经过身体下方、脸与甲壳完全固定以及自然回环仍需逐帧美术修正。不要将“六张齐全”视作“循环已经流畅”。

后续应按各 raw 原稿的真实像素台阶读回，并以 reference/ 定稿校准脸、部件尺度和 PPU；完成格子清理、基线对齐和小跑衔接后再接入游戏。本轮未改动游戏、骨架、动画表、技能代码或仓库。
