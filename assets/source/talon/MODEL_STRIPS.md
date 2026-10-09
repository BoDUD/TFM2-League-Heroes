# 泰隆：动作帧（第 2 步，给 Codex 的提示词）

> **一帧一张图。** 按 `design/talon_design.png`（用户已定稿的游戏精灵，8 倍）的样子，照英雄联盟原版的每一帧动作，把泰隆的 9 个动作共 57 帧**逐帧单独画**：每帧一张 960×896 的透明 PNG（120×112 格 × 8 倍），画在 `frames/<动作>_<帧号>/1_target.png` 的位置上。
> - **长相、颜色、大小都和定稿一样**：站直时约 42 格高；蓝紫兜帽 + 额前银色刀刃护额；**不画眼睛**——护额下面是一条黑色兜帽阴影，只露下半张脸（鼻子、嘴、下巴）；三层银肩甲；锈红披风带银刀尖；近手一把长长的银色腕刃；蓝紫衣裤、青色腰布、金扣；深枪灰护胫和银护膝。
> - **姿势照 `2_league.png`**（同一帧的英雄联盟原版，同位置同比例）：身体、手臂、腿、披风怎么摆就怎么画；只抄姿势，不抄 3D 的光影。
> - **大小和位置照 `1_target.png`**：红线 = 地面（脚踩在线上，线下面一格都不能画），蓝十字 = 站立点，淡灰剪影 = 这一帧的姿势和大小。
> - **像素规则**：每格严格 8×8、从画布左上角开始对齐同一网格；不抗锯齿、不模糊、不渐变；只用 `design/palette.png` 里的颜色；外面一圈 1 格近黑描边；像定稿那样大块平涂。透明背景；不画特效、飞刀、残影、拖尾、影子、文字。
> - **跑步 8 帧特别规则**：上半身（头、肩甲、上衣、披风上半部）**照 `3_upper_body.png` 原样抄**，不要重画、不要变形，最多整体上下移 1 格；只画腿（交叉步，两只脚一前一后明显错开）和披风下摆的摆动。
> - 交付到 `outputs/talon-strips/`：每帧一张 `<动作>_<帧号>.png`（如 `attack_03.png`，960×896 透明），外加 `HANDOFF.md`（**最后写**，列出所有交付的文件），最好打成 `talon_strips_done.zip`。画不完可以分几次交，每次都写 HANDOFF。

## 每个动作

| 动作 | 帧数 | 每帧毫秒 | 命中 / 出手帧 |
|---|---|---|---|
| `run`（跑步） | 8 | 121 121 121 121 121 121 121 121 | — |
| `attack`（普攻） | 5 | 60 50 80 80 110 | 第 3 帧 |
| `skill`（W 斩草除根） | 6 | 50 50 80 70 70 90 | 第 3 帧 |
| `skill2`（Q 跃击） | 7 | 60 50 60 80 70 80 90 | 第 4 帧 |
| `skill2_stab`（Q 近身回旋斩） | 6 | 50 50 70 70 70 90 | 第 3 帧 |
| `skill_e`（E 翻越） | 7 | 60 60 60 60 60 70 90 | 第 5 帧 |
| `ult`（R 刀锋旋转） | 8 | 50 50 60 60 60 60 60 90 | 第 3 帧 |
| `hit`（受击） | 2 | 120 120 | — |
| `dead`（死亡） | 8 | 100 100 100 120 120 150 200 500 | — |

## 逐帧说明（每帧附图：`frames/<动作>_<帧号>/` 里的 1_target、2_league；跑步多一张 3_upper_body）

### run（跑步）

- `run_01`：压低身子冲刺，左脚（近侧）在前落地、右脚在后蹬地  
  *low sprint: near (image-left) foot planted in front, far foot pushing off behind*
- `run_02`：近脚向后滑，远脚离地往前收  
  *near foot sliding back, far foot lifting and swinging forward*
- `run_03`：两腿交叉经过身体下方，远脚抬到膝盖高  
  *legs passing under the body, the far foot raised to knee height*
- `run_04`：远脚向前伸出、准备落地，近脚在后面蹬起  
  *far foot reaching forward to land, near foot pushing off behind*
- `run_05`：远脚在前落地、近脚在后蹬地（第 1 帧的左右对调）  
  *far foot planted in front, near foot pushing off behind (frame 1 mirrored legs)*
- `run_06`：远脚向后滑，近脚离地往前收  
  *far foot sliding back, near foot lifting and swinging forward*
- `run_07`：两腿交叉经过身体下方，近脚抬到膝盖高  
  *legs passing under the body, the near foot raised to knee height*
- `run_08`：近脚向前伸出、准备落地，远脚在后面蹬起  
  *near foot reaching forward to land, far foot pushing off behind*

### attack（普攻）

- `attack_01`：蓄力：身子往后收，近手连长刃拉到身后  
  *wind-up: the body draws back, the near hand pulls the wrist blade behind*
- `attack_02`：开始前冲，近手往前带  
  *starting the lunge, the near hand coming forward*
- `attack_03`：**出刀（命中帧）**：身体前倾，近手笔直向前，长刃平刺到胸口高度、刀尖指向画面右侧  
  ***THE HIT**: leaning in, the near arm straight forward, the long wrist blade stabbing horizontally at chest height, tip to image right*
- `attack_04`：收势：手臂开始往回收，披风被带起  
  *follow-through: the arm starts to come back, the cape swings up*
- `attack_05`：回到待机姿势  
  *back to the idle pose*

### skill（W 斩草除根）

- `skill_01`：双手交叉收到胸前（把刀片攥在手里）  
  *both hands cross before the chest, gathering the blades*
- `skill_02`：近手向后拉开，身体扭转蓄力  
  *the near hand draws back, the torso winds up*
- `skill_03`：**甩出（出手帧）**：近手向前横扫甩出，手臂伸直，披风向两侧张开（飞出去的刀片不用画，特效另画）  
  ***THE THROW**: the near arm sweeps forward and out, straight; the cape flares to both sides (do NOT draw the flying blades - effects come later)*
- `skill_04`：披风上的刀片向后张开成扇形，手停在前面  
  *the cape's blades fanned out behind, the hand still forward*
- `skill_05`：披风开始落下，手往回收  
  *the cape settling, the hand coming back*
- `skill_06`：回到待机姿势  
  *back to the idle pose*

### skill2（Q 跃击）

- `skill2_01`：跃起在半空，身体蜷起，长刃举过头顶  
  *leaping, high in the air, body tucked, the blade raised over the head*
- `skill2_02`：继续上升，身体前倾，长刃举高准备下刺  
  *still rising, leaning forward, the blade high, ready to strike down*
- `skill2_03`：开始下落，长刃指向前下方  
  *coming down, the blade pointing forward and down*
- `skill2_04`：**落地刺击（命中帧）**：落地半蹲，长刃向前下方刺出，披风连同上面所有刀片向上张开成扇形  
  ***THE STRIKE (landing)**: landing in a crouch, the blade stabbed forward and down, the cape with all its blades fanned UP behind him*
- `skill2_05`：冲击：身子压得最低，披风落下  
  *impact: the lowest crouch, the cape coming down*
- `skill2_06`：起身，长刃收回身侧  
  *rising, the blade back at his side*
- `skill2_07`：回到待机姿势  
  *back to the idle pose*

### skill2_stab（Q 近身回旋斩）

- `skill2_stab_01`：下蹲蓄力  
  *crouching wind-up*
- `skill2_stab_02`：跳起开始旋转，两臂张开  
  *jumping into a spin, arms spread*
- `skill2_stab_03`：**回旋斩（命中帧）**：半空中旋转，长刃横扫过身前  
  ***THE SPIN SLASH**: spinning in the air, the blade sweeping across his front*
- `skill2_stab_04`：继续旋转，披风甩成一圈  
  *the spin continues, the cape whirling round him*
- `skill2_stab_05`：落地  
  *landing*
- `skill2_stab_06`：回到待机姿势  
  *back to the idle pose*

### skill_e（E 翻越）

- `skill_e_01`：下蹲准备起跳，披风上的刀片竖起  
  *crouching to jump, the cape's blades raised*
- `skill_e_02`：向上跃起，一条腿伸直  
  *springing up, one leg stretched*
- `skill_e_03`：空中蜷身翻转  
  *tucked, turning over in the air*
- `skill_e_04`：继续翻转，头朝下方  
  *turning over, head low*
- `skill_e_05`：**落地（落点帧）**：半蹲落地，披风在后面拖开  
  ***LANDING**: landing in a crouch, the cape trailing behind*
- `skill_e_06`：起身，近手长刃指向前方  
  *rising, the near blade pointing forward*
- `skill_e_07`：回到待机姿势  
  *back to the idle pose*

### ult（R 刀锋旋转）

- `ult_01`：深蹲，身体蜷起  
  *a deep crouch, body coiled*
- `ult_02`：起身开始旋转，近手长刃甩到身后  
  *rising into a spin, the near blade swung behind*
- `ult_03`：**刀锋张开（出手帧）**：旋转中，披风完全张开，上面的刀片向四周呈扇形甩出（飞出去的刀片不用画）  
  ***THE BLADES OUT**: spinning, the cape fully spread, its blades fanned out all round him (do NOT draw flying blades)*
- `ult_04`：继续旋转，背对画面  
  *spinning on, back to the viewer*
- `ult_05`：继续旋转，披风甩开  
  *spinning on, the cape flung out*
- `ult_06`：转回正面，披风开始收拢  
  *turning front again, the cape closing*
- `ult_07`：落到深蹲  
  *dropping into a deep crouch*
- `ult_08`：回到待机姿势  
  *back to the idle pose*

### hit（受击）

- `hit_01`：被击中，身体向后缩，头低下  
  *hit: the body flinches back, head down*
- `hit_02`：稍微恢复，比待机更低  
  *recovering a little, lower than the idle*

### dead（死亡）

- `dead_01`：被击中，身体后仰  
  *struck, the body arching back*
- `dead_02`：向后踉跄，两臂甩开  
  *staggering back, arms flung out*
- `dead_03`：双脚离地向后倒  
  *feet leaving the ground, falling back*
- `dead_04`：身体倾斜在半空  
  *the body tilted in the air*
- `dead_05`：背部着地  
  *landing on his back*
- `dead_06`：躺平，披风摊开  
  *lying flat, the cape spread*
- `dead_07`：躺在地上不动，长刃伸在一边  
  *lying still on the ground, the blade out to one side*
- `dead_08`：同上（最后一帧，停住）  
  *the same (last frame, held)*

## 提示词（每帧都用这一段，最后加上这一帧的英文说明）

附图顺序：`design/talon_design.png`、这一帧的 `1_target.png`、`2_league.png`（跑步再加 `3_upper_body.png`）。

```text
Attached: (1) the APPROVED game sprite of this character (talon_design.png, 8x: every 8x8 square is one game pixel) - his look, colours, size and the pixel style to keep; (2) 1_target.png - the canvas to draw on (960 x 896 = 120 x 112 squares at 8x): the red line is the ground (nothing below it), the blue cross is where he stands, the faint grey shape shows this frame's pose and size; (3) 2_league.png - the same frame of the original game animation, same place and scale: copy the POSE from it (body, arms, legs, cape), not its 3D look.
Draw ONE frame of this character as a small pixel-art game sprite on the target canvas: exactly the approved sprite's look - the blue-violet hood with the silver blade crest and NO EYES (a black band of hood shadow under the crest, only the lower face visible), the three-tier silver pauldron, the rust-red cape with silver blade tips, the long silver wrist blade, blue-violet clothes, teal sash, dark gunmetal legs with silver knee guards - at the SAME size as the approved sprite (about 42 squares tall when standing), in the pose of 2_league.png.
Pixel rules: every square 8x8 on one grid starting at the canvas corner, no anti-aliasing, no blur, no gradients, no soft shading; only the approved sprite's colours (palette.png); one 1-square near-black outline round the figure; big flat colour areas like the approved sprite. Transparent background. Nothing below the red line. No effects, no flying blades, no motion lines, no shadow, no text.
THIS FRAME: <paste the frame's English line from the list above>
RUN FRAMES ONLY: copy the upper body of 3_upper_body.png exactly as it is (same squares, same colours; it may move 1 square up or down as a whole); draw only the legs in a clear crossing stride and the cape's hem swinging.
```

## 交回前自查

- [ ] 每帧一张 960×896 透明 PNG，8×8 网格对齐，没有半透明；
- [ ] 和定稿一样大（站直约 42 格），脚在红线上，线下面没有像素；
- [ ] 没有眼睛：护额下是黑色兜帽阴影，只露下半张脸；
- [ ] 只用色板里的颜色，外圈一格近黑描边，大块平涂；
- [ ] 姿势和 `2_league.png` 一致；没有飞刀、刀光等特效；
- [ ] 跑步帧的上半身和 `3_upper_body.png` 一模一样；
- [ ] 一共 57 张，最后写 `HANDOFF.md`。

色板：#120E1A #4A0B15 #141250 #6E1219 #35343F #0A4A66 #221F7E #A01C24 #7A4A30 #55525E #3533AA #D82A2F #2A92A2 #4D4BD2 #7A7986 #C27E4E #D09A38 #7279F6 #A4A6B4 #ECB486 #CFD0DC #FAFAFC
