# 凯南：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是你画的**版本 A**，按约德尔人的尺寸裁成 **37 格高**（只删整行整列；**脸、眼睛、手都照你原稿，没改**）：`design/kennen_design.png`（放大 8 倍，1024×1024；手里剑顶到脚底 37 格，兜帽顶到脚底 31 格，27 格宽，21 色；脚底在第 99 行，两脚中间在第 64 列）。**造型图就是标准**：紫色兜帽和两只尖耳朵、金色闪电镶边、脸上的蓝眼睛和眉毛、紫色面罩、紫色长袍和金边、肩甲、两只深紫爪子手套和钢片、短腿和忍者鞋、**背上的大金色手里剑**，颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`kennen_idle.png`，每帧就是造型图，站在待机的站位点上），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 8 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/kennen_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂和手里剑的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **和参考图不一样、以造型图为准的地方**：① 参考图是英雄联盟的比例，我们**照造型图的比例**（大兜帽头、小身子、短腿，手里剑是造型图的大小和样子）；② 头是贴上去的（见下），英雄联盟里他会低头、扭头，我们**头每帧不变形、不旋转、始终是造型图的 3/4 正面**（死亡倒地时整个头跟着身体转），**不画背影**；③ 移动：英雄联盟的忍者跑身子压得很低，我们身体最多前倾 25 度左右，头保持竖直；④ **E 雷铠**：英雄联盟里他整个人变成闪电，我们画一个压低身子的疾冲姿势，闪电球是第 3 步的特效，这里不画。
> - **背上的手里剑**：每帧都背在背上（两个金色尖角从兜帽后面左上方和肩膀后面露出来，和造型图一样），只有这几帧例外：普攻第 1–4 帧拿在手里、第 5 帧已经甩出去（背上空着），W 第 1–4 帧拿在手里，大招第 2–5 帧拿在手里，死亡第 5–8 帧掉在地上。
> - 出招方向：**甩手里剑、出手、冲刺都朝图的右边**（游戏里朝左时会整张镜像）。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox）和 `generation_prompts.json`，最好打成一个 zip（`kennen_strips_pack_done.zip`，放在 outputs 里）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/kennen_palette.png`，或直接读 `design/kennen_design_1x.png`）。**先把眼睛专用的蓝色 `#3FAEF8` 从色板里去掉**（吸附时会跑到别的地方），它只随第 4 步贴的头回来。
4. **贴头**：把造型图的头（`design/kennen_head_1x.png` 里不透明的格子：兜帽和两只耳朵、脸、眼睛、面罩，到兜帽下沿为止；在 128×128 画布上的范围 x 54–78、y 68–82，**按图里的形状贴，不是整个方框**——左边的手里剑不属于头，它跟着身体/手走）原样贴进每一帧头的位置（只平移；死亡倒地的帧整个头跟着转 90 度）。这样每帧的脸都和造型图一模一样。头下面接长袍的领口和肩膀，不要拉出一截脖子。
5. 对位：每帧按 `kennen_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底落在脚底线上；检查脚底线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/kennen_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/kennen_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/kennen_head.png`、`_1x.png` | 要贴进每一帧的头（兜帽、耳朵、脸、眼睛、面罩，不含手里剑） | 贴头 |
| `design/kennen_palette.png` | 造型图的全部 21 色（暗到亮） | 色板 |
| `kennen_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/kennen_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂和手里剑的动作 |
| `guide/kennen_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `kennen_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/kennen_picture.png` | 造型来源的原画 A（长相参考；比例以定稿造型为准） | 需要时参考 |
| `style/tfm2_style_ref.png`、`tfm2_style_ref_undead.png`、`4_tfm2_style.png` | 团战经理2 原版英雄（含忍者、雷电法师），放大 8 倍 | 像素大小和干净程度 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：待机姿态时和造型图一样高（手里剑顶到脚底 37 格），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 21 种颜色**，不加新颜色；明暗照定稿（兜帽的淡紫高光、金边的亮金跟着姿势移动），不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，**不要再画一圈黑、不要零散的黑格**。
- **手**：照造型图的爪子手套（深紫手套、手背钢片、爪子），手臂在宽袖子里、2–3 格粗；**不要 1 像素的黑细棍、不要飘着的手**。
- **背上的大手里剑**：四个尖角的金色手里剑，大小和样子照造型图，每帧都在背上（除了上面列出的拿在手里 / 甩出 / 掉落的帧）；拿在手里时整个手里剑完整、不变形。
- **头每帧都是造型图的头**（兜帽、两只耳朵、脸、眼睛、面罩逐格一样），只平移（死亡倒地时整个转）；蓝色 `#3FAEF8` 只用在眼睛上。
- **长袍**：每帧都有，跟着动作摆（冲刺时向后飘）；袍子下面能看到短腿和忍者鞋。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：每帧最低一行是脚底线（参考线图的红线就在它下面），手里剑、袍角都在它上面。只有死亡倒地的帧可以低于红线，最多 2 格。
- **移动循环**：每帧头相对站位点的横向位置不变；两条腿交叉迈步（前 4 帧一条腿在前，后 4 帧另一条），两条腿颜色一样；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 正面朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立**。**只画角色**：手里剑飞出去之后、闪电、电光、雷暴、闪电球、冲刺残影都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯品红 `#FF00FF`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/kennen_design.png`，第二张 `now/kennen_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `kennen_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, face, costume, hands, shuriken and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 front view facing right, the same big violet hood with its two pointed ears and gold zigzag trims, the face with the blue eyes, the brows and the violet mask, the violet robe with gold trims, the shoulder plate, the dark plum clawed gloves with their steel plates, the short legs and ninja shoes, the big gold four-pointed shuriken on his back, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the throw, the recovery), the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the arms, the body and the shuriken from it, but keep the FIRST image's proportions (a big hooded head, a small body, short legs, its shuriken); never draw him from the back or upside down.
The character: Kennen (a tiny yordle ninja: a big violet hood with two pointed ears and gold zigzag lightning trims, blue eyes and dark brows above a violet mask, a violet robe with gold trims, a dark plum shoulder plate with a gold lightning emblem, dark plum clawed gloves with steel plates, short legs in dark plum wraps, small ninja shoes, a big gold four-pointed shuriken strapped on his back).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (37 squares from the shuriken's top to the soles in the idle stance), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 21 colors of the FIRST image, no new colors: #0B060E #02112D #251324 #4C1819 #3A1452 #452348 #7A3E1C #8E3E30 #5E2386 #4A4E70 #6E3E75 #CB7420 #8A36B8 #C9714E #8A8FB0 #F8A23B #3FAEF8 #B657DE #EDA27A #FEDC80 #F5F5F5. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring, never stray black squares. Copy the FIRST image's shading - the hood's lavender highlights and the bright gold trims move with the pose; no dithering, no noise, no random specks added. The hands are the FIRST image's clawed gloves at the ends of arms 2-3 squares wide in wide sleeves - never 1-pixel black sticks or floating hands. The big shuriken stays on his back in every frame except where the animation says he holds, throws or drops it; held, it is whole and the same size as in the FIRST image; no loose pieces.
The head (the hood with both ears, the face with the eyes and brows, the mask, down to the hood's lower rim) is COPIED from the FIRST image in every frame, square for square, and only moved (in the death it turns with the body as he lies down); never redraw, squash, turn or tilt it, or it flickers when the frames play. It sits on the robe's collar - no neck. The blue #3FAEF8 appears ONLY in the eyes.
The robe is in every frame and moves with the pose (streaming back in the dash); his short legs and shoes show under it.
Feet line: in every cell his lowest square is on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down - not the shuriken, not the robe's hem - because the game draws the health bar there (only the frames of the death lying on the ground may dip at most 2 squares). His place across the cell follows the SECOND image (each frame's standing point is in kennen_cells.json). In the move loop his head keeps the same horizontal place relative to the standing point in every frame and the legs cross in turn.
3/4 front view like the FIRST image; every throw and dash goes to the RIGHT of the image; never his back, never upside down. Do not draw effects (the flying shuriken after it leaves his hand, lightning, sparks, the storm, the ball of lightning, afterimages) - only the character. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 80x72 squares (640x576 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both eyes visible, the blue #3FAEF8 only in the eyes, the shuriken on his back (or held / thrown / dropped where the animation says), real clawed gloves, the robe in every frame, no loose pieces, no stray black squares, nothing below the feet line, never his back or upside down, the frames in the same cells as the SECOND image.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `kennen_idle.png`（待机） | 6 × 180 | — | 3 列 × 2 行，1920×1152 | 第 59 行 | **已做好，不用画** |
| `kennen_run.png`（移动（小步忍者跑，双手后摆）） | 8 × 100 | — | 4 列 × 2 行，2560×1152 | 第 59 行 | `MOVE, 8 frames, one seamless loop (8 x 100 ms, League's run): a quick little ninja run - his body leans forward (at most about 25 degrees from upright, less than the SECOND image), both arms swept back behind him with the claws trailing, the big shuriken staying on his back; short fast steps under the robe: in frames 1-4 one foot comes forward, in frames 5-8 the other, the knees passing in frames 2-3 and 6-7 (the legs CROSS - never the same stance in all frames), both legs the same dark plum; the body bobs 1 square down and up over each half; his head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `kennen_attack.png`（普攻（从背上取下大手里剑甩出去）） | 6 帧：60 60 60 70 70 80 | 第 4 帧（tick 11） | 3 列 × 2 行，1920×1152 | 第 59 行 | `BASIC ATTACK, 6 frames (League's attack1: he pulls the big shuriken off his back and hurls it): 1 his near hand reaches up behind his hood toward the shuriken; 2 he lifts the shuriken off his back, the star now above and behind his head in his hand; 3 he swings it over his head, the star above his head and a little forward; 4 THE THROW (it leaves his hand here): his arm snaps forward and down to the right, the star at his fingertips in front of him at chest height, his body leaning forward; 5 the follow-through, crouched, both claws forward - the shuriken is gone from his back (it is flying); 6 back to the idle stance with the shuriken on his back again. The flying shuriken is an effect - do not draw it after frame 4.` |
| `kennen_skill.png`（Q 千鸟（近侧手甩出手里剑）） | 6 帧：50 60 70 80 90 100 | 第 4 帧（tick 11） | 3 列 × 2 行，1920×1152 | 第 59 行 | `THUNDERING SHURIKEN (Q: he flings a charged shuriken from his near hand), 6 frames (League's spell1): 1 the idle stance, the near hand lifting; 2 he raises the near hand beside his hood, crouching a little; 3 the wind-up: his body twists back, the near hand cocked behind his ear, the far claw forward; 4 THE THROW (the shuriken leaves his hand here): he snaps the near arm straight forward to the right at shoulder height, leaning forward, the far arm back; 5 the follow-through, the arm still out; 6 back to the idle stance. The big shuriken stays on his back in every frame; the thrown shuriken and its lightning are effects - do not draw them.` |
| `kennen_skill2.png`（E 雷铠（压低身子疾冲，闪电球是特效）） | 4 × 75 | — | 4 列 × 1 行，2560×576 | 第 59 行 | `LIGHTNING RUSH (E: he rushes forward as a bolt of lightning), 4 frames, one loop (4 x 75 ms): a very low, fast ninja dash - his body leaning forward about 30 degrees, both arms swept straight back behind him, the claws open, the legs in a long low stride (frames 1-2 one leg forward, frames 3-4 the other), the robe streaming back, the big shuriken on his back; the head (the FIRST image's, upright) leads. The ball of lightning around him is an effect drawn separately - do not draw sparks, glow or a ball.` |
| `kennen_w.png`（W 电刃（举起手里剑，然后蹲下张开双臂放电）） | 5 帧：50 50 60 60 60 | 第 3 帧（tick 6） | 3 列 × 2 行，1920×1152，最后 1 格空 | 第 59 行 | `ELECTRICAL SURGE (W: lightning bursts out of him), 5 frames (League's spell2): 1 he reaches back and raises the big shuriken high above his head in his near hand; 2 holding it high, crouching a little; 3 THE SURGE (the lightning bursts out here): he drops into a wide crouch, both arms flung out to the sides, the shuriken held out low in front of him; 4 holding the wide crouch; 5 rising back toward the idle stance, the shuriken back on his back. The lightning is an effect - do not draw it.` |
| `kennen_ult.png`（R 万雷天牢引（跃起举手里剑，落地低旋）） | 6 帧：60 60 60 70 70 80 | — | 3 列 × 2 行，1920×1152 | 第 59 行 | `SLICING MAELSTROM (R: he calls down the storm), 6 frames (League's spell4): 1 he crouches to spring; 2 he leaps up (about 3 squares off the ground), holding the big shuriken overhead in both hands; 3 at the top of the leap, the shuriken raised high; 4 he lands in a crouch, the shuriken held out in front of him; 5 he spins low, crouched, one arm sweeping forward, the shuriken behind him; 6 back to the idle stance, the shuriken on his back. The storm and its lightning are effects - do not draw them.` |
| `kennen_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，1280×576 | 第 59 行 | `HIT, 2 frames: 1 jolted back by a blow: his body and hood pushed back 1-2 squares (to the left), the arms flung out, the robe swaying; 2 recovering toward the idle stance.` |
| `kennen_dead.png`（死亡（被击飞向后倒地，手里剑掉在地上）） | 8 帧：100 100 110 110 120 150 300 500 | — | 4 列 × 2 行，2560×1152 | 第 59 行 | `DEATH, 8 frames (League's death: he is blown backward and lands on his back): 1 struck, he staggers back; 2 he is thrown backward, the arms up, the feet leaving the ground; 3 he tips over backward in the air - the body tilting back up to a quarter turn with the head turning WITH the body (never upside down); 4 falling on his back; 5 he hits the ground on his back and the big shuriken falls off his back onto the ground beside him; 6-8 he lies still on his back (the same pose), the hood to the left, the feet to the right, the shuriken lying flat on the ground by his feet. Frames 5-8 lie on the feet line and may reach 2 squares below it, nothing lower.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色（逐像素比对，没有新颜色），明暗照定稿，没有自己加的碎点；
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（逐格一样，只平移；死亡倒地时整个转），两只眼睛都在；
- [ ] 蓝色 `#3FAEF8` 只出现在眼睛上：头部以外 0 个像素；
- [ ] 背上的手里剑每帧都在（除了拿在手里 / 甩出 / 掉落的帧），大小和样子和造型图一样；手是爪子手套、不是黑细棍，没有飘着的碎块；
- [ ] 每帧都有长袍；脚底线以下没有任何像素（只有死亡倒地的帧可以低 1–2 格）；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立；出招都朝图的右边；
- [ ] 移动循环：头的横向位置每帧一样，两条腿交叉迈步、颜色一样，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点和 bbox 都写了；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `kennen_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、蓝色只在眼睛上、连通块、手臂粗细、手里剑是否完整、零散黑格、每帧面积和待机比），不在网格上的重新取样；头不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`kennen_cells.json` 用包里这份，`kennen_idle.png` 用包里已做好的那张。
- `import_native.py --hero kennen`：ORDER 待机一张图 + BOB 呼吸（缝选在袍子的直段），EYES = `#3FAEF8`（按眼睛对齐待机和移动），COMPLETE + CLEAN 补描边、清黑边，NECK 检查领口每帧在兜帽下沿同一行。
- 按出手帧核对技能数据的时机（普攻 tick 11、Q tick 11、W 放电 tick 6；E 冲刺 4 帧循环、R 起跳落地），量特效挂点（手的高度、背上手里剑的位置）和头像截取点，重跑模拟，做预览 GIF。
