# 泰隆动作帧交付：第 2 步

9 个动作、57 张独立动作 PNG 已完成。根目录为可交接帧文件：960×896、RGBA 透明、120×112 逻辑像素严格放大 8 倍。原始输入 ZIP 未改动。

## 动作和时间

| 动作 | 帧数 | 每帧毫秒 | 出手/命中帧 |
|---|---:|---|---|
| run | 8 | 121 121 121 121 121 121 121 121 | — |
| attack | 5 | 60 50 80 80 110 | 第 3 帧 |
| skill | 6 | 50 50 80 70 70 90 | 第 3 帧 |
| skill2 | 7 | 60 50 60 80 70 80 90 | 第 4 帧 |
| skill2_stab | 6 | 50 50 70 70 70 90 | 第 3 帧 |
| skill_e | 7 | 60 60 60 60 60 70 90 | 第 5 帧 |
| ult | 8 | 50 50 60 60 60 60 60 90 | 第 3 帧 |
| hit | 2 | 120 120 | — |
| dead | 8 | 100 100 100 120 120 150 200 500 | — |

`animation_manifest.json` 保留输入的逐帧时长与 pivot，命中帧从 1 开始计数，event_at_ms 是对应帧开始的累计毫秒。pivot 使用逻辑像素。原输入 head/tilt 只是原版参考定位，未当作新绘头部坐标；它们仅保留在 design/source_talon_cells.json 中。输入中的 idle 未列入本次 57 帧，也未生成。

## 处理与核验

- 每帧独立生成原画，保存在 raw/；raw/ 不是可直接导入的严格网格最终帧。
- 最终帧经最近邻采样和缩放、22 色量化、二值透明、参照剪影摆放，再按 8 倍最近邻输出；少量孤立的 1–2 格采样杂点已清除。逐帧处理记录在 qa/。
- 落地帧将整个人物平移至 y=784 地面边界；空中帧保留空隙，必要时整体上移。没有通过裁脚实现落地。最终所有帧 y>=784 为空，画布边缘为空。
- 跑步 8 帧逐像素覆盖并核对提供的上半身前景，头、肩甲、衣服及披风上部保留模板；模板空白处允许新绘交叉腿部。
- 死亡第 8 帧使用第 7 帧的最终图像，保证停住；独立生成的第 8 帧原画仍保留在 raw/。
- 57 帧均通过尺寸、RGBA、二值透明、8×8 网格、色板、地面边界、画布边缘检查。qa_report.json 含检查结果和最终帧 SHA-256。
- 已查看 9 组最终动作接触表，核对主要姿势、兜帽阴影、腕刃和披风；像素化姿势是参考动作的简化表达，未宣称和原版逐像素重合。

## 文件使用

根目录的动作 PNG 用于下一步导入；1x/ 为其 120×112 逻辑原尺寸。previews/ 含逐动作接触表、GIF 和总览。GIF 为观察动作而循环播放，并按输入 pivot 对齐，最终 PNG 未因预览对齐而改变位置。GIF 格式以 10ms 为单位，跑步 121ms 在 GIF 中显示为 120ms；正式时长以 animation_manifest.json 为准。

design/ 包含提供的定稿、色板和原始说明备份。generation-prompts.txt 记录实际逐帧提示词。本次只交付动作美术，尚未安装进游戏，也未验证游戏内播放或碰撞。

## 完整交付文件清单

- `1x/attack_01.png`
- `1x/attack_02.png`
- `1x/attack_03.png`
- `1x/attack_04.png`
- `1x/attack_05.png`
- `1x/dead_01.png`
- `1x/dead_02.png`
- `1x/dead_03.png`
- `1x/dead_04.png`
- `1x/dead_05.png`
- `1x/dead_06.png`
- `1x/dead_07.png`
- `1x/dead_08.png`
- `1x/hit_01.png`
- `1x/hit_02.png`
- `1x/run_01.png`
- `1x/run_02.png`
- `1x/run_03.png`
- `1x/run_04.png`
- `1x/run_05.png`
- `1x/run_06.png`
- `1x/run_07.png`
- `1x/run_08.png`
- `1x/skill2_01.png`
- `1x/skill2_02.png`
- `1x/skill2_03.png`
- `1x/skill2_04.png`
- `1x/skill2_05.png`
- `1x/skill2_06.png`
- `1x/skill2_07.png`
- `1x/skill2_stab_01.png`
- `1x/skill2_stab_02.png`
- `1x/skill2_stab_03.png`
- `1x/skill2_stab_04.png`
- `1x/skill2_stab_05.png`
- `1x/skill2_stab_06.png`
- `1x/skill_01.png`
- `1x/skill_02.png`
- `1x/skill_03.png`
- `1x/skill_04.png`
- `1x/skill_05.png`
- `1x/skill_06.png`
- `1x/skill_e_01.png`
- `1x/skill_e_02.png`
- `1x/skill_e_03.png`
- `1x/skill_e_04.png`
- `1x/skill_e_05.png`
- `1x/skill_e_06.png`
- `1x/skill_e_07.png`
- `1x/ult_01.png`
- `1x/ult_02.png`
- `1x/ult_03.png`
- `1x/ult_04.png`
- `1x/ult_05.png`
- `1x/ult_06.png`
- `1x/ult_07.png`
- `1x/ult_08.png`
- `HANDOFF.md`
- `animation_manifest.json`
- `attack_01.png`
- `attack_02.png`
- `attack_03.png`
- `attack_04.png`
- `attack_05.png`
- `dead_01.png`
- `dead_02.png`
- `dead_03.png`
- `dead_04.png`
- `dead_05.png`
- `dead_06.png`
- `dead_07.png`
- `dead_08.png`
- `design/palette.hex`
- `design/palette.png`
- `design/source_MODEL_STRIPS.md`
- `design/source_talon_cells.json`
- `design/talon_design.png`
- `design/talon_design_1x.png`
- `generation-prompts.txt`
- `hit_01.png`
- `hit_02.png`
- `previews/all-actions.png`
- `previews/attack-contact.png`
- `previews/attack.gif`
- `previews/dead-contact.png`
- `previews/dead.gif`
- `previews/hit-contact.png`
- `previews/hit.gif`
- `previews/run-contact.png`
- `previews/run.gif`
- `previews/skill-contact.png`
- `previews/skill.gif`
- `previews/skill2-contact.png`
- `previews/skill2.gif`
- `previews/skill2_stab-contact.png`
- `previews/skill2_stab.gif`
- `previews/skill_e-contact.png`
- `previews/skill_e.gif`
- `previews/ult-contact.png`
- `previews/ult.gif`
- `qa/attack_01.json`
- `qa/attack_02.json`
- `qa/attack_03.json`
- `qa/attack_04.json`
- `qa/attack_05.json`
- `qa/dead_01.json`
- `qa/dead_02.json`
- `qa/dead_03.json`
- `qa/dead_04.json`
- `qa/dead_05.json`
- `qa/dead_06.json`
- `qa/dead_07.json`
- `qa/dead_08.json`
- `qa/hit_01.json`
- `qa/hit_02.json`
- `qa/run_01.json`
- `qa/run_02.json`
- `qa/run_03.json`
- `qa/run_04.json`
- `qa/run_05.json`
- `qa/run_06.json`
- `qa/run_07.json`
- `qa/run_08.json`
- `qa/skill2_01.json`
- `qa/skill2_02.json`
- `qa/skill2_03.json`
- `qa/skill2_04.json`
- `qa/skill2_05.json`
- `qa/skill2_06.json`
- `qa/skill2_07.json`
- `qa/skill2_stab_01.json`
- `qa/skill2_stab_02.json`
- `qa/skill2_stab_03.json`
- `qa/skill2_stab_04.json`
- `qa/skill2_stab_05.json`
- `qa/skill2_stab_06.json`
- `qa/skill_01.json`
- `qa/skill_02.json`
- `qa/skill_03.json`
- `qa/skill_04.json`
- `qa/skill_05.json`
- `qa/skill_06.json`
- `qa/skill_e_01.json`
- `qa/skill_e_02.json`
- `qa/skill_e_03.json`
- `qa/skill_e_04.json`
- `qa/skill_e_05.json`
- `qa/skill_e_06.json`
- `qa/skill_e_07.json`
- `qa/ult_01.json`
- `qa/ult_02.json`
- `qa/ult_03.json`
- `qa/ult_04.json`
- `qa/ult_05.json`
- `qa/ult_06.json`
- `qa/ult_07.json`
- `qa/ult_08.json`
- `qa_report.json`
- `raw/attack_01.png`
- `raw/attack_02.png`
- `raw/attack_03.png`
- `raw/attack_04.png`
- `raw/attack_05.png`
- `raw/dead_01.png`
- `raw/dead_02.png`
- `raw/dead_03.png`
- `raw/dead_04.png`
- `raw/dead_05.png`
- `raw/dead_06.png`
- `raw/dead_07.png`
- `raw/dead_08.png`
- `raw/hit_01.png`
- `raw/hit_02.png`
- `raw/run_01.png`
- `raw/run_02.png`
- `raw/run_03.png`
- `raw/run_04.png`
- `raw/run_05.png`
- `raw/run_06.png`
- `raw/run_07.png`
- `raw/run_08.png`
- `raw/skill2_01.png`
- `raw/skill2_02.png`
- `raw/skill2_03.png`
- `raw/skill2_04.png`
- `raw/skill2_05.png`
- `raw/skill2_06.png`
- `raw/skill2_07.png`
- `raw/skill2_stab_01.png`
- `raw/skill2_stab_02.png`
- `raw/skill2_stab_03.png`
- `raw/skill2_stab_04.png`
- `raw/skill2_stab_05.png`
- `raw/skill2_stab_06.png`
- `raw/skill_01.png`
- `raw/skill_02.png`
- `raw/skill_03.png`
- `raw/skill_04.png`
- `raw/skill_05.png`
- `raw/skill_06.png`
- `raw/skill_e_01.png`
- `raw/skill_e_02.png`
- `raw/skill_e_03.png`
- `raw/skill_e_04.png`
- `raw/skill_e_05.png`
- `raw/skill_e_06.png`
- `raw/skill_e_07.png`
- `raw/ult_01.png`
- `raw/ult_02.png`
- `raw/ult_03.png`
- `raw/ult_04.png`
- `raw/ult_05.png`
- `raw/ult_06.png`
- `raw/ult_07.png`
- `raw/ult_08.png`
- `run_01.png`
- `run_02.png`
- `run_03.png`
- `run_04.png`
- `run_05.png`
- `run_06.png`
- `run_07.png`
- `run_08.png`
- `skill2_01.png`
- `skill2_02.png`
- `skill2_03.png`
- `skill2_04.png`
- `skill2_05.png`
- `skill2_06.png`
- `skill2_07.png`
- `skill2_stab_01.png`
- `skill2_stab_02.png`
- `skill2_stab_03.png`
- `skill2_stab_04.png`
- `skill2_stab_05.png`
- `skill2_stab_06.png`
- `skill_01.png`
- `skill_02.png`
- `skill_03.png`
- `skill_04.png`
- `skill_05.png`
- `skill_06.png`
- `skill_e_01.png`
- `skill_e_02.png`
- `skill_e_03.png`
- `skill_e_04.png`
- `skill_e_05.png`
- `skill_e_06.png`
- `skill_e_07.png`
- `ult_01.png`
- `ult_02.png`
- `ult_03.png`
- `ult_04.png`
- `ult_05.png`
- `ult_06.png`
- `ult_07.png`
- `ult_08.png`
