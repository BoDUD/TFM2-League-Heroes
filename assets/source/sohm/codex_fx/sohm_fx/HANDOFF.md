# 索姆特效与技能图标交付

11 张动画图集（合计 56 帧）与 3 张技能图标已绘制并整理，使用原生 image_gen。原始图保留在 raw/。没有用程序绘制特效形状；程序按生成图多数颜色取格、约束调色板、校正对称和透明度。

## 动画图集

| 文件 | 帧数 | 每帧游戏像素 | 对称 |
|---|---:|---|---|
| `sohm_fx_a_bolt.png` | 4 | 10 × 8 | top-bottom |
| `sohm_fx_a_hit.png` | 4 | 14 × 14 | left-right |
| `sohm_fx_q_wave.png` | 6 | 40 × 16 | top-bottom |
| `sohm_fx_q_hit.png` | 4 | 16 × 16 | left-right |
| `sohm_fx_q_flower.png` | 6 | 14 × 12 | left-right |
| `sohm_fx_q_jump.png` | 4 | 10 × 8 | top-bottom |
| `sohm_fx_e.png` | 5 | 24 × 16 | left-right |
| `sohm_fx_e_shield.png` | 6 | 24 × 38 | left-right |
| `sohm_fx_r_bloom.png` | 7 | 40 × 40 | left-right |
| `sohm_fx_r_hit.png` | 4 | 16 × 16 | left-right |
| `sohm_fx_p_glow.png` | 6 | 44 × 48 | left-right |

## 导入与文件

- `pixel_1x/`：实际导入用图，每个动画横向单行排帧，顺序由左到右。按 manifest.json 的 frames 和 cell_1x 切格。
- 根目录同名 `sohm_fx_*.png`：1倍图逐像素放大 8 倍的预览。
- `sohm_icon_skill.png`、`sohm_icon_skill2.png`、`sohm_icon_ult.png`：64×64，分别为潮涌、海潮护佑、潮汐绽放。
- `sohm_fx_*.gif`：各特效的视觉循环预览，统一 110ms；仅用于看图，不代表最终技能时序。
- `contact-sheet.png`：图集及图标总览。
- `manifest.json`：帧数、每帧尺寸、对称方式、原稿布局、取回方式与游戏绑定。
- `generation-prompts.txt`：实际提示词和参考图。
- `reference/import-bindings.json`：输入包给出的绑定关系。
- `validation.json`：技术检查结果。

## 技术校验

11 张 1倍图均逐帧非空，动画至少有两张不同帧；帧数和 cell_1x 均符合清单；透明度只有 0/255。a_bolt、q_wave、q_jump 每帧上下严格对称且朝右，其余每帧左右严格对称。8倍图与1倍图精确对应。水盾和潮汐光环的身体中心区域已清空 alpha。

部分原稿采用分行生成，再按行优先顺序整理为横向图集。每个序列使用共同取样区域，保留其生长、爆开、消退的相对变化。为满足逐格对称，成对像素合并后镜像，优先保留金色/粉色高光；未逐帧单独按外接框放大。原始生成图尺寸不等于最终导入尺寸。

本包是图片素材交付，没有安装进游戏或修改战斗逻辑。实际特效位置、层级、旋转中心和技能播放时序仍需在导入游戏时验证。水花缩到 10×8 等小尺寸后已简化为少量色块，可对照 raw/ 检查。
