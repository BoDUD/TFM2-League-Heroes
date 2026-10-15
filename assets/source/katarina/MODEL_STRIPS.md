# 卡特琳娜（不祥之刃）：第 2 步，照英雄联盟的动作逐帧画动作条（给 Codex 的提示词）

> 造型已经定了（用户选了正面 K1 + 侧身 1），共用一套颜色：
> - **侧身**：`design/katarina_side_design.png`（**58 × 68 格**，约 3/4 侧身朝右，K1 那颗头：深红长发、两只绿眼、一只眼上的细竖疤、浅笑；近侧手把一把弯刃匕首举在胸前朝右，远侧手低低握着另一把）——**所有动作都从它画**；
> - **头**：`design/katarina_head_x2.png`（K1 的头放大），**每一帧都用这一颗头**；
> - **正面**：`design/katarina_front_design.png`（待机和选人卡用，**这一轮不用画**，只给你看样子）。
> 这里每格 **8 × 8 px**（1536×1024 里 192 × 128 格）。**待机和受击不用画**。
> - **每帧一张图**：`now/katarina_<动作>_<n>.png` 是**骨架**——英雄联盟里这一帧的 3D 模型，已经按造型的大小、按同一个格子放好：**姿势、位置照它**。`guide/` 是同一张加了线：**红线 = 鞋底线**（第 118 行的下边），**蓝线 = 造型站直时发顶的高度**，**蓝十字 = 站位点**（第 90 列），浅灰线每 10 格一条——对位用，**不要画进图里**。`design/katarina_side_design_on_canvas.png` 是造型站在这个画布上的样子（同一个站位点）。
> - **长相、比例、颜色、细节全部照侧身造型**（「骨架 + 皮囊」）：骨架是 3D 渲染，只看姿势，**不要照它的写实比例**（骨架的头比造型小、腿比造型长——一律照造型）。**和造型一样大**：站直时发顶到鞋底 68 格；不要画大也不要画小。
> - **头每帧都是造型的头**：深红长发（侧分刘海）、白皙皮肤、**两只绿眼睛**、细竖疤、浅笑，逐格照抄造型（造型最上面那一块，到下巴为止），**只平移**，脸朝右前方（两只眼睛都看得见）；**不要重新画一张脸**，不要画侧脸，**头不要歪、不要转、不要缩放**。身后的长发可以随动作飘（跑、跳、转身时往后甩），但颜色和发型照造型。
> - **衣服每帧照造型**：炭黑皮甲上衣 + 钢灰胸甲、露腰；带尖刺的深钢小肩甲；带尖刺的银灰护腕；黑手套；交叉的棕皮带、腰后暗红布条；黑皮裤 + 大腿银色刃饰；银灰护胫 + 黑靴；背后斜插的匕首刀柄。**手臂、腿的粗细和长短每帧一样**（和造型一样，不要画细、画长）。
> - **两把匕首**：银白弯刃 + 深色刀柄，**每帧都和造型里的一样大、一样形状**（只平移、按手的方向转 90° 的倍数或照骨架的角度整把转），**轮廓连续，不碎、不弯、不变长变短**；匕首永远在手里（除了下面写明扔出去的那一帧，扔出去后那只手是空的）。
> - **一律侧身朝右**（和侧身造型一样）：**两条腿一前一后**（近侧腿颜色亮；远侧腿暗一档）。
> - 每格 8 × 8 px 一个纯色方块，所有格子对齐同一个网格（`design/katarina_side_design_on_canvas.png` 的格子）；**只用造型的颜色**（`design/katarina_palette.png`）；外轮廓描边和造型一样粗（约 2 格近黑）；不要抖动、渐变、噪点、抗锯齿、半透明（**alpha 只能是 0 或 255**）。
> - **不画特效**（刀光、残影、旋转的刀圈、飞出去的匕首、尘土），只画角色；**红线以下什么都不能有**；出手一律朝画面右边。
> - 骨架只是参考：英雄联盟里她有几帧背过身去或者在空中翻转，**我们不背身、不倒立**——脸一直朝右前方，照下表写的画。
> - 交付到 `outputs/katarina-strips/`：每帧 `katarina_<动作>_<n>.png`（1536×1024、透明背景、和骨架同一个格子）+ `katarina_<动作>_<n>_1x.png`（1 像素 1 格，必须和大图逐格一致）；生图原稿放 `raw/`（**原样，不要重采样、不要自己整理**）；**最后**写 `HANDOFF.md`（每张用了哪条提示词、哪里没做到），再打包成 `outputs/katarina_strips_done.zip`。中间不要停，42 帧全部画完再交。
> - 一个动作里的几帧，**画后一帧时附上前一帧**，让角色、头、匕首一样大。

## 要画的帧（42 帧，全部侧身朝右）

| 文件 | 动作 | 这一帧画什么（身体照骨架；手脚按这里） |
|---|---|---|
| `katarina_run_1..8.png` | 跑步（8 帧循环） | 朝右压低身子快跑，**两条腿照骨架交替迈步**：1–4 帧近侧腿往前、远侧腿往后蹬，5–8 帧反过来，**第 3、7 帧两腿在身体下面交叉**，脚抬起时膝盖弯；两手各握一把匕首，手臂随步子前后摆（刀尖朝后下方）；长发往身后飘；身体随步子上下颠 1–2 格 |
| `katarina_attack_1.png` | 普攻：近侧匕首刺击 | 身体稍微后收，近侧手把匕首收到肩前蓄力 |
| `katarina_attack_2.png` | | 身体往右前方压，近侧手臂开始往前送 |
| `katarina_attack_3.png` | | **刺中的一刻**：近侧手臂伸直朝右，**匕首刀尖朝右**，身体前倾，后腿蹬直 |
| `katarina_attack_4.png` | | 刺完：手臂收回一半，身体开始回正 |
| `katarina_attack_5.png` | | 回到造型的站姿 |
| `katarina_skill_1.png` | Q 弹射之刃：甩出一把旋转的匕首 | 近侧手把匕首拉到身后（肩后），身体往后转一点蓄力 |
| `katarina_skill_2.png` | | 身体往前转，手臂从肩后往前甩 |
| `katarina_skill_3.png` | | **出手的一刻**：近侧手臂朝右前方甩直，**手是空的**（匕首已经飞出去——飞出去的匕首不画），身体前倾 |
| `katarina_skill_4.png` | | 甩完：手臂还伸在前面，身体开始回正，近侧手仍是空的 |
| `katarina_skill_5.png` | | 回到站姿，近侧手**重新握着匕首**（她从背后又抽出一把） |
| `katarina_skill2_1.png` | W 伺机待发：把匕首抛向空中 | 下蹲，近侧手握匕首放低在身侧 |
| `katarina_skill2_2.png` | | 往上轻跳，近侧手臂往上抬 |
| `katarina_skill2_3.png` | | **抛出的一刻**：近侧手臂**往正上方举直**、手是空的（匕首已抛到高处——不画），身体伸展，脚尖离地 1–2 格 |
| `katarina_skill2_4.png` | | 落地：两脚踩回红线，近侧手放下 |
| `katarina_skill2_5.png` | | 回到站姿，近侧手**重新握着匕首** |
| `katarina_blink_1.png` | E 瞬步：闪到目标身边落地 | **落地的一刻**：身体低伏、双膝弯，两把匕首往两侧张开，长发还往上飘着 |
| `katarina_blink_2.png` | | 站起一半，近侧匕首往右前方一挥 |
| `katarina_blink_3.png` | | 回到站姿 |
| `katarina_spin_1.png` | 捡起匕首：原地旋身横斩 | 微微跳起，双臂收在胸前，两把匕首交叉 |
| `katarina_spin_2.png` | | 空中：**双臂往两边张开**、匕首朝外，身体还是侧身朝右，长发往一边甩开 |
| `katarina_spin_3.png` | | 双臂还张开，长发甩向另一边（像转了一圈），两只脚收在身下 |
| `katarina_spin_4.png` | | 落地，回到站姿 |
| `katarina_ult_1..6.png` | R 死亡莲华：原地旋转、向四周掷刀（6 帧循环，2.5 秒一直重复） | 两脚踩在红线上、膝盖微弯，**双臂往两边张开**、两把匕首朝外，身体在原地扭转；**每一帧双臂的高低和匕首的方向轮换**（像在转圈），**长发按旋转的方向一帧一帧甩到不同的一边**；头始终是造型那颗、脸朝右前方；第 6 帧要能接回第 1 帧 |
| `katarina_dead_1.png` | 死亡 | 被打中，身体往后仰，双手垂下 |
| `katarina_dead_2.png` | | 腿一软，膝盖弯下去 |
| `katarina_dead_3.png` | | 往后倒 |
| `katarina_dead_4.png` | | 躺在地上（仰面，头在画面左边），整个身体贴着红线，匕首掉在身边 |
| `katarina_dead_5.png` | | 同上 |
| `katarina_dead_6.png` | | 同上，静止（最后一帧） |

## 提示词（每帧一次）

附图（工具一次最多 5 张时按这个顺序）：
1. `now/katarina_<动作>_<n>.png`（骨架）
2. `design/katarina_side_design.png`（侧身造型）
3. `design/katarina_side_design_on_canvas.png`（造型在画布上的大小和位置）
4. 同一个动作的前一帧（你刚交付的那张；第 1 帧不附）
5. `design/katarina_head_x2.png`（她的头，每帧都用这一颗）

```text
Image 2 is the final pixel-art design of this character: a woman assassin seen three quarters SIDE-ON facing right - long crimson red hair with a side-swept lock flowing down her back, fair skin, TWO GREEN EYES, a thin vertical scar over one eye, a faint smile (a 3/4 head: both eyes visible), a charcoal-black leather top with a dark steel chest plate and a bare midriff, small spiked dark steel shoulder guards, spiked silver-grey bracers, black gloves, crossed brown belts and a dark red cloth strip, black leather trousers with silver blade ornaments on the thighs, silver-grey greaves over black boots, dagger hilts on her back; the near hand holds a curved silver dagger up before her chest pointing right, the far hand holds the other low. It is drawn on a grid of 8x8-pixel squares, 58 x 68 squares. Image 3 shows the design standing on a 1536x1024 canvas: that is the size and the place. Image 5 is her head enlarged: the ONE head every frame keeps.
Image 1 is a 3D render of the same character from the game in THIS FRAME'S POSE, already scaled and placed on the same canvas: copy its pose and its place - NOT its 3D look and NOT its realistic proportions (its head is smaller and its legs longer than the design's: always keep the design's). (Image 4, when attached, is the previous frame of the same action: keep her exactly as big.)
Draw ONE frame: <WHAT>
Rules: the same 1536x1024 transparent canvas and the SAME 8-pixel grid as Image 3, every square one flat colour from Image 2's colours only; the character exactly as big as Image 2 (68 squares from the top of the hair to the soles when standing) with Image 2's proportions - the arms and legs as thick and as long as in Image 2 in every frame; she stays SIDE-ON facing image right like Image 2, never turned away, never upside down; her head - the crimson hair, both green eyes, the scar, the smile, down to the chin - copied square for square from Image 2 / Image 5, only moved, never tilted, turned, scaled or redrawn as a profile (only the long hair down her back may swing); the two curved daggers exactly the design's size and shape, whole clean curves, never bent, broken or stretched; the near leg in full tone, the far leg one shade darker; the soles on the red line of the guide (square row 118) unless this frame is in the air, nothing below it; the same near-black outline as Image 2 (about 2 squares); alpha only 0 or 255; no dithering, no gradients, no noise, no anti-aliasing, no semi-transparency; no effects (no blade trails, no afterimages, no spinning blades, no thrown dagger, no glow, no dust), no text, no grid lines. Also deliver a 1x copy (one pixel per square) that matches square for square.
```

`<WHAT>` 换成上表这一帧的英文说明（下面每帧一行，直接复制）：

```text
run_1..8: running fast to the right, low; the legs take turns as in the skeleton: frames 1-4 the near leg forward and the far leg pushing back, frames 5-8 the other way round, in frames 3 and 7 the legs cross under her body; the lifted foot's knee bent; a dagger in each hand, the arms swinging back and forth with the stride (blades pointing back and down); the long hair streaming behind; the body bobbing 1-2 squares with the steps.
attack_1: leaning back a little, the near hand drawing its dagger back in front of the shoulder.
attack_2: pressing forward to the right, the near arm starting to thrust.
attack_3: THE HIT: the near arm thrust straight to the right, the dagger's point to the right, the body leaning in, the back leg straight.
attack_4: the arm half drawn back, the body straightening.
attack_5: back to the design's stance.
skill_1: the near hand pulls its dagger back behind the shoulder, the body twisting back to wind up.
skill_2: the body turning forward, the arm swinging from behind the shoulder.
skill_3: THE THROW: the near arm flung straight to the front-right, the hand EMPTY (the dagger has flown - do not draw it), the body leaning in.
skill_4: the arm still forward, the near hand still empty, the body straightening.
skill_5: back to the stance, the near hand holding a dagger again (drawn from her back).
skill2_1: crouching, the near hand holding its dagger low at her side.
skill2_2: hopping up a little, the near arm rising.
skill2_3: THE TOSS: the near arm raised STRAIGHT UP, the hand EMPTY (the dagger is high in the air - do not draw it), the body stretched, the toes 1-2 squares off the ground.
skill2_4: landing, both soles back on the red line, the near arm coming down.
skill2_5: back to the stance, the near hand holding a dagger again.
blink_1: THE LANDING of a blink: crouched low, both knees bent, both daggers spread out to the sides, the long hair still floating up.
blink_2: half risen, the near dagger slashing forward to the right.
blink_3: back to the stance.
spin_1: a little hop, both arms drawn in before the chest, the two daggers crossed.
spin_2: in the air: BOTH ARMS FLUNG OUT to the sides, the daggers pointing outward, the body still side-on facing right, the hair swung out to one side.
spin_3: the arms still out, the hair swung to the other side (as after a full turn), the feet tucked under her.
spin_4: landing, back to the stance.
ult_1..6 (a loop): both soles on the red line, knees a little bent, BOTH ARMS SPREAD WIDE with the daggers pointing outward, the body twisting in place; from frame to frame the arms' heights and the daggers' directions take turns (as if spinning), the long hair swung to a different side each frame following the turn; the head always the design's head facing front-right; frame 6 leads back into frame 1.
dead_1: struck: leaning back, both hands dropping.
dead_2: the legs giving way, the knees bending.
dead_3: falling backwards.
dead_4..6: lying on her back on the ground (head on the image left), the whole body along the red line, the daggers dropped beside her; 5 and 6 the same, still.
```

## 交回前请检查

- 42 帧都在，每帧都有 `_1x` 版并逐格一致；1536×1024、8 px 格子对齐、alpha 只有 0 / 255。
- 每帧的头都是造型那颗（两只绿眼、竖疤、浅笑，脸朝右前方），大小一样；身体和造型一样大、一样比例。
- 匕首每帧都是造型那两把（大小、形状不变、轮廓连续）；Q 第 3–4 帧和 W 第 3 帧那只手是空的，下一个回到站姿的帧重新握着。
- 跑步两腿真的交替（1–4 / 5–8 前后对调，第 3、7 帧交叉），鞋底踩在红线上。
- 没有特效、没有地面、红线以下没有东西。

## Claude 收到后（给 Claude 看）

- 原稿逐格读回（先量实际格子，再 regrid），每帧找到 Codex 画的头换成造型那颗（rig_jayce / rig_milio 的做法：只换头、身体不缩放），匕首整块检查；跑步检查交叉步；补描边（complete_outline）。
- 写 1 倍帧和 PPU 1.5 的高清帧（rig_katarina.py），idle 由造型呼吸生成、hit 闪白；然后第 3 步特效包（PROMPTS_FX.md，含画进帧的图）。
