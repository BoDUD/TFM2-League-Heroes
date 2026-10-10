# 德莱文：待机和普攻照英雄联盟重画，缩到 90%（给 Codex）

> 用户：「模型可以适当缩小点」（选了 **90%**），「另外待机姿势能改成和英雄联盟一样吗 攻击姿势也是」。
> - **这一包 6 张：待机 1 帧 + 普攻 5 帧，每帧单独生成一张，整个人一起画。**
> - **大小：头顶鸡冠到鞋底 36 格**（原来 40 格）。`1_look_90.png` 是定稿缩到 90% 的样子：照它的**长相、颜色、粗细**（头、毛皮披肩、胸前皮带、腰带、红飘带、手臂、斧头、腿），只用 `2_palette.png` 的颜色。
> - **只照长相，不照姿势**：定稿把一把斧举过头顶，英雄联盟的待机两把斧都放低。两斧放低时手臂和斧头的样子看 `3_axes_low_90.png`。
> - **头照 `4_head_16x.png` 一格一格画**（鸡冠、金头带、马蹄胡、大笑），每帧都朝画面右边、一样大。
> - **姿势照英雄联盟这一帧**：`a_league_game_size.png`（按 36 格渲染好的游戏尺寸，看位置和大小）、`b_league_pose.png`（高清，看手臂、斧头朝向和腿）。英雄联盟里有几帧头扭向左边，这里一律朝右。
> - 鞋底在第 99 行（红线），站位点第 64 列（蓝线），绿线（第 64 行）是 36 格高的头顶。斧头和定稿一样大，不要画大。
> - 出手那帧（`attack_4`）斧头已经扔出去：手里空着，**画面里不要画飞出去的斧头**，也不要拖影、速度线、特效。
> - **画完不要再挪动、缩放、重采样任何部位**；只做：按 8 格网格取色、对齐色板、透明度二值化。画得不对就**重新生成那一帧**。
> - 交付到 `outputs/draven-pose/`：`idle_1.png`、`attack_1.png` … `attack_5.png`（1024×1024），**生图原稿** `raw/<名字>.png`（必交），最后写 `HANDOFF.md`，打成 `draven_pose_done.zip`。

## 每帧画什么

| 文件 | 英雄联盟 | 姿势 |
|---|---|---|
| `idle_1.png` | draven_idle1 第 0 毫秒 | 站立待机：两腿前后分开、膝盖微屈，身体微微后仰；画面左侧那只手把斧头横着往身后伸，斧头在胸口高度、斧刃朝左；画面右侧那只手垂在身前，斧头斜向右下、在近腿旁边，斧刃朝右下；抬头大笑 |
| `attack_1.png` | attack1 第 0 毫秒（准备） | 准备：身体前倾、微蹲；左手的斧头垂在身前左下方，斧刃朝左下；右手往右伸，斧头横在身体右侧、斧刃朝右 |
| `attack_2.png` | attack1 第 100 毫秒（引臂） | 引臂：右手把斧头举到右上方（斧刃在右上角），左手的斧头仍垂在左下方；身体后仰、重心在后腿 |
| `attack_3.png` | attack1 第 190 毫秒（蓄力） | 蓄力：右手把斧头举到头顶正上方（斧刃朝上），左手把另一把斧横着往左伸（斧刃朝左）；身体拧转后仰，像要把斧头从头顶甩出去 |
| `attack_4.png` | attack1 第 270 毫秒（出手，斧头这一帧离手） | 出手：身体往右前方压低、前倾；右手往画面右侧伸直，手里是空的（斧头已经扔出去）；左手的斧头收在身体左侧、斧刃朝下；前腿弓、后腿蹬 |
| `attack_5.png` | attack1 第 420 毫秒（收势） | 收势：身体直起来；左手把斧头举在头的左侧、横着朝左；右手收回垂在身侧，手里是空的；两腿回到站姿 |

（左手 / 右手 = 画面左侧 / 右侧那只手。普攻在游戏里共 400 毫秒：50 / 60 / 73 / 117 / 100，第 4 帧在 183 毫秒出手，和技能数据里斧头离手的时刻一致。）

## 英文提示词（每帧一次；附上根目录的 1、2、3、4 号图和这一帧文件夹里的两张图）

```text
Attached: FIRST the approved game sprite of this character made 90% as big, at 8x on a 1024x1024 canvas (128x128 squares) - copy its LOOK exactly (not its pose): the same head, fur mantle, chest straps, belt, crimson ribbons, arms, axes and legs, the same colours and the same thickness of every part; SECOND its palette - use only these colours; THIRD the same character with BOTH axes held LOW at his sides - how the arms and axes look when they are not raised; FOURTH his head at 16x - draw it square for square like this, facing image right, in every frame; FIFTH League of Legends' own pose for this frame rendered at game size on the same canvas - copy the POSE (body lean, which arm holds which axe where, which way each blade points, the legs), the place and the size; SIXTH the same pose in high detail.
Draw this ONE frame as the WHOLE character, one crisp pixel-art sprite at 8x: every square one 8x8 block on one 8-px grid, alpha only 0 or 255, one 1-square near-black outline, flat shades, no anti-aliasing, no blur, no dithering. 3/4 view facing image right like the FIRST image, the face toward image right in every frame. Size: exactly 36 squares from the top of the hair crest (green line, row 64) to the soles (red line, row 99) when standing, the body as broad as the FIRST image; the planted sole on the red line, nothing below it; the standing point on the blue line (column 64). The two axes are the FIRST image's axes (same size, same steel blade, gold studs, crimson wraps) - not bigger. No flying axes (in the release frame the axe is simply gone from the hand), no motion lines, no trails, no dust, no effects. Transparent background (else solid #FF00FF).
This frame: <NAME> - <FRAME>
```

每帧的 <NAME> 和 <FRAME>：

```text
idle_1: standing idle: legs apart front and back, knees slightly bent, the upper body leaning back a little; the image-left hand holds its axe straight out BEHIND him at chest height, the blade pointing image-left; the image-right hand hangs in front with its axe slanting down to the image-right beside the near leg, the blade pointing down-right; head up, grinning
attack_1: ready: leaning forward, slightly crouched; the left-hand axe hangs low in front to the lower left, blade pointing down-left; the right arm reaches out to the image-right with its axe held level on the right, blade pointing right
attack_2: wind-up: the right arm lifts its axe high to the upper right (the blade at the top right), the left-hand axe still hangs low at the lower left; the body leans back, the weight on the back leg
attack_3: cocked: the right arm holds its axe straight up over the head (blade at the top), the left arm holds the other axe straight out to the image-left (blade pointing left); the body twisted and leaning back, about to hurl the axe over the head
attack_4: release: the body lunges low to the image-right; the right arm whipped out straight to the image-right, the hand EMPTY and open (the axe has just left it); the left-hand axe tucked by his left side, blade down; front leg bent, back leg pushing
attack_5: follow-through: the body straightens up; the left arm holds its axe beside the head, level, blade pointing left; the right arm comes back down to his side, the hand still empty; the legs back in a standing stance
```

## 交回前自查

- [ ] 6 张 1024×1024，严格 8×8 方块、透明度 0/255、只用色板颜色、一圈近黑描边；
- [ ] 站立时头顶到鞋底 36 格，身体和 `1_look_90.png` 一样宽，斧头一样大；头和 `4_head_16x.png` 一样、朝右；
- [ ] 待机两斧都放低（左边横着往后伸，右边斜向右下），不举过头顶；普攻 5 帧照英雄联盟的姿势，第 4 帧手里是空的；
- [ ] 鞋底在第 99 行，下面没有像素；画完没有挪动、拉伸任何部位；交了原稿；最后写 `HANDOFF.md`。
