# 乐芙兰：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是你画的**版本 B**，按游戏尺寸裁成 **43 格高**（只删整行整列，脸、眼睛没动；法杖拉直、补了右边的蝙蝠翼；两只金耳饰做成一样、和眼睛同高；描边清理干净）：`design/leblanc_design.png`（放大 8 倍，1024×1024；头冠尖到脚底 43 格，32 格宽，18 色；脚底在第 99 行，两脚中间在第 64 列）。**造型图就是标准**：靛蓝头发、金色头冠和尖角、两只金色尖耳饰、白皙的脸、琥珀色大眼睛（近侧眼 3 格宽、远侧眼 2 格宽）、金泪痕、深紫红的小嘴、金领甲、午夜蓝和深红的长裙、身后的领翼和披风、远侧手里的法杖（金色螺旋杖身、红水晶、两只深蓝蝙蝠翼），颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`leblanc_idle.png`，每帧就是造型图，站在待机的站位点上），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 8 张动作图按下面的表画。**大招不用画**（故技重施用被重放的那个技能自己的动作）。
> - 帧数、每帧时长、出手帧和站位照 `now/leblanc_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂和法杖的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **三处和参考图不一样，以造型图为准**：① **参考图里没有披风**（英雄联盟的披风是特效材质，渲染不出来，我们把它藏了）：我们每帧都画造型图的领翼和披风，跟着动作飘；② 参考图是英雄联盟的比例（头小、身子细长、法杖很长），我们**照造型图的比例**：大头、Q 版身材、法杖是造型图里的长度和样子；③ 头是贴上去的（见下），英雄联盟里她会扭头、低头，我们**头每帧不变形、不旋转、始终是造型图的 3/4 正面**（死亡躺下时整个头跟着身体转），**不画背影**。
> - 出招方向：**挥杖、刺、甩锁链、冲刺都朝图的右边**（游戏里朝左时会整张镜像）。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox）和 `generation_prompts.json`，最好打成一个 zip（`leblanc_strips_pack_done.zip`，放在 outputs 里）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/leblanc_palette.png`，或直接读 `design/leblanc_design_1x.png`）。**先把眼睛专用的暗红 `#7A0012` 从色板里去掉**（吸附时会跑到裙子、水晶的暗红上），它只随第 4 步贴的头回来。
4. **贴头**：把造型图的头（`design/leblanc_head_1x.png` 里不透明的格子：头冠和尖角、头发、脸、两只眼睛、两只金耳饰，到下巴的描边为止；在 128×128 画布上的范围 x 54–71、y 57–75，**按图里的形状贴，不是整个方框**——右边的法杖不属于头）原样贴进每一帧头的位置（只平移；死亡躺下的帧整个头跟着转）。这样每帧的脸都和造型图一模一样。头下面接领甲和肩膀，不要拉出一截脖子。
5. 对位：每帧按 `leblanc_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底落在脚底线上；检查脚底线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/leblanc_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/leblanc_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/leblanc_head.png`、`_1x.png` | 要贴进每一帧的头（头冠、头发、脸、眼睛、耳饰，不含法杖和领甲） | 贴头 |
| `design/leblanc_palette.png` | 造型图的全部 18 色（暗到亮） | 色板 |
| `leblanc_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/leblanc_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂和法杖的动作 |
| `guide/leblanc_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `leblanc_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/leblanc_picture.png` | 造型来源的原画 A（长相参考；比例以定稿造型为准） | 需要时参考 |
| `style/tfm2_style_ref.png`、`tfm2_style_ref_undead.png`、`tfm2_style_mages.png` | 团战经理2 原版英雄（含 5 位女法师），放大 8 倍 | 像素大小和干净程度 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：待机姿态时和造型图一样高（头冠尖到脚底 43 格），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 18 种颜色**，不加新颜色；明暗照定稿（头发的蓝色高光、金饰的亮金跟着姿势移动），不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，**不要再画一圈黑、不要零散的黑格**（用户特别要求黑边干净）。
- **手要像手**：手臂是 2–3 格粗的紫黑长手套（加描边），手腕一格金手镯，手是小而圆的手套，握着法杖；**不要 1 像素的黑细棍、不要飘着的手**。
- **法杖每帧都在她远侧手里**（死亡倒下时掉在地上）：杖身是 1 格金色、两边描边的**笔直**线（不能歪、不能一截截错开），上面是造型图的红水晶和两只深蓝蝙蝠翼，长度和造型图一样；法杖跟着手臂动，横着、斜着都要是直线。
- **头每帧都是造型图的头**（头冠、头发、脸、两只眼睛、两只耳饰逐格一样），只平移（死亡躺下时整个转）；暗红 `#7A0012` 只用在近侧眼的瞳孔上。
- **披风和长裙**：每帧都有，跟着动作飘（冲刺时向后飘、闪回时先裹住身体再展开）；裙摆下面能看到脚和高跟鞋。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：每帧最低一行是脚底线（参考线图的红线就在它下面），法杖尖、裙摆、披风都在它上面。只有死亡躺倒的帧可以低于红线，最多 2 格。
- **移动循环**：每帧头相对站位点的横向位置不变；两条腿交叉迈步（前 4 帧一条腿在前，后 4 帧另一条），两条腿颜色一样；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 正面朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立**。**只画角色**：法球、魔印、锁链、冲刺的残影、落地爆炸、闪回的光、幻像都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯品红 `#FF00FF`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/leblanc_design.png`，第二张 `now/leblanc_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `leblanc_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, face, costume, staff and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 front view facing right, the same big head with the dark indigo-blue hair, the gold diadem with its tall spike, the two pointed gold ear-cuffs at eye height, the pale face with the big amber eyes, the gold tear marks and the small dark plum mouth, the gold collar, the long midnight-blue and crimson gown, the collar wings and the cape behind her, the long plum-black gloves with gold bracelets, the staff in her far hand (a straight gold shaft, a red crystal on top, two navy bat wings), the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the cast, the recovery), the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the arms, the body and the staff from it, but keep the FIRST image's proportions (big head, chibi body, its staff); the 3D model is shown WITHOUT its cape, so draw the FIRST image's collar wings and cape in every frame; never draw her from the back or upside down.
The character: LeBlanc (a smug sorceress: dark indigo-blue hair with blue highlights, a gold diadem with a tall spike, pointed gold ear-cuffs, pale skin, big amber eyes, gold tear marks, a small dark plum mouth; a big gold collar; a long midnight-blue gown with crimson lining and gold trims; tall collar wings and a cape behind her; long plum-black gloves with gold bracelets; a tall staff with a straight gold shaft, a red crystal on top and two navy bat wings below it).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (43 squares from the tip of the diadem to the soles in the idle stance), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 18 colors of the FIRST image, no new colors: #060212 #2B010E #130F31 #390C20 #1C1948 #7A0012 #7F0015 #690B36 #AA011B #C90D33 #2C40A3 #B8662B #DE8D36 #F4AA45 #F9B954 #FCC967 #FDE59B #FEDECD. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring, never stray black squares. Copy the FIRST image's shading - the hair's blue highlights and the bright gold move with the pose; no dithering, no noise, no random specks added. Arms are gloves 2-3 squares wide with the outline and a gold bracelet, the hands small rounded gloves - never 1-pixel black sticks or floating hands; the staff stays in her far hand, its shaft a STRAIGHT 1-square gold line between outline squares (never zig-zagging), its crystal and wings as in the FIRST image; no loose pieces.
The head (the diadem with its spike, the hair, the face with both eyes, the two gold ear-cuffs, down to the chin's outline) is COPIED from the FIRST image in every frame, square for square, and only moved (in the death it turns with the body as she lies down); never redraw, squash, turn or tilt it, or it flickers when the frames play. It sits on the gold collar - no neck. The dark red #7A0012 appears ONLY in the near eye's pupil.
The gown and the cape are in every frame and move with the pose (streaming back in the dash, wrapped round her and opening again in the return); her feet and heels show under the hem.
Feet line: in every cell her lowest square is on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down - not the staff's tip, not the hem - because the game draws the health bar there (only the frames of the death lying on the ground may dip at most 2 squares). Her place across the cell follows the SECOND image (each frame's standing point is in leblanc_cells.json). In the move loop her head keeps the same horizontal place relative to the standing point in every frame and the legs cross in turn.
3/4 front view like the FIRST image; every swing, thrust, throw and dash goes to the RIGHT of the image; never her back, never upside down. Do not draw effects (the magic orb, the sigil, the chain, the dash's afterimages, the blast, the flash of the return, the mirror image) - only the character. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 96x80 squares (768x640 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both eyes visible and level, the dark red #7A0012 only in the near eye, the staff straight and in her far hand in every frame (until the death drops it), hands real gloves, the gown and the cape in every frame, no loose pieces, no stray black squares, nothing below the feet line, never her back or upside down, the frames in the same cells as the SECOND image.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `leblanc_idle.png`（待机） | 6 × 180 | — | 3 列 × 2 行，2304×1280 | 第 67 行 | **已做好，不用画** |
| `leblanc_run.png`（移动） | 8 × 142 | — | 4 列 × 2 行，3072×1280 | 第 67 行 | `MOVE, 8 frames, one seamless loop (8 x 142 ms, League's run): she runs forward to the right leaning a little forward, the staff held low and almost level in her far hand at hip height, its crystal pointing ahead to the right, the near arm bent and swinging; the gown and the cape stream back behind her and sway; her legs stride under the gown (the near leg showing through the slit): in frames 1-4 one foot comes forward, in frames 5-8 the other, the knees passing in frames 2-3 and 6-7; the body bobs 1 square down and up over each half; her head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `leblanc_attack.png`（普攻（转杖前刺，水晶放出法球）） | 6 帧：50 50 60 70 80 90 | 第 4 帧（tick 10） | 3 列 × 2 行，2304×1280 | 第 67 行 | `BASIC ATTACK, 6 frames (League's attack1: she twirls the staff over her head and thrusts it forward, the magic orb leaving the crystal): 1 she lifts the staff, the crystal rising above her head; 2 she raises it high overhead, upright, rising on her toes with one knee lifted; 3 she swings it over: the staff now slants across behind her head, the crystal high behind her to the left, the shaft's end pointing down ahead to the right, her body twisting forward; 4 THE THRUST (the orb leaves the crystal here): she lunges forward, the far arm stretched out, the staff level at chest height pointing straight ahead to the right with the crystal in front, the near arm back; 5 holding the thrust; 6 back to the idle stance, the staff upright again. The orb and its glow are effects - do not draw them.` |
| `leblanc_skill.png`（Q 恶意魔印（前挥法杖弹出魔印）） | 5 帧：50 60 70 80 100 | 第 3 帧（tick 7） | 3 列 × 2 行，2304×1280，最后 1 格空 | 第 67 行 | `SIGIL OF MALICE (she flicks the sigil at an enemy), 5 frames (League's spell1): 1 the idle stance, the near hand lifting; 2 she leans forward and flicks the staff: it tilts forward to the right, the crystal ahead of her at head height, the near arm swinging back behind her, the gown swirling; 3 THE CAST (the sigil leaves the crystal here): the flick at its furthest, the staff tilted furthest toward the target; 4 still leaning, the staff coming back up; 5 back to the idle stance. The sigil is an effect - do not draw it.` |
| `leblanc_skill2.png`（W 魔影迷踪：冲刺） | 5 × 60 | — | 3 列 × 2 行，2304×1280，最后 1 格空 | 第 67 行 | `DISTORTION (she dashes forward in a flash), 5 frames (League's spell2, played while she flies to the target): 1 she dives forward to the right, the body leaning far forward (at most 30 degrees from upright - the references lay her flat in this frame, do NOT copy that), the staff trailing back to the left, the gown and the cape streaming back; 2 still diving, the staff swinging down in front of her; 3 she lands in a long stride, the front foot forward to the right, the back leg stretched behind, the near arm thrown back, the staff upright in her far hand; 4-5 holding the landing stride, rising a little (the blast round her is an effect). The head stays the FIRST image's head (upright, both eyes visible) and only moves with the body; never her back.` |
| `leblanc_skill2_back.png`（W 魔影迷踪：闪回原处（裹着披风蹲起）） | 5 × 80 | — | 3 列 × 2 行，2304×1280，最后 1 格空 | 第 67 行 | `DISTORTION'S RETURN (she blinks back to where she started: she appears there curled up under her cape and springs up), 5 frames (League's spell2_recast): 1 she kneels low, curled up under her cape like a low mound: the cape wrapped round her body, only her head (the FIRST image's head, upright, moved down) and the staff's crystal showing; 2 still crouched low, the cape spread along the ground; 3 she starts to rise from the crouch, leaning forward, the staff coming out ahead of her, its crystal low at the right; 4 she springs up, the staff held level and pointing forward to the right; 5 standing, the staff pointing up to the right, almost back in the idle stance. The flash where she appears is an effect - do not draw it.` |
| `leblanc_e.png`（E 幻影锁链（法杖前指，锁链从水晶射出）） | 6 帧：60 60 70 90 100 120 | 第 4 帧（tick 11） | 3 列 × 2 行，2304×1280 | 第 67 行 | `ETHEREAL CHAINS (she points the staff and the chain shoots from its crystal), 6 frames (League's spell3): 1 the idle stance, turning a little; 2 she draws the staff down across her body, its crystal near her chest and the shaft pointing down to the right; 3 she gathers, crouching a little, the staff pulled in close; 4 THE THROW (the chain leaves the crystal here): she leans far forward, the far arm stretched out to the right holding the staff just below its head, the staff level at shoulder height with the crystal pointing at the target and the shaft running back behind her to the left, the near arm back, the gown and the cape trailing; 5 holding that pose; 6 back to the idle stance, the staff upright. The chain is an effect - do not draw it.` |
| `leblanc_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，1536×640 | 第 67 行 | `HIT, 2 frames: 1 jolted back by a blow: her body and head pushed back 1-2 squares (to the left), the staff tilting back, the gown swaying; 2 recovering toward the idle stance.` |
| `leblanc_dead.png`（死亡（松开法杖，向后倒地）） | 8 帧：100 100 100 120 120 150 200 400 | — | 4 列 × 2 行，3072×1280 | 第 67 行 | `DEATH, 8 frames (League's death: she lets go of the staff and falls on her back): 1 struck, she lets go of the staff, which stands on its own just to her right; 2 she doubles over and staggers back, the near arm reaching out; 3 she arches back, her feet leaving the ground; 4 she falls back to the left, almost level; 5 she lies on her back on the ground, the head to the left, the legs to the right, the gown and the cape spread out (the head turns with the body); the staff still stands to her right; 6-8 she lies still (the same pose) and the staff has fallen flat onto the ground to her right. Frames 5-8 lie on the feet line and may reach 2 squares below it, nothing lower.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色（逐像素比对，没有新颜色），明暗照定稿，没有自己加的碎点；
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（逐格一样，只平移；死亡躺下时整个转），两只眼睛都在、同一高度，两只耳饰一样；
- [ ] 暗红 `#7A0012` 只出现在近侧眼的瞳孔上：头部以外 0 个像素；
- [ ] 法杖每帧都在远侧手里（死亡倒下时掉在地上），杖身是笔直的 1 格金线，水晶和两只蝙蝠翼完整；手是手套、不是黑细棍，没有飘着的碎块；
- [ ] 每帧都有领翼、披风和长裙；脚底线以下没有任何像素（只有死亡躺倒的帧可以低 1–2 格）；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立；出招都朝图的右边；
- [ ] 移动循环：头的横向位置每帧一样，两条腿交叉迈步、颜色一样，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点和 bbox 都写了；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `leblanc_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、暗红只在眼睛上、连通块、手臂粗细、法杖是否笔直、零散黑格、每帧面积和待机比），不在网格上的重新取样；头不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`leblanc_cells.json` 用包里这份，`leblanc_idle.png` 用包里已做好的那张；`ult` 用 Q 的帧。
- `import_native.py --hero leblanc`：ORDER 待机一张图 + BOB 呼吸（缝选在裙子的直段），EYES = `#7A0012`（按眼睛对齐待机和移动），COMPLETE + CLEAN 补描边、清黑边，NECK 检查领甲每帧在下巴下面同一行。
- 按出手帧核对技能数据的时机（普攻 tick 10、Q tick 7、E tick 11；W 冲刺和闪回的动作长度），量特效挂点（法杖水晶的高度）和头像截取点，重跑模拟，做预览 GIF。
