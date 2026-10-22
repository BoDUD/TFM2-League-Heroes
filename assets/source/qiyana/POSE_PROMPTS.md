# 元素女皇 奇亚娜：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 奇亚娜的造型用户已经定稿（`2_design.png`，你上一轮画的 A-1：3/4 正面朝右的高傲女王——暖棕皮肤、银白长发和齐刘海、金王冠嵌翠绿宝石、白玉尖冠、琥珀金眼睛和黑眼线、翠绿金珠项圈、青绿抹胸短裙加金边和墨绿裙摆、金臂环手镯、深棕紧身裤和金三角纹、紫棕凉鞋，近侧的手握着竖在身边的大圆环刀刃——深色弯刃、青绿内圈、金箍、玫瑰铜护手、两颗白玉水晶刃头）。英雄联盟里她每个动作都把圆环抡起来——抡到身后、扫到身前、平举、拖着突进、举过头、砸地、扛在背上跑、掉在地上——这些靠挪动定稿本身的部件摆不出来，所以请你按骨架画 **15 个姿势，每个一张图**（11 个动作姿势 + 4 帧跑步）。待机、挨打我从定稿本身来做，不用画。
> - **每张图都是同一个奇亚娜**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 13 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1196**），网格从画布左上角对齐。
> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到脖子根），**红线 = 近侧的腿（画面左边那条，在前面、颜色全亮）**，**蓝线 = 远侧的腿（画面右边那条，暗一档）**，**橙线 = 近侧的手臂（画面左边）**，**紫线 = 远侧的手臂（画面右边）**；**黄色的椭圆 = 圆环刀刃**（看成椭圆是因为它侧过来或放平了：椭圆越扁，圆环越接近平放或侧对着我们），**青色的两段 = 两颗白玉水晶刃头**的位置；握环的那只手臂的末端就在椭圆上（那里是手握着环的地方）；**灰框 = 头的位置**。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。**腿、手臂的长短粗细和定稿一样**（骨架就是按定稿量的），关节处弯折，**不要拉长或压短，不要把直的腿整块转个方向贴上去**。手臂从肩膀长出来，不能悬空。**圆环和定稿一样大、一样粗**（只是转了方向：竖着、放平、侧过来、斜着），环中间是空的。
> - **头一格一格照 `1_head.png` 画在灰框里**（连尖冠和头发 28 × 31 格，同样朝右前方、两只琥珀金眼睛都看得见）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。手臂、手、圆环**不要盖住脸**（眼睛和嘴）。
> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。英雄联盟的奇亚娜是正常比例、圆环比她还大；我们的是 Q 版大头、圆环小一些：身子短、手臂短，**圆环不要举到脸前面，手臂往两边、往前、往后伸，不要从脸前面横过去**。

## 15 个姿势

| 图 | 文件 | 姿势 |
|---|---|---|
| 3 | `qiyana-pose-a_wind.png` | 挥环蓄势：远侧腿站直，近侧腿屈膝往前抬起，身子微微后仰，近侧手臂往左后方把圆环抡到身后（圆环几乎放平、在她身后左边，和肩一样高），远侧手臂往前平伸（普攻起手） |
| 4 | `qiyana-pose-a_strike.png` | 挥环砍出：往前跃起（脚离地约 3 格），身子前倾，近侧手臂把圆环往前抡到她身前右边（圆环斜着、下沿在她腰的高度），远侧手臂往后甩开，近侧腿屈膝在前、远侧腿往后伸（普攻出手） |
| 5 | `qiyana-pose-q_wind.png` | 横扫蓄势：弓步压低，前腿（远侧）屈膝、后腿（近侧）往后伸，身子前倾，近侧手臂往后把圆环拖在身后左边（圆环放平、贴近地面），远侧手臂弯在身前（Q 起手） |
| 6 | `qiyana-pose-q_sweep.png` | 横扫：身子往前一拧，近侧手臂把圆环从身后抡到她身前右边（圆环竖起来正对着我们、在她身前右边），远侧手臂往左后方甩开，两腿大开（Q 打出） |
| 7 | `qiyana-pose-q_end.png` | 收势：站直，近侧手臂把圆环平平地举在身前右边（圆环侧过来看成一条斜的长扁环，和肩一样高），远侧手臂往右上方张开，远侧腿屈膝抬起（Q 收尾） |
| 8 | `qiyana-pose-e_dash.png` | 突进：身子压得很低往前冲（几乎和地面平行，头在右前方），近侧手臂把圆环平平地拖在身后（侧过来看成一条斜的长扁环），前腿（远侧）屈膝、后腿（近侧）往后蹬直（E 突进） |
| 9 | `qiyana-pose-e_hit.png` | 落地斩：低低的大弓步落地，近侧手臂把圆环往前平平地砍出去（圆环放平、在她身前右边，腰的高度），远侧手臂往后甩，后腿（近侧）往后伸直（E 砍中） |
| 10 | `qiyana-pose-r_leap.png` | 跃起举环：笔直地跳起来（脚离地约 10 格），两腿屈膝收起，近侧手臂把圆环举到身后上方（圆环竖着、在她头后面偏左，环的下沿在肩膀的高度，不挡脸），远侧手臂往右上方张开（R 起跳） |
| 11 | `qiyana-pose-r_slam.png` | 砸环：落地前倾，近侧手臂把圆环从上往前下方狠狠砸出去（圆环斜着、在她身前右边，下沿碰到地面），远侧手臂往左后方甩开，前腿（远侧）屈膝、后腿（近侧）往后伸（R 砸出冲击波） |
| 12 | `qiyana-pose-run1.png` | 跑步 1（远侧腿在前着地，近侧腿往后抬起）：身子前倾，近侧手把圆环斜扛在背后（从左上到右下的一条斜扁环），远侧手臂在身前摆 |
| 13 | `qiyana-pose-run2.png` | 跑步 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格，圆环同样斜扛在背后 |
| 14 | `qiyana-pose-run3.png` | 跑步 3（近侧腿在前着地，远侧腿往后抬起） |
| 15 | `qiyana-pose-run4.png` | 跑步 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格 |
| 16 | `qiyana-pose-d_fall.png` | 踉跄倒下：身子往左后方倒，膝盖弯下去，近侧手臂垂下、圆环从手里滑落到她身后左边的地上（圆环斜着、下沿碰地），远侧手捂着胸口（死亡第一下） |
| 17 | `qiyana-pose-d_lie.png` | 跪坐倒地：坐到地上，近侧腿跪着折在身下，远侧腿立起膝盖，近侧手撑在身边的地上，远侧手搭在膝盖上，头低着；圆环平躺在她身后左边的地上（侧过来看成一条贴地的扁环）（死亡） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 13 px squares (soles on y 1196) - a chibi PROUD YOUNG EMPRESS with a BIG head: warm tan-brown skin, long wavy silver-white hair with straight bangs, a gold tiara with emerald gems and a tall white-jade crest, amber-gold eyes with thick black eyeliner, an emerald-and-gold bead choker, a turquoise-teal strapless short dress with gold trim and a dark green flap behind, gold armlets and bracelets, dark brown-black leggings with gold triangle markings, purple-brown sandals, and her HUGE RING BLADE held in her hand (a dark brown-black curved blade, a teal inner rim, gold and teal bands, rose-copper guards, two white-jade crystal blade heads at opposite points); B its HEAD with the crest and the hair shown 8x (28 squares wide, 31 tall); C a SKELETON on the same 1254 canvas and 13 px grid: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left, in front), BLUE = the FAR leg (image right), ORANGE = the NEAR arm (image left), PURPLE = the FAR arm (image right), the YELLOW ELLIPSE = the RING BLADE as it is seen in this pose (a flatter ellipse = the ring turned flat or edge-on; the ring keeps the design's size and thickness), the two CYAN strokes = its two crystal heads, the arm that ends on the ellipse holds the ring there, GREY BOX = where the head goes, the red horizontal line = the ground; D the original character in this pose, 3/4 view facing right (copy the POSE and the ring's swing from it, never its 3D look, its realistic proportions or its oversized ring); E (if attached) the same skeleton drawn over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 13 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; feet that touch the ground on y 1196.
Lay the body along the skeleton: the torso along the green line, each leg along its line (bending at the dots: the dark leggings with their gold triangles, the purple-brown sandal - the SAME thickness, length and colours as in image A), each arm from its shoulder along its line (the arms grow from the shoulders, never floating; the gold armlet and bracelet stay on), the hand on the ellipse GRIPPING the ring there. THE RING drawn along the yellow ellipse at the design's size and blade thickness, its middle EMPTY, its teal inner rim, gold bands and rose-copper guards, its two white-jade crystal heads where the cyan strokes are; turned flat or edge-on it reads as a long narrow oval or a thick curved bar. Never stretch or shorten a limb, never paste a straight leg turned as one block. The near side in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the face to the front-right, both amber-gold eyes with their eyeliner, the mouth, the gold tiara, the white-jade crest, the silver-white hair) - the same head in every pose, only moved, never turned, never redrawn as a profile. No arm, hand or part of the ring covers the face (the eyes and the mouth).
The same colours as image A; one continuous 1-square near-black outline (round the ring's inner edge too); no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no elemental glow, no leaves, no water, no rocks, no shock waves, no motion trails), no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_wind: `WIND-UP - standing on the FAR leg, the NEAR knee lifted forward, the body leaning back a little, the NEAR arm swinging the ring back behind her to the image left (the ring almost flat, at shoulder height behind her), the far arm stretched forward level.`
- a_strike: `STRIKE - springing forward (the feet about 3 squares up), the body leaning forward, the NEAR arm sweeping the ring round to the front at the image right (the ring tilted, its lower edge at her waist), the far arm flung back, the near knee bent forward, the far leg stretched back.`
- q_wind: `SWEEP WIND-UP - a deep low lunge, the front (far) knee bent, the back (near) leg stretched out behind, the body leaning forward, the NEAR arm dragging the ring low behind her to the image left (the ring flat, close to the ground), the far arm bent before her.`
- q_sweep: `SWEEP - twisting forward, the NEAR arm sweeping the ring from behind round to the front at the image right (the ring upright and facing us, beside her on the image right), the far arm flung back to the upper left, the legs wide apart.`
- q_end: `FOLLOW-THROUGH - standing tall, the NEAR arm holding the ring out level in front at the image right (the ring seen edge-on as a long flat oval at shoulder height), the far arm flung up and out to the upper right, the far knee lifted.`
- e_dash: `DASH - dashing forward very low, the body almost level, the head at the front (image right), the NEAR arm trailing the ring flat behind her (seen edge-on as a long flat oval), the front (far) knee bent, the back (near) leg pushed straight out behind.`
- e_hit: `LANDING SLASH - landed in a low wide lunge, the NEAR arm slashing the ring forward flat (the ring flat in front at the image right, at waist height), the far arm flung back, the back (near) leg stretched out.`
- r_leap: `LEAP - leaping straight up (the feet about 10 squares up), both knees tucked up, the NEAR arm raising the ring up behind her (upright, behind her head toward the image left, its lower edge at her shoulders, never over the face), the far arm flung up and out to the upper right.`
- r_slam: `SLAM - landing and leaning forward, the NEAR arm smashing the ring down forward (tilted, in front at the image right, its lower edge touching the ground), the far arm flung back to the upper left, the front (far) knee bent, the back (near) leg stretched out.`
- run1: `RUN 1 - running: the FAR leg forward with its foot landing, the NEAR leg kicked up behind her, the body leaning forward, the NEAR hand carrying the ring slung diagonally across her back (a flat oval from the upper left to the lower right behind her), the far arm swinging before her.`
- run2: `RUN 2 - running: the near leg under the body carrying her, the FAR knee lifted forward, the body one square higher, the ring slung diagonally across her back as before, the far arm swinging back.`
- run3: `RUN 3 - running: the NEAR leg forward with its foot landing, the FAR leg kicked up behind her, the body leaning forward, the ring slung diagonally across her back, the far arm swinging back.`
- run4: `RUN 4 - running: the far leg under the body carrying her, the NEAR knee lifted forward, the body one square higher, the ring slung diagonally across her back, the far arm swinging before her.`
- d_fall: `STAGGER - falling back toward the image left, the knees buckling, the NEAR arm hanging with the ring slipping from her hand onto the ground behind her on the image left (tilted, its lower edge on the ground), the far hand clutching her chest.`
- d_lie: `DOWN - sunk down sitting on the ground, the near leg folded under her with its knee on the ground, the far knee raised, the near hand propped on the ground beside her, the far hand resting on the raised knee; the ring lying flat on the ground behind her on the image left (seen as a flat oval on the ground).`

## 交回前请检查

- **15 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 13 px**（和定稿一样，数一数腿的粗细：和定稿一样宽）。
- 每张都是定稿的同一个奇亚娜：**同一个头（照图 B，脸朝右前方、两只琥珀金眼睛和黑眼线、金王冠、白玉尖冠、银白头发）**、同样粗的腿和手臂；**圆环和定稿一样大、一样粗**，中间空，两颗白玉刃头，握着它的手在环上；手臂从肩膀长出来，手和圆环没有盖住脸；姿势沿着骨架；着地的脚在 y 1196。
- 所有图没有特效、没有骨架线、没有网格线。

## 交付（`outputs/qiyana-poses/`）

- `qiyana-pose-a_wind.png`、`qiyana-pose-a_strike.png`、`qiyana-pose-q_wind.png`、`qiyana-pose-q_sweep.png`、`qiyana-pose-q_end.png`、`qiyana-pose-e_dash.png`、`qiyana-pose-e_hit.png`、`qiyana-pose-r_leap.png`、`qiyana-pose-r_slam.png`、`qiyana-pose-run1.png`、`qiyana-pose-run2.png`、`qiyana-pose-run3.png`、`qiyana-pose-run4.png`、`qiyana-pose-d_fall.png`、`qiyana-pose-d_lie.png`；原始生成图原样放 `outputs/qiyana-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/qiyana_poses_done.zip`。中间不要停，15 张都画完再交。

## 附图（压缩包 `qiyana_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分，黄椭圆 = 圆环） |
| `1_head.png` | 定稿的头（8 倍）：每个姿势都照它逐格画 |
| `2_design.png` | 定稿（每格 13 px，脚底 y 1196） |
| `3_a_wind_*` … `17_d_lie_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |

## Claude 收到后（给 Claude 看）

- 量格子（应约 13 px），按格读回（design_neeko_poses / design_ksante_poses 的做法：按身体面积定比例，头换成定稿的头），颜色对到定稿的调色板；**先在 8 倍下量每条腿、手臂和圆环的长短粗细，和定稿比**（codex-legs-need-skeletons），再拼进 rig_qiyana.py 的动作里，逐帧自查后才发合成 GIF。
- 动作安排（照英雄联盟）：普攻 = a_wind → a_strike → 定稿；Q（skill，四种元素共用姿势，特效画进帧里）= q_wind → q_sweep → q_end；E（skill2）= e_dash（突进）→ e_hit；R（ult）= r_leap → r_slam；死亡 = d_fall → d_lie；跑 = run1–4；待机 = 定稿一帧；受击 = 定稿后退一格闪白。
