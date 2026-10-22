# 乌迪尔技能特效交接

日期：2026-10-22。全部 24 组原稿已由内置 imagegen 生成，共 107 帧，已完成按游戏格读回、硬 alpha、指定对称与 8 倍导出。先前因额度中断的 17 组本次已补齐。

## 文件

- pixel_1x/：24 张单行精灵表，按 manifest.json 的 frames / cell_1x 导入。
- 顶层 udyr_fx_*.png：精确最近邻放大 8 倍的24张帧表。
- raw/：24张原始生成图，未经处理，保留生成器的实际尺寸与原始布局。
- animations/：GIF快速预览；逐帧导入应使用 PNG。preview.html 使用PNG帧表播放、可暂停和筛选姿态。
- manifest.json：帧数、每帧尺寸、对称、绑定、原稿布局、色板、逐帧像素检查。
- generation-prompts.txt：实际提示词。validation.json：本次验证。
- pending.json 为空；pending-prompts.txt 标明全部生成。

## 交付清单

| 名称 | 帧数 | 每帧游戏像素 | 对称 |
|---|---|---|---|
| a_hit | 3 | 10×10 | left-right |
| q_on | 5 | 16×16 | left-right |
| q_wake | 6 | 50×50 | left-right |
| q_as | 4 | 34×10 | left-right |
| q_swipe | 3 | 28×24 | none (forward) |
| q_hit | 4 | 18×18 | left-right |
| q_bolt | 4 | 10×8 | top-bottom |
| q_bolt_hit | 5 | 22×48 | left-right |
| e_on | 5 | 16×16 | left-right |
| e_wake | 6 | 50×52 | left-right |
| e_ms | 4 | 30×10 | left-right |
| e_imm | 4 | 20×8 | left-right |
| e_trail | 4 | 36×18 | none (forward) |
| e_hit | 4 | 24×24 | left-right |
| e_stun | 4 | 16×6 | left-right |
| r_on | 5 | 16×16 | left-right |
| r_storm | 6 | 64×44 | left-right |
| r_hit | 3 | 14×14 | left-right |
| r_slow | 4 | 20×6 | left-right |
| r_rel | 4 | 30×20 | top-bottom |
| r_rel_hit | 6 | 36×36 | left-right |
| w_on | 6 | 48×52 | left-right |
| w_sh | 4 | 46×50 | left-right |
| w_heal | 4 | 24×30 | left-right |

## 原稿与读回

全部特效图形由 imagegen 绘制。代码仅用于复制、按格取色、限定色板、硬透明、成对像素对称、帧排列和放大；未用代码拼出替代特效。

原稿实际布局可能与请求不同，已按目视调整来源切格。公羊图腾实际是横向五帧，其有效区域从原稿取框后读回，保留raw原图不变。每游戏格过半像素可见（alpha≥128）才保留，取可见像素最近指定颜色的众数；成对像素取其中已有的更亮颜色并镜像。冰晶色板允许近黑实物描边，能量不添加黑描边。原稿柔光会在读回时舍弃。

## 验证与局限

24组均验证精灵表尺寸、帧数、非空、alpha仅0/255、左右/上下对称和8倍图逐像素一致。unique_frame_count 可检查读回后独立帧数。

数值通过不等于最终美术或运行验收。小尺寸图腾、电弧、爪弧、环线读回后仍可能简化或断裂；需要按游戏实际背景和动画速度审阅。原稿中的细节、各帧生成形状和身体留空是美术近似；没有把数值PASS称作视觉完美。

本次没有修改仓库/已安装模组或技能机制；未测试视图触发、跟随目标、Z层、地形遮挡、弹道方向和正式动画时序。预览140ms/帧只用于检查，不是引擎时长。技能绑定沿用用户参考包说明，不表示已实现。

参考包内Riot贴图仅本地参考，没有放进交付包。本包可交给下游切格整合；游戏内验收仍待完成。
