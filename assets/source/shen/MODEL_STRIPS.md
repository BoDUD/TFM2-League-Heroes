# 慎：动作帧（第 2 步，给 Codex 的提示词）

> 造型已定稿（`design/shen_design.png`：128×128 画布 ×8，头巾顶第 60 行到脚底第 99 行 40 格，30 色；`design/shen_palette.png` 是它的全部颜色）。这一步画 **38 帧**动作，**每帧单独一次生成**（整条动作画在一张图里会糊），每帧一个文件夹 `frames/<动作>_<帧号>/`：
>   - `1_design.png` 定稿（长相、比例、衣服、刀全照它）；`2_league_game_size.png` 英雄联盟原版这一帧，**已经按游戏尺寸放在同一张画布上**（红线 = 脚底第 99 行，蓝线 = 站位列）；`3_league_hd.png` 同一帧的高清图。
>   - **整个人照 2/3 号图的姿势一格一格重画**（头随身体一起画，不要贴头），身体大小和 1 号图一样（站直时头巾顶到脚底 40 格），只用定稿的颜色。
>   - **手以定稿为准**：举起的手（定稿图左）反手握刀、柄尾朝上；另一只是张开的棕手套。除非这一帧的说明写了刀怎么动。
>   - **跑步特殊**：`1_given_upper_body.png` 是定稿本身的上半身（第 86 行以上，已经按跑步起伏放好），**一格都不要改**；只按 `4_leg_guide.png` 的引导线画第 86 行以下：红 = 近腿（画在前面）、蓝 = 远腿，膝盖在引导线拐弯处，靴子在方框里；两腿要在一个循环里**交叉**；前摆下端、身后长布尾下端随步子摆。
> - 交付：`outputs/shen-strips/<动作>_<帧号>.png`（1024×1024，例如 `attack_4.png`）+ `outputs/shen-strips/raw/<同名>.png`（**生图原稿，不要重采样**），全部画完**最后**写 `outputs/shen-strips/HANDOFF.md`。
> - 严格 8×8 网格、透明度 0/255、只用定稿颜色、一种近黑描边 `#0B010F`；脚底线以下没有像素（倒地那帧也贴着脚底线）。

## 帧表

| 动作 | 帧数 | 每帧时长（ms） | 出手帧 |
|---|---|---|---|
| `run` 跑步 | 8 | 100 100 100 100 100 100 100 100 | — |
| `attack` 普攻（前冲一步，反手刀从右往左下横扫） | 6 | 50 60 60 90 80 60 | 第 4 帧 |
| `skill` Q 奥义！暮临（前手推掌召回灵魂之刃） | 4 | 60 60 80 100 | 第 3 帧 |
| `skill2` E 奥义！影缚（下蹲后整个人向前平飞冲出） | 4 | 50 50 100 100 | — |
| `ult` R 起手（收刀，双手胸前结印） | 3 | 100 100 100 | — |
| `ult_loop` R 引导（双手结印，循环） | 4 | 200 200 200 200 | — |
| `hit` 受击 | 1 | 100 | — |
| `dead` 死亡（踉跄、跪下、侧身倒地） | 8 | 100 100 120 150 150 200 250 400 | — |

## 逐帧说明（中文 / English）

### `run` 跑步

1. `run_1`：按引导线画腿：红=近腿（画在前面），蓝=远腿；远腿踩地在后、近腿抬起往前摆  
   *legs on the guide: red = near leg (in front), blue = far leg*
2. `run_2`：按引导线：两腿在胯下交错  
   *legs cross under the hips*
3. `run_3`：按引导线：远腿踩地、近腿在后蹬起  
   *far leg planted, near leg pushing off behind*
4. `run_4`：按引导线：近腿向前摆过远腿  
   *near leg swinging past the far leg*
5. `run_5`：按引导线：近腿落地在前、远腿在后  
   *near leg lands in front, far leg behind*
6. `run_6`：按引导线：远腿离地向前收（身体最高）  
   *far leg lifted and coming forward (body highest)*
7. `run_7`：按引导线：两腿交错，远腿向前摆  
   *legs crossing, far leg swinging forward*
8. `run_8`：按引导线：远腿伸到前面准备落地（接回第 1 帧）  
   *far leg reaching ahead to land (loops to frame 1)*

### `attack` 普攻（前冲一步，反手刀从右往左下横扫）

1. `attack_1`：起手：和待机几乎一样——举起的手反手握刀在头顶上方，前手向前张开  
   *start: like the idle, the sword up in a reverse grip, the open hand forward*
2. `attack_2`：准备：身体略向右转，举刀的手更高，刀身从头后往前翻（刀尖指向左上）  
   *wind-up: the sword arm higher, the blade turning over from behind the head*
3. `attack_3`：前冲：向前跳一步（前膝抬到腰高），持刀手甩到身体右前方、刀横在肩前；前手收到胸前  
   *leap forward (front knee up), the sword hand swung out to the front right, blade level at the shoulder*
4. `attack_4`：**挥中**：身体前压、头低，持刀手从右往左下横扫，刀身横在身前膝盖高（刀尖朝图左），不低过脚底线；前脚落地 **← 出手帧**  
   *HIT: body pressed forward, the blade sweeps low across the front at knee height (tip to the image left), front foot down*
5. `attack_5`：收刀：刀转到身后左下方竖着（刀尖朝下），持刀手在腰侧；前手向前上方伸出、掌心朝前  
   *follow-through: the blade upright behind on the lower left, the other hand stretched forward-up*
6. `attack_6`：回势：站稳，刀反手垂在身后左侧，前手伸在前方  
   *recover: standing, the sword hanging behind on the left, the open hand forward*

### `skill` Q 奥义！暮临（前手推掌召回灵魂之刃）

1. `skill_1`：待机姿势（反手举刀，前手张开）  
   *the idle pose*
2. `skill_2`：举刀的手不动；前手向前推出、张开手掌，身体略前倾  
   *the sword hand stays up; the open hand pushes forward, the body leans a little*
3. `skill_3`：**出手**：前手推到最前（手臂伸直、掌心朝前、五指张开）——召回灵魂之刃 **← 出手帧**  
   *RELEASE: the open hand pushed fully forward, arm straight, palm out (calling the spirit blade)*
4. `skill_4`：保持推掌，身体回直  
   *holding the palm out, the body upright again*

### `skill2` E 奥义！影缚（下蹲后整个人向前平飞冲出）

1. `skill2_1`：下蹲蓄力：身体前倾，两膝深弯，刀仍反手握在头后上方  
   *crouch: leaning forward, knees deeply bent, the sword still up behind the head*
2. `skill2_2`：起跳：身体向前斜冲约 45 度，后腿蹬直，持刀手收到肩上、刀横在背上  
   *launch: the body diving forward at ~45 degrees, back leg straight, the sword laid along the back*
3. `skill2_3`：平飞：整个人几乎水平向前飞——头在最前（朝右）、身体在后、两腿向后伸直，刀横在背上方，冰蓝柄尾朝前  
   *flying flat: head first to the right, body and straight legs trailing, the sword along the back, ice-blue pommel forward*
4. `skill2_4`：平飞（同 3，布尾向后飘起）  
   *flying flat (as 3, the cloth tail streaming back)*

### `ult` R 起手（收刀，双手胸前结印）

1. `ult_1`：待机，举刀的手开始放下  
   *the idle, the sword hand starting to come down*
2. `ult_2`：刀收到身侧（反手、刀尖朝下贴在身后），两手在胸前合拢结印（双拳相对、两肘张开）  
   *the sword lowered to the side (tip down behind), both hands meeting before the chest in a seal, elbows out*
3. `ult_3`：双手向前平推结印，站直  
   *both hands pushed forward in the seal, standing straight*

### `ult_loop` R 引导（双手结印，循环）

1. `ult_loop_1`：双手在胸前结印，站直（刀反手贴在身后）  
   *hands together before the chest, standing straight (sword down behind)*
2. `ult_loop_2`：两肘向外张开，双拳在胸前  
   *elbows out wider, fists at the chest*
3. `ult_loop_3`：双臂向两侧平伸，掌心朝外  
   *both arms stretched out to the sides, palms out*
4. `ult_loop_4`：收回胸前结印（接回第 1 帧）  
   *back to the seal at the chest (loops to frame 1)*

### `hit` 受击

1. `hit_1`：被击中：身体向后（图左）仰、头后仰，前手抬起，刀仍反手举着  
   *hit: leaning back (image left), head back, the open hand up, the sword still raised*

### `dead` 死亡（踉跄、跪下、侧身倒地）

1. `dead_1`：受击后仰（同受击）  
   *knocked back (as hit)*
2. `dead_2`：踉跄后退，前手抬到脸前，刀反手举过头  
   *staggering back, the open hand before the face, the sword up*
3. `dead_3`：身体歪向后方，刀从头上垂下到身侧（刀尖朝下）  
   *tilting back, the sword coming down to the side (tip down)*
4. `dead_4`：身体下沉，两膝弯，刀拄在身侧  
   *sinking, knees bent, the sword planted at his side*
5. `dead_5`：半跪（一膝着地），头低下  
   *half kneeling (one knee down), head bowed*
6. `dead_6`：单膝跪地，身体前倾，持刀手撑在身后  
   *on one knee, leaning forward, the sword hand propped behind*
7. `dead_7`：跪得更低，即将倒下  
   *kneeling lower, about to fall*
8. `dead_8`：侧身倒在地上：平躺，头朝图右、脚朝图左，刀落在身旁（都贴着脚底线，不低过它）  
   *lying on his side on the ground, head to the image right, feet left, the sword beside him (on the feet line)*

## 提示词（每帧一次；把 {name} 换成帧名、{line} 换成这一帧的英文说明，附上这一帧文件夹里的图，按编号顺序）

动作帧（除跑步外）：

```text
Attached for ONE frame: (1) the approved game sprite of this character - the design, at 8x on a 1024x1024 canvas (128x128 squares, one square = an 8x8 block): its look, colours, proportions, clothes and its sword are final; (2) League of Legends' own frame of this action at the same game size on the same canvas (the red line = the soles' row 99, the blue line = his standing column); (3) the same League frame in high detail.
Draw this ONE frame of the action as a game sprite on a 1024x1024 canvas: the WHOLE figure in the pose of image 2/3, redrawn square by square in the look of image 1 - the same head size and face (the navy hood with its silver brow band and fin, the grey ridged mask, the two glowing lavender eyes in a skin slit), the same pauldrons, chest plates, bare tanned upper arms, navy gauntlets and BROWN gloves, the same sash, tassets, apron and long cloth tail, the same purple baggy trousers and brown boots, the same curved silver sword with the ice-blue pommel. Body size exactly as in image 1 (40 squares from the hood's top to the soles when standing); every square one crisp 8x8 block on one 8-px grid; only the design's colours (image 1's palette); a one-square near-black outline (#0B010F); transparent background; no anti-aliasing, no half-transparent pixels, no text, no grid, no shadow.
The design's hands win over League's: the RAISED arm (image left in the design) holds the sword in a REVERSE grip (pommel on top) unless the frame text says the sword moves; the other hand is the open gloved hand. The motion of THIS frame: {line}
Place: League's pose where image 2 has it - the soles on row 99 (y=792-799) unless the frame is off the ground, the standing column x=512 as in image 2. Nothing below row 99.
Deliver this frame as outputs/shen-strips/{name}.png (1024x1024) and the image generator's original output untouched as outputs/shen-strips/raw/{name}.png.
```

跑步帧：

```text
Attached for ONE run frame: (1) the character's UPPER BODY, given - the approved design's own pixels from the waist up, at 8x on a 1024x1024 canvas (128x128 squares; the red line = the soles' row 99, the blue line = his standing column); (2) League of Legends' own run frame at the same game size; (3) the same in high detail; (4) the LEG GUIDE for this frame over image 1: the near leg red (drawn in front), the far leg blue - hip, knee, ankle - and each boot's box.
Draw ONLY what is below row 86 (the waist): both legs in the design's baggy purple trousers (3 purples, fold lines, one-square near-black outline) and brown boots with purple shoes, following the guide exactly - the near leg over the far leg, a knee where the guide bends, each boot inside its box; also the lower ends of the design's navy apron (between the legs) and of its long navy cloth tail (behind, image left) swinging with the stride. Do NOT change one square of image 1 (the upper body is final, pixel for pixel - it only rises and falls with the run, already placed). Same 8-px grid, the design's colours only, transparent background, no anti-aliasing, no text, no grid, no shadow. The legs must CROSS through the cycle: {line}
Deliver this frame as outputs/shen-strips/{name}.png (1024x1024, upper body + your legs) and the generator's original untouched as outputs/shen-strips/raw/{name}.png.
```

## 交回前自查

- [ ] 38 帧齐全，每帧 1024×1024，文件名 `<动作>_<帧号>.png`，`raw/` 里有同名生图原稿；
- [ ] 每帧整个人和定稿一样大（头一样大、衣服一样），姿势照英雄联盟这一帧；举刀的手反手握刀、另一只是棕手套；
- [ ] 跑步帧第 86 行以上和给的上半身**逐格一样**；两腿按引导线、近腿在前、循环里交叉；
- [ ] 严格 8×8 网格、只用定稿颜色、透明度 0/255；脚底第 99 行，下面没有像素；
- [ ] 最后写 `HANDOFF.md`。
