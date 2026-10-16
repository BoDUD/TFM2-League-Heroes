# 蒙多医生（祖安狂人）：第 2 步，照英雄联盟的动作逐帧画动作条（给 Codex 的提示词）

> 造型已经定了（用户 2026-10-16：「选 A，42 行，PPU 1.5」）：`design/drmundo_design.png`，**就是你第 0 步画的 A 逐格读回**。它是 115 × 90 格，3/4 正面朝右，微微驼背站着，近侧的手（画面左边）垂着拎骨锯，37 色。这里每格 **7 × 7 px**，画布 1536×1024 正好 219 × 146 格。造型就是待机，**待机和受击不用画**；其余动作照英雄联盟里蒙多的动作画。
> - **每帧一张图**：`now/drmundo_<动作>_<n>.png` 是**骨架**，也就是英雄联盟里这一帧的 3D 模型，已经按造型的大小、在同一个格子里放好了，**姿势、位置、身高都照它**。`guide/` 里是同一张图加了参考线：**红线 = 脚底线**（第 138 行的下边），**蓝线 = 造型最高的地方**，**蓝十字 = 站位点**（第 100 列），浅灰线每 10 格一条。这些线只是对位用的，**不要画进图里**。`design/drmundo_design_on_canvas.png` 是造型站在这张画布上的样子（同一个站位点）。
> - **长相、比例、颜色、细节全部照造型**（骨架 + 皮囊）：骨架是 3D 渲染，只看它的姿势；**身材按造型画**（小脑袋缩在两个巨大的肩膀中间，粗胳膊、大手、短粗腿）。**大小和造型一样**：站直时头发顶到脚底 90 格，不要画大，也不要画小。
> - **每一帧的头都是造型的头**：黑色刺头、方下巴、紫色的脸、近侧那只发光的粉红眼睛、歪牙，逐格照抄造型（第 0–22 行那一块），只平移，脸朝右前方。**不要重新画一张脸，也不要画成侧脸。** 吼叫的帧（W 结束、R）可以把嘴张大一点，其余照抄。
> - **骨锯就是造型里那把**（钢青色刀身、下缘的大锯齿、锈橙色刀背、青蓝色的刀箍），**长短、宽窄不能变**：整把跟着手移动、转角度，不能变短、变窄、弯曲。肩上的铜星片和粉红宝石、手腕的绷带、腰带、裤子都和造型一样。
> - **E 的药箱**：E 是远侧的手（画面右边）抡起一个**黑色皮革的大医药箱**（带棕色提手和铜扣，大约 22 × 18 格）砸出去。骨架里能看到这个箱子。箱子**只在 E 的 5 帧里出现**，其他动作都没有。
> - **Q 扔出去的骨锯不画**：Q 是近侧的手把骨锯举到头后**整把扔出去**。出手前骨锯在手里；出手那帧（第 4 帧）**手里是空的**（飞出去的锯是第 3 步的特效）；第 5 帧骨锯**又回到手里**，和造型一样。
> - **一律 3/4 正面朝右**（脸和胸口朝着看画的人，和造型一样），**身体不要转成侧面**。骨架也是 3/4 视角，照它的手脚动作画就行。近侧的腿在画面左边、颜色亮；远侧的腿在画面右边、暗一档。
> - **跑步**：大块头重重地往前跑，身体前倾，骨锯拎在近侧手里跟着摆。**两条腿轮流在前**：第 1–4 帧近侧的腿在前，第 5–8 帧远侧的腿在前（第 3、7 帧两条腿交叉而过）。**不能 8 帧都是同一条腿在前。** 两只脚的脚尖最多离地 2–3 格。
> - 每格 7 × 7 px 一个纯色方块，所有格子对齐同一个网格（`design/drmundo_design_on_canvas.png` 的格子）；**只用造型的 37 色**（`design/drmundo_palette.png`），药箱用造型里的近黑、深灰、棕和铜色；外面一圈近黑描边（和造型一样粗）；不要抖动、渐变、噪点、抗锯齿、半透明。
> - **不画特效**（飞出去的锯、电击的闪电、药水的光、血、残影、烟），只画蒙多；**红线以下什么都不能有**；出招一律朝画面右边。
> - 骨架只是参考：英雄联盟里他死的时候骨锯会飞到一边，**我们让骨锯掉在他手边**。死亡第 3–6 帧的骨架**浮在半空**（3D 模型往镜头这边倒，投到画面上就高了），**请把他的背直接放在红线上躺平**，骨锯也落在红线上。
> - 交付到 `outputs/drmundo-strips/`：每帧 `drmundo_<动作>_<n>.png`（1536×1024、透明背景、和骨架同一个格子）+ `drmundo_<动作>_<n>_1x.png`（1 像素 1 格，必须和大图逐格一致）；生图的原稿放 `raw/`（不要重采样）；**最后**写 `HANDOFF.md`（每张用了哪条提示词、哪里没做到），最好再打成一个 zip（`drmundo_strips_done.zip`）。
> - 生图后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩放**。画一个动作的后一帧时，**附上前一帧**，让人、头、骨锯一样大。

## 要画的帧（43 帧）

| 文件 | 动作 | 这一帧画什么（身体照骨架） |
|---|---|---|
| `drmundo_run_1..8.png` | 跑步（8 帧循环） | 重重地向右跑，身体前倾，骨锯拎在近侧手里摆动；两条腿轮流在前（1–4 近侧腿在前，5–8 远侧腿在前，3、7 交叉），远侧的手臂前后摆 |
| `drmundo_attack_1.png` | 普攻：骨锯劈砍 | 近侧的手把骨锯举过头顶，身体后仰 |
| `drmundo_attack_2.png` | | 骨锯举到最高、在头后，身体蓄力 |
| `drmundo_attack_3.png` | | 出手：身体前扑，骨锯从头顶向画面右前方劈下，劈到腰的高度 |
| `drmundo_attack_4.png` | | 收势，骨锯压在前下方，身子压低 |
| `drmundo_attack_5.png` | | 回到造型的站姿 |
| `drmundo_attack_e_1.png` | E 钝器创伤：抡药箱 | 远侧的手提起黑色药箱往后拉，近侧的手拎着骨锯横在身前 |
| `drmundo_attack_e_2.png` | | 药箱拉到身后，身体扭转蓄力，弓步 |
| `drmundo_attack_e_3.png` | | 出手：远侧的手把药箱向画面右边狠狠抡出、手臂伸直 |
| `drmundo_attack_e_4.png` | | 药箱抡过头，手臂在头上方弯过来 |
| `drmundo_attack_e_5.png` | | 收势，药箱垂在远侧手里，回到站姿 |
| `drmundo_skill_1.png` | Q 感染之锯：扔骨锯 | 近侧的手把骨锯举到头侧，身体后仰 |
| `drmundo_skill_2.png` | | 骨锯举到头后，手臂弯起蓄力 |
| `drmundo_skill_3.png` | | 身体前倾，手臂开始往前甩 |
| `drmundo_skill_4.png` | | 出手：手臂向画面右边伸直，**手里空了**（飞出去的锯不画） |
| `drmundo_skill_5.png` | | 回到造型的站姿，骨锯回到手里 |
| `drmundo_skill2_1..4.png` | W 心脏电击器：开启 | 照骨架：两条胳膊向两边张开、挺胸，像给自己通电，骨锯仍在近侧手里；第 4 帧手臂回收 |
| `drmundo_skill2_end_1..4.png` | W 心脏电击器：放电 | 照骨架：1 弓背收紧，2 猛地挺身张嘴吼，3 两臂向下一甩，4 回到站姿 |
| `drmundo_ult_1..6.png` | R 极限剂量 | 照骨架：1–2 蹲低、握拳、骨锯横在身前，3–4 身体缩紧蓄力，5 挺身仰头、张嘴大吼、两臂张开秀肌肉，6 回到站姿 |
| `drmundo_dead_1.png` | 死亡 | 被打中，身体一僵、往后仰 |
| `drmundo_dead_2.png` | | 往后倒，手脚无力，骨锯脱手 |
| `drmundo_dead_3.png` | | 摔到地上（背贴着红线，不要浮在半空） |
| `drmundo_dead_4.png` | | 仰面躺在地上，骨锯掉在手边 |
| `drmundo_dead_5.png` | | 同上，一条腿抽动一下 |
| `drmundo_dead_6.png` | | 同第 4 帧，静止（最后一帧） |

## 提示词

每帧一次，附图（工具一次最多 5 张时按这个顺序）：
1. `now/drmundo_<动作>_<n>.png`（骨架）
2. `design/drmundo_design.png`（造型）
3. `design/drmundo_design_on_canvas.png`（造型在画布上的大小和位置）
4. 同一个动作的前一帧（你刚交付的那张；第 1 帧不附）
5. `refs/drmundo-A.png`（你第 0 步画的原画，看长相）

```text
Image 2 is the final pixel-art design of this character: Dr. Mundo, a huge purple-skinned brute in 3/4 front view facing right, standing a little hunched - a SMALL head with short spiky black hair, a square jaw and one glowing pink eye sunk between ENORMOUS shoulders, purple skin with big muscle masses, bronze star-shaped plates with pink gems on both shoulders, an off-white sleeveless patient's top with leather straps and brass buckles, cream bandages on the wrists, a brown belt, baggy blue-grey trousers, big bare purple feet (a grey flip-flop on the near foot), and a big rusty BONE SAW (teal-steel blade with big jagged teeth, rusty orange back, teal band at the grip) hanging in his near hand. It is drawn on a grid of 7x7-pixel squares, 115 x 90 squares, 37 colours. Image 3 shows the design standing on a 1536x1024 canvas: that is the size and the place.
Image 1 is a 3D render of the same character from the game in THIS FRAME'S POSE, already scaled and placed on the same canvas: copy its pose, its place and its size - NOT its 3D look, NOT its proportions (keep the design's build: the small head between huge shoulders, thick arms, short thick legs). (Image 4, when attached, is the previous frame of the same action: keep him exactly as big.)
Draw ONE frame: <WHAT>
Rules: the same 1536x1024 transparent canvas and the SAME 7-pixel grid as Image 3, every square one flat colour from Image 2's 37 colours; the character exactly as big as Image 2 (90 squares from the top of his hair to his soles standing); he stays in the 3/4 FRONT view of Image 2 (face and chest toward the viewer), never turned side-on; his head - spiky black hair, purple face, the glowing pink eye, crooked teeth - copied square for square from Image 2, only moved (the mouth may open wider in a roar); the bone saw is the design's, the same length, width and colours, moved and turned as a whole piece, never shorter, narrower or bent; the shoulder plates, bandages, belt and trousers as in Image 2; the near leg on the image left in full tone, the far leg on the image right one shade darker; the soles on the red line of the guide (square row 138) - when lying, the back on it - nothing below it; a near-black outline as thick as Image 2's; no dithering, no gradients, no noise, no anti-aliasing, no semi-transparency; no effects (no flying saw, no lightning, no chemical glow, no blood, no afterimage, no smoke), no text, no grid lines. Also deliver a 1x copy (one pixel per square) that matches square for square.
```

`<WHAT>` 按上表换成英文：

- run：`running forward to the right, heavy and lumbering, frame <n> of an 8-frame loop: the body leaning forward, the bone saw swinging in the near hand, the far arm swinging; the legs as in Image 1 - the NEAR leg in front in frames 1-4 and the FAR leg in front in frames 5-8, the legs crossing in frames 3 and 7 (never the same leg in front in all eight); the toes at most 2-3 squares off the ground`
- attack 1–5：`basic attack, an overhead chop with the bone saw in his NEAR hand, frame <n> of 5: <1: lifting the saw over his head, leaning back | 2: the saw at its highest, behind his head, gathering | 3: the strike: lunging forward, the saw chopped down to the image right to waist height | 4: the follow-through, the saw low in front, crouching | 5: back to the stance of Image 2>`
- attack_e 1–5：`Blunt Force Trauma, swinging a heavy BLACK LEATHER DOCTOR'S BAG (brown handle, brass clasps, about 22 x 18 squares, as in Image 1) with his FAR hand while the near hand holds the bone saw across his body, frame <n> of 5: <1: the far hand lifting the bag and pulling it back | 2: the bag drawn behind him, the body twisted, a wide lunge | 3: the strike: the bag swung hard out to the image right, the far arm straight | 4: the bag carried on over his head, the arm curling above | 5: recovering, the bag hanging from the far hand, back toward the stance of Image 2>`
- skill 1–5：`Infected Bonesaw, throwing the bone saw, frame <n> of 5: <1: the saw lifted beside his head in the near hand, leaning back | 2: the saw cocked behind his head, the arm bent to gather | 3: leaning forward, the arm starting to whip forward | 4: the release: the throwing arm straight out to the image right, the hand now EMPTY (the flying saw is NOT drawn) | 5: back to the stance of Image 2, the bone saw back in his hand>`
- skill2 1–4：`Heart Zapper, charging himself up, frame <n> of 4 as in Image 1: both arms spread wide to the sides, the chest pushed out, the saw still in the near hand <4: the arms coming back in>`
- skill2_end 1–4：`Heart Zapper, the discharge, frame <n> of 4: <1: hunched, the back curled, gathering | 2: snapping upright, the mouth wide open in a roar | 3: both arms flung down | 4: back to the stance of Image 2>`
- ult 1–6：`Maximum Dosage, frame <n> of 6 as in Image 1: <1: crouching low, fists clenched, the saw held across his body | 2: the same, lower | 3: the body clenched, gathering | 4: tighter still | 5: rearing up, head thrown back, the mouth wide open in a roar, both arms flexed out | 6: back to the stance of Image 2>`
- dead 1–6：`dying, frame <n> of 6: <1: hit, the body stiffening, leaning back | 2: falling backward, limbs going limp, the saw slipping from the hand | 3: hitting the ground | 4: lying on his back, the bone saw on the ground beside his hand (frames 3-6: Image 1 floats above the ground - lay his back ON the red line, the saw on the red line too) | 5: the same, one leg twitching | 6: the same as frame 4, still (the last frame)>`

## 交回前请检查

- 43 帧都在，文件名对，每张 1536×1024 透明底、7 px 一格，`_1x` 和大图逐格一致。
- 每帧和造型一样大（站直头发顶到脚底 90 格），一直是 3/4 正面；头是造型的头（同一张脸）；骨锯长短宽窄不变。
- Q 出手那帧手里空着，最后一帧骨锯回到手里；E 的 5 帧都有黑色药箱、在远侧手里，其他动作没有药箱。
- 跑步两条腿轮流在前（1–4 近侧腿、5–8 远侧腿），不是 8 帧同一条腿在前。
- 脚底在红线上（死亡躺下的帧是背贴红线），红线以下没有东西；没有特效、没有文字和格子线。
- 全部画完后最后写 `outputs/drmundo-strips/HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 每张按 7 px 格读回（regrid --size 7），颜色贴回造型的 37 色；头按造型逐格贴回（**整颗头连头发一起贴**，伊莉丝的教训：只贴脸会出现两个头）；量每帧头和身体、髋和腿的相对位置（Codex 贴的部件会漂）；跑步逐帧量两只脚的 x，确认换步；骨锯查变形和缝。
- 待机 = 造型 + 呼吸；受击 = 造型平移 + 闪白；写 assets/source/ppu/drmundo_<tag>.png 和 1x 表；用 ppu_restyle 降到 PPU 1.5（用户定的，42 行）；ppu_hd 生成 hd_ / lo_ 帧，在 hd.rs HEROES 里登记（league.dll 0.7.13）；按帧重定出手时间，重跑平衡；逐帧自查后再给用户看 GIF。
- Codex 额度不够时：按塔姆、卡莉丝塔的做法，用定稿自己的像素摆动作（`rig_drmundo.py`，只做无损变换），并告诉用户。
