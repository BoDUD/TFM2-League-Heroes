# 贾克斯：E 爆发 6 帧 + 死亡第 2–8 帧，按游戏尺寸重画（给 Codex）

> 贾克斯的这 13 帧是你之前从生图大图缩到游戏尺寸的：姿势对，但每种颜色都碎成了一个个单像素，看着很「花」、很脏，身体里还有透出地面的小洞（已经补过）。用户：「这个拜托codex吧」。
> **这次直接按游戏尺寸画**：每帧画在它自己 96×96 格的画布上，一格就是游戏里的一个像素（8 倍图里每格是 8×8 的色块），只用定稿的 24 种颜色。导入时不再取样，你交的 1 倍图直接替换这一帧。

## 要求（每帧都一样）

- **姿势**照英雄联盟同一帧（`_2_league_game.png` 游戏尺寸、`_3_league_render.png` 大图、`_4_league_parts.png` 分部位）；现在的帧（`_1_now`）已经是这个姿势，**轮廓、大小、位置照它**，它糊成一团看不清的地方照英雄联盟画。
- **模型**照定稿 `0_design_8x.png`：皇家紫的兜帽和破边披风、青铜面具上四颗青色灯（2×2，每颗一格，**面具照 `_1_now` 逐格照搬**，趴着看不到脸的帧不画）、深蓝羽饰、灰紫皮肤、红棕皮手套和绑带、藏青裤子；灯柱是一根笔直的杆（`#693A5D`），一头青铜钩、一头带尖刺的青铜灯笼（橙色玻璃），长度和 `_1_now` 一样。
- **像素规矩**：每格一种颜色，只用 `0_palette.png` 的 24 色（不加新色、不混色、不要半透明和抗锯齿）；每种材质 2–3 个平涂色阶、光从左上，和定稿一样，**色块里不要别的颜色的单个像素**；外面一圈 1 格 `#110315` 描边，两部分重叠处也用它分开，不要双层描边、色块里不要黑点；**不要洞**（身体里不能透出地面，只有手臂或灯柱和身体之间本来就空的地方留空，和英雄联盟一样）；手臂至少 3 格粗、拳头握在杆上；红线（脚底那一行）以下什么都没有，离画布四边至少空 1 格；不画特效、地面、影子、文字。
- **画质标准**：`0_quality_bar.png` 是他在游戏里现在干净的几帧（待机、普攻等），13 帧都要画到这个程度。

## 交付

- 每帧两张：`jax_<动作>_<帧>.png`（96×96，透明底，一格一个像素，**和 `_1_now_1x.png` 同一张画布**：脚底在红线那一行，站位点在十字处），和 `jax_<动作>_<帧>_8x.png`（768×768，每格 8×8 色块）。
- 13 帧的文件名：`jax_skill2_burst_1.png`、`jax_skill2_burst_2.png`、`jax_skill2_burst_3.png`、`jax_skill2_burst_4.png`、`jax_skill2_burst_5.png`、`jax_skill2_burst_6.png`、`jax_dead_2.png`、`jax_dead_3.png`、`jax_dead_4.png`、`jax_dead_5.png`、`jax_dead_6.png`、`jax_dead_7.png`、`jax_dead_8.png`。
- 一张 `preview_redo13.png`：每帧现在的样子和你画的并排；`HANDOFF.md` **最后写**（哪几帧照英雄联盟改了姿势、有没有没做到的）；最好打成 `jax_redo13_done.zip`。

## 附图（压缩包 `jax/` 里）

| 文件 | 内容 |
|---|---|
| `0_design_8x.png` / `0_design_1x.png` | 定稿（36 行）：长相、颜色、画法 |
| `0_palette.png` | 24 种颜色和各自画什么 |
| `0_quality_bar.png` | 他在游戏里干净的几帧（8 倍）：画质标准 |
| `0_overview.png` | 13 帧：上面现在、下面英雄联盟（3 倍） |
| `<动作>_<帧>_1_now_8x.png` / `_1_now_1x.png` | 这一帧现在（96×96 画布，红线 = 脚底那一行，十字 = 站位点）；1 倍图是它的原像素 |
| `<动作>_<帧>_2_league_game.png` | 英雄联盟同一帧，按游戏尺寸画在同一张画布上（8 倍） |
| `<动作>_<帧>_3_league_render.png` | 英雄联盟同一帧的 8 倍渲染：看细节 |
| `<动作>_<帧>_4_league_parts.png` | 同一帧分部位上色：头红、灯柱绿、身体蓝 |

## 提示词（每帧一次，替换 [frame]、[tag]、[n]）

```text
Attached for this ONE frame of Jax's sprite (a small pixel-art game character, about 36 squares tall standing):
FIRST `_1_now_8x.png` and `_1_now_1x.png`: the frame exactly as the game shows it now, on its own 96x96-square canvas (8x: every
square an 8x8 block; red line = the row of his soles, cross = his standing point). Its pose and size are right, but it was
shrunk from a big painting, so every colour is broken into single pixels - the drawing is noisy and dirty.
SECOND `_2_league_game.png`: the same moment of the original 3D animation, rendered at the same game size on the same
canvas. THIRD `_3_league_render.png`: the same moment rendered big, for detail. FOURTH `_4_league_parts.png`: the same
render painted by part - head red, lamppost green, body blue - to tell the arm, the pole, the cape and the legs apart.
Shared: `0_design_8x.png` (the approved model: his look, colours and pixel style), `0_palette.png` (the 24 colours and
what each paints), `0_quality_bar.png` (his clean frames in the game: the target quality).
Task: redraw this frame as CLEAN pixel art AT GAME SIZE on the same 96x96 canvas, as the clean frames in
0_quality_bar.png are drawn. Pose: the moment in the SECOND/THIRD images (the FIRST already follows it - keep its
silhouette, size and place; where the FIRST is an unreadable jumble, follow League). Model: the design - royal-purple hood
and ragged cape, the bronze mask with its FOUR cyan lights (a 2x2 group, one square each; copy the mask square for square
from the FIRST image wherever it shows; when he lies face down it is hidden), the dark-blue plume, grey-lavender skin,
red-brown leather gloves and straps, navy trousers, and the lamppost: one straight rigid pole #693A5D, the bronze hook at
one end and the spiked bronze lantern with its orange glass at the other, as long as in the FIRST image.
Pixel rules: every square one solid colour from 0_palette.png only (no new colours, no blending, no semi-transparency,
no anti-aliasing); each material in 2-3 flat tones lit from the upper left, as in the design - no single stray pixels of
another colour inside an area; a one-square #110315 outline round the silhouette and where two parts overlap, no double
outlines, no black dots inside areas; no holes - the ground never shows through the body (only real gaps between an arm or
the pole and the body stay open, as in League); arms at least 3 squares thick with the fists on the pole; nothing below the
red line (the soles' row), at least one empty square to every edge of the canvas; no effects, no ground, no shadow, no text.
This frame: [frame]
Deliver `jax_[tag]_[n].png` (96x96, transparent, one pixel per square, on exactly the same canvas: the soles on the red
line, the standing point where the cross is) and `jax_[tag]_[n]_8x.png` (768x768, each square an 8x8 block).
```

## 13 帧的 [frame]

- `jax_skill2_burst_1.png`（附 `skill2_burst_1_1_now_8x.png`、`_1_now_1x.png`、`_2_league_game.png`、`_3_league_render.png`、`_4_league_parts.png`）：`Counter Strike's release begins: crouched and compact, the mask facing us, the lamppost held upright at his front (right) side - the lantern up beside his head, the hook end down at the lower left behind him; the free (far) arm out to the right, claws open; knees bent.`
- `jax_skill2_burst_2.png`（附 `skill2_burst_2_1_now_8x.png`、`_1_now_1x.png`、`_2_league_game.png`、`_3_league_render.png`、`_4_league_parts.png`）：`Springing forward to the right: the body leaning right, the far arm stretched forward-right, claws spread; the near hand at his waist holds the lamppost trailing behind him to the lower left - the pole slanting down-left, the spiked lantern far at the lower left; the plume streaming up-left; legs tucked under him.`
- `jax_skill2_burst_3.png`（附 `skill2_burst_3_1_now_8x.png`、`_1_now_1x.png`、`_2_league_game.png`、`_3_league_render.png`、`_4_league_parts.png`）：`Mid-air sweep: the lamppost held level behind him at waist height, straight out to the left, the lantern at its far left end; the far arm reaching up-right, claws open; the plume streaming up-left; legs bent under the body.`
- `jax_skill2_burst_4.png`（附 `skill2_burst_4_1_now_8x.png`、`_1_now_1x.png`、`_2_league_game.png`、`_3_league_render.png`、`_4_league_parts.png`）：`The spin's peak: body upright, the plume flung straight up; the cape flares up behind his shoulders in spikes; the lamppost held level out to the left (lantern at the left end); the far arm raised up-right, claws open; legs hanging.`
- `jax_skill2_burst_5.png`（附 `skill2_burst_5_1_now_8x.png`、`_1_now_1x.png`、`_2_league_game.png`、`_3_league_render.png`、`_4_league_parts.png`）：`The strike comes down: wide crouch; the near arm swings the lamppost down at his left - the lantern low on the ground at the lower left, the pole rising to his fist at shoulder height; the far arm stretched right, claws open. The opening between the swinging arm and the body stays open.`
- `jax_skill2_burst_6.png`（附 `skill2_burst_6_1_now_8x.png`、`_1_now_1x.png`、`_2_league_game.png`、`_3_league_render.png`、`_4_league_parts.png`）：`Recovering into his stance: crouched, the lamppost diagonal in front of him - the hook end up at the left by his near fist, the pole running down-right to the lantern low at the lower right; plume up.`
- `jax_dead_2.png`（附 `dead_2_1_now_8x.png`、`_1_now_1x.png`、`_2_league_game.png`、`_3_league_render.png`、`_4_league_parts.png`）：`Struck and thrown back: the near arm flung up holding the lamppost high - the lantern at the top, the straight pole slanting down-right to the hook end; the head tipped back, the mask turned up-left; the plume streaming to the upper left; the cape's ragged strands hanging to the left; knees bent wide.`
- `jax_dead_3.png`（附 `dead_3_1_now_8x.png`、`_1_now_1x.png`、`_2_league_game.png`、`_3_league_render.png`、`_4_league_parts.png`）：`Slumping to his knees: hunched forward to the right, head bowed, leaning on the lamppost planted upright in front of him (right): the lantern at the top, the hook end on the ground; his near fist grips the pole low; the plume over his back to the upper left; the cape's strands hang down at the left.`
- `jax_dead_4.png`（附 `dead_4_1_now_8x.png`、`_1_now_1x.png`、`_2_league_game.png`、`_3_league_render.png`、`_4_league_parts.png`）：`Sinking lower on his knees, still leaning on the upright lamppost at the right (lantern at the top, hook on the ground); the far hand grips the pole at chest height, the near arm on his knee; head bowed.`
- `jax_dead_5.png`（附 `dead_5_1_now_8x.png`、`_1_now_1x.png`、`_2_league_game.png`、`_3_league_render.png`、`_4_league_parts.png`）：`Lower still, head bowed onto his fists on the upright pole (lantern at the top, hook on the ground); the body sagging, the cape spread down at the left.`
- `jax_dead_6.png`（附 `dead_6_1_now_8x.png`、`_1_now_1x.png`、`_2_league_game.png`、`_3_league_render.png`、`_4_league_parts.png`）：`Falling forward: the body tipping forward to the right toward the ground, the near arm reaching down; the lamppost falling over to the right - the lantern at the right at the hand's height; the plume up-left, the cape spread to the left.`
- `jax_dead_7.png`（附 `dead_7_1_now_8x.png`、`_1_now_1x.png`、`_2_league_game.png`、`_3_league_render.png`、`_4_league_parts.png`）：`Lying face down on the ground, head and shoulders at the right, the face hidden; the cape spread to the left in ragged strands; the plume lying along the ground under him; the lamppost lying on the ground by his right hand, the lantern at the far right.`
- `jax_dead_8.png`（附 `dead_8_1_now_8x.png`、`_1_now_1x.png`、`_2_league_game.png`、`_3_league_render.png`、`_4_league_parts.png`）：`Lying still, the same as the frame before but settled a little flatter; the lantern on the ground at the right by his hand.`

## 交回前自查

- [ ] 13 帧都是 96×96、和 `_1_now_1x.png` 同一画布：脚底在红线那一行，没有东西在红线以下，离四边至少 1 格；
- [ ] 只用 24 色，没有半透明；8 倍图每格是完整的 8×8 色块；
- [ ] 色块干净（没有夹在别的颜色里的单个像素），一圈 `#110315` 描边，没有双层描边和内部黑点，身体里没有洞；
- [ ] 面具和四颗灯照 `_1_now` 逐格照搬（看得到脸的帧）；灯柱笔直、钩和灯笼都在、长度不变；手臂至少 3 格粗；
- [ ] `HANDOFF.md` 最后写。

## Claude 导入时（给 Claude 看）

- 1 倍图直接替换 `assets/source/native/jax_skill2_burst.png`、`jax_dead.png` 里对应的格子（`tools/art/fix_jax_frames.py` 在补洞之前读 `assets/source/jax/codex_redo13/`）；检查：画布和脚底一致、颜色都在色板里、没有洞、只有一块（掉落的灯柱除外），再给用户审核。
