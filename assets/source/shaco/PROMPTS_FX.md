# 恶魔小丑 萨科：给 Codex 的特效提示词（第 3 步）

> **这一份是 16 张特效图。** 造型已定（`design/shaco_design.png`，8 倍，你画的 46 格 v4 A 版）。幻像分身就是萨科本人，Claude 用导入的动作帧做，这里不用画。
> - 大小对照 `design/shaco_size.png`：定稿造型放大 4 倍，站在红色脚底线上，上面是 10 格一段的刻度，右边是原版忍者。萨科 37×46 格（帽尖到鞋底 46 格），原版英雄约 31–36 格高。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里萨科自己的特效贴图（多数是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行（Q 的烟和毛笔圈、E 的毒刃和匕首、R 的爆炸和魔盒的光），只在本地用，不要提交。颜色按下面写的色阶。
> - 特效照下面第 1–16 条和「所有特效图的规则」画，每张一个 PNG，文件名 `shaco_fx_<名字>.png`，排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方）。最好打成一个 zip 放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「背刺」 | 匕首划砍；打被控制（比如被恐惧）的敌方英雄时多一刀背刺 | `shaco_fx_hit` · `shaco_fx_bs_hit` |
| 普攻里的 E「双面毒刃」 | 每 8 秒，下一次普攻改为掷出毒刃：魔法伤害、减速 | `shaco_fx_e_shiv` · `shaco_fx_e_hit` |
| 技能 1 = Q「欺诈魔术」 | 原地化成一团烟消失、隐身，闪到目标身后现身；下一次普攻是必定暴击的背刺 | `shaco_fx_q_vanish` · `shaco_fx_q_appear` · `shaco_fx_q_hit` |
| 技能 2 = W「惊吓魔盒」 | 把魔盒扔到敌人脚下，落地后弹开：周围敌人恐惧（头顶的笑脸漩涡），魔盒接着 5 秒每 0.5 秒射一下周围的敌人 | `shaco_fx_w_throw` · `shaco_fx_w_land` · `shaco_fx_w_box` · `shaco_fx_fear` · `shaco_fx_shot_hit` |
| 大招 = R「幻像」 | 萨科一闪隐身，敌方英雄身后出现他的分身（Claude 用萨科的帧做），跟着萨科一起砍；5 秒后或目标死亡时分身爆炸，留下三个小魔盒，再吓人、射 2.5 秒 | `shaco_fx_r_poof` · `shaco_fx_r_boom` · `shaco_fx_r_burn` · `shaco_fx_r_mini` · `shaco_fx_fear` · `shaco_fx_shot_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、烟、火花没有黑描边，也不要用最深的颜色给形状描一圈边**（特效和角色相反）。
- **只有魔盒和弹出来的小丑头是「物体」**（`w_throw`、`w_land`、`w_box`、`r_mini`）：像角色一样画 1 格近黑描边 `#0F0419`，用萨科自己的颜色，小丑头照造型图的帽子和面具画（缩小版）。
- 颜色（按每条写的用）：
  - 恶魔紫（萨科的魔法：烟里的光、恐惧、爆炸、魔盒的射击）：`#FFFFFF`、`#F2D9FF`、`#C98CF0`、`#9447D1`、`#5E2491`、`#2E0F4D`；
  - 毒绿（毒刃）：`#F4FFD6`、`#C8F27A`、`#86D23F`、`#4C9A2A`、`#1F5419`；
  - 刀光银（匕首划光、毒刃的刀身）：`#FFFFFF`、`#E6E8F0`、`#B8C4D8`、`#7F8CA8`、`#4A5470`；
  - 血红（背刺、暴击）：`#FFF2F2`、`#FF9A9A`、`#FC2D3F`、`#B3112D`、`#6A0A1E`；
  - 烟（消失和爆炸的烟）：`#E8E0F0`、`#A89BB8`、`#6E6280`、`#3E3450`、`#1E1828`；尘土：`#C8BCA8`、`#9A8C78`、`#6E6252`；
  - 魔盒和小丑头：#0F0419 (outline), #1D264A, #334782, #475C75 (navy), #6A0A1E, #B3112D, #FC2D3F (red), #8A5D25, #F3BF27, #FFF2A3 (gold), #D1CBDE, #F7F7F8 (mask white), #03A7E9, #B8FAFF (eyes)。
- **魔盒在所有图里是同一个样子**：深蓝色的小方盒，侧面红金两色的菱形花纹，金色的边，右侧一个金色摇把；弹出来的小丑头是萨科的缩小版（白面具、冰青色眼睛、咧嘴的牙、深蓝和红色的双角帽、金铃）。
- **飞行类特效朝右画，而且上下对称**（毒刃 `e_shiv`）：游戏会把它转到飞行方向；翻滚的盒子 `w_throw` 每帧转 90 度。
- 命中、爆炸、范围特效居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）；落在地上的魔盒、烟，地面在格子底部。
- 套在角色身上的特效（消失、现身、施法的烟）：格子里留出空的人形位置，不要画人；恐惧画在头顶，不挡脸。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（16 张）

16 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `shaco_fx_hit.png`：普攻命中，5 帧

匕首划中目标：一道银白色的短斜划光，几点银色火花往外飞（参考 common_JesterDagger 的刃光）。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from a steel ramp (#FFFFFF, #E6E8F0, #B8C4D8, #7F8CA8, #4A5470).
Effect: a DAGGER SLASH HIT, 5 frames: 1 a small white flash at the center; 2 a short bright diagonal slash of light (a narrow crescent, white core, pale steel edge) across the center from upper left to lower right; 3 the slash at full length with 3-4 small steel sparks flying outward; 4 the slash thins, the sparks fly further and dim; 5 a few grey specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `shaco_fx_q_hit.png`：Q 后的背刺（必定暴击）命中，6 帧

背刺暴击：两道交叉的深红色大划痕（X 形，白芯、红边），中心炸开一圈紫红色的光，四周飞出红色和紫色的碎片。比普攻命中大一倍，一看就是暴击。约 26 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from a crimson ramp (#FFF2F2, #FF9A9A, #FC2D3F, #B3112D, #6A0A1E) with the demon violet (#FFFFFF, #F2D9FF, #C98CF0, #9447D1, #5E2491, #2E0F4D).
Effect: a BACKSTAB CRITICAL HIT, 6 frames: 1 a bright white flash at the center; 2 two long crossing slashes of light (an X, white cores, crimson edges) filling 80% of the cell; 3 the X at full size, a ring of violet light bursts around the center and 6-8 crimson and violet shards fly outward; 4 the X shrinks, the ring widens and thins; 5 the shards scatter and dim to deep red; 6 a few crimson specks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `shaco_fx_bs_hit.png`：被动 背刺（打被控制的英雄）命中，5 帧

被动背刺：打中被恐惧、被控制的英雄时多出的一刀：一道深红色的短竖划痕加一小团紫色的火星，比 Q 的暴击小。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from a crimson ramp (#FFF2F2, #FF9A9A, #FC2D3F, #B3112D, #6A0A1E) with the demon violet (#FFFFFF, #F2D9FF, #C98CF0, #9447D1, #5E2491, #2E0F4D).
Effect: a BACKSTAB HIT, 5 frames: 1 a small white flash; 2 a short vertical slash of light (white core, crimson edge) through the center; 3 a small burst of violet sparks around it; 4 the slash fades, the sparks drift outward; 5 a few violet specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `shaco_fx_e_shiv.png`：E 双面毒刃：飞出去的毒刃（飞行中循环），4 帧

掷出的毒刃：一把小匕首刀尖朝右平飞，刀身裹着一层绿色毒光，后面拖两三格绿色的毒雾尾巴（参考 Shaco_Base_E_Bullet_Front、common_JesterDagger）。上下对称。约 12 格长、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from a steel ramp (#FFFFFF, #E6E8F0, #B8C4D8, #7F8CA8, #4A5470) with poison green (#F4FFD6, #C8F27A, #86D23F, #4C9A2A, #1F5419).
Effect: a THROWN POISON DAGGER flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a small dagger, point to the right (a 6-square silver blade with a bright edge, a 2-square dark hilt), wrapped in a thin glow of poison green, a short trail of green mist and drops behind it to the left; the glow and the trail flicker each frame (the dagger itself does not move).
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 2048x256 (each cell 512x256); the dagger on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `shaco_fx_e_hit.png`：E 毒刃命中（减速），5 帧

毒刃扎中：一团绿色的毒液溅开，几滴毒液往下滴（表示减速和中毒）。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from poison green (#F4FFD6, #C8F27A, #86D23F, #4C9A2A, #1F5419).
Effect: a POISON SPLASH, 5 frames: 1 a small bright green flash at the center; 2 a splash of green poison bursts outward (blobs and drops, a pale-green core); 3 the splash at full size, drops flying; 4 the drops fall down and the splash breaks up; 5 a few green drops near the bottom.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `shaco_fx_fear.png`：恐惧（被吓到的单位头顶，约 1 秒），8 帧

被惊吓魔盒吓到：头顶一个紫色的小漩涡，里面一张小小的咧嘴笑脸（萨科的笑：两只亮点眼睛、一道弯弯的牙），转着、一闪一闪。8 帧约 1 秒，第 1 帧出现、第 8 帧散去。约 16 格宽、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from the demon violet (#FFFFFF, #F2D9FF, #C98CF0, #9447D1, #5E2491, #2E0F4D).
Effect: a FEAR above a head, 8 frames: 1 a small violet swirl appears; 2-7 a swirling spiral of violet light (wider than tall) turning a little each frame, inside it a tiny grinning face made of light (two bright dots for eyes, a curved row of pale teeth) that flickers; 8 the swirl breaks into a few violet specks.
Layout: one horizontal row of 8 equal cells, each 4 wide to 3 tall, image size 2048x192 (each cell 256x192); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `shaco_fx_shot_hit.png`：魔盒射出的弹打中敌人，4 帧

魔盒每 0.5 秒射一下，打中周围的敌人：一个小小的紫色爆点。约 10 格，很多个同时出现，不要太大。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from the demon violet (#FFFFFF, #F2D9FF, #C98CF0, #9447D1, #5E2491, #2E0F4D).
Effect: a SMALL MAGIC HIT, 4 frames: 1 a small white-violet flash; 2 a tiny star burst of violet light; 3 it breaks into 4 sparks; 4 two violet specks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `shaco_fx_q_vanish.png`：Q 欺诈魔术：原地消失的烟（地面，不跟随），6 帧

萨科隐身闪走时留在原地的一团烟：一圈深紫灰色的烟从脚下往上涌起、裹住人形的位置，里面闪几点紫色的光，然后散开；地上一道紫色的毛笔圈（参考 Shaco_Base_Q_Smoke_SharpShape_02、Shaco_Base_Q_Rune_01）。中间不要画人。约 30 格宽、34 格高，地面在格子底部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from smoke (#E8E0F0, #A89BB8, #6E6280, #3E3450, #1E1828) with the demon violet (#FFFFFF, #F2D9FF, #C98CF0, #9447D1, #5E2491, #2E0F4D).
Effect: a VANISHING PUFF where a figure stood (do NOT draw the figure), 6 frames: 1 a flat violet brush-stroke ring flashes on the ground at the bottom (an ellipse twice as wide as tall) and the first puffs of dark violet-grey smoke rise from it; 2 a column of round smoke puffs billows up to the figure's height; 3 the smoke at full size, a few bright violet sparkles inside it; 4 the puffs break apart and drift outward; 5 thin wisps and the ring fading; 6 a few smoke specks.
Layout: one horizontal row of 6 equal cells, each 7 wide to 8 tall, image size 2688x512 (each cell 448x512); the ground line near the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `shaco_fx_q_appear.png`：Q 欺诈魔术：在目标身后出现（不跟随），5 帧

萨科在目标身后现身：一小团紫色的烟从中间往外一炸、很快散掉，地上一圈小的紫色毛笔圈。比消失的烟小。中间不要画人。约 24 格宽、28 格高，地面在格子底部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from smoke (#E8E0F0, #A89BB8, #6E6280, #3E3450, #1E1828) with the demon violet (#FFFFFF, #F2D9FF, #C98CF0, #9447D1, #5E2491, #2E0F4D).
Effect: a SMALL REAPPEARING PUFF around a figure's place (do NOT draw the figure), 5 frames: 1 a violet flash at the middle; 2 a ring of dark violet-grey smoke puffs bursts outward from the middle and a small violet brush-stroke ring appears on the ground; 3 the puffs spread and thin; 4 wisps and specks; 5 faint specks.
Layout: one horizontal row of 5 equal cells, each 6 wide to 7 tall, image size 1920x448 (each cell 384x448); the ground line near the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `shaco_fx_r_poof.png`：R 幻像：萨科施法时的一团烟和紫光（不跟随），6 帧

放大招：萨科身边一圈紫色和红色的烟花一样的光点炸开，一团深紫色的烟裹住人形的位置（他短暂隐身），地上一道紫色的毛笔圈（参考 Shaco_Base_R_Rune_01、Shaco_Base_R_Glow01）。比 Q 的烟更大更亮。中间不要画人。约 32 格宽、36 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from smoke (#E8E0F0, #A89BB8, #6E6280, #3E3450, #1E1828) with the demon violet (#FFFFFF, #F2D9FF, #C98CF0, #9447D1, #5E2491, #2E0F4D) and crimson (#FFF2F2, #FF9A9A, #FC2D3F, #B3112D, #6A0A1E).
Effect: a HALLUCINATION BURST around a figure's place (do NOT draw the figure), 6 frames: 1 a bright violet flash at the middle and a violet brush-stroke ring on the ground; 2 a burst of violet and crimson sparkles flies out in all directions and dark violet smoke puffs billow up around the figure's place; 3 the smoke at full size, sparkles further out; 4 the smoke breaks apart, the sparkles twinkle; 5 wisps; 6 a few violet specks.
Layout: one horizontal row of 6 equal cells, each 8 wide to 9 tall, image size 3072x576 (each cell 512x576); the ground line near the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `shaco_fx_r_burn.png`：R 幻像爆炸打中的每个敌人，5 帧

幻像爆炸打中：一团紫黑色的火焰在敌人身上一窜就灭（参考 Shaco_Base_R_Ball_Lightning）。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from the demon violet (#FFFFFF, #F2D9FF, #C98CF0, #9447D1, #5E2491, #2E0F4D).
Effect: a DARK MAGIC BURN, 5 frames: 1 a violet flash at the center; 2 a burst of violet flames (a pale-violet core, deep purple edges) licking upward; 3 the flames at full size with a few crackling violet sparks; 4 the flames break into wisps rising; 5 a few purple specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `shaco_fx_w_throw.png`：W 惊吓魔盒：扔出去的盒子（飞行中循环），4 帧

抛出去的惊吓魔盒：一个小方盒子在空中翻滚（每帧转 90 度），样子和下面落地的魔盒一样（深蓝底、红金菱形花纹、金边、侧面一个摇把）。约 10 格见方。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from the box's colours (#0F0419 (outline), #1D264A, #334782, #475C75 (navy), #6A0A1E, #B3112D, #FC2D3F (red), #8A5D25, #F3BF27, #FFF2A3 (gold), #D1CBDE, #F7F7F8 (mask white), #03A7E9, #B8FAFF (eyes)).
Effect: a SMALL TUMBLING BOX, 4 frames, a seamless loop: a small cube toy box drawn like a game object (a 1-square dark outline #0F0419): dark navy sides with a red-and-gold diamond pattern, gold edges, a little gold crank handle on its side; it turns a quarter turn each frame as it tumbles through the air.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; the box centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `shaco_fx_w_land.png`：W 魔盒落地（地面，不跟随），5 帧

盒子落在敌人脚下：盒子砸到地上弹一下，扬起一圈小尘土；落地后盒子静止，下一张 `w_box` 从这个样子接着弹开。约 24 格宽、16 格高，地面在格子底部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from the box's colours (#0F0419 (outline), #1D264A, #334782, #475C75 (navy), #6A0A1E, #B3112D, #FC2D3F (red), #8A5D25, #F3BF27, #FFF2A3 (gold), #D1CBDE, #F7F7F8 (mask white), #03A7E9, #B8FAFF (eyes)) with dust (#C8BCA8, #9A8C78, #6E6252).
Effect: a TOY BOX LANDING on the ground, 5 frames: 1 the small cube box (dark navy with a red-and-gold diamond pattern, gold edges, a gold crank on its right side, a 1-square dark outline, about 10 squares wide) drops in from above; 2 it hits the ground squashed a little, a flat ring of dust puffs out to both sides; 3 it bounces up 2 squares, the dust spreads; 4 it settles on the ground, the dust thins; 5 the box sits still, faint dust.
Layout: one horizontal row of 5 equal cells, each 3 wide to 2 tall, image size 1920x256 (each cell 384x256); the ground line near the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `shaco_fx_w_box.png`：W 惊吓魔盒弹开、射击 5 秒、消失（地面，不跟随），10 帧

魔盒弹开：盖子弹飞，弹簧上弹出一个小丑头（萨科的样子：白面具、冰青色眼睛、咧嘴笑，深蓝和红色的双角帽带金铃），嘴里冒紫光。1–3 帧弹开，4–7 帧循环（小丑头在弹簧上左右晃、嘴里一闪一闪地射出紫光，导入时重复到 5 秒），8–10 帧小丑头缩回去、盒子化成一团紫烟消失。盒子在格子底部中间，和 `w_land` 最后一帧同一个盒子、同一个位置。约 24 格宽、32 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from the box's colours (#0F0419 (outline), #1D264A, #334782, #475C75 (navy), #6A0A1E, #B3112D, #FC2D3F (red), #8A5D25, #F3BF27, #FFF2A3 (gold), #D1CBDE, #F7F7F8 (mask white), #03A7E9, #B8FAFF (eyes)) with the demon violet (#FFFFFF, #F2D9FF, #C98CF0, #9447D1, #5E2491, #2E0F4D) and smoke (#E8E0F0, #A89BB8, #6E6280, #3E3450, #1E1828).
Effect: a JACK-IN-THE-BOX on the ground, 10 frames: 1 the small cube box (the same as the landing box: dark navy, red-and-gold diamond pattern, gold edges, a gold crank on its right side, about 10 squares wide, a 1-square dark outline) sits on the ground, the lid starting to rattle; 2 the lid flies open and a coiled spring shoots up; 3 a grinning jester head pops out on the spring: a white mask with two glowing ice-cyan eyes and a wide toothy grin, a two-horned jester hat (one horn navy, one red, a gold bell on each tip); 4-7 a seamless loop: the head bobs left and right on the spring and its grin flashes violet light as it shoots (violet sparks at the mouth in frames 5 and 7); 8 the head sinks back into the box; 9 the box bursts into a puff of dark violet smoke; 10 faint smoke specks. Everything stands on the ground at the bottom middle of the cell; the box is in exactly the same place in every frame.
Layout: one horizontal row of 10 equal cells, each 3 wide to 4 tall, image size 3840x512 (each cell 384x512); the ground line near the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `shaco_fx_r_boom.png`：R 幻像爆炸（地面，不跟随，大图），7 帧

幻像到时间或目标死亡时爆炸：一团紫黑色的魔法爆炸从中间炸开，地上一圈紫色的冲击波扩到整个范围（宽是高的 2 倍），往上窜起紫色的火焰和红色的火星，最后剩一圈紫烟（参考 Shaco_Base_R_Shockwave_1、Shaco_Base_R_Ball_Lightning、Shaco_Base_R_Rune_01）。约 60 格宽、44 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from the demon violet (#FFFFFF, #F2D9FF, #C98CF0, #9447D1, #5E2491, #2E0F4D) with crimson (#FFF2F2, #FF9A9A, #FC2D3F, #B3112D, #6A0A1E) and smoke (#E8E0F0, #A89BB8, #6E6280, #3E3450, #1E1828).
Effect: a DARK MAGIC EXPLOSION on the ground (seen from above at an angle), 7 frames: 1 a bright white-violet flash at the middle of the ground ellipse; 2 a ball of violet fire bursts up from it, a ring of violet light spreads on the ground (an ellipse twice as wide as tall); 3 the fireball at full size with crimson sparks flying out, the ground ring reaching the edges of the cell; 4 the fire breaks into rising violet flames and dark smoke; 5 the smoke billows, the ring fades; 6 wisps of dark violet smoke; 7 a few specks.
Layout: one horizontal row of 7 equal cells, each 4 wide to 3 tall, image size 3584x384 (each cell 512x384); the ground ellipse centered at the bottom third of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `shaco_fx_r_mini.png`：R 爆炸后的三个小魔盒（地面，不跟随，大图），10 帧

爆炸后留下三个小惊吓魔盒（和 `w_box` 一样的盒子，小一号），在爆炸点周围排成三角形（左、右、后上），一起弹开、吓人、射击 2.5 秒后消失。1–3 帧弹开，4–7 帧循环（导入时重复到 2.5 秒），8–10 帧缩回、化成紫烟。约 64 格宽、32 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from the box's colours (#0F0419 (outline), #1D264A, #334782, #475C75 (navy), #6A0A1E, #B3112D, #FC2D3F (red), #8A5D25, #F3BF27, #FFF2A3 (gold), #D1CBDE, #F7F7F8 (mask white), #03A7E9, #B8FAFF (eyes)) with the demon violet (#FFFFFF, #F2D9FF, #C98CF0, #9447D1, #5E2491, #2E0F4D) and smoke (#E8E0F0, #A89BB8, #6E6280, #3E3450, #1E1828).
Effect: THREE SMALL JACK-IN-THE-BOXES on the ground around the middle of the cell (seen from above at an angle: one at the left, one at the right, one at the back - higher up - in the middle, the middle itself empty), each a smaller copy of a toy box (dark navy, red-and-gold diamond pattern, gold edges, about 7 squares wide, a 1-square dark outline), 10 frames: 1 the three boxes sit on the ground, rattling; 2 their lids fly open; 3 three small grinning jester heads (a white mask, glowing ice-cyan eyes, a toothy grin, a navy-and-red two-horned hat) pop out on springs; 4-7 a seamless loop: the heads bob and their grins flash violet sparks; 8 the heads sink back; 9 each box bursts into a puff of violet smoke; 10 faint specks. The boxes stay exactly in the same places in every frame.
Layout: one horizontal row of 10 equal cells, each 2 wide to 1 tall, image size 5120x256 (each cell 512x256); the three boxes in the same places in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `shaco_fx_hit` | view_effects `league_shaco_hit`（跟随） | 14 |
| `shaco_fx_q_hit` | view_effects `league_shaco_q_hit`（跟随） | 26 |
| `shaco_fx_bs_hit` | view_effects `league_shaco_bs_hit`（跟随） | 18 |
| `shaco_fx_e_shiv` | view_projectiles `league_shaco_e_shiv`（朝右，游戏转到飞行方向） | 12 × 6 |
| `shaco_fx_e_hit` | view_effects `league_shaco_e_hit`（跟随） | 16 |
| `shaco_fx_fear` | view_effects `league_shaco_fear`（跟随，画在人物上面） | 16 × 12 |
| `shaco_fx_shot_hit` | view_effects `league_shaco_shot_hit`（跟随） | 10 |
| `shaco_fx_q_vanish` | view_effects `league_shaco_q_vanish`（施法者身上，不跟随） | 30 × 34 |
| `shaco_fx_q_appear` | view_effects `league_shaco_q_appear`（施法者身上，不跟随） | 24 × 28 |
| `shaco_fx_r_poof` | view_effects `league_shaco_r_poof`（施法者身上，不跟随） | 32 × 36 |
| `shaco_fx_r_burn` | view_effects `league_shaco_r_burn`（跟随） | 18 |
| `shaco_fx_w_throw` | view_projectiles `league_shaco_w_throw`（抛物线，游戏会转到飞行方向） | 10 |
| `shaco_fx_w_land` | view_effects `league_shaco_w_land`（地面，不跟随，大图 league_shaco_big） | 24 × 16 |
| `shaco_fx_w_box` | view_effects `league_shaco_w_box`（地面，不跟随，大图） | 24 × 32 |
| `shaco_fx_r_boom` | view_effects `league_shaco_r_boom`（地面，不跟随，大图） | 60 × 44（半径 30000） |
| `shaco_fx_r_mini` | view_effects `league_shaco_r_mini`（地面，不跟随，大图） | 64 × 32（半径 32000） |

- `w_box` 的 4–7 帧循环重复到 5 秒（W 射击 300 tick），`r_mini` 的 4–7 帧重复到 2.5 秒（150 tick）；`fear` 8 帧共 60 tick（英雄的恐惧 1 秒）。
- 清掉 Codex 给光和烟描的最深色边（`import_riven.py` 的 `unrim` 做法），魔盒和小丑头的描边保留；核对交回的张数和这份清单。
- 幻像分身（`league_shaco_clone` 的 `clone_in`、`clone_idle`、`clone_attack`）用萨科导入的待机和普攻帧做：`clone_idle` 是待机一帧（每 4 tick 播一次），`clone_attack` 是普攻（约 24 tick），`clone_in` 是带一团紫烟的现身。
