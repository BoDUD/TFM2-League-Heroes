# 泰隆特效交付：第 3 步

16 张主特效横条、共 72 帧已生成和整理。每张一个 PNG，文件名、帧数、单帧尺寸和横条画布均按输入清单。未改动原输入 ZIP。

## 每张使用的提示词和帧数

| 文件 | 帧数 | 单帧尺寸 | 条图尺寸 | 提示词 |
|---|---:|---|---|---|
| `talon_fx_a_hit.png` | 4 | 192×192 | 768×192 | PROMPTS.md 第 1 条；实际内容见 generation-records.json 中 `a_hit` |
| `talon_fx_p_wound.png` | 4 | 160×128 | 640×128 | PROMPTS.md 第 2 条；实际内容见 generation-records.json 中 `p_wound` |
| `talon_fx_p_bleed.png` | 6 | 320×320 | 1920×320 | PROMPTS.md 第 3 条；实际内容见 generation-records.json 中 `p_bleed` |
| `talon_fx_q_leap.png` | 4 | 384×224 | 1536×224 | PROMPTS.md 第 4 条；实际内容见 generation-records.json 中 `q_leap` |
| `talon_fx_q_hit.png` | 5 | 288×288 | 1440×288 | PROMPTS.md 第 5 条；实际内容见 generation-records.json 中 `q_hit` |
| `talon_fx_q_heal.png` | 5 | 256×384 | 1280×384 | PROMPTS.md 第 6 条；实际内容见 generation-records.json 中 `q_heal` |
| `talon_fx_w_out.png` | 4 | 288×352 | 1152×352 | PROMPTS.md 第 7 条；实际内容见 generation-records.json 中 `w_out` |
| `talon_fx_w_back.png` | 4 | 352×352 | 1408×352 | PROMPTS.md 第 8 条；实际内容见 generation-records.json 中 `w_back` |
| `talon_fx_w_hit.png` | 3 | 160×160 | 480×160 | PROMPTS.md 第 9 条；实际内容见 generation-records.json 中 `w_hit` |
| `talon_fx_w_slow.png` | 4 | 288×128 | 1152×128 | PROMPTS.md 第 10 条；实际内容见 generation-records.json 中 `w_slow` |
| `talon_fx_e_vault.png` | 5 | 416×288 | 2080×288 | PROMPTS.md 第 11 条；实际内容见 generation-records.json 中 `e_vault` |
| `talon_fx_e_haste.png` | 4 | 320×144 | 1280×144 | PROMPTS.md 第 12 条；实际内容见 generation-records.json 中 `e_haste` |
| `talon_fx_r_out.png` | 6 | 1024×512 | 6144×512 | PROMPTS.md 第 13 条；实际内容见 generation-records.json 中 `r_out` |
| `talon_fx_r_back.png` | 6 | 1024×512 | 6144×512 | PROMPTS.md 第 14 条；实际内容见 generation-records.json 中 `r_back` |
| `talon_fx_r_hit.png` | 4 | 224×224 | 896×224 | PROMPTS.md 第 15 条；实际内容见 generation-records.json 中 `r_hit` |
| `talon_fx_r_on.png` | 4 | 384×544 | 1536×544 | PROMPTS.md 第 16 条；实际内容见 generation-records.json 中 `r_on` |

使用内置 image_gen，每张特效独立一次生图。generation-records.json 保留原提示词与实际提示词；实际提示词将长横条改为紧凑的 2×2 或 3×2 生图图集，避免生成时挤压长条，并强调独立帧、无人物、对称。R 出刀/收刀另强调十二把分离的弯刃。后处理再裁帧，整理为要求的一行横条。不是用代码绘制方块特效。

## 版本和文件

- 根目录 `talon_fx_*.png`：主版本，保留生成的弯刃、血滴、十字和烟雾细节；规范到指定画布、色板和二值透明，逐帧强制指定方向的对称。内部像素块大小仍保留生成图特征，**不是统一 16×16 网格**。
- `pixel16/`：相同画布和帧数的严格 16×16 网格版本，二值透明、指定色板。`1x/` 为其游戏逻辑像素横条，`frames/` 为其逐帧逻辑尺寸 PNG。缩小后薄刃、三道小伤口和回血十字会明显简化，推荐导入者对照主版本判断。
- `frames-native/`：主版本逐帧 PNG；与主横条的对应矩形像素完全一致。
- `raw/`：16 张未改动的内置生图原稿，可能有半透明细边、非规则像素块和生成杂点。切片区域见 manifest.json 的 variants.raw.frames[].rect。
- `previews/index.html`：离线动画总览。GIF 和接触表使用深色背景，只有预览图有标题/帧号；特效 PNG 没有文字、边框或背景。
- `source/`：原输入说明、绑定清单和参考图备份。原版特效参考仅供本地参考，未公开发布。

## 对称、颜色与处理

W 去程/回程朝右、逐帧上下对称；其余 14 张逐帧左右对称。生成后从一半复制到另一半以严格保证对称，原始不对称结果仍可在 raw/ 查看。

在各原稿等分格中识别主体范围，使用该动作统一的包围区域和缩放比例，去掉多余空白并调整横向居中；不逐帧拉伸改变刀刃比例。原图的亮芯在逻辑尺寸采样时优先保留。主版本做最近邻缩放、色板量化和透明阈值处理，16 格版另做面积采样和二值化再最近邻放大。没有程序生成新的刀刃、血滴、火星或烟雾形状。

## 已完成的核对

16 张主横条与清单一致，72 帧均非空；尺寸、RGBA、二值透明、色板、每帧对称、切片矩形、逐帧文件与横条一致性、透明画布边缘全部通过。16 格变体另通过严格网格检查。逐帧 SHA-256、亮度与检查结果见 qa_report.json 和 qa/。

已逐张查看全部 16 组接触表，核对出刀、爆发、消散等阶段；没有画入人物、标签、网格或边框。主版本刀刃亮银白/冰蓝、回程暗红拖尾，回血绿色、隐身蓝紫；R 刀圈留出中央位置。单帧图元的具体形状仍是对提示词的像素化表达，未宣称与原版贴图逐像素相同。

## 导入时仍需处理的事项

输入允许交生图原稿；本包额外提供了规范画布/颜色/透明度的细节主版本和严格网格变体。主版本未达到统一 16 格像素块，16 格版在极小尺寸下会损失细节，导入者需按技能实际范围选择。主版本和 16 格版的 frames[].rect 相同，禁止将 raw/ 当作同一横条矩形切片。

manifest.json 是美术交接格式，assets[].frames[].rect = [x, y, 宽, 高]，坐标单位是图像像素。reference_game_size 和 binding_from_source 保留输入的大小/绑定说明；它们没有被自动写入游戏配置。输入没有给出特效逐帧时长，engine_frame_duration_ms 和各帧 duration_ms 保留 null，预览统一 100ms/帧并循环播放。游戏中的缩放、脚下锚点、覆盖层、持续时间、出手同步和循环接缝仍需实际导入验证；本次未安装或测试游戏。

## 完整交付文件清单

- `1x/talon_fx_a_hit.png`
- `1x/talon_fx_e_haste.png`
- `1x/talon_fx_e_vault.png`
- `1x/talon_fx_p_bleed.png`
- `1x/talon_fx_p_wound.png`
- `1x/talon_fx_q_heal.png`
- `1x/talon_fx_q_hit.png`
- `1x/talon_fx_q_leap.png`
- `1x/talon_fx_r_back.png`
- `1x/talon_fx_r_hit.png`
- `1x/talon_fx_r_on.png`
- `1x/talon_fx_r_out.png`
- `1x/talon_fx_w_back.png`
- `1x/talon_fx_w_hit.png`
- `1x/talon_fx_w_out.png`
- `1x/talon_fx_w_slow.png`
- `HANDOFF.md`
- `frames-native/a_hit/01.png`
- `frames-native/a_hit/02.png`
- `frames-native/a_hit/03.png`
- `frames-native/a_hit/04.png`
- `frames-native/e_haste/01.png`
- `frames-native/e_haste/02.png`
- `frames-native/e_haste/03.png`
- `frames-native/e_haste/04.png`
- `frames-native/e_vault/01.png`
- `frames-native/e_vault/02.png`
- `frames-native/e_vault/03.png`
- `frames-native/e_vault/04.png`
- `frames-native/e_vault/05.png`
- `frames-native/p_bleed/01.png`
- `frames-native/p_bleed/02.png`
- `frames-native/p_bleed/03.png`
- `frames-native/p_bleed/04.png`
- `frames-native/p_bleed/05.png`
- `frames-native/p_bleed/06.png`
- `frames-native/p_wound/01.png`
- `frames-native/p_wound/02.png`
- `frames-native/p_wound/03.png`
- `frames-native/p_wound/04.png`
- `frames-native/q_heal/01.png`
- `frames-native/q_heal/02.png`
- `frames-native/q_heal/03.png`
- `frames-native/q_heal/04.png`
- `frames-native/q_heal/05.png`
- `frames-native/q_hit/01.png`
- `frames-native/q_hit/02.png`
- `frames-native/q_hit/03.png`
- `frames-native/q_hit/04.png`
- `frames-native/q_hit/05.png`
- `frames-native/q_leap/01.png`
- `frames-native/q_leap/02.png`
- `frames-native/q_leap/03.png`
- `frames-native/q_leap/04.png`
- `frames-native/r_back/01.png`
- `frames-native/r_back/02.png`
- `frames-native/r_back/03.png`
- `frames-native/r_back/04.png`
- `frames-native/r_back/05.png`
- `frames-native/r_back/06.png`
- `frames-native/r_hit/01.png`
- `frames-native/r_hit/02.png`
- `frames-native/r_hit/03.png`
- `frames-native/r_hit/04.png`
- `frames-native/r_on/01.png`
- `frames-native/r_on/02.png`
- `frames-native/r_on/03.png`
- `frames-native/r_on/04.png`
- `frames-native/r_out/01.png`
- `frames-native/r_out/02.png`
- `frames-native/r_out/03.png`
- `frames-native/r_out/04.png`
- `frames-native/r_out/05.png`
- `frames-native/r_out/06.png`
- `frames-native/w_back/01.png`
- `frames-native/w_back/02.png`
- `frames-native/w_back/03.png`
- `frames-native/w_back/04.png`
- `frames-native/w_hit/01.png`
- `frames-native/w_hit/02.png`
- `frames-native/w_hit/03.png`
- `frames-native/w_out/01.png`
- `frames-native/w_out/02.png`
- `frames-native/w_out/03.png`
- `frames-native/w_out/04.png`
- `frames-native/w_slow/01.png`
- `frames-native/w_slow/02.png`
- `frames-native/w_slow/03.png`
- `frames-native/w_slow/04.png`
- `frames/a_hit/01.png`
- `frames/a_hit/02.png`
- `frames/a_hit/03.png`
- `frames/a_hit/04.png`
- `frames/e_haste/01.png`
- `frames/e_haste/02.png`
- `frames/e_haste/03.png`
- `frames/e_haste/04.png`
- `frames/e_vault/01.png`
- `frames/e_vault/02.png`
- `frames/e_vault/03.png`
- `frames/e_vault/04.png`
- `frames/e_vault/05.png`
- `frames/p_bleed/01.png`
- `frames/p_bleed/02.png`
- `frames/p_bleed/03.png`
- `frames/p_bleed/04.png`
- `frames/p_bleed/05.png`
- `frames/p_bleed/06.png`
- `frames/p_wound/01.png`
- `frames/p_wound/02.png`
- `frames/p_wound/03.png`
- `frames/p_wound/04.png`
- `frames/q_heal/01.png`
- `frames/q_heal/02.png`
- `frames/q_heal/03.png`
- `frames/q_heal/04.png`
- `frames/q_heal/05.png`
- `frames/q_hit/01.png`
- `frames/q_hit/02.png`
- `frames/q_hit/03.png`
- `frames/q_hit/04.png`
- `frames/q_hit/05.png`
- `frames/q_leap/01.png`
- `frames/q_leap/02.png`
- `frames/q_leap/03.png`
- `frames/q_leap/04.png`
- `frames/r_back/01.png`
- `frames/r_back/02.png`
- `frames/r_back/03.png`
- `frames/r_back/04.png`
- `frames/r_back/05.png`
- `frames/r_back/06.png`
- `frames/r_hit/01.png`
- `frames/r_hit/02.png`
- `frames/r_hit/03.png`
- `frames/r_hit/04.png`
- `frames/r_on/01.png`
- `frames/r_on/02.png`
- `frames/r_on/03.png`
- `frames/r_on/04.png`
- `frames/r_out/01.png`
- `frames/r_out/02.png`
- `frames/r_out/03.png`
- `frames/r_out/04.png`
- `frames/r_out/05.png`
- `frames/r_out/06.png`
- `frames/w_back/01.png`
- `frames/w_back/02.png`
- `frames/w_back/03.png`
- `frames/w_back/04.png`
- `frames/w_hit/01.png`
- `frames/w_hit/02.png`
- `frames/w_hit/03.png`
- `frames/w_out/01.png`
- `frames/w_out/02.png`
- `frames/w_out/03.png`
- `frames/w_out/04.png`
- `frames/w_slow/01.png`
- `frames/w_slow/02.png`
- `frames/w_slow/03.png`
- `frames/w_slow/04.png`
- `generation-prompts.txt`
- `generation-records.json`
- `manifest.json`
- `pixel16/talon_fx_a_hit.png`
- `pixel16/talon_fx_e_haste.png`
- `pixel16/talon_fx_e_vault.png`
- `pixel16/talon_fx_p_bleed.png`
- `pixel16/talon_fx_p_wound.png`
- `pixel16/talon_fx_q_heal.png`
- `pixel16/talon_fx_q_hit.png`
- `pixel16/talon_fx_q_leap.png`
- `pixel16/talon_fx_r_back.png`
- `pixel16/talon_fx_r_hit.png`
- `pixel16/talon_fx_r_on.png`
- `pixel16/talon_fx_r_out.png`
- `pixel16/talon_fx_w_back.png`
- `pixel16/talon_fx_w_hit.png`
- `pixel16/talon_fx_w_out.png`
- `pixel16/talon_fx_w_slow.png`
- `previews/a_hit-contact.png`
- `previews/a_hit-pixel16-contact.png`
- `previews/a_hit-pixel16.gif`
- `previews/a_hit.gif`
- `previews/e_haste-contact.png`
- `previews/e_haste-pixel16-contact.png`
- `previews/e_haste-pixel16.gif`
- `previews/e_haste.gif`
- `previews/e_vault-contact.png`
- `previews/e_vault-pixel16-contact.png`
- `previews/e_vault-pixel16.gif`
- `previews/e_vault.gif`
- `previews/index.html`
- `previews/overview.png`
- `previews/p_bleed-contact.png`
- `previews/p_bleed-pixel16-contact.png`
- `previews/p_bleed-pixel16.gif`
- `previews/p_bleed.gif`
- `previews/p_wound-contact.png`
- `previews/p_wound-pixel16-contact.png`
- `previews/p_wound-pixel16.gif`
- `previews/p_wound.gif`
- `previews/q_heal-contact.png`
- `previews/q_heal-pixel16-contact.png`
- `previews/q_heal-pixel16.gif`
- `previews/q_heal.gif`
- `previews/q_hit-contact.png`
- `previews/q_hit-pixel16-contact.png`
- `previews/q_hit-pixel16.gif`
- `previews/q_hit.gif`
- `previews/q_leap-contact.png`
- `previews/q_leap-pixel16-contact.png`
- `previews/q_leap-pixel16.gif`
- `previews/q_leap.gif`
- `previews/r_back-contact.png`
- `previews/r_back-pixel16-contact.png`
- `previews/r_back-pixel16.gif`
- `previews/r_back.gif`
- `previews/r_hit-contact.png`
- `previews/r_hit-pixel16-contact.png`
- `previews/r_hit-pixel16.gif`
- `previews/r_hit.gif`
- `previews/r_on-contact.png`
- `previews/r_on-pixel16-contact.png`
- `previews/r_on-pixel16.gif`
- `previews/r_on.gif`
- `previews/r_out-contact.png`
- `previews/r_out-pixel16-contact.png`
- `previews/r_out-pixel16.gif`
- `previews/r_out.gif`
- `previews/w_back-contact.png`
- `previews/w_back-pixel16-contact.png`
- `previews/w_back-pixel16.gif`
- `previews/w_back.gif`
- `previews/w_hit-contact.png`
- `previews/w_hit-pixel16-contact.png`
- `previews/w_hit-pixel16.gif`
- `previews/w_hit.gif`
- `previews/w_out-contact.png`
- `previews/w_out-pixel16-contact.png`
- `previews/w_out-pixel16.gif`
- `previews/w_out.gif`
- `previews/w_slow-contact.png`
- `previews/w_slow-pixel16-contact.png`
- `previews/w_slow-pixel16.gif`
- `previews/w_slow.gif`
- `qa/a_hit.json`
- `qa/e_haste.json`
- `qa/e_vault.json`
- `qa/p_bleed.json`
- `qa/p_wound.json`
- `qa/q_heal.json`
- `qa/q_hit.json`
- `qa/q_leap.json`
- `qa/r_back.json`
- `qa/r_hit.json`
- `qa/r_on.json`
- `qa/r_out.json`
- `qa/w_back.json`
- `qa/w_hit.json`
- `qa/w_out.json`
- `qa/w_slow.json`
- `qa_report.json`
- `raw/talon_fx_a_hit.png`
- `raw/talon_fx_e_haste.png`
- `raw/talon_fx_e_vault.png`
- `raw/talon_fx_p_bleed.png`
- `raw/talon_fx_p_wound.png`
- `raw/talon_fx_q_heal.png`
- `raw/talon_fx_q_hit.png`
- `raw/talon_fx_q_leap.png`
- `raw/talon_fx_r_back.png`
- `raw/talon_fx_r_hit.png`
- `raw/talon_fx_r_on.png`
- `raw/talon_fx_r_out.png`
- `raw/talon_fx_w_back.png`
- `raw/talon_fx_w_hit.png`
- `raw/talon_fx_w_out.png`
- `raw/talon_fx_w_slow.png`
- `source/PROMPTS.md`
- `source/design/talon_design.png`
- `source/design/talon_shots.png`
- `source/design/talon_size.png`
- `source/fx_list.json`
- `source/refs/lol_fx_ref.png`
- `talon_fx_a_hit.png`
- `talon_fx_e_haste.png`
- `talon_fx_e_vault.png`
- `talon_fx_p_bleed.png`
- `talon_fx_p_wound.png`
- `talon_fx_q_heal.png`
- `talon_fx_q_hit.png`
- `talon_fx_q_leap.png`
- `talon_fx_r_back.png`
- `talon_fx_r_hit.png`
- `talon_fx_r_on.png`
- `talon_fx_r_out.png`
- `talon_fx_w_back.png`
- `talon_fx_w_hit.png`
- `talon_fx_w_out.png`
- `talon_fx_w_slow.png`
