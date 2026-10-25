# 巨魔之王 特朗德尔：给 Codex 的特效提示词（第 3 步）

> **这一份是 15 张特效图。** 造型已定（`design/trundle_design.png`：Q 版冰霜巨魔，炸开的红头发和红胡子、亮蓝眼睛、骨头鼻子和獠牙、白毛领、青绿宝石肩甲、灰蓝皮肤、巨大的寒冰狼牙棒）。特朗德尔在游戏里是**高清**的（每个游戏格子里 2×2 个细像素），43 格高、52 格宽（高×宽，含冰棒）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/trundle_size.png`：特朗德尔缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里特朗德尔自己的特效贴图（大多是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用。**特朗德尔是弗雷尔卓德的巨魔之王，特效都是冰和蛮力**：**冰**（浅蓝到深冰蓝、白色棱面）、**寒霜和雪**、他偷走力气时的**红色**、大招吸取的**冷紫蓝色**、被动回血的**淡绿色**；不要光滑的霓虹光束，也不要火。
> - **特效要亮**：每道光、每块冰都有最亮一档或白色的高光，暗底上一眼能看见。
> - **光、寒气、雪尘没有黑描边**（碎冰碴也不要描黑边，用它自己最深的一档）；**只有冰柱（`e_pillar`）这个“东西”有 1 格近黑描边**。
> - **围着人的画面只画外圈、脚下、头上或身后，身体位置留空**，不要盖住人。
> - **对称**：所有画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）——冰柱**正面**看。这次没有弹道。
> - **冰柱**（`e_pillar`）在游戏里要立 4 秒：第 6 帧是「立着」的那一帧，导入时会让它停 3 秒多，所以第 5、6 帧要是完整、稳定的冰柱。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `trundle_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格左右对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/trundle_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/trundle_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 抡冰狼牙棒砸 | `a_hit` |
| 被动「国王的贡品」（并入 W 冰封领域） | 附近敌人死亡时回血；Q 咬中英雄时跳起冻住地面，冰面上攻速、移速更快 | `p_heal` · `w_hop` · `w_domain` · `w_aura` |
| 技能 1 =「利齿撕咬」 | 咬一口：伤害、减速、偷对方的攻击力 | `q_hit` · `q_buff` · `q_sap` · `slow` |
| 技能 2 =「寒冰之柱」 | 在敌方英雄处冒出一根冰柱，周围减速（附加包里冰柱是挡路的地形） | `e_pillar` · `e_hit` · `slow` |
| 大招 =「强权至上」 | 抓住敌方英雄吸取生命、护甲和魔抗 4 秒，顺带在他那冒一根冰柱 | `r_hit` · `r_tick` · `r_chain` · `r_sap` |

连招：**冰柱 → 利齿撕咬马上好**，**咬中英雄 → 冻住地面**，**强权至上 → 利齿撕咬刷新 + 冰柱**，**冰面上击杀 → 回血加倍**。

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、寒气、雪尘没有黑描边，也不要用最深的颜色给形状描一圈边**（冰柱除外）。
- **都是冰和蛮力**：冰、寒霜、红、紫蓝、淡绿；每个形状 2–3 档平涂，冰块用棱角分明的几何面。
- **要亮**：每个形状都有最亮一档或白色的高光。
- 颜色（按每条写的用）：
  - 冰：`#FFFFFF`、`#D8F8FF`、`#9EE6FF`、`#52BFF0`、`#2A80C8`、`#164C8C`；
  - 寒霜·雪：`#FFFFFF`、`#E4F4FA`、`#B8D8E8`、`#7EA8C4`；
  - 力气·红：`#FFE0C8`、`#FF9A6A`、`#F0485A`、`#B81E3C`、`#6E0E26`；
  - 吸取·紫蓝：`#F0ECFF`、`#B8B0FF`、`#7A70E8`、`#4A3CB0`、`#261C68`；
  - 回血·淡绿：`#F0FFE8`、`#B8F0A8`、`#6CD080`、`#2E8C56`；
- 打中、爆发居中画，不旋转；地面上的圈（冰面、寒霜）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、身后的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（15 张）

15 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `trundle_fx_a_hit.png`：普攻：冰棒砸中，3 帧

冰狼牙棒砸在敌人身上：一个白色的闪光，一圈碎冰碴往外崩（参考 common_hiteffect、weapon_trail）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #D8F8FF, #9EE6FF, #52BFF0, #2A80C8, #164C8C), a frost and snow ramp (#FFFFFF, #E4F4FA, #B8D8E8, #7EA8C4).
Effect: AN ICE CLUB STRIKE LANDING, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-blue flash 6 squares across; 2 a ring of angular ice shards bursting out 12 across at mirrored places; 3 the shards further out, dimming into frost dust. everything is the FRELJORD'S ICE and a TROLL KING'S brute strength: faceted pale-blue ice with white facets and deep-blue shade, frost dust and snow, red for the strength he steals, a cold violet-blue for Subjugate's drain; flat shades, crisp angular shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `trundle_fx_p_heal.png`：国王的贡品：附近有人死、回血，5 帧

附近的敌人倒下，特朗德尔吸走一点生命：几缕淡绿色的光从脚下绕着他升起来，头顶几点亮光（参考 r_heal_trail）。光只画在他身体外圈和头顶，**身体位置留空**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale green heal ramp (#F0FFE8, #B8F0A8, #6CD080, #2E8C56), a frost and snow ramp (#FFFFFF, #E4F4FA, #B8D8E8, #7EA8C4).
Effect: A HEALING TRIBUTE ON A BIG TROLL, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), Trundle stands in the middle, not drawn: about 52 squares wide (with his club) and 43 tall: 1 a few pale green motes on the ground at his feet, at both sides; 2 two thin green wisps curling up both sides of him; 3 the wisps at his shoulders, small plus sparkles; 4 a ring of green and white sparkles above his head; 5 the last motes fading. The middle (his body) left empty. everything is the FRELJORD'S ICE and a TROLL KING'S brute strength: faceted pale-blue ice with white facets and deep-blue shade, frost dust and snow, red for the strength he steals, a cold violet-blue for Subjugate's drain; flat shades, crisp angular shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 5 equal 40:44 cells, image size 3200x704 (each cell 640x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `trundle_fx_q_hit.png`：利齿撕咬：咬中，4 帧

特朗德尔一口咬下去：上下两排**米白的大獠牙**咬合（参考 q_teeth、q_bite_marks），中间一下白光，迸出冰碴和一点红色（他吸走对方的力气）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #D8F8FF, #9EE6FF, #52BFF0, #2A80C8, #164C8C), a red rage ramp (#FFE0C8, #FF9A6A, #F0485A, #B81E3C, #6E0E26), a frost and snow ramp (#FFFFFF, #E4F4FA, #B8D8E8, #7EA8C4).
Effect: A TROLL'S BITE, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 two rows of big cream-white troll teeth 14 across, wide open above and below; 2 the jaws snapped shut with a white-blue flash between them; 3 a burst of ice shards and a few red sparks flying out at mirrored places, two faint red bite marks; 4 frost dust and dimming red motes. everything is the FRELJORD'S ICE and a TROLL KING'S brute strength: faceted pale-blue ice with white facets and deep-blue shade, frost dust and snow, red for the strength he steals, a cold violet-blue for Subjugate's drain; flat shades, crisp angular shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `trundle_fx_q_buff.png`：利齿撕咬：特朗德尔变强，4 帧循环

咬到人以后特朗德尔攻击力变高（4 秒）：头顶一个小小的**红色獠牙标记**，往上冒几点红光，一闪一闪。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a red rage ramp (#FFE0C8, #FF9A6A, #F0485A, #B81E3C, #6E0E26).
Effect: A SMALL STRENGTH MARK OVER HIS HEAD, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): two small upward red troll tusks side by side, 8 squares across, with a bright core; frames 1-4 the tusks pulsing brighter and dimmer and a few red motes rising from them. everything is the FRELJORD'S ICE and a TROLL KING'S brute strength: faceted pale-blue ice with white facets and deep-blue shade, frost dust and snow, red for the strength he steals, a cold violet-blue for Subjugate's drain; flat shades, crisp angular shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 4 equal 14:10 cells, image size 896x160 (each cell 224x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `trundle_fx_q_sap.png`：利齿撕咬：被咬的人变弱，4 帧循环

被咬的人攻击力变低：头顶一个**裂开的暗红獠牙**，往下滴冰蓝色的碎屑。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a red rage ramp (#FFE0C8, #FF9A6A, #F0485A, #B81E3C, #6E0E26), an ice ramp (#FFFFFF, #D8F8FF, #9EE6FF, #52BFF0, #2A80C8, #164C8C).
Effect: A WEAKENED MARK OVER THE HEAD, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): one dull dark-red tusk 6 squares tall with a crack down it, pointing down; frames 1-4 small ice-blue flakes dripping down from it and fading. everything is the FRELJORD'S ICE and a TROLL KING'S brute strength: faceted pale-blue ice with white facets and deep-blue shade, frost dust and snow, red for the strength he steals, a cold violet-blue for Subjugate's drain; flat shades, crisp angular shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 4 equal 12:10 cells, image size 768x160 (each cell 192x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `trundle_fx_slow.png`：减速：脚下一圈寒霜，4 帧循环

被冻慢了：脚下一圈薄薄的白霜和冰晶，几点雪花往上飘。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a frost and snow ramp (#FFFFFF, #E4F4FA, #B8D8E8, #7EA8C4), an ice ramp (#FFFFFF, #D8F8FF, #9EE6FF, #52BFF0, #2A80C8, #164C8C).
Effect: A FROST SLOW AT THE FEET, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall): a thin ellipse of white frost 14 wide with small ice crystals on it; frames 1-4 the crystals glinting in turn and a few snowflakes drifting up. everything is the FRELJORD'S ICE and a TROLL KING'S brute strength: faceted pale-blue ice with white facets and deep-blue shade, frost dust and snow, red for the strength he steals, a cold violet-blue for Subjugate's drain; flat shades, crisp angular shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 4 equal 16:8 cells, image size 1024x128 (each cell 256x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `trundle_fx_w_hop.png`：冰封领域：跳起落地的寒霜冲击，4 帧

特朗德尔跳起来落地：脚下一圈白色的寒霜冲击波往外推开，带起雪尘（参考 w_shockwave_scroll、w_nova_snow_edge）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a frost and snow ramp (#FFFFFF, #E4F4FA, #B8D8E8, #7EA8C4), an ice ramp (#FFFFFF, #D8F8FF, #9EE6FF, #52BFF0, #2A80C8, #164C8C).
Effect: A FROST SHOCKWAVE ON LANDING, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall): 1 a white-blue flash ellipse 10 wide; 2 a ring of frost and snow dust 22 wide pushing out; 3 the ring 32 wide, breaking into puffs of snow; 4 the last snow puffs fading at both ends. everything is the FRELJORD'S ICE and a TROLL KING'S brute strength: faceted pale-blue ice with white facets and deep-blue shade, frost dust and snow, red for the strength he steals, a cold violet-blue for Subjugate's drain; flat shades, crisp angular shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 4 equal 36:14 cells, image size 2304x224 (each cell 576x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `trundle_fx_w_domain.png`：冰封领域：地面冻起来，8 帧

他的领地：从他脚下往外**冻出一大片冰面**——蓝白的冰往四周铺开，冰面上有裂纹，边上冒出一圈小冰刺（参考 w_ground、w_ground_cracks、w_speedbuff_ground_glow），最后一帧是铺满的冰面（之后由脚下的 w_aura 接着循环）。**冰面要大**：最后铺满时**横向 80 格、纵向 26 格**，差不多是特朗德尔（连冰棒 52 格宽）的一倍半宽，几乎占满整格（上一版只画到 46 格宽，太小了）。**左右对称**，8 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #D8F8FF, #9EE6FF, #52BFF0, #2A80C8, #164C8C), a frost and snow ramp (#FFFFFF, #E4F4FA, #B8D8E8, #7EA8C4).
Effect: THE GROUND FREEZING OVER, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), centred, the field growing to a BIG ellipse 80 squares wide and 26 tall - nearly the whole cell, one and a half times as wide as the troll standing on it (52 squares with his club): 1 a bright white-blue crack star 14 wide; 2 pale-blue ice spreading 34 wide with white cracks; 3 the ice 56 wide, frost smoke at its edge; 4 the ice 74 wide, a ring of small ice spikes (3-4 squares tall) popping up along its rim; 5 the ice 80 wide, the spikes at full height, the cracks glowing white; 6-7 the frost smoke settling, a few glints; 8 the full frozen ellipse 80 x 26 with its cracks and a thin rim of spikes, calm. Frames 5-8 MUST fill 80 squares across. everything is the FRELJORD'S ICE and a TROLL KING'S brute strength: faceted pale-blue ice with white facets and deep-blue shade, frost dust and snow, red for the strength he steals, a cold violet-blue for Subjugate's drain; flat shades, crisp angular shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 8 equal 84:28 cells, image size 10752x448 (each cell 1344x448, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `trundle_fx_w_aura.png`：冰封领域：脚下的冰面，6 帧循环

领地生效时（8 秒）他脚下一直有一片冰面：蓝白的冰、白色的裂纹一闪一闪，边上几缕寒气往上飘（他在冰面上攻速、移速更快）。**和 w_domain 最后一帧一样大：横向 80 格、纵向 26 格**（上一版只有 34 格宽，太小了）。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #D8F8FF, #9EE6FF, #52BFF0, #2A80C8, #164C8C), a frost and snow ramp (#FFFFFF, #E4F4FA, #B8D8E8, #7EA8C4).
Effect: A BIG FROZEN FIELD UNDER HIM, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall): an ellipse of pale-blue ice 80 squares wide and 26 tall (nearly the whole cell, as big as the domain's last frame) with white cracks and a thin rim of small ice spikes; frames 1-6 the cracks glinting in turn around the ellipse, thin wisps of frost smoke rising from its rim. Every frame MUST fill 80 squares across. everything is the FRELJORD'S ICE and a TROLL KING'S brute strength: faceted pale-blue ice with white facets and deep-blue shade, frost dust and snow, red for the strength he steals, a cold violet-blue for Subjugate's drain; flat shades, crisp angular shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 6 equal 84:28 cells, image size 8064x448 (each cell 1344x448, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `trundle_fx_e_pillar.png`：寒冰之柱：冰柱冒出、立着、碎掉，8 帧

在目标处的地面上**冒出一根巨大的冰柱**（英雄联盟里是挡路的地形）：先是地面裂开冒寒气，一根粗大的多面体冰柱从地里猛地顶上来（深蓝的冰、白色的棱面、底下一圈碎冰和白霜，参考 e_pillar_base、e_pillar_glow、e_pillar_rays、e_pillar_smoke），立着（这一帧导入时会停 3 秒多），最后裂开碎成冰块倒下。**正面看，左右对称**，8 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #D8F8FF, #9EE6FF, #52BFF0, #2A80C8, #164C8C), a frost and snow ramp (#FFFFFF, #E4F4FA, #B8D8E8, #7EA8C4).
Effect: A HUGE ICE PILLAR ERUPTING FROM THE GROUND, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), seen from the FRONT, standing on the ground line at the bottom of the cell: 1 a white-blue crack in the ground 14 wide, frost smoke; 2 jagged ice tips breaking out 10 squares tall; 3 a thick faceted ice pillar shooting up 40 squares tall, 16 wide, deep-blue body with white facets, a ring of broken ice and frost at its foot; 4 the pillar at full height 52 squares, a white flash on its tip; 5 the pillar standing (frost glinting on its facets); 6 the same, standing still (THIS frame is held while it stands); 7 deep cracks running down it, chunks breaking off; 8 it collapsing into a heap of ice chunks and frost smoke. Every ice part has a 1-square near-black outline (it is a solid thing), the frost smoke none. everything is the FRELJORD'S ICE and a TROLL KING'S brute strength: faceted pale-blue ice with white facets and deep-blue shade, frost dust and snow, red for the strength he steals, a cold violet-blue for Subjugate's drain; flat shades, crisp angular shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 8 equal 26:58 cells, image size 3328x928 (each cell 416x928, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `trundle_fx_e_hit.png`：寒冰之柱：冰柱旁边的人，4 帧

冰柱冒出来时站在旁边的英雄：脚下一圈冰刺扎起来、寒气冲上来（他被冻住、跑不动）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #D8F8FF, #9EE6FF, #52BFF0, #2A80C8, #164C8C), a frost and snow ramp (#FFFFFF, #E4F4FA, #B8D8E8, #7EA8C4).
Effect: ICE SPIKES BURSTING AROUND A UNIT'S FEET, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit hit stands in the middle, not drawn: 16 squares wide and 36 tall: 1 a white crack ring at the feet; 2 short ice spikes (4-6 squares) stabbing up in a ring 20 wide around the feet; 3 frost smoke rising 10 squares at both sides; 4 the spikes crumbling into frost. everything is the FRELJORD'S ICE and a TROLL KING'S brute strength: faceted pale-blue ice with white facets and deep-blue shade, frost dust and snow, red for the strength he steals, a cold violet-blue for Subjugate's drain; flat shades, crisp angular shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 4 equal 22:16 cells, image size 1408x256 (each cell 352x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `trundle_fx_r_hit.png`：强权至上：抓住目标吸取，5 帧

特朗德尔伸手把敌人的生命和护甲吸过来：目标身上炸开一圈冷冷的紫蓝色光，一圈冰晶符文合拢，光往上一冲（参考 r_swirl、r_glow、r_wispy_big_scroll、r_cast_wisp）。光只画在外圈，**身体位置留空**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cold violet-blue drain ramp (#F0ECFF, #B8B0FF, #7A70E8, #4A3CB0, #261C68), an ice ramp (#FFFFFF, #D8F8FF, #9EE6FF, #52BFF0, #2A80C8, #164C8C).
Effect: A COLD DRAIN SEIZING A UNIT, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit hit stands in the middle, not drawn: 16 squares wide and 36 tall: 1 a violet-blue flash at the middle 8 across; 2 a ring of angular ice runes 24 wide closing in around the unit; 3 the runes locked, cold violet light flaring up 20 squares at both sides; 4 wisps of violet light streaming up out of the unit; 5 the last motes and a faint ring. The middle (the body) left empty. everything is the FRELJORD'S ICE and a TROLL KING'S brute strength: faceted pale-blue ice with white facets and deep-blue shade, frost dust and snow, red for the strength he steals, a cold violet-blue for Subjugate's drain; flat shades, crisp angular shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 5 equal 26:30 cells, image size 2080x480 (each cell 416x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `trundle_fx_r_tick.png`：强权至上：每秒吸一口，3 帧

大招持续吸取的每一下：几点紫蓝色的光点从目标身上往上被抽走。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cold violet-blue drain ramp (#F0ECFF, #B8B0FF, #7A70E8, #4A3CB0, #261C68).
Effect: A DRAIN PULSE, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small violet-blue flash 5 across; 2 four bright motes pulled up and out at mirrored places; 3 the motes higher, fading. everything is the FRELJORD'S ICE and a TROLL KING'S brute strength: faceted pale-blue ice with white facets and deep-blue shade, frost dust and snow, red for the strength he steals, a cold violet-blue for Subjugate's drain; flat shades, crisp angular shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `trundle_fx_r_chain.png`：强权至上：被吸着的目标身上，6 帧循环

被吸取的 4 秒里目标身上一直缠着**一圈冰晶锁链**，紫蓝的光往上飘（他的力量正被抽走）。锁链只在身体外圈，**身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cold violet-blue drain ramp (#F0ECFF, #B8B0FF, #7A70E8, #4A3CB0, #261C68), an ice ramp (#FFFFFF, #D8F8FF, #9EE6FF, #52BFF0, #2A80C8, #164C8C).
Effect: ICE SHACKLES ON A DRAINED UNIT, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit hit stands in the middle, not drawn: 16 squares wide and 36 tall: a loose ring of angular pale-blue ice chain links around the unit's middle, 24 wide, seen slightly from above; frames 1-6 the links glinting in turn and thin streams of violet-blue light rising off the unit at both sides. The middle (the body) left empty. everything is the FRELJORD'S ICE and a TROLL KING'S brute strength: faceted pale-blue ice with white facets and deep-blue shade, frost dust and snow, red for the strength he steals, a cold violet-blue for Subjugate's drain; flat shades, crisp angular shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 6 equal 26:34 cells, image size 2496x544 (each cell 416x544, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `trundle_fx_r_sap.png`：强权至上：被偷走护甲的人头上，4 帧循环

被偷走护甲、魔抗的人：头顶一个**裂成两半的冰蓝盾牌**，紫光一闪一闪。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cold violet-blue drain ramp (#F0ECFF, #B8B0FF, #7A70E8, #4A3CB0, #261C68), an ice ramp (#FFFFFF, #D8F8FF, #9EE6FF, #52BFF0, #2A80C8, #164C8C).
Effect: A BROKEN SHIELD MARK OVER THE HEAD, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a small pale-blue shield 8 squares tall split down the middle, the halves a square apart; frames 1-4 a violet glow pulsing in the crack and a few motes drifting away. everything is the FRELJORD'S ICE and a TROLL KING'S brute strength: faceted pale-blue ice with white facets and deep-blue shade, frost dust and snow, red for the strength he steals, a cold violet-blue for Subjugate's drain; flat shades, crisp angular shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `trundle_fx_a_hit` | view_effects `league_trundle_a_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `trundle_fx_p_heal` | view_effects `league_trundle_p_heal`（跟随特朗德尔，z 2；左右对称） | 40 × 44 |
| `trundle_fx_q_hit` | view_effects `league_trundle_q_hit`（跟随目标，z 2；左右对称） | 18 × 18 |
| `trundle_fx_q_buff` | view_buffs `league_trundle_q_ad`（跟随特朗德尔，头顶，z 3；左右对称） | 14 × 10 |
| `trundle_fx_q_sap` | view_buffs `league_trundle_q_sap`（跟随目标，头顶，z 3；左右对称） | 12 × 10 |
| `trundle_fx_slow` | view_buffs `league_trundle_q_slow` / `league_trundle_e_slow`（跟随，脚下，z -1；左右对称） | 16 × 8 |
| `trundle_fx_w_hop` | view_effects `league_trundle_w_hop`（地上，z -1，不跟随；左右对称） | 36 × 14 |
| `trundle_fx_w_domain` | view_effects `league_trundle_w_domain`（大表，地上，z -1，不跟随；左右对称） | 84 × 28 |
| `trundle_fx_w_aura` | view_buffs `league_trundle_w_on`（跟随特朗德尔，脚下，z -1；左右对称） | 84 × 28 |
| `trundle_fx_e_pillar` | view_effects `league_trundle_e_pillar`（大表，地上，z 1，不跟随；左右对称） | 26 × 58 |
| `trundle_fx_e_hit` | view_effects `league_trundle_e_hit`（跟随目标，z 2；左右对称） | 22 × 16 |
| `trundle_fx_r_hit` | view_effects `league_trundle_r_hit`（跟随目标，z 2；左右对称） | 26 × 30 |
| `trundle_fx_r_tick` | view_effects `league_trundle_r_tick`（跟随目标，z 2；左右对称） | 14 × 14 |
| `trundle_fx_r_chain` | view_effects `league_trundle_r_chain`（跟随目标，z 2；左右对称） | 26 × 34 |
| `trundle_fx_r_sap` | view_buffs `league_trundle_r_sap`（跟随目标，头顶，z 3；左右对称） | 12 × 12 |

- 两张表：`asset/league/effects/league_trundle_fx`（小的）和 `league_trundle_big`（w_domain、e_pillar），tag = 名字（build_trundle.py 的 views；buff 的 tag：w_on → w_aura、q_slow / e_slow → slow、q_ad → q_buff）。e_pillar 的第 6 帧拉长到冰柱立满 e_t（240 tick）；r_chain 由 casted 每 60 tick 播一次（循环 1 秒）。
- 全部断言左右对称。
- 用 `pixel_1x/` 切格（import_yorick_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
