# 贾克斯：灯柱返修（9 帧，给 Codex）

> 上一轮 3 帧（大招 3、4，W 第 3 帧）已导入。用户看动作 GIF 时指出：**“攻击的时候武器是歪的”**。逐帧对照英雄联盟后，这 9 帧的灯柱都有同一类问题：
> - **普攻第 1、6 帧**：灯柱缩成头旁边的一团金色，整根杆不见了；第 6 帧的姿势也应是英雄联盟那样把灯柱斜举在身前。
> - **普攻第 4、5 帧**：灯笼画成竖直的，没有顺着杆的方向，接在斜杆/平杆的末端就歪了。
> - **大招期间的攻击（反手）第 1、2、6 帧**：钩端画成了金色圆球、杆很短，灯笼不见了，看起来像一根锤子。
> - **跳斩第 2 帧、死亡第 1 帧**：灯柱缺失。
> 每帧交一张图：`jax_<动作>_<帧>.png`（如 `jax_attack_1.png`、`jax_attack_r_2.png`、`jax_skill_2.png`、`jax_dead_1.png`），只画人物（透明底，做不到就纯品红 `#FF00FF`），人物大小和第一张图一样。附 `HANDOFF.md`（用了哪段提示词、哪里没做到）。

## 灯柱的规矩（每帧都要）

- 一根**笔直、刚硬**的杆，颜色是定稿的暗紫 `#693A5D` 加近黑描边（**不要粉色、不要紫蓝色**，上一轮 W 第 3 帧画成了粉色）。
- 长度和定稿一样（大约和他一样高），一端是青铜**钩**（弯钩，不是圆球），另一端是带尖刺、发橙光的青铜**灯笼**。
- **灯笼是杆的一部分**：灯笼底座接在杆上，尖刺顺着杆的方向朝外（离手的方向）。杆斜，灯笼就跟着斜；杆平，灯笼就横着——不能竖着插在斜杆上，也不能侧挂。
- 两端都要在画面里（英雄联盟那帧里伸出画面的端点，也要收在画面内）；什么都不能低于脚底线。

## 附图（每帧四张）

| 文件 | 内容 |
|---|---|
| `<动作>_<帧>_1_now.png` | 这一帧现在在游戏里的样子（游戏尺寸，放大 8 倍）：身体、大小、配色、面具照它 |
| `<动作>_<帧>_2_guide.png` | 同一帧上用青色线画出灯柱应该在的位置：H 是钩端，L 是灯笼端 |
| `<动作>_<帧>_3_league.png` | 英雄联盟同一帧的渲染：灯柱怎么拿、朝哪照它 |
| `jax_design.png` | 定稿（放大 8 倍）：长相、颜色、灯柱和灯笼的样子以它为准 |

## 提示词（每帧一张，只替换 [frame]）

每张附四张图：`<动作>_<帧>_1_now.png`、`<动作>_<帧>_2_guide.png`、`<动作>_<帧>_3_league.png`、`jax_design.png`。

```text
Four attached images. FIRST: this frame as it is now in the game (pixel art at 8x) - keep its body pose, size, colors, mask and pixel style. SECOND: the same frame with a cyan GUIDE line where the lamppost must go, from the hook end H to the lantern end L (the cyan line is only a guide - do not draw it). THIRD: the same moment of the original 3D animation - how he holds the lamppost. FOURTH: the approved design (8x) - his look, colors, and the lamppost with its hook and lantern.
Draw this ONE frame again as clean pixel art in the style of the FIRST image, the character at the same size as the FIRST image, every pixel a crisp square, no anti-aliasing, no blur, only the colors of the FOURTH image. The face is the bronze mask with FOUR cyan lights (2x2, one square each) in the magenta hood; the cyan is used nowhere else. One 1-square near-black outline round the silhouette. His arms are at least 3 squares thick with the fists gripping the pole.
THE LAMPPOST: one straight rigid pole, dark mauve #693A5D with the near-black outline (not pink, not violet, not blue), about as long as he is tall, the bronze HOOK cap (a crook, not a ball) at one end and the spiked bronze LANTERN with its orange glow at the other. The lantern is part of the pole: its base sits on the pole and its spike points ALONG the pole's line, away from the hands - never upright on a slanted pole, never hanging sideways, never shrunk into a club head by his head.
The whole figure and the lamppost are one connected piece, inside the picture, nothing below his feet. No effects, no ground, no shadow, no text, no guide line.
Frame: [frame]
Transparent background (if not possible: solid #FF00FF magenta).
```

## 九帧的 [frame]

- `jax_attack_1.png`（附 `attack_1_1_now.png`、`attack_1_2_guide.png`、`attack_1_3_league.png`）：`Winding up the swing: the lamppost held upright at his back (left side) - the lantern end up beside his head (its spike pointing up), the straight pole running down through his fists to the hook end low near his back foot, as in League's frame. Keep his crouch, cape, mask and size as in the FIRST card.`
- `jax_attack_4.png`（附 `attack_4_1_now.png`、`attack_4_2_guide.png`、`attack_4_3_league.png`）：`The blow lands: the lantern end crashes on the ground in front of him (right, resting ON the ground line, not below his feet), the straight pole rising from it up-left through his fists to the hook end behind his hands. The lantern lies along the pole (spike pointing down-right, continuing the pole's line). Keep his body pose as in the FIRST card; only the lamppost is redrawn.`
- `jax_attack_5.png`（附 `attack_5_1_now.png`、`attack_5_2_guide.png`、`attack_5_3_league.png`）：`The lunge: the lamppost thrust straight out to the right, level - the lantern end at the right lying along the pole (spike pointing right), his fists on the pole, the pole continuing back past his fists to the hook end. Keep his body pose as in the FIRST card; only the lamppost is redrawn.`
- `jax_attack_6.png`（附 `attack_6_1_now.png`、`attack_6_2_guide.png`、`attack_6_3_league.png`）：`Back to the ready stance, as in League's frame: the lamppost diagonal in front of him - the hook end low at the left near his back foot, the straight pole rising up-right through his fists (at his waist) to the lantern end up-right at about his head's height (spike pointing up-right). His crouch, cape, mask and size as in the FIRST card.`
- `jax_attack_r_1.png`（附 `attack_r_1_1_now.png`、`attack_r_1_2_guide.png`、`attack_r_1_3_league.png`）：`Reversed grip, as in League's frame: the pole slants from the hook end up-left (the bronze crook) down-right through his fists to the lantern end low at the right near his front foot (resting on the ground line, not below his feet; spike pointing down-right). Keep his stance, cape, mask and size as in the FIRST card.`
- `jax_attack_r_2.png`（附 `attack_r_2_1_now.png`、`attack_r_2_2_guide.png`、`attack_r_2_3_league.png`）：`Reversed grip, raised to thrust, as in League's frame: the hook end high up-left, the straight pole running down-right through his fists (chest height) to the lantern end low in front (spike pointing down-right). Keep his stance, cape, mask and size as in the FIRST card.`
- `jax_attack_r_6.png`（附 `attack_r_6_1_now.png`、`attack_r_6_2_guide.png`、`attack_r_6_3_league.png`）：`Reversed grip, recovering, as in League's frame: the lamppost low and diagonal in front - the hook end at the left, the straight pole running down-right through his fists to the lantern end low at the right (spike pointing down-right, on the ground line). Keep his stance, cape, mask and size as in the FIRST card.`
- `jax_skill_2.png`（附 `skill_2_1_now.png`、`skill_2_2_guide.png`、`skill_2_3_league.png`）：`Leap Strike, springing up: he holds the lamppost raised above and behind his head in both fists - the lantern end up and back (upper left, spike pointing up-left, fully inside the picture), the hook end down in front of him (right). The whole straight pole visible. His rising pose, cape, mask and size as in the FIRST card.`
- `jax_dead_1.png`（附 `dead_1_1_now.png`、`dead_1_2_guide.png`、`dead_1_3_league.png`）：`Struck and starting to fall back, as in League's frame: the lamppost slipping low in his hand - the lantern end at his hip in front (spike pointing right), the straight pole slanting down-left behind his legs to the hook end near the ground. His body, cape, mask and size as in the FIRST card.`

## Claude 导入时（给 Claude 看）

- `tools/art/export_jax.py --fix` 的单帧路径（FIXES 加这 9 帧）：按被替换帧的面积定取样间距、贴定稿面具、按英雄联盟的头和脚底线放回原格子、再只留一圈描边；Codex 的紫色灯柱会映射成定稿灯柱色，粉色杆要按线改色。
