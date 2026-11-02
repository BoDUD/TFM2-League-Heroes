# 锋啄鸟特效与图标交付

10 套动画特效表与 3 个技能图标，全部使用内置 image_gen 生成原稿，随后按格采样导出。没有用代码绘制替代特效形状。

## 文件

- `raptor_fx_<名字>.png`：8 倍整数放大的单行特效表。
- `pixel_1x/raptor_fx_<名字>.png`：原尺寸单行表，直接按 manifest 的 cell_1x 切帧。
- `raptor_icon_skill.png`、`raptor_icon_skill2.png`、`raptor_icon_ult.png`：64×64，2 px 方块。
- `raw/`：每套特效及图标的原始生成图，未改动。
- `manifest.json`：每张帧数、切格大小、原稿排版、对称方向、真实原稿尺寸、不同帧数和 alpha 记录。
- `preview.png`、`preview_<名字>.gif`：总览与逐套动画预览。
- `generation-prompts.txt`：实际提示词。

## 帧数与尺寸

| 名称 | 帧数 | 每帧游戏像素 | 对称 |
|---|---:|---|---|
| a_bolt | 4 | 14×6 | 上下，朝右 |
| a_hit | 4 | 14×14 | 左右 |
| q_feather | 4 | 20×8 | 上下，朝右 |
| q_hit | 4 | 18×16 | 左右 |
| r_peck | 4 | 12×6 | 上下，朝右 |
| r_peck_hit | 4 | 12×12 | 左右 |
| e_jump | 5 | 40×14 | 左右 |
| e_rush | 6 | 56×40 | 左右 |
| p_shred | 6 | 12×12 | 左右 |
| r_flock | 6 | 84×44 | 左右 |

## 工艺和验证

为避免极宽原稿把每帧压扁，生图使用等格的多行布局（4 帧 2×2，5 帧 2×3 末格空，6 帧 3×2）。导出按行读取，逐逻辑格取最近指定调色板的多数颜色，alpha 仅 0/255，再将每帧对称像素配对读取并镜像统一，最后排列为单行。鸟群左右两组生成像素分别向外平移 3 游戏像素，中央保留完整的 50 像素宽透明通道；没有重绘小鸟。所有原稿仍在 raw/，不会把采样和对称处理冒充模型原生精确输出。修正提示词分别在 revision-prompts.txt、flock-revision-prompt.txt 和 shred-revision-prompt.txt。

已校验文件清单、每帧非空、帧数、尺寸、硬 alpha 和逐像素对称性；不同帧数量及哈希在 manifest。此交付完成素材制作与导出，未绑定游戏 view_projectiles/view_effects/view_buffs 或技能图标路径，未进行运行时观感验收。
