# 战争女神 希维尔：给 Codex 的特效提示词（第 3 步）

> **这一份是 16 张特效图。** 造型和动作已定（`design/sivir_design.png`，8 倍，40 格）。
> - 大小对照 `design/sivir_size.png`：定稿造型放大 4 倍，鞋底在红色脚底线上，上面是 10 格一段的刻度，右边是原版枪手。希维尔 51×40 格（头顶到鞋底 40 格）。每条写的大小都是游戏像素（格）。
> - `design/sivir_blade.png`：从定稿大招第 3 帧剪下来的十字刃（8 倍，她举过头顶的那一把；右下角露出的是她的头发）。**所有飞出去的刃（普攻、W、Q）都是这一把**：金色、四个弯刃尖、中间一个空心圆环、几颗青色小宝石，按每条写的大小缩放。
> - `design/sivir_shots.png`：出手、接刃、开盾、开大那几帧的定稿动作（4 倍），青色十字是出手闪光、接刃闪光、护盾和冲击波的中心（导入时 Claude 把特效放到这里）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里希维尔自己的特效贴图（很多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行（普攻和 W、W 弹射、Q 大刃、E 护盾、R 狩猎），只在本地用，不要提交。颜色按下面写的色阶：**刃和斩痕用金色；刃的拖尾、W 的弹射光用青绿色；E 的法术护盾用蓝紫色；R 的冲击波、月牙、速度线用青蓝色**，和英雄联盟一样。
> - **特效要亮**：魔腾的特效画成了最深的几档颜色，叠在人身上看不见。每个形状都要用最亮的几档和白色的芯，暗底上一眼能看见。
> - **护盾和套在人身上的特效中间要空着**：E 的护盾只画气泡的边和高光，里面的人要看得清；W 的光点、R 的风环也不能挡住人。
> - 特效照下面第 1–16 条和「所有特效图的规则」画，每张一个 PNG，文件名 `sivir_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准）。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`sivir_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「敏锐疾行」 | 扔十字刃；打中英雄时她加一小段移速 | `sivir_fx_a_blade` · `sivir_fx_a_hit` |
| 普攻里的 W「弹射」 | 每 10 秒自动开 4 秒：攻速变快，刃打中后最多再弹到 3 个附近的敌人 | `sivir_fx_w_cast` · `sivir_fx_w_on` · `sivir_fx_w_blade` · `sivir_fx_w_bounce` · `sivir_fx_w_hit` |
| 技能 1 = Q「回旋之刃」 | 扔出大十字刃，飞到最远再飞回她手里，去和回都打伤路上的敌人；刃飞着的时候她空着手，回来时接住 | `sivir_fx_q_blade` · `sivir_fx_q_throw` · `sivir_fx_q_hit` · `sivir_fx_q_catch` |
| 技能 2 = E「法术护盾」 | 罩上最多 3 秒的魔法护罩，挡下敌人的技能伤害和控制；挡下第一个技能时回血、加移速 | `sivir_fx_e_shroud` · `sivir_fx_e_block` |
| 大招 = R「狩猎」 | 周围的队友一起加速；狩猎中她每打中英雄就缩短技能冷却，打死英雄狩猎重新计时 | `sivir_fx_r_cast` · `sivir_fx_r_hunt` · `sivir_fx_r_renew` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、斩痕、拖尾、火星、护盾、冲击波没有黑描边，也不要用最深的颜色给形状描一圈边**（特效和角色相反）。只有十字刃本身（`a_blade`、`w_blade`、`w_bounce`、`q_blade`）像角色一样有 1 格深色描边。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的第四档，第五档（最深）只给很少的点缀。
- 颜色（按每条写的用）：
  - 金色（刃、斩痕、火星）：`#FFFFFF`、`#FFF3C4`、`#FFD45E`、`#E8A830`、`#A8641A`；
  - 青绿（刃的拖尾、W 的弹射光、宝石的光）：`#FFFFFF`、`#D6FFF6`、`#7EF2DC`、`#2CC4B0`、`#137A70`；
  - 蓝紫（E 的法术护盾）：`#FFFFFF`、`#DCE8FF`、`#8FB4FF`、`#5A6CF0`、`#3A2E9E`；
  - 青蓝（R 的冲击波、月牙、速度线，E 的十字星）：`#FFFFFF`、`#D8F8FF`、`#7FE0FF`、`#2E9EE8`、`#1A4E9E`；
- **飞行的刃画在格子正中，原地旋转**（`a_blade`、`w_blade`、`q_blade`）：游戏会把整张转到飞行方向，转着的十字刃怎么转都行；4 帧转四分之一圈（十字刃四个刃尖一样，所以无缝循环）。
- 命中、闪光居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 2 倍）。挂在人身上的循环画面（`w_on`、`e_shroud`、`r_hunt`）左右对称，因为人朝左朝右都用同一张。
- 套在角色身上的特效：格子里留出空的人形位置，不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（16 张）

16 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `sivir_fx_a_blade.png`：普攻：飞出去的小十字刃（飞行中循环），4 帧

希维尔的普攻：把她的十字刃（`design/sivir_blade.png`，缩小）旋转着扔出去。刃在格子中间转，4 帧转四分之一圈（四个刃尖，所以正好无缝循环），刃外面一圈淡淡的青色旋转残影（参考 BA_Mis_BlurryWeapon、BA_Mis_Trail）。约 10×10 格。刃是物体，有 1 格深色描边；残影没有。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, crescents, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #E8A830, #A8641A) and a teal ramp (#FFFFFF, #D6FFF6, #7EF2DC, #2CC4B0, #137A70).
Effect: a small SPINNING CROSSBLADE in flight, 4 frames, a seamless loop: the crossblade 8 squares across at the center of the cell, turned 22 degrees further each frame (a quarter turn over the 4 frames), a thin pale-teal motion-blur ring 10 squares across round it, brightest just behind each blade tip. The crossblade itself (not its trail or glow) is the one in design/sivir_blade.png: a golden four-armed throwing blade with an open ring in the middle and small teal gems, with a 1-square dark outline like a game sprite.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; the blade centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `sivir_fx_w_blade.png`：W 弹射：开了 W 以后的十字刃（飞行中循环），4 帧

开了 W「弹射」以后普攻扔出去的刃：同一把十字刃，转得更快，外面裹着一层亮青色的光，后面拖两三颗青色火星（参考 W_Mis_BlurryWeapon、W_Mis_Glow、W_Buf_Trail）。约 12×12 格。刃有 1 格深色描边；光和火星没有。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, crescents, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #E8A830, #A8641A) and a teal ramp (#FFFFFF, #D6FFF6, #7EF2DC, #2CC4B0, #137A70).
Effect: a CHARGED SPINNING CROSSBLADE in flight, 4 frames, a seamless loop: the same crossblade 8 squares across at the center, turned 22 degrees further each frame, wrapped in a bright teal glow 1-2 squares thick that follows its outline, a white-teal flare at each blade tip, 2-3 small teal sparks round it changing place each frame. The crossblade itself (not its trail or glow) is the one in design/sivir_blade.png: a golden four-armed throwing blade with an open ring in the middle and small teal gems, with a 1-square dark outline like a game sprite.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; the blade centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `sivir_fx_a_hit.png`：普攻打中，4 帧

十字刃打中：一道金色的小月牙斩痕，几颗金色和青色的火星（参考 W_Tar_HitSwirl）。约 10 格，不要太大。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, crescents, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #E8A830, #A8641A) and a teal ramp (#FFFFFF, #D6FFF6, #7EF2DC, #2CC4B0, #137A70).
Effect: a SMALL BLADE HIT, 4 frames: 1 a white flash at the center; 2 a thin white-gold crescent slash 8 squares long curving round the center, 3 tiny teal sparks; 3 the crescent thinner and fainter, the sparks flying out; 4 a few fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `sivir_fx_w_cast.png`：W 开启：刃上亮一圈青光（施法者身上），5 帧

开 W 的一瞬间，她手里的十字刃亮起一圈青色的光，四个刃尖各闪一颗小白星（参考 W_Buf_Glow、W_Buf_BlurryWeapon）。只画光，不画人和刃（导入时套在刃上）。约 16 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, crescents, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a teal ramp (#FFFFFF, #D6FFF6, #7EF2DC, #2CC4B0, #137A70) and a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #E8A830, #A8641A).
Effect: a CHARGE-UP GLOW round a weapon (do NOT draw the weapon; leave the middle empty), 5 frames: 1 a white point at the center; 2 a bright teal ring 10 squares across flashes round it; 3 four small white-teal stars at the ring's top, bottom, left and right (where the blade tips are), the ring wider; 4 the ring breaks into teal sparks, the stars fading; 5 a few teal sparks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `sivir_fx_w_on.png`：W 弹射持续中（她身上，循环，4 秒），4 帧

W 开着的 4 秒（攻速变快、刃会弹射）：她身边飘着几颗青色的小光点，绕着她慢慢转，偶尔闪一下（参考 W_Buf_Glow、color-sivirsparks）。中间是人，不要画人，人的位置留空。左右对称（她朝左朝右都用同一张），4 帧无缝循环，不要太密，不能挡住人。约 18 格宽、12 格高，中心在格子正中（对着她的腰）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, crescents, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a teal ramp (#FFFFFF, #D6FFF6, #7EF2DC, #2CC4B0, #137A70).
Effect: a LIGHT AURA round a figure's waist (do NOT draw the figure; leave the middle empty; symmetric left and right), 4 frames, a seamless loop: 5 small teal motes (1-2 squares, white cores) on a flattened ellipse 18 squares wide and 6 tall round the middle of the cell, moving a quarter of the way round each frame; the ones at the front brighter; one of them flashing a tiny white cross each frame.
Layout: one horizontal row of 4 equal 3:2 cells, image size 1536x256 (each cell 384x256); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `sivir_fx_w_bounce.png`：W 刃弹到下一个敌人：一道青色的弧线落到目标身上，4 帧

弹射：刃打中第一个敌人以后弹到旁边的下一个敌人。从格子左上角划过来一道青色和金色的弧线，最后落到格子中心（导入时对着下一个目标），弧线的头上是那把小十字刃（参考 Sivir_RicochetPax、W_Mis_Glow）。约 16×16 格。刃有 1 格深色描边；弧线没有。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, crescents, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #E8A830, #A8641A) and a teal ramp (#FFFFFF, #D6FFF6, #7EF2DC, #2CC4B0, #137A70).
Effect: a BLADE BOUNCING IN, 4 frames: a small crossblade (6 squares across) arrives along a curving teal arc from the top left corner: 1 the blade near the top left, a short teal arc behind it; 2 halfway, the arc 8 squares long; 3 the blade a square short of the center, the arc fading at its tail; 4 the blade at the center, a white spark under it, the arc nearly gone. The crossblade itself (not its trail or glow) is the one in design/sivir_blade.png: a golden four-armed throwing blade with an open ring in the middle and small teal gems, with a 1-square dark outline like a game sprite.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; the arc ends at the center of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `sivir_fx_w_hit.png`：W 弹射打中，4 帧

弹射打中：一道青色的月牙斩痕旋开，几颗白色和金色的火星（参考 W_Tar_HitSwirl、Sivir_RicochetPax）。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, crescents, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a teal ramp (#FFFFFF, #D6FFF6, #7EF2DC, #2CC4B0, #137A70) and a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #E8A830, #A8641A).
Effect: a RICOCHET HIT, 4 frames: 1 a white flash; 2 a bright teal crescent slash 10 squares long swirling round the center, a gold spark on it; 3 a second thinner teal crescent opposite the first, both fading, 4 sparks flying out; 4 a few fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `sivir_fx_q_blade.png`：Q 回旋之刃：飞出去再飞回来的大十字刃（飞行中循环，大图），4 帧

回旋之刃：把她的十字刃整把扔出去，飞到最远再飞回她手里（去和回用同一张）。大一号的十字刃在格子中间飞快地转，外面一圈金色和青色的旋转残影，四个刃尖拖出金色的弧线（参考 Q_Mis_Trail、Q_bluelight、BA_Mis_BlurryWeapon）。约 20×20 格（刃 14 格）。刃有 1 格深色描边；残影和弧线没有。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, crescents, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #E8A830, #A8641A) and a teal ramp (#FFFFFF, #D6FFF6, #7EF2DC, #2CC4B0, #137A70).
Effect: a BIG SPINNING CROSSBLADE in flight, 4 frames, a seamless loop: the crossblade 14 squares across at the center of the cell, turned 22 degrees further each frame, each of its four tips trailing a curved gold motion arc a quarter circle long (a spinning pinwheel of light 20 squares across), a soft teal light in the ring at its middle, a few gold sparks flung off. The crossblade itself (not its trail or glow) is the one in design/sivir_blade.png: a golden four-armed throwing blade with an open ring in the middle and small teal gems, with a 1-square dark outline like a game sprite.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; the blade centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `sivir_fx_q_throw.png`：Q 出手：手上的金色闪光（施法者身上），4 帧

扔出大刃的一瞬间，她的手前面一个金色的四角星闪光，带一圈青色的小光环（参考 Q_bluelight、E_spark）。只画闪光。约 12 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, crescents, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #E8A830, #A8641A) and a teal ramp (#FFFFFF, #D6FFF6, #7EF2DC, #2CC4B0, #137A70).
Effect: a SMALL THROW FLASH, 4 frames: 1 a white point; 2 a four-pointed white-gold star with long thin rays; 3 the star wider and thinner, a thin teal ring round it; 4 fading sparkles.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `sivir_fx_q_hit.png`：Q 打中，5 帧

大刃打中（去和回都会打）：一道大的金色月牙斩痕，几颗青色火星（参考 W_Tar_HitSwirl、Q_Mis_Trail）。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, crescents, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #E8A830, #A8641A) and a teal ramp (#FFFFFF, #D6FFF6, #7EF2DC, #2CC4B0, #137A70).
Effect: a HEAVY BLADE HIT, 5 frames: 1 a white flash; 2 a broad white-gold crescent slash 14 squares long curving round the center; 3 the crescent at full size, a thinner teal crescent inside it, 5 gold and teal sparks flying out; 4 the crescents thin and break; 5 a few fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `sivir_fx_q_catch.png`：Q 接住飞回来的刃（施法者身上），4 帧

大刃飞回来被她接住：刃周围一圈金色的光一收，几颗青色的小星溅开（参考 BA_Mis_BlurryWeapon、E_spark）。只画光，不画人和刃（导入时套在刃上）。约 14 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, crescents, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #E8A830, #A8641A) and a teal ramp (#FFFFFF, #D6FFF6, #7EF2DC, #2CC4B0, #137A70).
Effect: a CATCH GLINT round a weapon (do NOT draw the weapon; leave the middle empty), 4 frames: 1 a gold ring 12 squares across round the center; 2 the ring snaps inward to 8 squares, bright, 4 small teal stars popping out of it; 3 the ring gone, the stars further out; 4 two fading sparkles.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `sivir_fx_e_shroud.png`：E 法术护盾：罩住她的蓝紫色魔法护罩（三段：出现、持续、消失，大图），3 行 × 4 帧

法术护盾（最多 3 秒）：一个罩住她全身的蓝紫色魔法气泡（参考 E_buf_manashield：深蓝到紫色的球，边上亮，中间透明；E_spark 青白色的十字星）。**只画气泡的边和几处高光，中间一定要空着**（人要看得见），不要画人。第 1 行出现（从她胸口一个小光点涨成整个球，4 帧）；第 2 行持续（球边缘的光慢慢流动，顶上一颗青白色的十字星闪烁，4 帧无缝循环）；第 3 行消失（球变淡、碎成光点散开，4 帧）。左右对称。约 46 格宽、48 格高（她 51×40 格），球的中心在格子中间偏下（底部往上 22 格）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, crescents, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a shield ramp (#FFFFFF, #DCE8FF, #8FB4FF, #5A6CF0, #3A2E9E) and a cyan-white star from (#FFFFFF, #D8F8FF, #7FE0FF, #2E9EE8, #1A4E9E).
Effect: a MAGIC SHIELD BUBBLE round a standing figure (do NOT draw the figure; the inside of the bubble stays EMPTY - only its rim and a few highlights are drawn; symmetric left and right), 3 rows of 4 frames: ROW 1 (appear): 1 a white point at the middle; 2 a small blue ring 12 squares across; 3 the ring 30 squares across, violet sparks on it; 4 the full bubble: a round rim 44 squares across and 46 tall, 1-2 squares thick, light blue at the top left fading to deep violet at the bottom right, a white highlight arc at the top left. ROW 2 (hold, a seamless loop): the full bubble, a bright band of light sliding round the rim a quarter of the way each frame, a cyan-white four-pointed star twinkling at the top (big, small, big, small). ROW 3 (break): 1 the rim flickers, broken into arcs; 2 the arcs thinner, blue sparks; 3 sparks drifting outward; 4 a few fading sparks.
Layout: three horizontal rows of 4 equal square cells each, image size 1536x1152 (each cell 384x384); the bubble's center 22 squares up from the bottom of every cell (a little below the middle), horizontally centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `sivir_fx_e_block.png`：E 挡下技能：护盾闪一下、回血（施法者身上），5 帧

法术护盾挡下敌人的技能：她胸前一个很亮的青白色十字星爆闪，一圈蓝色的波纹荡开，几片蓝紫色的碎光往外飞（参考 E_spark、E_shield_line、base_E_blueorb）。约 24 格，中心在格子正中（对着她的胸口）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, crescents, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a shield ramp (#FFFFFF, #DCE8FF, #8FB4FF, #5A6CF0, #3A2E9E) and a cyan ramp (#FFFFFF, #D8F8FF, #7FE0FF, #2E9EE8, #1A4E9E).
Effect: a SPELL BLOCKED FLASH, 5 frames: 1 a white flash at the center; 2 a big cyan-white four-pointed star with long thin rays, a blue ring 10 squares across; 3 the ring 20 squares across, 6 small blue-violet shards flying out; 4 the star small, the ring thin and broken, the shards further; 5 a few fading shards.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `sivir_fx_r_cast.png`：R 狩猎：开大时脚下的冲击波（大图，画在人物下面），6 帧

开大的一瞬间：她脚下一圈青蓝色的冲击波往外荡开，地上几道青白色的速度线朝外冲，几道青色的月牙光（参考 R_buf_shockwave、R_buf_cloudring、R_buf_speedlines、R_Buf_cresent）。中间是人，不要画人。从斜上方看，地上的圈是宽是高 2 倍的椭圆。约 64 格宽、32 格高，圈的中心在格子底部往上 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, crescents, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan ramp (#FFFFFF, #D8F8FF, #7FE0FF, #2E9EE8, #1A4E9E).
Effect: a WAR CRY SHOCKWAVE on the ground round a figure's feet (do NOT draw the figure; the ground seen from above at an angle: every ring a flattened ellipse twice as wide as tall), 6 frames: 1 a white flash at the center; 2 a bright cyan ring 20 squares wide; 3 the ring 40 squares wide with a jagged cyan cloud edge (like flames lying flat), 6 short white-cyan speed lines shooting outward from it; 4 the ring 56 squares wide and thinner, two cyan crescents sweeping round it; 5 the ring 62 squares wide, broken into arcs; 6 a few fading arcs.
Layout: one horizontal row of 6 equal 2:1 cells, image size 3072x256 (each cell 512x256); the rings' center 12 squares up from the bottom of every cell, horizontally centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `sivir_fx_r_hunt.png`：R 狩猎：队友加速（脚下，三段：出现、持续、消失），3 行 × 4 帧

狩猎期间每个加速的队友脚下：一圈青色的风环贴着地面转，旁边几道青白色的速度线往后掠（参考 R_buf_cloudring、R_buf_speedlines、R_Buf_cresent）。中间是人，不要画人。左右对称（人朝左朝右都用同一张）。第 1 行出现（4 帧），第 2 行持续（4 帧无缝循环），第 3 行消失（4 帧）。约 26 格宽、12 格高，贴着地面。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, crescents, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan ramp (#FFFFFF, #D8F8FF, #7FE0FF, #2E9EE8, #1A4E9E).
Effect: a SPEED-UP RING at a figure's feet (do NOT draw the figure; symmetric left and right; on the ground seen from above at an angle), 3 rows of 4 frames: ROW 1 (appear): a cyan flash at the bottom middle growing into a flattened ring 22 squares wide and 8 tall with a jagged wind edge. ROW 2 (hold, a seamless loop): the ring turning (its bright part moving a quarter of the way round each frame), 2 short white-cyan speed lines on each side streaking up and outward, in a different place each frame. ROW 3 (fade): the ring breaks into arcs and fades, the lines gone.
Layout: three horizontal rows of 4 equal cells each, each cell 2 wide to 1 tall, image size 2048x768 (each cell 512x256); the ring at the bottom middle of every cell (its center 6 squares up from the bottom). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `sivir_fx_r_renew.png`：R 击杀刷新狩猎（施法者身上），5 帧

狩猎时打死敌方英雄，狩猎时间重新开始：她身上一个青白色的爆闪，两道青色的月牙光绕着她转一圈（参考 R_alliesbuff_flash、R_Buf_cresent）。约 22 格，中心在格子正中（对着她的胸口）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, crescents, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan ramp (#FFFFFF, #D8F8FF, #7FE0FF, #2E9EE8, #1A4E9E) and a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #E8A830, #A8641A).
Effect: a HUNT RENEWED FLASH, 5 frames: 1 a white flash; 2 a cyan-white four-pointed star with long rays; 3 two bright cyan crescents 18 squares across sweeping round the center in opposite directions, gold sparks; 4 the crescents thinner, further round; 5 a few fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `sivir_fx_a_blade` | view_projectiles `league_sivir_a_blade`（循环，游戏转到飞行方向） | 10 × 10 |
| `sivir_fx_w_blade` | view_projectiles `league_sivir_w_blade`（循环，游戏转到飞行方向） | 12 × 12 |
| `sivir_fx_a_hit` | view_effects `league_sivir_a_hit`（跟随，画在人物上面） | 10 |
| `sivir_fx_w_cast` | view_effects `league_sivir_w_cast`（施法者身上，跟随，朝左时镜像；放到普攻第 3 帧出手的刃上） | 16 |
| `sivir_fx_w_on` | view_buffs `league_sivir_w_on`（循环，画在人物上面） | 18 × 12 |
| `sivir_fx_w_bounce` | view_effects `league_sivir_w_bounce`（跟随，画在人物上面；格子中心对着下一个目标，随后接 `w_hit`） | 16 × 16 |
| `sivir_fx_w_hit` | view_effects `league_sivir_w_hit`（跟随，画在人物上面） | 12 |
| `sivir_fx_q_blade` | view_projectiles `league_sivir_q_out` 和 `league_sivir_q_back`（同一张图，循环，大图） | 20 × 20 |
| `sivir_fx_q_throw` | view_effects `league_sivir_q_throw`（施法者身上，不跟随；放到 Q 第 4 帧出手的手上） | 12 |
| `sivir_fx_q_hit` | view_effects `league_sivir_q_hit`（跟随，画在人物上面） | 16 |
| `sivir_fx_q_catch` | view_effects `league_sivir_q_catch`（施法者身上，不跟随；放到接刃第 1 帧刃的中心） | 14 |
| `sivir_fx_e_shroud` | view_buffs `league_sivir_e_shroud`（ThreePhase：第 1 行 `e_pre` 出现，第 2 行 `e_loop` 循环，第 3 行 `e_remove` 消失；画在人物上面，大图） | 46 × 48 |
| `sivir_fx_e_block` | view_effects `league_sivir_e_block`（施法者身上，不跟随，画在人物上面） | 24 |
| `sivir_fx_r_cast` | view_effects `league_sivir_r_cast`（施法者身上，画在人物下面，大图） | 64 × 32 |
| `sivir_fx_r_hunt` | view_buffs `league_sivir_r_hunt`（ThreePhase：第 1 行 `r_pre`，第 2 行 `r_loop` 循环，第 3 行 `r_remove`；画在人物下面） | 26 × 12 |
| `sivir_fx_r_renew` | view_effects `league_sivir_r_renew`（施法者身上，不跟随，画在人物上面） | 22 |

- 小图进 `league_sivir_fx`，大图（`q_blade` → `q_out` + `q_back` 两个 tag、`e_shroud` 三段 `e_pre`/`e_loop`/`e_remove`、`r_cast`）进 `league_sivir_big`；`r_hunt` 三段 `r_pre`/`r_loop`/`r_remove` 在 `league_sivir_fx`。
- 施法者身上的画面（`w_cast`、`q_throw`、`q_catch`、`e_block`、`r_cast`、`r_renew`）按 `design/sivir_shots.png` 的十字把格子中心挪过去；`q_throw`、`q_catch`、`e_block`、`r_renew` 是 `is_follow: false`（红方朝向规则），`r_cast` 的圈心在脚底。
- 飞行物（`a_blade`、`w_blade`、`q_out`、`q_back`）第一帧前加一个空帧（出生那一 tick 画面朝上，`import_lucian.py` 的 `RAY_SKIP`）；刃从 `bolt_y` / `q_y` 的高度出手，和出手帧的手差不超过 8 像素。
- 清掉 Codex 给光描的最深色边（`import_riven.py` 的 `unrim` 做法，十字刃本身保留描边）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比（魔腾的教训）；Codex 交的如果是要求尺寸的 2 倍（娑娜那次），缩一半。
