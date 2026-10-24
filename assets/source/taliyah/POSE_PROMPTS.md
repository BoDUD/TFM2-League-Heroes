# 岩雀 塔莉垭：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 塔莉垭的造型用户已经定稿（`2_design.png`，你上一轮画的 A-2：3/4 正面朝右——小麦色皮肤、往上盘起的棕色大头发和金色发饰（中间奶白石头）、米白石片披肩、深靛紫上衣和金边、红色长外套和两条挂灰石头的垂带、紫袖子米白护腕、棕色长靴）。英雄联盟里她召石头扔、推出一串石子、撒石雷、按地掀人、唤石墙、蹲在大石头上冲浪——这些靠挪动定稿本身的部件摆不出来，所以请你按骨架画 **14 个姿势，每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张图都是同一个塔莉垭**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 11 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1188**），网格从画布左上角对齐。
> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到脖子根），**红线 = 近侧的腿（画面左边那条，在前面、颜色全亮）**，**蓝线 = 远侧的腿（画面右边那条，暗一档）**，**橙线 = 近侧的手臂（画面左边）**，**紫线 = 远侧的手臂（画面右边）**；**灰框 = 头的位置**；**棕色圆角框 = 冲浪的大石头**（只在冲浪的三个姿势里）。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。
> - **长短要数格子**：**头 29 × 30 格**（Q 版，盘起的大头发占了很多）；**每条腿从胯到脚底约 16 格**，**手臂从肩膀到指尖约 16 格**（手臂很短，比头的宽度还短）；**冲浪的大石头约 44 格宽、24 格高**。骨架就是按定稿量的：**腿、手臂沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长或压短**（以前的英雄腿画错了只能重画——请画完数一数），**不要把直的腿整块转个方向贴上去**。手臂从肩膀（披肩下面）长出来，不能悬空。
> - **头一格一格照 `1_head.png` 画在灰框里**（同样朝右前方、盘起的棕色大头发、金色发饰、两只琥珀色眼睛都看得见、小红嘴）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸或背影、不要重新设计**。手臂和手**不要盖住脸**（举起来的手臂画在头发两边的外面或前面，但不挡眼睛和嘴）。
> - **两条红垂带和末端的灰石头是布**：跟着动作甩动（往后飘、往上扬、摊在地上），但长短、宽窄、石头的数量和定稿一样。**米白石片披肩**永远在肩膀上，跟着身体走。
> - **冲浪的石头**照 `2b_surf_picture.png`（第 0 步你画的 B：一块棕色大岩石，裹着红布，布上有金边）：画在棕色圆角框的位置，**她两只脚踩在石头顶上**，石头底在地面线上；石头本身不动，只有她的身子和手臂在三张里换姿势。
> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。英雄联盟里她有时跳起来、转过身——**我们的永远是 3/4 正面朝右**，只照它的手臂、身体和垂带的动作。

## 14 个姿势

| 图 | 文件 | 姿势 |
|---|---|---|
| 3 | `taliyah-pose-a_wind.png` | 召石：身子微微后仰，远侧手臂高高举到头的右上方、手掌朝上（一块小石头浮在手上方），近侧手臂往后下方摆，两腿站稳，红垂带往后飘（普攻起手） |
| 4 | `taliyah-pose-a_throw.png` | 甩出：身子往前（画面右边）压，远侧手臂往右前方甩出、手张开（石头刚扔出去），近侧手臂往后摆，远侧腿往前一步（普攻打出） |
| 5 | `taliyah-pose-q_raise.png` | 举手召石：身子挺直、微微踮脚，远侧手臂往右上方伸直、手指张开（一串石头从地上升起），近侧手臂往左下方甩开（石穿：起手） |
| 6 | `taliyah-pose-q_cast.png` | 推出石串：身子往前（画面右边）压低，远侧手臂往正前方推直、手掌朝前（石头一颗颗射出去），近侧手臂往后伸开保持平衡，弓步（石穿：射出） |
| 7 | `taliyah-pose-e_raise.png` | 双手举石：两只手臂一起往左上、右上方高高举起成 V 字（手在头发两边的外面，不挡脸），手指张开托着一片碎石，身子挺直（撒石阵：起手） |
| 8 | `taliyah-pose-e_sweep.png` | 撒雷：身子往前弯、半蹲，两只手臂一起从上往前下方扫出去、手张开（一片石雷撒到身前地上），两腿分开（撒石阵：撒出） |
| 9 | `taliyah-pose-w_crouch.png` | 按地：蹲下来，远侧手掌按在身前的地上（地面要隆起），近侧手臂往后上方扬起，膝盖弯着（岩突：按地） |
| 10 | `taliyah-pose-w_push.png` | 横推：站起来，身子转向右前方，远侧手臂往右边横着一推、手掌朝外（把敌人掀飞），近侧手臂收在胸前，两腿站稳（岩突：推开） |
| 11 | `taliyah-pose-r_call.png` | 唤墙：挺直站着，远侧手臂笔直举向天空、手掌张开（石墙从地里升起），近侧手臂往身侧张开，红垂带往上飘（墙幔：起手） |
| 12 | `taliyah-pose-surf1.png` | 冲浪 1：半蹲在一块大石头上（石头裹着红布，见附图 B），远侧手臂往前（画面右边）伸开，近侧手臂往后下方摆着保持平衡，两只脚踩在石头顶上、膝盖朝前，外套往后飘（移动） |
| 13 | `taliyah-pose-surf2.png` | 冲浪 2：和冲浪 1 一样蹲在石头上，身子再低一点往前压，远侧手臂往前下方，外套和垂带飘得更高（移动） |
| 14 | `taliyah-pose-surf3.png` | 冲浪 3：蹲在石头上身子稍微抬起，远侧手臂往右上方张开，近侧手臂往后伸（移动） |
| 15 | `taliyah-pose-d_stagger.png` | 踉跄：身子往后（画面左边）倒，膝盖弯下去，两只手臂往两边甩开（死亡第一下） |
| 16 | `taliyah-pose-d_down.png` | 坐倒：一屁股坐在地上，两腿往前（画面右边）伸，身子往后仰，两只手撑在身后的地上，红垂带摊在地上（死亡） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`；冲浪的三个姿势再加 `2b_surf_picture.png`；有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 11 px squares (soles on y 1188) - THE STONEWEAVER GIRL: a young desert girl with TANNED skin, a BIG SWEPT-UP MASS OF BROWN HAIR piled high with a ROUND GOLD ORNAMENT (a cream stone in it), amber eyes, a CREAM STONE-PLATE MANTLE over her shoulders, a DARK INDIGO TUNIC with GOLD trim, a long RED COAT whose TWO RED PANELS hang to her shins each ending in GREY STONES, PURPLE SLEEVES with CREAM CUFFS, dark indigo leggings and BROWN BOOTS; B its HEAD shown 8x (29 x 30 squares); C a SKELETON on the same 1254 canvas and 11 px grid: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left, in front), BLUE = the FAR leg (image right), ORANGE = the NEAR arm (image left), PURPLE = the FAR arm (image right), GREY BOX = where the head goes, a BROWN ROUNDED BOX (surf poses only) = her big boulder, the red horizontal line = the ground; D the original character in this pose (copy the POSE, the arms and the panels' swing from it - never its 3D look, its realistic proportions or a turned back); E (surf poses) her boulder as drawn before: a big brown rock wrapped in RED CLOTH with a gold edge; F (if attached) the same skeleton drawn over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 11 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; feet that touch the ground on y 1188 (in the surf poses the boulder's bottom is on that line and her feet stand on its top).
COUNT THE SQUARES: the head 29 x 30 squares; each leg about 16 squares from the hip to the sole, each arm about 16 squares from the shoulder to the fingertips (short chibi arms), the boulder about 44 x 24 squares, exactly as in images A and E. Lay the body along the skeleton: the indigo tunic with its gold trim and the red coat along the green line, the stone mantle on the shoulders, each leg along its line (bending at the dots: the indigo legging and the brown boot - the SAME thickness, length and colours as in image A), each arm from its shoulder along its line (the arms grow from under the mantle, never floating; purple sleeve, cream cuff, tanned hand). The two red panels and their grey end stones are cloth: they swing with the pose but keep their length, width and stones. Never stretch or shorten a limb, never paste a straight leg turned as one block. The near side in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the face to the front-right, the piled brown hair and its gold ornament, both amber eyes at the same height, the small red mouth) - the same head in every pose, only moved, never turned, never redrawn as a profile or from behind. No arm or hand covers the face (raised arms go outside or in front of the hair's sides, never over the eyes or the mouth).
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no flying rocks, no rising stones, no mines, no wall, no dust, no motion lines), no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_wind: `SUMMON - leaning back a little, the FAR arm raised high above the head on the image right, palm up (a small stone floating over the hand), the NEAR arm swung back and down, the legs planted, the red panels swinging back.`
- a_throw: `THE FLICK - leaning forward to the image right, the FAR arm flung forward to the right with the hand open (the stone just thrown), the NEAR arm swung back, the far leg a step forward.`
- q_raise: `THE CALL - standing tall on her toes, the FAR arm stretched up to the upper right with the fingers spread (a string of rocks rising from the ground), the NEAR arm flung out to the lower left.`
- q_cast: `THE VOLLEY - leaning forward and low to the image right, the FAR arm pushed straight forward, palm out (the rocks shooting out one after another), the NEAR arm stretched back for balance; a lunge.`
- e_raise: `BOTH HANDS UP - both arms raised high in a V to the upper left and upper right (the hands outside the hair on either side, never over the face), the fingers spread holding up a spray of pebbles, standing tall.`
- e_sweep: `THE SCATTER - bent forward in a half crouch, both arms swept down and forward, the hands open (a spray of mines thrown onto the ground in front of her), the legs apart.`
- w_crouch: `PRESSING THE GROUND - crouched down, the FAR palm pressed on the ground in front of her (the ground about to erupt), the NEAR arm thrown up and back, the knees bent.`
- w_push: `THE SHOVE - risen, turned to the front-right, the FAR arm thrust out sideways to the image right, palm out (throwing the enemies), the NEAR arm drawn in before the chest, the legs planted.`
- r_call: `THE WALL - standing straight, the FAR arm raised straight up to the sky, the palm open (the wall rising from the ground), the NEAR arm opened out at her side, the red panels flying up.`
- surf1: `SURF 1 - crouching on her big boulder (wrapped in red cloth, like picture B), the FAR arm reaching forward to the image right, the NEAR arm swung back and down for balance, both feet on the boulder's top with the knees forward, the coat flying back.`
- surf2: `SURF 2 - as surf 1 on the boulder, lower and leaning further forward, the FAR arm forward and down, the coat and panels flying higher.`
- surf3: `SURF 3 - on the boulder, the body a little higher, the FAR arm opened to the upper right, the NEAR arm stretched back.`
- d_stagger: `STAGGER - reeling back to the image left, the knees buckling, both arms flung out to the sides.`
- d_down: `DOWN - sitting on the ground, both legs stretched forward to the image right, leaning back, both hands propped on the ground behind her, the red panels spread on the ground.`

## 交回前请检查

- **14 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 11 px**（和定稿一样）。
- **数格子**：头 29 × 30 格、每条腿从胯到脚底约 16 格、手臂约 16 格、冲浪石约 44 × 24 格，和定稿一样——腿或手臂画长了就重画。
- 每张都是定稿的同一个塔莉垭：**同一个头（照图 B，脸朝右前方、两只眼睛、金色发饰）**、同样粗的腿和手臂、同样的披肩和垂带；手臂从肩膀长出来，手没有盖住脸；姿势沿着骨架；着地的脚在 y 1188（冲浪：石头底在 y 1188，脚踩在石头顶上）；没有一张是背影或侧脸。
- 所有图没有特效、没有骨架线、没有网格线。

## 交付（`outputs/taliyah-poses/`）

- `taliyah-pose-a_wind.png`、`taliyah-pose-a_throw.png`、`taliyah-pose-q_raise.png`、`taliyah-pose-q_cast.png`、`taliyah-pose-e_raise.png`、`taliyah-pose-e_sweep.png`、`taliyah-pose-w_crouch.png`、`taliyah-pose-w_push.png`、`taliyah-pose-r_call.png`、`taliyah-pose-surf1.png`、`taliyah-pose-surf2.png`、`taliyah-pose-surf3.png`、`taliyah-pose-d_stagger.png`、`taliyah-pose-d_down.png`；原始生成图原样放 `outputs/taliyah-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/taliyah_poses_done.zip`。中间不要停，14 张都画完再交。

## 附图（压缩包 `taliyah_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分） |
| `1_head.png` | 定稿的头（8 倍）：每个姿势都照它逐格画 |
| `2_design.png` | 定稿（每格 11 px，脚底 y 1188） |
| `2b_surf_picture.png` | 第 0 步的 B：冲浪的大石头长什么样（只照石头，她的大小照定稿） |
| `3_a_wind_*` … `16_d_down_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |

## Claude 收到后（给 Claude 看）

- 量格子（应约 11 px），按格读回（design_singed_poses / design_aurora_poses 的做法：按头的大小定比例，头换成定稿的头），颜色对到定稿的调色板；**先在 8 倍下量每条腿和手臂的长短粗细，和定稿比**（codex-legs-need-skeletons），再拼进 rig_taliyah.py 的动作里，逐帧自查后才发合成 GIF。
- 动作安排（照英雄联盟，标签见 tools/kit/build_taliyah.py）：普攻 attack = a_wind → a_throw；石穿 skill = q_raise → q_cast；岩突 + 撒石阵 skill2 = e_raise → e_sweep → w_crouch → w_push；墙幔 ult = r_call → surf1-3（踩墙冲浪）；移动 run = surf1 → surf2 → surf3（被动冲浪）；死亡 dead = d_stagger → d_down；待机 = 定稿（hero_reels 做待机和 BP 动画）；受击 hit = 定稿后退一格闪白。
