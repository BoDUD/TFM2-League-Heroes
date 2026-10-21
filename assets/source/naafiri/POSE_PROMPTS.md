# 百裂冥犬 纳亚菲利：动作关键姿势（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 纳亚菲利和伙伴的造型用户已经定了（`0_design_naafiri.png`、`0_design_packmate.png`，就是你上一步画的 A-2 和 P-2 缩到游戏格子数）。这一步照**英雄联盟的动作**画**18 个关键姿势**，Claude 再用它们拼成动作帧。
> - 每个姿势附一张**参考图**（`<编号>_<名字>_guide.png`）：英雄联盟里那一帧，按 TFM2 的大头比例渲染、按造型的大小放在画布上，格子和地面线（红线）都画好了。**姿势、位置、大小照参考图**；**样子、颜色、格子大小照造型**（参考图只是 3D 渲染，不要照它的光影和细节）。
> - **一张图只画一只狗**。纳亚菲利每格 **11 px**（和 `0_design_naafiri.png` 一样，身高约 45 格），伙伴每格 **22 px**（和 `0_design_packmate.png` 一样，身高约 24 格）。画布 **1254 × 1254**，网格从左上角 (0, 0) 对齐。
> - **头和脸照造型**（`1_head_naafiri.png`、`1_head_packmate.png` 是两个头放大 8 倍）：纳亚菲利的红脸、白色口鼻斑纹、黄眼睛、白牙、嘴角的匕首骨柄；伙伴的骨头盔和刀刃、黄眼睛。头可以转、可以仰、可以张嘴，但**脸的画法和颜色不变**，**不要比造型的头大或小**。
> - **腿不能变形**：每条腿的粗细、长短和造型一样，关节往正确的方向弯（前腿的腕关节往前、后腿的跗关节往后），四条腿分得开，近处的腿全亮、远处的暗一档；**身子不要压扁到腿上**。

## 附图（压缩包 `naafiri_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_design_naafiri.png` / `0_design_packmate.png` | 造型（用户定的），在网格上，爪子踩红线：**样子、颜色、格子大小** |
| `1_head_naafiri.png` / `1_head_packmate.png` | 两个头放大 8 倍：**脸** |
| `<编号>_<名字>_guide.png` | 每个姿势的参考图（英雄联盟那一帧，按要画的大小放好）：**姿势、位置、大小** |
| `<编号>_<名字>_league.png` | 同一帧的大图：看清楚四条腿、头和尾巴怎么摆 |

## 姿势

| 参考图 | 名字 | 谁 | 画什么 |
|---|---|---|---|
| `2_crouch_guide.png` | **crouch** | 纳亚菲利，每格 11 px | 蓄势：后腿下蹲、前身微微抬起，头往前伸、嘴微张，刀刃鬃毛往后贴，尾巴在身后（普攻、大招的起手）；爪子踩在红线上 |
| `3_rear_guide.png` | **rear** | 纳亚菲利，每格 11 px | 人立张嘴：前身高高抬起、两只前爪离地，头仰起、嘴张到最大露出满口尖牙，刀刃鬃毛竖起（普攻出手前、E 剔骨本能起手）；爪子踩在红线上 |
| `4_lunge_guide.png` | **lunge** | 纳亚菲利，每格 11 px | 前扑撕咬：身子贴低往前伸到最长，头往前伸、咬下去，前腿往前探、后腿往后蹬，尾巴平伸在身后（普攻命中、扑中后撕咬）；爪子踩在红线上 |
| `5_fling_guide.png` | **fling** | 纳亚菲利，每格 11 px | 跃空甩匕首：整个身子跃起离地，弓成一道弧，头往前下方甩，嘴里的匕首甩出去的那一下（Q 暗裔犬牙）；离地（照参考图的高度） |
| `6_flare_guide.png` | **flare** | 纳亚菲利，每格 11 px | 压低张刃：前身压到最低、几乎贴地，后身抬高，刀刃鬃毛往前上方整片张开，头低着盯着前面（大招猎狗血性的起手）；爪子踩在红线上 |
| `7_dash_guide.png` | **dash** | 纳亚菲利，每格 11 px | 贴地飞扑：整个身子拉直成一条线往前飞，四条腿收在身下往前后伸直，刀刃鬃毛往后平贴，尾巴拉直在后面（大招飞扑、E 冲刺）；最低点离地约 3 格 |
| `8_rise_guide.png` | **rise** | 纳亚菲利，每格 11 px | 人立仰头：前身斜斜往上立起，头仰向前上方，前爪离地，后腿撑地，尾巴扬起（E 剔骨本能撕裂）；爪子踩在红线上 |
| `9_howl_guide.png` | **howl** | 纳亚菲利，每格 11 px | 仰天长嚎：坐在后腿上，前腿撑直，脖子和头笔直朝天，嘴张开嚎叫，刀刃鬃毛竖起（大招暴吼、阵亡第一下）；爪子踩在红线上 |
| `10_lie_guide.png` | **lie** | 纳亚菲利，每格 11 px | 趴倒：整个身子侧趴在地上，四条腿伸向一边，头贴在地上（朝画面右边），刀刃鬃毛平贴，尾巴拖在地上（阵亡）；爪子踩在红线上 |
| `11_run1_guide.png` | **run1** | 纳亚菲利，每格 11 px | 奔跑 1：前腿往前伸、后腿往后蹬，身子拉长（四足奔跑的腾空伸展）；爪子踩在红线上 |
| `12_run2_guide.png` | **run2** | 纳亚菲利，每格 11 px | 奔跑 2：前腿着地往后收，后腿往前收到肚子下面，身子缩短拱起；爪子踩在红线上 |
| `13_run3_guide.png` | **run3** | 纳亚菲利，每格 11 px | 奔跑 3：后腿着地往后蹬，前腿离地往前伸；爪子踩在红线上 |
| `14_run4_guide.png` | **run4** | 纳亚菲利，每格 11 px | 奔跑 4：四条腿都收在身下，身子腾空、最高；最低点离地约 2 格 |
| `15_p_run1_guide.png` | **p_run1** | 伙伴，每格 22 px | 伙伴奔跑 1：前腿往前伸、后腿往后蹬；爪子踩在红线上 |
| `16_p_run2_guide.png` | **p_run2** | 伙伴，每格 22 px | 伙伴奔跑 2：前腿着地往后收、后腿往前收；爪子踩在红线上 |
| `17_p_run3_guide.png` | **p_run3** | 伙伴，每格 22 px | 伙伴奔跑 3：后腿着地往后蹬、前腿往前伸；爪子踩在红线上 |
| `18_p_run4_guide.png` | **p_run4** | 伙伴，每格 22 px | 伙伴奔跑 4：四条腿收在身下、身子最高；最低点离地约 1 格 |
| `19_p_bite_guide.png` | **p_bite** | 伙伴，每格 22 px | 伙伴扑咬：往前下方扑下去，头和头盔的刀刃朝前下方，后腿蹬直（伙伴撕咬目标）；爪子踩在红线上 |

## 提示词（同一段，每个姿势换最后一句）

附 `0_design_*`、`1_head_*` 和这个姿势的 `guide`、`league` 两张图。**用 image_gen 画。**

```text
Attached images: 0N the LEADER's approved pixel-art design at game size - a big lean hound on four legs: a crimson-red wolf head with a white blaze on the snout, yellow eyes, white fangs and a bone dagger hilt at the corner of the mouth, a slate blue-teal armoured hide with crimson veins, a big fan of curved dark-purple blades rimmed in mint green rising from the neck and shoulders, teal spine spikes, crimson legs, black claws and a long whip tail; 0P the PACKMATE's approved design - a smaller lean crimson hound with a slate-grey bony helmet whose curved blade juts forward over the snout, one yellow eye, black claws and a thin tail with a grey-blue end; 1N and 1P their heads enlarged 8x; the GUIDE: League's own frame of the pose, a 3D render shown with the game's big-headed proportions at exactly the size and place to draw it on the grid, the red line the ground; the LEAGUE image: the same frame large, to read the legs, the head and the tail.
Draw with the image generator ONE clean pixel-art picture: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), BIG SQUARES aligned on one straight grid from the canvas corner (the square size is given below - the SAME as the design's), ONE hound. Copy the POSE, the PLACE and the SIZE from the guide; copy the LOOK, the COLOURS, the SQUARE SIZE and the HEAD from the design - never the render's 3D shading or extra detail.
The head and face exactly as the design's (the same squares, the same colours; turned, raised or with the jaws opened as the pose needs, never bigger or smaller). Every leg as thick and as long as the design's, its joints bending the right way (the fore legs' wrists forward, the hind legs' hocks back), the four legs clearly apart, the near legs in full tone and the far legs a step darker, the body never squashed onto the legs. One continuous 1-square near-black outline round the figure; every material in its own 2-4 flat shades; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No spell effects (no thrown dagger in flight, no blood, no trails, no glow), no background, no ground, no cast shadow, no text, no grid lines.
```

最后一句，按要画的那一个姿势换：

- **crouch**（`naafiri-pose-crouch.png`）：
  ```text
  POSE CROUCH: CROUCH - gathering to spring: the hind legs bent low, the front a little raised, the head stretched forward with the jaws slightly open, the blade mane laid back, the tail behind her. Draw THE LEADER (images 0N and 1N) in exactly the pose of guide image 2, at the guide's place and size, every square exactly 11 px, its paws on the red line.
  ```
- **rear**（`naafiri-pose-rear.png`）：
  ```text
  POSE REAR: REAR - rearing up on the hind legs, both fore paws off the ground, the head thrown up with the jaws opened as wide as they go (all the fangs and the dark red mouth), the blade mane standing up. Draw THE LEADER (images 0N and 1N) in exactly the pose of guide image 3, at the guide's place and size, every square exactly 11 px, its paws on the red line.
  ```
- **lunge**（`naafiri-pose-lunge.png`）：
  ```text
  POSE LUNGE: LUNGE - stretched out low and long, the head thrust forward biting, the fore legs reaching forward, the hind legs pushing back, the tail stretched out level behind. Draw THE LEADER (images 0N and 1N) in exactly the pose of guide image 4, at the guide's place and size, every square exactly 11 px, its paws on the red line.
  ```
- **fling**（`naafiri-pose-fling.png`）：
  ```text
  POSE FLING: FLING - leaping off the ground with the body arched in a curve, the head whipped forward and down as she flings the dagger from her jaws, the legs tucked under her, the tail streaming behind. Draw THE LEADER (images 0N and 1N) in exactly the pose of guide image 5, at the guide's place and size, every square exactly 11 px, its lowest point as high above the red line as in the guide.
  ```
- **flare**（`naafiri-pose-flare.png`）：
  ```text
  POSE FLARE: FLARE - the front pressed down almost to the ground, the hindquarters raised, the whole blade mane fanned out forward and up, the head low and staring ahead (the pounce's wind-up). Draw THE LEADER (images 0N and 1N) in exactly the pose of guide image 6, at the guide's place and size, every square exactly 11 px, its paws on the red line.
  ```
- **dash**（`naafiri-pose-dash.png`）：
  ```text
  POSE DASH: DASH - flying forward stretched into one straight line, the four legs stretched forward and back under her, the blade mane swept flat backwards, the tail straight out behind (the pounce and the dash). Draw THE LEADER (images 0N and 1N) in exactly the pose of guide image 7, at the guide's place and size, every square exactly 11 px, its lowest point about 3 squares above the red line.
  ```
- **rise**（`naafiri-pose-rise.png`）：
  ```text
  POSE RISE: RISE - reared diagonally up on the hind legs, the head raised forward and up, the fore paws off the ground, the tail lifted (Eviscerate's shred). Draw THE LEADER (images 0N and 1N) in exactly the pose of guide image 8, at the guide's place and size, every square exactly 11 px, its paws on the red line.
  ```
- **howl**（`naafiri-pose-howl.png`）：
  ```text
  POSE HOWL: HOWL - sitting back on the hind legs with the fore legs braced straight, the neck and head pointed straight up at the sky, the jaws open howling, the blade mane standing up (the roar). Draw THE LEADER (images 0N and 1N) in exactly the pose of guide image 9, at the guide's place and size, every square exactly 11 px, its paws on the red line.
  ```
- **lie**（`naafiri-pose-lie.png`）：
  ```text
  POSE LIE: LIE - fallen and lying flat on her side on the ground, the four legs stretched out to one side, the head resting on the ground at the image right, the blade mane flat, the tail lying along the ground. Draw THE LEADER (images 0N and 1N) in exactly the pose of guide image 10, at the guide's place and size, every square exactly 11 px, its paws on the red line.
  ```
- **run1**（`naafiri-pose-run1.png`）：
  ```text
  POSE RUN1: RUN 1 - galloping: the fore legs reaching forward, the hind legs kicked back, the body stretched long. Draw THE LEADER (images 0N and 1N) in exactly the pose of guide image 11, at the guide's place and size, every square exactly 11 px, its paws on the red line.
  ```
- **run2**（`naafiri-pose-run2.png`）：
  ```text
  POSE RUN2: RUN 2 - galloping: the fore paws on the ground drawing back, the hind legs swung forward under the belly, the body gathered and arched. Draw THE LEADER (images 0N and 1N) in exactly the pose of guide image 12, at the guide's place and size, every square exactly 11 px, its paws on the red line.
  ```
- **run3**（`naafiri-pose-run3.png`）：
  ```text
  POSE RUN3: RUN 3 - galloping: the hind paws on the ground pushing back, the fore legs off the ground reaching forward. Draw THE LEADER (images 0N and 1N) in exactly the pose of guide image 13, at the guide's place and size, every square exactly 11 px, its paws on the red line.
  ```
- **run4**（`naafiri-pose-run4.png`）：
  ```text
  POSE RUN4: RUN 4 - galloping: all four legs gathered under her, the body off the ground at its highest. Draw THE LEADER (images 0N and 1N) in exactly the pose of guide image 14, at the guide's place and size, every square exactly 11 px, its lowest point about 2 squares above the red line.
  ```
- **p_run1**（`naafiri-pose-p_run1.png`）：
  ```text
  POSE P_RUN1: PACKMATE RUN 1 - the fore legs reaching forward, the hind legs kicked back. Draw THE PACKMATE (images 0P and 1P) in exactly the pose of guide image 15, at the guide's place and size, every square exactly 22 px, its paws on the red line.
  ```
- **p_run2**（`naafiri-pose-p_run2.png`）：
  ```text
  POSE P_RUN2: PACKMATE RUN 2 - the fore paws down drawing back, the hind legs swung forward. Draw THE PACKMATE (images 0P and 1P) in exactly the pose of guide image 16, at the guide's place and size, every square exactly 22 px, its paws on the red line.
  ```
- **p_run3**（`naafiri-pose-p_run3.png`）：
  ```text
  POSE P_RUN3: PACKMATE RUN 3 - the hind paws down pushing back, the fore legs reaching forward. Draw THE PACKMATE (images 0P and 1P) in exactly the pose of guide image 17, at the guide's place and size, every square exactly 22 px, its paws on the red line.
  ```
- **p_run4**（`naafiri-pose-p_run4.png`）：
  ```text
  POSE P_RUN4: PACKMATE RUN 4 - all four legs gathered under it, the body at its highest. Draw THE PACKMATE (images 0P and 1P) in exactly the pose of guide image 18, at the guide's place and size, every square exactly 22 px, its lowest point about 1 squares above the red line.
  ```
- **p_bite**（`naafiri-pose-p_bite.png`）：
  ```text
  POSE P_BITE: PACKMATE BITE - diving forward and down onto its prey, the head and the helmet's blade pointing forward-down, the hind legs pushed straight. Draw THE PACKMATE (images 0P and 1P) in exactly the pose of guide image 19, at the guide's place and size, every square exactly 22 px, its paws on the red line.
  ```

## 交回前请检查

- **全部是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；每张一只狗。
- 格子：纳亚菲利每格 11 px，伙伴每格 22 px（数一下台阶：格子画小了就重画）；大小、位置照参考图，爪子踩红线（飞扑、跃空的那几张离地）。
- 头和脸和造型一样（白色斑纹、黄眼睛、白牙、匕首骨柄；伙伴的头盔刀刃）；腿不变形、关节方向对、四条腿分得开；刀刃鬃毛一片片分开、薄荷绿边清楚。
- 交付：`outputs/naafiri-poses/naafiri-pose-<名字>.png`（18 张，名字照上表）；原始生成图原样放 `outputs/naafiri-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/naafiri_poses_done.zip`。中间不要停，全部画完再交。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/naafiri/codex_poses/`，按造型的头找每张的头（design_shyvana_poses 的做法：头的格子数 / 读回比例），读回到造型的格子和颜色，造型的头贴回去（一张脸用在所有帧），8 倍下查腿（`codex-legs-need-skeletons`、`rig-deformation-checks`）。
- 动作帧（`tools/art/rig_naafiri.py`，rig_shyvana 的做法）：她的每个标签都画两只伙伴（伙伴跑步、扑咬的姿势跟着她的动作），再出一套四只的 `p4_*`（附加包暴吼时用）；标签：idle run attack hit dead skill skill2 ult ult_b。
