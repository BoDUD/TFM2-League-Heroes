# 诺拉与悠米：给 Codex 的特效提示词（第 3 步）

> **这一份是 15 张特效图。** 造型已定（`design/norra_design.png`：约德尔小法师，高高的青绿礼帽、粉框大圆眼镜、两只垂耳、蓝紫长袍红腰带，近侧手里握着一个**金色小圆环**——她的次元门）。诺拉在游戏里是**高清**的（每个游戏格子里 2×2 个细像素），36 格高、24 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/norra_size.png`：诺拉缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里诺拉自己的特效贴图（金色花纹门环、紫色漩涡、金色螺旋、小星星、青色传送门圈），按用在我们哪张特效分好了行；`refs/video_tft_cast.jpg` 是金铲铲视频里她施法（紫光）、普攻（金色光弹）的样子，`refs/video_wr_ult.jpg` 是英雄联盟手游里她大招的**金色同心次元门**。只在本地用。
> - **诺拉是班德尔城的次元门法师，特效都是童话风的魔法**：**金色花纹的门环**（带卷卷的藤蔓花纹）、门里**紫色的漩涡**、**粉金色的小星星**、Q 的**纸画颜料**（米色纸上的品红、青、紫、金黄颜料漩涡）；不要光滑的霓虹光束，也不要写实的火和烟。
> - **特效要亮**：每道光、每个门环都有最亮一档或白色的高光，暗底上一眼能看见。
> - **光、门环、颜料、星星没有黑描边**；**只有“东西”（铁砧、巨书、药瓶）有 1 格近黑描边**。
> - **围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人。
> - **对称**：除了两个弹道和地上的纸画，所有画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）——铁砧、巨书、药瓶都**正面**看。**弹道**（`a_bolt`、`q_ball`）**朝右画、尾巴在左边，严格上下对称**（游戏按方向转这张图）。**地上的纸画 `q_paint` 左右、上下都要对称**（它是地面区域，游戏可能把它转半圈）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `norra_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、按上面的要求逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/norra_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/norra_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 手指一指，从金环里射出一颗金色魔法弹 | `a_bolt` · `a_hit` |
| 被动「最佳好友」 | 悠米趴在书上骑在一个队友头上（悠米的图另外做），每隔几秒给他回血、分他法强 | `p_heal` |
| 技能 1 =「次元门狂欢」 | 抛出次元球，落地爆炸、把地面涂成纸画持续掉血；上一片纸画还在时，球会再弹到附近另一个敌人那里炸一次 | `q_ball` · `q_blast` · `q_hit` · `q_paint` |
| 技能 2 =「异界来物」 | 在队友身边开门给他护盾；敌人头顶开门，轮流掉下铁砧（眩晕）/ 药水（给自己人回血）/ 巨书（击飞） | `e_guard` · `e_anvil_hit` · `e_potion` · `e_book_hit` |
| 大招 =「门槛之书」 | 敌人头顶打开同心的大次元门，巨大书页落下：伤害、眩晕、「纸化」（受到的伤害变多）；范围里的队友得到护盾 | `r_warn` · `r_book` · `r_hit` · `r_paper` · `e_guard` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、门环、颜料没有黑描边，也不要用最深的颜色给形状描一圈边**（铁砧、巨书、药瓶除外）。
- **都是童话风的次元门魔法**：金色花纹门环、紫色漩涡、粉金小星星、纸和颜料；每个形状 2–3 档平涂。
- **要亮**：每个形状都有最亮一档或白色的高光。
- 颜色（按每条写的用）：
  - 金色花纹：`#FFFFFF`、`#FFF4C4`、`#FFD95A`、`#F2B12E`、`#C77A16`、`#7E4410`；
  - 紫色漩涡：`#F4E6FF`、`#C9A2FF`、`#9A62F0`、`#6A34D0`、`#3E1C8C`、`#22104E`；
  - 粉金星星：`#FFE8F4`、`#FF9CCB`、`#F05A9E`、`#B02A6E`；
  - 青色门圈：`#E6FFFF`、`#8FF0F0`、`#44C8D2`、`#1E8C9E`、`#0E4E60`；
  - 米色纸：`#FFFDF4`、`#F2E6CC`、`#D8C6A0`、`#A8906A`；
  - 颜料：`#F05A9E`、`#44C8D2`、`#9A62F0`、`#FFD95A`；
  - 铁砧：`#E8EEF2`、`#A8B4BE`、`#6E7A86`、`#3E4650`、`#1E2228`；
  - 巨书：`#F2DCA8`、`#C4472E`、`#8A2A1C`、`#4E160E`、`#FFD95A`、`#C77A16`；
  - 治疗：`#FFFFFF`、`#FFF0C8`、`#C8F0A0`、`#7CD87A`、`#FF9CCB`；
- 打中、爆发居中画，不旋转；地面上的圈（预警圈、纸画、冲击波）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（15 张）

15 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `norra_fx_a_bolt.png`：普攻：魔法弹，4 帧循环

她手指一指飞出去的**魔法弹**：一颗金色的四角小星星，后面拖着一小条紫色的彗尾和两三粒粉色星屑（视频里普攻是一道金光；参考 starsprite、vex_comet）。**朝右飞，上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold filigree ramp (#FFFFFF, #FFF4C4, #FFD95A, #F2B12E, #C77A16, #7E4410), a violet portal ramp (#F4E6FF, #C9A2FF, #9A62F0, #6A34D0, #3E1C8C, #22104E), a pink star ramp (#FFE8F4, #FF9CCB, #F05A9E, #B02A6E).
Effect: A STAR BOLT, 4 looping frames, pointing RIGHT (its tail on the left), SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight): a bright gold four-point star 5 squares across at the right with a white core, a tapering violet comet tail 6 squares long behind it, two pink sparkle flecks in the tail; frames 1-4 the star twinkling and the tail flickering. everything is a YORDLE PORTAL MAGE'S whimsical magic: GOLD FILIGREE portal rings with curling vines, a VIOLET SWIRL inside each portal, little pink-gold STARS and sparkles, and for the paint cream PAPER with bright ink swirls; flat shades, crisp shapes; no smooth neon beams, no realistic fire or smoke.
Layout: one horizontal row of 4 equal 12:8 cells, image size 768x128 (each cell 192x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `norra_fx_a_hit.png`：普攻：打中，3 帧

魔法弹打中：一圈金色的小花纹门环一闪，迸出几颗粉金色小星星（参考 basicattack_portal、starsprite）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold filigree ramp (#FFFFFF, #FFF4C4, #FFD95A, #F2B12E, #C77A16, #7E4410), a pink star ramp (#FFE8F4, #FF9CCB, #F05A9E, #B02A6E).
Effect: A STAR HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold star flash 6 squares across; 2 a thin gold filigree ring 10 across with little curls, four small pink-gold stars popping out at mirrored places; 3 the ring fading, the stars further out and smaller. everything is a YORDLE PORTAL MAGE'S whimsical magic: GOLD FILIGREE portal rings with curling vines, a VIOLET SWIRL inside each portal, little pink-gold STARS and sparkles, and for the paint cream PAPER with bright ink swirls; flat shades, crisp shapes; no smooth neon beams, no realistic fire or smoke.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `norra_fx_p_heal.png`：最佳好友：悠米的治疗，4 帧

悠米每隔几秒给她骑着的队友回血：一颗粉色的小爱心和几颗暖白、浅绿的光点往上飘。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a soft heal ramp (#FFFFFF, #FFF0C8, #C8F0A0, #7CD87A, #FF9CCB), a pink star ramp (#FFE8F4, #FF9CCB, #F05A9E, #B02A6E).
Effect: A LITTLE HEAL, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small pink heart 3 squares across low in the middle with two warm white plus sparkles at its sides; 2 the heart rising, soft green light dots around it; 3 the heart higher and paler, the dots spreading; 4 the last dots fading. everything is a YORDLE PORTAL MAGE'S whimsical magic: GOLD FILIGREE portal rings with curling vines, a VIOLET SWIRL inside each portal, little pink-gold STARS and sparkles, and for the paint cream PAPER with bright ink swirls; flat shades, crisp shapes; no smooth neon beams, no realistic fire or smoke.
Layout: one horizontal row of 4 equal 12:16 cells, image size 768x256 (each cell 192x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `norra_fx_q_ball.png`：次元门狂欢：抛出去的次元球，4 帧循环

抛出去的**次元球**：一个紫色的漩涡球（里面一圈圈往里转），外面套着一圈金色的花纹门环，几颗小星星绕着转（参考 mask、mask_swirl、basicattack_portal；视频里施法时她身边那团紫光）。它在空中转着飞，**上下对称**（朝右飞），4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet portal ramp (#F4E6FF, #C9A2FF, #9A62F0, #6A34D0, #3E1C8C, #22104E), a gold filigree ramp (#FFFFFF, #FFF4C4, #FFD95A, #F2B12E, #C77A16, #7E4410), a pink star ramp (#FFE8F4, #FF9CCB, #F05A9E, #B02A6E).
Effect: A PORTAL BALL, 4 looping frames, pointing RIGHT (its tail on the left), SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight): a round violet swirl ball 10 squares across (a spiral of lighter violet turning inward to a white-violet core) inside a thin gold filigree ring 14 across with little curls, two tiny pink-gold stars orbiting at mirrored places; frames 1-4 the spiral turning and the stars moving round. everything is a YORDLE PORTAL MAGE'S whimsical magic: GOLD FILIGREE portal rings with curling vines, a VIOLET SWIRL inside each portal, little pink-gold STARS and sparkles, and for the paint cream PAPER with bright ink swirls; flat shades, crisp shapes; no smooth neon beams, no realistic fire or smoke.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `norra_fx_q_blast.png`：次元门狂欢：次元球爆开，7 帧

次元球落地爆开：先一下紫白的闪光，紫色漩涡和金色门环往外炸开，**四周甩出一团团彩色颜料**（品红、青、紫、金黄）和几片米色纸屑，最后颜料落到地上（地上的纸画是另一张 `q_paint`）。爆炸中心在格子下部（地面），往上炸起来。**左右对称**，7 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet portal ramp (#F4E6FF, #C9A2FF, #9A62F0, #6A34D0, #3E1C8C, #22104E), a gold filigree ramp (#FFFFFF, #FFF4C4, #FFD95A, #F2B12E, #C77A16, #7E4410), bright ink colours (#F05A9E, #44C8D2, #9A62F0, #FFD95A), a cream paper ramp (#FFFDF4, #F2E6CC, #D8C6A0, #A8906A).
Effect: A PORTAL BURST WITH PAINT, 7 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): the burst sits on the ground line 6 squares above the bottom. 1 a white-violet flash 10 squares across; 2 a violet swirl blast 22 across with a gold filigree ring round it; 3 the blast 34 across, blobs of bright ink (magenta, teal, violet, gold) flung out at mirrored places, cream paper scraps; 4 the ink blobs 44 across and falling, the swirl breaking up; 5 the blobs splashing down near the ground line, little stars; 6 paint drops and paper scraps settling; 7 a few fading sparkles. everything is a YORDLE PORTAL MAGE'S whimsical magic: GOLD FILIGREE portal rings with curling vines, a VIOLET SWIRL inside each portal, little pink-gold STARS and sparkles, and for the paint cream PAPER with bright ink swirls; flat shades, crisp shapes; no smooth neon beams, no realistic fire or smoke.
Layout: one horizontal row of 7 equal 48:40 cells, image size 5376x640 (each cell 768x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `norra_fx_q_hit.png`：次元门狂欢：被砸中，3 帧

被次元球的爆炸打中：身上溅了一团彩色颜料，一颗小星星。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from bright ink colours (#F05A9E, #44C8D2, #9A62F0, #FFD95A), a pink star ramp (#FFE8F4, #FF9CCB, #F05A9E, #B02A6E).
Effect: A PAINT SPLAT HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small magenta-and-teal ink splat 6 squares across with a white core; 2 the splat 10 across with drops at mirrored places and a little gold star; 3 the drops falling and fading. everything is a YORDLE PORTAL MAGE'S whimsical magic: GOLD FILIGREE portal rings with curling vines, a VIOLET SWIRL inside each portal, little pink-gold STARS and sparkles, and for the paint cream PAPER with bright ink swirls; flat shades, crisp shapes; no smooth neon beams, no realistic fire or smoke.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `norra_fx_q_paint.png`：次元门狂欢：地上的纸画，6 帧循环

被涂色的地面（金铲铲里叫「纸化」，诺拉来自班德尔城的绘本世界）：**地上铺开一大片米色纸**，上面用彩色颜料画出卷卷的漩涡和星星（品红、青、紫、金黄），边缘是纸撕开的毛边，颜色慢慢流动、星星一闪一闪（站在上面的敌人一直掉血）。这是地上区域的图，游戏会把它转半圈，所以**左右、上下都要对称**。最大 **横 60 格、纵 20 格**。6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cream paper ramp (#FFFDF4, #F2E6CC, #D8C6A0, #A8906A), bright ink colours (#F05A9E, #44C8D2, #9A62F0, #FFD95A), a gold filigree ramp (#FFFFFF, #FFF4C4, #FFD95A, #F2B12E, #C77A16, #7E4410).
Effect: A PAINTED PAPER GROUND, 6 looping frames, SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame, square for square (it lies on the ground and the game may turn it half round), on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall): a big ellipse of cream paper 60 squares wide and 20 tall with a torn, wavy paper edge, painted with bright ink swirls - magenta, teal, violet and gold curls and small spirals - and a few little gold stars; frames 1-6 the ink swirls slowly turning and the stars twinkling in turn. Flat colours, crisp pixel shapes. everything is a YORDLE PORTAL MAGE'S whimsical magic: GOLD FILIGREE portal rings with curling vines, a VIOLET SWIRL inside each portal, little pink-gold STARS and sparkles, and for the paint cream PAPER with bright ink swirls; flat shades, crisp shapes; no smooth neon beams, no realistic fire or smoke.
Layout: one horizontal row of 6 equal 64:22 cells, image size 6144x352 (each cell 1024x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `norra_fx_e_anvil_hit.png`：异界来物：铁砧从次元门掉下来，8 帧

目标头顶高处打开一个**金色花纹的小次元门**（横着的椭圆，里面紫色漩涡），一个**铁砧**从门里掉下来，砸在目标站的地方，砸出一圈灰尘和金色小星星（被砸的人晕一下）。铁砧正面看、左右对称，**有 1 格近黑描边**（它是个东西）；门、光、灰尘、星星没有描边。砸的地方在格子底部往上 6 格。**左右对称**，8 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold filigree ramp (#FFFFFF, #FFF4C4, #FFD95A, #F2B12E, #C77A16, #7E4410), a violet portal ramp (#F4E6FF, #C9A2FF, #9A62F0, #6A34D0, #3E1C8C, #22104E), an iron ramp (#E8EEF2, #A8B4BE, #6E7A86, #3E4650, #1E2228), a pink star ramp (#FFE8F4, #FF9CCB, #F05A9E, #B02A6E).
Effect: AN ANVIL OUT OF A PORTAL, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small gold filigree portal (a flat ellipse 16 squares wide and 5 tall with a violet swirl inside) opening near the top of the cell; 2 an iron anvil seen from the FRONT (12 wide, 8 tall, flat top, narrow waist, wide base; grey iron with a 1-square near-black outline) coming out of the portal; 3-4 the anvil falling straight down; 5 the anvil slamming onto the ground line 6 squares above the bottom, a white flash and a ring of dust 24 wide at its foot; 6 dust puffs at both sides and little gold stars spinning above it; 7 the portal closing; 8 the anvil and the dust fading. everything is a YORDLE PORTAL MAGE'S whimsical magic: GOLD FILIGREE portal rings with curling vines, a VIOLET SWIRL inside each portal, little pink-gold STARS and sparkles, and for the paint cream PAPER with bright ink swirls; flat shades, crisp shapes; no smooth neon beams, no realistic fire or smoke.
Layout: one horizontal row of 8 equal 36:64 cells, image size 4608x1024 (each cell 576x1024, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `norra_fx_e_book_hit.png`：异界来物：巨书从次元门掉下来，8 帧

同样一个**金色次元门**在目标头顶打开，一本**合着的巨大厚书**（正面看：棕红皮面、金色包角和搭扣，像悠米的书）掉下来，砸到地上啪地**摊开**，书页和纸屑往上翻飞（被砸的人被击飞）。书有 1 格近黑描边。砸的地方在格子底部往上 6 格。**左右对称**，8 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold filigree ramp (#FFFFFF, #FFF4C4, #FFD95A, #F2B12E, #C77A16, #7E4410), a violet portal ramp (#F4E6FF, #C9A2FF, #9A62F0, #6A34D0, #3E1C8C, #22104E), a book ramp (#F2DCA8, #C4472E, #8A2A1C, #4E160E, #FFD95A, #C77A16), a cream paper ramp (#FFFDF4, #F2E6CC, #D8C6A0, #A8906A).
Effect: A GIANT BOOK OUT OF A PORTAL, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small gold filigree portal (a flat ellipse 16 squares wide and 5 tall with a violet swirl inside) opening near the top of the cell; 2 a giant closed book seen from the FRONT cover (14 wide, 18 tall, red-brown leather, gold corners and a gold clasp in the middle, a 1-square near-black outline) coming out; 3-4 the book falling straight down; 5 the book slamming onto the ground line 6 squares above the bottom and bursting OPEN flat (now 30 wide and 8 tall, cream pages fanned up in the middle), a white flash; 6 pages and paper scraps flying up at both sides; 7 the portal closing, scraps falling; 8 the book and scraps fading. everything is a YORDLE PORTAL MAGE'S whimsical magic: GOLD FILIGREE portal rings with curling vines, a VIOLET SWIRL inside each portal, little pink-gold STARS and sparkles, and for the paint cream PAPER with bright ink swirls; flat shades, crisp shapes; no smooth neon beams, no realistic fire or smoke.
Layout: one horizontal row of 8 equal 40:64 cells, image size 5120x1024 (each cell 640x1024, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `norra_fx_e_potion.png`：异界来物：药水，6 帧

次元门里掉出一瓶药水：队友头顶一个小小的金色门环里掉出**一个圆肚小药瓶**（粉色药水、软木塞，有描边），落到头上啪地碎成粉色、浅绿的光点洒下来（回血）。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold filigree ramp (#FFFFFF, #FFF4C4, #FFD95A, #F2B12E, #C77A16, #7E4410), a pink star ramp (#FFE8F4, #FF9CCB, #F05A9E, #B02A6E), a soft heal ramp (#FFFFFF, #FFF0C8, #C8F0A0, #7CD87A, #FF9CCB).
Effect: A POTION POPS, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a tiny gold filigree ring 8 squares wide near the top of the cell; 2 a little round potion bottle (4 wide, 5 tall, pink liquid, a cork, a 1-square near-black outline) dropping out of it; 3 the bottle lower, over the unit's head (the middle of the cell); 4 the bottle bursting into pink and soft green light drops and a white flash; 5 the drops raining down at both sides; 6 the last drops fading. The bottom half (the unit's body) mostly empty. everything is a YORDLE PORTAL MAGE'S whimsical magic: GOLD FILIGREE portal rings with curling vines, a VIOLET SWIRL inside each portal, little pink-gold STARS and sparkles, and for the paint cream PAPER with bright ink swirls; flat shades, crisp shapes; no smooth neon beams, no realistic fire or smoke.
Layout: one horizontal row of 6 equal 14:26 cells, image size 1344x416 (each cell 224x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `norra_fx_e_guard.png`：异界来物 / 门槛之书：次元门护盾，6 帧循环

护盾：人身上套着一圈**金色花纹的门环**（从斜上方看的椭圆，围着腰），身体外圈一层淡紫色的光膜轮廓，几颗小星星绕着转。**身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold filigree ramp (#FFFFFF, #FFF4C4, #FFD95A, #F2B12E, #C77A16, #7E4410), a violet portal ramp (#F4E6FF, #C9A2FF, #9A62F0, #6A34D0, #3E1C8C, #22104E), a pink star ramp (#FFE8F4, #FF9CCB, #F05A9E, #B02A6E).
Effect: A PORTAL RING SHIELD, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit hit stands in the middle, not drawn: 16 squares wide and 36 tall: a thin gold filigree ring 24 squares wide and 7 tall around the unit's waist (seen slightly from above, its back half behind the unit's place), a faint violet outline like a bubble around the whole unit 22 wide and 40 tall, three tiny pink-gold stars circling; frames 1-6 the ring's curls glinting in turn and the stars moving round. The middle (the body) left empty. everything is a YORDLE PORTAL MAGE'S whimsical magic: GOLD FILIGREE portal rings with curling vines, a VIOLET SWIRL inside each portal, little pink-gold STARS and sparkles, and for the paint cream PAPER with bright ink swirls; flat shades, crisp shapes; no smooth neon beams, no realistic fire or smoke.
Layout: one horizontal row of 6 equal 26:42 cells, image size 2496x672 (each cell 416x672, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `norra_fx_r_warn.png`：门槛之书：地上的预警圈，6 帧

大招要落下的地方：地上一圈圈**同心的金色门环**慢慢亮起来、往里转（视频里手游大招的金色同心圈；参考 basicattack_portal、ring_00_erosion）。最大 **横 54 格、纵 18 格**。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold filigree ramp (#FFFFFF, #FFF4C4, #FFD95A, #F2B12E, #C77A16, #7E4410), a violet portal ramp (#F4E6FF, #C9A2FF, #9A62F0, #6A34D0, #3E1C8C, #22104E).
Effect: A WARNING OF CONCENTRIC PORTAL RINGS, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall): 1 a thin gold ring 20 squares wide; 2 a second, wider gold filigree ring 36 wide around it; 3 three concentric gold rings, the widest 54 wide and 18 tall, with little curls on them and a faint violet glow between them; 4-6 the rings brightening in turn from the outside in, small gold sparks rising. Flat colours, crisp pixel shapes. everything is a YORDLE PORTAL MAGE'S whimsical magic: GOLD FILIGREE portal rings with curling vines, a VIOLET SWIRL inside each portal, little pink-gold STARS and sparkles, and for the paint cream PAPER with bright ink swirls; flat shades, crisp shapes; no smooth neon beams, no realistic fire or smoke.
Layout: one horizontal row of 6 equal 60:22 cells, image size 5760x352 (each cell 960x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `norra_fx_r_book.png`：门槛之书：天上的大门和落下的书页，10 帧

大招：目标头顶高处打开**两三圈同心的巨大金色次元门**（正面略微从下往上看的椭圆，金色花纹、中间紫色漩涡，像视频里手游大招的金色圆环），**一张巨大的发光书页**（米色纸、金边，上面有卷卷的花纹）从门里**直直落下来**，一道金光柱跟着砸到地上，地面炸开一圈纸屑和金色冲击波（范围里的敌人被「纸化」眩晕）。砸的地方在格子底部往上 8 格。**左右对称**，10 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold filigree ramp (#FFFFFF, #FFF4C4, #FFD95A, #F2B12E, #C77A16, #7E4410), a violet portal ramp (#F4E6FF, #C9A2FF, #9A62F0, #6A34D0, #3E1C8C, #22104E), a cream paper ramp (#FFFDF4, #F2E6CC, #D8C6A0, #A8906A), a pink star ramp (#FFE8F4, #FF9CCB, #F05A9E, #B02A6E).
Effect: THE BOOK OF THRESHOLDS, 10 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a gold filigree ring 24 squares wide and 8 tall opening high in the cell (its middle 14 squares below the top); 2 two more concentric gold rings around it, the widest 60 wide and 20 tall, a violet swirl in the middle; 3 the rings glowing, a giant glowing PAGE (cream paper 20 wide and 26 tall with a gold border and gold curls on it, seen from the front, upright) coming out of the middle; 4-5 the page falling straight down inside a wide pillar of gold light 22 wide; 6 the page slamming onto the ground line 8 squares above the bottom, a white-gold flash 40 wide; 7 a gold shockwave ellipse 64 wide and 16 tall on the ground, paper scraps flying up at both sides; 8 scraps falling, the rings above fading; 9 the light pillar thinning; 10 the last scraps and sparkles. Frames 6-8 MUST fill 60 squares across. everything is a YORDLE PORTAL MAGE'S whimsical magic: GOLD FILIGREE portal rings with curling vines, a VIOLET SWIRL inside each portal, little pink-gold STARS and sparkles, and for the paint cream PAPER with bright ink swirls; flat shades, crisp shapes; no smooth neon beams, no realistic fire or smoke.
Layout: one horizontal row of 10 equal 70:84 cells, image size 11200x1344 (each cell 1120x1344, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `norra_fx_r_hit.png`：门槛之书：被砸中，4 帧

被书页砸中：一下金白的闪光，几片米色纸屑和金色小星星往外飞。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold filigree ramp (#FFFFFF, #FFF4C4, #FFD95A, #F2B12E, #C77A16, #7E4410), a cream paper ramp (#FFFDF4, #F2E6CC, #D8C6A0, #A8906A), a pink star ramp (#FFE8F4, #FF9CCB, #F05A9E, #B02A6E).
Effect: A PAGE HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash 8 squares across; 2 cream paper scraps and gold stars 14 across flying out at mirrored places; 3 the scraps further out, turning; 4 fading scraps. everything is a YORDLE PORTAL MAGE'S whimsical magic: GOLD FILIGREE portal rings with curling vines, a VIOLET SWIRL inside each portal, little pink-gold STARS and sparkles, and for the paint cream PAPER with bright ink swirls; flat shades, crisp shapes; no smooth neon beams, no realistic fire or smoke.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `norra_fx_r_paper.png`：门槛之书：被「纸化」，6 帧循环

被纸化的人（眩晕、受到的伤害变多）：身体外圈一圈**米色纸片的轮廓**，像被剪成纸人贴在一张纸上，纸边有折痕，四周几片小纸屑慢慢飘，头顶一个小小的纸折星星。**身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cream paper ramp (#FFFDF4, #F2E6CC, #D8C6A0, #A8906A), bright ink colours (#F05A9E, #44C8D2, #9A62F0, #FFD95A).
Effect: A PAPER-CUT LOOK, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit hit stands in the middle, not drawn: 16 squares wide and 36 tall: a cream paper frame around the unit 22 wide and 40 tall like the edge of a paper cut-out (a thick wavy paper border with a few fold lines, the inside left empty), four small paper scraps drifting at mirrored places and a little folded paper star with a magenta ink dot over its head; frames 1-6 the scraps drifting and turning, the star bobbing. The middle (the body) left empty. everything is a YORDLE PORTAL MAGE'S whimsical magic: GOLD FILIGREE portal rings with curling vines, a VIOLET SWIRL inside each portal, little pink-gold STARS and sparkles, and for the paint cream PAPER with bright ink swirls; flat shades, crisp shapes; no smooth neon beams, no realistic fire or smoke.
Layout: one horizontal row of 6 equal 24:42 cells, image size 2304x672 (each cell 384x672, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `norra_fx_a_bolt` | view_projectiles `tft_norra_a_bolt`（弹道，z 2；朝右、上下对称） | 12 × 8 |
| `norra_fx_a_hit` | view_effects `tft_norra_a_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `norra_fx_p_heal` | view_effects `tft_norra_p_heal`（跟随被治疗的人，z 2；左右对称） | 12 × 16 |
| `norra_fx_q_ball` | view_projectiles `tft_norra_q_ball`（抛物线弹道，z 2；朝右、上下对称） | 16 × 16 |
| `norra_fx_q_blast` | view_effects `tft_norra_q_blast`（大表，落点，z 2，不跟随；左右对称） | 48 × 40 |
| `norra_fx_q_hit` | view_effects `tft_norra_q_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `norra_fx_q_paint` | view_projectiles `tft_norra_q_paint` / `tft_norra_q2_paint`（大表，地面区域，z -2；左右、上下都对称） | 64 × 22 |
| `norra_fx_e_anvil_hit` | view_effects `tft_norra_e_anvil_hit`（大表，目标脚下，z 2，不跟随；左右对称） | 36 × 64 |
| `norra_fx_e_book_hit` | view_effects `tft_norra_e_book_hit`（大表，目标脚下，z 2，不跟随；左右对称） | 40 × 64 |
| `norra_fx_e_potion` | view_effects `tft_norra_e_potion`（跟随每个被治疗的队友，z 2；左右对称） | 14 × 26 |
| `norra_fx_e_guard` | view_buffs `tft_norra_e_guard`（跟随有护盾的人，z 3；左右对称） | 26 × 42 |
| `norra_fx_r_warn` | view_effects `tft_norra_r_warn`（大表，落点，地面，z -2，不跟随；左右对称） | 60 × 22 |
| `norra_fx_r_book` | view_effects `tft_norra_r_book`（大表，落点，z 3，不跟随；左右对称） | 70 × 84 |
| `norra_fx_r_hit` | view_effects `tft_norra_r_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `norra_fx_r_paper` | view_buffs `tft_norra_r_paper`（跟随目标，z 3；左右对称） | 24 × 42 |

- 两张表：`asset/tft/effects/tft_norra_fx`（小的）和 `tft_norra_big`（q_blast、q_paint、e_anvil_hit、e_book_hit、r_warn、r_book），tag = 名字（build_norra.py 的 views：q2_paint → q_paint、q2_blast → q_blast）；悠米 `tft_norra_yuumi` 是 hd/yuumi.png 做的单独一张表。
- 弹道（a_bolt、q_ball）断言上下对称；q_paint 断言两个方向都对称；其余断言左右对称。
- r_warn 在 R 的门飞行的 r_open 帧里一直显示（拉长到那么长）。
- 用 `pixel_1x/` 切格（import_locke_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
