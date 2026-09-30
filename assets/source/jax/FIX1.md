# 贾克斯：动作帧小返修（3 帧，给 Codex）

> 上一包的 11 张动作图已经导入游戏（Claude 按网格取格、贴定稿面具、按英雄联盟的头和脚底线对位）。用户看过后选了“小返修包”：只重画这 3 帧，其余不动。
> - **大招第 3、4 帧**：跳到空中那两帧画成了侧后方，看不到面具（团战经理的英雄都朝右、看得到脸，不能画背影）。要转到英雄联盟那一帧的朝向：3/4 正面朝右，兜帽右侧露出青铜面具和四颗青色灯眼。
> - **蓄力一击（W）第 3 帧**：灯柱画成了弯的（像鞭子）。英雄联盟的这一帧自己把灯柱拉弯了（动画的拉伸效果，参考图里也是弯的），但我们的灯柱是硬的，要一根直杆。
> - 每帧交一张图：`jax_ult_3.png`、`jax_ult_4.png`、`jax_attack_w_3.png`，只画人物（透明底，做不到就纯品红 `#FF00FF`），大小和上一包的动作图一样（人物约和定稿一样高）。附 `HANDOFF.md`（用了哪段提示词、哪里没做到）。

## 附图

| 文件 | 内容 |
|---|---|
| `<动作>_<帧>_1_now.png` | 这一帧现在在游戏里的样子（游戏尺寸，放大 8 倍）：大小、配色、面具、灯柱照它 |
| `<动作>_<帧>_2_league.png` | 英雄联盟同一帧的渲染：身体的朝向和动作照它 |
| `jax_design.png` | 定稿（放大 8 倍）：长相、颜色、灯柱长度以它为准 |

## 提示词（每帧一张，只替换 [frame]）

每张附三张图：第一张 `<动作>_<帧>_1_now.png`，第二张 `<动作>_<帧>_2_league.png`，第三张 `jax_design.png`。

```text
Three attached images. FIRST: this frame as it is now in the game (pixel art at 8x) - keep its size, colors, mask, lamppost and pixel style. SECOND: the same moment of the original 3D animation - copy the body's facing and motion from it. THIRD: the approved design of the character (8x) - his look, colors and lamppost length.
Draw this ONE frame again as clean pixel art in the style of the FIRST image, the character at the same size as the FIRST image, every pixel a crisp square, no anti-aliasing, no blur, only the colors of the THIRD image. The face is the bronze mask with FOUR cyan lights (2x2, one square each) in the magenta hood; the cyan is used nowhere else. One 1-square near-black outline round the silhouette, each material's own dark shade inside it. His arms are at least 3 squares thick with the fists holding the pole; the lamppost is ONE straight rigid pole 2 squares thick with the bronze hook cap at one end and the spiked lantern glowing orange at the other; the whole figure and the lamppost are one connected piece. No effects, no ground, no shadow, no text.
Frame: [frame]
Transparent background (if not possible: solid #FF00FF magenta).
```

## 三帧的 [frame]

- `jax_ult_3.png`（附 `ult_3_1_now.png`、`ult_3_2_league.png`）：`In the air, rising: he holds the lamppost upright above his head in his raised fist (lantern end up), body stretched upward, legs tucked below, the cape and plume trailing down behind him. TURN HIM TO THE CAMERA like League's frame (the SECOND card): 3/4 front view facing right, his bronze mask with the four cyan lights clearly visible on the right side of the hood, his chest toward us - NOT his back and NOT the cape covering him.`
- `jax_ult_4.png`（附 `ult_4_1_now.png`、`ult_4_2_league.png`）：`At the top of the jump, starting to come down: the lamppost still upright above him in his raised fist, the body a little bent, legs tucked, the cape and plume trailing. TURN HIM TO THE CAMERA like League's frame (the SECOND card): 3/4 front view facing right, the mask with its four cyan lights visible on the right side of the hood, his chest toward us - NOT his back.`
- `jax_attack_w_3.png`（附 `attack_w_3_1_now.png`、`attack_w_3_2_league.png`）：`The charged smash, mid-swing: he leans back and swings the lamppost down over his head with both fists, as now. The lamppost must be ONE STRAIGHT POLE, 2 squares thick, from his fists to the spiked lantern end - it is rigid and must not bend or curve like a whip (League's own render in the SECOND card bends it: a stretch effect of that animation - ignore the bend). Keep the body, the pose, the mask and the size exactly as in the FIRST card; only the pole is redrawn straight.`

## Claude 导入时（给 Claude 看）

- `tools/art/export_jax.py` 的单帧路径：按面积定取样间距（和定稿同样大小）、贴定稿面具、按英雄联盟的头和脚底线放回原来的格子，再只留一圈描边；其余帧逐格不变。
