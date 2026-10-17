# 云安娜最终特效素材交付

已完成 22 张特效表，共 95 帧。所有特效形状均由内置 image_gen 生成，再从原稿分帧、取格、归入指定色板并做对称校正；未使用代码拼画原始特效。未连接游戏工程，未执行游戏内导入或实机测试。

## 文件

- 根目录 yunara_fx_*.png：22 张 8 倍最近邻放大图，均为横向单行帧表。
- pixel_1x/：22 张原尺寸横向单行帧表，游戏导入请使用这一份。
- raw/：22 张原始生成图，以及射线的 1 张额外清理尝试，共 23 张；原图内容未修改。
- manifest.json：每张图的帧数、每帧宽高、1x/8x 尺寸、对称方向、色板、源图散列、源分帧位置与取样参数。
- validation.json：22 张几何、硬透明、逐帧对称、8 倍最近邻一致性及非空帧检查，全部通过。
- generation-prompts.txt：22 次实际生图提示词；cleanup-generation-prompt.txt：射线额外清理尝试的提示词。
- previews/overview.png：22 种特效代表帧总览。
- previews/*.gif：22 个暗底动画预览。GIF 中的暗底仅用于观察，不存在于交付 PNG 中。

参考贴图 lol_fx_ref.png 仅在本地用于生图参考，没有放入交付包。

## 帧格清单

以下宽高是每帧的游戏像素格，整张 1x 帧表宽度 = 帧数 × 每帧宽度。8x 图的两轴再乘 8。

| 文件 | 帧数 | 每帧宽 × 高 | 逐帧对称 |
|---|---:|---|---|
| yunara_fx_a_bead.png | 2 | 14 × 8 | 上下 |
| yunara_fx_q_bead.png | 4 | 18 × 10 | 上下 |
| yunara_fx_a_hit.png | 4 | 12 × 12 | 左右 |
| yunara_fx_q_hit.png | 5 | 18 × 18 | 左右 |
| yunara_fx_q_sp_hit.png | 3 | 10 × 10 | 左右 |
| yunara_fx_q_spread.png | 4 | 62 × 22 | 左右 |
| yunara_fx_q_burst.png | 5 | 28 × 40 | 左右 |
| yunara_fx_w_bead.png | 4 | 18 × 14 | 上下 |
| yunara_fx_w_hit.png | 4 | 16 × 16 | 左右 |
| yunara_fx_w_end.png | 6 | 20 × 16 | 左右 |
| yunara_fx_w_tick.png | 3 | 12 × 12 | 左右 |
| yunara_fx_rw_charge.png | 4 | 32 × 60 | 左右 |
| yunara_fx_rw_beam.png | 6 | 120 × 18 | 上下 |
| yunara_fx_rw_hit.png | 5 | 20 × 20 | 左右 |
| yunara_fx_e_cast.png | 5 | 30 × 12 | 左右 |
| yunara_fx_re_trail.png | 5 | 40 × 44 | 左右 |
| yunara_fx_r_burst.png | 6 | 56 × 64 | 左右 |
| yunara_fx_q_on.png | 4 | 28 × 30 | 左右 |
| yunara_fx_r_on.png | 4 | 36 × 48 | 左右 |
| yunara_fx_e_ms.png | 4 | 24 × 8 | 左右 |
| yunara_fx_w_slow0.png | 4 | 16 × 6 | 左右 |
| yunara_fx_rw_slow0.png | 4 | 16 × 6 | 左右 |

## 取格与清理说明

生成模型没有严格输出指定像素尺寸，因此最终文件不是直接缩小整个原稿。先依实际网格分帧，清除低 alpha、离色板过远及微小噪点，提取生成形状的内容区域，再按各阶段的目标占格尺寸进行取样。颜色使用分割后前景样本中的多数颜色，并归入包中指定的紫蓝、金白与铜色色板。

普通格子要求至少 50% 的有效前景覆盖；两张细减速圈使用 12% 的覆盖阈值以保留细线，颜色仍取有效前景的多数色。极小闪点在必要时收紧取样区域。光效的最深色阶已限制，铜珠保留深色材质阴影。身周火焰、夜影翻内侧及减速圈内侧另外清空人物/光环的透明区域。这些步骤是对生成素材的提取与裁切，没有另外合成特效形状。

对称采用对应源格合并、保留更亮样本：a_bead、q_bead、w_bead、rw_beam 上下逐格对称，其余左右逐格对称。射线每帧最左 6 格严格为空。

原稿 rw_hit 实际排成 3 列 2 行，已据实际内容分帧；其余源布局及每帧取样框见 manifest。所有最终帧表统一为从左至右播放的一行。

## 导入注意

- 以 manifest.json 的 frame_width / frame_height / frames 切 pixel_1x/，不要从 raw/ 再次猜格。
- w_slow0 与 rw_slow0 按逐条提示词的帧格采用 16×6；原文绑定表的 16×5 是显示大小参考，不能直接当切格高度。
- GIF 默认约 100 ms/帧，仅用于视觉预览；射线预览前 3 帧各 180 ms，共 540 ms。实际播放时长和命中 tick 应在游戏工程中绑定。
- 已通过文件级检查；战场亮度、角色遮挡、特效层级、循环衔接和技能时序仍需导入游戏后验收。

