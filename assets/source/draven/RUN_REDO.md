# 德莱文：跑步整个人重画（给 Codex）

> 用户看了前几版跑步：「我要的是交叉步啊」「走路时候下半身还严重变形」，然后选了 **Codex 照英雄联盟跑步逐帧把整个人重画**。
> 上一包的问题：我让你只画腰带以下的腿、还要对准靴子框，你交付前又把腿挪动、拉伸重采样去对框，腿就变细变碎了；原稿里的腿虽然完整，但一直是叉开的宽步，没有交叉。
> - **这一包：8 帧跑步，每帧单独生成一张，整个人一起画**（头、身体、手臂、斧头、腿一次画完）。
> - **长相、大小照定稿** `1_design.png`：同样的头（鸡冠、金头带、马蹄胡、大笑）、毛皮披肩、胸前皮带、腰带和飘带；头尖到脚底 40 格；只用 `2_palette.png` 的颜色。
> - **手臂和斧头照** `3_run_look.png`：**两把斧都低握在身体两侧**（英雄联盟和 oppi 的德莱文都是这样跑的），手臂可以随步子前后摆 1–2 格。
> - **腿照英雄联盟这一帧**（`a_league_game_size.png` 位置和大小，`b_league_pose.png` 关节）：**交叉步**——两腿收到胯下、互相越过，不要定稿那种叉开的站姿。**腿的粗细照** `4_legs_look.png`：黑裤 5–6 格宽、带亮边，银蓝大护胫 6–7 格宽、白高光和膝甲，深色靴子；两腿同色（远侧可以暗一档），膝盖看得出来。
> - 着地那只脚的鞋底在第 99 行（红线），下面什么都不能有；站位点第 64 列（蓝线）。
> - **画完不要再挪动、缩放、重采样任何部位**（上一包就是这一步把腿弄坏的）。只做：按 8 格网格取色、对齐色板、透明度二值化。如果某帧画得不对，**重新生成那一帧**，不要用脚本改。
> - 交付到 `outputs/draven-run/`：`run_1.png` … `run_8.png`（1024×1024），**生图原稿** `raw/run_<k>.png`（必交），最后写 `HANDOFF.md`，打成 `draven_run_done.zip`。

## 每帧画什么（英雄联盟 Draven 跑步，100 毫秒一帧）

| 帧 | 腿 |
|---|---|
| `run_1.png` | 近腿（画面右侧那条、画在前面）着地、在身体正下方稍靠前；远腿往后上踢，脚跟抬到膝盖高度、小腿朝后 |
| `run_2.png` | 近腿着地在身体正下方（开始往后蹬）；远腿屈膝往前摆，脚离地约 5 格 |
| `run_3.png` | 近腿往后蹬（脚在身后、仍着地）；远腿膝盖抬起往前伸，脚离地 2–3 格——两腿在这一帧交叉 |
| `run_4.png` | 近腿脚尖离地在身后；远腿在前方落地 |
| `run_5.png` | 远腿着地在身体正下方稍靠前；近腿往后上踢，脚跟抬到膝盖高度（和第 1 帧左右腿互换） |
| `run_6.png` | 远腿着地在身体正下方；近腿屈膝往前摆，脚离地约 5 格 |
| `run_7.png` | 远腿往后蹬；近腿膝盖抬起往前伸——两腿交叉，近腿在前 |
| `run_8.png` | 远腿脚尖离地在身后；近腿在前方落地 |

（近腿 = 画面右侧那条、离镜头近、画在前面；远腿 = 被挡住一部分的那条。）

## 英文提示词（每帧一次；附上根目录的 1、2、3、4 号图和这一帧文件夹里的两张图）

```text
Attached: FIRST the approved game sprite of this character at 8x on a 1024x1024 canvas (128x128 squares) - copy its look, colours, size and proportions exactly: the same head (hair crest, gold headband, moustache, grin), fur mantle, chest straps, belt, ribbons, arms, axes and legs; SECOND its palette - use only these colours; THIRD the same character with BOTH axes held LOW at his sides (the far arm brought down like the near one) - this is how the arms and axes look while running; FOURTH the character's legs enlarged - draw the running legs exactly this thick: black trousers 5-6 squares wide with a lit edge, big silver-blue greaves 6-7 squares wide with white highlights and a knee plate, dark boots; FIFTH League of Legends' own run pose for this frame shrunk to game size and placed on the same canvas - copy the LEG POSE (which leg is in front, which is lifted, how the knees bend), the place and the size; SIXTH the same pose in high detail.
Draw this ONE running frame as the WHOLE character, one crisp pixel-art sprite at 8x: every square one 8x8 block on one 8-px grid, alpha only 0 or 255, one 1-square near-black outline, flat shades, no anti-aliasing, no blur, no dithering. 3/4 front view facing image right, the face toward the viewer; upper body upright as in the FIRST image (a slight bob is fine), both axes held low at the sides as in the THIRD image (the arms may swing 1-2 squares, opposite to the legs). The legs do a RUNNING CROSS-STEP like League: the legs come close together under the hips and pass each other - not the wide standing stance of the FIRST image. Both legs the same colours (the far leg may be one shade darker), as thick as the FOURTH image, a visible knee. The planted foot's sole on the red line (row 99); nothing below it. Same height as the FIRST image (40 squares from the hair crest to the soles). No flying axes, no motion lines, no dust, no effects. Transparent background (else solid #FF00FF).
This frame: run <K> of 8 - <FRAME>
```

每帧的 <K> 和 <FRAME>：

```text
run 1: near leg planted just ahead of the hips; far leg kicked up behind, heel at knee height, shin pointing back
run 2: near leg planted under the hips, starting to push back; far leg swinging forward, knee bent, foot ~5 squares up
run 3: near leg pushing back, foot behind on the ground; far knee up reaching forward, foot 2-3 squares up - the legs cross
run 4: near foot leaving the ground behind; far foot landing ahead
run 5: far leg planted just ahead of the hips; near leg kicked up behind, heel at knee height (frame 1 with the legs swapped)
run 6: far leg planted under the hips; near leg swinging forward, knee bent, foot ~5 squares up
run 7: far leg pushing back; near knee up reaching forward - the legs cross, the near leg in front
run 8: far foot leaving the ground behind; near foot landing ahead
```

## 交回前自查

- [ ] 8 张 1024×1024，严格 8×8 方块、透明度 0/255、只用色板颜色、一圈近黑描边；
- [ ] 每帧都是整个人，和定稿一样大（头一样大、身体一样宽），两把斧低握在两侧；
- [ ] 腿是交叉步：第 3、7 帧两腿交叉，第 1、5 帧一条腿往后上踢；腿和定稿一样粗、护胫一样大；
- [ ] 着地的鞋底在第 99 行，下面没有像素；画完没有挪动、拉伸任何部位；交了原稿；最后写 `HANDOFF.md`。
