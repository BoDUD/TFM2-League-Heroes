# 正义天使 凯尔：升阶变身的翅膀和 12 级强化特效（给 Codex 的提示词）

> 凯尔在 5 / 8 / 12 级升阶（升腾、炽诚、超凡）。数据里待机、走路、受击、死亡的动作是引擎选的，换不了，所以「变身」用**跟着她的翅膀画面**来做：**每升一阶，她身后多一对翅膀**（英雄联盟里凯尔升级时翅膀也是一对变三对，`refs/lol_kayle_wings.png` 左边一对、右边三对）；12 级时她的技能特效换成**更大更亮的超凡版**。
> - 这一份是 **11 张特效图**：3 张翅膀（每阶一层，三层叠在一起）+ 8 张 12 级强化特效。
> - 造型参考 `design/kayle_idle.png`（她的待机 ×8，青色十字是站位点）和 `design/kayle_size.png`（×4，10 格刻度，旁边是原版斗士）：凯尔 31×49 格（连头后一对淡蓝色小翅膀），站位点在她脚底上方约 9 格。**翅膀画在她身后**（游戏里画在人物下面一层），三层的翅膀根都在她背后同一个点：**格子正中间那一点 = 她背上的翅膀根（站位点正上方 20 格）**。
> - 现在的特效 `now/league_kayle_effects.png`（游戏里的样子 ×3）：12 级的 8 张就是把这些「升级」——同样的形状和用途，更大一圈、更亮、加白金色的火焰和光芒。
> - 颜色：**圣光金** `#FFFFFF, #FFF6C8, #FFE27A, #F7B931, #C47A12`；**圣火橙** `#FFFFFF, #FFE6A8, #FFB347, #F07A1C, #B8460C`；**超凡白金**（12 级）`#FFFFFF, #FFFBEA, #FFF0B0, #DDEBFF, #9CC4FF`。光和火焰都不描黑边。
> - **对称（红色方不会镜像特效）**：翅膀和打中 / 爆炸都**严格左右对称**（逐格）；飞出去的火焰弹、焰浪、圣剑、星火画成朝右飞，**严格上下对称**（往左飞时会整张转 180°）；地上的 `q_blast_x` 上下左右都对称。
> - 每张一个 PNG，文件名 `kayle_fx_<名字>.png`，排版按每条写的格子来（1 格 = 16 像素）；**同时交一份 1 格 = 1 像素的 `pixel_1x/`**（透明度只有 0 和 255，对称的逐格对称）；生图原稿放 `raw/`；**最后**写 `HANDOFF.md`。交付到 `outputs/kayle-ascend/` 或打成 `kayle_ascend_done.zip`。**请用生图画，不要用代码拼方块。**

## 每张图

| 文件 | 内容 | 格子（1 格 = 1 游戏像素） | 帧 |
|---|---|---|---|
| `kayle_fx_wings1.png` | **5 级翅膀（第一层）**：她背后**腰部往下斜伸出的一对金色光翼**（中等大小，羽片一片片的，金色带白芯，边缘发光），左右对称地张开，在她两侧露出来；**中间 12 格宽的人形位置留空**（翅膀从人背后伸出来，别盖住她）。每帧羽片轻轻扇动 1 格 | 60×44，翅膀根在格子正中 | 4 帧循环 |
| `kayle_fx_wings2.png` | **8 级翅膀（第二层，叠在第一层上）**：**肩膀两侧横着张开的一对更大的火焰翼**（圣火橙，羽尖带火苗），比第一层宽、位置高一点；中间人形位置留空；只画这一对（第一层另外画好了） | 76×48，翅膀根在格子正中 | 4 帧循环 |
| `kayle_fx_wings3.png` | **12 级翅膀（第三层）+ 光环**：**头顶两侧往上斜伸的一对白金火焰大翼**（超凡白金，燃着白色和淡蓝的圣火），加一圈**悬在她头顶的金色光环**（光环在翅膀根上方 26 格）；中间人形位置留空 | 84×64，翅膀根在格子正中 | 4 帧循环 |
| `kayle_fx_bolt_x.png` | 12 级的普攻火焰弹：比现在的 `bolt` 大一圈（约 18×9），白金色的火芯、金橙色的火焰尾，朝右飞，**上下对称** | 20×12，弹头在右边第 1 格 | 4 帧循环 |
| `kayle_fx_wave_x.png` | 12 级的炽诚焰浪：比现在的 `wave` 大（约 16×26），白金色的竖立火焰波，朝右推进，**上下对称** | 18×28，波前在右边第 1 格 | 4 帧循环 |
| `kayle_fx_q_sword_x.png` | 12 级的 Q 星体之剑：比现在的 `q_sword` 大（约 32×14），白金色的光剑、剑身燃着淡蓝白火，后面拖金色光尾，朝右飞，**上下对称** | 34×16，剑尖在右边第 1 格 | 4 帧循环 |
| `kayle_fx_e_bolt_x.png` | 12 级的 E 星火：比现在的 `e_bolt` 大（约 24×14），白金火球带一圈金色火焰，朝右飞，**上下对称** | 26×16，火球前沿在右边第 1 格 | 4 帧循环 |
| `kayle_fx_bolt_hit_x.png` | 12 级火焰弹打中：比现在的 `bolt_hit` 大（约 20），白金色火花炸开 + 一圈金色光环，**左右对称** | 22×22，居中 | 5 帧 |
| `kayle_fx_e_hit_x.png` | 12 级 E 打中：比现在的 `e_hit` 大（约 26×30），白金色的火焰往上窜、金色火星四散，**左右对称** | 28×32，居中 | 6 帧 |
| `kayle_fx_q_blast_x.png` | 12 级 Q 爆开（地上，从斜上方看的扁椭圆）：比现在的 `q_blast` 大（约 50×32），白金色圣光环炸开、中间几道金色光柱往上射，**上下左右都对称** | 52×34，居中 | 7 帧 |
| `kayle_fx_e_blast_x.png` | 12 级 E 的爆炸（竖立的火焰爆发）：比现在的 `e_blast` 大（约 50×56），白金和金橙色的大火球炸开再散成火星，**左右对称** | 52×58，爆炸底部在格子底边往上 4 格 | 7 帧 |

## 提示词（每张都用这一段开头，再接每张的 Effect / Layout）

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire or wings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a holy gold ramp (#FFFFFF, #FFF6C8, #FFE27A, #F7B931, #C47A12), a holy fire ramp (#FFFFFF, #FFE6A8, #FFB347, #F07A1C, #B8460C) and, for the level-12 versions, a transcendent white-gold ramp (#FFFFFF, #FFFBEA, #FFF0B0, #DDEBFF, #9CC4FF).
```

- wings1：`Effect: a PAIR OF GOLDEN LIGHT WINGS spreading from a figure's back, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame square for square: the wing root at the cell's exact center; each wing sweeps out and DOWN at about 30 degrees below horizontal, 24 squares long, made of 5-6 overlapping feather plates in gold with white cores and glowing edges; the middle 12 squares across (the figure's place) EMPTY; the feathers flutter one square frame to frame. Layout: one horizontal row of 4 equal cells, each 60x44 squares (960x704 px); the wing root on the center of every cell. Transparent background. No figure, no gaps, no borders, no labels.`
- wings2：`Effect: a PAIR OF LARGE HOLY FIRE WINGS spreading level from a figure's shoulders, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT: the wing root at the cell's exact center, each wing reaching out sideways and slightly up, 32 squares long, broad feathers of orange-gold fire with flame tips and white cores; the middle 12 squares (the figure) EMPTY; the flames flicker frame to frame. Layout: one row of 4 cells, each 76x48 squares (1216x768 px); the root on the center of every cell. Transparent background.`
- wings3：`Effect: a PAIR OF TRANSCENDENT WHITE-GOLD FLAME WINGS rising from a figure's upper back plus a HALO, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT: the wing root at the cell's exact center, each wing sweeping UP and out at about 45 degrees, 34 squares long, burning with white and pale blue holy flame over gold; a golden halo ring 14 squares wide and 4 tall floating 26 squares above the root; the middle 12 squares (the figure) EMPTY; the flames rise frame to frame. Layout: one row of 4 cells, each 84x64 squares (1344x1024 px); the root on the center of every cell. Transparent background.`
- bolt_x / wave_x / q_sword_x / e_bolt_x：照上表的形状，`flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is turned 180 degrees)`，格子照上表，前沿在右边第 1 格、上下居中。
- bolt_hit_x / e_hit_x / e_blast_x：照上表，`SYMMETRIC LEFT TO RIGHT in every frame, square for square`，格子照上表。
- q_blast_x：照上表，`a holy shockwave on the ground seen from above at an angle, SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM`，格子照上表。

## 附图

| 文件 | 内容 |
|---|---|
| `design/kayle_idle.png` | 凯尔待机 ×8，青色十字是站位点（翅膀根在它正上方 20 格） |
| `design/kayle_size.png` | 凯尔 ×4、10 格刻度、原版斗士 |
| `now/league_kayle_effects.png` | 她现在的特效（游戏里的样子 ×3）：12 级强化版就是把这些放大、加亮 |
| `refs/lol_kayle_wings.png` | 英雄联盟的凯尔：左一对翅膀、右三对（只看翅膀怎么一对对加上去；本地参考，不要提交） |
| `refs/lol_fx_ref.png` | 英雄联盟凯尔的翅膀火焰、圣光、剑光贴图（灰度形状为主；本地参考） |

## Claude 导入时（给 Claude 看）

- 用 `pixel_1x/` 切格，断言对称；翅膀三层绑到 view_buffs：`rank5` → wings1、`rank8` → wings2、新加的 `form3`（和 `rank12` 一起加）→ wings3（`rank12` 自己还是圣火 `exalted`），z −1，锚点 = 格子中心放在站位点上方 20 格。
- 12 级强化：数据里每个 `bolt` / `wave` / `q_sword` / `e_bolt` 弹道和 `bolt_hit` / `e_hit` / `q_blast` / `e_blast` 画面外面包一层 `SwitchByBuff rank12`，换成 `*_x` 的名字（弹道子树只有 2–7 个节点，技能树多十来个节点）。
