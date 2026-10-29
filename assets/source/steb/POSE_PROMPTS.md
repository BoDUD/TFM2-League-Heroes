# 斯特卜：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 斯特卜的造型用户已经定稿（`0_design.png` 是你第 0 步画的 A，按你自己的格子读回、定稿：3/4 朝右，**待机站姿，远处的手把一根警棍扛在肩上，近处的手握着另一根警棍朝下**；浅海绿皮肤、青绿色飞机头、尖尖的绿色鱼鳍耳、脸颊上的青色鳞点、浅青色眼睛、偏紫的嘴唇；蓝色执法官制服 + 金边高领 + 蓝金肩甲、浅色胸甲、胸前一排棕色药包和交叉皮背带、深棕腰带、灰紫长裤、墨绿手套和带金环的高筒靴；**背后一个很大的棕色皮背包**；**两根带侧把手的蓝钢警棍**（一头是带青色符文的黄铜头，另一头是银灰钢杆，中间木把手））。
> - 请你画 **12 个姿势**（10 个动作 + 2 帧倒地），**每个一张图**。待机、挨打我从定稿本身来做，不用画；**跑步在另一个包里**（`steb_run_pack.zip`，8 帧一整个周期、带交叉步）。
> - **每张都是同一个斯特卜**：样子、颜色、粗细、长短全照 `0_design.png`，**格子和它一样大：每格 9 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1176**），网格从画布左上角对齐。
> - **参考图（每个姿势一张 `*_ref.png`）是他在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，头已经放大到定稿的比例、摆在同一张画布、同一个格子上、同样的大小和位置——**身体的姿势照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（骨盆到脖子根），**橙线 = 右手、青线 = 左手**（第一个点是肩膀，**大圆点是手腕**），红线 / 蓝线 = 两条腿；**紫线 = 警棍**（**金色圆点 = 带青色符文的黄铜头**，另一头是银灰钢杆）；**棕色框 = 背包**；**灰框 = 头的位置**。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看每条线对应身体的哪一部分。
> - **警棍的大小照定稿，不照参考图**：每根约 30 格长、2–3 格粗，侧把手 1–2 格；沿着紫线的方向画，黄铜头在金点那一头；线比这长时画到定稿的长度就停。手握在警棍的侧把手上。
> - **背包一直背在背上**，大小和定稿一样，照棕色框的位置；身体转过来时露出的部分多一点或少一点。
> - **头一格一格照 `1_head.png` 画在灰框里**（青绿飞机头、浅海绿的脸朝右前方、两只鱼鳍耳、浅青色眼睛、脸颊鳞点、偏紫的嘴）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**（`d_fall` / `d_down` 倒下时头跟着身体放倒，但还是这个头）。警棍和手**不要挡住脸**（眼睛、嘴）；警棍举过头顶时（`e_raise`、`r_cross`）它在头的旁边或上面，脸露在外面。
> - **长短要数格子**：和定稿一样，头（含飞机头和耳朵）约 29 × 31 格，手臂从肩膀到手约 30 格。**手臂沿着骨架画，长短和定稿一样，关节处弯折，不要拉长**；腿沿着红线 / 蓝线，靴子和定稿一样大。他身材修长但结实。
> - **`d_down`**：他趴在地上（金铲铲原样），**身体贴着地面线**，背包在背上朝上，头在右边、脸朝下侧着，警棍落在身边。

## 12 个姿势

| 图 | 文件 | 片段 | 前面的手臂 | 姿势 |
|---|---|---|---|---|
| 2 | `steb-pose-a_wind.png` | attack2@296 | 橙（右手） | 普攻（双警棍连击）第一下 1：近处的手把警棍高高举到右上方，蓄力 |
| 3 | `steb-pose-a_hit.png` | attack2@445 | 青（左手） | 第一下 2：弓步往前，警棍狠狠往右前下方劈下去（技能1的重击也用这一帧） |
| 4 | `steb-pose-a2_wind.png` | attack1@0 | 青（左手） | 第二下 1：换另一根警棍，两臂张开，身体往后一拧蓄力 |
| 5 | `steb-pose-a2_hit.png` | attack1@326 | 橙（右手） | 第二下 2：另一根警棍横着扫出去，打向右前方 |
| 6 | `steb-pose-q_dose.png` | spell@983 | 青（左手） | 技能1 战地医疗 1：两脚分开站稳，把警棍发光的黄铜头按在自己胸口，给自己打一针（绿光之后单独画，不画） |
| 7 | `steb-pose-q_raise.png` | attack2@593 | 青（左手） | 技能1 2：压低身子，把警棍竖着高高举起，准备砸下去 |
| 8 | `steb-pose-e_raise.png` | spell@590 | 青（左手） | 技能2 通缉令 1：站直，两根警棍竖着举在身体两侧——发通缉！ |
| 9 | `steb-pose-e_point.png` | attack2@741 | 青（左手） | 通缉令 2：压低身子，两根警棍平举对准右前方的目标（标记之后单独画，不画） |
| 10 | `steb-pose-r_cross.png` | dance@0 | 橙（右手） | 大招 医疗背包 1：两根警棍在头顶交叉，召集队友 |
| 11 | `steb-pose-r_squat.png` | dance@275 | 橙（右手） | 大招 2：两腿分开稳稳地蹲下，双手撑在膝上，背后的大背包朝上（背包打开的光之后单独画，不画） |
| 12 | `steb-pose-d_fall.png` | death@380 | 橙（右手） | 被击倒：跪倒在地、身体往后仰，警棍脱手 |
| 13 | `steb-pose-d_down.png` | death@1100 | 青（左手） | 倒地：趴在地上（金铲铲原样），背包在背上，警棍落在身边 |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 9 px squares (his soles on y 1176) - a TALL, LEAN BUT STURDY YOUNG FISH-FOLK MAN: PALE SEA-GREEN SKIN, a TEAL QUIFF, POINTED GREEN FIN EARS, teal scale spots on his cheeks, pale cyan eyes, purplish lips; a BLUE ENFORCER UNIFORM with a gold-trimmed high collar and blue-and-gold shoulder guards, a pale chest plate, a row of brown leather medicine pouches on crossed brown straps, a dark brown belt, grey-purple trousers, dark bottle-green gloves and tall boots with gold rings; a BIG BROWN LEATHER BACKPACK on his back; TWO SIDE-HANDLE BATONS (a blue steel tube, a BRASS HEAD with glowing cyan runes at one end, a silver-grey rod at the other, a wooden side grip); B its HEAD shown 8x (about 29 squares wide, 31 tall: the quiff, the face and the fin ears); C a 3D RENDER of this same character's own game model in THIS POSE, on the same 1254 canvas and grid, already scaled and placed where the picture must be (copy the BODY POSE from it - never its 3D shading); D the SKELETON of that pose, exactly over C: green = the spine (pelvis to the base of the neck), ORANGE = his right arm, CYAN = his left arm (each line from the shoulder, the big dot = the hand / wrist), red / blue = his legs (red = left, blue = right), PURPLE bars = the two BATONS (the GOLD DOT = the brass head), the BROWN outline = the BACKPACK, GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 9 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; his soles (or the lowest point) on y 1176.
COUNT THE SQUARES: the same proportions as image A - the head with the quiff and the ears about 29 x 31, each arm about 30 squares from the shoulder to the hand, a lean, sturdy body. The body exactly where C shows it. The arms along their lines, bending at the elbow, never stretched; the legs along the red / blue lines, the boots as big as in A. THE BATONS along the purple bars, EXACTLY AS LONG AND AS THICK AS IN IMAGE A (about 30 squares long, 2-3 thick), the brass head with its cyan runes at the gold dot, the hand on the side grip - stop at that length even if a bar runs longer. THE BACKPACK always on his back, as big as in A, where the brown outline is. The near side in full tone, the far side a step darker (the far leg a step darker than the near leg).
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the sea-green face to the front-right, the fin ears, the pale cyan eyes, the cheek scales, the teal quiff) - the same head in every pose, only moved (tilted with the body when he falls or lies down), never turned, never redrawn as a profile. Neither a baton nor a hand covers the face.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow halo, no blur, no anti-aliasing.
No effects (no green healing glow, no shield, no target mark, no light from the pack, no sparks, no motion lines), no target character, no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_wind: `BATON WIND-UP - the near hand raising its baton high to the upper right, loading the blow.`
- a_hit: `BATON STRIKE - lunging forward, the baton slammed down to the front-right.`
- a2_wind: `SECOND BATON WIND-UP - the other baton now, both arms spread, the body twisted back to load.`
- a2_hit: `SECOND BATON SWEEP - the other baton swept across to the front-right.`
- q_dose: `FIELD MEDICINE - feet planted apart, pressing a baton's glowing brass head to his own chest: a dose of medicine (the green glow comes later: do NOT draw it).`
- q_raise: `STRIKE RAISE - crouched low, a baton raised straight up, about to smash down.`
- e_raise: `WANTED CALL - standing tall, both batons held upright at his sides: a call to his squad.`
- e_point: `WANTED AIM - crouched, both batons held level and aimed at the target to the front-right (the mark comes later: do NOT draw it).`
- r_cross: `MEDIC'S PACK RALLY - both batons crossed high over his head, rallying his squad.`
- r_squat: `MEDIC'S PACK BRACE - a wide, steady squat, hands on his knees, the big backpack on his back facing up (the light of the opened pack comes later: do NOT draw it).`
- d_fall: `KNOCKED DOWN - dropped to his knees, the body thrown back, the batons slipping from his hands.`
- d_down: `DOWN - lying face down on the ground (as in the game), the backpack on his back, the batons beside him.`

## 交回

- 每个姿势一张：`outputs/steb-poses/steb-pose-<名字>.png`（1254 × 1254、真透明背景、每格 9 px）；原始生成图原样放进 `outputs/steb-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **12 张都画完再交**，中间不要停，最后写 `outputs/steb-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/steb_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/steb/codex_poses/`，**先量 Codex 实际的格子**（不一定是 9 px），读 raw，按定稿的头（hd/idle.png）对齐、缩到定稿的密度；每帧 8 倍检查（头不动、脸上眼睛还在、警棍不挡脸、警棍长短方向对、背包还在背上、没有被压扁的身体、腿不变形、跑步有交叉步、远近腿深浅分得开）。
- 骨架包：`tools/art/pack_steb_poses.py`（骨架是他客户端模型自己的骨骼，按动作片段的那一帧投影：不是手摆的；警棍按 Weapon 子网格挂在 L_Weapon / R_Weapon 上的顶点画，黄铜头按贴图颜色找）；这份提示词由 `tools/art/gen_steb_pose_md.py` 生成。跑步 8 帧在 1.30 秒的周期里各占 `RUN_MS` 的一段。
