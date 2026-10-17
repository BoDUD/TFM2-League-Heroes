# 维迦：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选的是你按游戏尺寸画的 **B 版**（帽子 14 行）：`design/veigar_design.png`（放大 8 倍，1024×1024，脚底在 y=792–799；帽尖到脚底 40 格，37 格宽，23 色）。**造型图就是标准**：帽子、黑脸黄眼、长袍、铁手套、短法杖、颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`veigar_idle.png`，每帧就是造型图，站在待机的站位点上），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 7 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/veigar_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。**大招 R 用的是英雄联盟里 W 的跳起举杖**（用户选的），所以 `ult` 的参考是 W 的动作。
> - **两处和参考图不一样，以造型图为准**：① 法杖是造型图里的**短杖**（站着时杖头在帽檐高度），英雄联盟的法杖比帽子高很多，不要照参考图画长；② 英雄联盟 E 转圈时会露出背影，我们**永远朝右、不画背影**。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。附 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox）和 `generation_prompts.json`。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/veigar_palette.png`，或直接读 `design/veigar_design_1x.png`）。**先把两个眼睛颜色 `#FFD132`、`#FFF28A` 从色板里去掉**（它们和橙色水晶、亮银很近，一吸附就会跑到别处），它们只随第 4 步贴的头回来。
4. **贴头**：把造型图的头（`design/veigar_head_1x.png`：帽子、帽带、帽檐、黑脸和两只眼睛，不含法杖和铁手套；在 128×128 画布上的范围 x 50–73、y 60–77）原样贴进每一帧头的位置（只平移，身体倾斜时整体倾斜；死亡倒地的帧可以不贴）。这样每帧的帽子和脸都和造型图一模一样。受击第 1 帧把眼睛眯成一行（只留眼睛下面那一行）。
5. 对位：每帧按 `veigar_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底踩在脚底线上；检查脚底线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/veigar_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底） | 每张动作图的第一张附图 |
| `design/veigar_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/veigar_head.png`、`_1x.png` | 要贴进每一帧的头（帽子 + 黑脸黄眼，不含法杖、铁手套） | 贴头 |
| `design/veigar_palette.png` | 造型图的全部 23 色（暗到亮） | 色板 |
| `veigar_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/veigar_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：身体的动作 |
| `guide/veigar_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `veigar_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/veigar_picture.png` | 造型来源的原画 A（长相参考；比例以定稿造型为准） | 需要时参考 |
| `style/tfm2_style_ref*.png` | 团战经理2 原版英雄，放大 8 倍 | 像素大小和干净程度 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：站着时和造型图一样高（帽尖到脚底 40 格），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 23 种颜色**，不加新颜色；明暗照定稿（亮边、银色高光、褶跟着姿势移动），不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，不要再画一圈黑。
- **身体粗细照定稿**：手臂和铁手套至少 3 格宽（加描边），不能只有 1–2 格（在小尺寸下会像手脱离了身体）；长袍下摆宽、腿短；各部分之间有描边隔开，但身体、手臂、法杖、手套必须连成一个整体，不能有飘在空中的碎块。
- **头每帧都是造型图的头**（帽子、帽带、帽檐、黑脸、眼睛逐格一样），只平移或整体倾斜；帽尖永远向后（左）垂；两只眼睛一样大、同一行，`#FFD132` 和 `#FFF28A` 只用在眼睛上。
- **法杖在近侧的手（图里左边），大铁手套在远侧的手（右边）**，每帧都拿在手里，不能飘开，不能挡眼睛；法杖是造型图的**短杖**，不要画成参考图里那么长。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：每帧最低一行是脚底线（参考线图的红线就在它下面），法杖的下端也在它上面。只有死亡倒地的帧可以低于红线，最多 2 格。
- **移动循环**：每帧头相对站位点的横向位置不变；两条腿交替（前 4 帧一步、后 4 帧另一步，中间膝盖交错）；上下起伏最多 2 格；首尾能无缝接上。
- 3/4 正面朝右，**不画背影**、不画倒立（死亡最后倒地的帧除外）。**只画角色**：暗能量弹、牢笼、黑暗物质、爆发的光都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯品红 `#FF00FF`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/veigar_design.png`，第二张 `now/veigar_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `veigar_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, hat, face, staff, gauntlet and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same chibi proportions, the same hat, robe, belt, magenta cloth, silver spikes and boots, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the release, the recovery), the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the body from it, but keep the FIRST image's short staff (the THIRD image's staff is much longer) and never show his back (where the original spins, keep him facing right).
The character: Veigar (a tiny evil yordle wizard: a huge blue-violet pointed hat whose purple tip bends backward and droops, a silver studded hat band with a square buckle and a wide brim; under it a black face with two glowing yellow eyes and no mouth; a blue-violet robe with a wide flared skirt rimmed in silver spikes, a brown belt with a buckle, a magenta cloth at the hip, silver spiked shoulder guards; a short grey staff with a silver claw head round an orange crystal in his near hand; a huge silver spiked gauntlet on his far hand; short dark legs and silver spiked boots).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (40 squares from the top of the hat to the soles when standing), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 23 colors of the FIRST image, no new colors: #111020 #252637 #201660 #4F291F #581052 #3D3E50 #2D258B #474857 #A94708 #89502D #69239B #4034C1 #A51B8B #737586 #BD7C42 #F6810B #6558F3 #A744D3 #FFD132 #FFBE54 #B4B4BF #FFF28A #F5EFDF. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring. Copy the FIRST image's shading - its lit edges and silver highlights move with the pose; no dithering, no noise, no random specks added. Arms and the gauntlet at least 3 squares wide with the outline, joined to the body; no loose pieces.
The head (the hat with its band, buckle, brim and drooping purple tip, and the black face with the two eyes) is COPIED from the FIRST image in every frame, square for square, and only moved (or tilted as a whole where the body leans); never redraw it, or it flickers when the frames play. The staff is always in his NEAR hand (the left one in the image) and the huge spiked gauntlet on his FAR hand (the right one), as in the FIRST image - in EVERY frame, whatever the THIRD image shows. It is the FIRST image's SHORT staff: standing, its claw head is at the height of the hat's brim; never draw League's tall staff of the THIRD image, whose head rises far above the hat. The staff and the gauntlet move with his hands, never float free, and never cover the eyes. His face is the FIRST image's: a black face under the brim with two glowing yellow eyes, each an L of 3 squares (2 yellow #FFD132 and a bright core #FFF28A at the inner bottom), the same size, on the same rows, one black square apart; those two colours appear ONLY in the eyes.
Feet line: in every cell the lowest row of his feet is square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down - not the staff - because the game draws the health bar there (a fall may dip at most 2 squares). His place across the cell follows the SECOND image (each frame's standing point is in veigar_cells.json). In the move loop his head keeps the same horizontal place relative to the standing point in every frame and the legs alternate.
3/4 FRONT view facing right, never his back, never upside down (except a frame lying on the ground). Do not draw effects (bolts, the cage, dark matter, glows) - only the character. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 96x96 squares (768x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both eyes visible, level and the same size, the short staff in the near hand and the gauntlet on the far hand in every frame, arms at least 3 squares wide, no loose pieces, nothing below the feet line, never his back, the frames in the same cells as the SECOND image.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `veigar_idle.png` | 6 × 200 | — | 3 列 × 2 行，2304×1536 | 第 81 行 | **已做好，不用画** |
| `veigar_run.png` | 8 帧：104 104 104 104 104 104 104 105 | — | 4 列 × 2 行，3072×1536 | 第 81 行 | `MOVE, 8 frames, one seamless loop of League's run (0.83 s cycle, 8 x 104 ms, the SECOND and THIRD images): Veigar's springy, skipping little run - the body bobs up and down (at most 2 squares), the staff held upright in his near hand, the gauntlet swinging a little; the legs ALTERNATE as in the THIRD image (frames 1-4 one stride, 5-8 the other: the near leg forward in one half, the far leg in the other, the knees passing each other in between); his head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `veigar_attack.png` | 6 帧：60 60 70 80 90 100 | 第 4 帧（tick 12） | 3 列 × 2 行，2304×1536 | 第 81 行 | `BASIC ATTACK, 6 frames (League's attack1): 1 he lifts the staff; 2 raises it high; 3 swings it back over his shoulder; 4 the release (the dark bolt leaves here): he thrusts the staff forward to the right, the claw head pointing ahead; 5 held; 6 back toward the idle stance. The bolt is an effect - do not draw it.` |
| `veigar_skill.png` | 6 帧：60 70 70 80 90 110 | 第 4 帧（tick 12） | 3 列 × 2 行，2304×1536 | 第 81 行 | `BALEFUL STRIKE, 6 frames (League's attack2): 1 he crouches and pulls the staff back low; 2-3 drawn back, coiled, weight on the back foot; 4 the release (the bolt leaves here): he lunges and thrusts the staff straight forward to the right at chest height, the claw head pointing at the target; 5 held out; 6 back toward the idle stance. The bolt is an effect - do not draw it.` |
| `veigar_skill2.png` | 7 帧：60 60 70 80 90 90 100 | 第 4 帧（tick 12） | 3 列 × 2 行，2304×1536，最后 -1 格空 | 第 81 行 | `EVENT HORIZON, 6 frames (League's spell3, a twirl of the staff): 1 he lifts the staff; 2 raises it high to the right; 3 swings it round, crouching; 4 the release (the cage forms at the target here): the staff swept down and round; 5 the staff held out at arm's length behind him, the claw head low (as in the THIRD image - his body keeps facing right, never his back); 6 back toward the idle stance. The cage and the falling Dark Matter are effects - do not draw them.` |
| `veigar_ult.png` | 7 帧：60 60 70 90 90 90 100 | 第 4 帧（tick 12） | 4 列 × 2 行，3072×1536，最后 1 格空 | 第 81 行 | `PRIMORDIAL BURST, 7 frames (League's spell2 leap, the user's pick for the ult): 1 he crouches, gathering power; 2 crouched lower, the staff pulled in; 3 he springs up; 4 the release (the burst leaves the staff here): at the top of the jump, the staff raised high overhead, the gauntlet flung out; 5 landing; 6 crouched after the landing; 7 back toward the idle stance. The burst is an effect - do not draw it.` |
| `veigar_hit.png` | 2 × 120 | — | 2 列 × 1 行，1536×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow, the hat knocked askew a little, the eyes narrowed to their lower row; 2 recovering toward the idle stance.` |
| `veigar_dead.png` | 8 帧：100 100 110 110 120 130 150 500 | — | 4 列 × 2 行，3072×1536 | 第 81 行 | `DEATH, 8 frames, as in the THIRD image: 1 struck; 2 staggering; 3 crumpling; 4 sinking down; 5 collapsing; 6 falling; 7 on the ground; 8 lying in a heap on the ground line, the hat over him, the staff on the ground beside him. Frames 6-8 may reach 2 squares below the feet line, nothing lower.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色（逐像素比对，没有新颜色），明暗照定稿，没有自己加的碎点；
- [ ] 每一帧站着时和造型图一样高；头就是造型图的头（逐格一样，只平移），两只眼睛都在、一样大、同一高度；
- [ ] `#FFD132`、`#FFF28A` 只出现在眼睛上：头部范围以外 0 个像素；
- [ ] 法杖是短杖、在近侧的手，铁手套在远侧的手，每帧都在，不挡眼睛；手臂至少 3 格宽，没有飘着的碎块；
- [ ] 没有背影、没有倒立；脚底线以下没有任何像素（只有死亡帧可以低 1–2 格）；
- [ ] 移动循环：头的横向位置每帧一样，两条腿交替，上下起伏不超过 2 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点和 bbox 都写了。

## Claude 导入时（给 Claude 看）

- 交回的 `veigar_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、眼睛只在眼睛上、连通块、手臂粗细、每帧面积和待机比），不在网格上的重新取样；眼睛不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`veigar_cells.json` 用包里这份，`veigar_idle.png` 用包里已做好的那张。
- `import_native.py --hero veigar`：ORDER 待机一张图 + BOB 呼吸，EYES = `#FFD132`（按眼睛对齐待机和移动），COMPLETE 补描边。
- 按出手帧核对技能数据的时机（普攻、Q、E、R 都在第 4 帧，约 tick 12），重量特效挂点和头像截取点，重跑模拟，做预览 GIF。
