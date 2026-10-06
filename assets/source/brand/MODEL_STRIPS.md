# 布兰德：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/brand_design.png`（放大 8 倍，1024×1024；连头顶火焰 43 行高、37 格宽，22 色；脚底在第 99 行，两脚中间在第 64 列）。它是你上一轮生图原稿 `refs/brand_draft_codex.png` 按格子读回、整行整列删到光头顶到脚底 37 行的版本，用户确认过（头也不改）。**造型图就是标准**：焦黑带紫的身体和亮橙熔岩裂纹、胸口最亮的竖裂、光头和头顶一簇火焰、两只黄色发光眼睛、两只火焰手、棕褐破长裤和铜扣、光脚，颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`brand_idle.png`），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 7 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/brand_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **和参考图不一样、以造型图为准的地方**：① 我们照造型图的比例（头大）；② 头是贴上去的（见下），**头每帧不变形、不旋转、始终是造型图的 3/4 侧脸**，**不画背影**；头顶火焰跟头一起贴；③ **腿**：in the standing frames (idle, the wind-ups, the hit) he stands on the design's OWN legs square for square - the same slight crouch, the same tan-brown torn trousers with the copper buckles and the bare charred feet, never spread wider, never shorter; in the throws, the slam and the leap he may step, lunge, crouch or jump as the THIRD image shows, the legs keeping the design's materials and thickness (the WHOLE figure moves with them, never the upper body alone over still legs); only the run steps and only the death falls；④ 手：he has no weapon: his two HANDS are the design's FIRE HANDS (red-orange outside, yellow inside) at the design's size in every frame - never shrunk, never turned into fireballs, never dropped; the fireballs, pillars and flames he throws are effects drawn later, not in these strips；⑤ 手臂：the arms are the design's arms: charred purple-grey with the orange lava cracks, the forearms turning red to the fire hands, the same thickness as in the design in every frame - never thinner, never 1-pixel sticks, never floating hands; each arm comes out of the outer corner of its shoulder and moves as ONE piece with its hand (no stretched or bent-rubber arms); both hands are always in sight in front of or beside his body, never hidden behind it; the bare chest with its bright crack, the belt and the trousers stay on him。
> - **施法的身体就是待机的身体**：放技能时躯干、胸口裂纹、裤子照待机逐格不变，只有手臂（连火焰手整块）和必要时整个人一起动；手臂从肩膀外角出来，不拉长、不错行，手不能藏到身体后面。
> - 出招方向：**甩火球、砸地、放火、推火球都朝图的右边**（游戏里朝左时会整张镜像）。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**：图1 = `now/brand_now_<动作>.png`（骨架：帧数、每格位置、大小、姿势），图2 = `design/brand_design.png`（皮囊），下面有那段简短中文提示词；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行**。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/brand-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧出手那只火焰手的位置）和所有生图原稿（`raw/`），最好打成一个 zip（`brand_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/brand_palette.png`，或直接读 `design/brand_design_1x.png`）。
4. **贴头**：把造型图的头（`design/brand_head_1x.png` 里不透明的格子：头顶火焰、光头、脸到下巴；在 128×128 画布上的范围 x 57–74、y 57–71，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移）。贴之前先擦掉你自己画的头，不要在头旁边留下多余的火焰或描边。
5. 对位：每帧按 `brand_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底落在脚底线上；检查线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/brand_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/brand_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/brand_head.png`、`_1x.png` | 要贴进每一帧的头（头顶火焰、光头、脸到下巴） | 贴头 |
| `design/brand_palette.png` | 造型图的全部 22 色（暗到亮） | 色板 |
| `brand_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/brand_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂和身体的动作 |
| `guide/brand_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `brand_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/brand_picture.png`、`refs/brand_draft_codex.png` | 用户选的原画 A 和你的生图原稿（长相参考；比例以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一样的像素**：待机姿态时和造型图一样高（43 行），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 22 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边。
- **腿**：in the standing frames (idle, the wind-ups, the hit) he stands on the design's OWN legs square for square - the same slight crouch, the same tan-brown torn trousers with the copper buckles and the bare charred feet, never spread wider, never shorter; in the throws, the slam and the leap he may step, lunge, crouch or jump as the THIRD image shows, the legs keeping the design's materials and thickness (the WHOLE figure moves with them, never the upper body alone over still legs); only the run steps and only the death falls。
- **手**：he has no weapon: his two HANDS are the design's FIRE HANDS (red-orange outside, yellow inside) at the design's size in every frame - never shrunk, never turned into fireballs, never dropped; the fireballs, pillars and flames he throws are effects drawn later, not in these strips。
- **手臂**：the arms are the design's arms: charred purple-grey with the orange lava cracks, the forearms turning red to the fire hands, the same thickness as in the design in every frame - never thinner, never 1-pixel sticks, never floating hands; each arm comes out of the outer corner of its shoulder and moves as ONE piece with its hand (no stretched or bent-rubber arms); both hands are always in sight in front of or beside his body, never hidden behind it; the bare chest with its bright crack, the belt and the trousers stay on him。
- **头每帧都是造型图的头**（头顶火焰、光头、发光的眼睛、脸逐格一样），只平移。
- **脚底线以下什么都不能有**（游戏在脚下画血条）。
- **跑步循环**：每帧头相对站位点的横向位置不变；两条腿交叉交替迈步，远侧腿暗一档，着地的脚踩在线上；上下起伏约 1 格；首尾能无缝接上。
- 3/4 侧前方朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立**。**只画角色**：火球、火柱、地上的火、火焰风暴都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/brand_design.png`，第二张 `now/brand_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `brand_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, body and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 view facing right, the same charred purple-grey body with the bright orange lava cracks and the brightest crack down the chest, the bald head with the crown of FLAMES on top, the two glowing yellow eyes, the two FIRE HANDS, the tan-brown torn trousers with the copper buckles, the bare charred feet, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the arms and the body from it, but keep the FIRST image's proportions (43 squares tall with the flames, a big head); never draw him from the back or upside down.
The character: Brand, the Burning Vengeance (a man burned into living charcoal, flames on his head, fire hands).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (43 squares from the top of the flames to the soles in the idle stance), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 22 colors of the FIRST image, no new colors: #080307 #350607 #21121E #4D090A #3A2A1F #352134 #A30806 #513E2D #B80402 #453646 #F01D09 #805B40 #B46117 #706278 #F95307 #AA784B #FA7406 #CD7D2B #FC9103 #FBC302 #FCCC02 #FADA03. A 1-square near-black outline around the silhouette. Copy the FIRST image's shading; no dithering, no noise, no random specks added.
The casting body is the idle body: in every frame his torso, chest crack, belt and trousers are the FIRST image's, square for square; only the arms (each arm and its fire hand as one rigid piece) and, where the animation needs it, the whole figure move.
Legs: in the standing frames (idle, the wind-ups, the hit) he stands on the design's OWN legs square for square - the same slight crouch, the same tan-brown torn trousers with the copper buckles and the bare charred feet, never spread wider, never shorter; in the throws, the slam and the leap he may step, lunge, crouch or jump as the THIRD image shows, the legs keeping the design's materials and thickness (the WHOLE figure moves with them, never the upper body alone over still legs); only the run steps and only the death falls.
The hands: he has no weapon: his two HANDS are the design's FIRE HANDS (red-orange outside, yellow inside) at the design's size in every frame - never shrunk, never turned into fireballs, never dropped; the fireballs, pillars and flames he throws are effects drawn later, not in these strips.
The arms: the arms are the design's arms: charred purple-grey with the orange lava cracks, the forearms turning red to the fire hands, the same thickness as in the design in every frame - never thinner, never 1-pixel sticks, never floating hands; each arm comes out of the outer corner of its shoulder and moves as ONE piece with its hand (no stretched or bent-rubber arms); both hands are always in sight in front of or beside his body, never hidden behind it; the bare chest with its bright crack, the belt and the trousers stay on him.
The head (the flames on top, the bald skull, the glowing eyes, the face to the chin) is COPIED from the FIRST image in every frame, square for square, and only moved; never redraw, squash, turn or tilt it, or it flickers when the frames play. Erase your own head before pasting it, so no extra flame or outline is left beside it.
Feet line: in every cell his soles are on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there. His place across the cell follows the SECOND image (each frame's standing point is in brand_cells.json). In the run his head keeps the same horizontal place relative to the standing point in every frame.
3/4 view like the FIRST image; every throw, slam and blast goes to the RIGHT of the image; never his back, never upside down. Do not draw effects (fireballs, pillars, ground fire, fire storms, trails) - only the character. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 128x96 squares (1024x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, the torso the idle's torso, both arms and both fire hands in sight in every frame, the legs the design's legs, no loose pieces, no stray black squares, nothing below the feet line, never his back or upside down, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块，人物不能变大也不能变小。
2. 保留每一帧的动作：手臂和身体的方向和姿势照图1；站着的动作腿用图2自己的腿；身体（胸口裂纹、裤子）照图2不变；两只火焰手不能藏到身体后面。
3. 长相、配色、细节全部换成图2：焦黑带紫的身体和亮橙熔岩裂纹、胸口亮裂纹、光头和头顶火焰、黄色发光眼睛、两只火焰手、棕褐破长裤和铜扣、光脚。
4. 动作：[animation]
背景保持纯绿色 #00FF00，方便抠图。风格保持与图2一致。重点在于精准复刻图1的“动作骨架”，只是换了“皮囊”。
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `brand_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，3072×1536 | 第 81 行 | **已做好，不用画** |
| `brand_run.png`（跑步） | 8 × 125 | — | 4 列 × 2 行，4096×1536 | 第 81 行 | `RUN, 8 frames, one seamless loop (League's run, 1.0 s a cycle): the design's own legs (his trousers and bare feet) step from the hips in a CROSSING stride - left and right alternate, the leading foot changes every half cycle, the feet at most 12 squares apart, the far leg one shade darker - the planted foot on the feet line; the body leans a little forward and bobs about 1 square; the arms swing a little at his sides with the fire hands open; the head flames flicker a little; his head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `brand_attack.png`（普攻（甩火球）） | 6 帧：60 60 60 70 80 100 | 第 4 帧（tick 11） | 3 列 × 2 行，3072×1536 | 第 81 行 | `FIREBALL THROW (basic attack), 6 frames: 1 from the idle stance the front hand drawn back; 2-3 the arm wound back and up beside his head, the body twisting; 4 THE THROW (the fireball leaves here): the front arm whipped forward and down to the image right, the body bending forward 1-2 squares; 5 the follow-through; 6 back toward the idle stance. The fireball is an effect - do not draw it.` |
| `brand_skill.png`（W 烈焰之柱（双手高举后砸地）） | 6 帧：50 60 70 80 80 100 | 第 4 帧（tick 11） | 3 列 × 2 行，3072×1536 | 第 81 行 | `PILLAR OF FLAME (W), 6 frames: 1 from the idle stance both hands come up; 2-3 BOTH fire hands raised HIGH over his head, the body stretched up; 4 THE SLAM (the pillar rises here): he crouches and slams both hands down to the ground in front of him (image right), knees bent, head low; 5 still low; 6 rising back toward the idle stance. The ground fire and the pillar are effects.` |
| `brand_skill2.png`（E 烈火燃烧接 Q 火焰烙印（张臂放火后前推火球）） | 8 帧：40 60 70 60 60 70 80 100 | 第 6 帧（tick 17） | 4 列 × 2 行，4096×1536 | 第 81 行 | `CONFLAGRATION then SEAR (E then Q), 8 frames: 1-2 both fire hands pulled together in front of his chest, gathering; 3 THE BLAZE (E lands here): both arms flung wide open to the sides, the chest out; 4-5 the front hand drawn back to his shoulder, the body coiled; 6 THE FIREBALL (Q leaves here): the front arm thrust straight out to the image right, palm forward; 7 the follow-through; 8 back toward the idle stance. The blaze and the fireball are effects.` |
| `brand_ult.png`（R 烈焰风暴（跃起张臂）） | 6 帧：50 60 70 80 100 120 | 第 4 帧（tick 11） | 3 列 × 2 行，3072×1536 | 第 81 行 | `PYROCLASM (R), 6 frames: 1 he crouches, hands low; 2-3 he leaps up a little (the feet 3-5 squares off the ground at most), knees tucked, the hands gathered at his chest; 4 THE RELEASE (the fire seed leaves here): in the air both arms flung wide open, the chest out, the head back; 5 coming down, arms still open; 6 landing back in the idle stance. The fire is an effect.` |
| `brand_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，2048×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow: his whole body and head pushed back 1-2 squares (to the left), the head flames swaying; 2 recovering toward the idle stance. The design's legs.` |
| `brand_dead.png`（死亡（照希维尔：受击、击退、45° 倒下、90° 躺平）） | 8 帧：100 110 110 120 130 150 200 300 | — | 4 列 × 2 行，4096×1536 | 第 81 行 | `DEATH, 8 frames (like the pack's league_sivir death): 1 struck, he staggers back; 2 knocked back a step, the arms thrown up; 3-4 the WHOLE figure falls backward stiffly, tilting to about 45 degrees (turned about the feet, not bent); 5-6 lying flat on his back at 90 degrees on the ground, the head to the left; 7-8 still, the head flames low and small; 7 and 8 the same pose. The head is the design's head turned with the body, never upside down. Nothing below the feet line.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色，明暗照定稿，没有自己加的碎点；
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（逐格一样，只平移），头旁边没有多余的火焰、描边；
- [ ] 躯干是待机的躯干；两只手臂和两只火焰手都在、看得见、不藏在身后；手臂从肩膀外角出来，整块动、不拉长；腿和造型图一样的材质和粗细；
- [ ] 脚底线以下没有任何像素；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立；出招都朝图的右边；
- [ ] 跑步循环：头的横向位置每帧一样，两腿交叉交替、远侧腿暗一档，上下起伏约 1 格，首尾能接上；
- [ ] 死亡照希维尔：受击、击退、整个人 45° 倒下、90° 躺平；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 写全；生图原稿放进 `raw/`；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `brand_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、腿和待机比、零散黑格、每帧面积和待机比、手看不看得见），不在网格上的按格取多数色重读；头不对的帧换回造型图的头；放技能时的身体换回待机的身体，手臂连火焰手整块转（rigkit），不画骨骼；rigkit.finish 后保留 2 格以上的缝。
- 放进 `assets/source/native/`，`brand_cells.json` 用包里这份，`brand_idle.png` 用包里已做好的那张。
- `import_native.py`：ORDER 待机一张图，COMPLETE 补描边。
- 按出手帧核对技能数据的时机（普攻 tick 11、W 烈焰之柱 tick 11、E 烈火燃烧接 Q 火焰烙印 tick 17、R 烈焰风暴 tick 11），量出手手的位置和头像截取点；有朝向的施法特效按红方规则画进动作帧（brand_bake.json）；重跑模拟，做预览 GIF。
