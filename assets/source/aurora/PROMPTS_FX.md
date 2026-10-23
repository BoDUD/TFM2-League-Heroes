# 双界灵兔 阿萝拉：给 Codex 的特效提示词（第 3 步）

> **这一份是 20 张特效图。** 造型已定（`design/aurora_design.png`：Q 版兔子女巫，铜红卷发、圆金框眼镜、紫蓝眼睛、青绿宽檐女巫帽和两只长兔耳朵、米白长外套和浅蓝毛边披肩、橙色兔尾巴，肩上扛着一根细长的魔杖）。她在游戏里是**高清**的（每个游戏格子里 2.25×2.25 个细像素），46 格高、24 格宽（高×宽，连耳朵）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/aurora_size.png`：阿萝拉放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里阿萝拉自己的特效贴图（大多是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用。**阿萝拉是穿行于两个世界的兔子女巫，所有特效都是灵界的魔法**：冰蓝和紫色的光、粉紫色的点缀、白色的星点和霜花，还有**发光的小灵兔**（圆滚滚的蓝色身体、两只紫粉色长耳朵、两个白点眼睛）；不要火，也不要光滑的霓虹光束。
> - **特效要亮**：每道光、每只小灵兔都有最亮一档或白色的高光，暗底上一眼能看见。
> - **光、雾、冲击波、光环都没有黑描边**（小灵兔也不要描黑边，用它自己最深的一档）。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。
> - **对称**：打中、脚下、身上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（`a_bolt`、`q_out`、`q_back`、`e_wave`）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `aurora_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/aurora_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/aurora_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 魔杖点出一团灵光 | `a_bolt` · `a_hit` |
| 被动「驱灵奇术」 | 打中英雄叠驱灵层，第三下抽出灵物：额外伤害，灵物飞回她身上回血加速 | `p_mark` · `p_spirit` · `p_heal` |
| 被动里的「灵纱洞开」（W） | 残血又被贴身时往后一跳进入灵界：隐身、加速 | `w_veil` · `w_haste` |
| 技能 1 =「飞去来咒」 | 咒弹穿过敌人飞出去、留下诅咒，停一下再把诅咒抽回来，回程再打一次 | `q_out` · `q_hit` · `q_curse` · `q_back` · `q_back_hit` |
| 技能 2 =「怪奇喷涌」 | 身前打开界域之窗，往前喷出一道灵魂冲击：伤害、减速，然后她往后一跳 | `e_burst` · `e_wave` · `e_hit` · `slow` |
| 大招 =「双界合一」 | 跳到敌人身上落地放冲击波，地上张开两界交汇的领域减速；目标跑开时她穿过领域传送过去 | `r_shock` · `r_hit` · `r_zone` · `r_blink` · `slow` |

连招：**怪奇喷涌 → 飞去来咒**（冲击打中英雄马上补咒弹），**双界合一 → 怪奇喷涌**（落地马上喷），**飞去来咒去回两次都叠驱灵层**，**领域里传送追击**。

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、雾、冲击波没有黑描边，也不要用最深的颜色给形状描一圈边**。
- **都是灵界的魔法**：冰蓝、紫色、粉紫、白色星点和霜花、小灵兔；每个形状 2–3 档平涂。
- **要亮**：每个形状都有最亮一档或白色的高光。
- 颜色（按每条写的用）：
  - 灵界·冰蓝：`#FFFFFF`、`#D8F0FF`、`#8CC8FF`、`#4A86F0`、`#2A48C0`、`#18206A`；
  - 魔法·紫：`#FFFFFF`、`#F0DCFF`、`#C49CFF`、`#8A5CE8`、`#5430A8`、`#2A1660`；
  - 诅咒·粉紫：`#FFFFFF`、`#FFD8F4`、`#FF94DC`、`#E04CB4`、`#8A1E70`；
  - 星点霜花·白：`#FFFFFF`、`#E8FAFF`、`#B4E8F8`、`#70B8DC`；
  - 魔杖·金光：`#FFFFFF`、`#FFF4B0`、`#FFD850`、`#E8A820`、`#9A6814`；
  - 回血·薄荷绿：`#F4FFF0`、`#C8FFD8`、`#7CEAB0`、`#34B880`、`#146A48`；
- 打中、爆发居中画，不旋转；地面上的圈（冲击波、领域、脚下的光和雾）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（20 张）

20 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `aurora_fx_a_bolt.png`：普攻：魔杖射出的灵光，4 帧循环

魔杖点出去的一小团蓝紫色灵光：一个亮白核心的小光球，后面拖一条短短的蓝色光尾和几颗小星点。**朝右飞、上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an icy spirit-blue ramp (#FFFFFF, #D8F0FF, #8CC8FF, #4A86F0, #2A48C0, #18206A), a violet magic ramp (#FFFFFF, #F0DCFF, #C49CFF, #8A5CE8, #5430A8, #2A1660), a white frost and sparkle ramp (#FFFFFF, #E8FAFF, #B4E8F8, #70B8DC).
Effect: A SMALL SPIRIT BOLT, 4 looping frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a white-cored round blue-violet light ball 4 squares across at the right, a short tapering icy blue trail 8 squares long behind it with two or three tiny white sparkles that move back frame to frame. everything is SPIRIT-REALM magic of a bunny witch: icy blue and violet light, magenta-pink accents, white sparkles and frost, little glowing bunny spirits (round blobs with two long ears); flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 4 equal 14:8 cells, image size 896x128 (each cell 224x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `aurora_fx_a_hit.png`：普攻：灵光打中，3 帧

灵光打中敌人：一个蓝白色的闪光，四周弹出几颗紫色和白色的星点。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an icy spirit-blue ramp (#FFFFFF, #D8F0FF, #8CC8FF, #4A86F0, #2A48C0, #18206A), a violet magic ramp (#FFFFFF, #F0DCFF, #C49CFF, #8A5CE8, #5430A8, #2A1660), a white frost and sparkle ramp (#FFFFFF, #E8FAFF, #B4E8F8, #70B8DC).
Effect: A SPIRIT BOLT LANDING, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-blue flash 5 squares across; 2 a ring of short violet and white star sparkles bursting out 11 across at mirrored places; 3 the sparkles further out, fading to their darkest shades. everything is SPIRIT-REALM magic of a bunny witch: icy blue and violet light, magenta-pink accents, white sparkles and frost, little glowing bunny spirits (round blobs with two long ears); flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `aurora_fx_q_out.png`：飞去来咒：飞出去的咒弹，4 帧循环

飞出去的诅咒弹（参考 q_mis、missilehead）：一个**紫色的菱形咒印**，中间一格白亮，前面尖、两边有两道弯弯的小钩，后面拖一条蓝紫色的光带和星点。**朝右飞、上下对称**，4 帧循环（咒印微微闪、光带抖动）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet magic ramp (#FFFFFF, #F0DCFF, #C49CFF, #8A5CE8, #5430A8, #2A1660), an icy spirit-blue ramp (#FFFFFF, #D8F0FF, #8CC8FF, #4A86F0, #2A48C0, #18206A), a magenta-pink ramp (#FFFFFF, #FFD8F4, #FF94DC, #E04CB4, #8A1E70).
Effect: A HEX MISSILE, 4 looping frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): at the right a violet DIAMOND-SHAPED SIGIL 8 squares long with a white core square and two small curved hooks sweeping back above and below it (mirrored), a rippling blue-violet ribbon trail 12 squares long behind it with pink and white specks; the sigil flickers and the ribbon waves frame to frame. everything is SPIRIT-REALM magic of a bunny witch: icy blue and violet light, magenta-pink accents, white sparkles and frost, little glowing bunny spirits (round blobs with two long ears); flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 4 equal 22:12 cells, image size 1408x192 (each cell 352x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `aurora_fx_q_back.png`：飞去来咒：收回来的咒弹，4 帧循环

收回来的诅咒：和 q_out 同一个咒印，但**带着一团粉紫色的诅咒雾**往回飞，光带更粗、带几只小灵兔的影子。**朝右画（游戏按方向转）、上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta-pink ramp (#FFFFFF, #FFD8F4, #FF94DC, #E04CB4, #8A1E70), a violet magic ramp (#FFFFFF, #F0DCFF, #C49CFF, #8A5CE8, #5430A8, #2A1660), an icy spirit-blue ramp (#FFFFFF, #D8F0FF, #8CC8FF, #4A86F0, #2A48C0, #18206A).
Effect: A HEX RETURNING, 4 looping frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): the same violet diamond sigil at the right, wrapped in a swirl of magenta-pink curse mist 10 squares across, a thicker violet-and-pink ribbon trail 14 squares long behind it with two tiny bunny-spirit silhouettes (round blobs with two long ears) in it at mirrored places. everything is SPIRIT-REALM magic of a bunny witch: icy blue and violet light, magenta-pink accents, white sparkles and frost, little glowing bunny spirits (round blobs with two long ears); flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 4 equal 24:12 cells, image size 1536x192 (each cell 384x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `aurora_fx_q_hit.png`：飞去来咒：咒弹打中，4 帧

咒弹打中：一个紫色菱形咒印在敌人身上一闪张开，变成一圈紫色和蓝色的碎光往外散。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet magic ramp (#FFFFFF, #F0DCFF, #C49CFF, #8A5CE8, #5430A8, #2A1660), an icy spirit-blue ramp (#FFFFFF, #D8F0FF, #8CC8FF, #4A86F0, #2A48C0, #18206A), a white frost and sparkle ramp (#FFFFFF, #E8FAFF, #B4E8F8, #70B8DC).
Effect: A HEX STRIKING, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-cored violet diamond sigil 6 squares tall flashing; 2 the sigil opening into four violet points with blue light between; 3 a ring of violet and blue shards 15 across; 4 the shards scattered, dimming. everything is SPIRIT-REALM magic of a bunny witch: icy blue and violet light, magenta-pink accents, white sparkles and frost, little glowing bunny spirits (round blobs with two long ears); flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `aurora_fx_q_back_hit.png`：飞去来咒：诅咒被抽回时的爆开，4 帧

诅咒被抽回时打中：敌人身上一团**粉紫色的诅咒雾**猛地被扯碎，里面一只小灵兔的影子飞出来，白色星点四散。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta-pink ramp (#FFFFFF, #FFD8F4, #FF94DC, #E04CB4, #8A1E70), a violet magic ramp (#FFFFFF, #F0DCFF, #C49CFF, #8A5CE8, #5430A8, #2A1660), a white frost and sparkle ramp (#FFFFFF, #E8FAFF, #B4E8F8, #70B8DC).
Effect: A CURSE TORN OUT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a magenta-pink curse mist 10 squares across around the target's chest with a white flash; 2 the mist bursting outward, a small glowing bunny spirit (a round blob with two long ears, pale blue and violet) rising out of it in the middle; 3 the spirit higher, the mist in rags, white sparkles flying at mirrored places; 4 the rags fading. everything is SPIRIT-REALM magic of a bunny witch: icy blue and violet light, magenta-pink accents, white sparkles and frost, little glowing bunny spirits (round blobs with two long ears); flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 4 equal 18:22 cells, image size 1152x352 (each cell 288x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `aurora_fx_q_curse.png`：飞去来咒：敌人身上的诅咒印，4 帧循环

中了诅咒的敌人胸口：一个慢慢转的**粉紫色菱形咒印**（参考 qvulnerable），四个角上翘的小钩，一闪一闪。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta-pink ramp (#FFFFFF, #FFD8F4, #FF94DC, #E04CB4, #8A1E70), a violet magic ramp (#FFFFFF, #F0DCFF, #C49CFF, #8A5CE8, #5430A8, #2A1660).
Effect: A CURSE MARK, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a magenta-pink and violet DIAMOND SIGIL 9 squares tall with four small hooked corners curling outward, a white core square pulsing bright and dim across the frames, two tiny sparkles orbiting at mirrored places. everything is SPIRIT-REALM magic of a bunny witch: icy blue and violet light, magenta-pink accents, white sparkles and frost, little glowing bunny spirits (round blobs with two long ears); flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `aurora_fx_p_mark.png`：驱灵奇术：敌人头上的驱灵层数，4 帧循环

被打中的敌人头顶：一个小小的**蓝色灵光圈**（参考 passivering），圈上三颗小星点慢慢绕着转。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an icy spirit-blue ramp (#FFFFFF, #D8F0FF, #8CC8FF, #4A86F0, #2A48C0, #18206A), a white frost and sparkle ramp (#FFFFFF, #E8FAFF, #B4E8F8, #70B8DC).
Effect: A SPIRIT MARK OVER THE HEAD, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat icy blue ring 10 squares wide and 4 tall seen from above, three tiny white star sparkles riding around it (their places mirrored in every frame), the ring brightening and dimming. everything is SPIRIT-REALM magic of a bunny witch: icy blue and violet light, magenta-pink accents, white sparkles and frost, little glowing bunny spirits (round blobs with two long ears); flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 4 equal 12:8 cells, image size 768x128 (each cell 192x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `aurora_fx_p_spirit.png`：驱灵奇术：灵物被抽出来，6 帧

第三下打中时：敌人身上冒出一只**发光的小灵兔**（参考 basespirit：蓝色身体、紫粉色的长耳朵，圆滚滚的），往上飘起来、转一圈，化成一串白色的星点。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an icy spirit-blue ramp (#FFFFFF, #D8F0FF, #8CC8FF, #4A86F0, #2A48C0, #18206A), a violet magic ramp (#FFFFFF, #F0DCFF, #C49CFF, #8A5CE8, #5430A8, #2A1660), a magenta-pink ramp (#FFFFFF, #FFD8F4, #FF94DC, #E04CB4, #8A1E70), a white frost and sparkle ramp (#FFFFFF, #E8FAFF, #B4E8F8, #70B8DC).
Effect: A SPIRIT EXORCISED, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-blue flash on the target's chest; 2 a small glowing BUNNY SPIRIT (a round icy blue body 6 squares across, two long violet-pink ears, two white dot eyes) popping out; 3 the spirit rising above the target's head; 4 the spirit at the top of the cell, a ring of sparkles round it; 5 the spirit bursting into white star sparkles; 6 the sparkles fading. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall. everything is SPIRIT-REALM magic of a bunny witch: icy blue and violet light, magenta-pink accents, white sparkles and frost, little glowing bunny spirits (round blobs with two long ears); flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 6 equal 20:30 cells, image size 1920x480 (each cell 320x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `aurora_fx_p_heal.png`：驱灵奇术：灵物回到她身边回血，6 帧

灵物飞回她身上：两只小灵兔绕着她转一圈，留下薄荷绿和蓝色的光点往上升，脚下一个淡淡的光圈。**只画外圈，身体位置留空**，**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a soft mint healing ramp (#F4FFF0, #C8FFD8, #7CEAB0, #34B880, #146A48), an icy spirit-blue ramp (#FFFFFF, #D8F0FF, #8CC8FF, #4A86F0, #2A48C0, #18206A), a white frost and sparkle ramp (#FFFFFF, #E8FAFF, #B4E8F8, #70B8DC).
Effect: A HEALING SPIRIT, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): two small glowing bunny spirits (icy blue bodies, long violet ears) circling her at mirrored places - from her feet in frame 1 up past her waist to her head in frame 4, dissolving in 5-6 - leaving soft mint and blue plus-shaped sparkles that rise and fade; a faint mint ring on the ground under her in frames 1-3. she stands in the middle, not drawn: 24 squares wide and 46 tall (with the ears). everything is SPIRIT-REALM magic of a bunny witch: icy blue and violet light, magenta-pink accents, white sparkles and frost, little glowing bunny spirits (round blobs with two long ears); flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 6 equal 28:48 cells, image size 2688x768 (each cell 448x768, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `aurora_fx_w_veil.png`：灵纱洞开：后跳隐身的一阵灵雾，5 帧

她往后跳进灵界的一瞬间：原地一团**蓝紫色的灵雾**炸开，里面一圈垂下来的光帘（参考 w_rays），几片白色的霜花飘散。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet magic ramp (#FFFFFF, #F0DCFF, #C49CFF, #8A5CE8, #5430A8, #2A1660), an icy spirit-blue ramp (#FFFFFF, #D8F0FF, #8CC8FF, #4A86F0, #2A48C0, #18206A), a white frost and sparkle ramp (#FFFFFF, #E8FAFF, #B4E8F8, #70B8DC).
Effect: A VEIL OPENING, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-blue flash at her waist height; 2 a puff of violet and blue spirit mist 20 squares across with a curtain of thin vertical light rays falling through it; 3 the mist widest, 28 across, the rays brightest; 4 the mist thinning into wisps, white frost flakes drifting out at mirrored places; 5 a few wisps and flakes fading. she stands in the middle, not drawn: 24 squares wide and 46 tall (with the ears). everything is SPIRIT-REALM magic of a bunny witch: icy blue and violet light, magenta-pink accents, white sparkles and frost, little glowing bunny spirits (round blobs with two long ears); flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 5 equal 30:40 cells, image size 2400x640 (each cell 480x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `aurora_fx_w_haste.png`：灵纱洞开：加速时脚下的灵光，4 帧循环

隐身加速时她脚下：一圈淡蓝色的光，两边各有几道往后飘的小光条和霜点。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an icy spirit-blue ramp (#FFFFFF, #D8F0FF, #8CC8FF, #4A86F0, #2A48C0, #18206A), a white frost and sparkle ramp (#FFFFFF, #E8FAFF, #B4E8F8, #70B8DC).
Effect: A HASTE GLOW, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), a faint icy blue ellipse 16 squares wide, short streaks of light and frost specks lifting off both of its ends (mirrored), flickering frame to frame. everything is SPIRIT-REALM magic of a bunny witch: icy blue and violet light, magenta-pink accents, white sparkles and frost, little glowing bunny spirits (round blobs with two long ears); flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 4 equal 20:8 cells, image size 1280x128 (each cell 320x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `aurora_fx_e_wave.png`：怪奇喷涌：往前冲出去的灵魂冲击，4 帧循环

往前冲出去的一道**蓝紫色灵魂冲击**（参考 windblast、blastring）：前面一道弯弯的弧形光墙（凸向右），里面翻滚着灵雾和几只小灵兔的影子，后面拖着碎光。**朝右飞、上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet magic ramp (#FFFFFF, #F0DCFF, #C49CFF, #8A5CE8, #5430A8, #2A1660), an icy spirit-blue ramp (#FFFFFF, #D8F0FF, #8CC8FF, #4A86F0, #2A48C0, #18206A), a white frost and sparkle ramp (#FFFFFF, #E8FAFF, #B4E8F8, #70B8DC).
Effect: A SPIRIT BLAST WAVE, 4 looping frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): at the right a curved crescent wall of icy blue and violet light 20 squares tall bulging to the right, 4 squares thick with a white leading edge; behind it churning violet spirit mist with two tiny bunny-spirit silhouettes at mirrored places and broken light trailing to the left; the wall ripples frame to frame. everything is SPIRIT-REALM magic of a bunny witch: icy blue and violet light, magenta-pink accents, white sparkles and frost, little glowing bunny spirits (round blobs with two long ears); flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 4 equal 30:22 cells, image size 1920x352 (each cell 480x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `aurora_fx_e_burst.png`：怪奇喷涌：她身前张开的界域之窗，5 帧

她推出冲击的一瞬间：身前张开一个**圆形的界域之窗**（参考 r_ring：一圈带花纹钩的紫蓝色光环），从小到大张开再碎掉。**左右对称**（游戏不会翻转这张图，所以画成正对着看的圆窗），5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet magic ramp (#FFFFFF, #F0DCFF, #C49CFF, #8A5CE8, #5430A8, #2A1660), an icy spirit-blue ramp (#FFFFFF, #D8F0FF, #8CC8FF, #4A86F0, #2A48C0, #18206A), a white frost and sparkle ramp (#FFFFFF, #E8FAFF, #B4E8F8, #70B8DC).
Effect: A REALM WINDOW OPENING, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a round ornate RING of violet and icy blue light seen face-on, with small curling hooks at four mirrored places on its rim, centred on her chest: 1 a 6-square ring with a white flash; 2 the ring 16 across, its hooks unfurling; 3 the ring 26 across at its brightest, a violet glow inside; 4 the ring cracking into arcs; 5 the arcs scattering as sparkles. she stands in the middle, not drawn: 24 squares wide and 46 tall (with the ears). everything is SPIRIT-REALM magic of a bunny witch: icy blue and violet light, magenta-pink accents, white sparkles and frost, little glowing bunny spirits (round blobs with two long ears); flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 5 equal square cells, image size 2400x480 (each cell 480x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `aurora_fx_e_hit.png`：怪奇喷涌：打中，4 帧

冲击打中敌人：一阵蓝紫色的灵雾裹住他，几颗白色霜花溅开。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet magic ramp (#FFFFFF, #F0DCFF, #C49CFF, #8A5CE8, #5430A8, #2A1660), an icy spirit-blue ramp (#FFFFFF, #D8F0FF, #8CC8FF, #4A86F0, #2A48C0, #18206A), a white frost and sparkle ramp (#FFFFFF, #E8FAFF, #B4E8F8, #70B8DC).
Effect: A BLAST STRIKING, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash at the target's chest; 2 a gust of violet and blue spirit mist wrapping round it 14 across; 3 frost flakes splashing out at mirrored places; 4 the mist thinning away. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall. everything is SPIRIT-REALM magic of a bunny witch: icy blue and violet light, magenta-pink accents, white sparkles and frost, little glowing bunny spirits (round blobs with two long ears); flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 4 equal 16:20 cells, image size 1024x320 (each cell 256x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `aurora_fx_slow.png`：减速：脚下的霜雾，4 帧循环（E 和 R 的减速共用）

被减速的人脚下：一圈缠着脚的**淡紫色霜雾**，几粒冰晶。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet magic ramp (#FFFFFF, #F0DCFF, #C49CFF, #8A5CE8, #5430A8, #2A1660), a white frost and sparkle ramp (#FFFFFF, #E8FAFF, #B4E8F8, #70B8DC).
Effect: A SLOWING FROST MIST, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), a pale violet mist 14 squares wide coiling round the feet with a few white ice crystals glinting at mirrored places, drifting frame to frame. everything is SPIRIT-REALM magic of a bunny witch: icy blue and violet light, magenta-pink accents, white sparkles and frost, little glowing bunny spirits (round blobs with two long ears); flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 4 equal 16:8 cells, image size 1024x128 (each cell 256x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `aurora_fx_r_shock.png`：双界合一：落地的冲击波，6 帧

她落地放出的冲击波（参考 leadingedge_ring、icecrack）：脚下一圈**蓝紫色的光环**飞快往外扩，地上裂开发光的冰裂纹，白色霜花往外溅。**地上的椭圆、左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an icy spirit-blue ramp (#FFFFFF, #D8F0FF, #8CC8FF, #4A86F0, #2A48C0, #18206A), a violet magic ramp (#FFFFFF, #F0DCFF, #C49CFF, #8A5CE8, #5430A8, #2A1660), a white frost and sparkle ramp (#FFFFFF, #E8FAFF, #B4E8F8, #70B8DC).
Effect: A LANDING SHOCKWAVE, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall): 1 a white-blue flash 10 across at the centre; 2 a bright icy blue ring 24 wide racing out, glowing ice cracks spreading from the centre; 3 the ring 40 wide, violet behind its white edge; 4 the ring 54 wide, frost flakes thrown up along it; 5 the ring at the cell's edge, thin, the cracks dimming; 6 fading cracks and flakes only. everything is SPIRIT-REALM magic of a bunny witch: icy blue and violet light, magenta-pink accents, white sparkles and frost, little glowing bunny spirits (round blobs with two long ears); flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 6 equal 60:26 cells, image size 5760x416 (each cell 960x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `aurora_fx_r_zone.png`：双界合一：两界交汇的领域，8 帧循环

地上张开的领域（参考 spiritwall、r_ring、ultcenter）：一个很大的**蓝紫色椭圆界域**，边缘是一圈垂直往上冒的**灵墙光帘**（像一圈矮矮的发光栅栏），里面地上淡淡的紫色雾和花纹，几只小灵兔在边缘慢慢绕。**地上的椭圆、左右对称**，8 帧循环（前 2 帧张开，后面循环）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet magic ramp (#FFFFFF, #F0DCFF, #C49CFF, #8A5CE8, #5430A8, #2A1660), an icy spirit-blue ramp (#FFFFFF, #D8F0FF, #8CC8FF, #4A86F0, #2A48C0, #18206A), a magenta-pink ramp (#FFFFFF, #FFD8F4, #FF94DC, #E04CB4, #8A1E70), a white frost and sparkle ramp (#FFFFFF, #E8FAFF, #B4E8F8, #70B8DC).
Effect: THE REALM BETWEEN WORLDS, 8 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), a big violet and icy blue ellipse 76 squares wide: its rim a ring of short vertical SPIRIT-WALL light curtains rising 6-8 squares (like a low glowing fence), inside it a faint violet mist with a thin ornate circle pattern on the ground, three small bunny spirits drifting slowly round the rim at mirrored places; frames 1-2 the realm opening from the centre, 3-8 the curtains rippling and the spirits moving on. everything is SPIRIT-REALM magic of a bunny witch: icy blue and violet light, magenta-pink accents, white sparkles and frost, little glowing bunny spirits (round blobs with two long ears); flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 8 equal 80:34 cells, image size 10240x544 (each cell 1280x544, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `aurora_fx_r_hit.png`：双界合一：冲击波打中，4 帧

冲击波打中敌人：一道蓝白色的竖向光一闪，周围冰晶炸开。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an icy spirit-blue ramp (#FFFFFF, #D8F0FF, #8CC8FF, #4A86F0, #2A48C0, #18206A), a white frost and sparkle ramp (#FFFFFF, #E8FAFF, #B4E8F8, #70B8DC), a violet magic ramp (#FFFFFF, #F0DCFF, #C49CFF, #8A5CE8, #5430A8, #2A1660).
Effect: A SHOCKWAVE STRIKING, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a tall white-blue flash 4 squares wide through the target; 2 ice crystals and violet sparks bursting out 15 across; 3 the crystals further out; 4 fading. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall. everything is SPIRIT-REALM magic of a bunny witch: icy blue and violet light, magenta-pink accents, white sparkles and frost, little glowing bunny spirits (round blobs with two long ears); flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 4 equal 16:20 cells, image size 1024x320 (each cell 256x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `aurora_fx_r_blink.png`：双界合一：领域里的传送，5 帧

她穿过领域传送过去的一闪：一个竖立的**椭圆形的门**（蓝紫色光边，中间白亮）一下张开又合上，周围飘出几颗星点和一只小灵兔。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet magic ramp (#FFFFFF, #F0DCFF, #C49CFF, #8A5CE8, #5430A8, #2A1660), an icy spirit-blue ramp (#FFFFFF, #D8F0FF, #8CC8FF, #4A86F0, #2A48C0, #18206A), a white frost and sparkle ramp (#FFFFFF, #E8FAFF, #B4E8F8, #70B8DC).
Effect: A STEP BETWEEN WORLDS, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a tall upright oval PORTAL with a violet and icy blue rim and a white core: 1 a thin vertical white line 30 squares tall; 2 the portal opening 12 wide; 3 the portal widest, 18 wide, a small bunny spirit and sparkles spilling out at its sides (mirrored); 4 the portal closing to a line; 5 sparkles only. she stands in the middle, not drawn: 24 squares wide and 46 tall (with the ears). everything is SPIRIT-REALM magic of a bunny witch: icy blue and violet light, magenta-pink accents, white sparkles and frost, little glowing bunny spirits (round blobs with two long ears); flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 5 equal 24:44 cells, image size 1920x704 (each cell 384x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `aurora_fx_a_bolt` | view_projectiles `league_aurora_a_bolt`（弹道，z 2；上下对称） | 14 × 8 |
| `aurora_fx_a_hit` | view_effects `league_aurora_a_hit`（跟随目标，z 2；左右对称） | 12 × 12 |
| `aurora_fx_q_out` | view_projectiles `league_aurora_q_out`（弹道，z 2；上下对称；E→Q 连招的追踪咒弹也用它） | 22 × 12 |
| `aurora_fx_q_back` | view_projectiles `league_aurora_q_back`（弹道，z 2；上下对称） | 24 × 12 |
| `aurora_fx_q_hit` | view_effects `league_aurora_q_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `aurora_fx_q_back_hit` | view_effects `league_aurora_q_back_hit`（跟随目标，z 2；左右对称） | 18 × 22 |
| `aurora_fx_q_curse` | view_buffs `league_aurora_q_curse`（跟随，胸口，z 3；左右对称） | 12 × 12 |
| `aurora_fx_p_mark` | view_buffs `league_aurora_p_mark`（跟随，头顶，z 3；左右对称） | 12 × 8 |
| `aurora_fx_p_spirit` | view_effects `league_aurora_p_spirit`（跟随目标，z 3；左右对称） | 20 × 30 |
| `aurora_fx_p_heal` | view_effects `league_aurora_p_heal`（跟随她，z 3；左右对称） | 28 × 48 |
| `aurora_fx_w_veil` | view_effects `league_aurora_w_veil`（在她起跳的地方，不跟随，z 3；左右对称） | 30 × 40 |
| `aurora_fx_w_haste` | view_buffs `league_aurora_w_haste`（跟随她，脚下，z -1；左右对称） | 20 × 8 |
| `aurora_fx_e_wave` | view_projectiles `league_aurora_e_wave`（弹道，z 2；上下对称） | 30 × 22 |
| `aurora_fx_e_burst` | view_effects `league_aurora_e_burst`（在她身上，不跟随，z 3；左右对称） | 30 × 30 |
| `aurora_fx_e_hit` | view_effects `league_aurora_e_hit`（跟随目标，z 2；左右对称） | 16 × 20 |
| `aurora_fx_slow` | view_buffs `league_aurora_e_slow` / `r_slow` / `r_slow1`（tag `slow`，跟随，脚下，z -1；左右对称） | 16 × 8 |
| `aurora_fx_r_shock` | view_effects `league_aurora_r_shock`（大表，在她落地的地方，地上，z -1；左右对称） | 60 × 26 |
| `aurora_fx_r_zone` | view_effects `league_aurora_r_zone`（大表，地上，z -1，不跟随；左右对称；放 3.5 秒） | 80 × 34 |
| `aurora_fx_r_hit` | view_effects `league_aurora_r_hit`（跟随目标，z 2；左右对称） | 16 × 20 |
| `aurora_fx_r_blink` | view_effects `league_aurora_r_blink`（在她传送到的敌人身边，z 3；左右对称） | 24 × 44 |

- 两张表：`asset/league/effects/league_aurora_fx`（小的）和 `league_aurora_big`（r_shock、r_zone），tag = 名字（build_aurora.py 的 views；q_ball 用 q_out 的 tag，三个减速用 `slow`）。
- 弹道（a_bolt、q_out、q_back、e_wave）断言上下对称；其余断言左右对称；r_zone 放在地上 3.5 秒（循环），q_curse 跟随 70 帧左右，p_mark 4 秒。
- 用 `pixel_1x/` 切格（import_illaoi_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
