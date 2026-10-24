# 璐璐的变形小动物 + 亚索的风之障壁（给 Codex）

用户 2026-10-24：「接着做璐璐变形：先出小动物的设计给我审」「还有个亚索风墙吧？但是亚索风墙要智能点放啊」「你要做风墙的特效也一起把压缩包整理了」。

**顺序**：先画第 1 张（小动物的三种设计 A / B / C），交给用户挑；挑好之后再画第 2-4 张（变形的出现、循环、散开，照挑中的那只画）。亚索的四张（第 5-8 张）和小动物无关，可以和第 1 张一起画。每张一个 PNG，按下面的文件名交付。

**参考图**（按编号上传）：图1 英雄联盟的变形小动物（正面、斜前、侧面、待机），图2 现在的变形（一团烟 + 小松鼠，人还露在外面），图3 游戏尺寸对照（几个英雄和三种小动物的大小），图4 英雄联盟风之障壁的贴图，图5 亚索的游戏尺寸。

**为什么要盖住人**：游戏换不了被变形的敌人的模型（引擎不给改别的英雄的贴图），只能在他身上叠一张跟着他走的图。所以小动物要**大到能把人盖住**（A、B），或者像现在这样小、坐在一团烟上（C）。**画面挂在人身上，左右必须对称**（游戏在红方不翻转特效）：小动物**正面朝着我们**，不画侧面。

---

## 1. `squill_design.png`：小动物的三种设计（游戏尺寸），给用户挑

三格并排（游戏里的英雄约 35-48 格宽、34-42 格高，见图3）：**A 盖住人**——英雄联盟那只小动物正面站着，连两条竖起来的大尾巴约 36 格宽、40 格高，把一般英雄的头和身体大半挡住；**B 盖住人 + 魔法烟**——同一只小动物约 30 × 32，坐在一团粉紫魔法烟上（烟约 46 格宽、14 格高，在脚下），合起来约 46 × 42，拿大剑、骑野猪的宽英雄也能挡住大半；**C 小一点**——同一只小动物约 20 × 22，坐在一团大烟雾前面（同现在的做法，烟约 34 × 30），小动物照英雄联盟的样子重画。三只都是**正面、左右对称**。

```text
Pixel art game sprite for a small tactics game, drawn AT GAME SIZE: chunky square pixels (one square = one game pixel, 16 px a square in this image), hard edges, no anti-aliasing, no blur; ONE 1-square outline in #24123A round the critter (never a second black ring), 3-4 flat shades per material, no specks, details at least 2 squares; colours only: fur #F4ECFF, #DCC8FF, #BE9CF8, #9C74EC, #7A50D4, #5634A8, #38206E; white #FFFFFF, #F0F0FA, #D2D4EA, #A8ACCE; pink #FFD6F0, #FF9ADA, #F05AC0, #B82A94; eyes #120A1E (the eye) and #FFFFFF (one 1-square shine); paws #2A1440. Lulu's pink magic puff (B and C only, no outline): #FFFFFF, #FFE6FA, #FFB0F0, #FF70E0, #E040D0, #B020B8; violet: #FFFFFF, #E8E0FF, #C0B0FF, #9A80FF, #7A50F0, #5A30C8.
Subject: League of Legends' polymorph critter (Lulu's Whimsy, the 'Squill', image 1): a chubby lilac-purple squirrel-like critter seen FROM THE FRONT, facing the viewer: a big round head with two huge pointed ears (pink inside with a white fringe), two huge glossy black eyes with a white shine, a white face and muzzle with a tiny pink nose and a small happy mouth, a white belly, stubby legs with dark paws, and TWO big fluffy tails rising behind it in a V, lilac with white tips. Three design options side by side, each SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side):
A) the critter standing, 36 squares wide and 40 tall from the tails' tips to its paws, big enough to hide most of a champion about 40 squares wide and 40 tall standing behind it (head and body in the middle 26 squares, the tails in a V above and behind the head);
B) the same critter 30 wide and 32 tall sitting on a puffy cloud of pink and violet magic smoke 46 squares wide and 14 tall at its feet (glitter in the smoke, no outline on the smoke), 46 x 42 together;
C) the same critter small, 20 wide and 22 tall, sitting in front of a big billowing cloud of pink and violet magic smoke 34 squares wide and 30 tall that fills the cell's lower middle.
Match image 1's look (colours, the huge glossy eyes, the pink-lined ears, the two white-tipped tails); the face must read at game size: 2x2-square eye whites at least, the eyes the darkest thing on it. Nothing below the feet line.
Layout: one horizontal row of 3 equal cells, image size 2400x768 (each cell 800x768, 16 px a square); the feet (or the smoke's bottom) 2 squares above each cell's bottom, centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

## 2-4. 变形的三段（用户挑好设计后再画；把挑中的那一格作为第一张参考图）

游戏里叫 `league_lulu_w_poly`（ThreePhase：出现 `w_poly_in` → 循环 `w_poly` → 散开 `w_poly_out`），挂在被变形的敌人身上，跟着他走，1.75 秒。格子和第 1 张一样大，人的脚在格子底上 2 格、水平居中。三段都**左右对称**。

### 2. `lulu_fx_w_poly_in.png`，4 帧

砰地一下：白粉闪光，一团粉紫魔法烟罩住人，最后一帧烟里蹦出挑中的那只小动物（和循环第 1 帧一样大、一样的位置）。

```text
Pixel art game sprite for a small tactics game, drawn AT GAME SIZE: chunky square pixels (one square = one game pixel, 16 px a square in this image), hard edges, no anti-aliasing, no blur; ONE 1-square outline in #24123A round the critter (never a second black ring), 3-4 flat shades per material, no specks, details at least 2 squares; colours only: fur #F4ECFF, #DCC8FF, #BE9CF8, #9C74EC, #7A50D4, #5634A8, #38206E; white #FFFFFF, #F0F0FA, #D2D4EA, #A8ACCE; pink #FFD6F0, #FF9ADA, #F05AC0, #B82A94; eyes #120A1E (the eye) and #FFFFFF (one 1-square shine); paws #2A1440. Pink magic (no outline): #FFFFFF, #FFE6FA, #FFB0F0, #FF70E0, #E040D0, #B020B8; violet: #FFFFFF, #E8E0FF, #C0B0FF, #9A80FF, #7A50F0, #5A30C8.
The POLYMORPH of a champion into the critter of image 1 (the design the user picked) - 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-pink flash in the middle; 2 a round puff of pink and violet magic smoke bursts out, as big as the chosen design's whole shape; 3 the puff at full size, glitter in it; 4 the chosen critter popping out of the thinning puff, exactly where and as big as in the loop's first frame. Do not draw the champion: the critter (and smoke) hides him.
Layout: one horizontal row of 4 equal cells, image size 3200x768 (each cell 800x768, 16 px a square); the feet 2 squares above each cell's bottom, centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `lulu_fx_w_poly.png`，6 帧

无缝循环：挑中的那只小动物一跳一跳（身体上下 1 格）、两条尾巴左右摇、耳朵抖一下，头上冒两三颗小星星；有烟的设计烟慢慢翻滚。

```text
Pixel art game sprite for a small tactics game, drawn AT GAME SIZE: chunky square pixels (one square = one game pixel, 16 px a square in this image), hard edges, no anti-aliasing, no blur; ONE 1-square outline in #24123A round the critter (never a second black ring), 3-4 flat shades per material, no specks, details at least 2 squares; colours only: fur #F4ECFF, #DCC8FF, #BE9CF8, #9C74EC, #7A50D4, #5634A8, #38206E; white #FFFFFF, #F0F0FA, #D2D4EA, #A8ACCE; pink #FFD6F0, #FF9ADA, #F05AC0, #B82A94; eyes #120A1E (the eye) and #FFFFFF (one 1-square shine); paws #2A1440. Pink magic (no outline): #FFFFFF, #FFE6FA, #FFB0F0, #FF70E0, #E040D0, #B020B8; violet: #FFFFFF, #E8E0FF, #C0B0FF, #9A80FF, #7A50F0, #5A30C8.
The POLYMORPH of a champion into the critter of image 1 (the design the user picked) - 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a seamless loop of the chosen design: the critter bobs 1 square up and down, its two tails sway left and right (mirrored, so it stays symmetric), its ears twitch once, 2-3 tiny pink stars twinkle over its head; any smoke rolls slowly. Do not draw the champion: the critter (and smoke) hides him.
Layout: one horizontal row of 6 equal cells, image size 4800x768 (each cell 800x768, 16 px a square); the feet 2 squares above each cell's bottom, centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `lulu_fx_w_poly_out.png`，4 帧

变形结束：小动物噗地变成一团闪粉，烟往四周散开，露出下面的人。

```text
Pixel art game sprite for a small tactics game, drawn AT GAME SIZE: chunky square pixels (one square = one game pixel, 16 px a square in this image), hard edges, no anti-aliasing, no blur; ONE 1-square outline in #24123A round the critter (never a second black ring), 3-4 flat shades per material, no specks, details at least 2 squares; colours only: fur #F4ECFF, #DCC8FF, #BE9CF8, #9C74EC, #7A50D4, #5634A8, #38206E; white #FFFFFF, #F0F0FA, #D2D4EA, #A8ACCE; pink #FFD6F0, #FF9ADA, #F05AC0, #B82A94; eyes #120A1E (the eye) and #FFFFFF (one 1-square shine); paws #2A1440. Pink magic (no outline): #FFFFFF, #FFE6FA, #FFB0F0, #FF70E0, #E040D0, #B020B8; violet: #FFFFFF, #E8E0FF, #C0B0FF, #9A80FF, #7A50F0, #5A30C8.
The POLYMORPH of a champion into the critter of image 1 (the design the user picked) - 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-pink flash where the critter is, the critter gone; 2 a puff bursting outward; 3 the puff breaking into pink and violet glitter at the cell's edges, the middle empty; 4 a few fading specks. Do not draw the champion: the critter (and smoke) hides him.
Layout: one horizontal row of 4 equal cells, image size 3200x768 (each cell 800x768, 16 px a square); the feet 2 squares above each cell's bottom, centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 5-8. 亚索的风之障壁

英雄联盟的 W：亚索在身前竖起一面风墙，4 秒，挡掉敌人飞过来的东西（普攻的弹、技能弹）。游戏里：墙是一个慢慢往前飘的投射物，**投射物的图会跟着飞行方向转**，所以墙画成**朝右飞**的样子——一道**竖着**的风墙（飞行方向朝右，墙面上下展开），**上下对称**；其他三张（出手的风、挡住东西的一下、墙散掉）不会转，画成**左右对称**。颜色照英雄联盟：白色到浅蓝、钢蓝的风（参考图4）。

### 5. `yasuo_w_wall.png`：墙身（投射物，循环），6 帧

墙厚 6-8 格（左右）、高 48 格（上下），中间稍微往右鼓；风一道道往上卷，中间一条白色的芯，右边（朝敌人那面）飘出小风丝；6 帧无缝循环，上下对称。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels (16 px a square), hard edges, no anti-aliasing, NO outline around light, wind, smoke or glitter, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a wind ramp (#FFFFFF, #E6FAFF, #B4EEFA, #78D8F0, #3CB0DC, #1E7AB4, #134A7A; grey-blue dust #DCE6F0, #A8B8CC, #74869E).
Effect: a WIND WALL seen as it flies RIGHT: a vertical curtain of swirling wind 6-8 squares thick (left to right) and 48 squares tall (top to bottom), bulging slightly to the RIGHT in the middle (a shallow arc), made of white and pale blue wind streaks curling upward, a bright white core line down its middle, small wisps peeling off its right face; 6 frames, a seamless loop (the streaks crawl upward); SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight).
Layout: one horizontal row of 6 equal cells, image size 1536x832 (each cell 256x832, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `yasuo_w_cast.png`：出手的风（亚索脚下），4 帧

亚索竖墙时脚下卷起的一阵风：白光一闪，两道风往两边往上卷开（约 26 × 18），带一点地上的灰，最后散成风丝；左右对称。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels (16 px a square), hard edges, no anti-aliasing, NO outline around light, wind, smoke or glitter, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a wind ramp (#FFFFFF, #E6FAFF, #B4EEFA, #78D8F0, #3CB0DC, #1E7AB4, #134A7A; grey-blue dust #DCE6F0, #A8B8CC, #74869E).
Effect: a GUST at a swordsman's feet as he flicks up a wall of wind: 1 a white flash at the middle bottom; 2 two curls of wind sweeping up and out to both sides, 26 squares wide and 18 tall; 3 the curls at full size, dust at the bottom; 4 fading wisps. SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side).
Layout: one horizontal row of 4 equal cells, image size 2048x384 (each cell 512x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `yasuo_w_block.png`：挡住东西的一下，4 帧

飞过来的弹撞在墙上被挡掉：一道白色竖光、青白色的菱形光（参考图4的 block_impact），然后散成小风丝；左右对称，约 10 × 16。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels (16 px a square), hard edges, no anti-aliasing, NO outline around light, wind, smoke or glitter, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a wind ramp (#FFFFFF, #E6FAFF, #B4EEFA, #78D8F0, #3CB0DC, #1E7AB4, #134A7A).
Effect: a BLOCK FLASH where a missile hits the wind wall: 1 a white vertical spark 4 squares wide and 14 tall; 2 a pale cyan diamond flare 10 wide and 16 tall with a white core (like image 4's block impact); 3 the flare breaking into small wind wisps; 4 two fading wisps. SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side).
Layout: one horizontal row of 4 equal cells, image size 1024x320 (each cell 256x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `yasuo_w_fade.png`：墙散掉，4 帧

墙到时间散掉：一圈白蓝色的风丝往外旋开、变淡（画成圆的：这张图不会跟着墙转）；左右上下都对称，约 24 × 24。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels (16 px a square), hard edges, no anti-aliasing, NO outline around light, wind, smoke or glitter, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a wind ramp (#FFFFFF, #E6FAFF, #B4EEFA, #78D8F0, #3CB0DC, #1E7AB4, #134A7A).
Effect: the WIND WALL DISPERSING (round, because the game cannot turn this one): 1 a ring of white and pale blue wind wisps 24 squares across; 2 the wisps spiralling outward and thinning; 3 a few wisps; 4 two fading specks. SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) and top to bottom.
Layout: one horizontal row of 4 equal cells, image size 1792x448 (each cell 448x448, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

交付：8 个 PNG（文件名照上面），透明背景，格子严格对齐。
