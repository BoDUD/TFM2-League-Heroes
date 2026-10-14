# 虚空先知 玛尔扎哈：给 Codex 的特效提示词（第 3 步）

> **这一份是 13 张特效图。** 造型和动作已定（`design/malzahar_idle.png`：游戏里的 3/4 正面待机，悬浮，脚尖朝下）。他在游戏里约 33 格宽、42 格高（悬浮离地约 3 格）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素）。
> - 大小对照 `design/malzahar_size.png`：他在游戏里的样子放大 4 倍，红线是地面，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/malzahar_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效从哪里出来。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里玛尔扎哈自己的特效贴图（虚空弹、幻象的电弧和烟、W 的虚空门、Q 的电弧、R 的触手和虚空），按用在我们哪张特效分好了行；`refs/voidling.png` 是英雄联盟里虚空虫的模型（灰紫色甲壳头、洋红色眼睛、镰刀前爪）。都只在本地用，不要提交。颜色照英雄联盟原版：**虚空的紫色和紫黑色、紫白色的光、他的洋红色、虚空虫灰紫色的壳和洋红色的眼睛**。
> - **特效要亮**：每道光、每个电弧都要有白色或最亮一档的芯，暗底上一眼能看见；暗紫黑的虚空物质（触手、领域、烟）旁边要有亮紫色的边，不然在暗底上看不见。
> - **围着人的光壳、电弧、触手、虫子只画外圈，中间人形位置留空**。
> - **方向（重要，红色方不会镜像）**：飞出去的 `a_bolt`、`e_bolt` 画成朝右，**上下对称**（往左飞时会上下翻）。其余所有画面（打中、身上、脚下、地上的圈、裂隙、虫子、触手、护盾）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）：两只虚空虫画成一左一右互相对着的镜像，两道裂隙、两条触手也是镜像。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `malzahar_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `malzahar_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「虚空穿越」 | 甩出虚空弹；身上一层虚空护盾（被打破后过一会儿回来） | `a_bolt` · `a_hit` · `p_shift` |
| 技能 1 = E「煞星幻象」+ W「虚空虫群」 | 幻象飞向目标、缠住他持续掉血（目标死了会跳到附近的敌人）；虚空虫从目标脚下钻出来咬他 | `e_bolt` · `e_hit` · `e_mark` · `w_spawn` · `w_swarm` · `w_bite` |
| 技能 2 = Q「虚空召唤」 | 目标两侧撕开两道裂隙，光束在中间相撞：伤害 + 沉默 | `q_rift` · `q_hit` |
| 大招 = R「冥府之握」 | 压制一个敌方英雄 2.5 秒（虚空触手缠住他），脚下留下 5 秒的虚空领域 | `r_grasp` · `r_pool` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、电弧、光环都没有黑描边，也不要用最深的颜色给光描一圈边**（暗紫黑的触手、领域可以用自己最深一档收边）。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 虚空紫光：`#FFFFFF`、`#F3E3FF`、`#D9A6FF`、`#B163F5`、`#8130D9`、`#5A169E`、`#36095F`；
  - 虚空暗紫：`#4A1C7A`、`#2E0F52`、`#1C0838`、`#100422`；
  - 洋红：`#FFE3F4`、`#FF86D2`、`#EE3AA6`、`#B4187A`、`#6E0B4B`；
  - 虚空虫的甲壳：`#EFE6F2`、`#C6B4D2`、`#9682A8`、`#67527A`、`#3D2C4E`；
- 打中、爆发居中画，不旋转；地面上的门、领域是从斜上方看的椭圆（宽是高的 2.5–3 倍）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（13 张）

13 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 52000，Q 打中半径 18000，R 领域半径 20000，E 跳转距离 40000）。

### 1. `malzahar_fx_a_bolt.png`：普攻：飞出去的虚空弹（朝目标飞，循环），4 帧

从手心甩出去的一颗小虚空弹：紫白色的小光球，外面一圈紫色，后面拖一小段暗紫色的虚空烟和几个小光点（参考 BA_mis_dots、BA_Mis_mult、common_voidtrailhot）。**上下对称**，朝右飞。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks or rings (dark void matter may have its own darkest shade at its edge), BRIGHT light (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void-violet ramp (#FFFFFF, #F3E3FF, #D9A6FF, #B163F5, #8130D9, #5A169E, #36095F) and a dark void ramp (#4A1C7A, #2E0F52, #1C0838, #100422).
Effect: a SMALL VOID BOLT flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a white-violet glowing ball 4 squares across at the front inside a violet halo, a short tapering trail of dark purple void smoke behind it with 2-3 violet motes flickering in turn.
Layout: one horizontal row of 4 equal 12:8 cells, image size 768x128 (each cell 192x128, 16 px a square); the ball's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `malzahar_fx_a_hit.png`：普攻打中（目标身上），4 帧

虚空弹打中：目标身上紫白色的光一闪，炸成一圈小小的紫色火花（参考 BA_muzzle_flash、common_voidslash）。**左右对称**。约 10 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks or rings (dark void matter may have its own darkest shade at its edge), BRIGHT light (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void-violet ramp (#FFFFFF, #F3E3FF, #D9A6FF, #B163F5, #8130D9, #5A169E, #36095F).
Effect: a VOID HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 3 squares; 2 a violet four-pointed burst 8 squares across with a white core; 3 the burst breaking into 6 small violet sparks at mirrored places, 10 squares across; 4 two fading specks.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `malzahar_fx_e_bolt.png`：E 煞星幻象：飞出去的幻象（朝目标飞，循环），4 帧

飞向目标的幻象：前头一团暗紫色的虚空球，中间一点紫白的光，球面上闪着细细的紫色电弧，后面拖一条扭动的暗紫色烟尾（参考 E_Mis_AlphaCircles、E_Lightning03、E_SmokeErode、Demon_Trail4）。**上下对称**，朝右飞。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks or rings (dark void matter may have its own darkest shade at its edge), BRIGHT light (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void-violet ramp (#FFFFFF, #F3E3FF, #D9A6FF, #B163F5, #8130D9, #5A169E, #36095F) and a dark void ramp (#4A1C7A, #2E0F52, #1C0838, #100422).
Effect: a DARK VISION ORB flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a dark purple void ball 6 squares across with a white-violet core and thin violet lightning crackling over it (the crackle pattern mirrored top to bottom), a wavy dark purple smoke tail 8 squares long behind it, its two edges mirrored.
Layout: one horizontal row of 4 equal 16:10 cells, image size 1024x160 (each cell 256x160, 16 px a square); the ball's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `malzahar_fx_e_hit.png`：E 打中：幻象缠上目标（目标身上），5 帧

幻象缠上目标的一下：一圈暗紫色、带锯齿边的虚空环在目标身上一合（参考 E_Edges、E_ImpactT），环里闪出紫白的光，几道紫色电弧往外蹦。**左右对称**，中间人形位置留空。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks or rings (dark void matter may have its own darkest shade at its edge), BRIGHT light (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void-violet ramp (#FFFFFF, #F3E3FF, #D9A6FF, #B163F5, #8130D9, #5A169E, #36095F) and a dark void ramp (#4A1C7A, #2E0F52, #1C0838, #100422).
Effect: a VISION LATCHING on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), its middle EMPTY (a clear upright area 8 squares wide): 1 a white violet flash 4 squares; 2 a jagged dark purple ring 18 squares across closing in, violet light along its inner edge; 3 the ring 12 squares across, 4 violet lightning sparks jumping out at mirrored places; 4 the ring breaking into dark wisps; 5 fading wisps.
Layout: one horizontal row of 5 equal square cells, image size 1600x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `malzahar_fx_e_mark.png`：E 幻象持续：缠在目标身上的虚空电弧（目标身上，1 秒循环），4 帧

被煞星幻象缠住：目标上半身两边有暗紫色的虚空烟一缕缕往上飘，烟里噼啪闪着细细的紫白电弧（参考 E_Static_01、E_Lightning03、P_Morgana_Base_E_Wisps）。**中间人形位置留空**，**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks or rings (dark void matter may have its own darkest shade at its edge), BRIGHT light (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void-violet ramp (#FFFFFF, #F3E3FF, #D9A6FF, #B163F5, #8130D9, #5A169E, #36095F) and a dark void ramp (#4A1C7A, #2E0F52, #1C0838, #100422).
Effect: VOID WISPS AND CRACKLES round a unit's upper body, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY (a clear upright area 10 squares wide and 22 tall): at each side 2 thin dark purple wisps rising and curling, small white-violet lightning zigzags (2-4 squares) flickering in them at mirrored places, a different pair lit in each frame.
Layout: one horizontal row of 4 equal 24:28 cells, image size 1536x448 (each cell 384x448, 16 px a square); centered across, the wisps' bottom 2 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `malzahar_fx_w_spawn.png`：W 虚空虫群：虫子出现的小虚空门（目标脚下），4 帧

虚空虫从地下钻出来的门：目标脚下一个扁扁的紫色虚空门（从斜上方看的椭圆，亮紫色的边，中间深紫黑，参考 W_VoidGate_Core_ring、W_VoidGate_DarkGround、W_Portal_Swirl），打开、闪光、合上。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks or rings (dark void matter may have its own darkest shade at its edge), BRIGHT light (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void-violet ramp (#FFFFFF, #F3E3FF, #D9A6FF, #B163F5, #8130D9, #5A169E, #36095F) and a dark void ramp (#4A1C7A, #2E0F52, #1C0838, #100422).
Effect: a SMALL VOID GATE on the ground, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse 22 squares wide and 8 tall, its rim bright violet 1 square thick, its inside dark purple-black with a violet swirl; 1 a thin violet line opening; 2 the gate open, a few violet motes spurting up at mirrored places; 3 the gate's rim brightest; 4 the gate shrinking to a thin fading line.
Layout: one horizontal row of 4 equal 24:10 cells, image size 1536x160 (each cell 384x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `malzahar_fx_w_swarm.png`：W 虚空虫：两只虚空虫在目标脚边咬他（目标身上，1 秒循环），4 帧

两只虚空虫（参考 `refs/voidling.png`：灰紫色的甲壳头、两三只发光的洋红色眼睛、紫色的身体、镰刀一样的前爪），**一左一右在目标脚边，互相对着（左边那只朝右、右边那只朝左，像镜子一样对称）**，扑上去咬目标、退回来，轮流。中间人形位置留空。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks or rings (dark void matter may have its own darkest shade at its edge), BRIGHT light (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a lilac-grey shell ramp (#EFE6F2, #C6B4D2, #9682A8, #67527A, #3D2C4E), a dark void ramp (#4A1C7A, #2E0F52, #1C0838, #100422) and a magenta ramp (#FFE3F4, #FF86D2, #EE3AA6, #B4187A, #6E0B4B).
Effect: TWO VOIDLINGS biting at a unit's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the left one facing right, the right one its mirror image facing left), the middle EMPTY (a clear area 14 squares wide): each voidling 9 squares wide and 8 tall - a lilac-grey armored head with 2-3 glowing magenta eyes and small fangs, a dark purple body, two sickle claws, short legs; 1 both crouched; 2 both lunging inward 2 squares, claws raised; 3 both biting (closest); 4 both springing back.
Layout: one horizontal row of 4 equal 36:14 cells, image size 2304x224 (each cell 576x224, 16 px a square); centered across, their feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `malzahar_fx_w_bite.png`：W 虫子咬一口（目标身上），3 帧

虚空虫咬中：目标身上两道洋红色的爪痕交叉一闪（左右对称的 X），几个小紫点溅开。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks or rings (dark void matter may have its own darkest shade at its edge), BRIGHT light (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta ramp (#FFE3F4, #FF86D2, #EE3AA6, #B4187A, #6E0B4B) and a void-violet ramp (#FFFFFF, #F3E3FF, #D9A6FF, #B163F5, #8130D9, #5A169E, #36095F).
Effect: a VOIDLING BITE on a unit, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 two magenta claw marks crossing as an X, 8 squares, white at the crossing; 2 the X brighter, 4 violet specks flying out at mirrored places; 3 fading marks.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `malzahar_fx_q_rift.png`：Q 虚空召唤：目标两侧的两道裂隙，合拢时两道光束在中间相撞（地上，不跟随，约 0.5 秒），6 帧

虚空召唤：目标**左右两边**各撕开一道竖着的虚空裂隙（细长的紫黑色裂口，边缘亮紫色、闪着电弧，参考 W_Portal_Swirl、Q_Lightning03、Q_OrbEdge），慢慢张开发亮；然后**两道裂隙同时朝中间射出紫白色的光束，在正中间撞在一起**一炸，裂隙合上。**左右对称**（两道裂隙是一对镜像）。两道裂隙相距约 36 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks or rings (dark void matter may have its own darkest shade at its edge), BRIGHT light (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void-violet ramp (#FFFFFF, #F3E3FF, #D9A6FF, #B163F5, #8130D9, #5A169E, #36095F) and a dark void ramp (#4A1C7A, #2E0F52, #1C0838, #100422).
Effect: TWO VOID RIFTS facing each other, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): two upright rifts 36 squares apart (their middles at columns 2 and 37 of the 40), each a narrow dark purple-black tear 4 squares wide and 20 tall with a bright violet jagged rim and small lightning crackles; 1 two thin violet cracks; 2 the rifts half open; 3 fully open, dark inside; 4 the rims brightest, violet light gathering inside; 5 two white-violet beams 3 squares thick shooting from both rifts to the middle and meeting there in a white flash 8 squares across (one straight horizontal line across the whole width at the rifts' middle height); 6 the beams gone, the rifts closing to fading cracks.
Layout: one horizontal row of 6 equal 42:26 cells, image size 4032x416 (each cell 672x416, 16 px a square); centered across, the rifts' bottom 2 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `malzahar_fx_q_hit.png`：Q 打中：被沉默（目标身上），4 帧

被虚空光束打中、沉默：目标身上紫白的光一炸，散成一圈紫色电火花（参考 Q_Lightning03、common_voidslash）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks or rings (dark void matter may have its own darkest shade at its edge), BRIGHT light (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void-violet ramp (#FFFFFF, #F3E3FF, #D9A6FF, #B163F5, #8130D9, #5A169E, #36095F).
Effect: a VOID BLAST on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-violet flash 5 squares; 2 a violet burst 12 squares across with a white core; 3 a ring of 8 small violet lightning sparks 14 squares across at mirrored places; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `malzahar_fx_r_grasp.png`：R 冥府之握：从地下伸出来抓住目标的虚空触手（目标身上，循环），4 帧

被冥府之握压制：两条暗紫色的虚空触手从目标脚下两边伸出来，弯上去缠住目标的腰和胸口（触手边缘亮紫色，上面有一节节的纹路，参考 W_VoidTentacles_01、Z_VoidTentacles_01、R_beam_Palette），触手间闪着紫白的电弧，微微扭动。**左右对称**（两条触手是一对镜像），中间人形位置留空。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks or rings (dark void matter may have its own darkest shade at its edge), BRIGHT light (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dark void ramp (#4A1C7A, #2E0F52, #1C0838, #100422), a void-violet ramp (#FFFFFF, #F3E3FF, #D9A6FF, #B163F5, #8130D9, #5A169E, #36095F) and a magenta ramp (#FFE3F4, #FF86D2, #EE3AA6, #B4187A, #6E0B4B).
Effect: VOID TENTACLES GRIPPING a unit, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY (a clear upright area 10 squares wide and 24 tall): two thick dark purple tentacles rising from the ground at both sides, 4 squares thick at the root tapering to 2, curling up and inward round the unit's waist and chest, their edges bright violet, magenta segment marks on them; small white-violet lightning crackling between them; the tentacles writhing a little from frame to frame (every frame mirrored).
Layout: one horizontal row of 4 equal 28:32 cells, image size 1792x512 (each cell 448x512, 16 px a square); centered across, the tentacles' roots on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `malzahar_fx_r_pool.png`：R 冥府领域：目标脚下的虚空领域（地上，不跟随，5 秒），8 帧

冥府之握留下的虚空领域：地上一个大圆（从斜上方看的扁椭圆），边缘一圈亮紫色，里面是暗紫黑色的虚空，里面有紫色的星点和慢慢转的漩涡（参考 Void_03、Void_05、Crater_01、W_VoidGate_DarkGround），边上一圈小火苗一样的紫色光往上冒。**左右对称**。范围约 40 格宽（半径 20000）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks or rings (dark void matter may have its own darkest shade at its edge), BRIGHT light (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dark void ramp (#4A1C7A, #2E0F52, #1C0838, #100422), a void-violet ramp (#FFFFFF, #F3E3FF, #D9A6FF, #B163F5, #8130D9, #5A169E, #36095F) and a magenta ramp (#FFE3F4, #FF86D2, #EE3AA6, #B4187A, #6E0B4B).
Effect: a NULL ZONE on the ground, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse 40 squares wide and 14 tall, its rim violet 1-2 squares thick, its inside dark purple-black with violet star motes and a slow violet swirl, small violet flames licking up from the rim at mirrored places; 1 a thin violet ring appearing; 2 the zone filling; 3-6 a seamless loop: the swirl and the flames shifting step by step (every frame mirrored); 7 the zone fading to its rim; 8 a faint thin ring.
Layout: one horizontal row of 8 equal 42:16 cells, image size 5376x256 (each cell 672x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `malzahar_fx_p_shift.png`：被动 虚空穿越：玛尔扎哈身上的虚空护盾（他身上，循环），4 帧

虚空穿越的护盾：玛尔扎哈全身外面一层很薄的紫白色光壳（竖着的椭圆，只画边缘一两格宽的弧光，上面几处亮的高光，参考 P_Shield_Edges、Q_Shield_Edges），光在边上慢慢流动。**中间人形位置留空**（他自己在里面），**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks or rings (dark void matter may have its own darkest shade at its edge), BRIGHT light (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void-violet ramp (#FFFFFF, #F3E3FF, #D9A6FF, #B163F5, #8130D9, #5A169E, #36095F).
Effect: a THIN VOID SHELL round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), its inside EMPTY (a clear upright area 28 squares wide and 38 tall): an upright ellipse 34 squares wide and 44 tall drawn only as a thin violet rim 1 square thick, brighter white-violet arcs 6-8 squares long on it at mirrored places moving one step round in each frame, a few violet motes beside the rim.
Layout: one horizontal row of 4 equal 36:46 cells, image size 2304x736 (each cell 576x736, 16 px a square); centered across, the shell's bottom 1 square above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `malzahar_fx_a_bolt` | view_projectiles `league_malzahar_a_bolt`（朝飞行方向转，画成朝右飞；上下对称） | 10 × 6 |
| `malzahar_fx_a_hit` | view_effects `league_malzahar_a_hit`（跟随，画在人物上面；左右对称） | 10 |
| `malzahar_fx_e_bolt` | view_projectiles `league_malzahar_e_bolt`（朝飞行方向转，画成朝右飞；上下对称） | 14 × 8 |
| `malzahar_fx_e_hit` | view_effects `league_malzahar_e_hit`（跟随，画在人物上面；左右对称） | 18 |
| `malzahar_fx_e_mark` | view_effects `league_malzahar_e_mark`（跟随，画在人物上面；左右对称；4 帧 1 秒，幻象持续时每秒放一次）；附加包跳过去的幻象也用这张（buff `league_malzahar_e_markb`） | 22 × 26 |
| `malzahar_fx_w_spawn` | view_effects `league_malzahar_w_spawn`（跟随，画在人物下面；左右对称） | 22 × 8 |
| `malzahar_fx_w_swarm` | view_effects `league_malzahar_w_swarm`（跟随，画在人物下面；左右对称；4 帧 1 秒，每秒放一次，持续 4 秒） | 34 × 12 |
| `malzahar_fx_w_bite` | view_effects `league_malzahar_w_bite`（跟随，画在人物上面；左右对称） | 10 |
| `malzahar_fx_q_rift` | view_effects `league_malzahar_q_rift`（不跟随，画在人物上面；左右对称；前 4 帧 0.4 秒，第 5 帧光束相撞=伤害生效） | 40 × 24 |
| `malzahar_fx_q_hit` | view_effects `league_malzahar_q_hit`（跟随，画在人物上面；左右对称） | 14 |
| `malzahar_fx_r_grasp` | view_effects `league_malzahar_r_grasp`（跟随，画在人物上面；左右对称；4 帧共 0.25 秒，引导时每 0.25 秒放一次） | 26 × 30 |
| `malzahar_fx_r_pool` | view_effects `league_malzahar_r_pool`（不跟随，画在人物下面；左右对称；1-2 打开，3-6 循环，7-8 消失，导入时拼成 5 秒） | 40 × 14 |
| `malzahar_fx_p_shift` | view_buffs `league_malzahar_p_shift`（跟随，画在人物上面；左右对称） | 34 × 44 |

- 两张表：`asset/league/effects/league_malzahar_fx`（小的）和 `league_malzahar_big`（q_rift、r_grasp、r_pool），tag = 名字（build_malzahar.py 的 views；`e_markb` 绑到 `e_mark` 这张）。
- 飞行的 `a_bolt`、`e_bolt` 朝飞行方向转；`q_rift`、`r_pool` 不跟随；`e_mark`、`w_swarm` 4 帧 1 秒；`r_grasp` 4 帧 0.25 秒；`q_rift` 前 4 帧共 24 tick、第 5 帧光束相撞；`r_pool` 拼成 5 秒（1-2 打开、3-6 循环、7-8 消失）。
- 用 `pixel_1x/` 切格（import_bard_fx 的做法），断言对称；必要时从 raw 重读（Codex 的读回可能清掉中间）；核对交回的张数和这份清单。
