# 刀锋舞者 艾瑞莉娅：给 Codex 的特效提示词（第 3 步）

> **这一份是 18 张特效图。** 造型和动作已定（`design/irelia_design.png`，idle 第 1 帧放大 8 倍，44 行、34 格宽，连身边的浮刀）。
> - 大小对照 `design/irelia_size.png`：idle 放大 4 倍，鞋底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/irelia_shots.png`：定稿动作的出手帧（4 倍），青色十字是她的站位点（线、刀群、身上的画面都从这里算）。
> - **她的特效就是她的刀**：她不握刀，四把弯月形的刀浮在身边、用意念驱动——刀刃绯红、刀背深蓝、银色刀尖、刀根一颗青色宝石，和 `design/irelia_design.png` 里浮在她身边的刀一模一样。刀光是绯红色（白芯），宝石和眩晕、护身是青色。这次没有英雄联盟的特效贴图参考。
> - **特效要亮**：每道刀光、光圈、光点都用最亮的几档和白色的芯，暗底上一眼能看见。
> - **围着人的画面（被动满层、W 蓄力、W 出手）只画外圈和两边，中间人形位置留空**，不然会把人整个挡住。
> - **方向（重要，红色方不会镜像）**：`e_line`、`w_line` 是**一整条线的画面**：游戏把整张图从她（左端）铺到线的尽头（右端）、朝施放方向转，所以**画成朝右、左端是她**，而且要**上下对称**（往左放时会上下翻）。飞出去的刀群 `r_blades` 画成朝右飞，同样**上下对称**。画在人身上、脚下、地上的（打中、标记、眩晕、减速、被动、W 蓄力、W 出手、E 出手、刀墙）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。
> - 特效照下面第 1–18 条和「所有特效图的规则」画，每张一个 PNG，文件名 `irelia_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准，1 格 = 16 像素）。
> - **请同时交游戏尺寸版**：每张再整理一份 1 格 = 1 像素的原尺寸条，放在 `pixel_1x/`（文件名一样），严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入。
> - 生图原稿（半透明边、格子比例不准）也一起交在 `raw/`。每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`irelia_fx_done.zip`）放在 outputs 里，或放在 `outputs/irelia-fx/`。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 浮刀飞过去砍一下 | `a_hit` |
| 被动「艾欧尼亚热诚」 | Q 每打中一个单位、E/W/R 每打中一个英雄叠一层（攻速），满 4 层时普攻多一段伤害、身边的刀发青光 | `pv4` · `p_hit` |
| 技能 1 = Q「利刃冲击」 | 冲向目标砍一刀并回血；打带标记的目标或打死目标就能再冲一次 | `q_hit` · `mark` |
| 技能 2 = E「比翼双刃」 | 一把刀在她脚边、一把在目标身后，互相飞向对方，连成的线上的敌人被眩晕并打上标记 | `e_cast` · `e_line` · `e_hit` · `e_stun` · `mark` |
| 技能 2（E 冷却时）= W「距破之舞」 | 蓄力约 1 秒（物理伤害减半），然后沿直线砍出一刀 | `w_on` · `w_slash` · `w_line` · `w_hit` |
| 大招 = R「先锋之刃」 | 身边的刀全部飞向一个英雄，打中后对后方扇形里的敌人造成伤害、减速、缴械，再在落点插出一圈刀墙减速 | `r_blades` · `r_hit` · `r_slow` · `r_wall_v` · `r_wslow` · `mark` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**刀光、光圈、光点都没有黑描边，也不要用最深的颜色给它们描一圈边**；只有实体的刀有 1 格深色描边 `#0A081C`。
- **要亮**：每道光都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只做很少的点缀。
- 颜色（按每条写的用）：
  - 绯红（刀刃、刀光、减速、刀墙的光）：`#FFFFFF`、`#FFC8D8`、`#F32D5B`、`#D51046`、`#A80A36`、`#750629`；
  - 青色（宝石、眩晕、被动、护身、E 的线）：`#FFFFFF`、`#D8FBFF`、`#84EBFF`、`#27CFF3`、`#098FBA`；
  - 银色（刀尖、火星）：`#FFFFFF`、`#E8F4FC`、`#BDCFDF`、`#96ACC3`、`#6C7A98`；
  - 深蓝（刀背，只用在实体的刀上）：`#4D6085`、`#344367`、`#222B51`、`#131A37`、`#0A081C`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。
- 画在她或别人身上、脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（18 张）

18 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：普攻距离 25000，E 的线长 80000，W 的线长 55000，R 刀群打中后的扇形半径 35000，刀墙半径 30000）。

### 1. `irelia_fx_a_hit.png`：普攻打中（目标身上），4 帧

她的普攻是浮在身边的刀飞过去砍一下：目标身上一道红色的斜十字刀光（白芯、绯红光），两道交叉、左右对称，外面几点银白火星。约 14 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, trails or rings (only her solid blades get the dark #0A081C outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson ramp (#FFFFFF, #FFC8D8, #F32D5B, #D51046, #A80A36, #750629) and a silver ramp (#FFFFFF, #E8F4FC, #BDCFDF, #96ACC3, #6C7A98).
Effect: a BLADE STRIKE on the target, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares across; 2 two crimson slash arcs crossing in an X 14 squares across, white cores; 3 the arcs thinning, a few silver sparks flying out at mirrored places; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `irelia_fx_p_hit.png`：被动满层时普攻附带的伤害（目标身上），4 帧

被动「艾欧尼亚热诚」叠满 4 层后，普攻多一段伤害：在目标身上一小圈青色的光（白芯），四周 4 片很小的刀形光点向外散开。**左右对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, trails or rings (only her solid blades get the dark #0A081C outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan ramp (#FFFFFF, #D8FBFF, #84EBFF, #27CFF3, #098FBA) and a crimson ramp (#FFFFFF, #FFC8D8, #F32D5B, #D51046, #A80A36, #750629).
Effect: a SMALL CYAN BURST on the target, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-cyan dot; 2 a cyan ring 10 squares across with a white core; 3 four tiny crimson-edged leaf sparks flying out diagonally (mirrored); 4 fading.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `irelia_fx_pv4.png`：被动叠满 4 层（她身上，循环），4 帧

被动叠满时她身边的刀发出青光：在她身体外围上下左右几个位置有青色小光点一闪一闪（像刀上的宝石在发光），**中间人形的位置留空**，**左右对称**。约 34 格宽、42 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, trails or rings (only her solid blades get the dark #0A081C outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan ramp (#FFFFFF, #D8FBFF, #84EBFF, #27CFF3, #098FBA).
Effect: a CYAN GLOW round her, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the figure's place in the middle (16 x 40 squares, its bottom on the cell's bottom) EMPTY: six small cyan glints (2-3 squares, white cores) spread round the figure's outline - two at shoulder height, two at the hips, two at the knees, each pair mirrored - twinkling in turn, with 1-square cyan sparkles drifting up between them.
Layout: one horizontal row of 4 equal 36:44 cells, image size 2304x704 (each cell 576x704, 16 px a square). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `irelia_fx_q_hit.png`：Q 利刃冲击打中（目标身上），5 帧

她冲到目标身上砍下：一道又亮又粗的红色刀光从左上到右下、另一道从右上到左下交叉（白芯、绯红光），中心一闪白光，几片红色的光屑往外飞。**左右对称**。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, trails or rings (only her solid blades get the dark #0A081C outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson ramp (#FFFFFF, #FFC8D8, #F32D5B, #D51046, #A80A36, #750629) and a silver ramp (#FFFFFF, #E8F4FC, #BDCFDF, #96ACC3, #6C7A98).
Effect: a DASH STRIKE on the target, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 squares across; 2 two thick crimson slash arcs crossing in an X 18 squares across, white cores; 3 the X at its brightest with a silver-white ring 12 squares across; 4 crimson shards flying out at mirrored places; 5 a few fading shards.
Layout: one horizontal row of 5 equal square cells, image size 1600x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `irelia_fx_mark.png`：被 E / R 打中的标记（敌方英雄头上，循环），4 帧

被 E 或 R 打中的英雄身上的「不稳」标记（Q 打它会刷新）：头顶上方一个小小的刀形印记（青色宝石在中间、红色的刀尖朝上下），一闪一闪。**左右对称**。约 10 格，画在格子上部（人头上方）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, trails or rings (only her solid blades get the dark #0A081C outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson ramp (#FFFFFF, #FFC8D8, #F32D5B, #D51046, #A80A36, #750629) and a cyan ramp (#FFFFFF, #D8FBFF, #84EBFF, #27CFF3, #098FBA).
Effect: a SMALL MARK over the head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a diamond sigil 8 squares tall and 6 wide - a cyan gem in the middle, two small crimson blade points above and below it - pulsing brighter and dimmer, two 1-square cyan sparkles at its sides.
Layout: one horizontal row of 4 equal 12:48 cells, image size 768x768 (each cell 192x768, 16 px a square); the sigil's middle 4 squares from the TOP of the cell, centered; the rest of the cell empty. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `irelia_fx_e_cast.png`：E 比翼双刃出手（她脚下），5 帧

她把第一把刀插在脚边：脚下一圈青色的光闪起来再收回（地上的椭圆，宽是高的 2–3 倍），中间一道竖着的白光一闪。**左右对称**，**画在格子下部（她的脚下）**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, trails or rings (only her solid blades get the dark #0A081C outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan ramp (#FFFFFF, #D8FBFF, #84EBFF, #27CFF3, #098FBA) and a silver ramp (#FFFFFF, #E8F4FC, #BDCFDF, #96ACC3, #6C7A98).
Effect: a FLASH AT HER FEET, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white vertical glint 2 squares wide and 8 tall rising from the bottom middle; 2 a flat cyan ellipse 24 squares wide and 8 tall round it on the ground, white inner rim; 3 the ellipse at its brightest; 4 the ellipse breaking into cyan dashes; 5 a few fading dashes.
Layout: one horizontal row of 5 equal 26:12 cells, image size 2080x192 (each cell 416x192, 16 px a square); the ellipse's middle 4 squares above the cell's bottom, centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `irelia_fx_e_line.png`：E 两把刀会合的那条线（从她到目标后方，转向），6 帧

E 的两把刀一把在她脚边、一把在目标身后，互相飞向对方，中间连成一道发光的线，线上的敌人被眩晕。画成**朝右的一整条线：左端是她，右端 80 格外**，两把刀从两端往中间飞（刀用她身边那种绯红刀刃、深蓝刀背、银色刀尖、青色宝石的样子），后面拖着青色的细光线，第 5 帧在中间会合一闪，第 6 帧整条线亮一下。**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, trails or rings (only her solid blades get the dark #0A081C outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson ramp (#FFFFFF, #FFC8D8, #F32D5B, #D51046, #A80A36, #750629), a cyan ramp (#FFFFFF, #D8FBFF, #84EBFF, #27CFF3, #098FBA), a silver ramp (#FFFFFF, #E8F4FC, #BDCFDF, #96ACC3, #6C7A98) and a navy ramp for the blades' backs (#4D6085, #344367, #222B51, #131A37, #0A081C).
Effect: a LINE BETWEEN TWO BLADES pointing RIGHT, 6 frames, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): the picture spans the whole line, its LEFT edge is where she stands and its RIGHT edge 80 squares away. HER BLADE: a slim crescent blade like a curved leaf, crimson edge, navy back, a silver tip and a small cyan gem at its base, a 1-square dark outline - exactly the blades floating round her in design/irelia_design.png, lying flat along the line, 9 squares long. 1 a blade at each end; 2-4 the two blades flying toward the middle, each trailing a thin cyan beam (2 squares thick, white core) back to its end; 5 the blades meet in the middle in a white-cyan flash 10 squares tall; 6 the whole line glowing cyan-white 3 squares thick, the blades gone.
Layout: one horizontal row of 6 equal 82:14 cells, image size 7872x224 (each cell 1312x224, 16 px a square); the line on the cell's middle row from the LEFT edge to the RIGHT edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `irelia_fx_e_hit.png`：E 线上的敌人被打中（目标身上），4 帧

E 的线扫过敌人：青色的横向光闪一下、中心白光，几道青色短线往外跳。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, trails or rings (only her solid blades get the dark #0A081C outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan ramp (#FFFFFF, #D8FBFF, #84EBFF, #27CFF3, #098FBA) and a crimson ramp (#FFFFFF, #FFC8D8, #F32D5B, #D51046, #A80A36, #750629).
Effect: a CYAN SLICE HIT on the target, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white horizontal glint 6 squares long; 2 a cyan flash 14 squares wide and 6 tall, white core, a thin crimson rim; 3 short cyan streaks jumping out at mirrored places; 4 fading streaks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `irelia_fx_e_stun.png`：E 眩晕（敌人头上，循环），4 帧

被 E 眩晕的敌人头顶：三片很小的青色刀形光片绕着转（从斜上方看的小椭圆）。**左右对称**（每帧逐格对称，所以画成两边对称地转）。约 14 格宽，画在格子上部（人头上方）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, trails or rings (only her solid blades get the dark #0A081C outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan ramp (#FFFFFF, #D8FBFF, #84EBFF, #27CFF3, #098FBA) and a silver ramp (#FFFFFF, #E8F4FC, #BDCFDF, #96ACC3, #6C7A98).
Effect: STUN over the head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a small flat ellipse of light 14 squares wide and 5 tall with three tiny cyan-silver leaf glints on it (one in the middle front, two at mirrored sides), the glints moving outward and back in turn.
Layout: one horizontal row of 4 equal 16:48 cells, image size 1024x768 (each cell 256x768, 16 px a square); the ellipse's middle 4 squares from the TOP of the cell, centered; the rest of the cell empty. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `irelia_fx_w_on.png`：W 距破之舞蓄力（她身上，循环），4 帧

W 蓄力时她用刀护身、受到的物理伤害减半：她身体两侧各一把刀交叉成盾的样子（刀尖朝上、在她头部两侧，左右对称），刀上有青色的光在流动，**中间人形位置留空**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, trails or rings (only her solid blades get the dark #0A081C outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson ramp (#FFFFFF, #FFC8D8, #F32D5B, #D51046, #A80A36, #750629), a cyan ramp (#FFFFFF, #D8FBFF, #84EBFF, #27CFF3, #098FBA), a silver ramp (#FFFFFF, #E8F4FC, #BDCFDF, #96ACC3, #6C7A98) and a navy ramp for the blades' backs (#4D6085, #344367, #222B51, #131A37, #0A081C).
Effect: a GUARD OF BLADES round her, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the figure's place in the middle (16 x 40 squares, its bottom on the cell's bottom) EMPTY: HER BLADE: a slim crescent blade like a curved leaf, crimson edge, navy back, a silver tip and a small cyan gem at its base, a 1-square dark outline - exactly the blades floating round her in design/irelia_design.png, 12 squares long - one on each side of the figure, standing upright at shoulder height with the tips leaning in over the head, mirrored; a thin cyan glow running along each blade's edge from base to tip, moving up a few squares each frame.
Layout: one horizontal row of 4 equal 36:44 cells, image size 2304x704 (each cell 576x704, 16 px a square). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `irelia_fx_w_slash.png`：W 出手（她身上），5 帧

W 蓄满出手的一瞬：她身前身后各一道红色的弧形刀光（左右对称地展开），中心白光一闪。**左右对称**（游戏不给它镜像，往哪边砍由 `w_line` 表现）。约 30 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, trails or rings (only her solid blades get the dark #0A081C outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson ramp (#FFFFFF, #FFC8D8, #F32D5B, #D51046, #A80A36, #750629) and a silver ramp (#FFFFFF, #E8F4FC, #BDCFDF, #96ACC3, #6C7A98).
Effect: a RELEASE BURST round her, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the figure's place (16 x 40 squares, bottom on the cell's bottom) EMPTY: 1 a white flash at chest height 6 squares across; 2 two crimson crescent arcs opening to both sides, 30 squares from tip to tip, white cores; 3 the arcs at their widest; 4 the arcs thinning into silver streaks; 5 fading.
Layout: one horizontal row of 5 equal 32:44 cells, image size 2560x704 (each cell 512x704, 16 px a square); the flash at chest height (26 squares above the cell's bottom), centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `irelia_fx_w_line.png`：W 那一刀扫出去的刀光（从她往前，转向），5 帧

W 的一刀沿直线砍出去：一道又宽又亮的红色刀光（像月牙形的冲击波）从她身前往前冲到 55 格外，后面拖着红色的残光。画成**朝右的一整条线：左端是她，右端 55 格外**。**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, trails or rings (only her solid blades get the dark #0A081C outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson ramp (#FFFFFF, #FFC8D8, #F32D5B, #D51046, #A80A36, #750629) and a silver ramp (#FFFFFF, #E8F4FC, #BDCFDF, #96ACC3, #6C7A98).
Effect: a SLASH WAVE pointing RIGHT, 5 frames, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): the picture spans the whole line, its LEFT edge is where she stands and its RIGHT edge 55 squares away; a crimson crescent wave 12 squares tall (its bow toward the right, white core) travelling from the left end to the right end over frames 1-4, a crimson trail 4 squares thick behind it, thinning; 5 only the fading trail.
Layout: one horizontal row of 5 equal 57:16 cells, image size 4560x256 (each cell 912x256, 16 px a square); the wave on the cell's middle row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `irelia_fx_w_hit.png`：W 打中（目标身上），4 帧

W 的刀光扫过目标：一道粗的横向红色刀光闪过，白芯，几片红色光屑。**左右对称**。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, trails or rings (only her solid blades get the dark #0A081C outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson ramp (#FFFFFF, #FFC8D8, #F32D5B, #D51046, #A80A36, #750629) and a silver ramp (#FFFFFF, #E8F4FC, #BDCFDF, #96ACC3, #6C7A98).
Effect: a HEAVY SLASH HIT on the target, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white horizontal flash 8 squares long; 2 a thick crimson horizontal slash 16 squares long and 4 tall, white core; 3 crimson shards flying out at mirrored places; 4 fading.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `irelia_fx_r_blades.png`：R 先锋之刃飞出去的一群刀（飞行中，循环），4 帧

大招：她身边的刀全部飞出去：画成朝右飞的一群刀（5 把，排成箭头形：最前面 1 把、上下各 2 把错开在后面），每把都是她身边那种刀的样子，后面拖着红色的光尾。**上下对称**。约 26 格长、16 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, trails or rings (only her solid blades get the dark #0A081C outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson ramp (#FFFFFF, #FFC8D8, #F32D5B, #D51046, #A80A36, #750629), a cyan ramp (#FFFFFF, #D8FBFF, #84EBFF, #27CFF3, #098FBA), a silver ramp (#FFFFFF, #E8F4FC, #BDCFDF, #96ACC3, #6C7A98) and a navy ramp for the blades' backs (#4D6085, #344367, #222B51, #131A37, #0A081C).
Effect: a VOLLEY OF BLADES flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): HER BLADE: a slim crescent blade like a curved leaf, crimson edge, navy back, a silver tip and a small cyan gem at its base, a 1-square dark outline - exactly the blades floating round her in design/irelia_design.png, 8 squares long, pointing right; five of them in an arrowhead - one in front on the middle row, two above and two below it stepped back 4 squares each, mirrored - every blade trailing a crimson streak 6 squares long; the streaks flicker and the blades bob a square in turn.
Layout: one horizontal row of 4 equal 28:18 cells, image size 1792x288 (each cell 448x288, 16 px a square); the front blade's tip 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `irelia_fx_r_hit.png`：R 打中（目标身上），5 帧

大招的刀群砍中：几道红色刀光同时交叉（米字形），中心白光，外面一圈青色光环，碎光往外飞。**左右对称**。约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, trails or rings (only her solid blades get the dark #0A081C outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson ramp (#FFFFFF, #FFC8D8, #F32D5B, #D51046, #A80A36, #750629), a cyan ramp (#FFFFFF, #D8FBFF, #84EBFF, #27CFF3, #098FBA) and a silver ramp (#FFFFFF, #E8F4FC, #BDCFDF, #96ACC3, #6C7A98).
Effect: a VOLLEY HIT on the target, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 8 squares across; 2 three crimson slashes crossing in a star 20 squares across (one horizontal, two diagonal), white cores; 3 a cyan ring 16 squares across round them; 4 crimson and cyan shards flying out at mirrored places; 5 fading shards.
Layout: one horizontal row of 5 equal square cells, image size 1760x352 (each cell 352x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `irelia_fx_r_wall_v.png`：R 刀墙（地上一圈插着的刀，5 秒），10 帧

大招打中后，刀插在地上围成一圈刀墙（圆圈从斜上方看是椭圆，宽 60 格、高约 26 格），里面的敌人被减速。10 帧播一遍：1–2 刀从地里冒出来，3–8 刀墙立着、刀上的青色宝石一闪一闪、地上的圈有红光流动，9–10 刀往下沉、光淡掉。刀是她身边那种刀，刀尖朝上、竖着插。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, trails or rings (only her solid blades get the dark #0A081C outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson ramp (#FFFFFF, #FFC8D8, #F32D5B, #D51046, #A80A36, #750629), a cyan ramp (#FFFFFF, #D8FBFF, #84EBFF, #27CFF3, #098FBA), a silver ramp (#FFFFFF, #E8F4FC, #BDCFDF, #96ACC3, #6C7A98) and a navy ramp for the blades' backs (#4D6085, #344367, #222B51, #131A37, #0A081C).
Effect: a RING WALL OF BLADES on the ground, 10 frames played once, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse 60 squares wide and 26 tall seen from above at an angle; twelve of her blade: a slim crescent blade like a curved leaf, crimson edge, navy back, a silver tip and a small cyan gem at its base, a 1-square dark outline - exactly the blades floating round her in design/irelia_design.png, 7 squares tall, standing upright round the ellipse's rim with their tips up (the front ones lower on the picture, the back ones higher, the side ones smaller); a thin crimson glow line on the ground along the rim. 1-2 the blades rising out of the ground; 3-8 the wall standing, the cyan gems twinkling in turn and a brighter crimson pulse running round the rim; 9-10 the blades sinking, the glow fading.
Layout: one horizontal row of 10 equal 64:36 cells, image size 10240x576 (each cell 1024x576, 16 px a square); the ellipse's middle 16 squares above the cell's bottom, centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `irelia_fx_r_slow.png`：R 刀群打中的减速（脚下，循环），4 帧

被大招打中的敌人脚下一圈红色的小刀印（地上的椭圆），慢慢转。**左右对称**，画在格子下部（脚下）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, trails or rings (only her solid blades get the dark #0A081C outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson ramp (#FFFFFF, #FFC8D8, #F32D5B, #D51046, #A80A36, #750629).
Effect: a SLOW RING at the feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat crimson ellipse 18 squares wide and 6 tall on the ground, six tiny blade-shaped notches on it (mirrored) pulsing in turn, white highlights on the front.
Layout: one horizontal row of 4 equal 20:8 cells, image size 1280x128 (each cell 320x128, 16 px a square); the ellipse's middle 3 squares above the cell's bottom, centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `irelia_fx_r_wslow.png`：在刀墙里的减速（脚下，循环），4 帧

站在刀墙里的敌人脚下一圈淡一点的红色光圈（比 r_slow 小一点、暗一点），一闪一闪。**左右对称**，画在格子下部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, trails or rings (only her solid blades get the dark #0A081C outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson ramp (#FFFFFF, #FFC8D8, #F32D5B, #D51046, #A80A36, #750629).
Effect: a FAINT SLOW RING at the feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a thin crimson ellipse 16 squares wide and 5 tall on the ground, dimmer than a full slow (mid crimson, no white), a brighter dash running round it.
Layout: one horizontal row of 4 equal 18:8 cells, image size 1152x128 (each cell 288x128, 16 px a square); the ellipse's middle 3 squares above the cell's bottom, centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） | 图集 |
|---|---|---|---|
| `irelia_fx_a_hit` | view_effects `league_irelia_a_hit`（跟随目标，画在人物上面；左右对称） | 14 | league_irelia_fx |
| `irelia_fx_p_hit` | view_effects `league_irelia_p_hit`（跟随目标；左右对称） | 12 | league_irelia_fx |
| `irelia_fx_pv4` | view_buffs `league_irelia_pv4`（画在人物上面，循环；左右对称） | 34 × 42 | league_irelia_fx |
| `irelia_fx_q_hit` | view_effects `league_irelia_q_hit`（跟随目标；左右对称） | 18 | league_irelia_fx |
| `irelia_fx_mark` | view_buffs `league_irelia_mark`（画在人物上面，5 秒；左右对称） | 10 | league_irelia_fx |
| `irelia_fx_e_cast` | CasterViewEffect `league_irelia_e_cast`（跟随她，画在人物上面；左右对称） | 24 × 10 | league_irelia_fx |
| `irelia_fx_e_line` | view_projectiles `league_irelia_e_line`（LineRangeProjectile 的画面：整条线，从她到 80 格外，朝方向转；上下对称） | 80 × 12 | league_irelia_big |
| `irelia_fx_e_hit` | view_effects `league_irelia_e_hit`（跟随目标；左右对称） | 14 | league_irelia_fx |
| `irelia_fx_e_stun` | view_buffs `league_irelia_e_stun`（画在人物上面，循环 0.75 秒；左右对称） | 14 × 6 | league_irelia_fx |
| `irelia_fx_w_on` | view_buffs `league_irelia_w_on`（画在人物上面，蓄力约 1 秒；左右对称） | 34 × 40 | league_irelia_fx |
| `irelia_fx_w_slash` | CasterViewEffect `league_irelia_w_slash`（跟随她，画在人物上面；左右对称） | 30 | league_irelia_big |
| `irelia_fx_w_line` | view_projectiles `league_irelia_w_line`（LineRangeProjectile 的画面：整条线，从她到 55 格外，朝方向转；上下对称） | 55 × 14 | league_irelia_big |
| `irelia_fx_w_hit` | view_effects `league_irelia_w_hit`（跟随目标；左右对称） | 16 | league_irelia_fx |
| `irelia_fx_r_blades` | view_projectiles `league_irelia_r_blades`（直线弹，朝飞行方向转，画成朝右飞；上下对称） | 26 × 16 | league_irelia_big |
| `irelia_fx_r_hit` | view_effects `league_irelia_r_hit`（跟随目标；左右对称） | 20 | league_irelia_fx |
| `irelia_fx_r_wall_v` | ViewEffect `league_irelia_r_wall_v`（在落点，画在人物下面 z -1，播一遍 5 秒；左右对称） | 60 × 28 | league_irelia_big |
| `irelia_fx_r_slow` | view_buffs `league_irelia_r_slow`（画在人物下面 z -1，2 秒；左右对称） | 18 × 6 | league_irelia_fx |
| `irelia_fx_r_wslow` | view_buffs `league_irelia_r_wslow`（画在人物下面 z -1，刀墙里每 10 tick 续；左右对称） | 16 × 6 | league_irelia_fx |

- `e_line`、`w_line`：LineRangeProjectile 的画面从她铺到线尽头（champion-data「Cone / fan」：精灵中心在线的中点，左端在施法者）；按每条格子切，确认上下对称；`e_line` 循环（repeat），帧时长让 6 帧盖住 delay 24 tick。
- `r_blades`：直线弹，y_offset 0，朝飞行方向转；`r_wall_v`：ViewEffect 在落点（z -1），10 帧铺满 r_wall_t 150 tick（第 1–2、9–10 帧短，中间长）。
- `e_cast`、`w_slash` 是 CasterViewEffect（不转、不镜像）：逐格左右对称；`pv4`、`w_on`、`mark`、`e_stun` 画在人物上面，`r_slow`、`r_wslow` 在脚下（z -1）。
- 用 `pixel_1x/` 切格（import_syndra 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。
