# 魔腾：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是你画的**版本 B**（两只 2×2 白眼），按用户要求削到 **40 格高**（只删整行整列，没动脸）：`design/nocturne_design.png`（放大 8 倍，1024×1024；头冠尖到尾巴尖 40 格，33 格宽，20 色；尾巴尖在第 99 行、第 64 列）。**造型图就是标准**：正面的姿态、向后扫的头冠、两只纯白方眼、深靛蓝暗影身体和亮蓝描边、两块紫银大肩甲（蓝色圆环符文、钢刺）、钢护手、两条前臂外侧的红银弯刃、红色腰布和银色圆环纹章、烟雾尾巴、颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`nocturne_idle.png`，每帧就是造型图，站在待机的站位点上），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 9 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/nocturne_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂和刀刃的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **三处和参考图不一样，以造型图为准**：① **英雄联盟的模型没有下半身**（他的烟雾尾巴是特效，渲染图里看不到，参考图里人悬在空中）：我们每帧都画造型图的烟雾尾巴，尾巴尖落在脚底线上（飞扑的几帧可以离地）；② 参考图是英雄联盟的比例（头小、刀长、身子宽），我们**照造型图的比例**：大头、紧凑的身体、刀是造型图里的长度；③ 头是贴上去的（见下），英雄联盟里他会扭身、低头、背对镜头，我们**头每帧不变形、不旋转、始终正面**（死亡沉进黑烟时头跟着往下沉，最后一帧没有头），**不画背影、不画倒立**。
> - 出招方向：造型是正面的，**攻击、掷刃、伸手、飞扑都朝图的右边**（游戏里朝左时会整张镜像）。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。附 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox）和 `generation_prompts.json`，最好打成一个 zip（`nocturne_strips_pack_done.zip`，放在 outputs 里）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/nocturne_palette.png`，或直接读 `design/nocturne_design_1x.png`）。**先把眼睛的纯白 `#FFFFFF` 从色板里去掉**（吸附时会跑到钢刺、刀刃的高光上），它只随第 4 步贴的头回来。
4. **贴头**：把造型图的头（`design/nocturne_head_1x.png` 里不透明的格子：头冠、头骨、两只白眼，到下巴的描边为止；在 128×128 画布上的范围 x 56–69、y 60–77，**按图里的形状贴，不是整个方框**——两边的肩甲不属于头）原样贴进每一帧头的位置（只平移）。这样每帧的脸都和造型图一模一样。头下面接两块肩甲之间的身体，不要拉出脖子。
5. 对位：每帧按 `nocturne_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），尾巴尖落在脚底线上；检查脚底线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/nocturne_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线（尾巴尖）第 99 行 | 每张动作图的第一张附图 |
| `design/nocturne_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/nocturne_head.png`、`_1x.png` | 要贴进每一帧的头（头冠、头骨、两只白眼，不含肩甲和身体） | 贴头 |
| `design/nocturne_palette.png` | 造型图的全部 20 色（暗到亮） | 色板 |
| `nocturne_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/nocturne_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂和刀刃的动作 |
| `guide/nocturne_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `nocturne_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/nocturne_picture.png` | 造型来源的原画 A（长相参考；比例和正面姿态以定稿造型为准） | 需要时参考 |
| `style/tfm2_style_ref.png`、`tfm2_style_ref_undead.png`、`tfm2_style_dark.png` | 团战经理2 原版英雄（含暗色、幽灵类），放大 8 倍 | 像素大小和干净程度 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：待机姿态时和造型图一样高（头冠尖到尾巴尖 40 格），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 20 种颜色**，不加新颜色；明暗照定稿（亮蓝描边、钢的高光跟着姿势移动），不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，不要再画一圈黑。
- **身体粗细照定稿**：手臂（护手）至少 3 格宽（加描边），拳头和造型图一样大；两把弯刃长在前臂外侧、和造型图一样大，跟着前臂动；各部分之间有描边隔开，但头、身体、肩甲、手臂、刀刃、腰布、尾巴必须连成一个整体，不能有飘在空中的碎块（死亡最后落在烟里的刀除外）。
- **头每帧都是造型图的头**（头冠、头骨、两只白眼逐格一样），只平移（死亡时跟着身体往下沉）；纯白 `#FFFFFF` 只用在眼睛上。
- **烟雾尾巴每帧都有**：从腰布下面伸出，越往下越细，最低一格落在脚底线上（飞扑的帧可以离地、向后飘）；可以随动作摆动、卷曲，但不能断成碎块。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：每帧最低一行是脚底线（参考线图的红线就在它下面），刀尖也在它上面。只有死亡最后沉成一滩烟的帧可以低于红线，最多 2 格。
- **移动循环**：每帧头相对站位点的横向位置不变；两只手臂轮流前后摆；上下起伏最多 1 格；尾巴摆动；首尾能无缝接上。
- 正面（和造型图一样），出招朝图的右边，**不画背影、不画倒立**。**只画角色**：飞出去的暗影之刃、影径、梦魇灵链、黑暗庇护、横扫刀光、黑雾、落地冲击都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯品红 `#FF00FF`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/nocturne_design.png`，第二张 `now/nocturne_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `nocturne_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, face, armour, blades and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same front-on stance, the same big head with the swept-back crest and the two square white eyes, the same dark navy-indigo shadow body with its light blue rim highlights, the two big purple-and-silver pauldrons with their blue ring runes and steel spikes, the steel gauntlets, the two crimson-and-silver curved blades on the outside of the forearms, the crimson tabard with the silver ring emblem, the smoke tail, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the hit, the recovery), the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the arms and the blades from it, but keep the FIRST image's proportions (big head, compact body, its blade size); the 3D model has NO lower body (his smoke tail is an effect there), so draw the FIRST image's smoke tail in every frame; never draw him from the back or upside down.
The character: Nocturne (a floating shadow demon in spiked armour: a big bare dark-navy head with a tall crest sweeping back and two glowing square pure-white eyes, no mouth; two big rounded purple-and-silver pauldrons with blue ring runes and steel spikes; steel gauntlets and big navy fists; a curved crimson blade with silver edges on the outside of each forearm; a crimson tabard with a silver ring emblem; no legs - a dark navy smoke tail that narrows down to a point).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (40 squares from the tip of the crest to the tip of the tail in the idle stance), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 20 colors of the FIRST image, no new colors: #080611 #101029 #171C43 #560F27 #342039 #202952 #33323E #9B1032 #583262 #30437B #284C85 #555160 #D3143E #794786 #465DAC #777680 #888BA2 #A1A3AA #D3D7DC #FFFFFF. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring. Copy the FIRST image's shading - its light blue rims and steel highlights move with the pose; no dithering, no noise, no random specks added. Arms (gauntlets) at least 3 squares wide with the outline, the fists as big as in the FIRST image, the blades attached to the forearms and as big as in the FIRST image; no loose pieces.
The head (the crest, the skull with the two white eyes, down to the chin's outline) is COPIED from the FIRST image in every frame, square for square, and only moved (in the death it sinks with the body into the smoke); never redraw, squash, turn or tilt it, or it flickers when the frames play. It sits between the pauldrons - no neck. Both eyes are the FIRST image's 2x2 white squares on the same rows; pure white #FFFFFF appears ONLY in the eyes.
The smoke tail is in every frame: it comes out under the tabard, narrows and ends in a 1-2 square point; it may sway and curl with the motion but never breaks into pieces.
Feet line: in every cell the tail's lowest square is on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]) - in the flying frames of the dive it may lift off it; NOTHING from pixel [R*8+8] down - not a blade tip - because the game draws the health bar there (only the last frames of the death, a pool of smoke, may dip at most 2 squares). His place across the cell follows the SECOND image (each frame's standing point is in nocturne_cells.json). In the move loop his head keeps the same horizontal place relative to the standing point in every frame.
Front view like the FIRST image; every strike, throw, reach and dive goes to the RIGHT of the image; never his back, never upside down. Do not draw effects (the thrown shadow blade, the dusk trail, the tether chain, the shroud, slash trails, dark mist, impact bursts) - only the character. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 120x104 squares (960x832 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both white eyes visible and level, white only in the eyes, both blades on the forearms in every frame (until the death drops them), arms at least 3 squares wide, the smoke tail in every frame, no loose pieces, nothing below the feet line, never his back or upside down, the frames in the same cells as the SECOND image.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `nocturne_idle.png`（待机） | 6 × 180 | — | 3 列 × 2 行，2880×1664 | 第 88 行 | **已做好，不用画** |
| `nocturne_run.png`（移动（浮空滑行）） | 8 × 100 | — | 4 列 × 2 行，3840×1664 | 第 88 行 | `MOVE, 8 frames, one seamless loop (8 x 100 ms): he glides forward to the right, floating - he has NO legs: the smoke tail streams back and down to the left and waves from frame to frame (curling a little more in some frames), its lowest square always on the feet line; the body leans a little forward (to the right) and bobs 1 square down and up over the loop (frames 1-4 one bob, 5-8 the next); the arms swing gently in turn - in frames 1-4 the right arm (image right) is a little forward and the left arm back, in frames 5-8 the other way - the blades following the forearms, pointing down and back; his head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `nocturne_attack.png`（普攻） | 6 帧：60 60 60 70 80 90 | 第 3 帧（tick 7） | 3 列 × 2 行，2880×1664 | 第 88 行 | `BASIC ATTACK, 6 frames (League's attack1, a downward blade slash): 1 he draws the right arm (image right) up and back, the blade lifting; 2 the wind-up: the right blade raised high above his right shoulder, the body leaning back a little; 3 THE SLASH (the hit lands here): he whips the right arm down and forward to the right, the blade cutting down in front of him, the body leaning into it; 4 the follow-through: the right blade low in front, the left arm drawn back; 5 recovering, the arms coming back to his sides; 6 back to the idle stance. Slash trails are effects - do not draw them.` |
| `nocturne_attack_p.png`（被动暗影之刃，横扫普攻） | 6 帧：60 60 70 80 80 90 | 第 3 帧（tick 7） | 3 列 × 2 行，2880×1664 | 第 88 行 | `UMBRA BLADES (the empowered attack: a cleave all round him), 6 frames (League's crit): 1 he hunches a little and cocks both arms in front of his chest, the blades crossed; 2 both arms drawn back, the blades raised behind his shoulders; 3 THE CLEAVE (the hit lands here): both arms flung wide open to the sides at shoulder height, both blades sweeping out level like wings - the widest frame; 4 the arms still wide, the blades swept further back; 5 the arms coming down and in; 6 back to the idle stance. The swirl of the cleave is an effect - do not draw it.` |
| `nocturne_skill.png`（Q 梦魇之径，掷刃） | 5 帧：60 70 70 80 100 | 第 3 帧（tick 8） | 3 列 × 2 行，2880×1664，最后 1 格空 | 第 88 行 | `DUSKBRINGER (he hurls a shadow blade), 5 frames (League's spell1): 1 he draws the right arm (image right) back behind him; 2 the wind-up: the right arm far back, the left arm forward for balance, leaning back; 3 THE THROW (the shadow blade leaves his right hand here and flies to the right - the flying blade is an effect, his own forearm blades stay on his arms): the right arm whipped forward and straight out to the right at shoulder height; 4 the follow-through, the right arm low in front, leaning forward; 5 back to the idle stance.` |
| `nocturne_skill2.png`（E 无言恐惧（并入 W）） | 5 帧：60 70 70 80 100 | 第 3 帧（tick 8） | 3 列 × 2 行，2880×1664，最后 1 格空 | 第 88 行 | `UNSPEAKABLE HORROR (he reaches out and plants a nightmare tether in the enemy), 5 frames (League's spell3): 1 he rises a little and raises both fists in front of his chest, menacing; 2 both arms spread out to the sides, fists up, the blades hanging from the forearms; 3 THE GRIP (the tether shoots out here - an effect): the right arm (image right) thrust straight forward to the right with the hand open like a claw, the left arm held back; 4 still reaching, the clawed hand pulling back a little; 5 back to the idle stance. The dark shroud round him is an effect - do not draw it.` |
| `nocturne_ult.png`（R 鬼影重重：起身、飞扑） | 6 帧：60 70 155 155 155 155 | 第 3 帧（tick 8） | 3 列 × 2 行，2880×1664 | 第 88 行 | `PARANOIA (he rises, then flies at a far enemy champion), 6 frames (League's spell4): 1 he gathers, hunching low, both blades drawn back; 2 he rears up and spreads both arms wide and high, the blades raised above his shoulders, the tail coiled under him; 3 THE LAUNCH (he takes off here): he throws himself forward to the right - the body leaning far forward (at most 30 degrees), both arms swept back behind him with the blades trailing, the tail streaming back to the left and up off the ground; 4-6 the flight: the same diving pose, the tail and the blades rippling a little from frame to frame (the game holds these frames while he flies). The head stays the FIRST image's head (upright, both eyes visible) and only moves with the body; never his back.` |
| `nocturne_ult_hit.png`（R 落地斩击） | 4 帧：80 80 80 100 | 第 1 帧（tick 0） | 4 列 × 1 行，3840×832 | 第 88 行 | `PARANOIA'S STRIKE (he lands on the enemy), 4 frames (League's attack3): 1 THE STRIKE (the hit lands here, on the first frame): both blades crash down in front of him, crossing, the body low and leaning forward; 2 the blades driven down low, the arms crossed in front; 3 he pulls the blades back up and apart; 4 back to the idle stance.` |
| `nocturne_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，1920×832 | 第 88 行 | `HIT, 2 frames: 1 jolted back by a blow: his body and head pushed back 1-2 squares (to the left), the arms flung out a little, the tail bending; 2 recovering toward the idle stance.` |
| `nocturne_dead.png`（死亡（化成黑烟）） | 8 帧：100 100 100 120 120 150 200 400 | — | 4 列 × 2 行，3840×1664 | 第 88 行 | `DEATH, 8 frames (he dissolves into shadow): 1 struck, he rocks back, the arms flung out; 2 he rears up, both arms spread wide, the blades out; 3 he doubles over, the arms dropping; 4 he sinks lower, the smoke tail spreading on the ground; 5 his body sinks into a pool of dark smoke - the head, the pauldrons and the arms above it; 6 lower still, the blades lying on the ground at his sides; 7 only the pauldrons, the top of the head and the blade tips above the smoke pool; 8 a flat pool of dark navy-violet smoke on the ground with the two crimson blades lying in it, nothing else. Frames 5-8 lie on the feet line and may reach 2 squares below it, nothing lower.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色（逐像素比对，没有新颜色），明暗照定稿，没有自己加的碎点；
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（逐格一样，只平移；死亡时跟着下沉），两只白眼都在、同一高度；
- [ ] 纯白 `#FFFFFF` 只出现在眼睛上：头部范围以外 0 个像素；
- [ ] 两把刀每帧都长在前臂上（死亡最后落在烟里的除外），大小照造型图，不挡眼睛；手臂至少 3 格宽，没有飘着的碎块；
- [ ] 每帧都有烟雾尾巴，尾巴尖在脚底线上（飞扑的帧除外）；脚底线以下没有任何像素（只有死亡最后的烟可以低 1–2 格）；
- [ ] 没有背影、没有倒立；出招都朝图的右边；
- [ ] 移动循环：头的横向位置每帧一样，手臂轮流前后摆，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点和 bbox 都写了。

## Claude 导入时（给 Claude 看）

- 交回的 `nocturne_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、纯白只在眼睛上、连通块、手臂粗细、每帧面积和待机比），不在网格上的重新取样；眼睛不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`nocturne_cells.json` 用包里这份，`nocturne_idle.png` 用包里已做好的那张。
- `import_native.py --hero nocturne`：ORDER 待机一张图 + BOB 浮空呼吸（整个人连尾巴上下一格，只留尾巴尖），EYES = `#FFFFFF`（按眼睛对齐待机和移动），COMPLETE 补描边，头是贴的：NECK 检查肩甲每帧在下巴两边同一行。
- 按出手帧核对技能数据的时机（普攻 tick 7、横扫 tick 7、Q tick 8、E tick 8、R 起飞 tick 8、R 落地 tick 0），量特效挂点（手和刀的高度）和头像截取点，重跑模拟，做预览 GIF。
